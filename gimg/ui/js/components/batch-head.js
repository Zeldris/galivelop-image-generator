/* Cabecera de una tanda en la galería del pedido (0.8.0 §2.2): «Tanda 3 · sujeto: "…" · 4 intentos», los avisos con los
   que se encoló y, si la tanda falló, su motivo. `s`: {id, rec (el registro de `order.batches`, si está), n (su número,
   por orden de creación), attempts: [intentos], pending: entradas de la cola sin intento aún}. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { traitLabel } from './brand-order.js';

const MAX_SUBJECT = 80;

export function batchHead(ctx, s) {
  const rec = s.rec || {};
  const subject = typeof rec.subject === 'string' && rec.subject ? (rec.subject.length > MAX_SUBJECT ? `${rec.subject.slice(0, MAX_SUBJECT).trimEnd()}…` : rec.subject) : '';
  const parts = [t('ui.batch.title', { n: s.n })];
  if (subject) parts.push(t('ui.batch.subject', { subject }));
  parts.push(t('ui.batch.attempts', { n: s.attempts.length }));
  if (s.pending) parts.push(t('ui.batch.pending', { n: s.pending }));
  const warnings = (rec.warnings || []).map((c) => {
    const msg = c.message || {};
    return h('span.chip.chip-warn', { title: c.id || '' }, t(msg.key || c.id, msg.params));
  });
  const failed = rec.failed
    ? h('span.chip.chip-bad', { data: { slot: 'batch-failed' } }, t('ui.batch.failed', { reason: traitLabel(ctx.sheet, (rec.reason && rec.reason.trait) || 'other') }))
    : null;
  return h('div.batch-head', { data: { batch: s.id } },
    h('h3', {}, parts.join(' · ')), failed, warnings.length ? h('div.row', { data: { slot: 'batch-warnings' } }, warnings) : null,
    h('span.grow'), ...(s.actions || []));
}
