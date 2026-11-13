#!/usr/bin/env python3
"""Tonos del acento de un producto Galivelop, calculados (no elegidos a ojo).

Método: docs/marcas/portal/hoja.md, «Decisiones de la persona (2026-11-12)», punto 1.
Uso: python3 docs/marcas/galivelop-workflow/acento.py [#rrggbb]   (por defecto, #3D6FD9)
Solo stdlib. OKLab de Björn Ottosson (D65); contraste WCAG 2.x sobre el hex redondeado.
"""
import math
import re
import sys

PAPEL, PAPEL_OSCURO, BLANCO, TINTA, TINTA_OSCURA = "#fbfcfd", "#0d171e", "#ffffff", "#13212b", "#e6eef3"
PASO = 0.005


def a_rgb(h):
    if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", h):
        print("hex no válido: %s (se espera #RRGGBB)" % h, file=sys.stderr)
        sys.exit(2)
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def gamma(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminancia(h):
    r, g, b = (lineal(c) for c in a_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def a_oklch(h):
    r, g, b = (lineal(c) for c in a_rgb(h))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.atan2(B, A)


def a_srgb_lineal(L, C, H):
    A, B = C * math.cos(H), C * math.sin(H)
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def a_hex(L, C, H):
    """Hex de 8 bits; si cae fuera de sRGB baja C de 0,005 en 0,005 sin tocar el tono."""
    while True:
        rgb = a_srgb_lineal(L, C, H)
        if all(-1e-6 <= c <= 1 + 1e-6 for c in rgb) or C <= 0:
            return "#" + "".join(f"{round(255 * gamma(min(1, max(0, c)))):02x}" for c in rgb), C
        C = max(0.0, C - PASO)


def buscar(vivo, fondo, signo):
    """Primer hex con >= 4,5:1 sobre el fondo, moviendo L en pasos de 0,005 (signo -1 baja, +1 sube)."""
    if contraste(vivo, fondo) >= 4.5:
        return vivo, "es el vivo: ya cumple"
    L, C, H = a_oklch(vivo)
    while 0 < L < 1:
        L += signo * PASO
        h, c = a_hex(L, C, H)
        if contraste(h, fondo) >= 4.5:
            return h, f"L={L:.3f} C={c:.3f}"
    raise SystemExit("no hay tono que cumpla")


def mezcla(sobre, fondo, alfa):
    return "#" + "".join(f"{round(255 * (alfa * s + (1 - alfa) * f)):02x}" for s, f in zip(a_rgb(sobre), a_rgb(fondo)))


def main():
    vivo = (sys.argv[1] if len(sys.argv) > 1 else "#3D6FD9").lower()
    L, C, H = a_oklch(vivo)
    hondo, como_h = buscar(vivo, PAPEL, -1)
    oscuro, como_o = buscar(vivo, PAPEL_OSCURO, +1)
    tinte_c, tinte_o = mezcla(vivo, PAPEL, 0.12), mezcla(vivo, PAPEL_OSCURO, 0.18)
    print(f"vivo   {vivo}  OKLCH L={L:.3f} C={C:.3f} h={math.degrees(H) % 360:.1f}")
    print(f"hondo  {hondo}  ({como_h})")
    print(f"oscuro {oscuro}  ({como_o})")
    filas = [
        ("vivo sobre papel #fbfcfd", vivo, PAPEL), ("blanco sobre vivo", BLANCO, vivo),
        ("tinta #13212b sobre vivo", TINTA, vivo), ("vivo sobre papel oscuro #0d171e", vivo, PAPEL_OSCURO),
        ("hondo sobre papel #fbfcfd", hondo, PAPEL), ("blanco sobre hondo", BLANCO, hondo),
        ("hondo sobre papel oscuro #0d171e", hondo, PAPEL_OSCURO),
        ("oscuro sobre papel oscuro #0d171e", oscuro, PAPEL_OSCURO),
        ("papel oscuro #0d171e sobre oscuro (texto encima)", PAPEL_OSCURO, oscuro),
        (f"tinta sobre tinte claro {tinte_c} (vivo al 12 %)", TINTA, tinte_c),
        (f"tinta clara #e6eef3 sobre tinte oscuro {tinte_o} (vivo al 18 %)", TINTA_OSCURA, tinte_o),
        ("vivo frente a hondo", vivo, hondo),
    ]
    for nombre, a, b in filas:
        print(f"{contraste(a, b):6.2f}:1  {nombre}")


if __name__ == "__main__":
    main()
