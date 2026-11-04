"""`gimg sheet` (hoja de contactos): geometría pura, motivos de fallo (el mensaje, no solo el código) y hojas reales
con PNG sintéticos de ffmpeg, que se saltan sin ffmpeg salvo en el CI (mismo patrón que `tests/test_measure.py`)."""
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from gimg import cli, measure, sheet
from gimg.errors import GimgError

TOOLS = ("ffmpeg", "ffprobe", "rsvg-convert")
TIENE_TODO = all(shutil.which(t) for t in TOOLS)
EN_CI = os.environ.get("CI") == "true"
CON_HERRAMIENTAS = unittest.skipUnless(EN_CI or TIENE_TODO, "hacen falta ffmpeg, ffprobe y rsvg-convert")


def color_png(path, color, size):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=%s:s=%s" % (color, size),
                    "-frames:v", "1", str(path)], check=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def error(self, *args, **kw):
        with self.assertRaises(GimgError) as cm:
            sheet.sheet(*args, **kw)
        return cm.exception

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()


class GeometryTests(unittest.TestCase):
    def test_posiciones_y_tamano_en_dos_columnas(self):
        geo = sheet.layout([(200, 100), (100, 100), (100, 200)], 2, 100)
        self.assertEqual(geo["heights"], [50, 100, 200])
        g, lh = sheet.GAP, sheet.LABEL_H
        self.assertEqual(geo["row_heights"], [lh + 100 + g, lh + 200 + g])
        self.assertEqual(geo["positions"], [(0, 0), (100 + g, 0), (0, lh + 100 + g)])
        self.assertEqual(geo["size"], (2 * (100 + g), lh + 100 + g + lh + 200 + g))

    def test_menos_imagenes_que_columnas_no_deja_hueco(self):
        self.assertEqual(sheet.layout([(10, 10)], 3, 100)["size"][0], 100 + sheet.GAP)

    def test_el_rotulo_se_corta_por_el_principio_y_conserva_el_final(self):
        texto = sheet._label_text(3, "/a/b/" + "x" * 200 + "-final.png", 640)
        self.assertTrue(texto.startswith("…") and texto.endswith("-final.png"))
        self.assertEqual(sheet._label_text(1, "/a/corto.png", 640), "1  corto.png")

    def test_el_svg_escapa_el_nombre(self):
        svg = sheet._label_svg('a<b>&"c".png', 640)
        self.assertIn("a&lt;b&gt;&amp;", svg)
        self.assertNotIn("<b>", svg)


class ErrorTests(Base):
    def test_sin_imagenes(self):
        exc = self.error([], self.tmp / "o.png")
        self.assertEqual(exc.code, "sheet.no_images")
        self.assertIn("no images", exc.message("en"))
        self.assertIn("faltan imágenes", exc.message("es"))

    def test_entrada_inexistente_nombra_la_ruta(self):
        exc = self.error([self.tmp / "no existe.png"], self.tmp / "o.png")
        self.assertEqual(exc.code, "sheet.unreadable")
        self.assertIn("no existe.png", exc.message("en"))
        self.assertIn("cannot read the image", exc.message("en"))

    def test_la_salida_no_puede_ser_una_entrada(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"datos")
        exc = self.error([img], img)
        self.assertEqual(exc.code, "sheet.out_is_input")
        self.assertIn("also one of the inputs", exc.message("en"))
        self.assertEqual(img.read_bytes(), b"datos")

    def test_la_salida_como_enlace_a_una_entrada_tampoco(self):
        img, link = self.tmp / "a.png", self.tmp / "enlace.png"
        img.write_bytes(b"datos")
        link.symlink_to(img)
        self.assertEqual(self.error([img], link).code, "sheet.out_is_input")

    def test_falta_una_herramienta(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        with mock.patch("gimg.sheet.shutil.which", side_effect=lambda t: None if t == "ffmpeg" else "/bin/" + t):
            exc = self.error([img], self.tmp / "o.png")
        self.assertEqual((exc.code, exc.params["tool"]), ("sheet.tool_missing", "ffmpeg"))
        self.assertIn("\"ffmpeg\" is missing for making the sheet", exc.message("en"))
        self.assertFalse((self.tmp / "o.png").exists())

    def test_columnas_y_ancho_invalidos(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        exc = self.error([img], self.tmp / "o.png", columns=0)
        self.assertEqual(exc.code, "sheet.bad_columns")
        self.assertIn("not a valid number of columns", exc.message("en"))
        exc = self.error([img], self.tmp / "o.png", width=10)
        self.assertEqual(exc.code, "sheet.bad_width")
        self.assertIn("not a valid width", exc.message("en"))

    def test_demasiadas_imagenes(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        exc = self.error([img] * (sheet.MAX_IMAGES + 1), self.tmp / "o.png")
        self.assertEqual(exc.code, "sheet.too_many")

    def test_cli_sin_imagenes_sale_con_1_y_el_motivo_en_stderr(self):
        code, out, err = self.run_cli("sheet", "--out", str(self.tmp / "o.png"), "--lang", "en")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("no images", err)

    def test_cli_sin_out_lo_rechaza_argparse(self):
        code, out, err = self.run_cli("sheet", "a.png", "--lang", "en")
        self.assertNotEqual(code, 0)
        self.assertIn("--out", err)


@CON_HERRAMIENTAS
class RealSheetTests(Base):
    def imagenes(self):
        # nombres con espacios, comillas, dos puntos, % y un guion inicial: ninguno puede romper el filtro
        nombres = ["uno dos.png", "it's: 100%.png", "-raro.png", "tres.png", "cuatro.png"]
        tamanos = ["200x100", "100x100", "100x200", "300x100", "100x100"]
        rutas = []
        for nombre, tam in zip(nombres, tamanos):
            ruta = self.tmp / nombre
            color_png(ruta, "red", tam)
            rutas.append(ruta)
        return rutas

    def test_tamano_de_la_hoja_es_columnas_por_filas(self):
        rutas = self.imagenes()
        destino = self.tmp / "salida con espacios.png"
        res = sheet.sheet(rutas, destino, columns=2, width=100)
        esperado = sheet.layout([(200, 100), (100, 100), (100, 200), (300, 100), (100, 100)], 2, 100)["size"]
        self.assertEqual(tuple(res["size"]), esperado)
        self.assertEqual(measure.image_size(destino), esperado)
        self.assertEqual(res["columns"], 2)

    def test_una_columna_y_tres_columnas(self):
        rutas = self.imagenes()[:3]
        una = sheet.sheet(rutas, self.tmp / "a.png", columns=1, width=100)
        self.assertEqual(una["size"][0], 100 + sheet.GAP)
        tres = sheet.sheet(rutas, self.tmp / "b.png", columns=9, width=100)  # más columnas que imágenes
        self.assertEqual((tres["columns"], tres["size"][0]), (3, 3 * (100 + sheet.GAP)))
        self.assertEqual(measure.image_size(self.tmp / "b.png"), tuple(tres["size"]))

    def test_una_sola_imagen(self):
        ruta = self.imagenes()[0]
        res = sheet.sheet([ruta], self.tmp / "s.png", width=100)
        self.assertEqual(tuple(res["size"]), (100 + sheet.GAP, sheet.LABEL_H + 50 + sheet.GAP))

    def test_el_rotulo_se_dibuja(self):
        # sin rótulo el fondo del rótulo es todo #202020; con texto blanco hay píxeles claros en esa franja
        ruta = self.tmp / "gris.png"
        color_png(ruta, "black", "100x100")
        destino = self.tmp / "s.png"
        sheet.sheet([ruta], destino, width=200)
        zona = measure.pixels(destino, (0, 0, 200, sheet.LABEL_H))
        self.assertGreater(max(max(p) for p in zona), 200)

    def test_cli_imprime_el_numero_y_la_ruta_de_cada_casilla(self):
        rutas = self.imagenes()[:2]
        code, out, err = self.run_cli("sheet", *map(str, rutas), "--out", str(self.tmp / "s.png"), "--width", "100",
                                      "--lang", "en")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("2 columns, 2 images", out)
        self.assertIn("  2  %s" % rutas[1], out)
        code, out, _ = self.run_cli("sheet", *map(str, rutas), "--out", str(self.tmp / "j.png"), "--width", "100", "--json")
        self.assertEqual(json.loads(out)["images"], [str(r) for r in rutas])

    def test_una_entrada_ilegible_da_el_motivo_de_ffmpeg(self):
        malo = self.tmp / "malo.png"
        malo.write_bytes(b"no soy un png")
        exc = self.error([malo], self.tmp / "o.png")
        self.assertEqual(exc.code, "sheet.unreadable")
        self.assertFalse((self.tmp / "o.png").exists())


if __name__ == "__main__":
    unittest.main()
