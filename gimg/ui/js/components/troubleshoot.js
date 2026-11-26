/* Troubleshooting de un pedido de marca (0.8.0 paso 5c, docs/interfaz/marca.md §2.5).
   `troubleshootForm(ctx, {onSave, onExtend})`: el formulario que sustituye al panel lateral cuando el pedido está bloqueado
   (`troubleshooting.state === 'blocked'`), con las columnas del registro: Problema (propuesto con los motivos de
   `failures.reasons`), Intentos (los `q<id>` de las tandas falladas, editable), Rediseño (texto) y, opcional, los
   términos que harán saltar el «ya falló antes». Salidas: «Apuntar y rediseñar yo» (`onSave(body)` -> POST …/troubleshooting) y
   «Una tanda más sin rediseñar» (pide confirmación; `onExtend()`). Las dos devuelven una promesa: si rechaza, el error
   sale en el formulario y se conserva lo escrito. El foco va al título (`tabindex="-1"`) y el aviso lleva `role="alert"`.
   `troubleshootTable(project)`: el registro del proyecto (Marca › Troubleshooting) con enlaces a los intentos y filtro por pieza. */

import { h, replace, when } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError } from '../api.js';
import { to } from '../router.js';
import { confirmAction } from './confirm.js';
import { failuresOf, reasonsText } from './brand-order.js';

/** Los ids de los intentos de las tandas falladas del pedido. */
export function failedAttemptIds(order) {
  const failed = new Set((order.batches || []).filter((b) => b.failed).map((b) => b.id));
  return (order.attempts || []).filter((a) => a.batch !== null && a.batch !== undefined && failed.has(typeof a.batch === 'object' ? a.batch.id : a.batch)).map((a) => a.id);
}

const parseIds = (text) => [...new Set((String(text).match(/\d+/g) || []).map(Number))];
const parseTerms = (text) => [...new Set(String(text).split(/[,;\n]/).map((x) => x.trim()).filter(Boolean))];

export function troubleshootForm(ctx, { onSave, onExtend }) {
  const order = ctx.order;
  const f = failuresOf(order);
  const problem = h('textarea', { id: 'ts-problem', rows: 3, value: reasonsText(f.reasons, ctx.sheet), aria: { describedby: 'ts-problem-hint' } });
  const attempts = h('input', { id: 'ts-attempts', type: 'text', value: failedAttemptIds(order).map((id) => `q${id}`).join(', '), aria: { describedby: 'ts-attempts-hint' } });
  const redesign = h('textarea', { id: 'ts-redesign', rows: 3 });
  const terms = h('input', { id: 'ts-terms', type: 'text', aria: { describedby: 'ts-terms-hint' } });
  const errorHost = h('div', { data: { slot: 'ts-error' } });
  const title = h('h2', { id: 'ts-title', tabindex: '-1' }, t('ui.ts.title'));
  let busy = false;
  const buttons = [];
  const run = async (fn) => {
    if (busy) return;
    busy = true;
    buttons.forEach((b) => { b.disabled = true; });
    replace(errorHost);
    try { await fn(); } catch (e) {
      replace(errorHost, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)));
    } finally { busy = false; buttons.forEach((b) => { b.disabled = false; }); }
  };
  const save = h('button.btn.btn-primary', { type: 'button', data: { slot: 'ts-save' }, onclick: () => run(async () => {
    if (!problem.value.trim()) { problem.focus(); throw new Error(t('ui.ts.problemRequired')); }
    const body = { key: order.key, profile: order.profile, problem: problem.value.trim(), attempts: parseIds(attempts.value), by: 'person' };
    if (redesign.value.trim()) body.redesign = redesign.value.trim();
    const list = parseTerms(terms.value);
    if (list.length) body.terms = list;
    await onSave(body);
  }) }, t('ui.ts.save'));
  const more = h('button.btn', { type: 'button', data: { slot: 'ts-extend' }, onclick: (ev) => run(async () => {
    const ok = await confirmAction({ title: t('ui.ts.extendTitle'), message: t('ui.ts.extendMessage'), confirmLabel: t('ui.ts.extend'), opener: ev.currentTarget });
    if (ok) await onExtend();
  }) }, t('ui.ts.extend'));
  buttons.push(save, more);
  const node = h('section.card.troubleshoot', { aria: { labelledby: 'ts-title' }, data: { slot: 'ts-form' } },
    title,
    h('p.notice.notice-bad', { role: 'alert' }, t('ui.fail.blocked', { count: f.count, limit: f.limit })),
    h('div.field', {}, h('label', { for: 'ts-problem' }, t('ui.ts.problem')), problem, h('div.hint', { id: 'ts-problem-hint' }, t('ui.ts.problemHint'))),
    h('div.field', {}, h('label', { for: 'ts-attempts' }, t('ui.ts.attempts')), attempts, h('div.hint', { id: 'ts-attempts-hint' }, t('ui.ts.attemptsHint'))),
    h('div.field', {}, h('label', { for: 'ts-redesign' }, t('ui.ts.redesign')), redesign),
    h('div.field', {}, h('label', { for: 'ts-terms' }, t('ui.ts.terms')), terms, h('div.hint', { id: 'ts-terms-hint' }, t('ui.ts.termsHint'))),
    errorHost,
    h('div.row', {}, save, more));
  return { node, focus: () => title.focus() };
}

/** La tabla del registro de un proyecto: GET …/troubleshooting, con filtro por pieza; cargando / vacío / error con «Reintentar». */
export function troubleshootTable(project) {
  const body = h('div.stack', { aria: { live: 'polite' } });
  let rows = [];
  let piece = '';
  const pieceOf = (r) => r.piece || r.key;
  const draw = () => {
    const pieces = [...new Set(rows.map(pieceOf))].sort();
    const shown = rows.filter((r) => !piece || pieceOf(r) === piece);
    const filter = h('select', { id: 'ts-filter', data: { slot: 'ts-filter' }, onchange: (ev) => { piece = ev.target.value; draw(); ctxFocus(); } },
      h('option', { value: '' }, t('ui.ts.allPieces')), pieces.map((p) => h('option', { value: p, selected: p === piece }, p)));
    const ctxFocus = () => { const el = document.getElementById('ts-filter'); if (el) el.focus(); };
    replace(body,
      h('div.row', {}, h('label', { for: 'ts-filter' }, t('ui.ts.filter')), filter, h('span.hint', {}, t('ui.ts.count', { n: shown.length }))),
      shown.length ? h('div.table-wrap', {}, h('table.tbl', { data: { slot: 'ts-table' } },
        h('thead', {}, h('tr', {}, ['piece', 'order', 'problem', 'attempts', 'redesign', 'terms', 'at'].map((c) => h('th', { scope: 'col' }, t(`ui.ts.col.${c}`))))),
        h('tbody', {}, shown.map((r) => h('tr', { data: { piece: pieceOf(r) } },
          h('td', {}, pieceOf(r)),
          h('td', {}, h('a', { href: to.order(project, r.profile, r.key) }, `${r.key} @ ${r.profile}`)),
          h('td', {}, r.problem || ''),
          h('td', {}, (r.attempts || []).map((id, i) => [i ? ', ' : '', h('a', { href: to.order(project, r.profile, r.key, id), data: { attempt: id } }, `q${id}`)])),
          h('td', {}, r.redesign || ''),
          h('td', {}, (r.terms || []).join(', ')),
          h('td', {}, when(r.at))))))) : h('p.empty', { data: { slot: 'ts-empty' } }, t(rows.length ? 'ui.ts.noneForPiece' : 'ui.ts.empty')));
  };
  const load = async () => {
    replace(body, h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
    try { rows = await api.troubleshootingRows(project); rows = Array.isArray(rows) ? rows : []; } catch (e) {
      replace(body, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)),
        h('button.btn', { type: 'button', data: { slot: 'ts-retry' }, onclick: load }, '↻ ', t('ui.ts.retry')));
      return;
    }
    draw();
  };
  const node = h('section.card', { aria: { labelledby: 'ts-table-h' } }, h('h2', { id: 'ts-table-h' }, t('ui.ts.tableTitle')), h('p.hint', {}, t('ui.ts.tableHint')), body);
  return { node, load };
}
