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
# .ttc/.otc (collections) are fine: `brand._name_table` reads the family of the first face (``ttcf`` header) and `brand.wordmark`
# copies the file whole into a private fontconfig folder, which indexes every face of it, so rsvg-convert finds the family.
FONT_SUFFIXES = (".ttf", ".otf", ".ttc", ".otc")
# CSS weight (what the API and the SVG ``font-weight`` use) -> fontconfig weight (``FC_WEIGHT_*``), the points of
# ``FcWeightFromOpenType``: 100 thin = 0, 200 extralight = 40, 300 light = 50, 400 regular = 80, 500 medium = 100,
# 600 semibold = 180, 700 bold = 200, 800 extrabold = 205, 900 black = 210 (1000 -> 215); in between, interpolated.
_FC_WEIGHTS = ((1, 0), (100, 0), (200, 40), (300, 50), (400, 80), (500, 100), (600, 180), (700, 200), (800, 205), (900, 210),
               (1000, 215))
DESTS = ("data", "project")
PIECES = tuple(k for k in brand.SYSTEM_FILES if k != "contactos.png")
STEP_OF = {"emblema-alpha.png": "matte", "emblema.svg": "trace", "emblema-mono.svg": "trace", "wordmark.svg": "wordmark",
           "lockup-h.svg": "lockup", "lockup-v.svg": "lockup"}
# What each piece feeds: redoing a step deletes these, so `save` cannot mix pieces drawn from different inputs.
DERIVED = {"emblema-alpha.png": ("emblema.svg", "emblema-mono.svg", "lockup-h.svg", "lockup-v.svg", "contactos.png"),
           "emblema.svg": ("lockup-h.svg", "lockup-v.svg", "contactos.png"),
           "emblema-mono.svg": ("contactos.png",),
           "wordmark.svg": ("lockup-h.svg", "lockup-v.svg", "contactos.png")}


def _stale(project: str, slug: str, key: str) -> None:
    """Delete the pieces of the workshop that derive from the freshly redone `key`."""
    for dep in DERIVED.get(key, ()):
        try:
            os.unlink(piece(project, slug, dep))
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise GimgError("brand.write_failed", path=piece(project, slug, dep), reason=str(exc.strerror or exc)[:300])


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
    result = brand.matte(src, piece(project, slug, "emblema-alpha.png"), **opts)
    _stale(project, slug, "emblema-alpha.png")
    return result


def trace(project: str, name: str, mode: str, palette=None, **opts) -> dict:
    slug = slug_of(name)
    if mode not in ("color", "mono"):
        raise GimgError("brand.bad_option", reason="mode must be color or mono (got %r)" % (mode,))
    alpha = _need(project, slug, "emblema-alpha.png")
    out = piece(project, slug, "emblema.svg" if mode == "color" else "emblema-mono.svg")
    result = brand.trace(alpha, out, mode, palette, title=name.strip(), **opts)
    _stale(project, slug, "emblema.svg" if mode == "color" else "emblema-mono.svg")
    return result


def _escape(text: str) -> str:
    return "".join("\\" + ch if ch in "\\-:,=()" else ch for ch in text)


def fc_weight(css_weight) -> int:
    """The fontconfig weight of a CSS weight 1-1000 (`_FC_WEIGHTS`)."""
    w = max(1, min(1000, css_weight))
    for (w0, f0), (w1, f1) in zip(_FC_WEIGHTS, _FC_WEIGHTS[1:]):
        if w <= w1:
            return round(f0 + (f1 - f0) * (w - w0) / (w1 - w0))
    return _FC_WEIGHTS[-1][1]


def resolve_font(family, weight=None) -> str:
    """The font file of an installed `family` (``fc-match``, asked for the pattern ``family:weight=N`` with `fc_weight` of the
    CSS `weight` when given, so a family of static files answers with the face of that weight); never a path from the client.
    ``brand.font_unknown`` when no installed family is called so (``fc-match`` would answer with a fallback),
    ``brand.font_unreadable`` when it is no .ttf/.otf/.ttc/.otc."""
    if not isinstance(family, str) or not family.strip() or len(family) > 100 or any(ord(c) < 32 or ord(c) == 127 for c in family):
        raise GimgError("brand.font_unknown", font=str(family)[:100])
    family = family.strip()
    pattern = _escape(family)
    if weight is not None:
        brand._check_weight_spacing(weight, None)  # the error and message that wordmark gives
        pattern += ":weight=%d" % fc_weight(weight)
    exe = shutil.which("fc-match")
    if exe is None:
        raise GimgError("brand.tool_missing", tool="fc-match")
    try:
        done = subprocess.run([exe, "-f", "%{file}\\n%{family}\\n%{index}\\n", pattern], capture_output=True, text=True,
                              errors="replace", timeout=FC_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as exc:
        raise GimgError("brand.tool_failed", tool="fc-match", reason=str(getattr(exc, "strerror", None) or exc)[:300])
    lines = done.stdout.split("\n")
    if done.returncode != 0 or len(lines) < 3 or not lines[0]:
        raise GimgError("brand.font_unknown", font=family)
    if family.lower() not in {n.strip().lower() for n in lines[1].split(",")}:
        raise GimgError("brand.font_unknown", font=family)
    if not lines[0].lower().endswith(FONT_SUFFIXES):
        raise GimgError("brand.font_unreadable", path=lines[0], reason="not a .ttf, .otf, .ttc or .otc file")
    # fontconfig packs the named instance of a variable font in the high 16 bits (131072 = face 0, instance 1): only the
    # face (low 16 bits) matters, since brand reads the names of face 0 of a collection
    raw = lines[2].strip()
    face = int(raw) & 0xFFFF if raw.isdigit() else raw
    if face not in ("", 0):
        raise GimgError("brand.font_unreadable", path=lines[0], reason="the face is number %s of a font collection: only a face 0 is read" % face)
    return lines[0]


def wordmark(project: str, name: str, font: str, text=None, **opts) -> dict:
    slug = slug_of(name)
    line = text if text else name.strip().upper()
    result = brand.wordmark(line, resolve_font(font, opts.get("weight") or brand.DEFAULT_WEIGHT), piece(project, slug, "wordmark.svg"), title=name.strip(), **opts)
    _stale(project, slug, "wordmark.svg")
    return result


def lockup(project: str, name: str, layout: str, **opts) -> dict:
    slug = slug_of(name)
    if layout not in brand.LAYOUTS:
        raise GimgError("brand.bad_option", reason="layout must be one of %s (got %r)" % (", ".join(brand.LAYOUTS), layout))
    emblem = _need(project, slug, "emblema.svg")
    word = _need(project, slug, "wordmark.svg")
    return brand.lockup(emblem, word, piece(project, slug, "lockup-%s.svg" % layout), layout, title=name.strip(), force=True, **opts)


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
            brand.write_file(targets[key], fh.read())
    return {"name": name.strip(), "slug": slug, "dest": dest, "out_dir": str(out_dir), "files": dict(targets),
            "contact_size": list(size), "overwritten": sorted(clash)}
