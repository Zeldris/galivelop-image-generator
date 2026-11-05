/* Estado compartido mínimo: la cola (la sondea queue-poll.js) y comodidades del navegador (tema, filtros,
   «ver compuesta/fondo»). Lo que importa (veredictos, notas, elegida, textos) vive en la API, no aquí. */

const state = {
  queue: [],            // entradas de GET /api/queue, tal cual
  queueAt: null,        // Date.now() del último sondeo bueno
  showRaw: false,       // galería: ver el fondo crudo en vez de la compuesta
  filters: {},          // por proyecto: {profile, state}
};
const subs = new Map();

export function get(key) { return state[key]; }

export function set(key, value) {
  state[key] = value;
  for (const fn of subs.get(key) || []) fn(value);
}

export function subscribe(key, fn) {
  if (!subs.has(key)) subs.set(key, new Set());
  subs.get(key).add(fn);
  return () => subs.get(key).delete(fn);
}

/** Entradas de la cola de un pedido concreto. */
export function queueOf(project, profile, key) {
  return state.queue.filter((e) => e.project === project && e.profile === profile && e.key === key);
}

export function queueCounts() {
  const c = { running: 0, queued: 0, failed: 0, done: 0 };
  for (const e of state.queue) if (e.state in c) c[e.state] += 1;
  return c;
}
