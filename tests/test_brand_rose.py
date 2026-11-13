"""`gimg brand rose` (gimg/brand.py): the compass rose drawn by code as an exact SVG."""
import json
import math
import re
import shutil
import unittest
import xml.etree.ElementTree as ET

from tests.test_brand import BrandBase

SVG = "{http://www.w3.org/2000/svg}"


class RoseTests(BrandBase):
    def make(self, *extra, name="rose.svg"):
        out = self.tmp / name
        code, stdout, err = self.run_cli("brand", "rose", "-o", str(out), *extra)
        self.assertEqual(code, 0, err)
        return out.read_text(encoding="utf-8")

    def arms(self, svg):
        return [p for p in ET.fromstring(svg).iter(SVG + "path") if p.get("class") == "arm"]

    def test_arm_count_follows_points(self):
        for points in (4, 8, 16):
            svg = self.make("--points", str(points), name="r%d.svg" % points)
            self.assertEqual(len(self.arms(svg)), points)
            for arm in self.arms(svg):
                self.assertTrue(arm.get("d").endswith("Z"))  # closed

    def test_one_stroke_width_and_no_text(self):
        svg = self.make("--points", "16")
        self.assertEqual(re.findall(r'stroke-width="([^"]+)"', svg), ["20.48"])
        self.assertNotIn("<text", svg)
        self.assertEqual(ET.fromstring(svg).get("viewBox"), "0 0 1024 1024")

    def test_current_color_leaves_no_ink_hex(self):
        svg = self.make("--ink", "currentcolor", "--accent", "currentColor")
        self.assertIn("currentColor", svg)
        for hexcolor in ("#13212b", "#0072a8"):
            self.assertNotIn(hexcolor, svg)

    def test_size_budget(self):
        self.assertLess(len(self.make("--points", "8").encode()), 15 * 1024)

    def test_main_tips_at_radius(self):
        svg = self.make("--size", "800", "--margin", "0.1")
        radius = 400 * 0.8
        dists = []
        for arm in self.arms(svg):
            pts = [(float(x), float(y)) for x, y in re.findall(r"([\d.]+) ([\d.]+)", arm.get("d"))]
            dists.append(max(math.hypot(x - 400, y - 400) for x, y in pts))
        self.assertEqual(sum(abs(d - radius) < 0.01 * radius for d in dists), 4)  # the four main arms
        self.assertEqual(sum(abs(d - 0.62 * radius) < 0.01 * radius for d in dists), 4)

    def test_bad_options_say_which(self):
        cases = (("--points", "6", "points must be one of 4, 8 or 16"),
                 ("--stroke", "0", "stroke must be"), ("--stroke", "0.1", "stroke must be"),
                 ("--margin", "0.4", "margin must be"), ("--margin", "-0.1", "margin must be"),
                 ("--ink", "red", "ink must be"), ("--accent", "#12", "accent must be"))
        for opt, value, text in cases:
            code, out, err = self.run_cli("brand", "rose", "-o", str(self.tmp / "x.svg"), opt + "=" + value)
            self.assertNotEqual(code, 0, (opt, value))
            self.assertIn(text, out + err)
            self.assertFalse((self.tmp / "x.svg").exists())

    def test_no_ring_and_no_ticks(self):
        svg = self.make("--no-ring", "--ticks", "0")
        self.assertNotIn('class="ring"', svg)
        self.assertNotIn('class="tick"', svg)

    def test_json(self):
        out = self.tmp / "j.svg"
        code, stdout, _ = self.run_cli("brand", "rose", "-o", str(out), "--json")
        data = json.loads(stdout)
        self.assertEqual((data["arms"], data["out"], data["bytes"]), (8, str(out), out.stat().st_size))

    @unittest.skipUnless(shutil.which("rsvg-convert"), "needs rsvg-convert")
    def test_png(self):
        png_path = self.tmp / "rose.png"
        self.make("--size", "256", "--png", str(png_path))
        data = png_path.read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(int.from_bytes(data[16:20], "big"), 256)


if __name__ == "__main__":
    unittest.main()
