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

    def test_no_else_after_a_loop_body_without_braces(self):
        # `else if (a) for (…) if (b) x; else …` ties the else to the inner if: in dom.js#h() that dropped every
        # attribute after `aria` (no href, no onclick) and nothing could be clicked.
        dangling = re.compile(r"\b(for|while)\s*\([^\n{]*\)\s*if\s*\([^\n{]*;[ \t]*\n\s*else\b")
        for path in JS:
            code = re.sub(r"/\*.*?\*/|//[^\n]*", "", read(path), flags=re.S)
            self.assertIsNone(dangling.search(code), rel(path))

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

    def test_the_measured_zone_is_the_one_of_the_template_of_each_attempt(self):
        slots = read(UI / "js" / "components" / "slots.js")
        self.assertIn("zoneParam(tpl ? tpl.zone : ctx.measure.zone)", slots)  # the profile's zone is only the fallback
        self.assertIn("const { tpl } = templateOf(ctx, attempt)", slots[slots.index("export function measureFor"):])
        for name in ("attempt-card.js", "compare-view.js"):
            self.assertNotIn("ctx.measure.zone", read(UI / "js" / "components" / name), name)

    def test_failed_compose_reloads_the_order_and_select_keeps_focus(self):
        text = self.js("components/order-view.js")
        self.assertIn("finally", text)
        self.assertNotIn("'button, a, input, summary'", text)

    def test_retry_resends_the_model_of_the_entry_when_it_is_not_the_profile_one(self):
        text = self.js("components/order-view.js")
        retry = text[text.index("retry: guard("):text.index("cancel: guard(")]
        self.assertRegex(retry, r"e\.params\.model !== profileCfg\.model\s*\?\s*\{ model: e\.params\.model \}")
        # recreate and vary go through the retouch panel, which loads the model of the attempt into its selector and sends it
        panel = self.js("components/retouch-panel.js")
        self.assertIn("modelSel.value = opt && p.model !== model ? p.model : ''", panel)
        self.assertIn("s.model = modelSel.value", panel)

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


class LayoutEditor(unittest.TestCase):
    """F4c.3: el editor de elementos, comprobado en estático (no hay navegador: el recorrido es de la persona)."""

    def comp(self, name):
        return read(UI / "js" / "components" / name)

    def test_the_applied_layout_falls_back_to_the_one_of_the_compose_error(self):
        self.assertIn("(attempt.composeError || attempt.compose || {}).layout", self.comp("layout-editor.js"))
        self.assertNotIn("attempt.compose && attempt.compose.layout", self.comp("layout-editor.js"))

    def test_the_slot_opens_the_editor_only_with_elements_and_a_composed_attempt(self):
        slots = self.comp("slots.js")
        self.assertIn("editorSlot(ctx, attempt)", self.comp("attempt-card.js"))
        self.assertIn("openLayoutEditor(ctx, attempt, tpl, button)", slots)
        self.assertRegex(slots, r"!\(tpl\.elements \|\| \[\]\)\.length|!tpl\.elements")
        self.assertIn("!attempt.compose || attempt.composeError", slots)
        self.assertNotIn("editSoon", "".join(read(f) for f in JS))

    def test_the_html_preview_is_gone(self):
        self.assertFalse((UI / "js" / "components" / "compose-preview.js").exists())
        self.assertNotIn("compose-preview", "".join(read(f) for f in JS + CSS))
        self.assertNotIn("previewText", "".join(read(f) for f in JS))

    def test_apply_reset_and_save_use_the_api_shapes(self):
        editor, order = self.comp("layout-editor.js"), self.comp("order-view.js")
        self.assertIn("setLayout(attempt, changedLayout(items))", editor)
        self.assertIn("setLayout(attempt, {})", editor)
        self.assertIn("{ layout }", order)
        self.assertIn("from: { key, attempt: a.id }, name, dest", order)
        self.assertIn("base: true", editor)
        self.assertIn("MEASURE_DELAY_MS = 400", editor)
        self.assertIn("base=1", read(UI / "js" / "api.js"))

    def test_template_name_pattern_is_the_one_of_the_server(self):
        from gimg import compose
        editor = self.comp("layout-editor.js")
        self.assertIn("NAME_PATTERN = /^[a-z0-9][a-z0-9-]{0,39}$/", editor)
        self.assertIn("[a-z0-9][a-z0-9-]{0,39}", compose._TEMPLATE_ID.pattern)
        self.assertIn("name !== 'default'", editor)
        self.assertIn("compose || {}).templatesDir", editor)

    def test_dialog_traps_focus_stops_global_keys_and_returns_focus(self):
        editor = self.comp("layout-editor.js")
        for needle in ("showModal()", "ev.key !== 'Tab'", "ev.stopPropagation()", "opener.focus()", "setPointerCapture", "ev.shiftKey", "ev.altKey"):
            self.assertIn(needle, editor)
        self.assertNotIn("setAttribute('style'", editor)

    def test_local_templates_get_an_export_link_with_download(self):
        slots = self.comp("slots.js")
        self.assertIn("tpl.source !== 'local'", slots)
        self.assertRegex(slots, r"download: `\$\{tpl\.id\}\.svg`")


class F4dUi(unittest.TestCase):
    """F4d.2: panel de pedido nuevo, piezas, marca, modelo y cola movible, comprobados en estático."""

    def comp(self, name):
        return read(UI / "js" / "components" / name)

    def test_the_new_order_body_follows_the_api_and_the_schema(self):
        panel = self.comp("new-order.js")
        pattern = json.loads(read(Path(server.__file__).parent / "schemas" / "order.schema.json"))["properties"]["key"]["pattern"]
        self.assertIn("KEY_PATTERN = /%s/" % pattern.replace("/", "\\/"), panel)
        for needle in ("api.newOrder(project, body)", "body.template = ", "body.model = ", "body.params = ", "novalidate", "showModal()",
                       "ev.stopPropagation()", "opener.focus()", "disabled: m.allowed === false", "m.reason.message"):
            self.assertIn(needle, panel)
        self.assertIn("newOrder: (p, body) => post(paths.newOrder(p), body)", read(UI / "js" / "api.js"))
        self.assertNotIn("newOrderSoon", "".join(read(f) for f in JS))

    def test_banned_words_only_warn(self):
        panel = self.comp("new-order.js")
        self.assertIn("bannedWord(allText(), banned)", panel)
        self.assertNotIn("banned", panel[panel.index("function buildBody"):panel.index("function showError")])
        self.assertIn("export function bannedWord", self.comp("attempt-util.js"))

    def test_attempts_can_carry_a_model_and_blocked_ones_are_disabled(self):
        retouch = self.comp("retouch-panel.js")
        self.assertIn("s.model = modelSel.value", retouch)
        self.assertIn("negative.value.trim() === (order.negative || '')", retouch)  # the «changed» mark sees the negative
        self.assertIn("negative.addEventListener('input', checkPrompt)", retouch)
        self.assertIn("disabled: m.allowed === false", retouch)
        self.assertIn("api.models()", self.comp("order-view.js"))

    def test_the_queue_moves_only_queued_entries_and_clearing_asks_first(self):
        bar = self.comp("queue-bar.js")
        self.assertIn("if (e.state === 'queued') {", bar)
        for to in ("up", "down", "top"):
            self.assertIn("mover('%s'" % to, bar)
        self.assertIn("api.move(e.id, to2)", bar)
        self.assertIn("if (!ok) return;\n  try {\n    const cancelled = await api.clearQueue(project)", bar)
        self.assertIn("confirmAction(", bar)
        self.assertIn("showModal()", self.comp("confirm.js"))
        api = read(UI / "js" / "api.js")
        self.assertIn("post(paths.move(id), { to })", api)
        self.assertIn("post(paths.clear(), project ? { project } : {})", api)

    def test_the_project_tabs_use_the_new_views(self):
        view = self.comp("project-view.js")
        for needle in ("piecesTab(panel, project, cfg)", "brandTab(panel, project, cfg)", "newOrderButton(project)"):
            self.assertIn(needle, view)
        self.assertIn("api.check(project)", self.comp("brand-tab.js"))
        self.assertIn("STATUS_CHIP", self.comp("brand-tab.js"))
        self.assertIn("paths.asset(project, name, 'template', x.id)", self.comp("pieces-tab.js"))


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

    def test_r9_fonts_are_declared_and_served(self):
        css = read(UI / "css" / "tokens.css")
        for family, name in (("Big Shoulders Display", "BigShouldersDisplay"), ("Literata", "Literata"),
                             ("JetBrains Mono", "JetBrainsMono")):
            self.assertIn('font-family: "%s"' % family, css)
            self.assertIn("/ui/fonts/%s.ttf" % name, css)
            resp, payload = self.call(path="/ui/fonts/%s.ttf" % name)
            self.assertEqual(resp.status, 200, name)
            self.assertEqual(resp.getheader("Content-Type").split(";")[0], "font/ttf", name)
            self.assertEqual(payload[:4], b"\x00\x01\x00\x00", name)
        for old in ("Sora", "Inter"):
            self.assertFalse((UI / "fonts" / (old + ".ttf")).exists(), old)

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
    light = re.search(r"^:root \{(.*?)\n\}", css, re.S | re.M).group(1)
    auto = re.search(r"@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme=\"light\"\]\) \{(.*?)\n  \}", css, re.S).group(1)
    dark = re.search(r":root\[data-theme=\"dark\"\] \{(.*?)\n\}", css, re.S).group(1)
    var = lambda block: dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\b", block))
    base = var(light)
    return {"light": base, "dark(auto)": {**base, **var(auto)}, "dark(selector)": {**base, **var(dark)}}


TEXT_PAIRS = [("text", "bg"), ("text", "surface"), ("text", "surface-2"), ("text-2", "bg"), ("text-2", "surface"),
              ("text-2", "surface-2"), ("accent-text", "bg"), ("accent-text", "surface"), ("accent-text", "surface-2"),
              ("on-accent", "accent-fill"), ("ok", "bg"), ("ok", "surface"), ("warn", "bg"), ("warn", "surface"),
              ("bad", "bg"), ("bad", "surface"), ("text", "accent-soft"), ("text-2", "accent-soft"),
              ("family", "bg"), ("family", "surface"), ("on-status", "ok"), ("on-status", "warn"), ("on-status", "bad"),
              ("text-3", "bg"), ("text-3", "surface"), ("text-3", "surface-2")]
NONTEXT_PAIRS = [("border", "bg"), ("border", "surface"), ("border", "surface-2"), ("focus", "bg"), ("focus", "surface"),
                 ("focus", "surface-2"), ("accent", "bg"), ("accent", "surface"), ("accent", "surface-2")]
# r10: the progress bar is outlined with --border and filled with --accent on --surface-2


class DashedChamfer(unittest.TestCase):
    def test_every_dashed_card_has_a_dashed_diagonal(self):
        """Revisión de r10: el chaflán recorta el borde y ::after dibuja la diagonal; con borde discontinuo, a trazos."""
        css = "\n".join(p.read_text(encoding="utf-8") for p in sorted((UI / "css").glob("*.css")))
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        rules = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
        dashed_after = set()
        for selectors, body in rules:
            if "repeating-linear-gradient" in body:
                dashed_after.update(s.strip() for s in selectors.split(",") if s.strip().endswith("::after"))
        checked = 0
        for selectors, body in rules:
            if not re.search(r"border-style:\s*dashed", body):
                continue
            for sel in (s.strip() for s in selectors.split(",")):
                if sel.startswith((".attempt", ".project-card", ".card")):
                    checked += 1
                    self.assertIn(sel + "::after", dashed_after, sel)
        self.assertGreaterEqual(checked, 3)


class EditorThinBoxes(unittest.TestCase):
    def test_handles_and_name_leave_the_text_visible(self):
        """Revisión de r10: en cajas finas el rótulo y las asas tapaban el texto que encuadran."""
        css = re.sub(r"/\*.*?\*/", "", read(UI / "css" / "components.css"), flags=re.S)
        self.assertRegex(css, r"\.ed-box \{[^}]*container-type:\s*size")
        self.assertRegex(css, r"\.ed-handle \{[^}]*opacity:\s*0[;\s]")
        self.assertRegex(css, r"\.ed-box:hover \.ed-handle, \.ed-box:focus-within \.ed-handle \{\s*opacity:\s*1")
        self.assertRegex(css, r"@container \(max-height: 40px\) \{\s*\.ed-name \{\s*top:\s*100%")


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
        for theme, tokens in theme_blocks().items():
            self.assertEqual(tokens["accent-fill"].lower(), "#7c5cd6", theme)
            self.assertEqual(tokens["accent"].lower(), "#7c5cd6", theme)
            self.assertEqual(tokens["on-accent"].lower(), "#ffffff", theme)
        self.assertGreaterEqual(ratio("#ffffff", "#7C5CD6"), 4.5)

    def test_on_image_over_the_veil_reaches_aa_on_a_white_image(self):
        """--on-image va sobre --overlay, que es translúcido: el peor caso es el velo sobre una imagen blanca."""
        css = (UI / "css" / "tokens.css").read_text(encoding="utf-8")
        veils = re.findall(r"--overlay:\s*rgb\((\d+) (\d+) (\d+) / (\.\d+|[01](?:\.\d+)?)\)", css)
        self.assertEqual(len(veils), 3, "un --overlay por bloque de tema")
        for theme, tokens in theme_blocks().items():
            self.assertEqual(tokens["on-image"].lower(), "#ffffff", theme)
        for r, g, b, alpha in veils:
            a = float(alpha)
            mixed = "#%02x%02x%02x" % tuple(round(int(v) * a + 255 * (1 - a)) for v in (r, g, b))
            self.assertGreaterEqual(ratio("#ffffff", mixed), 4.5, "--on-image sobre --overlay %s" % alpha)

    def test_accent_text_is_never_a_fill(self):
        """--on-accent sobre --accent-text no llega a 4,5:1 en oscuro: --accent-text es solo tinta, nunca relleno."""
        for path in sorted((UI / "css").glob("*.css")) + sorted((UI / "js").rglob("*.js")):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(background|background-color|fill)\s*:\s*var\(--accent-text\)", path.name)

    def test_r10_values_and_tokens_in_both_themes(self):
        blocks = theme_blocks()
        for theme, tokens in blocks.items():
            for name in ("family", "rule", "text-3", "grid", "accent-text"):
                self.assertIn(name, tokens, "%s: falta --%s" % (theme, name))
            self.assertNotIn("brand", tokens, theme)  # r10 has one violet, --accent
        light, dark = blocks["light"], blocks["dark(selector)"]
        self.assertEqual((light["bg"].lower(), light["family"].lower()), ("#fbfcfd", "#0072a8"))
        self.assertEqual((dark["bg"].lower(), dark["family"].lower()), ("#0d171e", "#5cc8f2"))
        self.assertEqual((light["accent-text"].lower(), dark["accent-text"].lower()), ("#7453cc", "#9577f3"))
        self.assertEqual(blocks["dark(auto)"], dark)  # the media query and the selector agree

    def test_border_and_rule_are_the_sheets(self):
        blocks = theme_blocks()
        for theme, tokens in blocks.items():
            self.assertEqual(tokens["border"].lower(), "#6f8493", theme)
            self.assertNotIn("border-strong", tokens, theme)
        self.assertEqual(blocks["light"]["rule"].lower(), "#b9cbd6")
        self.assertEqual(blocks["dark(selector)"]["rule"].lower(), "#2b3d49")
        self.assertEqual(blocks["dark(auto)"]["rule"].lower(), "#2b3d49")
        for theme, tokens in blocks.items():  # controls sit on these three fills
            for bg in ("bg", "surface", "surface-2"):
                self.assertGreaterEqual(ratio(tokens["border"], tokens[bg]), 3.0, "%s: --border on --%s" % (theme, bg))

    def test_controls_use_border_and_dividers_use_rule(self):
        css = "".join(read(UI / "css" / n) for n in ("base.css", "components.css", "layout.css"))
        self.assertNotIn("border-strong", css)
        for sel in (r"\.btn \{", r"input\[type=\"text\"\][^{]*\{", r"\.chip \{"):
            self.assertIn("var(--border)", re.search(sel + r"[^}]*\}", css, re.S).group(0), sel)
        for sel in (r"\.card \{", r"\.tabs \{"):  # the card draws its line (and its chamfer) with --edge
            self.assertIn("var(--rule)", re.search(sel + r"[^}]*\}", css, re.S).group(0), sel)

    def test_chip_status_text_reaches_aa_on_its_fill(self):
        css = read(UI / "css" / "base.css")
        fill = re.search(r"\.chip \{[^}]*?background: var\(--([\w-]+)\)", css, re.S).group(1)
        self.assertIn(fill, ("bg", "surface"))
        for theme, tokens in theme_blocks().items():
            for status in ("ok", "warn", "bad", "family"):
                self.assertGreaterEqual(ratio(tokens[status], tokens[fill]), 4.5, "%s: --%s on chip --%s" % (theme, status, fill))

    def test_light_is_the_default_theme(self):
        css = re.sub(r"/\*.*?\*/", "", read(UI / "css" / "tokens.css"), flags=re.S)
        self.assertIn("color-scheme: light;", re.search(r"^:root \{(.*?)\n\}", css, re.S | re.M).group(1))
        self.assertIn("prefers-color-scheme: dark", css)
        self.assertNotIn("gradient", css)

    def test_inherited_rules_of_the_sheet(self):
        """r10: no radii but the status dot and the spinner, no blur, no gradient but the 24 px grid."""
        names = ("tokens.css", "base.css", "components.css", "layout.css")
        css = re.sub(r"/\*.*?\*/", "", "".join(read(UI / "css" / n) for n in names), flags=re.S)
        for banned in ("backdrop-filter", "blur(", "drop-shadow", "--r:", "--r-s:", "var(--r)", "var(--r-s)"):
            self.assertNotIn(banned, css, banned)
        rounded = re.findall(r"([^{}]+)\{[^{}]*border-radius[^{}]*\}", css)
        self.assertTrue(rounded)
        for group in rounded:
            for sel in group.split(","):  # cada selector del grupo, no solo el último
                self.assertRegex(sel.strip(), r"(\.dot|\.spin)$", "border-radius fuera de las excepciones: " + sel.strip())
        grads = re.findall(r"([^{}]+)\{([^{}]*gradient[^{}]*)\}", css)
        # la única otra: la diagonal discontinua del chaflán, trazos de corte seco (DashedChamfer), no un degradado
        dashes = [(g, b) for g, b in grads if all(s.strip().endswith("::after") for s in g.split(","))]
        for _, body in dashes:
            self.assertRegex(body, r"repeating-linear-gradient\(135deg, var\(--edge\) 0 3px, transparent 3px 6px\)")
        self.assertEqual([g.strip() for g, b in grads if (g, b) not in dashes], ["body"])
        self.assertIn("var(--grid)", re.search(r"body \{[^}]*\}", css, re.S).group(0))
        for token in ("--chamfer-l: 28px", "--chamfer: 14px", "--chamfer-s: 10px", "--grid-step: 24px"):
            self.assertIn(token, css, token)
        self.assertIn("clip-path", re.search(r"\.card \{[^}]*\}", css, re.S).group(0))

    def test_outlines_on_chamfered_elements_stay_inside(self):
        """Retro R1 (2026-11-13): un contorno con desfase positivo sobre un elemento con chaflán lo recorta el
        `clip-path`. Elementos con chaflán: los que llevan `clip-path` en el CSS y las clases que el JS pone junto a
        `.card`. Toda regla con `outline` cuyo sujeto sea uno de ellos lleva `outline-offset` negativo."""
        css = re.sub(r"/\*.*?\*/", "", "".join(read(UI / "css" / n) for n in ("base.css", "layout.css", "components.css")), flags=re.S)
        rules = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
        tokens = lambda compound: set(re.findall(r"^[a-z]+|\.[a-zA-Z_-]+", re.sub(r":[a-z-]+(\([^)]*\))?", "", compound)))
        chamfered = set()
        for sel, body in rules:
            if re.search(r"clip-path\s*:\s*polygon", body):
                chamfered |= {t for s in sel.split(",") if "::" not in s for t in tokens(re.split(r"\s+|>|\+|~", s.strip())[-1])}
        js = "".join(read(f) for f in (UI / "js").rglob("*.js"))
        for combo in re.findall(r"'[a-z]*((?:\.[a-z-]+)*\.card(?:\.[a-z-]+)*)'", js):
            chamfered |= {"." + c for c in combo.split(".") if c and c != "card"}
        self.assertTrue({".card", "dialog", ".attempt"} <= chamfered, chamfered)
        seen = 0
        for sel, body in rules:
            if not re.search(r"(^|;)\s*outline(-offset)?\s*:", body):
                continue
            for one in sel.split(","):
                subject = re.split(r"\s+|>|\+|~", one.strip())[-1]
                if not tokens(subject) & chamfered:
                    continue
                seen += 1
                m = re.search(r"outline-offset\s*:\s*([^;]+)", body)
                self.assertTrue(m and m.group(1).strip().startswith(("-", "calc(-")), f"{one.strip()}: {body.strip()}")
        self.assertGreaterEqual(seen, 2)

    def test_review_fixes_of_buttons_focus_and_selects(self):
        """Revisión de r10: el hover primario no cambia el relleno (--accent-text bajo blanco es 3,4:1 en oscuro), las
        reglas de desactivado van detrás de las de hover, el peligro sigue rojo al pasar el puntero, el foco y la
        comparación van dentro del chaflán y los `select` conservan la grafía de los nombres."""
        css = re.sub(r"/\*.*?\*/", "", read(UI / "css" / "base.css") + read(UI / "css" / "components.css"), flags=re.S)
        rules = [(sel.strip(), body) for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css)]
        def where(selector):
            hits = [i for i, (sel, _) in enumerate(rules) if selector in [x.strip() for x in sel.split(",")]]
            self.assertTrue(hits, selector)
            return hits
        for i in where(".btn-primary:hover"):
            self.assertNotIn("background", rules[i][1])
        last_hover = max(where(".btn:hover") + where(".btn-primary:hover") + where(".btn-danger:hover"))
        for sel in (".btn:disabled", ".btn-primary:disabled", ".btn-danger:disabled"):
            self.assertGreater(min(where(sel)), last_hover, sel + " va antes de un hover")
        self.assertIn("var(--bad)", rules[where(".btn-danger:hover")[0]][1])
        self.assertRegex(rules[where(".card:focus-visible")[0]][1], r"outline-offset:\s*calc\(-1")
        self.assertRegex(rules[where(".attempt.is-compared")[0]][1], r"outline-offset:\s*-")
        for i in where("select"):
            self.assertNotIn("text-transform", rules[i][1])


if __name__ == "__main__":
    unittest.main()
