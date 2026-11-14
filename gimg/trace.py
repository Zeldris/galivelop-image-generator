"""Turn an RGBA image into a layered SVG, stdlib only (D37, D6: no PIL, numpy or potrace).

`to_svg(width, height, rgba, mode="color", ...)` is the one entry point and returns the SVG text. The steps:

1. Each pixel is classified to the nearest color of `palette` (hex strings) or, with none, of `ncolores` colors taken
   from the image (k-means). A pixel with alpha under `bg_tol` (0-255) is background and belongs to no color.
2. The image is reduced to at most `max_side` pixels on its long side (an integer factor, rounded up, majority vote per cell) and each color's mask is smoothed
   with `smooth_passes` passes of a 3x3 majority filter.
3. The mask borders are traced, simplified with Douglas-Peucker (`dp_tol`, in reduced pixels) and written as cubic
   Bezier curves (`curves`) that keep every corner sharper than `corner_deg` degrees, or as straight lines.
4. Loops smaller than `min_island` (reduced pixels, area) are dropped.
5. The layers are stacked: the whole opaque silhouette first, filled with the color that covers most, then one path
   per other color, biggest first. So a ``color`` SVG has one ``<path>`` per color found (a color that only had
   islands has none).

`mode="mono"` is one path of one color (`color`, ``currentColor`` by default) over the pixels of the palette entries
in `ink` (indexes). Default: every color but the darkest or, in an image with no transparent pixel, every color but
the paper (each color on at least 20% of the border, so a two-color background is all paper; with a gradient where
none reaches 20%, the darkest is left out as before). A dark frame that fills the border is taken for paper: pass `ink`
by hand (API) or remove the background first (``--matte``). One-pixel straight lines survive the smoothing (mono only).
`mode="silueta"` is one path over the whole opaque shape.
`title` loses control characters. A bad option (also a `color` that is not ``#rgb``, ``#rrggbb`` or a name) raises
``ValueError``.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from xml.sax.saxutils import escape, quoteattr

MODES = ("color", "mono", "silueta")
PAPER_SHARE = 0.2  # mono, opaque image: a color on at least this share of the border is paper, not ink
MAX_COLORS = 64  # `ncolores` cap: the palette pick costs O(k^2 * points)
_CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_COLOR = re.compile(r"^(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|[A-Za-z]{3,20})$")  # hex, a name or currentColor
_DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # right, down, left, up (clockwise on screen)


# ---------- palette ----------

def clean_title(title: str) -> str:
    """`title` as XML text: control characters dropped, markup escaped (the one way to write a ``<title>``)."""
    return escape(_CONTROL.sub("", str(title)))


def parse_hex(text: str) -> tuple:
    s = text.strip().lstrip("#") if isinstance(text, str) else ""
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    try:
        if len(s) != 6:
            raise ValueError
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError("palette: %r is not a color like #rrggbb" % (text,)) from None


def _hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in rgb)


def _d2(a, b) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def extract_palette(width: int, height: int, rgba, n: int, bg_tol: int = 128) -> list:
    """`n` hex colors of the opaque pixels (k-means over a sample, start from the most frequent color)."""
    count = defaultdict(int)
    step = max(1, (width * height) // 20000)
    for k in range(0, width * height, step):
        i = k * 4
        if rgba[i + 3] >= bg_tol:
            count[(rgba[i], rgba[i + 1], rgba[i + 2])] += 1
    if not count:
        return []
    pts = list(count.items())
    centers = [max(pts, key=lambda p: p[1])[0]]
    while len(centers) < min(n, len(pts)):
        centers.append(max(pts, key=lambda p: min(_d2(p[0], c) for c in centers))[0])
    centers = [tuple(float(v) for v in c) for c in centers]
    for _ in range(8):
        sums = [[0.0, 0.0, 0.0, 0] for _ in centers]
        for col, w in pts:
            j = min(range(len(centers)), key=lambda q: _d2(col, centers[q]))
            for c in range(3):
                sums[j][c] += col[c] * w
            sums[j][3] += w
        centers = [tuple(s[c] / s[3] for c in range(3)) if s[3] else centers[j] for j, s in enumerate(sums)]
    return [_hex(c) for c in centers]


# ---------- masks ----------

def _reduce(width: int, height: int, rgba, factor: int, label):
    """Grid ``(W, H, rows)`` of labels (majority per `factor`x`factor` cell); `label(i)` of a pixel offset, -1 for none."""
    W, H = max(1, width // factor), max(1, height // factor)
    rows = []
    for gy in range(H):
        row = []
        for gx in range(W):
            if factor == 1:
                row.append(label((gy * width + gx) * 4))
                continue
            cnt = {}
            for dy in range(min(factor, height - gy * factor)):  # a side shorter than the factor has a short block
                for dx in range(min(factor, width - gx * factor)):
                    lab = label(((gy * factor + dy) * width + gx * factor + dx) * 4)
                    cnt[lab] = cnt.get(lab, 0) + 1
            row.append(max(cnt, key=cnt.get))
        rows.append(row)
    return W, H, rows


def _majority(m, W: int, H: int, passes: int):
    """`passes` of a 3x3 majority filter over rows of 0/1; outside the image counts as the nearest pixel."""
    for _ in range(passes):
        out = []
        for y in range(H):
            a, b, c = m[max(y - 1, 0)], m[y], m[min(y + 1, H - 1)]
            row = []
            for x in range(W):
                xl, xr = max(x - 1, 0), min(x + 1, W - 1)
                row.append(1 if a[xl] + a[x] + a[xr] + b[xl] + b[x] + b[xr] + c[xl] + c[x] + c[xr] >= 5 else 0)
            out.append(row)
        m = out
    return m


def _thin(orig, smooth, W: int, H: int):
    """`smooth` plus the one-pixel-wide lines of `orig` that the majority filter erased (a stroke must survive it)."""
    def on(y, x):
        return 0 <= y < H and 0 <= x < W and orig[y][x]
    out = [row[:] for row in smooth]
    for y in range(H):
        for x in range(W):
            if orig[y][x] and not smooth[y][x]:
                horiz = on(y, x - 1) and on(y, x + 1) and not on(y - 1, x) and not on(y + 1, x)
                vert = on(y - 1, x) and on(y + 1, x) and not on(y, x - 1) and not on(y, x + 1)
                if horiz or vert:
                    out[y][x] = 1
    return out


# ---------- outlines ----------

def _loops(m, W: int, H: int) -> list:
    """Closed outlines of the mask along pixel borders (the inside is on the right of the walking direction)."""
    nxt = defaultdict(list)
    for y in range(H):
        row = m[y]
        up = m[y - 1] if y else None
        dn = m[y + 1] if y + 1 < H else None
        for x in range(W):
            if not row[x]:
                continue
            if not (up and up[x]):
                nxt[(x, y)].append((x + 1, y))
            if not (x + 1 < W and row[x + 1]):
                nxt[(x + 1, y)].append((x + 1, y + 1))
            if not (dn and dn[x]):
                nxt[(x + 1, y + 1)].append((x, y + 1))
            if not (x and row[x - 1]):
                nxt[(x, y + 1)].append((x, y))
    loops = []
    while nxt:
        start = cur = next(iter(nxt))
        d = None
        pts = [start]
        while True:
            outs = nxt[cur]
            if len(outs) > 1 and d is not None:  # ambiguous corner: turn right, which keeps diagonals apart
                outs.sort(key=lambda q: ((_DIRS.index((q[0] - cur[0], q[1] - cur[1])) - d) % 4) != 1)
            nxt_pt = outs.pop(0)
            if not outs:
                del nxt[cur]
            d = _DIRS.index((nxt_pt[0] - cur[0], nxt_pt[1] - cur[1]))
            cur = nxt_pt
            if cur == start:
                break
            pts.append(cur)
        loops.append(pts)
    return loops


def _drop_straight(p: list) -> list:
    n = len(p)
    out = []
    for i in range(n):
        a, b, c = p[i - 1], p[i], p[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
            out.append(b)
    return out


def _area(p: list) -> float:
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2


def _dp(pts: list, tol: float) -> list:
    """Douglas-Peucker over an open polyline (iterative: a long outline must not hit the recursion limit)."""
    if len(pts) < 3:
        return pts
    keep = {0, len(pts) - 1}
    todo = [(0, len(pts) - 1)]
    while todo:
        i, j = todo.pop()
        a, b = pts[i], pts[j]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        far, dmax = i, -1.0
        for k in range(i + 1, j):
            q = pts[k]
            dd = abs(dy * (q[0] - a[0]) - dx * (q[1] - a[1])) / length if length else math.hypot(q[0] - a[0], q[1] - a[1])
            if dd > dmax:
                far, dmax = k, dd
        if dmax > tol:
            keep.add(far)
            todo += [(i, far), (far, j)]
    return [pts[k] for k in sorted(keep)]


def _dp_closed(p: list, tol: float) -> list:
    if len(p) < 4:
        return p
    far = max(range(len(p)), key=lambda i: (p[i][0] - p[0][0]) ** 2 + (p[i][1] - p[0][1]) ** 2)
    return _dp(p[:far + 1], tol)[:-1] + _dp(p[far:] + [p[0]], tol)[:-1]


def _num(v: float) -> str:
    return ("%.1f" % v).rstrip("0").rstrip(".")


def _smooth(p: list, corner_deg: float) -> str:
    """Path data for a closed outline: Catmull-Rom cubic Beziers, with straight sharp corners."""
    n = len(p)
    tan = []
    for i in range(n):
        a, b, c = p[i - 1], p[i], p[(i + 1) % n]
        v1, v2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 == 0 or l2 == 0:
            tan.append((0, 0))
            continue
        cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)
        if math.degrees(math.acos(max(-1, min(1, cosang)))) > corner_deg:
            tan.append((0, 0))
            continue
        tx, ty = c[0] - a[0], c[1] - a[1]
        tl = math.hypot(tx, ty)
        tan.append((tx / tl, ty / tl))
    s = "M%s %s" % (_num(p[0][0]), _num(p[0][1]))
    for i in range(n):
        b, c = p[i], p[(i + 1) % n]
        ln = math.hypot(c[0] - b[0], c[1] - b[1]) / 3
        t1, t2 = tan[i], tan[(i + 1) % n]
        if t1 == (0, 0) and t2 == (0, 0):
            s += "L%s %s" % (_num(c[0]), _num(c[1]))
        else:
            s += "C%s %s %s %s %s %s" % (_num(b[0] + t1[0] * ln), _num(b[1] + t1[1] * ln),
                                         _num(c[0] - t2[0] * ln), _num(c[1] - t2[1] * ln), _num(c[0]), _num(c[1]))
    return s + "Z"


def _path_data(m, W: int, H: int, sx: float, sy: float, dp_tol: float, min_island: float, curves: bool, corner_deg: float) -> str:
    out = []
    for loop in _loops(m, W, H):
        if abs(_area(loop)) < min_island:
            continue
        q = _dp_closed(_drop_straight(loop), dp_tol)
        if len(q) < 3:
            continue
        q = [(x * sx, y * sy) for x, y in q]
        out.append(_smooth(q, corner_deg) if curves else "M" + "L".join("%s %s" % (_num(x), _num(y)) for x, y in q) + "Z")
    return "".join(out)


# ---------- entry point ----------

def to_svg(width: int, height: int, rgba, mode: str = "color", *, palette=None, ncolores: int = 4, bg_tol: int = 128,
           smooth_passes: int = 2, dp_tol: float = 1.2, min_island: float = 12, curves: bool = True,
           corner_deg: float = 55.0, max_side: int = 512, color: str = "currentColor", ink=None, title: str = "") -> str:
    """The SVG text of the RGBA image (see the module docstring for the steps and every option)."""
    if width < 1 or height < 1 or len(rgba) != width * height * 4:
        raise ValueError("%d bytes do not fit a %dx%d RGBA image" % (len(rgba), width, height))
    if mode not in MODES:
        raise ValueError("mode must be one of %s (got %r)" % (", ".join(MODES), mode))
    if not 1 <= ncolores <= MAX_COLORS:
        raise ValueError("ncolores must be between 1 and %d (got %s)" % (MAX_COLORS, ncolores))
    if smooth_passes < 0 or dp_tol < 0 or min_island < 0 or max_side < 1 or not 0 <= corner_deg <= 180:
        raise ValueError("smooth_passes, dp_tol and min_island >= 0, max_side >= 1 and corner_deg in 0-180")
    if not isinstance(color, str) or not _COLOR.match(color):
        raise ValueError("color: %r is not #rgb, #rrggbb or a color name such as currentColor" % (color,))
    pal_hex = list(palette) if palette else (extract_palette(width, height, rgba, ncolores, bg_tol) if mode != "silueta" else [])
    pal = [parse_hex(h) for h in pal_hex]
    pal_hex = [_hex(c) for c in pal]
    cache = {}

    def label(i):
        if rgba[i + 3] < bg_tol:
            return -1
        key = (rgba[i], rgba[i + 1], rgba[i + 2])
        if key not in cache:
            cache[key] = min(range(len(pal)), key=lambda j: _d2(key, pal[j])) if pal else 0
        return cache[key]

    W, H, grid = _reduce(width, height, rgba, -(-max(width, height) // max_side), label)
    sx, sy = width / W, height / H
    counts = defaultdict(int)
    for row in grid:
        for v in row:
            if v >= 0:
                counts[v] += 1

    def layer(fill, keep, mono=False):
        raw = [[1 if keep(v) else 0 for v in row] for row in grid]
        m = _majority(raw, W, H, smooth_passes)
        if mono and smooth_passes:
            m = _thin(raw, m, W, H)
        d = _path_data(m, W, H, sx, sy, dp_tol, min_island, curves, corner_deg)
        return '<path fill=%s fill-rule="evenodd" d="%s"/>' % (quoteattr(fill), d) if d else ""

    layers = []
    if mode == "silueta":
        layers.append(layer(color, lambda v: v >= 0))
    elif mode == "mono":
        if ink is None and counts and -1 not in {v for row in grid for v in row} and len(pal) > 1:
            # an opaque image (strokes on paper): the paper is every color that fills >= PAPER_SHARE of the border
            edge = defaultdict(int)
            for x in range(W):
                edge[grid[0][x]] += 1
                edge[grid[H - 1][x]] += 1
            for y in range(H):
                edge[grid[y][0]] += 1
                edge[grid[y][W - 1]] += 1
            paper = {j for j, n in edge.items() if n >= PAPER_SHARE * sum(edge.values())}
            if paper and len(paper) < len(pal):  # every color on the border: no paper to tell, darkest rule
                ink = [j for j in range(len(pal)) if j not in paper]
        if ink is None:
            dark = min(range(len(pal)), key=lambda j: sum(pal[j]) * 1.0) if len(pal) > 1 else -1
            ink = [j for j in range(len(pal)) if j != dark]
        elif any(not isinstance(j, int) or not 0 <= j < len(pal) for j in ink):
            raise ValueError("ink: every index must be a color of the palette (0-%d)" % (len(pal) - 1))
        layers.append(layer(color, lambda v, s=frozenset(ink): v in s, True))
    else:
        order = sorted(counts, key=lambda j: -counts[j])
        if order:
            layers.append(layer(pal_hex[order[0]], lambda v: v >= 0))  # the silhouette, under the rest
            layers += [layer(pal_hex[j], lambda v, j=j: v == j) for j in order[1:]]
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img">' % (width, height)
    return head + ("<title>%s</title>" % clean_title(title) if title else "") + "".join(layers) + "</svg>\n"
