/* La ficha de la marca de la configuración del proyecto (F4d): paleta, color del texto, mínimo de paleta, palabras
   vetadas, fuentes (las de `compose.fonts` de cada perfil) y logos (los de las plantillas, con su miniatura).
   Sin hoja es la pestaña Marca de siempre; con hoja va dentro de la ficha de paleta de la subpestaña Hoja. */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths } from '../api.js';

export const swatch = (c) => h('span.swatch', { title: c, vars: { sw: c }, role: 'img', aria: { label: c } });

/** Devuelve `{ node, load }`: `node` es la tarjeta; `load()` busca los logos (una vez) y los pinta. */
export function brandFacts(project, cfg, { title = true } = {}) {
  const brand = cfg.brand || {};
  const profiles = cfg.profiles || {};
  const fonts = new Map(); // fuente -> perfiles que la usan
  for (const [name, p] of Object.entries(profiles)) {
    for (const f of (p.compose && p.compose.fonts) || []) fonts.set(f, [...(fonts.get(f) || []), name]);
  }
  const logosHost = h('div.row');
  const palette = brand.palette || [];
  const none = () => h('span.hint', {}, t('ui.brand.none'));
  const node = h('div.card', { data: { card: 'brand-facts' } },
    title ? h('h2', {}, t('ui.project.palette')) : null,
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
      h('dd', {}, logosHost)));

  async function load() {
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
  return { node, load };
}
