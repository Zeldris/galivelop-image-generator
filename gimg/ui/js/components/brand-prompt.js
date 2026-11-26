/* Prompt de marca montado (0.7.0 §2.10 y 0.8.0 §2.1). Dos piezas:
   - `promptBuilder(...)`: el componente que usan «Probar un sujeto», el nuevo pedido y el retoque de un pedido de marca.
     Tipo de pieza (con perfil · registro · croma al lado), sujeto (con contador de palabras), zona limpia, el prompt
     montado en tramos con su rótulo y de dónde sale, la comprobación en vivo (POST …/brand/prompt 300 ms después de la
     última tecla; cada respuesta lleva un número de secuencia y la vieja se descarta), «Copiar prompt», el aviso «ya
     falló antes» (`known`, no bloquea) y los ajustes del tipo en un `details` cerrado.
     Estados (`state().status`): `empty` (sin sujeto), `loading`, `ready` (se puede encolar, con o sin avisos), `blocked`
     (la hoja falla: se dice por qué, `aria-describedby` apunta a `reasonId`) y `error` (con «Reintentar»: en marca no se
     encola sin comprobación).
   - `brandPrompt(host, project, pieceTypes)`: la subpestaña «Probar un sujeto» de la pestaña Marca: el constructor con un
     botón «Montar» que no espera al retardo, y la comprobación de un prompt libre (POST …/brand/lint, los errores bajan a
     avisos). No encola nada y no escribe nada. */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError } from '../api.js';
import { loc } from './sheet-view.js';
import { copyButton } from './copy-button.js';
import { checkList } from './check-list.js';

export const DEBOUNCE_MS = 300;

function busy(node) { replace(node, h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading'))); }
function failed(node, e) { replace(node, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t))); }
const wordCount = (s) => (s.trim() ? s.trim().split(/\s+/).length : 0);
const rowLabel = (row) => (row && typeof row === 'object' ? (row.key ?? row.id ?? row.n ?? row.row ?? JSON.stringify(row)) : row);
/** «Ya falló antes»: el término, la fila de troubleshooting y, si la fila lo trae, el rediseño apuntado. No bloquea. */
export const knownText = (k) => t(k.row && typeof k.row === 'object' && k.row.redesign ? 'ui.prompt.knownRedesign' : 'ui.prompt.known',
  { term: k.term, row: rowLabel(k.row), redesign: k.row && typeof k.row === 'object' ? k.row.redesign || '' : '' });

/** Los tramos con las palabras que rompen una regla (`span` de los fallos, en el prompt entero) dentro de `<mark>`. */
function segmentText(segments, prompt, checks, index) {
  const text = segments[index].text;
  if (segments.map((s) => s.text).join(' ') !== prompt) return text;
  const start = segments.slice(0, index).reduce((n, s) => n + s.text.length + 1, 0);
  const spans = checks.filter((c) => c.status === 'error' && Array.isArray(c.span))
    .map((c) => [Math.max(c.span[0], start) - start, Math.min(c.span[1], start + text.length) - start])
    .filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
  if (!spans.length) return text;
  const out = [];
  let at = 0;
  for (const [a, b] of spans) {
    if (a < at) continue;
    out.push(text.slice(at, a), h('mark', {}, text.slice(a, b)));
    at = b;
  }
  out.push(text.slice(at));
  return out;
}

/** Opciones: `project`, `pieceTypes`, `piece`, `subject`, `cleanZone` (valores iniciales), `lockPiece` (el retoque: la pieza
    no se cambia), `prefix` (ids), `mountButton` (la subpestaña), `onState(state)` y `onSubmit()` (Ctrl+Intro en el sujeto). */
export function promptBuilder({ project, pieceTypes = [], piece = '', subject = '', cleanZone = '', lockPiece = false, prefix = 'bp', mountButton = false, onState = () => {}, onSubmit = null } = {}) {
  const types = Array.isArray(pieceTypes) ? pieceTypes : [];
  const reasonId = `${prefix}-why`;
  const pieceSel = h('select', { id: `${prefix}-piece`, disabled: lockPiece },
    types.map((p) => h('option', { value: p.id, selected: p.id === piece }, `${loc(p.label) || p.id} (${p.id})`)));
  const chips = h('div.row', { data: { slot: 'piece-chips' } });
  const subjectEl = h('textarea', { id: `${prefix}-subject`, rows: 4, spellcheck: 'false', value: subject, aria: { describedby: `${prefix}-subject-hint` } });
  const subjectHint = h('span.hint', { id: `${prefix}-subject-hint` });
  const zoneEl = h('input', { id: `${prefix}-zone`, type: 'text', spellcheck: 'false', autocomplete: 'off', value: cleanZone });
  const why = h('div', { id: reasonId, role: 'status', data: { slot: 'why' } });
  const out = h('div.stack', { aria: { live: 'polite', busy: 'false' }, data: { out: 'prompt' } });
  const settings = h('details', { data: { slot: 'settings' } }, h('summary', {}, t('ui.prompt.settings')), h('div', { data: { slot: 'defaults-host' } }));
  const mount = mountButton ? h('button.btn.btn-primary', { type: 'button', onclick: () => run() }, t('ui.prompt.mount')) : null;

  let seq = 0;
  let timer = null;
  const st = { status: 'empty', piece: '', subject: '', cleanZone: '', prompt: '', words: 0, checks: [], errors: [], known: [], defaults: {}, blocked: false, error: null, segments: [] };
  let live = false; // `onState` no se llama durante la construcción: quien lo recibe aún no tiene el componente

  const focusField = (name) => { const el = name === 'zone' ? zoneEl : name === 'piece' ? pieceSel : subjectEl; el.focus(); };
  function values() { return { piece: pieceSel.value, subject: subjectEl.value.trim(), cleanZone: zoneEl.value.trim() }; }
  function publish() { Object.assign(st, values()); if (live) onState({ ...st }); }

  function paintChips() {
    const p = types.find((x) => x.id === pieceSel.value);
    replace(chips, p ? [p.profile ? h('span.chip', {}, p.profile) : null, p.register ? h('span.chip', {}, p.register) : null,
      h('span.chip', {}, p.chroma ? p.chroma : t('ui.sheet.noChroma'))] : null);
  }

  function paintWhy() {
    if (st.status === 'empty') replace(why, h('span.hint', {}, t('ui.prompt.noSubject')));
    else if (st.status === 'loading') replace(why, h('span.hint', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.prompt.checking')));
    else if (st.status === 'blocked') {
      replace(why, h('p.notice.notice-bad', {}, t('ui.prompt.cantQueue', { n: st.errors.length })),
        st.errors[0] ? h('p.hint', {}, t((st.errors[0].message || {}).key || st.errors[0].id, (st.errors[0].message || {}).params)) : null);
    } else if (st.status === 'error') {
      replace(why, h('p.notice.notice-bad', { role: 'alert' }, t('ui.prompt.checkFailed'), ': ', st.error || ''),
        h('button.btn', { type: 'button', onclick: () => run() }, '↻ ', t('ui.prompt.retry')));
    } else replace(why);
  }

  function paintResult() {
    if (st.status === 'empty' || st.status === 'error') { replace(out); return; }
    if (st.status === 'loading' && !st.prompt) { busy(out); return; }
    const d = st.defaults || {};
    replace(out,
      h('div.row-between', {}, h('h3', {}, t('ui.prompt.result')),
        h('span.hint', { data: { slot: 'words' } }, t('ui.prompt.words', { n: st.words })), copyButton(st.prompt, { label: t('ui.prompt.copy') })),
      mountButton && st.blocked ? h('p.notice.notice-bad', { role: 'status', data: { slot: 'blocked' } }, t('ui.prompt.blocked')) : null,
      ...st.known.map((k) => h('p.notice.notice-warn', { role: 'status', data: { slot: 'known' } }, knownText(k))),
      h('pre.sheet-code', { data: { slot: 'prompt' } }, h('code', {}, st.prompt)),
      h('h3', {}, t('ui.prompt.segments')),
      h('ol.stack', { data: { list: 'segments' } }, st.segments.map((s, i) => h('li.seg', { class: s.source === 'input' ? 'seg-input' : '', data: { role: s.role, source: s.source === 'input' ? 'input' : 'sheet' } },
        h('div.row', {}, h('b', {}, `${i + 1} ${t(`ui.prompt.role.${s.role}`)}`), h('code.mono.hint', {}, s.source === 'input' ? t('ui.prompt.fromYou') : s.source)),
        h('span', {}, segmentText(st.segments, st.prompt, st.checks, i))))),
      h('h3', {}, t('ui.prompt.checks')), checkList(st.checks, { onField: focusField }));
    replace(settings.lastChild,
      h('dl.facts', { data: { slot: 'defaults' } },
        h('dt', {}, t('ui.sheet.col.profile')), h('dd', {}, d.profile ? h('code.mono', {}, d.profile) : '—'),
        h('dt', {}, t('ui.sheet.col.seed')), h('dd', {}, d.seed ?? '—'),
        h('dt', {}, t('ui.sheet.col.count')), h('dd', {}, d.count ?? '—'),
        h('dt', {}, t('ui.prompt.model')), h('dd', {}, d.model ? h('code.mono', {}, d.model) : '—'),
        h('dt', {}, t('ui.sheet.col.chroma')), h('dd', {}, d.chroma ? h('code.mono', {}, d.chroma) : t('ui.sheet.noChroma'))));
  }

  function paint() {
    paintChips();
    replace(subjectHint, t('ui.prompt.subjectWords', { n: wordCount(subjectEl.value) }), ' · ', t('ui.prompt.subjectHint'));
    paintWhy();
    paintResult();
    out.setAttribute('aria-busy', st.status === 'loading' ? 'true' : 'false');
    if (mount) mount.disabled = st.status === 'loading';
    publish();
  }

  /** Pide la comprobación ahora; solo vale la última respuesta (número de secuencia). */
  async function run() {
    clearTimeout(timer);
    timer = null;
    const mine = ++seq;
    const v = values();
    if (!v.piece) { st.status = 'error'; st.error = t('ui.prompt.noType'); paint(); return; }
    if (!v.subject) { Object.assign(st, { status: 'empty', prompt: '', segments: [], checks: [], errors: [], known: [], blocked: false, error: null }); paint(); return; }
    st.status = 'loading';
    st.error = null;
    paint();
    const body = { piece: v.piece, subject: v.subject };
    if (v.cleanZone) body.cleanZone = v.cleanZone;
    try {
      const r = await api.brandPrompt(project, body);
      if (mine !== seq) return; // una respuesta vieja no pisa a la nueva
      const checks = r.checks || [];
      Object.assign(st, { prompt: r.prompt, words: r.words, segments: r.segments || [], checks, known: r.known || [], defaults: r.defaults || {},
        blocked: Boolean(r.blocked), errors: checks.filter((c) => c.status === 'error'), error: null });
      st.status = r.blocked ? 'blocked' : 'ready';
    } catch (e) {
      if (mine !== seq) return;
      st.status = 'error';
      st.error = describeError(e, t);
    }
    paint();
  }

  /** Cada tecla invalida lo comprobado (el botón se apaga ya) y pide la nueva comprobación a los 300 ms. */
  function schedule() {
    clearTimeout(timer);
    seq += 1;
    if (!subjectEl.value.trim()) { run(); return; }
    st.status = 'loading';
    paint();
    timer = setTimeout(run, DEBOUNCE_MS);
  }

  subjectEl.addEventListener('input', schedule);
  zoneEl.addEventListener('input', schedule);
  pieceSel.addEventListener('change', schedule);
  subjectEl.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter' && (ev.ctrlKey || ev.metaKey) && onSubmit) { ev.preventDefault(); onSubmit(); }
  });

  const node = h('div.stack', { data: { builder: 'brand' } },
    h('div.field', {}, h('label', { for: `${prefix}-piece` }, t('ui.prompt.piece')), pieceSel, chips),
    h('div.field', {}, h('label', { for: `${prefix}-subject` }, t('ui.prompt.subject')), subjectEl, subjectHint),
    h('div.field', {}, h('label', { for: `${prefix}-zone` }, t('ui.prompt.zone')), zoneEl),
    mount ? h('div.row', {}, mount) : null,
    why, out, settings);
  paint();
  live = true;
  if (subject.trim()) setTimeout(run, 0); // fuera de la construcción: el que recibe `onState` aún no tiene el componente

  return {
    node,
    reasonId,
    state: () => ({ ...st, ...values() }),
    focusField,
    flush: run,
    setValues(v = {}) {
      if (v.piece !== undefined && types.some((p) => p.id === v.piece)) pieceSel.value = v.piece;
      if (v.subject !== undefined) subjectEl.value = v.subject;
      if (v.cleanZone !== undefined) zoneEl.value = v.cleanZone;
      schedule();
    },
    destroy() { clearTimeout(timer); seq += 1; },
  };
}

export async function brandPrompt(host, project, pieceTypes) {
  const types = Array.isArray(pieceTypes) ? pieceTypes : [];
  const builder = promptBuilder({ project, pieceTypes: types, prefix: 'bp', mountButton: true });

  const freePrompt = h('textarea', { id: 'bl-prompt', rows: 5, spellcheck: 'false' });
  const freePiece = h('select', { id: 'bl-piece' }, h('option', { value: '' }, t('ui.prompt.noPiece')), types.map((p) => h('option', { value: p.id }, `${loc(p.label) || p.id} (${p.id})`)));
  const freeOut = h('div.stack', { aria: { live: 'polite', busy: 'false' }, data: { out: 'lint' } });
  const lintGo = h('button.btn', { type: 'button', onclick: () => lint() }, t('ui.prompt.lint'));

  async function lint() {
    if (!freePrompt.value.trim()) { replace(freeOut, h('p.notice.notice-warn', { role: 'alert' }, t('ui.prompt.noPrompt'))); freePrompt.focus(); return; }
    const body = { prompt: freePrompt.value };
    if (freePiece.value) body.piece = freePiece.value;
    lintGo.disabled = true;
    freeOut.setAttribute('aria-busy', 'true');
    busy(freeOut);
    try {
      const r = await api.brandLint(project, body);
      replace(freeOut, h('p.hint', { data: { slot: 'words' } }, t('ui.prompt.words', { n: wordCount(freePrompt.value) })), checkList(r.checks || []));
    } catch (e) { failed(freeOut, e); }
    freeOut.setAttribute('aria-busy', 'false');
    lintGo.disabled = false;
  }

  host.append(
    h('section.card', { data: { card: 'prompt' }, aria: { labelledby: 'bp-h' } },
      h('h2', { id: 'bp-h' }, t('ui.prompt.title')), h('p.hint', {}, t('ui.prompt.intro')), builder.node),
    h('section.card', { data: { card: 'lint' }, aria: { labelledby: 'bl-h' } },
      h('h2', { id: 'bl-h' }, t('ui.prompt.freeTitle')), h('p.hint', {}, t('ui.prompt.freeIntro')),
      h('div.field', {}, h('label', { for: 'bl-prompt' }, t('ui.prompt.freePrompt')), freePrompt),
      h('div.field', {}, h('label', { for: 'bl-piece' }, t('ui.prompt.freePiece')), freePiece),
      h('div.row', {}, lintGo), freeOut));
}
