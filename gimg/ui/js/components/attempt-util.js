/* Ayudas pequeñas compartidas por las tarjetas, el comparador, el chip de medida y el panel de retoque. */

/** Versión de la imagen de un intento para la URL (`?v=`): un hash corto (djb2) de lo que cambia al recomponer.
    La API no da fecha de composición, así que se deriva del propio registro. */
export function imageVersion(attempt) {
  const s = JSON.stringify([attempt.image, attempt.compose, attempt.composeError]);
  let hash = 5381;
  for (let i = 0; i < s.length; i += 1) hash = ((hash * 33) ^ s.charCodeAt(i)) >>> 0;
  return hash.toString(36);
}

/** El intento guarda el prompt con el estilo del perfil añadido (`prompt + ", " + style`): se quita el sufijo exacto
    para no duplicarlo al volver a enviarlo. */
export function stripStyle(prompt, style) {
  const text = prompt || '';
  if (!style) return text;
  const suffix = `, ${style}`;
  return text.endsWith(suffix) ? text.slice(0, -suffix.length) : text;
}

/** La primera palabra vetada (`brand.bannedWords`) que aparece en `text` como palabra entera, sin distinguir
    mayúsculas; null si no hay ninguna. Es un aviso, nunca un bloqueo. */
export function bannedWord(text, words) {
  const escape = (w) => String(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return (words || []).find((w) => w && new RegExp(`\\b${escape(w)}\\b`, 'i').test(text || '')) || null;
}
