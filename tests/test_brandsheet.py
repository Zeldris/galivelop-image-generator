"""Brand sheet as data (0.7.0 step 1): schema, inheritance, tones, assembly and lint."""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import brandsheet as B, projects, schema as S
from gimg.errors import GimgError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())

ENGRAVED = ("Richly detailed engraved antique nautical chart style, like a fine sea chart printed in two inks: many "
            "layers of fine lines and hatching, line density increasing in the darker areas to give depth and tone, "
            "lines of several weights, crisp and sharp, intricate but calm, premium print quality, high detail, "
            "elegant.")
LINE = ("Simple line icon style: one uniform stroke width, rounded caps and joins, no shading, no hatching, no fill, "
        "no texture, bold and clear enough to read at 24 pixels, generous empty margin around each icon, a single "
        "ink colour.")
CLOSING = ("No photographic rendering, no glow, no text, no letters, no numbers, no watermark, full-bleed edge to "
           "edge, no border, no frame, no white margin, no blank band.")


def label(es, en=None):
    return {"es": es, "en": en or es}


def color(value, name):
    return {"$value": value, "$type": "color", "promptName": name}


PORTAL = {
    "schemaVersion": 1,
    "name": "portal",
    "palette": {
        "paper": color("#fbfcfd", "plain flat off-white"),
        "ink": color("#13212b", "ink grey"),
        "accent": color("#5d7a6a", "a touch of seaweed green"),
        "halo": color("#0072a8", "medium cerulean ocean blue"),
        "dark": {"paper": color("#0d171e", "dark slate"), "ink": color("#e6eef3", "pale off-white")},
        "measureOnly": ["#1aa6df"],
    },
    "registers": {
        "engraved": {"label": label("Grabado", "Engraved"), "block": ENGRAVED},
        "line": {"label": label("Línea simple", "Simple line"), "block": LINE},
    },
    "closing": CLOSING,
    "paletteSentence": "Palette strictly limited to {halo} and its tints and shades, {paper}, {ink} and {accent}",
    "vetoes": {
        "groups": [
            {"id": "ethics", "label": label("Ética", "Ethics"), "reason": label("biblia", "bible"),
             "terms": ["robot", "hands"]},
            {"id": "nautical", "label": label("Náutico"), "reason": label("el mar pone el dónde", "the sea is the where"),
             "terms": ["lighthouse", "boat", "anchor"]},
        ],
        "exceptions": [{"term": "lighthouse", "pieces": ["cover"]}],
        "neverWrite": ["transparent", "exactly", "sky blue"],
        "colorWords": ["white", "golden", "red"],
        "fillPhrase": "filling the whole sheet",
    },
    "pieceTypes": {
        "cover": {"label": label("Portada", "Cover"), "profile": "portada", "register": "engraved",
                  "chroma": None, "seed": 42, "count": 2, "workshop": ["crop"]},
        "icon": {"label": label("Icono", "Icon"), "profile": "icono", "register": "line",
                 "chroma": "#00ff00", "seed": 7, "count": 4, "workshop": ["matte", "trace"], "delivery": "public/icons"},
    },
    "acceptance": {"traits": {"palette": 3, "frame": 1}, "references": ["refs/q311.png"], "autoDiscard": False,
                   "unmeasured": [{"id": "horizon", "label": label("Horizonte", "Horizon")}]},
    "promptWords": {"min": 120, "max": 200},
}

SUBJECT = ("A wide sea chart of the Galician coast seen from above, with a terminal window resting on calm charted "
           "water on the left third, a short commit history drawn as a vertical line with a few round nodes beside "
           "it, isobaths and contour lines curving around small islands, and a compass rose in one corner")
ZONE = "The lower third of the sheet is plain flat off-white paper, open and unmarked"


class Env(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data")})
        env.start()
        self.addCleanup(env.stop)

    def project(self, name, sheet=None, rel="marca.json"):
        root = self.tmp / name
        root.mkdir(exist_ok=True)
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        cfg["name"] = name
        if rel is not None:
            cfg.setdefault("brand", {})["sheet"] = rel
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        if sheet is not None:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(json.dumps(sheet))
        projects.add(root)
        return root

    def code(self, fn, *args, **kwargs):
        with self.assertRaises(GimgError) as cm:
            fn(*args, **kwargs)
        return cm.exception


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.sch = S.load_schema("brand-sheet")

    def errs(self, data):
        return sorted((e.path, e.code) for e in S.validate(data, self.sch))

    def test_fixture_valid_and_child_can_be_partial(self):
        self.assertEqual(self.errs(PORTAL), [])
        self.assertEqual(self.errs({"schemaVersion": 1, "name": "dev", "extends": "portal"}), [])

    def test_invalid(self):
        bad = copy.deepcopy(PORTAL)
        bad["palette"]["accent"]["$value"] = "#12345"
        bad["pieceTypes"]["icon"]["workshop"] = ["paint"]
        bad["schemaVersion"] = 2
        bad["extra"] = 1
        self.assertEqual(self.errs(bad), [
            ("/extra", "additionalProperties"), ("/palette/accent/$value", "pattern"),
            ("/pieceTypes/icon/workshop/0", "enum"), ("/schemaVersion", "const")])

    def test_project_config_takes_sheet_path(self):
        sch = S.load_schema("project-config")
        cfg = dict(EXAMPLE, brand={"sheet": "../marca.json"})
        self.assertEqual([(e.path, e.code) for e in S.validate(cfg, sch)], [("/brand/sheet", "pattern")])
        self.assertEqual(S.validate(dict(EXAMPLE, brand={"sheet": "docs/marca.json"}), sch), [])


class LoadResolveTests(Env):
    def test_load_errors(self):
        self.assertEqual(self.code(B.load, self.tmp / "nope.json").code, "brandsheet.missing")
        (self.tmp / "bad.json").write_text("{")
        self.assertEqual(self.code(B.load, self.tmp / "bad.json").code, "brandsheet.unreadable")
        (self.tmp / "inv.json").write_text(json.dumps({"name": "x"}))
        err = self.code(B.load, self.tmp / "inv.json")
        self.assertEqual((err.code, [e.code for e in err.errors]), ("brandsheet.invalid", ["required"]))

    def test_two_level_inheritance_and_origin(self):
        self.project("portal", PORTAL)
        self.project("family", {"schemaVersion": 1, "name": "family", "extends": "portal",
                                "vetoes": {"groups": [{"id": "ethics", "terms": ["robot", "hands", "brain"]}],
                                           "exceptions": [{"term": "boat", "pieces": ["cover"]}]}})
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "family",
                             "palette": {"accent": color("#0e9a93", "a touch of teal")},
                             "vetoes": {"groups": [{"id": "gears", "label": label("Engranajes"), "terms": ["gear"]}]}})
        sheet = B.resolve("dev")
        self.assertEqual(sheet["chain"], ["dev", "family", "portal"])
        self.assertEqual(sheet["palette"]["accent"]["$value"], "#0e9a93")
        self.assertEqual(sheet["palette"]["paper"]["$value"], "#fbfcfd")
        groups = {g["id"]: g for g in sheet["vetoes"]["groups"]}
        self.assertEqual(list(groups), ["ethics", "nautical", "gears"])
        self.assertEqual(groups["ethics"]["terms"], ["robot", "hands", "brain"])
        self.assertEqual(groups["ethics"]["reason"], label("biblia", "bible"))  # merged by id, not replaced
        self.assertEqual([e["term"] for e in sheet["vetoes"]["exceptions"]], ["lighthouse", "boat"])
        self.assertNotIn("extends", sheet)
        origin = sheet["origin"]
        self.assertEqual(origin["palette.accent.$value"], {"origin": "own", "project": "dev"})
        self.assertEqual(origin["palette.paper.$value"], {"origin": "inherited", "project": "portal"})
        self.assertEqual(origin["vetoes.groups.ethics.terms"], {"origin": "inherited", "project": "family"})
        self.assertEqual(origin["vetoes.groups.gears.terms"], {"origin": "own", "project": "dev"})
        self.assertEqual(origin["vetoes.exceptions.0.term"], {"origin": "inherited", "project": "portal"})
        self.assertEqual(origin["vetoes.exceptions.1.term"], {"origin": "inherited", "project": "family"})
        self.assertRegex(sheet["version"], r"^[0-9a-f]{12}$")
        self.assertNotEqual(sheet["version"], B.resolve("portal")["version"])
        self.assertEqual(sheet["version"], B.resolve("dev")["version"])

    def test_cycle(self):
        self.project("a", dict(PORTAL, name="a", extends="b"))
        self.project("b", {"schemaVersion": 1, "name": "b", "extends": "a"})
        err = self.code(B.resolve, "a")
        self.assertEqual((err.code, err.params["chain"]), ("brandsheet.extends_cycle", "a -> b -> a"))

    def test_missing_parent(self):
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "ghost"})
        err = self.code(B.resolve, "dev")
        self.assertEqual((err.code, err.params["parent"]), ("brandsheet.extends_missing", "ghost"))

    def test_parent_without_sheet(self):
        self.project("portal", rel=None)
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "portal"})
        self.assertEqual(self.code(B.resolve, "dev").code, "brandsheet.extends_missing")

    def test_no_sheet(self):
        self.project("plain", rel=None)
        self.assertEqual(self.code(B.resolve, "plain").code, "brandsheet.none")

    def test_parent_sheet_outside_root_by_symlink(self):
        outside = self.tmp / "elsewhere.json"
        outside.write_text(json.dumps(PORTAL))
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "portal"})
        root = self.tmp / "portal"
        root.mkdir()
        (root / "marca.json").symlink_to(outside)
        cfg = dict(copy.deepcopy(EXAMPLE), name="portal", brand={"sheet": "marca.json"})
        cfg.pop("$schema", None)
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        with self.assertRaises(GimgError) as cm:
            projects.load_config(root)
        self.assertEqual(cm.exception.code, "path.outside")
        # registered before the link appeared: resolving the child still refuses it
        (root / "marca.json").unlink()
        (root / "marca.json").write_text(json.dumps(PORTAL))
        projects.add(root)
        (root / "marca.json").unlink()
        (root / "marca.json").symlink_to(outside)
        err = self.code(B.resolve, "dev")
        self.assertEqual((err.code, err.params["path"]), ("path.outside", "marca.json"))

    def test_parent_sheet_symlink_caught_by_project_sheet_guard(self):
        # load_config is bypassed (mocked), so only _project_sheet's paths.inside can refuse the link
        outside = self.tmp / "elsewhere.json"
        outside.write_text(json.dumps(PORTAL))
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "portal"})
        root = self.tmp / "portal"
        root.mkdir()
        (root / "marca.json").symlink_to(outside)
        real_get = projects.get
        portal = {"name": "portal", "root": str(root), "config": {"brand": {"sheet": "marca.json"}}}
        with mock.patch.object(B.projects, "get", side_effect=lambda n: portal if n == "portal" else real_get(n)):
            err = self.code(B.resolve, "dev")
        self.assertEqual((err.code, err.params["path"]), ("path.outside", "marca.json"))

    def test_parent_sheet_dotdot_in_config_rejected_by_the_schema(self):
        # the schema alone: `load_config` refuses `..` in `brand.sheet` (the `extends` path is the next test)
        root = self.tmp / "portal"
        root.mkdir()
        cfg = dict(copy.deepcopy(EXAMPLE), name="portal", brand={"sheet": "../marca.json"})
        cfg.pop("$schema", None)
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        err = self.code(projects.load_config, root)
        self.assertEqual((err.code, [(e.path, e.code) for e in err.errors]),
                         ("project.config_invalid", [("/brand/sheet", "pattern")]))

    def test_extends_a_parent_whose_sheet_path_has_dotdot_is_refused(self):
        # registered with a good sheet path, then the parent's config is edited to `../marca.json`: resolving the child
        # (the `extends` route) must refuse it with the parent's name and the schema reason, not read outside the root
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "portal"})
        root = self.project("portal", PORTAL)
        (self.tmp / "marca.json").write_text(json.dumps(PORTAL))
        cfg = json.loads((root / "galivelop-images.json").read_text())
        cfg["brand"] = {"sheet": "../marca.json"}
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        err = self.code(B.resolve, "dev")
        self.assertEqual((err.code, err.params["parent"]), ("brandsheet.extends_broken", "portal"))
        self.assertIn("/brand/sheet", err.params["reason"])

    def test_incomplete_and_bad_references(self):
        self.project("half", {"schemaVersion": 1, "name": "half", "closing": "x"})
        err = self.code(B.resolve, "half")
        self.assertEqual((err.code, err.params["field"]), ("brandsheet.incomplete", "palette.paper"))
        bad = copy.deepcopy(PORTAL)
        bad["name"] = "bad"
        bad["pieceTypes"]["icon"]["register"] = "watercolour"
        self.project("bad", bad)
        err = self.code(B.resolve, "bad")
        self.assertEqual((err.code, err.params["register"]), ("brandsheet.unknown_register", "watercolour"))
        wide = copy.deepcopy(PORTAL)
        wide["name"] = "wide"
        wide["pieceTypes"]["icon"]["promptWords"] = {"min": 300, "max": 100}
        self.project("wide", wide)
        err = self.code(B.resolve, "wide")
        self.assertEqual((err.code, err.params["piece"], err.params["field"]),
                         ("brandsheet.incomplete", "icon", "pieceTypes.icon.promptWords"))
        worse = dict(copy.deepcopy(PORTAL), name="worse", paletteSentence="Only {grid}")
        self.project("worse", worse)
        err = self.code(B.resolve, "worse")
        self.assertEqual((err.code, err.params["placeholder"]), ("brandsheet.bad_placeholder", "grid"))
        self.assertEqual(err.params["where"], "paletteSentence")


TONOS = {
    "galivelop-developer": "#0E9A93",
    "galivelop-voice-generator": "#D9467A",
}


class ToneTests(unittest.TestCase):
    def script_tones(self, product, accent):
        out = subprocess.run([sys.executable, str(ROOT / "docs" / "marcas" / product / "tonos.py"), accent],
                             capture_output=True, text=True, check=True).stdout
        deep = re.search(r"^hondo\s+(#[0-9a-f]{6})", out, re.M).group(1)
        dark = re.search(r"^oscuro\s+(#[0-9a-f]{6})", out, re.M).group(1)
        return {"deep": deep, "dark": dark}

    def test_same_as_product_scripts(self):
        for product, accent in TONOS.items():
            self.assertEqual(B.accent_tones(accent), self.script_tones(product, accent), product)
        # extra accents through one script: the methods agree beyond the two shipped values
        for accent in ("#0072a8", "#5d7a6a", "#7c4dff", "#ffcc00"):
            self.assertEqual(B.accent_tones(accent), self.script_tones("galivelop-developer", accent), accent)

    def test_known_values(self):
        self.assertEqual(B.accent_tones("#D9467A"), {"deep": "#ce3c71", "dark": "#db487b"})

    def test_bad_hex(self):
        with self.assertRaises(GimgError) as cm:
            B.accent_tones("#12345g")
        self.assertEqual(cm.exception.code, "brandsheet.bad_hex")

    def test_dark_paper_sheet_does_not_raise(self):
        sheet = copy.deepcopy(PORTAL)
        sheet["palette"]["paper"] = color("#101820", "deep slate")
        pal = B.palette(sheet)
        self.assertIn("#101820", pal)
        tones = B.accent_tones("#5d7a6a", "#101820")
        self.assertGreaterEqual(B.contrast(tones["deep"], "#101820"), 4.5)
        zone = ZONE.replace("plain flat off-white", "deep slate")
        prompt = B.assemble(sheet, "cover", SUBJECT, zone)["prompt"]
        self.assertFalse(B.lint(sheet, prompt, piece="cover", clean_zone=zone)["blocked"])

    def test_palette(self):
        tones = B.accent_tones("#5d7a6a")
        pal = B.palette(PORTAL)
        self.assertEqual(pal[:4], ["#fbfcfd", "#13212b", "#5d7a6a", "#0072a8"])
        self.assertEqual(pal[-3:], ["#0d171e", "#e6eef3", "#1aa6df"])
        self.assertEqual(len(pal), len(set(pal)))
        self.assertTrue({tones["deep"], tones["dark"]} <= set(pal))


class AssembleTests(unittest.TestCase):
    def test_order_and_punctuation(self):
        out = B.assemble(PORTAL, "cover", SUBJECT, ZONE)
        self.assertEqual([s["role"] for s in out["segments"]],
                         ["subject", "cleanZone", "register", "closing", "palette"])
        self.assertEqual(out["segments"][2]["source"], "registers.engraved")
        self.assertTrue(all(s["text"].endswith(".") for s in out["segments"]))
        self.assertEqual(out["prompt"], " ".join(s["text"] for s in out["segments"]))
        self.assertEqual(out["segments"][-1]["text"],
                         "Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, "
                         "plain flat off-white #fbfcfd, ink grey #13212b and a touch of seaweed green #5d7a6a.")
        self.assertEqual(out["words"], len(out["prompt"].split()))

    def test_without_zone_and_unknown_piece(self):
        out = B.assemble(PORTAL, "icon", "A terminal window.")
        self.assertEqual([s["role"] for s in out["segments"]], ["subject", "register", "closing", "palette"])
        with self.assertRaises(GimgError) as cm:
            B.assemble(PORTAL, "poster", SUBJECT)
        self.assertEqual(cm.exception.code, "brandsheet.unknown_piece")


def with_piece(**spec):
    sheet = copy.deepcopy(PORTAL)
    sheet["pieceTypes"]["stage"] = {**sheet["pieceTypes"]["cover"], **spec}
    return sheet


PIECE_CLOSING = "No realistic objects, no glow, no text, no frame."
PIECE_PALETTE = "Palette limited to {halo} and {ink}"


class PieceTypeOverridesTests(Env):
    def test_closing_and_palette_sentence_of_the_piece_replace_the_sheets(self):
        sheet = with_piece(closing=PIECE_CLOSING, paletteSentence=PIECE_PALETTE)
        out = B.assemble(sheet, "stage", "A chart.")
        self.assertEqual([s["text"] for s in out["segments"]][2:],
                         [PIECE_CLOSING, "Palette limited to medium cerulean ocean blue #0072a8 and ink grey #13212b."])
        self.assertEqual([s["source"] for s in out["segments"]][2:],
                         ["pieceTypes.stage.closing", "pieceTypes.stage.paletteSentence"])
        other = B.assemble(sheet, "cover", "A chart.")  # a piece without them keeps the sheet's
        self.assertEqual(other["segments"][2]["text"], CLOSING)
        self.assertEqual(other["segments"][2]["source"], "closing")
        self.assertTrue(other["prompt"].endswith("a touch of seaweed green #5d7a6a."))

    def test_word_range_of_the_piece_beats_the_sheets(self):
        words = lambda sh: [c for c in B.lint(sh, B.assemble(sh, "stage", "A chart.")["prompt"], "stage")["checks"]
                            if c["id"] == "words"][0]
        base = with_piece()
        n = len(B.assemble(base, "stage", "A chart.")["prompt"].split())
        base["promptWords"] = {"min": n + 50, "max": n + 100}
        self.assertEqual(words(base)["status"], "error")  # the sheet's range applies without one of its own
        own = with_piece(promptWords={"min": n - 5, "max": n + 5})
        own["promptWords"] = {"min": n + 50, "max": n + 100}  # the sheet's range, out of reach of the prompt
        self.assertEqual(words(own)["status"], "ok")  # the piece's range wins

    def test_clean_zone_after_the_closing_continues_its_sentence(self):
        sheet = with_piece(closing=PIECE_CLOSING, cleanZone="afterClosing")
        out = B.assemble(sheet, "stage", "A chart.", "the islet small on the left")
        self.assertEqual([s["role"] for s in out["segments"]],
                         ["subject", "register", "closing", "cleanZone", "palette"])
        self.assertEqual(out["segments"][2]["text"], "No realistic objects, no glow, no text, no frame,")
        self.assertEqual(out["segments"][3]["text"], "the islet small on the left.")
        self.assertIn("No realistic objects, no glow, no text, no frame, the islet small on the left.", out["prompt"])
        self.assertEqual(out["prompt"].count("the islet small on the left"), 1)
        # no zone given: the closing is untouched
        self.assertEqual(B.assemble(sheet, "stage", "A chart.")["segments"][2]["text"], PIECE_CLOSING)
        # the default position is before the register
        before = B.assemble(with_piece(cleanZone="beforeRegister"), "stage", "A chart.", "The zone")
        self.assertEqual([s["role"] for s in before["segments"]][:3], ["subject", "cleanZone", "register"])

    def test_lint_looks_at_the_closing_and_palette_sentence_of_the_piece(self):
        zone = "the islet small on the left"
        sheet = with_piece(closing=PIECE_CLOSING, paletteSentence=PIECE_PALETTE, cleanZone="afterClosing")
        prompt = B.assemble(sheet, "stage", "A chart.", zone)["prompt"]
        res = B.lint(sheet, prompt, "stage", "brand", zone)
        self.assertEqual([c["id"] for c in res["checks"] if c["status"] != "ok" and c["id"] != "words"], [])
        # the sheet's closing is not the piece's: seen as a cover the same prompt lacks it and its palette
        bad = {(c["id"]) for c in B.lint(sheet, prompt, "cover")["checks"] if c["status"] != "ok"}
        self.assertLessEqual({"closing", "palette"}, bad)
        # the zone before the closing is out of place when the type puts it after
        swapped = "A chart. %s. %s %s %s" % (zone, sheet["registers"]["engraved"]["block"], PIECE_CLOSING,
                                              B.palette_sentence(sheet, sheet["pieceTypes"]["stage"]))
        found = [(c["id"], c["message"]["key"]) for c in B.lint(sheet, swapped, "stage", "brand", zone)["checks"]
                 if c["status"] != "ok" and c["id"] == "cleanZone"]
        self.assertEqual(found, [("cleanZone", "lint.clean_zone_order")])

    def test_negation_and_colour_words_follow_the_closing_of_the_piece(self):
        sheet = with_piece(closing="No yellow, no warm colors.")
        prompt = B.assemble(sheet, "stage", "A chart.")["prompt"]
        res = B.lint(sheet, prompt, "stage")
        self.assertEqual([c["id"] for c in res["checks"] if c["status"] != "ok" and c["id"] != "words"], [])
        # the same text as a cover's closing is not the sheet's: «no», «yellow» are out of place there
        loose = [c["id"] for c in B.lint(sheet, prompt, "cover")["checks"] if c["status"] != "ok"]
        self.assertIn("closing", loose)
        self.assertIn("negation", loose)

    def test_vetoed_term_inside_the_closing_is_not_a_veto(self):
        sheet = with_piece(closing="No boat, no frame.")
        prompt = B.assemble(sheet, "stage", "A chart.")["prompt"]
        self.assertFalse([c for c in B.lint(sheet, prompt, "stage")["checks"] if c["id"] == "veto" and c["status"] != "ok"])
        again = B.assemble(sheet, "stage", "A boat on a chart.")["prompt"]
        self.assertTrue([c for c in B.lint(sheet, again, "stage")["checks"] if c["id"] == "veto" and c["status"] != "ok"])

    def test_schema_and_resolution_check_the_new_fields(self):
        sheet = with_piece(closing=PIECE_CLOSING, paletteSentence=PIECE_PALETTE, cleanZone="afterClosing")
        schema = S.load_schema("brand-sheet")
        self.assertEqual(S.validate(sheet, schema), [])
        self.assertTrue(S.validate(with_piece(cleanZone="middle"), schema))
        self.assertTrue(S.validate(with_piece(closing=""), schema))
        self.project("portal", with_piece(paletteSentence="Palette {nope}"))
        err = self.code(B.resolve, "portal")
        self.assertEqual((err.code, err.params["placeholder"], err.params["where"]),
                         ("brandsheet.bad_placeholder", "nope", "pieceTypes.stage.paletteSentence"))
        self.assertIn("pieceTypes.stage.paletteSentence", err.message())

    def test_a_product_overrides_the_closing_of_an_inherited_type_by_key(self):
        self.project("portal", with_piece(closing=PIECE_CLOSING, paletteSentence=PIECE_PALETTE, cleanZone="afterClosing"))
        self.project("dev", {"schemaVersion": 1, "name": "dev", "extends": "portal",
                             "pieceTypes": {"stage": {
                                 "label": label("Etapa"), "profile": "portada", "register": "engraved",
                                 "closing": "No frame."}}})
        sheet = B.resolve("dev")
        stage = sheet["pieceTypes"]["stage"]
        self.assertEqual((stage["closing"], stage["paletteSentence"], stage["cleanZone"], stage["register"]),
                         ("No frame.", PIECE_PALETTE, "afterClosing", "engraved"))
        self.assertEqual(sheet["origin"]["pieceTypes.stage.closing"], {"origin": "own", "project": "dev"})
        self.assertEqual(sheet["origin"]["pieceTypes.stage.paletteSentence"], {"origin": "inherited", "project": "portal"})
        self.assertEqual(B.resolve("portal")["pieceTypes"]["stage"]["closing"], PIECE_CLOSING)
        self.assertEqual(B.assemble(sheet, "stage", "A chart.")["segments"][2]["text"], "No frame.")


class LintTests(unittest.TestCase):
    def good(self, piece="cover", subject=SUBJECT, zone=ZONE):
        return B.assemble(PORTAL, piece, subject, zone)["prompt"]

    def run_lint(self, prompt, **kw):
        return B.lint(PORTAL, prompt, **kw)

    def problems(self, result):
        return [(c["id"], c["message"]["key"]) for c in result["checks"] if c["status"] != "ok"]

    def test_assembled_prompt_passes(self):
        result = self.run_lint(self.good(), piece="cover", clean_zone=ZONE)
        self.assertEqual(self.problems(result), [])
        self.assertFalse(result["blocked"])
        self.assertEqual([c["id"] for c in result["checks"]],
                         ["words", "palette", "register", "closing", "cleanZone", "fillPhrase", "veto",
                          "neverWrite", "colorWord", "negation", "hex"])

    def test_words(self):
        result = self.run_lint(self.good(subject="A terminal window", zone=None), piece="cover")
        self.assertEqual(self.problems(result), [("words", "lint.words")])
        self.assertTrue(result["blocked"])
        self.assertEqual(result["checks"][0]["message"]["params"]["min"], 120)

    def test_palette_not_at_end(self):
        result = self.run_lint(self.good() + " Calm.", piece="cover")
        self.assertIn(("palette", "lint.palette"), self.problems(result))

    def test_palette_missing_hex(self):
        result = self.run_lint(self.good().replace(" and a touch of seaweed green #5d7a6a", ""), piece="cover")
        check = [c for c in result["checks"] if c["id"] == "palette"][0]
        self.assertEqual((check["status"], check["message"]["params"]["missing"]), ("error", "#5d7a6a"))

    def test_palette_missing_hex_with_a_multi_sentence_palette_sentence(self):
        sheet = copy.deepcopy(PORTAL)
        sheet["paletteSentence"] = "Palette: {halo}. Also {paper}, {ink} and {accent}"
        prompt = B.assemble(sheet, "cover", SUBJECT, ZONE)["prompt"]
        check = [c for c in B.lint(sheet, prompt, "cover", "brand", ZONE)["checks"] if c["id"] == "palette"][0]
        self.assertEqual(check["status"], "ok")
        bad = prompt.replace(" and a touch of seaweed green #5d7a6a", "")
        check = [c for c in B.lint(sheet, bad, "cover")["checks"] if c["id"] == "palette"][0]
        self.assertEqual((check["status"], check["message"]["params"]["missing"]), ("error", "#5d7a6a"))

    def test_short_and_alpha_hex_are_seen(self):
        for bad in ("#f00", "#ff0000cc", "#f00c"):
            prompt = self.good(subject=SUBJECT + ", a stripe " + bad)
            hexes = [(c["message"]["params"]["value"]) for c in self.run_lint(prompt, piece="cover")["checks"]
                     if c["id"] == "hex" and c["status"] != "ok"]
            self.assertEqual(hexes, [bad])

    def test_clean_zone_of_only_spaces_is_no_zone(self):
        prompt = B.assemble(PORTAL, "cover", SUBJECT, "   ")["prompt"]
        self.assertEqual(prompt, B.assemble(PORTAL, "cover", SUBJECT)["prompt"])
        self.assertNotIn(("cleanZone", "lint.clean_zone_missing"),
                         self.problems(self.run_lint(prompt, piece="cover", clean_zone="   ")))

    def test_a_register_contained_in_another_is_not_register_many(self):
        sheet = copy.deepcopy(PORTAL)
        sheet["registers"]["short"] = {"label": label("Corto"), "block": LINE.rstrip(".").split(",")[0]}
        prompt = B.assemble(sheet, "icon", SUBJECT)["prompt"]
        self.assertIn(sheet["registers"]["short"]["block"], prompt)
        result = B.lint(sheet, prompt, piece="icon")
        self.assertNotIn(("register", "lint.register_many"), self.problems(result))

    def test_a_short_register_also_written_apart_is_register_many(self):
        sheet = copy.deepcopy(PORTAL)
        sheet["registers"]["short"] = {"label": label("Corto"), "block": "fine sea chart"}
        prompt = B.assemble(sheet, "cover", SUBJECT)["prompt"]
        self.assertEqual(self.problems(B.lint(sheet, prompt, piece="cover")), [])
        apart = prompt + " Like a fine sea chart."
        found = [c for c in B.lint(sheet, apart, piece="cover")["checks"] if c["id"] == "register"][0]
        self.assertEqual((found["message"]["key"], found["message"]["params"]["registers"]),
                         ("lint.register_many", "engraved, short"))

    def test_other_registers_text_is_not_exempt_with_a_piece(self):
        sheet = copy.deepcopy(PORTAL)
        sheet["registers"]["line"]["block"] = LINE.rstrip(".") + ", golden"
        prompt = B.assemble(sheet, "cover", SUBJECT)["prompt"] + " " + sheet["registers"]["line"]["block"]
        with_piece_ = self.problems(B.lint(sheet, prompt, piece="cover"))
        self.assertIn(("negation", "lint.negation"), with_piece_)
        self.assertIn(("colorWord", "lint.color_word"), with_piece_)
        # without a piece every register's text is approved
        without = self.problems(B.lint(sheet, prompt))
        self.assertNotIn(("negation", "lint.negation"), without)
        self.assertNotIn(("colorWord", "lint.color_word"), without)

    def test_short_hex_needs_a_letter(self):
        for text in ("#2026", "#123", "#1234"):
            self.assertIsNone(B._HEX.search(text), text)
        self.assertEqual([m.group(0) for m in B._HEX.finditer("a #fa0 and #12ab and #123456")],
                         ["#fa0", "#12ab", "#123456"])
        result = self.run_lint(self.good(subject=SUBJECT + " for event #2026"), piece="cover")
        self.assertNotIn("hex", [p[0] for p in self.problems(result)])
        result = self.run_lint(self.good(subject=SUBJECT + " on #fa0"), piece="cover")
        self.assertIn(("hex", "lint.hex"), self.problems(result))

    def test_register_own_text_exempts_only_the_pieces_register(self):
        sheet = copy.deepcopy(PORTAL)
        sheet["registers"]["line"]["block"] = LINE.rstrip(".") + ", never a robot"
        sheet["vetoes"]["groups"][0]["terms"] = ["robot"]
        # as an icon (line register) the word is the register's own text; as a cover (engraved) it is not
        prompt = B.assemble(sheet, "icon", SUBJECT)["prompt"]
        self.assertNotIn(("veto", "lint.veto"), self.problems(B.lint(sheet, prompt, piece="icon")))
        self.assertIn(("veto", "lint.veto"), self.problems(B.lint(sheet, prompt, piece="cover")))

    def test_register_none(self):
        prompt = self.good().replace(ENGRAVED, "")
        self.assertIn(("register", "lint.register_none"), self.problems(self.run_lint(prompt)))

    def test_register_many(self):
        prompt = self.good().replace(ENGRAVED, ENGRAVED + " " + LINE)
        self.assertIn(("register", "lint.register_many"), self.problems(self.run_lint(prompt)))

    def test_register_wrong_for_piece(self):
        result = self.run_lint(self.good(), piece="icon")
        check = [c for c in result["checks"] if c["id"] == "register"][0]
        self.assertEqual((check["message"]["key"], check["message"]["params"]["expected"]),
                         ("lint.register_wrong", "line"))

    def test_closing_missing(self):
        prompt = self.good().replace(CLOSING, "")
        self.assertIn(("closing", "lint.closing"), self.problems(self.run_lint(prompt)))

    def test_clean_zone_after_register(self):
        prompt = self.good(zone=None).replace(ENGRAVED, ENGRAVED + " " + ZONE + ".")
        self.assertIn(("cleanZone", "lint.clean_zone_order"), self.problems(self.run_lint(prompt, clean_zone=ZONE)))

    def test_clean_zone_after_closing_needs_the_closing_and_its_order(self):
        zone = "the islet small on the left"
        sheet = with_piece(closing=PIECE_CLOSING, cleanZone="afterClosing")
        ok = B.assemble(sheet, "stage", "A chart.", zone)["prompt"]
        self.assertNotIn("cleanZone", [p[0] for p in self.problems_of(sheet, ok, zone)])
        # without the closing the zone has nothing to follow: only `closing` says so, not a second order error
        no_closing = ok.replace(PIECE_CLOSING.rstrip("."), "")
        found = self.problems_of(sheet, no_closing, zone)
        self.assertIn(("closing", "lint.closing"), found)
        self.assertNotIn("cleanZone", [p[0] for p in found])
        # the zone before the closing is not after it
        inside = ok.replace(zone, "").replace(PIECE_CLOSING.rstrip("."), zone + ". " + PIECE_CLOSING.rstrip("."))
        self.assertIn(("cleanZone", "lint.clean_zone_order"), self.problems_of(sheet, inside, zone))

    def problems_of(self, sheet, prompt, zone):
        return self.problems(B.lint(sheet, prompt, "stage", "brand", zone))

    def test_clean_zone_missing(self):
        self.assertIn(("cleanZone", "lint.clean_zone_missing"),
                      self.problems(self.run_lint(self.good(zone=None), clean_zone=ZONE)))

    def test_fill_phrase_with_clean_zone(self):
        prompt = self.good(subject=SUBJECT + ", waves filling the whole sheet")
        result = self.run_lint(prompt, piece="cover", clean_zone=ZONE)
        self.assertEqual(self.problems(result), [("fillPhrase", "lint.fill_phrase")])
        # without a clean zone the phrase is fine
        self.assertEqual(self.problems(self.run_lint(self.good(subject=SUBJECT + ", waves filling the whole sheet",
                                                               zone=None), piece="cover")), [])

    def test_veto_with_reason_and_span(self):
        prompt = self.good(subject=SUBJECT + ", a small Boat")
        result = self.run_lint(prompt, piece="cover")
        veto = [c for c in result["checks"] if c["id"] == "veto"]
        self.assertEqual(len(veto), 1)
        params = veto[0]["message"]["params"]
        self.assertEqual((params["term"], params["group"], params["reason"]["en"]),
                         ("boat", "nautical", "the sea is the where"))
        i, j = veto[0]["span"]
        self.assertEqual(prompt[i:j], "Boat")

    def test_real_closing_with_white_vetoed_not_blocked(self):
        result = self.run_lint(self.good(), piece="cover", clean_zone=ZONE)
        self.assertIn("no white margin", self.good())
        self.assertFalse(result["blocked"])
        self.assertEqual(self.problems(result), [])
        # the same word outside the shielded text still blocks
        bad = self.run_lint(self.good(subject=SUBJECT + ", a white ring"), piece="cover")
        self.assertIn(("colorWord", "lint.color_word"), self.problems(bad))

    def test_veto_plural(self):
        for text in ("paper boats", "two anchors", "tall lighthouses", "robots"):
            prompt = self.good(subject=SUBJECT + ", " + text)
            self.assertIn(("veto", "lint.veto"), self.problems(self.run_lint(prompt)), text)

    def test_color_word_plural(self):
        prompt = self.good(subject=SUBJECT + ", deep reds")
        checks = [c for c in self.run_lint(prompt, piece="cover")["checks"] if c["status"] != "ok"]
        self.assertEqual([prompt[c["span"][0]:c["span"][1]] for c in checks if c["id"] == "colorWord"], ["reds"])

    def test_never_write_plural(self):
        prompt = self.good(subject=SUBJECT + ", transparents")
        self.assertIn(("neverWrite", "lint.never_write"), self.problems(self.run_lint(prompt, piece="cover")))

    def test_veto_whole_word_only(self):
        prompt = self.good(subject=SUBJECT + ", boathouses of paper")
        self.assertEqual(self.problems(self.run_lint(prompt, piece="cover")), [])

    def test_veto_exception_only_for_its_piece(self):
        prompt = self.good(subject=SUBJECT + ", a lighthouse")
        self.assertEqual(self.problems(self.run_lint(prompt, piece="cover")), [])
        self.assertIn(("veto", "lint.veto"), self.problems(self.run_lint(prompt)))

    def test_never_write(self):
        prompt = self.good(subject=SUBJECT + ", on a transparent background")
        self.assertEqual(self.problems(self.run_lint(prompt, piece="cover")), [("neverWrite", "lint.never_write")])

    def test_color_word(self):
        prompt = self.good(subject=SUBJECT + ", a golden ring")
        result = self.run_lint(prompt, piece="cover")
        self.assertEqual(self.problems(result), [("colorWord", "lint.color_word")])
        # the palette's own names ("off-white") do not count
        self.assertEqual(self.problems(self.run_lint(self.good(), piece="cover")), [])

    def test_negation_outside_closing(self):
        prompt = self.good(subject=SUBJECT + ", not a harbour")
        result = self.run_lint(prompt, piece="cover")
        self.assertEqual(self.problems(result), [("negation", "lint.negation")])
        # the line register block carries approved negations
        icon = self.good(piece="icon", zone=None)
        self.assertNotIn("negation", [c[0] for c in self.problems(self.run_lint(icon, piece="icon"))])

    def test_hex_outside_palette(self):
        prompt = self.good(subject=SUBJECT + " on a plain flat solid bright green #00ff00 background")
        result = self.run_lint(prompt, piece="cover")
        self.assertEqual(self.problems(result), [("hex", "lint.hex")])
        # the chroma of the piece is allowed
        icon = self.good(piece="icon", zone=None,
                         subject=SUBJECT + " on a plain flat solid bright green #00ff00 background")
        self.assertNotIn("hex", [c[0] for c in self.problems(self.run_lint(icon, piece="icon"))])

    def test_free_mode_never_blocks(self):
        result = self.run_lint("a golden boat, not transparent, #123456", mode="free")
        self.assertFalse(result["blocked"])
        statuses = {c["status"] for c in result["checks"]}
        self.assertEqual(statuses - {"ok"}, {"warn"})
        self.assertIn("veto", [c["id"] for c in result["checks"] if c["status"] == "warn"])
        self.assertTrue(self.run_lint("a golden boat", mode="brand")["blocked"])

    def test_bad_mode(self):
        with self.assertRaises(GimgError) as cm:
            self.run_lint("x", mode="loose")
        self.assertEqual(cm.exception.code, "brandsheet.bad_mode")


if __name__ == "__main__":
    unittest.main()
