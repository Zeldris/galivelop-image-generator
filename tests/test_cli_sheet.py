"""gimg brand init | prompt | lint (0.7.0 step 2A)."""
import contextlib
import io
import json
import unittest

from gimg import brandsheet as B, cli, projects, schema
from tests.test_brandsheet import PORTAL, SUBJECT, ZONE, Env


class SheetCli(Env):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv) + ["--lang", "en"])
        return code, out.getvalue(), err.getvalue()


class InitTests(SheetCli):
    def test_init_writes_valid_sheet_and_links_it(self):
        root = self.project("fresh", rel=None)
        code, out, err = self.run_cli("brand", "init", "--project", "fresh")
        self.assertEqual((code, err), (0, ""))
        data = json.loads((root / "marca.json").read_text())
        self.assertEqual(schema.validate(data, schema.load_schema("brand-sheet")), [])
        self.assertEqual(projects.get("fresh")["config"]["brand"]["sheet"], "marca.json")
        self.assertEqual(B.resolve("fresh")["name"], "fresh")

    def test_init_does_not_overwrite_without_force(self):
        root = self.project("fresh", rel=None)
        self.run_cli("brand", "init", "--project", "fresh")
        (root / "marca.json").write_text(json.dumps({"mine": 1}))
        code, out, err = self.run_cli("brand", "init", "--project", "fresh")
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)
        self.assertIn("--force", err)
        self.assertEqual(json.loads((root / "marca.json").read_text()), {"mine": 1})
        self.assertEqual(self.run_cli("brand", "init", "--project", "fresh", "--force")[0], 0)
        self.assertNotIn("mine", json.loads((root / "marca.json").read_text()))

    def test_init_never_writes_over_the_config_nor_git(self):
        # revisión paso 2, punto 5: `brand.sheet` passes the same guard as delivery.dir and manifest, also with --force
        for rel, code_expected in (("galivelop-images.json", "cannot be galivelop-images.json"),
                                   (".git/marca.json", "cannot be inside .git")):
            root = self.project("fresh", rel=None)
            cfg_path = root / "galivelop-images.json"
            cfg = json.loads(cfg_path.read_text())
            cfg["brand"] = {"sheet": rel}
            cfg_path.write_text(json.dumps(cfg))
            before = cfg_path.read_text()
            code, _, err = self.run_cli("brand", "init", "--project", "fresh", "--force", "--json")
            self.assertEqual(code, 1)
            self.assertIn(code_expected, err)
            self.assertEqual(cfg_path.read_text(), before)
            self.assertFalse((root / ".git" / "marca.json").exists())

    def test_init_extends_and_unknown_parent(self):
        self.project("parent", PORTAL)
        root = self.project("child", rel=None)
        code, _, err = self.run_cli("brand", "init", "--project", "child", "--extends", "ghost")
        self.assertEqual(code, 1)
        self.assertIn("ghost", err)
        self.assertFalse((root / "marca.json").exists())
        self.assertEqual(self.run_cli("brand", "init", "--project", "child", "--extends", "parent")[0], 0)
        self.assertEqual(json.loads((root / "marca.json").read_text())["extends"], "parent")
        self.assertEqual(B.resolve("child")["closing"], PORTAL["closing"])


class PromptTests(SheetCli):
    def test_prompt_matches_assemble_and_json_shape(self):
        self.project("portal", PORTAL)
        code, out, err = self.run_cli("brand", "prompt", "--project", "portal", "--piece", "cover",
                                      "--subject", SUBJECT, "--clean-zone", ZONE, "--json")
        self.assertEqual((code, err), (0, ""))
        res = json.loads(out)
        self.assertEqual(res["prompt"], B.assemble(PORTAL, "cover", SUBJECT, ZONE)["prompt"])
        self.assertEqual(set(res), {"prompt", "words", "segments", "checks", "blocked", "defaults", "known"})
        self.assertEqual(res["defaults"]["seed"], 42)
        code, out, _ = self.run_cli("brand", "prompt", "--project", "portal", "--piece", "cover", "--subject", SUBJECT)
        self.assertEqual(code, 0)
        self.assertIn(SUBJECT, out)

    def test_blocked_prompt_exits_1_with_reason(self):
        self.project("portal", PORTAL)
        code, out, _ = self.run_cli("brand", "prompt", "--project", "portal", "--piece", "cover",
                                    "--subject", SUBJECT + ", a small boat")
        self.assertEqual(code, 1)
        self.assertIn("“boat” is vetoed (group nautical)", out)
        self.assertIn("blocked", out)

    def test_unknown_piece_is_a_user_error(self):
        self.project("portal", PORTAL)
        code, out, err = self.run_cli("brand", "prompt", "--project", "portal", "--piece", "poster", "--subject", "x")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("no piece type poster", err)


class LintTests(SheetCli):
    def setUp(self):
        super().setUp()
        self.project("portal", PORTAL)
        self.good = B.assemble(PORTAL, "cover", SUBJECT, ZONE)["prompt"]

    def test_good_prompt_passes(self):
        code, out, err = self.run_cli("brand", "lint", "--project", "portal", "--piece", "cover", "--prompt", self.good,
                                      "--clean-zone", ZONE)
        self.assertEqual((code, err), (0, ""))
        self.assertNotIn("[error]", out)

    def test_error_blocks_in_brand_with_reason_and_not_in_free(self):
        bad = self.good.replace("sea chart", "sea chart with a robot", 1)
        args = ("brand", "lint", "--project", "portal", "--piece", "cover", "--prompt", bad)
        code, out, _ = self.run_cli(*args)
        self.assertEqual(code, 1)
        self.assertIn("[error] veto: “robot” is vetoed (group ethics)", out)
        code, out, _ = self.run_cli(*args, "--mode", "free")
        self.assertEqual(code, 0)
        self.assertIn("[warn] veto", out)

    def test_file_and_json(self):
        path = self.tmp / "p.txt"
        path.write_text(self.good + " no", encoding="utf-8")
        code, out, _ = self.run_cli("brand", "lint", "--project", "portal", "--file", str(path), "--json")
        res = json.loads(out)
        self.assertEqual(set(res), {"checks", "blocked"})
        self.assertEqual(code, 1 if res["blocked"] else 0)

    def test_needs_exactly_one_source(self):
        code, _, err = self.run_cli("brand", "lint", "--project", "portal")
        self.assertEqual(code, 1)
        self.assertIn("exactly one of --prompt or --file", err)


if __name__ == "__main__":
    unittest.main()
