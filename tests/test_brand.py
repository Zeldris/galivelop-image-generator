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


if __name__ == "__main__":
    unittest.main()
