"""Command line front end (`python3 -m gimg`): a thin layer over the core modules."""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback

from . import __version__, brand, compose, delivery, doctor, i18n, measure, orders, projects, queue, service, sheet, worker
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
    leaf(g, "submit", "cli.cmd.order_submit", project, arg("file", "cli.arg.file"),
         opt("--draft", "cli.arg.draft", action=argparse.BooleanOptionalAction, default=None),
         opt("--template", "cli.arg.template", metavar="ID"),
         opt("--model", "cli.arg.model", metavar="ID"))
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
         opt("--cfg", "cli.arg.cfg", type=float), opt("--sampler", "cli.arg.sampler"),
         opt("--draft", "cli.arg.draft", action=argparse.BooleanOptionalAction, default=None),
         opt("--template", "cli.arg.template", metavar="ID"),
         opt("--model", "cli.arg.model", metavar="ID"))
    leaf(g, "mark", "cli.cmd.attempt_mark", project, okey, oprofile, attempt,
         arg("state", "cli.arg.state", choices=orders.STATES))
    leaf(g, "note", "cli.cmd.attempt_note", project, okey, oprofile, attempt,
         arg("text", "cli.arg.text"))

    leaf(top, "choose", "cli.cmd.choose", project, okey, oprofile, attempt)
    leaf(top, "undo", "cli.cmd.undo", project, okey, oprofile)
    leaf(top, "compose", "cli.cmd.compose", project, okey, oprofile,
         arg("attempt", "cli.arg.attempt_optional", type=int, nargs="?", default=None),
         opt("--text", "cli.arg.text_kv", action="append", default=[], metavar="FIELD=TEXT"),
         opt("--template", "cli.arg.template", metavar="ID"),
         opt("--layout", "cli.arg.layout", metavar="JSON"))
    leaf(top, "templates", "cli.cmd.templates", project, oprofile)
    g = group(top, "template", "cli.cmd.template")
    leaf(g, "save", "cli.cmd.template_save", project, oprofile, okey, attempt, arg("name", "cli.arg.template_name"),
         opt("--dest", "cli.arg.template_dest", choices=("local", "project"), default="local"))

    leaf(top, "measure", "cli.cmd.measure", arg("image", "cli.arg.image_path"),
         opt("--palette", "cli.arg.palette"), opt("--project", "cli.arg.measure_project", metavar="PROJECT"),
         opt("--refs", "cli.arg.refs", nargs="+", default=[], metavar="IMAGE"),
         opt("--zone", "cli.arg.zone", metavar="X,Y,W,H"), opt("--text", "cli.arg.text_color", metavar="#RRGGBB"))

    g = group(top, "brand", "cli.cmd.brand")
    leaf(g, "matte", "cli.cmd.brand_matte", arg("image", "cli.arg.brand_png"),
         opt("-o", "cli.arg.brand_out_matte", dest="out", metavar="PNG"),
         opt("--tol", "cli.arg.brand_tol", type=float, default=60),
         opt("--soft", "cli.arg.brand_soft", type=float, default=110),
         opt("--border", "cli.arg.brand_border", type=int, default=6),
         opt("--grow", "cli.arg.brand_grow", type=int, default=3),
         opt("--holes", "cli.arg.brand_holes", action="store_true"))
    leaf(g, "trace", "cli.cmd.brand_trace", arg("image", "cli.arg.brand_png"),
         opt("-o", "cli.arg.brand_out_svg", dest="out", metavar="SVG"),
         opt("--mode", "cli.arg.brand_mode", choices=tuple(brand.MODES), default="color"),
         opt("--palette", "cli.arg.brand_palette", metavar="#HEX,#HEX"),
         opt("--colors", "cli.arg.brand_colors", type=int, metavar="N"),
         opt("--dp-tol", "cli.arg.brand_dp_tol", type=float, default=1.2),
         opt("--min-island", "cli.arg.brand_min_island", type=float, default=12),
         opt("--matte", "cli.arg.brand_matte", action="store_true"))
    leaf(g, "wordmark", "cli.cmd.brand_wordmark", arg("text", "cli.arg.brand_text"),
         opt("--font", "cli.arg.brand_font", required=True, metavar="TTF"),
         opt("--weight", "cli.arg.brand_weight", type=int, default=800),
         opt("--spacing", "cli.arg.brand_spacing", type=float, default=0.12),
         opt("-o", "cli.arg.brand_out_svg", dest="out", metavar="SVG"))
    props = (opt("--cap", "cli.arg.brand_cap", type=float, default=0.45),
             opt("--gap", "cli.arg.brand_gap", type=float, default=0.25),
             opt("--width", "cli.arg.brand_width", type=float, default=1.6))
    leaf(g, "lockup", "cli.cmd.brand_lockup", arg("emblem", "cli.arg.brand_emblem_svg"),
         arg("wordmark", "cli.arg.brand_wordmark_svg"),
         opt("--layout", "cli.arg.brand_layout", choices=brand.LAYOUTS, default="h"),
         opt("--margin", "cli.arg.brand_margin", type=float, default=0.0),
         opt("--color", "cli.arg.brand_ink", metavar="COLOR"),
         opt("-o", "cli.arg.brand_out_svg", dest="out", metavar="SVG"), *props)
    leaf(g, "system", "cli.cmd.brand_system", arg("image", "cli.arg.brand_png"),
         opt("--name", "cli.arg.brand_name", required=True),
         opt("--font", "cli.arg.brand_font", required=True, metavar="TTF"),
         opt("--out-dir", "cli.arg.brand_out_dir", required=True, metavar="DIR"),
         opt("--weight", "cli.arg.brand_weight", type=int, default=800),
         opt("--spacing", "cli.arg.brand_spacing", type=float, default=0.12),
         opt("--palette", "cli.arg.brand_palette", metavar="#HEX,#HEX"),
         opt("--colors", "cli.arg.brand_colors", type=int, metavar="N"),
         opt("--text", "cli.arg.brand_wordmark_text"),
         opt("--holes", "cli.arg.brand_holes", action="store_true"),
         opt("--force", "cli.arg.brand_force", action="store_true"), *props)

    leaf(top, "sheet", "cli.cmd.sheet", arg("images", "cli.arg.sheet_images", nargs="*", metavar="IMAGE"),
         opt("--out", "cli.arg.sheet_out", required=True, metavar="PNG"),
         opt("--columns", "cli.arg.sheet_columns", type=int, default=sheet.DEFAULT_COLUMNS),
         opt("--width", "cli.arg.sheet_width", type=int, default=sheet.DEFAULT_WIDTH))

    g = group(top, "queue", "cli.cmd.queue")
    leaf(g, "list", "cli.cmd.queue_list", opt("--state", "cli.arg.queue_state", choices=queue.STATES))
    leaf(g, "cancel", "cli.cmd.queue_cancel", arg("entry", "cli.arg.entry", type=int))
    leaf(g, "move", "cli.cmd.queue_move", arg("entry", "cli.arg.entry", type=int),
         arg("to", "cli.arg.queue_to", choices=queue.MOVES))
    leaf(g, "clear", "cli.cmd.queue_clear", opt("--project", "cli.arg.queue_project", metavar="P"))

    leaf(top, "work", "cli.cmd.work", opt("--once", "cli.arg.once", action="store_true"))
    serve = leaf(top, "serve", "cli.cmd.serve", opt("--port", "cli.arg.serve_port", type=int),
                 opt("--idle-min", "cli.arg.serve_idle", type=int, metavar="N"))
    mode = serve.add_mutually_exclusive_group()
    mode.add_argument("--detach", action="store_true", help=t("cli.arg.serve_detach"))
    mode.add_argument("--status", action="store_true", help=t("cli.arg.serve_status"))
    mode.add_argument("--stop", action="store_true", help=t("cli.arg.serve_stop"))
    leaf(top, "ui", "cli.cmd.ui", opt("--no-browser", "cli.arg.no_browser", action="store_true"))
    leaf(top, "doctor", "cli.cmd.doctor", opt("--verify", "cli.arg.verify", action="store_true"))
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
    return queue.entry_view(entry, out.lang)


def _autostart(out: _Out) -> dict:
    """After an enqueue: make sure the service runs. The entries are queued already, so a failure here is a warning
    on stderr (exit code 0), and is reported in the ``service`` field of ``--json``."""
    if not service.autostart_enabled():
        return {"running": False, "autostart": False}

    def warn(text):
        print(text, file=sys.stderr)

    try:
        state = service.ensure_running(out.lang, warn)
    except KeyboardInterrupt:
        return {"running": False, "autostart": True, "error": "interrupted", "message": "interrupted"}
    except Exception as exc:  # noqa: BLE001 - the entries are queued: nothing here may turn into a failure
        message = exc.message(out.lang) if isinstance(exc, GimgError) else "%s: %s" % (type(exc).__name__, exc)
        warn(out.t("cli.warn.service_failed", error=message))
        return {"running": False, "autostart": True, "error": getattr(exc, "code", type(exc).__name__),
                "message": message}
    return {"running": True, "autostart": True, "url": state["url"], "pid": state["pid"]}


def _queued(out: _Out, entries: list, provider: str) -> None:
    if out.as_json:
        view = queue.queued_view(entries, provider, out.lang)
        out.data(dict(view, service=_autostart(out)))
        return
    estimate = queue.estimate_for(entries[0], provider) if entries else None
    out.line("cli.out.queued", count=len(entries), ids=", ".join(str(e["id"]) for e in entries))
    if estimate is None:
        out.line("cli.out.no_estimate")
    else:
        out.line("cli.out.estimate", seconds=round(estimate / 1000, 1))
    sys.stdout.flush()
    _autostart(out)


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


def _doctor(args, out: _Out) -> int:
    checks = doctor.run(verify=args.verify)
    bad = doctor.failed(checks)
    if out.as_json:
        out.data({"ok": not bad, "checks": [c.as_dict(out.lang) for c in checks]})
        return 1 if bad else 0
    for c in checks:
        out.line("doctor.line", label=c.label(out.lang), message=c.message(out.lang))
        if c.fix_key:
            out.line("doctor.fix_line", fix=c.fix(out.lang))
    out.line("doctor.summary_fail" if bad else "doctor.summary_ok")
    return 1 if bad else 0


def _brand(args, sub, out: _Out) -> None:
    if sub == "matte":
        res = brand.matte(args.image, args.out, args.tol, args.soft, args.border, args.grow, args.holes)
        key = "cli.out.brand_matte"
    elif sub == "trace":
        res = brand.trace(args.image, args.out, args.mode, args.palette, args.colors, args.dp_tol, args.min_island,
                          args.matte)
        key = "cli.out.brand_trace"
    elif sub == "lockup":
        res = brand.lockup(args.emblem, args.wordmark, args.out, args.layout, args.cap, args.gap, args.width, args.margin,
                           args.color)
        key = "cli.out.brand_lockup"
    elif sub == "system":
        res = brand.system(args.image, args.name, args.font, args.out_dir, args.weight, args.spacing, args.palette,
                           args.colors, args.text, args.cap, args.gap, args.width, args.force, args.holes)
        if out.as_json:
            out.data(res)
            return
        out.line("cli.out.brand_system", slug=res["slug"], out_dir=res["out_dir"], count=len(res["files"]),
                 paths=sum(res["paths"].values()), seconds=res["seconds"])
        for path in res["files"].values():
            out.line("cli.out.brand_file", path=path)
        if res["overwritten"]:
            out.line("cli.out.brand_overwrote", files=", ".join(res["overwritten"]))
        return
    else:
        res = brand.wordmark(args.text, args.font, args.out, args.weight, args.spacing)
        key = "cli.out.brand_wordmark"
    if out.as_json:
        out.data(res)
        return
    out.line(key, **{**res, "width": res["size"][0], "height": res["size"][1]})
    if res.get("opaque_background"):
        out.line("cli.out.brand_opaque")


def _run(args, out: _Out) -> int:
    cmd, sub = args.cmd, getattr(args, "sub", None)
    if cmd == "version":
        print(__version__)
    elif cmd == "doctor":
        return _doctor(args, out)
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
    elif cmd == "compose":
        _compose(args, out)
    elif cmd == "templates":
        _templates(args, out)
    elif cmd == "template":
        _template_save(args, out)
    elif cmd == "measure":
        _measure(args, out)
    elif cmd == "brand":
        _brand(args, sub, out)
    elif cmd == "sheet":
        res = sheet.sheet(args.images, args.out, args.columns, args.width)
        if out.as_json:
            out.data(res)
        else:
            out.line("cli.out.sheet_done", out=res["out"], width=res["size"][0], height=res["size"][1],
                     columns=res["columns"], count=len(res["images"]))
            for i, path in enumerate(res["images"], 1):
                out.line("cli.out.sheet_item", index=i, path=path)
    elif cmd == "queue":
        _queue(args, sub, out)
    elif cmd == "serve":
        return _serve(args, out)
    elif cmd == "ui":
        return _ui(args, out)
    elif cmd == "work":
        handled = worker.run(once=args.once, lang=out.lang)
        out.data({"processed": handled}) if out.as_json else out.line("cli.out.processed", count=handled)
    return 0


def _serve(args, out: _Out) -> int:
    def show(state):
        if out.as_json:
            out.data(state)
        else:
            out.line("cli.out.serve_running", url=state["url"], pid=state["pid"])
        sys.stdout.flush()

    if args.status:
        state = service.status()
        if out.as_json:
            out.data({"running": state is not None, **(state or {})})
        elif state is None:
            out.line("cli.out.serve_stopped")
        else:
            out.line("cli.out.serve_status", url=state["url"], pid=state["pid"], since=state["startedAt"])
        return 0 if state else 1
    if args.stop:
        state = service.stop()
        out.data(state) if out.as_json else out.line("cli.out.serve_stopping", pid=state["pid"])
        return 0
    if args.detach:
        show(service.detach(args.port, args.idle_min, out.lang))
        return 0
    idle_s = None if args.idle_min is None else service.resolve_idle_s(args.idle_min)
    service.run(args.port, idle_s, out.lang, announce=show)
    return 0


def _open_browser(url: str) -> bool:
    """Open `url` in the browser with stdout/stderr on /dev/null (the browser must not keep our pipes); never
    raises. Without a display nothing is opened: the URL is printed anyway."""
    if sys.platform.startswith("linux") and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    import webbrowser
    sys.stdout.flush()
    sys.stderr.flush()
    saved = []
    try:
        null = os.open(os.devnull, os.O_RDWR)
        try:
            for fd in (1, 2):
                saved.append((fd, os.dup(fd)))
                os.dup2(null, fd)
            return bool(webbrowser.open(url))
        finally:
            for fd, old in saved:
                os.dup2(old, fd)
                os.close(old)
            os.close(null)
    except Exception:  # noqa: BLE001
        return False


def _ui(args, out: _Out) -> int:
    if service.autostart_enabled():
        state = service.ensure_running(out.lang, lambda text: print(text, file=sys.stderr))
    else:
        state = service.status()
        if state is None:
            raise GimgError("serve.not_running")
    opened = False
    if not args.no_browser:
        opened = _open_browser(state["url"])
    if out.as_json:
        out.data(dict(state, opened=opened))
    else:
        out.line("cli.out.ui_url", url=state["url"])
    return 0


def _text_pairs(pairs) -> dict:
    """``["title=Hi", ...]`` as ``{"title": "Hi"}``: split at the first ``=``; a later pair replaces an earlier one."""
    text = {}
    for pair in pairs:
        field, sep, value = pair.partition("=")
        if not sep or not field:
            raise GimgError("cli.text_invalid", value=pair)
        text[field] = value
    return text


def _compose(args, out: _Out) -> None:
    text = _text_pairs(args.text)
    layout = None
    if args.layout is not None:
        try:
            layout = json.loads(args.layout)
        except ValueError as exc:
            raise GimgError("compose.bad_layout", element="", reason=str(exc)[:100])
    item = compose.recompose(args.project, args.key, args.profile, args.attempt, text or None, args.template, layout)
    if out.as_json:
        out.data(item)
    elif "delivered" in item:
        out.line("cli.out.composed_delivered", id=item["id"], path=item["delivered"])
    else:
        out.line("cli.out.composed", id=item["id"], image=item["image"])


def _template_save(args, out: _Out) -> None:
    item = compose.save_template(args.project, args.key, args.profile, args.attempt, args.name, args.dest)
    if out.as_json:
        out.data(item)
    else:
        out.line("cli.out.template_saved", id=item["id"], source=item["source"], template=item["template"])


def _templates(args, out: _Out) -> None:
    proj = projects.get(args.project)
    if proj["config"]["profiles"].get(args.profile) is None:
        raise GimgError("order.profile_unknown", profile=args.profile)
    items = compose.templates_with_elements(proj, args.profile)
    if out.as_json:
        out.data(items)
        return
    if not items:
        out.line("cli.out.templates_none", profile=args.profile)
    for item in items:
        out.line("cli.out.template_line", id=item["id"], template=item["template"], logo=out.none(item["logo"]),
                 fields=", ".join(item["fields"]) or out.t("cli.out.none"),
                 default=out.t("cli.out.template_default") if item["default"] else "")


def _measure(args, out: _Out) -> None:
    palette = args.palette.split(",") if args.palette else None
    if palette is None and args.project:
        brand = projects.get(args.project)["config"].get("brand")
        if not brand or not brand.get("palette"):
            raise GimgError("measure.no_brand_palette", name=args.project)
        palette = brand["palette"]
    res = measure.measure(args.image, palette, args.refs, args.zone, args.text)
    if out.as_json:
        out.data(res)
        return
    out.line("cli.out.measure_head", image=res["image"])
    out.line("cli.out.measure_luma", yavg=res["yavg"], satavg=res["satavg"])
    if "palette" in res:
        p = res["palette"]
        out.line("cli.out.measure_palette", pct=p["pct"], delta=p["deltaE"], count=len(p["colors"]))
        for color, pct in p["by_color"].items():
            out.line("cli.out.measure_palette_color", color=color, pct=pct)
    for e in res.get("emd", ()):
        out.line("cli.out.measure_emd", **e)
    if "emd_median" in res:
        out.line("cli.out.measure_emd_median", **res["emd_median"])
    if "contrast" in res:
        c = res["contrast"]
        out.line("cli.out.measure_contrast", text=c["text"], zone=",".join(str(v) for v in c["zone"]),
                 mean=c["mean"], p10=c["p10"], p90=c["p90"], worst=c["worst"])


def _order(args, sub, out: _Out) -> None:
    if sub == "submit":
        order = _read_order(args.file)
        entries, provider = queue.submit_order(args.project, order, args.draft, template=args.template, model=args.model)
        _queued(out, entries, provider)
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
        if o.get("initImage") is not None:
            out.line("cli.out.order_init" if o.get("strength") is not None else "cli.out.order_init_nostrength",
                     path=o["initImage"], strength=o.get("strength"))
        out.line("cli.out.order_chosen", chosen=out.none(o["chosen"]))
        if o.get("text"):
            for field, value in o["text"].items():
                out.line("cli.out.order_text", field=field, value=value)
        if not o["attempts"]:
            out.line("cli.out.attempts_none")
        for a in o["attempts"]:
            out.line("cli.out.attempt_line", id=a["id"], state=a["state"], seed=a["seed"], image=a["image"],
                     draft=out.t("cli.out.draft_mark") if a.get("draft") else "")
            if a.get("composeError"):
                out.line("cli.out.compose_error_mark", error=queue.error_text(a["composeError"], out.lang))
            if a.get("note"):
                out.line("cli.out.attempt_note", note=a["note"])


def _attempt(args, sub, out: _Out) -> None:
    if sub == "new":
        overrides = {k: v for k, v in (("steps", args.steps), ("cfg", args.cfg),
                                       ("sampler", args.sampler)) if v is not None}
        entries, provider = queue.new_attempts(args.project, args.key, args.profile, args.count,
                                               seed=args.seed, prompt=args.prompt, params=overrides,
                                               draft=args.draft, template=args.template, model=args.model)
        _queued(out, entries, provider)
    elif sub == "mark":
        item = orders.mark(args.project, args.key, args.profile, args.attempt, args.state)
        out.data(item) if out.as_json else out.line("cli.out.marked", id=item["id"], state=item["state"])
    else:
        item = orders.note(args.project, args.key, args.profile, args.attempt, args.text)
        out.data(item) if out.as_json else out.line("cli.out.noted", id=item["id"])


def _eta_text(seconds) -> str:
    """``1:16`` or, from an hour, ``1:02:03``."""
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    return ("%d:%02d:%02d" % (hours, rest // 60, rest % 60)) if hours else "%d:%02d" % (rest // 60, rest % 60)


def _queue_running_lines(out: _Out, entry: dict) -> None:
    """The progress of a running entry and, if the engine has written it, where its preview image is."""
    progress = entry.get("progress")
    if isinstance(progress, dict) and isinstance(progress.get("step"), int) and isinstance(progress.get("steps"), int):
        eta = progress.get("etaS")
        if isinstance(eta, (int, float)) and not isinstance(eta, bool) and eta >= 0:
            out.line("cli.out.queue_progress_eta", step=progress["step"], steps=progress["steps"], eta=_eta_text(eta))
        else:
            out.line("cli.out.queue_progress", step=progress["step"], steps=progress["steps"])
    preview = entry.get("preview")
    if isinstance(preview, str) and os.path.isfile(preview):
        out.line("cli.out.queue_preview", path=preview)


def _queue(args, sub, out: _Out) -> None:
    if sub == "list":
        entries = queue.list_entries(None if args.state is None else [args.state])
        if out.as_json:
            out.data([_entry_json(out, e) for e in entries])
        elif not entries:
            out.line("cli.out.queue_none")
        for e in entries if not out.as_json else ():
            out.line("cli.out.queue_line", id=e["id"], state=e["state"], project=e["project"],
                     order=e["key"], profile=e["profile"], seed=e["seed"],
                     draft=out.t("cli.out.draft_mark") if e.get("draft") else "")
            if e["state"] == "running":
                _queue_running_lines(out, e)
            text = queue.error_text(e, out.lang)
            if text:
                out.line("cli.out.queue_error", error=text)
    elif sub == "move":
        entry = queue.move(args.entry, args.to)
        out.data(_entry_json(out, entry)) if out.as_json else out.line("cli.out.moved", id=entry["id"], to=args.to)
    elif sub == "clear":
        found = queue.clear(args.project)
        if out.as_json:
            out.data([_entry_json(out, e) for e in found])
        else:
            out.line("cli.out.cleared", count=len(found), ids=", ".join(str(e["id"]) for e in found) or "-")
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
