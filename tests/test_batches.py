"""0.8.0 step 2: batches (the entries of one submit or one `attempts` call): record, move, cancel, stop on a high score."""
import contextlib
import copy
import io
import json
import unittest
from unittest import mock

from gimg import cli, orders, queue, worker
from tests.test_brand_orders import CoreBase, brand_order
from tests.test_brandsheet import SUBJECT
from tests.test_queue import QueueBase
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase
from tests.test_brand_orders import SHEET


def free(key="libre", **kw):
    return dict({"key": key, "profile": "banner", "prompt": "a cat"}, **kw)


class Batches(CoreBase):
    hold_worker_lock = QueueBase.hold_worker_lock

    def batch_of(self, entries):
        return [e.get("batch") for e in entries]

    def test_brand_submit_is_a_batch_even_of_one(self):
        entries, _, _ = self.submit(brand_order(count=1))
        self.assertEqual(entries[0]["batch"], {"id": entries[0]["id"], "index": 0, "size": 1})
        entries, _, _ = self.submit(brand_order(key="portada/dos"))
        self.assertEqual(self.batch_of(entries), [{"id": entries[0]["id"], "index": i, "size": 2} for i in (0, 1)])

    def test_order_records_the_batch(self):
        entries, _, checks = self.submit(brand_order())
        order = orders.get("proj", "portada/uno", "banner")
        [rec] = order["batches"]
        self.assertEqual((rec["id"], rec["size"], rec["mode"], rec["subject"], rec["cleanZone"]),
                         (entries[0]["id"], 2, "brand", order["subject"], order["cleanZone"]))
        self.assertEqual(rec["warnings"], [c for c in checks if c["status"] == "warn"])
        self.assertIn("createdAt", rec)

    def test_free_batch_only_when_more_than_one(self):
        [one], _, _ = self.submit(free(count=1))
        self.assertNotIn("batch", one)
        self.assertNotIn("batches", orders.get("proj", "libre", "banner"))
        entries, _, _ = self.submit(free(key="otra", count=3))
        self.assertEqual(self.batch_of(entries), [{"id": entries[0]["id"], "index": i, "size": 3} for i in range(3)])
        [rec] = orders.get("proj", "otra", "banner")["batches"]
        self.assertEqual((rec["mode"], rec["size"]), ("free", 3))
        self.assertNotIn("subject", rec)

    def test_attempts_call_makes_its_own_batch(self):
        self.submit(brand_order(count=1))
        entries, _, _ = queue.new_attempts_checked("proj", "portada/uno", "banner", 2)
        self.assertEqual(entries[0]["batch"], {"id": entries[0]["id"], "index": 0, "size": 2})
        [one], _, _ = queue.new_attempts_checked("proj", "portada/uno", "banner", 1)
        self.assertEqual(one["batch"]["size"], 1)
        self.assertEqual([b["size"] for b in orders.get("proj", "portada/uno", "banner")["batches"]], [1, 2, 1])

    def test_client_cannot_set_batches(self):
        self.submit(brand_order(batches=[{"id": 9}]))
        order = orders.get("proj", "portada/uno", "banner")
        self.assertEqual([b["id"] for b in order["batches"]], [1])

    def test_attempts_carry_their_batch(self):
        self.submit(brand_order(count=1))
        self.submit(free(count=1))
        worker.run()
        self.assertEqual(orders.get("proj", "portada/uno", "banner")["attempts"][0]["batch"], 1)
        self.assertNotIn("batch", orders.get("proj", "libre", "banner")["attempts"][0])

    def two_batches(self):
        a, _, _ = self.submit(brand_order(key="a/a"))      # ids 1, 2
        [s], _, _ = self.submit(free(key="s", count=1))    # id 3 (no batch)
        b, _, _ = self.submit(brand_order(key="b/b"))      # ids 4, 5
        return a, s, b

    def order_of(self):
        return [e["id"] for e in sorted(queue.list_entries(["queued"]), key=queue._pos)]

    def test_move_batch(self):
        self.two_batches()
        self.assertEqual(self.order_of(), [1, 2, 3, 4, 5])
        got = queue.move_batch(4, "top")
        self.assertEqual([e["id"] for e in got], [4, 5])
        self.assertEqual(self.order_of(), [4, 5, 1, 2, 3])
        queue.move_batch(4, "down")  # past the block of batch 1
        self.assertEqual(self.order_of(), [1, 2, 4, 5, 3])
        queue.move_batch(4, "down")  # past the single entry
        self.assertEqual(self.order_of(), [1, 2, 3, 4, 5])
        queue.move_batch(4, "down")  # already last
        self.assertEqual(self.order_of(), [1, 2, 3, 4, 5])
        queue.move_batch(4, "up")
        self.assertEqual(self.order_of(), [1, 2, 4, 5, 3])
        queue.move_batch(4, "up")
        self.assertEqual(self.order_of(), [4, 5, 1, 2, 3])
        queue.move_batch(4, "up")
        self.assertEqual(self.order_of(), [4, 5, 1, 2, 3])
        self.assertEqual(self.err(queue.move_batch, 4, "sideways").code, "queue.bad_move")
        self.assertEqual(self.err(queue.move_batch, 99, "top").code, "queue.batch_not_found")

    def test_move_batch_skips_running_entries(self):
        self.two_batches()
        self.hold_worker_lock()
        queue.claim()
        got = queue.move_batch(1, "down")
        self.assertEqual([e["id"] for e in got], [2])
        self.assertEqual(self.order_of(), [3, 2, 4, 5])
        queue.finish(1, "done")
        queue.cancel_batch(1)
        self.assertEqual(self.err(queue.move_batch, 1, "top").code, "queue.not_movable")

    def test_cancel_batch(self):
        self.two_batches()
        self.hold_worker_lock()
        queue.claim()
        got = queue.cancel_batch(1)
        self.assertEqual([(e["id"], e["state"], e["cancelRequested"]) for e in got],
                         [(1, "running", True), (2, "cancelled", False)])
        self.assertEqual(queue.get(4)["state"], "queued")
        self.assertEqual(self.err(queue.cancel_batch, 99).code, "queue.batch_not_found")
        queue.finish(1, "cancelled")
        self.assertEqual(self.err(queue.cancel_batch, 1).code, "queue.not_cancellable")

    def test_stop_batch_cancels_only_the_queued_ones(self):
        self.two_batches()
        self.hold_worker_lock()
        queue.claim()
        got = queue.stop_batch(1, 7)
        self.assertEqual([(e["id"], e["state"], e["stoppedBy"]) for e in got], [(2, "cancelled", 7)])
        self.assertEqual((queue.get(1)["state"], queue.get(4)["state"]), ("running", "queued"))
        self.assertEqual(queue.stop_batch(1, 7), [])

    def test_a_high_score_stops_the_rest_of_the_batch(self):
        self.submit(brand_order(key="a/a", count=3))
        real = orders.add_attempt

        def scored(project, key, profile, spec, entry_id=None):
            attempt_id = real(project, key, profile, spec, entry_id=entry_id)
            orders._modify(project, key, profile,
                           lambda o: o["attempts"][-1].update(score={"value": 9 if entry_id == 1 else 3}))
            return attempt_id

        with mock.patch.object(orders, "add_attempt", scored):
            worker.run()
        self.assertEqual([queue.get(i)["state"] for i in (1, 2, 3)], ["done", "cancelled", "cancelled"])
        self.assertEqual(queue.get(2)["stoppedBy"], 1)
        self.assertEqual(len(orders.get("proj", "a/a", "banner")["attempts"]), 1)

    def test_a_low_score_does_not_stop(self):
        self.submit(brand_order(key="a/a", count=2))
        real = orders.add_attempt

        def scored(project, key, profile, spec, entry_id=None):
            attempt_id = real(project, key, profile, spec, entry_id=entry_id)
            orders._modify(project, key, profile, lambda o: o["attempts"][-1].update(score={"value": 8.9}))
            return attempt_id

        with mock.patch.object(orders, "add_attempt", scored):
            worker.run()
        self.assertEqual([queue.get(i)["state"] for i in (1, 2)], ["done", "done"])


class BatchApi(WriteBase):
    def setUp(self):
        super().setUp()
        (self.root / "marca.json").write_text(json.dumps(SHEET))
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["brand"] = {"sheet": "marca.json"}
        path.write_text(json.dumps(cfg))

    def test_routes(self):
        got = self.ok("POST", self.orders_url(), brand_order(count=2), 201)
        self.assertEqual(got["entries"][1]["batch"], {"id": 1, "index": 1, "size": 2})
        self.assertEqual(got["order"]["batches"][0]["id"], 1)
        self.assertEqual(orders.get(NAME, "portada/uno", "banner")["batches"][0]["size"], 2)
        listed = self.ok("GET", "/api/queue")
        self.assertEqual(listed[0]["batch"]["id"], 1)
        self.bad("POST", "/api/queue/batches/1/move", {"to": "x"}, 400, "queue.bad_move")
        self.bad("POST", "/api/queue/batches/1/move", {}, 400, "api.bad_param")
        self.bad("POST", "/api/queue/batches/99/move", {"to": "top"}, 404, "queue.batch_not_found")
        self.bad("POST", "/api/queue/batches/99/cancel", {}, 404, "queue.batch_not_found")
        moved = self.ok("POST", "/api/queue/batches/1/move", {"to": "top"})
        self.assertEqual([e["id"] for e in moved["entries"]], [1, 2])
        done = self.ok("POST", "/api/queue/batches/1/cancel", {})
        self.assertEqual([e["state"] for e in done["entries"]], ["cancelled", "cancelled"])
        self.bad("POST", "/api/queue/batches/1/cancel", {}, 409, "queue.not_cancellable")
        self.bad("POST", "/api/queue/batches/1/move", {"to": "top"}, 409, "queue.not_movable")


class BatchCli(CoreBase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv) + ["--lang", "en"])
        return code, out.getvalue(), err.getvalue()

    def test_batch_flag(self):
        self.submit(brand_order(key="a/a"))
        self.submit(brand_order(key="b/b"))
        code, out, err = self.run_cli("queue", "move", "--batch", "3", "top", "--json")
        self.assertEqual((code, err), (0, ""), out)
        self.assertEqual([e["id"] for e in json.loads(out)], [3, 4])
        self.assertEqual([e["id"] for e in sorted(queue.list_entries(["queued"]), key=queue._pos)], [3, 4, 1, 2])
        code, out, err = self.run_cli("queue", "cancel", "--batch", "3", "--json")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([e["state"] for e in json.loads(out)], ["cancelled", "cancelled"])
        code, _, err = self.run_cli("queue", "cancel", "--batch", "99")
        self.assertEqual(code, 1)
        self.assertIn("batch 99", err)
        code, _, err = self.run_cli("queue", "cancel")  # neither entry nor batch
        self.assertEqual(code, 1)
        self.assertIn("--batch", err)
        self.assertEqual(self.run_cli("queue", "cancel", "1", "--batch", "1")[0], 1)  # both


if __name__ == "__main__":
    unittest.main()
