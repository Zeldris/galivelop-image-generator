"""Atomic JSON files and per-file locks."""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import tempfile
import threading
from pathlib import Path

_MISSING = object()
_umask_lock = threading.Lock()


def honour_umask(fd: int) -> None:
    """`mkstemp` files are 0600; give the final file the mode a plain open() would (0666 & ~umask)."""
    with _umask_lock:
        mask = os.umask(0)
        os.umask(mask)
    os.fchmod(fd, 0o666 & ~mask)


def write_json(path, data) -> None:
    """Write JSON (indent 2, sorted keys, trailing newline) via temp file + os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".", suffix=".tmp")
    try:
        honour_umask(fd)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def read_json(path, default=_MISSING):
    """Read JSON; if the file is missing return `default` (or raise FileNotFoundError)."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        if default is _MISSING:
            raise
        return default


@contextlib.contextmanager
def lock(path):
    """Exclusive flock on `<path>.lock` for a read-modify-write of `path`."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)  # closing releases the lock
