# Retro 2026-11-13: release 0.5.0, leves sin equipo y prompt negativo (`ccr-85e9d14e-zt7p8b` → `main`)

**Estado:** aprobada por la persona el 2026-11-13 y aplicada: gw-opt-tokens 1 y 2 aplicadas, 3 rechazada por ahora
(el suelo fijo del entorno no se toca), 4 pasa al flujo como W2; R1 y R2 aplicadas; W1-W4 quedan aquí para
`gw-harvest`.

Fase 2 de la ida a `main`, después de la fase 1 (10 hallazgos, 9 arreglados en `da2f525`, el leve en
`docs/records/leves-ccr-85e9d14e-zt7p8b.md`) y de los ganchos de autor (`796a290`).

## gw-opt-tokens

Desde `529468b`, sesiones `0cacc78c` y `6e5628a7`: principal 123 llamadas, ~15 M (126k y 117k de media, techos
162/149k, sin compactaciones); 4 subagentes, 113 llamadas, ~12,3 M, arranque 66-69k. Suelo tras `/clear`: 85-88k
(38-45k en octubre), casi todo herramientas y conectores del entorno.

1. **Tope de 30 llamadas en el encargo de cada subagente** (`.claude/gw/gw-orchestrate-dealer.md`): «negative en el
   pedido» hizo 40 llamadas a 132k de media (5,3 M). Aplicada.
2. **`/clear` entre dos tareas de la misma sesión y tras más de 1 h de pausa** (`.claude/gw/gw-opt-tokens.md`):
   `0cacc78c` encadenó la release y los leves, 70 llamadas a 126k frente a un suelo de 88k, ~1,9 M. Aplicada como regla,
   sin gancho.
3. **Bajar el suelo fijo** desactivando conectores sin uso en el entorno: rechazada por ahora.
4. **Filtrar la salida del check al empezar**: es de `AGENTS.md` (archivo del flujo), pasa a W2.

## Proyecto

- **R1. Paridad `README.md` ↔ `README.en.md`** (`tests/test_readme_parity.py`): la fase 1 encontró `README.en.md` sin
  el campo `prompt` del pedido; `tests/test_doc_options.py` solo mira que lo documentado exista en el parser. El test
  compara las opciones `--x` en código y los campos en viñeta `` - `campo`: `` de los dos README. Aplicada.
- **R2. Prueba en la Deck de `--negative-prompt`** a `docs/plan.md` («Riesgos y no confirmado», manual Deck): estaba
  solo en la fila de la bitácora. Aplicada.

## Para Galivelop-workflow

- **W1. `red-without-fix.sh` sin `git stash`.** El stash es común a todos los worktrees: el 2026-11-13 dos subagentes
  recogieron cada uno el stash del otro (segunda vez; recuperado, nada perdido). Propuesta: quitar el arreglo en una
  copia temporal o un `git worktree` propio, o `--fix-at HEAD` por omisión.
- **W2. Check de «Al empezar» con la salida filtrada** (`… 2>&1 | tail -3` en la plantilla de `AGENTS.md`, o
  `check.sh --quiet`): la salida entera, ~5k tokens, se arrastró 283k en una sesión.
- **W3. Tope de llamadas en el encargo de la skill `gw-orchestrate-dealer`**: pasadas ~30, commit `WIP:` y devolver
  qué falta. Aplicado aquí como nota del proyecto; tres encargos lo pasaron en dos días (80, 66, 40).
- **W4. Rechazar commits con autor o committer `noreply@anthropic.com`**: propuesta completa en
  `docs/propuestas/galivelop-workflow/autor-agente-2026-11-13.md`.
