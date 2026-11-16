"""Crop an attempt into a derived attempt (`gimg crop`, point 9 of the plan, 0.6.0).

``crop(project, key, profile, attempt_id, box)`` takes `box` = ``[x0, y0, x1, y1]`` (integers, x1 and y1 exclusive, in pixels
of the **raw** image of the attempt: `orders.raw_image`, which is its ``image`` when it has no ``raw``) and stores the piece as
a new attempt, the **derived** one; the original attempt, its file and its record are never touched.

- **Size:** with `lock_ratio` (the default) the box must have the proportion of the destination profile (1 % of
  difference at most, ``crop.ratio_mismatch``) and the result is exactly its ``width`` x ``height``. Without it, the result has
  the size of the box and is not resampled.
- **Resampling:** `export.resize`: area average when reducing, bilinear when enlarging, on premultiplied alpha. The same box
  always gives the same image.
- **Destination:** `to` is ``None`` (the same order) or ``{"profile", "key"}`` (take the piece to another order, "Llevar a otro
  pedido"). A destination order that does not exist is created with `orders.submit` and the ``prompt`` of the source order; its
  profile must exist in the project (``order.profile_unknown``).
- **Record:** `orders.add_derived`: ``state`` ``new``, ``image`` ``attempts/<id>.png``, ``seed``, ``prompt``, ``params`` (with the
  new ``width`` and ``height``), ``references``, ``negative`` and ``draft`` of the source, and ``derivedFrom``
  ``{"profile", "key", "attempt", "box", "lockRatio"}``. It is chosen like any other attempt (a draft cannot be).

Errors (`GimgError`): ``crop.bad_box`` (not four integers, or no area), ``crop.outside`` (the box leaves the image),
``crop.ratio_mismatch``, ``crop.bad_target``, ``crop.write_failed``; and the ``order.*`` and ``png.invalid`` ones. Everything is
checked before anything is written; the image and the record are stored together (`orders.add_derived`).
"""
from __future__ import annotations

import copy

from . import export, orders, png, projects
from .errors import GimgError

RATIO_TOLERANCE = 0.01


def parse_box(text) -> list:
    """``"x0,y0,x1,y1"`` as a list of four integers (``crop.bad_box`` if it is not)."""
    try:
        return [int(v) for v in str(text).split(",")]
    except ValueError:
        raise GimgError("crop.bad_box", value=str(text)) from None


def _check_box(box) -> list:
    if (not isinstance(box, (list, tuple)) or len(box) != 4
            or not all(type(v) is int for v in box)):
        raise GimgError("crop.bad_box", value=str(box))
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        raise GimgError("crop.bad_box", value=",".join(str(v) for v in box))
    return [x0, y0, x1, y1]


def _target(to, source_key: str, source_profile: str) -> tuple:
    if to is None:
        return source_profile, source_key
    if (not isinstance(to, dict) or set(to) - {"profile", "key"}
            or not all(isinstance(to.get(k), str) and to.get(k) for k in ("profile", "key"))):
        raise GimgError("crop.bad_target", value=str(to))
    return to["profile"], to["key"]


def crop(project: str, key: str, profile: str, attempt_id: int, box, lock_ratio: bool = True, to=None) -> dict:
    """Crop `box` of attempt `attempt_id` of order (`key`, `profile`) into a derived attempt (see the module docstring).

    Returns ``{"attempt": <the derived record, a copy>, "profile", "key" (of the order that got it), "created": bool (a new order)}``."""
    box = _check_box(box)
    lock_ratio = bool(lock_ratio)
    source = orders.get(project, key, profile)
    attempt = next((a for a in source["attempts"] if type(attempt_id) is int and a["id"] == attempt_id), None)
    if attempt is None:
        raise GimgError("order.attempt_unknown", attempt=attempt_id, order=key, profile=profile)
    dest_profile, dest_key = _target(to, key, profile)
    config = projects.get(project)["config"]
    profile_cfg = orders._profile(config, dest_profile)  # order.profile_unknown, before anything else changes
    orders._check_id(dest_key, dest_profile)
    width, height, rgba = png.read_rgba(orders.raw_image(project, key, profile, attempt))
    x0, y0, x1, y1 = box
    if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
        raise GimgError("crop.outside", box=",".join(str(v) for v in box), width=width, height=height)
    box_w, box_h = x1 - x0, y1 - y0
    if lock_ratio:
        out_w, out_h = int(profile_cfg["width"]), int(profile_cfg["height"])
        if abs(box_w / box_h - out_w / out_h) > RATIO_TOLERANCE * out_w / out_h:
            raise GimgError("crop.ratio_mismatch", box=",".join(str(v) for v in box), box_ratio="%.3f" % (box_w / box_h),
                            profile=dest_profile, size="%dx%d" % (out_w, out_h), ratio="%.3f" % (out_w / out_h))
    else:
        out_w, out_h = box_w, box_h
    piece = export.crop_box(width, height, rgba, (x0, y0, box_w, box_h))
    pixels = export.resize(box_w, box_h, piece, out_w, out_h)
    data = png.rgba_bytes(out_w, out_h, pixels)

    created = False
    try:
        orders.get(project, dest_key, dest_profile)
    except GimgError as exc:
        if exc.code != "order.unknown":
            raise
        orders.submit(project, {"key": dest_key, "profile": dest_profile, "prompt": source["prompt"]})
        created = True
    params = copy.deepcopy(attempt["params"])
    params["width"], params["height"] = out_w, out_h
    spec = {"seed": attempt["seed"], "prompt": attempt["prompt"], "params": params,
            "references": list(attempt.get("references", source["references"])),
            "draft": attempt.get("draft") is True, "negative": attempt.get("negative")}
    derived_from = {"profile": profile, "key": key, "attempt": attempt["id"], "box": box, "lockRatio": lock_ratio}
    try:
        record = orders.add_derived(project, dest_key, dest_profile, spec, derived_from, data)
    except OSError as exc:
        raise GimgError("crop.write_failed", reason=str(exc.strerror or exc)) from None
    return {"attempt": record, "profile": dest_profile, "key": dest_key, "created": created}
