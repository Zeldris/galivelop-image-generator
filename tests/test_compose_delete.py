"""F4e.1a trozo 2 (D41): delete the composition of an attempt (`orders.delete_compose`, DELETE ...//compose and
`gimg compose rm`). Edge cases: it goes back to its raw image; nothing composed; a lock in use; the chosen one says so;
`rm` without `--yes` and without a terminal; CLI = API."""
import io
import json
import sys
import unittest
from unittest import mock

from gimg import fsutil, log, orders, paths
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase

LAYOUT = {"templateId": "default", "layout": {"title": {"dx": 3}}}


class Tty(io.StringIO):
    def isatty(self):
        return True


class ComposeDeleteTests(WriteBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order()
        self.folder = paths.project_data_dir(NAME) / "orders" / self.key / ("@" + self.profile)

    def compose(self, n=1, key=None):
        """Fake a finished composition for attempt `n`: the raw image stays, the composed one is written."""
        key = key or self.key
        item = orders.get(NAME, key, self.profile)["attempts"][n - 1]
        raw, image = orders.compose_names(item)
        folder = paths.project_data_dir(NAME) / "orders" / key / ("@" + self.profile)
        (folder / raw).write_bytes((folder / item["image"]).read_bytes())
        (folder / image).write_bytes(b"composed")
        orders.set_composed(NAME, key, self.profile, n, LAYOUT)
        return folder / raw, folder / image

    def url(self, n=1, key=None):
        return self.att(key or self.key, self.profile, n, "/compose")

    def stored(self, n=1, key=None):
        return orders.get(NAME, key or self.key, self.profile)["attempts"][n - 1]

    def cli_fails(self, *argv, stdin=None):
        import contextlib
        from gimg import cli
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch.object(sys, "stdin", stdin or io.StringIO()):
                code = cli.main(list(argv))
        self.assertEqual((code, out.getvalue()), (1, ""), argv)
        return err.getvalue()

    def test_a_deleted_composition_leaves_the_attempt_on_its_raw_image_without_layout(self):
        raw, image = self.compose()
        self.assertIn("layout", self.stored()["compose"])
        got = self.ok("DELETE", self.url())
        self.assertEqual((got["attempt"], got["files"], got["chosen"]), (1, 1, False))
        item = self.stored()
        self.assertNotIn("compose", item)
        self.assertNotIn("composeError", item)
        self.assertEqual(item["image"], item["raw"])
        self.assertEqual(item["image"], got["image"])
        self.assertTrue(raw.is_file())
        self.assertFalse(image.is_file())
        self.assertNotIn("layout", json.dumps(self.stored()))
        self.assertEqual(self.stored(2).get("compose"), None)  # the other attempt is untouched

    def test_an_attempt_without_composition_gives_order_compose_none(self):
        self.bad("DELETE", self.url(), None, 409, "order.compose_none")
        self.assertIn("has no composition to delete",
                      self.cli_fails("--lang", "en", "compose", "rm", NAME, self.key, self.profile, "1", "--yes"))

    def test_a_missing_raw_image_gives_order_compose_no_raw_and_changes_nothing(self):
        raw, image = self.compose()
        raw.unlink()
        self.bad("DELETE", self.url(), None, 409, "order.compose_no_raw")
        self.assertIn("compose", self.stored())
        self.assertTrue(image.is_file())

    def test_a_composition_in_progress_is_409_and_nothing_is_deleted(self):
        raw, image = self.compose()
        with fsutil.try_lock(orders.compose_lock_path(NAME, self.key, self.profile, 1)) as taken:
            self.assertTrue(taken)
            self.bad("DELETE", self.url(), None, 409, "order.delete_busy")
            self.assertIn("queued, being generated or being composed", self.cli_fails(
                "--lang", "en", "compose", "rm", NAME, self.key, self.profile, "1", "--yes"))
        self.assertIn("compose", self.stored())
        self.assertTrue(image.is_file())

    def test_unknown_attempt_and_order_and_bad_id(self):
        self.bad("DELETE", self.url(99), None, 404, "order.attempt_unknown")
        self.bad("DELETE", self.url(key="fauna/nada"), None, 404, "order.unknown")
        self.bad("DELETE", self.url().replace("/1/", "/x/"), None, 400, "api.bad_param")

    def test_the_chosen_one_says_so_and_its_delivery_is_not_touched(self):
        self.compose()
        self.ok("POST", self.order_url(self.key, self.profile, "/choose"), {"attempt": 1})
        before = {k: v for k, v in orders.get(NAME, self.key, self.profile).items() if k not in ("attempts", "updatedAt")}
        got = self.ok("DELETE", self.url())
        self.assertTrue(got["chosen"])
        after = {k: v for k, v in orders.get(NAME, self.key, self.profile).items() if k not in ("attempts", "updatedAt")}
        self.assertEqual(after, before)  # chosen, history and the rest of the order stay as they were
        self.assertEqual(after["chosen"], 1)

    def test_api_equals_cli_and_the_log_gets_a_line(self):
        self.compose()
        other, _ = self.make_order(key="fauna/otro")
        self.compose(key=other)
        via_api = self.ok("DELETE", self.url())
        via_cli = self.cli_json("compose", "rm", NAME, other, self.profile, "1", "--yes")
        self.assertEqual(dict(via_api, image=0), dict(via_cli, image=0))
        self.assertTrue(via_api["image"].endswith(".raw.png") and via_cli["image"].endswith(".raw.png"))
        lines = [json.loads(x) for x in log.log_path(NAME).read_text().splitlines()]
        lines = [r for r in lines if r["gen_ai.operation.name"] == log.OP_COMPOSE_DELETE]
        self.assertEqual([r["app.image.key"] for r in lines], [self.key, other])
        self.assertEqual((lines[0]["app.image.template"], lines[0]["app.attempt.id"]), ("default", 1))
        self.assertNotIn("gen_ai.provider.name", lines[0])

    def test_cli_without_yes_and_without_a_terminal_fails_with_its_reason(self):
        _raw, image = self.compose()
        err = self.cli_fails("--lang", "en", "compose", "rm", NAME, self.key, self.profile, "1",
                             stdin=io.StringIO("y\n"))
        self.assertIn("no terminal to ask", err)
        self.assertTrue(image.is_file())
        self.assertIn("compose", self.stored())

    def test_cli_asks_on_a_terminal_and_the_prompt_warns_when_chosen(self):
        _raw, image = self.compose()
        self.ok("POST", self.order_url(self.key, self.profile, "/choose"), {"attempt": 1})
        err = self.cli_fails("--lang", "en", "compose", "rm", NAME, self.key, self.profile, "1", stdin=Tty("n\n"))
        self.assertIn("nothing was deleted", err)
        self.assertTrue(image.is_file())
        with mock.patch.object(sys, "stdin", Tty("y\n")):
            out = self.cli("--lang", "en", "compose", "rm", NAME, self.key, self.profile, "1")
        self.assertIn("Composition of attempt 1 deleted", out)
        self.assertIn("does not change until it is delivered again", out)
        self.assertFalse(image.is_file())

    def test_through_main_compose_rm_deletes_and_only_when_compose_is_the_command(self):
        from gimg import cli
        raw, image = self.compose()
        self.assertIn("Composition of attempt 1 deleted", self.cli(
            "--lang", "en", "compose", "rm", NAME, self.key, self.profile, "1", "--yes"))
        self.assertFalse(image.is_file())
        for argv, want in ((["--lang", "en", "compose", "rm", "x"], ["--lang", "en", "compose-rm", "x"]),
                           (["compose", "--", "rm", "k", "p"], None), (["order", "compose", "rm"], None),
                           (["--json", "--lang", "rm", "compose", "rm"], ["--json", "--lang", "rm", "compose-rm"])):
            got = list(argv)
            cli._rewrite_compose_rm(got)
            self.assertEqual(got, want or argv)

    def test_a_project_named_rm_is_composed_with_the_double_dash_and_compose_rm_is_not_in_help(self):
        from gimg import cli
        args = cli._build("en").parse_args(["compose", "--", "rm", "k", "p"])
        self.assertEqual((args.cmd, args.project, args.key, args.profile), ("compose", "rm", "k", "p"))
        out = io.StringIO()
        import contextlib
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            cli._build("en").parse_args(["--help"])
        self.assertNotIn("compose-rm", out.getvalue())

    def test_compose_itself_still_parses_and_a_project_is_not_confused_with_rm(self):
        from gimg import cli
        parser = cli._build("en")
        args = parser.parse_args(["compose", NAME, self.key, self.profile])
        self.assertEqual((args.cmd, args.project), ("compose", NAME))


if __name__ == "__main__":
    unittest.main()
