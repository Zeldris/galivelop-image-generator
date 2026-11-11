<!-- galivelop-workflow v0.5.0 -->
# gw-opt-tokens — notas del proyecto

Las lee la skill `gw-opt-tokens` antes de proponer nada, y se actualizan cuando la persona aprueba un cambio. El flujo
las crea una vez; desde entonces son del proyecto.

## Herramientas que ya ahorran

<!-- Una línea cada una, con cómo se corre. -->
- `python3 .claude/gw/scripts/recover.py --state` y `--search "<texto>"`: recuperar lo que se llevó una
  compactación.
- `gw-orchestrate-dealer`: el trabajo de más de un paso, repartido a subagentes de contexto limpio.
- Aviso de presupuesto de compactaciones: `recover.py --state` (gancho tras compactar o `/clear`) compara las
  compactaciones de la sesión con «Presupuesto de compactaciones: N» de la fila de la rama (de serie desde la v0.5.0;
  aprobado aquí el 2026-10-27).
- `.claude/hooks/leer-entero.py` (PreToolUse de Read): rechaza leer `docs/plan.md` entero sin `offset`/`limit` y dice
  el `grep` que basta (aprobado el 2026-10-27). Otro documento grande se añade a `GRANDES`.
- `gimg sheet IMAGEN... --out hoja.png`: hoja de contactos con rótulos; las rondas se revisan con una hoja, no con
  imágenes sueltas (una hoja de 6 cuesta como una imagen; aprobado el 2026-11-04).
- Subagentes que escriben código mientras la principal sigue: en worktree (`isolation: "worktree"`) y de vuelta con
  `merge-branch.sh`, nunca en el árbol principal (el gancho de parada bloqueó 5 vueltas × ~105k el 2026-11-04; aprobado
  ese día, propuesto al flujo en `docs/records/retro-2026-11-04-f2-motor.md`).
- Cada `docs/records/lectura-*` abre con `**HEAD leído:** <repo> <rama> <sha>`: la siguiente lectura empieza con
  `git log <sha>..` (aprobado el 2026-11-04).

- Aquí `logRows` está apagado: las filas de la bitácora se editan a mano, sin `handoff.py set-row` ni
  `GW_SHARED_LOG` (descubrirlo costó 4 llamadas el 2026-11-05; aprobado ese día).

## Costes conocidos

<!-- Lo que se ha visto que cuesta mucho en este proyecto (archivos grandes leídos enteros, salidas largas...). -->
- Leer enteros los documentos del flujo (`README.es.md`, `docs/es/apply.md`, `gw-init/SKILL.md`): 7,5k tokens
  arrastrados 362k (6 % de la sesión). Para aplicar o actualizar el flujo: `apply.py --help` o `--check`, o la
  lectura a un subagente.
- `cat` de `CLAUDE.md` o `AGENTS.md`: ya están en el contexto; releerlos costó 151k arrastrados.
- `cat docs/handoff.md` (9 veces, 80k arrastrados): usar `python3 .claude/gw/scripts/recover.py --state`.
- «Pendiente» de la bitácora lleno de leves de ramas fusionadas (2026-11-06, `fix-0.4.1`: 7 lecturas, 247k
  arrastrados, 5,5 % de la sesión; 28,5k caracteres): al fusionar una rama, sus leves pasan a
  `docs/records/leves-<rama>.md` y en «Pendiente» queda un puntero de una línea (aprobado el 2026-11-06).
- `cat docs/plan.md` entero al empezar una fase (F0: 3,7k tokens junto con la bitácora, 97k arrastrados): basta
  `grep -n '^| F0' docs/plan.md` y las decisiones que cite (`grep -n '^| D1[25] ' docs/plan.md`).
- Escribir en la sesión principal el contrato de una fase («F1 en detalle»): leer `plan.md`, los esquemas y
  `schema.py` enteros arrastró unos 750k tokens (9 % de la principal en F1). Desde F2 lo escribe un subagente
  (`.claude/gw/gw-orchestrate-dealer.md`).
- `grep` amplio sobre `docs/plan.md` (2026-11-04: 291k arrastrados): buscar con el ancla de la fila
  (`grep -n '^| F2.1[0-2]' docs/plan.md | cut -c1-400`) o `sed -n` sobre el rango (aprobado el 2026-11-04).

- Mirar en la sesión principal las imágenes del piloto (F2.0: 25 imágenes, ~1 M arrastrado): el veredicto de estilo o
  composición lo da un subagente Fable que devuelve texto; la persona las ve en las páginas de `examples/pilot/ver.py`
  (aprobado el 2026-10-27).
- Iterar scripts del piloto en la principal (F2.0: `ronda.sh` 24 lecturas y `componer.py` 17, ~200k arrastrados): va
  a un subagente sonnet con su check, como los arreglos de la revisión de `bb7719a` (aprobado el 2026-10-27).

## Ajustes en vigor

- Ventana de compactación automática: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` en `.claude/settings.json`, 200000 desde el
  2026-11-11 por decisión de la persona (140000 se quedaba corto: 5 compactaciones en `claude/marca-r9`, con
  presupuesto de 3). Del 2026-11-05 al 2026-11-11 fue 140000 (la regla de `/clear` a los 120k se incumplió en F4: 229
  llamadas a 105k de media y techos de 168k).
- Un paso del plan por subagente implementador (no «F4b.1-F4b.2»): los de dos pasos hicieron 60-66 llamadas a
  96-105k de media, ~6,3 M cada uno (aprobado el 2026-11-05).
- `/clear` entre tareas: al cerrar cada PR y cada fase (F0…F5), con la bitácora escrita y subida (aprobado el
  2026-10-25; el diseño fue un solo tramo de 50 llamadas que llegó a 166k).
- `/clear` también al cerrar cada paso de una fase (F1.x) si la sesión principal pasa de ~120k (aprobado el
  2026-10-25; F1 en un tramo de 38 llamadas llegó a 167k).
- En F2.0, cada ronda del piloto (rN) cuenta como paso: se cierra con la bitácora subida y `/clear` (aprobado el
  2026-10-27).

## Referencias medidas

<!-- Cifras medidas con las que comparar: fecha, sesión, contexto medio, llamadas, total. -->
- 2026-11-05, `f2-motor` desde `849b301` (F3.3-F4d, 4 sesiones): ~98 M de entrada, 66 % en subagentes; la principal
  más cara, `0e571705`: 229 llamadas, 105k de media, 3 tramos (118/166, 110/168, 77/95).
- 2026-10-25, sesión `a0f496d5` (aplicar el flujo y diseño D1-D26): 50 llamadas, contexto medio 113k (suelo 38k,
  techo 166k), 5,6 M de entrada en la principal + 0,9 M en subagentes.
- 2026-10-25, sesión `1d4848af` (F0 hasta la retro): 30 llamadas, contexto medio 81k (suelo 45k, techo 115k),
  2,4 M de entrada en la principal + 1,3 M en 4 subagentes (la revisión con Opus, 0,58 M).
- 2026-10-25, sesión `38762d2d` (F1 entera, F1.1-F1.6 y su revisión): 77 llamadas, contexto medio 109k (suelo 53k,
  techo 131k; el primer tramo, 167k), 8,4 M de entrada en la principal + 13,4 M en 20 subagentes (Sonnet 11,6 M;
  la revisión con Opus, 1,8 M).
- 2026-10-26/27, sesión `3220fabf` (F2.0, r2-r5, biblias, logos, propuesta de interfaz): 318 llamadas, 5 compactaciones
  sobre un presupuesto de 4, contexto medio 114k (suelo 66k, techo 158k), 36,4 M de entrada en la principal + 16,8 M en
  20 subagentes (Fable 13,3 M). La sesión siguiente, tras `/clear`: 34 llamadas, 77k de media.
- 2026-11-04, sesión `19a5eb0e` (lectura del LoRA, F2.10, hoja de estilo, revisión antes de `main`): 72 llamadas,
  contexto medio 105k (suelo 43k, techo 153k), 0 compactaciones; la revisión con Opus, 20 llamadas y 2,1 M.
