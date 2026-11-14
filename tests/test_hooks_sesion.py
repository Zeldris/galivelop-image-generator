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



_spec2 = importlib.util.spec_from_file_location('intentos_en_hoja', R / '.claude' / 'hooks' / 'intentos-en-hoja.py')
intentos_en_hoja = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(intentos_en_hoja)


class IntentosEnHojaTests(unittest.TestCase):
    def test_avisa_sin_bloquear_en_un_intento(self):
        d = intentos_en_hoja.decision({'tool_name': 'Read', 'tool_input': {'file_path': '/x/attempts/q123-a.png'}})
        h = d['hookSpecificOutput']
        self.assertEqual(h['hookEventName'], 'PreToolUse')
        self.assertIn('gimg sheet', h['additionalContext'])
        self.assertNotIn('permissionDecision', h)

    def test_avisa_tambien_con_capturas_del_scratchpad(self):
        d = intentos_en_hoja.decision({'tool_name': 'Read', 'tool_input': {'file_path': '/tmp/c/scratchpad/r2/pedidos-d-dark.png'}})
        self.assertIn('gimg sheet', d['hookSpecificOutput']['additionalContext'])

    def test_la_primera_captura_de_la_sesion_pasa_y_avisa_desde_la_segunda(self):
        with tempfile.TemporaryDirectory() as carpeta:
            def leer(ruta, sesion='s1'):
                return intentos_en_hoja.decision(
                    {'tool_name': 'Read', 'session_id': sesion, 'tool_input': {'file_path': ruta}}, carpeta)
            self.assertIsNone(leer('/tmp/c/scratchpad/una.png'))
            self.assertIn('gimg sheet', leer('/tmp/c/scratchpad/dos.png')['hookSpecificOutput']['additionalContext'])
            self.assertIsNone(leer('/tmp/c/scratchpad/otra.png', 's2'))
            self.assertIn('gimg sheet', leer('/x/attempts/q9.png', 's3')['hookSpecificOutput']['additionalContext'])

    def test_avisa_tambien_con_jpg_y_webp(self):
        for ext in ('jpg', 'JPEG', 'webp'):
            d = intentos_en_hoja.decision({'tool_name': 'Read', 'tool_input': {'file_path': f'/x/attempts/q1.{ext}'}})
            self.assertIn('gimg sheet', d['hookSpecificOutput']['additionalContext'], ext)

    def test_calla_en_lo_demas(self):
        for datos in ({'tool_name': 'Read', 'tool_input': {'file_path': '/x/aprobadas/01.png'}},
                      {'tool_name': 'Read', 'tool_input': {'file_path': '/x/attempts/q1.json'}},
                      {'tool_name': 'Read', 'tool_input': {'file_path': '/tmp/c/scratchpad/r2/hoja-r2.png'}},
                      {'tool_name': 'Bash', 'tool_input': {'file_path': '/x/attempts/q1.png'}}):
            self.assertIsNone(intentos_en_hoja.decision(datos))


if __name__ == '__main__':
    unittest.main()
