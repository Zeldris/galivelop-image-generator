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
- **Un subagente que escribe código** va en worktree (`isolation: "worktree"`) o, si va en la carpeta principal, la
  sesión principal no termina su turno hasta su aviso: el gancho de parada ve el árbol a medias y pide commit
  (una vuelta de ~110k; aprobado el 2026-11-14).
- **Subagentes en paralelo no corren la suite completa**: en su encargo, solo los tests de su módulo
  (`python3 -m unittest tests.test_<mod>`) y el `bash -n` de los ganchos; la suite entera la corre `merge-branch.sh` al
  fusionar, una rama detrás de otra. Un comando largo se espera con un solo `Monitor` con tiempo límite, nunca con
  `sleep` en bucle, y las esperas cuentan para el tope de 30 (aprobado el 2026-11-14: con tres suites a la vez, el
  subagente de `tile` esperó ~40 de sus 76 llamadas, ~3,5 M, y la suite acabó matada).
