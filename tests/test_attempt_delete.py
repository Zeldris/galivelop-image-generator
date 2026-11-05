"""F4e.1a: delete an attempt (D41): engine (`orders.delete_attempt`), API (DELETE) and CLI (`attempt rm`)."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import fsutil, log, orders, paths, projects, queue
from gimg.errors import GimgError
from tests.test_orders import EXAMPLE
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase


class EngineTests(unittest.TestCase):
    """The storage rules, without the queue or the server."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data")})
        env.start()
        self.addCleanup(env.stop)
        (self.tmp / "proj").mkdir()
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        cfg["name"] = "proj"
        (self.tmp / "proj" / "galivelop-images.json").write_text(json.dumps(cfg))
        projects.add(self.tmp / "proj")
        orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "a cat"})
        self.folder = paths.project_data_dir("proj") / "orders" / "a" / "@banner"

    def add(self, n=1, **extra):
        spec = {"seed": n, "prompt": "p", "params": {"steps": 6}, **extra}
        return orders.add_attempt("proj", "a", "banner", spec)

    def put(self, rel, data=b"x"):
        path = self.folder / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def code(self, fn, *args):
        with self.assertRaises(GimgError) as cm:
            fn(*args)
        return cm.exception.code

    def delete(self, n):
        return orders.delete_attempt("proj", "a", "banner", n)

    def stored(self):
        return fsutil.read_json(self.folder / "order.json")

    def test_number_is_not_reused_after_deleting_the_last(self):
        self.add(), self.add()
        self.delete(2)
        self.assertEqual(self.stored()["nextId"], 3)
        self.assertEqual(self.add(), 3)
        self.assertEqual([a["id"] for a in self.stored()["attempts"]], [1, 3])

    def test_old_order_without_next_id_takes_max_plus_one(self):
        self.add(), self.add(), self.add()
        data = self.stored()
        data.pop("nextId")
        fsutil.write_json(self.folder / "order.json", data)
        self.delete(3)  # the old order has no memory of 3, so its number comes from the ids left...
        self.assertEqual(self.stored()["nextId"], 4)  # ...but the delete itself stores it first: 3 stays burned
        data = self.stored()
        data.pop("nextId")
        fsutil.write_json(self.folder / "order.json", data)
        self.assertEqual(self.add(), 3)  # no memory at all: max(ids)+1, as before F4e.1
        self.assertEqual(self.stored()["nextId"], 4)

    def test_new_orders_start_at_one(self):
        self.assertEqual(self.stored()["nextId"], 1)
        self.assertEqual(self.add(), 1)
        self.assertEqual(self.stored()["nextId"], 2)

    def test_chosen_history_is_cleaned(self):
        for n in (1, 2, 3):
            self.add(n)
        orders.choose("proj", "a", "banner", 1)
        orders.choose("proj", "a", "banner", 2)
        orders.choose("proj", "a", "banner", 3)
        self.assertEqual(self.stored()["chosenHistory"], [None, 1, 2])
        self.delete(1)
        self.assertEqual(self.stored()["chosenHistory"], [None, 2])
        self.assertEqual(self.stored()["chosen"], 3)

    def test_chosen_is_protected_and_nothing_changes(self):
        self.add()
        orders.choose("proj", "a", "banner", 1)
        image = self.put("attempts/1.png")
        before = self.stored()
        self.assertEqual(self.code(self.delete, 1), "order.delete_chosen")
        self.assertEqual(self.stored(), before)
        self.assertTrue(image.exists())

    def test_busy_attempt_is_protected(self):
        entry = queue.enqueue("proj", "a", "banner", orders.attempt_specs("proj", "a", "banner", 1))[0]
        orders.add_attempt("proj", "a", "banner", {"seed": 1, "prompt": "p", "params": {}}, entry_id=entry["id"])
        image = self.put("attempts/q%d.png" % entry["id"])
        self.assertEqual(self.code(self.delete, 1), "order.delete_busy")  # queued
        self.assertTrue(image.exists())
        self.assertEqual(queue.claim()["id"], entry["id"])
        self.assertEqual(self.code(self.delete, 1), "order.delete_busy")  # running
        self.assertTrue(image.exists())
        queue.cancel(entry["id"])  # a cancelled entry is not busy
        self.assertEqual(self.delete(1)["deleted"], 1)
        self.assertFalse(image.exists())

    def test_being_composed_is_busy(self):
        self.add()
        with fsutil.try_lock(orders.compose_lock_path("proj", "a", "banner", 1)) as taken:
            self.assertTrue(taken)
            # flock locks belong to the open file description: a second open in this process conflicts too
            self.assertEqual(self.code(self.delete, 1), "order.delete_busy")
        self.assertEqual(self.delete(1)["deleted"], 1)

    def test_files_are_deleted_and_the_rest_stay(self):
        entry = 7
        self.add()
        orders.add_attempt("proj", "a", "banner", {
            "seed": 2, "prompt": "p", "params": {}, "log": "attempts/q7.log", "raw": "attempts/q7.raw.png",
            "compose": {"template": "t"}}, entry_id=entry)
        mine = [self.put(p) for p in ("attempts/q7.png", "attempts/q7.raw.png", "attempts/q7.log",
                                      "attempts/q7.preview.png", "attempts/.pending-7.preview.png")]
        other = [self.put("attempts/1.png"), self.put("attempts/q8.png"), self.put("attempts/q8.log")]
        delivered = self.tmp / "proj" / "public" / "a.png"
        delivered.parent.mkdir()
        delivered.write_bytes(b"d")
        got = self.delete(2)
        self.assertEqual(got, {"deleted": 2, "files": 5})
        self.assertEqual([p.exists() for p in mine], [False] * 5)
        self.assertEqual([p.exists() for p in other], [True] * 3)
        self.assertTrue(delivered.exists())  # what was delivered is not touched
        self.assertEqual([a["id"] for a in self.stored()["attempts"]], [1])

    def test_files_already_gone_are_not_an_error(self):
        self.add()
        self.assertEqual(self.delete(1), {"deleted": 1, "files": 0})
        self.assertEqual(self.stored()["attempts"], [])

    def test_order_without_attempts_and_unknown_ids(self):
        self.assertEqual(self.code(self.delete, 1), "order.attempt_unknown")
        self.add()
        for bad in (99, 0, "1", None, True, 1.0):
            with self.subTest(bad=bad):
                self.assertEqual(self.code(self.delete, bad), "order.attempt_unknown")
        self.assertEqual(self.code(orders.delete_attempt, "proj", "zzz", "banner", 1), "order.unknown")
        self.assertEqual(len(self.stored()["attempts"]), 1)

    def test_nothing_outside_the_order_folder(self):
        self.add()
        outside = self.tmp / "outside.png"
        outside.write_bytes(b"keep")
        data = self.stored()
        data["attempts"][0]["image"] = "../../../../../outside.png"
        fsutil.write_json(self.folder / "order.json", data)
        self.assertEqual(self.code(self.delete, 1), "path.dotdot")
        data["attempts"][0]["image"] = "attempts/link.png"  # a link that leads out of the folder
        (self.folder / "attempts").mkdir(exist_ok=True)
        (self.folder / "attempts" / "link.png").symlink_to(outside)
        fsutil.write_json(self.folder / "order.json", data)
        self.assertEqual(self.code(self.delete, 1), "path.outside")
        self.assertTrue(outside.exists())
        self.assertEqual(len(self.stored()["attempts"]), 1)  # refused before anything was touched

    def test_history_has_no_adjacent_duplicates_after_deleting(self):
        for n in (1, 2, 3):
            self.add(n)
        data = self.stored()
        data["chosenHistory"] = [None, 1, 3, 1]
        data["chosen"] = 2
        fsutil.write_json(self.folder / "order.json", data)
        self.delete(3)
        self.assertEqual(self.stored()["chosenHistory"], [None, 1])

    def test_a_delete_waits_for_the_delivery_lock(self):
        """`delivery.undo` plans and applies under this lock: a delete that could slip in between would edit the
        history it planned on. Held by someone else, the delete does not go through."""
        import threading
        from gimg import delivery
        self.add(), self.add()
        done = threading.Event()
        with delivery._lock("proj"):
            thread = threading.Thread(target=lambda: (self.delete(2), done.set()))
            thread.start()
            self.assertFalse(done.wait(0.5))
            self.assertEqual(len(self.stored()["attempts"]), 2)
        thread.join(5)
        self.assertTrue(done.is_set())
        self.assertEqual([a["id"] for a in self.stored()["attempts"]], [1])

    def test_the_log_gets_an_attempt_delete_line(self):
        self.add(5)
        self.delete(1)
        lines = [json.loads(line) for line in log.log_path("proj").read_text().splitlines()]
        self.assertEqual(len(lines), 1)
        self.assertEqual((lines[0]["gen_ai.operation.name"], lines[0]["app.attempt.id"], lines[0]["app.image.key"],
                          lines[0]["app.task"], lines[0]["app.image.seed"]),
                         ("attempt.delete", 1, "a", "banner", 5))
        self.assertNotIn("gen_ai.provider.name", lines[0])  # not a generation: the estimate never reads it


class SurfaceTests(WriteBase):
    """CLI = API: same results, same codes and states."""

    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()

    def delete(self, id, key=None, profile=None):
        return self.call("DELETE", self.att(key or self.key, profile or self.profile, id))

    def stored(self, key=None):
        return orders.get(NAME, key or self.key, self.profile)

    def test_api_equals_cli(self):
        resp, payload = self.delete(2)
        self.assertEqual(resp.status, 200, payload)
        got = json.loads(payload)
        other, _ = self.make_order(key="fauna/otro")
        cli = self.cli_json("attempt", "rm", NAME, other, self.profile, "2", "--yes")
        self.assertEqual(got, cli)
        self.assertEqual(got["deleted"], 2)
        self.assertGreaterEqual(got["files"], 1)
        for key in (self.key, other):
            self.assertEqual([a["id"] for a in self.stored(key)["attempts"]], [1])
            self.assertEqual(self.stored(key)["nextId"], 3)

    def test_api_files_and_nextid(self):
        attempt = self.stored()["attempts"][1]
        image = orders.attempt_image(NAME, self.key, self.profile, attempt)
        self.assertTrue(image.exists())
        self.assertEqual(self.delete(2)[0].status, 200)
        self.assertFalse(image.exists())
        self.assertTrue(orders.attempt_image(NAME, self.key, self.profile, self.stored()["attempts"][0]).exists())
        self.ok("POST", self.order_url(self.key, self.profile, "/attempts"), {"count": 1}, 202)
        self.cli("work")
        self.assertEqual([a["id"] for a in self.stored()["attempts"]], [1, 3])

    def test_errors_and_statuses(self):
        resp, payload = self.delete(99)
        self.err(resp, payload, 404, "order.attempt_unknown")
        resp, payload = self.delete(1, key="fauna/nada")
        self.err(resp, payload, 404, "order.unknown")
        resp, payload = self.call("DELETE", self.att(self.key, self.profile, 1).replace("/1", "/x"))
        self.err(resp, payload, 400, "api.bad_param")
        self.ok("POST", self.order_url(self.key, self.profile, "/choose"), {"attempt": 1})
        resp, payload = self.delete(1)
        self.err(resp, payload, 409, "order.delete_chosen")
        self.assertEqual(len(self.stored()["attempts"]), 2)

    def test_busy_is_409_in_the_api_and_fails_in_the_cli(self):
        self.ok("POST", self.order_url(self.key, self.profile, "/attempts"), {"count": 1}, 202)  # queued, no worker
        entry = queue.list_entries(["queued"])[0]
        orders.add_attempt(NAME, self.key, self.profile, {"seed": 1, "prompt": "p", "params": {}},
                           entry_id=entry["id"])
        resp, payload = self.delete(3)
        self.err(resp, payload, 409, "order.delete_busy")
        self.assertIn("queued, being generated or being composed",
                      self.cli_fails("--lang", "en", "attempt", "rm", NAME, self.key, self.profile, "3", "--yes"))

    def test_only_delete_with_a_good_origin(self):
        resp, payload = self.call("DELETE", self.att(self.key, self.profile, 1), host="evil.test")
        self.err(resp, payload, 403, "api.bad_host")
        resp, payload = self.call("DELETE", self.att(self.key, self.profile, 1),
                                  headers={"Origin": "http://evil.test"})
        self.err(resp, payload, 403, "api.bad_origin")
        resp, payload = self.call("DELETE", self.att(self.key, self.profile, 1),
                                  headers={"Sec-Fetch-Site": "cross-site"})
        self.err(resp, payload, 403, "api.bad_origin")
        self.assertEqual(len(self.stored()["attempts"]), 2)  # none of them deleted anything
        resp, payload = self.call("DELETE", "/api/projects/%s" % NAME)  # other routes still do not accept it
        self.err(resp, payload, 405, "api.method_not_allowed")

    # --- CLI ---
    def cli_fails(self, *argv, stdin=None):
        import contextlib
        import io
        from gimg import cli
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if stdin is None:
                code = cli.main(list(argv))
            else:
                with mock.patch.object(sys, "stdin", stdin):
                    code = cli.main(list(argv))
        self.assertEqual((code, out.getvalue()), (1, ""), argv)
        return err.getvalue()

    def test_cli_without_yes_and_without_a_terminal_fails_with_its_reason(self):
        import io
        err = self.cli_fails("--lang", "en", "attempt", "rm", NAME, self.key, self.profile, "1", stdin=io.StringIO("y\n"))
        self.assertIn("no terminal to ask", err)
        self.assertEqual(len(self.stored()["attempts"]), 2)

    def test_cli_asks_on_a_terminal(self):
        import io

        class Tty(io.StringIO):
            def isatty(self):
                return True

        err = self.cli_fails("--lang", "en", "attempt", "rm", NAME, self.key, self.profile, "1", stdin=Tty("n\n"))
        self.assertIn("nothing was deleted", err)
        self.assertEqual(len(self.stored()["attempts"]), 2)
        with mock.patch.object(sys, "stdin", Tty("y\n")):
            out = self.cli("--lang", "en", "attempt", "rm", NAME, self.key, self.profile, "1")
        self.assertIn("Attempt 1 deleted", out)
        self.assertEqual([a["id"] for a in self.stored()["attempts"]], [2])

    def test_cli_errors(self):
        self.assertIn("has no attempt 99", self.cli_fails("--lang", "en", "attempt", "rm", NAME, self.key,
                                                         self.profile, "99", "--yes"))
        self.ok("POST", self.order_url(self.key, self.profile, "/choose"), {"attempt": 1})
        self.assertIn("is the chosen one and cannot be deleted",
                      self.cli_fails("--lang", "en", "attempt", "rm", NAME, self.key, self.profile, "1", "--yes"))
        self.assertIn("es el elegido y no se puede borrar",
                      self.cli_fails("--lang", "es", "attempt", "rm", NAME, self.key, self.profile, "1", "--yes"))


if __name__ == "__main__":
    unittest.main()
