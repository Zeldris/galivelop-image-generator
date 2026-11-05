/* Modal para renombrar un pedido (F4e.5): un campo de texto con la clave actual y «Renombrar» / «Cancelar». Resuelve la
   clave nueva (texto) o null si se cancela, se cierra con Esc o no cambia. La clave pasa por el mismo patrón que al crear
   un pedido; lo demás (clave repetida, pedido ocupado) lo dice el servidor y sale en un aviso. El foco vuelve a `opener`. */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { KEY_PATTERN, MAX_KEY } from './new-order.js';

export function renameDialog({ current, opener = null }) {
  return new Promise((resolve) => {
    let answer = null;
    const error = h('p.notice.notice-bad', { id: 'rn-error', role: 'alert', hidden: true });
    const input = h('input', { id: 'rn-key', type: 'text', value: current, autocomplete: 'off', spellcheck: 'false', maxlength: MAX_KEY, aria: { describedby: 'rn-hint' } });
    const accept = () => {
      const value = input.value.trim();
      if (!KEY_PATTERN.test(value) || value.length > MAX_KEY) {
        error.textContent = t('ui.newOrder.keyInvalid');
        error.hidden = false;
        input.focus();
        return;
      }
      answer = value === current ? null : value;
      dlg.close();
    };
    const cancel = h('button.btn', { type: 'button', onclick: () => dlg.close() }, t('ui.newOrder.cancel'));
    const ok = h('button.btn.btn-primary', { type: 'submit' }, t('ui.order.renameConfirm'));
    const form = h('form', { onsubmit: (ev) => { ev.preventDefault(); accept(); } },
      h('div.field', {}, h('label', { for: 'rn-key' }, t('ui.order.renameLabel')), input, h('span.hint', { id: 'rn-hint' }, t('ui.order.renameHint'))),
      error, h('div.row', {}, ok, cancel));
    const dlg = h('dialog.confirm', { aria: { labelledby: 'rn-title' } }, h('h2', { id: 'rn-title' }, t('ui.order.renameTitle', { key: current })), form);
    dlg.addEventListener('keydown', (ev) => ev.stopPropagation());
    dlg.addEventListener('close', () => {
      dlg.remove();
      const back = typeof opener === 'function' ? opener() : opener;
      if (back && back.isConnected) back.focus();
      resolve(answer);
    });
    document.body.append(dlg);
    dlg.showModal();
    input.focus();
    input.select();
  });
}
