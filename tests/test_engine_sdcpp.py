import json
import os
import signal
import stat
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from gimg import engine, engine_sdcpp, limits, models, orders, paths, queue, worker
from gimg.engine_sdcpp import SdCppEngine
from gimg.errors import GimgError
from tests.test_queue import QueueBase

FAKE = Path(__file__).resolve().parent / "fake_sd_cli.py"
MODEL = "flux2-klein-4b-q8"
REAL_LOG = (
    "[I] loading tensors completed, taking 1.81s (read: 1.49s) --- model_loader.cpp:1400\n"
    "  |######      |  34/298 - 679.53MB/s\x1b[K  |###########  |  60/298 - 713.05MB/s\x1b[K\r"
    "[I] loading tensors completed, taking 0.08s (read: 0.02s) --- model_loader.cpp:1400\n"
    "  |==================================================| 6/6 -  30.52s/it\x1b[K\n"
    "[I] sampling completed, taking 183.47s --- image.cpp:907\n"
    "[I] generating 1 latent images completed, taking 183.47s --- image.cpp:919\n"
    "[V] computing vae decode graph completed, taking 38.73s --- vae.hpp:384\n"
    "[I] decode_first_stage completed, taking 38.74s --- image.cpp:632\n"
    "[I] generate_image completed in 225.60s --- image.cpp:1058\n")


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:  # a zombie nobody reaped is dead too
        with open("/proc/%d/stat" % pid) as fh:
            return fh.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return True


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.models_home = self.tmp / "mod els"  # a space on purpose
        env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(self.tmp / "cfg"), "GIMG_DATA_HOME": str(self.tmp / "data"),
            "GIMG_MODELS_HOME": str(self.models_home), "GIMG_SD_CLI": str(FAKE),
            "LD_LIBRARY_PATH": "/somewhere/else"})
        env.start()
        self.addCleanup(env.stop)
        for var in ("GIMG_ENGINE", "GIMG_MACHINE_PROFILE", "FAKE_SD_ARGV", "FAKE_SD_SLEEP", "FAKE_SD_CHILD_PID",
                    "FAKE_SD_FAIL", "FAKE_SD_NO_IMAGE", "FAKE_SD_NO_TIMES"):
            os.environ.pop(var, None)
        self.install(MODEL)
        self.argv_file = self.tmp / "argv.json"
        self.machine = limits.load_machine("steam-deck")

    def install(self, model_id):
        for kind, entry in models.load_catalog()["models"][model_id]["files"].items():
            path = self.models_home / kind / entry["name"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    def env(self, **kw):
        patcher = mock.patch.dict(os.environ, kw)
        patcher.start()
        self.addCleanup(patcher.stop)

    def job(self, **kw):
        base = dict(prompt="a cat", width=64, height=32, seed=7, model=MODEL,
                    output=str(self.tmp / "out dir" / ".pending-5.png"))
        base.update(kw)
        return engine.EngineJob(**base)

    def run_job(self, machine=None, **kw):
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        eng = SdCppEngine(self.machine if machine is None else machine, poll_s=0.05, kill_grace_s=2)
        job = self.job(**kw)
        return eng, job, eng.generate(job, lambda: False)

    def argv(self):
        return json.loads(self.argv_file.read_text())["argv"]

    def md(self, kind):
        return str(self.models_home / kind / models.load_catalog()["models"][MODEL]["files"][kind]["name"])


class ArgvTests(Base):
    def expected(self, job_out, *, tail_before=(), refs=(), steps="6", cfg="1", sampler="euler", prompt="a cat",
                 machine_part=("--params-backend", "disk", "--max-vram", "vulkan0=2")):
        out = Path(job_out)
        return (["--diffusion-model", self.md("diffusion"), "--llm", self.md("text"), "--vae", self.md("vae"),
                 "-p", prompt, "--cfg-scale", cfg, "--steps", steps, "--sampling-method", sampler,
                 "-W", "64", "-H", "32", "--seed", "7", *machine_part,
                 "--flash-attn", "off,diffusion=on", "--vae-tiling", *tail_before,
                 *[x for r in refs for x in ("-r", r)],
                 "--preview", "proj", "--preview-interval", "1",
                 "--preview-path", str(out.with_suffix(".preview.png")), "-o", str(out), "-v"])

    def test_exact_argv_with_machine_overrides_and_catalog_defaults(self):
        _, job, _ = self.run_job()
        argv = self.argv()
        self.assertEqual(argv[0], str(FAKE))
        self.assertEqual(argv[1:], self.expected(job.output))

    def test_exact_argv_without_machine_overrides(self):
        _, job, _ = self.run_job(machine={"timeoutS": 60})
        self.assertEqual(self.argv()[1:], self.expected(job.output, machine_part=()))

    def test_threads_and_references_and_job_values(self):
        machine = {"timeoutS": 60, "engine": {"threads": 4, "maxVram": "vulkan0=1"}}
        refs = [str(self.tmp / "my refs" / "a.png"), str(self.tmp / "b.png")]
        _, job, _ = self.run_job(machine=machine, references=refs, steps=3, cfg=2.5, sampler="dpm++2m")
        want = self.expected(job.output, refs=refs, steps="3", cfg="2.5", sampler="dpm++2m",
                             machine_part=("--max-vram", "vulkan0=1", "-t", "4"))
        self.assertEqual(self.argv()[1:], want)

    def test_machine_model_args_come_after_catalog_args_and_threads(self):
        machine = {"timeoutS": 60, "engine": {"threads": 2, "models": {MODEL: {"args": ["-t", "8"]}}}}
        _, job, _ = self.run_job(machine=machine)
        argv = self.argv()
        self.assertEqual(argv.index("-t"), argv.index("2") - 1)
        self.assertEqual(argv[argv.index("--vae-tiling") + 1:argv.index("--vae-tiling") + 3], ["-t", "8"])

    def test_job_machine_beats_constructor_machine(self):
        self.env(FAKE_SD_ARGV=str(self.argv_file))
        SdCppEngine({"timeoutS": 60}, poll_s=0.05).generate(self.job(machine=self.machine), lambda: False)
        self.assertIn("--max-vram", self.argv())
        SdCppEngine(self.machine, poll_s=0.05).generate(self.job(machine={"timeoutS": 9}), lambda: False)
        self.assertNotIn("--max-vram", self.argv())

    def test_awkward_prompt_goes_through_unchanged(self):
        prompt = "a \"quoted\" cat's $HOME `ls` --steps 99  spaced\nnew line; -W 1"
        _, job, _ = self.run_job(prompt=prompt)
        self.assertEqual(self.argv()[1:], self.expected(job.output, prompt=prompt))

    def test_paths_with_spaces(self):
        _, job, res = self.run_job(output=str(self.tmp / "a b" / "c d" / ".pending-9.png"))
        self.assertEqual(self.argv()[-1], "-v")
        self.assertEqual(Path(self.argv()[self.argv().index("-o") + 1]), Path(job.output))
        self.assertTrue(Path(job.output).is_file())
        self.assertIn(" ", self.md("diffusion"))
        self.assertEqual(self.argv()[self.argv().index("--diffusion-model") + 1], self.md("diffusion"))

    def test_command_has_relative_model_paths(self):
        _, job, res = self.run_job()
        cat = models.load_catalog()["models"][MODEL]["files"]
        self.assertEqual(res.command[0], "sd-cli")
        self.assertEqual(res.command[res.command.index("--diffusion-model") + 1], "diffusion/" + cat["diffusion"]["name"])
        self.assertEqual(res.command[res.command.index("--llm") + 1], "text/" + cat["text"]["name"])
        self.assertEqual(res.command[res.command.index("--vae") + 1], "vae/" + cat["vae"]["name"])
        self.assertNotIn(str(self.models_home), " ".join(res.command))
        self.assertEqual(res.command[1:res.command.index("--diffusion-model")], [])
        self.assertEqual(res.command[res.command.index("-p"):], self.argv()[self.argv().index("-p"):])

    def test_ld_library_path_is_the_binary_folder(self):
        self.run_job()
        self.assertEqual(json.loads(self.argv_file.read_text())["ld_library_path"], str(FAKE.parent))

    def test_invalid_size(self):
        eng = SdCppEngine(self.machine)
        with self.assertRaises(engine.EngineError) as cm:
            eng.generate(self.job(width=None), lambda: False)
        self.assertIn("invalid size", cm.exception.message)


class ModelTests(Base):
    def gen(self, **kw):
        return SdCppEngine(self.machine, poll_s=0.05).generate(self.job(**kw), lambda: False)

    def test_unknown_model(self):
        with self.assertRaises(GimgError) as cm:
            self.gen(model="nope")
        self.assertEqual((cm.exception.code, cm.exception.params["model"]), ("model.unknown", "nope"))

    def test_no_model(self):
        for value in (None, ""):
            with self.assertRaises(GimgError) as cm:
                self.gen(model=value)
            self.assertEqual(cm.exception.code, "model.required")
            self.assertIn(MODEL, cm.exception.params["known"])

    def test_not_installed_says_which_file_and_how_to_install(self):
        other = "flux3-klein-q8"
        with self.assertRaises(GimgError) as cm:
            self.gen(model=other)
        err = cm.exception
        self.assertEqual(err.code, "model.not_installed")
        self.assertEqual(err.params["command"], "instalar.sh --with " + other)
        self.assertIn("flux3-image-klein-Q8_0.gguf", err.params["files"])
        self.assertIn("instalar.sh --with flux3-klein-q8", err.message("en"))
        self.assertFalse(Path(self.job().output).exists())  # the engine never started

    def test_one_missing_file_is_enough(self):
        vae = Path(self.md("vae"))
        vae.unlink()
        with self.assertRaises(GimgError) as cm:
            self.gen()
        self.assertEqual(cm.exception.code, "model.not_installed")
        self.assertEqual(cm.exception.params["files"], str(vae))


class BinaryTests(Base):
    def gen(self):
        return SdCppEngine(self.machine, poll_s=0.05).generate(self.job(), lambda: False)

    def test_missing_binary(self):
        self.env(GIMG_SD_CLI=str(self.tmp / "nope" / "sd-cli"))
        with self.assertRaises(GimgError) as cm:
            self.gen()
        self.assertEqual((cm.exception.code, cm.exception.params["path"]),
                         ("engine.binary_missing", str(self.tmp / "nope" / "sd-cli")))

    def test_binary_without_execute_permission(self):
        plain = self.tmp / "sd-cli"
        plain.write_text("#!/bin/sh\n")
        plain.chmod(stat.S_IRUSR | stat.S_IWUSR)
        self.env(GIMG_SD_CLI=str(plain))
        with self.assertRaises(GimgError) as cm:
            self.gen()
        self.assertEqual(cm.exception.code, "engine.binary_not_executable")

    def test_binary_resolution_order(self):
        machine = {"engine": {"sdCli": "/from/profile/sd-cli"}}
        self.assertEqual(engine_sdcpp.binary_path(machine), Path(str(FAKE)))  # GIMG_SD_CLI wins
        os.environ.pop("GIMG_SD_CLI")
        self.assertEqual(engine_sdcpp.binary_path(machine), Path("/from/profile/sd-cli"))
        self.assertEqual(engine_sdcpp.binary_path({}),
                         self.tmp / "data" / "engine" / engine_sdcpp.RELEASE / "sd-cli")
        self.assertEqual(engine_sdcpp.RELEASE, "master-1000-95ff762")


class RunTests(Base):
    def make(self, machine=None, **kw):
        return SdCppEngine(self.machine if machine is None else machine, poll_s=0.05, kill_grace_s=2, **kw)

    def test_result_fields_and_times_from_the_log(self):
        _, job, res = self.run_job()
        self.assertEqual((res.engine_version, res.load_ms, res.sample_ms, res.decode_ms),
                         ("master-1000-95ff762", 1750, 4800, 750))
        self.assertEqual(res.min_free_mb, None)
        self.assertGreaterEqual(res.duration_ms, 0)
        self.assertEqual(Path(res.log_path), Path(job.output).with_suffix(".log"))
        self.assertIn("sampling completed", Path(res.log_path).read_text())
        self.assertEqual(Path(job.output).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_log_without_timing_lines(self):
        self.env(FAKE_SD_NO_TIMES="1")
        _, job, res = self.run_job()
        self.assertEqual((res.load_ms, res.sample_ms, res.decode_ms), (None, None, None))

    def test_parse_timings_on_the_real_format(self):
        self.assertEqual(engine_sdcpp.parse_timings(REAL_LOG),
                         {"load_ms": 1890, "sample_ms": 183470, "decode_ms": 38740})
        self.assertEqual(engine_sdcpp.parse_timings(""), {"load_ms": None, "sample_ms": None, "decode_ms": None})

    def test_exit_code_gives_the_last_five_lines(self):
        self.env(FAKE_SD_FAIL="\n".join("line%d" % n for n in range(1, 9)))
        with self.assertRaises(engine.EngineError) as cm:
            self.run_job()
        msg = cm.exception.message
        self.assertIn("exited with code 3", msg)
        self.assertEqual([ln for ln in msg.splitlines() if ln.startswith("line")],
                         ["line%d" % n for n in range(4, 9)])
        self.assertNotIn("line3", msg)
        self.assertNotIsInstance(cm.exception, engine.EngineTimeout)

    def test_missing_png_is_an_error_with_its_reason(self):
        self.env(FAKE_SD_NO_IMAGE="1")
        with self.assertRaises(engine.EngineError) as cm:
            self.run_job()
        self.assertIn("without writing the image", cm.exception.message)
        self.assertNotIn("exited with code", cm.exception.message)

    def test_stale_image_does_not_pass_for_the_new_one(self):
        out = Path(self.job().output)
        out.parent.mkdir(parents=True)
        out.write_bytes(b"\x89PNG\r\n\x1a\nstale")
        self.env(FAKE_SD_NO_IMAGE="1")
        with self.assertRaises(engine.EngineError):
            self.run_job()
        self.assertFalse(out.exists())

    def test_not_a_png_is_an_error(self):
        with mock.patch.object(SdCppEngine, "_is_png", return_value=False):
            with self.assertRaises(engine.EngineError):
                self.run_job()

    def test_cancel_kills_the_whole_group(self):
        pid_file = self.tmp / "child.pid"
        self.env(FAKE_SD_SLEEP="30", FAKE_SD_CHILD_PID=str(pid_file))
        t0 = time.monotonic()
        with self.assertRaises(engine.Cancelled):
            self.make().generate(self.job(), lambda: pid_file.exists())
        self.assertLess(time.monotonic() - t0, 10)
        child = int(pid_file.read_text())
        for _ in range(50):
            if not alive(child):
                break
            time.sleep(0.1)
        self.assertFalse(alive(child), "the child of sd-cli survived the cancel")

    def test_timeout_comes_from_the_model_then_the_profile_then_the_job(self):
        self.env(FAKE_SD_SLEEP="30")
        machine = {"timeoutS": 0.3}
        for kw in ({}, {"timeout_s": 99}):  # the profile wins over the job
            t0 = time.monotonic()
            with self.assertRaises(engine.EngineTimeout):
                self.make(machine).generate(self.job(**kw), lambda: False)
            self.assertLess(time.monotonic() - t0, 10)
        machine = {"timeoutS": 99, "engine": {"models": {MODEL: {"timeoutS": 0.3}}}}  # the model beats the profile
        with self.assertRaises(engine.EngineTimeout) as cm:
            self.make(machine).generate(self.job(), lambda: False)
        self.assertEqual(cm.exception.message, engine.TIMEOUT_MESSAGE)
        with self.assertRaises(engine.EngineTimeout):  # the job only when the profile has none
            self.make({}).generate(self.job(timeout_s=0.3), lambda: False)

    def test_timeout_kills_the_child_too(self):
        pid_file = self.tmp / "child.pid"
        self.env(FAKE_SD_SLEEP="30", FAKE_SD_CHILD_PID=str(pid_file))
        with self.assertRaises(engine.EngineTimeout):
            self.make({"timeoutS": 0.6}).generate(self.job(), lambda: False)
        child = int(pid_file.read_text())
        for _ in range(50):
            if not alive(child):
                break
            time.sleep(0.1)
        self.assertFalse(alive(child))

    def test_timeout_none_zero_or_negative_means_no_limit(self):
        self.env(FAKE_SD_SLEEP="0.4")
        for value in (None, 0, -5):
            res = self.make({}).generate(self.job(timeout_s=value), lambda: False)
            self.assertEqual(res.engine_version, engine_sdcpp.RELEASE)

    def test_tick_hook_runs_and_an_error_in_it_kills_the_process(self):
        pid_file = self.tmp / "child.pid"
        self.env(FAKE_SD_SLEEP="30", FAKE_SD_CHILD_PID=str(pid_file))
        ticks = []

        class Hooked(SdCppEngine):
            def _on_tick(self, proc, log_path, job):
                ticks.append(proc.pid)
                if len(ticks) == 3 and pid_file.exists():
                    raise RuntimeError("hook failed")

        with self.assertRaises(RuntimeError):
            Hooked(self.machine, poll_s=0.05, kill_grace_s=2).generate(self.job(), lambda: False)
        self.assertGreaterEqual(len(ticks), 3)
        child = int(pid_file.read_text())
        for _ in range(50):
            if not alive(child):
                break
            time.sleep(0.1)
        self.assertFalse(alive(child))

    def test_windows_fallback_terminates_only_the_process(self):
        proc = mock.Mock()
        proc.pid = 123
        proc.wait.return_value = 0
        with mock.patch.object(engine_sdcpp, "_POSIX", False), \
                mock.patch.object(engine_sdcpp.os, "killpg", create=True) as killpg:
            self.make()._kill(proc)
        killpg.assert_not_called()
        proc.terminate.assert_called_once_with()
        proc.kill.assert_not_called()


class GetEngineTests(Base):
    def config(self, text):
        path = self.tmp / "cfg" / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_default_is_fake(self):
        self.assertIsInstance(engine.get_engine(), engine.FakeEngine)

    def test_env_sdcpp(self):
        self.env(GIMG_ENGINE="sdcpp")
        eng = engine.get_engine()
        self.assertIsInstance(eng, SdCppEngine)
        self.assertEqual((eng.provider, eng.machine["name"]), ("stable-diffusion.cpp", "steam-deck"))
        self.assertIn(MODEL, eng.catalog["models"])

    def test_config_file_sdcpp_and_env_beats_it(self):
        self.config('{"engine": "sdcpp"}')
        self.assertIsInstance(engine.get_engine(), SdCppEngine)
        self.env(GIMG_ENGINE="fake")
        self.assertIsInstance(engine.get_engine(), engine.FakeEngine)

    def test_config_without_engine_key_or_with_other_keys(self):
        self.config('{"machineProfile": "steam-deck"}')
        self.assertIsInstance(engine.get_engine(), engine.FakeEngine)
        self.config('[1]')
        self.assertIsInstance(engine.get_engine(), engine.FakeEngine)

    def test_unknown_value_in_the_config_file(self):
        self.config('{"engine": "comfy"}')
        with self.assertRaises(GimgError) as cm:
            engine.get_engine()
        self.assertEqual((cm.exception.code, cm.exception.params["engine"]), ("engine.unknown", "comfy"))
        self.assertNotIn("solo existe", cm.exception.message("es"))
        self.assertIn("sdcpp", cm.exception.message("en"))

    def test_unreadable_config_file(self):
        self.config("{not json")
        with self.assertRaises(GimgError) as cm:
            engine.get_engine()
        self.assertEqual(cm.exception.code, "machine.config_unreadable")


class WorkerTests(QueueBase):
    def setUp(self):
        super().setUp()
        env = mock.patch.dict(os.environ, {
            "GIMG_MODELS_HOME": str(self.tmp / "models"), "GIMG_SD_CLI": str(FAKE), "GIMG_ENGINE": "sdcpp"})
        env.start()
        self.addCleanup(env.stop)
        for kind, entry in models.load_catalog()["models"][MODEL]["files"].items():
            (self.tmp / "models" / kind).mkdir(parents=True, exist_ok=True)
            (self.tmp / "models" / kind / entry["name"]).touch()

    def attempts_dir(self):
        return orders.pending_image_path("proj", "a", "banner", 1).parent

    def test_success_keeps_the_log_next_to_the_image(self):
        self.push()
        self.assertEqual(worker.run(), 1)
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]), ("done", None))
        names = sorted(p.name for p in self.attempts_dir().iterdir())
        self.assertEqual(names, ["q1.log", "q1.png"])
        self.assertIn("sampling completed", (self.attempts_dir() / "q1.log").read_text())

    def test_failure_leaves_no_pending_log_and_reports_the_motive(self):
        self.push()
        with mock.patch.dict(os.environ, {"FAKE_SD_FAIL": "vk: out of device memory"}):
            worker.run()
        entry = queue.get(1)
        self.assertEqual((entry["state"], entry["error"]["code"]), ("failed", "engine.failed"))
        self.assertIn("vk: out of device memory", entry["error"]["params"]["message"])
        self.assertEqual(list(self.attempts_dir().iterdir()) if self.attempts_dir().exists() else [], [])

    def test_recovery_removes_the_pending_log_and_preview(self):
        self.push()
        entry = queue.claim()
        folder = self.attempts_dir()
        folder.mkdir(parents=True, exist_ok=True)
        for name in (".pending-1.png", ".pending-1.log", ".pending-1.preview.png", "q9.log"):
            (folder / name).write_bytes(b"x")
        queue.recover_orphans()
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["q9.log"])


if __name__ == "__main__":
    unittest.main()
