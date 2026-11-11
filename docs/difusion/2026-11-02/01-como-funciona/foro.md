# Foro: Un generador de imágenes por máquina

Post de foro propio: título y cuerpo en Markdown, 10000 caracteres como mucho por idioma. Aporta algo a la comunidad
antes que promocionar. La imagen va en una línea `Imagen:`.

## es

**Título:** Un generador de imágenes local compartido por varios proyectos: cómo lo estamos diseñando

Estamos montando un generador de imágenes con IA local que **no vive dentro de ningún proyecto**: es un servicio por máquina que comparten varios. Os cuento el flujo y por qué lo planteamos así.

Imagen: medios/diagrama.webp

### El flujo

1. Un proyecto manda un **pedido**: clave (la pone el proyecto) + perfil + prompt + semilla.
2. El pedido entra en una **cola persistente en disco**: una generación a la vez, en orden de llegada.
3. Cada pedido tiene **N intentos** y **como mucho una elegida**.
4. Elegir otro intento sustituye la entrega, conserva el historial y **se puede deshacer**.

### Por qué uno por máquina

- Copiar el generador en cada proyecto duplicaría los modelos (19 GB en un caso real) y cada copia acabaría distinta.
- El generador **no conoce el dominio de ningún proyecto**: solo recibe pedidos cerrados. Construir el prompt es cosa de cada proyecto; lo único que aplica el generador es un estilo declarado por perfil, un texto fijo sin lógica.
- Una sola cola evita que dos proyectos pidan a la vez en una máquina donde no caben dos generaciones.

### Con qué está hecho

Python 3 con solo la biblioteca estándar, y stable-diffusion.cpp como motor.

### Estado

El núcleo (proyectos, pedidos, intentos, elegida, cola, línea de órdenes) funciona de extremo a extremo con un **motor de pruebas** que genera imágenes de color liso. El motor real está **en desarrollo**: todavía no es algo entregado. Después vendrán una API HTTP y una interfaz.

### Qué os pregunto

¿Compartís un generador entre proyectos o cada uno lleva el suyo? ¿Qué haríais distinto en el pedido o en el reparto de intentos y elegida?

## en

**Title:** A local image generator shared across projects: how we are designing it

We are building a local AI image generator that **does not live inside any one project**: it is one service per machine, shared by several. Here is the flow and why we chose it.

Imagen: medios/diagrama.en.webp

### The flow

1. A project sends an **order**: key (set by the project) + profile + prompt + seed.
2. The order goes into a **persistent queue on disk**: one generation at a time, in arrival order.
3. Each order has **N attempts** and **at most one chosen**.
4. Choosing another attempt replaces the delivery, keeps the history and **can be undone**.

### Why one per machine

- Copying the generator into every project would duplicate the models (19 GB in a real case) and every copy would end up different.
- The generator **knows nothing about any project's domain**: it only takes closed orders. Building the prompt is each project's job; the only thing the generator applies is a style declared per profile, a fixed text with no logic.
- A single queue stops two projects from asking at once on a machine that cannot fit two generations.

### What it is built with

Python 3 with only the standard library, and stable-diffusion.cpp as the engine.

### Status

The core (projects, orders, attempts, chosen, queue, command line) works end to end with a **test engine** that produces flat-colour images. The real engine is **in development**: it is not shipped yet. An HTTP API and an interface come after that.

### What I am asking

Do you share one generator across projects, or does each have its own? What would you do differently in the order or in how attempts and chosen work?
