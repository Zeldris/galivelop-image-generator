/* Pantalla del pedido (el corazón de F4a, docs/interfaz/propuesta.md): galería de intentos con estados, veredicto,
   elegir/deshacer, comparar, panel de retoque, textos compuestos, chip de medida, vista previa de lo que se genera.
   Carga GET project (config del perfil y marca) + GET order; se refresca cuando la cola cambia (queue-poll) sin perder
   el foco. Los atajos de la galería (←/→/↑/↓, Intro, S, N, E, C, F, G, R) viven aquí. */

import { h, el, closest } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError, ApiError } from '../api.js';
import { to } from '../router.js';
import * as store from '../store.js';
import * as poll from '../queue-poll.js';
import { attemptCard, queueCard, stateOf } from './attempt-card.js';
import { compareView } from './compare-view.js';
import { retouchPanel } from './retouch-panel.js';
import { textPanel } from './text-panel.js';
import { invalidateMeasure } from './measure-chip.js';
import { isTyping } from './shortcuts.js';
import { toast, toastError, toastOk } from './toast.js';

const PENDING = ['queued', 'running'];

export async function orderView(host, route) {
  const { project, profile, key } = route;
  host.append(h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
  let info;
  let order;
  try {
    [info, order] = await Promise.all([api.project(project), api.order(project, profile, key)]);
  } catch (e) {
    host.replaceChildren(h('h1', {}, key), h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)),
      h('p', {}, h('a.btn', { href: to.project(project) }, '← ', t('ui.order.backToProject'))));
    return;
  }
  const cfg = info.config || {};
  const profileCfg = (cfg.profiles || {})[profile] || {};
  const brand = cfg.brand || {};
  const compose = profileCfg.compose || {};
  const ctx = {
    project, profile, key, order, profileCfg, brand,
    measure: { zone: compose.zone, textColor: compose.textColor || brand.textColor, paletteMin: brand.paletteMin },
    showRaw: store.get('showRaw'), previewText: null, compare: [], queuedIds: [], estimateMs: estimateFor(profile),
    actions: {},
  };

  const galleryBar = h('div.gallery-bar', { role: 'toolbar', aria: { label: t('ui.order.galleryTools') } });
  const gallery = h('div.gallery', { role: 'list', aria: { label: t('ui.order.gallery'), live: 'polite' } });
  const compareHost = h('div');
  const deliveredHost = h('div');
  const panel = h('aside.order-panel', { aria: { label: t('ui.order.panel') } });
  const title = h('div.page-head', {}, h('h1', {}, key), h('span.chip', {}, profile, profileCfg.width ? ` · ${profileCfg.width}×${profileCfg.height}` : ''),
    h('a.btn.btn-ghost', { href: to.project(project) }, '← ', t('ui.order.backToProject')));
  host.replaceChildren(title, h('div.order-layout', {}, h('div', {}, deliveredHost, compareHost, galleryBar, gallery), panel));

  let retouch;
  let texts;
  const reload = async () => {
    try { ctx.order = await api.order(project, profile, key); } catch (e) { toastError(describeError(e, t)); return; }
    paint();
  };
  const guard = (fn) => async (...args) => { try { await fn(...args); } catch (e) { toastError(describeError(e, t)); } };

  Object.assign(ctx.actions, {
    mark: guard(async (a, st) => { await api.mark(project, profile, key, a.id, st); await reload(); }),
    note: guard(async (a, text) => { await api.note(project, profile, key, a.id, text); a.note = text; }),
    choose: guard(async (a) => {
      try {
        await api.choose(project, profile, key, a.id);
        toastOk(t('ui.order.chosenToast', { id: a.id }));
      } catch (e) {
        if (e instanceof ApiError && e.code && e.code.startsWith('compose.')) toastError(`${describeError(e, t)} — ${t('ui.order.composeFailedHint')}`);
        else throw e;
      }
      invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`);
      await reload();
    }),
    undo: guard(async () => { const r = await api.undo(project, profile, key); toast(t('ui.order.undone', { id: r && r.new !== null && r.new !== undefined ? `q${r.new}` : '—' })); await reload(); }),
    compare: (a) => {
      const i = ctx.compare.indexOf(a.id);
      if (i >= 0) ctx.compare.splice(i, 1); else { ctx.compare.push(a.id); if (ctx.compare.length > 2) ctx.compare.shift(); }
      paint();
    },
    recreate: (a) => retouch.load(a),
    vary: (a) => retouch.vary(a),
    copyParams: (a) => copy(JSON.stringify({ seed: a.seed, prompt: a.prompt, ...(a.params || {}) }, null, 2), t('ui.attempt.copied')),
    copyError: (e) => copy(e.errorText || JSON.stringify(e.error), t('ui.attempt.copied')),
    retry: guard(async (e) => { await submit({ count: 1, seed: e.seed, draft: Boolean(e.draft), ...pick(e.params, ['steps', 'cfg', 'sampler']) }); }),
    cancel: guard(async (e) => { await api.cancel(e.id); toast(t('ui.queue.cancelled', { id: e.id })); await poll.refreshNow(); }),
    recompose: guard(async (a) => { await api.compose(project, profile, key, a.id, {}); invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`); toastOk(t('ui.text.recomposed', { id: a.id })); await reload(); }),
  });

  async function submit(spec) {
    const res = await api.newAttempts(project, profile, key, spec);
    const n = (res && res.entries && res.entries.length) || spec.count || 1;
    toastOk(t('ui.retouch.queued', { n, t: res && Number.isFinite(res.estimateMs) ? ` · ~${Math.round(res.estimateMs / 1000)} s` : '' }));
    if (res && Number.isFinite(res.estimateMs)) ctx.estimateMs = res.estimateMs / Math.max(1, n);
    await poll.refreshNow();
  }

  function paint() {
    const order = ctx.order;
    const focused = document.activeElement && closest(document.activeElement, '[data-kind]');
    const focusKey = focused ? `${focused.dataset.kind}:${focused.dataset.attempt || focused.dataset.entry}` : null;
    const entries = store.queueOf(project, profile, key);
    ctx.queuedIds = store.get('queue').filter((e) => e.state === 'queued').map((e) => e.id);
    const knownAttempts = new Set((order.attempts || []).map((a) => a.id));
    const loose = entries.filter((e) => e.state !== 'done' && (e.attemptId === null || e.attemptId === undefined || !knownAttempts.has(e.attemptId)))
      .sort((a, b) => b.id - a.id);
    const attempts = [...(order.attempts || [])].sort((a, b) => (order.chosen === a.id ? -1 : order.chosen === b.id ? 1 : b.id - a.id));
    ctx.compare = ctx.compare.filter((id) => knownAttempts.has(id));

    // barra de la galería
    galleryBar.replaceChildren(
      h('span.hint', {}, t('ui.order.counts', { n: attempts.length, c: attempts.filter((a) => a.state === 'candidate').length, p: loose.filter((e) => PENDING.includes(e.state)).length })),
      h('span.grow'),
      compose.template ? h('button.btn.btn-toggle', { type: 'button', aria: { pressed: ctx.showRaw }, onclick: () => { ctx.showRaw = !ctx.showRaw; store.set('showRaw', ctx.showRaw); paint(); } }, t(ctx.showRaw ? 'ui.order.showingRaw' : 'ui.order.showingComposed'), h('kbd.kbd', { aria: { hidden: true } }, 'F')) : null,
      h('button.btn.btn-ghost', { type: 'button', onclick: reload }, '⟳ ', t('ui.order.refresh')));

    // entregada
    const chosen = attempts.find((a) => a.id === order.chosen);
    deliveredHost.replaceChildren(chosen ? h('div.card.delivered', {},
      h('span.chip.chip-fill-ok', {}, '★ ', t('ui.state.chosen')), h('b', {}, `q${chosen.id}`),
      h('span.path', {}, order.deliveredTo || (cfg.delivery && cfg.delivery.root ? `${cfg.delivery.root}/…` : '')),
      h('span.grow'),
      h('button.btn', { type: 'button', onclick: ctx.actions.undo }, '↶ ', t('ui.order.undo'))) : null);

    // comparar
    compareHost.replaceChildren(ctx.compare.length === 2 ? compareView(ctx, byId(attempts, ctx.compare[0]), byId(attempts, ctx.compare[1]), {
      onSwap: () => { ctx.compare.reverse(); paint(); }, onClose: () => { ctx.compare = []; paint(); },
    }) : ctx.compare.length === 1 ? h('p.hint', {}, t('ui.compare.pickAnother', { id: ctx.compare[0] })) : null);

    // galería
    const cards = [...loose.map((e) => queueCard(ctx, e)), ...attempts.map((a) => attemptCard(ctx, a))];
    for (const c of cards) c.setAttribute('role', 'listitem');
    gallery.replaceChildren(cards.length ? cards : h('div.empty', {}, h('p', {}, t('ui.order.noAttempts')), h('p.hint', {}, t('ui.order.noAttemptsHint'))));
    if (focusKey) { const again = gallery.querySelector(`[data-kind="${focusKey.split(':')[0]}"][data-${focusKey.split(':')[0] === 'attempt' ? 'attempt' : 'entry'}="${focusKey.split(':')[1]}"]`); if (again) again.focus(); }

    // panel lateral (se reconstruye solo si el pedido cambió de verdad: prompt/params/text/chosen)
    const sig = JSON.stringify([order.prompt, order.params, order.seed, order.draft, order.text, order.chosen]);
    if (panel.dataset.sig !== sig) {
      panel.dataset.sig = sig;
      retouch = retouchPanel(ctx, { onSubmit: guard(submit) });
      texts = textPanel(ctx, {
        onSave: async (text) => { try { await api.setText(project, profile, key, text); ctx.order.text = text; toastOk(t('ui.text.saved')); return true; } catch (e) { toastError(describeError(e, t)); return false; } },
        onRecompose: (id) => ctx.actions.recompose({ id }),
        onPreview: (text) => { ctx.previewText = text; store.set('previewText', Boolean(text)); paintGalleryOnly(); },
      });
      panel.replaceChildren(retouch.node, texts.node);
    }
  }

  function paintGalleryOnly() {
    for (const card of gallery.querySelectorAll('[data-kind="attempt"]')) {
      const a = byId(ctx.order.attempts || [], Number(card.dataset.attempt));
      if (a) card.replaceWith(Object.assign(attemptCard(ctx, a), { role: 'listitem' }));
    }
  }

  // atajos de la galería
  const onKey = (e) => {
    if (isTyping(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
    const card = closest(e.target, '[data-kind]');
    const cards = [...gallery.querySelectorAll('[data-kind]')];
    const i = cards.indexOf(card);
    const cols = Math.max(1, Math.round(gallery.clientWidth / (cards[0] ? cards[0].offsetWidth + 12 : 320)));
    const go = (j) => { const c = cards[Math.max(0, Math.min(cards.length - 1, j))]; if (c) { c.focus(); c.scrollIntoView({ block: 'nearest' }); } };
    const k = e.key;
    if (k === 'ArrowRight') { e.preventDefault(); go(i < 0 ? 0 : i + 1); }
    else if (k === 'ArrowLeft') { e.preventDefault(); go(i < 0 ? 0 : i - 1); }
    else if (k === 'ArrowDown') { e.preventDefault(); go(i < 0 ? 0 : i + cols); }
    else if (k === 'ArrowUp') { e.preventDefault(); go(i < 0 ? 0 : i - cols); }
    else if (k === 'f' || k === 'F') { const b = galleryBar.querySelector('.btn-toggle'); if (b) b.click(); }
    else if (k === 'g' || k === 'G') { if (retouch) retouch.another(); }
    else if (k === 'r' || k === 'R') { e.preventDefault(); if (retouch) retouch.focusPrompt(); }
    else if (card && card.dataset.kind === 'attempt') {
      const a = byId(ctx.order.attempts || [], Number(card.dataset.attempt));
      if (!a) return;
      const st = stateOf(ctx.order, a);
      if (k === 'Enter' && e.target === card) card.querySelector('.open').click();
      else if (k === 's' || k === 'S') ctx.actions.mark(a, st === 'candidate' ? 'new' : 'candidate');
      else if ((k === 'n' || k === 'N') && st !== 'chosen') ctx.actions.mark(a, st === 'discarded' ? 'new' : 'discarded');
      else if (k === 'e' || k === 'E') { if (st === 'chosen') ctx.actions.undo(); else if (st !== 'discarded' && !a.draft) ctx.actions.choose(a); }
      else if (k === 'c' || k === 'C') ctx.actions.compare(a);
    }
  };
  host.addEventListener('keydown', onKey);

  // refresco con la cola: lo de este pedido
  const mine = (e) => e.project === project && e.profile === profile && e.key === key;
  const offs = [
    poll.on('changed', () => { if (store.queueOf(project, profile, key).length || gallery.querySelector('[data-kind="entry"]')) paint(); }),
    poll.on('finished', (e) => { if (mine(e)) reload(); }),
    poll.on('failed', (e) => { if (mine(e)) reload(); }),
    poll.on('cancelled', (e) => { if (mine(e)) reload(); }),
  ];
  host.cleanup = () => { host.removeEventListener('keydown', onKey); offs.forEach((off) => off()); };

  paint();
  const want = route.query && route.query.a;
  const first = want ? gallery.querySelector(`[data-attempt="${want}"]`) : null;
  (first || gallery.querySelector('[data-kind]') || el('main')).focus();
}

function byId(list, id) { return list.find((a) => a.id === id); }
function pick(obj, keys) { const o = {}; for (const k of keys) if (obj && obj[k] !== undefined) o[k] = obj[k]; return o; }

/** Mediana de estimateMs de las entradas recientes del mismo perfil (si el servidor lo da). */
function estimateFor(profile) {
  const xs = store.get('queue').filter((e) => e.profile === profile && Number.isFinite(e.estimateMs)).map((e) => e.estimateMs).sort((a, b) => a - b);
  return xs.length ? xs[Math.floor(xs.length / 2)] : undefined;
}

async function copy(text, okMsg) {
  try { await navigator.clipboard.writeText(text); toast(okMsg); } catch { toastError(t('ui.attempt.copyFailed')); }
}
