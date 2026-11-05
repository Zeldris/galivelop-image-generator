"""F4d.1: model and template in the new order / attempts, GET /api/models, GET …/check, move and clear the queue.
CLI and API give the same; every error has its code and status."""
import fcntl
import json
import os
import unittest
from unittest import mock

from gimg import models, queue
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase


class F4dBase(WriteBase):
    def setUp(self):
        super().setUp()
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        cfg["profiles"]["og"]["compose"]["templates"] = {"alt": {"template": "t.svg"}}
        cfg["profiles"]["og"]["compose"]["fonts"] = ["Zzz Not Installed Font"]
        cfg["brand"] = {"palette": ["#112233"], "textColor": "#FFFFFF", "paletteMin": 60, "bannedWords": ["x", "y"]}
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))

    def machine(self, **limits):
        profile = self.tmp / "m.json"
        profile.write_text(json.dumps(dict({"name": "m", "minFreeMemoryMb": 1, "watchMemoryMb": 1, "maxReferences": 1,
                                            "timeoutS": 5, "maxSteps": 50, "maxPixels": 1048576}, **limits)))
        env = mock.patch.dict(os.environ, {"GIMG_MACHINE_PROFILE": str(profile)})
        env.start()
        self.addCleanup(env.stop)

    def hold_worker_lock(self):
        """Pretend a worker is alive, so a ``running`` entry is not recovered by the next read."""
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, fd)

    def queued_ids(self):
        return [e["id"] for e in sorted(queue.list_entries(["queued"]), key=queue._pos)]


class BrandSchemaTests(F4dBase):
    def test_brand_fields_validate(self):
        got = self.ok("GET", "/api/projects/%s" % NAME)
        self.assertEqual(got["config"]["brand"]["paletteMin"], 60)
        for bad in ({"textColor": "white"}, {"paletteMin": 101}, {"bannedWords": ["a"] * 101}, {"bannedWords": [3]}):
            cfg = json.loads((self.root / "galivelop-images.json").read_text())
            cfg["brand"] = bad
            (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
            self.bad("GET", "/api/projects/%s" % NAME, None, 500, "project.config_invalid")


class OrderTemplateTests(F4dBase):
    def test_template_goes_to_the_entries_like_the_cli(self):
        got = self.ok("POST", self.orders_url(), self.order(profile="og", template="alt", count=1), 201)
        self.assertEqual(got["entries"][0]["template"], "alt")
        self.assertNotIn("template", got["order"])  # not part of the stored order
        f = self.tmp / "o.json"
        f.write_text(json.dumps(self.order(key="fauna/otro", profile="og", count=1)))
        cli = self.cli_json("order", "submit", NAME, str(f), "--template", "alt")
        self.assertEqual(cli["entries"][0]["template"], "alt")

    def test_unknown_template_queues_and_stores_nothing(self):
        self.bad("POST", self.orders_url(), self.order(profile="og", template="nope"), 400, "compose.template_unknown")
        self.assertEqual(queue.list_entries(), [])
        self.bad("GET", self.order_url("fauna/lobo", "og"), None, 404, "order.unknown")
        self.bad("POST", self.orders_url(), self.order(profile="og", template=3), 400, "api.bad_param")


class OrderModelTests(F4dBase):
    def test_model_goes_to_the_entries_like_the_cli(self):
        got = self.ok("POST", self.orders_url(), self.order(profile="og", model="flux3-klein-q8", count=1), 201)
        self.assertEqual(got["entries"][0]["params"]["model"], "flux3-klein-q8")
        self.assertNotIn("model", got["order"])  # not part of the stored order
        f = self.tmp / "o.json"
        f.write_text(json.dumps(self.order(key="fauna/otro", profile="og", count=1)))
        cli = self.cli_json("order", "submit", NAME, str(f), "--model", "flux3-klein-q8")
        self.assertEqual(cli["entries"][0]["params"]["model"], "flux3-klein-q8")

    def test_unknown_model_queues_and_stores_nothing(self):
        self.bad("POST", self.orders_url(), self.order(profile="og", model="nope"), 400, "model.unknown")
        self.assertEqual(queue.list_entries(), [])
        self.bad("GET", self.order_url("fauna/lobo", "og"), None, 404, "order.unknown")
        self.bad("POST", self.orders_url(), self.order(profile="og", model=3), 400, "api.bad_param")


    def test_a_model_over_max_steps_stores_and_queues_nothing(self):
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        del cfg["profiles"]["banner"]["steps"]  # then the steps are the model's (16), which the machine refuses
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        self.machine(maxSteps=10)
        err = self.bad("POST", self.orders_url(), self.order(model="flux3-klein-q8"), 400, "limit.steps")
        self.assertEqual((err["params"]["steps"], err["params"]["max"]), (16, 10))
        self.assertEqual(queue.list_entries(), [])
        self.bad("GET", self.order_url("fauna/lobo", "banner"), None, 404, "order.unknown")


class AttemptModelTests(F4dBase):
    def setUp(self):
        super().setUp()
        self.ok("POST", self.orders_url(), self.order(count=1), 201)
        self.url = self.order_url("fauna/lobo", "banner", "/attempts")

    def test_model_matches_the_cli(self):
        got = self.ok("POST", self.url, {"model": "flux3-klein-q8"}, 202)
        self.assertEqual(got["entries"][0]["params"]["model"], "flux3-klein-q8")
        cli = self.cli_json("attempt", "new", NAME, "fauna/lobo", "banner", "--model", "flux3-klein-q8")
        self.assertEqual(cli["entries"][0]["params"]["model"], "flux3-klein-q8")

    def test_errors(self):
        self.bad("POST", self.url, {"model": "nope"}, 400, "model.unknown")
        self.bad("POST", self.url, {"model": 3}, 400, "api.bad_param")
        self.machine(maxSteps=4)
        self.bad("POST", self.url, {"model": "flux3-klein-q8"}, 400, "limit.steps")
        self.assertEqual(len(queue.list_entries()), 1)  # only the order's own attempt


class ModelsRouteTests(F4dBase):
    def test_allowed_for_the_machine(self):
        got = self.ok("GET", "/api/models")
        self.assertEqual([m["id"] for m in got], models.ids())
        self.assertTrue(all(m["allowed"] and "reason" not in m for m in got))
        self.machine(maxSteps=10)
        got = {m["id"]: m for m in self.ok("GET", "/api/models")}
        self.assertTrue(got["flux2-klein-4b-q8"]["allowed"])
        self.assertFalse(got["flux3-klein-q8"]["allowed"])
        self.assertEqual(got["flux3-klein-q8"]["reason"]["code"], "limit.steps")
        self.assertIn("16", got["flux3-klein-q8"]["reason"]["message"])


class CheckRouteTests(F4dBase):
    def test_project_checks(self):
        got = self.ok("GET", "/api/projects/%s/check" % NAME)
        self.assertTrue(got)
        for item in got:
            self.assertIn(item["status"], ("ok", "warn", "fail"))
            self.assertTrue(item["message"])
            self.assertIn(item["id"].split(":")[0], ("font", "fonts", "template", "templates"))
        self.bad("GET", "/api/projects/nope/check", None, 404, "project.unknown")


class QueueMoveClearTests(F4dBase):
    def setUp(self):
        super().setUp()
        self.ids = [e["id"] for e in self.ok("POST", self.orders_url(), self.order(count=4), 201)["entries"]]

    def move(self, id, to, status=200):
        return self.ok("POST", "/api/queue/%d/move" % id, {"to": to}, status)

    def test_move_matches_the_cli_and_changes_the_order(self):
        a, b, c, d = self.ids
        self.assertEqual(self.queued_ids(), [a, b, c, d])
        self.move(c, "up")
        self.assertEqual(self.queued_ids(), [a, c, b, d])
        self.move(a, "down")
        self.assertEqual(self.queued_ids(), [c, a, b, d])
        self.move(d, "top")
        self.assertEqual(self.queued_ids(), [d, c, a, b])
        self.move(d, "up")  # already first: nothing changes
        self.assertEqual(self.queued_ids(), [d, c, a, b])
        self.assertEqual(self.cli_json("queue", "move", str(b), "top")["id"], b)
        self.assertEqual(self.queued_ids(), [b, d, c, a])
        extra = self.ok("POST", self.orders_url(), self.order(key="fauna/otro", count=1), 201)["entries"][0]["id"]
        self.assertEqual(self.queued_ids()[-1], extra)  # a new entry still goes last

    def test_worker_takes_the_moved_entry_first(self):
        a, b, c, d = self.ids
        self.move(d, "top")
        self.cli("work", "--once")
        self.assertEqual(queue.get(d)["state"], "done")
        self.assertEqual(queue.get(a)["state"], "queued")

    def test_errors(self):
        a = self.ids[0]
        self.bad("POST", "/api/queue/%d/move" % a, {"to": "sideways"}, 400, "queue.bad_move")
        self.bad("POST", "/api/queue/%d/move" % a, {}, 400, "api.bad_param")
        self.bad("POST", "/api/queue/999/move", {"to": "up"}, 404, "queue.unknown")
        self.hold_worker_lock()
        queue.claim()
        err = self.bad("POST", "/api/queue/%d/move" % a, {"to": "down"}, 409, "queue.not_movable")
        self.assertEqual(err["params"]["state"], "running")
        queue.cancel(self.ids[1])
        self.bad("POST", "/api/queue/%d/move" % self.ids[1], {"to": "up"}, 409, "queue.not_movable")

    def test_clear_cancels_queued_and_never_running(self):
        a, b, c, d = self.ids
        self.hold_worker_lock()
        queue.claim()  # a is running
        got = self.ok("POST", "/api/queue/clear", {})
        self.assertEqual(sorted(e["id"] for e in got), [b, c, d])
        self.assertEqual(queue.get(a)["state"], "running")
        self.assertEqual(queue.list_entries(["queued"]), [])
        self.assertEqual(self.ok("POST", "/api/queue/clear", {}), [])

    def test_clear_by_project_and_cli(self):
        other = self.tmp / "other"
        other.mkdir()
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        cfg["name"] = "otro"
        (other / "galivelop-images.json").write_text(json.dumps(cfg))
        self.cli("project", "add", str(other))
        self.ok("POST", "/api/projects/otro/orders", self.order(key="x", count=2), 201)
        got = self.cli_json("queue", "clear", "--project", "otro")
        self.assertEqual(len(got), 2)
        self.assertEqual(len(queue.list_entries(["queued"])), 4)
        self.bad("POST", "/api/queue/clear", {"project": 3}, 400, "api.bad_param")
        self.bad("POST", "/api/queue/clear", {"all": True}, 400, "api.bad_param")

    def test_queue_without_positions_orders_by_id(self):
        path = queue.queue_path()
        data = json.loads(path.read_text())
        for e in data["entries"]:
            e.pop("position", None)
        path.write_text(json.dumps(data))
        self.assertEqual(self.queued_ids(), self.ids)
        self.move(self.ids[2], "top")
        self.assertEqual(self.queued_ids()[0], self.ids[2])


if __name__ == "__main__":
    unittest.main()
