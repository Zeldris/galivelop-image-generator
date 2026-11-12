#!/usr/bin/env python3
"""Tonos de acento de un producto Galivelop, calculados (solo stdlib).

Método: docs/marcas/portal/hoja.md, «Decisiones de la persona (2026-11-12)», punto 1.
Uso:    python3 docs/marcas/galivelop-voice-generator/tonos.py '#D9467A' ['#C9467A' ...]

Para cada hex vivo: lo pasa a OKLCH (OKLab de Björn Ottosson, D65), y con tono y croma
fijos baja L de 0,005 en 0,005 hasta el primer hex de 8 bits con contraste WCAG 2.x
>= 4,5:1 sobre el papel #fbfcfd (hondo), y la sube hasta el primero con >= 4,5:1 sobre
el papel oscuro #0d171e (variante oscura). Si un paso cae fuera de sRGB, baja la croma
de 0,005 en 0,005 desde la del vivo (sin tocar el tono) hasta que entra. Si el vivo ya
cumple un umbral, ese tono es el vivo. El contraste se calcula sobre el hex redondeado.
"""
import math
import sys

PAPEL, PAPEL_OSCURO, BLANCO, TINTA, TINTA_OSCURA = "#fbfcfd", "#0d171e", "#ffffff", "#13212b", "#e6eef3"
PASO, UMBRAL = 0.005, 4.5


def rgb(hexa):
    h = hexa.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def gamma(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminancia(hexa):
    r, g, b = (lineal(c) for c in rgb(hexa))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def a_oklch(hexa):
    r, g, b = (lineal(c) for c in rgb(hexa))
    l = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.atan2(B, A)


def a_srgb(L, C, h):
    A, B = C * math.cos(h), C * math.sin(h)
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return [gamma(max(v, 0.0)) if v > 0 else v for v in (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)]


def a_hex(L, C, h):
    """Hex de 8 bits y la croma usada (se baja solo si hace falta para entrar en sRGB)."""
    while True:
        canales = a_srgb(L, C, h)
        if all(-1e-6 <= c <= 1 + 1e-6 for c in canales) or C <= 0:
            return "#" + "".join(f"{round(min(max(c, 0), 1) * 255):02x}" for c in canales), C
        C = max(C - PASO, 0.0)


def buscar(vivo, fondo, sentido):
    L, C, h = a_oklch(vivo)
    if contraste(vivo, fondo) >= UMBRAL:
        return vivo.lower(), L, C, 0
    pasos = 0
    while 0.0 < L < 1.0:
        L += sentido * PASO
        pasos += 1
        hexa, c = a_hex(L, C, h)
        if contraste(hexa, fondo) >= UMBRAL:
            return hexa, L, c, pasos
    raise SystemExit(f"sin solución para {vivo} sobre {fondo}")


def mezcla(encima, debajo, alfa):
    return "#" + "".join(f"{round((a * alfa + b * (1 - alfa)) * 255):02x}" for a, b in zip(rgb(encima), rgb(debajo)))


def r(a, b):
    return f"{contraste(a, b):.2f}"


def informe(vivo):
    L, C, h = a_oklch(vivo)
    hondo, lh, ch, ph = buscar(vivo, PAPEL, -1)
    oscuro, lo, co, po = buscar(vivo, PAPEL_OSCURO, +1)
    t12, t18 = mezcla(vivo, PAPEL, 0.12), mezcla(vivo, PAPEL_OSCURO, 0.18)
    print(f"vivo   {vivo.lower()}  OKLCH L={L:.4f} C={C:.4f} h={math.degrees(h) % 360:.2f}")
    print(f"       sobre {PAPEL} {r(vivo, PAPEL)} | blanco encima {r(BLANCO, vivo)} | tinta {TINTA} encima {r(TINTA, vivo)}"
          f" | sobre {PAPEL_OSCURO} {r(vivo, PAPEL_OSCURO)}")
    print(f"hondo  {hondo}  L={lh:.4f} C={ch:.4f} ({ph} pasos)")
    print(f"       sobre {PAPEL} {r(hondo, PAPEL)} | blanco encima {r(BLANCO, hondo)} | sobre {PAPEL_OSCURO} {r(hondo, PAPEL_OSCURO)}")
    print(f"oscuro {oscuro}  L={lo:.4f} C={co:.4f} ({po} pasos)")
    print(f"       sobre {PAPEL_OSCURO} {r(oscuro, PAPEL_OSCURO)}")
    print(f"tinte  12 % sobre {PAPEL} = {t12}, tinta encima {r(TINTA, t12)}"
          f" | 18 % sobre {PAPEL_OSCURO} = {t18}, tinta {TINTA_OSCURA} encima {r(TINTA_OSCURA, t18)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for i, v in enumerate(sys.argv[1:]):
        if i:
            print()
        informe(v)
