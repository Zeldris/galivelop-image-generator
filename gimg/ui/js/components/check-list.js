/* Lista de comprobación de la hoja de marca (0.8.0 §2.1): el resumen «N bien · N avisos · N fallos» y una fila por regla,
   con su estado en texto además del color. La usan «Probar un sujeto» (brand-prompt.js), el nuevo pedido y el retoque.
   `checkList(checks, {onField})`: con `onField(campo)` cada fallo con campo (`c.field`, o el que le toca por su `id`) es un
   enlace enfocable que lleva a ese campo (`subject`, `zone`). */

import { h } from '../dom.js';
import { t } from '../i18n.js';

const STATUS = { ok: ['ui.check.ok', 'chip-ok'], warn: ['ui.check.warn', 'chip-warn'], error: ['ui.check.fail', 'chip-bad'] };
/** Qué campo arregla cada regla cuando la comprobación no trae `field`. */
export const FIELD_OF = { words: 'subject', veto: 'subject', neverWrite: 'subject', colorWord: 'subject', negation: 'subject', fillPhrase: 'subject', hex: 'subject', cleanZone: 'zone' };

export function checkList(checks, { onField = null } = {}) {
  const list = Array.isArray(checks) ? checks : [];
  const count = (s) => list.filter((c) => c.status === s).length;
  return h('div.stack', {},
    h('p', {}, h('b', {}, t('ui.check.summary', { ok: count('ok'), warn: count('warn'), fail: count('error') }))),
    h('ul.check-list', { data: { list: 'checks' } }, list.map((c) => {
      const [key, chip] = STATUS[c.status] || STATUS.warn;
      const msg = c.message || {};
      const field = c.status === 'error' && onField ? (c.field || FIELD_OF[c.id]) : null;
      const text = t(msg.key || c.id, msg.params);
      return h('li.check-item', { class: `is-${c.status === 'error' ? 'fail' : c.status}`, data: { check: c.id, status: c.status } },
        h('span.chip', { class: chip }, t(key)),
        h('div', {},
          h('div', {}, text, field ? [' ', h('a.check-link', { href: '#', data: { field }, onclick: (ev) => { ev.preventDefault(); onField(field); } }, '→ ', t('ui.check.goTo'))] : null),
          h('code.mono.hint', {}, c.id)));
    })));
}
