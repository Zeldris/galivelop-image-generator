"""Los scripts de tonos de `docs/marcas/` rechazan un hex mal formado con su motivo."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "docs/marcas/galivelop-developer/tonos.py",
    "docs/marcas/galivelop-voice-generator/tonos.py",
    "docs/marcas/galivelop-image-generator/acento_oklch.py",
    "docs/marcas/galivelop-workflow/acento.py",
]


def run(script, *args):
    return subprocess.run([sys.executable, str(ROOT / script), *args], capture_output=True, text=True, timeout=60)


class MalformedHex(unittest.TestCase):
    def test_a_malformed_hex_is_refused_with_its_reason(self):
        for script in SCRIPTS:
            for bad in ("#1234567", "#12345g", "#abc", "azul"):
                with self.subTest(script=script, value=bad):
                    proc = run(script, bad)
                    self.assertEqual(proc.returncode, 2, proc.stderr)
                    self.assertIn("#RRGGBB", proc.stderr)
                    self.assertIn(bad, proc.stderr)
                    self.assertNotIn("Traceback", proc.stderr)

    def test_a_well_formed_hex_still_works(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                proc = run(script, "#7C5CD6")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertTrue(proc.stdout.strip())


if __name__ == "__main__":
    unittest.main()
