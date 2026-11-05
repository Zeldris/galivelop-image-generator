# orchestrate-dealer — notas del proyecto

Las lee la skill `orchestrate-dealer` antes de repartir. Son de este proyecto; se cambian cuando la persona lo aprueba.

- **El contrato de una fase** («Fx en detalle» y la tabla de pasos de `docs/plan.md`) lo escribe un subagente `opus`
  que lee el plan, los esquemas y el código que haga falta; la sesión principal revisa su diff y lleva a la persona lo
  que sea decisión suya (`grilling`). Así las lecturas largas no se arrastran en la sesión principal.
- **Al cerrar cada paso de una fase** (F1.1, F1.2…), si la sesión principal pasa de ~120k tokens: bitácora al día y
  subida, y se pide a la persona un `/clear` antes del paso siguiente.
