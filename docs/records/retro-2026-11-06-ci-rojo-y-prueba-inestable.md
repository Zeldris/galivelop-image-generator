# Retro especial: CI rojo desde UI.6 y prueba inestable de autoarranque (2026-11-06)

**Estado:** aprobada por la persona el 2026-11-06: P1 aplicada en el proyecto (`.claude/gw/diagnosing-bugs.md` y regla en `REVIEW.md`) y llevada al flujo; P2-P5 aprobadas y llevadas al flujo (sección «For Galivelop-workflow»).

Pedida por la persona para sacar un patrón de diagnóstico. Episodio, en `f4e-piezas`:

- **CI rojo solo en Chrome** (runs 42209486876 … 42227649792) en el editor a 360. Tres causas sucesivas, dos de
  ellas hipótesis falsas que llegaron a arreglarse:
  - `100vw` con barra clásica (cierto: `707007f`);
  - escala por `clientWidth` entero (`68fbe00`): arregló un desfase de Firefox, no el de Chrome;
  - «Chrome ajusta la altura de la imagen» (falsa, descartada midiendo).
  La causa real, medida en Chrome con una rama de diagnóstico, era CSS: el escenario se encogía en una columna
  (`f4cd0be`), y también en Firefox, sin una prueba que lo viera. CI verde en `472dcfc` (run 42230776540).
- **Prueba inestable de autoarranque** (1 de cada ~15 pasadas, solo en el check largo). El mensaje de diagnóstico
  (`ca6cea2`: estado, pids, versiones, stderr de cada CLI) descartó la hipótesis (b) en el primer fallo siguiente y
  señaló la real: sondeos `LOCK_EX|LOCK_NB` que chocaban entre sí (`ec89eb0`, 40/40 en verde).
- **Tropiezos de herramientas:**
  - un `pkill -f` que se mató a sí mismo y canceló un commit;
  - worktrees de subagentes que arrancan en `71a69a3`;
  - un revisor que cambió de rama el checkout principal mientras corría un `pre-push`;
  - el check completo (~5 min) repetido en `merge-branch.sh` y en el `pre-push`.

## Candidatos, de más a menos grave

### P1 · Patrón: medir antes de arreglar (lo que más interesa a la persona) — flujo + proyecto

En los dos casos, lo que funcionó fue lo mismo: **primero una medida que decide entre las hipótesis, y el arreglo
solo cuando ella decide**. Lo que falló, también: dos arreglos sobre una hipótesis sin medir (`68fbe00` y la escala por
eje), que costaron dos rondas de CI. `diagnosing-bugs` pide un bucle rojo rápido, pero no dice qué hacer cuando el
fallo solo se da en un sitio caro: 1 de cada 15 en un check de 5 minutos, o solo en el CI.

Propuesta: una sección «Fallo caro de reproducir» en `diagnosing-bugs`, con estos pasos:

1. **Prueba inestable:** antes de arreglar, el mensaje de fallo de la prueba recoge la evidencia que separa las
   hipótesis (estado, pids, versiones, stderr de cada proceso). Se sube así y se espera el siguiente fallo natural.
   Se arregla cuando ese mensaje decide la causa.
2. **Fallo solo en el CI o en otro navegador:** una rama de diagnóstico que mide en ese entorno (rectángulos,
   tamaños, valores intermedios en el mensaje) y se empuja para que la corra el CI; el arreglo va después, en la
   misma rama.
3. **El commit del arreglo cita la salida que decidió la causa**, y nombra las hipótesis descartadas.

Destino: la sección es **general** y va a Galivelop-workflow. Mientras llega, el proyecto la copia en
`.claude/gw/diagnosing-bugs.md`, que la skill ya lee si existe. El punto 3 va además a `REVIEW.md`, como criterio
para el revisor: un arreglo de prueba inestable o de fallo solo en el CI sin evidencia citada es un hallazgo medio.

### P2 · Comprobación: lanzar en el CI solo las pruebas de una rama de diagnóstico — flujo

Cada medición en Chrome costó una ronda completa de CI (~5 min) y esperarla. Propuesta: `check.yml` con
`workflow_dispatch` y una entrada opcional `tests`, para correr solo esas pruebas con
`gh workflow run check.yml -f tests=…`. Así se mide en el CI en ~1 min. `check.yml` lo copia el flujo, así que es
**general** y no se parchea aquí.

### P3 · Reparto a subagentes: worktree en el commit de la rama, revisor sin `checkout` — flujo

- Los worktrees con `isolation: "worktree"` arrancan en un commit viejo (`71a69a3`). La plantilla de
  `gw-orchestrate-dealer` compara con `origin/<branch>` y hace `reset --hard`, que no vale para una rama
  `worktree-agent-*`. Se lo dije a mano en cada encargo. Propuesta: en worktree, la plantilla pide
  `git merge --ff-only <commit de la rama de trabajo>` y comprobar `git log -1`.
- El revisor que cambió de rama el checkout principal hizo fallar un `pre-push` y confundió el diagnóstico de la
  prueba inestable. Propuesta: el encargo del revisor (paso 3 de la skill) dice que lea con
  `git diff`/`git show <commit>:<ruta>` y que, si necesita ejecutar, lo haga en su propio worktree.

Las dos son **generales**: cambian `gw-orchestrate-dealer` en el flujo.

### P4 · Comprobación: `pkill -f`/`pgrep -f` en las órdenes del propio agente — flujo

`REVIEW.md` ya lo prohíbe en el código, pero el tropiezo fue en una orden mía de Bash: el patrón iba en la línea y
casó consigo mismo. Propuesta: un gancho `PreToolUse` sobre Bash que avise cuando una orden lleva
`pkill -f`/`pgrep -f` y propone la alternativa: `TaskStop`, un pid guardado o `pgrep -x`. Es **general** (gancho en
`.claude/settings.json` y un script del flujo), y aquí no se toca sin tu permiso.

### P5 · Economía: `merge-branch.sh` apunta el árbol verde como `check.sh` — flujo, leve

`merge-branch.sh` corre el check completo, pero no lo apunta. Si se sube justo después de fusionar, el `pre-push` lo
repite (~5 min). Propuesta: que lo apunte con el mismo mecanismo de `check.sh`. Es **general** (script del flujo).

## Lo que funcionó

- El mensaje de diagnóstico de la prueba inestable: un solo fallo natural descartó (b) y señaló la causa real.
- Medir en Chrome con una rama propia empujada al CI: encontró un fallo de CSS que nadie sospechaba, y que también
  tenía Firefox.
- `red-without-fix.sh` en las pruebas nuevas, y 40 pasadas seguidas para dar por cerrada la prueba inestable.

## For Galivelop-workflow

- P1: sección «Fallo caro de reproducir» en `diagnosing-bugs` (mensaje de diagnóstico primero, rama de medida en el
  CI, el commit cita la evidencia).
- P2: `check.yml` con `workflow_dispatch` y entrada `tests`.
- P3: en `gw-orchestrate-dealer`, worktree con `merge --ff-only` al commit de la rama, y revisor sin `checkout`.
- P4: gancho `PreToolUse` que avisa de `pkill -f`/`pgrep -f` en las órdenes del agente.
- P5: `merge-branch.sh` apunta el árbol verde, como `check.sh`.
