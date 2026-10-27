import copy
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import limits, models, paths, projects, schema
from gimg.errors import GimgError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())
SHA = "a" * 64


def file_entry(name):
    return {"name": name, "url": "https://example.org/" + name, "sha256": SHA, "sizeMb": 10}


def small_catalog():
    return {"models": {"m-one": {
        "license": "MIT",
        "files": {"diffusion": file_entry("d.gguf"), "text": file_entry("t.gguf"), "vae": file_entry("v.safetensors")},
        "defaults": {"steps": 4, "cfg": 1.5, "sampler": "euler"},
        "args": ["--a", "1"]}}}


def errs(instance):
    return sorted((e.path, e.code) for e in schema.validate(instance, schema.load_schema("models")))


class CatalogSchemaTests(unittest.TestCase):
    def test_schema_is_valid_and_catalog_passes(self):
        schema.check_schema(schema.load_schema("models"))
        self.assertEqual(errs(small_catalog()), [])
        self.assertEqual(errs(json.loads(models.CATALOG.read_text())), [])

    def test_catalog_schema_reference_points_to_the_schema(self):
        ref = json.loads(models.CATALOG.read_text())["$schema"]
        self.assertTrue((models.CATALOG.parent / ref).is_file(), ref)

    def test_file_missing_from_a_model(self):
        cat = small_catalog()
        del cat["models"]["m-one"]["files"]["vae"]
        self.assertEqual(errs(cat), [("/models/m-one/files", "required")])

    def test_extra_file_kind_rejected(self):
        cat = small_catalog()
        cat["models"]["m-one"]["files"]["lora"] = file_entry("l.gguf")
        self.assertEqual(errs(cat), [("/models/m-one/files/lora", "additionalProperties")])

    def test_uppercase_or_odd_id_rejected(self):
        for bad in ("Flux2", "a_b", "-a", "a b", ""):
            cat = small_catalog()
            cat["models"][bad] = cat["models"].pop("m-one")
            codes = [c for _, c in errs(cat)]
            self.assertIn("propertyNames", codes, repr(bad))

    def test_empty_catalog_rejected(self):
        self.assertEqual(errs({"models": {}}), [("/models", "minProperties")])

    def test_bad_file_fields(self):
        for field, value, code in (
                ("sha256", "A" * 64, "pattern"), ("sha256", "a" * 63, "pattern"),
                ("sha256", "a" * 64 + "\n", "pattern"),
                ("url", "http://example.org/x", "pattern"), ("url", "https://a b", "pattern"),
                ("name", "a/b.gguf", "pattern"), ("name", "../x", "pattern"), ("name", ".hidden", "pattern"),
                ("sizeMb", 0, "minimum"), ("sizeMb", 1.5, "type"), ("sizeMb", "10", "type")):
            cat = small_catalog()
            cat["models"]["m-one"]["files"]["vae"][field] = value
            self.assertEqual(errs(cat), [("/models/m-one/files/vae/" + field, code)], (field, value))

    def test_missing_defaults_and_bad_args(self):
        cat = small_catalog()
        del cat["models"]["m-one"]["defaults"]["cfg"]
        cat["models"]["m-one"]["args"] = ["--a", 1]
        self.assertEqual(errs(cat), [("/models/m-one/args/1", "type"),
                                     ("/models/m-one/defaults", "required")])

    def test_empty_license_rejected(self):
        cat = small_catalog()
        cat["models"]["m-one"]["license"] = ""
        self.assertEqual(errs(cat), [("/models/m-one/license", "minLength")])


class RealCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = models.load_catalog()

    def test_ids_and_licenses(self):
        self.assertEqual(models.ids(self.catalog), ["flux2-klein-4b-q8", "flux3-klein-q8"])
        self.assertEqual(self.catalog["models"]["flux2-klein-4b-q8"]["license"], "Apache-2.0")
        self.assertEqual(self.catalog["models"]["flux3-klein-q8"]["license"], "unconfirmed")

    def test_files(self):
        expect = {
            "flux2-klein-4b-q8": ("flux-2-klein-4b-Q8_0.gguf", "Qwen3-4B-Q4_K_M.gguf",
                                  "full_encoder_small_decoder.safetensors"),
            "flux3-klein-q8": ("flux3-image-klein-Q8_0.gguf", "Qwen3VL-4B-Instruct-Q4_K_M.gguf",
                               "flux2-vae.safetensors")}
        for model_id, names in expect.items():
            files = self.catalog["models"][model_id]["files"]
            self.assertEqual(tuple(files[k]["name"] for k in models.KINDS), names)
        for model_id, model in self.catalog["models"].items():
            for kind, entry in model["files"].items():
                self.assertRegex(entry["sha256"], r"[0-9a-f]{64}", (model_id, kind))
                self.assertTrue(entry["url"].startswith("https://huggingface.co/"), (model_id, kind))
                self.assertGreater(entry["sizeMb"], 100, (model_id, kind))

    def test_same_file_has_the_same_hash_in_both_models(self):
        by_name = {}
        for model in self.catalog["models"].values():
            for entry in model["files"].values():
                self.assertEqual(by_name.setdefault(entry["name"], entry["sha256"]), entry["sha256"])

    def test_defaults_and_args(self):
        flux2 = self.catalog["models"]["flux2-klein-4b-q8"]
        flux3 = self.catalog["models"]["flux3-klein-q8"]
        self.assertEqual(flux2["defaults"], {"steps": 6, "cfg": 1, "sampler": "euler"})
        self.assertEqual(flux3["defaults"], {"steps": 16, "cfg": 1, "sampler": "euler"})
        for model in (flux2, flux3):
            self.assertEqual(model["args"], ["--flash-attn", "off,diffusion=on", "--vae-tiling"])


class LoadCatalogTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def write(self, text):
        path = self.tmp / "models.json"
        path.write_text(text)
        return path

    def test_invalid_catalog_reports_the_schema_errors(self):
        cat = small_catalog()
        del cat["models"]["m-one"]["files"]["vae"]
        with self.assertRaises(GimgError) as cm:
            models.load_catalog(self.write(json.dumps(cat)))
        self.assertEqual(cm.exception.code, "model.catalog_invalid")
        self.assertEqual([(e.path, e.code) for e in cm.exception.errors], [("/models/m-one/files", "required")])
        self.assertIn("vae", cm.exception.message("en"))

    def test_not_json_and_missing_file(self):
        for path in (self.write("{"), self.tmp / "nope.json"):
            with self.assertRaises(GimgError) as cm:
                models.load_catalog(path)
            self.assertEqual(cm.exception.code, "model.catalog_invalid")
            self.assertTrue(cm.exception.params["reason"])


class ModelsDirTests(unittest.TestCase):
    def env(self, **kw):
        base = {k: "" for k in ("GIMG_MODELS_HOME", "GIMG_DATA_HOME", "XDG_DATA_HOME")}
        base.update(kw)
        return mock.patch.dict(os.environ, base)

    def test_explicit_wins(self):
        with self.env(GIMG_MODELS_HOME="/sd/models", GIMG_DATA_HOME="/d"):
            self.assertEqual(paths.models_dir(), Path("/sd/models"))

    def test_default_is_inside_the_data_folder(self):
        with self.env(GIMG_DATA_HOME="/d"):
            self.assertEqual(paths.models_dir(), Path("/d/models"))
        with self.env(XDG_DATA_HOME="/x"):
            self.assertEqual(paths.models_dir(), Path("/x/gimg/models"))


class ResolveTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        env = mock.patch.dict(os.environ, {"GIMG_MODELS_HOME": str(self.tmp / "models")})
        env.start()
        self.addCleanup(env.stop)
        self.deck = limits.load_machine("steam-deck")

    def test_unknown_model_names_it_and_lists_the_known_ones(self):
        with self.assertRaises(GimgError) as cm:
            models.resolve("nope", self.deck)
        self.assertEqual(cm.exception.code, "model.unknown")
        self.assertEqual(cm.exception.params["model"], "nope")
        self.assertEqual(cm.exception.params["known"], "flux2-klein-4b-q8, flux3-klein-q8")
        self.assertIn("nope", cm.exception.message("es"))
        self.assertIn("flux3-klein-q8", cm.exception.message("en"))

    def test_ids_are_exact_no_case_folding_no_blank(self):
        for bad in ("FLUX2-KLEIN-4B-Q8", "Flux3-Klein-Q8", " flux3-klein-q8", "", None, 3):
            with self.assertRaises(GimgError) as cm:
                models.resolve(bad, self.deck)
            self.assertEqual(cm.exception.code, "model.unknown", repr(bad))

    def test_fast_model_on_the_deck_uses_general_limits(self):
        r = models.resolve("flux2-klein-4b-q8", self.deck)
        self.assertEqual(r["defaults"], {"steps": 6, "cfg": 1, "sampler": "euler"})
        self.assertEqual(r["args"], ["--flash-attn", "off,diffusion=on", "--vae-tiling"])
        self.assertEqual((r["timeoutS"], r["minFreeMemoryMb"]), (900, 7000))
        self.assertEqual(r["license"], "Apache-2.0")

    def test_quality_model_on_the_deck_is_overridden_and_args_keep_order(self):
        r = models.resolve("flux3-klein-q8", self.deck)
        self.assertEqual(r["args"], ["--flash-attn", "off,diffusion=on", "--vae-tiling",
                                     "--backend", "diffusion=cpu", "-t", "8"])
        self.assertEqual((r["timeoutS"], r["minFreeMemoryMb"]), (10800, 5000))
        self.assertEqual(r["defaults"]["steps"], 16)

    def test_partial_override_falls_back_for_the_rest(self):
        machine = {"timeoutS": 100, "minFreeMemoryMb": 200,
                   "engine": {"models": {"m-one": {"timeoutS": 5}}}}
        r = models.resolve("m-one", machine, small_catalog())
        self.assertEqual((r["timeoutS"], r["minFreeMemoryMb"], r["args"]), (5, 200, ["--a", "1"]))

    def test_override_of_zero_free_memory_is_kept(self):
        machine = {"timeoutS": 100, "minFreeMemoryMb": 200,
                   "engine": {"models": {"m-one": {"minFreeMemoryMb": 0}}}}
        self.assertEqual(models.resolve("m-one", machine, small_catalog())["minFreeMemoryMb"], 0)

    def test_machine_without_engine_section(self):
        machine = {"timeoutS": 100, "minFreeMemoryMb": 200}
        r = models.resolve("m-one", machine, small_catalog())
        self.assertEqual((r["timeoutS"], r["minFreeMemoryMb"], r["args"]), (100, 200, ["--a", "1"]))

    def test_machine_naming_a_model_outside_the_catalog_is_ignored(self):
        machine = {"timeoutS": 100, "minFreeMemoryMb": 200,
                   "engine": {"models": {"ghost": {"args": ["--x"], "timeoutS": 1}}}}
        r = models.resolve("m-one", machine, small_catalog())
        self.assertEqual((r["timeoutS"], r["args"]), (100, ["--a", "1"]))
        with self.assertRaises(GimgError) as cm:  # and asking for it is still an error
            models.resolve("ghost", machine, small_catalog())
        self.assertEqual(cm.exception.code, "model.unknown")

    def test_resolution_does_not_change_catalog_or_machine(self):
        cat, machine = small_catalog(), copy.deepcopy(self.deck)
        r = models.resolve("m-one", machine, cat)
        r["args"].append("--zzz")
        r["defaults"]["steps"] = 99
        self.assertEqual(cat, small_catalog())
        self.assertEqual(machine, self.deck)

    def test_file_paths_follow_models_dir(self):
        r = models.resolve("flux3-klein-q8", self.deck)
        root = self.tmp / "models"
        self.assertEqual(r["files"]["diffusion"]["path"], root / "diffusion" / "flux3-image-klein-Q8_0.gguf")
        self.assertEqual(r["files"]["text"]["path"], root / "text" / "Qwen3VL-4B-Instruct-Q4_K_M.gguf")
        self.assertEqual(r["files"]["vae"]["path"], root / "vae" / "flux2-vae.safetensors")
        self.assertEqual(r["files"]["vae"]["sizeMb"], 336)

    def test_missing_files(self):
        r = models.resolve("m-one", self.deck, small_catalog())
        self.assertEqual(models.missing_files(r), ["diffusion", "text", "vae"])
        for kind in ("diffusion", "vae"):
            path = r["files"][kind]["path"]
            path.parent.mkdir(parents=True)
            path.write_bytes(b"x")
        self.assertEqual(models.missing_files(r), ["text"])
        r["files"]["text"]["path"].mkdir(parents=True)  # a folder is not the file
        self.assertEqual(models.missing_files(r), ["text"])


class MachineProfileTests(unittest.TestCase):
    def test_steam_deck_matches_the_contract(self):
        deck = json.loads((ROOT / "gimg" / "machine_profiles" / "steam-deck.json").read_text())
        self.assertEqual(deck["engine"], {
            "maxVram": "vulkan0=2", "paramsBackend": "disk", "ollama": "abort",
            "models": {"flux3-klein-q8": {"args": ["--backend", "diffusion=cpu", "-t", "8"],
                                          "timeoutS": 10800, "minFreeMemoryMb": 5000}}})

    def test_engine_schema(self):
        sch = schema.load_schema("machine-profile")
        base = {"name": "x", "minFreeMemoryMb": 1, "maxReferences": 1, "timeoutS": 1}

        def check(engine):
            return sorted((e.path, e.code) for e in schema.validate(dict(base, engine=engine), sch))

        self.assertEqual(check({"sdCli": "/bin/sd-cli", "ollama": "unload", "threads": 4,
                                "models": {"a-b": {"args": ["-t", "8"], "timeoutS": 5, "minFreeMemoryMb": 0}}}), [])
        self.assertEqual(check({"ollama": "kill", "threads": 0, "sdCli": ""}),
                         [("/engine/ollama", "enum"), ("/engine/sdCli", "minLength"),
                          ("/engine/threads", "minimum")])
        self.assertEqual(check({"models": {"A": {}}}), [("/engine/models/A", "propertyNames")])
        self.assertEqual(check({"models": {"a": {"extra": 1}}}),
                         [("/engine/models/a/extra", "additionalProperties")])
        self.assertEqual(check({"models": {"a": {"args": "-t", "timeoutS": 0, "minFreeMemoryMb": -1}}}),
                         [("/engine/models/a/args", "type"), ("/engine/models/a/minFreeMemoryMb", "minimum"),
                          ("/engine/models/a/timeoutS", "minimum")])


class ProjectModelTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def load(self, model, **extra):
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        if model is None:
            del cfg["profiles"]["banner"]["model"]
        else:
            cfg["profiles"]["banner"]["model"] = model
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        return projects.load_config(self.root)

    def test_catalog_ids_load(self):
        for model_id in models.ids():
            self.assertEqual(self.load(model_id)["profiles"]["banner"]["model"], model_id)

    def test_profile_without_model_loads(self):
        self.assertNotIn("model", self.load(None)["profiles"]["banner"])

    def test_unknown_model_fails_with_model_unknown(self):
        for bad in ("flux9", "FLUX2-KLEIN-4B-Q8"):
            with self.assertRaises(GimgError) as cm:
                self.load(bad)
            self.assertEqual(cm.exception.code, "model.unknown")
            self.assertEqual(cm.exception.params["model"], bad)

    def test_example_models_are_in_the_catalog(self):
        known = models.ids()
        for profile in EXAMPLE["profiles"].values():
            if "model" in profile:
                self.assertIn(profile["model"], known)


if __name__ == "__main__":
    unittest.main()
