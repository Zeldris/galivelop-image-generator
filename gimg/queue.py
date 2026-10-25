"""Persistent job queue (D10): one for the whole generator, ``<data>/queue.json``.

``{"nextId": n, "entries": [...]}``; entry: ``id``, ``project``, ``key``, ``profile``, ``seed``, ``prompt``,
``params``, ``references``, ``state`` (queued|running|done|failed|cancelled), ``pid``, ``enqueuedAt``,
``startedAt``, ``finishedAt``, ``error``, ``attemptId``, ``cancelRequested``. Entries stay in arrival order.

``error`` of a failed entry is ``{"code": ..., "params": {...}}`` (JSON); `error_text` renders it.

Every read goes through one locked transaction (`fsutil.lock` of ``queue.json``), which also recovers
the file. Recovery is decided by the worker lock (``<data>/worker.lock``), not by pids: a process that can take
it without waiting knows no worker is alive, so every ``running`` entry is dead and goes back to ``queued``
(or to ``cancelled`` if a cancel was already requested), and the ``.pending-<entry>.png`` files it left are
deleted. If the lock is taken, running entries are left alone. `list_entries`, `get` and `enqueue` try this;
the worker does it right after taking its own lock (`recover_orphans`); `claim`, `cancel`, `finish`,
`next_queued` and `is_cancel_requested` never do. ``pid`` stays in the entry as information only.
Only the last `KEEP_TERMINAL` finished entries are kept.
"""
from __future__ import annotations

import contextlib
import copy
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from . import engine as engine_mod
from . import fsutil, i18n, limits, log, orders, paths
from .errors import GimgError

KEEP_TERMINAL = 200
TERMINAL = ("done", "failed", "cancelled")
STATES = ("queued", "running") + TERMINAL


def queue_path() -> Path:
    return paths.data_dir() / "queue.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def worker_lock_path() -> Path:
    return paths.data_dir() / "worker.lock"


@contextlib.contextmanager
def _no_worker():
    """Yields True if the worker lock could be taken without waiting (no worker alive), else False.
    A second open() + flock inside the worker's own process fails too, which correctly means "alive"."""
    path = worker_lock_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
    except OSError:
        yield False
        return
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            free = True
        except OSError:
            free = False
        yield free
    finally:
        os.close(fd)


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


def _clean_pending(entry: dict) -> None:
    try:
        folder = orders.pending_image_path(entry["project"], entry["key"], entry["profile"], entry["id"]).parent
        names = ".pending-%d.png" % entry["id"]
        for found in list(folder.glob(names)) + list(folder.glob("." + names + ".*.tmp")):
            with contextlib.suppress(OSError):
                found.unlink()
    except Exception:  # a bad entry must not stop the recovery
        pass


def _recover(data: dict, running_dead: bool) -> list:
    """Prune, and (`running_dead`) send every ``running`` entry back to ``queued``/``cancelled``.
    Returns the entries recovered."""
    now = _now()
    recovered = []
    for entry in data["entries"]:
        if running_dead and entry["state"] == "running":
            entry["pid"] = None
            entry["startedAt"] = None
            if entry.get("cancelRequested"):
                entry["state"] = "cancelled"
                entry["finishedAt"] = now
            else:
                entry["state"] = "queued"
            recovered.append(entry)
    done = [e for e in data["entries"] if e["state"] in TERMINAL]
    if len(done) > KEEP_TERMINAL:
        drop = {e["id"] for e in done[:len(done) - KEEP_TERMINAL]}
        data["entries"] = [e for e in data["entries"] if e["id"] not in drop]
    return recovered


def _txn(change, recover: bool = False, own_lock: bool = False):
    """Locked read, `change(data)` (edits in place, returns the result), write if anything changed.

    `recover`: try the worker lock and, if free, recover ``running`` entries first. `own_lock`: the caller
    already holds the worker lock (the worker): recover without trying. Pruning always happens."""
    path = queue_path()
    with fsutil.lock(path), contextlib.ExitStack() as stack:
        free = own_lock or (recover and stack.enter_context(_no_worker()))
        data = _load()
        before = copy.deepcopy(data)
        for entry in _recover(data, bool(free)):
            _clean_pending(entry)
        result = change(data)
        if data != before:
            fsutil.write_json(path, data)
        return copy.deepcopy(result)


def recover_orphans() -> None:
    """For the worker, which holds the worker lock: every ``running`` entry is dead; recover them all."""
    _txn(lambda data: None, own_lock=True)


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

    return _txn(change, recover=True)


def list_entries(states=None) -> list:
    """Entries in arrival order, optionally only those whose state is in `states`."""
    wanted = None if states is None else set(states)
    return _txn(lambda data: [e for e in data["entries"] if wanted is None or e["state"] in wanted],
                recover=True)


def get(entry_id) -> dict:
    return _txn(lambda data: _find(data, entry_id), recover=True)


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


def make_error(code: str, **params) -> dict:
    """The ``error`` of an entry: ``{"code", "params"}``, JSON-serialisable (values that are not become text)."""
    return json.loads(json.dumps({"code": code, "params": params}, default=str))


def error_text(error, lang: str | None = None) -> str:
    """Render an entry's ``error`` (or the entry itself) with i18n; ``""`` if there is no error."""
    if isinstance(error, dict) and "state" in error:
        error = error.get("error")
    if not error:
        return ""
    code, params = error["code"], error.get("params") or {}
    try:
        text = i18n.t("error." + code, lang, **params)
    except (KeyError, IndexError, TypeError, ValueError):  # missing or oddly named placeholder
        return code
    return code if text == "error." + code else text  # no text for this code: show the code


def finish(entry_id, state: str, error=None, attempt_id=None) -> dict:
    """Close a running entry as done, failed or cancelled. `error`: ``{"code", "params"}`` (see `make_error`);
    a plain string is taken as a code without params."""
    if state not in TERMINAL:
        raise GimgError("queue.bad_state", state=str(state), states=", ".join(TERMINAL))
    if isinstance(error, str):
        error = make_error(error)

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
