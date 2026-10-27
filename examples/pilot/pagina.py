#!/usr/bin/env python3
"""F2.0: página de revisión de las rondas del piloto, para mirarlas en el navegador.

Uso: examples/pilot/pagina.py <carpeta del piloto>
Escribe <piloto>/<ronda>/index.html (proyecto a proyecto: prompt, intentos lado a lado, tiempos y botones sí/no) y
<piloto>/index.html con las rondas. Los sí/no se guardan en el navegador; «Copiar veredicto» da el texto para pegarlo
en el chat. Lee lo que dejan ronda.sh y el generar.sh de Tarkor: <proyecto>/{intentos,prompts,logs}/ y resumen.txt.
"""
import html
import json
import re
import sys
from pathlib import Path

CSS = """
:root { color-scheme: dark; --bg:#111318; --panel:#1b1e25; --texto:#e6e6e6; --tenue:#9aa0aa; --si:#2e9e5b; --no:#c0392b; }
body { margin:0; padding:16px; background:var(--bg); color:var(--texto); font:15px/1.5 system-ui, sans-serif; }
h1 { margin:0 0 4px; } a { color:#7cc4ff; }
section { background:var(--panel); border-radius:10px; padding:14px; margin:18px 0; }
.fila { display:flex; flex-wrap:wrap; gap:12px; }
figure { margin:0; flex:1 1 420px; max-width:640px; }
figure img { width:100%; border-radius:6px; display:block; cursor:zoom-in; }
figcaption { color:var(--tenue); font-size:13px; margin-top:4px; display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
details { color:var(--tenue); font-size:13px; margin-bottom:8px; } details p { white-space:pre-wrap; color:var(--texto); }
button { background:#2a2f3a; color:var(--texto); border:1px solid #3a404c; border-radius:6px; padding:2px 10px; cursor:pointer; }
button.si.on { background:var(--si); } button.no.on { background:var(--no); }
#aviso { background:#5a3a10; padding:8px 12px; border-radius:6px; }
textarea { width:100%; height:9em; background:var(--panel); color:var(--texto); border:1px solid #3a404c; border-radius:6px; }
"""

JS = """
const R = document.body.dataset.ronda;
const clave = id => 'piloto:' + R + ':' + id;
function lee(id) { try { return localStorage.getItem(clave(id)) || ''; } catch (e) { return ''; } }
function pinta() {
  const lineas = [];
  document.querySelectorAll('[data-pieza]').forEach(f => {
    const v = lee(f.dataset.pieza);
    f.querySelector('.si').classList.toggle('on', v === 'sí');
    f.querySelector('.no').classList.toggle('on', v === 'no');
    if (v) lineas.push(f.dataset.pieza + ' ' + v);
  });
  document.getElementById('veredicto').value = R + ': ' + (lineas.join(', ') || '(sin marcar)');
}
document.querySelectorAll('[data-pieza]').forEach(f => f.querySelectorAll('button').forEach(b => b.onclick = () => {
  const v = b.classList.contains('si') ? 'sí' : 'no';
  try { localStorage.setItem(clave(f.dataset.pieza), lee(f.dataset.pieza) === v ? '' : v); } catch (e) {}
  pinta();
}));
document.getElementById('copiar').onclick = () => {
  const t = document.getElementById('veredicto'); t.select(); navigator.clipboard?.writeText(t.value);
};
pinta();
// Abierta como archivo desde un flatpak, el portal da solo el HTML y no las imágenes: avisa una vez.
addEventListener('error', e => {
  if (e.target.tagName !== 'IMG' || location.protocol !== 'file:' || document.getElementById('aviso')) return;
  const p = document.createElement('p'); p.id = 'aviso';
  p.textContent = 'Las imágenes no cargan abiertas como archivo (pasa con VS Code o el navegador en flatpak). '
    + 'Ábrelas con: python3 examples/pilot/ver.py';
  document.body.prepend(p);
}, true);
"""


def esc(s):
    return html.escape(str(s))


def resumen(ronda):
    """{(proyecto, nombre): línea} de resumen.txt; las líneas sin proyecto delante (r0 y r1) no se reparten."""
    datos = {}
    f = ronda / 'resumen.txt'
    for linea in f.read_text().splitlines() if f.exists() else []:
        m = re.match(r'(\S+) (\S+) salida=', linea)
        if m:
            datos[m.groups()] = linea
    return datos


def tiempos(log, linea):
    t = log.read_text(errors='replace') if log.exists() else ''
    partes = []
    for etiqueta, patron in (('muestreo', r'sampling completed, taking ([0-9.]+)s'),
                             ('decodificar', r'decode_first_stage completed, taking ([0-9.]+)s')):
        m = re.search(patron, t)
        if m:
            partes.append(f'{etiqueta} {float(m.group(1)):.0f} s')
    for etiqueta, patron in (('total', r'total=(\d+s)'), ('mín. libre', r'min_libre=(\d+MB)'),
                             ('salida', r'salida=(\d+)')):
        m = re.search(patron, linea or '')
        if m:
            partes.append(f'{etiqueta} {m.group(1)}')
    return ' · '.join(partes)


def medidas(f):
    """Las medidas de piezas.py (r4, r5): contraste de la zona de texto y paleta."""
    if not f.exists():
        return ''
    m = json.loads(f.read_text())
    c, pal = m.get('contraste'), m.get('paleta')
    partes = ([f'contraste {c.get("media")}:1, peor {c.get("peor")}:1'] if c else []) + \
             ([f'paleta {pal.get("porcentaje")} %'] if pal else []) + ([f'YAVG {m["YAVG"]}'] if 'YAVG' in m else [])
    return ' · '.join(partes)


def pagina_ronda(ronda):
    res = resumen(ronda)
    secciones = []
    for proy in sorted(p for p in ronda.iterdir() if (p / 'intentos').is_dir()):
        figuras, prompts = [], []
        for img in sorted((proy / 'intentos').glob('*.png')):
            n = img.stem
            pf = proy / 'prompts' / f'{n}.txt'
            if pf.exists():
                prompts.append((n, pf.read_text()))
            rel = img.relative_to(ronda).as_posix()
            pieza = f'{proy.name} {n.removeprefix("og-")}'
            info = ' · '.join(filter(None, (tiempos(proy / 'logs' / f'{n}.log', res.get((proy.name, n))),
                                            medidas(proy / 'medidas' / f'{n}.json'))))
            figuras.append(
                f'<figure data-pieza="{esc(pieza)}"><a href="{esc(rel)}" target="_blank"><img src="{esc(rel)}" '
                f'alt="{esc(pieza)}" loading="lazy"></a><figcaption><b>{esc(n)}</b> {esc(info)} '
                f'<button class="si">sí</button><button class="no">no</button></figcaption></figure>')
        # Un prompt para todas (r1: varias semillas) o uno por imagen (r2: variantes del estilo).
        distintos = {t for _, t in prompts}
        detalles = ''.join(f'<details><summary>Prompt{"" if len(distintos) == 1 else " " + esc(n)}</summary>'
                           f'<p>{esc(t)}</p></details>' for n, t in (prompts[:1] if len(distintos) == 1 else prompts))
        secciones.append(f'<section><h2>{esc(proy.name)}</h2>{detalles}<div class="fila">{"".join(figuras)}</div></section>')
    hoja = '<p><a href="hoja.png" target="_blank">Hoja de contacto</a></p>' if (ronda / 'hoja.png').exists() else ''
    (ronda / 'index.html').write_text(
        f'<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f'<title>Piloto {esc(ronda.name)}</title><style>{CSS}</style><body data-ronda="{esc(ronda.name)}">'
        f'<p><a href="../index.html">← rondas</a></p><h1>Ronda {esc(ronda.name)}</h1>{hoja}'
        f'<p>Pincha una imagen para verla a tamaño real. Marca sí/no y pega el veredicto en el chat.</p>'
        f'{"".join(secciones)}<section><h2>Veredicto</h2><textarea id="veredicto" readonly></textarea>'
        f'<p><button id="copiar">Copiar veredicto</button></p></section><script>{JS}</script></body></html>')


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2])
        return 2
    piloto = Path(argv[1])
    rondas = sorted(r for r in piloto.iterdir() if r.is_dir() and any(r.glob('*/intentos/*.png')))
    for r in rondas:
        pagina_ronda(r)
    enlaces = ''.join(f'<li><a href="{esc(r.name)}/index.html">{esc(r.name)}</a> · '
                      f'{len(list(r.glob("*/intentos/*.png")))} imágenes</li>' for r in rondas)
    if (piloto / 'logos' / 'index.html').exists():
        enlaces += '<li><a href="logos/index.html">Propuestas de logo</a> (examples/pilot/logos.py)</li>'
    (piloto / 'index.html').write_text(
        f'<!doctype html><html lang="es"><meta charset="utf-8"><title>Piloto de contenido</title><style>{CSS}</style>'
        f'<body><h1>Piloto de contenido</h1><p>Si no se ven las imágenes, ábrelo con <code>python3 examples/pilot/ver.py'
        f'</code> (desde VS Code en flatpak, el archivo llega sin sus imágenes).</p><ul>{enlaces}</ul></body></html>')
    print(f'Página: {piloto / "index.html"}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
