"""Brand measurement (F2.9, D31): numbers about an image, never a verdict (`gimg measure`).

Stdlib plus ``ffmpeg``/``ffprobe``; the image is only read. What is measured:

- ``yavg`` / ``satavg``: ``signalstats`` of the whole image (BT.601, 0-255).
- ``palette``: share of pixels within CIE76 delta E < `DELTA_E` of some palette colour (image scaled to 256 px wide).
- ``families``: share of pixels per colour family (``--family NAME=#hex,#hex``, repeatable): each pixel goes to the
  nearest colour of all the families and counts for its family if it is within CIE76 delta E < `DELTA_E`, else for
  ``other`` (checks rules such as Tarkor's 60/30/10).
- ``emd``: Wasserstein-1 distance between the Y, Cb and Cr histograms of the image and of each reference, on a 160x64
  ``yuv444p`` decimation, identical to Tarkor's ``medir/emd.py``; the median per channel if there is more than one reference.
- ``contrast``: WCAG 2.x ratio of a text colour against the mean, the 10th and the 90th percentile of the relative
  luminance of a zone (pixels of the original image).

Failures are ``GimgError`` with a ``measure.*`` code.
"""
from __future__ import annotations

import os
import re
import shutil
import statistics
import subprocess

from .errors import GimgError

TIMEOUT_S = 120
DELTA_E = 15.0
PALETTE_WIDTH = 256
EMD_W, EMD_H = 160, 64
CHANNELS = ("Y", "Cb", "Cr")
_HEX = re.compile(r"#?([0-9a-fA-F]{6})")


def parse_hex(text) -> tuple:
    m = _HEX.fullmatch(str(text).strip())
    if not m:
        raise GimgError("measure.bad_hex", value=str(text))
    v = m.group(1)
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def hex_of(rgb) -> str:
    return "#%02x%02x%02x" % tuple(rgb)


def parse_families(specs) -> list:
    """``["NAME=#hex,#hex", ...]`` to ``[(name, [rgb, ...]), ...]`` in the given order; ``measure.bad_family`` on an
    empty or repeated name, a missing ``=`` or a family without colours (a bad colour is ``measure.bad_hex``)."""
    out, seen = [], set()
    for spec in specs:
        name, sep, colors = str(spec).partition("=")
        name = name.strip()
        parts = [c for c in colors.split(",") if c.strip()] if sep else []
        if not name or name in seen or not parts:
            raise GimgError("measure.bad_family", value=str(spec))
        seen.add(name)
        out.append((name, [parse_hex(c) for c in parts]))
    return out


def parse_zone(text) -> tuple:
    try:
        zone = tuple(int(v) for v in str(text).split(","))
    except ValueError:
        zone = ()
    if len(zone) != 4 or zone[2] <= 0 or zone[3] <= 0 or zone[0] < 0 or zone[1] < 0:
        raise GimgError("measure.bad_zone", value=str(text))
    return zone


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    """WCAG relative luminance (0-1)."""
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(l1, l2) -> float:
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def rgb_lab(rgb) -> tuple:
    """sRGB to CIE Lab, D65."""
    r, g, b = (_lin(c) for c in rgb)
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b) -> float:
    return sum((p - q) ** 2 for p, q in zip(a, b)) ** 0.5


def _last_line(text: bytes) -> str:
    lines = [ln.strip() for ln in text.decode("utf-8", errors="replace").splitlines() if ln.strip()]
    return lines[-1][:300] if lines else ""


def _run(argv, tool, scope="measure") -> bytes:
    """Run `argv` (no shell, no input, time limit) and return its stdout; a failure is a ``<scope>.*`` error
    (``measure`` by default; ``gimg sheet`` passes its own so the message names what it was doing)."""
    if shutil.which(argv[0]) is None:
        raise GimgError(scope + ".tool_missing", tool=tool)
    try:
        done = subprocess.run(argv, capture_output=True, stdin=subprocess.DEVNULL, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise GimgError(scope + ".timeout", tool=tool, seconds=TIMEOUT_S)
    except FileNotFoundError:
        raise GimgError(scope + ".tool_missing", tool=tool)
    except OSError as exc:
        raise GimgError(scope + ".tool_failed", tool=tool, reason=str(exc.strerror or exc)[:300])
    if done.returncode != 0:
        raise GimgError(scope + ".tool_failed", tool=tool,
                        reason=_last_line(done.stderr) or "exit code %d" % done.returncode)
    return done.stdout


def _check_file(path, scope="measure") -> None:
    if not os.path.isfile(path):
        raise GimgError(scope + ".unreadable", path=str(path))


def _input(path) -> str:
    """`path` as ffmpeg's ``file:`` protocol: a name starting with ``-`` or with ``proto:`` is read as a file."""
    return "file:" + os.path.abspath(str(path))


def _ffmpeg(path, vf, *extra) -> bytes:
    return _run(["ffmpeg", "-v", "error", "-nostdin", "-i", _input(path), "-vf", vf, "-frames:v", "1", *extra],
                "ffmpeg")


def image_size(path, scope="measure") -> tuple:
    _check_file(path, scope)
    out = _run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                "-of", "csv=p=0", _input(path)], "ffprobe", scope)
    try:
        w, h = out.decode().strip().split(",")[:2]
        size = int(w), int(h)
    except ValueError:
        raise GimgError(scope + ".unreadable", path=str(path))
    if size[0] <= 0 or size[1] <= 0:
        raise GimgError(scope + ".unreadable", path=str(path))
    return size


def signalstats(path) -> tuple:
    """``(YAVG, SATAVG)`` of the whole image."""
    _check_file(path)
    out = _ffmpeg(path, "format=yuv444p,signalstats,metadata=print:file=-", "-f", "null", "-").decode(errors="replace")
    vals = dict(re.findall(r"lavfi\.signalstats\.(YAVG|SATAVG)=([\d.]+)", out))
    if "YAVG" not in vals or "SATAVG" not in vals:
        raise GimgError("measure.unreadable", path=str(path))
    return float(vals["YAVG"]), float(vals["SATAVG"])


def pixels(path, zone=None) -> list:
    """RGB triples of the image (or of `zone` x,y,w,h in original pixels) scaled to at most 256 px wide."""
    size = image_size(path)
    filters = []
    sw, sh = size
    if zone:
        x, y, w, h = zone
        if x + w > size[0] or y + h > size[1]:
            raise GimgError("measure.zone_outside", zone="%d,%d,%d,%d" % zone, width=size[0], height=size[1])
        filters.append("crop=%d:%d:%d:%d" % (w, h, x, y))
        sw, sh = w, h
    tw = min(PALETTE_WIDTH, sw)
    th = max(1, round(sh * tw / sw))
    filters.append("scale=%d:%d:flags=area" % (tw, th))
    data = _ffmpeg(path, ",".join(filters), "-f", "rawvideo", "-pix_fmt", "rgb24", "-")
    if len(data) != tw * th * 3:
        raise GimgError("measure.unreadable", path=str(path))
    return [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]


def _nearest(pix, colors, threshold):
    """Per pixel, the index of the nearest of `colors` (CIE76) or None if it is not within `threshold`."""
    labs = [rgb_lab(c) for c in colors]
    cache = {}
    out = []
    for p in pix:
        if p not in cache:
            lab = rgb_lab(p)
            dists = [delta_e(lab, q) for q in labs]
            best = min(range(len(dists)), key=dists.__getitem__)
            cache[p] = best if dists[best] < threshold else None
        out.append(cache[p])
    return out


def palette_share(pix, palette, threshold=DELTA_E) -> dict:
    """``{"pct": share near any colour, "by_color": {hex: share whose nearest colour it is}}``, in percent."""
    counts = [0] * len(palette)
    near = 0
    for i in _nearest(pix, palette, threshold):
        if i is not None:
            counts[i] += 1
            near += 1
    total = len(pix) or 1
    by_color = {}
    for c, n in zip(palette, counts):
        by_color[hex_of(c)] = round(100.0 * n / total, 2)
    return {"pct": round(100.0 * near / total, 2), "by_color": by_color}


def family_share(pix, families, threshold=DELTA_E) -> dict:
    """`families` is ``[(name, [rgb, ...]), ...]``. ``{"deltaE", "by_family": {name: pct}, "other": pct}``: each pixel
    goes to the family of its nearest colour if within `threshold`, else to ``other``; percent, 2 decimals."""
    colors, owner = [], []
    for k, (_, rgbs) in enumerate(families):
        colors.extend(rgbs)
        owner.extend([k] * len(rgbs))
    counts, other = [0] * len(families), 0
    for i in _nearest(pix, colors, threshold):
        if i is None:
            other += 1
        else:
            counts[owner[i]] += 1
    total = len(pix) or 1
    return {"deltaE": threshold, "by_family": {n: round(100.0 * c / total, 2) for (n, _), c in zip(families, counts)},
            "other": round(100.0 * other / total, 2)}


def yuv_planes(path) -> list:
    """The Y, Cb and Cr planes (160x64 bytes each) of the image, as Tarkor's ``medir/emd.py`` reads them."""
    _check_file(path)
    data = _ffmpeg(path, "scale=%d:%d:flags=area,format=yuv444p" % (EMD_W, EMD_H), "-f", "rawvideo", "-")
    n = EMD_W * EMD_H
    if len(data) < 3 * n:
        raise GimgError("measure.unreadable", path=str(path))
    return [data[i * n:(i + 1) * n] for i in range(3)]


def _cdf(plane) -> list:
    hist = [0] * 256
    for v in plane:
        hist[v] += 1
    total, acc, out = len(plane), 0, []
    for n in hist:
        acc += n
        out.append(acc / total)
    return out


def emd(planes_a, planes_b) -> dict:
    """Wasserstein-1 between the histograms of each channel: sum over the 256 levels of |CDF a - CDF b|."""
    return {name: sum(abs(x - y) for x, y in zip(_cdf(a), _cdf(b))) for name, a, b in zip(CHANNELS, planes_a, planes_b)}


def _percentile(values, p):
    v = sorted(values)
    return v[min(len(v) - 1, int(p / 100 * len(v)))]


def contrast(pix, text_rgb) -> dict:
    lt = luminance(text_rgb)
    lums = [luminance(p) for p in pix]
    res = {"mean": contrast_ratio(lt, sum(lums) / len(lums)), "p10": contrast_ratio(lt, _percentile(lums, 10)),
           "p90": contrast_ratio(lt, _percentile(lums, 90))}
    res["worst"] = min(res.values())
    return {k: round(v, 2) for k, v in res.items()}


def measure(image, palette=None, refs=(), zone=None, text=None, families=None) -> dict:
    """All the measures asked for, as a JSON-ready dict. `palette` and `text` are hex strings, `zone` is x,y,w,h, `families` a list of ``NAME=#hex,#hex``."""
    fams = parse_families(families) if families else []
    palette_rgb = [parse_hex(c) for c in palette] if palette else []
    text_rgb = parse_hex(text) if text is not None else None
    zone_t = parse_zone(zone) if isinstance(zone, str) else zone
    if (zone_t is None) != (text_rgb is None):
        raise GimgError("cli.measure_zone_text")
    yavg, satavg = signalstats(image)
    result = {"image": str(image), "yavg": round(yavg, 2), "satavg": round(satavg, 2)}
    if palette_rgb:
        share = palette_share(pixels(image), palette_rgb)
        result["palette"] = {"colors": [hex_of(c) for c in palette_rgb], "deltaE": DELTA_E,
                             "pct": share["pct"], "by_color": share["by_color"]}
    if fams:
        result["families"] = family_share(pixels(image), fams)
    if refs:
        mine = yuv_planes(image)
        per_ref = []
        for ref in refs:
            per_ref.append({"ref": str(ref), **{k: round(v, 3) for k, v in emd(mine, yuv_planes(ref)).items()}})
        result["emd"] = per_ref
        if len(per_ref) > 1:
            result["emd_median"] = {k: round(statistics.median(r[k] for r in per_ref), 3) for k in CHANNELS}
    if zone_t is not None:
        result["contrast"] = {"zone": list(zone_t), "text": hex_of(text_rgb),
                              **contrast(pixels(image, zone_t), text_rgb)}
    return result
