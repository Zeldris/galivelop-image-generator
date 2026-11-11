# Ficha: texto-svg (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/02-texto-svg/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- x
- linkedin
- foro

## Qué se cuenta

- **En una frase (quien lo usa):** Cambiar el titular de una imagen no obliga a volver a generarla: se recompone en un par de segundos.
- **En una frase (técnico):** El texto y el logo no los pinta el modelo: una plantilla SVG se rasteriza y se superpone sobre la imagen cruda, y se guardan las dos.
- **Estado:** en desarrollo

## Hechos comprobados

| Dato | Fuente |
|---|---|
| FLUX no da texto legible: los prompts de otro proyecto piden «completely textless» | `docs/plan.md:40` |
| El perfil declara una plantilla SVG con huecos (título, subtítulo, logo) y el tamaño de destino; el pedido trae los textos | `docs/plan.md:40` |
| El generador rasteriza la plantilla con `rsvg-convert` y la superpone con `ffmpeg` sobre la imagen generada, recortada y escalada | `docs/plan.md:40` |
| Se guardan la cruda (`q<id>.raw.png`) y la compuesta (`q<id>.png`), que es la que se ve y se entrega | `docs/plan.md:40` |
| `gimg compose` recompone desde la cruda sin volver a generar | `docs/plan.md:40` |
| Los logos son SVG vectoriales, nunca generados | `docs/plan.md:41` |
| Un cambio de titular tras 49 min de generación no puede costar otros 49 | `docs/plan.md:40` |
| El modelo de calidad tarda unos 49 min | `docs/plan.md:42` |
| Componer una pieza lleva ~2 s y no toca la imagen generada | `docs/registros/contenido/r4-composicion.md:40` |
| La medida de contraste por percentiles no ve líneas finas que cruzan el texto; se propone medir en la caja de cada línea | `docs/registros/contenido/r4-composicion.md:42-44` |

## Imágenes

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/diagrama.webp` | es: diagrama de cuatro pasos: imagen cruda sin texto, plantilla SVG con huecos, composición con rsvg-convert y ffmpeg, imagen compuesta; una flecha de vuelta indica que un titular nuevo se recompone desde la cruda sin regenerar / en: four-step diagram: raw image with no text, SVG template with slots, composition with rsvg-convert and ffmpeg, composed image; a return arrow shows a new headline is recomposed from the raw image without regenerating | x, foro |
| `medios/diagrama.png` | es: diagrama de cuatro pasos: imagen cruda sin texto, plantilla SVG con huecos, composición con rsvg-convert y ffmpeg, imagen compuesta; una flecha de vuelta indica que un titular nuevo se recompone desde la cruda sin regenerar / en: four-step diagram: raw image with no text, SVG template with slots, composition with rsvg-convert and ffmpeg, composed image; a return arrow shows a new headline is recomposed from the raw image without regenerating | linkedin |
| `medios/diagrama.en.webp` | es: versión en inglés del diagrama de cuatro pasos: raw image, SVG template, composition, composed image, con la flecha de vuelta para recomponer sin regenerar / en: four-step diagram: raw image, SVG template, composition, composed image, with a return arrow to recompose without regenerating | x, foro |
| `medios/diagrama.en.png` | es: versión en inglés del diagrama de cuatro pasos: raw image, SVG template, composition, composed image, con la flecha de vuelta para recomponer sin regenerar / en: four-step diagram: raw image, SVG template, composition, composed image, with a return arrow to recompose without regenerating | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P2 de `docs/difusion/propuestas/2026-11-02.md`; decisión D28, tarea F2.8, commit `a2bb37b` (sin fusionar a `main`).
- El repo es privado y sin licencia: ningún enlace. No nombrar las marcas hermanas.
- Canal foro (sustituye a Reddit): sin normas de subreddit.

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
