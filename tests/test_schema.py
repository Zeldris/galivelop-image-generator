import unittest

from gimg import schema as S


def codes(instance, sch):
    return [(e.path, e.code) for e in S.validate(instance, sch)]


class TypeTests(unittest.TestCase):
    def test_accepts_each_type(self):
        cases = {"object": {}, "array": [], "string": "a", "integer": 3,
                 "number": 1.5, "boolean": True, "null": None}
        for name, value in cases.items():
            self.assertEqual(codes(value, {"type": name}), [], name)

    def test_rejects_wrong_type(self):
        self.assertEqual(codes("a", {"type": "integer"}), [("", "type")])

    def test_bool_is_not_integer_or_number(self):
        self.assertEqual(codes(True, {"type": "integer"}), [("", "type")])
        self.assertEqual(codes(False, {"type": "number"}), [("", "type")])

    def test_whole_float_is_integer(self):
        self.assertEqual(codes(1280.0, {"type": "integer"}), [])
        self.assertEqual(codes(1.5, {"type": "integer"}), [("", "type")])

    def test_non_finite_is_not_a_number(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            for name in ("number", "integer"):
                self.assertEqual(codes(value, {"type": name}), [("", "type")], (value, name))

    def test_int_is_number(self):
        self.assertEqual(codes(1, {"type": "number"}), [])


class KeywordTests(unittest.TestCase):
    def test_required(self):
        sch = {"type": "object", "required": ["a"]}
        self.assertEqual(codes({"a": 1}, sch), [])
        errs = S.validate({}, sch)
        self.assertEqual([(e.path, e.code, e.params["name"]) for e in errs], [("", "required", "a")])

    def test_dependent_required(self):
        sch = {"type": "object", "dependentRequired": {"b": ["a", "c"]}}
        self.assertEqual(codes({}, sch), [])
        self.assertEqual(codes({"a": 1}, sch), [])
        self.assertEqual(codes({"a": 1, "b": 2, "c": 3}, sch), [])
        errs = S.validate({"b": 2, "c": 3}, sch)
        self.assertEqual([(e.path, e.code, e.params["trigger"], e.params["name"]) for e in errs],
                         [("", "dependentRequired", "b", "a")])
        self.assertEqual(S.format_error(errs[0], "en"), '/: "b" needs "a"')

    def test_dependent_required_path_of_nested_object(self):
        sch = {"properties": {"o": {"dependentRequired": {"x": ["y"]}}}}
        self.assertEqual(codes({"o": {"x": 1}}, sch), [("/o", "dependentRequired")])

    def test_dependent_required_shape_is_checked(self):
        with self.assertRaises(S.SchemaError):
            S.check_schema({"dependentRequired": {"x": "y"}})

    def test_properties_nested_path(self):
        sch = {"properties": {"a": {"properties": {"b": {"type": "string"}}}}}
        self.assertEqual(codes({"a": {"b": "x"}}, sch), [])
        self.assertEqual(codes({"a": {"b": 1}}, sch), [("/a/b", "type")])

    def test_additional_properties_false(self):
        sch = {"properties": {"a": {}}, "additionalProperties": False}
        self.assertEqual(codes({"a": 1}, sch), [])
        self.assertEqual(codes({"a": 1, "z": 2}, sch), [("/z", "additionalProperties")])

    def test_additional_properties_schema(self):
        sch = {"additionalProperties": {"type": "integer"}}
        self.assertEqual(codes({"x": 1}, sch), [])
        self.assertEqual(codes({"x": "s"}, sch), [("/x", "type")])

    def test_property_names(self):
        sch = {"propertyNames": {"pattern": "^[a-z]+$"}}
        self.assertEqual(codes({"abc": 1}, sch), [])
        self.assertEqual(codes({"AB": 1}, sch), [("/AB", "propertyNames")])

    def test_min_properties(self):
        sch = {"minProperties": 1}
        self.assertEqual(codes({"a": 1}, sch), [])
        self.assertEqual(codes({}, sch), [("", "minProperties")])

    def test_items_and_array_limits(self):
        sch = {"items": {"type": "integer"}, "minItems": 1, "maxItems": 2}
        self.assertEqual(codes([1, 2], sch), [])
        self.assertEqual(codes([], sch), [("", "minItems")])
        self.assertEqual(codes([1, 2, 3], sch), [("", "maxItems")])
        self.assertEqual(codes([1, "x"], sch), [("/1", "type")])

    def test_enum(self):
        sch = {"enum": ["a", "b"]}
        self.assertEqual(codes("a", sch), [])
        self.assertEqual(codes("c", sch), [("", "enum")])

    def test_enum_and_const_do_not_equate_bool_and_number(self):
        self.assertEqual(codes(True, {"enum": [1]}), [("", "enum")])
        self.assertEqual(codes(0, {"enum": [False]}), [("", "enum")])
        self.assertEqual(codes(1, {"enum": [1.0]}), [])
        self.assertEqual(codes(True, {"const": 1}), [("", "const")])
        self.assertEqual(codes([True], {"const": [1]}), [("", "const")])
        self.assertEqual(codes({"a": [1]}, {"const": {"a": [1.0]}}), [])
        self.assertEqual(codes({"a": False}, {"enum": [{"a": 0}]}), [("", "enum")])

    def test_false_schema(self):
        self.assertEqual(codes(1, {"properties": {"a": False}, "required": []}), [])
        self.assertEqual(codes({"a": 1}, {"properties": {"a": False}}), [("/a", "false")])
        err = S.validate({"a": 1}, {"properties": {"a": False}})[0]
        self.assertIn("/a", S.format_error(err, "en"))

    def test_unlisted_code_is_an_internal_error(self):
        with self.assertRaises(AssertionError):
            S._error("", "bogus", {})

    def test_pattern_dollar_is_ecma_end_of_input(self):
        sch = {"pattern": "^[a-z]+$"}
        self.assertEqual(codes("abc", sch), [])
        self.assertEqual(codes("abc\n", sch), [("", "pattern")])
        self.assertEqual(codes("a$", {"pattern": "^a[$]$"}), [])
        self.assertEqual(codes("a$", {"pattern": "^a\\$$"}), [])

    def test_pattern_digit_is_ascii(self):
        self.assertEqual(codes("\u0661", {"pattern": "^\\d$"}), [("", "pattern")])
        self.assertEqual(codes("1", {"pattern": "^\\d$"}), [])

    def test_const(self):
        self.assertEqual(codes(1, {"const": 1}), [])
        self.assertEqual(codes(2, {"const": 1}), [("", "const")])

    def test_pattern_uses_search(self):
        self.assertEqual(codes("xxabxx", {"pattern": "ab"}), [])
        self.assertEqual(codes("xx", {"pattern": "ab"}), [("", "pattern")])

    def test_string_length(self):
        sch = {"minLength": 2, "maxLength": 3}
        self.assertEqual(codes("ab", sch), [])
        self.assertEqual(codes("a", sch), [("", "minLength")])
        self.assertEqual(codes("abcd", sch), [("", "maxLength")])

    def test_number_bounds(self):
        sch = {"minimum": 1, "maximum": 3}
        self.assertEqual(codes(2, sch), [])
        self.assertEqual(codes(0, sch), [("", "minimum")])
        self.assertEqual(codes(4, sch), [("", "maximum")])

    def test_ref(self):
        sch = {"properties": {"a": {"$ref": "#/$defs/n"}},
               "$defs": {"n": {"type": "integer", "minimum": 5}}}
        self.assertEqual(codes({"a": 5}, sch), [])
        self.assertEqual(codes({"a": 1}, sch), [("/a", "minimum")])

    def test_path_escapes_pointer_chars(self):
        sch = {"additionalProperties": {"type": "integer"}}
        self.assertEqual(codes({"a/b": "x"}, sch), [("/a~1b", "type")])

    def test_many_errors_at_once(self):
        sch = {"required": ["r"], "properties": {"a": {"type": "integer"}, "b": {"minimum": 3}},
               "additionalProperties": False}
        got = sorted(codes({"a": "x", "b": 1, "z": 0}, sch))
        self.assertEqual(got, sorted([("", "required"), ("/a", "type"),
                                      ("/b", "minimum"), ("/z", "additionalProperties")]))


class SchemaCheckTests(unittest.TestCase):
    def test_unknown_keyword_rejected(self):
        with self.assertRaises(S.SchemaError) as cm:
            S.check_schema({"properties": {"a": {"oneOf": []}}})
        self.assertIn("oneOf", str(cm.exception))

    def test_annotations_allowed(self):
        S.check_schema({"title": "t", "description": "d", "default": 1, "$comment": "c",
                        "properties": {"title": {"type": "string"}}})

    def test_remote_ref_rejected(self):
        with self.assertRaises(S.SchemaError) as cm:
            S.check_schema({"$ref": "http://x/y"})
        self.assertIn("local", str(cm.exception))

    def test_unresolved_ref(self):
        with self.assertRaises(S.SchemaError) as cm:
            S.validate(1, {"$ref": "#/$defs/missing"})
        self.assertIn("unresolved", str(cm.exception))

    def test_invalid_pattern_rejected(self):
        with self.assertRaises(S.SchemaError) as cm:
            S.check_schema({"properties": {"a": {"pattern": "("}}})
        self.assertIn("pattern", str(cm.exception))

    def test_unresolved_ref_rejected_at_load(self):
        for sch in ({"$ref": "#/$defs/missing"},
                    {"$defs": {"a": {"$ref": "#/$defs/missing"}}}):
            with self.assertRaises(S.SchemaError) as cm:
                S.check_schema(sch)
            self.assertIn("unresolved", str(cm.exception))
        S.check_schema({"$defs": {"a": {"type": "string"}}, "$ref": "#/$defs/a"})

    def test_format_error(self):
        err = S.validate({}, {"required": ["a"]})[0]
        self.assertEqual(S.format_error(err, "en"), '/: missing required property "a"')
        self.assertIn("falta la propiedad", S.format_error(err, "es"))


PROFILE = {"width": 1280, "height": 640}


def project(**profile):
    return {"minVersion": "0.1.0", "name": "proj", "delivery": {"dir": "img"},
            "profiles": {"og": dict(PROFILE, **profile)}}


class ComposeConfigTests(unittest.TestCase):
    """`compose`, `targetWidth` and `targetHeight` of a profile (F2.8, D28)."""

    def found(self, **profile):
        return sorted((e.path, e.code) for e in S.validate(project(**profile), S.load_schema("project-config")))

    def test_a_full_composition_is_valid(self):
        self.assertEqual(self.found(
            targetWidth=1200, targetHeight=630,
            compose={"template": "brand/og.svg", "logo": "brand/logo.svg", "fields": ["title", "subtitle2"],
                     "fonts": ["Sora", "Cormorant Garamond"], "fit": "contain"}), [])
        self.assertEqual(self.found(compose={"template": "og.svg"}), [])
        self.assertEqual(self.found(targetWidth=16, targetHeight=4096), [])

    def test_target_needs_both_sides(self):
        base = "/profiles/og"
        self.assertEqual(self.found(targetWidth=1200), [(base, "dependentRequired")])
        self.assertEqual(self.found(targetHeight=630), [(base, "dependentRequired")])
        errs = S.validate(project(targetHeight=630), S.load_schema("project-config"))
        self.assertEqual((errs[0].params["trigger"], errs[0].params["name"]), ("targetHeight", "targetWidth"))

    def test_target_limits_and_type(self):
        for bad, code in ((15, "minimum"), (4097, "maximum"), ("1200", "type"), (1200.5, "type"), (True, "type")):
            self.assertEqual(self.found(targetWidth=bad, targetHeight=630), [("/profiles/og/targetWidth", code)], bad)

    def test_compose_needs_a_template(self):
        self.assertEqual(self.found(compose={}), [("/profiles/og/compose", "required")])
        self.assertEqual(self.found(compose={"logo": "l.svg"}), [("/profiles/og/compose", "required")])

    def test_compose_rejects_unknown_keys_and_lut(self):
        self.assertEqual(self.found(compose={"template": "t.svg", "lut": "x.cube"}),
                         [("/profiles/og/compose/lut", "additionalProperties")])

    def test_template_and_logo_are_relative_svg_paths(self):
        for field in ("template", "logo"):
            for bad in ("t.png", "t.svg.png", "../t.svg", "/t/t.svg", "~/t.svg", "a/../t.svg", "t\\x.svg", "t\n.svg",
                        "t\x00.svg", "", "t.svg\n", "svg"):
                cfg = {"template": "t.svg"}
                cfg[field] = bad
                errors = self.found(compose=cfg)
                self.assertTrue(errors, (field, bad))
                self.assertTrue(all(p == "/profiles/og/compose/" + field for p, _ in errors), (field, bad, errors))
            self.assertEqual(self.found(compose={"template": "t.svg", field: "a/b/c.svg"}), [])

    def test_fit_is_cover_or_contain(self):
        self.assertEqual(self.found(compose={"template": "t.svg", "fit": "stretch"}),
                         [("/profiles/og/compose/fit", "enum")])
        self.assertEqual(self.found(compose={"template": "t.svg", "fit": "cover"}), [])

    def test_field_names(self):
        base = "/profiles/og/compose/fields/0"
        for bad in ("logo", "Title", "1a", "a-b", "a_b", "a b", "", "x" * 41, "título", "a\n"):
            self.assertTrue([e for e in self.found(compose={"template": "t.svg", "fields": [bad]}) if e[0] == base],
                            bad)
        for good in ("title", "title2", "subTitle", "x" * 40, "logos", "logo2"):
            self.assertEqual(self.found(compose={"template": "t.svg", "fields": [good]}), [], good)

    def test_logo_is_reserved_with_the_reason_a_pattern(self):
        self.assertEqual(self.found(compose={"template": "t.svg", "fields": ["logo"]}),
                         [("/profiles/og/compose/fields/0", "pattern")])

    def test_at_most_ten_fields_and_ten_fonts(self):
        names = ["f%d" % i for i in range(11)]
        self.assertEqual(self.found(compose={"template": "t.svg", "fields": names}),
                         [("/profiles/og/compose/fields", "maxItems")])
        self.assertEqual(self.found(compose={"template": "t.svg", "fields": names[:10]}), [])
        self.assertEqual(self.found(compose={"template": "t.svg", "fonts": names}),
                         [("/profiles/og/compose/fonts", "maxItems")])

    def test_fonts_are_short_strings_without_controls(self):
        base = "/profiles/og/compose/fonts/0"
        self.assertEqual(self.found(compose={"template": "t.svg", "fonts": [""]}), [(base, "minLength")])
        self.assertEqual(self.found(compose={"template": "t.svg", "fonts": ["x" * 101]}), [(base, "maxLength")])
        self.assertEqual(self.found(compose={"template": "t.svg", "fonts": ["So\nra"]}), [(base, "pattern")])
        self.assertEqual(self.found(compose={"template": "t.svg", "fonts": [3]}), [(base, "type")])


class OrderTextTests(unittest.TestCase):
    ORDER = {"key": "a", "profile": "og", "prompt": "x"}

    def found(self, text):
        return sorted((e.path, e.code) for e in S.validate(dict(self.ORDER, text=text), S.load_schema("order")))

    def test_text_by_field_name(self):
        self.assertEqual(self.found({"title": "Hola", "subtitle": "x" * 200, "t2": ""}), [])
        self.assertEqual(S.validate(self.ORDER, S.load_schema("order")), [])

    def test_text_longer_than_200(self):
        self.assertEqual(self.found({"title": "x" * 201}), [("/text/title", "maxLength")])

    def test_text_with_control_characters(self):
        for bad in ("a\nb", "a\x00b", "a\tb", "a\x7fb", "a\x1fb"):
            self.assertEqual(self.found({"title": bad}), [("/text/title", "pattern")], repr(bad))
        self.assertEqual(self.found({"title": "ñ é \u2028 猫 <&>"}), [])  # printable and markup are the template's business

    def test_text_values_are_strings(self):
        self.assertEqual(self.found({"title": 3}), [("/text/title", "type")])
        self.assertEqual(self.found({"title": None}), [("/text/title", "type")])

    def test_text_is_an_object(self):
        self.assertEqual(self.found(["a"]), [("/text", "type")])
        self.assertEqual(self.found("a"), [("/text", "type")])

    def test_text_keys_are_field_names_and_logo_is_reserved(self):
        for bad in ("logo", "Title", "a-b", "1a", "", "x" * 41, "a\nb"):
            self.assertEqual(self.found({bad: "v"}), [("/text/" + bad, "propertyNames")], repr(bad))
        self.assertEqual(S.validate(dict(self.ORDER, text={"logo": "v"}), S.load_schema("order"))[0].params["name"], "logo")


if __name__ == "__main__":
    unittest.main()
