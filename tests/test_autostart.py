"""F3.5: on-demand start of the service (`ensure_running`, `gimg ui`, `order submit`, `attempt new`); real subprocesses."""
import json
import os
import socket
import subprocess
import sys
import unittest
from unittest import mock

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
        results = []
        for proc in procs:
            out, err = proc.communicate(timeout=60)
            self.assertEqual(proc.returncode, 0, err)
            results.append(json.loads(out))
        self.assertEqual(results[0]["pid"], results[1]["pid"])
        self.assertNotEqual(results[0]["pid"], old.pid)
        self.assertEqual(old.wait(timeout=15), 0)
        self.assertEqual(service.read_state()["pid"], results[0]["pid"])
        self.assertTrue(alive(results[0]["pid"]))

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
