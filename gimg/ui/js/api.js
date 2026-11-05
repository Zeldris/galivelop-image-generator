/* Cliente de la API local de gimg (docs/plan.md «F3 en detalle»).
   - Toda petición lleva `?lang=` (el idioma del selector) y, si escribe, `Content-Type: application/json`.
   - Un error de la API llega como ApiError {status, code, params, message, errors}; la red caída, como OfflineError.
   - El transporte se puede sustituir (`setTransport`) para el prototipo sin servidor (`?mock=1`) y para los tests. */

export class ApiError extends Error {
  constructor(status, body) {
    const err = (body && body.error) || {};
    super(err.message || `HTTP ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.code = err.code || 'api.unexpected';
    this.params = err.params || {};
    this.errors = err.errors || null;
  }
}

export class OfflineError extends Error {
  constructor(cause) { super('offline'); this.name = 'OfflineError'; this.cause = cause; }
}

const state = { lang: 'es', transport: null, offline: false };
const offlineListeners = new Set();

export function setLang(lang) { state.lang = lang; }
export function getLang() { return state.lang; }

/** transport(method, path, body) -> {status, json|blob}. Si es null se usa fetch. */
export function setTransport(fn) { state.transport = fn; }

/** Avisa de cambios de conectividad: fn(isOffline). */
export function onOffline(fn) { offlineListeners.add(fn); return () => offlineListeners.delete(fn); }
function setOffline(v) {
  if (state.offline === v) return;
  state.offline = v;
  for (const fn of offlineListeners) fn(v);
}
export function isOffline() { return state.offline; }

function withLang(path) {
  const sep = path.includes('?') ? '&' : '?';
  return `${path}${sep}lang=${encodeURIComponent(state.lang)}`;
}

async function request(method, path, body) {
  const url = withLang(path);
  if (state.transport) {
    const res = await state.transport(method, url, body);
    if (res.status >= 400) throw new ApiError(res.status, res.json);
    setOffline(false);
    return res.json;
  }
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
      body: body !== undefined ? JSON.stringify(body) : undefined,
      cache: 'no-store',
    });
  } catch (e) {
    setOffline(true);
    throw new OfflineError(e);
  }
  setOffline(false);
  if (res.status === 204) return null;
  let json = null;
  try { json = await res.json(); } catch { json = null; }
  if (!res.ok) throw new ApiError(res.status, json);
  return json;
}

export const get = (path) => request('GET', path);
export const post = (path, body = {}) => request('POST', path, body);
export const put = (path, body = {}) => request('PUT', path, body);
export const del = (path) => request('DELETE', path);

/* ---- rutas: el segmento de la clave va codificado en un solo segmento (`fauna%2Faullador-rojo`) ---- */
const enc = encodeURIComponent;
export const paths = {
  health: () => '/api/health',
  locales: (lang) => `/api/locales/${enc(lang)}`,
  projects: () => '/api/projects',
  project: (p) => `/api/projects/${enc(p)}`,
  orders: (p, q = {}) => {
    const qs = Object.entries(q).filter(([, v]) => v !== undefined && v !== null && v !== '')
      .map(([k, v]) => `${enc(k)}=${enc(v)}`).join('&');
    return `/api/projects/${enc(p)}/orders${qs ? '?' + qs : ''}`;
  },
  newOrder: (p) => `/api/projects/${enc(p)}/orders`,
  order: (p, profile, key) => `/api/projects/${enc(p)}/orders/${enc(profile)}/${enc(key)}`,
  text: (p, profile, key) => `${paths.order(p, profile, key)}/text`,
  attempts: (p, profile, key) => `${paths.order(p, profile, key)}/attempts`,
  attempt: (p, profile, key, id) => `${paths.order(p, profile, key)}/attempts/${enc(id)}`,
  mark: (p, profile, key, id) => `${paths.attempt(p, profile, key, id)}/mark`,
  note: (p, profile, key, id) => `${paths.attempt(p, profile, key, id)}/note`,
  compose: (p, profile, key, id) => `${paths.attempt(p, profile, key, id)}/compose`,
  image: (p, profile, key, id, { raw = false, v = '' } = {}) =>
    `${paths.attempt(p, profile, key, id)}/image${raw ? '?raw=1' : ''}${v ? (raw ? '&' : '?') + 'v=' + enc(v) : ''}`,
  log: (p, profile, key, id) => `${paths.attempt(p, profile, key, id)}/log`,
  measure: (p, profile, key, id, { zone, text, raw, base } = {}) => {
    const q = [];
    if (zone) q.push('zone=' + enc(zone));
    if (text) q.push('text=' + enc(text));
    if (raw) q.push('raw=1');
    if (base) q.push('base=1');
    return `${paths.attempt(p, profile, key, id)}/measure${q.length ? '?' + q.join('&') : ''}`;
  },
  choose: (p, profile, key) => `${paths.order(p, profile, key)}/choose`,
  undo: (p, profile, key) => `${paths.order(p, profile, key)}/undo`,
  asset: (p, profile, kind, id) => `/api/projects/${enc(p)}/profiles/${enc(profile)}/assets/${enc(kind)}${id ? '?id=' + enc(id) : ''}`,
  templates: (p, profile) => `/api/projects/${enc(p)}/profiles/${enc(profile)}/templates`,
  template: (p, profile, id) => `${paths.templates(p, profile)}/${enc(id)}`,
  queue: (state) => `/api/queue${state ? '?state=' + enc(state) : ''}`,
  cancel: (id) => `/api/queue/${enc(id)}/cancel`,
  move: (id) => `/api/queue/${enc(id)}/move`,
  clear: () => '/api/queue/clear',
  models: () => '/api/models',
  check: (p) => `/api/projects/${enc(p)}/check`,
  preview: (id) => `/api/queue/${enc(id)}/preview?t=${Date.now()}`,
};

/* ---- llamadas con nombre (lo que consumen los componentes) ---- */
export const api = {
  health: () => get(paths.health()),
  locales: (lang) => get(paths.locales(lang)),
  projects: () => get(paths.projects()),
  project: (p) => get(paths.project(p)),
  orders: (p, q) => get(paths.orders(p, q)),
  order: (p, profile, key) => get(paths.order(p, profile, key)),
  setText: (p, profile, key, text) => put(paths.text(p, profile, key), { text }),
  newAttempts: (p, profile, key, spec) => post(paths.attempts(p, profile, key), spec),
  mark: (p, profile, key, id, st) => post(paths.mark(p, profile, key, id), { state: st }),
  note: (p, profile, key, id, text) => post(paths.note(p, profile, key, id), { text }),
  templates: (p, profile) => get(paths.templates(p, profile)),
  template: (p, profile, id) => get(paths.template(p, profile, id)),
  deleteTemplate: (p, profile, id) => del(paths.template(p, profile, id)),
  deleteAttempt: (p, profile, key, id) => del(paths.attempt(p, profile, key, id)),
  deleteCompose: (p, profile, key, id) => del(paths.compose(p, profile, key, id)),
  saveTemplate: (p, profile, body) => post(paths.templates(p, profile), body),
  compose: (p, profile, key, id, body = {}) => post(paths.compose(p, profile, key, id), body),
  measure: (p, profile, key, id, opts) => get(paths.measure(p, profile, key, id, opts)),
  choose: (p, profile, key, attempt) => post(paths.choose(p, profile, key), { attempt }),
  undo: (p, profile, key) => post(paths.undo(p, profile, key), {}),
  queue: (state) => get(paths.queue(state)),
  cancel: (id) => post(paths.cancel(id), {}),
  move: (id, to) => post(paths.move(id), { to }),
  clearQueue: (project) => post(paths.clear(), project ? { project } : {}),
  models: () => get(paths.models()),
  check: (p) => get(paths.check(p)),
  newOrder: (p, body) => post(paths.newOrder(p), body),
};

/** Texto legible de cualquier fallo, para los avisos (el mensaje de la API ya viene en el idioma pedido). */
export function describeError(e, t) {
  if (e instanceof OfflineError) return t('ui.offline.title');
  if (e instanceof ApiError) return e.message || t('ui.error.code', { code: e.code });
  return t('ui.error.generic', { message: e && e.message ? e.message : String(e) });
}
