/* Panel «Nuevo pedido» (F4d, D22): un `dialog` modal para crear un pedido desde la interfaz.
   - Campos: clave, perfil, prompt, prompt negativo (opcional), textos de la composición (`compose.fields` del perfil), plantilla, modelo, semilla
     (vacía = al azar), borrador y número de intentos seguidos. «Copiar de…» rellena prompt, textos, semilla, borrador y
     parámetros (pasos, cfg, sampler) desde un pedido existente del mismo perfil.
   - Modelo: GET /api/models; los que la máquina no permite salen deshabilitados, con su motivo (`reason.message`).
   - Palabras vetadas (`brand.bannedWords`): aviso en vivo bajo el prompt, nunca bloquea.
   - Envía POST /api/projects/{p}/orders (`template` y `model` solo si difieren del perfil) y, si sale bien, abre el
     pedido. Un error de la API se muestra dentro del diálogo y en un aviso (un `dialog` modal tapa los avisos). */

import { h, replace, mmss } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError } from '../api.js';
import { navigate, to } from '../router.js';
import * as poll from '../queue-poll.js';
import { bannedWord } from './attempt-util.js';
import { toastError, toastOk } from './toast.js';

/** El patrón de `key` de order.schema.json. */
export const KEY_PATTERN = /^[a-z0-9][a-z0-9-]*(\/[a-z0-9][a-z0-9-]*)*$/;
export const MAX_KEY = 200;
export const MAX_COUNT = 50;
const PARAM_KEYS = ['steps', 'cfg', 'sampler'];

/** Abre el panel. `profile`: el perfil preseleccionado; `opener`: el botón que lo abrió (recupera el foco al cerrar). */
export async function openNewOrder(project, { profile = '', opener = null } = {}) {
  let info;
  let models = [];
  try {
    [info, models] = await Promise.all([api.project(project), api.models().catch(() => [])]);
  } catch (e) { toastError(describeError(e, t)); return null; }
  const cfg = info.config || {};
  const brand = cfg.brand || {};
  const profiles = Object.keys(cfg.profiles || {});
  if (!profiles.length) { toastError(t('ui.newOrder.noProfiles')); return null; }
  models = Array.isArray(models) ? models : [];
  const banned = brand.bannedWords || [];
  const profileOf = (name) => (cfg.profiles || {})[name] || {};

  let closed = false;
  let created = false;
  let busy = false;
  let loadSeq = 0;
  let textInputs = {};
  let copiedParams = null;
  let defaultTemplate = null;

  const error = h('p.notice.notice-bad', { id: 'no-error', role: 'alert', hidden: true });
  const key = h('input', { id: 'no-key', type: 'text', autocomplete: 'off', spellcheck: 'false', maxlength: MAX_KEY, aria: { describedby: 'no-key-hint' } });
  const profileSel = h('select', { id: 'no-profile' }, profiles.map((p) => h('option', { value: p, selected: p === (profiles.includes(profile) ? profile : profiles[0]) }, p)));
  const prompt = h('textarea', { id: 'no-prompt', rows: 4, spellcheck: 'false', aria: { describedby: 'no-prompt-hint' } });
  const promptHint = h('div.hint', { id: 'no-prompt-hint' });
  const negative = h('textarea', { id: 'no-negative', rows: 2, spellcheck: 'false', maxlength: 4000 });
  const textsBox = h('div.stack');
  const templateSel = h('select', { id: 'no-template' });
  const templateField = h('div.field', { hidden: true }, h('label', { for: 'no-template' }, t('ui.retouch.template')), templateSel);
  const modelSel = h('select', { id: 'no-model', aria: { describedby: 'no-model-hint' } });
  const modelField = models.length
    ? h('div.field', {}, h('label', { for: 'no-model' }, t('ui.retouch.model')), modelSel, h('span.hint', { id: 'no-model-hint' }, t('ui.newOrder.modelHint')))
    : null;
  const seed = h('input', { id: 'no-seed', type: 'number', min: 0, max: 4294967295, aria: { describedby: 'no-seed-hint' } });
  const dice = h('button.btn.btn-icon', { type: 'button', title: t('ui.retouch.dice'), aria: { label: t('ui.retouch.dice') }, onclick: () => { seed.value = Math.floor(Math.random() * 2 ** 31); } }, '⚄');
  const draft = h('input', { type: 'checkbox' });
  const count = h('input', { id: 'no-count', type: 'number', min: 1, max: MAX_COUNT, value: 1 });
  const copySel = h('select', { id: 'no-copy' });
  const copyField = h('div.field', { hidden: true }, h('label', { for: 'no-copy' }, t('ui.newOrder.copy')), copySel, h('span.hint', { id: 'no-copy-note', role: 'status' }));
  const copyNote = copyField.querySelector('#no-copy-note');
  const sendLabel = h('span', {}, t('ui.newOrder.submit'));
  const send = h('button.btn.btn-primary', { type: 'submit' }, sendLabel);
  const cancel = h('button.btn', { type: 'button', onclick: () => dlg.close() }, t('ui.newOrder.cancel'));

  const form = h('form.no-form', { novalidate: true, onsubmit: (ev) => { ev.preventDefault(); submit(); } },
    h('div.cols-2', {},
      h('div.field', {}, h('label', { for: 'no-key' }, t('ui.newOrder.key')), key, h('span.hint', { id: 'no-key-hint' }, t('ui.newOrder.keyHint'))),
      h('div.field', {}, h('label', { for: 'no-profile' }, t('ui.newOrder.profile')), profileSel)),
    copyField,
    h('div.field', {}, h('label', { for: 'no-prompt' }, t('ui.newOrder.prompt')), prompt, promptHint),
    h('div.field', {}, h('label', { for: 'no-negative' }, t('ui.newOrder.negative')), negative),
    textsBox,
    h('div.cols-2', {}, templateField, modelField),
    h('div.cols-2', {},
      h('div.field', {}, h('label', { for: 'no-seed' }, t('ui.retouch.seed')), h('div.with-button', {}, seed, dice), h('span.hint', { id: 'no-seed-hint' }, t('ui.newOrder.seedHint'))),
      h('div.field', {}, h('label', { for: 'no-count' }, t('ui.newOrder.count')), count)),
    h('label.check', {}, draft, h('span', {}, t('ui.retouch.draft'), ' ', h('span.hint', {}, t('ui.retouch.draftHint')))),
    error,
    h('div.row', {}, send, cancel));

  const dlg = h('dialog.new-order', { aria: { labelledby: 'no-title' } },
    h('h2', { id: 'no-title' }, t('ui.newOrder.title'), ' ', h('span.hint', {}, project)), form);

  const allText = () => [prompt.value, ...Object.values(textInputs).map((i) => i.value)].join(' ');
  function checkPrompt() {
    const hit = bannedWord(allText(), banned);
    replace(promptHint, hit ? h('span.field-warn', {}, '⚠ ', t('ui.retouch.bannedWord', { w: hit })) : t('ui.retouch.chars', { n: prompt.value.length, max: 2000 }));
  }
  prompt.addEventListener('input', checkPrompt);

  function fillModels() {
    if (!modelField) return;
    const current = profileOf(profileSel.value).model || '—';
    replace(modelSel,
      h('option', { value: '' }, t('ui.newOrder.modelProfile', { id: current })),
      models.map((m) => h('option', { value: m.id, disabled: m.allowed === false }, m.allowed === false ? t('ui.newOrder.modelBlocked', { id: m.id, reason: (m.reason && m.reason.message) || '' }) : m.id)));
  }

  function fillTexts() {
    const fields = (profileOf(profileSel.value).compose || {}).fields || [];
    const kept = Object.fromEntries(Object.entries(textInputs).map(([name, input]) => [name, input.value]));
    textInputs = {};
    replace(textsBox, fields.length ? [h('h3', {}, t('ui.newOrder.texts')), h('div.cols-2', {}, fields.map((f) => {
      const input = h('input', { id: `no-text-${f}`, type: 'text', maxlength: 200, value: kept[f] || '' });
      input.addEventListener('input', checkPrompt);
      textInputs[f] = input;
      return h('div.field', {}, h('label', { for: `no-text-${f}` }, t('ui.newOrder.textField', { field: f })), input);
    }))] : null);
  }

  /** Plantillas y pedidos del perfil elegido (las dos peticiones pueden fallar sin romper el panel). */
  async function loadProfile() {
    const name = profileSel.value;
    const seq = ++loadSeq;
    copiedParams = null;
    copyNote.textContent = '';
    fillModels();
    fillTexts();
    checkPrompt();
    const [templates, list] = await Promise.all([api.templates(project, name).catch(() => []), api.orders(project, { profile: name }).catch(() => [])]);
    if (closed || seq !== loadSeq) return;
    const tpls = Array.isArray(templates) ? templates : [];
    defaultTemplate = (tpls.find((x) => x.default) || {}).id || null;
    replace(templateSel, tpls.map((x) => h('option', { value: x.id, selected: x.id === defaultTemplate }, x.default ? t('ui.attempt.templateDefault', { id: x.id }) : x.id)));
    templateField.hidden = tpls.length < 2;
    const found = (Array.isArray(list) ? list : (list && list.orders) || []).slice()
      .sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')));
    replace(copySel, h('option', { value: '' }, t('ui.newOrder.copyNone')), found.map((o) => h('option', { value: o.key }, o.key)));
    copyField.hidden = !found.length;
  }

  async function copyFrom() {
    const name = profileSel.value;
    const from = copySel.value;
    if (!from) { copiedParams = null; copyNote.textContent = ''; return; }
    try {
      const o = await api.order(project, name, from);
      if (closed || profileSel.value !== name || copySel.value !== from) return;
      prompt.value = o.prompt || '';
      negative.value = o.negative || '';
      for (const [field, input] of Object.entries(textInputs)) input.value = (o.text || {})[field] ?? '';
      seed.value = o.seed ?? '';
      draft.checked = Boolean(o.draft);
      const picked = Object.fromEntries(PARAM_KEYS.filter((k) => o.params && o.params[k] !== undefined).map((k) => [k, o.params[k]]));
      copiedParams = Object.keys(picked).length ? picked : null;
      copyNote.textContent = [t('ui.newOrder.copied', { key: from }),
        copiedParams ? t('ui.newOrder.copyParams', { params: Object.entries(copiedParams).map(([k, v]) => `${k} ${v}`).join(' · ') }) : null].filter(Boolean).join(' ');
      checkPrompt();
    } catch (e) {
      copySel.value = '';
      showError(`${t('ui.newOrder.copyFailed', { key: from })}: ${describeError(e, t)}`);
    }
  }

  /** Lo que se manda a POST …/orders; null si algo no vale (el aviso y el foco ya están puestos). */
  function buildBody() {
    const k = key.value.trim();
    if (!KEY_PATTERN.test(k) || k.length > MAX_KEY) { showError(t('ui.newOrder.keyInvalid'), key); return null; }
    if (!prompt.value.trim()) { showError(t('ui.newOrder.promptRequired'), prompt); return null; }
    const body = { key: k, profile: profileSel.value, prompt: prompt.value.trim(), count: Math.max(1, Math.min(MAX_COUNT, Math.round(Number(count.value)) || 1)) };
    if (negative.value.trim()) body.negative = negative.value.trim();
    const text = Object.fromEntries(Object.entries(textInputs).filter(([, input]) => input.value !== '').map(([field, input]) => [field, input.value]));
    if (Object.keys(text).length) body.text = text;
    if (seed.value !== '') body.seed = Number(seed.value);
    if (draft.checked) body.draft = true;
    if (copiedParams) body.params = { ...copiedParams };
    if (templateSel.value && !templateField.hidden && templateSel.value !== defaultTemplate) body.template = templateSel.value;
    if (modelField && modelSel.value) body.model = modelSel.value;
    return body;
  }

  function showError(message, focusOn) {
    toastError(message);
    error.textContent = message;
    error.hidden = false;
    if (focusOn) focusOn.focus();
  }

  function setBusy(v) {
    busy = v;
    send.disabled = v;
    replace(sendLabel, v ? t('ui.newOrder.sending') : t('ui.newOrder.submit'));
  }

  async function submit() {
    if (busy) return;
    error.hidden = true;
    const body = buildBody();
    if (!body) return;
    setBusy(true);
    let res;
    try { res = await api.newOrder(project, body); } catch (e) { setBusy(false); showError(describeError(e, t)); return; }
    created = true;
    const order = (res && res.order) || body;
    const n = (res && res.entries && res.entries.length) || body.count;
    toastOk(t('ui.newOrder.created', { key: order.key, n, t: res && Number.isFinite(res.estimateMs) ? ` · ~${mmss(res.estimateMs * n)}` : '' }));
    poll.refreshNow();
    dlg.close();
    navigate(to.order(project, order.profile || body.profile, order.key));
  }

  profileSel.addEventListener('change', loadProfile);
  copySel.addEventListener('change', copyFrom);
  dlg.addEventListener('keydown', (ev) => ev.stopPropagation()); // los atajos globales no actúan con el panel abierto
  dlg.addEventListener('close', () => {
    closed = true;
    dlg.remove();
    if (!created && opener && opener.isConnected) opener.focus();
  });
  document.body.append(dlg);
  dlg.showModal();
  key.focus();
  loadProfile();
  return dlg;
}
