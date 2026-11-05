"""Model catalog (D30): loading, validation, and resolution of a model against a machine profile."""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import paths, schema
from .errors import GimgError

CATALOG = Path(__file__).resolve().parent / "models.json"
KINDS = ("diffusion", "text", "vae")  # also the subfolders of `paths.models_dir()`


def load_catalog(path=None) -> dict:
    """Read and validate the catalog: `path`, else ``$GIMG_CATALOG`` (a test seam: `instalar.sh` and `gimg doctor` read
    the catalog in their own processes), else `gimg/models.json`.

    Returns the parsed JSON. Raises ``model.catalog_invalid`` when it cannot be read, is not JSON
    or does not pass `models.schema.json`."""
    path = Path(path) if path is not None else Path(os.environ.get("GIMG_CATALOG") or CATALOG)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise GimgError("model.catalog_invalid", path=str(path), reason=str(exc))
    errors = schema.validate(data, schema.load_schema("models"))
    if errors:
        raise GimgError("model.catalog_invalid", errors=errors, path=str(path))
    return data


def ids(catalog=None) -> list:
    return sorted((catalog or load_catalog())["models"])


def check_known(model_id, catalog=None) -> str:
    """Return `model_id` if the catalog has it (exact match: ids are lowercase, nothing is
    normalized), else raise ``model.unknown`` with the known ids."""
    models = (catalog or load_catalog())["models"]
    if not isinstance(model_id, str) or model_id not in models:
        raise GimgError("model.unknown", model=str(model_id), known=", ".join(sorted(models)))
    return model_id


def resolve(model_id, machine, catalog=None) -> dict:
    """Effective settings to run `model_id` on `machine` (a loaded machine profile).

    - ``defaults``: ``steps``, ``cfg``, ``sampler`` of the catalog.
    - ``args``: the catalog ``args`` followed by ``engine.models.<id>.args`` of the machine.
    - ``initImageArgs``: the catalog ones (default ``[]``), added by the engine only for img2img.
    - ``timeoutS``, ``minFreeMemoryMb``: ``engine.models.<id>`` if the profile sets them for this
      model, else the profile's general ones.
    - ``files``: ``{kind: {"name", "url", "sha256", "sizeMb", "path"}}`` with the expected
      ``path`` under `paths.models_dir()`; nothing is checked on disk (see `missing_files`).

    An ``engine.models`` entry of the machine profile naming a model that is not in the catalog is
    ignored (a profile may outlive a catalog change); asking for that id raises ``model.unknown``."""
    catalog = catalog or load_catalog()
    check_known(model_id, catalog)
    model = catalog["models"][model_id]
    engine = machine.get("engine") or {}
    own = (engine.get("models") or {}).get(model_id) or {}
    root = paths.models_dir()
    files = {}
    for kind in KINDS:
        entry = dict(model["files"][kind])
        entry["path"] = root / kind / entry["name"]
        files[kind] = entry
    return {
        "id": model_id,
        "license": model["license"],
        "defaults": dict(model["defaults"]),
        "args": list(model["args"]) + list(own.get("args", [])),
        "initImageArgs": list(model.get("initImageArgs", [])),
        "timeoutS": own.get("timeoutS", machine.get("timeoutS")),
        "minFreeMemoryMb": own.get("minFreeMemoryMb", machine.get("minFreeMemoryMb")),
        "files": files,
    }


def missing_files(resolved) -> list:
    """Kinds (``diffusion``, ``text``, ``vae``) whose expected file is not a file on disk."""
    return [k for k in KINDS if not Path(resolved["files"][k]["path"]).is_file()]


def check_allowed(model_id, machine, catalog=None, steps=None) -> str:
    """`check_known`, plus the machine's limits for this model: its steps (`steps` if given, else the catalog default)
    must not exceed ``maxSteps`` (``limit.steps``, as in `limits.check`). Returns `model_id`."""
    catalog = catalog or load_catalog()
    check_known(model_id, catalog)
    wanted = steps if steps is not None else catalog["models"][model_id]["defaults"].get("steps")
    max_steps = machine.get("maxSteps")
    if wanted is not None and max_steps is not None and wanted > max_steps:
        from . import limits
        raise limits.LimitError("limit.steps", steps=wanted, max=max_steps)
    return model_id


def listing(lang=None, machine=None, catalog=None) -> list:
    """``GET /api/models``: the catalog as ``[{"id", "license", "defaults", "installDefault", "allowed", "reason"?}]``.
    ``allowed`` is False when the machine profile's limits stop the model (`check_allowed`); ``reason`` is then
    ``{"code", "message"}`` of that ``limit.*`` error."""
    from . import limits
    catalog = catalog or load_catalog()
    machine = machine if machine is not None else limits.load_machine()
    out = []
    for model_id in ids(catalog):
        model = catalog["models"][model_id]
        item = {"id": model_id, "license": model["license"], "defaults": dict(model["defaults"]),
                "installDefault": model.get("installDefault") is True, "allowed": True}
        try:
            check_allowed(model_id, machine, catalog)
        except GimgError as exc:
            item["allowed"] = False
            item["reason"] = {"code": exc.code, "message": exc.message(lang)}
        out.append(item)
    return out
