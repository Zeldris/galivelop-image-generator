/* Textos de la composición (D28, por pedido: decisión 4 de propuesta.md): un campo por `compose.fields` del perfil,
   PUT …/o/text al guardar y «Recomponer la elegida» (POST …/a/{id}/compose sin generar). La previsualización HTML se
   quitó en F4c: la sustituye el editor de elementos (layout-editor.js). */

import { h } from '../dom.js';
import { t, fieldLabel } from '../i18n.js';

export function textPanel(ctx, { onSave, onRecompose }) {
  // la unión (sin repetidos, en orden) de los campos del perfil y de los de todas sus plantillas
  const fields = [...new Set([...((ctx.profileCfg.compose && ctx.profileCfg.compose.fields) || []), ...(ctx.templates || []).flatMap((x) => x.fields || [])])];
  const saved = { ...(ctx.order.text || {}) };
  if (!fields.length) {
    return { node: h('section.card', {}, h('h2', {}, t('ui.text.title')), h('p.hint', {}, t('ui.text.noFields'))), values: () => ({}), setChosen() {} };
  }
  const inputs = new Map();
  const dirty = h('span.dirty', { hidden: true }, t('ui.text.dirty'));
  const values = () => Object.fromEntries([...inputs].map(([k, el]) => [k, el.value]));
  const isDirty = () => fields.some((f) => (saved[f] || '') !== (inputs.get(f).value || ''));
  const onInput = () => { dirty.hidden = !isDirty(); };

  const rows = fields.map((f) => {
    const id = `text-${f}`;
    const input = h('input', { type: 'text', id, value: saved[f] || '', maxlength: 200, oninput: onInput });
    inputs.set(f, input);
    return h('div.field', {}, h('label', { for: id }, fieldLabel(f)), input);
  });

  const save = h('button.btn.btn-primary', { type: 'button', onclick: async () => {
    const v = values();
    if (await onSave(v)) { Object.assign(saved, v); dirty.hidden = true; }
  } }, t('ui.text.save'));
  let chosen = ctx.order.chosen;
  const recompose = h('button.btn', { type: 'button', disabled: chosen === null || chosen === undefined, onclick: () => onRecompose(chosen) }, '⟳ ', t('ui.text.recompose'));

  const node = h('section.card', { aria: { labelledby: 'text-h' } },
    h('h2', { id: 'text-h' }, t('ui.text.title'), ' ', dirty),
    rows,
    h('div.panel-actions', {}, save, recompose),
    h('p.hint', {}, t('ui.text.hint')));
  /** Elegir o deshacer cambia solo este botón: el panel (y lo escrito en él) no se reconstruye. */
  const setChosen = (id) => { chosen = id; recompose.disabled = id === null || id === undefined; };
  return { node, values, isDirty, setChosen };
}
