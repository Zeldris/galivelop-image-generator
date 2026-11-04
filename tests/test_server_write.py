"""F3.3: the write routes of the local API (and `measure`), on the fake engine and temporary folders."""
import json
import shutil
import threading
import unittest
from urllib.parse import quote

from gimg import fsutil, orders, queue, schema, server
from tests.test_server_read import NAME, ORDER, ReadBase

TOOLS = shutil.which("ffmpeg") is not None and shutil.which("rsvg-convert") is not None
JSON = {"Content-Type": "application/json"}


class WriteBase(ReadBase):
    def send(self, method, path, body=None):
        return self.call(method, path, headers=dict(JSON), body={} if body is None else body)

    def ok(self, method, path, body=None, status=200):
        resp, payload = self.send(method, path, body)
        self.assertEqual(resp.status, status, payload)
        return json.loads(payload)

    def bad(self, method, path, body, status, code):
        resp, payload = self.send(method, path, body)
        return self.err(resp, payload, status, code)

    def att(self, key, profile, id, tail=""):
        return self.order_url(key, profile, "/attempts/%d%s" % (id, tail))

    def orders_url(self):
        return "/api/projects/%s/orders" % NAME

    def order(self, **kw):
        return dict(dict(ORDER, key="fauna/lobo", profile="banner", count=2), **kw)

    def tight(self):
        """A machine profile with maxSteps 2 for the rest of the test."""
        from unittest import mock
        import os
        profile = self.tmp / "tight.json"
        profile.write_text(json.dumps({"name": "tight", "minFreeMemoryMb": 1, "watchMemoryMb": 1,
                                       "maxReferences": 1, "timeoutS": 5, "maxSteps": 2, "maxPixels": 1048576}))
        env = mock.patch.dict(os.environ, {"GIMG_MACHINE_PROFILE": str(profile)})
        env.start()
        self.addCleanup(env.stop)


class SubmitTests(WriteBase):
    def test_submit_matches_the_cli(self):
        got = self.ok("POST", self.orders_url(), self.order(), 201)
        self.assertEqual(got["order"]["key"], "fauna/lobo")
        self.assertEqual([e["state"] for e in got["entries"]], ["queued", "queued"])
        self.assertIn("estimateMs", got)
        f = self.tmp / "o.json"
        f.write_text(json.dumps(self.order(key="fauna/otro")))
        cli = self.cli_json("order", "submit", NAME, str(f))
        self.assertEqual(sorted(cli), ["entries", "estimateMs"])
        self.assertEqual(sorted(got["entries"][0]), sorted(cli["entries"][0]))
        self.assertEqual(got["estimateMs"], cli["estimateMs"])
        self.assertEqual(len(queue.list_entries()), 4)

    def test_invalid_schema_has_errors(self):
        err = self.bad("POST", self.orders_url(), {"key": "x"}, 400, "order.invalid")
        self.assertTrue(err["errors"])
        self.assertEqual(queue.list_entries(), [])

    def test_limits_key_and_count(self):
        self.tight()
        self.bad("POST", self.orders_url(), self.order(params={"steps": 6}), 400, "limit.steps")
        self.assertEqual(queue.list_entries(), [])
        self.bad("POST", self.orders_url(), self.order(key="../x"), 400, "order.invalid")
        self.bad("POST", "/api/projects/%s/orders/banner/%s/attempts" % (NAME, quote("Mala Clave", safe="")), {}, 400,
                 "order.invalid")
        self.bad("POST", self.orders_url(), self.order(count=51), 400, "order.invalid")
        self.bad("POST", self.orders_url(), self.order(profile="nope"), 404, "order.profile_unknown")
        self.bad("POST", "/api/projects/nope/orders", self.order(), 404, "project.unknown")

    def test_bad_engine_queues_nothing(self):
        from unittest import mock
        import os
        with mock.patch.dict(os.environ, {"GIMG_ENGINE": "nope"}):
            self.bad("POST", self.orders_url(), self.order(), 500, "engine.unknown")
        self.assertEqual(queue.list_entries(), [])


class AttemptTests(WriteBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()

    def test_new_attempts_match_the_cli(self):
        got = self.ok("POST", self.order_url(self.key, self.profile, "/attempts"),
                      {"count": 2, "seed": 7, "steps": 4, "draft": True}, 202)
        self.assertEqual([e["seed"] for e in got["entries"]], [7, 8])
        cli = self.cli_json("attempt", "new", NAME, self.key, self.profile, "--seed", "7", "--count", "2",
                            "--steps", "4", "--draft")
        self.assertEqual(sorted(got), sorted(cli))
        self.assertEqual([e["seed"] for e in cli["entries"]], [7, 8])
        self.assertEqual(sorted(got["entries"][0]), sorted(cli["entries"][0]))

    def test_count_prompt_and_unknown_fields(self):
        url = self.order_url(self.key, self.profile, "/attempts")
        self.bad("POST", url, {"count": 0}, 400, "order.count_invalid")
        self.bad("POST", url, {"count": 51}, 400, "order.count_invalid")
        self.bad("POST", url, {"count": "2"}, 400, "order.count_invalid")
        self.bad("POST", url, {"prompt": "x" * 100000}, 400, "order.invalid")
        top = schema.load_schema("order")["properties"]["prompt"]["maxLength"]
        self.bad("POST", url, {"prompt": "x" * top}, 400, "order.prompt_too_long")  # the profile style tips it over
        self.tight()
        self.bad("POST", url, {"steps": 6}, 400, "limit.steps")
        self.bad("POST", url, {"draft": "yes"}, 400, "api.bad_param")
        self.bad("POST", url, {"nope": 1}, 400, "api.bad_param")
        self.bad("POST", self.order_url("fauna/otro", self.profile, "/attempts"), {}, 404, "order.unknown")

    def test_mark_equals_the_cli(self):
        got = self.ok("POST", self.att(self.key, self.profile, 1, "/mark"), {"state": "candidate"})
        self.assertEqual(got["state"], "candidate")
        cli = self.cli_json("attempt", "mark", NAME, self.key, self.profile, "1", "candidate")
        self.assertEqual(got, cli)
        url = self.att(self.key, self.profile, 1, "/mark")
        self.bad("POST", url, {"state": "great"}, 400, "order.state_invalid")
        self.bad("POST", url, {}, 400, "api.bad_param")
        self.bad("POST", self.att(self.key, self.profile, 99, "/mark"), {"state": "new"}, 404,
                 "order.attempt_unknown")
        self.bad("POST", self.att(self.key, self.profile, 1, "/mark").replace("/1/", "/x/"),
                 {"state": "new"}, 400, "api.bad_param")

    def test_discarding_the_chosen_is_409(self):
        self.ok("POST", self.order_url(self.key, self.profile, "/choose"), {"attempt": 1})
        self.bad("POST", self.att(self.key, self.profile, 1, "/mark"), {"state": "discarded"}, 409,
                 "order.discard_chosen")

    def test_note(self):
        url = self.att(self.key, self.profile, 1, "/note")
        self.assertEqual(self.ok("POST", url, {"text": "buena"})["note"], "buena")
        self.bad("POST", url, {"text": 5}, 400, "order.note_invalid")
        self.bad("POST", url, {}, 400, "order.note_invalid")

    def test_text(self):
        url = self.order_url(self.key, "og", "/text")
        self.make_order(key=self.key, profile="og", count=1)
        got = self.ok("PUT", url, {"text": {"title": "Hola"}})
        self.assertEqual(got["text"], {"title": "Hola"})
        self.bad("PUT", url, {"text": {"nope": "x"}}, 400, "order.text_unknown_field")
        self.bad("PUT", url, {"text": "x"}, 400, "api.bad_param")
        self.bad("PUT", url, {"text": {"title": 3}}, 400, "order.invalid")


class ChooseTests(WriteBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()
        self.url = self.order_url(self.key, self.profile)

    def test_choose_and_undo_equal_the_cli(self):
        got = self.ok("POST", self.url + "/choose", {"attempt": 1})
        self.assertEqual(sorted(got), ["new", "old"])
        other, _ = self.make_order(key="fauna/otro")  # a second, fresh order for the CLI side
        cli = self.cli_json("choose", NAME, other, self.profile, "1")
        self.assertEqual(got, cli)
        self.ok("POST", self.url + "/choose", {"attempt": 2})
        undone = self.ok("POST", self.url + "/undo", {})
        self.assertEqual(sorted(undone), ["new", "old"])

    def test_discarded_and_bad_attempt(self):
        self.ok("POST", self.att(self.key, self.profile, 2, "/mark"), {"state": "discarded"})
        self.bad("POST", self.url + "/choose", {"attempt": 2}, 409, "order.choose_discarded")
        self.bad("POST", self.url + "/choose", {"attempt": "2"}, 400, "api.bad_param")
        self.bad("POST", self.url + "/choose", {}, 400, "api.bad_param")
        self.bad("POST", self.url + "/choose", {"attempt": 99}, 404, "order.attempt_unknown")

    def test_undo_without_history(self):
        self.bad("POST", self.url + "/undo", {}, 409, "order.history_empty")
        self.bad("POST", self.url + "/undo", {"x": 1}, 400, "api.bad_param")


class CancelTests(WriteBase):
    def test_cancel(self):
        self.make_order(work=False)
        got = self.ok("POST", "/api/queue/1/cancel")
        self.assertEqual(got["state"], "cancelled")
        self.assertEqual(got, queue.entry_view(queue.get(1), "es"))
        self.bad("POST", "/api/queue/1/cancel", {}, 409, "queue.not_cancellable")
        self.bad("POST", "/api/queue/99/cancel", {}, 404, "queue.unknown")
        self.bad("POST", "/api/queue/x/cancel", {}, 400, "api.bad_param")

    def test_finished_entry(self):
        self.make_order()
        self.bad("POST", "/api/queue/1/cancel", {}, 409, "queue.not_cancellable")

    def test_after_enqueue_is_the_single_hook(self):
        from unittest import mock
        with mock.patch.object(server, "_after_enqueue") as hook:
            self.ok("POST", "/api/projects/%s/orders" % NAME, self.order_dict(), 201)
            self.ok("POST", self.order_url("fauna/lobo", "banner", "/attempts"), {}, 202)
        self.assertEqual(hook.call_count, 2)

    def order_dict(self):
        return dict(ORDER, key="fauna/lobo", profile="banner", count=1)


class MeasureTests(WriteBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()

    def test_bad_params(self):
        url = self.att(self.key, self.profile, 1, "/measure")
        for query, code in [("?zone=1,2,3&text=%23ffffff", "measure.bad_zone"), ("?zone=a,b,c,d&text=%23ffffff", "measure.bad_zone"),
                            ("?zone=0,0,10,10&text=nope", "measure.bad_hex"),
                            ("?zone=0,0,10,10", "api.bad_param"), ("?text=%23ffffff", "api.bad_param"),
                            ("?raw=2", "api.bad_param")]:
            resp, payload = self.get(url + query)
            self.err(resp, payload, 400, code)
        resp, payload = self.get(self.att(self.key, self.profile, 9, "/measure"))
        self.err(resp, payload, 404, "order.attempt_unknown")

    @unittest.skipUnless(TOOLS, "hacen falta ffmpeg y rsvg-convert")
    def test_measure_and_zone_outside(self):
        url = self.att(self.key, self.profile, 1, "/measure")
        got = self.ok("GET", url + "?zone=0,0,10,10&text=%23ffffff")
        self.assertIn("contrast", got)
        self.assertIn("yavg", got)
        resp, payload = self.get(url + "?zone=0,0,99999,10&text=%23ffffff")
        self.err(resp, payload, 400, "measure.zone_outside")

    def test_busy_semaphore_gives_409(self):
        url = self.att(self.key, self.profile, 1, "/measure")
        old = server.HEAVY_WAIT_S
        server.HEAVY_WAIT_S = 0.1
        self.addCleanup(setattr, server, "HEAVY_WAIT_S", old)
        self.assertTrue(server._HEAVY.acquire(timeout=1))
        try:
            resp, payload = self.get(url)
            self.err(resp, payload, 409, "measure.busy")
            self.bad("POST", self.att(self.key, self.profile, 1, "/compose"), {}, 409, "compose.busy")
        finally:
            server._HEAVY.release()

    def test_heavy_serialises_two_tasks(self):
        server.HEAVY_WAIT_S = 5
        self.addCleanup(setattr, server, "HEAVY_WAIT_S", 60.0)
        seen, errors = [], []

        def task():
            try:
                with server._heavy("measure.busy"):
                    seen.append("in")
                    threading.Event().wait(0.1)
                    seen.append("out")
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)
        threads = [threading.Thread(target=task) for _ in range(2)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual((seen, errors), (["in", "out", "in", "out"], []))


class ComposeTests(WriteBase):
    def setUp(self):
        super().setUp()
        (self.root / "t.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"/>')
        self.key, self.profile = self.make_order(profile="og", count=1)
        self.url = self.att(self.key, self.profile, 1, "/compose")

    def test_busy_when_the_lock_is_taken(self):
        with fsutil.try_lock(orders.compose_lock_path(NAME, self.key, self.profile, 1)) as taken:
            self.assertTrue(taken)
            self.bad("POST", self.url, {}, 409, "compose.busy")

    def test_bad_text_and_attempt(self):
        self.bad("POST", self.url, {"text": "x"}, 400, "api.bad_param")
        self.bad("POST", self.url, {"text": {"title": 3}}, 400, "api.bad_param")
        self.bad("POST", self.att(self.key, self.profile, 9, "/compose"), {}, 404, "order.attempt_unknown")

    @unittest.skipUnless(TOOLS, "hacen falta ffmpeg y rsvg-convert")
    def test_compose_equals_the_cli(self):
        got = self.ok("POST", self.url, {"text": {"title": "Hola"}})
        cli = self.cli_json("compose", NAME, self.key, self.profile, "1", "--text", "title=Hola")
        self.assertEqual(got["id"], cli["id"])
        self.assertEqual(sorted(got), sorted(cli))
