import json
import os
import stat
import unittest
from unittest import mock

from gimg.errors import GimgError
from gimg import delivery, engine, orders, worker
from tests.test_queue import QueueBase


class DeliveryBase(QueueBase):
    def config(self, name="proj"):
        return self.projects[name] / "galivelop-images.json"

    def set_delivery(self, name="proj", **fields):
        cfg = json.loads(self.config(name).read_text())
        cfg["delivery"].update(fields)
        self.config(name).write_text(json.dumps(cfg))

    def attempts(self, count=2, key="a", profile="banner"):
        """Real attempts through the queue and the fake engine."""
        self.push(key=key, profile=profile, count=count, seed=5)
        worker.run()
        return [a["id"] for a in orders.get("proj", key, profile)["attempts"]]

    def manifest(self, name="proj"):
        return json.loads((self.projects[name] / "galivelop-images.manifest.json").read_text())

    def state(self, key="a", profile="banner"):
        order = orders.get("proj", key, profile)
        return order["chosen"], order["chosenHistory"]

    def delivered(self, rel="uploads/images/a-banner.png"):
        return self.projects["proj"] / rel


class DeliveryTests(DeliveryBase):
    def test_choose_delivers_and_writes_manifest(self):
        one, _two = self.attempts()
        self.assertEqual(delivery.choose("proj", "a", "banner", one), {"old": None, "new": one})
        out = self.delivered()
        self.assertEqual(out.read_bytes(), orders.attempt_image(
            "proj", "a", "banner", orders.get("proj", "a", "banner")["attempts"][0]).read_bytes())
        entry = self.manifest()["images"]["a"]["banner"]
        self.assertEqual((entry["file"], entry["attemptId"], entry["seed"], entry["engine"],
                          entry["engineVersion"]), ("uploads/images/a-banner.png", one, 5, "fake",
                                                    engine.FAKE_VERSION))
        self.assertEqual(set(entry), {"file", "prompt", "seed", "params", "references", "engine",
                                      "engineVersion", "attemptId", "chosenAt"})
        self.assertEqual(entry["params"]["width"], 1280)

    def test_manifest_format(self):
        one, _ = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        text = (self.projects["proj"] / "galivelop-images.manifest.json").read_text()
        data = json.loads(text)
        self.assertEqual(data["version"], 1)
        self.assertEqual(text, json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        self.assertFalse(data["images"]["a"]["banner"]["file"].startswith("/"))

    def test_nested_key_and_template(self):
        self.set_delivery(template="{key}/{profile}.png")
        one, _ = self.attempts(key="x/y")
        delivery.choose("proj", "x/y", "banner", one)
        self.assertTrue(self.delivered("uploads/images/x/y/banner.png").is_file())
        self.assertEqual(self.manifest()["images"]["x/y"]["banner"]["file"],
                         "uploads/images/x/y/banner.png")

    def test_choose_another_replaces(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        first = self.delivered().read_bytes()
        self.assertEqual(delivery.choose("proj", "a", "banner", two), {"old": one, "new": two})
        self.assertNotEqual(self.delivered().read_bytes(), first)  # seed 5 vs 6: other color
        self.assertEqual(self.manifest()["images"]["a"]["banner"]["attemptId"], two)
        self.assertEqual(self.state(), (two, [None, one]))

    def test_two_profiles_one_key(self):
        one = self.attempts(1)[0]
        two = self.attempts(1, profile="thumbnail")[0]
        delivery.choose("proj", "a", "banner", one)
        delivery.choose("proj", "a", "thumbnail", two)
        self.assertEqual(set(self.manifest()["images"]["a"]), {"banner", "thumbnail"})
        delivery.undo("proj", "a", "banner")
        self.assertEqual(set(self.manifest()["images"]["a"]), {"thumbnail"})

    def test_undo_to_previous_and_to_null(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        bytes_one = self.delivered().read_bytes()
        delivery.choose("proj", "a", "banner", two)
        self.assertEqual(delivery.undo("proj", "a", "banner"), {"old": two, "new": one})
        self.assertEqual(self.delivered().read_bytes(), bytes_one)
        self.assertEqual(self.manifest()["images"]["a"]["banner"]["attemptId"], one)
        self.assertEqual(delivery.undo("proj", "a", "banner"), {"old": one, "new": None})
        self.assertFalse(self.delivered().exists())
        self.assertEqual(self.manifest(), {"version": 1, "images": {}})

    def test_undo_to_null_with_missing_file(self):
        one, _ = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        self.delivered().unlink()
        delivery.undo("proj", "a", "banner")
        self.assertEqual(self.state(), (None, []))
        self.assertEqual(self.manifest()["images"], {})

    def test_undo_keeps_other_entries(self):
        one = self.attempts(count=1)[0]
        other = self.attempts(count=1, key="b")[0]
        delivery.choose("proj", "a", "banner", one)
        delivery.choose("proj", "b", "banner", other)
        delivery.undo("proj", "a", "banner")
        self.assertEqual(list(self.manifest()["images"]), ["b"])

    def test_undo_empty_history(self):
        self.attempts(1)
        self.assertEqual(self.code(delivery.undo, "proj", "a", "banner"), "order.history_empty")

    def test_choose_same_again_redelivers(self):
        one, _ = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        self.delivered().unlink()
        self.assertEqual(delivery.choose("proj", "a", "banner", one), {"old": one, "new": one})
        self.assertTrue(self.delivered().is_file())
        self.assertEqual(self.state(), (one, [None]))

    def test_mode_honours_umask(self):
        one, _ = self.attempts()
        old = os.umask(0o022)
        try:
            delivery.choose("proj", "a", "banner", one)
        finally:
            os.umask(old)
        self.assertEqual(stat.S_IMODE(self.delivered().stat().st_mode), 0o644)
        self.assertEqual(stat.S_IMODE((self.projects["proj"] / "galivelop-images.manifest.json")
                                      .stat().st_mode), 0o644)
        self.assertEqual([p.name for p in self.delivered().parent.iterdir()], ["a-banner.png"])

    def test_unknown_and_discarded_leave_nothing(self):
        one, _ = self.attempts()
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", 99), "order.attempt_unknown")
        orders.mark("proj", "a", "banner", one, "discarded")
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "order.choose_discarded")
        self.assertFalse(self.delivered().exists())
        self.assertEqual(self.state(), (None, []))


class DeliveryFailureTests(DeliveryBase):
    def patched_config(self, **delivery_fields):
        """The schema already forbids `..` in the template; the guard must hold even if it did not."""
        real = delivery.projects.get("proj")
        real["config"]["delivery"].update(delivery_fields)
        return mock.patch("gimg.delivery.projects.get", return_value=real)

    def test_template_escapes_delivery_dir(self):
        one, _ = self.attempts()
        for template in ("../{key}-{profile}.png", "{key}/../../{profile}.png", "/abs/{key}-{profile}.png",
                         "~/{key}-{profile}.png"):
            with self.patched_config(template=template):
                self.assertIn(self.code(delivery.choose, "proj", "a", "banner", one),
                              ("path.dotdot", "path.absolute", "path.tilde"))
            self.assertEqual(self.state(), (None, []))
        self.assertFalse((self.projects["proj"] / "uploads" / "a-banner.png").exists())

    def test_delivery_dir_symlinked_outside(self):
        one, _ = self.attempts()
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.projects["proj"] / "uploads").mkdir()
        (self.projects["proj"] / "uploads" / "images").symlink_to(outside)
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "path.outside")
        self.assertEqual(list(outside.iterdir()), [])
        order = json.loads((self.tmp / "data/projects/proj/orders/a/@banner/order.json").read_text())
        self.assertEqual((order["chosen"], order["chosenHistory"]), (None, []))

    def test_parent_symlink_in_nested_key(self):
        self.set_delivery(template="{key}/{profile}.png")
        one, _ = self.attempts(key="x/y")
        outside = self.tmp / "outside"
        outside.mkdir()
        base = self.projects["proj"] / "uploads" / "images"
        base.mkdir(parents=True)
        (base / "x").symlink_to(outside)
        self.assertEqual(self.code(delivery.choose, "proj", "x/y", "banner", one), "path.outside")
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_at_target_outside(self):
        one, _ = self.attempts()
        victim = self.tmp / "victim.png"
        victim.write_bytes(b"keep")
        base = self.projects["proj"] / "uploads" / "images"
        base.mkdir(parents=True)
        (base / "a-banner.png").symlink_to(victim)
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "path.outside")
        self.assertEqual(victim.read_bytes(), b"keep")
        self.assertEqual(self.state(), (None, []))

    def test_template_onto_manifest(self):
        cfg = json.loads(self.config().read_text())
        cfg["manifest"] = "uploads/images/a-banner.png"
        self.config().write_text(json.dumps(cfg))
        one, _ = self.attempts()
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "delivery.reserved")
        self.assertEqual(self.state(), (None, []))

    def test_missing_source_image(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        att = orders.get("proj", "a", "banner")["attempts"][1]
        orders.attempt_image("proj", "a", "banner", att).unlink()
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", two), "delivery.source_missing")
        self.assertEqual(self.state(), (one, [None]))
        self.assertEqual(self.manifest()["images"]["a"]["banner"]["attemptId"], one)

    def test_undo_missing_source_leaves_order(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        delivery.choose("proj", "a", "banner", two)
        orders.attempt_image("proj", "a", "banner", orders.get("proj", "a", "banner")["attempts"][0]).unlink()
        self.assertEqual(self.code(delivery.undo, "proj", "a", "banner"), "delivery.source_missing")
        self.assertEqual(self.state(), (two, [None, one]))

    def test_missing_reference_does_not_block_delivery(self):
        orders.submit("proj", {"key": "r", "profile": "banner", "prompt": "p"})
        orders.add_attempt("proj", "r", "banner", {"seed": 1, "prompt": "p", "params": {},
                                                    "references": ["refs/none.png"]})
        att = orders.get("proj", "r", "banner")["attempts"][0]
        path = orders.attempt_image("proj", "r", "banner", att)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(engine.png_bytes(2, 2, (1, 2, 3)))
        self.assertEqual(delivery.choose("proj", "r", "banner", 1), {"old": None, "new": 1})
        self.assertEqual(self.manifest()["images"]["r"]["banner"]["references"], ["refs/none.png"])

    def test_corrupt_manifest(self):
        one, _ = self.attempts()
        manifest = self.projects["proj"] / "galivelop-images.manifest.json"
        for bad in ("{not json", "[]", '{"version": 2, "images": {}}', '{"version": 1, "images": {"a": 3}}'):
            manifest.write_text(bad)
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one),
                             "delivery.manifest_corrupt")
            self.assertEqual(self.state(), (None, []))
            self.assertFalse(self.delivered().exists())
            self.assertEqual(manifest.read_text(), bad)

    def test_failure_after_order_change_reverts_choose(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        with mock.patch("gimg.delivery._copy", side_effect=delivery.GimgError("delivery.write_failed",
                                                                                path="x", reason="boom")):
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", two), "delivery.write_failed")
        self.assertEqual(self.state(), (one, [None]))

    def test_failure_after_order_change_reverts_undo(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        delivery.choose("proj", "a", "banner", two)
        with mock.patch("gimg.delivery._copy", side_effect=delivery.GimgError("delivery.write_failed",
                                                                                path="x", reason="boom")):
            self.assertEqual(self.code(delivery.undo, "proj", "a", "banner"), "delivery.write_failed")
        self.assertEqual(self.state(), (two, [None, one]))

    def test_target_is_a_directory(self):
        one, _ = self.attempts()
        (self.projects["proj"] / "uploads" / "images" / "a-banner.png").mkdir(parents=True)
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "delivery.write_failed")
        self.assertEqual(self.state(), (None, []))
        self.assertEqual([p.name for p in (self.projects["proj"] / "uploads" / "images").iterdir()],
                         ["a-banner.png"])


class DeliveryRollbackTests(DeliveryBase):
    def fail_manifest_write(self):
        real = delivery.fsutil.write_json

        def write(path, data):
            if str(path).endswith("galivelop-images.manifest.json"):
                raise OSError("boom")
            return real(path, data)
        return mock.patch("gimg.delivery.fsutil.write_json", side_effect=write)

    def image(self, attempt_id):
        att = [a for a in orders.get("proj", "a", "banner")["attempts"] if a["id"] == attempt_id][0]
        return orders.attempt_image("proj", "a", "banner", att).read_bytes()

    def test_choose_manifest_failure_restores_previous_file(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        before = self.manifest()
        with self.fail_manifest_write():
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", two), "delivery.write_failed")
        self.assertEqual(self.state(), (one, [None]))
        self.assertEqual(self.delivered().read_bytes(), self.image(one))
        self.assertEqual(self.manifest(), before)

    def test_choose_manifest_failure_from_null_removes_file(self):
        one, _ = self.attempts()
        with self.fail_manifest_write():
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "delivery.write_failed")
        self.assertEqual(self.state(), (None, []))
        self.assertFalse(self.delivered().exists())
        self.assertFalse((self.projects["proj"] / "galivelop-images.manifest.json").exists())

    def test_undo_manifest_failure_to_older_restores_file(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        delivery.choose("proj", "a", "banner", two)
        before = self.manifest()
        with self.fail_manifest_write():
            self.assertEqual(self.code(delivery.undo, "proj", "a", "banner"), "delivery.write_failed")
        self.assertEqual(self.state(), (two, [None, one]))
        self.assertEqual(self.delivered().read_bytes(), self.image(two))
        self.assertEqual(self.manifest(), before)

    def test_undo_manifest_failure_to_null_restores_file(self):
        one, _ = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        before = self.manifest()
        with self.fail_manifest_write():
            self.assertEqual(self.code(delivery.undo, "proj", "a", "banner"), "delivery.write_failed")
        self.assertEqual(self.state(), (one, [None]))
        self.assertEqual(self.delivered().read_bytes(), self.image(one))
        self.assertEqual(self.manifest(), before)

    def test_restore_failure_raises_original_error(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        real = delivery._copy
        calls = []

        def copy(source, target):
            calls.append(source)
            if len(calls) > 1:
                raise delivery.GimgError("delivery.write_failed", path="x", reason="second")
            return real(source, target)
        with self.fail_manifest_write(), mock.patch("gimg.delivery._copy", side_effect=copy):
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", two), "delivery.write_failed")
        self.assertEqual(len(calls), 2)
        self.assertEqual(self.state(), (one, [None]))

    def test_undo_to_null_keeps_file_not_in_manifest_target(self):
        one, _ = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        self.set_delivery(template="other-{key}-{profile}.png")
        stray = self.delivered("uploads/images/other-a-banner.png")
        stray.write_bytes(b"not ours")
        delivery.undo("proj", "a", "banner")
        self.assertEqual(stray.read_bytes(), b"not ours")
        self.assertTrue(self.delivered().is_file())  # the old target is not the new one: left alone
        self.assertEqual(self.manifest(), {"version": 1, "images": {}})

    def test_choose_overwrites_existing_file(self):
        one, _ = self.attempts()
        self.delivered().parent.mkdir(parents=True)
        self.delivered().write_bytes(b"old")
        delivery.choose("proj", "a", "banner", one)
        self.assertEqual(self.delivered().read_bytes(), self.image(one))

    def test_copy_interrupt_leaves_no_temp_file_or_fd(self):
        one, _ = self.attempts()
        src = orders.attempt_image("proj", "a", "banner", orders.get("proj", "a", "banner")["attempts"][0])
        out = self.projects["proj"] / "uploads" / "images"
        fds = len(os.listdir("/proc/self/fd"))
        with mock.patch("gimg.delivery.fsutil.honour_umask", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                delivery._copy(src, out / "a-banner.png")
        self.assertEqual(list(out.iterdir()), [])
        self.assertEqual(len(os.listdir("/proc/self/fd")), fds)


class DeliveryFixesTests(DeliveryBase):
    def test_no_lock_file_in_project_root(self):
        one, two = self.attempts()
        delivery.choose("proj", "a", "banner", one)
        delivery.choose("proj", "a", "banner", two)
        delivery.undo("proj", "a", "banner")
        delivery.undo("proj", "a", "banner")
        self.assertEqual([p for p in self.projects["proj"].rglob("*.lock")], [])

    def test_target_inside_git_or_config_is_rejected(self):
        one, _ = self.attempts()
        for fields, code in (({"dir": ".", "template": ".git/{key}-{profile}.png"}, "project.forbidden_git"),
                             ({"dir": ".", "template": ".GIT/{key}-{profile}.png"}, "project.forbidden_git")):
            self.set_delivery(**fields)
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), code, fields)
            self.assertEqual(self.state(), (None, []))
        self.assertFalse((self.projects["proj"] / ".git").exists())

    def test_two_pairs_same_target_refused(self):
        cfg = json.loads(self.config().read_text())
        cfg["profiles"]["banne"] = cfg["profiles"]["banner"]
        cfg["delivery"]["template"] = "{profile}{key}.png"
        self.config().write_text(json.dumps(cfg))
        # ("a", "banner") and ("ra", "banne") both render to bannera.png... via banner+a / banne+ra
        one, = self.attempts(1, key="a", profile="banner")
        other, = self.attempts(1, key="ra", profile="banne")
        delivery.choose("proj", "a", "banner", one)
        with self.assertRaises(GimgError) as cm:
            delivery.choose("proj", "ra", "banne", other)
        self.assertEqual((cm.exception.code, cm.exception.params["otherKey"], cm.exception.params["otherProfile"]),
                         ("delivery.target_taken", "a", "banner"))
        self.assertEqual(self.state("ra", "banne"), (None, []))
        self.assertEqual(self.delivered("uploads/images/bannera.png").read_bytes(),
                         orders.attempt_image("proj", "a", "banner", orders.get("proj", "a", "banner")["attempts"][0]).read_bytes())
        delivery.undo("proj", "a", "banner")
        delivery.choose("proj", "ra", "banne", other)  # free again

    def test_choose_waits_for_the_delivery_lock(self):
        import threading
        one, _ = self.attempts()
        done = threading.Event()
        with delivery._lock("proj"):
            thread = threading.Thread(target=lambda: (delivery.choose("proj", "a", "banner", one), done.set()))
            thread.start()
            self.assertFalse(done.wait(0.4))
            self.assertEqual(self.state(), (None, []))
        thread.join(5)
        self.assertTrue(done.is_set())
        self.assertEqual(self.state(), (one, [None]))

    def test_attempt_flipping_from_discarded_is_reverted(self):
        one, two = self.attempts()
        orders.mark("proj", "a", "banner", two, "discarded")
        stale = orders.get("proj", "a", "banner")
        orders.mark("proj", "a", "banner", two, "candidate")
        with mock.patch.object(orders, "get", return_value=stale):
            self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", two), "order.choose_discarded")
        self.assertEqual(self.state(), (None, []))
        self.assertFalse((self.projects["proj"] / "galivelop-images.manifest.json").exists())
        self.assertFalse(self.delivered().exists())


class AttemptEngineTests(DeliveryBase):
    def test_worker_records_engine(self):
        self.attempts(1)
        att = orders.get("proj", "a", "banner")["attempts"][0]
        self.assertEqual((att["engine"], att["engineVersion"]), ("fake", engine.FAKE_VERSION))


class DeliveryComposeTests(DeliveryBase):
    """F2.8: the delivered image is the composed one and the manifest says how it was composed."""
    INFO = {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg", "text": {"title": "Hi"}}

    def composed_attempt(self):
        (one,) = self.attempts(1)
        folder = orders._order_dir("proj", "a", "banner") / "attempts"
        (folder / "q1.raw.png").write_bytes(b"the raw image")
        orders.set_composed("proj", "a", "banner", one, self.INFO)
        return one, folder

    def test_the_manifest_copies_compose_and_the_composed_image_is_delivered(self):
        one, folder = self.composed_attempt()
        delivery.choose("proj", "a", "banner", one)
        self.assertEqual(self.manifest()["images"]["a"]["banner"]["compose"], self.INFO)
        self.assertEqual(self.delivered().read_bytes(), (folder / "q1.png").read_bytes())
        self.assertNotEqual(self.delivered().read_bytes(), b"the raw image")

    def test_an_attempt_without_compose_leaves_the_manifest_entry_as_before(self):
        (one,) = self.attempts(1)
        delivery.choose("proj", "a", "banner", one)
        self.assertNotIn("compose", self.manifest()["images"]["a"]["banner"])

    def test_a_malformed_compose_is_not_copied(self):
        (one,) = self.attempts(1)
        path = orders._order_file("proj", "a", "banner")
        data = json.loads(path.read_text())
        data["attempts"][0]["compose"] = "not an object"
        path.write_text(json.dumps(data))
        delivery.choose("proj", "a", "banner", one)
        self.assertNotIn("compose", self.manifest()["images"]["a"]["banner"])

    def test_an_attempt_that_failed_to_compose_is_not_delivered(self):
        (one,) = self.attempts(1)
        path = orders._order_file("proj", "a", "banner")
        data = json.loads(path.read_text())
        data["attempts"][0]["composeError"] = {"code": "compose.tool_missing", "params": {"tool": "ffmpeg"}}
        path.write_text(json.dumps(data))
        self.assertEqual(self.code(delivery.choose, "proj", "a", "banner", one), "order.choose_uncomposed")
        self.assertFalse(self.delivered().exists())
        self.assertFalse((self.projects["proj"] / "galivelop-images.manifest.json").exists())
        self.assertEqual(self.state(), (None, []))


if __name__ == "__main__":
    unittest.main()
