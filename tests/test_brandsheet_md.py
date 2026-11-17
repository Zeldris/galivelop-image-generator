"""hoja.md ↔ datos (0.7.0, paso 4): the generated block of `docs/marcas/<p>/hoja.md` follows `marca.json`."""
import contextlib
import io
import unittest
from pathlib import Path

from gimg import brandsheet as B, cli
from gimg.errors import GimgError
from tests.test_brandsheet_portal import PortalEnv, SHEETS

ROOT = Path(__file__).resolve().parent.parent


class MarkdownTests(PortalEnv):
    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_every_hoja_has_the_block_of_its_data(self):
        for name in SHEETS:
            path = ROOT / "docs" / "marcas" / name / "hoja.md"
            found = B.extract_block(path.read_text(encoding="utf-8"), path)
            self.assertEqual(found, B.markdown(name),
                             "%s: el bloque no coincide con marca.json; arréglalo con: gimg brand md %s --write %s --lang es"
                             % (path, name, path))

    def test_the_match_fails_without_the_block(self):
        path = ROOT / "docs" / "marcas" / "portal" / "hoja.md"
        text = path.read_text(encoding="utf-8")
        cut = text[:text.index(B.MD_START)]
        self.assertIsNone(B.extract_block(cut))
        self.assertNotEqual(B.extract_block(cut), B.markdown("portal"))

    def test_replace_block_appends_without_markers(self):
        block = B.markdown("portal")
        self.assertEqual(B.replace_block("prosa\n", block), "prosa\n\n" + block)
        self.assertEqual(B.replace_block("", block), block)

    def test_replace_block_keeps_the_surroundings_byte_for_byte(self):
        old = B.markdown("portal").replace("paper", "PAPEL")
        before, after = "antes\r\n\n## T\n\n", "\n\ndespués  \n\n"
        text = before + old.rstrip("\n") + after
        new = B.replace_block(text, B.markdown("portal"))
        self.assertEqual(new, before + B.markdown("portal").rstrip("\n") + after)
        self.assertEqual(B.replace_block(new, B.markdown("portal")), new)

    def test_broken_markers_raise_their_code(self):
        block = B.markdown("portal")
        for text in (B.MD_START + "\nx\n", "x\n" + B.MD_END + "\n", block + block, B.MD_END + "\n" + B.MD_START + "\n"):
            with self.assertRaises(GimgError) as ctx:
                B.replace_block(text, block, "hoja.md")
            self.assertEqual(ctx.exception.code, "brandsheet.markdown_markers")
            self.assertEqual(ctx.exception.params["path"], "hoja.md")

    def test_child_marks_inherited_and_own(self):
        text = B.markdown("galivelop-workflow")
        self.assertIn("heredado de portal", text)
        self.assertRegex(text, r"`workflow-never`: [^\n]*\(propio\)")
        self.assertRegex(text, r"\| accent \|[^\n]*\| propio \|")
        self.assertRegex(text, r"\| paper \|[^\n]*\| heredado de portal \|")
        self.assertIn("galivelop-workflow ← portal", text)
        self.assertNotIn("heredado de", B.markdown("portal"))

    def test_english_titles(self):
        text = B.markdown("portal", "en")
        for title in ("### Sheet data", "#### Card", "#### Palette by role", "#### Vetoes", "#### Piece types"):
            self.assertIn(title, text)
        self.assertNotIn("#### Ficha", text)
        self.assertIn("#### Ficha", B.markdown("portal"))

    def test_cells_escape_the_pipe(self):
        self.assertEqual(B._cell("a|b"), "a\\|b")
        self.assertEqual(B._cell(None), "—")

    def test_cli_check_and_write(self):
        target = self.tmp / "hoja.md"
        target.write_text("# Hoja\n\nprosa\n", encoding="utf-8")
        code, _, err = self.cli("--lang", "es", "brand", "md", "portal", "--check", str(target))
        self.assertEqual(code, 1)
        self.assertIn("no coincide", err)
        self.assertEqual(self.cli("--lang", "es", "brand", "md", "portal", "--write", str(target))[0], 0)
        self.assertEqual(self.cli("--lang", "es", "brand", "md", "portal", "--check", str(target))[0], 0)
        self.assertTrue(target.read_text(encoding="utf-8").startswith("# Hoja\n\nprosa\n\n"))
        text = target.read_text(encoding="utf-8").replace("`portal`", "`portal2`", 1)
        target.write_text(text, encoding="utf-8")
        code, _, err = self.cli("--lang", "es", "brand", "md", "portal", "--check", str(target), "--json")
        self.assertEqual(code, 1)
        self.assertIn(str(target), err)
        self.assertIn("no coincide con marca.json", err)

    def test_cli_prints_the_block_and_creates_the_file(self):
        code, out, _ = self.cli("--lang", "es", "brand", "md", "portal")
        self.assertEqual((code, out), (0, B.markdown("portal")))
        target = self.tmp / "nuevo.md"
        self.assertEqual(self.cli("--lang", "es", "brand", "md", "portal", "--write", str(target))[0], 0)
        self.assertEqual(target.read_text(encoding="utf-8"), B.markdown("portal"))


if __name__ == "__main__":
    unittest.main()
