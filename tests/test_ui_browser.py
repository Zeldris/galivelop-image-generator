"""F4a: the web interface run for real in a headless Chrome over the DevTools protocol (tests/browser.py), against a
real `gimg serve` (in a thread) on the fake engine, temporary folders and an example project. Nothing is generated: the
fake engine writes placeholder images. Every scenario ends by asserting the page reported no exception, no console
error, no CSP violation and no failed load. Skipped when no Chrome is found (see ``GIMG_TEST_CHROME``)."""
import contextlib
import copy
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import quote

from gimg import cli, orders, paths, png, server
from tests import browser
from tests.test_brandsheet import PORTAL, SUBJECT

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


@unittest.skipUnless(browser.find_chrome(), "no Chrome/Chromium found (set GIMG_TEST_CHROME)")
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


@unittest.skipUnless(browser.find_chrome(), "no Chrome/Chromium found (set GIMG_TEST_CHROME)")
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
        compose["fields"] = ["title1", "subtitle"]  # los huecos de ELEMENTS_SVG (el ejemplo real solo lleva `lema`)
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
        order = {k: v for k, v in order.items() if v is not None}  # `prompt=None`: a brand order sends none
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
        self.shut(self.page)

    def shut(self, page):
        """Closes the tab itself (Chromium keeps it alive when only its socket closes), then the socket."""
        page.close()
        if page in self.browser.pages:
            self.browser.pages.remove(page)

    def replace_page(self, width, height):
        """Closes the current tab (not only its socket: Chromium keeps the tab alive) and opens one with that size."""
        self.shut(self.page)
        self.page = self.browser.new_page(width=width, height=height)

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
        perfiles = len(json.loads((self.root / "galivelop-images.json").read_text(encoding="utf-8"))["profiles"])
        self.page.wait("document.querySelectorAll('.piece-card').length === %d" % perfiles)  # one card per profile
        self.assertEqual(self.js("document.querySelector('nav.tabs a[aria-current=page]').textContent"), "Piezas")
        self.click("nav.tabs a[href='#/p/tarkor/marca']")
        self.page.wait("document.querySelector('.check-list .check-item')")  # sin hoja se abre en «Comprobación»
        self.assertIn("bien", self.js("document.querySelector('#tab-panel section b').textContent"))
        self.click("#sub-hoja")
        self.page.wait("document.querySelector('[data-card=no-sheet]')")
        self.assertGreaterEqual(self.js("document.querySelectorAll('.swatch').length"), 3)
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



def order_route(key, profile=PROFILE):
    return "/p/%s/o/%s/%s" % (PROJECT, profile, quote(key, safe=""))


class OrderPages(UiBase):
    """Helpers to open an order and press its buttons; `ORDER_PROFILE` is the profile of the orders."""

    ORDER_PROFILE = PROFILE

    def order(self, key):
        self.open(order_route(key, self.ORDER_PROFILE), "document.querySelectorAll('.gallery .attempt[data-kind=attempt]').length >= 2")
        self.page.wait("[...document.querySelectorAll('.gallery img')].every(i => i.complete && i.naturalWidth > 0)")

    def data(self, key):
        return self.api("GET", "/api/projects/%s/orders/%s/%s" % (PROJECT, self.ORDER_PROFILE, quote(key, safe="")))

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


@unittest.skipUnless(TOOLS, "ffmpeg and rsvg-convert are needed to compose")
class OrderScreen(OrderPages):
    """The order: attempts, verdicts, choosing, retouching, compare, lightbox, texts, editor. One order per scenario."""

    KEYS = ("fondos/voto", "fondos/elegir", "fondos/comparar", "fondos/retoque", "fondos/textos", "fondos/editor",
            "fondos/volver", "fondos/plantilla", "fondos/guardar", "fondos/atajos", "fondos/estrecho")

    @classmethod
    def prepare(cls):
        for key in cls.KEYS:
            cls.submit(key, count=2, work=False, text={"title1": "Titulo", "subtitle": "Sub"})
        run_cli("work")

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

    def test_editor_on_a_narrow_screen_shows_the_whole_image_and_no_overlap(self):
        # A una columna (≤1000 px), la escena con `overflow: hidden` era un contenedor desplazable: su fila encogía (la
        # imagen salía cortada; a 360 px, 18 px de alto) y la ayuda de debajo pisaba la lista de elementos.
        self.replace_page(768, 900)
        self.open_editor("fondos/estrecho")
        self.page.key("ArrowDown", shift=True)
        box = lambda s: self.js("(() => { const r = document.querySelector(%s).getBoundingClientRect();"
                                " return [r.top, r.bottom, r.height]; })()" % json.dumps(s))
        stage, img, main, side = box(".ed-stage"), box(".ed-img"), box(".ed-main"), box(".ed-side")
        self.assertGreater(img[2], 300)
        self.assertAlmostEqual(stage[2], img[2], delta=1, msg="la escena corta la imagen")
        self.assertAlmostEqual(stage[0], img[0], delta=1, msg="la imagen se desplazó dentro de la escena")
        last = self.js("document.querySelector('.ed-main').lastElementChild.getBoundingClientRect().bottom")
        self.assertLessEqual(last, main[1] + 1, "la ayuda se sale de su columna")
        self.assertLessEqual(main[1], side[0], "la ayuda pisa la lista de elementos")
        self.no_problems()

    # Sondeo de maquetación: la página no se desplaza a lo ancho, nada visible sale del ancho de la ventana y ningún
    # elemento en flujo pisa a su hermano siguiente. Devuelve la lista de problemas legibles.
    FIT_PROBE = r"""(() => {
      const W = innerWidth, out = [];
      const name = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + [...e.classList].map(c => '.' + c).join('');
      const shown = e => { const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
        return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && !e.closest('.sr-only'); };
      if (document.documentElement.scrollWidth > W + 1) out.push('página ' + document.documentElement.scrollWidth + ' px de ancho');
      const clipped = e => { for (let a = e.parentElement; a; a = a.parentElement) {
        const o = getComputedStyle(a).overflowX; if (o !== 'visible') return true; } return false; };
      const side = (e, n) => !n || ['absolute', 'fixed'].includes(getComputedStyle(n).position) ||
        ['absolute', 'fixed'].includes(getComputedStyle(e).position);
      const overlap = (r, q) => Math.min(r.right, q.right) - Math.max(r.left, q.left) > 2 &&
        Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top) > 2;
      for (const e of document.querySelectorAll('body *')) {   // una sola pasada por el DOM
        if (!shown(e)) continue;
        const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
        if ((r.right > W + 1 || r.left < -1) && !clipped(e)) out.push(name(e) + ' sale del ancho (' + Math.round(r.left) + '..' + Math.round(r.right) + ')');
        // un hermano siguiente en flujo no lo pisa
        const n = e.nextElementSibling;
        if (n && shown(n) && cs.display !== 'contents' && !side(e, n) && overlap(r, n.getBoundingClientRect()))
          out.push(name(e) + ' pisa a ' + name(n));
        // contenido que se sale de su caja y pisa al hermano siguiente de la caja
        const p = e.parentElement, pn = p && p.nextElementSibling;
        if (pn && shown(pn) && getComputedStyle(p).overflowY === 'visible' && !side(e, pn) && overlap(r, pn.getBoundingClientRect()))
          out.push(name(e) + ' se sale de ' + name(p) + ' y pisa a ' + name(pn));
        // cajas que recortan (hidden/clip) con contenido más alto que ellas: algo queda cortado
        if (e.clientHeight > 2 && (cs.overflowY === 'hidden' || cs.overflowY === 'clip') && e.scrollHeight > e.clientHeight + 2)
          out.push(name(e) + ' corta su contenido (' + e.scrollHeight + ' > ' + e.clientHeight + ')');
        // cajas con `overflow: auto/scroll` cuyo contenido se sale a lo ancho (salvo las pestañas, que se desplazan a propósito)
        if (['auto', 'scroll'].includes(cs.overflowX) && e.scrollWidth > e.clientWidth + 1 && !e.matches('.tabs'))
          out.push(name(e) + ' se desplaza a lo ancho (' + e.scrollWidth + ' > ' + e.clientWidth + ')');
      }
      return [...new Set(out)].slice(0, 12);
    })()"""

    def test_the_fit_probe_sees_what_sticks_out_of_an_auto_overflow_box(self):
        # (el hijo se estiliza por CSSOM: la CSP no deja `style=""` en el HTML)
        self.open("/", "document.querySelector('a.project-card')")
        self.js("""(() => { const d = document.createElement('div'); d.id = 'probe-box'; d.style.cssText = 'overflow:auto;width:100px';
            const c = document.createElement('div'); c.style.cssText = 'width:300px;height:10px';
            d.append(c); document.body.append(d); return true; })()""")
        self.assertEqual([p for p in self.js(self.FIT_PROBE) if "probe-box" in p], ["div#probe-box se desplaza a lo ancho (300 > 100)"])

    def test_main_screens_fit_at_360_768_and_1280(self):
        # Retro R2 (2026-11-13): la imagen cortada del editor solo se vio a mano; este barrido hace de red a tres anchos.
        screens = [
            ("proyectos", lambda: self.open("/", "document.querySelector('a.project-card')")),
            ("pedidos", lambda: self.open("/p/tarkor/pedidos", "document.querySelector('a.order-row')")),
            ("piezas", lambda: self.open("/p/tarkor/piezas", "document.querySelector('.piece-card')")),
            ("pedido", lambda: self.order("fondos/voto")),
            ("nuevo pedido", lambda: (self.open("/p/tarkor/piezas", "document.querySelector('.piece-card')"),
                                      self.click(".piece-card button[data-slot=new-order]"),
                                      self.page.wait("document.querySelector('dialog.new-order[open]')"))),
            ("atajos", lambda: (self.open("/", "document.querySelector('a.project-card')"), self.click("#help"),
                                self.page.wait("document.querySelector('#shortcuts[open] dt')"))),
            ("editor", lambda: self.open_editor("fondos/estrecho")),
        ]
        for width in (360, 768, 1280):
            self.replace_page(width, 800)
            for label, go in screens:
                with self.subTest(width=width, screen=label):
                    try:
                        go()
                        self.page.pump(0.2)
                        self.assertEqual(self.js(self.FIT_PROBE), [])
                    finally:   # un diálogo modal abierto inutilizaría las pantallas siguientes
                        self.js("document.querySelectorAll('dialog[open]').forEach(d => d.close())")
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


@unittest.skipUnless(TOOLS, "ffmpeg and rsvg-convert are needed to compose")
class CropScreen(OrderPages):
    """The crop editor on `social` (1280x640, no compose); `og` composes and is blocked."""

    ORDER_PROFILE = "social"
    KEYS = ("fondos/recorte", "fondos/recorte-libre", "fondos/recorte-repetir")

    @classmethod
    def prepare(cls):
        for key in cls.KEYS:
            cls.submit(key, profile="social", count=2, work=False)
        cls.submit("fondos/recorte-og", count=2, work=False)
        run_cli("work")

    def open_crop(self, key, n=2):
        self.order(key)
        self.js("document.querySelector(\"%s details\").open = true" % self.card(n))
        self.press(self.card(n), "Recortar")
        self.page.wait("document.querySelector('dialog.crop[open]') && !document.querySelector('.crop-box').hidden"
                       " && document.querySelector('.crop-box').style.width")

    def crop_box(self):
        return self.js("[...document.querySelectorAll('.crop-nums input')].map(i => Number(i.value))")

    def test_crop_moves_the_box_with_the_arrows_and_saves_a_derived_attempt(self):
        key = "fondos/recorte"
        self.open_crop(key)
        self.assertEqual(self.js("document.activeElement.className"), "crop-box")
        self.js("document.querySelector('input[name=crop-grid][value=\"2\"]').click()")
        self.page.wait("document.querySelector('[data-cell=\"1\"]')")
        self.js("document.querySelector('[data-cell=\"1\"]').click()")
        x0, y0, x1, y1 = self.crop_box()
        self.assertEqual((x0, y0), (0, 0))
        self.assertEqual(self.js("document.activeElement.className"), "crop-box")
        self.page.key("ArrowRight")  # mover, paso 10 px
        self.assertEqual(self.crop_box(), [10, 0, x1 + 10, y1])
        self.js("document.querySelector('input[name=crop-mode][value=size]').click(); document.querySelector('.crop-box').focus()")
        self.page.key("ArrowDown")  # tamaño: con la proporción bloqueada también cambia el ancho
        b = self.crop_box()
        self.assertEqual(b[1], 0)
        self.assertEqual(b[3], y1 + 10)
        self.assertEqual(self.js("document.querySelector('.crop-preview').width > 0"), True)
        self.press("dialog.crop", "Guardar como intento derivado")
        self.page.wait("!document.querySelector('dialog.crop')")
        derived = [a for a in self.data(key)["attempts"] if a.get("derivedFrom")]
        self.assertEqual(len(derived), 1)
        self.assertEqual(derived[0]["derivedFrom"]["box"], b)
        self.assertEqual(derived[0]["derivedFrom"]["attempt"], 2)
        self.page.wait("document.querySelector(\".gallery .attempt .badges\") && document.body.textContent.includes('Recorte de q2')")
        self.no_problems()

    def test_crop_is_blocked_with_its_reason_when_the_profile_composes(self):
        self.open(order_route("fondos/recorte-og", PROFILE), "document.querySelectorAll('.gallery .attempt[data-kind=attempt]').length >= 2")
        self.page.wait("[...document.querySelectorAll('.gallery img')].every(i => i.complete && i.naturalWidth > 0)")
        self.js("document.querySelector(\"%s details\").open = true" % self.card(2))
        self.press(self.card(2), "Recortar")
        self.page.wait("document.querySelector('dialog.crop[open]') && !document.querySelector('.crop-box').hidden")
        self.assertIn("Este perfil compone texto y logo", self.js("document.querySelector('dialog.crop .crop-compose:not([hidden])').textContent"))
        self.assertTrue(self.js("[...document.querySelectorAll('dialog.crop button')].find(b => b.textContent.includes('Guardar como')).disabled"))
        self.press("dialog.crop", "Llevar a otro pedido")  # sigue disponible para elegir otro perfil
        self.js("(() => { const s = document.getElementById('crop-to-profile'); s.value = 'social'; s.dispatchEvent(new Event('change', {bubbles: true})); })()")
        self.page.wait("!document.querySelector('dialog.crop .crop-compose:not([hidden])')")
        self.no_problems()

    def test_crop_blocks_a_box_outside_the_image_with_its_reason_and_frees_the_ratio(self):
        key = "fondos/recorte-libre"
        self.open_crop(key)
        _, _, x1, y1 = self.crop_box()
        self.js("""(() => { const i = document.querySelector('.crop-nums input[data-field=x1]');
            i.value = %d; i.dispatchEvent(new Event('change', {bubbles: true})); })()""" % (x1 + 500))
        self.page.wait("document.querySelector('dialog.crop [role=status]:not([hidden])')")
        self.assertTrue(self.js("[...document.querySelectorAll('dialog.crop button')].find(b => b.textContent.includes('Guardar como')).disabled"))
        self.assertIn("sale de la imagen", self.js("document.querySelector('dialog.crop .notice-warn:not([hidden])').textContent"))
        self.js("document.querySelector('input[name=crop-ratio][value=\"0\"]').click()")
        self.js("""(() => { const i = document.querySelector('.crop-nums input[data-field=x1]');
            i.value = %d; i.dispatchEvent(new Event('change', {bubbles: true}));
            const j = document.querySelector('.crop-nums input[data-field=y1]');
            j.value = %d; j.dispatchEvent(new Event('change', {bubbles: true})); })()""" % (x1 - 3, y1))
        self.page.wait("![...document.querySelectorAll('dialog.crop button')].find(b => b.textContent.includes('Guardar como')).disabled")
        self.no_problems()

    def set_field(self, name, value):
        self.js("""(() => { const i = document.querySelector('.crop-nums input[data-field=%s]'); i.focus();
            i.value = %s; i.dispatchEvent(new Event('change', {bubbles: true})); })()""" % (name, value))

    def save_disabled(self):
        return self.js("[...document.querySelectorAll('dialog.crop button')].find(b => b.textContent.includes('Guardar como')).disabled")

    def pick_destination(self, profile):
        self.press("dialog.crop", "Llevar a otro pedido")
        self.js("(() => { const s = document.getElementById('crop-to-profile'); s.value = %s; s.dispatchEvent(new Event('change', {bubbles: true})); })()"
                % json.dumps(profile))

    def test_save_waits_while_the_destination_panel_changes_the_ratio(self):
        self.open_crop("fondos/recorte-libre")
        self.assertFalse(self.save_disabled())
        self.pick_destination("square")  # 1:1: la caja sigue al destino, no al perfil del pedido
        self.assertTrue(self.save_disabled())
        self.assertIn("1024", self.js("document.getElementById('crop-output').textContent"))
        self.no_problems()

    def test_closing_the_destination_panel_goes_back_to_the_ratio_of_the_order(self):
        self.open_crop("fondos/recorte-libre")
        self.pick_destination("square")
        x0, y0, x1, y1 = self.crop_box()
        self.assertEqual(x1 - x0, y1 - y0)
        self.press("dialog.crop", "Llevar a otro pedido")  # cierra el panel
        x0, y0, x1, y1 = self.crop_box()
        self.assertEqual(x1 - x0, 2 * (y1 - y0))
        self.assertFalse(self.save_disabled())
        self.no_problems()

    def test_repeat_lists_only_the_originals_of_the_source_batch(self):
        key = "fondos/recorte-repetir"
        self.open()  # una página del mismo origen para llamar a la API antes de abrir el pedido
        res = self.api("POST", "/api/projects/%s/orders/%s/%s/attempts/2/crop" % (PROJECT, self.ORDER_PROFILE, quote(key, safe="")),
                       {"box": [0, 0, 640, 320], "lockRatio": True})
        self.assertEqual(res["attempt"]["id"], 3, res)
        self.open_crop(key, n=3)
        self.page.wait("document.querySelectorAll('#crop-repeat-pick option').length")
        self.assertEqual(self.js("[...document.querySelectorAll('#crop-repeat-pick option')].map(o => o.value)"), ["1"])
        self.no_problems()

    def test_dragging_a_corner_with_the_ratio_locked_keeps_the_ratio_exactly(self):
        self.open_crop("fondos/recorte-libre")
        self.set_field("x1", 101)
        x0, y0, x1, y1 = self.crop_box()
        self.assertEqual((x1 - x0, y1 - y0), (101, 51))
        self.js("""(() => { const img = document.querySelector('.ed-img'); const k = img.clientWidth / img.naturalWidth;
            const hd = document.querySelector('.crop-handle.h-se');
            const ev = (type, x) => hd.dispatchEvent(new PointerEvent(type, {bubbles: true, button: 0, pointerId: 7, clientX: x, clientY: 0}));
            ev('pointerdown', 0); ev('pointermove', 99 * k); ev('pointerup', 99 * k); })()""")
        x0, y0, x1, y1 = self.crop_box()
        self.assertEqual((x1 - x0, y1 - y0), (200, 100))
        self.no_problems()

    def test_a_typed_box_value_keeps_the_keyboard_focus(self):
        self.open_crop("fondos/recorte-libre")
        self.set_field("x1", 300)
        self.assertEqual(self.js("document.activeElement.dataset.field"), "x1")
        self.assertEqual(self.js("document.activeElement.value"), "300")
        self.no_problems()

    def test_everything_in_the_footer_waits_while_a_request_is_running(self):
        self.open_crop("fondos/recorte-libre")
        self.js("window.fetch = () => new Promise(() => {})")  # la petición no termina
        self.press("dialog.crop", "Guardar como intento derivado")
        self.page.wait("document.getElementById('crop-to-profile').disabled")
        self.assertTrue(self.js("document.getElementById('crop-to-key').disabled"))
        self.assertTrue(self.js("document.getElementById('crop-step').disabled"))

    def test_the_handles_have_room_inside_the_stage(self):
        self.open_crop("fondos/recorte-libre")
        self.assertTrue(self.js("""(() => { const s = document.querySelector('.crop-stage').getBoundingClientRect();
            const hd = document.querySelector('.crop-handle.h-nw').getBoundingClientRect();
            return hd.left >= s.left && hd.top >= s.top; })()"""))
        self.no_problems()


class NewOrderScreen(UiBase):
    @classmethod
    def prepare(cls):
        cls.submit("fondos/previo", count=1, work=True)

    def test_create_an_order_from_the_panel(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('.order-row')")
        self.click("button[data-slot=new-order]")
        self.page.wait("document.querySelector('dialog.new-order[open]') && document.getElementById('no-copy')")
        self.assertTrue(self.js("document.getElementById('no-mode-brand').disabled"))  # no sheet: brand is off and free is the default
        self.assertTrue(self.js("document.getElementById('no-mode-free').checked"))
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


    def test_pause_and_resume(self):
        """R1, leve: the drawer pauses and resumes the queue; the pill says so, also after a poll."""
        self.addCleanup(run_cli, "queue", "resume")  # the mark lives in the shared data folder
        self.open("/", "document.querySelector('.queue-pill')")
        self.click(".queue-pill")
        self.page.wait("document.querySelector('[data-fid=pause]')")
        self.assertEqual(self.js("document.querySelector('[data-fid=pause]').getAttribute('aria-pressed')"), "false")
        self.click("[data-fid=pause]")
        self.page.wait("document.querySelector('.queue-pill.is-paused')")
        self.assertIn("en pausa", self.js("document.querySelector('.queue-pill').textContent"))
        self.assertIs(self.api("GET", "/api/health")["paused"], True)
        self.page.wait("document.querySelector('[data-fid=pause]').getAttribute('aria-pressed') === 'true'")
        self.click("[data-fid=pause]")
        self.page.wait("!document.querySelector('.queue-pill.is-paused')")
        self.assertIs(self.api("GET", "/api/health")["paused"], False)
        run_cli("queue", "pause")  # paused from the CLI: the next poll shows it
        self.page.wait("document.querySelector('.queue-pill.is-paused')", timeout=10)
        self.no_problems()

    def test_a_queue_answer_from_before_the_click_does_not_undo_the_pause(self):
        """A GET /api/queue launched before «Pausar cola» and answered after it must not put the old pause back."""
        self.addCleanup(run_cli, "queue", "resume")
        self.open("/", "document.querySelector('.queue-pill')")
        self.assertTrue(self.js("""import('/ui/js/api.js').then(m => { window.__api = m.api; window.__real = m.api.queueState;
            window.__pending = []; m.api.queueState = () => new Promise(res => window.__pending.push(res)); return true; })"""))
        # refreshNow() asks for the queue synchronously, so the resolver pushed during that call is the old answer;
        # any other pending one comes from the poll timer and is not the one to hold back
        self.assertTrue(self.js("""import('/ui/js/queue-poll.js').then(m => { const n = window.__pending.length; window.__poll = m.refreshNow();
            window.__old = window.__pending[n]; return window.__pending.length === n + 1 && typeof window.__old === 'function'; })"""))
        self.assertTrue(self.js("typeof window.__old === 'function'"))  # the old answer is held back: paused false
        self.click(".queue-pill")
        self.click("[data-fid=pause]")
        self.page.wait("document.querySelector('.queue-pill.is-paused')")
        self.js("window.__pending.filter(res => res !== window.__old).forEach(res => res({entries: [], paused: true})); window.__old({entries: [], paused: false})")  # arrives after the click
        self.assertTrue(self.js("window.__poll.then(() => true)"))  # the first refresh is done, with the stale answer last
        self.js("window.__api.queueState = window.__real; true")
        self.page.pump(0.3)
        self.assertTrue(self.js("!!document.querySelector('.queue-pill.is-paused')"))
        self.assertIs(self.api("GET", "/api/health")["paused"], True)
        self.no_problems()

    def test_a_queue_answer_without_the_header_keeps_the_last_known_pause(self):
        self.addCleanup(run_cli, "queue", "resume")
        self.open("/", "document.querySelector('.queue-pill')")
        run_cli("queue", "pause")
        self.page.wait("document.querySelector('.queue-pill.is-paused')", timeout=10)
        self.assertTrue(self.js("""import('/ui/js/api.js').then(m => { window.__api = m.api; window.__real = m.api.queueState;
            m.api.queueState = async () => ({entries: [], paused: null}); return true; })"""))
        self.assertTrue(self.js("import('/ui/js/queue-poll.js').then(m => m.refreshNow()).then(() => true)"))  # termina con `paused: null`
        self.js("window.__api.queueState = window.__real; true")
        self.page.pump(0.3)
        self.assertTrue(self.js("!!document.querySelector('.queue-pill.is-paused')"))
        self.no_problems()


class BrandShop(UiBase):
    """«Sistema de logo» in the Marca tab: steps stay disabled with their reason until the piece exists, and the origin
    can come from the URL (`?src=profile|key|attempt`). The steps that need the tools (matte on a real flat background,
    rsvg) are covered by tests/test_brand.py and the API tests; no step is run here. This class is also where the browser
    tests of the workshop form live."""

    @classmethod
    def prepare(cls):
        cls.submit("fondos/marca", count=2)

    def disabled(self, text):
        return self.js("""[...document.querySelectorAll('#brand-shop .shop-action')].filter(a => a.textContent.includes(%s))
            .every(a => a.querySelector('button').disabled)""" % json.dumps(text))

    def test_steps_wait_for_their_piece_and_say_why(self):
        self.open("/p/tarkor/marca?s=taller", "document.querySelector('#brand-shop .shop-step')")
        self.assertEqual(self.js("document.querySelectorAll('#brand-shop .shop-step').length"), 7)
        self.assertTrue(self.js("document.getElementById('shop-name').value.toLowerCase().includes('tarkor')"))
        for label in ("Quitar fondo", "Pasar a SVG en color", "Lockup horizontal", "Guardar sistema"):
            self.assertTrue(self.disabled(label), label)
        self.assertIn("intento de origen", self.js("document.querySelector('#brand-shop .shop-why').textContent"))
        self.no_problems()

    def test_the_source_comes_from_the_url_and_enables_the_matte(self):
        src = quote("%s|%s|1" % (PROFILE, "fondos/marca"), safe="")
        self.open("/p/tarkor/marca?src=" + src, "document.querySelector('#brand-shop input[name=shop-attempt]:checked')")
        self.page.wait("![...document.querySelectorAll('#brand-shop .shop-action button')].find(b => b.textContent === 'Quitar fondo').disabled")
        self.assertTrue(self.disabled("Pasar a SVG en color"))  # still needs the matte
        self.no_problems()

    def test_the_wordmark_spacing_is_sent_only_when_the_field_has_a_value(self):
        self.open("/p/tarkor/marca?s=taller", "document.querySelector('#shop-wspacing')")
        self.js("""import('/ui/js/api.js').then(m => { window.__api = m.api; window.__real = m.api.brandWordmark; window.__bodies = [];
            m.api.brandWordmark = (project, body) => { window.__bodies.push(body); return Promise.resolve({}); }; return true; })""")
        self.addCleanup(lambda: self.js("window.__api.brandWordmark = window.__real; true"))
        self.assertEqual(self.js("document.getElementById('shop-wspacing').value"), "")
        self.js("""const f = document.getElementById('shop-wfont'); f.value = 'Inter'; f.dispatchEvent(new Event('input', {bubbles: true})); true""")
        go = """[...document.querySelectorAll('#brand-shop .shop-action button')].find(b => /wordmark/i.test(b.textContent))"""
        self.page.wait("!(%s).disabled" % go)
        self.js("(%s).click(); true" % go)
        self.page.wait("window.__bodies.length === 1")
        self.assertFalse(self.js("'spacing' in window.__bodies[0]"))
        self.js("const s = document.getElementById('shop-wspacing'); s.value = '0.05'; s.dispatchEvent(new Event('input', {bubbles: true})); true")
        self.page.wait("!(%s).disabled" % go)
        self.js("(%s).click(); true" % go)
        self.page.wait("window.__bodies.length === 2")
        self.assertEqual(self.js("window.__bodies[1].spacing"), 0.05)
        self.no_problems()

    def seed_shop(self, slug):
        """A workshop of another brand on disk, with its matte piece; removed when the test ends."""
        shop = paths.project_data_dir(PROJECT) / "brand" / slug
        shop.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, shop, ignore_errors=True)
        (shop / ("%s-emblema-alpha.png" % slug)).write_bytes(png.rgba_bytes(2, 2, bytes([20, 90, 40, 255]) * 4))

    def open_with_shops(self):
        self.open("/p/tarkor/marca?s=taller", "document.querySelector('#brand-shop .btn-toggle')")

    def test_a_name_without_workshop_does_not_adopt_another_brand(self):
        self.seed_shop("portal")
        self.open_with_shops()
        self.assertTrue(self.js("document.getElementById('shop-name').value.toLowerCase().includes('tarkor')"))
        self.assertEqual(self.js("document.querySelectorAll('#brand-shop .shop-img').length"), 0)  # no piece of `portal`
        self.assertTrue(self.disabled("Pasar a SVG en color"))
        self.assertEqual(self.js("document.querySelector('#brand-shop .btn-toggle').getAttribute('aria-pressed')"), "false")
        self.no_problems()

    def test_picking_a_workshop_syncs_the_wordmark_text(self):
        self.seed_shop("portal")
        self.open_with_shops()
        self.assertEqual(self.js("document.getElementById('shop-wtext').value"), self.js("document.getElementById('shop-name').value.toUpperCase()"))
        self.click("#brand-shop .btn-toggle")
        self.page.wait("document.getElementById('shop-name').value === 'portal'")
        self.assertEqual(self.js("document.getElementById('shop-wtext').value"), "PORTAL")
        self.assertEqual(self.js("document.querySelectorAll('#brand-shop .shop-img').length > 0"), True)  # its piece is shown
        self.no_problems()

    def test_picking_a_workshop_keeps_a_text_typed_for_that_name(self):
        self.seed_shop("portal")
        self.open_with_shops()
        self.js("""(() => { const n = document.getElementById('shop-name'); n.value = 'portal'; n.dispatchEvent(new Event('input'));
            const w = document.getElementById('shop-wtext'); w.value = 'EL PORTAL'; w.dispatchEvent(new Event('input')); })()""")
        self.click("#brand-shop .btn-toggle")
        self.page.wait("document.querySelector('#brand-shop .btn-toggle').getAttribute('aria-pressed') === 'true'")
        self.assertEqual(self.js("document.getElementById('shop-wtext').value"), "EL PORTAL")
        self.no_problems()

    def test_a_project_without_brand_dir_cannot_save_there(self):
        self.open("/p/tarkor/marca?s=taller", "document.getElementById('shop-dest')")
        has_dir = self.js("!document.querySelector('#shop-dest option[value=project]').disabled")
        cfg = json.loads((self.root / "galivelop-images.json").read_text(encoding="utf-8"))
        self.assertEqual(has_dir, bool((cfg.get("brand") or {}).get("dir")))

    def test_the_attempt_card_links_to_the_brand_tab(self):
        self.open(order_route("fondos/marca"), "document.querySelector('.gallery .attempt')")
        href = self.js("document.querySelector('.gallery .attempt details a[href*=\"/marca?src=\"]').getAttribute('href')")
        self.assertTrue(href.startswith("#/p/tarkor/marca?src="), href)


def add_brand_sheet(root):
    """The portal sheet (cover → og, icon → social) as the project's brand sheet."""
    sheet = copy.deepcopy(PORTAL)
    sheet["pieceTypes"]["cover"]["profile"] = PROFILE
    sheet["pieceTypes"]["icon"]["profile"] = "social"
    (root / "marca.json").write_text(json.dumps(sheet), encoding="utf-8")
    path = root / "galivelop-images.json"
    cfg = json.loads(path.read_text())
    cfg.setdefault("brand", {})["sheet"] = "marca.json"
    path.write_text(json.dumps(cfg))


class BrandSheetScreen(UiBase):
    """0.7.0 §2.10: the Marca tab with a brand sheet: subtabs with ←/→, the palette by roles, «Probar un sujeto»."""

    @classmethod
    def customize_project(cls):
        super().customize_project()
        add_brand_sheet(cls.root)

    def selected(self):
        return self.js("document.querySelector('[role=tab][aria-selected=true]').dataset.sub")

    def test_the_subtabs_move_with_the_arrows_and_the_sheet_shows_its_palette(self):
        self.open("/p/tarkor/marca", "document.querySelector('[data-role=paper]')")
        self.assertEqual(self.selected(), "hoja")  # with a sheet it opens there
        self.assertEqual(self.js("document.querySelector('[data-role=paper] code').textContent"), "#fbfcfd")
        self.assertEqual(self.js("document.querySelectorAll('.role-row').length"), 4)
        self.assertEqual(self.js("document.querySelector('[data-sheet=chain]').textContent"), "tarkor")
        self.assertEqual(self.js("document.querySelectorAll('[data-card=pieces] tbody tr').length"), 2)
        self.assertEqual(self.js("document.querySelectorAll('[data-card=pieces] [data-slot=new-order]').length"), 2)
        self.js("document.getElementById('sub-hoja').focus(); true")
        for expected in ("probar", "check", "taller", "hoja"):
            self.page.key("ArrowRight")
            self.page.wait("document.querySelector('[role=tab][aria-selected=true]').dataset.sub === %s" % json.dumps(expected))
            self.assertIn("s=" + expected, self.js("location.hash"))
            self.assertEqual(self.js("document.activeElement.dataset.sub"), expected)
        self.page.key("ArrowLeft")
        self.page.wait("document.querySelector('[role=tab][aria-selected=true]').dataset.sub === 'taller'")
        self.assertTrue(self.js("document.querySelector('#subpanel-hoja').hidden"))
        self.assertTrue(self.js("document.querySelector('#brand-shop') !== null"))
        self.no_problems()

    def test_the_check_subtab_lists_the_sheet_rows(self):
        self.open("/p/tarkor/marca?s=check", "document.querySelector('.check-item')")
        self.assertEqual(self.selected(), "check")
        self.page.wait("[...document.querySelectorAll('.check-item code')].some(c => c.textContent === 'sheet.valid')")
        self.no_problems()

    def test_pieces_come_by_piece_type_with_their_profile_inside(self):
        self.open("/p/tarkor/piezas", "document.querySelector('.piece-type .piece-card')")
        self.assertEqual(self.js("document.querySelectorAll('.piece-type').length"), 2)
        self.assertEqual(self.js("document.querySelector('.piece-type[data-piece=cover] .piece-card').dataset.profile"), PROFILE)
        self.no_problems()

    def test_probar_builds_a_prompt_and_checks_a_free_one(self):
        self.open("/p/tarkor/marca?s=probar", "document.getElementById('bp-subject')")
        self.js("(() => { const s = document.getElementById('bp-subject'); s.value = %s; s.dispatchEvent(new Event('input')); })()" % json.dumps(SUBJECT))
        self.js("document.getElementById('bp-piece').value = 'cover'; true")
        self.click("[data-card=prompt] .btn-primary")
        self.page.wait("document.querySelector('[data-slot=prompt]')")
        self.assertTrue(self.js("document.querySelector('[data-slot=prompt]').textContent.startsWith(%s)" % json.dumps(SUBJECT[:40])))
        self.assertEqual(self.js("[...document.querySelectorAll('[data-list=segments] li')].map(l => l.dataset.role).join()"),
                         "subject,register,closing,palette")
        self.assertGreaterEqual(self.js("document.querySelectorAll('[data-out=prompt] [data-check]').length"), 5)
        self.assertEqual(self.js("document.querySelector('[data-slot=defaults] code').textContent"), PROFILE)
        self.assertEqual(self.api("GET", "/api/queue"), [])  # nothing was queued
        self.js("(() => { const s = document.getElementById('bl-prompt'); s.value = 'a red fox'; s.dispatchEvent(new Event('input')); })()")
        self.click("[data-card=lint] .btn")
        self.page.wait("document.querySelector('[data-out=lint] [data-check=words]')")
        self.assertEqual(self.js("document.querySelector('[data-out=lint] [data-check=words]').dataset.status"), "warn")
        self.assertIn("palabras", self.js("document.querySelector('[data-out=lint] [data-check=words]').textContent"))
        self.no_problems()

    def test_a_brand_order_sends_the_subject_and_never_the_prompt(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('button[data-slot=new-order]')")
        self.click("button[data-slot=new-order]")
        self.page.wait("document.querySelector('dialog.new-order[open]') && document.getElementById('no-subject')")
        self.assertFalse(self.js("document.getElementById('no-subject').closest('[data-box=brand]').hidden"))
        self.assertTrue(self.js("document.getElementById('no-prompt').closest('[data-box=free]').hidden"))
        self.assertTrue(self.js("document.querySelector('dialog.new-order button[type=submit]').disabled"))  # no subject yet
        self.js("(() => { const s = document.getElementById('no-subject'); s.value = %s; s.dispatchEvent(new Event('input')); })()" % json.dumps(SUBJECT))
        self.page.wait("document.querySelector('dialog.new-order [data-out=prompt] [data-slot=prompt]')")
        self.page.wait("!document.querySelector('dialog.new-order button[type=submit]').disabled || document.querySelector('dialog.new-order [data-slot=why] .notice-bad')")
        self.assertNotEqual(self.js("document.getElementById('no-key').value"), "")  # a key is proposed: <piece>/<slug>
        self.no_problems()


class BrandBatches(UiBase):
    """0.8.0 paso 5b: tandas de marca en la cola del cajón (agrupadas por `batch.id`), cancelar una tanda entera."""

    @classmethod
    def customize_project(cls):
        super().customize_project()
        add_brand_sheet(cls.root)

    @classmethod
    def brand(cls, key, count=3, seed=311):
        cls.submit(key, work=False, count=count, seed=seed, mode="brand", piece="cover", subject=SUBJECT, prompt=None)

    @classmethod
    def prepare(cls):
        for key in ("portada/a", "portada/b", "portada/c"):
            cls.brand(key)
        cls.submit("fondos/suelta", count=1, work=False)

    def queued(self, key):
        return [e for e in self.api("GET", "/api/queue") if e["key"] == key]

    def test_entries_of_a_batch_are_one_group_with_its_header_and_the_pill_counts_batches(self):
        self.open("/", "document.querySelector('.queue-pill')")
        self.page.wait("document.querySelector('.queue-pill').textContent.includes('tandas en cola (9 imágenes)')")
        self.assertIn("1 en cola", self.js("document.querySelector('.queue-pill').textContent"))  # the loose entry
        self.click(".queue-pill")
        self.page.wait("document.querySelectorAll('#queue-drawer .queue-batch').length >= 3")
        batch = self.queued("portada/a")[0]["batch"]
        head = "#queue-drawer .queue-batch[data-batch='%d'] .queue-batch-head" % batch["id"]
        text = self.js("document.querySelector(%s).textContent" % json.dumps(head))
        for part in ("portada/a @ og", "0 de 3", "semillas 311-313"):
            self.assertIn(part, text)
        opened = "document.querySelector('#queue-drawer .queue-batch[data-batch=\"%d\"] details').open" % batch["id"]
        self.assertFalse(self.js(opened))
        self.js("document.querySelector(%s).focus(); true" % json.dumps(head))
        self.page.key("Enter")
        self.page.wait(opened)
        self.assertEqual(self.js("document.querySelectorAll('#queue-drawer .queue-batch[data-batch=\"%d\"] details .queue-entry').length" % batch["id"]), 3)
        self.page.key("ArrowRight")  # head -> first button
        self.assertEqual(self.js("document.activeElement.tagName"), "BUTTON")
        self.js("document.querySelector(%s).focus(); true" % json.dumps(head))
        self.page.key("]")
        self.assertTrue(self.js("document.activeElement.classList.contains('queue-batch-head')"))
        self.assertNotEqual(self.js("document.activeElement.parentElement.dataset.batch"), str(batch["id"]))
        self.no_problems()

    def test_moving_a_batch_moves_all_its_entries_together_and_cancelling_asks_first(self):
        self.open("/", "document.querySelector('.queue-pill')")
        self.click(".queue-pill")
        b = self.queued("portada/c")[0]["batch"]["id"]
        self.page.wait("document.querySelector('[data-fid=\"top-b%d\"]')" % b)
        self.click("[data-fid='top-b%d']" % b)
        self.page.wait("document.querySelector('[data-fid=\"top-b%d\"]').disabled" % b)
        line = [e for e in self.api("GET", "/api/queue") if e["state"] == "queued"]
        line.sort(key=lambda e: (e.get("position", e["id"]), e["id"]))
        self.assertEqual([e["key"] for e in line[:3]], ["portada/c"] * 3)
        # cancel: the dialog first; refusing leaves everything queued
        self.click("[data-fid='cancel-b%d']" % b)
        self.page.wait("document.querySelector('dialog.confirm[open]')")
        self.assertIn("tanda %d" % b, self.js("document.querySelector('dialog.confirm').textContent"))
        self.js("[...document.querySelectorAll('dialog.confirm button')].find(x => x.textContent === 'Cancelar').click(); true")
        self.page.wait("!document.querySelector('dialog.confirm')")
        self.assertEqual({e["state"] for e in self.queued("portada/c")}, {"queued"})
        self.click("[data-fid='cancel-b%d']" % b)
        self.page.wait("document.querySelector('dialog.confirm[open]')")
        self.js("document.querySelector('dialog.confirm .btn-danger').click(); true")
        self.page.wait("!document.querySelector('[data-fid=\"cancel-b%d\"]')" % b)
        self.assertEqual({e["state"] for e in self.queued("portada/c")}, {"cancelled"})
        self.no_problems()


@unittest.skipUnless(TOOLS, "ffmpeg and rsvg-convert are needed to compose")
class BrandGallery(OrderPages):
    """0.8.0 paso 5b: la galería por tandas, el distintivo Marca/Libre, el marcador de fallos y el pedido bloqueado."""

    KEYS = {"portada/g1": 1, "portada/g2": 2, "portada/g3": 3}  # clave -> tandas falladas a mano

    @classmethod
    def customize_project(cls):
        super().customize_project()
        add_brand_sheet(cls.root)

    @classmethod
    def prepare(cls):
        for key, failed in cls.KEYS.items():
            cls.submit(key, count=2, seed=500, mode="brand", piece="cover", subject=SUBJECT, prompt=None)
            for n in range(max(2, failed) - 1):  # the order's own batch plus these, newest last
                run_cli("attempt", "new", PROJECT, key, PROFILE, "--count", "2", "--seed", str(600 + 10 * n))
                run_cli("work")
            for rec in orders.get(PROJECT, key, PROFILE)["batches"][:failed]:
                run_cli("order", "fail", PROJECT, key, PROFILE, str(rec["id"]), "--reason", "horizon")

    def test_the_gallery_has_one_section_per_batch_newest_first_and_the_header_says_mode_and_failures(self):
        self.open(order_route("portada/g1"), "document.querySelectorAll('.gallery .batch-head').length >= 2")
        heads = self.js("[...document.querySelectorAll('.gallery .batch-head h3')].map(h => h.textContent)")
        self.assertEqual(len(heads), 2)
        self.assertTrue(heads[0].startswith("Tanda 2 · "), heads)
        self.assertTrue(heads[1].startswith("Tanda 1 · "), heads)
        self.assertIn("sujeto: «A wide sea chart", heads[1])
        self.assertIn("2 intentos", heads[1])
        self.assertEqual(self.js("document.querySelector('.order-status [data-mode]').dataset.mode"), "brand")
        self.assertEqual(self.js("document.querySelector('.order-status [data-mode]').textContent"), "Marca")
        self.assertIn("Fallos 1 de 3", self.js("document.querySelector('.fail-marker').textContent"))
        self.assertIn("■□□", self.js("document.querySelector('.fail-marker').textContent"))
        self.assertIsNone(self.js("document.querySelector('[data-slot=fail-notice]')"))
        # the first batch is the failed one: its header says so, with the sheet's label
        self.assertIn("FALLO: Horizonte", self.js("document.querySelector('.gallery .batch-head[data-batch] [data-slot=batch-failed]').textContent"))
        # the cards come after their header, newest section first
        order = self.js("[...document.querySelectorAll('.gallery > *')].map(n => n.classList.contains('batch-head') ? 'H' : 'A').join('')")
        self.assertEqual(order, "HAAHAA")
        self.assertEqual(self.js("document.querySelector('.gallery .attempt [data-mode]').textContent"), "Marca")
        self.no_problems()

    def test_the_second_failure_warns_with_the_reasons(self):
        self.open(order_route("portada/g2"), "document.querySelector('[data-slot=fail-notice]')")
        text = self.js("document.querySelector('[data-slot=fail-notice]').textContent")
        self.assertIn("Un fallo más y toca rediseñar.", text)
        self.assertIn("Motivos hasta ahora: Horizonte ×2", text)
        self.assertIn("Fallos 2 de 3", self.js("document.querySelector('.fail-marker').textContent"))
        self.no_problems()

    def test_a_blocked_order_cannot_queue_and_says_why(self):
        self.open(order_route("portada/g3"), "document.querySelector('.order-status [data-slot=blocked]')")
        reason = self.js("document.querySelector('[data-slot=troubleshoot]').textContent")
        self.assertIn("3 fallos de 3", reason)
        self.assertTrue(self.js("document.querySelector('.order-panel .panel-actions .btn-primary').disabled"))
        self.assertIn("3 fallos de 3", self.js("document.querySelector('.order-panel .panel-actions .btn-primary').title"))
        self.assertTrue(self.js("[...document.querySelectorAll('.gallery .attempt details .btn')].filter(b => /Recrear|Variar/.test(b.textContent)).every(b => b.disabled)"))
        self.page.key("g")
        self.page.pump(0.5)
        self.assertEqual([e for e in self.api("GET", "/api/queue") if e["key"] == "portada/g3" and e["state"] == "queued"], [])
        self.no_problems()

    def test_the_order_list_has_the_mode_and_failures_columns(self):
        self.open("/p/tarkor/pedidos", "document.querySelector('.order-row [data-col=mode]')")
        self.page.wait("document.querySelector('.order-row [data-col=failures]')")
        rows = self.js("[...document.querySelectorAll('.order-row')].filter(r => r.textContent.includes('portada/g2')).map(r => r.querySelector('[data-col=failures]').textContent)")
        self.assertEqual(len(rows), 1)
        self.assertIn("Fallos 2 de 3", rows[0])
        self.assertEqual(self.js("document.querySelector('.order-row [data-col=mode]').textContent"), "Marca")
        self.no_problems()


if __name__ == "__main__":
    unittest.main()
