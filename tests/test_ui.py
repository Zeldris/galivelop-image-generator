"""F4a: checks on the web interface in gimg/ui without a browser (CSP rules, imports, texts, API routes, contrast)."""
import json
import re
import unittest
from pathlib import Path

from gimg import server
from tests.test_server import ServerBase

UI = Path(server.UI_DIR)
LOCALES = Path(server.LOCALES_DIR)
JS = sorted(UI.rglob("*.js"))
HTML = sorted(UI.rglob("*.html"))
CSS = sorted(UI.rglob("*.css"))


def read(path):
    return path.read_text(encoding="utf-8")


def rel(path):
    return str(path.relative_to(UI))


class Csp(unittest.TestCase):
    def test_there_are_files(self):
        self.assertGreater(len(JS), 15)
        self.assertTrue(HTML)

    def test_html_has_no_inline_script_style_or_handlers(self):
        for path in HTML:
            text = read(path)
            for tag in re.findall(r"<script\b[^>]*>", text, re.I):
                self.assertRegex(tag, r"\bsrc=", rel(path) + ": inline <script>")
            self.assertNotRegex(text, r"(?i)<script\b[^>]*>\s*\S[^<]*</script>", rel(path))
            self.assertNotRegex(text, r"(?i)<style\b", rel(path))
            self.assertNotRegex(text, r"(?i)<[^>]+\sstyle\s*=", rel(path) + ": style attribute")
            self.assertNotRegex(text, r"(?i)<[^>]+\son[a-z]+\s*=", rel(path) + ": on* attribute")

    def test_js_has_no_html_injection_or_eval(self):
        banned = re.compile(r"\.(innerHTML|outerHTML)\b|insertAdjacentHTML|\beval\s*\(|new\s+Function\b|document\.write\b"
                            r"|setAttribute\(\s*['\"](style|on\w+)['\"]")
        for path in JS:
            code = re.sub(r"/\*.*?\*/|//[^\n]*", "", read(path), flags=re.S)
            self.assertIsNone(banned.search(code), rel(path))

    def test_css_has_no_external_urls(self):
        for path in CSS:
            for url in re.findall(r"url\(\s*['\"]?([^'\")]+)", read(path)):
                self.assertTrue(url.startswith(("/ui/", "data:")), "%s: %s" % (rel(path), url))

    def test_balanced_brackets(self):
        # no JS engine here: a cheap check of (), [] and {} outside strings, comments and template text
        for path in JS:
            self.assertEqual(_unbalanced(read(path)), None, rel(path))


def _unbalanced(src):
    stack, i, n = [], 0, len(src)
    pairs = {")": "(", "]": "[", "}": "{"}
    tmpl = []  # brace depth at which each open template literal resumes
    while i < n:
        c = src[i]
        if c == "/" and src[i:i + 2] == "//":
            i = src.find("\n", i)
            i = n if i < 0 else i
        elif c == "/" and src[i:i + 2] == "/*":
            i = src.find("*/", i) + 2
        elif c in "'\"":
            j = i + 1
            while src[j] != c:
                j += 2 if src[j] == "\\" else 1
            i = j + 1
        elif c == "`":
            i = _template(src, i + 1, stack, tmpl)
        elif c in "([{":
            stack.append(c)
            i += 1
        elif c in ")]}":
            if not stack or stack.pop() != pairs[c]:
                return "unbalanced %r near offset %d" % (c, i)
            i += 1
        elif c == "/" and _regex_start(src, i):
            j = i + 1
            while src[j] != "/" or src[j - 1] == "\\" and src[j - 2] != "\\":
                j += 1
                if src[j] == "[":
                    j = src.find("]", j)
            i = j + 1
        else:
            i += 1
    return None if not stack else "unclosed %s" % "".join(stack)


def _template(src, i, stack, tmpl):
    """Skip a template literal starting after its backtick; recursive for ${...}. Returns the index after it."""
    n = len(src)
    while i < n:
        c = src[i]
        if c == "\\":
            i += 2
        elif c == "`":
            return i + 1
        elif src[i:i + 2] == "${":
            depth, i = 1, i + 2
            start = i
            while depth:
                d = src[i]
                if d == "`":
                    i = _template(src, i + 1, stack, tmpl)
                    continue
                if d in "'\"":
                    j = i + 1
                    while src[j] != d:
                        j += 2 if src[j] == "\\" else 1
                    i = j
                elif d == "{":
                    depth += 1
                elif d == "}":
                    depth -= 1
                i += 1
            err = _unbalanced(src[start:i - 1])
            if err:
                raise AssertionError("in template: " + err)
        else:
            i += 1
    raise AssertionError("unterminated template")


def _regex_start(src, i):
    j = i - 1
    while j >= 0 and src[j] in " \t":
        j -= 1
    return j < 0 or src[j] in "(,=:[!&|?{};+-*%<>~^" or src[max(0, j - 5):j + 1] in ("return",)


IMPORT = re.compile(r"import\s*(?:([\w$*{},\s]+?)\s*from\s*)?['\"]([^'\"]+)['\"]")
EXPORT = re.compile(r"export\s+(?:async\s+)?(?:function\*?|const|let|var|class)\s+([\w$]+)")
EXPORT_LIST = re.compile(r"export\s*\{([^}]*)\}")


def exports_of(path):
    text = read(path)
    names = set(EXPORT.findall(text))
    for group in EXPORT_LIST.findall(text):
        names.update(p.split(" as ")[-1].strip() for p in group.split(",") if p.strip())
    if re.search(r"export\s+default\b", text):
        names.add("default")
    return names


class ReviewFixes(unittest.TestCase):
    """Arreglos de la revisión de F4a (docs/records/revision-F4a-2026-11-05.md), comprobados en estático."""

    def js(self, name):
        return read(UI / "js" / name)

    def test_chosen_filter_sends_true_false_and_mock_rejects_1_0(self):
        text = self.js("components/project-view.js")
        self.assertNotRegex(text, r"chosen:[^\n]*\b[01]\b")
        self.assertIn("'true'", text)
        self.assertIn("'false'", text)
        mock = read(UI / "mock" / "api-mock.js")
        self.assertIn("api.bad_param", mock)

    def test_gallery_is_not_a_live_region_and_is_reconciled_by_key(self):
        text = self.js("components/order-view.js")
        self.assertNotRegex(text, r"live:\s*'polite'")
        self.assertIn("cardsByKey", text)

    def test_panel_signature_leaves_out_chosen_and_text(self):
        text = self.js("components/order-view.js")
        sig = re.search(r"const sig = JSON\.stringify\(\[([^\]]*)\]\)", text).group(1)
        self.assertNotIn("chosen", sig)
        self.assertNotIn("text", sig)
        self.assertIn("setChosen", self.js("components/text-panel.js"))

    def test_measure_requests_are_not_duplicated(self):
        self.assertIn("inflight", self.js("components/measure-chip.js"))

    def test_skip_link_is_handled_by_a_listener(self):
        self.assertIn("a.skip", self.js("app.js"))
        self.assertIn("preventDefault", self.js("app.js"))
        self.assertRegex(read(UI / "index.html"), r'<main id="main"[^>]*tabindex="-1"')

    def test_queue_bar_repaints_only_on_change_and_keeps_focus(self):
        text = self.js("components/queue-bar.js")
        self.assertIn("lastSig", text)
        self.assertIn("data-fid", text)

    def test_one_key_shortcuts_can_be_turned_off(self):
        self.assertIn("oneKeyEnabled", self.js("components/shortcuts.js"))
        self.assertIn("oneKeyEnabled", self.js("components/order-view.js"))
        for lang in ("es", "en"):
            d = json.loads(read(LOCALES / (lang + ".json")))
            self.assertIn("ui.shortcuts.oneKey", d)

    def test_order_view_checks_host_after_loading(self):
        self.assertIn("host.isConnected", self.js("components/order-view.js"))

    def test_template_selector_is_labelled_and_used_by_card_panel_and_measure(self):
        slots = read(UI / "js" / "components" / "slots.js")
        self.assertRegex(slots, r"h\('label', \{ for: `template-")
        self.assertIn("composeError.templateId", slots)
        self.assertIn("list.length < 2", slots)
        self.assertIn("templateSlot(ctx, attempt)", read(UI / "js" / "components" / "attempt-card.js"))
        for name in ("attempt-card.js", "compare-view.js"):
            self.assertIn("measureFor(ctx,", read(UI / "js" / "components" / name))
        self.assertIn("s.template = template.value", read(UI / "js" / "components" / "retouch-panel.js"))
        self.assertIn("api.templates(project, profile)", read(UI / "js" / "components" / "order-view.js"))
        self.assertNotIn("templateSoon", "".join(read(f) for f in JS))

    def test_image_version_does_not_depend_on_compose_at(self):
        comp = UI / "js" / "components"
        for name in ("attempt-card.js", "compare-view.js", "measure-chip.js"):
            text = read(comp / name)
            self.assertIn("imageVersion(", text, name)
        self.assertNotIn("compose.at", read(comp / "measure-chip.js"))
        self.assertNotRegex(read(UI / "mock" / "api-mock.js"), r"compose[^\n]*\bat:")

    def test_attempt_prompt_loses_the_profile_style_before_resending(self):
        comp = UI / "js" / "components"
        self.assertIn("export function stripStyle", read(comp / "attempt-util.js"))
        for name in ("retouch-panel.js", "order-view.js"):
            self.assertIn("stripStyle(", read(comp / name), name)

    def test_text_panel_paints_the_fields_of_every_template(self):
        self.assertIn("ctx.templates", read(UI / "js" / "components" / "text-panel.js"))

    def test_measure_does_not_send_a_zone_without_colour(self):
        self.assertIn("textColor ? zoneParam", read(UI / "js" / "components" / "slots.js"))
        self.assertIn("ctx.zone && ctx.textColor", read(UI / "js" / "components" / "measure-chip.js"))

    def test_failed_compose_reloads_the_order_and_select_keeps_focus(self):
        text = self.js("components/order-view.js")
        self.assertIn("finally", text)
        self.assertNotIn("'button, a, input, summary'", text)

    def test_estimate_is_per_entry(self):
        text = self.js("components/order-view.js")
        self.assertNotIn("estimateMs / Math.max", text)
        self.assertIn("res.estimateMs * n", text)


class Imports(unittest.TestCase):
    def resolve(self, path, spec):
        if spec.startswith("/ui/"):
            return UI / spec[4:]
        self.assertTrue(spec.startswith("."), "%s: bare import %s" % (rel(path), spec))
        return (path.parent / spec).resolve()

    def test_relative_imports_resolve_and_export_what_is_imported(self):
        checked = 0
        for path in JS:
            for names, spec in IMPORT.findall(read(path)):
                target = self.resolve(path, spec)
                self.assertTrue(target.is_file(), "%s imports %s" % (rel(path), spec))
                if not names or names.strip().startswith("*"):
                    continue
                inner = re.search(r"\{([^}]*)\}", names)
                wanted = [p.split(" as ")[0].strip() for p in inner.group(1).split(",") if p.strip()] if inner else []
                if re.match(r"\s*[\w$]+\s*(,|$)", names):
                    wanted.append("default")
                for name in wanted:
                    self.assertIn(name, exports_of(target), "%s imports %s from %s" % (rel(path), name, spec))
                    checked += 1
        self.assertGreater(checked, 40)

    def test_dynamic_imports_resolve(self):
        for path in JS:
            for spec in re.findall(r"import\(\s*['\"]([^'\"]+)['\"]\s*\)", read(path)):
                self.assertTrue(self.resolve(path, spec).is_file(), "%s: %s" % (rel(path), spec))

    def test_html_assets_exist(self):
        for path in HTML:
            for spec in re.findall(r"""(?:src|href)=["'](/ui/[^"']+)""", read(path)):
                self.assertTrue((UI / spec[4:]).is_file(), spec)


KEY = re.compile(r"""['"`](ui\.[\w.]*[\w$]|ui\.[\w.]*\$\{)""")


class Texts(unittest.TestCase):
    def setUp(self):
        self.locales = {lang: json.loads(read(LOCALES / (lang + ".json"))) for lang in ("es", "en")}
        self.es = {k for k in self.locales["es"] if k.startswith("ui.")}
        self.used, self.prefixes = set(), set()
        for path in JS + HTML:
            text = read(path)
            for m in re.finditer(r"""(?:['"`]|=")(ui\.[\w.]*)(\$\{)?""", text):
                key = m.group(1)
                if m.group(2) or key.endswith("."):  # ui.state.${x} or 'ui.state.' + x: a family of keys
                    self.prefixes.add(key if key.endswith(".") else key.rsplit(".", 1)[0] + ".")
                elif "." in key:
                    self.used.add(key)

    def test_every_key_used_exists_in_both_languages(self):
        self.assertGreater(len(self.used), 100)
        for prefix in self.prefixes:
            self.assertTrue(any(k.startswith(prefix) for k in self.es), prefix)
        for lang, dictionary in self.locales.items():
            missing = sorted(k for k in self.used if k not in dictionary)
            self.assertEqual(missing, [], lang)

    def test_same_ui_keys_in_both_languages(self):
        self.assertEqual(self.es, {k for k in self.locales["en"] if k.startswith("ui.")})

    def test_no_unused_ui_keys(self):
        unused = sorted(k for k in self.es if k not in self.used and not any(k.startswith(p) for p in self.prefixes))
        self.assertEqual(unused, [])

    def test_placeholders_match(self):
        for key in self.es:
            self.assertEqual(set(re.findall(r"\{(\w+)\}", self.locales["es"][key])),
                             set(re.findall(r"\{(\w+)\}", self.locales["en"][key])), key)


class ApiRoutes(unittest.TestCase):
    def setUp(self):
        self.text = read(UI / "js" / "api.js")

    def patterns(self):
        """name -> route pattern of every entry of `paths` in api.js (query strings dropped)."""
        body = self.text[self.text.index("export const paths"):self.text.index("/* ---- llamadas con nombre")]
        entries = {}
        for m in re.finditer(r"^  (\w+): (.*?)(?=^  \w+: |^\};)", body, re.S | re.M):
            entries[m.group(1)] = m.group(2)
        out = {}

        def build(name):
            if name in out:
                return out[name]
            strings = [x for pair in re.findall(r"`([^`]*)`|'([^']*)'", entries[name]) for x in pair if x]
            template = next(x for x in strings if x.startswith(("/api", "${paths.")))
            template = re.sub(r"\$\{paths\.(\w+)\([^)]*\)\}", lambda mm: build(mm.group(1)), template)
            template = re.sub(r"\$\{[^}]*\}", "{}", template)
            template = re.sub(r"(?<=[^/])\{\}.*$", "", template).split("?")[0]
            out[name] = template
            return template

        for name in entries:
            build(name)
        return out

    def methods(self):
        found = re.findall(r"^  \w+: .*?=> (get|post|put)\(paths\.(\w+)", self.text, re.M)
        return {name: method.upper() for method, name in found}

    def test_every_path_matches_a_registered_route_with_its_method(self):
        routes = {(r.method, tuple("{}" if p.startswith("{") else p for p in r.parts)) for r in server.ROUTES}
        patterns = self.patterns()
        self.assertGreater(len(patterns), 15)
        methods = self.methods()
        used = set(methods) | {n for f in JS if f.name != "api.js" for n in re.findall(r"\bpaths\.(\w+)\(", read(f))}
        self.assertIn("image", used)
        for name, pattern in patterns.items():
            if name not in used:  # helper that only builds other paths (`attempt`)
                continue
            parts = tuple("{}" if p == "{}" else p for p in pattern.strip("/").split("/"))
            method = methods.get(name, "GET")  # paths used as <img src>, text or SVG are GET
            self.assertIn((method, parts), routes, "paths.%s -> %s %s" % (name, method, pattern))

    def test_every_named_call_uses_an_existing_path(self):
        patterns = self.patterns()
        for _method, name in re.findall(r"=> (get|post|put)\(paths\.(\w+)", self.text):
            self.assertIn(name, patterns)
        for path in JS:
            for name in re.findall(r"\bpaths\.(\w+)\(", read(path)):
                self.assertIn(name, patterns, rel(path))


class Served(ServerBase):
    TYPES = {".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml",
             ".png": "image/png", ".ttf": "font/ttf", ".woff2": "font/woff2", ".json": "application/json"}

    def test_root_and_every_file(self):
        resp, payload = self.call(path="/")
        self.assertEqual(resp.status, 200)
        self.assertEqual(payload, (UI / "index.html").read_bytes())
        served = [p for p in UI.rglob("*") if p.is_file() and p.suffix in self.TYPES]
        self.assertGreater(len(served), 30)
        for path in served:
            resp, payload = self.call(path="/ui/" + path.relative_to(UI).as_posix())
            name = rel(path)
            self.assertEqual(resp.status, 200, name)
            self.assertEqual(resp.getheader("Content-Type").split(";")[0], self.TYPES[path.suffix], name)
            self.assertIn("script-src 'self'", resp.getheader("Content-Security-Policy"), name)
            self.assertEqual(payload, path.read_bytes(), name)

    def test_every_file_has_a_served_type(self):
        for path in UI.rglob("*"):
            if path.is_file() and path.name != "OFL.txt":  # the licence travels with the fonts and is not served
                self.assertIn(path.suffix, server.STATIC_TYPES, rel(path))

    def test_locale_has_the_interface_texts(self):
        resp, payload = self.call(path="/api/locales/es")
        self.assertIn("ui.loading", json.loads(payload))


def _lum(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def theme_blocks():
    css = read(UI / "css" / "tokens.css")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    dark = re.search(r"^:root \{(.*?)\n\}", css, re.S | re.M).group(1)
    auto = re.search(r"@media \(prefers-color-scheme: light\) \{\s*:root:not\(\[data-theme=\"dark\"\]\) \{(.*?)\n  \}", css, re.S).group(1)
    light = re.search(r":root\[data-theme=\"light\"\] \{(.*?)\n\}", css, re.S).group(1)
    var = lambda block: dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\b", block))
    base = var(dark)
    return {"dark": base, "light(auto)": {**base, **var(auto)}, "light(selector)": {**base, **var(light)}}


TEXT_PAIRS = [("text", "bg"), ("text", "surface"), ("text", "surface-2"), ("text-2", "bg"), ("text-2", "surface"),
              ("text-2", "surface-2"), ("accent-text", "bg"), ("accent-text", "surface"), ("accent-text", "surface-2"),
              ("on-accent", "accent-fill"), ("ok", "bg"), ("ok", "surface"), ("warn", "bg"), ("warn", "surface"),
              ("bad", "bg"), ("bad", "surface"), ("text", "accent-soft"), ("text-2", "accent-soft"),
              ("on-status", "ok"), ("on-status", "warn"), ("on-status", "bad")]
NONTEXT_PAIRS = [("border-strong", "bg"), ("border-strong", "surface"), ("focus", "bg"), ("focus", "surface"),
                 ("focus", "surface-2")]


class Contrast(unittest.TestCase):
    def test_text_pairs_reach_aa(self):
        for theme, tokens in theme_blocks().items():
            for fg, bg in TEXT_PAIRS:
                self.assertGreaterEqual(ratio(tokens[fg], tokens[bg]), 4.5, "%s: --%s on --%s" % (theme, fg, bg))

    def test_borders_and_focus_reach_three(self):
        for theme, tokens in theme_blocks().items():
            for fg, bg in NONTEXT_PAIRS:
                self.assertGreaterEqual(ratio(tokens[fg], tokens[bg]), 3.0, "%s: --%s on --%s" % (theme, fg, bg))

    def test_primary_button_fill_is_the_declared_one(self):
        self.assertEqual(theme_blocks()["dark"]["accent-fill"].lower(), "#5b34c9")
        self.assertGreaterEqual(ratio("#ffffff", "#5B34C9"), 7.5)


if __name__ == "__main__":
    unittest.main()
