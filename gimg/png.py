"""PNG text chunks and the bytes of a plain PNG, stdlib only (F2.4, `docs/interfaz/propuesta.md`, decision nueva 2).

`add_text_chunk(path, key, text)` writes a metadata chunk just before ``IEND`` and replaces the file atomically
(temporary file in the same folder + ``os.replace``, like `fsutil`); an earlier text chunk with the same key is
replaced, not duplicated, so calling it twice is the same as once. `read_text_chunks(path)` returns ``{key: text}``
for every ``tEXt``, ``zTXt`` and ``iTXt`` chunk (a repeated key keeps the last one).

``tEXt`` is Latin-1 and cannot hold a NUL, so a text that fits is written as ``tEXt`` (what other tools read) and any
other (a prompt with an emoji or a CJK character) as an uncompressed ``iTXt`` in UTF-8, with the same key. A key is
1-79 Latin-1 characters without NUL, newline or leading/trailing space (PNG spec).

A file that is not a PNG, is cut, or has a chunk with a bad CRC raises ``GimgError("png.invalid", path, reason)``; the
file is never touched in that case.
"""
from __future__ import annotations

import contextlib
import os
import struct
import tempfile
import zlib
from pathlib import Path

from . import fsutil
from .errors import GimgError

SIGNATURE = b"\x89PNG\r\n\x1a\n"
_TEXT_KINDS = (b"tEXt", b"zTXt", b"iTXt")
_MAX_TEXT = 1 << 24  # a decompressed text bigger than this is refused (zip bombs)


def chunk(kind: bytes, data: bytes) -> bytes:
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def png_bytes(width: int, height: int, color: tuple) -> bytes:
    """A valid 8-bit RGB PNG of one solid color."""
    row = b"\x00" + bytes(color) * width
    return (SIGNATURE
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * height))
            + chunk(b"IEND", b""))


def _invalid(path, reason: str) -> GimgError:
    return GimgError("png.invalid", path=str(path), reason=reason)


def _chunks(data: bytes, path) -> list:
    """``[(kind, body)]`` of a PNG, checking the signature, the lengths, every CRC and the final ``IEND``."""
    if data[:8] != SIGNATURE:
        raise _invalid(path, "not a PNG (bad signature)")
    out, pos = [], 8
    while pos < len(data):
        if pos + 8 > len(data):
            raise _invalid(path, "truncated chunk header")
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 8 + length
        if end + 4 > len(data):
            raise _invalid(path, "truncated chunk %s" % kind.decode("latin-1"))
        body = data[pos + 8:end]
        if struct.unpack(">I", data[end:end + 4])[0] != zlib.crc32(kind + body) & 0xFFFFFFFF:
            raise _invalid(path, "bad CRC in chunk %s" % kind.decode("latin-1"))
        out.append((kind, body))
        pos = end + 4
        if kind == b"IEND":
            break
    if not out or out[0][0] != b"IHDR":
        raise _invalid(path, "the first chunk is not IHDR")
    if out[-1][0] != b"IEND":
        raise _invalid(path, "no IEND chunk (file cut)")
    return out


def _read(path) -> bytes:
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError as exc:
        raise _invalid(path, "cannot read the file: %s" % exc.strerror)


def _inflate(data: bytes, path) -> bytes:
    try:
        raw = zlib.decompressobj().decompress(data, _MAX_TEXT + 1)
    except zlib.error as exc:
        raise _invalid(path, "bad compressed text: %s" % exc)
    if len(raw) > _MAX_TEXT:
        raise _invalid(path, "compressed text is too big")
    return raw


def _decode(kind: bytes, body: bytes, path):
    """``(key, text)`` of one text chunk."""
    key, sep, rest = body.partition(b"\x00")
    if not sep:
        raise _invalid(path, "bad %s chunk (no key separator)" % kind.decode("latin-1"))
    name = key.decode("latin-1")
    if kind == b"tEXt":
        return name, rest.decode("latin-1")
    if kind == b"zTXt":
        if rest[:1] != b"\x00":
            raise _invalid(path, "bad zTXt chunk (unknown compression method)")
        return name, _inflate(rest[1:], path).decode("latin-1")
    if len(rest) < 2:
        raise _invalid(path, "bad iTXt chunk (cut)")
    flag, method, rest = rest[0], rest[1], rest[2:]
    _lang, sep1, rest = rest.partition(b"\x00")
    _translated, sep2, text = rest.partition(b"\x00")
    if not (sep1 and sep2):
        raise _invalid(path, "bad iTXt chunk (cut)")
    if flag:
        if method != 0:
            raise _invalid(path, "bad iTXt chunk (unknown compression method)")
        text = _inflate(text, path)
    return name, text.decode("utf-8", errors="replace")


def read_text_chunks(path) -> dict:
    """``{key: text}`` of the text chunks of the PNG at `path` (empty if it has none)."""
    found = {}
    for kind, body in _chunks(_read(path), path):
        if kind in _TEXT_KINDS:
            key, text = _decode(kind, body, path)
            found[key] = text
    return found


def _check_key(key: str) -> bytes:
    try:
        raw = key.encode("latin-1")
    except UnicodeEncodeError:
        raw = b""
    if not 1 <= len(raw) <= 79 or b"\x00" in raw or b"\n" in raw or raw != raw.strip(b" "):
        raise GimgError("png.bad_key", key=key)
    return raw


def text_chunk(key: str, text: str) -> bytes:
    """The ``tEXt`` chunk for `key` and `text`, or an uncompressed UTF-8 ``iTXt`` when `text` is not Latin-1 or has a NUL."""
    raw_key = _check_key(key)
    with contextlib.suppress(UnicodeEncodeError):
        latin = text.encode("latin-1")
        if b"\x00" not in latin:
            return chunk(b"tEXt", raw_key + b"\x00" + latin)
    return chunk(b"iTXt", raw_key + b"\x00\x00\x00\x00\x00" + text.encode("utf-8"))


def add_text_chunk(path, key: str, text: str) -> None:
    """Put `text` under `key` in the PNG at `path` (see the module docstring); atomic."""
    path = Path(path)
    new = text_chunk(key, text)
    chunks = _chunks(_read(path), path)
    raw_key = key.encode("latin-1")
    body = b""
    for kind, data in chunks[:-1]:
        if kind in _TEXT_KINDS and data.partition(b"\x00")[0] == raw_key:
            continue  # the old value of this key
        body += chunk(kind, data)
    result = SIGNATURE + body + new + chunk(b"IEND", chunks[-1][1])
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".", suffix=".tmp")
    try:
        fsutil.honour_umask(fd)
        with os.fdopen(fd, "wb") as fh:
            fh.write(result)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise
