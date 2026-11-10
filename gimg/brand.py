"""The brand process (D37), small enough for the command line and the interface to share: matte, trace, wordmark.

- `matte(src, out=None, **opts)`: the PNG `src` with its flat background made transparent (`matte.remove_bg`). The default
  `out` is next to `src`, with ``-alpha`` before the extension; the original is never written.
- `trace(src, out=None, mode="color", ...)`: the PNG `src` as an SVG (`trace.to_svg`); ``matte=True`` removes the
  background first. ``mode`` is ``color``, ``mono`` or ``silhouette`` (``silueta`` also works).
- `wordmark(text, font, out=None, weight=800, spacing=0.12)`: `text` set in the font file `font` and turned into paths, with no
  ``<text>`` and no need for the font afterwards. ``rsvg-convert`` draws the text big in black; the result is cropped
  to the ink and traced in mono mode. The font reaches ``rsvg-convert`` through a throwaway fontconfig file that adds a
  copy of it to the system fonts (a variable font gets the weight asked for).

Each returns a dict (``out`` is the written path) and raises `GimgError` (``brand.*``): the ``ValueError`` of the
modules below becomes ``brand.bad_option``. Stdlib plus ``rsvg-convert`` (only for the wordmark), called without a shell.
"""
from __future__ import annotations

import os
import shutil
import struct
import subprocess
import tempfile
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


__all__ = ["matte", "trace", "wordmark", "parse_palette", "default_out", "MODES", "TOOL"]
