/* Panel de retoque del pedido: prompt (D19) + estilo del perfil en solo lectura, parámetros (pasos, cfg, sampler,
   semilla con dado, borrador) y las acciones que encolan: «Otra semilla» (semilla + 1, vecindario) y «N seguidas».
   Envía POST …/o/attempts con solo lo que difiere del pedido. «Recrear» y «Variar» de las tarjetas entran por `load()`.
   El modelo se muestra, no se cambia: la API mínima no publica el catálogo (F4d). */

import { h, mmss, replace } from '../dom.js';
import { t } from '../i18n.js';
import { stripStyle } from './attempt-util.js';

const MAX_PROMPT = 2000; // tope orientativo; la API responde order.prompt_too_long con el real

export function retouchPanel(ctx, { onSubmit }) {
  const order = ctx.order;
  const cfg = ctx.profileCfg;
  const params = { ...(order.params || {}) };
  const model = params.model || cfg.model || '—';
  const banned = (ctx.brand && ctx.brand.bannedWords) || [];

  const prompt = h('textarea', { id: 'retouch-prompt', value: order.prompt || '', spellcheck: 'false', aria: { describedby: 'retouch-prompt-hint' } });
  const promptHint = h('div.hint', { id: 'retouch-prompt-hint' });
  const steps = h('input', { type: 'number', min: 1, max: 60, value: params.steps ?? cfg.steps ?? '' });
  const cfgScale = h('input', { type: 'number', min: 0, max: 30, step: 0.5, value: params.cfg ?? cfg.cfg ?? '' });
  const sampler = h('input', { type: 'text', value: params.sampler ?? cfg.sampler ?? '' });
  const seed = h('input', { type: 'number', min: 0, value: order.seed ?? lastSeed(order) ?? '' });
  const draft = h('input', { type: 'checkbox', checked: Boolean(order.draft) });
  const count = h('input', { type: 'number', min: 2, max: 20, value: 3, aria: { label: t('ui.retouch.batchCount') } });
  const templates = ctx.templates || [];
  const templateOfChosen = () => {
    const a = (ctx.order.attempts || []).find((x) => x.id === ctx.order.chosen);
    const id = a && ((a.compose && a.compose.templateId) || (a.composeError && a.composeError.templateId));
    return templates.some((x) => x.id === id) ? id : (templates.find((x) => x.default) || {}).id;
  };
  const template = templates.length > 1
    ? h('select', { id: 'retouch-template' }, templates.map((x) => h('option', { value: x.id, selected: x.id === templateOfChosen() }, x.default ? t('ui.attempt.templateDefault', { id: x.id }) : x.id)))
    : null;
  let templateTouched = false;
  if (template) template.addEventListener('change', () => { templateTouched = true; });
  const dirty = h('span.dirty', { hidden: true }, t('ui.retouch.changed'));

  const checkPrompt = () => {
    const text = prompt.value;
    const hit = banned.find((w) => new RegExp(`\\b${w}\\b`, 'i').test(text));
    replace(promptHint, hit ? h('span.field-error', {}, t('ui.retouch.bannedWord', { w: hit })) : t('ui.retouch.chars', { n: text.length, max: MAX_PROMPT }));
    dirty.hidden = text === (order.prompt || '');
  };
  prompt.addEventListener('input', checkPrompt);
  checkPrompt();

  const spec = (extra = {}) => {
    const s = { count: 1, ...extra };
    const text = stripStyle(prompt.value, cfg.style);
    if (text !== (order.prompt || '')) s.prompt = text;
    const num = (el) => (el.value === '' ? undefined : Number(el.value));
    if (num(steps) !== undefined && num(steps) !== params.steps) s.steps = num(steps);
    if (num(cfgScale) !== undefined && num(cfgScale) !== params.cfg) s.cfg = num(cfgScale);
    if (sampler.value && sampler.value !== params.sampler) s.sampler = sampler.value;
    s.draft = draft.checked;
    if (template && template.value) s.template = template.value;
    return s;
  };

  const another = h('button.btn.btn-primary', { type: 'button', onclick: () => {
    const next = seed.value === '' ? randomSeed() : Number(seed.value) + 1;
    seed.value = next;
    onSubmit(spec({ seed: next }));
  } }, h('span', {}, '▶ ', t('ui.retouch.another'), h('kbd.kbd', { aria: { hidden: true } }, 'G')), etaSpan(ctx, 1));
  const batch = h('button.btn', { type: 'button', onclick: () => {
    const n = Math.max(2, Math.min(20, Number(count.value) || 3));
    const base = seed.value === '' ? randomSeed() : Number(seed.value) + 1;
    seed.value = base + n - 1;
    onSubmit(spec({ count: n, seed: base }));
  } }, h('span', {}, '▶▶ ', t('ui.retouch.batch', { n: count.value })), etaSpan(ctx, Number(count.value) || 3));
  count.addEventListener('input', () => { replace(batch, h('span', {}, '▶▶ ', t('ui.retouch.batch', { n: count.value })), etaSpan(ctx, Number(count.value) || 3)); });

  const node = h('section.card', { aria: { labelledby: 'retouch-h' } },
    h('h2', { id: 'retouch-h' }, t('ui.retouch.title'), ' ', dirty),
    h('div.field', {}, h('label', { for: 'retouch-prompt' }, t('ui.retouch.prompt')), prompt, promptHint),
    cfg.style ? h('div.field', {}, h('span.label', {}, t('ui.retouch.style')), h('div.readonly', {}, cfg.style)) : null,
    h('div.row', {}, h('button.btn', { type: 'button', onclick: () => { prompt.value = order.prompt || ''; checkPrompt(); } }, t('ui.retouch.restore'))),
    h('h3', {}, t('ui.retouch.params')),
    h('div.field', {}, h('span.label', {}, t('ui.retouch.model')), h('div.readonly.mono', {}, model)),
    h('div.cols-3', {},
      h('div.field', {}, h('label', { for: 'retouch-steps' }, t('ui.retouch.steps')), Object.assign(steps, { id: 'retouch-steps' })),
      h('div.field', {}, h('label', { for: 'retouch-cfg' }, t('ui.retouch.cfg')), Object.assign(cfgScale, { id: 'retouch-cfg' })),
      h('div.field', {}, h('label', { for: 'retouch-sampler' }, t('ui.retouch.sampler')), Object.assign(sampler, { id: 'retouch-sampler' }))),
    h('div.field', {}, h('label', { for: 'retouch-seed' }, t('ui.retouch.seed')), h('div.with-button', {}, Object.assign(seed, { id: 'retouch-seed' }),
      h('button.btn.btn-icon', { type: 'button', title: t('ui.retouch.dice'), aria: { label: t('ui.retouch.dice') }, onclick: () => { seed.value = randomSeed(); } }, '⚄')),
      h('span.hint', {}, t('ui.retouch.seedHint'))),
    template ? h('div.field', {}, h('label', { for: 'retouch-template' }, t('ui.retouch.template')), template) : null,
    h('label.check', {}, draft, h('span', {}, t('ui.retouch.draft'), ' ', h('span.hint', {}, t('ui.retouch.draftHint')))),
    h('div.panel-actions', {}, another, h('div.with-button', {}, batch, count)),
    ctx.limits ? h('p.hint', {}, ctx.limits) : null);

  return {
    node,
    /** Carga los parámetros de un intento (Recrear). */
    load(attempt) {
      const p = attempt.params || {};
      prompt.value = attempt.prompt ? stripStyle(attempt.prompt, cfg.style) : order.prompt || '';
      if (p.steps !== undefined) steps.value = p.steps;
      if (p.cfg !== undefined) cfgScale.value = p.cfg;
      if (p.sampler !== undefined) sampler.value = p.sampler;
      seed.value = attempt.seed;
      draft.checked = Boolean(attempt.draft);
      const tid = (attempt.compose && attempt.compose.templateId) || (attempt.composeError && attempt.composeError.templateId);
      if (template && templates.some((x) => x.id === tid)) template.value = tid;
      checkPrompt();
      prompt.focus();
    },
    /** Encola otra semilla con los parámetros de un intento (Variar). */
    vary(attempt) {
      this.load(attempt);
      const next = Number(attempt.seed) + 1;
      seed.value = next;
      onSubmit(spec({ seed: next }));
    },
    /** Cambió la elegida: el selector de plantilla pasa a la de la elegida, salvo que la persona lo haya tocado. */
    setChosen() { if (template && !templateTouched) template.value = templateOfChosen(); },
    focusPrompt() { prompt.focus(); },
    another() { another.click(); },
  };
}

function lastSeed(order) {
  const a = order.attempts && order.attempts[order.attempts.length - 1];
  return a ? a.seed : null;
}

function randomSeed() { return Math.floor(Math.random() * 2 ** 31); }

/** «· ~3:00» a partir de la mediana de las entradas de la cola del mismo perfil (estimateMs), si la hay. */
function etaSpan(ctx, n) {
  const ms = ctx.estimateMs;
  return Number.isFinite(ms) ? h('span.eta', {}, t('ui.retouch.eta', { t: mmss(ms * n) })) : null;
}
