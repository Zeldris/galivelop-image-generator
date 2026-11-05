#!/usr/bin/env python3
"""Etiquetas y releases de GitHub de `gimg` (pedido de la persona del 2026-11-05, `docs/plan.md`).

    python3 releases.py notes 0.4.0      # notas de la release: la sección de los dos CHANGELOG (es y en)
    python3 releases.py check [--ref origin/main]
                                         # ¿la versión de gimg en esa rama tiene etiqueta vX.Y.Z y release?

`check` sale con 0 si las dos existen, 1 si falta alguna (y dice la orden que la crea) y 2 si no lo puede saber
(sin `git` o `gh`, sin red). Se corre al cerrar cada fase, con la rama ya en `main`.
"""
import re
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parent
_VERSION = re.compile(r'^__version__\s*=\s*"([^"]+)"', re.M)
_HEADINGS = {"es": ("CHANGELOG.es.md", "Español"), "en": ("CHANGELOG.md", "English")}


def section(text, version):
    """El cuerpo de la sección `## [version]` de un CHANGELOG, sin el título; None si no está."""
    lines, out, inside = text.splitlines(), [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line.startswith(f"## [{version}]")
            continue
        if inside:
            out.append(line)
    body = "\n".join(out).strip()
    return body or None


def notes(version, root=R):
    """Las notas de la release en es y en; ValueError si a algún CHANGELOG le falta la sección."""
    parts = []
    for lang, (name, title) in _HEADINGS.items():
        body = section((root / name).read_text(encoding="utf-8"), version)
        if body is None:
            raise ValueError(f"{name} no tiene la sección ## [{version}]")
        parts.append(f"## {title}\n\n" + re.sub(r"^### ", "#### ", body, flags=re.M))
    return "\n\n".join(parts) + "\n"


def version_at(ref, run=subprocess.run):
    """La `__version__` de `gimg/__init__.py` en `ref`."""
    done = run(["git", "show", f"{ref}:gimg/__init__.py"], cwd=R, capture_output=True, text=True, check=True)
    found = _VERSION.search(done.stdout)
    if not found:
        raise ValueError(f"gimg/__init__.py de {ref} no tiene __version__")
    return found.group(1)


def check(ref, run=subprocess.run):
    """(código de salida, mensaje) de si la versión de `ref` tiene etiqueta y release."""
    try:
        version = version_at(ref, run)
        tag = f"v{version}"
        tags = run(["git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}"], cwd=R, capture_output=True,
                   text=True, check=True).stdout
        release = run(["gh", "release", "view", tag, "--json", "tagName"], cwd=R, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        return 2, f"releases: no se puede comprobar ({exc})"
    missing = []
    if not tags.strip():
        missing.append(f"la etiqueta: git tag -a {tag} <commit> -m 'gimg {version}' && git push origin {tag}")
    if release.returncode != 0:
        if "not found" not in (release.stderr or "").lower():
            return 2, f"releases: gh no responde ({(release.stderr or '').strip()})"
        missing.append(f"la release: python3 releases.py notes {version} > notas.md && "
                       f"gh release create {tag} --verify-tag --title '{version}' --notes-file notas.md")
    if missing:
        return 1, f"releases: a gimg {version} ({ref}) le falta " + "; y ".join(missing)
    return 0, f"releases: gimg {version} ({ref}) tiene etiqueta y release"


def main(argv):
    if len(argv) == 2 and argv[0] == "notes":
        try:
            sys.stdout.write(notes(argv[1]))
        except ValueError as exc:
            print(f"releases: {exc}", file=sys.stderr)
            return 1
        return 0
    if argv[:1] == ["check"] and argv[1:] in ([], ["--ref", argv[-1]]):
        code, message = check(argv[2] if len(argv) == 3 else "origin/main")
        print(message, file=sys.stderr if code else sys.stdout)
        return code
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
