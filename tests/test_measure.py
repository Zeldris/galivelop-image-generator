"""Brand measurement (F2.9, D31): `gimg/measure.py` and `gimg measure`.

The pure parts (colour maths, parsing, errors that come before any tool) need nothing; the rest runs `ffmpeg` on
synthetic images of known colour and is skipped without it, except in the CI (same pattern as `tests/test_compose.py`).
Every test that expects a failure checks the error code."""
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

from gimg import cli, measure
from gimg.errors import GimgError

TIENE_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
EN_CI = os.environ.get("CI") == "true"
CON_FFMPEG = unittest.skipUnless(EN_CI or TIENE_FFMPEG, "hace falta ffmpeg")


def color_png(path, color, size="64x32"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=%s:s=%s" % (color, size),
                    "-frames:v", "1", str(path)], check=True)


def half_png(path, left, right, size="64x32"):
    """Left half `left`, right half `right`."""
    w, h = (int(v) for v in size.split("x"))
    flt = "color=c=%s:s=%s,drawbox=x=%d:y=0:w=%d:h=%d:color=%s:t=fill" % (left, size, w // 2, w - w // 2, h, right)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", flt, "-frames:v", "1", str(path)], check=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def code(self, fn, *a, **kw):
        with self.assertRaises(GimgError) as cm:
            fn(*a, **kw)
        return cm.exception.code


class MathTests(unittest.TestCase):
    def test_lab_del_rojo_puro(self):
        for v, esperado in zip(measure.rgb_lab((255, 0, 0)), (53.24, 80.09, 67.20)):
            self.assertAlmostEqual(v, esperado, places=1)

    def test_lab_del_blanco_y_negro(self):
        self.assertAlmostEqual(measure.rgb_lab((255, 255, 255))[0], 100.0, places=1)
        self.assertAlmostEqual(measure.rgb_lab((0, 0, 0))[0], 0.0, places=3)

    def test_umbral_de_delta_e(self):
        color, pixel = (128, 128, 128), (140, 128, 128)
        d = measure.delta_e(measure.rgb_lab(color), measure.rgb_lab(pixel))
        self.assertGreater(d, 1)
        self.assertEqual(measure.palette_share([pixel], [color], threshold=d + 0.01)["pct"], 100.0)
        self.assertEqual(measure.palette_share([pixel], [color], threshold=d - 0.01)["pct"], 0.0)

    def test_paleta_mitad_y_mitad(self):
        pix = [(255, 0, 0)] * 50 + [(0, 0, 255)] * 50
        res = measure.palette_share(pix, [(255, 0, 0), (0, 255, 0)])
        self.assertEqual(res["pct"], 50.0)
        self.assertEqual(res["by_color"], {"#ff0000": 50.0, "#00ff00": 0.0})

    def test_contraste_blanco_sobre_negro_21(self):
        res = measure.contrast([(0, 0, 0)] * 10, (255, 255, 255))
        self.assertEqual(res, {"mean": 21.0, "p10": 21.0, "p90": 21.0, "worst": 21.0})

    def test_contraste_peor_es_la_menor(self):
        res = measure.contrast([(0, 0, 0)] * 5 + [(255, 255, 255)] * 5, (255, 255, 255))
        self.assertEqual(res["worst"], 1.0)
        self.assertGreater(res["mean"], 1.0)

    def test_emd_de_dos_planos_constantes(self):
        a, b = [bytes([10]) * 100] * 3, [bytes([30]) * 100] * 3
        self.assertEqual(measure.emd(a, a), {"Y": 0.0, "Cb": 0.0, "Cr": 0.0})
        self.assertEqual(measure.emd(a, b), {"Y": 20.0, "Cb": 20.0, "Cr": 20.0})


class ParseTests(Base):
    def test_hex_valido_con_y_sin_almohadilla(self):
        self.assertEqual(measure.parse_hex("#1AA6df"), (26, 166, 223))
        self.assertEqual(measure.parse_hex("1aa6df"), (26, 166, 223))

    def test_hex_malo(self):
        for bad in ("#12345", "#1234567", "rojo", "#ggg000", "#112233\n#445566", ""):
            self.assertEqual(self.code(measure.parse_hex, bad), "measure.bad_hex", bad)

    def test_zona_valida(self):
        self.assertEqual(measure.parse_zone("1,2,30,40"), (1, 2, 30, 40))

    def test_zona_mala(self):
        for bad in ("1,2,3", "1,2,3,4,5", "a,b,c,d", "0,0,0,5", "0,0,5,-1", "-1,0,5,5", "1.5,0,5,5"):
            self.assertEqual(self.code(measure.parse_zone, bad), "measure.bad_zone", bad)

    def test_zona_sin_texto_y_texto_sin_zona(self):
        self.assertEqual(self.code(measure.measure, "x.png", zone="0,0,1,1"), "cli.measure_zone_text")
        self.assertEqual(self.code(measure.measure, "x.png", text="#ffffff"), "cli.measure_zone_text")

    def test_hex_malo_en_la_paleta_antes_de_leer(self):
        self.assertEqual(self.code(measure.measure, "no-existe.png", palette=["#00ff00", "verde"]), "measure.bad_hex")


class SinHerramientasTests(Base):
    def test_ffmpeg_ausente_con_path_vacio(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        with mock.patch.dict(os.environ, {"PATH": ""}):
            self.assertEqual(self.code(measure.measure, str(img)), "measure.tool_missing")

    def test_ffprobe_ausente(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        real = shutil.which
        with mock.patch("gimg.measure.shutil.which", lambda n: None if n == "ffprobe" else real(n)):
            e = None
            try:
                measure.image_size(str(img))
            except GimgError as exc:
                e = exc
        self.assertEqual(e.code, "measure.tool_missing")
        self.assertEqual(e.params["tool"], "ffprobe")

    def test_timeout(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        with mock.patch("gimg.measure.shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch("gimg.measure.subprocess.run", side_effect=subprocess.TimeoutExpired("ffmpeg", 1)):
            self.assertEqual(self.code(measure.measure, str(img)), "measure.timeout")

    def test_imagen_que_no_existe(self):
        self.assertEqual(self.code(measure.measure, str(self.tmp / "no.png")), "measure.unreadable")
        self.assertEqual(self.code(measure.yuv_planes, str(self.tmp / "no.png")), "measure.unreadable")

    def test_ffmpeg_da_menos_bytes(self):
        img = self.tmp / "a.png"
        img.write_bytes(b"x")
        with mock.patch("gimg.measure._ffmpeg", return_value=b"\x00" * 10):
            self.assertEqual(self.code(measure.yuv_planes, str(img)), "measure.unreadable")


@CON_FFMPEG
class ImagenesTests(Base):
    def test_no_es_una_imagen(self):
        bad = self.tmp / "no.png"
        bad.write_text("esto no es un png")
        self.assertEqual(self.code(measure.measure, str(bad)), "measure.tool_failed")

    def test_signalstats_de_blanco_y_negro(self):
        color_png(self.tmp / "w.png", "white")
        color_png(self.tmp / "k.png", "black")
        y_w, s_w = measure.signalstats(str(self.tmp / "w.png"))
        y_k, _ = measure.signalstats(str(self.tmp / "k.png"))
        self.assertGreater(y_w, 230)
        self.assertLess(y_k, 20)
        self.assertLess(s_w, 5)

    def test_signalstats_de_16_bits_en_escala_de_8(self):
        img = self.tmp / "g16.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x808080:s=64x32",
                        "-frames:v", "1", "-pix_fmt", "rgb48be", str(img)], check=True)
        yavg, _ = measure.signalstats(img)
        self.assertLess(yavg, 256)
        self.assertAlmostEqual(yavg, 126, delta=3)

    def test_rutas_que_ffmpeg_tomaria_por_opcion_o_protocolo(self):
        for name in ("-raro.png", "concat:x.png"):
            img = self.tmp / name
            color_png(self.tmp / "base.png", "white")
            shutil.copy(self.tmp / "base.png", img)
            res = measure.measure(str(img), ["#ffffff"])
            self.assertEqual(res["palette"]["pct"], 100.0, name)

    def test_pixeles_de_un_color_conocido(self):
        color_png(self.tmp / "r.png", "0x336699", "300x100")
        pix = measure.pixels(str(self.tmp / "r.png"))
        self.assertEqual(len(pix), 256 * 85)  # reducida a 256 de ancho
        for c, esperado in zip(pix[0], (0x33, 0x66, 0x99)):
            self.assertAlmostEqual(c, esperado, delta=2)

    def test_paleta_de_imagen_mitad_y_mitad(self):
        half_png(self.tmp / "h.png", "red", "blue")
        res = measure.measure(str(self.tmp / "h.png"), palette=["#ff0000", "#00ff00"])
        self.assertAlmostEqual(res["palette"]["pct"], 50.0, delta=3)
        self.assertAlmostEqual(res["palette"]["by_color"]["#ff0000"], 50.0, delta=3)
        self.assertEqual(res["palette"]["by_color"]["#00ff00"], 0.0)
        res = measure.measure(str(self.tmp / "h.png"), palette=["#ff0000", "#0000ff"])
        self.assertAlmostEqual(res["palette"]["pct"], 100.0, delta=1)

    def test_emd_cero_consigo_misma_y_mayor_que_cero_con_otra(self):
        color_png(self.tmp / "a.png", "0x204060")
        color_png(self.tmp / "b.png", "0xe0d0a0")
        res = measure.measure(str(self.tmp / "a.png"), refs=[str(self.tmp / "a.png"), str(self.tmp / "b.png")])
        misma, otra = res["emd"]
        self.assertEqual((misma["Y"], misma["Cb"], misma["Cr"]), (0.0, 0.0, 0.0))
        self.assertGreater(otra["Y"], 50)
        self.assertGreater(otra["Cb"], 0)
        self.assertGreater(otra["Cr"], 0)

    def test_emd_mediana_de_tres_y_sin_mediana_con_una(self):
        for name, c in (("a", "0x000000"), ("r1", "0x101010"), ("r2", "0x303030"), ("r3", "0xf0f0f0")):
            color_png(self.tmp / (name + ".png"), c)
        p = lambda n: str(self.tmp / (n + ".png"))  # noqa: E731
        res = measure.measure(p("a"), refs=[p("r1"), p("r2"), p("r3")])
        ys = sorted(r["Y"] for r in res["emd"])
        self.assertEqual(res["emd_median"]["Y"], ys[1])
        self.assertNotEqual(ys[0], ys[2])
        self.assertNotIn("emd_median", measure.measure(p("a"), refs=[p("r1")]))

    def test_emd_igual_que_la_formula_de_tarkor(self):
        # a: gris liso; b: mitad claro mitad oscuro. A mano: Y de a = YA; la CDF de a salta en YA y la de b en YL e YO.
        half_png(self.tmp / "b.png", "black", "white")
        color_png(self.tmp / "a.png", "gray")
        pa, pb = measure.yuv_planes(str(self.tmp / "a.png")), measure.yuv_planes(str(self.tmp / "b.png"))
        self.assertEqual(len(pa[0]), 160 * 64)
        ya = pa[0][0]
        yo, yl = min(pb[0]), max(pb[0])
        esperado = (ya - yo) * 0.5 + (yl - ya) * 0.5
        self.assertAlmostEqual(measure.emd(pa, pb)["Y"], esperado, delta=1.0)

    def test_contraste_blanco_sobre_negro_21(self):
        color_png(self.tmp / "k.png", "black", "200x100")
        res = measure.measure(str(self.tmp / "k.png"), zone="10,10,50,20", text="#ffffff")
        self.assertEqual(res["contrast"]["worst"], 21.0)
        self.assertEqual(res["contrast"]["zone"], [10, 10, 50, 20])
        self.assertEqual(res["contrast"]["text"], "#ffffff")

    def test_contraste_de_la_zona_y_no_de_la_imagen(self):
        half_png(self.tmp / "h.png", "black", "white", "200x100")
        izq = measure.measure(str(self.tmp / "h.png"), zone="0,0,90,100", text="#ffffff")["contrast"]
        der = measure.measure(str(self.tmp / "h.png"), zone="110,0,90,100", text="#ffffff")["contrast"]
        self.assertEqual(izq["worst"], 21.0)
        self.assertEqual(der["worst"], 1.0)

    def test_zona_fuera_de_la_imagen(self):
        color_png(self.tmp / "k.png", "black", "200x100")
        for zone in ("150,0,60,10", "0,90,10,20"):
            self.assertEqual(self.code(measure.measure, str(self.tmp / "k.png"), zone=zone, text="#ffffff"),
                             "measure.zone_outside", zone)
        # justo al borde cabe
        measure.measure(str(self.tmp / "k.png"), zone="150,0,50,100", text="#ffffff")


@CON_FFMPEG
class CliTests(Base):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_json_con_todo(self):
        half_png(self.tmp / "h.png", "black", "white", "200x100")
        color_png(self.tmp / "r.png", "gray", "200x100")
        code, out, _ = self.run_cli("measure", str(self.tmp / "h.png"), "--palette", "#000000,#ffffff",
                                    "--refs", str(self.tmp / "r.png"), "--zone", "0,0,90,100", "--text", "#ffffff",
                                    "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(set(data), {"image", "yavg", "satavg", "palette", "emd", "contrast"})
        self.assertAlmostEqual(data["palette"]["pct"], 100.0, delta=1)
        self.assertEqual(data["contrast"]["worst"], 21.0)

    def test_texto_legible_en_los_dos_idiomas(self):
        color_png(self.tmp / "k.png", "black", "200x100")
        for lang, palabra in (("es", "luma media"), ("en", "mean luma")):
            code, out, _ = self.run_cli("measure", str(self.tmp / "k.png"), "--lang", lang, "--zone", "0,0,10,10",
                                        "--text", "#ffffff")
            self.assertEqual(code, 0)
            self.assertIn(palabra, out)
            self.assertIn("21.0:1", out)

    def test_zona_sin_texto_es_error_del_cli(self):
        color_png(self.tmp / "k.png", "black")
        code, out, err = self.run_cli("measure", str(self.tmp / "k.png"), "--zone", "0,0,5,5", "--lang", "en")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("--zone and --text go together", err)

    def test_error_de_medida_sale_por_stderr(self):
        code, _, err = self.run_cli("measure", str(self.tmp / "no.png"), "--lang", "en")
        self.assertEqual(code, 1)
        self.assertIn("cannot read the image", err)

    def test_no_escribe_nada_junto_a_la_imagen(self):
        color_png(self.tmp / "k.png", "black")
        antes = sorted(os.listdir(self.tmp))
        self.run_cli("measure", str(self.tmp / "k.png"), "--palette", "#000000")
        self.assertEqual(sorted(os.listdir(self.tmp)), antes)


if __name__ == "__main__":
    unittest.main()
