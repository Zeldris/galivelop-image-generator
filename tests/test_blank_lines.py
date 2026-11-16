"""El código de gimg no deja tres o más líneas en blanco seguidas (PEP 8 pide dos como máximo).

Lo pidió la retro de L7 (2026-11-15): quitar un alias dejó una de más y solo se vio a mano; sin linter (D6, solo stdlib).
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class BlankLinesTests(unittest.TestCase):
    def test_no_three_blank_lines_in_a_row(self):
        bad = []
        for path in sorted((ROOT / "gimg").rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            for m in re.finditer(r"\n[ \t]*\n[ \t]*\n[ \t]*\n", text):
                bad.append(f"{path.relative_to(ROOT)}:{text.count(chr(10), 0, m.start()) + 2}")
        self.assertEqual(bad, [], "tres o más líneas en blanco seguidas (deja dos como máximo): " + ", ".join(bad))


if __name__ == "__main__":
    unittest.main()
