# Entrega de marca al Portal: lote 25-30, rosa y sello (2026-11-13)

Para la sesión del Portal (`Portal-Galivelop`). Completa la nota del 2026-11-12 (`entrega-marca-2026-11-12.md`), que
sigue valiendo. Desde aquí no se toca ese repo: esta nota dice qué hay y qué cambiar allí.

**Dónde están:** en la raíz de `piloto/portal-marca/portal-web-final/portal/`, la misma carpeta que la vez anterior;
la persona la pasa entera. Los iconos traen su SVG en `svg/` (se usa el SVG; el PNG queda de respaldo). Todo
aprobado por la persona; el intento de origen de cada una está en el `LEEME.md` de la carpeta.

## Qué hay

| Archivo | Para qué | Formato |
|---|---|---|
| `25a-icono-resumen` | icono de la sección Resumen de la página de proyecto: hoja con renglones | PNG + SVG |
| `25b-icono-galeria` | sección Galería: dos marcos superpuestos | PNG + SVG |
| `25c-icono-a-fondo` | sección A fondo: capas apiladas | PNG + SVG |
| `25d-icono-como-esta-hecho` | sección Cómo está hecho: llave inglesa entre «‹ ›» | PNG + SVG |
| `25e-icono-avance` | sección Avance: nodos hasta una bandera | PNG + SVG |
| `26a-marcador-hecho` | hito hecho: aro con visto | PNG, PNG de 64 px (`-64`) y SVG |
| `26b-marcador-en-curso` | hito en curso: el mismo aro con «…» | PNG, PNG de 64 px y SVG |
| `26c-marcador-pendiente` | hito pendiente: el mismo aro, vacío | PNG, PNG de 64 px y SVG |
| `27-estado-vacio` | estado vacío: ventana en blanco con cursor sobre la carta | PNG 480×360 |
| `28-aviso-error` | error de carga: ventana con los enchufes desconectados | PNG 480×360 |
| `29-banda-participar` | banda de la llamada a participar: cabo enrollado | PNG 1600×400 |
| `30-cabecera-novedades` | cabecera de Novedades: botella con mensaje sobre mar grabado | PNG 1600×400 |
| `04b-rosa-vientos` | rosa de los vientos, nueva versión | PNG transparente + SVG |
| `05b-sello-taller` | sello de taller, nueva versión | PNG transparente + SVG |

## Qué cambiar en el Portal

1. **Página de proyecto:** los iconos 25 son una serie; van juntos, uno por sección, sin mezclarlos con lucide.
2. **Avance:** los marcadores 26a, 26b y 26c son una serie (mismo aro y mismo trazo); el de 64 px es para tamaños
   pequeños si el SVG no se ve bien.
3. **Estados de carga:** 27 cuando una lista está vacía y 28 cuando falla la carga.
4. **29 y 30** van a sangre, a todo el ancho. El motivo de la 29 (el cabo) está en el tercio derecho, para dejar
   sitio al texto. Si el título no se lee sobre alguna de las dos, se le pone un velo por CSS; la imagen no se
   recorta.
5. **04b y 05b sustituyen** a la rosa (`public/marca/rosa-vientos.svg`) y al sello (`public/marca/sello.svg`). Sus
   PNG salen del SVG, con fondo transparente y el cerúleo `#0072a8` de la paleta. En la rosa, el contorno claro de
   las puntas sale punteado: no se nota a tamaño de icono, pero en grande sí.
