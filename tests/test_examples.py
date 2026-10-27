import copy
import json
import re
import unittest
from pathlib import Path

from gimg import schema as S

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    with open(ROOT / rel, encoding="utf-8") as fh:
        return json.load(fh)


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_schema = S.load_schema("project-config")
        cls.order_schema = S.load_schema("order")
        cls.machine_schema = S.load_schema("machine-profile")
        cls.project = read("examples/galivelop-images.json")
        cls.order = read("examples/order.json")

    def errs(self, instance, sch):
        return sorted((e.path, e.code) for e in S.validate(instance, sch))

    def order_with(self, **changes):
        order = copy.deepcopy(self.order)
        order.update(changes)
        return order

    def test_examples_valid(self):
        self.assertEqual(S.validate(self.project, self.project_schema), [])
        self.assertEqual(S.validate(self.order, self.order_schema), [])
        steam = read("gimg/machine_profiles/steam-deck.json")
        self.assertEqual(S.validate(steam, self.machine_schema), [])

    def test_order_bad_keys(self):
        for key in ("a/../b", "../x", "/abs", "A", "a//b", "a/"):
            self.assertEqual(self.errs(self.order_with(key=key), self.order_schema),
                             [("/key", "pattern")], key)

    def test_order_key_rejects_trailing_newline(self):
        self.assertEqual(self.errs(self.order_with(key="fauna/x\n"), self.order_schema),
                         [("/key", "pattern")])

    def test_order_profile_rejects_hyphen_and_newline(self):
        for name in ("banner-thumb", "banner\n", "1x", "Banner"):
            self.assertEqual(self.errs(self.order_with(profile=name), self.order_schema),
                             [("/profile", "pattern")], name)

    def test_order_bad_references(self):
        for ref in ("/etc/passwd", "../x.png", "a/../../x.png", "~/x", "a\\b.png",
                    "a\n/../../etc/passwd", "a\x00b", "a\x7f"):
            self.assertEqual(self.errs(self.order_with(references=[ref]), self.order_schema),
                             [("/references/0", "pattern")], repr(ref))
        self.assertEqual(self.errs(self.order_with(references=[""]), self.order_schema),
                         [("/references/0", "minLength"), ("/references/0", "pattern")])

    def test_order_good_reference_with_dots_in_name(self):
        order = self.order_with(references=["refs/a..b.png"])
        self.assertEqual(S.validate(order, self.order_schema), [])

    def test_order_count_zero(self):
        self.assertEqual(self.errs(self.order_with(count=0), self.order_schema),
                         [("/count", "minimum")])

    def test_order_unknown_property(self):
        self.assertEqual(self.errs(self.order_with(extra=1), self.order_schema),
                         [("/extra", "additionalProperties")])

    def test_project_profile_without_width(self):
        proj = copy.deepcopy(self.project)
        del proj["profiles"]["banner"]["width"]
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/banner", "required")])

    def test_project_unknown_property(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["banner"]["colour"] = "red"
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/banner/colour", "additionalProperties")])

    def test_project_template_without_png(self):
        proj = copy.deepcopy(self.project)
        proj["delivery"]["template"] = "{key}-{profile}.jpg"
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/delivery/template", "pattern")])

    def test_project_template_rules(self):
        bad = ("/etc/x.png", "../{key}-{profile}.png", "fixed.png", "{key}.png",
               "{foo}-{key}-{profile}.png", "~/{key}-{profile}.png", "a/../{key}-{profile}.png",
               "{key}-{profile}.png\n", "{key} {profile}.png", "{key}-{profile}.png/")
        for tpl in bad:
            proj = copy.deepcopy(self.project)
            proj["delivery"]["template"] = tpl
            self.assertEqual(self.errs(proj, self.project_schema),
                             [("/delivery/template", "pattern")], repr(tpl))
        for tpl in ("{key}-{profile}.png", "img/{profile}/{key}.png", "a..b/{key}_{profile}.png"):
            proj = copy.deepcopy(self.project)
            proj["delivery"]["template"] = tpl
            self.assertEqual(S.validate(proj, self.project_schema), [], tpl)

    def test_project_delivery_dir_newline(self):
        proj = copy.deepcopy(self.project)
        proj["delivery"]["dir"] = "a\n/../../etc"
        self.assertEqual(self.errs(proj, self.project_schema), [("/delivery/dir", "pattern")])

    def test_project_hyphenated_profile_name(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["banner-thumb"] = proj["profiles"]["banner"]
        proj["profiles"]["banner\n"] = proj["profiles"]["banner"]
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/banner\n", "propertyNames"),
                          ("/profiles/banner-thumb", "propertyNames")])

    def test_project_min_version_non_ascii_digits(self):
        proj = copy.deepcopy(self.project)
        proj["minVersion"] = "\u0661.\u0660.\u0660"
        self.assertEqual(self.errs(proj, self.project_schema), [("/minVersion", "pattern")])
        proj["minVersion"] = "1.0.0\n"
        self.assertEqual(self.errs(proj, self.project_schema), [("/minVersion", "pattern")])

    def test_order_params_non_finite(self):
        for value in (float("nan"), float("inf")):
            order = self.order_with(params={"cfg": value})
            self.assertEqual(self.errs(order, self.order_schema), [("/params/cfg", "type")])

    def test_whole_float_size_is_valid(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["banner"]["width"] = 1280.0
        self.assertEqual(S.validate(proj, self.project_schema), [])
        proj["profiles"]["banner"]["width"] = 1280.5
        self.assertEqual(self.errs(proj, self.project_schema), [("/profiles/banner/width", "type")])

    def test_shared_defs_are_identical_across_schemas(self):
        seen = {}
        for name in ("project-config", "order", "machine-profile", "models"):
            for key, definition in S.load_schema(name).get("$defs", {}).items():
                seen.setdefault(key, []).append((name, definition))
        for key in ("name", "profileName", "relativePath", "steps", "cfg", "sampler"):
            self.assertTrue(seen.get(key), key)
        for key, copies in seen.items():
            for name, definition in copies[1:]:
                self.assertEqual(definition, copies[0][1], "%s: %s vs %s" % (key, name, copies[0][0]))

    def test_readme_examples_validate(self):
        for readme in ("README.md", "README.en.md"):
            with open(ROOT / readme, encoding="utf-8") as fh:
                blocks = re.findall(r"```json\n(.*?)```", fh.read(), re.S)
            projects = orders = 0
            for block in blocks:
                data = json.loads(block)
                if "profiles" in data:
                    projects += 1
                    self.assertEqual(S.validate(data, self.project_schema), [], readme)
                if "key" in data:
                    orders += 1
                    self.assertEqual(S.validate(data, self.order_schema), [], readme)
            self.assertGreaterEqual(projects, 1, readme)
            self.assertGreaterEqual(orders, 1, readme)

    def test_project_unsafe_delivery_dir_and_manifest(self):
        proj = copy.deepcopy(self.project)
        proj["delivery"]["dir"] = "../out"
        proj["manifest"] = "/tmp/m.json"
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/delivery/dir", "pattern"), ("/manifest", "pattern")])

    def test_project_bad_profile_name_and_empty_profiles(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["Bad_Name"] = proj["profiles"]["banner"]
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/Bad_Name", "propertyNames")])
        proj["profiles"] = {}
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles", "minProperties")])

    def test_project_bad_min_version_and_size(self):
        proj = copy.deepcopy(self.project)
        proj["minVersion"] = "1.0"
        proj["profiles"]["banner"]["width"] = 63
        proj["profiles"]["banner"]["height"] = 5000
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/minVersion", "pattern"),
                          ("/profiles/banner/height", "maximum"),
                          ("/profiles/banner/width", "minimum")])

    def test_machine_profile_errors(self):
        steam = read("gimg/machine_profiles/steam-deck.json")
        steam["engine"]["paramsBackend"] = "ram"
        steam["engine"]["maxVram"] = "bad"
        del steam["timeoutS"]
        self.assertEqual(self.errs(steam, self.machine_schema),
                         [("", "required"), ("/engine/maxVram", "pattern"),
                          ("/engine/paramsBackend", "enum")])


if __name__ == "__main__":
    unittest.main()
