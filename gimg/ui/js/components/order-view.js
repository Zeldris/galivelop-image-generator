/* Pantalla del pedido (el corazón de F4a, docs/interfaz/propuesta.md): galería de intentos con estados, veredicto,
   elegir/deshacer, comparar, panel de retoque, textos compuestos, chip de medida, vista previa de lo que se genera.
   Carga GET project (config del perfil y marca) + GET order; se refresca cuando la cola cambia (queue-poll) sin perder
   el foco. Los atajos de la galería (←/→/↑/↓, Intro, S, N, E, C, F, G, R) viven aquí. */

import { h, el, closest } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError, ApiError } from '../api.js';
import { to, navigate } from '../router.js';
import * as store from '../store.js';
import * as poll from '../queue-poll.js';
import { attemptCard, queueCard, stateOf } from './attempt-card.js';
import { compareView } from './compare-view.js';
import { stripStyle } from './attempt-util.js';
import { retouchPanel } from './retouch-panel.js';
import { textPanel } from './text-panel.js';
import { invalidateMeasure } from './measure-chip.js';
import { isTyping, oneKeyEnabled } from './shortcuts.js';
import { toast, toastError, toastOk } from './toast.js';
import { confirmAction } from './confirm.js';
import { renameDialog } from './rename-dialog.js';

const PENDING = ['queued', 'running'];

export async function orderView(host, route) {
  const { project, profile, key } = route;
  host.append(h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
  let info;
  let order;
  let templates = [];
  let models = [];
  try {
    // las plantillas y el catálogo de modelos se piden una vez por vista; si fallan, el pedido sigue sin selector
    [info, order, templates, models] = await Promise.all([api.project(project), api.order(project, profile, key), api.templates(project, profile).catch(() => []), api.models().catch(() => [])]);
  } catch (e) {
    host.replaceChildren(h('h1', {}, key), h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)),
      h('p', {}, h('a.btn', { href: to.project(project) }, '← ', t('ui.order.backToProject'))));
    return;
  }
  if (!host.isConnected) return; // se navegó a otra pantalla durante la carga: nada que registrar
  const cfg = info.config || {};
  const profileCfg = (cfg.profiles || {})[profile] || {};
  const brand = cfg.brand || {};
  const compose = profileCfg.compose || {};
  const ctx = {
    project, profile, key, order, profileCfg, brand, templates: Array.isArray(templates) ? templates : [], models: Array.isArray(models) ? models : [],
    measure: { zone: compose.zone, textColor: compose.textColor || brand.textColor, paletteMin: brand.paletteMin },
    showRaw: store.get('showRaw'), compare: [], queuedIds: [], estimateMs: estimateFor(profile),
    actions: {},
  };

  const galleryBar = h('div.gallery-bar', { role: 'toolbar', aria: { label: t('ui.order.galleryTools') } });
  const gallery = h('div.gallery', { role: 'list', aria: { label: t('ui.order.gallery') } });
  const compareHost = h('div');
  const deliveredHost = h('div');
  const panel = h('aside.order-panel', { aria: { label: t('ui.order.panel') } });
  const title = h('div.page-head', {}, h('h1', { tabindex: '-1' }, key), h('span.chip', {}, profile, profileCfg.width ? ` · ${profileCfg.width}×${profileCfg.height}` : ''),
    h('button.btn', { type: 'button', data: { fid: 'rename-order' }, onclick: () => ctx.actions.rename() }, t('ui.order.rename')),
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
    copyParams: (a) => copy(JSON.stringify({ seed: a.seed, prompt: a.prompt === null || a.prompt === undefined ? a.prompt : stripStyle(a.prompt, profileCfg.style), ...(a.params || {}) }, null, 2), t('ui.attempt.copied')),
    copyError: (e) => copy(e.errorText || JSON.stringify(e.error), t('ui.attempt.copied')),
    retry: guard(async (e) => {
      const text = e.prompt === null || e.prompt === undefined ? null : stripStyle(e.prompt, profileCfg.style);
      await submit({ count: 1, seed: e.seed, draft: Boolean(e.draft), ...(text !== null && text !== (ctx.order.prompt || '') ? { prompt: text } : {}), ...(e.template ? { template: e.template } : {}), ...pick(e.params, ['steps', 'cfg', 'sampler']),
        ...(e.params && e.params.model && e.params.model !== (ctx.order.params || {}).model && e.params.model !== profileCfg.model ? { model: e.params.model } : {}) }); // F4d: el modelo del intento, si no es el del pedido ni el del perfil
    }),
    cancel: guard(async (e) => { await api.cancel(e.id); toast(t('ui.queue.cancelled', { id: e.id })); await poll.refreshNow(); }),
    /** F4e.1: quitar de la cola una entrada fallida o cancelada (sin intento ni imagen), tras el modal «sí / no». */
    removeEntry: guard(async (e) => {
      const opener = () => document.querySelector(`[data-entry="${e.id}"][data-kind="entry"]`);
      const ok = await confirmAction({ title: t('ui.queue.deleteTitle', { id: e.id }), message: t('ui.queue.deleteMessage', { id: e.id }), confirmLabel: t('ui.queue.deleteConfirm'), opener });
      if (!ok) return;
      try {
        await api.removeEntry(e.id);
        toastOk(t('ui.queue.deleted', { id: e.id }));
      } finally {
        await poll.refreshNow();
      }
    }),
    setTemplate: async (a, id) => {
      try {
        await api.compose(project, profile, key, a.id, { template: id });
        invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`);
        toastOk(t('ui.attempt.templateChanged', { id: a.id, template: id }));
        await reload();
        return true;
      } catch (e) {
        toastError(describeError(e, t));
        await reload(); // el servidor ya cambió el intento (composeError, imagen cruda)
        return false;
      }
    },
    /** El editor de elementos (layout-editor.js): `layout` = solo lo movido; `{}` vuelve a la plantilla. Si falla, recarga
        el pedido (el servidor ya dejó el intento con su composeError) y relanza el error para que el editor lo muestre. */
    setLayout: async (a, layout) => {
      try {
        await api.compose(project, profile, key, a.id, { layout });
        invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`);
        toastOk(t(Object.keys(layout).length ? 'ui.editor.applied' : 'ui.editor.resetDone', { id: a.id }));
        await reload();
      } catch (e) {
        await reload();
        throw e;
      }
    },
    /** Plantilla nueva desde un intento (D40); después se piden otra vez las plantillas para que salga en los selectores. */
    saveTemplate: async (a, name, dest) => {
      const entry = await api.saveTemplate(project, profile, { from: { key, attempt: a.id }, name, dest });
      toastOk(t('ui.editor.saved', { name }));
      try { ctx.templates = await api.templates(project, profile); } catch (e) { toastError(describeError(e, t)); }
      paintGalleryOnly();
      return entry;
    },
    /** F4e.5: renombrar el pedido. Con la clave nueva aceptada, el servidor lo mueve todo y se navega al pedido renombrado;
        si falla (clave repetida, pedido ocupado...), el aviso lleva el motivo y esta pantalla queda como estaba. */
    rename: guard(async () => {
      const opener = () => document.querySelector('[data-fid="rename-order"]');
      const newKey = await renameDialog({ current: key, opener });
      if (!newKey) return;
      const renamed = await api.renameOrder(project, profile, key, newKey);
      const now = (renamed && renamed.key) || newKey;
      toastOk(t('ui.order.renamed', { key: now }));
      navigate(to.order(project, profile, now));
    }),
    /** F4e.1: borrar un intento o su composición; siempre tras el modal «sí / no». El 409 del servidor sale en el toast. */
    deleteAttempt: guard(async (a) => {
      const opener = () => document.querySelector(`[data-attempt="${a.id}"][data-kind="attempt"]`);
      const ok = await confirmAction({ title: t('ui.attempt.deleteTitle', { id: a.id }), message: t('ui.attempt.deleteMessage', { id: a.id }), confirmLabel: t('ui.attempt.deleteConfirm'), opener });
      if (!ok) return;
      try {
        await api.deleteAttempt(project, profile, key, a.id);
        ctx.compare = ctx.compare.filter((x) => x !== a.id);
        toastOk(t('ui.attempt.deleted', { id: a.id }));
      } finally {
        invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`);
        await reload();
      }
    }),
    deleteCompose: guard(async (a) => {
      const chosen = ctx.order.chosen === a.id;
      const opener = () => document.querySelector(`[data-attempt="${a.id}"][data-kind="attempt"]`);
      const ok = await confirmAction({ title: t('ui.attempt.deleteComposeTitle', { id: a.id }),
        message: chosen ? t('ui.attempt.deleteComposeChosenMessage', { id: a.id }) : t('ui.attempt.deleteComposeMessage', { id: a.id }),
        confirmLabel: t('ui.attempt.deleteComposeConfirm'), opener });
      if (!ok) return;
      try {
        await api.deleteCompose(project, profile, key, a.id);
        toastOk(t('ui.attempt.composeDeleted', { id: a.id }));
      } finally {
        invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`);
        await reload();
      }
    }),
    recompose: guard(async (a) => {
      try {
        await api.compose(project, profile, key, a.id, {});
        toastOk(t('ui.text.recomposed', { id: a.id }));
      } finally {
        invalidateMeasure(`${project}/${profile}/${key}/${a.id}@`);
        await reload();
      }
    }),
  });

  async function submit(spec) {
    const res = await api.newAttempts(project, profile, key, spec);
    const n = (res && res.entries && res.entries.length) || spec.count || 1;
    // res.estimateMs es lo que tarda una entrada (la primera): el total del aviso es ese tiempo por n
    toastOk(t('ui.retouch.queued', { n, t: res && Number.isFinite(res.estimateMs) ? ` · ~${Math.round((res.estimateMs * n) / 1000)} s` : '' }));
    if (res && Number.isFinite(res.estimateMs)) ctx.estimateMs = res.estimateMs;
    await poll.refreshNow();
  }

  /** Reconstruye una zona solo si su firma cambió: un sondeo de la cola sin novedades no toca el DOM (ni el foco). */
  function section(node, sig, build) {
    if (node.dataset.sig === sig) return;
    node.dataset.sig = sig;
    const FOCUSABLE = 'button, a, input, select, summary';
    const active = document.activeElement;
    const idx = node.contains(active) ? [...node.querySelectorAll(FOCUSABLE)].indexOf(active) : -1;
    node.replaceChildren(...[].concat(build()).filter(Boolean));
    if (idx >= 0) { const again = node.querySelectorAll(FOCUSABLE)[idx]; if (again) again.focus(); }
  }

  function paint() {
    const order = ctx.order;
    const entries = store.queueOf(project, profile, key);
    ctx.queuedIds = store.get('queue').filter((e) => e.state === 'queued').map((e) => e.id);
    const knownAttempts = new Set((order.attempts || []).map((a) => a.id));
    const loose = entries.filter((e) => e.state !== 'done' && (e.attemptId === null || e.attemptId === undefined || !knownAttempts.has(e.attemptId)))
      .sort((a, b) => b.id - a.id);
    const attempts = [...(order.attempts || [])].sort((a, b) => (order.chosen === a.id ? -1 : order.chosen === b.id ? 1 : b.id - a.id));
    ctx.compare = ctx.compare.filter((id) => knownAttempts.has(id));
    ctx.attemptsSorted = attempts;
    ctx.loose = loose;

    // barra de la galería
    const counts = { n: attempts.length, c: attempts.filter((a) => a.state === 'candidate').length, p: loose.filter((e) => PENDING.includes(e.state)).length };
    section(galleryBar, JSON.stringify([counts, ctx.showRaw, Boolean(compose.template)]), () => [
      h('span.hint', {}, t('ui.order.counts', counts)),
      h('span.grow'),
      compose.template ? h('button.btn.btn-toggle', { type: 'button', aria: { pressed: ctx.showRaw }, onclick: () => { ctx.showRaw = !ctx.showRaw; store.set('showRaw', ctx.showRaw); paint(); } }, t(ctx.showRaw ? 'ui.order.showingRaw' : 'ui.order.showingComposed'), h('kbd.kbd', { aria: { hidden: true } }, 'F')) : null,
      h('button.btn.btn-ghost', { type: 'button', onclick: reload }, '⟳ ', t('ui.order.refresh'))]);

    // entregada
    const chosen = attempts.find((a) => a.id === order.chosen);
    section(deliveredHost, JSON.stringify([chosen ? chosen.id : null, order.deliveredTo]), () => chosen ? h('div.card.delivered', {},
      h('span.chip.chip-fill-ok', {}, '★ ', t('ui.state.chosen')), h('b', {}, `q${chosen.id}`),
      h('span.path', {}, order.deliveredTo || (cfg.delivery && cfg.delivery.root ? `${cfg.delivery.root}/…` : '')),
      h('span.grow'),
      h('button.btn', { type: 'button', onclick: ctx.actions.undo }, '↶ ', t('ui.order.undo'))) : null);

    // comparar
    section(compareHost, JSON.stringify([ctx.compare, ctx.showRaw, ctx.compare.map((id) => byId(attempts, id)), order.chosen]), () => ctx.compare.length === 2 ? compareView(ctx, byId(attempts, ctx.compare[0]), byId(attempts, ctx.compare[1]), {
      onSwap: () => { ctx.compare.reverse(); paint(); }, onClose: () => { ctx.compare = []; paint(); },
    }) : ctx.compare.length === 1 ? h('p.hint', {}, t('ui.compare.pickAnother', { id: ctx.compare[0] })) : null);

    paintGalleryOnly();

    // panel lateral: se reconstruye solo si cambió el prompt o los parámetros del pedido (no `chosen` ni `text`:
    // elegir, deshacer o guardar los textos no debe borrar lo que se está editando ni el foco)
    const sig = JSON.stringify([order.prompt, order.params, order.seed, order.draft]);
    if (panel.dataset.sig !== sig) {
      panel.dataset.sig = sig;
      retouch = retouchPanel(ctx, { onSubmit: guard(submit) });
      texts = textPanel(ctx, {
        onSave: async (text) => { try { await api.setText(project, profile, key, text); ctx.order.text = text; toastOk(t('ui.text.saved')); return true; } catch (e) { toastError(describeError(e, t)); return false; } },
        onRecompose: (id) => ctx.actions.recompose({ id }),
      });
      panel.replaceChildren(retouch.node, texts.node);
    } else {
      if (texts && texts.setChosen) texts.setChosen(order.chosen);
      if (retouch && retouch.setChosen) retouch.setChosen();
    }
  }

  /** Concilia la galería por clave: solo se rehace la tarjeta cuya firma cambió; el resto (con su foco, su nota a
      medio escribir y su «Más» abierto) no se toca. Una tarjeta con el foco en un campo se deja hasta que lo pierda. */
  const cardsByKey = new Map(); // 'attempt:3' | 'entry:11' -> {sig, node}
  function paintGalleryOnly() {
    const order = ctx.order;
    const attempts = ctx.attemptsSorted || [];
    const loose = ctx.loose || [];
    const wanted = [
      ...loose.map((e) => ({ k: `entry:${e.id}`, sig: JSON.stringify([e, ctx.queuedIds.indexOf(e.id)]), make: () => queueCard(ctx, e) })),
      ...attempts.map((a) => {
        const { note, ...rest } = a; // la nota la escribe la propia tarjeta: no cuenta como cambio
        const st = stateOf(order, a);
        const compared = ctx.compare.includes(a.id);
        return { k: `attempt:${a.id}`, sig: JSON.stringify([rest, st, compared, ctx.showRaw, ctx.templates.map((x) => x.id)]), make: () => attemptCard(ctx, a) };
      }),
    ];
    if (!wanted.length) {
      if (cardsByKey.size || !gallery.firstChild) {
        cardsByKey.clear();
        gallery.replaceChildren(h('div.empty', {}, h('p', {}, t('ui.order.noAttempts')), h('p.hint', {}, t('ui.order.noAttemptsHint'))));
      }
      return;
    }
    const keep = new Set(wanted.map((w) => w.k));
    for (const [k, rec] of cardsByKey) if (!keep.has(k)) { rec.node.remove(); cardsByKey.delete(k); }
    if (!cardsByKey.size) gallery.replaceChildren();
    const active = document.activeElement;
    wanted.forEach((w, i) => {
      const old = cardsByKey.get(w.k);
      let node = old && old.node;
      if (!old || old.sig !== w.sig) {
        const typing = old && old.node.contains(active) && isTyping(active);
        if (typing) { node = old.node; } else {
          const fresh = w.make();
          fresh.setAttribute('role', 'listitem');
          if (old) {
            const els = [...old.node.querySelectorAll('button, a, input, select, summary')];
            const idx = old.node.contains(active) ? (active === old.node ? -1 : els.indexOf(active)) : -2;
            const was = old.node.querySelector('details');
            const det = fresh.querySelector('details');
            if (was && det && was.open) det.open = true;
            old.node.replaceWith(fresh);
            if (idx === -1) fresh.focus();
            else if (idx >= 0) { const again = [...fresh.querySelectorAll('button, a, input, select, summary')][idx]; (again || fresh).focus(); }
          }
          node = fresh;
          cardsByKey.set(w.k, { sig: w.sig, node });
        }
      }
      if (gallery.children[i] !== node) gallery.insertBefore(node, gallery.children[i] || null);
    });
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
    const letter = k.length === 1 && /[a-z]/i.test(k);
    if (letter && (!oneKeyEnabled() || panel.contains(e.target))) return; // atajos de una tecla: apagados, o el foco está en el panel
    if (k === 'ArrowRight') { e.preventDefault(); go(i < 0 ? 0 : i + 1); }
    else if (k === 'ArrowLeft') { e.preventDefault(); go(i < 0 ? 0 : i - 1); }
    else if (k === 'ArrowDown') { e.preventDefault(); go(i < 0 ? 0 : i + cols); }
    else if (k === 'ArrowUp') { e.preventDefault(); go(i < 0 ? 0 : i - cols); }
    else if (k === 'f' || k === 'F') { const b = galleryBar.querySelector('.btn-toggle'); if (b) b.click(); }
    else if (k === 'g' || k === 'G') { if (retouch) retouch.another(); }
    else if (k === 'r' || k === 'R') { e.preventDefault(); if (retouch) retouch.focusPrompt(); }
    else if (k === 't' || k === 'T' || k === 'x' || k === 'X') {
      const zone = (k === 't' || k === 'T') ? retouch && retouch.node : texts && texts.node;
      const c = zone && zone.querySelector('button, a, input, select, textarea, summary');
      if (c) { e.preventDefault(); c.focus(); }
    }
    else if (card && card.dataset.kind === 'attempt') {
      const a = byId(ctx.order.attempts || [], Number(card.dataset.attempt));
      if (!a) return;
      const st = stateOf(ctx.order, a);
      if (k === 'Enter' && e.target === card) { e.preventDefault(); card.querySelector('.open').click(); } // sin keypress: en Firefox caería en el botón que recibe el foco del visor y lo cerraría
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
  const all = ctx.order.attempts || [];
  const nuevos = all.filter((a) => stateOf(ctx.order, a) === 'new').length;
  const status = document.getElementById('status'); // polite: no corta la lectura del título que recibe el foco
  if (status) { status.textContent = ''; status.textContent = t('ui.order.loaded', { n: all.length, m: nuevos }); }
  // el foco va al título de la vista; solo un enlace directo a un intento (?a=) lo lleva a su tarjeta
  (first || title.querySelector('h1') || el('main')).focus();
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
