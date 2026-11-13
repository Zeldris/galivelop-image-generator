"""`gimg brand fit` (gimg/brand.py): the motif lands in a zone, the rest is paper; on small synthetic PNGs."""
import json
import unittest
from pathlib import Path

from gimg import png
from tests.test_brand import BrandBase

W, H = 160, 40
LIGHT, DARK = (240, 236, 220), (20, 24, 40)
INK_ON_LIGHT, INK_ON_DARK = (30, 60, 140), (230, 200, 90)


def band_png(path, paper=LIGHT, ink=INK_ON_LIGHT, rect=(10, 8, 50, 32), size=(W, H)):
    """A flat `paper` image with a rectangle of `ink` (x0, y0, x1, y1; end excluded)."""
    w, h = size
    x0, y0, x1, y1 = rect
    rgba = bytearray()
    for y in range(h):
        for x in range(w):
            rgba += bytes(ink if x0 <= x < x1 and y0 <= y < y1 else paper) + b"\xff"
    Path(path).write_bytes(png.rgba_bytes(w, h, rgba))


def px(rgba, w, x, y):
    i = (y * w + x) * 4
    return tuple(rgba[i:i + 3])


class FitTests(BrandBase):
    def setUp(self):
        super().setUp()
        self.src = self.tmp / "band.png"
        self.out = self.tmp / "fit.png"

    def fit(self, *extra, src=None):
        return self.run_cli("brand", "fit", str(src or self.src), "-o", str(self.out), *extra)

    def test_anchor_right_with_min_x_moves_the_box_into_the_zone(self):
        band_png(self.src)  # a 40x24 box at x 10-50
        code, out, err = self.fit("--anchor", "right", "--min-x", "100", "--margin", "8", "--feather", "0", "--json")
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        self.assertEqual(res["paper"], "#f0ecdc")
        self.assertEqual(res["box"], [10, 8, 50, 32])
        self.assertEqual(res["scale"], 1.0)
        self.assertEqual(res["box_after"][2], W - 8)  # the right side of the box on the right side of the zone
        self.assertEqual(res["box_after"][0], W - 8 - 40)
        self.assertEqual(res["shift"], [W - 8 - 50, 0])
        w, h, rgba = png.read_rgba(self.out)
        self.assertEqual((w, h), (W, H))
        self.assertEqual(px(rgba, w, W - 8 - 20, 20), INK_ON_LIGHT)  # the middle of the moved rectangle
        self.assertEqual(px(rgba, w, 30, 20), LIGHT)  # where it was

    def test_a_box_wider_than_the_zone_is_scaled_to_it(self):
        band_png(self.src, rect=(10, 8, 90, 32))  # 80 wide
        code, out, err = self.fit("--min-x", "100", "--margin", "8", "--json")
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        self.assertAlmostEqual(res["scale"], 52 / 80, places=3)  # zone 100..152
        self.assertAlmostEqual(res["box_after"][0], 100, delta=1)
        self.assertAlmostEqual(res["box_after"][2], 152, delta=1)

    def test_pixels_outside_the_moved_image_are_paper_and_output_is_opaque(self):
        band_png(self.src)
        self.assertEqual(self.fit("--min-x", "100", "--margin", "8", "--feather", "0", "--feather-y", "0")[0], 0)
        w, h, rgba = png.read_rgba(self.out)
        self.assertTrue(all(a == 255 for a in rgba[3::4]))
        shift = W - 8 - 50
        for y in range(h):
            for x in range(shift):  # left of the moved image
                self.assertEqual(px(rgba, w, x, y), LIGHT)

    def test_edges_fade_in_a_ramp_and_the_ones_on_the_canvas_edge_do_not(self):
        # a dark image whose ink is bright: the fade must go from paper (dark) to the image
        band_png(self.src, paper=DARK, ink=INK_ON_DARK, rect=(10, 12, 40, 28))
        code, out, err = self.fit("--min-x", "100", "--margin", "8", "--feather", "20", "--feather-y", "0", "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["paper"], "#141828")
        w, h, rgba = png.read_rgba(self.out)
        shift = json.loads(out)["shift"][0]
        # the left edge of the image is inside the canvas: its first column is nearly the paper
        self.assertEqual(px(rgba, w, shift, 20), DARK)  # alpha 0.5/20 over a paper that is the same everywhere
        self.assertEqual(px(rgba, w, 0, 0), DARK)

    def test_fade_blends_toward_the_paper(self):
        band_png(self.src, rect=(10, 0, 50, 40))  # ink touches the top and bottom rows
        code, out, err = self.fit("--min-x", "100", "--margin", "0", "--feather", "20", "--feather-y", "0", "--json")
        self.assertEqual(code, 0, err)
        shift = json.loads(out)["shift"][0]
        w, h, rgba = png.read_rgba(self.out)
        edge, mid = px(rgba, w, shift + 10, 20), px(rgba, w, shift + 25, 20)
        self.assertEqual(mid, INK_ON_LIGHT)  # past the ramp
        self.assertNotEqual(edge, INK_ON_LIGHT)  # inside the ramp (the image starts at x 0 of itself: paper there)
        self.assertEqual(edge, tuple(round(p + (i - p) * 10.5 / 20) for p, i in zip(LIGHT, INK_ON_LIGHT)))

    def test_dark_paper_is_found_with_auto(self):
        band_png(self.src, paper=DARK, ink=INK_ON_DARK)
        code, out, err = self.fit("--min-x", "100", "--margin", "8", "--feather", "0", "--json")
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        self.assertEqual(res["paper"], "#141828")
        self.assertEqual(res["box"], [10, 8, 50, 32])
        w, h, rgba = png.read_rgba(self.out)
        self.assertEqual(px(rgba, w, W - 8 - 20, 20), INK_ON_DARK)
        self.assertEqual(px(rgba, w, 5, 5), DARK)

    def test_explicit_paper_overrides_auto(self):
        band_png(self.src)
        code, out, _ = self.fit("--min-x", "100", "--margin", "8", "--paper", "#ffffff", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["paper"], "#ffffff")

    def test_a_box_already_in_the_zone_leaves_the_image_as_it_is(self):
        band_png(self.src, rect=(110, 8, 150, 32))
        code, out, err = self.fit("--min-x", "100", "--margin", "8", "--json")
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        self.assertEqual((res["scale"], res["shift"]), (1.0, [0, 0]))
        self.assertEqual(png.read_rgba(self.out), png.read_rgba(self.src))

    def test_noise_does_not_widen_the_box(self):
        band_png(self.src)
        w, h, rgba = png.read_rgba(self.src)
        rgba = bytearray(rgba)
        i = (20 * w + 140) * 4  # one stray ink pixel far away: under 0.5 % of its column and row
        rgba[i:i + 3] = bytes(INK_ON_LIGHT)
        Path(self.src).write_bytes(png.rgba_bytes(w, h, rgba))
        _, out, _ = self.fit("--min-x", "100", "--margin", "8", "--json")
        self.assertEqual(json.loads(out)["box"], [10, 8, 50, 32])

    def test_center_and_left_anchors(self):
        band_png(self.src)
        _, out, _ = self.fit("--anchor", "left", "--min-x", "100", "--margin", "8", "--json")
        self.assertEqual(json.loads(out)["box_after"][0], 100)
        _, out, _ = self.fit("--anchor", "center", "--min-x", "100", "--margin", "8", "--json")
        after = json.loads(out)["box_after"]
        self.assertEqual((after[0] + after[2]) / 2, (100 + W - 8) / 2)

    def test_text_output_and_source_untouched(self):
        band_png(self.src)
        before = self.src.read_bytes()
        code, out, _ = self.fit("--min-x", "100", "--margin", "8")
        self.assertEqual(code, 0)
        self.assertIn("scale 1.0", out)
        self.assertEqual(self.src.read_bytes(), before)

    def test_no_ink_says_so(self):
        band_png(self.src, ink=LIGHT)
        code, out, err = self.fit("--min-x", "100", "--margin", "8")
        self.assertEqual(code, 1)
        self.assertIn("no ink found", err)
        self.assertFalse(self.out.exists())

    def test_empty_zone_says_so(self):
        band_png(self.src)
        code, out, err = self.fit("--min-x", "120", "--max-x", "120", "--margin", "8")
        self.assertEqual(code, 1)
        self.assertIn("empty zone", err)
        code, out, err = self.fit("--min-x", "130", "--max-x", "100", "--margin", "8")
        self.assertIn("empty zone", err)

    def test_output_equal_to_input_is_refused(self):
        band_png(self.src)
        before = self.src.read_bytes()
        code, out, err = self.run_cli("brand", "fit", str(self.src), "-o", str(self.src), "--min-x", "100")
        self.assertEqual(code, 1)
        self.assertIn("is the original itself", err)
        self.assertEqual(self.src.read_bytes(), before)

    def test_options_out_of_range_name_the_problem(self):
        band_png(self.src)
        for args, text in ((("--tol", "900"), "tol 0-442"), (("--feather", "-1"), "feather"),
                           (("--max-scale", "0"), "max-scale above 0"), (("--margin", "-3"), "margin"),
                           (("--paper", "nope"), "not a color"), (("--max-x", "500"), "min-x and max-x must lie inside"),
                           (("--min-x", "-5"), "min-x and max-x must lie inside")):
            code, out, err = self.fit("--margin", "8", *args)
            self.assertEqual(code, 1, args)
            self.assertIn("invalid option", err, args)
            self.assertIn(text, err, args)


if __name__ == "__main__":
    unittest.main()
