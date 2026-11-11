# Ficha: un generador de imágenes por máquina (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/01-como-funciona/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- x
- linkedin
- discord
- foro

## Qué se cuenta

- **En una frase (quien lo usa):** Varios proyectos piden imágenes a un solo servicio local: mandas un pedido, salen varios intentos y eliges uno, con deshacer.
- **En una frase (técnico):** Servicio local por máquina (Python solo con la biblioteca estándar, stable-diffusion.cpp), con pedidos cerrados, cola persistente en disco, N intentos y como mucho una elegida.
- **Estado:** el núcleo (pedidos, intentos, elegida, cola) está fusionado en la rama principal el 2026-10-25; el motor real, la API y la interfaz están en desarrollo, no entregados

## Hechos comprobados

| Dato | Fuente |
|---|---|
| Es un servicio local por máquina que usa stable-diffusion.cpp; Python 3 solo con la biblioteca estándar | `README.md:5-7` |
| Copiarlo en cada proyecto duplicaría los modelos (19 GB en un caso real) y cada copia divergiría | `docs/adr/0001-servicio-local-independiente.md:1-9` |
| El generador no conoce el dominio de ningún proyecto; solo recibe pedidos cerrados y aplica un estilo declarado por perfil | `docs/adr/0002-generador-sin-dominio.md:1-6` |
| Un pedido tiene N intentos y como mucho una elegida; elegir otra sustituye la entrega, conserva el historial y se puede deshacer | `docs/plan.md:21` (D9) |
| Cola persistente en disco, una generación a la vez, en orden de llegada; en la Deck no caben dos a la vez | `docs/plan.md:22` (D10) |
| El pedido lo identifica una clave que pone el proyecto más el perfil; el pedido usa una semilla | `docs/plan.md:30` (D18), `docs/plan.md:118-119` |
| El núcleo funciona de extremo a extremo con un motor de pruebas de color liso; el motor real llega después | `README.md:11-13` |
| Después del motor real vienen la API HTTP y la interfaz de tres pantallas | `docs/plan.md:72-74` (F3, F4) |
| El núcleo se fusionó en la rama principal el 2026-10-25 | `git log` (commit `021806c`, 2026-10-25) |

## Imágenes

Una fila por cada archivo de `medios/` que se usa (`.webp` para X y Discord, `.png` para LinkedIn, `.pdf` para un
carrusel de LinkedIn). El texto alternativo describe lo que se ve de la pieza, con el formato `es: texto / en: text`.
El primer idioma de `Idiomas:` usa `medios/<n>.webp`; otro idioma puede tener su propia imagen
`medios/<n>.<idioma>.webp` (fuente `<n>.<idioma>.html`), con su fila y el texto alternativo en ese idioma.

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/diagrama.webp` | es: Diagrama de cinco pasos, de izquierda a derecha: un proyecto, un pedido (clave, perfil, prompt y semilla), una cola persistente, N intentos y una elegida; una flecha de vuelta dice que elegir otra sustituye la entrega y se puede deshacer. / en: Five-step diagram, left to right: a project, an order (key, profile, prompt and seed), a persistent queue, N attempts and one chosen; a return arrow says choosing another replaces the delivery and can be undone. | x, discord, foro |
| `medios/diagrama.png` | es: Diagrama de cinco pasos, de izquierda a derecha: un proyecto, un pedido (clave, perfil, prompt y semilla), una cola persistente, N intentos y una elegida; una flecha de vuelta dice que elegir otra sustituye la entrega y se puede deshacer. / en: Five-step diagram, left to right: a project, an order (key, profile, prompt and seed), a persistent queue, N attempts and one chosen; a return arrow says choosing another replaces the delivery and can be undone. | linkedin |
| `medios/diagrama.en.webp` | es: Diagrama de cinco pasos, de izquierda a derecha: un proyecto, un pedido (clave, perfil, prompt y semilla), una cola persistente, N intentos y una elegida; una flecha de vuelta dice que elegir otra sustituye la entrega y se puede deshacer. / en: Five-step diagram, left to right: a project, an order (key, profile, prompt and seed), a persistent queue, N attempts and one chosen; a return arrow says choosing another replaces the delivery and can be undone. | x, discord, foro |
| `medios/diagrama.en.png` | es: Diagrama de cinco pasos, de izquierda a derecha: un proyecto, un pedido (clave, perfil, prompt y semilla), una cola persistente, N intentos y una elegida; una flecha de vuelta dice que elegir otra sustituye la entrega y se puede deshacer. / en: Five-step diagram, left to right: a project, an order (key, profile, prompt and seed), a persistent queue, N attempts and one chosen; a return arrow says choosing another replaces the delivery and can be undone. | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P1 de `docs/difusion/propuestas/2026-11-02.md`. El motor real es F2 (en curso); el núcleo es F1, cerrado el 2026-10-25.
- Las marcas hermanas no se nombran; el caso de los 19 GB es el del proyecto piloto de migración (D7), sin nombrarlo.
- El repo es privado y sin licencia (`README.md:110`): ningún texto enlaza.

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
