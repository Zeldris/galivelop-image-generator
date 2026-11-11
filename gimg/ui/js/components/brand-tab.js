/* Pestaña Marca (F4d, D22), de solo lectura: paleta, color del texto, mínimo de paleta, palabras vetadas, fuentes (las
   de `compose.fonts` de cada perfil) y logos (los de las plantillas, con su miniatura), y debajo la comprobación del
   proyecto: GET /api/projects/{p}/check -> [{id, status: ok|warn|fail, message, fix?}], las de `gimg doctor` que le
   tocan. El estado va siempre en texto además del color. */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import { brandWorkshop } from './brand-workshop.js';

const STATUS_CHIP = { ok: 'chip-ok', warn: 'chip-warn', fail: 'chip-bad' };

export async function brandTab(panel, project, cfg) {
  const brand = cfg.brand || {};
  const profiles = cfg.profiles || {};
  const fonts = new Map(); // fuente -> perfiles que la usan
  for (const [name, p] of Object.entries(profiles)) {
    for (const f of (p.compose && p.compose.fonts) || []) fonts.set(f, [...(fonts.get(f) || []), name]);
  }
  const logosHost = h('div.row');
  const checkHost = h('div.stack', { aria: { live: 'polite' } });
  const palette = brand.palette || [];
  const none = () => h('span.hint', {}, t('ui.brand.none'));
  const swatch = (c) => h('span.swatch', { title: c, vars: { sw: c }, role: 'img', aria: { label: c } });

  panel.append(h('div.stack', {},
    h('p.hint', {}, t('ui.brand.hint')),
    h('div.card', {},
      h('h2', {}, t('ui.project.palette')),
      palette.length ? h('div.swatches', {}, palette.map((c) => h('span.swatch-item', {}, swatch(c), h('code.mono', {}, c)))) : h('p.hint', {}, t('ui.brand.noPalette')),
      h('dl.facts', {},
        h('dt', {}, t('ui.brand.textColor')),
        h('dd', {}, brand.textColor ? h('span.swatch-item', {}, swatch(brand.textColor), h('code.mono', {}, brand.textColor)) : h('span.hint', {}, t('ui.brand.notSet'))),
        h('dt', {}, t('ui.brand.paletteMin')),
        h('dd', {}, Number.isFinite(brand.paletteMin) ? t('ui.brand.paletteMinValue', { n: brand.paletteMin }) : h('span.hint', {}, t('ui.brand.notSet'))),
        h('dt', {}, t('ui.brand.bannedWords')),
        h('dd', {}, (brand.bannedWords || []).length ? h('span.row', {}, brand.bannedWords.map((w) => h('span.chip', {}, w))) : none()),
        h('dt', {}, t('ui.brand.fonts')),
        h('dd', {}, fonts.size ? h('span.row', {}, [...fonts].map(([f, who]) => h('span.chip', { title: who.join(', ') }, f))) : none()),
        h('dt', {}, t('ui.brand.logos')),
        h('dd', {}, logosHost))),
    h('section.card', { aria: { labelledby: 'check-h' } },
      h('div.row-between', {}, h('h2', { id: 'check-h' }, t('ui.check.title')),
        h('button.btn', { type: 'button', onclick: () => runCheck() }, '↻ ', t('ui.check.run'))),
      checkHost),
    brandWorkshop(project, cfg)));

  async function loadLogos() {
    const seen = new Set();
    const found = [];
    await Promise.all(Object.keys(profiles).map(async (name) => {
      const list = await api.templates(project, name).catch(() => []);
      for (const x of Array.isArray(list) ? list : []) {
        if (!x.logo || seen.has(x.logo)) continue;
        seen.add(x.logo);
        found.push({ profile: name, tpl: x.id, logo: x.logo });
      }
    }));
    found.sort((a, b) => String(a.logo).localeCompare(String(b.logo)));
    replace(logosHost, found.length ? found.map((l) => h('span.logo-item', {},
      h('img.logo-thumb', { src: paths.asset(project, l.profile, 'logo', l.tpl), alt: '', loading: 'lazy' }), h('code.mono', {}, l.logo))) : none());
  }

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

  await Promise.all([loadLogos(), runCheck()]);
}
