# Retro de `plan-piezas` (fase 2, 2026-11-05)

**Estado:** aprobadas y aplicadas las cuatro propuestas (1-4) por la persona el 2026-11-05; las dos de «For
Galivelop-workflow» quedan para el flujo.

Sesión medida con `gw-opt-tokens` (`measure.py --hours 0`): 25 llamadas, contexto medio 62k (suelo 44k, techo 74k),
sin compactaciones; 2 subagentes (revisión con `opus`, CHANGELOG con `sonnet`), ~29k de arranque cada uno. No hay
gasto grande que recortar; las propuestas vienen sobre todo de errores.

## Propuestas

1. **[proyecto] La bitácora dice que hay filas por rama y `logRows` está apagado.** El párrafo bajo la tabla de
   `docs/handoff.md` («Con `logRows`… el push lo comprueba») hizo gastar 4 llamadas (~26k arrastrados) en descubrir
   que `handoff.py set-row` no funciona y que no hace falta `GW_SHARED_LOG`. Cambio: ese párrafo dice que aquí
   `logRows` está apagado y las filas se editan a mano (o se enciende `logRows`). Riesgo: ninguno.
2. **[proyecto] Test de paridad de los CHANGELOG.** Cada sección `## [x.y.z]` existe en los dos idiomas con el mismo
   número de puntos (`tests/test_releases.py`). Habría avisado de un CHANGELOG traducido a medias. Coste: un test.
   Riesgo: ninguno.
3. **[proyecto] Opciones de `gimg` citadas en la documentación existen.** Un test recorre `CHANGELOG*.md` y
   `README*.md`, saca los `` `gimg <orden> --opción` `` y comprueba que el parser de `gimg/cli.py` los tiene. El
   subagente del CHANGELOG escribió `gimg doctor --project`, que no existe; lo cacé a mano. Coste: un test de ~40
   líneas. Riesgo: falsos positivos con opciones planeadas a propósito (se marcan como tales o se excluyen).
4. **[proyecto] `REVIEW.md`: un PR que cierra una fase trae su entrada en los dos CHANGELOG.** F1 y F2 llegaron a
   `main` sin entrada y las notas de v0.3.0 salieron sin ellas (arreglado y republicado hoy). Es criterio, no
   mecánico: va a `REVIEW.md`. Riesgo: ninguno.

## For Galivelop-workflow

- **`commit-msg` no comprueba que `Siguiente:` esté en el bloque final con las atribuciones** (AGENTS.md, «Mensajes
  de commit»). Los 4 commits anteriores de esta rama lo dejaron en un párrafo aparte. Propuesta: que el gancho lo
  exija, o que la regla diga que basta con que `Siguiente:` sea la última línea antes de las atribuciones.
- **La plantilla de la bitácora escribe el párrafo de `logRows` aunque esté apagado**: escribirlo solo con
  `"logRows": true`, y que `handoff.py close-row` avise (hoy sale con 0 sin escribir nada) igual que `set-row`.
