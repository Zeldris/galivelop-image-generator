# Retro 2026-11-14: segunda ida a `main` de `ccr-85e9d14e-zt7p8b` (leves de la fase 1)

**Estado:** aprobada por la persona el 2026-11-14 y aplicada: R1 y R2 aplicadas; W1 y W2 quedan aquí para
`gw-harvest`.

Fase 2 de la ida a `main`, tras la fase 1 (11 hallazgos: 5 medios arreglados en `6266700`, `089689b` y `8fd2b39`; los
leves en «Pendiente» de la bitácora) y `gw-opt-tokens` (sus tres propuestas aprobadas y aplicadas en `eaf2c23`).

## gw-opt-tokens

Desde `d2913d1`, sesión `66f16e48`: principal 21 llamadas, 2,2 M (106k de media); revisión Opus 0,9 M; arreglos
Sonnet 2,4 M. Aplicado: subagente que escribe código en worktree o la principal espera su aviso; `CLAUDE.md` ignora el
gancho «Unverified»; la medición, en «Referencias medidas».

## Proyecto

- **R1. Un valor por defecto que cambia se busca en la documentación** (`REVIEW.md`, «Un dato, un sitio»): el defecto
  de `spacing` pasó de 0,01 a «según la familia» y `docs/api.md`/`docs/en/api.md` siguieron diciendo 0,01; lo cazó la
  revisión, no el que hizo el cambio. Regla de criterio: «al cambiar un valor por defecto, `grep` del valor viejo en
  `docs/` y los README en el mismo commit». Es criterio porque el valor viejo (0.01) aparece también en usos legítimos
  (ejemplos con `--spacing 0.01`).
- **R2. Test en el navegador del espaciado vacío** (`tests/test_ui_browser.py`, clase `BrandShop`): el subagente dijo
  que no había arnés de JS para el taller y dejó M1 sin test, pero `BrandShop` existe (l.673). Un test que intercepte
  `api.brandWordmark` y compruebe que el cuerpo no lleva `spacing` con el campo vacío y sí con un valor. Y, en el
  docstring de `BrandShop`, que es el sitio de los tests del formulario del taller.

## Para Galivelop-workflow

- **W1. `gw-orchestrate-dealer`: no terminar el turno con un subagente escribiendo en la carpeta principal.** El
  gancho de parada ve el árbol a medias y pide commit; la nota del proyecto lo dice ya, la skill no. Propuesta: en la
  skill, «un subagente que escribe código va en worktree; si no, la principal espera su aviso sin cerrar el turno».
- **W2. Encargo de arreglos con la ruta de los tests de cada capa.** El subagente no encontró los tests de la
  interfaz; la plantilla de encargo de `gw-orchestrate-dealer` podría pedir «dónde viven los tests de lo que tocas»
  (aquí, `tests/test_ui_browser.py` para la interfaz).
