"""F3.5: on-demand start of the service (`ensure_running`, `gimg ui`, `order submit`, `attempt new`); real subprocesses."""
import json
import os
import socket
import subprocess
import sys
import unittest
from unittest import mock

import gimg
from gimg import queue, service
from tests.test_service import NAME, ROOT, Env, alive, wait_until


class Autostart(Env):
    def setUp(self):
        super().setUp()
        self.env["GIMG_AUTOSTART"] = "1"
        self.project()
        self.order_file = self.tmp / "order.json"
        self.order_file.write_text(json.dumps(self.order()))

    def submit(self, *extra, env=None):
        return self.gimg("--json", "order", "submit", NAME, str(self.order_file), *extra, env=env)

    def port(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def use_port(self):
        self.env["GIMG_PORT"] = str(self.port())

    def test_submit_starts_the_service_and_the_worker_processes_it(self):
        self.use_port()
        done = self.submit()
        self.assertEqual(done.returncode, 0, done.stderr)
        view = json.loads(done.stdout)
        self.assertEqual(len(view["entries"]), 1)
        state = service.read_state()
        self.assertEqual(view["service"], {"running": True, "autostart": True, "url": state["url"],
                                           "pid": state["pid"]})
        self.assertEqual(state["port"], int(self.env["GIMG_PORT"]))
        self.assertTrue(wait_until(lambda: self.states() == ["done"], 30), self.states())
        # a second submit (and `attempt new`) reuses the same service
        again = json.loads(self.submit().stdout)
        self.assertEqual(again["service"]["pid"], state["pid"])
        new = self.gimg("--json", "attempt", "new", NAME, "fauna/lobo", "banner")
        self.assertEqual(new.returncode, 0, new.stderr)
        self.assertEqual(json.loads(new.stdout)["service"]["pid"], state["pid"])
        self.assertEqual(service.read_state()["pid"], state["pid"])

    def test_autostart_off_starts_nothing(self):
        self.use_port()
        env = dict(self.env, GIMG_AUTOSTART="0")
        done = self.submit(env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["service"], {"running": False, "autostart": False})
        self.assertEqual(self.states(), ["queued"])
        self.assertIsNone(service.read_state())
        self.assertFalse(service.lock_held())
        ui = self.gimg("ui", "--no-browser", env=env)
        self.assertEqual(ui.returncode, 1)
        self.assertIn("the service is not running", ui.stderr)

    def test_failed_start_leaves_the_entry_queued_with_a_warning_and_code_0(self):
        with socket.socket() as sock:  # something that is not gimg holds the port
            sock.bind(("127.0.0.1", 0))
            sock.listen()
            self.env["GIMG_PORT"] = str(sock.getsockname()[1])
            done = self.submit()
            self.assertEqual(done.returncode, 0, done.stderr)
            view = json.loads(done.stdout)
            self.assertEqual(view["service"]["running"], False)
            self.assertEqual(view["service"]["error"], "serve.start_failed")
            self.assertIn("is busy", view["service"]["message"])  # the last lines of serve.log
            self.assertIn("warning: the entry stays queued", done.stderr)
            self.assertIn("did not start in time", done.stderr)
            self.assertEqual(self.states(), ["queued"])
            text = self.submit("--draft", env=dict(self.env, GIMG_AUTOSTART="0"))
            self.assertEqual(text.returncode, 0, text.stderr)
            plain = self.gimg("order", "submit", NAME, str(self.order_file))
            self.assertEqual(plain.returncode, 0, plain.stderr)
            self.assertIn("Queued", plain.stdout)
            self.assertIn("did not start in time", plain.stderr)

    def test_other_version_without_a_worker_is_restarted(self):
        self.use_port()
        old = subprocess.Popen(
            [sys.executable, "-c", "import sys, gimg; gimg.__version__ = '0.0.0-old'; from gimg.cli import main; "
             "sys.exit(main(['serve', '--port', sys.argv[1]]))", self.env["GIMG_PORT"]],
            cwd=ROOT, env=self.env, stdout=subprocess.PIPE, text=True)
        self.addCleanup(old.stdout.close)
        self.addCleanup(old.kill)
        old.stdout.readline()
        self.assertEqual(service.read_state()["version"], "0.0.0-old")
        warnings = []
        with mock.patch.object(queue, "worker_alive", return_value=True):  # a worker: the old one stays
            state = service.ensure_running("en", warnings.append)
        self.assertEqual(state["pid"], old.pid)
        self.assertEqual(len(warnings), 1)
        self.assertIn("0.0.0-old", warnings[0])
        # no worker: the old one is stopped and a new one started
        ui = self.gimg("ui", "--no-browser", "--json")
        self.assertEqual(ui.returncode, 0, ui.stderr)
        new = json.loads(ui.stdout)
        self.assertNotEqual(new["pid"], old.pid)
        self.assertEqual(old.wait(timeout=15), 0)
        self.assertEqual(service.read_state()["pid"], new["pid"])
        self.assertNotEqual(service.read_state()["version"], "0.0.0-old")

    def test_same_version_but_older_code_is_restarted(self):
        """`arrancar.sh` after a `git pull`: same `__version__`, other code; the old service goes (F4e)."""
        self.use_port()
        old = subprocess.Popen(
            [sys.executable, "-c", "import sys, gimg; gimg.build_id = lambda: 'old-code'; from gimg.cli import main; "
             "sys.exit(main(['serve', '--port', sys.argv[1]]))", self.env["GIMG_PORT"]],
            cwd=ROOT, env=self.env, stdout=subprocess.PIPE, text=True)
        self.addCleanup(old.stdout.close)
        self.addCleanup(old.kill)
        old.stdout.readline()
        self.assertEqual(service.read_state()["build"], "old-code")
        warnings = []
        with mock.patch.object(queue, "worker_alive", return_value=True):  # a worker: the old one stays, and says why
            state = service.ensure_running("en", warnings.append)
        self.assertEqual(state["pid"], old.pid)
        self.assertEqual(len(warnings), 1)
        self.assertIn("+old-code", warnings[0])
        ui = self.gimg("ui", "--no-browser", "--json")
        self.assertEqual(ui.returncode, 0, ui.stderr)
        new = json.loads(ui.stdout)
        self.assertNotEqual(new["pid"], old.pid)
        self.assertEqual(old.wait(timeout=15), 0)
        self.assertEqual(service.read_state()["build"], gimg.build_id())

    def test_the_same_code_reuses_the_running_service(self):
        self.use_port()
        first = json.loads(self.gimg("ui", "--no-browser", "--json").stdout)
        again = json.loads(self.gimg("ui", "--no-browser", "--json").stdout)
        self.assertEqual(again["pid"], first["pid"])

    def test_two_clis_replacing_an_old_version_end_with_one_new_service(self):
        self.use_port()
        old = subprocess.Popen(
            [sys.executable, "-c", "import sys, gimg; gimg.__version__ = '0.0.0-old'; from gimg.cli import main; "
             "sys.exit(main(['serve', '--port', sys.argv[1]]))", self.env["GIMG_PORT"]],
            cwd=ROOT, env=self.env, stdout=subprocess.PIPE, text=True)
        self.addCleanup(old.stdout.close)
        self.addCleanup(old.kill)
        old.stdout.readline()
        args = [sys.executable, "-m", "gimg", "--lang", "en", "ui", "--no-browser", "--json"]
        procs = [subprocess.Popen(args, cwd=ROOT, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True) for _ in range(2)]
        results, errs = [], []
        for proc in procs:
            out, err = proc.communicate(timeout=60)
            self.assertEqual(proc.returncode, 0, err)
            results.append(json.loads(out))
            errs.append(err)
        # on a failure, say which pid is the old one, what each CLI warned and what the service log holds
        log = self.data / "serve.log"
        why = "old pid %d; results %r; stderr %r; serve.log:\n%s" % (old.pid, results, errs,
                                                                   log.read_text() if log.exists() else "")
        self.assertEqual(results[0]["pid"], results[1]["pid"], why)
        self.assertNotEqual(results[0]["pid"], old.pid)
        self.assertEqual(old.wait(timeout=15), 0)
        self.assertEqual(service.read_state()["pid"], results[0]["pid"])
        self.assertTrue(alive(results[0]["pid"]))

    def test_a_state_read_before_a_replacement_is_not_returned(self):
        """Another way the test above could end with the old record: this CLI read ``serve.json`` of the old service,
        another CLI replaced it on the same port, and the new one answered `/api/health` for it."""
        old = {"pid": 2 ** 22 + 1, "port": 1, "url": "http://127.0.0.1:1", "version": "0.0.0-old",
               "build": gimg.build_id(), "startedAt": "2026-11-06T13:08:35Z"}
        new = dict(old, pid=2 ** 22 + 2, version=gimg.__version__, startedAt="2026-11-06T13:08:36Z")
        answer = {"ok": True, "pid": new["pid"], "port": 1, "version": gimg.__version__, "build": gimg.build_id()}
        reads = iter([old])
        with mock.patch.object(service, "read_state", side_effect=lambda: next(reads, new)), \
                mock.patch.object(service, "lock_held", return_value=True), \
                mock.patch.object(service, "health", return_value=answer), \
                mock.patch.object(queue, "worker_alive", return_value=False), \
                mock.patch.object(service, "detach", side_effect=AssertionError("nothing to start")):
            state = service.ensure_running("en")
        self.assertEqual((state["pid"], state["version"]), (new["pid"], gimg.__version__))

    def test_a_probe_at_the_same_moment_is_not_a_worker_nor_a_service(self):
        """The real flake: CLI B probed ``worker.lock`` while CLI A (or the old service's `/api/health`) was probing
        it too, saw it taken and kept the old service with "a worker is alive". A probe holds the lock shared."""
        import fcntl
        self.data.mkdir(parents=True, exist_ok=True)
        for path, probe in ((queue.worker_lock_path(), queue.worker_alive), (service.lock_path(), service.lock_held)):
            fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)  # another probe in progress
                self.assertIs(probe(), False, path.name)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # the real holder
                self.assertIs(probe(), True, path.name)
            finally:
                os.close(fd)

    def test_autostart_values(self):
        for value, expected in (("0", False), ("FALSE", False), ("no", False), (" Off ", False), ("1", True),
                                ("", True)):
            with mock.patch.dict(os.environ, {"GIMG_AUTOSTART": value}):
                self.assertEqual(service.autostart_enabled(), expected, value)

    def test_ui_prints_the_url_and_leaves_the_service_alive(self):
        self.use_port()
        done = self.gimg("ui", "--no-browser")
        self.assertEqual(done.returncode, 0, done.stderr)
        state = service.read_state()
        self.assertIn("Interface at " + state["url"], done.stdout)
        self.assertTrue(service.lock_held())
        self.assertTrue(alive(state["pid"]))
        again = self.gimg("ui", "--no-browser", "--json")
        data = json.loads(again.stdout)
        self.assertEqual((data["pid"], data["opened"]), (state["pid"], False))
        self.assertEqual(self.gimg("serve", "--stop").returncode, 0)
        self.assertTrue(wait_until(self.stopped, 5))


if __name__ == "__main__":
    unittest.main()
