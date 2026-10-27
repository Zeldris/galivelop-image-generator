<!-- galivelop-workflow v0.4.0 -->
# opt-tokens — notas del proyecto

Las lee la skill `opt-tokens` antes de proponer nada, y se actualizan cuando la persona aprueba un cambio. El flujo
las crea una vez; desde entonces son del proyecto.

## Herramientas que ya ahorran

<!-- Una línea cada una, con cómo se corre. -->
- `python3 .claude/gw/scripts/recuperar.py --estado` y `--buscar "<texto>"`: recuperar lo que se llevó una
  compactación.
- `orchestrate-dealer`: el trabajo de más de un paso, repartido a subagentes de contexto limpio.
- Aviso de presupuesto de compactaciones: `recuperar.py --estado` (gancho tras compactar o `/clear`) compara las
  compactaciones de la sesión con «Presupuesto: N compactaciones» de la fila de la rama y, si se pasa, pide cerrar el
  paso y un `/clear` (aprobado el 2026-10-27; cambio local del flujo, pendiente de proponerlo a Galivelop-workflow).
- `.claude/hooks/leer-entero.py` (PreToolUse de Read): rechaza leer `docs/plan.md` entero sin `offset`/`limit` y dice
  el `grep` que basta (aprobado el 2026-10-27). Otro documento grande se añade a `GRANDES`.

## Costes conocidos

<!-- Lo que se ha visto que cuesta mucho en este proyecto (archivos grandes leídos enteros, salidas largas...). -->
- Leer enteros los documentos del flujo (`README.es.md`, `docs/es/aplicar.md`, `gw-init/SKILL.md`): 7,5k tokens
  arrastrados 362k (6 % de la sesión). Para aplicar o actualizar el flujo: `aplicar.py --help` o `--check`, o la
  lectura a un subagente.
- `cat` de `CLAUDE.md` o `AGENTS.md`: ya están en el contexto; releerlos costó 151k arrastrados.
- `cat docs/traspaso.md` (9 veces, 80k arrastrados): usar `python3 .claude/gw/scripts/recuperar.py --estado`.
- `cat docs/plan.md` entero al empezar una fase (F0: 3,7k tokens junto con la bitácora, 97k arrastrados): basta
  `grep -n '^| F0' docs/plan.md` y las decisiones que cite (`grep -n '^| D1[25] ' docs/plan.md`).
- Escribir en la sesión principal el contrato de una fase («F1 en detalle»): leer `plan.md`, los esquemas y
  `schema.py` enteros arrastró unos 750k tokens (9 % de la principal en F1). Desde F2 lo escribe un subagente
  (`.claude/gw/orchestrate-dealer.md`).

- Mirar en la sesión principal las imágenes del piloto (F2.0: 25 imágenes, ~1 M arrastrado): el veredicto de estilo o
  composición lo da un subagente Fable que devuelve texto; la persona las ve en las páginas de `examples/pilot/ver.py`
  (aprobado el 2026-10-27).
- Iterar scripts del piloto en la principal (F2.0: `ronda.sh` 24 lecturas y `componer.py` 17, ~200k arrastrados): va
  a un subagente sonnet con su check, como los arreglos de la revisión de `bb7719a` (aprobado el 2026-10-27).

## Ajustes en vigor

- Ventana de compactación automática: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` en `.claude/settings.json`.
- `/clear` entre tareas: al cerrar cada PR y cada fase (F0…F5), con la bitácora escrita y subida (aprobado el
  2026-10-25; el diseño fue un solo tramo de 50 llamadas que llegó a 166k).
- `/clear` también al cerrar cada paso de una fase (F1.x) si la sesión principal pasa de ~120k (aprobado el
  2026-10-25; F1 en un tramo de 38 llamadas llegó a 167k).
- En F2.0, cada ronda del piloto (rN) cuenta como paso: se cierra con la bitácora subida y `/clear` (aprobado el
  2026-10-27).

## Referencias medidas

<!-- Cifras medidas con las que comparar: fecha, sesión, contexto medio, llamadas, total. -->
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
