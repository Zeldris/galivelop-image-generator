/* Huecos para las fases siguientes (D39). Cada uno es un componente con la misma firma que tendrá después, para que la
   tarjeta y el panel no cambien de forma cuando lleguen:
   - F4b: selector de plantilla por intento (GET …/profiles/{profile}/templates; POST …/compose {"template"}).
   - F4c: editor de elementos (mover y redimensionar titular, subtítulo, logo y adornos; POST …/compose {"layout"};
     guardar como plantilla nueva con destino local/proyecto, D40). */

import { h } from '../dom.js';
import { t } from '../i18n.js';

/** F4b: aquí irá un <select> con las plantillas del perfil y la del intento (`attempt.compose.template`). */
export function templateSlot(attempt) {
  return h('div.slot', { data: { slot: 'template', attempt: attempt.id } }, h('span.chip', {}, 'F4b'), t('ui.attempt.templateSoon'));
}

/** F4c: aquí irá el botón que abre el editor sobre la imagen del intento. */
export function editorSlot(attempt) {
  return h('div.slot', { data: { slot: 'editor', attempt: attempt.id } }, h('span.chip', {}, 'F4c'), t('ui.attempt.editSoon'));
}

/** F4d: panel «Nuevo pedido» desde Piezas o Pedidos (POST /api/projects/{p}/orders ya existe en F3). */
export function newOrderSlot() {
  return h('div.slot', { data: { slot: 'new-order' } }, h('span.chip', {}, 'F4d'), t('ui.project.newOrderSoon'));
}
