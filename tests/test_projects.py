import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import fsutil, projects, schema
from gimg.errors import GimgError, PathError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())


class ProjectTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data")})
        env.start()
        self.addCleanup(env.stop)

    def make(self, name="proj", **changes):
        root = self.tmp / name
        root.mkdir(exist_ok=True)
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        cfg["name"] = name
        for key, value in changes.items():
            if value is None:
                cfg.pop(key, None)
            else:
                cfg[key] = value
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        return root

    def code(self, fn, *args):
        with self.assertRaises(GimgError) as cm:
            fn(*args)
        return cm.exception

    def test_defaults_applied(self):
        root = self.make(delivery={"dir": "out"}, manifest=None)
        cfg = projects.load_config(root)
        self.assertEqual(cfg["delivery"]["template"], "{key}-{profile}.png")
        self.assertEqual(cfg["manifest"], "galivelop-images.manifest.json")

    def test_explicit_values_kept(self):
        root = self.make(delivery={"dir": "out", "template": "{profile}/{key}.png"}, manifest="m.json")
        cfg = projects.load_config(root)
        self.assertEqual(cfg["delivery"]["template"], "{profile}/{key}.png")
        self.assertEqual(cfg["manifest"], "m.json")

    def test_missing_and_bad_json(self):
        root = self.tmp / "empty"
        root.mkdir()
        self.assertEqual(self.code(projects.load_config, root).code, "project.config_missing")
        (root / "galivelop-images.json").write_text("{nope")
        self.assertEqual(self.code(projects.load_config, root).code, "project.config_unreadable")

    def test_schema_errors_listed_and_translated(self):
        root = self.make(profiles={})
        err = self.code(projects.load_config, root)
        self.assertEqual(err.code, "project.config_invalid")
        self.assertEqual([e.code for e in err.errors], ["minProperties"])
        self.assertIn("/profiles", err.message("en"))
        self.assertIn("no es válido", err.message("es"))

    def test_min_version(self):
        err = self.code(projects.load_config, self.make(minVersion="99.0.0"))
        self.assertEqual(err.code, "project.version_too_new")
        self.assertEqual(err.params["required"], "99.0.0")
        projects.load_config(self.make("ok", minVersion="0.1.0"))
        # numeric, not lexical: 0.10.0 > 0.9.0
        with mock.patch.object(projects, "__version__", "0.9.0"):
            self.assertEqual(
                self.code(projects.load_config, self.make("n", minVersion="0.10.0")).code,
                "project.version_too_new")

    def test_delivery_and_manifest_guards(self):
        cases = [
            ({"delivery": {"dir": ".git"}}, "project.forbidden_git"),
            ({"delivery": {"dir": ".git/images"}}, "project.forbidden_git"),
            ({"delivery": {"dir": "a/.GIT/x"}}, "project.forbidden_git"),
            ({"manifest": ".git/m.json"}, "project.forbidden_git"),
            ({"manifest": "galivelop-images.json"}, "project.forbidden_config"),
            ({"manifest": "a/../galivelop-images.json"}, "project.config_invalid"),
            ({"delivery": {"dir": "galivelop-images.json"}}, "project.forbidden_config"),
        ]
        for i, (change, code) in enumerate(cases):
            with self.subTest(change=change):
                err = self.code(projects.load_config, self.make("c%d" % i, **change))
                self.assertEqual(err.code, code)

    def test_delivery_symlink_into_git_or_outside(self):
        root = self.make("lnk")
        (root / ".git").mkdir()
        os.symlink(root / ".git", root / "sneaky")
        (root / "galivelop-images.json").write_text(json.dumps(
            dict(EXAMPLE, name="lnk", delivery={"dir": "sneaky"})))
        self.assertEqual(self.code(projects.load_config, root).code, "project.forbidden_git")
        os.symlink(self.tmp, root / "away")
        (root / "galivelop-images.json").write_text(json.dumps(
            dict(EXAMPLE, name="lnk", manifest="away/m.json")))
        self.assertEqual(self.code(projects.load_config, root).code, "path.outside")

    def test_registry_add_get_list_remove(self):
        a, b = self.make("alpha"), self.make("beta")
        self.assertEqual(projects.list_projects(), {})
        self.assertEqual(projects.add(a), "alpha")
        projects.add(b)
        projects.add(a)  # same name, same path: fine
        self.assertEqual(list(projects.list_projects()), ["alpha", "beta"])
        got = projects.get("alpha")
        self.assertEqual(got["root"], str(a))
        self.assertEqual(got["config"]["name"], "alpha")
        projects.remove("alpha")
        self.assertEqual(list(projects.list_projects()), ["beta"])
        self.assertEqual(self.code(projects.get, "alpha").code, "project.unknown")
        self.assertEqual(self.code(projects.remove, "alpha").code, "project.unknown")

    def test_same_name_other_path(self):
        a = self.make("alpha")
        other = self.tmp / "elsewhere"
        other.mkdir()
        (other / "galivelop-images.json").write_text((a / "galivelop-images.json").read_text())
        projects.add(a)
        err = self.code(projects.add, other)
        self.assertEqual(err.code, "project.name_taken")
        self.assertEqual(err.params["root"], str(a))

    def test_add_invalid_does_not_register(self):
        root = self.make("bad", profiles={})
        self.assertEqual(self.code(projects.add, root).code, "project.config_invalid")
        self.assertEqual(projects.list_projects(), {})
        self.assertEqual(self.code(projects.add, self.tmp / "nope").code, "project.root_not_dir")

    def test_config_reread_each_time(self):
        root = self.make("alpha")
        projects.add(root)
        self.assertEqual(projects.get("alpha")["config"]["delivery"]["dir"], "uploads/images")
        cfg = json.loads((root / "galivelop-images.json").read_text())
        cfg["delivery"]["dir"] = "other"
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        self.assertEqual(projects.get("alpha")["config"]["delivery"]["dir"], "other")

    def test_corrupt_registry(self):
        fsutil.write_json(projects.registry_path(), {"projects": {"x": 3}})
        self.assertEqual(self.code(projects.list_projects).code, "project.registry_corrupt")


class OrderLimitsTests(unittest.TestCase):
    def test_max_length_in_schema(self):
        sch = schema.load_schema("order")
        order = {"key": "a" * 201, "profile": "banner", "prompt": "p" * 4001}
        errs = sorted((e.path, e.code) for e in schema.validate(order, sch))
        self.assertEqual(errs, [("/key", "maxLength"), ("/prompt", "maxLength")])
        order.update(key="a" * 200, prompt="p" * 4000)
        self.assertEqual(schema.validate(order, sch), [])
