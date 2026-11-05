"""F4b.2 (D39): the API routes of the templates of a profile answer what the CLI answers, with the codes of the table.

The server and the CLI share `compose.templates_of`; what composes for real is in `tests/test_templates.py`."""
import json
import unittest

from gimg import orders, queue
from tests import test_server_write
from tests.test_server_read import NAME

ALT = "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630' id='alt'/>"


class TemplateApiBase(test_server_write.WriteBase):
    def setUp(self):
        super().setUp()
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["profiles"]["og"]["compose"]["templates"] = {
            "claro": {"template": "alt.svg", "fields": ["title"], "zone": {"x": 1, "y": 2, "w": 30, "h": 40},
                      "textColor": "#102030"}}
        path.write_text(json.dumps(cfg))
        (self.root / "alt.svg").write_text(ALT)

    def templates_url(self, profile="og"):
        return "/api/projects/%s/profiles/%s/templates" % (NAME, profile)

    def asset_url(self, kind="template", query=""):
        return "/api/projects/%s/profiles/og/assets/%s%s" % (NAME, kind, query)


class TemplatesRouteTests(TemplateApiBase):
    def test_the_list_is_the_one_of_the_cli(self):
        got = self.ok_json(self.templates_url())
        self.assertEqual(got, self.cli_json("templates", NAME, "og"))
        self.assertEqual([(i["id"], i["default"]) for i in got], [("default", True), ("claro", False)])
        self.assertEqual(got[1], {"id": "claro", "template": "alt.svg", "logo": "logo.svg", "fields": ["title"],
                                  "zone": {"x": 1, "y": 2, "w": 30, "h": 40}, "textColor": "#102030",
                                  "default": False})
        self.assertNotIn("zone", got[0])

    def test_a_profile_without_compose_has_an_empty_list_and_an_unknown_one_is_404(self):
        self.assertEqual(self.ok_json(self.templates_url("banner")), [])
        resp, payload = self.get(self.templates_url("zzz"))
        self.err(resp, payload, 404, "order.profile_unknown")


class AssetIdTests(TemplateApiBase):
    def test_id_serves_that_template_and_no_id_the_default(self):
        resp, payload = self.get(self.asset_url("template", "?id=claro"))
        self.assertEqual((resp.status, payload), (200, ALT.encode()))
        self.assertEqual(resp.getheader("Content-Security-Policy"),
                         "sandbox; default-src 'none'; style-src 'unsafe-inline'")
        for query in ("", "?id=default"):
            resp, payload = self.get(self.asset_url("template", query))
            self.assertEqual(payload, (self.root / "t.svg").read_bytes(), query)

    def test_the_logo_is_inherited_by_a_template_without_one(self):
        resp, payload = self.get(self.asset_url("logo", "?id=claro"))
        self.assertEqual((resp.status, payload), (200, (self.root / "logo.svg").read_bytes()))

    def test_an_unknown_id_is_a_400_with_the_code(self):
        resp, payload = self.get(self.asset_url("template", "?id=nope"))
        body = self.err(resp, payload, 400, "compose.template_unknown")
        self.assertIn("nope", json.dumps(body))
        resp, payload = self.get("/api/projects/%s/profiles/banner/assets/template?id=claro" % NAME)
        self.err(resp, payload, 400, "compose.template_unknown")


class ChooseTemplateTests(TemplateApiBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order(profile="og", count=1)

    def test_compose_with_an_unknown_template_is_a_400_and_changes_nothing(self):
        before = orders.get(NAME, self.key, self.profile)
        self.bad("POST", self.att(self.key, self.profile, 1, "/compose"), {"template": "nope"}, 400,
                 "compose.template_unknown")
        self.assertEqual(orders.get(NAME, self.key, self.profile), before)

    def test_compose_takes_a_string_template_only(self):
        self.bad("POST", self.att(self.key, self.profile, 1, "/compose"), {"template": 3}, 400, "api.bad_param")
        self.bad("POST", self.att(self.key, self.profile, 1, "/compose"), {"template": ["a"]}, 400, "api.bad_param")

    def test_attempts_with_a_template_queue_it_and_an_unknown_one_queues_nothing(self):
        before = len(queue.list_entries())
        self.bad("POST", self.order_url(self.key, self.profile, "/attempts"), {"count": 2, "template": "nope"}, 400,
                 "compose.template_unknown")
        self.bad("POST", self.order_url(self.key, self.profile, "/attempts"), {"template": 5}, 400, "api.bad_param")
        self.assertEqual(len(queue.list_entries()), before)
        got = self.ok("POST", self.order_url(self.key, self.profile, "/attempts"), {"count": 2, "template": "claro"},
                      202)
        self.assertEqual([e["template"] for e in got["entries"]], ["claro", "claro"])
        plain = self.ok("POST", self.order_url(self.key, self.profile, "/attempts"), {}, 202)
        self.assertEqual([e["template"] for e in plain["entries"]], [None])

    @unittest.skipUnless(test_server_write.TOOLS, "hacen falta ffmpeg y rsvg-convert")
    def test_compose_with_a_template_keeps_it_like_the_cli(self):
        got = self.ok("POST", self.att(self.key, self.profile, 1, "/compose"), {"template": "claro"})
        self.assertEqual(got["compose"]["templateId"], "claro")
        cli = self.cli_json("compose", NAME, self.key, self.profile, "1", "--template", "claro")
        self.assertEqual(cli["compose"], got["compose"])
        again = self.ok("POST", self.att(self.key, self.profile, 1, "/compose"), {})
        self.assertEqual(again["compose"]["templateId"], "claro")


if __name__ == "__main__":
    unittest.main()
