<!-- galivelop-workflow v0.9.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-85e9d14e-zt7p8b` (rama de la sesión; `main` `7c2f412` fusionada el 2026-11-24): leves de `brand.py` y pedidos de marca del Portal |
| **Fase / tarea** | FM, 0.7.0 «Hoja como datos» (`docs/plan/fm.md`; interfaz en `docs/interfaz/marca.md` §2.10 y §4) |
| **Último punto estable** | `main` en `7c2f412` (PR #28, flujo 0.9.0, 2026-11-24, CI en verde); release v0.6.0 publicada (etiqueta en `98fcc7c`, PR #20, 2026-11-16) |
| **Siguiente paso** | el de la fila de `ccr-85e9d14e-zt7p8b` |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |
| **Tarea en curso · `gw-0.9.0`** | Flujo a 0.9.0 (2026-11-24): `apply.py --update`, `gw.json` a `schemaVersion` 2 (bloque `languages`), `agentsSkillsDir: ".agents/skills"` fijado (decisión de la persona), gancho PreToolUse nuevo en `settings.json`; `AGENTS.md`, `CLAUDE.md` y `REVIEW.md` fusionados a mano (todos los cambios de plantilla aceptados). `apply.py --check` en 0, `doctor.py` sin FAIL (avisos: `workflowClone` y worktree viejo), check en verde (1951 tests). CI en verde en `20025ee`. Fase 1 hecha (0 hallazgos; código: `gw.json`, `settings.json`, `check.yml`). Fase 2: `gw-opt-tokens` sin propuestas (76 % arranque fijo); retro `docs/records/retro-2026-11-24-gw-0.9.0.md` aprobada (P1-P4, al flujo). Fase 3 hecha (marca `67d542c`). **PR #28 fusionado en `main`** (`7c2f412`, 2026-11-24, CI en verde, fusión confirmada por la persona). Siguiente: nada aquí. |
| **Tarea en curso · `gw-0.8.2`** | Flujo a 0.8.2 (2026-11-22): `apply.py --update` (111 archivos del flujo), `AGENTS.md` y `REVIEW.md` fusionados a mano; `apply.py --check` en 0 y `doctor.py` sin FAIL (aviso: `workflowClone`, P1). Fase 1 hecha (0 hallazgos). Fase 2: `gw-opt-tokens` sin propuestas nuevas; retro `docs/records/retro-2026-11-22-gw-0.8.2.md` aprobada (P1-P4; P1-P2 al flujo, P4 aplicada). **Próxima actualización del flujo (P3):** la rama sale de `main` y se le fusiona la de la anterior si tiene commits de bitácora fuera de `main` (`recover.py --state`). Fase 3 hecha (marca `78f9eb0`). **PR #27 fusionado en `main`** (`8c0a4b9`, 2026-11-22, CI en verde, fusión confirmada por la persona). Siguiente: nada aquí. |
| **Tarea en curso · `gw-0.8.1`** | Flujo a 0.8.1 (2026-11-19): `apply.py --update` aplicado, `AGENTS.md`/`CLAUDE.md` fusionados, `REVIEW.md` con ancla, «Invariantes» y «Navegadores», «Pendiente» movido a `docs/records/pending.md` (`pendingFile`), `legacyNames: false` (las citas viejas son de piezas fechadas o de otros repos), `whole-read.py` ya una sola vez. Fase 1 hecha (0 hallazgos; solo `gw.json`, `settings.json`, `check.yml` eran código); CI en verde en `662d7c0`; `gw-opt-tokens` presentada y aprobada (P1-P3, al flujo); retro `docs/records/retro-2026-11-19-gw-0.8.1.md` aprobada (P1-P5). **PR #26 fusionado en `main`** (`f025f40`, 2026-11-19, CI en verde). Queda: worktree `agent-ae25df5d0ca1f6b46` (solo 4 líneas borradas del registro; borrar con `--force` si la persona lo pide). Siguiente: nada aquí. |
| **Tarea en curso · `hoja-datos`** | **PR #25 fusionado en `main`** (`61ce509`, 2026-11-18, CI en verde): versión 0.7.0 «Hoja como datos». Leves abiertos en `docs/records/revision-hoja-datos-paso{1..5}.md` (barrido B de `brandsheet.py` para 0.8, en `docs/plan/fm.md`). Siguiente: publicar la release v0.7.0 si la persona lo pide; luego 0.8 según `docs/plan/fm.md`. |
| **Tarea en curso · `fix-0.4.1`** | Terminada (PR #5, v0.4.1). |
| **Tarea en curso · `ccr-85e9d14e-zt7p8b`** | `main` fusionada el 2026-11-24. Pedidos 34-36 del Portal en `examples/portal/orders/marca/`, sin generar (no hay cola de gimg en la nube): generarlos en local. Barrido B de `brandsheet.py` hecho (`bdc482a`, `5fdaefd`, `594c9fe`, revisión en `730f488`). **0.8.0 «Pieza de marca» empezada el 2026-11-26** (confirmada por la persona; el recorrido con mando en la Deck queda pendiente para antes de `main`): pasos en `docs/plan/fm.md` «0.8.0 en pasos». Presupuesto de compactaciones: 4 (la sesión ya arranca al 61 % por el sistema). Pasos 1 (`860a79f`) y 2 (`668cb16`, tandas) hechos; revisión de bloque: 4 medios arreglados en el commit de arreglos, 3 leves a `pending.md`. Pasos 3 (`7ef92cc`) y 4 (`85ae5f4`) hechos; revisión de bloque: 6 medios y 3 leves arreglados, 3 leves a `pending.md`. Siguiente: paso 5, interfaz. |
| **Tarea en curso · `claude/marca-r9`** | Terminada (PR #6). Queda, en otra tarea: medir una ronda plana y `og`/`social` con el lockup nuevo (y quitar la copia congelada y `REDRAWN_COPY_SHA256`). |
| **Tarea en curso · `portal-marca`** | Fusionada en `hojas-repos`; sus imágenes del Portal están completas en `piloto/portal-marca/portal-web-final/portal/` (LEEME; raíz = aprobado, `svg/`, `aprobadas/`, `pendiente/`, `descartes/`). Historia de rondas, intentos aprobados y reglas en «Hecho». Falta: la sesión del Portal aplica `docs/proposals/portal/entrega-marca-2026-11-12.md`. Siguiente: nada aquí; seguir por la fila de `hojas-repos`. |
| **Tarea en curso · `hojas-repos`** | Abierta el 2026-11-12 (hojas de estilo a cada repo por la vía A; detalle en «Hecho»). **Cola del generador parada**: pendientes #832, #834-835, #812, #814, #820, #824, #826 y el mapa de Tarkor; #833 sin revisar; reanudar con `gimg serve` (o `gimg queue resume` si se pausó). **Fusionada en `main` por el PR #8 (`2e6b642`, 2026-11-12, CI en verde)**; R1 `gimg queue pause|resume` incluida, retro aprobada. Después: cola del Portal, oscuras 10/18/19/27/28, prueba A1 a 768², nota de entrega al Portal, 61 pedidos de Tarkor. Leves: botón de pausa en la UI y `_busy` en pausa, hechos en `ccr-85e9d14e-zt7p8b` (2026-11-13); tonos repetidos sin validar el hex en `docs/marcas/*/tonos.py` y `acento*.py`, también hecho allí. Siguiente: reanudar la cola y revisar lo del Portal. |

Aquí `logRows` está apagado en `.claude/gw.json`: las filas se editan a mano (`handoff.py set-row` no escribe) y no
hace falta `GW_SHARED_LOG`. Aun así, cada rama toca solo su fila salvo al cerrar o fusionar otra.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-11-26 — ccr-85e9d14e-zt7p8b: PRs #23 y #24 fusionados; luego leves de brand.py (72bdd72) y de la fase 1 del 2026-11-17 (04f029e).
2. 2026-11-17 — 2026-11-16/17 · `ccr-85e9d14e-zt7p8b`: tanda L8 (orders, cli crop, export._resample, aviso del taller), barrido P2 de `brand.py`, `GIMG_AUTOSTART=0` en `tests/test_cli.py`; fase 1 (4 leves) y retro `retro-2026-11-17-tanda-l8.md`.
3. 2026-11-16 — **FM 0.6.0 Recortar (2026-11-16, `ccr-85e9d14e-zt7p8b`):** `gimg/crop.py` + `POST …/attempts/{id}/crop` (intento derivado con `derivedFrom`; errores `crop.bad_box|outside|ratio_mismatch|bad_target|write_failed|compose_unsupported`); revisión del backend (`2b1a08e`, Findings: 4: destino que compone rechazado, alta atómica del destino, `tileable` fuera). Interfaz: `box-drag.js` extraído de `layout-editor.js`, `crop-editor.js`, «Recortar» y distintivo en `attempt-card.js`; revisión (`34a00b1`, Findings: 7). Flujo a Galivelop-workflow v0.7.0 (confirmado por la persona).
4. 2026-11-15 — **Séptima tanda (L7), 2026-11-15, `ccr-85e9d14e-zt7p8b`:** `tile` marca como `.gimg-stale-*` la copia que no pudo borrar y `recover_backups` la borra o la da como `stale`, nunca como original; la CLI usa `tile.describe_recovery` (`42987df`). `brand`: el fill de `<line>` no cuenta al aplanar, `_has_fill` = `_sets`, `lockup --force` con `cli.arg.brand_force`, validaciones compartidas, color de `lockup` con `trace._COLOR`, `brand.write_file` público, `border_color` una vez, tests de `lockup` (`9bb35cd`). Taller: `resolve_font` pide el peso a `fc-match` y acepta `.ttc`/`.otc`, límites de la UI = servidor y `PIECES` = `SYSTEM_FILES` con test (`7b3b1a6`). Sin probar con fuente real (equipo de la persona): el peso en `fc-match` y una `.ttc` renderizada. Fuera: `trace` `min_island`; `brand_force_square` sobra (mismo texto que `brand_force`).
5. 2026-11-15 — **Sexta tanda acotada de leves (`ccr-85e9d14e-zt7p8b`), elegida por la persona:** `brand square`: un `<line>` ya no hereda el `fill` de la raíz; `trace` con `max_side` bajo ya no da error de capas vacías (si todo sale vacío y hubo reducción, repite sin suavizar y con `min_island`/factor²); `tile`: lo restaurado antes de un fallo de `recover_backups` viaja en `exc.recovered` y lo dice la CLI; la copia que no se pudo borrar tras un éxito sale en `stale_backups` y la CLI pide borrarla a mano.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `for f in .githooks/pre-commit .githooks/pre-push .githooks/commit-msg; do bash -n "$f"; done` y `python3 -m unittest discover -s tests -t .`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
