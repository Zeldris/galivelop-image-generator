<!-- galivelop-workflow v0.4.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `f0-esqueleto` |
| **Fase / tarea** | F0 Esqueleto (`docs/plan.md`): paquete `gimg`, esquemas, validador stdlib, textos es/en, README es/en, check con `unittest`. Presupuesto: 1 compactación (llevadas: 1 al empezar) |
| **Último punto estable** | F0 implementada: `gimg/` (validador, i18n, esquemas, preajuste `steam-deck`), `examples/`, 50 tests, README es/en, CHANGELOG |
| **Siguiente paso** | Fase 1 antes de `main`: `/code-review --max-findings all` del diff contra `origin/main` |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |

Con `logRows` en `.claude/gw.json`, cada rama escribe solo en su fila de esta tabla, como mucho 600 caracteres, con
la forma ``| **Tarea en curso · `<rama>`** | tarea, fases antes de `main`, qué falta y siguiente paso |``; el push lo comprueba.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-10-25 — `diseno-generador` a `main` por push directo con confirmación de la persona: CI sin cuota, **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `b111e4f`.
2. 2026-10-25 — Diseño ronda 3 aprobada: clave del pedido, retoque de prompt, entrega PNG, `gimg`, seguridad, registro opt-ai.
3. 2026-10-25 — Diseño ronda 2 aprobada: pedido/intentos/elegida, cola, perfil de máquina, es+en, ADR 0001-0002.
4. 2026-10-25 — Diseño ronda 1 aprobada: servicio local independiente, sin dominio, Python stdlib, WMF piloto (`docs/plan.md`).
5. 2026-10-25 — Flujo Galivelop-workflow v0.4.0 aplicado (`aplicar.py --init`, `pushToProtected: pr`, `doctor.py` en verde).

## Pendiente

- **F1, entrega (D25):** el esquema no impide que `delivery.template` salga de la carpeta de entrega
  (`../{key}.png`, porque `{key}` lleva `/` a propósito); la entrega tiene que resolver la ruta final, con enlaces,
  y rechazarla si queda fuera de `delivery.dir`. Igual con `references` (enlaces que salgan del proyecto).
- **Cuando la persona avise:** revisar las actualizaciones de Tarkor (otro repo) sobre su generador de imágenes: lo lee
  un subagente `Explore` que devuelve un resumen con rutas (`orchestrate-dealer`); desde aquí no se modifica.
- El flujo copiado es la 0.4.0 **sin publicar** (rama `ccr-6dfbc880-ddr41g` del flujo, commit `d227bbf`; su `main` está en
  0.3.0): `/gw-update` cuando la 0.4.0 salga publicada.
- Proponer al flujo (`gw-harvest`) lo de `docs/registros/retro-2026-10-25-diseno.md` (R1-R4, R7); el hallazgo
  MEDIO de R7 (claves pegadas a una letra en `pre-commit`) conviene arreglarlo antes de publicar la 0.4.0.
- Proponer al flujo (`gw-harvest`) una operación de imagen en el `log-format.md` de `opt-ai` (D26).

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit .githooks/pre-push .githooks/commit-msg` y `python3 -m unittest discover -s tests -t .`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recuperar.py --estado`.
