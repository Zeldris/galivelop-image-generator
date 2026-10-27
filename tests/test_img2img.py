"""img2img (F2.7 b): `initImage`/`strength` in the order schema, submit, specs, queue, worker, argv, metadata, CLI."""
import json
import unittest

from gimg import engine, orders, png, queue, schema, worker
from gimg.engine_sdcpp import SdCppEngine
from gimg.errors import GimgError
from tests.test_cli import ORDER, CliBase
from tests.test_delivery import DeliveryBase
from tests.test_engine_sdcpp import Base as SdBase

SPEC = {"key": "a", "profile": "banner", "prompt": "a cat"}


class SchemaTests(unittest.TestCase):
    def errors(self, **extra):
        return schema.validate(dict(SPEC, **extra), schema.load_schema("order"))

    def test_valid(self):
        self.assertEqual(self.errors(initImage="refs/base.png", strength=0.6), [])
        self.assertEqual(self.errors(initImage="a.png", strength=0), [])
        self.assertEqual(self.errors(initImage="a.png", strength=1), [])

    def test_rejections_name_path_and_keyword(self):
        for bad in ("/etc/x.png", "~/x.png", "../x.png", "a/../x.png", "a\nb.png", "a\x00b.png"):
            found = self.errors(initImage=bad)
            self.assertTrue(found and "initImage" in str(found) and "pattern" in str(found), (bad, found))
        for bad, word in ((1.5, "maximum"), (-0.1, "minimum"), ("x", "type")):
            found = self.errors(initImage="a.png", strength=bad)
            self.assertTrue(found and "strength" in str(found) and word in str(found), (bad, found))


class FlowTests(DeliveryBase):
    def submit(self, **extra):
        return orders.submit("proj", dict(SPEC, **extra))

    def make_init(self, rel="refs/base.png"):
        target = self.projects["proj"] / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x")
        return target

    def test_strength_without_init_is_rejected_with_its_code(self):
        with self.assertRaises(GimgError) as cm:
            self.submit(strength=0.5)
        self.assertEqual(cm.exception.code, "order.strength_without_init")
        self.assertIn("initImage", cm.exception.message("en"))

    def test_submit_stores_and_resubmit_replaces_or_clears(self):
        rec = self.submit(initImage="refs/base.png", strength=0.4)
        self.assertEqual((rec["initImage"], rec["strength"]), ("refs/base.png", 0.4))
        rec = self.submit(initImage="refs/other.png")
        self.assertEqual((rec["initImage"], rec["strength"]), ("refs/other.png", None))
        rec = self.submit()
        self.assertEqual((rec["initImage"], rec["strength"]), (None, None))

    def test_specs_queue_and_attempt_carry_the_fields(self):
        self.submit(initImage="refs/base.png", strength=0.4)
        specs = orders.attempt_specs("proj", "a", "banner", 2)
        self.assertEqual([(s["initImage"], s["strength"]) for s in specs], [("refs/base.png", 0.4)] * 2)
        entries = queue.enqueue("proj", "a", "banner", specs)
        self.assertEqual([(e["initImage"], e["strength"]) for e in entries], [("refs/base.png", 0.4)] * 2)
        attempt = orders.add_attempt("proj", "a", "banner", dict(specs[0], params={}), entry_id=1)
        record = orders.get("proj", "a", "banner")["attempts"][0]
        self.assertEqual((attempt, record["initImage"], record["strength"]), (1, "refs/base.png", 0.4))

    def test_order_without_them_keeps_its_shape(self):
        self.submit()
        spec = orders.attempt_specs("proj", "a", "banner")[0]
        self.assertEqual((spec["initImage"], spec["strength"]), (None, None))
        entry = queue.enqueue("proj", "a", "banner", [spec])[0]
        self.assertEqual((entry["initImage"], entry["strength"]), (None, None))
        orders.add_attempt("proj", "a", "banner", dict(spec, params={}), entry_id=1)
        record = orders.get("proj", "a", "banner")["attempts"][0]
        self.assertNotIn("initImage", record)
        self.assertNotIn("strength", record)
        old = {k: v for k, v in entry.items() if k not in ("initImage", "strength")}
        self.assertIsNone(old.get("initImage"))

    def test_worker_resolves_init_image_and_writes_metadata(self):
        init = self.make_init()
        self.submit(initImage="refs/base.png", strength=0.4)
        queue.enqueue("proj", "a", "banner", orders.attempt_specs("proj", "a", "banner"))
        seen = []

        class Spy(engine.FakeEngine):
            def generate(self, job, should_cancel):
                seen.append((job.init_image, job.strength))
                return super().generate(job, should_cancel)

        worker.run(engine=Spy())
        self.assertEqual(seen, [(str(init.resolve()), 0.4)])
        attempt = orders.get("proj", "a", "banner")["attempts"][0]
        meta = json.loads(png.read_text_chunks(orders.attempt_image("proj", "a", "banner", attempt))["gimg"])
        self.assertEqual((meta["initImage"], meta["strength"]), ("base.png", 0.4))

    def test_worker_missing_init_image(self):
        self.submit(initImage="refs/nope.png")
        entry = queue.enqueue("proj", "a", "banner", orders.attempt_specs("proj", "a", "banner"))[0]
        worker.run()
        done = queue.get(entry["id"])
        self.assertEqual((done["state"], done["error"]),
                         ("failed", {"code": "worker.init_image_missing", "params": {"path": "refs/nope.png"}}))

    def test_worker_rejects_init_image_symlinked_outside(self):
        outside = self.tmp / "secret.png"
        outside.write_bytes(b"x")
        (self.projects["proj"] / "link.png").symlink_to(outside)
        self.submit(initImage="link.png")
        entry = queue.enqueue("proj", "a", "banner", orders.attempt_specs("proj", "a", "banner"))[0]
        worker.run()
        done = queue.get(entry["id"])
        self.assertEqual((done["state"], done["error"]["code"]), ("failed", "path.outside"))

    def test_metadata_without_init_image_has_neither_key(self):
        entry = {"project": "p", "key": "a", "profile": "b", "seed": 1, "prompt": "x", "params": {}, "references": []}
        self.assertNotIn("initImage", worker.metadata_for(entry, None))
        self.assertNotIn("strength", worker.metadata_for(dict(entry, strength=0.5), None))
        meta = worker.metadata_for(dict(entry, initImage="d/i.png"), None)
        self.assertEqual(meta["initImage"], "i.png")
        self.assertNotIn("strength", meta)


class ArgvTests(SdBase):
    def test_flux2_img2img_has_i_and_strength_only(self):
        _, job, _ = self.run_job(init_image=str(self.tmp / "i.png"), strength=0.6)
        argv = self.argv()
        at = argv.index("-i")
        self.assertEqual(argv[at:at + 3], ["-i", str(self.tmp / "i.png"), "--strength"])
        self.assertEqual(argv[at + 3], "0.6")
        self.assertEqual(argv[at + 4], "--preview")
        self.assertNotIn("--extra-sample-args", argv)

    def test_flux3_adds_the_catalog_args_after_strength(self):
        self.install("flux3-klein-q8")
        _, job, _ = self.run_job(model="flux3-klein-q8", init_image="/x/i.png", strength=0.25)
        argv = self.argv()
        at = argv.index("-i")
        self.assertEqual(argv[at:at + 6], ["-i", "/x/i.png", "--strength", "0.25",
                                           "--extra-sample-args", "strength_as_noise_level=true"])
        self.assertEqual(argv[at + 6], "--preview")

    def test_no_strength_and_no_init_image(self):
        self.install("flux3-klein-q8")
        self.run_job(model="flux3-klein-q8", init_image="/x/i.png")
        argv = self.argv()
        self.assertNotIn("--strength", argv)
        self.assertIn("--extra-sample-args", argv)
        self.run_job(model="flux3-klein-q8", strength=0.5)  # a strength alone does nothing
        argv = self.argv()
        for flag in ("-i", "--strength", "--extra-sample-args"):
            self.assertNotIn(flag, argv)


class CliTests(CliBase):
    def test_order_show_prints_init_image(self):
        name, key, prof = "example-world", ORDER["key"], ORDER["profile"]
        self.ok("project", "add", str(self.root))
        self.write_order(count=1)
        self.js("order", "submit", name, str(self.order_file))
        self.assertNotRegex(self.ok("order", "show", name, key, prof), "(imagen inicial|init image)")
        self.write_order(count=1, initImage="refs/base.png", strength=0.5)
        self.js("order", "submit", name, str(self.order_file))
        shown = self.ok("order", "show", name, key, prof)
        self.assertRegex(shown, r"(imagen inicial|init image): refs/base.png \((fuerza|strength) 0.5\)")
        self.write_order(count=1, initImage="refs/base.png")
        self.js("order", "submit", name, str(self.order_file))
        self.assertRegex(self.ok("order", "show", name, key, prof), r"refs/base.png \((sin fuerza|no strength)\)")


if __name__ == "__main__":
    unittest.main()
