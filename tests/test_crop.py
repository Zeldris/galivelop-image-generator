"""`gimg crop` (0.6.0): recorte de un intento a un intento derivado, por la función, la CLI y la API, y el remuestreo
(`export.resize`) con valores conocidos. Los errores se comprueban por su código."""
import json
import os
import unittest
from unittest import mock

from gimg import crop, export, orders, png
from gimg.errors import GimgError
from tests.test_server_read import EXAMPLE, NAME, ReadBase

W, H = 40, 20


def imagen(width=W, height=H):
    data = bytearray()
    for y in range(height):
        for x in range(width):
            data += bytes((x * 6 % 256, y * 12 % 256, (x + y) % 256, 255))
    return data


class CropBase(ReadBase):
    def setUp(self):
        super().setUp()
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        for name, w, h in (("tiny", 128, 64), ("sq", 64, 64), ("wide", 256, 128)):
            cfg["profiles"][name] = {k: v for k, v in dict(cfg["profiles"]["banner"], width=w, height=h).items()
                                     if k != "compose"}
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        orders.submit(NAME, {"key": "hoja", "profile": "tiny", "prompt": "una hoja 2x2", "references": ["refs/wolf.png"]})
        spec = {"seed": 7, "prompt": "una hoja 2x2, estilo", "params": {"width": W, "height": H, "steps": 6},
                "negative": "borroso", "references": ["refs/wolf.png"]}
        orders.add_attempt(NAME, "hoja", "tiny", spec)
        self.src = self.folder("hoja", "tiny") / "attempts" / "1.png"
        self.src.parent.mkdir(parents=True, exist_ok=True)
        self.src.write_bytes(png.rgba_bytes(W, H, imagen()))

    def folder(self, key, profile):
        return orders._order_dir(NAME, key, profile)

    def code(self, *args, **kw):
        with self.assertRaises(GimgError) as cm:
            crop.crop(NAME, *args, **kw)
        return cm.exception.code

    def snapshot(self):
        return self.src.read_bytes(), orders.get(NAME, "hoja", "tiny")["attempts"][0]


class CropTests(CropBase):
    def test_proporcion_bloqueada_sale_del_tamano_del_perfil(self):
        res = crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 40, 20])
        made = res["attempt"]
        self.assertEqual((res["profile"], res["key"], res["created"]), ("tiny", "hoja", False))
        self.assertEqual((made["id"], made["state"], made["image"]), (2, "new", "attempts/2.png"))
        self.assertEqual(png.size(self.folder("hoja", "tiny") / "attempts" / "2.png"), (128, 64))
        self.assertEqual((made["params"]["width"], made["params"]["height"], made["params"]["steps"]), (128, 64, 6))
        self.assertEqual((made["seed"], made["prompt"], made["negative"], made["references"]),
                         (7, "una hoja 2x2, estilo", "borroso", ["refs/wolf.png"]))
        self.assertEqual(made["derivedFrom"], {"profile": "tiny", "key": "hoja", "attempt": 1,
                                               "box": [0, 0, 40, 20], "lockRatio": True})
        for absent in ("raw", "compose", "composeError", "queueEntry"):
            self.assertNotIn(absent, made)
        self.assertEqual(orders.get(NAME, "hoja", "tiny")["attempts"][1], made)

    def test_el_original_queda_intacto(self):
        before = self.snapshot()
        crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 10])
        crop.crop(NAME, "hoja", "tiny", 1, [4, 2, 14, 12], lock_ratio=False)
        self.assertEqual(self.snapshot(), before)

    def test_repetir_la_caja_da_la_misma_imagen(self):
        first = crop.crop(NAME, "hoja", "tiny", 1, [2, 2, 22, 12])["attempt"]
        again = crop.crop(NAME, "hoja", "tiny", 1, first["derivedFrom"]["box"])["attempt"]
        base = self.folder("hoja", "tiny")
        self.assertEqual((first["id"], again["id"]), (2, 3))
        self.assertEqual((base / first["image"]).read_bytes(), (base / again["image"]).read_bytes())

    def test_libre_es_el_tamano_de_la_caja_sin_remuestrear(self):
        made = crop.crop(NAME, "hoja", "tiny", 1, [4, 2, 14, 12], lock_ratio=False)["attempt"]
        w, h, pixels = png.read_rgba(self.folder("hoja", "tiny") / made["image"])
        self.assertEqual((w, h), (10, 10))
        self.assertEqual(pixels, export.crop_box(W, H, imagen(), (4, 2, 10, 10)))
        self.assertEqual((made["params"]["width"], made["params"]["height"]), (10, 10))
        self.assertIs(made["derivedFrom"]["lockRatio"], False)

    def test_un_derivado_se_puede_recortar_y_elegir(self):
        made = crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 40, 20])["attempt"]
        again = crop.crop(NAME, "hoja", "tiny", made["id"], [0, 0, 128, 64])["attempt"]
        self.assertEqual(again["derivedFrom"]["attempt"], made["id"])
        self.assertEqual(orders.choose(NAME, "hoja", "tiny", again["id"]), {"old": None, "new": again["id"]})

    def test_un_borrador_derivado_sigue_siendo_borrador(self):
        orders.add_attempt(NAME, "hoja", "tiny", {"seed": 1, "prompt": "p", "params": {}, "draft": True})
        draft = orders.get(NAME, "hoja", "tiny")["attempts"][1]
        (self.folder("hoja", "tiny") / draft["image"]).write_bytes(png.rgba_bytes(W, H, imagen()))
        made = crop.crop(NAME, "hoja", "tiny", draft["id"], [0, 0, 40, 20])["attempt"]
        self.assertIs(made["draft"], True)
        with self.assertRaises(GimgError) as cm:
            orders.choose(NAME, "hoja", "tiny", made["id"])
        self.assertEqual(cm.exception.code, "order.choose_draft")

    def test_usa_la_imagen_cruda_si_la_hay(self):
        raw = self.folder("hoja", "tiny") / "attempts" / "q9.raw.png"
        raw.write_bytes(png.rgba_bytes(8, 4, imagen(8, 4)))
        order_file = self.folder("hoja", "tiny") / "order.json"
        record = json.loads(order_file.read_text())
        record["attempts"][0]["raw"] = "attempts/q9.raw.png"
        order_file.write_text(json.dumps(record))
        made = crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 8, 4], lock_ratio=False)["attempt"]
        self.assertEqual(png.size(self.folder("hoja", "tiny") / made["image"]), (8, 4))
        self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 40, 20]), "crop.outside")


class DestinoTests(CropBase):
    def test_a_un_pedido_nuevo(self):
        res = crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20], to={"profile": "sq", "key": "icono"})
        self.assertEqual((res["profile"], res["key"], res["created"]), ("sq", "icono", True))
        dest = orders.get(NAME, "icono", "sq")
        self.assertEqual(dest["prompt"], "una hoja 2x2")
        self.assertEqual(dest["attempts"], [res["attempt"]])
        self.assertEqual(png.size(self.folder("icono", "sq") / "attempts" / "1.png"), (64, 64))
        self.assertEqual(res["attempt"]["derivedFrom"]["key"], "hoja")
        self.assertEqual(len(orders.get(NAME, "hoja", "tiny")["attempts"]), 1)

    def test_a_un_pedido_existente(self):
        to = {"profile": "sq", "key": "icono"}
        crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20], to=to)
        res = crop.crop(NAME, "hoja", "tiny", 1, [20, 0, 40, 20], to=to)
        self.assertEqual((res["created"], res["attempt"]["id"]), (False, 2))

    def test_la_proporcion_es_la_del_perfil_de_destino(self):
        self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 20, 10], to={"profile": "sq", "key": "i"}),
                         "crop.ratio_mismatch")
        res = crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 10], to={"profile": "wide", "key": "i"})
        self.assertEqual(png.size(self.folder("i", "wide") / res["attempt"]["image"]), (256, 128))

    def test_perfil_o_destino_invalido_no_crea_nada(self):
        self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 20, 20], to={"profile": "nada", "key": "i"}),
                         "order.profile_unknown")
        for bad in ("sq", {"profile": "sq"}, {"profile": "sq", "key": "i", "x": 1}, {"profile": 3, "key": "i"}):
            self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 20, 20], to=bad), "crop.bad_target")
        self.assertEqual([o["key"] for o in orders.list_orders(NAME)], ["hoja"])


class ErrorTests(CropBase):
    def test_cada_error_por_su_codigo(self):
        casos = [
            ("crop.bad_box", [0, 0, 40]), ("crop.bad_box", "0,0,40,20"), ("crop.bad_box", [0, 0, 40, "20"]),
            ("crop.bad_box", [0, 0, 40.0, 20]), ("crop.bad_box", [True, 0, 40, 20]), ("crop.bad_box", None),
            ("crop.bad_box", [5, 0, 5, 20]), ("crop.bad_box", [0, 9, 40, 9]), ("crop.bad_box", [10, 0, 5, 20]),
            ("crop.outside", [-2, 0, 38, 20]), ("crop.outside", [0, -1, 40, 19]),
            ("crop.outside", [0, 0, 42, 21]), ("crop.outside", [0, 0, 40, 21]),
            ("crop.ratio_mismatch", [0, 0, 20, 20]), ("crop.ratio_mismatch", [0, 0, 40, 19]),
        ]
        for code, box in casos:
            with self.subTest(box=box):
                before = self.snapshot()
                self.assertEqual(self.code("hoja", "tiny", 1, box), code)
                self.assertEqual(self.snapshot(), before)
        self.assertEqual(sorted(p.name for p in (self.folder("hoja", "tiny") / "attempts").iterdir()), ["1.png"])

    def test_el_error_nombra_el_tamano_y_las_proporciones(self):
        with self.assertRaises(GimgError) as cm:
            crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 41, 20])
        self.assertEqual((cm.exception.params["width"], cm.exception.params["height"]), (W, H))
        with self.assertRaises(GimgError) as cm:
            crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20])
        self.assertEqual((cm.exception.params["box_ratio"], cm.exception.params["ratio"]), ("1.000", "2.000"))

    def test_libre_no_pide_proporcion(self):
        crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20], lock_ratio=False)

    def test_tolerancia_del_uno_por_ciento(self):
        orders.submit(NAME, {"key": "g", "profile": "wide", "prompt": "x"})
        big = self.folder("hoja", "tiny") / "attempts" / "1.png"
        big.write_bytes(png.rgba_bytes(210, 100, imagen(210, 100)))
        crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 201, 100])  # 2,01 frente a 2: dentro del 1 %
        self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 205, 100]), "crop.ratio_mismatch")

    def test_intento_o_pedido_desconocido(self):
        self.assertEqual(self.code("hoja", "tiny", 9, [0, 0, 40, 20]), "order.attempt_unknown")
        self.assertEqual(self.code("nada", "tiny", 1, [0, 0, 40, 20]), "order.unknown")

    def test_si_falla_al_guardar_no_queda_ni_archivo_ni_registro(self):
        before = orders.get(NAME, "hoja", "tiny")
        with mock.patch("gimg.fsutil.write_json", side_effect=OSError("disco lleno")):
            self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 40, 20]), "crop.write_failed")
        self.assertEqual(orders.get(NAME, "hoja", "tiny"), before)
        self.assertEqual(sorted(p.name for p in (self.folder("hoja", "tiny") / "attempts").iterdir()), ["1.png"])

    def test_si_falla_la_imagen_no_queda_registro(self):
        before = orders.get(NAME, "hoja", "tiny")
        with mock.patch("gimg.orders.os.replace", side_effect=OSError(28, "sin espacio")):
            self.assertEqual(self.code("hoja", "tiny", 1, [0, 0, 40, 20]), "crop.write_failed")
        self.assertEqual(orders.get(NAME, "hoja", "tiny"), before)
        self.assertEqual(sorted(p.name for p in (self.folder("hoja", "tiny") / "attempts").iterdir()), ["1.png"])

    def test_el_resto_de_un_recorte_matado_se_limpia_y_el_del_motor_no(self):
        attempts = self.folder("hoja", "tiny") / "attempts"
        (attempts / ".2.crop.k1ll3d.tmp").write_bytes(b"a medias")
        (attempts / ".q3.png.motor.tmp").write_bytes(b"lo escribe el worker")
        crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 40, 20])
        self.assertEqual(sorted(p.name for p in attempts.iterdir()), [".q3.png.motor.tmp", "1.png", "2.png"])

    def test_la_limpieza_solo_toca_los_temporales_de_recorte_con_su_forma(self):
        attempts = self.folder("hoja", "tiny") / "attempts"
        ajeno = attempts / ".notas.crop.guardado.tmp"
        ajeno.write_bytes(b"de otro")
        (attempts / ".2.crop.k1ll3d.tmp").write_bytes(b"a medias")
        crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 40, 20])
        self.assertEqual(sorted(p.name for p in attempts.iterdir()), [".notas.crop.guardado.tmp", "1.png", "2.png"])

    def test_destino_que_compone_se_rechaza_sin_escribir(self):
        cfg = json.loads((self.root / "galivelop-images.json").read_text())
        cfg["profiles"]["og"] = dict(cfg["profiles"]["tiny"], compose={"template": "t.svg", "fields": ["title"]})
        (self.root / "galivelop-images.json").write_text(json.dumps(cfg))
        for to in ({"profile": "og", "key": "hoja"}, {"profile": "og", "key": "nuevo"}):
            with self.subTest(to=to):
                with self.assertRaises(GimgError) as cm:
                    crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 40, 20], lock_ratio=False, to=to)
                self.assertEqual(cm.exception.code, "crop.compose_unsupported")
                self.assertEqual(cm.exception.params["profile"], to["profile"])
                with self.assertRaises(GimgError) as gone:
                    orders.get(NAME, to["key"], to["profile"])
                self.assertEqual(gone.exception.code, "order.unknown")
        self.assertEqual(len(orders.get(NAME, "hoja", "tiny")["attempts"]), 1)

    def test_pedido_de_destino_existente_no_se_pisa_aunque_get_no_lo_vea(self):
        orders.submit(NAME, {"key": "otro", "profile": "sq", "prompt": "ajeno"})
        real = orders.get

        def stale(project, key, profile):
            if key == "otro":
                raise GimgError("order.unknown", project=project, order=key, profile=profile)
            return real(project, key, profile)

        with mock.patch("gimg.orders.get", side_effect=stale):
            res = crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20], to={"profile": "sq", "key": "otro"})
        self.assertFalse(res["created"])
        self.assertEqual(real(NAME, "otro", "sq")["prompt"], "ajeno")

    def test_si_add_derived_falla_se_deshace_el_pedido_nuevo(self):
        to = {"profile": "sq", "key": "nuevo"}
        with mock.patch("gimg.orders.add_derived", side_effect=GimgError("order.spec_invalid", missing="x")):
            with self.assertRaises(GimgError) as cm:
                crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20], to=to)
        self.assertEqual(cm.exception.code, "order.spec_invalid")
        with self.assertRaises(GimgError) as gone:
            orders.get(NAME, "nuevo", "sq")
        self.assertEqual(gone.exception.code, "order.unknown")

    def test_oserror_al_crear_el_pedido_es_write_failed(self):
        with mock.patch("gimg.fsutil.write_json", side_effect=OSError("disco lleno")):
            with self.assertRaises(GimgError) as cm:
                crop.crop(NAME, "hoja", "tiny", 1, [0, 0, 20, 20], to={"profile": "sq", "key": "nuevo"})
        self.assertEqual(cm.exception.code, "crop.write_failed")
        self.assertEqual(cm.exception.params["reason"], "disco lleno")

    def test_tileable_solo_se_conserva_con_la_imagen_entera(self):
        spec = {"seed": 7, "prompt": "p", "params": {"width": W, "height": H, "tileable": "xy"}}
        orders.add_attempt(NAME, "hoja", "tiny", spec)
        (self.folder("hoja", "tiny") / "attempts" / "2.png").write_bytes(png.rgba_bytes(W, H, imagen()))
        whole = crop.crop(NAME, "hoja", "tiny", 2, [0, 0, 40, 20])["attempt"]
        part = crop.crop(NAME, "hoja", "tiny", 2, [0, 0, 20, 10])["attempt"]
        self.assertEqual(whole["params"].get("tileable"), "xy")
        self.assertNotIn("tileable", part["params"])


class ResizeTests(unittest.TestCase):
    def test_mismo_tamano_es_una_copia(self):
        data = imagen(3, 2)
        self.assertEqual(export.resize(3, 2, data, 3, 2), data)

    def test_reducir_promedia_el_area(self):
        data = bytearray([0, 0, 0, 255, 200, 100, 40, 255, 100, 50, 20, 255, 100, 50, 20, 255])
        self.assertEqual(export.resize(2, 2, data, 1, 1), bytearray([100, 50, 20, 255]))
        fila = bytearray(b"".join(bytes((v, v, v, 255)) for v in (0, 100, 200, 50)))
        self.assertEqual(export.resize(4, 1, fila, 2, 1), bytearray([50, 50, 50, 255, 125, 125, 125, 255]))

    def test_ampliar_es_bilineal(self):
        fila = bytearray([0, 0, 0, 255, 100, 200, 40, 255])
        self.assertEqual(export.resize(2, 1, fila, 4, 1),
                         bytearray([0, 0, 0, 255, 25, 50, 10, 255, 75, 150, 30, 255, 100, 200, 40, 255]))
        col = bytearray([0, 0, 0, 255, 100, 100, 100, 255])
        self.assertEqual(export.resize(1, 2, col, 1, 4)[::4], bytearray([0, 25, 75, 100]))

    def test_un_eje_se_reduce_y_el_otro_se_amplia(self):
        data = bytearray([0, 0, 0, 255, 100, 100, 100, 255, 100, 100, 100, 255, 200, 200, 200, 255])  # 2x2
        out = export.resize(2, 2, data, 3, 1)
        self.assertEqual(len(out), 12)
        self.assertEqual(out[3::4], bytearray([255, 255, 255]))
        self.assertEqual(out[0], 50)
        self.assertEqual(out[8], 150)

    def test_alfa_premultiplicado(self):
        data = bytearray([255, 0, 0, 255, 0, 0, 0, 0])
        self.assertEqual(export.resize(2, 1, data, 1, 1), bytearray([255, 0, 0, 128]))
        self.assertEqual(export.resize(2, 1, data, 3, 1)[:4], bytearray([255, 0, 0, 255]))

    def test_medida_invalida(self):
        with self.assertRaises(ValueError):
            export.resize(2, 2, imagen(2, 2), 0, 2)


class CliTests(CropBase):
    def run_cli(self, *argv):
        import contextlib
        import io
        from gimg import cli
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["--lang", "es", *argv])
        return code, out.getvalue(), err.getvalue()

    def test_salida_de_texto(self):
        code, out, err = self.run_cli("crop", NAME, "hoja", "tiny", "1", "--box", "0,0,40,20")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Intento derivado 2 en hoja (tiny): 128x64, caja 0,0,40,20.", out)

    def test_libre_y_json(self):
        code, out, _ = self.run_cli("--json", "crop", NAME, "hoja", "tiny", "1", "--box", "4,2,14,12", "--free")
        self.assertEqual(code, 0)
        res = json.loads(out)
        self.assertEqual((res["attempt"]["params"]["width"], res["attempt"]["derivedFrom"]["lockRatio"]), (10, False))

    def test_to_y_to_profile(self):
        code, out, _ = self.run_cli("crop", NAME, "hoja", "tiny", "1", "--box", "0,0,20,20",
                                    "--to", "icono", "--to-profile", "sq")
        self.assertEqual(code, 0)
        self.assertIn("icono (sq)", out)
        self.assertIn("no existía", out)
        code, out, _ = self.run_cli("--json", "crop", NAME, "hoja", "tiny", "1", "--box", "0,0,20,20", "--to-profile", "sq")
        self.assertEqual((json.loads(out)["key"], json.loads(out)["profile"]), ("hoja", "sq"))
        code, out, _ = self.run_cli("--json", "crop", NAME, "hoja", "tiny", "1", "--box", "0,0,20,10", "--to", "otra")
        self.assertEqual((json.loads(out)["key"], json.loads(out)["profile"]), ("otra", "tiny"))

    def test_to_vacio_no_se_toma_por_no_dado(self):
        code, out, err = self.run_cli("crop", NAME, "hoja", "tiny", "1", "--box", "0,0,20,20", "--to", "")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("no es un destino válido", err)

    def test_errores(self):
        for box, message in (("0,0,41,20", "se sale de la imagen"), ("0,0,20,20", "proporción"), ("a,b", "no es una caja"),
                             ("0,0,0,5", "no es una caja")):
            with self.subTest(box=box):
                code, out, err = self.run_cli("crop", NAME, "hoja", "tiny", "1", "--box=" + box)
                self.assertEqual((code, out), (1, ""))
                self.assertIn(message, err)

    def test_sin_caja_es_error_de_uso(self):
        code, _, err = self.run_cli("crop", NAME, "hoja", "tiny", "1")
        self.assertEqual(code, 2)
        self.assertIn("--box", err)


class ApiTests(CropBase):
    def url(self, key="hoja", profile="tiny", id=1):
        return self.order_url(key, profile, "/attempts/%d/crop" % id)

    def post(self, body, url=None):
        return self.call("POST", url or self.url(), headers={"Content-Type": "application/json"}, body=body)

    def test_recorta_y_devuelve_el_derivado(self):
        resp, payload = self.post({"box": [0, 0, 40, 20]})
        self.assertEqual(resp.status, 200, payload)
        res = json.loads(payload)
        self.assertEqual((res["profile"], res["key"], res["created"], res["attempt"]["id"]), ("tiny", "hoja", False, 2))
        self.assertEqual(res["attempt"]["derivedFrom"]["lockRatio"], True)
        self.assertEqual(orders.get(NAME, "hoja", "tiny")["attempts"][1], res["attempt"])

    def test_libre_y_a_otro_pedido(self):
        resp, payload = self.post({"box": [0, 0, 20, 20], "lockRatio": False, "to": {"profile": "sq", "key": "icono"}})
        self.assertEqual(resp.status, 200, payload)
        res = json.loads(payload)
        self.assertEqual((res["created"], res["key"], res["attempt"]["params"]["width"]), (True, "icono", 20))

    def test_errores_y_estados(self):
        for body, status, code in (
                ({"box": [0, 0, 40]}, 400, "crop.bad_box"), ({}, 400, "crop.bad_box"),
                ({"box": [0, 0, 41, 20]}, 400, "crop.outside"),
                ({"box": [0, 0, 20, 20]}, 400, "crop.ratio_mismatch"),
                ({"box": [0, 0, 40, 20], "to": "sq"}, 400, "crop.bad_target"),
                ({"box": [0, 0, 40, 20], "to": {"profile": "nada", "key": "i"}}, 404, "order.profile_unknown"),
                ({"box": [0, 0, 40, 20], "lockRatio": "si"}, 400, "api.bad_param"),
                ({"box": [0, 0, 40, 20], "otro": 1}, 400, "api.bad_param")):
            with self.subTest(body=body):
                resp, payload = self.post(body)
                self.err(resp, payload, status, code)
        resp, payload = self.post({"box": [0, 0, 40, 20]}, self.url(id=9))
        self.err(resp, payload, 404, "order.attempt_unknown")
        resp, payload = self.post({"box": [0, 0, 40, 20]}, self.url(key="nada"))
        self.err(resp, payload, 404, "order.unknown")

    def test_es_una_tarea_pesada(self):
        from gimg import server
        with mock.patch.object(server, "HEAVY_WAIT_S", 0.05):
            self.assertTrue(server._HEAVY.acquire(timeout=1))
            try:
                resp, payload = self.post({"box": [0, 0, 40, 20]})
            finally:
                server._HEAVY.release()
        self.err(resp, payload, 409, "api.heavy_busy")


if __name__ == "__main__":
    unittest.main()
