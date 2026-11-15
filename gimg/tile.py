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
to `preview_side` px on its longer side (the view of a 1024 px piece at full size would be 4096 px). The source is never written. The input is
at most `MAX_PIXELS` (4,194,304 px in total, like 2048x2048; checked from the header before decoding): the pure-Python blend takes ~2 s per megapixel.
"""
from __future__ import annotations

import contextlib
import errno
import hashlib
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path

from . import export, fsutil, i18n, png
from .errors import GimgError

MAX_BLEND = 0.5
MIN_SIDE = 8  # a smaller piece has no room for a blend
MAX_PIXELS = 1 << 22  # 4,194,304 px in total (2048x2048 is the square that fits): pure Python spends ~2 s per megapixel; `png.read_rgba` alone allows 1 << 24
PREVIEW_GRID = 4
MIN_PREVIEW, MAX_PREVIEW = 8, 1024


def _smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _weights(n: int, f: float) -> list:
    """Weight of the original along one axis: 1 at the seam of the rolled image (between n//2 - 1 and n//2), 0 at `f` px."""
    s = n // 2
    w = [_smooth(1 - abs(i + 0.5 - s) / f) for i in range(n)]
    w[0] = w[-1] = 0.0  # the borders of the rolled image already join: with blend 0.5 the formula leaves them above 0
    return w


def _mix(p, q, m: float):
    """`p` * (1 - m) + `q` * m as RGBA 4-sequences, mixed with premultiplied alpha (a clear pixel has no color to give)."""
    ap, aq = p[3] * (1 - m), q[3] * m
    a = ap + aq
    if a <= 0:
        return (p[0], p[1], p[2], 0) if m < 0.5 else (q[0], q[1], q[2], 0)
    return tuple(int((p[c] * ap + q[c] * aq) / a + 0.5) for c in range(3)) + (int(a + 0.5),)


def _spots(offsets, weights) -> list:
    """Per-pixel constants for `_mix_into`: ``(byte offset, weight, ap, aq, a)`` where the last three are what `_mix`
    computes when both pixels are opaque (the common case), so they are worked out once per weight, not per pixel."""
    out = []
    for i, m in zip(offsets, weights):
        ap, aq = 255 * (1 - m), 255 * m
        out.append((i, m, ap, aq, ap + aq))
    return out


def _mix_into(dst: bytearray, other, spots) -> None:
    """`_mix` of ``dst`` with ``other`` at each spot of `_spots`, written into ``dst``: the same arithmetic as `_mix`
    (byte for byte the same result), without a call, two slices and a tuple per pixel."""
    for i, m, op, oq, oa in spots:
        j, k, l = i + 1, i + 2, i + 3
        a3, b3 = dst[l], other[l]
        if a3 == 255 and b3 == 255:
            dst[i] = int((dst[i] * op + other[i] * oq) / oa + 0.5)
            dst[j] = int((dst[j] * op + other[j] * oq) / oa + 0.5)
            dst[k] = int((dst[k] * op + other[k] * oq) / oa + 0.5)
            continue
        ap, aq = a3 * (1 - m), b3 * m
        a = ap + aq
        if a <= 0:
            if m >= 0.5:
                dst[i], dst[j], dst[k] = other[i], other[j], other[k]
            dst[l] = 0
            continue
        dst[i] = int((dst[i] * ap + other[i] * aq) / a + 0.5)
        dst[j] = int((dst[j] * ap + other[j] * aq) / a + 0.5)
        dst[k] = int((dst[k] * ap + other[k] * aq) / a + 0.5)
        dst[l] = int(a + 0.5)


def _check_options(width: int, height: int, blend: float) -> None:
    if min(width, height) < MIN_SIDE:
        raise ValueError("the image must be at least %d px on each side (it is %dx%d)" % (MIN_SIDE, width, height))
    if not 0 < blend <= MAX_BLEND:
        raise ValueError("blend must be above 0 and at most %s (got %s)" % (MAX_BLEND, blend))
    if blend * min(width, height) < 1:
        raise ValueError("blend x the shorter side must be at least 1 px (got %s x %d)" % (blend, min(width, height)))


def tileable(width: int, height: int, rgba, blend: float = 0.25) -> bytearray:
    """RGBA copy of `rgba` that repeats with no seam (see the module docstring); the input is not touched."""
    if len(rgba) != width * height * 4:
        raise ValueError("%d bytes do not fit a %dx%d RGBA image" % (len(rgba), width, height))
    _check_options(width, height, blend)
    sx, sy = width // 2, height // 2
    wx, wy = _weights(width, blend * width), _weights(height, blend * height)
    row_bytes = width * 4
    cut = (-sx % width) * 4  # rolled row: the last sx pixels of the row first
    live = [x for x in range(width) if wx[x] > 0]
    spots_x = _spots([x * 4 for x in live], [wx[x] for x in live])
    offsets_y = range(0, row_bytes, 4)
    # Pass 1, x: roll every row by half a width and cover its seam with the unrolled row (continuous there).
    mid = bytearray(len(rgba))
    for y in range(height):
        base = y * row_bytes
        row = bytes(rgba[base:base + row_bytes])
        rolled = bytearray(row[cut:] + row[:cut])
        _mix_into(rolled, row, spots_x)
        mid[base:base + row_bytes] = rolled
    # Pass 2, y: the same on the result of pass 1, so the borders of both axes are already continuous.
    out = bytearray(len(rgba))
    for y in range(height):
        base = y * row_bytes
        src = ((y - sy) % height) * row_bytes
        rolled = mid[src:src + row_bytes]
        m = wy[y]
        if m > 0:
            row = mid[base:base + row_bytes]
            rolled = bytearray(rolled)
            _mix_into(rolled, row, _spots(offsets_y, [m] * width))
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


BACKUP_GRACE = 600  # s: a copy younger than this may belong to a run that is still publishing (a run takes seconds)


def _backup_prefix(path) -> str:
    """Name start of the copy of `path` moved aside while it is replaced: it carries a short hash of the target's file
    name, so a copy left by a killed run can be matched to its target."""
    name = os.path.basename(str(path)).encode("utf-8", "surrogateescape")
    return ".gimg-bak-" + hashlib.sha1(name, usedforsecurity=False).hexdigest()[:12] + "-"


def _backup_name(path, pid=None, stamp=None) -> str:
    """``<prefix><pid>-<ns since epoch>-<random>``: who made the copy and when, so another run can tell a live one."""
    return "%s%d-%d-%s" % (_backup_prefix(path), os.getpid() if pid is None else pid,
                           time.time_ns() if stamp is None else stamp, uuid.uuid4().hex)


def _pid_alive(pid: int) -> bool:
    if os.name == "nt":  # `os.kill` would end the process there: the age alone decides
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:  # no permission to signal it: it exists
        return True
    return True


def _backup_info(rest: str):
    """``(pid, stamp)`` from the part of a copy's name after the prefix; ``(None, 0)`` for a name that carries none."""
    parts = rest.split("-")
    try:
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return None, 0


def recover_backups(paths) -> list:
    """Deal with copies ``.gimg-bak-*`` left beside each of `paths` by a run that was killed half way (SIGKILL, power).
    A copy of a run that may still be alive (its pid exists, or it is younger than `BACKUP_GRACE`) is not touched.
    If the target is missing, the oldest copy is the original and is put back; if the target exists, the copies are
    left where they are and reported (one may be the only copy of an original that the half-done run replaced:
    nothing is deleted that cannot be told apart from a leftover of a finished run). Returns one dict per copy,
    ``{"action": "restored" | "kept", "backup": ..., "path": ...}``."""
    done, now = [], time.time_ns()
    for path in paths:
        folder, prefix = os.path.dirname(os.path.abspath(path)), _backup_prefix(path)
        try:
            names = [n for n in os.listdir(folder) if n.startswith(prefix)]
        except OSError:
            continue
        found = []
        for name in names:
            pid, stamp = _backup_info(name[len(prefix):])
            if now - stamp < BACKUP_GRACE * 10 ** 9 or (pid is not None and _pid_alive(pid)):
                continue
            found.append((stamp, name))
        for stamp, name in sorted(found):
            bak = os.path.join(folder, name)
            try:
                if os.path.lexists(path):
                    done.append({"action": "kept", "backup": bak, "path": str(path)})
                else:
                    os.replace(bak, path)
                    done.append({"action": "restored", "backup": bak, "path": str(path)})
            except OSError as exc:
                raise GimgError("tile.write_failed", path=str(path),
                                reason="cannot recover %s: %s" % (bak, exc.strerror or exc))
    return done


def describe_recovery(item: dict, lang=None) -> str:
    return i18n.t("cli.out.tile_recovery_" + item["action"], lang, path=item["path"], backup=item["backup"])


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
    """Write every ``(path, data)`` or none: all are staged first; a target that is a folder is refused before
    anything is staged. Each existing target is moved aside (same folder) before the new file takes its place: on
    success a symlink is replaced by the new regular file (what it pointed at is not touched); if anything fails the
    ones already in place are put back (the old file, or nothing if there was none), a symlink and its mode as they were."""
    staged, done = [], []  # done: (path, backup or None)
    path = None
    try:
        for path, _ in files:
            if os.path.isdir(path) and not os.path.islink(path):
                raise OSError(errno.EISDIR, "Is a directory")
        for path, data in files:
            staged.append((_stage(path, data), path))
        for tmp, path in staged:
            backup = None
            if os.path.lexists(path):
                backup = os.path.join(os.path.dirname(os.path.abspath(path)), _backup_name(path))
                os.replace(path, backup)
            done.append((path, backup))
            os.replace(tmp, path)
    except BaseException as exc:
        failed = []  # rollback steps that did not work: said, never hidden behind the original error
        for p, backup in reversed(done):
            try:
                if backup:
                    os.replace(backup, p)
                else:
                    os.unlink(p)
            except OSError as rb:
                what = "put back %s from %s (the copy keeps the original)" % (p, backup) if backup else "remove %s" % p
                failed.append("%s: %s" % (what, rb.strerror or rb))
        done = []  # a backup that could not be put back stays on disk, and it may be the only copy of the original:
        # the next run reports it (`recover_backups`) and restores it only if the target is missing
        note = "; rollback incomplete (" + "; ".join(failed) + ")" if failed else ""
        if isinstance(exc, OSError):
            raise GimgError("tile.write_failed", path=str(path), reason=str(exc.strerror or exc) + note)
        if note:
            print(i18n.t("cli.out.tile_rollback_incomplete", detail=note[2:]), file=sys.stderr)
        raise
    finally:
        for tmp, _ in staged:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
        for _, backup in done:
            if backup:
                with contextlib.suppress(OSError):
                    os.unlink(backup)


def _same_file(a: str, b: str) -> bool:
    try:
        if os.path.exists(a) and os.path.exists(b):
            return os.path.samefile(a, b)
    except OSError as exc:  # a path that cannot be read (no permission on a folder, a loop of links)
        raise GimgError("tile.write_failed", path=str(a), reason=str(exc.strerror or exc))
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
    out = out or default_out(src)
    out = _check_target(src, out, True)  # identity only: nothing is touched on disk before the input is validated
    if preview is not None:
        preview = _check_target(src, preview, True)
        if _same_file(preview, out):
            raise GimgError("tile.same_outputs", path=out)
    width, height = png.size(src)  # the header only: an image over the limit is refused before it is inflated
    if width * height > MAX_PIXELS:
        raise GimgError("tile.too_big", width=width, height=height, max=MAX_PIXELS)
    try:  # from the header: nothing is recovered or touched for a call that fails validation
        _check_options(width, height, blend)
    except ValueError as exc:
        raise GimgError("tile.bad_option", reason=str(exc))
    recovered = recover_backups([out] + ([preview] if preview is not None else []))
    try:
        if not force:  # before inflating and blending: an existing output is refused without doing the work
            for target in (out, preview):
                if target is not None and os.path.exists(target):
                    raise GimgError("tile.exists", path=target)
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
        if recovered:
            res["recovered"] = recovered
        return res
    except GimgError as exc:
        exc.recovered = recovered  # what was put back before the failure: the command line says it
        raise
