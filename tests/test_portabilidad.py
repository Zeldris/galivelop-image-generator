"""Comprobaciones mecánicas de REVIEW.md: shell de bash 3.2 (macOS) y JS de las páginas que se abren en el navegador."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]

# Lo que bash 3.2 o las herramientas BSD de macOS no tienen, o donde dan otra salida (wc mete espacios).
NO_PORTABLE = {
    r'readlink -f': 'readlink -f no existe en macOS < 12.3: cd "$(dirname "$0")/.." && pwd',
    r'\b(mapfile|readarray)\b': 'mapfile/readarray son de bash 4',
    r'\b(declare|local|typeset) -[a-zA-Z]*A': 'los arrays asociativos son de bash 4',
    r'\$\{\w+(,|\^)': '${v,}, ${v,,}, ${v^} y ${v^^} son de bash 4',
    r'wc -[lwc][^|)]*\)"?\s*!?==?(?!~)': 'wc mete espacios en BSD: compara con -eq o quita espacios con tr -d " "',
}


def problemas(texto):
    return [(n, motivo) for n, linea in enumerate(texto.splitlines(), 1)
            if not linea.lstrip().startswith('#')
            for patron, motivo in NO_PORTABLE.items() if re.search(patron, linea)]


def scripts_de_shell():
    salida = subprocess.run(['git', 'ls-files', '-z', '*.sh', '.githooks/*'], cwd=R, capture_output=True, text=True,
                            check=True).stdout
    return [R / f for f in salida.split('\0') if f]


class ShellPortableTests(unittest.TestCase):
    def test_los_patrones_cazan_lo_que_rompe_en_macos(self):
        malo = ('R=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)\nmapfile -t L < f\ndeclare -A m\necho ${x,,}\n'
                '[ "$(ls | wc -l)" = 3 ]\n')
        self.assertEqual([n for n, _ in problemas(malo)], [1, 2, 3, 4, 5])
        variantes = 'declare -gA m\nlocal -Ag m\necho ${x,}\necho ${x^}\necho ${x,,[a-z]}\n[[ $(wc -l < f) == 3 ]]\n'
        self.assertEqual([n for n, _ in problemas(variantes)], [1, 2, 3, 4, 5, 6])
        self.assertEqual(problemas('# readlink -f en un comentario\n[ "$(ls | wc -l | tr -d " ")" -eq 3 ]\n'
                                   'declare -a lista\necho ${x:-y} ${#x}\n[[ $(wc -l < f) =~ ^ *3$ ]]\n'), [])

    def test_ningun_script_del_repo_usa_lo_que_rompe_en_macos(self):
        encontrados = [f'{f.relative_to(R)}:{n}: {motivo}' for f in scripts_de_shell()
                       for n, motivo in problemas(f.read_text(encoding='utf-8', errors='replace'))]
        self.assertEqual(encontrados, [])


def scripts_en_linea(html):
    """El JS de cada <script> en línea, con o sin atributos (los de `src=` no traen código)."""
    return [m.group(1) for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S | re.I)]


@unittest.skipUnless(shutil.which('node'), 'sin node: el CI de GitHub lo trae')
class JsTests(unittest.TestCase):
    def comprobar(self, nombre, codigo):
        with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
            f.write(codigo)
        self.addCleanup(Path(f.name).unlink)
        r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f'{nombre}: {r.stderr}')

    def test_detecta_un_js_roto(self):
        with self.assertRaisesRegex(AssertionError, 'SyntaxError'):
            self.comprobar('roto', 'function f( {')

    def test_saca_el_js_de_script_con_atributos(self):
        html = '<script>a()</script><script type="module">b()</script><script src="c.js"></script><SCRIPT>d()</SCRIPT>'
        self.assertEqual(scripts_en_linea(html), ['a()', 'b()', 'd()'])

    def test_el_js_del_prototipo_es_valido(self):
        trozos = scripts_en_linea((R / 'docs/interfaz/prototipo/index.html').read_text(encoding='utf-8'))
        self.assertTrue(trozos)
        for i, codigo in enumerate(trozos):
            self.comprobar(f'prototipo, <script> {i + 1}', codigo)

    def test_el_js_de_las_paginas_del_piloto_es_valido(self):
        piloto = str(R / 'examples' / 'pilot')
        sys.path.insert(0, piloto)
        self.addCleanup(sys.path.remove, piloto)
        import pagina
        self.comprobar('pagina.JS', pagina.JS)


if __name__ == '__main__':
    unittest.main()
