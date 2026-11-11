# Ficha: steam-deck (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/08-steam-deck/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- x
- discord
- foro

## Qué se cuenta

- **En una frase (quien lo usa):** el modelo grande no cabe en la GPU de una Steam Deck y en CPU tarda casi una hora; el pequeño hace el definitivo en unos 4 minutos.
- **En una frase (técnico):** FLUX.3 pide 5862 MB frente a un margen de 5350 MB en la GPU y en CPU tarda 59 min a 1280×640 y 16 pasos; el modelo pequeño tarda 229 s a 8 pasos.
- **Estado:** en desarrollo

## Hechos comprobados

| Dato | Fuente |
|---|---|
| FLUX.3 en la GPU no arranca: «need 5862.40 MB device / 5350.40 MB budget» (falla a los 12-13 s) | `docs/registros/contenido/r3-borrador.md:14` y `:19-20` |
| Su grafo va en un solo segmento que no se trocea | `docs/registros/contenido/r3-borrador.md:20-21` |
| En CPU, a 1280×640 y 16 pasos: 59 min (3524 s); RAM libre mínima 3133 MB (unos 3 GB) | `docs/registros/contenido/r3-borrador.md:29` y `:32-33` |
| Unas 15 veces el definitivo del modelo pequeño, que tarda 229 s (228-230 s, 8 pasos, 1280×640) | `docs/registros/contenido/r3-borrador.md:13` y `:32-33` |
| Subir el tope de memoria de vídeo llegó a bloquear la Deck; el generador lleva protecciones de memoria propias | `docs/adr/0001-servicio-local-independiente.md:5-7` |
| La Steam Deck es la máquina de referencia | `README.md:6` |
| Las rondas reales en la Deck siguen abiertas; todo es trabajo en curso | `docs/difusion/propuestas/2026-11-02.md` (P8, notas del conjunto) |

## Imágenes

Una fila por cada archivo de `medios/` que se usa (`.webp` para X y Discord, `.png` para LinkedIn, `.pdf` para un
carrusel de LinkedIn). El texto alternativo describe lo que se ve de la pieza, con el formato `es: texto / en: text`.
El primer idioma de `Idiomas:` usa `medios/<n>.webp`; otro idioma puede tener su propia imagen
`medios/<n>.<idioma>.webp` (fuente `<n>.<idioma>.html`), con su fila y el texto alternativo en ese idioma.

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/tarjeta.webp` | es: tarjeta con el titular «Un modelo grande no cabe en la Deck» y tres cifras: 5862 MB pedidos en la GPU, 59 min en CPU y 229 s con el modelo pequeño / en: card with the headline "The big model does not fit on the Deck" and three figures: 5862 MB asked for on the GPU, 59 min on CPU and 229 s with the small model | x, discord, foro |
| `medios/tarjeta.en.webp` | es: versión en inglés de la tarjeta, con las mismas tres cifras / en: English version of the card with the same three figures | x, discord, foro |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P8 de `docs/difusion/propuestas/2026-11-02.md`; trabajo de F2.10 (rondas en la Deck), en curso, sin fusionar a la rama principal.
- Canal «foro» sustituye a Reddit: no hay normas de subreddit.
- La fuente compara con el banco de otro proyecto; en los textos no se nombra.
- Los 5862 MB y 5350 MB son del mensaje de error con el tope de VRAM de la ronda (2 GB); la tarjeta los presenta como «pedido» y «margen».

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
