/* Botón «Copiar» de un texto al portapapeles, con aviso de lo copiado (o de que no se pudo). */

import { h } from '../dom.js';
import { t } from '../i18n.js';
import { toast, toastError } from './toast.js';

export function copyButton(text, { label = null, aria = null } = {}) {
  return h('button.btn.btn-ghost', {
    type: 'button', aria: { label: aria }, data: { slot: 'copy' },
    onclick: async () => {
      try { await navigator.clipboard.writeText(text); toast(t('ui.sheet.copied')); } catch { toastError(t('ui.attempt.copyFailed')); }
    },
  }, '⎘ ', label || t('ui.sheet.copy'));
}
