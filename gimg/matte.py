"""Remove a flat background from an image, stdlib only (D37: every graphic is born in gimg, locally; D6).

`remove_bg(width, height, rgba, t0=60, t1=110, border=6, grow=3, holes=False)` takes the background color from the border of the
image (the median of each channel over a band of `border` pixels), floods from the border over every pixel closer
than `t0` to it (so a color inside the shape that looks like the background is **not** background: it is not
connected to the border), grows the flood up to `grow` pixels over the soft edge (pixels closer than `t1`) and gives
that edge a partial alpha, ``(distance - t0) / (t1 - t0)``, with the background tint taken out of its color
(despill), so the edge has no halo of the background color. With ``holes=True`` every region **not connected to the
border** whose pixels are closer than `t0` to the background color is background too (a ring of background enclosed
by the shape, as in an emblem with an open ring), with the same grow and despill; by default such a region is kept. It returns a new RGBA ``bytearray``; the input is not
touched. A pixel whose own alpha is under 128 is background (and ends fully transparent), and the border color
is taken from the border pixels that are not. `border_color` gives the background color alone.

Distances are Euclidean in RGB, from 0 to about 441. `t1` has to be larger than `t0`, both not negative. The defaults
(`t0=60`, `t1=110`) are for the background of FLUX, which is green but not flat: it has a gradient, and next to the
subject it drifts 32-35 away from the border color, so a smaller `t0` cuts the flood short and leaves opaque green
patches; the shapes that matter (gold, brown) are far beyond 110.
"""
from __future__ import annotations

import math
from statistics import median

MAX_GROW = 32  # pixels the flood may grow over the soft edge; each pass walks the whole image


def _check(width: int, height: int, rgba) -> None:
    if width < 1 or height < 1 or len(rgba) != width * height * 4:
        raise ValueError("%d bytes do not fit a %dx%d RGBA image" % (len(rgba), width, height))


def _border_pixels(width: int, height: int, border: int):
    b = max(1, min(border, (min(width, height) + 1) // 2))
    for y in range(height):
        if y < b or y >= height - b:
            yield from ((x, y) for x in range(width))
        else:
            yield from ((x, y) for x in range(min(b, width)))
            yield from ((x, y) for x in range(max(b, width - b), width))


def border_color(width: int, height: int, rgba, border: int = 6) -> tuple:
    """``(r, g, b)``: the median color of the band of `border` pixels around the image."""
    _check(width, height, rgba)
    pixels = [(y * width + x) * 4 for x, y in _border_pixels(width, height, border)]
    pixels = [i for i in pixels if rgba[i + 3] >= 128] or pixels  # an already transparent border has no real color
    vals = ([rgba[i] for i in pixels], [rgba[i + 1] for i in pixels], [rgba[i + 2] for i in pixels])
    return tuple(int(median(v)) for v in vals)


def remove_bg(width: int, height: int, rgba, t0: float = 60, t1: float = 110, border: int = 6, grow: int = 3,
              holes: bool = False) -> bytearray:
    """RGBA copy of `rgba` with the flat background made transparent (see the module docstring)."""
    _check(width, height, rgba)
    if not 0 <= t0 < t1:
        raise ValueError("remove_bg: t0 and t1 must satisfy 0 <= t0 < t1 (got %s and %s)" % (t0, t1))
    if border < 1 or not 0 <= grow <= MAX_GROW:
        raise ValueError("remove_bg: border must be at least 1 and grow between 0 and %d" % MAX_GROW)
    bg = border_color(width, height, rgba, border)
    n = width * height
    dist = [math.sqrt((rgba[k * 4] - bg[0]) ** 2 + (rgba[k * 4 + 1] - bg[1]) ** 2 + (rgba[k * 4 + 2] - bg[2]) ** 2)
            if rgba[k * 4 + 3] >= 128 else 0.0 for k in range(n)]
    seen = bytearray(n)
    stack = []
    for x in range(width):
        stack += [x, (height - 1) * width + x]
    for y in range(height):
        stack += [y * width, y * width + width - 1]
    while stack:
        k = stack.pop()
        if seen[k] or dist[k] >= t0:
            continue
        seen[k] = 1
        x = k % width
        if x:
            stack.append(k - 1)
        if x < width - 1:
            stack.append(k + 1)
        if k >= width:
            stack.append(k - width)
        if k < n - width:
            stack.append(k + width)
    if holes:  # a flood seeded from every background-like pixel: the regions closed off from the border too
        for k in range(n):
            if dist[k] < t0:
                seen[k] = 1
    for _ in range(grow):  # the soft edge: grows only over what still looks like background
        add = []
        for k in range(n):
            if seen[k] or dist[k] >= t1:
                continue
            x = k % width
            if (x and seen[k - 1]) or (x < width - 1 and seen[k + 1]) or (k >= width and seen[k - width]) \
                    or (k < n - width and seen[k + width]):
                add.append(k)
        if not add:
            break
        for k in add:
            seen[k] = 1
    out = bytearray(rgba)
    for k in range(n):
        if rgba[k * 4 + 3] < 128:
            out[k * 4 + 3] = 0
            continue
        if not seen[k]:
            continue
        i, d = k * 4, dist[k]
        if d <= t0:
            out[i + 3] = 0
            continue
        a = (d - t0) / (t1 - t0)
        for c in range(3):
            out[i + c] = max(0, min(255, int((rgba[i + c] - (1 - a) * bg[c]) / a)))  # despill
        out[i + 3] = min(rgba[i + 3], int(a * 255))
    return out
