# Revisión de bloque del paso 5 de 0.7.0 (pestaña Marca)

2026-11-17. Diff `3cb3395..aaf0004` (`gimg`, `tests`, `docs/api.md`), `/code-review --max-findings all` con un
`gw-reviewer`. 10 hallazgos: 6 medios (1-6) y 4 leves. Se arreglan 1-8 en `2666313` (`Findings: 8`; parte del
backend en `6c4aab6`, el contenedor se reinició a medias).

## Leves que quedan (no vuelven a revisarse en este PR)

- **9.** `gimg/doctor.py` (fila `sheet.markdown`): `brandsheet.markdown` se llama para `es` y para `en`, y cada una
  vuelve a resolver la cadena de hojas que `_sheet` ya resolvió. Arreglo: pasar la hoja resuelta o montar la vista
  una vez y pintarla en los dos idiomas.
- **10.** `gimg/ui/js/components/brand-prompt.js` (prompt libre): cuenta palabras en el cliente con `split(/\s+/)`
  en vez de usar `params.count` de la comprobación `words` del servidor; los dos números pueden no coincidir.
