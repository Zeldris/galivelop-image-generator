"""Ganchos de sesión: el rechazo de lecturas enteras (el aviso de presupuesto de compactaciones es del flujo desde la v0.5.0)."""
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('leer_entero', R / '.claude' / 'hooks' / 'leer-entero.py')
leer_entero = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(leer_entero)


class LeerEnteroTests(unittest.TestCase):
    def leer(self, ruta, **extra):
        return leer_entero.decision({'tool_name': 'Read', 'tool_input': {'file_path': str(ruta), **extra}}, str(R))

    def test_rechaza_el_plan_entero_y_dice_como_leerlo(self):
        d = self.leer(R / 'docs' / 'plan.md')
        self.assertEqual(d['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('grep -n', d['hookSpecificOutput']['permissionDecisionReason'])

    def test_deja_pasar_con_limite_u_otro_archivo(self):
        self.assertIsNone(self.leer(R / 'docs' / 'plan.md', offset=30, limit=20))
        self.assertIsNone(self.leer(R / 'docs' / 'plan.md', limit=leer_entero.MAX_LINEAS))
        self.assertIsNone(self.leer(R / 'AGENTS.md'))
        self.assertIsNone(leer_entero.decision({'tool_name': 'Bash', 'tool_input': {}}, str(R)))

    def test_rechaza_un_limite_que_lo_lee_casi_entero(self):
        for extra in ({'offset': 1}, {'limit': 2000}, {'offset': 1, 'limit': leer_entero.MAX_LINEAS + 1},
                      {'limit': True}, {'limit': 0}):
            with self.subTest(extra=extra):
                self.assertEqual(self.leer(R / 'docs' / 'plan.md', **extra)['hookSpecificOutput']['permissionDecision'],
                                 'deny')

    def test_rechaza_el_plan_de_un_worktree(self):
        with tempfile.TemporaryDirectory(prefix='worktree-') as wt:
            (Path(wt) / '.claude').mkdir()
            (Path(wt) / '.claude' / 'gw.json').write_text('{}', encoding='utf-8')
            d = self.leer(Path(wt) / 'docs' / 'plan.md')
            self.assertEqual(d['hookSpecificOutput']['permissionDecision'], 'deny')
            self.assertIsNone(self.leer(Path(wt) / 'otro' / 'docs' / 'plan.md'))

    def test_el_grep_sugerido_encuentra_las_filas(self):
        orden = re.match(r'grep .*? docs/plan\.md', leer_entero.GRANDES['docs/plan.md']).group()
        salida = subprocess.run(orden, shell=True, cwd=R, capture_output=True, text=True).stdout
        self.assertRegex(salida, r'^\d+:\| D22 ')
        self.assertIn('| F2.4 ', salida)


if __name__ == '__main__':
    unittest.main()
