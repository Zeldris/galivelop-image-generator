# Retro 2026-11-14: tercera ida a `main` de `ccr-85e9d14e-zt7p8b` (gancho de hojas y fase 1)

**Estado:** pendiente de la persona.

Fase 2 de la ida a `main`, tras el arreglo del gancho de hojas (`87feeb8`), la fase 1 (14 hallazgos, SHIP WITH FIXES:
2 medios arreglados en `34f6031`; los leves en «Pendiente» de la bitácora) y `gw-opt-tokens` (aprobado y aplicado en
`e6755b8`).

## gw-opt-tokens

Desde `1c178d3`, sesión `79c75ecd`: principal 27 llamadas, 2,76 M (102k de media); revisión Opus 10 llamadas, 0,9 M.
Total 3,7 M (la pasada anterior, 5,5 M). Aplicado: el check largo en primer plano con 6 min, o en segundo plano sin
cerrar el turno.

## Proyecto

- **R1. `trace` no devuelve un SVG vacío sin decirlo** (`gimg/trace.py`, `to_svg`): el arreglo de la fase 1 tapa un
  caso, pero cualquier otra combinación (`ink` explícito sobre colores que el suavizado borra, `min_island` alto) puede
  seguir dando un `<svg>` sin trazos. Propuesta: si no queda ningún trazo, `ValueError` con el motivo («no ink left:
  pass ink or --mode color»), y un test. Riesgo: un uso que hoy acepta un SVG vacío pasa a fallar (no hay ninguno en los
  tests ni en `examples/`).

## Para Galivelop-workflow

- **W1. La revisión de la fase 1 recibe los leves ya apuntados.** El revisor volvió a informar de 3 leves que ya estaban
  en «Pendiente» (`_publish` no atómico, `_thin`, el negro implícito de `brand`): trabajo y tokens repetidos. Propuesta:
  la fase 1 de `AGENTS.md` (o la skill de revisión) pasa al revisor la sección «Pendiente» de la bitácora con «no
  informes de lo que ya está aquí».
- **W2. El gancho de parada con un check en segundo plano.** El gancho pide commit mientras `check.sh` corre en segundo
  plano, y la sesión vuelve dos veces a esperar (~0,5 M). Propuesta: `check.sh` escribe un testigo mientras corre y el
  gancho de parada, si lo ve, dice «el check sigue corriendo: espera su aviso» en vez de pedir commit.
