"""`gimg brand` (gimg/brand.py): matte, trace and wordmark on tiny synthetic PNGs; the wordmark needs rsvg-convert and a font."""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from xml.etree import ElementTree
from xml.sax.saxutils import escape
from pathlib import Path
from unittest import mock

from gimg import brand, cli, png
from gimg.errors import GimgError


def _font():
    for cand in (os.path.expanduser("~/.local/share/fonts/galivelop/Cinzel[wght].ttf"),):
        if os.path.exists(cand):
            return cand
    if shutil.which("fc-match"):
        done = subprocess.run(["fc-match", "-f", "%{file}", "sans"], capture_output=True, text=True)
        if done.returncode == 0 and done.stdout.strip().lower().endswith((".ttf", ".otf")):
            return done.stdout.strip()
    return None


FONT = _font()
HAS_WORDMARK = bool(shutil.which("rsvg-convert") and FONT)


def square_png(path, bg=(20, 90, 40), fg=(250, 200, 30), size=24, alpha=255):
    """A `fg` square centered on a flat `bg`."""
    rgba = bytearray()
    for y in range(size):
        for x in range(size):
            inside = size // 4 <= x < size - size // 4 and size // 4 <= y < size - size // 4
            rgba += bytes(fg if inside else bg) + bytes([alpha])
    Path(path).write_bytes(png.rgba_bytes(size, size, rgba))


class BrandBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {"GIMG_LANG": "en"})
        env.start()
        self.addCleanup(env.stop)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()


class MatteTests(BrandBase):
    def test_default_name_has_alpha_suffix_and_original_is_untouched(self):
        src = self.tmp / "logo.png"
        square_png(src)
        before = hashlib.sha256(src.read_bytes()).hexdigest()
        code, out, _ = self.run_cli("brand", "matte", str(src))
        self.assertEqual(code, 0)
        res = self.tmp / "logo-alpha.png"
        self.assertTrue(res.exists())
        self.assertIn(str(res), out)
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(), before)
        w, h, rgba = png.read_rgba(res)
        self.assertEqual(rgba[3], 0)  # the corner is background now
        self.assertEqual(rgba[(12 * w + 12) * 4 + 3], 255)  # the square stays

    def test_json_and_explicit_output(self):
        src, dst = self.tmp / "a.png", self.tmp / "sub" / "b.png"
        square_png(src)
        code, out, _ = self.run_cli("brand", "matte", str(src), "-o", str(dst), "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["out"], str(dst))
        self.assertEqual(data["size"], [24, 24])
        self.assertEqual(data["background"], "#145a28")
        self.assertGreater(data["transparent"], 0.5)
        self.assertTrue(dst.exists())

    def test_output_equal_to_input_is_refused_with_its_reason(self):
        src = self.tmp / "a.png"
        square_png(src)
        before = src.read_bytes()
        code, _, err = self.run_cli("brand", "matte", str(src), "-o", str(src))
        self.assertEqual(code, 1)
        self.assertIn("is the original itself", err)
        self.assertEqual(src.read_bytes(), before)

    def test_bad_tolerance_is_a_gimg_error(self):
        src = self.tmp / "a.png"
        square_png(src)
        with self.assertRaises(GimgError) as cm:
            brand.matte(src, tol=90, soft=10)
        self.assertEqual(cm.exception.code, "brand.bad_option")
        code, _, err = self.run_cli("brand", "matte", str(src), "--tol", "90", "--soft", "10")
        self.assertEqual(code, 1)
        self.assertIn("invalid option", err)
        self.assertIn("t0 and t1", err)
        self.assertFalse((self.tmp / "a-alpha.png").exists())

    def test_missing_file_reports_the_path(self):
        code, _, err = self.run_cli("brand", "matte", str(self.tmp / "nope.png"))
        self.assertEqual(code, 1)
        self.assertIn("nope.png", err)

    def test_a_file_that_is_no_png_is_refused_with_its_reason(self):
        src = self.tmp / "roto.png"
        src.write_bytes(b"not a png at all")
        with self.assertRaises(GimgError) as cm:
            brand.matte(src)
        self.assertEqual(cm.exception.code, "png.invalid")
        code, _, err = self.run_cli("brand", "matte", str(src))
        self.assertEqual(code, 1)
        self.assertIn("roto.png", err)
        self.assertIn("not a PNG", err)
        self.assertFalse((self.tmp / "roto-alpha.png").exists())

    def test_wordmark_and_system_without_font_are_usage_errors(self):
        src = self.tmp / "a.png"
        square_png(src)
        for argv in (("brand", "wordmark", "Galivelop"), ("brand", "system", str(src))):
            with self.subTest(cmd=argv[1]):
                code, _, err = self.run_cli(*argv)
                self.assertEqual(code, 2)
                self.assertIn("--font", err)
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["a.png"])


class WriteTests(BrandBase):
    def test_output_has_the_mode_of_a_plain_file(self):
        src = self.tmp / "logo.png"
        square_png(src)
        brand.matte(str(src))
        mask = os.umask(0o022)
        os.umask(mask)
        self.assertEqual((self.tmp / "logo-alpha.png").stat().st_mode & 0o777, 0o666 & ~mask)

    def test_a_write_that_fails_is_a_gimg_error_with_its_reason(self):
        src = self.tmp / "logo.png"
        square_png(src)
        (self.tmp / "afile").write_text("x")
        with self.assertRaises(GimgError) as cm:
            brand.matte(str(src), str(self.tmp / "afile" / "out.png"))
        self.assertEqual(cm.exception.code, "brand.write_failed")
        self.assertIn("afile", cm.exception.params["path"])
        code, _, err = self.run_cli("brand", "matte", str(src), "-o", str(self.tmp / "afile" / "out.png"))
        self.assertEqual(code, 1)
        self.assertIn("could not write", err)


class TraceTests(BrandBase):
    def test_trace_writes_svg_next_to_png(self):
        src = self.tmp / "logo.png"
        rgba = bytearray(24 * 24 * 4)
        for y in range(6, 18):
            for x in range(6, 18):
                rgba[(y * 24 + x) * 4:(y * 24 + x) * 4 + 4] = bytes((250, 200, 30, 255))
        src.write_bytes(png.rgba_bytes(24, 24, rgba))
        code, out, _ = self.run_cli("brand", "trace", str(src), "--mode", "silhouette", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        svg = (self.tmp / "logo.svg").read_text()
        self.assertEqual(data["out"], str(self.tmp / "logo.svg"))
        self.assertTrue(svg.startswith("<svg"))
        self.assertEqual(data["paths"], 1)
        self.assertFalse(data["opaque_background"])
        self.assertTrue(src.exists())

    def test_matte_flag_removes_an_opaque_background(self):
        src = self.tmp / "logo.png"
        square_png(src)
        _, out, _ = self.run_cli("brand", "trace", str(src), "--mode", "silhouette", "--json")
        self.assertTrue(json.loads(out)["opaque_background"])
        plain = (self.tmp / "logo.svg").read_text()
        code, out, _ = self.run_cli("brand", "trace", str(src), "--mode", "silhouette", "--matte", "--json",
                                    "-o", str(self.tmp / "m.svg"))
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["matted"])
        # without --matte the silhouette is the whole canvas; with it, only the inner square
        self.assertIn("M0 0L24 0L24 24L0 24", plain)
        self.assertNotIn("L24 24", (self.tmp / "m.svg").read_text())

    def test_text_output_warns_about_an_opaque_png(self):
        src = self.tmp / "logo.png"
        square_png(src)
        _, out, _ = self.run_cli("brand", "trace", str(src))
        self.assertIn("--matte", out)

    def test_palette_and_colors_exclude_each_other(self):
        src = self.tmp / "logo.png"
        square_png(src)
        code, _, err = self.run_cli("brand", "trace", str(src), "--palette", "#fff", "--colors", "2")
        self.assertEqual(code, 1)
        self.assertIn("exclude each other", err)

    def test_zero_colors_with_a_palette_is_still_exclusive(self):
        src = self.tmp / "logo.png"
        square_png(src)
        with self.assertRaises(GimgError) as cm:
            brand.trace(str(src), palette="#fff", colors=0)
        self.assertIn("exclude each other", cm.exception.params["reason"])

    def test_bad_palette_color_names_the_color(self):
        src = self.tmp / "logo.png"
        square_png(src)
        code, _, err = self.run_cli("brand", "trace", str(src), "--palette", "#12345g")
        self.assertEqual(code, 1)
        self.assertIn("#12345g", err)

    def test_palette_colors_end_up_in_the_svg(self):
        src = self.tmp / "logo.png"
        square_png(src)
        code, _, _ = self.run_cli("brand", "trace", str(src), "--palette", "#145a28,#fac81e")
        self.assertEqual(code, 0)
        svg = (self.tmp / "logo.svg").read_text().lower()
        self.assertIn("#145a28", svg)
        self.assertIn("#fac81e", svg)


class WordmarkTests(BrandBase):
    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_wordmark_is_paths_without_text(self):
        dst = self.tmp / "wm.svg"
        code, out, _ = self.run_cli("brand", "wordmark", "TARKOR", "--font", FONT, "-o", str(dst), "--json")
        self.assertEqual(code, 0)
        svg = dst.read_text()
        self.assertNotIn("<text", svg)
        self.assertNotIn("font-family", svg)
        self.assertTrue(svg.startswith("<svg"))
        self.assertRegex(svg, r"<path [^>]*d=\"M")
        self.assertIsNotNone(re.search(r'viewBox="0 0 \d+ \d+"', svg))
        data = json.loads(out)
        self.assertEqual(data["out"], str(dst))
        self.assertEqual(data["text"], "TARKOR")
        self.assertGreater(data["size"][0], data["size"][1])

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_spacing_widens_the_wordmark(self):
        tight = brand.wordmark("AVE", FONT, str(self.tmp / "a.svg"), spacing=0.0)
        wide = brand.wordmark("AVE", FONT, str(self.tmp / "b.svg"), spacing=0.5)
        self.assertGreater(wide["size"][0], tight["size"][0] + 50)

    @unittest.skipUnless(shutil.which("rsvg-convert") and os.path.exists(
        os.path.expanduser("~/.local/share/fonts/galivelop/Cinzel[wght].ttf")), "needs rsvg-convert and Cinzel")
    def test_weight_of_a_variable_font_is_applied(self):
        cinzel = os.path.expanduser("~/.local/share/fonts/galivelop/Cinzel[wght].ttf")
        light = brand.wordmark("TARKOR", cinzel, str(self.tmp / "l.svg"), weight=400)
        bold = brand.wordmark("TARKOR", cinzel, str(self.tmp / "b.svg"), weight=800)
        self.assertGreater(bold["size"][0], light["size"][0] + 40)

    def test_a_file_that_is_no_font_is_refused_with_its_reason(self):
        code, _, err = self.run_cli("brand", "wordmark", "X", "--font", __file__)
        self.assertEqual(code, 1)
        self.assertIn("not a TrueType or OpenType font", err)

    def test_missing_tool_message(self):
        font = self.tmp / "fake.ttf"
        font.write_bytes(self._tiny_font())
        with mock.patch.dict(os.environ, {"PATH": ""}):
            code, _, err = self.run_cli("brand", "wordmark", "X", "--font", str(font), "-o", str(self.tmp / "o.svg"))
        self.assertEqual(code, 1)
        self.assertIn('the tool "rsvg-convert" is missing', err)
        self.assertFalse((self.tmp / "o.svg").exists())

    def test_unreadable_font_and_empty_text(self):
        code, _, err = self.run_cli("brand", "wordmark", "X", "--font", str(self.tmp / "none.ttf"))
        self.assertEqual(code, 1)
        self.assertIn("none.ttf", err)
        code, _, err = self.run_cli("brand", "wordmark", "  ", "--font", __file__)
        self.assertEqual(code, 1)
        self.assertIn("the name text is missing", err)

    def test_bad_weight_is_refused_with_its_reason(self):
        with self.assertRaises(GimgError) as cm:
            brand.wordmark("X", __file__, weight=5000)
        self.assertEqual(cm.exception.code, "brand.bad_option")
        self.assertIn("weight", cm.exception.params["reason"])

    def _tiny_path(self):
        font = self.tmp / "tiny.ttf"
        font.write_bytes(self._tiny_font())
        return str(font)

    def _fake_rsvg(self, rgba_fill, size=(8, 8)):
        """Patch the tool as present and make it write an 8x8 PNG whose every pixel is `rgba_fill`."""
        def fake(argv, env):
            Path(argv[-2]).write_bytes(png.rgba_bytes(size[0], size[1], bytes(rgba_fill) * (size[0] * size[1])))
        for target in (mock.patch.object(brand.shutil, "which", return_value="/bin/rsvg-convert"),
                       mock.patch.object(brand, "_rsvg", fake)):
            target.start()
            self.addCleanup(target.stop)

    def test_a_font_cannot_be_overwritten_as_the_output(self):
        font = self._tiny_path()
        with self.assertRaises(GimgError) as cm:
            brand.wordmark("X", font, font)
        self.assertEqual(cm.exception.code, "brand.out_is_input")
        self.assertEqual(Path(font).read_bytes(), self._tiny_font())

    def test_text_that_cannot_fit_the_pixel_limit_is_refused(self):
        with self.assertRaises(GimgError) as cm:
            brand.wordmark("A" * brand.MAX_TEXT, self._tiny_path(), str(self.tmp / "o.svg"), spacing=2)
        self.assertEqual(cm.exception.code, "brand.wordmark_no_fit")
        self.assertFalse((self.tmp / "o.svg").exists())

    def test_ink_on_the_edge_of_the_drawing_is_refused(self):
        self._fake_rsvg((0, 0, 0, 255))  # every pixel inked, so the text was cut off
        with self.assertRaises(GimgError) as cm:
            brand.wordmark("X", self._tiny_path(), str(self.tmp / "o.svg"))
        self.assertEqual(cm.exception.code, "brand.wordmark_no_fit")
        self.assertIn("edge", cm.exception.params["reason"])

    def test_a_font_without_those_letters_is_empty_wordmark(self):
        self._fake_rsvg((0, 0, 0, 0))
        with self.assertRaises(GimgError) as cm:
            brand.wordmark("X", self._tiny_path(), str(self.tmp / "o.svg"))
        self.assertEqual(cm.exception.code, "brand.empty_wordmark")
        self.assertEqual(cm.exception.params["family"], "Tiny")

    def test_a_failing_tool_reports_its_last_error_line(self):
        done = subprocess.CompletedProcess([], 1, b"", b"warning\nCould not open the thing\n")
        with mock.patch.object(brand.shutil, "which", return_value="/bin/rsvg-convert"), \
                mock.patch.object(brand.subprocess, "run", return_value=done):
            with self.assertRaises(GimgError) as cm:
                brand.wordmark("X", self._tiny_path(), str(self.tmp / "o.svg"))
        self.assertEqual(cm.exception.code, "brand.tool_failed")
        self.assertEqual(cm.exception.params["reason"], "Could not open the thing")

    def test_control_characters_are_dropped_from_the_text(self):
        seen = {}
        def fake(argv, env):
            seen["svg"] = Path(argv[-1]).read_text()
            Path(argv[-2]).write_bytes(png.rgba_bytes(3, 3, bytes(36)))
        with mock.patch.object(brand.shutil, "which", return_value="/bin/rsvg-convert"), \
                mock.patch.object(brand, "_rsvg", fake):
            with self.assertRaises(GimgError):  # empty ink: only the text sent to the tool matters here
                brand.wordmark("A\x00\x1bB\tC\n", self._tiny_path(), str(self.tmp / "o.svg"))
        self.assertIn(">AB C<", seen["svg"])
        self.assertNotIn("\x00", seen["svg"])
        self.assertNotIn("\x1b", seen["svg"])

    @staticmethod
    def _tiny_font():
        """An sfnt header with a name table holding the family "Tiny": enough for brand to accept the file."""
        import struct
        text = "Tiny".encode("utf-16-be")
        table = struct.pack(">HHH", 0, 1, 18) + struct.pack(">6H", 3, 1, 0x409, 1, len(text), 0) + text
        head = b"\x00\x01\x00\x00" + struct.pack(">HHHH", 1, 16, 0, 0)
        return head + struct.pack(">4sIII", b"name", 0, 28, len(table)) + table


def path_svg(w, h, color="currentColor", title=""):
    """An SVG like the ones of `brand trace` and `brand wordmark`: one rectangle path filling a ``w`` x ``h`` viewBox."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img">%s<path fill="%s" fill-rule="evenodd" '
            'd="M0 0L%d 0L%d %dL0 %dZ"/></svg>\n' % (w, h, "<title>%s</title>" % title if title else "", color, w, w, h, h))


def box_of(svg_text):
    """``[(x, y, w, h)]`` of the scaled groups of a lockup: where each rectangle ends up (all start at 0, 0)."""
    out = []
    for m in re.finditer(r'<g transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)">.*?d="M0 0L(\d+) 0L\d+ (\d+)', svg_text, re.S):
        x, y, k, w, h = (float(v) for v in m.groups())
        out.append((x, y, w * k, h * k))
    return out


class LockupTests(BrandBase):
    def setUp(self):
        super().setUp()
        self.emblem, self.word = self.tmp / "e.svg", self.tmp / "w.svg"
        self.emblem.write_text(path_svg(100, 100, "#b8862b", "emblem"))
        self.word.write_text(path_svg(400, 50, title="word"))

    def lock(self, *extra):
        out = self.tmp / "l.svg"
        code, text, err = self.run_cli("brand", "lockup", str(self.emblem), str(self.word), "-o", str(out), "--json", *extra)
        return code, (json.loads(text) if code == 0 else err), out

    def test_h_puts_the_wordmark_right_and_centered_with_the_sheet_proportions(self):
        code, data, out = self.lock()
        self.assertEqual(code, 0)
        (ex, ey, ew, eh), (wx, wy, ww, wh) = box_of(out.read_text())
        self.assertAlmostEqual(wh, 45, places=2)  # cap 0.45 of the diameter
        self.assertAlmostEqual(wx - (ex + ew), 25, places=2)  # gap 0.25 of the diameter
        self.assertAlmostEqual(wy + wh / 2, ey + eh / 2, places=2)
        self.assertEqual(data["layout"], "h")
        self.assertEqual(data["size"], [485.0, 100.0])
        self.assertEqual(data["paths"], 2)

    def test_v_puts_the_wordmark_below_and_centered(self):
        code, data, out = self.lock("--layout", "v")
        self.assertEqual(code, 0)
        (ex, ey, ew, eh), (wx, wy, ww, wh) = box_of(out.read_text())
        self.assertAlmostEqual(ww, 160, places=2)  # width 1.6 diameters
        self.assertAlmostEqual(wy - (ey + eh), 25, places=2)
        self.assertAlmostEqual(wx + ww / 2, ex + ew / 2, places=2)
        self.assertEqual(data["size"], [160.0, 100 + 25 + 20.0])

    def test_a_wordmark_wider_than_the_emblem_makes_the_canvas_as_wide_as_it_is(self):
        code, data, out = self.lock("--layout", "v")
        (ex, _, ew, _), (wx, _, ww, _) = box_of(out.read_text())
        self.assertGreater(ww, ew)
        self.assertAlmostEqual(ex, 30, places=2)  # the emblem is the one centered in the wider canvas
        self.assertAlmostEqual(wx, 0, places=2)

    def test_an_emblem_wider_than_the_wordmark_keeps_the_wordmark_centered(self):
        code, data, out = self.lock("--layout", "v", "--width", "0.5")
        (ex, _, ew, _), (wx, _, ww, _) = box_of(out.read_text())
        self.assertLess(ww, ew)
        self.assertAlmostEqual(ex, 0, places=2)
        self.assertAlmostEqual(wx, 25, places=2)
        self.assertEqual(data["size"][0], 100.0)

    def test_a_taller_wordmark_in_h_centers_the_emblem_vertically(self):
        code, data, out = self.lock("--cap", "2")
        (ex, ey, ew, eh), (wx, wy, ww, wh) = box_of(out.read_text())
        self.assertAlmostEqual(wh, 200, places=2)
        self.assertAlmostEqual(ey, 50, places=2)
        self.assertEqual(data["size"][1], 200.0)

    def test_no_text_no_image_and_currentcolor_survives(self):
        code, _, out = self.lock()
        svg = out.read_text()
        self.assertNotIn("<text", svg)
        self.assertNotIn("<image", svg)
        self.assertIn('fill="currentColor"', svg)
        self.assertIn('fill="#b8862b"', svg)
        self.assertNotIn("<title>emblem", svg)  # the inner titles are not duplicated

    def test_color_replaces_currentcolor_in_the_wordmark_only(self):
        _, _, out = self.lock("--color", "#f1e4d0")
        svg = out.read_text()
        self.assertNotIn("currentColor", svg)
        self.assertIn('fill="#f1e4d0"', svg)

    def test_a_svg_with_text_is_refused_with_its_reason(self):
        self.word.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9"><text>X</text></svg>')
        code, err, _ = self.lock()
        self.assertEqual(code, 1)
        self.assertIn("does not work for the lockup", err)
        self.assertIn("only paths", err)
        self.assertFalse((self.tmp / "l.svg").exists())

    def test_a_title_with_markup_looking_text_is_not_refused(self):
        ns = "{http://www.w3.org/2000/svg}"
        for name in ("A one = b", "x id = y", "R&D onload = 1 <text>"):
            for piece in (self.emblem, self.word):
                piece.write_text(path_svg(100, 50, title=escape(name)))  # as gimg writes a title
            brand.lockup(self.emblem, self.word, self.tmp / "l.svg", title=name, force=True)
            self.assertEqual(ElementTree.fromstring((self.tmp / "l.svg").read_text()).find(ns + "title").text, name)

    def test_a_forbidden_attribute_is_still_refused_next_to_a_title(self):
        self.word.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9"><title>t</title><path id="a" d="M0 0L9 9Z"/></svg>')
        code, err, _ = self.lock()
        self.assertEqual(code, 1)
        self.assertIn("only paths", err)

    def test_a_viewbox_float_cannot_read_is_bad_svg(self):
        for vb in ("0 0 1e - 5", "0 0 1e 5", "0 0 1e999 1", "0 0 -- 5"):
            self.word.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s"><path d="M0 0L9 9Z"/></svg>' % vb)
            code, err, _ = self.lock()
            self.assertEqual(code, 1, vb)
            self.assertIn("with a viewBox" if "e999" not in vb else "no area", err)

    def test_control_characters_are_dropped_from_the_lockup_title(self):
        brand.lockup(self.emblem, self.word, self.tmp / "l.svg", title="Tar\u0001kor")
        root = ElementTree.fromstring((self.tmp / "l.svg").read_text())  # a raw control character is not XML
        self.assertEqual(root.find("{http://www.w3.org/2000/svg}title").text, "Tarkor")

    def test_a_file_that_is_no_svg_is_refused(self):
        self.emblem.write_text("nope")
        code, err, _ = self.lock()
        self.assertEqual(code, 1)
        self.assertIn("with a viewBox", err)

    def test_bad_options_and_inputs_are_not_overwritten(self):
        code, err, _ = self.lock("--cap", "0")
        self.assertEqual(code, 1)
        self.assertIn("cap 0.01-5", err)
        code, err, _ = self.lock("--color", "red;x")
        self.assertEqual(code, 1)
        self.assertIn("is not #rgb", err)
        before = self.emblem.read_bytes()
        code, _, err = self.run_cli("brand", "lockup", str(self.emblem), str(self.word), "-o", str(self.emblem))
        self.assertEqual(code, 1)
        self.assertIn("is the original itself", err)
        self.assertEqual(self.emblem.read_bytes(), before)

    def test_styles_ids_links_and_handlers_are_refused_with_their_reason(self):
        for body in ('<style>p{}</style><path d="M0 0L9 9Z"/>', '<path id="a" d="M0 0L9 9Z"/>',
                     '<path onclick="x()" d="M0 0L9 9Z"/>', '<a href="u"><path d="M0 0L9 9Z"/></a>'):
            self.word.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">%s</svg>' % body)
            code, err, _ = self.lock()
            self.assertEqual(code, 1, body)
            self.assertIn("does not work for the lockup", err)
            self.assertIn("only paths", err)

    def test_a_lockup_used_as_a_piece_is_placed_by_its_viewbox_not_a_wrong_box(self):
        code, _, out = self.lock()
        self.assertEqual(code, 0)
        self.assertEqual(brand._read_svg(out)["box"], tuple(float(v) for v in re.search(
            r'viewBox="([^"]+)"', out.read_text()).group(1).split()[:2]) + (485.0, 100.0))

    def test_lockup_does_not_overwrite_without_force(self):
        code, _, out = self.lock()
        self.assertEqual(code, 0)
        out.write_text("mine")
        code, err, _ = self.lock()
        self.assertEqual(code, 1)
        self.assertIn("l.svg", err)
        self.assertEqual(out.read_text(), "mine")
        with self.assertRaises(GimgError) as cm:
            brand.lockup(self.emblem, self.word, out)
        self.assertEqual(cm.exception.code, "brand.exists")
        code, _, _ = self.lock("--force")
        self.assertEqual(code, 0)
        self.assertIn("<path", out.read_text())

    def test_text_output_line(self):
        code, out, _ = self.run_cli("brand", "lockup", str(self.emblem), str(self.word), "-o", str(self.tmp / "t.svg"))
        self.assertEqual(code, 0)
        self.assertIn("layout h, 485.0x100.0, 2 paths", out)


class SlugTests(unittest.TestCase):
    def test_accents_and_symbols(self):
        self.assertEqual(brand.slugify("Tarkor"), "tarkor")
        self.assertEqual(brand.slugify("Ñandú  del Sur!"), "nandu-del-sur")
        self.assertEqual(brand.slugify("Café-Ünïcode 2"), "cafe-unicode-2")
        self.assertEqual(brand.slugify("日本"), "")

    def test_letters_that_do_not_decompose_are_transliterated(self):
        self.assertEqual(brand.slugify("Bjørk Straße"), "bjork-strasse")
        self.assertEqual(brand.slugify("Æther Đuro Łódź"), "aether-duro-lodz")


class InkBoxTests(unittest.TestCase):
    def test_a_transform_makes_the_box_unknown(self):
        self.assertIsNone(brand._ink_box('<g transform="translate(5 5)"><path d="M0 0L10 0L10 10Z"/></g>'))
        self.assertEqual(brand._ink_box('<path d="M0 0L10 0L10 10Z"/>'), (0, 0, 10, 10))

    def test_the_box_follows_the_curve_not_its_control_points(self):
        # control points reach y=-40 and y=140, but a cubic with them only goes to 0.75 of that
        box = brand._ink_box('<path d="M0 50C0 -40 100 -40 100 50C100 140 0 140 0 50Z"/>')
        self.assertAlmostEqual(box[1], 50 - 90 * 0.75, places=3)
        self.assertAlmostEqual(box[3], 50 + 90 * 0.75, places=3)
        self.assertEqual((box[0], box[2]), (0, 100))


class SystemTests(BrandBase):
    def setUp(self):
        super().setUp()
        self.src = self.tmp / "emb.png"
        square_png(self.src, size=48)
        self.out = self.tmp / "out"

    def system(self, *extra, name="Tarkor"):
        return self.run_cli("brand", "system", str(self.src), "--name", name, "--font", FONT or "x", "--out-dir", str(self.out),
                            *extra)

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_writes_the_seven_files_and_leaves_the_original_alone(self):
        before = hashlib.sha256(self.src.read_bytes()).hexdigest()
        code, out, err = self.system("--json")
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        names = sorted(p.name for p in self.out.iterdir())
        self.assertEqual(names, sorted("tarkor-" + n for n in brand.SYSTEM_FILES))
        self.assertEqual(data["slug"], "tarkor")
        self.assertEqual(data["files"]["lockup-v.svg"], str(self.out / "tarkor-lockup-v.svg"))
        self.assertEqual(hashlib.sha256(self.src.read_bytes()).hexdigest(), before)
        for n in ("emblema.svg", "emblema-mono.svg", "wordmark.svg", "lockup-h.svg", "lockup-v.svg"):
            svg = (self.out / ("tarkor-" + n)).read_text()
            self.assertNotIn("<text", svg)
            self.assertNotIn("<image", svg)
        self.assertIn("currentColor", (self.out / "tarkor-emblema-mono.svg").read_text())
        w, h, rgba = png.read_rgba(self.out / "tarkor-contactos.png")
        self.assertEqual((w, h), tuple(data["contact_size"]))
        self.assertEqual(rgba[:3], bytes((0xf1, 0xe4, 0xd0)))  # light on the left
        self.assertEqual(rgba[(w - 1) * 4:(w - 1) * 4 + 3], bytes((0x0f, 0x14, 0x28)))  # dark on the right
        _, _, alpha = png.read_rgba(self.out / "tarkor-emblema-alpha.png")
        self.assertEqual(alpha[3], 0)

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_mono_and_margin_reach_both_lockups(self):
        code, _, err = self.system("--mono", "--margin", "0.25")
        self.assertEqual(code, 0, err)
        for layout in ("h", "v"):
            with self.subTest(layout=layout):
                ref = self.tmp / ("ref-%s.svg" % layout)
                brand.lockup(self.out / "tarkor-emblema-mono.svg", self.out / "tarkor-wordmark.svg", ref, layout,
                             margin=0.25, title="Tarkor")
                got = (self.out / ("tarkor-lockup-%s.svg" % layout)).read_text()
                self.assertEqual(got, ref.read_text())
        self.assertNotEqual((self.out / "tarkor-emblema-mono.svg").read_text(),
                            (self.out / "tarkor-emblema.svg").read_text())  # else the check above proves nothing
        plain = self.tmp / "plain"
        self.assertEqual(self.run_cli("brand", "system", str(self.src), "--name", "Tarkor", "--font", FONT,
                                      "--out-dir", str(plain))[0], 0)
        ref = self.tmp / "ref-color.svg"
        brand.lockup(plain / "tarkor-emblema.svg", plain / "tarkor-wordmark.svg", ref, "h", title="Tarkor")
        self.assertEqual((plain / "tarkor-lockup-h.svg").read_text(), ref.read_text())

    def test_a_margin_out_of_range_is_refused_with_its_reason(self):
        code, _, err = self.system("--margin", "3")
        self.assertEqual(code, 1)
        self.assertIn("margin 0-2", err)

    @unittest.skipUnless(shutil.which("rsvg-convert"), "needs rsvg-convert")
    def test_the_default_spacing_is_the_family_one(self):
        self.assertEqual(brand.SPACING, 0.01)
        big = str(Path(brand.__file__).parent / "ui" / "fonts" / "BigShouldersDisplay.ttf")
        code, out, err = self.run_cli("brand", "wordmark", "AVE", "--font", big, "-o", str(self.tmp / "d.svg"), "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["spacing"], 0.01)
        code, out, _ = self.run_cli("brand", "system", str(self.src), "--name", "Tarkor", "--font", big, "--out-dir",
                                    str(self.out), "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["spacing"], 0.01)
        made = (self.out / "tarkor-wordmark.svg").read_text()
        brand.wordmark("TARKOR", big, str(self.tmp / "ref.svg"), spacing=0.01, title="Tarkor")
        self.assertEqual(made, (self.tmp / "ref.svg").read_text())

    @unittest.skipUnless(shutil.which("rsvg-convert"), "needs rsvg-convert")
    def test_the_default_spacing_depends_on_the_font_family(self):
        fonts = Path(brand.__file__).parent / "ui" / "fonts"
        big, other = str(fonts / "BigShouldersDisplay.ttf"), str(fonts / "Literata.ttf")
        self.assertEqual(brand.wordmark("AVE", big, str(self.tmp / "b.svg"))["spacing"], 0.01)
        self.assertEqual(brand.wordmark("AVE", other, str(self.tmp / "o.svg"))["spacing"], 0.12)
        self.assertEqual(brand.wordmark("AVE", other, str(self.tmp / "e.svg"), spacing=0.3)["spacing"], 0.3)
        self.assertEqual(brand.wordmark("AVE", big, str(self.tmp / "f.svg"), spacing=0.0)["spacing"], 0.0)
        code, out, err = self.run_cli("brand", "wordmark", "AVE", "--font", other, "-o", str(self.tmp / "c.svg"), "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["spacing"], 0.12)
        code, out, err = self.run_cli("brand", "wordmark", "AVE", "--font", other, "--spacing", "0.05", "-o",
                                      str(self.tmp / "d.svg"), "--json")
        self.assertEqual(json.loads(out)["spacing"], 0.05)

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_system_resolves_the_default_spacing_with_the_font(self):
        other = str(Path(brand.__file__).parent / "ui" / "fonts" / "Literata.ttf")
        res = brand.system(self.src, "Tarkor", other, self.out)
        self.assertEqual(res["spacing"], 0.12)

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_text_output_lists_the_files(self):
        code, out, _ = self.system()
        self.assertEqual(code, 0)
        self.assertIn("system 'tarkor'", out)
        self.assertIn("7 files", out)
        self.assertIn(str(self.out / "tarkor-lockup-v.svg"), out)

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_a_folder_that_already_has_the_files_is_not_overwritten_without_force(self):
        self.out.mkdir()
        mine = self.out / "tarkor-lockup-v.svg"
        mine.write_text("mine")
        (self.out / "other.txt").write_text("keep")
        code, _, err = self.system()
        self.assertEqual(code, 1)
        self.assertIn("already has tarkor-lockup-v.svg", err)
        self.assertIn("--force", err)
        self.assertEqual(mine.read_text(), "mine")
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), ["other.txt", "tarkor-lockup-v.svg"])  # nothing else written
        code, out, _ = self.system("--force")
        self.assertEqual(code, 0)
        self.assertNotEqual(mine.read_text(), "mine")
        self.assertEqual((self.out / "other.txt").read_text(), "keep")
        self.assertIn("overwritten: tarkor-lockup-v.svg", out)

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_accents_in_the_name_give_an_ascii_slug_and_the_name_in_capitals(self):
        code, out, err = self.system("--json", name="Ñandú")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["slug"], "nandu")
        self.assertTrue((self.out / "nandu-lockup-h.svg").exists())

    def test_an_out_dir_that_is_a_file_is_refused_before_any_work(self):
        self.out.write_text("x")
        code, _, err = self.system()
        self.assertEqual(code, 1)
        self.assertIn("not a folder", err)
        self.assertEqual(self.out.read_text(), "x")

    def test_a_target_that_is_a_folder_is_refused_even_with_force(self):
        (self.out / "tarkor-lockup-h.svg").mkdir(parents=True)
        code, _, err = self.system("--force")
        self.assertEqual(code, 1)
        self.assertIn("it is a folder", err)
        self.assertEqual([p.name for p in self.out.iterdir()], ["tarkor-lockup-h.svg"])

    def test_bad_wordmark_options_and_font_fail_before_the_long_work(self):
        code, _, err = self.system("--weight", "0")
        self.assertEqual(code, 1)
        self.assertIn("weight 1-1000", err)
        self.assertFalse(self.out.exists())
        code, _, err = self.run_cli("brand", "system", str(self.src), "--name", "Tarkor", "--font", str(self.tmp / "nope.ttf"),
                                    "--out-dir", str(self.out))
        self.assertEqual(code, 1)
        self.assertIn("nope.ttf", err)
        self.assertFalse(self.out.exists())

    def test_a_name_with_no_ascii_letters_is_refused_with_its_reason(self):
        code, _, err = self.system(name="日本")
        self.assertEqual(code, 1)
        self.assertIn("gives no file prefix", err)
        self.assertFalse(self.out.exists())

    def test_an_emblem_with_no_flat_background_is_refused_with_its_reason(self):
        rgba = bytearray()
        for y in range(32):
            for x in range(32):
                rgba += bytes(((x * 8) % 256, (y * 8) % 256, (x * y) % 256, 255))
        self.src.write_bytes(png.rgba_bytes(32, 32, rgba))
        with mock.patch("gimg.brand.shutil.which", return_value="/usr/bin/rsvg-convert"):
            code, _, err = self.system()
        self.assertEqual(code, 1)
        self.assertIn("no flat background to cut out", err)
        self.assertFalse(self.out.exists())

    def test_missing_tool_writes_nothing(self):
        with mock.patch.dict(os.environ, {"PATH": ""}):
            code, _, err = self.system()
        self.assertEqual(code, 1)
        self.assertIn('the tool "rsvg-convert" is missing', err)
        self.assertFalse(self.out.exists())

    def test_the_original_cannot_be_a_target(self):
        target = self.tmp / "tarkor-emblema-alpha.png"
        target.write_bytes(self.src.read_bytes())
        before = target.read_bytes()
        code, _, err = self.run_cli("brand", "system", str(target), "--name", "Tarkor", "--font", FONT or "x", "--out-dir",
                                    str(self.tmp), "--force")
        self.assertEqual(code, 1)
        self.assertIn("is the original itself", err)
        self.assertEqual(target.read_bytes(), before)

    def test_palette_and_colors_exclude_each_other(self):
        with mock.patch("gimg.brand.shutil.which", return_value="/usr/bin/rsvg-convert"):
            code, _, err = self.system("--palette", "#fac81e", "--colors", "3")
        self.assertEqual(code, 1)
        self.assertIn("exclude each other", err)
        self.assertFalse(self.out.exists())


class SquareTests(BrandBase):
    def setUp(self):
        super().setUp()
        self.draw = self.tmp / "ig.svg"
        self.draw.write_text(path_svg(40, 20, "#123456", "ig"))
        self.out = self.tmp / "sq.svg"

    def make(self, **kw):
        args = dict(fill="#7C5CD6", ink="#fbfcfd")
        args.update(kw)
        return brand.square(self.draw, kw.pop("out", self.out), **{k: v for k, v in args.items() if k != "out"})

    def code(self, **kw):
        with self.assertRaises(GimgError) as cm:
            self.make(**kw)
        return cm.exception

    def test_the_square_path_has_the_chamfer_on_the_top_right_only(self):
        res = self.make()
        text = self.out.read_text()
        self.assertIn('viewBox="0 0 128 128"', text)
        self.assertIn('<path fill="#7c5cd6" d="M0 0 H100 L128 28 V128 H0 Z"/>', text)
        self.assertNotIn("rx=", text)
        self.assertNotIn("Gradient", text)
        self.assertEqual(res["out"], str(self.out))
        self.assertEqual(res["pngs"], [])
        self.assertEqual((res["fill"], res["ink"]), ("#7c5cd6", "#fbfcfd"))
        self.assertAlmostEqual(res["contrast"], 4.69, places=1)

    def test_another_chamfer_changes_the_path(self):
        self.make(chamfer=40)
        self.assertIn('d="M0 0 H88 L128 40 V128 H0 Z"', self.out.read_text())

    def test_the_drawing_is_fitted_centered_inside_the_padding_in_the_ink(self):
        self.make()
        text = self.out.read_text()
        self.assertNotIn("#123456", text)
        self.assertNotIn("currentColor", text)
        self.assertIn('fill="#fbfcfd"', text)
        (x, y, w, h), = box_of(text)
        self.assertAlmostEqual(w, 80, places=2)  # 128 - 2 * 24
        self.assertAlmostEqual(h, 40, places=2)
        self.assertAlmostEqual(x, 24, places=2)
        self.assertAlmostEqual(y, 44, places=2)  # centered vertically

    def test_current_color_and_none_are_handled(self):
        self.draw.write_text(path_svg(20, 20).replace('fill="currentColor"', 'fill="currentColor" stroke="none"'))
        self.make()
        text = self.out.read_text()
        self.assertNotIn("currentColor", text)
        self.assertIn('stroke="none"', text)

    def test_attributes_that_only_end_in_fill_are_left_alone(self):
        self.draw.write_text(path_svg(20, 20).replace('fill="currentColor"', 'fill="#123456" data-fill="keep"'))
        self.make()
        text = self.out.read_text()
        self.assertIn('data-fill="keep"', text)
        self.assertNotIn("#123456", text)

    def test_validations_carry_their_code(self):
        for kw in ({"chamfer": -1}, {"chamfer": 65}, {"pad": -1}, {"pad": 49}, {"fill": "red"}, {"ink": "#fff"}, {"fill": None},
                   {"pngs": [0]}, {"pngs": [9000]}):
            exc = self.code(**kw)
            self.assertEqual(exc.code, "brand.bad_square", kw)
        self.assertFalse(self.out.exists())
        self.assertIn("chamfer", str(self.code(chamfer=65)))

    def test_does_not_overwrite_without_force(self):
        self.out.write_text("mine")
        self.assertEqual(self.code().code, "brand.exists")
        self.assertEqual(self.out.read_text(), "mine")
        self.make(force=True)
        self.assertIn("<path", self.out.read_text())

    @unittest.skipUnless(shutil.which("rsvg-convert"), "needs rsvg-convert")
    def test_force_is_all_or_nothing_when_a_png_fails_midway(self):
        old = {self.out: "old svg", self.tmp / "sq-64.png": "old 64", self.tmp / "sq-32.png": "old 32"}
        for path, text in old.items():
            path.write_text(text)
        before = set(self.tmp.iterdir())
        real, calls = brand._rsvg, []

        def flaky(argv, env):
            calls.append(argv)
            if len(calls) == 2:
                raise GimgError("brand.tool_failed", tool="rsvg-convert", reason="boom")
            return real(argv, env)

        with mock.patch.object(brand, "_rsvg", flaky):
            exc = self.code(pngs=[64, 32], force=True)
        self.assertEqual(exc.code, "brand.tool_failed")
        self.assertIn("boom", str(exc))
        self.assertEqual(len(calls), 2)
        for path, text in old.items():
            self.assertEqual(path.read_text(), text)
        self.assertEqual(set(self.tmp.iterdir()), before)  # no temporary files left

    def test_a_failed_final_rename_restores_every_old_file(self):
        old = {self.out: "old svg", self.tmp / "sq-64.png": "old 64", self.tmp / "sq-32.png": "old 32"}
        for path, text in old.items():
            path.write_text(text)
        before = set(self.tmp.iterdir())

        def fake_rsvg(argv, env):
            Path(argv[argv.index("-o") + 1]).write_bytes(b"new png")

        real = os.replace

        def flaky(src, dst, *a, **k):
            if str(dst) == str(self.tmp / "sq-32.png") and str(src).endswith(".png.tmp"):
                raise OSError(28, "No space left")
            return real(src, dst, *a, **k)

        with mock.patch.object(brand, "_rsvg", fake_rsvg), mock.patch.object(brand.shutil, "which", return_value="/x"), \
                mock.patch.object(brand.os, "replace", flaky):
            exc = self.code(pngs=[64, 32], force=True)
        self.assertEqual(exc.code, "brand.write_failed")
        self.assertIn("No space left", str(exc))
        for path, text in old.items():
            self.assertEqual(path.read_text(), text)  # the SVG and the first PNG were not left new
        self.assertEqual(set(self.tmp.iterdir()), before)  # no temporaries or backups left

    def test_default_output_sits_next_to_the_drawing(self):
        res = brand.square(self.draw, None, "#7C5CD6", "#fbfcfd")
        self.assertEqual(res["out"], str(self.tmp / "ig-square.svg"))
        self.assertTrue((self.tmp / "ig-square.svg").exists())

    @unittest.skipUnless(shutil.which("rsvg-convert"), "needs rsvg-convert")
    def test_png_sizes_and_corners(self):
        res = self.make(pngs=[64, 32])
        self.assertEqual(res["pngs"], [str(self.tmp / "sq-64.png"), str(self.tmp / "sq-32.png")])
        w, h, rgba = png.read_rgba(self.tmp / "sq-64.png")
        self.assertEqual((w, h), (64, 64))
        top_right, bottom_left = rgba[((0 * w) + w - 1) * 4:][:4], rgba[((h - 1) * w) * 4:][:4]
        self.assertEqual(top_right[3], 0)  # the chamfer cuts the corner
        self.assertEqual(tuple(bottom_left), (0x7C, 0x5C, 0xD6, 255))
        self.assertEqual(png.read_rgba(self.tmp / "sq-32.png")[:2], (32, 32))

    @unittest.skipUnless(shutil.which("rsvg-convert"), "needs rsvg-convert")
    def test_png_clash_needs_force(self):
        (self.tmp / "sq-64.png").write_bytes(b"x")
        self.assertEqual(self.code(pngs=[64]).code, "brand.exists")
        self.assertFalse(self.out.exists())

    def test_cli(self):
        code, text, err = self.run_cli("brand", "square", str(self.draw), "--fill", "#7C5CD6", "--ink", "#fbfcfd",
                                       "-o", str(self.out), "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(text)["fill"], "#7c5cd6")
        code, text, err = self.run_cli("brand", "square", str(self.draw), "--fill", "#7C5CD6", "--ink", "#7C5CE6",
                                       "-o", str(self.tmp / "b.svg"))
        self.assertEqual(code, 0, err)
        self.assertIn("contrast", text)
        self.assertIn("under 4.5:1", text)
        code, text, err = self.run_cli("brand", "square", str(self.draw), "--fill", "#7C5CD6", "--ink", "#fbfcfd",
                                       "-o", str(self.out))
        self.assertNotEqual(code, 0)
        self.assertIn("already has", err)
        code, text, err = self.run_cli("brand", "square", str(self.draw), "--fill", "#7C5CD6", "--ink", "#fbfcfd",
                                       "--chamfer", "99", "-o", str(self.tmp / "c.svg"))
        self.assertNotEqual(code, 0)
        self.assertIn("chamfer", err)


if __name__ == "__main__":
    unittest.main()
