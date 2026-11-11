# LinkedIn: Hoja de ruta

800 a 1.300 caracteres (el máximo es 3.000). Las dos primeras líneas enganchan: son lo único que se ve antes de
«ver más». Reto, cómo y qué se aprendió. De 3 a 5 etiquetas al final. LinkedIn no admite WebP: la imagen es el
`.png`. Para un carrusel, cambia la línea `Imagen:` por `medios/carrusel.pdf` (y añade su fila en `ficha.md`).

## es

Empezar por un motor de pruebas y dejar el real para después.
Así vamos con nuestro generador de imágenes con IA local.

El reto: un servicio que varios proyectos comparten tiene que ser fiable antes de ser vistoso. Si el motor real llega primero, cada fallo de la cola o de la elección de intentos se mezcla con los de la generación.

Cómo lo ordenamos:
• Esqueleto y núcleo, hechos: pedidos, intentos, elegida con deshacer, cola en disco y línea de órdenes, sobre un motor de pruebas. 282 tests en verde.
• Motor real, en curso: borradores, composición de texto y logo, medida de marca.
• Después: API HTTP, una interfaz de tres pantallas (ya hay un prototipo navegable) y un piloto en otro proyecto.

Lo que aprendimos: con el ciclo completo probado de antemano, cambiar el motor deja de dar miedo.

Todavía no se generan imágenes reales; lo contaremos cuando pase. ¿Vosotros qué dejáis para el final: el motor o lo que lo rodea?

#IA #IAlocal #Python #Roadmap
Imagen: medios/diagrama.png

## en

Start with a test engine, leave the real one for later.
That is how we are building our local AI image generator.

The challenge: a service that several projects share has to be reliable before it is flashy. If the real engine comes first, every bug in the queue or in the attempt selection gets mixed up with generation bugs.

How we ordered it:
• Skeleton and core, done: orders, attempts, chosen with undo, on-disk queue and command line, on a test engine. 282 tests passing.
• Real engine, in progress: drafts, text and logo compositing, brand measurement.
• Later: an HTTP API, a three-screen interface (a clickable prototype already exists) and a pilot in another project.

What we learned: with the whole cycle tested up front, swapping the engine stops being scary.

No real images are generated yet; we will say so when that changes. What do you leave for last: the engine or everything around it?

#AI #LocalAI #Python #Roadmap
Imagen: medios/diagrama.en.png
