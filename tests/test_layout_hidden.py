"""F4e.1a (trozo 3): `"hidden": true` per element of a layout. Casos límite: todos ocultos, id inexistente con hidden,
hidden junto a x/y cambiados, hidden no booleano, mostrar (quitar hidden), layout viejo, plantilla guardada."""
import json
import unittest
from unittest import mock

from gimg import compose, orders
from gimg.errors import GimgError
from tests import test_compose, test_compose_worker, test_elements, test_template_save
from tests.test_elements import SVG, TARGET, LayoutFakeRender, RecomposeLayoutTests

TITLE = {"x": 100, "y": 200, "w": 400, "h": 80}  # the original box of the title
LOGO = {"x": 1000, "y": 20, "w": 160, "h": 60}
HID = dict(TITLE, hidden=True)


def code_and_reason(case, call, *args):
    with case.assertRaises(GimgError) as cm:
        call(*args)
    return cm.exception.code, cm.exception.params.get("reason")


class HiddenSvgTests(unittest.TestCase):
    def test_a_hidden_element_gets_display_none_even_with_its_box_unchanged(self):
        out = compose.apply_layout(SVG, {"title": HID}, TARGET)
        self.assertIn('display="none"', out)
        self.assertEqual(out.count('display="none"'), 1)
        self.assertEqual(out.replace(' display="none"', ""), SVG)  # nothing else changed: the box is the original

    def test_an_existing_display_attribute_is_replaced_not_repeated(self):
        svg = SVG.replace('<rect id="gimg-ornament1"', '<rect id="gimg-ornament1" display="inline"')
        out = compose.apply_layout(svg, {"ornament1": dict(x=0, y=600, w=1200, h=30, hidden=True)}, TARGET)
        self.assertIn('display="none"', out)
        self.assertNotIn("inline", out)
        self.assertEqual(out.count("display="), 1)

    def test_all_elements_hidden(self):
        layout = {"title": HID, "logo": dict(LOGO, hidden=True), "ornament1": dict(x=0, y=600, w=1200, h=30, hidden=True)}
        out = compose.apply_layout(SVG, layout, TARGET)
        self.assertEqual(out.count('display="none"'), 3)
        self.assertEqual(len(compose.elements(out, TARGET)), 3)  # still readable as elements
        self.assertEqual(compose._check_layout(compose._elements(SVG, TARGET), layout, TARGET),
                         {"title": HID, "logo": dict(LOGO, hidden=True),
                          "ornament1": dict(x=0, y=600, w=1200, h=30, hidden=True)})

    def test_hidden_with_a_moved_box_moves_and_hides(self):
        box = {"x": 50, "y": 100, "w": 200, "h": 40, "hidden": True}
        out = compose.apply_layout(SVG, {"title": box}, TARGET)
        self.assertIn("translate(50 100) scale(0.5 0.5) translate(-100 -200)", out)
        self.assertIn('data-gimg-box="50 100 200 40"', out)
        self.assertIn('display="none"', out)

    def test_showing_it_back_is_dropping_hidden_or_setting_false(self):
        self.assertEqual(compose.apply_layout(SVG, {"title": dict(TITLE, hidden=False)}, TARGET), SVG)
        self.assertEqual(compose.apply_layout(SVG, {"title": TITLE}, TARGET), SVG)
        moved = dict(x=50, y=100, w=200, h=40)
        found = compose._elements(SVG, TARGET)
        self.assertEqual(compose._check_layout(found, {"title": dict(moved, hidden=False)}, TARGET), {"title": moved})
        self.assertNotIn("display", compose.apply_layout(SVG, {"title": dict(moved, hidden=False)}, TARGET))

    def test_an_old_layout_without_hidden_is_the_same_as_before(self):
        out = compose.apply_layout(SVG, {"title": {"x": 50, "y": 100, "w": 200, "h": 40}}, TARGET)
        self.assertNotIn("display", out)

    def test_an_unknown_id_with_hidden_is_element_unknown(self):
        self.assertEqual(code_and_reason(self, compose.apply_layout, SVG, {"ghost": dict(TITLE, hidden=True)}, TARGET)[0],
                         "compose.element_unknown")

    def test_hidden_that_is_not_a_boolean_is_bad_layout_with_its_reason(self):
        for value in ("true", 1, 0, None, [], "yes"):
            self.assertEqual(code_and_reason(self, compose.apply_layout, SVG, {"title": dict(TITLE, hidden=value)}, TARGET),
                             ("compose.bad_layout", "hidden boolean"), value)
        self.assertEqual(code_and_reason(self, compose.apply_layout, SVG, {"title": dict(TITLE, other=True)}, TARGET),
                         ("compose.bad_layout", "x, y, w, h integers"))


class InheritedHiddenTests(unittest.TestCase):
    """A template saved with a hidden element carries ``display="none"``; showing it must work."""
    SAVED = compose.apply_layout(SVG, {"title": HID}, TARGET)

    def test_hidden_false_on_a_tag_that_is_already_hidden_is_kept_and_removes_the_display(self):
        found = compose._elements(self.SAVED, TARGET)
        self.assertEqual(compose._check_layout(found, {"title": dict(TITLE, hidden=False)}, TARGET),
                         {"title": dict(TITLE, hidden=False)})
        out = compose.apply_layout(self.SAVED, {"title": dict(TITLE, hidden=False)}, TARGET)
        self.assertNotIn("none", out)
        self.assertEqual(out.replace(' display="inline"', ""), SVG)

    def test_without_hidden_the_template_stays_hidden(self):
        self.assertEqual(compose.apply_layout(self.SAVED, {}, TARGET), self.SAVED)

    def test_style_display_is_written_and_removed_inside_style(self):
        svg = SVG.replace('<rect id="gimg-ornament1"', '<rect id="gimg-ornament1" style="fill:red;display:inline"')
        box = dict(x=0, y=600, w=1200, h=30)
        hid = compose.apply_layout(svg, {"ornament1": dict(box, hidden=True)}, TARGET)
        self.assertIn('style="fill:red;display:none"', hid)
        self.assertNotIn('display="none"', hid)
        shown = compose.apply_layout(hid, {"ornament1": dict(box, hidden=False)}, TARGET)
        self.assertEqual(shown, svg)
        self.assertEqual(compose.apply_layout(svg, {"ornament1": dict(box, hidden=False)}, TARGET), svg)  # not hidden: dropped


@test_compose_worker.CON_HERRAMIENTAS
class HiddenRenderTests(test_compose_worker.ComposeWorkerBase):
    def setUp(self):
        super().setUp()
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

    def test_a_hidden_element_is_not_painted_and_not_measured(self):
        box = {"x": 400, "y": 200, "w": 300, "h": 100}
        info, at = self.render()
        self.assertIn("title", info["contrast"])
        test_compose.near(self, at(450, 250), (0, 0, 0))
        info, at = self.render(layout={"title": dict(box, hidden=True)})
        test_compose.near(self, at(450, 250), (128, 128, 128))  # the base shows: nothing painted
        self.assertNotIn("contrast", info)  # the only text is hidden: no measure, so no contrast warning
        self.assertEqual(info["layout"], {"title": dict(box, hidden=True)})

    def test_showing_it_again_paints_and_measures_it(self):
        box = {"x": 400, "y": 200, "w": 300, "h": 100}
        info, at = self.render(layout={"title": dict(box, hidden=False)})
        test_compose.near(self, at(450, 250), (0, 0, 0))
        self.assertIn("title", info["contrast"])
        self.assertNotIn("layout", info)


class HiddenRecomposeTests(RecomposeLayoutTests):
    def test_the_hidden_layout_is_kept_and_reaches_the_render_and_showing_it_empties_it(self):
        self.made()
        att, render = self.go(layout={"title": HID})
        self.assertEqual((render.calls[0]["layout"], att["compose"]["layout"]), ({"title": HID}, {"title": HID}))
        att, render = self.go()  # without layout: the hidden one is kept
        self.assertEqual(render.calls[0]["layout"], {"title": HID})
        att, render = self.go(layout={"title": dict(HID, hidden=False)})  # show: the box is the original
        self.assertEqual(render.calls[0]["layout"], {"title": dict(TITLE, hidden=False)})

    def test_a_bad_hidden_changes_nothing_and_composes_nothing(self):
        self.made()
        before = orders.get("proj", "a", "og")
        with self.assertRaises(GimgError) as cm:
            self.go(layout={"title": dict(TITLE, hidden="yes")})
        self.assertEqual((cm.exception.code, cm.exception.params["reason"]), ("compose.bad_layout", "hidden boolean"))
        self.assertEqual(orders.get("proj", "a", "og"), before)


class HiddenSaveAndApiTests(test_template_save.SaveBase):
    def hide(self, layout):
        with mock.patch.object(compose, "render", lambda *a, **k: {
                "fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg", "text": {},
                "layout": k.get("layout")}):
            return self.ok("POST", self.att(self.key, self.profile, 1, "/compose"), {"layout": layout})

    def test_the_api_refuses_a_hidden_that_is_not_a_boolean_with_its_code_and_reason(self):
        resp, payload = self.send("POST", self.att(self.key, self.profile, 1, "/compose"),
                                  {"layout": {"title": dict(TITLE, hidden=1)}})
        self.err(resp, payload, 400, "compose.bad_layout")
        self.assertIn("hidden boolean", payload.decode())

    def test_save_as_template_keeps_the_hidden_element_and_leaves_the_origin_alone(self):
        self.hide({"title": HID})
        origin = (self.root / "t.svg").read_bytes()
        self.ok("POST", self.url, self.body(), 201)
        saved = (self.data / "mio.svg").read_text(encoding="utf-8")
        self.assertIn('display="none"', saved)
        self.assertEqual(saved.count('display="none"'), 1)
        self.assertEqual(saved.replace(' display="none"', ""), test_template_save.SVG)
        self.assertEqual((self.root / "t.svg").read_bytes(), origin)
        self.assertNotIn("display", origin.decode())


@test_compose_worker.CON_HERRAMIENTAS
class ShowInheritedRenderTests(HiddenRenderTests):
    def test_a_template_saved_with_a_hidden_element_paints_it_again_when_shown(self):
        box = {"x": 400, "y": 200, "w": 300, "h": 100}
        saved = compose.apply_layout((self.root / "t.svg").read_text(encoding="utf-8"), {"title": dict(box, hidden=True)},
                                     TARGET)
        (self.root / "t.svg").write_text(saved, encoding="utf-8")  # what save_template writes
        info, at = self.render()
        test_compose.near(self, at(450, 250), (128, 128, 128))  # composed with it: hidden
        info, at = self.render(layout={"title": dict(box, hidden=False)})
        test_compose.near(self, at(450, 250), (0, 0, 0))
        self.assertIn("title", info["contrast"])
