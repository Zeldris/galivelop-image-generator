"""The workshop of `gimg/brandshop.py`: redoing a step deletes the pieces derived from it, so `save` never mixes pieces
drawn from different inputs. The brand steps are replaced by stubs that write a file: no tools needed."""
import os
import subprocess
import unittest
from unittest import mock

from gimg import brand, brandshop
from gimg.errors import GimgError
from tests.test_server_brand import NAME, SLUG, BrandApiBase


def _stub(dest_index):
    def run(*args, **kw):
        with open(args[dest_index], "w") as fh:
            fh.write("<svg/>")
        return {}
    return run


def _fc_match(file, family="Cinzel", index="0"):
    """A fake `subprocess.run` of fc-match that records its argv and answers `file`, `family` and the face `index`."""
    calls = []

    def run(argv, **kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "%s\n%s\n%s\n" % (file, family, index), "")
    return run, calls


class ResolveFontTests(unittest.TestCase):
    def resolve(self, file, family="Cinzel", index="0", **kw):
        run, calls = _fc_match(file, family, index)
        with mock.patch.object(brandshop.shutil, "which", lambda n: "/usr/bin/" + n), \
                mock.patch.object(brandshop.subprocess, "run", run):
            return brandshop.resolve_font(family, **kw), calls

    def test_the_weight_goes_to_fc_match_in_the_fontconfig_scale(self):
        for css, fc in ((400, 80), (700, 200), (800, 205), (900, 210), (100, 0), (600, 180), (450, 90), (1000, 215)):
            path, calls = self.resolve("/f/Cinzel.ttf", weight=css)
            self.assertEqual(calls[0][-1], "Cinzel:weight=%d" % fc, css)
            self.assertEqual(path, "/f/Cinzel.ttf")

    def test_no_weight_keeps_the_bare_family(self):
        self.assertEqual(self.resolve("/f/Cinzel.ttf")[1][0][-1], "Cinzel")

    def test_the_family_is_escaped_before_the_weight_is_added(self):
        _, calls = self.resolve("/f/a.ttf", family="A:B", weight=700)
        self.assertEqual(calls[0][-1], "A\\:B:weight=200")

    def test_a_font_collection_is_accepted(self):
        self.assertEqual(self.resolve("/f/Cinzel.ttc", weight=400)[0], "/f/Cinzel.ttc")
        self.assertEqual(self.resolve("/f/Cinzel.OTC")[0], "/f/Cinzel.OTC")

    def test_other_formats_say_which_are_valid(self):
        with self.assertRaises(GimgError) as ctx:
            self.resolve("/f/Cinzel.woff2")
        self.assertEqual(ctx.exception.code, "brand.font_unreadable")
        self.assertIn(".ttc", ctx.exception.params["reason"])

    def test_a_bad_weight_is_refused(self):
        with self.assertRaises(GimgError) as ctx:
            self.resolve("/f/Cinzel.ttf", weight="bold")
        self.assertEqual(ctx.exception.code, "brand.bad_option")

    def test_the_weight_is_checked_as_wordmark_does_before_fc_match_runs(self):
        for weight in (0, 1001, 400.5, "bold", True):
            run, calls = _fc_match("/f/Cinzel.ttf")
            with mock.patch.object(brandshop.shutil, "which", lambda n: "/usr/bin/" + n), \
                    mock.patch.object(brandshop.subprocess, "run", run), self.assertRaises(GimgError) as ctx:
                brandshop.resolve_font("Cinzel", weight)
            self.assertEqual(ctx.exception.code, "brand.bad_option", weight)
            self.assertEqual(ctx.exception.params["reason"], "weight 1-1000 and spacing between -0.5 and 2 em", weight)
            self.assertEqual(calls, [], weight)

    def test_a_face_that_is_not_number_0_of_a_collection_is_refused(self):
        run, calls = _fc_match("/f/Cinzel.ttc", index="2")
        with mock.patch.object(brandshop.shutil, "which", lambda n: "/usr/bin/" + n), \
                mock.patch.object(brandshop.subprocess, "run", run):
            with self.assertRaises(GimgError) as ctx:
                brandshop.resolve_font("Cinzel")
        self.assertEqual(ctx.exception.code, "brand.font_unreadable")
        self.assertIn("number 2", ctx.exception.params["reason"])
        self.assertIn("%{index}", calls[0][2])
        self.assertEqual(self.resolve("/f/Cinzel.ttc", index="0")[0], "/f/Cinzel.ttc")


class DerivedPiecesTests(BrandApiBase):
    def seed(self):
        self.shop().mkdir(parents=True, exist_ok=True)
        for key in brand.SYSTEM_FILES:
            (self.shop() / ("%s-%s" % (SLUG, key))).write_bytes(b"x")

    def present(self):
        return sorted(k for k in brand.SYSTEM_FILES if (self.shop() / ("%s-%s" % (SLUG, k))).exists())

    def redo(self, step):
        with mock.patch.object(brand, "matte", _stub(1)), mock.patch.object(brand, "trace", _stub(1)), \
                mock.patch.object(brand, "wordmark", _stub(2)), mock.patch.object(brandshop, "resolve_font", lambda f, w=None: f):
            if step == "matte":
                brandshop.matte(NAME, "Mi Marca", "src")
            elif step == "color":
                brandshop.trace(NAME, "Mi Marca", "color")
            elif step == "mono":
                brandshop.trace(NAME, "Mi Marca", "mono")
            else:
                brandshop.wordmark(NAME, "Mi Marca", "Any")

    def assert_save_refused_for(self, file):
        with self.assertRaises(GimgError) as caught:
            brandshop.save(NAME, "Mi Marca")
        self.assertEqual(caught.exception.code, "brand.missing_piece")
        self.assertEqual(caught.exception.params["file"], "%s-%s" % (SLUG, file))

    def test_the_wordmark_asks_for_the_face_of_its_weight(self):
        seen = []
        self.shop().mkdir(parents=True, exist_ok=True)

        def fake(family, weight=None):
            seen.append((family, weight))
            return family
        with mock.patch.object(brand, "wordmark", _stub(2)), mock.patch.object(brandshop, "resolve_font", fake):
            brandshop.wordmark(NAME, "Mi Marca", "Cinzel", weight=600)
            brandshop.wordmark(NAME, "Mi Marca", "Cinzel")
        self.assertEqual(seen, [("Cinzel", 600), ("Cinzel", brand.DEFAULT_WEIGHT)])  # no weight: the one brand.wordmark draws at

    def test_redoing_the_matte_drops_everything_drawn_from_it(self):
        self.seed()
        self.redo("matte")
        self.assertEqual(self.present(), ["emblema-alpha.png", "wordmark.svg"])
        self.assert_save_refused_for("emblema.svg")

    def test_redoing_the_color_trace_drops_lockups_and_contact_sheet(self):
        self.seed()
        self.redo("color")
        self.assertEqual(self.present(), ["emblema-alpha.png", "emblema-mono.svg", "emblema.svg", "wordmark.svg"])
        self.assert_save_refused_for("lockup-h.svg")

    def test_redoing_the_mono_trace_only_drops_the_contact_sheet(self):
        self.seed()
        self.redo("mono")
        self.assertEqual(self.present(), sorted(k for k in brand.SYSTEM_FILES if k != "contactos.png"))

    def test_redoing_the_wordmark_drops_lockups_and_contact_sheet(self):
        self.seed()
        self.redo("wordmark")
        self.assertEqual(self.present(), ["emblema-alpha.png", "emblema-mono.svg", "emblema.svg", "wordmark.svg"])
        self.assert_save_refused_for("lockup-h.svg")

    def test_a_failed_step_keeps_the_derived_pieces(self):
        self.seed()
        with mock.patch.object(brand, "matte", side_effect=GimgError("brand.bad_option", reason="x")):
            with self.assertRaises(GimgError):
                brandshop.matte(NAME, "Mi Marca", "src")
        self.assertEqual(self.present(), sorted(brand.SYSTEM_FILES))


if __name__ == "__main__":
    unittest.main()
