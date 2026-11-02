# LinkedIn: Un generador de imágenes por máquina

800 a 1.300 caracteres (el máximo es 3.000). Las dos primeras líneas enganchan: son lo único que se ve antes de
«ver más». Reto, cómo y qué se aprendió. De 3 a 5 etiquetas al final. LinkedIn no admite WebP: la imagen es el
`.png`. Para un carrusel, cambia la línea `Imagen:` por `medios/carrusel.pdf` (y añade su fila en `ficha.md`).

## es

¿Un generador de imágenes por proyecto, o uno por máquina?
Estamos construyendo lo segundo: un servicio local que varios proyectos comparten.

El reto: cada proyecto necesita imágenes con su propia marca, pero copiar el generador en cada uno duplicaría los modelos (19 GB en un caso real) y cada copia acabaría divergiendo.

Cómo lo resolvemos:
• El proyecto manda un pedido cerrado: clave + perfil + prompt + semilla. El generador no conoce el dominio de ningún proyecto; construir el prompt es cosa de cada uno.
• Cada pedido puede tener varios intentos y como mucho una elegida. Elegir otra sustituye la entrega, y se puede deshacer.
• Una cola persistente en disco hace una generación a la vez, en orden de llegada.

Está hecho con Python y solo su biblioteca estándar, sobre stable-diffusion.cpp. El núcleo ya funciona con un motor de pruebas; el motor real está en desarrollo.

Lo que aprendimos: separar «qué se pide» de «cómo se genera» deja el servicio pequeño y reutilizable.

¿Compartís un generador entre proyectos, o cada uno tiene el suyo?

#IA #IAlocal #Python #StableDiffusion
Imagen: medios/diagrama.png

## en

One image generator per project, or one per machine?
We are building the second: a local service that several projects share.

The challenge: each project needs images in its own brand, but copying the generator into each one would duplicate the models (19 GB in a real case) and every copy would end up drifting apart.

How we solve it:
• A project sends a closed order: key + profile + prompt + seed. The generator knows nothing about any project's domain; building the prompt is each project's job.
• Each order can have several attempts and at most one chosen. Choosing another replaces the delivery, and it can be undone.
• A persistent queue on disk runs one generation at a time, in arrival order.

It is written in Python with only its standard library, on top of stable-diffusion.cpp. The core already works with a test engine; the real engine is still in development.

What we learned: separating what is asked for from how it is generated keeps the service small and reusable.

Do you share one generator across projects, or does each have its own?

#AI #LocalAI #Python #StableDiffusion
Imagen: medios/diagrama.en.png
