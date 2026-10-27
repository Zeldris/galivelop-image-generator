import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

from gimg import png
from gimg.errors import GimgError


class PngTextTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.path = self.dir / "a.png"
        self.path.write_bytes(png.png_bytes(3, 2, (1, 2, 3)))

    def reason(self, path=None):
        with self.assertRaises(GimgError) as cm:
            png.read_text_chunks(path or self.path)
        self.assertEqual(cm.exception.code, "png.invalid")
        return cm.exception.params["reason"]

    def test_png_without_chunks_has_none(self):
        self.assertEqual(png.read_text_chunks(self.path), {})

    def test_write_and_read_back_latin1_as_text_chunk(self):
        png.add_text_chunk(self.path, "gimg", '{"seed": 3, "prompt": "niño á"}')
        self.assertEqual(png.read_text_chunks(self.path), {"gimg": '{"seed": 3, "prompt": "niño á"}'})
        self.assertIn(b"tEXt", self.path.read_bytes())
        self.assertNotIn(b"iTXt", self.path.read_bytes())

    def test_text_outside_latin1_is_written_as_utf8_itxt(self):
        text = '{"prompt": "a cat 猫 \U0001F63A"}'
        png.add_text_chunk(self.path, "gimg", text)
        self.assertEqual(png.read_text_chunks(self.path), {"gimg": text})
        self.assertIn(b"iTXt", self.path.read_bytes())
        self.assertNotIn(b"tEXt", self.path.read_bytes())

    def test_nul_in_the_text_goes_to_itxt_too(self):
        png.add_text_chunk(self.path, "k", "a\x00b")
        self.assertEqual(png.read_text_chunks(self.path), {"k": "a\x00b"})
        self.assertIn(b"iTXt", self.path.read_bytes())

    def test_same_key_replaces_and_other_keys_stay(self):
        png.add_text_chunk(self.path, "a", "1")
        png.add_text_chunk(self.path, "b", "2")
        png.add_text_chunk(self.path, "a", "猫")  # a different kind of chunk for the same key
        self.assertEqual(png.read_text_chunks(self.path), {"a": "猫", "b": "2"})
        self.assertEqual(self.path.read_bytes().count(b"iTXt") + self.path.read_bytes().count(b"tEXt"), 2)

    def test_image_data_is_untouched_and_chunk_goes_before_iend(self):
        before = [k for k, _ in png._chunks(self.path.read_bytes(), self.path)]
        png.add_text_chunk(self.path, "gimg", "x")
        after = [k for k, _ in png._chunks(self.path.read_bytes(), self.path)]
        self.assertEqual(before, [b"IHDR", b"IDAT", b"IEND"])
        self.assertEqual(after, [b"IHDR", b"IDAT", b"tEXt", b"IEND"])
        plain = png.png_bytes(3, 2, (1, 2, 3))
        self.assertTrue(self.path.read_bytes().startswith(plain[:-12]))  # signature, IHDR and IDAT byte for byte
        self.assertTrue(self.path.read_bytes().endswith(plain[-12:]))  # and the same IEND

    def test_reads_compressed_ztxt_and_itxt(self):
        raw = self.path.read_bytes()
        z = png.chunk(b"zTXt", b"zk\x00\x00" + zlib.compress(b"caf\xe9"))
        i = png.chunk(b"iTXt", b"ik\x00\x01\x00\x00\x00" + zlib.compress("猫".encode("utf-8")))
        self.path.write_bytes(raw[:-12] + z + i + raw[-12:])
        self.assertEqual(png.read_text_chunks(self.path), {"zk": "café", "ik": "猫"})

    def test_not_a_png(self):
        bad = self.dir / "b.png"
        bad.write_bytes(b"GIF89a....")
        self.assertEqual(self.reason(bad), "not a PNG (bad signature)")

    def test_missing_file(self):
        self.assertTrue(self.reason(self.dir / "nope.png").startswith("cannot read the file"))

    def test_cut_file_says_what_is_cut(self):
        data = self.path.read_bytes()
        self.path.write_bytes(data[:-12])  # IEND missing
        self.assertEqual(self.reason(), "no IEND chunk (file cut)")
        self.path.write_bytes(data[:-2])  # IEND cut inside
        self.assertEqual(self.reason(), "truncated chunk IEND")
        self.path.write_bytes(data[:12])  # a chunk header cut inside
        self.assertEqual(self.reason(), "truncated chunk header")
        self.path.write_bytes(data[:8])  # only the signature
        self.assertEqual(self.reason(), "the first chunk is not IHDR")
        for size in range(len(data)):  # whatever the cut, it is an error with a reason, never a traceback
            self.path.write_bytes(data[:size])
            self.assertTrue(self.reason())

    def test_bad_crc_names_the_chunk(self):
        data = bytearray(self.path.read_bytes())
        data[-1] ^= 0xFF  # the CRC of IEND
        self.path.write_bytes(bytes(data))
        self.assertEqual(self.reason(), "bad CRC in chunk IEND")

    def test_corrupt_file_is_not_modified_by_add(self):
        data = self.path.read_bytes()[:-3]
        self.path.write_bytes(data)
        with self.assertRaises(GimgError) as cm:
            png.add_text_chunk(self.path, "gimg", "x")
        self.assertEqual(cm.exception.code, "png.invalid")
        self.assertEqual(self.path.read_bytes(), data)
        self.assertEqual(sorted(os.listdir(self.dir)), ["a.png"])

    def test_bad_keys(self):
        for key in ("", " a", "a ", "a\nb", "a\x00b", "x" * 80, "猫"):
            with self.assertRaises(GimgError) as cm:
                png.add_text_chunk(self.path, key, "v")
            self.assertEqual((cm.exception.code, cm.exception.params["key"]), ("png.bad_key", key))
        png.add_text_chunk(self.path, "x" * 79, "v")  # the longest one is fine

    def test_write_is_atomic_a_failure_leaves_the_original_and_no_temporary(self):
        original = self.path.read_bytes()
        with mock.patch("gimg.png.os.replace", side_effect=OSError("disk gone")):
            with self.assertRaises(OSError):
                png.add_text_chunk(self.path, "gimg", "x")
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(sorted(os.listdir(self.dir)), ["a.png"])

    def test_the_replacement_is_a_single_os_replace_of_a_complete_file(self):
        seen = []
        real = os.replace

        def spy(src, dst):
            seen.append(png.read_text_chunks(src))  # what is about to become the file is already complete and valid
            return real(src, dst)

        with mock.patch("gimg.png.os.replace", side_effect=spy):
            png.add_text_chunk(self.path, "gimg", "x")
        self.assertEqual(seen, [{"gimg": "x"}])

    def test_crc_of_the_chunk_we_write_is_right(self):
        body = png.text_chunk("k", "v")
        length = struct.unpack(">I", body[:4])[0]
        self.assertEqual(struct.unpack(">I", body[-4:])[0], zlib.crc32(body[4:-4]) & 0xFFFFFFFF)
        self.assertEqual(length, len(b"k\x00v"))


class PngSizeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.path = self.dir / "a.png"

    def reason(self):
        with self.assertRaises(GimgError) as cm:
            png.size(self.path)
        self.assertEqual(cm.exception.code, "png.invalid")
        return cm.exception.params["reason"]

    def test_width_and_height_in_that_order(self):
        self.path.write_bytes(png.png_bytes(7, 3, (1, 2, 3)))
        self.assertEqual(png.size(self.path), (7, 3))

    def test_size_ignores_what_comes_after_the_header(self):
        self.path.write_bytes(png.png_bytes(7, 3, (1, 2, 3))[:33])  # nothing but signature and IHDR
        self.assertEqual(png.size(self.path), (7, 3))

    def test_size_of_a_file_with_text_chunks(self):
        self.path.write_bytes(png.png_bytes(5, 9, (1, 2, 3)))
        png.add_text_chunk(self.path, "gimg", "{}")
        self.assertEqual(png.size(self.path), (5, 9))

    def test_not_a_png(self):
        self.path.write_bytes(b"GIF89a" + b"\x00" * 40)
        self.assertEqual(self.reason(), "not a PNG (bad signature)")

    def test_cut_inside_the_header(self):
        data = png.png_bytes(7, 3, (1, 2, 3))
        for size in (0, 7, 8, 12, 20, 32):
            self.path.write_bytes(data[:size])
            self.assertTrue(self.reason(), size)
        self.path.write_bytes(data[:20])
        self.assertEqual(self.reason(), "truncated chunk header")

    def test_first_chunk_is_not_ihdr(self):
        self.path.write_bytes(png.SIGNATURE + png.chunk(b"IDAT", b"x" * 13) + b"\x00" * 20)
        self.assertEqual(self.reason(), "the first chunk is not IHDR")

    def test_bad_ihdr_crc_is_refused(self):
        data = bytearray(png.png_bytes(7, 3, (1, 2, 3)))
        data[32] ^= 0xFF  # the CRC of IHDR
        self.path.write_bytes(bytes(data))
        self.assertEqual(self.reason(), "bad CRC in chunk IHDR")

    def test_a_zero_side_is_refused(self):
        ihdr = png.chunk(b"IHDR", struct.pack(">IIBBBBB", 0, 3, 8, 2, 0, 0, 0))
        self.path.write_bytes(png.SIGNATURE + ihdr + png.chunk(b"IEND", b""))
        self.assertEqual(self.reason(), "the image has a zero side")

    def test_missing_file_and_directory_are_png_invalid(self):
        self.assertIn("cannot read the file", self.reason())
        self.path.mkdir()
        self.assertIn("cannot read the file", self.reason())


if __name__ == "__main__":
    unittest.main()
