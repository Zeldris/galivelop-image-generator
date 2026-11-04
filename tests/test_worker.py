import fcntl
import io
import json
import os
import signal
import struct
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from gimg import engine, log, models, orders, queue, worker
from gimg.errors import GimgError
from tests.test_engine_sdcpp import FAKE, MODEL, alive, protections_off_env, wait_for_file
from tests.test_queue import QueueBase


class StubEngine(engine.Engine):
    provider = "fake"

    def __init__(self, error=None):
        self.error = error

    def generate(self, job, should_cancel):
        raise self.error


class WorkerTests(QueueBase):
    def lines(self, project="proj"):
        path = log.log_path(project)
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text().splitlines()]

    def leftovers(self):
        return [p for p in (self.tmp / "data" / "projects").rglob("*")
                if p.is_file() and p.suffix in (".png", ".tmp") or p.name.startswith(".pending")]

    def test_success(self):
        self.push(count=2, seed=7)
        self.assertEqual(worker.run(), 2)
        for n, seed in ((1, 7), (2, 8)):
            entry = queue.get(n)
            self.assertEqual((entry["state"], entry["attemptId"], entry["error"]), ("done", n, None))
        order = orders.get("proj", "a", "banner")
        self.assertEqual([a["id"] for a in order["attempts"]], [1, 2])
        self.assertEqual(order["attempts"][1]["seed"], 8)
        attempt = orders.get("proj", "a", "banner")["attempts"][0]
        self.assertEqual((attempt["image"], attempt["queueEntry"]), ("attempts/q1.png", 1))
        png = orders.attempt_image("proj", "a", "banner", attempt).read_bytes()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", png[16:24]), (1280, 512))
        names = {p.name for p in orders.pending_image_path("proj", "a", "banner", 1).parent.iterdir()}
        self.assertEqual(names, {"q1.png", "q2.png"})  # no temp left
        lines = self.lines()
        self.assertEqual(len(lines), 2)
        first = lines[0]
        self.assertNotIn("app.error", first)
        self.assertEqual((first["gen_ai.provider.name"], first["app.task"], first["app.image.key"],
                          first["app.image.seed"], first["app.image.steps"], first["app.machine_profile"],
                          first["app.image.references"], first["app.image.engine_version"]),
                         ("fake", "banner", "a", 7, 6, "steam-deck", 0, engine.FAKE_VERSION))
        self.assertIn("app.duration_ms", first)

    def test_once_and_empty(self):
        self.assertEqual(worker.run(), 0)
        self.push(count=3)
        self.assertEqual(worker.run(once=True), 1)
        self.assertEqual([e["state"] for e in queue.list_entries()], ["done", "queued", "queued"])
        self.assertEqual(worker.run(), 2)

    def test_fifo_across_projects(self):
        self.push("proj", "a")
        self.push("other", "b")
        worker.run()
        self.assertEqual([(e["project"], e["state"]) for e in queue.list_entries()],
                         [("proj", "done"), ("other", "done")])
        self.assertEqual(len(self.lines("proj")), 1)
        self.assertEqual(len(self.lines("other")), 1)

    def test_engine_from_env(self):
        self.push()
        with mock.patch.dict(os.environ, {"GIMG_FAKE_FAIL": "out of vram"}):
            worker.run()
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]),
                         ("failed", {"code": "engine.failed", "params": {"message": "out of vram"}}))

    def test_engine_failure(self):
        self.push()
        worker.run(engine=engine.FakeEngine(fail_with="boom"))
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"], entry["attemptId"]), ("failed", {"code": "engine.failed", "params": {"message": "boom"}}, None))
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"], [])
        self.assertEqual(self.lines()[0]["app.error"], "the engine failed: boom")
        self.assertNotIn("app.duration_ms", self.lines()[0])
        self.assertEqual(self.leftovers(), [])

    def test_timeout(self):
        self.push()
        worker.run(engine=StubEngine(engine.EngineTimeout()))
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]), ("failed", {"code": "engine.timeout", "params": {}}))
        self.assertEqual(self.lines()[0]["app.error"], queue.error_text(entry["error"], "en"))

    def test_timeout_s_comes_from_machine(self):
        seen = []

        class Spy(engine.FakeEngine):
            def generate(self, job, should_cancel):
                seen.append((job.timeout_s, job.machine.get("name"), job.references))
                return super().generate(job, should_cancel)

        self.push()
        worker.run(engine=Spy())
        self.assertEqual(seen, [(900, "steam-deck", [])])

    def test_unexpected_error_fails_entry_and_continues(self):
        self.push(count=2)
        worker.run(engine=StubEngine(ValueError("bug")))
        self.assertEqual([(e["state"], e["error"]) for e in queue.list_entries()],
                         [("failed", {"code": "worker.unexpected",
                                      "params": {"message": "ValueError: bug"}})] * 2)

    def test_limits_rechecked_at_run(self):
        self.push()
        profile = self.tmp / "tight.json"
        profile.write_text(json.dumps({"name": "tight", "minFreeMemoryMb": 1, "watchMemoryMb": 1,
                                       "maxReferences": 1, "timeoutS": 5, "maxSteps": 2,
                                       "maxPixels": 1048576}))
        with mock.patch.dict(os.environ, {"GIMG_MACHINE_PROFILE": str(profile)}):
            worker.run()
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]), ("failed", {"code": "limit.steps", "params": {"steps": 6, "max": 2}}))
        self.assertEqual(self.lines()[0]["app.error"], queue.error_text(entry["error"], "en"))
        self.assertIn("6", self.lines()[0]["app.error"])
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"], [])

    def test_references_resolved(self):
        (self.projects["proj"] / "refs").mkdir()
        (self.projects["proj"] / "refs" / "r.png").write_bytes(b"x")
        orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "p", "references": ["refs/r.png"]})
        self.push()
        seen = []

        class Spy(engine.FakeEngine):
            def generate(self, job, should_cancel):
                seen.append(job.references)
                return super().generate(job, should_cancel)

        worker.run(engine=Spy())
        self.assertEqual(queue.get(1)["state"], "done")
        self.assertEqual(seen, [[str(self.projects["proj"].resolve() / "refs" / "r.png")]])
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"][0]["references"], ["refs/r.png"])
        self.assertEqual(self.lines()[0]["app.image.references"], 1)

    def test_reference_missing_or_directory(self):
        (self.projects["proj"] / "adir").mkdir()
        for ref in ("nope.png", "adir"):
            orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "p", "references": [ref]})
            entry = self.push()[0]
            worker.run()
            done = queue.get(entry["id"])
            self.assertEqual((done["state"], done["error"]), ("failed", {"code": "worker.reference_missing", "params": {"path": ref}}), ref)
        self.assertIn("nope.png", self.lines()[0]["app.error"])

    def test_reference_outside_project(self):
        outside = self.tmp / "secret.png"
        outside.write_bytes(b"x")
        (self.projects["proj"] / "link.png").symlink_to(outside)
        orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "p"})
        for ref, code in (("../secret.png", "path.dotdot"), ("/etc/passwd", "path.absolute"),
                          ("link.png", "path.outside")):
            entry = queue.enqueue("proj", "a", "banner", [{"seed": 1, "prompt": "p", "params": {},
                                                           "references": [ref]}])[0]
            worker.run()
            done = queue.get(entry["id"])
            self.assertEqual((done["state"], done["error"]["code"]), ("failed", code), ref)

    def test_cancel_running(self):
        self.push()
        eng = engine.FakeEngine(delay_s=5)
        thread = threading.Thread(target=worker.run, kwargs={"engine": eng})
        thread.start()
        deadline = time.monotonic() + 5
        while queue.get(1)["state"] != "running" and time.monotonic() < deadline:
            time.sleep(0.01)
        started = time.monotonic()
        queue.cancel(1)
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertLess(time.monotonic() - started, 2)
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["attemptId"]), ("cancelled", None))
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"], [])
        self.assertEqual(self.lines(), [])
        self.assertEqual(self.leftovers(), [])

    def test_cancel_requested_after_generation_leaves_no_image(self):
        self.push()

        class Late(engine.FakeEngine):
            def generate(self, job, should_cancel):
                result = super().generate(job, lambda: False)
                queue.cancel(1)
                return result

        worker.run(engine=Late())
        self.assertEqual(queue.get(1)["state"], "cancelled")
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"], [])
        self.assertEqual(self.leftovers(), [])

    def test_cancelled_queued_is_skipped(self):
        self.push(count=2)
        queue.cancel(1)
        self.assertEqual(worker.run(), 1)
        self.assertEqual([e["state"] for e in queue.list_entries()], ["cancelled", "done"])

    def test_second_worker_refused_same_process(self):
        worker.lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(worker.lock_path()), os.O_RDWR | os.O_CREAT)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX)
        self.push()
        self.assertEqual(self.code(worker.run), "worker.already_running")
        self.assertEqual(queue.get(1)["state"], "queued")  # nothing was taken

    def test_second_worker_refused_other_process(self):
        self.push()
        code = ("import sys,time\nfrom gimg import worker, engine\n"
                "worker.run(engine=engine.FakeEngine(delay_s=3))\n")
        proc = subprocess.Popen([sys.executable, "-c", code], cwd=str(Path(__file__).resolve().parent.parent),
                                env=dict(os.environ))
        try:
            deadline = time.monotonic() + 10
            while queue.get(1)["state"] != "running" and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertEqual(queue.get(1)["pid"], proc.pid)
            self.assertEqual(self.code(worker.run), "worker.already_running")
            queue.cancel(1)
            proc.wait(10)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        self.assertEqual(queue.get(1)["state"], "cancelled")
        self.assertEqual(worker.run(), 0)  # the lock is free again

    def test_lock_released_after_run(self):
        worker.run()
        worker.run()

    def test_dead_worker_entry_is_run_again(self):
        self.push()
        queue.claim()  # its pid is this live process: only the worker lock decides
        self.assertEqual(worker.run(), 1)
        self.assertEqual(queue.get(1)["state"], "done")

    def test_worker_recovers_and_deletes_pending_before_its_loop(self):
        self.push()
        queue.claim()
        pending = orders.pending_image_path("proj", "a", "banner", 1)
        pending.parent.mkdir(parents=True)
        pending.write_bytes(b"half")
        seen = []

        class Spy(engine.FakeEngine):
            def generate(self, job, should_cancel):
                seen.append(Path(job.output).exists())
                return super().generate(job, should_cancel)

        worker.run(engine=Spy())
        self.assertEqual(seen, [False])
        self.assertEqual(queue.get(1)["state"], "done")
        self.assertEqual(self.leftovers(), [orders.attempt_image(
            "proj", "a", "banner", orders.get("proj", "a", "banner")["attempts"][0])])

    def test_crash_after_add_attempt_does_not_duplicate(self):
        self.push()
        real = queue.finish
        with mock.patch.object(queue, "finish", side_effect=KeyboardInterrupt):  # a hard stop, not an Exception
            with self.assertRaises(KeyboardInterrupt):
                worker.run()
        self.assertEqual(len(orders.get("proj", "a", "banner")["attempts"]), 1)
        self.assertEqual(queue.get(1)["state"], "queued")  # recovery: the worker is gone
        worker.run(engine=StubEngine(AssertionError("the engine must not run again")))
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["attemptId"], entry["error"]), ("done", 1, None))
        attempts = orders.get("proj", "a", "banner")["attempts"]
        self.assertEqual([(a["id"], a["queueEntry"]) for a in attempts], [(1, 1)])
        self.assertTrue(orders.attempt_image("proj", "a", "banner", attempts[0]).is_file())
        self.assertEqual(len(self.lines()), 1)
        self.assertIs(queue.finish, real)

    def test_failing_finish_done_keeps_loop_and_writes_no_failure_line(self):
        self.push(count=2)
        real = queue.finish
        calls = []

        def flaky(*args, **kwargs):
            calls.append(args[0])
            if len(calls) == 1:
                raise GimgError("queue.corrupt", path="x")
            return real(*args, **kwargs)

        with mock.patch.object(queue, "finish", side_effect=flaky):
            self.assertEqual(worker.run(), 2)
        self.assertEqual(calls, [1, 2])
        lines = self.lines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(all("app.error" not in x for x in lines))
        self.assertEqual(queue.get(2)["state"], "done")
        self.assertEqual(queue.get(1)["state"], "queued")  # was left running; the next recovery re-queues it
        worker.run()
        self.assertEqual(len(orders.get("proj", "a", "banner")["attempts"]), 2)  # no duplicate for entry 1
        self.assertEqual(queue.get(1)["state"], "done")

    def test_failing_finish_in_failure_handler_keeps_loop(self):
        self.push(count=2)
        real = queue.finish
        calls = []

        def flaky(*args, **kwargs):
            calls.append(args[0])
            if len(calls) == 1:
                raise GimgError("queue.corrupt", path="x")
            return real(*args, **kwargs)

        with mock.patch.object(queue, "finish", side_effect=flaky):
            self.assertEqual(worker.run(engine=engine.FakeEngine(fail_with="boom")), 2)
        self.assertEqual(calls, [1, 2])
        self.assertEqual(queue.get(2)["error"]["code"], "engine.failed")

    def test_schema_errors_survive_in_the_entry_error(self):
        from gimg import schema
        self.push()
        boom = GimgError("order.invalid", errors=[schema.ValidationError("/prompt", "maxLength", {"limit": 4000})])
        worker.run(engine=StubEngine(boom))
        entry = queue.get(1)
        self.assertEqual(entry["error"]["errors"][0]["path"], "/prompt")
        self.assertIn("/prompt: must be at most 4000 characters", queue.error_text(entry, "en"))

    def finish_message(self, lang):
        self.push()
        with mock.patch.object(queue, "finish", side_effect=GimgError("queue.corrupt", path="x")), \
                mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            worker.run(lang=lang, once=True)
        return err.getvalue()

    def test_worker_messages_use_the_given_language(self):
        self.assertIn("could not finish queue entry 1", self.finish_message("en"))

    def test_worker_messages_in_spanish(self):
        self.assertIn("no se pudo cerrar la entrada 1", self.finish_message("es"))

    def test_failing_log_line_does_not_fail_the_entry(self):
        self.push()
        with mock.patch.object(log, "append", side_effect=OSError("disk full")):
            worker.run()
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["attemptId"], entry["error"]), ("done", 1, None))

    def test_add_attempt_failure_leaves_no_image(self):
        self.push()
        with mock.patch.object(orders, "add_attempt", side_effect=GimgError("order.corrupt", path="x")):
            worker.run()
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]["code"]), ("failed", "order.corrupt"))
        self.assertEqual(self.leftovers(), [])

    def test_estimate_after_runs(self):
        entry = self.push(count=3)[0]
        self.assertIsNone(queue.estimate_for(entry))
        worker.run()
        estimate = queue.estimate_for(entry)
        self.assertIsNotNone(estimate)
        durations = sorted(x["app.duration_ms"] for x in self.lines())
        self.assertEqual(estimate, durations[1])
        worker.run(engine=engine.FakeEngine(fail_with="x"))  # errors do not count
        self.assertEqual(queue.estimate_for(entry), estimate)


@unittest.skipUnless(hasattr(os, "killpg"), "needs process groups")
class WorkerSignalTests(QueueBase):
    """A worker killed by SIGTERM or SIGHUP must not leave `sd-cli` (own session) running."""

    def setUp(self):
        super().setUp()
        for kind, entry in models.load_catalog()["models"][MODEL]["files"].items():
            path = self.tmp / "models" / kind / entry["name"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    def stop_worker_with(self, signum):
        self.push()
        pids = {name: self.tmp / (name + ".pid") for name in ("sd", "child")}
        env = dict(os.environ, GIMG_MODELS_HOME=str(self.tmp / "models"), GIMG_SD_CLI=str(FAKE),
                   GIMG_ENGINE="sdcpp", FAKE_SD_SLEEP="60", FAKE_SD_PID=str(pids["sd"]),
                   FAKE_SD_CHILD_PID=str(pids["child"]), **protections_off_env(self.tmp))
        proc = subprocess.Popen([sys.executable, "-m", "gimg", "work"], env=env, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, cwd=str(Path(__file__).resolve().parent.parent))
        found = []
        try:
            for path in pids.values():
                self.assertTrue(wait_for_file(path), "the fake sd-cli did not start")
            time.sleep(0.2)  # let both pid files be complete
            found = [int(path.read_text()) for path in pids.values()]
            proc.send_signal(signum)
            proc.wait(15)
            for pid in found:
                for _ in range(100):
                    if not alive(pid):
                        break
                    time.sleep(0.1)
                self.assertFalse(alive(pid), "pid %d survived the worker" % pid)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            for pid in found:
                if alive(pid):
                    os.kill(pid, signal.SIGKILL)
        return proc.returncode

    def check_after(self, code, signum):
        self.assertEqual(code, 128 + signum)
        folder = orders.pending_image_path("proj", "a", "banner", 1).parent  # before any queue read recovers it
        left = [p.name for p in folder.iterdir()] if folder.exists() else []
        self.assertEqual([n for n in left if n.startswith(".pending")], [])
        # as after Ctrl-C the entry was left running; with no worker alive any read requeues it
        self.assertEqual(queue.get(1)["state"], "queued")

    def test_sigterm_kills_sd_cli_and_its_children(self):
        self.check_after(self.stop_worker_with(signal.SIGTERM), signal.SIGTERM)

    @unittest.skipUnless(hasattr(signal, "SIGHUP"), "needs SIGHUP")
    def test_sighup_kills_sd_cli_and_its_children(self):
        self.check_after(self.stop_worker_with(signal.SIGHUP), signal.SIGHUP)

    def test_handlers_are_restored_after_run(self):
        names = [n for n in ("SIGTERM", "SIGHUP") if hasattr(signal, n)]
        before = {n: signal.getsignal(getattr(signal, n)) for n in names}
        seen = {}

        class Spy(engine.FakeEngine):
            def generate(self, job, should_cancel):
                seen.update({n: signal.getsignal(getattr(signal, n)) for n in names})
                return super().generate(job, should_cancel)

        self.push()
        worker.run(engine=Spy())
        for n in names:
            self.assertIs(seen[n], worker._terminate)
            self.assertEqual(signal.getsignal(getattr(signal, n)), before[n])
