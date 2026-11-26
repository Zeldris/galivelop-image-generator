"""0.8.0 step 3: failures of brand orders, the troubleshooting block, rows, `extend` and `known` (core, API and CLI)."""
import contextlib
import io
import json
import unittest
from unittest import mock

from gimg.errors import GimgError
from gimg import brandsheet, cli, failures, orders, queue, worker
from tests.test_batches import free
from tests.test_brand_orders import CoreBase, SHEET, brand_order
from tests.test_brandsheet import SUBJECT
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase

P, K, PR = "proj", "portada/uno", "banner"
REASON = {"trait": "horizon"}


class FailBase(CoreBase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv) + ["--lang", "en"])
        return code, out.getvalue(), err.getvalue()

    def made(self, key=K, **kw):
        """A brand order whose first batch (count 2) has been generated; returns the id of that batch."""
        entries, _, _ = self.submit(brand_order(key=key, **kw))
        worker.run()
        return entries[0]["batch"]["id"]

    def more(self, key=K, count=1):
        entries, _, _ = queue.new_attempts_checked(P, key, PR, count)
        worker.run()
        return entries[0]["batch"]["id"]

    def fail_it(self, batch, key=K):
        return failures.fail_batch(P, key, PR, batch, REASON)

    def block(self, key=K):
        batch = self.made(key)
        self.fail_it(batch, key)
        self.fail_it(self.more(key), key)
        self.fail_it(self.more(key), key)
        return key

    def order(self, key=K):
        return failures.view(orders.get(P, key, PR))


class Counter(FailBase):
    def test_old_order_without_keys_reads_as_zero(self):
        self.made()
        stored = orders.get(P, K, PR)
        self.assertNotIn("failures", stored)
        view = failures.view(stored)
        self.assertEqual(view["failures"], {"count": 0, "limit": 3, "reasons": []})
        self.assertEqual(view["troubleshooting"], {"state": "open"})

    def test_ninguno_vale_counts_one_per_batch_and_discards_it(self):
        batch = self.made()
        got = self.fail_it(batch)
        self.assertEqual(got["failures"]["count"], 1)
        self.assertEqual(got["failures"]["limit"], 3)
        [why] = got["failures"]["reasons"]
        self.assertEqual((why["batch"], why["trait"]), (batch, "horizon"))
        order = orders.get(P, K, PR)
        self.assertEqual([a["state"] for a in order["attempts"]], ["discarded", "discarded"])
        self.assertTrue(order["batches"][0]["failed"])
        self.assertEqual(order["batches"][0]["reason"], REASON)
        self.assertEqual(self.err(self.fail_it, batch).code, "order.batch_failed")
        self.assertEqual(self.order()["failures"]["count"], 1)

    def test_reason_must_name_a_trait_of_the_sheet_or_other_with_text(self):
        batch = self.made()
        for bad in ({}, {"trait": "nope"}, {"trait": "other"}, {"text": "x"}, {"trait": "horizon", "text": 3}, "horizon"):
            with self.subTest(reason=bad):
                self.assertEqual(self.err(failures.fail_batch, P, K, PR, batch, bad).code, "order.reason_invalid")
        self.assertEqual(self.order()["failures"]["count"], 0)
        got = failures.fail_batch(P, K, PR, batch, {"trait": "other", "text": "looks flat"})
        self.assertEqual(got["failures"]["reasons"][0]["text"], "looks flat")
        self.assertEqual(self.err(failures.fail_batch, P, K, PR, 99, REASON).code, "order.batch_unknown")

    def test_free_orders_do_not_count(self):
        entries, _, _ = self.submit(free(count=2))
        worker.run()
        self.assertEqual(self.err(failures.fail_batch, P, "libre", PR, entries[0]["batch"]["id"], REASON).code,
                         "order.not_brand")
        orders.mark(P, "libre", PR, 1, "discarded")
        orders.mark(P, "libre", PR, 2, "discarded")
        self.assertNotIn("failures", orders.get(P, "libre", PR))

    def test_no_with_reason_on_every_attempt_of_a_batch_is_one_failure(self):
        self.made()
        orders.mark(P, K, PR, 1, "discarded", reason=REASON)
        self.assertEqual(self.order()["failures"]["count"], 0)  # one attempt is not the batch
        got = orders.mark(P, K, PR, 2, "discarded", reason={"trait": "other", "text": "no"})
        self.assertEqual(got["reason"], {"trait": "other", "text": "no"})
        view = self.order()
        self.assertEqual(view["failures"]["count"], 1)
        self.assertEqual(view["failures"]["reasons"][0]["trait"], "other")
        orders.mark(P, K, PR, 2, "candidate")  # taking it back does not count again nor keep the reason
        self.assertNotIn("reason", orders.get(P, K, PR)["attempts"][1])
        orders.mark(P, K, PR, 2, "discarded")
        self.assertEqual(self.order()["failures"]["count"], 1)

    def test_a_discard_without_reason_still_counts_the_batch(self):
        self.made()
        orders.mark(P, K, PR, 1, "discarded")
        orders.mark(P, K, PR, 2, "discarded")
        view = self.order()
        self.assertEqual(view["failures"]["count"], 1)
        self.assertNotIn("trait", view["failures"]["reasons"][0])

    def test_reason_only_with_discarded_and_validated(self):
        self.made()
        self.assertEqual(self.err(orders.mark, P, K, PR, 1, "candidate", reason=REASON).code, "order.reason_invalid")
        self.assertEqual(self.err(orders.mark, P, K, PR, 1, "discarded", reason={"trait": "zzz"}).code,
                         "order.reason_invalid")

    def test_cancelled_and_technical_failures_do_not_count(self):
        entries, _, _ = self.submit(brand_order())
        queue.cancel_batch(entries[0]["batch"]["id"])
        self.assertEqual(self.order()["failures"]["count"], 0)
        entries, _, _ = queue.new_attempts_checked(P, K, PR, 2)
        queue.claim()
        queue.finish(entries[0]["id"], "failed", queue.make_error("engine.failed"))
        self.assertEqual(queue.get(entries[0]["id"])["state"], "failed")
        self.assertEqual(self.order()["failures"]["count"], 0)

    def test_score_of_five_or_more_resets_and_less_does_not(self):
        batch = self.made()
        self.fail_it(batch)
        self.assertEqual(failures.reset_on_score(P, K, PR, {"value": 4.9}), False)
        self.assertEqual(self.order()["failures"]["count"], 1)
        self.assertEqual(failures.reset_on_score(P, K, PR, {"value": 5}), True)
        self.assertEqual(self.order()["failures"], {"count": 0, "limit": 3, "reasons": []})
        self.assertEqual(failures.reset_on_score(P, K, PR, None), False)

    def test_worker_resets_on_a_score_of_five(self):
        self.fail_it(self.made())
        real = orders.add_attempt

        def scored(project, key, profile, spec, entry_id=None):
            attempt_id = real(project, key, profile, spec, entry_id=entry_id)
            orders._modify(project, key, profile, lambda o: o["attempts"][-1].update(score={"value": 5.5}))
            return attempt_id

        queue.new_attempts_checked(P, K, PR, 1)
        with mock.patch.object(orders, "add_attempt", scored):
            worker.run()
        self.assertEqual(self.order()["failures"]["count"], 0)

    def test_changing_the_subject_resets(self):
        self.fail_it(self.made())
        queue.new_attempts_checked(P, K, PR, 1)  # same subject: kept
        self.assertEqual(self.order()["failures"]["count"], 1)
        queue.new_attempts_checked(P, K, PR, 1, subject=SUBJECT.replace("compass rose", "lighthouse"))
        self.assertEqual(self.order()["failures"], {"count": 0, "limit": 3, "reasons": []})

    def test_limit_is_configurable(self):
        path = self.tmp / "proj" / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["brand"]["failureLimit"] = 1
        path.write_text(json.dumps(cfg))
        got = self.fail_it(self.made())
        self.assertEqual(got["failures"]["limit"], 1)
        self.assertEqual(got["troubleshooting"]["state"], "blocked")


class Blocking(FailBase):
    def test_third_failure_blocks_attempts_and_submit(self):
        self.made()
        self.fail_it(1)
        self.assertEqual(self.order()["troubleshooting"]["state"], "open")
        self.fail_it(self.more())
        got = self.fail_it(self.more())
        self.assertEqual(got["troubleshooting"]["state"], "blocked")
        exc = self.err(queue.new_attempts_checked, P, K, PR, 1)
        self.assertEqual(exc.code, "order.troubleshooting")
        exc = self.err(self.submit, brand_order())
        self.assertEqual(exc.code, "order.troubleshooting")
        self.assertEqual(self.err(queue.new_attempts_checked, P, K, PR, 1,
                                  subject=SUBJECT.replace("compass rose", "lighthouse")).code, "order.troubleshooting")
        self.assertEqual(queue.list_entries(["queued"]), [])

    def test_queued_entries_of_a_blocked_order_are_held(self):
        self.made()
        self.fail_it(1)
        queued, _, _ = queue.new_attempts_checked(P, K, PR, 2)
        other, _, _ = self.submit(brand_order(key="otra/pieza"))
        # block the first order through two more failed batches
        for _ in range(2):
            orders._modify(P, K, PR, lambda o: orders.add_failure(o, P, batch=0, reason=REASON))
        held = [queue.entry_view(e).get("held") for e in queue.list_entries(["queued"])]
        self.assertEqual(held, ["troubleshooting", "troubleshooting", None, None])
        self.assertEqual(queue.claim()["key"], "otra/pieza")  # the held ones are skipped
        self.assertEqual(queue.claim()["key"], "otra/pieza")
        self.assertIsNone(queue.claim())
        self.assertIsNone(queue.next_queued())
        self.assertEqual([queue.get(e["id"])["state"] for e in queued], ["queued", "queued"])
        self.assertEqual(len(queue.cancel_batch(queued[0]["batch"]["id"])), 2)  # cancelling them works

    def test_free_order_is_never_held(self):
        entries, _, _ = self.submit(free(count=2))
        self.assertNotIn("held", queue.entry_view(entries[0]))

    def test_old_queue_entries_without_batch_or_mode_are_not_held(self):
        self.assertIsNone(failures.held_entry({"project": P, "key": K, "profile": PR, "state": "queued", "id": 1}))

    def test_switching_to_free_unblocks(self):
        self.block()
        orders.apply_changes(P, K, PR, {"mode": "free"})
        self.assertEqual(self.order()["troubleshooting"]["state"], "open")


class Rows(FailBase):
    ROW = {"key": K, "profile": PR, "problem": "the islet keeps coming out as a flat disc",
           "attempts": [1, 2], "redesign": "describe it as a cliff from the side", "terms": ["islet", "foundations"]}

    def test_row_resets_counter_and_releases(self):
        self.block()
        queued = [e for e in queue.list_entries(["queued"])]
        self.assertEqual(queued, [])
        row = failures.add_row(P, self.ROW)
        self.assertEqual(row["piece"], "cover")
        self.assertEqual((row["key"], row["problem"], row["attempts"], row["terms"]),
                         (K, self.ROW["problem"], [1, 2], ["islet", "foundations"]))
        self.assertIn("at", row)
        self.assertEqual(row["by"], "person")
        view = self.order()
        self.assertEqual(view["failures"]["count"], 0)
        self.assertEqual(view["troubleshooting"]["state"], "open")
        self.assertEqual(view["troubleshooting"]["row"]["problem"], self.ROW["problem"])
        queue.new_attempts_checked(P, K, PR, 1)  # open again

    def test_row_releases_held_entries(self):
        self.made()
        self.fail_it(1)
        queue.new_attempts_checked(P, K, PR, 1)
        for _ in range(2):
            orders._modify(P, K, PR, lambda o: orders.add_failure(o, P, batch=0, reason=REASON))
        self.assertIsNone(queue.claim())
        failures.add_row(P, self.ROW)
        self.assertEqual(queue.claim()["key"], K)

    def test_validation(self):
        self.made()
        row = self.ROW
        for name, bad, code in (("problem", "", "api.bad_param"), ("problem", 3, "api.bad_param"),
                                ("attempts", "1", "api.bad_param"), ("attempts", [True], "api.bad_param"),
                                ("attempts", [99], "order.attempt_unknown"), ("terms", "x", "api.bad_param"),
                                ("terms", [""], "api.bad_param"), ("redesign", 1, "api.bad_param"),
                                ("by", 1, "api.bad_param"), ("key", "nope/none", "order.unknown")):
            with self.subTest(name=name, bad=bad):
                self.assertEqual(self.err(failures.add_row, P, dict(row, **{name: bad})).code, code)
        self.assertEqual(self.err(failures.add_row, P, dict(row, extra=1)).code, "api.bad_param")
        missing = dict(row)
        del missing["problem"]
        self.assertEqual(self.err(failures.add_row, P, missing).code, "api.bad_param")
        self.assertNotIn("troubleshooting", orders.get(P, K, PR))

    def test_row_on_a_free_order_is_not_brand(self):
        self.submit(free(count=1))
        self.assertEqual(self.err(failures.add_row, P, dict(self.ROW, key="libre")).code, "order.not_brand")

    def test_list_gathers_every_order_and_writes_the_markdown(self):
        self.made()
        self.made("otra/pieza")
        failures.add_row(P, self.ROW)
        failures.add_row(P, dict(self.ROW, key="otra/pieza", problem="second", terms=[], by="agent"))
        rows = failures.list_rows(P)
        self.assertEqual({(r["key"], r["profile"]) for r in rows}, {(K, PR), ("otra/pieza", PR)})
        self.assertEqual({r["key"]: r["by"] for r in rows}, {K: "person", "otra/pieza": "agent"})
        text = failures.markdown_path(P).read_text(encoding="utf-8")
        self.assertIn(self.ROW["problem"], text)
        self.assertIn("second", text)
        self.assertIn("islet", text)

    def test_known_terms_in_the_prompt_response(self):
        self.made()
        self.assertEqual(brandsheet.prompt_response(P, "cover", SUBJECT)["known"], [])
        row = failures.add_row(P, self.ROW)
        res = brandsheet.prompt_response(P, "cover", "A stone islet with only the foundations showing")
        self.assertEqual([k["term"] for k in res["known"]], ["islet", "foundations"])
        self.assertEqual(res["known"][0]["row"]["problem"], row["problem"])
        res = brandsheet.prompt_response(P, "cover", "A lighthouse and the isletted coast")  # whole words only
        self.assertEqual(res["known"], [])
        res = brandsheet.prompt_response(P, "cover", "An ISLET")
        self.assertEqual([k["term"] for k in res["known"]], ["islet"])


class Extend(FailBase):
    def test_extend_needs_a_blocked_order(self):
        self.made()
        self.assertEqual(self.err(failures.extend, P, K, PR).code, "order.not_blocked")

    def test_only_one_extension_per_failure_cycle(self):
        self.block()
        failures.extend(P, K, PR)
        self.more()  # uses it and fails again
        order = orders.get(P, K, PR)
        self.assertFalse(order["troubleshooting"]["extendPending"])
        self.assertTrue(failures.view(order)["troubleshooting"]["extensionUsed"])
        self.assertEqual(self.err(failures.extend, P, K, PR).code, "order.extend_used")

    def test_a_reset_of_the_counter_allows_an_extension_again(self):
        self.block()
        failures.extend(P, K, PR)
        orders._modify(P, K, PR, orders.reset_failures)
        self.assertNotIn("extensionUsed", failures.view(orders.get(P, K, PR))["troubleshooting"])

    def test_one_more_batch_runs_and_is_noted(self):
        self.block()
        got = failures.extend(P, K, PR)
        self.assertEqual(got["troubleshooting"]["state"], "extended")
        self.assertEqual(self.err(failures.extend, P, K, PR).code, "order.extend_pending")
        extra = self.more()  # runs: not held
        self.assertEqual(orders.get(P, K, PR)["attempts"][-1]["batch"], extra)
        order = orders.get(P, K, PR)
        self.assertEqual(len(order["troubleshooting"]["extensions"]), 1)
        self.assertEqual(order["troubleshooting"]["extensions"][0]["batch"], extra)
        self.assertEqual(self.order()["troubleshooting"]["state"], "blocked")  # still blocked after it
        self.assertEqual(self.err(queue.new_attempts_checked, P, K, PR, 1).code, "order.troubleshooting")

    def test_extension_does_not_release_the_older_held_entries(self):
        self.made()
        self.fail_it(1)
        old, _, _ = queue.new_attempts_checked(P, K, PR, 1)
        for _ in range(2):
            orders._modify(P, K, PR, lambda o: orders.add_failure(o, P, batch=0, reason=REASON))
        failures.extend(P, K, PR)
        new, _, _ = queue.new_attempts_checked(P, K, PR, 1)
        self.assertEqual(queue.claim()["id"], new[0]["id"])
        self.assertIsNone(queue.claim())
        self.assertEqual(queue.entry_view(queue.get(old[0]["id"]))["held"], "troubleshooting")


class Derived(FailBase):
    def test_a_derived_attempt_inherits_mode_and_sheet_version(self):
        from gimg import crop
        self.made()
        order = orders.get(P, K, PR)
        w, h = order["attempts"][0]["params"]["width"], order["attempts"][0]["params"]["height"]
        res = crop.crop(P, K, PR, 1, [0, 0, w, h])
        made = res["attempt"]
        self.assertEqual((made["mode"], made["sheetVersion"]), ("brand", order["sheetVersion"]))

    def test_a_derived_attempt_of_a_free_one_stays_free(self):
        from gimg import crop
        self.submit(free(count=1))
        worker.run()
        a = orders.get(P, "libre", PR)["attempts"][0]
        res = crop.crop(P, "libre", PR, 1, [0, 0, a["params"]["width"], a["params"]["height"]])
        self.assertEqual(res["attempt"]["mode"], "free")
        self.assertNotIn("sheetVersion", res["attempt"])


class FailuresApi(WriteBase):
    def setUp(self):
        super().setUp()
        (self.root / "marca.json").write_text(json.dumps(SHEET))
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["brand"] = {"sheet": "marca.json"}
        path.write_text(json.dumps(cfg))
        self.ok("POST", self.orders_url(), brand_order(), 201)
        self.cli("work")

    def batch(self, tail):
        return self.order_url("portada/uno", "banner", "/batches/1" + tail)

    def test_fail_route_and_order_view(self):
        self.bad("POST", self.batch("/fail"), {}, 400, "api.bad_param")
        self.bad("POST", self.batch("/fail"), {"reason": {"trait": "zzz"}}, 400, "order.reason_invalid")
        self.bad("POST", self.order_url("portada/uno", "banner", "/batches/9/fail"), {"reason": REASON}, 404,
                 "order.batch_unknown")
        got = self.ok("POST", self.batch("/fail"), {"reason": REASON})
        self.assertEqual(got["failures"]["count"], 1)
        self.bad("POST", self.batch("/fail"), {"reason": REASON}, 409, "order.batch_failed")
        shown = self.ok("GET", self.order_url("portada/uno", "banner"))
        self.assertEqual(shown["failures"]["count"], 1)
        self.assertEqual(shown["troubleshooting"], {"state": "open"})

    def test_mark_with_reason(self):
        got = self.ok("POST", self.att("portada/uno", "banner", 1, "/mark"), {"state": "discarded", "reason": REASON})
        self.assertEqual(got["reason"], REASON)
        self.bad("POST", self.att("portada/uno", "banner", 1, "/mark"), {"state": "discarded", "reason": 3}, 400,
                 "order.reason_invalid")

    def test_block_extend_and_rows(self):
        url = "/api/projects/%s/troubleshooting" % NAME
        self.assertEqual(self.ok("GET", url), [])
        self.bad("POST", self.order_url("portada/uno", "banner", "/troubleshooting/extend"), {}, 409, "order.not_blocked")
        self.ok("POST", self.batch("/fail"), {"reason": REASON})
        # two more failed batches, through the core
        for _ in range(2):
            orders._modify(NAME, "portada/uno", "banner", lambda o: orders.add_failure(o, NAME, batch=0, reason=REASON))
        shown = self.ok("GET", self.order_url("portada/uno", "banner"))
        self.assertEqual(shown["troubleshooting"]["state"], "blocked")
        got = self.bad("POST", self.order_url("portada/uno", "banner", "/attempts"), {}, 409, "order.troubleshooting")
        self.assertEqual(got["params"]["limit"], 3)
        self.bad("POST", self.orders_url(), brand_order(), 409, "order.troubleshooting")
        self.assertEqual(self.ok("POST", self.order_url("portada/uno", "banner", "/troubleshooting/extend"), {})
                         ["troubleshooting"]["state"], "extended")
        self.bad("POST", self.order_url("portada/uno", "banner", "/troubleshooting/extend"), {}, 409,
                 "order.extend_pending")
        row = self.ok("POST", url, {"key": "portada/uno", "profile": "banner", "problem": "flat", "attempts": [1],
                                    "redesign": "side view", "terms": ["islet"]}, 201)
        self.assertEqual((row["piece"], row["by"]), ("cover", "person"))
        self.assertEqual([r["key"] for r in self.ok("GET", url)], ["portada/uno"])
        self.assertEqual(self.ok("GET", self.order_url("portada/uno", "banner"))["failures"]["count"], 0)
        self.bad("POST", url, {"key": "portada/uno", "profile": "banner"}, 400, "api.bad_param")
        self.bad("POST", url, {"key": "x/y", "profile": "banner", "problem": "p", "redesign": ""}, 404, "order.unknown")
        self.assertTrue(failures.markdown_path(NAME).is_file())

    def test_routes_start_the_worker(self):
        for _ in range(3):
            orders._modify(NAME, "portada/uno", "banner", lambda o: orders.add_failure(o, NAME, batch=0, reason=REASON))
        with mock.patch("gimg.server._after_enqueue") as after:
            self.ok("POST", self.order_url("portada/uno", "banner", "/troubleshooting/extend"), {})
            self.assertEqual(after.call_count, 1)
            self.ok("POST", "/api/projects/%s/troubleshooting" % NAME,
                    {"key": "portada/uno", "profile": "banner", "problem": "p"}, 201)
            self.assertEqual(after.call_count, 2)

    def test_queue_view_has_held_and_brand_prompt_known(self):
        for _ in range(3):
            orders._modify(NAME, "portada/uno", "banner", lambda o: orders.add_failure(o, NAME, batch=0, reason=REASON))
        entries = queue.list_entries()
        self.assertEqual(entries, [e for e in entries if e["state"] == "done"])
        failures.add_row(NAME, {"key": "portada/uno", "profile": "banner", "problem": "p", "redesign": "",
                                "terms": ["islet"]})
        got = self.ok("POST", "/api/projects/%s/brand/prompt" % NAME,
                      {"piece": "cover", "subject": "An islet at dawn"})
        self.assertEqual(got["known"][0]["term"], "islet")


class FailuresCli(FailBase):
    def test_commands(self):
        batch = self.made()
        code, out, err = self.run_cli("order", "fail", P, K, PR, str(batch), "--reason", "horizon", "--json")
        self.assertEqual((code, err), (0, ""), out)
        self.assertEqual(json.loads(out)["failures"]["count"], 1)
        code, _, err = self.run_cli("order", "fail", P, K, PR, str(batch), "--reason", "horizon")
        self.assertEqual(code, 1)
        self.assertIn("already", err)
        code, _, err = self.run_cli("order", "fail", P, K, PR, "7", "--reason", "other")  # other needs --note
        self.assertEqual(code, 1)
        code, out, err = self.run_cli("attempt", "mark", P, K, PR, "1", "candidate", "--reason", "horizon")
        self.assertEqual(code, 1)
        for _ in range(2):
            orders._modify(P, K, PR, lambda o: orders.add_failure(o, P, batch=0, reason=REASON))
        code, out, err = self.run_cli("attempt", "new", P, K, PR)
        self.assertEqual(code, 1)
        self.assertIn("troubleshooting", err)
        code, out, err = self.run_cli("troubleshoot", "extend", P, K, PR, "--json")
        self.assertEqual((code, json.loads(out)["troubleshooting"]["state"]), (0, "extended"), err)
        code, out, err = self.run_cli("troubleshoot", "add", P, K, PR, "--problem", "flat", "--attempt", "1",
                                      "--term", "islet", "--term", "rock", "--redesign", "side", "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["terms"], ["islet", "rock"])
        code, out, _ = self.run_cli("troubleshoot", "list", P, "--json")
        self.assertEqual([r["problem"] for r in json.loads(out)], ["flat"])
        code, out, _ = self.run_cli("troubleshoot", "list", P)
        self.assertIn("flat", out)
        code, out, _ = self.run_cli("brand", "prompt", "--project", P, "--piece", "cover", "--subject", "An islet", "--json")
        self.assertEqual(json.loads(out)["known"][0]["term"], "islet")

    def test_order_show_json_has_the_view(self):
        self.made()
        code, out, _ = self.run_cli("order", "show", P, K, PR, "--json")
        self.assertEqual(json.loads(out)["failures"]["count"], 0)
        self.assertEqual(json.loads(out)["troubleshooting"], {"state": "open"})


class ReviewFixes(FailBase):
    """Findings of the block review of 0.8.0 steps 3-4."""
    ROW = {"key": K, "profile": PR, "problem": "flat", "attempts": [1], "redesign": "", "terms": ["islet"]}

    def held_one(self):
        self.made()
        self.fail_it(1)
        queue.new_attempts_checked(P, K, PR, 1)
        for _ in range(2):
            orders._modify(P, K, PR, lambda o: orders.add_failure(o, P, batch=0, reason=REASON))

    def test_free_is_the_way_out_of_a_block(self):
        self.block()
        entries, _, _ = queue.new_attempts_checked(P, K, PR, 1, mode="free", prompt="x")
        self.assertEqual(entries[0]["mode"], "free")
        self.assertEqual(self.order()["troubleshooting"], {"state": "open"})

    def test_resubmitting_a_blocked_order_as_free_is_not_refused(self):
        self.block()
        queue.submit_order_checked(P, free(key=K))
        self.assertEqual(self.order()["mode"], "free")

    def test_a_restart_clears_the_pending_extension(self):
        self.block()
        failures.extend(P, K, PR)
        self.assertTrue(failures.reset_on_score(P, K, PR, {"value": orders.RESET_SCORE}))
        for _ in range(3):
            orders._modify(P, K, PR, lambda o: orders.add_failure(o, P, batch=0, reason=REASON))
        self.assertEqual(self.order()["troubleshooting"]["state"], "blocked")

    def test_markdown_failures_do_not_fail_the_row(self):
        from gimg.errors import PathError
        self.made()
        for exc in (GimgError("order.corrupt", path="x"), PathError("path.outside", path="x")):
            with self.subTest(exc=type(exc).__name__), mock.patch.object(failures, "markdown", side_effect=exc):
                self.assertEqual(failures.add_row(P, dict(self.ROW))["problem"], "flat")
        self.assertEqual(len(failures.list_rows(P)), 2)

    def test_unreadable_order_does_not_break_the_prompt_response(self):
        self.made()
        self.made("otra/pieza")
        failures.add_row(P, dict(self.ROW))
        path = orders._order_file(P, "otra/pieza", PR)
        path.write_text("{ not json", encoding="utf-8")
        res = brandsheet.prompt_response(P, "cover", "An islet")
        self.assertEqual([k["term"] for k in res["known"]], ["islet"])

    def test_known_terms_once_per_term(self):
        self.made()
        failures.add_row(P, dict(self.ROW))
        failures.add_row(P, dict(self.ROW, terms=["Islet"]))
        self.assertEqual(len(failures.known_terms(P, "an islet")), 1)

    def test_cli_row_starts_the_worker(self):
        self.held_one()
        with mock.patch.object(cli, "_autostart") as start:
            code, _, err = self.run_cli("troubleshoot", "add", P, K, PR, "--problem", "flat")
        self.assertEqual((code, err), (0, ""))
        start.assert_called_once()

    def test_cli_extend_starts_the_worker_for_what_is_runnable(self):
        self.block()
        self.submit(free(key="libre", count=1))  # a runnable entry is waiting
        with mock.patch.object(cli, "_autostart") as start:
            code, _, err = self.run_cli("troubleshoot", "extend", P, K, PR)
        self.assertEqual((code, err), (0, ""))
        start.assert_called_once()

    def test_resume_ignores_held_entries(self):
        self.held_one()
        queue.pause()
        with mock.patch.object(cli, "_autostart") as start:
            code, _, _ = self.run_cli("queue", "resume")
        self.assertEqual(code, 0)
        start.assert_not_called()

    def test_extension_is_not_lost_when_the_enqueue_fails(self):
        self.block()
        failures.extend(P, K, PR)
        with mock.patch.object(queue, "enqueue", side_effect=GimgError("queue.corrupt", path="x")):
            self.assertEqual(self.err(queue.new_attempts_checked, P, K, PR, 1).code, "queue.corrupt")
        self.assertEqual(self.order()["troubleshooting"]["state"], "extended")

    def test_a_single_entry_extension_notes_its_id(self):
        self.block()
        failures.extend(P, K, PR)
        [spec] = orders.attempt_specs(P, K, PR, 1)
        spec.update(mode="free", extended=True)
        [entry] = queue.enqueue(P, K, PR, [spec])
        self.assertNotIn("batch", entry)
        self.assertEqual(orders.get(P, K, PR)["troubleshooting"]["extensions"][-1]["batch"], entry["id"])


if __name__ == "__main__":
    unittest.main()
