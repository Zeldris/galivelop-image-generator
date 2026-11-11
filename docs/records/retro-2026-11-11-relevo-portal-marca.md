# Retro — relevo de `portal-marca` a `main` (`ccr-85e9d14e-zt7p8b`, 2026-11-11)

**Estado:** aprobada entera por la persona el 2026-11-11. P1 aplicada (nota en `.claude/gw/gw-opt-tokens.md`, con la
forma corregida: `per_page` no recorta `actions_list`); P2 aplicada como entorno personal propio del repo con script
de arranque (`apt-get update` e instalar `librsvg2-bin`), no en el Default; P3 aprobada sin cambio.

Alcance: solo el relevo (fusión de `portal-marca`, revisión de fase 1 y sus arreglos). `portal-marca` ya hizo sus
propias retros y su `gw-opt-ai`; aquí no hubo medidas con un modelo local.

## Medida (`measure.py --since 2509674`)

Principal: 41 llamadas, contexto medio 126k, 5,2 M de entrada (96 % de caché). Subagentes: 3 (uno de revisión, dos
`sonnet` de arreglos), 4,5 M de entrada, arranque medio 66k. Lo más arrastrado en la principal:
`actions_list` con 15 ejecuciones (12k tokens, 170k arrastrados) y `list_pull_requests` con `state: all` (5,7k, 91k).

## Propuestas

- **P1 (gasto, proyecto).** Apuntar en `.claude/gw/gw-opt-tokens.md`: el CI y los pull requests se consultan con
  `per_page` 3 (o `minimal_output`), no con listados de 15. Ahorro: ~250k arrastrados por sesión de cierre. Riesgo:
  ninguno; si hace falta más historia se pide otra página.
- **P2 (entorno, de la persona).** Este contenedor no tiene `rsvg-convert` y `apt-get install librsvg2-bin` falló: 73
  tests se saltan y el camino wordmark → lockup → `system` → `save` solo lo comprueba el CI. Añadir
  `apt-get install -y librsvg2-bin` al script de arranque del entorno en la nube. Riesgo: ninguno. Lo bueno de no
  tenerlo: destapó que `brand system` pedía la herramienta antes de validar las opciones (`4a45c88`).
- **P3 (proceso, sin cambio).** Los dos subagentes de arreglos escribieron en el árbol principal y no en un worktree,
  contra la nota del 2026-11-04; el gancho de parada pidió un commit con sus cambios a medias (una vuelta y un commit
  solo de documentación). La regla ya existe y ya está propuesta al flujo: no se añade nada, se cumple.

## For Galivelop-workflow

- `gw-orchestrate-dealer`: que el encargo de un subagente que escribe código lleve `isolation: "worktree"` por
  defecto cuando la principal sigue trabajando (repite la propuesta del 2026-11-04; volvió a costar una vuelta).
