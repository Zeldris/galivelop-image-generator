"""`instalar.sh` (F2.5): only with a temporary HOME, a fake catalog (`GIMG_CATALOG`) and a fake `curl` that serves local files:
nothing is downloaded, installed or written outside the temporary folders. The real engine download (the zip and its
sha256) is manual on the Deck: no zip with that sum can be made here."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from gimg import __version__, engine_sdcpp
from tests.test_doctor import body, script, small_catalog

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "instalar.sh"
SD_ZIP = re.search(r'^SD_ZIP="(\S+) ([0-9a-f]{64})"$', SCRIPT.read_text(encoding="utf-8"), re.M)

FAKE_CURL = r"""#!/bin/sh
echo "$*" >> "$FAKE_CURL_LOG"
out=""; url=""
while [ $# -gt 0 ]; do
  case "$1" in -o) out="$2"; shift ;; -*) ;; *) url="$1" ;; esac
  shift
done
[ -n "${FAKE_SERVE:-}" ] && [ -f "$FAKE_SERVE/$(basename "$url")" ] || { echo "fake curl: 404 $url" >&2; exit 22; }
cp "$FAKE_SERVE/$(basename "$url")" "$out"
"""


@unittest.skipUnless(shutil.which("bash") and SD_ZIP, "needs bash")
class InstalarBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.home = self.tmp / "home"
        self.fakebin = self.tmp / "fakebin"
        self.serve = self.tmp / "serve"
        self.curl_log = self.tmp / "curl.log"
        for d in (self.home, self.fakebin, self.serve):
            d.mkdir()
        script(self.fakebin / "curl", FAKE_CURL.split("\n", 1)[1])
        script(self.fakebin / "ffmpeg", 'echo "ffmpeg version 9.9-test"')
        script(self.fakebin / "rsvg-convert", 'echo "rsvg-convert version 1.2.3"')
        self.meminfo = self.tmp / "meminfo"
        self.meminfo.write_text("MemAvailable: 20000000 kB\n", encoding="utf-8")
        self.data, self.config = self.tmp / "data", self.tmp / "config"

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIMG_", "XDG_"))}
        env.update(HOME=str(self.home), GIMG_LANG="en", FAKE_CURL_LOG=str(self.curl_log), FAKE_SERVE=str(self.serve),
                   PATH="%s:%s:%s" % (self.fakebin, self.home / ".local" / "bin", os.environ["PATH"]))
        env.update(extra)
        return env

    script_path = SCRIPT

    def path_without(self, *names):
        """A folder of symlinks to everything in the system bin folders except `names` (to simulate a missing tool)."""
        folder = self.tmp / ("bin-without-" + "-".join(names))
        folder.mkdir()
        for bindir in ("/usr/bin", "/bin"):
            for entry in os.listdir(bindir) if os.path.isdir(bindir) else ():
                if entry not in names and not (folder / entry).exists():
                    os.symlink(os.path.join(bindir, entry), folder / entry)
        return folder

    def run_script(self, *args, **extra):
        return subprocess.run(["bash", str(self.script_path), *args], capture_output=True, text=True, env=self.env(**extra),
                              cwd=str(self.tmp), timeout=120)

    def curl_calls(self):
        return self.curl_log.read_text(encoding="utf-8").splitlines() if self.curl_log.exists() else []


class ScriptTextTests(unittest.TestCase):
    def test_the_release_lives_only_in_the_engine_module_and_the_zip_name_matches_it(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn(engine_sdcpp.RELEASE, text)
        self.assertIn("engine_sdcpp.RELEASE", text)
        self.assertIn(engine_sdcpp.RELEASE.rsplit("-", 1)[1], SD_ZIP.group(1))  # the short commit hash
        self.assertTrue(SD_ZIP.group(1).endswith("-vulkan.zip") and "Linux" in SD_ZIP.group(1))

    def test_the_script_reads_folders_and_catalog_instead_of_repeating_them(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for needle in ("paths.data_dir()", "paths.models_dir()", "paths.config_dir()", "models.load_catalog()"):
            self.assertIn(needle, text)
        self.assertNotIn("huggingface.co", text)
        self.assertNotIn(".gguf", text)

    def test_it_is_executable_and_parses(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


class DryRunTests(InstalarBase):
    def test_only_cli_dry_run_says_what_it_would_write_and_writes_nothing(self):
        done = self.run_script("--dry-run", "--only-cli")
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        launcher = self.home / ".local" / "bin" / "gimg"
        self.assertIn("[dry-run] [2/6] would write the launcher %s (exec python3 -m gimg, from %s)" % (launcher, ROOT), done.stdout)
        self.assertIn("Launcher only (--only-cli)", done.stdout)
        self.assertNotIn("[3/6]", done.stdout)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_only_cli_dry_run_in_spanish(self):
        done = self.run_script("--dry-run", "--only-cli", GIMG_LANG="es")
        self.assertIn("escribiría el lanzador", done.stdout)
        self.assertIn("Solo el lanzador", done.stdout)

    def test_it_warns_when_the_launcher_folder_is_not_in_path(self):
        done = self.run_script("--dry-run", "--only-cli", PATH="/usr/bin:/bin")
        self.assertIn("is not in PATH", done.stdout)
        self.assertIn('export PATH="$HOME/.local/bin:$PATH"', done.stdout)
        done = self.run_script("--dry-run", "--only-cli")  # the folder is in the PATH of env()
        self.assertNotIn("is not in PATH", done.stdout)

    def test_dry_run_lists_the_default_model_files_and_the_engine_and_never_calls_curl(self):
        models = self.tmp / "models"
        done = self.run_script("--dry-run", GIMG_MODELS_HOME=str(models), GIMG_DATA_HOME=str(self.data),
                               GIMG_CONFIG_HOME=str(self.config))
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        out = done.stdout
        self.assertIn("[dry-run] [3/6] would download https://github.com/leejet/stable-diffusion.cpp/releases/download/%s/%s"
                      % (engine_sdcpp.RELEASE, SD_ZIP.group(1)), out)
        self.assertIn("%s/engine/%s" % (self.data, engine_sdcpp.RELEASE), out)
        self.assertIn("flux2-klein-4b-q8/diffusion: would download https://huggingface.co/leejet/FLUX.2-klein-4B-GGUF/"
                      "resolve/main/flux-2-klein-4b-Q8_0.gguf (4301 MB) -> %s/diffusion/flux-2-klein-4b-Q8_0.gguf" % models, out)
        self.assertIn("flux2-klein-4b-q8/text:", out)
        self.assertIn("flux2-klein-4b-q8/vae:", out)
        self.assertNotIn("flux3-klein-q8", out)  # optional: only with --with
        self.assertIn('would set "engine": "sdcpp" in %s/config.json' % self.config, out)
        self.assertIn("[dry-run] [6/6] would run: gimg doctor", out)
        self.assertFalse(self.curl_log.exists())
        self.assertEqual(list(self.home.iterdir()), [])
        self.assertFalse(models.exists() or self.data.exists() or self.config.exists())

    def test_with_adds_other_models_and_repeats(self):
        done = self.run_script("--dry-run", "--with", "flux3-klein-q8", "--with", "flux2-klein-4b-q8",
                               GIMG_MODELS_HOME=str(self.tmp / "m"))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("flux3-klein-q8/diffusion: would download", done.stdout)
        self.assertEqual(done.stdout.count("flux2-klein-4b-q8/diffusion:"), 1)  # asked twice, installed once

    def test_an_unknown_model_id_stops_with_the_known_ones(self):
        done = self.run_script("--dry-run", "--with", "nope")
        self.assertEqual(done.returncode, 1)
        self.assertIn("unknown model in --with: nope (known: flux2-klein-4b-q8 flux3-klein-q8", done.stderr)

    def test_a_file_that_is_already_there_is_kept_and_a_models_from_file_would_be_linked(self):
        models, source = self.tmp / "models", self.tmp / "tarkor"
        (models / "diffusion").mkdir(parents=True)
        (models / "diffusion" / "flux-2-klein-4b-Q8_0.gguf").write_bytes(b"x")
        (source / "text").mkdir(parents=True)
        (source / "text" / "Qwen3-4B-Q4_K_M.gguf").write_bytes(b"x")
        (source / "full_encoder_small_decoder.safetensors").write_bytes(b"x")
        done = self.run_script("--dry-run", "--models-from", str(source), GIMG_MODELS_HOME=str(models))
        out = done.stdout
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("diffusion: flux-2-klein-4b-Q8_0.gguf is already there; its sha256 would be checked", out)
        self.assertIn("text: would link %s/text/Qwen3-4B-Q4_K_M.gguf -> %s/text/Qwen3-4B-Q4_K_M.gguf after checking" % (source, models), out)
        self.assertIn("vae: would link %s/full_encoder_small_decoder.safetensors" % source, out)
        self.assertEqual(os.listdir(models / "diffusion"), ["flux-2-klein-4b-Q8_0.gguf"])  # nothing linked in a dry run

    def test_bad_arguments_fail_with_a_reason(self):
        for args, message in ((["--nope"], "unknown option: --nope"), (["--with"], "--with needs a model id"),
                              (["--models-from"], "--models-from needs a folder"),
                              (["--models-from", str(self.tmp / "absent")], "--models-from folder does not exist")):
            done = self.run_script("--dry-run", *args)
            self.assertEqual(done.returncode, 1, args)
            self.assertIn(message, done.stderr)


class LauncherTests(InstalarBase):
    def test_only_cli_writes_a_launcher_that_runs_gimg_from_the_repo_and_is_idempotent(self):
        done = self.run_script("--only-cli")
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        launcher = self.home / ".local" / "bin" / "gimg"
        self.assertTrue(os.access(launcher, os.X_OK))
        text = launcher.read_text(encoding="utf-8")
        self.assertIn('exec python3 -m gimg "$@"', text)
        self.assertIn("PYTHONPATH='%s'" % ROOT, text)
        ran = subprocess.run([str(launcher), "version"], capture_output=True, text=True, cwd=str(self.tmp),
                             env=self.env(GIMG_DATA_HOME=str(self.data), GIMG_CONFIG_HOME=str(self.config)))
        self.assertEqual((ran.returncode, ran.stdout.strip()), (0, __version__), ran.stderr)
        self.assertEqual(sorted(p.name for p in self.home.rglob("*") if p.is_file()), ["gimg"])  # nothing else written
        again = self.run_script("--only-cli")
        self.assertIn("Launcher already up to date", again.stdout)


class FullRunBase(InstalarBase):
    """A whole run (steps 1-6) with the engine already in place, a fake catalog of three tiny files per model and a fake curl."""

    def setUp(self):
        super().setUp()
        self.catalog_file = self.tmp / "catalog.json"
        self.catalog = small_catalog()
        self.catalog_file.write_text(json.dumps(self.catalog), encoding="utf-8")
        engine = self.data / "engine" / engine_sdcpp.RELEASE
        engine.mkdir(parents=True)
        script(engine / "sd-cli", "exit 0")
        (engine / "libggml.so").write_bytes(b"")
        (engine / ".zip-sha256").write_text(SD_ZIP.group(2) + "\n", encoding="utf-8")
        self.models = self.tmp / "models"
        self.config.mkdir()
        (self.config / "config.json").write_text('{"keep": 1, "machineProfile": "steam-deck"}', encoding="utf-8")
        dead = subprocess.run(["python3", "-c", "import socket; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1])"],
                              capture_output=True, text=True).stdout.strip()
        self.base_env = dict(GIMG_CATALOG=str(self.catalog_file), GIMG_DATA_HOME=str(self.data), GIMG_CONFIG_HOME=str(self.config),
                             GIMG_MODELS_HOME=str(self.models), GIMG_MEMINFO=str(self.meminfo),
                             GIMG_OLLAMA_URL="http://127.0.0.1:" + dead)

    def go(self, *args, **extra):
        return self.run_script(*args, **dict(self.base_env, **extra))

    def files_of(self, model_id):
        return {k: v for k, v in self.catalog["models"][model_id]["files"].items()}

    def serve_model(self, model_id, corrupt=None):
        for kind, entry in self.files_of(model_id).items():
            (self.serve / entry["name"]).write_bytes(body(kind, "-bad" if kind == corrupt else ""))


class FullRunTests(FullRunBase):
    def test_models_from_links_files_whose_sha_matches_and_downloads_nothing(self):
        source = self.tmp / "tarkor"
        source.mkdir()
        for kind, entry in self.files_of("m-default").items():
            (source / entry["name"]).write_bytes(body(kind))
        done = self.go("--models-from", str(source))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        for kind, entry in self.files_of("m-default").items():
            link = self.models / kind / entry["name"]
            self.assertTrue(link.is_symlink() and link.resolve() == (source / entry["name"]).resolve(), kind)
        self.assertEqual(self.curl_calls(), [])
        self.assertIn("Engine %s already installed" % engine_sdcpp.RELEASE, done.stdout)
        self.assertTrue(done.stdout.rstrip().endswith("All good."), done.stdout)
        self.assertEqual(json.loads((self.config / "config.json").read_text()),
                         {"engine": "sdcpp", "keep": 1, "machineProfile": "steam-deck"})  # other keys stay
        self.assertFalse((self.models / "diffusion" / "d2.gguf").exists())  # the optional model was not asked for
        self.assertTrue((self.home / ".local" / "bin" / "gimg").is_file())

    def test_it_downloads_with_resume_checks_the_sha_and_does_not_download_twice(self):
        self.serve_model("m-default")
        done = self.go()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = self.curl_calls()
        self.assertEqual(len(calls), 3)
        for kind, entry in self.files_of("m-default").items():
            self.assertTrue(any(c.startswith("-fL -C - ") and entry["url"] in c and c.endswith(entry["url"]) for c in calls), kind)
            final = self.models / kind / entry["name"]
            self.assertEqual(final.read_bytes(), body(kind))
            self.assertFalse(final.is_symlink() or Path(str(final) + ".part").exists())
        again = self.go()
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertEqual(len(self.curl_calls()), 3)  # nothing new
        self.assertEqual(again.stdout.count("already matches; left alone"), 3)

    def test_a_download_with_the_wrong_sha_stops_and_leaves_no_final_file(self):
        self.serve_model("m-default", corrupt="vae")
        done = self.go()
        self.assertEqual(done.returncode, 1)
        self.assertIn("the sha256 of v.safetensors does not match", done.stderr)
        self.assertIn("the download was deleted, retry", done.stderr)
        self.assertFalse((self.models / "vae" / "v.safetensors").exists())
        self.assertFalse((self.models / "vae" / "v.safetensors.part").exists())  # a bad .part is not resumed next time
        self.assertTrue((self.models / "diffusion" / "d.gguf").exists())  # the earlier ones are kept
        self.assertEqual(json.loads((self.config / "config.json").read_text()).get("engine"), None)  # no config before models

    def test_a_failed_download_leaves_the_file_that_was_there_untouched(self):
        (self.models / "diffusion").mkdir(parents=True)
        old = self.models / "diffusion" / "d.gguf"
        old.write_bytes(body("diffusion", "-bad"))  # does not match the catalog; nothing is served, curl fails
        done = self.go()
        self.assertEqual(done.returncode, 1)
        self.assertIn("d.gguf does not match the catalog; replacing it", done.stdout)
        self.assertIn("the download of d.gguf failed; whatever was at %s is untouched" % old, done.stderr)
        self.assertEqual(old.read_bytes(), body("diffusion", "-bad"))

    def test_replacing_a_symlink_swaps_the_link_and_never_writes_through_it(self):
        self.serve_model("m-default")
        outside = self.tmp / "outside.gguf"
        outside.write_bytes(body("diffusion", "-bad"))
        (self.models / "diffusion").mkdir(parents=True)
        link = self.models / "diffusion" / "d.gguf"
        link.symlink_to(outside)
        done = self.go()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertFalse(link.is_symlink())
        self.assertEqual(link.read_bytes(), body("diffusion"))
        self.assertEqual(outside.read_bytes(), body("diffusion", "-bad"))  # the file behind the old link is not ours

    def test_a_models_from_link_replaces_a_wrong_existing_file_in_place(self):
        source = self.tmp / "tarkor"
        source.mkdir()
        for kind, entry in self.files_of("m-default").items():
            (source / entry["name"]).write_bytes(body(kind))
        (self.models / "vae").mkdir(parents=True)
        (self.models / "vae" / "v.safetensors").write_bytes(body("vae", "-bad"))
        done = self.go("--models-from", str(source))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        link = self.models / "vae" / "v.safetensors"
        self.assertTrue(link.is_symlink() and link.resolve() == (source / "v.safetensors").resolve())
        self.assertFalse(Path(str(link) + ".part").exists())

    def test_without_sha256sum_it_falls_back_to_shasum_and_without_both_it_stops(self):
        self.serve_model("m-default")
        only_shasum = self.path_without("sha256sum")
        done = self.go(PATH="%s:%s:%s" % (self.fakebin, self.home / ".local" / "bin", only_shasum))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual((self.models / "vae" / "v.safetensors").read_bytes(), body("vae"))
        self.serve_model("m-default", corrupt="vae")
        (self.models / "vae" / "v.safetensors").unlink()
        done = self.go(PATH="%s:%s:%s" % (self.fakebin, self.home / ".local" / "bin", only_shasum))
        self.assertEqual(done.returncode, 1)  # shasum really compares: a wrong sum is not "ok"
        self.assertIn("the sha256 of v.safetensors does not match", done.stderr)
        neither = self.path_without("sha256sum", "shasum")
        for lang, message in (("en", "sha256sum (or shasum) is missing"), ("es", "falta sha256sum (o shasum)")):
            done = self.go("--dry-run", GIMG_LANG=lang, PATH="%s:%s" % (self.fakebin, neither))
            self.assertEqual(done.returncode, 1, done.stdout)
            self.assertIn(message, done.stderr)
            self.assertNotIn("[2/6]", done.stdout)

    def test_a_models_from_file_with_another_sha_is_not_linked_and_the_file_is_downloaded(self):
        self.serve_model("m-default")
        source = self.tmp / "tarkor"
        source.mkdir()
        for kind, entry in self.files_of("m-default").items():
            (source / entry["name"]).write_bytes(body(kind, "-bad" if kind == "text" else ""))
        done = self.go("--models-from", str(source))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("does not match the catalog sha256; downloading", done.stdout)
        self.assertEqual(len(self.curl_calls()), 1)
        self.assertFalse((self.models / "text" / "t.gguf").is_symlink())
        self.assertTrue((self.models / "diffusion" / "d.gguf").is_symlink())

    def test_an_existing_file_with_another_sha_is_replaced_but_one_that_matches_is_never_touched(self):
        self.serve_model("m-default")
        (self.models / "diffusion").mkdir(parents=True)
        (self.models / "diffusion" / "d.gguf").write_bytes(body("diffusion", "-bad"))
        (self.models / "text").mkdir()
        good = self.models / "text" / "t.gguf"
        good.write_bytes(body("text"))
        before = good.stat().st_mtime_ns
        done = self.go()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("d.gguf does not match the catalog; replacing it", done.stdout)
        self.assertEqual((self.models / "diffusion" / "d.gguf").read_bytes(), body("diffusion"))
        self.assertEqual(good.stat().st_mtime_ns, before)
        self.assertEqual(len(self.curl_calls()), 2)

    def test_with_installs_the_optional_model_too(self):
        self.serve_model("m-default")
        self.serve_model("m-optional")
        done = self.go("--with", "m-optional")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.curl_calls()), 6)
        self.assertIn("model \"m-optional\": installed", done.stdout)

    def test_a_config_that_is_not_json_stops_before_the_doctor_and_is_left_alone(self):
        self.serve_model("m-default")
        (self.config / "config.json").write_text("{broken", encoding="utf-8")
        done = self.go()
        self.assertEqual(done.returncode, 1)
        self.assertIn("could not write %s/config.json" % self.config, done.stderr)
        self.assertEqual((self.config / "config.json").read_text(), "{broken")
        self.assertNotIn("[6/6]", done.stdout)


@unittest.skipUnless(shutil.which("unzip"), "needs unzip")
class EngineDownloadTests(FullRunBase):
    """The engine branch of step 3 with a fake zip (built here) in place of the real one, via a copy of the script."""

    ASSET = "fake-engine.zip"

    def setUp(self):
        super().setUp()
        self.engine = self.data / "engine" / engine_sdcpp.RELEASE
        shutil.rmtree(self.engine)
        archive = self.serve / self.ASSET
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("sd-cli", "#!/bin/sh\nexit 0\n")
            z.writestr("libggml.so", "ggml")
        self.zip_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.source = self.tmp / "tarkor"
        self.source.mkdir()
        for kind, entry in self.files_of("m-default").items():
            (self.source / entry["name"]).write_bytes(body(kind))
        self.copy = self.tmp / "repo-copy"
        self.copy.mkdir()
        os.symlink(ROOT / "gimg", self.copy / "gimg")  # the script finds gimg/ next to itself
        self.script_path = self.copy / "instalar.sh"

    def fix_zip(self, sha):
        text = SCRIPT.read_text(encoding="utf-8")
        text, count = re.subn(r'^SD_ZIP=".*"$', 'SD_ZIP="%s %s"' % (self.ASSET, sha), text, flags=re.M)
        self.assertEqual(count, 1)
        self.script_path.write_text(text, encoding="utf-8")

    def leftovers(self):
        return sorted(p.name for p in (self.data / "engine").iterdir() if ".tmp." in p.name or ".old." in p.name)

    def test_it_downloads_checks_extracts_marks_and_replaces_an_older_engine_cleanly(self):
        self.fix_zip(self.zip_sha)
        done = self.go("--models-from", str(self.source))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("Engine installed in %s" % self.engine, done.stdout)
        self.assertTrue(os.access(self.engine / "sd-cli", os.X_OK))
        self.assertEqual((self.engine / "libggml.so").read_text(), "ggml")
        self.assertEqual((self.engine / ".zip-sha256").read_text().strip(), self.zip_sha)
        self.assertEqual(self.leftovers(), [])
        self.assertTrue(any(c.endswith("/" + self.ASSET) and "-o" in c for c in self.curl_calls()), self.curl_calls())
        done = self.go("--models-from", str(self.source))  # same sum: nothing to do
        self.assertIn("already installed", done.stdout)
        self.assertEqual(len(self.curl_calls()), 1)
        (self.engine / "stale.txt").write_text("from the older engine")
        (self.engine / ".zip-sha256").write_text("0" * 64 + "\n")  # an engine of another zip: it must be replaced
        done = self.go("--models-from", str(self.source))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(self.curl_calls()), 2)
        self.assertFalse((self.engine / "stale.txt").exists())
        self.assertEqual((self.engine / ".zip-sha256").read_text().strip(), self.zip_sha)
        self.assertTrue(os.access(self.engine / "sd-cli", os.X_OK))
        self.assertEqual(self.leftovers(), [])

    def test_a_zip_with_the_wrong_sha_stops_and_keeps_the_previous_engine(self):
        self.fix_zip("1" * 64)
        self.engine.mkdir(parents=True)
        script(self.engine / "sd-cli", "exit 0")
        (self.engine / ".zip-sha256").write_text("0" * 64 + "\n")
        done = self.go("--models-from", str(self.source), GIMG_LANG="es")
        self.assertEqual(done.returncode, 1)
        self.assertIn("el sha256 del zip del motor no cuadra (esperado %s)" % ("1" * 64), done.stderr)
        self.assertEqual((self.engine / ".zip-sha256").read_text(), "0" * 64 + "\n")
        self.assertTrue(os.access(self.engine / "sd-cli", os.X_OK))
        self.assertEqual(self.leftovers(), [])
        self.assertFalse((self.models / "diffusion").exists())  # it stopped before the models


if __name__ == "__main__":
    unittest.main()
