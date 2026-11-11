# Retro — `claude/marca-r9` (hoja r9 aplicada), 2026-11-11

**Estado:** aprobada entera por la persona (2026-11-11). Aplicadas en `claude/marca-r9`: P1 (`tests/test_changelog.py`), P2
(`docs/records/leves-claude-marca-r9.md`, nota en `.claude/gw/gw-opt-tokens.md`), P3 (filas fusionadas fuera de la tabla) y P4
(`<title>` de los símbolos y su test). W1 y W2 van al flujo.

Sesión: hoja r9 de Galivelop IG aplicada a la interfaz (tokens, claro por defecto, fuentes), a los logos y al nombre
visible (D38), en dos ramas de subagente (`agent/r9a-tokens`, `agent/r9b-logos`) y commits de documentación. La fase 1
dio 10 hallazgos: 4 medios arreglados en `6eb6b3b` y 6 leves en la bitácora. Medida de `gw-opt-tokens` tras el último
`/clear`: 15 llamadas a 106k de media en la principal (suelo de 89k nada más empezar), sin compactaciones; dos
subagentes con 68k de arranque cada uno. Antes del `/clear` la rama llevaba 5 compactaciones con presupuesto de 3; la
ventana ya se subió a 200000 por decisión de la persona (`f25fa87`).

## Candidatos, de más a menos grave

**P1. CHANGELOG vacío con cambios visibles (proyecto, comprobación automática).** La rama cambió el tema por defecto,
las fuentes, el logo y el nombre visible, y «[Sin publicar]» seguía vacío en los dos CHANGELOG hasta que lo vio la
revisión. `REVIEW.md` ya lo pide; es mecánico. Propuesta: un test (`tests/test_changelog.py`) que falle si el diff
contra `origin/main` toca `gimg/` (fuera de tests) y «[Sin publicar]» / «[Unreleased]» no tienen ninguna entrada; se
salta si no hay `origin/main` o si la rama es la de una release recién etiquetada. Riesgo: un cambio interno sin
efecto visible obligaría a escribir una línea; se acepta («Interno: …») o se añade una marca para saltarlo.

**P2. Los leves, a su archivo desde la fase 1 (proyecto, bitácora).** La fila de `claude/marca-r9` tiene 1672
caracteres (límite 800, aviso del `pre-commit`) porque lleva los 10 leves. La regla aprobada el 2026-11-06 los mueve a
`docs/records/leves-<rama>.md` «al fusionar»; hasta entonces el gancho de inicio los reimprime en cada sesión.
Propuesta: los leves se escriben en `docs/records/leves-<rama>.md` nada más cerrar la fase 1 y la fila lleva solo el
puntero. Se aplica ya a esta rama (`docs/records/leves-claude-marca-r9.md`).

**P3. Filas de ramas ya fusionadas en la tabla de estado (proyecto, gasto).** La tabla conserva `f2-motor`,
`plan-piezas` y `release-install`, fusionadas el 2026-11-05. El gancho de inicio las imprime en cada sesión y tras cada
compactación (unos 400 tokens fijos, arrastrados en todas las llamadas). Propuesta: pasan a «Hecho» en una línea cada
una y se borran de la tabla; al fusionar una rama, su fila se va en el mismo commit que apunta la fusión. Riesgo:
ninguno, el dato sigue en «Hecho».

**P4. El `<title>` de los símbolos y el contrato de los logos (proyecto, comprobación automática).** El símbolo y el
favicon siguen diciendo «galivelop-image-generator: rejilla de intentos» con D38 dada por aplicada, y
`test_contract` solo exige un título no vacío. Propuesta: el test exige que el `<title>` de los SVG de marca empiece
por el nombre visible de la hoja («Galivelop IG»), y se corrigen los dos títulos. Es uno de los leves; se propone
porque el arreglo y su comprobación son dos líneas.

## Para Galivelop-workflow

**W1. El gancho de parada no ve un push en marcha.** Con el `git push` lanzado en segundo plano y el `pre-push`
pasando el check (aquí tarda más de 3 minutos), el gancho de parada bloqueó tres veces con «1 commit sin subir»; cada
vuelta cuesta el contexto entero (~105k). Propuesta: el `pre-push` deja una marca (`$(git rev-parse --git-dir)/push.lock`
con su PID) mientras corre, y el gancho de parada no bloquea si esa marca existe y su proceso vive.

**W2. Arreglos en serie sobre la rama de trabajo: quién sube.** La plantilla de `gw-orchestrate-dealer` dice al
subagente que suba; la regla de los worktrees en paralelo dice que no. El encargo de esta sesión (un subagente, en
serie, en la rama de trabajo) llevó «sin push» y el commit quedó en local con la principal parada. Propuesta: la
plantilla lo dice en una línea propia: «en la rama de trabajo, subes tú; en un worktree, no».

## Sin propuesta

- `gw-selector`, `/code-review` y `gw-orchestrate-dealer` hicieron su trabajo: la revisión encontró la espera sin
  límite de `_single_worker`, que ningún test cubría, y el arreglo llegó con su test en rojo sin él.
- El suelo de 89k tras un `/clear` es casi todo contexto fijo del entorno (herramientas y skills), no del proyecto.
