/* Editor de elementos de la composición (F4c.3, D39 y D40): un `dialog` a pantalla casi completa sobre la imagen del
   intento, con una caja por elemento de la plantilla (titular, subtítulo, logo, adornos) que se mueve y se redimensiona.
   - Fondo: la imagen COMPUESTA del intento (`…/image`, ya llevada al destino, con el texto pintado). La cruda
     (`raw=1`) no sirve tal cual: no está llevada al destino. Aproximación: cada caja pinta como fondo el trozo de esa
     imagen que ocupaba su sitio actual al abrir, así se ve moverse el elemento; el fondo de debajo no se retoca (el
     hueco que deja se ve hasta aplicar). La composición real la hace el servidor al aplicar.
   - Coordenadas en píxeles del destino (W×H); lo que se muestra se escala por `img.clientWidth / W`.
   - Puntero: pointer events con captura (arrastrar la caja = mover; las asas de las esquinas = redimensionar, con la
     proporción fija salvo con Mayús). Teclado: Tab entre cajas, flechas 1 px, Mayús+flechas 10 px, Alt+flechas el
     tamaño (ancho/alto por separado).
   - Contraste en vivo de cada elemento de texto: `measure?zone&text&base=1`, 400 ms después de soltar o de la última
     tecla, por la cola de medidas de measure-chip.js.
   - Texto y tipografía (F4e.2c): al elegir un elemento de texto, el panel «Texto y tipografía» edita su `text` y su
     `style` (familia con la lista de `GET /api/fonts`, tamaño, peso, cursiva, color, alineación, interlineado); vacío
     es «como en la plantilla». «Añadir texto» crea `extra<N>` (`add: true`, estilo completo; hasta 10) y «Quitar» lo
     saca del layout. La caja de un texto editado pinta una vista previa aproximada con un SVG en línea (fuentes del
     navegador); la composición real la hace el servidor al aplicar y, si avisa de `overflow` o `missingFonts`, el
     editor sigue abierto con cada aviso en su fila (borde ámbar y texto) para corregirlo.
   - Aplicar manda solo lo que difiere de la plantilla (`POST …/compose {"layout"}`); «Volver a la plantilla» manda `{}`;
     «Guardar como plantilla» aplica antes lo pendiente (la API guarda lo que el intento tiene aplicado).
   - Los avisos de error van al toast y también dentro del diálogo (un `dialog` modal tapa el contenedor de toasts). */

import { h, replace, clear } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import { toastError } from './toast.js';
import { renderMeasure, requestMeasure } from './measure-chip.js';
import { imageVersion } from './attempt-util.js';
import { trapFocus } from '../lib/focus-trap.js';

export const NAME_PATTERN = /^[a-z0-9][a-z0-9-]{0,39}$/;
export const MEASURE_DELAY_MS = 400;
export const MAX_ADDED = 10;
export const MAX_TEXT = 500;
export const FAMILY_PATTERN = /^[A-Za-z0-9 ._-]{1,64}$/;
export const COLOR_PATTERN = /^#[0-9a-fA-F]{6}$/;
const STEP = 1;
const STEP_BIG = 10;
const CORNERS = ['nw', 'ne', 'sw', 'se'];
const ARROWS = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
const WEIGHTS = [100, 200, 300, 400, 500, 600, 700, 800, 900];
const ALIGNS = ['left', 'center', 'right'];
const SVG_NS = 'http://www.w3.org/2000/svg';

const clamp = (v, lo, hi) => Math.min(Math.max(lo, hi), Math.max(lo, v));
export const sameBox = (a, b) => a.x === b.x && a.y === b.y && a.w === b.w && a.h === b.h;

/** Mueve la caja `b` (`{x, y, w, h}`) `dx`, `dy` píxeles sin salir del destino `W`×`H`. */
export function moveBox(b, dx, dy, W, H) {
  return { x: clamp(b.x + dx, 0, W - b.w), y: clamp(b.y + dy, 0, H - b.h), w: b.w, h: b.h };
}

/** Cambia el tamaño de `b` en `dw`, `dh` (teclado, ancho y alto por separado) sin salir del destino ni bajar de 1. */
export function sizeBox(b, dw, dh, W, H) {
  return { x: b.x, y: b.y, w: clamp(b.w + dw, 1, W - b.x), h: clamp(b.h + dh, 1, H - b.y) };
}

/** Arrastra la esquina `corner` (`nw|ne|sw|se`) de `b` `dx`, `dy` píxeles: la esquina opuesta queda fija. Con `lock`
    la proporción de `b` se mantiene (manda el eje que más cambia). Siempre dentro del destino y de al menos 1×1. */
export function resizeBox(b, corner, dx, dy, lock, W, H) {
  const east = corner.includes('e');
  const south = corner.includes('s');
  const anchorX = east ? b.x : b.x + b.w;
  const anchorY = south ? b.y : b.y + b.h;
  const maxW = east ? W - anchorX : anchorX;
  const maxH = south ? H - anchorY : anchorY;
  let w = clamp(b.w + (east ? dx : -dx), 1, maxW);
  let hh = clamp(b.h + (south ? dy : -dy), 1, maxH);
  if (lock) {
    let k = Math.abs(w / b.w - 1) >= Math.abs(hh / b.h - 1) ? w / b.w : hh / b.h;
    k = Math.min(k, maxW / b.w, maxH / b.h);
    k = Math.max(k, 1 / Math.min(b.w, b.h));
    w = Math.max(1, Math.round(b.w * k));
    hh = Math.max(1, Math.round(b.h * k));
  }
  return { x: east ? anchorX : anchorX - w, y: south ? anchorY : anchorY - hh, w, h: hh };
}

/** `{nombre: entrada}` de lo que difiere de la plantilla (lo que se manda a la API). Un elemento de la plantilla va
    con su caja cuando esta se movió, cuando `hidden` no es el de la plantilla (`true` oculta; `false` muestra lo que la
    plantilla trae oculto) o cuando tiene `text` o `style` propios (F4e.2c); `hidden` se lee del layout aplicado y se
    reenvía, o aplicar deshace un oculto puesto por la CLI (F4e.1). Un texto añadido va siempre, entero
    (`add: true`, caja, `text` y `style` completo). */
export function changedLayout(items) {
  const out = {};
  for (const it of items) {
    if (it.added) { out[it.name] = { add: true, ...it.cur, text: it.text || '', style: { ...it.style } }; continue; }
    const entry = { ...it.cur };
    if (it.hidden !== Boolean(it.tplHidden)) entry.hidden = it.hidden;
    if (typeof it.text === 'string') entry.text = it.text;
    if (it.style && Object.keys(it.style).length) entry.style = { ...it.style };
    if (!sameBox(it.cur, it.tplBox) || Object.keys(entry).length > 4) out[it.name] = entry;
  }
  return out;
}

/** Los problemas de un `style` tal como lo escribió la persona (`{clave: clave i18n del motivo}`); `raw` trae cadenas
    (vacía = sin valor). Devuelve también el estilo limpio en `style` (solo las claves con valor). */
export function parseStyle(raw) {
  const style = {};
  const problems = {};
  const family = (raw.family || '').trim();
  if (family) { if (FAMILY_PATTERN.test(family)) style.family = family; else problems.family = 'ui.editor.badFamily'; }
  const size = (raw.size || '').trim();
  if (size) { const n = Number(size); if (Number.isInteger(n) && n >= 4 && n <= 1000) style.size = n; else problems.size = 'ui.editor.badSize'; }
  if (raw.weight) style.weight = Number(raw.weight);
  if (raw.italic) style.italic = raw.italic === 'true';
  const color = (raw.color || '').trim();
  if (color) { if (COLOR_PATTERN.test(color)) style.color = color.toLowerCase(); else problems.color = 'ui.editor.badColor'; }
  if (raw.align) style.align = raw.align;
  const lh = (raw.lineHeight || '').trim().replace(',', '.');
  if (lh) { const n = Number(lh); if (Number.isFinite(n) && n >= 0.8 && n <= 3) style.lineHeight = Math.round(n * 100) / 100; else problems.lineHeight = 'ui.editor.badLineHeight'; }
  return { style, problems };
}

/** El nombre de una plantilla nueva: el patrón de los id y nunca `default`. */
export function validName(name) { return NAME_PATTERN.test(name) && name !== 'default'; }

const styleJson = (s) => JSON.stringify(sortKeys(s || {}));
const svgEl = (tag) => document.createElementNS(SVG_NS, tag);

/**
 * Abre el editor. ctx: el del pedido ({project, profile, key, order, profileCfg, brand, templates, measure, actions});
 * attempt: el intento (compuesto, con `compose`); tpl: su plantilla (con `elements`); opener: el botón que lo abrió
 * (recupera el foco al cerrar).
 */
export function openLayoutEditor(ctx, attempt, tpl, opener) {
  const cfg = ctx.profileCfg || {};
  const W = cfg.targetWidth || cfg.width;
  const H = cfg.targetHeight || cfg.height;
  // la maqueta aplicada: la de la composición o, si la última falló (`compose` se va y queda `composeError`), la del error
  const applied0 = ((attempt.composeError || attempt.compose || {}).layout) || {};
  let appliedNow = { ...applied0 };
  let closed = false;
  let busy = false;
  let removed = 0;        // textos añadidos quitados desde el último aplicar
  let current = null;     // el elemento del panel de texto
  let src = paths.image(ctx.project, ctx.profile, ctx.key, attempt.id, { v: imageVersion(attempt) });
  const hintId = `ed-hint-${attempt.id}`;
  const orderText = (ctx.order && ctx.order.text) || {};
  const fonts = { profile: [], installed: [], available: false };
  const tplColor = tpl.textColor || (ctx.measure && ctx.measure.textColor) || null;

  const img = h('img.ed-img', { src, alt: '', draggable: 'false' });
  const stage = h('div.ed-stage', { role: 'group', aria: { label: t('ui.editor.stage', { id: attempt.id }), describedby: hintId } }, img);
  const list = h('ul.ed-list');
  const error = h('p.notice.notice-bad', { role: 'alert', hidden: true });
  const warn = h('p.notice.notice-warn', { role: 'status', hidden: true });

  const items = [];

  /** Crea un elemento (de la plantilla o añadido), su caja en la imagen y su fila de la lista. */
  function makeItem(spec) {
    const it = { name: spec.name, kind: spec.kind, color: spec.color, tplBox: { ...spec.tplBox }, start: { ...spec.box }, cur: { ...spec.box },
      tplHidden: spec.tplHidden, added: spec.added === true, isNew: spec.isNew === true, text: spec.text, style: { ...(spec.style || {}) },
      problems: {}, timer: null, zone: null, svg: null };
    it.hidden = spec.hidden;
    it.startHidden = it.hidden;
    it.startText = it.text;
    it.startStyle = styleJson(it.style);
    it.node = h('div.ed-box', { class: `ed-${it.kind}`, tabindex: 0, role: 'group', data: { element: it.name } },
      h('span.ed-name', {}, it.name), CORNERS.map((c) => h('span.ed-handle', { class: `h-${c}`, data: { corner: c }, aria: { hidden: true } })));
    it.nums = h('output.ed-nums');
    it.chip = it.kind === 'text' && (it.color || it.style.color) ? h('span.measure', { aria: { live: 'off' } }) : null;
    it.warn = h('span.ed-warn', { hidden: true });
    it.toggle = it.added
      ? h('button.btn.btn-ghost', { type: 'button', aria: { label: t('ui.editor.removeAria', { name: it.name }) }, onclick: () => removeText(it) }, t('ui.editor.remove'))
      : h('button.btn.btn-ghost', { type: 'button', aria: { pressed: it.hidden }, onclick: () => toggleHidden(it) });
    it.row = h('li.ed-item', { data: { element: it.name } },
      h('button.btn.btn-ghost', { type: 'button', onclick: () => it.node.focus() }, h('b', {}, it.name), ' ',
        h('span.hint', {}, t(`ui.editor.kind.${it.kind}`) + (it.added ? ` · ${t('ui.editor.added')}` : ''))),
      it.nums, it.chip, it.warn, it.toggle);
    stage.append(it.node);
    list.append(it.row);
    it.node.addEventListener('pointerdown', (ev) => startDrag(ev, it, null));
    for (const handle of it.node.querySelectorAll('.ed-handle')) handle.addEventListener('pointerdown', (ev) => startDrag(ev, it, handle.dataset.corner));
    it.node.addEventListener('keydown', (ev) => onBoxKey(ev, it));
    it.node.addEventListener('focus', () => select(it));
    items.push(it);
    return it;
  }

  for (const e of tpl.elements) {
    const entry = applied0[e.id] || {};
    const it = { tplHidden: e.hidden === true };
    it.hidden = typeof (applied0[e.id] || {}).hidden === 'boolean' ? applied0[e.id].hidden : it.tplHidden;
    makeItem({ name: e.id, kind: e.kind, color: e.color || tplColor, tplBox: e.box, box: applied0[e.id] || e.box, tplHidden: it.tplHidden, hidden: it.hidden,
      text: typeof entry.text === 'string' ? entry.text : null, style: entry.style || {} });
  }
  // los textos añadidos en un aplicar anterior (`extra<N>`, `add: true`): su caja de partida es la que tienen
  for (const [name, entry] of Object.entries(applied0)) {
    if (entry && entry.add === true && !items.some((x) => x.name === name)) {
      makeItem({ name, kind: 'text', color: null, tplBox: entry, box: entry, tplHidden: false, hidden: false, added: true, text: entry.text || '', style: entry.style || {} });
    }
  }

  // --- panel «Texto y tipografía» (F4e.2c) ---
  const asTpl = t('ui.editor.asTemplate');
  const option = (value, label) => h('option', { value }, label);
  const selectEl = (id, options) => h('select', { id, oninput: onField }, options.map(([v, l]) => option(v, l)));
  const fields = {
    text: h('textarea', { id: 'ed-text', rows: 3, maxlength: MAX_TEXT, placeholder: asTpl, aria: { describedby: 'ed-text-hint' }, oninput: onField }),
    family: h('input', { type: 'text', id: 'ed-family', list: 'ed-fonts', maxlength: 64, placeholder: asTpl, autocomplete: 'off', spellcheck: 'false', aria: { describedby: 'ed-family-hint ed-family-warn ed-family-error' }, oninput: onField }),
    size: h('input', { type: 'number', id: 'ed-size', min: 4, max: 1000, step: 1, inputmode: 'numeric', placeholder: asTpl, aria: { describedby: 'ed-size-error' }, oninput: onField }),
    weight: selectEl('ed-weight', [['', asTpl], ...WEIGHTS.map((w) => [String(w), String(w)])]),
    italic: selectEl('ed-italic', [['', asTpl], ['true', t('ui.editor.italicOn')], ['false', t('ui.editor.italicOff')]]),
    color: h('input', { type: 'text', id: 'ed-color', maxlength: 7, placeholder: '#rrggbb', autocomplete: 'off', spellcheck: 'false', aria: { describedby: 'ed-color-error' }, oninput: onField }),
    align: selectEl('ed-align', [['', asTpl], ...ALIGNS.map((a) => [a, t(`ui.editor.align${a[0].toUpperCase()}${a.slice(1)}`)])]),
    lineHeight: h('input', { type: 'number', id: 'ed-lh', min: 0.8, max: 3, step: 0.1, inputmode: 'decimal', placeholder: asTpl, aria: { describedby: 'ed-lh-error' }, oninput: onField }),
  };
  const swatch = h('input', { type: 'color', id: 'ed-swatch', aria: { label: t('ui.editor.colorPick') }, oninput: () => { fields.color.value = swatch.value; onField(); } });
  const errors = Object.fromEntries(['family', 'size', 'color', 'lineHeight'].map((k) => [k, h('p.field-error', { id: `${fields[k].id}-error` })]));
  const familyWarn = h('p.field-warn', { id: 'ed-family-warn' });
  const datalist = h('datalist', { id: 'ed-fonts' });
  const field = (key, label, ...extra) => h('div.field', {}, h('label', { for: fields[key].id }, label), fields[key], ...extra);
  const editing = h('p.ed-editing');
  const noText = h('p.hint', {}, t('ui.editor.noText'));
  const form = h('div.ed-fields', { hidden: true },
    field('text', t('ui.editor.textLabel'), h('p.hint', { id: 'ed-text-hint' }, t('ui.editor.textHint'))),
    field('family', t('ui.editor.family'), datalist, h('p.hint', { id: 'ed-family-hint' }, t('ui.editor.familyHint')), familyWarn, errors.family),
    h('div.cols-2', {}, field('size', t('ui.editor.size'), errors.size), field('weight', t('ui.editor.weight'))),
    h('div.cols-2', {}, field('italic', t('ui.editor.italic')), field('align', t('ui.editor.align'))),
    h('div.ed-color', {}, field('color', t('ui.editor.color'), errors.color), swatch),
    field('lineHeight', t('ui.editor.lineHeight'), errors.lineHeight),
    h('p.hint', {}, t('ui.editor.previewHint')));
  const addBtn = h('button.btn', { type: 'button', onclick: () => addText() }, '+ ', t('ui.editor.addText'));
  const addHint = h('p.hint', {}, t('ui.editor.addTextMax'));
  const panel = h('section.ed-text', { aria: { labelledby: 'ed-text-title' } }, h('h3', { id: 'ed-text-title' }, t('ui.editor.textPanel')), editing, noText, form);

  const apply = h('button.btn.btn-primary', { type: 'button', onclick: () => applyLayout() }, t('ui.editor.apply'));
  const reset = h('button.btn', { type: 'button', onclick: () => run(() => ctx.actions.setLayout(attempt, {}), true) }, '↶ ', t('ui.editor.reset'));
  const save = h('button.btn', { type: 'button', onclick: () => saveAsTemplate() }, t('ui.editor.save'));
  const close = h('button.btn.btn-ghost', { type: 'button', onclick: () => dlg.close() }, t('ui.actions.close'));
  const exportA = tpl.source === 'local'
    ? h('a.btn.btn-ghost', { href: paths.asset(ctx.project, ctx.profile, 'template', tpl.id), download: `${tpl.id}.svg`, title: t('ui.editor.exportHint', { id: tpl.id }) }, '⭳ ', t('ui.editor.export'))
    : null;

  const dlg = h('dialog.editor', { aria: { labelledby: 'ed-title' } },
    h('div.ed-head', {}, h('h2', { id: 'ed-title' }, t('ui.editor.title', { id: attempt.id })), h('span.grow'), close),
    h('div.ed-body', {},
      h('div.ed-main', {}, stage, h('p.hint', { id: hintId }, t('ui.editor.hint')), h('p.hint', {}, t('ui.editor.approx'))),
      h('aside.ed-side', {}, h('h3', {}, t('ui.editor.elements')), list, h('div.ed-add', {}, addBtn, addHint), panel, warn, error,
        h('div.panel-actions', {}, apply, reset, save, exportA))));

  function layoutBoxes() {
    const k = img.clientWidth / W;
    if (!k) return;
    for (const it of items) {
      const { x, y, w, h: hh } = it.cur;
      const kx = w / it.start.w;
      const ky = hh / it.start.h;
      const s = it.node.style;
      s.left = `${x * k}px`; s.top = `${y * k}px`; s.width = `${w * k}px`; s.height = `${hh * k}px`;
      s.setProperty('background-size', `${W * k * kx}px ${H * k * ky}px`);
      s.setProperty('background-position', `${-it.start.x * k * kx}px ${-it.start.y * k * ky}px`);
    }
  }

  const hasText = (it) => it.added || typeof it.text === 'string' || Object.keys(it.style).length > 0;
  const dirty = () => removed > 0 || items.some((x) => x.isNew || !sameBox(x.cur, x.start) || x.hidden !== x.startHidden || x.text !== x.startText || styleJson(x.style) !== x.startStyle);
  const invalid = () => items.some((x) => Object.keys(x.problems).length > 0);

  function refresh(it) {
    layoutBoxes();
    const label = t('ui.editor.box', { name: it.name, x: it.cur.x, y: it.cur.y, w: it.cur.w, h: it.cur.h });
    it.node.setAttribute('aria-label', label);
    it.nums.textContent = `${it.cur.x}, ${it.cur.y} · ${it.cur.w}×${it.cur.h}`;
    const changed = Object.keys(changedLayout(items)).length > 0;
    it.node.classList.toggle('is-hidden', it.hidden);
    it.row.classList.toggle('is-hidden', it.hidden);
    it.row.classList.toggle('is-edited', !it.added && hasText(it));
    if (!it.added) {
      it.toggle.textContent = it.hidden ? t('ui.editor.show') : t('ui.editor.hide');
      it.toggle.setAttribute('aria-pressed', String(it.hidden));
      it.toggle.setAttribute('aria-label', it.hidden ? t('ui.editor.showAria', { name: it.name }) : t('ui.editor.hideAria', { name: it.name }));
    }
    renderPreview(it);
    apply.disabled = busy || !dirty() || invalid();
    reset.disabled = busy || (!changed && !Object.keys(appliedNow).length);
    save.disabled = busy || invalid();
    const added = items.filter((x) => x.added).length;
    addBtn.disabled = busy || added >= MAX_ADDED;
    addHint.hidden = added < MAX_ADDED;
  }

  function refreshAll() { for (const it of items) refresh(it); }

  /** F4e.1: «Ocultar» / «Mostrar» un elemento (`hidden: true` en su entrada del layout; no se borra nada). */
  function toggleHidden(it) {
    if (busy) return;
    it.hidden = !it.hidden;
    refresh(it);
  }

  // --- texto y tipografía ---
  /** El elemento del panel: un texto muestra sus campos; otro (logo, adorno), solo la pista. */
  function select(it) {
    current = it;
    const isText = Boolean(it && it.kind === 'text');
    form.hidden = !isText;
    noText.hidden = isText;
    editing.hidden = !it;
    editing.textContent = it ? t('ui.editor.editing', { name: it.name }) : '';
    if (isText) fill(it);
  }

  function fill(it) {
    const s = it.style;
    fields.text.value = it.text === null || it.text === undefined ? '' : it.text;
    fields.text.placeholder = it.added ? '' : (typeof orderText[it.name] === 'string' && orderText[it.name] ? orderText[it.name] : asTpl);
    fields.family.value = s.family || '';
    fields.size.value = s.size === undefined ? '' : String(s.size);
    fields.weight.value = s.weight === undefined ? '' : String(s.weight);
    fields.italic.value = s.italic === undefined ? '' : String(s.italic);
    fields.color.value = s.color || '';
    swatch.value = s.color || it.color || '#ffffff';
    fields.align.value = s.align || '';
    fields.lineHeight.value = s.lineHeight === undefined ? '' : String(s.lineHeight);
    for (const k of Object.keys(errors)) { errors[k].textContent = it.problems[k] ? t(it.problems[k]) : ''; fields[k].setAttribute('aria-invalid', String(Boolean(it.problems[k]))); }
    for (const k of ['family', 'size', 'color', 'lineHeight']) fields[k].placeholder = it.added ? '' : (k === 'color' ? '#rrggbb' : asTpl);
    checkFamily();
  }

  /** Lee los campos al elemento actual: en uno de la plantilla, vacío = como en la plantilla; en uno añadido, vacío = su
      valor por defecto (la API pide el estilo completo). */
  function onField() {
    const it = current;
    if (!it || it.kind !== 'text') return;
    const { style, problems } = parseStyle({ family: fields.family.value, size: fields.size.value, weight: fields.weight.value, italic: fields.italic.value,
      color: fields.color.value, align: fields.align.value, lineHeight: fields.lineHeight.value });
    const text = fields.text.value.slice(0, MAX_TEXT);
    if (it.added) { it.style = { ...defaultStyle(), ...style }; it.text = text; }
    else { it.style = style; it.text = text === '' ? null : text; }
    it.problems = problems;
    for (const k of Object.keys(errors)) { errors[k].textContent = problems[k] ? t(problems[k]) : ''; fields[k].setAttribute('aria-invalid', String(Boolean(problems[k]))); }
    if (style.color) swatch.value = style.color;
    checkFamily();
    refresh(it);
    measureLater(it);
  }

  function checkFamily() {
    const family = fields.family.value.trim();
    const known = !family || !fonts.available || fonts.installed.some((f) => f.toLowerCase() === family.toLowerCase());
    familyWarn.textContent = known ? '' : t('ui.editor.familyMissing', { family });
  }

  function defaultStyle() {
    const family = fonts.profile[0] || fonts.installed[0] || 'sans-serif';
    const color = COLOR_PATTERN.test(tplColor || '') ? tplColor.toLowerCase() : '#ffffff';
    return { family, size: 40, weight: 400, italic: false, color, align: 'left' };
  }

  /** La vista previa aproximada de un texto editado o añadido: un SVG en la caja, con las fuentes del navegador. */
  function renderPreview(it) {
    const show = it.kind === 'text' && hasText(it);
    it.node.classList.toggle('is-preview', show);
    it.node.style.setProperty('background-image', show ? 'none' : `url("${src}")`);
    if (!show) { if (it.svg) { it.svg.remove(); it.svg = null; } return; }
    if (!it.svg) { it.svg = svgEl('svg'); it.svg.setAttribute('aria-hidden', 'true'); it.node.append(it.svg); }
    const s = it.style;
    const size = s.size || (it.added ? 40 : Math.max(8, Math.round(it.tplBox.h * 0.66)));
    const text = typeof it.text === 'string' ? it.text : (typeof orderText[it.name] === 'string' ? orderText[it.name] : it.name);
    const x = s.align === 'center' ? it.cur.w / 2 : s.align === 'right' ? it.cur.w : 0;
    it.svg.setAttribute('viewBox', `0 0 ${it.cur.w} ${it.cur.h}`);
    const txt = svgEl('text');
    txt.setAttribute('x', x);
    txt.setAttribute('y', Math.round(size * 0.9));
    txt.setAttribute('font-size', size);
    txt.setAttribute('fill', s.color || it.color || '#ffffff');
    txt.setAttribute('text-anchor', s.align === 'center' ? 'middle' : s.align === 'right' ? 'end' : 'start');
    if (s.family) txt.setAttribute('font-family', `"${s.family}", sans-serif`);
    if (s.weight) txt.setAttribute('font-weight', s.weight);
    if (s.italic !== undefined) txt.setAttribute('font-style', s.italic ? 'italic' : 'normal');
    txt.style.whiteSpace = 'pre';
    text.split('\n').forEach((line, i) => {
      const span = svgEl('tspan');
      span.setAttribute('x', x);
      if (i) span.setAttribute('dy', Math.round((s.lineHeight || 1.2) * size));
      span.textContent = line || ' ';
      txt.append(span);
    });
    clear(it.svg);
    it.svg.append(txt);
  }

  function addText() {
    if (busy || items.filter((x) => x.added).length >= MAX_ADDED) return;
    let n = 1;
    while (items.some((x) => x.name === `extra${n}`)) n++;
    const style = defaultStyle();
    const w = Math.min(W, Math.round(W / 2));
    const hh = Math.min(H, Math.round(style.size * 1.5));
    const k = items.filter((x) => x.added).length;
    const box = { x: Math.round((W - w) / 2), y: clamp(Math.round((H - hh) / 2 + k * hh), 0, H - hh), w, h: hh };
    const it = makeItem({ name: `extra${n}`, kind: 'text', color: null, tplBox: box, box, tplHidden: false, hidden: false, added: true, isNew: true, text: t('ui.editor.newText'), style });
    it.node.style.setProperty('background-image', `url("${src}")`);
    refreshAll();
    it.node.focus();
    measureNow(it);
  }

  function removeText(it) {
    if (busy) return;
    clearTimeout(it.timer);
    items.splice(items.indexOf(it), 1);
    it.node.remove();
    it.row.remove();
    if (!it.isNew) removed++;
    if (current === it) select(null);
    refreshAll();
    addBtn.focus();
  }

  /** Los avisos de la composición (`overflow` por elemento, `missingFonts`): borde ámbar y texto en cada fila, y el
      aviso general. Devuelve si hay alguno. */
  function showWarnings(compose) {
    const over = (compose && compose.overflow) || {};
    const missing = (compose && compose.missingFonts) || [];
    for (const it of items) {
      const o = over[it.name];
      it.node.classList.toggle('is-overflow', Boolean(o));
      it.row.classList.toggle('is-overflow', Boolean(o));
      it.warn.hidden = !o;
      it.warn.textContent = o ? t('ui.editor.overflow', { size: o.size, min: o.min }) : '';
    }
    const parts = [];
    const names = Object.keys(over).filter((n) => items.some((x) => x.name === n));
    if (names.length) parts.push(t('ui.editor.overflowList', { names: names.join(', ') }));
    if (missing.length) parts.push(t('ui.editor.missingFonts', { fonts: missing.join(', ') }));
    warn.hidden = !parts.length;
    warn.textContent = parts.length ? `${t('ui.editor.warnings')} ${parts.join(' ')}` : '';
    return parts.length > 0;
  }

  /** Tras aplicar sin cerrar: el intento recompuesto es el punto de partida (imagen nueva, nada pendiente). */
  function settle(composed) {
    attempt = composed;
    src = paths.image(ctx.project, ctx.profile, ctx.key, attempt.id, { v: imageVersion(attempt) });
    img.src = src;
    for (const it of items) {
      it.start = { ...it.cur }; it.startHidden = it.hidden; it.startText = it.text; it.startStyle = styleJson(it.style); it.isNew = false;
      it.node.style.setProperty('background-image', `url("${src}")`);
    }
    removed = 0;
    refreshAll();
  }

  async function applyLayout() {
    let stay = false;
    await run(async () => {
      const composed = await ctx.actions.setLayout(attempt, changedLayout(items));
      appliedNow = changedLayout(items);
      stay = showWarnings(composed && composed.compose);
      if (stay && !closed) settle(composed);
    }, () => !stay);
  }

  function setBusy(v) { busy = v; refreshAll(); }

  function showError(e) {
    const message = describeError(e, t);
    toastError(message);
    error.textContent = message;
    error.hidden = false;
  }

  /** Ejecuta una acción del pedido con el diálogo ocupado; `andClose` (booleano o función): lo cierra si salió bien. */
  async function run(fn, andClose) {
    error.hidden = true;
    setBusy(true);
    try { await fn(); } catch (e) { if (!closed) { setBusy(false); showError(e); } return false; }
    const shouldClose = typeof andClose === 'function' ? andClose() : andClose;
    if (shouldClose && !closed) dlg.close();
    else if (!closed) setBusy(false);
    return true;
  }

  async function saveAsTemplate() {
    if (invalid()) return;
    const answer = await askTemplate(ctx, save);
    if (!answer) return;
    const layout = changedLayout(items);
    const pending = JSON.stringify(sortKeys(layout)) !== JSON.stringify(sortKeys(appliedNow));
    await run(async () => {
      if (pending) { await ctx.actions.setLayout(attempt, layout); appliedNow = layout; }
      await ctx.actions.saveTemplate(attempt, answer.name, answer.dest);
    }, true);
  }

  // --- puntero ---
  function startDrag(ev, it, corner) {
    if (busy || (ev.button !== undefined && ev.button !== 0)) return;
    ev.preventDefault();
    ev.stopPropagation();
    it.node.focus();
    const target = ev.currentTarget;
    try { target.setPointerCapture(ev.pointerId); } catch { /* sin captura el arrastre sigue mientras el puntero esté encima */ }
    const origin = { x: ev.clientX, y: ev.clientY, box: { ...it.cur } };
    const onMove = (m) => {
      const k = img.clientWidth / W;
      if (!k) return;
      const dx = Math.round((m.clientX - origin.x) / k);
      const dy = Math.round((m.clientY - origin.y) / k);
      it.cur = corner ? resizeBox(origin.box, corner, dx, dy, !m.shiftKey, W, H) : moveBox(origin.box, dx, dy, W, H);
      refresh(it);
    };
    const onEnd = () => {
      target.removeEventListener('pointermove', onMove);
      target.removeEventListener('pointerup', onEnd);
      target.removeEventListener('pointercancel', onEnd);
      try { target.releasePointerCapture(ev.pointerId); } catch { /* ya soltado */ }
      measureLater(it);
    };
    target.addEventListener('pointermove', onMove);
    target.addEventListener('pointerup', onEnd);
    target.addEventListener('pointercancel', onEnd);
  }

  // --- teclado ---
  function onBoxKey(ev, it) {
    const dir = ARROWS[ev.key];
    if (!dir || busy || ev.ctrlKey || ev.metaKey) return;
    ev.preventDefault();
    const step = ev.shiftKey ? STEP_BIG : STEP;
    it.cur = ev.altKey ? sizeBox(it.cur, dir[0] * step, dir[1] * step, W, H) : moveBox(it.cur, dir[0] * step, dir[1] * step, W, H);
    refresh(it);
    measureLater(it);
  }

  // --- contraste en vivo ---
  function measureLater(it) {
    if (!it.chip) return;
    clearTimeout(it.timer);
    it.timer = setTimeout(() => measureNow(it), MEASURE_DELAY_MS);
  }

  function measureNow(it) {
    if (closed || !it.chip) return;
    const { x, y, w, h: hh } = it.cur;
    const zone = [x, y, w, hh].join(',');
    const color = it.style.color || it.color;
    it.zone = zone;
    replace(it.chip, h('span.chip', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.measure.pending')));
    const cacheKey = `${ctx.project}/${ctx.profile}/${ctx.key}/${attempt.id}@base:${zone}:${color}`;
    requestMeasure(cacheKey, () => api.measure(ctx.project, ctx.profile, ctx.key, attempt.id, { zone, text: color, base: true }))
      .then((res) => { if (!closed && it.zone === zone) renderMeasure(it.chip, res, { paletteMin: ctx.brand && ctx.brand.paletteMin }, () => measureNow(it)); });
  }

  // --- fuentes (una vez al abrir; sin lista no es un error: se puede escribir igual) ---
  api.fonts(ctx.project).then((res) => {
    if (closed || !res) return;
    const proj = (res.projects || []).find((p) => p.project === ctx.project) || (res.projects || [])[0] || {};
    const prof = (proj.profiles || []).find((p) => p.profile === ctx.profile) || {};
    fonts.profile = (prof.fonts || []).map((f) => f.name);
    fonts.installed = Array.isArray(res.installed) ? res.installed : [];
    fonts.available = res.available === true;
    const names = [...new Set([...fonts.profile, ...fonts.installed])];
    replace(datalist, names.map((n) => option(n, n)));
    checkFamily();
  }).catch(() => { /* sin lista */ });

  // --- foco atrapado y cierre ---
  dlg.addEventListener('keydown', (ev) => {
    ev.stopPropagation(); // los atajos de la galería y los globales no actúan con el editor abierto
  });
  trapFocus(dlg);
  dlg.addEventListener('close', () => {
    closed = true;
    for (const it of items) clearTimeout(it.timer);
    if (observer) observer.disconnect();
    window.removeEventListener('resize', layoutBoxes);
    dlg.remove();
    // el pedido se recarga al aplicar y la tarjeta se rehace: si el botón ya no está, la tarjeta del intento
    const back = opener && opener.isConnected ? opener : document.querySelector(`[data-attempt="${attempt.id}"][data-kind="attempt"]`);
    if (back) back.focus();
  });

  document.body.append(dlg);
  const observer = ('ResizeObserver' in window) ? new ResizeObserver(layoutBoxes) : null;
  if (observer) observer.observe(img); else window.addEventListener('resize', layoutBoxes);
  img.addEventListener('load', layoutBoxes);
  dlg.showModal();
  for (const it of items) it.node.style.setProperty('background-image', `url("${src}")`);
  select(null);
  showWarnings(attempt.compose);
  for (const it of items) { refresh(it); measureNow(it); }
  (items[0] ? items[0].node : close).focus();
  return dlg;
}

function sortKeys(obj) { return Object.fromEntries(Object.keys(obj).sort().map((k) => [k, obj[k]])); }

/** Diálogo «Guardar como plantilla»: nombre (validado antes de enviar) y destino. Devuelve `{name, dest}` o null. */
function askTemplate(ctx, opener) {
  const dir = (ctx.profileCfg.compose || {}).templatesDir;
  return new Promise((resolve) => {
    let answer = null;
    const input = h('input', { type: 'text', id: 'ed-name', maxlength: 40, required: true, autocomplete: 'off', spellcheck: 'false', aria: { describedby: 'ed-name-hint ed-name-error' } });
    const problem = h('p.field-error', { id: 'ed-name-error', role: 'alert' });
    const radio = (value, label, checked) => h('label.check', {}, h('input', { type: 'radio', name: 'ed-dest', value, checked }), h('span', {}, label));
    const dest = h('fieldset.field', {}, h('legend.label', {}, t('ui.editor.dest')),
      radio('local', t('ui.editor.destLocal'), true), dir ? radio('project', t('ui.editor.destProject', { dir }), false) : null);
    const form = h('form', { novalidate: true },
      h('div.field', {}, h('label', { for: 'ed-name' }, t('ui.editor.name')), input, h('p.hint', { id: 'ed-name-hint' }, t('ui.editor.nameHint')), problem),
      dest,
      h('div.panel-actions', {}, h('button.btn.btn-primary', { type: 'submit' }, t('ui.editor.saveGo')),
        h('button.btn', { type: 'button', onclick: () => dlg.close() }, t('ui.editor.cancel'))));
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const name = input.value.trim();
      if (!validName(name)) { problem.textContent = t('ui.editor.nameInvalid'); input.focus(); return; }
      if ((ctx.templates || []).some((x) => x.id === name)) { problem.textContent = t('ui.editor.nameExists', { name }); input.focus(); return; }
      const checked = form.querySelector('input[name="ed-dest"]:checked');
      answer = { name, dest: checked ? checked.value : 'local' };
      dlg.close();
    });
    const dlg = h('dialog.editor-save', { aria: { labelledby: 'ed-save-title' } }, h('h2', { id: 'ed-save-title' }, t('ui.editor.saveTitle')), form);
    dlg.addEventListener('keydown', (ev) => ev.stopPropagation());
    dlg.addEventListener('close', () => { dlg.remove(); if (opener && opener.isConnected) opener.focus(); resolve(answer); });
    document.body.append(dlg);
    dlg.showModal();
    input.focus();
  });
}
