"""Export of a delivered PNG to the formats some channels ask for (`gimg export`): WebP, ICO, BMP of 24 bits, or a PNG of
another size. Stdlib only (D6): the encoders are written here.

The delivered image stays a PNG (it carries the provenance chunk); an export is a copy for one destination.

- **Crop:** ``--crop X,Y,W,H`` takes that box of the original (pixels) first, before anything else: a declared,
  repeatable crop instead of a hand-made copy.
- **Size:** ``--size WxH`` crops the source to the target's proportion (``cover``), by default centred (``--anchor``
  puts the box at the top, bottom, left or right, or in a corner: ``top-left``), and scales it down by
  area average on premultiplied alpha. Scaling up is refused: the source should be generated bigger.
- **WebP:** lossless (VP8L): subtract-green, one predictor for the whole image (the best of four, measured on a sample
  of rows) and prefix codes on literals, without backward references nor colour cache. Smaller than raw, about the
  size of the PNG; ``webp`` decoders read it like any other.
- **ICO:** one PNG per size (16 to 256, square; the source is cropped to a square first), as Windows Vista and later
  read it. The small sizes are scaled from the 256 one, which is faster and looks the same.
- **BMP:** 24 bits, bottom-up rows, no alpha (an installer of Windows refuses alpha): transparent pixels are laid over
  ``--background`` (white by default).
"""
from __future__ import annotations

import contextlib
import heapq
import math
import os
import re
import struct
import tempfile
from collections import Counter

from . import png
from .errors import GimgError

FORMATS = ("webp", "ico", "bmp", "png")
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
MAX_WEBP_SIDE = 16384
BACKGROUND = "#FFFFFF"

# ---------------------------------------------------------------------------------------------------- scaling


def _parse_size(text) -> tuple:
    match = re.fullmatch(r"\s*(\d+)\s*[xX×]\s*(\d+)\s*", str(text))
    if not match or not int(match.group(1)) or not int(match.group(2)):
        raise GimgError("export.bad_size", value=text)
    return int(match.group(1)), int(match.group(2))


def _parse_crop(text) -> tuple:
    try:
        box = tuple(int(v) for v in str(text).split(","))
    except ValueError:
        box = ()
    if len(box) != 4 or box[2] <= 0 or box[3] <= 0 or box[0] < 0 or box[1] < 0:
        raise GimgError("export.bad_crop", value=text)
    return box


ANCHORS = ("center", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right")


def _parse_anchor(text) -> tuple:
    """``(fx, fy)``: where the crop box sits along the slack, 0 = start, 0.5 = centre, 1 = end."""
    name = str(text).strip().lower()
    if name not in ANCHORS:
        raise GimgError("export.bad_anchor", value=text, anchors=", ".join(ANCHORS))
    parts = name.split("-")
    fx = 0.0 if "left" in parts else 1.0 if "right" in parts else 0.5
    fy = 0.0 if "top" in parts else 1.0 if "bottom" in parts else 0.5
    return fx, fy


def crop_box(width: int, height: int, rgba, box) -> bytearray:
    """The pixels of `box` (x, y, w, h) of `rgba`; `export.crop_outside` if it leaves the image."""
    x, y, w, h = box
    if x + w > width or y + h > height:
        raise GimgError("export.crop_outside", crop=",".join(str(v) for v in box), width=width, height=height)
    out = bytearray()
    for row in range(y, y + h):
        out += rgba[(row * width + x) * 4:(row * width + x + w) * 4]
    return out


def _parse_icon_sizes(text) -> tuple:
    try:
        sizes = tuple(sorted({int(part) for part in str(text).split(",") if part.strip()}))
    except ValueError:
        raise GimgError("export.bad_icon_sizes", value=text) from None
    if not sizes or sizes[0] < 1 or sizes[-1] > 256:
        raise GimgError("export.bad_icon_sizes", value=text)
    return sizes


def _parse_color(text) -> tuple:
    if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", str(text)):
        raise GimgError("export.bad_background", value=text)
    value = str(text).lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _taps(src_len: int, start: float, span: float, dst_len: int) -> list:
    """For each output pixel, ``[(source index, weight)]`` of the source interval it covers (weights add up to 1)."""
    step = span / dst_len
    out = []
    for i in range(dst_len):
        lo, hi = start + i * step, start + (i + 1) * step
        taps, j = [], int(lo)
        while j < hi - 1e-9 and j < src_len:
            part = min(hi, j + 1) - max(lo, j)
            if part > 1e-9:
                taps.append((j, part / step))
            j += 1
        out.append(taps)
    return out


def fit(width: int, height: int, rgba, dst_w: int, dst_h: int, anchor=(0.5, 0.5)) -> bytearray:
    """`rgba` cropped to the proportion of ``dst_w x dst_h`` (centred unless `anchor` = ``(fx, fy)`` says otherwise)
    and scaled down to it by area average."""
    if (dst_w, dst_h) == (width, height):
        return bytearray(rgba)
    scale = max(dst_w / width, dst_h / height)
    if scale > 1 + 1e-9:
        raise GimgError("export.upscale", width=width, height=height, target="%dx%d" % (dst_w, dst_h))
    span_x, span_y = dst_w / scale, dst_h / scale
    cols = _taps(width, (width - span_x) * anchor[0], span_x, dst_w)
    rows = _taps(height, (height - span_y) * anchor[1], span_y, dst_h)
    alpha = rgba[3::4]
    planes = [[c * a for c, a in zip(rgba[k::4], alpha)] for k in range(3)] + [list(alpha)]
    needed = sorted({j for taps in rows for j, _ in taps})
    wide = []  # per channel, {source row: [dst_w floats]}
    for plane in planes:
        by_row = {}
        for y in needed:
            base = y * width
            by_row[y] = [sum(plane[base + j] * w for j, w in taps) for taps in cols]
        wide.append(by_row)
    out = bytearray(dst_w * dst_h * 4)
    for y, taps in enumerate(rows):
        mixed = []
        for by_row in wide:
            acc = [0.0] * dst_w
            for j, w in taps:
                src = by_row[j]
                acc = [a + s * w for a, s in zip(acc, src)]
            mixed.append(acc)
        base = y * dst_w * 4
        for x in range(dst_w):
            a = mixed[3][x]
            o = base + x * 4
            if a >= 0.5:
                for k in range(3):
                    out[o + k] = min(255, max(0, round(mixed[k][x] / a)))
            out[o + 3] = min(255, max(0, round(a)))
    return out


# ---------------------------------------------------------------------------------------------------- BMP and ICO


def bmp_bytes(width: int, height: int, rgba, background=(255, 255, 255)) -> bytes:
    """A 24-bit BMP (BITMAPINFOHEADER, bottom-up, no alpha) of `rgba` laid over `background`."""
    stride = (width * 3 + 3) & ~3
    pad = b"\x00" * (stride - width * 3)
    bg_r, bg_g, bg_b = background
    rows = []
    for y in range(height - 1, -1, -1):
        row = bytearray(width * 3)
        src = rgba[y * width * 4:(y + 1) * width * 4]
        for x in range(width):
            r, g, b, a = src[x * 4:x * 4 + 4]
            if a != 255:
                r = (r * a + bg_r * (255 - a) + 127) // 255
                g = (g * a + bg_g * (255 - a) + 127) // 255
                b = (b * a + bg_b * (255 - a) + 127) // 255
            row[x * 3:x * 3 + 3] = bytes((b, g, r))
        rows.append(bytes(row) + pad)
    pixels = b"".join(rows)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0, len(pixels), 2835, 2835, 0, 0)
    head = struct.pack("<2sIHHI", b"BM", 14 + len(info) + len(pixels), 0, 0, 14 + len(info))
    return head + info + pixels


def ico_bytes(images) -> bytes:
    """An ICO of `images` ``[(side, rgba)]``, each entry a PNG (sizes 1 to 256)."""
    blobs = [(side, png.rgba_bytes(side, side, rgba)) for side, rgba in images]
    offset = 6 + 16 * len(blobs)
    head = struct.pack("<HHH", 0, 1, len(blobs))
    entries, data = b"", b""
    for side, blob in blobs:
        entries += struct.pack("<BBBBHHII", side % 256, side % 256, 0, 0, 1, 32, len(blob), offset + len(data))
        data += blob
    return head + entries + data


# ---------------------------------------------------------------------------------------------------- WebP (VP8L)

_CODE_LENGTH_ORDER = (17, 18, 0, 1, 2, 3, 4, 5, 16, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
_PREDICTOR_BITS = 9  # one predictor tile of 512 px: the whole image uses one mode
_MODES = (1, 2, 7, 12)  # L, T, average of L and T, L + T - TL


class _Bits:
    """LSB-first bit writer (the VP8L order)."""

    def __init__(self):
        self.out, self.acc, self.n = bytearray(), 0, 0

    def put(self, value: int, nbits: int) -> None:
        self.acc |= value << self.n
        self.n += nbits
        while self.n >= 8:
            self.out.append(self.acc & 0xFF)
            self.acc >>= 8
            self.n -= 8

    def done(self) -> bytes:
        if self.n:
            self.out.append(self.acc & 0xFF)
            self.acc, self.n = 0, 0
        return bytes(self.out)


def _code_lengths(counts, limit: int) -> list:
    """Huffman code lengths of `counts` (≥ 2 symbols used), none longer than `limit`: the counts are halved until fit."""
    used = [s for s, c in enumerate(counts) if c]
    shift = 0
    while True:
        lengths = [0] * len(counts)
        heap = [(max(1, counts[s] >> shift), i, [s]) for i, s in enumerate(used)]
        heapq.heapify(heap)
        tick = len(heap)
        while len(heap) > 1:
            w1, _, a = heapq.heappop(heap)
            w2, _, b = heapq.heappop(heap)
            for s in a + b:
                lengths[s] += 1
            heapq.heappush(heap, (w1 + w2, tick, a + b))
            tick += 1
        if max(lengths) <= limit:
            return lengths
        shift += 1


def _canonical(lengths) -> list:
    """``[(bit-reversed code, length)]`` per symbol: canonical codes, as the LSB-first reader takes them."""
    codes = [(0, 0)] * len(lengths)
    code = 0
    for length in range(1, max(lengths) + 1):
        for sym, ln in enumerate(lengths):
            if ln == length:
                codes[sym] = (int(format(code, "0%db" % length)[::-1], 2), length)
                code += 1
        code <<= 1
    return codes


def _length_tokens(lengths) -> list:
    """The code lengths as code-length symbols ``[(symbol, extra bits, extra value)]``: literals and runs of zeros."""
    tokens, i, n = [], 0, len(lengths)
    while i < n:
        if lengths[i] == 0:
            run = 1
            while i + run < n and lengths[i + run] == 0 and run < 138:
                run += 1
            if run >= 11:
                tokens.append((18, 7, run - 11))
            elif run >= 3:
                tokens.append((17, 3, run - 3))
            else:
                tokens.extend([(0, 0, 0)] * run)
            i += run
        else:
            tokens.append((lengths[i], 0, 0))
            i += 1
    return tokens


def _write_code(bits: _Bits, counts) -> list:
    """Write the prefix code of `counts` (alphabet = ``len(counts)``) and return ``[(code, length)]`` per symbol."""
    used = [s for s, c in enumerate(counts) if c]
    if len(used) <= 1:
        sym = used[0] if used else 0
        bits.put(1, 1)  # simple code
        bits.put(0, 1)  # one symbol
        if sym < 2:
            bits.put(0, 1)
            bits.put(sym, 1)
        else:
            bits.put(1, 1)
            bits.put(sym, 8)
        return [(0, 0)] * len(counts)
    lengths = _code_lengths(counts, 15)
    tokens = _length_tokens(lengths)
    tcounts = [0] * 19
    for sym, _, _ in tokens:
        tcounts[sym] += 1
    tused = [s for s, c in enumerate(tcounts) if c]
    if len(tused) == 1:
        tlengths = [0] * 19
        tlengths[tused[0]] = 1  # a code of one symbol reads zero bits
        tcodes = [(0, 0)] * 19
    else:
        tlengths = _code_lengths(tcounts, 7)
        tcodes = _canonical(tlengths)
    count = max(4, max(i + 1 for i, s in enumerate(_CODE_LENGTH_ORDER) if tlengths[s] or i < 4))
    bits.put(0, 1)  # normal code
    bits.put(count - 4, 4)
    for s in _CODE_LENGTH_ORDER[:count]:
        bits.put(tlengths[s], 3)
    bits.put(0, 1)  # every symbol's length is written
    for sym, nextra, extra in tokens:
        code, ln = tcodes[sym]
        if ln:
            bits.put(code, ln)
        if nextra:
            bits.put(extra, nextra)
    return _canonical(lengths)


def _row_residual(cur, prev, mode: int) -> bytes:
    """Residuals of one channel row, pixels 1.. (pixel 0 is predicted from the top), for a predictor `mode`."""
    left, top, top_left, here = cur[:-1], prev[1:], prev[:-1], cur[1:]
    if mode == 1:
        return bytes((c - l) & 255 for c, l in zip(here, left))
    if mode == 2:
        return bytes((c - t) & 255 for c, t in zip(here, top))
    if mode == 7:
        return bytes((c - ((l + t) >> 1)) & 255 for c, l, t in zip(here, left, top))
    return bytes((c - min(255, max(0, l + t - tl))) & 255 for c, l, t, tl in zip(here, left, top, top_left))


def _entropy(data) -> float:
    total = len(data)
    return -sum(c * math.log2(c / total) for c in Counter(data).values()) if total else 0.0


def _residuals(planes, width: int, height: int, mode: int) -> list:
    """The predicted planes (A, R, G, B), with the border rules of VP8L: (0, 0) from ARGB 0xff000000, the first row from
    the left, the first column from the top."""
    out = []
    for k, plane in enumerate(planes):
        res = bytearray(len(plane))
        res[0] = (plane[0] - (255 if k == 0 else 0)) & 255
        res[1:width] = bytes((c - l) & 255 for c, l in zip(plane[1:width], plane[:width - 1]))
        for y in range(1, height):
            o = y * width
            cur, prev = plane[o:o + width], plane[o - width:o]
            res[o] = (cur[0] - prev[0]) & 255
            res[o + 1:o + width] = _row_residual(cur, prev, mode)
        out.append(res)
    return out


def _best_mode(planes, width: int, height: int) -> int:
    if width < 2 or height < 2:
        return 1
    rows = range(1, height, max(1, height // 32))
    best = None
    for mode in _MODES:
        cost = 0.0
        for plane in planes:
            sample = b"".join(_row_residual(plane[y * width:(y + 1) * width], plane[(y - 1) * width:y * width], mode)
                              for y in rows)
            cost += _entropy(sample)
        if best is None or cost < best[0]:
            best = (cost, mode)
    return best[1]


def webp_bytes(width: int, height: int, rgba) -> bytes:
    """A lossless WebP (VP8L) of `rgba`."""
    if width > MAX_WEBP_SIDE or height > MAX_WEBP_SIDE:
        raise GimgError("export.too_big", format="webp", max=MAX_WEBP_SIDE)
    a, r, g, b = bytes(rgba[3::4]), bytearray(rgba[0::4]), bytes(rgba[1::4]), bytearray(rgba[2::4])
    r = bytes((x - y) & 255 for x, y in zip(r, g))  # subtract green
    b = bytes((x - y) & 255 for x, y in zip(b, g))
    planes = [a, r, g, b]
    mode = _best_mode(planes, width, height)
    ra, rr, rg, rb = _residuals(planes, width, height, mode)

    bits = _Bits()
    bits.put(0x2F, 8)
    bits.put(width - 1, 14)
    bits.put(height - 1, 14)
    bits.put(0 if a.count(255) == len(a) else 1, 1)
    bits.put(0, 3)
    bits.put(1, 1)  # transform: subtract green
    bits.put(2, 2)
    bits.put(1, 1)  # transform: predictor, one mode in every tile
    bits.put(0, 2)
    bits.put(_PREDICTOR_BITS - 2, 3)
    bits.put(0, 1)  # sub-image: no colour cache; its five codes have one symbol each (zero bits per tile)
    for sym, size in ((mode, 280), (0, 256), (0, 256), (255, 256), (0, 40)):  # green carries the mode
        _write_code(bits, [1 if s == sym else 0 for s in range(size)])
    bits.put(0, 1)  # no more transforms
    bits.put(0, 1)  # main image: no colour cache
    bits.put(0, 1)  # no meta prefix codes
    green = _write_code(bits, list(_counts(rg)) + [0] * 24)
    red = _write_code(bits, _counts(rr))
    blue = _write_code(bits, _counts(rb))
    alpha = _write_code(bits, _counts(ra))
    _write_code(bits, [1] + [0] * 39)  # distance: unused
    _write_pixels(bits, rg, rr, rb, ra, green, red, blue, alpha)
    data = bits.done()
    body = b"WEBP" + b"VP8L" + struct.pack("<I", len(data)) + data + b"\x00" * (len(data) % 2)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def _counts(plane) -> list:
    counts = [0] * 256
    for value, c in Counter(plane).items():
        counts[value] = c
    return counts


def _write_pixels(bits: _Bits, rg, rr, rb, ra, green, red, blue, alpha) -> None:
    gc, gl = [c for c, _ in green], [n for _, n in green]
    rc, rl = [c for c, _ in red], [n for _, n in red]
    bc, bl = [c for c, _ in blue], [n for _, n in blue]
    ac, al = [c for c, _ in alpha], [n for _, n in alpha]
    acc, n, out = bits.acc, bits.n, bits.out
    for g, r, b, a in zip(rg, rr, rb, ra):
        acc |= gc[g] << n
        n += gl[g]
        acc |= rc[r] << n
        n += rl[r]
        acc |= bc[b] << n
        n += bl[b]
        acc |= ac[a] << n
        n += al[a]
        if n >= 64:
            out += (acc & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")
            acc >>= 64
            n -= 64
    bits.acc, bits.n = acc, n
    while bits.n >= 8:
        out.append(bits.acc & 0xFF)
        bits.acc >>= 8
        bits.n -= 8


# ---------------------------------------------------------------------------------------------------- the order


def _format_of(out) -> str:
    ext = os.path.splitext(str(out))[1].lower().lstrip(".")
    if ext not in FORMATS:
        raise GimgError("export.bad_format", path=out, formats=", ".join("." + f for f in FORMATS))
    return ext


def export(image, out, size=None, icon_sizes=None, background=BACKGROUND, force: bool = False,
           crop=None, anchor=None) -> dict:
    """Write `image` (a PNG) to `out` in the format of its extension and return ``{"out", "format", "sizes", "bytes"}``
    (plus ``"crop": [x, y, w, h]`` when `crop` is given).

    `crop` (``"X,Y,W,H"``, pixels of the original) is applied first; `anchor` (``center`` by default, ``top``,
    ``bottom``, ``left``, ``right`` or a corner) says where `size`'s crop box sits when the proportion changes.

    `size` (``"WxH"``) crops and scales the image (WebP, BMP, PNG); `icon_sizes` (``"16,32,…"``) are the sides of an
    ICO (by default ``ICON_SIZES`` up to the source's smaller side). An existing `out` is kept unless `force`."""
    fmt = _format_of(out)
    image, out = str(image), str(out)
    if fmt == "ico" and size is not None:
        raise GimgError("export.size_not_for_ico")
    if fmt != "ico" and icon_sizes is not None:
        raise GimgError("export.icon_sizes_only_ico")
    bg = _parse_color(background)
    target = _parse_size(size) if size is not None else None
    sides = _parse_icon_sizes(icon_sizes) if icon_sizes is not None else None
    box = _parse_crop(crop) if crop is not None else None
    anchor_xy = _parse_anchor(anchor) if anchor is not None else (0.5, 0.5)
    if os.path.exists(out) and os.path.exists(image) and os.path.samefile(image, out):
        raise GimgError("export.out_is_input", path=out)
    if os.path.exists(out) and not force:
        raise GimgError("export.exists", path=out)
    width, height, rgba = png.read_rgba(image)
    if box is not None:
        rgba = crop_box(width, height, rgba, box)
        width, height = box[2], box[3]
    if fmt == "ico":
        side = min(width, height)
        if sides is None:
            sides = tuple(s for s in ICON_SIZES if s <= side) or (side,)
        big = max(sides)
        square = fit(width, height, rgba, big, big, anchor_xy)
        images = [(s, square if s == big else fit(big, big, square, s, s)) for s in sides]
        blob, sizes = ico_bytes(images), [(s, s) for s in sides]
    else:
        if target is not None:
            rgba = fit(width, height, rgba, *target, anchor_xy)
            width, height = target
        sizes = [(width, height)]
        if fmt == "webp":
            blob = webp_bytes(width, height, rgba)
        elif fmt == "bmp":
            blob = bmp_bytes(width, height, rgba, bg)
        else:
            blob = png.rgba_bytes(width, height, rgba)
    folder = os.path.dirname(os.path.abspath(out))
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".gimg-export-", dir=folder)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(blob)
        os.chmod(tmp, 0o666 & ~_umask())
        os.replace(tmp, out)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise
    res = {"out": out, "format": fmt, "sizes": sizes, "bytes": len(blob)}
    if box is not None:
        res["crop"] = list(box)
    return res


def _umask() -> int:
    mask = os.umask(0)
    os.umask(mask)
    return mask

