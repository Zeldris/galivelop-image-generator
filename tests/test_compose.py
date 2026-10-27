"""Composition (F2.8, D28): `gimg/compose.py`.

The first half needs no tool: geometry, escaping, the path guard, the exact argument lists and the failures that come
before any tool runs (or because there is no tool). The second half runs `rsvg-convert` and `ffmpeg` on synthetic images
and reads pixels back; it is skipped when they are missing, except in the CI, where `ciInstall` installs them and a
missing one must fail (same pattern as `tests/test_pilot_scripts.py`)."""
import io
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from gimg import compose, png
from gimg.errors import GimgError, PathError

TIENE_FFMPEG = shutil.which("ffmpeg") is not None
TIENE_RSVG = shutil.which("rsvg-convert") is not None
EN_CI = os.environ.get("CI") == "true"
CON_HERRAMIENTAS = unittest.skipUnless(EN_CI or (TIENE_FFMPEG and TIENE_RSVG), "hacen falta ffmpeg y rsvg-convert")

LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 40">'
        '<rect width="100" height="40" fill="#ff0000"/></svg>')
GRAY = (128, 128, 128)


def striped_png(path, width, height, edge=24, left=(255, 0, 0), right=(0, 0, 255), middle=GRAY):
    """A synthetic raw image: gray with an `edge`-pixel column of `left` color on the left and of `right` on the right."""
    row = left * edge + middle * (width - 2 * edge) + right * edge
    data = png.SIGNATURE + png.chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) \
        + png.chunk(b"IDAT", zlib.compress((b"\x00" + bytes(row)) * height)) + png.chunk(b"IEND", b"")
    Path(path).write_bytes(data)


def pixels(path, width, height, fmt="rgb24"):
    """The decoded pixels of a PNG as `(x, y) -> tuple`, through ffmpeg."""
    bpp = {"rgb24": 3, "rgba": 4}[fmt]
    data = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", fmt, "-"],
                          capture_output=True, check=True).stdout
    assert len(data) == width * height * bpp, (len(data), width, height)
    return lambda x, y: tuple(data[(y * width + x) * bpp:(y * width + x + 1) * bpp])


def near(test, got, want, tol=6):
    test.assertTrue(all(abs(a - b) <= tol for a, b in zip(got, want)), "%s is not near %s" % (got, want))


class ProjectBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.root = self.tmp / "proj"
        self.root.mkdir()
        self.outside = self.tmp / "outside"
        self.outside.mkdir()
        self.work = self.tmp / "work"
        self.work.mkdir()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def profile(self, **extra):
        return dict({"width": 1280, "height": 640, "targetWidth": 1200, "targetHeight": 630}, **extra)


class LocaleTests(unittest.TestCase):
    PARAMS = {
        "bad_size": {"source": "0x5", "target": "1200x630"}, "bad_fit": {"fit": "stretch", "allowed": "cover, contain"},
        "field_unknown": {"field": "ghost"}, "template_missing": {"path": "brand/t.svg"},
        "logo_missing": {"path": "brand/l.svg"}, "svg_too_big": {"path": "brand/t.svg", "limit": 5000000},
        "svg_unreadable": {"path": "brand/t.svg", "reason": "not UTF-8"}, "no_logo": {"template": "brand/t.svg"},
        "bad_text": {"field": "title"}, "nothing_to_do": {"profile": "og"}, "tool_missing": {"tool": "ffmpeg"},
        "timeout": {"tool": "ffmpeg", "seconds": 120}, "tool_failed": {"tool": "ffmpeg", "reason": "Invalid data"},
        "write_failed": {"path": "out/q1.png", "reason": "No such file or directory"},
        "no_attempts": {"order": "hero", "profile": "og"}, "unexpected": {"reason": "KeyError: 'x'"},
    }

    def test_every_code_of_compose_py_has_a_text_in_both_languages_that_uses_its_parameters(self):
        source = (Path(compose.__file__)).read_text(encoding="utf-8")
        import re
        used = set(re.findall(r'"compose\.([a-z_]+)"', source)) - {"chunk_failed", "log_failed"}
        self.assertEqual(used, set(self.PARAMS))  # a new code has to be added here, with its parameters
        for lang in ("es", "en"):
            for code, params in self.PARAMS.items():
                text = GimgError("compose." + code, **params).message(lang)
                self.assertNotEqual(text, "error.compose." + code, (lang, code))
                for value in params.values():
                    self.assertIn(str(value), text, (lang, code))

    def test_the_two_languages_say_different_things(self):
        for code, params in self.PARAMS.items():
            self.assertNotEqual(GimgError("compose." + code, **params).message("es"),
                                GimgError("compose." + code, **params).message("en"), code)


class FitGeometryTests(unittest.TestCase):
    def test_cover_og_crops_the_sides(self):
        self.assertEqual(compose.fit_geometry(1280, 640, 1200, 630, "cover"), (1260, 630, 30, 0))

    def test_cover_wide_crops_top_and_bottom(self):
        self.assertEqual(compose.fit_geometry(1280, 768, 1200, 675, "cover"), (1200, 720, 0, 22))

    def test_cover_rounds_the_scaled_side_up(self):
        # 1283*630/640 = 1262.9...: rounded up to 1263 so the crop never runs out of pixels
        self.assertEqual(compose.fit_geometry(1283, 640, 1200, 630, "cover"), (1263, 630, 31, 0))
        self.assertEqual(compose.fit_geometry(640, 1283, 630, 1200, "cover"), (630, 1263, 0, 31))

    def test_cover_square_scales_only(self):
        self.assertEqual(compose.fit_geometry(1024, 1024, 1080, 1080, "cover"), (1080, 1080, 0, 0))

    def test_cover_same_size_changes_nothing(self):
        self.assertEqual(compose.fit_geometry(1200, 630, 1200, 630, "cover"), (1200, 630, 0, 0))

    def test_cover_always_reaches_the_target_on_both_sides(self):
        for src in ((1281, 641), (999, 1001), (64, 4096), (4096, 64), (1, 1)):
            for dst in ((1200, 630), (1080, 1080), (16, 4096), (3, 7)):
                sw, sh, x, y = compose.fit_geometry(*src, *dst, "cover")
                self.assertTrue(sw >= dst[0] and sh >= dst[1], (src, dst, sw, sh))
                self.assertTrue(0 <= x and x + dst[0] <= sw and 0 <= y and y + dst[1] <= sh, (src, dst))
                self.assertTrue(sw == dst[0] or sh == dst[1], (src, dst))

    def test_contain_wide_source_pads_top_and_bottom(self):
        self.assertEqual(compose.fit_geometry(1280, 640, 1200, 630, "contain"), (1200, 600, 0, 15))

    def test_contain_tall_source_pads_the_sides(self):
        self.assertEqual(compose.fit_geometry(640, 1280, 1200, 630, "contain"), (315, 630, 442, 0))

    def test_contain_never_exceeds_the_target(self):
        for src in ((1281, 641), (999, 1001), (64, 4096), (4096, 64), (1, 1)):
            for dst in ((1200, 630), (1080, 1080), (16, 4096), (3, 7)):
                sw, sh, x, y = compose.fit_geometry(*src, *dst, "contain")
                self.assertTrue(1 <= sw <= dst[0] and 1 <= sh <= dst[1], (src, dst, sw, sh))
                self.assertTrue(x >= 0 and y >= 0 and x + sw <= dst[0] and y + sh <= dst[1], (src, dst))

    def test_sizes_zero_or_negative_are_refused(self):
        for args in ((0, 640, 1200, 630), (1280, 0, 1200, 630), (1280, 640, 0, 630), (1280, 640, 1200, -1)):
            with self.assertRaises(GimgError) as cm:
                compose.fit_geometry(*args, "cover")
            self.assertEqual(cm.exception.code, "compose.bad_size", args)

    def test_unknown_fit_is_refused_with_its_name(self):
        with self.assertRaises(GimgError) as cm:
            compose.fit_geometry(10, 10, 10, 10, "stretch")
        self.assertEqual((cm.exception.code, cm.exception.params["fit"]), ("compose.bad_fit", "stretch"))


class SubstituteTests(unittest.TestCase):
    def test_xml_escape(self):
        self.assertEqual(compose.xml_escape("a & b <c> \"d\" 'e'"), "a &amp; b &lt;c&gt; &quot;d&quot; &apos;e&apos;")

    def test_xml_escape_drops_what_xml_cannot_carry(self):
        self.assertEqual(compose.xml_escape("a\x00b\x08c\x1fd￾e"), "abcde")
        self.assertEqual(compose.xml_escape("a\tb\nc\rd"), "a\tb\nc\rd")

    def test_xml_escape_drops_lone_surrogates_so_the_result_encodes_as_utf8(self):
        out = compose.xml_escape("a\ud800b\udfffc\udc00d")
        self.assertEqual(out, "abcd")
        out.encode("utf-8")
        self.assertEqual(compose.xml_escape("😀ñ"), "😀ñ")

    def test_values_are_escaped_in_text_and_in_attributes(self):
        out = compose.substitute('<text a="{{t}}">{{t}}</text>', {"t": '<&>"\''})
        self.assertEqual(out, '<text a="&lt;&amp;&gt;&quot;&apos;">&lt;&amp;&gt;&quot;&apos;</text>')

    def test_a_value_is_never_expanded_again(self):
        out = compose.substitute("{{a}}|{{b}}", {"a": "{{b}}", "b": "{{a}}"})
        self.assertEqual(out, "{{b}}|{{a}}")

    def test_a_value_with_a_logo_hole_stays_text(self):
        self.assertEqual(compose.substitute("{{title}}", {"title": "{{logo}}", "logo": "data:x"}), "{{logo}}")

    def test_unknown_hole_names_the_field(self):
        with self.assertRaises(GimgError) as cm:
            compose.substitute("<a>{{title}}{{ghost}}</a>", {"title": "x"})
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.field_unknown", {"field": "ghost"}))

    def test_empty_value_and_text_without_holes(self):
        self.assertEqual(compose.substitute("[{{a}}]", {"a": ""}), "[]")
        self.assertEqual(compose.substitute("{ {a} } {{ a }} {{1a}}", {}), "{ {a} } {{ a }} {{1a}}")

    def test_logo_data_uri_holds_the_svg_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            logo = Path(tmp) / "logo.svg"
            logo.write_text(LOGO, encoding="utf-8")
            uri = compose.logo_data_uri(logo)
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"))
        import base64
        self.assertEqual(base64.b64decode(uri.split(",", 1)[1]).decode("utf-8"), LOGO)
        self.assertEqual(compose.substitute('<image href="{{logo}}"/>', {"logo": uri}), '<image href="%s"/>' % uri)


class PlanTests(unittest.TestCase):
    def test_nothing_to_do_without_compose_and_target(self):
        self.assertIsNone(compose.plan_for({"width": 1280, "height": 640}, 1280, 640))
        self.assertIsNone(compose.plan_for({"width": 1280, "height": 640}, 640, 320))  # a draft: left as it is

    def test_nothing_to_do_when_the_target_is_the_raw_size(self):
        cfg = {"width": 1280, "height": 640, "targetWidth": 1280, "targetHeight": 640}
        self.assertIsNone(compose.plan_for(cfg, 1280, 640))

    def test_a_target_different_from_the_raw_size_is_a_plan_without_template(self):
        cfg = {"width": 1280, "height": 640, "targetWidth": 1200, "targetHeight": 630}
        self.assertEqual(compose.plan_for(cfg, 1280, 640), {"fit": "cover", "targetWidth": 1200, "targetHeight": 630})
        self.assertEqual(compose.plan_for(cfg, 640, 320)["targetWidth"], 1200)  # a draft goes up to the target

    def test_compose_is_always_a_plan_even_at_the_raw_size(self):
        cfg = {"width": 1280, "height": 640, "compose": {"template": "t.svg", "logo": "l.svg", "fit": "contain"}}
        self.assertEqual(compose.plan_for(cfg, 1280, 640),
                         {"fit": "contain", "targetWidth": 1280, "targetHeight": 640, "template": "t.svg",
                          "logo": "l.svg"})

    def test_target_size_falls_back_to_the_generation_size(self):
        self.assertEqual(compose.target_size({"width": 1280, "height": 640}), (1280, 640))
        self.assertEqual(compose.target_size({"width": 1280, "height": 640, "targetWidth": 8, "targetHeight": 9}), (8, 9))


class ArgvTests(unittest.TestCase):
    def test_rsvg(self):
        self.assertEqual(compose.rsvg_argv("/t/a.svg", "/t/l.png", 1200, 630),
                         ["rsvg-convert", "-w", "1200", "-h", "630", "-o", "/t/l.png", "/t/a.svg"])

    HEAD = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", "/t/raw.png"]
    TAIL = ["-map", "[out]", "-frames:v", "1", "-update", "1", "-map_metadata", "-1", "/t/out.png"]

    def test_ffmpeg_cover_with_layer(self):
        argv = compose.ffmpeg_argv("/t/raw.png", "/t/layer.png", "/t/out.png", (1200, 630, 1260, 630, 30, 0), "cover")
        self.assertEqual(argv, self.HEAD + ["-i", "/t/layer.png", "-filter_complex",
                                            "[0:v]scale=1260:630:flags=lanczos,crop=1200:630:30:0[b];"
                                            "[b][1:v]overlay=0:0:format=auto,format=rgb24[out]"] + self.TAIL)

    def test_ffmpeg_cover_without_layer(self):
        argv = compose.ffmpeg_argv("/t/raw.png", None, "/t/out.png", (1200, 630, 1200, 720, 0, 22), "cover")
        self.assertEqual(argv, self.HEAD + ["-filter_complex",
                                            "[0:v]scale=1200:720:flags=lanczos,crop=1200:630:0:22,format=rgb24[out]"]
                         + self.TAIL)

    def test_ffmpeg_contain_with_layer(self):
        argv = compose.ffmpeg_argv("/t/raw.png", "/t/layer.png", "/t/out.png", (1200, 630, 1200, 600, 0, 15), "contain")
        self.assertEqual(argv, self.HEAD + ["-i", "/t/layer.png", "-filter_complex",
                                            "[0:v]scale=1200:600:flags=lanczos,format=rgba,pad=1200:630:0:15:color=black@0[b];"
                                            "[b][1:v]overlay=0:0:format=auto,format=rgba[out]"] + self.TAIL)

    def test_ffmpeg_contain_without_layer(self):
        argv = compose.ffmpeg_argv("/t/raw.png", None, "/t/out.png", (1200, 630, 1200, 600, 0, 15), "contain")
        self.assertEqual(argv[-len(self.TAIL) - 2], "-filter_complex")
        self.assertEqual(argv[-len(self.TAIL) - 1],
                         "[0:v]scale=1200:600:flags=lanczos,format=rgba,pad=1200:630:0:15:color=black@0[out]")

    def test_the_arguments_are_a_list_and_never_go_through_a_shell(self):
        argv = compose.ffmpeg_argv("/t/a b;rm -rf.png", None, "/t/o.png", (2, 2, 2, 2, 0, 0), "cover")
        self.assertIn("/t/a b;rm -rf.png", argv)


class AssetGuardTests(ProjectBase):
    """Every case the D25 guard has to refuse, for the template and for the logo (REVIEW.md, «Rutas y nombres de archivo»)."""

    def setUp(self):
        super().setUp()
        self.write("brand/t.svg", "<svg/>")
        self.write("brand/l.svg", LOGO)

    def refused(self, field, rel):
        cfg = {"template": "brand/t.svg", "logo": "brand/l.svg"}
        cfg[field] = rel
        with self.assertRaises(GimgError) as cm:
            compose.resolve_assets(self.root, cfg)
        return cm.exception

    def check(self, rel, code):
        for field in ("template", "logo"):
            err = self.refused(field, rel)
            self.assertEqual(err.code, code, (field, rel))

    def test_valid_assets_resolve_inside_the_project(self):
        template, logo = compose.resolve_assets(self.root, {"template": "brand/t.svg", "logo": "brand/l.svg"})
        self.assertEqual((template, logo), (self.root / "brand/t.svg", self.root / "brand/l.svg"))
        self.assertEqual(compose.resolve_assets(self.root, {"template": "brand/t.svg"})[1], None)

    def test_dotdot_is_refused(self):
        self.check("../outside/x.svg", "path.dotdot")
        self.check("brand/../../x.svg", "path.dotdot")

    def test_absolute_path_is_refused(self):
        self.check(str(self.outside / "x.svg"), "path.absolute")

    def test_tilde_is_refused(self):
        self.check("~/x.svg", "path.tilde")
        self.check("~root/x.svg", "path.tilde")

    def test_newline_is_refused(self):
        self.check("brand/t.svg\n", "path.control")
        self.check("brand/\nt.svg", "path.control")

    def test_nul_is_refused(self):
        self.check("brand/t.svg\x00.png", "path.nul")

    def test_backslash_is_refused(self):
        self.check("brand\\t.svg", "path.backslash")

    def test_guard_errors_are_path_errors(self):
        self.assertIsInstance(self.refused("template", "../x.svg"), PathError)

    def test_a_link_that_leaves_the_project_is_refused(self):
        (self.outside / "x.svg").write_text("<svg/>", encoding="utf-8")
        os.symlink(self.outside / "x.svg", self.root / "brand" / "link.svg")
        self.check("brand/link.svg", "path.outside")

    def test_a_folder_that_is_a_link_out_is_refused(self):
        (self.outside / "x.svg").write_text("<svg/>", encoding="utf-8")
        os.symlink(self.outside, self.root / "brand" / "dir")
        self.check("brand/dir/x.svg", "path.outside")

    def test_a_link_that_stays_inside_is_fine(self):
        os.symlink(self.root / "brand" / "t.svg", self.root / "brand" / "alias.svg")
        template, _ = compose.resolve_assets(self.root, {"template": "brand/alias.svg"})
        self.assertEqual(template, self.root / "brand" / "t.svg")

    def test_a_folder_instead_of_a_file(self):
        (self.root / "brand" / "folder.svg").mkdir()
        self.assertEqual(self.refused("template", "brand/folder.svg").code, "compose.template_missing")
        self.assertEqual(self.refused("logo", "brand/folder.svg").code, "compose.logo_missing")

    def test_a_missing_file_says_which_path(self):
        err = self.refused("template", "brand/nope.svg")
        self.assertEqual((err.code, err.params), ("compose.template_missing", {"path": "brand/nope.svg"}))
        err = self.refused("logo", "brand/nope.svg")
        self.assertEqual((err.code, err.params), ("compose.logo_missing", {"path": "brand/nope.svg"}))

    def test_a_file_that_is_too_big(self):
        self.write("brand/big.svg", "<svg>" + " " * 100 + "</svg>")
        with mock.patch.object(compose, "MAX_SVG_BYTES", 50):
            for field in ("template", "logo"):
                err = self.refused(field, "brand/big.svg")
                self.assertEqual((err.code, err.params), ("compose.svg_too_big", {"path": "brand/big.svg", "limit": 50}))

    def test_a_file_at_the_limit_is_fine(self):
        self.write("brand/ok.svg", "x" * 50)
        with mock.patch.object(compose, "MAX_SVG_BYTES", 50):
            compose.resolve_assets(self.root, {"template": "brand/ok.svg"})
            self.assertEqual(compose._read_svg(self.root / "brand" / "ok.svg"), "x" * 50)

    def test_the_size_is_checked_again_when_reading(self):
        # the file grows between the check and the read: the read itself is capped
        self.write("brand/grows.svg", "x" * 60)
        with mock.patch.object(compose, "MAX_SVG_BYTES", 50):
            with self.assertRaises(GimgError) as cm:
                compose._read_svg(self.root / "brand" / "grows.svg")
        self.assertEqual(cm.exception.code, "compose.svg_too_big")

    def test_a_file_that_is_not_utf8(self):
        (self.root / "brand" / "latin.svg").write_bytes("<svg>ñ</svg>".encode("latin-1"))
        with self.assertRaises(GimgError) as cm:
            compose._read_svg(self.root / "brand" / "latin.svg")
        self.assertEqual((cm.exception.code, cm.exception.params["reason"]), ("compose.svg_unreadable", "not UTF-8"))


class FailuresBeforeToolsTests(ProjectBase):
    """What `render` refuses without running anything, and what it does when there is no tool."""

    def setUp(self):
        super().setUp()
        self.raw = self.work / "raw.png"
        striped_png(self.raw, 1280, 640)
        self.out = self.work / "out.png"

    def render(self, profile, text=None):
        return compose.render(self.root, profile, self.raw, self.out, text or {})

    def no_leftovers(self):
        self.assertFalse(self.out.exists())
        self.assertEqual(sorted(p.name for p in self.work.iterdir()), ["raw.png"])

    def test_the_template_uses_logo_but_the_profile_has_none(self):
        self.write("t.svg", '<svg xmlns="http://www.w3.org/2000/svg"><image href="{{logo}}"/></svg>')
        with self.assertRaises(GimgError) as cm:
            self.render(self.profile(compose={"template": "t.svg"}))
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.no_logo", {"template": "t.svg"}))
        self.no_leftovers()

    def test_a_hole_that_is_not_a_field(self):
        self.write("t.svg", "<svg>{{title}}{{ghost}}</svg>")
        with self.assertRaises(GimgError) as cm:
            self.render(self.profile(compose={"template": "t.svg", "fields": ["title"]}), {"title": "x"})
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.field_unknown", {"field": "ghost"}))
        self.no_leftovers()

    def test_a_text_that_is_not_a_string(self):
        self.write("t.svg", "<svg>{{title}}</svg>")
        with self.assertRaises(GimgError) as cm:
            self.render(self.profile(compose={"template": "t.svg", "fields": ["title"]}), {"title": 3})
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.bad_text", {"field": "title"}))

    def test_a_bad_path_in_the_configuration_is_refused_before_anything_runs(self):
        for rel, code in (("../x.svg", "path.dotdot"), ("/x.svg", "path.absolute"), ("~/x.svg", "path.tilde"),
                          ("t\n.svg", "path.control"), ("t\x00.svg", "path.nul")):
            with self.assertRaises(GimgError) as cm:
                self.render(self.profile(compose={"template": rel}))
            self.assertEqual(cm.exception.code, code, rel)
        self.no_leftovers()

    def test_nothing_to_do_names_the_profile(self):
        with self.assertRaises(GimgError) as cm:
            compose.render(self.root, {"width": 1280, "height": 640}, self.raw, self.out, {}, profile="og")
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.nothing_to_do", {"profile": "og"}))

    def test_the_raw_image_has_to_be_a_png(self):
        self.raw.write_bytes(b"not a png")
        with self.assertRaises(GimgError) as cm:
            self.render(self.profile())
        self.assertEqual(cm.exception.code, "png.invalid")

    def test_a_missing_output_folder_is_a_write_failure_not_an_oserror(self):
        out = self.work / "nope" / "q1.png"
        with self.assertRaises(GimgError) as cm:
            compose.render(self.root, self.profile(), self.raw, out, {})
        self.assertEqual(cm.exception.code, "compose.write_failed")
        self.assertEqual(cm.exception.params["path"], str(out))
        self.assertTrue(cm.exception.params["reason"])

    def test_a_write_that_fails_midway_is_a_write_failure(self):
        self.write("t.svg", "<svg/>")
        with mock.patch.object(Path, "write_text", side_effect=OSError(28, "No space left on device")):
            with self.assertRaises(GimgError) as cm:
                self.render(self.profile(compose={"template": "t.svg"}))
        self.assertEqual((cm.exception.code, cm.exception.params["reason"]),
                         ("compose.write_failed", "No space left on device"))

    def test_without_rsvg_nothing_is_written(self):
        self.write("t.svg", "<svg/>")
        with mock.patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaises(GimgError) as cm:
                self.render(self.profile(compose={"template": "t.svg"}))
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.tool_missing", {"tool": "rsvg-convert"}))
        self.no_leftovers()

    def test_without_ffmpeg_a_scale_alone_names_ffmpeg(self):
        with mock.patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaises(GimgError) as cm:
                self.render(self.profile())
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.tool_missing", {"tool": "ffmpeg"}))
        self.no_leftovers()

    def test_a_tool_that_takes_too_long(self):
        import subprocess as sp
        with mock.patch.object(compose.shutil, "which", return_value="/bin/x"), \
                mock.patch.object(compose.subprocess, "run", side_effect=sp.TimeoutExpired("ffmpeg", 120)):
            with self.assertRaises(GimgError) as cm:
                compose._run(["ffmpeg"], "ffmpeg")
        self.assertEqual((cm.exception.code, cm.exception.params), ("compose.timeout", {"tool": "ffmpeg", "seconds": 120}))

    def test_a_tool_that_fails_gives_the_last_line_of_stderr_cut_at_300(self):
        failed = subprocess.CompletedProcess(["x"], 1, b"", b"first\n\n" + b"y" * 400 + b"\n \n")
        with mock.patch.object(compose.shutil, "which", return_value="/bin/x"), \
                mock.patch.object(compose.subprocess, "run", return_value=failed):
            with self.assertRaises(GimgError) as cm:
                compose._run(["x"], "rsvg-convert")
        self.assertEqual(cm.exception.code, "compose.tool_failed")
        self.assertEqual(cm.exception.params, {"tool": "rsvg-convert", "reason": "y" * 300})

    def test_a_tool_that_fails_without_a_message_says_the_exit_code(self):
        failed = subprocess.CompletedProcess(["x"], 3, b"", b"")
        with mock.patch.object(compose.shutil, "which", return_value="/bin/x"), \
                mock.patch.object(compose.subprocess, "run", return_value=failed):
            with self.assertRaises(GimgError) as cm:
                compose._run(["x"], "ffmpeg")
        self.assertEqual(cm.exception.params["reason"], "exit code 3")

    def test_the_tools_run_without_a_shell_and_without_input(self):
        done = subprocess.CompletedProcess(["x"], 0, b"", b"")
        with mock.patch.object(compose.shutil, "which", return_value="/bin/x"), \
                mock.patch.object(compose.subprocess, "run", return_value=done) as run:
            compose._run(["ffmpeg", "-i", "a;b"], "ffmpeg")
        args, kwargs = run.call_args
        self.assertEqual(args[0], ["ffmpeg", "-i", "a;b"])
        self.assertEqual((kwargs.get("shell", False), kwargs["stdin"], kwargs["timeout"]),
                         (False, subprocess.DEVNULL, compose.TIMEOUT_S))


@CON_HERRAMIENTAS
class RenderTests(ProjectBase):
    TEMPLATE = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
                '<rect x="100" y="100" width="50" height="50" fill="#00ff00"/>'
                '<text x="400" y="300" font-size="40">{{title}}</text></svg>')

    def setUp(self):
        super().setUp()
        self.raw = self.work / "raw.png"
        striped_png(self.raw, 1280, 640)
        self.out = self.work / "out.png"

    def leftovers(self):
        return sorted(p.name for p in self.work.iterdir() if p.name not in ("raw.png", "out.png"))

    def test_composes_a_raw_image_to_the_target_size_with_text_that_needs_escaping(self):
        self.write("t.svg", self.TEMPLATE)
        profile = self.profile(compose={"template": "t.svg", "fields": ["title", "subtitle"]})
        info = compose.render(self.root, profile, self.raw, self.out, {"title": "Tom & <Jerry> \"x\" 'y'"})
        self.assertEqual(png.size(self.out), (1200, 630))
        self.assertEqual(info, {"fit": "cover", "targetWidth": 1200, "targetHeight": 630, "template": "t.svg",
                                "text": {"title": "Tom & <Jerry> \"x\" 'y'", "subtitle": ""}})
        self.assertEqual(self.leftovers(), [])
        at = pixels(self.out, 1200, 630)
        near(self, at(125, 125), (0, 255, 0))  # the layer is over the image
        near(self, at(600, 500), GRAY)  # the image is under the layer

    def test_cover_crops_the_edge_columns_and_never_deforms(self):
        self.write("t.svg", self.TEMPLATE)
        compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}), self.raw, self.out, {})
        at = pixels(self.out, 1200, 630)
        # the raw 24 px red and blue columns are 23.6 px at 1260/1280; the crop takes 30 px from each side
        for y in (5, 300, 620):
            near(self, at(0, y), GRAY)
            near(self, at(1199, y), GRAY)

    def test_the_logo_travels_as_a_data_uri(self):
        self.write("t.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
                            '<image href="{{logo}}" x="200" y="200" width="250" height="100"/></svg>')
        self.write("l.svg", LOGO)
        info = compose.render(self.root, self.profile(compose={"template": "t.svg", "logo": "l.svg"}),
                              self.raw, self.out, {})
        self.assertEqual(info["logo"], "l.svg")
        at = pixels(self.out, 1200, 630)
        near(self, at(325, 250), (255, 0, 0))
        near(self, at(150, 250), GRAY)

    def test_a_lone_surrogate_in_the_text_is_dropped_and_does_not_break_the_write(self):
        self.write("t.svg", self.TEMPLATE)
        profile = self.profile(compose={"template": "t.svg", "fields": ["title"]})
        compose.render(self.root, profile, self.raw, self.out, {"title": "a\ud800b"})
        self.assertEqual(png.size(self.out), (1200, 630))

    def test_a_text_that_looks_like_a_hole_is_text(self):
        self.write("t.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">'
                            '<text x="10" y="50" font-size="20">{{title}}</text></svg>')
        info = compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}),
                              self.raw, self.out, {"title": "{{logo}} {{title}}"})
        self.assertEqual(info["text"], {"title": "{{logo}} {{title}}"})
        self.assertEqual(png.size(self.out), (1200, 630))

    def test_the_gimg_chunk_survives_with_compose(self):
        self.write("t.svg", self.TEMPLATE)
        meta = {"seed": 7, "prompt": "un gato 猫", "width": 1280, "height": 640}
        png.add_text_chunk(self.raw, "gimg", json.dumps(meta, ensure_ascii=False))
        info = compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}),
                              self.raw, self.out, {"title": "Hola"})
        chunk = json.loads(png.read_text_chunks(self.out)["gimg"])
        self.assertEqual(chunk["compose"], info)
        self.assertEqual({k: v for k, v in chunk.items() if k != "compose"}, meta)
        self.assertEqual(png.read_text_chunks(self.out).keys(), {"gimg"})  # ffmpeg's own metadata is dropped
        self.assertNotIn("compose", json.loads(png.read_text_chunks(self.raw)["gimg"]))  # the raw one is untouched

    def test_a_raw_image_without_a_chunk_gives_a_result_without_one(self):
        self.write("t.svg", self.TEMPLATE)
        compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}), self.raw, self.out, {})
        self.assertEqual(png.read_text_chunks(self.out), {})

    def test_a_bad_chunk_in_the_raw_image_only_prints_a_line(self):
        self.write("t.svg", self.TEMPLATE)
        png.add_text_chunk(self.raw, "gimg", "this is not json")
        err = io.StringIO()
        with redirect_stderr(err):
            compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}),
                           self.raw, self.out, {})
        self.assertEqual(png.size(self.out), (1200, 630))
        self.assertIn("gimg:", err.getvalue())
        self.assertIn("Expecting value", err.getvalue())  # the reason is the JSON parser's

    def test_scale_alone_without_a_template(self):
        info = compose.render(self.root, self.profile(targetWidth=640, targetHeight=320), self.raw, self.out, {"title": "x"})
        self.assertEqual(png.size(self.out), (640, 320))
        self.assertEqual(info, {"fit": "cover", "targetWidth": 640, "targetHeight": 320, "text": {}})
        at = pixels(self.out, 640, 320)
        near(self, at(320, 160), GRAY)
        near(self, at(2, 160), (255, 0, 0), tol=40)  # nothing was cropped: the edge column is still there

    def test_contain_leaves_transparent_bands_for_the_template_to_paint(self):
        self.write("t.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">'
                            '<rect x="0" y="0" width="1200" height="8" fill="#0000ff"/></svg>')
        compose.render(self.root, self.profile(compose={"template": "t.svg", "fit": "contain"}), self.raw, self.out, {})
        self.assertEqual(png.size(self.out), (1200, 630))
        at = pixels(self.out, 1200, 630, "rgba")
        near(self, at(600, 4), (0, 0, 255, 255))  # the template painted this band
        self.assertEqual(at(600, 12)[3], 0)  # the other band, 15 px tall, is left transparent
        near(self, at(600, 315)[:3], GRAY)
        self.assertEqual(at(600, 315)[3], 255)

    def test_a_broken_template_names_the_tool_and_leaves_nothing(self):
        self.write("t.svg", "<svg><not closed")
        with self.assertRaises(GimgError) as cm:
            compose.render(self.root, self.profile(compose={"template": "t.svg"}), self.raw, self.out, {})
        self.assertEqual(cm.exception.code, "compose.tool_failed")
        self.assertEqual(cm.exception.params["tool"], "rsvg-convert")
        self.assertTrue(cm.exception.params["reason"])
        self.assertFalse(self.out.exists())
        self.assertEqual(self.leftovers(), [])

    def test_a_broken_raw_image_names_ffmpeg(self):
        self.write("t.svg", self.TEMPLATE)
        good = self.raw.read_bytes()
        # the header is fine, the pixels are cut: png.size reads it, ffmpeg cannot
        self.raw.write_bytes(good[:33] + png.chunk(b"IDAT", b"garbage") + png.chunk(b"IEND", b""))
        with self.assertRaises(GimgError) as cm:
            compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}),
                           self.raw, self.out, {})
        self.assertEqual((cm.exception.code, cm.exception.params["tool"]), ("compose.tool_failed", "ffmpeg"))
        self.assertEqual(self.leftovers(), [])

    def test_the_template_cannot_read_files_outside_its_own_folder(self):
        secret = self.outside / "secret.png"
        striped_png(secret, 64, 64, edge=0, middle=(255, 0, 0))
        for href in (secret.as_uri(), str(secret), "../outside/secret.png"):
            self.write("t.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">'
                                '<image href="%s" x="200" y="200" width="300" height="300"/></svg>' % href)
            compose.render(self.root, self.profile(compose={"template": "t.svg"}), self.raw, self.out, {})
            at = pixels(self.out, 1200, 630)
            near(self, at(350, 350), GRAY)  # not red: the file was not read

    def test_the_work_folder_is_a_hidden_one_next_to_the_result(self):
        # same file system as the result so the final os.replace is atomic; nothing is written inside the project
        self.write("t.svg", self.TEMPLATE)
        real = tempfile.TemporaryDirectory
        with mock.patch.object(compose.tempfile, "TemporaryDirectory", wraps=real) as spy:
            compose.render(self.root, self.profile(compose={"template": "t.svg", "fields": ["title"]}),
                           self.raw, self.out, {})
        self.assertEqual(spy.call_args.kwargs, {"dir": str(self.work), "prefix": ".compose-"})
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["t.svg"])

    def test_a_second_render_replaces_the_first_atomically(self):
        self.write("t.svg", self.TEMPLATE)
        profile = self.profile(compose={"template": "t.svg", "fields": ["title"]})
        compose.render(self.root, profile, self.raw, self.out, {"title": "a"})
        first = self.out.read_bytes()
        compose.render(self.root, profile, self.raw, self.out, {"title": "b"})
        self.assertNotEqual(self.out.read_bytes(), first)
        self.assertEqual(self.leftovers(), [])


if __name__ == "__main__":
    unittest.main()
