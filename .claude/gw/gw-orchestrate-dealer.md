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
