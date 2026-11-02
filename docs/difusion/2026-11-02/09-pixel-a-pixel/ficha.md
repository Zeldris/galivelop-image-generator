# Ficha: pixel-a-pixel (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/09-pixel-a-pixel/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- x
- linkedin
- foro

## Qué se cuenta

- **En una frase (quien lo usa):** ¿Da lo mismo generar una imagen con el script de pruebas que con el servicio? Con la misma semilla, sí: 14 imágenes iguales píxel a píxel.
- **En una frase (técnico):** Se compara el md5 de los fotogramas decodificados con `ffmpeg -f md5`; los bytes del PNG difieren solo por un bloque `tEXt` que añade el servicio, pero los píxeles no.
- **Estado:** en desarrollo (el motor real del servicio aún no está fusionado en la rama principal)

## Hechos comprobados

| Dato | Fuente |
|---|---|
| Las 14 imágenes del servicio son píxel a píxel iguales a las del script anterior, comprobado con `ffmpeg -f md5` | `docs/registros/contenido/r1-fondos.md:22` |
| El md5 es de píxeles; los bytes de los PNG difieren solo por un bloque `tEXt` que añade el servicio | `docs/registros/contenido/r1-fondos.md:24-27` |
| Las 14 piezas: 1280×640, 6 pasos, semillas 3 y 4, dos imágenes por proyecto | `docs/registros/contenido/r1-fondos.md:8-10` |
| El tiempo es predecible por píxeles y pasos, con un margen de ±1 % | `docs/registros/contenido/r5-piezas.md:67` |
| La tarjeta es una ilustración de la comprobación: nombres de archivo simplificados (`script/`, `servicio/`), orden `ffmpeg -v error -i <imagen> -f md5 -` | `docs/registros/contenido/r1-fondos.md:22` (solo `ffmpeg -f md5`) |

## Imágenes

Una fila por cada archivo de `medios/` que se usa (`.webp` para X y Discord, `.png` para LinkedIn, `.pdf` para un
carrusel de LinkedIn). El texto alternativo describe lo que se ve de la pieza, con el formato `es: texto / en: text`.
El primer idioma de `Idiomas:` usa `medios/<n>.webp`; otro idioma puede tener su propia imagen
`medios/<n>.<idioma>.webp` (fuente `<n>.<idioma>.html`), con su fila y el texto alternativo en ese idioma.

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/codigo.webp` | es: tarjeta con un terminal que ejecuta dos veces `ffmpeg -v error -i <imagen> -f md5 -`, una sobre la imagen del script y otra sobre la del servicio, con el comentario «mismo md5 = mismos píxeles» / en: card showing a terminal that runs `ffmpeg -v error -i <image> -f md5 -` twice, once on the script's image and once on the service's, with the comment "same md5 = same pixels" | x, foro |
| `medios/codigo.png` | es: tarjeta con un terminal que ejecuta dos veces `ffmpeg -v error -i <imagen> -f md5 -`, una sobre la imagen del script y otra sobre la del servicio, con el comentario «mismo md5 = mismos píxeles» / en: card showing a terminal that runs `ffmpeg -v error -i <image> -f md5 -` twice, once on the script's image and once on the service's, with the comment "same md5 = same pixels" | linkedin |
| `medios/codigo.en.webp` | es: versión en inglés de la tarjeta, titulada «Same result, pixel for pixel», con los mismos dos `ffmpeg -f md5` / en: English version of the card, titled "Same result, pixel for pixel", with the same two `ffmpeg -f md5` commands | x, foro |
| `medios/codigo.en.png` | es: versión en inglés de la tarjeta, titulada «Same result, pixel for pixel», con los mismos dos `ffmpeg -f md5` / en: English version of the card, titled "Same result, pixel for pixel", with the same two `ffmpeg -f md5` commands | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P9 de `docs/difusion/propuestas/2026-11-02.md`; origen: ronda r1 de F2.6 (`gimg work`), sin fusionar a `main`.
- Repo privado y sin licencia: ningún enlace. No nombrar las marcas hermanas.
- Canal foro (sustituye a Reddit): sin normas de subreddit; no hay canal reddit.
- Se omite que 7 proyectos dieran las 14 piezas por nombre y la comparación de tiempos de r1; solo se cuenta el md5.

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
