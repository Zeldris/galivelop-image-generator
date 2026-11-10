"""F3.4: `gimg serve` (lock, state file, stop, idleness) and the worker it launches; real subprocesses, the fake engine."""
import contextlib
import copy
import fcntl
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from gimg import paths, queue, service, worker
from gimg.errors import GimgError

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = json.loads((ROOT / "examples" / "galivelop-images.json").read_text())
ORDER = json.loads((ROOT / "examples" / "order.json").read_text())
NAME = EXAMPLE["name"]


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def wait_until(check, seconds=15.0, step=0.05):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(step)
    return check()


class Env(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.config, self.data = self.tmp / "config", self.tmp / "data"
        self.env = dict(os.environ, GIMG_CONFIG_HOME=str(self.config), GIMG_DATA_HOME=str(self.data),
                        GIMG_ENGINE="fake", GIMG_SERVE_IDLE_S="0", GIMG_AUTOSTART="0")
        for name in ("GIMG_PORT", "GIMG_FAKE_DELAY", "GIMG_FAKE_FAIL", "GIMG_DEBUG"):
            self.env.pop(name, None)
        patcher = mock.patch.dict(os.environ, {k: self.env[k] for k in
                                               ("GIMG_CONFIG_HOME", "GIMG_DATA_HOME", "GIMG_ENGINE")})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.kill_service)

    def kill_service(self):
        pids = []
        with contextlib.suppress(Exception):
            pids = [e["pid"] for e in json.loads((self.data / "queue.json").read_text())["entries"]
                    if e["state"] == "running" and isinstance(e.get("pid"), int)]
        for pid in pids:  # a launched `gimg work` that outlived a failing test
            if alive(pid):
                with contextlib.suppress(OSError):
                    os.kill(pid, signal.SIGKILL)
        state = service.read_state()
        if state is not None and alive(state["pid"]):
            os.kill(state["pid"], signal.SIGKILL)
            wait_until(lambda: not alive(state["pid"]), 5)

    def gimg(self, *args, env=None, timeout=30):
        return subprocess.run([sys.executable, "-m", "gimg", "--lang", "en", *args], cwd=ROOT, env=env or self.env,
                              capture_output=True, text=True, timeout=timeout)

    def start(self, *extra):
        done = self.gimg("serve", "--detach", "--port", "0", "--json", *extra)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def stopped(self):
        return not service.state_path().exists() and not service.lock_held()

    def call(self, state, path, body=None):
        req = urllib.request.Request(state["url"] + path, method="GET" if body is None else "POST",
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers={} if body is None else {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    def project(self):
        root = self.tmp / "proj"
        (root / "refs").mkdir(parents=True)
        (root / "refs" / "wolf.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        cfg = copy.deepcopy(EXAMPLE)
        cfg.pop("$schema", None)
        (root / "galivelop-images.json").write_text(json.dumps(cfg))
        self.assertEqual(self.gimg("project", "add", str(root)).returncode, 0)

    def order(self, key="fauna/lobo", count=1):
        return dict(ORDER, key=key, profile="banner", count=count)

    def entries(self):
        return json.loads(self.gimg("--json", "queue", "list").stdout)

    def states(self):
        return [e["state"] for e in self.entries()]


class ServeCommand(Env):
    def test_lifecycle_lock_state_file_and_stop(self):
        state = self.start()
        mode = service.state_path().stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)
        self.assertEqual(json.loads(service.state_path().read_text()), state)
        self.assertEqual(sorted(state), ["build", "pid", "port", "startedAt", "url", "version"])
        self.assertEqual(self.call(state, "/api/health")["pid"], state["pid"])
        self.assertTrue(service.lock_held())
        # --status with a service
        status = self.gimg("serve", "--status", "--json")
        self.assertEqual(status.returncode, 0)
        self.assertEqual(json.loads(status.stdout), dict(state, running=True))
        self.assertIn(state["url"], self.gimg("serve", "--status").stdout)
        # a second one is refused, in the foreground and detached, with the URL
        for extra in ((), ("--detach",)):
            again = self.gimg("serve", "--port", "0", *extra)
            self.assertEqual(again.returncode, 1)
            self.assertIn("already running at " + state["url"], again.stderr)
        self.assertEqual(json.loads(service.state_path().read_text()), state)
        # --stop: SIGTERM, serve.json removed, lock released
        stopped = self.gimg("serve", "--stop")
        self.assertEqual(stopped.returncode, 0, stopped.stderr)
        self.assertTrue(wait_until(self.stopped, 5))
        self.assertTrue(wait_until(lambda: not alive(state["pid"]), 3))
        # nothing left to stop or to report
        again = self.gimg("serve", "--stop")
        self.assertEqual(again.returncode, 1)
        self.assertIn("the service is not running", again.stderr)
        status = self.gimg("serve", "--status")
        self.assertEqual((status.returncode, status.stdout.strip()), (1, "The service is not running."))
        self.assertEqual(json.loads(self.gimg("serve", "--status", "--json").stdout), {"running": False})

    def test_sigterm_deletes_the_state_file(self):
        state = self.start()
        os.kill(state["pid"], signal.SIGTERM)
        self.assertTrue(wait_until(self.stopped, 5))

    def test_foreground_stops_on_sigint(self):
        proc = subprocess.Popen([sys.executable, "-m", "gimg", "--lang", "en", "serve", "--port", "0"], cwd=ROOT,
                                env=self.env, stdout=subprocess.PIPE, text=True)
        self.addCleanup(proc.kill)
        self.addCleanup(proc.stdout.close)
        line = proc.stdout.readline()
        self.assertIn("Service at http://127.0.0.1:", line)
        self.assertTrue(service.lock_held())
        proc.send_signal(signal.SIGINT)
        self.assertEqual(proc.wait(timeout=15), 0)
        self.assertTrue(self.stopped())

    def test_state_file_without_a_lock_is_ignored_and_overwritten(self):
        service.state_path().parent.mkdir(parents=True)
        service.state_path().write_text(json.dumps({"pid": 2 ** 22 + 1, "port": 1, "url": "http://127.0.0.1:1",
                                                    "version": "0", "startedAt": "x"}))
        status = self.gimg("serve", "--status")
        self.assertEqual(status.returncode, 1)
        self.assertEqual(self.gimg("serve", "--stop").returncode, 1)
        state = self.start()
        self.assertNotEqual(state["port"], 1)
        self.assertEqual(json.loads(service.state_path().read_text()), state)

    def test_busy_port(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen()
            port = sock.getsockname()[1]
            done = self.gimg("serve", "--port", str(port))
            self.assertEqual(done.returncode, 1)
            self.assertIn("port %d is busy" % port, done.stderr)
            self.assertFalse(service.state_path().exists())
            self.assertFalse(service.lock_held())
            detached = self.gimg("serve", "--detach", "--port", str(port))
            self.assertEqual(detached.returncode, 1)
            self.assertIn("did not start in time", detached.stderr)
            self.assertIn("is busy", detached.stderr)  # the last lines of serve.log

    def test_bad_values(self):
        self.assertIn("invalid port", self.gimg("serve", "--port", "70000").stderr)
        env = dict(self.env, GIMG_SERVE_IDLE_S="soon")
        self.assertIn("invalid idle time", self.gimg("serve", "--port", "0", env=env).stderr)


class Settings(Env):
    def test_port_precedence(self):
        self.assertEqual(service.resolve_port(), 8737)
        self.config.mkdir(parents=True)
        (self.config / "config.json").write_text(json.dumps({"serve": {"port": 9001, "idleMinutes": 3}}))
        self.assertEqual(service.resolve_port(), 9001)
        with mock.patch.dict(os.environ, {"GIMG_PORT": "9002"}):
            self.assertEqual(service.resolve_port(), 9002)
            self.assertEqual(service.resolve_port(0), 0)
        self.assertEqual(service.resolve_idle_s(), 180)
        self.assertEqual(service.resolve_idle_s(7), 420)
        with mock.patch.dict(os.environ, {"GIMG_SERVE_IDLE_S": "1.5"}):
            self.assertEqual(service.resolve_idle_s(7), 1.5)
        (self.config / "config.json").write_text(json.dumps({"serve": {"port": "x"}}))
        with self.assertRaises(GimgError) as ctx:
            service.resolve_port()
        self.assertEqual(ctx.exception.code, "serve.bad_port")
        self.assertEqual(service.resolve_idle_s(), 900)


class Idle(Env):
    def test_stops_by_itself_when_idle(self):
        env = dict(self.env, GIMG_SERVE_IDLE_S="1")
        done = self.gimg("serve", "--detach", "--port", "0", "--json", env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        state = json.loads(done.stdout)
        self.assertTrue(wait_until(self.stopped, 6))
        self.assertTrue(wait_until(lambda: not alive(state["pid"]), 3))

    def test_requests_keep_it_alive(self):
        env = dict(self.env, GIMG_SERVE_IDLE_S="1.5")
        state = json.loads(self.gimg("serve", "--detach", "--port", "0", "--json", env=env).stdout)
        end = time.monotonic() + 3
        while time.monotonic() < end:
            self.call(state, "/api/health")
            time.sleep(0.3)
        self.assertTrue(service.lock_held())
        self.assertTrue(wait_until(self.stopped, 6))

    def test_does_not_stop_with_a_worker_or_a_queued_entry(self):
        self.project()
        order = self.tmp / "order.json"
        order.write_text(json.dumps(self.order()))
        # the test holds the worker lock: a worker "is alive", so nothing is launched and the service must stay
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(lambda: os.close(fd) if fd is not None else None)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.assertEqual(self.gimg("order", "submit", NAME, str(order)).returncode, 0)
        env = dict(self.env, GIMG_SERVE_IDLE_S="1")
        state = json.loads(self.gimg("serve", "--detach", "--port", "0", "--json", env=env).stdout)
        # well past the idle time (1 s) and two beats: it is still there because of the worker lock and the entry
        quiet = wait_until(lambda: not alive(state["pid"]) or not service.lock_held(), 3.5)
        self.assertFalse(quiet)
        self.assertTrue(alive(state["pid"]) and service.lock_held())
        self.assertEqual(self.states(), ["queued"])
        self.assertTrue(self.call(state, "/api/health")["worker"])
        # the worker "dies": the service launches a real one, the entry gets done and only then it stops
        os.close(fd)
        fd = None
        self.assertTrue(wait_until(lambda: self.states() == ["done"], 20), self.states())
        self.assertTrue(wait_until(self.stopped, 10))


class Worker(Env):
    def test_api_enqueue_is_processed_by_the_launched_worker(self):
        self.project()
        state = self.start()
        self.assertFalse(self.call(state, "/api/health")["worker"])
        done = self.call(state, "/api/projects/%s/orders" % NAME, self.order(count=2))
        self.assertEqual(len(done["entries"]), 2)
        self.assertTrue(wait_until(lambda: self.states() == ["done", "done"], 20), self.states())
        self.assertTrue((self.data / "worker.log").exists())
        self.assertTrue(wait_until(lambda: not queue.worker_alive(), 10))

    def test_stopping_the_service_does_not_kill_the_worker(self):
        self.project()
        env = dict(self.env, GIMG_FAKE_DELAY="2.5")
        self.env = env
        state = self.start()
        self.call(state, "/api/projects/%s/orders" % NAME, self.order())
        running = wait_until(lambda: next((e for e in self.entries() if e["state"] == "running"), None), 15)
        self.assertTrue(running)
        pid = running["pid"]
        self.addCleanup(lambda: os.kill(pid, signal.SIGKILL) if alive(pid) else None)
        self.assertNotEqual(pid, state["pid"])
        self.assertEqual(self.gimg("serve", "--stop").returncode, 0)
        self.assertTrue(wait_until(self.stopped, 5))
        self.assertTrue(alive(pid))
        self.assertEqual(self.states(), ["running"])
        self.assertTrue(wait_until(lambda: self.states() == ["done"], 20), self.states())


class Launching(Env):
    """`maybe_launch_worker` in-process, with `Popen` replaced."""

    def setUp(self):
        super().setUp()
        self.project()
        order = self.tmp / "order.json"
        order.write_text(json.dumps(self.order()))
        self.assertEqual(self.gimg("order", "submit", NAME, str(order)).returncode, 0)

    def test_two_kicks_launch_one_worker(self):
        proc = mock.Mock()
        proc.poll.return_value = None
        launcher = service._Launcher("en")
        with mock.patch.object(service.subprocess, "Popen", return_value=proc) as popen:
            self.assertTrue(service.maybe_launch_worker(launcher))
            self.assertFalse(service.maybe_launch_worker(launcher))
        popen.assert_called_once()
        args, kwargs = popen.call_args
        self.assertEqual(args[0], [sys.executable, "-m", "gimg", "work", "--lang", "en"])
        self.assertTrue(kwargs["start_new_session"])

    def test_threads_racing_launch_one_worker(self):
        import threading
        proc = mock.Mock()
        proc.poll.return_value = None
        launcher = service._Launcher("en")
        with mock.patch.object(service.subprocess, "Popen", return_value=proc) as popen:
            threads = [threading.Thread(target=service.maybe_launch_worker, args=(launcher,)) for _ in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        self.assertEqual(popen.call_count, 1)

    def test_a_queue_error_is_reported_once(self):
        launcher = service._Launcher("en")
        with mock.patch.object(queue, "list_entries", side_effect=GimgError("queue.corrupt", path="q")), \
                mock.patch("sys.stderr") as err:
            for _ in range(3):
                self.assertFalse(service.maybe_launch_worker(launcher))
        self.assertEqual(err.write.call_count, 2)  # one print = text + newline

    def test_an_entry_left_running_by_a_dead_worker_is_recovered_and_launches(self):
        data = json.loads((self.data / "queue.json").read_text())
        data["entries"][0].update(state="running", pid=2 ** 22 + 1)
        (self.data / "queue.json").write_text(json.dumps(data))
        with mock.patch.object(service.subprocess, "Popen") as popen:
            self.assertTrue(service.maybe_launch_worker(service._Launcher("en")))
        popen.assert_called_once()

    def test_unknown_lock_state_launches_nothing(self):
        with mock.patch.object(service.subprocess, "Popen") as popen, \
                mock.patch.object(queue, "worker_alive", return_value=None):
            self.assertFalse(service.maybe_launch_worker(service._Launcher("en")))
        popen.assert_not_called()

    def test_nothing_queued_launches_nothing(self):
        self.assertEqual(self.gimg("work").returncode, 0)
        with mock.patch.object(service.subprocess, "Popen") as popen:
            self.assertFalse(service.maybe_launch_worker(service._Launcher("en")))
        popen.assert_not_called()

    def test_a_failing_worker_is_not_relaunched_in_a_loop(self):
        proc = mock.Mock()
        proc.poll.return_value = 1
        launcher = service._Launcher("en")
        with mock.patch.object(service.subprocess, "Popen", return_value=proc) as popen:
            self.assertTrue(service.maybe_launch_worker(launcher))
            self.assertFalse(service.maybe_launch_worker(launcher))
            self.assertFalse(service.maybe_launch_worker(launcher))
        popen.assert_called_once()

    def test_kick_does_nothing_outside_the_service(self):
        with mock.patch.object(service.subprocess, "Popen") as popen:
            service.kick()
        popen.assert_not_called()


class Races(Env):
    def test_two_detaches_at_once_both_get_the_one_service(self):
        procs = [subprocess.Popen([sys.executable, "-m", "gimg", "--lang", "en", "serve", "--detach", "--port", "0",
                                   "--json"], cwd=ROOT, env=self.env, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outs = [p.communicate(timeout=30) for p in procs]
        self.assertEqual([p.returncode for p in procs], [0, 0], outs)
        states = [json.loads(out) for out, _ in outs]
        self.assertEqual(states[0]["pid"], states[1]["pid"])

    def test_worker_survives_a_momentary_lock_holder(self):
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        threading.Timer(0.1, os.close, args=(fd,)).start()
        with worker._single_worker():
            pass
        fd2 = os.open(str(queue.worker_lock_path()), os.O_RDWR)
        self.addCleanup(os.close, fd2)
        fcntl.flock(fd2, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with mock.patch.object(worker, "LOCK_RETRY_S", 0.05), self.assertRaises(GimgError) as ctx:
            with worker._single_worker():
                pass
        self.assertEqual(ctx.exception.code, "worker.already_running")

    def test_worker_waits_out_a_probe_that_outlasts_the_retry_window(self):
        # flaky test_second_worker_refused_other_process: a `queue.get` probe stalled past LOCK_RETRY_S under load
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)  # `_no_worker` inside a slow `_txn`
        threading.Timer(0.1, os.close, args=(fd,)).start()
        with mock.patch.object(worker, "LOCK_RETRY_S", 0), worker._single_worker():
            pass

    def test_a_queue_probe_does_not_hide_a_free_worker_lock_from_another_probe(self):
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)  # another probe (`worker_alive`) at the same instant
        with queue._no_worker() as free:
            self.assertTrue(free, "a shared probe made `_no_worker` see a worker")
            self.assertIs(queue.worker_alive(), False, "`_no_worker` made `worker_alive` see a worker")

    def test_service_survives_a_momentary_lock_probe(self):
        service.lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(service.lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)  # `lock_held` from another CLI
        threading.Timer(0.1, os.close, args=(fd,)).start()
        with service._single_instance():
            pass
        fd2 = os.open(str(service.lock_path()), os.O_RDWR)
        self.addCleanup(os.close, fd2)
        fcntl.flock(fd2, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with mock.patch.object(service, "LOCK_RETRY_S", 0.05), self.assertRaises(GimgError) as ctx:
            with service._single_instance():
                pass
        self.assertEqual(ctx.exception.code, "serve.already_running")

    def test_build_ignores_file_dates(self):
        import gimg
        target = Path(gimg.__file__)
        before, info = gimg.build_id(), target.stat()
        self.addCleanup(os.utime, target, ns=(info.st_atime_ns, info.st_mtime_ns))
        os.utime(target, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))
        self.assertEqual(gimg.build_id(), before, "touching a file without changing it changed the build")

    def test_stop_ignores_a_state_file_whose_pid_is_not_the_service(self):
        state = self.start()
        stale = dict(state, pid=os.getpid())  # a live process that is not the service
        service.state_path().write_text(json.dumps(stale))
        with mock.patch.object(service.os, "kill") as kill, self.assertRaises(GimgError) as ctx:
            service.stop()
        self.assertEqual(ctx.exception.code, "serve.not_running")
        kill.assert_not_called()
        service.state_path().write_text(json.dumps(state))

    def test_stop_with_a_foreign_pid_is_not_running(self):
        state = self.start()
        with mock.patch.object(service.os, "kill", side_effect=PermissionError), \
                self.assertRaises(GimgError) as ctx:
            service.stop()
        self.assertEqual(ctx.exception.code, "serve.not_running")

    def test_sighup_stops_like_sigterm(self):
        state = self.start()
        os.kill(state["pid"], signal.SIGHUP)
        self.assertTrue(wait_until(self.stopped, 5))


class WorkerAlive(Env):
    def test_reading_creates_nothing(self):
        self.assertFalse(self.data.exists())
        self.assertIs(queue.worker_alive(), False)
        self.assertFalse(self.data.exists())

    def test_follows_the_lock_and_reports_unknown(self):
        self.data.mkdir()
        path = queue.worker_lock_path()
        path.write_text("")
        fd = os.open(str(path), os.O_RDWR)
        self.addCleanup(os.close, fd)
        self.assertIs(queue.worker_alive(), False)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.assertIs(queue.worker_alive(), True)
        with mock.patch.object(queue.os, "open", side_effect=PermissionError):
            self.assertIsNone(queue.worker_alive())


if __name__ == "__main__":
    unittest.main()
