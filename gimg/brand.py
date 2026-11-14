"""The brand process (D37), small enough for the command line and the interface to share: matte, trace, wordmark, lockup and system.

- `matte(src, out=None, **opts)`: the PNG `src` with its flat background made transparent (`matte.remove_bg`). The default
  `out` is next to `src`, with ``-alpha`` before the extension; the original is never written.
- `trace(src, out=None, mode="color", ...)`: the PNG `src` as an SVG (`trace.to_svg`); ``matte=True`` removes the
  background first. ``mode`` is ``color``, ``mono`` or ``silhouette`` (``silueta`` also works).
- `lockup(emblem, wordmark, out=None, layout="h"|"v")`: the emblem SVG and the wordmark SVG in one, as paths only (proportions of
  the sheet: wordmark height 0.45 and gap 0.25 of the emblem diameter in ``h``; width 1.6 in ``v``).
- `system(src, name, font, out_dir)`: the seven files of the logo system (matte, traces, wordmark, both lockups, contact sheet).
- `wordmark(text, font, out=None, weight=800, spacing=None)`: `text` set in the font file `font` and turned into paths, with no
  ``<text>`` and no need for the font afterwards. ``rsvg-convert`` draws the text big in black; the result is cropped
  to the ink and traced in mono mode. The font reaches ``rsvg-convert`` through a throwaway fontconfig file that adds a
  copy of it to the system fonts (a variable font gets the weight asked for). ``spacing=None`` is the family's tracking:
  `SPACING` (0.01 em) for Big Shoulders Display and `SPACING_OTHER` (0.12 em) for any other font; a given value always wins.

Each returns a dict (``out`` is the written path) and raises `GimgError` (``brand.*``): the ``ValueError`` of the
modules below becomes ``brand.bad_option``. Stdlib plus ``rsvg-convert`` (only for the wordmark), called without a shell.
"""
from __future__ import annotations

import math
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

from . import fsutil, matte as _matte, measure, png, trace as _trace
from .errors import GimgError

TOOL = "rsvg-convert"
TIMEOUT_S = 120
MAX_TEXT = 60
FONT_PX = 260
MAX_PIXELS = 1 << 24  # the limit of `png.read_rgba`
PAD_PX = 6
MIN_TRANSPARENT = 0.02  # a matte that frees less than this found no flat background
SPACING = 0.01  # em between letters: the family's tracking (Big Shoulders Display 800, hojas de docs/marcas/)
SPACING_OTHER = 0.12  # em between letters for any other font
SPACING_FAMILIES = ("big shoulders display", "big shoulders")
SPACING_SUFFIXES = ("sc", "variable", "thin", "extralight", "light", "regular", "medium", "semibold", "bold", "extrabold",
                    "black", "italic", "heavy", "demibold", "ultralight", "ultrabold")  # trailing words of a family name that are not a different design
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


def matte(src, out=None, tol: float = 60, soft: float = 110, border: int = 6, grow: int = 3,
          holes: bool = False) -> dict:
    """Write the transparent copy of `src` (see the module docstring); ``tol``/``soft``/``holes`` are ``t0``/``t1``/``holes`` of `remove_bg`."""
    out = _check_out(src, out or default_out(src, "-alpha", ".png"))
    width, height, rgba = png.read_rgba(src)
    try:
        res = _matte.remove_bg(width, height, rgba, t0=tol, t1=soft, border=border, grow=grow, holes=holes)
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


def _font_family(font) -> str:
    """The family of the font file `font`; a file that cannot be opened or parsed is ``brand.font_unreadable``."""
    try:
        with open(font, "rb") as fh:
            data = fh.read(64 * 1024 * 1024)
    except OSError as exc:
        raise GimgError("brand.font_unreadable", path=str(font), reason=str(exc.strerror or exc))
    return _name_table(data, font)


def default_spacing(family) -> float:
    """The tracking in em when none is given: `SPACING` for Big Shoulders Display (also the variable "Big Shoulders", the
    "SC" variants and a weight or style that a static file carries in its family name, such as "Big Shoulders Display
    ExtraBold", "Extra Bold", "Display-Bold" or "Display 800", case and spacing aside), `SPACING_OTHER` for any other family. Other cuts of the superfamily ("Text",
    "Inline Display", "Stencil") are other designs, with no sheet in `docs/marcas/`: they keep `SPACING_OTHER`."""
    words = str(family).lower().replace("-", " ").split()
    while len(words) > 1:
        if len(words) > 2 and words[-2] + words[-1] in SPACING_SUFFIXES:  # "extra bold", "semi bold"
            del words[-2:]
        elif words[-1] in SPACING_SUFFIXES or (words[-1].isdigit() and 100 <= int(words[-1]) <= 900 and int(words[-1]) % 100 == 0):
            words.pop()
        else:
            break
    return SPACING if " ".join(words) in SPACING_FAMILIES else SPACING_OTHER


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


def wordmark(text: str, font, out=None, weight: int = 800, spacing=None, title: str = "", *, _family=None) -> dict:
    """Write the SVG of `text` in `font`, as paths (see the module docstring). ``spacing`` is in em; ``None`` is the family's (`default_spacing`)."""
    text = " ".join("".join(ch for ch in str(text) if ch.isspace() or unicodedata.category(ch) != "Cc").split())
    if not text:
        raise GimgError("brand.empty_text")
    if len(text) > MAX_TEXT:
        raise GimgError("brand.text_too_long", max=MAX_TEXT)
    if not isinstance(weight, int) or not 1 <= weight <= 1000 or (spacing is not None and not -0.5 <= spacing <= 2):
        raise GimgError("brand.bad_option", reason="weight 1-1000 and spacing between -0.5 and 2 em")
    family = _family if _family is not None else _font_family(font)  # `_family`: the caller already read it (`system`)
    if spacing is None:
        spacing = default_spacing(family)
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
_FORBIDDEN = re.compile(r"<(text|image|foreignObject|script|use|style|defs|a)\b|\s(id|href|xlink:href)\s*=|\son\w+\s*=", re.I)
_TITLE = re.compile(r"<title>.*?</title>", re.S)
_PATH_D = re.compile(r'<path\b[^>]*?\sd="([^"]*)"', re.S)
_PATH_TOKEN = re.compile(r"[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
LAYOUTS = ("h", "v")
SYSTEM_FILES = ("emblema-alpha.png", "emblema.svg", "emblema-mono.svg", "wordmark.svg", "lockup-h.svg", "lockup-v.svg",
                "contactos.png")
LIGHT, DARK = "#f1e4d0", "#0f1428"
INK_ON_LIGHT, INK_ON_DARK = "#221c16", "#f1e4d0"


_TRANSLIT = {ord(k): v for k, v in {"ø": "o", "Ø": "O", "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "đ": "d", "Đ": "D",
                                    "ł": "l", "Ł": "L"}.items()}


def slugify(name: str) -> str:
    """``"Tarkor Ñandú"`` -> ``"tarkor-nandu"``: accents out, ASCII letters and digits, hyphens between; ``""`` if none."""
    plain = str(name).translate(_TRANSLIT)
    plain = unicodedata.normalize("NFKD", plain).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")


def _read_svg(path) -> dict:
    """``{"vb": (x, y, w, h), "inner": str, "root": str (the attributes of ``<svg>``), "box": (x0, y0, x1, y1)}`` of a traced SVG; ``brand.bad_svg`` if it is not one."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read(32 * 1024 * 1024)
    except (OSError, UnicodeDecodeError) as exc:
        raise GimgError("brand.bad_svg", path=str(path), reason=str(getattr(exc, "strerror", None) or exc))
    m = _SVG.match(text)
    vb = _VIEWBOX.search(m.group(1)) if m else None
    nums = None
    if vb:
        try:
            nums = [float(v) for v in vb.groups()]
        except ValueError:
            vb = None
    if not m or not vb:
        raise GimgError("brand.bad_svg", path=str(path), reason="not an SVG with a viewBox (the one of `brand trace` or `brand wordmark`)")
    if _FORBIDDEN.search(_TITLE.sub("<title></title>", text)):  # the text of a title is a name, not markup
        raise GimgError("brand.bad_svg", path=str(path), reason="it has <text>, <image>, <use>, <style>, <defs>, <script>, <foreignObject>, ids, links or handlers: only paths")
    x, y, w, h = nums
    if not all(math.isfinite(v) for v in nums) or not (w > 0 and h > 0):
        raise GimgError("brand.bad_svg", path=str(path), reason="the viewBox has no area")
    inner = _TITLE.sub("", m.group(2))
    return {"vb": (x, y, w, h), "inner": inner, "root": m.group(1), "box": _ink_box(inner) or (x, y, x + w, y + h)}


def _bez(p0, p1, p2, p3):
    """Extremes of one cubic coordinate: the ends plus the roots of its derivative inside (0, 1)."""
    vals = [p0, p3]
    a, b, c = -p0 + 3 * p1 - 3 * p2 + p3, 2 * (p0 - 2 * p1 + p2), p1 - p0
    roots = []
    if abs(a) < 1e-12:
        if abs(b) > 1e-12:
            roots.append(-c / b)
    else:
        disc = b * b - 4 * a * c
        if disc >= 0:
            sq = disc ** 0.5
            roots += [(-b + sq) / (2 * a), (-b - sq) / (2 * a)]
    for t in roots:
        if 0 < t < 1:
            u = 1 - t
            vals.append(u ** 3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3 * p3)
    return vals


def _ink_box(inner: str):
    """The box of the absolute paths in `inner` (curve extremes, not control points); ``None`` if there are other shapes,
    relative commands or a ``transform``."""
    if re.search(r"<(rect|circle|ellipse|polygon|polyline|line)\b", inner) or "transform" in inner:
        return None
    xs, ys = [], []
    for d in _PATH_D.findall(inner):
        cmd, nums, cur = None, [], (0.0, 0.0)
        toks = _PATH_TOKEN.findall(d) + ["Z"]
        for tok in toks:
            if tok.isalpha():
                if tok not in "MLCZ":
                    return None
                if cmd == "C" and nums or cmd in ("M", "L") and nums:
                    return None
                cmd, nums = tok, []
                continue
            nums.append(float(tok))
            need = 6 if cmd == "C" else 2
            if cmd in ("M", "L", "C") and len(nums) == need:
                if cmd == "C":
                    (x1, y1, x2, y2, x3, y3) = nums
                    xs += _bez(cur[0], x1, x2, x3)
                    ys += _bez(cur[1], y1, y2, y3)
                    cur = (x3, y3)
                else:
                    xs.append(nums[0])
                    ys.append(nums[1])
                    cur = (nums[0], nums[1])
                nums = []
            elif cmd is None:
                return None
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _num(v: float) -> str:
    return ("%.3f" % v).rstrip("0").rstrip(".")


def _place(piece: dict, x: float, y: float, scale: float) -> str:
    """`piece` drawn with its ink box's corner at ``(x, y)`` and scaled by `scale`."""
    x0, y0 = piece["box"][:2]
    return '<g transform="translate(%s %s) scale(%s)">%s</g>' % (_num(x - x0 * scale), _num(y - y0 * scale), _num(scale), piece["inner"])


def lockup(emblem, wordmark, out=None, layout: str = "h", cap: float = 0.45, gap: float = 0.25, width: float = 1.6,
           margin: float = 0.0, color=None, title: str = "", force: bool = False) -> dict:
    """Write one SVG with the `emblem` and the `wordmark` (both SVG files of this module), as paths only.

    The diameter D is the longer side of the emblem's ink box. ``h``: the wordmark's height is ``cap`` x D, ``gap`` x D to the
    right of the emblem, both centered vertically. ``v``: the wordmark's width is ``width`` x D, ``gap`` x D under the emblem,
    both centered horizontally. ``margin`` (x D) is free space around. ``color`` replaces ``currentColor`` in the wordmark.
    ``brand.exists`` if `out` is there and not `force`.
    """
    if layout not in LAYOUTS:
        raise GimgError("brand.bad_option", reason="layout must be one of %s (got %r)" % (", ".join(LAYOUTS), layout))
    if not (0.01 <= cap <= 5 and 0 <= gap <= 5 and 0.01 <= width <= 10 and 0 <= margin <= 2):
        raise GimgError("brand.bad_option", reason="cap 0.01-5, gap 0-5, width 0.01-10 and margin 0-2 (in emblem diameters)")
    out = str(out or "lockup-%s.svg" % layout)
    for src in (emblem, wordmark):
        _check_out(src, out)
    if os.path.lexists(out) and not force:
        raise GimgError("brand.exists", folder=os.path.dirname(os.path.abspath(out)), files=os.path.basename(out))
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
           % (_num(w), _num(h), "<title>%s</title>" % _trace.clean_title(title) if title else "", "".join(parts)))
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


SQUARE = 128
_PAINT = re.compile(r'(?<![\w:.-])(fill|stroke)="([^"]*)"')
_STYLE = re.compile(r'(?<![\w:.-])style="([^"]*)"')
_DECL = re.compile(r'(?<![\w-])(fill|stroke)(\s*:\s*)((?:[^;!]|!(?!\s*important))*)(!\s*important)?')
_NO_PAINT = ("", "none", "currentcolor", "inherit", "transparent")


def _paints(value: str) -> bool:
    """False for no paint, ``transparent`` and any color with alpha 0 (``rgba(…, 0)``, ``#0000``, ``hsla(…, 0)``)."""
    v = value.strip().lower()
    return v not in ("", "none", "transparent") and not _invisible(_norm_color(v))


def _invisible(norm: str) -> bool:
    return bool(re.fullmatch(r"#[0-9a-f]{6}00", norm))


def _square_ink(inner: str, ink: str) -> str:
    """`inner` with every fill and stroke that paints (not ``none``) turned into `ink`, as attributes and as declarations
    of a ``style`` attribute; unpainted paths inherit it."""
    def decl(m):
        if not _paints(m.group(3)):
            return m.group(0)
        important = m.group(4)  # `!important` stays, with the space it had before it
        return "%s%s%s%s" % (m.group(1), m.group(2), ink, (m.group(3)[len(m.group(3).rstrip()):] + important) if important else "")

    out = _STYLE.sub(lambda m: 'style="%s"' % _DECL.sub(decl, m.group(1)), inner)
    out = _PAINT.sub(lambda m: m.group(0) if not _paints(m.group(2)) else '%s="%s"' % (m.group(1), ink), out)
    return '<g fill="%s">%s</g>' % (ink, out)


_NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "lime": "#00ff00", "blue": "#0000ff", "yellow": "#ffff00",
          "cyan": "#00ffff", "aqua": "#00ffff", "magenta": "#ff00ff", "fuchsia": "#ff00ff", "gray": "#808080", "grey": "#808080",
          "silver": "#c0c0c0", "maroon": "#800000", "olive": "#808000", "green": "#008000", "purple": "#800080", "teal": "#008080",
          "navy": "#000080", "orange": "#ffa500"}
_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)"
_RGB = re.compile(r"rgba?\(\s*(%s)(%%?)\s*[,\s]\s*(%s)(%%?)\s*[,\s]\s*(%s)(%%?)\s*(?:[,/]\s*(%s)(%%?)\s*)?\)" % ((_NUM,) * 4))
_HSL = re.compile(r"hsla?\(\s*(%s)(?:deg)?\s*[,\s]\s*(%s)%%\s*[,\s]\s*(%s)%%\s*(?:[,/]\s*(%s)(%%?)\s*)?\)" % ((_NUM,) * 4))
_SHAPE = re.compile(r"<(path|rect|circle|ellipse|polygon|polyline|line)\b([^>]*)>")
_TAG = re.compile(r"<(/?)(g|path|rect|circle|ellipse|polygon|polyline|line)\b([^>]*)>")
_CLASS = re.compile(r'(?<![\w:.-])class\s*=')


def _has_fill(attrs: str) -> bool:
    return (any(m.group(1) == "fill" for m in _PAINT.finditer(attrs))
            or any(d.group(1) == "fill" for st in _STYLE.finditer(attrs) for d in _DECL.finditer(st.group(1))))


def _hex_alpha(rgb, alpha) -> str:
    """``#rrggbb``, or ``#rrggbbaa`` when `alpha` (0-1) is not fully opaque."""
    a = round(min(max(alpha, 0.0), 1.0) * 255)
    return "#%02x%02x%02x" % tuple(rgb) + ("" if a == 255 else "%02x" % a)


def _alpha_of(num, pct) -> float:
    return 1.0 if num is None else float(num) / (100 if pct else 1)


def _norm_color(value: str) -> str:
    """`value` as lowercase ``#rrggbb`` (``#rrggbbaa`` if it is not opaque) when it is a hex color (3, 4, 6 or 8 digits), a
    basic CSS color name, ``rgb()`` / ``rgba()`` or ``hsl()`` / ``hsla()``; anything else, lowercased."""
    v = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3,4}", v):
        v = "#" + "".join(c * 2 for c in v[1:])
    if re.fullmatch(r"#[0-9a-f]{8}", v):
        return v[:7] if v.endswith("ff") else v
    rgb = _RGB.fullmatch(v)
    if rgb:
        g = rgb.groups()
        chans = [float(g[i]) * (2.55 if g[i + 1] else 1) for i in (0, 2, 4)]
        if all(math.isfinite(c) and -0.5 <= c < 255.5 for c in chans):
            return _hex_alpha([round(min(max(c, 0), 255)) for c in chans], _alpha_of(g[6], g[7]))
    hsl = _HSL.fullmatch(v)
    if hsl:
        if not math.isfinite(float(hsl.group(1))):
            return v
        h, sat, light = float(hsl.group(1)) % 360, min(max(float(hsl.group(2)), 0), 100) / 100, min(max(float(hsl.group(3)), 0), 100) / 100
        c = (1 - abs(2 * light - 1)) * sat
        x = c * (1 - abs((h / 60) % 2 - 1))
        r, g2, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
        m = light - c / 2
        return _hex_alpha([round((n + m) * 255) for n in (r, g2, b)], _alpha_of(hsl.group(4), hsl.group(5)))
    return _NAMED.get(v, v)


def _paint_colors(inner: str, root: str = "") -> set:
    """The distinct colors that `inner` paints with (attributes and ``style`` declarations), as `_norm_color` writes them;
    ``none``, ``currentColor`` and strokes that are not there do not count, but a shape with no ``fill`` at all paints the
    default black (unless a ``<g>`` or the root (`root`: the attributes of ``<svg>``) sets a fill, or it has a ``class`` or the
    drawing a ``<style>``: then it is not counted); a ``<line>`` has no area, so it only paints by its stroke."""
    found = [m.group(2) for m in _PAINT.finditer(inner + " " + root)]
    for st in _STYLE.finditer(inner + " " + root):
        found += [m.group(3) for m in _DECL.finditer(st.group(1))]
    colors = {_norm_color(v)[:7] if re.fullmatch(r"#[0-9a-f]{8}", _norm_color(v)) else _norm_color(v)  # alpha aside: same color
              for v in found if v.strip().lower() not in _NO_PAINT and not _invisible(_norm_color(v))}
    if "<style" not in inner.lower():  # with a stylesheet the color may come from CSS: not counted
        groups = [_has_fill(root)]  # one flag per open <g> (the first, the root): does it set a fill its shapes inherit?
        for m in _TAG.finditer(inner):
            closing, tag, attrs = m.groups()
            if tag == "g":
                if closing:
                    if groups:
                        groups.pop()
                elif not attrs.rstrip().endswith("/"):
                    groups.append(_has_fill(attrs))
            elif not closing and tag != "line" and not any(groups) and not _has_fill(attrs) and not _CLASS.search(attrs):
                colors.add("#000000")
    return colors


def square(drawing, out=None, fill=None, ink=None, chamfer: int = 28, pad: int = 24, pngs=None, force: bool = False) -> dict:
    """The family symbol: a flat `fill` square of 128 with a 45-degree `chamfer` cut off its top right corner and the SVG
    `drawing` (paths only, as `trace` / `wordmark` make them) fitted inside `pad`, all of it in the one color `ink`
    (``fill`` / ``stroke`` attributes and ``style`` declarations alike; ``flattened`` in the result counts the paint colors it had, if more than one).

    `pngs` are sides in pixels: each also gets ``<out stem>-<side>.png`` (needs rsvg-convert). Returns the files, the colors
    and the WCAG contrast of `ink` on `fill`; `brand.exists` if a file is there and not `force`."""
    if isinstance(chamfer, bool) or not isinstance(chamfer, (int, float)) or not (0 <= chamfer <= 64):
        raise GimgError("brand.bad_square", reason="chamfer must be a number from 0 to 64 (got %r)" % (chamfer,))
    if isinstance(pad, bool) or not isinstance(pad, (int, float)) or not (0 <= pad <= 48):
        raise GimgError("brand.bad_square", reason="pad must be a number from 0 to 48 (got %r)" % (pad,))
    colors = []
    for name, value in (("fill", fill), ("ink", ink)):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(value or "")):
            raise GimgError("brand.bad_square", reason="%s must be #rrggbb (got %r)" % (name, value))
        colors.append(str(value).lower())
    fill, ink = colors
    sides = []
    for side in (pngs or ()):
        if isinstance(side, bool) or not isinstance(side, int) or not (1 <= side <= 8192):
            raise GimgError("brand.bad_square", reason="a PNG side is a whole number from 1 to 8192 (got %r)" % (side,))
        if side not in sides:
            sides.append(side)
    out = _check_out(drawing, out or default_out(drawing, "-square", ".svg"))
    files = {side: str(Path(out).with_name("%s-%d.png" % (Path(out).stem, side))) for side in sides}
    clash = [f for f in (out, *files.values()) if os.path.exists(f)]
    if clash and not force:
        raise GimgError("brand.exists", folder=os.path.dirname(os.path.abspath(out)), files=", ".join(os.path.basename(f) for f in clash))
    piece = _read_svg(drawing)
    x0, y0, x1, y1 = piece["box"]
    bw, bh, room = x1 - x0, y1 - y0, SQUARE - 2 * pad
    if bw <= 0 or bh <= 0:
        raise GimgError("brand.bad_svg", path=str(drawing), reason="the drawing has no ink")
    if room <= 0:
        raise GimgError("brand.bad_square", reason="pad leaves no room for the drawing")
    k = min(room / bw, room / bh)
    flattened = len(_paint_colors(piece["inner"], piece["root"]))
    art = _place(dict(piece, inner=_square_ink(piece["inner"], ink)), (SQUARE - bw * k) / 2, (SQUARE - bh * k) / 2, k)
    d = "M0 0 H%s L%d %s V%d H0 Z" % (_num(SQUARE - chamfer), SQUARE, _num(chamfer), SQUARE)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img"><path fill="%s" d="%s"/>%s</svg>\n'
           % (SQUARE, SQUARE, fill, d, art))
    if sides and shutil.which(TOOL) is None:
        raise GimgError("brand.tool_missing", tool=TOOL)
    # All or nothing: the SVG and every PNG are made under temporary names next to their targets and only renamed at the end.
    staged = {}  # temporary path -> final path
    try:
        folder = os.path.dirname(os.path.abspath(out))
        try:
            os.makedirs(folder, exist_ok=True)
            fd, tmp_svg = tempfile.mkstemp(dir=folder, prefix=".brand-", suffix=".svg.tmp")
        except OSError as exc:
            raise GimgError("brand.write_failed", path=str(out), reason=str(exc.strerror or exc))
        staged[tmp_svg] = out
        try:
            fsutil.honour_umask(fd)
            with os.fdopen(fd, "wb") as fh:
                fh.write(svg.encode("utf-8"))
        except OSError as exc:
            raise GimgError("brand.write_failed", path=str(out), reason=str(exc.strerror or exc))
        for side, path in files.items():
            try:
                fd_png, tmp_png = tempfile.mkstemp(dir=folder, prefix=".brand-", suffix=".png.tmp")
                fsutil.honour_umask(fd_png)
                os.close(fd_png)
            except OSError as exc:
                raise GimgError("brand.write_failed", path=str(path), reason=str(exc.strerror or exc))
            staged[tmp_png] = path
            _rsvg([TOOL, "-f", "png", "-w", str(side), "-h", str(side), "-o", tmp_png, tmp_svg], dict(os.environ))
            if os.path.getsize(tmp_png) == 0:
                raise GimgError("brand.tool_failed", tool=TOOL, reason="no output")
        _commit(staged)
    finally:
        for tmp in staged:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    contrast = measure.contrast_ratio(measure.luminance(measure.parse_hex(ink)), measure.luminance(measure.parse_hex(fill)))
    res = {"out": out, "pngs": list(files.values()), "fill": fill, "ink": ink, "contrast": round(contrast, 2)}
    if flattened > 1:
        res["flattened"] = flattened  # the drawing had this many paint colors: all of them are now the ink
    return res


def _commit(staged: dict) -> None:
    """Move every temporary onto its final path, all or nothing as far as practical: an existing target is first moved
    to a backup; if any rename fails, the new files are removed and the backups put back (``brand.write_failed``)."""
    backups, placed = {}, []  # final path -> backup path; final paths already holding the new file
    try:
        for tmp, final in staged.items():
            if os.path.lexists(final):
                fd, backup = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(final)), prefix=".brand-", suffix=".bak")
                os.close(fd)
                backups[final] = backup
                os.replace(final, backup)
            os.replace(tmp, final)
            placed.append(final)
    except OSError as exc:
        for final in placed:
            try:
                os.unlink(final)
            except OSError:
                pass
        for final, backup in backups.items():
            try:
                os.replace(backup, final)
            except OSError:
                pass
        raise GimgError("brand.write_failed", path=str(final), reason=str(exc.strerror or exc))
    finally:
        for backup in backups.values():
            try:
                os.unlink(backup)
            except OSError:
                pass


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


def contact_sheet(files: dict, tmp: str) -> tuple:
    """Draw ``files["contactos.png"]`` from the five SVGs of `files` (keys of `SYSTEM_FILES`); `tmp` is scratch space.
    Returns the size of the sheet; ``brand.tool_missing`` / ``brand.tool_failed`` / ``brand.bad_svg`` as `system`."""
    if shutil.which(TOOL) is None:
        raise GimgError("brand.tool_missing", tool=TOOL)
    pieces = {"emblem": _read_svg(files["emblema.svg"]), "mono": _read_svg(files["emblema-mono.svg"]),
              "wordmark": _read_svg(files["wordmark.svg"]), "lockup_h": _read_svg(files["lockup-h.svg"]),
              "lockup_v": _read_svg(files["lockup-v.svg"])}
    sheet_svg, size = _contact_svg(pieces)
    sheet_src = os.path.join(tmp, "contactos.svg")
    with open(sheet_src, "w", encoding="utf-8") as fh:
        fh.write(sheet_svg)
    if os.path.exists(files["contactos.png"]):
        os.unlink(files["contactos.png"])
    _rsvg([TOOL, "-o", files["contactos.png"], sheet_src], dict(os.environ))
    if not os.path.exists(files["contactos.png"]):
        raise GimgError("brand.tool_failed", tool=TOOL, reason="no output")
    return size


def targets_of(slug: str, out_dir) -> dict:
    """``{key: path}`` of the seven files of the system `slug` in `out_dir`."""
    return {key: os.path.join(str(out_dir), "%s-%s" % (slug, key)) for key in SYSTEM_FILES}


def check_targets(targets: dict, out_dir, force: bool = False, src=None) -> list:
    """Refuse a `out_dir` that is no folder or a target that is one (``brand.write_failed``), and files already there
    unless `force` (``brand.exists``); returns the names that will be overwritten."""
    if src is not None:
        for path in targets.values():
            _check_out(src, path)
    if os.path.lexists(str(out_dir)) and not os.path.isdir(str(out_dir)):
        raise GimgError("brand.write_failed", path=str(out_dir), reason="not a folder")
    for path in targets.values():
        if os.path.isdir(path):
            raise GimgError("brand.write_failed", path=path, reason="it is a folder")
    clash = [os.path.basename(p) for p in targets.values() if os.path.lexists(p)]
    if clash and not force:
        raise GimgError("brand.exists", folder=str(out_dir), files=", ".join(clash))
    return clash


def system(src, name: str, font, out_dir, weight: int = 800, spacing=None, palette=None, colors=None, text=None,
           cap: float = 0.45, gap: float = 0.25, width: float = 1.6, force: bool = False, holes: bool = False,
           margin: float = 0.0, mono: bool = False) -> dict:
    """The logo system of `name` from the emblem PNG `src`, in `out_dir`: ``<slug>-emblema-alpha.png``, ``-emblema.svg``,
    ``-emblema-mono.svg``, ``-wordmark.svg``, ``-lockup-h.svg``, ``-lockup-v.svg`` and ``-contactos.png`` (see `SYSTEM_FILES`).

    Everything is built in a throwaway folder and copied in at the end, so a failure while working leaves `out_dir` as it
    was (only an I/O failure in the final copy can leave some files); a file already there is ``brand.exists`` unless `force`. The wordmark text is `text`, else `name` in capitals.
    The lockups take ``margin`` (see `lockup`) and, with `mono`, the one-ink emblem instead of the color one: the whole
    lockup in ``currentColor``, as the family's sheets ask.
    """
    t0 = time.monotonic()
    slug = slugify(name)
    if not str(name).strip():
        raise GimgError("brand.empty_text")
    if not slug:
        raise GimgError("brand.bad_name", name=str(name))
    targets = targets_of(slug, out_dir)
    clash = check_targets(targets, out_dir, force, src)
    if palette and colors is not None:
        raise GimgError("brand.bad_option", reason="--palette and --colors exclude each other")
    line = text if text else str(name).strip().upper()
    if not str(line).strip():
        raise GimgError("brand.empty_text")
    if len(line) > MAX_TEXT:
        raise GimgError("brand.text_too_long", max=MAX_TEXT)
    if not isinstance(weight, int) or not 1 <= weight <= 1000 or (spacing is not None and not -0.5 <= spacing <= 2):
        raise GimgError("brand.bad_option", reason="weight 1-1000 and spacing between -0.5 and 2 em")
    if not 0 <= margin <= 2:
        raise GimgError("brand.bad_option", reason="margin 0-2 (in emblem diameters)")
    if len(os.path.basename(next(iter(targets.values()))).encode("utf-8")) > 255:
        raise GimgError("brand.bad_name", name=str(name))
    family = _font_family(font)  # an unreadable font fails here, before the matte and the traces
    if spacing is None:
        spacing = default_spacing(family)
    if shutil.which(TOOL) is None:  # after the caller's own mistakes: those are reported with or without the tool
        raise GimgError("brand.tool_missing", tool=TOOL)
    with tempfile.TemporaryDirectory(prefix="gimg-brand-") as tmp:
        t = {key: os.path.join(tmp, key) for key in SYSTEM_FILES}
        m = matte(src, t["emblema-alpha.png"], holes=holes)
        if m["transparent"] < MIN_TRANSPARENT:
            raise GimgError("brand.no_matte", path=str(src), transparent=round(m["transparent"] * 100, 1))
        title = str(name).strip()
        color = trace(t["emblema-alpha.png"], t["emblema.svg"], "color", palette, colors, title=title)
        try:
            one_ink = trace(t["emblema-alpha.png"], t["emblema-mono.svg"], "mono", title=title)
        except GimgError as exc:  # no ink left: only the lockups that use it stop; otherwise its silhouette
            if mono or exc.code != "brand.bad_option":
                raise
            one_ink = trace(t["emblema-alpha.png"], t["emblema-mono.svg"], "silhouette", title=title)
        word = wordmark(line, font, t["wordmark.svg"], weight, spacing, title=title, _family=family)
        emblem = t["emblema-mono.svg" if mono else "emblema.svg"]
        lh = lockup(emblem, t["wordmark.svg"], t["lockup-h.svg"], "h", cap, gap, width, margin, title=title, force=True)
        lv = lockup(emblem, t["wordmark.svg"], t["lockup-v.svg"], "v", cap, gap, width, margin, title=title, force=True)
        sheet_size = contact_sheet(t, tmp)
        for key in SYSTEM_FILES:
            with open(t[key], "rb") as fh:
                _write(targets[key], fh.read())
    files = {key: targets[key] for key in SYSTEM_FILES}
    return {"src": str(src), "name": str(name).strip(), "slug": slug, "out_dir": str(out_dir), "files": files, "spacing": spacing,
            "paths": {"emblem": color["paths"], "mono": one_ink["paths"], "wordmark": word["paths"], "lockup_h": lh["paths"],
                      "lockup_v": lv["paths"]},
            "contact_size": list(sheet_size), "overwritten": sorted(clash), "seconds": round(time.monotonic() - t0, 1)}


__all__ = ["contact_sheet", "targets_of", "check_targets", "matte", "trace", "wordmark", "lockup", "system", "slugify", "parse_palette", "default_out", "MODES", "SPACING", "SPACING_OTHER", "default_spacing", "LAYOUTS",
           "SYSTEM_FILES", "TOOL"]
