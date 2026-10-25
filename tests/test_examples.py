import copy
import json
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

    def test_order_bad_references(self):
        for ref in ("/etc/passwd", "../x.png", "a/../../x.png", "~/x", "a\\b.png", ""):
            got = self.errs(self.order_with(references=[ref]), self.order_schema)
            self.assertEqual(got[0][0], "/references/0", ref)
            self.assertIn(got[0][1], ("pattern", "minLength"), ref)

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
