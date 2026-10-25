"""Data and config folders, and the D25 path guard."""
from __future__ import annotations

import os
from pathlib import Path

from .errors import GimgError, PathError

MAX_KEY = 200
MAX_SEGMENT = 100


def _home_dir(own: str, xdg: str, fallback: tuple) -> Path:
    explicit = os.environ.get(own)
    if explicit:
        return Path(explicit)
    base = os.environ.get(xdg)
    if base:
        return Path(base) / "gimg"
    return Path.home().joinpath(*fallback)


def config_dir() -> Path:
    return _home_dir("GIMG_CONFIG_HOME", "XDG_CONFIG_HOME", (".config", "gimg"))


def data_dir() -> Path:
    return _home_dir("GIMG_DATA_HOME", "XDG_DATA_HOME", (".local", "share", "gimg"))


def check_relative(rel) -> str:
    """Reject anything that is not a plain relative path; return it unchanged."""
    if not isinstance(rel, str):
        raise PathError("path.type")
    if rel == "":
        raise PathError("path.empty")
    if "\x00" in rel:
        raise PathError("path.nul")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in rel):
        raise PathError("path.control")
    if "\\" in rel:
        raise PathError("path.backslash")
    if rel.startswith("/"):
        raise PathError("path.absolute")
    if rel.startswith("~"):
        raise PathError("path.tilde")
    if ".." in rel.split("/"):
        raise PathError("path.dotdot")
    return rel


def inside(root, rel) -> Path:
    """Resolve `rel` under `root` (following links) and require it stays inside.

    The target may not exist yet. Returns the resolved path."""
    check_relative(rel)
    try:
        real_root = Path(root).resolve()
        target = (real_root / rel).resolve()
    except (OSError, RuntimeError):
        raise PathError("path.unresolvable", path=rel)
    if target != real_root and real_root not in target.parents:
        raise PathError("path.outside", path=rel)
    return target


def check_key(key: str) -> str:
    """Length limits of an order key (shape is the order schema's job)."""
    if len(key) > MAX_KEY:
        raise GimgError("key.too_long", limit=MAX_KEY)
    for segment in key.split("/"):
        if len(segment) > MAX_SEGMENT:
            raise GimgError("key.segment_too_long", limit=MAX_SEGMENT, segment=segment[:20])
    return key
