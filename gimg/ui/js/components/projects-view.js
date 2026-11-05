/* Pantalla de proyectos: GET /api/projects. Un proyecto que no carga (configuración rota) se muestra con su error y
   sin enlace, como hace `gimg doctor`. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError } from '../api.js';
import { to } from '../router.js';
import { newOrderSlot } from './slots.js';

export async function projectsView(host) {
  host.append(h('div.page-head', {}, h('h1', {}, t('ui.projects.title'))), h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
  let list;
  try {
    const res = await api.projects();
    list = Array.isArray(res) ? res : (res && res.projects) || [];
  } catch (e) {
    host.replaceChildren(h('div.page-head', {}, h('h1', {}, t('ui.projects.title'))), h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)));
    return;
  }
  host.replaceChildren(
    h('div.page-head', {}, h('h1', {}, t('ui.projects.title')), h('span.hint', {}, t('ui.projects.count', { n: list.length }))),
    list.length ? h('div.project-grid', {}, list.map(card)) : h('div.empty', {}, h('p', {}, t('ui.projects.empty')), h('code.mono', {}, 'gimg project add <ruta>')),
    h('p.hint', {}, t('ui.projects.hint')),
    newOrderSlot());
}

function card(p) {
  const name = p.name || p.id || '?';
  const broken = Boolean(p.error);
  const body = [
    h('h2', {}, name),
    h('span.path', { title: p.root || '' }, p.root || ''),
    broken ? h('span.chip.chip-bad', {}, t('ui.projects.broken')) : h('div.meta', {},
      Number.isFinite(p.orders) ? h('span', {}, t('ui.projects.orders', { n: p.orders })) : null,
      Number.isFinite(p.chosen) ? h('span', {}, t('ui.projects.chosen', { n: p.chosen })) : null,
      Array.isArray(p.profiles) ? h('span', {}, p.profiles.join(' · ')) : null),
    broken ? h('div.mono.small', {}, p.error.message || p.error.code || String(p.error)) : null,
  ];
  return broken
    ? h('div.card.project-card.is-broken', { aria: { label: `${name}: ${t('ui.projects.broken')}` } }, body)
    : h('a.card.project-card', { href: to.project(name) }, body);
}
