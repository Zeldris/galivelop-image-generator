"""F4e.2b: `GET /api/fonts` and `gimg fonts` answer the same, on a fake ``fc-list`` (an executable in a temporary PATH)."""
import json
import os
import unittest
from unittest import mock

from tests import test_elements
from tests.test_server_read import NAME, ReadBase

URL = "/api/fonts"


class FontsBase(ReadBase):
    def setUp(self):
        super().setUp()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        env = mock.patch.dict(os.environ, {"PATH": str(self.bin)})  # no other tool: only the fake ``fc-list``
        env.start()
        self.addCleanup(env.stop)
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        cfg["profiles"]["og"]["compose"]["fonts"] = ["Sora", "Cormorant Garamond", "Inter"]
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))

    def fc_list(self, lines, code=0, stderr=""):
        """A fake ``fc-list`` that prints `lines` (builtins only: the PATH has nothing else) and exits with `code`."""
        shown = " ".join("'%s'" % line for line in lines)
        body = "#!/bin/sh\nprintf '%%s\\n' %s\n" % shown
        if stderr:
            body += "printf '%%s\\n' '%s' >&2\n" % stderr
        body += "exit %d\n" % code
        path = self.bin / "fc-list"
        path.write_text(body)
        path.chmod(0o755)


class FontsTests(FontsBase):
    def test_api_and_cli_give_the_same_report(self):
        self.fc_list(["Sora", "inter,Inter Display", "Sora", "DejaVu Sans"])
        got = self.ok_json(URL)
        self.assertEqual(got, self.cli_json("fonts"))
        self.assertEqual(got["installed"], ["DejaVu Sans", "Inter Display", "Sora", "inter"])
        self.assertEqual((got["available"], got["reason"]), (True, None))
        self.assertEqual(got["projects"], [{"project": NAME, "profiles": [{"profile": "og", "fonts": [
            {"name": "Sora", "installed": True}, {"name": "Cormorant Garamond", "installed": False},
            {"name": "Inter", "installed": True}]}]}])  # `banner` does not compose: it is not listed

    def test_the_fonts_of_a_saved_template_join_those_of_the_profile(self):
        self.fc_list(["Sora", "Lato"])
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        cfg["profiles"]["og"]["compose"]["templatesDir"] = "templates"
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        folder = self.root / "templates" / "og"
        folder.mkdir(parents=True)
        (folder / "mio.svg").write_text(test_elements.SVG, encoding="utf-8")
        (folder / "mio.json").write_text(json.dumps({"fonts": ["Lato", "Sora", "Fraunces"]}), encoding="utf-8")
        got = self.ok_json(URL)
        self.assertEqual(got, self.cli_json("fonts"))
        fonts = got["projects"][0]["profiles"][0]["fonts"]
        self.assertEqual([(f["name"], f["installed"]) for f in fonts],
                         [("Sora", True), ("Cormorant Garamond", False), ("Inter", False), ("Lato", True),
                          ("Fraunces", False)])

    def test_without_fc_list_it_is_not_an_error_and_says_why(self):
        got = self.ok_json(URL)
        self.assertEqual(got, self.cli_json("fonts"))
        self.assertEqual((got["installed"], got["available"], got["reason"]), ([], False, "not_found"))
        self.assertEqual([f["installed"] for f in got["projects"][0]["profiles"][0]["fonts"]], [None, None, None])
        self.assertIn("fc-list", self.cli("fonts"))

    def test_a_failing_fc_list_says_its_error(self):
        self.fc_list([], code=1, stderr="Fontconfig error: no cache")
        got = self.ok_json(URL)
        self.assertEqual(got, self.cli_json("fonts"))
        self.assertEqual((got["available"], got["reason"]), (False, "Fontconfig error: no cache"))
        self.assertEqual(got["installed"], [])

    def test_the_project_filter_and_an_unknown_project(self):
        self.fc_list(["Sora"])
        self.assertEqual(self.ok_json(URL + "?project=" + NAME), self.cli_json("fonts", "--project", NAME))
        resp, payload = self.get(URL + "?project=nope")
        self.err(resp, payload, 404, "project.unknown")

    def test_a_project_that_does_not_load_does_not_take_the_report_down(self):
        self.fc_list(["Sora"])
        (self.root / "galivelop-images.json").write_text("{")
        got = self.ok_json(URL)
        self.assertEqual(got, self.cli_json("fonts"))
        self.assertEqual(got["installed"], ["Sora"])
        self.assertEqual(got["projects"][0]["project"], NAME)
        self.assertEqual(got["projects"][0]["profiles"], [])
        self.assertTrue(got["projects"][0]["error"]["code"])

    def test_text_output_lists_each_font_with_its_state(self):
        self.fc_list(["Sora"])
        text = self.cli("fonts")
        self.assertIn("Sora: instalada", text)
        self.assertIn("Inter: NO instalada", text)
        with mock.patch.dict(os.environ, {"GIMG_LANG": "en"}):
            text = self.cli("fonts")
        self.assertIn("Inter: NOT installed", text)
        self.assertIn(NAME + " / og:", text)


if __name__ == "__main__":
    unittest.main()
