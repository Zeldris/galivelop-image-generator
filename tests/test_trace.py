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


def evenodd_area(d, size):
    """Pixels (centers) inside the path `d` made of straight M/L/Z loops, by the even-odd rule."""
    loops = [[tuple(map(float, pt.split())) for pt in re.findall(r"[ML]([\d. ]+)", chunk)] for chunk in d.split("Z") if chunk]
    count = 0
    for y in range(size):
        for x in range(size):
            px, py, inside = x + 0.5, y + 0.5, False
            for lp in loops:
                for i in range(len(lp)):
                    (x1, y1), (x2, y2) = lp[i], lp[(i + 1) % len(lp)]
                    if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
                        inside = not inside
            count += inside
    return count


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

    def test_filters_1_to_4_decode_in_rgb_too(self):
        w, h, bpp = 4, 5, 3
        rows = [bytes((11 * y + 5 * i + (i * i) % 7) & 255 for i in range(w * bpp)) for y in range(h)]
        raw, prev = b"", bytes(w * bpp)
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
        path = self.dir / "rgb.png"
        path.write_bytes(png.SIGNATURE + png.chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                         + png.chunk(b"IDAT", zlib.compress(raw)) + png.chunk(b"IEND", b""))
        got = png.read_rgba(path)[2]
        want = bytearray()
        for line in rows:
            for x in range(w):
                want += line[x * 3:x * 3 + 3] + b"\xff"
        self.assertEqual(got, want)

    def test_cut_or_missing_image_data_and_too_big_say_so(self):
        def reason(idat, w=2, h=2):
            path = self.dir / "c.png"
            path.write_bytes(png.SIGNATURE + png.chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                             + idat + png.chunk(b"IEND", b""))
            with self.assertRaises(GimgError) as cm:
                png.read_rgba(path)
            return cm.exception.params["reason"]
        self.assertIn("image data is missing", reason(b""))
        self.assertIn("image data is cut (9 of 18 bytes)", reason(png.chunk(b"IDAT", zlib.compress(b"\x00" * 9))))
        self.assertIn("too big", reason(png.chunk(b"IDAT", zlib.compress(b"")), w=5000, h=5000))

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
        self.assertIn("the image data is cut (2 of 5 bytes)", reason(png.SIGNATURE + ihdr(8, 6, 0) + idat + end))
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
        for mode in ("color", "silueta"):
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
        root = ElementTree.fromstring(trace.to_svg(w, h, px, "silueta", title='a<b & "c"', min_island=1))
        self.assertEqual(root.find(NS + "title").text, 'a<b & "c"')

    def test_mono_keeps_the_hole_of_a_stroke_ring_and_a_hollow_square(self):
        for bg in ((0, 0, 0, 0), (250, 250, 250, 255)):  # transparent, or strokes on opaque paper
            for name, (x0, x1) in (("ring", (4, 36)), ("square", (6, 34))):
                img = canvas(40, 40, bg)
                fill(img, x0, x0, x1, x1, (20, 20, 20, 255))
                fill(img, x0 + 4, x0 + 4, x1 - 4, x1 - 4, bg)
                with self.subTest(name=name, bg=bg[3]):
                    ps = paths(trace.to_svg(*img, "mono", smooth_passes=0, curves=False, dp_tol=0, min_island=1))
                    self.assertEqual(len(ps), 1)
                    d = ps[0].get("d")
                    self.assertEqual(ps[0].get("fill-rule"), "evenodd")
                    self.assertEqual(d.count("M"), 2, "outer and inner outline, not a filled block")
                    side = x1 - x0
                    self.assertEqual(evenodd_area(d, 40), side * side - (side - 8) ** 2)

    def test_mono_keeps_a_one_pixel_line_through_the_smoothing(self):
        for bg in ((0, 0, 0, 0), (255, 255, 255, 255)):
            img = canvas(60, 20, bg)
            fill(img, 3, 10, 57, 11, (0, 0, 0, 255))
            with self.subTest(bg=bg[3]):
                d = paths(trace.to_svg(*img, "mono", dp_tol=0.5, min_island=2, curves=False))[0].get("d")
                self.assertGreaterEqual(evenodd_area(d, 60), 40)
                self.assertEqual(d.count("M"), 1)

    def test_mono_two_color_paper_is_not_ink(self):
        img = canvas(40, 40, (250, 250, 250, 255))
        fill(img, 20, 0, 40, 40, (200, 215, 245, 255))  # half light, half blue background
        fill(img, 6, 6, 34, 34, (20, 20, 20, 255))
        fill(img, 10, 10, 30, 30, (250, 250, 250, 255))
        ps = paths(trace.to_svg(*img, "mono", ncolores=3, smooth_passes=0, curves=False, dp_tol=0, min_island=1))
        self.assertEqual(len(ps), 1)
        d = ps[0].get("d")
        self.assertEqual(evenodd_area(d, 40), 28 * 28 - 20 * 20)

    def test_mono_with_every_color_on_the_border_falls_back_to_the_darkest_rule(self):
        img = canvas(40, 40, (250, 250, 250, 255))
        fill(img, 0, 0, 40, 20, (20, 20, 20, 255))  # half dark, half light: both are >= 20% of the border
        ps = paths(trace.to_svg(*img, "mono", ncolores=2, smooth_passes=0, curves=False, dp_tol=0, min_island=1))
        self.assertEqual(len(ps), 1, "an empty SVG would mean every color was taken for paper")
        self.assertEqual(evenodd_area(ps[0].get("d"), 40), 40 * 20)

    def test_mono_refuses_an_empty_result_with_its_reason(self):
        img = canvas(20, 20, (250, 250, 250, 255))
        fill(img, 5, 5, 15, 15, (20, 20, 20, 255))
        pal = ["#fafafa", "#141414", "#c00000"]  # the only ink, red, is not in the drawing
        with self.assertRaisesRegex(ValueError, "no ink left"):
            trace.to_svg(*img, "mono", palette=pal, ink=[2], smooth_passes=0)
        self.assertEqual(paths(trace.to_svg(*canvas(8, 8), "mono")), [], "an empty drawing still gives an empty SVG")

    def test_thin_lines_are_only_restored_in_mono(self):
        img = canvas(60, 20)
        fill(img, 3, 10, 57, 11, (0, 0, 0, 255))
        for mode in ("color", "silueta"):
            with self.assertRaisesRegex(ValueError, "no shape left"):  # a bare 1 px line is smoothed away outside mono
                trace.to_svg(*img, mode, ncolores=1)

    def test_ring_with_a_hole_renders_as_a_ring_with_evenodd(self):
        img = canvas(24, 24)
        fill(img, 2, 2, 22, 22, GOLD + (255,))
        fill(img, 8, 8, 16, 16, (0, 0, 0, 0))
        d = paths(trace.to_svg(*img, "silueta", smooth_passes=0, curves=False, dp_tol=0, min_island=1))[0].get("d")
        self.assertEqual(d.count("M"), 2)
        self.assertEqual(evenodd_area(d, 24), 20 * 20 - 8 * 8)

    def test_control_characters_are_removed_and_color_is_checked(self):
        img = canvas(12, 12)
        fill(img, 2, 2, 10, 10, GOLD + (255,))
        w, h, px = img
        for title in ("a\x0bb", "a\x00b\x1f"):
            root = ElementTree.fromstring(trace.to_svg(w, h, px, "silueta", title=title))
            self.assertEqual(root.find(NS + "title").text, "ab")
        self.assertEqual(ElementTree.fromstring(trace.to_svg(w, h, px, "silueta", color="#abc")).find(NS + "path").get("fill"), "#abc")
        for bad in ('red"/><script', "a\x0bb", "", "#12"):
            with self.assertRaisesRegex(ValueError, "color: .* is not #rgb, #rrggbb or a color name"):
                trace.to_svg(w, h, px, "silueta", color=bad)

    def test_reduction_rounds_up_and_scales_each_axis(self):
        img = canvas(1023, 20)
        fill(img, 0, 0, 501, 20, GOLD + (255,))
        svg = trace.to_svg(*img, "silueta", max_side=512, curves=False, smooth_passes=0, dp_tol=0)
        self.assertEqual(ElementTree.fromstring(svg).get("viewBox"), "0 0 1023 20")
        d = paths(svg)[0].get("d")
        xs = sorted({float(m) for m in re.findall(r"[ML]([\d.]+) ", d)})
        ys = sorted({float(m) for m in re.findall(r"[ML][\d.]+ ([\d.]+)", d)})
        self.assertEqual(ys, [0.0, 20.0])  # y is scaled by 20/10, x by 1023/511: each axis apart
        self.assertEqual(xs[0], 0.0)
        # reduced by 2 (ceil of 1023/512), not left at 1:1: the edge lands on the coarse grid
        self.assertLess(abs(xs[1] * 511 / 1023 - round(xs[1] * 511 / 1023)), 0.01)
        self.assertNotEqual(xs[1], 501.0)

    def test_bad_options_say_why(self):
        w, h, px = logo()
        with self.assertRaisesRegex(ValueError, "mode must be one of color, mono, silueta"):
            trace.to_svg(w, h, px, "otro")
        with self.assertRaisesRegex(ValueError, "'rojo' is not a color like #rrggbb"):
            trace.to_svg(w, h, px, palette=["rojo"])
        with self.assertRaisesRegex(ValueError, "do not fit a 5x5"):
            trace.to_svg(5, 5, px)
        with self.assertRaisesRegex(ValueError, "ncolores must be between 1 and 64"):
            trace.to_svg(w, h, px, ncolores=0)

    def test_colors_have_a_cap(self):
        w, h, px = logo()
        with self.assertRaisesRegex(ValueError, "ncolores must be between 1 and 64 .got 65"):
            trace.to_svg(w, h, px, ncolores=trace.MAX_COLORS + 1)
        trace.to_svg(w, h, px, ncolores=trace.MAX_COLORS)

    def test_a_side_shorter_than_the_reduction_factor_still_traces(self):
        for w, h in ((3, 2000), (1, 600), (2000, 2)):
            img = canvas(w, h, (10, 20, 30, 255))
            svg = trace.to_svg(w, h, img[2], max_side=100, min_island=0, smooth_passes=0, dp_tol=0)
            self.assertIn('viewBox="0 0 %d %d"' % (w, h), svg)
            ElementTree.fromstring(svg)  # well-formed, and no IndexError on the way

    # ---- leves de la fase 3 (R1) y de la tercera tanda ----

    def test_mono_keeps_l_t_diagonal_strokes_and_the_tips(self):
        def mono(img):
            return paths(trace.to_svg(*img, "mono", dp_tol=0.5, min_island=2, curves=False))
        l_img = canvas(40, 40)
        fill(l_img, 5, 5, 6, 30, (0, 0, 0, 255))
        fill(l_img, 5, 29, 30, 30, (0, 0, 0, 255))
        t_img = canvas(40, 40)
        fill(t_img, 5, 10, 35, 11, (0, 0, 0, 255))
        fill(t_img, 20, 10, 21, 35, (0, 0, 0, 255))
        diag = canvas(40, 40)
        for i in range(30):
            fill(diag, 5 + i, 5 + i, 6 + i, 6 + i, (0, 0, 0, 255))
        for name, img, area in (("L", l_img, 49), ("T", t_img, 54)):
            with self.subTest(name):
                ps = mono(img)
                self.assertEqual(len(ps), 1)
                self.assertEqual(evenodd_area(ps[0].get("d"), 40), area)  # tips included, nothing added
        d = "".join(p.get("d") for p in paths(trace.to_svg(*diag, "mono", dp_tol=0, min_island=0, curves=False)))
        self.assertGreaterEqual(d.count("M"), 25, "the diagonal survives as its pixels")
        self.assertLessEqual(evenodd_area(d, 40), 30, "and is not widened beyond the original")

    def test_mono_does_not_bring_back_burrs_or_specks_next_to_a_thick_block(self):
        img = canvas(30, 20)
        fill(img, 3, 8, 27, 18, (0, 0, 0, 255))
        for x in (3, 5, 8, 10, 12, 15):  # burrs on top of the block: "#.#..#.#.#..#...#"
            fill(img, x, 7, x + 1, 8, (0, 0, 0, 255))
        fill(img, 20, 2, 21, 3, (0, 0, 0, 255))  # a lone speck
        d = paths(trace.to_svg(*img, "mono", dp_tol=0, min_island=0, curves=False, smooth_passes=1))[0].get("d")
        self.assertEqual(d.count("M"), 1)
        self.assertLessEqual(evenodd_area(d, 30), 24 * 10)

    def test_mono_refuses_a_single_opaque_color_instead_of_a_filled_rectangle(self):
        with self.assertRaisesRegex(ValueError, "one opaque color"):
            trace.to_svg(*canvas(8, 8, GOLD + (255,)), "mono")
        self.assertEqual(len(paths(trace.to_svg(*canvas(8, 8, GOLD + (255,)), "mono", ink=[0], min_island=1))), 1)

    def test_mono_warns_when_the_ink_is_most_of_the_image(self):
        img = canvas(40, 40, (20, 20, 20, 255))  # dark frame, light inside: the light is taken for ink
        fill(img, 3, 3, 37, 37, (240, 240, 240, 255))
        with self.assertWarnsRegex(UserWarning, "frame or the background"):
            trace.to_svg(*img, "mono", ncolores=2)
        ok = canvas(40, 40, (250, 250, 250, 255))
        fill(ok, 10, 10, 20, 20, (20, 20, 20, 255))
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            trace.to_svg(*ok, "mono", ncolores=2)

    def test_color_and_silueta_refuse_an_empty_svg_too(self):
        img = canvas(20, 20)
        fill(img, 5, 5, 15, 15, GOLD + (255,))
        for mode in ("color", "silueta"):
            with self.assertRaisesRegex(ValueError, "no shape left"):
                trace.to_svg(*img, mode, min_island=100000)
        self.assertEqual(paths(trace.to_svg(*canvas(8, 8), "color")), [], "an empty drawing still gives an empty SVG")

    def test_a_sample_that_misses_the_opaque_pixels_still_gives_a_palette(self):
        img = canvas(400, 400)
        fill(img, 3, 3, 4, 4, GOLD + (255,))  # one opaque pixel, off the 1-in-8 sample
        self.assertEqual(trace.extract_palette(*img[:2], img[2], 2), ["#b8862b"])
        svg = trace.to_svg(*img, "color", min_island=0, smooth_passes=0, dp_tol=0)
        self.assertEqual(len(paths(svg)), 1)

    def test_an_explicit_empty_ink_has_its_own_error(self):
        img = canvas(20, 20)
        fill(img, 5, 5, 15, 15, GOLD + (255,))
        with self.assertRaisesRegex(ValueError, "ink: the list is empty"):
            trace.to_svg(*img, "mono", ink=[])


if __name__ == "__main__":
    unittest.main()
