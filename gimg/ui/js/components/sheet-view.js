/* Subpestaña Hoja de la pestaña Marca (0.7.0 §2.10): la hoja de marca resuelta (`GET /api/projects/{p}/brand/sheet`,
   `extends` aplicado) en fichas de solo lectura: Ficha, Paleta por papeles, Registros y cierre, Vetos, Tipos de pieza
   y Aceptación. Cada valor lleva su procedencia (`origin`): «propio» o «heredado (proyecto)»; la marca solo sale si
   la hoja hereda de otra. Estados: cargando, error, hoja con errores (los de `GET /api/projects/{p}`, arriba, y lo
   que se pueda leer) y padre de `extends` no encontrado. La hoja se edita en su archivo (ruta copiable). */

import { h, replace } from '../dom.js';
import { t, lang } from '../i18n.js';
import { api, describeError, ApiError } from '../api.js';
import { newOrderButton } from './slots.js';
import { copyButton } from './copy-button.js';
import { brandFacts, swatch } from './brand-facts.js';

const ROLES = ['paper', 'ink', 'accent', 'halo', 'grid'];
const EXTENDS_CODES = ['brandsheet.extends_missing', 'brandsheet.extends_broken', 'brandsheet.extends_cycle'];

/** Texto de un `{es, en}` (o de una cadena) en el idioma de la interfaz. */
export const loc = (x) => (x && typeof x === 'object' ? x[lang()] || x.es || x.en || '' : x == null ? '' : String(x));

/** Procedencia de un campo (o de todo lo que cuelga de él): `{origin: 'own'|'inherited', project}` o null. Propio si
    alguna parte lo es; si no, el proyecto del que hereda. */
export function originOf(origin, prefix) {
  let found = null;
  for (const [field, o] of Object.entries(origin || {})) {
    if (field !== prefix && !field.startsWith(`${prefix}.`)) continue;
    if (o.origin === 'own') return { origin: 'own', project: o.project };
    found = found || { origin: 'inherited', project: o.project };
  }
  return found;
}

export async function sheetView(host, project, cfg, info) {
  const sheet = info.sheet || {};
  const body = h('div.stack', { aria: { live: 'polite', busy: 'true' } }, h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading')));
  host.append(body);
  const errors = (sheet.errors || []).length
    ? h('div.notice.notice-bad', { role: 'alert', data: { sheet: 'errors' } }, h('div', {}, h('b', {}, t('ui.sheet.errors')),
      h('ul', {}, sheet.errors.map((line) => h('li', {}, line)))))
    : null;
  let view;
  try { view = await api.brandSheet(project); } catch (e) {
    body.setAttribute('aria-busy', 'false');
    const parent = e instanceof ApiError && EXTENDS_CODES.includes(e.code);
    replace(body, errors,
      h('p.notice.notice-bad', { role: 'alert', data: { sheet: parent ? 'extends' : 'error' } }, parent ? [h('b', {}, t('ui.sheet.extendsMissing')), ' ', describeError(e, t)] : describeError(e, t)),
      sheetFile(sheet),
      (info.pieceTypes || []).length ? pieceTypesCard(project, cfg, info.pieceTypes, null, false) : null);
    return;
  }
  body.setAttribute('aria-busy', 'false');
  const many = (view.chain || []).length > 1;
  const facts = brandFacts(project, cfg, { title: false });
  replace(body, errors,
    identityCard(view, sheet, many),
    paletteCard(view, many, facts),
    registersCard(view, many),
    vetoesCard(view, many),
    pieceTypesCard(project, cfg, view.pieceTypes || [], view.origin, many),
    acceptanceCard(view, many));
  await facts.load();
}

function tag(origin, prefix, many) {
  if (!many) return null;
  const o = originOf(origin, prefix);
  if (!o) return null;
  return o.origin === 'own'
    ? h('span.chip.chip-accent', { data: { origin: 'own' } }, t('ui.sheet.own'))
    : h('span.chip', { data: { origin: 'inherited' } }, t('ui.sheet.inherited', { project: o.project }));
}

function sheetFile(sheet) {
  return sheet.path ? h('p', {}, t('ui.sheet.file'), ' ', h('code.mono', {}, sheet.path), ' ', copyButton(sheet.path, { label: t('ui.sheet.copyPath') })) : null;
}

function card(id, title, ...children) {
  return h('section.card', { data: { card: id }, aria: { labelledby: `sheet-${id}` } }, h('h2', { id: `sheet-${id}` }, title), ...children);
}

function identityCard(view, sheet, many) {
  return card('identity', t('ui.sheet.identity'),
    h('dl.facts', {},
      h('dt', {}, t('ui.sheet.name')), h('dd', {}, view.name),
      h('dt', {}, t('ui.sheet.version')), h('dd', {}, h('code.mono', {}, view.version)),
      h('dt', {}, t('ui.sheet.file')), h('dd', {}, sheet.path ? h('span.row', {}, h('code.mono', {}, sheet.path), copyButton(sheet.path, { label: t('ui.sheet.copyPath') })) : h('span.hint', {}, t('ui.brand.notSet'))),
      h('dt', {}, t('ui.sheet.chain')), h('dd', {}, h('code.mono', { data: { sheet: 'chain' } }, (view.chain || []).join(' ← ')),
        many ? null : h('span.hint', {}, ' ', t('ui.sheet.noParent'))),
      h('dt', {}, t('ui.sheet.words')), h('dd', {}, t('ui.sheet.wordsValue', { min: (view.promptWords || {}).min, max: (view.promptWords || {}).max }))),
    h('p.hint', {}, t('ui.sheet.readOnly')));
}

function paletteCard(view, many, facts) {
  const roles = view.roles || {};
  const rows = ROLES.filter((r) => roles[r]).map((r) => h('li.role-row', { data: { role: r } },
    swatch(roles[r].hex), h('b', {}, t(`ui.sheet.role.${r}`)), h('code.mono', {}, roles[r].hex),
    h('span', {}, roles[r].name || '—'), tag(view.origin, `palette.${r}`, many)));
  return card('palette', t('ui.project.palette'),
    h('ul.role-list', {}, rows),
    h('h3', {}, t('ui.sheet.paletteSentence'), ' ', tag(view.origin, 'paletteSentence', many)),
    h('pre.sheet-code', {}, h('code', {}, view.paletteSentenceText || '')),
    copyButton(view.paletteSentenceText || ''),
    h('h3', {}, t('ui.sheet.projectBrand')),
    facts.node);
}

function registersCard(view, many) {
  const regs = Object.entries(view.registers || {});
  return card('registers', t('ui.sheet.registers'),
    regs.map(([id, r]) => h('div.stack', { data: { register: id } },
      h('h3', {}, loc(r.label) || id, ' ', h('code.mono.hint', {}, id), ' ', tag(view.origin, `registers.${id}`, many)),
      h('pre.sheet-code', {}, h('code', {}, r.block || '')), copyButton(r.block || ''))),
    h('h3', {}, t('ui.sheet.closing'), ' ', tag(view.origin, 'closing', many)),
    h('pre.sheet-code', {}, h('code', {}, view.closing || '')), copyButton(view.closing || ''));
}

function vetoesCard(view, many) {
  const v = view.vetoes || {};
  const list = (words) => (words && words.length ? h('span.row', {}, words.map((w) => h('span.chip', {}, w))) : h('span.hint', {}, t('ui.brand.none')));
  return card('vetoes', t('ui.sheet.vetoes'),
    (v.groups || []).map((g) => h('div.stack', { data: { group: g.id } },
      h('h3', {}, loc(g.label) || g.id, ' ', tag(view.origin, `vetoes.groups.${g.id}`, many)),
      g.reason ? h('p.hint', {}, loc(g.reason)) : null, list(g.terms))),
    h('h3', {}, t('ui.sheet.exceptions')),
    (v.exceptions || []).length
      ? h('ul', {}, v.exceptions.map((x, i) => h('li', {}, h('b', {}, x.term), ' ', t('ui.sheet.onlyIn'), ' ', (x.pieces || []).map((p) => h('code.mono', {}, p, ' ')), tag(view.origin, `vetoes.exceptions.${i}`, many))))
      : h('p.hint', {}, t('ui.brand.none')),
    h('h3', {}, t('ui.sheet.colorWords'), ' ', tag(view.origin, 'vetoes.colorWords', many)), list(v.colorWords),
    h('h3', {}, t('ui.sheet.neverWrite'), ' ', tag(view.origin, 'vetoes.neverWrite', many)), list(v.neverWrite),
    v.fillPhrase ? h('p', {}, h('b', {}, t('ui.sheet.fillPhrase')), ' ', h('code.mono', {}, v.fillPhrase)) : null);
}

function pieceTypesCard(project, cfg, types, origin, many) {
  const profiles = cfg.profiles || {};
  return card('pieces', t('ui.sheet.pieceTypes'),
    types.length ? h('div.table-wrap', {}, h('table.tbl', {},
      h('thead', {}, h('tr', {}, ['type', 'profile', 'register', 'chroma', 'seed', 'count', 'workshop'].map((c) => h('th', { scope: 'col' }, t(`ui.sheet.col.${c}`))), h('th', { scope: 'col' }, h('span.sr-only', {}, t('ui.pieces.order'))))),
      h('tbody', {}, types.map((p) => h('tr', { data: { piece: p.id } },
        h('th', { scope: 'row' }, loc(p.label) || p.id, ' ', h('code.mono.hint', {}, p.id), ' ', tag(origin, `pieceTypes.${p.id}`, many)),
        h('td', {}, p.profile ? h('code.mono', {}, p.profile) : '—'),
        h('td', {}, p.register ? h('code.mono', {}, p.register) : '—'),
        h('td', {}, p.chroma ? h('span.swatch-item', {}, swatch(p.chroma), h('code.mono', {}, p.chroma)) : t('ui.sheet.noChroma')),
        h('td', {}, p.seed ?? '—'),
        h('td', {}, p.count ?? '—'),
        h('td', {}, (p.workshop || []).length ? p.workshop.join(', ') : '—'),
        h('td', {}, p.profile && profiles[p.profile]
          ? newOrderButton(project, { profile: p.profile, label: t('ui.pieces.order'), aria: t('ui.pieces.orderAria', { profile: p.profile }), primary: false })
          : h('span.hint', {}, '—'))))))) : h('p.hint', {}, t('ui.sheet.noPieceTypes')));
}

function acceptanceCard(view, many) {
  const a = view.acceptance || {};
  const traits = Object.entries(a.traits || {});
  const refs = a.references || [];
  const un = a.unmeasured || [];
  if (!traits.length && !refs.length && !un.length && a.autoDiscard === undefined) {
    return card('acceptance', t('ui.sheet.acceptance'), h('p.hint', {}, t('ui.sheet.noAcceptance')));
  }
  return card('acceptance', t('ui.sheet.acceptance'), tag(view.origin, 'acceptance', many),
    h('dl.facts', {},
      h('dt', {}, t('ui.sheet.traits')), h('dd', {}, traits.length ? h('span.row', {}, traits.map(([id, w]) => h('span.chip', {}, `${id} · ${w}`))) : h('span.hint', {}, t('ui.brand.none'))),
      h('dt', {}, t('ui.sheet.references')), h('dd', {}, refs.length ? h('span.row', {}, refs.map((r) => h('code.mono', {}, r))) : h('span.hint', {}, t('ui.brand.none'))),
      h('dt', {}, t('ui.sheet.autoDiscard')), h('dd', {}, a.autoDiscard ? t('ui.sheet.yes') : t('ui.sheet.no')),
      h('dt', {}, t('ui.sheet.unmeasured')), h('dd', {}, un.length ? h('span.row', {}, un.map((u) => h('span.chip', { title: u.id }, loc(u.label) || u.id))) : h('span.hint', {}, t('ui.brand.none')))));
}
