"""HTTP API of the brand sheet (0.7.0 step 2B): project sheet state, sheet view, prompt, lint, `sheet.*` check rows."""
import json

from gimg import brandsheet as B, doctor, server
from tests.test_brandsheet import PORTAL, SUBJECT, ZONE, Env
from tests.test_server import ServerBase


class SheetApi(ServerBase, Env):
    def setUp(self):
        Env.setUp(self)
        ServerBase.setUp(self)
        self.addCleanup(lambda: None)

    def get(self, path):
        resp, payload = self.call("GET", path)
        return resp, payload

    def ok(self, method, path, body=None):
        resp, payload = self.call(method, path, headers={"Content-Type": "application/json"} if body is not None else None,
                                  body=body)
        self.assertEqual(resp.status, 200, payload)
        return json.loads(payload)

    def rows(self, name):
        return {r["id"]: r for r in self.ok("GET", "/api/projects/%s/check" % name)}


class ProjectShowTests(SheetApi):
    def test_without_sheet_is_not_an_error(self):
        self.project("bare", rel=None)
        data = self.ok("GET", "/api/projects/bare")
        self.assertFalse(data["sheet"]["present"])
        self.assertEqual(data["pieceTypes"], [])
        self.assertIn("config", data)

    def test_with_sheet_and_inheritance(self):
        self.project("portal", PORTAL)
        self.project("child", {"schemaVersion": 1, "name": "child", "extends": "portal"})
        data = self.ok("GET", "/api/projects/child")
        self.assertTrue(data["sheet"]["valid"])
        self.assertEqual(data["sheet"]["extends"], ["portal"])
        self.assertEqual(data["sheet"]["version"], B.resolve("child")["version"])
        ids = [p["id"] for p in data["pieceTypes"]]
        self.assertEqual(ids, list(PORTAL["pieceTypes"]))
        self.assertEqual(data["pieceTypes"][0]["register"], PORTAL["pieceTypes"][ids[0]]["register"])

    def test_broken_parent_lists_the_errors(self):
        self.project("orphan", {"schemaVersion": 1, "name": "orphan", "extends": "ghost"})
        data = self.ok("GET", "/api/projects/orphan")
        self.assertTrue(data["sheet"]["present"])
        self.assertFalse(data["sheet"]["valid"])
        self.assertIn("ghost", " ".join(data["sheet"]["errors"]))


class SheetViewTests(SheetApi):
    def test_resolved_sheet_with_origin(self):
        self.project("portal", PORTAL)
        self.project("child", {"schemaVersion": 1, "name": "child", "extends": "portal", "closing": "No text."})
        data = self.ok("GET", "/api/projects/child/brand/sheet")
        self.assertEqual(data["roles"]["paper"]["hex"], "#fbfcfd")
        self.assertEqual(data["roles"]["paper"]["name"], "plain flat off-white")
        self.assertEqual(data["closing"], "No text.")
        self.assertEqual(data["origin"]["closing"]["origin"], "own")
        self.assertEqual(data["origin"]["palette.paper.$value"]["origin"], "inherited")
        self.assertEqual(data["origin"]["palette.paper.$value"]["project"], "portal")
        self.assertEqual(data["origin"]["palette.paper.$value"]["file"], "marca.json")

    def test_no_sheet_is_404_with_its_code(self):
        self.project("bare", rel=None)
        resp, payload = self.get("/api/projects/bare/brand/sheet")
        self.err(resp, payload, 404, "brandsheet.none")

    def test_broken_parent_is_422(self):
        self.project("orphan", {"schemaVersion": 1, "name": "orphan", "extends": "ghost"})
        resp, payload = self.get("/api/projects/orphan/brand/sheet")
        self.err(resp, payload, 422, "brandsheet.extends_missing")

    def test_parent_with_its_file_gone_is_422_extends_broken(self):
        # revisión paso 2, punto 1: the parent's missing file is not the child's
        parent = self.project("portal", PORTAL)
        self.project("child", {"schemaVersion": 1, "name": "child", "extends": "portal"})
        (parent / "marca.json").unlink()
        resp, payload = self.get("/api/projects/child/brand/sheet")
        self.err(resp, payload, 422, "brandsheet.extends_broken")
        resp, payload = self.call("POST", "/api/projects/child/brand/prompt",
                                  headers={"Content-Type": "application/json"}, body={"piece": next(iter(PORTAL["pieceTypes"])), "subject": "x"})
        self.err(resp, payload, 422, "brandsheet.extends_broken")

    def test_parent_with_invalid_config_is_422_not_500(self):
        parent = self.project("portal", PORTAL)
        self.project("child", {"schemaVersion": 1, "name": "child", "extends": "portal"})
        (parent / "galivelop-images.json").write_text(json.dumps({"name": "portal"}))
        resp, payload = self.get("/api/projects/child/brand/sheet")
        self.err(resp, payload, 422, "brandsheet.extends_broken")


class PromptTests(SheetApi):
    def post_prompt(self, name, body):
        return self.call("POST", "/api/projects/%s/brand/prompt" % name, headers={"Content-Type": "application/json"},
                         body=body)

    def test_same_shape_as_the_cli(self):
        self.project("portal", PORTAL)
        data = self.ok("POST", "/api/projects/portal/brand/prompt", {"piece": "cover", "subject": SUBJECT, "cleanZone": ZONE})
        self.assertEqual(data, B.prompt_response("portal", "cover", SUBJECT, ZONE))
        self.assertEqual(data["prompt"], B.assemble(PORTAL, "cover", SUBJECT, ZONE)["prompt"])
        self.assertEqual(set(data), {"prompt", "words", "segments", "checks", "blocked", "defaults", "known"})

    def test_from_is_not_supported_yet(self):
        self.project("portal", PORTAL)
        self.err(*self.post_prompt("portal", {"from": "a free prompt"}), 400, "brandsheet.convert_unsupported")

    def test_unknown_piece_and_bad_field(self):
        self.project("portal", PORTAL)
        self.err(*self.post_prompt("portal", {"piece": "nope", "subject": "x"}), 400, "brandsheet.unknown_piece")
        self.err(*self.post_prompt("portal", {"piece": "cover"}), 400, "api.bad_param")

    def test_project_without_sheet(self):
        self.project("bare", rel=None)
        self.err(*self.post_prompt("bare", {"piece": "cover", "subject": "x"}), 404, "brandsheet.none")


class LintTests(SheetApi):
    def post_lint(self, name, body):
        return self.call("POST", "/api/projects/%s/brand/lint" % name, headers={"Content-Type": "application/json"},
                         body=body)

    def test_free_mode_never_blocks(self):
        self.project("portal", PORTAL)
        data = self.ok("POST", "/api/projects/portal/brand/lint", {"prompt": "a red fox", "piece": "cover"})
        self.assertEqual(list(data), ["checks"])
        self.assertTrue(data["checks"])
        self.assertNotIn("error", {c["status"] for c in data["checks"]})

    def test_unknown_piece_and_missing_prompt(self):
        self.project("portal", PORTAL)
        self.err(*self.post_lint("portal", {"prompt": "x", "piece": "nope"}), 400, "brandsheet.unknown_piece")
        self.err(*self.post_lint("portal", {"piece": "cover"}), 400, "api.bad_param")


class CheckRowsTests(SheetApi):
    def test_rows_of_a_good_sheet(self):
        self.project("portal", PORTAL)
        rows = self.rows("portal")
        self.assertEqual(rows["sheet.valid"]["status"], "ok")
        self.assertEqual(rows["sheet.present"]["status"], "ok")
        self.assertEqual(rows["sheet.contrast"]["status"], "ok")
        self.assertEqual(set(rows["sheet.valid"]) - {"fix"}, {"id", "status", "message"})

    def test_no_sheet_warns_with_the_fix(self):
        self.project("bare", rel=None)
        row = self.rows("bare")["sheet.present"]
        self.assertEqual(row["status"], "warn")
        self.assertIn("gimg brand init --project bare", row["fix"])

    def test_broken_extends_fails(self):
        self.project("orphan", {"schemaVersion": 1, "name": "orphan", "extends": "ghost"})
        row = self.rows("orphan")["sheet.extends"]
        self.assertEqual(row["status"], "fail")
        self.assertIn("ghost", row["message"])

    def test_parent_file_gone_blames_the_inheritance(self):
        # revisión paso 2, punto 1: sheet.present of the child stays ok, the fix is not `brand init`
        parent = self.project("portal", PORTAL)
        self.project("child", {"schemaVersion": 1, "name": "child", "extends": "portal"})
        (parent / "marca.json").unlink()
        rows = self.rows("child")
        self.assertEqual(rows["sheet.present"]["status"], "ok")
        self.assertEqual(rows["sheet.extends"]["status"], "fail")
        self.assertIn("portal", rows["sheet.extends"]["message"])
        self.assertNotIn("brand init", rows["sheet.extends"].get("fix", ""))
        self.assertNotIn("sheet.valid", rows)

    def test_vivid_accent_with_a_deep_tone_is_ok(self):
        # revisión paso 2, punto 2: the teal accent (3.4:1 vivid) has a deep tone, so contrast is ok
        teal = json.loads(json.dumps(PORTAL))
        teal["palette"]["accent"]["$value"] = "#0e9a93"
        self.project("teal", teal)
        self.assertLess(B.contrast("#0e9a93", teal["palette"]["paper"]["$value"]), B.TONE_THRESHOLD)
        self.assertEqual(self.rows("teal")["sheet.contrast"]["status"], "ok")

    def test_low_contrast_warns(self):
        low = json.loads(json.dumps(PORTAL))
        low["palette"]["ink"]["$value"] = "#f0f0f0"
        self.project("pale", low)
        row = self.rows("pale")["sheet.contrast"]
        self.assertEqual(row["status"], "warn")
        self.assertIn("#f0f0f0", row["message"])

    def test_missing_file_fails(self):
        self.project("gone", None)
        rows = self.rows("gone")
        self.assertEqual(rows["sheet.present"]["status"], "fail")
