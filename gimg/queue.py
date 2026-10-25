"""Persistent job queue (D10): one for the whole generator, ``<data>/queue.json``.

``{"nextId": n, "entries": [...]}``; entry: ``id``, ``project``, ``key``, ``profile``, ``seed``, ``prompt``,
``params``, ``references``, ``state`` (queued|running|done|failed|cancelled), ``pid``, ``enqueuedAt``,
``startedAt``, ``finishedAt``, ``error``, ``attemptId``, ``cancelRequested``. Entries stay in arrival order.

Every read goes through one locked transaction (`fsutil.lock` of ``queue.json``), which also recovers
the file: a ``running`` entry whose ``pid`` is gone goes back to ``queued`` (or to ``cancelled`` if a
cancel was already requested), and only the last `KEEP_TERMINAL` finished entries are kept.
"""
from __future__ import annotations

import copy
import os
from datetime import datetime, timezone
from pathlib import Path

from . import engine as engine_mod
from . import fsutil, limits, log, orders, paths
from .errors import GimgError

KEEP_TERMINAL = 200
TERMINAL = ("done", "failed", "cancelled")
STATES = ("queued", "running") + TERMINAL


def queue_path() -> Path:
    return paths.data_dir() / "queue.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _alive(pid) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _load() -> dict:
    path = queue_path()
    try:
        data = fsutil.read_json(path, default={"nextId": 1, "entries": []})
    except (OSError, ValueError):
        raise GimgError("queue.corrupt", path=str(path))
    if (not isinstance(data, dict) or not isinstance(data.get("entries"), list)
            or not isinstance(data.get("nextId"), int)
            or not all(isinstance(e, dict) and e.get("state") in STATES and isinstance(e.get("id"), int)
                       for e in data["entries"])):
        raise GimgError("queue.corrupt", path=str(path))
    return data


def _recover(data: dict) -> None:
    now = _now()
    for entry in data["entries"]:
        if entry["state"] == "running" and not _alive(entry.get("pid")):
            entry["pid"] = None
            entry["startedAt"] = None
            if entry.get("cancelRequested"):
                entry["state"] = "cancelled"
                entry["finishedAt"] = now
            else:
                entry["state"] = "queued"
    done = [e for e in data["entries"] if e["state"] in TERMINAL]
    if len(done) > KEEP_TERMINAL:
        drop = {e["id"] for e in done[:len(done) - KEEP_TERMINAL]}
        data["entries"] = [e for e in data["entries"] if e["id"] not in drop]


def _txn(change):
    """Locked read, recovery, `change(data)` (edits in place, returns the result), write if anything changed."""
    path = queue_path()
    with fsutil.lock(path):
        data = _load()
        before = copy.deepcopy(data)
        _recover(data)
        result = change(data)
        if data != before:
            fsutil.write_json(path, data)
        return copy.deepcopy(result)


def _find(data: dict, entry_id) -> dict:
    for entry in data["entries"]:
        if type(entry_id) is int and entry["id"] == entry_id:
            return entry
    raise GimgError("queue.unknown", id=str(entry_id))


def enqueue(project: str, key: str, profile: str, specs: list) -> list:
    """Queue one entry per spec (from ``orders.attempt_specs``); returns the new entries.

    The order must exist and every spec must pass the limits of the current machine profile;
    nothing is queued if any fails."""
    orders.get(project, key, profile)
    machine = limits.load_machine()
    for spec in specs:
        limits.check(spec, machine)
    now = _now()

    def change(data):
        added = []
        for spec in specs:
            entry = {"id": data["nextId"], "project": project, "key": key, "profile": profile,
                     "seed": spec["seed"], "prompt": spec["prompt"],
                     "params": copy.deepcopy(spec["params"]),
                     "references": list(spec.get("references") or []),
                     "state": "queued", "pid": None, "enqueuedAt": now, "startedAt": None,
                     "finishedAt": None, "error": None, "attemptId": None, "cancelRequested": False}
            data["nextId"] += 1
            data["entries"].append(entry)
            added.append(entry)
        return added

    return _txn(change)


def list_entries(states=None) -> list:
    """Entries in arrival order, optionally only those whose state is in `states`."""
    wanted = None if states is None else set(states)
    return _txn(lambda data: [e for e in data["entries"] if wanted is None or e["state"] in wanted])


def get(entry_id) -> dict:
    return _txn(lambda data: _find(data, entry_id))


def cancel(entry_id) -> dict:
    """queued -> cancelled; running -> ``cancelRequested: true`` (the worker stops it); finished -> error."""
    def change(data):
        entry = _find(data, entry_id)
        if entry["state"] == "queued":
            entry["state"] = "cancelled"
            entry["finishedAt"] = _now()
        elif entry["state"] == "running":
            entry["cancelRequested"] = True
        else:
            raise GimgError("queue.not_cancellable", id=entry["id"], state=entry["state"])
        return entry

    return _txn(change)


def next_queued():
    """The first queued entry, without taking it; ``None`` if there is none."""
    return _txn(lambda data: next((e for e in data["entries"] if e["state"] == "queued"), None))


def claim():
    """Mark the first queued entry ``running`` with this process's pid; returns it, or ``None``."""
    def change(data):
        entry = next((e for e in data["entries"] if e["state"] == "queued"), None)
        if entry is not None:
            entry["state"] = "running"
            entry["pid"] = os.getpid()
            entry["startedAt"] = _now()
        return entry

    return _txn(change)


def finish(entry_id, state: str, error=None, attempt_id=None) -> dict:
    """Close a running entry as done, failed or cancelled."""
    if state not in TERMINAL:
        raise GimgError("queue.bad_state", state=str(state), states=", ".join(TERMINAL))

    def change(data):
        entry = _find(data, entry_id)
        if entry["state"] != "running":
            raise GimgError("queue.not_running", id=entry["id"], state=entry["state"])
        entry.update(state=state, error=error, attemptId=attempt_id, finishedAt=_now(), pid=None)
        return entry

    return _txn(change)


def is_cancel_requested(entry_id) -> bool:
    return bool(get(entry_id).get("cancelRequested"))


def estimate_for(entry: dict, provider: str | None = None):
    """Median duration (ms) of similar past attempts, or ``None``. `provider` defaults to the configured engine's."""
    if provider is None:
        provider = engine_mod.get_engine().provider
    steps = (entry.get("params") or {}).get("steps")
    return log.estimate(entry["project"], provider, entry["profile"], steps, bool(entry.get("references")))
