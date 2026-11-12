"""examples/pilot/reemplaza.sh: mueve el destino a descartes/, copia la nueva y anota el LEEME.md."""
import subprocess
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
SCRIPT = R / 'examples' / 'pilot' / 'reemplaza.sh'


class ReemplazaTests(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.d = Path(self._t.name) / 'con espacios'
        self.d.mkdir()
        self.nueva = Path(self._t.name) / 'nueva img.png'
        self.nueva.write_bytes(b'NUEVA')

    def run_(self):
        return subprocess.run(['bash', str(SCRIPT), str(self.nueva), str(self.d / '07 a.png')],
                              capture_output=True, text=True)

    def test_destino_inexistente(self):
        p = self.run_()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((self.d / '07 a.png').read_bytes(), b'NUEVA')
        self.assertFalse((self.d / 'descartes').exists())
        self.assertIn('07 a.png: nuevo', (self.d / 'LEEME.md').read_text())

    def test_destino_existente(self):
        (self.d / '07 a.png').write_bytes(b'VIEJA')
        p = self.run_()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((self.d / '07 a.png').read_bytes(), b'NUEVA')
        self.assertEqual((self.d / 'descartes' / '07 a-anterior.png').read_bytes(), b'VIEJA')
        self.assertIn('descartes/07 a-anterior.png', (self.d / 'LEEME.md').read_text())

    def test_descarte_ya_existente_no_se_pisa(self):
        (self.d / 'descartes').mkdir()
        (self.d / 'descartes' / '07 a-anterior.png').write_bytes(b'PRIMERA')
        (self.d / '07 a.png').write_bytes(b'VIEJA')
        p = self.run_()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual((self.d / 'descartes' / '07 a-anterior.png').read_bytes(), b'PRIMERA')
        self.assertEqual((self.d / 'descartes' / '07 a-anterior-2.png').read_bytes(), b'VIEJA')

    def test_leeme_ausente_se_crea_y_presente_se_conserva(self):
        self.run_()
        self.assertTrue((self.d / 'LEEME.md').is_file())
        (self.d / 'LEEME.md').write_text('previo\n')
        self.run_()
        t = (self.d / 'LEEME.md').read_text()
        self.assertTrue(t.startswith('previo\n'))
        self.assertIn('descartes/07 a-anterior.png', t)

    def test_falla_si_falta_la_nueva(self):
        self.nueva.unlink()
        p = self.run_()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('no existe la nueva', p.stderr)


if __name__ == '__main__':
    unittest.main()
