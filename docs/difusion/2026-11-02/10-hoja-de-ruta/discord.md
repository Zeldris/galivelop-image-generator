# Discord: Hoja de ruta

Markdown de Discord. Cada mensaje tiene menos de 2.000 caracteres; si hace falta más, se parte con una línea que
solo contenga `---`. Título, novedades, detalle técnico y qué viene. El título va con `###`: un `##` cierra la
sección del idioma.

## es

### Hoja de ruta: del núcleo a la interfaz

- **Hecho:** el núcleo (pedidos, intentos, elegida con deshacer, cola en disco, línea de órdenes) funciona de extremo a extremo con un motor de pruebas. 282 tests en verde.
- **En curso:** el motor real, con composición de texto y logo, borradores y medida de marca.
- **Después:** una API HTTP, una interfaz de tres pantallas y un piloto en otro proyecto.

Imagen: medios/diagrama.webp

---

Para ser claros: **todavía no se generan imágenes reales**. El motor de pruebas devuelve imágenes de color liso y sirve para comprobar el ciclo completo.

La interfaz ya tiene un prototipo navegable, así que el diseño de las pantallas se puede discutir antes de construirla. ¿Qué pantalla os gustaría ver primero?

## en

### Roadmap: from the core to the interface

- **Done:** the core (orders, attempts, chosen with undo, on-disk queue, command line) works end to end on a test engine. 282 tests passing.
- **In progress:** the real engine, with text and logo compositing, drafts and brand measurement.
- **Later:** an HTTP API, a three-screen interface and a pilot in another project.

Imagen: medios/diagrama.en.webp

---

To be clear: **no real images are generated yet**. The test engine returns flat-colour images and is there to check the whole cycle.

The interface already has a clickable prototype, so the screens can be discussed before they are built. Which screen would you like to see first?
