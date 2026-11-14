# Retro 2026-11-14: cuarta tanda de leves de `ccr-85e9d14e-zt7p8b`

**Estado:** decidida por la persona el 2026-11-14: P1 aprobada y aplicada; P2 aprobada, queda aquí para `gw-harvest`;
P3 rechazada.

Fase 2 de la ida a `main`, tras la cuarta tanda de leves (cinco ramas) y la fase 1 (8 hallazgos; los tres medios y
cuatro baratos arreglados en `19f00ce`, `1fd4fb6` y `6201952`).

## gw-opt-tokens

Desde `2c608ed`, sesión `ec96ac04`: principal 30 llamadas, 3,4 M (114k de media, techo 150k); revisión Opus 10
llamadas, 0,94 M; 3 subagentes Sonnet 115 llamadas, 10,2 M. Total 14,5 M, unas tres veces las dos idas anteriores
(3,7 M y 5,5 M). El subagente de `tile` hizo 76 llamadas (tope 30) y 7,1 M: ~40 fueron esperar la suite completa
(19 `Monitor` con `sleep` de hasta 600 s, 9 `Read` del log), con tres suites corriendo a la vez en tres worktrees; una
pasada de ~4 min pasó de 40 min y acabó matada. El check que valió fue el de `merge-branch.sh`.

## Proyecto

- **P1. Subagentes en paralelo sin la suite completa** (aplicada en `.claude/gw/gw-orchestrate-dealer.md`): solo los
  tests de su módulo y el `bash -n` de los ganchos; la suite entera en `merge-branch.sh`, en serie; esperas con un
  `Monitor` con tiempo límite, contadas en el tope de 30. Riesgo: un arreglo que rompe otro módulo se ve al fusionar;
  `merge-branch.sh` lo para y cuesta un reencargo.
- **P3. Subir antes de cerrar un turno con subagentes en marcha** (6 vueltas del gancho de parada, ~0,7 M; 3 de ellas
  el aviso «Unverified», inevitable): rechazada.

## Observación

- Un leve dice que el test de limpieza del gancho pasa también sin el arreglo: `red-without-fix.sh` no lo cazó en el
  encargo. Convertirlo en comprobación tocaría `merge-branch.sh` (del flujo); sin propuesta por ahora.

## For Galivelop-workflow

- **P2. La plantilla de encargo de `gw-orchestrate-dealer` dice que los subagentes en paralelo no corren la suite
  completa** (solo los tests de su módulo; la suite, en `merge-branch.sh`) y que un comando largo se espera con un
  `Monitor` con tiempo límite, nunca con `sleep` en bucle, dentro del tope de llamadas. Medido aquí: ~3,5 M de 14,5 M
  en esperas de un solo subagente.
