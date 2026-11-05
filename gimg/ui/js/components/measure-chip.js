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

const cache = new Map();         // cacheKey -> result | Error
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
      if (e instanceof ApiError && e.code === 'measure.busy') { await sleep(BUSY_RETRY_MS); continue; }
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
  return new Promise((resolve) => { pending.push({ cacheKey, fetcher, resolve }); pump(); });
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
  const version = (attempt.compose && attempt.compose.at) || attempt.image || '';
  const cacheKey = `${ctx.project}/${ctx.profile}/${ctx.key}/${attempt.id}@${version}`;
  const run = () => {
    replace(node, h('span.chip', { title: t('ui.measure.pending') }, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.measure.pending')));
    requestMeasure(cacheKey, () => api.measure(ctx.project, ctx.profile, ctx.key, attempt.id, {
      zone: ctx.zone, text: ctx.zone ? ctx.textColor : undefined,
    })).then((res) => render(node, res, ctx, run));
  };
  if (cache.has(cacheKey)) render(node, cache.get(cacheKey), ctx, run);
  else if (observer) { replace(node, h('span.chip', {}, t('ui.measure.none'))); node.addEventListener('gvig:visible', run, { once: true }); observer.observe(node); }
  else run();
  return node;
}

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
  replace(node, h('span.chip', { class: `chip-${lvl}`, title, tabindex: 0, role: 'img', aria: { label: `${t('ui.measure.label')}: ${title}` } }, parts.join(' · ') || '—'));
}
