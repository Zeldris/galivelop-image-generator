"""F4c.1 (D39): editable elements of a template, `layout`, `zone_to_raw`, the contrast over the base image and the
layout that an attempt keeps (`recompose`, `composeError.layout`, `--layout`).

The pure parts need no tool; what composes for real is ``skipUnless`` ffmpeg and rsvg-convert."""
import json
import unittest
from unittest import mock

from gimg import compose, orders
from gimg.errors import GimgError
from tests import test_cli, test_compose, test_compose_worker, test_recompose

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
       '<!-- <g id="gimg-ghost" data-gimg-box="0 0 1 1"/> -->'
       '<text id="gimg-title" data-gimg-box="100 200 400 80" data-gimg-color="#ffffff" x="100" y="260">{{title}}</text>'
       "<g id='gimg-logo' data-gimg-box='1000 20 160 60' transform='rotate(0)'><rect width='10' height='10'/></g>"
       '<rect id="gimg-ornament1" data-gimg-box="0 600 1200 30"/>'
       '<rect id="plain" width="5" height="5"/></svg>')
TARGET = (1200, 630)


def code_of(call, *args):
    with unittest.TestCase().assertRaises(GimgError) as cm:
        call(*args)
    return cm.exception.code


class ElementsTests(unittest.TestCase):
    def test_reads_kind_box_and_colour_in_document_order_skipping_comments(self):
        got = compose.elements(SVG, TARGET)
        self.assertEqual([(e["id"], e["kind"]) for e in got],
                         [("title", "text"), ("logo", "logo"), ("ornament1", "ornament")])
        self.assertEqual(got[0], {"id": "title", "kind": "text", "box": {"x": 100, "y": 200, "w": 400, "h": 80},
                                  "color": "#ffffff"})
        self.assertEqual(got[1]["box"], {"x": 1000, "y": 20, "w": 160, "h": 60})

    def test_a_viewbox_that_is_not_the_target_leaves_no_elements(self):
        self.assertEqual(compose.elements(SVG, (1280, 640)), [])
        self.assertEqual(compose.elements(SVG.replace('viewBox="0 0 1200 630"', ""), TARGET), [])
        self.assertEqual(len(compose.elements(SVG)), 3)  # without a target the viewBox is not asked for
        self.assertEqual(compose.elements('<svg viewBox="0 0 1200 630"/>', TARGET), [])

    def test_a_repeated_id_or_a_bad_box_is_bad_element_and_says_which(self):
        for svg, reason in ((SVG + SVG.replace("<svg", "<g"), "repeated"),
                            (SVG.replace('data-gimg-box="100 200 400 80"', 'data-gimg-box="100 200 0 80"'), "data-gimg-box"),
                            (SVG.replace('data-gimg-box="100 200 400 80"', 'data-gimg-box="a b c d"'), "data-gimg-box"),
                            (SVG.replace('data-gimg-box="100 200 400 80" ', ""), "data-gimg-box"),
                            (SVG.replace("#ffffff", "white"), "data-gimg-color"),
                            (SVG.replace("gimg-title", "gimg-Title"), "name")):
            with self.assertRaises(GimgError) as cm:
                compose.elements(svg, TARGET)
            self.assertEqual((cm.exception.code, cm.exception.params["reason"]), ("compose.bad_element", reason))


class ApplyLayoutTests(unittest.TestCase):
    def test_a_moved_element_gets_a_transform_in_front_and_a_new_box_and_nothing_else_changes(self):
        out = compose.apply_layout(SVG, {"title": {"x": 50, "y": 100, "w": 200, "h": 40}}, TARGET)
        self.assertIn('<text id="gimg-title" data-gimg-box="50 100 200 40" data-gimg-color="#ffffff" x="100" y="260"'
                      ' transform="translate(50 100) scale(0.5 0.5) translate(-100 -200)">{{title}}</text>', out)
        self.assertEqual(out.replace(out[out.index("<text"):out.index("</text>")], ""),
                         SVG.replace(SVG[SVG.index("<text"):SVG.index("</text>")], ""))

    def test_an_existing_transform_stays_behind_the_new_one_with_its_own_quotes(self):
        out = compose.apply_layout(SVG, {"logo": {"x": 0, "y": 0, "w": 160, "h": 60}}, TARGET)
        self.assertIn("transform='translate(0 0) scale(1 1) translate(-1000 -20) rotate(0)'", out)
        self.assertIn("data-gimg-box='0 0 160 60'", out)
        self.assertEqual(out.count("transform="), 1)

    def test_a_box_equal_to_the_original_and_an_empty_layout_change_nothing(self):
        self.assertEqual(compose.apply_layout(SVG, {}, TARGET), SVG)
        self.assertEqual(compose.apply_layout(SVG, {"title": {"x": 100, "y": 200, "w": 400, "h": 80}}, TARGET), SVG)

    def test_two_elements_and_a_self_closing_tag(self):
        out = compose.apply_layout(SVG, {"ornament1": {"x": 0, "y": 10, "w": 600, "h": 30},
                                         "title": {"x": 1, "y": 2, "w": 3, "h": 4}}, TARGET)
        self.assertIn('data-gimg-box="0 10 600 30" transform="translate(0 10) scale(0.5 1) translate(0 -600)"/>', out)
        self.assertIn('data-gimg-box="1 2 3 4"', out)

    def test_an_unknown_name_is_element_unknown_and_lists_the_known_ones(self):
        with self.assertRaises(GimgError) as cm:
            compose.apply_layout(SVG, {"ghost": {"x": 0, "y": 0, "w": 1, "h": 1}}, TARGET)
        self.assertEqual((cm.exception.code, cm.exception.params["allowed"]),
                         ("compose.element_unknown", "title, logo, ornament1"))
        with self.assertRaises(GimgError) as cm:  # the viewBox does not match: the template has no elements at all
            compose.apply_layout(SVG, {"title": {"x": 0, "y": 0, "w": 1, "h": 1}}, (1280, 640))
        self.assertEqual(cm.exception.code, "compose.element_unknown")

    def test_a_bad_box_is_bad_layout(self):
        for box in ({"x": 0, "y": 0, "w": 0, "h": 5}, {"x": -1, "y": 0, "w": 5, "h": 5},
                    {"x": 1100, "y": 0, "w": 101, "h": 5}, {"x": 0, "y": 626, "w": 5, "h": 5},
                    {"x": 0.5, "y": 0, "w": 5, "h": 5}, {"x": True, "y": 0, "w": 5, "h": 5},
                    {"x": 0, "y": 0, "w": 5}, {"x": 0, "y": 0, "w": 5, "h": 5, "z": 1}, "box", None):
            with self.assertRaises(GimgError) as cm:
                compose.apply_layout(SVG, {"title": box}, TARGET)
            self.assertEqual((cm.exception.code, cm.exception.params["element"]), ("compose.bad_layout", "title"), box)
        with self.assertRaises(GimgError) as cm:
            compose.apply_layout(SVG, ["title"], TARGET)
        self.assertEqual(cm.exception.code, "compose.bad_layout")


class ZoneToRawTests(unittest.TestCase):
    def cfg(self, fit):
        return {"targetWidth": 1200, "targetHeight": 630, "compose": {"template": "t.svg", "fit": fit}}

    def test_cover_is_the_inverse_of_fit_geometry(self):
        sw, sh, gx, gy = compose.fit_geometry(1280, 640, 1200, 630, "cover")
        self.assertEqual((sw, sh, gx, gy), (1260, 630, 30, 0))
        x, y, w, h = compose.zone_to_raw(self.cfg("cover"), 1280, 640, (0, 0, 1200, 630))
        self.assertEqual((y, h), (0, 640))
        self.assertLessEqual(abs(x - 30 * 1280 / 1260), 1)
        self.assertLessEqual(abs(x + w - (1230 * 1280 / 1260)), 1.5)
        inner = compose.zone_to_raw(self.cfg("cover"), 1280, 640, (630, 315, 10, 10))
        self.assertLessEqual(abs(inner[0] - (660 * 1280 / 1260)), 1)
        self.assertLessEqual(abs(inner[1] - 320), 1)

    def test_contain_is_cut_to_the_image_and_a_zone_in_the_band_is_outside(self):
        cfg = self.cfg("contain")  # 1280x640 into 1200x630 contain: 1200x600 at y=15
        self.assertEqual(compose.fit_geometry(1280, 640, 1200, 630, "contain"), (1200, 600, 0, 15))
        self.assertEqual(compose.zone_to_raw(cfg, 1280, 640, (0, 0, 1200, 630)), (0, 0, 1280, 640))
        x, y, w, h = compose.zone_to_raw(cfg, 1280, 640, (0, 115, 1200, 100))  # 100 px down inside the image
        self.assertEqual((x, w), (0, 1280))
        self.assertLessEqual(abs(y - 100 * 640 / 600), 1)
        self.assertLessEqual(abs(h - 100 * 640 / 600), 1.5)
        with self.assertRaises(GimgError) as cm:
            compose.zone_to_raw(cfg, 1280, 640, (0, 0, 1200, 10))
        self.assertEqual(cm.exception.code, "measure.zone_outside")

    def test_a_zone_beyond_the_target_is_cut_and_one_entirely_outside_fails(self):
        self.assertEqual(compose.zone_to_raw(self.cfg("cover"), 1200, 630, (1100, 600, 500, 500)), (1100, 600, 100, 30))
        with self.assertRaises(GimgError) as cm:
            compose.zone_to_raw(self.cfg("cover"), 1200, 630, (1300, 0, 5, 5))
        self.assertEqual(cm.exception.code, "measure.zone_outside")


class LayoutFakeRender(test_recompose.FakeRender):
    def __call__(self, root, cfg, raw, out, text, profile=None, prefix=None, template=None, layout=None):
        info = super().__call__(root, cfg, raw, out, text, profile, prefix)
        self.calls[-1].update(template=template, layout=layout)
        compose.effective(cfg.get("compose"), template)
        info["templateId"] = template or "default"
        if layout:
            info["layout"] = layout
        return info


TITLE = {"x": 10, "y": 20, "w": 400, "h": 80}


class RecomposeLayoutTests(test_recompose.RecomposeBase):
    def setUp(self):
        super().setUp()
        (self.root / "t.svg").write_text(SVG, encoding="utf-8")
        (self.root / "alt.svg").write_text(SVG, encoding="utf-8")
        self.profiles({"og": dict(test_compose_worker.BASE, targetWidth=1200, targetHeight=630, compose={
            "template": "t.svg", "fields": ["title"], "templates": {"alt": {"template": "alt.svg"}}})})

    def go(self, *args, **kw):
        return self.recompose(*args, render=LayoutFakeRender(), **kw)

    def test_the_layout_is_kept_by_the_attempt_and_by_the_next_composition(self):
        self.made()
        att, render = self.go(layout={"title": TITLE})
        self.assertEqual((render.calls[0]["layout"], att["compose"]["layout"]), ({"title": TITLE}, {"title": TITLE}))
        att, render = self.go(text={"title": "New"})
        self.assertEqual((render.calls[0]["layout"], att["compose"]["layout"]), ({"title": TITLE}, {"title": TITLE}))

    def test_an_empty_layout_goes_back_to_the_template(self):
        self.made()
        self.go(layout={"title": TITLE})
        att, render = self.go(layout={})
        self.assertIsNone(render.calls[0]["layout"])
        self.assertNotIn("layout", att["compose"])

    def test_a_different_template_empties_the_layout_but_the_same_one_keeps_it(self):
        self.made()
        self.go(layout={"title": TITLE})
        att, render = self.go(template="default")
        self.assertEqual(render.calls[0]["layout"], {"title": TITLE})
        att, render = self.go(template="alt")
        self.assertIsNone(render.calls[0]["layout"])
        self.assertNotIn("layout", att["compose"])
        att, render = self.go(template="default", layout={"title": TITLE})  # both given: the layout rules
        self.assertEqual(render.calls[0]["layout"], {"title": TITLE})

    def test_a_failed_composition_keeps_the_layout_in_the_error_and_the_next_one_uses_it(self):
        self.made()
        self.go(layout={"title": TITLE})
        with self.assertRaises(GimgError):
            self.recompose(render=LayoutFakeRender(fail=GimgError("compose.tool_failed", tool="ffmpeg", reason="x")))
        att = self.attempt("og")
        self.assertEqual(att["composeError"]["layout"], {"title": TITLE})
        self.assertNotIn("compose", att)
        done, render = self.go()
        self.assertEqual((render.calls[0]["layout"], done["compose"]["layout"]), ({"title": TITLE}, {"title": TITLE}))

    def test_a_layout_the_template_does_not_take_changes_nothing_and_composes_nothing(self):
        self.made(choose=1)
        before = (self.attempt("og"), self.delivered().read_bytes())
        for layout, code in (({"ghost": TITLE}, "compose.element_unknown"),
                             ({"title": dict(TITLE, w=5000)}, "compose.bad_layout")):
            render = LayoutFakeRender()
            with self.assertRaises(GimgError) as cm:
                self.recompose(layout=layout, render=render)
            self.assertEqual(cm.exception.code, code)
            self.assertEqual(render.calls, [])
        self.assertEqual((self.attempt("og"), self.delivered().read_bytes()), before)


@test_compose_worker.CON_HERRAMIENTAS
class RenderLayoutTests(test_compose_worker.ComposeWorkerBase):
    """The real tools: the layout moves what is painted and the contrast is measured under the layer."""

    def setUp(self):
        super().setUp()
        # a black block over the zone of the title; the text colour is black too: over the base (gray) the contrast
        # is that of black on gray, over the composed image it would be 1
        (self.root / "t.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
            '<rect id="gimg-title" data-gimg-box="400 200 300 100" x="400" y="200" width="300" height="100"'
            ' fill="#000000"/></svg>', encoding="utf-8")
        self.profiles({"og": dict(test_compose_worker.BASE, targetWidth=1200, targetHeight=630, compose={
            "template": "t.svg", "fields": ["title"], "textColor": "#000000"})})
        self.raw, self.out = self.root / "raw.png", self.root / "out.png"
        test_compose.striped_png(self.raw, 1280, 640)
        self.cfg = orders.projects.get("proj")["config"]["profiles"]["og"]

    def render(self, **kw):
        return compose.render(self.root, self.cfg, self.raw, self.out, {}, "og", **kw), test_compose.pixels(self.out, 1200, 630)

    def test_the_layout_moves_the_painted_element_and_is_reported(self):
        box = {"x": 800, "y": 400, "w": 300, "h": 100}
        info, at = self.render(layout={"title": box})
        self.assertEqual(info["layout"], {"title": box})
        test_compose.near(self, at(900, 450), (0, 0, 0))
        test_compose.near(self, at(450, 250), (128, 128, 128))  # the old place shows the base again

    def test_contrast_is_measured_on_the_base_image_not_on_the_composition(self):
        info, at = self.render()
        test_compose.near(self, at(450, 250), (0, 0, 0))  # the layer hides the base there
        got = info["contrast"]["title"]
        self.assertEqual((got["zone"], got["text"]), ([400, 200, 300, 100], "#000000"))
        self.assertGreater(got["worst"], 4)  # black on gray 128; it would be 1.0 over the black block
        info, _ = self.render(layout={"title": {"x": 10, "y": 10, "w": 100, "h": 50}})
        self.assertEqual(info["contrast"]["title"]["zone"], [10, 10, 100, 50])

    def test_a_template_without_elements_has_no_contrast_and_a_malformed_one_still_composes(self):
        (self.root / "t.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">'
                                         '<g id="gimg-a" data-gimg-box="0 0 5 5"/><g id="gimg-a" data-gimg-box="0 0 5 5"/>'
                                         '</svg>', encoding="utf-8")
        info, _ = self.render()
        self.assertNotIn("contrast", info)
        with self.assertRaises(GimgError) as cm:  # ... but a layout asks for the elements
            self.render(layout={"a": {"x": 0, "y": 0, "w": 5, "h": 5}})
        self.assertEqual(cm.exception.code, "compose.bad_element")


class CliLayoutTests(test_cli.CliBase):
    def test_a_layout_that_is_not_json_is_bad_layout_and_composes_nothing(self):
        self.fails("compose", "nope", "og", "a", "--layout", "{no", message="invalid layout", lang="en")


if __name__ == "__main__":
    unittest.main()
