"""The brand workshop routes of the local API (`/api/projects/{p}/brand`), on temporary folders and the fake engine."""
import json
import os
import subprocess
import unittest
from pathlib import Path
from urllib.parse import quote

from gimg import brand, orders, paths
from tests.test_brand import FONT, HAS_WORDMARK, square_png
from tests.test_server_read import NAME
from tests.test_server_write import WriteBase

BASE = "/api/projects/%s/brand" % NAME
SLUG = "mi-marca"


def family_of(font):
    done = subprocess.run(["fc-scan", "--format", "%{family}\\n", font], capture_output=True, text=True)
    return done.stdout.split("\n")[0].split(",")[0].strip()


class BrandApiBase(WriteBase):
    def setUp(self):
        super().setUp()
        self.key, self.profile = self.make_order(count=1)
        order = orders.get(NAME, self.key, self.profile)
        self.attempt = order["attempts"][0]
        square_png(orders.attempt_image(NAME, self.key, self.profile, self.attempt), size=48)
        self.source = {"profile": self.profile, "key": self.key, "attempt": self.attempt["id"]}

    def shop(self):
        return paths.project_data_dir(NAME) / "brand" / SLUG

    def matte(self, **kw):
        return self.ok("POST", BASE + "/matte", dict({"name": "Mi Marca", "source": self.source}, **kw))

    def trace(self, mode="color", **kw):
        return self.ok("POST", BASE + "/trace", dict({"name": "Mi Marca", "mode": mode}, **kw))

    def declare_dir(self, rel="marca"):
        path = self.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        cfg["brand"] = dict(cfg.get("brand") or {}, dir=rel, palette=["#145a28", "#fac81e"])
        path.write_text(json.dumps(cfg))

    def full_shop(self):
        """The six pieces of the workshop, as the steps leave them."""
        self.matte()
        self.trace("color", colors=2)
        self.trace("mono")
        self.ok("POST", BASE + "/wordmark", {"name": "Mi Marca", "font": family_of(FONT)})
        for layout in ("h", "v"):
            self.ok("POST", BASE + "/lockup", {"name": "Mi Marca", "layout": layout})


class MatteTraceTests(BrandApiBase):
    def test_matte_writes_the_workshop_and_leaves_the_original(self):
        image = orders.attempt_image(NAME, self.key, self.profile, self.attempt)
        before = image.read_bytes()
        got = self.matte()
        self.assertTrue((self.shop() / (SLUG + "-emblema-alpha.png")).is_file())
        self.assertIsInstance(got, dict)
        self.assertEqual(image.read_bytes(), before)

    def test_matte_again_overwrites(self):
        self.matte()
        path = self.shop() / (SLUG + "-emblema-alpha.png")
        path.write_bytes(b"old")
        self.matte(tol=20)
        self.assertNotEqual(path.read_bytes(), b"old")

    def test_matte_rejections(self):
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca"}, 400, "api.bad_param")  # no source
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": dict(self.source, extra=1)}, 400, "api.bad_param")
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": self.source, "tol": "x"}, 400, "api.bad_param")
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": self.source, "bogus": 1}, 400, "api.bad_param")
        self.bad("POST", BASE + "/matte", {"name": "!!!", "source": self.source}, 400, "brand.bad_name")
        self.bad("POST", BASE + "/matte", {"name": "  ", "source": self.source}, 400, "brand.empty_text")
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": dict(self.source, attempt=99)}, 404,
                 "order.attempt_unknown")
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": dict(self.source, key="no/existe")}, 404,
                 "order.unknown")
        self.bad("POST", "/api/projects/nope/brand/matte", {"name": "Mi Marca", "source": self.source}, 404,
                 "project.unknown")
        self.assertFalse(self.shop().exists())

    def test_matte_source_cannot_leave_the_order_folder(self):
        record = orders.get(NAME, self.key, self.profile)
        path = orders._order_dir(NAME, self.key, self.profile) / "order.json"
        if not path.is_file():
            self.skipTest("order record layout changed")
        data = json.loads(path.read_text())
        data["attempts"][0]["image"] = "../../../../outside.png"
        path.write_text(json.dumps(data))
        self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": self.source}, 404, "api.not_found")
        self.assertIsNotNone(record)

    def test_trace_needs_the_matte_first(self):
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "color", "colors": 2}, 409, "brand.missing_piece")

    def test_trace_color_and_mono(self):
        self.matte()
        self.trace("color", colors=2)
        self.trace("mono")
        self.assertTrue((self.shop() / (SLUG + "-emblema.svg")).read_text().startswith("<svg"))
        self.assertTrue((self.shop() / (SLUG + "-emblema-mono.svg")).is_file())

    def test_trace_use_palette(self):
        self.matte()
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "color", "usePalette": True}, 400, "brand.no_palette")
        self.declare_dir()
        self.trace("color", usePalette=True)

    def test_trace_rejections(self):
        self.matte()
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "sepia"}, 400, "brand.bad_option")
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "mono", "colors": 2}, 400, "brand.bad_option")
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "mono", "usePalette": True}, 400, "brand.bad_option")
        self.declare_dir()
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "color", "colors": 2, "usePalette": True}, 400,
                 "brand.bad_option")
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "color", "usePalette": "yes"}, 400, "api.bad_param")
        self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "color", "colors": True}, 400, "api.bad_param")

    def test_colors_and_grow_have_a_cap(self):
        self.matte()
        for n in (65, 0):
            err = self.bad("POST", BASE + "/trace", {"name": "Mi Marca", "mode": "color", "colors": n}, 400, "brand.bad_option")
            self.assertIn("ncolores must be between 1 and 64", json.dumps(err))
        err = self.bad("POST", BASE + "/matte", {"name": "Mi Marca", "source": self.source, "grow": 33}, 400, "brand.bad_option")
        self.assertIn("grow between 0 and 32", json.dumps(err))


@unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
class WordmarkLockupTests(BrandApiBase):
    def test_wordmark_and_lockup(self):
        self.full_shop()
        for key in ("wordmark.svg", "lockup-h.svg", "lockup-v.svg"):
            self.assertTrue((self.shop() / ("%s-%s" % (SLUG, key))).is_file(), key)

    def test_wordmark_font_is_a_family_never_a_path(self):
        self.bad("POST", BASE + "/wordmark", {"name": "Mi Marca", "font": FONT}, 400, "brand.font_unknown")
        self.bad("POST", BASE + "/wordmark", {"name": "Mi Marca", "font": "/etc/passwd"}, 400, "brand.font_unknown")
        self.bad("POST", BASE + "/wordmark", {"name": "Mi Marca", "font": "Familia Que No Existe XYZ"}, 400,
                 "brand.font_unknown")
        self.bad("POST", BASE + "/wordmark", {"name": "Mi Marca"}, 400, "api.bad_param")
        self.assertFalse((self.shop() / (SLUG + "-wordmark.svg")).exists())

    def test_wordmark_text_defaults_to_the_name_and_can_be_given(self):
        path = self.shop() / (SLUG + "-wordmark.svg")
        self.ok("POST", BASE + "/wordmark", {"name": "Mi Marca", "font": family_of(FONT)})
        by_name = path.read_text()
        self.ok("POST", BASE + "/wordmark", {"name": "Mi Marca", "font": family_of(FONT), "text": "OTRA"})
        self.assertNotEqual(path.read_text(), by_name)  # the glyphs are outlines: another text, another drawing

    def test_lockup_rejections(self):
        self.bad("POST", BASE + "/lockup", {"name": "Mi Marca", "layout": "h"}, 409, "brand.missing_piece")
        self.matte()
        self.trace("color", colors=2)
        self.bad("POST", BASE + "/lockup", {"name": "Mi Marca", "layout": "h"}, 409, "brand.missing_piece")
        self.bad("POST", BASE + "/lockup", {"name": "Mi Marca", "layout": "x"}, 400, "brand.bad_option")
        self.bad("POST", BASE + "/lockup", {"name": "Mi Marca"}, 400, "api.bad_param")


class LockupNeedsPiecesTests(BrandApiBase):
    def test_lockup_without_pieces(self):
        self.bad("POST", BASE + "/lockup", {"name": "Mi Marca", "layout": "h"}, 409, "brand.missing_piece")
        self.bad("POST", BASE + "/lockup", {"name": "Mi Marca", "layout": "x"}, 400, "brand.bad_option")


class FilesTests(BrandApiBase):
    def test_list_empty_and_after_matte(self):
        self.assertEqual(self.ok("GET", BASE), [])
        self.matte()
        listed = self.ok("GET", BASE)
        self.assertEqual([(e["slug"], e["files"]) for e in listed], [(SLUG, ["emblema-alpha.png"])])

    def test_serve_png_and_svg_with_safe_headers(self):
        self.matte()
        self.trace("color", colors=2)
        resp, payload = self.get("%s/files/%s/emblema-alpha.png" % (BASE, SLUG))
        self.assertEqual((resp.status, resp.getheader("Content-Type")), (200, "image/png"))
        self.assertTrue(payload.startswith(b"\x89PNG"))
        resp, payload = self.get("%s/files/%s/emblema.svg" % (BASE, SLUG))
        self.assertEqual((resp.status, resp.getheader("Content-Type")), (200, "image/svg+xml"))
        self.assertIn("sandbox", resp.getheader("Content-Security-Policy"))
        self.assertEqual(resp.getheader("X-Content-Type-Options"), "nosniff")

    def test_only_the_system_files_are_served(self):
        self.matte()
        (self.shop() / "secret.txt").write_text("x")
        (self.shop() / (SLUG + "-extra.png")).write_bytes(b"x")
        for name, file in ((SLUG, "secret.txt"), (SLUG, "extra.png"), (SLUG, "..%2F..%2Fbrand-out"), (SLUG, "emblema.svg"),
                           ("..", "emblema-alpha.png"), ("Mi Marca", "emblema-alpha.png"), ("nada", "emblema-alpha.png")):
            resp, payload = self.get("%s/files/%s/%s" % (BASE, quote(name, safe=""), file))
            self.err(resp, payload, 404 if name != "Mi Marca" else 400, "api.not_found" if name != "Mi Marca" else "brand.bad_name")

    def test_unknown_project(self):
        resp, payload = self.get("/api/projects/nope/brand/files/%s/emblema.svg" % SLUG)
        self.err(resp, payload, 404, "project.unknown")


class SaveTests(BrandApiBase):
    def test_save_needs_every_piece_and_a_valid_dest(self):
        self.matte()
        self.bad("POST", BASE + "/save", {"name": "Mi Marca", "dest": "data"}, 409, "brand.missing_piece")
        self.bad("POST", BASE + "/save", {"name": "Mi Marca", "dest": "mars"}, 400, "brand.bad_option")
        self.bad("POST", BASE + "/save", {"name": "Mi Marca"}, 400, "api.bad_param")
        self.bad("POST", BASE + "/save", {"name": "Mi Marca", "dest": "data", "force": "yes"}, 400, "api.bad_param")

    def test_dest_project_without_brand_dir(self):
        self.bad("POST", BASE + "/save", {"name": "Mi Marca", "dest": "project"}, 400, "brand.dir_missing")

    def test_brand_dir_outside_the_root(self):
        self.declare_dir("../fuera")  # the schema refuses it: the project is invalid, nothing is written
        resp, payload = self.send("POST", BASE + "/save", {"name": "Mi Marca", "dest": "project"})
        self.err(resp, payload, 500, "project.config_invalid")
        self.assertFalse((self.root.parent / "fuera").exists())

    def test_brand_dir_symlink_leaving_the_root(self):
        outside = self.tmp / "fuera"
        outside.mkdir()
        (self.root / "marca").symlink_to(outside)
        self.declare_dir("marca")
        resp, payload = self.send("POST", BASE + "/save", {"name": "Mi Marca", "dest": "project"})
        self.err(resp, payload, 400, "path.outside")
        self.assertEqual(os.listdir(outside), [])

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_save_to_data_and_exists_without_force(self):
        self.full_shop()
        got = self.ok("POST", BASE + "/save", {"name": "Mi Marca", "dest": "data"})
        out = paths.project_data_dir(NAME) / "brand-out" / SLUG
        self.assertEqual(got["out_dir"], str(out))
        self.assertEqual(sorted(os.listdir(out)), sorted("%s-%s" % (SLUG, k) for k in brand.SYSTEM_FILES))
        self.assertEqual(got["overwritten"], [])
        self.bad("POST", BASE + "/save", {"name": "Mi Marca", "dest": "data"}, 409, "brand.exists")
        again = self.ok("POST", BASE + "/save", {"name": "Mi Marca", "dest": "data", "force": True})
        self.assertEqual(len(again["overwritten"]), len(brand.SYSTEM_FILES))

    @unittest.skipUnless(HAS_WORDMARK, "needs rsvg-convert and a .ttf/.otf font")
    def test_save_to_the_project(self):
        self.declare_dir("marca")
        self.full_shop()
        got = self.ok("POST", BASE + "/save", {"name": "Mi Marca", "dest": "project"})
        self.assertEqual(got["out_dir"], str(self.root / "marca"))
        self.assertTrue((self.root / "marca" / (SLUG + "-lockup-h.svg")).is_file())
        self.bad("POST", BASE + "/save", {"name": "Mi Marca", "dest": "project"}, 409, "brand.exists")


if __name__ == "__main__":
    unittest.main()
