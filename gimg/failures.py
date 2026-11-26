"""Failures and troubleshooting of brand orders (0.8.0, step 3; `docs/plan/fm.md`, `docs/interfaz/marca.md` 2.5).

Only brand orders (``mode: brand``) count failures; free ones never do, and neither does a technical failure of the engine
or a cancellation. ``order.json`` carries, written by the generator (a client cannot set them):

- ``failures``: ``{count, limit, reasons}``. A failed batch adds one (`fail_batch` = "Ninguno vale"; `orders.mark` when the
  person discards every attempt of a batch; `orders.add_failure` is the hook for the failure by score of 0.9.0).
  An attempt scoring `orders.RESET_SCORE` or more (`reset_on_score`), a new subject (`orders.apply_changes`) or a
  troubleshooting row (`add_row`) put it back to zero. An old order without the key has no failures.
- ``troubleshooting``: ``{rows, extendPending, extendUsed, extensions}``. The rows are data (``{piece, key, problem, attempts, redesign,
  terms, at, by}`` plus ``profile``); `list_rows` gathers those of a project and writes the Markdown (`markdown_path`).

An order is **blocked** when ``count >= limit`` (3 unless ``brand.failureLimit`` says otherwise) and it is still brand:
`check_open` and `admit` refuse a new batch (``order.troubleshooting``) and its queued entries are *held*
(`held_entry`; the worker never starts them, see `queue._first_queued`). A row, a subject change, a good score or switching
the order to free end the block. `extend` allows one batch more while blocked; its entries carry ``extended`` and are not held, and the
extension is noted (``extensions``). Only one extension per failure cycle (``extendUsed``; a cycle ends when the counter
goes to zero).

`view` is the order as the API and the CLI show it: ``failures`` with its defaults and ``troubleshooting`` as
``{state: open|blocked|extended, row?}`` (the stored rows stay in the file).
"""
from __future__ import annotations

import copy
import re

from . import i18n, orders, paths, projects
from .errors import GimgError, PathError

_ROW_FIELDS = ("key", "profile", "problem", "attempts", "redesign", "terms", "by")
_MAX_TERMS = 30


def _failures(order: dict) -> dict:
    stored = order.get("failures") if isinstance(order.get("failures"), dict) else {}
    return {"count": stored.get("count", 0), "limit": stored.get("limit", orders.FAILURE_LIMIT),
            "reasons": list(stored.get("reasons", []))}


def is_blocked(order: dict) -> bool:
    """A brand order whose counter reached its limit."""
    record = _failures(order)
    return order.get("mode") == "brand" and record["count"] >= record["limit"]


def _stored(order: dict) -> dict:
    stored = order.get("troubleshooting")
    return stored if isinstance(stored, dict) else {}


def state_of(order: dict) -> str:
    """``open``, ``blocked`` or ``extended`` (blocked, with one more batch allowed and not yet used)."""
    if not is_blocked(order):
        return "open"
    return "extended" if _stored(order).get("extendPending") else "blocked"


def view(order: dict) -> dict:
    """The order with ``failures`` filled in and ``troubleshooting`` as ``{state, row?}`` (a copy)."""
    out = dict(order)
    out["failures"] = _failures(order)
    out["troubleshooting"] = _state_view(order)
    return out


def _state_view(order: dict) -> dict:
    rows = _stored(order).get("rows") or []
    got = {"state": state_of(order)}
    if _stored(order).get("extendUsed"):
        got["extensionUsed"] = True
    if rows:
        got["row"] = copy.deepcopy(rows[-1])
    return got


def _blocked_error(order: dict) -> GimgError:
    record = _failures(order)
    return GimgError("order.troubleshooting", order=order["key"], profile=order["profile"], count=record["count"],
                     limit=record["limit"])


def check_open(project: str, key: str, profile: str) -> None:
    """``order.troubleshooting`` if the order is blocked and has no extension to use; an order that does not exist is open."""
    order = orders.peek(project, key, profile)
    if order is not None and is_blocked(order) and not _stored(order).get("extendPending"):
        raise _blocked_error(order)


def admit(project: str, key: str, profile: str) -> bool:
    """A new batch is going to be queued: ``False`` if the order is open; ``True`` if it is blocked and uses its pending
    extension (consumed here); ``order.troubleshooting`` if blocked without one."""
    order = orders.peek(project, key, profile)
    if order is None or not is_blocked(order):
        return False

    def change(current):
        if not is_blocked(current):
            return False
        stored = current.setdefault("troubleshooting", {})
        if not stored.get("extendPending"):
            raise _blocked_error(current)
        stored["extendPending"] = False
        return True

    return orders._modify(project, key, profile, change)


def restore_extension(project: str, key: str, profile: str) -> None:
    """`admit` consumed the extension but what came after failed (best effort): it is pending again."""
    def change(order):
        if is_blocked(order):
            _stored(order)["extendPending"] = True

    try:
        orders._modify(project, key, profile, change)
    except (GimgError, OSError):
        pass


def note_extension(project: str, key: str, profile: str, batch_id: int) -> None:
    """The batch `batch_id` is the one an extension allowed: noted in the extension."""
    def change(order):
        extensions = _stored(order).get("extensions")
        if extensions:
            extensions[-1]["batch"] = batch_id

    orders._modify(project, key, profile, change)


def held_entry(entry: dict):
    """``"troubleshooting"`` if the queued `entry` belongs to a blocked brand order (and is not the extension's), else ``None``."""
    if entry.get("state") != "queued" or entry.get("mode") != "brand" or entry.get("extended") is True:
        return None
    order = orders.peek(entry["project"], entry["key"], entry["profile"])
    return "troubleshooting" if order is not None and is_blocked(order) else None


def fail_batch(project: str, key: str, profile: str, batch_id, reason) -> dict:
    """"Ninguno vale": the batch failed. Discards its attempts, marks the batch ``failed`` with the `reason` (``{trait, text?}``,
    ``order.reason_invalid``) and counts one failure. Returns ``{failures, troubleshooting}``. Errors: ``order.not_brand``,
    ``order.batch_unknown``, ``order.batch_failed`` (already counted), ``order.discard_chosen``."""
    reason = orders.check_reason(project, reason, required=True)

    def change(order):
        if order.get("mode") != "brand":
            raise GimgError("order.not_brand", order=key, profile=profile)
        found = [b for b in order.get("batches", ()) if type(batch_id) is int and b["id"] == batch_id]
        if not found:
            raise GimgError("order.batch_unknown", id=str(batch_id), order=key, profile=profile)
        if found[0].get("failed"):
            raise GimgError("order.batch_failed", id=batch_id)
        mine = [a for a in order["attempts"] if a.get("batch") == batch_id]
        if any(a["id"] == order["chosen"] for a in mine):
            raise GimgError("order.discard_chosen", attempt=order["chosen"])
        for item in mine:
            item["state"] = "discarded"
        found[0].update(failed=True, reason=dict(reason))
        orders.add_failure(order, project, batch=batch_id, reason=reason)
        return {"failures": _failures(order), "troubleshooting": _state_view(order)}

    return orders._modify(project, key, profile, change)


def reset_on_score(project: str, key: str, profile: str, score) -> bool:
    """A finished attempt with `score` (``{"value": n}``) of `orders.RESET_SCORE` or more puts the counter to zero.
    Returns whether it did (best effort for the worker: the caller ignores errors)."""
    value = (score or {}).get("value") if isinstance(score, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < orders.RESET_SCORE:
        return False
    order = orders.peek(project, key, profile)
    if order is None or not order.get("failures", {}).get("count"):
        return False
    orders._modify(project, key, profile, orders.reset_failures)
    return True


def extend(project: str, key: str, profile: str) -> dict:
    """"Una tanda más" for a blocked order, noted in ``troubleshooting.extensions``. Returns ``{failures, troubleshooting}``.
    Only one per failure cycle (``extendUsed``, cleared when the counter goes to zero: row, good score, new subject).
    Errors: ``order.not_blocked`` (the order is not blocked), ``order.extend_pending`` (one is already waiting to be used),
    ``order.extend_used`` (the cycle already used its extension)."""
    def change(order):
        if not is_blocked(order):
            raise GimgError("order.not_blocked", order=key, profile=profile)
        stored = order.setdefault("troubleshooting", {})
        if stored.get("extendPending"):
            raise GimgError("order.extend_pending", order=key, profile=profile)
        if stored.get("extendUsed"):
            raise GimgError("order.extend_used", order=key, profile=profile)
        stored["extendPending"] = True
        stored["extendUsed"] = True
        stored.setdefault("extensions", []).append({"at": orders._now()})
        return {"failures": _failures(order), "troubleshooting": _state_view(order)}

    return orders._modify(project, key, profile, change)


def _row_text(body: dict, name: str, required: bool, maximum: int):
    value = body.get(name)
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > maximum:
        raise GimgError("api.bad_param", name=name)
    return value


def _row(project: str, body, order: dict) -> dict:
    """The row to store from a request `body`, checked against the `order` it belongs to."""
    if not isinstance(body, dict):
        raise GimgError("api.bad_param", name="body")
    for name in body:
        if name not in _ROW_FIELDS:
            raise GimgError("api.bad_param", name=name)
    problem = _row_text(body, "problem", True, 4000)
    redesign = _row_text(body, "redesign", False, 4000) or ""
    by = _row_text(body, "by", False, 80) or "person"
    attempts = body.get("attempts", [])
    if not isinstance(attempts, list) or any(type(a) is not int for a in attempts):
        raise GimgError("api.bad_param", name="attempts")
    known = {a["id"] for a in order["attempts"]}
    for number in attempts:
        if number not in known:
            raise GimgError("order.attempt_unknown", attempt=number, order=order["key"], profile=order["profile"])
    terms = body.get("terms", [])
    if (not isinstance(terms, list) or len(terms) > _MAX_TERMS
            or any(not isinstance(t, str) or not t.strip() or len(t) > 80 for t in terms)):
        raise GimgError("api.bad_param", name="terms")
    return {"piece": order.get("piece"), "key": order["key"], "profile": order["profile"], "problem": problem,
            "attempts": list(attempts), "redesign": redesign, "terms": [t.strip() for t in terms], "at": orders._now(),
            "by": by}


def add_row(project: str, body) -> dict:
    """``POST /api/projects/{p}/troubleshooting``: store a troubleshooting row in its order (``body``: ``key``, ``profile``,
    ``problem``, and optionally ``attempts``, ``redesign``, ``terms``, ``by``); the order's counter goes to zero and what it
    held is released. Returns the row. The Markdown is generated again (`write_markdown`)."""
    projects.get(project)
    if not isinstance(body, dict):
        raise GimgError("api.bad_param", name="body")
    key, profile = body.get("key"), body.get("profile")
    if not isinstance(key, str):
        raise GimgError("api.bad_param", name="key")
    if not isinstance(profile, str):
        raise GimgError("api.bad_param", name="profile")

    def change(order):
        if order.get("mode") != "brand":
            raise GimgError("order.not_brand", order=key, profile=profile)
        row = _row(project, body, order)
        stored = order.setdefault("troubleshooting", {})
        stored.setdefault("rows", []).append(row)
        stored["extendPending"] = False
        orders.reset_failures(order)
        return copy.deepcopy(row)

    row = orders._modify(project, key, profile, change)
    write_markdown(project)
    return row


def list_rows(project: str) -> list:
    """The rows of every order of the project, oldest first."""
    rows = []
    for order in orders.list_orders(project, skip_corrupt=True):
        rows += copy.deepcopy(_stored(order).get("rows") or [])
    return sorted(rows, key=lambda r: (r.get("at", ""), r.get("key", ""), r.get("profile", "")))


def _word(term: str, text: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.IGNORECASE) is not None


def known_terms(project: str, subject: str) -> list:
    """``[{term, row}]``: the terms of the project's rows that appear (whole word, any case) in `subject`."""
    found, seen = [], set()
    for row in list_rows(project):
        for term in row.get("terms", ()):
            if term.lower() not in seen and _word(term, subject):
                seen.add(term.lower())
                found.append({"term": term, "row": row})
    return found


def markdown_path(project: str):
    """Where the generated Markdown goes: ``brand.troubleshootingMarkdown`` of the project config (inside its root), else
    ``troubleshooting.md`` in the project's data folder."""
    proj = projects.get(project)
    rel = (proj["config"].get("brand") or {}).get("troubleshootingMarkdown")
    if rel:
        return paths.inside(proj["root"], rel)
    return paths.project_data_dir(project) / "troubleshooting.md"


def markdown(project: str, lang: str | None = None) -> str:
    t = lambda key, **kw: i18n.t("troubleshooting.md." + key, lang, **kw)  # noqa: E731
    lines = ["# " + t("title", project=project), "", t("generated"), ""]
    rows = list_rows(project)
    if not rows:
        lines.append(t("none"))
    for row in rows:
        lines += ["## %s (%s) · %s" % (row["key"], row["profile"], row["at"]), "",
                  "- **%s:** %s" % (t("problem"), row["problem"]),
                  "- **%s:** %s" % (t("attempts"), ", ".join(str(a) for a in row["attempts"]) or "-"),
                  "- **%s:** %s" % (t("redesign"), row["redesign"] or "-"),
                  "- **%s:** %s" % (t("terms"), ", ".join("`%s`" % x for x in row["terms"]) or "-"),
                  "- **%s:** %s" % (t("by"), row["by"]), ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def write_markdown(project: str, lang: str | None = None):
    """Write `markdown` to `markdown_path`; a file that cannot be written is not a failure of the row (best effort)."""
    from . import fsutil
    path = markdown_path(project)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fsutil.write_bytes_atomic(path, markdown(project, lang).encode("utf-8"))
    except (OSError, GimgError, PathError):  # best effort: another order's corrupt file or a bad path is not the row's failure
        return None
    return path
