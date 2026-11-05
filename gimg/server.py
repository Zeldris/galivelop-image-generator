"""Local HTTP API (F3, D25): router, security checks, JSON errors, static files of ``gimg/ui``.

Routes are lines in ``ROUTES`` (method, pattern, handler); ``@route("GET", "/api/x/{p}")`` adds one. A handler takes a
`Request` and returns a dict/list (sent as JSON, 200) or a `Reply`. It raises `GimgError` for user errors.
"""
from __future__ import annotations

import contextlib
import json
import os
import stat as _stat
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote

from . import __version__, compose, delivery, doctor, i18n, measure, models, orders, paths, projects, queue
from .errors import GimgError

API_VERSION = 1
MAX_BODY = 1024 * 1024
READ_TIMEOUT = 30
UI_DIR = Path(__file__).resolve().parent / "ui"
LOCALES_DIR = Path(__file__).resolve().parent / "locales"

STATIC_TYPES = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
    ".woff2": "font/woff2", ".ttf": "font/ttf", ".json": "application/json; charset=utf-8",
}
STATIC_CSP = ("default-src 'self'; img-src 'self' data: blob:; script-src 'self'; style-src 'self'; "
              "frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
SVG_CSP = "sandbox; default-src 'none'; style-src 'unsafe-inline'"
BASE_HEADERS = {
    "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
    "Cross-Origin-Resource-Policy": "same-origin", "Cross-Origin-Opener-Policy": "same-origin",
}

# --- error code -> HTTP status (docs/plan.md, «Errores e idioma»); first match wins, no match = 500 ---
_EXACT = {
    403: ("api.bad_host", "api.bad_origin"),
    404: ("project.unknown", "order.unknown", "order.profile_unknown", "order.attempt_unknown", "queue.unknown",
          "api.not_found", "compose.template_missing", "compose.logo_missing", "compose.delete_unknown"),
    405: ("api.method_not_allowed",), 411: ("api.length_required",), 413: ("api.body_too_large",),
    415: ("api.content_type",),
    409: ("compose.template_exists", "compose.busy", "measure.busy", "api.heavy_busy", "compose.nothing_to_do", "compose.no_attempts", "serve.already_running", "serve.port_busy", "serve.not_running", "order.discard_chosen",
          "order.delete_chosen", "order.delete_busy", "order.compose_none", "order.compose_no_raw", "compose.delete_default", "compose.delete_config", "compose.delete_symlink", "order.history_empty", "queue.not_cancellable", "queue.not_movable", "queue.not_removable", "delivery.target_taken"),
    400: ("measure.zone_outside", "order.seed_range", "api.bad_request", "order.prompt_too_long", "order.text_unknown_field", "compose.field_unknown", "compose.template_unknown", "compose.element_unknown", "compose.bad_layout", "compose.bad_element", "compose.templates_dir_missing", "api.bad_json",
          "api.bad_param"),
}
# Server-side faults whose names match the 400 patterns below: checked first.
_SERVER_FAULTS = ("compose.svg_too_big", "engine.unknown", "engine.bad_delay", "machine.invalid", "machine.bad_path", "machine.bad_name",
                  "model.catalog_invalid", "png.invalid", "png.bad_key", "order.spec_invalid", "queue.bad_progress",
                  "compose.bad_fit", "compose.bad_size", "project.config_invalid")
_PREFIX = (("order.choose_", 409), ("order.undo_", 409), ("path.", 400), ("key.", 400), ("limit.", 400))
_SUFFIX = ((".invalid", 400), ("_invalid", 400), (".unknown", 400))
_BAD = ".bad_"


def status_for(code: str) -> int:
    """HTTP status of a `GimgError` code; 500 when the table has no entry."""
    if code in _SERVER_FAULTS:
        return 500
    for status, codes in _EXACT.items():
        if code in codes:
            return status
    for prefix, status in _PREFIX:
        if code.startswith(prefix):
            return status
    if _BAD in code:
        return 400
    for suffix, status in _SUFFIX:
        if code.endswith(suffix):
            return status
    return 500


# --- router ---
@dataclass
class Reply:
    status: int = 200
    body: object = b""          # bytes, or any JSON value when json=True
    content_type: str = "application/octet-stream"
    headers: dict = field(default_factory=dict)
    json: bool = False


@dataclass
class Request:
    method: str
    params: dict
    query: dict
    body: dict | None
    lang: str
    server: object
    headers: object


@dataclass
class Route:
    method: str
    parts: tuple
    handler: object


ROUTES: list = []
# Variables that may hold "/" once decoded (a key like "fauna/aullador-rojo"); every other segment may not.
SLASH_VARS = {"key"}


def route(method: str, pattern: str):
    def register(handler):
        ROUTES.append(Route(method, tuple(pattern.strip("/").split("/")), handler))
        return handler
    return register


def _match(parts: tuple, segments: list):
    if len(parts) != len(segments):
        return None
    params = {}
    for part, seg in zip(parts, segments):
        if part.startswith("{") and part.endswith("}"):
            name = part[1:-1]
            if "/" in seg and name not in SLASH_VARS:
                return None
            params[name] = seg
        elif part != seg:
            return None
    return params


def _bad_segment(seg: str) -> bool:
    return seg == "" or "\x00" in seg or "\\" in seg or ".." in seg.split("/") or "" in seg.split("/")


def split_path(raw: str):
    """Raw path (no query) -> decoded segments, or None if any segment is unacceptable (404)."""
    if not raw.startswith("/"):
        return None
    if raw == "/":
        return []
    segments = []
    for piece in raw[1:].split("/"):
        try:
            seg = unquote(piece, errors="strict")
        except UnicodeDecodeError:
            return None
        if _bad_segment(seg):
            return None
        segments.append(seg)
    return segments


# --- language ---
def supported_langs() -> list:
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json"))


def pick_lang(query: dict, accept: str | None) -> str:
    langs = supported_langs()
    asked = (query.get("lang") or [""])[0]
    if asked in langs:
        return asked
    ranked = []
    for index, item in enumerate((accept or "").split(",")):
        tag, _, rest = item.strip().partition(";")
        q = 1.0
        if rest.strip().startswith("q="):
            try:
                q = float(rest.strip()[2:])
            except ValueError:
                q = 0.0
        primary = tag.strip().lower().split("-")[0]
        if primary in langs and q > 0:
            ranked.append((-q, index, primary))
    if ranked:
        return min(ranked)[2]
    return i18n.default_lang()


def error_body(exc: GimgError, lang: str) -> dict:
    body = queue.make_error(exc.code, exc.errors, **exc.params)
    if exc.errors:
        from . import schema
        body["errors"] = [schema.format_error(e, lang) for e in exc.errors]
    body["message"] = exc.message(lang)
    return {"error": body}


def safe_error_body(exc: GimgError, lang: str) -> dict:
    """`error_body`, or a minimal body (message = code) if rendering the error itself fails."""
    try:
        return error_body(exc, lang)
    except Exception:  # noqa: BLE001 - a missing param or a bad schema line must not kill the response
        return {"error": {"code": exc.code, "params": {}, "message": exc.code}}


# --- handler ---
class Handler(BaseHTTPRequestHandler):
    server_version = "gimg"
    sys_version = ""
    timeout = READ_TIMEOUT

    def log_message(self, fmt, *args):  # quiet: the service has its own log
        if os.environ.get("GIMG_DEBUG") == "1":
            super().log_message(fmt, *args)

    def send_error(self, code, message=None, explain=None):  # malformed request line etc.
        lang = i18n.default_lang()
        if code == 501:
            exc, status = GimgError("api.method_not_allowed", method=self.command or "?"), 405
        elif code == 404:
            exc, status = GimgError("api.not_found", path=""), 404
        else:
            exc, status = GimgError("api.bad_request"), code if 400 <= code < 500 else 400
        self._write(Reply(status, safe_error_body(exc, lang), json=True))

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionError, TimeoutError):
            self.close_connection = True

    def do_GET(self):
        self._dispatch()

    do_POST = do_PUT = do_GET
    do_HEAD = do_DELETE = do_OPTIONS = do_PATCH = do_GET

    def _write(self, reply: Reply, no_store: bool = True):
        if reply.json:
            data = json.dumps(reply.body, ensure_ascii=False).encode("utf-8")
            ctype = "application/json; charset=utf-8"
        else:
            data = reply.body if isinstance(reply.body, bytes) else str(reply.body).encode("utf-8")
            ctype = reply.content_type
        self.send_response(reply.status)
        for name, value in BASE_HEADERS.items():
            self.send_header(name, value)
        if reply.status != 304:  # a 304 has no body, so no length or type of one
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
        if no_store and "Cache-Control" not in reply.headers:
            self.send_header("Cache-Control", "no-store")
        for name, value in reply.headers.items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD" and reply.status != 304:
            self.wfile.write(data)
        self.close_connection = True

    def _fail(self, exc: GimgError, lang: str):
        self._write(Reply(status_for(exc.code), safe_error_body(exc, lang), json=True))

    # the five checks of D25, in order
    def _check_origin(self):
        port = self.server.server_address[1]
        hosts = {"127.0.0.1:%d" % port, "localhost:%d" % port}
        host = self.headers.get("Host")
        if host is None or host.lower() not in hosts:
            raise GimgError("api.bad_host")
        origin = self.headers.get("Origin")
        if origin is not None and origin.lower() not in {"http://" + h for h in hosts}:
            raise GimgError("api.bad_origin")
        site = self.headers.get("Sec-Fetch-Site")
        if site is not None and site.lower() not in ("same-origin", "none"):
            raise GimgError("api.bad_origin")

    def _read_body(self):
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ctype != "application/json":
            raise GimgError("api.content_type")
        length = self.headers.get("Content-Length")
        if self.headers.get("Transfer-Encoding") or length is None or not length.isascii() or not length.isdigit():
            raise GimgError("api.length_required")
        if len(length) > 8 or int(length) > MAX_BODY:
            raise GimgError("api.body_too_large", limit=MAX_BODY)
        try:
            raw = self.rfile.read(int(length))
        except (TimeoutError, OSError):
            raise GimgError("api.bad_json")
        if len(raw) != int(length):
            raise GimgError("api.bad_json")
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise GimgError("api.bad_json")
        if not isinstance(body, dict):
            raise GimgError("api.bad_json")
        return body

    def _dispatch(self):
        self.server.begin_request()
        try:
            self._dispatch_one()
        finally:
            self.server.end_request()

    def _dispatch_one(self):
        raw, _, qs = self.path.partition("?")
        query = parse_qs(qs, keep_blank_values=True)
        lang = pick_lang(query, self.headers.get("Accept-Language"))
        try:
            self._check_origin()
            if self.command not in ("GET", "POST", "PUT", "DELETE"):
                raise GimgError("api.method_not_allowed", method=self.command)
            body = self._read_body() if self.command in ("POST", "PUT") else None
            segments = split_path(raw)
            reply = None
            if segments is not None:
                reply = self._route(segments, query, body, lang)
            if reply is None:
                raise GimgError("api.not_found", path=raw[:200])
            self._write(reply, no_store=segments[:1] == ["api"])
        except GimgError as exc:
            self._fail(exc, lang)
        except Exception as exc:  # noqa: BLE001 - nothing but the type and text leaves the process
            if os.environ.get("GIMG_DEBUG") == "1":
                traceback.print_exc(file=sys.stderr)
            self._fail(GimgError("api.unexpected", message="%s: %s" % (type(exc).__name__, exc)), lang)

    def _route(self, segments, query, body, lang):
        wrong_method = False
        for entry in ROUTES:
            params = _match(entry.parts, segments)
            if params is None:
                continue
            if entry.method != self.command:
                wrong_method = True
                continue
            result = entry.handler(Request(self.command, params, query, body, lang, self.server, self.headers))
            return result if isinstance(result, Reply) else Reply(200, result, json=True)
        if wrong_method:
            raise GimgError("api.method_not_allowed", method=self.command)
        if self.command == "GET":
            return _static(segments)
        return None


def _static(segments):
    """``/`` -> ui/index.html; ``/ui/<path>`` -> files of ``gimg/ui`` with a known extension. None = 404."""
    if not segments:
        rel = "index.html"
    elif segments[0] == "ui" and len(segments) > 1:
        rel = "/".join(segments[1:])
    else:
        return None
    ctype = STATIC_TYPES.get(os.path.splitext(rel)[1].lower())
    if ctype is None:
        return None
    try:
        target = paths.inside(UI_DIR, rel)
        if not target.is_file():
            return None
        data = target.read_bytes()
    except (GimgError, OSError):
        return None
    return Reply(200, data, ctype, {"Content-Security-Policy": STATIC_CSP, "Cache-Control": "no-cache"})


# --- routes of F3.1 ---
@route("GET", "/api/health")
def health(req):
    try:
        from . import engine
        provider = engine.get_engine().provider
    except GimgError:
        provider = None
    return {"ok": True, "api": API_VERSION, "version": __version__, "pid": os.getpid(),
            "port": req.server.server_address[1], "engine": provider, "worker": queue.worker_alive() is True}


@route("GET", "/api/locales/{lang}")
def locales(req):
    lang = req.params["lang"]
    if lang not in supported_langs():
        raise GimgError("api.not_found", path=lang)
    with open(LOCALES_DIR / (lang + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


# --- read routes of F3.2 (the same functions the CLI calls) ---
def _int_param(name: str, value: str) -> int:
    if not value.isascii() or not value.isdigit() or len(value) > 9:
        raise GimgError("api.bad_param", name=name)
    return int(value)


def _bool_query(req, name: str):
    raw = (req.query.get(name) or [None])[0]
    if raw is None:
        return None
    if raw not in ("true", "false"):
        raise GimgError("api.bad_param", name=name)
    return raw == "true"


def _config_profile(config: dict, profile: str) -> dict:
    found = config["profiles"].get(profile)
    if found is None:
        raise GimgError("order.profile_unknown", profile=profile)
    return found


@route("GET", "/api/projects")
def projects_list(req):
    out = []
    for name, entry in projects.list_projects().items():
        item = {"name": name, "root": entry["root"], "ok": True, "profiles": [], "orders": 0, "delivered": 0}
        try:
            item["profiles"] = list(projects.get(name)["config"]["profiles"])
            found = orders.list_orders(name)
            item["orders"] = len(found)
            item["delivered"] = sum(1 for o in found if o["chosen"] is not None)
        except GimgError as exc:  # a broken project must not take the list down
            item["ok"] = False
            item["error"] = safe_error_body(exc, req.lang)["error"]
        out.append(item)
    return out


@route("GET", "/api/projects/{p}")
def project_show(req):
    return projects.get(req.params["p"])


@route("GET", "/api/projects/{p}/orders")
def orders_list(req):
    name = req.params["p"]
    profile = (req.query.get("profile") or [None])[0] or None
    if profile is not None:
        _config_profile(projects.get(name)["config"], profile)
    return orders.list_orders(name, profile, _bool_query(req, "chosen"))


def _delivered_to(project: str, key: str, profile: str, chosen) -> str | None:
    """Path (relative to the project root, never absolute) of the delivered file, or None if nothing is chosen."""
    if chosen is None:
        return None
    try:
        return delivery.delivered_file(project, key, profile)
    except GimgError:
        return None


@route("GET", "/api/projects/{p}/orders/{profile}/{key}")
def order_show(req):
    q = req.params
    order = orders.get(q["p"], q["key"], q["profile"])
    order["deliveredTo"] = _delivered_to(q["p"], q["key"], q["profile"], order["chosen"])
    return order


def _etag(st) -> str:
    return '"%x-%x"' % (st.st_size, st.st_mtime_ns)


def _file_reply(req, path, ctype: str, cache: str = "private, no-cache", etag: bool = True):
    """Serve `path` (already guarded); 404 if it is not a file. With `etag`, honour ``If-None-Match`` (304)."""
    try:
        with open(path, "rb") as fh:
            st = os.fstat(fh.fileno())
            if not _stat.S_ISREG(st.st_mode):
                raise GimgError("api.not_found", path=path.name)
            tag = _etag(st)
            wanted = req.headers.get("If-None-Match") if etag else None
            headers = {"Cache-Control": cache}
            if etag:
                headers["ETag"] = tag
            if wanted is not None and (wanted.strip() == "*" or tag in [w.strip() for w in wanted.split(",")]):
                return Reply(304, b"", ctype, headers)
            return Reply(200, fh.read(), ctype, headers)
    except OSError:
        raise GimgError("api.not_found", path=path.name)


def _guarded(call):
    """Run a path-resolving `call`; a path that fails the D25 guard is simply not found (404)."""
    try:
        return call()
    except GimgError as exc:
        if exc.code.startswith("path."):
            raise GimgError("api.not_found", path="") from exc
        raise


def _attempt_of(req) -> tuple:
    q = req.params
    order = orders.get(q["p"], q["key"], q["profile"])
    attempt_id = _int_param("id", q["id"])
    for item in order["attempts"]:
        if item["id"] == attempt_id:
            return order, item
    raise GimgError("order.attempt_unknown", attempt=attempt_id, order=order["key"], profile=order["profile"])


_ATT = "/api/projects/{p}/orders/{profile}/{key}/attempts/{id}"


@route("GET", _ATT + "/image")
def attempt_image(req):
    _order, attempt = _attempt_of(req)
    q = req.params
    raw = (req.query.get("raw") or [""])[0]
    if raw not in ("", "0", "1"):
        raise GimgError("api.bad_param", name="raw")
    find = orders.raw_image if raw == "1" else orders.attempt_image
    path = _guarded(lambda: find(q["p"], q["key"], q["profile"], attempt))
    return _file_reply(req, path, "image/png")


@route("GET", _ATT + "/log")
def attempt_log(req):
    _order, attempt = _attempt_of(req)
    q = req.params
    rel = attempt.get("log")
    if not isinstance(rel, str):
        raise GimgError("api.not_found", path="log")
    folder = _guarded(lambda: orders.attempt_image(q["p"], q["key"], q["profile"], {"image": "."}))
    path = _guarded(lambda: paths.inside(folder, rel))
    return _file_reply(req, path, "text/plain; charset=utf-8", cache="no-store", etag=False)


def _template_param(value, allow_empty=True):
    """A template id from a body or a query: a string (``None`` is the default template); anything else is a bad param."""
    if value is not None and not isinstance(value, str):
        raise GimgError("api.bad_param", name="template" if allow_empty else "id")
    return value


@route("GET", "/api/projects/{p}/profiles/{profile}/templates")
def profile_templates(req):
    q = req.params
    proj = projects.get(q["p"])
    _config_profile(proj["config"], q["profile"])
    return compose.templates_with_elements(proj, q["profile"])


@route("POST", "/api/projects/{p}/profiles/{profile}/templates")
def profile_template_save(req):
    q = req.params
    body = _fields(req.body, ("from", "name", "dest"))
    origin = body.get("from")
    if not (isinstance(origin, dict) and set(origin) == {"key", "attempt"} and isinstance(origin["key"], str)):
        raise GimgError("api.bad_param", name="from")
    attempt_id = _attempt_id(origin["attempt"])
    name = body.get("name")
    if not isinstance(name, str):
        raise GimgError("api.bad_param", name="name")
    dest = body.get("dest", "local")
    if not isinstance(dest, str):
        raise GimgError("api.bad_param", name="dest")
    _config_profile(projects.get(q["p"])["config"], q["profile"])
    return Reply(201, compose.save_template(q["p"], origin["key"], q["profile"], attempt_id, name, dest), json=True)


_TPL = "/api/projects/{p}/profiles/{profile}/templates/{id}"


@route("GET", _TPL)
def profile_template_usage(req):
    q = req.params
    return compose.template_usage(q["p"], q["profile"], q["id"])


@route("DELETE", _TPL)
def profile_template_delete(req):
    q = req.params
    return compose.delete_template(q["p"], q["profile"], q["id"])


@route("GET", "/api/projects/{p}/profiles/{profile}/assets/{kind}")
def profile_asset(req):
    q = req.params
    if q["kind"] not in ("template", "logo"):
        raise GimgError("api.not_found", path=q["kind"])
    project = projects.get(q["p"])
    _config_profile(project["config"], q["profile"])
    cfg = (compose.merged_profile(project, q["profile"]) or {}).get("compose")
    wanted = _template_param(req.query.get("id", [None])[0], allow_empty=False)
    if wanted is not None:
        cfg = compose.effective(cfg, wanted)  # compose.template_unknown for an id that does not exist
    if not cfg:
        raise GimgError("compose.template_missing", path="")
    template, logo = compose.resolve_assets(project["root"], cfg)
    path = template if q["kind"] == "template" else logo
    if path is None:
        raise GimgError("compose.logo_missing", path="")
    reply = _file_reply(req, path, "image/svg+xml", cache="no-store", etag=False)
    reply.headers["Content-Security-Policy"] = SVG_CSP
    return reply


@route("GET", "/api/queue")
def queue_list(req):
    state = (req.query.get("state") or [None])[0]
    if state is not None and state not in queue.STATES:
        raise GimgError("queue.bad_state", state=state, states=", ".join(queue.STATES))
    entries = queue.list_entries(None if state is None else [state])
    provider = None
    memo = {}
    out = []
    for entry in entries:
        item = queue.entry_view(entry, req.lang)
        item.pop("preview", None)
        if entry["state"] in ("queued", "running"):
            try:  # the estimate is optional: a bad engine setting must not take the whole queue down
                if provider is None:
                    from . import engine
                    provider = engine.get_engine().provider
                estimate = queue.estimate_for(entry, provider, memo)
            except GimgError:
                estimate = None
            if estimate is not None:
                item["estimateMs"] = estimate
        out.append(item)
    return out


@route("GET", "/api/queue/{id}/preview")
def queue_preview(req):
    entry = queue.get(_int_param("id", req.params["id"]))
    shown = entry.get("preview")
    if not isinstance(shown, str):
        raise GimgError("api.not_found", path="preview")
    data = paths.data_dir().resolve()
    try:
        rel = os.path.relpath(Path(shown).resolve(), data)
    except (OSError, ValueError, RuntimeError):
        raise GimgError("api.not_found", path="preview")
    path = _guarded(lambda: paths.inside(data, rel))
    return _file_reply(req, path, "image/png", cache="no-store", etag=False)


# --- write routes of F3.3 (the same functions the CLI calls) ---
HEAVY_WAIT_S = float(os.environ.get("GIMG_HEAVY_WAIT_S") or 60)  # tests set the attribute
_HEAVY = threading.BoundedSemaphore(1)


@contextlib.contextmanager
def _heavy():
    """One heavy task (ffmpeg/rsvg: compose, measure) at a time; the second waits `HEAVY_WAIT_S`, then 409
    `api.heavy_busy` (the holder may be any heavy task, so the text names none)."""
    if not _HEAVY.acquire(timeout=HEAVY_WAIT_S):
        raise GimgError("api.heavy_busy")
    try:
        yield
    finally:
        _HEAVY.release()


def _after_enqueue() -> None:
    """The one place where the server starts the worker after an enqueue (a no-op unless `gimg serve` runs it)."""
    from . import service
    service.kick()


def _fields(body: dict, allowed: tuple) -> dict:
    for name in body:
        if name not in allowed:
            raise GimgError("api.bad_param", name=name)
    return body


def _attempt_id(value) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise GimgError("api.bad_param", name="attempt")
    return value


def _str_field(body: dict, name: str) -> str:
    value = body.get(name)
    if not isinstance(value, str):
        raise GimgError("api.bad_param", name=name)
    return value


@route("POST", "/api/projects/{p}/orders")
def order_submit(req):
    order = dict(req.body)
    template = _template_param(order.pop("template", None))  # not part of the order file: it goes to the attempts
    model = order.pop("model", None)  # idem: the model of the attempts (F4d)
    if model is not None and not isinstance(model, str):
        raise GimgError("api.bad_param", name="model")
    entries, provider = queue.submit_order(req.params["p"], order, template=template, model=model)
    _after_enqueue()
    # the order itself is read back by its own key: `submit` normalises it (profile, params)
    record = orders.get(req.params["p"], entries[0]["key"], entries[0]["profile"]) if entries else None
    view = queue.queued_view(entries, provider, req.lang)
    return Reply(201, {"order": record, **view}, json=True)


_ORD = "/api/projects/{p}/orders/{profile}/{key}"


@route("PUT", _ORD + "/text")
def order_text(req):
    q = req.params
    text = req.body.get("text")
    if not isinstance(_fields(req.body, ("text",)).get("text"), dict):
        raise GimgError("api.bad_param", name="text")
    orders.set_text(q["p"], q["key"], q["profile"], text, replace=True)
    return orders.get(q["p"], q["key"], q["profile"])


@route("POST", _ORD + "/attempts")
def attempt_new(req):
    q, body = req.params, _fields(req.body, ("count", "seed", "prompt", "steps", "cfg", "sampler", "draft", "template", "model"))
    model = body.get("model")
    if model is not None and not isinstance(model, str):
        raise GimgError("api.bad_param", name="model")
    draft = body.get("draft")
    if draft is not None and not isinstance(draft, bool):
        raise GimgError("api.bad_param", name="draft")
    overrides = {k: body[k] for k in ("steps", "cfg", "sampler") if body.get(k) is not None}
    entries, provider = queue.new_attempts(q["p"], q["key"], q["profile"], body.get("count", 1),
                                           seed=body.get("seed"), prompt=body.get("prompt"), params=overrides,
                                           draft=draft, template=_template_param(body.get("template")), model=model)
    _after_enqueue()
    return Reply(202, queue.queued_view(entries, provider, req.lang), json=True)


@route("DELETE", _ATT)
def attempt_delete(req):
    q = req.params
    return orders.delete_attempt(q["p"], q["key"], q["profile"], _int_param("id", q["id"]))


@route("DELETE", _ATT + "/compose")
def attempt_compose_delete(req):
    q = req.params
    return orders.delete_compose(q["p"], q["key"], q["profile"], _int_param("id", q["id"]))


@route("POST", _ATT + "/mark")
def attempt_mark(req):
    q = req.params
    state = _str_field(_fields(req.body, ("state",)), "state")
    return orders.mark(q["p"], q["key"], q["profile"], _int_param("id", q["id"]), state)


@route("POST", _ATT + "/note")
def attempt_note(req):
    q = req.params
    text = _fields(req.body, ("text",)).get("text")
    return orders.note(q["p"], q["key"], q["profile"], _int_param("id", q["id"]), text)


@route("POST", _ORD + "/choose")
def order_choose(req):
    q = req.params
    attempt = _attempt_id(_fields(req.body, ("attempt",)).get("attempt"))
    result = delivery.choose(q["p"], q["key"], q["profile"], attempt)
    result["deliveredTo"] = _delivered_to(q["p"], q["key"], q["profile"], result["new"])
    return result


@route("POST", _ORD + "/undo")
def order_undo(req):
    q = req.params
    _fields(req.body, ())
    result = delivery.undo(q["p"], q["key"], q["profile"])
    result["deliveredTo"] = _delivered_to(q["p"], q["key"], q["profile"], result["new"])
    return result


@route("POST", _ATT + "/compose")
def attempt_compose(req):
    q = req.params
    body = _fields(req.body, ("text", "template", "layout"))
    text = body.get("text")
    if text is not None and not (isinstance(text, dict) and all(isinstance(v, str) for v in text.values())):
        raise GimgError("api.bad_param", name="text")
    template = _template_param(body.get("template"))
    layout = body.get("layout")
    if layout is not None and not isinstance(layout, dict):
        raise GimgError("compose.bad_layout", element="", reason="not an object")
    attempt_id = _int_param("id", q["id"])
    with _heavy():
        return compose.recompose(q["p"], q["key"], q["profile"], attempt_id, text or None, template, layout)


@route("GET", _ATT + "/measure")
def attempt_measure(req):
    q = req.params
    _order, attempt = _attempt_of(req)
    raw = (req.query.get("raw") or [""])[0]
    if raw not in ("", "0", "1"):
        raise GimgError("api.bad_param", name="raw")
    base = (req.query.get("base") or [""])[0]
    if base not in ("", "0", "1") or (base == "1" and raw == "1"):
        raise GimgError("api.bad_param", name="base")
    zone = (req.query.get("zone") or [None])[0]
    text = (req.query.get("text") or [None])[0]
    if (zone is None) != (text is None):
        raise GimgError("api.bad_param", name="zone" if zone is None else "text")
    find = orders.raw_image if raw == "1" or base == "1" else orders.attempt_image
    path = _guarded(lambda: find(q["p"], q["key"], q["profile"], attempt))
    proj = projects.get(q["p"])
    brand = proj["config"].get("brand") or {}
    dest_zone = measure.parse_zone(zone) if base == "1" and zone is not None else None
    with _heavy():
        if dest_zone is not None:  # F4c: the zone is in pixels of the delivered image; the raw one is measured
            raw_size = measure.image_size(path)
            zone = ",".join(str(v) for v in compose.zone_to_raw(_config_profile(proj["config"], q["profile"]),
                                                                *raw_size, dest_zone))
        result = measure.measure(path, brand.get("palette") or None, (), zone, text)
    if dest_zone is not None:
        result["contrast"]["zone"] = list(dest_zone)
    result["image"] = attempt["id"]  # by id, never by path (D25)
    result["raw"] = raw == "1"
    result["base"] = base == "1"
    return result


@route("POST", "/api/queue/{id}/cancel")
def queue_cancel(req):
    _fields(req.body, ())
    return queue.entry_view(queue.cancel(_int_param("id", req.params["id"])), req.lang)


@route("DELETE", "/api/queue/{id}")
def queue_remove(req):
    return queue.entry_view(queue.remove(_int_param("id", req.params["id"])), req.lang)


@route("POST", "/api/queue/{id}/move")
def queue_move(req):
    to = _fields(req.body, ("to",)).get("to")
    if not isinstance(to, str):
        raise GimgError("api.bad_param", name="to")
    return queue.entry_view(queue.move(_int_param("id", req.params["id"]), to), req.lang)


@route("POST", "/api/queue/clear")
def queue_clear(req):
    project = _fields(req.body, ("project",)).get("project")
    if project is not None and not isinstance(project, str):
        raise GimgError("api.bad_param", name="project")
    return [queue.entry_view(e, req.lang) for e in queue.clear(project)]


@route("GET", "/api/models")
def models_list(req):
    return models.listing(req.lang)


@route("GET", "/api/projects/{p}/check")
def project_check(req):
    projects.get(req.params["p"])  # project.unknown (404) before anything else
    return [{k: v for k, v in c.as_dict(req.lang).items() if v is not None} for c in doctor.run_project(req.params["p"])]


# --- server ---
class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clock = threading.Lock()
        self.last_activity = time.monotonic()  # the idle clock of `gimg serve`
        self.inflight = 0

    def begin_request(self) -> None:
        with self._clock:
            self.inflight += 1
            self.last_activity = time.monotonic()

    def end_request(self) -> None:
        with self._clock:
            self.inflight -= 1
            self.last_activity = time.monotonic()

    def activity(self) -> tuple:
        """``(seconds since the last request began or ended, requests in progress)``."""
        with self._clock:
            return time.monotonic() - self.last_activity, self.inflight

    @property
    def port(self) -> int:
        return self.server_address[1]


def make_server(port: int = 0) -> Server:
    """Bind ``127.0.0.1:<port>`` (0 = any free port) without serving yet; see `start_thread`."""
    return Server(("127.0.0.1", port), Handler)


def start_thread(server: Server) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
    thread.start()
    return thread
