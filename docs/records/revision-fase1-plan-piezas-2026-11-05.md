# Revisión de fase 1 de `plan-piezas` (diff `origin/main...HEAD`, 2026-11-05)

`/code-review --max-findings all`: 9 hallazgos, ninguno grave. Los medios se arreglan en la rama (los de `releases.py` con
tests, rojos sin el arreglo según `red-without-fix.sh`); los leves quedan como pendientes y no se revisan más en este PR.

**Medio**
1. `releases.py` `check`: leía la versión de la referencia local `origin/main` sin traerla; tras fusionar un PR en GitHub
   daba por buena la versión anterior. **Hecho:** si la referencia es `origin/<rama>`, primero `git fetch origin <rama>`.
   Test: `tests.test_releases.CheckTests.test_fetches_the_remote_branch_before_reading_the_version`.
2. `releases.py` `check`: cualquier error de `gh` con «not found» (repositorio, permisos, 404) contaba como «falta la
   release» (salida 1). **Hecho:** solo el mensaje exacto de `gh`, «release not found», es falta; lo demás, 2.
   Test: `test_repo_not_found_is_unknown_not_missing`.
3. `CHANGELOG.md`/`CHANGELOG.es.md`: F1 y F2 no estaban en ninguna sección, así que las notas de v0.3.0 solo traían F3.
   **Hecho:** F1 y F2 añadidas a `[0.3.0]`. Queda actualizar las notas de la release v0.3.0 ya publicada en GitHub
   (con la confirmación de la persona).
4. `CHANGELOG` `[0.4.0]` no nombraba `releases.py`. **Hecho.**
5. `docs/handoff.md`: las filas comunes y la de `f2-motor` seguían en F2 y en «PR de `f2-motor`». **Hecho:** al día, y
   `f2-motor` cerrada.
6. `releases.py`: la orden sugerida escribía `notas.md` en la raíz del repo, sin ignorar. **Hecho:** se pasa por tubería
   (`--notes-file -`). El test lo comprueba en `test_missing_tag_and_release_say_how_to_make_them`.

**Leve**
7. `releases.py` `main`: `check --ref --ref` llegaba a `git show`. **Hecho** de paso (barato): un `--ref` que empieza por
   `-` muestra el uso. Test: `test_check_rejects_an_option_as_ref`.
8. `docs/plan.md` ~95: el párrafo de la MIT pasa del ancho de ~120 columnas. Pendiente.
9. Mensajes de commit de la rama: `Siguiente:` va en un párrafo aparte de `Co-Authored-By`, no en el mismo bloque final
   (AGENTS.md, «Mensajes de commit»). Los ya subidos no se reescriben; los nuevos lo cumplen.
