"""`gimg queue pause` / `resume` (R1): the mark, the worker that stops taking entries, the service that launches none."""
import contextlib
import io
import json
import unittest
from unittest import mock

from gimg import cli, engine, queue, service, worker
from tests.test_queue import QueueBase


class PausingEngine(engine.Engine):
    """The fake engine, but the queue is paused while the first image is being generated."""
    provider = "fake"

    def __init__(self):
        self.inner = engine.get_engine()
        self.calls = 0

    def generate(self, job, should_cancel):
        self.calls += 1
        if self.calls == 1:
            queue.pause()
        return self.inner.generate(job, should_cancel)


class PauseTests(QueueBase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["--lang", "en", *argv])
        return code, out.getvalue()

    def test_pause_with_nothing_running_marks_and_worker_does_nothing(self):
        self.assertTrue(queue.pause())
        self.assertTrue(queue.is_paused())
        self.assertEqual(worker.run(), 0)
        self.push()
        self.assertEqual(worker.run(), 0)
        self.assertEqual([e["state"] for e in queue.list_entries()], ["queued"])  # nothing claimed

    def test_pause_during_an_image_finishes_it_and_does_not_take_the_next(self):
        self.push(count=3)
        self.assertEqual(worker.run(engine=PausingEngine()), 1)
        self.assertEqual([e["state"] for e in queue.list_entries()], ["done", "queued", "queued"])
        self.assertEqual(worker.run(), 0)  # still paused
        self.assertTrue(queue.resume())
        self.assertEqual(worker.run(), 2)  # the rest goes on after resume

    def test_resume_without_pause_is_a_harmless_no(self):
        self.assertFalse(queue.resume())
        self.assertFalse(queue.is_paused())
        self.push()
        self.assertEqual(worker.run(), 1)

    def test_pause_twice_reports_no_change_and_one_resume_clears_it(self):
        self.assertTrue(queue.pause())
        self.assertFalse(queue.pause())
        self.assertTrue(queue.resume())
        self.assertFalse(queue.is_paused())

    def test_service_down_a_hand_launched_worker_honours_the_mark(self):
        self.push()
        queue.pause()
        self.assertEqual(worker.run(), 0)
        queue.resume()
        self.assertEqual(worker.run(), 1)

    def test_service_launches_no_worker_while_paused_and_launches_after_resume(self):
        self.push()
        queue.pause()
        launcher = service._Launcher("en")
        with mock.patch.object(service.subprocess, "Popen") as popen:
            self.assertFalse(service.maybe_launch_worker(launcher))
            popen.assert_not_called()
            queue.resume()
            self.assertTrue(service.maybe_launch_worker(launcher))
            popen.assert_called_once()

    def test_cli_pause_resume_and_list_say_so(self):
        self.push()
        code, out = self.run_cli("queue", "pause")
        self.assertEqual(code, 0)
        self.assertIn("Queue paused", out)
        self.assertIn("already paused", self.run_cli("queue", "pause")[1])
        listed = self.run_cli("queue", "list")[1]
        self.assertIn("The queue is paused", listed)
        self.assertIn("#1 queued", listed)
        self.assertEqual(json.loads(self.run_cli("--json", "queue", "pause")[1]), {"paused": True, "changed": False})
        self.assertIn("Queue resumed", self.run_cli("queue", "resume")[1])
        self.assertNotIn("paused", self.run_cli("queue", "list")[1])
        self.assertIn("was not paused", self.run_cli("queue", "resume")[1])


if __name__ == "__main__":
    unittest.main()
