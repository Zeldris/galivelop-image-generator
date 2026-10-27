"""F2.8 (D28), E2: the worker composes what the engine generates, and a failed composition never loses it.

Without ffmpeg and rsvg-convert (an empty ``PATH``) it checks the paths that do not need them; with them (``skipUnless``,
as in `tests/test_pilot_scripts.py`) it checks the real files."""
import contextlib
import io
import json
import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

from gimg import compose, delivery, engine, i18n, log, orders, png, queue, worker
from gimg.errors import GimgError
from tests.test_queue import QueueBase

TIENE_HERRAMIENTAS = shutil.which("ffmpeg") is not None and shutil.which("rsvg-convert") is not None
EN_CI = os.environ.get("CI") == "true"
CON_HERRAMIENTAS = unittest.skipUnless(EN_CI or TIENE_HERRAMIENTAS, "hacen falta ffmpeg y rsvg-convert")

TEMPLATE = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
            '<rect x="100" y="100" width="50" height="50" fill="#00ff00"/>'
            '<text x="400" y="300" font-size="40">{{title}}</text></svg>')
BASE = {"width": 1280, "height": 640, "steps": 6, "cfg": 1.0, "sampler": "euler", "model": "flux2-klein-4b-q8"}


class GarbageEngine(engine.Engine):
    """An engine whose 'image' is not a PNG."""
    provider = "fake"

    def generate(self, job, should_cancel):
        Path(job.output).parent.mkdir(parents=True, exist_ok=True)
        Path(job.output).write_bytes(b"this is not a png")
        return engine.EngineResult(duration_ms=1, engine_version="garbage-1")


class ComposeWorkerBase(QueueBase):
    def setUp(self):
        super().setUp()
        self.root = self.projects["proj"]
        (self.root / "t.svg").write_text(TEMPLATE, encoding="utf-8")
        self.profiles({
            "plain": dict(BASE),  # no compose, no target: nothing to do
            "same": dict(BASE, targetWidth=1280, targetHeight=640),  # a target that is the raw size: nothing to do
            "scaled": dict(BASE, targetWidth=1200, targetHeight=630),  # a target and no compose: ffmpeg only
            "og": dict(BASE, targetWidth=1200, targetHeight=630,
                       compose={"template": "t.svg", "fields": ["title", "subtitle"]}),
        })

    def profiles(self, extra):
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["profiles"].update(extra)
        path.write_text(json.dumps(cfg))

    def submit(self, profile, **extra):
        orders.submit("proj", dict({"key": "a", "profile": profile, "prompt": "a cat"}, **extra))

    def run_worker(self, **kw):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            handled = worker.run(**kw)
        return handled, err.getvalue()

    def folder(self, profile):
        return orders.pending_image_path("proj", "a", profile, 1).parent

    def names(self, profile):
        folder = self.folder(profile)
        return sorted(p.name for p in folder.iterdir()) if folder.exists() else []

    def attempt(self, profile, index=0):
        return orders.get("proj", "a", profile)["attempts"][index]

    def lines(self):
        return [json.loads(x) for x in log.log_path("proj").read_text().splitlines()]

    def enqueue(self, profile, **kw):
        return queue.enqueue("proj", "a", profile, orders.attempt_specs("proj", "a", profile, **kw))


class NothingToComposeTests(ComposeWorkerBase):
    def test_a_profile_without_compose_leaves_the_disk_as_before_and_never_calls_a_tool(self):
        for profile in ("plain", "same"):
            self.submit(profile)
            self.enqueue(profile)
        with mock.patch.object(compose.subprocess, "run", side_effect=AssertionError("a tool was called")), \
                mock.patch.object(compose, "render", side_effect=AssertionError("render was called")), \
                mock.patch.dict(os.environ, {"PATH": ""}):
            self.assertEqual(self.run_worker()[0], 2)
        for profile in ("plain", "same"):
            self.assertEqual(self.names(profile), ["q%d.png" % (1 if profile == "plain" else 2)])
            att = self.attempt(profile)
            self.assertTrue({"raw", "compose", "composeError"}.isdisjoint(att), att)
            self.assertEqual(att["image"], "attempts/q%d.png" % att["queueEntry"])
        for line in self.lines():
            self.assertTrue({"app.image.compose", "app.image.compose_error"}.isdisjoint(line))
        self.assertEqual([e["state"] for e in queue.list_entries()], ["done", "done"])

    def test_what_the_engine_left_that_is_not_a_png_is_kept_as_before_not_composed(self):
        self.submit("og")
        self.enqueue("og")
        with mock.patch.object(compose, "render", side_effect=AssertionError("render was called")):
            self.assertEqual(self.run_worker(engine=GarbageEngine())[0], 1)
        self.assertEqual(self.names("og"), ["q1.png"])
        self.assertTrue({"raw", "compose", "composeError"}.isdisjoint(self.attempt("og")))
        self.assertEqual(queue.get(1)["state"], "done")


class ComposeFailureTests(ComposeWorkerBase):
    """A failed composition keeps the generation: the attempt is `done`, shows the raw image and cannot be chosen."""

    def failed(self, profile="og", path="", **extra):
        self.submit(profile, **extra)
        self.enqueue(profile)
        with mock.patch.dict(os.environ, {"PATH": path}):
            return self.run_worker()

    def check_kept(self, profile, code, **params):
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"], entry["attemptId"]), ("done", None, 1))
        att = self.attempt(profile)
        self.assertEqual((att["image"], att["raw"]), ("attempts/q1.raw.png", "attempts/q1.raw.png"))
        self.assertEqual(att["composeError"], {"code": code, "params": params})
        self.assertNotIn("compose", att)
        self.assertEqual(self.names(profile), ["q1.raw.png"])  # no half-made composed image, no temp folder
        raw = orders.raw_image("proj", "a", profile, att)
        self.assertEqual(png.size(raw), (1280, 640))
        self.assertEqual(orders.attempt_image("proj", "a", profile, att), raw)
        self.assertEqual(self.code(orders.choose, "proj", "a", profile, 1), "order.choose_uncomposed")
        self.assertEqual(self.code(delivery.choose, "proj", "a", profile, 1), "order.choose_uncomposed")
        return att

    def test_without_the_tools_the_attempt_keeps_the_raw_image_and_says_why(self):
        handled, err = self.failed()
        self.assertEqual(handled, 1)
        self.check_kept("og", "compose.tool_missing", tool="rsvg-convert")
        self.assertNotIn("worker.compose_failed", err)  # the line is translated
        self.assertIn("rsvg-convert", err)  # the reason is the rendered error

    def test_the_stderr_line_is_in_both_languages(self):
        for lang, word in (("en", "could not be composed"), ("es", "no se pudo componer")):
            self.assertIn(word, i18n.t("worker.compose_failed", lang, id=1, reason="x"))

    def test_a_profile_with_only_a_target_needs_ffmpeg(self):
        self.failed("scaled")
        self.check_kept("scaled", "compose.tool_missing", tool="ffmpeg")

    def test_the_log_line_says_the_composition_failed_and_with_which_template_it_did_not_happen(self):
        self.failed()
        (line,) = self.lines()
        self.assertEqual(line["app.image.compose_error"], "compose.tool_missing")
        self.assertNotIn("app.image.compose", line)
        self.assertNotIn("app.error", line)  # the generation itself went well

    def test_a_missing_template_and_a_template_that_leaves_the_project_are_kept_too(self):
        (self.root / "t.svg").unlink()
        self.failed()
        self.check_kept("og", "compose.template_missing", path="t.svg")
        (self.root.parent / "outside.svg").write_text(TEMPLATE)
        (self.root / "t.svg").symlink_to(self.root.parent / "outside.svg")
        self.enqueue("og")
        with mock.patch.dict(os.environ, {"PATH": ""}):
            self.run_worker()
        second = self.attempt("og", 1)
        self.assertTrue(second["composeError"]["code"].startswith("path."), second["composeError"])
        self.assertEqual(second["image"], "attempts/q2.raw.png")

    def test_any_gimg_error_of_the_render_is_kept_including_png_errors(self):
        self.submit("og")
        self.enqueue("og")
        with mock.patch.object(compose, "render", side_effect=GimgError("png.invalid", path="p", reason="bad")):
            self.run_worker()
        self.check_kept("og", "png.invalid", path="p", reason="bad")

    def test_a_draft_that_cannot_be_composed_is_kept_as_a_draft(self):
        self.submit("og")
        self.enqueue("og", draft=True)
        with mock.patch.dict(os.environ, {"PATH": ""}):
            self.run_worker()
        att = self.attempt("og")
        self.assertEqual((att["draft"], att["composeError"]["code"]), (True, "compose.tool_missing"))
        self.assertEqual(png.size(orders.raw_image("proj", "a", "og", att)), (640, 320))


class AbortTests(ComposeWorkerBase):
    def test_add_attempt_failing_after_render_removes_both_images(self):
        self.submit("og")
        self.enqueue("og")

        seen = []

        def fake_render(root, cfg, raw, out, text, profile=None):
            Path(out).write_bytes(Path(raw).read_bytes())
            seen.append((Path(raw).name, Path(out).name))
            return {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "text": {}}

        with mock.patch.object(compose, "render", fake_render), \
                mock.patch.object(orders, "add_attempt", side_effect=GimgError("order.corrupt", path="p")):
            self.run_worker()
        self.assertEqual(seen, [("q1.raw.png", "q1.png")])  # both images existed when add_attempt failed
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]["code"]), ("failed", "order.corrupt"))
        self.assertEqual(self.names("og"), [])
        self.assertEqual(orders.get("proj", "a", "og")["attempts"], [])

    def test_a_sigterm_half_way_through_composing_leaves_no_images_and_the_entry_to_be_retried(self):
        self.submit("og")
        self.enqueue("og")

        def killed(root, cfg, raw, out, text, profile=None):
            Path(out).write_bytes(b"half")
            raise SystemExit(143)  # what `_terminate` raises

        with mock.patch.object(compose, "render", killed):
            with self.assertRaises(SystemExit):
                self.run_worker()
        self.assertEqual(queue.get(1)["state"], "queued")  # it was running; the next look at the queue recovers it
        self.assertEqual(self.names("og"), [])
        self.assertEqual(orders.get("proj", "a", "og")["attempts"], [])

    def test_recovery_removes_a_composition_folder_a_killed_worker_left(self):
        self.submit("og")
        self.enqueue("og")
        queue.claim()
        folder = self.folder("og")
        folder.mkdir(parents=True)
        stale = folder / ".compose-abc123"
        stale.mkdir()
        (stale / "layer.png").write_bytes(b"x")
        queue.recover_orphans()
        self.assertFalse(stale.exists())

    def test_the_worker_composes_the_profile_as_it_is_now_not_as_it_was_when_queued(self):
        self.submit("og")
        self.enqueue("og")
        seen = []

        def fake_render(root, cfg, raw, out, text, profile=None):
            seen.append(cfg["targetWidth"])
            raise GimgError("compose.tool_failed", tool="ffmpeg", reason="x")

        original = engine.FakeEngine.generate

        def slow(self_, job, cancel):
            result = original(self_, job, cancel)
            self.profiles({"og": dict(BASE, targetWidth=800, targetHeight=400,
                                      compose={"template": "t.svg", "fields": ["title"]})})
            return result

        with mock.patch.object(compose, "render", fake_render), mock.patch.object(engine.FakeEngine, "generate", slow):
            self.run_worker()
        self.assertEqual(seen, [800])


class TextTests(ComposeWorkerBase):
    def capture(self):
        seen = []

        def fake_render(root, cfg, raw, out, text, profile=None):
            seen.append((Path(root), text, profile))
            raise GimgError("compose.tool_failed", tool="ffmpeg", reason="stop")

        return seen, mock.patch.object(compose, "render", fake_render)

    def test_the_text_of_the_order_reaches_the_render_and_set_text_changes_the_next_attempt(self):
        self.submit("og", text={"title": "Hello"})
        self.enqueue("og")
        orders.set_text("proj", "a", "og", {"title": "Bye", "subtitle": "x"})
        self.enqueue("og")
        seen, patch = self.capture()
        with patch:
            self.run_worker()
        self.assertEqual(seen, [(self.root, {"title": "Hello"}, "og"),
                                (self.root, {"title": "Bye", "subtitle": "x"}, "og")])

    def test_an_entry_queued_before_f2_8_has_no_text_and_is_composed_with_none(self):
        self.submit("og")
        self.enqueue("og")
        path = queue.queue_path()
        data = json.loads(path.read_text())
        del data["entries"][0]["text"]
        path.write_text(json.dumps(data))
        seen, patch = self.capture()
        with patch:
            self.run_worker()
        self.assertEqual([text for _, text, _ in seen], [{}])

    def test_enqueue_stores_the_text_apart_from_the_spec(self):
        self.submit("og", text={"title": "Hello"})
        specs = orders.attempt_specs("proj", "a", "og")
        (entry,) = queue.enqueue("proj", "a", "og", specs)
        self.assertEqual(entry["text"], {"title": "Hello"})
        specs[0]["text"]["title"] = "changed"
        self.assertEqual(queue.get(entry["id"])["text"], {"title": "Hello"})
        (older,) = queue.enqueue("proj", "a", "og", [{"seed": 1, "prompt": "p", "params": {}, "references": []}])
        self.assertEqual(older["text"], {})


@CON_HERRAMIENTAS
class WithToolsTests(ComposeWorkerBase):
    def test_the_raw_and_the_composed_image_are_saved_and_the_log_names_the_template(self):
        self.submit("og", text={"title": "Tom & <Jerry>"})
        self.enqueue("og")
        self.assertEqual(self.run_worker()[0], 1)
        self.assertEqual(self.names("og"), ["q1.png", "q1.raw.png"])
        att = self.attempt("og")
        self.assertEqual((att["image"], att["raw"]), ("attempts/q1.png", "attempts/q1.raw.png"))
        self.assertNotIn("composeError", att)
        want = {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg",
                "text": {"title": "Tom & <Jerry>", "subtitle": ""}}
        self.assertEqual(att["compose"], want)
        done, raw = orders.attempt_image("proj", "a", "og", att), orders.raw_image("proj", "a", "og", att)
        self.assertEqual((png.size(done), png.size(raw)), ((1200, 630), (1280, 640)))
        chunk = json.loads(png.read_text_chunks(done)["gimg"])  # what made the raw image, and what composed it
        self.assertEqual((chunk["compose"], chunk["seed"], chunk["profile"]), (want, att["seed"], "og"))
        self.assertNotIn("compose", json.loads(png.read_text_chunks(raw)["gimg"]))
        (line,) = self.lines()
        self.assertEqual(line["app.image.compose"], "t.svg")
        self.assertNotIn("app.image.compose_error", line)
        self.assertEqual(queue.get(1)["state"], "done")

    def test_a_composed_attempt_can_be_chosen_and_delivers_the_composed_image_and_its_compose(self):
        self.submit("og", text={"title": "Hi"})
        self.enqueue("og")
        self.run_worker()
        delivery.choose("proj", "a", "og", 1)
        target = self.root / "uploads" / "images" / "a-og.png"
        self.assertEqual(png.size(target), (1200, 630))
        manifest = json.loads((self.root / "galivelop-images.manifest.json").read_text())
        self.assertEqual(manifest["images"]["a"]["og"]["compose"], self.attempt("og")["compose"])

    def test_a_draft_is_composed_too_and_still_cannot_be_chosen(self):
        self.submit("og", text={"title": "Draft"})
        self.enqueue("og", draft=True)
        self.run_worker()
        att = self.attempt("og")
        self.assertEqual((att["draft"], att["image"], att["raw"]), (True, "attempts/q1.png", "attempts/q1.raw.png"))
        self.assertEqual(png.size(orders.attempt_image("proj", "a", "og", att)), (1200, 630))
        self.assertEqual(png.size(orders.raw_image("proj", "a", "og", att)), (640, 320))
        self.assertEqual(self.code(orders.choose, "proj", "a", "og", 1), "order.choose_draft")

    def test_a_profile_with_only_a_target_scales_the_raw_image(self):
        self.submit("scaled")
        self.enqueue("scaled")
        self.run_worker()
        att = self.attempt("scaled")
        self.assertEqual(png.size(orders.attempt_image("proj", "a", "scaled", att)), (1200, 630))
        self.assertEqual(att["compose"], {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "text": {}})
        self.assertNotIn("app.image.compose", self.lines()[0])  # there is no template to name

    def test_the_composed_text_follows_set_text_on_the_next_attempt(self):
        self.submit("og", text={"title": "One"})
        self.enqueue("og")
        orders.set_text("proj", "a", "og", {"title": "Two"})
        self.enqueue("og")
        self.run_worker()
        self.assertEqual([a["compose"]["text"]["title"] for a in orders.get("proj", "a", "og")["attempts"]],
                         ["One", "Two"])


if __name__ == "__main__":
    unittest.main()
