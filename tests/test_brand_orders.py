"""0.8.0 step 1: brand-mode orders (core, API and CLI): the sheet assembles the prompt, the lint blocks it."""
import contextlib
import copy
import io
import json
import os
import unittest
from unittest import mock

from gimg import brandsheet as B, cli, orders, queue, server
from tests.test_brandsheet import PORTAL, SUBJECT, ZONE, Env
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase

SHEET = copy.deepcopy(PORTAL)
SHEET["pieceTypes"]["cover"]["profile"] = "banner"
SHEET["pieceTypes"]["icon"]["profile"] = "thumbnail"


def brand_order(**changes):
    return dict({"key": "portada/uno", "mode": "brand", "piece": "cover", "subject": SUBJECT, "cleanZone": ZONE},
                **changes)


class CoreBase(Env):
    def setUp(self):
        super().setUp()
        env = mock.patch.dict(os.environ, {"GIMG_ENGINE": "fake"})
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("GIMG_MACHINE_PROFILE", None)
        self.project("proj", SHEET)

    def submit(self, order, **kw):
        return queue.submit_order_checked("proj", order, **kw)

    def err(self, fn, *args, **kw):
        return self.code(fn, *args, **kw)


class Core(CoreBase):
    def test_brand_order_gets_prompt_profile_and_defaults_from_the_piece(self):
        entries, _, checks = self.submit(brand_order())
        built = B.assemble(B.resolve("proj"), "cover", SUBJECT, ZONE)["prompt"]
        order = orders.get("proj", "portada/uno", "banner")
        self.assertEqual((order["mode"], order["piece"], order["subject"], order["cleanZone"]),
                         ("brand", "cover", SUBJECT, ZONE))
        self.assertEqual(order["prompt"], built)
        self.assertEqual(order["sheetVersion"], B.resolve("proj")["version"])
        self.assertEqual(order["seed"], 42)
        self.assertEqual([e["seed"] for e in entries], [42, 43])  # count 2 from the piece type
        self.assertTrue(all(e["prompt"] == built for e in entries))  # no profile style after the sheet's prompt
        self.assertEqual({(e["mode"], e["sheetVersion"]) for e in entries}, {("brand", order["sheetVersion"])})
        self.assertTrue(checks and all(c["status"] != "error" for c in checks))

    def test_explicit_seed_count_and_profile_win_or_must_match(self):
        entries, _, _ = self.submit(brand_order(seed=5, count=1, profile="banner"))
        self.assertEqual([e["seed"] for e in entries], [5])
        self.assertEqual(self.err(self.submit, brand_order(key="x", profile="thumbnail")).code,
                         "order.profile_mismatch")

    def test_rejections_say_why(self):
        self.assertEqual(self.err(self.submit, brand_order(prompt="mine")).code, "order.brand_prompt")
        self.assertEqual(self.err(self.submit, brand_order(subject="   ")).code, "order.subject_required")
        no_subject = brand_order()
        del no_subject["subject"]
        self.assertEqual(self.err(self.submit, no_subject).code, "order.subject_required")
        no_piece = brand_order()
        del no_piece["piece"]
        self.assertEqual(self.err(self.submit, no_piece).code, "order.piece_required")
        self.assertEqual(self.err(self.submit, brand_order(piece="nope")).code, "brandsheet.unknown_piece")
        self.assertEqual(self.err(self.submit, brand_order(subject="x" * 4001)).code, "order.invalid")
        self.assertEqual(self.err(self.submit, brand_order(mode="other")).code, "order.invalid")

    def test_no_sheet_is_brand_no_sheet_and_free_has_no_checks(self):
        self.project("bare", rel=None)
        self.assertEqual(self.err(queue.submit_order_checked, "bare", brand_order()).code, "brand.no_sheet")
        _, _, checks = queue.submit_order_checked("bare", {"key": "a", "profile": "banner", "prompt": "a cat"})
        self.assertIsNone(checks)

    def test_blocked_prompt_stores_nothing_and_lists_the_failing_checks(self):
        exc = self.err(self.submit, brand_order(subject=SUBJECT + ", with a robot waving"))
        self.assertEqual(exc.code, "brand.blocked")
        self.assertIn("veto", [e.params["id"] for e in exc.errors])
        self.assertIn("robot", exc.message("en"))
        self.assertEqual(self.err(orders.get, "proj", "portada/uno", "banner").code, "order.unknown")

    def test_free_order_never_blocks_and_reports_warnings(self):
        entries, _, checks = self.submit({"key": "libre", "profile": "banner", "prompt": "a robot"})
        self.assertTrue(any(c["status"] == "warn" for c in checks))
        self.assertEqual(entries[0]["mode"], "free")
        self.assertNotIn("sheetVersion", entries[0])
        self.assertTrue(entries[0]["prompt"].startswith("a robot, "))  # style appended as always
        self.assertEqual(orders.get("proj", "libre", "banner")["mode"], "free")

    def test_client_cannot_set_sheet_version_or_mode_changes(self):
        self.submit(brand_order(sheetVersion="forged", modeChanges=[{"from": "brand", "to": "free", "at": "x"}]))
        order = orders.get("proj", "portada/uno", "banner")
        self.assertNotEqual(order["sheetVersion"], "forged")
        self.assertNotIn("modeChanges", order)

    def test_old_orders_read_as_free(self):
        self.submit({"key": "viejo", "profile": "banner", "prompt": "a cat"})
        entry = queue.list_entries()[0]
        self.assertEqual(entry.get("mode", "free"), "free")
        record = orders.add_attempt("proj", "viejo", "banner", {"seed": 1, "prompt": "p", "params": {"steps": 6}})
        self.assertEqual(orders.get("proj", "viejo", "banner")["attempts"][record - 1]["mode"], "free")

    def test_attempt_record_stores_mode_and_sheet_version(self):
        self.submit(brand_order(count=1))
        spec = orders.attempt_specs("proj", "portada/uno", "banner", 1)[0]
        self.assertEqual(spec["mode"], "brand")
        att = orders.add_attempt("proj", "portada/uno", "banner", spec)
        record = orders.get("proj", "portada/uno", "banner")["attempts"][att - 1]
        self.assertEqual((record["mode"], record["sheetVersion"]), ("brand", spec["sheetVersion"]))


class Attempts(CoreBase):
    def setUp(self):
        super().setUp()
        self.submit(brand_order(count=1))
        self.base = orders.get("proj", "portada/uno", "banner")

    def new(self, **kw):
        return queue.new_attempts_checked("proj", "portada/uno", "banner", 1, **kw)

    def test_new_subject_reassembles_and_updates_the_order(self):
        new = SUBJECT.replace("compass rose", "weather vane")
        entries, _, checks = self.new(subject=new)
        order = orders.get("proj", "portada/uno", "banner")
        self.assertEqual(order["subject"], new)
        self.assertEqual(order["prompt"], B.assemble(B.resolve("proj"), "cover", new, ZONE)["prompt"])
        self.assertEqual(entries[0]["prompt"], order["prompt"])
        self.assertEqual(entries[0]["mode"], "brand")
        self.assertTrue(checks)

    def test_clean_zone_can_be_cleared(self):
        self.new(clean_zone="")
        self.assertNotIn("cleanZone", orders.get("proj", "portada/uno", "banner"))

    def test_blocked_leaves_the_order_and_queue_alone(self):
        before = len(queue.list_entries())
        exc = self.err(self.new, subject=SUBJECT + " with a robot")
        self.assertEqual(exc.code, "brand.blocked")
        self.assertTrue(exc.errors)
        self.assertEqual(orders.get("proj", "portada/uno", "banner")["subject"], SUBJECT)
        self.assertEqual(len(queue.list_entries()), before)

    def test_prompt_on_a_brand_order_needs_mode_free(self):
        self.assertEqual(self.err(self.new, prompt="mine").code, "order.brand_prompt")
        self.assertEqual(self.err(self.new, mode="free").code, "order.mode_conflict")
        self.assertEqual(self.err(self.new, mode="free", prompt="mine", subject="x").code, "order.mode_conflict")
        self.assertEqual(self.err(self.new, mode="brand", prompt="mine").code, "order.brand_prompt")
        self.assertEqual(orders.get("proj", "portada/uno", "banner").get("modeChanges"), None)

    def test_pasar_a_imagen_libre(self):
        entries, _, checks = self.new(prompt="a plain fox", mode="free")
        order = orders.get("proj", "portada/uno", "banner")
        self.assertEqual((order["mode"], order["prompt"]), ("free", "a plain fox"))
        self.assertEqual([(c["from"], c["to"]) for c in order["modeChanges"]], [("brand", "free")])
        self.assertTrue(order["modeChanges"][0]["at"])
        self.assertTrue(entries[0]["prompt"].startswith("a plain fox, "))  # style appended again
        self.assertEqual(entries[0]["mode"], "free")
        self.assertTrue(checks)
        entries, _, _ = self.new(prompt="another")  # now a free order: a retouched prompt is fine
        self.assertEqual(entries[0]["mode"], "free")

    def test_free_order_takes_no_brand_fields(self):
        self.submit({"key": "libre", "profile": "banner", "prompt": "a cat"})
        for kw in ({"subject": "x"}, {"clean_zone": "x"}, {"mode": "brand"}):
            with self.subTest(kw=kw):
                exc = self.err(queue.new_attempts_checked, "proj", "libre", "banner", 1, **kw)
                self.assertEqual(exc.code, "order.not_brand")
        entries, _, checks = queue.new_attempts_checked("proj", "libre", "banner", 1, prompt="b", mode="free")
        self.assertEqual(entries[0]["mode"], "free")
        self.assertIsNotNone(checks)


class Api(WriteBase):
    def setUp(self):
        super().setUp()
        sheet = copy.deepcopy(SHEET)
        sheet["pieceTypes"]["cover"]["profile"] = "banner"
        (self.root / "marca.json").write_text(json.dumps(sheet))
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["brand"] = {"sheet": "marca.json"}
        path.write_text(json.dumps(cfg))

    def test_brand_submit_201_with_checks_and_the_worker_records_the_mode(self):
        got = self.ok("POST", self.orders_url(), brand_order(), 201)
        self.assertEqual(got["order"]["mode"], "brand")
        self.assertEqual(got["order"]["profile"], "banner")
        self.assertEqual(len(got["entries"]), 2)
        self.assertTrue(got["checks"])
        self.cli("work")
        order = orders.get(NAME, "portada/uno", "banner")
        self.assertEqual({(a["mode"], a["sheetVersion"]) for a in order["attempts"]},
                         {("brand", order["sheetVersion"])})

    def test_blocked_is_422_with_the_checks(self):
        resp, payload = self.send("POST", self.orders_url(), brand_order(subject=SUBJECT + " with a robot"))
        body = self.err(resp, payload, 422, "brand.blocked")
        self.assertTrue(body["errors"])
        self.assertIn("robot", " ".join(body["errors"]))

    def test_brand_rejections_have_their_status(self):
        self.bad("POST", self.orders_url(), brand_order(prompt="mine"), 400, "order.brand_prompt")
        self.bad("POST", self.orders_url(), brand_order(subject=" "), 400, "order.subject_required")
        self.bad("POST", self.orders_url(), brand_order(profile="thumbnail"), 400, "order.profile_mismatch")

    def test_no_sheet_is_422(self):
        self.root.joinpath("galivelop-images.json").write_text(
            json.dumps({k: v for k, v in json.loads(self.root.joinpath("galivelop-images.json").read_text()).items()
                        if k != "brand"}))
        self.bad("POST", self.orders_url(), brand_order(), 422, "brand.no_sheet")

    def test_free_order_reports_checks_only_with_a_sheet(self):
        got = self.ok("POST", self.orders_url(), self.order(key="libre"), 201)
        self.assertIn("checks", got)
        self.assertTrue(all(c["status"] != "error" for c in got["checks"]))

    def test_attempts_route(self):
        self.ok("POST", self.orders_url(), brand_order(count=1), 201)
        url = self.order_url("portada/uno", "banner", "/attempts")
        got = self.ok("POST", url, {"subject": SUBJECT.replace("compass rose", "weather vane")}, 202)
        self.assertIn("weather vane", orders.get(NAME, "portada/uno", "banner")["prompt"])
        self.assertTrue(got["checks"])
        resp, payload = self.send("POST", url, {"subject": SUBJECT + " with a robot"})
        self.assertTrue(self.err(resp, payload, 422, "brand.blocked")["errors"])
        self.bad("POST", url, {"prompt": "mine"}, 400, "order.brand_prompt")
        self.bad("POST", url, {"subject": 3}, 400, "api.bad_param")
        self.ok("POST", url, {"prompt": "mine", "mode": "free"}, 202)
        self.assertEqual(orders.get(NAME, "portada/uno", "banner")["mode"], "free")
        self.bad("POST", url, {"subject": "x"}, 400, "order.not_brand")


class Cli(CoreBase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv) + ["--lang", "en"])
        return code, out.getvalue(), err.getvalue()

    def order_file(self, **changes):
        path = self.tmp / "o.json"
        path.write_text(json.dumps(brand_order(**changes)))
        return str(path)

    def test_order_submit_brand_and_blocked(self):
        code, out, err = self.run_cli("order", "submit", "proj", self.order_file(), "--json")
        self.assertEqual((code, err), (0, ""), out)
        self.assertIn("checks", json.loads(out))
        code, out, err = self.run_cli("order", "submit", "proj", self.order_file(key="otra", subject=SUBJECT + " robot"))
        self.assertEqual(code, 1)
        self.assertIn("robot", err)
        self.assertIn("vetoed", err)

    def test_attempt_new_subject_clean_zone_and_mode_free(self):
        self.run_cli("order", "submit", "proj", self.order_file(count=1))
        args = ("attempt", "new", "proj", "portada/uno", "banner")
        code, _, err = self.run_cli(*args, "--subject", "A small boat" + " " + SUBJECT, "--clean-zone", ZONE)
        self.assertEqual(code, 1, err)  # "boat" is vetoed
        self.assertIn("boat", err)
        code, _, err = self.run_cli(*args, "--subject", SUBJECT.replace("compass rose", "weather vane"))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.run_cli(*args, "--prompt", "mine")[0], 1)
        code, _, err = self.run_cli(*args, "--prompt", "mine", "--mode", "free")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(orders.get("proj", "portada/uno", "banner")["mode"], "free")


if __name__ == "__main__":
    unittest.main()
