# Retro 2026-11-17: tanda L8, barrido P2 de `brand.py` y fase 1 antes de `main`

**Rama:** `ccr-85e9d14e-zt7p8b`, tramo desde `c5827e2` (PR #22) hasta `7e2e58c`.

**Estado:** aprobada y aplicada entera (P1 en `.claude/gw/gw-opt-tokens.md`, P2 en `REVIEW.md`, P3 en «Pendiente» de la bitácora, P4 en la fila de la rama), 2026-11-17.

## Medida (gw-opt-tokens)

`measure.py --since c5827e2`: principal 57 llamadas, 6,56 M de entrada (98 % caché), 115k de media, techo 138k,
0 compactaciones; revisor de fase 1 (`gw-reviewer`) ~45k. Lo fijo (sistema, herramientas, conectores) son ~82k del
arranque (84 %): conocido, la persona no lo cambia de momento. Lo evitable: `sed -n 590,800p gimg/brand.py` para
revisar en la sesión (4,5k que se arrastraron 220k) y el archivo de leves leído entero (77k arrastrados).

## Propuestas

- **P1 (tokens, proyecto · `.claude/gw/gw-opt-tokens.md`):** la revisión en la sesión de un diff de bloque de más de
  `reviewTrivialLines` líneas va al `gw-reviewer` (arranque 15-21k) en vez de leer el módulo en la principal; aquí se
  revisó dos veces lo mismo (sesión y fase 1). Ahorro: ~250k por bloque. Riesgo: el revisor no conoce la intención;
  contrapeso: el encargo la dice en un párrafo, como en esta fase 1.
- **P2 (revisión, proyecto · `REVIEW.md`):** el barrido P2 separó `stroke-opacity` y `stroke-width` en el estado
  pero los volvió a unir al llamar a `_mute_attrs`, y el test solo cubría un sentido; lo vio la fase 1. Regla de
  criterio: cuando un arreglo separa dos condiciones, el test cubre cada una sola y en los dos sentidos.
- **P3 (barrido, proyecto):** `gimg/brand.py` es el script con más leves abiertos (`_mute` de la fase 1, `fill` en
  `<line>`, `rgb` con separadores mezclados, exponentes, `hsl(none …)`, `fill-opacity`/`opacity`, `turn`/`rad`).
  Tarea para la 0.7.0: un barrido de color/pintura de `brand.py` que los cierre (la persona elige cuáles).
- **P4 (bitácora, proyecto):** la fila de `ccr-85e9d14e-zt7p8b` pasa de 800 caracteres (1075; el `pre-commit` avisa)
  y «Pendiente» decía «sin revisar» lo que la fila daba por revisado. Al cerrar la rama, mover lo hecho a «Hecho» con
  `handoff.py done` y dejar la fila en una línea.

## For Galivelop-workflow

- Nada nuevo; sigue abierto el de `tests-for.py --run` sin `tests/__init__.py` (en «Pendiente»).
