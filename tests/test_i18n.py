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


class LocaleTests(unittest.TestCase):
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

    def test_every_emitted_code_is_listed(self):
        import inspect
        src = inspect.getsource(S)
        for code in set(__import__("re").findall(r'add\("(\w+)"|ValidationError\([^"]*"(\w+)"', src)):
            for c in code:
                if c:
                    self.assertIn(c, S.CODES)

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

    def test_default_en(self):
        self.check({}, "en")


if __name__ == "__main__":
    unittest.main()
