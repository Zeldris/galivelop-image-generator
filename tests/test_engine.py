import os
import struct
import tempfile
import threading
import time
import unittest
import zlib
from pathlib import Path
from unittest import mock

from gimg import engine
from gimg.errors import GimgError


def parse_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, chunks = 8, []
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos + 4])[0]
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        crc = struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0]
        assert crc == zlib.crc32(kind + body) & 0xFFFFFFFF, kind
        chunks.append((kind, body))
        pos += 12 + n
    assert pos == len(data)
    return chunks


class FakeEngineTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def job(self, name="a.png", seed=7, w=5, h=3):
        return engine.EngineJob(prompt="p", width=w, height=h, seed=seed, output=str(self.tmp / "sub" / name))

    def test_png_valid(self):
        job = self.job()
        res = engine.FakeEngine().generate(job, lambda: False)
        chunks = parse_png(Path(job.output).read_bytes())
        self.assertEqual([k for k, _ in chunks], [b"IHDR", b"IDAT", b"IEND"])
        w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", chunks[0][1])
        self.assertEqual((w, h, depth, ctype, comp, filt, inter), (5, 3, 8, 2, 0, 0, 0))
        raw = zlib.decompress(chunks[1][1])
        color = bytes(engine.seed_color(7))
        self.assertEqual(raw, (b"\x00" + color * 5) * 3)
        self.assertEqual(res.engine_version, "fake-1")
        self.assertIsInstance(res.duration_ms, int)
        self.assertEqual(os.listdir(self.tmp / "sub"), ["a.png"])  # no temp left

    def test_same_seed_same_bytes_other_seed_other_color(self):
        a, b, c = self.job("a.png", 1), self.job("b.png", 1), self.job("c.png", 2)
        for j in (a, b, c):
            engine.FakeEngine().generate(j, lambda: False)
        read = lambda j: Path(j.output).read_bytes()
        self.assertEqual(read(a), read(b))
        self.assertNotEqual(read(a), read(c))

    def test_cancel_during_delay(self):
        job = self.job()
        flag = threading.Event()
        threading.Timer(0.1, flag.set).start()
        start = time.monotonic()
        with self.assertRaises(engine.Cancelled):
            engine.FakeEngine(delay_s=5).generate(job, flag.is_set)
        self.assertLess(time.monotonic() - start, 2)
        self.assertFalse(Path(job.output).exists())

    def test_delay_is_measured(self):
        res = engine.FakeEngine(delay_s=0.1).generate(self.job(), lambda: False)
        self.assertGreaterEqual(res.duration_ms, 90)

    def test_fail_with(self):
        job = self.job()
        with self.assertRaises(engine.EngineError) as cm:
            engine.FakeEngine(fail_with="boom").generate(job, lambda: False)
        self.assertEqual(cm.exception.message, "boom")
        self.assertFalse(Path(job.output).exists())

    def test_bad_size(self):
        with self.assertRaises(engine.EngineError):
            engine.FakeEngine().generate(self.job(w=0), lambda: False)

    def test_timeout(self):
        job = self.job()
        job.timeout_s = 0.1
        t0 = time.monotonic()
        with self.assertRaises(engine.EngineError) as cm:
            engine.FakeEngine(delay_s=5).generate(job, lambda: False)
        self.assertLess(time.monotonic() - t0, 2)
        self.assertEqual(cm.exception.message, engine.TIMEOUT_MESSAGE)
        self.assertIsInstance(cm.exception, engine.EngineTimeout)
        self.assertFalse(Path(job.output).exists())

    def test_no_timeout_when_fast(self):
        job = self.job()
        job.timeout_s = 5
        engine.FakeEngine(delay_s=0.05).generate(job, lambda: False)
        self.assertTrue(Path(job.output).exists())

    def test_png_mode_honours_umask(self):
        job = self.job()
        old = os.umask(0o022)
        try:
            engine.FakeEngine().generate(job, lambda: False)
        finally:
            os.umask(old)
        self.assertEqual(os.stat(job.output).st_mode & 0o777, 0o644)


class GetEngineTests(unittest.TestCase):
    def env(self, **kw):
        patch = mock.patch.dict(os.environ, kw)
        patch.start()
        self.addCleanup(patch.stop)

    def setUp(self):
        for k in ("GIMG_ENGINE", "GIMG_FAKE_DELAY", "GIMG_FAKE_FAIL"):
            self.env(**{k: ""})

    def test_default_fake(self):
        e = engine.get_engine()
        self.assertIsInstance(e, engine.FakeEngine)
        self.assertEqual(e.provider, "fake")

    def test_unknown(self):
        self.env(GIMG_ENGINE="sd-cli")
        with self.assertRaises(GimgError) as cm:
            engine.get_engine()
        self.assertEqual(cm.exception.code, "engine.unknown")

    def test_knobs(self):
        self.env(GIMG_FAKE_DELAY="0.5", GIMG_FAKE_FAIL="x")
        e = engine.get_engine()
        self.assertEqual((e.delay_s, e.fail_with), (0.5, "x"))

    def test_bad_delay_values(self):
        for bad in ("nan", "inf", "-1", "-inf"):
            self.env(GIMG_FAKE_DELAY=bad)
            with self.assertRaises(GimgError) as cm:
                engine.get_engine()
            self.assertEqual(cm.exception.code, "engine.bad_delay", bad)

    def test_bad_delay(self):
        self.env(GIMG_FAKE_DELAY="abc")
        with self.assertRaises(GimgError) as cm:
            engine.get_engine()
        self.assertEqual(cm.exception.code, "engine.bad_delay")
