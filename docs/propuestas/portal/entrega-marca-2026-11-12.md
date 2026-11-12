# Entrega de marca al Portal (2026-11-12)

Para la sesión del Portal (`Portal-Galivelop`). Desde aquí no se toca ese repo: esta nota dice qué hay y qué
cambiar allí.

**Dónde están las imágenes:** `piloto/portal-marca/portal-web-final/portal/` de galivelop-image-generator (fuera
de git; la carpeta la tiene la persona en su equipo). La raíz es lo que va a la web; `svg/` trae la versión
vectorial de los iconos (se usa esa, el PNG queda de respaldo); `aprobadas/` es lo aprobado sin sitio en la web;
`LEEME.md` tiene el intento de origen de cada una.

Desde el 2026-11-12, `portal-web-final/` tiene una carpeta por proyecto del que habla la web, con el mismo reparto
(`LEEME.md` general en `portal-web-final/`): `portal/` (la marca del Portal), `galivelop-voice-generator/` (tarjeta
«próximamente» 15, q331), `galivelop-developer/` (tarjeta 15, q311), `galivelop-workflow/` (icono 23, q490, con su
SVG), y `tarkor/`, `toveriai/` y `galivelop-image-generator/`, aún vacías. Esas tres piezas salieron de `portal/`:
la ruta cambia, el archivo no.

## Qué cambiar en el Portal

1. **Ficha 6 de `docs/marca.md`: las tres portadas por estado son ahora una serie del faro**, sin ventana de
   editor:
   - desarrollo: faro en obra con andamio (`06-portada-desarrollo-faro.png`, q628);
   - diseño: islote con cimientos, estacas y trípode (`06-portada-diseno-faro.png`, q635);
   - publicado: faro encendido de noche (`06-portada-publicado-faro.png`, q641).
   Hoy solo se ve la de desarrollo (cabecera `color`); para las otras dos hace falta el velo por estado del commit
   `88354fb` del Portal.
2. **La q311 (barco de olas) no tiene sitio**: Developer solo sale en «próximamente» con la ficha 15. Queda en
   `aprobadas/06-portada-developer-q311.png`.
3. **Series de iconos completas** (el Portal no las mezcla con lucide), en `svg/`:
   - 07 líneas de trabajo, **cinco** para las cinco líneas de `src/data/lineas.ts`: 07a código, 07b papel-ventana
     (corregido: una sola figura cuadrada, hoja con esquina doblada y ventana de tres puntos; q651), 07c documento con check, 07d compás sobre plano, 07e mundos (mapa plegado con cordillera). El reparto
     icono-línea lo decide el Portal.
   - 08 valores: 08a candado, 08b mira, 08c historial (corregido: tres nodos en vertical y una rama a un cuarto; q658), 08d ramas unidas (corregido: «Y» invertida ancha, casi cuadrada, con las dos ramas confluyendo en un nodo central; q782).
   - 09 vías: 09a rama, 09b bombilla, 09c terminal.
4. Sin cambios: 10, 13, 15, 17, 18, 19 y 23 ya están en la web; el 12 (separador) espera su componente y se queda el de
   siempre (q564, con estrella) por decisión de la persona del 2026-11-12, aunque el Portal pidió uno sin estrella; el 14
   sigue sin uso (ADR 0004), en `aprobadas/`.
