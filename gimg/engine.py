"""Image engines: the fake one here, the real `sd-cli` wrapper in `engine_sdcpp`.

Engine choice (D36): ``GIMG_ENGINE``, else ``"engine"`` of ``<config>/config.json``, else ``fake``; the values are ``fake`` and
``sdcpp``. The fake engine reads ``GIMG_FAKE_DELAY`` (seconds to wait) and ``GIMG_FAKE_FAIL`` (fail with that message)."""
from __future__ import annotations

import math
import os
import tempfile
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import fsutil, paths
from .png import png_bytes  # noqa: F401  (re-exported: the fake engine and the tests use it from here)
from .errors import GimgError

FAKE_VERSION = "fake-1"
_TICK_S = 0.02


@dataclass
class EngineJob:
    prompt: str
    width: int
    height: int
    seed: int
    output: str  # absolute path
    steps: Optional[int] = None
    cfg: Optional[float] = None
    sampler: Optional[str] = None
    model: Optional[str] = None
    references: list = field(default_factory=list)  # absolute paths
    init_image: Optional[str] = None  # absolute path (img2img)
    strength: Optional[float] = None
    machine: dict = field(default_factory=dict)
    timeout_s: Optional[float] = None
    on_progress: Optional[Callable[[dict], None]] = None  # called with ``{"step", "steps", "etaS"}`` when the step changes (F2.4)


@dataclass
class EngineResult:
    duration_ms: int
    engine_version: str
    load_ms: Optional[int] = None
    sample_ms: Optional[int] = None
    decode_ms: Optional[int] = None
    min_free_mb: Optional[int] = None
    command: Optional[list] = None  # argv of the engine for the log (D34); model files relative to the models folder
    log_path: Optional[str] = None  # the engine's log of this run; the worker keeps it as ``attempts/q<entry>.log``
    model_files: Optional[dict] = None  # file names (no folder) by kind: ``{"diffusion", "text", "vae"}`` (D34)
    backend: Optional[str] = None  # ``cpu`` or ``vulkan`` (D34)
    threads: Optional[int] = None  # the ``-t`` of the command, if there is one
    compose: Optional[str] = None  # the composition template, F2.8
    params: Optional[dict] = None  # steps, cfg and sampler actually used (the job's, else the model's defaults)


class EngineError(Exception):
    """The engine failed; `message` is for the log and the queue entry. With a `code` (and its `params`) the worker
    stores that code, so the front end shows the translated ``error.<code>`` text instead of ``engine.failed``."""

    def __init__(self, message: str, code: Optional[str] = None, **params):
        super().__init__(message)
        self.message = message
        self.code = code
        self.params = params


TIMEOUT_MESSAGE = "timeout"


class EngineTimeout(EngineError):
    """The job ran past `job.timeout_s`; the message is always `TIMEOUT_MESSAGE`."""

    def __init__(self):
        super().__init__(TIMEOUT_MESSAGE)


class Cancelled(Exception):
    """`should_cancel()` returned true while generating."""


class Engine:
    provider = ""

    @staticmethod
    def preview_path(output: Path) -> Optional[Path]:
        """Where this engine writes the preview of the image that will be `output`; ``None`` if it makes none."""
        return None

    def generate(self, job: EngineJob, should_cancel: Callable[[], bool]) -> EngineResult:
        raise NotImplementedError


def seed_color(seed: int) -> tuple:
    """Deterministic RGB from a seed."""
    value = zlib.crc32(str(seed).encode()) & 0xFFFFFF
    return (value >> 16, (value >> 8) & 0xFF, value & 0xFF)


class FakeEngine(Engine):
    provider = "fake"

    def __init__(self, delay_s: float = 0, fail_with: Optional[str] = None):
        self.delay_s = delay_s
        self.fail_with = fail_with

    def generate(self, job: EngineJob, should_cancel: Callable[[], bool]) -> EngineResult:
        start = time.monotonic()
        end = start + self.delay_s
        limit = None if job.timeout_s is None else start + job.timeout_s
        while True:
            if should_cancel():
                raise Cancelled()
            now = time.monotonic()
            if limit is not None and now >= limit and end > limit:
                raise EngineTimeout()
            left = end - now
            if left <= 0:
                break
            if limit is not None and end > limit:
                left = min(left, limit - now)
            time.sleep(min(_TICK_S, left))
        if self.fail_with:
            raise EngineError(self.fail_with)
        if not (isinstance(job.width, int) and isinstance(job.height, int)
                and job.width > 0 and job.height > 0):
            raise EngineError("invalid size %sx%s" % (job.width, job.height))
        out = Path(job.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.monotonic()
        data = png_bytes(job.width, job.height, seed_color(job.seed))
        fd, tmp = tempfile.mkstemp(dir=str(out.parent), prefix="." + out.name + ".", suffix=".tmp")
        try:
            fsutil.honour_umask(fd)
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, out)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        decode_ms = int((time.monotonic() - t0) * 1000)
        total = int((time.monotonic() - start) * 1000)
        return EngineResult(duration_ms=total, engine_version=FAKE_VERSION,
                            load_ms=0, sample_ms=max(total - decode_ms, 0), decode_ms=decode_ms)


def _configured_engine() -> str:
    """``GIMG_ENGINE``, else ``"engine"`` of ``<config>/config.json``, else ``fake``."""
    name = os.environ.get("GIMG_ENGINE")
    if name:
        return name
    config_file = paths.config_dir() / "config.json"
    try:
        config = fsutil.read_json(config_file, {})
    except (OSError, ValueError) as exc:
        raise GimgError("machine.config_unreadable", path=str(config_file), reason=str(exc))
    value = config.get("engine") if isinstance(config, dict) else None
    return value if isinstance(value, str) and value else "fake"


def get_engine() -> Engine:
    """The engine named by ``GIMG_ENGINE`` or the config file (default ``fake``); see the module docstring."""
    name = _configured_engine()
    if name == "sdcpp":
        from . import engine_sdcpp, limits, models  # engine_sdcpp imports this module
        return engine_sdcpp.SdCppEngine(limits.load_machine(), models.load_catalog())
    if name != "fake":
        raise GimgError("engine.unknown", engine=name)
    try:
        delay = float(os.environ.get("GIMG_FAKE_DELAY") or 0)
    except ValueError:
        raise GimgError("engine.bad_delay", value=os.environ["GIMG_FAKE_DELAY"])
    if not math.isfinite(delay) or delay < 0:
        raise GimgError("engine.bad_delay", value=os.environ["GIMG_FAKE_DELAY"])
    return FakeEngine(delay_s=delay, fail_with=os.environ.get("GIMG_FAKE_FAIL") or None)
