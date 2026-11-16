# Retro — FM 0.6.0 Recortar (`ccr-85e9d14e-zt7p8b`, 2026-11-16)

**Estado:** pendiente de la persona (P1-P5).

Fuentes: los registros de las sesiones `0cacc78c` (trabajo) y `66ab8160` (fase 2), buscados con `recover.py --search`,
y `git log 4624825..HEAD` (30 commits; revisiones de bloque `Findings: 4` y `Findings: 7`, sin `Retries`).

## Propuestas, de más a menos grave

### P1 — Tests relacionados en las subidas a la rama (del proyecto; tocar `.claude/gw.json` pide tu permiso)

- **Qué pasó:** `relatedTests` y `testMap` están vacíos. Por eso cada subida a la rama de trabajo corre el check
  entero (~4,5 min, 1.779 tests); el `pre-push` lo dice: «relatedTests has no command».
- Tres subidas chocaron con otro check en marcha, a las 16:11, 16:35 y 17:43: «CHECK FAILED: not run, another check
  is running». Cada vez hubo que mirar procesos y volver a subir.
- **Cambio:** en `.claude/gw.json`:
  - `testMap.rules`: `gimg/(?P<m>\w+)\.py` → `tests/test_{m}.py`, y `gimg/ui/` → `tests/test_ui.py` y
    `tests/test_ui_browser.py`.
  - `testMap.command`: `python3 -m unittest {files}`.
  - `relatedTests.fast`: `python3 .claude/gw/scripts/tests-for.py --run {files}`.
  - `checkLockWait`: 300, para que una segunda subida espere al check en marcha en vez de fallar.
- El check entero se sigue corriendo al subir a `main` y en el CI.

### P2 — `leer-entero.py` frente a `whole-read.py`: se quedan los dos (del proyecto y del flujo)

- No hacen lo mismo:
  - `leer-entero.py` **rechaza** leer entero `docs/plan.md`, que `whole-read.py` no vigila.
  - `whole-read.py` solo **avisa**, y vigila la bitácora, su archivo y `docs/records/`.
- Meter `docs/plan.md` en `wholeReadPaths` y borrar `leer-entero.py` cambiaría un rechazo por un aviso. Ese rechazo
  nació de los 348k de F2.0.
- Lo caro del diseño de FM no lo para ninguno de los dos: fueron lecturas con `sed`/`grep` por Bash. Eso ya lo cubre
  la regla aprobada el 2026-11-16: el contrato lo escribe un subagente.
- **Cambio del proyecto:** juntar los dos bloques PreToolUse de `Read` de `.claude/settings.json` en el `^Read$`
  (es el leve ya apuntado; pide tu permiso).
- **Cambio para el flujo:** ver más abajo.

### P3 — Barrido de leves de `crop-editor.js` (del proyecto, para 0.7.0)

- `gimg/ui/crop-editor.js` es el archivo con más leves abiertos (5, en `docs/records/leves-ccr-85e9d14e-zt7p8b.md`,
  «interfaz de recortar»):
  - `refresh()` completo en cada `pointermove`;
  - error duplicado entre `showError` y `toastError`;
  - «Repetir» activo con un perfil que compone;
  - trampa de foco copiada de `layout-editor.js` (`trapDialog` compartido);
  - `boxFor` repite `toBox`.
- Una tarea B (`handoff.py next-id B` no da id: `plan` está vacío en `.claude/gw.json`) que los cierre en 0.7.0.
- Lo siguiente es `orders.add_derived`, con 2 leves.

### P4 — Cambio de contrato a mitad de trabajos en paralelo (del proyecto, nota de `gw-orchestrate-dealer`)

- **Qué pasó:** el arreglo de la revisión del backend añadió `crop.compose_unsupported` mientras otro subagente
  hacía la interfaz. Al unirlos falló `test_crop_moves_the_box…` en `tests/test_ui_browser.py`.
- `merge-branch.sh` lo cazó. Arreglarlo costó un subagente más (`c58326c`).
- **Cambio:** una línea en `.claude/gw/gw-orchestrate-dealer.md`. Si un arreglo cambia el contrato (un código de
  error, un estado, un campo), se avisa al trabajo en paralelo que lo usa, o se fusiona antes.

### P5 — Esquema de `Monitor` sin cargar (leve, sin cambio)

Una llamada a `Monitor` falló por no haber cargado antes su esquema con `ToolSearch`. Pasó una vez; no merece regla.

## Para Galivelop-workflow

- **G1 (de P2):** que `whole-read.py` acepte rutas que se **rechazan**, no solo que se avisan; por ejemplo,
  `wholeReadDenyPaths` con su orden alternativa. Así un proyecto no necesita su propio `leer-entero.py`.
- **G2:** que `merge-branch.sh` no intente borrar un worktree bloqueado por un agente vivo. El 2026-11-16 dio
  «cannot remove a locked working tree». Que diga que se limpiará cuando el agente acabe, o que lo deje en una lista
  para la siguiente pasada.
- **G3 (de P1):** que `doctor.py` avise cuando `branchCheck` es `related` y `relatedTests` está vacío: cada subida a
  una rama corre entonces el check entero sin que nadie lo haya elegido.
