/* Pestaña Marca (F4d, D22; 0.7.0 §2.10), de solo lectura, en subpestañas `?s=hoja|probar|check|taller`:
   - Hoja: la hoja de marca resuelta (sheet-view.js); sin hoja, el aviso con cómo crearla y la marca de la configuración.
   - Probar un sujeto: monta el prompt de un tipo de pieza y comprueba un prompt libre (brand-prompt.js), sin encolar.
   - Comprobación: GET /api/projects/{p}/check -> [{id, status: ok|warn|fail, message, fix?}], las de `gimg doctor` que le
     tocan (con hoja, también las filas `sheet.*`). El estado va siempre en texto además del color.
   - Taller: el sistema de logo de siempre (brand-workshop.js).
   Las subpestañas son un `role="tablist"` con ←/→; cada panel se construye al abrirlo y se conserva. La subpestaña
   activa vive en la consulta del hash (se cambia sin repintar la pantalla). Por defecto, Taller con `?src=` (el enlace
   de un intento), si no Hoja si el proyecto tiene hoja y, si no, Comprobación. */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError } from '../api.js';
import { brandWorkshop } from './brand-workshop.js';
import { brandFacts } from './brand-facts.js';
import { sheetView } from './sheet-view.js';
import { brandPrompt } from './brand-prompt.js';

const STATUS_CHIP = { ok: 'chip-ok', warn: 'chip-warn', fail: 'chip-bad' };
export const SUBTABS = ['hoja', 'probar', 'check', 'taller'];

/** Cambia `?s=` del hash sin disparar `hashchange` (la pantalla no se repinta). */
function rememberSub(sub) {
  const [path, query = ''] = location.hash.replace(/^#/, '').split('?');
  const params = new URLSearchParams(query);
  params.set('s', sub);
  history.replaceState(null, '', `#${path}?${params}`);
}

export async function brandTab(panel, project, cfg, info = {}, query = {}) {
  const sheet = info.sheet || { present: false, valid: false, errors: [] };
  const first = SUBTABS.includes(query.s) ? query.s : (query.src ? 'taller' : sheet.present ? 'hoja' : 'check'); // `?src=` es del taller
  const bodies = {};
  const builders = {
    hoja: (host) => (sheet.present ? sheetView(host, project, cfg, info) : noSheet(host, project, cfg)),
    probar: (host) => (sheet.present && sheet.valid ? brandPrompt(host, project, info.pieceTypes || []) : host.append(unavailable(project, sheet))),
    check: (host) => checkPanel(host, project),
    taller: (host) => host.append(brandWorkshop(project, cfg)),
  };
  const built = new Set();
  const tabs = SUBTABS.map((s) => h('button', {
    type: 'button', role: 'tab', id: `sub-${s}`, data: { sub: s }, aria: { controls: `subpanel-${s}`, selected: 'false' }, tabindex: '-1',
    onclick: () => select(s),
    onkeydown: (e) => {
      const i = SUBTABS.indexOf(s);
      const to = e.key === 'ArrowRight' ? (i + 1) % SUBTABS.length : e.key === 'ArrowLeft' ? (i + SUBTABS.length - 1) % SUBTABS.length
        : e.key === 'Home' ? 0 : e.key === 'End' ? SUBTABS.length - 1 : -1;
      if (to < 0) return;
      e.preventDefault();
      select(SUBTABS[to], true);
    },
  }, t(`ui.brand.sub.${s}`)));
  for (const s of SUBTABS) {
    bodies[s] = h('div.stack', { role: 'tabpanel', id: `subpanel-${s}`, tabindex: '0', hidden: true, aria: { labelledby: `sub-${s}` } });
  }
  panel.append(h('div.stack', {},
    h('p.hint', {}, t('ui.brand.hint')),
    h('div.tabs', { role: 'tablist', aria: { label: t('ui.brand.sub.label') } }, tabs),
    SUBTABS.map((s) => bodies[s])));

  let pending = null;
  function select(s, focus = false) {
    SUBTABS.forEach((x, i) => {
      const on = x === s;
      tabs[i].setAttribute('aria-selected', on ? 'true' : 'false');
      tabs[i].tabIndex = on ? 0 : -1;
      bodies[x].hidden = !on;
    });
    if (focus) tabs[SUBTABS.indexOf(s)].focus();
    rememberSub(s);
    if (!built.has(s)) { built.add(s); pending = Promise.all([pending, builders[s](bodies[s])]); }
    return pending;
  }
  rememberSub(first);
  await select(first);
}

function unavailable(project, sheet) {
  return h('div.stack', {},
    h('p.notice.notice-warn', { role: 'status' }, sheet.present ? t('ui.sheet.invalid') : t('ui.brand.noSheet.title')),
    sheet.present ? null : h('code.mono', {}, `gimg brand init ${project}`));
}

/** Sin hoja: el aviso, cómo crearla y la marca de la configuración como siempre. */
async function noSheet(host, project, cfg) {
  const facts = brandFacts(project, cfg);
  host.append(
    h('div.card', { data: { card: 'no-sheet' } }, h('h2', {}, t('ui.brand.noSheet.title')),
      h('p', {}, t('ui.brand.noSheet.how')), h('code.mono', {}, `gimg brand init ${project}`)),
    facts.node);
  await facts.load();
}

async function checkPanel(host, project) {
  const checkHost = h('div.stack', { aria: { live: 'polite' } });
  async function runCheck() {
    replace(checkHost, h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
    let list;
    try { list = await api.check(project); } catch (e) {
      replace(checkHost, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t)));
      return;
    }
    list = Array.isArray(list) ? list : [];
    const count = (s) => list.filter((c) => c.status === s).length;
    replace(checkHost,
      list.length ? h('p', {}, h('b', {}, t('ui.check.summary', { ok: count('ok'), warn: count('warn'), fail: count('fail') }))) : h('p.hint', {}, t('ui.check.none')),
      list.length ? h('ul.check-list', {}, list.map((c) => h('li.check-item', { class: `is-${c.status}` },
        h('span.chip', { class: STATUS_CHIP[c.status] || '' }, t(`ui.check.${c.status}`)),
        h('div', {}, h('div', {}, c.message || c.id), h('code.mono.hint', {}, c.id),
          c.fix ? h('div.hint', {}, t('ui.check.fix'), ' ', h('code.mono', {}, c.fix)) : null)))) : null);
  }
  host.append(h('section.card', { aria: { labelledby: 'check-h' } },
    h('div.row-between', {}, h('h2', { id: 'check-h' }, t('ui.check.title')),
      h('button.btn', { type: 'button', onclick: () => runCheck() }, '↻ ', t('ui.check.run'))),
    checkHost));
  await runCheck();
}
