"""Image engines. F1 has only the fake one; the real `sd-cli` wrapper arrives in F2.

Environment: ``GIMG_ENGINE`` picks the engine (default ``fake``). The fake engine reads
``GIMG_FAKE_DELAY`` (seconds to wait) and ``GIMG_FAKE_FAIL`` (fail with that message)."""
from __future__ import annotations

import math
import os
import struct
import tempfile
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import fsutil
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
    machine: dict = field(default_factory=dict)
    timeout_s: Optional[float] = None


@dataclass
class EngineResult:
    duration_ms: int
    engine_version: str
    load_ms: Optional[int] = None
    sample_ms: Optional[int] = None
    decode_ms: Optional[int] = None
    min_free_mb: Optional[int] = None


class EngineError(Exception):
    """The engine failed; `message` is for the log and the queue entry."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


TIMEOUT_MESSAGE = "timeout"


class EngineTimeout(EngineError):
    """The job ran past `job.timeout_s`; the message is always `TIMEOUT_MESSAGE`."""

    def __init__(self):
        super().__init__(TIMEOUT_MESSAGE)


class Cancelled(Exception):
    """`should_cancel()` returned true while generating."""


class Engine:
    provider = ""

    def generate(self, job: EngineJob, should_cancel: Callable[[], bool]) -> EngineResult:
        raise NotImplementedError


def _chunk(kind: bytes, data: bytes) -> bytes:
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def png_bytes(width: int, height: int, color: tuple) -> bytes:
    """A valid 8-bit RGB PNG of one solid color."""
    row = b"\x00" + bytes(color) * width
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(row * height))
            + _chunk(b"IEND", b""))


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


def get_engine() -> Engine:
    """The engine named by ``GIMG_ENGINE`` (default ``fake``)."""
    name = os.environ.get("GIMG_ENGINE") or "fake"
    if name != "fake":
        raise GimgError("engine.unknown", engine=name)
    try:
        delay = float(os.environ.get("GIMG_FAKE_DELAY") or 0)
    except ValueError:
        raise GimgError("engine.bad_delay", value=os.environ["GIMG_FAKE_DELAY"])
    if not math.isfinite(delay) or delay < 0:
        raise GimgError("engine.bad_delay", value=os.environ["GIMG_FAKE_DELAY"])
    return FakeEngine(delay_s=delay, fail_with=os.environ.get("GIMG_FAKE_FAIL") or None)
