"""opt-ai JSONL log of every attempt, and the duration estimate (D26)."""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone

from . import fsutil, paths


def log_path(project: str):
    return paths.project_data_dir(project, "log.bad_project") / "log.jsonl"


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
        # D34: the whole order. ``app.load_ms`` above already is the load time (the opt-ai name).
        "app.image.model_files": getattr(result, "model_files", None),
        "app.image.backend": getattr(result, "backend", None),
        "app.image.threads": getattr(result, "threads", None),
        "app.image.draft": bool(spec.get("draft")),
        "app.image.initImage": (str(spec["initImage"]).rsplit("/", 1)[-1] if spec.get("initImage") is not None else None),
        "app.image.strength": spec.get("strength") if spec.get("initImage") is not None else None,
        "app.image.compose": getattr(result, "compose", None),
        "app.image.command": getattr(result, "command", None),
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


def estimate(project: str, provider: str, profile: str, steps, has_references: bool, draft: bool = False,
             img2img: bool = False):
    """Median ``app.duration_ms`` (ms) of the non-error lines with the same provider, profile,
    steps, with/without references, draft and img2img (a line without ``app.image.draft`` is not a draft, one without
    ``app.image.initImage`` is not img2img); ``None`` without data."""
    values = []
    for line in _lines(log_path(project)):
        refs, duration = line.get("app.image.references"), line.get("app.duration_ms")
        if ("app.error" in line or line.get("gen_ai.provider.name") != provider
                or line.get("app.task") != profile or line.get("app.image.steps") != steps
                or bool(line.get("app.image.draft")) != bool(draft)
                or ("app.image.initImage" in line) != bool(img2img)
                or not isinstance(refs, int) or isinstance(refs, bool)
                or (refs > 0) != bool(has_references)
                or not isinstance(duration, (int, float)) or isinstance(duration, bool)):
            continue
        values.append(duration)
    return statistics.median(values) if values else None
