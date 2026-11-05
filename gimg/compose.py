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
import posixpath
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
    template reserves a different zone). ``fit`` is the profile's; ``fonts`` is the profile's plus the ``fonts`` of the
    entry (the families a saved template uses, F4e.2). An id that does not exist, or a
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
    own = entry.get("fonts")
    if isinstance(own, list) and own:  # F4e.2: the families the template uses join the profile's `compose.fonts`
        out["fonts"] = list(base.get("fonts") or []) + [f for f in own if f not in (base.get("fonts") or [])]
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


def templates_with_elements(proj, profile) -> list:
    """`templates_of` of the profile `profile` of the loaded project `proj`, each entry with ``"elements"``: what
    `elements` reads on its SVG (F4c.3, for the editor). ``[]`` if the ``viewBox`` is not the target, the SVG has no
    elements or cannot be read (the rest of the list is still given)."""
    pcfg = merged_profile(proj, profile)
    items = templates_of(pcfg)
    if not items:
        return items
    target = target_size(pcfg)
    for item in items:
        try:
            template, _logo = resolve_assets(proj["root"], effective(pcfg["compose"], item["id"]))
            item["elements"] = elements(_read_svg(template), target)
        except GimgError:
            item["elements"] = []
    return items


# --- templates from folders (F4c.2, D40) ---
_TEMPLATE_ID = re.compile(r"(?!default$)[a-z0-9][a-z0-9-]{0,39}")
_FIELD_NAME = re.compile(r"(?!logo$)[a-z][a-zA-Z0-9]*")
_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
SOURCES = ("config", "project", "local")
MAX_FOLDER_TEMPLATES = 100
MAX_SIDECAR_BYTES = 65536
MAX_FONTS = 20
_FAMILY = re.compile(r"[A-Za-z0-9 ._-]{1,64}")


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
    """The inheritable keys of ``<name>.json`` that are valid (anything else is ignored); ``{}`` if unreadable.
    ``fonts`` (F4e.2) is a list of up to 20 family names."""
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
    fonts = data.get("fonts")
    if isinstance(fonts, list) and 0 < len(fonts) <= MAX_FONTS and all(isinstance(f, str) and _FAMILY.fullmatch(f) for f in fonts):
        out["fonts"] = list(fonts)
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
        if _is_hidden_in(attrs):
            element["hidden"] = True
        found.append(dict(element, _tag=(m, attrs)))
    return found


def elements(svg_text, target=None) -> list:
    """The editable elements of a template: ``[{"id", "kind": "text|logo|ornament", "box": {x, y, w, h}, "color"?,
    "hidden"?}]`` (``hidden: true`` when the template itself carries ``display="none"``),
    in document order. An element is any tag with ``id="gimg-<name>"`` and ``data-gimg-box="x y w h"`` (``id`` here is
    the ``<name>``, the key of a layout). With `target` (``(width, height)``) only a template whose ``viewBox`` is
    ``0 0 <width> <height>`` has elements (``[]`` otherwise). A repeated id or a bad box or colour raises
    ``compose.bad_element``."""
    return [{k: v for k, v in e.items() if k != "_tag"} for e in _elements(svg_text, target)]


STYLE_KEYS = ("family", "size", "weight", "italic", "color", "align", "lineHeight")
ALIGNS = ("left", "center", "right")
MAX_TEXT = 500
MAX_ADDED = 10
ADDED_PREFIX = "extra"
_ADDED = re.compile(r"extra[1-9][0-9]{0,2}")
DEFAULT_SIZE = 16
DEFAULT_LINE_HEIGHT = 1.2
_ANCHORS = {"start": "left", "middle": "center", "end": "right"}


def _is_number(v) -> bool:
    return type(v) in (int, float) and v == v and v not in (float("inf"), float("-inf"))


def _check_text(name, text) -> str:
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise GimgError("compose.bad_layout", element=name, reason="text: a string of up to %d characters" % MAX_TEXT)
    return text


def _check_style(name, style, full=False) -> dict:
    """`style` validated: ``{family?, size?, weight?, italic?, color?, align?, lineHeight?}``; with `full` all of them
    but ``lineHeight`` are required (an added text has nothing to inherit)."""
    def bad(reason):
        return GimgError("compose.bad_layout", element=name, reason=reason)

    if not isinstance(style, dict):
        raise bad("style: an object")
    for key in style:
        if key not in STYLE_KEYS:
            raise bad("style.%s: unknown key (allowed: %s)" % (str(key)[:30], ", ".join(STYLE_KEYS)))
    if full:
        missing = [k for k in STYLE_KEYS if k != "lineHeight" and k not in style]
        if missing:
            raise bad("style: %s required" % ", ".join(missing))
    out = dict(style)
    if "family" in out and not (isinstance(out["family"], str) and _FAMILY.fullmatch(out["family"])):
        raise bad("style.family: 1-64 characters of A-Z a-z 0-9 space . _ -")
    if "size" in out and not (type(out["size"]) is int and 4 <= out["size"] <= 1000):
        raise bad("style.size: an integer from 4 to 1000")
    if "weight" in out and not (type(out["weight"]) is int and 100 <= out["weight"] <= 900 and out["weight"] % 100 == 0):
        raise bad("style.weight: 100 to 900 in steps of 100")
    if "italic" in out and type(out["italic"]) is not bool:
        raise bad("style.italic: a boolean")
    if "color" in out and not (isinstance(out["color"], str) and _HEX_COLOR.fullmatch(out["color"])):
        raise bad("style.color: #rrggbb")
    if "align" in out and out["align"] not in ALIGNS:
        raise bad("style.align: left, center or right")
    if "lineHeight" in out and not (_is_number(out["lineHeight"]) and 0.8 <= out["lineHeight"] <= 3):
        raise bad("style.lineHeight: a number from 0.8 to 3")
    return out


def _check_box(name, entry, target) -> dict:
    box = {k: entry.get(k) for k in ("x", "y", "w", "h")}
    if not all(type(v) is int for v in box.values()):
        raise GimgError("compose.bad_layout", element=name, reason="x, y, w, h integers")
    if box["w"] < 1 or box["h"] < 1 or box["x"] < 0 or box["y"] < 0 \
            or box["x"] + box["w"] > target[0] or box["y"] + box["h"] > target[1]:
        raise GimgError("compose.bad_layout", element=name, reason="outside %dx%d" % tuple(target))
    return box


def _check_added(name, entry, known, target) -> dict:
    """An entry ``{"add": true, x, y, w, h, text, style}`` validated; the added text it describes (F4e.2)."""
    def bad(reason):
        return GimgError("compose.bad_layout", element=name, reason=reason)

    if entry.get("add") is not True:
        raise bad("add: true")
    if not _ADDED.fullmatch(str(name)):
        raise bad("an added text is called extra<N>")
    if name in known:
        raise bad("the template already has an element with this id")
    if not set(entry) <= {"add", "x", "y", "w", "h", "text", "style"} \
            or not {"x", "y", "w", "h", "text", "style"} <= set(entry):
        raise bad("an added text needs x, y, w, h, text and style, and nothing else")
    box = _check_box(name, entry, target)
    return {"add": True, **box, "text": _check_text(name, entry["text"]), "style": _check_style(name, entry["style"], True)}


def _check_layout(found, layout, target, adds=True) -> dict:
    """`layout` validated against the elements `found`: ``{name: {x, y, w, h, hidden?, text?, style?}}`` of those that
    move, are hidden (``"hidden": true``; a box equal to the original and not hidden is dropped; ``hidden: false`` is
    dropped unless the element is hidden by the template itself, ``display="none"``: then it is kept and shows it) or
    are given a ``text`` or a ``style`` (F4e.2, only an element whose tag is ``<text>``; an empty ``style`` alone does
    nothing). With `adds`, an entry ``{"add": true, x, y, w, h, text, style}`, named ``extra<N>`` (at most
    `MAX_ADDED`), is a text to add: it is kept as ``{"add": true, ...}``. ``compose.element_unknown`` for a name the
    template lacks, ``compose.bad_layout`` otherwise."""
    if not isinstance(layout, dict):
        raise GimgError("compose.bad_layout", element="", reason="not an object")
    known = {e["id"]: e for e in found}
    moved, added = {}, 0
    for name, box in layout.items():
        if adds and isinstance(box, dict) and "add" in box:
            added += 1
            if added > MAX_ADDED:
                raise GimgError("compose.bad_layout", element=str(name)[:60], reason="at most %d added texts" % MAX_ADDED)
            moved[name] = _check_added(str(name)[:60], box, known, target)
            continue
        if name not in known:
            raise GimgError("compose.element_unknown", element=str(name)[:60], allowed=", ".join(known))
        keys = {"x", "y", "w", "h", "hidden", "text", "style"}
        if not (isinstance(box, dict) and {"x", "y", "w", "h"} <= set(box) and set(box) <= keys
                and all(type(box[k]) is int for k in ("x", "y", "w", "h"))):
            raise GimgError("compose.bad_layout", element=name, reason="x, y, w, h integers")
        if "hidden" in box and type(box["hidden"]) is not bool:
            raise GimgError("compose.bad_layout", element=name, reason="hidden boolean")
        _check_box(name, box, target)
        tag = known[name].get("_tag")
        if ("text" in box or "style" in box) and not (tag[0].group(1) == "text" if tag else known[name]["kind"] == "text"):
            raise GimgError("compose.bad_layout", element=name, reason="text and style only in <text>")
        text = _check_text(name, box["text"]) if "text" in box else None
        style = _check_style(name, box["style"]) if "style" in box else {}
        paint = {**({"text": text} if text is not None else {}), **({"style": style} if style else {})}
        xywh = {k: box[k] for k in ("x", "y", "w", "h")}
        if box.get("hidden") is True:
            moved[name] = {**xywh, "hidden": True, **paint}
        elif box.get("hidden") is False and tag and _is_hidden_in(tag[1]):  # showing what the template hides
            moved[name] = {**xywh, "hidden": False, **paint}
        elif xywh != known[name]["box"] or paint:
            moved[name] = {**xywh, **paint}
    return moved


_STYLE_DISPLAY = re.compile(r"(display\s*:\s*)([^;]*)", re.I)
_STYLE_PROP = r"(?:^|;)\s*%s\s*:\s*([^;]*)"
_NUMBER = re.compile(r"[0-9]*\.?[0-9]+")


def _is_hidden_in(attrs) -> bool:
    """Whether the tag already carries ``display="none"`` (attribute or inside ``style``): a template saved with a hidden element."""
    if (attrs.get("display") or ("",))[0].strip() == "none":
        return True
    m = _STYLE_DISPLAY.search((attrs.get("style") or ("",))[0])
    return bool(m and m.group(2).strip().lower().startswith("none"))


def _num(value) -> str:
    text = ("%.4f" % value).rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def _css_prop(attrs, prop):
    """The value of `prop` as the tag sets it (inside ``style`` first, else as an attribute), or ``None``."""
    m = re.search(_STYLE_PROP % re.escape(prop), (attrs.get("style") or ("",))[0], re.I)
    if m:
        return m.group(1).strip()
    return (attrs.get(prop) or (None,))[0]


def _base_size(attrs) -> int:
    """The ``font-size`` a text element has in the template (``DEFAULT_SIZE`` if none or not a number), 4-1000."""
    m = _NUMBER.match(_css_prop(attrs, "font-size") or "")
    return min(1000, max(4, int(round(float(m.group(0)))))) if m else DEFAULT_SIZE


def _text_size(attrs, box, sizes) -> int:
    """The size a text element is painted with: ``sizes[name]`` (what `render` fitted), else ``style.size``, else the template's."""
    return (sizes or {}).get(box["_name"]) or (box.get("style") or {}).get("size") or _base_size(attrs)


def _text_paint(box, name, attrs, size, inner=None):
    """What painting a text element in `box` (an entry of the layout with ``text`` and/or ``style``) changes:
    ``({attribute: value}, style_to_append, content)``. `attrs` are the attributes the tag has (``{}`` for an added one);
    `inner` is its current content (already XML), used when the layout brings no ``text``."""
    style = box.get("style") or {}
    align = style.get("align") or _ANCHORS.get((_css_prop(attrs, "text-anchor") or "").strip(), "left")
    x = {"left": box["x"], "center": box["x"] + box["w"] / 2, "right": box["x"] + box["w"]}[align]
    height = style.get("lineHeight", DEFAULT_LINE_HEIGHT)
    if "text" in box:
        lines = [xml_escape(ln) for ln in box["text"].replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    else:
        lines = [re.sub(r"<[^>]*>", "", inner or "").strip()]
    content = "".join('<tspan x="%s" dy="%s">%s</tspan>' % (_num(x), "0" if i == 0 else _num(height * size), ln)
                      for i, ln in enumerate(lines))
    css = ["font-size:%spx" % _num(size), "text-anchor:%s" % {v: k for k, v in _ANCHORS.items()}[align]]
    if "family" in style:
        css.append("font-family:&quot;%s&quot;" % style["family"])
    if "weight" in style:
        css.append("font-weight:%d" % style["weight"])
    if "italic" in style:
        css.append("font-style:%s" % ("italic" if style["italic"] else "normal"))
    if "color" in style:
        css.append("fill:%s" % style["color"])
    values = {"x": _num(x), "y": _num(box["y"] + size), "data-gimg-box": "%d %d %d %d" % (box["x"], box["y"], box["w"], box["h"])}
    if "color" in style:
        values["data-gimg-color"] = style["color"]
    return values, ";".join(css), content


def _added_xml(name, box, size) -> str:
    values, css, content = _text_paint(dict(box, _name=name), name, {}, size)
    values = {"id": ELEMENT_PREFIX + name, "data-gimg-box": values.pop("data-gimg-box"), **values}
    return "<text %s style=\"%s\">%s</text>" % (" ".join('%s="%s"' % kv for kv in values.items()), css, content)


def _apply_tagged(svg_text, layout, target, sizes=None):
    """`_apply` with the ``_tag`` of each element kept in `found`. `sizes` (``{name: size}``) replaces the size an
    element with ``text`` or ``style`` is painted with (`render` shrinks what does not fit)."""
    found = _elements(svg_text, target)
    if isinstance(layout, dict) and any(isinstance(b, dict) and "add" in b for b in layout.values()) \
            and viewbox_of(svg_text) != (0.0, 0.0, float(target[0]), float(target[1])):
        raise GimgError("compose.bad_layout", element="", reason="the template viewBox is not %dx%d" % tuple(target))
    moved = _check_layout(found, layout, target)
    edits = []
    for e in found:
        box = moved.get(e["id"])
        if box is None:
            continue
        m, attrs = e["_tag"]
        o = e["box"]
        painting = "text" in box or bool(box.get("style"))
        new_style = attrs["style"][0] if "style" in attrs else None
        new_attrs = {}
        if painting:
            size = _text_size(attrs, dict(box, _name=e["id"]), sizes)
            end = svg_text.find("</text>", m.end()) if not m.group(3) else -1
            if not m.group(3) and end < 0:
                raise GimgError("compose.bad_layout", element=e["id"], reason="the <text> is not closed")
            inner = "" if m.group(3) else svg_text[m.end():end]
            values, css, content = _text_paint(box, e["id"], attrs, size, inner)
            new_attrs.update(values)
            new_style = (new_style or "").rstrip().rstrip(";") + (";" if new_style and new_style.strip() else "") + css
            if m.group(3):
                edits.append((m.end(2), m.end(), ">" + content + "</text>"))
            else:
                edits.append((m.end(), end, content))
        elif {k: box[k] for k in ("x", "y", "w", "h")} != o:  # hidden alone leaves the box and the transform as they were
            move = "translate(%s %s) scale(%s %s) translate(%s %s)" % (
                box["x"], box["y"], _num(box["w"] / o["w"]), _num(box["h"] / o["h"]), -o["x"], -o["y"])
            if "transform" in attrs:
                value, start, end, _quote = attrs["transform"]
                edits.append((start, end, (move + " " + value).strip()))
            else:
                new_attrs["transform"] = move
            new_attrs["data-gimg-box"] = "%d %d %d %d" % (box["x"], box["y"], box["w"], box["h"])
        if "hidden" in box:
            word = "none" if box["hidden"] else "inline"
            sm = _STYLE_DISPLAY.search(new_style) if new_style else None
            if sm:  # a display inside style beats the attribute: write it there too
                new_style = new_style[:sm.start(2)] + word + new_style[sm.end(2):]
            if "display" in attrs:
                _value, start, end, _quote = attrs["display"]
                edits.append((start, end, word))
            elif box["hidden"] and not sm:
                new_attrs["display"] = "none"
        if new_style is not None and new_style != (attrs["style"][0] if "style" in attrs else None):
            if "style" in attrs:
                _value, start, end, _quote = attrs["style"]
                edits.append((start, end, new_style))
            else:
                new_attrs["style"] = new_style
        inserted = ""
        for key, value in new_attrs.items():
            if key in attrs and key != "style":
                _value, start, end, _quote = attrs[key]
                edits.append((start, end, value))
            elif key not in attrs:
                inserted += ' %s="%s"' % (key, value)
        if inserted:
            edits.append((m.end(2), m.end(2), inserted))
    adds = sorted((n for n, b in moved.items() if b.get("add")), key=lambda n: int(n[len(ADDED_PREFIX):]))
    if adds:
        close = svg_text.rfind("</svg>")
        if close < 0:
            raise GimgError("compose.bad_layout", element=adds[0], reason="the template has no </svg>")
        edits.append((close, close, "".join(_added_xml(n, moved[n], (sizes or {}).get(n) or moved[n]["style"]["size"])
                                            for n in adds)))
    out = svg_text
    for start, end, text in sorted(edits, key=lambda ed: (ed[0], ed[1]), reverse=True):
        out = out[:start] + text + out[end:]
    return out, moved, found


def _apply(svg_text, layout, target, sizes=None):
    """``(svg, moved, found)``: `svg_text` with the moved elements transformed, what moved and the elements read."""
    out, moved, found = _apply_tagged(svg_text, layout, target, sizes)
    return out, moved, [{k: v for k, v in e.items() if k != "_tag"} for e in found]


def apply_layout(svg_text, layout, target, sizes=None) -> str:
    """`svg_text` with the elements of `layout` (``{name: {x, y, w, h, hidden?, text?, style?}}``, integers, the box inside
    `target`) moved (and, with ``"hidden": true``, given ``display="none"``): the opening tag of each gets
    ``transform="translate(x y) scale(w/w0 h/h0) translate(-x0 -y0)"`` in front of the ``transform`` it had, and its
    ``data-gimg-box`` is rewritten. The rest of the SVG is not touched (it is not parsed as XML).

    An element with ``text`` or ``style`` (F4e.2, a ``<text>`` only) is not scaled: its box is a frame. The tag gets the
    ``x``, ``y`` and ``data-gimg-box`` of the frame and the style (font, size, weight, italic, ``fill``, ``text-anchor``)
    appended to its ``style`` attribute, so it beats the attributes and a ``<style>`` sheet; ``color`` is also
    ``data-gimg-color``. The content is rewritten as one ``<tspan>`` per line of ``text`` (escaped; without ``text`` the
    current content, as one line) with the first baseline at ``box.y + size`` and ``dy = lineHeight x size`` (1.2 by
    default). `size` is ``style.size``, else the ``font-size`` of the element, else 16; `sizes` (``{name: size}``)
    overrides it. An entry ``{"add": true, x, y, w, h, text, style}`` named ``extra<N>`` inserts
    ``<text id="gimg-extra<N>">`` before the final ``</svg>`` (up to 10). ``compose.element_unknown`` /
    ``compose.bad_layout`` / ``compose.bad_element`` on failure."""
    return _apply(svg_text, layout, target, sizes)[0]


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
    the ``style.color`` of the layout, else the element's ``data-gimg-color``, else the template's ``textColor``; an
    added text is measured too. An element without colour, or whose measure fails, is left out (a measure never fails
    a composition)."""
    out = {}
    candidates = list(found) + [{"id": n, "kind": "text", "box": b} for n, b in moved.items() if b.get("add")]
    for e in candidates:
        color = (moved.get(e["id"], {}).get("style") or {}).get("color") or e.get("color") or compose_cfg.get("textColor")
        if e["kind"] != "text" or not color or moved.get(e["id"], {}).get("hidden"):
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


# --- fonts, and fitting the text into its box (F4e.2) ---
def families_status():
    """``(families, reason)``: the font families ``fc-list : family`` knows, sorted and without repeats (an entry such as
    ``A,B`` is two), and ``None``; or ``None`` and why it cannot tell (``"not_found"`` when ``fc-list`` is not in PATH,
    else what failed: the error, the time limit, the last line of its stderr or the exit code)."""
    exe = shutil.which("fc-list")
    if exe is None:
        return None, "not_found"
    try:
        done = subprocess.run([exe, ":", "family"], capture_output=True, text=True, errors="replace",
                              timeout=30, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, "timeout after 30s"
    except (OSError, subprocess.SubprocessError) as exc:
        return None, str(getattr(exc, "strerror", None) or exc)[:300]
    if done.returncode != 0:
        err = done.stderr if isinstance(done.stderr, str) else ""
        lines = [ln.strip() for ln in err.splitlines() if ln.strip()]
        return None, (lines[-1][:300] if lines else "exit code %d" % done.returncode)
    return sorted({n.strip() for line in done.stdout.splitlines() for n in line.split(",") if n.strip()}), None


def installed_families():
    """The font families ``fc-list`` knows (`families_status`), or ``None`` if it is missing or fails."""
    return families_status()[0]


def fonts_report(project=None) -> dict:
    """What ``GET /api/fonts`` and ``gimg fonts`` answer (F4e.2b): ``{"installed": [family], "available": bool,
    "reason": str|None, "projects": [{"project", "profiles": [{"profile", "fonts": [{"name", "installed": bool|None}]}]}]}``.
    The fonts of a profile are its ``compose.fonts`` plus the ``fonts`` of every template saved for it, without repeats;
    `installed` is ``None`` for all of them when ``fc-list`` cannot tell (``available`` false, ``reason`` says why:
    ``not_found`` or the failure). `project` limits the report to that project (``project.unknown`` if it is not
    registered); a project whose configuration does not load has ``"error"`` (the error body) instead of ``profiles``."""
    families, reason = families_status()
    have = None if families is None else {f.lower() for f in families}
    names = [project] if project else list(projects.list_projects())
    out = []
    for name in names:
        try:
            proj = projects.get(name)
        except GimgError as exc:
            if project:
                raise
            out.append({"project": name, "error": {"code": exc.code, "params": exc.params}, "profiles": []})
            continue
        profiles = []
        for pname, pcfg in proj["config"]["profiles"].items():
            if not pcfg.get("compose"):
                continue
            wanted = list((pcfg["compose"]).get("fonts") or [])
            try:
                for src in template_sources(proj, pname):
                    wanted += [f for f in (src["entry"].get("fonts") or []) if f not in wanted]
            except (GimgError, OSError, ValueError):
                pass
            profiles.append({"profile": pname, "fonts": [
                {"name": f, "installed": None if have is None else f.lower() in have} for f in dict.fromkeys(wanted)]})
        out.append({"project": name, "profiles": profiles})
    return {"installed": families or [], "available": families is not None, "reason": reason, "projects": out}


def families_of(layout) -> list:
    """The ``style.family`` names a layout uses, sorted and without repeats."""
    return sorted({b["style"]["family"] for b in (layout or {}).values()
                   if isinstance(b, dict) and isinstance(b.get("style"), dict) and "family" in b["style"]})


def _missing_fonts(moved) -> list:
    used = families_of({n: b for n, b in moved.items() if not b.get("hidden")})
    installed = installed_families() if used else None
    if installed is None:
        return []
    have = {f.lower() for f in installed}
    return [f for f in used if f.lower() not in have]


def _solo_svg(svg, name, target):
    """An SVG with the root tag, the ``<style>``/``<defs>`` blocks and only the text element `name` of `svg`."""
    root = next(m for m, _attrs in _tags(svg) if m.group(1) == "svg")
    element = next(e for e in _elements(svg, target) if e["id"] == name)
    start = element["_tag"][0].start()
    end = svg.index("</text>", start) + len("</text>")
    blocks = "".join(m.group(0) for m in re.finditer(r"<(style|defs)\b.*?</\1>", svg, re.S | re.I))
    return svg[:0] + root.group(0) + blocks + svg[start:end] + "</svg>"


def _alpha_box(data, width, height):
    """``(x0, y0, x1, y1)`` (end excluded) of the pixels of an RGBA buffer whose alpha is not 0, or ``None``."""
    alpha = data[3::4]
    x0, x1, y0, y1 = width, 0, None, 0
    for y in range(height):
        row = alpha[y * width:(y + 1) * width]
        if not row.strip(b"\0"):
            continue
        y0 = y if y0 is None else y0
        y1 = y + 1
        x0 = min(x0, width - len(row.lstrip(b"\0")))
        x1 = max(x1, len(row.rstrip(b"\0")))
    return None if y0 is None else (x0, y0, x1, y1)


def _text_extent(substituted, name, box, size, target, tmp):
    """The pixel box of the text element `name` painted alone at `size` (``None`` if it paints nothing)."""
    entry = {k: v for k, v in box.items() if k != "hidden"}
    svg, _moved, _found = _apply_tagged(substituted, {name: entry}, target, {name: size})
    solo, png_path = Path(tmp) / "fit.svg", Path(tmp) / "fit.png"
    solo.write_text(_solo_svg(svg, name, target), encoding="utf-8")
    _run(rsvg_argv(solo, png_path, target[0], target[1]), "rsvg-convert")
    data = measure._run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(png_path), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                        "ffmpeg")
    if len(data) != target[0] * target[1] * 4:
        raise GimgError("compose.tool_failed", tool="ffmpeg", reason="unexpected size")
    return _alpha_box(data, target[0], target[1])


def _fits(extent, box) -> bool:
    return extent is None or (extent[0] >= box["x"] - 1 and extent[1] >= box["y"] - 1
                              and extent[2] <= box["x"] + box["w"] + 1 and extent[3] <= box["y"] + box["h"] + 1)


def _fit_texts(substituted, moved, tagged, target, tmp):
    """``(fitted, overflow)`` for the elements of `moved` with ``text`` or ``style``: each is painted alone and its
    pixels measured (`_text_extent`). One that sticks out of its box is painted again smaller, in proportion, down to
    ``max(8, size // 2)``; a third try at that minimum if the proportional one still does not fit. ``fitted`` is
    ``{name: size painted}``; ``overflow`` is ``{name: {"size": asked, "min": minimum}}`` for those that do not fit even
    at the minimum. An element whose measure fails (no tool, bad SVG) is left out of both and painted as asked."""
    fitted, overflow = {}, {}
    for name, box in moved.items():
        if box.get("hidden") or not ("text" in box or box.get("style")):
            continue
        tag = tagged.get(name)
        asked = (box.get("style") or {}).get("size") or (_base_size(tag["_tag"][1]) if tag else DEFAULT_SIZE)
        least = min(asked, max(8, asked // 2))
        try:
            extent = _text_extent(substituted, name, box, asked, target, tmp)
            if _fits(extent, box):
                fitted[name] = asked
                continue
            ratio = min(box["w"] / max(1, extent[2] - extent[0]), box["h"] / max(1, extent[3] - extent[1]))
            size = max(least, min(asked - 1, int(asked * ratio)))
            if asked > least and not _fits(_text_extent(substituted, name, box, size, target, tmp), box):
                size = least
                if size < asked and _fits(_text_extent(substituted, name, box, size, target, tmp), box):
                    fitted[name] = size
                    continue
            elif asked > least:
                fitted[name] = size
                continue
        except (GimgError, OSError, ValueError, StopIteration):
            continue
        fitted[name] = least
        overflow[name] = {"size": asked, "min": least}
    return fitted, overflow


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
    moved, found, tagged, substituted = {}, [], {}, None
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
        layer_svg = substituted = substitute(source, values)
        try:
            layer_svg, moved, found_tagged = _apply_tagged(layer_svg, layout or {}, (width, height))
            tagged = {e["id"]: e for e in found_tagged}
            found = [{k: v for k, v in e.items() if k != "_tag"} for e in found_tagged]
        except GimgError as exc:
            if exc.code == "compose.bad_element" and not layout:
                found = []
            else:
                raise
    elif layout:
        _check_layout([], layout, (width, height), adds=False)
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
        missing = _missing_fonts(moved)
        if missing:
            info["missingFonts"] = missing
    try:
        with tempfile.TemporaryDirectory(dir=str(out_path.parent), prefix=prefix) as tmp:
            tmp = Path(tmp)
            layer = None
            if layer_svg is not None:
                fitted, overflow = _fit_texts(substituted, moved, tagged, (width, height), tmp)
                if fitted:
                    info["fitted"] = fitted
                    # always repaint: an element without its own ``style.size`` was asked at the template's size
                    layer_svg = _apply_tagged(substituted, layout or {}, (width, height), fitted)[0]
                if overflow:
                    info["overflow"] = overflow
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
    The attempt's ``compose`` also keeps what `render` measured of the edited texts (F4e.2): ``fitted``, ``overflow``
    and ``missingFonts``.

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
        _check_layout([], layout, (0, 0), adds=False)
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
        svg = apply_layout(svg, layout, target_size(profile_cfg), sizes=stored.get("fitted"))
    if dest == "project":
        folder = project_templates_dir(proj["root"], compose_cfg, profile)
    else:
        folder = local_templates_dir(project, profile)
    svg_path, json_path = paths.inside(folder, name + ".svg"), paths.inside(folder, name + ".json")
    sidecar = {"base": base, **{k: cfg[k] for k in ("logo", "fields", "zone", "textColor") if k in cfg}}
    used = families_of(layout)[:MAX_FONTS]
    if used:
        sidecar["fonts"] = used
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


def _template_files(proj, profile, template_id) -> dict:
    """Where the template `template_id` of `profile` lives as files, and everything that decides if it can be deleted
    (F4e.1, D41): ``{"id", "source", "svg", "json", "usedBy", "inRepo"}``. Raises ``compose.bad_name`` (not an id),
    ``compose.delete_default`` (``default``, or the file is the ``template`` of ``compose`` or of a ``compose.templates``
    entry of any profile), ``compose.delete_config`` (declared in ``compose.templates``: there is no file of its own),
    ``compose.delete_symlink`` (the .svg or .json is a link: never followed, never deleted), ``compose.delete_unknown`` (no such template in the folders), ``order.profile_unknown`` and ``path.*`` (the folder
    leaves the project: D25). Nothing is changed. ``usedBy`` counts the attempts (``compose.templateId`` or
    ``composeError.templateId``) of every order of the profile that have it."""
    if template_id == DEFAULT_TEMPLATE:
        raise GimgError("compose.delete_default", template=template_id)
    if not isinstance(template_id, str) or not _TEMPLATE_ID.fullmatch(template_id):
        raise GimgError("compose.bad_name", name=str(template_id)[:60])
    if proj["config"]["profiles"].get(profile) is None:
        raise GimgError("order.profile_unknown", profile=profile)
    cfg = proj["config"]["profiles"][profile].get("compose")
    if not cfg:
        raise GimgError("compose.delete_unknown", template=template_id, profile=profile)
    if template_id in (cfg.get("templates") or {}):
        raise GimgError("compose.delete_config", template=template_id)
    found = None
    folder = project_templates_dir(proj["root"], cfg, profile)  # raises path.* if templatesDir leaves the project
    for source, where in (("project", folder), ("local", local_templates_dir(proj["name"], profile))):
        if where is None:
            continue
        where = Path(where).resolve()  # the folder resolved, the name added: a link is never followed to its target
        if (where / (template_id + ".svg")).is_symlink() or (where / (template_id + ".json")).is_symlink():
            raise GimgError("compose.delete_symlink", template=template_id)
        if (where / (template_id + ".svg")).is_file():
            found = (source, where)
            break
    if found is None:
        raise GimgError("compose.delete_unknown", template=template_id, profile=profile)
    source, folder = found
    if source == "project":
        own = posixpath.normpath(paths.check_relative(cfg["templatesDir"]).rstrip("/") + "/" + profile + "/"
                                 + template_id + ".svg")
        for other in proj["config"]["profiles"].values():  # any profile may point at this file as its template
            ccfg = other.get("compose") or {}
            for ref in [ccfg.get("template")] + [(e or {}).get("template") for e in (ccfg.get("templates") or {}).values()]:
                if isinstance(ref, str) and posixpath.normpath(paths.check_relative(ref)) == own:
                    raise GimgError("compose.delete_default", template=template_id)
    used = 0
    for order in orders.list_orders(proj["name"], profile):
        for attempt in order["attempts"]:
            stored = attempt.get("compose") or attempt.get("composeError") or {}
            used += stored.get("templateId") == template_id
    return {"id": template_id, "source": source, "svg": folder / (template_id + ".svg"),
            "json": folder / (template_id + ".json"), "usedBy": used, "inRepo": source == "project"}


def template_usage(project, profile, template_id) -> dict:
    """What deleting the template `template_id` of `profile` would do, without doing it: ``{"id", "source", "usedBy",
    "inRepo"}`` (``inRepo``: the files are in the project's repository, so the change stays there uncommitted).
    Raises what `delete_template` raises."""
    found = _template_files(projects.get(project), profile, template_id)
    return {k: found[k] for k in ("id", "source", "usedBy", "inRepo")}


def delete_template(project, profile, template_id) -> dict:
    """Delete the template `template_id` of `profile` for good (F4e.1, D41): its ``.svg`` and its ``.json``, in the
    local folder or in ``<compose.templatesDir>/<profile>/`` (only there, behind `paths.inside`). Returns ``{"id",
    "source", "files", "usedBy", "inRepo"}``; the attempts that had it keep their ``templateId`` (composing them again
    fails with ``compose.template_unknown`` until it is back). A line ``template.delete`` goes to the project log.
    Errors: those of `template_usage`."""
    proj = projects.get(project)
    found = _template_files(proj, profile, template_id)
    removed = 0
    try:
        found["json"].unlink()  # the sidecar first: if the svg then fails, the template is still whole and listed
        removed += 1
    except FileNotFoundError:
        pass  # it never had one
    found["svg"].unlink()  # a failure here goes up: nothing is answered nor logged as deleted
    removed += 1
    log.append(project, log.template_delete_record(profile, template_id, found["source"], removed, found["usedBy"]))
    return {"id": template_id, "source": found["source"], "files": removed, "usedBy": found["usedBy"],
            "inRepo": found["inRepo"]}


__all__ = ["recompose", "render", "effective", "templates_of", "templates_with_elements", "merged_profile", "template_sources", "installed_families", "save_template", "delete_template", "template_usage",
           "elements", "apply_layout", "zone_to_raw", "viewbox_of", "DEFAULT_TEMPLATE", "plan_for", "target_size", "fit_geometry", "substitute", "xml_escape", "resolve_assets",
           "logo_data_uri", "rsvg_argv", "ffmpeg_argv", "TIMEOUT_S", "MAX_SVG_BYTES"]
