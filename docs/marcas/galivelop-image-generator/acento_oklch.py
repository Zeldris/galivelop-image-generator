#!/usr/bin/env python3
"""Tonos del acento de un producto Galivelop, con el método de `docs/marcas/portal/hoja.md`,
«Decisiones de la persona (2026-11-12)», punto 1. Solo stdlib (D6).

    python3 docs/marcas/galivelop-image-generator/acento_oklch.py '#7C5CD6'
    python3 docs/marcas/galivelop-image-generator/acento_oklch.py '#7C5CD6' --par '#5B34C9' '#fbfcfd'
    python3 docs/marcas/galivelop-image-generator/acento_oklch.py '#7C5CD6' --sobre '#111f29'

`--par A B` da el contraste de dos hex; `--sobre FONDO` aplica el mismo método a otro fondo (baja L si el fondo es
claro, la sube si es oscuro): sirve para ver qué tono haría falta sobre una superficie que no es el papel.

Método: el vivo pasa de sRGB a OKLCH (OKLab de Björn Ottosson, D65); con h y C fijos se mueve L en pasos de 0,005
(hacia abajo para el hondo, sobre el papel claro; hacia arriba para la variante oscura, sobre el papel oscuro) hasta el
primer hex de 8 bits con contraste WCAG 2.x >= 4,5:1, medido sobre el hex ya redondeado. Si un paso cae fuera de sRGB,
se baja C de 0,005 en 0,005 sin tocar h. Si el vivo ya cumple en un tema, ese tono es el vivo.
"""
import math
import re
import sys

PAPEL, PAPEL_OSCURO, BLANCO, TINTA, TINTA_OSCURA = "#fbfcfd", "#0d171e", "#ffffff", "#13212b", "#e6eef3"
PASO, UMBRAL, EPS = 0.005, 4.5, 1e-6


def _rgb(hexa):
    if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", hexa):
        print("hex no válido: %s (se espera #RRGGBB)" % hexa, file=sys.stderr)
        sys.exit(2)
    h = hexa.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gamma(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lum(hexa):
    r, g, b = (_lin(c) for c in _rgb(hexa))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def a_oklch(hexa):
    r, g, b = (_lin(c) for c in _rgb(hexa))
    l = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def _lineal(L, C, h):
    A, B = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def a_hex(L, C, h):
    """El hex de 8 bits de (L, C, h) y el C con el que entró en sRGB."""
    while C > 0 and not all(-EPS <= c <= 1 + EPS for c in _lineal(L, C, h)):
        C = max(0.0, C - PASO)
    canales = (min(1.0, max(0.0, c)) for c in _lineal(L, C, h))
    return "#" + "".join("%02x" % round(_gamma(c) * 255) for c in canales), C


def tono(vivo, fondo, sentido):
    """Primer hex con >= 4,5:1 sobre `fondo`, moviendo L en `sentido` (-1 baja, +1 sube) desde el vivo."""
    L, C, h = a_oklch(vivo)
    if ratio(vivo, fondo) >= UMBRAL:
        return vivo.lower(), L, C, 0
    for n in range(1, 400):
        Ln = L + sentido * PASO * n
        if not 0 <= Ln <= 1:
            break
        hexa, Cn = a_hex(Ln, C, h)
        if ratio(hexa, fondo) >= UMBRAL:
            return hexa, Ln, Cn, n
    raise SystemExit("no hay tono con %.1f:1 sobre %s" % (UMBRAL, fondo))


def mezcla(encima, debajo, alfa):
    """`encima` al `alfa` sobre `debajo`, mezclado en sRGB de 8 bits como hace el navegador."""
    a, b = _rgb(encima), _rgb(debajo)
    return "#" + "".join("%02x" % round((x * alfa + y * (1 - alfa)) * 255) for x, y in zip(a, b))


def main(argv):
    if len(argv) >= 4 and argv[1] == "--par" or len(argv) >= 5 and argv[2] == "--par":
        i = argv.index("--par")
        print("%s sobre %s: %.2f:1" % (argv[i + 1], argv[i + 2], ratio(argv[i + 1], argv[i + 2])))
        return
    vivo = argv[1] if len(argv) > 1 else "#7C5CD6"
    if "--sobre" in argv:
        fondo = argv[argv.index("--sobre") + 1]
        hexa, Ls, Cs, n = tono(vivo, fondo, -1 if lum(fondo) > 0.18 else +1)
        print("%s sobre %s: %s  L=%.4f C=%.4f pasos=%d  %.2f:1" % (vivo.lower(), fondo, hexa, Ls, Cs, n, ratio(hexa, fondo)))
        return
    L, C, h = a_oklch(vivo)
    hondo, Lh, Ch, nh = tono(vivo, PAPEL, -1)
    oscuro, Lo, Co, no = tono(vivo, PAPEL_OSCURO, +1)
    tinte_c, tinte_o = mezcla(vivo, PAPEL, 0.12), mezcla(vivo, PAPEL_OSCURO, 0.18)
    print("vivo    %s  OKLCH L=%.4f C=%.4f h=%.2f" % (vivo.lower(), L, C, h))
    print("hondo   %s  L=%.4f C=%.4f pasos=%d%s" % (hondo, Lh, Ch, nh, "  (es el vivo: ya cumple)" if nh == 0 else ""))
    print("oscuro  %s  L=%.4f C=%.4f pasos=%d%s" % (oscuro, Lo, Co, no, "  (es el vivo: ya cumple)" if no == 0 else ""))
    print("tinte   %s (vivo al 12 %% sobre %s)   %s (vivo al 18 %% sobre %s)" % (tinte_c, PAPEL, tinte_o, PAPEL_OSCURO))
    filas = (("vivo sobre papel claro", vivo, PAPEL), ("hondo sobre papel claro", hondo, PAPEL),
             ("blanco sobre hondo", BLANCO, hondo), ("blanco sobre vivo", BLANCO, vivo),
             ("tinta sobre vivo", TINTA, vivo), ("vivo sobre papel oscuro", vivo, PAPEL_OSCURO),
             ("hondo sobre papel oscuro", hondo, PAPEL_OSCURO), ("oscuro sobre papel oscuro", oscuro, PAPEL_OSCURO),
             ("oscuro sobre superficie oscura #111f29", oscuro, "#111f29"),
             ("hondo sobre superficie clara #ffffff", hondo, BLANCO),
             ("tinta sobre tinte claro", TINTA, tinte_c), ("tinta oscura sobre tinte oscuro", TINTA_OSCURA, tinte_o),
             ("hondo sobre tinte claro", hondo, tinte_c), ("oscuro sobre tinte oscuro", oscuro, tinte_o))
    for nombre, a, b in filas:
        print("%-40s %s / %s  %.2f:1" % (nombre, a, b, ratio(a, b)))


if __name__ == "__main__":
    main(sys.argv)
