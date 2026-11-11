"""The workshop of `gimg/brandshop.py`: redoing a step deletes the pieces derived from it, so `save` never mixes pieces
drawn from different inputs. The brand steps are replaced by stubs that write a file: no tools needed."""
import os
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


class DerivedPiecesTests(BrandApiBase):
    def seed(self):
        self.shop().mkdir(parents=True, exist_ok=True)
        for key in brand.SYSTEM_FILES:
            (self.shop() / ("%s-%s" % (SLUG, key))).write_bytes(b"x")

    def present(self):
        return sorted(k for k in brand.SYSTEM_FILES if (self.shop() / ("%s-%s" % (SLUG, k))).exists())

    def redo(self, step):
        with mock.patch.object(brand, "matte", _stub(1)), mock.patch.object(brand, "trace", _stub(1)), \
                mock.patch.object(brand, "wordmark", _stub(2)), mock.patch.object(brandshop, "resolve_font", lambda f: f):
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
