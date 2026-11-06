__version__ = "0.4.1"


def build_id() -> str:
    """A fingerprint of the code of this checkout: path, size and mtime of every ``.py`` and ``.json`` of the package
    (the UI is left out: the server reads it from disk on each request). Within one version it changes whenever the
    code does, so a service started from older code is told apart and replaced (``service.ensure_running``)."""
    import hashlib
    from pathlib import Path

    root = Path(__file__).resolve().parent
    digest = hashlib.sha1()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel.parts[0] == "ui" or "__pycache__" in rel.parts or path.suffix not in (".py", ".json"):
            continue
        try:
            info = path.stat()
        except OSError:
            continue
        digest.update(("%s\0%d\0%d\n" % (rel.as_posix(), info.st_size, info.st_mtime_ns)).encode("utf-8"))
    return digest.hexdigest()[:12]
