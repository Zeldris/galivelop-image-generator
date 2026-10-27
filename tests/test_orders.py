import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import orders, paths, projects
from gimg.errors import GimgError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())


class OrderTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data")})
        env.start()
        self.addCleanup(env.stop)
        root = self.tmp / "proj"
        root.mkdir()
        self.cfg = copy.deepcopy(EXAMPLE)
        self.cfg.pop("$schema", None)
        self.cfg["name"] = "proj"
        self.write_cfg()
        projects.add(root)
        self.root = root

    def write_cfg(self):
        (self.tmp / "proj" / "galivelop-images.json").write_text(json.dumps(self.cfg))

    def order(self, **changes):
        data = {"key": "a", "profile": "banner", "prompt": "a cat"}
        data.update(changes)
        return data

    def code(self, fn, *args, **kwargs):
        with self.assertRaises(GimgError) as cm:
            fn(*args, **kwargs)
        return cm.exception.code

    def spec(self, n=1):
        return {"seed": n, "prompt": "p%d" % n, "params": {"steps": 6}}

    def new_order(self, attempts=0, **changes):
        orders.submit("proj", self.order(**changes))
        key, profile = changes.get("key", "a"), changes.get("profile", "banner")
        for n in range(1, attempts + 1):
            orders.add_attempt("proj", key, profile, self.spec(n))

    # storage and submit
    def test_create_and_path(self):
        rec = orders.submit("proj", self.order(references=["r.png"], seed=5, params={"steps": 9}))
        self.assertEqual((rec["chosen"], rec["chosenHistory"], rec["attempts"]), (None, [], []))
        self.assertEqual((rec["seed"], rec["references"], rec["params"]), (5, ["r.png"], {"steps": 9}))
        self.assertRegex(rec["createdAt"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        f = self.tmp / "data" / "projects" / "proj" / "orders" / "a" / "@banner" / "order.json"
        self.assertTrue(f.is_file())
        self.assertEqual(orders.get("proj", "a", "banner"), rec)
        rec = orders.get("proj", "a", "banner")
        rec["attempts"].append({"image": "attempts/3.png"})
        self.assertEqual(orders.attempt_image("proj", "a", "banner", rec["attempts"][0]), f.parent / "attempts" / "3.png")
        self.assertEqual(orders.pending_image_path("proj", "a", "banner", 4), f.parent / "attempts" / ".pending-4.png")

    def test_count_not_stored(self):
        self.assertNotIn("count", orders.submit("proj", self.order(count=3)))

    def test_resubmit_keeps_attempts_and_updates(self):
        self.new_order(attempts=2, seed=1)
        orders.choose("proj", "a", "banner", 2)
        first = orders.get("proj", "a", "banner")
        rec = orders.submit("proj", self.order(prompt="a dog", references=["x.png"], params={"cfg": 2}))
        self.assertEqual((rec["prompt"], rec["references"], rec["params"], rec["seed"]),
                         ("a dog", ["x.png"], {"cfg": 2}, None))
        self.assertEqual(rec["attempts"], first["attempts"])
        self.assertEqual((rec["chosen"], rec["chosenHistory"]), (2, [None]))
        self.assertEqual(rec["createdAt"], first["createdAt"])

    def test_slash_key_does_not_collide_with_profile(self):
        orders.submit("proj", self.order(key="a/banner", profile="thumbnail", prompt="one"))
        orders.submit("proj", self.order(key="a", profile="banner", prompt="two"))
        self.assertEqual(orders.get("proj", "a/banner", "thumbnail")["prompt"], "one")
        self.assertEqual(orders.get("proj", "a", "banner")["prompt"], "two")
        self.assertEqual(len(orders.list_orders("proj")), 2)

    def test_bad_project_name_in_paths(self):
        for bad in (".", "..", "a/b", "A"):
            self.assertEqual(self.code(orders.pending_image_path, bad, "a", "banner", 1),
                             "project.bad_name", bad)

    def test_submit_failures(self):
        self.assertEqual(self.code(orders.submit, "proj", self.order(profile="nope")), "order.profile_unknown")
        self.assertEqual(self.code(orders.submit, "proj", self.order(prompt="")), "order.invalid")
        self.assertEqual(self.code(orders.submit, "proj", self.order(key="../x")), "order.invalid")
        self.assertEqual(self.code(orders.submit, "proj", {"key": "a"}), "order.invalid")
        self.assertEqual(self.code(orders.submit, "proj", self.order(key="/".join(["a" * 101, "b"]))),
                         "key.segment_too_long")
        self.assertEqual(self.code(orders.submit, "nope", self.order()), "project.unknown")
        self.assertEqual(self.code(orders.get, "proj", "zz", "banner"), "order.unknown")
        err = None
        try:
            orders.submit("proj", self.order(seed=-1))
        except GimgError as exc:
            err = exc
        self.assertTrue(err.errors)

    # attempt specs
    def test_seeds_from_order_seed(self):
        self.new_order(seed=10)
        self.assertEqual([s["seed"] for s in orders.attempt_specs("proj", "a", "banner", 3)], [10, 11, 12])
        self.assertEqual([s["seed"] for s in orders.attempt_specs("proj", "a", "banner", 2, seed=100)], [100, 101])

    def test_seed_zero_is_a_seed(self):
        self.new_order(seed=0)
        self.assertEqual([s["seed"] for s in orders.attempt_specs("proj", "a", "banner", 2)], [0, 1])

    def test_random_seeds_without_seed(self):
        self.new_order()
        seeds = [s["seed"] for s in orders.attempt_specs("proj", "a", "banner", 20)]
        self.assertTrue(all(0 <= s < 2 ** 32 for s in seeds))
        self.assertGreater(len(set(seeds)), 1)

    def test_param_precedence(self):
        self.new_order(params={"steps": 9, "cfg": 2.5})
        full = orders.attempt_specs("proj", "a", "banner")[0]["params"]
        self.assertEqual(full, {"width": 1280, "height": 512, "steps": 9, "cfg": 2.5,
                                "sampler": "euler", "model": "flux2-klein-4b-q8"})
        over = orders.attempt_specs("proj", "a", "banner", params={"steps": 20})[0]["params"]
        self.assertEqual((over["steps"], over["cfg"]), (20, 2.5))

    def test_style_join_and_empty_style(self):
        self.new_order()
        self.assertEqual(orders.attempt_specs("proj", "a", "banner")[0]["prompt"],
                         "a cat, flat illustration, soft colors, no text")
        self.cfg["profiles"]["banner"]["style"] = ""
        self.write_cfg()
        self.assertEqual(orders.attempt_specs("proj", "a", "banner")[0]["prompt"], "a cat")

    def test_prompt_plus_style_too_long_fails_before_queueing(self):
        limit = 4000
        style = self.cfg["profiles"]["banner"]["style"]
        self.new_order(prompt="x" * (limit - 3))  # fits alone, not with ", " + style
        with self.assertRaises(GimgError) as cm:
            orders.attempt_specs("proj", "a", "banner")
        self.assertEqual(cm.exception.code, "order.prompt_too_long")
        self.assertEqual(cm.exception.params, {"length": limit - 3 + 2 + len(style), "max": limit})
        self.cfg["profiles"]["banner"]["style"] = ""
        self.write_cfg()
        self.assertEqual(len(orders.attempt_specs("proj", "a", "banner")[0]["prompt"]), limit - 3)

    def test_retouch_does_not_change_order(self):
        self.new_order(seed=3)
        before = orders.get("proj", "a", "banner")
        spec = orders.attempt_specs("proj", "a", "banner", prompt="a bird", params={"steps": 2})[0]
        self.assertTrue(spec["prompt"].startswith("a bird, "))
        self.assertEqual(spec["params"]["steps"], 2)
        self.assertEqual(orders.get("proj", "a", "banner"), before)

    def test_spec_failures(self):
        self.new_order()
        f = orders.attempt_specs
        self.assertEqual(self.code(f, "proj", "a", "banner", 0), "order.count_invalid")
        self.assertEqual(self.code(f, "proj", "a", "banner", 51), "order.count_invalid")
        self.assertEqual(self.code(f, "proj", "a", "banner", params={"steps": 0}), "order.invalid")
        self.assertEqual(self.code(f, "proj", "a", "banner", params={"bogus": 1}), "order.invalid")
        self.assertEqual(self.code(f, "proj", "a", "banner", prompt=""), "order.invalid")
        self.assertEqual(self.code(f, "proj", "zz", "banner"), "order.unknown")

    # attempts, states, notes
    def test_add_attempt(self):
        self.new_order(references=["r.png"])
        ids = [orders.add_attempt("proj", "a", "banner", self.spec(n)) for n in (1, 2, 3)]
        self.assertEqual(ids, [1, 2, 3])
        att = orders.get("proj", "a", "banner")["attempts"][1]
        self.assertEqual((att["id"], att["state"], att["note"], att["seed"]), (2, "new", "", 2))
        self.assertEqual((att["image"], att["references"]), ("attempts/2.png", ["r.png"]))
        self.assertRegex(att["createdAt"], r"^\d{4}-")
        self.assertEqual(self.code(orders.add_attempt, "proj", "a", "banner", {"seed": 1}), "order.spec_invalid")
        self.assertEqual(self.code(orders.add_attempt, "proj", "zz", "banner", self.spec()), "order.unknown")

    def test_mark_and_note(self):
        self.new_order(attempts=2)
        self.assertEqual(orders.mark("proj", "a", "banner", 1, "candidate")["state"], "candidate")
        self.assertEqual(orders.mark("proj", "a", "banner", 1, "discarded")["state"], "discarded")
        self.assertEqual(orders.note("proj", "a", "banner", 2, "nice")["note"], "nice")
        self.assertEqual(orders.get("proj", "a", "banner")["attempts"][1]["note"], "nice")
        self.assertEqual(orders.note("proj", "a", "banner", 2, "")["note"], "")
        self.assertEqual(self.code(orders.mark, "proj", "a", "banner", 1, "bogus"), "order.state_invalid")
        self.assertEqual(self.code(orders.mark, "proj", "a", "banner", 9, "new"), "order.attempt_unknown")
        self.assertEqual(self.code(orders.note, "proj", "a", "banner", 9, "x"), "order.attempt_unknown")
        self.assertEqual(self.code(orders.note, "proj", "a", "banner", 1, 5), "order.note_invalid")

    def test_cannot_discard_chosen_nor_choose_discarded(self):
        self.new_order(attempts=2)
        orders.mark("proj", "a", "banner", 2, "discarded")
        self.assertEqual(self.code(orders.choose, "proj", "a", "banner", 2), "order.choose_discarded")
        orders.choose("proj", "a", "banner", 1)
        self.assertEqual(self.code(orders.mark, "proj", "a", "banner", 1, "discarded"), "order.discard_chosen")
        self.assertEqual(orders.mark("proj", "a", "banner", 1, "candidate")["state"], "candidate")
        orders.undo("proj", "a", "banner")
        self.assertEqual(orders.mark("proj", "a", "banner", 1, "discarded")["state"], "discarded")

    # choose and undo
    def test_choose_undo_stack(self):
        self.new_order(attempts=3)
        c = lambda i: orders.choose("proj", "a", "banner", i)
        self.assertEqual(c(1), {"old": None, "new": 1})
        self.assertEqual(c(3), {"old": 1, "new": 3})
        self.assertEqual(c(3), {"old": 3, "new": 3})  # no push when unchanged
        rec = orders.get("proj", "a", "banner")
        self.assertEqual((rec["chosen"], rec["chosenHistory"]), (3, [None, 1]))
        self.assertEqual(orders.undo("proj", "a", "banner"), {"old": 3, "new": 1})
        self.assertEqual(orders.undo("proj", "a", "banner"), {"old": 1, "new": None})
        rec = orders.get("proj", "a", "banner")
        self.assertEqual((rec["chosen"], rec["chosenHistory"]), (None, []))
        self.assertEqual(self.code(orders.undo, "proj", "a", "banner"), "order.history_empty")
        self.assertEqual(self.code(orders.choose, "proj", "a", "banner", 9), "order.attempt_unknown")
        self.assertEqual(self.code(orders.undo, "proj", "zz", "banner"), "order.unknown")

    # listing
    def test_list_orders_filters(self):
        self.new_order(attempts=1, key="b")
        self.new_order(key="a")
        self.new_order(key="a", profile="thumbnail")
        orders.choose("proj", "b", "banner", 1)
        keys = lambda **kw: [(o["key"], o["profile"]) for o in orders.list_orders("proj", **kw)]
        self.assertEqual(keys(), [("a", "banner"), ("a", "thumbnail"), ("b", "banner")])
        self.assertEqual(keys(profile="thumbnail"), [("a", "thumbnail")])
        self.assertEqual(keys(chosen=True), [("b", "banner")])
        self.assertEqual(keys(chosen=False), [("a", "banner"), ("a", "thumbnail")])
        self.assertEqual(self.code(orders.list_orders, "nope"), "project.unknown")

    def test_list_empty_project(self):
        self.assertEqual(orders.list_orders("proj"), [])

    def test_corrupt_order(self):
        self.new_order()
        (paths.data_dir() / "projects/proj/orders/a/@banner/order.json").write_text("{nope")
        self.assertEqual(self.code(orders.get, "proj", "a", "banner"), "order.corrupt")

    def test_undo_rejects_discarded(self):
        self.new_order(attempts=2)
        orders.choose("proj", "a", "banner", 1)
        orders.choose("proj", "a", "banner", 2)
        orders.mark("proj", "a", "banner", 1, "discarded")
        before = orders.get("proj", "a", "banner")
        with self.assertRaises(GimgError) as cm:
            orders.undo("proj", "a", "banner")
        self.assertEqual((cm.exception.code, cm.exception.params), ("order.undo_discarded", {"attempt": 1}))
        self.assertEqual(orders.get("proj", "a", "banner"), before)
        for lang in ("es", "en"):
            self.assertNotIn("error.", cm.exception.message(lang))
        orders.mark("proj", "a", "banner", 1, "candidate")
        self.assertEqual(orders.undo("proj", "a", "banner"), {"old": 2, "new": 1})

    def test_undo_to_null_allowed_even_if_all_discarded(self):
        self.new_order(attempts=1)
        orders.choose("proj", "a", "banner", 1)
        self.assertEqual(orders.undo("proj", "a", "banner"), {"old": 1, "new": None})

    def test_bad_key_or_profile_everywhere(self):
        self.new_order(attempts=1)
        for key, profile in [("a//b", "banner"), ("a/./b", "banner"), ("a/@b", "banner"),
                             ("a", "p/q"), ("A B", "banner")]:
            for fn, args in [(orders.get, ()), (orders.choose, (1,)), (orders.pending_image_path, (1,)), (orders.attempt_for_entry, (1,)),
                             (orders.attempt_image, ({"image": "attempts/1.png"},)),
                             (orders.mark, (1, "new")), (orders.note, (1, "x")), (orders.undo, ()),
                             (orders.add_attempt, (self.spec(),)), (orders.attempt_specs, ())]:
                self.assertEqual(self.code(fn, "proj", key, profile, *args), "order.invalid", (fn, key, profile))

    def test_bool_is_not_attempt_id(self):
        self.new_order(attempts=1)
        self.assertEqual(self.code(orders.choose, "proj", "a", "banner", True), "order.attempt_unknown")

    def test_list_orders_corrupt_shape(self):
        self.new_order()
        file = paths.data_dir() / "projects/proj/orders/a/@banner/order.json"
        good = json.loads(file.read_text())
        for bad in ({k: v for k, v in good.items() if k != "profile"},
                    {k: v for k, v in good.items() if k != "chosen"},
                    dict(good, attempts="x")):
            file.write_text(json.dumps(bad))
            self.assertEqual(self.code(orders.list_orders, "proj"), "order.corrupt")

    def test_add_attempt_for_entry_is_idempotent(self):
        self.new_order()
        first = orders.add_attempt("proj", "a", "banner", self.spec(1), entry_id=7)
        again = orders.add_attempt("proj", "a", "banner", self.spec(1), entry_id=7)
        other = orders.add_attempt("proj", "a", "banner", self.spec(2), entry_id=8)
        plain = orders.add_attempt("proj", "a", "banner", self.spec(3))
        self.assertEqual((first, again, other, plain), (1, 1, 2, 3))
        attempts = orders.get("proj", "a", "banner")["attempts"]
        self.assertEqual([(a["image"], a.get("queueEntry")) for a in attempts],
                         [("attempts/q7.png", 7), ("attempts/q8.png", 8), ("attempts/3.png", None)])
        self.assertEqual(orders.attempt_for_entry("proj", "a", "banner", 8)["id"], 2)
        self.assertIsNone(orders.attempt_for_entry("proj", "a", "banner", 9))
        folder = orders.pending_image_path("proj", "a", "banner", 7).parent
        self.assertEqual(orders.attempt_image("proj", "a", "banner", attempts[0]), folder / "q7.png")
        for bad in (0, -1, True, "7", 1.5):
            self.assertEqual(self.code(orders.add_attempt, "proj", "a", "banner", self.spec(), entry_id=bad),
                             "order.spec_invalid", bad)

    def test_attempt_image_stays_inside_order_folder(self):
        self.new_order()
        for image in ("../order.json", "/etc/x", "attempts/../../x"):
            self.assertIn(self.code(orders.attempt_image, "proj", "a", "banner", {"image": image}),
                          ("path.dotdot", "path.absolute", "path.dotdot"), image)

    def test_add_attempt_validates_fields(self):
        self.new_order()
        for spec in ({"seed": "1", "prompt": "p", "params": {}}, {"seed": -1, "prompt": "p", "params": {}},
                     {"seed": 1, "prompt": 3, "params": {}}, {"seed": 1, "prompt": "p", "params": []},
                     {"seed": 1, "prompt": "p", "params": {"steps": 0}},
                     {"seed": 1, "prompt": "p", "params": {"width": "x"}}):
            self.assertEqual(self.code(orders.add_attempt, "proj", "a", "banner", spec), "order.invalid", spec)
        full = {"seed": 1, "prompt": "p", "params": {"width": 8, "height": 8, "steps": 2, "cfg": 1, "sampler": "s", "model": "m"}}
        self.assertEqual(orders.add_attempt("proj", "a", "banner", full), 1)

    def test_messages_in_both_languages(self):
        for lang in ("es", "en"):
            try:
                orders.undo("proj", "zz", "banner")
            except GimgError as exc:
                self.assertNotIn("error.", exc.message(lang))


class ComposeOrderTests(unittest.TestCase):
    """F2.8: `text` in the order, and the raw / composed images of an attempt."""
    write_cfg, order, code, spec = OrderTests.write_cfg, OrderTests.order, OrderTests.code, OrderTests.spec

    def setUp(self):
        OrderTests.setUp(self)
        self.cfg["profiles"]["og"] = dict(self.cfg["profiles"]["banner"], width=1280, height=640,
                                          targetWidth=1200, targetHeight=630,
                                          compose={"template": "t.svg", "fields": ["title", "subtitle"]})
        self.write_cfg()

    def og(self, **changes):
        return self.order(profile="og", **changes)

    def reason(self, fn, *args):
        with self.assertRaises(GimgError) as cm:
            fn(*args)
        return cm.exception

    def test_submit_stores_text_and_defaults_to_empty(self):
        self.assertEqual(orders.submit("proj", self.og(text={"title": "Hi"}))["text"], {"title": "Hi"})
        self.assertEqual(orders.submit("proj", self.og())["text"], {})  # resubmitting replaces it, like the other fields
        self.assertEqual(orders.submit("proj", self.order())["text"], {})  # a profile without compose: always {}

    def test_text_outside_compose_fields_names_the_field_the_profile_and_the_valid_ones(self):
        exc = self.reason(orders.submit, "proj", self.og(text={"title": "x", "headline": "y"}))
        self.assertEqual((exc.code, exc.params), ("order.text_unknown_field", {
            "field": "headline", "profile": "og", "fields": "title, subtitle"}))
        exc = self.reason(orders.submit, "proj", self.order(text={"title": "x"}))  # banner has no compose at all
        self.assertEqual((exc.code, exc.params["fields"]), ("order.text_unknown_field", "-"))
        with self.assertRaises(GimgError):
            orders.get("proj", "a", "og")  # nothing was stored

    def test_attempt_specs_copy_the_text_and_never_share_it(self):
        orders.submit("proj", self.og(text={"title": "Hi"}))
        specs = orders.attempt_specs("proj", "a", "og", 2)
        self.assertEqual([s["text"] for s in specs], [{"title": "Hi"}] * 2)
        specs[0]["text"]["title"] = "changed"
        self.assertEqual(orders.get("proj", "a", "og")["text"], {"title": "Hi"})
        self.assertEqual(specs[1]["text"], {"title": "Hi"})

    def test_an_order_stored_before_f2_8_has_no_text_and_still_gives_specs(self):
        orders.submit("proj", self.og())
        path = orders._order_file("proj", "a", "og")
        data = json.loads(path.read_text())
        del data["text"]
        path.write_text(json.dumps(data))
        self.assertEqual(orders.attempt_specs("proj", "a", "og")[0]["text"], {})
        self.assertEqual(orders.set_text("proj", "a", "og", {"title": "T"}), {"title": "T"})

    def test_set_text_merges_into_the_order(self):
        orders.submit("proj", self.og(text={"title": "Hi", "subtitle": "there"}))
        self.assertEqual(orders.set_text("proj", "a", "og", {"title": "Bye"}), {"title": "Bye", "subtitle": "there"})
        self.assertEqual(orders.get("proj", "a", "og")["text"], {"title": "Bye", "subtitle": "there"})
        self.assertEqual(orders.set_text("proj", "a", "og", {"subtitle": ""})["subtitle"], "")
        self.assertEqual(orders.attempt_specs("proj", "a", "og")[0]["text"], {"title": "Bye", "subtitle": ""})

    def test_set_text_rejects_what_submit_rejects_and_changes_nothing(self):
        orders.submit("proj", self.og(text={"title": "Hi"}))
        before = orders.get("proj", "a", "og")
        exc = self.reason(orders.set_text, "proj", "a", "og", {"nope": "x"})
        self.assertEqual((exc.code, exc.params["field"]), ("order.text_unknown_field", "nope"))
        self.assertEqual(self.code(orders.set_text, "proj", "a", "og", {"title": "x" * 201}), "order.invalid")
        self.assertEqual(self.code(orders.set_text, "proj", "a", "og", {"title": "a\nb"}), "order.invalid")
        self.assertEqual(self.code(orders.set_text, "proj", "a", "og", {"title": 5}), "order.invalid")
        self.assertEqual(self.code(orders.set_text, "proj", "a", "og", "x"), "order.invalid")
        self.assertEqual(self.code(orders.set_text, "proj", "zz", "og", {"title": "x"}), "order.unknown")
        self.assertEqual(orders.get("proj", "a", "og"), before)

    def test_add_attempt_keeps_raw_compose_and_compose_error_only_with_the_right_type(self):
        orders.submit("proj", self.og())
        info = {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "text": {}}
        orders.add_attempt("proj", "a", "og", dict(self.spec(1), raw="attempts/q1.raw.png", compose=info), entry_id=1)
        orders.add_attempt("proj", "a", "og", dict(self.spec(2), raw=5, compose="x", composeError="x"), entry_id=2)
        orders.add_attempt("proj", "a", "og", dict(self.spec(3), composeError={"code": 3, "params": {}}), entry_id=3)
        orders.add_attempt("proj", "a", "og", dict(self.spec(4), composeError={"code": "c", "params": []}), entry_id=4)
        first, wrong, bad_code, bad_params = orders.get("proj", "a", "og")["attempts"]
        self.assertEqual((first["raw"], first["compose"], first["image"]), ("attempts/q1.raw.png", info, "attempts/q1.png"))
        for att in (wrong, bad_code, bad_params):
            self.assertTrue({"raw", "compose", "composeError"}.isdisjoint(att), att)

    def test_add_attempt_with_a_compose_error_shows_the_raw_image(self):
        orders.submit("proj", self.og())
        error = {"code": "compose.tool_missing", "params": {"tool": "ffmpeg"}}
        orders.add_attempt("proj", "a", "og", dict(self.spec(1), raw="attempts/q1.raw.png", composeError=error), entry_id=1)
        att = orders.get("proj", "a", "og")["attempts"][0]
        self.assertEqual((att["image"], att["raw"], att["composeError"]), ("attempts/q1.raw.png", "attempts/q1.raw.png", error))
        # a compose error without a raw image changes nothing about where the image is
        orders.add_attempt("proj", "a", "og", dict(self.spec(2), composeError=error), entry_id=2)
        self.assertEqual(orders.get("proj", "a", "og")["attempts"][1]["image"], "attempts/q2.png")

    def test_raw_image_name_and_path(self):
        orders.submit("proj", self.og())
        self.assertEqual(orders.raw_image_name(7), "attempts/q7.raw.png")
        orders.add_attempt("proj", "a", "og", dict(self.spec(1), raw="attempts/q1.raw.png"), entry_id=1)
        orders.add_attempt("proj", "a", "og", self.spec(2), entry_id=2)  # made before F2.8: no raw
        one, two = orders.get("proj", "a", "og")["attempts"]
        folder = orders._order_dir("proj", "a", "og")
        self.assertEqual(orders.raw_image("proj", "a", "og", one), folder / "attempts" / "q1.raw.png")
        self.assertEqual(orders.raw_image("proj", "a", "og", two), folder / "attempts" / "q2.png")
        self.assertEqual(self.code(orders.raw_image, "proj", "a", "og", dict(one, raw="../../x.png")), "path.dotdot")

    def test_set_composed(self):
        orders.submit("proj", self.og())
        error = {"code": "compose.tool_missing", "params": {"tool": "ffmpeg"}}
        orders.add_attempt("proj", "a", "og", dict(self.spec(1), raw="attempts/q1.raw.png", composeError=error), entry_id=1)
        orders.add_attempt("proj", "a", "og", self.spec(2), entry_id=2)  # no raw: made before F2.8
        orders.add_attempt("proj", "a", "og", self.spec(3))  # no entry: attempts/3.png
        info = {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "text": {"title": "T"}}
        out = orders.set_composed("proj", "a", "og", 1, info)
        self.assertEqual((out["image"], out["raw"], out["compose"]), ("attempts/q1.png", "attempts/q1.raw.png", info))
        self.assertNotIn("composeError", out)
        out = orders.set_composed("proj", "a", "og", 2, info)
        self.assertEqual((out["image"], out["raw"]), ("attempts/q2.png", "attempts/q2.raw.png"))
        out = orders.set_composed("proj", "a", "og", 3, info)
        self.assertEqual((out["image"], out["raw"]), ("attempts/3.png", "attempts/3.raw.png"))
        stored = orders.get("proj", "a", "og")["attempts"][0]
        self.assertEqual((stored["image"], "composeError" in stored, stored["compose"]), ("attempts/q1.png", False, info))
        info["text"]["title"] = "changed after"
        self.assertEqual(orders.get("proj", "a", "og")["attempts"][0]["compose"]["text"], {"title": "T"})  # a copy
        self.assertEqual(self.code(orders.set_composed, "proj", "a", "og", 9, info), "order.attempt_unknown")
        self.assertEqual(self.code(orders.set_composed, "proj", "a", "og", 1, "x"), "order.spec_invalid")

    def test_an_attempt_that_failed_to_compose_cannot_be_chosen_until_it_is_composed(self):
        orders.submit("proj", self.og())
        error = {"code": "compose.tool_missing", "params": {"tool": "ffmpeg"}}
        orders.add_attempt("proj", "a", "og", dict(self.spec(1), raw="attempts/q1.raw.png", composeError=error), entry_id=1)
        self.assertEqual(self.code(orders.choose, "proj", "a", "og", 1), "order.choose_uncomposed")
        self.assertIsNone(orders.get("proj", "a", "og")["chosen"])
        orders.set_composed("proj", "a", "og", 1, {"fit": "cover", "targetWidth": 1, "targetHeight": 1, "text": {}})
        self.assertEqual(orders.choose("proj", "a", "og", 1), {"old": None, "new": 1})

    def test_the_other_choose_rules_still_come_first(self):
        orders.submit("proj", self.og())
        error = {"code": "compose.tool_missing", "params": {}}
        orders.add_attempt("proj", "a", "og", dict(self.spec(1), raw="attempts/q1.raw.png", composeError=error, draft=True), entry_id=1)
        self.assertEqual(self.code(orders.choose, "proj", "a", "og", 1), "order.choose_draft")
        orders.mark("proj", "a", "og", 1, "discarded")
        self.assertEqual(self.code(orders.choose, "proj", "a", "og", 1), "order.choose_discarded")

    def test_the_new_messages_exist_in_both_languages_and_use_their_params(self):
        for lang in ("es", "en"):
            exc = GimgError("order.text_unknown_field", field="headline", profile="og", fields="title")
            self.assertTrue(all(w in exc.message(lang) for w in ("headline", "og", "title")), lang)
            self.assertIn("7", GimgError("order.choose_uncomposed", attempt=7).message(lang))
            self.assertNotIn("error.", GimgError("order.choose_uncomposed", attempt=7).message(lang))


if __name__ == "__main__":
    unittest.main()
