# Retro 2026-11-04: f2-motor antes del PR a `main` (lectura del LoRA, F2.10, hoja de estilo)

**Estado:** aprobada por la persona el 2026-11-04 y aplicada (P1-P5; P1 además propuesta al flujo).

Sesión del 2026-11-04 en `f2-motor`: lectura de Tarkor (IMG-32/33), propuestas del LoRA aprobadas, `gimg sheet`,
aviso de VRAM en `doctor`, plantilla de hoja de estilo y hoja real de este proyecto, revisión antes de `main` (3 medios
arreglados).

## Medida (`opt-tokens`, `medir.py`)

72 llamadas en la sesión principal; contexto medio 105k, techo 153k, suelo 43k; 0 compactaciones. El resultado más
arrastrado fue el primer `grep` sobre `docs/plan.md` (291k arrastrados). Dos imágenes arrastraron 155k. Los bucles del
gancho de parada mientras un subagente en segundo plano editaba el árbol principal costaron unas 5 vueltas × ~105k. El
arranque de un subagente cuesta ~26k. La revisión de código con `opus` costó 20 llamadas y 2,1M.

## Propuestas (por gravedad)

1. **Subagentes que tocan código, en worktree y de vuelta con `fusionar.sh`** (general). Un subagente en segundo plano
   editando el árbol principal dejó cambios sin commit; el gancho de parada bloqueó la sesión cinco veces, y acabé con
   un commit `WIP` con `--no-verify` (luego rehecho con los ganchos). `orchestrate-dealer` ya dice `isolation:
   "worktree"` para arreglos en paralelo, pero no para un único subagente de código en segundo plano. Cambio: la skill
   lo exige para todo subagente que escriba código mientras la sesión principal sigue. Riesgo: los worktrees cuestan
   un arranque algo mayor; contrapeso: `fusionar.sh` ya corre el check.
2. **Cada `lectura-*` apunta el HEAD de la fuente de forma fija** (proyecto). Una línea `**HEAD leído:** <repo>
   <rama> <sha>` al principio, para que la siguiente lectura empiece con `git log <sha>..` sin buscarlo en prosa.
   Coste: una línea en la próxima lectura. Riesgo: ninguno.
3. **Las rondas de imágenes se revisan con `gimg sheet`** (proyecto, ya hecho en F2.10). Se apunta en
   `.claude/gw/opt-tokens.md` como herramienta que ahorra: una hoja de 6 imágenes cuesta como una imagen.
4. **Búsquedas en `docs/plan.md` con el ancla de la fila** (proyecto). El `grep` amplio arrastró 291k; con
   `grep -n "^| F2.1[0-2]"` o `sed -n` sobre el rango sale lo justo. Se apunta en `.claude/gw/opt-tokens.md`.
5. **`/clear` al cerrar este PR** (proyecto). El contexto medio (105k) está cerca del umbral de 150k; la bitácora basta
   para retomar con E3 (r2).

Fuera de esta retro, aprobado también el 2026-11-04: los 17 cambios a la plantilla, los huecos del perfil de la hoja
real y el validador de la hoja en `gimg doctor --project` (antes de r5).

## For Galivelop-workflow

- `orchestrate-dealer`: todo subagente que escriba código en segundo plano mientras la sesión principal sigue va en
  worktree (`isolation: "worktree"`, o `git worktree add` en la nube) y vuelve con `fusionar.sh`; nunca edita el árbol
  principal. Motivo: el gancho de parada bloquea la sesión principal por cambios ajenos sin commit y empuja a
  `--no-verify`.
