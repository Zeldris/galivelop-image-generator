"""F4c.2 (D40): the three sources of templates, saving the template of an attempt as a new one (`gimg template save`
and its route) and `measure` over the base image.

The attempt comes from the fake engine; with no tools the composition fails and the attempt keeps its `composeError`,
which is what `save_template` falls back to, so nothing here needs ffmpeg."""
import json
import unittest

from gimg import compose, doctor, orders, paths
from gimg.errors import GimgError
from tests import test_elements, test_server_write
from tests.test_server_read import NAME

SVG = test_elements.SVG.replace("{{title}}", "x")


class SaveBase(test_server_write.WriteBase):
    def setUp(self):
        super().setUp()
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["profiles"]["og"]["compose"].update(templatesDir="templates", textColor="#102030")
        path.write_text(json.dumps(cfg))
        (self.root / "t.svg").write_text(SVG, encoding="utf-8")
        self.key, self.profile = self.make_order(profile="og", count=1)
        self.url = "/api/projects/%s/profiles/og/templates" % NAME
        self.data = paths.data_dir() / "projects" / NAME / "templates" / "og"

    def body(self, name="mio", dest="local"):
        return {"from": {"key": self.key, "attempt": 1}, "name": name, "dest": dest}


class SaveTests(SaveBase):
    def test_local_writes_the_svg_and_the_sidecar_in_the_data_folder_and_answers_201(self):
        resp, payload = self.send("POST", self.url, self.body())
        self.assertEqual(resp.status, 201, payload)
        got = json.loads(payload)
        self.assertEqual((got["id"], got["source"], got["default"]), ("mio", "local", False))
        self.assertEqual((self.data / "mio.svg").read_text(encoding="utf-8"), SVG)
        side = json.loads((self.data / "mio.json").read_text())
        self.assertEqual((side["base"], side["fields"], side["textColor"]), ("default", ["title"], "#102030"))
        self.assertEqual(sorted(p.name for p in self.data.iterdir()), ["mio.json", "mio.svg"])

    def test_project_writes_inside_templates_dir_and_lists_it_with_its_source(self):
        got = self.ok("POST", self.url, self.body("suyo", "project"), 201)
        self.assertEqual(got["source"], "project")
        self.assertTrue((self.root / "templates" / "og" / "suyo.svg").is_file())
        listed = {i["id"]: i["source"] for i in self.ok("GET", self.url)}
        self.assertEqual(listed, {"default": "config", "suyo": "project"})

    def test_cli_and_route_answer_the_same(self):
        via_cli = self.cli_json("template", "save", NAME, "og", self.key, "1", "uno")
        via_api = self.ok("POST", self.url, self.body("dos"), 201)
        self.assertEqual(dict(via_cli, id="x", template="x"), dict(via_api, id="x", template="x"))
        self.assertEqual(sorted(i["id"] for i in self.ok("GET", self.url)), ["default", "dos", "uno"])

    def test_the_saved_template_is_usable_by_id_and_served(self):
        self.ok("POST", self.url, self.body(), 201)
        resp, payload = self.get(self.url.replace("/templates", "/assets/template") + "?id=mio")
        self.assertEqual((resp.status, payload), (200, SVG.encode()))

    def test_it_never_overwrites_and_the_first_copy_survives(self):
        self.ok("POST", self.url, self.body(), 201)
        before = (self.data / "mio.svg").read_bytes()
        (self.root / "t.svg").write_text("<svg viewBox='0 0 1 1'/>")
        self.bad("POST", self.url, self.body(), 409, "compose.template_exists")
        self.bad("POST", self.url, self.body("default"), 400, "compose.bad_name")  # a reserved id
        self.assertEqual((self.data / "mio.svg").read_bytes(), before)

    def test_a_stray_sidecar_blocks_the_name_and_leaves_no_svg(self):
        self.data.mkdir(parents=True)
        (self.data / "mio.json").write_text("{}")
        self.bad("POST", self.url, self.body(), 409, "compose.template_exists")
        self.assertFalse((self.data / "mio.svg").exists())
        self.assertEqual((self.data / "mio.json").read_text(), "{}")

    def test_without_templates_dir_the_project_destination_is_refused(self):
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        del cfg["profiles"]["og"]["compose"]["templatesDir"]
        path.write_text(json.dumps(cfg))
        self.bad("POST", self.url, self.body(dest="project"), 400, "compose.templates_dir_missing")
        self.assertFalse((self.root / "templates").exists())

    def test_bad_names_destinations_and_bodies(self):
        for name in ("Mio", "a b", "../x", "", "x" * 60, "mio.svg"):
            self.bad("POST", self.url, self.body(name), 400, "compose.bad_name")
        self.bad("POST", self.url, self.body(dest="cloud"), 400, "compose.bad_dest")
        self.bad("POST", self.url, {"name": "mio"}, 400, "api.bad_param")
        self.bad("POST", self.url, dict(self.body(), extra=1), 400, "api.bad_param")
        self.bad("POST", self.url, dict(self.body(), name=3), 400, "api.bad_param")
        self.bad("POST", self.url, {"from": {"key": self.key, "attempt": 9}, "name": "mio"}, 404, "order.attempt_unknown")
        self.bad("POST", self.url.replace("/og/", "/zzz/"), self.body(), 404, "order.profile_unknown")
        self.assertFalse(self.data.exists())

    def test_a_symlinked_templates_dir_that_leaves_the_project_is_refused(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        (self.root / "templates").symlink_to(outside)
        resp, payload = self.send("POST", self.url, self.body(dest="project"))
        self.assertGreaterEqual(resp.status, 400, payload)
        self.assertEqual(list(outside.rglob("*")), [])


class StoredLayoutTests(SaveBase):
    def test_a_stored_layout_is_applied_to_the_copy(self):
        box = {"x": 10, "y": 20, "w": 200, "h": 40}
        from unittest import mock
        with mock.patch.object(compose, "render", lambda *a, **k: {
                "fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg", "text": {},
                "layout": k.get("layout")}):
            self.ok("POST", self.att(self.key, self.profile, 1, "/compose"), {"layout": {"title": box}})
        self.ok("POST", self.url, self.body(), 201)
        saved = (self.data / "mio.svg").read_text(encoding="utf-8")
        self.assertIn('data-gimg-box="10 20 200 40"', saved)
        self.assertIn("translate(10 20) scale(0.5 0.5) translate(-100 -200)", saved)
        self.assertEqual([e["box"] for e in compose.elements(saved, (1200, 630)) if e["id"] == "title"], [box])


class SourcesTests(SaveBase):
    def test_an_id_repeated_between_sources_keeps_the_first_and_doctor_warns(self):
        (self.root / "templates" / "og").mkdir(parents=True)
        (self.root / "templates" / "og" / "dup.svg").write_text(SVG)
        self.data.mkdir(parents=True)
        (self.data / "dup.svg").write_text("<svg viewBox='0 0 1200 630'/>")
        listed = {i["id"]: i["source"] for i in self.ok("GET", self.url)}
        self.assertEqual(listed["dup"], "project")  # config, project, local: the first one wins
        checks = [c for c in doctor._template_files() if c.id.endswith(":dup:dup")]
        self.assertEqual([(c.status, c.key) for c in checks], [("warn", "doctor.templates.duplicate")])
        self.assertEqual((checks[0].params["used"], checks[0].params["ignored"]), ("project", "local"))

    def test_doctor_warns_when_the_viewbox_is_not_the_target_or_an_element_is_malformed(self):
        (self.root / "templates" / "og").mkdir(parents=True)
        (self.root / "templates" / "og" / "small.svg").write_text(SVG.replace("0 0 1200 630", "0 0 1280 640"))
        (self.root / "templates" / "og" / "twice.svg").write_text(SVG + SVG)
        got = {c.id.rsplit(":", 2)[-2]: c.key for c in doctor._template_files() if c.id.endswith(":elements")}
        self.assertEqual(got, {"small": "doctor.templates.elements", "twice": "doctor.templates.elements"})
        text = " ".join(str(c.params["message"]) for c in doctor._template_files() if c.id.endswith(":elements"))
        self.assertIn("1200", text)

    def test_a_local_template_saved_alone_does_not_warn_in_doctor(self):
        self.ok("POST", self.url, self.body(), 201)  # lives in <data>/..., relative to its templateRoot
        warns = [c for c in doctor._template_files() if c.status == "warn"]
        self.assertEqual([(c.id, c.key) for c in warns], [])

    def test_a_clean_project_has_no_element_warnings(self):
        self.assertEqual([c for c in doctor._template_files() if c.status == "warn"], [])


class MeasureBaseTests(test_server_write.WriteBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order(profile="og", count=1)
        self.url = self.att(self.key, self.profile, 1, "/measure")

    def test_base_with_raw_is_a_bad_param_and_so_is_a_value_that_is_not_a_flag(self):
        for query in ("?base=1&raw=1", "?base=2"):
            resp, payload = self.get(self.url + query)
            self.assertEqual(resp.status, 400, payload)
            self.assertEqual(json.loads(payload)["error"]["params"]["name"], "base", query)

    @unittest.skipUnless(test_server_write.TOOLS, "hacen falta ffmpeg y rsvg-convert")
    def test_base_measures_the_raw_image_in_the_zone_of_the_delivered_one(self):
        got = self.ok("GET", self.url + "?base=1&zone=100,100,200,100&text=%23ffffff")
        self.assertEqual((got["base"], got["raw"]), (True, False))
        self.assertEqual(got["contrast"]["zone"], [100, 100, 200, 100])
        plain = self.ok("GET", self.url)
        self.assertEqual(plain["base"], False)
        resp, payload = self.get(self.url + "?base=1&zone=5000,0,5,5&text=%23ffffff")
        self.assertEqual(resp.status, 400, payload)


if __name__ == "__main__":
    unittest.main()
