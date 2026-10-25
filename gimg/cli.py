"""Command line front end (`python3 -m gimg`): a thin layer over the core modules."""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback

from . import __version__, delivery, i18n, orders, projects, queue, worker
from .errors import GimgError

LANGS = ("es", "en")


def _prescan_lang(argv) -> str:
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument("--lang", choices=LANGS)
    found, _rest = probe.parse_known_args(argv)
    return found.lang or i18n.default_lang()


def _build(lang: str) -> argparse.ArgumentParser:
    def t(key, **params):
        return i18n.t(key, lang, **params)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", choices=LANGS, default=argparse.SUPPRESS, help=t("cli.help.lang"))
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=t("cli.help.json"))

    parser = argparse.ArgumentParser(prog="gimg", description=t("cli.description"), parents=[common])
    top = parser.add_subparsers(dest="cmd", metavar="<command>", required=True)

    def leaf(group, name, help_key, *args):
        p = group.add_parser(name, help=t(help_key), description=t(help_key), parents=[common])
        for flags, kwargs in args:
            kwargs = dict(kwargs)
            if "help" in kwargs:
                kwargs["help"] = t(kwargs["help"])
            p.add_argument(*flags, **kwargs)
        return p

    def group(parent, name, help_key):
        p = parent.add_parser(name, help=t(help_key), description=t(help_key), parents=[common])
        return p.add_subparsers(dest="sub", metavar="<command>", required=True)

    def arg(name, help_key, **kw):
        return ((name,), dict(help=help_key, **kw))

    def opt(name, help_key, **kw):
        return ((name,), dict(help=help_key, **kw))

    project = arg("project", "cli.arg.project")
    okey, oprofile = arg("key", "cli.arg.key"), arg("profile", "cli.arg.profile")
    attempt = arg("attempt", "cli.arg.attempt", type=int)

    g = group(top, "project", "cli.cmd.project")
    leaf(g, "add", "cli.cmd.project_add", arg("path", "cli.arg.path"))
    leaf(g, "remove", "cli.cmd.project_remove", project)
    leaf(g, "list", "cli.cmd.project_list")

    g = group(top, "order", "cli.cmd.order")
    leaf(g, "submit", "cli.cmd.order_submit", project, arg("file", "cli.arg.file"))
    lst = leaf(g, "list", "cli.cmd.order_list", project,
               opt("--profile", "cli.arg.profile_filter"))
    mutex = lst.add_mutually_exclusive_group()
    mutex.add_argument("--chosen", action="store_true", help=t("cli.arg.chosen"))
    mutex.add_argument("--unchosen", action="store_true", help=t("cli.arg.unchosen"))
    leaf(g, "show", "cli.cmd.order_show", project, okey, oprofile)

    g = group(top, "attempt", "cli.cmd.attempt")
    leaf(g, "new", "cli.cmd.attempt_new", project, okey, oprofile,
         opt("--seed", "cli.arg.seed", type=int), opt("--count", "cli.arg.count", type=int, default=1),
         opt("--prompt", "cli.arg.prompt"), opt("--steps", "cli.arg.steps", type=int),
         opt("--cfg", "cli.arg.cfg", type=float), opt("--sampler", "cli.arg.sampler"))
    leaf(g, "mark", "cli.cmd.attempt_mark", project, okey, oprofile, attempt,
         arg("state", "cli.arg.state", choices=orders.STATES))
    leaf(g, "note", "cli.cmd.attempt_note", project, okey, oprofile, attempt,
         arg("text", "cli.arg.text"))

    leaf(top, "choose", "cli.cmd.choose", project, okey, oprofile, attempt)
    leaf(top, "undo", "cli.cmd.undo", project, okey, oprofile)

    g = group(top, "queue", "cli.cmd.queue")
    leaf(g, "list", "cli.cmd.queue_list", opt("--state", "cli.arg.queue_state", choices=queue.STATES))
    leaf(g, "cancel", "cli.cmd.queue_cancel", arg("entry", "cli.arg.entry", type=int))

    leaf(top, "work", "cli.cmd.work", opt("--once", "cli.arg.once", action="store_true"))
    leaf(top, "version", "cli.cmd.version")
    return parser


class _Out:
    def __init__(self, lang: str, as_json: bool):
        self.lang, self.as_json = lang, as_json

    def t(self, key, **params):
        return i18n.t(key, self.lang, **params)

    def data(self, value) -> None:
        print(json.dumps(value, ensure_ascii=False, indent=2))

    def line(self, key, **params) -> None:
        print(self.t(key, **params))

    def none(self, value):
        return self.t("cli.out.none") if value is None else value


def _entry_json(out: _Out, entry: dict) -> dict:
    item = dict(entry)
    text = queue.error_text(entry, out.lang)
    if text:
        item["errorText"] = text
    return item


def _queued(out: _Out, entries: list) -> None:
    estimate = queue.estimate_for(entries[0]) if entries else None
    if out.as_json:
        out.data({"entries": [_entry_json(out, e) for e in entries], "estimateMs": estimate})
        return
    out.line("cli.out.queued", count=len(entries), ids=", ".join(str(e["id"]) for e in entries))
    if estimate is None:
        out.line("cli.out.no_estimate")
    else:
        out.line("cli.out.estimate", seconds=round(estimate / 1000, 1))


def _read_order(source: str) -> dict:
    try:
        if source == "-":
            text = sys.stdin.read()
        else:
            with open(source, encoding="utf-8") as fh:
                text = fh.read()
        return json.loads(text)
    except (OSError, ValueError) as exc:  # includes UnicodeDecodeError
        raise GimgError("cli.order_unreadable", path=source, reason=str(exc))


def _run(args, out: _Out) -> int:
    cmd, sub = args.cmd, getattr(args, "sub", None)
    if cmd == "version":
        print(__version__)
    elif cmd == "project":
        if sub == "add":
            name = projects.add(args.path)
            out.data({"name": name}) if out.as_json else out.line("cli.out.project_added", name=name)
        elif sub == "remove":
            projects.remove(args.project)
            out.data({"removed": args.project}) if out.as_json else out.line(
                "cli.out.project_removed", name=args.project)
        else:
            found = projects.list_projects()
            if out.as_json:
                out.data([{"name": n, "root": v["root"]} for n, v in found.items()])
            elif not found:
                out.line("cli.out.project_none")
            for n, v in found.items():
                if not out.as_json:
                    out.line("cli.out.project_line", name=n, root=v["root"])
    elif cmd == "order":
        _order(args, sub, out)
    elif cmd == "attempt":
        _attempt(args, sub, out)
    elif cmd in ("choose", "undo"):
        if cmd == "choose":
            result = delivery.choose(args.project, args.key, args.profile, args.attempt)
        else:
            result = delivery.undo(args.project, args.key, args.profile)
        if out.as_json:
            out.data(result)
        else:
            out.line("cli.out.chosen" if cmd == "choose" else "cli.out.undone",
                     new=out.none(result["new"]), old=out.none(result["old"]))
    elif cmd == "queue":
        _queue(args, sub, out)
    elif cmd == "work":
        handled = worker.run(once=args.once)
        out.data({"processed": handled}) if out.as_json else out.line("cli.out.processed", count=handled)
    return 0


def _order(args, sub, out: _Out) -> None:
    if sub == "submit":
        order = _read_order(args.file)
        record = orders.submit(args.project, order)
        count = order.get("count", 1)
        specs = orders.attempt_specs(args.project, record["key"], record["profile"], count)
        entries = queue.enqueue(args.project, record["key"], record["profile"], specs)
        _queued(out, entries)
    elif sub == "list":
        chosen = True if args.chosen else False if args.unchosen else None
        found = orders.list_orders(args.project, args.profile, chosen)
        if out.as_json:
            out.data(found)
        elif not found:
            out.line("cli.out.order_none")
        else:
            for o in found:
                out.line("cli.out.order_line", order=o["key"], profile=o["profile"],
                         chosen=out.none(o["chosen"]), attempts=len(o["attempts"]))
    else:
        o = orders.get(args.project, args.key, args.profile)
        if out.as_json:
            out.data(o)
            return
        out.line("cli.out.order_head", order=o["key"], profile=o["profile"])
        out.line("cli.out.order_prompt", prompt=o["prompt"])
        out.line("cli.out.order_seed", seed=out.none(o["seed"]))
        out.line("cli.out.order_refs", references=", ".join(o["references"]) or out.t("cli.out.none"))
        out.line("cli.out.order_chosen", chosen=out.none(o["chosen"]))
        if not o["attempts"]:
            out.line("cli.out.attempts_none")
        for a in o["attempts"]:
            out.line("cli.out.attempt_line", id=a["id"], state=a["state"], seed=a["seed"], image=a["image"])
            if a.get("note"):
                out.line("cli.out.attempt_note", note=a["note"])


def _attempt(args, sub, out: _Out) -> None:
    if sub == "new":
        overrides = {k: v for k, v in (("steps", args.steps), ("cfg", args.cfg),
                                       ("sampler", args.sampler)) if v is not None}
        specs = orders.attempt_specs(args.project, args.key, args.profile, args.count,
                                     seed=args.seed, prompt=args.prompt, params=overrides)
        _queued(out, queue.enqueue(args.project, args.key, args.profile, specs))
    elif sub == "mark":
        item = orders.mark(args.project, args.key, args.profile, args.attempt, args.state)
        out.data(item) if out.as_json else out.line("cli.out.marked", id=item["id"], state=item["state"])
    else:
        item = orders.note(args.project, args.key, args.profile, args.attempt, args.text)
        out.data(item) if out.as_json else out.line("cli.out.noted", id=item["id"])


def _queue(args, sub, out: _Out) -> None:
    if sub == "list":
        entries = queue.list_entries(None if args.state is None else [args.state])
        if out.as_json:
            out.data([_entry_json(out, e) for e in entries])
        elif not entries:
            out.line("cli.out.queue_none")
        for e in entries if not out.as_json else ():
            out.line("cli.out.queue_line", id=e["id"], state=e["state"], project=e["project"],
                     order=e["key"], profile=e["profile"], seed=e["seed"])
            text = queue.error_text(e, out.lang)
            if text:
                out.line("cli.out.queue_error", error=text)
    else:
        entry = queue.cancel(args.entry)
        if out.as_json:
            out.data(_entry_json(out, entry))
        elif entry["state"] == "running":
            out.line("cli.out.cancel_requested", id=entry["id"])
        else:
            out.line("cli.out.cancelled", id=entry["id"])


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    lang = _prescan_lang(argv)
    parser = _build(lang)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse: usage errors exit 2, --help exits 0
        return exc.code if isinstance(exc.code, int) else 2
    lang = getattr(args, "lang", None) or lang
    out = _Out(lang, getattr(args, "json", False))
    try:
        return _run(args, out)
    except GimgError as exc:
        print(exc.message(lang), file=sys.stderr)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        if os.environ.get("GIMG_DEBUG") == "1":
            traceback.print_exc()
        print(i18n.t("cli.unexpected", lang, message="%s: %s" % (type(exc).__name__, exc)),
              file=sys.stderr)
    return 1
