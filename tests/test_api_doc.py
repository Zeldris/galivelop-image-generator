"""F3.6: every route registered in the router has its section in docs/api.md (the doc cannot fall behind)."""
import unittest
from pathlib import Path

from gimg import server

DOC = (Path(__file__).resolve().parent.parent / "docs" / "api.md").read_text(encoding="utf-8")


def real_routes():
    """The routes of the product: other tests register `/api/test/...` ones in the same router."""
    return [e for e in server.ROUTES if e.parts[:2] != ("api", "test")]


class ApiDocTests(unittest.TestCase):
    def test_every_route_is_documented(self):
        self.assertTrue(real_routes())
        for entry in real_routes():
            heading = "### %s /%s\n" % (entry.method, "/".join(entry.parts))
            with self.subTest(route=heading.strip()):
                self.assertIn(heading, DOC)

    def test_every_documented_route_exists(self):
        real = {"%s /%s" % (e.method, "/".join(e.parts)) for e in real_routes()}
        documented = {line[4:].strip() for line in DOC.splitlines() if line.startswith("### ") and "/api/" in line}
        self.assertEqual(documented, real)

    def test_every_route_has_a_curl_example(self):
        sections = DOC.split("\n### ")[1:]
        for section in sections:
            if section.startswith(("GET /", "POST /", "PUT /", "DELETE /")) and "/api/" in section.split("\n")[0]:
                with self.subTest(route=section.split("\n")[0]):
                    self.assertIn("curl ", section)
                    if section.startswith(("POST", "PUT")):
                        self.assertIn("Content-Type: application/json", section)


if __name__ == "__main__":
    unittest.main()
