/* Diálogo de motivo (0.8.0 §2.3): los rasgos de la hoja y «otro» (que pide una nota). Lo usan el «No» de un intento de
   un pedido de marca (`allowNone`: «Sin motivo», o una segunda N, descarta igual) y el «Ninguno vale» de una tanda
   (que además confirma). Resuelve {trait, text?}, {none: true} o null si se cancela. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { reasonChoices } from './brand-order.js';

export function askReason({ sheet, title, message = '', allowNone = false, confirmLabel, opener = null }) {
  return new Promise((resolve) => {
    let answer = null;
    const done = (v) => { answer = v; dlg.close(); };
    const textIn = h('input', { type: 'text', maxlength: 200, aria: { label: t('ui.reason.otherText') }, placeholder: t('ui.reason.otherText'), data: { slot: 'reason-text' } });
    const textRow = h('div.row', { hidden: true }, textIn,
      h('button.btn.btn-primary', { type: 'button', data: { slot: 'reason-other-ok' }, onclick: () => { const text = textIn.value.trim(); if (text) done({ trait: 'other', text }); else textIn.focus(); } }, confirmLabel || t('ui.reason.accept')));
    const choices = reasonChoices(sheet).map((c) => h('button.btn', { type: 'button', data: { trait: c.trait }, onclick: () => {
      if (c.trait === 'other') { textRow.hidden = false; textIn.focus(); } else done({ trait: c.trait });
    } }, c.label));
    const none = allowNone ? h('button.btn.btn-ghost', { type: 'button', data: { slot: 'reason-none' }, onclick: () => done({ none: true }) }, t('ui.reason.none'), h('kbd.kbd', { aria: { hidden: true } }, 'N')) : null;
    const dlg = h('dialog.confirm.reason', { aria: { labelledby: 'reason-title' } },
      h('h2', { id: 'reason-title' }, title), message ? h('p', {}, message) : null,
      h('div.row.reason-choices', { role: 'group', aria: { label: title } }, choices), textRow,
      h('div.row', {}, none, h('button.btn', { type: 'button', onclick: () => dlg.close() }, t('ui.newOrder.cancel'))));
    dlg.addEventListener('keydown', (ev) => {
      ev.stopPropagation();
      if (allowNone && (ev.key === 'n' || ev.key === 'N') && ev.target !== textIn) { ev.preventDefault(); done({ none: true }); }
    });
    dlg.addEventListener('close', () => {
      dlg.remove();
      const back = typeof opener === 'function' ? opener() : opener;
      if (back && back.isConnected) back.focus();
      resolve(answer);
    });
    document.body.append(dlg);
    dlg.showModal();
    if (choices[0]) choices[0].focus();
  });
}
