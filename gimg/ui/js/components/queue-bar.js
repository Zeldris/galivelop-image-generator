/* Barra de cola persistente: pastilla en la cabecera («1 generando · 2 en cola», progreso) y cajón desplegable con las
   entradas (filtro pendientes / terminadas / fallidas / todas), cancelar, vista previa del intento en marcha y enlace al
   intento terminado. Se alimenta de store.queue (queue-poll.js).
   F4d: cada entrada `queued` se sube, baja o pasa a primera (POST /api/queue/{id}/move) y «Vaciar cola» cancela todo lo
   que espera (POST /api/queue/clear, con confirmación; nunca toca lo que corre). El orden de la fila es el de
   `position` (si la entrada no la trae, su id), que es de donde toma el trabajador. */

import { h, mmss, replace } from '../dom.js';
import * as i18n from '../i18n.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import * as store from '../store.js';
import * as router from '../router.js';
import { to } from '../router.js';
import { toast, toastError } from './toast.js';
import { confirmAction } from './confirm.js';
import { trapFocus } from '../lib/focus-trap.js';

const FILTERS = ['pending', 'done', 'failed', 'all'];
const PENDING = ['queued', 'running'];
let filter = 'pending';
let open = false;
let hosts = null;

export function initQueueBar(pillHost, drawerHost) {
  hosts = { pillHost, drawerHost };
  trapFocus(drawerHost);
  store.subscribe('queue', render);
  render();
}

export function toggleQueue(force) {
  open = force === undefined ? !open : Boolean(force);
  render();
  if (open) { const title = hosts.drawerHost.querySelector('h2'); if (title) title.focus(); }
  else { const pill = hosts.pillHost.querySelector('button'); if (pill) pill.focus(); }
}

export function isQueueOpen() { return open; }

/** Las entradas `queued` en el orden de la fila (`position`, si no el id), de donde toma el trabajador. */
export function queuedOrder(entries) {
  const pos = (e) => (Number.isFinite(e.position) ? e.position : e.id);
  return entries.filter((e) => e.state === 'queued').sort((a, b) => pos(a) - pos(b) || a.id - b.id);
}

/** Tiempo restante estimado (ms) de una entrada, o null. */
export function remainingMs(e) {
  if (e.progress && Number.isFinite(e.progress.etaS)) return e.progress.etaS * 1000;
  if (e.state === 'running' && Number.isFinite(e.estimateMs) && e.startedAt) {
    return Math.max(0, e.estimateMs - (Date.now() - Date.parse(e.startedAt)));
  }
  if (e.state === 'queued' && Number.isFinite(e.estimateMs)) return e.estimateMs;
  return null;
}

/** <progress> de una entrada en marcha: pasos si el motor los da, si no tiempo sobre la previsión, si no indeterminada. */
export function progressOf(e) {
  const p = h('progress', { aria: { label: t('ui.queue.progressLabel') } });
  if (e.progress && e.progress.steps) { p.max = e.progress.steps; p.value = e.progress.step; }
  else if (Number.isFinite(e.estimateMs) && e.startedAt) { p.max = e.estimateMs; p.value = Math.min(e.estimateMs * 0.98, Date.now() - Date.parse(e.startedAt)); }
  return p;
}

let lastSig = null;

function render() {
  if (!hosts) return;
  const entries = store.get('queue');
  // Solo se repinta si cambia lo que se ve (cada sondeo vuelve a llamar aquí); con algo en marcha, las cuentas atrás
  // y las barras por tiempo se refrescan en cada sondeo (cubo de 3 s).
  const tick = entries.some((e) => e.state === 'running') ? Math.floor(Date.now() / 3000) : 0;
  const sig = JSON.stringify([i18n.lang(), open, filter, entries, tick, router.parse().project || null]);
  if (sig === lastSig) return;
  lastSig = sig;
  const active = document.activeElement;
  const fid = active && active.dataset && active.dataset.fid && (hosts.pillHost.contains(active) || hosts.drawerHost.contains(active)) ? active.dataset.fid : null;
  paint(entries);
  if (fid) {
    const again = document.querySelector(`[data-fid="${fid}"]`);
    if (again && again !== document.activeElement) again.focus();
  }
}

function paint(entries) {
  const c = store.queueCounts();
  const running = entries.find((e) => e.state === 'running');
  const label = c.running || c.queued
    ? [c.running ? t('ui.queue.running', { n: c.running }) : null, c.queued ? t('ui.queue.queued', { n: c.queued }) : null].filter(Boolean).join(' · ')
    : t('ui.queue.empty');
  const pill = h('button.queue-pill', {
    type: 'button', class: running ? 'is-running' : '', data: { fid: 'pill' }, aria: { expanded: open, controls: 'queue-drawer', label: `${t('ui.queue.label')}: ${label}` },
    onclick: () => toggleQueue(),
  }, h('span.dot', { aria: { hidden: true } }), h('span', {}, label), running ? progressOf(running) : null);
  replace(hosts.pillHost, pill);

  const drawer = hosts.drawerHost;
  drawer.hidden = !open;
  // diálogo modal: lo de detrás queda inerte (ni foco ni clic) mientras está abierto
  for (const sel of ['#main', '.app-header']) { const node = document.querySelector(sel); if (node) node.inert = open; }
  if (!open) return;
  const line = queuedOrder(entries);
  const queuedIds = line.map((e) => e.id);
  // lo que corre primero, y lo que espera en el orden de la fila; el resto, como llega
  const shown = entries.filter((e) => filter === 'all' || (filter === 'pending' ? PENDING.includes(e.state) : e.state === filter));
  if (filter === 'pending') shown.sort((a, b) => (a.state === 'running' ? 0 : 1) - (b.state === 'running' ? 0 : 1) || queuedIds.indexOf(a.id) - queuedIds.indexOf(b.id));
  const current = router.parse().project;
  const inProject = current ? line.filter((e) => e.project === current).length : 0;
  replace(drawer,
    h('div.row-between', {}, h('h2', { id: 'queue-title', tabindex: '-1', data: { fid: 'title' } }, t('ui.queue.label')),
      h('button.btn.btn-icon.btn-ghost', { type: 'button', data: { fid: 'close' }, aria: { label: t('ui.queue.close') }, onclick: () => toggleQueue(false) }, '✕')),
    h('div.row', { role: 'group', aria: { label: t('ui.queue.filterLabel') } }, FILTERS.map((f) =>
      h('button.btn.btn-toggle', { type: 'button', data: { fid: `filter-${f}` }, aria: { pressed: filter === f }, onclick: () => { filter = f; render(); } }, t(`ui.queue.filter.${f}`)))),
    shown.length ? h('div.stack', {}, shown.map((e) => entry(e, queuedIds.indexOf(e.id), line.length))) : h('p.empty', {}, t(filter === 'pending' ? 'ui.queue.empty' : 'ui.queue.nothing')),
    line.length ? h('div.row', { role: 'group', aria: { label: t('ui.queue.clear') } },
      h('button.btn.btn-danger', { type: 'button', data: { fid: 'clear-all' }, onclick: () => clearQueue(null, line.length) }, t('ui.queue.clear'), ` (${line.length})`),
      inProject && inProject < line.length
        ? h('button.btn', { type: 'button', data: { fid: 'clear-project' }, onclick: () => clearQueue(current, inProject) }, t('ui.queue.clearProject', { project: current }), ` (${inProject})`)
        : null) : null,
    h('p.hint', {}, t('ui.queue.idle')));
}

function entry(e, queuedPos, queuedCount) {
  const who = `${e.project} · ${e.key} @ ${e.profile}`;
  const what = [];
  if (e.state === 'running') {
    what.push(t('ui.state.running'));
    if (e.progress && e.progress.steps) what.push(t('ui.queue.step', { step: e.progress.step, steps: e.progress.steps }));
    const rem = remainingMs(e);
    what.push(rem === null ? t('ui.queue.noEstimate') : t('ui.queue.eta', { t: mmss(rem) }));
  } else if (e.state === 'queued') {
    what.push(t('ui.state.queued'), t('ui.queue.position', { n: queuedPos + 1 }));
    const rem = remainingMs(e);
    if (rem !== null) what.push(t('ui.queue.eta', { t: mmss(rem) }));
  } else {
    what.push(t(`ui.state.${e.state}`));
    if (e.startedAt && e.finishedAt) what.push(mmss(Date.parse(e.finishedAt) - Date.parse(e.startedAt)));
  }
  what.push(`${t('ui.attempt.seed')} ${e.seed}`);
  if (e.draft) what.push(t('ui.state.draft'));

  let thumb;
  if (e.state === 'running') thumb = h('img.thumb', { src: paths.preview(e.id), alt: '', onerror: (ev) => ev.target.replaceWith(h('div.thumb-empty')) });
  else if (e.state === 'done' && e.attemptId !== null && e.attemptId !== undefined) thumb = h('img.thumb', { src: paths.image(e.project, e.profile, e.key, e.attemptId), alt: '' });
  else thumb = h('div.thumb-empty');

  const actions = [];
  if (e.state === 'queued') {
    const who2 = `${e.key} @ ${e.profile}`;
    const first = queuedPos <= 0;
    const last = queuedPos >= queuedCount - 1;
    const mover = (to2, label, glyph, disabled) => h('button.btn.btn-icon', { type: 'button', disabled, title: label, data: { fid: `${to2}-${e.id}` }, aria: { label: `${label}: ${who2}` }, onclick: () => move(e, to2) }, glyph);
    actions.push(h('div.row.queue-move', { role: 'group', aria: { label: t('ui.queue.position', { n: queuedPos + 1 }) } },
      mover('up', t('ui.queue.up'), '▲', first), mover('down', t('ui.queue.down'), '▼', last), mover('top', t('ui.queue.top'), '⤒', first)));
  }
  if (PENDING.includes(e.state)) {
    actions.push(h('button.btn.btn-danger', { type: 'button', data: { fid: `cancel-${e.id}` }, onclick: () => cancel(e) }, t('ui.queue.cancel')));
  } else if (e.state === 'done' && e.attemptId !== null && e.attemptId !== undefined) {
    actions.push(h('a.btn', { href: to.order(e.project, e.profile, e.key, e.attemptId), data: { fid: `go-${e.id}` }, onclick: () => toggleQueue(false) }, t('ui.queue.goToAttempt')));
  } else if (e.state === 'failed') {
    actions.push(h('a.btn', { href: to.order(e.project, e.profile, e.key), data: { fid: `go-${e.id}` }, onclick: () => toggleQueue(false) }, t('ui.queue.goToOrder')));
  }
  const node = h('div.queue-entry', { class: `is-${e.state}`, aria: { label: `${who}: ${what.join(', ')}` } },
    thumb,
    h('div', {}, h('div.who', {}, who), h('div.what', {}, what.join(' · ')),
      e.state === 'running' ? progressOf(e) : null,
      e.state === 'failed' && e.errorText ? h('div.what.mono', {}, e.errorText) : null),
    actions.length ? h('div.queue-actions', {}, actions) : null);
  return node;
}

async function cancel(e) {
  try {
    await api.cancel(e.id);
    toast(t('ui.queue.cancelled', { id: e.id }));
    const { refreshNow } = await import('../queue-poll.js');
    refreshNow();
  } catch (err) { toastError(describeError(err, t)); }
}

/** Mueve una entrada que espera y, si su botón queda deshabilitado (ya es la primera o la última), deja el foco en el
    siguiente movimiento posible de la misma entrada. */
async function move(e, to2) {
  try {
    await api.move(e.id, to2);
    toast(t('ui.queue.moved', { id: e.id }));
    const { refreshNow } = await import('../queue-poll.js');
    await refreshNow();
    const next = [to2, 'down', 'up'].map((d) => document.querySelector(`[data-fid="${d}-${e.id}"]`)).find((b) => b && !b.disabled);
    if (next && next !== document.activeElement) next.focus();
  } catch (err) { toastError(describeError(err, t)); }
}

/** «Vaciar cola»: confirma y cancela todo lo que espera (de un proyecto, si se da). Lo que corre no se toca. */
async function clearQueue(project, n) {
  const fid = project ? 'clear-project' : 'clear-all';
  const ok = await confirmAction({
    title: t('ui.queue.clearTitle'), message: t('ui.queue.clearMessage', { n }), confirmLabel: t('ui.queue.clearConfirm'),
    opener: () => document.querySelector(`[data-fid="${fid}"]`) || document.querySelector('[data-fid="pill"]'),
  });
  if (!ok) return;
  try {
    const cancelled = await api.clearQueue(project);
    toast(t('ui.queue.cleared', { n: Array.isArray(cancelled) ? cancelled.length : n }));
    const { refreshNow } = await import('../queue-poll.js');
    await refreshNow();
  } catch (err) { toastError(describeError(err, t)); }
}
