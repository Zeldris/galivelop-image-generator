"""`gimg doctor` (F2.5): each check green and red, with its reason, on fake folders (`GIMG_*_HOME`, `GIMG_SD_CLI`,
`GIMG_CATALOG`, a trimmed `PATH`). Nothing here starts a real `sd-cli`, reads the real Ollama or touches the real folders."""
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import cli, doctor, engine_sdcpp, i18n, limits, projects
from tests.test_engine_protections import FakeOllama, loaded
from tests.test_engine_sdcpp import dead_ollama_url

ROOT = Path(__file__).resolve().parent.parent
BODY = 2_000_000  # 2 MB: the size the small catalog declares (sizeMb 2, +-1 MB tolerated)


def body(kind, variant=""):
    return (kind + variant).encode().ljust(BODY, b".")


def small_catalog():
    def entry(kind, name):
        return {"name": name, "url": "https://example.org/" + name, "sizeMb": 2,
                "sha256": hashlib.sha256(body(kind)).hexdigest()}

    def model(default):
        suffix = "" if default else "2"  # the optional model has files of its own
        data = {"license": "MIT", "defaults": {"steps": 4, "cfg": 1, "sampler": "euler"}, "args": [],
                "files": {"diffusion": entry("diffusion", "d%s.gguf" % suffix), "text": entry("text", "t%s.gguf" % suffix),
                          "vae": entry("vae", "v%s.safetensors" % suffix)}}
        if default:
            data["installDefault"] = True
        return data

    return {"models": {"m-default": model(True), "m-optional": model(False)}}


def script(path, text):
    path.write_text("#!/bin/sh\n" + text + "\n", encoding="utf-8")
    path.chmod(0o755)


class DoctorBase(unittest.TestCase):
    """A machine where everything is installed and the engine is ``sdcpp``; each test breaks one thing."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.home = self.tmp / "home"
        self.bin = self.tmp / "bin"
        self.data, self.config = self.tmp / "data", self.tmp / "config"
        self.catalog_file = self.tmp / "catalog.json"
        self.meminfo = self.tmp / "meminfo"
        for d in (self.home / ".local" / "bin", self.bin, self.data, self.config):
            d.mkdir(parents=True)
        script(self.home / ".local" / "bin" / "gimg", "exit 0")
        script(self.bin / "ffmpeg", 'echo "ffmpeg version 9.9-test Copyright"')
        script(self.bin / "rsvg-convert", 'echo "rsvg-convert version 1.2.3"')
        self.set_meminfo(20_000_000)
        self.catalog_file.write_text(json.dumps(small_catalog()), encoding="utf-8")
        (self.config / "config.json").write_text('{"engine": "sdcpp"}', encoding="utf-8")
        self.engine_dir = self.data / "engine" / engine_sdcpp.RELEASE
        self.engine_dir.mkdir(parents=True)
        script(self.engine_dir / "sd-cli", "exit 0")
        (self.engine_dir / "libggml.so").write_bytes(b"")
        self.install_model("diffusion", "d.gguf")
        self.install_model("text", "t.gguf")
        self.install_model("vae", "v.safetensors")
        self.dead = dead_ollama_url()
        env = mock.patch.dict(os.environ, {
            "HOME": str(self.home), "PATH": "%s:%s" % (self.bin, self.home / ".local" / "bin"),
            "GIMG_CONFIG_HOME": str(self.config), "GIMG_DATA_HOME": str(self.data),
            "GIMG_CATALOG": str(self.catalog_file), "GIMG_MEMINFO": str(self.meminfo),
            "GIMG_OLLAMA_URL": self.dead, "GIMG_LANG": "en"})
        env.start()
        self.addCleanup(env.stop)
        for name in ("GIMG_ENGINE", "GIMG_SD_CLI", "GIMG_MODELS_HOME", "GIMG_MACHINE_PROFILE", "XDG_DATA_HOME",
                     "XDG_CONFIG_HOME"):
            os.environ.pop(name, None)

    def set_meminfo(self, kb):
        self.meminfo.write_text("MemTotal: 99999999 kB\nMemAvailable: %d kB\n" % kb, encoding="utf-8")

    def install_model(self, kind, name, content=None):
        folder = self.data / "models" / kind
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(body(kind) if content is None else content)

    def remove_model(self, kind, name):
        (self.data / "models" / kind / name).unlink()

    def set_config(self, text):
        (self.config / "config.json").write_text(text, encoding="utf-8")

    def machine_file(self, **engine):
        profile = json.loads((limits._PRESETS / "steam-deck.json").read_text(encoding="utf-8"))
        profile["engine"].update(engine)
        path = self.tmp / "machine.json"
        path.write_text(json.dumps(profile), encoding="utf-8")
        os.environ["GIMG_MACHINE_PROFILE"] = str(path)

    def checks(self, **kwargs):
        return {c.id: c for c in doctor.run(**kwargs)}

    def one(self, check_id, **kwargs):
        return self.checks(**kwargs)[check_id]


class GreenTests(DoctorBase):
    def test_a_complete_machine_has_no_warning_and_exits_0(self):
        found = doctor.run()
        self.assertEqual([(c.id, c.status) for c in found if c.status != doctor.OK], [])
        self.assertFalse(doctor.failed(found))
        ids = [c.id for c in found]
        for expected in ("python", "launcher", "config", "engine", "machine", "binary", "libs", "model:m-default",
                         "model:m-optional", "memory", "tool:ffmpeg", "tool:rsvg-convert", "data", "ollama"):
            self.assertIn(expected, ids)
        self.assertEqual(self.checks()["tool:ffmpeg"].params["version"], "ffmpeg version 9.9-test Copyright")
        self.assertEqual(self.checks()["tool:rsvg-convert"].params["version"], "rsvg-convert version 1.2.3")
        self.assertEqual(self.checks()["model:m-optional"].key, "doctor.model.optional")
        self.assertIn("instalar.sh --with m-optional", self.checks()["model:m-optional"].fix("en"))


class PythonTests(DoctorBase):
    def test_python_older_than_3_10_fails_with_the_minimum(self):
        with mock.patch.object(sys, "version_info", (3, 9, 18, "final", 0)):
            check = doctor._python()
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.python.old"))
        self.assertEqual((check.params["version"], check.params["min"]), ("3.9.18", "3.10"))
        self.assertIn("3.10", check.message("en"))


class LauncherTests(DoctorBase):
    def test_missing_launcher_fails_and_says_how_to_install_it(self):
        (self.home / ".local" / "bin" / "gimg").unlink()
        check = self.one("launcher")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.launcher.missing"))
        self.assertRegex(check.fix("en"), r"instalar\.sh --only-cli$")

    def test_launcher_outside_path_only_warns_and_says_the_line_to_add(self):
        os.environ["PATH"] = str(self.bin)
        check = self.one("launcher")
        self.assertEqual((check.status, check.key), (doctor.WARN, "doctor.launcher.not_in_path"))
        self.assertIn('export PATH="$HOME/.local/bin:$PATH"', check.fix("en"))


class ConfigTests(DoctorBase):
    def test_no_config_file_warns_and_the_engine_is_fake(self):
        (self.config / "config.json").unlink()
        found = self.checks()
        self.assertEqual((found["config"].status, found["config"].key), (doctor.WARN, "doctor.config.missing"))
        self.assertEqual((found["engine"].status, found["engine"].key), (doctor.WARN, "doctor.engine.fake"))

    def test_unreadable_config_fails_with_the_reason_and_so_does_the_engine(self):
        self.set_config("{not json")
        found = self.checks()
        self.assertEqual((found["config"].status, found["config"].key), (doctor.FAIL, "doctor.config.unreadable"))
        self.assertIn("Expecting", found["config"].params["reason"])
        self.assertEqual((found["engine"].status, found["engine"].key), (doctor.FAIL, "doctor.engine.error"))

    def test_unknown_engine_fails_naming_it(self):
        self.set_config('{"engine": "cuda"}')
        check = self.one("engine")
        self.assertEqual((check.status, check.key, check.params["engine"]), (doctor.FAIL, "doctor.engine.unknown", "cuda"))

    def test_gimg_engine_wins_over_the_file(self):
        os.environ["GIMG_ENGINE"] = "fake"
        self.assertEqual(self.one("engine").key, "doctor.engine.fake")

    def test_invalid_machine_profile_fails_with_its_message(self):
        os.environ["GIMG_MACHINE_PROFILE"] = "no-such-machine"
        check = self.one("machine")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.machine.error"))
        self.assertIn("no-such-machine", check.params["message"])


class BinaryTests(DoctorBase):
    def test_missing_binary_fails_under_sdcpp_and_warns_under_fake(self):
        (self.engine_dir / "sd-cli").unlink()
        check = self.one("binary")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.binary.missing"))
        self.assertIn(engine_sdcpp.RELEASE, check.params["path"])
        self.assertNotIn("libs", self.checks())  # nothing to look next to
        os.environ["GIMG_ENGINE"] = "fake"
        self.assertEqual(self.one("binary").status, doctor.WARN)

    def test_binary_without_the_exec_bit_fails_with_chmod(self):
        (self.engine_dir / "sd-cli").chmod(0o644)
        check = self.one("binary")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.binary.not_executable"))
        self.assertTrue(check.fix("en").startswith("chmod +x "))

    def test_no_libggml_next_to_the_binary_fails(self):
        (self.engine_dir / "libggml.so").unlink()
        (self.engine_dir / "libother.so").write_bytes(b"")
        check = self.one("libs")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.libs.missing"))
        self.assertEqual(check.params["dir"], str(self.engine_dir))

    def test_gimg_sd_cli_moves_the_folder_where_the_libraries_are_looked_for(self):
        other = self.tmp / "elsewhere"
        other.mkdir()
        script(other / "sd-cli", "exit 0")
        os.environ["GIMG_SD_CLI"] = str(other / "sd-cli")
        self.assertEqual(self.one("libs").status, doctor.FAIL)
        (other / "libggml-base.so.0").write_bytes(b"")
        libs = self.one("libs")
        self.assertEqual((libs.status, libs.params["count"], libs.params["dir"]), (doctor.OK, 1, str(other)))


class ModelTests(DoctorBase):
    def test_a_default_model_with_nothing_installed_fails_under_sdcpp_and_warns_under_fake(self):
        for kind, name in (("diffusion", "d.gguf"), ("text", "t.gguf"), ("vae", "v.safetensors")):
            self.remove_model(kind, name)
        check = self.one("model:m-default")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.model.absent"))
        os.environ["GIMG_ENGINE"] = "fake"
        self.assertEqual(self.one("model:m-default").status, doctor.WARN)

    def test_a_partial_model_fails_and_names_the_missing_files(self):
        self.remove_model("text", "t.gguf")
        check = self.one("model:m-default")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.model.partial"))
        self.assertEqual(check.params["files"], "text/t.gguf")
        os.environ["GIMG_ENGINE"] = "fake"
        self.assertEqual(self.one("model:m-default").status, doctor.FAIL)  # a half-installed model is never fine

    def test_a_partial_optional_model_fails_and_the_fix_asks_for_it_by_id(self):
        self.install_model("diffusion", "d2.gguf")  # only one of its three files
        check = self.one("model:m-optional")
        self.assertEqual((check.status, check.key, check.params["files"]),
                         (doctor.FAIL, "doctor.model.partial", "text/t2.gguf, vae/v2.safetensors"))
        self.assertTrue(check.fix("en").endswith("--with m-optional"))

    def test_a_file_of_the_wrong_size_fails_with_both_sizes(self):
        self.install_model("diffusion", "d.gguf", b"short")
        check = self.one("model:m-default")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.model.size"))
        self.assertEqual((check.params["file"], check.params["got"], check.params["want"]), ("d.gguf", 0, 2))
        self.assertIn("delete ", check.fix("en"))

    def test_without_verify_the_sha_is_not_checked_and_it_says_so(self):
        self.install_model("vae", "v.safetensors", body("vae", "-other"))  # same size, other content
        check = self.one("model:m-default")
        self.assertEqual((check.status, check.key), (doctor.OK, "doctor.model.ok_size"))
        self.assertIn("--verify", check.message("en"))

    def test_verify_sums_the_files_and_catches_the_same_size_different_content(self):
        self.install_model("vae", "v.safetensors", body("vae", "-other"))
        check = self.one("model:m-default", verify=True)
        self.assertEqual((check.status, check.key, check.params["file"]), (doctor.FAIL, "doctor.model.sha", "v.safetensors"))

    def test_verify_passes_when_every_sha_matches(self):
        check = self.one("model:m-default", verify=True)
        self.assertEqual((check.status, check.key), (doctor.OK, "doctor.model.ok_sha"))

    def test_gimg_models_home_moves_where_the_models_are_looked_for(self):
        elsewhere = self.tmp / "sdcard"
        os.environ["GIMG_MODELS_HOME"] = str(elsewhere)
        self.assertEqual(self.one("model:m-default").key, "doctor.model.absent")
        for kind, name in (("diffusion", "d.gguf"), ("text", "t.gguf"), ("vae", "v.safetensors")):
            (elsewhere / kind).mkdir(parents=True)
            (elsewhere / kind / name).write_bytes(body(kind))
        self.assertEqual(self.one("model:m-default").status, doctor.OK)

    def test_an_invalid_catalog_fails_with_its_message(self):
        self.catalog_file.write_text('{"models": {}}', encoding="utf-8")
        check = self.one("models")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.models.catalog"))


class MemoryAndToolsTests(DoctorBase):
    def test_low_free_memory_warns_with_both_numbers(self):
        self.set_meminfo(3_072_000)
        check = self.one("memory")
        self.assertEqual((check.status, check.params), (doctor.WARN, {"free": 3000, "needed": 7000}))

    def test_no_meminfo_skips_the_check(self):
        self.meminfo.unlink()
        self.assertNotIn("memory", self.checks())

    def test_a_missing_tool_fails_and_names_the_packages(self):
        (self.bin / "rsvg-convert").unlink()
        check = self.one("tool:rsvg-convert")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.tool.missing"))
        self.assertIn("apt install librsvg2-bin", check.fix("en"))
        self.assertIn("pacman -S librsvg", check.fix("en"))
        self.assertEqual(self.one("tool:ffmpeg").status, doctor.OK)

    def test_a_tool_that_cannot_run_fails_as_broken(self):
        (self.bin / "ffmpeg").write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        check = self.one("tool:ffmpeg")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.tool.broken"))


class FolderTests(DoctorBase):
    def test_a_data_folder_that_does_not_exist_yet_warns_with_mkdir(self):
        os.environ["GIMG_DATA_HOME"] = str(self.tmp / "later")
        check = self.one("data")
        self.assertEqual((check.status, check.key), (doctor.WARN, "doctor.data.missing"))
        self.assertTrue(check.fix("en").startswith("mkdir -p "))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes anywhere")
    def test_a_read_only_data_folder_fails(self):
        self.data.chmod(0o500)
        self.addCleanup(self.data.chmod, 0o700)
        check = self.one("data")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.data.unwritable"))

    def test_xdg_into_flatpak_warns_and_says_how_to_pin_the_folders(self):
        del os.environ["GIMG_DATA_HOME"]
        os.environ["XDG_DATA_HOME"] = str(self.home / ".var" / "app" / "com.example.Editor" / "data")
        check = self.one("flatpak")
        self.assertEqual((check.status, check.key), (doctor.WARN, "doctor.flatpak.warn"))
        self.assertIn("XDG_DATA_HOME=", check.params["vars"])
        self.assertIn(".var/app/com.example.Editor/data/gimg", check.params["data"])  # the XDG is honoured, not ignored
        self.assertIn('export GIMG_DATA_HOME="$HOME/.local/share/gimg"', check.fix("en"))
        self.assertNotIn("GIMG_CONFIG_HOME", check.fix("en"))

    def test_a_pinned_folder_silences_the_flatpak_warning_for_that_variable(self):
        os.environ["XDG_DATA_HOME"] = str(self.home / ".var" / "app" / "x" / "data")  # GIMG_DATA_HOME is set
        self.assertNotIn("flatpak", self.checks())
        del os.environ["GIMG_CONFIG_HOME"]
        os.environ["XDG_CONFIG_HOME"] = str(self.home / ".var" / "app" / "x" / "config")
        check = self.one("flatpak")
        self.assertIn('GIMG_CONFIG_HOME="$HOME/.config/gimg"', check.fix("en"))
        self.assertNotIn("GIMG_DATA_HOME", check.fix("en"))

    def test_no_flatpak_warning_on_a_normal_xdg(self):
        os.environ["XDG_DATA_HOME"] = str(self.home / ".local" / "share")
        self.assertNotIn("flatpak", self.checks())


class OllamaTests(DoctorBase):
    def test_models_loaded_in_ollama_fail_under_abort_with_the_stop_commands(self):
        server = FakeOllama(self, models=[loaded("llama3:8b"), loaded("nomic-embed")])
        check = self.one("ollama", ollama_url=server.url)
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.ollama.loaded"))
        self.assertEqual(check.fix("en"), "ollama stop llama3:8b; ollama stop nomic-embed")
        os.environ["GIMG_ENGINE"] = "fake"
        self.assertEqual(self.one("ollama", ollama_url=server.url).status, doctor.WARN)

    def test_the_url_comes_from_gimg_ollama_url_when_it_is_not_injected(self):
        server = FakeOllama(self, models=[loaded("a")])
        os.environ["GIMG_OLLAMA_URL"] = server.url
        self.assertEqual(self.one("ollama").key, "doctor.ollama.loaded")

    def test_unload_mode_only_warns_because_gimg_unloads_them(self):
        self.machine_file(ollama="unload")
        server = FakeOllama(self, models=[loaded("a")])
        check = self.one("ollama", ollama_url=server.url)
        self.assertEqual((check.status, check.key), (doctor.WARN, "doctor.ollama.loaded_unload"))

    def test_ignore_mode_does_not_even_ask_ollama(self):
        self.machine_file(ollama="ignore")
        server = FakeOllama(self, models=[loaded("a")])
        check = self.one("ollama", ollama_url=server.url)
        self.assertEqual((check.status, check.key, server.ps_hits), (doctor.OK, "doctor.ollama.ignored", 0))

    def test_ollama_that_is_off_counts_as_nothing_loaded(self):
        check = self.one("ollama")
        self.assertEqual((check.status, check.key, check.params["url"]), (doctor.OK, "doctor.ollama.ok", self.dead))

    def test_a_bad_ollama_url_fails(self):
        os.environ["GIMG_OLLAMA_URL"] = "ftp://nope"
        check = self.one("ollama")
        self.assertEqual((check.status, check.key), (doctor.FAIL, "doctor.ollama.bad_url"))
        self.assertIn("ftp://nope", check.params["message"])


class CliTests(DoctorBase):
    def doctor(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["doctor", *argv])
        return code, out.getvalue()

    def test_exit_0_and_a_readable_report_when_everything_is_fine(self):
        code, text = self.doctor()
        self.assertEqual(code, 0)
        self.assertIn("[OK    ] ffmpeg: ffmpeg version 9.9-test Copyright", text)
        self.assertTrue(text.rstrip().endswith("All good."))

    def test_exit_1_with_the_fix_under_the_failed_line(self):
        (self.engine_dir / "sd-cli").unlink()
        code, text = self.doctor()
        self.assertEqual(code, 1)
        lines = text.splitlines()
        at = next(i for i, line in enumerate(lines) if line.startswith("[FAIL  ] sd-cli is missing"))
        self.assertRegex(lines[at + 1], r"^ +-> bash .*instalar\.sh$")
        self.assertIn("something failed".lower(), lines[-1].lower())

    def test_only_warnings_still_exit_0(self):
        os.environ["GIMG_ENGINE"] = "fake"
        code, text = self.doctor()
        self.assertEqual(code, 0)
        self.assertIn("[WARN  ] configured engine: fake", text)

    def test_spanish_text(self):
        (self.engine_dir / "libggml.so").unlink()
        code, text = self.doctor("--lang", "es")
        self.assertEqual(code, 1)
        self.assertIn("[FALLO ] no hay libggml* junto a sd-cli", text)
        self.assertIn("Hay fallos", text)

    def test_json_has_status_message_and_fix_per_check(self):
        (self.bin / "ffmpeg").unlink()
        code, text = self.doctor("--json")
        data = json.loads(text)
        self.assertEqual((code, data["ok"]), (1, False))
        ffmpeg = next(c for c in data["checks"] if c["id"] == "tool:ffmpeg")
        self.assertEqual(ffmpeg["status"], "fail")
        self.assertIn("ffmpeg is not in PATH", ffmpeg["message"])
        self.assertIn("apt install ffmpeg", ffmpeg["fix"])
        python = next(c for c in data["checks"] if c["id"] == "python")
        self.assertEqual((python["status"], python["fix"]), ("ok", None))

    def test_verify_flag_reaches_the_checks(self):
        self.install_model("vae", "v.safetensors", body("vae", "-other"))
        self.assertEqual(self.doctor()[0], 0)
        code, text = self.doctor("--verify")
        self.assertEqual(code, 1)
        self.assertIn("the sha256 of v.safetensors does not match", text)


class FontsTests(DoctorBase):
    """F2.8: the fonts of ``compose.fonts`` of the registered projects, looked up with one ``fc-list``; always ``warn``."""

    def project(self, name, fonts_by_profile):
        root = self.tmp / name
        root.mkdir()
        profiles = {}
        for profile, fonts in fonts_by_profile.items():
            data = {"width": 1280, "height": 640, "steps": 6, "cfg": 1.0, "sampler": "euler", "model": "m-default"}
            if fonts is not None:
                data["compose"] = {"template": "t.svg", "fonts": fonts}
            profiles[profile] = data
        (root / "galivelop-images.json").write_text(json.dumps(
            {"minVersion": "0.1.0", "name": name, "delivery": {"dir": "out", "template": "{key}-{profile}.png"},
             "profiles": profiles}), encoding="utf-8")
        projects.add(root)
        return root

    def fc_list(self, families):
        """A fake ``fc-list`` that answers `families` and records its arguments."""
        self.fc_args = self.tmp / "fc-args"
        lines = " ".join("'%s'" % f for f in families)  # builtins only: the fake PATH has no cat
        script(self.bin / "fc-list", 'printf "%%s\\n" "$@" >> "%s"\nprintf \'%%s\\n\' %s' % (self.fc_args, lines))

    def fonts(self):
        return {c.id: c for c in doctor.run() if c.id.startswith(("font", "fonts"))}

    def test_no_project_declares_fonts_is_ok_and_fc_list_is_not_needed(self):
        self.project("p", {"og": None})
        self.assertEqual([(c.id, c.status, c.key) for c in self.fonts().values()], [("fonts", doctor.OK, "doctor.fonts.none")])

    def test_an_installed_font_is_ok_case_insensitive_and_a_line_can_list_several_families(self):
        self.fc_list(["Sora,Sora Thin", "Inter", "Cormorant Garamond,Cormorant Garamond Light"])
        self.project("p", {"og": ["sora", "Cormorant Garamond"], "wide": ["Inter"]})
        found = self.fonts()
        self.assertEqual({k: (c.status, c.key) for k, c in found.items()},
                         {"font:sora": (doctor.OK, "doctor.fonts.ok"), "font:Cormorant Garamond": (doctor.OK, "doctor.fonts.ok"),
                          "font:Inter": (doctor.OK, "doctor.fonts.ok")})
        self.assertEqual(self.fc_args.read_text().split("\n")[:-1], ["--format", "%{family}\\n"])  # ONE call, with the format

    def test_a_missing_font_warns_with_the_projects_that_use_it_and_how_to_install_it(self):
        self.fc_list(["Inter"])
        self.project("alpha", {"og": ["Sora"]})
        self.project("beta", {"og": ["Sora", "Inter"], "wide": ["Sora"]})
        found = self.fonts()
        check = found["font:Sora"]
        self.assertEqual((check.status, check.key, check.params), (doctor.WARN, "doctor.fonts.missing",
                                                                    {"font": "Sora", "projects": "alpha, beta"}))
        self.assertEqual(found["font:Inter"].status, doctor.OK)
        self.assertIn("fc-cache -f", check.fix("en"))
        self.assertIn("~/.local/share/fonts", check.fix("es"))
        self.assertFalse(doctor.failed(doctor.run()))  # a warning, never a failure

    def test_without_fc_list_it_warns_once_and_does_not_fail(self):
        self.project("p", {"og": ["Sora", "Inter"]})
        found = self.fonts()
        self.assertEqual([(c.id, c.status, c.key) for c in found.values()],
                         [("fonts", doctor.WARN, "doctor.fonts.no_fc_list")])
        self.assertIn("fontconfig", found["fonts"].fix("en"))
        self.assertFalse(doctor.failed(doctor.run()))

    def test_an_fc_list_that_fails_counts_as_missing(self):
        script(self.bin / "fc-list", "exit 3")
        self.project("p", {"og": ["Sora"]})
        self.assertEqual(self.fonts()["fonts"].key, "doctor.fonts.no_fc_list")

    def test_a_broken_project_warns_with_its_name_and_the_others_are_still_checked(self):
        self.fc_list(["Inter"])
        self.project("good", {"og": ["Inter"]})
        broken = self.project("broken", {"og": ["Sora"]})
        (broken / "galivelop-images.json").write_text("{not json", encoding="utf-8")
        found = self.fonts()
        check = found["fonts:broken"]
        self.assertEqual((check.status, check.key, check.params["project"]), (doctor.WARN, "doctor.fonts.project_error", "broken"))
        self.assertIn("galivelop-images.json", check.params["message"])
        self.assertEqual(found["font:Inter"].status, doctor.OK)
        self.assertNotIn("font:Sora", found)

    def test_no_registered_project_is_ok(self):
        self.assertEqual([c.key for c in self.fonts().values()], ["doctor.fonts.none"])

    def test_the_texts_exist_in_both_languages(self):
        for key in ("doctor.fonts.none", "doctor.fonts.ok", "doctor.fonts.missing", "doctor.fonts.no_fc_list",
                    "doctor.fonts.project_error", "doctor.fix.fonts"):
            self.assertNotEqual(i18n.t(key, "es", font="f", projects="p", project="p", message="m"),
                                i18n.t(key, "en", font="f", projects="p", project="p", message="m"), key)


class LocaleTests(unittest.TestCase):
    def test_every_doctor_key_has_text_in_both_languages(self):
        keys = set()
        for name in ("doctor.py", "cli.py"):
            keys |= set(re.findall(r'"(doctor\.[a-z_.]+)"', (ROOT / "gimg" / name).read_text(encoding="utf-8")))
        self.assertIn("doctor.python.old", keys)
        self.assertIn("doctor.fix.flatpak", keys)
        for lang in ("es", "en"):
            texts = json.loads((ROOT / "gimg" / "locales" / (lang + ".json")).read_text(encoding="utf-8"))
            self.assertEqual(sorted(k for k in keys if k not in texts), [], lang)

    def test_the_two_languages_differ(self):
        for key in ("doctor.binary.missing", "doctor.summary_fail", "doctor.tool.missing"):
            self.assertNotEqual(i18n.t(key, "es", path="p", tool="t"), i18n.t(key, "en", path="p", tool="t"))


if __name__ == "__main__":
    unittest.main()
