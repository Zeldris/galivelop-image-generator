"""Seamless textures (`gimg tile`), stdlib only (D6): a PNG that repeats with no visible seam, and a 4x4 view to check it.

`tileable(width, height, rgba, blend=0.25)` rolls the image by half a piece in x and y (`S`): the original's borders now
meet in the middle cross of `S`, and `S`'s own borders are the original's centre lines, which are neighbours in the
original, so `S` repeats with no seam at its edges. The cross (the old seam) is then covered with the original `O`, whose
centre is continuous there: ``out = S * (1 - m) + O * m``, with ``m`` 1 on the cross and a smooth fall (smoothstep) to 0
at ``blend`` of the side on each side of it. It is done one axis after the other (x, then y on that result): blending both
at once would bring the original's mismatched borders in along the bar of the cross. ``blend`` is in
``(0, 0.5]``. A larger ``blend`` hides the join better and ghosts more of the picture; there is no scale, mark or
border added. The blend is done with premultiplied alpha, so a clear pixel does not tint its neighbours.

`repeat(width, height, rgba, nx, ny)` is `nx` x `ny` copies of the piece, for the view that proves the result.
`tile(src, out=None, blend=0.25, preview=None, preview_side=256, force=False)` is the command: it writes the seamless PNG
(by default next to `src`, with ``-tile`` before the extension) and, if asked, the 4x4 view with each piece scaled down
to `preview_side` px on its longer side (the view of a 1024 px piece at full size would be 4096 px). The source is never written.
"""
from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

from . import export, fsutil, png
from .errors import GimgError

MAX_BLEND = 0.5
MIN_SIDE = 8  # a smaller piece has no room for a blend
PREVIEW_GRID = 4
MIN_PREVIEW, MAX_PREVIEW = 8, 1024


def _smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _weights(n: int, f: float) -> list:
    """Weight of the original along one axis: 1 at the seam of the rolled image (between n//2 - 1 and n//2), 0 at `f` px."""
    s = n // 2
    return [_smooth(1 - abs(i + 0.5 - s) / f) for i in range(n)]


def _mix(p, q, m: float):
    """`p` * (1 - m) + `q` * m as RGBA 4-sequences, mixed with premultiplied alpha (a clear pixel has no color to give)."""
    ap, aq = p[3] * (1 - m), q[3] * m
    a = ap + aq
    if a <= 0:
        return (p[0], p[1], p[2], 0) if m < 0.5 else (q[0], q[1], q[2], 0)
    return tuple(int((p[c] * ap + q[c] * aq) / a + 0.5) for c in range(3)) + (int(a + 0.5),)


def tileable(width: int, height: int, rgba, blend: float = 0.25) -> bytearray:
    """RGBA copy of `rgba` that repeats with no seam (see the module docstring); the input is not touched."""
    if len(rgba) != width * height * 4:
        raise ValueError("%d bytes do not fit a %dx%d RGBA image" % (len(rgba), width, height))
    if min(width, height) < MIN_SIDE:
        raise ValueError("the image must be at least %d px on each side (it is %dx%d)" % (MIN_SIDE, width, height))
    if not 0 < blend <= MAX_BLEND:
        raise ValueError("blend must be above 0 and at most %s (got %s)" % (MAX_BLEND, blend))
    if blend * min(width, height) < 1:
        raise ValueError("blend x the shorter side must be at least 1 px (got %s x %d)" % (blend, min(width, height)))
    sx, sy = width // 2, height // 2
    wx, wy = _weights(width, blend * width), _weights(height, blend * height)
    row_bytes = width * 4
    cut = (-sx % width) * 4  # rolled row: the last sx pixels of the row first
    live = [x for x in range(width) if wx[x] > 0]
    # Pass 1, x: roll every row by half a width and cover its seam with the unrolled row (continuous there).
    mid = bytearray(len(rgba))
    for y in range(height):
        base = y * row_bytes
        row = bytes(rgba[base:base + row_bytes])
        rolled = bytearray(row[cut:] + row[:cut])
        for x in live:
            m, i = wx[x], x * 4
            rolled[i:i + 4] = bytes(_mix(rolled[i:i + 4], row[i:i + 4], m))
        mid[base:base + row_bytes] = rolled
    # Pass 2, y: the same on the result of pass 1, so the borders of both axes are already continuous.
    out = bytearray(len(rgba))
    for y in range(height):
        base = y * row_bytes
        rolled = mid[((y - sy) % height) * row_bytes:][:row_bytes]
        m = wy[y]
        if m > 0:
            row = mid[base:base + row_bytes]
            rolled = bytearray(rolled)
            for i in range(0, row_bytes, 4):
                rolled[i:i + 4] = bytes(_mix(rolled[i:i + 4], row[i:i + 4], m))
        out[base:base + row_bytes] = rolled
    return out


def repeat(width: int, height: int, rgba, nx: int = PREVIEW_GRID, ny: int = PREVIEW_GRID) -> bytearray:
    """`nx` x `ny` copies of the piece, side by side."""
    if len(rgba) != width * height * 4 or nx < 1 or ny < 1:
        raise ValueError("cannot repeat %d bytes as %dx%d pieces of %dx%d" % (len(rgba), nx, ny, width, height))
    out = bytearray()
    for _ in range(ny):
        for y in range(height):
            out += bytes(rgba[y * width * 4:(y + 1) * width * 4]) * nx
    return out


def default_out(src) -> str:
    p = Path(src)
    return str(p.with_name(p.stem + "-tile.png"))


def _stage(path: str, data: bytes) -> str:
    """Write `data` to a temporary file next to `path` and return its name (`os.replace` puts it in place)."""
    folder = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".gimg-tile-", dir=folder)
    except OSError as exc:
        raise GimgError("tile.write_failed", path=str(path), reason=str(exc.strerror or exc))
    try:
        fsutil.honour_umask(fd)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
    except BaseException as exc:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        if isinstance(exc, OSError):
            raise GimgError("tile.write_failed", path=str(path), reason=str(exc.strerror or exc))
        raise
    return tmp


def _publish(files) -> None:
    """Write every ``(path, data)`` or none: all are staged first, so a failure on any leaves no output behind."""
    staged = []
    try:
        for path, data in files:
            staged.append((_stage(path, data), path))
        for tmp, path in staged:
            os.replace(tmp, path)
    except OSError as exc:
        raise GimgError("tile.write_failed", path=str(path), reason=str(exc.strerror or exc))
    finally:
        for tmp, _ in staged:
            with contextlib.suppress(OSError):
                os.unlink(tmp)


def _same_file(a: str, b: str) -> bool:
    if os.path.exists(a) and os.path.exists(b):
        return os.path.samefile(a, b)
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def _check_target(src, path, force) -> str:
    path = str(path)
    if _same_file(path, str(src)):
        raise GimgError("tile.out_is_input", path=path)
    if os.path.exists(path) and not force:
        raise GimgError("tile.exists", path=path)
    return path


def tile(src, out=None, blend: float = 0.25, preview=None, preview_side: int = 256, force: bool = False) -> dict:
    """Write the seamless copy of the PNG `src` (and the 4x4 view in `preview`); returns the written paths and the size."""
    if not MIN_PREVIEW <= preview_side <= MAX_PREVIEW:
        raise GimgError("tile.bad_preview_side", value=preview_side, low=MIN_PREVIEW, high=MAX_PREVIEW)
    out = _check_target(src, out or default_out(src), force)
    if preview is not None:
        preview = _check_target(src, preview, force)
        if _same_file(preview, out):
            raise GimgError("tile.same_outputs", path=out)
    width, height, rgba = png.read_rgba(src)
    try:
        result = tileable(width, height, rgba, blend)
    except ValueError as exc:
        raise GimgError("tile.bad_option", reason=str(exc))
    files = [(out, png.rgba_bytes(width, height, result))]
    res = {"src": str(src), "out": out, "size": [width, height], "blend": blend}
    if preview is not None:
        scale = min(1.0, preview_side / max(width, height))
        pw, ph = max(1, round(width * scale)), max(1, round(height * scale))
        small = export.fit(width, height, result, pw, ph) if (pw, ph) != (width, height) else result
        grid = repeat(pw, ph, small)
        files.append((preview, png.rgba_bytes(pw * PREVIEW_GRID, ph * PREVIEW_GRID, grid)))
        res["preview"] = preview
        res["preview_size"] = [pw * PREVIEW_GRID, ph * PREVIEW_GRID]
    _publish(files)
    return res
