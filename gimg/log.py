"""opt-ai JSONL log of every attempt, and the duration estimate (D26)."""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone

from . import fsutil, paths
from .errors import GimgError


def log_path(project: str):
    if not isinstance(project, str) or not project or "/" in project:
        raise GimgError("log.bad_project", project=str(project))
    return paths.inside(paths.data_dir(), "projects/%s/log.jsonl" % project)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_for(key: str, profile: str, spec: dict, machine: dict, provider: str,
               result=None, error: str | None = None, ts: str | None = None) -> dict:
    """The log line of one attempt: from an `EngineResult` (`result`) or an error message.
    Absent values are omitted, never ``null``."""
    params = spec.get("params") or {}
    line = {
        "ts": ts or _now(),
        "gen_ai.operation.name": "image_generation",
        "gen_ai.provider.name": provider,
        "gen_ai.request.model": params.get("model"),
        "app.task": profile,
        "app.machine_profile": machine.get("name"),
        "app.duration_ms": getattr(result, "duration_ms", None),
        "app.load_ms": getattr(result, "load_ms", None),
        "app.error": error,
        "app.image.key": key,
        "app.image.steps": params.get("steps"),
        "app.image.cfg": params.get("cfg"),
        "app.image.sampler": params.get("sampler"),
        "app.image.width": params.get("width"),
        "app.image.height": params.get("height"),
        "app.image.seed": spec.get("seed"),
        "app.image.references": len(spec.get("references") or []),
        "app.image.engine_version": getattr(result, "engine_version", None),
        "app.image.sample_ms": getattr(result, "sample_ms", None),
        "app.image.decode_ms": getattr(result, "decode_ms", None),
        "app.image.min_free_mb": getattr(result, "min_free_mb", None),
    }
    return {k: v for k, v in line.items() if v is not None}


def append(project: str, record: dict) -> None:
    """Append one JSON line to the project's log."""
    path = log_path(project)
    text = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
    with fsutil.lock(path):
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()


def _lines(path):
    try:
        fh = open(path, encoding="utf-8")
    except FileNotFoundError:
        return
    with fh:
        for raw in fh:
            try:
                line = json.loads(raw)
            except ValueError:
                continue
            if isinstance(line, dict):
                yield line


def estimate(project: str, provider: str, profile: str, steps, has_references: bool):
    """Median ``app.duration_ms`` (ms) of the non-error lines with the same provider, profile,
    steps and with/without references; ``None`` without data."""
    values = []
    for line in _lines(log_path(project)):
        refs, duration = line.get("app.image.references"), line.get("app.duration_ms")
        if ("app.error" in line or line.get("gen_ai.provider.name") != provider
                or line.get("app.task") != profile or line.get("app.image.steps") != steps
                or not isinstance(refs, int) or isinstance(refs, bool)
                or (refs > 0) != bool(has_references)
                or not isinstance(duration, (int, float)) or isinstance(duration, bool)):
            continue
        values.append(duration)
    return statistics.median(values) if values else None
