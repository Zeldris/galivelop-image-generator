import contextlib
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import __version__, cli, i18n

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())
ORDER = json.loads((ROOT / "examples" / "order.json").read_text())


class CliBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data"),
            "GIMG_ENGINE": "fake", "GIMG_LANG": "en"})
        env.start()
        self.addCleanup(env.stop)
        for name in ("GIMG_MACHINE_PROFILE", "GIMG_DEBUG", "GIMG_FAKE_FAIL", "GIMG_FAKE_DELAY"):
            os.environ.pop(name, None)
        self.root = self.tmp / "proj"
        (self.root / "refs").mkdir(parents=True)
        (self.root / "refs" / "wolf.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        self.order_file = self.tmp / "order.json"
        self.write_order(count=2)

    def write_order(self, **extra):
        self.order_file.write_text(json.dumps(dict(ORDER, **extra)))

    def run_cli(self, *argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if stdin is None:
                code = cli.main(list(argv))
            else:
                with mock.patch.object(sys, "stdin", io.StringIO(stdin)):
                    code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def ok(self, *argv, **kw):
        code, out, err = self.run_cli(*argv, **kw)
        self.assertEqual((code, err), (0, ""), argv)
        return out

    def js(self, *argv, **kw):
        return json.loads(self.ok("--json", *argv, **kw))

    def project_files(self) -> set:
        return {p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if not p.is_dir()}

    def fails(self, *argv, message, lang="en", **kw):
        code, out, err = self.run_cli("--lang", lang, *argv, **kw)
        self.assertEqual((code, out), (1, ""), argv)
        self.assertIn(message, err)
        return err


class FullCycleTests(CliBase):
    def test_end_to_end(self):
        name = "example-world"
        key, prof = ORDER["key"], ORDER["profile"]
        self.assertIn(name, self.ok("project", "add", str(self.root)))
        self.assertEqual(self.js("project", "list"), [{"name": name, "root": str(self.root)}])

        queued = self.js("order", "submit", name, str(self.order_file))
        self.assertEqual([e["id"] for e in queued["entries"]], [1, 2])
        self.assertEqual([e["seed"] for e in queued["entries"]], [42, 43])
        self.assertIsNone(queued["estimateMs"])
        entries = self.js("queue", "list")
        self.assertEqual([e["state"] for e in entries], ["queued", "queued"])
        self.assertIn("#1 queued", self.ok("queue", "list"))

        self.assertEqual(self.js("work"), {"processed": 2})
        self.assertIn("Processed 0 entries", self.ok("work"))
        order = self.js("order", "show", name, key, prof)
        self.assertEqual([a["id"] for a in order["attempts"]], [1, 2])
        data = Path(os.environ["GIMG_DATA_HOME"]) / "projects" / name / "orders"
        for attempt in order["attempts"]:
            self.assertEqual(len(list(data.rglob(os.path.basename(attempt["image"])))), 1)
        listing = self.ok("order", "list", name)
        self.assertIn("fauna/red-howler @banner", listing)
        self.assertEqual(len(self.js("order", "list", name, "--unchosen")), 1)
        self.assertEqual(self.js("order", "list", name, "--chosen"), [])

        base = (name, key, prof)
        self.assertEqual(self.js("attempt", "mark", *base, "1", "candidate")["state"], "candidate")
        self.assertEqual(self.js("attempt", "mark", *base, "2", "discarded")["state"], "discarded")
        self.assertEqual(self.js("attempt", "note", *base, "1", "good wings")["note"], "good wings")
        self.assertIn("note: good wings", self.ok("order", "show", *base))
        self.fails("choose", *base, "2", message="attempt 2 is discarded")

        self.assertEqual(self.js("choose", *base, "1"), {"old": None, "new": 1})
        delivered = self.root / "uploads/images/fauna/red-howler-banner.png"
        manifest = self.root / "galivelop-images.manifest.json"
        first = delivered.read_bytes()
        self.assertEqual(first[:8], b"\x89PNG\r\n\x1a\n")
        entry = json.loads(manifest.read_text())["images"][key][prof]
        self.assertEqual((entry["attemptId"], entry["seed"]), (1, 42))
        # the project only gains the delivered image and the manifest: no locks, temporaries or data
        own = {"galivelop-images.json", "refs/wolf.png"}
        self.assertEqual(self.project_files(), own | {
            "uploads/images/fauna/red-howler-banner.png", "galivelop-images.manifest.json"})

        self.assertEqual(self.js("attempt", "mark", *base, "2", "new")["state"], "new")
        new = self.js("attempt", "new", *base, "--seed", "999", "--steps", "4", "--cfg", "1.5")
        self.assertEqual([(e["id"], e["seed"], e["params"]["steps"], e["params"]["cfg"])
                          for e in new["entries"]], [(3, 999, 4, 1.5)])
        self.assertTrue(new["entries"][0]["prompt"].startswith(ORDER["prompt"]))
        self.assertEqual(self.js("work", "--once"), {"processed": 1})
        order = self.js("order", "show", *base)
        self.assertEqual([(a["id"], a["seed"]) for a in order["attempts"]][-1], (3, 999))
        self.assertEqual(self.js("choose", *base, "3"), {"old": 1, "new": 3})
        self.assertNotEqual(delivered.read_bytes(), first)
        self.assertEqual(self.js("undo", *base), {"old": 3, "new": 1})
        self.assertEqual(delivered.read_bytes(), first)
        self.assertEqual(self.js("undo", *base), {"old": 1, "new": None})
        self.assertFalse(delivered.exists())
        self.assertNotIn(key, json.loads(manifest.read_text())["images"])
        self.assertEqual(self.project_files(), own | {"galivelop-images.manifest.json"})
        self.fails("undo", *base, message="nothing to undo")

        again = self.js("attempt", "new", *base)
        self.assertEqual(len(again["entries"]), 1)
        random_seed = again["entries"][0]["seed"]
        self.assertTrue(0 <= random_seed < 2 ** 32)
        cancelled = self.js("queue", "cancel", str(again["entries"][0]["id"]))
        self.assertEqual(cancelled["state"], "cancelled")
        self.fails("queue", "cancel", str(again["entries"][0]["id"]), message="cannot be cancelled")
        extra = self.js("attempt", "new", *base)["entries"][0]["id"]
        self.assertIn("cancelled", self.ok("queue", "cancel", str(extra)))

        self.assertIn(name, self.ok("project", "remove", name))
        self.assertEqual(self.js("project", "list"), [])

    def test_languages_differ_and_json_parses(self):
        es = self.ok("--lang", "es", "project", "list")
        en = self.ok("--lang", "en", "project", "list")
        self.assertNotEqual(es, en)
        self.assertIn("No hay proyectos", es)
        self.assertEqual(self.js("project", "list"), [])
        self.assertIn("registrar", self.help_text("es", "project"))
        self.assertNotEqual(self.help_text("es", "work"), self.help_text("en", "work"))

    def help_text(self, lang, cmd):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["--lang", lang, cmd, "--help"]), 0)
        return out.getvalue()

    def test_estimate_after_work(self):
        self.ok("project", "add", str(self.root))
        self.ok("order", "submit", "example-world", str(self.order_file))
        self.ok("work")
        out = self.js("order", "submit", "example-world", str(self.order_file))
        self.assertIsInstance(out["estimateMs"], (int, float))
        self.assertRegex(self.ok("attempt", "new", "example-world", ORDER["key"], ORDER["profile"]),
                         r"Estimate per attempt: [\d.]+ s")

    def test_submit_from_stdin(self):
        self.ok("project", "add", str(self.root))
        out = self.js("order", "submit", "example-world", "-", stdin=json.dumps(dict(ORDER, count=1)))
        self.assertEqual(len(out["entries"]), 1)
        self.assertIn("No estimate yet", self.ok("order", "submit", "example-world", "-",
                                                 stdin=json.dumps(dict(ORDER, count=2))))

    def test_failed_entry_shows_translated_error(self):
        self.ok("project", "add", str(self.root))
        self.ok("order", "submit", "example-world", str(self.order_file))
        with mock.patch.dict(os.environ, {"GIMG_FAKE_FAIL": "boom"}):
            self.ok("work")
        text = self.ok("queue", "list")
        self.assertIn("failed", text)
        self.assertIn("boom", text)
        failed = self.js("queue", "list", "--state", "failed")
        self.assertIn("boom", failed[0]["errorText"])


class FailureTests(CliBase):
    def test_unknown_project(self):
        self.fails("order", "list", "nope", message='no registered project is named "nope"')
        self.fails("order", "list", "nope", message="ningún proyecto registrado llamado «nope»", lang="es")

    def test_invalid_order_file(self):
        self.ok("project", "add", str(self.root))
        bad = self.tmp / "bad.json"
        bad.write_text("{not json")
        self.fails("order", "submit", "example-world", str(bad), message="could not read the order")
        self.fails("order", "submit", "example-world", str(self.tmp / "missing.json"),
                  message="could not read the order")
        bad.write_text(json.dumps({"key": "x"}))
        self.fails("order", "submit", "example-world", str(bad), message="the order is not valid")
        self.fails("order", "submit", "example-world", str(bad), message="no es válido", lang="es")

    def test_worker_already_running(self):
        import fcntl
        from gimg import queue
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.fails("work", message="a worker is already running")

    def test_usage_error_exits_2(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(cli.main(["choose", "p", "k", "banner", "notanumber"]), 2)
            self.assertEqual(cli.main([]), 2)
        self.assertIn("invalid int value", err.getvalue())

    def test_unexpected_error_is_short_unless_debug(self):
        with mock.patch("gimg.cli.projects.list_projects", side_effect=RuntimeError("kaput")):
            code, _out, err = self.run_cli("project", "list")
            self.assertEqual((code, err), (1, "unexpected error: RuntimeError: kaput\n"))
            with mock.patch.dict(os.environ, {"GIMG_DEBUG": "1"}):
                code, _out, err = self.run_cli("project", "list")
        self.assertIn("Traceback", err)
        self.assertIn("unexpected error", err)


class ProcessTests(unittest.TestCase):
    def test_python_m_gimg_version(self):
        done = subprocess.run([sys.executable, "-m", "gimg", "version"], cwd=ROOT,
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout.strip(), done.stderr), (0, __version__, ""))


class LocaleCoverageTests(unittest.TestCase):
    def test_every_cli_key_exists_in_both_languages(self):
        source = (ROOT / "gimg" / "cli.py").read_text()
        import re
        keys = set(re.findall(r'"(cli\.[a-z_.]+)"', source))
        self.assertTrue(keys)
        for lang in ("es", "en"):
            texts = json.loads((ROOT / "gimg" / "locales" / (lang + ".json")).read_text(encoding="utf-8"))
            for key in keys:
                self.assertTrue(key in texts or "error." + key in texts, (lang, key))


class BadEngineTests(CliBase):
    def test_bad_engine_fails_before_queueing(self):
        self.ok("project", "add", str(self.root))
        with mock.patch.dict(os.environ, {"GIMG_ENGINE": "nope"}):
            self.fails("order", "submit", "example-world", str(self.order_file), message="nope")
            self.fails("attempt", "new", "example-world", ORDER["key"], ORDER["profile"], message="nope")
        self.assertEqual(self.js("queue", "list"), [])  # nothing queued, so a retry cannot duplicate

    def test_work_passes_the_language(self):
        with mock.patch("gimg.worker.run", return_value=0) as run:
            self.ok("--lang", "es", "work", "--once")
        self.assertEqual(run.call_args.kwargs["lang"], "es")
