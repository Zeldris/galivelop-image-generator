# Revisión de bloque del paso 3 de hoja-datos (2026-11-17)

Diff `ea89d45..a627f98`+bitácora, `/code-review --max-findings all`, revisor de contexto limpio. 8 hallazgos: 3 medios
(1-3, se arreglan en la rama) y 5 leves (4-8, pendientes aquí).

## Leves pendientes

4. **Hecho (barrido B a).** `gimg/brandsheet.py` (orden de la zona con `cleanZone: afterClosing`): da ok aunque falte el cierre y acepta la
   zona en cualquier posición tras el comienzo del cierre (solo rechaza `zone[0] < closing_span[0]`).
5. **Hecho (barrido B a).** `own_text` exime de vetos y `neverWrite` el bloque de **todos** los registros de la hoja, no solo el de la pieza;
   hoy sin efecto (ningún bloque contiene un término vetado), pero un producto que vete una palabra de un bloque
   heredado lo destaparía.
6. **Hecho (barrido B a).** Un marcador malo en el `paletteSentence` de un tipo da `brandsheet.bad_placeholder` sin decir de qué pieza.
7. El bucle de validación de marcadores está copiado dos veces (un `_check_placeholders(..., piece=None)` arregla 6 y 7).
8. `own_text` (vetos) y `quiet` (negaciones) son la misma lista calculada dos veces.

## Queda para después (de los pasos 1-2, sin cambio)

`known` = `[]`; checks sin `field`; `from`/`overrides`/`key` en `brand/prompt`; `origin` por ruta de hoja (no por
objeto); `acceptance` sin refs ni `unmeasured`; filas de `check` «md↔datos», «refs existen», «aprobadas ≥ umbral».
