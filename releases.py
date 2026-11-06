#!/usr/bin/env python3
"""Versiones, etiquetas y releases de GitHub de `gimg` (pedido de la persona del 2026-11-05, `docs/plan.md`).

    python3 releases.py suggest          # versión que piden los commits desde la última etiqueta vX.Y.Z (solo sugiere)
    python3 releases.py bump 0.5.0 [--date 2026-11-05]
                                         # sube __version__ y pasa [Unreleased]/[Sin publicar] de los dos CHANGELOG
                                         # a una sección ## [0.5.0] - fecha (por defecto hoy), y pone la
                                         # versión en la línea «Versión **X**» de README.md y README.en.md
    python3 releases.py notes 0.4.0      # notas de la release: la sección de los dos CHANGELOG (es y en)
    python3 releases.py verify-tag v0.4.0 [--ref HEAD]
                                         # ¿la etiqueta es igual a __version__ en ese commit? (lo llama release.yml)
    python3 releases.py check [--ref origin/main]
                                         # ¿la versión de gimg en esa rama tiene etiqueta vX.Y.Z y release?

`suggest`: `tipo!:` o `BREAKING CHANGE` suben la menor mientras la versión sea 0.x (la mayor desde 1.0); `feat`, la
menor; `fix` y `perf`, el parche; sin nada de eso, ninguna. `bump` sale con 1 y dice el motivo si la versión no es
semver, no es mayor que la actual o si algún CHANGELOG no tiene nada sin publicar. `verify-tag` sale con 0 o 1.
`check` sale con 0 si las dos existen, 1 si falta alguna (y dice la orden que la crea) y 2 si no lo puede saber
(sin `git` o `gh`, sin red). Se corre al cerrar cada fase, con la rama ya en `main`. Antes de leer la versión trae
`ref` del remoto si es una rama de `origin/` (un `origin/main` viejo daría por buena la versión anterior).
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parent
_VERSION = re.compile(r'^__version__\s*=\s*"([^"]+)"', re.M)
_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_UNRELEASED = re.compile(r"^## \[(Unreleased|Sin publicar)\]\s*$")
_REPO = "https://github.com/Zeldris/galivelop-image-generator"
_HEADINGS = {"es": ("CHANGELOG.es.md", "Español"), "en": ("CHANGELOG.md", "English")}
_README = {"README.md": re.compile(r"^(Versión \*\*)([^*]+)(\*\*)", re.M),
           "README.en.md": re.compile(r"^(Version \*\*)([^*]+)(\*\*)", re.M)}


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
    """Las notas de la release (es, luego en, con enlaces a los CHANGELOG); ValueError si falta alguna sección."""
    bodies = {}
    for lang, (name, title) in _HEADINGS.items():
        body = section((root / name).read_text(encoding="utf-8"), version)
        if body is None:
            raise ValueError(f"{name} no tiene la sección ## [{version}]")
        bodies[lang] = f"## {title}\n\n" + re.sub(r"^### ", "#### ", body, flags=re.M)
    base = f"{_REPO}/blob/v{version}"
    return ("**ES** · [English below](#en)\n\n" + bodies["es"] + '\n\n<a id="en"></a>\n\n' + bodies["en"]
            + f"\n\nFull entry / Entrada completa: [CHANGELOG.md]({base}/CHANGELOG.md) · "
              f"[CHANGELOG.es.md]({base}/CHANGELOG.es.md)\n")


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
        if ref.startswith("origin/"):
            run(["git", "fetch", "--quiet", "origin", ref.removeprefix("origin/")], cwd=R, capture_output=True,
                text=True, check=True)
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
        if (release.stderr or "").strip().lower() != "release not found":
            return 2, f"releases: gh no responde ({(release.stderr or '').strip()})"
        missing.append(f"la release: python3 releases.py notes {version} | "
                       f"gh release create {tag} --verify-tag --title '{version}' --notes-file -")
    if missing:
        return 1, f"releases: a gimg {version} ({ref}) le falta " + "; y ".join(missing)
    return 0, f"releases: gimg {version} ({ref}) tiene etiqueta y release"


def readme_versions(root=R):
    """{README: versión que dice su línea «Versión **X**»} (None si no la tiene)."""
    out = {}
    for name, pattern in _README.items():
        found = pattern.search((root / name).read_text(encoding="utf-8"))
        out[name] = found.group(2) if found else None
    return out


def _parse(version):
    found = _SEMVER.match(version)
    return tuple(int(n) for n in found.groups()) if found else None


def verify_tag(tag, ref="HEAD", run=subprocess.run):
    """(código de salida, mensaje) de si la etiqueta `vX.Y.Z` es igual a la `__version__` de `ref`."""
    if not re.match(r"^v\d+\.\d+\.\d+$", tag):
        return 1, f"releases: la etiqueta {tag} no tiene la forma vX.Y.Z"
    try:
        version = version_at(ref, run)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        return 1, f"releases: no se puede leer la versión de {ref} ({exc})"
    if tag != f"v{version}":
        return 1, f"releases: la etiqueta {tag} no coincide con __version__ = {version} en {ref}"
    return 0, f"releases: la etiqueta {tag} coincide con __version__ en {ref}"


def bump(version, date=None, root=R):
    """Sube `__version__` y pasa lo sin publicar de cada CHANGELOG a `## [version] - date`; ValueError si no procede.

    También reescribe la línea «Versión **X**» / «Version **X**» de los dos README. Valida todo antes de escribir
    nada: o se cambian los cinco archivos o ninguno."""
    new = _parse(version)
    if new is None:
        raise ValueError(f"{version} no es una versión semver X.Y.Z")
    date = date or datetime.date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise ValueError(f"la fecha {date} no tiene la forma AAAA-MM-DD")
    init = root / "gimg" / "__init__.py"
    text = init.read_text(encoding="utf-8")
    found = _VERSION.search(text)
    if not found:
        raise ValueError("gimg/__init__.py no tiene __version__")
    if _parse(found.group(1)) is None or new <= _parse(found.group(1)):
        raise ValueError(f"{version} no es mayor que la versión actual {found.group(1)}")
    writes = [(init, text[:found.start(1)] + version + text[found.end(1):])]
    for name, _ in _HEADINGS.values():
        lines = (root / name).read_text(encoding="utf-8").split("\n")
        start = next((i for i, line in enumerate(lines) if _UNRELEASED.match(line)), None)
        if start is None:
            raise ValueError(f"{name} no tiene la sección ## [Unreleased] / ## [Sin publicar]")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        if not "\n".join(lines[start + 1:end]).strip():
            raise ValueError(f"{name} no tiene nada sin publicar")
        body = lines[start + 1:end]
        while body and not body[-1].strip():
            body.pop()
        out = lines[:start + 1] + ["", f"## [{version}] - {date}"] + body + ([""] if end < len(lines) else [])
        writes.append((root / name, "\n".join(out + lines[end:])))
    for name, pattern in _README.items():
        readme = (root / name).read_text(encoding="utf-8")
        found = pattern.search(readme)
        if not found:
            raise ValueError(f"{name} no tiene la línea de versión (Versión **X** / Version **X**)")
        writes.append((root / name, readme[:found.start(2)] + version + readme[found.end(2):]))
    for path, content in writes:
        path.write_text(content, encoding="utf-8")


def suggest(run=subprocess.run):
    """(código de salida, mensaje) con la versión que piden los commits desde la última etiqueta vX.Y.Z."""
    try:
        tag = run(["git", "describe", "--tags", "--abbrev=0", "--match", "v*"], cwd=R, capture_output=True,
                  text=True, check=True).stdout.strip()
        log = run(["git", "log", "--format=%s%n%b%x00", f"{tag}..HEAD"], cwd=R, capture_output=True, text=True,
                  check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        return 2, f"releases: no se puede leer el historial ({exc})"
    current = _parse(tag.removeprefix("v"))
    if current is None:
        return 2, f"releases: la etiqueta {tag} no es vX.Y.Z"
    levels = {"major": [], "minor": [], "patch": []}
    for commit in log.split("\x00"):
        subject = commit.strip().split("\n", 1)[0]
        head = re.match(r"^(\w+)(?:\([^)]*\))?(!)?:", subject)
        if not subject:
            continue
        breaking = bool(head and head.group(2)) or re.search(r"^BREAKING[ -]CHANGE", commit, re.M)
        if breaking:
            levels["major" if current[0] >= 1 else "minor"].append(f"{subject} (rompe)")
        elif head and head.group(1) == "feat":
            levels["minor"].append(subject)
        elif head and head.group(1) in ("fix", "perf"):
            levels["patch"].append(subject)
    for level in ("major", "minor", "patch"):
        if levels[level]:
            a, b, c = current
            new = {"major": (a + 1, 0, 0), "minor": (a, b + 1, 0), "patch": (a, b, c + 1)}[level]
            why = "\n".join(f"  - {s}" for s in levels[level])
            return 0, f"{'.'.join(map(str, new))} ({level}, desde {tag}):\n{why}"
    return 0, f"ninguna: ningún commit desde {tag} pide versión (solo feat, fix, perf o cambios que rompen)"


def main(argv):
    if len(argv) == 2 and argv[0] == "notes":
        try:
            sys.stdout.write(notes(argv[1]))
        except ValueError as exc:
            print(f"releases: {exc}", file=sys.stderr)
            return 1
        return 0
    if argv[:1] == ["check"] and (len(argv) == 1 or len(argv) == 3 and argv[1] == "--ref"
                                  and not argv[2].startswith("-")):
        code, message = check(argv[2] if len(argv) == 3 else "origin/main")
        print(message, file=sys.stderr if code else sys.stdout)
        return code
    if argv[:1] == ["suggest"] and len(argv) == 1:
        code, message = suggest()
        print(message, file=sys.stderr if code else sys.stdout)
        return code
    if argv[:1] == ["bump"] and (len(argv) == 2 or len(argv) == 4 and argv[2] == "--date") \
            and not argv[1].startswith("-"):
        try:
            bump(argv[1], argv[3] if len(argv) == 4 else None)
        except ValueError as exc:
            print(f"releases: {exc}", file=sys.stderr)
            return 1
        print(f"releases: versión {argv[1]}; revisa git diff y ajusta los CHANGELOG si hace falta")
        return 0
    if argv[:1] == ["verify-tag"] and (len(argv) == 2 or len(argv) == 4 and argv[2] == "--ref") \
            and not argv[1].startswith("-"):
        code, message = verify_tag(argv[1], argv[3] if len(argv) == 4 else "HEAD")
        print(message, file=sys.stderr if code else sys.stdout)
        return code
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
