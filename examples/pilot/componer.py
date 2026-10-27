#!/usr/bin/env python3
"""Prueba de concepto de `gimg compose` (D28): fondo + velo + logo + texto, en un SVG que rsvg-convert rasteriza.

    componer.py fondo.png salida.png --ancho 1200 --alto 630 --logo lockup.svg --titulo "..." [--subtitulo "..."]
        [--zona izquierda|derecha|abajo|arriba] [--color-texto #hex] [--velo #hex:opacidad]
        [--fuente Sora] [--fuente-texto Inter]

Decisiones (las porta F2.8):
- El fondo se recorta en modo cover con `preserveAspectRatio="xMidYMid slice"` en un <image> del tamaño de destino; la
  geometría del recorte, para quien la necesite, está en `recorte_cover`. El fondo va en base64 (data URI): rsvg no
  resuelve bien rutas relativas ni fuera de su directorio base, y así el SVG de depuración es autónomo.
- El lockup va como <image> con data URI base64 de SVG: rsvg lo renderiza con sus fuentes y sus ids no chocan con
  los del SVG exterior (en línea habría que renombrar ids y degradados).
- Fuentes: rsvg corre con un FONTCONFIG_FILE temporal que suma `piloto/fuentes/` (ver fuentes.sh) a las del sistema.
- Se guarda el SVG junto a la salida (`<salida>.svg`) para depurar (piezas.py lo mueve luego a `svg/`).
"""
import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent.parent
FUENTES = RAIZ / "piloto" / "fuentes"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class ErrorComponer(Exception):
    pass


def esc(texto):
    """Escapa un texto para meterlo como contenido o atributo XML."""
    return escape(texto, {'"': "&quot;", "'": "&apos;"})


def recorte_cover(sw, sh, w, h):
    """Rectángulo (x, y, ancho, alto) de la fuente que cubre w×h centrado, sin deformar."""
    if min(sw, sh, w, h) <= 0:
        raise ErrorComponer("los tamaños tienen que ser positivos")
    if sw * h > sh * w:  # la fuente es más ancha: se recortan los lados
        cw = sh * w / h
        return ((sw - cw) / 2, 0.0, cw, float(sh))
    ch = sw * h / w
    return (0.0, (sh - ch) / 2, float(sw), ch)


def _hex(valor, nombre):
    if not HEX.match(valor):
        raise ErrorComponer(f"{nombre}: se esperaba un color #rrggbb, no {valor!r}")
    return valor


def parsear_velo(texto):
    color, _, op = texto.partition(":")
    _hex(color, "velo")
    try:
        opacidad = float(op) if op else 0.85
    except ValueError:
        raise ErrorComponer(f"velo: la opacidad no es un número: {op!r}") from None
    if not 0 <= opacidad <= 1:
        raise ErrorComponer(f"velo: la opacidad tiene que estar entre 0 y 1, no {opacidad}")
    return color, opacidad


def _data_uri(ruta, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(ruta).read_bytes()).decode()


def _viewbox(ruta):
    m = re.search(r'viewBox="\s*[-\d.]+[ ,]+[-\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)\s*"',
                  Path(ruta).read_text(encoding="utf-8"))
    if not m:
        raise ErrorComponer(f"{ruta}: el logo no tiene viewBox")
    return float(m.group(1)), float(m.group(2))


FACTOR_TITULO = 0.56  # ancho estimado de un carácter, en tamaños de fuente
FACTOR_SUB = 0.5


def ajustar(texto, tam, ancho_max, factor=FACTOR_TITULO):
    """Parte `texto` en líneas de ancho estimado (factor·tam por carácter) <= ancho_max."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if actual and len(prueba) * tam * factor > ancho_max:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


ZONAS = ("izquierda", "derecha", "abajo", "arriba")


def caja_zona(w, h, zona):
    """(x, y, ancho, alto) de la caja de logo y texto de la zona; medir.py mide el contraste en ella."""
    if zona not in ZONAS:
        raise ErrorComponer(f"zona desconocida: {zona!r} ({', '.join(ZONAS)})")
    m = round(0.06 * min(w, h))
    if zona == "abajo":
        return m, round(h * 0.52), w - 2 * m, h - m - round(h * 0.52)
    if zona == "arriba":
        return m, m, w - 2 * m, round(h * 0.48) - m
    cw = round(w * 0.55) - m
    return (m if zona == "izquierda" else w - m - cw), m, cw, h - 2 * m


def construir_svg(fondo, w, h, logo, titulo, subtitulo=None, zona=None, color_texto="#eaf4fa",
                  velo="#06121c:0.85", fuente="Sora", fuente_texto="Inter", texto=True, peso_titulo=700):
    """El SVG de la pieza; con texto=False, solo fondo y velo (para medir el contraste de la zona sin el propio texto)."""
    _hex(color_texto, "color-texto")
    vcolor, vop = parsear_velo(velo)
    zona = zona or ("izquierda" if w > h * 1.2 else "abajo")
    m = round(0.06 * min(w, h))  # margen
    cx, cy0, cw, alto_caja = caja_zona(w, h, zona)
    cy1 = cy0 + alto_caja
    # Logo arriba de la caja
    lw, lh = _viewbox(logo)
    # Misma altura en todas las marcas (9 % del alto), salvo que el lockup no quepa a lo ancho de la columna: con el
    # tope anterior al 40 % del ancho, un lockup de 1100×128 salía a 24 px y su nombre no se leía.
    alto_logo = round(min(0.09 * h, cw * lh / lw))
    ancho_logo = alto_logo * lw / lh
    ly = cy0
    # Texto: baja el cuerpo hasta que cabe
    tam = round((0.075 if zona in ("abajo", "arriba") else 0.09) * h)
    sub_tam = max(round(tam * 0.42), 14)
    top = ly + alto_logo + m * 0.9
    disp = cy1 - top
    while True:
        lt = ajustar(titulo, tam, cw)
        ls = ajustar(subtitulo, sub_tam, cw, FACTOR_SUB) if subtitulo else []
        total = len(lt) * tam * 1.12 + (sub_tam * 0.8 + len(ls) * sub_tam * 1.3 if ls else 0)
        ancho_max = max([len(l) * tam * FACTOR_TITULO for l in lt] + [len(l) * sub_tam * FACTOR_SUB for l in ls])
        if total <= disp and len(lt) <= 3 and ancho_max <= cw:
            break
        if tam <= 16:
            motivo = "una línea más ancha que la columna" if ancho_max > cw else "no entra en la altura"
            raise ErrorComponer(f"el texto no cabe en la zona {zona} de {w}×{h} ni a 16 px ({motivo}): acorta el "
                                "título o el subtítulo, o usa otra zona")
        tam = round(tam * 0.93)
        sub_tam = max(round(tam * 0.42), 14)
    y = {"abajo": cy1 - total, "arriba": top}.get(zona, top + (disp - total) / 2)
    partes = []
    for i, linea in enumerate(lt):
        partes.append(f'<text x="{cx}" y="{y + tam * (0.85 + 1.12 * i):.1f}" font-family="{esc(fuente)}, sans-serif" '
                      f'font-weight="{int(peso_titulo)}" font-size="{tam}" fill="{color_texto}">{esc(linea)}</text>')
    y2 = y + len(lt) * tam * 1.12 + sub_tam * 0.8
    for i, linea in enumerate(ls):
        partes.append(f'<text x="{cx}" y="{y2 + sub_tam * (0.9 + 1.3 * i):.1f}" font-family="{esc(fuente_texto)}, sans-serif" '
                      f'font-weight="400" font-size="{sub_tam}" fill="{color_texto}" fill-opacity="0.82">{esc(linea)}</text>')
    # Velo en degradado: opaco en el borde de la zona, transparente al otro lado
    if zona == "izquierda":
        g = (0, 0, 1, 0); rect = (0, 0, w, h)
    elif zona == "derecha":
        g = (1, 0, 0, 0); rect = (0, 0, w, h)
    elif zona == "arriba":
        g = (0, 0, 0, 1); rect = (0, 0, w, h)
    else:
        g = (0, 1, 0, 0); rect = (0, 0, w, h)
    cola = 0.95 if zona in ("izquierda", "derecha") else 0.9
    velo_svg = (
        f'<linearGradient id="velo" x1="{g[0]}" y1="{g[1]}" x2="{g[2]}" y2="{g[3]}">'
        f'<stop offset="0" stop-color="{vcolor}" stop-opacity="{vop}"/>'
        f'<stop offset="0.55" stop-color="{vcolor}" stop-opacity="{vop * 0.88:.3f}"/>'
        f'<stop offset="{cola}" stop-color="{vcolor}" stop-opacity="0"/></linearGradient>')
    if zona in ("abajo", "arriba"):  # desde su borde: casi opaco hasta la mitad y transparente al 90 % del alto
        velo_svg = velo_svg.replace('offset="0.55"', 'offset="0.5"')
    marca = (f'<image x="{cx}" y="{ly}" width="{ancho_logo:.1f}" height="{alto_logo:.1f}" '
             f'href="{_data_uri(logo, "image/svg+xml")}"/>\n' + "\n".join(partes) + "\n") if texto else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<defs>{velo_svg}</defs>\n'
        f'<image x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" '
        f'href="{_data_uri(fondo, "image/png")}"/>\n'
        f'<rect x="{rect[0]}" y="{rect[1]}" width="{rect[2]}" height="{rect[3]}" fill="url(#velo)"/>\n'
        + marca + "</svg>\n")


def fonts_conf(directorio_fuentes, destino):
    """Escribe un fonts.conf que suma `directorio_fuentes` a la configuración del sistema."""
    destino = Path(destino)
    destino.write_text(
        '<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">\n<fontconfig>\n'
        '  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>\n'
        f'  <dir>{esc(str(directorio_fuentes))}</dir>\n'
        f'  <cachedir>{esc(str(destino.parent / "cache"))}</cachedir>\n</fontconfig>\n', encoding="utf-8")
    return destino


def entorno_fuentes(tmpdir, directorio_fuentes=FUENTES):
    env = dict(os.environ)
    env["FONTCONFIG_FILE"] = str(fonts_conf(directorio_fuentes, Path(tmpdir) / "fonts.conf"))
    return env


def rasterizar(svg, salida, w, h, directorio_fuentes=FUENTES):
    if not shutil.which("rsvg-convert"):
        raise ErrorComponer("falta rsvg-convert")
    with tempfile.TemporaryDirectory(prefix="componer-") as tmp:
        r = subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", str(salida), str(svg)],
                           env=entorno_fuentes(tmp, directorio_fuentes), capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorComponer(f"rsvg-convert falló: {r.stderr.strip()}")


def componer(fondo, salida, w, h, logo, titulo, **kw):
    for ruta, nombre in ((fondo, "fondo"), (logo, "logo")):
        if not Path(ruta).is_file():
            raise ErrorComponer(f"no existe el {nombre}: {ruta}")
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    svg = salida.with_suffix(".svg")
    svg.write_text(construir_svg(fondo, w, h, logo, titulo, **kw), encoding="utf-8")
    rasterizar(svg, salida, w, h)
    return svg


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("fondo")
    p.add_argument("salida")
    p.add_argument("--ancho", type=int, required=True)
    p.add_argument("--alto", type=int, required=True)
    p.add_argument("--logo", required=True)
    p.add_argument("--titulo", required=True)
    p.add_argument("--subtitulo")
    p.add_argument("--zona", choices=ZONAS)
    p.add_argument("--color-texto", default="#eaf4fa")
    p.add_argument("--velo", default="#06121c:0.85")
    p.add_argument("--fuente", default="Sora")
    p.add_argument("--fuente-texto", default="Inter")
    a = p.parse_args(argv)
    try:
        svg = componer(a.fondo, a.salida, a.ancho, a.alto, a.logo, a.titulo, subtitulo=a.subtitulo, zona=a.zona,
                       color_texto=a.color_texto, velo=a.velo, fuente=a.fuente, fuente_texto=a.fuente_texto)
    except ErrorComponer as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"{a.salida} ({a.ancho}x{a.alto}); SVG de depuración: {svg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
