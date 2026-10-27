#!/usr/bin/env python3
"""Prueba de concepto de `gimg measure` (D31): YAVG/SATAVG, % de píxeles cerca de la paleta y contraste WCAG.

    medir.py imagen.png [--paleta #hex,#hex,...] [--zona x,y,w,h] [--color-texto #hex] [--json]

Criterios (los porta F2.9):
- YAVG y SATAVG: `signalstats` de ffmpeg sobre la imagen entera (promedio de luma y de saturación, 0-255).
- % de paleta: se reduce la imagen a 256 px de ancho, se leen los píxeles RGB y se cuenta el que está a ΔE76 < UMBRAL_DE
  (15) de algún color de la paleta, en CIE Lab (D65). ΔE ≈ 2 apenas se nota y ≈ 10-15 es «el mismo color con otra luz»;
  15 admite el degradado y el grano de un fondo generado sin dar por cerca un color de otro tono. A calibrar con las
  imágenes de marca (r1), como pide D31.
- Contraste: con --zona y --color-texto, relación WCAG 2.x entre el texto y la luminancia relativa de la zona: media,
  percentil 10 (oscuro) y 90 (claro). `peor` es la más baja de las tres: lo que manda para legibilidad.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

UMBRAL_DE = 15.0
ANCHO = 256
HEX = re.compile(r"^#?([0-9a-fA-F]{6})$")


class ErrorMedir(Exception):
    pass


def hex_rgb(texto):
    m = HEX.match(texto.strip())
    if not m:
        raise ErrorMedir(f"se esperaba un color #rrggbb, no {texto!r}")
    v = m.group(1)
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(rgb):
    """Luminancia relativa WCAG (0-1)."""
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(l1, l2):
    """Relación de contraste WCAG entre dos luminancias relativas."""
    claro, oscuro = max(l1, l2), min(l1, l2)
    return (claro + 0.05) / (oscuro + 0.05)


def rgb_lab(rgb):
    r, g, b = (_lin(c) for c in rgb)
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def _ffmpeg(args):
    if not shutil.which("ffmpeg"):
        raise ErrorMedir("falta ffmpeg")
    r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", *args], capture_output=True)
    if r.returncode != 0:
        raise ErrorMedir(f"ffmpeg falló: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def signalstats(imagen):
    """(YAVG, SATAVG) de la imagen."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", imagen, "-frames:v", "1",
                        "-vf", "signalstats,metadata=print:file=-", "-f", "null", "-"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorMedir(f"ffmpeg falló: {r.stderr.strip()}")
    vals = dict(re.findall(r"lavfi\.signalstats\.(YAVG|SATAVG)=([\d.]+)", r.stdout))
    if "YAVG" not in vals or "SATAVG" not in vals:
        raise ErrorMedir("signalstats no devolvió YAVG y SATAVG")
    return float(vals["YAVG"]), float(vals["SATAVG"])


def tamano(imagen):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", imagen], capture_output=True, text=True)
    try:
        w, h = r.stdout.strip().split(",")
        return int(w), int(h)
    except ValueError:
        raise ErrorMedir(f"no se pudo leer el tamaño de {imagen}: {r.stderr.strip()}") from None


def pixeles(imagen, zona=None):
    """Lista de (r, g, b) de la imagen (o la zona x,y,w,h en píxeles originales) reducida a ~ANCHO px de ancho."""
    filtros = []
    if zona:
        x, y, w, h = zona
        W, H = tamano(imagen)
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > W or y + h > H:
            raise ErrorMedir(f"la zona {x},{y},{w},{h} se sale de la imagen ({W}x{H})")
        filtros.append(f"crop={w}:{h}:{x}:{y}")
    filtros.append(f"scale='min({ANCHO},iw)':-2:flags=area")
    sal = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", imagen, "-vf", ",".join(filtros),
                          "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    if sal.returncode != 0:
        raise ErrorMedir(f"ffmpeg falló: {sal.stderr.decode(errors='replace').strip()}")
    d = sal.stdout
    return [(d[i], d[i + 1], d[i + 2]) for i in range(0, len(d) - 2, 3)]


def porcentaje_paleta(pix, paleta, umbral=UMBRAL_DE):
    """% de píxeles a ΔE76 < umbral de algún color de la paleta."""
    if not pix:
        return 0.0
    labs = [rgb_lab(c) for c in paleta]
    cache, cerca = {}, 0
    for p in pix:
        if p not in cache:
            l = rgb_lab(p)
            cache[p] = any(((l[0] - q[0]) ** 2 + (l[1] - q[1]) ** 2 + (l[2] - q[2]) ** 2) ** 0.5 < umbral
                           for q in labs)
        cerca += cache[p]
    return 100.0 * cerca / len(pix)


def percentil(valores, p):
    v = sorted(valores)
    return v[min(len(v) - 1, int(p / 100 * len(v)))]


def contraste_zona(pix, color_texto):
    lt = luminancia(color_texto)
    lums = [luminancia(p) for p in pix]
    media = sum(lums) / len(lums)
    r = {"media": contraste(lt, media), "p10_oscuro": contraste(lt, percentil(lums, 10)),
         "p90_claro": contraste(lt, percentil(lums, 90))}
    r["peor"] = min(r.values())
    return r


def medir(imagen, paleta=None, zona=None, color_texto=None):
    yavg, satavg = signalstats(imagen)
    res = {"imagen": imagen, "YAVG": round(yavg, 2), "SATAVG": round(satavg, 2)}
    if paleta:
        res["paleta"] = {"colores": ["#%02x%02x%02x" % c for c in paleta], "umbral_deltaE": UMBRAL_DE,
                         "porcentaje": round(porcentaje_paleta(pixeles(imagen), paleta), 2)}
    if zona or color_texto:
        if not (zona and color_texto):
            raise ErrorMedir("el contraste pide --zona y --color-texto a la vez")
        c = contraste_zona(pixeles(imagen, zona), color_texto)
        res["contraste"] = {"zona": list(zona), "texto": "#%02x%02x%02x" % color_texto,
                            **{k: round(v, 2) for k, v in c.items()}}
    return res


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("imagen")
    p.add_argument("--paleta")
    p.add_argument("--zona", help="x,y,w,h en píxeles")
    p.add_argument("--color-texto")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        paleta = [hex_rgb(c) for c in a.paleta.split(",")] if a.paleta else None
        zona = None
        if a.zona:
            try:
                zona = tuple(int(v) for v in a.zona.split(","))
                if len(zona) != 4:
                    raise ValueError(a.zona)
            except ValueError:
                raise ErrorMedir(f"--zona: se esperaba x,y,w,h en enteros, no {a.zona!r}") from None
        res = medir(a.imagen, paleta, zona, hex_rgb(a.color_texto) if a.color_texto else None)
    except ErrorMedir as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(f"{res['imagen']}\n  YAVG {res['YAVG']}  SATAVG {res['SATAVG']}")
        if "paleta" in res:
            print(f"  paleta: {res['paleta']['porcentaje']} % de píxeles a ΔE < {UMBRAL_DE} de {len(paleta)} colores")
        if "contraste" in res:
            c = res["contraste"]
            print(f"  contraste {c['texto']} en zona {c['zona']}: media {c['media']}, p10 oscuro {c['p10_oscuro']}, "
                  f"p90 claro {c['p90_claro']}; peor {c['peor']}:1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
