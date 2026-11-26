/* Lo que el pedido de marca (0.8.0) añade a la pantalla del pedido, a la lista de pedidos y a las tarjetas: el distintivo
   Marca / Libre, el marcador «Fallos 2 de 3 ■■□» (siempre con texto), el aviso al penúltimo fallo, el motivo de un pedido
   bloqueado en troubleshooting y los motivos de un «No» o un «Ninguno vale» (rasgos de la hoja + «otro»).
   Todo lee lo que da GET …/orders/{profile}/{key}: `mode`, `failures: {count, limit, reasons}`, `troubleshooting: {state}`,
   `modeChanges`, `batches`. La lista de pedidos (GET …/orders) trae el pedido tal cual está guardado: sin `failures` vale 0 de 3. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { loc } from './sheet-view.js';

export const isBrand = (order) => Boolean(order) && order.mode === 'brand';

/** Distintivo «Marca» / «Libre». */
export function modeBadge(mode) {
  const brand = mode === 'brand';
  return h('span.chip', { class: brand ? 'chip-accent' : '', data: { mode: brand ? 'brand' : 'free' } }, t(brand ? 'ui.mode.brand' : 'ui.mode.free'));
}

/** Sujeto y zona limpia de LA TANDA de un intento o entrada (`x.batch`: id u objeto con `id`), según `order.batches[]`;
    sin tanda, o sin sujeto en su registro, los del pedido. */
export function batchSpecOf(order, x) {
  const b = x && x.batch !== null && x.batch !== undefined && typeof x.batch === 'object' ? x.batch.id : x && x.batch;
  const rec = b === null || b === undefined ? null : (order.batches || []).find((r) => r.id === b);
  if (rec && typeof rec.subject === 'string') return { subject: rec.subject, cleanZone: rec.cleanZone || '' };
  return { subject: order.subject || '', cleanZone: order.cleanZone || '' };
}

/** {count, limit, reasons} de un pedido, con los valores por omisión de la API. */
export function failuresOf(order) {
  const f = (order && order.failures) || {};
  return { count: Number.isFinite(f.count) ? f.count : 0, limit: Number.isFinite(f.limit) && f.limit > 0 ? f.limit : 3, reasons: Array.isArray(f.reasons) ? f.reasons : [] };
}

/** Pedido de marca en troubleshooting: sus botones que encolan quedan apagados. */
export const isBlocked = (order) => isBrand(order) && Boolean(order.troubleshooting) && order.troubleshooting.state === 'blocked';

/** Texto de por qué no se puede encolar, o null. */
export function blockedReason(order) {
  if (!isBlocked(order)) return null;
  const f = failuresOf(order);
  return t('ui.fail.blocked', { count: f.count, limit: f.limit });
}

/** «Fallos 2 de 3 ■■□», o null si no es de marca o no hay fallos. */
export function failureMarker(order) {
  if (!isBrand(order)) return null;
  const f = failuresOf(order);
  if (!f.count) return null;
  const text = t('ui.fail.marker', { count: f.count, limit: f.limit });
  const squares = '■'.repeat(Math.min(f.count, f.limit)) + '□'.repeat(Math.max(0, f.limit - f.count));
  return h('span.chip.fail-marker', { class: f.count >= f.limit ? 'chip-bad' : 'chip-warn', data: { failures: f.count, limit: f.limit }, title: text },
    text, ' ', h('span', { aria: { hidden: true } }, squares));
}

/** Etiqueta de un rasgo: «otro», el rótulo de la hoja (`acceptance.unmeasured`) o el propio id. */
export function traitLabel(sheet, trait) {
  if (trait === 'other') return t('ui.reason.other');
  const un = ((sheet && sheet.acceptance && sheet.acceptance.unmeasured) || []).find((u) => u.id === trait);
  return (un && loc(un.label)) || trait;
}

/** Los motivos que se pueden elegir: los rasgos no medidos de la hoja, los medidos y «otro» (que pide una nota). */
export function reasonChoices(sheet) {
  const acceptance = (sheet && sheet.acceptance) || {};
  const out = [];
  const seen = new Set();
  for (const u of acceptance.unmeasured || []) if (u && u.id && !seen.has(u.id)) { seen.add(u.id); out.push({ trait: u.id, label: loc(u.label) || u.id }); }
  const traits = acceptance.traits;
  for (const id of Array.isArray(traits) ? traits.map((x) => (x && x.id) || x) : Object.keys(traits || {})) if (id && !seen.has(id)) { seen.add(id); out.push({ trait: id, label: id }); }
  out.push({ trait: 'other', label: t('ui.reason.other') });
  return out;
}

/** «horizonte ×2, paleta» a partir de los motivos guardados. */
export function reasonsText(reasons, sheet) {
  const counts = new Map();
  for (const r of reasons || []) {
    const label = r.trait === 'other' && r.text ? r.text : traitLabel(sheet, r.trait || 'other');
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return [...counts].map(([label, n]) => (n > 1 ? `${label} ×${n}` : label)).join(', ');
}

/** Aviso suave al penúltimo fallo, o null. */
export function failureNotice(order, sheet) {
  if (!isBrand(order) || isBlocked(order)) return null;
  const f = failuresOf(order);
  if (f.count < 1 || f.count !== f.limit - 1) return null;
  const why = reasonsText(f.reasons, sheet);
  return h('p.notice.notice-warn', { role: 'status', data: { slot: 'fail-notice' } }, t('ui.fail.warn'), why ? ` ${t('ui.fail.reasons', { reasons: why })}` : '');
}

/** Aviso de que el pedido pasó a libre (`modeChanges` lo apunta), o null. */
export function modeChangeNotice(order) {
  const changes = (order && order.modeChanges) || [];
  const last = changes[changes.length - 1];
  if (!last || last.to !== 'free') return null;
  return h('p.hint', { data: { slot: 'mode-change' } }, t('ui.mode.toFreeNotice'));
}
