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


if __name__ == "__main__":
    unittest.main()
