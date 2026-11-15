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


OLD = 1_000_000_000  # ns since the epoch: far older than the grace period


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

    def test_an_unreadable_target_is_refused_naming_its_path(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"old")

        def denied(a, b):
            raise PermissionError(13, "Permission denied", a)

        with mock.patch("gimg.tile.os.path.samefile", denied), self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, force=True)
        self.assertEqual(cm.exception.code, "tile.write_failed")
        self.assertEqual(cm.exception.params["path"], out)
        self.assertIn("Permission denied", cm.exception.params["reason"])
        self.assertEqual(Path(out).read_bytes(), b"old")

    def test_a_copy_left_by_a_killed_run_is_put_back_when_the_target_is_missing(self):
        out = os.path.join(self.dir.name, "o.png")
        orphan = tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD)
        Path(self.dir.name, orphan).write_bytes(b"the original")
        with self.assertRaises(GimgError) as cm:  # the original is back, so it is not overwritten without --force
            tile.tile(self.src, out=out)
        self.assertEqual(cm.exception.code, "tile.exists")
        self.assertEqual(Path(out).read_bytes(), b"the original")
        self.assertEqual(sorted(os.listdir(self.dir.name)), ["o.png", "tex.png"])
        res = tile.tile(self.src, out=out, force=True)
        self.assertEqual(res["out"], out)

    def test_a_copy_left_beside_a_target_in_place_is_kept_and_reported(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"new, already in place")
        kept = Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD))
        kept.write_bytes(b"old")
        other = Path(self.dir.name, tile._backup_name(os.path.join(self.dir.name, "x.png"), pid=2 ** 22 + 5, stamp=OLD))
        other.write_bytes(b"belongs to another target")
        res = tile.tile(self.src, out=out, force=True)
        self.assertEqual(len(res["recovered"]), 1)
        self.assertEqual(res["recovered"][0]["action"], "kept")
        self.assertTrue(other.exists(), "a copy of another target is not touched")
        self.assertEqual(kept.read_bytes(), b"old",
                         "an original that may be the only copy is never deleted")

    def test_a_failed_rollback_is_reported_with_the_original_error_and_keeps_the_copy(self):
        out, view = os.path.join(self.dir.name, "o.png"), os.path.join(self.dir.name, "v.png")
        Path(out).write_bytes(b"old texture")
        Path(view).write_bytes(b"old view")
        real = os.replace

        def flaky(a, b):
            if b == view and ".gimg-tile-" in a:
                raise OSError(28, "No space left on device", a)
            if ".gimg-bak-" in a:  # the rollback cannot put the old file back
                raise OSError(5, "Input/output error", a)
            return real(a, b)

        with mock.patch("gimg.tile.os.replace", flaky), self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, preview=view, preview_side=32, force=True)
        reason = cm.exception.params["reason"]
        self.assertIn("No space left", reason)
        self.assertIn("rollback incomplete", reason)
        self.assertIn("Input/output error", reason)
        self.assertIn("the copy keeps the original", reason)
        self.assertIn(out, reason)
        baks = [n for n in os.listdir(self.dir.name) if n.startswith(".gimg-bak-")]
        self.assertEqual(len(baks), 2, "the old files stay on disk for the next run")
        self.assertEqual(Path(self.dir.name, [n for n in baks if n.startswith(tile._backup_prefix(out))][0]).read_bytes(),
                         b"old texture")
        res = tile.tile(self.src, out=os.path.join(self.dir.name, "z.png"))  # untouched targets: copies stay
        self.assertNotIn("recovered", res)
        self.assertEqual(tile.recover_backups([out]), [], "too recent, and this process is alive: not touched yet")
        for n in baks:  # later: the process is gone and the grace period over
            parts = n.split("-")
            os.rename(os.path.join(self.dir.name, n), os.path.join(self.dir.name, "-".join(parts[:3] + ["%d" % (2 ** 22 + 5), str(OLD), parts[-1]])))
        os.unlink(out)  # the new file in place was lost too: the next run restores the original first
        with self.assertRaises(GimgError) as cm2:
            tile.tile(self.src, out=out)
        self.assertEqual(cm2.exception.code, "tile.exists")
        self.assertEqual(Path(out).read_bytes(), b"old texture")

    def test_odd_and_tiny_sizes(self):
        for w, h in ((1, 1), (3, 5), (7, 7), (7, 64)):
            src = os.path.join(self.dir.name, "s%dx%d.png" % (w, h))
            Path(src).write_bytes(png.rgba_bytes(w, h, bytes((9, 9, 9, 255)) * (w * h)))
            with self.assertRaises(GimgError) as cm:
                tile.tile(src)
            self.assertEqual(cm.exception.code, "tile.bad_option")
            self.assertIn("at least %d px" % tile.MIN_SIDE, cm.exception.params["reason"])
            self.assertIn("%dx%d" % (w, h), cm.exception.params["reason"])
            self.assertFalse(os.path.exists(tile.default_out(src)))
        for w, h in ((8, 8), (9, 9), (11, 8), (15, 9), (13, 17)):
            tw, th, px = texture(w, h)
            out = tile.tileable(tw, th, px)
            self.assertEqual(len(out), w * h * 4)
            self.assertTrue(all(out[3::4][i] == 255 for i in range(w * h)))
            src = os.path.join(self.dir.name, "t%dx%d.png" % (w, h))
            Path(src).write_bytes(png.rgba_bytes(tw, th, px))
            res = tile.tile(src, preview_side=16)
            self.assertEqual(res["size"], [w, h])

    def test_a_copy_of_a_live_or_recent_run_is_not_touched(self):
        import time
        out = os.path.join(self.dir.name, "o.png")
        mine = Path(self.dir.name, tile._backup_name(out, pid=os.getpid(), stamp=OLD))  # old, but its pid is alive
        fresh = Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=time.time_ns()))  # dead pid, just made
        mine.write_bytes(b"live")
        fresh.write_bytes(b"recent")
        self.assertEqual(tile.recover_backups([out]) if os.name != "nt" else [], [])
        res = tile.tile(self.src, out=out)  # the target is missing, yet no copy is put back
        self.assertNotIn("recovered", res)
        self.assertEqual(mine.read_bytes(), b"live")
        self.assertEqual(fresh.read_bytes(), b"recent")

    def test_the_oldest_copy_is_the_one_put_back(self):
        out = os.path.join(self.dir.name, "o.png")
        newer = Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD + 10 ** 9))
        older = Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD))
        newer.write_bytes(b"newer")
        older.write_bytes(b"the original")
        items = tile.recover_backups([out])
        self.assertEqual([i["action"] for i in items], ["restored", "kept"])
        self.assertEqual(Path(out).read_bytes(), b"the original")

    def test_nothing_is_recovered_when_the_call_fails_validation(self):
        out = os.path.join(self.dir.name, "o.png")
        orphan = Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD))
        orphan.write_bytes(b"the original")
        with self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, blend=0.9)
        self.assertEqual(cm.exception.code, "tile.bad_option")
        self.assertTrue(orphan.exists())
        self.assertFalse(os.path.exists(out), "a failing call has no effect on disk")

    def test_the_command_line_says_what_it_put_back_even_when_it_then_fails(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD)).write_bytes(b"the original")
        code, so, se = self.run_cli("--lang", "en", "tile", self.src, "-o", out)
        self.assertNotEqual(code, 0)
        self.assertIn("already exists", se)
        self.assertIn("the original was put back from", se)
        Path(out).unlink()
        orphan = Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD + 1))
        orphan.write_bytes(b"x")
        Path(out).write_bytes(b"in place")
        code, so, se = self.run_cli("--lang", "es", "tile", self.src, "-o", out, "--force")
        self.assertEqual(code, 0)
        self.assertIn("puede ser el original", so)
        self.assertNotIn("bórrala si no la necesitas", so)
        code, so, se = self.run_cli("--lang", "en", "tile", self.src, "-o", out, "--force")
        self.assertIn("may be the original", so)

    def test_what_was_put_back_before_a_failed_recovery_is_said(self):
        out, view = os.path.join(self.dir.name, "o.png"), os.path.join(self.dir.name, "v.png")
        Path(self.dir.name, tile._backup_name(out, pid=2 ** 22 + 5, stamp=OLD)).write_bytes(b"the original")
        Path(self.dir.name, tile._backup_name(view, pid=2 ** 22 + 5, stamp=OLD)).write_bytes(b"the old view")
        real = os.replace

        def flaky(a, b):
            if b == view:
                raise OSError(13, "Permission denied", a)
            return real(a, b)

        with mock.patch("gimg.tile.os.replace", flaky), self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out, preview=view, force=True)
        self.assertEqual(cm.exception.code, "tile.write_failed")
        self.assertIn("cannot recover", cm.exception.params["reason"])
        self.assertEqual([(i["action"], i["path"]) for i in cm.exception.recovered], [("restored", out)])
        self.assertEqual(Path(out).read_bytes(), b"the original")

    def test_a_copy_that_could_not_be_deleted_after_a_success_is_said(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"old texture")
        real = os.unlink

        def flaky(p, *a, **k):
            if ".gimg-bak-" in os.fspath(p):
                raise OSError(16, "Device or resource busy", p)
            return real(p, *a, **k)

        with mock.patch("gimg.tile.os.unlink", flaky):
            res = tile.tile(self.src, out=out, force=True)
        [item] = res["stale_backups"]
        self.assertEqual(item["path"], out)
        self.assertIn("Device or resource busy", item["reason"])
        self.assertEqual(Path(item["backup"]).read_bytes(), b"old texture")
        self.assertNotEqual(Path(out).read_bytes(), b"old texture")
        with mock.patch("gimg.tile.os.unlink", flaky):
            code, so, se = self.run_cli("--lang", "es", "tile", self.src, "-o", out, "--force")
        self.assertEqual(code, 0)
        self.assertIn("no se pudo borrar", so)
        self.assertIn("Device or resource busy", so)

    def test_a_copy_that_could_not_be_deleted_is_marked_and_a_later_run_never_restores_or_keeps_it(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"old texture")
        real = os.unlink

        def flaky(p, *a, **k):
            if ".gimg-bak-" in os.fspath(p) or ".gimg-stale-" in os.fspath(p):
                raise OSError(16, "Device or resource busy", p)
            return real(p, *a, **k)

        with mock.patch("gimg.tile.os.unlink", flaky):
            res = tile.tile(self.src, out=out, force=True)
        [item] = res["stale_backups"]
        self.assertTrue(os.path.basename(item["backup"]).startswith(".gimg-stale-"))
        self.assertEqual(Path(item["backup"]).read_bytes(), b"old texture")
        self.assertEqual([n for n in os.listdir(self.dir.name) if n.startswith(".gimg-bak-")], [])
        new = Path(out).read_bytes()
        os.utime(item["backup"], (0, 0))
        with mock.patch("gimg.tile.os.unlink", flaky):  # still busy: said as stale, not as a possible original
            [rec] = tile.recover_backups([out])
        self.assertEqual((rec["action"], rec["backup"]), ("stale", item["backup"]))
        self.assertIn("sobrante", tile.describe_recovery(rec, "es"))
        os.unlink(out)  # even with the target missing, a marked copy is not put back
        with mock.patch("gimg.tile.os.unlink", flaky):
            [rec] = tile.recover_backups([out])
        self.assertEqual(rec["action"], "stale")
        self.assertFalse(os.path.exists(out))
        self.assertEqual(tile.recover_backups([out]), [])  # the copy is deleted now that it can be
        self.assertFalse(os.path.exists(item["backup"]))
        self.assertNotEqual(new, b"old texture")

    def test_every_recovery_action_has_its_text_in_both_languages(self):
        for lang in ("es", "en"):
            for action in ("restored", "kept", "stale"):
                text = tile.describe_recovery({"action": action, "path": "P", "backup": "B"}, lang)
                self.assertNotIn("cli.out.tile_recovery_", text)
                self.assertIn("B", text)

    def test_a_copy_that_cannot_even_be_renamed_keeps_its_name(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"old texture")
        real_unlink, real_replace = os.unlink, os.replace

        def busy(p, *a, **k):
            if ".gimg-bak-" in os.fspath(p):
                raise OSError(16, "Device or resource busy", p)
            return real_unlink(p, *a, **k)

        def no_rename(a, b):
            if ".gimg-stale-" in os.fspath(b):
                raise OSError(13, "Permission denied", a)
            return real_replace(a, b)

        with mock.patch("gimg.tile.os.unlink", busy), mock.patch("gimg.tile.os.replace", no_rename):
            res = tile.tile(self.src, out=out, force=True)
        [item] = res["stale_backups"]
        self.assertTrue(os.path.basename(item["backup"]).startswith(".gimg-bak-"))
        self.assertEqual(Path(item["backup"]).read_bytes(), b"old texture")

    def test_an_existing_output_without_force_is_refused_before_decoding_or_blending(self):
        out = os.path.join(self.dir.name, "o.png")
        Path(out).write_bytes(b"keep me")
        with mock.patch.object(png, "read_rgba", side_effect=AssertionError("decoded")), mock.patch.object(
                tile, "tileable", side_effect=AssertionError("blended")), self.assertRaises(GimgError) as cm:
            tile.tile(self.src, out=out)
        self.assertEqual(cm.exception.code, "tile.exists")
        self.assertEqual(Path(out).read_bytes(), b"keep me")

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
