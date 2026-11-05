"""F4b.1 (D39): templates a profile offers (`compose.templates`): the configuration, `compose.templates_of`/`effective`,
`render` and `recompose` with a template, the queue entry, the worker, `gimg templates`, `--template` and `gimg doctor`.

The pure parts need no tool; what composes for real is ``skipUnless`` ffmpeg and rsvg-convert (as in
`tests/test_compose_worker.py`)."""
import json
import unittest
from pathlib import Path
from unittest import mock

from gimg import compose, doctor, i18n, orders, projects, queue, schema
from gimg.errors import GimgError
from tests import test_cli, test_compose, test_compose_worker, test_doctor, test_recompose

ALT = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
       '<rect x="100" y="100" width="50" height="50" fill="#0000ff"/></svg>')
COMPOSE = {
    "template": "t.svg", "logo": "l.svg", "fields": ["title", "subtitle"], "fonts": ["Sora"], "fit": "contain",
    "zone": {"x": 10, "y": 20, "w": 300, "h": 100}, "textColor": "#ffffff",
    "templates": {
        "wide": {"template": "w.svg", "fields": ["title"], "zone": {"x": 0, "y": 0, "w": 50, "h": 50}},
        "alt": {"template": "alt.svg", "logo": "l2.svg", "textColor": "#000000"},
    },
}


def errors_of(compose_cfg):
    profile = {"width": 1280, "height": 640, "steps": 6, "cfg": 1.0, "sampler": "euler", "model": "m-default",
               "compose": compose_cfg}
    config = {"minVersion": "0.1.0", "name": "p", "delivery": {"dir": "o", "template": "{key}-{profile}.png"},
              "profiles": {"og": profile}}
    return [(e.path, e.code) for e in schema.validate(config, schema.load_schema("project-config"))]


class ConfigTests(unittest.TestCase):
    def test_a_full_configuration_is_valid(self):
        self.assertEqual(errors_of(COMPOSE), [])

    def test_default_is_a_reserved_id(self):
        bad = dict(COMPOSE, templates={"default": {"template": "x.svg"}})
        self.assertEqual(errors_of(bad), [("/profiles/og/compose/templates/default", "propertyNames")])

    def test_ids_are_lowercase_slugs(self):
        for name in ("Alt", "-a", "a b", "a" * 41, ""):
            bad = dict(COMPOSE, templates={name: {"template": "x.svg"}})
            self.assertEqual(errors_of(bad), [("/profiles/og/compose/templates/" + name, "propertyNames")], name)

    def test_at_most_twenty_templates(self):
        many = {"t%d" % i: {"template": "x.svg"} for i in range(21)}
        self.assertEqual(errors_of(dict(COMPOSE, templates=many)), [("/profiles/og/compose/templates", "maxProperties")])
        self.assertEqual(errors_of(dict(COMPOSE, templates=dict(list(many.items())[:20]))), [])

    def test_zone_and_text_colour_are_checked(self):
        self.assertEqual(errors_of(dict(COMPOSE, zone={"x": 1, "y": 2, "w": 0, "h": 4})),
                         [("/profiles/og/compose/zone/w", "minimum")])
        self.assertEqual(errors_of(dict(COMPOSE, zone={"x": 1, "y": 2, "w": 3})),
                         [("/profiles/og/compose/zone", "required")])
        self.assertEqual(errors_of(dict(COMPOSE, textColor="red")), [("/profiles/og/compose/textColor", "pattern")])
        bad = dict(COMPOSE, templates={"a": {"template": "x.svg", "textColor": "#12345"}})
        self.assertEqual(errors_of(bad), [("/profiles/og/compose/templates/a/textColor", "pattern")])

    def test_an_entry_needs_a_template_and_takes_nothing_unknown(self):
        self.assertEqual(errors_of(dict(COMPOSE, templates={"a": {"logo": "l.svg"}})),
                         [("/profiles/og/compose/templates/a", "required")])
        self.assertEqual(errors_of(dict(COMPOSE, templates={"a": {"template": "x.svg", "fit": "cover"}})),
                         [("/profiles/og/compose/templates/a/fit", "additionalProperties")])


class EffectiveTests(unittest.TestCase):
    def test_default_is_the_compose_of_the_profile_without_templates(self):
        for tid in (None, "default"):
            got = compose.effective(COMPOSE, tid)
            self.assertNotIn("templates", got)
            self.assertEqual((got["template"], got["logo"], got["fields"], got["zone"], got["textColor"]),
                             ("t.svg", "l.svg", ["title", "subtitle"], COMPOSE["zone"], "#ffffff"))

    def test_an_entry_inherits_logo_and_fields_and_keeps_fit_and_fonts_of_the_profile(self):
        wide = compose.effective(COMPOSE, "wide")
        self.assertEqual((wide["template"], wide["logo"], wide["fields"], wide["fit"], wide["fonts"]),
                         ("w.svg", "l.svg", ["title"], "contain", ["Sora"]))
        alt = compose.effective(COMPOSE, "alt")
        self.assertEqual((alt["template"], alt["logo"], alt["fields"]), ("alt.svg", "l2.svg", ["title", "subtitle"]))

    def test_zone_and_text_colour_belong_to_each_template(self):
        self.assertEqual(compose.effective(COMPOSE, "wide")["zone"], {"x": 0, "y": 0, "w": 50, "h": 50})
        self.assertNotIn("textColor", compose.effective(COMPOSE, "wide"))
        self.assertEqual(compose.effective(COMPOSE, "alt")["textColor"], "#000000")
        self.assertNotIn("zone", compose.effective(COMPOSE, "alt"))

    def test_an_unknown_id_says_what_exists(self):
        for cfg, tid, allowed in ((COMPOSE, "nope", "default, alt, wide"), (None, "x", ""), (None, "default", ""),
                                  ({"template": "t.svg"}, "x", "default"), (COMPOSE, 3, "default, alt, wide")):
            with self.assertRaises(GimgError) as cm:
                compose.effective(cfg, tid)
            self.assertEqual((cm.exception.code, cm.exception.params["allowed"]), ("compose.template_unknown", allowed))

    def test_a_profile_without_compose_has_the_default_none(self):
        self.assertEqual(compose.effective(None), {})

    def test_templates_of_lists_default_first_then_by_id(self):
        items = compose.templates_of({"compose": COMPOSE})
        self.assertEqual([(i["id"], i["default"], i["template"], i["logo"]) for i in items],
                         [("default", True, "t.svg", "l.svg"), ("alt", False, "alt.svg", "l2.svg"),
                          ("wide", False, "w.svg", "l.svg")])
        self.assertEqual(items[2]["fields"], ["title"])
        self.assertEqual((items[0]["zone"], items[0]["textColor"]), (COMPOSE["zone"], "#ffffff"))
        self.assertNotIn("zone", items[1])

    def test_templates_of_a_profile_without_compose_is_empty_and_without_logo_is_none(self):
        self.assertEqual(compose.templates_of({"width": 64}), [])
        self.assertIsNone(compose.templates_of({"compose": {"template": "t.svg"}})[0]["logo"])

    def test_the_error_has_text_in_both_languages(self):
        for lang in ("es", "en"):
            text = i18n.t("error.compose.template_unknown", lang, template="zz", allowed="default")
            self.assertIn("zz", text)
            self.assertNotIn("{", text)


class TemplateBase(test_compose_worker.ComposeWorkerBase):
    def setUp(self):
        super().setUp()
        (self.root / "alt.svg").write_text(ALT, encoding="utf-8")
        self.profiles({"og": dict(test_compose_worker.BASE, targetWidth=1200, targetHeight=630, compose={
            "template": "t.svg", "fields": ["title", "subtitle"], "templates": {"alt": {"template": "alt.svg"}}})})


@test_compose_worker.CON_HERRAMIENTAS
class RenderWithTemplateTests(TemplateBase):
    def render(self, template):
        raw, out = self.root / "raw.png", self.root / "out.png"
        test_compose.striped_png(raw, 1280, 640)
        cfg = orders.projects.get("proj")["config"]["profiles"]["og"]
        info = compose.render(self.root, cfg, raw, out, {"title": "x"}, "og", template=template)
        return info, test_compose.pixels(out, 1200, 630)

    def test_the_default_template_is_the_one_of_compose(self):
        for tid in (None, "default"):
            info, at = self.render(tid)
            self.assertEqual((info["template"], info["templateId"]), ("t.svg", "default"))
            test_compose.near(self, at(125, 125), (0, 255, 0))

    def test_another_template_paints_its_own_layer_and_the_info_says_which(self):
        info, at = self.render("alt")
        self.assertEqual((info["template"], info["templateId"]), ("alt.svg", "alt"))
        test_compose.near(self, at(125, 125), (0, 0, 255))

    def test_an_unknown_template_fails_before_any_tool_runs(self):
        with mock.patch.object(compose.subprocess, "run", side_effect=AssertionError("a tool was called")):
            with self.assertRaises(GimgError) as cm:
                self.render("nope")
        self.assertEqual((cm.exception.code, cm.exception.params["template"]), ("compose.template_unknown", "nope"))

    def test_a_profile_that_only_has_a_target_has_no_template_id(self):
        raw, out = self.root / "raw.png", self.root / "out.png"
        test_compose.striped_png(raw, 1280, 640)
        info = compose.render(self.root, self.profile_cfg("scaled"), raw, out, {}, "scaled")
        self.assertNotIn("templateId", info)
        with self.assertRaises(GimgError) as cm:
            compose.render(self.root, self.profile_cfg("scaled"), raw, out, {}, "scaled", template="alt")
        self.assertEqual(cm.exception.code, "compose.template_unknown")

    def profile_cfg(self, name):
        return orders.projects.get("proj")["config"]["profiles"][name]


class QueueTemplateTests(TemplateBase):
    def test_the_entry_carries_the_template_and_an_older_way_has_none(self):
        self.submit("og")
        self.enqueue("og", template="alt")
        self.enqueue("og")
        self.assertEqual([e["template"] for e in queue.list_entries()], ["alt", None])

    def test_an_unknown_template_is_refused_before_anything_is_queued(self):
        self.submit("og")
        self.assertEqual(self.code(self.enqueue, "og", count=3, template="nope"), "compose.template_unknown")
        self.assertEqual(self.code(queue.new_attempts, "proj", "a", "og", 2, template="nope"),
                         "compose.template_unknown")
        self.assertEqual(queue.list_entries(), [])

    def test_a_profile_without_compose_refuses_any_template(self):
        self.submit("plain")
        self.assertEqual(self.code(self.enqueue, "plain", template="alt"), "compose.template_unknown")
        self.assertEqual(queue.list_entries(), [])

    def test_the_worker_composes_with_the_template_of_the_entry(self):
        self.submit("og")
        self.enqueue("og", template="alt")
        self.enqueue("og")
        calls = []

        def fake(root, cfg, raw, out, text, profile=None, prefix=None, **kw):
            calls.append(kw)
            Path(out).write_bytes(Path(raw).read_bytes())
            return {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg", "text": {},
                    "templateId": kw.get("template", "default")}

        with mock.patch.object(compose, "render", fake):
            self.assertEqual(self.run_worker()[0], 2)
        self.assertEqual(calls, [{"template": "alt"}, {}])
        self.assertEqual([self.attempt("og", i)["compose"]["templateId"] for i in (0, 1)], ["alt", "default"])

    def test_a_worker_failure_with_a_template_is_fixed_by_compose_with_the_same_one(self):
        self.submit("og")
        self.enqueue("og", template="alt")
        with mock.patch.object(compose, "render", side_effect=GimgError("compose.tool_failed", tool="x", reason="y")):
            self.run_worker()
        att = self.attempt("og")
        self.assertEqual((att["composeError"]["code"], att["composeError"]["templateId"]),
                         ("compose.tool_failed", "alt"))
        seen = []

        def fake(root, cfg, raw, out, text, profile=None, prefix=None, template=None):
            seen.append(template)
            Path(out).write_bytes(Path(raw).read_bytes())
            return {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "alt.svg", "text": {},
                    "templateId": template or "default"}

        with mock.patch.object(compose, "render", fake):
            done = compose.recompose("proj", "a", "og")
        self.assertEqual((seen, done["compose"]["templateId"], "composeError" in done), (["alt"], "alt", False))

    @test_compose_worker.CON_HERRAMIENTAS
    def test_for_real_the_attempt_records_the_template_and_its_layer(self):
        self.submit("og")
        self.enqueue("og", template="alt")
        self.assertEqual(self.run_worker()[0], 1)
        att = self.attempt("og")
        self.assertEqual((att["compose"]["templateId"], att["compose"]["template"]), ("alt", "alt.svg"))
        at = test_compose.pixels(orders.attempt_image("proj", "a", "og", att),
                                 1200, 630)
        test_compose.near(self, at(125, 125), (0, 0, 255))

    def test_a_template_removed_before_the_worker_composes_leaves_the_error_on_the_attempt(self):
        self.submit("og")
        self.enqueue("og", template="alt")
        self.profiles({"og": dict(test_compose_worker.BASE, targetWidth=1200, targetHeight=630,
                                  compose={"template": "t.svg", "fields": ["title"]})})
        self.assertEqual(self.run_worker()[0], 1)
        att = self.attempt("og")
        self.assertEqual(att["composeError"]["code"], "compose.template_unknown")
        self.assertEqual(att["composeError"]["params"]["template"], "alt")
        self.assertEqual(queue.get(1)["state"], "done")


class RecomposeTemplateTests(test_recompose.RecomposeBase):
    """`recompose` with a fake render that echoes the template it was given (the real tools are in the class above)."""

    def setUp(self):
        super().setUp()
        self.profiles({"og": dict(test_compose_worker.BASE, targetWidth=1200, targetHeight=630, compose={
            "template": "t.svg", "fields": ["title", "subtitle"], "templates": {"alt": {"template": "alt.svg"}}})})

    class Echo(test_recompose.FakeRender):
        def __call__(self, root, cfg, raw, out, text, profile=None, prefix=None, template=None):
            info = super().__call__(root, cfg, raw, out, text, profile, prefix)
            self.calls[-1]["template"] = template
            compose.effective(cfg.get("compose"), template)  # as the real render does
            return dict(info, templateId=template or "default")

    def go(self, *args, **kw):
        return self.recompose(*args, render=self.Echo(), **kw)

    def test_with_a_template_it_is_used_and_kept_by_the_attempt(self):
        self.made()
        att, render = self.go(template="alt")
        self.assertEqual((render.calls[0]["template"], att["compose"]["templateId"]), ("alt", "alt"))
        self.assertEqual(self.attempt("og")["compose"]["templateId"], "alt")

    def test_without_one_the_template_of_the_attempt_is_kept(self):
        self.made()
        self.go(template="alt")
        att, render = self.go(text={"title": "New"})
        self.assertEqual((render.calls[0]["template"], att["compose"]["templateId"]), ("alt", "alt"))

    def test_an_attempt_that_had_none_uses_default(self):
        self.made()
        att, render = self.go()
        self.assertEqual((render.calls[0]["template"], att["compose"]["templateId"]), (None, "default"))

    def test_default_can_be_chosen_again(self):
        self.made()
        self.go(template="alt")
        att, _ = self.go(template="default")
        self.assertEqual(att["compose"]["templateId"], "default")

    def test_an_unknown_template_changes_nothing(self):
        self.made(choose=1)
        before = (self.attempt("og"), self.delivered().read_bytes())
        render = self.Echo()
        with self.assertRaises(GimgError) as cm:
            self.recompose(template="nope", render=render)
        self.assertEqual((cm.exception.code, cm.exception.params["template"]), ("compose.template_unknown", "nope"))
        self.assertEqual(render.calls, [])
        self.assertEqual((self.attempt("og"), self.delivered().read_bytes()), before)

    def test_a_failed_recompose_with_a_template_keeps_it_for_the_next_one(self):
        self.made()
        failing = self.Echo(fail=GimgError("compose.tool_failed", tool="rsvg-convert", reason="x"))
        with self.assertRaises(GimgError):
            self.recompose(template="alt", render=failing)
        att = self.attempt("og")
        self.assertEqual((att["composeError"]["code"], att["composeError"]["templateId"]),
                         ("compose.tool_failed", "alt"))
        self.assertNotIn("compose", att)
        done, render = self.go()
        self.assertEqual((render.calls[0]["template"], done["compose"]["templateId"]), ("alt", "alt"))
        self.assertNotIn("composeError", done)

    def test_a_failure_while_recomposing_keeps_the_template_the_attempt_already_had(self):
        self.made()
        self.go(template="alt")
        with self.assertRaises(GimgError):
            self.recompose(render=self.Echo(fail=GimgError("compose.tool_failed", tool="ffmpeg", reason="x")))
        self.assertEqual(self.attempt("og")["composeError"]["templateId"], "alt")

    def test_a_stored_template_that_no_longer_exists_fails_and_is_not_replaced_by_another(self):
        self.made()
        self.go(template="alt")
        self.profiles({"og": dict(test_compose_worker.BASE, targetWidth=1200, targetHeight=630,
                                  compose={"template": "t.svg", "fields": ["title"]})})
        render = self.Echo()
        with self.assertRaises(GimgError) as cm:
            self.recompose(render=render)
        self.assertEqual(cm.exception.code, "compose.template_unknown")
        self.assertEqual(render.calls[0]["template"], "alt")
        self.assertEqual(self.attempt("og")["composeError"]["code"], "compose.template_unknown")
        att, _ = self.go(template="default")  # the way out: another template
        self.assertNotIn("composeError", att)


class CliTemplateTests(test_cli.CliBase):
    NAME = "example-world"

    def setUp(self):
        super().setUp()
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        cfg["profiles"]["og"] = dict(cfg["profiles"]["banner"], width=1280, height=640, targetWidth=1200, targetHeight=630,
                                     compose={"template": "t.svg", "fields": ["title"],
                                              "templates": {"alt": {"template": "alt.svg", "fields": ["subtitle"]}}})
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        for name in ("t.svg", "alt.svg"):
            (self.root / name).write_text("<svg/>", encoding="utf-8")
        self.ok("project", "add", str(self.root))

    def test_templates_json_is_the_list_of_the_api(self):
        got = self.js("templates", self.NAME, "og")
        self.assertEqual(got, compose.templates_of(json.loads((self.root / "galivelop-images.json").read_text())
                                                   ["profiles"]["og"]))
        self.assertEqual([(i["id"], i["default"]) for i in got], [("default", True), ("alt", False)])

    def test_templates_text_marks_the_default(self):
        text = self.ok("templates", self.NAME, "og")
        self.assertEqual(len(text.splitlines()), 2)
        self.assertIn("default [default]: t.svg", text)
        self.assertIn("alt: alt.svg (logo: none; fields: subtitle)", text)

    def test_a_profile_without_compose_has_none_and_an_unknown_one_fails(self):
        self.assertEqual(self.js("templates", self.NAME, "banner"), [])
        code, _, err = self.run_cli("templates", self.NAME, "banner")
        self.assertEqual((code, err), (0, ""))
        code, _, err = self.run_cli("templates", self.NAME, "nope")
        self.assertNotEqual(code, 0)
        self.assertIn("nope", err)

    def test_attempt_new_takes_the_template_and_refuses_an_unknown_one(self):
        self.ok("order", "submit", self.NAME, str(self.order_file))
        self.order_file.write_text(json.dumps(dict(test_cli.ORDER, profile="og")))
        self.ok("order", "submit", self.NAME, str(self.order_file))
        before = len(self.js("queue", "list"))
        code, _, err = self.run_cli("attempt", "new", self.NAME, test_cli.ORDER["key"], "og",
                                    "--template", "nope")
        self.assertNotEqual(code, 0)
        self.assertIn("nope", err)
        self.assertEqual(len(self.js("queue", "list")), before)
        out = self.js("attempt", "new", self.NAME, test_cli.ORDER["key"], "og", "--template", "alt")
        entries = out["entries"] if isinstance(out, dict) else out
        self.assertEqual([e["template"] for e in entries], ["alt"])


class DoctorTemplateTests(test_doctor.DoctorBase):
    def project(self, files):
        root = self.tmp / "p"
        root.mkdir()
        for name in files:
            (root / name).write_text("<svg/>", encoding="utf-8")
        (root / "galivelop-images.json").write_text(json.dumps({
            "minVersion": "0.1.0", "name": "p", "delivery": {"dir": "out", "template": "{key}-{profile}.png"},
            "profiles": {"og": {"width": 1280, "height": 640, "steps": 6, "cfg": 1.0, "sampler": "euler",
                                "model": "m-default", "compose": {
                                    "template": "t.svg", "logo": "l.svg",
                                    "templates": {"alt": {"template": "alt.svg"}}}}}}), encoding="utf-8")
        projects.add(root)

    def checks(self):
        return [c for c in doctor.run() if c.id.startswith("template")]

    def test_everything_in_place_is_one_ok_line(self):
        self.project(["t.svg", "l.svg", "alt.svg"])
        self.assertEqual([(c.id, c.status, c.params["count"]) for c in self.checks()],
                         [("templates:p", doctor.OK, 2)])

    def test_a_missing_file_of_a_template_entry_is_a_warning_that_names_it(self):
        self.project(["t.svg", "l.svg"])
        got = self.checks()
        self.assertEqual([(c.id, c.status, c.key) for c in got],
                         [("template:p:og:alt", doctor.WARN, "doctor.templates.bad")])
        self.assertEqual(got[0].params["path"], "alt.svg")
        self.assertIn("alt.svg", got[0].message("en"))

    def test_the_logo_of_default_is_checked_too(self):
        self.project(["t.svg", "alt.svg"])
        self.assertEqual([c.params["path"] for c in self.checks()], ["l.svg"])


if __name__ == "__main__":
    unittest.main()
