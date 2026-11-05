/* Pantalla de un proyecto: pestañas Pedidos (lista con filtros por perfil y estado) y Piezas / Marca («próximamente»,
   F4d: la pieza como índice de pedidos, D21/D37). Usa GET /api/projects/{p} (config: perfiles, marca) y
   GET /api/projects/{p}/orders?profile=&chosen=. */

import { h, when } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import { to } from '../router.js';
import * as store from '../store.js';
import { newOrderSlot } from './slots.js';

const TABS = ['pedidos', 'piezas', 'marca'];

export async function projectView(host, route) {
  const { project, tab } = route;
  host.append(h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
  let info;
  try { info = await api.project(project); } catch (e) {
    host.replaceChildren(h('h1', {}, project), h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)));
    return;
  }
  const cfg = info.config || {};
  const profiles = Object.keys(cfg.profiles || {});
  host.replaceChildren(
    h('div.page-head', {}, h('h1', {}, info.name || project), h('span.path.hint', { title: info.root }, info.root)),
    h('nav.tabs', { aria: { label: t('ui.project.tabs') } }, TABS.map((tb) =>
      h('a', { href: to.project(project, tb), aria: { current: tb === tab ? 'page' : null } }, t(`ui.project.tab.${tb}`)))),
    h('section', { id: 'tab-panel', aria: { label: t(`ui.project.tab.${tab}`) } }));
  const panel = host.querySelector('#tab-panel');
  if (tab === 'pedidos') await ordersTab(panel, project, profiles, cfg);
  else if (tab === 'piezas') panel.append(h('div.empty', {}, h('p', {}, t('ui.project.piecesSoon')), h('p.hint', {}, t('ui.project.piecesHint'))), newOrderSlot());
  else panel.append(brandTab(cfg));
}

async function ordersTab(panel, project, profiles, cfg) {
  const saved = store.get('filters')[project] || { profile: '', state: '' };
  const profileSel = h('select', { id: 'f-profile', value: saved.profile },
    h('option', { value: '' }, t('ui.project.filter.allProfiles')), profiles.map((p) => h('option', { value: p, selected: p === saved.profile }, p)));
  const stateSel = h('select', { id: 'f-state', value: saved.state },
    ['', 'pending', 'chosen'].map((s) => h('option', { value: s, selected: s === saved.state }, t(`ui.project.filter.${s || 'allStates'}`))));
  const list = h('div.order-list', { aria: { live: 'polite', busy: 'true' } });
  const count = h('span.hint');
  const load = async () => {
    const f = { profile: profileSel.value, state: stateSel.value };
    store.set('filters', { ...store.get('filters'), [project]: f });
    list.setAttribute('aria-busy', 'true');
    list.replaceChildren(h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
    try {
      const res = await api.orders(project, { profile: f.profile, chosen: f.state === 'chosen' ? 1 : f.state === 'pending' ? 0 : undefined });
      const orders = Array.isArray(res) ? res : (res && res.orders) || [];
      orders.sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')));
      count.textContent = t('ui.project.orderCount', { n: orders.length });
      list.replaceChildren(orders.length ? orders.map((o) => row(project, o, cfg)) : h('div.empty', {}, h('p', {}, t('ui.project.noOrders')), h('code.mono', {}, `gimg order submit ${project} <clave> --profile <perfil>`)));
    } catch (e) {
      list.replaceChildren(h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)));
    }
    list.setAttribute('aria-busy', 'false');
  };
  profileSel.addEventListener('change', load);
  stateSel.addEventListener('change', load);
  panel.append(
    h('div.filters', {},
      h('div.field', {}, h('label', { for: 'f-profile' }, t('ui.project.filter.profile')), profileSel),
      h('div.field', {}, h('label', { for: 'f-state' }, t('ui.project.filter.state')), stateSel),
      count),
    list, newOrderSlot());
  await load();
}

function row(project, o, cfg) {
  const n = (o.attempts && (Array.isArray(o.attempts) ? o.attempts.length : o.attempts)) || o.attemptCount || 0;
  const chosen = o.chosen !== null && o.chosen !== undefined;
  const pending = store.queueOf(project, o.profile, o.key).filter((e) => e.state === 'queued' || e.state === 'running').length;
  const thumbId = chosen ? o.chosen : (o.lastAttempt ?? (Array.isArray(o.attempts) && o.attempts.length ? o.attempts[o.attempts.length - 1].id : null));
  const thumb = thumbId !== null && thumbId !== undefined
    ? h('img.thumb', { src: paths.image(project, o.profile, o.key, thumbId), alt: '', loading: 'lazy' })
    : h('div.thumb-empty', {}, '—');
  const prof = (cfg.profiles || {})[o.profile] || {};
  return h('a.card.order-row', { href: to.order(project, o.profile, o.key), aria: { label: `${o.key} @ ${o.profile}` } },
    thumb,
    h('div', {}, h('div.key', {}, o.key), h('div.meta', {},
      h('span', {}, o.profile, prof.width ? ` · ${prof.width}×${prof.height}` : ''),
      h('span', {}, t('ui.project.attempts', { n })),
      pending ? h('span.chip.chip-accent', {}, t('ui.project.pending', { n: pending })) : null,
      o.updatedAt ? h('span', {}, when(o.updatedAt)) : null)),
    chosen ? h('span.chip.chip-ok', {}, `★ ${t('ui.state.chosen')} q${o.chosen}`) : h('span.chip', {}, t('ui.project.filter.pending')));
}

function brandTab(cfg) {
  const brand = cfg.brand || {};
  const palette = brand.palette || [];
  return h('div.stack', {},
    h('div.empty', {}, h('p', {}, t('ui.project.brandSoon')), h('p.hint', {}, t('ui.project.brandHint'))),
    palette.length ? h('div.card', {}, h('h2', {}, t('ui.project.palette')), h('div.swatches', {}, palette.map((c) =>
      h('span.swatch', { title: c, vars: { sw: c }, role: 'img', aria: { label: c } })))) : null);
}
