import re
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from xml.etree import ElementTree

from gimg import png, trace
from gimg.errors import GimgError

NS = "{http://www.w3.org/2000/svg}"
GOLD, DARK, LIGHT = (184, 134, 43), (58, 52, 45), (255, 233, 168)


def canvas(w, h, color=(0, 0, 0, 0)):
    return w, h, bytearray(bytes(color) * (w * h))


def fill(img, x0, y0, x1, y1, color):
    w, _h, px = img
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[(y * w + x) * 4:(y * w + x) * 4 + 4] = bytes(color)


def paths(svg):
    return ElementTree.fromstring(svg).findall(NS + "path")


def logo():
    """Gold square with a dark square in it and a light one in that, on transparency."""
    img = canvas(40, 40)
    fill(img, 4, 4, 36, 36, GOLD + (255,))
    fill(img, 12, 12, 28, 28, DARK + (255,))
    fill(img, 17, 17, 23, 23, LIGHT + (255,))
    return img


class PngReadTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def test_rgba_round_trip(self):
        px = bytearray(range(12 * 4))
        path = self.dir / "a.png"
        path.write_bytes(png.rgba_bytes(4, 3, px))
        self.assertEqual(png.read_rgba(path), (4, 3, px))

    def test_rgb_reads_as_opaque_rgba(self):
        path = self.dir / "a.png"
        path.write_bytes(png.png_bytes(3, 2, (10, 20, 30)))
        w, h, px = png.read_rgba(path)
        self.assertEqual((w, h, bytes(px)), (3, 2, bytes((10, 20, 30, 255)) * 6))

    def test_all_filters_decode(self):
        # a 3x5 RGBA picture encoded by hand with filters 0-4, one per row
        w, h, bpp = 3, 5, 4
        rows = [bytes((7 * y + 3 * i + (i * i) % 11) & 255 for i in range(w * bpp)) for y in range(h)]
        raw = b""
        prev = bytes(w * bpp)
        for y, line in enumerate(rows):
            f = y % 5
            enc = bytearray()
            for i, v in enumerate(line):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pred = (0, a, b, (a + b) >> 1, a if pa <= pb and pa <= pc else (b if pb <= pc else c))[f]
                enc.append((v - pred) & 255)
            raw += bytes([f]) + bytes(enc)
            prev = line
        data = (png.SIGNATURE + png.chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + png.chunk(b"IDAT", zlib.compress(raw)) + png.chunk(b"IEND", b""))
        path = self.dir / "f.png"
        path.write_bytes(data)
        self.assertEqual(bytes(png.read_rgba(path)[2]), b"".join(rows))

    def test_unsupported_and_broken_files_say_why(self):
        def reason(data):
            path = self.dir / "x.png"
            path.write_bytes(data)
            with self.assertRaises(GimgError) as cm:
                png.read_rgba(path)
            self.assertEqual(cm.exception.code, "png.invalid")
            return cm.exception.params["reason"]
        ihdr = lambda depth, color, il: png.chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, depth, color, 0, 0, il))
        idat = png.chunk(b"IDAT", zlib.compress(b"\x00\x00"))
        end = png.chunk(b"IEND", b"")
        self.assertIn("only 8-bit RGB or RGBA", reason(png.SIGNATURE + ihdr(16, 6, 0) + idat + end))
        self.assertIn("interlace 1", reason(png.SIGNATURE + ihdr(8, 6, 1) + idat + end))
        self.assertIn("wrong length", reason(png.SIGNATURE + ihdr(8, 6, 0) + idat + end))
        self.assertIn("unknown scanline filter 9", reason(
            png.SIGNATURE + ihdr(8, 2, 0) + png.chunk(b"IDAT", zlib.compress(b"\x09\x00\x00\x00")) + end))
        self.assertIn("not a PNG", reason(b"nope"))

    def test_rgba_bytes_rejects_a_wrong_size(self):
        with self.assertRaisesRegex(ValueError, "do not fit a 2x2"):
            png.rgba_bytes(2, 2, b"\x00" * 15)


class ToSvgTests(unittest.TestCase):
    def test_one_path_per_color_and_xml_parses(self):
        w, h, px = logo()
        svg = trace.to_svg(w, h, px, palette=["#b8862b", "#3a342d", "#ffe9a8"], smooth_passes=0, min_island=1)
        root = ElementTree.fromstring(svg)
        self.assertEqual(root.get("viewBox"), "0 0 40 40")
        ps = root.findall(NS + "path")
        self.assertEqual(len(ps), 3)
        self.assertEqual([p.get("fill") for p in ps].count("#b8862b"), 1)
        self.assertEqual(ps[0].get("fill"), "#b8862b")  # the silhouette goes under, in the color that covers most

    def test_colors_come_from_the_image_without_a_palette(self):
        w, h, px = logo()
        svg = trace.to_svg(w, h, px, ncolores=3, smooth_passes=0, min_island=1)
        fills = {p.get("fill") for p in paths(svg)}
        self.assertEqual(fills, {"#b8862b", "#3a342d", "#ffe9a8"})

    def test_palette_quantizes_to_the_nearest_color(self):
        w, h, px = canvas(20, 20)
        fill((w, h, px), 2, 2, 18, 18, (250, 10, 10, 255))
        svg = trace.to_svg(w, h, px, palette=["#ff0000", "#0000ff"], smooth_passes=0, min_island=1)
        self.assertEqual([p.get("fill") for p in paths(svg)], ["#ff0000"])

    def test_small_island_is_dropped_and_min_island_zero_keeps_it(self):
        img = canvas(40, 40)
        fill(img, 5, 5, 30, 30, GOLD + (255,))
        fill(img, 33, 33, 35, 35, DARK + (255,))  # a 2x2 speck, apart
        w, h, px = img
        opts = dict(palette=["#b8862b", "#3a342d"], smooth_passes=0)
        kept = trace.to_svg(w, h, px, min_island=1, **opts)
        dropped = trace.to_svg(w, h, px, min_island=9, **opts)
        self.assertEqual(len(paths(kept)), 2)
        self.assertEqual(len(paths(dropped)), 1)  # no path for a color that only had an island
        self.assertEqual(paths(dropped)[0].get("fill"), "#b8862b")
        self.assertEqual(paths(dropped)[0].get("d").count("M"), 1)

    def test_mono_and_silhouette_are_one_path(self):
        w, h, px = logo()
        mono = paths(trace.to_svg(w, h, px, "mono", palette=["#b8862b", "#3a342d", "#ffe9a8"], smooth_passes=0))
        self.assertEqual(len(mono), 1)
        self.assertEqual(mono[0].get("fill"), "currentColor")
        sil = paths(trace.to_svg(w, h, px, "silueta", color="#123456", smooth_passes=0))
        self.assertEqual(len(sil), 1)
        self.assertEqual(sil[0].get("fill"), "#123456")
        self.assertEqual(sil[0].get("d").count("M"), 1)  # the whole shape, no holes for the inner colors

    def test_mono_leaves_out_the_darkest_color_by_default_and_ink_overrides(self):
        w, h, px = logo()
        pal = ["#b8862b", "#3a342d", "#ffe9a8"]
        default = paths(trace.to_svg(w, h, px, "mono", palette=pal, smooth_passes=0))[0].get("d")
        self.assertEqual(default.count("M"), 3)  # the gold ring (outer edge + hole where the dark square is) and the light square
        all_ink = paths(trace.to_svg(w, h, px, "mono", palette=pal, ink=[0, 1, 2], smooth_passes=0))[0].get("d")
        self.assertEqual(all_ink.count("M"), 1)
        with self.assertRaisesRegex(ValueError, "ink: every index"):
            trace.to_svg(w, h, px, "mono", palette=pal, ink=[7])

    def test_curves_and_lines(self):
        img = canvas(40, 40)
        fill(img, 5, 5, 35, 35, GOLD + (255,))
        w, h, px = img
        flat = paths(trace.to_svg(w, h, px, "silueta", curves=False))[0].get("d")
        self.assertRegex(flat, r"^M[\d. ]+(L[\d. ]+)+Z$")
        sharp = paths(trace.to_svg(w, h, px, "silueta", curves=True, corner_deg=55))[0].get("d")
        self.assertNotIn("C", sharp)  # a square has only 90 degree corners, all kept sharp
        round_ = paths(trace.to_svg(w, h, px, "silueta", curves=True, corner_deg=179))[0].get("d")
        self.assertIn("C", round_)

    def test_dp_tol_simplifies(self):
        img = canvas(60, 60)
        for y in range(10, 50):  # a staircase diagonal edge
            fill(img, 10, y, 10 + (y - 10), y + 1, GOLD + (255,))
        w, h, px = img
        points = lambda tol: len(re.findall(r"[LM]", paths(trace.to_svg(w, h, px, "silueta", dp_tol=tol, curves=False,
                                                                       smooth_passes=0))[0].get("d")))
        self.assertGreater(points(0), points(3))

    def test_edge_cases(self):
        w, h, px = canvas(8, 8)
        empty = trace.to_svg(w, h, px)  # all background
        self.assertEqual(paths(empty), [])
        full = canvas(8, 8, GOLD + (255,))
        for mode in trace.MODES:
            self.assertEqual(len(paths(trace.to_svg(*full, mode, min_island=1))), 1, mode)
        one = trace.to_svg(1, 1, bytearray(GOLD + (255,)), min_island=0, dp_tol=0)
        self.assertEqual(len(paths(one)), 1)
        self.assertEqual(ElementTree.fromstring(one).get("viewBox"), "0 0 1 1")

    def test_big_image_is_reduced_and_the_viewbox_keeps_its_size(self):
        img = canvas(64, 64)
        fill(img, 8, 8, 56, 56, GOLD + (255,))
        w, h, px = img
        svg = trace.to_svg(w, h, px, "silueta", max_side=32, smooth_passes=0, curves=False)
        self.assertEqual(ElementTree.fromstring(svg).get("viewBox"), "0 0 64 64")
        self.assertEqual(paths(svg)[0].get("d"), "M8 8L56 8L56 56L8 56Z")

    def test_title_is_escaped(self):
        w, h, px = canvas(2, 2, GOLD + (255,))
        root = ElementTree.fromstring(trace.to_svg(w, h, px, "silueta", title='a<b & "c"'))
        self.assertEqual(root.find(NS + "title").text, 'a<b & "c"')

    def test_bad_options_say_why(self):
        w, h, px = logo()
        with self.assertRaisesRegex(ValueError, "mode must be one of color, mono, silueta"):
            trace.to_svg(w, h, px, "otro")
        with self.assertRaisesRegex(ValueError, "'rojo' is not a color like #rrggbb"):
            trace.to_svg(w, h, px, palette=["rojo"])
        with self.assertRaisesRegex(ValueError, "do not fit a 5x5"):
            trace.to_svg(5, 5, px)
        with self.assertRaisesRegex(ValueError, "ncolores >= 1"):
            trace.to_svg(w, h, px, ncolores=0)


if __name__ == "__main__":
    unittest.main()
