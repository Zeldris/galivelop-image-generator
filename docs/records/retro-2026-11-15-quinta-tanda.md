# Retro 2026-11-15: quinta tanda de leves de `ccr-85e9d14e-zt7p8b`

**Estado:** aprobada por la persona el 2026-11-15: P1, P2 y P3 aplicadas en `.claude/gw/gw-orchestrate-dealer.md` y
`.claude/gw/gw-opt-tokens.md`; P4 aprobada, queda aquí para `gw-harvest`.

Fase 2 de la ida a `main`, tras la quinta tanda de leves (cinco ramas `agent/L5*`) y su fase 1 (seis medios
arreglados en `0199087` y `700488a`).

## gw-opt-tokens

Desde `2e31af8`: principal 78 llamadas, 10,8 M (139k de media, suelo 102k, techo 160k, 1 compactación); 13
subagentes, 242 llamadas, 22,5 M (arranque medio 65,7k). Total 33,3 M, frente a 14,5 M de la cuarta tanda (tres
ramas). Por subagente: `tile` 44 llamadas y 4,55 M (tope 30), `trace` 35 y 3,37 M, `brand` 28 y 2,63 M, `matte` 28 y
2,48 M, revisión de fase 1 (Opus) 21 y 2,25 M, arreglos de fase 1 20 y 1,65 M. Lo más arrastrado en la principal: el
diff entero de `agent/L5d-tests` (41,6k), la carga de `code-review` (34k) y una salida de `pgrep -af` (17,6k).

## Proyecto

- **P1. Partir los encargos grandes de un módulo**, en `.claude/gw/gw-orchestrate-dealer.md`: un módulo con más de
  ~4 leves, o con leves que tocan librería, CLI e i18n a la vez, va en dos encargos. `tile` (copias, recuperación,
  textos traducibles y velocidad en uno) hizo 44 llamadas; a partir de ~30 cada llamada cuesta más de 100k. Ahorro
  estimado ~1-1,5 M por tanda. Riesgo: un arranque más (~65k) y una fusión más; ninguno de calidad.
- **P2. La principal revisa lo que vuelve con `git diff --stat` y el archivo del revisor**, nunca el diff entero (ya
  lo dice `gw-orchestrate-dealer`; aquí no se cumplió). Se anota en `.claude/gw/gw-opt-tokens.md` como coste
  conocido, junto con `pgrep -a <nombre> | head` en vez de `pgrep -af`. Ahorro: ~60k por llamada arrastrada × las
  llamadas siguientes (~2-3 M en esta sesión). Riesgo: un fallo que solo se ve en el diff; lo cubren el revisor por
  rama y la fase 1.
- **P3. Nueva referencia medida** en `.claude/gw/gw-opt-tokens.md` (la línea de arriba). Sin riesgo.

## Observación

- La revisión por rama no vio dos fallos entre módulos que sí vio la fase 1: `/brand/trace` del servidor no pasaba
  `lang` a `brand.trace` (cambio de firma en `trace`, llamador en `server.py`) y el negro implícito con trazo
  heredado. El encargo del revisor ya pide comparar con los llamadores; falló el revisor, no la regla. Ver P4.

## For Galivelop-workflow

- **P4. Un script lista los llamadores de lo que cambia una rama** (las funciones con `def` tocadas en el diff y sus
  usos con `grep` fuera de los archivos de la rama), y el encargo del revisor de `gw-orchestrate-dealer` le pasa esa
  salida. Convierte en comprobación lo que hoy depende de que el revisor se acuerde. Riesgo: ruido con nombres
  comunes; se filtra por módulo.
