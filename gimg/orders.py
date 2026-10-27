"""Orders and attempts (D18-D20): storage, states, notes, choose and undo.

Layout: ``<data>/projects/<project>/orders/<key>/@<profile>/order.json`` and
``.../attempts/<id>.png``. The ``@`` keeps key ``a/banner`` apart from key ``a`` + profile ``banner``.

This module neither enqueues (queue, F1.4) nor delivers (F1.5): `choose` and `undo` return the old and
new chosen ids so delivery can hook in. Every read-modify-write holds `fsutil.lock` of ``order.json``.

Public API: `submit`, `attempt_specs`, `add_attempt`, `attempt_for_entry`, `attempt_image`, `pending_image_path`, `mark`, `note`, `choose`,
`undo`, `get`, `list_orders`. All raise `GimgError` with codes ``order.*`` on bad input.
"""
from __future__ import annotations

import copy
import os
import random
from datetime import datetime, timezone
from pathlib import Path

from . import fsutil, paths, projects, schema
from .errors import GimgError

STATES = ("new", "candidate", "discarded")
SEED_LIMIT = 2 ** 32
_PROFILE_PARAMS = ("width", "height", "steps", "cfg", "sampler", "model")
_ORDER_FILE = "order.json"
_FULL_PARAMS = {"type": "object", "properties": {
    "width": {"type": "integer", "minimum": 1}, "height": {"type": "integer", "minimum": 1},
    "model": {"type": "string", "minLength": 1}}}
DRAFT_STEPS = 8
DRAFT_SCALE = 0.5
SIDE_STEP = 64
_rng = random.SystemRandom()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_id(key, profile) -> None:
    """key and profile must satisfy the order schema (``key`` and ``profileName`` patterns) and D25."""
    _check_fields_of({"key": key, "profile": profile, "prompt": "x"})
    paths.check_key(key)


def _check_fields_of(probe: dict) -> None:
    errors = schema.validate(probe, schema.load_schema("order"))
    if errors:
        raise GimgError("order.invalid", errors=errors)


def _order_dir(project: str, key: str, profile: str) -> Path:
    """Folder of one order. Every public entry point builds it, so key and profile are validated here."""
    _check_id(key, profile)
    return paths.inside(paths.project_data_dir(project), "orders/%s/@%s" % (key, profile))


def _order_file(project: str, key: str, profile: str) -> Path:
    return _order_dir(project, key, profile) / _ORDER_FILE


def attempt_image(project: str, key: str, profile: str, attempt: dict) -> Path:
    """Where the image of an attempt record lives: its ``image`` field, relative to the order folder
    (``attempts/<id>.png``, or ``attempts/q<entry>.png`` for an attempt made by a queue entry).
    The path is resolved and must stay inside the order folder (D25). Path only; nothing is read."""
    return paths.inside(_order_dir(project, key, profile), attempt["image"])


def pending_image_path(project: str, key: str, profile: str, entry_id: int) -> Path:
    """Where the engine writes the image of queue entry `entry_id` before it is final:
    ``attempts/.pending-<entry>.png`` (same filesystem as the final ``attempts/q<entry>.png``)."""
    return _order_dir(project, key, profile) / "attempts" / (".pending-%d.png" % int(entry_id))


def entry_image_name(entry_id: int) -> str:
    """The ``image`` field of the attempt made by queue entry `entry_id` (unique across the generator)."""
    return "attempts/q%d.png" % int(entry_id)


def draft_params(profile_cfg: dict, params: dict) -> dict:
    """The params of a draft (D32), from the profile and the params the attempt would have (a copy).

    Without ``draft`` in the profile: sides x 0.5, 8 steps, same model. With it: ``scale`` (else 1), ``steps`` and
    ``model`` (else the ones `params` already has). With a `scale` other than 1 each side becomes
    ``max(64, int(side * scale / 64 + 0.5) * 64)`` (half rounds up); with none, or 1, the sides are not touched.
    cfg and sampler do not change."""
    out = copy.deepcopy(params)
    declared = profile_cfg.get("draft")
    if declared is None:
        scale, out["steps"] = DRAFT_SCALE, DRAFT_STEPS
    else:
        scale = declared.get("scale", 1)
        if "steps" in declared:
            out["steps"] = declared["steps"]
        if "model" in declared:
            out["model"] = declared["model"]
    if scale != 1:
        for side in ("width", "height"):
            if side in out:
                out[side] = max(SIDE_STEP, int(out[side] * scale / SIDE_STEP + 0.5) * SIDE_STEP)
    return out


def _profile(config: dict, profile: str) -> dict:
    found = config["profiles"].get(profile)
    if found is None:
        raise GimgError("order.profile_unknown", profile=profile)
    return found


def _check_fields(prompt=None, params=None, seed=None) -> None:
    """Validate loose fields (overrides) with the order schema, through a dummy order."""
    probe = {"key": "x", "profile": "x", "prompt": "x" if prompt is None else prompt}
    if params is not None:
        probe["params"] = params
    if seed is not None:
        probe["seed"] = seed
    _check_fields_of(probe)


def _read(project: str, key: str, profile: str) -> dict:
    path = _order_file(project, key, profile)
    try:
        data = fsutil.read_json(path)
    except FileNotFoundError:
        raise GimgError("order.unknown", project=project, order=key, profile=profile)
    except (OSError, ValueError):
        raise GimgError("order.corrupt", path=str(path))
    return _shape(data, path)


def _shape(data, path) -> dict:
    if (not isinstance(data, dict) or not isinstance(data.get("attempts"), list)
            or not isinstance(data.get("profile"), str) or not isinstance(data.get("key"), str)
            or "chosen" not in data or not isinstance(data.get("chosenHistory"), list)):
        raise GimgError("order.corrupt", path=str(path))
    return data


def _modify(project: str, key: str, profile: str, change):
    """Locked read-modify-write: `change(order)` edits in place and returns the call's result."""
    path = _order_file(project, key, profile)
    if not path.exists():  # do not create folders or lock files for an unknown order
        raise GimgError("order.unknown", project=project, order=key, profile=profile)
    with fsutil.lock(path):
        order = _read(project, key, profile)
        result = change(order)
        order["updatedAt"] = _now()
        fsutil.write_json(path, order)
    return result


def _attempt(order: dict, attempt_id) -> dict:
    for item in order["attempts"]:
        if type(attempt_id) is int and item["id"] == attempt_id:
            return item
    raise GimgError("order.attempt_unknown", attempt=attempt_id, order=order["key"], profile=order["profile"])


def submit(project: str, order: dict) -> dict:
    """Create or update an order (D18); returns the stored record (a copy).

    `order` follows the ``order`` schema (``count`` is accepted but not stored: it is for the caller to
    pass to `attempt_specs`). Resubmitting the same key + profile replaces prompt, references, params
    seed (a missing ``seed`` clears it) and draft (a missing one is false) and keeps attempts, chosen and history. Does not enqueue."""
    errors = schema.validate(order, schema.load_schema("order"))
    if errors:
        raise GimgError("order.invalid", errors=errors)
    paths.check_key(order["key"])
    config = projects.get(project)["config"]
    _profile(config, order["profile"])
    key, profile = order["key"], order["profile"]
    fields = {
        "prompt": order["prompt"],
        "references": list(order.get("references", [])),
        "params": copy.deepcopy(order.get("params", {})),
        "seed": order.get("seed"),
        "draft": bool(order.get("draft", False)),
    }
    path = _order_file(project, key, profile)
    with fsutil.lock(path):
        now = _now()
        try:
            record = _read(project, key, profile)
        except GimgError as exc:
            if exc.code != "order.unknown":
                raise
            record = {"key": key, "profile": profile, "createdAt": now, "attempts": [],
                      "chosen": None, "chosenHistory": []}
        record.update(fields)
        record["updatedAt"] = now
        fsutil.write_json(path, record)
    return copy.deepcopy(record)


def attempt_specs(project: str, key: str, profile: str, count: int = 1, *,
                  seed=None, prompt=None, params=None, draft=None) -> list:
    """Specs of `count` attempts to enqueue; never changes the stored order (D19-D20).

    Each spec is ``{"seed", "prompt", "params", "references", "draft"}``:
    - seed: `seed` if given, else the order's seed, then ``seed + i`` for attempt i (0-based);
      with neither, a random integer in ``[0, 2**32)`` per attempt (`random.SystemRandom`).
    - params: profile settings (width, height, steps, cfg, sampler, model; only those the profile
      defines) overridden by the order's params, then by `params` (steps, cfg, sampler), then, for a draft,
      by `draft_params`; a ``steps`` in `params` wins over the draft's steps.
    - draft: `draft` if given (True/False), else the order's ``draft``.
    - prompt: `prompt` (a retouched one) or the order's, plus the profile ``style`` appended as
      ``prompt + ", " + style`` when the style is non-empty (otherwise the prompt alone)."""
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 50:
        raise GimgError("order.count_invalid", min=1, max=50)
    _check_fields(prompt, params, seed)
    order = get(project, key, profile)
    profile_cfg = _profile(projects.get(project)["config"], profile)
    full = {k: profile_cfg[k] for k in _PROFILE_PARAMS if k in profile_cfg}
    full.update(order["params"])
    full.update(params or {})
    is_draft = bool(order.get("draft", False)) if draft is None else bool(draft)
    if is_draft:
        full = draft_params(profile_cfg, full)
        if "steps" in (params or {}):
            full["steps"] = params["steps"]
    text = order["prompt"] if prompt is None else prompt
    style = profile_cfg.get("style", "")
    if style:
        text = "%s, %s" % (text, style)
    max_prompt = schema.load_schema("order")["properties"]["prompt"]["maxLength"]
    if len(text) > max_prompt:
        raise GimgError("order.prompt_too_long", length=len(text), max=max_prompt)
    base = order["seed"] if seed is None else seed
    return [{
        "seed": _rng.randrange(SEED_LIMIT) if base is None else base + i,
        "prompt": text,
        "params": copy.deepcopy(full),
        "references": list(order["references"]),
        "draft": is_draft,
    } for i in range(count)]


def attempt_for_entry(project: str, key: str, profile: str, entry_id: int):
    """The attempt made by queue entry `entry_id` (a copy), or ``None``."""
    for item in get(project, key, profile)["attempts"]:
        if item.get("queueEntry") == entry_id and type(entry_id) is int:
            return copy.deepcopy(item)
    return None


def add_attempt(project: str, key: str, profile: str, spec: dict, entry_id=None) -> int:
    """Append an attempt in state ``new`` (used by the worker after generating); returns its id.

    Ids are sequential from 1. `spec` needs ``seed``, ``prompt`` and ``params``; ``references``
    defaults to the order's; ``engine`` / ``engineVersion`` / ``log`` (strings, optional), ``command`` (list of strings) and ``modelFiles`` (name by kind) are stored as given when they have that type (D34). Without `entry_id`, ``image`` is ``attempts/<id>.png``, relative to the order
    folder. With `entry_id` (the queue entry that made it) ``image`` is ``attempts/q<entry>.png`` and the
    attempt records ``queueEntry``; the call is idempotent per entry: if an attempt with that
    ``queueEntry`` exists, its id is returned and nothing is added."""
    if entry_id is not None and (type(entry_id) is not int or entry_id < 1):
        raise GimgError("order.spec_invalid", missing="entry_id")
    missing = [k for k in ("seed", "prompt", "params") if k not in spec]
    if missing:
        raise GimgError("order.spec_invalid", missing=", ".join(missing))
    params = spec["params"]
    if isinstance(params, dict):
        extra = {k: v for k, v in params.items() if k not in ("width", "height", "model")}
        errors = schema.validate(params, _FULL_PARAMS)
        if errors:
            raise GimgError("order.invalid", errors=errors)
        _check_fields(spec["prompt"], extra, spec["seed"])
    else:
        _check_fields(spec["prompt"], params, spec["seed"])

    def change(order):
        if entry_id is not None:
            for item in order["attempts"]:
                if item.get("queueEntry") == entry_id:
                    return item["id"]
        new_id = max((a["id"] for a in order["attempts"]), default=0) + 1
        record = {
            "id": new_id,
            "state": "new",
            "seed": spec["seed"],
            "prompt": spec["prompt"],
            "params": copy.deepcopy(spec["params"]),
            "references": list(spec.get("references", order["references"])),
            "image": "attempts/%d.png" % new_id if entry_id is None else entry_image_name(entry_id),
            "note": "",
            "createdAt": _now(),
        }
        if entry_id is not None:
            record["queueEntry"] = entry_id
        if spec.get("draft") is True:  # only drafts carry the key, so stored orders keep their shape
            record["draft"] = True
        for extra in ("engine", "engineVersion", "log"):  # which engine made it (the manifest repeats the first two)
            if isinstance(spec.get(extra), str):
                record[extra] = spec[extra]
        command, files = spec.get("command"), spec.get("modelFiles")  # D34: how to repeat it
        if isinstance(command, list) and all(isinstance(a, str) for a in command):
            record["command"] = list(command)
        if isinstance(files, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
            record["modelFiles"] = dict(files)
        order["attempts"].append(record)
        return new_id

    return _modify(project, key, profile, change)


def mark(project: str, key: str, profile: str, attempt_id: int, state: str) -> dict:
    """Set an attempt's state (new|candidate|discarded); the chosen one cannot be discarded."""
    if state not in STATES:
        raise GimgError("order.state_invalid", state=str(state), states=", ".join(STATES))

    def change(order):
        item = _attempt(order, attempt_id)
        if state == "discarded" and order["chosen"] == attempt_id:
            raise GimgError("order.discard_chosen", attempt=attempt_id)
        item["state"] = state
        return copy.deepcopy(item)

    return _modify(project, key, profile, change)


def note(project: str, key: str, profile: str, attempt_id: int, text: str) -> dict:
    """Replace an attempt's note (``""`` clears it)."""
    if not isinstance(text, str):
        raise GimgError("order.note_invalid")

    def change(order):
        item = _attempt(order, attempt_id)
        item["note"] = text
        return copy.deepcopy(item)

    return _modify(project, key, profile, change)


def check_choosable(attempt: dict) -> None:
    """The one eligibility rule: a discarded attempt and a draft cannot be chosen (raises, else returns)."""
    if attempt["state"] == "discarded":
        raise GimgError("order.choose_discarded", attempt=attempt["id"])
    if attempt.get("draft") is True:
        raise GimgError("order.choose_draft", attempt=attempt["id"])


def choose(project: str, key: str, profile: str, attempt_id: int) -> dict:
    """Choose an attempt; returns ``{"old": id|None, "new": id}`` for delivery to act on.

    The previous chosen (even ``None``) is pushed to ``chosenHistory``. A discarded attempt and a draft
    cannot be chosen. Choosing the already chosen attempt changes nothing (``old == new``, no push)."""
    def change(order):
        item = _attempt(order, attempt_id)
        check_choosable(item)
        old = order["chosen"]
        if old != attempt_id:
            order["chosenHistory"].append(old)
            order["chosen"] = attempt_id
        return {"old": old, "new": attempt_id}

    return _modify(project, key, profile, change)


def undo(project: str, key: str, profile: str) -> dict:
    """Pop the last chosen from the history (may be ``None``); returns ``{"old", "new"}``.

    Errors with ``order.history_empty`` if there is nothing to undo."""
    def change(order):
        if not order["chosenHistory"]:
            raise GimgError("order.history_empty", order=order["key"], profile=order["profile"])
        old = order["chosen"]
        target = order["chosenHistory"][-1]
        if target is not None and _attempt(order, target)["state"] == "discarded":
            raise GimgError("order.undo_discarded", attempt=target)
        order["chosenHistory"].pop()
        order["chosen"] = target
        return {"old": old, "new": order["chosen"]}

    return _modify(project, key, profile, change)


def get(project: str, key: str, profile: str) -> dict:
    """The order record (a fresh copy); ``order.unknown`` if it does not exist."""
    projects.get(project)
    return _read(project, key, profile)


def list_orders(project: str, profile: str | None = None, chosen: bool | None = None) -> list:
    """Orders of a project sorted by (key, profile). `chosen` True/False keeps only orders with/without
    a chosen attempt; `profile` keeps one profile."""
    projects.get(project)
    base = paths.project_data_dir(project) / "orders"
    found = []
    for folder, _dirs, files in os.walk(base):
        if _ORDER_FILE not in files or not os.path.basename(folder).startswith("@"):
            continue
        file = Path(folder) / _ORDER_FILE
        try:
            record = _shape(fsutil.read_json(file), file)
        except (OSError, ValueError):
            raise GimgError("order.corrupt", path=str(file))
        if profile is not None and record["profile"] != profile:
            continue
        if chosen is not None and (record["chosen"] is not None) != chosen:
            continue
        found.append(record)
    return sorted(found, key=lambda r: (r["key"], r["profile"]))
