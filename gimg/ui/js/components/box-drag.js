/* Cajas que se arrastran, se redimensionan y se mueven con el teclado (las usan layout-editor.js y crop-editor.js).
   - Coordenadas en píxeles de un lienzo W×H; lo que se pinta se escala con `scale()` (píxeles de pantalla por píxel).
   - Puntero: pointer events con captura (arrastrar la caja = mover; las asas de las esquinas = redimensionar).
   - Teclado: flechas mueven; con `size` cambian el ancho y el alto; el paso es `step`. */

export const STEP = 1;
export const STEP_BIG = 10;
export const CORNERS = ['nw', 'ne', 'sw', 'se'];
export const ARROWS = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };

export const clamp = (v, lo, hi) => Math.min(Math.max(lo, hi), Math.max(lo, v));
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

/**
 * Empieza un arrastre con captura de puntero desde un `pointerdown`. opts: {
 *   getBox(): la caja actual; setBox(box): la caja nueva (se llama en cada movimiento); scale(): píxeles de pantalla por
 *   píxel (0 = aún sin medir); W, H: el lienzo; corner: null = mover, `nw|ne|sw|se` = redimensionar;
 *   lock(ev): ¿se mantiene la proporción al redimensionar?; busy(): ¿se ignora?; focus: nodo que recibe el foco;
 *   onEnd(): al soltar }.
 */
export function startBoxDrag(ev, opts) {
  if ((opts.busy && opts.busy()) || (ev.button !== undefined && ev.button !== 0)) return;
  ev.preventDefault();
  ev.stopPropagation();
  if (opts.focus) opts.focus.focus();
  const target = ev.currentTarget;
  try { target.setPointerCapture(ev.pointerId); } catch { /* sin captura el arrastre sigue mientras el puntero esté encima */ }
  const origin = { x: ev.clientX, y: ev.clientY, box: { ...opts.getBox() } };
  const onMove = (m) => {
    const k = opts.scale();
    if (!k) return;
    const dx = Math.round((m.clientX - origin.x) / k);
    const dy = Math.round((m.clientY - origin.y) / k);
    opts.setBox(opts.corner ? resizeBox(origin.box, opts.corner, dx, dy, opts.lock ? opts.lock(m) : false, opts.W, opts.H) : moveBox(origin.box, dx, dy, opts.W, opts.H));
  };
  const onEnd = () => {
    target.removeEventListener('pointermove', onMove);
    target.removeEventListener('pointerup', onEnd);
    target.removeEventListener('pointercancel', onEnd);
    try { target.releasePointerCapture(ev.pointerId); } catch { /* ya soltado */ }
    if (opts.onEnd) opts.onEnd();
  };
  target.addEventListener('pointermove', onMove);
  target.addEventListener('pointerup', onEnd);
  target.addEventListener('pointercancel', onEnd);
}

/**
 * Una flecha sobre una caja: devuelve la caja nueva (y detiene el evento) o null si la tecla no cuenta.
 * opts: {W, H, step, size}: `step` píxeles por pulsación; `size`: cambia el tamaño en vez de mover.
 */
export function boxKey(ev, box, opts) {
  const dir = ARROWS[ev.key];
  if (!dir || ev.ctrlKey || ev.metaKey) return null;
  ev.preventDefault();
  const step = opts.step;
  return opts.size ? sizeBox(box, dir[0] * step, dir[1] * step, opts.W, opts.H) : moveBox(box, dir[0] * step, dir[1] * step, opts.W, opts.H);
}
