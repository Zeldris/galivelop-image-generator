"""Ganchos de sesión: el rechazo de lecturas enteras (el aviso de presupuesto de compactaciones es del flujo desde la v0.5.0)."""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
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
        d = intentos_en_hoja.decision({'tool_name': 'Read', 'tool_input': {'file_path': '/x/attempts/q2-d-dark.png'}})
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

    def test_sin_session_id_se_comporta_igual_con_clave_de_reserva(self):
        with tempfile.TemporaryDirectory() as carpeta:
            datos = lambda ruta: {'tool_name': 'Read', 'tool_input': {'file_path': ruta}}  # noqa: E731
            self.assertIsNone(intentos_en_hoja.decision(datos('/tmp/c/scratchpad/una.png'), carpeta))
            self.assertIn('gimg sheet', intentos_en_hoja.decision(
                datos('/tmp/c/scratchpad/dos.png'), carpeta)['hookSpecificOutput']['additionalContext'])

    def test_la_clave_sin_session_id_depende_de_transcript_y_de_ppid(self):
        from unittest import mock
        ruta = '/tmp/c/scratchpad/a.png'
        def primera(carpeta, **extra):
            datos = {'tool_name': 'Read', 'tool_input': {'file_path': ruta}, **extra}
            return intentos_en_hoja.decision(datos, carpeta) is None
        with tempfile.TemporaryDirectory() as c:  # transcript distintos: marcas distintas; el mismo: la misma
            self.assertTrue(primera(c, transcript_path='/t/1.jsonl'))
            self.assertTrue(primera(c, transcript_path='/t/2.jsonl'))
            self.assertFalse(primera(c, transcript_path='/t/1.jsonl'))
        with tempfile.TemporaryDirectory() as c:  # sin transcript: el ppid
            with mock.patch.object(os, 'getppid', return_value=111):
                self.assertTrue(primera(c))
                self.assertFalse(primera(c))
            with mock.patch.object(os, 'getppid', return_value=222):
                self.assertTrue(primera(c))

    def test_usar_la_marca_renueva_su_mtime(self):
        with tempfile.TemporaryDirectory() as c:
            datos = {'tool_name': 'Read', 'session_id': 's', 'tool_input': {'file_path': '/tmp/c/scratchpad/a.png'}}
            intentos_en_hoja.decision(datos, c)
            marca = os.path.join(c, os.listdir(c)[0])
            antes = time.time() - 3600
            os.utime(marca, (antes, antes))
            intentos_en_hoja.decision(datos, c)
            self.assertGreater(os.path.getmtime(marca), antes + 1800)

    def test_las_marcas_viejas_se_borran_y_las_recientes_no(self):
        with tempfile.TemporaryDirectory() as carpeta:
            vieja = os.path.join(carpeta, 'gimg-captura-vieja')
            reciente = os.path.join(carpeta, 'gimg-captura-reciente')
            ajena = os.path.join(carpeta, 'otra-cosa')
            for ruta in (vieja, reciente, ajena):
                open(ruta, 'w').close()
            antes = time.time() - 2 * 24 * 3600
            os.utime(vieja, (antes, antes))
            os.utime(ajena, (antes, antes))
            intentos_en_hoja.decision({'tool_name': 'Read', 'session_id': 's',
                                       'tool_input': {'file_path': '/tmp/c/scratchpad/a.png'}}, carpeta)
            self.assertFalse(os.path.exists(vieja))
            self.assertTrue(os.path.exists(reciente))
            self.assertTrue(os.path.exists(ajena))

    def _leer_en_tmp(self, tmp, sesion):
        from unittest import mock
        datos = {'tool_name': 'Read', 'session_id': sesion, 'tool_input': {'file_path': '/tmp/c/scratchpad/a.png'}}
        with mock.patch.object(tempfile, 'gettempdir', return_value=tmp):
            return intentos_en_hoja.decision(datos)

    def test_carpeta_por_usuario_con_permisos_700(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(self._leer_en_tmp(tmp, 's1'))
            carpetas = [p for p in Path(tmp).iterdir() if p.name.startswith('gimg-capturas-')]
            self.assertEqual(len(carpetas), 1)
            self.assertEqual(carpetas[0].stat().st_mode & 0o777, 0o700)
            self.assertEqual(len(list(carpetas[0].iterdir())), 1)

    @unittest.skipUnless(hasattr(os, 'symlink') and hasattr(os, 'getuid'), 'symlinks y uid de POSIX')
    def test_carpeta_plantada_como_symlink_no_se_toca(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as victima:
            os.symlink(victima, os.path.join(tmp, 'gimg-capturas-%d' % os.getuid()))
            self.assertIsNone(self._leer_en_tmp(tmp, 's1'))  # falla abierto, sin aviso
            self.assertEqual(os.listdir(victima), [])

    @unittest.skipUnless(hasattr(os, 'getuid'), 'uid de POSIX')
    def test_carpeta_con_permisos_de_grupo_u_otros_se_rechaza(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = os.path.join(tmp, 'gimg-capturas-%d' % os.getuid())
            os.mkdir(c)
            os.chmod(c, 0o755)
            self.assertIsNone(self._leer_en_tmp(tmp, 's1'))
            self.assertEqual(os.listdir(c), [])

    @unittest.skipUnless(hasattr(os, 'symlink') and os.utime in os.supports_follow_symlinks, 'symlinks y utime')
    def test_marca_plantada_como_symlink_no_toca_el_mtime_de_su_destino(self):
        with tempfile.TemporaryDirectory() as carpeta, tempfile.TemporaryDirectory() as victima:
            objetivo = os.path.join(victima, 'objetivo')
            Path(objetivo).write_text('x')
            os.utime(objetivo, (1000, 1000))
            datos = {'tool_name': 'Read', 'session_id': 's1', 'tool_input': {'file_path': '/tmp/c/scratchpad/a.png'}}
            intentos_en_hoja.decision(datos, carpeta)  # crea la marca real; la cambiamos por un enlace
            marca = os.path.join(carpeta, os.listdir(carpeta)[0])
            os.remove(marca)
            os.symlink(objetivo, marca)
            d = intentos_en_hoja.decision(datos, carpeta)
            self.assertIn('gimg sheet', d['hookSpecificOutput']['additionalContext'])  # la marca existe: avisa
            self.assertEqual(os.stat(objetivo).st_mtime, 1000)

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symlinks')
    def test_la_limpieza_no_sigue_symlinks(self):
        with tempfile.TemporaryDirectory() as carpeta, tempfile.TemporaryDirectory() as victima:
            objetivo = os.path.join(victima, 'objetivo')
            Path(objetivo).write_text('x')
            antes = time.time() - 2 * 24 * 3600
            os.utime(objetivo, (antes, antes))
            os.symlink(objetivo, os.path.join(carpeta, 'gimg-captura-enlace'))
            intentos_en_hoja.decision({'tool_name': 'Read', 'session_id': 's',
                                       'tool_input': {'file_path': '/tmp/c/scratchpad/a.png'}}, carpeta)
            self.assertTrue(os.path.exists(objetivo))

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
