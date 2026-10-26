"""Pruebas de los scripts de prueba de concepto de examples/pilot/ (componer.py y medir.py)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PILOTO = Path(__file__).resolve().parent.parent / "examples" / "pilot"
sys.path.insert(0, str(PILOTO))

import componer  # noqa: E402
import medir  # noqa: E402

TIENE_FFMPEG = shutil.which("ffmpeg") is not None
TIENE_RSVG = shutil.which("rsvg-convert") is not None
# En el CI (ciInstall de .claude/gw.json las instala) no se saltan: si faltan, fallan en vez de salir verdes sin probar.
EN_CI = os.environ.get("CI") == "true"

LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 40">'
        '<rect width="100" height="40" fill="#2BB3EA"/></svg>')


def color_png(ruta, color, tam="64x32"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={tam}",
                    "-frames:v", "1", str(ruta)], check=True)


class EscapeTests(unittest.TestCase):
    def test_escapa_xml(self):
        self.assertEqual(componer.esc('a & b <c> "d" \'e\''), "a &amp; b &lt;c&gt; &quot;d&quot; &apos;e&apos;")

    def test_color_invalido_dice_el_motivo(self):
        with self.assertRaises(componer.ErrorComponer) as cm:
            componer.parsear_velo("rojo:0.5")
        self.assertIn("se esperaba un color #rrggbb", str(cm.exception))

    def test_lab_del_rojo(self):
        for v, esperado in zip(medir.rgb_lab((255, 0, 0)), (53.24, 80.09, 67.20)):
            self.assertAlmostEqual(v, esperado, places=1)

    def test_luminancia_del_rojo(self):
        self.assertAlmostEqual(medir.luminancia((255, 0, 0)), 0.2126, places=4)

    def test_recorte_cover_centrado(self):
        x, y, w, h = componer.recorte_cover(1280, 640, 1, 1)
        self.assertEqual((x, y, w, h), (320.0, 0.0, 640.0, 640.0))


@unittest.skipUnless(EN_CI or (TIENE_FFMPEG and TIENE_RSVG), "hacen falta ffmpeg y rsvg-convert")
class ComponerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        color_png(self.tmp / "fondo.png", "0x336699", "200x100")
        (self.tmp / "logo.svg").write_text(LOGO, encoding="utf-8")

    def tamano(self, ruta):
        return medir.tamano(str(ruta))

    def test_cover_da_el_tamano_exacto(self):
        for w, h in ((120, 63), (108, 108), (50, 200)):
            salida = self.tmp / f"s{w}x{h}.png"
            componer.componer(self.tmp / "fondo.png", salida, w, h, self.tmp / "logo.svg", "Título <&>")
            self.assertEqual(self.tamano(salida), (w, h))
            self.assertTrue(salida.with_suffix(".svg").is_file())

    def test_el_texto_va_escapado_en_el_svg(self):
        svg = componer.componer(self.tmp / "fondo.png", self.tmp / "o.png", 200, 100, self.tmp / "logo.svg",
                                "A & B <i>", subtitulo="x < y")
        texto = svg.read_text(encoding="utf-8")
        self.assertIn("A &amp; B &lt;i&gt;", texto)
        self.assertNotIn("<i>", texto)

    def test_sin_fondo_falla_con_motivo(self):
        with self.assertRaises(componer.ErrorComponer) as cm:
            componer.componer(self.tmp / "no.png", self.tmp / "o.png", 10, 10, self.tmp / "logo.svg", "t")
        self.assertIn("no existe el fondo", str(cm.exception))


@unittest.skipUnless(EN_CI or TIENE_FFMPEG, "hace falta ffmpeg")
class MedirTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.rojo = self.tmp / "rojo.png"
        color_png(self.rojo, "0xff0000")

    def test_paleta_con_su_color_da_100(self):
        pix = medir.pixeles(str(self.rojo))
        self.assertGreater(medir.porcentaje_paleta(pix, [medir.hex_rgb("#ff0000")]), 99.0)

    def test_paleta_con_otro_color_da_0(self):
        pix = medir.pixeles(str(self.rojo))
        self.assertLess(medir.porcentaje_paleta(pix, [medir.hex_rgb("#0000ff")]), 1.0)

    def test_signalstats_del_negro_y_del_blanco(self):
        negro, blanco = self.tmp / "n.png", self.tmp / "b.png"
        color_png(negro, "black")
        color_png(blanco, "white")
        self.assertLess(medir.signalstats(str(negro))[0], 20)
        self.assertGreater(medir.signalstats(str(blanco))[0], 230)

    def test_contraste_blanco_sobre_negro_es_21(self):
        self.assertAlmostEqual(medir.contraste(medir.luminancia((255, 255, 255)), medir.luminancia((0, 0, 0))), 21.0)

    def test_contraste_de_zona_negra_con_texto_blanco(self):
        negro = self.tmp / "n.png"
        color_png(negro, "black")
        r = medir.medir(str(negro), zona=(0, 0, 32, 16), color_texto=(255, 255, 255))
        self.assertGreater(r["contraste"]["peor"], 20.0)

    def test_zona_fuera_de_la_imagen_dice_el_motivo(self):
        with self.assertRaises(medir.ErrorMedir) as cm:
            medir.pixeles(str(self.rojo), (0, 0, 500, 500))
        self.assertIn("se sale de la imagen", str(cm.exception))

    def test_color_malo_dice_el_motivo(self):
        with self.assertRaises(medir.ErrorMedir) as cm:
            medir.hex_rgb("azul")
        self.assertIn("se esperaba un color #rrggbb", str(cm.exception))



class ZonasTests(unittest.TestCase):
    def test_caja_arriba_ocupa_la_mitad_de_arriba(self):
        x, y, w, h = componer.caja_zona(1080, 1080, "arriba")
        self.assertEqual((x, y), (65, 65))
        self.assertLessEqual(y + h, 1080 * 0.5)

    def test_zona_desconocida_dice_cuales_hay(self):
        with self.assertRaises(componer.ErrorComponer) as cm:
            componer.caja_zona(100, 100, "centro")
        self.assertIn("izquierda, derecha, abajo, arriba", str(cm.exception))


class SinTextoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "logo.svg").write_text(LOGO, encoding="utf-8")
        (self.tmp / "fondo.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    def test_sin_texto_no_lleva_ni_texto_ni_logo(self):
        svg = componer.construir_svg(self.tmp / "fondo.png", 200, 100, self.tmp / "logo.svg", "Hola", zona="arriba",
                                     texto=False)
        self.assertNotIn("<text", svg)
        self.assertEqual(svg.count("<image"), 1)
        self.assertIn('y2="1"', svg)  # el velo de «arriba» baja desde el borde de arriba

    def test_con_texto_lleva_el_titulo(self):
        svg = componer.construir_svg(self.tmp / "fondo.png", 200, 100, self.tmp / "logo.svg", "Hola", zona="arriba")
        self.assertIn(">Hola</text>", svg)


@unittest.skipUnless(EN_CI or (TIENE_FFMPEG and TIENE_RSVG), "hacen falta ffmpeg y rsvg-convert")
class PiezasTests(unittest.TestCase):
    def setUp(self):
        import piezas
        self.piezas = piezas
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.viejo = piezas.PILOTO
        piezas.PILOTO = self.tmp
        self.addCleanup(setattr, piezas, "PILOTO", self.viejo)

    def test_sin_fondo_dice_donde_lo_busco(self):
        with self.assertRaises(componer.ErrorComponer) as cm:
            self.piezas.fondo_de("portal", "estilo")
        self.assertIn("piloto/r5-fondos ni piloto/r3", str(cm.exception))

    def test_elige_el_definitivo_y_no_el_borrador_ni_flux3(self):
        d = self.tmp / "r3" / "portal" / "intentos"
        d.mkdir(parents=True)
        color_png(d / "estilo-640x320-p4-s3.png", "red", "64x32")
        color_png(d / "estilo-1280x640-p16-flux3-s3.png", "red", "256x128")
        color_png(d / "estilo-1280x640-p8-s3.png", "red", "128x64")
        self.assertEqual(self.piezas.fondo_de("portal", "estilo").name, "estilo-1280x640-p8-s3.png")

    def test_pieza_compuesta_con_medidas_sin_texto(self):
        d = self.tmp / "r3" / "demo" / "intentos"
        d.mkdir(parents=True)
        color_png(d / "estilo-1280x640-p8-s3.png", "black", "128x64")
        logo = self.tmp / "logo.svg"
        logo.write_text(LOGO, encoding="utf-8")
        p = {"id": "og", "ancho": 120, "alto": 63, "fondo": "estilo", "logo": str(logo), "titulo": "Hola",
             "zona": "izquierda", "color_texto": "#ffffff", "velo": "#000000:0.5"}
        m = self.piezas.pieza("demo", {}, p, self.tmp / "r4" / "demo")
        self.assertTrue((self.tmp / "r4" / "demo" / "intentos" / "og.png").is_file())
        self.assertGreater(m["contraste"]["peor"], 15)  # fondo negro, texto blanco: el texto no entra en la medida


if __name__ == "__main__":
    unittest.main()
