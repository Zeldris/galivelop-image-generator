import fcntl
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from gimg import engine, engine_sdcpp, log, orders, png, projects, queue, worker
from gimg.engine_sdcpp import SdCppEngine, parse_progress
from gimg.errors import GimgError
from tests.test_cli import CliBase
from tests.test_engine_sdcpp import Base, WorkerTests
from tests.test_queue import QueueBase

# Pieces of piloto/r0/portal/logs/og-s3.log (the real sd-cli): bars are split by \r and end with \x1b[K.
STEP3 = "\r  |=========================>                        | 3/6 -  24.65s/it - ETA 01:16\x1b[K"
STEP6 = "\r  |==================================================| 6/6 -  24.28s/it\x1b[K\n"
VAE = ("\r  |=>                                                |  1/36 -   1.07s/it - ETA 00:37\x1b[K"
       "\r  |==>                                               |  2/36 -   1.27it/s - ETA 00:31\x1b[K")
LOAD = "\r  |##################################################| 140/140 - 527.77MB/s\x1b[K\n"
SAMPLED = "[I] sampling completed, taking 149.61s --- image.cpp:907\n"


class ParseProgressTests(unittest.TestCase):
    def test_a_real_step_bar(self):
        self.assertEqual(parse_progress(STEP3, 6)[0], {"step": 3, "steps": 6, "etaS": 76})

    def test_the_last_bar_has_no_eta(self):
        self.assertEqual(parse_progress(STEP6, 6)[0], {"step": 6, "steps": 6, "etaS": None})

    def test_the_last_of_several_bars_wins(self):
        text = "[V] loading 12/149 tensors" + STEP3 + STEP6
        self.assertEqual(parse_progress(text, 6)[0]["step"], 6)

    def test_two_bars_the_vae_one_after_sampling_is_ignored(self):
        text = STEP6 + SAMPLED + "[V] processing 36 tiles\n" + VAE
        self.assertEqual(parse_progress(text, 6), ({"step": 6, "steps": 6, "etaS": None}, True))
        # no marker and no bar with the jobs total: the first bar sets the total (an engine that reports other steps)
        self.assertEqual(parse_progress(VAE, 6)[0]["steps"], 36)
        self.assertEqual(parse_progress(VAE, 6, sampled=True), (None, True))

    def test_a_bar_whose_total_is_not_the_jobs_is_ignored(self):
        self.assertEqual(parse_progress(VAE + STEP3, 6)[0], {"step": 3, "steps": 6, "etaS": 76})

    def test_without_the_jobs_steps_the_first_bar_sets_the_total(self):
        self.assertEqual(parse_progress(STEP3 + VAE, 4)[0], {"step": 3, "steps": 6, "etaS": 76})
        self.assertEqual(parse_progress(STEP3, None)[0]["steps"], 6)

    def test_it_per_second_and_hours(self):
        self.assertEqual(parse_progress("|=| 2/36 -   1.27it/s - ETA 00:31\x1b[K", 36)[0],
                         {"step": 2, "steps": 36, "etaS": 31})
        self.assertEqual(parse_progress("|=| 1/6 -  9.0s/it - ETA 1:02:03\x1b[K", 6)[0]["etaS"], 3723)

    def test_the_weight_loading_bar_is_not_a_step_bar(self):
        self.assertEqual(parse_progress(LOAD, 140), (None, False))

    def test_nonsense_numbers_are_ignored(self):
        self.assertEqual(parse_progress("|=| 7/6 - 1.0s/it\x1b[K |=| 0/0 - 1.0s/it\x1b[K", None), (None, False))

    def test_an_unfinished_bar_does_not_count(self):
        for cut in range(STEP3.index("\x1b")):  # the ESC that ends the bar is what makes it complete
            progress = parse_progress(STEP3[:cut], 6)[0]
            self.assertIsNone(progress, STEP3[:cut])  # also the ones cut inside "ETA 01:16", which must not read 1:1

    def test_the_marker_is_found_whatever_the_lines_are(self):
        self.assertEqual(parse_progress("x" + SAMPLED, 6), (None, True))


class Collector:
    def __init__(self):
        self.events = []

    def __call__(self, progress):
        self.events.append(dict(progress))


class FeedTests(unittest.TestCase):
    """`SdCppEngine._report_progress` with the log arriving in pieces."""

    def feed(self, pieces, steps=6, callback=None):
        run = engine_sdcpp._Run(steps=steps)
        got = callback or Collector()
        job = engine.EngineJob(prompt="p", width=1, height=1, seed=1, output="x", on_progress=got)
        for piece in pieces:
            run.new = piece
            SdCppEngine._report_progress(run, job)
        return got

    def test_a_bar_cut_at_any_byte_is_read_whole_on_the_next_tick(self):
        text = "[I] loading\n" + STEP3
        for cut in range(len(text) + 1):
            got = self.feed([text[:cut], text[cut:]])
            self.assertEqual(got.events, [{"step": 3, "steps": 6, "etaS": 76}], cut)

    def test_the_marker_cut_between_reads_still_closes_the_step_bar(self):
        text = STEP6 + SAMPLED + VAE
        for cut in range(len(text) + 1):
            got = self.feed([text[:cut], text[cut:]])
            self.assertEqual(got.events[-1:], [{"step": 6, "steps": 6, "etaS": None}], cut)
            self.assertTrue(all(e["steps"] == 6 for e in got.events), cut)

    def test_one_byte_at_a_time(self):
        text = STEP3 + "\r" + STEP6 + SAMPLED + VAE
        got = self.feed(list(text))
        self.assertEqual([(e["step"], e["steps"]) for e in got.events], [(3, 6), (6, 6)])

    def test_the_same_step_is_reported_once(self):
        got = self.feed([STEP3, "[V] something\n", STEP3])
        self.assertEqual(len(got.events), 1)

    def test_a_callback_that_raises_does_not_stop_the_run(self):
        def boom(progress):
            raise RuntimeError("queue gone")

        self.feed([STEP3, STEP6], callback=boom)  # must not raise

    def test_no_callback_no_work(self):
        run = engine_sdcpp._Run(steps=6)
        run.new = STEP3
        SdCppEngine._report_progress(run, engine.EngineJob(prompt="p", width=1, height=1, seed=1, output="x"))

    def test_the_carry_stays_small(self):
        run = engine_sdcpp._Run(steps=6)
        job = engine.EngineJob(prompt="p", width=1, height=1, seed=1, output="x")
        run.new = "a" * 10000
        SdCppEngine._report_progress(run, job)
        self.assertEqual(len(run.bar_carry), engine_sdcpp.BAR_CARRY_MAX)


class EngineProgressTests(Base):
    def test_events_from_a_fake_sd_cli_gated_by_a_file(self):
        gate = self.tmp / "gate"
        events = []

        def on_progress(progress):
            events.append(dict(progress))
            if progress["step"] == 3:
                gate.write_text("go")

        self.env(FAKE_SD_GATE=str(gate), FAKE_SD_GATE_AFTER="3")
        _, job, res = self.run_job(steps=6, on_progress=on_progress)
        self.assertIn({"step": 3, "steps": 6, "etaS": 3}, events)
        self.assertEqual(sorted(events, key=lambda e: e["step"]), events)
        self.assertTrue(all(e["steps"] == 6 for e in events))  # the 36-tile bar of the VAE never shows
        self.assertEqual(res.params["steps"], 6)

    def test_result_has_the_d34_fields(self):
        _, job, res = self.run_job()
        names = {k: Path(self.md(k)).name for k in ("diffusion", "text", "vae")}
        self.assertEqual((res.model_files, res.backend, res.draft, res.compose), (names, "vulkan", False, None))
        self.assertEqual(res.params, {"steps": 6, "cfg": 1, "sampler": "euler"})
        self.assertEqual(res.command[0], "sd-cli")

    def test_backend_and_threads_from_the_args(self):
        self.assertEqual(engine_sdcpp._backend(["--backend", "diffusion=cpu", "-t", "8"]), "cpu")
        self.assertEqual(engine_sdcpp._backend(["--backend", "vae=cpu,diffusion=cpu"]), "cpu")
        self.assertEqual(engine_sdcpp._backend(["--backend", "vae=cpu"]), "vulkan")
        self.assertEqual(engine_sdcpp._backend(["--max-vram", "vulkan0=2"]), "vulkan")
        self.assertEqual(engine_sdcpp._threads(["-t", "4", "x", "-t", "8"]), 8)
        self.assertEqual(engine_sdcpp._threads(["--threads", "0", "-t", "abc"]), None)
        self.assertEqual(engine_sdcpp._threads([]), None)


class SetProgressTests(QueueBase):
    def running(self):
        self.push()
        entry = queue.claim()
        self.hold_worker_lock()  # as the worker does: without it any read would find the running entry dead
        return entry

    def test_stores_and_replaces_progress_on_a_running_entry(self):
        entry = self.running()
        queue.set_progress(entry["id"], {"step": 1, "steps": 6, "etaS": 120})
        self.assertEqual(queue.get(entry["id"])["progress"], {"step": 1, "steps": 6, "etaS": 120})
        queue.set_progress(entry["id"], {"step": 6, "steps": 6, "etaS": None})
        self.assertEqual(queue.get(entry["id"])["progress"], {"step": 6, "steps": 6, "etaS": None})

    def test_an_identical_pulse_does_not_rewrite_the_file(self):
        entry = self.running()
        progress = {"step": 2, "steps": 6, "etaS": 90}
        queue.set_progress(entry["id"], progress)
        with mock.patch("gimg.queue.fsutil.write_json") as write:
            queue.set_progress(entry["id"], dict(progress))
        write.assert_not_called()

    def test_only_a_running_entry_takes_it(self):
        self.push()
        self.assertEqual(self.code(queue.set_progress, 1, {"step": 1, "steps": 2, "etaS": None}), "queue.not_running")
        entry = queue.claim()
        queue.finish(entry["id"], "done")
        self.assertEqual(self.code(queue.set_progress, 1, {"step": 1, "steps": 2, "etaS": None}), "queue.not_running")
        self.assertEqual(self.code(queue.set_progress, 99, {"step": 1, "steps": 2, "etaS": None}), "queue.unknown")

    def test_bad_progress_is_refused_and_nothing_is_stored(self):
        entry = self.running()
        bad = [None, "3/6", {}, {"step": 1, "steps": 6}, {"step": 1, "steps": 6, "etaS": None, "x": 1},
               {"step": True, "steps": 6, "etaS": None}, {"step": 7, "steps": 6, "etaS": None},
               {"step": -1, "steps": 6, "etaS": None}, {"step": 0, "steps": 0, "etaS": None},
               {"step": 1.0, "steps": 6, "etaS": None}, {"step": 1, "steps": 6, "etaS": "5"},
               {"step": 1, "steps": 6, "etaS": -1}, {"step": 1, "steps": 6, "etaS": True}]
        for item in bad:
            self.assertEqual(self.code(queue.set_progress, entry["id"], item), "queue.bad_progress", item)
        self.assertNotIn("progress", queue.get(entry["id"]))

    def test_preview_must_be_a_clean_path(self):
        entry = self.running()
        for item in ("", None, 3, "a\nb", "a\x00b"):
            self.assertEqual(self.code(queue.set_preview, entry["id"], item), "queue.bad_progress", item)
        queue.set_preview(entry["id"], "/d/.pending-1.preview.png")
        self.assertEqual(queue.get(entry["id"])["preview"], "/d/.pending-1.preview.png")

    def test_finishing_or_requeuing_clears_progress_and_preview(self):
        entry = self.running()
        queue.set_progress(entry["id"], {"step": 1, "steps": 6, "etaS": 1})
        queue.set_preview(entry["id"], "/p.png")
        queue.recover_orphans()  # the entry is dead: back to queued (own_lock: the caller says it holds the worker lock)
        got = queue.get(entry["id"])
        self.assertEqual(got["state"], "queued")
        self.assertNotIn("progress", got)
        self.assertNotIn("preview", got)
        entry = queue.claim()
        queue.set_progress(entry["id"], {"step": 1, "steps": 6, "etaS": 1})
        queue.set_preview(entry["id"], "/p.png")
        queue.finish(entry["id"], "failed", error="engine.failed")
        got = queue.get(entry["id"])
        self.assertNotIn("progress", got)
        self.assertNotIn("preview", got)


class QueueListTests(CliBase):
    def make(self):
        name = projects.add(self.root)
        orders.submit(name, {"key": "a", "profile": "banner", "prompt": "a cat"})
        queue.enqueue(name, "a", "banner", orders.attempt_specs(name, "a", "banner", 1))
        entry = queue.claim()
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)  # pretend the worker is alive
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, fd)
        return entry

    def test_list_prints_progress_eta_and_the_preview_of_a_running_entry(self):
        entry = self.make()
        preview = self.tmp / "p.preview.png"
        preview.write_bytes(b"x")
        queue.set_progress(entry["id"], {"step": 3, "steps": 6, "etaS": 76})
        queue.set_preview(entry["id"], str(preview))
        out = self.ok("queue", "list")
        self.assertIn("      progress: 3/6 · ETA 1:16\n", out)
        self.assertIn("      preview: %s\n" % preview, out)
        out = self.ok("--lang", "es", "queue", "list")
        self.assertIn("      progreso: 3/6 · faltan 1:16\n", out)
        self.assertIn("      vista previa: %s\n" % preview, out)

    def test_without_eta_with_hours_and_with_a_preview_that_is_not_there_yet(self):
        entry = self.make()
        queue.set_progress(entry["id"], {"step": 6, "steps": 6, "etaS": None})
        queue.set_preview(entry["id"], str(self.tmp / "none.png"))
        out = self.ok("queue", "list")
        self.assertIn("      progress: 6/6\n", out)
        self.assertNotIn("ETA", out)
        self.assertNotIn("preview", out)
        queue.set_progress(entry["id"], {"step": 1, "steps": 16, "etaS": 3723})
        self.assertIn("progress: 1/16 · ETA 1:02:03\n", self.ok("queue", "list"))

    def test_json_has_the_fields_and_a_queued_entry_shows_none(self):
        entry = self.make()
        queue.set_progress(entry["id"], {"step": 2, "steps": 4, "etaS": 5})
        item = self.js("queue", "list")[0]
        self.assertEqual(item["progress"], {"step": 2, "steps": 4, "etaS": 5})
        queue.recover_orphans()
        self.assertNotIn("progress", self.ok("queue", "list"))

    def test_odd_stored_progress_does_not_break_the_list(self):
        entry = self.make()
        for odd in ("x", {"step": "a"}, {"step": 1, "steps": 2, "etaS": "soon"}, None):
            data = json.loads(queue.queue_path().read_text())
            data["entries"][0]["progress"] = odd
            queue.queue_path().write_text(json.dumps(data))
            self.ok("queue", "list")


class WorkerProgressAndMetadataTests(WorkerTests):
    def test_progress_and_preview_are_in_the_entry_while_it_runs_and_gone_after(self):
        seen = {}
        gate = self.tmp / "gate"

        self.push()
        orig = queue.set_progress

        def spy(entry_id, progress):
            result = orig(entry_id, progress)
            if progress["step"] == 3:
                seen["entry"] = queue.get(entry_id)
                gate.write_text("go")
            return result

        with mock.patch.dict(os.environ, {"FAKE_SD_GATE": str(gate), "FAKE_SD_GATE_AFTER": "3"}), \
                mock.patch("gimg.queue.set_progress", side_effect=spy):
            self.assertEqual(worker.run(), 1)
        entry = seen["entry"]
        self.assertEqual(entry["progress"], {"step": 3, "steps": 6, "etaS": 3})
        self.assertEqual(entry["preview"], str(self.attempts_dir() / ".pending-1.preview.png"))
        done = queue.get(1)
        self.assertEqual(done["state"], "done")
        self.assertNotIn("progress", done)
        self.assertNotIn("preview", done)

    def test_png_of_the_attempt_has_the_gimg_chunk(self):
        self.push()
        worker.run()
        text = png.read_text_chunks(self.attempts_dir() / "q1.png")["gimg"]
        meta = json.loads(text)
        self.assertEqual(meta["seed"], queue.get(1)["seed"])
        self.assertEqual((meta["steps"], meta["cfg"], meta["sampler"], meta["prompt"]), (6, 1, "euler", queue.get(1)["prompt"]))
        self.assertEqual(meta["engineVersion"], "master-1000-95ff762")
        self.assertEqual((meta["project"], meta["key"], meta["profile"]), ("proj", "a", "banner"))
        self.assertEqual(meta["references"], [])
        self.assertIn("model", meta)

    def test_attempt_records_command_model_files_and_log(self):
        self.push()
        worker.run()
        attempt = orders.get("proj", "a", "banner")["attempts"][0]
        self.assertEqual(attempt["command"][0], "sd-cli")
        self.assertEqual(sorted(attempt["modelFiles"]), ["diffusion", "text", "vae"])
        self.assertEqual(attempt["log"], "attempts/q1.log")
        self.assertTrue((self.attempts_dir().parent / attempt["log"]).is_file())

    def test_log_line_has_the_new_fields_with_their_types(self):
        self.push()
        worker.run()
        line = json.loads(log.log_path("proj").read_text().splitlines()[-1])
        self.assertEqual(sorted(line["app.image.model_files"]), ["diffusion", "text", "vae"])
        self.assertTrue(all(isinstance(v, str) for v in line["app.image.model_files"].values()))
        self.assertEqual(line["app.image.backend"], "vulkan")
        self.assertIs(line["app.image.draft"], False)
        self.assertNotIn("app.image.compose", line)
        self.assertEqual(line["app.image.command"][0], "sd-cli")
        self.assertTrue(all(isinstance(a, str) for a in line["app.image.command"]))
        self.assertIsInstance(line["app.load_ms"], int)
        self.assertEqual(line["app.image.engine_version"], "master-1000-95ff762")

    def test_a_damaged_png_does_not_fail_the_attempt(self):
        self.push()
        with mock.patch("gimg.worker.png.add_text_chunk", side_effect=GimgError("png.invalid", path="p", reason="bad CRC")):
            self.assertEqual(worker.run(), 1)
        self.assertEqual(queue.get(1)["state"], "done")
        self.assertEqual(png.read_text_chunks(self.attempts_dir() / "q1.png"), {})


class RecordTests(unittest.TestCase):
    def test_fake_engine_record_has_draft_false_and_no_command(self):
        res = engine.EngineResult(duration_ms=1, engine_version="fake-1")
        rec = log.record_for("k", "banner", {"seed": 1, "prompt": "p", "params": {}}, {}, "fake", result=res)
        self.assertIs(rec["app.image.draft"], False)
        for name in ("command", "model_files", "backend", "threads", "compose"):
            self.assertNotIn("app.image." + name, rec)

    def test_error_record_has_none_of_them(self):
        rec = log.record_for("k", "banner", {"seed": 1, "prompt": "p", "params": {}}, {}, "fake", error="x")
        self.assertFalse([k for k in rec if k.split(".")[2:3] in (["draft"], ["command"], ["backend"])])


if __name__ == "__main__":
    unittest.main()
