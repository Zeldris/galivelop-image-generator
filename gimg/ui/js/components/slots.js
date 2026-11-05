/* Huecos para las fases siguientes (D39). Cada uno es un componente con la misma firma que tendrá después, para que la
   tarjeta y el panel no cambien de forma cuando lleguen:
   - F4b: selector de plantilla por intento (GET …/profiles/{profile}/templates; POST …/compose {"template"}).
   - F4c: editor de elementos (mover y redimensionar titular, subtítulo, logo y adornos; POST …/compose {"layout"};
     guardar como plantilla nueva con destino local/proyecto, D40). */

import { h } from '../dom.js';
import { t } from '../i18n.js';

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
    h('label', { for: `template-${attempt.id}` }, t('ui.attempt.template', { id: attempt.id })), select);
}

/** F4c: aquí irá el botón que abre el editor sobre la imagen del intento. */
export function editorSlot(attempt) {
  return h('div.slot', { data: { slot: 'editor', attempt: attempt.id } }, h('span.chip', {}, 'F4c'), t('ui.attempt.editSoon'));
}

/** F4d: panel «Nuevo pedido» desde Piezas o Pedidos (POST /api/projects/{p}/orders ya existe en F3). */
export function newOrderSlot() {
  return h('div.slot', { data: { slot: 'new-order' } }, h('span.chip', {}, 'F4d'), t('ui.project.newOrderSoon'));
}
