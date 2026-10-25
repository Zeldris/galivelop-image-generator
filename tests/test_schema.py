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

    def test_whole_float_is_not_integer(self):
        self.assertEqual(codes(1.0, {"type": "integer"}), [("", "type")])

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

    def test_format_error(self):
        err = S.validate({}, {"required": ["a"]})[0]
        self.assertEqual(S.format_error(err, "en"), '/: missing required property "a"')
        self.assertIn("falta la propiedad", S.format_error(err, "es"))


if __name__ == "__main__":
    unittest.main()
