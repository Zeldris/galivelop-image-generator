import http.client
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import __version__, i18n, queue, server
from gimg.errors import GimgError

LOCALES = Path(__file__).resolve().parent.parent / "gimg" / "locales"

# Codes that answer 500 on purpose (corrupt files, tools, writes: «el resto de GimgError»).
INTENDED_500 = {
    "project.registry_corrupt", "project.config_missing", "project.config_unreadable", "project.version_too_new",
    "project.forbidden_git", "project.forbidden_config", "project.root_not_dir", "project.name_taken",
    "order.corrupt", "machine.config_unreadable", "machine.missing", "machine.unreadable",
    "engine.binary_missing", "engine.binary_not_executable", "engine.low_memory",
    "engine.ollama_loaded", "engine.ollama_url", "engine.watch_memory", "engine.driver_no_memory",
    "engine.timeout", "engine.failed",
    "queue.corrupt", "queue.not_running",
    "compose.svg_too_big", "compose.svg_unreadable", "compose.no_logo", "compose.tool_missing", "compose.timeout",
    "compose.tool_failed", "compose.write_failed", "compose.pending", "compose.unexpected",
    "queue.bad_progress", "engine.unknown", "engine.bad_delay", "machine.invalid", "machine.bad_path",
    "machine.bad_name", "model.catalog_invalid", "png.invalid", "png.bad_key", "order.spec_invalid",
    "compose.bad_fit", "compose.bad_size", "project.config_invalid",
    "worker.already_running", "worker.reference_missing", "worker.init_image_missing", "worker.image_move",
    "worker.unexpected", "delivery.reserved", "delivery.manifest_corrupt", "delivery.source_missing",
    "delivery.write_failed", "cli.order_unreadable", "cli.measure_zone_text",
    "model.not_installed", "model.required",
    "measure.tool_missing", "measure.tool_failed", "measure.timeout", "measure.unreadable",
    "measure.no_brand_palette", "sheet.no_images", "sheet.too_many", "sheet.unreadable",
    "sheet.out_is_input", "sheet.tool_missing", "sheet.tool_failed", "sheet.timeout", "api.unexpected",
    "serve.start_failed",
    # brand.*: faults of the machine, not of the request (the rest of brand.* has its 4xx)
    "brand.out_is_input", "brand.tool_missing", "brand.tool_failed", "brand.timeout", "brand.write_failed", "export.write_failed",
    "export.out_is_input",
    # tile.*: no endpoint serves `gimg tile` (CLI only), so none of its errors maps to a status; add a 409/400 when one does
    "tile.out_is_input", "tile.same_outputs", "tile.write_failed", "tile.exists", "tile.too_big",
}


class StatusTableTests(unittest.TestCase):
    def test_no_error_key_falls_into_500_by_accident(self):
        es = json.loads((LOCALES / "es.json").read_text(encoding="utf-8"))
        codes = {k[len("error."):] for k in es if k.startswith("error.")}
        accidental = sorted(c for c in codes if server.status_for(c) == 500 and c not in INTENDED_500)
        self.assertEqual(accidental, [])
        stale = sorted(c for c in INTENDED_500 if c in codes and server.status_for(c) != 500)
        self.assertEqual(stale, [], "listed as 500 but mapped to another status")

    def test_some_statuses(self):
        for code, status in [("api.bad_host", 403), ("api.bad_origin", 403), ("project.unknown", 404),
                             ("model.unknown", 400), ("order.choose_draft", 409), ("order.undo_discarded", 409),
                             ("limit.steps", 400), ("api.content_type", 415), ("api.length_required", 411),
                             ("api.body_too_large", 413), ("api.method_not_allowed", 405),
                             ("compose.busy", 409), ("measure.busy", 409), ("order.invalid", 400),
                             ("queue.bad_state", 400), ("brand.exists", 409), ("brand.no_matte", 400), ("brand.nothing", 500)]:
            self.assertEqual(server.status_for(code), status, code)


class ServerBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data"),
            "GIMG_LANG": "es", "GIMG_ENGINE": "fake"})
        env.start()
        self.addCleanup(env.stop)
        self.srv = server.make_server(0)
        self.port = self.srv.port
        server.start_thread(self.srv)
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def call(self, method="GET", path="/api/health", headers=None, body=None, host="default", raw_body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            if host == "default":
                host = "127.0.0.1:%d" % self.port
            if host is not None:
                conn.putheader("Host", host)
            data = raw_body
            if body is not None:
                data = json.dumps(body).encode()
            headers = dict(headers or {})
            if data is not None and "Content-Length" not in headers and headers.pop("NoLength", None) is None:
                headers["Content-Length"] = str(len(data))
            headers.pop("NoLength", None)
            for k, v in headers.items():
                if v is not None:
                    conn.putheader(k, v)
            conn.endheaders(data if data is not None else None)
            resp = conn.getresponse()
            payload = resp.read()
            return resp, payload
        finally:
            conn.close()

    def err(self, resp, payload, status, code):
        self.assertEqual(resp.status, status, payload)
        body = json.loads(payload)
        self.assertEqual(body["error"]["code"], code)
        return body["error"]

    def post(self, headers=None, **kw):
        h = {"Content-Type": "application/json"}
        h.update(headers or {})
        return self.call("POST", "/api/echo", headers=h, **kw)


@server.route("POST", "/api/test/echo/{key}")
def _echo(req):
    return {"key": req.params["key"], "body": req.body}


@server.route("GET", "/api/test/boom")
def _boom(req):
    raise RuntimeError("secret detail")


@server.route("GET", "/api/test/gimg")
def _gimg(req):
    raise GimgError("order.prompt_too_long", length=9, max=5)


JSON = {"Content-Type": "application/json"}


class QueuePauseApi(ServerBase):
    def test_pause_resume_and_health(self):
        def body(resp):
            return json.loads(resp[1])
        self.assertEqual(body(self.call("POST", "/api/queue/pause", headers=JSON, body={})), {"paused": True, "changed": True})
        self.assertEqual(body(self.call("POST", "/api/queue/pause", headers=JSON, body={})), {"paused": True, "changed": False})
        self.assertIs(body(self.call())["paused"], True)
        self.assertEqual(body(self.call("POST", "/api/queue/resume", headers=JSON, body={})), {"paused": False, "changed": True})
        self.assertEqual(body(self.call("POST", "/api/queue/resume", headers=JSON, body={})), {"paused": False, "changed": False})
        self.assertIs(body(self.call())["paused"], False)
        self.assertEqual(body(self.call("GET", "/api/queue")), [])  # still a list


class HealthAndHeaders(ServerBase):
    def test_health(self):
        resp, payload = self.call()
        self.assertEqual(resp.status, 200)
        body = json.loads(payload)
        self.assertEqual(body["ok"], True)
        self.assertEqual(body["api"], 1)
        self.assertEqual(body["version"], __version__)
        self.assertEqual(body["port"], self.port)
        self.assertEqual(body["engine"], "fake")
        self.assertIs(body["worker"], False)
        self.assertIs(body["paused"], False)
        self.assertEqual(resp.getheader("Cache-Control"), "no-store")
        self.assertIn("application/json", resp.getheader("Content-Type"))

    def test_headers_on_every_kind_of_response(self):
        for resp, _ in (self.call(), self.call(path="/api/nope"), self.call(host="evil.test"),
                        self.call(path="/"), self.call("DELETE")):
            self.assertEqual(resp.getheader("X-Content-Type-Options"), "nosniff")
            self.assertEqual(resp.getheader("Referrer-Policy"), "no-referrer")
            self.assertEqual(resp.getheader("Cross-Origin-Resource-Policy"), "same-origin")
            self.assertEqual(resp.getheader("Cross-Origin-Opener-Policy"), "same-origin")
            self.assertFalse([h for h, _ in resp.getheaders() if h.lower().startswith("access-control")])

    def test_worker_alive_follows_the_lock(self):
        import fcntl
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.assertTrue(json.loads(self.call()[1])["worker"])

    def test_locales(self):
        resp, payload = self.call(path="/api/locales/en")
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(payload), json.loads((LOCALES / "en.json").read_text(encoding="utf-8")))
        self.err(*self.call(path="/api/locales/xx"), 404, "api.not_found")
        self.err(*self.call(path="/api/locales/..%2Fmodels"), 404, "api.not_found")


class HostOrigin(ServerBase):
    def test_host(self):
        for host in (None, "evil.test", "127.0.0.1", "127.0.0.1:1", "localhost", "127.0.0.1:%d.evil.test" % 0):
            self.err(*self.call(host=host), 403, "api.bad_host")
        resp, _ = self.call(host="localhost:%d" % self.port)
        self.assertEqual(resp.status, 200)

    def test_origin(self):
        for origin in ("http://evil.test", "null", "https://127.0.0.1:%d" % self.port, "http://127.0.0.1:1"):
            self.err(*self.call(headers={"Origin": origin}), 403, "api.bad_origin")
        for origin in ("http://127.0.0.1:%d" % self.port, "http://localhost:%d" % self.port):
            self.assertEqual(self.call(headers={"Origin": origin})[0].status, 200)

    def test_sec_fetch_site(self):
        for site in ("cross-site", "same-site"):
            self.err(*self.call(headers={"Sec-Fetch-Site": site}), 403, "api.bad_origin")
        for site in ("same-origin", "none"):
            self.assertEqual(self.call(headers={"Sec-Fetch-Site": site})[0].status, 200)

    def test_checks_run_before_the_body_and_the_route(self):
        self.err(*self.call("POST", "/api/nope", host="evil.test", raw_body=b"x"), 403, "api.bad_host")


class WriteMethods(ServerBase):
    URL = "/api/test/echo/k"

    def w(self, headers=None, **kw):
        return self.call("POST", self.URL, headers=headers, **kw)

    def test_content_type(self):
        for ctype in (None, "text/plain", "application/x-www-form-urlencoded", "application/jsonx"):
            self.err(*self.w({"Content-Type": ctype}, raw_body=b"{}"), 415, "api.content_type")

    def test_charset_is_accepted(self):
        resp, payload = self.w({"Content-Type": "application/json; charset=utf-8"}, body={"a": "ñ"})
        self.assertEqual(resp.status, 200, payload)
        self.assertEqual(json.loads(payload)["body"], {"a": "ñ"})

    def test_length_required(self):
        self.err(*self.w({"Content-Type": "application/json", "NoLength": "1"}, raw_body=b"{}"), 411,
                 "api.length_required")
        self.err(*self.w({"Content-Type": "application/json", "Content-Length": "abc"}, raw_body=b"{}"), 411,
                 "api.length_required")

    def test_body_too_large(self):
        err = self.err(*self.w({"Content-Type": "application/json", "Content-Length": str(server.MAX_BODY + 1)},
                               raw_body=b"{}"), 413, "api.body_too_large")
        self.assertEqual(err["params"]["limit"], server.MAX_BODY)

    def test_body_at_the_limit_is_read(self):
        pad = "x" * (server.MAX_BODY - len('{"a":""}'))
        raw = json.dumps({"a": pad}, separators=(",", ":")).encode()
        self.assertEqual(len(raw), server.MAX_BODY)
        self.assertEqual(self.w({"Content-Type": "application/json"}, raw_body=raw)[0].status, 200)

    def test_json_must_be_an_object(self):
        for raw in (b"[]", b'"x"', b"1", b"null", b"{broken", b"", b"\xff\xfe"):
            self.err(*self.w({"Content-Type": "application/json"}, raw_body=raw), 400, "api.bad_json")
        self.assertEqual(self.w({"Content-Type": "application/json"}, raw_body=b"{}")[0].status, 200)

    def test_options_and_delete_are_405_without_cors(self):
        for method in ("OPTIONS", "DELETE", "PATCH", "HEAD"):
            resp, payload = self.call(method, "/api/health", headers={"Origin": "http://127.0.0.1:%d" % self.port})
            self.assertEqual(resp.status, 405)
            self.assertFalse([h for h, _ in resp.getheaders() if h.lower().startswith("access-control")])
            if method != "HEAD":
                self.assertEqual(json.loads(payload)["error"]["code"], "api.method_not_allowed")

    def test_known_path_wrong_method(self):
        self.err(*self.post(raw_body=b"{}", ), 404, "api.not_found")
        self.err(*self.call("POST", "/api/health", headers={"Content-Type": "application/json"}, raw_body=b"{}"),
                 405, "api.method_not_allowed")
        self.err(*self.call("GET", "/api/test/echo/k"), 405, "api.method_not_allowed")


class Paths(ServerBase):
    def test_bad_segments_are_404(self):
        for path in ("/api/../etc", "/api/%2e%2e/x", "/api/%2E%2e", "/api//health", "/api/health/", "/api/a%00b",
                     "/api/locales/en%5Cx", "/api/locales/a%2Fb", "/api/locales/%C3%28",
                     "/ui/..%2f..%2fserver.py", "/ui/%2e%2e/server.py", "/ui//index.html"):
            self.err(*self.call(path=path), 404, "api.not_found")

    def test_key_segment_can_carry_an_encoded_slash(self):
        h = {"Content-Type": "application/json"}
        resp, payload = self.call("POST", "/api/test/echo/fauna%2Faullador-rojo", headers=h, body={})
        self.assertEqual(json.loads(payload)["key"], "fauna/aullador-rojo")
        self.err(*self.call("POST", "/api/test/echo/a%2F..%2Fb", headers=h, body={}), 404, "api.not_found")
        self.err(*self.call("POST", "/api/test/echo/a%2F%2Fb", headers=h, body={}), 404, "api.not_found")

    def test_absolute_form_target_is_404(self):
        self.err(*self.call(path="http://127.0.0.1:%d/api/health" % self.port), 404, "api.not_found")


class Languages(ServerBase):
    def message(self, path="/api/test/gimg", headers=None):
        return json.loads(self.call(path=path, headers=headers)[1])["error"]

    def test_default_comes_from_i18n(self):
        err = self.message()
        self.assertEqual(err["code"], "order.prompt_too_long")
        self.assertEqual(err["params"], {"length": 9, "max": 5})
        self.assertEqual(err["message"], i18n.t("error.order.prompt_too_long", "es", length=9, max=5))

    def test_query_lang(self):
        self.assertEqual(self.message("/api/test/gimg?lang=en")["message"],
                         i18n.t("error.order.prompt_too_long", "en", length=9, max=5))

    def test_accept_language(self):
        en = i18n.t("error.order.prompt_too_long", "en", length=9, max=5)
        self.assertEqual(self.message(headers={"Accept-Language": "en-US,en;q=0.9"})["message"], en)
        self.assertEqual(self.message(headers={"Accept-Language": "fr;q=1, en;q=0.5"})["message"], en)
        self.assertEqual(self.message(headers={"Accept-Language": "en;q=0.4, es;q=0.8"})["message"],
                         i18n.t("error.order.prompt_too_long", "es", length=9, max=5))

    def test_query_wins_over_header_and_unknown_falls_through(self):
        es = i18n.t("error.order.prompt_too_long", "es", length=9, max=5)
        self.assertEqual(self.message("/api/test/gimg?lang=es", {"Accept-Language": "en"})["message"], es)
        self.assertEqual(self.message("/api/test/gimg?lang=zz", {"Accept-Language": "xx"})["message"], es)

    def test_security_errors_are_localised(self):
        resp, payload = self.call(host="evil.test", path="/api/health?lang=en")
        self.assertEqual(json.loads(payload)["error"]["message"], i18n.t("error.api.bad_host", "en"))


class Unexpected(ServerBase):
    def test_non_gimg_exception_is_500_without_traceback(self):
        resp, payload = self.call(path="/api/test/boom")
        err = self.err(resp, payload, 500, "api.unexpected")
        self.assertEqual(err["params"], {"message": "RuntimeError: secret detail"})
        self.assertNotIn("Traceback", payload.decode())
        self.assertNotIn("server.py", payload.decode())
        self.assertEqual(set(err), {"code", "params", "message"})


class Statics(ServerBase):
    def test_root_and_ui_file(self):
        for path in ("/", "/ui/index.html"):
            resp, payload = self.call(path=path)
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.getheader("Content-Type"))
            self.assertIn(b"Galivelop IG", payload)
            self.assertIn("default-src 'self'", resp.getheader("Content-Security-Policy"))
            self.assertIn("frame-ancestors 'none'", resp.getheader("Content-Security-Policy"))
            self.assertEqual(resp.getheader("X-Content-Type-Options"), "nosniff")

    def test_extension_not_allowed_or_missing_file(self):
        for path in ("/ui/server.py", "/ui/x.txt", "/ui/noext", "/ui/nope.js", "/ui", "/other", "/ui/"):
            self.err(*self.call(path=path), 404, "api.not_found")

    def test_symlink_leaving_ui_is_404(self):
        outside = self.tmp / "secret.json"
        outside.write_text("{}")
        link = server.UI_DIR / "zz-test-link.json"
        link.symlink_to(outside)
        self.addCleanup(link.unlink)
        self.err(*self.call(path="/ui/zz-test-link.json"), 404, "api.not_found")

    def test_known_types(self):
        for name, ctype in (("zz.css", "text/css"), ("zz.js", "text/javascript"), ("zz.svg", "image/svg+xml")):
            f = server.UI_DIR / name
            f.write_text("x")
            self.addCleanup(f.unlink)
            resp, _ = self.call(path="/ui/" + name)
            self.assertEqual((resp.status, resp.getheader("Content-Type").split(";")[0]), (200, ctype))


class Robustness(ServerBase):
    def test_error_that_cannot_render_still_answers(self):
        @server.route("GET", "/api/test/noparam")
        def noparam(req):
            raise GimgError("api.not_found")  # its text needs {path}
        resp, payload = self.call(path="/api/test/noparam")
        self.assertEqual(resp.status, 404)
        self.assertEqual(json.loads(payload)["error"], {"code": "api.not_found", "params": {}, "message": "api.not_found"})

    def test_short_body_is_400_not_500(self):
        server.Handler.timeout = 1
        self.addCleanup(setattr, server.Handler, "timeout", server.READ_TIMEOUT)
        self.err(*self.call("POST", "/api/test/echo/k", headers={"Content-Type": "application/json",
                 "Content-Length": "50"}, raw_body=b"{}"), 400, "api.bad_json")

    def test_huge_content_length_is_413(self):
        self.err(*self.call("POST", "/api/test/echo/k", headers={"Content-Type": "application/json",
                 "Content-Length": "9" * 5000}, raw_body=b"{}"), 413, "api.body_too_large")

    def test_long_uri_keeps_414_with_bad_request(self):
        resp, payload = self.call(path="/api/" + "a" * 70000)
        self.err(resp, payload, 414, "api.bad_request")

    def test_zone_outside_is_400(self):
        self.assertEqual(server.status_for("measure.zone_outside"), 400)


class RouterTable(unittest.TestCase):
    def test_a_route_is_one_line(self):
        self.assertTrue(any(r.parts == ("api", "health") and r.method == "GET" for r in server.ROUTES))
        self.assertEqual(server._match(("api", "p", "{p}"), ["api", "p", "x"]), {"p": "x"})
        self.assertIsNone(server._match(("api", "{p}"), ["api", "a/b"]))
        self.assertEqual(server._match(("api", "{key}"), ["api", "a/b"]), {"key": "a/b"})


if __name__ == "__main__":
    unittest.main()
