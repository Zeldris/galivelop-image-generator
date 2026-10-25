import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gimg import fsutil


def _bump(path, n):
    for _ in range(n):
        with fsutil.lock(path):
            data = fsutil.read_json(path, default={"n": 0})
            data["n"] += 1
            fsutil.write_json(path, data)


class FsutilTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def test_write_format(self):
        p = self.dir / "sub" / "a.json"
        fsutil.write_json(p, {"b": 1, "a": [1]})
        self.assertEqual(p.read_text(), '{\n  "a": [\n    1\n  ],\n  "b": 1\n}\n')
        self.assertEqual(sorted(x.name for x in p.parent.iterdir()), ["a.json"])

    def test_failed_write_keeps_old_and_no_temp(self):
        p = self.dir / "a.json"
        fsutil.write_json(p, {"v": 1})
        with self.assertRaises(TypeError):
            fsutil.write_json(p, {"v": object()})
        self.assertEqual(json.loads(p.read_text()), {"v": 1})
        with mock.patch("os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                fsutil.write_json(p, {"v": 2})
        self.assertEqual(json.loads(p.read_text()), {"v": 1})
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), ["a.json"])

    def test_read_default_and_missing(self):
        p = self.dir / "none.json"
        self.assertEqual(fsutil.read_json(p, default=5), 5)
        with self.assertRaises(FileNotFoundError):
            fsutil.read_json(p)

    def test_lock_serialises_processes(self):
        p = self.dir / "c.json"
        procs = [multiprocessing.Process(target=_bump, args=(p, 25)) for _ in range(4)]
        for pr in procs:
            pr.start()
        for pr in procs:
            pr.join()
            self.assertEqual(pr.exitcode, 0)
        self.assertEqual(fsutil.read_json(p)["n"], 100)
