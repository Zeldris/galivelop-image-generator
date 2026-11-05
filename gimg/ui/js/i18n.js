/* Textos de la interfaz (D16): se cargan de GET /api/locales/{lang} (todo el gimg/locales/<lang>.json, con las
   claves `ui.*`). Si una clave falta, se devuelve la propia clave: así se ve qué falta sin romper nada.
   Idioma: el guardado en el navegador, si no el del navegador (es/en), si no `es`. */

import { api, setLang as apiSetLang } from './api.js';

export const SUPPORTED = ['es', 'en'];
const STORAGE_KEY = 'gvig.lang';
let current = 'es';
let dict = {};
const listeners = new Set();

export function detect() {
  const saved = safeGet(STORAGE_KEY);
  if (SUPPORTED.includes(saved)) return saved;
  const nav = (navigator.languages || [navigator.language || 'es']).map((l) => String(l).slice(0, 2).toLowerCase());
  return nav.find((l) => SUPPORTED.includes(l)) || 'es';
}

export async function load(lang) {
  const chosen = SUPPORTED.includes(lang) ? lang : 'es';
  apiSetLang(chosen);
  try {
    dict = await api.locales(chosen) || {};
  } catch {
    dict = {}; // sin servicio: las claves hacen de texto hasta que vuelva
  }
  current = chosen;
  document.documentElement.lang = chosen;
  safeSet(STORAGE_KEY, chosen);
  for (const fn of listeners) fn(chosen);
  return chosen;
}

export function lang() { return current; }

/** fn(lang) tras cada cambio de idioma. */
export function onChange(fn) { listeners.add(fn); return () => listeners.delete(fn); }

/** t('ui.queue.running', {n: 2}) → «2 generando». Los huecos son `{nombre}` como en gimg/i18n.py. */
export function t(key, params) {
  let s = Object.prototype.hasOwnProperty.call(dict, key) ? dict[key] : key;
  if (params) s = s.replace(/\{(\w+)\}/g, (m, k) => (k in params ? String(params[k]) : m));
  return s;
}

/** Ayuda para campos de texto de la composición: `ui.text.field.<nombre>` o el nombre tal cual. */
export function fieldLabel(name) {
  const key = `ui.text.field.${name}`;
  const s = t(key);
  return s === key ? name : s;
}

function safeGet(k) { try { return localStorage.getItem(k); } catch { return null; } }
function safeSet(k, v) { try { localStorage.setItem(k, v); } catch { /* sin almacenamiento: no pasa nada */ } }
