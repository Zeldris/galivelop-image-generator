"""The queue worker: one process at a time (``<data>/worker.lock``, non-blocking flock).

Right after taking its lock the worker recovers the queue (`queue.recover_orphans`): holding the lock proves no
other worker is alive, so every ``running`` entry is dead and goes back to ``queued`` (``cancelled`` if a cancel was
requested), and the ``.pending-<entry>.png`` files of those entries are deleted (only theirs: cheaper than walking
every order, and a crash can only leave a pending file for an entry that was running).

Per entry: claim -> if an attempt with ``queueEntry == entry id`` already exists (crash after `add_attempt`), skip
the engine and finish ``done`` -> machine profile and limits again (the profile may have changed since enqueue) ->
resolve references (`paths.inside`, must be files; D25) -> engine -> metadata chunk in the PNG -> `orders.add_attempt` -> log line -> finish.

While the engine runs the entry shows its ``progress`` (the job's ``on_progress``, `queue.set_progress`) and ``preview`` (the
path the engine writes its preview to, `queue.set_preview`; the file appears when the engine makes it and is deleted with
the run). Both are best effort: a queue error there never fails the generation.

Metadata (F2.4): before the image is moved into place the worker writes a ``gimg`` text chunk into the pending PNG
(`png.add_text_chunk`; JSON with seed, steps, cfg, sampler, model, width, height, prompt, references as file names, engine and
engine version, and ``project``/``key``/``profile``). It lives here, not in the engines, so every engine gets it and it is
written once, atomically, on the file that is about to become the attempt's image. If it cannot be written (a PNG the engine
damaged) the attempt goes on without it and a line goes to stderr. The attempt also records ``command``, ``modelFiles`` and
``log`` (``attempts/q<entry>.log``, only if the log was kept) when the engine reports them.

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
a `GimgError` keeps its code, params and schema errors, `EngineTimeout` is ``engine.timeout``, an `EngineError` with a `code` keeps it, any other is
``engine.failed`` with ``{"message"}``, anything else ``worker.unexpected`` with ``{"message": "Type: msg"}``.
Log: one line for every attempt that fails (limits, references, engine, timeout) or succeeds; for failures
``app.error`` is the English rendering of that error (e.g. "the attempt asks for 99 steps ..."); a cancel writes no line.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import signal
import sys
import threading

from . import engine as engine_mod
from . import fsutil, i18n, limits, log, orders, paths, png, projects, queue
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
    if isinstance(exc, engine_mod.EngineError) and exc.code:
        return queue.make_error(exc.code, **exc.params)
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


def _progress_to_queue(entry_id):
    def report(progress):
        with contextlib.suppress(Exception):
            queue.set_progress(entry_id, progress)
    return report


def _expose_preview(entry_id, eng, tmp) -> None:
    preview = eng.preview_path(tmp) if hasattr(eng, "preview_path") else None
    if preview is not None:
        with contextlib.suppress(Exception):
            queue.set_preview(entry_id, str(preview))


def metadata_for(entry: dict, result) -> dict:
    """What the ``gimg`` chunk of the PNG says: the attempt's parameters (the engine's effective steps, cfg and sampler
    over the entry's), the reference file names and the engine."""
    params = dict(entry["params"])
    params.update({k: v for k, v in (getattr(result, "params", None) or {}).items() if v is not None})
    meta = {"project": entry["project"], "key": entry["key"], "profile": entry["profile"],
            "seed": entry["seed"], "prompt": entry["prompt"],
            "references": [str(ref).rsplit("/", 1)[-1] for ref in entry["references"]],
            "engineVersion": getattr(result, "engine_version", None)}
    if entry.get("draft") is True:
        meta["draft"] = True
    for name in ("model", "width", "height", "steps", "cfg", "sampler"):
        if params.get(name) is not None:
            meta[name] = params[name]
    return meta


def _generate(entry: dict, eng, machine: dict, state: dict, lang=None):
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
        machine=machine, timeout_s=machine.get("timeoutS"), on_progress=_progress_to_queue(entry_id))
    _expose_preview(entry_id, eng, tmp)
    state["result"] = eng.generate(job, lambda: queue.is_cancel_requested(entry_id))
    if queue.is_cancel_requested(entry_id):
        raise engine_mod.Cancelled()
    try:
        png.add_text_chunk(tmp, "gimg", json.dumps(metadata_for(entry, state["result"]), ensure_ascii=False,
                                                   sort_keys=True))
    except (GimgError, OSError) as exc:
        reason = exc.params.get("reason", exc.code) if isinstance(exc, GimgError) else str(exc)
        print(i18n.t("worker.metadata_failed", lang, id=entry_id, reason=reason), file=sys.stderr)
    final = tmp.parent / ("q%d.png" % entry_id)
    try:
        os.replace(tmp, final)
    except OSError as exc:
        raise GimgError("worker.image_move", reason=str(exc))
    engine_log = getattr(state["result"], "log_path", None)
    kept_log = None
    if engine_log:  # best effort: the log is a nicety, the attempt does not depend on it
        try:
            os.replace(engine_log, tmp.parent / ("q%d.log" % entry_id))
            kept_log = "attempts/q%d.log" % entry_id
        except OSError:
            pass
    state["tmp"] = None
    state["final"] = final
    result = state["result"]
    attempt_id = orders.add_attempt(project_name, key, profile, {
        "seed": entry["seed"], "prompt": entry["prompt"], "params": params,
        "references": entry["references"], "engine": eng.provider,
        "engineVersion": result.engine_version, "command": getattr(result, "command", None),
        "modelFiles": getattr(result, "model_files", None), "log": kept_log,
        "draft": entry.get("draft") is True}, entry_id=entry_id)
    state["final"] = None
    return attempt_id


def _process(entry: dict, eng, lang=None) -> None:
    entry_id = entry["id"]
    machine = {}
    state = {"tmp": None, "final": None, "result": None}
    try:
        attempt_id = _generate(entry, eng, machine, state, lang)
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


def _terminate(signum, frame):
    raise SystemExit(128 + signum)


@contextlib.contextmanager
def _exit_on_signals():
    """SIGTERM and SIGHUP end the worker through `SystemExit`, like Ctrl-C does through `KeyboardInterrupt`: the
    ``finally`` blocks run, so the engine kills the process group of `sd-cli` (``start_new_session``) instead of
    leaving it alive with its memory. The entry in progress stays ``running`` (as after Ctrl-C) and
    `queue.recover_orphans` requeues it on the next run. Only in the main thread; the old handlers come back on exit."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    previous = {}
    try:
        for name in ("SIGTERM", "SIGHUP"):
            if hasattr(signal, name):
                num = getattr(signal, name)
                previous[num] = signal.signal(num, _terminate)
        yield
    finally:
        for num, handler in previous.items():
            signal.signal(num, handler)


def run(once: bool = False, engine=None, lang=None) -> int:
    """Process queued entries (one with `once`, else until none is left); returns how many were handled.

    `lang` is the language of the messages the worker prints (the CLI passes its ``--lang``).
    Raises ``GimgError("worker.already_running")`` if another process holds the worker lock."""
    with _single_worker(), _exit_on_signals():
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
