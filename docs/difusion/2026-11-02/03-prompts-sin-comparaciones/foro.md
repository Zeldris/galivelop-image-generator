# Foro: prompts sin comparaciones

Post de foro propio: título y cuerpo en Markdown, tono técnico y cercano, hasta 10000 caracteres por idioma.

## es

**Título:** «Like distant lanterns» dibujó un farolillo: el modelo pinta lo que nombras

Una lección pequeña de las primeras pruebas con el motor real de mi generador de imágenes local (**en desarrollo**, todavía no está entregado).

El prompt era para la imagen de portada de un portal web, 1280×640, con flux2 klein 4B Q8_0, 6 pasos y 184 segundos en total. Casi todo salió bien: la mitad izquierda limpia, la rejilla de puntos en su sitio y el resplandor celeste sobre el azul noche.

Lo que falló fue lo que yo creía una forma elegante de describir:

- «like distant lanterns» dibujó un farolillo literal.
- «caustic» salió como rayos.

El modelo pinta lo que se nombra, también cuando va dentro de una comparación. No entiende «como un farolillo» como una pista de luz: ve «farolillo» y lo dibuja.

La regla que sacamos: **nada de «like …»**. Se describe la cosa directamente (el color, la forma, dónde cae la luz) en lugar de decir a qué se parece. Y no solo en este prompt: quitamos las comparaciones de todos los prompts del proyecto, incluidas otras como «art magazine» o «relay».

Es fácil de comprobar: coge un prompt tuyo, busca los «like», «as if», «reminiscent of» y mira si en la imagen aparece justo lo que usabas como ejemplo.

¿Os ha pasado algo parecido con otros modelos? Me interesa saber si es general o cosa de este.

Imagen: medios/cita.webp

## en

**Title:** "Like distant lanterns" drew a lantern: the model paints what you name

A small lesson from the first tests with the real engine of my local image generator (**work in progress**, not delivered yet).

The prompt was for the cover image of a web portal, 1280×640, with flux2 klein 4B Q8_0, 6 steps, 184 seconds in total. Most of it came out right: a clean left half, the dot grid in place and the sky-blue glow over the night blue.

What failed was what I thought was an elegant way to describe things:

- "like distant lanterns" drew a literal lantern.
- "caustic" came out as rays.

The model paints what you name, even inside a comparison. It doesn't read "like a lantern" as a hint about light: it sees "lantern" and draws it.

The rule we took from it: **no "like …"**. Describe the thing directly (the colour, the shape, where the light falls) instead of saying what it resembles. And not only in this prompt: we removed the comparisons from every prompt in the project, including others such as "art magazine" or "relay".

Easy to check: take one of your own prompts, look for "like", "as if", "reminiscent of" and see whether the image shows exactly what you used as the example.

Has anything similar happened to you with other models? I'd like to know whether it's general or specific to this one.

Imagen: medios/cita.en.webp
