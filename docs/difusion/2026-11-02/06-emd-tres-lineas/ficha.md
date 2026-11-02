# Ficha: emd-tres-lineas (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/06-emd-tres-lineas/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- x
- linkedin
- foro

## Qué se cuenta

- **En una frase (quien lo usa):** ¿Se parece esta imagen a la marca? Con la distancia de Wasserstein entre histogramas de color, calculada en tres líneas de Python sin numpy.
- **En una frase (técnico):** La función `emd` suma, sobre los 256 niveles de cada canal (Y, Cb, Cr), la diferencia absoluta entre las distribuciones acumuladas de dos imágenes; usa solo la biblioteca estándar.
- **Estado:** en desarrollo (medida de marca aún sin fusionar en la rama principal)

## Hechos comprobados

| Dato | Fuente |
|---|---|
| `emd` suma sobre los 256 niveles de abs(CDF a − CDF b) por canal (Y, Cb, Cr) | `gimg/measure.py:212-214`, `gimg/measure.py:28` |
| `_cdf` acumula el histograma del canal y lo divide por el total de píxeles | `gimg/measure.py:201-209` |
| El proyecto no tiene dependencias: Python 3 solo con la biblioteca estándar | `README.md:5-7` |
| `gimg measure` da el porcentaje de paleta, YAVG y SATAVG, la EMD de Cb y Cr con imágenes de referencia y el contraste WCAG de una zona | `docs/plan.md:43` |
| La imagen muestra `emd` con el `return` partido en dos líneas y un comentario en lugar del docstring, por ancho | `gimg/measure.py:212-214` |

## Imágenes

Una fila por cada archivo de `medios/` que se usa (`.webp` para X y Discord, `.png` para LinkedIn, `.pdf` para un
carrusel de LinkedIn). El texto alternativo describe lo que se ve de la pieza, con el formato `es: texto / en: text`.
El primer idioma de `Idiomas:` usa `medios/<n>.webp`; otro idioma puede tener su propia imagen
`medios/<n>.<idioma>.webp` (fuente `<n>.<idioma>.html`), con su fila y el texto alternativo en ese idioma.

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/codigo.webp` | es: código Python de la función `emd` de gimg/measure.py: `def emd(planes_a, planes_b) -> dict:`, un comentario «Wasserstein-1: suma sobre los 256 niveles de abs(CDF a - CDF b)» y un `return` que, por cada canal, suma abs(x - y) sobre zip(_cdf(a), _cdf(b)) / en: Python code of the `emd` function in gimg/measure.py: `def emd(planes_a, planes_b) -> dict:`, a comment "Wasserstein-1: sum over the 256 levels of abs(CDF a - CDF b)" and a `return` that, per channel, sums abs(x - y) over zip(_cdf(a), _cdf(b)) | x, foro |
| `medios/codigo.png` | es: código Python de la función `emd` de gimg/measure.py: `def emd(planes_a, planes_b) -> dict:`, un comentario «Wasserstein-1: suma sobre los 256 niveles de abs(CDF a - CDF b)» y un `return` que, por cada canal, suma abs(x - y) sobre zip(_cdf(a), _cdf(b)) / en: Python code of the `emd` function in gimg/measure.py: `def emd(planes_a, planes_b) -> dict:`, a comment "Wasserstein-1: sum over the 256 levels of abs(CDF a - CDF b)" and a `return` that, per channel, sums abs(x - y) over zip(_cdf(a), _cdf(b)) | linkedin |
| `medios/codigo.en.webp` | es: versión en inglés de la tarjeta de código de `emd` (gimg/measure.py), con el título «Does it match the brand? EMD in three lines» y el mismo código: un `return` que suma abs(x - y) sobre zip(_cdf(a), _cdf(b)) por canal / en: English version of the `emd` code card (gimg/measure.py), titled "Does it match the brand? EMD in three lines" with the same code: a `return` that sums abs(x - y) over zip(_cdf(a), _cdf(b)) per channel | x, foro |
| `medios/codigo.en.png` | es: versión en inglés de la tarjeta de código de `emd` (gimg/measure.py), con el título «Does it match the brand? EMD in three lines» y el mismo código: un `return` que suma abs(x - y) sobre zip(_cdf(a), _cdf(b)) por canal / en: English version of the `emd` code card (gimg/measure.py), titled "Does it match the brand? EMD in three lines" with the same code: a `return` that sums abs(x - y) over zip(_cdf(a), _cdf(b)) per channel | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P6 de `docs/difusion/propuestas/2026-11-02.md`; tarea F2.9 (D31), commit `d6fc49d`, sin fusionar a `main`.
- Repo privado y sin licencia: ningún enlace. No nombrar las marcas hermanas.
- Canal foro (sustituye a Reddit): sin normas de subreddit; no hay canal reddit.
- Se omite de la propuesta el dato «ΔE76 < 15»: no consta en `docs/plan.md:43`.

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
