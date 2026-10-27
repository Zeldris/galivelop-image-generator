"""Delivery of the chosen attempt into the project and the manifest (D13, D21, D25).

Public API: `choose(project, key, profile, attempt_id)` and `undo(project, key, profile)`. They wrap
`orders.choose` / `orders.undo` (the CLI never calls those directly) and return their ``{"old", "new"}``.

Everything of a choose/undo runs under one lock per project (``<data>/projects/<name>/delivery.lock``, never inside
the delivered project). The target must not be inside ``.git``, the config, the manifest, nor the ``file`` of another
(key, profile) entry of the manifest (``delivery.target_taken``).

Order of work (nothing is changed until everything that can be checked is):
1. Prepare, without touching anything: target path (``inside(root, delivery.dir)``, then ``inside(<that>, template)``
   so ``../`` and links leaving the delivery folder are rejected), source image of the attempt (must be a file)
   and the manifest (must parse). References are not checked here: they only matter for generation (the worker).
2. Change the order (`orders.choose` / `orders.undo`).
3. Deliver: copy the image (temp file in the target folder + `os.replace`, umask honoured) and update the manifest
   under its lock (an existing file at the target is overwritten: the delivery folder belongs to the generator); or,
   when the new chosen is ``None``, delete the file (only if the manifest entry's ``file`` is the current target; if
   not, the file is left alone) and the manifest entry.
If step 3 fails the order change is reverted (a choose is undone with `orders.undo`; an undo is redone with
`orders.choose` of the old attempt) and the error is raised; the revert is best effort. If the delivered file had
already changed (the manifest write failed after the copy or the delete) the revert also restores it: the previous
chosen image is copied back (or the file removed when there was none); the manifest on disk is untouched because its
write is atomic. If the restore fails too, the original error is the one raised. A failed prepare leaves
the order untouched. Choosing the already chosen attempt delivers it again (repairs a lost file) and reverts nothing.
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from . import fsutil, orders, paths, projects
from .errors import GimgError

MANIFEST_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _target(root: Path, config: dict, key: str, profile: str) -> Path:
    base = paths.inside(root, config["delivery"]["dir"])
    name = config["delivery"]["template"].replace("{key}", key).replace("{profile}", profile)
    target = paths.inside(base, name)  # relative to the delivery folder, not the project
    projects._forbidden(root, "delivery.template", target.relative_to(root.resolve()).as_posix())
    reserved = {paths.inside(root, config["manifest"]), paths.inside(root, projects.CONFIG_FILE)}
    if target in reserved or target == base:
        raise GimgError("delivery.reserved", path=name)
    return target


def _manifest_path(root: Path, config: dict) -> Path:
    return paths.inside(root, config["manifest"])


def _read_manifest(path: Path) -> dict:
    try:
        data = fsutil.read_json(path, default={"version": MANIFEST_VERSION, "images": {}})
    except (OSError, ValueError):
        raise GimgError("delivery.manifest_corrupt", path=str(path))
    ok = (isinstance(data, dict) and data.get("version") == MANIFEST_VERSION
          and isinstance(data.get("images"), dict)
          and all(isinstance(v, dict) and all(isinstance(e, dict) for e in v.values())
                  for v in data["images"].values()))
    if not ok:
        raise GimgError("delivery.manifest_corrupt", path=str(path))
    return data


def _find(order: dict, attempt_id):
    for item in order["attempts"]:
        if type(attempt_id) is int and item["id"] == attempt_id:
            return item
    return None


def _prepare(project: dict, order: dict, attempt):
    """Validate everything delivering `attempt` (None: removing) needs; returns the plan."""
    root, config = Path(project["root"]), project["config"]
    key, profile = order["key"], order["profile"]
    plan = {"root": root, "config": config, "key": key, "profile": profile, "attempt": attempt,
            "target": _target(root, config, key, profile), "manifest": _manifest_path(root, config)}
    images = _read_manifest(plan["manifest"])["images"]
    rel = _relative(plan)
    for other_key, by_profile in images.items():
        for other_profile, entry in by_profile.items():
            if (other_key, other_profile) != (key, profile) and entry.get("file") == rel:
                raise GimgError("delivery.target_taken", path=rel, otherKey=other_key, otherProfile=other_profile)
    if attempt is not None:
        source = orders.attempt_image(project["name"], key, profile, attempt)
        if not source.is_file():
            raise GimgError("delivery.source_missing", attempt=attempt["id"], path=attempt["image"])
        plan["source"] = source
    return plan


def _copy(source: Path, target: Path) -> None:
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix="." + target.name + ".", suffix=".tmp")
    except OSError as exc:
        raise GimgError("delivery.write_failed", path=str(target), reason=str(exc))
    try:
        try:
            fsutil.honour_umask(fd)
            out = os.fdopen(fd, "wb")
        except BaseException:
            with contextlib.suppress(OSError):
                os.close(fd)
            raise
        with out, open(source, "rb") as src:
            shutil.copyfileobj(src, out)
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, target)
    except BaseException as exc:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        if isinstance(exc, OSError):
            raise GimgError("delivery.write_failed", path=str(target), reason=str(exc))
        raise


def _relative(plan: dict) -> str:
    return plan["target"].relative_to(plan["root"].resolve()).as_posix()


def _restore_source(project: dict, order: dict):
    """Image to put back if delivering fails: the current chosen's, None if there is none, False if unknown."""
    current = _find(order, order["chosen"]) if order["chosen"] is not None else None
    if current is None:
        return None
    try:
        return orders.attempt_image(project["name"], order["key"], order["profile"], current)
    except Exception:
        return False


def _rollback(plan: dict, restore) -> None:
    """Best effort: put the delivered file back as it was before `_apply`."""
    if restore is False:
        return
    with contextlib.suppress(Exception):
        if restore is None:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(plan["target"])
        else:
            _copy(restore, plan["target"])


def _apply(plan: dict, restore=False) -> None:
    attempt, key, profile = plan["attempt"], plan["key"], plan["profile"]
    manifest = plan["manifest"]  # callers hold the project delivery lock
    touched = False
    try:
        data = _read_manifest(manifest)
        images = data["images"]
        if attempt is None:
            entry = images.get(key, {}).get(profile)
            if entry is not None and entry.get("file") == _relative(plan):
                try:
                    os.unlink(plan["target"])
                    touched = True
                except FileNotFoundError:
                    pass
            images.get(key, {}).pop(profile, None)
            if key in images and not images[key]:
                del images[key]
        else:
            _copy(plan["source"], plan["target"])
            touched = True
            images.setdefault(key, {})[profile] = {
                "file": _relative(plan), "prompt": attempt["prompt"], "seed": attempt["seed"],
                "params": attempt["params"], "references": attempt.get("references", []),
                "engine": attempt.get("engine"), "engineVersion": attempt.get("engineVersion"),
                "attemptId": attempt["id"], "chosenAt": _now()}
        fsutil.write_json(manifest, data)
    except BaseException as exc:
        if touched:
            _rollback(plan, restore)
        if isinstance(exc, OSError):
            raise GimgError("delivery.write_failed", path=str(plan["target"]), reason=str(exc))
        raise


def _lock(project: str):
    """Delivery lock of a project: lives in the generator's data dir, never inside the delivered project."""
    return fsutil.lock(paths.project_data_dir(project) / "delivery")


def choose(project: str, key: str, profile: str, attempt_id) -> dict:
    """Choose an attempt and deliver it; returns ``{"old", "new"}`` as `orders.choose` does."""
    proj = projects.get(project)
    with _lock(project):  # read, decide, change the order, deliver and revert: one unit
        order = orders.get(project, key, profile)
        attempt = _find(order, attempt_id)
        # an unknown attempt (a discarded one, a draft) is reported by orders.choose itself
        ok = attempt is not None and attempt["state"] != "discarded" and attempt.get("draft") is not True
        plan = _prepare(proj, order, attempt) if ok else None
        restore = _restore_source(proj, order) if plan is not None else False
        result = orders.choose(project, key, profile, attempt_id)
        try:
            if plan is None:  # the attempt stopped being discarded after we looked (a mark outside the lock)
                raise GimgError("order.choose_discarded", attempt=attempt_id)
            _apply(plan, restore)
        except BaseException:
            if result["old"] != result["new"]:
                with contextlib.suppress(Exception):
                    orders.undo(project, key, profile)
            raise
        return result


def undo(project: str, key: str, profile: str) -> dict:
    """Undo the last choose and deliver (or remove) the restored one; returns ``{"old", "new"}``."""
    proj = projects.get(project)
    with _lock(project):
        order = orders.get(project, key, profile)
        if not order["chosenHistory"]:
            return orders.undo(project, key, profile)  # raises order.history_empty
        target_id = order["chosenHistory"][-1]
        attempt = _find(order, target_id) if target_id is not None else None
        plan = _prepare(proj, order, attempt) if target_id is None or attempt is not None else None
        restore = _restore_source(proj, order) if plan is not None else False
        result = orders.undo(project, key, profile)
        try:
            if plan is None:  # see choose
                raise GimgError("order.undo_discarded", attempt=target_id)
            _apply(plan, restore)
        except BaseException:
            if result["old"] is not None:
                with contextlib.suppress(Exception):
                    orders.choose(project, key, profile, result["old"])
            raise
        return result
