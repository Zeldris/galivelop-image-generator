/* Trampa de foco de los editores modales (recorte y capas): el `keydown` del `dialog` no sale al resto de la página,
   Tab y Mayús+Tab dan la vuelta dentro del diálogo y, al cerrar, el foco vuelve a quien lo abrió. */

const FOCUSABLE = 'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), [tabindex="0"]';

/**
 * Instala la trampa en `dlg`. `opener`: el botón que lo abrió; `fallback`: función que devuelve el nodo alternativo si el
 * botón ya no está (el pedido se recarga y la tarjeta se rehace). Los oyentes corren por orden de registro: el editor
 * registra primero su propio `close` (`dlg.remove()`…) y llama a esta función después, así el foco se devuelve al final.
 */
export function trapDialog(dlg, { opener, fallback } = {}) {
  dlg.addEventListener('keydown', (ev) => {
    ev.stopPropagation(); // los atajos de la galería y los globales no actúan con el editor abierto
    if (ev.key !== 'Tab') return;
    const nodes = [...dlg.querySelectorAll(FOCUSABLE)].filter((n) => n.getClientRects().length > 0);
    if (!nodes.length) return;
    const first = nodes[0];
    const last = nodes[nodes.length - 1];
    if (ev.shiftKey && (document.activeElement === first || document.activeElement === dlg)) { ev.preventDefault(); last.focus(); }
    else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
  });
  dlg.addEventListener('close', () => {
    const back = opener && opener.isConnected ? opener : (fallback ? fallback() : null);
    if (back) back.focus();
  });
}
