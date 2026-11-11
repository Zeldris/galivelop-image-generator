"""Logos de Galivelop IG (hoja de marca, sección 4): geometría, colores y favicon, sin navegador."""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "docs" / "marcas" / "galivelop-image-generator" / "logos"
UI = ROOT / "gimg" / "ui" / "assets"
SVG = "{http://www.w3.org/2000/svg}"
P = "galivelop-image-generator-b"
SYMBOLS = {  # archivo -> (tinta de las líneas, relleno de la celda encendida)
    LOGOS / (P + ".svg"): ("#fbfcfd", "#fbfcfd"),
    LOGOS / (P + "-linea.svg"): ("#13212b", "#8B5CF6"),
    LOGOS / (P + "-linea-oscuro.svg"): ("#e6eef3", "#8B5CF6"),
    UI / "gvig.svg": ("#fbfcfd", "#fbfcfd"),
}
LOCKUPS = {  # archivo -> (tinta, IG)
    LOGOS / (P + "-lockup.svg"): ("#13212b", "#5B34C9"),
    LOGOS / (P + "-lockup-oscuro.svg"): ("#e6eef3", "#A78BFA"),
    UI / "gvig-lockup.svg": ("#13212b", "#5B34C9"),
}


def tree(path):
    return ET.fromstring(path.read_text(encoding="utf-8"))


def filled_rects(root):
    return [r for r in root.iter(SVG + "rect") if r.get("fill") not in (None, "none") and r.get("width") != "128"]


class Symbols(unittest.TestCase):
    def test_contract(self):
        for path in SYMBOLS:
            root = tree(path)
            self.assertEqual(root.get("viewBox"), "0 0 128 128", path)
            self.assertTrue((root.findtext(SVG + "title") or "").strip().startswith("Galivelop IG"), path)  # D38
            self.assertEqual(list(root.iter(SVG + "text")), [], path)
            raw = path.read_text(encoding="utf-8")
            for banned in ("linearGradient", "radialGradient", "<filter", "<image"):
                self.assertNotIn(banned, raw, (path, banned))

    def test_one_lit_cell_with_exact_colors(self):
        for path, (ink, lit) in SYMBOLS.items():
            root = tree(path)
            cells = filled_rects(root)
            self.assertEqual(len(cells), 1, path)
            self.assertEqual(cells[0].get("fill"), lit, path)
            strokes = {g.get("stroke") for g in root.iter(SVG + "g")}
            self.assertEqual(strokes, {ink}, path)
            self.assertEqual({g.get("stroke-width") for g in root.iter(SVG + "g")}, {"12"}, path)

    def test_tile_is_flat_with_28_corner(self):
        for path in (LOGOS / (P + ".svg"), UI / "gvig.svg"):
            tile = [r for r in tree(path).iter(SVG + "rect") if r.get("width") == "128"]
            self.assertEqual(len(tile), 1, path)
            self.assertEqual((tile[0].get("fill"), tile[0].get("rx")), ("#5B34C9", "28"), path)
        for path in (LOGOS / (P + "-linea.svg"), LOGOS / (P + "-linea-oscuro.svg")):
            self.assertNotIn("#5B34C9", path.read_text(encoding="utf-8"), path)

    def test_favicon_is_the_tile_symbol_and_lit_cell_reaches_4px_at_16px(self):
        self.assertEqual((UI / "gvig.svg").read_text(encoding="utf-8"), (LOGOS / (P + ".svg")).read_text(encoding="utf-8"))
        cell = filled_rects(tree(UI / "gvig.svg"))[0]
        self.assertGreaterEqual(float(cell.get("width")) * 16 / 128, 4)
        self.assertGreaterEqual(float(cell.get("height")) * 16 / 128, 4)


class Lockups(unittest.TestCase):
    def test_contract_and_text(self):
        for path, (ink, ig) in LOCKUPS.items():
            root = tree(path)
            self.assertEqual(root.get("viewBox"), "0 0 1100 128", path)
            self.assertTrue((root.findtext(SVG + "title") or "").strip(), path)
            texts = list(root.iter(SVG + "text"))
            self.assertEqual(len(texts), 1, path)
            self.assertIn("Big Shoulders Display", texts[0].get("font-family"), path)
            self.assertEqual(texts[0].get("font-weight"), "700", path)
            self.assertEqual(texts[0].get("fill"), ink, path)
            self.assertEqual("".join(texts[0].itertext()), "Galivelop IG", path)
            spans = list(texts[0].iter(SVG + "tspan"))
            self.assertEqual([(s.text, s.get("fill")) for s in spans], [("IG", ig)], path)
            self.assertEqual(float(texts[0].get("x")), 128 + 28, path)  # separación 28/128 de la baldosa
            raw = path.read_text(encoding="utf-8")
            self.assertNotRegex(raw, r"linearGradient|radialGradient|<filter|Sora")
            self.assertEqual(len(filled_rects(root)), 1, path)

    def test_ui_lockup_matches_the_brand_one(self):
        self.assertEqual((UI / "gvig-lockup.svg").read_text(encoding="utf-8"),
                         (LOGOS / (P + "-lockup.svg")).read_text(encoding="utf-8"))

    def test_dark_variant_swaps_only_ink_and_accent(self):
        light = (LOGOS / (P + "-lockup.svg")).read_text(encoding="utf-8")
        dark = (LOGOS / (P + "-lockup-oscuro.svg")).read_text(encoding="utf-8")
        swapped = light.replace("#13212b", "#e6eef3").replace('fill="#5B34C9">IG', 'fill="#A78BFA">IG')
        self.assertEqual(re.sub(r'-lockup-t', '-lockup-oscuro-t', swapped), dark)


if __name__ == "__main__":
    unittest.main()
