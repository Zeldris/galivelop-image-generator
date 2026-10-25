import json
import os
import string
import unittest
from pathlib import Path
from unittest import mock

from gimg import i18n, schema as S

LOCALES = Path(__file__).resolve().parent.parent / "gimg" / "locales"


def load(lang):
    with open(LOCALES / (lang + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def placeholders(text):
    return {f for _, f, _, _ in string.Formatter().parse(text) if f}


def raised_codes():
    """Literal error codes raised in gimg/: first argument of GimgError/PathError/make_error and `code` defaults."""
    import ast
    found = set()
    for path in sorted((LOCALES.parent).glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "id", getattr(node.func, "attr", ""))
                if name in ("GimgError", "PathError", "make_error") and node.args \
                        and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    found.add(node.args[0].value)
            elif isinstance(node, ast.FunctionDef):
                args = node.args.args
                for arg, default in zip(args[len(args) - len(node.args.defaults):], node.args.defaults):
                    if arg.arg == "code" and isinstance(default, ast.Constant) and isinstance(default.value, str):
                        found.add(default.value)
    return found


class LocaleTests(unittest.TestCase):
    def test_every_raised_error_code_has_text(self):
        codes = raised_codes()
        self.assertIn("delivery.reserved", codes)  # the scan itself works
        self.assertIn("project.bad_name", codes)
        for lang in ("es", "en"):
            missing = sorted(c for c in codes if "error." + c not in load(lang))
            self.assertEqual(missing, [], lang)

    def test_same_keys_and_placeholders(self):
        es, en = load("es"), load("en")
        self.assertEqual(set(es), set(en))
        for key in es:
            self.assertEqual(placeholders(es[key]), placeholders(en[key]), key)

    def test_every_validator_code_has_text(self):
        for lang in ("es", "en"):
            data = load(lang)
            for code in S.CODES:
                self.assertIn("schema." + code, data, (lang, code))

    def test_codes_have_same_placeholders_in_both_languages(self):
        es, en = load("es"), load("en")
        for code in S.CODES:
            key = "schema." + code
            self.assertEqual(placeholders(es[key]), placeholders(en[key]), key)

    def test_all_messages_render(self):
        params = {"path": "/p", "name": "n", "expected": "e", "allowed": "a",
                  "pattern": "p", "limit": 1}
        for lang in ("es", "en"):
            for code in S.CODES:
                text = i18n.t("schema." + code, lang, **params)
                self.assertIn("/p", text)


class FallbackTests(unittest.TestCase):
    def test_language_texts(self):
        self.assertIn("falta", i18n.t("schema.required", "es", path="/", name="x"))
        self.assertIn("missing", i18n.t("schema.required", "en", path="/", name="x"))

    def test_unknown_language_falls_back_to_en(self):
        self.assertIn("missing", i18n.t("schema.required", "xx", path="/", name="x"))

    def test_unknown_key_returns_key(self):
        self.assertEqual(i18n.t("no.such.key", "es"), "no.such.key")

    def test_key_missing_in_lang_falls_back_to_en(self):
        with mock.patch.dict(i18n._cache, {"es": {}, "en": {"k": "english {a}"}}):
            self.assertEqual(i18n.t("k", "es", a=1), "english 1")


class DefaultLangTests(unittest.TestCase):
    def check(self, env, expected):
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(i18n.default_lang(), expected)

    def test_explicit_wins(self):
        self.check({"GIMG_LANG": "en", "LANG": "es_ES.UTF-8"}, "en")
        self.check({"GIMG_LANG": "es", "LANG": "en_US.UTF-8"}, "es")

    def test_from_lang(self):
        self.check({"LANG": "es_ES.UTF-8"}, "es")
        self.check({"LANG": "en_US.UTF-8"}, "en")

    def test_lc_all_precedes_lang(self):
        self.check({"LC_ALL": "es_ES.UTF-8", "LANG": "en_US.UTF-8"}, "es")
        self.check({"LC_ALL": "en_US.UTF-8", "LANG": "es_ES.UTF-8"}, "en")

    def test_full_precedence_order(self):
        env = {"GIMG_LANG": "en", "LC_ALL": "es", "LC_MESSAGES": "es", "LANG": "es"}
        self.check(env, "en")
        del env["GIMG_LANG"]
        self.check(env, "es")
        self.check({"LC_ALL": "en_US", "LC_MESSAGES": "es_ES", "LANG": "es_ES"}, "en")
        self.check({"LC_MESSAGES": "es_ES", "LANG": "en_US"}, "es")
        self.check({"LC_MESSAGES": "en_US", "LANG": "es_ES"}, "en")
        self.check({"LC_ALL": "", "LC_MESSAGES": "", "LANG": "es_ES"}, "es")

    def test_default_en(self):
        self.check({}, "en")


if __name__ == "__main__":
    unittest.main()
