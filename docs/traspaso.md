<!-- galivelop-workflow v0.4.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `diseno-generador` |
| **Fase / tarea** | Paso 1 hecho (flujo Galivelop-workflow v0.4.0 aplicado); paso 2 en curso: diseño del generador de imágenes local reutilizable (`grilling` + `domain-modeling`; compactaciones: presupuesto 1, llevadas 0) |
| **Último punto estable** | Diseño rondas 1-2: decisiones D1-D17 en `docs/plan.md`, ADR 0001-0002, términos en `GLOSSARY.md` |
| **Siguiente paso** | Ronda 3 de `grilling` (lo de «Pendiente de decidir» en `docs/plan.md`); después, fases de implementación |
| **Check** | `bash -n .githooks/pre-commit .githooks/pre-push .githooks/commit-msg`: verde |

Con `logRows` en `.claude/gw.json`, cada rama escribe solo en su fila de esta tabla, como mucho 600 caracteres, con
la forma ``| **Tarea en curso · `<rama>`** | tarea, fases antes de `main`, qué falta y siguiente paso |``; el push lo comprueba.

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. 2026-10-25 — Diseño ronda 2 aprobada: pedido/intentos/elegida, cola, perfil de máquina, es+en, ADR 0001-0002.
2. 2026-10-25 — Diseño ronda 1 aprobada: servicio local independiente, sin dominio, Python stdlib, WMF piloto (`docs/plan.md`).
3. 2026-10-25 — Flujo Galivelop-workflow v0.4.0 aplicado (`aplicar.py --init`, `pushToProtected: pr`, `doctor.py` en verde).

## Pendiente

- **Deuda:** el `check` solo hace `bash -n` de los ganchos porque aún no hay código; cambiarlo por el lint + tests
  reales en cuanto se elija stack (`.claude/gw.json` → `check`, y `install` si hace falta).

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit .githooks/pre-push .githooks/commit-msg`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recuperar.py --estado`.
