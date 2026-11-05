/* Servidor fingido para el prototipo (solo con `?mock=1`): mismo contrato que la API local de F3 (docs/plan.md «F3 en
   detalle»), en memoria. Las imágenes se pintan con <canvas> (data: URL, permitido por la CSP) sustituyendo
   `paths.image/preview/asset`; la cola avanza sola (una entrada tarda ~12 s). Los textos salen de /api/locales/<lang> (hay que servirlo con gimg serve).
   No se carga en producción: app.js solo lo importa si la URL lleva `?mock=1`. */

import { paths } from '../js/api.js';

const now = () => new Date().toISOString();
const ago = (s) => new Date(Date.now() - s * 1000).toISOString();
const PROJECT = 'galivelop-image-generator';
const PALETTE = ['#06121c', '#A78BFA', '#8B5CF6', '#ffffff', '#eaf4fa'];

const projects = {
  [PROJECT]: {
    name: PROJECT, root: '/home/deck/Desarrollos/galivelop-image-generator',
    config: {
      name: PROJECT, brand: { palette: PALETTE, paletteMin: 72, bannedWords: ['sun', 'muted'] }, delivery: { root: 'docs/marcas/galivelop-image-generator' },
      profiles: {
        og: { width: 1280, height: 640, steps: 6, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8', targetWidth: 1200, targetHeight: 630, draft: { scale: 0.5, steps: 4 },
          style: 'dark abyssal blue background, violet luminous filaments, calm, no text', compose: { template: 'plantillas/og.svg', fields: ['title1', 'title2', 'subtitle', 'subtitle2'], logo: 'logos/b-lockup.svg', fonts: ['Sora', 'Inter'], fit: 'cover' } },
        cuadrado: { width: 1024, height: 1024, steps: 6, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8', compose: { template: 'plantillas/cuadrado.svg', fields: ['title1', 'subtitle'], fonts: ['Sora'], fit: 'cover' } },
        icono: { width: 512, height: 512, steps: 8, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8' },
      },
    },
  },
  tarkor: { name: 'tarkor', root: '/home/deck/Desarrollos/tarkor', config: { name: 'tarkor', brand: { palette: ['#1b1b1f', '#e2b714', '#2F7A55'] }, profiles: { og: { width: 1280, height: 640, steps: 6, cfg: 1, sampler: 'euler', model: 'flux2-klein-4b-q8', compose: { fields: ['title1', 'subtitle'] } } } } },
  roto: { name: 'roto', root: '/home/deck/Desarrollos/roto', error: { code: 'project.config_invalid', message: 'models.json: «flux-x» no está en el catálogo' } },
};

let nextAttempt = 7;
let nextEntry = 12;
const att = (id, seed, state, extra = {}) => ({ id, state, seed, prompt: null, params: { steps: 6, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8', width: 1280, height: 640 }, image: `attempts/q${id}.png`, raw: `attempts/q${id}.raw.png`, note: '', createdAt: ago(3600 - id * 300), log: `attempts/q${id}.log`, durationMs: 11000 + id * 700, compose: { at: ago(3000 - id * 300) }, ...extra });
const orders = [
  { key: 'portada/og', profile: 'og', prompt: 'a vast dark abyssal ocean, violet bioluminescent filaments rising, calm, cinematic, no text', params: { steps: 6, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8' }, seed: 12, draft: false,
    text: { title1: 'Galivelop', title2: 'Image Generator', subtitle: 'Imágenes de marca en local', subtitle2: 'Steam Deck · sin instalaciones' },
    attempts: [att(1, 12, 'discarded', { note: 'demasiado claro' }), att(2, 13, 'candidate'), att(3, 14, 'new', { durationMs: 12400 }), att(4, 15, 'candidate', { note: 'la mejor luz' }), att(5, 20, 'new', { draft: true, compose: undefined, params: { steps: 4, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8', width: 640, height: 320 } }), att(6, 16, 'new', { compose: undefined, composeError: { code: 'compose.font_missing', message: 'Falta la fuente Sora' } })],
    chosen: 4, chosenHistory: [null], createdAt: ago(7200), updatedAt: ago(600) },
  { key: 'portada/cuadrado', profile: 'cuadrado', prompt: 'dark abyssal blue, violet filaments, centered, calm, no text', params: { steps: 6, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8' }, seed: 40, draft: false, text: { title1: 'GVIG', subtitle: 'local' },
    attempts: [], chosen: null, chosenHistory: [], createdAt: ago(900), updatedAt: ago(900) },
  { key: 'icono', profile: 'icono', prompt: 'glowing violet b letter, dark background', params: { steps: 8, cfg: 1.0, sampler: 'euler', model: 'flux2-klein-4b-q8' }, seed: 7, draft: false, text: {},
    attempts: [{ ...att(8, 7, 'new'), params: { steps: 8, cfg: 1, sampler: 'euler', model: 'flux2-klein-4b-q8', width: 512, height: 512 }, compose: undefined }], chosen: null, chosenHistory: [], createdAt: ago(5000), updatedAt: ago(4000) },
];
nextAttempt = 9;
const ordersOf = { [PROJECT]: orders, tarkor: [{ key: 'og', profile: 'og', prompt: 'desert fortress at dusk', params: { steps: 6, cfg: 1, sampler: 'euler' }, seed: 1, draft: false, text: {}, attempts: [], chosen: null, chosenHistory: [], createdAt: ago(100), updatedAt: ago(100) }] };

const queue = [
  { id: 10, project: PROJECT, key: 'portada/cuadrado', profile: 'cuadrado', seed: 41, params: { steps: 6, width: 1024, height: 1024 }, draft: false, state: 'running', startedAt: ago(4), finishedAt: null, error: null, attemptId: null, progress: { step: 2, steps: 6, etaS: 8 }, estimateMs: 12000 },
  { id: 11, project: PROJECT, key: 'portada/cuadrado', profile: 'cuadrado', seed: 42, params: { steps: 6, width: 1024, height: 1024 }, draft: false, state: 'queued', startedAt: null, finishedAt: null, error: null, attemptId: null, estimateMs: 12000 },
  { id: 9, project: PROJECT, key: 'portada/og', profile: 'og', seed: 17, params: { steps: 6, width: 1280, height: 640 }, draft: false, state: 'failed', startedAt: ago(400), finishedAt: ago(380), error: { code: 'engine.oom' }, errorText: 'CUDA out of memory (needs 2.3 GB, 1.9 GB free)', attemptId: null },
  { id: 8, project: PROJECT, key: 'icono', profile: 'icono', seed: 7, params: { steps: 8, width: 512, height: 512 }, draft: false, state: 'done', startedAt: ago(4100), finishedAt: ago(4000), error: null, attemptId: 8 },
];

/* la cola avanza sola */
setInterval(() => {
  const running = queue.find((e) => e.state === 'running');
  if (running) {
    const elapsed = (Date.now() - Date.parse(running.startedAt)) / 1000;
    const steps = running.params.steps || 6;
    running.progress = { step: Math.min(steps, Math.floor(elapsed / 2)), steps, etaS: Math.max(0, Math.round(steps * 2 - elapsed)) };
    if (elapsed >= steps * 2) {
      running.state = 'done'; running.finishedAt = now(); running.progress = undefined;
      const order = findOrder(running.project, running.profile, running.key);
      const id = nextAttempt++;
      const prof = projects[running.project].config.profiles[running.profile];
      order.attempts.push({ ...att(id, running.seed, 'new'), params: { ...prof, ...running.params, width: running.params.width || prof.width, height: running.params.height || prof.height }, prompt: running.prompt || null, draft: running.draft, compose: prof.compose && !running.draft ? { at: now() } : undefined, createdAt: now(), durationMs: Math.round(elapsed * 1000) });
      order.updatedAt = now();
      running.attemptId = id;
    }
  } else {
    const q = queue.find((e) => e.state === 'queued');
    if (q) { q.state = 'running'; q.startedAt = now(); q.progress = { step: 0, steps: q.params.steps || 6, etaS: (q.params.steps || 6) * 2 }; }
  }
}, 1000);

function findOrder(p, profile, key) { return (ordersOf[p] || []).find((o) => o.profile === profile && o.key === key); }
const err = (status, code, message, params = {}) => ({ status, json: { error: { code, params, message } } });
const ok = (json, status = 200) => ({ status, json });

let locales = {};
async function loadLocale(lang) {
  if (!locales[lang]) { try { locales[lang] = await (await fetch(`/api/locales/${lang}`)).json(); } catch { locales[lang] = {}; } }
  return locales[lang];
}

export async function transport(method, url, body) {
  await new Promise((r) => setTimeout(r, 120 + Math.random() * 180));
  const u = new URL(url, location.origin);
  const seg = u.pathname.split('/').filter(Boolean).map(decodeURIComponent); // ['api', ...]
  const lang = u.searchParams.get('lang') || 'es';
  const [, r0, r1, r2, r3, r4, r5, r6, r7] = seg;
  if (r0 === 'health') return ok({ ok: true, version: '0.0.0-mock', worker: true, queue: { running: queue.filter((e) => e.state === 'running').length, queued: queue.filter((e) => e.state === 'queued').length } });
  if (r0 === 'locales') return ok(await loadLocale(r1));
  if (r0 === 'queue') {
    if (r1 && r2 === 'cancel') {
      const e = queue.find((x) => x.id === Number(r1));
      if (!e) return err(404, 'queue.not_found', `No hay entrada ${r1}`, { id: r1 });
      if (!['queued', 'running'].includes(e.state)) return err(409, 'queue.not_pending', `La entrada ${r1} ya terminó`, { id: r1 });
      e.state = 'cancelled'; e.finishedAt = now(); e.progress = undefined;
      return ok(e);
    }
    const st = u.searchParams.get('state');
    return ok(queue.filter((e) => !st || e.state === st).map((e) => ({ ...e })));
  }
  if (r0 === 'projects') {
    if (!r1) return ok(Object.values(projects).map((p) => ({ name: p.name, root: p.root, error: p.error || undefined, orders: (ordersOf[p.name] || []).length, chosen: (ordersOf[p.name] || []).filter((o) => o.chosen !== null).length, profiles: p.config ? Object.keys(p.config.profiles) : undefined })));
    const p = projects[r1];
    if (!p) return err(404, 'project.not_found', `No existe el proyecto «${r1}»`, { name: r1 });
    if (p.error) return err(409, p.error.code, p.error.message);
    if (!r2) return ok({ name: p.name, root: p.root, config: p.config });
    if (r2 === 'profiles') return err(404, 'api.not_found', 'El prototipo no sirve recursos por la API');
    if (r2 === 'orders') {
      if (!r3) {
        const prof = u.searchParams.get('profile'); const chosen = u.searchParams.get('chosen');
        return ok((ordersOf[r1] || []).filter((o) => (!prof || o.profile === prof) && (chosen === null || chosen === '' || (chosen === '1') === (o.chosen !== null)))
          .map((o) => ({ key: o.key, profile: o.profile, chosen: o.chosen, attempts: o.attempts.length, lastAttempt: o.attempts.length ? o.attempts[o.attempts.length - 1].id : null, updatedAt: o.updatedAt })));
      }
      const order = findOrder(r1, r3, r4);
      if (!order) return err(404, 'order.not_found', `No hay pedido «${r4}» con el perfil «${r3}»`, { key: r4, profile: r3 });
      if (!r5) return ok(order);
      if (r5 === 'text' && method === 'PUT') {
        const fields = (projects[r1].config.profiles[r3].compose || {}).fields || [];
        const bad = Object.keys(body.text || {}).filter((k) => !fields.includes(k));
        if (bad.length) return err(422, 'order.text_unknown_field', `Campo desconocido: ${bad.join(', ')}`, { fields: bad.join(', ') });
        order.text = { ...body.text }; order.updatedAt = now();
        return ok(order);
      }
      if (r5 === 'choose') {
        const a = order.attempts.find((x) => x.id === body.attempt);
        if (!a) return err(404, 'attempt.not_found', `No hay intento q${body.attempt}`, { id: body.attempt });
        if (a.state === 'discarded') return err(409, 'order.choose_discarded', `q${a.id} está descartado`, { id: a.id });
        if (a.draft) return err(409, 'order.choose_draft', `q${a.id} es un borrador: no se puede elegir`, { id: a.id });
        if (a.composeError) return err(409, a.composeError.code, a.composeError.message);
        order.chosenHistory.push(order.chosen); order.chosen = a.id; a.state = 'candidate'; order.updatedAt = now();
        return ok({ old: order.chosenHistory[order.chosenHistory.length - 1], new: a.id, deliveredTo: `docs/marcas/${r1}/${r4.replace('/', '-')}-${r3}.png` });
      }
      if (r5 === 'undo') {
        if (!order.chosenHistory.length) return err(409, 'order.nothing_to_undo', 'No hay nada que deshacer');
        const old = order.chosen; order.chosen = order.chosenHistory.pop(); order.updatedAt = now();
        return ok({ old, new: order.chosen });
      }
      if (r5 === 'attempts' && !r6) {
        const spec = body || {};
        const prof = projects[r1].config.profiles[r3];
        const n = Math.max(1, Math.min(20, spec.count || 1));
        const entries = [];
        for (let i = 0; i < n; i += 1) {
          const e = { id: nextEntry++, project: r1, key: r4, profile: r3, seed: (spec.seed ?? Math.floor(Math.random() * 1e6)) + i, params: { steps: spec.steps ?? prof.steps, cfg: spec.cfg ?? prof.cfg, sampler: spec.sampler ?? prof.sampler, model: prof.model, width: spec.draft ? prof.width / 2 : prof.width, height: spec.draft ? prof.height / 2 : prof.height }, prompt: spec.prompt, draft: Boolean(spec.draft), text: order.text, state: 'queued', startedAt: null, finishedAt: null, error: null, attemptId: null, estimateMs: (spec.draft ? 8 : (spec.steps ?? prof.steps)) * 2000 };
          queue.push(e); entries.push(e);
        }
        if (spec.prompt !== undefined) order.prompt = spec.prompt;
        return ok({ entries, estimateMs: entries.reduce((s, e) => s + e.estimateMs, 0) }, 202);
      }
      if (r5 === 'attempts' && r6) {
        const a = order.attempts.find((x) => x.id === Number(r6));
        if (!a) return err(404, 'attempt.not_found', `No hay intento q${r6}`, { id: r6 });
        if (r7 === 'mark') { if (body.state === 'discarded' && order.chosen === a.id) return err(409, 'order.discard_chosen', 'No se descarta la elegida: deshaz primero'); a.state = body.state; return ok(a); }
        if (r7 === 'note') { a.note = body.text; return ok(a); }
        if (r7 === 'compose') {
          if (a.composeError && a.id === 6) return err(422, 'compose.font_missing', 'Falta la fuente Sora (gimg doctor)', { font: 'Sora' });
          a.compose = { at: now() }; a.composeError = undefined; return ok(a);
        }
        if (r7 === 'measure') {
          if (a.id === 3 && !measureBusyOnce.done) { measureBusyOnce.done = true; return err(409, 'measure.busy', 'Hay otra medida en marcha (espera 60 s)'); }
          const k = (a.seed * 7919) % 100;
          const worst = a.id === 1 ? 2.4 : a.id === 5 ? 3.6 : 4.6 + (k % 40) / 10;
          return ok({ yavg: 0.18 + (k % 30) / 100, satavg: 0.4, palette: { pct: a.id === 1 ? 51 : 62 + (k % 35) }, contrast: u.searchParams.get('zone') ? { mean: worst + 2.1, p10: worst + 0.3, p90: worst + 4, worst } : undefined });
        }
      }
    }
  }
  return err(404, 'api.not_found', `Ruta desconocida: ${method} ${u.pathname}`, { path: u.pathname });
}
const measureBusyOnce = { done: false };

/* ---- imágenes por canvas ---- */
const imgCache = new Map();
function picture(seed, w, h, label, raw) {
  const key = `${seed}/${w}x${h}/${label}/${raw}`;
  if (imgCache.has(key)) return imgCache.get(key);
  const c = document.createElement('canvas'); c.width = Math.min(w, 640); c.height = Math.round(c.width * h / w);
  const g = c.getContext('2d');
  const rnd = mulberry(seed);
  const grad = g.createLinearGradient(0, 0, c.width, c.height);
  grad.addColorStop(0, '#06121c'); grad.addColorStop(1, `hsl(${250 + rnd() * 30} 70% ${18 + rnd() * 14}%)`);
  g.fillStyle = grad; g.fillRect(0, 0, c.width, c.height);
  for (let i = 0; i < 24; i += 1) {
    g.strokeStyle = `hsl(${255 + rnd() * 20} 80% ${55 + rnd() * 25}% / ${0.25 + rnd() * 0.5})`; g.lineWidth = 1 + rnd() * 3;
    g.beginPath(); const x = rnd() * c.width; g.moveTo(x, c.height); g.bezierCurveTo(x + (rnd() - 0.5) * 200, c.height * 0.6, x + (rnd() - 0.5) * 200, c.height * 0.3, x + (rnd() - 0.5) * 100, -10); g.stroke();
  }
  if (!raw && label) {
    g.fillStyle = 'rgb(6 18 28 / .45)'; g.fillRect(0, 0, w > h ? c.width / 2 : c.width, w > h ? c.height : c.height / 2);
    g.fillStyle = '#eaf4fa'; g.font = `700 ${Math.round(c.width / 16)}px Sora, Inter, sans-serif`; g.fillText(label, c.width * 0.06, c.height * 0.5);
  }
  g.fillStyle = '#9fb4c4'; g.font = '12px monospace'; g.fillText(`seed ${seed}`, 8, c.height - 8);
  const url = c.toDataURL('image/png');
  imgCache.set(key, url);
  return url;
}
function mulberry(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

paths.image = (p, profile, key, id, { raw = false } = {}) => {
  const order = findOrder(p, profile, key); const a = order && order.attempts.find((x) => x.id === Number(id));
  if (!a) return 'data:,';
  return picture(a.seed, a.params.width, a.params.height, (order.text && order.text.title1) || '', raw || !a.compose);
};
paths.preview = (id) => { const e = queue.find((x) => x.id === Number(id)); return e ? picture(e.seed + 1000, e.params.width || 1280, e.params.height || 640, '', true) : 'data:,'; };
paths.asset = () => '/ui/assets/gvig-lockup.svg';
paths.log = () => 'data:text/plain,registro%20del%20intento%20(mock)';
