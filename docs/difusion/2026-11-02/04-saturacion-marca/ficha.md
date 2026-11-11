# Ficha: saturacion-marca (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/04-saturacion-marca/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- linkedin
- foro
- x

## Qué se cuenta

- **En una frase (quien lo usa):** Oscurecer el fondo arregló el brillo de una pieza de marca, pero el color siguió apagado y el ajuste a la paleta empeoró.
- **En una frase (técnico):** Al pasar el YAVG de 169 a 66 la saturación (SATAVG) siguió en 5, lejos del 15-30 que pide la marca, y la paleta cayó al 51 %.
- **Estado:** en desarrollo (medición hecha con el generador local, que aún no está entregado)

## Hechos comprobados

| Dato | Fuente |
|---|---|
| Con el fondo más oscuro, el YAVG de la pieza pasa de 169 a 66 y el fondo deja de estar lavado | `docs/registros/contenido/r5-piezas.md:41-42` |
| El SATAVG sigue en 5 (en la versión anterior, 7,8), lejos del 15-30 que pide el juego | `docs/registros/contenido/r5-piezas.md:42-43` |
| El ajuste a la paleta cae al 51 % (el cielo no está entre los colores hex de la guía de la marca) | `docs/registros/contenido/r5-piezas.md:43` |
| Bajar la luz no basta: hace falta pedir el color de forma explícita (acento en las agujas, banda cálida más ancha) o aceptar que la marca es desaturada | `docs/registros/contenido/r5-piezas.md:43-44` |
| Cómo se escribe el color (palabras, hex o material) da casi la misma imagen; los hex no mejoran el porcentaje de paleta de forma clara | `docs/registros/contenido/r2-estilo.md:59-61` |

## Imágenes

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/metricas.webp` | es: tarjeta de métricas con la cifra grande «SATAVG 5» y cinco barras: luminosidad antes 169, luminosidad ahora 66, saturación ahora 5, saturación pedida 15-30 y ajuste a la paleta 51 % / en: metrics card with the big figure "SATAVG 5" and five bars: brightness before 169, brightness now 66, saturation now 5, saturation asked 15-30 and palette fit 51 % | foro, x |
| `medios/metricas.png` | es: tarjeta de métricas con la cifra grande «SATAVG 5» y cinco barras: luminosidad antes 169, luminosidad ahora 66, saturación ahora 5, saturación pedida 15-30 y ajuste a la paleta 51 % / en: metrics card with the big figure "SATAVG 5" and five bars: brightness before 169, brightness now 66, saturation now 5, saturation asked 15-30 and palette fit 51 % | linkedin |
| `medios/metricas.en.webp` | es: versión en inglés de la tarjeta de métricas: SATAVG 5 frente a los 15-30 pedidos, luminosidad 169 a 66, paleta 51 % / en: English version of the metrics card: SATAVG 5 against the 15-30 asked, brightness 169 to 66, palette fit 51 % | foro, x |
| `medios/metricas.en.png` | es: versión en inglés de la tarjeta de métricas: SATAVG 5 frente a los 15-30 pedidos, luminosidad 169 a 66, paleta 51 % / en: English version of the metrics card: SATAVG 5 against the 15-30 asked, brightness 169 to 66, palette fit 51 % | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P4 de `docs/difusion/propuestas/2026-11-02.md`. La pieza medida es la variante «og-bajo» de r5; la anterior es la de r4.
- La decisión sobre LUT o color explícito sigue abierta (D31, F2.9).
- El repo es privado y sin licencia: ningún enlace. No nombrar las marcas hermanas.
- Canal foro (sustituye a Reddit): sin normas de subreddit.
- La escala de las barras es común (la más larga es 169); mezcla unidades distintas, por eso cada barra lleva su etiqueta.

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
