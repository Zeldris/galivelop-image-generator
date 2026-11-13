# Entrega de marca al Portal: lote 25-30, rosa y sello (2026-11-13)

Para la sesión del Portal (`Portal-Galivelop`). Completa la nota del 2026-11-12 (`entrega-marca-2026-11-12.md`), que
sigue valiendo. Desde aquí no se toca ese repo: esta nota dice qué hay y qué cambiar allí.

**Dónde están:** en la raíz de `piloto/portal-marca/portal-web-final/portal/`, la misma carpeta que la vez anterior;
la persona la pasa entera. Los iconos traen su SVG en `svg/` (se usa el SVG; el PNG queda de respaldo). Todo
aprobado por la persona; el intento de origen de cada una está en el `LEEME.md` de la carpeta.

**Revisión del Portal (2026-11-13):** 26a, 26b, 29, 04b y 05b se rehacen (ver «Pendiente»); hasta entonces, lo que
hay de ellas en la carpeta no se usa.

## Nuevo en este lote

| Archivo | Para qué | Formato |
|---|---|---|
| `25d-icono-como-esta-hecho` | sección Cómo está hecho de la página de proyecto: llave inglesa entre «‹ ›» | PNG + SVG |
| `26c-marcador-pendiente` | hito pendiente: aro vacío; es el aro de referencia de la serie 26 | PNG, PNG de 64 px (`-64`) y SVG |
| `30-cabecera-novedades` | cabecera de Novedades: botella con mensaje sobre mar grabado | PNG 1600×400 |

## Ya entregado el 2026-11-12

| Archivo | Para qué |
|---|---|
| `25a-icono-resumen`, `25b-icono-galeria`, `25c-icono-a-fondo`, `25e-icono-avance` | iconos de las secciones Resumen, Galería, A fondo y Avance |
| `26a-marcador-hecho` | hito hecho (se rehace, ver «Pendiente») |
| `27-estado-vacio`, `28-aviso-error` | estado vacío y error de carga (ya publicadas) |

## Qué cambiar en el Portal

1. **Página de proyecto:** los iconos 25 son una serie; van juntos, uno por sección, sin mezclarlos con lucide.
2. **Avance:** los marcadores 26 son una serie y tienen que superponerse: mismo aro (diámetro y grosor) y un solo
   grosor de trazo. Mientras llegan 26a y 26b rehechos, no se mezcla el 26c con los actuales.
3. **30** va a sangre, a todo el ancho. Si el título no se lee encima, se le pone un velo por CSS; la imagen no se
   recorta.

## Pendiente

- **26a marcador hecho:** el visto, del mismo grosor que el aro, y el aro igual que el de 26c.
- **26b marcador en curso:** tres puntos macizos y centrados (los aritos huecos se emborronan a 16-24 px), con el aro
  de 26c.
- **29 banda Participar:** sin la rayita suelta sobre el cabo, y con el cabo entero, punta incluida, de x≈1000 en
  adelante (sobre 1600).
- **04b rosa de los vientos** (ficha 4, primera entrega: `public/marca/` no tiene ninguna): de ocho puntas, en línea
  simple, con un solo grosor y el contorno continuo. Se usará también en grande, como marca de agua: tiene que verse
  bien a 512 px, y su SVG, sin escalones, con menos de ~15 KB.
- **05b sello de taller** (ficha 5, primera entrega): dos anillos con marcas de grados regulares y el monograma GV del
  logo en el centro, sin texto; SVG limpio, sin escalones.
- **04b y 05b, versión de una sola tinta:** un color, sin el papel de fondo, para pintarla con `currentColor` en los
  temas claro y oscuro.
- **29 versión oscura:** el mismo cabo sobre el fondo noche del Portal (`#0d171e`, superficie `#111f29`), dibujado para
  fondo oscuro, no el claro invertido; 1600×400, con el cabo en la mitad derecha.
- **10b** y las **versiones oscuras** de 10, 18, 19, 27 y 28.
