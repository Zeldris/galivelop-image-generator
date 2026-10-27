"""Drafts (F2.7 a, D32): profile and order schema, `draft_params`, specs, queue, worker, choose, CLI."""
import copy
import json
import unittest

from gimg import delivery, engine, log, orders, png, projects, queue, schema, worker
from gimg.errors import GimgError
from tests.test_cli import EXAMPLE, ORDER, CliBase
from tests.test_delivery import DeliveryBase

BASE = {"width": 1280, "height": 512, "steps": 6, "cfg": 1.0, "sampler": "euler", "model": "flux2-klein-4b-q8"}


class DraftParamsTests(unittest.TestCase):
    def test_default_without_draft(self):
        out = orders.draft_params({}, BASE)
        self.assertEqual((out["width"], out["height"], out["steps"]), (640, 256, 8))
        self.assertEqual((out["cfg"], out["sampler"], out["model"]), (1.0, "euler", BASE["model"]))
        self.assertEqual(BASE["steps"], 6)  # the input is not touched

    def test_declared_values(self):
        out = orders.draft_params({"draft": {"scale": 0.25, "steps": 3, "model": "m2"}}, BASE)
        self.assertEqual((out["width"], out["height"], out["steps"], out["model"]), (320, 128, 3, "m2"))

    def test_declared_empty_keeps_everything(self):
        self.assertEqual(orders.draft_params({"draft": {}}, BASE), BASE)

    def test_rounding_and_minimum(self):
        out = orders.draft_params({"draft": {"scale": 0.5}}, {"width": 1000, "height": 100})
        self.assertEqual((out["width"], out["height"]), (512, 64))  # 500/64 = 7.8 -> 8; 50/64 -> 1
        out = orders.draft_params({"draft": {"scale": 0.1}}, {"width": 128, "height": 640})
        self.assertEqual((out["width"], out["height"]), (64, 64))
        self.assertNotIn("steps", orders.draft_params({"draft": {"scale": 1}}, {"width": 64}))


class DraftSchemaTests(unittest.TestCase):
    def errors(self, draft):
        cfg = copy.deepcopy(EXAMPLE)
        cfg["profiles"]["banner"]["draft"] = draft
        return schema.validate(cfg, schema.load_schema("project-config"))

    def test_valid_and_invalid(self):
        self.assertEqual(self.errors({"model": "flux2-klein-4b-q8", "steps": 4, "scale": 0.5}), [])
        self.assertEqual(self.errors({}), [])
        for bad in ({"scale": 1.5}, {"scale": 0.05}, {"steps": 0}, {"model": ""}, {"extra": 1}):
            self.assertTrue(self.errors(bad), bad)

    def test_order_draft_is_boolean(self):
        sch = schema.load_schema("order")
        order = {"key": "a", "profile": "banner", "prompt": "x"}
        self.assertEqual(schema.validate(dict(order, draft=True), sch), [])
        self.assertTrue(schema.validate(dict(order, draft="yes"), sch))


class DraftFlowTests(DeliveryBase):
    def set_draft(self, draft):
        cfg = json.loads(self.config().read_text())
        cfg["profiles"]["banner"]["draft"] = draft
        self.config().write_text(json.dumps(cfg))

    def submit(self, **extra):
        orders.submit("proj", dict({"key": "a", "profile": "banner", "prompt": "a cat"}, **extra))

    def specs(self, **kw):
        return orders.attempt_specs("proj", "a", "banner", **kw)

    def test_unknown_draft_model_is_rejected(self):
        self.set_draft({"model": "no-such-model"})
        with self.assertRaises(GimgError) as cm:
            projects.get("proj")
        self.assertEqual(cm.exception.code, "model.unknown")

    def test_submit_stores_draft_and_resubmit_replaces(self):
        self.assertIs(orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "x"})["draft"], False)
        self.assertIs(orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "x", "draft": True})["draft"], True)
        self.assertIs(orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "x"})["draft"], False)

    def test_specs_follow_order_and_can_be_forced(self):
        self.submit(draft=True)
        spec = self.specs()[0]
        self.assertIs(spec["draft"], True)
        self.assertEqual((spec["params"]["width"], spec["params"]["height"], spec["params"]["steps"]), (640, 256, 8))
        self.assertIs(self.specs(draft=False)[0]["draft"], False)
        self.assertEqual(self.specs(draft=False)[0]["params"]["width"], 1280)
        self.submit()
        self.assertIs(self.specs()[0]["draft"], False)
        self.assertEqual(self.specs(draft=True)[0]["params"]["width"], 640)

    def test_steps_precedence(self):
        self.set_draft({"steps": 3})
        self.submit(draft=True, params={"steps": 9})
        self.assertEqual(self.specs()[0]["params"]["steps"], 3)  # the draft's steps beat the order's
        self.assertEqual(self.specs(params={"steps": 12})[0]["params"]["steps"], 12)  # the call's win
        self.assertEqual(self.specs(params={"cfg": 2.0})[0]["params"]["cfg"], 2.0)

    def test_queue_worker_attempt_png_and_log(self):
        self.submit()
        entries = queue.enqueue("proj", "a", "banner", self.specs(draft=True) + self.specs())
        self.assertEqual([e["draft"] for e in entries], [True, False])
        seen = []
        real = engine.FakeEngine.generate

        def spy(eng, job, should_cancel):
            seen.append(job.draft)
            return real(eng, job, should_cancel)

        engine.FakeEngine.generate = spy
        self.addCleanup(setattr, engine.FakeEngine, "generate", real)
        worker.run()
        self.assertEqual(seen, [True, False])
        first, second = orders.get("proj", "a", "banner")["attempts"]
        self.assertIs(first.get("draft"), True)
        self.assertNotIn("draft", second)
        meta = json.loads(png.read_text_chunks(orders.attempt_image("proj", "a", "banner", first))["gimg"])
        self.assertIs(meta["draft"], True)
        meta = json.loads(png.read_text_chunks(orders.attempt_image("proj", "a", "banner", second))["gimg"])
        self.assertNotIn("draft", meta)
        lines = [json.loads(x) for x in log.log_path("proj").read_text().splitlines()]
        self.assertEqual([x["app.image.draft"] for x in lines], [True, False])

    def test_old_queue_entry_is_not_a_draft(self):
        entry = {"project": "proj", "key": "a", "profile": "banner", "seed": 1, "prompt": "p", "params": {}, "references": []}
        self.assertNotIn("draft", worker.metadata_for(entry, None))

    def test_draft_cannot_be_chosen(self):
        self.submit()
        queue.enqueue("proj", "a", "banner", self.specs(draft=True) + self.specs())
        worker.run()
        self.assertEqual(self.code(orders.choose, "proj", "a", "banner", 1), "order.choose_draft")
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", 1), "order.choose_draft")
        self.assertFalse((self.projects["proj"] / "galivelop-images.manifest.json").exists())
        self.assertEqual(self.state(), (None, []))
        self.assertEqual(orders.mark("proj", "a", "banner", 1, "candidate")["state"], "candidate")
        self.assertEqual(delivery.choose("proj", "a", "banner", 2)["new"], 2)


class DraftCliTests(CliBase):
    def test_submit_and_new_with_draft(self):
        name, key, prof = "example-world", ORDER["key"], ORDER["profile"]
        self.ok("project", "add", str(self.root))
        queued = self.js("order", "submit", name, str(self.order_file), "--draft")
        self.assertTrue(all(e["draft"] for e in queued["entries"]))
        self.assertEqual(queued["entries"][0]["params"]["steps"], 8)
        self.assertIn("[draft]", self.ok("queue", "list"))
        queued = self.js("attempt", "new", name, key, prof, "--draft")
        self.assertTrue(queued["entries"][0]["draft"])
        self.js("work")
        shown = self.ok("order", "show", name, key, prof)
        self.assertEqual(shown.count("[draft]"), 3)
        self.assertEqual([a.get("draft") for a in self.js("order", "show", name, key, prof)["attempts"]],
                         [True, True, True])

    def test_without_option_uses_the_order(self):
        name, key, prof = "example-world", ORDER["key"], ORDER["profile"]
        self.ok("project", "add", str(self.root))
        self.write_order(count=1, draft=True)
        self.assertTrue(self.js("order", "submit", name, str(self.order_file))["entries"][0]["draft"])
        self.assertTrue(self.js("attempt", "new", name, key, prof)["entries"][0]["draft"])
        self.write_order(count=1)
        self.assertFalse(self.js("order", "submit", name, str(self.order_file))["entries"][0]["draft"])
        self.assertNotIn("[draft]", self.ok("order", "show", name, key, prof))


if __name__ == "__main__":
    unittest.main()
