"""Protections of the real engine (F2.3, D33): memory before the start, Ollama, the memory watch and the driver's
"reported free 0.00 MB". Nothing here touches the real Ollama (11434) or the real `sd-cli`: Ollama is a `http.server`
of the test on a free port of 127.0.0.1, and `sd-cli` is `tests/fake_sd_cli.py`."""
import copy
import http.server
import json
import os
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from gimg import engine, engine_sdcpp, log, orders, queue, worker
from gimg.engine_sdcpp import SdCppEngine
from gimg.errors import GimgError
from tests.test_engine_sdcpp import (FAKE, MODEL, Base, MEMINFO_TEXT, alive, dead_ollama_url, protections_off_env,
                                     wait_for_file)
from tests.test_queue import QueueBase


class Quiet(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):  # a client that gave up (timeout) is part of the tests
        pass


class FakeOllama:
    """Ollama on a free local port. `models`: what ``/api/ps`` lists; `raw`: bytes to send instead; `unload_path`: the
    POST that empties the list (``None``: none does); `block`: ``/api/ps`` waits for `release` before answering."""

    def __init__(self, test, models=(), raw=None, status=200, unload_path=None, block=False):
        self.models, self.raw, self.status = list(models), raw, status
        self.unload_path, self.block = unload_path, block
        self.ps_hits, self.posts = 0, []
        self.release = threading.Event()
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send(self, body, status=200):
                self.send_response(status)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                outer.ps_hits += 1
                if self.path != "/api/ps":
                    return self.send(b"{}", 404)
                if outer.block:
                    outer.release.wait(10)
                body = outer.raw if outer.raw is not None else json.dumps({"models": outer.models}).encode()
                self.send(body, outer.status)

            def do_POST(self):
                size = int(self.headers.get("Content-Length") or 0)
                outer.posts.append((self.path, json.loads(self.rfile.read(size))))
                if self.path == outer.unload_path:
                    outer.models = []
                self.send(b"{}")

        self.server = Quiet(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        test.addCleanup(self.close)

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()


def loaded(name, size=5_000_000_000):
    return {"name": name, "model": name, "size": size}


class Seq:
    """A `read_meminfo` that serves `values` in order and then repeats the last one; it keeps what it served."""

    def __init__(self, *values):
        self.values, self.served = list(values), []

    def __call__(self):
        value = self.values.pop(0) if len(self.values) > 1 else self.values[0]
        self.served.append(value)
        return value


class ProtBase(Base):
    def machine_with(self, **engine_over):
        machine = copy.deepcopy(self.machine)
        machine["engine"].update(engine_over)
        return machine

    def make(self, machine=None, free=20000, **kw):
        reader = free if callable(free) else (lambda: free)
        eng = SdCppEngine(machine or self.machine, poll_s=0.05, kill_grace_s=2, read_meminfo=reader, **kw)
        eng.ollama_wait_s, eng.ollama_wait_poll_s = 0.3, 0.05  # unload: look again for 0.3 s, not 15
        return eng

    def go(self, machine=None, free=20000, **kw):
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        eng = self.make(machine, free)
        return eng.generate(self.job(**kw), lambda: False)

    def refused(self, code, machine=None, free=20000):
        """Run, expect the guard `code`, and check that nothing started: no process, no log, no image."""
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        self.argv_file.unlink(missing_ok=True)  # an earlier run of the same test
        job = self.job()
        out = Path(job.output)
        shutil.rmtree(out.parent, ignore_errors=True)
        with self.assertRaises(GimgError) as cm:
            self.make(machine, free).generate(job, lambda: False)
        self.assertEqual(cm.exception.code, code)
        self.assertFalse(self.argv_file.exists(), "sd-cli was started")
        self.assertEqual(list(out.parent.iterdir()) if out.parent.exists() else [], [])
        return cm.exception

    def wait_dead(self, pid_file):
        self.assertTrue(wait_for_file(pid_file), "the fake sd-cli never wrote its child pid")
        child = int(pid_file.read_text())
        for _ in range(100):
            if not alive(child):
                return
            time.sleep(0.1)
        self.fail("the child of sd-cli survived")


class MeminfoParsingTests(unittest.TestCase):
    def test_real_format(self):
        self.assertEqual(engine_sdcpp.parse_meminfo(MEMINFO_TEXT), 20000)
        self.assertEqual(engine_sdcpp.parse_meminfo("MemAvailable:\t2048 kB"), 2)
        self.assertEqual(engine_sdcpp.parse_meminfo("MemAvailable: 1023 kB\n"), 0)

    def test_odd_formats_are_none(self):
        for text in ("", "MemTotal: 5 kB\n", "MemAvailable:\n", "MemAvailable: abc kB", "MemAvailable: 2048",
                     "MemAvailable: 2048 MB", "MemAvailable: -5 kB", "MemAvailable: 1.5 kB", "memavailable: 5 kB",
                     "MemAvailable: 5 kB trailing", "\x00\xff garbage", "MemAvailable 5 kB"):
            self.assertIsNone(engine_sdcpp.parse_meminfo(text), repr(text))

    def test_a_huge_number_is_still_a_number(self):
        self.assertEqual(engine_sdcpp.parse_meminfo("MemAvailable: %d kB" % (1 << 60)), 1 << 50)

    def test_reader_reads_the_file_of_the_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "good", Path(tmp) / "bad"
            good.write_text(MEMINFO_TEXT)
            bad.write_bytes(b"MemAvailable: \xff\xfe kB\n")
            with mock.patch.dict(os.environ, {"GIMG_MEMINFO": str(good)}):
                self.assertEqual(engine_sdcpp.read_meminfo_mb(), 20000)
            with mock.patch.dict(os.environ, {"GIMG_MEMINFO": str(bad)}):
                self.assertIsNone(engine_sdcpp.read_meminfo_mb())
            with mock.patch.dict(os.environ, {"GIMG_MEMINFO": str(Path(tmp) / "nope")}):  # no /proc here
                self.assertIsNone(engine_sdcpp.read_meminfo_mb())
            with mock.patch.dict(os.environ, {"GIMG_MEMINFO": tmp}):  # a folder cannot be read
                self.assertIsNone(engine_sdcpp.read_meminfo_mb())


class MemoryBeforeStartTests(ProtBase):
    def test_not_enough_memory_says_how_much_is_free_and_how_much_is_needed(self):
        err = self.refused("engine.low_memory", free=3000)
        self.assertEqual((err.params["free_mb"], err.params["needed_mb"]), (3000, 7000))
        for lang in ("en", "es"):
            self.assertIn("3000", err.message(lang))
            self.assertIn("7000", err.message(lang))

    def test_exactly_the_minimum_is_enough(self):
        self.assertEqual(self.go(free=7000).min_free_mb, 7000)

    def test_one_mb_less_is_not(self):
        self.refused("engine.low_memory", free=6999)

    def test_without_meminfo_the_check_is_skipped_and_the_log_says_so(self):
        for reader in (lambda: None, lambda: "lots", lambda: True, lambda: -1, lambda: 12.5):
            res = self.go(free=reader)
            self.assertIsNone(res.min_free_mb)
            self.assertIn("memory check skipped", Path(res.log_path).read_text())

    def test_the_default_reader_without_proc_skips_the_check_too(self):
        self.env(GIMG_MEMINFO=str(self.tmp / "no-proc-here"))
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        res = SdCppEngine(self.machine, poll_s=0.05).generate(self.job(), lambda: False)
        self.assertIsNone(res.min_free_mb)

    def test_the_model_minimum_beats_the_general_one_both_ways(self):
        lower = self.machine_with(models={MODEL: {"minFreeMemoryMb": 100}})
        self.assertEqual(self.go(lower, free=2000).min_free_mb, 2000)  # general 7000 would refuse
        higher = self.machine_with(models={MODEL: {"minFreeMemoryMb": 9000}})
        self.refused("engine.low_memory", higher, free=8000)
        zero = self.machine_with(models={MODEL: {"minFreeMemoryMb": 0}})  # 0 is a value, not "unset"
        del zero["watchMemoryMb"]  # 1 MB free would also trip the watch
        self.assertEqual(self.go(zero, free=1).min_free_mb, 1)

    def test_a_refusal_before_the_start_needs_no_ollama(self):
        self.env(GIMG_OLLAMA_URL="ftp://nope")  # would be engine.ollama_url, but the memory comes first
        self.refused("engine.low_memory", free=1)


class OllamaTests(ProtBase):
    def serve(self, **kw):
        server = FakeOllama(self, **kw)
        self.env(GIMG_OLLAMA_URL=server.url)
        return server

    def test_abort_names_the_loaded_models(self):
        server = self.serve(models=[loaded("llama3:8b"), loaded("nomic-embed")])
        err = self.refused("engine.ollama_loaded")
        self.assertEqual(err.params["models"], "llama3:8b, nomic-embed")
        self.assertEqual(err.params["hint"], "ollama stop llama3:8b; ollama stop nomic-embed")
        self.assertIn("llama3:8b", err.message("en"))
        self.assertIn("ollama stop nomic-embed", err.message("es"))
        self.assertEqual(server.posts, [])  # abort never unloads

    def test_abort_is_the_default_when_the_profile_says_nothing(self):
        self.serve(models=[loaded("m")])
        machine = copy.deepcopy(self.machine)
        del machine["engine"]["ollama"]
        self.refused("engine.ollama_loaded", machine)

    def test_abort_with_the_service_off_goes_on(self):
        self.env(GIMG_OLLAMA_URL=dead_ollama_url())
        self.assertTrue(Path(self.go().log_path).is_file())

    def test_abort_with_nothing_loaded_goes_on(self):
        server = self.serve(models=[])
        self.go()
        self.assertEqual((server.ps_hits, server.posts), (1, []))

    def test_unload_empties_ollama_and_goes_on(self):
        server = self.serve(models=[loaded("a"), loaded("b:1")], unload_path="/api/generate")
        res = self.go(self.machine_with(ollama="unload"))
        self.assertEqual(server.posts, [("/api/generate", {"model": "a", "keep_alive": 0}),
                                        ("/api/embed", {"model": "a", "input": "", "keep_alive": 0}),
                                        ("/api/generate", {"model": "b:1", "keep_alive": 0}),
                                        ("/api/embed", {"model": "b:1", "input": "", "keep_alive": 0})])
        self.assertGreaterEqual(server.ps_hits, 2)  # it looked again after the unload
        self.assertIn("ollama: unloaded a, b:1", Path(res.log_path).read_text())

    def test_unload_of_an_embedding_model_works_through_api_embed(self):
        self.serve(models=[loaded("emb")], unload_path="/api/embed")
        self.go(self.machine_with(ollama="unload"))

    def test_unload_that_does_not_work_aborts_with_what_is_still_loaded(self):
        server = self.serve(models=[loaded("stuck")])
        err = self.refused("engine.ollama_loaded", self.machine_with(ollama="unload"))
        self.assertEqual(err.params["models"], "stuck")
        self.assertEqual([p for p, _ in server.posts], ["/api/generate", "/api/embed"])

    def test_unload_with_nothing_loaded_posts_nothing(self):
        server = self.serve(models=[])
        self.go(self.machine_with(ollama="unload"))
        self.assertEqual(server.posts, [])

    def test_ignore_never_asks(self):
        server = self.serve(models=[loaded("big")])
        res = self.go(self.machine_with(ollama="ignore"))
        self.assertEqual((server.ps_hits, server.posts), (0, []))
        self.assertIn("ollama check skipped", Path(res.log_path).read_text())

    def test_url_of_the_profile_and_the_environment_wins(self):
        server = FakeOllama(self, models=[loaded("viaprofile")])
        os.environ.pop("GIMG_OLLAMA_URL")
        err = self.refused("engine.ollama_loaded", self.machine_with(ollamaUrl=server.url + "/"))  # trailing /
        self.assertEqual(err.params["models"], "viaprofile")
        self.env(GIMG_OLLAMA_URL=dead_ollama_url())  # the environment beats the profile: nothing loaded there
        self.go(self.machine_with(ollamaUrl=server.url))

    def test_the_default_url_is_the_local_ollama(self):
        os.environ.pop("GIMG_OLLAMA_URL")
        self.assertEqual(engine_sdcpp.ollama_url(self.machine), "http://localhost:11434")
        self.assertEqual(engine_sdcpp.ollama_url({"engine": {"ollamaUrl": "https://h:1/x/"}}), "https://h:1/x")

    def test_a_url_that_is_not_http_is_refused_before_anything_is_opened(self):
        for url in ("file:///etc/passwd", "ftp://h/", "localhost:11434", "http://", "http://a b", "http://h\nx"):
            self.env(GIMG_OLLAMA_URL=url)
            err = self.refused("engine.ollama_url")
            self.assertEqual(err.params["url"], url)
            self.assertIn("GIMG_OLLAMA_URL", err.message("en"))

    # edge cases of /api/ps: each one counts as "nothing loaded" (or only what is well formed)

    def assert_goes_on(self, **kw):
        server = self.serve(**kw)
        self.go()
        self.assertEqual(server.ps_hits, 1)

    def test_ps_with_invalid_json(self):
        self.assert_goes_on(raw=b"{not json")

    def test_ps_with_an_empty_body(self):
        self.assert_goes_on(raw=b"")

    def test_ps_with_bytes_that_are_not_utf8(self):
        self.assert_goes_on(raw=b"\xff\xfe\x00")

    def test_ps_without_models(self):
        self.assert_goes_on(raw=b"{}")

    def test_ps_with_models_null_or_not_a_list(self):
        self.assert_goes_on(raw=b'{"models": null}')
        self.assert_goes_on(raw=b'{"models": {"name": "x", "size": 5}}')

    def test_ps_that_is_not_an_object(self):
        self.assert_goes_on(raw=b'[{"name": "x", "size": 5}]')

    def test_ps_with_entries_that_are_not_objects(self):
        self.assert_goes_on(raw=b'{"models": [1, "x", null, [2]]}')

    def test_ps_with_a_server_error(self):
        self.assert_goes_on(raw=json.dumps({"models": [loaded("x")]}).encode(), status=500)

    def test_models_without_a_usable_size_do_not_count(self):
        entries = [{"name": "nosize"}, {"name": "zero", "size": 0}, {"name": "neg", "size": -5},
                   {"name": "bool", "size": True}, {"name": "text", "size": "5"}, {"name": "null", "size": None}]
        self.assert_goes_on(models=entries)

    def test_a_model_with_size_counts_even_if_its_size_is_a_float(self):
        self.serve(models=[{"name": "f", "size": 1.5e9}])
        self.refused("engine.ollama_loaded")

    def test_a_loaded_model_without_a_name_is_still_a_loaded_model(self):
        self.serve(models=[{"size": 5}, {"model": "by-model-key", "size": 5}, {"name": 3, "size": 5}])
        err = self.refused("engine.ollama_loaded")
        self.assertEqual(err.params["models"], "(unnamed), by-model-key, (unnamed)")

    def test_a_slow_answer_past_the_timeout_counts_as_nothing_loaded(self):
        server = self.serve(models=[loaded("x")], block=True)
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        eng = self.make()
        eng.ollama_ps_timeout_s = 0.2
        t0 = time.monotonic()
        eng.generate(self.job(), lambda: False)
        self.assertLess(time.monotonic() - t0, 8)  # it did not wait for the 10 s of the server
        self.assertEqual(server.ps_hits, 1)

    def test_a_slow_answer_after_an_unload_does_not_hang(self):
        server = self.serve(models=[loaded("x")])
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        eng = self.make(self.machine_with(ollama="unload"))
        eng.ollama_ps_timeout_s = 0.2
        real = engine_sdcpp.ollama_unload

        def unload_then_block(url, name, timeout):
            real(url, name, timeout)
            server.block = True  # from now on /api/ps hangs: "nothing loaded" within the timeout

        with mock.patch.object(engine_sdcpp, "ollama_unload", unload_then_block):
            eng.generate(self.job(), lambda: False)


class WatchTests(ProtBase):
    def test_memory_below_the_threshold_kills_the_group(self):
        pid_file = self.tmp / "child.pid"
        self.env(FAKE_SD_SLEEP="30", FAKE_SD_CHILD_PID=str(pid_file))
        # plenty at the start; low once sd-cli is running (its child pid file exists)
        reader = lambda: 100 if pid_file.exists() else 20000
        t0 = time.monotonic()
        with self.assertRaises(engine.EngineError) as cm:
            self.make(free=reader).generate(self.job(), lambda: False)
        self.assertLess(time.monotonic() - t0, 10)
        err = cm.exception
        self.assertNotIsInstance(err, engine.EngineTimeout)
        self.assertEqual((err.code, err.params), ("engine.watch_memory", {"free_mb": 100, "watch_mb": 1500}))
        self.assertIn("100 MB free", err.message)
        self.assertIn("1500 MB", err.message)
        self.wait_dead(pid_file)

    def test_the_threshold_itself_does_not_kill(self):
        self.env(FAKE_SD_SLEEP="0.4")
        self.assertEqual(self.go(free=Seq(20000, 1500)).min_free_mb, 1500)

    def test_without_a_threshold_in_the_profile_nothing_is_watched(self):
        machine = copy.deepcopy(self.machine)
        del machine["watchMemoryMb"]
        self.env(FAKE_SD_SLEEP="0.4")
        self.assertEqual(self.go(machine, free=Seq(20000, 10)).min_free_mb, 10)

    def test_a_meminfo_that_disappears_while_running_does_not_kill(self):
        self.env(FAKE_SD_SLEEP="0.4")
        self.assertEqual(self.go(free=Seq(20000, None)).min_free_mb, 20000)

    def test_reported_free_zero_mb_in_the_log_kills_the_group(self):
        pid_file = self.tmp / "child.pid"
        self.env(FAKE_SD_SLEEP="30", FAKE_SD_CHILD_PID=str(pid_file), FAKE_SD_REPORT_ZERO="1")
        t0 = time.monotonic()
        with self.assertRaises(engine.EngineError) as cm:
            self.make().generate(self.job(), lambda: False)
        self.assertLess(time.monotonic() - t0, 10)
        self.assertEqual((cm.exception.code, cm.exception.params), ("engine.driver_no_memory", {}))
        self.assertIn("0.00 MB", cm.exception.message)
        self.wait_dead(pid_file)

    def test_min_free_mb_is_the_lowest_value_seen(self):
        self.env(FAKE_SD_SLEEP="0.6")
        seq = Seq(9000, 8000, 9500)
        res = self.go(free=seq)
        self.assertIn(8000, seq.served)
        self.assertEqual(res.min_free_mb, min(seq.served))
        self.assertEqual(res.min_free_mb, 8000)

    def test_a_new_attempt_starts_a_new_minimum(self):
        eng = self.make(free=Seq(900, 20000))
        eng.machine = self.machine_with()
        eng.machine["minFreeMemoryMb"] = 0
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        self.assertEqual(eng.generate(self.job(), lambda: False).min_free_mb, 900)
        self.assertEqual(eng.generate(self.job(), lambda: False).min_free_mb, 20000)


class LogReadingTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "x.log"
        self.run_state = engine_sdcpp._Run()

    def append(self, data):
        with open(self.path, "ab") as fh:
            fh.write(data)

    def read(self):
        return SdCppEngine._new_log_text(self.path, self.run_state)

    def test_only_the_new_part_is_read(self):
        self.append(b"a" * 4000)
        self.assertEqual(self.read(), "a" * 4000)
        self.assertEqual(self.run_state.log_pos, 4000)
        self.append(b"b")
        text = self.read()
        self.assertEqual(text, "a" * (len(engine_sdcpp.ZERO_FREE) - 1) + "b")  # the carry plus the new byte
        self.assertEqual(self.run_state.log_pos, 4001)

    def test_a_phrase_cut_by_the_read_boundary_is_found(self):
        phrase = engine_sdcpp.ZERO_FREE.encode()
        for cut in range(1, len(phrase)):
            self.run_state = engine_sdcpp._Run()
            self.path.write_bytes(b"x " + phrase[:cut])
            self.assertNotIn(engine_sdcpp.ZERO_FREE, self.read())
            self.append(phrase[cut:])
            self.assertIn(engine_sdcpp.ZERO_FREE, self.read(), cut)

    def test_a_missing_log_reads_nothing(self):
        self.assertEqual(self.read(), "")

    def test_bytes_that_are_not_utf8_do_not_raise(self):
        self.append(b"\xff\xfe reported free 0.00 MB \x80")
        self.assertIn(engine_sdcpp.ZERO_FREE, self.read())


class WorkerTests(QueueBase):
    """Each guard through the worker: the entry fails with the guard's code and text, and nothing is left behind."""

    def setUp(self):
        super().setUp()
        self.protections = protections_off_env(self.tmp)
        env = mock.patch.dict(os.environ, {"GIMG_MODELS_HOME": str(self.tmp / "models"), "GIMG_SD_CLI": str(FAKE),
                                           **self.protections})
        env.start()
        self.addCleanup(env.stop)
        for var in ("FAKE_SD_SLEEP", "FAKE_SD_REPORT_ZERO", "FAKE_SD_CHILD_PID"):
            os.environ.pop(var, None)
        from gimg import limits, models
        self.machine = limits.load_machine("steam-deck")
        for kind, entry in models.load_catalog()["models"][MODEL]["files"].items():
            (self.tmp / "models" / kind).mkdir(parents=True, exist_ok=True)
            (self.tmp / "models" / kind / entry["name"]).touch()

    def folder(self):
        return orders.pending_image_path("proj", "a", "banner", 1).parent

    def lines(self):
        path = log.log_path("proj")
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

    def run_with(self, free, **env):
        self.push()
        with mock.patch.dict(os.environ, env):
            worker.run(engine=SdCppEngine(poll_s=0.05, kill_grace_s=2, read_meminfo=free))
        return queue.get(1)

    def assert_clean_failure(self, entry, code):
        self.assertEqual((entry["state"], entry["error"]["code"]), ("failed", code))
        left = [p.name for p in self.folder().iterdir()] if self.folder().exists() else []
        self.assertEqual(left, [])  # no image, no pending log, no preview
        text_en, text_es = queue.error_text(entry, "en"), queue.error_text(entry, "es")
        self.assertNotEqual(text_en, text_es)
        self.assertNotIn("{", text_en + text_es)
        self.assertEqual([line["app.error"] for line in self.lines()], [text_en])
        return text_en

    def test_low_memory_fails_the_entry_with_the_numbers(self):
        entry = self.run_with(lambda: 2500)
        text = self.assert_clean_failure(entry, "engine.low_memory")
        self.assertEqual(entry["error"]["params"], {"free_mb": 2500, "needed_mb": 7000})
        self.assertIn("2500", text)

    def test_ollama_loaded_fails_the_entry_with_the_models(self):
        server = FakeOllama(self, models=[loaded("llama3:8b")])
        entry = self.run_with(lambda: 20000, GIMG_OLLAMA_URL=server.url)
        text = self.assert_clean_failure(entry, "engine.ollama_loaded")
        self.assertIn("llama3:8b", text)

    def test_watch_memory_fails_the_entry_and_removes_the_log_of_the_attempt(self):
        pid_file = self.tmp / "child.pid"
        entry = self.run_with(lambda: 100 if pid_file.exists() else 20000, FAKE_SD_SLEEP="30",
                              FAKE_SD_CHILD_PID=str(pid_file))
        text = self.assert_clean_failure(entry, "engine.watch_memory")
        self.assertEqual(entry["error"]["params"], {"free_mb": 100, "watch_mb": 1500})
        self.assertIn("100 MB", text)

    def test_driver_without_memory_fails_the_entry(self):
        entry = self.run_with(lambda: 20000, FAKE_SD_SLEEP="30", FAKE_SD_REPORT_ZERO="1")
        self.assert_clean_failure(entry, "engine.driver_no_memory")

    def test_min_free_mb_reaches_the_log_of_the_project(self):
        entry = self.run_with(lambda: 12345)
        self.assertEqual(entry["state"], "done")
        self.assertEqual([line["app.image.min_free_mb"] for line in self.lines()], [12345])
        self.assertEqual(sorted(p.name for p in self.folder().iterdir()), ["q1.log", "q1.png"])


class LocaleTests(unittest.TestCase):
    CODES = ("low_memory", "ollama_loaded", "ollama_url", "watch_memory", "driver_no_memory")

    def test_the_guard_messages_exist_in_both_languages_and_differ(self):
        from gimg import i18n
        params = dict(free_mb=1, needed_mb=2, models="m", hint="h", url="u", watch_mb=3)
        for code in self.CODES:
            en, es = i18n.t("error.engine." + code, "en", **params), i18n.t("error.engine." + code, "es", **params)
            self.assertNotEqual(en, es, code)
            for text in (en, es):
                self.assertNotIn("{", text)
                self.assertFalse(text.startswith("error."), code)


if __name__ == "__main__":
    unittest.main()
