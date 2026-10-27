#!/usr/bin/env python3
"""Página de revisión de las propuestas de logo de docs/marcas/<proyecto>/logos/.

Uso: examples/pilot/logos.py [carpeta de salida]   (por defecto piloto/logos)
Cada propuesta sale con su símbolo sobre claro y oscuro, a 128, 32 y 16 px, y su lockup, con botones sí/no y «Copiar
veredicto» como las rondas (pagina.py). Los SVG van en línea, así que las fuentes de Google se aplican al texto.
"""
import re
import sys
from pathlib import Path

from pagina import CSS, JS, esc

R = Path(__file__).resolve().parents[2]
MARCAS = R / 'docs' / 'marcas'
FUENTES = ('https://fonts.googleapis.com/css2?family=Sora:wght@700&family=Inter:wght@400;800'
           '&family=Cormorant+Garamond:wght@300;400&family=DM+Sans:wght@400;500&family=Cinzel:wght@400;700&display=swap')
MAS_CSS = """
.prop { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:10px 0 4px; }
.caja { border-radius:8px; padding:10px; display:flex; gap:10px; align-items:center; }
.claro { background:#f6f4f0; } .oscuro { background:#06121c; }
.s128 { width:128px; height:128px; } .s32 { width:32px; height:32px; } .s16 { width:16px; height:16px; }
.s128 svg, .s32 svg, .s16 svg { width:100%; height:100%; display:block; }
.lockup svg { height:64px; width:auto; display:block; }
h3 { margin:14px 0 0; font-size:15px; }
"""


def svg(f):
    """El SVG sin la declaración XML, listo para ir en línea."""
    return re.sub(r'<\?xml[^>]*\?>', '', f.read_text(encoding='utf-8')).strip()


def concepto(f):
    m = re.search(r'<!--\s*(.*?)\s*-->', f.read_text(encoding='utf-8'), re.S)
    return m.group(1) if m else ''


def tarjeta(proy, f):
    nombre = f.stem
    lock = f.with_name(f'{nombre}-lockup.svg')
    s = svg(f)
    cajas = ''.join(f'<div class="caja {fondo}"><div class="s128">{s}</div><div class="s32">{s}</div>'
                    f'<div class="s16">{s}</div></div>' for fondo in ('claro', 'oscuro'))
    if lock.exists():
        # Un lockup hecho para un solo fondo lo dice con data-fondo; si no, va sobre los dos.
        m = re.search(r'<svg[^>]*\sdata-fondo="(claro|oscuro)"', lock.read_text(encoding='utf-8'))
        fondos = (m.group(1),) if m else ('claro', 'oscuro')
        cajas += ''.join(f'<div class="caja {fondo} lockup">{svg(lock)}</div>' for fondo in fondos)
    for var in sorted(f.parent.glob(f'{nombre}-lockup-*.svg')):
        fondo = 'claro' if var.stem.endswith('-claro') else 'oscuro'
        cajas += f'<div class="caja {fondo} lockup">{svg(var)}</div>'
    return (f'<figure data-pieza="{esc(nombre)}" style="max-width:none"><h3>{esc(nombre)}</h3>'
            f'<figcaption>{esc(concepto(f))}</figcaption><div class="prop">{cajas}</div>'
            f'<figcaption><button class="si">sí</button><button class="no">no</button></figcaption></figure>')


def main(argv):
    out = Path(argv[1]) if len(argv) > 1 else R / 'piloto' / 'logos'
    secciones = []
    for d in sorted(p for p in MARCAS.iterdir() if (p / 'logos').is_dir()):
        # Los lockups, también sus variantes de fondo (-lockup-claro, -lockup-oscuro), van con su símbolo.
        props = sorted(f for f in (d / 'logos').glob('*.svg') if '-lockup' not in f.stem)
        if props:
            secciones.append(f'<section><h2>{esc(d.name)}</h2>{"".join(tarjeta(d.name, f) for f in props)}</section>')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(
        f'<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f'<title>Propuestas de logo</title><link rel="stylesheet" href="{FUENTES}"><style>{CSS}{MAS_CSS}</style>'
        f'<body data-ronda="logos"><p><a href="../index.html">← piloto</a></p><h1>Propuestas de logo</h1>'
        f'<p>Cada propuesta: símbolo a 128, 32 y 16 px sobre claro y oscuro, y su lockup. Marca sí/no y pega el veredicto '
        f'en el chat. Las biblias están en <code>docs/marcas/</code>.</p>{"".join(secciones)}'
        f'<section><h2>Veredicto</h2><textarea id="veredicto" readonly></textarea>'
        f'<p><button id="copiar">Copiar veredicto</button></p></section><script>{JS}</script></body></html>', encoding='utf-8')
    print(f'Página: {out / "index.html"}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
