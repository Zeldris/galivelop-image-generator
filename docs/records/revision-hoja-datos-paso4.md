# Revisión de bloque del paso 4 de 0.7.0 (`hoja.md` desde `marca.json`)

2026-11-17. Diff `2681fa2..fd400df` (`gimg`, `tests`), `/code-review --max-findings all` con un `gw-reviewer`.
11 hallazgos: 3 medios (1-3) y 8 leves. Se arreglan 1, 2, 3, 5, 6, 9 y 10 (`Findings: 7`).

## Leves que quedan (no vuelven a revisarse en este PR)

- **4.** `gimg/cli.py` (`brand md --write`): `Path.read_text` convierte los CRLF de la prosa en LF; una `hoja.md`
  con CRLF se reescribe entera. Arreglo: leer con `newline=""`.
- **7. Hecho (barrido B b**, rama quitada; las cadenas `brandsheet.md.threshold` de `gimg/locales/` siguen, fuera del alcance del encargo)**.** `gimg/brandsheet.py` (`markdown`, aceptación): la rama `threshold` no puede darse (el esquema no tiene ese
  campo) y sus cadenas `brandsheet.md.threshold` sobran. Quitarlas o añadirle el origen cuando entre en el esquema.
- **8. Hecho (barrido B b**, `_tones`)**.** `gimg/brandsheet.py`: el `try`/`except` de `accent_tones` con los papeles por defecto está repetido en
  `palette()` y en `markdown()`; un ayudante común `_tones(pal)`.
- **11. Hecho (barrido B b**, `find`/`rfind`)**.** `gimg/brandsheet.py` (`_block_span`): recorre el texto hasta cinco veces; con dos `find` basta.
