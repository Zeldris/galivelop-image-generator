"""F3.2: the read routes of the local API, on the fake engine and temporary folders."""
import contextlib
import copy
import fcntl
import io
import json
import os
import unittest
from unittest import mock
from pathlib import Path
from urllib.parse import quote

from gimg import cli, paths, queue
from tests.test_server import ServerBase

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())
ORDER = json.loads((ROOT / "examples" / "order.json").read_text())
NAME = EXAMPLE["name"]


class ReadBase(ServerBase):
    def setUp(self):
        super().setUp()
        self.root = self.tmp / "proj"
        (self.root / "refs").mkdir(parents=True)
        (self.root / "refs" / "wolf.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        cfg["profiles"]["og"] = dict(cfg["profiles"]["banner"], width=1280, height=640, targetWidth=1200,
                                     targetHeight=630, compose={"template": "t.svg", "logo": "logo.svg",
                                                               "fields": ["title"]})
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        (self.root / "t.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
        (self.root / "logo.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
        self.cli("project", "add", str(self.root))

    def cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(list(argv)), 0, argv)
        return out.getvalue()

    def cli_json(self, *argv):
        return json.loads(self.cli("--json", *argv))

    def make_order(self, key="fauna/lobo", profile="banner", count=2, work=True):
        f = self.tmp / "order.json"
        f.write_text(json.dumps(dict(ORDER, key=key, profile=profile, count=count)))
        self.cli("order", "submit", NAME, str(f))
        if work:
            self.cli("work")
        return key, profile

    def get(self, path, **kw):
        return self.call("GET", path, **kw)

    def ok_json(self, path):
        resp, payload = self.get(path)
        self.assertEqual(resp.status, 200, payload)
        return json.loads(payload)

    def order_url(self, key, profile, tail=""):
        return "/api/projects/%s/orders/%s/%s%s" % (NAME, profile, quote(key, safe=""), tail)


class ProjectTests(ReadBase):
    def test_list_and_show(self):
        listed = self.ok_json("/api/projects")
        self.assertEqual(listed, [{"name": NAME, "root": str(self.root), "ok": True, "profiles": ["banner", "thumbnail", "og"],
                                   "orders": 0, "delivered": 0}])
        self.make_order()
        self.cli("choose", NAME, "fauna/lobo", "banner", "1")
        self.make_order(key="fauna/otro")
        got = self.ok_json("/api/projects")[0]
        self.assertEqual((got["orders"], got["delivered"]), (2, 1))
        shown = self.ok_json("/api/projects/" + NAME)
        self.assertEqual(shown["name"], NAME)
        self.assertIn("banner", shown["config"]["profiles"])

    def test_unknown_project(self):
        resp, payload = self.get("/api/projects/nope")
        self.err(resp, payload, 404, "project.unknown")
        resp, payload = self.get("/api/projects/nope/orders")
        self.err(resp, payload, 404, "project.unknown")

    def test_broken_config_does_not_fail_the_list(self):
        (self.root / "galivelop-images.json").write_text("{not json")
        listed = self.ok_json("/api/projects")
        self.assertEqual(len(listed), 1)
        self.assertIs(listed[0]["ok"], False)
        self.assertTrue(listed[0]["error"]["code"].startswith("project."))
        self.assertTrue(listed[0]["error"]["message"])
        resp, payload = self.get("/api/projects/" + NAME)
        self.assertEqual(resp.status, 500, payload)


class OrderTests(ReadBase):
    def test_list_filters(self):
        self.make_order()
        url = "/api/projects/%s/orders" % NAME
        self.assertEqual(self.ok_json(url), self.cli_json("order", "list", NAME))
        self.assertEqual(len(self.ok_json(url + "?profile=banner")), 1)
        self.assertEqual(self.ok_json(url + "?chosen=true"), [])
        self.assertEqual(len(self.ok_json(url + "?chosen=false")), 1)
        resp, payload = self.get(url + "?chosen=maybe")
        self.err(resp, payload, 400, "api.bad_param")

    def test_unknown_profile(self):
        resp, payload = self.get("/api/projects/%s/orders?profile=zzz" % NAME)
        self.err(resp, payload, 404, "order.profile_unknown")

    def test_show_matches_the_cli_and_the_key_has_a_slash(self):
        key, profile = self.make_order()
        url = self.order_url(key, profile)
        self.assertIn("%2F", url)
        shown = self.ok_json(url)
        self.assertIsNone(shown.pop("deliveredTo"))
        self.assertEqual(shown, self.cli_json("order", "show", NAME, key, profile))

    def test_delivered_to_is_relative(self):
        key, profile = self.make_order()
        self.cli("choose", NAME, key, profile, "1")
        got = self.ok_json(self.order_url(key, profile))["deliveredTo"]
        self.assertIsInstance(got, str)
        self.assertFalse(os.path.isabs(got), got)
        self.assertTrue((self.root / got).is_file(), got)

    def test_unknown_order(self):
        resp, payload = self.get(self.order_url("nada", "banner"))
        self.err(resp, payload, 404, "order.unknown")


class ImageTests(ReadBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()
        self.order = self.ok_json(self.order_url(self.key, self.profile))
        self.attempt = self.order["attempts"][0]
        self.url = self.order_url(self.key, self.profile, "/attempts/%d" % self.attempt["id"])
        self.folder = paths.project_data_dir(NAME) / "orders" / self.key / ("@" + self.profile)

    def test_image_headers_and_304(self):
        resp, payload = self.get(self.url + "/image")
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.getheader("Content-Type"), "image/png")
        self.assertEqual(resp.getheader("Cache-Control"), "private, no-cache")
        self.assertEqual(payload, (self.folder / self.attempt["image"]).read_bytes())
        tag = resp.getheader("ETag")
        self.assertTrue(tag)
        resp, payload = self.get(self.url + "/image", headers={"If-None-Match": tag})
        self.assertEqual((resp.status, payload), (304, b""))
        self.assertEqual(resp.getheader("ETag"), tag)
        self.assertIsNone(resp.getheader("Content-Length"))
        self.assertIsNone(resp.getheader("Content-Type"))
        resp, payload = self.get(self.url + "/image", headers={"If-None-Match": '"other"'})
        self.assertEqual(resp.status, 200)
        self.assertTrue(payload)

    def test_raw_image_and_missing_raw(self):
        resp, payload = self.get(self.url + "/image?raw=1")
        self.assertEqual(resp.status, 200, payload)
        raw = paths.inside(self.folder, self.attempt.get("raw") or self.attempt["image"])
        self.assertEqual(payload, raw.read_bytes())
        if self.attempt.get("raw"):
            raw.unlink()
            resp, payload = self.get(self.url + "/image?raw=1")
            self.err(resp, payload, 404, "api.not_found")

    def test_attempt_without_image(self):
        (self.folder / self.attempt["image"]).unlink()
        resp, payload = self.get(self.url + "/image")
        self.err(resp, payload, 404, "api.not_found")

    def test_unknown_attempt_and_bad_id(self):
        resp, payload = self.get(self.order_url(self.key, self.profile, "/attempts/999/image"))
        self.err(resp, payload, 404, "order.attempt_unknown")
        resp, payload = self.get(self.order_url(self.key, self.profile, "/attempts/x/image"))
        self.err(resp, payload, 400, "api.bad_param")

    def test_image_resolving_outside_the_order_folder_is_404(self):
        outside = self.tmp / "secret.png"
        outside.write_bytes(b"secret")
        target = self.folder / self.attempt["image"]
        target.unlink()
        target.symlink_to(outside)
        resp, payload = self.get(self.url + "/image")
        self.err(resp, payload, 404, "api.not_found")
        self.assertNotIn(b"secret", payload)

    def test_log(self):
        rel = self.attempt.get("log")
        if rel is None:  # the fake engine keeps no log: give the attempt one, as the worker does for sd-cli
            rel = "attempts/q%d.log" % self.attempt["id"]
            (self.folder / rel).write_text("step 1/2\n")
            order_file = self.folder / "order.json"
            data = json.loads(order_file.read_text())
            data["attempts"][0]["log"] = rel
            order_file.write_text(json.dumps(data))
        resp, payload = self.get(self.url + "/log")
        self.assertEqual(resp.status, 200)
        self.assertTrue(resp.getheader("Content-Type").startswith("text/plain"))
        self.assertEqual(payload, (self.folder / rel).read_bytes())

    def test_log_missing_is_404(self):
        order_file = self.folder / "order.json"
        data = json.loads(order_file.read_text())
        for a in data["attempts"]:
            a.pop("log", None)
        order_file.write_text(json.dumps(data))
        resp, payload = self.get(self.url + "/log")
        self.err(resp, payload, 404, "api.not_found")


class QueueTests(ReadBase):
    def test_list_matches_the_cli(self):
        self.make_order(work=False)
        api = self.ok_json("/api/queue")
        cli_out = self.cli_json("queue", "list")
        strip = lambda items: [{k: v for k, v in i.items() if k not in ("estimateMs", "preview")} for i in items]
        self.assertEqual(strip(api), strip(cli_out))
        self.assertEqual(len(api), 2)
        self.assertEqual(len(self.ok_json("/api/queue?state=queued")), 2)
        self.assertEqual(self.ok_json("/api/queue?state=done"), [])

    def test_the_pause_travels_in_a_header_and_the_body_stays_a_list(self):
        self.addCleanup(queue.resume)
        queue.resume()
        resp, payload = self.get("/api/queue")
        self.assertEqual(resp.getheader("X-Queue-Paused"), "0")
        self.assertIsInstance(json.loads(payload), list)
        queue.pause()
        resp, payload = self.get("/api/queue?state=done")
        self.assertEqual(resp.getheader("X-Queue-Paused"), "1")
        self.assertEqual(json.loads(payload), [])
        self.assertIs(self.ok_json("/api/health")["paused"], True)

    def test_failed_entry_has_error_text_like_the_cli(self):
        self.make_order(work=False)
        os.environ["GIMG_FAKE_FAIL"] = "1"
        self.addCleanup(os.environ.pop, "GIMG_FAKE_FAIL", None)
        self.cli("work")
        api = self.ok_json("/api/queue?state=failed")
        self.assertTrue(api)
        self.assertTrue(all(i.get("errorText") for i in api))
        self.assertEqual(api, [dict(i) for i in self.cli_json("queue", "list", "--state", "failed")])

    def test_bad_state(self):
        resp, payload = self.get("/api/queue?state=bogus")
        self.err(resp, payload, 400, "queue.bad_state")

    def hold_worker_lock(self):
        path = queue.worker_lock_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # a live worker: running entries are not recovered

    def test_preview(self):
        self.make_order(work=False)
        entry = queue.list_entries()[0]
        resp, payload = self.get("/api/queue/%d/preview" % entry["id"])
        self.err(resp, payload, 404, "api.not_found")
        resp, payload = self.get("/api/queue/999/preview")
        self.err(resp, payload, 404, "queue.unknown")
        png = paths.data_dir() / "prev.png"
        png.write_bytes(b"\x89PNGdata")
        self.hold_worker_lock()
        queue.claim()
        queue.set_preview(entry["id"], str(png))
        resp, payload = self.get("/api/queue/%d/preview" % entry["id"])
        self.assertEqual((resp.status, payload), (200, b"\x89PNGdata"))
        self.assertEqual(resp.getheader("Cache-Control"), "no-store")
        queue.set_preview(entry["id"], str(self.tmp / "elsewhere.png"))
        (self.tmp / "elsewhere.png").write_bytes(b"x")
        resp, payload = self.get("/api/queue/%d/preview" % entry["id"])
        self.err(resp, payload, 404, "api.not_found")


class QueueResilienceTests(ReadBase):
    def test_bad_engine_omits_the_estimate_instead_of_500(self):
        self.make_order(work=False)
        with mock.patch.dict(os.environ, {"GIMG_ENGINE": "nope"}):
            got = self.ok_json("/api/queue")
        self.assertEqual(len(got), 2)
        self.assertNotIn("estimateMs", got[0])

    def test_estimate_is_read_once_per_question(self):
        self.make_order(work=False, count=3)
        with mock.patch("gimg.queue.log.estimate", return_value=5) as est:
            got = self.ok_json("/api/queue")
        self.assertEqual([e["estimateMs"] for e in got], [5, 5, 5])
        self.assertEqual(est.call_count, 1)


class AssetTests(ReadBase):
    def url(self, kind, profile="og"):
        return "/api/projects/%s/profiles/%s/assets/%s" % (NAME, profile, kind)

    def test_svg_with_sandbox_csp(self):
        for kind, name in (("template", "t.svg"), ("logo", "logo.svg")):
            resp, payload = self.get(self.url(kind))
            self.assertEqual(resp.status, 200, payload)
            self.assertEqual(payload, (self.root / name).read_bytes())
            self.assertEqual(resp.getheader("Content-Type"), "image/svg+xml")
            self.assertEqual(resp.getheader("Content-Security-Policy"),
                             "sandbox; default-src 'none'; style-src 'unsafe-inline'")
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")

    def test_big_svg_is_a_project_fault(self):
        with open(self.root / "t.svg", "ab") as fh:
            fh.truncate(5_000_001)
        resp, payload = self.get(self.url("template"))
        self.err(resp, payload, 500, "compose.svg_too_big")

    def test_errors(self):
        resp, payload = self.get(self.url("template", "zzz"))
        self.err(resp, payload, 404, "order.profile_unknown")
        resp, payload = self.get(self.url("template", "banner"))
        self.err(resp, payload, 404, "compose.template_missing")
        resp, payload = self.get(self.url("other"))
        self.err(resp, payload, 404, "api.not_found")
        (self.root / "logo.svg").unlink()
        resp, payload = self.get(self.url("logo"))
        self.err(resp, payload, 404, "compose.logo_missing")


if __name__ == "__main__":
    unittest.main()
