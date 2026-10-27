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
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import delivery, i18n, limits, log, orders, paths, png, projects
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
    ``compose.logo_missing``; one over MAX_SVG_BYTES, ``compose.svg_too_big``."""
    template = _asset(project_root, compose_cfg["template"], "compose.template_missing")
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


def render(project_root, profile_cfg, raw_path, out_path, text, profile=None, prefix=COMPOSE_TMP_PREFIX) -> dict:
    """Compose the raw image `raw_path` into `out_path` for `profile_cfg` and return what was done.

    `project_root` is the folder of the project (the template and the logo are resolved inside it); `text` maps the
    ``compose.fields`` to their texts (a missing field is the empty string). The result is written atomically: nothing
    is left at `out_path` if a step fails. Returns ``{"fit", "targetWidth", "targetHeight", "text"}`` plus
    ``template`` and ``logo`` when the profile has them: what the attempt records as ``compose``.

    The temporary folder sits next to `out_path` and starts with `prefix`: each caller uses its own, so recovering one
    composition (`queue._clean_pending` removes ``.compose-q<entry>-*``) never touches another's."""
    raw_path, out_path = Path(raw_path), Path(out_path)
    raw_w, raw_h = png.size(raw_path)
    plan = plan_for(profile_cfg, raw_w, raw_h)
    if plan is None:
        raise GimgError("compose.nothing_to_do", profile=profile or "")
    width, height, fit = plan["targetWidth"], plan["targetHeight"], plan["fit"]
    geom = (width, height) + fit_geometry(raw_w, raw_h, width, height, fit)
    compose_cfg = profile_cfg.get("compose")
    used = {}
    layer_svg = None
    if compose_cfg is not None:
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
    info = dict(plan, text=used)
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
    """One line in the project log, like the worker's (D26): ``app.image.compose`` or ``app.image.compose_error``; the
    extra ``app.image.recompose`` tells it from a generation (no engine ran: no duration). Never fails the caller."""
    try:
        record = log.record_for(key, profile, attempt, limits.load_machine(), attempt.get("engine") or "unknown",
                                compose=(info or {}).get("template"), compose_error=(error or {}).get("code"))
        record["app.image.recompose"] = True
        log.append(project, record)
    except Exception as exc:
        print(i18n.t("compose.log_failed", reason=str(exc)), file=sys.stderr)


def recompose(project, key, profile, attempt_id=None, text=None) -> dict:
    """Compose an attempt again from its raw image, without generating (D28); returns the attempt (a copy).

    The attempt is `attempt_id`, else the chosen one, else the last. `text` (``{field: value}``) is merged into the
    order's ``text`` first (`orders.set_text`: the next attempts and the gallery use it too) and the order's text is what
    gets composed. An attempt made before F2.8 has no raw image: its ``image`` is copied to ``<stem>.raw.png`` before
    anything else (`orders.set_composed` expects it). The temporary folder is ``.compose-c<id>-*``.

    A profile with nothing to compose raises ``compose.nothing_to_do`` before anything changes. If the render fails, the
    attempt gets the error as ``composeError`` (`orders.set_compose_error`) and it is raised again; a project log line
    records either result. The chosen attempt is delivered again (manifest included) and the result then has
    ``delivered``: the file, relative to the project."""
    proj = projects.get(project)
    profile_cfg = proj["config"]["profiles"].get(profile)
    order = orders.get(project, key, profile)
    if profile_cfg is None:
        raise GimgError("order.profile_unknown", profile=profile)
    attempt = _pick_attempt(order, attempt_id)
    attempt_id = attempt["id"]
    raw_path, out_path = orders.compose_paths(project, key, profile, attempt)
    # an attempt without ``raw`` is made before F2.8; if its copy is already there, the image may be a composed one
    keep = not isinstance(attempt.get("raw"), str) and not raw_path.is_file()
    source = orders.attempt_image(project, key, profile, attempt) if keep else raw_path
    if plan_for(profile_cfg, *png.size(source)) is None:
        raise GimgError("compose.nothing_to_do", profile=profile)
    texts = orders.set_text(project, key, profile, text) if text else dict(order.get("text") or {})
    if keep:
        _keep_raw(source, raw_path)
    try:
        info = render(proj["root"], profile_cfg, raw_path, out_path, texts, profile,
                      prefix=RECOMPOSE_TMP_PREFIX % attempt_id)
        done = orders.set_composed(project, key, profile, attempt_id, info)
    except Exception as exc:
        code, params = (exc.code, exc.params) if isinstance(exc, GimgError) else (
            "compose.unexpected", {"reason": ("%s: %s" % (type(exc).__name__, exc))[:300]})
        error = {"code": code, "params": json.loads(json.dumps(params, default=str))}
        try:
            failed = orders.set_compose_error(project, key, profile, attempt_id, error)
        except Exception:
            failed = attempt
        _log_recompose(project, key, profile, failed, error=error)
        raise
    _log_recompose(project, key, profile, done, info=info)
    if orders.get(project, key, profile)["chosen"] == attempt_id:
        delivery.choose(project, key, profile, attempt_id)
        done["delivered"] = delivery.delivered_file(project, key, profile)
    return done


__all__ = ["recompose", "render", "plan_for", "target_size", "fit_geometry", "substitute", "xml_escape", "resolve_assets",
           "logo_data_uri", "rsvg_argv", "ffmpeg_argv", "TIMEOUT_S", "MAX_SVG_BYTES"]
