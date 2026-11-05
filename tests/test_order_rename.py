"""F4e.5: rename an order (`orders.rename`), its API route and `gimg order rename`."""
import contextlib
import io
import json
import unittest
from unittest import mock

from gimg import cli, delivery, fsutil, log, orders, paths, queue
from gimg.errors import GimgError
from tests.test_delivery import DeliveryBase
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase

JSON = {"Content-Type": "application/json"}


class EngineTests(DeliveryBase):
    def setUp(self):
        super().setUp()
        self.ids = self.attempts(count=2)

    def folder(self, key="a", profile="banner"):
        return paths.project_data_dir("proj") / "orders" / key / ("@" + profile)

    def rename(self, new="b", key="a", profile="banner"):
        return orders.rename("proj", key, profile, new)

    def test_renames_folder_and_key(self):
        first = orders.get("proj", "a", "banner")["attempts"][0]
        data = orders.attempt_image("proj", "a", "banner", first).read_bytes()
        got = self.rename("b")
        self.assertEqual(got["key"], "b")
        self.assertEqual(orders.get("proj", "b", "banner")["key"], "b")
        self.assertEqual([a["id"] for a in got["attempts"]], self.ids)
        self.assertEqual(orders.attempt_image("proj", "b", "banner", got["attempts"][0]).read_bytes(), data)
        self.assertEqual(self.code(orders.get, "proj", "a", "banner"), "order.unknown")
        self.assertFalse(self.folder("a").exists())

    def test_nested_keys_clean_empty_parents(self):
        self.attempts(count=1, key="fauna/lobo")
        self.rename("flora/pino", key="fauna/lobo")
        self.assertFalse(self.folder("fauna/lobo").parent.exists())
        self.assertTrue(self.folder("flora/pino").is_dir())

    def test_errors_with_their_codes(self):
        self.assertEqual(self.code(self.rename, "a"), "order.same_key")
        self.assertEqual(self.code(self.rename, "b", "nada"), "order.unknown")
        self.assertEqual(self.code(self.rename, "Mala Clave"), "order.invalid")
        self.assertEqual(self.code(self.rename, "../x"), "order.invalid")
        self.attempts(count=1, key="b")
        self.assertEqual(self.code(self.rename, "b"), "order.exists")
        self.assertEqual(orders.get("proj", "a", "banner")["key"], "a")
        self.assertEqual(len(orders.get("proj", "b", "banner")["attempts"]), 1)

    def test_other_profile_with_the_new_key_does_not_clash(self):
        self.attempts(count=1, key="b", profile="thumbnail")
        self.rename("b")
        self.assertEqual(orders.get("proj", "b", "thumbnail")["profile"], "thumbnail")
        self.assertEqual(orders.get("proj", "b", "banner")["profile"], "banner")

    def test_busy_when_queued_or_running(self):
        self.push(key="a", count=1)  # queued, no worker
        self.assertEqual(self.code(self.rename, "b"), "order.busy")
        self.assertTrue(self.folder("a").is_dir())
        self.assertFalse(self.folder("b").exists())
        self.assertTrue(all(e["key"] == "a" for e in queue.list_entries()))

    def test_busy_when_composing(self):
        lock_path = orders.compose_lock_path("proj", "a", "banner", self.ids[0])
        with fsutil.lock(lock_path):
            self.assertEqual(self.code(self.rename, "b"), "order.busy")
        self.assertTrue(self.folder("a").is_dir())
        self.rename("b")

    def test_terminal_queue_entries_get_the_new_key(self):
        before = queue.list_entries()
        self.assertTrue(before and all(e["state"] == "done" for e in before))
        ids = {e["id"] for e in before}
        self.push(key="z", count=1)
        self.rename("b")
        mine = [e for e in queue.list_entries() if e["id"] in ids]
        self.assertTrue(mine and all(e["key"] == "b" for e in mine))
        self.assertEqual([e["key"] for e in queue.list_entries() if e["id"] not in ids], ["z"])

    def test_delivery_follows_the_order(self):
        delivery.choose("proj", "a", "banner", self.ids[0])
        old, new = self.delivered("uploads/images/a-banner.png"), self.delivered("uploads/images/b-banner.png")
        data = old.read_bytes()
        self.rename("b")
        self.assertFalse(old.exists())
        self.assertEqual(new.read_bytes(), data)
        images = self.manifest()["images"]
        self.assertNotIn("a", images)
        entry = images["b"]["banner"]
        self.assertEqual((entry["file"], entry["attemptId"]), ("uploads/images/b-banner.png", self.ids[0]))
        self.assertEqual(self.state("b")[0], self.ids[0])

    def test_taken_target_is_rejected_before_moving_anything(self):
        delivery.choose("proj", "a", "banner", self.ids[0])
        manifest = self.manifest()
        # another entry (some other key) already owns the file `c` would be delivered at
        manifest["images"]["zz"] = {"banner": dict(manifest["images"]["a"]["banner"],
                                                   file="uploads/images/c-banner.png")}
        (self.projects["proj"] / "galivelop-images.manifest.json").write_text(json.dumps(manifest))
        before = (self.manifest(), self.delivered().read_bytes())
        self.assertEqual(self.code(self.rename, "c"), "delivery.target_taken")
        self.assertTrue(self.folder("a").is_dir())
        self.assertFalse(self.folder("c").exists())
        self.assertEqual((self.manifest(), self.delivered().read_bytes()), before)
        self.assertFalse(self.delivered("uploads/images/c-banner.png").exists())
        self.assertEqual(orders.get("proj", "a", "banner")["key"], "a")

    def test_failed_delivery_puts_everything_back(self):
        delivery.choose("proj", "a", "banner", self.ids[0])
        before = (self.manifest(), self.delivered().read_bytes())
        keys = [e["key"] for e in queue.list_entries()]
        with mock.patch.object(delivery, "_copy", side_effect=OSError("disk")):
            with self.assertRaises(GimgError) as cm:
                self.rename("b")
        self.assertEqual(cm.exception.code, "delivery.write_failed")
        self.assertTrue(self.folder("a").is_dir())
        self.assertFalse(self.folder("b").exists())
        self.assertEqual(orders.get("proj", "a", "banner")["key"], "a")
        self.assertEqual([e["key"] for e in queue.list_entries()], keys)
        self.assertEqual((self.manifest(), self.delivered().read_bytes()), before)
        self.assertFalse(self.delivered("uploads/images/b-banner.png").exists())

    def test_log_keeps_old_lines_and_gets_a_rename_line(self):
        before = log.log_path("proj").read_text().splitlines()
        self.rename("b")
        lines = log.log_path("proj").read_text().splitlines()
        self.assertEqual(lines[:len(before)], before)
        last = json.loads(lines[-1])
        self.assertEqual((last["gen_ai.operation.name"], last["app.image.key"], last["app.image.oldKey"],
                          last["app.task"]), ("order.rename", "b", "a", "banner"))
        self.assertNotIn("gen_ai.provider.name", last)


class SurfaceTests(WriteBase):
    """CLI = API: same results, same codes and statuses."""

    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()

    def rename(self, new, key=None, profile=None, body=None):
        return self.call("POST", self.order_url(key or self.key, profile or self.profile, "/rename"),
                         headers=JSON, body={"key": new} if body is None else body)

    def code(self, fn, *args):
        with self.assertRaises(GimgError) as cm:
            fn(*args)
        return cm.exception.code

    def test_api_equals_cli(self):
        resp, payload = self.rename("fauna/gris")
        self.assertEqual(resp.status, 200, payload)
        got = json.loads(payload)
        other, _ = self.make_order(key="fauna/otro")
        out = self.cli_json("order", "rename", NAME, other, self.profile, "fauna/blanco")
        self.assertEqual((got["key"], out["key"]), ("fauna/gris", "fauna/blanco"))
        self.assertEqual(sorted(got), sorted(out))
        self.assertEqual([a["id"] for a in got["attempts"]], [a["id"] for a in out["attempts"]])
        self.assertEqual(orders.get(NAME, "fauna/gris", self.profile)["key"], "fauna/gris")
        self.assertEqual(self.code(orders.get, NAME, self.key, self.profile), "order.unknown")

    def test_errors_and_statuses(self):
        resp, payload = self.rename(self.key)
        self.err(resp, payload, 400, "order.same_key")
        resp, payload = self.rename("fauna/x", key="fauna/nada")
        self.err(resp, payload, 404, "order.unknown")
        resp, payload = self.rename("Mala Clave")
        self.err(resp, payload, 400, "order.invalid")
        other, _ = self.make_order(key="fauna/otro")
        resp, payload = self.rename(other)
        self.err(resp, payload, 409, "order.exists")
        resp, payload = self.rename(None, body={})
        self.err(resp, payload, 400, "api.bad_param")
        resp, payload = self.rename(None, body={"key": 3})
        self.err(resp, payload, 400, "api.bad_param")
        self.assertEqual(orders.get(NAME, self.key, self.profile)["key"], self.key)

    def test_busy_is_409_and_the_cli_fails_with_its_reason(self):
        self.ok("POST", self.order_url(self.key, self.profile, "/attempts"), {"count": 1}, 202)
        resp, payload = self.rename("fauna/gris")
        self.err(resp, payload, 409, "order.busy")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["--lang", "en", "order", "rename", NAME, self.key, self.profile, "fauna/gris"])
        self.assertEqual((code, out.getvalue()), (1, ""))
        self.assertIn("queued, being generated or being composed", err.getvalue())

    def test_needs_a_good_origin(self):
        resp, payload = self.call("POST", self.order_url(self.key, self.profile, "/rename"),
                                  headers=dict(JSON, Origin="http://evil.test"), body={"key": "fauna/gris"})
        self.err(resp, payload, 403, "api.bad_origin")
        self.assertEqual(orders.get(NAME, self.key, self.profile)["key"], self.key)


if __name__ == "__main__":
    unittest.main()
