/* Textos de la composición (D28, por pedido: decisión 4 de propuesta.md): un campo por `compose.fields` del perfil,
   PUT …/o/text al guardar, «Recomponer la elegida» (POST …/a/{id}/compose sin generar) y una previsualización
   inmediata (superposición HTML sobre los intentos) mientras se escribe. Color, velo y zona no están en el esquema del
   pedido hoy (solo `compose.fields`): llegan con la plantilla (F4b) y el editor (F4c). */

import { h } from '../dom.js';
import { t, fieldLabel } from '../i18n.js';

export function textPanel(ctx, { onSave, onRecompose, onPreview }) {
  const fields = (ctx.profileCfg.compose && ctx.profileCfg.compose.fields) || [];
  const saved = { ...(ctx.order.text || {}) };
  if (!fields.length) {
    return { node: h('section.card', {}, h('h2', {}, t('ui.text.title')), h('p.hint', {}, t('ui.text.noFields'))), values: () => ({}) };
  }
  const inputs = new Map();
  const dirty = h('span.dirty', { hidden: true }, t('ui.text.dirty'));
  const preview = h('input', { type: 'checkbox', checked: ctx.previewText });
  const values = () => Object.fromEntries([...inputs].map(([k, el]) => [k, el.value]));
  const isDirty = () => fields.some((f) => (saved[f] || '') !== (inputs.get(f).value || ''));
  const onInput = () => { dirty.hidden = !isDirty(); if (preview.checked) onPreview(values()); };

  const rows = fields.map((f) => {
    const id = `text-${f}`;
    const input = h('input', { type: 'text', id, value: saved[f] || '', maxlength: 200, oninput: onInput });
    inputs.set(f, input);
    return h('div.field', {}, h('label', { for: id }, fieldLabel(f)), input);
  });
  preview.addEventListener('change', () => onPreview(preview.checked ? values() : null));

  const save = h('button.btn.btn-primary', { type: 'button', onclick: async () => {
    const v = values();
    if (await onSave(v)) { Object.assign(saved, v); dirty.hidden = true; }
  } }, t('ui.text.save'));
  const chosen = ctx.order.chosen;
  const recompose = h('button.btn', { type: 'button', disabled: chosen === null || chosen === undefined, onclick: () => onRecompose(chosen) }, '⟳ ', t('ui.text.recompose'));

  const node = h('section.card', { aria: { labelledby: 'text-h' } },
    h('h2', { id: 'text-h' }, t('ui.text.title'), ' ', dirty),
    rows,
    h('label.check', {}, preview, h('span', {}, t('ui.text.preview'))),
    h('div.panel-actions', {}, save, recompose),
    h('p.hint', {}, t('ui.text.hint')));
  return { node, values, isDirty };
}
