"""Hoja del Portal y de sus productos como datos (0.7.0, paso 3B): validan, se resuelven, reproducen los pedidos
aprobados y rechazan los descartes del troubleshooting por su motivo."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from gimg import brandsheet as B, schema as S
from tests.test_brandsheet import Env

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
PRODUCTS = ("galivelop-developer", "galivelop-image-generator", "galivelop-voice-generator", "galivelop-workflow")
SHEETS = sorted(p.parent.name for p in EXAMPLES.glob("*/marca.json"))
FIXTURE = json.loads((ROOT / "tests" / "fixtures" / "portal-pedidos.json").read_text(encoding="utf-8"))
ORDERS = EXAMPLES / "portal" / "orders" / "marca"
TONE_SCRIPTS = {
    "galivelop-developer": "tonos.py",
    "galivelop-image-generator": "acento_oklch.py",
    "galivelop-voice-generator": "tonos.py",
    "galivelop-workflow": "acento.py",
}


class PortalEnv(Env):
    def setUp(self):
        super().setUp()
        self.register(("portal",) + PRODUCTS)

    def register(self, names):
        from gimg import projects
        for name in names:
            projects.add(EXAMPLES / name)

    def errors(self, sheet, prompt, piece, zone=None):
        """The error checks of `lint` as (check id, group id or term, entry)."""
        out = []
        for c in B.lint(sheet, prompt, piece, "brand", zone)["checks"]:
            if c["status"] == "error":
                params = c["message"]["params"]
                out.append((c["id"], params.get("group") or params.get("term"), c))
        return out

    def vetoes(self, sheet, prompt, piece, zone=None):
        return {(cid, key) for cid, key, _ in self.errors(sheet, prompt, piece, zone) if cid == "veto"}


class ExamplesTests(PortalEnv):
    def test_every_example_sheet_validates_and_is_the_one_its_project_declares(self):
        self.assertEqual(SHEETS, sorted(("portal",) + PRODUCTS))
        schema = S.load_schema("brand-sheet")
        for name in SHEETS:
            data = json.loads((EXAMPLES / name / "marca.json").read_text(encoding="utf-8"))
            self.assertEqual(S.validate(data, schema), [], name)
            config = json.loads((EXAMPLES / name / "galivelop-images.json").read_text(encoding="utf-8"))
            self.assertEqual(config["brand"]["sheet"], "marca.json", name)
            self.assertEqual(data["name"], name)

    def test_every_sheet_resolves_and_products_inherit_the_portal(self):
        portal = B.resolve("portal")
        self.assertEqual(portal["chain"], ["portal"])
        for name in PRODUCTS:
            sheet = B.resolve(name)
            self.assertEqual(sheet["chain"], [name, "portal"])
            self.assertEqual(sheet["registers"], portal["registers"])
            self.assertEqual(sheet["closing"], portal["closing"])
            self.assertEqual(sheet["pieceTypes"], portal["pieceTypes"])
            self.assertEqual(sheet["palette"]["halo"], portal["palette"]["halo"])
            self.assertEqual(sheet["palette"]["paper"], portal["palette"]["paper"])

    def test_products_declare_only_accent_and_their_own_vetoes(self):
        for name in PRODUCTS:
            sheet = B.resolve(name)
            own = {field.split(".")[0] for field, o in sheet["origin"].items() if o["project"] == name}
            self.assertLessEqual(own, {"palette", "paletteSentence", "vetoes"}, name)
            palette_own = {f for f, o in sheet["origin"].items() if o["project"] == name and f.startswith("palette.")}
            self.assertTrue(all(f.startswith("palette.accent.") for f in palette_own if f != "paletteSentence"), name)
            self.assertIn("palette.accent.$value", palette_own, name)

    def test_piece_profiles_exist_in_the_portal_config(self):
        profiles = json.loads((EXAMPLES / "portal" / "galivelop-images.json").read_text())["profiles"]
        for piece, spec in B.resolve("portal")["pieceTypes"].items():
            self.assertIn(spec["profile"], profiles, piece)

    def test_references_exist(self):
        for rel in B.resolve("portal")["acceptance"]["references"]:
            self.assertTrue((EXAMPLES / "portal" / rel).is_file(), rel)

    def test_portal_literals_of_the_sheet(self):
        sheet = B.resolve("portal")
        self.assertEqual(B.palette_sentence(sheet),
                         "Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, "
                         "off-white #fbfcfd, ink grey #13212b and a touch of seaweed green #5d7a6a.")
        self.assertEqual(sheet["registers"]["line"]["block"].split(":")[0], "Simple line icon style")
        self.assertTrue(sheet["registers"]["engraved"]["block"].startswith("Richly detailed engraved antique"))
        pal = B.palette(sheet)
        for hex_ in ("#0072a8", "#1aa6df", "#fbfcfd", "#13212b", "#5d7a6a", "#e6eef3", "#0d171e"):
            self.assertIn(hex_, pal)


class ToneTests(PortalEnv):
    def script_tones(self, name):
        script = ROOT / "docs" / "marcas" / name / TONE_SCRIPTS[name]
        if not script.is_file():
            self.skipTest("no tone script for " + name)
        accent = json.loads((EXAMPLES / name / "marca.json").read_text())["palette"]["accent"]["$value"]
        out = subprocess.run([sys.executable, str(script), accent], capture_output=True, text=True, check=True).stdout
        deep = re.search(r"^hondo\s+(#[0-9a-f]{6})", out, re.M).group(1)
        dark = re.search(r"^oscuro\s+(#[0-9a-f]{6})", out, re.M).group(1)
        return accent, {"deep": deep, "dark": dark}

    def test_accent_tones_match_the_product_scripts(self):
        for name in PRODUCTS:
            accent, expected = self.script_tones(name)
            self.assertEqual(B.accent_tones(accent), expected, name)
            pal = B.palette(B.resolve(name))
            self.assertIn(expected["deep"], pal, name)
            self.assertIn(expected["dark"], pal, name)
            self.assertNotIn("#5d7a6a", pal, name)  # the product accent takes the place of the seaweed green

    def test_developer_sentence_names_the_deep_tone(self):
        sheet = B.resolve("galivelop-developer")
        self.assertEqual(B.accent_tones(sheet["palette"]["accent"]["$value"])["deep"], "#16827c")
        self.assertTrue(B.palette_sentence(sheet).endswith("and a touch of deep teal #16827c."))

    def test_product_sentences_carry_the_vivid_accent(self):
        for name, ending in (("galivelop-image-generator", "a touch of violet #7c5cd6."),
                             ("galivelop-voice-generator", "a touch of raspberry pink #d9467a."),
                             ("galivelop-workflow", "a touch of cobalt blue #3d6fd9.")):
            self.assertTrue(B.palette_sentence(B.resolve(name)).endswith(ending), name)


class ReproductionTests(PortalEnv):
    def case(self, order):
        return next(c for c in FIXTURE["cases"] if c["order"] == order)

    def order_prompt(self, case):
        return json.loads((ORDERS / (case["order"] + ".json")).read_text(encoding="utf-8"))["prompt"]

    def norm(self, text):
        return " ".join(text.split())

    def build(self, case, sheet=None):
        return B.assemble(sheet or B.resolve("portal"), case["piece"], case["subject"], case["cleanZone"])

    def test_approved_orders_are_reproduced_word_for_word_from_subject_and_zone(self):
        self.assertEqual([c["order"] for c in FIXTURE["cases"]],
                         ["19-enviado", "06-portada-desarrollo", "06-portada-diseno", "06-portada-publicado"])
        for case in FIXTURE["cases"]:
            self.assertEqual(self.norm(self.build(case)["prompt"]), self.norm(self.order_prompt(case)), case["order"])

    def test_products_reproduce_the_same_orders_but_for_their_accent(self):
        # the product only changes the palette sentence's accent; everything before it is the Portal's
        for name in PRODUCTS:
            sheet = B.resolve(name)
            for case in FIXTURE["cases"]:
                built = self.build(case, sheet)["prompt"]
                self.assertEqual(self.norm(built).rsplit(" Palette ", 1)[0],
                                 self.norm(self.order_prompt(case)).rsplit(" Palette ", 1)[0], (name, case["order"]))

    def test_the_15_of_developer_is_obsolete_and_the_sheet_vetoes_it(self):
        sheet = B.resolve("portal")
        case = FIXTURE["obsolete"][0]
        self.assertEqual(case["order"], "15-proximamente-developer")
        built = B.assemble(sheet, case["piece"], case["subject"], case["cleanZone"])["prompt"]
        self.assertEqual(sorted({(cid, key) for cid, key, _ in self.errors(sheet, built, case["piece"], case["cleanZone"])}),
                         [("colorWord", "white"), ("veto", "nautical")])

    def test_the_06_put_the_zone_at_the_end_of_their_own_closing(self):
        case = self.case("06-portada-desarrollo")
        built = self.build(case)
        self.assertEqual([s["role"] for s in built["segments"]], ["subject", "register", "closing", "palette"])
        self.assertEqual(built["segments"][1]["source"], "registers.engraved-stage")
        self.assertEqual(built["segments"][2]["source"], "pieceTypes.stage-cover.closing")
        self.assertTrue(built["segments"][2]["text"].endswith("no frame, " + case["cleanZone"] + "."))
        self.assertEqual(self.build(self.case("19-enviado"))["segments"][2]["source"], "pieceTypes.sent.closing")

    def test_the_order_of_a_default_piece_is_subject_zone_register_closing_palette(self):
        built = B.assemble(B.resolve("portal"), "cover", "A sea chart.", "The lower third is open")
        self.assertEqual([s["role"] for s in built["segments"]],
                         ["subject", "cleanZone", "register", "closing", "palette"])
        self.assertTrue(built["prompt"].endswith(B.palette_sentence(B.resolve("portal"))))

    def test_approved_orders_trip_only_the_expected_checks(self):
        sheet = B.resolve("portal")
        for case in FIXTURE["cases"]:
            built = self.build(case)["prompt"]
            found = sorted({(cid, key) for cid, key, _ in self.errors(sheet, built, case["piece"], case["cleanZone"])})
            # 19 is 111 words and the 06 are 224-268, the limits being 120-200: only the length trips, no veto
            self.assertEqual([cid for cid, _ in found], ["words"], (case["order"], found))


class LintTroubleshootingTests(PortalEnv):
    def setUp(self):
        super().setUp()
        self.sheet = B.resolve("portal")

    def prompt(self, piece, subject, zone=None):
        return B.assemble(self.sheet, piece, subject, zone)["prompt"]

    def blocked_by(self, piece, subject, group, term=None, sheet=None):
        sheet = sheet or self.sheet
        built = B.assemble(sheet, piece, subject)["prompt"]
        found = [c for cid, key, c in self.errors(sheet, built, piece) if cid == "veto" and key == group]
        self.assertTrue(found, "%s did not trip %s" % (subject, group))
        params = found[0]["message"]["params"]
        group_data = next(g for g in sheet["vetoes"]["groups"] if g["id"] == group)
        self.assertEqual(params["reason"], group_data["reason"])
        self.assertTrue(params["reason"]["es"] and params["reason"]["en"])
        if term:
            self.assertEqual(params["term"], term)
        self.assertTrue(B.lint(sheet, built, piece)["blocked"])
        return params

    def test_editor_window_in_a_cover_q574_q607(self):
        params = self.blocked_by("cover", "A code editor window resting on calm charted water on the left third",
                                 "glyph-windows", "editor window")
        self.assertIn("q574-q607", params["reason"]["es"])
        self.blocked_by("stage-cover", "A terminal window on the water", "glyph-windows", "terminal window")

    def test_window_is_fine_as_a_line_icon(self):
        built = self.prompt("icon", "A terminal window with a prompt chevron and a block caret")
        self.assertEqual(self.vetoes(self.sheet, built, "icon"), set())

    def test_navigation_compass_q610_q616(self):
        params = self.blocked_by("stage-cover", "A navigation compass lying on the chart", "navigation-compass")
        self.assertIn("q610", params["reason"]["es"])

    def test_the_compass_rose_is_not_vetoed(self):
        built = self.prompt("cover", "A sea chart with a small compass rose in one corner")
        self.assertEqual(self.vetoes(self.sheet, built, "cover"), set())

    def test_camera_prefix_q614(self):
        params = self.blocked_by("cover", "Seen from high above looking down, a sea chart of the coast", "camera-prefix")
        self.assertIn("q614", params["reason"]["es"])

    def test_clock_with_arrow_q646_q647(self):
        params = self.blocked_by("icon", "A clock with an arrow turning backwards", "clock-arrow", "clock")
        self.assertIn("q646", params["reason"]["es"])

    def test_nautical_motifs_outside_their_exception(self):
        for piece, subject, term in (("cover", "A lighthouse on a small rocky islet", "lighthouse"),
                                     ("cover", "A paper boat on the sea", "boat"),
                                     ("icon", "A small anchor", "anchor"),
                                     ("coming-soon", "A line of buoys", "buoy"),
                                     ("sent", "A lighthouse beside the quay", "lighthouse"),
                                     ("stage-cover", "A small anchor on the chart", "anchor"),
                                     ("stage-cover-night", "A small anchor on the chart", "anchor")):
            params = self.blocked_by(piece, subject, "nautical", term)
            self.assertIn("tres excepciones", params["reason"]["es"])

    def test_the_crane_is_an_exception_of_the_06_and_nowhere_else(self):
        subject = "A wooden crane on the quay"
        for piece in ("stage-cover", "stage-cover-night"):
            self.assertEqual(self.vetoes(self.sheet, self.prompt(piece, subject), piece), set(), piece)
        for piece in ("cover", "icon", "sent", "coming-soon"):
            params = self.blocked_by(piece, subject, "nautical", "crane")
            self.assertIn("grúa", params["reason"]["es"])

    def test_the_three_exceptions_pass_in_their_piece_type(self):
        for piece, subject in (("sent", "A paper boat leaving a quay"),
                               ("stage-cover-night", "A lighthouse at night"),
                               ("stage-cover", "A lighthouse under construction on a rocky islet"),
                               ("stage-cover", "A small buoy on open water"),
                               ("stage-cover", "A folded paper boat with a pennant")):
            self.assertEqual(self.vetoes(self.sheet, self.prompt(piece, subject), piece), set(), subject)

    def test_the_boat_of_the_19_does_not_leak_to_the_15_of_developer(self):
        subject = "A folded paper boat on a sea with waves"
        self.blocked_by("coming-soon", subject, "nautical", "boat")
        developer = B.resolve("galivelop-developer")
        for piece in ("coming-soon", "cover", "social"):
            built = B.assemble(developer, piece, subject)["prompt"]
            self.assertEqual(self.vetoes(developer, built, piece), set(), piece)
        built = B.assemble(developer, "stage-cover", "A lighthouse on a rocky islet")["prompt"]
        self.assertEqual(self.vetoes(developer, built, "stage-cover"), set())  # the Portal's own exception, inherited
        self.blocked_by("icon", "A paper boat", "nautical", "boat", sheet=developer)

    def test_words_that_are_never_written(self):
        for word in ("transparent", "exactly", "sky blue"):
            built = self.prompt("cover", "A chart with %s water" % word)
            found = [c for cid, _, c in self.errors(self.sheet, built, "cover") if cid == "neverWrite"]
            self.assertEqual([c["message"]["params"]["term"] for c in found], [word])

    def test_colour_names_outside_the_palette_sentence(self):
        built = self.prompt("cover", "A white line on a golden ring")
        terms = sorted(key for cid, key, _ in self.errors(self.sheet, built, "cover") if cid == "colorWord")
        self.assertEqual(terms, ["golden", "white"])
        # «ink grey» and «off-white» are the sheet's own names: not a colour word
        built = self.prompt("cover", "An ink grey line on off-white paper")
        self.assertEqual([k for cid, k, _ in self.errors(self.sheet, built, "cover") if cid == "colorWord"], [])

    def test_fill_phrase_with_a_clean_zone(self):
        zone = "The lower third of the sheet is plain flat off-white paper, open and unmarked"
        built = self.prompt("cover", "A sea chart of the coast, hatching filling the whole sheet to every edge", zone)
        self.assertIn("fillPhrase", [cid for cid, _, _ in self.errors(self.sheet, built, "cover", zone)])
        clean = self.prompt("cover", "A sea chart of the coast", zone)
        self.assertNotIn("fillPhrase", [cid for cid, _, _ in self.errors(self.sheet, clean, "cover", zone)])

    def test_ethics_is_inherited_by_every_product(self):
        for name in PRODUCTS:
            sheet = B.resolve(name)
            self.blocked_by("cover", "A robot hand holding a chart", "ethics", sheet=sheet)

    def test_product_vetoes_are_their_own(self):
        for name, subject in (("galivelop-developer", "A keyboard beside a gear"),
                              ("galivelop-image-generator", "A paintbrush on a canvas"),
                              ("galivelop-voice-generator", "A microphone in a studio"),
                              ("galivelop-workflow", "A glowing circuit with a pill")):
            sheet = B.resolve(name)
            self.blocked_by("icon", subject, name.replace("galivelop-", "") + "-never", sheet=sheet)
            self.assertNotIn(name.replace("galivelop-", "") + "-never",
                             [g["id"] for g in B.resolve("portal")["vetoes"]["groups"]])


if __name__ == "__main__":
    unittest.main()
