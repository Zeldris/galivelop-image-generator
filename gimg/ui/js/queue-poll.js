/* Sondeo de GET /api/queue cada 3 s (docs/interfaz/propuesta.md «Técnica»): mantiene store.queue y avisa de las
   transiciones (terminado, fallido, cancelado) para los avisos y para refrescar el pedido abierto.
   Se para con la pestaña oculta y vuelve al mostrarla; mientras sondea, el servicio no se apaga por inactividad. */

import { api, OfflineError } from './api.js';
import * as store from './store.js';

export const INTERVAL_MS = 3000;
const listeners = { finished: new Set(), failed: new Set(), cancelled: new Set(), changed: new Set() };
let timer = null;
let known = new Map(); // id -> state del último sondeo
let running = false;

// Contador de cambios de pausa hechos desde aquí (el botón): un GET /api/health lanzado antes de un cambio no debe
// reescribir `queuePaused` con el valor viejo si responde después.
let pauseGen = 0;
export function notePauseChange() { pauseGen += 1; }

export function on(event, fn) { listeners[event].add(fn); return () => listeners[event].delete(fn); }

function emit(event, entry) { for (const fn of listeners[event]) fn(entry); }

export async function refreshNow() {
  let entries;
  // la pausa se lee en GET /api/health, a la vez que la cola; si no responde, se queda lo último sabido
  const gen = pauseGen;
  const health = api.health().then((hth) => {
    if (gen === pauseGen && hth && typeof hth.paused === 'boolean' && hth.paused !== store.get('queuePaused')) store.set('queuePaused', hth.paused);
  }, () => {});
  try {
    entries = await api.queue();
  } catch (e) {
    if (!(e instanceof OfflineError)) console.warn('queue', e);
    return false;
  } finally {
    await health;
  }
  if (!Array.isArray(entries)) return false;
  const next = new Map();
  let changed = known.size !== entries.length;
  for (const e of entries) {
    next.set(e.id, e.state);
    const before = known.get(e.id);
    if (before !== e.state) changed = true;
    if (before && before !== e.state) {
      if (e.state === 'done') emit('finished', e);
      else if (e.state === 'failed') emit('failed', e);
      else if (e.state === 'cancelled') emit('cancelled', e);
    }
  }
  known = next;
  store.set('queue', entries);
  store.set('queueAt', Date.now());
  if (changed || entries.some((e) => e.state === 'running')) emit('changed', entries);
  return true;
}

function schedule() {
  clearTimeout(timer);
  if (!running || document.visibilityState === 'hidden') return;
  timer = setTimeout(async () => { await refreshNow(); schedule(); }, INTERVAL_MS);
}

export function start() {
  if (running) return;
  running = true;
  document.addEventListener('visibilitychange', onVisibility);
  refreshNow().then(schedule);
}

export function stop() {
  running = false;
  clearTimeout(timer);
  document.removeEventListener('visibilitychange', onVisibility);
}

function onVisibility() {
  if (document.visibilityState === 'visible') { refreshNow().then(schedule); } else { clearTimeout(timer); }
}
