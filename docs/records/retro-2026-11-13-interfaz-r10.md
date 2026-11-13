# Retro 2026-11-13: revisión de la interfaz con la hoja r10 (`ccr-85e9d14e-zt7p8b` → `main`)

**Estado:** aprobada por la persona el 2026-11-13 y aplicada: T1, T2, R1 y R2 aplicadas; W1 y W2 quedan aquí para
`gw-harvest`.

R2 encontró un solape real (el cuerpo de la ayuda pisaba 4 px su pie, por el margen negativo de la fase 1;
arreglado) y es roja sin el arreglo del editor (`aebaa00`): la ayuda pisa la lista a 360 px y la escena corta la
imagen a 768 px.

Fase 2 de la ida a `main`: `gw-opt-tokens` (desde `2e6b642`) y retro. Solo se aplica lo que la persona confirme.

## gw-opt-tokens (aprobado y aplicado el 2026-11-13)

135 llamadas, 127,6k de media, 3 compactaciones sobre un presupuesto de 2; 28 capturas sueltas, ~2,2 M arrastrados
(13 %). Detalle en `.claude/gw/gw-opt-tokens.md`.

- **T1.** El gancho `intentos-en-hoja.py` avisa también de las capturas `.png` del scratchpad: cada ronda se monta con
  `gimg sheet` (prueba en `tests/test_hooks_sesion.py`, roja sin el cambio).
- **T2.** Cada ronda de revisión visual de la interfaz es un paso: commit, bitácora y `/clear`.

## Candidatos, de más a menos grave

- **R1 · Comprobación (proyecto).** Dos hallazgos de la revisión fueron el mismo fallo: un contorno de foco o de
  comparación con desfase positivo en un elemento con chaflán (`clip-path`), que lo recorta. Hoy lo prueban solo dos
  selectores. Propuesta: en `tests/test_ui.py`, una prueba que recorre las reglas con `clip-path: polygon` y exige que
  su `:focus-visible` (y cualquier `outline` propio) lleve desfase negativo. Mecánico: va a test, no a `REVIEW.md`.
- **R2 · Comprobación (proyecto).** La imagen cortada del editor a ≤1000 px solo se vio con un proyecto real; los
  barridos de desbordes a 360/768/1280 se hicieron a mano con capturas. Propuesta: una prueba de navegador que abre las
  pantallas principales (proyectos, pedidos, pedido, editor, diálogos) a 360, 768 y 1280 px y falla si algún elemento
  sale del ancho de la página o se solapa con su hermano siguiente. Deja las capturas solo para el juicio estético.
- **R3 · Flujo (general).** El presupuesto de compactaciones se pasó (3 de 2) sin que nada lo frenara antes: el aviso
  llega tras compactar. Propuesta al flujo, abajo.

## For Galivelop-workflow

- **W1.** Un gancho PreToolUse de Read que avise, sin bloquear, al leer capturas sueltas del scratchpad y sugiera
  montarlas en una hoja (en este proyecto, `intentos-en-hoja.py`): sirve a cualquier proyecto con interfaz.
- **W2.** Que `recover.py --state` (o el gancho de parada) avise cuando el contexto de un tramo se acerca a la ventana
  y el presupuesto de compactaciones ya está gastado, proponiendo cerrar el paso con `/clear` antes de la siguiente.
