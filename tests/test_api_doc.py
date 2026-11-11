"""F3.6: every route registered in the router has its section in docs/api.md (the doc cannot fall behind)."""
import unittest
from pathlib import Path

from gimg import server

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
DOCS = {"es": (DOCS_DIR / "api.md").read_text(encoding="utf-8"), "en": (DOCS_DIR / "en" / "api.md").read_text(encoding="utf-8")}


def real_routes():
    """The routes of the product: other tests register `/api/test/...` ones in the same router."""
    return [e for e in server.ROUTES if e.parts[:2] != ("api", "test")]


class ApiDocTests(unittest.TestCase):
    def test_every_route_is_documented(self):
        self.assertTrue(real_routes())
        for lang, doc in DOCS.items():
            for entry in real_routes():
                heading = "### %s /%s\n" % (entry.method, "/".join(entry.parts))
                with self.subTest(lang=lang, route=heading.strip()):
                    self.assertIn(heading, doc)

    def test_every_documented_route_exists(self):
        real = {"%s /%s" % (e.method, "/".join(e.parts)) for e in real_routes()}
        for lang, doc in DOCS.items():
            documented = {line[4:].strip() for line in doc.splitlines() if line.startswith("### ") and "/api/" in line}
            with self.subTest(lang=lang):
                self.assertEqual(documented, real)

    def test_every_route_has_a_curl_example(self):
        for lang, doc in DOCS.items():
            for section in doc.split("\n### ")[1:]:
                if section.startswith(("GET /", "POST /", "PUT /")) and "/api/" in section.split("\n")[0]:
                    with self.subTest(lang=lang, route=section.split("\n")[0]):
                        self.assertIn("curl ", section)
                        if section.startswith(("POST", "PUT")):
                            self.assertIn("Content-Type: application/json", section)


if __name__ == "__main__":
    unittest.main()
