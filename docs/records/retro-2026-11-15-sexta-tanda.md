# Retro · sexta tanda acotada de leves (`ccr-85e9d14e-zt7p8b`, 2026-11-15)

**Estado:** aprobada por la persona el 2026-11-15: P1 aplicada (los leves de las tandas 1-5 en `docs/records/leves-ccr-85e9d14e-zt7p8b.md`, con puntero en la bitácora); P2 aprobada y apuntada para el flujo; P3 es una observación.

## Medidas (`gw-opt-tokens`, sesión `697aa2d0`)

63 llamadas en la principal, contexto medio 127k (suelo 95k, techo 140k), 1 compactación sobre un presupuesto de 1;
8,0 M de entrada en la principal y 3,0 M en 3 subagentes (Sonnet 2,3 M; la revisión de la fase 1 con Opus, 0,68 M).
Lo más arrastrado: la bitácora, 5 lecturas y 203k (una sola lectura de «Pendiente», 190k).

## Propuestas

- **P1 (proyecto) · «Pendiente» de la bitácora a un registro aparte.** Los leves de las tandas ya cerradas pasan a
  `docs/records/leves.md` y en la bitácora queda una línea con el puntero. `recover.py --state` corta a 9 500
  caracteres justo dentro de «Pendiente», así que hubo que leerlo con `sed` (190k arrastrados). Riesgo para la
  calidad: ninguno, los leves siguen en un archivo y la próxima tanda los elige de ahí.
- **P2 (para Galivelop-workflow) · arreglos tras fusionar un subagente.** `merge-branch.sh` borra el worktree, y luego
  `SendMessage` al mismo subagente falla («its worktree no longer exists»). `gw-orchestrate-dealer` pide devolverle
  los arreglos de la revisión, pero la fase 1 llega después de fusionar. Propuesta: el paso 3 dice que, tras la
  fusión, los arreglos van a un subagente nuevo con el archivo de hallazgos como puntero (arranque medido: 66k), o que
  `merge-branch.sh` tenga un `--keep-worktree`. Riesgo: ninguno.
- **P3 (observación, sin cambio) · la revisión por trozo se saltó.** La rama de `trace` se fusionó tras revisar yo
  su diff, sin el `/code-review` corto de un subagente que pide el paso 3 del dealer. Sus dos medios aparecieron en la
  fase 1 y costaron una ronda más (0,75 M). La regla ya existe: se aplica, sin regla nueva.

## For Galivelop-workflow

- P2: `gw-orchestrate-dealer` paso 3 / `merge-branch.sh`: los arreglos que llegan después de la fusión no pueden
  volver al subagente original porque su worktree ya no existe; decir que van a uno nuevo con el archivo de hallazgos,
  o añadir `--keep-worktree`.
