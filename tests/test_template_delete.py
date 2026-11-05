"""F4e.1a trozo 2 (D41): delete a template (`compose.delete_template`, DELETE and GET of .../templates/{id},
`gimg template rm`). The default one is protected; ids and folders are guarded; the count of attempts that use it."""
import io
import json
import sys
import unittest
from unittest import mock

from gimg import compose, log, orders, paths
from tests.test_compose_delete import Tty
from tests.test_server_read import NAME
from tests.test_template_save import SVG, SaveBase


class TemplateDeleteTests(SaveBase):
    def setUp(self):
        super().setUp()
        self.proj_dir = self.root / "templates" / "og"

    def save(self, name, dest="local"):
        return self.ok("POST", self.url, self.body(name, dest), 201)

    def one(self, id):
        return "%s/%s" % (self.url, id)

    def names(self, folder):
        return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []

    def cli_fails(self, *argv, stdin=None):
        import contextlib
        from gimg import cli
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch.object(sys, "stdin", stdin or io.StringIO()):
                code = cli.main(list(argv))
        self.assertEqual((code, out.getvalue()), (1, ""), argv)
        return err.getvalue()

    def test_a_local_template_goes_with_its_sidecar_and_the_others_stay(self):
        self.save("mio"), self.save("otro")
        got = self.ok("DELETE", self.one("mio"))
        self.assertEqual((got["id"], got["source"], got["files"], got["inRepo"]), ("mio", "local", 2, False))
        self.assertEqual(self.names(self.data), ["otro.json", "otro.svg"])
        self.assertEqual(sorted(i["id"] for i in self.ok("GET", self.url)), ["default", "otro"])

    def test_a_project_template_is_deleted_and_says_it_stays_in_the_repo(self):
        self.save("suyo", "project")
        self.assertEqual(self.names(self.proj_dir), ["suyo.json", "suyo.svg"])
        got = self.ok("DELETE", self.one("suyo"))
        self.assertEqual((got["source"], got["files"], got["inRepo"]), ("project", 2, True))
        self.assertEqual(self.names(self.proj_dir), [])

    def test_a_template_without_sidecar_counts_one_file(self):
        self.save("mio")
        (self.data / "mio.json").unlink()
        self.assertEqual(self.ok("DELETE", self.one("mio"))["files"], 1)

    def test_the_default_template_is_protected(self):
        self.bad("DELETE", self.one("default"), None, 409, "compose.delete_default")
        self.assertTrue((self.root / "t.svg").is_file())
        self.assertEqual(sorted(i["id"] for i in self.ok("GET", self.url)), ["default"])
        self.assertIn("is the default one of the profile", self.cli_fails(
            "--lang", "en", "template", "rm", NAME, "og", "default", "--yes"))

    def test_a_project_file_that_is_the_configured_default_is_protected_too(self):
        self.proj_dir.mkdir(parents=True)
        (self.proj_dir / "base.svg").write_text(SVG, encoding="utf-8")
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["profiles"]["og"]["compose"]["template"] = "templates/og/base.svg"
        path.write_text(json.dumps(cfg))
        self.bad("DELETE", self.one("base"), None, 409, "compose.delete_default")
        self.assertTrue((self.proj_dir / "base.svg").is_file())

    def test_a_template_declared_in_the_config_is_not_a_file_to_delete(self):
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["profiles"]["og"]["compose"]["templates"] = {"viejo": {"template": "t.svg"}}
        path.write_text(json.dumps(cfg))
        self.bad("DELETE", self.one("viejo"), None, 409, "compose.delete_config")
        self.assertTrue((self.root / "t.svg").is_file())

    def test_a_nonexistent_template_is_404_and_so_is_a_nonexistent_profile(self):
        self.bad("DELETE", self.one("nada"), None, 404, "compose.delete_unknown")
        self.bad("DELETE", "/api/projects/%s/profiles/nada/templates/mio" % NAME, None, 404, "order.profile_unknown")
        self.assertIn("has no local or project template", self.cli_fails(
            "--lang", "en", "template", "rm", NAME, "og", "nada", "--yes"))

    def test_an_id_with_traversal_or_a_bad_shape_is_rejected_with_its_code_and_nothing_goes(self):
        self.save("mio")
        outside = self.tmp / "ajeno.svg"
        outside.write_text("x")
        for bad in ("..%2F..%2Fajeno", "%2E%2E", "a%2Fb", "a%5Cb", "MIO", "x" * 41, "-a"):
            resp, payload = self.send("DELETE", self.one(bad))
            self.assertIn(resp.status, (400, 404), (bad, payload))
            if resp.status == 400:
                self.assertEqual(json.loads(payload)["error"]["code"], "compose.bad_name", bad)
        self.assertTrue(outside.is_file())
        self.assertEqual(self.names(self.data), ["mio.json", "mio.svg"])
        with self.assertRaises(compose.GimgError) as cm:
            compose.delete_template(NAME, "og", "../../ajeno")
        self.assertEqual(cm.exception.code, "compose.bad_name")

    def test_a_templates_dir_that_leaves_the_project_is_refused_with_its_code(self):
        outside = self.tmp / "outside"
        (outside / "og").mkdir(parents=True)
        (outside / "og" / "mio.svg").write_text(SVG)
        (self.root / "templates").symlink_to(outside)
        resp, payload = self.send("DELETE", self.one("mio"))
        self.assertEqual(resp.status, 400, payload)
        self.assertEqual(json.loads(payload)["error"]["code"], "path.outside")
        self.assertTrue((outside / "og" / "mio.svg").is_file())

    def test_usage_counts_the_attempts_that_have_the_template(self):
        self.save("mio"), self.save("otro")
        for n, tpl in ((1, "mio"),):
            orders.set_composed(NAME, self.key, "og", n, {"templateId": tpl, "layout": {}})
        other, _ = self.make_order(key="fauna/otro", profile="og", count=2)
        orders.set_composed(NAME, other, "og", 1, {"templateId": "mio"})
        orders.set_composed(NAME, other, "og", 2, {"templateId": "otro"})
        got = self.ok("GET", self.one("mio"))
        self.assertEqual(got, {"id": "mio", "source": "local", "usedBy": 2, "inRepo": False})
        self.assertEqual(self.ok("GET", self.one("otro"))["usedBy"], 1)
        self.assertEqual(self.ok("DELETE", self.one("mio"))["usedBy"], 2)
        self.assertEqual(self.names(self.data), ["otro.json", "otro.svg"])  # GET deleted nothing, DELETE only its own

    def test_usage_counts_a_failed_composition_by_its_compose_error(self):
        self.save("mio")
        self.assertEqual(self.stored_attempt().get("composeError", {}).get("templateId"), None)
        self.assertEqual(self.ok("GET", self.one("mio"))["usedBy"], 0)
        orders.set_compose_error(NAME, self.key, "og", 1, {"code": "x", "params": {}}, template_id="mio")
        self.assertEqual(self.ok("GET", self.one("mio"))["usedBy"], 1)

    def stored_attempt(self):
        return orders.get(NAME, self.key, "og")["attempts"][0]

    def test_api_equals_cli_and_the_log_gets_a_line(self):
        self.save("uno"), self.save("dos")
        via_api = self.ok("DELETE", self.one("uno"))
        via_cli = self.cli_json("template", "rm", NAME, "og", "dos", "--yes")
        self.assertEqual(dict(via_api, id=0), dict(via_cli, id=0))
        lines = [json.loads(x) for x in log.log_path(NAME).read_text().splitlines()]
        lines = [r for r in lines if r["gen_ai.operation.name"] == log.OP_TEMPLATE_DELETE]
        self.assertEqual(len(lines), 2)
        self.assertEqual((lines[0]["app.task"], lines[0]["app.image.template"]), ("og", "uno"))
        self.assertNotIn("gen_ai.provider.name", lines[0])

    def test_cli_without_yes_and_without_a_terminal_fails_with_its_reason(self):
        self.save("mio")
        err = self.cli_fails("--lang", "en", "template", "rm", NAME, "og", "mio", stdin=io.StringIO("y\n"))
        self.assertIn("no terminal to ask", err)
        self.assertEqual(self.names(self.data), ["mio.json", "mio.svg"])

    def test_cli_warns_before_asking_and_a_no_deletes_nothing(self):
        self.save("suyo", "project")
        orders.set_composed(NAME, self.key, "og", 1, {"templateId": "suyo"})
        err = self.cli_fails("--lang", "en", "template", "rm", NAME, "og", "suyo", stdin=Tty("n\n"))
        self.assertIn("1 attempts use it", err)
        self.assertIn("stays in the repository, uncommitted", err)
        self.assertIn("nothing was deleted", err)
        self.assertEqual(self.names(self.proj_dir), ["suyo.json", "suyo.svg"])
        with mock.patch.object(sys, "stdin", Tty("y\n")):
            out = self.cli("--lang", "en", "template", "rm", NAME, "og", "suyo")
        self.assertIn("Template \"suyo\" deleted", out)
        self.assertEqual(self.names(self.proj_dir), [])


if __name__ == "__main__":
    unittest.main()
