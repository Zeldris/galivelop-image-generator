/* Tarjeta de un intento en la galería del pedido: imagen (compuesta o fondo crudo), estado, metadatos, chip de medida,
   veredicto sí/no, elegir/deshacer, comparar, nota, y acciones secundarias (recrear, variar, copiar parámetros, registro).
   La misma tarjeta pinta una entrada de la cola todavía sin intento (en cola, generando con vista previa, fallo).
   Selector de plantilla (F4b, slots.js) y botón «Editar composición» (F4c, layout-editor.js). */

import { h, mmss, when, setVars } from '../dom.js';
import { t } from '../i18n.js';
import { paths } from '../api.js';
import { to } from '../router.js';
import { measureChip } from './measure-chip.js';
import { templateSlot, editorSlot, measureFor } from './slots.js';
import { progressOf, remainingMs } from './queue-bar.js';
import { openLightbox } from './lightbox.js';
import { imageVersion } from './attempt-util.js';

/** Estado de presentación de un intento: chosen > candidate/discarded/new. */
export function stateOf(order, attempt) {
  if (order.chosen === attempt.id) return 'chosen';
  return attempt.state || 'new';
}

function aspect(ctx, a) {
  const p = (a && a.params) || {};
  const w = p.width || ctx.profileCfg.width || 2;
  const hgt = p.height || ctx.profileCfg.height || 1;
  return `${w} / ${hgt}`;
}

/**
 * ctx: {project, profile, key, order, profileCfg, brand, measure: {zone, textColor, paletteMin}, templates: [plantillas del perfil], showRaw,
 *       compare: [ids], actions: {mark, note, choose, undo, compare, recreate, vary, copyParams, openLog, retry, cancel, copyError, recompose, setTemplate, setLayout, saveTemplate}}
 */
export function attemptCard(ctx, attempt) {
  const st = stateOf(ctx.order, attempt);
  const id = attempt.id;
  const compared = ctx.compare.includes(id);
  const raw = ctx.showRaw && attempt.raw;
  const version = imageVersion(attempt);
  const src = paths.image(ctx.project, ctx.profile, ctx.key, id, { raw, v: version });
  const alt = t('ui.attempt.image', { id, seed: attempt.seed });

  const figure = h('figure.figure', {}, h('img', { src, alt: '', loading: 'lazy' }));
  setVars(figure, { ar: aspect(ctx, attempt) });
  figure.append(h('button.open', { type: 'button', aria: { label: t('ui.attempt.open', { id }) }, onclick: () => openLightbox(src, `${t('ui.attempt.id', { id })} · ${t('ui.attempt.seed')} ${attempt.seed}`, alt) }));
  figure.append(badges(st, attempt));

  const meta = h('div.meta', {},
    h('span.id', {}, `q${id}`),
    h('span', {}, `${t('ui.attempt.seed')} `, h('b', {}, attempt.seed)),
    attempt.params && attempt.params.steps ? h('span', {}, `${attempt.params.steps} ${t('ui.attempt.steps')}`) : null,
    attempt.params && attempt.params.model ? h('span', { title: attempt.params.model }, shortModel(attempt.params.model)) : null,
    attempt.params && attempt.params.width ? h('span', {}, `${attempt.params.width}×${attempt.params.height}`) : null,
    Number.isFinite(attempt.durationMs) ? h('span', {}, mmss(attempt.durationMs)) : null,
    h('span.grow'),
    attempt.raw || attempt.image ? measureChip({ project: ctx.project, profile: ctx.profile, key: ctx.key, ...measureFor(ctx, attempt) }, attempt) : null);

  const yes = h('button.btn.btn-yes', { type: 'button', aria: { pressed: st === 'candidate' || st === 'chosen' }, onclick: () => ctx.actions.mark(attempt, st === 'candidate' ? 'new' : 'candidate') }, t('ui.attempt.yes'), h('kbd.kbd', { aria: { hidden: true } }, 'S'));
  const no = h('button.btn.btn-no', { type: 'button', disabled: st === 'chosen', aria: { pressed: st === 'discarded' }, onclick: () => ctx.actions.mark(attempt, st === 'discarded' ? 'new' : 'discarded') }, t('ui.attempt.no'), h('kbd.kbd', { aria: { hidden: true } }, 'N'));
  const choose = st === 'chosen'
    ? h('button.btn', { type: 'button', onclick: () => ctx.actions.undo() }, '↶ ', t('ui.order.undo'))
    : h('button.btn.btn-primary', { type: 'button', disabled: st === 'discarded' || Boolean(attempt.draft) || Boolean(attempt.composeError && ctx.profileCfg.compose), title: attempt.draft ? t('ui.attempt.draftNoChoose') : null, onclick: () => ctx.actions.choose(attempt) }, '★ ', t('ui.attempt.choose'), h('kbd.kbd', { aria: { hidden: true } }, 'E'));
  const compare = h('button.btn.btn-toggle', { type: 'button', aria: { pressed: compared }, onclick: () => ctx.actions.compare(attempt) }, '⇄ ', t(compared ? 'ui.attempt.compareOn' : 'ui.attempt.compare'), h('kbd.kbd', { aria: { hidden: true } }, 'C'));
  const actions = h('div.actions', {}, yes, no, choose, compare);

  const note = h('input.note', {
    type: 'text', value: attempt.note || '', placeholder: t('ui.attempt.notePlaceholder'), maxlength: 500,
    aria: { label: t('ui.attempt.noteFor', { id }) },
    onchange: (e) => ctx.actions.note(attempt, e.target.value),
  });

  const more = h('details', {}, h('summary', {}, t('ui.attempt.more')), h('div.actions', {},
    h('button.btn', { type: 'button', title: t('ui.attempt.recreateHint'), onclick: () => ctx.actions.recreate(attempt) }, '↩ ', t('ui.attempt.recreate')),
    h('button.btn', { type: 'button', title: t('ui.attempt.varyHint'), onclick: () => ctx.actions.vary(attempt) }, '▶ ', t('ui.attempt.vary')),
    h('button.btn', { type: 'button', onclick: () => ctx.actions.copyParams(attempt) }, '⎘ ', t('ui.attempt.copyParams')),
    attempt.image ? h('a.btn', { href: `${to.project(ctx.project, 'marca')}?src=${encodeURIComponent(`${ctx.profile}|${ctx.key}|${id}`)}`, title: t('ui.attempt.forBrandHint') }, '◈ ', t('ui.attempt.forBrand')) : null,
    attempt.log ? h('a.btn', { href: paths.log(ctx.project, ctx.profile, ctx.key, id), target: '_blank', rel: 'noopener' }, t('ui.attempt.log')) : null,
  ), h('div.stack', {}, templateSlot(ctx, attempt), editorSlot(ctx, attempt)));

  const extras = [];
  if (attempt.composeError) extras.push(h('p.notice.notice-warn.small', {}, t('ui.attempt.notComposed'), ' ', h('button.btn', { type: 'button', onclick: () => ctx.actions.recompose(attempt) }, t('ui.text.recomposeThis'))));
  if (attempt.compose && attempt.compose.at) extras.push(h('p.hint', {}, t('ui.attempt.composedAt', { when: when(attempt.compose.at) })));

  return h('article.card.attempt', {
    class: `is-${st}${compared ? ' is-compared' : ''}`, tabindex: 0, data: { attempt: id, kind: 'attempt' },
    aria: { label: `${t('ui.attempt.id', { id })}, ${t('ui.state.' + st)}` },
  }, figure, meta, actions, extras, note, more);
}

/** Tarjeta de una entrada de la cola sin intento aún (queued / running / failed / cancelled). */
export function queueCard(ctx, entry) {
  const id = `q${entry.id}`;
  const figure = h('figure.figure', {});
  setVars(figure, { ar: aspect(ctx, entry) });
  const block = h('div.status-block', {});
  if (entry.state === 'running') {
    block.append(h('img.preview', { src: paths.preview(entry.id), alt: '', onerror: (e) => e.target.remove() }));
    const rem = remainingMs(entry);
    block.append(h('b', {}, t('ui.state.running'), '…'),
      h('span', {}, entry.progress && entry.progress.steps ? t('ui.queue.step', { step: entry.progress.step, steps: entry.progress.steps }) : null, ' ', rem === null ? t('ui.queue.noEstimate') : t('ui.queue.eta', { t: mmss(rem) })),
      progressOf(entry),
      h('button.btn.btn-danger', { type: 'button', onclick: () => ctx.actions.cancel(entry) }, t('ui.queue.cancel')));
  } else if (entry.state === 'queued') {
    const pos = ctx.queuedIds.indexOf(entry.id) + 1;
    const rem = remainingMs(entry);
    block.append(h('b', {}, t('ui.state.queued')), h('span', {}, t('ui.queue.position', { n: pos }), rem === null ? '' : ` · ${t('ui.queue.eta', { t: mmss(rem) })}`),
      h('button.btn.btn-danger', { type: 'button', onclick: () => ctx.actions.cancel(entry) }, t('ui.queue.cancel')));
  } else {
    block.append(h('b', {}, t(`ui.state.${entry.state}`)), h('div.err', {}, entry.errorText || (entry.error && entry.error.code) || ''),
      h('div.actions', {},
        h('button.btn', { type: 'button', onclick: () => ctx.actions.retry(entry) }, t('ui.attempt.retry')),
        entry.errorText ? h('button.btn', { type: 'button', onclick: () => ctx.actions.copyError(entry) }, '⎘ ', t('ui.attempt.copyError')) : null));
  }
  figure.append(block, badges(entry.state, entry));
  const meta = h('div.meta', {}, h('span.id', {}, id), h('span', {}, `${t('ui.attempt.seed')} `, h('b', {}, entry.seed)),
    entry.params && entry.params.steps ? h('span', {}, `${entry.params.steps} ${t('ui.attempt.steps')}`) : null,
    entry.params && entry.params.model ? h('span', {}, shortModel(entry.params.model)) : null);
  return h('article.card.attempt', { class: `is-${entry.state}`, tabindex: 0, data: { entry: entry.id, kind: 'entry' }, aria: { label: `${id}, ${t('ui.state.' + entry.state)}` } }, figure, meta);
}

function badges(st, a) {
  const cls = { chosen: 'chip-fill-ok', candidate: 'chip-fill-accent', failed: 'chip-fill-bad', running: 'chip-fill-ok' }[st] || '';
  return h('div.badges', {}, h('span.chip', { class: cls }, t(`ui.state.${st}`)), a.draft ? h('span.chip', {}, t('ui.state.draft')) : null, a.compose ? h('span.chip', {}, t('ui.attempt.composed')) : null);
}

function shortModel(m) { return String(m).replace(/-q\d+.*$/i, '').slice(0, 24); }
