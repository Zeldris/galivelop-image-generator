"""The queue worker: one process at a time (``<data>/worker.lock``, non-blocking flock).

Right after taking its lock the worker recovers the queue (`queue.recover_orphans`): holding the lock proves no
other worker is alive, so every ``running`` entry is dead and goes back to ``queued`` (``cancelled`` if a cancel was
requested), and the ``.pending-<entry>.png`` files of those entries are deleted (only theirs: cheaper than walking
every order, and a crash can only leave a pending file for an entry that was running).

Per entry: claim -> if an attempt with ``queueEntry == entry id`` already exists (crash after `add_attempt`), skip
the engine and finish ``done`` -> machine profile and limits again (the profile may have changed since enqueue) ->
resolve references (`paths.inside`, must be files; D25) -> engine -> `orders.add_attempt` -> log line -> finish.

Image: named after the queue entry id, unique across the generator. The engine writes
``attempts/.pending-<entry>.png``; the worker `os.replace`s it onto ``attempts/q<entry>.png`` and only then calls
`orders.add_attempt(..., entry_id=entry)`, idempotent per entry (the attempt records ``image`` and ``queueEntry``). A crash
at any point leaves either no attempt or one with its image, and a retry never duplicates it. The engine's ``.pending-<entry>.log`` is renamed to ``attempts/q<entry>.log`` right after the image. The pending file (with its
``.log`` and ``.preview.png``) is removed on every failure or cancel; if `add_attempt` fails the moved image is removed too.

Once the attempt exists nothing can fail the entry: the success log line and `queue.finish` are best effort (an
entry whose `finish` failed stays ``running`` and recovery deals with it), and no failure line is written. No
`finish` error ever stops `run()`.

Errors: the entry ``error`` is ``{"code", "params"}`` plus ``"errors"`` (schema errors as path/code/params)
when there are any (`queue.make_error`; render with `queue.error_text`):
a `GimgError` keeps its code, params and schema errors, `EngineTimeout` is ``engine.timeout``, any other `EngineError` is
``engine.failed`` with ``{"message"}``, anything else ``worker.unexpected`` with ``{"message": "Type: msg"}``.
Log: one line for every attempt that fails (limits, references, engine, timeout) or succeeds; for failures
``app.error`` is the English rendering of that error (e.g. "the attempt asks for 99 steps ..."); a cancel writes no line.
"""
from __future__ import annotations

import contextlib
import fcntl
import os
import sys

from . import engine as engine_mod
from . import fsutil, i18n, limits, log, orders, paths, projects, queue
from .errors import GimgError


def lock_path():
    return queue.worker_lock_path()


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


def _error_for(exc: BaseException) -> dict:
    if isinstance(exc, GimgError):
        return queue.make_error(exc.code, exc.errors, **exc.params)
    if isinstance(exc, engine_mod.EngineTimeout):
        return queue.make_error("engine.timeout")
    if isinstance(exc, engine_mod.EngineError):
        return queue.make_error("engine.failed", message=exc.message)
    return queue.make_error("worker.unexpected", message="%s: %s" % (type(exc).__name__, exc))


def _log_failure(entry: dict, machine: dict, provider: str, error: dict) -> None:
    try:
        text = queue.error_text(error, "en") or error["code"]
        record = log.record_for(entry["key"], entry["profile"], entry, machine, provider, error=text)
        log.append(entry["project"], record)
    except Exception:  # the log must never hide the real failure
        pass


def _finish(entry_id, state, lang=None, **kw) -> None:
    """`queue.finish` that never raises: the entry stays ``running`` and recovery deals with it."""
    try:
        queue.finish(entry_id, state, **kw)
    except Exception as exc:
        print(i18n.t("worker.finish_failed", lang, id=entry_id, reason=exc), file=sys.stderr)


def _generate(entry: dict, eng, machine: dict, state: dict):
    """Everything up to and including `add_attempt`; returns the attempt id. `state["tmp"]`/`["final"]` are
    the files to clean up if it raises."""
    entry_id = entry["id"]
    project_name, key, profile = entry["project"], entry["key"], entry["profile"]
    machine.update(limits.load_machine())
    orders.get(project_name, key, profile)
    existing = orders.attempt_for_entry(project_name, key, profile, entry_id)
    if existing is not None:  # a crash after add_attempt: the attempt and its image are already there
        return existing["id"]
    limits.check(entry, machine)
    project = projects.get(project_name)
    references = _references(project, entry)
    tmp = orders.pending_image_path(project_name, key, profile, entry_id)
    state["tmp"] = tmp
    params = entry["params"]
    job = engine_mod.EngineJob(
        prompt=entry["prompt"], width=params.get("width"), height=params.get("height"),
        seed=entry["seed"], output=str(tmp), steps=params.get("steps"), cfg=params.get("cfg"),
        sampler=params.get("sampler"), model=params.get("model"), references=references,
        machine=machine, timeout_s=machine.get("timeoutS"))
    state["result"] = eng.generate(job, lambda: queue.is_cancel_requested(entry_id))
    if queue.is_cancel_requested(entry_id):
        raise engine_mod.Cancelled()
    final = tmp.parent / ("q%d.png" % entry_id)
    try:
        os.replace(tmp, final)
    except OSError as exc:
        raise GimgError("worker.image_move", reason=str(exc))
    engine_log = getattr(state["result"], "log_path", None)
    if engine_log:  # best effort: the log is a nicety, the attempt does not depend on it
        try:
            os.replace(engine_log, tmp.parent / ("q%d.log" % entry_id))
        except OSError:
            pass
    state["tmp"] = None
    state["final"] = final
    attempt_id = orders.add_attempt(project_name, key, profile, {
        "seed": entry["seed"], "prompt": entry["prompt"], "params": params,
        "references": entry["references"], "engine": eng.provider,
        "engineVersion": state["result"].engine_version}, entry_id=entry_id)
    state["final"] = None
    return attempt_id


def _process(entry: dict, eng, lang=None) -> None:
    entry_id = entry["id"]
    machine = {}
    state = {"tmp": None, "final": None, "result": None}
    try:
        attempt_id = _generate(entry, eng, machine, state)
    except engine_mod.Cancelled:
        _finish(entry_id, "cancelled", lang)
        return
    except Exception as exc:  # a bug must not leave the entry running or kill the loop
        error = _error_for(exc)
        _log_failure(entry, machine, eng.provider, error)
        _finish(entry_id, "failed", lang, error=error)
        return
    finally:
        for leftover in (state["tmp"], state["final"]):
            if leftover is not None:
                _unlink(leftover)
        if state["tmp"] is not None:  # the engine's log and preview of a failed or cancelled run
            for suffix in (".log", ".preview.png"):
                _unlink(state["tmp"].with_suffix(suffix))
    # the attempt exists: from here nothing may fail the entry
    if state["result"] is not None:
        try:
            log.append(entry["project"], log.record_for(
                entry["key"], entry["profile"], entry, machine, eng.provider, result=state["result"]))
        except Exception as exc:
            print(i18n.t("worker.log_failed", lang, id=entry_id, reason=exc), file=sys.stderr)
    _finish(entry_id, "done", lang, attempt_id=attempt_id)


def run(once: bool = False, engine=None, lang=None) -> int:
    """Process queued entries (one with `once`, else until none is left); returns how many were handled.

    `lang` is the language of the messages the worker prints (the CLI passes its ``--lang``).
    Raises ``GimgError("worker.already_running")`` if another process holds the worker lock."""
    with _single_worker():
        queue.recover_orphans()
        eng = engine or engine_mod.get_engine()
        handled = 0
        while True:
            entry = queue.claim()
            if entry is None:
                return handled
            _process(entry, eng, lang)
            handled += 1
            if once:
                return handled
