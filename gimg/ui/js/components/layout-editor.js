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
   - Aplicar manda solo lo que difiere de la plantilla (`POST …/compose {"layout"}`); «Volver a la plantilla» manda `{}`;
     «Guardar como plantilla» aplica antes lo pendiente (la API guarda lo que el intento tiene aplicado).
   - Los avisos de error van al toast y también dentro del diálogo (un `dialog` modal tapa el contenedor de toasts). */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, paths, describeError } from '../api.js';
import { toastError } from './toast.js';
import { renderMeasure, requestMeasure } from './measure-chip.js';
import { imageVersion } from './attempt-util.js';
import { CORNERS, STEP, STEP_BIG, moveBox, sizeBox, resizeBox, sameBox, startBoxDrag, boxKey } from './box-drag.js';
import { trapDialog } from './dialog-trap.js';

export const NAME_PATTERN = /^[a-z0-9][a-z0-9-]{0,39}$/;
export const MEASURE_DELAY_MS = 400;

export { moveBox, sizeBox, resizeBox, sameBox };

/** `{nombre: caja}` de lo que difiere de la caja de la plantilla (lo que se manda a la API). */
export function changedLayout(items) {
  const out = {};
  for (const it of items) if (!sameBox(it.cur, it.tplBox)) out[it.name] = { ...it.cur };
  return out;
}

/** El nombre de una plantilla nueva: el patrón de los id y nunca `default`. */
export function validName(name) { return NAME_PATTERN.test(name) && name !== 'default'; }

/**
 * Abre el editor. ctx: el del pedido ({project, profile, key, profileCfg, brand, templates, measure, actions});
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
  const src = paths.image(ctx.project, ctx.profile, ctx.key, attempt.id, { v: imageVersion(attempt) });
  const hintId = `ed-hint-${attempt.id}`;

  const img = h('img.ed-img', { src, alt: '', draggable: 'false' });
  const stage = h('div.ed-stage', { role: 'group', aria: { label: t('ui.editor.stage', { id: attempt.id }), describedby: hintId } }, img);
  const list = h('ul.ed-list');
  const error = h('p.notice.notice-bad', { role: 'alert', hidden: true });

  const items = tpl.elements.map((e) => {
    const box = { ...(applied0[e.id] || e.box) };
    const it = { name: e.id, kind: e.kind, color: e.color || tpl.textColor || (ctx.measure && ctx.measure.textColor) || null,
      tplBox: { ...e.box }, start: { ...box }, cur: { ...box }, timer: null, zone: null };
    it.node = h('div.ed-box', { class: `ed-${e.kind}`, tabindex: 0, role: 'group', data: { element: e.id } },
      h('span.ed-name', {}, e.id), CORNERS.map((c) => h('span.ed-handle', { class: `h-${c}`, data: { corner: c }, aria: { hidden: true } })));
    it.node.style.setProperty('background-image', `url("${src}")`);
    it.nums = h('output.ed-nums');
    it.chip = e.kind === 'text' && it.color ? h('span.measure', { aria: { live: 'off' } }) : null;
    it.row = h('li.ed-item', {},
      h('button.btn.btn-ghost', { type: 'button', onclick: () => it.node.focus() }, h('b', {}, e.id), ' ', h('span.hint', {}, t(`ui.editor.kind.${e.kind}`))),
      it.nums, it.chip);
    stage.append(it.node);
    list.append(it.row);
    it.node.addEventListener('pointerdown', (ev) => startDrag(ev, it, null));
    for (const handle of it.node.querySelectorAll('.ed-handle')) handle.addEventListener('pointerdown', (ev) => startDrag(ev, it, handle.dataset.corner));
    it.node.addEventListener('keydown', (ev) => onBoxKey(ev, it));
    return it;
  });

  const apply = h('button.btn.btn-primary', { type: 'button', onclick: () => run(() => ctx.actions.setLayout(attempt, changedLayout(items)), true) }, t('ui.editor.apply'));
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
      h('aside.ed-side', {}, h('h3', {}, t('ui.editor.elements')), list, error,
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

  function refresh(it) {
    layoutBoxes();
    const label = t('ui.editor.box', { name: it.name, x: it.cur.x, y: it.cur.y, w: it.cur.w, h: it.cur.h });
    it.node.setAttribute('aria-label', label);
    it.nums.textContent = `${it.cur.x}, ${it.cur.y} · ${it.cur.w}×${it.cur.h}`;
    const changed = Object.keys(changedLayout(items)).length > 0;
    apply.disabled = busy || items.every((x) => sameBox(x.cur, x.start));
    reset.disabled = busy || (!changed && !Object.keys(appliedNow).length);
    save.disabled = busy;
  }

  function setBusy(v) { busy = v; for (const it of items) refresh(it); }

  function showError(e) {
    const message = describeError(e, t);
    toastError(message);
    error.textContent = message;
    error.hidden = false;
  }

  /** Ejecuta una acción del pedido con el diálogo ocupado; `andClose`: lo cierra si salió bien. */
  async function run(fn, andClose) {
    error.hidden = true;
    setBusy(true);
    try { await fn(); } catch (e) { if (!closed) { setBusy(false); showError(e); } return false; }
    if (andClose && !closed) dlg.close();
    else if (!closed) setBusy(false);
    return true;
  }

  async function saveAsTemplate() {
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
    startBoxDrag(ev, {
      getBox: () => it.cur, setBox: (box) => { it.cur = box; refresh(it); }, scale: () => img.clientWidth / W, W, H, corner,
      lock: (m) => !m.shiftKey, busy: () => busy, focus: it.node, onEnd: () => measureLater(it),
    });
  }

  // --- teclado ---
  function onBoxKey(ev, it) {
    if (busy) return;
    const next = boxKey(ev, it.cur, { W, H, step: ev.shiftKey ? STEP_BIG : STEP, size: ev.altKey });
    if (!next) return;
    it.cur = next;
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
    it.zone = zone;
    replace(it.chip, h('span.chip', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.measure.pending')));
    const cacheKey = `${ctx.project}/${ctx.profile}/${ctx.key}/${attempt.id}@base:${zone}:${it.color}`;
    requestMeasure(cacheKey, () => api.measure(ctx.project, ctx.profile, ctx.key, attempt.id, { zone, text: it.color, base: true }))
      .then((res) => { if (!closed && it.zone === zone) renderMeasure(it.chip, res, { paletteMin: ctx.brand && ctx.brand.paletteMin }, () => measureNow(it)); });
  }

  // --- foco atrapado y cierre ---
  dlg.addEventListener('close', () => {
    closed = true;
    for (const it of items) clearTimeout(it.timer);
    if (observer) observer.disconnect();
    window.removeEventListener('resize', layoutBoxes);
    dlg.remove();
  });
  // el pedido se recarga al aplicar y la tarjeta se rehace: si el botón ya no está, la tarjeta del intento
  trapDialog(dlg, { opener, fallback: () => document.querySelector(`[data-attempt="${attempt.id}"][data-kind="attempt"]`) });

  document.body.append(dlg);
  const observer = ('ResizeObserver' in window) ? new ResizeObserver(layoutBoxes) : null;
  if (observer) observer.observe(img); else window.addEventListener('resize', layoutBoxes);
  img.addEventListener('load', layoutBoxes);
  dlg.showModal();
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
