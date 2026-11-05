/* Previsualización de los textos compuestos: una superposición HTML (logo SVG, titular, subtítulo) sobre el fondo crudo
   del intento, con la fuente y el color de la hoja. Es una aproximación inmediata al escribir en el panel; la composición
   de verdad la hace `gimg compose` (D28). La zona reservada no la declara aún la configuración (hoja §9, hueco):
   mientras tanto, izquierda 1/2 en apaisado y arriba 1/2 en vertical o cuadrado. F4c la sustituye por el editor. */

import { h, setVars } from '../dom.js';
import { paths } from '../api.js';

export function zoneOf(profileCfg) {
  const z = profileCfg && profileCfg.compose && profileCfg.compose.zoneName;
  if (['left', 'right', 'top', 'bottom'].includes(z)) return z;
  const w = profileCfg.targetWidth || profileCfg.width || 2;
  const hgt = profileCfg.targetHeight || profileCfg.height || 1;
  return w > hgt ? 'left' : 'top';
}

/** ctx: {project, profile, profileCfg, brand}; text: {campo: valor}. */
export function composePreview(ctx, text) {
  const cfg = ctx.profileCfg || {};
  const compose = cfg.compose || {};
  const fields = compose.fields || Object.keys(text || {});
  const titles = fields.filter((f) => f.startsWith('title')).map((f) => text[f]).filter(Boolean);
  const subs = fields.filter((f) => f.startsWith('subtitle')).map((f) => text[f]).filter(Boolean);
  const node = h('div.compose-preview', { class: `zone-${zoneOf(cfg)}`, aria: { hidden: true } });
  setVars(node, { 'preview-color': (ctx.brand && ctx.brand.textColor) || '#eaf4fa', 'preview-veil': 'rgb(6 18 28 / .35)' });
  node.append(h('div.veil'));
  if (compose.logo) node.append(h('img.logo', { src: paths.asset(ctx.project, ctx.profile, 'logo'), alt: '' }));
  for (const line of titles) node.append(h('div.t1', {}, line));
  for (const line of subs) node.append(h('div.t2', {}, line));
  return node;
}
