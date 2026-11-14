"""`gimg tile`: una textura sin costura (media pieza desplazada y la cruz fundida) y su vista 4x4."""
import io
import json
import os
import random
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from gimg import cli, png, tile
from gimg.errors import GimgError


def texture(w=96, h=64, seed=7):
    """A texture that does NOT repeat: a strong gradient (left dark, top light) with a little noise."""
    rnd = random.Random(seed)
    px = bytearray()
    for y in range(h):
        for x in range(w):
            base = 30 + 190 * x / (w - 1)
            top = 40 * (1 - y / (h - 1))
            v = max(0, min(255, int(base * 0.8 + top + rnd.randint(-6, 6))))
            px += bytes((v, (v * 3) // 4, 255 - v, 255))
    return w, h, px


def wrap_edge(w, h, px, axis):
    """Mean abs difference between the last and the first column (axis 'x') or row ('y'), the pair a repeat joins."""
    total = n = 0
    if axis == "x":
        for y in range(h):
            a, b = (y * w + w - 1) * 4, y * w * 4
            total += sum(abs(px[a + c] - px[b + c]) for c in range(3))
            n += 3
    else:
        for x in range(w):
            a, b = ((h - 1) * w + x) * 4, x * 4
            total += sum(abs(px[a + c] - px[b + c]) for c in range(3))
            n += 3
    return total / n


def inner_step(w, h, px):
    """Mean abs difference between neighbours inside the image: what a seamless join should look like."""
    total = n = 0
    for y in range(h):
        for x in range(w - 1):
            a = (y * w + x) * 4
            total += sum(abs(px[a + c] - px[a + 4 + c]) for c in range(3))
            n += 3
    return total / n


class TileableTests(unittest.TestCase):
    def test_original_has_a_seam_and_the_result_has_none(self):
        w, h, px = texture()
        step = inner_step(w, h, px)
        self.assertGreater(wrap_edge(w, h, px, "x"), 10 * step, "the fixture must have a visible seam")
        out = tile.tileable(w, h, px)
        self.assertEqual(len(out), len(px))
        for axis in "xy":
            self.assertLessEqual(wrap_edge(w, h, out, axis), 1.5 * inner_step(w, h, out) + 1,
                                 "the seam on %s is still visible" % axis)

    def test_input_is_not_touched_and_alpha_stays_opaque(self):
        w, h, px = texture(32, 32)
        before = bytes(px)
        out = tile.tileable(w, h, px)
        self.assertEqual(bytes(px), before)
        self.assertEqual(set(out[3::4]), {255})

    def test_edges_come_from_the_middle_of_the_original(self):
        w, h, px = texture(32, 32)
        out = tile.tileable(w, h, px)
        i = (0 * w + 0) * 4  # corner of the result = centre of the original
        j = ((h // 2) * w + w // 2) * 4
        self.assertEqual(bytes(out[i:i + 4]), bytes(px[j:j + 4]))

    def test_blend_out_of_range_is_refused_with_its_reason(self):
        w, h, px = texture(16, 16)
        for bad in (0, 0.6, -1):
            with self.assertRaises(ValueError) as cm:
                tile.tileable(w, h, px, blend=bad)
            self.assertIn("blend", str(cm.exception))

    def test_too_small_blend_or_image_is_refused_not_faked(self):
        w, h, px = texture(64, 64)
        for blend in (0.001, 1e-9):
            with self.assertRaises(ValueError) as cm:
                tile.tileable(w, h, px, blend=blend)
            self.assertIn("at least 1 px", str(cm.exception))
        w, h, px = texture(4, 4)
        with self.assertRaises(ValueError) as cm:
            tile.tileable(w, h, px)
        self.assertIn("at least %d px" % tile.MIN_SIDE, str(cm.exception))

    def test_transparent_pixels_do_not_bleed_their_hidden_color(self):
        w, h = 32, 32
        px = bytearray()
        for y in range(h):
            for x in range(w):
                px += bytes((0, 0, 255, 0)) if x < w // 2 else bytes((255, 0, 0, 255))
        out = tile.tileable(w, h, px)
        for i in range(0, len(out), 4):
            if out[i + 3] > 0:
                self.assertEqual(tuple(out[i:i + 3]), (255, 0, 0), "a blue tint came from fully transparent pixels")

    def test_repeat_is_a_grid_of_copies(self):
        w, h, px = texture(8, 6)
        out = tile.repeat(w, h, px, 4, 4)
        self.assertEqual(len(out), 4 * w * 4 * h * 4)
        for ty, tx in ((0, 0), (3, 3), (1, 2)):
            for y in (0, h - 1):
                a = ((ty * h + y) * 4 * w + tx * w) * 4
                self.assertEqual(bytes(out[a:a + w * 4]), bytes(px[y * w * 4:(y + 1) * w * 4]))


class BlendEdgeTests(unittest.TestCase):
    def test_blend_half_leaves_the_borders_of_the_piece_untouched_so_they_repeat(self):
        for n in (64, 65, 96):
            for w in (tile._weights(n, 0.5 * n), tile._weights(n, 0.25 * n)):
                self.assertEqual((w[0], w[-1]), (0.0, 0.0), n)
        w, h, px = texture(64, 64)
        out = tile.tileable(w, h, px, 0.5)
        step = inner_step(w, h, px)
        for axis in ("x", "y"):
            self.assertLessEqual(wrap_edge(w, h, out, axis), 2 * step, axis)
        self.assertGreater(wrap_edge(w, h, px, "x"), 10 * step)


class TileCommandTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.src = os.path.join(self.dir.name, "tex.png")
        w, h, px = texture()
        Path(self.src).write_bytes(png.rgba_bytes(w, h, px))

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_writes_the_tileable_and_the_4x4_preview(self):
        res = tile.tile(self.src, preview=os.path.join(self.dir.name, "p.png"), preview_side=32)
        self.assertEqual(res["out"], os.path.join(self.dir.name, "tex-tile.png"))
        w, h, px = png.read_rgba(res["out"])
        self.assertEqual((w, h), (96, 64))
        self.assertLessEqual(wrap_edge(w, h, px, "x"), 1.5 * inner_step(w, h, px) + 1)
        pw, ph, _ = png.read_rgba(res["preview"])
        self.assertEqual(pw, 128)
        self.assertEqual(ph, 4 * round(64 * 32 / 96))

    def test_cli_json_and_texts_in_both_languages(self):
        for lang, word in (("es", "sin costura"), ("en", "seamless")):
            out = os.path.join(self.dir.name, lang + ".png")
            code, text, err = self.run_cli("--lang", lang, "tile", self.src, "-o", out)
            self.assertEqual((code, err), (0, ""))
            self.assertIn(word, text)
        code, text, _ = self.run_cli("--json", "tile", self.src, "-o", os.path.join(self.dir.name, "j.png"), "--force")
        self.assertEqual(json.loads(text)["size"], [96, 64])

    def test_will_not_overwrite_the_input_or_an_existing_output(self):
        with self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=self.src)
        self.assertEqual(cm.exception.code, "tile.out_is_input")
        out = os.path.join(self.dir.name, "o.png")
        tile.tile(self.src, out=out)
        with self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out)
        self.assertEqual(cm.exception.code, "tile.exists")
        tile.tile(self.src, out=out, force=True)


    def test_outputs_that_are_one_file_and_a_failing_view_leave_nothing_half_written(self):
        link = os.path.join(self.dir.name, "link.png")
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"")
        os.symlink(out, link)
        with self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, preview=link, force=True)
        self.assertEqual(cm.exception.code, "tile.same_outputs")
        blocked = os.path.join(self.dir.name, "nofolder")
        Path(blocked).write_text("a file where a folder should be")
        fresh = os.path.join(self.dir.name, "fresh.png")
        with self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=fresh, preview=os.path.join(blocked, "v.png"))
        self.assertEqual(cm.exception.code, "tile.write_failed")
        self.assertFalse(os.path.exists(fresh), "the texture must not be left without its view")

    def test_a_failing_second_replace_puts_back_what_was_there(self):
        out, view = os.path.join(self.dir.name, "o.png"), os.path.join(self.dir.name, "v.png")
        Path(out).write_bytes(b"old texture")
        Path(view).write_bytes(b"old view")
        real = os.replace

        def flaky(a, b):
            if b == view and ".gimg-tile-" in a:  # the new view taking its place; the error names the source, as real ones do
                raise OSError(28, "No space left on device", a)
            return real(a, b)

        with mock.patch("gimg.tile.os.replace", flaky), self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, preview=view, preview_side=32, force=True)
        self.assertEqual(cm.exception.code, "tile.write_failed")
        self.assertIn("No space", cm.exception.params["reason"])
        self.assertEqual(cm.exception.params["path"], view, "the error names the target, not the temporary")
        self.assertEqual(Path(out).read_bytes(), b"old texture")
        self.assertEqual(Path(view).read_bytes(), b"old view")
        self.assertEqual(sorted(os.listdir(self.dir.name)), ["o.png", "tex.png", "v.png"], "no temporary left behind")

    def test_a_folder_in_the_target_is_refused_and_left_intact(self):
        out, view = os.path.join(self.dir.name, "o.png"), os.path.join(self.dir.name, "v.png")
        os.makedirs(os.path.join(out, "inner"))
        Path(view).write_bytes(b"old view")
        with self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, preview=view, preview_side=32, force=True)
        self.assertEqual(cm.exception.code, "tile.write_failed")
        self.assertIn("directory", cm.exception.params["reason"].lower())
        self.assertEqual(cm.exception.params["path"], out)
        self.assertTrue(os.path.isdir(os.path.join(out, "inner")))
        self.assertEqual(Path(view).read_bytes(), b"old view")
        self.assertEqual(sorted(os.listdir(self.dir.name)), ["o.png", "tex.png", "v.png"], "nothing moved or left behind")

    def test_a_failing_second_replace_removes_the_new_first_file(self):
        out, view = os.path.join(self.dir.name, "o.png"), os.path.join(self.dir.name, "v.png")
        real = os.replace

        def flaky(a, b):
            if b == view and ".gimg-tile-" in a:  # the new view taking its place; the error names the source, as real ones do
                raise OSError(28, "No space left on device", a)
            return real(a, b)

        with mock.patch("gimg.tile.os.replace", flaky), self.assertRaises(GimgError):
            tile.tile(self.src, out=out, preview=view, preview_side=32)
        self.assertEqual(sorted(os.listdir(self.dir.name)), ["tex.png"])

    def test_rollback_keeps_a_symlinked_target_and_its_mode(self):
        real_file = os.path.join(self.dir.name, "real.png")
        out, view = os.path.join(self.dir.name, "o.png"), os.path.join(self.dir.name, "v.png")
        Path(real_file).write_bytes(b"old texture")
        os.chmod(real_file, 0o640)
        os.symlink(real_file, out)
        Path(view).write_bytes(b"old view")
        real = os.replace

        def flaky(a, b):
            if b == view and ".gimg-tile-" in a:
                raise OSError(28, "No space left on device", a)
            return real(a, b)

        with mock.patch("gimg.tile.os.replace", flaky), self.assertRaises(GimgError):
            tile.tile(self.src, out=out, preview=view, preview_side=32, force=True)
        self.assertTrue(os.path.islink(out))
        self.assertEqual(Path(out).read_bytes(), b"old texture")
        self.assertEqual(os.stat(real_file).st_mode & 0o777, 0o640)
        self.assertEqual(sorted(os.listdir(self.dir.name)), ["o.png", "real.png", "tex.png", "v.png"])

    def test_an_input_over_the_pixel_limit_is_refused_with_its_reason(self):
        with mock.patch.object(tile, "MAX_PIXELS", 96 * 64 - 1), mock.patch.object(
                png, "read_rgba", side_effect=AssertionError("decoded")) as read, self.assertRaises(GimgError) as cm:
            tile.tile(self.src)
        read.assert_not_called()
        self.assertEqual(cm.exception.code, "tile.too_big")
        self.assertFalse(os.path.exists(tile.default_out(self.src)))
        tile.tile(self.src)  # the real limit lets it through


if __name__ == "__main__":
    unittest.main()
