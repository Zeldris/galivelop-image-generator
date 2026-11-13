__version__ = "0.5.0"


def build_id() -> str:
    """A fingerprint of the code: relative path and content of every ``.py`` and ``.json`` of the package (the UI is
    left out: the server reads it from disk on each request). Within one version it changes whenever the code does,
    so a service started from older code is told apart and replaced (``service.ensure_running``); two checkouts with
    the same code give the same fingerprint, so they do not replace each other's service."""
    import hashlib
    from pathlib import Path

    root = Path(__file__).resolve().parent
    digest = hashlib.sha1()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel.parts[0] == "ui" or "__pycache__" in rel.parts or path.suffix not in (".py", ".json"):
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        digest.update(("%s\0%d\0" % (rel.as_posix(), len(data))).encode("utf-8"))
        digest.update(data)
    return digest.hexdigest()[:12]
