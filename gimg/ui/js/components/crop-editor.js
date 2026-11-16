/* Editor de recorte (FM 0.6.0, docs/interfaz/marca.md §2.6): un `dialog` modal sobre la imagen CRUDA del intento
   (`…/image?raw=1`) con una sola caja. Guarda el trozo como intento derivado (`POST …/attempts/{id}/crop`); el original
   no se toca.
   - Coordenadas en píxeles de la imagen cruda (`naturalWidth`×`naturalHeight`); la caja es `[x0, y0, x1, y1]` con x1 e
     y1 excluidos, como la API. Lo que se pinta se escala por `img.clientWidth / naturalWidth`.
   - Proporción: la del perfil de destino (`width`×`height`, como el servidor) o libre. Rejilla libre/2×2/3×3: sus celdas
     son botones que colocan la caja. Paso 1/10/50 px y modo mover/tamaño para las flechas, sin Mayús ni Alt (en teclado
     siguen valiendo los gestos de layout-editor: Mayús+flechas 10 px, Alt+flechas el tamaño).
   - Los números de la caja se pueden escribir: una caja fuera de la imagen o sin área bloquea con su motivo; una salida
     que amplía más de ×2 solo avisa. La vista previa es un `<canvas>` del cliente (sin servidor).
   - Los errores de la API van dentro del diálogo (un `dialog` modal tapa el contenedor de toasts). */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError, ApiError, paths } from '../api.js';
import { toastError } from './toast.js';
import { imageVersion } from './attempt-util.js';
import { KEY_PATTERN, MAX_KEY } from './new-order.js';
import { CORNERS, STEP_BIG, clamp, startBoxDrag, boxKey } from './box-drag.js';

export const RATIO_TOLERANCE = 0.01;
export const ENLARGE_WARN = 2;
export const STEPS = [1, 10, 50];
export const GRIDS = [['free', 'ui.crop.gridFree'], ['2', 'ui.crop.grid2'], ['3', 'ui.crop.grid3']];
const FOCUSABLE = 'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), [tabindex="0"]';
const PREVIEW_MAX = 240;

const gcd = (a, b) => (b ? gcd(b, a % b) : a);

/** `{x, y, w, h}` -> `[x0, y0, x1, y1]`. */
export const toBox = (b) => [b.x, b.y, b.x + b.w, b.y + b.h];

/** Motivo por el que la caja no se puede guardar, o null. `size` = {w, h} de la imagen; `ratio` = proporción exigida
    (null = libre). Una clave de `ui.crop.blocked.*`: `area`, `outside` o `ratio`. */
export function blockedReason(b, size, ratio) {
  const [x0, y0, x1, y1] = toBox(b);
  if (![x0, y0, x1, y1].every(Number.isInteger) || x1 <= x0 || y1 <= y0) return 'area';
  if (x0 < 0 || y0 < 0 || x1 > size.w || y1 > size.h) return 'outside';
  if (ratio && Math.abs(b.w / b.h - ratio) > RATIO_TOLERANCE * ratio) return 'ratio';
  return null;
}

/** Cuánto amplía la salida (`outW`×`outH`) la caja `b`: el mayor de los dos factores. */
export function enlargement(b, outW, outH) { return Math.max(outW / b.w, outH / b.h); }

/** La caja más grande de proporción `ratio` que cabe en `size`, centrada en `c` ({x, y}) sin salir de la imagen. */
export function fitRatio(ratio, size, c) {
  let w = size.w;
  let hh = Math.round(w / ratio);
  if (hh > size.h) { hh = size.h; w = Math.round(hh * ratio); }
  w = Math.max(1, Math.min(w, size.w));
  hh = Math.max(1, Math.min(hh, size.h));
  return { x: clamp(Math.round(c.x - w / 2), 0, size.w - w), y: clamp(Math.round(c.y - hh / 2), 0, size.h - hh), w, h: hh };
}

/** La caja `b` con la proporción `ratio`: manda el eje `axis` (`w` o `h`) y, con `clip`, se recorta si no cabe en `size`
    (lo escrito a mano no se recorta: la caja que sale de la imagen se bloquea con su motivo). */
export function lockTo(b, ratio, size, axis, clip = true) {
  let w = axis === 'w' ? b.w : Math.round(b.h * ratio);
  let hh = axis === 'w' ? Math.round(b.w / ratio) : b.h;
  if (clip && hh > size.h - b.y) { hh = size.h - b.y; w = Math.round(hh * ratio); }
  if (clip && w > size.w - b.x) { w = size.w - b.x; hh = Math.round(w / ratio); }
  return { x: b.x, y: b.y, w: Math.max(1, w), h: Math.max(1, hh) };
}

/** La celda `i` (0-based, por filas) de una rejilla `n`×`n` sobre `size`, en píxeles. */
export function cellBox(n, i, size) {
  const col = i % n;
  const row = Math.floor(i / n);
  const edge = (k, total) => Math.round((k * total) / n);
  return { x: edge(col, size.w), y: edge(row, size.h), w: edge(col + 1, size.w) - edge(col, size.w), h: edge(row + 1, size.h) - edge(row, size.h) };
}

/**
 * Abre el editor. ctx: el del pedido ({project, profile, key, order, profileCfg, profiles, actions: {crop}});
 * attempt: el intento; opener: el botón que lo abrió (recupera el foco al cerrar).
 */
export function openCropEditor(ctx, attempt, opener) {
  const profiles = ctx.profiles && Object.keys(ctx.profiles).length ? ctx.profiles : { [ctx.profile]: ctx.profileCfg || {} };
  let size = null; // {w, h} de la imagen cruda, cuando carga
  let box = { x: 0, y: 0, w: 1, h: 1 };
  let locked = true;
  let grid = 'free';
  let step = 10;
  let mode = 'move';
  let busy = false;
  let closed = false;

  const src = paths.image(ctx.project, ctx.profile, ctx.key, attempt.id, { raw: true, v: imageVersion(attempt) });
  const img = h('img.ed-img', { src, alt: '', draggable: 'false' });
  const boxNode = h('div.crop-box', { tabindex: 0, role: 'group', hidden: true }, CORNERS.map((c) => h('span.ed-handle.crop-handle', { class: `h-${c}`, data: { corner: c }, aria: { hidden: true } })));
  const gridNode = h('div.crop-grid', { aria: { hidden: true } });
  // el margen de 22 px del escenario deja sitio a la mitad de las asas de 44 px que sobresalen de la caja en el borde
  const stage = h('div.ed-stage.crop-stage', { role: 'group', aria: { label: t('ui.crop.stage', { id: attempt.id }), describedby: 'crop-hint' } }, h('div.crop-inner', {}, img, gridNode, boxNode));
  const loading = h('p.hint', { role: 'status' }, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.crop.loading'));
  const error = h('p.notice.notice-bad', { role: 'alert', hidden: true });
  const status = h('p.notice.notice-warn', { role: 'status', hidden: true });
  const warn = h('p.notice.notice-warn.small', { role: 'status', hidden: true });
  const composeNote = h('p.notice.notice-warn.crop-compose', { role: 'status', hidden: true }, t('ui.crop.compose'));
  // un perfil que compone (texto y logo) no admite recorte: el servidor lo rechaza con `crop.compose_unsupported`
  const composes = (cfg) => Boolean(cfg && cfg.compose);

  const radios = (name, options, current, onPick) => options.map(([value, label]) => {
    const input = h('input', { type: 'radio', name, value, checked: value === current });
    input.addEventListener('change', () => { if (input.checked) onPick(value); });
    return h('label.check', {}, input, h('span', {}, label));
  });
  const ratioProfile = () => ((toBox_.hidden ? null : profiles[toProfile.value]) || ctx.profileCfg || {});
  const ratioText = () => {
    const p = ratioProfile();
    const d = gcd(p.width, p.height) || 1;
    return `${p.width / d}:${p.height / d}`;
  };
  const ratioValue = () => (locked ? ratioProfile().width / ratioProfile().height : null);

  const lockRadios = radios('crop-ratio', [['1', t('ui.crop.ratioLocked', { ratio: '' })], ['0', t('ui.crop.ratioFree')]], '1', (v) => {
    locked = v === '1';
    if (locked && size) box = lockTo(box, ratioValue(), size, 'w');
    refresh();
  });
  const ratioLabel = lockRadios[0].querySelector('span');
  const gridRadios = radios('crop-grid', GRIDS.map(([v, k]) => [v, t(k)]), grid, (v) => { grid = v; paintGrid(); });
  const modeRadios = radios('crop-mode', [['move', t('ui.crop.modeMove')], ['size', t('ui.crop.modeSize')]], mode, (v) => { mode = v; });
  const stepSel = h('select', { id: 'crop-step', aria: { label: t('ui.crop.step') } }, STEPS.map((n) => h('option', { value: n, selected: n === step }, t('ui.crop.stepPx', { n }))));
  stepSel.addEventListener('change', () => { step = Number(stepSel.value); });
  const cells = h('div.crop-cells', {});

  const nums = ['x0', 'y0', 'x1', 'y1'].map((name) => {
    const input = h('input', { type: 'number', step: 1, data: { field: name }, aria: { label: t('ui.crop.field', { name }) } });
    input.addEventListener('change', () => typed(name, input));
    return { name, input };
  });
  const numNodes = h('div.crop-nums', {}, nums.map((n) => h('label', {}, h('span.label', {}, n.name), n.input)));
  const output = h('output.ed-nums', { id: 'crop-output' });
  const canvas = h('canvas.crop-preview', { role: 'img', aria: { label: t('ui.crop.previewAlt') } });

  const save = h('button.btn.btn-primary', { type: 'button', onclick: () => { if (toBox_.hidden) run(() => ctx.actions.crop(attempt, payload(null)), true); } }, t('ui.crop.save'));
  const cancel = h('button.btn', { type: 'button', onclick: () => dlg.close() }, t('ui.editor.cancel'));
  const close = h('button.btn.btn-ghost', { type: 'button', onclick: () => dlg.close() }, t('ui.actions.close'));
  const moveBtn = h('button.btn', { type: 'button', aria: { expanded: 'false', controls: 'crop-to' }, onclick: () => { toBox_.hidden = !toBox_.hidden; moveBtn.setAttribute('aria-expanded', String(!toBox_.hidden)); if (locked && size) box = lockTo(box, ratioValue(), size, 'w'); if (!toBox_.hidden) toKey.focus(); refresh(); } }, t('ui.crop.moveTo'));
  const toProfile = h('select', { id: 'crop-to-profile' }, Object.keys(profiles).map((p) => h('option', { value: p, selected: p === ctx.profile }, p)));
  toProfile.addEventListener('change', () => { if (locked && size) box = lockTo(box, ratioValue(), size, 'w'); refresh(); });
  const toKey = h('input', { id: 'crop-to-key', type: 'text', autocomplete: 'off', spellcheck: 'false', maxlength: MAX_KEY, aria: { describedby: 'crop-to-hint' } });
  const toProblem = h('p.field-error', { role: 'alert' });
  const toGo = h('button.btn.btn-primary', { type: 'button', onclick: () => {
    const name = toKey.value.trim();
    if (!KEY_PATTERN.test(name) || name.length > MAX_KEY) { toProblem.textContent = t('ui.crop.toKeyInvalid'); toKey.focus(); return; }
    toProblem.textContent = '';
    run(() => ctx.actions.crop(attempt, payload({ profile: toProfile.value, key: name })), true);
  } }, t('ui.crop.toGo'));
  const toBox_ = h('fieldset.field.crop-to', { id: 'crop-to', hidden: true },
    h('div.field', {}, h('label', { for: 'crop-to-profile' }, t('ui.crop.toProfile')), toProfile),
    h('div.field', {}, h('label', { for: 'crop-to-key' }, t('ui.crop.toKey')), toKey, h('p.hint', { id: 'crop-to-hint' }, t('ui.crop.toHint')), toProblem), toGo);

  // «Repetir la misma caja en…»: los intentos de la tanda de origen (el pedido del que salió este derivado), sin derivados
  // y sin el propio intento de origen; si el origen es otro pedido, se pide y el recorte lleva `to` hacia el pedido visto
  const df = attempt.derivedFrom;
  const sameOrder = Boolean(df) && df.profile === ctx.profile && df.key === ctx.key;
  let others = [];
  const repeatSel = h('select', { id: 'crop-repeat-pick', aria: { label: t('ui.crop.repeatPick') } });
  const repeatGo = h('button.btn', { type: 'button', onclick: () => {
    const target = others.find((a) => a.id === Number(repeatSel.value));
    if (!target) return;
    const body = { box: df.box, lockRatio: df.lockRatio !== false, ...(sameOrder ? {} : { to: { profile: ctx.profile, key: ctx.key } }) };
    run(() => ctx.actions.crop(target, body, sameOrder ? null : { profile: df.profile, key: df.key }), true);
  } }, t('ui.crop.repeatGo'));
  const repeat = df ? h('div.crop-repeat', { hidden: true }, h('label', { for: 'crop-repeat-pick' }, t('ui.crop.repeat')), repeatSel, repeatGo) : null;
  const setOthers = (list, late) => {
    others = (list || []).filter((a) => !a.derivedFrom && a.id !== df.attempt && (a.raw || a.image));
    repeatSel.replaceChildren(...others.map((a) => h('option', { value: a.id }, `q${a.id}`)));
    repeat.hidden = !others.length;
    if (late && !closed) refresh();
  };
  if (df && sameOrder) setOthers(ctx.order.attempts);
  else if (df) api.order(ctx.project, df.profile, df.key).then((o) => setOthers(o.attempts, true), () => {});

  const dlg = h('dialog.editor.crop', { aria: { labelledby: 'crop-title' } },
    h('div.ed-head', {}, h('h2', { id: 'crop-title' }, t('ui.crop.title', { id: attempt.id })), h('span.grow'), close),
    h('div.ed-body', {},
      h('div.ed-main', {}, loading, stage, h('p.hint', { id: 'crop-hint' }, t('ui.crop.hint'))),
      h('aside.ed-side', {},
        h('fieldset.field', {}, h('legend.label', {}, t('ui.crop.ratio')), lockRadios),
        h('fieldset.field', {}, h('legend.label', {}, t('ui.crop.grid')), gridRadios, cells),
        h('fieldset.field', {}, h('legend.label', {}, t('ui.crop.mode')), modeRadios, h('label.crop-step', {}, h('span.label', {}, t('ui.crop.step')), stepSel)),
        h('fieldset.field', {}, h('legend.label', {}, t('ui.crop.boxFields')), numNodes),
        h('div.field', {}, h('span.label', {}, t('ui.crop.output')), output),
        h('div.field', {}, h('span.label', {}, t('ui.crop.preview')), canvas),
        composeNote, status, warn, error)),
    h('div.crop-foot', {},
      h('p.hint', {}, t('ui.crop.untouched')),
      h('div.crop-actions', {}, cancel, moveBtn, save), toBox_, repeat));

  // --- estado -> pantalla ---
  const boxFor = (b) => ({ x0: b.x, y0: b.y, x1: b.x + b.w, y1: b.y + b.h });
  const scale = () => (size ? img.clientWidth / size.w : 0);
  const out = () => {
    if (!locked) return { w: box.w, h: box.h };
    const p = ratioProfile();
    return { w: p.width, h: p.height };
  };

  function payload(to) {
    return { box: toBox(box), lockRatio: locked, ...(to ? { to } : {}) };
  }

  function layoutBox() {
    const k = scale();
    if (!k) return;
    const s = boxNode.style;
    s.left = `${box.x * k}px`; s.top = `${box.y * k}px`; s.width = `${box.w * k}px`; s.height = `${box.h * k}px`;
  }

  function paintGrid() {
    gridNode.replaceChildren();
    cells.replaceChildren();
    const n = grid === 'free' ? 0 : Number(grid);
    gridNode.hidden = !n;
    cells.hidden = !n;
    if (!n) return;
    gridNode.style.setProperty('--n', String(n));
    cells.style.setProperty('--n', String(n));
    for (let i = 0; i < n * n; i += 1) {
      gridNode.append(h('span.crop-cell'));
      cells.append(h('button.btn', { type: 'button', data: { cell: i + 1 }, aria: { label: t('ui.crop.cell', { n: i + 1 }) }, disabled: !size || busy, onclick: () => putInCell(i, n) }, String(i + 1)));
    }
  }

  function putInCell(i, n) {
    const cell = cellBox(n, i, size);
    box = locked ? fitRatio(ratioValue(), { w: cell.w, h: cell.h }, { x: cell.w / 2, y: cell.h / 2 }) : cell;
    if (locked) box = { ...box, x: box.x + cell.x, y: box.y + cell.y };
    refresh();
    boxNode.focus();
  }

  function refresh() {
    ratioLabel.textContent = t('ui.crop.ratioLocked', { ratio: ratioText() });
    layoutBox();
    const b = boxFor(box);
    for (const n of nums) if (document.activeElement !== n.input) n.input.value = String(b[n.name]);
    boxNode.setAttribute('aria-label', t('ui.crop.boxLabel', b));
    const reason = size ? blockedReason(box, size, ratioValue()) : 'area';
    const o = out();
    const k = size && !reason ? enlargement(box, o.w, o.h) : 0;
    output.textContent = size && !reason ? t('ui.crop.outputValue', { w: o.w, h: o.h, scale: k.toFixed(1) }) : '—';
    const saveLocked = composes(ctx.profileCfg);
    const goLocked = composes(profiles[toProfile.value]);
    composeNote.hidden = !(toBox_.hidden ? saveLocked : goLocked);
    status.hidden = !(size && reason);
    if (size && reason) status.textContent = t(`ui.crop.blocked.${reason}`, { w: size.w, h: size.h, ratio: ratioText() });
    warn.hidden = !(k > ENLARGE_WARN);
    if (k > ENLARGE_WARN) warn.textContent = t('ui.crop.small', { scale: k.toFixed(1) });
    // con el panel de destino abierto la caja sigue la proporción del destino: «Guardar» (aquí, en el perfil del pedido) espera a que se cierre
    save.disabled = busy || Boolean(reason) || !size || saveLocked || !toBox_.hidden;
    moveBtn.disabled = busy || !size;
    toGo.disabled = busy || Boolean(reason) || !size || goLocked;
    repeatGo.disabled = busy || !size;
    for (const el of dlg.querySelectorAll('.ed-side input, .ed-side select, .crop-cells button, .crop-foot select, .crop-foot input')) el.disabled = busy || !size;
    paintPreview(reason);
  }

  function paintPreview(reason) {
    const o = out();
    const w = Math.max(1, Math.min(PREVIEW_MAX, o.w));
    const hh = Math.max(1, Math.round((w * o.h) / o.w));
    canvas.width = w;
    canvas.height = hh;
    const g = canvas.getContext('2d');
    if (!g || !size || reason) return;
    g.imageSmoothingQuality = 'high';
    g.drawImage(img, box.x, box.y, box.w, box.h, 0, 0, w, hh);
  }

  function typed(name, input) {
    const v = Number.parseInt(input.value, 10);
    const b = boxFor(box);
    if (!Number.isFinite(v)) { input.value = String(b[name]); return; }
    b[name] = v;
    box = { x: b.x0, y: b.y0, w: b.x1 - b.x0, h: b.y1 - b.y0 };
    if (locked && box.w > 0 && box.h > 0) box = lockTo(box, ratioValue(), size, name[0] === 'x' ? 'w' : 'h', false);
    refresh();
    input.value = String(boxFor(box)[name]); // `refresh` no toca el campo con el foco, que se queda donde está
  }

  function showError(e) {
    const message = e instanceof ApiError && e.code === 'api.heavy_busy' ? t('ui.crop.busy') : describeError(e, t);
    toastError(message);
    error.textContent = message;
    error.hidden = false;
  }

  async function run(fn, andClose) {
    error.hidden = true;
    busy = true;
    refresh();
    try { await fn(); } catch (e) { busy = false; if (!closed) { refresh(); showError(e); } return false; }
    busy = false;
    if (andClose && !closed) dlg.close();
    else if (!closed) refresh();
    return true;
  }

  function ready() {
    if (size || !img.naturalWidth) return;
    size = { w: img.naturalWidth, h: img.naturalHeight };
    loading.hidden = true;
    boxNode.hidden = false;
    box = fitRatio(ratioValue(), size, { x: size.w / 2, y: size.h / 2 });
    paintGrid();
    refresh();
    boxNode.focus();
  }

  // --- puntero y teclado ---
  // con la proporción bloqueada, `resizeBox` redondea ancho y alto por separado y el error se acumula: se rehace el alto
  // desde el ancho (como la ruta del teclado), con la esquina opuesta fija
  const lockedDrag = (b, corner) => {
    const r = lockTo(b, ratioValue(), size, 'w');
    return { x: corner.includes('w') ? Math.max(0, b.x + b.w - r.w) : r.x, y: corner.includes('n') ? Math.max(0, b.y + b.h - r.h) : r.y, w: r.w, h: r.h };
  };
  const drag = (ev, corner) => startBoxDrag(ev, {
    getBox: () => box, setBox: (b) => { box = locked && size && corner ? lockedDrag(b, corner) : b; refresh(); }, scale, W: size ? size.w : 1, H: size ? size.h : 1, corner,
    lock: () => locked, busy: () => busy || !size, focus: boxNode,
  });
  boxNode.addEventListener('pointerdown', (ev) => drag(ev, null));
  for (const handle of boxNode.querySelectorAll('.ed-handle')) handle.addEventListener('pointerdown', (ev) => drag(ev, handle.dataset.corner));
  boxNode.addEventListener('keydown', (ev) => {
    if (busy || !size) return;
    const sizing = ev.altKey || mode === 'size';
    const next = boxKey(ev, box, { W: size.w, H: size.h, step: ev.shiftKey ? STEP_BIG : step, size: sizing });
    if (!next) return;
    box = locked && sizing ? lockTo(next, ratioValue(), size, ev.key === 'ArrowLeft' || ev.key === 'ArrowRight' ? 'w' : 'h') : next;
    refresh();
  });

  // --- foco atrapado y cierre ---
  dlg.addEventListener('keydown', (ev) => {
    ev.stopPropagation(); // los atajos de la galería y los globales no actúan con el editor abierto
    if (ev.key !== 'Tab') return;
    const nodes = [...dlg.querySelectorAll(FOCUSABLE)].filter((n) => n.getClientRects().length > 0);
    if (!nodes.length) return;
    const first = nodes[0];
    const last = nodes[nodes.length - 1];
    if (ev.shiftKey && (document.activeElement === first || document.activeElement === dlg)) { ev.preventDefault(); last.focus(); }
    else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
  });
  dlg.addEventListener('close', () => {
    closed = true;
    if (observer) observer.disconnect();
    dlg.remove();
    const back = opener && opener.isConnected ? opener : document.querySelector(`[data-attempt="${attempt.id}"][data-kind="attempt"]`);
    if (back) back.focus();
  });

  img.addEventListener('load', ready);
  img.addEventListener('error', () => { replace(loading, t('ui.crop.imageError')); loading.setAttribute('role', 'alert'); });
  document.body.append(dlg);
  const observer = ('ResizeObserver' in window) ? new ResizeObserver(layoutBox) : null;
  if (observer) observer.observe(img);
  dlg.showModal();
  paintGrid();
  refresh();
  if (img.complete) ready();
  (size ? boxNode : close).focus();
  return dlg;
}
