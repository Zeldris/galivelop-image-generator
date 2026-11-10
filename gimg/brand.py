"""The brand process (D37), small enough for the command line and the interface to share: matte, trace, wordmark, lockup and system.

- `matte(src, out=None, **opts)`: the PNG `src` with its flat background made transparent (`matte.remove_bg`). The default
  `out` is next to `src`, with ``-alpha`` before the extension; the original is never written.
- `trace(src, out=None, mode="color", ...)`: the PNG `src` as an SVG (`trace.to_svg`); ``matte=True`` removes the
  background first. ``mode`` is ``color``, ``mono`` or ``silhouette`` (``silueta`` also works).
- `lockup(emblem, wordmark, out=None, layout="h"|"v")`: the emblem SVG and the wordmark SVG in one, as paths only (proportions of
  the sheet: wordmark height 0.45 and gap 0.25 of the emblem diameter in ``h``; width 1.6 in ``v``).
- `system(src, name, font, out_dir)`: the seven files of the logo system (matte, traces, wordmark, both lockups, contact sheet).
- `wordmark(text, font, out=None, weight=800, spacing=0.12)`: `text` set in the font file `font` and turned into paths, with no
  ``<text>`` and no need for the font afterwards. ``rsvg-convert`` draws the text big in black; the result is cropped
  to the ink and traced in mono mode. The font reaches ``rsvg-convert`` through a throwaway fontconfig file that adds a
  copy of it to the system fonts (a variable font gets the weight asked for).

Each returns a dict (``out`` is the written path) and raises `GimgError` (``brand.*``): the ``ValueError`` of the
modules below becomes ``brand.bad_option``. Stdlib plus ``rsvg-convert`` (only for the wordmark), called without a shell.
"""
from __future__ import annotations

import os
import re
import shutil
import struct
import subprocess
import tempfile
import time
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

from . import fsutil, matte as _matte, png, trace as _trace
from .errors import GimgError

TOOL = "rsvg-convert"
TIMEOUT_S = 120
MAX_TEXT = 60
FONT_PX = 260
MAX_PIXELS = 1 << 24  # the limit of `png.read_rgba`
PAD_PX = 6
MIN_TRANSPARENT = 0.02  # a matte that frees less than this found no flat background
MODES = {"color": "color", "mono": "mono", "silhouette": "silueta", "silueta": "silueta"}


def _bad(exc) -> GimgError:
    return GimgError("brand.bad_option", reason=str(exc))


def default_out(src, suffix: str, ext: str) -> str:
    """`src` with `suffix` before a new extension, in the same folder: ``a/b.png`` -> ``a/b-alpha.png``."""
    p = Path(src)
    return str(p.with_name(p.stem + suffix + ext))


def _check_out(src, out) -> str:
    out = str(out)
    if os.path.exists(out) and os.path.exists(str(src)) and os.path.samefile(out, str(src)):
        raise GimgError("brand.out_is_input", path=out)
    return out


def _write(path: str, data: bytes) -> None:
    """Atomic write; the file gets the mode of a plain open(); any OSError is ``brand.write_failed``."""
    folder = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=folder, prefix=".brand-", suffix=".tmp")
    except OSError as exc:
        raise GimgError("brand.write_failed", path=str(path), reason=str(exc.strerror or exc))
    try:
        fsutil.honour_umask(fd)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException as exc:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        if isinstance(exc, OSError):
            raise GimgError("brand.write_failed", path=str(path), reason=str(exc.strerror or exc))
        raise


def _opaque(rgba) -> bool:
    return all(a >= 250 for a in rgba[3::4])


def matte(src, out=None, tol: float = 30, soft: float = 80, border: int = 6, grow: int = 3) -> dict:
    """Write the transparent copy of `src` (see the module docstring); ``tol``/``soft`` are ``t0``/``t1`` of `remove_bg`."""
    out = _check_out(src, out or default_out(src, "-alpha", ".png"))
    width, height, rgba = png.read_rgba(src)
    try:
        res = _matte.remove_bg(width, height, rgba, t0=tol, t1=soft, border=border, grow=grow)
        bg = _matte.border_color(width, height, rgba, border)
        data = png.rgba_bytes(width, height, res)
    except ValueError as exc:
        raise _bad(exc)
    _write(out, data)
    clear = sum(1 for a in res[3::4] if a == 0)
    return {"src": str(src), "out": out, "size": [width, height], "background": "#%02x%02x%02x" % bg,
            "transparent": round(clear / (width * height), 4)}


def parse_palette(text) -> list:
    """``"#aabbcc,#112233"`` -> ``["#aabbcc", "#112233"]`` (a list passes through); a bad color is ``brand.bad_option``."""
    items = [s.strip() for s in text.split(",")] if isinstance(text, str) else list(text)
    items = [s for s in items if s]
    try:
        for item in items:
            _trace.parse_hex(item)
    except ValueError as exc:
        raise _bad(exc)
    return items


def trace(src, out=None, mode: str = "color", palette=None, colors=None, dp_tol: float = 1.2, min_island: float = 12,
          matte: bool = False, **opts) -> dict:
    """Write the SVG of `src`; ``opts`` go to `trace.to_svg` (``color``, ``max_side``, ``title``...)."""
    if mode not in MODES:
        raise GimgError("brand.bad_option", reason="mode must be one of %s (got %r)" % (", ".join(MODES), mode))
    if palette and colors is not None:
        raise GimgError("brand.bad_option", reason="--palette and --colors exclude each other")
    out = _check_out(src, out or default_out(src, "", ".svg"))
    width, height, rgba = png.read_rgba(src)
    had_alpha = not _opaque(rgba)
    try:
        if matte:
            rgba = _matte.remove_bg(width, height, rgba)
        if colors is not None:
            opts["ncolores"] = colors
        svg = _trace.to_svg(width, height, rgba, MODES[mode], palette=parse_palette(palette) if palette else None,
                            dp_tol=dp_tol, min_island=min_island, **opts)
    except ValueError as exc:
        raise _bad(exc)
    _write(out, svg.encode("utf-8"))
    return {"src": str(src), "out": out, "size": [width, height], "mode": mode, "paths": svg.count("<path"),
            "bytes": len(svg.encode("utf-8")), "matted": bool(matte),
            "opaque_background": not had_alpha and not matte}


# ---------- wordmark ----------

def _name_table(data: bytes, path) -> str:
    """The family name of an sfnt font (name 16, else 1); anything else is ``brand.font_unreadable``."""
    try:
        base = struct.unpack(">I", data[12:16])[0] if data[:4] == b"ttcf" else 0
        if data[base:base + 4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
            raise ValueError("not a TrueType or OpenType font")
        count = struct.unpack(">H", data[base + 4:base + 6])[0]
        for i in range(count):
            tag, _sum, off, length = struct.unpack(">4sIII", data[base + 12 + i * 16:base + 28 + i * 16])
            if tag == b"name":
                table = data[off:off + length]
                _fmt, n, string_off = struct.unpack(">HHH", table[:6])
                names = {}
                for j in range(n):
                    plat, _enc, _lang, name_id, ln, so = struct.unpack(">6H", table[6 + j * 12:18 + j * 12])
                    raw = table[string_off + so:string_off + so + ln]
                    text = raw.decode("utf-16-be" if plat in (0, 3) else "latin-1", errors="replace").strip()
                    if text and name_id in (1, 16):
                        names.setdefault(name_id, text)
                if names:
                    return names.get(16) or names[1]
        raise ValueError("no family name")
    except (struct.error, ValueError) as exc:
        raise GimgError("brand.font_unreadable", path=str(path), reason=str(exc))


def _fontconfig(folder: str) -> str:
    conf = os.path.join(folder, "fonts.conf")
    posix = lambda p: escape(Path(p).as_posix())
    with open(conf, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
                 '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
                 '<dir>%s</dir><cachedir>%s</cachedir></fontconfig>'
                 % (posix(os.path.join(folder, "fonts")), posix(os.path.join(folder, "cache"))))
    return conf


def _rsvg(argv, env) -> None:
    if shutil.which(argv[0]) is None:
        raise GimgError("brand.tool_missing", tool=TOOL)
    try:
        done = subprocess.run(argv, capture_output=True, stdin=subprocess.DEVNULL, timeout=TIMEOUT_S, env=env)
    except subprocess.TimeoutExpired:
        raise GimgError("brand.timeout", tool=TOOL, seconds=TIMEOUT_S)
    except FileNotFoundError:
        raise GimgError("brand.tool_missing", tool=TOOL)
    except OSError as exc:
        raise GimgError("brand.tool_failed", tool=TOOL, reason=str(exc.strerror or exc)[:300])
    if done.returncode != 0:
        lines = [ln.strip() for ln in done.stderr.decode("utf-8", errors="replace").splitlines() if ln.strip()]
        raise GimgError("brand.tool_failed", tool=TOOL, reason=(lines[-1][:300] if lines else "exit code %d" % done.returncode))


def _touches_edge(width: int, height: int, rgba) -> bool:
    """True if any pixel of the outer ring is not fully transparent (the text was cut off)."""
    alpha = rgba[3::4]
    return (any(alpha[:width]) or any(alpha[(height - 1) * width:]) or any(alpha[::width])
            or any(alpha[width - 1::width]))


def _crop(width: int, height: int, rgba, pad: int):
    """The box of the ink (alpha >= 128) plus `pad` transparent pixels, as ``(w, h, rgba)``; ``None`` if there is none."""
    alpha = rgba[3::4]
    rows = [y for y in range(height) if any(a >= 128 for a in alpha[y * width:(y + 1) * width])]
    if not rows:
        return None
    cols = [x for x in range(width) if any(a >= 128 for a in alpha[x::width])]
    x0, x1, y0, y1 = cols[0], cols[-1] + 1, rows[0], rows[-1] + 1
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    res = bytearray(w * h * 4)
    for y in range(y0, y1):
        s = (y * width + x0) * 4
        d = ((y - y0 + pad) * w + pad) * 4
        res[d:d + (x1 - x0) * 4] = rgba[s:s + (x1 - x0) * 4]
    return w, h, res


def wordmark(text: str, font, out=None, weight: int = 800, spacing: float = 0.12, title: str = "") -> dict:
    """Write the SVG of `text` in `font`, as paths (see the module docstring). ``spacing`` is in em."""
    text = " ".join("".join(ch for ch in str(text) if ch.isspace() or unicodedata.category(ch) != "Cc").split())
    if not text:
        raise GimgError("brand.empty_text")
    if len(text) > MAX_TEXT:
        raise GimgError("brand.text_too_long", max=MAX_TEXT)
    if not isinstance(weight, int) or not 1 <= weight <= 1000 or not -0.5 <= spacing <= 2:
        raise GimgError("brand.bad_option", reason="weight 1-1000 and spacing between -0.5 and 2 em")
    try:
        with open(font, "rb") as fh:
            data = fh.read(64 * 1024 * 1024)
    except OSError as exc:
        raise GimgError("brand.font_unreadable", path=str(font), reason=str(exc.strerror or exc))
    family = _name_table(data, font)
    out = _check_out(font, out or "wordmark.svg")
    gap = spacing * FONT_PX
    canvas_w = int(len(text) * (FONT_PX * 1.3 + gap)) + FONT_PX
    canvas_h = int(FONT_PX * 1.8)
    if canvas_w * canvas_h > MAX_PIXELS:
        raise GimgError("brand.wordmark_no_fit", reason="too long for this spacing: use a shorter text or less spacing")
    if shutil.which(TOOL) is None:
        raise GimgError("brand.tool_missing", tool=TOOL)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d"><text x="%d" y="%d" font-family="%s" '
           'font-weight="%d" font-size="%d" letter-spacing="%s" fill="#000">%s</text></svg>'
           % (canvas_w, canvas_h, FONT_PX // 4, int(FONT_PX * 1.3), escape(family, {'"': "&quot;"}), weight, FONT_PX,
              round(gap, 2), escape(text)))
    with tempfile.TemporaryDirectory(prefix="gimg-brand-") as tmp:
        os.makedirs(os.path.join(tmp, "fonts"))
        shutil.copyfile(font, os.path.join(tmp, "fonts", "font" + (Path(font).suffix.lower() or ".ttf")))
        env = dict(os.environ, FONTCONFIG_FILE=_fontconfig(tmp))
        src, big = os.path.join(tmp, "w.svg"), os.path.join(tmp, "w.png")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(svg)
        _rsvg([TOOL, "-o", big, src], env)
        if not os.path.exists(big):
            raise GimgError("brand.tool_failed", tool=TOOL, reason="no output")
        width, height, rgba = png.read_rgba(big)
    if _touches_edge(width, height, rgba):
        raise GimgError("brand.wordmark_no_fit", reason="the letters reach the edge of the drawing: use a shorter text or less spacing")
    box = _crop(width, height, rgba, PAD_PX)
    if box is None:
        raise GimgError("brand.empty_wordmark", family=family)
    w, h, rgba = box
    try:
        res = _trace.to_svg(w, h, rgba, "mono", ncolores=1, max_side=1000, dp_tol=0.8, min_island=6,
                            title=title or text)
    except ValueError as exc:
        raise _bad(exc)
    _write(out, res.encode("utf-8"))
    return {"out": str(out), "text": text, "font": str(font), "family": family, "weight": weight, "spacing": spacing,
            "size": [w, h], "paths": res.count("<path"), "bytes": len(res.encode("utf-8"))}


# ---------- lockup and system ----------

_SVG = re.compile(r"^\s*(?:<\?xml[^>]*\?>\s*)?<svg\b([^>]*)>(.*)</svg>\s*$", re.S)
_VIEWBOX = re.compile(r'viewBox="\s*([-\d.eE]+)[ ,]+([-\d.eE]+)[ ,]+([-\d.eE]+)[ ,]+([-\d.eE]+)\s*"')
_FORBIDDEN = re.compile(r"<(text|image|foreignObject|script|use)\b", re.I)
_TITLE = re.compile(r"<title>.*?</title>", re.S)
_PATH_D = re.compile(r'<path\b[^>]*?\sd="([^"]*)"', re.S)
_PATH_TOKEN = re.compile(r"[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
LAYOUTS = ("h", "v")
SYSTEM_FILES = ("emblema-alpha.png", "emblema.svg", "emblema-mono.svg", "wordmark.svg", "lockup-h.svg", "lockup-v.svg",
                "contactos.png")
LIGHT, DARK = "#f1e4d0", "#0f1428"
INK_ON_LIGHT, INK_ON_DARK = "#221c16", "#f1e4d0"


def slugify(name: str) -> str:
    """``"Tarkor Ñandú"`` -> ``"tarkor-nandu"``: accents out, ASCII letters and digits, hyphens between; ``""`` if none."""
    plain = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")


def _read_svg(path) -> dict:
    """``{"vb": (x, y, w, h), "inner": str, "box": (x0, y0, x1, y1)}`` of a traced SVG; ``brand.bad_svg`` if it is not one."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read(32 * 1024 * 1024)
    except (OSError, UnicodeDecodeError) as exc:
        raise GimgError("brand.bad_svg", path=str(path), reason=str(getattr(exc, "strerror", None) or exc))
    m = _SVG.match(text)
    vb = _VIEWBOX.search(m.group(1)) if m else None
    if not m or not vb:
        raise GimgError("brand.bad_svg", path=str(path), reason="not an SVG with a viewBox (the one of `brand trace` or `brand wordmark`)")
    if _FORBIDDEN.search(text):
        raise GimgError("brand.bad_svg", path=str(path), reason="it has <text>, <image>, <use>, <script> or <foreignObject>: only paths")
    x, y, w, h = (float(v) for v in vb.groups())
    if not (w > 0 and h > 0):
        raise GimgError("brand.bad_svg", path=str(path), reason="the viewBox has no area")
    inner = _TITLE.sub("", m.group(2))
    return {"vb": (x, y, w, h), "inner": inner, "box": _ink_box(inner) or (x, y, x + w, y + h)}


def _ink_box(inner: str):
    """The box of the coordinates of the absolute paths in `inner`; ``None`` if there are other shapes or relative commands."""
    if re.search(r"<(rect|circle|ellipse|polygon|polyline|line)\b", inner):
        return None
    xs, ys = [], []
    for d in _PATH_D.findall(inner):
        nums = []
        for tok in _PATH_TOKEN.findall(d):
            if tok.isalpha():
                if tok not in "MLCZ":
                    return None
                if len(nums) % 2:
                    return None
            else:
                nums.append(float(tok))
        if len(nums) % 2:
            return None
        xs += nums[0::2]
        ys += nums[1::2]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _num(v: float) -> str:
    return ("%.3f" % v).rstrip("0").rstrip(".")


def _place(piece: dict, x: float, y: float, scale: float) -> str:
    """`piece` drawn with its ink box's corner at ``(x, y)`` and scaled by `scale`."""
    x0, y0 = piece["box"][:2]
    return '<g transform="translate(%s %s) scale(%s)">%s</g>' % (_num(x - x0 * scale), _num(y - y0 * scale), _num(scale), piece["inner"])


def lockup(emblem, wordmark, out=None, layout: str = "h", cap: float = 0.45, gap: float = 0.25, width: float = 1.6,
           margin: float = 0.0, color=None, title: str = "") -> dict:
    """Write one SVG with the `emblem` and the `wordmark` (both SVG files of this module), as paths only.

    The diameter D is the longer side of the emblem's ink box. ``h``: the wordmark's height is ``cap`` x D, ``gap`` x D to the
    right of the emblem, both centered vertically. ``v``: the wordmark's width is ``width`` x D, ``gap`` x D under the emblem,
    both centered horizontally. ``margin`` (x D) is free space around. ``color`` replaces ``currentColor`` in the wordmark.
    """
    if layout not in LAYOUTS:
        raise GimgError("brand.bad_option", reason="layout must be one of %s (got %r)" % (", ".join(LAYOUTS), layout))
    if not (0.01 <= cap <= 5 and 0 <= gap <= 5 and 0.01 <= width <= 10 and 0 <= margin <= 2):
        raise GimgError("brand.bad_option", reason="cap 0.01-5, gap 0-5, width 0.01-10 and margin 0-2 (in emblem diameters)")
    out = str(out or "lockup-%s.svg" % layout)
    for src in (emblem, wordmark):
        _check_out(src, out)
    em, wm = _read_svg(emblem), _read_svg(wordmark)
    if color:
        if not re.fullmatch(r"#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|[A-Za-z]{3,20}", str(color)):
            raise GimgError("brand.bad_option", reason="color %r is not #rgb, #rrggbb or a color name" % (color,))
        wm = dict(wm, inner=wm["inner"].replace("currentColor", str(color)))
    ew, eh = em["box"][2] - em["box"][0], em["box"][3] - em["box"][1]
    ww, wh = wm["box"][2] - wm["box"][0], wm["box"][3] - wm["box"][1]
    if min(ew, eh, ww, wh) <= 0:
        raise GimgError("brand.bad_svg", path=str(emblem if min(ew, eh) <= 0 else wordmark), reason="the drawing has no ink")
    d = max(ew, eh)
    pad, space = margin * d, gap * d
    if layout == "h":
        s = cap * d / wh
        ww2, wh2 = ww * s, wh * s
        total_w, total_h = ew + space + ww2, max(eh, wh2)
        parts = [_place(em, pad, pad + (total_h - eh) / 2, 1.0), _place(wm, pad + ew + space, pad + (total_h - wh2) / 2, s)]
    else:
        s = width * d / ww
        ww2, wh2 = ww * s, wh * s
        total_w, total_h = max(ew, ww2), eh + space + wh2
        parts = [_place(em, pad + (total_w - ew) / 2, pad, 1.0), _place(wm, pad + (total_w - ww2) / 2, pad + eh + space, s)]
    w, h = total_w + 2 * pad, total_h + 2 * pad
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" role="img">%s%s</svg>\n'
           % (_num(w), _num(h), "<title>%s</title>" % escape(title) if title else "", "".join(parts)))
    _write(out, svg.encode("utf-8"))
    return {"out": out, "layout": layout, "size": [round(w, 1), round(h, 1)], "paths": svg.count("<path"),
            "bytes": len(svg.encode("utf-8"))}


def _fit(piece: dict, x: float, y: float, w: float, h: float, ink=None) -> str:
    """`piece` centered in the box ``x, y, w, h``, as large as fits; `ink` is the ``color`` its ``currentColor`` resolves to."""
    vx, vy, vw, vh = piece["vb"]
    k = min(w / vw, h / vh)
    pw, ph = vw * k, vh * k
    inner = '<svg x="%s" y="%s" width="%s" height="%s" viewBox="%s %s %s %s">%s</svg>' % (
        _num(x + (w - pw) / 2), _num(y + (h - ph) / 2), _num(pw), _num(ph), _num(vx), _num(vy), _num(vw), _num(vh), piece["inner"])
    return '<g color="%s">%s</g>' % (ink, inner) if ink else inner


def _contact_svg(pieces: dict) -> tuple:
    """The SVG text and ``(width, height)`` of the contact sheet: every piece on light and on dark, then the small sizes."""
    col, row, margin, last = 640, 200, 40, 180
    rows = ("emblem", "mono", "wordmark", "lockup_h", "lockup_v")
    height = row * len(rows) + last
    parts = []
    for c, (bg, ink) in enumerate(((LIGHT, INK_ON_LIGHT), (DARK, INK_ON_DARK))):
        x0 = c * col
        parts.append('<rect x="%d" y="0" width="%d" height="%d" fill="%s"/>' % (x0, col, height, bg))
        for r, key in enumerate(rows):
            parts.append(_fit(pieces[key], x0 + margin, r * row + 20, col - 2 * margin, row - 40, ink))
        x = x0 + margin
        for size in (16, 32, 64, 128):
            parts.append(_fit(pieces["emblem"], x, len(rows) * row + (last - size) / 2, size, size, ink))
            x += size + 32
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>'
            % (2 * col, height, 2 * col, height, "".join(parts)), (2 * col, height))


def system(src, name: str, font, out_dir, weight: int = 800, spacing: float = 0.12, palette=None, colors=None, text=None,
           cap: float = 0.45, gap: float = 0.25, width: float = 1.6, force: bool = False) -> dict:
    """The logo system of `name` from the emblem PNG `src`, in `out_dir`: ``<slug>-emblema-alpha.png``, ``-emblema.svg``,
    ``-emblema-mono.svg``, ``-wordmark.svg``, ``-lockup-h.svg``, ``-lockup-v.svg`` and ``-contactos.png`` (see `SYSTEM_FILES`).

    Everything is built in a throwaway folder and copied in at the end, so a failure leaves `out_dir` as it was; a file that
    is already there is ``brand.exists`` unless `force`. The wordmark text is `text`, else `name` in capitals.
    """
    t0 = time.monotonic()
    slug = slugify(name)
    if not str(name).strip():
        raise GimgError("brand.empty_text")
    if not slug:
        raise GimgError("brand.bad_name", name=str(name))
    targets = {key: os.path.join(str(out_dir), "%s-%s" % (slug, key)) for key in SYSTEM_FILES}
    for path in targets.values():
        _check_out(src, path)
    clash = [os.path.basename(p) for p in targets.values() if os.path.lexists(p)]
    if clash and not force:
        raise GimgError("brand.exists", folder=str(out_dir), files=", ".join(clash))
    if shutil.which(TOOL) is None:
        raise GimgError("brand.tool_missing", tool=TOOL)
    if palette and colors is not None:
        raise GimgError("brand.bad_option", reason="--palette and --colors exclude each other")
    with tempfile.TemporaryDirectory(prefix="gimg-brand-") as tmp:
        t = {key: os.path.join(tmp, key) for key in SYSTEM_FILES}
        m = matte(src, t["emblema-alpha.png"])
        if m["transparent"] < MIN_TRANSPARENT:
            raise GimgError("brand.no_matte", path=str(src), transparent=round(m["transparent"] * 100, 1))
        title = str(name).strip()
        color = trace(t["emblema-alpha.png"], t["emblema.svg"], "color", palette, colors, title=title)
        mono = trace(t["emblema-alpha.png"], t["emblema-mono.svg"], "mono", title=title)
        word = wordmark(text if text else str(name).strip().upper(), font, t["wordmark.svg"], weight, spacing, title=title)
        lh = lockup(t["emblema.svg"], t["wordmark.svg"], t["lockup-h.svg"], "h", cap, gap, width, title=title)
        lv = lockup(t["emblema.svg"], t["wordmark.svg"], t["lockup-v.svg"], "v", cap, gap, width, title=title)
        pieces = {"emblem": _read_svg(t["emblema.svg"]), "mono": _read_svg(t["emblema-mono.svg"]),
                  "wordmark": _read_svg(t["wordmark.svg"]), "lockup_h": _read_svg(t["lockup-h.svg"]),
                  "lockup_v": _read_svg(t["lockup-v.svg"])}
        sheet_svg, sheet_size = _contact_svg(pieces)
        sheet_src = os.path.join(tmp, "contactos.svg")
        with open(sheet_src, "w", encoding="utf-8") as fh:
            fh.write(sheet_svg)
        _rsvg([TOOL, "-o", t["contactos.png"], sheet_src], dict(os.environ))
        if not os.path.exists(t["contactos.png"]):
            raise GimgError("brand.tool_failed", tool=TOOL, reason="no output")
        for key in SYSTEM_FILES:
            with open(t[key], "rb") as fh:
                _write(targets[key], fh.read())
    files = {key: targets[key] for key in SYSTEM_FILES}
    return {"src": str(src), "name": str(name).strip(), "slug": slug, "out_dir": str(out_dir), "files": files,
            "paths": {"emblem": color["paths"], "mono": mono["paths"], "wordmark": word["paths"], "lockup_h": lh["paths"],
                      "lockup_v": lv["paths"]},
            "contact_size": list(sheet_size), "overwritten": sorted(clash), "seconds": round(time.monotonic() - t0, 1)}


__all__ = ["matte", "trace", "wordmark", "lockup", "system", "slugify", "parse_palette", "default_out", "MODES", "LAYOUTS",
           "SYSTEM_FILES", "TOOL"]
