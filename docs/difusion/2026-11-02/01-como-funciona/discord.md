# Discord: Un generador de imágenes por máquina

Markdown de Discord. Cada mensaje tiene menos de 2.000 caracteres; si hace falta más, se parte con una línea que
solo contenga `---`. Título, novedades, detalle técnico y qué viene. El título va con `###`: un `##` cierra la
sección del idioma.

## es

### Un generador de imágenes por máquina, no uno por proyecto

- Varios proyectos piden imágenes a un solo servicio local.
- El pedido lleva clave + perfil + prompt + semilla.
- Salen varios intentos y tú eliges uno; elegir otra sustituye la entrega y se puede deshacer.
- Una cola en disco hace una generación a la vez.

Imagen: medios/diagrama.webp

---

Por qué uno por máquina: copiarlo en cada proyecto duplicaría los modelos (19 GB en un caso real) y cada copia divergiría. Además el generador no conoce el dominio de ningún proyecto: solo recibe pedidos cerrados.

Es Python con solo la biblioteca estándar, sobre stable-diffusion.cpp. El núcleo funciona de extremo a extremo con un motor de pruebas; lo que viene es el motor real, que está en desarrollo, y después una API HTTP y una interfaz.

## en

### One image generator per machine, not one per project

- Several projects ask a single local service for images.
- An order carries key + profile + prompt + seed.
- You get several attempts and pick one; choosing another replaces the delivery and can be undone.
- A queue on disk runs one generation at a time.

Imagen: medios/diagrama.en.webp

---

Why one per machine: copying it into every project would duplicate the models (19 GB in a real case) and every copy would drift. The generator also knows nothing about any project's domain: it only takes closed orders.

It is Python with only the standard library, on top of stable-diffusion.cpp. The core works end to end with a test engine; next comes the real engine, which is in development, and then an HTTP API and an interface.

