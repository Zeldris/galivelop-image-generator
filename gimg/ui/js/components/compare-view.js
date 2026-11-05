/* Comparar dos intentos lado a lado, al mismo tamaño (decisión 8 de propuesta.md), con intercambiar y cerrar. */

import { h, setVars } from '../dom.js';
import { t } from '../i18n.js';
import { paths } from '../api.js';
import { stateOf } from './attempt-card.js';
import { measureChip } from './measure-chip.js';

export function compareView(ctx, a, b, { onSwap, onClose }) {
  const fig = (att, side) => {
    const raw = ctx.showRaw && att.raw;
    const src = paths.image(ctx.project, ctx.profile, ctx.key, att.id, { raw });
    const f = h('div.figure', {}, h('img', { src, alt: t('ui.attempt.image', { id: att.id, seed: att.seed }) }));
    const p = att.params || {};
    setVars(f, { ar: `${p.width || ctx.profileCfg.width || 2} / ${p.height || ctx.profileCfg.height || 1}` });
    return h('figure', {}, h('figcaption', {}, h('b.mono', {}, `${t(side)}: q${att.id}`), h('span.chip', {}, t('ui.state.' + stateOf(ctx.order, att))),
      h('span', {}, `${t('ui.attempt.seed')} ${att.seed}${p.steps ? ` · ${p.steps} ${t('ui.attempt.steps')}` : ''}`),
      measureChip({ project: ctx.project, profile: ctx.profile, key: ctx.key, ...ctx.measure }, att)), f);
  };
  return h('section.card.compare', { aria: { label: t('ui.compare.title') } },
    h('div.row-between', {}, h('h2', {}, t('ui.compare.title')), h('div.row', {},
      h('button.btn', { type: 'button', onclick: onSwap }, '⇄ ', t('ui.compare.swap')),
      h('button.btn', { type: 'button', onclick: onClose }, t('ui.compare.close')))),
    h('div.pair', {}, fig(a, 'ui.compare.a'), fig(b, 'ui.compare.b')));
}
