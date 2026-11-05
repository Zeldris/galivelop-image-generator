"""F4e.2a (motor): `text` y `style` por elemento del layout, textos añadidos (`extraN`), ajuste de tamaño midiendo
píxeles, `missingFonts` y `fonts` de la plantilla guardada."""
import json
import unittest
from unittest import mock

from gimg import compose, doctor, png, projects
from gimg.errors import GimgError
from tests import test_doctor, test_elements, test_template_save
from tests.test_compose import CON_HERRAMIENTAS, ProjectBase, striped_png
from tests.test_elements import SVG, TARGET

TITLE = {"x": 100, "y": 200, "w": 400, "h": 80}
STYLE = {"family": "Sora", "size": 30, "weight": 700, "italic": True, "color": "#ff8800", "align": "center"}


def code_and_reason(case, call, *args, **kw):
    with case.assertRaises(GimgError) as cm:
        call(*args, **kw)
    return cm.exception.code, cm.exception.params.get("reason")


def added(**kw):
    return dict({"add": True, "x": 10, "y": 20, "w": 300, "h": 60, "text": "Hola", "style": dict(STYLE)}, **kw)


class PaintTests(unittest.TestCase):
    def test_text_replaces_the_content_escaped_with_one_tspan_per_line(self):
        out = compose.apply_layout(SVG, {"title": dict(TITLE, text="a & <b>\nsegunda")}, TARGET)
        self.assertNotIn("{{title}}", out)
        self.assertEqual(out.count("<tspan"), 2)
        self.assertIn("a &amp; &lt;b&gt;", out)
        self.assertIn("segunda", out)

    def test_the_box_is_not_scaled_when_text_or_style_travels(self):
        moved = dict(x=50, y=100, w=200, h=40)
        out = compose.apply_layout(SVG, {"title": dict(moved, text="x")}, TARGET)
        self.assertNotIn("scale(", out.split("gimg-logo")[0])
        self.assertIn('data-gimg-box="50 100 200 40"', out)
        out = compose.apply_layout(SVG, {"title": dict(moved)}, TARGET)
        self.assertIn("scale(", out)

    def test_line_height_default_and_given_and_y_is_box_y_plus_size(self):
        out = compose.apply_layout(SVG, {"title": dict(TITLE, text="a\nb", style={"size": 20})}, TARGET)
        self.assertIn('dy="24"', out)
        self.assertIn('y="220"', out)
        out = compose.apply_layout(SVG, {"title": dict(TITLE, text="a\nb", style={"size": 20, "lineHeight": 2})}, TARGET)
        self.assertIn('dy="40"', out)

    def test_align_sets_x_and_text_anchor(self):
        for align, x, anchor in (("left", 100, "start"), ("center", 300, "middle"), ("right", 500, "end")):
            out = compose.apply_layout(SVG, {"title": dict(TITLE, text="a", style={"align": align})}, TARGET)
            self.assertIn('x="%d"' % x, out)
            self.assertIn(anchor, out)

    def test_style_goes_last_in_the_style_attribute_and_colour_to_data_attribute(self):
        svg = SVG.replace('x="100" y="260">', 'x="100" y="260" style="fill:#000;font-size:10px">')
        out = compose.apply_layout(svg, {"title": dict(TITLE, text="a", style=STYLE)}, TARGET)
        style = out.split('style="')[1].split('"')[0]
        self.assertTrue(style.startswith("fill:#000;font-size:10px"))
        self.assertIn("Sora", style)
        self.assertIn("#ff8800", style.split("font-size:10px")[1])
        self.assertIn('data-gimg-color="#ff8800"', out)
        self.assertNotIn('data-gimg-color="#ffffff"', out)

    def test_sizes_override_the_requested_size(self):
        out = compose.apply_layout(SVG, {"title": dict(TITLE, text="a", style={"size": 40})}, TARGET, sizes={"title": 17})
        self.assertIn("17", out)
        self.assertNotIn("font-size:40", out.replace(" ", ""))

    def test_without_size_the_font_size_of_the_element_is_used_else_16(self):
        svg = SVG.replace('x="100" y="260">', 'x="100" y="260" font-size="50">')
        self.assertIn('y="250"', compose.apply_layout(svg, {"title": dict(TITLE, text="a")}, TARGET))
        self.assertIn('y="216"', compose.apply_layout(SVG, {"title": dict(TITLE, text="a")}, TARGET))

    def test_an_added_text_is_inserted_before_the_end_with_its_id_and_box(self):
        out = compose.apply_layout(SVG, {"extra1": added()}, TARGET)
        self.assertLess(out.index('id="gimg-extra1"'), out.rindex("</svg>"))
        self.assertIn('data-gimg-box="10 20 300 60"', out)
        self.assertIn("Hola", out)
        self.assertEqual([e["id"] for e in compose.elements(out, TARGET)][-1], "extra1")

    def test_check_layout_keeps_text_and_style_in_moved(self):
        found = compose._elements(SVG, TARGET)
        got = compose._check_layout(found, {"title": dict(TITLE, text="x", style={"size": 20})}, TARGET)
        self.assertEqual(got["title"]["text"], "x")
        self.assertEqual(got["title"]["style"], {"size": 20})


class BadLayoutTests(unittest.TestCase):
    def bad(self, layout, svg=SVG):
        code, reason = code_and_reason(self, compose.apply_layout, svg, layout, TARGET)
        self.assertEqual(code, "compose.bad_layout")
        self.assertTrue(reason)
        return reason

    def test_text_that_is_not_a_string_or_too_long(self):
        self.bad({"title": dict(TITLE, text=5)})
        self.assertIn("500", self.bad({"title": dict(TITLE, text="x" * 501)}))
        compose.apply_layout(SVG, {"title": dict(TITLE, text="x" * 500)}, TARGET)

    def test_text_and_style_only_in_text_elements(self):
        self.assertIn("text", self.bad({"logo": dict(LOGO, text="x")}))
        self.assertIn("text", self.bad({"ornament1": {"x": 0, "y": 0, "w": 5, "h": 5, "style": {"size": 9}}}))

    def test_each_style_key_is_checked(self):
        for style in ({"family": "bad;font"}, {"family": ""}, {"family": "x" * 65}, {"size": 3}, {"size": 1001},
                      {"size": 10.5}, {"size": True}, {"weight": 150}, {"weight": 1000}, {"italic": "yes"},
                      {"color": "red"}, {"color": "#fff"}, {"align": "justify"}, {"lineHeight": 0.5},
                      {"lineHeight": 3.5}, {"lineHeight": "1"}, {"bogus": 1}, "bold", ["size"]):
            with self.subTest(style=style):
                self.bad({"title": dict(TITLE, style=style)})

    def test_valid_extremes_pass(self):
        for style in ({"size": 4}, {"size": 1000}, {"weight": 100}, {"weight": 900}, {"lineHeight": 0.8},
                      {"lineHeight": 3}, {"family": "a" * 64}, {"family": "Sora Thin-2._x"}):
            compose.apply_layout(SVG, {"title": dict(TITLE, text="a", style=style)}, TARGET)

    def test_the_reason_names_the_key(self):
        self.assertIn("size", self.bad({"title": dict(TITLE, style={"size": 3})}))
        self.assertIn("color", self.bad({"title": dict(TITLE, style={"color": "red"})}))

    def test_added_texts_need_every_style_key_but_line_height(self):
        for key in ("family", "size", "weight", "italic", "color", "align"):
            style = {k: v for k, v in STYLE.items() if k != key}
            with self.subTest(missing=key):
                self.assertIn(key, self.bad({"extra1": added(style=style)}))
        compose.apply_layout(SVG, {"extra1": added(style=dict(STYLE, lineHeight=1.5))}, TARGET)

    def test_added_texts_need_text_and_a_box_and_a_valid_name(self):
        entry = added()
        del entry["text"]
        self.assertIn("text", self.bad({"extra1": entry}))
        entry = added()
        del entry["w"]
        self.bad({"extra1": entry})
        self.bad({"extra0": added()})
        self.bad({"extraX": added()})

    def test_at_most_ten_added_texts(self):
        compose.apply_layout(SVG, {"extra%d" % n: added() for n in range(1, 11)}, TARGET)
        self.assertIn("10", self.bad({"extra%d" % n: added() for n in range(1, 12)}))

    def test_an_added_id_colliding_with_a_template_id_is_refused(self):
        svg = SVG.replace('<rect id="plain"', '<rect id="gimg-extra1" data-gimg-box="0 0 5 5"/><rect id="plain"')
        self.bad({"extra1": added()}, svg)

    def test_an_unknown_name_without_add_is_still_refused(self):
        self.assertEqual(code_and_reason(self, compose.apply_layout, SVG, {"ghost": dict(TITLE, text="x")}, TARGET)[0],
                         "compose.element_unknown")


LOGO = {"x": 1000, "y": 20, "w": 160, "h": 60}


class FontsTests(unittest.TestCase):
    def fc(self, stdout="Inter\nSora,Sora Thin\n", code=0):
        return mock.patch.object(compose.subprocess, "run", return_value=mock.Mock(returncode=code, stdout=stdout))

    def test_installed_families_splits_commas_sorts_and_dedupes(self):
        with self.fc("Sora,Sora Thin\nInter\nInter\n"), mock.patch.object(compose.shutil, "which", return_value="/x/fc-list"):
            self.assertEqual(compose.installed_families(), ["Inter", "Sora", "Sora Thin"])

    def test_installed_families_is_none_when_it_fails_or_is_missing(self):
        with self.fc(code=1), mock.patch.object(compose.shutil, "which", return_value="/x/fc-list"):
            self.assertIsNone(compose.installed_families())
        with mock.patch.object(compose.shutil, "which", return_value=None):
            self.assertIsNone(compose.installed_families())
        with mock.patch.object(compose.shutil, "which", return_value="/x/fc-list"), \
                mock.patch.object(compose.subprocess, "run", side_effect=OSError("boom")):
            self.assertIsNone(compose.installed_families())

    def test_missing_fonts_lists_the_families_not_installed_case_insensitively(self):
        moved = {"title": dict(TITLE, style={"family": "sora"}), "t2": dict(TITLE, style={"family": "Nope"}),
                 "t3": dict(TITLE, hidden=True, style={"family": "Hidden"})}
        with mock.patch.object(compose, "installed_families", return_value=["Sora"]):
            self.assertEqual(compose._missing_fonts(moved), ["Nope"])
        with mock.patch.object(compose, "installed_families", return_value=None):
            self.assertEqual(compose._missing_fonts(moved), [])
        with mock.patch.object(compose, "installed_families", side_effect=AssertionError("no call")):
            self.assertEqual(compose._missing_fonts({"a": TITLE}), [])

    def test_effective_unions_the_template_fonts_after_the_profile_ones(self):
        cfg = {"template": "t.svg", "fonts": ["A"], "templates": {"x": {"template": "x.svg", "fonts": ["B", "A"]}}}
        self.assertEqual(compose.effective(cfg, "x")["fonts"], ["A", "B"])
        self.assertEqual(compose.effective(cfg, None)["fonts"], ["A"])


@CON_HERRAMIENTAS
class FitTests(ProjectBase):
    TEMPLATE = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
                '<text id="gimg-title" data-gimg-box="100 100 600 100" x="100" y="150" font-size="40" '
                'fill="#ffffff">{{title}}</text></svg>')

    def setUp(self):
        super().setUp()
        self.raw = self.work / "raw.png"
        striped_png(self.raw, 1280, 640)
        self.out = self.work / "out.png"
        self.write("t.svg", self.TEMPLATE)
        self.profile_cfg = self.profile(compose={"template": "t.svg", "fields": ["title"]})

    def render(self, layout):
        with mock.patch.object(compose, "installed_families", return_value=None):
            return compose.render(self.root, self.profile_cfg, self.raw, self.out, {"title": "x"}, layout=layout)

    def box(self, **kw):
        return dict({"x": 100, "y": 100, "w": 600, "h": 100}, **kw)

    def test_a_short_text_fits_at_the_requested_size(self):
        info = self.render({"title": self.box(text="Hola", style={"size": 40})})
        self.assertEqual(info["fitted"], {"title": 40})
        self.assertNotIn("overflow", info)
        self.assertEqual(info["layout"]["title"]["style"]["size"], 40)
        self.assertEqual(png.size(self.out), (1200, 630))

    def test_a_long_text_shrinks_and_reports_fitted_below_the_requested_size(self):
        info = self.render({"title": self.box(text="palabra " * 12, style={"size": 60})})
        self.assertLess(info["fitted"]["title"], 60)
        self.assertGreaterEqual(info["fitted"]["title"], 30)
        self.assertEqual(info["layout"]["title"]["style"]["size"], 60)  # the layout keeps what was asked

    def test_a_text_that_does_not_fit_even_at_half_reports_overflow(self):
        info = self.render({"title": self.box(text="palabra " * 60, style={"size": 60})})
        self.assertEqual(info["overflow"], {"title": {"size": 60, "min": 30}})
        self.assertEqual(info["fitted"]["title"], 30)

    def test_a_failing_measure_does_not_fail_the_composition(self):
        with mock.patch.object(compose, "_text_extent", side_effect=GimgError("compose.tool_failed", tool="x", reason="y")):
            info = self.render({"title": self.box(text="Hola", style={"size": 40})})
        self.assertNotIn("fitted", info)
        self.assertEqual(png.size(self.out), (1200, 630))

    def test_alpha_box(self):
        data = bytearray(4 * 4 * 3)
        data[3 + 4 * (1 * 4 + 1)] = 255
        data[3 + 4 * (2 * 4 + 2)] = 9
        self.assertEqual(compose._alpha_box(bytes(data), 4, 3), (1, 1, 3, 3))
        self.assertIsNone(compose._alpha_box(bytes(48), 4, 3))

    def test_missing_fonts_goes_to_info(self):
        with mock.patch.object(compose, "installed_families", return_value=["Inter"]):
            info = compose.render(self.root, self.profile_cfg, self.raw, self.out, {"title": "x"},
                                  layout={"title": self.box(text="Hola", style={"family": "Nope", "size": 40})})
        self.assertEqual(info["missingFonts"], ["Nope"])

    def test_an_added_text_is_painted_and_measured(self):
        info = self.render({"extra1": added(x=100, y=300, w=500, h=80, text="Hola")})
        self.assertEqual(info["fitted"], {"extra1": 30})
        self.assertEqual(png.size(self.out), (1200, 630))


class SaveTemplateTests(test_template_save.SaveBase):
    def compose_with(self, layout):
        with mock.patch.object(compose, "render", lambda *a, **k: {
                "fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg", "text": {},
                "layout": k.get("layout"), "fitted": {"title": 22}}):
            self.ok("POST", self.att(self.key, self.profile, 1, "/compose"), {"layout": layout})

    def setUp(self):
        super().setUp()
        (self.root / "t.svg").write_text(test_elements.SVG, encoding="utf-8")  # this one has the {{title}} hole

    def test_edited_text_is_saved_as_is_with_fonts_in_the_sidecar_and_added_texts_become_elements(self):
        self.compose_with({"title": dict(TITLE, text="Fijo", style={"family": "Sora", "size": 40}),
                           "extra1": added(style=dict(STYLE, family="Inter"))})
        self.ok("POST", self.url, self.body(), 201)
        saved = (self.data / "mio.svg").read_text(encoding="utf-8")
        self.assertNotIn("{{title}}", saved)
        self.assertIn("Fijo", saved)
        self.assertIn("22", saved)  # the size that was fitted
        self.assertEqual([e["id"] for e in compose.elements(saved, TARGET)][-1], "extra1")
        side = json.loads((self.data / "mio.json").read_text())
        self.assertEqual(side["fonts"], ["Inter", "Sora"])
        entry = next(t for t in compose.templates_of(compose.merged_profile(projects.get(test_template_save.NAME), "og"))
                     if t["id"] == "mio")
        self.assertEqual(entry["id"], "mio")

    def test_a_text_without_text_keeps_its_hole_and_no_fonts_are_written(self):
        self.compose_with({"title": dict(TITLE, x=10)})
        self.ok("POST", self.url, self.body(), 201)
        self.assertIn("{{title}}", (self.data / "mio.svg").read_text(encoding="utf-8"))
        self.assertNotIn("fonts", json.loads((self.data / "mio.json").read_text()))

    def test_sidecar_reads_only_a_valid_fonts_list(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.json"
            for fonts, want in ((["A", "B c"], ["A", "B c"]), ("A", None), (["bad;x"], None), ([1], None),
                                (["f%d" % n for n in range(21)], None)):
                path.write_text(json.dumps({"fonts": fonts}))
                self.assertEqual(compose._sidecar(path).get("fonts"), want, fonts)


class DoctorFontsTests(test_doctor.FontsTests):
    def test_the_fonts_of_a_template_sidecar_are_checked_too(self):
        self.fc_list(["Inter"])
        root = self.project("p", {"og": None})
        cfg = json.loads((root / "galivelop-images.json").read_text())
        cfg["profiles"]["og"]["compose"] = {"template": "t.svg", "templatesDir": "templates"}
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        folder = root / "templates" / "og"
        folder.mkdir(parents=True)
        (folder / "mio.svg").write_text(SVG, encoding="utf-8")
        (folder / "mio.json").write_text(json.dumps({"fonts": ["Sora"]}), encoding="utf-8")
        check = self.fonts()["font:Sora"]
        self.assertEqual((check.status, check.key), (doctor.WARN, "doctor.fonts.missing"))


del test_doctor.FontsTests  # only the new test of the subclass runs here, not the inherited ones

if __name__ == "__main__":
    unittest.main()
