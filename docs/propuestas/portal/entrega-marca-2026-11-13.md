# Entrega de marca al Portal: lote 25-30, rosa y sello (2026-11-13)

Para la sesión del Portal (`Portal-Galivelop`). Completa la nota del 2026-11-12 (`entrega-marca-2026-11-12.md`), que
sigue valiendo. Desde aquí no se toca ese repo: esta nota dice qué hay y qué cambiar allí.

**Dónde están:** en la raíz de `piloto/portal-marca/portal-web-final/portal/`, la misma carpeta que la vez anterior;
la persona la pasa entera. Los iconos traen su SVG en `svg/` (se usa el SVG; el PNG queda de respaldo). Todo
aprobado por la persona; el intento de origen de cada una está en el `LEEME.md` de la carpeta.

**Revisión del Portal (2026-11-13):** 26a, 26b, 29, 05b y la rosa 04b ya están rehechas (abajo, en «Rehecho tras la revisión»).

## Nuevo en este lote

| Archivo | Para qué | Formato |
|---|---|---|
| `25d-icono-como-esta-hecho` | sección Cómo está hecho de la página de proyecto: llave inglesa entre «‹ ›» | PNG + SVG |
| `26c-marcador-pendiente` | hito pendiente: aro vacío; es el aro de referencia de la serie 26 | PNG, PNG de 64 px (`-64`) y SVG |
| `30-cabecera-novedades` | cabecera de Novedades: botella con mensaje sobre mar grabado | PNG 1600×400 |

## Rehecho tras la revisión

| Archivo | Para qué | Formato |
|---|---|---|
| `26a-marcador-hecho` | hito hecho: el aro de 26c con un visto del mismo grosor | PNG, PNG de 64 px (`-64`) y SVG |
| `26b-marcador-en-curso` | hito en curso: el aro de 26c con tres puntos macizos y centrados | PNG, PNG de 64 px (`-64`) y SVG |
| `05b-sello-taller` | sello de taller: dos anillos con marcas de grados y el monograma GV de `public/marca/gv-logo.svg`, sin texto | PNG + SVG, y `svg/05b-sello-taller-tinta.svg` de una sola tinta (`currentColor`, sin papel) |
| `04b-rosa-vientos` | rosa de los vientos (ficha 4): ocho puntas, un solo grosor, contorno continuo, dibujada por código (SVG exacto de ~5 KB) | PNG + SVG, y `svg/04b-rosa-vientos-tinta.svg` de una sola tinta (`currentColor`, sin papel, centro hueco) |
| `29-banda-participar` | banda Participar: cabo de x≈1050 en adelante, sin la rayita | PNG 1600×400 |
| `29-banda-participar-oscura` | la misma banda sobre el fondo noche (#0d171e), dibujada para oscuro | PNG 1600×400 |

Los 26a, 26b y 26c llevan el mismo aro exacto (el de 26c, copiado por gimg), así que se superponen.

## Ya entregado el 2026-11-12

| Archivo | Para qué |
|---|---|
| `25a-icono-resumen`, `25b-icono-galeria`, `25c-icono-a-fondo`, `25e-icono-avance` | iconos de las secciones Resumen, Galería, A fondo y Avance |
| `27-estado-vacio`, `28-aviso-error` | estado vacío y error de carga (ya publicadas) |

## Qué cambiar en el Portal

1. **Página de proyecto:** los iconos 25 son una serie; van juntos, uno por sección, sin mezclarlos con lucide.
2. **Avance:** los marcadores 26 son una serie y tienen que superponerse: mismo aro (diámetro y grosor) y un solo
   grosor de trazo. Ya llegan los tres: se sustituyen 26a y 26b por los de esta entrega.
3. **30** va a sangre, a todo el ancho. Si el título no se lee encima, se le pone un velo por CSS; la imagen no se
   recorta.
4. **29** en tema claro y **29-banda-participar-oscura** en el oscuro (cambiar de imagen con el tema, no invertirla).

## Pendiente

- **10b** y las **versiones oscuras** de 10, 18, 19, 27 y 28.
