/* Pestaña Piezas (F4d, D22): en gimg una pieza es un perfil del proyecto. Con una hoja de marca válida (0.7.0) hay una
   tarjeta por tipo de pieza, con la tarjeta de su perfil dentro, y debajo los perfiles sin tipo («Pedir» en modo libre). Cada tarjeta enseña los tamaños (generación y
   destino), el ajuste (`compose.fit`), el modelo, los campos de texto, las plantillas con su miniatura (el SVG por
   `assets/template?id=`), cuántos pedidos tiene y cuántos están entregados, un «Pedir» que abre el panel con ese perfil
   y un enlace a sus pedidos. Plantillas y pedidos se piden por perfil; si una petición falla, la tarjeta sale sin ese dato. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths } from '../api.js';
import { to } from '../router.js';
import * as store from '../store.js';
import { newOrderButton } from './slots.js';
import { loc } from './sheet-view.js';

export async function piecesTab(panel, project, cfg, info = {}) {
  const names = Object.keys(cfg.profiles || {});
  panel.append(h('p.hint', {}, t('ui.pieces.hint')));
  if (!names.length) { panel.append(h('div.empty', {}, h('p', {}, t('ui.newOrder.noProfiles')))); return; }
  const types = info.sheet && info.sheet.valid ? (info.pieceTypes || []) : [];
  const typed = new Set(types.map((p) => p.profile).filter(Boolean));
  const loose = types.length ? names.filter((n) => !typed.has(n)) : names;
  const data = new Map(); // perfil -> {templates, orders}, pedido una sola vez aunque lo usen varios tipos
  const dataOf = (name) => {
    if (!data.has(name)) {
      data.set(name, Promise.all([
        api.templates(project, name).catch(() => []),
        api.orders(project, { profile: name }).catch(() => []),
      ]));
    }
    return data.get(name);
  };
  const slot = (name) => h('div.card.piece-card', { data: { profile: name } },
    h('h2', {}, name), h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
  const fill = async (node, name) => {
    const [templates, orders] = await dataOf(name);
    node.replaceWith(card(project, name, (cfg.profiles || {})[name] || {}, Array.isArray(templates) ? templates : [],
      Array.isArray(orders) ? orders : (orders && orders.orders) || []));
  };
  const jobs = [];
  const grids = [];
  if (types.length) {
    const grid = h('div.piece-grid', { aria: { busy: 'true' } }, types.map((pt) => {
      const known = pt.profile && names.includes(pt.profile);
      const inner = known ? slot(pt.profile) : null;
      if (inner) jobs.push(fill(inner, pt.profile));
      return h('section.card.piece-type', { data: { piece: pt.id }, aria: { labelledby: `pt-${pt.id}` } },
        h('div.row-between', {}, h('h2', { id: `pt-${pt.id}` }, loc(pt.label) || pt.id),
          h('span.row', {}, h('code.mono.hint', {}, pt.id), pt.register ? h('span.chip', {}, pt.register) : null)),
        inner || h('p.hint', {}, t('ui.pieces.profileMissing', { profile: pt.profile || '—' })));
    }));
    grids.push(grid);
    panel.append(grid);
  }
  if (loose.length) {
    if (types.length) panel.append(h('h2', { id: 'pieces-loose' }, t('ui.pieces.loose')), h('p.hint', {}, t('ui.pieces.looseHint')));
    const grid = h('div.piece-grid', { aria: { busy: 'true' }, data: { group: 'loose' } }, loose.map((name) => {
      const node = slot(name);
      jobs.push(fill(node, name));
      return node;
    }));
    grids.push(grid);
    panel.append(grid);
  }
  await Promise.all(jobs);
  for (const g of grids) g.setAttribute('aria-busy', 'false');
}

function card(project, name, p, templates, orders) {
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
        h('span', {}, x.default ? t('ui.attempt.templateDefault', { id: x.id }) : x.id))))
      : h('p.hint', {}, t('ui.pieces.noTemplates')),
    h('div.row-between', {},
      h('span.hint', {}, t('ui.pieces.orders', { n: orders.length, c: delivered })),
      h('a.btn.btn-ghost', { href: to.project(project, 'pedidos'), onclick: () => store.set('filters', { ...store.get('filters'), [project]: { profile: name, state: '' } }) }, t('ui.pieces.seeOrders'))));
}
