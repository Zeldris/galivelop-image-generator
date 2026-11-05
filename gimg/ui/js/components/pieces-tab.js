/* Pestaña Piezas (F4d, D22): en gimg una pieza es un perfil del proyecto. Cada tarjeta enseña los tamaños (generación y
   destino), el ajuste (`compose.fit`), el modelo, los campos de texto, las plantillas con su miniatura (el SVG por
   `assets/template?id=`), cuántos pedidos tiene y cuántos están entregados, un «Pedir» que abre el panel con ese perfil
   y un enlace a sus pedidos. Plantillas y pedidos se piden por perfil; si una petición falla, la tarjeta sale sin ese dato. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import { to } from '../router.js';
import * as store from '../store.js';
import { newOrderButton } from './slots.js';
import { confirmAction } from './confirm.js';
import { toastError, toastOk } from './toast.js';

export async function piecesTab(panel, project, cfg) {
  const names = Object.keys(cfg.profiles || {});
  panel.append(h('p.hint', {}, t('ui.pieces.hint')));
  if (!names.length) { panel.append(h('div.empty', {}, h('p', {}, t('ui.newOrder.noProfiles')))); return; }
  const grid = h('div.piece-grid', { aria: { busy: 'true' } }, names.map((name) => h('div.card.piece-card', { data: { profile: name } },
    h('h2', {}, name), h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')))));
  panel.append(grid);
  const load = async (name, i) => {
    const [templates, orders] = await Promise.all([
      api.templates(project, name).catch(() => []),
      api.orders(project, { profile: name }).catch(() => []),
    ]);
    grid.children[i].replaceWith(card(project, name, (cfg.profiles || {})[name] || {}, Array.isArray(templates) ? templates : [],
      Array.isArray(orders) ? orders : (orders && orders.orders) || [], () => load(name, i)));
  };
  await Promise.all(names.map(load));
  grid.setAttribute('aria-busy', 'false');
}

/** F4e.1: borrar una plantilla. Antes de confirmar pregunta al servidor (GET) cuántos intentos la usan y si es del repo. */
async function deleteTemplate(project, profile, x, reload, opener) {
  let info;
  try { info = await api.template(project, profile, x.id); } catch (e) { toastError(describeError(e, t)); return; }
  const used = info.usedBy > 1 ? t('ui.pieces.deleteUsed', { n: info.usedBy }) : info.usedBy === 1 ? t('ui.pieces.deleteUsedOne') : t('ui.pieces.deleteUnused');
  const ok = await confirmAction({ title: t('ui.pieces.deleteTitle', { id: x.id }),
    message: [used, info.inRepo ? t('ui.pieces.deleteInRepo') : ''].filter(Boolean).join(' '),
    confirmLabel: t('ui.pieces.deleteConfirm'), opener });
  if (!ok) return;
  try {
    await api.deleteTemplate(project, profile, x.id);
    toastOk(t('ui.pieces.deleted', { id: x.id }));
  } catch (e) { toastError(describeError(e, t)); }
  await reload();
}

function card(project, name, p, templates, orders, reload) {
  const compose = p.compose || {};
  const fields = compose.fields || [];
  const delivered = orders.filter((o) => o.chosen !== null && o.chosen !== undefined).length;
  const sizes = [
    p.width ? h('span.chip', {}, t('ui.pieces.generation', { w: p.width, h: p.height })) : null,
    p.targetWidth ? h('span.chip', {}, t('ui.pieces.target', { w: p.targetWidth, h: p.targetHeight })) : null,
    compose.fit ? h('span.chip', {}, t('ui.pieces.fit', { fit: compose.fit })) : null,
    p.model ? h('span.chip.mono', {}, t('ui.pieces.model', { id: p.model })) : null,
  ];
  return h('div.card.piece-card', { data: { profile: name } },
    h('div.row-between', {}, h('h2', {}, name), newOrderButton(project, { profile: name, label: t('ui.pieces.order'), aria: t('ui.pieces.orderAria', { profile: name }) })),
    h('div.row', {}, sizes),
    h('h3', {}, t('ui.pieces.fields')),
    fields.length ? h('div.row', {}, fields.map((f) => h('code.mono', {}, f))) : h('p.hint', {}, t('ui.pieces.noFields')),
    h('h3', {}, t('ui.pieces.templates')),
    templates.length
      ? h('ul.tpl-list', {}, templates.map((x) => h('li.tpl', {},
        h('img.tpl-thumb', { src: paths.asset(project, name, 'template', x.id), alt: '', loading: 'lazy' }),
        h('span', {}, x.default ? t('ui.attempt.templateDefault', { id: x.id }) : x.id),
        h('button.btn.btn-danger', { type: 'button', data: { fid: `delete-template-${name}-${x.id}` }, disabled: Boolean(x.default),
          title: x.default ? t('ui.pieces.deleteDefaultHint') : null, aria: { label: t('ui.pieces.deleteAria', { id: x.id }) },
          onclick: (ev) => deleteTemplate(project, name, x, reload, ev.currentTarget) }, t('ui.pieces.delete')))))
      : h('p.hint', {}, t('ui.pieces.noTemplates')),
    h('div.row-between', {},
      h('span.hint', {}, t('ui.pieces.orders', { n: orders.length, c: delivered })),
      h('a.btn.btn-ghost', { href: to.project(project, 'pedidos'), onclick: () => store.set('filters', { ...store.get('filters'), [project]: { profile: name, state: '' } }) }, t('ui.pieces.seeOrders'))));
}
