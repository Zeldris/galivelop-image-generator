<!-- galivelop-workflow v0.4.0 -->
# opt-tokens — notas del proyecto

Las lee la skill `opt-tokens` antes de proponer nada, y se actualizan cuando la persona aprueba un cambio. El flujo
las crea una vez; desde entonces son del proyecto.

## Herramientas que ya ahorran

<!-- Una línea cada una, con cómo se corre. -->
- `python3 .claude/gw/scripts/recuperar.py --estado` y `--buscar "<texto>"`: recuperar lo que se llevó una
  compactación.
- `orchestrate-dealer`: el trabajo de más de un paso, repartido a subagentes de contexto limpio.

## Costes conocidos

<!-- Lo que se ha visto que cuesta mucho en este proyecto (archivos grandes leídos enteros, salidas largas...). -->
- Leer enteros los documentos del flujo (`README.es.md`, `docs/es/aplicar.md`, `gw-init/SKILL.md`): 7,5k tokens
  arrastrados 362k (6 % de la sesión). Para aplicar o actualizar el flujo: `aplicar.py --help` o `--check`, o la
  lectura a un subagente.
- `cat` de `CLAUDE.md` o `AGENTS.md`: ya están en el contexto; releerlos costó 151k arrastrados.
- `cat docs/traspaso.md` (9 veces, 80k arrastrados): usar `python3 .claude/gw/scripts/recuperar.py --estado`.

## Ajustes en vigor

- Ventana de compactación automática: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` en `.claude/settings.json`.
- `/clear` entre tareas: al cerrar cada PR y cada fase (F0…F5), con la bitácora escrita y subida (aprobado el
  2026-10-25; el diseño fue un solo tramo de 50 llamadas que llegó a 166k).

## Referencias medidas

<!-- Cifras medidas con las que comparar: fecha, sesión, contexto medio, llamadas, total. -->
- 2026-10-25, sesión `a0f496d5` (aplicar el flujo y diseño D1-D26): 50 llamadas, contexto medio 113k (suelo 38k,
  techo 166k), 5,6 M de entrada en la principal + 0,9 M en subagentes.
