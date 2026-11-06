"""F4a: the web interface run for real in a headless Chrome over the DevTools protocol (tests/browser.py), against a
real `gimg serve` (in a thread) on the fake engine, temporary folders and an example project. Nothing is generated: the
fake engine writes placeholder images. Every scenario ends by asserting the page reported no exception, no console
error, no CSP violation and no failed load. Skipped when no Chrome is found (see ``GIMG_TEST_CHROME``)."""
import contextlib
import fcntl
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import quote

from gimg import cli, server
from tests import browser

ROOT = Path(__file__).resolve().parent.parent
TOOLS = shutil.which("ffmpeg") is not None and shutil.which("rsvg-convert") is not None
ELEMENTS_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630' viewBox='0 0 1200 630'>"
    "<rect width='1200' height='630' fill='#102030' fill-opacity='0.2'/>"
    "<text id='gimg-title1' data-gimg-box='40 40 500 60' data-gimg-color='#FFFFFF' x='40' y='90' font-size='40' fill='#ffffff'>{{title1}}</text>"
    "<text id='gimg-subtitle' data-gimg-box='40 140 500 40' data-gimg-color='#FFFFFF' x='40' y='170' font-size='20' fill='#ffffff'>{{subtitle}}</text>"
    "<g id='gimg-logo' data-gimg-box='40 500 200 60'><image href='{{logo}}' x='40' y='500' width='200' height='60'/></g>"
    "</svg>")
CLARO_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630' viewBox='0 0 1200 630'>"
             "<text x='40' y='90' font-size='40' fill='#000000'>{{title1}}</text></svg>")
PROJECT = "tarkor"
PROFILE = "og"
KEY = "fondos/r1"


def run_cli(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = cli.main(list(argv))
    if code != 0:
        raise AssertionError("gimg %s exited %s" % (" ".join(argv), code))
    return out.getvalue()


@unittest.skipUnless(browser.find_browser(), "no Firefox/Chrome found (set GIMG_TEST_BROWSER)")
class BrowserLifetime(unittest.TestCase):
    def test_close_shuts_the_browser_down_even_outside_our_process_group(self):
        # A flatpak or host Chrome is not in our process group: killpg alone left it running. After close(), its
        # DevTools port must refuse new connections.
        b = browser.Browser()
        url = b.ws_url
        b.close()
        with self.assertRaises(OSError) as caught:
            browser.WebSocket(url, timeout=3).close()
        self.assertIsInstance(caught.exception, (ConnectionRefusedError, ConnectionResetError, TimeoutError),
                              "the DevTools port still answers after close(): %r" % caught.exception)


@unittest.skipUnless(browser.find_browser(), "no Firefox/Chrome found (set GIMG_TEST_BROWSER)")
class UiBase(unittest.TestCase):
    """One server and one browser for the whole class; each test opens a fresh tab."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(browser.scratch_dir("gimg-ui-")).resolve()  # never in /tmp (a small tmpfs)
        cls.env = mock.patch.dict(os.environ, {
            "GIMG_CONFIG_HOME": str(cls.tmp / "cfg"), "GIMG_DATA_HOME": str(cls.tmp / "data"),
            "GIMG_LANG": "es", "GIMG_ENGINE": "fake", "GIMG_AUTOSTART": "0"})
        cls.env.start()
        try:
            cls.root = cls.tmp / "proj"
            shutil.copytree(ROOT / "examples" / PROJECT, cls.root)
            cls.customize_project()
            run_cli("project", "add", str(cls.root))
            cls.prepare()
            cls.srv = server.make_server(0)
            cls.port = cls.srv.port
            server.start_thread(cls.srv)
            cls.browser = browser.Browser()
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def customize_project(cls):
        """The copied example gets a template with editable elements (``gimg-*``), a second plain template and a
        ``templatesDir`` so a template can be saved into the project."""
        (cls.root / "plantillas" / "og.svg").write_text(ELEMENTS_SVG)
        (cls.root / "plantillas" / "claro.svg").write_text(CLARO_SVG)
        path = cls.root / "galivelop-images.json"
        cfg = json.loads(path.read_text())
        compose = cfg["profiles"][PROFILE]["compose"]
        compose["templates"] = {"claro": {"template": "plantillas/claro.svg", "fields": ["title1"]}}
        compose["templatesDir"] = "plantillas-extra"
        path.write_text(json.dumps(cfg))

    @classmethod
    def prepare(cls):
        """Hook: submit orders / run the worker before the server starts."""

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "browser", None):
            cls.browser.close()
        if getattr(cls, "srv", None):
            cls.srv.shutdown()
            cls.srv.server_close()
        cls.env.stop()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def submit(cls, key=KEY, profile=PROFILE, count=2, work=True, **extra):
        order = {"key": key, "profile": profile, "prompt": "A test scene. The image is completely textless.",
                 "seed": 3, "count": count}
        order.update(extra)
        f = cls.tmp / ("order-%s.json" % key.replace("/", "-"))
        f.write_text(json.dumps(order))
        run_cli("order", "submit", PROJECT, str(f))
        if work:
            run_cli("work")

    def setUp(self):
        self.page = self.browser.new_page()
        self.browser.take_problems()
        self.addCleanup(self.close_page)

    def close_page(self):
        self.page.ws.close()

    # helpers ---------------------------------------------------------------------------------------------------
    def open(self, route="/", wait="document.querySelector('#main h1')"):
        self.page.goto("http://127.0.0.1:%d/ui/index.html#%s" % (self.port, route))
        self.page.wait(wait)

    def js(self, expression):
        return self.page.evaluate(expression)

    def click(self, selector):
        self.page.wait("document.querySelector(%s)" % json.dumps(selector))
        self.js("document.querySelector(%s).click()" % json.dumps(selector))

    def no_problems(self):
        self.page.pump(0.3)
        self.assertEqual(self.browser.take_problems(), [])

    # UI.4: every visible control is a 44 px target (a checkbox counts through the label that wraps it). Inline links
    # inside running text are exempt (WCAG 2.5.8): none remain. The only exception is `.ed-box`, the boxes of the
    # layout editor drawn over the image at the size of the template's own geometry (essential, WCAG 2.5.8); they
    # have a keyboard alternative (arrows) and numeric fields, which are 44 px.
    SMALL_TARGETS = """(() => { const out = [];
        for (const n of document.querySelectorAll('a, button, input, select, [tabindex="0"]')) {
            if (!n.getClientRects().length || n.disabled || n.type === 'hidden' || n.matches('.ed-box')) continue;
            let box = n;
            if (n.matches('input[type=checkbox], input[type=radio]')) box = n.closest('label') || n;
            const r = box.getBoundingClientRect();
            if (r.width < 43.5 || r.height < 43.5) out.push((n.id ? '#' + n.id : n.tagName.toLowerCase() + '.' + n.className) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height) + ' "' + (n.textContent || n.getAttribute('aria-label') || '').trim().slice(0, 20) + '"');
        }
        return out; })()"""

    def assert_tap_targets(self, where):
        small = self.js(self.SMALL_TARGETS)
        self.assertEqual(small, [], "targets under 44x44 %s" % where)

    def api(self, method, path, body=None):
        return self.js("fetch(%s, {method: %s, headers: {'Content-Type': 'application/json'}, body: %s}).then(r => r.json())"
                       % (json.dumps(path), json.dumps(method), json.dumps(json.dumps(body)) if body is not None else "undefined"))


class Browse(UiBase):
    """Projects, a project's tabs and filters, language and theme."""

    @classmethod
    def prepare(cls):
        cls.submit("fondos/uno", count=1, work=False)
        cls.submit("redes/dos", profile="social", count=1, work=False)
        run_cli("work")

    def test_project_cards_are_links_and_their_meta_is_spaced(self):
        self.open("/", "document.querySelector('a.project-card')")
        self.assertEqual(self.js("document.querySelector('a.project-card').getAttribute('href')"), "#/p/tarkor/pedidos")
        gap = self.js("""(() => { const s = document.querySelectorAll('.project-card .meta span');
            const a = s[0].getBoundingClientRect(), b = s[1].getBoundingClientRect();
            return b.top >= a.bottom - 1 ? 99 : b.left - a.right; })()""")  # wrapped onto another line counts as apart
        self.assertGreaterEqual(gap, 4, "the spans of .meta touch each other")
        self.click("a.project-card")
        self.page.wait("location.hash === '#/p/tarkor/pedidos' && document.querySelector('.order-row')")
        self.no_problems()

    def test_tabs_navigate_and_paint(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('.order-row')")
        self.click("nav.tabs a[href='#/p/tarkor/piezas']")
        self.page.wait("document.querySelectorAll('.piece-card').length === 6")
        self.assertEqual(self.js("document.querySelector('nav.tabs a[aria-current=page]').textContent"), "Piezas")
        self.click("nav.tabs a[href='#/p/tarkor/marca']")
        self.page.wait("document.querySelector('.check-list .check-item')")
        self.assertGreaterEqual(self.js("document.querySelectorAll('.swatch').length"), 3)
        self.assertIn("bien", self.js("document.querySelector('#tab-panel section b').textContent"))
        self.click("nav.tabs a[href='#/p/tarkor/pedidos']")
        self.page.wait("document.querySelector('.order-row')")
        self.no_problems()

    def test_filters(self):
        self.open("/p/tarkor/pedidos", "document.querySelectorAll('.order-row').length === 2")
        self.js("(() => { const s = document.getElementById('f-profile'); s.value = 'social'; s.dispatchEvent(new Event('change')); })()")
        self.page.wait("document.querySelectorAll('.order-row').length === 1 && document.querySelector('.order-row .key').textContent === 'redes/dos'")
        self.js("(() => { const s = document.getElementById('f-state'); s.value = 'chosen'; s.dispatchEvent(new Event('change')); })()")
        self.page.wait("document.querySelector('.order-list .empty')")
        self.js("(() => { for (const id of ['f-profile', 'f-state']) { const s = document.getElementById(id); s.value = ''; s.dispatchEvent(new Event('change')); } })()")
        self.page.wait("document.querySelectorAll('.order-row').length === 2")
        self.no_problems()

    def test_order_rows_are_links_with_a_thumbnail(self):
        self.open("/p/tarkor/pedidos", "document.querySelectorAll('.order-row').length === 2")
        self.assertTrue(self.js("[...document.querySelectorAll('.order-row')].every(a => a.getAttribute('href').startsWith('#/p/tarkor/o/'))"))
        self.page.wait("[...document.querySelectorAll('.order-row img.thumb')].every(i => i.complete && i.naturalWidth > 0)")
        self.click(".order-row[aria-label='fondos/uno @ og']")
        self.page.wait("document.querySelector('.gallery .attempt')")
        self.assertEqual(self.js("document.querySelector('h1').textContent"), "fondos/uno")
        self.no_problems()

    def test_new_order_buttons_open_the_panel_with_the_profile(self):
        self.open("/p/tarkor/piezas", "document.querySelector('.piece-card')")
        self.click(".piece-card[data-profile=square] button[data-slot=new-order]")
        self.page.wait("document.querySelector('dialog.new-order[open]')")
        self.assertEqual(self.js("document.getElementById('no-profile').value"), "square")
        self.js("document.querySelector('dialog.new-order button[type=button]:not(.btn-icon)').click()")
        self.page.wait("!document.querySelector('dialog.new-order')")
        self.no_problems()

    def test_language_and_theme(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('.order-row')")
        self.js("(() => { const s = document.getElementById('lang'); s.value = 'en'; s.dispatchEvent(new Event('change')); })()")
        self.page.wait("document.querySelector('nav.tabs a').textContent === 'Orders'")
        self.js("(() => { const s = document.getElementById('theme'); s.value = 'dark'; s.dispatchEvent(new Event('change')); })()")
        self.assertEqual(self.js("document.documentElement.dataset.theme"), "dark")
        self.js("(() => { const s = document.getElementById('theme'); s.value = 'light'; s.dispatchEvent(new Event('change')); })()")
        self.assertEqual(self.js("document.documentElement.dataset.theme"), "light")
        self.js("(() => { const s = document.getElementById('lang'); s.value = 'es'; s.dispatchEvent(new Event('change')); })()")
        self.page.wait("document.querySelector('nav.tabs a').textContent === 'Pedidos'")
        self.js("localStorage.removeItem('gvig.theme')")
        self.no_problems()

    def test_help_and_unknown_route(self):
        self.open("/", "document.querySelector('a.project-card')")
        self.click("#help")
        self.page.wait("document.querySelector('#shortcuts[open] dt')")
        self.page.key("Escape")
        self.page.wait("!document.querySelector('#shortcuts[open]')")
        self.open("/nada/por/aqui", "document.querySelector('.empty a.btn')")
        self.no_problems()


    def header_metrics(self):
        return self.js("""(() => { const r = (s) => document.querySelector(s).getBoundingClientRect();
            const header = r('.app-header'), crumbs = document.getElementById('crumbs');
            // same line = same centre; a sub-pixel gap (Chrome centres a 44 px link and a text separator half a pixel apart) is not a new line
            const centres = [...crumbs.children].map((c) => { const b = c.getBoundingClientRect(); return b.top + b.height / 2; }).sort((a, b) => a - b);
            const lines = centres.filter((c, i) => i === 0 || c - centres[i - 1] > 2).length;
            return {headerH: header.height, token: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')),
                    crumbLines: lines, crumbsInside: r('#crumbs').bottom <= header.bottom + 0.5,
                    settings: [r('#settings-btn').width, r('#settings-btn').height], help: [r('#help').width, r('#help').height],
                    hscroll: document.documentElement.scrollWidth - document.documentElement.clientWidth}; })()""")

    def test_header_has_one_height_and_settings_menu(self):
        """UI.1: the header keeps one height per breakpoint on every screen, the crumbs stay on one line, nothing
        scrolls sideways, and language and theme live in a «Ajustes» menu with 44 px targets."""
        for width, limit in ((360, 96), (1440, 60)):
            self.page.ws.close()
            self.page = self.browser.new_page(width=width, height=780)
            heights = set()
            for route, ready in (("/", "document.querySelector('a.project-card')"),
                                 (order_route("fondos/uno"), "document.querySelector('.gallery .attempt')")):
                self.open(route, ready)
                m = self.header_metrics()
                where = "%s at %d" % (route, width)
                self.assertLessEqual(m["headerH"], limit, where)
                self.assertAlmostEqual(m["token"], m["headerH"], delta=1, msg=where)
                self.assertEqual(m["crumbLines"], 1, where)
                self.assertTrue(m["crumbsInside"], where)
                self.assertEqual(m["hscroll"], 0, where)
                for size in (m["settings"], m["help"]):
                    self.assertGreaterEqual(min(size), 44, where)
                heights.add(round(m["headerH"]))
            self.assertEqual(len(heights), 1, "the header changes height between screens at %d: %s" % (width, heights))
        self.click("#settings-btn")
        self.page.wait("document.getElementById('settings').matches(':popover-open')")
        sizes = self.js("['lang', 'theme', 'font-scale'].map((id) => { const r = document.getElementById(id).getBoundingClientRect(); return [r.width, r.height]; })")
        for w, h in sizes:
            self.assertGreaterEqual(h, 44)
            self.assertGreaterEqual(w, 120)
        self.assertEqual(self.js("document.getElementById('settings-btn').getAttribute('aria-label')"), "Ajustes")
        self.page.key("Escape")
        self.page.wait("!document.getElementById('settings').matches(':popover-open')")
        self.no_problems()

    def test_gamepad_moves_focus_activates_and_closes(self):
        """UI.9: with a (stubbed) standard gamepad connected, the d-pad moves the focus inside the open menu, A activates
        the focused button and B closes the «Ajustes» menu, the help dialog and a dialog that stops the propagation of its
        keys (the new-order panel), which the global Esc handler never sees. The real device is checked on the Deck."""
        self.open("/p/tarkor/piezas", "document.querySelector('.piece-card')")
        self.js("""(() => { const pad = {index: 0, connected: true, mapping: 'standard', buttons: Array.from({length: 17}, () => ({pressed: false, value: 0}))};
            window.__pad = pad; navigator.getGamepads = () => [pad];
            const ev = new Event('gamepadconnected'); Object.defineProperty(ev, 'gamepad', {value: pad}); window.dispatchEvent(ev); })()""")

        def press(button):
            self.js("window.__pad.buttons[%d].pressed = true" % button)
            self.page.pump(0.15)
            self.js("window.__pad.buttons[%d].pressed = false" % button)
            self.page.pump(0.15)

        popover_open = "document.getElementById('settings').matches(':popover-open')"
        self.js("document.getElementById('settings-btn').focus()")
        press(0)                                                    # A activates the focused button
        self.page.wait(popover_open)
        press(13)                                                   # d-pad down: first control of the open menu
        self.assertEqual(self.js("document.activeElement.id"), "lang")
        press(13)
        self.assertEqual(self.js("document.activeElement.id"), "theme")
        press(1)                                                    # B closes the menu
        self.page.wait("!" + popover_open)
        self.js("document.getElementById('help').focus()")
        press(0)
        self.page.wait("document.getElementById('shortcuts').open")
        press(1)
        self.page.wait("!document.getElementById('shortcuts').open")
        press(3)                                                    # Y opens the help
        self.page.wait("document.getElementById('shortcuts').open")
        press(1)
        self.page.wait("!document.getElementById('shortcuts').open")
        self.click(".piece-card[data-profile=square] button[data-slot=new-order]")
        self.page.wait("document.querySelector('dialog.new-order[open]')")
        press(1)                                                    # B cancels it like the real Esc
        self.page.wait("!document.querySelector('dialog.new-order[open]')")
        self.no_problems()

    def test_font_scale_persists(self):
        """UI.9: «Ajustes» picks the text size (Normal, Grande, Muy grande); the root font size and the body text grow,
        the choice survives a reload and nothing scrolls sideways at 360 px with the larger size."""
        self.page.ws.close()
        self.page = self.browser.new_page(width=360, height=780)
        self.open("/", "document.querySelector('a.project-card')")
        self.addCleanup(lambda: self.page.evaluate("localStorage.removeItem('gvig.fontScale')"))  # the profile is shared with other tests
        size = "parseFloat(getComputedStyle(%s).fontSize)"
        root, body = size % "document.documentElement", size % "document.querySelector('.project-card .meta')"
        base = (self.js(root), self.js(body))
        self.assertEqual(base[0], 16)
        self.click("#settings-btn")
        self.page.wait("document.getElementById('settings').matches(':popover-open')")
        self.js("(() => { const s = document.getElementById('font-scale'); s.value = 'large'; s.dispatchEvent(new Event('change', {bubbles: true})); })()")
        self.assertAlmostEqual(self.js(root), 16 * 1.15, delta=0.01)
        self.assertGreater(self.js(body), base[1])
        self.page.goto("http://127.0.0.1:%d/ui/index.html#/" % self.port)
        self.page.wait("document.querySelector('a.project-card')")
        self.assertAlmostEqual(self.js(root), 16 * 1.15, delta=0.01)
        self.assertGreater(self.js(body), base[1])
        self.assertEqual(self.js("document.getElementById('font-scale').value"), "large")
        self.js("(() => { const s = document.getElementById('font-scale'); s.value = 'xlarge'; s.dispatchEvent(new Event('change', {bubbles: true})); })()")
        self.assertAlmostEqual(self.js(root), 16 * 1.3, delta=0.01)
        for route, ready in (("/", "document.querySelector('a.project-card')"), (order_route("fondos/uno"), "document.querySelector('.gallery .attempt')")):
            self.open(route, ready)
            self.page.pump(0.3)
            self.assertEqual(self.js("document.documentElement.scrollWidth - document.documentElement.clientWidth"), 0, route)
            m = self.header_metrics()
            self.assertEqual(m["hscroll"], 0, route)
            self.assertTrue(m["crumbsInside"], route)
        self.no_problems()


def order_route(key, profile=PROFILE):
    return "/p/%s/o/%s/%s" % (PROJECT, profile, quote(key, safe=""))


@unittest.skipUnless(TOOLS, "ffmpeg and rsvg-convert are needed to compose")
class OrderScreen(UiBase):
    """The order: attempts, verdicts, choosing, retouching, compare, lightbox, texts, editor. One order per scenario."""

    KEYS = ("fondos/voto", "fondos/elegir", "fondos/comparar", "fondos/retoque", "fondos/textos", "fondos/editor",
            "fondos/volver", "fondos/plantilla", "fondos/guardar", "fondos/atajos", "fondos/texto", "fondos/tamano")

    @classmethod
    def prepare(cls):
        for key in cls.KEYS:
            cls.submit(key, count=2, work=False, text={"title1": "Titulo", "subtitle": "Sub"})
        run_cli("work")

    def order(self, key):
        self.open(order_route(key), "document.querySelectorAll('.gallery .attempt[data-kind=attempt]').length >= 2")
        self.page.wait("[...document.querySelectorAll('.gallery img')].every(i => i.complete && i.naturalWidth > 0)")

    def data(self, key):
        return self.api("GET", "/api/projects/%s/orders/%s/%s" % (PROJECT, PROFILE, quote(key, safe="")))

    def card(self, n):
        return ".gallery .attempt[data-attempt='%d']" % n

    def pressed(self, n, cls):
        return "document.querySelector(\"%s %s\").getAttribute('aria-pressed') === 'true'" % (self.card(n), cls)

    def press(self, selector, text=None):
        """Clicks the button inside ``selector`` whose text contains ``text``."""
        self.js("""(() => { const root = document.querySelector(%s);
            const b = [...root.querySelectorAll('button, a')].find(x => x.textContent.includes(%s));
            if (!b) throw new Error('no button ' + %s); b.click(); })()""" % (
            json.dumps(selector), json.dumps(text or ""), json.dumps(text)))

    def test_cards_show_images_and_metadata(self):
        self.order("fondos/voto")
        self.assertEqual(self.js("document.querySelectorAll('.gallery .attempt').length"), 2)
        self.assertEqual(self.js("document.querySelector('.gallery .attempt .meta .id').textContent"), "q2")
        self.assertTrue(self.js("document.querySelector('.gallery img').naturalWidth > 0"))
        self.no_problems()

    def test_vote_note_and_undo_vote(self):
        key = "fondos/voto"
        self.order(key)
        self.press(self.card(1), "Sí")
        self.page.wait(self.pressed(1, ".btn-yes"))
        self.assertEqual(self.data(key)["attempts"][0]["state"], "candidate")
        self.press(self.card(1), "No")
        self.page.wait(self.pressed(1, ".btn-no"))
        self.assertEqual(self.data(key)["attempts"][0]["state"], "discarded")
        self.press(self.card(1), "No")  # pressing again clears the verdict
        self.page.wait("!(%s)" % self.pressed(1, ".btn-no"))
        self.js("""(() => { const i = document.querySelector("%s input.note"); i.value = 'me gusta la luz';
            i.dispatchEvent(new Event('change')); })()""" % self.card(2))
        self.page.pump(0.6)
        self.assertEqual([a["note"] for a in self.data(key)["attempts"] if a["id"] == 2], ["me gusta la luz"])
        self.no_problems()

    def test_choose_and_undo(self):
        key = "fondos/elegir"
        self.order(key)
        self.press(self.card(2), "Elegir")
        self.page.wait("document.querySelector('.delivered')")
        self.assertEqual(self.data(key)["chosen"], 2)
        self.assertTrue(self.js("document.querySelector('.delivered').textContent.includes('q2')"))
        self.press(".delivered", "Deshacer")
        self.page.wait("!document.querySelector('.delivered')")
        self.assertIsNone(self.data(key)["chosen"])
        self.no_problems()

    def test_order_page_keeps_focus(self):
        self.order("fondos/textos")
        self.assertEqual(self.js("document.activeElement.tagName"), "H1")
        self.assertRegex(self.js("document.getElementById('status').textContent"), r"^\d+ intentos, \d+ nuevos$")
        self.assertEqual(self.js("document.getElementById('alerts').textContent"), "")
        sel = self.card(1) + " .btn-toggle"
        idx = "[...document.querySelector(\"%s\").querySelectorAll('button, a, input, select, summary')].indexOf(document.activeElement)" % self.card(1)
        self.js("document.querySelector(\"%s\").focus()" % sel)
        before = self.js(idx)
        self.assertGreaterEqual(before, 0)
        self.js("document.activeElement.click()")
        self.page.wait(self.pressed(1, ".btn-toggle"))
        self.page.wait("document.activeElement.closest('.attempt').dataset.attempt === '1' && %s === %d" % (idx, before))
        self.js("document.querySelector(\"%s\").focus()" % self.card(2))
        self.page.key("t")
        self.page.wait("document.activeElement.closest('.order-panel')")
        inside_retouch = self.js("!!document.activeElement.closest('.order-panel > :nth-child(2)')")
        self.assertTrue(inside_retouch)
        self.js("document.querySelector(\"%s\").focus()" % self.card(2))
        self.page.key("x")
        self.page.wait("document.activeElement.closest('.order-panel > :nth-child(3)')")

    def test_keyboard_shortcuts(self):
        self.order("fondos/atajos")
        self.js("document.querySelector(\"%s\").focus()" % self.card(2))
        self.page.key("ArrowRight")
        self.page.wait("document.activeElement.dataset.attempt === '1'")
        self.page.key("c")
        self.page.wait(self.pressed(1, ".btn-toggle"))
        self.page.key("c")
        self.page.wait("!(%s)" % self.pressed(1, ".btn-toggle"))
        self.page.key("f")
        self.page.wait("document.querySelector('.gallery-bar .btn-toggle').getAttribute('aria-pressed') === 'true'")
        self.page.key("f")
        self.page.key("Enter")
        self.page.wait("document.querySelector('#lightbox[open]')")
        self.assertTrue(self.js("document.getElementById('lightbox-img').getAttribute('src').includes('/attempts/1/image')"))
        self.page.key("Escape")
        self.page.wait("!document.querySelector('#lightbox[open]')")
        self.page.key("q")
        self.page.wait("!document.getElementById('queue-drawer').hidden")
        self.page.key("Escape")
        self.page.wait("document.getElementById('queue-drawer').hidden")
        self.no_problems()

    def test_compare_and_lightbox(self):
        self.order("fondos/comparar")
        self.press(self.card(1), "Comparar")
        self.page.wait("document.querySelector('p.hint')")
        self.press(self.card(2), "Comparar")
        self.page.wait("document.querySelector('section.compare figure img')")
        self.assertEqual(self.js("document.querySelectorAll('section.compare figure').length"), 2)
        before = self.js("document.querySelector('section.compare figcaption b').textContent")
        self.press("section.compare", "Intercambiar")
        self.page.wait("document.querySelector('section.compare figcaption b').textContent !== %s" % json.dumps(before))
        self.press("section.compare", "Cerrar")
        self.page.wait("!document.querySelector('section.compare')")
        self.click(self.card(1) + " button.open")
        self.page.wait("document.querySelector('#lightbox[open]') && document.getElementById('lightbox-img').naturalWidth > 0")
        self.click("#lightbox-close")
        self.page.wait("!document.querySelector('#lightbox[open]')")
        self.no_problems()

    def test_texts_panel_saves_and_recomposes(self):
        key = "fondos/textos"
        self.order(key)
        self.page.wait("document.getElementById('text-title1')")
        self.assertEqual(self.js("document.getElementById('text-title1').value"), "Titulo")
        self.js("""(() => { const i = document.getElementById('text-title1'); i.value = 'Otro';
            i.dispatchEvent(new Event('input')); })()""")
        self.press("section[aria-labelledby=text-h]", "Guardar")
        self.page.wait("document.querySelector('.toast-ok')")
        self.assertEqual(self.data(key)["text"]["title1"], "Otro")
        recompose = "document.querySelector(\"section[aria-labelledby=text-h] .panel-actions button:nth-child(2)\")"
        self.assertTrue(self.js(recompose + ".disabled"))
        self.press(self.card(2), "Elegir")
        self.page.wait("document.querySelector('.delivered')")
        self.page.wait("!" + recompose + ".disabled")
        self.press("section[aria-labelledby=text-h]", "Recomponer")
        self.page.wait("document.querySelectorAll('.toast-ok').length >= 2")
        self.no_problems()

    def test_retouch_queues_more_attempts_with_model_and_template(self):
        key = "fondos/retoque"
        self.order(key)
        self.page.wait("document.getElementById('retouch-model') && document.getElementById('retouch-template')")
        models = self.js("[...document.getElementById('retouch-model').options].filter(o => o.value && !o.disabled).map(o => o.value)")
        self.assertTrue(models, "no allowed model offered")
        self.js("""(() => { const p = document.getElementById('retouch-prompt'); p.value = 'Otra escena. The image is completely textless.';
            p.dispatchEvent(new Event('input'));
            const m = document.getElementById('retouch-model'); m.value = %s; m.dispatchEvent(new Event('change'));
            const t = document.getElementById('retouch-template'); t.value = 'claro'; t.dispatchEvent(new Event('change')); })()""" % json.dumps(models[0]))
        self.press("section[aria-labelledby=retouch-h]", "Otra semilla")
        self.page.wait("document.querySelector('.gallery .attempt[data-kind=entry]')")
        self.assertIn("En cola", self.js("document.querySelector('.gallery .attempt[data-kind=entry]').textContent"))
        queued = [e for e in self.api("GET", "/api/queue") if e["key"] == key and e["state"] == "queued"]
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0]["params"].get("model"), models[0])
        self.assertEqual(queued[0].get("template"), "claro")
        self.assertEqual(queued[0]["prompt"][:11], "Otra escena")
        run_cli("work")
        self.press(".gallery-bar", "Actualizar")
        self.page.wait("document.querySelectorAll('.gallery .attempt[data-kind=attempt]').length === 3")
        self.page.wait("[...document.querySelectorAll('.gallery img')].every(i => i.complete && i.naturalWidth > 0)")
        self.no_problems()

    def test_template_selector_recomposes(self):
        key = "fondos/plantilla"
        self.order(key)
        self.js("document.querySelector(\"%s details\").open = true" % self.card(2))
        self.js("(() => { const s = document.getElementById('template-2'); s.value = 'claro'; s.dispatchEvent(new Event('change')); })()")
        self.page.wait("document.querySelector('.toast-ok')")
        self.page.wait("document.getElementById('template-2').value === 'claro' && !document.getElementById('template-2').disabled")
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"]["templateId"], "claro")
        self.no_problems()

    def test_tap_targets_are_44px(self):
        """UI.4: at 360 and 1440, no visible link, button, field or tab stop is smaller than 44x44 on the projects
        list, an order page (retouch and texts panels, lists open) or the editor."""
        key = "fondos/atajos"
        for width in (360, 1440):
            self.page.ws.close()
            self.page = self.browser.new_page(width=width, height=780)
            where = "at %d" % width
            self.open("/", "document.querySelector('a.project-card')")
            self.assert_tap_targets("on the projects list " + where)
            for tab, ready in (("pedidos", ".order-row"), ("piezas", ".piece-card"), ("marca", ".check-list .check-item")):
                self.open("/p/%s/%s" % (PROJECT, tab), "document.querySelector(%s)" % json.dumps(ready))
                self.assert_tap_targets("on the %s tab %s" % (tab, where))
            self.open("/p/%s/pedidos" % PROJECT, "document.querySelector('.order-row')")
            self.click("button[data-slot=new-order]")
            self.page.wait("document.querySelector('dialog.new-order[open]') && document.getElementById('no-copy')")
            self.assert_tap_targets("in the new order panel " + where)
            self.page.key("Escape")
            self.page.wait("!document.querySelector('dialog[open]')")
            self.order(key)
            self.click("#help")
            self.page.wait("document.querySelector('dialog[open]')")
            self.assert_tap_targets("in the shortcuts dialog " + where)
            self.page.key("Escape")
            self.page.wait("!document.querySelector('dialog[open]')")
            self.js("for (const d of document.querySelectorAll('.attempt details, .order-panel details')) d.open = true")
            self.assert_tap_targets("on the order page " + where)
            self.open_editor(key)
            self.assert_tap_targets("in the editor " + where)
        self.no_problems()

    def check_measure_chip(self, sel, *expected):
        """The chip at `sel` is a 44 px button; Enter opens its detail (each expected text in it), Esc closes it and the
        focus returns to the chip."""
        self.page.wait("document.querySelector(%s)" % json.dumps(sel))
        m = self.js("""(() => { const c = document.querySelector(%s), r = c.getBoundingClientRect();
            return {tag: c.tagName, h: r.height, expanded: c.getAttribute('aria-expanded'), label: c.getAttribute('aria-label'),
                    controls: c.getAttribute('aria-controls'), target: c.getAttribute('popovertarget')}; })()""" % json.dumps(sel))
        self.assertEqual(m["tag"], "BUTTON")
        self.assertGreaterEqual(m["h"], 44)
        self.assertEqual(m["expanded"], "false")
        self.assertTrue(m["label"].startswith("Medida de marca: "), m["label"])
        self.assertTrue(m["controls"] and m["controls"] == m["target"])
        box = "document.getElementById(%s)" % json.dumps(m["controls"])
        self.js("document.querySelector(%s).focus()" % json.dumps(sel))
        self.page.key("Enter")
        self.page.wait("%s.matches(':popover-open')" % box)
        self.assertEqual(self.js("document.querySelector(%s).getAttribute('aria-expanded')" % json.dumps(sel)), "true")
        text = self.js("%s.textContent" % box)
        for want in expected:
            self.assertRegex(text, want)
        self.page.key("Escape")
        self.page.wait("!%s.matches(':popover-open')" % box)
        self.assertTrue(self.js("document.activeElement === document.querySelector(%s)" % json.dumps(sel)), "the focus did not return to the chip")
        self.assertEqual(self.js("document.querySelector(%s).getAttribute('aria-expanded')" % json.dumps(sel)), "false")

    def test_measure_chip_opens_its_detail(self):
        """UI.4: the measure chip is a 44 px button that opens a native popover with the contrast (mean and worst) and
        the palette, each line with its verdict in words; Esc closes it and the focus returns to the chip. On the card
        there is no zone, so only the palette is measured; in the editor the text elements have one."""
        verdict = r"(correcto|justo|insuficiente)"
        palette = r"Paleta \d+ % dentro de la marca \(mínimo \d+ %\): " + verdict
        self.order("fondos/atajos")
        self.check_measure_chip(".gallery .attempt[data-kind=attempt] .measure button.chip", r"Sin zona declarada", palette)
        self.open_editor("fondos/atajos")
        self.check_measure_chip("dialog.editor .measure button.chip", r"Contraste medio \d+\.\d:1 \(AA ≥ 4,5\): " + verdict,
                                r"Contraste del peor punto \d+\.\d:1 \(ámbar ≥ 3\): " + verdict)
        self.no_problems()

    def toast(self, text="Aviso de prueba"):
        """Raises a persistent toast through the page's own module (the same instance the app uses)."""
        self.js("import('/ui/js/components/toast.js').then((m) => { m.toast(%s, {timeout: 0}); return true; })" % json.dumps(text))
        self.page.wait(self.OWN_TOAST)

    # the app may show its own toasts (no worker...): the test looks only at the one it raised
    OWN_TOAST = "[...document.querySelectorAll('#toasts .toast')].find((t) => t.textContent.startsWith('Aviso de prueba'))"

    def test_retouch_panel_is_reachable_and_toasts_do_not_cover(self):
        """UI.5: at 1440 the retouch panel stays in the window and «Textos» is reached by scrolling only the panel; at
        360 a «Retoque» button opens the same panel as a modal side dialog (focus inside, Esc closes it and returns the
        focus to the button); a toast never overlaps the buttons of the first card (at 360 and 1440) and Esc closes it."""
        key = "fondos/atajos"
        footer = """(() => { const c = document.querySelector('.gallery .attempt[data-kind=attempt]');
            const bs = [...c.querySelectorAll('.actions > button')].filter((b) => b.getClientRects().length);
            bs[bs.length - 1].scrollIntoView({block: 'end'});
            return bs.map((b) => { const r = b.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }); })()"""
        toast_rect = """(() => { const r = [...document.querySelectorAll('#toasts .toast')].find((t) => t.textContent.startsWith('Aviso de prueba')).getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })()"""

        def overlaps(a, b):
            return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

        def check_toast(where):
            buttons = self.js(footer)
            self.assertTrue(buttons, "no footer buttons " + where)
            self.toast()
            self.page.pump(0.2)
            rect = self.js(toast_rect)
            for b in buttons:
                self.assertFalse(overlaps(rect, b), "the toast %s covers a button of the first card %s: %s" % (rect, where, b))
            # Esc with the focus inside the toast closes it
            self.js("%s.querySelector('button').focus()" % self.OWN_TOAST)
            self.page.key("Escape")
            self.page.wait("!(%s)" % self.OWN_TOAST)
            # Esc anywhere else closes the last toast when nothing else is open
            self.toast()
            self.js("document.activeElement.blur()")
            self.page.key("Escape")
            self.page.wait("!(%s)" % self.OWN_TOAST)

        # 1440: the sticky column
        self.page.ws.close()
        self.page = self.browser.new_page(width=1440, height=780)
        self.order(key)
        m = self.js("""(() => { const r = document.querySelector('.order-panel').getBoundingClientRect();
            return {top: r.top, bottom: r.bottom, vh: innerHeight, button: getComputedStyle(document.querySelector('.retouch-open')).display}; })()""")
        self.assertGreaterEqual(m["top"], 0)
        self.assertLessEqual(m["bottom"], m["vh"], "the panel is taller than the window at 1440: %s" % m)
        self.assertEqual(m["button"], "none", "the «Retoque» button shows at 1440")
        self.js("window.scrollTo(0, 200)")
        y = self.js("scrollY")
        after = self.js("""(() => { const p = document.querySelector('.order-panel'); p.scrollTop = p.scrollHeight;
            const pr = p.getBoundingClientRect(), h = document.getElementById('text-h'), r = h.getBoundingClientRect();
            return {y: scrollY, panelBottom: pr.bottom, panelTop: pr.top, hTop: r.top, hBottom: r.bottom}; })()""")
        self.assertEqual(after["y"], y, "scrolling the panel moved the page")
        self.assertGreaterEqual(after["hTop"], after["panelTop"] - 1, "«Textos» is above the panel: %s" % after)
        self.assertLessEqual(after["hBottom"], after["panelBottom"] + 1, "«Textos» is below the panel: %s" % after)
        self.assertLessEqual(after["panelBottom"], m["vh"], "the sticky panel left the window: %s" % after)
        self.js("window.scrollTo(0, 0)")
        check_toast("at 1440")

        # 360: the same panel as a side dialog
        self.page.ws.close()
        self.page = self.browser.new_page(width=360, height=780)
        self.order(key)
        btn = ".retouch-open"
        self.assertEqual(self.js("document.querySelector('.order-panel').getClientRects().length"), 0, "the panel shows stacked at 360")
        r = self.js("(() => { const r = document.querySelector('%s').getBoundingClientRect(); return [r.width, r.height]; })()" % btn)
        self.assertGreater(r[0], 0, "the «Retoque» button is not visible at 360")
        self.assertGreaterEqual(r[1], 44)
        self.click(btn)
        self.page.wait("document.querySelector('.order-panel.is-open')")
        d = self.js("""(() => { const p = document.querySelector('.order-panel'), pr = p.getBoundingClientRect(), a = document.activeElement;
            return {role: p.getAttribute('role'), modal: p.getAttribute('aria-modal'), label: document.getElementById(p.getAttribute('aria-labelledby')).textContent,
                inside: p.contains(a), top: pr.top, headerH: document.querySelector('.app-header').getBoundingClientRect().height, bottom: pr.bottom, vh: innerHeight,
                inert: [document.querySelector('.app-header').inert, document.querySelector('.order-layout > div').inert, p.inert],
                expanded: document.querySelector('%s').getAttribute('aria-expanded'),
                prompt: Boolean(p.querySelector('#retouch-prompt')), texts: Boolean(p.querySelector('#text-h'))}; })()""" % btn)
        self.assertEqual((d["role"], d["modal"]), ("dialog", "true"))
        self.assertEqual(d["label"], "Retoque y textos")
        self.assertTrue(d["inside"], "the focus did not go inside the dialog")
        self.assertAlmostEqual(d["top"], d["headerH"], delta=1)
        self.assertLessEqual(d["bottom"], d["vh"])
        self.assertEqual(d["inert"], [True, True, False])
        self.assertEqual(d["expanded"], "true")
        self.assertTrue(d["prompt"] and d["texts"], d)
        self.assert_tap_targets("in the retouch dialog at 360")
        # Tab from the last control wraps inside the dialog
        self.js("""(() => { const n = [...document.querySelectorAll('.order-panel button:not(:disabled), .order-panel a[href], .order-panel input:not(:disabled), .order-panel select:not(:disabled), .order-panel [tabindex="0"]')].filter((x) => x.getClientRects().length); n[n.length - 1].focus(); })()""")
        self.page.key("Tab")
        self.assertTrue(self.js("document.querySelector('.order-panel').contains(document.activeElement)"), "Tab left the dialog")
        self.page.key("Escape")
        self.page.wait("!document.querySelector('.order-panel.is-open')")
        self.assertTrue(self.js("document.activeElement === document.querySelector('%s')" % btn), "the focus did not return to «Retoque»")
        self.assertEqual(self.js("[document.querySelector('.app-header').inert, document.querySelector('.order-layout > div').inert]"), [False, False])
        # the T shortcut opens it and focuses its first control
        self.js("document.querySelector('.gallery .attempt[data-kind=attempt]').focus()")
        self.page.key("t")
        self.page.wait("document.querySelector('.order-panel.is-open')")
        self.assertTrue(self.js("document.querySelector('.order-panel').contains(document.activeElement) && document.activeElement !== document.querySelector('.order-panel')"))
        self.page.key("Escape")
        self.page.wait("!document.querySelector('.order-panel.is-open')")
        check_toast("at 360")
        self.no_problems()

    # the editor -------------------------------------------------------------------------------------------------
    def open_editor(self, key, n=2, boxes=3):
        self.order(key)
        self.js("document.querySelector(\"%s details\").open = true" % self.card(n))
        self.press(self.card(n) + " .slot[data-slot=editor]", "Editar")
        self.page.wait("document.querySelector('dialog.editor[open]') && document.querySelectorAll('.ed-box').length === %d" % boxes)
        self.page.wait("document.querySelector('.ed-img').complete && document.querySelector('.ed-box').style.width")

    def test_editor_moves_a_box_with_the_keyboard_and_applies(self):
        key = "fondos/editor"
        self.open_editor(key)
        self.assertEqual(self.js("document.activeElement.dataset.element"), "title1")
        for _ in range(3):
            self.page.key("ArrowRight")
        self.page.key("ArrowDown", ctrl=True)  # UI.6: Ctrl makes the step 10 px (Shift resizes)
        self.assertEqual(self.js("document.querySelector('.ed-item output').textContent"), "43, 50 · 500×60")
        self.press("dialog.editor", "Aplicar")
        self.page.wait("!document.querySelector('dialog.editor')")
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"]["layout"], {"title1": {"x": 43, "y": 50, "w": 500, "h": 60}})
        self.no_problems()

    # UI.6: the visible handles of the editor, grouped by box: [[element, x, y, w, h], ...]
    VISIBLE_HANDLES = """[...document.querySelectorAll('.ed-box .ed-handle')]
        .filter((n) => getComputedStyle(n).display !== 'none')
        .map((n) => { const r = n.getBoundingClientRect(); return [n.closest('.ed-box').dataset.element, r.left, r.top, r.width, r.height]; })"""

    def test_editor_resizes_with_the_keyboard(self):
        """UI.6 (audit R4, A6; WCAG 2.5.7): Shift+arrows change `w`/`h` of the focused box (Ctrl makes the step 10 px,
        plain arrows still move it) and the numeric fields x, y, w, h of the side panel move or resize it within the
        target. At 360 the dialog fills the window, the stage is `100vw - 24px` wide and at most max(50vh, 320px)
        high, the 24 px handles (44 px touch zone) show only on the picked box so no two boxes' handles overlap, the
        box labels leave the stage (the names stay in the list) and nothing scrolls sideways."""
        key = "fondos/tamano"
        self.open_editor(key)
        self.assertEqual(self.js("document.activeElement.dataset.element"), "title1")
        nums = "document.querySelector('.ed-item[data-element=title1] output').textContent"
        self.page.key("ArrowRight", shift=True)
        self.page.key("ArrowRight", shift=True)
        self.page.key("ArrowDown", shift=True)
        self.page.key("ArrowLeft", shift=True)
        self.assertEqual(self.js(nums), "40, 40 · 501×61")
        self.page.key("ArrowRight", shift=True, ctrl=True)
        self.assertEqual(self.js(nums), "40, 40 · 511×61")
        self.page.key("ArrowDown", ctrl=True)
        self.assertEqual(self.js(nums), "40, 50 · 511×61")
        # the numeric fields follow the picked box and drive it: x moves (the size stays), w resizes (x stays) and
        # the target clips what does not fit
        self.assertFalse(self.js("document.querySelector('.ed-geom').hidden"))
        self.assertEqual(self.js("['x', 'y', 'w', 'h'].map((k) => document.getElementById('ed-' + k).value)"), ["40", "50", "511", "61"])
        self.set_field("ed-x", "100")
        self.assertEqual(self.js(nums), "100, 50 · 511×61")
        self.set_field("ed-w", "2000")
        self.assertEqual(self.js(nums), "100, 50 · 1100×61")
        self.assertEqual(self.js("document.getElementById('ed-w').value"), "1100")
        self.set_field("ed-h", "")  # half-typed: nothing moves
        self.assertEqual(self.js(nums), "100, 50 · 1100×61")
        self.press("dialog.editor", "Aplicar")
        self.page.wait("!document.querySelector('dialog.editor')")
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"]["layout"], {"title1": {"x": 100, "y": 50, "w": 1100, "h": 61}})
        self.no_problems()
        # at 360: the stage takes the width, the handles (24 px, 44 px touch zone) show only on the picked box and
        # never overlap between boxes, the labels leave the stage and nothing scrolls sideways
        self.page.ws.close()
        self.page = self.browser.new_page(width=360, height=780)
        self.open_editor(key)
        inner_w, inner_h = self.js("window.innerWidth"), self.js("window.innerHeight")
        stage = self.js("document.querySelector('.ed-stage').getBoundingClientRect().toJSON()")
        self.assertAlmostEqual(stage["width"], inner_w - 24, delta=1)
        self.assertLessEqual(self.js("document.querySelector('.ed-img').getBoundingClientRect().height"), max(inner_h / 2, 320) + 1)
        for sel in ("document.documentElement", "document.querySelector('dialog.editor')", "document.querySelector('.ed-main')", "document.querySelector('.ed-side')"):
            self.assertLessEqual(self.js(sel + ".scrollWidth"), self.js(sel + ".clientWidth || window.innerWidth"), sel)
        self.assertEqual(self.js("[...document.querySelectorAll('.ed-name')].filter((n) => getComputedStyle(n).display !== 'none').length"), 0)
        self.assertEqual(self.js("[...document.querySelectorAll('.ed-item b')].map((n) => n.textContent)"), ["title1", "subtitle", "logo"])
        for element in ("title1", "subtitle", "logo"):
            self.js("document.querySelector('.ed-box[data-element=%s]').focus()" % element)
            handles = self.js(self.VISIBLE_HANDLES)
            for i, (e1, x1, y1, w1, h1) in enumerate(handles):  # whatever is visible: no overlap between boxes
                for e2, x2, y2, w2, h2 in handles[i + 1:]:
                    if e1 != e2:
                        self.assertFalse(x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1, "handles of %s and %s overlap" % (e1, e2))
            self.assertEqual(sorted({hd[0] for hd in handles}), [element])  # only the picked box shows them
            self.assertEqual(len(handles), 4)
            for _, _, _, w, hgt in handles:
                self.assertAlmostEqual(w, 24, delta=0.5)
                self.assertAlmostEqual(hgt, 24, delta=0.5)
            self.assertEqual(self.js("getComputedStyle(document.querySelector('.ed-box[data-element=%s] .ed-handle'), '::before').top" % element), "-10px")
        self.assert_tap_targets("in the editor at 360")
        self.no_problems()

    def test_editor_goes_back_to_the_template(self):
        key = "fondos/volver"  # its own order: the tests of a class run in name order
        self.open_editor(key)
        for _ in range(3):
            self.page.key("ArrowRight")
        self.press("dialog.editor", "Aplicar")
        self.page.wait("!document.querySelector('dialog.editor')")
        self.open_editor(key)
        self.assertEqual(self.js("document.querySelector('.ed-item output').textContent"), "43, 40 · 500×60")
        self.press("dialog.editor", "Volver")
        self.page.wait("!document.querySelector('dialog.editor')")
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"].get("layout") or {}, {})
        self.no_problems()

    def test_editor_saves_a_template_that_shows_up_in_the_selector(self):
        key = "fondos/guardar"
        self.open_editor(key)
        self.page.key("ArrowLeft")
        self.press("dialog.editor", "Guardar como")
        self.page.wait("document.querySelector('dialog.editor-save[open]')")
        self.js("""(() => { const i = document.getElementById('ed-name'); i.value = 'Mal Nombre';
            document.querySelector('dialog.editor-save form').requestSubmit(); })()""")
        self.page.wait("document.getElementById('ed-name-error').textContent")
        self.js("""(() => { const i = document.getElementById('ed-name'); i.value = 'movida';
            document.querySelector('dialog.editor-save form').requestSubmit(); })()""")
        self.page.wait("!document.querySelector('dialog.editor-save') && !document.querySelector('dialog.editor')")
        self.page.wait("document.querySelector(\"#template-1 option[value=movida]\")")
        listed = self.api("GET", "/api/projects/%s/profiles/%s/templates" % (PROJECT, PROFILE))
        self.assertIn("movida", [t["id"] for t in listed])
        self.no_problems()


    def set_field(self, field_id, value):
        """Types `value` into the editor field `field_id` (the panel listens to `input`)."""
        self.js("""(() => { const e = document.getElementById(%s); e.value = %s;
            e.dispatchEvent(new Event('input', { bubbles: true })); })()""" % (json.dumps(field_id), json.dumps(value)))

    def test_editor_edits_text_and_style_warns_of_overflow_and_adds_texts(self):
        """F4e.2c: the «Texto y tipografía» panel shows up for the focused text, its fields go to the layout (only what
        differs from the template; the box preview is an inline SVG), Apply keeps the editor open with the overflow
        of the element in its row (amber + text) and the missing font in the notice, and added texts (`extra1`,
        `add: true`, full style) can be removed before applying or sent whole. Nothing scrolls sideways at 360."""
        key = "fondos/texto"
        self.open_editor(key)
        self.assertEqual(self.js("document.activeElement.dataset.element"), "title1")
        self.page.wait("!document.querySelector('.ed-fields').hidden && document.getElementById('ed-text').placeholder === 'Titulo'")
        self.assertEqual(self.js("document.querySelector('.ed-editing').textContent"), "Editando title1")
        self.assertTrue(self.js("document.querySelector('dialog.editor button.btn-primary').disabled"))
        self.page.wait("document.querySelectorAll('#ed-fonts option').length >= 1")  # fed by GET /api/fonts
        self.set_field("ed-text", "Hola\nMundo")
        self.set_field("ed-family", "Fuente Inexistente")
        self.set_field("ed-size", "400")
        self.set_field("ed-lh", "0.5")  # out of range: Apply is held back with the reason under the field
        self.assertEqual(self.js("document.getElementById('ed-lh-error').textContent"), "Un número de 0,8 a 3.")
        self.assertTrue(self.js("document.querySelector('dialog.editor button.btn-primary').disabled"))
        self.set_field("ed-lh", "")
        self.assertEqual(self.js("document.getElementById('ed-lh-error').textContent"), "")
        self.assertFalse(self.js("document.querySelector('dialog.editor button.btn-primary').disabled"))
        self.assertEqual(self.js("document.querySelectorAll(\"[data-element=title1].ed-box.is-preview svg tspan\").length"), 2)
        fonts = self.api("GET", "/api/fonts?project=%s" % PROJECT)
        if fonts["available"]:
            self.assertIn("Fuente Inexistente", self.js("document.getElementById('ed-family-warn').textContent"))
        self.press("dialog.editor", "Aplicar")
        self.page.wait("document.querySelector('dialog.editor[open] .ed-item.is-overflow[data-element=title1]')")
        warn = self.js("document.querySelector('.ed-item[data-element=title1] .ed-warn').textContent")
        self.assertTrue(warn.startswith("No cabe en su caja: pedido 400 px, pintado al mínimo 200 px"), warn)
        notice = self.js("document.querySelector('dialog.editor .notice-warn').textContent")
        self.assertIn("title1", notice)
        if fonts["available"]:
            self.assertIn("Fuente Inexistente", notice)
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"]["layout"], {"title1": {"x": 40, "y": 40, "w": 500, "h": 60, "text": "Hola\nMundo",
                                                             "style": {"family": "Fuente Inexistente", "size": 400}}})
        self.assertEqual(a["compose"]["overflow"], {"title1": {"size": 400, "min": 200}})
        self.assertTrue(self.js("document.querySelector('dialog.editor button.btn-primary').disabled"))  # nothing pending
        # add a text, remove it, add again and apply: it goes whole
        self.press("dialog.editor", "Añadir texto")
        self.page.wait("document.querySelectorAll('.ed-box').length === 4 && document.activeElement.dataset.element === 'extra1'")
        self.assertEqual(self.js("document.querySelector('.ed-editing').textContent"), "Editando extra1")
        self.assertEqual(self.js("document.getElementById('ed-text').value"), "Texto nuevo")
        self.press(".ed-item[data-element=extra1]", "Quitar")
        self.page.wait("document.querySelectorAll('.ed-box').length === 3")
        self.assertTrue(self.js("document.querySelector('dialog.editor button.btn-primary').disabled"))
        self.press("dialog.editor", "Añadir texto")
        self.page.wait("document.activeElement.dataset.element === 'extra1'")
        self.set_field("ed-text", "Pie")
        self.set_field("ed-size", "24")
        self.set_field("ed-align", "center")
        # title1 back to one line and the template's style: without warnings left, Apply closes the editor
        self.js("document.querySelector('.ed-box[data-element=title1]').focus()")
        self.page.wait("document.querySelector('.ed-editing').textContent === 'Editando title1'")
        self.assertEqual(self.js("document.getElementById('ed-size').value"), "400")
        self.set_field("ed-text", "Hola")
        self.set_field("ed-family", "")
        self.set_field("ed-size", "")
        state = "JSON.stringify([...document.querySelectorAll('dialog.editor .field-error, dialog.editor .notice-warn')].map((e) => e.id + ': ' + e.textContent).filter((x) => !/: $/.test(x)))"
        self.assertFalse(self.js("document.querySelector('dialog.editor button.btn-primary').disabled"), self.js(state))
        self.press("dialog.editor", "Aplicar")
        try:
            self.page.wait("!document.querySelector('dialog.editor')")
        except browser.CdpError:
            self.fail("the editor stays open: %s" % self.js(state))
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"]["layout"]["title1"], {"x": 40, "y": 40, "w": 500, "h": 60, "text": "Hola"})
        self.assertEqual(a["compose"].get("overflow", {}), {})
        extra = a["compose"]["layout"]["extra1"]
        self.assertEqual(extra["text"], "Pie")
        self.assertTrue(extra["add"])
        self.assertEqual(extra["style"]["size"], 24)
        self.assertEqual(extra["style"]["align"], "center")
        self.assertEqual(sorted(extra["style"]), ["align", "color", "family", "italic", "size", "weight"])
        # at 360 the panel fits: no sideways scroll, and the added text comes back as an item
        self.page.ws.close()
        self.page = self.browser.new_page(width=360, height=780)
        self.open_editor(key, boxes=4)  # the added text comes back as an item
        self.assertEqual(self.js("document.querySelector('.ed-item[data-element=extra1] .hint').textContent"), "texto · añadido")
        self.assertLessEqual(self.js("document.documentElement.scrollWidth"), self.js("window.innerWidth"))
        self.assertLessEqual(self.js("document.querySelector('.ed-side').scrollWidth"), self.js("document.querySelector('.ed-side').clientWidth"))
        self.assert_tap_targets("in the text panel at 360")
        self.no_problems()


class NewOrderScreen(UiBase):
    @classmethod
    def prepare(cls):
        cls.submit("fondos/previo", count=1, work=True)

    def test_create_an_order_from_the_panel(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('.order-row')")
        self.click("button[data-slot=new-order]")
        self.page.wait("document.querySelector('dialog.new-order[open]') && document.getElementById('no-copy')")
        # an invalid key and an empty prompt are refused without leaving
        self.js("document.querySelector('dialog.new-order form').requestSubmit()")
        self.page.wait("!document.getElementById('no-error').hidden")
        self.js("""(() => { const set = (id, v) => { const e = document.getElementById(id); e.value = v;
            e.dispatchEvent(new Event('input')); e.dispatchEvent(new Event('change')); };
            set('no-key', 'fondos/nuevo'); set('no-prompt', 'Algo nuevo. The image is completely textless.');
            set('no-seed', '7'); set('no-count', '2'); })()""")
        self.js("document.querySelector('dialog.new-order form').requestSubmit()")
        self.page.wait("location.hash === '#/p/tarkor/o/og/fondos%2Fnuevo'")
        self.page.wait("document.querySelectorAll('.gallery .attempt[data-kind=entry]').length === 2")
        self.click(".queue-pill")
        self.page.wait("document.querySelectorAll('#queue-drawer .queue-entry').length >= 2")
        self.assertIn("fondos/nuevo", self.js("document.querySelector('#queue-drawer .queue-entry').textContent"))
        run_cli("work")
        self.page.wait("document.querySelectorAll('.gallery .attempt[data-kind=attempt]').length === 2", timeout=20)
        self.no_problems()

    def test_copy_from_fills_the_form(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('.order-row')")
        self.click("button[data-slot=new-order]")
        self.page.wait("!document.getElementById('no-copy').closest('.field').hidden")
        self.js("(() => { const s = document.getElementById('no-copy'); s.value = 'fondos/previo'; s.dispatchEvent(new Event('change')); })()")
        self.page.wait("document.getElementById('no-prompt').value.includes('test scene')")
        self.assertEqual(self.js("document.getElementById('no-text-title1').value"), "")
        self.no_problems()


class QueueDrawer(UiBase):
    def setUp(self):
        run_cli("queue", "clear")
        for n in range(3):
            self.submit("fila/p%d" % n, count=1, work=False)
        super().setUp()

    ORDER = ("JSON.stringify([...document.querySelectorAll('#queue-drawer .queue-entry .who')]"
             ".map(w => w.textContent.split(' · ')[1].split(' @ ')[0])) === %s")

    def order_is(self, *keys):
        return self.ORDER % json.dumps(json.dumps(list(keys), separators=(",", ":")))

    def test_move_and_clear(self):
        self.open("/", "document.querySelector('.queue-pill')")
        self.page.wait("document.querySelector('.queue-pill').textContent.includes('3 en cola')")
        self.click(".queue-pill")
        self.page.wait("document.querySelectorAll('#queue-drawer .queue-entry').length === 3")
        self.page.wait(self.order_is("fila/p0", "fila/p1", "fila/p2"))
        self.click("#queue-drawer .queue-entry:nth-child(2) [data-fid^=top-]")
        self.page.wait(self.order_is("fila/p1", "fila/p0", "fila/p2"))
        self.click("#queue-drawer .queue-entry:nth-child(2) [data-fid^=down-]")
        self.page.wait(self.order_is("fila/p1", "fila/p2", "fila/p0"))
        self.click("#queue-drawer .queue-entry:nth-child(3) [data-fid^=up-]")
        self.page.wait(self.order_is("fila/p1", "fila/p0", "fila/p2"))
        # cancelling the confirmation keeps everything
        self.click("[data-fid=clear-all]")
        self.page.wait("document.querySelector('dialog.confirm[open]')")
        self.click("dialog.confirm button:not(.btn-danger)")
        self.page.wait("!document.querySelector('dialog.confirm')")
        self.assertEqual(len([e for e in self.api("GET", "/api/queue") if e["state"] == "queued"]), 3)
        self.click("[data-fid=clear-all]")
        self.page.wait("document.querySelector('dialog.confirm[open]')")
        self.click("dialog.confirm button.btn-danger")
        self.page.wait("!document.querySelector('dialog.confirm')")
        self.page.wait("document.querySelectorAll('#queue-drawer .queue-entry').length === 0")
        self.assertEqual([e for e in self.api("GET", "/api/queue") if e["state"] == "queued"], [])
        self.no_problems()


    def test_tap_targets_are_44px(self):
        """UI.4: every control of the queue drawer (and the pill) is at least 44x44 at 360 and 1440."""
        for width in (360, 1440):
            self.page.ws.close()
            self.page = self.browser.new_page(width=width, height=780)
            self.open("/", "document.querySelector('.queue-pill')")
            self.click(".queue-pill")
            self.page.wait("document.querySelectorAll('#queue-drawer .queue-entry').length >= 3")
            self.assert_tap_targets("in the queue drawer at %d" % width)
        self.no_problems()

    def test_queue_drawer_fits_and_traps_focus(self):
        """UI.2: the drawer is a modal dialog right under the header at any width, nothing in it scrolls sideways,
        the thumbnail and the «Fallidas» filter are fully visible, Tab wraps inside it, the page behind is inert and
        Esc closes it and returns the focus to the pill."""
        from gimg import queue
        queue.finish(queue.claim()["id"], "failed", error="boom")
        queue.claim()  # p1 runs; a live worker lock keeps it from being recovered as queued
        queue.worker_lock_path().parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(queue.worker_lock_path()), os.O_RDWR | os.O_CREAT, 0o600)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for width in (360, 1440):
            self.page.ws.close()
            self.page = self.browser.new_page(width=width, height=780)
            where = "at %d" % width
            self.open("/", "document.querySelector('.queue-pill')")
            self.click(".queue-pill")
            self.page.wait("document.querySelectorAll('#queue-drawer .queue-entry').length >= 2")
            m = self.js("""(() => { const d = document.getElementById('queue-drawer'), dr = d.getBoundingClientRect();
                const inside = (n) => { const r = n.getBoundingClientRect();
                    return r.width > 0 && r.height > 0 && r.left >= dr.left - 0.5 && r.right <= dr.right + 0.5 && r.top >= dr.top - 0.5 && r.bottom <= dr.bottom + 0.5; };
                const failed = document.querySelector('[data-fid=filter-failed]'), thumb = d.querySelector('.queue-entry .thumb, .queue-entry .thumb-empty');
                const nodes = [...d.querySelectorAll('button:not(:disabled), a[href]')].filter((n) => n.getClientRects().length);
                return {top: dr.top, headerH: document.querySelector('.app-header').getBoundingClientRect().height,
                    scroll: [d.scrollWidth, d.clientWidth], failedOk: Boolean(failed) && inside(failed), thumbOk: Boolean(thumb) && inside(thumb),
                    entryScroll: [...d.querySelectorAll('.queue-entry')].map((e) => e.scrollWidth - e.clientWidth),
                    role: d.getAttribute('role'), modal: d.getAttribute('aria-modal'), label: document.getElementById(d.getAttribute('aria-labelledby')).textContent,
                    inert: [document.getElementById('main').inert, document.querySelector('.app-header').inert, d.inert],
                    focus: document.activeElement.tagName + '#' + document.activeElement.id,
                    first: nodes[0].dataset.fid, last: nodes[nodes.length - 1].dataset.fid}; })()""")
            self.assertAlmostEqual(m["top"], m["headerH"], delta=1, msg="drawer top %s vs header %s %s" % (m["top"], m["headerH"], where))
            self.assertLessEqual(m["scroll"][0], m["scroll"][1], "drawer scrolls sideways %s: %s" % (where, m["scroll"]))
            self.assertTrue(all(x <= 0 for x in m["entryScroll"]), "an entry overflows %s: %s" % (where, m["entryScroll"]))
            self.assertTrue(m["failedOk"], "the «Fallidas» filter is cut or hidden " + where)
            self.assertTrue(m["thumbOk"], "the thumbnail is cut or hidden " + where)
            self.assertEqual((m["role"], m["modal"]), ("dialog", "true"), where)
            self.assertEqual(m["label"], "Cola", where)
            self.assertEqual(m["inert"], [True, True, False], "inert main/header/drawer %s" % where)
            self.assertEqual(m["focus"], "H2#queue-title", "the focus does not start on the title " + where)
            focus = "document.querySelector('[data-fid=%s]').focus()"
            active = "document.activeElement.dataset.fid"
            self.js(focus % m["last"])
            self.page.key("Tab")
            self.assertEqual(self.js(active), m["first"], "Tab from the last control does not wrap " + where)
            self.page.key("Tab", shift=True)
            self.assertEqual(self.js(active), m["last"], "Shift+Tab from the first control does not wrap " + where)
            self.page.key("Escape")
            self.page.wait("document.getElementById('queue-drawer').hidden")
            self.assertEqual(self.js("[document.activeElement.dataset.fid, document.getElementById('main').inert, document.querySelector('.app-header').inert]"),
                             ["pill", False, False], "after Esc the focus is not on the pill or the page is still inert " + where)
        self.no_problems()


if __name__ == "__main__":
    unittest.main()
