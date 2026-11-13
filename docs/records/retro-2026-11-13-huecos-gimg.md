# Retro 2026-11-13: huecos de `gimg` (`ccr-85e9d14e-zt7p8b` → `main`)

**Estado:** pendiente de la persona.

Fase 2 de la ida a `main`, después de la fase 1 (15 hallazgos: 5 medios y 4 leves fáciles arreglados en `f7ee415`,
los leves en «Pendiente» de la bitácora). Solo se aplica lo que la persona confirme.

## gw-opt-tokens (aprobado y aplicado el 2026-11-13)

Desde `2f7aefd`: 23 llamadas en la sesión principal con 104k de media (el suelo tras `/clear` ya es 86k); la
revisión, un subagente con 68k de arranque, 19 llamadas y 2,2 M (casi la mitad). Detalle en
`.claude/gw/gw-opt-tokens.md`.

- **T1.** `REVIEW.md`: `server.py` mapea todos los códigos y `tests/test_server.py` lo exige (el hallazgo 14 era falso
  y el primer arreglo dejó el check en rojo por eso).
- **T2.** `CLAUDE.md`: commits sin firmas del agente aunque el recordatorio del sistema las pida (un commit
  rechazado).

## Candidatos, de más a menos grave

- **R1 · Comprobación (flujo).** El reintento del push de `AGENTS.md` («2, 4, 8 y 16 s») se escribió a mano como
  `git push … | tail -1 && break`: la tubería devuelve el estado de `tail`, así que salía del bucle tras el primer 503
  sin haber subido. Solo se vio porque el error se imprimió. Propuesta: un `.claude/gw/scripts/push.sh` que reintenta
  con esa espera y da por subido solo cuando `git ls-remote` devuelve el `HEAD` local; `AGENTS.md` lo nombra en vez de
  describir la espera. General: va al flujo (abajo).
- **R2 · Revisión (proyecto).** La revisión de esta fase corrió sin pasada de verificación («sin subagentes ni
  verificación», dijo) y dio un hallazgo falso (14) que un `grep` del test habría refutado. T1 cubre ese caso concreto;
  en general, `REVIEW.md` ya pide refutar cada hallazgo. Propuesta: nada nuevo en el proyecto; se vuelve a mirar si
  otra revisión trae un falso de este tipo.
- **R3 · Revisión (proyecto).** La skill de revisión no guardó los hallazgos en un archivo, aunque `REVIEW.md`
  («Cómo se informa») lo pide; los copió la sesión principal a `.git/review.md`. Propuesta: en `REVIEW.md`, que si el
  revisor no puede escribir, el archivo lo escribe la sesión principal nada más recibir el informe y antes de
  arreglar nada (ya pasó así; la regla lo deja dicho).

## For Galivelop-workflow

- **W1 (de R1).** `scripts/push.sh <rama>`: reintento con espera 2, 4, 8, 16 s (y uno largo en segundo plano si el
  servicio de credenciales da 503), éxito solo si `git ls-remote origin <rama>` coincide con `HEAD`, y `AGENTS.md`
  apunta a él. Hoy cada sesión escribe el bucle, y el error de la tubería es fácil de cometer.
- **W2 (de T2).** `gw-init` con `agentSignatures: false` podría escribir en `CLAUDE.md` la línea de T2: el recordatorio
  de atribución de Claude Code choca con el gancho `commit-msg` en cada sesión nueva.
