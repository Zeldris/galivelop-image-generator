"""The queue worker: one process at a time (``<data>/worker.lock``, non-blocking flock).

Per entry: claim -> machine profile and limits again (the profile may have changed since enqueue) -> resolve
references (`paths.inside`, must be files; D25) -> engine -> `orders.add_attempt` -> log line -> finish.

Image id: `orders.add_attempt` assigns the id, so the engine writes to a hidden temp file inside the
order's ``attempts/`` folder (``.pending-<entry>.png``, same filesystem) and the worker `os.replace`s it onto
``attempts/<id>.png`` right after `add_attempt`. The temp file is removed on every failure or cancel.
If that move itself fails, the entry fails with ``worker.image_move`` (the attempt row stays, with no image).

Log: one line for every attempt that fails (limits, references, engine, timeout) or succeeds, with
``app.error`` for the failures; a cancel writes no line. The queue ``error`` is the `GimgError` code or the
engine message (``timeout`` for `EngineTimeout`).
"""
from __future__ import annotations

import contextlib
import fcntl
import os

from . import engine as engine_mod
from . import fsutil, limits, log, orders, paths, projects, queue
from .errors import GimgError


def lock_path():
    return paths.data_dir() / "worker.lock"


@contextlib.contextmanager
def _single_worker():
    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise GimgError("worker.already_running", path=str(path))
        yield
    finally:
        os.close(fd)


def _references(project: dict, entry: dict) -> list:
    found = []
    for ref in entry["references"]:
        target = paths.inside(project["root"], ref)
        if not target.is_file():
            raise GimgError("worker.reference_missing", path=ref)
        found.append(str(target))
    return found


def _unlink(path) -> None:
    with contextlib.suppress(OSError):
        os.unlink(path)


def _log_failure(entry: dict, machine: dict, provider: str, message: str) -> None:
    try:
        record = log.record_for(entry["key"], entry["profile"], entry, machine, provider, error=message)
        log.append(entry["project"], record)
    except Exception:  # the log must never hide the real failure
        pass


def _process(entry: dict, eng) -> None:
    entry_id = entry["id"]
    machine = {}
    tmp = None
    try:
        machine = limits.load_machine()
        limits.check(entry, machine)
        project = projects.get(entry["project"])
        references = _references(project, entry)
        orders.get(entry["project"], entry["key"], entry["profile"])
        final_probe = orders.attempt_image_path(entry["project"], entry["key"], entry["profile"], 0)
        tmp = final_probe.parent / (".pending-%d.png" % entry_id)
        params = entry["params"]
        job = engine_mod.EngineJob(
            prompt=entry["prompt"], width=params.get("width"), height=params.get("height"),
            seed=entry["seed"], output=str(tmp), steps=params.get("steps"), cfg=params.get("cfg"),
            sampler=params.get("sampler"), model=params.get("model"), references=references,
            machine=machine, timeout_s=machine.get("timeoutS"))
        result = eng.generate(job, lambda: queue.is_cancel_requested(entry_id))
        if queue.is_cancel_requested(entry_id):
            raise engine_mod.Cancelled()
        attempt_id = orders.add_attempt(entry["project"], entry["key"], entry["profile"], {
            "seed": entry["seed"], "prompt": entry["prompt"], "params": params,
            "references": entry["references"]})
        try:
            os.replace(tmp, orders.attempt_image_path(
                entry["project"], entry["key"], entry["profile"], attempt_id))
        except OSError as exc:
            raise GimgError("worker.image_move", reason=str(exc))
        tmp = None
        log.append(entry["project"], log.record_for(
            entry["key"], entry["profile"], entry, machine, eng.provider, result=result))
        queue.finish(entry_id, "done", attempt_id=attempt_id)
    except engine_mod.Cancelled:
        queue.finish(entry_id, "cancelled")
    except GimgError as exc:
        _log_failure(entry, machine, eng.provider, exc.code)
        queue.finish(entry_id, "failed", error=exc.code)
    except engine_mod.EngineError as exc:  # includes EngineTimeout
        _log_failure(entry, machine, eng.provider, exc.message)
        queue.finish(entry_id, "failed", error=exc.message)
    except Exception as exc:  # a bug must not leave the entry running or kill the loop
        message = "%s: %s" % (type(exc).__name__, exc)
        _log_failure(entry, machine, eng.provider, message)
        queue.finish(entry_id, "failed", error=message)
    finally:
        if tmp is not None:
            _unlink(tmp)


def run(once: bool = False, engine=None) -> int:
    """Process queued entries (one with `once`, else until none is left); returns how many were handled.

    Raises ``GimgError("worker.already_running")`` if another process holds the worker lock."""
    with _single_worker():
        eng = engine or engine_mod.get_engine()
        handled = 0
        while True:
            entry = queue.claim()
            if entry is None:
                return handled
            _process(entry, eng)
            handled += 1
            if once:
                return handled
