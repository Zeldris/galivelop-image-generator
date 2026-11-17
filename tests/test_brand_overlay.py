"""`gimg brand trace --ink-only` and `gimg brand overlay` (gimg/brand.py, gimg/trace.py) on tiny synthetic inputs."""
import json
import re
import unittest
from xml.etree import ElementTree as ET

from gimg import png
from tests.test_brand import BrandBase, path_svg

NS = "{http://www.w3.org/2000/svg}"
LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"><defs><linearGradient id="gv-fondo" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#2BB3EA"/><stop offset="1" stop-color="#0083C1"/></linearGradient></defs>'
        '<rect width="128" height="128" rx="30" fill="url(#gv-fondo)"/><g fill="none" stroke="#FFFFFF" stroke-width="12" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M55.4 45.6 A24 24 0 1 0 64 64"/><path d="M50 64 H80"/>'
        '<path d="M71 40 L89.5 88 L108 40"/></g></svg>')


def two_color_png(path, size=24):
    """Blue square on a white page."""
    rgba = bytearray()
    for y in range(size):
        for x in range(size):
            inside = size // 4 <= x < size - size // 4 and size // 4 <= y < size - size // 4
            rgba += bytes((0, 114, 168) if inside else (251, 252, 253)) + b"\xff"
    path.write_bytes(png.rgba_bytes(size, size, rgba))


class InkOnlyTests(BrandBase):
    def setUp(self):
        super().setUp()
        self.src = self.tmp / "a.png"
        two_color_png(self.src)

    def trace(self, *extra):
        out = self.tmp / "a.svg"
        code, text, err = self.run_cli("brand", "trace", str(self.src), "-o", str(out), "--ink-only", "--palette",
                                       "#13212b,#0072a8,#fbfcfd", *extra)
        return code, err, out

    def test_paper_is_dropped_and_the_rest_is_one_currentcolor_path(self):
        code, err, out = self.trace()
        self.assertEqual(code, 0, err)
        svg = out.read_text()
        self.assertEqual(svg.count("<path"), 1)
        self.assertIn('fill="currentColor"', svg)
        self.assertNotRegex(svg, r"#[0-9a-fA-F]{6}")
        # the page is not drawn: the one path stays inside the blue square (6..18 of 24 -> 256..768 of 1024-ish units)
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", re.search(r' d="([^"]*)"', svg).group(1))]
        self.assertTrue(nums and min(nums) > 1 and max(nums) < 23.5, nums)

    def test_an_explicit_paper_drops_that_color_instead(self):
        code, err, out = self.trace("--paper", "#0072a8")
        self.assertEqual(code, 0, err)
        svg = out.read_text()
        self.assertEqual(svg.count("<path"), 1)
        self.assertEqual(svg.count("currentColor"), 1)

    def test_paper_needs_ink_only(self):
        code, _, err = self.run_cli("brand", "trace", str(self.src), "-o", str(self.tmp / "x.svg"), "--paper", "#ffffff")
        self.assertEqual(code, 1)
        self.assertIn("--paper only goes with --ink-only", err)


class InkOnlyNoPaperTests(BrandBase):
    def test_silueta_ink_only_without_palette_traces_everything_opaque(self):  # finding 3
        src, out = self.tmp / "s.png", self.tmp / "s.svg"
        two_color_png(src)
        code, _, err = self.run_cli("brand", "trace", str(src), "-o", str(out), "--mode", "silhouette", "--ink-only")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.read_text().count("<path"), 1)
        self.assertIn('fill="currentColor"', out.read_text())

    def test_matte_ink_only_keeps_the_light_details_of_the_drawing(self):  # finding 6
        size = 24
        rgba = bytearray()
        for y in range(size):  # transparent page; a dark square with a near-white block inside it
            for x in range(size):
                if 4 <= x < 20 and 4 <= y < 20:
                    rgba += bytes((250, 250, 250) if 8 <= x < 16 and 8 <= y < 16 else (20, 40, 90)) + b"\xff"
                else:
                    rgba += b"\0\0\0\0"
        src, out = self.tmp / "t.png", self.tmp / "t.svg"
        src.write_bytes(png.rgba_bytes(size, size, rgba))
        code, _, err = self.run_cli("brand", "trace", str(src), "-o", str(out), "--ink-only", "--palette", "#142a5a,#fafafa")
        self.assertEqual(code, 0, err)
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", re.search(r' d="([^"]*)"', out.read_text()).group(1))]
        self.assertTrue(min(nums) > 1 and max(nums) < 23.5)
        self.assertEqual(out.read_text().count("M"), 1)  # one solid shape: the light block is ink, not a hole


class OverlayTests(BrandBase):
    def setUp(self):
        super().setUp()
        self.base, self.motif = self.tmp / "base.svg", self.tmp / "motif.svg"
        self.base.write_text(path_svg(1024, 1024, "#13212b"))
        self.motif.write_text(LOGO)
        self.out = self.tmp / "o.svg"

    def run_overlay(self, *extra, ok=True):
        code, text, err = self.run_cli("brand", "overlay", str(self.base), str(self.motif), "-o", str(self.out), "--json", *extra)
        if ok:
            self.assertEqual(code, 0, err)
            return json.loads(text)
        return code, err

    def nested(self):
        return ET.fromstring(self.out.read_text()).find(NS + "svg")

    def test_default_fit_centres_a_half_width_motif(self):
        data = self.run_overlay()
        svg = self.nested()
        self.assertEqual((svg.get("x"), svg.get("y"), svg.get("width"), svg.get("height")), ("256", "256", "512", "512"))
        self.assertEqual(svg.get("viewBox"), "0 0 128 128")
        self.assertEqual(data["scale"], 4.0)

    def test_the_base_is_kept_as_it_was(self):
        self.run_overlay()
        text, base = self.out.read_text(), self.base.read_text()
        self.assertTrue(text.startswith(base[:base.rindex("</svg>")]))
        self.assertTrue(text.rstrip().endswith("</svg>"))

    def test_fit_scales_by_the_longer_side_of_a_box(self):
        data = self.run_overlay("--fit", "0.25", "--box", "20,30,100,50")
        svg = self.nested()
        self.assertEqual(svg.get("viewBox"), "20 30 100 50")
        self.assertEqual((svg.get("width"), svg.get("height")), ("256", "128"))  # 100 -> 0.25 x 1024
        self.assertEqual((svg.get("x"), svg.get("y")), ("384", "448"))  # centred: (1024-256)/2, (1024-128)/2
        self.assertEqual(data["scale"], 2.56)

    def test_a_taller_box_is_fitted_by_its_height(self):
        self.run_overlay("--box", "0,0,40,80")
        svg = self.nested()
        self.assertEqual((svg.get("width"), svg.get("height")), ("256", "512"))
        self.assertEqual(svg.get("x"), "384")

    def test_strokes_are_kept_and_the_ids_are_prefixed(self):
        self.run_overlay()
        text = self.out.read_text()
        self.assertIn('stroke="#FFFFFF"', text)
        self.assertIn('stroke-width="12"', text)
        self.assertIn('id="mo-gv-fondo"', text)
        self.assertIn("url(#mo-gv-fondo)", text)
        self.assertNotIn('id="gv-fondo"', text)
        self.assertNotIn("url(#gv-fondo)", text)

    def test_ids_that_the_base_already_has_do_not_collide(self):
        self.base.write_text(LOGO.replace("viewBox=\"0 0 128 128\"", "viewBox=\"0 0 1024 1024\""))
        self.run_overlay()
        ids = [el.get("id") for el in ET.fromstring(self.out.read_text()).iter() if el.get("id")]
        self.assertEqual(sorted(ids), ["gv-fondo", "mo-gv-fondo"])

    def test_recolor_paints_every_fill_and_stroke_that_is_not_none(self):
        self.motif.write_text(LOGO.replace('<path d="M50 64 H80"/>', '<path d="M50 64 H80" style="stroke:#112233;fill:none"/>'))
        self.run_overlay("--recolor", "#ABCDEF")
        text = self.out.read_text()
        self.assertNotIn("#FFFFFF", text)
        self.assertNotIn("#112233", text)
        self.assertNotIn("url(#", text)
        self.assertNotIn("gv-fondo", text)
        self.assertIn('stroke="#ABCDEF"', text)
        self.assertIn("stroke:#ABCDEF;fill:none", text)
        self.assertIn('fill="none"', text)

    def test_recolor_current_color_leaves_a_single_ink_motif(self):
        self.run_overlay("--recolor", "currentcolor", "--skip-rect")
        text = self.out.read_text()
        self.assertIn('stroke="currentColor"', text)
        self.assertNotIn("#FFFFFF", text)
        self.assertNotIn("currentcolor", text)

    def test_skip_rect_drops_the_background_square(self):
        self.run_overlay("--skip-rect")
        text = self.out.read_text()
        self.assertNotIn("<rect", text)
        self.assertEqual(text.count("<path"), 4)  # the base path and the three strokes

    def test_a_traced_motif_is_placed_too(self):
        self.motif.write_text(path_svg(1024, 1024, "#0072a8"))
        self.run_overlay("--fit", "0.5", "--recolor", "#ffffff")
        svg = self.nested()
        self.assertEqual((svg.get("x"), svg.get("width"), svg.get("viewBox")), ("256", "512", "0 0 1024 1024"))
        self.assertIn('fill="#ffffff"', self.out.read_text())

    def test_a_malformed_motif_says_why_and_writes_nothing(self):
        self.motif.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><g></svg>')
        code, err = self.run_overlay(ok=False)
        self.assertEqual(code, 1)
        self.assertIn("does not work for the overlay", err)
        self.assertIn("not well-formed XML", err)
        self.assertFalse(self.out.exists())

    def test_a_motif_without_viewbox_asks_for_box(self):
        self.motif.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>')
        code, err = self.run_overlay(ok=False)
        self.assertEqual(code, 1)
        self.assertIn("no usable viewBox (give --box x,y,w,h)", err)

    def test_a_base_without_viewbox_is_refused(self):
        self.base.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>")
        code, err = self.run_overlay(ok=False)
        self.assertEqual(code, 1)
        self.assertIn("not an SVG with a viewBox", err)

    def test_a_script_in_the_motif_is_refused(self):
        self.motif.write_text(LOGO.replace("<rect", "<script>alert(1)</script><rect"))
        code, err = self.run_overlay(ok=False)
        self.assertEqual(code, 1)
        self.assertIn("it has <script>", err)

    def test_bad_options_say_which(self):
        for extra, msg in ((("--recolor", "red"), "is not #rgb, #rrggbb or currentColor"), (("--box", "1,2,3"), "box must be x,y,w,h"),
                           (("--fit", "0"), "fit must be above 0")):
            code, err = self.run_overlay(*extra, ok=False)
            self.assertEqual(code, 1)
            self.assertIn(msg, err)

    def test_the_output_cannot_be_an_input(self):
        self.out = self.base
        code, err = self.run_overlay(ok=False)
        self.assertEqual(code, 1)
        self.assertIn("is the original itself", err)


if __name__ == "__main__":
    unittest.main()


class OverlayPaintTests(BrandBase):
    def overlay(self, body, *extra):
        motif, base, out = self.tmp / "m.svg", self.tmp / "b.svg", self.tmp / "o.svg"
        base.write_text(path_svg(1024, 1024, "#13212b"))
        motif.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">%s</svg>' % body)
        code, _, err = self.run_cli("brand", "overlay", str(base), str(motif), "-o", str(out), *extra)
        self.assertEqual(code, 0, err)
        return out.read_text()

    def test_recolor_leaves_unpainted_values_alone(self):  # finding 4
        text = self.overlay('<path d="M0 0h1v1z" fill="transparent" stroke="rgba(0,0,0,0)"/>'
                            '<path d="M2 2h1v1z" fill="inherit" stroke="currentColor"/>'
                            '<path d="M4 4h1v1z" fill="#123456"/>', "--recolor", "#ffffff")
        for kept in ('fill="transparent"', 'stroke="rgba(0,0,0,0)"', 'fill="inherit"', 'stroke="currentColor"'):
            self.assertIn(kept, text)
        self.assertNotIn("#123456", text)
        self.assertIn('fill="#ffffff"', text)

    def test_recolor_reaches_the_css_and_ids_are_prefixed_and_scoped(self):  # finding 5
        text = self.overlay('<style>#a{fill:#ff0000;stroke:none}.b{fill:red}</style>'
                            '<path id="a" d="M0 0h1v1z"/><path class="b" d="M2 2h1v1z"/>', "--recolor", "#00ff00")
        self.assertNotIn("#ff0000", text)
        self.assertNotIn("fill:red", text)
        self.assertIn("stroke:none", text)
        self.assertIn("#mo-root #mo-a{fill:#00ff00;stroke:none}", text)
        self.assertIn("#mo-root .b{fill:#00ff00}", text)
