"""Ganchos de sesión: el aviso de presupuesto de compactaciones (recuperar.py) y el rechazo de lecturas enteras."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
_scripts = str(R / '.claude' / 'gw' / 'scripts')
sys.path.insert(0, _scripts)  # recuperar importa config de su carpeta; se quita para no tapar otros módulos
try:
    import recuperar  # noqa: E402
finally:
    sys.path.remove(_scripts)

_spec = importlib.util.spec_from_file_location('leer_entero', R / '.claude' / 'hooks' / 'leer-entero.py')
leer_entero = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(leer_entero)


class PresupuestoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='presupuesto-'))
        self.addCleanup(shutil.rmtree, self.tmp)
        git = ['git', '-C', str(self.tmp), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
        subprocess.run(['git', 'init', '-q', str(self.tmp)], check=True)
        subprocess.run(git + ['checkout', '-q', '-b', 'x'], check=True)
        subprocess.run(git + ['commit', '-q', '--allow-empty', '--no-verify', '-m', 'inicio'], check=True)
        (self.tmp / '.claude').mkdir()
        shutil.copy(R / '.claude' / 'gw.json', self.tmp / '.claude' / 'gw.json')
        log = json.loads((R / '.claude' / 'gw.json').read_text(encoding='utf-8'))['log']
        self.log = self.tmp / log
        self.log.parent.mkdir(parents=True, exist_ok=True)

    def fila(self, texto):
        self.log.write_text(f'| Campo | Valor |\n|---|---|\n| **Tarea en curso · `x`** | {texto} |\n',
                            encoding='utf-8')
        return recuperar.compaction_budget(self.tmp, 'x')

    def test_lee_el_presupuesto_de_la_fila_de_la_rama(self):
        self.assertEqual(self.fila('F2.0. Presupuesto: 4 compactaciones (5 gastadas)'), 4)
        self.assertEqual(self.fila('Budget: 2 compactions'), 2)
        self.assertEqual(self.fila('F2: 3 compactaciones gastadas. Presupuesto: 4 compactaciones'), 4)

    def test_sin_presupuesto_o_sin_fila(self):
        self.assertIsNone(self.fila('F2.0 sin presupuesto'))
        self.assertIsNone(recuperar.compaction_budget(self.tmp, 'otra'))

    def test_sin_numero_de_presupuesto(self):
        self.assertIsNone(self.fila('F2: 3 compactaciones gastadas'))

    def estado(self, compactaciones):
        sesion = self.tmp / 's.jsonl'
        sesion.write_text('{"type": "system", "subtype": "compact_boundary"}\n' * compactaciones, encoding='utf-8')
        return subprocess.run([sys.executable, str(R / '.claude' / 'gw' / 'scripts' / 'recuperar.py'), '--estado',
                               '--root', str(self.tmp), '--sesion', str(sesion)],
                              capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout

    def test_estado_avisa_al_pasarse(self):
        self.fila('Presupuesto: 1 compactación')
        self.assertIn('Over the compaction budget (2 of 1)', self.estado(2))

    def test_estado_no_avisa_al_llegar_justo(self):
        self.fila('Presupuesto: 2 compactaciones')
        salida = self.estado(2)
        self.assertIn('Compactions in this session: 2', salida)
        self.assertNotIn('Over the compaction budget', salida)


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
