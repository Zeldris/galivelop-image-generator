# Revisión de bloque — `hoja-datos`, paso 1 (2026-11-17)

Revisión de bloque (fase 1) de `origin/main...44e5e7c`: `/code-review --max-findings all` con el criterio de
`REVIEW.md`, hecha por `gw-reviewer`. Hay 14 hallazgos: 1 grave, 4 medios y 9 leves.

Está comprobado y bien:

- `accent_tones` da lo mismo que `docs/marcas/galivelop-developer/tonos.py` en 3008 colores.
- La guarda D25: `paths.inside` en `projects.load_config` y en `_project_sheet`, y `..` lo rechaza el esquema.
- Se detectan los ciclos de `extends`.

**Hecho (2026-11-17):** el arreglo de los puntos 1-5 (además, `palette()` omite los tonos si no hay tono posible, en vez de saltar). Plan seguido: Va a un subagente: `opus` para el 5, que toca la guarda, y `sonnet` para
el resto. Va en un commit con `Findings: 5`, y cada test nuevo se pasa por `red-without-fix.sh`. Los leves (6-14) se
quedan apuntados aquí y no vuelven a revisarse en este PR.

## Grave

1. **`gimg/brandsheet.py:454-463` — `lint` bloquea el cierre real del Portal.**
   - `colorWord` no exime el cierre ni los bloques de registro (la comprobación de negaciones sí los exime), ni los
     `promptName` de `palette.dark`.
   - Con el cierre de `docs/marcas/portal/hoja.md` («…no frame, no white margin, no blank band») y «white» vetado, todo
     prompt montado por gimg da `blocked=True`.
   - El `CLOSING` del fixture (`tests/test_brandsheet.py:26`) recorta esa parte y por eso no se ve.
   - **Arreglo:** meter en `shield` el cierre, las posiciones de los registros y los `promptName` de `palette.dark`, como
     hace `quiet`. El fixture usa el cierre real.

## Medios

2. **`gimg/brandsheet.py:85` (`_owned`) — `origin` atribuye mal `vetoes.exceptions`.**
   - Cada hoja numera desde 0, pero las listas se concatenan.
   - **Arreglo:** un desplazamiento acumulado en `resolve` y corregir la aserción de `tests/test_brandsheet.py:175`
     (0 = portal, 1 = family).
3. **`gimg/brandsheet.py:276` (`palette`) — una hoja con papel oscuro (`#101820`) hace que `palette()`, y con ella
   `lint`, salte con `brandsheet.no_tone`.**
   - **Arreglo:** elegir la dirección por la luminancia del papel (o calcular el tono hondo sobre `PAPER_LIGHT`, como
     `tonos.py`), o validarlo en `resolve` con un 4xx. `lint` no debe depender de la excepción.
4. **`gimg/brandsheet.py:443` (`_word_spans`) — los plurales se saltan los vetos.**
   - «paper boats», «anchors» o «reds» pasan, y lo mismo en `neverWrite`.
   - **Arreglo:** un sufijo de plural opcional `(?:e?s)?` en el último término, con un test por veto, color y
     `neverWrite`.
5. **`test_parent_sheet_outside_root_by_symlink` no ejercita la guarda de `_project_sheet` (`brandsheet.py:65`).**
   - `load_config` ya da `path.outside` antes de llegar a ella.
   - **Arreglo:** hacer mock de `projects.get` (o cambiar el symlink después de `load_config`) y pasarlo por
     `red-without-fix.sh`.

## Leves (apuntados, no se arreglan en este PR salvo que caigan de paso)

6. `brandsheet.py:395`: el hex «missing» mira solo la última frase del prompt, así que falla con un `paletteSentence`
   de varias frases.
7. `brandsheet.py:30`: `_HEX` solo ve `#rrggbb`, así que `#f00` y `#ff0000cc` pasan.
8. `brandsheet.py:420`: con una zona limpia de solo espacios, `assemble` la descarta pero `lint` da
   `clean_zone_missing`.
9. `brandsheet.py:400`: un registro contenido en otro da `register_many` (con los textos actuales no pasa).
10. `brandsheet.py:48`: `brandsheet.invalid` y `bad_placeholder` serían 400, mientras `project.config_invalid` es 500.
    Se decide en el paso 2.
11. `brandsheet.py:185-212`: repite hex, linealización y contraste de `gimg/measure.py`.
12. `brandsheet.py:475`: `lint` recalcula `palette()` y `palette_sentence()` cada vez. Se calcularán en `resolve` para
    el lint en vivo del paso 5.
13. `brandsheet.py:91` (`_merge`): la herencia no puede borrar claves heredadas. Hay que documentarlo en el esquema.
14. `test_parent_sheet_with_dotdot_rejected` prueba solo el esquema, no `..` por `extends`. Hay que renombrarlo o
    anotarlo.
