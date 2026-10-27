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
- **Tick hook:** `_on_tick(proc, log_path, job)` runs once per poll; F2.3 (memory watch, "reported free 0.00 MB") and F2.4
  (progress in the queue) hook in there. Not implemented here: memory guards, Ollama, ``draft``, ``initImage``, ``strength``.

Timings come from the log: ``load_ms`` is the sum of the ``loading tensors completed, taking Xs`` lines, ``sample_ms`` is
the last ``sampling completed, taking Xs`` and ``decode_ms`` the last ``decode_first_stage completed, taking Xs``; a line
that is not there leaves its field ``None``.
"""
from __future__ import annotations

import contextlib
import os
import re
import signal
import subprocess
import time
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
_LOAD = re.compile(r"loading tensors completed, taking ([0-9.]+)s")
_SAMPLE = re.compile(r"sampling completed, taking ([0-9.]+)s")
_DECODE = re.compile(r"decode_first_stage completed, taking ([0-9.]+)s")
_POSIX = hasattr(os, "killpg")


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


def _read_log(path) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


class SdCppEngine(Engine):
    provider = PROVIDER

    def __init__(self, machine: Optional[dict] = None, catalog: Optional[dict] = None,
                 poll_s: float = POLL_S, kill_grace_s: float = KILL_GRACE_S):
        self.machine = machine or {}
        self.catalog = catalog
        self.poll_s = poll_s
        self.kill_grace_s = kill_grace_s

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
        defaults, files = resolved["defaults"], resolved["files"]
        steps = job.steps if job.steps is not None else defaults["steps"]
        cfg = job.cfg if job.cfg is not None else defaults["cfg"]
        sampler = job.sampler if job.sampler is not None else defaults["sampler"]
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
        argv += ["--preview", "proj", "--preview-interval", "1", "--preview-path", str(self.preview_path(out)),
                 "-o", str(out), "-v"]
        return argv

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

    def _on_tick(self, proc, log_path, job: EngineJob) -> None:
        """Called once per poll while `sd-cli` runs. F2.3 (memory watch) and F2.4 (progress) hook in here."""

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
                            log_path=str(log_path), **parse_timings(text))

    @staticmethod
    def _is_png(path: Path) -> bool:
        try:
            with open(path, "rb") as fh:
                return fh.read(8) == _PNG
        except OSError:
            return False
