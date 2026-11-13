"""The local service (F3.4): ``gimg serve``, its state file, its lock and the worker it launches.

* ``<data>/serve.lock``: non-blocking ``flock`` held for the whole life of the process; a second `run` is refused
  with ``serve.already_running``. Alive = the lock is held **and** ``GET /api/health`` answers.
* ``<data>/serve.json`` (0600, `fsutil.write_json`): ``{"pid", "port", "url", "version", "build", "startedAt"}``. One without
  the lock is a dead process's and is ignored (and overwritten).
* The server never generates: `maybe_launch_worker` starts ``python -m gimg work`` as a separate process (own
  session, output to ``<data>/worker.log``) when something is ``queued`` and nobody holds ``worker.lock``. It runs
  after each enqueue through the API (`kick`) and on a 2 s beat. If the lock state cannot be known
  (`queue.worker_alive` is ``None``) nothing is launched.
* It stops on SIGTERM/SIGINT or after the idle time (no request, no worker, nothing queued/running; with the queue
  paused, what is queued does not count): it stops
  accepting, waits up to `STOP_WAIT_S` for requests in progress, deletes ``serve.json`` and releases the lock. It
  never touches the worker.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone

from . import __version__, build_id, fsutil, i18n, paths, queue
from .errors import GimgError

DEFAULT_PORT = 8737
DEFAULT_IDLE_MIN = 15
BEAT_S = 2.0
TICK_S = 0.2
STOP_WAIT_S = 10.0
LOCK_RETRY_S = 0.3  # how long a fresh service keeps trying `serve.lock` before it says another one is running
HEALTH_WAIT_S = 5.0
RETRY_AFTER_FAILURE_S = 30.0  # a worker that exited with an error is not relaunched sooner

_launch_lock = threading.Lock()
_launcher = None  # set while `run` is serving; `kick` does nothing otherwise


def state_path():
    return paths.data_dir() / "serve.json"


def lock_path():
    return paths.data_dir() / "serve.lock"


def log_path():
    return paths.data_dir() / "serve.log"


def worker_log_path():
    return paths.data_dir() / "worker.log"


# --- settings ---
def _config() -> dict:
    path = paths.config_dir() / "config.json"
    try:
        data = fsutil.read_json(path, {})
    except (OSError, ValueError) as exc:
        raise GimgError("machine.config_unreadable", path=str(path), reason=str(exc))
    section = data.get("serve") if isinstance(data, dict) else None
    return section if isinstance(section, dict) else {}


def _number(value, code: str, low: int, high: int, **params) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise GimgError(code, value=str(value), **params)
    try:
        number = int(value)
    except ValueError:
        raise GimgError(code, value=str(value), **params)
    if not low <= number <= high:
        raise GimgError(code, value=str(value), **params)
    return number


def resolve_port(arg=None) -> int:
    """``--port``, else ``GIMG_PORT``, else ``serve.port`` of the config, else 8737 (0 = any free port, for tests)."""
    for value in (arg, os.environ.get("GIMG_PORT") or None, _config().get("port")):
        if value is not None:
            return _number(value, "serve.bad_port", 0, 65535)
    return DEFAULT_PORT


def resolve_idle_s(arg=None) -> float:
    """Idle seconds before stopping: ``GIMG_SERVE_IDLE_S`` (tests), else minutes from ``--idle-min``, else
    ``serve.idleMinutes``, else 15. 0 = never."""
    seconds = os.environ.get("GIMG_SERVE_IDLE_S")
    if seconds:
        try:
            value = float(seconds)
        except ValueError:
            raise GimgError("serve.bad_idle", value=seconds)
        if value < 0:
            raise GimgError("serve.bad_idle", value=seconds)
        return value
    for value in (arg, _config().get("idleMinutes")):
        if value is not None:
            return 60.0 * _number(value, "serve.bad_idle", 0, 100000)
    return 60.0 * DEFAULT_IDLE_MIN


# --- state and lock ---
def read_state():
    """The content of ``serve.json`` if it is a valid state object, else ``None``."""
    try:
        data = fsutil.read_json(state_path(), None)
    except (OSError, ValueError):
        return None
    if (isinstance(data, dict) and isinstance(data.get("pid"), int) and isinstance(data.get("port"), int)
            and isinstance(data.get("url"), str)):
        return data
    return None


def lock_held() -> bool:
    """Is ``serve.lock`` taken by a live process? A pure read: it creates nothing (not knowing counts as not taken)."""
    return fsutil.held(lock_path()) is True


def health(port: int, timeout: float = 1.0):
    """The parsed ``/api/health`` of the local server on `port`, or ``None``."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/api/health" % port, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - anything wrong means "does not answer"
        return None
    return data if isinstance(data, dict) and data.get("ok") is True else None


def _live():
    """``(state, health)`` of the running service, or ``(None, None)``. The health answer must come from the pid in
    the state: a ``serve.json`` read just before another CLI replaced the service on the same port is old (F3.5), so
    it is read again."""
    for attempt in range(3):
        if attempt:
            time.sleep(0.1)  # let the CLI that is replacing the service write its `serve.json`
        state = read_state()
        if state is None or not lock_held():
            return None, None
        answer = health(state["port"])
        if answer is None:
            return None, None
        if answer.get("pid") == state["pid"]:
            return state, answer
    return None, None


def status():
    """The state of the running service (``serve.json``) or ``None`` when it is not alive."""
    return _live()[0]


def stop(wait_s: float = STOP_WAIT_S + 2.0, expected_pid=None) -> dict:
    """SIGTERM to the service in ``serve.json`` if its lock is still taken, and wait for it to let go.
    Raises ``serve.not_running`` otherwise. Returns the state it stopped."""
    state = read_state()
    if state is None or not lock_held() or (expected_pid is not None and state["pid"] != expected_pid):
        raise GimgError("serve.not_running")
    answer = health(state["port"])
    if answer is None or answer.get("pid") != state["pid"]:  # a stale file whose pid may belong to someone else
        raise GimgError("serve.not_running")
    try:
        os.kill(state["pid"], signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        raise GimgError("serve.not_running")
    deadline = time.monotonic() + wait_s
    while lock_held() and time.monotonic() < deadline:
        time.sleep(0.05)
    return state


# --- the worker ---
class _Launcher:
    def __init__(self, lang: str):
        self.lang = lang
        self.proc = None
        self.not_before = 0.0
        self.last_error = None


def maybe_launch_worker(launcher: _Launcher) -> bool:
    """Start ``gimg work`` if something is queued and no worker is alive. One at a time (`_launch_lock`), and only
    when the worker lock is known to be free. Never raises. Returns whether a worker was launched."""
    with _launch_lock:
        try:
            proc = launcher.proc
            if proc is not None:
                code = proc.poll()
                if code is None:
                    return False  # ours is starting or running
                launcher.proc = None
                if code != 0:
                    launcher.not_before = time.monotonic() + RETRY_AFTER_FAILURE_S
            if time.monotonic() < launcher.not_before:
                return False
            if queue.is_paused() or queue.worker_alive() is not False or not queue.list_entries(["queued"]):
                return False
            with open(worker_log_path(), "ab") as log:
                launcher.proc = subprocess.Popen(
                    [sys.executable, "-m", "gimg", "work", "--lang", launcher.lang],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            return True
        except Exception as exc:  # noqa: BLE001 - a failed launch must not fail a request or stop the service
            text = "%s: %s" % (type(exc).__name__, exc)
            if text != launcher.last_error:  # the 2 s beat must not repeat the same line for ever
                launcher.last_error = text
                print("gimg serve: " + text, file=sys.stderr, flush=True)
            return False


def kick() -> None:
    """After an enqueue: launch the worker now (no-op unless this process is `run`)."""
    launcher = _launcher
    if launcher is not None:
        maybe_launch_worker(launcher)


# --- serving ---
def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextlib.contextmanager
def _single_instance():
    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        # a momentary probe (`lock_held`, shared) must not make a fresh service give up, as in `worker._single_worker`
        deadline = time.monotonic() + LOCK_RETRY_S
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    state = read_state()
                    raise GimgError("serve.already_running", url=state["url"] if state else "?")
                time.sleep(0.02)
        yield
    finally:
        os.close(fd)


def _busy() -> bool:
    """Work the service must not stop under: a worker (or not knowing), or a queued/running entry (or not knowing).
    With the queue paused, a queued entry waits for `resume`, not for the service: only a running one counts, so a
    paused queue does not keep the service alive for ever (`gimg queue resume` starts it again)."""
    if queue.worker_alive() is not False:
        return True
    try:
        return bool(queue.list_entries(["running"] if queue.is_paused() else ["queued", "running"]))
    except Exception:  # noqa: BLE001
        return True


def run(port=None, idle_s=None, lang=None, announce=None) -> dict:
    """Serve in the foreground until SIGTERM/SIGINT or idleness; returns the state it served with.
    `announce(state)` is called once the port is bound and ``serve.json`` is written."""
    global _launcher
    from . import server as server_mod
    port = resolve_port(port)
    idle_s = resolve_idle_s() if idle_s is None else idle_s
    lang = lang or i18n.default_lang()
    with _single_instance():
        try:
            httpd = server_mod.make_server(port)
        except OSError:
            raise GimgError("serve.port_busy", port=port)
        stop_event = threading.Event()
        previous = {}

        def on_signal(*_):
            if stop_event.is_set():  # a second signal while stopping: leave now
                with contextlib.suppress(OSError):
                    os.unlink(state_path())
                os._exit(130)
            stop_event.set()

        if threading.current_thread() is threading.main_thread():
            for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                previous[sig] = signal.signal(sig, on_signal)
        bound = httpd.server_address[1]
        state = {"pid": os.getpid(), "port": bound, "url": "http://127.0.0.1:%d" % bound,
                 "version": __version__, "build": server_mod.BUILD, "startedAt": _now()}
        launcher = _Launcher(lang)
        thread = None
        try:
            fsutil.write_json(state_path(), state)
            os.chmod(state_path(), 0o600)
            thread = server_mod.start_thread(httpd)
            _launcher = launcher
            if announce:
                announce(state)
            last_beat = 0.0
            while not stop_event.wait(TICK_S):
                now = time.monotonic()
                if now - last_beat >= BEAT_S:
                    last_beat = now
                    maybe_launch_worker(launcher)
                if idle_s > 0:
                    quiet, inflight = httpd.activity()
                    if inflight == 0 and quiet >= idle_s and not _busy():
                        break
        finally:
            _launcher = None
            httpd.shutdown() if thread else None  # stop accepting
            deadline = time.monotonic() + STOP_WAIT_S
            while httpd.activity()[1] > 0 and time.monotonic() < deadline:
                time.sleep(0.05)
            httpd.server_close()
            with contextlib.suppress(OSError):
                os.unlink(state_path())
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        return state


# --- background start ---
def _tail(path, lines: int = 5) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return "\n".join(fh.read().splitlines()[-lines:])
    except OSError:
        return ""


def wait_status(seconds: float):
    """`status()` of a service that is starting, waiting up to `seconds`; ``None`` if none comes up."""
    deadline = time.monotonic() + seconds
    while True:
        current = status()
        if current is not None or time.monotonic() >= deadline:
            return current
        time.sleep(0.05)


def detach(port=None, idle_min=None, lang=None) -> dict:
    """Start ``gimg serve`` in the background and wait up to 5 s for its ``/api/health``; returns its state."""
    current = status()
    if current is not None:
        raise GimgError("serve.already_running", url=current["url"])
    port = resolve_port(port)
    resolve_idle_s(idle_min)  # fail here on a bad value instead of in the log
    cmd = [sys.executable, "-m", "gimg", "serve", "--port", str(port), "--lang", lang or i18n.default_lang()]
    if idle_min is not None:
        cmd += ["--idle-min", str(idle_min)]
    paths.data_dir().mkdir(parents=True, exist_ok=True)
    with open(log_path(), "ab") as log:
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
    deadline = time.monotonic() + HEALTH_WAIT_S
    while time.monotonic() < deadline and proc.poll() is None:
        state = read_state()
        if state is not None and state["pid"] == proc.pid and health(state["port"]) is not None:
            return state
        time.sleep(0.05)
    if proc.poll() is not None and lock_held():  # it may have lost the lock to a service another `--detach` just started
        alive = wait_status(HEALTH_WAIT_S)
        if alive is not None:
            return alive
    if proc.poll() is None:
        with contextlib.suppress(OSError):
            proc.terminate()
        with contextlib.suppress(Exception):
            proc.wait(timeout=STOP_WAIT_S)
    else:
        proc.wait()
    raise GimgError("serve.start_failed", log=_tail(log_path()))


# --- on demand (F3.5) ---
def autostart_enabled() -> bool:
    """``GIMG_AUTOSTART=0|false|no|off`` turns the on-demand start off (the test suite sets it)."""
    return os.environ.get("GIMG_AUTOSTART", "").strip().lower() not in ("0", "false", "no", "off")


def ensure_running(lang=None, warn=None) -> dict:
    """The state of a live service, starting one in the background if there is none. A running service of another
    version, or of the same version but older code (`build_id`), is stopped and replaced unless a worker is alive (or
    may be): then it is kept and `warn(text)` says so.
    Raises ``serve.start_failed`` / ``serve.port_busy`` when none comes up."""
    lang = lang or i18n.default_lang()
    current, answer = _live()
    if current is not None:
        running = answer.get("version") or current.get("version")
        built = answer.get("build") or current.get("build")
        mine = build_id()
        if running == __version__ and built == mine:
            return current
        if queue.worker_alive() is not False:
            _warn_other_code(warn, lang, running, built, mine)
            return current
        # one CLI at a time replaces it (a second SIGTERM would cut the old one's requests in progress)
        paths.data_dir().mkdir(parents=True, exist_ok=True)
        fd = os.open(str(paths.data_dir() / "serve.replace.lock"), os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            fresh = status()
            if fresh is not None and fresh["pid"] != current["pid"]:  # another CLI already replaced it
                if (fresh.get("version"), fresh.get("build")) != (__version__, mine):  # with other code: say so
                    _warn_other_code(warn, lang, fresh.get("version"), fresh.get("build"), mine)
                return fresh
            with contextlib.suppress(GimgError):
                stop(expected_pid=current["pid"])
            deadline = time.monotonic() + STOP_WAIT_S + 2.0
            while lock_held() and time.monotonic() < deadline:
                time.sleep(0.05)
            return _detach_or_join(lang)
        finally:
            os.close(fd)
    return _detach_or_join(lang)


def _warn_other_code(warn, lang, running, built, mine) -> None:
    """`warn` that the service kept runs other code than this CLI: another version, or the same one with another
    build (a checkout that changed), then both builds are named."""
    if not warn:
        return
    if running == __version__:
        running, installed = "%s+%s" % (running, built or "?"), "%s+%s" % (__version__, mine)
    else:
        installed = __version__
    warn(i18n.t("cli.warn.service_old_version", lang, running=running or "?", installed=installed))


def _detach_or_join(lang) -> dict:
    try:
        return detach(lang=lang)
    except GimgError as exc:
        if exc.code == "serve.already_running":  # another process started it first
            alive = wait_status(HEALTH_WAIT_S)
            if alive is not None:
                return alive
        raise
