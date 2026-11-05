"""F4a: the web interface run for real in a headless Chrome over the DevTools protocol (tests/browser.py), against a
real `gimg serve` (in a thread) on the fake engine, temporary folders and an example project. Nothing is generated: the
fake engine writes placeholder images. Every scenario ends by asserting the page reported no exception, no console
error, no CSP violation and no failed load. Skipped when no Chrome is found (see ``GIMG_TEST_CHROME``)."""
import contextlib
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
            const tops = new Set([...crumbs.children].map((c) => { const b = c.getBoundingClientRect(); return Math.round(b.top + b.height / 2); }));  // same line = same centre
            return {headerH: header.height, token: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-h')),
                    crumbLines: tops.size, crumbsInside: r('#crumbs').bottom <= header.bottom + 0.5,
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
        sizes = self.js("['lang', 'theme'].map((id) => { const r = document.getElementById(id).getBoundingClientRect(); return [r.width, r.height]; })")
        for w, h in sizes:
            self.assertGreaterEqual(h, 44)
            self.assertGreaterEqual(w, 120)
        self.assertEqual(self.js("document.getElementById('settings-btn').getAttribute('aria-label')"), "Ajustes")
        self.page.key("Escape")
        self.page.wait("!document.getElementById('settings').matches(':popover-open')")
        self.no_problems()


def order_route(key, profile=PROFILE):
    return "/p/%s/o/%s/%s" % (PROJECT, profile, quote(key, safe=""))


@unittest.skipUnless(TOOLS, "ffmpeg and rsvg-convert are needed to compose")
class OrderScreen(UiBase):
    """The order: attempts, verdicts, choosing, retouching, compare, lightbox, texts, editor. One order per scenario."""

    KEYS = ("fondos/voto", "fondos/elegir", "fondos/comparar", "fondos/retoque", "fondos/textos", "fondos/editor",
            "fondos/volver", "fondos/plantilla", "fondos/guardar", "fondos/atajos")

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

    # the editor -------------------------------------------------------------------------------------------------
    def open_editor(self, key, n=2):
        self.order(key)
        self.js("document.querySelector(\"%s details\").open = true" % self.card(n))
        self.press(self.card(n) + " .slot[data-slot=editor]", "Editar")
        self.page.wait("document.querySelector('dialog.editor[open]') && document.querySelectorAll('.ed-box').length === 3")
        self.page.wait("document.querySelector('.ed-img').complete && document.querySelector('.ed-box').style.width")

    def test_editor_moves_a_box_with_the_keyboard_and_applies(self):
        key = "fondos/editor"
        self.open_editor(key)
        self.assertEqual(self.js("document.activeElement.dataset.element"), "title1")
        for _ in range(3):
            self.page.key("ArrowRight")
        self.page.key("ArrowDown", shift=True)
        self.assertEqual(self.js("document.querySelector('.ed-item output').textContent"), "43, 50 · 500×60")
        self.press("dialog.editor", "Aplicar")
        self.page.wait("!document.querySelector('dialog.editor')")
        a = [x for x in self.data(key)["attempts"] if x["id"] == 2][0]
        self.assertEqual(a["compose"]["layout"], {"title1": {"x": 43, "y": 50, "w": 500, "h": 60}})
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


if __name__ == "__main__":
    unittest.main()
