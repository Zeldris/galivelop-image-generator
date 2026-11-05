/* Atajos de teclado (y del mando de la Deck, que Steam Input traduce a teclas: cruceta = flechas, A = Intro,
   B = Escape). Los de la galería los maneja order-view.js; aquí van los globales y el diálogo de ayuda.
   Ninguno actúa mientras el foco está en un campo de texto. */

import { h, el, replace } from '../dom.js';
import { t } from '../i18n.js';

export const SHORTCUTS = [
  ['ui.shortcuts.group.global', [
    [['?'], 'ui.shortcuts.help'],
    [['Q'], 'ui.shortcuts.queue'],
    [['Esc'], 'ui.shortcuts.escape'],
    [['Tab'], 'ui.shortcuts.tab'],
  ]],
  ['ui.shortcuts.group.gallery', [
    [['←', '→'], 'ui.shortcuts.prevNext'],
    [['↑', '↓'], 'ui.shortcuts.rows'],
    [['Intro'], 'ui.shortcuts.open'],
    [['S'], 'ui.shortcuts.yes'],
    [['N'], 'ui.shortcuts.no'],
    [['E'], 'ui.shortcuts.choose'],
    [['C'], 'ui.shortcuts.compare'],
    [['F'], 'ui.shortcuts.raw'],
    [['G'], 'ui.shortcuts.another'],
    [['R'], 'ui.shortcuts.prompt'],
    [['T'], 'ui.shortcuts.retouch'],
    [['X'], 'ui.shortcuts.texts'],
  ]],
];

const ONE_KEY = 'gvig.oneKey';

/** Interruptor «atajos de una tecla» (WCAG 2.1.4): activado por defecto, se guarda en el navegador. */
export function oneKeyEnabled() {
  try { return localStorage.getItem(ONE_KEY) !== 'off'; } catch { return true; }
}

function setOneKey(on) {
  try { localStorage.setItem(ONE_KEY, on ? 'on' : 'off'); } catch { /* sin almacenamiento: vale la sesión */ }
}

export function isTyping(target) {
  return target instanceof Element && (target.closest('input, textarea, select, [contenteditable="true"]') !== null);
}

export function initShortcuts({ toggleQueue, closeAll }) {
  const dlg = el('shortcuts');
  el('shortcuts-close').addEventListener('click', () => dlg.close());
  el('help').addEventListener('click', () => openHelp());
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { closeAll(); return; }
    if (isTyping(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
    if (!oneKeyEnabled()) return;
    if (e.key === '?') { e.preventDefault(); openHelp(); }
    else if (e.key === 'q' || e.key === 'Q') { e.preventDefault(); toggleQueue(); }
  });
}

export function openHelp() {
  const body = el('shortcuts-body');
  replace(body, h('dl', {}, SHORTCUTS.map(([group, items]) => [
    h('h3', {}, t(group)),
    items.map(([keys, label]) => [h('dt', {}, keys.map((k) => h('kbd.kbd', {}, k))), h('dd', {}, t(label))]),
  ])), h('label.check', {}, h('input', { type: 'checkbox', checked: oneKeyEnabled(), onchange: (ev) => setOneKey(ev.target.checked) }), h('span', {}, t('ui.shortcuts.oneKey'))),
  h('p.hint', {}, t('ui.shortcuts.oneKeyHint')), h('p.hint', {}, t('ui.shortcuts.deck')));
  el('shortcuts').showModal();
}
