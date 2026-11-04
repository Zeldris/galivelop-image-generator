"""The real engine: `sd-cli` of stable-diffusion.cpp as a process in its own group (D26, D33, D34).

`SdCppEngine(machine, catalog).generate(job, should_cancel)` resolves ``job.model`` against the machine profile
(`models.resolve`), builds the argv of the "Motor" contract (`docs/plan.md`), runs it with ``stdout`` and ``stderr`` in
``<output stem>.log`` (the worker names the output ``attempts/.pending-<entry>.png``, so the log is
``attempts/.pending-<entry>.log``) and polls it every `poll_s` seconds.

Decisions:

- **Binary:** ``GIMG_SD_CLI`` > ``engine.sdCli`` of the machine profile > ``<data>/engine/<RELEASE>/sd-cli``.
  ``LD_LIBRARY_PATH`` is *replaced* by the binary's folder (D33: Ollama's libraries take the GPU from `sd-cli`).
- **Timeout:** the model's ``timeoutS`` (``engine.models.<id>.timeoutS``, else the profile's ``timeoutS``, resolved by
  `models.resolve`) wins; ``job.timeout_s`` is the fallback when the profile has none. The worker passes the profile's
  general ``timeoutS`` in the job, so giving the job priority would hide the per-model limit. A value that is ``None``,
  ``0`` or negative is "no limit" for that source (a profile never has one: its ``timeoutS`` is >= 1).
- **Machine:** ``job.machine`` (the worker reloads the profile for every entry) if it is not empty, else the one given
  to the constructor.
- **Log:** the engine leaves ``<output stem>.log`` and returns its path in ``EngineResult.log_path``; the worker renames
  it to ``attempts/q<entry>.log`` next to ``q<entry>.png`` after the image is in place, and deletes it on failure or
  cancel (the error already carries the last lines). ``<output stem>.preview.png`` is the preview of ``--preview proj``.
- **Kill:** POSIX: ``os.killpg`` (SIGTERM, then SIGKILL after `kill_grace_s`) to the process group created by
  ``start_new_session``. Where ``os.killpg`` does not exist (Windows) the fallback is ``terminate()`` then ``kill()`` of the
  process only, which leaves its children alive; the project runs on Linux, so that path is untested.
- **Tick hook:** `_on_tick(proc, log_path, job)` runs once per poll: the memory watch and the "reported free 0.00 MB"
  abort (F2.3) and the progress (F2.4) are there.
- **Progress (F2.4):** the new part of the log goes through `parse_progress`: the step bar of `sd-cli` is
  ``|====>   | 3/6 -  24.65s/it - ETA 01:16`` (``\r`` between bars, ``\x1b[K`` after each; ``it/s`` when it is fast). A bar
  counts only when a terminator (``\x1b``, ``\r`` or ``\n``) follows it, so a bar cut by the read boundary is kept in
  ``_Run.bar_carry`` and read whole on the next tick (a cut ``ETA 02:1`` would otherwise read as 2 min 1 s). Only bars
  before "sampling completed" count (the VAE tile bar ``1/36`` comes after); among them the ones whose total is the job's
  steps, else the ones with the total of the first bar; the last wins. The job's ``on_progress`` gets
  ``{"step", "steps", "etaS"}`` (``etaS`` from ``mm:ss`` or ``hh:mm:ss``; ``None`` without ETA, as in the last bar) only when
  ``(step, steps)`` changes, and an exception in it is ignored: progress never fails a generation.
- **Guards before the process (F2.3, D33):** after the argv is built and before the log exists, so a refusal leaves
  nothing behind. (1) ``MemAvailable`` >= ``minFreeMemoryMb`` (the model's, else the profile's; `models.resolve`), else
  ``engine.low_memory``. The reader is ``read_meminfo`` (constructor argument; default `read_meminfo_mb`, which reads
  ``GIMG_MEMINFO`` or ``/proc/meminfo`` and returns ``None`` where there is none or it is unparseable: the check is then
  skipped and a line in the attempt's log says so). (2) Ollama, by ``engine.ollama`` (``abort`` by default, ``unload``,
  ``ignore``): ``GET <url>/api/ps``; a service that is off, slow, unreachable or answers nonsense counts as "nothing
  loaded". The URL is ``GIMG_OLLAMA_URL``, else ``engine.ollamaUrl``, else ``http://localhost:11434`` (http/https only).
- **Watch:** every tick reads ``MemAvailable``: below ``watchMemoryMb`` the group is killed (``engine.watch_memory``), and
  so it is when the new part of the log (read from the last position, not the whole file) has "reported free 0.00 MB"
  (``engine.driver_no_memory``). The lowest value seen, from the first read before the start, is ``min_free_mb``.

Timings come from the log: ``load_ms`` is the sum of the ``loading tensors completed, taking Xs`` lines, ``sample_ms`` is
the last ``sampling completed, taking Xs`` and ``decode_ms`` the last ``decode_first_stage completed, taking Xs``; a line
that is not there leaves its field ``None``.
"""
from __future__ import annotations

import contextlib
import http.client
import json
import os
import re
import signal
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from . import models, paths
from .engine import Cancelled, Engine, EngineError, EngineJob, EngineResult, EngineTimeout
from .errors import GimgError

RELEASE = "master-1000-95ff762"
PROVIDER = "stable-diffusion.cpp"
POLL_S = 0.5
KILL_GRACE_S = 3.0
TAIL_LINES = 5
_PNG = b"\x89PNG\r\n\x1a\n"
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
SAMPLED = "sampling completed"
_BAR = re.compile(r"\|\s*(\d+)/(\d+)\s+-\s+[0-9.]+\s*(?:s/it|it/s)(?:\s+-\s+ETA\s+(\d+(?::\d+){1,2}))?(?=[\x1b\r\n])")
BAR_CARRY_MAX = 512
_LOAD = re.compile(r"loading tensors completed, taking ([0-9.]+)s")
_SAMPLE = re.compile(r"sampling completed, taking ([0-9.]+)s")
_DECODE = re.compile(r"decode_first_stage completed, taking ([0-9.]+)s")
_POSIX = hasattr(os, "killpg")
MEMINFO = "/proc/meminfo"
ZERO_FREE = "reported free 0.00 MB"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_PS_TIMEOUT_S = 2.0
OLLAMA_UNLOAD_TIMEOUT_S = 10.0
OLLAMA_WAIT_S = 15.0  # Ollama unloads asynchronously: generar.sh waits up to 15 s
OLLAMA_WAIT_POLL_S = 1.0
_MEM_AVAILABLE = re.compile(r"^MemAvailable:[ \t]+([0-9]+)[ \t]*kB[ \t]*$", re.MULTILINE)
_URL = re.compile(r"https?://[^\s\x00-\x1f\x7f]+")
_NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # a local service never goes through a proxy


def binary_path(machine: dict) -> Path:
    """``GIMG_SD_CLI``, else ``engine.sdCli`` of the profile, else ``<data>/engine/<RELEASE>/sd-cli``."""
    explicit = os.environ.get("GIMG_SD_CLI") or (machine.get("engine") or {}).get("sdCli")
    if explicit:
        return Path(explicit).expanduser()
    return paths.data_dir() / "engine" / RELEASE / "sd-cli"


def _num(value) -> str:
    return "%g" % value


def _clean_lines(text: str) -> list:
    """Non-empty lines of a log, with progress bars (``\\r``) and ANSI escapes split apart."""
    return [ln.strip() for ln in re.split(r"[\r\n]+", _ANSI.sub("", text)) if ln.strip()]


def parse_timings(text: str) -> dict:
    """``load_ms``, ``sample_ms`` and ``decode_ms`` (integers, or ``None`` when the log lacks the line)."""
    def ms(seconds):
        return int(round(float(seconds) * 1000))

    loads = _LOAD.findall(text)
    sample, decode = _SAMPLE.findall(text), _DECODE.findall(text)
    return {"load_ms": ms(sum(float(x) for x in loads)) if loads else None,
            "sample_ms": ms(sample[-1]) if sample else None,
            "decode_ms": ms(decode[-1]) if decode else None}


def parse_progress(text: str, steps=None, sampled: bool = False):
    """``(progress, sampled)`` of a piece of log: the last complete step bar as ``{"step", "steps", "etaS"}`` (or ``None``)
    and whether "sampling completed" has been seen (`sampled` says it already was: nothing counts then). See the
    module docstring."""
    before, marker, _ = text.partition(SAMPLED)
    if sampled:
        return None, True
    bars = []
    for step, total, eta in _BAR.findall(before):
        step, total = int(step), int(total)
        if total >= 1 and step <= total:
            seconds = None
            if eta:
                seconds = 0
                for part in eta.split(":"):
                    seconds = seconds * 60 + int(part)
            bars.append((step, total, seconds))
    chosen = [b for b in bars if b[1] == steps] if steps else []
    if not chosen and bars:
        chosen = [b for b in bars if b[1] == bars[0][1]]
    progress = {"step": chosen[-1][0], "steps": chosen[-1][1], "etaS": chosen[-1][2]} if chosen else None
    return progress, bool(marker)


def _backend(argv: list) -> str:
    """``cpu`` if the args put the diffusion model on the CPU (``--backend diffusion=cpu`` or ``cpu``), else ``vulkan``
    (the only GPU backend of the release this project installs; ``--max-vram`` is in the command)."""
    for flag, value in zip(argv, argv[1:]):
        if flag == "--backend" and any(t.strip() in ("cpu", "diffusion=cpu") for t in value.split(",")):
            return "cpu"
    return "vulkan"


def _threads(argv: list) -> Optional[int]:
    """The last ``-t`` / ``--threads`` of the argv that is a positive integer, else ``None``."""
    found = None
    for flag, value in zip(argv, argv[1:]):
        if flag in ("-t", "--threads") and value.isdigit() and int(value) > 0:
            found = int(value)
    return found


def _read_log(path) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def parse_meminfo(text: str) -> Optional[int]:
    """``MemAvailable`` of a ``/proc/meminfo`` text in MB (integer), or ``None`` if the line is missing or odd."""
    found = _MEM_AVAILABLE.search(text)
    return int(found.group(1)) // 1024 if found else None


def read_meminfo_mb() -> Optional[int]:
    """Free memory in MB: ``MemAvailable`` of ``GIMG_MEMINFO`` (tests) or ``/proc/meminfo``; ``None`` where it cannot
    be read (no ``/proc``) or parsed."""
    try:
        with open(os.environ.get("GIMG_MEMINFO") or MEMINFO, encoding="utf-8", errors="replace") as fh:
            return parse_meminfo(fh.read())
    except OSError:
        return None


def ollama_url(machine: dict) -> str:
    """``GIMG_OLLAMA_URL``, else ``engine.ollamaUrl``, else `OLLAMA_URL`, without a trailing ``/``; http or https only."""
    url = (os.environ.get("GIMG_OLLAMA_URL") or (machine.get("engine") or {}).get("ollamaUrl") or OLLAMA_URL)
    if not isinstance(url, str) or not _URL.fullmatch(url):
        raise GimgError("engine.ollama_url", url=str(url))
    return url.rstrip("/")


def ollama_loaded(url: str, timeout: float = OLLAMA_PS_TIMEOUT_S) -> list:
    """Names of the models Ollama has in memory (``size`` > 0 in ``/api/ps``). A service that is off, does not
    answer in `timeout` seconds or answers something that is not the expected JSON has none loaded."""
    try:
        with _NO_PROXY.open(url + "/api/ps", timeout=timeout) as resp:
            data = json.loads(resp.read(1 << 20).decode("utf-8"))
    except (OSError, ValueError, http.client.HTTPException):
        return []
    items = data.get("models") if isinstance(data, dict) else None
    names = []
    for item in items if isinstance(items, list) else []:
        size = item.get("size") if isinstance(item, dict) else None
        if isinstance(size, (int, float)) and not isinstance(size, bool) and size > 0:
            name = item.get("name") or item.get("model")
            names.append(name if isinstance(name, str) and name else "(unnamed)")
    return names


def ollama_unload(url: str, name: str, timeout: float = OLLAMA_UNLOAD_TIMEOUT_S) -> None:
    """Ask Ollama to drop `name` (``keep_alive: 0``; embedding models only accept ``/api/embed``). Errors are ignored:
    the caller looks again to see whether it worked."""
    for path, body in (("/api/generate", {"model": name, "keep_alive": 0}),
                       ("/api/embed", {"model": name, "input": "", "keep_alive": 0})):
        req = urllib.request.Request(url + path, data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with _NO_PROXY.open(req, timeout=timeout) as resp:
                resp.read(1 << 16)
        except (OSError, ValueError, http.client.HTTPException):
            pass


@dataclass
class _Run:
    """What the watch keeps for one attempt."""
    watch_mb: Optional[int] = None
    min_free_mb: Optional[int] = None
    log_pos: int = 0
    carry: str = ""
    steps: Optional[int] = None  # the job's steps: the total of the bar to follow
    new: str = ""  # what the last `_new_log_text` read, without the carry
    bar_carry: str = ""  # the end of the log after its last terminator: a bar that may be cut
    sampled: bool = False
    last: Optional[tuple] = None  # (step, steps) last reported

    def seen(self, free: int) -> None:
        self.min_free_mb = free if self.min_free_mb is None else min(self.min_free_mb, free)


class SdCppEngine(Engine):
    provider = PROVIDER

    def __init__(self, machine: Optional[dict] = None, catalog: Optional[dict] = None,
                 poll_s: float = POLL_S, kill_grace_s: float = KILL_GRACE_S,
                 read_meminfo: Optional[Callable[[], Optional[int]]] = None):
        self.machine = machine or {}
        self.catalog = catalog
        self.poll_s = poll_s
        self.kill_grace_s = kill_grace_s
        self.read_meminfo = read_meminfo  # free MB or None; None here means `read_meminfo_mb`
        self.ollama_ps_timeout_s = OLLAMA_PS_TIMEOUT_S
        self.ollama_unload_timeout_s = OLLAMA_UNLOAD_TIMEOUT_S
        self.ollama_wait_s = OLLAMA_WAIT_S
        self.ollama_wait_poll_s = OLLAMA_WAIT_POLL_S
        self._run = _Run()

    # -- pieces -------------------------------------------------------------------------------------------------

    def _resolve(self, job: EngineJob, machine: dict) -> dict:
        if not job.model:
            raise GimgError("model.required", known=", ".join(models.ids(self.catalog)))
        resolved = models.resolve(job.model, machine, self.catalog)
        missing = models.missing_files(resolved)
        if missing:
            raise GimgError("model.not_installed", model=job.model,
                            files=", ".join(str(resolved["files"][k]["path"]) for k in missing),
                            command="instalar.sh --with " + job.model)
        return resolved

    def build_argv(self, job: EngineJob, resolved: dict, machine: dict, binary) -> list:
        """The exact argv of the contract (absolute model paths; `_command` makes them relative for the log)."""
        if not (isinstance(job.width, int) and isinstance(job.height, int) and job.width > 0 and job.height > 0):
            raise EngineError("invalid size %sx%s" % (job.width, job.height))
        files = resolved["files"]
        used = self.effective(job, resolved)
        steps, cfg, sampler = used["steps"], used["cfg"], used["sampler"]
        eng = machine.get("engine") or {}
        out = Path(job.output)
        argv = [str(binary),
                "--diffusion-model", str(files["diffusion"]["path"]),
                "--llm", str(files["text"]["path"]),
                "--vae", str(files["vae"]["path"]),
                "-p", job.prompt,
                "--cfg-scale", _num(cfg), "--steps", str(steps), "--sampling-method", sampler,
                "-W", str(job.width), "-H", str(job.height), "--seed", str(job.seed)]
        if eng.get("paramsBackend"):
            argv += ["--params-backend", eng["paramsBackend"]]
        if eng.get("maxVram"):
            argv += ["--max-vram", eng["maxVram"]]
        if eng.get("threads"):  # before the model's args, so those can override it
            argv += ["-t", str(eng["threads"])]
        argv += resolved["args"]
        for ref in job.references or []:
            argv += ["-r", str(ref)]
        if job.init_image:
            argv += ["-i", str(job.init_image)]
            if job.strength is not None:
                argv += ["--strength", _num(job.strength)]
            argv += resolved.get("initImageArgs", [])
        argv += ["--preview", "proj", "--preview-interval", "1", "--preview-path", str(self.preview_path(out)),
                 "-o", str(out), "-v"]
        return argv

    @staticmethod
    def effective(job: EngineJob, resolved: dict) -> dict:
        """``steps``, ``cfg`` and ``sampler`` the run uses: the job's, else the model's defaults."""
        defaults = resolved["defaults"]
        return {k: getattr(job, k) if getattr(job, k) is not None else defaults[k] for k in ("steps", "cfg", "sampler")}

    @staticmethod
    def preview_path(output: Path) -> Path:
        return output.with_suffix(".preview.png")

    @staticmethod
    def log_path(output: Path) -> Path:
        return output.with_suffix(".log")

    @staticmethod
    def _command(argv: list) -> list:
        """The argv for the log (D34): `sd-cli` without its folder, model files relative to ``paths.models_dir()``."""
        root = paths.models_dir()
        command = ["sd-cli"] + argv[1:]
        for i, arg in enumerate(command[:-1]):
            if arg in ("--diffusion-model", "--llm", "--vae"):
                with contextlib.suppress(ValueError):
                    command[i + 1] = Path(command[i + 1]).relative_to(root).as_posix()
        return command

    @staticmethod
    def _timeout(resolved: dict, job: EngineJob) -> Optional[float]:
        for value in (resolved["timeoutS"], job.timeout_s):
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                return float(value)
        return None

    # -- guards (D33) -------------------------------------------------------------------------------------------

    def _free_mb(self) -> Optional[int]:
        free = (self.read_meminfo or read_meminfo_mb)()
        return free if isinstance(free, int) and not isinstance(free, bool) and free >= 0 else None

    def _check_memory(self, resolved: dict, notes: list) -> None:
        free = self._free_mb()
        if free is None:
            notes.append("memory check skipped: MemAvailable is not available here")
            return
        self._run.seen(free)
        needed = resolved["minFreeMemoryMb"]
        if needed and free < needed:
            raise GimgError("engine.low_memory", free_mb=free, needed_mb=needed)

    def _check_ollama(self, machine: dict, notes: list) -> None:
        mode = (machine.get("engine") or {}).get("ollama", "abort")
        if mode == "ignore":
            notes.append("ollama check skipped (engine.ollama: ignore)")
            return
        url = ollama_url(machine)
        loaded = ollama_loaded(url, self.ollama_ps_timeout_s)
        if loaded and mode == "unload":
            for name in loaded:
                ollama_unload(url, name, self.ollama_unload_timeout_s)
            deadline = time.monotonic() + self.ollama_wait_s
            while True:
                still = ollama_loaded(url, self.ollama_ps_timeout_s)
                if not still or time.monotonic() >= deadline:
                    break
                time.sleep(self.ollama_wait_poll_s)
            if not still:
                notes.append("ollama: unloaded " + ", ".join(loaded))
            loaded = still
        if loaded:
            raise GimgError("engine.ollama_loaded", models=", ".join(loaded),
                            hint="; ".join("ollama stop " + name for name in loaded))

    @staticmethod
    def _new_log_text(log_path, run: _Run) -> str:
        """The part of the log written since the last call, with the end of the previous one in front (a phrase may
        be cut by the read boundary)."""
        try:
            with open(log_path, "rb") as fh:
                fh.seek(run.log_pos)
                data = fh.read()
        except OSError:
            run.new = ""
            return run.carry
        run.log_pos += len(data)
        run.new = data.decode("utf-8", errors="replace")
        text = run.carry + run.new
        run.carry = text[-(len(ZERO_FREE) - 1):]
        return text

    def _on_tick(self, proc, log_path, job: EngineJob) -> None:
        """Called once per poll while `sd-cli` runs: the memory watch and the "reported free 0.00 MB" abort (F2.3), and the
        progress for the queue (F2.4). A refusal kills the group first and then raises."""
        run = self._run
        free = self._free_mb()
        if free is not None:
            run.seen(free)
            if run.watch_mb and free < run.watch_mb:
                self._kill(proc)
                raise EngineError("memory watch: %d MB free, below the %d MB threshold; sd-cli was killed"
                                  % (free, run.watch_mb), code="engine.watch_memory",
                                  free_mb=free, watch_mb=run.watch_mb)
        text = self._new_log_text(log_path, run)
        self._report_progress(run, job)
        if ZERO_FREE in text:
            self._kill(proc)
            raise EngineError("the GPU driver reported 0.00 MB free; sd-cli was killed", code="engine.driver_no_memory")

    @staticmethod
    def _report_progress(run: _Run, job: EngineJob) -> None:
        """Parse what the last read brought (after the unfinished end of the one before) and tell `job.on_progress`."""
        text = run.bar_carry + run.new
        cut = max(text.rfind(c) for c in "\x1b\r\n")
        run.bar_carry = text[cut + 1:][-BAR_CARRY_MAX:]
        progress, run.sampled = parse_progress(text, run.steps, run.sampled)
        if progress is None or job.on_progress is None:
            return
        key = (progress["step"], progress["steps"])
        if key != run.last:
            run.last = key
            with contextlib.suppress(Exception):  # progress is a courtesy: it never fails the generation
                job.on_progress(progress)

    def _kill(self, proc: subprocess.Popen) -> None:
        """Stop `proc` and its group and wait for it to die (see the module docstring for the Windows fallback)."""
        if _POSIX:
            with contextlib.suppress(OSError):
                os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=self.kill_grace_s)
            except subprocess.TimeoutExpired:
                pass
            with contextlib.suppress(OSError):  # also what is left of the group after the leader is gone
                os.killpg(proc.pid, signal.SIGKILL)
        else:
            with contextlib.suppress(OSError):
                proc.terminate()
            try:
                proc.wait(timeout=self.kill_grace_s)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(OSError):
                    proc.kill()
        try:
            proc.wait(timeout=max(self.kill_grace_s, 1.0))
        except subprocess.TimeoutExpired:
            pass

    # -- generate -----------------------------------------------------------------------------------------------

    def generate(self, job: EngineJob, should_cancel: Callable[[], bool]) -> EngineResult:
        machine = job.machine or self.machine
        resolved = self._resolve(job, machine)
        binary = binary_path(machine)
        if not binary.is_file():
            raise GimgError("engine.binary_missing", path=str(binary))
        if not os.access(binary, os.X_OK):
            raise GimgError("engine.binary_not_executable", path=str(binary))
        argv = self.build_argv(job, resolved, machine, binary)
        self._run = _Run(watch_mb=machine.get("watchMemoryMb"), steps=self.effective(job, resolved)["steps"])
        notes = []
        self._check_memory(resolved, notes)  # a refusal leaves no log, no image and no process
        self._check_ollama(machine, notes)
        out = Path(job.output)
        log_path = self.log_path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(OSError):
            out.unlink()  # a stale image must not pass for the new one
        env = dict(os.environ)
        env["LD_LIBRARY_PATH"] = str(binary.parent)
        popen_kw = {"start_new_session": True} if _POSIX else {
            "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
        limit_s = self._timeout(resolved, job)
        start = time.monotonic()
        with open(log_path, "wb") as log_fh:
            header = "".join("[gimg] %s\n" % note for note in notes).encode("utf-8")
            log_fh.write(header)
            log_fh.flush()
            self._run.log_pos = len(header)
            try:
                proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log_fh, stderr=subprocess.STDOUT,
                                        env=env, **popen_kw)
            except OSError as exc:
                raise GimgError("engine.binary_not_executable", path="%s (%s)" % (binary, exc))
            try:
                while True:
                    try:
                        proc.wait(timeout=self.poll_s)
                        break
                    except subprocess.TimeoutExpired:
                        pass
                    if should_cancel():
                        self._kill(proc)
                        raise Cancelled()
                    if limit_s is not None and time.monotonic() - start >= limit_s:
                        self._kill(proc)
                        raise EngineTimeout()
                    self._on_tick(proc, log_path, job)
            finally:
                if proc.poll() is None:  # an exception of our own (or Ctrl-C) must not leave the group running
                    self._kill(proc)
        total = int((time.monotonic() - start) * 1000)
        text = _read_log(log_path)
        if proc.returncode != 0:
            tail = "\n".join(_clean_lines(text)[-TAIL_LINES:])
            raise EngineError("sd-cli exited with code %d%s" % (proc.returncode, (":\n" + tail) if tail else ""))
        if not self._is_png(out):
            tail = "\n".join(_clean_lines(text)[-TAIL_LINES:])
            raise EngineError("sd-cli finished without writing the image" + ((":\n" + tail) if tail else ""))
        with contextlib.suppress(OSError):
            self.preview_path(out).unlink()
        return EngineResult(duration_ms=total, engine_version=RELEASE, command=self._command(argv),
                            log_path=str(log_path), min_free_mb=self._run.min_free_mb,
                            model_files={k: Path(resolved["files"][k]["path"]).name for k in ("diffusion", "text", "vae")},
                            backend=_backend(argv), threads=_threads(argv), params=self.effective(job, resolved),
                            **parse_timings(text))

    @staticmethod
    def _is_png(path: Path) -> bool:
        try:
            with open(path, "rb") as fh:
                return fh.read(8) == _PNG
        except OSError:
            return False
