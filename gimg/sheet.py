"""Contact sheet (`gimg sheet`): N images in one PNG, each with its number and file name, so an agent reviews a round
by reading one image instead of N.

Stdlib plus ``ffmpeg``/``ffprobe``/``rsvg-convert``; the inputs are only read. Every path travels as an argument (never
inside a filter string) and ffmpeg reads inputs as ``file:<abs path>``, so spaces, quotes, ``:`` or a leading ``-`` in
a name are harmless.

- **Labels:** the ffmpeg of the project machine may lack ``drawtext`` (it does on the Steam Deck), so each label is a small
  SVG rendered by ``rsvg-convert`` (already a dependency of ``compose``; the font comes from fontconfig, ``sans-serif``).
  The text is XML-escaped and, if it does not fit, cut with an ellipsis at the start (the end of a name is what differs).
- **Layout:** every cell is ``width`` px wide (the image keeps its proportion) with the label strip on top; the cells of
  a row are padded to the tallest one. One ``xstack`` with numeric positions puts them in ``columns`` columns.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from xml.sax.saxutils import escape

from . import measure
from .errors import GimgError

DEFAULT_COLUMNS = 2
DEFAULT_WIDTH = 640
MIN_WIDTH, MAX_WIDTH = 64, 2000
MAX_IMAGES = 64
LABEL_H = 32
FONT_PX = 20
GAP = 8
BACKGROUND = "0x202020"
TOOLS = ("ffmpeg", "ffprobe", "rsvg-convert")


def _label_text(index: int, path, width: int) -> str:
    text = "%d  %s" % (index, os.path.basename(str(path)))
    room = max(4, int((width - 16) / (FONT_PX * 0.62)))
    return text if len(text) <= room else "…" + text[-(room - 1):]


def _label_svg(text: str, width: int) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">'
            '<rect width="100%%" height="100%%" fill="#202020"/>'
            '<text x="8" y="%d" font-family="DejaVu Sans, sans-serif" font-size="%d" fill="#ffffff">%s</text></svg>'
            % (width, LABEL_H, LABEL_H - 10, FONT_PX, escape(text)))


def layout(sizes, columns: int, width: int) -> dict:
    """Pure geometry: ``{"heights", "positions", "size"}`` for images of `sizes` ``[(w, h)]`` in `columns` columns."""
    heights = [max(1, round(h * width / w)) for w, h in sizes]
    rows = [heights[i:i + columns] for i in range(0, len(heights), columns)]
    row_h = [LABEL_H + max(r) + GAP for r in rows]
    positions = []
    for i in range(len(sizes)):
        positions.append(((i % columns) * (width + GAP), sum(row_h[:i // columns])))
    return {"heights": heights, "positions": positions, "row_heights": row_h,
            "size": (min(columns, len(sizes)) * (width + GAP), sum(row_h))}


def _graph(sizes, columns: int, width: int) -> tuple:
    n = len(sizes)
    geo = layout(sizes, columns, width)
    parts = []
    for i, h in enumerate(geo["heights"]):
        cell_h = geo["row_heights"][i // columns]
        parts.append("[%d:v]scale=%d:%d:flags=lanczos,format=rgb24[i%d];[%d:v]format=rgb24[l%d];"
                     "[l%d][i%d]vstack=inputs=2,pad=%d:%d:0:0:color=%s[c%d]"
                     % (i, width, h, i, n + i, i, i, i, width + GAP, cell_h, BACKGROUND, i))
    inputs = "".join("[c%d]" % i for i in range(n))
    layout_arg = "|".join("%d_%d" % pos for pos in geo["positions"])
    if n == 1:
        parts.append("[c0]null[out]")
    else:
        parts.append("%sxstack=inputs=%d:layout=%s:fill=%s[out]" % (inputs, n, layout_arg, BACKGROUND))
    return ";".join(parts), geo["size"]


def sheet(images, out, columns: int = DEFAULT_COLUMNS, width: int = DEFAULT_WIDTH) -> dict:
    """Write the contact sheet of `images` to `out` and return ``{"out", "size", "columns", "width", "images"}``."""
    images = [str(p) for p in images]
    if not images:
        raise GimgError("sheet.no_images")
    if len(images) > MAX_IMAGES:
        raise GimgError("sheet.too_many", count=len(images), max=MAX_IMAGES)
    if columns < 1:
        raise GimgError("sheet.bad_columns", value=columns)
    if not MIN_WIDTH <= width <= MAX_WIDTH:
        raise GimgError("sheet.bad_width", value=width, min=MIN_WIDTH, max=MAX_WIDTH)
    out = str(out)
    for path in images:
        if not os.path.isfile(path):
            raise GimgError("sheet.unreadable", path=path)
    for path in images:
        if os.path.exists(out) and os.path.samefile(path, out):
            raise GimgError("sheet.out_is_input", path=out)
    for tool in TOOLS:
        if shutil.which(tool) is None:
            raise GimgError("sheet.tool_missing", tool=tool)
    columns = min(columns, len(images))
    sizes = [measure.image_size(p, "sheet") for p in images]
    out_dir = os.path.dirname(os.path.abspath(out))
    os.makedirs(out_dir, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gimg-sheet-") as tmp:
        labels = []
        for i, path in enumerate(images, 1):
            svg, png = os.path.join(tmp, "l%d.svg" % i), os.path.join(tmp, "l%d.png" % i)
            with open(svg, "w", encoding="utf-8") as fh:
                fh.write(_label_svg(_label_text(i, path, width), width))
            measure._run(["rsvg-convert", "-w", str(width), "-h", str(LABEL_H), "-o", png, svg], "rsvg-convert", "sheet")
            labels.append(png)
        graph, size = _graph(sizes, columns, width)
        argv = ["ffmpeg", "-v", "error", "-nostdin", "-y"]
        for path in images:
            argv += ["-i", measure._input(path)]
        for png in labels:
            argv += ["-i", "file:" + png]
        tmp_out = os.path.join(tmp, "sheet.png")
        argv += ["-filter_complex", graph, "-map", "[out]", "-frames:v", "1", tmp_out]
        measure._run(argv, "ffmpeg", "sheet")
        if not os.path.isfile(tmp_out):
            raise GimgError("sheet.tool_failed", tool="ffmpeg", reason="no output")
        shutil.move(tmp_out, out)
    return {"out": out, "size": list(size), "columns": columns, "width": width, "images": images}
