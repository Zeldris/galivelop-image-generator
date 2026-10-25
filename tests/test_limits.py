import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import limits
from gimg.errors import GimgError

STEAM = {"name": "steam-deck", "minFreeMemoryMb": 1, "maxReferences": 1, "timeoutS": 9,
         "maxSteps": 50, "maxPixels": 1048576}
MIN = {"name": "tiny", "minFreeMemoryMb": 1, "maxReferences": 0, "timeoutS": 9}


class LoadTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        env = mock.patch.dict(os.environ, {"GIMG_CONFIG_HOME": str(self.tmp / "cfg"),
                                           "GIMG_DATA_HOME": str(self.tmp / "data")})
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("GIMG_MACHINE_PROFILE", None)

    def code(self, *args):
        with self.assertRaises(GimgError) as cm:
            limits.load_machine(*args)
        return cm.exception.code

    def test_corrupt_config_json_is_translated(self):
        (self.tmp / "cfg").mkdir()
        (self.tmp / "cfg" / "config.json").write_text("{nope")
        with self.assertRaises(GimgError) as cm:
            limits.load_machine()
        self.assertEqual(cm.exception.code, "machine.config_unreadable")
        self.assertIn(str(self.tmp / "cfg" / "config.json"), cm.exception.message("en"))

    def test_tilde_unresolvable(self):
        with mock.patch.dict(os.environ, {"HOME": ""}), mock.patch(
                "pathlib.Path.expanduser", side_effect=RuntimeError("no home")):
            self.assertEqual(self.code("~nobody/x.json"), "machine.unreadable")

    def test_tilde_expanded(self):
        self.write(self.tmp / "home" / "m.json", MIN)
        with mock.patch.dict(os.environ, {"HOME": str(self.tmp / "home")}):
            self.assertEqual(limits.load_machine("~/m.json")["name"], "tiny")

    def test_control_chars_in_path(self):
        for bad in ("a\x00/b.json", "a\n/b.json", "a/\x1bb.json"):
            self.assertEqual(self.code(bad), "machine.bad_path")

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return str(path)

    def test_default_is_steam_deck(self):
        self.assertEqual(limits.load_machine()["name"], "steam-deck")

    def test_env_preset_beats_config(self):
        self.write(self.tmp / "cfg" / "config.json", {"machineProfile": "nope"})
        with mock.patch.dict(os.environ, {"GIMG_MACHINE_PROFILE": "steam-deck"}):
            self.assertEqual(limits.load_machine()["name"], "steam-deck")

    def test_env_path(self):
        p = self.write(self.tmp / "m.json", MIN)
        with mock.patch.dict(os.environ, {"GIMG_MACHINE_PROFILE": p}):
            self.assertEqual(limits.load_machine()["name"], "tiny")

    def test_config_used_when_no_env(self):
        p = self.write(self.tmp / "m.json", MIN)
        self.write(self.tmp / "cfg" / "config.json", {"machineProfile": p})
        self.assertEqual(limits.load_machine()["name"], "tiny")

    def test_config_unknown_preset(self):
        self.write(self.tmp / "cfg" / "config.json", {"machineProfile": "nope"})
        self.assertEqual(self.code(), "machine.missing")

    def test_bad_names(self):
        for bad in ("UPPER", "-x", "a b", "x\n"):
            self.assertEqual(self.code(bad), "machine.bad_name", bad)

    def test_path_forms_are_files_not_presets(self):
        self.assertEqual(self.code("../x"), "machine.missing")
        self.assertEqual(self.code("a/b"), "machine.missing")

    def test_invalid_json(self):
        p = self.write(self.tmp / "m.json", "{nope")
        self.assertEqual(self.code(p), "machine.unreadable")

    def test_invalid_schema(self):
        p = self.write(self.tmp / "m.json", {"name": "x"})
        self.assertEqual(self.code(p), "machine.invalid")

    def test_non_string_config_value(self):
        self.write(self.tmp / "cfg" / "config.json", {"machineProfile": 3})
        self.assertEqual(self.code(), "machine.bad_name")

    def test_messages_translated(self):
        for lang in ("es", "en"):
            try:
                limits.load_machine("nope")
            except GimgError as exc:
                self.assertNotIn("error.", exc.message(lang))


class CheckTests(unittest.TestCase):
    def spec(self, refs=0, **params):
        return {"seed": 1, "prompt": "p", "params": params, "references": ["r"] * refs}

    def code(self, spec, machine=STEAM):
        with self.assertRaises(limits.LimitError) as cm:
            limits.check(spec, machine)
        self.assertIsInstance(cm.exception, GimgError)
        return cm.exception.code

    def test_references(self):
        limits.check(self.spec(1), STEAM)
        self.assertEqual(self.code(self.spec(2)), "limit.references")
        self.assertEqual(self.code(self.spec(1), MIN), "limit.references")
        limits.check(self.spec(5), {k: v for k, v in STEAM.items() if k != "maxReferences"})

    def test_steps(self):
        limits.check(self.spec(steps=50), STEAM)
        self.assertEqual(self.code(self.spec(steps=51)), "limit.steps")
        limits.check(self.spec(), STEAM)  # absent in spec
        limits.check(self.spec(steps=999), MIN)  # absent in machine

    def test_pixels(self):
        limits.check(self.spec(width=1024, height=1024), STEAM)
        self.assertEqual(self.code(self.spec(width=1025, height=1024)), "limit.pixels")
        limits.check(self.spec(width=99999), STEAM)  # height absent
        limits.check(self.spec(), STEAM)
        limits.check(self.spec(width=9999, height=9999), MIN)

    def test_messages(self):
        for lang in ("es", "en"):
            with self.assertRaises(limits.LimitError) as cm:
                limits.check(self.spec(width=2000, height=2000), STEAM)
            self.assertNotIn("error.", cm.exception.message(lang))
