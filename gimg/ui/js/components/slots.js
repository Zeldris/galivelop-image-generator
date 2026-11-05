/* Piezas de la tarjeta de un intento que dependen de la plantilla (D39):
   - F4b: selector de plantilla por intento (GET …/profiles/{profile}/templates; POST …/compose {"template"}).
   - F4c: botón del editor de elementos (layout-editor.js; POST …/compose {"layout"}; guardar como plantilla nueva con
     destino local/proyecto, D40) y «Exportar» de las plantillas locales.
   - F4d: el botón que abre el panel «Nuevo pedido» (new-order.js). */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { paths } from '../api.js';
import { openLayoutEditor } from './layout-editor.js';
import { openNewOrder } from './new-order.js';

/** La plantilla de un intento: la de su composición (`compose.templateId`), si falló la de `composeError.templateId`,
    si no la de por defecto. Devuelve `{id, tpl}`: `tpl` es null si el id guardado ya no existe o no hay plantillas. */
export function templateOf(ctx, attempt) {
  const list = ctx.templates || [];
  const id = (attempt.compose && attempt.compose.templateId) || (attempt.composeError && attempt.composeError.templateId)
    || (list.find((x) => x.default) || {}).id || null;
  return { id, tpl: list.find((x) => x.id === id) || null };
}

/** `{x, y, w, h}` -> `x,y,w,h`, el formato de `api.measure` (una cadena ya hecha se deja). */
export function zoneParam(zone) {
  if (!zone) return undefined;
  if (typeof zone === 'string') return zone;
  return [zone.x, zone.y, zone.w, zone.h].join(',');
}

/** Lo que mide el chip de contraste de un intento: la zona y el color de su plantilla (si no los trae, los de
    `compose`; el color, en último término, el de la marca). Sin zona, solo la paleta. */
export function measureFor(ctx, attempt) {
  const { tpl } = templateOf(ctx, attempt);
  const textColor = (tpl && tpl.textColor) || ctx.measure.textColor;
  const zone = textColor ? zoneParam(tpl ? tpl.zone : ctx.measure.zone) : undefined; // zona sin color: la API responde 400
  return { ...ctx.measure, zone, textColor };
}

/** F4b: un <select> con las plantillas del perfil, marcada la del intento; solo si hay más de una. Al cambiar,
    `ctx.actions.setTemplate(attempt, id)` recompone (devuelve false si falla y entonces se vuelve a la anterior). */
export function templateSlot(ctx, attempt) {
  const list = ctx.templates || [];
  if (list.length < 2) return null;
  const { id } = templateOf(ctx, attempt);
  const known = list.some((x) => x.id === id);
  const select = h('select', { id: `template-${attempt.id}` },
    known ? null : h('option', { value: '', selected: true, disabled: true }, t('ui.attempt.templateMissing', { id: id || '—' })),
    list.map((x) => h('option', { value: x.id, selected: x.id === id }, x.default ? t('ui.attempt.templateDefault', { id: x.id }) : x.id)));
  select.addEventListener('change', async () => {
    const next = select.value;
    select.disabled = true;
    const ok = await ctx.actions.setTemplate(attempt, next);
    select.disabled = false;
    if (!ok) select.value = known ? id : '';
  });
  return h('div.slot', { data: { slot: 'template', attempt: attempt.id } },
    h('label', { for: `template-${attempt.id}` }, t('ui.attempt.template', { id: attempt.id })), select, exportLink(list.find((x) => x.id === id), ctx));
}

/** F4c: el botón «Editar composición», solo si la plantilla del intento tiene elementos y el intento está compuesto.
    Abre el editor (layout-editor.js) sobre la imagen compuesta del intento. */
export function editorSlot(ctx, attempt) {
  const { tpl } = templateOf(ctx, attempt);
  if (!tpl || !(tpl.elements || []).length || !attempt.compose || attempt.composeError) return null;
  const button = h('button.btn', { type: 'button', onclick: () => openLayoutEditor(ctx, attempt, tpl, button) }, '✎ ', t('ui.editor.open'));
  return h('div.slot', { data: { slot: 'editor', attempt: attempt.id } }, button, exportLink(tpl, ctx));
}

/** «Exportar» de una plantilla `local`: descarga su SVG (`assets/template?id=`). null si no es local. */
export function exportLink(tpl, ctx) {
  if (!tpl || tpl.source !== 'local') return null;
  return h('a.btn.btn-ghost', { href: paths.asset(ctx.project, ctx.profile, 'template', tpl.id), download: `${tpl.id}.svg`, title: t('ui.editor.exportHint', { id: tpl.id }) }, '⭳ ', t('ui.editor.export'));
}

/** F4d: el botón «Nuevo pedido» (Pedidos) o «Pedir» (Piezas, con el perfil de la pieza): abre el panel de new-order.js. */
export function newOrderButton(project, { profile = '', label = null, aria = null, primary = true } = {}) {
  const button = h(primary ? 'button.btn.btn-primary' : 'button.btn', {
    type: 'button', aria: { label: aria }, data: { slot: 'new-order', profile },
    onclick: () => openNewOrder(project, { profile, opener: button }),
  }, '＋ ', label || t('ui.newOrder.button'));
  return button;
}
