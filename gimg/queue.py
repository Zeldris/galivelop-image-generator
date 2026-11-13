"""Persistent job queue (D10): one for the whole generator, ``<data>/queue.json``.

``{"nextId": n, "entries": [...]}``; entry: ``id``, ``project``, ``key``, ``profile``, ``seed``, ``prompt``,
``params``, ``references``, ``state`` (queued|running|done|failed|cancelled), ``pid``, ``enqueuedAt``,
``startedAt``, ``finishedAt``, ``error``, ``attemptId``, ``cancelRequested``, ``draft`` (bool; an older entry without it is not a draft), ``initImage`` (relative path or ``None``) and ``strength`` (number or ``None``; an older entry without the keys has neither) and ``text`` (object, the values of the
profile's ``compose.fields``; an older entry without it has none: read it with ``.get``) and ``template`` (F4b: the id of the composition
template, ``None`` for ``default``; an older entry without it has none) and ``position`` (F4d: where a ``queued`` entry
stands; the worker takes the lowest one, ties and entries without it by id; `move` and `clear` edit it). Entries stay in arrival order in the file.
A running entry may also have ``progress`` (``{"step", "steps", "etaS"}``, `set_progress`) and ``preview`` (the path of
the engine's preview image, `set_preview`); both are removed when the entry finishes or goes back to ``queued``.

``error`` of a failed entry is ``{"code": ..., "params": {...}}`` (JSON); `error_text` renders it.

Every read goes through one locked transaction (`fsutil.lock` of ``queue.json``), which also recovers
the file. Recovery is decided by the worker lock (``<data>/worker.lock``), not by pids: a process that can take
it without waiting knows no worker is alive, so every ``running`` entry is dead and goes back to ``queued``
(or to ``cancelled`` if a cancel was already requested), and the ``.pending-<entry>.png`` files (and their ``.log`` and ``.preview.png``) it left are
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
import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import compose as compose_mod
from . import engine as engine_mod
from . import fsutil, i18n, limits, log, orders, paths, projects, schema
from . import models as models_mod
from .errors import GimgError

KEEP_TERMINAL = 200
TERMINAL = ("done", "failed", "cancelled")
STATES = ("queued", "running") + TERMINAL


def queue_path() -> Path:
    return paths.data_dir() / "queue.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pause_path() -> Path:
    return paths.data_dir() / "queue.paused"


def is_paused() -> bool:
    """Is the queue paused (the mark `pause` leaves next to ``queue.json``)? The worker finishes the image in progress
    and takes no other one; the service launches no worker."""
    return pause_path().exists()


def pause() -> bool:
    """Leave the pause mark; False if it was already there (pausing twice is harmless)."""
    path = pause_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with fsutil.lock(queue_path()):  # the queue's own lock: `claim` checks the mark under it
        try:
            fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(fd, "w") as fh:
            fh.write(_now() + "\n")
    return True


def resume() -> bool:
    """Remove the pause mark; False if there was none."""
    with fsutil.lock(queue_path()):
        try:
            pause_path().unlink()
        except FileNotFoundError:
            return False
    return True


def worker_lock_path() -> Path:
    return paths.data_dir() / "worker.lock"


@contextlib.contextmanager
def _no_worker():
    """Yields True if the worker lock could be taken without waiting (no worker alive), else False.
    A second open() + flock inside the worker's own process fails too, which correctly means "alive". The lock is
    shared, like ``worker_alive``: only the worker holds it exclusively, so a probe here never makes another probe
    see a worker that is not there (0.4.1)."""
    path = worker_lock_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
    except OSError:
        yield False
        return
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            free = True
        except OSError:
            free = False
        yield free
    finally:
        os.close(fd)


def worker_alive():
    """Does a worker hold ``worker.lock`` right now? ``True`` / ``False``, or ``None`` when it cannot be known (the
    lock exists but cannot be opened). A pure read: it creates neither the data folder nor the lock (no lock file
    means no worker has ever run, so ``False``). Callers that start workers must treat ``None`` as "do not start"."""
    return fsutil.held(worker_lock_path())


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
        stem = ".pending-%d" % entry["id"]  # the engine's log and preview sit next to the image
        found_all = (list(folder.glob(names)) + list(folder.glob("." + names + ".*.tmp"))
                     + [folder / (stem + ".log"), folder / (stem + ".preview.png")])
        for found in found_all:
            with contextlib.suppress(OSError):
                found.unlink()
        # a composition of this entry killed half way (only a dead worker can leave one); the folder of another
        # entry or of a `gimg compose` in progress has another prefix and stays
        for leftover in folder.glob(".compose-q%d-*" % entry["id"]):
            shutil.rmtree(leftover, ignore_errors=True)
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
            entry.pop("progress", None)
            entry.pop("preview", None)
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


def _pos(entry: dict):
    """Sort key of a queued entry: its ``position`` (else its id), then its id."""
    pos = entry.get("position")
    return (pos if isinstance(pos, (int, float)) and not isinstance(pos, bool) else entry["id"], entry["id"])


def _first_queued(data: dict):
    return min((e for e in data["entries"] if e["state"] == "queued"), key=_pos, default=None)


def _find(data: dict, entry_id) -> dict:
    for entry in data["entries"]:
        if type(entry_id) is int and entry["id"] == entry_id:
            return entry
    raise GimgError("queue.unknown", id=str(entry_id))


def check_specs(project: str, profile: str, specs: list) -> None:
    """What `enqueue` rejects before queueing anything: each spec against the machine profile's limits, its model
    against the catalog and the machine (``limit.steps``...), and its template against the profile's. `submit_order`
    runs it too, on the candidate specs, so a refused order is never stored."""
    machine = limits.load_machine()
    catalog = None
    for spec in specs:
        limits.check(spec, machine)
        model = (spec.get("params") or {}).get("model")
        if model is not None:
            catalog = catalog or models_mod.load_catalog()
            models_mod.check_allowed(model, machine, catalog, (spec.get("params") or {}).get("steps"))
    for tid in {spec["template"] for spec in specs if spec.get("template") is not None}:
        compose_mod.effective((compose_mod.merged_profile(projects.get(project), profile) or {}).get("compose"), tid)


def enqueue(project: str, key: str, profile: str, specs: list) -> list:
    """Queue one entry per spec (from ``orders.attempt_specs``); returns the new entries.

    The order must exist and every spec must pass the limits of the current machine profile;
    nothing is queued if any fails."""
    orders.get(project, key, profile)
    check_specs(project, profile, specs)
    now = _now()

    def change(data):
        added = []
        for spec in specs:
            entry = {"id": data["nextId"], "project": project, "key": key, "profile": profile,
                     "seed": spec["seed"], "prompt": spec["prompt"],
                     "params": copy.deepcopy(spec["params"]),
                     "references": list(spec.get("references") or []),
                     "draft": spec.get("draft") is True,
                     "initImage": spec.get("initImage"), "strength": spec.get("strength"),
                     "text": copy.deepcopy(spec.get("text") or {}),
                     "template": spec.get("template"), "position": data["nextId"],
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


MOVES = ("up", "down", "top")


def move(entry_id, to: str) -> dict:
    """Move a ``queued`` entry in the line the worker takes from: ``up``/``down`` one place (at the end of the line
    nothing changes), ``top`` first. Any other state is ``queue.not_movable``; another `to` is ``queue.bad_move``.
    Only the positions of the queued entries are permuted among themselves, so a later enqueue still goes last."""
    if to not in MOVES:
        raise GimgError("queue.bad_move", to=str(to), allowed=", ".join(MOVES))

    def change(data):
        entry = _find(data, entry_id)
        if entry["state"] != "queued":
            raise GimgError("queue.not_movable", id=entry["id"], state=entry["state"])
        line = sorted((e for e in data["entries"] if e["state"] == "queued"), key=_pos)
        slots = [_pos(e)[0] for e in line]
        at = line.index(entry)
        if to == "top":
            line.insert(0, line.pop(at))
        elif to == "up" and at > 0:
            line[at - 1], line[at] = line[at], line[at - 1]
        elif to == "down" and at < len(line) - 1:
            line[at + 1], line[at] = line[at], line[at + 1]
        for item, slot in zip(line, slots):
            item["position"] = slot
        return entry

    return _txn(change)


def clear(project: str | None = None) -> list:
    """Cancel every ``queued`` entry (of `project`, if given); a ``running`` one is never touched. Returns the cancelled."""
    def change(data):
        now = _now()
        found = [e for e in data["entries"] if e["state"] == "queued" and (project is None or e["project"] == project)]
        for entry in found:
            entry["state"] = "cancelled"
            entry["finishedAt"] = now
        return found

    return _txn(change)


def next_queued():
    """The first queued entry, without taking it; ``None`` if there is none."""
    return _txn(_first_queued)


def claim():
    """Mark the first queued entry ``running`` with this process's pid; returns it, or ``None`` (also while the queue
    is paused: the mark is checked under the queue lock, so a `pause` that returned stops every later claim)."""
    def change(data):
        entry = None if is_paused() else _first_queued(data)
        if entry is not None:
            entry["state"] = "running"
            entry["pid"] = os.getpid()
            entry["startedAt"] = _now()
        return entry

    return _txn(change)


def make_error(code: str, errors=(), **params) -> dict:
    """The ``error`` of an entry: ``{"code", "params"}`` (JSON-serialisable: values that are not become text),
    plus ``"errors": [{"path", "code", "params"}]`` when there are schema errors (`GimgError.errors`)."""
    error = {"code": code, "params": params}
    if errors:
        error["errors"] = [{"path": e.path, "code": e.code, "params": e.params} for e in errors]
    return json.loads(json.dumps(error, default=str))


def error_text(error, lang: str | None = None) -> str:
    """Render an entry's ``error`` (or the entry itself) with i18n; ``""`` if there is no error."""
    if isinstance(error, dict) and "state" in error:
        error = error.get("error")
    if not error:
        return ""
    if isinstance(error, str):  # older or hand-edited queue.json
        return error
    if not isinstance(error, dict) or not isinstance(error.get("code"), str):
        return str(error)
    code, params = error["code"], error.get("params")
    params = params if isinstance(params, dict) else {}
    try:
        text = i18n.t("error." + code, lang, **params)
    except (KeyError, IndexError, TypeError, ValueError):  # missing or oddly named placeholder
        return code
    if text == "error." + code:  # no text for this code: show the code
        text = code
    return "\n".join([text] + _schema_lines(error.get("errors"), lang))


def _schema_lines(errors, lang) -> list:
    """Texts of the stored schema errors; an old or odd shape (not a list of dicts) is skipped item by item."""
    lines = []
    for item in errors if isinstance(errors, list) else ():
        try:
            lines.append(schema.format_error(schema.ValidationError(
                str(item["path"]), str(item["code"]), dict(item["params"])), lang))
        except (KeyError, IndexError, TypeError, ValueError, AttributeError):
            continue
    return lines


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
        entry.pop("progress", None)
        entry.pop("preview", None)
        return entry

    return _txn(change)


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def _set_running(entry_id, field: str, value) -> dict:
    def change(data):
        entry = _find(data, entry_id)
        if entry["state"] != "running":
            raise GimgError("queue.not_running", id=entry["id"], state=entry["state"])
        if entry.get(field) != value:  # a pulse with nothing new does not rewrite the file
            entry[field] = value
        return entry

    return _txn(change)


def set_progress(entry_id, progress: dict) -> dict:
    """Store ``{"step": n, "steps": N, "etaS": seconds | None}`` in a running entry (the engine's progress bar).
    Only the three keys are kept; ``0 <= step <= steps``, ``steps >= 1``; ``etaS`` is ``None`` or a number >= 0.
    Anything else is ``queue.bad_progress``; a finished or queued entry is ``queue.not_running``."""
    ok = (isinstance(progress, dict) and set(progress) == {"step", "steps", "etaS"}
          and all(type(progress[k]) is int for k in ("step", "steps"))
          and 0 <= progress["step"] <= progress["steps"] and progress["steps"] >= 1
          and (progress["etaS"] is None or _number(progress["etaS"])))
    if not ok:
        raise GimgError("queue.bad_progress", progress=json.dumps(progress, default=str))
    return _set_running(entry_id, "progress", dict(progress))


def set_preview(entry_id, path) -> dict:
    """Store the path of the engine's preview image in a running entry (the file may not exist yet)."""
    if not isinstance(path, str) or not path or "\x00" in path or "\n" in path:
        raise GimgError("queue.bad_progress", progress=repr(path))
    return _set_running(entry_id, "preview", path)


def is_cancel_requested(entry_id) -> bool:
    """Polled by the worker every few ms: a plain locked read, it never tries the worker lock."""
    return _txn(lambda data: bool(_find(data, entry_id).get("cancelRequested")))


def entry_view(entry: dict, lang: str | None = None) -> dict:
    """The JSON form of an entry for `gimg queue list --json` and ``GET /api/queue``: the entry plus ``errorText``."""
    item = dict(entry)
    text = error_text(entry, lang)
    if text:
        item["errorText"] = text
    return item


def estimate_for(entry: dict, provider: str | None = None, memo: dict | None = None):
    """Median duration (ms) of similar past attempts, or ``None``. `provider` defaults to the configured engine's.
    With a `memo` dict, entries that ask the same question share one read of the log."""
    if provider is None:
        provider = engine_mod.get_engine().provider
    steps = (entry.get("params") or {}).get("steps")
    args = (entry["project"], provider, entry["profile"], steps, bool(entry.get("references")),
            entry.get("draft") is True, entry.get("initImage") is not None)
    if memo is None:
        return log.estimate(*args)
    if args not in memo:
        memo[args] = log.estimate(*args)
    return memo[args]


def submit_order(project: str, order: dict, draft=None, template=None, model=None) -> tuple:
    """`gimg order submit` and ``POST /api/projects/{p}/orders``: store the order and enqueue its attempts.
    Returns ``(entries, provider)``; a bad engine setting fails before anything is stored or queued."""
    provider = engine_mod.get_engine().provider
    if draft is not None:  # the option is the order's own field, so it is stored with the order
        order["draft"] = draft
    candidates = orders.check_order(project, order)  # limits, prompt length and seed range, before anything is stored
    if model is not None:  # F4d: the model of the attempts (not stored in the order); unknown fails before storing
        models_mod.check_known(model)
    for spec in candidates:  # the same checks as `enqueue`, on the candidates: a refused order is never stored
        if template is not None:
            spec["template"] = template
        if model is not None:
            spec["params"]["model"] = model
    check_specs(project, order["profile"], candidates)
    record = orders.submit(project, order)
    specs = orders.attempt_specs(project, record["key"], record["profile"], order.get("count", 1), template=template,
                                 model=model)
    return enqueue(project, record["key"], record["profile"], specs), provider


def new_attempts(project: str, key: str, profile: str, count: int = 1, *, seed=None, prompt=None, params=None,
                 draft=None, template=None, model=None) -> tuple:
    """`gimg attempt new` and ``POST …/attempts``: enqueue `count` more attempts. Returns ``(entries, provider)``."""
    provider = engine_mod.get_engine().provider
    specs = orders.attempt_specs(project, key, profile, count, seed=seed, prompt=prompt, params=params, draft=draft,
                                 template=template, model=model)
    return enqueue(project, key, profile, specs), provider


def queued_view(entries: list, provider: str, lang: str | None = None) -> dict:
    """The JSON of a fresh enqueue: ``{"entries", "estimateMs"}`` (the estimate of the first entry)."""
    estimate = estimate_for(entries[0], provider) if entries else None
    return {"entries": [entry_view(e, lang) for e in entries], "estimateMs": estimate}
