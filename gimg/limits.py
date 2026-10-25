"""Machine profile loading and safety limits (D15)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import fsutil, paths, schema
from .errors import GimgError

DEFAULT_PROFILE = "steam-deck"
_PRESETS = Path(__file__).resolve().parent / "machine_profiles"
_NAME = re.compile(r"[a-z0-9][a-z0-9-]*")


class LimitError(GimgError):
    """A spec exceeds a limit of the machine profile."""


def _load_file(path: Path, shown: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise GimgError("machine.missing", path=shown)
    except (OSError, ValueError) as exc:
        raise GimgError("machine.unreadable", path=shown, reason=str(exc))
    errors = schema.validate(data, schema.load_schema("machine-profile"))
    if errors:
        raise GimgError("machine.invalid", errors=errors, path=shown)
    return data


def _preset(name) -> dict:
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise GimgError("machine.bad_name", name=str(name))
    return _load_file(_PRESETS / (name + ".json"), name)


def load_machine(ref: str | None = None) -> dict:
    """Machine profile: `ref` (a preset name or a JSON path), else ``GIMG_MACHINE_PROFILE``,
    else ``machineProfile`` in ``<config>/config.json``, else ``steam-deck``.

    A value containing ``/`` or ending in ``.json`` is a file path; anything else is a preset name
    (validated, so it cannot leave `gimg/machine_profiles/`)."""
    if not ref:
        ref = os.environ.get("GIMG_MACHINE_PROFILE")
    if not ref:
        config = fsutil.read_json(paths.config_dir() / "config.json", {})
        ref = config.get("machineProfile") if isinstance(config, dict) else None
    if not ref:
        ref = DEFAULT_PROFILE
    if not isinstance(ref, str):
        raise GimgError("machine.bad_name", name=str(ref))
    if "/" in ref or ref.endswith(".json"):
        if any(ord(c) < 0x20 or ord(c) == 0x7F for c in ref):
            raise GimgError("machine.bad_path", path=repr(ref))
        try:
            path = Path(ref).expanduser()
        except (RuntimeError, OSError) as exc:
            raise GimgError("machine.unreadable", path=ref, reason=str(exc))
        return _load_file(path, ref)
    return _preset(ref)


def check(spec: dict, machine: dict) -> None:
    """Raise `LimitError` if `spec` (from ``orders.attempt_specs``) exceeds the machine limits.

    A limit the machine profile does not define, or a value the spec does not fix, is not checked."""
    refs = len(spec.get("references") or [])
    max_refs = machine.get("maxReferences")
    if max_refs is not None and refs > max_refs:
        raise LimitError("limit.references", count=refs, max=max_refs)
    params = spec.get("params") or {}
    steps, max_steps = params.get("steps"), machine.get("maxSteps")
    if steps is not None and max_steps is not None and steps > max_steps:
        raise LimitError("limit.steps", steps=steps, max=max_steps)
    width, height, max_pixels = params.get("width"), params.get("height"), machine.get("maxPixels")
    if width is not None and height is not None and max_pixels is not None and width * height > max_pixels:
        raise LimitError("limit.pixels", width=width, height=height, pixels=width * height, max=max_pixels)
