"""F4e.1: delete a failed or cancelled queue entry (D41): engine (`queue.remove`), API (DELETE) and CLI (`queue rm`)."""
import contextlib
import io
import sys
import unittest
from unittest import mock

from gimg import cli, orders, queue
from tests.test_queue import QueueBase
from tests.test_server_write import WriteBase


class EngineTests(QueueBase):
    def test_cancelled_and_failed_go_and_the_rest_stay(self):
        self.push(count=3)
        queue.cancel(1)
        queue.claim()  # takes 2 (1 is cancelled)
        queue.finish(2, "failed", error="boom")
        self.assertEqual(queue.remove(1)["id"], 1)
        self.assertEqual(queue.remove(2)["state"], "failed")
        self.assertEqual([e["id"] for e in queue.list_entries()], [3])
        self.assertEqual(self.code(queue.remove, 1), "queue.unknown")

    def test_queued_running_and_done_are_not_removable(self):
        self.hold_worker_lock()  # a live worker: the running entry is not recovered back to queued
        self.push(count=3)
        queue.claim()
        queue.finish(1, "done", attempt_id=1)
        queue.claim()
        self.assertEqual(self.code(queue.remove, 1), "queue.not_removable")  # done: it is its attempt
        self.assertEqual(self.code(queue.remove, 2), "queue.not_removable")  # running
        self.assertEqual(self.code(queue.remove, 3), "queue.not_removable")  # queued
        self.assertEqual([e["id"] for e in queue.list_entries()], [1, 2, 3])

    def test_its_pending_files_go_and_others_stay(self):
        self.push(count=2)
        queue.cancel(1)
        folder = orders.pending_image_path("proj", "a", "banner", 1).parent
        folder.mkdir(parents=True, exist_ok=True)
        mine = [folder / ".pending-1.png", folder / ".pending-1.log", folder / ".pending-1.preview.png"]
        other = folder / ".pending-2.png"
        for path in mine + [other]:
            path.write_bytes(b"x")
        queue.remove(1)
        self.assertEqual([p for p in mine if p.exists()], [])
        self.assertTrue(other.exists())

    def test_the_number_is_not_reused(self):
        self.push()
        queue.cancel(1)
        queue.remove(1)
        self.assertEqual(self.push()[0]["id"], 2)


class SurfaceTests(WriteBase):
    def setUp(self):
        super().setUp()
        self.make_order(work=False)  # entries 1 and 2, queued
        queue.cancel(1)
        queue.cancel(2)

    def cli_fails(self, *argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                mock.patch.object(sys, "stdin", stdin or io.StringIO()):
            code = cli.main(list(argv))
        self.assertEqual((code, out.getvalue()), (1, ""), argv)
        return err.getvalue()

    def test_api_equals_cli(self):
        resp, payload = self.call("DELETE", "/api/queue/1")
        self.assertEqual(resp.status, 200, payload)
        import json
        got = json.loads(payload)
        cli_got = self.cli_json("queue", "rm", "2", "--yes")
        self.assertEqual((got["id"], got["state"]), (1, "cancelled"))
        self.assertEqual((cli_got["id"], cli_got["state"]), (2, "cancelled"))
        self.assertEqual(set(got), set(cli_got))
        self.assertEqual(queue.list_entries(), [])

    def test_errors_and_statuses(self):
        resp, payload = self.call("DELETE", "/api/queue/99")
        self.err(resp, payload, 404, "queue.unknown")
        resp, payload = self.call("DELETE", "/api/queue/x")
        self.err(resp, payload, 400, "api.bad_param")
        self.ok("POST", self.order_url("fauna/lobo", "banner", "/attempts"), {"count": 1}, 202)  # entry 3, queued
        resp, payload = self.call("DELETE", "/api/queue/3")
        self.err(resp, payload, 409, "queue.not_removable")
        self.assertIn("only a failed or cancelled one", self.cli_fails("--lang", "en", "queue", "rm", "3", "--yes"))
        resp, payload = self.call("DELETE", "/api/queue/1", headers={"Origin": "http://evil.test"})
        self.err(resp, payload, 403, "api.bad_origin")
        self.assertEqual([e["id"] for e in queue.list_entries()], [1, 2, 3])

    def test_cli_asks_and_without_a_terminal_fails(self):
        self.assertIn("no terminal to ask", self.cli_fails("--lang", "en", "queue", "rm", "1"))

        class Tty(io.StringIO):
            def isatty(self):
                return True

        self.assertIn("nothing was deleted", self.cli_fails("--lang", "en", "queue", "rm", "1", stdin=Tty("n\n")))
        self.assertEqual(len(queue.list_entries()), 2)
        with mock.patch.object(sys, "stdin", Tty("y\n")):
            self.assertIn("Entry 1 removed", self.cli("--lang", "en", "queue", "rm", "1"))
        self.assertEqual([e["id"] for e in queue.list_entries()], [2])


if __name__ == "__main__":
    unittest.main()
