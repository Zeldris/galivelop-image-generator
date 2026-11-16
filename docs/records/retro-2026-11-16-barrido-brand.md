# Retro 2026-11-16: barrido de `brand.py` y revisión de bloque (rama `ccr-85e9d14e-zt7p8b`)

**Estado:** aprobada por la persona (2026-11-16): P1 aplicada en el proyecto (`.claude/gw/gw-opt-tokens.md`) y propuesta al flujo (abajo); P2 apuntada en «Pendiente» para 0.7.0, con `brand.py`. P3 era solo informativa.

Alcance: desde `fa842ef` (PR #21) hasta `c209756`: barrido de `gimg/brand.py` (P5 de la retro anterior), dos leves de
`orders.add_derived` y revisión de bloque contra `main` (`f41df36`, `Findings: 2`).

## Medida (`gw-opt-tokens`, `measure.py --since fa842ef`)

- Principal: 77 llamadas, 8,3 M de entrada (108k de media, techo 139k, 0 compactaciones), todo con el modelo grande.
- Subagentes: ninguno. Los `gw-worker` Sonnet de la tarea anterior trabajaron a ~32k de media por llamada.
- Arranque tras `/clear`: 97k (61 % del tope de compactación); ~82k son sistema, herramientas y MCP.

## Propuestas

**P1. Barridos y arreglos de revisión a un `gw-worker` (proyecto y flujo).** El barrido, los arreglos de
`orders.add_derived` y los de la revisión de bloque se hicieron en la principal, contra la regla de `AGENTS.md` y
`gw-orchestrate-dealer`. En un `gw-worker` habrían sido ~2,5 M de Sonnet en vez de 8,3 M del modelo grande. Riesgo:
Sonnet falla más en la semántica de pintura SVG; lo cubre la revisión de fase 1, que no se toca.

**P2. Barrido de `gimg/brand.py` para 0.7.0 (proyecto).** Cuatro leves abiertos en el archivo que cambió el bloque:
`_mute_attrs` sin efecto sobre los `<g>` en `flat`; dos bucles casi iguales en `_paint_colors`; `_no_paint` duplica
las sustituciones de `_mute_attrs` (y ya difieren en `prop=prop`); `_mute` mezcla `stroke-opacity` 0 y
`stroke-width` 0 en un booleano. Los tres de `orders.py` (cosméticos) se quedan en el archivo de leves.

**P3. Contexto de arranque (informativo).** El conector `Claude_Docs` no se usa aquí; quitarlo del entorno lo decide
la persona.

## For Galivelop-workflow

- P1: que `gw-selector`, al empezar un barrido o los arreglos de una revisión con 2 o más puntos, recomiende
  explícitamente repartirlo a un `gw-worker` y no hacerlo en la principal.
