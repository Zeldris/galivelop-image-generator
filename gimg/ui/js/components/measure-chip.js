/* Chip de medida de marca (D31) por intento: GET …/a/{id}/measure. ffmpeg cuesta y el servidor serializa las
   pesadas (una a la vez; 409 measure.busy si espera más de 60 s), así que:
   - se pide de una en una (cola propia) y solo cuando la tarjeta entra en pantalla (IntersectionObserver);
   - se guarda en memoria por intento (y por versión de la imagen: recomponer la invalida);
   - con measure.busy se reintenta a los 5 s, tres veces; después queda un botón «Medir».
   Umbrales: contraste WCAG ≥ 4,5 ok, ≥ 3 ámbar, menos rojo; paleta ≥ `brand.paletteMin` (72 por defecto, calibrado en
   docs/records/contenido/calibracion-measure.md) ok, ≥ paleteMin − 12 ámbar, menos rojo. */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, ApiError } from '../api.js';
import { imageVersion } from './attempt-util.js';

const cache = new Map();         // cacheKey -> result | Error
const inflight = new Map();      // cacheKey -> Promise de la medida ya encolada o en curso (sin duplicar)
const pending = [];              // [{cacheKey, fetcher, resolve}]
let busy = false;
const BUSY_RETRY_MS = 5000;
const BUSY_TRIES = 3;

async function pump() {
  if (busy || !pending.length) return;
  busy = true;
  const job = pending.shift();
  let result;
  for (let i = 0; i < BUSY_TRIES; i += 1) {
    try { result = await job.fetcher(); break; } catch (e) {
      result = e;
      if (e instanceof ApiError && (e.code === 'measure.busy' || e.code === 'api.heavy_busy')) { await sleep(BUSY_RETRY_MS); continue; }
      break;
    }
  }
  cache.set(job.cacheKey, result);
  busy = false;
  job.resolve(result);
  pump();
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

function requestMeasure(cacheKey, fetcher) {
  if (cache.has(cacheKey)) return Promise.resolve(cache.get(cacheKey));
  if (inflight.has(cacheKey)) return inflight.get(cacheKey);
  const p = new Promise((resolve) => { pending.push({ cacheKey, fetcher, resolve }); pump(); });
  inflight.set(cacheKey, p);
  p.then(() => inflight.delete(cacheKey));
  return p;
}

export function invalidateMeasure(prefix) { for (const k of cache.keys()) if (k.startsWith(prefix)) cache.delete(k); }

const observer = ('IntersectionObserver' in window)
  ? new IntersectionObserver((entries) => {
    for (const en of entries) if (en.isIntersecting) { observer.unobserve(en.target); en.target.dispatchEvent(new CustomEvent('gvig:visible')); }
  }, { rootMargin: '200px' })
  : null;

/**
 * ctx: {project, profile, key, zone?, textColor?, paletteMin?}; attempt: registro del intento (con `image`, `compose`).
 * Devuelve el nodo del chip; mide al entrar en pantalla.
 */
export function measureChip(ctx, attempt) {
  const node = h('span.measure', { aria: { live: 'off' } });
  const version = imageVersion(attempt);
  const cacheKey = `${ctx.project}/${ctx.profile}/${ctx.key}/${attempt.id}@${version}`;
  const run = () => {
    replace(node, h('span.chip', { title: t('ui.measure.pending') }, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.measure.pending')));
    requestMeasure(cacheKey, () => api.measure(ctx.project, ctx.profile, ctx.key, attempt.id, {
      zone: ctx.zone && ctx.textColor ? ctx.zone : undefined, text: ctx.zone && ctx.textColor ? ctx.textColor : undefined,
    })).then((res) => render(node, res, ctx, run));
  };
  if (cache.has(cacheKey)) render(node, cache.get(cacheKey), ctx, run);
  else if (observer) { replace(node, h('span.chip', {}, t('ui.measure.none'))); node.addEventListener('gvig:visible', run, { once: true }); observer.observe(node); }
  else run();
  return node;
}

export { render as renderMeasure, requestMeasure };

function level(ok, warn) { return ok ? 'ok' : warn ? 'warn' : 'bad'; }
const worse = (a, b) => (['bad', 'warn', 'ok'].indexOf(a) <= ['bad', 'warn', 'ok'].indexOf(b) ? a : b);

function render(node, res, ctx, retry) {
  if (res instanceof Error) {
    replace(node,
      h('span.chip.chip-warn', { title: res.message }, t('ui.measure.failed')),
      h('button.btn.btn-ghost', { type: 'button', onclick: () => { cache.delete([...cache.keys()].find((k) => cache.get(k) === res)); retry(); } }, t('ui.measure.retry')));
    return;
  }
  const paletteMin = Number.isFinite(ctx.paletteMin) ? ctx.paletteMin : 72;
  const pct = res.palette ? res.palette.pct : null;
  const worst = res.contrast ? res.contrast.worst : null;
  let lvl = 'ok';
  const parts = [];
  if (worst !== null && worst !== undefined) { parts.push(`${worst.toFixed(1)}:1`); lvl = worse(lvl, level(worst >= 4.5, worst >= 3)); }
  if (pct !== null && pct !== undefined) { parts.push(`${Math.round(pct)} %`); lvl = worse(lvl, level(pct >= paletteMin, pct >= paletteMin - 12)); }
  const title = worst !== null && worst !== undefined
    ? t('ui.measure.title', { c: res.contrast.mean.toFixed(1), w: worst.toFixed(1), p: Math.round(pct ?? 0) })
    : t('ui.measure.onlyPalette', { p: Math.round(pct ?? 0) });
  const id = `measure-detail-${++detailSeq}`;
  const lv = (l) => t(`ui.measure.level${l[0].toUpperCase()}${l.slice(1)}`);
  const lines = [];
  if (worst !== null && worst !== undefined) {
    const mean = res.contrast.mean;
    lines.push(t('ui.measure.mean', { c: mean.toFixed(1), l: lv(level(mean >= 4.5, mean >= 3)) }));
    lines.push(t('ui.measure.worst', { w: worst.toFixed(1), l: lv(level(worst >= 4.5, worst >= 3)) }));
  } else lines.push(t('ui.measure.noContrast'));
  if (pct !== null && pct !== undefined) lines.push(t('ui.measure.palette', { p: Math.round(pct), m: paletteMin, l: lv(level(pct >= paletteMin, pct >= paletteMin - 12)) }));
  const detail = h('div.measure-detail', { id, popover: 'auto', role: 'group', aria: { label: t('ui.measure.detail') } }, lines.map((l) => h('p', {}, l)));
  const chip = h('button.chip', { type: 'button', class: `chip-${lvl}`, title, popovertarget: id, aria: { expanded: 'false', controls: id, label: `${t('ui.measure.label')}: ${title}` } }, parts.join(' · ') || '—');
  detail.addEventListener('toggle', (ev) => {
    const open = ev.newState === 'open';
    chip.setAttribute('aria-expanded', String(open));
    if (open) placeDetail(chip, detail);
  });
  replace(node, chip, detail);
}

let detailSeq = 0;

/** Bajo el chip, dentro de la ventana (el popover está en la capa superior: posición fija). */
function placeDetail(chip, detail) {
  const r = chip.getBoundingClientRect();
  const w = Math.min(detail.offsetWidth || 320, window.innerWidth - 16);
  detail.style.left = `${Math.max(8, Math.min(r.left, window.innerWidth - w - 8))}px`;
  const below = r.bottom + 6;
  detail.style.top = `${below + detail.offsetHeight > window.innerHeight - 8 ? Math.max(8, r.top - 6 - detail.offsetHeight) : below}px`;
}
