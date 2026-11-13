"""`gimg export`: escalado, BMP, ICO y WebP sin pérdida escritos con stdlib. La estructura se mira a mano; los píxeles
se comparan exactos al decodificar con ffmpeg (se salta sin ffmpeg salvo en el CI, como `tests/test_sheet.py`)."""
import io
import json
import os
import random
import shutil
import struct
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from gimg import cli, export, png
from gimg.errors import GimgError

EN_CI = os.environ.get("CI") == "true"
CON_FFMPEG = unittest.skipUnless(EN_CI or shutil.which("ffmpeg"), "hace falta ffmpeg")


def ruido(width, height, seed=1, opaco=False):
    rnd = random.Random(seed)
    data = bytearray(rnd.randrange(256) for _ in range(width * height * 4))
    if opaco:
        data[3::4] = b"\xff" * (width * height)
    return data


def degradado(width, height):
    data = bytearray()
    for y in range(height):
        for x in range(width):
            data += bytes((x * 255 // max(1, width - 1), y * 255 // max(1, height - 1), (x + y) % 256,
                           255 if x < width // 2 else (x * 7 + y) % 256))
    return data


def ffmpeg_rgba(path) -> bytes:
    return subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                          check=True, capture_output=True).stdout


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def source(self, width, height, rgba, name="src.png"):
        path = self.tmp / name
        path.write_bytes(png.rgba_bytes(width, height, rgba))
        return path

    def error(self, *args, **kw):
        with self.assertRaises(GimgError) as cm:
            export.export(*args, **kw)
        return cm.exception


class FitTests(unittest.TestCase):
    def test_mismo_tamano_es_una_copia(self):
        data = ruido(5, 4)
        self.assertEqual(export.fit(5, 4, data, 5, 4), data)

    def test_mitad_promedia_cuatro_pixeles(self):
        data = bytearray([0, 0, 0, 255, 200, 100, 40, 255,
                          100, 50, 20, 255, 100, 50, 20, 255])
        self.assertEqual(export.fit(2, 2, data, 1, 1), bytearray([100, 50, 20, 255]))

    def test_alfa_premultiplicado_no_oscurece_el_borde(self):
        # Un píxel rojo opaco junto a uno transparente negro: el medio sigue rojo puro, con alfa a la mitad.
        data = bytearray([255, 0, 0, 255, 0, 0, 0, 0])
        self.assertEqual(export.fit(2, 1, data, 1, 1), bytearray([255, 0, 0, 128]))

    def test_recorte_centrado_a_la_proporcion(self):
        # 4x2 a 1x1: queda el cuadrado central (columnas 1 y 2).
        filas = [bytes((v, v, v, 255)) for v in (0, 100, 200, 50)]
        data = bytearray(b"".join(filas) * 2)
        self.assertEqual(export.fit(4, 2, data, 1, 1), bytearray([150, 150, 150, 255]))

    def test_no_amplia(self):
        with self.assertRaises(GimgError) as cm:
            export.fit(10, 10, ruido(10, 10), 20, 5)
        self.assertEqual(cm.exception.code, "export.upscale")
        self.assertIn("no amplía", cm.exception.message("es"))
        self.assertIn("20x5", cm.exception.message("en"))


class BmpTests(Base):
    def test_cabecera_filas_al_reves_y_relleno(self):
        data = bytearray([10, 20, 30, 255, 40, 50, 60, 255, 70, 80, 90, 255,   # fila de arriba
                          1, 2, 3, 255, 4, 5, 6, 255, 7, 8, 9, 255])            # fila de abajo
        blob = export.bmp_bytes(3, 2, data)
        magic, size, _, _, offset = struct.unpack("<2sIHHI", blob[:14])
        hsize, width, height, planes, bpp, comp = struct.unpack("<IiiHHI", blob[14:34])
        self.assertEqual((magic, size, offset), (b"BM", len(blob), 54))
        self.assertEqual((hsize, width, height, planes, bpp, comp), (40, 3, 2, 1, 24, 0))
        self.assertEqual(blob[54:], bytes([3, 2, 1, 6, 5, 4, 9, 8, 7, 0, 0, 0, 30, 20, 10, 60, 50, 40, 90, 80, 70, 0, 0, 0]))

    def test_transparencia_sobre_el_fondo(self):
        blob = export.bmp_bytes(1, 1, bytearray([0, 0, 0, 0]), (10, 20, 30))
        self.assertEqual(blob[54:57], bytes([30, 20, 10]))
        blob = export.bmp_bytes(1, 1, bytearray([255, 255, 255, 128]), (0, 0, 0))
        self.assertEqual(blob[54:57], bytes([128, 128, 128]))

    @CON_FFMPEG
    def test_ffmpeg_lo_lee_igual(self):
        data = ruido(7, 5, opaco=True)
        path = self.tmp / "a.bmp"
        path.write_bytes(export.bmp_bytes(7, 5, data))
        self.assertEqual(ffmpeg_rgba(path), bytes(data))


class IcoTests(Base):
    def entries(self, blob):
        reserved, kind, count = struct.unpack("<HHH", blob[:6])
        self.assertEqual((reserved, kind), (0, 1))
        out = []
        for i in range(count):
            w, h, colors, res, planes, bpp, size, offset = struct.unpack("<BBBBHHII", blob[6 + 16 * i:22 + 16 * i])
            self.assertEqual((colors, res, planes, bpp), (0, 0, 1, 32))
            image = blob[offset:offset + size]
            self.assertTrue(image.startswith(b"\x89PNG"))
            out.append((w or 256, h or 256, image))
        return out

    def test_lados_por_defecto_hasta_el_lado_menor(self):
        src = self.source(300, 200, degradado(300, 200))
        res = export.export(src, self.tmp / "a.ico")
        self.assertEqual(res["sizes"], [(s, s) for s in (16, 24, 32, 48, 64, 128)])
        entries = self.entries((self.tmp / "a.ico").read_bytes())
        self.assertEqual([(w, h) for w, h, _ in entries], res["sizes"])
        path = self.tmp / "e.png"
        for w, h, image in entries:
            path.write_bytes(image)
            self.assertEqual(png.read_rgba(path)[:2], (w, h))

    def test_256_se_escribe_como_cero(self):
        src = self.source(256, 256, ruido(256, 256))
        blob = (export.export(src, self.tmp / "a.ico", icon_sizes="256,16") and (self.tmp / "a.ico").read_bytes())
        self.assertEqual(blob[6:8], b"\x10\x10")
        self.assertEqual(blob[22:24], b"\x00\x00")

    def test_size_no_vale_para_ico(self):
        src = self.source(32, 32, ruido(32, 32))
        exc = self.error(src, self.tmp / "a.ico", size="16x16")
        self.assertEqual(exc.code, "export.size_not_for_ico")
        self.assertIn("--icon-sizes", exc.message("es"))

    def test_fallo_al_escribir_lleva_su_codigo(self):
        src = self.source(32, 32, ruido(32, 32))
        (self.tmp / "file").write_text("x")
        exc = self.error(src, self.tmp / "file" / "a.png")  # its folder is a file
        self.assertEqual(exc.code, "export.write_failed")
        self.assertIn("a.png", exc.message("es"))

    def test_lados_fuera_de_rango(self):
        src = self.source(32, 32, ruido(32, 32))
        exc = self.error(src, self.tmp / "a.ico", icon_sizes="16,512")
        self.assertEqual(exc.code, "export.bad_icon_sizes")
        self.assertIn("1 a 256", exc.message("es"))


class WebpTests(Base):
    CASOS = [(1, 1), (2, 1), (1, 3), (5, 7), (64, 33), (513, 3), (3, 600)]

    def test_contenedor_riff_y_cabecera_vp8l(self):
        blob = export.webp_bytes(5, 7, ruido(5, 7))
        self.assertEqual((blob[:4], blob[8:16]), (b"RIFF", b"WEBPVP8L"))
        self.assertEqual(struct.unpack("<I", blob[4:8])[0], len(blob) - 8)
        size = struct.unpack("<I", blob[16:20])[0]
        self.assertEqual(len(blob), 20 + size + size % 2)
        bits = int.from_bytes(blob[21:25], "little")
        self.assertEqual(blob[20], 0x2F)
        self.assertEqual((bits & 0x3FFF, (bits >> 14) & 0x3FFF, bits >> 28 & 1, bits >> 29), (4, 6, 1, 0))

    def test_alfa_opaco_se_declara(self):
        blob = export.webp_bytes(4, 4, ruido(4, 4, opaco=True))
        self.assertEqual(int.from_bytes(blob[21:25], "little") >> 28 & 1, 0)

    def test_un_degradado_ocupa_menos_que_crudo(self):
        self.assertLess(len(export.webp_bytes(200, 100, degradado(200, 100))), 200 * 100 * 4 // 2)

    def test_demasiado_grande(self):
        with self.assertRaises(GimgError) as cm:
            export.webp_bytes(export.MAX_WEBP_SIDE + 1, 1, bytearray(4 * (export.MAX_WEBP_SIDE + 1)))
        self.assertEqual(cm.exception.code, "export.too_big")
        self.assertIn("16384", cm.exception.message("es"))

    @CON_FFMPEG
    def test_ffmpeg_lo_lee_sin_perdida(self):
        path = self.tmp / "a.webp"
        for w, h in self.CASOS:
            for data in (ruido(w, h, seed=w * h), bytearray(b"\x10\x20\x30\xff" * (w * h)), degradado(w, h)):
                with self.subTest(size=(w, h)):
                    path.write_bytes(export.webp_bytes(w, h, data))
                    self.assertEqual(ffmpeg_rgba(path), bytes(data))


def indice(width, height):
    """Cada pixel lleva su columna y su fila: R = x, G = y (opaco)."""
    data = bytearray()
    for y in range(height):
        for x in range(width):
            data += bytes((x, y, 7, 255))
    return data


class CropTests(Base):
    def test_recorte_exacto_de_pixeles(self):
        src = self.source(10, 8, indice(10, 8))
        res = export.export(src, self.tmp / "o.png", crop="2,3,4,2")
        self.assertEqual(res["crop"], [2, 3, 4, 2])
        self.assertEqual(res["sizes"], [(4, 2)])
        w, h, rgba = png.read_rgba(self.tmp / "o.png")
        self.assertEqual((w, h), (4, 2))
        self.assertEqual(rgba, bytearray(indice(10, 8)[(3 * 10 + 2) * 4:(3 * 10 + 6) * 4]
                                         + indice(10, 8)[(4 * 10 + 2) * 4:(4 * 10 + 6) * 4]))

    def test_sin_recorte_no_hay_clave(self):
        src = self.source(4, 4, ruido(4, 4))
        self.assertNotIn("crop", export.export(src, self.tmp / "o.png"))

    def test_recorte_y_luego_tamano(self):
        # 8x4 -> recorte a 4x4 desde x=4 -> 2x2: promedio de cada bloque 2x2 de las columnas 4..7.
        src = self.source(8, 4, indice(8, 4))
        export.export(src, self.tmp / "o.png", size="2x2", crop="4,0,4,4")
        w, h, rgba = png.read_rgba(self.tmp / "o.png")
        self.assertEqual((w, h), (2, 2))
        self.assertEqual(list(rgba[0:4]), [round(4.5), round(0.5), 7, 255])
        self.assertEqual(list(rgba[4:8]), [round(6.5), round(0.5), 7, 255])

    def test_recorte_para_ico_antes_del_cuadrado(self):
        src = self.source(16, 8, indice(16, 8))
        res = export.export(src, self.tmp / "o.ico", icon_sizes="4", crop="8,0,8,8")
        self.assertEqual(res["crop"], [8, 0, 8, 8])
        self.assertEqual(res["sizes"], [(4, 4)])

    def test_caja_fuera(self):
        src = self.source(10, 8, ruido(10, 8))
        exc = self.error(src, self.tmp / "o.png", crop="8,0,4,4")
        self.assertEqual(exc.code, "export.crop_outside")
        self.assertIn("10x8", exc.message("es"))
        self.assertEqual(self.error(src, self.tmp / "o.png", crop="0,5,2,4").code, "export.crop_outside")

    def test_formato_malo(self):
        src = self.source(4, 4, ruido(4, 4))
        for texto in ("1,2,3", "a,b,c,d", "0,0,0,4", "0,0,4,0", "-1,0,2,2", "0,0,2,2,2", ""):
            with self.subTest(texto=texto):
                self.assertEqual(self.error(src, self.tmp / "o.png", crop=texto).code, "export.bad_crop")
        self.assertIn("X,Y,W,H", self.error(src, self.tmp / "o.png", crop="x").message("en"))


class AnchorTests(Base):
    def columnas(self, ancho, alto, **kw):
        src = self.source(ancho, alto, indice(ancho, alto))
        export.export(src, self.tmp / "o.png", force=True, **kw)
        return png.read_rgba(self.tmp / "o.png")

    def test_top_bottom_y_center_toman_filas_distintas(self):
        # 4x8 a 4x4 (sin reducir): quedan las filas 0-3, 4-7 o 2-5.
        for anchor, primera in (("top", 0), ("bottom", 4), ("center", 2), (None, 2)):
            with self.subTest(anchor=anchor):
                w, h, rgba = self.columnas(4, 8, size="4x4", anchor=anchor)
                self.assertEqual((w, h), (4, 4))
                self.assertEqual([rgba[(y * 4) * 4 + 1] for y in range(4)], [primera + y for y in range(4)])

    def test_left_y_right(self):
        for anchor, primera in (("left", 0), ("right", 4), ("center", 2)):
            with self.subTest(anchor=anchor):
                w, h, rgba = self.columnas(8, 4, size="4x4", anchor=anchor)
                self.assertEqual([rgba[x * 4] for x in range(4)], [primera + x for x in range(4)])

    def test_esquina(self):
        w, h, rgba = self.columnas(8, 4, size="4x4", anchor="bottom-right")
        self.assertEqual((rgba[0], rgba[1]), (4, 0))
        w, h, rgba = self.columnas(4, 8, size="4x4", anchor="bottom-left")
        self.assertEqual((rgba[0], rgba[1]), (0, 4))

    def test_ancla_con_recorte_se_mueve_dentro_de_la_caja(self):
        w, h, rgba = self.columnas(8, 8, size="4x2", crop="2,2,4,4", anchor="top")
        self.assertEqual((rgba[0], rgba[1]), (2, 2))

    def test_ancla_mala(self):
        src = self.source(4, 4, ruido(4, 4))
        exc = self.error(src, self.tmp / "o.png", size="2x2", anchor="arriba")
        self.assertEqual(exc.code, "export.bad_anchor")
        self.assertIn("top-left", exc.message("es"))

    def test_center_no_cambia_el_resultado_de_fit(self):
        data = degradado(37, 23)
        self.assertEqual(export.fit(37, 23, data, 10, 10), export.fit(37, 23, data, 10, 10, (0.5, 0.5)))


class CommandTests(Base):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_png_reducido_por_la_orden(self):
        src = self.source(64, 48, degradado(64, 48))
        code, out, err = self.run_cli("--json", "export", str(src), str(self.tmp / "o.png"), "--size", "32x32")
        self.assertEqual(code, 0, err)
        res = json.loads(out)
        self.assertEqual((res["format"], res["sizes"]), ("png", [[32, 32]]))
        self.assertEqual(png.read_rgba(self.tmp / "o.png")[:2], (32, 32))

    def test_crop_y_anchor_por_la_orden(self):
        src = self.source(16, 8, indice(16, 8))
        dst = self.tmp / "o.png"
        code, out, err = self.run_cli("--json", "export", str(src), str(dst), "--crop", "4,0,8,8", "--size", "4x2",
                                      "--anchor", "top")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["crop"], [4, 0, 8, 8])
        code, out, err = self.run_cli("export", str(src), str(self.tmp / "p.png"), "--crop", "4,0,8,8")
        self.assertEqual(code, 0, err)
        self.assertIn("4,0,8,8", out)
        code, out, err = self.run_cli("export", str(src), str(self.tmp / "q.png"), "--crop", "9,0,8,8")
        self.assertNotEqual(code, 0)
        self.assertIn("16x8", out + err)

    def test_extension_desconocida(self):
        src = self.source(4, 4, ruido(4, 4))
        exc = self.error(src, self.tmp / "o.jpg")
        self.assertEqual(exc.code, "export.bad_format")
        self.assertIn(".webp, .ico, .bmp, .png", exc.message("es"))

    def test_no_pisa_sin_force_ni_la_entrada(self):
        src = self.source(4, 4, ruido(4, 4))
        (self.tmp / "o.bmp").write_bytes(b"x")
        self.assertIn("--force", self.error(src, self.tmp / "o.bmp").message("es"))
        export.export(src, self.tmp / "o.bmp", force=True)
        self.assertTrue((self.tmp / "o.bmp").read_bytes().startswith(b"BM"))
        exc = self.error(src, src, force=True)
        self.assertEqual(exc.code, "export.out_is_input")
        self.assertIn("PNG entregado", exc.message("es"))

    def test_tamano_y_fondo_mal_escritos(self):
        src = self.source(4, 4, ruido(4, 4))
        self.assertEqual(self.error(src, self.tmp / "o.bmp", size="4por4").code, "export.bad_size")
        exc = self.error(src, self.tmp / "o.bmp", background="rojo")
        self.assertEqual(exc.code, "export.bad_background")
        self.assertIn("#RRGGBB", exc.message("en"))
        self.assertEqual(self.error(src, self.tmp / "o.bmp", icon_sizes="16").code, "export.icon_sizes_only_ico")

    def test_no_deja_temporales(self):
        src = self.source(8, 8, ruido(8, 8))
        export.export(src, self.tmp / "o.webp")
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["o.webp", "src.png"])


if __name__ == "__main__":
    unittest.main()
