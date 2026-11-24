/* Subpestaña «Probar un sujeto» de la pestaña Marca (0.7.0 §2.10): la cara de `gimg brand prompt` y `gimg brand lint`.
   - Montar: un tipo de pieza, un sujeto y una zona limpia opcional -> POST …/brand/prompt: el prompt (con Copiar), las
     palabras, los segmentos con su origen, las comprobaciones (estado en texto y color), si bloquea y los valores
     por defecto del tipo.
   - Comprobar un prompt libre: POST …/brand/lint (modo libre: los errores bajan a avisos).
   No encola nada y no escribe nada. */

import { h, replace } from '../dom.js';
import { t } from '../i18n.js';
import { api, describeError } from '../api.js';
import { loc } from './sheet-view.js';
import { copyButton } from './copy-button.js';

const STATUS = { ok: ['ui.check.ok', 'chip-ok'], warn: ['ui.check.warn', 'chip-warn'], error: ['ui.check.fail', 'chip-bad'] };

function checkList(checks) {
  const count = (s) => checks.filter((c) => c.status === s).length;
  return h('div.stack', {},
    h('p', {}, h('b', {}, t('ui.check.summary', { ok: count('ok'), warn: count('warn'), fail: count('error') }))),
    h('ul.check-list', { data: { list: 'checks' } }, checks.map((c) => {
      const [key, chip] = STATUS[c.status] || STATUS.warn;
      const msg = c.message || {};
      return h('li.check-item', { class: `is-${c.status === 'error' ? 'fail' : c.status}`, data: { check: c.id, status: c.status } },
        h('span.chip', { class: chip }, t(key)),
        h('div', {}, h('div', {}, t(msg.key || c.id, msg.params)), h('code.mono.hint', {}, c.id)));
    })));
}

function busy(node) { replace(node, h('p.empty', {}, h('span.spin', { aria: { hidden: true } }), ' ', t('ui.loading'))); }
function failed(node, e) { replace(node, h('p.notice.notice-bad', { role: 'alert' }, describeError(e, t))); }

export async function brandPrompt(host, project, pieceTypes) {
  const types = Array.isArray(pieceTypes) ? pieceTypes : [];
  const pieceSel = h('select', { id: 'bp-piece' }, types.map((p) => h('option', { value: p.id }, `${loc(p.label) || p.id} (${p.id})`)));
  const subject = h('textarea', { id: 'bp-subject', rows: 4, spellcheck: 'false', aria: { describedby: 'bp-subject-hint' } });
  const zone = h('input', { id: 'bp-zone', type: 'text', spellcheck: 'false', autocomplete: 'off' });
  const out = h('div.stack', { aria: { live: 'polite', busy: 'false' }, data: { out: 'prompt' } });
  const go = h('button.btn.btn-primary', { type: 'button', onclick: () => mount() }, t('ui.prompt.mount'));

  const freePrompt = h('textarea', { id: 'bl-prompt', rows: 5, spellcheck: 'false' });
  const freePiece = h('select', { id: 'bl-piece' }, h('option', { value: '' }, t('ui.prompt.noPiece')), types.map((p) => h('option', { value: p.id }, `${loc(p.label) || p.id} (${p.id})`)));
  const freeOut = h('div.stack', { aria: { live: 'polite', busy: 'false' }, data: { out: 'lint' } });
  const lintGo = h('button.btn', { type: 'button', onclick: () => lint() }, t('ui.prompt.lint'));

  async function mount() {
    if (!pieceSel.value) { replace(out, h('p.notice.notice-warn', { role: 'alert' }, t('ui.prompt.noType'))); return; }
    if (!subject.value.trim()) { replace(out, h('p.notice.notice-warn', { role: 'alert' }, t('ui.prompt.noSubject'))); subject.focus(); return; }
    const body = { piece: pieceSel.value, subject: subject.value.trim() };
    if (zone.value.trim()) body.cleanZone = zone.value.trim();
    go.disabled = true;
    out.setAttribute('aria-busy', 'true');
    busy(out);
    try {
      const r = await api.brandPrompt(project, body);
      const d = r.defaults || {};
      replace(out,
        h('div.row-between', {}, h('h3', {}, t('ui.prompt.result')), h('span.hint', { data: { slot: 'words' } }, t('ui.prompt.words', { n: r.words }))),
        r.blocked ? h('p.notice.notice-bad', { role: 'status', data: { slot: 'blocked' } }, t('ui.prompt.blocked')) : null,
        h('pre.sheet-code', { data: { slot: 'prompt' } }, h('code', {}, r.prompt)), copyButton(r.prompt),
        h('h3', {}, t('ui.prompt.segments')),
        h('ol.stack', { data: { list: 'segments' } }, (r.segments || []).map((s) => h('li.seg', { data: { role: s.role } },
          h('div.row', {}, h('b', {}, t(`ui.prompt.role.${s.role}`)), h('code.mono.hint', {}, s.source === 'input' ? t('ui.prompt.fromYou') : s.source)),
          h('span', {}, s.text)))),
        h('h3', {}, t('ui.prompt.checks')), checkList(r.checks || []),
        h('h3', {}, t('ui.prompt.defaults')),
        h('dl.facts', { data: { slot: 'defaults' } },
          h('dt', {}, t('ui.sheet.col.profile')), h('dd', {}, d.profile ? h('code.mono', {}, d.profile) : '—'),
          h('dt', {}, t('ui.sheet.col.seed')), h('dd', {}, d.seed ?? '—'),
          h('dt', {}, t('ui.sheet.col.count')), h('dd', {}, d.count ?? '—'),
          h('dt', {}, t('ui.prompt.model')), h('dd', {}, d.model ? h('code.mono', {}, d.model) : '—'),
          h('dt', {}, t('ui.sheet.col.chroma')), h('dd', {}, d.chroma ? h('code.mono', {}, d.chroma) : t('ui.sheet.noChroma'))));
    } catch (e) { failed(out, e); }
    out.setAttribute('aria-busy', 'false');
    go.disabled = false;
  }

  async function lint() {
    if (!freePrompt.value.trim()) { replace(freeOut, h('p.notice.notice-warn', { role: 'alert' }, t('ui.prompt.noPrompt'))); freePrompt.focus(); return; }
    const body = { prompt: freePrompt.value };
    if (freePiece.value) body.piece = freePiece.value;
    lintGo.disabled = true;
    freeOut.setAttribute('aria-busy', 'true');
    busy(freeOut);
    try {
      const r = await api.brandLint(project, body);
      replace(freeOut, h('p.hint', { data: { slot: 'words' } }, t('ui.prompt.words', { n: freePrompt.value.trim().split(/\s+/).length })), checkList(r.checks || []));
    } catch (e) { failed(freeOut, e); }
    freeOut.setAttribute('aria-busy', 'false');
    lintGo.disabled = false;
  }

  host.append(
    h('section.card', { data: { card: 'prompt' }, aria: { labelledby: 'bp-h' } },
      h('h2', { id: 'bp-h' }, t('ui.prompt.title')), h('p.hint', {}, t('ui.prompt.intro')),
      h('div.field', {}, h('label', { for: 'bp-piece' }, t('ui.prompt.piece')), pieceSel),
      h('div.field', {}, h('label', { for: 'bp-subject' }, t('ui.prompt.subject')), subject, h('span.hint', { id: 'bp-subject-hint' }, t('ui.prompt.subjectHint'))),
      h('div.field', {}, h('label', { for: 'bp-zone' }, t('ui.prompt.zone')), zone),
      h('div.row', {}, go), out),
    h('section.card', { data: { card: 'lint' }, aria: { labelledby: 'bl-h' } },
      h('h2', { id: 'bl-h' }, t('ui.prompt.freeTitle')), h('p.hint', {}, t('ui.prompt.freeIntro')),
      h('div.field', {}, h('label', { for: 'bl-prompt' }, t('ui.prompt.freePrompt')), freePrompt),
      h('div.field', {}, h('label', { for: 'bl-piece' }, t('ui.prompt.freePiece')), freePiece),
      h('div.row', {}, lintGo), freeOut));
}
