/* Barra de cola persistente: pastilla en la cabecera («1 generando · 2 en cola», progreso) y cajón desplegable con las
   entradas (filtro pendientes / terminadas / fallidas / todas), cancelar, vista previa del intento en marcha y enlace al
   intento terminado. Se alimenta de store.queue (queue-poll.js).
   F4d: cada entrada `queued` se sube, baja o pasa a primera (POST /api/queue/{id}/move) y «Vaciar cola» cancela todo lo
   que espera (POST /api/queue/clear, con confirmación; nunca toca lo que corre). El orden de la fila es el de
   `position` (si la entrada no la trae, su id), que es de donde toma el trabajador.
   R1: «Pausar cola» / «Reanudar cola» (POST /api/queue/pause|resume): en pausa, lo que corre termina y no empieza
   nada más; la pastilla lo dice («en pausa») y el estado se lee en la cabecera `X-Queue-Paused` de GET /api/queue (queue-poll.js).
   0.8.0 (paso 5b): las entradas con el mismo `batch.id` se pintan como un grupo (`group()`): cabecera enfocable con clave,
   «2 de 4», semillas, ETA y subir / bajar / primera / cancelar tanda (POST /api/queue/batches/{id}/move|cancel), y un `details`
   con sus entradas. Intro abre o cierra, ←/→ recorren los botones de la cabecera, `[` `]` saltan de tanda. Una entrada
   `held: 'troubleshooting'` se pinta «retenida». */

import { h, mmss, replace } from '../dom.js';
import * as i18n from '../i18n.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import * as store from '../store.js';
import * as router from '../router.js';
import { to } from '../router.js';
import { toast, toastError } from './toast.js';
import { confirmAction } from './confirm.js';

const FILTERS = ['pending', 'done', 'failed', 'all'];
const PENDING = ['queued', 'running'];
let filter = 'pending';
let open = false;
let hosts = null;

export function initQueueBar(pillHost, drawerHost) {
  hosts = { pillHost, drawerHost };
  drawerHost.addEventListener('keydown', jumpBatch);
  store.subscribe('queue', render);
  store.subscribe('queuePaused', render);
  render();
}

export function toggleQueue(force) {
  open = force === undefined ? !open : Boolean(force);
  render();
  if (open) { const first = hosts.drawerHost.querySelector('button, a'); if (first) first.focus(); }
  else { const pill = hosts.pillHost.querySelector('button'); if (pill) pill.focus(); }
}

export function isQueueOpen() { return open; }

/** Las entradas `queued` en el orden de la fila (`position`, si no el id), de donde toma el trabajador. */
export function queuedOrder(entries) {
  const pos = (e) => (Number.isFinite(e.position) ? e.position : e.id);
  // solo `position`: `queue.move` de una entrada suelta puede meterla entre las de una tanda, y el trabajador sigue ese orden
  return entries.filter((e) => e.state === 'queued').sort((a, b) => pos(a) - pos(b) || a.id - b.id);
}

/** `batch.id` de una entrada de tanda, o null. */
export function batchId(e) { return e && e.batch && e.batch.id !== undefined && e.batch.id !== null ? e.batch.id : null; }

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
  const sig = JSON.stringify([i18n.lang(), open, filter, entries, tick, router.parse().project || null, store.get('queuePaused')]);
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
  const paused = store.get('queuePaused') === true;
  const queuedEntries = entries.filter((e) => e.state === 'queued');
  const inBatches = queuedEntries.filter((e) => batchId(e) !== null);
  const nBatches = new Set(inBatches.map(batchId)).size;
  const loose = queuedEntries.length - inBatches.length;
  const label = [c.running || c.queued
    ? [c.running ? t('ui.queue.running', { n: c.running }) : null,
      nBatches ? t(nBatches === 1 ? 'ui.queue.batchesOne' : 'ui.queue.batches', { n: nBatches, m: inBatches.length }) : null,
      loose ? t('ui.queue.queued', { n: loose }) : null].filter(Boolean).join(' · ')
    : t('ui.queue.empty'), paused ? t('ui.queue.pausedLabel') : null].filter(Boolean).join(' · ');
  const pill = h('button.queue-pill', {
    type: 'button', class: [running ? 'is-running' : '', paused ? 'is-paused' : ''].filter(Boolean).join(' '), data: { fid: 'pill' }, aria: { expanded: open, controls: 'queue-drawer', label: `${t('ui.queue.label')}: ${label}` },
    onclick: () => toggleQueue(),
  }, h('span.dot', { aria: { hidden: true } }), h('span', {}, label), running ? progressOf(running) : null);
  replace(hosts.pillHost, pill);

  const drawer = hosts.drawerHost;
  drawer.hidden = !open;
  if (!open) return;
  const line = queuedOrder(entries);
  const queuedIds = line.map((e) => e.id);
  // lo que corre primero, y lo que espera en el orden de la fila; el resto, como llega
  const shown = entries.filter((e) => filter === 'all' || (filter === 'pending' ? PENDING.includes(e.state) : e.state === filter));
  if (filter === 'pending') shown.sort((a, b) => (a.state === 'running' ? 0 : 1) - (b.state === 'running' ? 0 : 1) || queuedIds.indexOf(a.id) - queuedIds.indexOf(b.id));
  const current = router.parse().project;
  const inProject = current ? line.filter((e) => e.project === current).length : 0;
  replace(drawer,
    h('div.row-between', {}, h('h2', {}, t('ui.queue.label')),
      h('button.btn.btn-icon.btn-ghost', { type: 'button', data: { fid: 'close' }, aria: { label: t('ui.queue.close') }, onclick: () => toggleQueue(false) }, '✕')),
    h('div.row', { role: 'group', aria: { label: t('ui.queue.filterLabel') } }, FILTERS.map((f) =>
      h('button.btn.btn-toggle', { type: 'button', data: { fid: `filter-${f}` }, aria: { pressed: filter === f }, onclick: () => { filter = f; render(); } }, t(`ui.queue.filter.${f}`)))),
    shown.length ? h('div.stack', {}, items(entries, shown, queuedIds, line)) : h('p.empty', {}, t(filter === 'pending' ? 'ui.queue.empty' : 'ui.queue.nothing')),
    line.length ? h('div.row', { role: 'group', aria: { label: t('ui.queue.clear') } },
      h('button.btn.btn-danger', { type: 'button', data: { fid: 'clear-all' }, onclick: () => clearQueue(null, line.length) }, t('ui.queue.clear'), ` (${line.length})`),
      inProject && inProject < line.length
        ? h('button.btn', { type: 'button', data: { fid: 'clear-project' }, onclick: () => clearQueue(current, inProject) }, t('ui.queue.clearProject', { project: current }), ` (${inProject})`)
        : null) : null,
    h('div.row', {},
      h('button.btn', { type: 'button', data: { fid: 'pause' }, aria: { pressed: paused }, onclick: () => togglePause(!paused) }, t(paused ? 'ui.queue.resume' : 'ui.queue.pause'))),
    paused ? h('p.hint', {}, t('ui.queue.pausedHint')) : null,
    h('p.hint', {}, t('ui.queue.idle')));
}

/** Lo que se pinta de la lista: un grupo por tanda (en el puesto de su primera entrada mostrada) y las entradas sin tanda. */
function items(all, shown, queuedIds, line) {
  const out = [];
  const seen = new Set();
  if (filter === 'pending') {
    // el orden de la fila manda: si una entrada suelta quedó entre las de una tanda, la tanda sale en dos tramos
    const runs = [];
    for (const e of shown) {
      const b = batchId(e);
      const last = runs[runs.length - 1];
      if (b !== null && last && last.b === b) last.visible.push(e);
      else runs.push({ b, e, visible: [e], n: b === null ? 0 : runs.filter((r) => r.b === b).length });
    }
    for (const r of runs) out.push(r.b === null ? entry(r.e, queuedIds.indexOf(r.e.id), line.length) : group(r.b, all.filter((x) => batchId(x) === r.b), r.visible, queuedIds, line, r.n));
    return out;
  }
  for (const e of shown) {
    const b = batchId(e);
    if (b === null) { out.push(entry(e, queuedIds.indexOf(e.id), line.length)); continue; }
    if (seen.has(b)) continue;
    seen.add(b);
    out.push(group(b, all.filter((x) => batchId(x) === b), shown.filter((x) => batchId(x) === b), queuedIds, line));
  }
  return out;
}

const batchOpen = new Map(); // tanda -> abierta a mano (si no se tocó, abierta solo la que tiene algo en marcha)

/** Cabecera de una tanda y sus entradas. `members`: todas las de la tanda; `visible`: las que el filtro deja ver. */
function group(id, members, visible, queuedIds, line, run = 0) {
  const first = members[0];
  const who = `${first.project} · ${first.key} @ ${first.profile}`;
  const size = (first.batch && first.batch.size) || members.length;
  const done = members.filter((e) => e.state === 'done').length;
  const queued = members.filter((e) => e.state === 'queued');
  const running = members.some((e) => e.state === 'running');
  const held = queued.length > 0 && queued.every((e) => e.held === 'troubleshooting');
  const pos = queued.map((e) => queuedIds.indexOf(e.id));
  const atTop = !queued.length || Math.min(...pos) <= 0;
  const atEnd = !queued.length || Math.max(...pos) >= line.length - 1;
  const seeds = members.map((e) => e.seed).filter(Number.isFinite).sort((a, b) => a - b);
  const seedText = !seeds.length ? '' : seeds.length > 1 && seeds.every((s, i) => i === 0 || s === seeds[i - 1] + 1) ? `${seeds[0]}-${seeds[seeds.length - 1]}` : seeds.join(', ');
  const rems = members.filter((e) => PENDING.includes(e.state)).map(remainingMs);
  const eta = rems.length && rems.every((r) => r !== null) ? rems.reduce((a, b) => a + b, 0) : null;
  const what = [t('ui.queue.batchOf', { done, size }), seedText ? t('ui.queue.batchSeeds', { s: seedText }) : null,
    eta === null ? null : t('ui.queue.batchEta', { t: mmss(eta) }), held ? t('ui.queue.held') : null].filter(Boolean);

  const fid = (k) => `${k}-b${id}${run ? `r${run}` : ''}`; // un segundo tramo de la misma tanda no repite las claves
  const mover = (to2, label, glyph, disabled) => h('button.btn.btn-icon', { type: 'button', disabled, title: label, data: { fid: fid(to2) }, aria: { label: `${label}: ${who}` }, onclick: () => moveBatch(id, to2) }, glyph);
  const buttons = [];
  if (queued.length) buttons.push(h('div.row.queue-move', { role: 'group', aria: { label: t('ui.queue.batch') } },
    mover('up', t('ui.queue.batchUp'), '▲', atTop), mover('down', t('ui.queue.batchDown'), '▼', atEnd), mover('top', t('ui.queue.batchTop'), '⤒', atTop)));
  if (queued.length || running) buttons.push(h('button.btn.btn-danger', { type: 'button', data: { fid: fid('cancel') }, onclick: () => cancelBatch(id, who, queued.length + (running ? 1 : 0)) }, t('ui.queue.batchCancel')));
  if (held) buttons.push(h('a.btn', { href: to.order(first.project, first.profile, first.key), data: { fid: fid('go') }, onclick: () => toggleQueue(false) }, t('ui.queue.goToOrder')));

  const isOpen = batchOpen.has(id) ? batchOpen.get(id) : running;
  const details = h('details', { open: isOpen, ontoggle: (ev) => { if (ev.target.open === running) batchOpen.delete(id); else batchOpen.set(id, ev.target.open); } },
    h('summary', { data: { fid: fid('sum') } }, t('ui.queue.batchEntries', { n: visible.length })),
    h('div.stack', {}, visible.map((e) => entry(e, queuedIds.indexOf(e.id), line.length, true))));
  const head = h('div.queue-batch-head', { tabindex: 0, role: 'group', data: { fid: fid('head') }, aria: { label: `${t('ui.queue.batch')} ${who}: ${what.join(', ')}` },
    onkeydown: (ev) => headKey(ev, head, details) },
  h('div', {}, h('div.who', {}, `${t('ui.queue.batch')} · ${who}`), h('div.what', {}, what.join(' · '))),
  h('div.row', {}, buttons));
  return h('div.queue-batch', { class: held ? 'is-held' : '', data: { batch: id } }, head, details);
}

/** Intro abre o cierra la tanda; ←/→ recorren sus botones (y la cabecera); `[` `]` salto de tanda lo lleva el cajón. */
function headKey(ev, head, details) {
  if (ev.key === 'Enter' && ev.target === head) { ev.preventDefault(); details.open = !details.open; return; }
  if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
  const stops = [head, ...head.querySelectorAll('button:not(:disabled), a')];
  const i = stops.indexOf(document.activeElement);
  if (i < 0) return;
  ev.preventDefault();
  stops[Math.max(0, Math.min(stops.length - 1, i + (ev.key === 'ArrowRight' ? 1 : -1)))].focus();
}

/** `[` y `]` saltan a la cabecera de la tanda anterior o siguiente (desde una cabecera o una entrada del cajón). */
function jumpBatch(ev) {
  if ((ev.key !== '[' && ev.key !== ']') || ev.ctrlKey || ev.metaKey || ev.altKey) return;
  const heads = [...hosts.drawerHost.querySelectorAll('.queue-batch-head')];
  if (!heads.length) return;
  const mine = document.activeElement && document.activeElement.closest ? document.activeElement.closest('.queue-batch') : null;
  const at = mine ? heads.indexOf(mine.querySelector('.queue-batch-head')) : -1;
  const next = ev.key === ']' ? Math.min(heads.length - 1, at + 1) : Math.max(0, at < 0 ? 0 : at - 1);
  ev.preventDefault();
  heads[next].focus();
}

function entry(e, queuedPos, queuedCount, grouped = false) {
  const who = `${e.project} · ${e.key} @ ${e.profile}`;
  const what = [];
  if (e.state === 'running') {
    what.push(t('ui.state.running'));
    if (e.progress && e.progress.steps) what.push(t('ui.queue.step', { step: e.progress.step, steps: e.progress.steps }));
    const rem = remainingMs(e);
    what.push(rem === null ? t('ui.queue.noEstimate') : t('ui.queue.eta', { t: mmss(rem) }));
  } else if (e.state === 'queued') {
    what.push(t('ui.state.queued'), t('ui.queue.position', { n: queuedPos + 1 }));
    if (e.held === 'troubleshooting') what.push(t('ui.queue.held'));
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
  if (e.state === 'queued' && !grouped) {
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
    h('div.stack', {}, actions));
  return node;
}

async function moveBatch(id, to2) {
  try {
    await api.moveBatch(id, to2);
    toast(t('ui.queue.batchMoved', { id }));
    const { refreshNow } = await import('../queue-poll.js');
    await refreshNow();
    const next = [to2, 'down', 'up'].map((d) => document.querySelector(`[data-fid="${d}-b${id}"]`)).find((b) => b && !b.disabled);
    if (next && next !== document.activeElement) next.focus();
  } catch (err) { toastError(describeError(err, t)); }
}

/** «Cancelar tanda»: confirma y cancela lo que espera de la tanda y pide parar la que corre. */
async function cancelBatch(id, who, n) {
  const ok = await confirmAction({
    title: t('ui.queue.batchCancelTitle'), message: t('ui.queue.batchCancelMessage', { id, who, n }), confirmLabel: t('ui.queue.batchCancel'),
    opener: () => document.querySelector(`[data-fid="cancel-b${id}"]`) || document.querySelector('[data-fid="pill"]'),
  });
  if (!ok) return;
  try {
    await api.cancelBatch(id);
    toast(t('ui.queue.batchCancelled', { id }));
    const { refreshNow } = await import('../queue-poll.js');
    await refreshNow();
  } catch (err) { toastError(describeError(err, t)); }
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

/** «Pausar cola» / «Reanudar cola»: lo que corre termina; el foco se queda en el mismo botón. */
async function togglePause(on) {
  try {
    const { refreshNow, notePauseChange } = await import('../queue-poll.js');
    notePauseChange(); // un sondeo de la cola en vuelo desde antes del clic no pisa lo que se pide
    await api.pauseQueue(on);
    notePauseChange(); // ni uno lanzado mientras el servicio aún no había cambiado
    store.set('queuePaused', on);
    toast(t(on ? 'ui.queue.pausedToast' : 'ui.queue.resumedToast'));
    await refreshNow();
  } catch (err) { toastError(describeError(err, t)); }
}
