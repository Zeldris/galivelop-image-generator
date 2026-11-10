"""The brand workshop of a project (what `gimg/server.py` exposes under ``/api/projects/{p}/brand``).

``<data>/projects/<p>/brand/<slug>/`` holds the draft of one brand: every step writes there its copy with the fixed names of
`brand.SYSTEM_FILES` (``<slug>-emblema-alpha.png``...), overwriting the previous draft; the attempt it comes from is never
touched. `save` builds the contact sheet and copies the whole system to ``<data>/projects/<p>/brand-out/<slug>/`` (``data``)
or to the folder ``brand.dir`` of the project configuration (``project``), the way ``compose.templatesDir`` works.
The steps are the functions of `gimg.brand`; this module only decides where their files live."""
import os
import shutil
import subprocess
import tempfile

from . import brand, paths, projects
from .errors import GimgError

FC_TIMEOUT_S = 20
FONT_SUFFIXES = (".ttf", ".otf")
DESTS = ("data", "project")
PIECES = tuple(k for k in brand.SYSTEM_FILES if k != "contactos.png")
STEP_OF = {"emblema-alpha.png": "matte", "emblema.svg": "trace", "emblema-mono.svg": "trace", "wordmark.svg": "wordmark",
           "lockup-h.svg": "lockup", "lockup-v.svg": "lockup"}


def slug_of(name) -> str:
    """The slug of a brand `name` (``brand.empty_text`` / ``brand.bad_name`` if it gives none)."""
    if not isinstance(name, str) or not name.strip():
        raise GimgError("brand.empty_text")
    slug = brand.slugify(name)
    if not slug or len(slug) > 60:
        raise GimgError("brand.bad_name", name=name)
    return slug


def check_slug(slug) -> str:
    """A slug that came in a URL: it must be one (``brand.bad_name``)."""
    if not isinstance(slug, str) or not slug or brand.slugify(slug) != slug:
        raise GimgError("brand.bad_name", name=str(slug))
    return slug


def shop_dir(project: str, slug: str):
    """``<data>/projects/<project>/brand/<slug>`` (guarded). Path only."""
    return paths.inside(paths.project_data_dir(project), "brand/" + slug)


def piece(project: str, slug: str, key: str) -> str:
    return os.path.join(str(shop_dir(project, slug)), "%s-%s" % (slug, key))


def _need(project: str, slug: str, key: str) -> str:
    path = piece(project, slug, key)
    if not os.path.isfile(path):
        raise GimgError("brand.missing_piece", file=os.path.basename(path), step=STEP_OF[key])
    return path


def matte(project: str, name: str, src, **opts) -> dict:
    slug = slug_of(name)
    return brand.matte(src, piece(project, slug, "emblema-alpha.png"), **opts)


def trace(project: str, name: str, mode: str, palette=None, **opts) -> dict:
    slug = slug_of(name)
    if mode not in ("color", "mono"):
        raise GimgError("brand.bad_option", reason="mode must be color or mono (got %r)" % (mode,))
    alpha = _need(project, slug, "emblema-alpha.png")
    out = piece(project, slug, "emblema.svg" if mode == "color" else "emblema-mono.svg")
    return brand.trace(alpha, out, mode, palette, title=name.strip(), **opts)


def _escape(text: str) -> str:
    return "".join("\\" + ch if ch in "\\-:,=()" else ch for ch in text)


def resolve_font(family) -> str:
    """The font file of an installed `family` (``fc-match``); never a path from the client. ``brand.font_unknown`` when no
    installed family is called so (``fc-match`` would answer with a fallback), ``brand.font_unreadable`` when it is no .ttf/.otf."""
    if not isinstance(family, str) or not family.strip() or len(family) > 100 or any(ord(c) < 32 or ord(c) == 127 for c in family):
        raise GimgError("brand.font_unknown", font=str(family)[:100])
    family = family.strip()
    exe = shutil.which("fc-match")
    if exe is None:
        raise GimgError("brand.tool_missing", tool="fc-match")
    try:
        done = subprocess.run([exe, "-f", "%{file}\\n%{family}\\n", _escape(family)], capture_output=True, text=True,
                              errors="replace", timeout=FC_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as exc:
        raise GimgError("brand.tool_failed", tool="fc-match", reason=str(getattr(exc, "strerror", None) or exc)[:300])
    lines = done.stdout.split("\n")
    if done.returncode != 0 or len(lines) < 2 or not lines[0]:
        raise GimgError("brand.font_unknown", font=family)
    if family.lower() not in {n.strip().lower() for n in lines[1].split(",")}:
        raise GimgError("brand.font_unknown", font=family)
    if not lines[0].lower().endswith(FONT_SUFFIXES):
        raise GimgError("brand.font_unreadable", path=lines[0], reason="not a .ttf or .otf file")
    return lines[0]


def wordmark(project: str, name: str, font: str, text=None, **opts) -> dict:
    slug = slug_of(name)
    line = text if text else name.strip().upper()
    return brand.wordmark(line, resolve_font(font), piece(project, slug, "wordmark.svg"), title=name.strip(), **opts)


def lockup(project: str, name: str, layout: str, **opts) -> dict:
    slug = slug_of(name)
    if layout not in brand.LAYOUTS:
        raise GimgError("brand.bad_option", reason="layout must be one of %s (got %r)" % (", ".join(brand.LAYOUTS), layout))
    emblem = _need(project, slug, "emblema.svg")
    word = _need(project, slug, "wordmark.svg")
    return brand.lockup(emblem, word, piece(project, slug, "lockup-%s.svg" % layout), layout, title=name.strip(), **opts)


def listing(project: str) -> list:
    """``[{"slug", "files": [keys present], "modified": epoch}]`` of the workshops of `project`, by slug."""
    base = paths.inside(paths.project_data_dir(project), "brand")
    found = []
    try:
        entries = sorted(os.scandir(base), key=lambda e: e.name)
    except OSError:
        return found
    for entry in entries:
        if not entry.is_dir(follow_symlinks=False) or brand.slugify(entry.name) != entry.name:
            continue
        have, newest = [], 0.0
        for key in brand.SYSTEM_FILES:
            try:
                st = os.stat(os.path.join(entry.path, "%s-%s" % (entry.name, key)))
            except OSError:
                continue
            have.append(key)
            newest = max(newest, st.st_mtime)
        found.append({"slug": entry.name, "files": have, "modified": round(newest, 3)})
    return found


def file_path(project: str, slug: str, key: str):
    """The path of one workshop file (``api.not_found`` for a name that is not in `brand.SYSTEM_FILES`)."""
    if key not in brand.SYSTEM_FILES:
        raise GimgError("api.not_found", path=str(key))
    return paths.inside(shop_dir(project, check_slug(slug)), "%s-%s" % (slug, key))


def save_dir(project: dict, slug: str, dest: str):
    """The folder `save` writes to: see the module docstring. ``brand.dir_missing`` for ``project`` without ``brand.dir``."""
    if dest == "data":
        return paths.inside(paths.project_data_dir(project["name"]), "brand-out/" + slug)
    if dest == "project":
        rel = (project["config"].get("brand") or {}).get("dir")
        if not rel:
            raise GimgError("brand.dir_missing", project=project["name"])
        return paths.inside(project["root"], paths.check_relative(rel).rstrip("/"))
    raise GimgError("brand.bad_option", reason="dest must be one of %s (got %r)" % (", ".join(DESTS), dest))


def save(project: str, name: str, dest: str = "data", force: bool = False) -> dict:
    """Contact sheet and the full system of the workshop of `name` copied to `dest`; ``brand.exists`` if something is
    there and not `force`, ``brand.missing_piece`` if a step has not been done."""
    slug = slug_of(name)
    proj = projects.get(project)
    out_dir = save_dir(proj, slug, dest)
    shop = {key: piece(project, slug, key) for key in brand.SYSTEM_FILES}
    for key in PIECES:
        _need(project, slug, key)
    targets = brand.targets_of(slug, out_dir)
    clash = brand.check_targets(targets, out_dir, force)
    with tempfile.TemporaryDirectory(prefix="gimg-brand-") as tmp:
        size = brand.contact_sheet(shop, tmp)
    for key in brand.SYSTEM_FILES:
        with open(shop[key], "rb") as fh:
            brand._write(targets[key], fh.read())
    return {"name": name.strip(), "slug": slug, "dest": dest, "out_dir": str(out_dir), "files": dict(targets),
            "contact_size": list(size), "overwritten": sorted(clash)}
