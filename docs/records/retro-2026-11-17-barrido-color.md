# Retro 2026-11-17: barrido de color de `brand.py` y su fase 1

Rama `ccr-85e9d14e-zt7p8b`, desde `78975bf` (PR #23) hasta `9b04e38`. Sesión `0cacc78c`.

## Medidas (gw-opt-tokens)

- Principal: 49 llamadas, 5,6 M de entrada (114k de media, suelo 134k, techo 139k, 0 compactaciones). Arranque tras
  `/clear`: 97k, de los que ~82k son el sistema, las herramientas y los conectores del entorno (conocido; la persona
  no lo cambia de momento).
- `gimg/brand.py` se leyó 19 veces en la principal (7,8k tokens, 239k arrastrados): el barrido P3 se hizo en la
  principal, no en un `gw-worker`, aunque la regla del 2026-11-16 lo pide.
- La revisión de fase 1 en `gw-reviewer`: 9 llamadas, 47k tokens. Encontró un medio real.

## Propuestas

**P1. El barrido a un `gw-worker`: la regla se sigue rompiendo** (al flujo). La regla aprobada el 2026-11-16 («un barrido
o los arreglos de una revisión con 2 o más puntos van a un `gw-worker`») no se cumplió en la tarea siguiente. Según
`AGENTS.md`, una regla que se rompe se convierte en comprobación: que `gw-selector`, cuando la tarea es un barrido o
unos arreglos de revisión, devuelva en su línea «a `gw-worker` sonnet», y que el gancho de inicio lo recuerde cuando
el «Siguiente» de la bitácora diga barrido o arreglos. Ahorro estimado: ~2-3 M del modelo grande por barrido.
Riesgo de calidad: el trabajador falla más; contrapeso, la fase 1 del bloque ya revisa su diff.

**P2. Un test de una salida SVG/XML la valida entera** (del proyecto, `REVIEW.md` y `tests/test_brand.py`). El medio de
esta fase 1 (`<g fill=… fill=…>`, XML que rsvg rechaza) pasaba el test porque solo miraba `startswith`. Propuesta:
un ayudante en `tests/test_brand.py` que pasa por `xml.etree.ElementTree.fromstring` toda salida de `_square_ink` y
de `square()` que comprueban los tests, y una regla en `REVIEW.md`: «un test de una salida generada (SVG, XML, JSON)
la parsea o la compara entera, no por prefijo (criterio)». Coste: pequeño. Riesgo: ninguno.

**P3. Barrido de leves de `gimg/brand.py`** (tarea B, para 0.7.0). Lo cierra: `_paint_value` salta valores mal
formados; `hsl(1e400 …)` como hace rsvg (comprobarlo antes); unir `_paints` y `_ink`; `_ink` una sola vez por pintura
heredada; `fill` explícito en `<line>` (sexta tanda). Al `gw-worker` sonnet (P1).

## For Galivelop-workflow

- P1: `gw-selector` y el gancho de inicio señalan el `gw-worker` para barridos y arreglos de revisión.

**Estado:** aprobada (2026-11-17) y aplicada: P2 (validador en `SquareTests.setUp` y regla en `REVIEW.md`); P1 aprobada, al flujo; P3 aprobada, en «Pendiente» de la bitácora para 0.7.0.
