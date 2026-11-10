import copy
import json
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import unittest
from pathlib import Path
from unittest import mock

from gimg import compose, png, schema as S

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    with open(ROOT / rel, encoding="utf-8") as fh:
        return json.load(fh)


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_schema = S.load_schema("project-config")
        cls.order_schema = S.load_schema("order")
        cls.machine_schema = S.load_schema("machine-profile")
        cls.project = read("examples/galivelop-images.json")
        cls.order = read("examples/order.json")

    def errs(self, instance, sch):
        return sorted((e.path, e.code) for e in S.validate(instance, sch))

    def order_with(self, **changes):
        order = copy.deepcopy(self.order)
        order.update(changes)
        return order

    def test_examples_valid(self):
        self.assertEqual(S.validate(self.project, self.project_schema), [])
        self.assertEqual(S.validate(self.order, self.order_schema), [])
        steam = read("gimg/machine_profiles/steam-deck.json")
        self.assertEqual(S.validate(steam, self.machine_schema), [])

    def test_order_bad_keys(self):
        for key in ("a/../b", "../x", "/abs", "A", "a//b", "a/"):
            self.assertEqual(self.errs(self.order_with(key=key), self.order_schema),
                             [("/key", "pattern")], key)

    def test_order_key_rejects_trailing_newline(self):
        self.assertEqual(self.errs(self.order_with(key="fauna/x\n"), self.order_schema),
                         [("/key", "pattern")])

    def test_order_profile_rejects_hyphen_and_newline(self):
        for name in ("banner-thumb", "banner\n", "1x", "Banner"):
            self.assertEqual(self.errs(self.order_with(profile=name), self.order_schema),
                             [("/profile", "pattern")], name)

    def test_order_bad_references(self):
        for ref in ("/etc/passwd", "../x.png", "a/../../x.png", "~/x", "a\\b.png",
                    "a\n/../../etc/passwd", "a\x00b", "a\x7f"):
            self.assertEqual(self.errs(self.order_with(references=[ref]), self.order_schema),
                             [("/references/0", "pattern")], repr(ref))
        self.assertEqual(self.errs(self.order_with(references=[""]), self.order_schema),
                         [("/references/0", "minLength"), ("/references/0", "pattern")])

    def test_order_good_reference_with_dots_in_name(self):
        order = self.order_with(references=["refs/a..b.png"])
        self.assertEqual(S.validate(order, self.order_schema), [])

    def test_order_count_zero(self):
        self.assertEqual(self.errs(self.order_with(count=0), self.order_schema),
                         [("/count", "minimum")])

    def test_order_unknown_property(self):
        self.assertEqual(self.errs(self.order_with(extra=1), self.order_schema),
                         [("/extra", "additionalProperties")])

    def test_project_profile_without_width(self):
        proj = copy.deepcopy(self.project)
        del proj["profiles"]["banner"]["width"]
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/banner", "required")])

    def test_project_unknown_property(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["banner"]["colour"] = "red"
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/banner/colour", "additionalProperties")])

    def test_project_template_without_png(self):
        proj = copy.deepcopy(self.project)
        proj["delivery"]["template"] = "{key}-{profile}.jpg"
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/delivery/template", "pattern")])

    def test_project_template_rules(self):
        bad = ("/etc/x.png", "../{key}-{profile}.png", "fixed.png", "{key}.png",
               "{foo}-{key}-{profile}.png", "~/{key}-{profile}.png", "a/../{key}-{profile}.png",
               "{key}-{profile}.png\n", "{key} {profile}.png", "{key}-{profile}.png/")
        for tpl in bad:
            proj = copy.deepcopy(self.project)
            proj["delivery"]["template"] = tpl
            self.assertEqual(self.errs(proj, self.project_schema),
                             [("/delivery/template", "pattern")], repr(tpl))
        for tpl in ("{key}-{profile}.png", "img/{profile}/{key}.png", "a..b/{key}_{profile}.png"):
            proj = copy.deepcopy(self.project)
            proj["delivery"]["template"] = tpl
            self.assertEqual(S.validate(proj, self.project_schema), [], tpl)

    def test_project_delivery_dir_newline(self):
        proj = copy.deepcopy(self.project)
        proj["delivery"]["dir"] = "a\n/../../etc"
        self.assertEqual(self.errs(proj, self.project_schema), [("/delivery/dir", "pattern")])

    def test_project_hyphenated_profile_name(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["banner-thumb"] = proj["profiles"]["banner"]
        proj["profiles"]["banner\n"] = proj["profiles"]["banner"]
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/banner\n", "propertyNames"),
                          ("/profiles/banner-thumb", "propertyNames")])

    def test_project_min_version_non_ascii_digits(self):
        proj = copy.deepcopy(self.project)
        proj["minVersion"] = "\u0661.\u0660.\u0660"
        self.assertEqual(self.errs(proj, self.project_schema), [("/minVersion", "pattern")])
        proj["minVersion"] = "1.0.0\n"
        self.assertEqual(self.errs(proj, self.project_schema), [("/minVersion", "pattern")])

    def test_order_params_non_finite(self):
        for value in (float("nan"), float("inf")):
            order = self.order_with(params={"cfg": value})
            self.assertEqual(self.errs(order, self.order_schema), [("/params/cfg", "type")])

    def test_whole_float_size_is_valid(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["banner"]["width"] = 1280.0
        self.assertEqual(S.validate(proj, self.project_schema), [])
        proj["profiles"]["banner"]["width"] = 1280.5
        self.assertEqual(self.errs(proj, self.project_schema), [("/profiles/banner/width", "type")])

    def test_shared_defs_are_identical_across_schemas(self):
        seen = {}
        for name in ("project-config", "order", "machine-profile", "models"):
            for key, definition in S.load_schema(name).get("$defs", {}).items():
                seen.setdefault(key, []).append((name, definition))
        for key in ("name", "profileName", "relativePath", "steps", "cfg", "sampler"):
            self.assertTrue(seen.get(key), key)
        for key, copies in seen.items():
            for name, definition in copies[1:]:
                self.assertEqual(definition, copies[0][1], "%s: %s vs %s" % (key, name, copies[0][0]))

    def test_readme_examples_validate(self):
        for readme in ("README.md", "README.en.md"):
            with open(ROOT / readme, encoding="utf-8") as fh:
                blocks = re.findall(r"```json\n(.*?)```", fh.read(), re.S)
            projects = orders = 0
            for block in blocks:
                data = json.loads(block)
                if "profiles" in data:
                    projects += 1
                    self.assertEqual(S.validate(data, self.project_schema), [], readme)
                if "key" in data:
                    orders += 1
                    self.assertEqual(S.validate(data, self.order_schema), [], readme)
            self.assertGreaterEqual(projects, 1, readme)
            self.assertGreaterEqual(orders, 1, readme)

    def test_project_unsafe_delivery_dir_and_manifest(self):
        proj = copy.deepcopy(self.project)
        proj["delivery"]["dir"] = "../out"
        proj["manifest"] = "/tmp/m.json"
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/delivery/dir", "pattern"), ("/manifest", "pattern")])

    def test_project_bad_profile_name_and_empty_profiles(self):
        proj = copy.deepcopy(self.project)
        proj["profiles"]["Bad_Name"] = proj["profiles"]["banner"]
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles/Bad_Name", "propertyNames")])
        proj["profiles"] = {}
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/profiles", "minProperties")])

    def test_project_bad_min_version_and_size(self):
        proj = copy.deepcopy(self.project)
        proj["minVersion"] = "1.0"
        proj["profiles"]["banner"]["width"] = 63
        proj["profiles"]["banner"]["height"] = 5000
        self.assertEqual(self.errs(proj, self.project_schema),
                         [("/minVersion", "pattern"),
                          ("/profiles/banner/height", "maximum"),
                          ("/profiles/banner/width", "minimum")])

    def test_machine_profile_errors(self):
        steam = read("gimg/machine_profiles/steam-deck.json")
        steam["engine"]["paramsBackend"] = "ram"
        steam["engine"]["maxVram"] = "bad"
        del steam["timeoutS"]
        self.assertEqual(self.errs(steam, self.machine_schema),
                         [("", "required"), ("/engine/maxVram", "pattern"),
                          ("/engine/paramsBackend", "enum")])


PILOT_PROJECTS = ("galivelop-developer", "galivelop-image-generator", "galivelop-voice-generator",
                  "galivelop-workflow", "portal", "tarkor", "toveriai")
R1_SEEDS = (3, 4)
# `portal` se rehízo con la hoja de estilo de marca (examples/portal/README.md): sin perfil `og`, sin r1/r2 ni compose.
OG_PROJECTS = tuple(n for n in PILOT_PROJECTS if n != "portal")


class PilotExampleTests(unittest.TestCase):
    """F2.6: `examples/<proyecto>/` of the seven pilot projects, with the r1 orders that must reproduce
    `ronda.sh r1` (same prompt as `prompts/og.txt`, seeds 3 and 4, 1280x640, 6 steps, the fast model)."""

    @classmethod
    def setUpClass(cls):
        cls.order_schema = S.load_schema("order")

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        env = mock.patch.dict(os.environ, {"GIMG_CONFIG_HOME": tmp.name + "/cfg",
                                           "GIMG_DATA_HOME": tmp.name + "/data"})
        env.start()
        self.addCleanup(env.stop)

    def test_the_seven_pilot_projects_have_a_config(self):
        found = sorted(p.parent.name for p in (ROOT / "examples").glob("*/galivelop-images.json"))
        self.assertEqual(found, sorted(PILOT_PROJECTS))

    def test_pilot_configs_load_and_fit_the_deck(self):
        from gimg import limits, projects
        deck = limits.load_machine("steam-deck")
        for name in PILOT_PROJECTS:
            root = ROOT / "examples" / name
            config = projects.load_config(root)
            self.assertEqual(config["name"], name)
            self.assertEqual(config["delivery"]["dir"], "entrega", name)
            if name in OG_PROJECTS:
                self.assertIn("og", config["profiles"], name)
            for profile, cfg in config["profiles"].items():
                self.assertEqual((cfg["width"] % 64, cfg["height"] % 64), (0, 0), (name, profile))
                try:
                    limits.check({"params": cfg, "references": []}, deck)
                except limits.LimitError as exc:
                    self.fail("%s/%s: %s" % (name, profile, exc))
                self.assertEqual(cfg["model"], "flux2-klein-4b-q8", (name, profile))

    def test_r1_orders_reproduce_ronda_r1(self):
        from gimg import orders, projects
        for name in OG_PROJECTS:
            root = ROOT / "examples" / name
            order = read("examples/%s/orders/r1-og.json" % name)
            self.assertEqual(S.validate(order, self.order_schema), [], name)
            prompt = (root / "prompts" / "og.txt").read_text(encoding="utf-8").strip()
            self.assertEqual(order["prompt"], prompt, name)
            projects.add(root)
            orders.submit(name, order)
            specs = orders.attempt_specs(name, order["key"], order["profile"], order["count"])
            self.assertEqual([s["seed"] for s in specs], list(R1_SEEDS), name)
            self.assertEqual({s["prompt"] for s in specs}, {prompt}, name)
            self.assertEqual(specs[0]["params"],
                             {"width": 1280, "height": 640, "steps": 6, "cfg": 1.0, "sampler": "euler",
                              "model": "flux2-klein-4b-q8"}, name)
            self.assertEqual(specs[0]["references"], [], name)

    def test_r2_orders_use_their_prompt_files_and_seeds(self):
        from gimg import orders, projects
        cases = [(name, "r2-luz", "r2-luz.txt", 3) for name in OG_PROJECTS]
        cases += [(name, "r2-control", "estilo.txt", 7) for name in OG_PROJECTS]
        cases.append(("tarkor", "r2-luz-r1", "r2-luz-r1.txt", 3))
        added = set()
        for name, stem, prompt_file, seed in cases:
            root = ROOT / "examples" / name
            order = read("examples/%s/orders/%s.json" % (name, stem))
            self.assertEqual(S.validate(order, self.order_schema), [], (name, stem))
            self.assertEqual((order["key"], order["profile"], order["count"]),
                             ("estilo/" + stem, "og", 1), (name, stem))
            prompt = (root / "prompts" / prompt_file).read_text(encoding="utf-8").strip()
            self.assertEqual(order["prompt"], prompt, (name, stem))
            if name not in added:
                projects.add(root)
                added.add(name)
            orders.submit(name, order)
            specs = orders.attempt_specs(name, order["key"], order["profile"], order["count"])
            self.assertEqual([s["seed"] for s in specs], [seed], (name, stem))
            self.assertEqual(specs[0]["params"],
                             {"width": 1280, "height": 640, "steps": 6, "cfg": 1.0, "sampler": "euler",
                              "model": "flux2-klein-4b-q8"}, (name, stem))
            # The second seed of R1 comes from `gimg attempt new --seed 7`, not from count.
            extra = orders.attempt_specs(name, order["key"], order["profile"], 1, seed=7)
            self.assertEqual([s["seed"] for s in extra], [7], (name, stem))

    def test_gitignore_keeps_pilot_deliveries_out_of_git(self):
        lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("/examples/*/entrega/", lines)
        self.assertIn("/examples/*/galivelop-images.manifest.json", lines)


COMPOSE_PROJECTS = {  # proyecto -> lockup elegido (docs/marcas/README.md)
    "tarkor": "tarkor-b-lockup.svg",
    "toveriai": "toveriai-a-lockup.svg",
    "galivelop-image-generator": "galivelop-image-generator-b-lockup.svg",
    "galivelop-workflow": "galivelop-workflow-b-lockup.svg",
}
FACTOR_TITULO, FACTOR_SUB = 0.56, 0.5  # los de examples/pilot/componer.py (`ajustar`)


class ComposeExampleTests(unittest.TestCase):
    """F2.10 E4: `compose` del perfil `og` de cinco ejemplos (plantilla, logo y texto dentro de cada uno)."""

    def each(self):
        for name, logo in COMPOSE_PROJECTS.items():
            root = ROOT / "examples" / name
            cfg = read("examples/%s/galivelop-images.json" % name)["profiles"]["og"]
            yield name, logo, root, cfg

    def test_configs_validate_and_declare_compose(self):
        sch = S.load_schema("project-config")
        for name, logo, root, cfg in self.each():
            self.assertEqual(S.validate(read("examples/%s/galivelop-images.json" % name), sch), [], name)
            self.assertEqual((cfg["targetWidth"], cfg["targetHeight"]), (1200, 630), name)
            self.assertEqual(cfg["draft"], {"scale": 0.5, "steps": 4}, name)
            self.assertEqual(cfg["compose"]["template"], "plantillas/og.svg", name)
            self.assertEqual(cfg["compose"]["logo"], "logos/" + logo, name)
            self.assertEqual(cfg["compose"]["fit"], "cover", name)
            # El titular va en title1, title2 (y title3 si hace falta una tercera línea, r6: Tarkor); luego el subtítulo.
            self.assertEqual(cfg["compose"]["fields"][:2], ["title1", "title2"], name)
            self.assertIn("subtitle", cfg["compose"]["fields"], name)

    def test_logo_copies_are_identical_to_their_originals(self):
        for name, logo, root, cfg in self.each():
            copy_ = (root / "logos" / logo).read_bytes()
            original = (ROOT / "docs" / "marcas" / name / "logos" / logo).read_bytes()
            self.assertEqual(copy_, original, name)

    def test_resolve_assets_finds_template_and_logo(self):
        for name, logo, root, cfg in self.each():
            template, found = compose.resolve_assets(root, cfg["compose"])
            self.assertEqual(template, (root / "plantillas" / "og.svg").resolve(), name)
            self.assertEqual(found, (root / "logos" / logo).resolve(), name)

    def test_template_holes_are_the_declared_fields(self):
        for name, logo, root, cfg in self.each():
            source = (root / "plantillas" / "og.svg").read_text(encoding="utf-8")
            holes = set(re.findall(r"\{\{([A-Za-z0-9]+)\}\}", source))
            self.assertEqual(holes, set(cfg["compose"]["fields"]) | {"logo"}, name)

    def test_text_lines_fit_their_column(self):
        for name, logo, root, cfg in self.each():
            svg = ET.parse(root / "plantillas" / "og.svg").getroot()
            _x, _y, col, _h = (int(v) for v in svg.get("data-caja").split(","))
            text = read("examples/%s/textos/og.json" % name)
            self.assertEqual(set(text), set(cfg["compose"]["fields"]), name)
            for el in svg.iter("{http://www.w3.org/2000/svg}text"):
                field = el.get("id")
                factor = FACTOR_TITULO if field.startswith("title") else FACTOR_SUB
                size = float(el.get("font-size"))
                self.assertLessEqual(len(text[field]) * size * factor, col, (name, field, text[field]))

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("rsvg-convert"), "hacen falta ffmpeg y rsvg-convert")
    def test_each_template_composes_a_synthetic_raw_at_1200x630(self):
        from tests.test_compose import striped_png
        for name, logo, root, cfg in self.each():
            with tempfile.TemporaryDirectory() as tmp:
                raw, out = Path(tmp) / "raw.png", Path(tmp) / "out.png"
                striped_png(raw, 1280, 640)
                compose.render(root, cfg, raw, out, read("examples/%s/textos/og.json" % name), profile="og")
                self.assertEqual(png.size(out), (1200, 630), name)


if __name__ == "__main__":
    unittest.main()
