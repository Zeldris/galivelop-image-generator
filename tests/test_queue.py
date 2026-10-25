import copy
import fcntl
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import log, orders, projects, queue
from gimg.errors import GimgError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())


class QueueBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data")})
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("GIMG_MACHINE_PROFILE", None)
        self.projects = {}
        for name in ("proj", "other"):
            self.add_project(name)

    def hold_worker_lock(self):
        """Pretend a worker is alive: hold ``worker.lock`` in this process (a second open() fails, as in a worker)."""
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, fd)

    def add_project(self, name):
        root = self.tmp / name
        root.mkdir()
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        cfg["name"] = name
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        projects.add(root)
        self.projects[name] = root
        return root

    def code(self, fn, *args, **kwargs):
        with self.assertRaises(GimgError) as cm:
            fn(*args, **kwargs)
        return cm.exception.code

    def push(self, project="proj", key="a", profile="banner", count=1, **kw):
        try:
            orders.get(project, key, profile)
        except GimgError:
            orders.submit(project, {"key": key, "profile": profile, "prompt": "a cat"})
        return queue.enqueue(project, key, profile, orders.attempt_specs(project, key, profile, count, **kw))


class QueueTests(QueueBase):
    def test_enqueue_fields(self):
        entries = self.push(count=2, seed=10)
        self.assertEqual([e["id"] for e in entries], [1, 2])
        first = entries[0]
        self.assertEqual((first["state"], first["seed"], first["project"], first["key"], first["profile"]),
                         ("queued", 10, "proj", "a", "banner"))
        self.assertEqual((first["pid"], first["attemptId"], first["error"], first["cancelRequested"]),
                         (None, None, None, False))
        self.assertEqual(entries[1]["seed"], 11)
        self.assertEqual(first["params"]["width"], 1280)
        self.assertTrue(first["prompt"].startswith("a cat, "))
        self.assertEqual(queue.get(2), entries[1])
        self.assertTrue((self.tmp / "data" / "queue.json").is_file())

    def test_unknown_order_not_queued(self):
        spec = [{"seed": 1, "prompt": "p", "params": {}, "references": []}]
        self.assertEqual(self.code(queue.enqueue, "proj", "nope", "banner", spec), "order.unknown")
        self.assertEqual(queue.list_entries(), [])

    def test_limits_at_enqueue(self):
        orders.submit("proj", {"key": "a", "profile": "banner", "prompt": "x", "params": {"steps": 99}})
        specs = orders.attempt_specs("proj", "a", "banner", 2)
        self.assertEqual(self.code(queue.enqueue, "proj", "a", "banner", specs), "limit.steps")
        self.assertEqual(queue.list_entries(), [])  # nothing half queued
        orders.submit("proj", {"key": "b", "profile": "banner", "prompt": "x", "references": ["1", "2"]})
        specs = orders.attempt_specs("proj", "b", "banner")
        self.assertEqual(self.code(queue.enqueue, "proj", "b", "banner", specs), "limit.references")

    def test_fifo_across_projects(self):
        self.push("proj", "a")
        self.push("other", "b")
        self.push("proj", "c")
        order = []
        while True:
            entry = queue.claim()
            if entry is None:
                break
            order.append((entry["id"], entry["project"]))
            self.assertEqual((entry["state"], entry["pid"]), ("running", os.getpid()))
            self.assertIsNotNone(entry["startedAt"])
            queue.finish(entry["id"], "done", attempt_id=1)
        self.assertEqual(order, [(1, "proj"), (2, "other"), (3, "proj")])
        self.assertIsNone(queue.next_queued())

    def test_next_queued_does_not_take(self):
        self.push(count=2)
        self.assertEqual(queue.next_queued()["id"], 1)
        self.assertEqual(queue.next_queued()["id"], 1)
        self.assertEqual(queue.claim()["id"], 1)
        self.assertEqual(queue.next_queued()["id"], 2)

    def test_list_filter(self):
        self.hold_worker_lock()
        self.push(count=3)
        queue.claim()
        self.assertEqual([e["id"] for e in queue.list_entries(["queued"])], [2, 3])
        self.assertEqual([e["id"] for e in queue.list_entries(("running", "queued"))], [1, 2, 3])
        self.assertEqual(queue.list_entries(["done"]), [])

    def test_cancel_queued(self):
        self.push(count=2)
        entry = queue.cancel(1)
        self.assertEqual((entry["state"], entry["cancelRequested"]), ("cancelled", False))
        self.assertIsNotNone(entry["finishedAt"])
        self.assertEqual(queue.claim()["id"], 2)

    def test_cancel_running_requests(self):
        self.hold_worker_lock()
        self.push()
        queue.claim()
        entry = queue.cancel(1)
        self.assertEqual((entry["state"], entry["cancelRequested"]), ("running", True))
        self.assertTrue(queue.is_cancel_requested(1))
        queue.finish(1, "cancelled")
        self.assertEqual(queue.get(1)["state"], "cancelled")

    def test_is_cancel_requested_never_recovers(self):
        self.push()
        queue.claim()  # running, and no worker holds the lock: a recovering read would re-queue it
        self.assertFalse(queue.is_cancel_requested(1))
        raw = json.loads((self.tmp / "data" / "queue.json").read_text())
        self.assertEqual(raw["entries"][0]["state"], "running")
        self.assertEqual(self.code(queue.is_cancel_requested, 99), "queue.unknown")

    def test_error_text_renders_schema_errors(self):
        from gimg import schema
        err = queue.make_error("order.invalid", [schema.ValidationError("/prompt", "maxLength", {"limit": 4000})])
        self.assertEqual(err["errors"], [{"path": "/prompt", "code": "maxLength", "params": {"limit": 4000}}])
        text = queue.error_text(err, "en")
        self.assertEqual(text.splitlines()[0], "the order is not valid:")
        self.assertIn("/prompt: must be at most 4000 characters", text)
        self.assertNotIn("errors", queue.make_error("x"))
        for odd in (None, "x", [1], [{"path": 1}], [{"path": "/a", "code": "nope", "params": 3}]):
            self.assertEqual(queue.error_text({"code": "order.invalid", "params": {}, "errors": odd}, "en")
                             .splitlines()[0], "the order is not valid:")

    def test_cancel_terminal_and_unknown(self):
        self.push()
        queue.claim()
        queue.finish(1, "failed", error="boom")
        self.assertEqual(self.code(queue.cancel, 1), "queue.not_cancellable")
        self.assertEqual(self.code(queue.cancel, 99), "queue.unknown")
        self.assertEqual(self.code(queue.get, "1"), "queue.unknown")

    def test_finish_rules(self):
        self.push()
        self.assertEqual(self.code(queue.finish, 1, "done"), "queue.not_running")  # still queued
        queue.claim()
        self.assertEqual(self.code(queue.finish, 1, "queued"), "queue.bad_state")
        entry = queue.finish(1, "failed", error=queue.make_error("limit.steps", steps=9, max=2))
        self.assertEqual((entry["state"], entry["error"], entry["pid"]),
                         ("failed", {"code": "limit.steps", "params": {"steps": 9, "max": 2}}, None))
        self.assertIsNotNone(entry["finishedAt"])

    def test_recovery_without_worker_lock(self):
        self.push(count=2)
        queue.claim()  # pid is this live process: the pid is irrelevant, only the worker lock counts
        path = self.tmp / "data" / "queue.json"
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["pid"], entry["startedAt"]), ("queued", None, None))
        self.assertEqual(json.loads(path.read_text())["entries"][0]["state"], "queued")  # persisted
        self.assertEqual(queue.claim()["id"], 1)  # first again, FIFO kept

    def test_recovery_with_cancel_requested(self):
        self.push()
        queue.claim()
        queue.cancel(1)
        self.assertEqual(queue.get(1)["state"], "cancelled")

    def test_live_worker_lock_keeps_running(self):
        self.push()
        queue.claim()
        self.hold_worker_lock()
        for read in (lambda: queue.get(1), lambda: queue.list_entries()[0]):
            self.assertEqual(read()["state"], "running")
        self.assertEqual(queue.get(1)["pid"], os.getpid())

    def test_enqueue_also_recovers(self):
        self.push()
        queue.claim()
        self.push(key="b")
        self.assertEqual(queue.list_entries()[0]["state"], "queued")

    def test_claim_and_finish_do_not_recover(self):
        self.push(count=2)
        queue.claim()
        self.assertEqual(queue.claim()["id"], 2)  # entry 1 is still running, not handed out again
        queue.finish(1, "done", attempt_id=1)

    def test_recover_orphans_is_for_the_lock_owner(self):
        self.push()
        queue.claim()
        self.hold_worker_lock()  # as the worker does; the others leave it alone
        self.assertEqual(queue.get(1)["state"], "running")
        queue.recover_orphans()
        self.assertEqual(queue.get(1)["state"], "queued")

    def test_recovery_deletes_pending_files(self):
        self.push()
        queue.claim()
        pending = orders.pending_image_path("proj", "a", "banner", 1)
        pending.parent.mkdir(parents=True)
        other = pending.parent / ".pending-2.png"
        for f in (pending, other):
            f.write_bytes(b"x")
        queue.list_entries()
        self.assertFalse(pending.exists())
        self.assertTrue(other.exists())  # only the recovered entries' files

    def test_error_text(self):
        error = queue.make_error("limit.steps", steps=9, max=2)
        self.assertIn("9", queue.error_text(error, "en"))
        self.assertNotEqual(queue.error_text(error, "es"), queue.error_text(error, "en"))
        self.push()
        queue.claim()
        entry = queue.finish(1, "failed", error=error)
        self.assertEqual(queue.error_text(entry, "en"), queue.error_text(error, "en"))
        self.assertEqual(queue.error_text(queue.make_error("nope.code")), "nope.code")  # unknown: the code
        self.assertEqual(queue.error_text(None), "")

    def test_error_text_odd_shapes(self):
        self.assertEqual(queue.error_text("timeout boom"), "timeout boom")
        self.assertEqual(queue.error_text({"params": {}}), "{'params': {}}")
        self.assertEqual(queue.error_text({"code": "nope.code", "params": [1]}), "nope.code")
        self.assertEqual(json.loads(json.dumps(queue.make_error("x", obj=Path("/a")))),
                         {"code": "x", "params": {"obj": "/a"}})

    def test_prune_keeps_last_200_terminal(self):
        total = queue.KEEP_TERMINAL + 15
        entries = [{"id": i, "project": "proj", "key": "a", "profile": "banner", "state": "done",
                    "seed": i, "prompt": "p", "params": {}, "references": []} for i in range(1, total + 1)]
        entries.append(dict(entries[0], id=total + 1, state="queued"))
        (self.tmp / "data").mkdir(exist_ok=True)
        (self.tmp / "data" / "queue.json").write_text(json.dumps({"nextId": total + 2, "entries": entries}))
        listed = queue.list_entries()
        self.assertEqual(len(listed), queue.KEEP_TERMINAL + 1)
        self.assertEqual(listed[0]["id"], 16)  # the oldest were dropped
        self.assertEqual(listed[-1]["state"], "queued")  # non terminal never dropped
        self.assertEqual(self.push()[0]["id"], total + 2)  # ids keep growing

    def test_corrupt_queue(self):
        (self.tmp / "data").mkdir(exist_ok=True)
        (self.tmp / "data" / "queue.json").write_text("{nope")
        self.assertEqual(self.code(queue.list_entries), "queue.corrupt")

    def test_estimate_for(self):
        entry = self.push()[0]
        self.assertIsNone(queue.estimate_for(entry))
        for ms in (100, 300, 200):
            log.append("proj", {"gen_ai.provider.name": "fake", "app.task": "banner", "app.image.steps": 6,
                                "app.image.references": 0, "app.duration_ms": ms})
        self.assertEqual(queue.estimate_for(entry), 200)
        self.assertEqual(queue.estimate_for(entry, provider="sd-cli"), None)
