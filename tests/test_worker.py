import fcntl
import json
import os
import struct
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from gimg import engine, log, orders, queue, worker
from gimg.errors import GimgError
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
        png = orders.attempt_image_path("proj", "a", "banner", 1).read_bytes()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", png[16:24]), (1280, 512))
        names = {p.name for p in orders.attempt_image_path("proj", "a", "banner", 1).parent.iterdir()}
        self.assertEqual(names, {"1.png", "2.png"})  # no temp left
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
        self.assertEqual((entry["state"], entry["error"]), ("failed", "out of vram"))

    def test_engine_failure(self):
        self.push()
        worker.run(engine=engine.FakeEngine(fail_with="boom"))
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"], entry["attemptId"]), ("failed", "boom", None))
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"], [])
        self.assertEqual(self.lines()[0]["app.error"], "boom")
        self.assertNotIn("app.duration_ms", self.lines()[0])
        self.assertEqual(self.leftovers(), [])

    def test_timeout(self):
        self.push()
        worker.run(engine=StubEngine(engine.EngineTimeout()))
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]), ("failed", engine.TIMEOUT_MESSAGE))
        self.assertEqual(self.lines()[0]["app.error"], "timeout")

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
                         [("failed", "ValueError: bug")] * 2)

    def test_limits_rechecked_at_run(self):
        self.push()
        profile = self.tmp / "tight.json"
        profile.write_text(json.dumps({"name": "tight", "minFreeMemoryMb": 1, "watchMemoryMb": 1,
                                       "maxReferences": 1, "timeoutS": 5, "maxSteps": 2,
                                       "maxPixels": 1048576}))
        with mock.patch.dict(os.environ, {"GIMG_MACHINE_PROFILE": str(profile)}):
            worker.run()
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]), ("failed", "limit.steps"))
        self.assertEqual(self.lines()[0]["app.error"], "limit.steps")
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
            self.assertEqual((done["state"], done["error"]), ("failed", "worker.reference_missing"), ref)
        self.assertEqual(self.lines()[0]["app.error"], "worker.reference_missing")

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
            self.assertEqual((done["state"], done["error"]), ("failed", code), ref)

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
        queue.claim()
        data = json.loads((self.tmp / "data" / "queue.json").read_text())
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        data["entries"][0]["pid"] = proc.pid
        (self.tmp / "data" / "queue.json").write_text(json.dumps(data))
        self.assertEqual(worker.run(), 1)
        self.assertEqual(queue.get(1)["state"], "done")

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
