/* Arranque de Galivelop IG: idioma, tema, textos estáticos, banda «sin servicio», sondeo de la cola, rutas y avisos.
   Con `?mock=1` en la URL carga /ui/mock/api-mock.js y sustituye el transporte (prototipo sin `gimg serve`). */

import { h, el, replace } from './dom.js';
import * as i18n from './i18n.js';
import { t } from './i18n.js';
import { onOffline, setTransport, api } from './api.js';
import * as router from './router.js';
import { to } from './router.js';
import * as poll from './queue-poll.js';
import { initQueueBar, toggleQueue, isQueueOpen } from './components/queue-bar.js';
import { initTheme } from './components/theme.js';
import { initFontScale } from './components/font-scale.js';
import { initLightbox } from './components/lightbox.js';
import { initShortcuts } from './components/shortcuts.js';
import { toast, toastError, dismissLastToast } from './components/toast.js';
import { projectsView } from './components/projects-view.js';
import { projectView } from './components/project-view.js';
import { orderView, isPanelOpen, closePanel } from './components/order-view.js';

async function boot() {
  const params = new URLSearchParams(location.search);
  if (params.get('mock') === '1') {
    const mock = await import('/ui/mock/api-mock.js');
    setTransport(mock.transport);
  }
  await i18n.load(i18n.detect());
  applyStatic();
  const langSel = el('lang');
  langSel.value = i18n.lang();
  langSel.addEventListener('change', async () => { await i18n.load(langSel.value); applyStatic(); render(router.parse()); });
  // «Saltar al contenido»: sin pasar por el router de hash (#main no es una ruta); la CSP prohíbe onclick en el HTML
  const skip = document.querySelector('a.skip');
  if (skip) skip.addEventListener('click', (e) => { e.preventDefault(); el('main').focus(); });
  initTheme(el('theme'));
  initFontScale(el('font-scale'));
  measureHeader();
  initLightbox();
  initQueueBar(el('queue-pill'), el('queue-drawer'));
  initShortcuts({ toggleQueue: toggleQueueGuarded, closeAll });

  onOffline((off) => {
    const banner = el('banner');
    banner.hidden = !off;
    replace(banner, h('span.dot', { aria: { hidden: true } }), h('b', {}, t('ui.offline.title')), h('span', {}, t('ui.offline.hint')), h('code.mono', {}, 'gimg serve'),
      h('button.btn.btn-ghost', { type: 'button', onclick: () => poll.refreshNow() }, t('ui.offline.retry')));
  });

  poll.on('finished', (e) => toast(t('ui.queue.finished', { key: e.key, id: e.attemptId ?? e.id }), { kind: 'ok', action: { label: t('ui.queue.goToAttempt'), href: to.order(e.project, e.profile, e.key, e.attemptId) } }));
  poll.on('failed', (e) => toast(`${t('ui.queue.failedToast', { key: e.key })}${e.errorText ? ': ' + e.errorText : ''}`, { kind: 'bad', action: { label: t('ui.queue.goToOrder'), href: to.order(e.project, e.profile, e.key) } }));
  poll.start();

  router.onChange(render);
  router.start();
  try { const hth = await api.health(); if (hth && hth.worker === false) toast(t('ui.offline.noWorker')); } catch { /* la banda ya lo dice */ }
}

/** `--header-h` sigue la altura real de la cabecera (fija por punto de corte, UI.1): el cajón y el retoque se colocan bajo ella. */
function measureHeader() {
  const header = document.querySelector('.app-header');
  const set = () => document.documentElement.style.setProperty('--header-h', `${header.offsetHeight}px`);
  set();
  if (window.ResizeObserver) new ResizeObserver(set).observe(header);
}

function closeAll() {
  // sin nada abierto (ni cola, ni retoque, ni diálogo, ni popover), Esc cierra el último aviso
  const anyOpen = isQueueOpen() || isPanelOpen() || document.querySelector('dialog[open], :popover-open') !== null;
  for (const d of document.querySelectorAll('dialog[open]')) d.close();
  if (isQueueOpen()) toggleQueue(false);
  if (isPanelOpen()) closePanel();
  const settings = el('settings');
  if (settings.matches(':popover-open')) settings.hidePopover();
  if (!anyOpen) dismissLastToast();
}

/** Q con el retoque abierto no abre la cola encima (los dos son diálogos modales). */
function toggleQueueGuarded(force) { if (!isPanelOpen()) toggleQueue(force); }

let current = null;
async function render(route) {
  const main = el('main');
  if (current && current.cleanup) current.cleanup();
  const host = h('div');
  main.replaceChildren(host);
  current = host;
  crumbs(route);
  try {
    if (route.name === 'projects') await projectsView(host);
    else if (route.name === 'project') await projectView(host, route);
    else if (route.name === 'order') await orderView(host, route);
    else host.append(h('div.empty', {}, h('p', {}, t('ui.nav.notFound')), h('a.btn', { href: to.projects() }, t('ui.nav.projects'))));
  } catch (e) {
    console.error(e);
    toastError(t('ui.error.generic', { message: e.message || String(e) }));
  }
  if (current !== host) return;
  document.title = `${titleOf(route)} · Galivelop IG`;
}

function titleOf(route) {
  if (route.name === 'order') return `${route.key} @ ${route.profile}`;
  if (route.name === 'project') return route.project;
  return t('ui.projects.title');
}

function crumbs(route) {
  const sep = () => h('span.sep', { aria: { hidden: true } }, '›');
  const parts = [h('a', { href: to.projects() }, t('ui.nav.projects'))];
  if (route.name === 'project' || route.name === 'order') {
    parts.push(sep(), route.name === 'project' ? h('b', { aria: { current: 'page' } }, route.project) : h('a', { href: to.project(route.project) }, route.project));
  }
  if (route.name === 'order') parts.push(sep(), h('b', { aria: { current: 'page' } }, `${route.key} @ ${route.profile}`));
  replace(el('crumbs'), parts);
}

/** Textos estáticos del index.html: data-i18n (contenido) y data-i18n-aria-label. */
function applyStatic() {
  for (const n of document.querySelectorAll('[data-i18n]')) n.textContent = t(n.dataset.i18n);
  for (const n of document.querySelectorAll('[data-i18n-aria-label]')) n.setAttribute('aria-label', t(n.dataset.i18nAriaLabel));
}

boot().catch((e) => { console.error(e); const m = el('main'); m.replaceChildren(h('p.notice.notice-bad', { role: 'alert' }, String(e.message || e))); });
