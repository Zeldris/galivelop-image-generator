# Retro 2026-11-16: barrido B de `crop-editor.js` (rama `ccr-85e9d14e-zt7p8b`)

**Estado:** pendiente de la decisión de la persona.

Alcance: desde `98fcc7c` (versión 0.6.0) hasta `eede8d5`: comprobar la release v0.6.0, barrido B (`4c297c1`), fase 1
(5 leves arreglados en `6398948`, `Findings: 5`) y CHANGELOG.

## Medida (`gw-opt-tokens`, `measure.py --since 98fcc7c`)

- Principal: 53 llamadas, 6,4 M de entrada (121k de media, techo 144k, 0 compactaciones). El arranque tras `/clear`
  es de ~92k, y ~78k de eso son el sistema y las herramientas MCP.
- Subagentes: 4, con 74 llamadas y 3,1 M. Arrancan con 15-21k, frente a los 66-69k de antes con `general-purpose`: los
  tipos `gw-worker`/`gw-reviewer` funcionan. El barrido usó 47 llamadas y 2,1 M; sus arreglos, 12 llamadas y 0,4 M.
  La revisión con Opus usó 7 llamadas y 0,25 M.
- Total: 127 llamadas y 9,6 M.

## Propuestas, de más a menos importante

**P1. Comprobar la tabla de la bitácora (flujo).** Al editar `docs/handoff.md` con un script calculé el índice antes de
otra sustitución. Una fila quedó pegada a otra y se perdió la de `claude/marca-r9`. Ningún check lo vio: lo encontró
la revisión de código por casualidad, fuera de su alcance. Propuesta: `handoff.py` (o el `pre-commit`) rechaza una
tabla de estado cuyas filas no tengan exactamente dos celdas o que pierda una fila `Tarea en curso` respecto a `HEAD`
sin que la rama se haya cerrado. Riesgo: ninguno; un falso positivo se ve enseguida.

**P2. El registro de tokens dispara el gancho de parada (flujo).** `docs/metrics/ledger.jsonl` se escribe al cerrar
cada turno. El gancho de parada de la nube ve el árbol sucio y pide subirlo, lo que costó 4 turnos extra (~0,5 M, el
8 % de la principal). No es la regla de «subir antes de cerrar el turno» que se rechazó el 2026-11-14: propuesta,
escribir en un archivo ignorado por git (`ledger.spool.jsonl`) y que `metrics.commitLedger` lo vuelque en el
`pre-commit`, como ya hace con el registro. Riesgo: si el contenedor muere sin un commit, se pierden las líneas de ese
tramo. Hoy pasa lo mismo si no se sube.

**P3. `releases.py check` no funciona en la nube (proyecto).** Usa GraphQL a través de `gh`, que la nube rechaza con
un 403. Tuve que pedir la release con la herramienta MCP, que devolvió el cuerpo entero (1,8k tokens, 64k arrastrados).
Propuesta: que `releases.py` consulte la API REST (`gh api repos/<o>/<r>/releases/tags/<tag>`) y la etiqueta con
`git ls-remote --tags`, y que devuelva una línea. Riesgo: ninguno, con un test del análisis de la respuesta.

**P4. Encargos del dealer: el mismo defecto en el archivo hermano (flujo, `gw-orchestrate-dealer`).** El barrido dejó
el leve 1 a medias, aunque el registro lo daba por hecho. Además, no vio que el error duplicado también estaba en
`layout-editor.js`, aunque tocó ese archivo. Lo pescó la fase 1, y costó un segundo subagente. Propuesta: la plantilla
del encargo añade «si el mismo defecto está en otro archivo que tocas, arréglalo también o dilo» y «devuelve, por
cada punto, si lo hiciste entero o en parte». Riesgo: encargos algo más largos.

**P5. Barrido de `gimg/brand.py` para 0.7.0 (proyecto).** Es el script con más leves abiertos (4): `_paint_colors`
cuenta el `stroke` de un `<g>` que pisan todos sus hijos; `_check_weight_spacing` acepta `True` como peso; `matte`
calcula `border_color` dos veces; un `fill` explícito en `<line>` cuenta como color. Va con
`docs/records/leves-ccr-85e9d14e-zt7p8b.md` y «Pendiente». No hay id `B`, porque `plan` está vacío en
`.claude/gw.json`. Le sigue `orders.add_derived`, con 2.

Ya conocido, no se repite: el suelo de ~78k del sistema y los conectores (la persona no lo cambia de momento); quitar
un conector que no se use aquí, como Claude Docs, lo bajaría en cada llamada.

## For Galivelop-workflow

- P1: comprobación de la tabla de estado en `handoff.py`/`pre-commit`.
- P2: registro de tokens en un archivo ignorado y volcado en el `pre-commit`.
- P4: dos líneas en la plantilla del encargo de `gw-orchestrate-dealer`.
