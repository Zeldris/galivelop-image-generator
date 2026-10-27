#!/usr/bin/env python3
"""F2.0: compone y mide las piezas de una ronda (r4, r5) desde examples/<proyecto>/piezas.json.

Uso: examples/pilot/piezas.py <ronda> [proyecto...]   (por defecto, los que tengan piezas.json)
Cada pieza de esa ronda sale en piloto/<ronda>/<proyecto>/intentos/<id>.png, con su SVG de depuración en
<proyecto>/svg/ y sus medidas en <proyecto>/medidas/<id>.json (pagina.py las enseña):
- El fondo es el definitivo generado con el prompt `fondo`: piloto/r5-fondos/ y si no piloto/r3/, el más grande que
  no sea borrador (640×320) ni FLUX.3. `"fondo": null` es un avatar: solo el logo, rasterizado al tamaño.
- Contraste: en la caja de la zona (componer.caja_zona) del fondo con el velo y sin el texto, contra color_texto.
- Paleta: los hex de la biblia, leídos de examples/<proyecto>/prompts/r2-hex.txt; el estilo elegido puede decir el
  color con palabras o materiales, y se mide igual contra la paleta de marca.
"""
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import componer
import medir

R = Path(__file__).resolve().parents[2]
PILOTO = R / 'piloto'
ID = re.compile(r'[a-z0-9][a-z0-9-]{0,39}')
OBLIGATORIOS = ('id', 'ancho', 'alto', 'logo')
CON_FONDO = ('titulo', 'zona', 'color_texto', 'velo')


def rel(f):
    return str(f.relative_to(R)) if f.is_relative_to(R) else str(f)


def fondo_de(proy, prompt):
    for ronda in ('r5-fondos', 'r3'):
        base = (PILOTO / ronda / proy / 'intentos').resolve()
        c = []
        for f in base.glob(f'{prompt}-*.png'):
            if '640x320' in f.name or 'flux3' in f.name or not f.resolve().is_relative_to(base):
                continue
            ancho, alto = medir.tamano(str(f))  # un ffprobe por archivo
            c.append((ancho * alto, f.name, f))
        if c:
            return max(c)[2]  # el de más área y, a igualdad, el de nombre mayor: no depende del orden del glob
    raise componer.ErrorComponer(f'no hay fondo de {proy}/{prompt} en piloto/r5-fondos ni piloto/r3')


def paleta_de(proy):
    f = R / 'examples' / proy / 'prompts' / 'r2-hex.txt'
    return [medir.hex_rgb(h) for h in sorted(set(re.findall(r'#[0-9A-Fa-f]{6}', f.read_text(encoding='utf-8'))))] if f.exists() else []


def _nombre_seguro(campo, valor):
    """D25: un nombre suelto (sin ruta): cadena sin separadores, `..`, `~`, saltos de línea ni NUL."""
    if (not isinstance(valor, str) or not valor or valor in ('.', '..') or valor.startswith('~')
            or any(c in valor for c in '/\\\n\r\x00*?[]') or '..' in valor):
        raise componer.ErrorComponer(f'{campo} {valor!r}: tiene que ser un nombre sin ruta, sin «..», «~», comodines ni saltos de línea')


def _entero_positivo(campo, valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise componer.ErrorComponer(f'{campo} {valor!r}: tiene que ser un entero positivo')


def validar(p):
    """Los campos que faltan, sus tipos y que el id, el fondo y el logo no se salgan de su sitio (D25 de REVIEW.md)."""
    if 'fondo' not in p:
        raise componer.ErrorComponer('falta el campo «fondo» (null para un avatar)')
    falta = [c for c in OBLIGATORIOS + (CON_FONDO if p['fondo'] is not None else ()) if c not in p]
    if falta:
        raise componer.ErrorComponer('falta el campo ' + ', '.join(f'«{c}»' for c in falta))
    if not isinstance(p['id'], str) or not ID.fullmatch(p['id']):
        raise componer.ErrorComponer(f'id {p["id"]!r}: solo minúsculas, cifras y guiones, hasta 40')
    _entero_positivo('ancho', p['ancho'])
    _entero_positivo('alto', p['alto'])
    if p['fondo'] is not None:
        _nombre_seguro('fondo', p['fondo'])
    if (not isinstance(p['logo'], str) or not p['logo'] or p['logo'].startswith('~')
            or any(c in p['logo'] for c in '\n\r\x00')):
        raise componer.ErrorComponer(f'logo {p["logo"]!r}: tiene que ser una ruta dentro del repo, sin «~» ni '
                                     'saltos de línea')
    logo = (R / p['logo']).resolve()
    if not logo.is_relative_to(R):
        raise componer.ErrorComponer(f'logo {p["logo"]!r}: tiene que ser una ruta dentro del repo')
    return logo


def pieza(proy, cfg, p, dest):
    logo = validar(p)
    salida = dest / 'intentos' / f'{p["id"]}.png'
    salida.parent.mkdir(parents=True, exist_ok=True)
    if p['fondo'] is None:
        componer.rasterizar(logo, salida, p['ancho'], p['alto'])
        return {'pieza': p['id'], 'logo': p['logo']}
    fondo = fondo_de(proy, p['fondo'])
    kw = dict(subtitulo=p.get('subtitulo'), zona=p['zona'], color_texto=p['color_texto'], velo=p['velo'],
              fuente=cfg.get('fuente', 'Sora'), fuente_texto=cfg.get('fuente_texto', 'Inter'),
              peso_titulo=cfg.get('peso_titulo', 700))
    svg = componer.componer(fondo, salida, p['ancho'], p['alto'], logo, p['titulo'], **kw)
    (dest / 'svg').mkdir(exist_ok=True)
    shutil.move(svg, dest / 'svg' / svg.name)
    with tempfile.TemporaryDirectory(prefix='piezas-') as tmp:
        limpio, png = Path(tmp) / 'limpio.svg', Path(tmp) / 'limpio.png'
        limpio.write_text(componer.construir_svg(fondo, p['ancho'], p['alto'], logo, p['titulo'], texto=False, **kw),
                           encoding='utf-8')
        componer.rasterizar(limpio, png, p['ancho'], p['alto'])
        zona = componer.caja_zona(p['ancho'], p['alto'], p['zona'])
        m = medir.medir(str(png), zona=zona, color_texto=medir.hex_rgb(p['color_texto']))
    # YAVG, SATAVG y paleta, de la pieza terminada; el contraste se queda el del fondo con velo y sin texto.
    m.update(medir.medir(str(salida), paleta=paleta_de(proy)))
    m.update(pieza=p['id'], fondo=rel(fondo), imagen=rel(salida))
    return m


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[2])
        return 2
    ronda = argv[1]
    proys = argv[2:] or sorted(d.name for d in (R / 'examples').iterdir() if (d / 'piezas.json').is_file())
    cfgs = {}
    for proy in proys:
        f = R / 'examples' / proy / 'piezas.json'
        try:
            cfgs[proy] = json.loads(f.read_text(encoding='utf-8'))
            if not isinstance(cfgs[proy]['piezas'], list):
                raise TypeError('no es una lista')
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f'{rel(f)}: no se puede leer la lista «piezas»: {e}')
            return 2
    if not any(p.get('ronda') == ronda for cfg in cfgs.values() for p in cfg['piezas']):
        print(f'ninguna pieza de la ronda {ronda!r} en {", ".join(proys)}')
        return 2
    fallos = 0
    for proy, cfg in cfgs.items():
        dest = PILOTO / ronda / proy
        for p in (p for p in cfg['piezas'] if p.get('ronda') == ronda):
            try:
                m = pieza(proy, cfg, p, dest)
            except (componer.ErrorComponer, medir.ErrorMedir) as e:
                print(f'{proy} {p.get("id")}: error: {e}')
                fallos += 1
                continue
            (dest / 'medidas').mkdir(parents=True, exist_ok=True)
            (dest / 'medidas' / f'{p["id"]}.json').write_text(json.dumps(m, ensure_ascii=False, indent=1),
                                                         encoding='utf-8')
            c = m.get('contraste', {})
            print(f'{proy} {p["id"]}: ' + (f'contraste {c["media"]}:1 (peor {c["peor"]}), paleta '
                                            f'{m.get("paleta", {}).get("porcentaje")} %' if c else 'avatar'))
    import pagina
    pagina.main(['pagina.py', str(PILOTO)])
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
