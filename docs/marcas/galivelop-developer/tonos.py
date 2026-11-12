#!/usr/bin/env python3
"""Tonos del acento de un producto de la familia Galivelop.

Aplica el método de docs/marcas/portal/hoja.md, «Decisiones de la persona
(2026-11-12)», punto 1: del acento vivo (hex) salen el hondo (tema claro) y la
variante de tema oscuro, con el tono y el croma OKLCH fijos y la luminosidad
movida en pasos de 0,005 hasta el primer hex con contraste WCAG 2.x >= 4,5:1.

Uso:  python3 docs/marcas/galivelop-developer/tonos.py '#0E9A93' ['#hex' ...]

Solo biblioteca estándar. Lo que el método no fija y este script decide:
el paso 0 es el propio vivo (regla 5); en cada paso el croma vuelve a empezar
en el del vivo antes de bajarlo si el color cae fuera de sRGB (regla 4); un
color está dentro de sRGB si sus tres canales lineales están en [0, 1] con una
tolerancia de 1e-6 (el redondeo de ida y vuelta del propio vivo).
"""
import math
import sys

PAPER_LIGHT = "#fbfcfd"  # --papel, tema claro (Portal global.css l.48)
PAPER_DARK = "#0d171e"   # --papel, tema oscuro (l.83)
INK_LIGHT = "#13212b"    # --tinta, tema claro (l.51)
INK_DARK = "#e6eef3"     # --tinta, tema oscuro (l.86)
WHITE = "#ffffff"
STEP = 0.005
THRESHOLD = 4.5
EPS = 1e-6


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{min(255, max(0, round(c * 255))):02x}" for c in rgb)


def to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_gamma(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(value):
    r, g, b = (to_linear(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def hex_to_oklch(value):
    r, g, b = (to_linear(c) for c in hex_to_rgb(value))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b2 = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return lightness, math.hypot(a, b2), math.atan2(b2, a)


def oklch_to_linear(lightness, chroma, hue):
    a, b = chroma * math.cos(hue), chroma * math.sin(hue)
    l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )


def oklch_to_hex(lightness, chroma, hue):
    """Devuelve (hex, croma usado): baja el croma hasta entrar en sRGB."""
    c = chroma
    while True:
        linear = oklch_to_linear(lightness, c, hue)
        if all(-EPS <= v <= 1 + EPS for v in linear) or c <= 0:
            clipped = (min(1.0, max(0.0, v)) for v in linear)
            return rgb_to_hex(tuple(to_gamma(v) for v in clipped)), c
        c = max(0.0, c - STEP)


def search(vivid, paper, direction):
    """Primer hex con contraste >= 4,5:1 sobre el papel; direction -1 baja L, +1 la sube."""
    lightness, chroma, hue = hex_to_oklch(vivid)
    if contrast(vivid, paper) >= THRESHOLD:
        return vivid.lower(), lightness, chroma, 0
    steps = 0
    while 0.0 <= lightness <= 1.0:
        steps += 1
        lightness += direction * STEP
        candidate, used = oklch_to_hex(lightness, chroma, hue)
        if contrast(candidate, paper) >= THRESHOLD:
            return candidate, lightness, used, steps
    raise SystemExit(f"sin solución para {vivid} sobre {paper}")


def mix(top, base, alpha):
    t, b = hex_to_rgb(top), hex_to_rgb(base)
    return rgb_to_hex(tuple(alpha * x + (1 - alpha) * y for x, y in zip(t, b)))


def report(vivid):
    lightness, chroma, hue = hex_to_oklch(vivid)
    deep, deep_l, deep_c, deep_n = search(vivid, PAPER_LIGHT, -1)
    dark, dark_l, dark_c, dark_n = search(vivid, PAPER_DARK, +1)
    tint_light = mix(vivid, PAPER_LIGHT, 0.12)
    tint_dark = mix(vivid, PAPER_DARK, 0.18)
    rows = [
        ("vivo", vivid.lower(), f"OKLCH L={lightness:.4f} C={chroma:.4f} h={math.degrees(hue) % 360:.2f}"),
        ("vivo sobre papel claro", f"{contrast(vivid, PAPER_LIGHT):.2f}", PAPER_LIGHT),
        ("blanco sobre vivo", f"{contrast(WHITE, vivid):.2f}", WHITE),
        ("tinta sobre vivo", f"{contrast(INK_LIGHT, vivid):.2f}", INK_LIGHT),
        ("vivo sobre papel oscuro", f"{contrast(vivid, PAPER_DARK):.2f}", PAPER_DARK),
        ("hondo", deep, f"L={deep_l:.4f} C={deep_c:.4f} pasos={deep_n}"),
        ("hondo sobre papel claro", f"{contrast(deep, PAPER_LIGHT):.2f}", PAPER_LIGHT),
        ("blanco sobre hondo", f"{contrast(WHITE, deep):.2f}", WHITE),
        ("hondo sobre papel oscuro", f"{contrast(deep, PAPER_DARK):.2f}", PAPER_DARK),
        ("oscuro", dark, f"L={dark_l:.4f} C={dark_c:.4f} pasos={dark_n}"),
        ("oscuro sobre papel oscuro", f"{contrast(dark, PAPER_DARK):.2f}", PAPER_DARK),
        ("tinte 12 % (claro)", tint_light, f"tinta encima {contrast(INK_LIGHT, tint_light):.2f}"),
        ("tinte 18 % (oscuro)", tint_dark, f"tinta encima {contrast(INK_DARK, tint_dark):.2f}"),
    ]
    for name, value, note in rows:
        print(f"{name:28} {value:9} {note}")


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    for index, value in enumerate(argv[1:]):
        if index:
            print()
        report(value)


if __name__ == "__main__":
    main(sys.argv)
