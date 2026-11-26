"""Brand sheet as data (D41): load, inherit, derive the palette, assemble and lint prompts.

Every function here is pure apart from reading the sheet files. The sheet is `marca.json` of a project,
linked from `brand.sheet` in its config and validated by `schemas/brand-sheet.schema.json`.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from pathlib import Path

from . import fsutil, i18n, measure, paths, projects, schema
from .errors import GimgError

ROLES = ("paper", "ink", "accent", "halo", "grid")
REQUIRED = ("palette.paper", "palette.ink", "palette.accent", "registers", "closing", "paletteSentence")
DEFAULT_WORDS = {"min": 120, "max": 200}
NEGATIONS = ("no", "not", "without")

# Accent tones (docs/marcas/portal/hoja.md, «Decisiones de la persona (2026-11-12)», point 1): hue and OKLCH chroma
# fixed, lightness moved in 0.005 steps until the first hex with WCAG 2.x contrast >= 4.5:1 on the paper.
PAPER_LIGHT = "#fbfcfd"
PAPER_DARK = "#0d171e"
TONE_STEP = 0.005
TONE_THRESHOLD = 4.5
_EPS = 1e-6
_HEX = re.compile(r"#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|(?=[0-9]*[A-Fa-f])[0-9A-Fa-f]{4}|(?=[0-9]*[A-Fa-f])[0-9A-Fa-f]{3})(?![0-9A-Za-z])")
_HEX_FULL = re.compile(r"#?[0-9A-Fa-f]{6}")
_PLACEHOLDER = re.compile(r"\{([A-Za-z]+)\}")


# --- loading and inheritance ------------------------------------------------------------------------------------

def load(path) -> dict:
    """Read and validate one sheet file (not resolved: `extends` is left as is)."""
    path = Path(path)
    try:
        data = fsutil.read_json(path)
    except FileNotFoundError:
        raise GimgError("brandsheet.missing", path=str(path))
    except (OSError, ValueError) as exc:
        raise GimgError("brandsheet.unreadable", path=str(path), reason=str(exc))
    errors = schema.validate(data, schema.load_schema("brand-sheet"))
    if errors:
        raise GimgError("brandsheet.invalid", errors=errors, path=str(path))
    return data


def _project_sheet(name: str, child: str | None = None) -> dict:
    """The raw sheet of registered project `name`, read inside its root (D25)."""
    try:
        project = projects.get(name)
    except GimgError as exc:
        if child is not None and exc.code == "project.unknown":
            raise GimgError("brandsheet.extends_missing", project=child, parent=name)
        if child is not None and exc.code.startswith("project.config_"):
            raise GimgError("brandsheet.extends_broken", project=child, parent=name,
                            reason=exc.message().replace("\n", " "))
        raise
    rel = project["config"].get("brand", {}).get("sheet")
    if rel is None:
        if child is not None:
            raise GimgError("brandsheet.extends_missing", project=child, parent=name)
        raise GimgError("brandsheet.none", project=name)
    if child is None:
        return load(paths.inside(project["root"], rel))
    try:
        return load(paths.inside(project["root"], rel))
    except GimgError as exc:
        # the parent's file is the broken one, not the child's sheet: say so (review paso 2, point 1)
        if exc.code.startswith("brandsheet."):  # path.* (D25) keeps its own code
            raise GimgError("brandsheet.extends_broken", project=child, parent=name,
                            reason=exc.message().replace("\n", " "))
        raise


def _leaves(value, prefix, out):
    if isinstance(value, dict) and value:
        for key, item in value.items():
            _leaves(item, "%s.%s" % (prefix, key) if prefix else key, out)
    else:
        out.append(prefix)


def _owned(sheet: dict, offset: int = 0) -> list:
    """Field paths a sheet declares itself (groups by id, exceptions by position in the merged list, after
    the `offset` exceptions of the sheets it extends)."""
    body = {k: v for k, v in sheet.items() if k not in ("$schema", "schemaVersion", "name", "extends")}
    vetoes = body.get("vetoes", {})
    groups, exceptions = vetoes.get("groups"), vetoes.get("exceptions")
    body = copy.deepcopy(body)
    if groups is not None:
        body["vetoes"]["groups"] = {g["id"]: g for g in groups}
    if exceptions is not None:
        body["vetoes"]["exceptions"] = {str(offset + i): e for i, e in enumerate(exceptions)}
    out = []
    _leaves(body, "", out)
    return [p for p in out if p]


def _merge(base, over):
    """Deep merge: objects merge, lists replace; vetoes.groups merge by id, vetoes.exceptions add up.
    Inheritance only adds or overrides: a child sheet cannot delete a key it inherits."""
    result = copy.deepcopy(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _merge_sheets(parent: dict, child: dict) -> dict:
    merged = _merge(parent, {k: v for k, v in child.items() if k != "vetoes"})
    pv, cv = parent.get("vetoes", {}), child.get("vetoes", {})
    vetoes = _merge(pv, {k: v for k, v in cv.items() if k not in ("groups", "exceptions")})
    groups = [copy.deepcopy(g) for g in pv.get("groups", [])]
    index = {g["id"]: i for i, g in enumerate(groups)}
    for group in cv.get("groups", []):
        if group["id"] in index:
            groups[index[group["id"]]] = _merge(groups[index[group["id"]]], group)
        else:
            index[group["id"]] = len(groups)
            groups.append(copy.deepcopy(group))
    if groups:
        vetoes["groups"] = groups
    exceptions = pv.get("exceptions", []) + cv.get("exceptions", [])
    if exceptions:
        vetoes["exceptions"] = copy.deepcopy(exceptions)
    if vetoes:
        merged["vetoes"] = vetoes
    return merged


def _get(sheet, dotted):
    node = sheet
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _check_resolved(sheet: dict, project: str) -> None:
    for field in REQUIRED:
        if not _get(sheet, field):
            raise GimgError("brandsheet.incomplete", project=project, field=field)
    def check_placeholders(text, where):
        for name in _PLACEHOLDER.findall(text):
            if name not in ROLES or name not in sheet["palette"]:
                raise GimgError("brandsheet.bad_placeholder", project=project, placeholder=name, where=where)

    check_placeholders(sheet["paletteSentence"], "paletteSentence")
    for piece, spec in sheet.get("pieceTypes", {}).items():
        if spec["register"] not in sheet["registers"]:
            raise GimgError("brandsheet.unknown_register", project=project, piece=piece, register=spec["register"])
        check_placeholders(spec.get("paletteSentence", ""), "pieceTypes.%s.paletteSentence" % piece)
    words = sheet.get("promptWords")
    if words and words["min"] > words["max"]:
        raise GimgError("brandsheet.incomplete", project=project, field="promptWords")
    for piece, spec in sheet.get("pieceTypes", {}).items():
        words = spec.get("promptWords")
        if words and words["min"] > words["max"]:
            raise GimgError("brandsheet.incomplete", project=project, field="pieceTypes.%s.promptWords" % piece,
                            piece=piece)


def canonical(sheet: dict) -> bytes:
    """Canonical JSON bytes of a sheet (sorted keys, no spaces), the input of its version hash."""
    return json.dumps(sheet, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def resolve(project_name: str) -> dict:
    """Resolved sheet of a registered project, following `extends` by registered project name.

    Each sheet is read inside its own project root (D25). Returns the merged sheet (without `extends`) plus
    `chain` (project names, child first), `origin` (dotted field path -> {"origin": "own"|"inherited",
    "project": owner}) and `version` (first 12 hex digits of the sha256 of the canonical merged sheet)."""
    chain, sheets = [], []
    name, child = project_name, None
    while name is not None:
        if name in chain:
            raise GimgError("brandsheet.extends_cycle", project=project_name, chain=" -> ".join(chain + [name]))
        chain.append(name)
        sheet = _project_sheet(name, child)
        sheets.append(sheet)
        child, name = name, sheet.get("extends")
    merged, origin, shift = {}, {}, 0
    for owner, sheet in reversed(list(zip(chain, sheets))):
        merged = _merge_sheets(merged, sheet)
        for field in _owned(sheet, shift):
            origin[field] = {"origin": "own" if owner == project_name else "inherited", "project": owner}
        shift += len(sheet.get("vetoes", {}).get("exceptions", []))
    merged["schemaVersion"] = sheets[0]["schemaVersion"]
    merged["name"] = sheets[0]["name"]
    merged.pop("extends", None)
    merged.pop("$schema", None)
    _check_resolved(merged, project_name)
    version = hashlib.sha256(canonical(merged)).hexdigest()[:12]
    merged.update(chain=chain, origin=dict(sorted(origin.items())), version=version)
    return merged


# --- colour -----------------------------------------------------------------------------------------------------

def _rgb(value):
    if not isinstance(value, str) or not _HEX_FULL.fullmatch(value):
        raise GimgError("brandsheet.bad_hex", value=str(value))
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _to_hex(rgb):
    return "#" + "".join("%02x" % min(255, max(0, round(c * 255))) for c in rgb)


def _linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gamma(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _luminance(value):
    r, g, b = (_linear(c) for c in _rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two #rrggbb colours."""
    return measure.contrast_ratio(_luminance(a), _luminance(b))


def _oklch(value):
    r, g, b = (_linear(c) for c in _rgb(value))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b2 = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return lightness, math.hypot(a, b2), math.atan2(b2, a)


def _oklch_hex(lightness, chroma, hue):
    """Hex of an OKLCH colour, lowering the chroma in steps until it fits in sRGB."""
    c = chroma
    while True:
        a, b = c * math.cos(hue), c * math.sin(hue)
        l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
        linear = (
            4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
        )
        if all(-_EPS <= v <= 1 + _EPS for v in linear) or c <= 0:
            return _to_hex(tuple(_gamma(min(1.0, max(0.0, v))) for v in linear))
        c = max(0.0, c - TONE_STEP)


def _tone(vivid, paper, direction):
    if _luminance(paper) < 0.18:  # a dark paper needs the lighter tone whatever the theme asked for
        direction = +1
    lightness, chroma, hue = _oklch(vivid)
    if contrast(vivid, paper) >= TONE_THRESHOLD:
        return vivid.lower()
    while 0.0 <= lightness <= 1.0:
        lightness += direction * TONE_STEP
        candidate = _oklch_hex(lightness, chroma, hue)
        if contrast(candidate, paper) >= TONE_THRESHOLD:
            return candidate
    raise GimgError("brandsheet.no_tone", value=vivid, paper=paper)


def accent_tones(hex_value: str, paper: str = PAPER_LIGHT, dark_paper: str = PAPER_DARK) -> dict:
    """Deep (light theme) and dark-theme tones of an accent: {"deep": hex, "dark": hex}.

    Same method as `docs/marcas/*/tonos.py`: OKLCH hue and chroma fixed (chroma lowered only to stay in sRGB),
    lightness moved down (deep, on `paper`) or up (dark, on `dark_paper`) in 0.005 steps until contrast >= 4.5:1;
    a vivid colour that already passes is its own tone."""
    _rgb(paper), _rgb(dark_paper)
    return {"deep": _tone(hex_value, paper, -1), "dark": _tone(hex_value, dark_paper, +1)}


def _value(token):
    return token["$value"].lower() if token else None


def _tones(pal: dict) -> dict | None:
    """Accent tones of a palette on its own papers (the defaults without them); None without accent or tone."""
    if not pal.get("accent"):
        return None
    try:
        return accent_tones(pal["accent"]["$value"], _value(pal.get("paper")) or PAPER_LIGHT,
                            _value(pal.get("dark", {}).get("paper")) or PAPER_DARK)
    except GimgError as exc:
        if exc.code != "brandsheet.no_tone":
            raise
        return None


def palette(sheet: dict) -> list:
    """Hex list for `brand.palette` / `measure`: roles, accent tones, dark version and measureOnly, no duplicates."""
    pal = sheet.get("palette", {})
    dark = pal.get("dark", {})
    found = [_value(pal.get(role)) for role in ROLES]
    tones = _tones(pal)
    if tones:
        found += [tones["deep"], tones["dark"]]
    found += [_value(dark.get("paper")), _value(dark.get("ink"))]
    found += [h.lower() for h in pal.get("measureOnly", [])]
    out = []
    for value in found:
        if value and value not in out:
            out.append(value)
    return out


def palette_sentence(sheet: dict, spec: dict | None = None) -> str:
    """The palette sentence (the piece type's own if it has one) with each {role} replaced by «promptName #hex»."""
    def fill(match):
        token = sheet["palette"][match.group(1)]
        name = token.get("promptName")
        return "%s %s" % (name, token["$value"].lower()) if name else token["$value"].lower()
    return _sentence(_PLACEHOLDER.sub(fill, (spec or {}).get("paletteSentence") or sheet["paletteSentence"]))


# --- prompt -----------------------------------------------------------------------------------------------------

def _sentence(text: str) -> str:
    text = " ".join(text.split())
    return text if not text or text[-1] in ".!?" else text + "."


def _piece(sheet, piece):
    spec = sheet.get("pieceTypes", {}).get(piece)
    if spec is None:
        raise GimgError("brandsheet.unknown_piece", piece=str(piece))
    return spec


def _closing(sheet, spec):
    """Closing of the piece type, or the sheet's."""
    return (spec or {}).get("closing") or sheet["closing"]


def _zone_after(spec):
    """True when the piece type puts the clean zone at the end of the closing (`cleanZone: "afterClosing"`)."""
    return (spec or {}).get("cleanZone") == "afterClosing"


def assemble(sheet: dict, piece: str, subject: str, clean_zone: str | None = None) -> dict:
    """Prompt in the sheet order: subject -> clean zone -> register block of the piece -> closing -> palette.

    The piece type may carry its own closing and palette sentence, and with `cleanZone: "afterClosing"` the clean
    zone is not a sentence before the register but the end of the closing sentence: the closing loses its full stop
    and goes on after a comma with the zone text as given (it should start in lower case), as its own segment.

    Returns {"prompt", "words", "segments": [{"role", "text", "source"}]}; each segment ends in a full stop (the
    closing before an after-closing zone, in a comma) and segments are joined with one space."""
    spec = _piece(sheet, piece)
    clean_zone = (clean_zone or "").strip() or None  # a zone of only spaces is no zone
    segments = [{"role": "subject", "text": _sentence(subject), "source": "input"}]
    after = bool(clean_zone) and _zone_after(spec)
    if clean_zone and not after:
        segments.append({"role": "cleanZone", "text": _sentence(clean_zone), "source": "input"})
    closing = _closing(sheet, spec)
    segments += [
        {"role": "register", "text": _sentence(sheet["registers"][spec["register"]]["block"]),
         "source": "registers." + spec["register"]},
        {"role": "closing", "text": _sentence(closing), "source": "pieceTypes.%s.closing" % piece
         if spec.get("closing") else "closing"},
    ]
    if after:
        # the zone is the person's own segment: the closing loses its full stop and ends in a comma, the zone
        # follows it and takes the full stop, so the joined text is «closing, zone.»
        segments[-1]["text"] = " ".join(closing.split()).rstrip(".!?") + ","
        segments.append({"role": "cleanZone", "text": _sentence(clean_zone), "source": "input"})
    segments.append({"role": "palette", "text": palette_sentence(sheet, spec),
                     "source": "pieceTypes.%s.paletteSentence" % piece if spec.get("paletteSentence")
                     else "paletteSentence"})
    segments = [s for s in segments if s["text"]]
    prompt = " ".join(s["text"] for s in segments)
    return {"prompt": prompt, "words": len(prompt.split()), "segments": segments}


def _norm(text):
    return " ".join(text.split()).lower()


def _find(prompt, needle):
    """Span of `needle` in `prompt` ignoring case and runs of whitespace (trailing full stop optional), or None."""
    spans = _find_all(prompt, needle)
    return spans[0] if spans else None


def _find_all(prompt, needle):
    """Every span of `needle` in `prompt` (same matching as `_find`)."""
    words = needle.strip().rstrip(".").split()
    if not words:
        return []
    return [[m.start(), m.end()] for m in re.finditer(r"\s+".join(re.escape(w) for w in words), prompt, re.IGNORECASE)]


def _word_spans(prompt, term):
    words = term.split()
    pattern = r"(?<!\w)" + r"\s+".join(re.escape(w) for w in words) + r"(?:e?s)?(?!\w)"
    return [[m.start(), m.end()] for m in re.finditer(pattern, prompt, re.IGNORECASE)]


def _inside(span, areas):
    return any(a[0] <= span[0] and span[1] <= a[1] for a in areas)


def lint(sheet: dict, prompt: str, piece: str | None = None, mode: str = "brand",
         clean_zone: str | None = None) -> dict:
    """Check a prompt against a resolved sheet.

    Returns {"checks": [{"id", "status": ok|warn|error, "message": {"key", "params"}, "span"?: [i, j]}],
    "blocked"}. Check ids: words, palette, register, closing, cleanZone, fillPhrase, veto, neverWrite,
    colorWord, negation, hex. A passing check appears once with status ok; each problem is its own entry.
    In mode "free" every error becomes a warning and `blocked` is always False."""
    if mode not in ("brand", "free"):
        raise GimgError("brandsheet.bad_mode", mode=str(mode))
    spec = _piece(sheet, piece) if piece is not None else None
    clean_zone = (clean_zone or "").strip() or None  # a zone of only spaces is no zone (as in `assemble`)
    checks = []

    def add(cid, problem=None, span=None, **params):
        entry = {"id": cid, "status": "error" if problem else "ok",
                 "message": {"key": "lint.%s" % problem if problem else "lint.ok.%s" % cid, "params": params}}
        if span is not None:
            entry["span"] = span
        checks.append(entry)

    def ok_unless(cid, before):
        if len(checks) == before:
            add(cid)

    # words
    limits = (spec or {}).get("promptWords") or sheet.get("promptWords", DEFAULT_WORDS)
    count = len(prompt.split())
    if not limits["min"] <= count <= limits["max"]:
        add("words", "words", count=count, min=limits["min"], max=limits["max"])
    else:
        add("words", count=count)

    # palette sentence at the end, with every hex
    expected = palette_sentence(sheet, spec)
    tail = prompt.rstrip()
    pal_span = None
    if _norm(tail).endswith(_norm(expected)):
        pal_span = _find(prompt, expected)
        add("palette")
    else:
        hexes = [h.lower() for h in _HEX.findall(expected)]
        # the palette sentence may have several sentences: look at as many sentences of the tail as it has
        n = len(re.split(r"(?<=[.!?])\s+", expected.strip()))
        last = " ".join(re.split(r"(?<=[.!?])\s+", tail)[-n:]).lower() if tail else ""
        missing = [h for h in hexes if h not in last]
        add("palette", "palette", missing=", ".join(missing) or "-")

    # register block: one and only one, the piece's own if known
    reg_spans = {rid: _find(prompt, reg["block"]) for rid, reg in sheet["registers"].items()}
    present = [rid for rid, span in reg_spans.items() if span]
    # a block written inside another one's text (one register contained in another) is not a second register
    # (only when every appearance of it is inside the other: one written apart is a second register)
    all_spans = {rid: _find_all(prompt, sheet["registers"][rid]["block"]) for rid in present}
    present = [rid for rid in present if not all(
        any(o != rid and a[0] <= span[0] and span[1] <= a[1] and a != span for o in present for a in all_spans[o])
        for span in all_spans[rid])]
    if not present:
        add("register", "register_none")
    elif len(present) > 1:
        add("register", "register_many", registers=", ".join(present))
    elif spec is not None and present[0] != spec["register"]:
        add("register", "register_wrong", found=present[0], expected=spec["register"], span=reg_spans[present[0]])
    else:
        add("register", register=present[0])

    # closing
    closing_span = _find(prompt, _closing(sheet, spec))
    if closing_span:
        add("closing")
    else:
        add("closing", "closing")

    # clean zone before the register, and no fill phrase with it
    fill = sheet.get("vetoes", {}).get("fillPhrase")
    if clean_zone:
        zone = _find(prompt, clean_zone)
        first_reg = min((s[0] for s in reg_spans.values() if s), default=None)
        if zone is None:
            add("cleanZone", "clean_zone_missing")
        elif _zone_after(spec):
            if closing_span is not None and zone[0] < closing_span[1]:  # no closing: `closing` already says it
                add("cleanZone", "clean_zone_order", span=zone)
            else:
                add("cleanZone")
        elif first_reg is not None and zone[0] > first_reg:
            add("cleanZone", "clean_zone_order", span=zone)
        else:
            add("cleanZone")
        before = len(checks)
        for span in (_word_spans(prompt, fill) if fill else []):
            add("fillPhrase", "fill_phrase", span=span, phrase=fill)
        ok_unless("fillPhrase", before)

    # vetoed terms (whole word, any case), minus the exceptions of this piece; the closing and the register block
    # are the sheet's own approved text (the 06 closing says «no clouds»), so a term inside them is not a veto
    own_regs = [reg_spans[spec["register"]]] if spec is not None else list(reg_spans.values())
    own_text = [s for s in [closing_span] + own_regs if s]
    vetoes = sheet.get("vetoes", {})
    allowed = {e["term"].lower() for e in vetoes.get("exceptions", []) if piece is not None and piece in e["pieces"]}
    before = len(checks)
    for group in vetoes.get("groups", []):
        reason = group.get("reason", {"es": "", "en": ""})
        for term in group["terms"]:
            if term.lower() in allowed:
                continue
            for span in _word_spans(prompt, term):
                if _inside(span, own_text):
                    continue
                add("veto", "veto", span=span, term=term, group=group["id"], reason=reason)
    ok_unless("veto", before)

    before = len(checks)
    for term in vetoes.get("neverWrite", []):
        for span in _word_spans(prompt, term):
            if not _inside(span, own_text):
                add("neverWrite", "never_write", span=span, term=term)
    ok_unless("neverWrite", before)

    # colour names outside the palette sentence and the colours' own prompt names
    shield = [s for s in [pal_span, closing_span] + own_regs if s]
    dark = sheet["palette"].get("dark", {})
    for token in [sheet["palette"].get(r) for r in ROLES] + [dark.get("paper"), dark.get("ink")]:
        if token and token.get("promptName"):
            shield += _word_spans(prompt, token["promptName"])
    before = len(checks)
    for term in vetoes.get("colorWords", []):
        for span in _word_spans(prompt, term):
            if not _inside(span, shield):
                add("colorWord", "color_word", span=span, term=term)
    ok_unless("colorWord", before)

    # negations only in the closing (register blocks are approved text and may carry them)
    quiet = [s for s in [closing_span] + own_regs if s]
    if clean_zone and _zone_after(spec):  # the person's zone put after the closing may say «no buildings»
        zone_span = _find(prompt, clean_zone)
        if zone_span:
            quiet.append(zone_span)
    before = len(checks)
    for word in NEGATIONS:
        for span in _word_spans(prompt, word):
            if not _inside(span, quiet):
                add("negation", "negation", span=span, word=prompt[span[0]:span[1]])
    ok_unless("negation", before)

    # hex outside the palette (the piece's chroma background is allowed)
    known = set(palette(sheet))
    if spec is not None and spec.get("chroma"):
        known.add(spec["chroma"].lower())
    before = len(checks)
    for match in _HEX.finditer(prompt):
        if match.group(0).lower() not in known:
            add("hex", "hex", span=[match.start(), match.end()], value=match.group(0))
    ok_unless("hex", before)

    if mode == "free":
        for check in checks:
            if check["status"] == "error":
                check["status"] = "warn"
    blocked = mode == "brand" and any(c["status"] == "error" for c in checks)
    return {"checks": checks, "blocked": blocked}


# --- what the CLI and the API both serve -------------------------------------------------------------------------

def declared(project: dict) -> str | None:
    """Relative path of the sheet the project's config declares (`brand.sheet`), or None."""
    return project["config"].get("brand", {}).get("sheet")


def profile_owner(sheet: dict, piece: str) -> str:
    """Project whose config holds the profile of a piece type: the one that declared that `profile` (an inherited
    piece type uses the profiles of the project that declared it, not the child's)."""
    found = sheet.get("origin", {}).get("pieceTypes.%s.profile" % piece)
    return found["project"] if found else sheet["chain"][0]


def piece_defaults(sheet: dict, piece: str) -> dict:
    """What a piece type gives an order that does not say otherwise: {profile, seed, count, model, chroma}. The model
    is the one of the profile in the config of the project that declared it (`profile_owner`)."""
    spec = sheet["pieceTypes"][piece]
    profile = spec.get("profile")
    model = projects.get(profile_owner(sheet, piece))["config"].get("profiles", {}).get(profile, {}).get("model")
    return {"profile": profile, "seed": spec.get("seed"), "count": spec.get("count"), "model": model,
            "chroma": spec.get("chroma")}


def blocking_errors(checks: list) -> list:
    """The failing checks of a lint as validation errors (`GimgError.errors`): path ``/prompt``, code ``lint.<problem>``
    (its text is the lint message), params of the message plus ``id`` and ``span``."""
    out = []
    for check in checks:
        if check["status"] == "error":
            params = {**check["message"]["params"], "id": check["id"]}
            if "span" in check:
                params["span"] = check["span"]
            out.append(schema.ValidationError("/prompt", check["message"]["key"], params))
    return out


def prompt_response(project_name: str, piece: str, subject: str, clean_zone: str | None = None) -> dict:
    """`gimg brand prompt --json` / `POST .../brand/prompt`: the assembled prompt, its checks and the piece defaults."""
    sheet = resolve(project_name)
    built = assemble(sheet, piece, subject, clean_zone)
    res = lint(sheet, built["prompt"], piece, "brand", clean_zone)
    from . import failures  # troubleshooting rows of the project: the terms that already failed (lazy: failures imports orders)
    return {**built, "checks": res["checks"], "blocked": res["blocked"], "defaults": piece_defaults(sheet, piece),
            "known": failures.known_terms(project_name, subject)}


def piece_list(piece_types: dict, sheet: dict | None = None, project: str | None = None) -> list:
    """Piece types as a list `[{"id", ...fields the sheet has, "profileProject"}]`. `profileProject` is the project
    whose config holds the profile (`profile_owner` of the resolved `sheet`; without one, `project` itself)."""
    return [{"id": pid, **copy.deepcopy(spec),
             "profileProject": profile_owner(sheet, pid) if sheet is not None else project}
            for pid, spec in piece_types.items()]


def _error_lines(exc: GimgError, lang) -> list:
    return exc.message(lang).split("\n")


def status(project_name: str, lang=None) -> dict:
    """State of the project's sheet that never raises for a sheet problem: `{"sheet": {present, valid, version,
    path, extends, errors}, "pieceTypes": [...]}`. A project without a sheet is `present: false`, no error."""
    project = projects.get(project_name)
    rel = declared(project)
    info = {"present": False, "valid": False, "version": None, "path": rel, "extends": [], "errors": []}
    if rel is None:
        return {"sheet": info, "pieceTypes": []}
    own = None
    try:
        own = load(paths.inside(project["root"], rel))
        info["present"] = True
        if own.get("extends"):
            info["extends"] = [own["extends"]]
    except GimgError as exc:
        info["present"] = exc.code != "brandsheet.missing"
        info["errors"] = _error_lines(exc, lang)
    except OSError as exc:
        info["errors"] = [str(exc)]
    if own is None:
        return {"sheet": info, "pieceTypes": []}
    try:
        sheet = resolve(project_name)
    except GimgError as exc:
        info["errors"] = _error_lines(exc, lang)
        return {"sheet": info, "pieceTypes": piece_list(own.get("pieceTypes", {}), None, project_name)}
    info.update(valid=True, version=sheet["version"], extends=sheet["chain"][1:])
    return {"sheet": info, "pieceTypes": piece_list(sheet.get("pieceTypes", {}), sheet)}


def sheet_view(project_name: str) -> dict:
    """`GET .../brand/sheet`: the resolved sheet as the UI shows it, with `origin` (own|inherited + project + file)
    for every field path `resolve` records (vetoes.exceptions by position in the merged list)."""
    sheet = resolve(project_name)
    pal = sheet["palette"]
    roles = {r: {"hex": _value(pal[r]), "name": pal[r].get("promptName")} for r in ROLES if r in pal}
    files = {}
    origin = {}
    for field, found in sheet["origin"].items():
        owner = found["project"]
        if owner not in files:
            files[owner] = declared(projects.get(owner))
        origin[field] = {"origin": found["origin"], "project": owner, "file": files[owner]}
    out = {"name": sheet["name"], "version": sheet["version"], "chain": sheet["chain"], "roles": roles,
           "palette": pal, "registers": sheet["registers"], "closing": sheet["closing"],
           "paletteSentence": sheet["paletteSentence"], "paletteSentenceText": palette_sentence(sheet),
           "vetoes": sheet.get("vetoes", {}), "pieceTypes": piece_list(sheet.get("pieceTypes", {}), sheet),
           "acceptance": sheet.get("acceptance", {}), "promptWords": sheet.get("promptWords", DEFAULT_WORDS),
           "origin": origin}
    return out


# --- hoja.md: the generated block (0.7.0, paso 4) ---------------------------------------------------------------

MD_START = "<!-- gimg brand md: start (generated from marca.json; do not edit by hand: gimg brand md --write) -->"
MD_END = "<!-- gimg brand md: end -->"
MD_PREFIX = "<!-- gimg brand md:"


def _cell(value) -> str:
    return "—" if value in (None, "", []) else str(value).replace("|", "\\|").replace("\n", " ")


def _code(text: str) -> list:
    """A fenced code block whose fence is longer than any backtick run in the text (3 at least)."""
    fence = "`" * max([3] + [len(run) + 1 for run in re.findall(r"`+", text)])
    return [fence, text.rstrip("\n"), fence]


def _no_marker(value, path=""):
    if isinstance(value, str):
        if MD_PREFIX in value:
            raise GimgError("brandsheet.markdown_marker_in_data", field=path)
    elif isinstance(value, dict):
        for key, item in value.items():
            _no_marker(item, "%s.%s" % (path, key) if path else str(key))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _no_marker(item, "%s.%d" % (path, i))


def _table(head: list, rows: list) -> list:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    return out + ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]


def _origin_text(origin: dict, prefix: str, lang: str) -> str:
    """«propio» / «heredado de X» for a field path and everything under it (the sheet's own mix is both)."""
    found = [v for k, v in origin.items() if k == prefix or k.startswith(prefix + ".")]
    parts = []
    if any(v["origin"] == "own" for v in found):
        parts.append(i18n.t("brandsheet.md.own", lang))
    for owner in dict.fromkeys(v["project"] for v in found if v["origin"] == "inherited"):
        parts.append(i18n.t("brandsheet.md.inherited", lang, project=owner))
    return " + ".join(parts) or "—"


def _words(value, lang) -> str:
    return i18n.t("brandsheet.md.words_range", lang, min=value["min"], max=value["max"]) if value else None


def markdown(project_name: str, lang: str = "es") -> str:
    """The generated `hoja.md` block (markers included) of a project's resolved sheet; deterministic."""
    view = sheet_view(project_name)
    _no_marker({k: v for k, v in view.items() if k != "origin"})
    origin = view["origin"]

    def t(key, **params):
        return i18n.t("brandsheet.md." + key, lang, **params)

    def own(prefix):
        return _origin_text(origin, prefix, lang)

    out = [MD_START, "", "### " + t("title"), "", "#### " + t("card")]
    out += ["", "- %s: `%s`" % (t("name"), view["name"]), "- %s: `%s`" % (t("version"), view["version"]),
            "- %s: %s" % (t("chain"), " ← ".join(view["chain"]))]
    pal = view["palette"]
    out += ["", "#### " + t("palette"), ""]
    rows = [(r, "`%s`" % view["roles"][r]["hex"], view["roles"][r]["name"], own("palette." + r))
            for r in ROLES if r in view["roles"]]
    out += _table([t("role"), "hex", t("prompt_name"), t("origin")], rows)
    tones = _tones(pal)
    if tones:
        out += ["", "- %s: `%s` / `%s`" % (t("tones"), tones["deep"], tones["dark"])]
    if pal.get("dark"):
        out += ["", "- %s: %s (%s)" % (t("dark"), ", ".join("%s `%s`" % (k, _value(v)) for k, v in pal["dark"].items()),
                                       own("palette.dark"))]
    if pal.get("measureOnly"):
        out += ["", "- %s: %s (%s)" % (t("measure_only"), ", ".join("`%s`" % h.lower() for h in pal["measureOnly"]),
                                       own("palette.measureOnly"))]
    out += ["", "- %s (%s):" % (t("palette_sentence"), own("paletteSentence")), ""]
    out += _code(view["paletteSentenceText"])

    out += ["", "#### " + t("registers")]
    for rid, reg in view["registers"].items():
        out += ["", "##### `%s`: %s (%s)" % (rid, reg["label"].get(lang) or reg["label"]["en"], own("registers." + rid)), ""]
        out += _code(reg["block"])
    out += ["", "- %s (%s):" % (t("closing"), own("closing")), ""] + _code(view["closing"])
    out += ["", "- %s: %s (%s)" % (t("prompt_words"), _words(view["promptWords"], lang), own("promptWords"))]

    vet = view["vetoes"]
    out += ["", "#### " + t("vetoes")]
    for group in vet.get("groups", []):
        gid = group["id"]
        label = group.get("label", {})
        reason = group.get("reason", {})
        out += ["", "##### `%s`: %s (%s)" % (gid, _cell(label.get(lang) or label.get("en")), own("vetoes.groups." + gid))]
        if reason.get(lang) or reason.get("en"):
            out += ["", "%s: %s" % (t("reason"), reason.get(lang) or reason["en"])]
        out += ["", "%s: %s" % (t("terms"), ", ".join("`%s`" % x for x in group["terms"]))]
    if vet.get("exceptions"):
        out += ["", "##### " + t("exceptions"), ""]
        rows = [(e["term"], ", ".join(e["pieces"]), own("vetoes.exceptions.%d" % i))
                for i, e in enumerate(vet["exceptions"])]
        out += _table([t("term"), t("pieces"), t("origin")], rows)
    for key in vet:
        if key in ("groups", "exceptions"):
            continue
        value = vet[key]
        text = ", ".join("`%s`" % x for x in value) if isinstance(value, list) else "`%s`" % value
        out += ["", "- `%s` (%s): %s" % (key, own("vetoes." + key), text)]

    out += ["", "#### " + t("pieces_title"), ""]
    head = [t("piece"), t("profile"), t("register"), t("chroma"), "seed", "count", t("workshop"), t("delivery"),
            t("own_closing"), t("own_sentence"), "cleanZone", "promptWords", t("origin")]
    rows = []
    for piece in view["pieceTypes"]:
        pid = piece["id"]
        label = piece.get("label", {}).get(lang)
        rows.append(("`%s`%s" % (pid, " (%s)" % label if label else ""), piece.get("profile"), piece.get("register"),
                     piece.get("chroma"), piece.get("seed"), piece.get("count"), ", ".join(piece.get("workshop", [])),
                     piece.get("delivery"), piece.get("closing"), piece.get("paletteSentence"), piece.get("cleanZone"),
                     _words(piece.get("promptWords"), lang), own("pieceTypes." + pid)))
    out += _table(head, rows) if rows else [t("none")]

    acc = view["acceptance"]
    out += ["", "#### " + t("acceptance"), ""]
    lines = []
    if acc.get("traits"):
        lines.append("- %s (%s): %s" % (t("traits"), own("acceptance.traits"),
                                        ", ".join("`%s` %s" % (k, v) for k, v in acc["traits"].items())))
    if acc.get("references"):
        lines.append("- %s (%s): %s" % (t("references"), own("acceptance.references"),
                                        ", ".join("`%s`" % r for r in acc["references"])))
    if acc.get("unmeasured"):
        lines.append("- %s (%s):" % (t("unmeasured"), own("acceptance.unmeasured")))
        lines += ["  - `%s`: %s" % (u["id"], u["label"].get(lang) or u["label"]["en"]) for u in acc["unmeasured"]]
    if "autoDiscard" in acc:
        lines.append("- autoDiscard (%s): %s" % (own("acceptance.autoDiscard"), "true" if acc["autoDiscard"] else "false"))
    out += lines or [t("none")]
    return "\n".join(out + ["", MD_END]) + "\n"


def _block_span(text: str, path) -> tuple | None:
    """(start, end) offsets of the block in `text` (end after the closing marker), None without markers;
    a lone or repeated marker raises."""
    start, end = text.find(MD_START), text.find(MD_END)
    if start < 0 and end < 0:
        return None
    if start < 0 or end < 0 or start != text.rfind(MD_START) or end != text.rfind(MD_END) or start > end:
        raise GimgError("brandsheet.markdown_markers", path=str(path))
    return start, end + len(MD_END)


def _gap(text: str) -> str:
    if not text or text.endswith("\n\n"):
        return ""
    return "\n" if text.endswith("\n") else "\n\n"


def extract_block(text: str, path="") -> str | None:
    """The block between the markers (markers included, one trailing newline), None if there are none."""
    span = _block_span(text, path)
    return None if span is None else text[span[0]:span[1]] + "\n"


def replace_block(text: str, block: str, path="") -> str:
    """`text` with the block between the markers replaced (the rest byte for byte); without markers, the block is
    appended after a blank line."""
    span = _block_span(text, path)
    if span is None:
        return text + _gap(text) + block
    tail = text[span[1]:]
    return text[:span[0]] + block.rstrip("\n") + (tail if tail else "\n")
