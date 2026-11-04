"""Local HTTP API (F3, D25): router, security checks, JSON errors, static files of ``gimg/ui``.

Routes are lines in ``ROUTES`` (method, pattern, handler); ``@route("GET", "/api/x/{p}")`` adds one. A handler takes a
`Request` and returns a dict/list (sent as JSON, 200) or a `Reply`. It raises `GimgError` for user errors.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import traceback
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote

from . import __version__, i18n, paths, queue
from .errors import GimgError

API_VERSION = 1
MAX_BODY = 1024 * 1024
READ_TIMEOUT = 30
UI_DIR = Path(__file__).resolve().parent / "ui"
LOCALES_DIR = Path(__file__).resolve().parent / "locales"

STATIC_TYPES = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
    ".woff2": "font/woff2", ".json": "application/json; charset=utf-8",
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
          "api.not_found", "compose.template_missing", "compose.logo_missing"),
    405: ("api.method_not_allowed",), 411: ("api.length_required",), 413: ("api.body_too_large",),
    415: ("api.content_type",),
    409: ("compose.busy", "measure.busy", "compose.nothing_to_do", "compose.no_attempts", "order.discard_chosen",
          "order.history_empty", "queue.not_cancellable", "delivery.target_taken"),
    400: ("order.prompt_too_long", "order.text_unknown_field", "compose.field_unknown", "api.bad_json",
          "api.bad_param"),
}
_PREFIX = (("order.choose_", 409), ("order.undo_", 409), ("path.", 400), ("key.", 400), ("limit.", 400))
_SUFFIX = ((".invalid", 400), ("_invalid", 400), (".unknown", 400))
_BAD = ".bad_"


def status_for(code: str) -> int:
    """HTTP status of a `GimgError` code; 500 when the table has no entry."""
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
        gcode = "api.method_not_allowed" if code == 501 else "api.not_found" if code == 404 else "api.bad_json"
        params = {"method": self.command or "?"} if gcode == "api.method_not_allowed" else (
            {"path": ""} if gcode == "api.not_found" else {})
        self._write(Reply(405 if code == 501 else 404 if code == 404 else 400,
                          error_body(GimgError(gcode, **params), lang), json=True))

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
        self._write(Reply(status_for(exc.code), error_body(exc, lang), json=True))

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
        if int(length) > MAX_BODY:
            raise GimgError("api.body_too_large", limit=MAX_BODY)
        raw = self.rfile.read(int(length))
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise GimgError("api.bad_json")
        if not isinstance(body, dict):
            raise GimgError("api.bad_json")
        return body

    def _dispatch(self):
        raw, _, qs = self.path.partition("?")
        query = parse_qs(qs, keep_blank_values=True)
        lang = pick_lang(query, self.headers.get("Accept-Language"))
        try:
            self._check_origin()
            if self.command not in ("GET", "POST", "PUT"):
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
            "port": req.server.server_address[1], "engine": provider, "worker": queue.worker_alive()}


@route("GET", "/api/locales/{lang}")
def locales(req):
    lang = req.params["lang"]
    if lang not in supported_langs():
        raise GimgError("api.not_found", path=lang)
    with open(LOCALES_DIR / (lang + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


# --- server ---
class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

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
