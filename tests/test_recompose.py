"""F2.8 (D28), E3: `compose.recompose` composes an attempt again from its raw image, without generating.

Most cases run with a fake `compose.render` (a copy of the raw image plus the text, so a redelivery is visible in the
bytes); the last class uses the real ffmpeg and rsvg-convert (``skipUnless``, as in `tests/test_compose_worker.py`)."""
import json
import contextlib
import io
import os
import unittest
from pathlib import Path
from unittest import mock

from gimg import compose, delivery, engine, fsutil, i18n, log, orders, png, queue
from gimg.errors import GimgError
from tests.test_compose_worker import CON_HERRAMIENTAS, ComposeWorkerBase


class FakeRender:
    """A `compose.render` that copies the raw image and appends the text it was given; records every call."""

    def __init__(self, fail=None):
        self.calls, self.fail = [], fail

    def __call__(self, root, cfg, raw, out, text, profile=None, prefix=None):
        self.calls.append({"root": Path(root), "raw": Path(raw), "out": Path(out), "text": dict(text),
                           "profile": profile, "prefix": prefix})
        if self.fail is not None:
            raise self.fail
        Path(out).write_bytes(Path(raw).read_bytes() + json.dumps(text, sort_keys=True).encode())
        return {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg", "text": dict(text)}


class RecomposeBase(ComposeWorkerBase):
    def made(self, count=1, choose=1, **extra):
        """Order `a`@`og` with `count` attempts composed by the worker (fake render); `choose` is delivered."""
        self.submit("og", **extra)
        self.enqueue("og", count=count)
        with mock.patch.object(compose, "render", FakeRender()):
            self.run_worker()
        if choose:
            delivery.choose("proj", "a", "og", choose)

    def recompose(self, *args, render=None, **kw):
        render = render or FakeRender()
        with mock.patch.object(compose, "render", render), \
                mock.patch.object(engine.FakeEngine, "generate", side_effect=AssertionError("generated")):
            return compose.recompose("proj", "a", "og", *args, **kw), render

    def delivered(self):
        return self.root / "uploads" / "images" / "a-og.png"

    def manifest(self):
        return json.loads((self.root / "galivelop-images.manifest.json").read_text())["images"]["a"]["og"]

    def make_old(self, attempt_id):
        """Turn the attempt into one made before F2.8: no ``raw``, no ``compose``, its ``image`` is the raw image."""
        folder = self.folder("og")
        raw, composed = folder / ("q%d.raw.png" % attempt_id), folder / ("q%d.png" % attempt_id)
        composed.unlink()
        raw.rename(composed)  # what the model gave, under the old name
        path = orders._order_file("proj", "a", "og")
        data = json.loads(path.read_text())
        for att in data["attempts"]:
            if att["id"] == attempt_id:
                att.pop("raw"), att.pop("compose")
        path.write_text(json.dumps(data))
        return composed.read_bytes()

    def log_lines(self):
        return self.lines()


class ChoiceOfAttemptTests(RecomposeBase):
    def test_without_an_attempt_the_chosen_one_is_composed_and_delivered_again_without_generating(self):
        self.made(count=2, choose=1, text={"title": "Old"})
        before = self.delivered().read_bytes()
        att, render = self.recompose(text={"title": "New"})
        self.assertEqual([(c["raw"].name, c["out"].name, c["text"]) for c in render.calls],
                         [("q1.raw.png", "q1.png", {"title": "New"})])
        self.assertEqual((att["id"], att["compose"]["text"], att["delivered"]), (1, {"title": "New"}, "uploads/images/a-og.png"))
        self.assertNotEqual(self.delivered().read_bytes(), before)
        self.assertTrue(self.delivered().read_bytes().endswith(b'{"title": "New"}'))
        self.assertEqual(self.manifest()["compose"]["text"], {"title": "New"})
        self.assertEqual((self.manifest()["attemptId"], orders.get("proj", "a", "og")["chosen"]), (1, 1))
        self.assertEqual(len(queue.list_entries()), 2)  # nothing was queued: no generation

    def test_without_a_chosen_one_the_last_attempt_is_composed_and_nothing_is_delivered(self):
        self.made(count=3, choose=None)
        att, render = self.recompose()
        self.assertEqual(([c["raw"].name for c in render.calls], att["id"]), (["q3.raw.png"], 3))
        self.assertNotIn("delivered", att)
        self.assertFalse(self.delivered().exists())

    def test_an_explicit_attempt_that_is_not_the_chosen_one_is_not_delivered(self):
        self.made(count=2, choose=1)
        before = self.delivered().read_bytes()
        att, render = self.recompose(2, text={"title": "Two"})
        self.assertEqual((att["id"], "delivered" in att), (2, False))
        self.assertEqual(self.delivered().read_bytes(), before)
        self.assertEqual(self.manifest()["attemptId"], 1)

    def test_a_choose_of_another_attempt_while_composing_is_not_undone_by_the_redelivery(self):
        self.made(count=2, choose=1, text={"title": "Old"})
        render = FakeRender()

        def render_then_choose(*args, **kw):
            result = render(*args, **kw)
            delivery.choose("proj", "a", "og", 2)  # `gimg choose 2` lands between the render and the redelivery
            return result

        with mock.patch.object(compose, "render", render_then_choose):
            att = compose.recompose("proj", "a", "og", None, {"title": "New"})
        self.assertNotIn("delivered", att)
        order = orders.get("proj", "a", "og")
        self.assertEqual((order["chosen"], order["chosenHistory"]), (2, [None, 1]))  # no second push of the history
        self.assertEqual((self.manifest()["attemptId"], self.delivered().read_bytes()),
                         (2, (self.folder("og") / "q2.png").read_bytes()))
        self.assertEqual(orders.get("proj", "a", "og")["attempts"][0]["compose"]["text"], {"title": "New"})  # 1 was composed

    def test_an_unknown_attempt_and_an_order_without_attempts_say_so(self):
        self.made(choose=None)
        with mock.patch.object(compose, "render", FakeRender()):
            for bad in (9, 0, True):
                self.assertEqual(self.code(compose.recompose, "proj", "a", "og", bad), "order.attempt_unknown", bad)
        self.submit("scaled")
        with mock.patch.object(compose, "render", side_effect=AssertionError("render was called")):
            self.assertEqual(self.code(compose.recompose, "proj", "a", "scaled"), "compose.no_attempts")
            self.assertEqual(self.code(compose.recompose, "proj", "zzz", "og"), "order.unknown")
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        del cfg["profiles"]["og"]
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        with mock.patch.object(compose, "render", side_effect=AssertionError("render was called")):
            self.assertEqual(self.code(compose.recompose, "proj", "a", "og"), "order.profile_unknown")

    def test_an_attempt_whose_composition_failed_is_fixed_and_becomes_choosable(self):
        self.submit("og")
        self.enqueue("og")
        with mock.patch.dict(os.environ, {"PATH": ""}):
            self.run_worker()
        self.assertEqual(self.code(delivery.choose, "proj", "a", "og", 1), "order.choose_uncomposed")
        att, _ = self.recompose(text={"title": "Fixed"})
        self.assertEqual((att["image"], att["raw"]), ("attempts/q1.png", "attempts/q1.raw.png"))
        self.assertNotIn("composeError", att)
        delivery.choose("proj", "a", "og", 1)
        self.assertTrue(self.delivered().exists())


class BusyTests(RecomposeBase):
    def lock(self, attempt_id=1):
        return fsutil.lock(orders.compose_lock_path("proj", "a", "og", attempt_id))

    def test_an_attempt_that_is_being_composed_is_busy_and_nothing_changes(self):
        self.made(count=2, choose=1, text={"title": "Old"})
        before = (self.delivered().read_bytes(), orders.get("proj", "a", "og"), self.names("og"))
        render = FakeRender()
        with self.lock(1), mock.patch.object(compose, "render", render):
            with self.assertRaises(GimgError) as cm:
                compose.recompose("proj", "a", "og", 1, {"title": "New"})
            self.assertEqual((cm.exception.code, cm.exception.params), ("compose.busy", {"attempt": 1}))
            self.assertEqual(cm.exception.message("en"), i18n.t("error.compose.busy", "en", attempt=1))
            for lang in ("es", "en"):
                self.assertIn("1", cm.exception.message(lang))
                self.assertNotIn("error.", cm.exception.message(lang))
            self.assertEqual(self.code(compose.recompose, "proj", "a", "og"), "compose.busy")  # the chosen one is 1
        self.assertEqual(render.calls, [])  # a busy attempt never reaches the render
        after = orders.get("proj", "a", "og")
        self.assertEqual((self.delivered().read_bytes(), after, self.names("og")), before)  # the new text was not saved either
        self.assertNotIn("composeError", after["attempts"][0])
        with self.lock(1):
            att, _ = self.recompose(2, text={"title": "Two"})  # the lock is per attempt: another one is free
        self.assertEqual(att["id"], 2)

    def test_the_lock_is_released_after_a_success_and_after_a_failure(self):
        self.made(choose=None)
        self.recompose()
        self.failing_once()
        self.recompose()  # not busy

    def failing_once(self):
        with mock.patch.object(compose, "render", FakeRender(fail=ValueError("x"))), self.assertRaises(ValueError):
            compose.recompose("proj", "a", "og")

    def test_what_a_killed_compose_left_for_this_attempt_is_removed_and_nothing_else(self):
        self.made(count=2, choose=None)
        folder = self.folder("og")
        stale_dir = folder / ".compose-c2-abc"
        stale_dir.mkdir()
        (stale_dir / "layer.png").write_bytes(b"x")
        stale_tmp = folder / ".q2.raw.png.k3j.tmp"
        stale_tmp.write_bytes(b"x")
        keep = [folder / ".compose-c1-abc", folder / ".compose-c20-abc", folder / ".compose-q2-abc"]
        for path in keep:
            path.mkdir()
        keep_tmp = folder / ".q1.raw.png.k3j.tmp"
        keep_tmp.write_bytes(b"x")
        self.recompose(2)
        self.assertEqual((stale_dir.exists(), stale_tmp.exists()), (False, False))
        self.assertTrue(all(p.exists() for p in keep + [keep_tmp]))

    def test_a_busy_attempt_keeps_the_leftovers_of_the_one_who_holds_it(self):
        self.made(choose=None)
        working = self.folder("og") / ".compose-c1-abc"
        working.mkdir()
        with self.lock(1), self.assertRaises(GimgError):
            compose.recompose("proj", "a", "og")
        self.assertTrue(working.exists())


class SameFileTests(RecomposeBase):
    def raw_is(self, name):
        path = orders._order_file("proj", "a", "og")
        data = json.loads(path.read_text())
        data["attempts"][0]["raw"] = name
        path.write_text(json.dumps(data))

    def refused(self):
        before = (orders.get("proj", "a", "og"), self.names("og"), (self.folder("og") / "q1.png").read_bytes())
        render = FakeRender()
        with mock.patch.object(compose, "render", render), self.assertRaises(GimgError) as cm:
            compose.recompose("proj", "a", "og", 1, {"title": "x"})
        self.assertEqual((cm.exception.code, cm.exception.params["reason"], render.calls),
                         ("compose.write_failed", "it is the raw image", []))
        self.assertEqual((orders.get("proj", "a", "og"), self.names("og"), (self.folder("og") / "q1.png").read_bytes()), before)

    def test_a_raw_that_does_not_end_in_raw_png_is_refused_before_anything_changes(self):
        self.made(choose=None)
        self.raw_is("attempts/q1.png")
        self.refused()

    def test_a_raw_that_is_a_link_to_the_composed_file_is_refused_before_anything_changes(self):
        self.made(choose=None)
        (self.folder("og") / "q1.raw.png").unlink()
        (self.folder("og") / "q1.raw.png").symlink_to(self.folder("og") / "q1.png")
        self.refused()


class TextTests(RecomposeBase):
    def test_text_is_saved_in_the_order_merged_and_the_whole_text_is_composed(self):
        self.made(choose=None, text={"title": "T", "subtitle": "S"})
        att, render = self.recompose(text={"title": "New"})
        self.assertEqual(render.calls[0]["text"], {"title": "New", "subtitle": "S"})
        self.assertEqual(orders.get("proj", "a", "og")["text"], {"title": "New", "subtitle": "S"})
        self.enqueue("og")  # the next attempt uses the new text too
        self.assertEqual(queue.list_entries()[-1]["text"], {"title": "New", "subtitle": "S"})

    def test_without_text_the_text_of_the_order_is_composed_and_the_order_is_not_touched(self):
        self.made(choose=None, text={"title": "T"})
        _, render = self.recompose()
        self.assertEqual(render.calls[0]["text"], {"title": "T"})
        self.assertEqual(orders.get("proj", "a", "og")["text"], {"title": "T"})
        _, render = self.recompose(text={})  # an empty text is "no text"
        self.assertEqual(render.calls[0]["text"], {"title": "T"})

    def test_a_field_the_profile_does_not_compose_is_refused_and_nothing_changes(self):
        self.made(choose=1, text={"title": "T"})
        before = self.delivered().read_bytes()
        render = FakeRender()
        with mock.patch.object(compose, "render", render):
            self.assertEqual(self.code(compose.recompose, "proj", "a", "og", None, {"color": "red"}),
                             "order.text_unknown_field")
        self.assertEqual((render.calls, orders.get("proj", "a", "og")["text"], self.delivered().read_bytes()),
                         ([], {"title": "T"}, before))


class NothingToDoTests(RecomposeBase):
    def test_a_profile_with_nothing_to_compose_raises_before_anything_changes(self):
        self.submit("plain")
        self.enqueue("plain")
        self.run_worker()
        before = (orders.get("proj", "a", "plain"), self.names("plain"))
        with mock.patch.object(compose, "render", side_effect=AssertionError("render was called")):
            with self.assertRaises(GimgError) as cm:
                compose.recompose("proj", "a", "plain")
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.nothing_to_do", {"profile": "plain"}))
        self.assertEqual((orders.get("proj", "a", "plain"), self.names("plain")), before)  # no .raw.png copy either
        self.assertEqual(len(self.log_lines()), 1)  # the generation's only: no line for a recomposition that did not happen

    def test_a_profile_whose_target_is_the_raw_size_has_nothing_to_do_either(self):
        self.submit("same")
        self.enqueue("same")
        self.run_worker()
        with mock.patch.object(compose, "render", side_effect=AssertionError("render was called")):
            self.assertEqual(self.code(compose.recompose, "proj", "a", "same"), "compose.nothing_to_do")


class OldAttemptTests(RecomposeBase):
    def test_an_attempt_made_before_f2_8_keeps_its_image_as_the_raw_one_before_anything_else(self):
        self.made(choose=1)
        old = self.make_old(1)
        order = {}

        def render(root, cfg, raw, out, text, profile=None, prefix=None):
            order["raw_bytes"] = Path(raw).read_bytes()  # the copy is there when the render starts
            order["att"] = orders.get("proj", "a", "og")["attempts"][0]  # and the order is not changed yet
            return FakeRender()(root, cfg, raw, out, text, profile, prefix)

        att, _ = self.recompose(render=render, text={"title": "Hi"})
        self.assertEqual(order["raw_bytes"], old)
        self.assertNotIn("raw", order["att"])
        self.assertEqual((att["raw"], att["image"]), ("attempts/q1.raw.png", "attempts/q1.png"))
        self.assertEqual((self.folder("og") / "q1.raw.png").read_bytes(), old)
        self.assertTrue((self.folder("og") / "q1.png").read_bytes().startswith(old))
        self.assertEqual(self.names("og"), ["q1.png", "q1.raw.png"])  # no temporary folder left
        self.assertEqual(orders.get("proj", "a", "og")["attempts"][0]["raw"], "attempts/q1.raw.png")

    def test_a_failed_recomposition_of_an_old_attempt_keeps_the_copy_and_does_not_overwrite_it_next_time(self):
        self.made(choose=None)
        old = self.make_old(1)
        fail = FakeRender(fail=GimgError("compose.tool_failed", tool="ffmpeg", reason="boom"))
        with mock.patch.object(compose, "render", fail), self.assertRaises(GimgError):
            compose.recompose("proj", "a", "og")
        att = self.attempt("og")
        self.assertEqual((att["image"], att["composeError"]["code"]), ("attempts/q1.png", "compose.tool_failed"))
        self.assertEqual((self.folder("og") / "q1.raw.png").read_bytes(), old)
        # the render of a second try works and overwrites the image: a third run must still read the copy, not q1.png
        self.recompose(text={"title": "x"})
        (self.folder("og") / "q1.png").write_bytes(b"composed")
        path = orders._order_file("proj", "a", "og")
        data = json.loads(path.read_text())
        data["attempts"][0].pop("raw")
        path.write_text(json.dumps(data))
        _, render = self.recompose()
        self.assertEqual(render.calls[0]["raw"].read_bytes(), old)

    def test_an_old_attempt_whose_image_is_gone_fails_on_the_png_and_changes_nothing(self):
        self.made(choose=None)
        self.make_old(1)
        (self.folder("og") / "q1.png").unlink()
        with mock.patch.object(compose, "render", side_effect=AssertionError("render was called")):
            self.assertEqual(self.code(compose.recompose, "proj", "a", "og"), "png.invalid")
        self.assertNotIn("composeError", self.attempt("og"))


class FailureTests(RecomposeBase):
    def failing(self, error, **kw):
        with mock.patch.object(compose, "render", FakeRender(fail=error)), self.assertRaises(type(error)) as cm:
            compose.recompose("proj", "a", "og", **kw)
        return cm.exception

    def test_a_failed_render_is_recorded_on_the_attempt_and_raised_again(self):
        self.made(choose=None)
        exc = self.failing(GimgError("compose.tool_failed", tool="ffmpeg", reason="boom"))
        self.assertEqual(exc.code, "compose.tool_failed")
        att = self.attempt("og")
        self.assertEqual(att["composeError"], {"code": "compose.tool_failed", "params": {"tool": "ffmpeg", "reason": "boom"}})
        self.assertEqual((att["image"], "compose" in att), ("attempts/q1.raw.png", False))
        self.assertEqual(self.code(delivery.choose, "proj", "a", "og", 1), "order.choose_uncomposed")

    def test_a_render_that_fails_for_another_reason_is_compose_unexpected_with_a_short_reason(self):
        self.made(choose=None)
        exc = self.failing(ValueError("x" * 400))
        self.assertIsInstance(exc, ValueError)
        error = self.attempt("og")["composeError"]
        self.assertEqual((error["code"], error["params"]["reason"]), ("compose.unexpected", ("ValueError: " + "x" * 400)[:300]))

    def test_a_failed_recomposition_of_the_chosen_one_cannot_be_undone_into(self):
        self.made(count=2, choose=1)
        delivery.choose("proj", "a", "og", 2)
        before = (self.delivered().read_bytes(), self.manifest())
        compose_failed = FakeRender(fail=GimgError("compose.tool_failed", tool="ffmpeg", reason="boom"))
        with mock.patch.object(compose, "render", compose_failed), self.assertRaises(GimgError):
            compose.recompose("proj", "a", "og", 1)
        with self.assertRaises(GimgError) as cm:
            delivery.undo("proj", "a", "og")
        self.assertEqual((cm.exception.code, cm.exception.params), ("order.undo_uncomposed", {"attempt": 1}))
        self.assertEqual((self.delivered().read_bytes(), self.manifest()), before)  # the raw image was not delivered
        self.assertEqual(orders.get("proj", "a", "og")["chosen"], 2)

    def test_the_delivered_file_is_not_touched_when_the_render_fails(self):
        self.made(choose=1)
        before = (self.delivered().read_bytes(), self.manifest())
        self.failing(GimgError("compose.tool_missing", tool="rsvg-convert"), text={"title": "x"})
        self.assertEqual((self.delivered().read_bytes(), self.manifest()), before)
        self.assertEqual(orders.get("proj", "a", "og")["text"]["title"], "x")  # the text was saved first (decision 5)

    def test_a_params_value_that_is_not_json_is_kept_as_text(self):
        self.made(choose=None)
        self.failing(GimgError("compose.tool_failed", tool="ffmpeg", reason=Path("/x")))
        self.assertEqual(self.attempt("og")["composeError"]["params"]["reason"], "/x")


class LogTests(RecomposeBase):
    def test_a_recomposition_writes_a_log_line_with_the_template(self):
        self.made(choose=None)
        self.recompose(text={"title": "x"})
        first, second = self.log_lines()
        self.assertNotIn("app.image.recompose", first)
        self.assertEqual((second["app.image.compose"], second["app.image.recompose"], second["app.task"], second["app.image.key"]),
                         ("t.svg", True, "og", "a"))
        for name in ("app.image.compose_error", "app.duration_ms", "app.error"):
            self.assertNotIn(name, second)
        self.assertEqual((second["app.image.width"], second["app.image.seed"]), (1280, self.attempt("og")["seed"]))

    def test_a_recomposition_is_not_logged_as_a_generation(self):
        self.made(choose=None)
        self.recompose(text={"title": "x"})
        first, second = self.log_lines()
        self.assertEqual((first["gen_ai.operation.name"], first["gen_ai.provider.name"]), ("image_generation", "fake"))
        self.assertIn("gen_ai.request.model", first)
        self.assertEqual(second["gen_ai.operation.name"], "image_composition")
        for name in ("gen_ai.provider.name", "gen_ai.request.model", "app.duration_ms"):
            self.assertNotIn(name, second)
        self.assertEqual(log.estimate("proj", "fake", "og", 6, False), first["app.duration_ms"])  # the generation only

    def test_a_failed_recomposition_writes_the_error_code_and_no_template(self):
        self.made(choose=None)
        with mock.patch.object(compose, "render", FakeRender(fail=GimgError("compose.timeout", tool="ffmpeg", seconds=1))), \
                self.assertRaises(GimgError):
            compose.recompose("proj", "a", "og")
        line = self.log_lines()[-1]
        self.assertEqual((line["app.image.compose_error"], line["app.image.recompose"]), ("compose.timeout", True))
        self.assertNotIn("app.image.compose", line)

    def test_a_log_that_cannot_be_written_does_not_fail_the_recomposition(self):
        self.made(choose=1)
        with mock.patch.object(log, "append", side_effect=OSError("disk full")), \
                mock.patch.object(compose, "render", FakeRender()):
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                att = compose.recompose("proj", "a", "og")
        self.assertIn("disk full", err.getvalue())
        self.assertNotIn("compose.log_failed", err.getvalue())  # translated
        self.assertIn("delivered", att)


class TemporaryFolderTests(RecomposeBase):
    def test_render_gets_a_prefix_of_its_own_that_the_worker_recovery_never_removes(self):
        self.made(count=2, choose=None)
        _, render = self.recompose(2)
        self.assertEqual(render.calls[0]["prefix"], ".compose-c2-")
        folder = self.folder("og")
        stale = folder / ".compose-c2-abc"
        stale.mkdir()
        (stale / "layer.png").write_bytes(b"x")
        self.enqueue("og")
        queue.claim()
        queue.recover_orphans()
        self.assertTrue(stale.exists())


@CON_HERRAMIENTAS
class WithToolsTests(RecomposeBase):
    def test_a_new_title_recomposes_the_chosen_attempt_and_delivers_it_again_without_generating(self):
        self.made(choose=1, text={"title": "Before"})
        before = self.delivered().read_bytes()
        raw = (self.folder("og") / "q1.raw.png").read_bytes()
        att, _ = self.real_recompose(text={"title": "After & <more>"})
        self.assertEqual(att["compose"]["text"], {"title": "After & <more>", "subtitle": ""})
        self.assertEqual(png.size(self.delivered()), (1200, 630))
        self.assertNotEqual(self.delivered().read_bytes(), before)
        self.assertEqual(self.delivered().read_bytes(), (self.folder("og") / "q1.png").read_bytes())
        self.assertEqual((self.folder("og") / "q1.raw.png").read_bytes(), raw)  # the raw image is never touched
        self.assertEqual(self.manifest()["compose"]["text"]["title"], "After & <more>")
        chunk = json.loads(png.read_text_chunks(self.delivered())["gimg"])
        self.assertEqual(chunk["compose"]["text"]["title"], "After & <more>")
        self.assertEqual(self.names("og"), ["q1.png", "q1.raw.png"])
        self.assertEqual(len(queue.list_entries()), 1)

    def test_an_attempt_made_before_f2_8_is_composed_from_a_copy_of_its_image(self):
        self.made(choose=1)
        old = self.make_old(1)
        att, _ = self.real_recompose(text={"title": "Hi"})
        self.assertEqual((self.folder("og") / "q1.raw.png").read_bytes(), old)
        self.assertEqual((att["image"], png.size(self.delivered())), ("attempts/q1.png", (1200, 630)))

    def test_a_broken_template_fails_with_the_tool_reason_and_keeps_the_delivered_file(self):
        self.made(choose=1)
        before = self.delivered().read_bytes()
        (self.root / "t.svg").write_text("<svg", encoding="utf-8")
        with self.assertRaises(GimgError) as cm:
            compose.recompose("proj", "a", "og")
        self.assertEqual((cm.exception.code, cm.exception.params["tool"]), ("compose.tool_failed", "rsvg-convert"))
        self.assertTrue(cm.exception.params["reason"])
        self.assertEqual(self.delivered().read_bytes(), before)
        self.assertEqual(self.attempt("og")["composeError"]["code"], "compose.tool_failed")
        self.assertFalse([n for n in self.names("og") if n.startswith(".compose")])  # no temporary folder left

    def real_recompose(self, *args, **kw):
        with mock.patch.object(engine.FakeEngine, "generate", side_effect=AssertionError("generated")):
            return compose.recompose("proj", "a", "og", *args, **kw), None

    def made(self, count=1, choose=1, **extra):  # the real tools compose what the worker generates
        self.submit("og", **extra)
        self.enqueue("og", count=count)
        self.run_worker()
        if choose:
            delivery.choose("proj", "a", "og", choose)


if __name__ == "__main__":
    unittest.main()
