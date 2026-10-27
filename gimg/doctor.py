"""`gimg doctor`: what is missing for the real engine, and the command that fixes each thing (F2.5, D5, D28, D36).

`run()` returns a list of `Check`; none of them changes anything on disk or starts `sd-cli`. Statuses: ``ok``, ``warn``
(works, but look at it) and ``fail`` (the command exits 1). What the real engine needs (binary, libraries, models,
Ollama) is a ``fail`` when the configured engine is ``sdcpp`` and only a ``warn`` while it is ``fake`` (D36): a fresh
clone with nothing installed is not "broken", it is not installed yet.

Checks, in order: Python, launcher in ``PATH``, ``config.json``, configured engine, machine profile, ``sd-cli`` and the
``libggml*`` next to it (``LD_LIBRARY_PATH`` is that folder, D33), models of the catalog by id, free memory, ``ffmpeg`` and
``rsvg-convert`` (D28: checked, never installed), data folder, flatpak, Ollama.

- **Models:** a model with no file at all is fine when it is optional (``installDefault`` is not true in the catalog) and
  a problem when it is a default one; a model with only some files is always a problem. A file that is there is checked
  by size against ``sizeMb`` (10^6 bytes, rounded: +-1 MB) and, only with ``verify=True``, by sha256.
- **Flatpak:** an editor in flatpak sets ``XDG_DATA_HOME=~/.var/app/<id>/data``, and gimg run from its terminal would use
  another data folder (and models) than from a normal one. The XDG variables are honoured, not ignored; the check warns and
  says to set ``GIMG_DATA_HOME`` / ``GIMG_CONFIG_HOME`` (which win over XDG, `paths`).
- **Ollama:** skipped with ``engine.ollama: ignore``; the URL is the one of `engine_sdcpp.ollama_url` (``GIMG_OLLAMA_URL``)
  or the ``ollama_url`` argument. A service that is off counts as "nothing loaded", as in the engine.
"""
from __future__ import annotations

import hashlib
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import engine, engine_sdcpp, fsutil, i18n, limits, models, paths
from .errors import GimgError

OK, WARN, FAIL = "ok", "warn", "fail"
REPO = Path(__file__).resolve().parent.parent
TOOL_TIMEOUT_S = 10
HASH_CHUNK = 1 << 20
SIZE_TOLERANCE_MB = 1.0
MIN_PYTHON = (3, 10)
_STATUS_KEYS = {OK: "doctor.status.ok", WARN: "doctor.status.warn", FAIL: "doctor.status.fail"}
# tool -> (version flag, apt package, pacman package)
TOOLS = {"ffmpeg": ("-version", "ffmpeg", "ffmpeg"), "rsvg-convert": ("--version", "librsvg2-bin", "librsvg")}


@dataclass
class Check:
    id: str
    status: str
    key: str
    params: dict = field(default_factory=dict)
    fix_key: Optional[str] = None
    fix_params: dict = field(default_factory=dict)

    def message(self, lang=None) -> str:
        return i18n.t(self.key, lang, **self.params)

    def fix(self, lang=None) -> Optional[str]:
        return i18n.t(self.fix_key, lang, **self.fix_params) if self.fix_key else None

    def label(self, lang=None) -> str:
        return i18n.t(_STATUS_KEYS[self.status], lang)

    def as_dict(self, lang=None) -> dict:
        return {"id": self.id, "status": self.status, "message": self.message(lang), "fix": self.fix(lang)}


def failed(checks) -> bool:
    return any(c.status == FAIL for c in checks)


def _install_cmd(*flags) -> str:
    return " ".join(["bash", shlex.quote(str(REPO / "instalar.sh"))] + list(flags))


def _first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def tool_version(exe: str, flag: str) -> Optional[str]:
    """First line of ``<exe> <flag>``, or ``""`` when it runs but prints nothing, or ``None`` when it cannot run."""
    try:
        done = subprocess.run([exe, flag], capture_output=True, text=True, errors="replace", timeout=TOOL_TIMEOUT_S,
                              stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    return _first_line(done.stdout) or _first_line(done.stderr)


def sha256_of(path, chunk: int = HASH_CHUNK) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def _python() -> Check:
    version = "%d.%d.%d" % sys.version_info[:3]
    if sys.version_info[:2] >= MIN_PYTHON:
        return Check("python", OK, "doctor.python.ok", {"version": version})
    return Check("python", FAIL, "doctor.python.old", {"version": version, "min": "%d.%d" % MIN_PYTHON},
                 "doctor.fix.python")


def _launcher() -> Check:
    found = shutil.which("gimg")
    if found:
        return Check("launcher", OK, "doctor.launcher.ok", {"path": found})
    folder = Path.home() / ".local" / "bin"
    if (folder / "gimg").is_file():
        return Check("launcher", WARN, "doctor.launcher.not_in_path", {"dir": str(folder)},
                     "doctor.fix.path", {"line": 'export PATH="$HOME/.local/bin:$PATH"'})
    return Check("launcher", FAIL, "doctor.launcher.missing", {"dir": str(folder)},
                 "doctor.fix.install", {"cmd": _install_cmd("--only-cli")})


def _config() -> tuple:
    """(checks, real): `real` is True when the configured engine is ``sdcpp``."""
    out = []
    path = paths.config_dir() / "config.json"
    try:
        fsutil.read_json(path)
    except FileNotFoundError:
        out.append(Check("config", WARN, "doctor.config.missing", {"path": str(path)},
                         "doctor.fix.install", {"cmd": _install_cmd()}))
    except (OSError, ValueError) as exc:
        out.append(Check("config", FAIL, "doctor.config.unreadable", {"path": str(path), "reason": str(exc)},
                         "doctor.fix.config", {"path": str(path)}))
    else:
        out.append(Check("config", OK, "doctor.config.ok", {"path": str(path)}))
    try:
        name = engine._configured_engine()
    except GimgError as exc:
        out.append(Check("engine", FAIL, "doctor.engine.error", {"message": exc.message()},
                         "doctor.fix.config", {"path": str(path)}))
        return out, False
    if name == "sdcpp":
        out.append(Check("engine", OK, "doctor.engine.sdcpp"))
    elif name == "fake":
        out.append(Check("engine", WARN, "doctor.engine.fake", {},
                         "doctor.fix.install", {"cmd": _install_cmd()}))
    else:
        out.append(Check("engine", FAIL, "doctor.engine.unknown", {"engine": name},
                         "doctor.fix.config", {"path": str(path)}))
    return out, name == "sdcpp"


def _machine() -> tuple:
    try:
        machine = limits.load_machine()
    except GimgError as exc:
        return {}, Check("machine", FAIL, "doctor.machine.error", {"message": exc.message()}, "doctor.fix.machine")
    return machine, Check("machine", OK, "doctor.machine.ok", {"name": machine.get("name", limits.DEFAULT_PROFILE)})


def _binary(machine: dict, bad: str) -> list:
    binary = engine_sdcpp.binary_path(machine)
    fix = ("doctor.fix.install", {"cmd": _install_cmd()})
    if not binary.is_file():
        return [Check("binary", bad, "doctor.binary.missing", {"path": str(binary)}, *fix)]
    if not os.access(binary, os.X_OK):
        return [Check("binary", bad, "doctor.binary.not_executable", {"path": str(binary)},
                      "doctor.fix.chmod", {"path": shlex.quote(str(binary))})]
    out = [Check("binary", OK, "doctor.binary.ok", {"path": str(binary)})]
    libs = sorted(p.name for p in binary.parent.glob("libggml*"))
    if libs:
        out.append(Check("libs", OK, "doctor.libs.ok", {"dir": str(binary.parent), "count": len(libs)}))
    else:
        out.append(Check("libs", bad, "doctor.libs.missing", {"dir": str(binary.parent)}, *fix))
    return out


def _model(model_id: str, model: dict, machine: dict, catalog: dict, verify: bool, bad: str) -> Check:
    resolved = models.resolve(model_id, machine, catalog)
    missing = models.missing_files(resolved)
    install = ("doctor.fix.install", {"cmd": _install_cmd()})
    if len(missing) == len(models.KINDS):
        if model.get("installDefault"):
            return Check("model:" + model_id, bad, "doctor.model.absent", {"id": model_id}, *install)
        return Check("model:" + model_id, OK, "doctor.model.optional", {"id": model_id},
                     "doctor.fix.with", {"cmd": _install_cmd("--with", model_id)})
    if missing:
        names = ", ".join("%s/%s" % (k, resolved["files"][k]["name"]) for k in missing)
        flags = ("--with", model_id) if not model.get("installDefault") else ()
        return Check("model:" + model_id, FAIL, "doctor.model.partial", {"id": model_id, "files": names},
                     "doctor.fix.install", {"cmd": _install_cmd(*flags)})
    for kind in models.KINDS:
        entry = resolved["files"][kind]
        size_mb = Path(entry["path"]).stat().st_size / 1e6
        if abs(size_mb - entry["sizeMb"]) > SIZE_TOLERANCE_MB:
            return Check("model:" + model_id, FAIL, "doctor.model.size",
                         {"id": model_id, "file": entry["name"], "got": round(size_mb), "want": entry["sizeMb"]},
                         "doctor.fix.redo", {"path": shlex.quote(str(entry["path"])), "cmd": _install_cmd()})
        if verify and sha256_of(entry["path"]) != entry["sha256"]:
            return Check("model:" + model_id, FAIL, "doctor.model.sha", {"id": model_id, "file": entry["name"]},
                         "doctor.fix.redo", {"path": shlex.quote(str(entry["path"])), "cmd": _install_cmd()})
    if verify:
        return Check("model:" + model_id, OK, "doctor.model.ok_sha", {"id": model_id})
    return Check("model:" + model_id, OK, "doctor.model.ok_size", {"id": model_id})


def _models(machine: dict, verify: bool, bad: str) -> list:
    try:
        catalog = models.load_catalog()
    except GimgError as exc:
        return [Check("models", FAIL, "doctor.models.catalog", {"message": exc.message()})]
    return [_model(mid, catalog["models"][mid], machine, catalog, verify, bad) for mid in models.ids(catalog)]


def _memory(machine: dict) -> list:
    free, needed = engine_sdcpp.read_meminfo_mb(), machine.get("minFreeMemoryMb")
    if free is None or not needed:
        return []
    if free >= needed:
        return [Check("memory", OK, "doctor.memory.ok", {"free": free, "needed": needed})]
    return [Check("memory", WARN, "doctor.memory.low", {"free": free, "needed": needed}, "doctor.fix.memory")]


def _tools() -> list:
    out = []
    for name, (flag, apt, pacman) in TOOLS.items():
        found = shutil.which(name)
        version = tool_version(found, flag) if found else None
        if found and version is not None:
            out.append(Check("tool:" + name, OK, "doctor.tool.ok", {"tool": name, "version": version or "?"}))
        elif found:
            out.append(Check("tool:" + name, FAIL, "doctor.tool.broken", {"tool": name, "path": found},
                             "doctor.fix.tool", {"tool": name, "apt": apt, "pacman": pacman}))
        else:
            out.append(Check("tool:" + name, FAIL, "doctor.tool.missing", {"tool": name},
                             "doctor.fix.tool", {"tool": name, "apt": apt, "pacman": pacman}))
    return out


def _folders() -> list:
    out = []
    data = paths.data_dir()
    if not data.exists():
        out.append(Check("data", WARN, "doctor.data.missing", {"path": str(data)}, "doctor.fix.mkdir",
                         {"path": shlex.quote(str(data))}))
    elif not data.is_dir() or not os.access(data, os.W_OK | os.X_OK):
        out.append(Check("data", FAIL, "doctor.data.unwritable", {"path": str(data)}, "doctor.fix.chmod_dir",
                         {"path": shlex.quote(str(data))}))
    else:
        out.append(Check("data", OK, "doctor.data.ok", {"path": str(data)}))
    seen, exports = [], []
    for xdg, own, normal in (("XDG_DATA_HOME", "GIMG_DATA_HOME", "$HOME/.local/share/gimg"),
                             ("XDG_CONFIG_HOME", "GIMG_CONFIG_HOME", "$HOME/.config/gimg")):
        value = os.environ.get(xdg, "")
        if "/.var/app/" in value and not os.environ.get(own):
            seen.append("%s=%s" % (xdg, value))
            exports.append('export %s="%s"' % (own, normal))
    if seen:
        out.append(Check("flatpak", WARN, "doctor.flatpak.warn",
                         {"vars": ", ".join(seen), "data": str(data), "config": str(paths.config_dir())},
                         "doctor.fix.flatpak", {"lines": "; ".join(exports)}))
    return out


def _ollama(machine: dict, bad: str, ollama_url: Optional[str]) -> Check:
    mode = (machine.get("engine") or {}).get("ollama", "abort")
    if mode == "ignore":
        return Check("ollama", OK, "doctor.ollama.ignored")
    try:
        url = ollama_url.rstrip("/") if ollama_url else engine_sdcpp.ollama_url(machine)
    except GimgError as exc:
        return Check("ollama", FAIL, "doctor.ollama.bad_url", {"message": exc.message()}, "doctor.fix.machine")
    loaded = engine_sdcpp.ollama_loaded(url)
    if not loaded:
        return Check("ollama", OK, "doctor.ollama.ok", {"url": url})
    names = ", ".join(loaded)
    if mode == "unload":
        return Check("ollama", WARN, "doctor.ollama.loaded_unload", {"models": names})
    return Check("ollama", bad, "doctor.ollama.loaded", {"models": names},
                 "doctor.fix.ollama", {"cmds": "; ".join("ollama stop " + n for n in loaded)})


def run(verify: bool = False, ollama_url: Optional[str] = None) -> list:
    """All the checks, in display order. `verify` sums the sha256 of every installed model file (slow: GBs)."""
    checks = [_python(), _launcher()]
    config_checks, real = _config()
    bad = FAIL if real else WARN
    machine, machine_check = _machine()
    checks += config_checks + [machine_check]
    checks += _binary(machine, bad)
    checks += _models(machine, verify, bad)
    checks += _memory(machine)
    checks += _tools()
    checks += _folders()
    checks.append(_ollama(machine, bad, ollama_url))
    return checks
