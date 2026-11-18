# Retro 2026-11-18 — 0.7.0 «Hoja como datos» (`hoja-datos`)

**Estado:** aprobada por la persona el 2026-11-18; P1 aplicada (`brandsheet.*` da 422 por defecto, con test), P2
apuntada como tarea de 0.8 en `docs/plan/fm.md`, P3 aplicada en `.claude/gw/gw-orchestrate-dealer.md` y propuesta al
flujo.

Fuentes: commits `43ef055..df00944`, revisiones de bloque `docs/records/revision-hoja-datos-paso{1..5}.md`, medida de
`gw-opt-tokens` (sus propuestas P2-P4 aprobadas y aplicadas el 2026-11-18; P1, conectores MCP, no se puede en la nube).

## Lo que funcionó

- La fase 1 adelantada a cada bloque: 5 revisiones (14, 12, 8, 11 y 10 hallazgos), 27 arreglos con su commit, y la
  fase 1 final fue trivial (versión y documentación, 0 hallazgos).

## Propuestas

### P1 (proyecto, comprobación) — el estado HTTP de `brandsheet.*` por prefijo

El mismo fallo en tres sitios: `brandsheet.invalid` y `bad_placeholder` mal clasificados (paso 1, #10), `bad_placeholder`
fuera del grupo 422 (paso 2, #4; seguía abierto: daba 400 por su `.bad_`) y los códigos de `brand md` (`3cb3395`). El test exige que
cada código esté en la tabla, pero no en qué grupo. Cambio: en `gimg/server.py`, `brandsheet.*` da 422 salvo los que
estén en otra lista (404/409/400 o los 500 de solo CLI), y un test que lo comprueba con `bad_placeholder`. Riesgo: un
código de CLI que debería ser 500 sale 422; la lista de 500 de `tests/test_server.py` lo sigue nombrando.

### P2 (proyecto, barrido) — leves de `gimg/brandsheet.py` para 0.8

`brandsheet.py` es el script con más leves abiertos de la rama (16). Una tarea B en dos encargos (regla de más de
~4 leves por módulo): paso 1 #6 (hex «missing» solo en la última frase), #7 (`_HEX` sin `#rgb`/`#rrggbbaa`), #8 (zona
limpia de espacios), #9 (registro contenido en otro), #11 (repite el contraste de `measure.py`), #12 (`lint` recalcula
`palette()`), #13 (documentar que la herencia no borra claves), #14 (test de `..` por `extends`); paso 3 #4 (orden con
`cleanZone: afterClosing`), #5 (`own_text` exime todos los registros), #6 (marcador malo sin decir la pieza), #7
(validación de marcadores duplicada), #8 (`own_text` y `quiet`, la misma lista); paso 4 #7 (rama `threshold`
imposible), #8 (`try` de `accent_tones` repetido), #11 (`_block_span` recorre el texto cinco veces).

### P3 (flujo) — buscar el ayudante antes de escribirlo

El leve más repetido (≥8 en 5 revisiones: paso 1 #11-12, paso 2 #11, paso 3 #7-8, paso 4 #8 y #11, paso 5 #9) es
código repetido o recalculado, y lo escribieron subagentes `gw-worker`. Cambio: una línea en el encargo de
`gw-orchestrate-dealer`, «antes de escribir una función auxiliar, busca con `grep` una que ya lo haga en el módulo y
en los que importa». Riesgo: ninguno; la revisión lo sigue mirando.

## For Galivelop-workflow

- P3, la línea del encargo de `gw-orchestrate-dealer`.
- El tope de 30 llamadas (de `.claude/gw/gw-orchestrate-dealer.md`) debería venir en la plantilla del encargo del
  flujo, no en las notas del proyecto: un encargo de arreglos sin él hizo 92 llamadas (gw-opt-tokens, 2026-11-18).
