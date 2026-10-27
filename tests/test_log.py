import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import engine, log
from gimg.errors import GimgError

SPEC = {"seed": 5, "prompt": "p", "references": ["a"],
        "params": {"width": 64, "height": 32, "steps": 4, "cfg": 1.5, "sampler": "euler", "model": "m"}}
MACHINE = {"name": "steam-deck"}


def line(duration, task="banner", steps=4, refs=0, provider="fake", **extra):
    d = {"gen_ai.provider.name": provider, "app.task": task, "app.image.steps": steps,
         "app.image.references": refs, "app.duration_ms": duration}
    d.update(extra)
    return d


class LogTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {"GIMG_CONFIG_HOME": str(self.tmp / "c"),
                                           "GIMG_DATA_HOME": str(self.tmp / "d")})
        env.start()
        self.addCleanup(env.stop)

    def put(self, *records):
        for r in records:
            log.append("proj", r)

    def test_record_success(self):
        res = engine.EngineResult(duration_ms=120, engine_version="fake-1", load_ms=0, sample_ms=100, decode_ms=20)
        rec = log.record_for("a/b", "banner", SPEC, MACHINE, "fake", result=res, ts="2026-01-01T00:00:00Z")
        self.assertEqual(rec, {
            "ts": "2026-01-01T00:00:00Z", "gen_ai.operation.name": "image_generation",
            "gen_ai.provider.name": "fake", "gen_ai.request.model": "m", "app.task": "banner",
            "app.machine_profile": "steam-deck", "app.duration_ms": 120, "app.load_ms": 0,
            "app.image.key": "a/b", "app.image.steps": 4, "app.image.cfg": 1.5,
            "app.image.sampler": "euler", "app.image.width": 64, "app.image.height": 32,
            "app.image.seed": 5, "app.image.references": 1, "app.image.engine_version": "fake-1",
            "app.image.sample_ms": 100, "app.image.decode_ms": 20, "app.image.draft": False})

    def test_record_error_and_no_nulls(self):
        spec = {"seed": 0, "prompt": "p", "params": {}}
        rec = log.record_for("k", "t", spec, MACHINE, "fake", error="boom")
        self.assertEqual(rec["app.error"], "boom")
        self.assertNotIn("app.duration_ms", rec)
        self.assertEqual(rec["app.image.seed"], 0)  # zero is kept
        self.assertEqual(rec["app.image.references"], 0)
        self.assertNotIn(None, rec.values())
        self.assertRegex(rec["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_a_composition_line_is_not_a_generation_and_the_estimate_ignores_it(self):
        rec = log.record_for("k", "banner", SPEC, MACHINE, None, operation=log.OP_COMPOSITION, compose="t.svg")
        self.assertEqual((rec["gen_ai.operation.name"], rec["app.image.compose"]), ("image_composition", "t.svg"))
        self.assertNotIn("gen_ai.provider.name", rec)
        self.put(dict(rec, **{"app.duration_ms": 1}))  # even with a duration it has no provider: not counted
        self.assertIsNone(log.estimate("proj", "fake", "banner", 4, True))
        self.assertEqual(log.record_for("k", "t", SPEC, MACHINE, "fake")["gen_ai.operation.name"], "image_generation")

    def test_append_writes_jsonl(self):
        self.put({"a": 1}, {"b": "é"})
        path = self.tmp / "d" / "projects" / "proj" / "log.jsonl"
        self.assertEqual([json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()],
                         [{"a": 1}, {"b": "é"}])

    def test_bad_project(self):
        for bad in ("../x", "a/b", "", "/etc"):
            with self.assertRaises(GimgError) as cm:
                log.append(bad, {})
            self.assertIn(cm.exception.code, ("log.bad_project", "path.dotdot"))

    def test_bad_project_names(self):
        for bad in (".", "..", "A", "-x", "a\n", "a b"):
            with self.assertRaises(GimgError) as cm:
                log.log_path(bad)
            self.assertEqual(cm.exception.code, "log.bad_project", bad)

    def test_estimate_none(self):
        self.assertIsNone(log.estimate("proj", "fake", "banner", 4, False))

    def test_estimate_median_odd_even(self):
        self.put(line(100), line(300), line(200))
        self.assertEqual(log.estimate("proj", "fake", "banner", 4, False), 200)
        self.put(line(1000))
        self.assertEqual(log.estimate("proj", "fake", "banner", 4, False), 250)

    def test_estimate_filters(self):
        self.put(line(100), line(900, task="other"), line(900, steps=8), line(900, provider="sd"),
                 line(900, refs=1), line(900, **{"app.error": "x"}))
        self.assertEqual(log.estimate("proj", "fake", "banner", 4, False), 100)
        self.assertEqual(log.estimate("proj", "fake", "banner", 4, True), 900)
        self.assertEqual(log.estimate("proj", "fake", "banner", 8, False), 900)
        self.assertIsNone(log.estimate("proj", "fake", "banner", 99, False))

    def test_estimate_skips_malformed(self):
        self.put(line(100))
        path = self.tmp / "d" / "projects" / "proj" / "log.jsonl"
        with open(path, "a") as fh:
            fh.write("{not json\n[1]\n\n" + json.dumps(line("x")) + "\n")
        self.put(line(300))
        self.assertEqual(log.estimate("proj", "fake", "banner", 4, False), 200)
