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
