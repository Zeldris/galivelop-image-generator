# Hallazgos leves — `ccr-85e9d14e-zt7p8b` (relevo de `portal-marca`, 2026-11-11)

De la revisión del diff contra `origin/main` (fase 1). No se arreglan en este pull request ni vuelven a revisarse en él.

- `brandshop.resolve_font` llama a `fc-match` sin el peso y rechaza las `.ttc`.
- Los límites de los campos del taller no casan con los del servidor: borde mínimo 0 (el servidor pide 1 o más), texto
  del nombre con `maxlength` 100 (`MAX_TEXT` es 60), tolerancias hasta 255 (la distancia llega a ~441).
- Validaciones y datos repetidos: peso y espaciado en `brand.wordmark` y `brand.system`; la exclusión
  `--palette`/`--colors`; la expresión de color frente a `trace._COLOR`; `PIECES` en JS frente a `brand.SYSTEM_FILES`;
  `brandshop.save` llama al privado `brand._write`.
- `brand.matte` calcula `border_color` dos veces (en `brand.py` y dentro de `matte.remove_bg`).
- Sin verificar (confianza baja): la fuente de reserva en `wordmark`; `_place` redondea la escala a 3 decimales;
  `png.read_rgba` ignora `tRNS`; `--circular` junto a `--vae-tiling` no está probado.
- El camino completo con `rsvg-convert` (wordmark, lockup, `system` y luego `save`) solo corre en el CI: este
  contenedor no lo tiene.

Fase 1 de 2026-11-13 (diff contra `origin/main` sobre `9844344`):

- `brand lockup --force` reutiliza la clave de ayuda `cli.arg.brand_force_square` (`gimg/cli.py:136`); mejor una
  genérica `cli.arg.brand_force`.

## Tandas 1-5 (2026-11-13/14), sacados de la bitácora el 2026-11-15 (retro de la sexta tanda, P1)

- **Leves de la fase 1 de `ccr-85e9d14e-zt7p8b` (2026-11-13), de la segunda fase 1, de la tercera tanda, de la fase 1 para el PR y de la fase 3 (2026-11-14):** hechos en la cuarta tanda (2026-11-14) salvo: los tests de 8 de `tile` usan texturas sintéticas y el test de `brand system` simula el fallo con un mock. El de `<use>` en el negro implícito de `brand` no aplica: `_read_svg` rechaza `<use>`. **Leves de la fase 1 de la cuarta tanda:** el aviso de marco oscuro de `trace` sale por `warnings.warn` (una vez por proceso, en inglés, sin llegar a la API); `square` no copia atributos de la raíz entre comillas simples; el test de limpieza del gancho pasa también sin el arreglo. **Leves de la quinta tanda (2026-11-14):** `trace`: solo mono cubre la diagonal (color y silueta siguen «sin forma»), con `max_side` 512 sale un SVG vacío, `warnings` sin documentar ni test de UI y en la lengua del servidor; `brand square`: exponentes, `hsl(none …)` y `rgb` mezclando % y número sin cubrir; `matte`: CHROMA_BAND solo se prueba en el test de equivalencia, islas semitransparentes sueltas vacían vecinos; `tile`: `.gimg-tile-*` tras SIGKILL, una copia cuyo borrado falló puede resucitar un original viejo, `_backup_prefix` sensible a mayúsculas en Windows/macOS, `recovered`/`.gimg-bak-*` sin documentar, sin tests de carreras; tests del gancho: comentarios sin tildes; fase 1 de la quinta: `recover_backups` fuera del try que pone `exc.recovered` (lo restaurado antes de un fallo no se informa), `<line>` hereda el fill de la raíz y lo cuenta, el aviso de rollback incompleto sale de la librería sin `lang`, `cli.py` duplica `tile.describe_recovery`, `_sets(attrs,'fill')` duplica `_has_fill`, la pasada 2 de `tile` rehace `_spots` por fila; gancho de hojas: la clave por ppid falla abierta con una shell intermedia o en Windows (límite aceptado y documentado en `.claude/hooks/intentos-en-hoja.py`, sin arreglo). **Leves de la cuarta tanda (2026-11-14), hechos en la quinta:** `trace`: una diagonal de 1 px vuelve como píxeles sueltos (solo con `min_island` bajo), el aviso de marco oscuro (tinta ≥60 %) da falso positivo en la rama «oscuro fuera» y no llega a la UI ni a `brand.trace`; test de foco de la UI: aplana `@media` (solo da rojo de más); `sides()`: em=16 y auto=0 son supuestos; el `refreshNow` del test de `paused: null` no se comprueba; `tile`: ~1,55 s a 1024², destino ilegible, un SIGKILL a mitad deja `.gimg-bak-*`, los errores del rollback se tragan, sin test de tamaños impares pequeños; `brand`: `rgb` con separadores mezclados, valores fuera de rango, unidades `turn`/`rad`, un `stroke` de la raíz cuenta, `fill-opacity`/`opacity` se ignoran.
- **Leves de la revisión de `ccr-85e9d14e-zt7p8b` (2026-11-13):** los de la interfaz y los de R1, la ayuda y el barrido, hechos (el último lote en `35adba0`). El del gancho de hojas (captura suelta legítima; `.jpg`/`.webp`), hecho el 2026-11-14 con la confirmación de la persona: la primera captura suelta de la sesión pasa sin aviso y avisa desde la segunda; también `.jpg`, `.jpeg` y `.webp`.

## Séptima tanda (L7, 2026-11-15): leves de la fase 1

- `tile._mark_stale` solo se intenta tras fallar el borrado, y el renombrado suele fallar por lo mismo (carpeta sin
  escritura, archivo abierto en Windows): en ese caso la copia sigue como `.gimg-bak-*` y se da como `kept`
  (límite documentado en `_mark_stale`); una copia marcada se informa como `stale` en cada ejecución hasta que se borre.
- `brand._paint_colors`: el `stroke` de un `<g>` se cuenta aunque todos sus hijos lo pisen (ya pasaba en `main`).
- El taller deja poner tolerancia ≥ borde suave (cada campo está en rango, la combinación la rechaza `remove_bg`).
- `brand._check_weight_spacing` acepta `True` como peso (`isinstance(True, int)`), en `wordmark` y ahora en `resolve_font`.
