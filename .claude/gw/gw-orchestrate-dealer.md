# orchestrate-dealer — notas del proyecto

Las lee la skill `orchestrate-dealer` antes de repartir. Son de este proyecto; se cambian cuando la persona lo aprueba.

- **El contrato de una fase** («Fx en detalle» y la tabla de pasos de `docs/plan.md`) lo escribe un subagente `opus`
  que lee el plan, los esquemas y el código que haga falta; la sesión principal revisa su diff y lleva a la persona lo
  que sea decisión suya (`grilling`). Así las lecturas largas no se arrastran en la sesión principal.
- **Al cerrar cada paso de una fase** (F1.1, F1.2…), si la sesión principal pasa de ~120k tokens: bitácora al día y
  subida, y se pide a la persona un `/clear` antes del paso siguiente.
- **Tope de 30 llamadas en cada encargo**, escrito en el propio encargo: «si pasas de 30 llamadas sin acabar, para,
  haz un commit `WIP:` en tu worktree y devuelve qué está hecho y qué falta». El siguiente intento sube un peldaño de la
  escalera de `gw-selector` o parte el encargo (aprobado el 2026-11-13: «negative en el pedido» hizo 40 llamadas a
  132k de media, 5,3 M; el 2026-11-12, 80 y 66).
- **Arreglos de una revisión: 4-5 puntos por encargo como máximo**, agrupados por archivo (dos encargos no tocan el
  mismo archivo) y en paralelo con worktree (aprobado el 2026-11-15: 9 puntos en un encargo fueron 47 llamadas, 4,6 M).
- **Un subagente que escribe código** va en worktree (`isolation: "worktree"`) o, si va en la carpeta principal, la
  sesión principal no termina su turno hasta su aviso: el gancho de parada ve el árbol a medias y pide commit
  (una vuelta de ~110k; aprobado el 2026-11-14).
- **Subagentes en paralelo no corren la suite completa**: en su encargo, solo los tests de su módulo
  (`python3 -m unittest tests.test_<mod>`) y el `bash -n` de los ganchos; la suite entera la corre `merge-branch.sh` al
  fusionar, una rama detrás de otra. Un comando largo se espera con un solo `Monitor` con tiempo límite, nunca con
  `sleep` en bucle, y las esperas cuentan para el tope de 30 (aprobado el 2026-11-14: con tres suites a la vez, el
  subagente de `tile` esperó ~40 de sus 76 llamadas, ~3,5 M, y la suite acabó matada).
- **Un arreglo que cambia el contrato** (un código de error, un estado, un campo de la API) se avisa al subagente en
  paralelo que lo usa, o se fusiona antes de que acabe (aprobado el 2026-11-16: `crop.compose_unsupported` llegó
  después de la interfaz de recortar, rompió un test de navegador al unirlas y costó un subagente más).
- **Un módulo con más de ~4 leves, o con leves que tocan librería, CLI e i18n a la vez, va en dos encargos** (aprobado
  el 2026-11-15: `tile` con copias, recuperación, textos traducibles y velocidad en uno hizo 44 llamadas y 4,55 M).
- **Actualizar el flujo (`apply.py --update`) es de un subagente Sonnet**, que devuelve en 10 líneas como mucho los
  conflictos de `AGENTS.md`/`CLAUDE.md` con su texto y las novedades del `CHANGELOG` que tocan al proyecto; la
  principal decide cada conflicto sobre ese texto (aprobado el 2026-11-16: en la principal, `CHANGELOG`, diffs y salida
  de `apply.py` arrastraron ~0,95 M).
- **El tope de 30 llamadas va también en los encargos de arreglos**, copiado en el texto del encargo, no supuesto
  (2026-11-18: «Arreglos 1-3 revisión paso 3» no lo llevaba e hizo 92 llamadas, 5,5 M, en 3 puntos).
- **El encargo que escribe código dice «antes de escribir una función auxiliar, busca con `grep` una que ya lo haga
  en el módulo y en los que importa»** (retro 2026-11-18, P3: código repetido o recalculado fue el leve más repetido de
  0.7.0, ≥8 en 5 revisiones).
