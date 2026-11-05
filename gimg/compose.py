"""Composition (F2.8, D28): a raw image plus an SVG template become the delivered image.

The pieces, all stdlib and all pure except `render`:

- `target_size` / `plan_for`: the delivered size of a profile and whether there is anything to do (a profile with
  neither ``compose`` nor ``targetWidth``/``targetHeight`` is left alone, and so is one whose target is the raw size).
- `fit_geometry`: the integer scale and crop (``cover``) or pad (``contain``) that take a raw image to the target.
- `substitute` / `xml_escape`: ``{{field}}`` holes of the template, filled in one pass with escaped text.
- `resolve_assets`: the template and the logo, behind the D25 guard (`paths.inside`) and a size limit.
- `rsvg_argv` / `ffmpeg_argv` / `_run`: the two tools, called without a shell, with a time limit.
- `render`: the whole thing; the substituted SVG is written to an empty temporary folder so ``rsvg-convert`` cannot
  read anything else from the disk (the logo travels inside the SVG as a ``data:`` URI, like `examples/pilot/componer.py`).

Every failure is a ``GimgError`` whose code starts with ``compose.``; a path that fails the guard keeps its ``path.*`` code.
The raw image is never modified. The ``gimg`` text chunk of the raw image is carried over to the result with a
``compose`` key (what was composed), so a delivered file still says how it was made.
"""
from __future__ import annotations

import base64
import copy
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import delivery, fsutil, i18n, limits, log, measure, orders, paths, png, projects
from .errors import GimgError

TIMEOUT_S = 120
MAX_SVG_BYTES = 5_000_000
FITS = ("cover", "contain")
COMPOSE_TMP_PREFIX = ".compose-"
RECOMPOSE_TMP_PREFIX = ".compose-c%d-"  # `recompose`: never the worker's ``.compose-q<entry>-`` (`queue._clean_pending`)

_HOLE = re.compile(r"\{\{([A-Za-z][A-Za-z0-9]*)\}\}")
# What XML 1.0 cannot carry at all (C0 controls but tab, LF and CR; the two non-characters) plus lone surrogates
# (a JSON "\ud800" is a valid Python str that UTF-8 cannot encode).
_XML_FORBIDDEN = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff￾￿]")
_ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;"}


def _has_target(profile_cfg) -> bool:
    return "targetWidth" in profile_cfg and "targetHeight" in profile_cfg


def target_size(profile_cfg) -> tuple:
    """The delivered ``(width, height)``: ``targetWidth``/``targetHeight``, else the generation size."""
    if _has_target(profile_cfg):
        return profile_cfg["targetWidth"], profile_cfg["targetHeight"]
    return profile_cfg["width"], profile_cfg["height"]


def _fit_of(compose_cfg) -> str:
    return (compose_cfg or {}).get("fit", "cover")


def plan_for(profile_cfg, raw_w, raw_h):
    """What composing a raw ``raw_w``x``raw_h`` image of this profile involves, or None if nothing.

    None when the profile has no ``compose`` and either no target or a target equal to the raw size. Otherwise a dict
    with ``fit``, ``targetWidth``, ``targetHeight`` and, if the profile has them, ``template`` and ``logo`` (the paths
    as written in the configuration)."""
    compose_cfg = profile_cfg.get("compose")
    width, height = target_size(profile_cfg)
    if compose_cfg is None and (not _has_target(profile_cfg) or (width, height) == (raw_w, raw_h)):
        return None
    plan = {"fit": _fit_of(compose_cfg), "targetWidth": width, "targetHeight": height}
    for key in ("template", "logo"):
        if compose_cfg and compose_cfg.get(key):
            plan[key] = compose_cfg[key]
    return plan


DEFAULT_TEMPLATE = "default"  # reserved id: the template of ``compose`` itself
_TEMPLATE_KEYS = ("template", "logo", "fields", "zone", "textColor", "templateRoot")  # templateRoot: local folder (F4c)


def _template_ids(compose_cfg) -> list:
    """``["default"]`` plus the ids of ``compose.templates``, sorted."""
    return [DEFAULT_TEMPLATE] + sorted(compose_cfg.get("templates") or {}) if compose_cfg else []


def effective(compose_cfg, template_id=None) -> dict:
    """The ``compose`` configuration of template `template_id` (``None`` or ``"default"``: the profile's own).

    The result is ``compose_cfg`` without ``templates``; an entry of ``templates`` replaces ``template`` and, if it has
    them, ``logo`` and ``fields`` (otherwise inherited); ``zone`` and ``textColor`` are the entry's own (a different
    template reserves a different zone). ``fit`` and ``fonts`` are the profile's. An id that does not exist, or a
    profile without ``compose``, raises ``compose.template_unknown`` (``template``, ``allowed``)."""
    if template_id is not None and not isinstance(template_id, str):
        raise GimgError("compose.template_unknown", template=str(template_id), allowed=", ".join(_template_ids(compose_cfg)))
    base = {k: v for k, v in (compose_cfg or {}).items() if k != "templates"}
    if template_id in (None, DEFAULT_TEMPLATE):
        if compose_cfg is None and template_id is not None:
            raise GimgError("compose.template_unknown", template=template_id, allowed="")
        return base
    entry = ((compose_cfg or {}).get("templates") or {}).get(template_id)
    if entry is None:
        raise GimgError("compose.template_unknown", template=template_id, allowed=", ".join(_template_ids(compose_cfg)))
    out = {k: v for k, v in base.items() if k not in ("zone", "textColor")}
    out.update({k: v for k, v in entry.items() if k in _TEMPLATE_KEYS})
    return out


def templates_of(profile_cfg) -> list:
    """The templates a profile offers, ``default`` first and then by id: ``{"id", "template", "logo", "fields",
    "zone"?, "textColor"?, "source", "default"}`` (``logo`` is ``None`` if there is none; ``source`` is ``config``,
    ``project`` or ``local``: where the template is declared, see `merged_profile`). ``[]`` for a profile without
    ``compose``."""
    compose_cfg = profile_cfg.get("compose")
    if not compose_cfg:
        return []
    items = []
    for tid in _template_ids(compose_cfg):
        cfg = effective(compose_cfg, tid)
        item = {"id": tid, "template": cfg["template"], "logo": cfg.get("logo"), "fields": list(cfg.get("fields", []))}
        for key in ("zone", "textColor"):
            if key in cfg:
                item[key] = cfg[key]
        entry = (compose_cfg.get("templates") or {}).get(tid) or {}
        item["source"] = entry.get("source", "config")
        item["default"] = tid == DEFAULT_TEMPLATE
        items.append(item)
    return items


# --- templates from folders (F4c.2, D40) ---
_TEMPLATE_ID = re.compile(r"(?!default$)[a-z0-9][a-z0-9-]{0,39}")
_FIELD_NAME = re.compile(r"(?!logo$)[a-z][a-zA-Z0-9]*")
_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
SOURCES = ("config", "project", "local")
MAX_FOLDER_TEMPLATES = 100
MAX_SIDECAR_BYTES = 65536


def local_templates_dir(project, profile) -> Path:
    """``<data>/projects/<project>/templates/<profile>``, behind the D25 guard. Path only; nothing is created."""
    return paths.inside(paths.project_data_dir(project), "templates/" + profile)


def project_templates_dir(root, compose_cfg, profile):
    """``<root>/<compose.templatesDir>/<profile>`` (guarded), or ``None`` if the profile declares no ``templatesDir``."""
    rel = (compose_cfg or {}).get("templatesDir")
    if not rel:
        return None
    return paths.inside(root, paths.check_relative(rel).rstrip("/") + "/" + profile)


def _sidecar(path: Path) -> dict:
    """The inheritable keys of ``<name>.json`` that are valid (anything else is ignored); ``{}`` if unreadable."""
    try:
        if path.stat().st_size > MAX_SIDECAR_BYTES:
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    if not isinstance(data, dict):
        return out
    logo = data.get("logo")
    if isinstance(logo, str) and logo.endswith(".svg"):
        try:
            out["logo"] = paths.check_relative(logo)
        except GimgError:
            pass
    fields = data.get("fields")
    if isinstance(fields, list) and len(fields) <= 10 and all(isinstance(f, str) and _FIELD_NAME.fullmatch(f) for f in fields):
        out["fields"] = list(fields)
    zone = data.get("zone")
    if isinstance(zone, dict) and sorted(zone) == ["h", "w", "x", "y"] and all(
            type(v) is int and 0 <= v <= 8192 for v in zone.values()) and zone["w"] >= 1 and zone["h"] >= 1:
        out["zone"] = {k: zone[k] for k in ("x", "y", "w", "h")}
    color = data.get("textColor")
    if isinstance(color, str) and _HEX_COLOR.fullmatch(color):
        out["textColor"] = color
    return out


def _folder_entries(folder, source, template_for, extra=None) -> list:
    """``[{"id", "source", "entry"}]`` for the ``*.svg`` files of `folder` whose stem is a valid template id."""
    out = []
    try:
        names = sorted(p for p in Path(folder).iterdir() if p.suffix == ".svg" and p.is_file())
    except OSError:
        return out
    for path in names[:MAX_FOLDER_TEMPLATES]:
        if not _TEMPLATE_ID.fullmatch(path.stem):
            continue
        entry = dict(_sidecar(path.with_suffix(".json")), template=template_for(path.stem), source=source, **(extra or {}))
        out.append({"id": path.stem, "source": source, "entry": entry})
    return out


def template_sources(proj, profile) -> list:
    """Every template declared for `profile` of the loaded project `proj`, repeated ids included, in the order of
    precedence: ``compose.templates`` (``config``), ``<templatesDir>/<profile>/`` (``project``) and the local folder
    (``local``). ``[{"id", "source", "entry"}]``; nothing for a profile without ``compose``."""
    cfg = (proj["config"]["profiles"].get(profile) or {}).get("compose")
    if not cfg:
        return []
    out = [{"id": tid, "source": "config", "entry": dict(entry, source="config")}
           for tid, entry in sorted((cfg.get("templates") or {}).items())]
    try:
        folder = project_templates_dir(proj["root"], cfg, profile)
    except GimgError:
        folder = None
    if folder is not None:
        prefix = paths.check_relative(cfg["templatesDir"]).rstrip("/") + "/" + profile + "/"
        out += _folder_entries(folder, "project", lambda stem: prefix + stem + ".svg")
    try:
        local = local_templates_dir(proj["name"], profile)
    except GimgError:
        local = None
    if local is not None:
        out += _folder_entries(local, "local", lambda stem: stem + ".svg", {"templateRoot": local})
    return out


def merged_profile(proj, profile):
    """The profile `profile` of the loaded project `proj` (``{"name", "root", "config"}``) with the templates of its
    three sources in ``compose.templates`` (the first source wins an id; `templates_of` says each ``source``). The
    profile itself if it has no ``compose``, ``None`` if it does not exist. Everything that composes takes the profile
    from here so a folder template is one more template."""
    cfg = proj["config"]["profiles"].get(profile)
    if cfg is None or not cfg.get("compose"):
        return cfg
    templates = {}
    for item in template_sources(proj, profile):
        templates.setdefault(item["id"], item["entry"])
    return dict(cfg, compose=dict(cfg["compose"], templates=templates))


# --- elements of a template and the layout (F4c.1, D39) ---
_TAG = re.compile(r"""<!--.*?-->|<!\[CDATA\[.*?\]\]>|<([A-Za-z][^\s/>]*)((?:\s+[^\s=/>"']+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)\s*(/?)>""", re.S)
_ATTR = re.compile(r"""([^\s=/>"']+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'))?""")
_ELEMENT_NAME = re.compile(r"[a-z][a-zA-Z0-9]*")
_ORNAMENT = re.compile(r"ornament[0-9]+")
_INT = re.compile(r"[0-9]+")
ELEMENT_PREFIX = "gimg-"


def _tags(svg_text):
    """``(match, attrs)`` of every opening tag of `svg_text` (comments and CDATA skipped): `attrs` maps the attribute
    name to ``(value, start, end, quote)``, `start`/`end` being the span of the value in `svg_text`."""
    for m in _TAG.finditer(svg_text):
        if m.group(1) is None:
            continue
        attrs = {}
        base = m.start(2)
        for a in _ATTR.finditer(m.group(2)):
            double = a.group(2) is not None
            idx = 2 if double else 3
            if a.group(idx) is None:
                continue
            attrs.setdefault(a.group(1), (a.group(idx), base + a.start(idx), base + a.end(idx), '"' if double else "'"))
        yield m, attrs


def viewbox_of(svg_text):
    """``(x, y, w, h)`` of the ``viewBox`` of the root ``<svg>`` as numbers, or ``None`` if it has none or it is not four numbers."""
    for m, attrs in _tags(svg_text):
        if m.group(1) == "svg":
            raw = (attrs.get("viewBox") or ("",))[0].replace(",", " ").split()
            try:
                box = tuple(float(v) for v in raw)
            except ValueError:
                return None
            return box if len(box) == 4 else None
    return None


def _elements(svg_text, target=None) -> list:
    if target is not None and viewbox_of(svg_text) != (0.0, 0.0, float(target[0]), float(target[1])):
        return []
    found, seen = [], set()
    for m, attrs in _tags(svg_text):
        ident = (attrs.get("id") or ("",))[0]
        if not ident.startswith(ELEMENT_PREFIX):
            continue
        name = ident[len(ELEMENT_PREFIX):]
        if not _ELEMENT_NAME.fullmatch(name):
            raise GimgError("compose.bad_element", id=ident[:60], reason="name")
        if name in seen:
            raise GimgError("compose.bad_element", id=ident, reason="repeated")
        seen.add(name)
        parts = (attrs.get("data-gimg-box") or ("",))[0].replace(",", " ").split()
        if len(parts) != 4 or not all(_INT.fullmatch(v) for v in parts):
            raise GimgError("compose.bad_element", id=ident, reason="data-gimg-box")
        x, y, w, h = (int(v) for v in parts)
        if w < 1 or h < 1:
            raise GimgError("compose.bad_element", id=ident, reason="data-gimg-box")
        element = {"id": name, "kind": "logo" if name == "logo" else "ornament" if _ORNAMENT.fullmatch(name) else "text",
                   "box": {"x": x, "y": y, "w": w, "h": h}}
        color = attrs.get("data-gimg-color")
        if color is not None:
            if not _HEX_COLOR.fullmatch(color[0]):
                raise GimgError("compose.bad_element", id=ident, reason="data-gimg-color")
            if element["kind"] == "text":
                element["color"] = color[0]
        found.append(dict(element, _tag=(m, attrs)))
    return found


def elements(svg_text, target=None) -> list:
    """The editable elements of a template: ``[{"id", "kind": "text|logo|ornament", "box": {x, y, w, h}, "color"?}]``,
    in document order. An element is any tag with ``id="gimg-<name>"`` and ``data-gimg-box="x y w h"`` (``id`` here is
    the ``<name>``, the key of a layout). With `target` (``(width, height)``) only a template whose ``viewBox`` is
    ``0 0 <width> <height>`` has elements (``[]`` otherwise). A repeated id or a bad box or colour raises
    ``compose.bad_element``."""
    return [{k: v for k, v in e.items() if k != "_tag"} for e in _elements(svg_text, target)]


def _check_layout(found, layout, target) -> dict:
    """`layout` validated against the elements `found`: ``{name: {x, y, w, h}}`` of those that move (a box equal to the
    original is dropped). ``compose.element_unknown`` for a name the template lacks, ``compose.bad_layout`` otherwise."""
    if not isinstance(layout, dict):
        raise GimgError("compose.bad_layout", element="", reason="not an object")
    known = {e["id"]: e for e in found}
    moved = {}
    for name, box in layout.items():
        if name not in known:
            raise GimgError("compose.element_unknown", element=str(name)[:60], allowed=", ".join(known))
        if not (isinstance(box, dict) and set(box) == {"x", "y", "w", "h"}
                and all(type(v) is int for v in box.values())):
            raise GimgError("compose.bad_layout", element=name, reason="x, y, w, h integers")
        if box["w"] < 1 or box["h"] < 1 or box["x"] < 0 or box["y"] < 0 \
                or box["x"] + box["w"] > target[0] or box["y"] + box["h"] > target[1]:
            raise GimgError("compose.bad_layout", element=name, reason="outside %dx%d" % tuple(target))
        if box != known[name]["box"]:
            moved[name] = {k: box[k] for k in ("x", "y", "w", "h")}
    return moved


def _num(value) -> str:
    text = ("%.4f" % value).rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def _apply(svg_text, layout, target):
    """``(svg, moved, found)``: `svg_text` with the moved elements transformed, what moved and the elements read."""
    found = _elements(svg_text, target)
    moved = _check_layout(found, layout, target)
    edits = []
    for e in found:
        box = moved.get(e["id"])
        if box is None:
            continue
        m, attrs = e["_tag"]
        o = e["box"]
        move = "translate(%s %s) scale(%s %s) translate(%s %s)" % (
            box["x"], box["y"], _num(box["w"] / o["w"]), _num(box["h"] / o["h"]), -o["x"], -o["y"])
        if "transform" in attrs:
            value, start, end, _quote = attrs["transform"]
            edits.append((start, end, (move + " " + value).strip()))
        else:
            edits.append((m.end(2), m.end(2), ' transform="%s"' % move))
        _value, start, end, _quote = attrs["data-gimg-box"]
        edits.append((start, end, "%d %d %d %d" % (box["x"], box["y"], box["w"], box["h"])))
    out = svg_text
    for start, end, text in sorted(edits, key=lambda ed: (ed[0], ed[1]), reverse=True):
        out = out[:start] + text + out[end:]
    return out, moved, [{k: v for k, v in e.items() if k != "_tag"} for e in found]


def apply_layout(svg_text, layout, target) -> str:
    """`svg_text` with the elements of `layout` (``{name: {x, y, w, h}}``, integers, the box inside `target`) moved: the
    opening tag of each gets ``transform="translate(x y) scale(w/w0 h/h0) translate(-x0 -y0)"`` in front of the
    ``transform`` it had, and its ``data-gimg-box`` is rewritten. The rest of the SVG is not touched (it is not parsed
    as XML). ``compose.element_unknown`` / ``compose.bad_layout`` / ``compose.bad_element`` on failure."""
    return _apply(svg_text, layout, target)[0]


def zone_to_raw(profile_cfg, raw_w, raw_h, zone) -> tuple:
    """The `zone` ``(x, y, w, h)``, in pixels of the delivered image, as ``(x, y, w, h)`` in pixels of the raw image
    (the inverse of `fit_geometry`, rounded outwards). A zone partly outside the target or in the bands of
    ``contain`` is cut to the image; one entirely outside raises ``measure.zone_outside``."""
    width, height = target_size(profile_cfg)
    fit = _fit_of(profile_cfg.get("compose"))
    scale_w, scale_h, gx, gy = fit_geometry(raw_w, raw_h, width, height, fit)
    x, y, w, h = zone
    sign = 1 if fit == "cover" else -1  # cover crops the scaled image at (gx, gy); contain pads it by (gx, gy)
    x0, y0 = max(x, 0) + sign * gx, max(y, 0) + sign * gy
    x1, y1 = min(x + w, width) + sign * gx, min(y + h, height) + sign * gy
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, scale_w), min(y1, scale_h)
    if x1 <= x0 or y1 <= y0:
        raise GimgError("measure.zone_outside", zone="%d,%d,%d,%d" % tuple(zone), width=raw_w, height=raw_h)
    rx0, ry0 = x0 * raw_w // scale_w, y0 * raw_h // scale_h
    rx1, ry1 = min(raw_w, _ceil_div(x1 * raw_w, scale_w)), min(raw_h, _ceil_div(y1 * raw_h, scale_h))
    return rx0, ry0, max(1, rx1 - rx0), max(1, ry1 - ry0)


def _contrast_of(profile_cfg, compose_cfg, raw_path, raw_size, found, moved) -> dict:
    """``{name: {"zone", "text", "mean", "p10", "p90", "worst"}}`` of the text elements, measured on the raw image
    (the base image: nothing painted over it) in their final box (zone in pixels of the delivered image). The colour is
    the element's ``data-gimg-color``, else the template's ``textColor``; an element without colour, or whose measure
    fails, is left out (a measure never fails a composition)."""
    out = {}
    for e in found:
        color = e.get("color") or compose_cfg.get("textColor")
        if e["kind"] != "text" or not color:
            continue
        box = moved.get(e["id"], e["box"])
        zone = (box["x"], box["y"], box["w"], box["h"])
        try:
            rgb = measure.parse_hex(color)
            pix = measure.pixels(raw_path, zone_to_raw(profile_cfg, raw_size[0], raw_size[1], zone))
            out[e["id"]] = {"zone": list(zone), "text": measure.hex_of(rgb), **measure.contrast(pix, rgb)}
        except GimgError:
            continue
    return out


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def fit_geometry(src_w, src_h, dst_w, dst_h, fit) -> tuple:
    """``(scale_w, scale_h, x, y)``, integers, to take a ``src_w``x``src_h`` image to ``dst_w``x``dst_h``.

    ``cover``: scale (rounding up) by the side that rules so both sides reach the target, then crop at ``(x, y)``,
    centred. ``contain``: scale (rounding down) so the image fits inside the target, then pad; ``(x, y)`` is where the
    scaled image sits in the padded canvas, centred. 1280x640 to 1200x630 is ``(1260, 630, 30, 0)``."""
    if min(src_w, src_h, dst_w, dst_h) <= 0:
        raise GimgError("compose.bad_size", source="%sx%s" % (src_w, src_h), target="%sx%s" % (dst_w, dst_h))
    if fit == "cover":
        if src_w * dst_h >= src_h * dst_w:  # the source is as wide or wider: the height rules, the sides are cropped
            scale_w, scale_h = _ceil_div(src_w * dst_h, src_h), dst_h
        else:
            scale_w, scale_h = dst_w, _ceil_div(src_h * dst_w, src_w)
        return scale_w, scale_h, (scale_w - dst_w) // 2, (scale_h - dst_h) // 2
    if fit == "contain":
        if src_w * dst_h >= src_h * dst_w:  # the width rules
            scale_w, scale_h = dst_w, max(1, src_h * dst_w // src_w)
        else:
            scale_w, scale_h = max(1, src_w * dst_h // src_h), dst_h
        return scale_w, scale_h, (dst_w - scale_w) // 2, (dst_h - scale_h) // 2
    raise GimgError("compose.bad_fit", fit=str(fit), allowed=", ".join(FITS))


def xml_escape(text: str) -> str:
    """`text` as XML content or attribute value: ``& < > " '`` escaped, characters XML 1.0 forbids dropped."""
    return "".join(_ESCAPES.get(c, c) for c in _XML_FORBIDDEN.sub("", text))


def substitute(svg_text: str, values: dict) -> str:
    """Fill every ``{{name}}`` of `svg_text` with the escaped ``values[name]``, in a single pass.

    A value that itself contains ``{{logo}}`` stays as text. A hole with no value raises ``compose.field_unknown``."""
    def fill(match):
        name = match.group(1)
        if name not in values:
            raise GimgError("compose.field_unknown", field=name)
        return xml_escape(str(values[name]))
    return _HOLE.sub(fill, svg_text)


def _read_svg(path: Path) -> str:
    """The UTF-8 text of an SVG of at most MAX_SVG_BYTES."""
    try:
        with open(path, "rb") as fh:
            data = fh.read(MAX_SVG_BYTES + 1)
    except OSError as exc:
        raise GimgError("compose.svg_unreadable", path=str(path), reason=exc.strerror or str(exc))
    if len(data) > MAX_SVG_BYTES:
        raise GimgError("compose.svg_too_big", path=str(path), limit=MAX_SVG_BYTES)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise GimgError("compose.svg_unreadable", path=str(path), reason="not UTF-8")


def _asset(project_root, rel, missing_code):
    """The resolved file `rel` inside the project: the D25 guard, then it has to be a file of a sane size."""
    target = paths.inside(project_root, rel)
    if not target.is_file():
        raise GimgError(missing_code, path=rel)
    try:
        size = target.stat().st_size
    except OSError:
        raise GimgError(missing_code, path=rel)
    if size > MAX_SVG_BYTES:
        raise GimgError("compose.svg_too_big", path=rel, limit=MAX_SVG_BYTES)
    return target


def resolve_assets(project_root, compose_cfg) -> tuple:
    """``(template_path, logo_path_or_None)`` of a ``compose`` configuration, resolved inside `project_root`.

    A path that fails the D25 guard raises its ``path.*`` code; one that is not a file, ``compose.template_missing`` or
    ``compose.logo_missing``; one over MAX_SVG_BYTES, ``compose.svg_too_big``. A template of the local folder (F4c.2)
    is resolved inside that folder (``templateRoot``), the logo always inside the project."""
    template = _asset(compose_cfg.get("templateRoot") or project_root, compose_cfg["template"], "compose.template_missing")
    logo = compose_cfg.get("logo")
    return template, (_asset(project_root, logo, "compose.logo_missing") if logo else None)


def logo_data_uri(logo_path) -> str:
    """The logo SVG as ``data:image/svg+xml;base64,...``: no path for ``rsvg-convert`` to resolve."""
    raw = _read_svg(Path(logo_path)).encode("utf-8")
    return "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")


def rsvg_argv(svg, out, width, height) -> list:
    return ["rsvg-convert", "-w", str(width), "-h", str(height), "-o", str(out), str(svg)]


def ffmpeg_argv(raw, layer, out, geom, fit) -> list:
    """The ``ffmpeg`` call that scales `raw`, crops or pads it and lays `layer` (or nothing) over it.

    `geom` is ``(width, height, scale_w, scale_h, x, y)``: the target and what `fit_geometry` returned."""
    width, height, scale_w, scale_h, x, y = geom
    scale = "[0:v]scale=%d:%d:flags=lanczos" % (scale_w, scale_h)
    if fit == "cover":
        base = "%s,crop=%d:%d:%d:%d" % (scale, width, height, x, y)
        graph = ("%s[b];[b][1:v]overlay=0:0:format=auto,format=rgb24[out]" % base if layer is not None
                 else "%s,format=rgb24[out]" % base)
    elif fit == "contain":  # the bands are transparent: the template paints them
        base = "%s,format=rgba,pad=%d:%d:%d:%d:color=black@0" % (scale, width, height, x, y)
        graph = ("%s[b];[b][1:v]overlay=0:0:format=auto,format=rgba[out]" % base if layer is not None
                 else "%s[out]" % base)
    else:
        raise GimgError("compose.bad_fit", fit=str(fit), allowed=", ".join(FITS))
    argv = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw)]
    if layer is not None:
        argv += ["-i", str(layer)]
    return argv + ["-filter_complex", graph, "-map", "[out]", "-frames:v", "1", "-update", "1",
                   "-map_metadata", "-1", str(out)]


def _last_line(text: bytes) -> str:
    lines = [ln.strip() for ln in text.decode("utf-8", errors="replace").splitlines() if ln.strip()]
    return lines[-1][:300] if lines else ""


def _run(argv, tool) -> None:
    """Run `argv` (no shell, no input, time limit); a failure is a ``compose.*`` error naming `tool`."""
    if shutil.which(argv[0]) is None:
        raise GimgError("compose.tool_missing", tool=tool)
    try:
        done = subprocess.run(argv, capture_output=True, stdin=subprocess.DEVNULL, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise GimgError("compose.timeout", tool=tool, seconds=TIMEOUT_S)
    except FileNotFoundError:
        raise GimgError("compose.tool_missing", tool=tool)
    except OSError as exc:
        raise GimgError("compose.tool_failed", tool=tool, reason=str(exc.strerror or exc)[:300])
    if done.returncode != 0:
        raise GimgError("compose.tool_failed", tool=tool,
                        reason=_last_line(done.stderr) or "exit code %d" % done.returncode)


def _carry_chunk(raw_path, out_path, info) -> None:
    """Copy the ``gimg`` chunk of the raw image to the result with ``compose`` added; a failure only prints a line."""
    try:
        meta = png.read_text_chunks(raw_path).get("gimg")
        if meta is None:
            return
        data = json.loads(meta)
        if not isinstance(data, dict):
            data = {}
        data["compose"] = info
        png.add_text_chunk(out_path, "gimg", json.dumps(data, ensure_ascii=False, sort_keys=True))
    except (GimgError, OSError, ValueError) as exc:
        reason = exc.params.get("reason", exc.code) if isinstance(exc, GimgError) else str(exc)
        print(i18n.t("compose.chunk_failed", path=str(out_path), reason=reason), file=sys.stderr)


def check_distinct(raw_path, out_path) -> None:
    """``compose.write_failed`` if the raw image and the result are the same file (a ``raw`` that does not end in
    ``.raw.png``, or a link): composing would overwrite the raw image, which is never modified."""
    try:
        same = Path(raw_path).resolve() == Path(out_path).resolve()
    except (OSError, RuntimeError):
        same = False
    if same:
        raise GimgError("compose.write_failed", path=str(out_path), reason="it is the raw image")


def render(project_root, profile_cfg, raw_path, out_path, text, profile=None, prefix=COMPOSE_TMP_PREFIX,
           template=None, layout=None) -> dict:
    """Compose the raw image `raw_path` into `out_path` for `profile_cfg` and return what was done.

    `project_root` is the folder of the project (the template and the logo are resolved inside it); `text` maps the
    ``compose.fields`` to their texts (a missing field is the empty string). The result is written atomically: nothing
    is left at `out_path` if a step fails. Returns ``{"fit", "targetWidth", "targetHeight", "text"}`` plus
    ``template`` and ``logo`` when the profile has them: what the attempt records as ``compose``, plus ``templateId``
    whenever there is a ``compose``. `template` is the id of one of ``compose.templates`` (``None``: ``default``, the
    profile's own; unknown: ``compose.template_unknown``).

    `layout` (``{name: {x, y, w, h}}``, F4c) moves the elements of the template (`apply_layout`, after the holes are
    filled); what moved is returned as ``layout`` and the contrast of each text element over the raw image, in its
    final box, as ``contrast`` (`_contrast_of`). A template whose elements are malformed composes as if it had none,
    unless a `layout` asks for them.

    The temporary folder sits next to `out_path` and starts with `prefix`: each caller uses its own, so recovering one
    composition (`queue._clean_pending` removes ``.compose-q<entry>-*``) never touches another's."""
    raw_path, out_path = Path(raw_path), Path(out_path)
    check_distinct(raw_path, out_path)
    raw_w, raw_h = png.size(raw_path)
    plan = plan_for(profile_cfg, raw_w, raw_h)
    if plan is None:
        raise GimgError("compose.nothing_to_do", profile=profile or "")
    width, height, fit = plan["targetWidth"], plan["targetHeight"], plan["fit"]
    geom = (width, height) + fit_geometry(raw_w, raw_h, width, height, fit)
    template_id = None if template == DEFAULT_TEMPLATE else template
    compose_cfg = effective(profile_cfg.get("compose"), template_id)
    used = {}
    layer_svg = None
    moved, found = {}, []
    if profile_cfg.get("compose") is not None:
        template, logo = resolve_assets(project_root, compose_cfg)
        source = _read_svg(template)
        values = {}
        for name in compose_cfg.get("fields", []):
            value = (text or {}).get(name, "")
            if not isinstance(value, str):
                raise GimgError("compose.bad_text", field=name)
            values[name] = value
            used[name] = value
        if "logo" in {m.group(1) for m in _HOLE.finditer(source)}:
            if logo is None:
                raise GimgError("compose.no_logo", template=compose_cfg["template"])
            values["logo"] = logo_data_uri(logo)
        layer_svg = substitute(source, values)
        try:
            layer_svg, moved, found = _apply(layer_svg, layout or {}, (width, height))
        except GimgError as exc:
            if exc.code == "compose.bad_element" and not layout:
                found = []
            else:
                raise
    elif layout:
        _check_layout([], layout, (width, height))
    info = dict(plan, text=used)
    if profile_cfg.get("compose") is not None:
        info["template"] = compose_cfg["template"]
        info.pop("logo", None)
        if compose_cfg.get("logo"):
            info["logo"] = compose_cfg["logo"]
        info["templateId"] = DEFAULT_TEMPLATE if template_id is None else template_id
        if moved:
            info["layout"] = moved
        contrast = _contrast_of(profile_cfg, compose_cfg, raw_path, (raw_w, raw_h), found, moved)
        if contrast:
            info["contrast"] = contrast
    try:
        with tempfile.TemporaryDirectory(dir=str(out_path.parent), prefix=prefix) as tmp:
            tmp = Path(tmp)
            layer = None
            if layer_svg is not None:
                svg = tmp / "template.svg"
                svg.write_text(layer_svg, encoding="utf-8")
                layer = tmp / "layer.png"
                _run(rsvg_argv(svg, layer, width, height), "rsvg-convert")
                if not layer.is_file():
                    raise GimgError("compose.tool_failed", tool="rsvg-convert", reason="no output")
            result = tmp / "out.png"
            _run(ffmpeg_argv(raw_path, layer, result, geom, fit), "ffmpeg")
            if not result.is_file():
                raise GimgError("compose.tool_failed", tool="ffmpeg", reason="no output")
            _carry_chunk(raw_path, result, info)
            os.replace(result, out_path)
    except OSError as exc:
        raise GimgError("compose.write_failed", path=str(out_path), reason=exc.strerror or str(exc))
    return info


def _pick_attempt(order: dict, attempt_id) -> dict:
    """The attempt `recompose` works on: `attempt_id`, else the chosen one, else the last (highest id)."""
    if attempt_id is None:
        attempt_id = order["chosen"]
    if attempt_id is None and order["attempts"]:
        attempt_id = max(a["id"] for a in order["attempts"])
    if attempt_id is None:
        raise GimgError("compose.no_attempts", order=order["key"], profile=order["profile"])
    for item in order["attempts"]:
        if type(attempt_id) is int and item["id"] == attempt_id:
            return item
    raise GimgError("order.attempt_unknown", attempt=attempt_id, order=order["key"], profile=order["profile"])


def _keep_raw(source: Path, raw_path: Path) -> None:
    """Copy `source` (the ``image`` of an attempt made before F2.8) to `raw_path`, atomically."""
    try:
        fd, tmp = tempfile.mkstemp(dir=str(raw_path.parent), prefix="." + raw_path.name + ".", suffix=".tmp")
        os.close(fd)
        try:
            shutil.copyfile(source, tmp)
            os.replace(tmp, raw_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except OSError as exc:
        raise GimgError("compose.write_failed", path=str(raw_path), reason=exc.strerror or str(exc))


def _log_recompose(project, key, profile, attempt, info=None, error=None) -> None:
    """One line in the project log, like the worker's (D26): ``app.image.compose`` or ``app.image.compose_error``. It is
    not a generation (nothing ran an engine): the operation is ``image_composition`` and there is no provider, model or
    duration, so `log.estimate` and the pilot's measures never count it; ``app.image.recompose`` also says so.
    Never fails the caller."""
    try:
        spec = dict(attempt, params={k: v for k, v in (attempt.get("params") or {}).items() if k != "model"})
        record = log.record_for(key, profile, spec, limits.load_machine(), None, operation=log.OP_COMPOSITION,
                                compose=(info or {}).get("template"), compose_error=(error or {}).get("code"))
        record["app.image.recompose"] = True
        log.append(project, record)
    except Exception as exc:
        print(i18n.t("compose.log_failed", reason=str(exc)), file=sys.stderr)


def recompose(project, key, profile, attempt_id=None, text=None, template=None, layout=None) -> dict:
    """Compose an attempt again from its raw image, without generating (D28); returns the attempt (a copy).

    The attempt is `attempt_id`, else the chosen one, else the last. `text` (``{field: value}``) is merged into the
    order's ``text`` first (`orders.set_text`: the next attempts and the gallery use it too) and the order's text is what
    gets composed. An attempt made before F2.8 has no raw image: its ``image`` is copied to ``<stem>.raw.png`` before
    anything else (`orders.set_composed` expects it). The temporary folder is ``.compose-c<id>-*``.

    One process composes an attempt at a time: from `orders.set_text` to the delivery the attempt's lock
    (`orders.compose_lock_path`, also the worker's) is held, and if it is not free this raises ``compose.busy``. With
    the lock taken, what an earlier ``gimg compose`` that was killed left (``.compose-c<id>-*``, ``.<raw>.*.tmp``) is removed.

    A profile with nothing to compose raises ``compose.nothing_to_do`` before anything changes, unless the attempt has a
    ``composeError``: then the error is dropped (`orders.clear_compose_error`) and it returns normally. If the render fails, the
    attempt gets the error as ``composeError`` (`orders.set_compose_error`) and it is raised again; a project log line
    records either result. The chosen attempt is delivered again (manifest included; `delivery.redeliver` checks it still
    is the chosen one under the delivery lock) and the result then has ``delivered``: the file, relative to the project.

    `template` (an id of `templates_of`) composes with that template and the attempt keeps it (``compose.templateId``); an
    unknown one raises ``compose.template_unknown`` before anything changes. Without it the attempt's own ``templateId``
    is used, else ``default``; one that no longer exists fails like any other composition error, it never falls back.

    `layout` (F4c, ``{name: {x, y, w, h}}``) is the position of the elements of the template and the attempt keeps it
    (``compose.layout``); ``{}`` goes back to the template. Without it the attempt's own layout is kept, except when
    `template` changes the template (its elements are other ones: the layout is emptied). A `layout` the template does
    not take (``compose.element_unknown``, ``compose.bad_layout``) raises before anything changes. A layout that was
    kept survives a failed composition (``composeError.layout``)."""
    proj = projects.get(project)
    profile_cfg = merged_profile(proj, profile)
    order = orders.get(project, key, profile)
    if profile_cfg is None:
        raise GimgError("order.profile_unknown", profile=profile)
    attempt_id = _pick_attempt(order, attempt_id)["id"]
    if template is not None:
        effective(profile_cfg.get("compose"), template)
    with fsutil.try_lock(orders.compose_lock_path(project, key, profile, attempt_id)) as taken:
        if not taken:  # the worker or another `gimg compose` is composing this attempt
            raise GimgError("compose.busy", attempt=attempt_id)
        return _recompose_locked(proj, project, key, profile, profile_cfg, attempt_id, text, template, layout)


def _clean_leftovers(raw_path: Path, folder: Path, attempt_id: int) -> None:
    """Remove what a ``gimg compose`` that was killed left for this attempt (the lock says nobody is composing it)."""
    leftovers = list(folder.glob((RECOMPOSE_TMP_PREFIX % attempt_id) + "*"))
    leftovers += raw_path.parent.glob("." + glob.escape(raw_path.name) + ".*.tmp")
    for item in leftovers:
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item, ignore_errors=True)
        else:
            try:
                item.unlink()
            except OSError:
                pass


def _check_layout_for(root, profile_cfg, template_id, layout) -> None:
    """Raise what `render` would raise for `layout` on this template, without composing anything."""
    compose_cfg = profile_cfg.get("compose")
    if not compose_cfg:
        _check_layout([], layout, (0, 0))
        return
    path, _logo = resolve_assets(root, effective(compose_cfg, template_id))
    _apply(_read_svg(path), layout, target_size(profile_cfg))


def _recompose_locked(proj, project, key, profile, profile_cfg, attempt_id, text, template=None, layout=None) -> dict:
    """`recompose` with the lock of the attempt held, from reading the attempt to delivering it."""
    order = orders.get(project, key, profile)  # again: it may have changed while the lock was not ours
    attempt = _pick_attempt(order, attempt_id)
    raw_path, out_path = orders.compose_paths(project, key, profile, attempt)
    check_distinct(raw_path, out_path)
    _clean_leftovers(raw_path, out_path.parent, attempt_id)
    # an attempt without ``raw`` is made before F2.8; if its copy is already there, the image may be a composed one
    keep = not isinstance(attempt.get("raw"), str) and not raw_path.is_file()
    source = orders.attempt_image(project, key, profile, attempt) if keep else raw_path
    if plan_for(profile_cfg, *png.size(source)) is None:
        if "composeError" not in attempt:
            raise GimgError("compose.nothing_to_do", profile=profile)
        # the profile stopped composing after a failure: the raw image is the attempt's image, as for a profile that never
        # composed. The error goes away (it blocks choose/undo) and this ends well: there is nothing left to fix.
        done = orders.clear_compose_error(project, key, profile, attempt_id)
        if delivery.redeliver(project, key, profile, attempt_id):
            done["delivered"] = delivery.delivered_file(project, key, profile)
        return done
    stored = attempt.get("compose") or {}
    failed_before = attempt.get("composeError") or {}
    previous = stored.get("templateId") or failed_before.get("templateId")
    if layout is not None and layout != {}:  # a layout the template does not take changes nothing
        _check_layout_for(proj["root"], profile_cfg, template or previous, layout)
    if layout is None:
        changed = template is not None and (template or DEFAULT_TEMPLATE) != (previous or DEFAULT_TEMPLATE)
        layout = {} if changed else copy.deepcopy(stored.get("layout") or failed_before.get("layout") or {})
    texts = orders.set_text(project, key, profile, text) if text else dict(order.get("text") or {})
    if keep:
        _keep_raw(source, raw_path)
    try:
        if template is None:
            template = previous
        info = render(proj["root"], profile_cfg, raw_path, out_path, texts, profile,
                      prefix=RECOMPOSE_TMP_PREFIX % attempt_id,
                      **({} if template is None else {"template": template}),
                      **({"layout": layout} if layout else {}))
        done = orders.set_composed(project, key, profile, attempt_id, info)
    except Exception as exc:
        code, params = (exc.code, exc.params) if isinstance(exc, GimgError) else (
            "compose.unexpected", {"reason": ("%s: %s" % (type(exc).__name__, exc))[:300]})
        error = {"code": code, "params": json.loads(json.dumps(params, default=str))}
        try:
            failed = orders.set_compose_error(project, key, profile, attempt_id, error, template, layout)
        except Exception:
            failed = attempt
        _log_recompose(project, key, profile, failed, error=error)
        raise
    _log_recompose(project, key, profile, done, info=info)
    if delivery.redeliver(project, key, profile, attempt_id):  # only if it still is the chosen one
        done["delivered"] = delivery.delivered_file(project, key, profile)
    return done


def _create_new(path: Path, data: bytes) -> None:
    """Write `data` to `path`, which must not exist (``O_EXCL``: nothing is ever overwritten, a link is not followed)."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        raise GimgError("compose.template_exists", template=path.stem)
    except OSError as exc:
        raise GimgError("compose.write_failed", path=path.name, reason=exc.strerror or str(exc))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        try:
            path.unlink()
        except OSError:
            pass
        raise GimgError("compose.write_failed", path=path.name, reason=exc.strerror or str(exc))


def save_template(project, key, profile, attempt_id, name, dest="local") -> dict:
    """Save the template of attempt `attempt_id` of the order, with its layout applied and the holes unfilled, as a new
    template `name` of `profile` (F4c.2, D40); returns its entry of `templates_of`.

    `dest` ``local`` writes ``<data>/projects/<project>/templates/<profile>/<name>.svg``; ``project`` writes
    ``<compose.templatesDir>/<profile>/<name>.svg`` inside the project (``compose.templates_dir_missing`` without
    ``templatesDir``). Next to the SVG goes ``<name>.json`` with ``base`` (the template it comes from) and what it
    inherited (``logo``, ``fields``, ``zone``, ``textColor``). `name` has the pattern of the template ids
    (``compose.bad_name``); one that exists in any source raises ``compose.template_exists`` and no file is ever
    overwritten."""
    if not isinstance(name, str) or not _TEMPLATE_ID.fullmatch(name):
        raise GimgError("compose.bad_name", name=str(name)[:60])
    if dest not in ("local", "project"):
        raise GimgError("compose.bad_dest", dest=str(dest)[:20], allowed="local, project")
    proj = projects.get(project)
    profile_cfg = merged_profile(proj, profile)
    if profile_cfg is None:
        raise GimgError("order.profile_unknown", profile=profile)
    compose_cfg = profile_cfg.get("compose")
    if not compose_cfg:
        raise GimgError("compose.nothing_to_do", profile=profile)
    if dest == "project" and not compose_cfg.get("templatesDir"):
        raise GimgError("compose.templates_dir_missing", profile=profile)
    if name in _template_ids(compose_cfg):
        raise GimgError("compose.template_exists", template=name)
    attempt = _pick_attempt(orders.get(project, key, profile), attempt_id)
    stored = attempt.get("compose") or attempt.get("composeError") or {}
    base = stored.get("templateId") or DEFAULT_TEMPLATE
    cfg = effective(compose_cfg, base)
    path, _logo = resolve_assets(proj["root"], cfg)
    svg = _read_svg(path)
    layout = stored.get("layout")
    if layout:
        svg = apply_layout(svg, layout, target_size(profile_cfg))
    if dest == "project":
        folder = project_templates_dir(proj["root"], compose_cfg, profile)
    else:
        folder = local_templates_dir(project, profile)
    svg_path, json_path = paths.inside(folder, name + ".svg"), paths.inside(folder, name + ".json")
    sidecar = {"base": base, **{k: cfg[k] for k in ("logo", "fields", "zone", "textColor") if k in cfg}}
    _create_new(json_path, (json.dumps(sidecar, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    try:
        _create_new(svg_path, svg.encode("utf-8"))
    except GimgError:
        try:
            json_path.unlink()
        except OSError:
            pass
        raise
    fresh = templates_of(merged_profile(projects.get(project), profile))
    return next(item for item in fresh if item["id"] == name)


__all__ = ["recompose", "render", "effective", "templates_of", "merged_profile", "template_sources", "save_template",
           "elements", "apply_layout", "zone_to_raw", "viewbox_of", "DEFAULT_TEMPLATE", "plan_for", "target_size", "fit_geometry", "substitute", "xml_escape", "resolve_assets",
           "logo_data_uri", "rsvg_argv", "ffmpeg_argv", "TIMEOUT_S", "MAX_SVG_BYTES"]
