# Ficha: hoja de ruta (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/10-hoja-de-ruta/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- linkedin
- discord

## Qué se cuenta

- **En una frase (quien lo usa):** El núcleo ya funciona de extremo a extremo con un motor de pruebas; ahora va el motor real, y después una API y una interfaz de tres pantallas.
- **En una frase (técnico):** Cinco etapas: esqueleto y núcleo (hechos), motor real (en desarrollo), API HTTP con arranque bajo demanda, interfaz y piloto en otro proyecto (después).
- **Estado:** el núcleo está fusionado en la rama principal el 2026-10-25; el motor real, la API, la interfaz y el piloto están en desarrollo o por hacer, no entregados

## Hechos comprobados

| Dato | Fuente |
|---|---|
| El plan se reparte en seis fases (esqueleto, núcleo, motor real, API y arranque, interfaz, piloto en otro proyecto) | `docs/plan.md:69-74` |
| El núcleo cubre proyectos, pedidos, intentos y estados, elegida con deshacer, entrega, cola persistente y línea de órdenes, todo con un motor de pruebas | `docs/plan.md:70` |
| El esqueleto trae esquemas de configuración, textos es/en y un check real | `docs/plan.md:69` |
| El motor real trae el envoltorio del motor con el perfil de máquina, catálogo de modelos, borradores, composición de texto y logo y medida de marca | `docs/plan.md:71` |
| La API HTTP y el arranque bajo demanda vienen después | `docs/plan.md:72` |
| La interfaz tiene tres pantallas, en español e inglés | `docs/plan.md:73`, `docs/plan.md:34` (D22) |
| Existe un prototipo navegable de la interfaz | `docs/interfaz/prototipo/index.html:6-7` |
| El piloto en otro proyecto trae configuración de ejemplo y guía de integración; se da por bueno cuando recibe una elegida sin copia a mano | `docs/plan.md:74` |
| El núcleo funciona de extremo a extremo con un motor de pruebas; aún no genera imágenes reales | `README.md:11-13` |
| El núcleo está en la rama principal con 282 tests | `docs/traspaso.md:13` |
| El núcleo se fusionó en la rama principal el 2026-10-25 | `git log` (commit `021806c`, 2026-10-25) |

## Imágenes

Una fila por cada archivo de `medios/` que se usa.

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/diagrama.webp` | es: Diagrama de cinco pasos, de izquierda a derecha, con una etiqueta de estado cada uno: esqueleto y núcleo (hecho), motor real (en curso), API y arranque, interfaz de tres pantallas y piloto en otro proyecto (después). Debajo, una nota: el motor de pruebas ya recorre el ciclo completo y todavía no se generan imágenes reales. / en: Five-step diagram, left to right, each with a status label: skeleton and core (done), real engine (in progress), API and startup, three-screen interface and pilot in another project (later). Below, a note: the test engine already runs the whole cycle and no real images are generated yet. | discord |
| `medios/diagrama.png` | es: Diagrama de cinco pasos, de izquierda a derecha, con una etiqueta de estado cada uno: esqueleto y núcleo (hecho), motor real (en curso), API y arranque, interfaz de tres pantallas y piloto en otro proyecto (después). Debajo, una nota: el motor de pruebas ya recorre el ciclo completo y todavía no se generan imágenes reales. / en: Five-step diagram, left to right, each with a status label: skeleton and core (done), real engine (in progress), API and startup, three-screen interface and pilot in another project (later). Below, a note: the test engine already runs the whole cycle and no real images are generated yet. | linkedin |
| `medios/diagrama.en.webp` | es: Diagrama de cinco pasos, de izquierda a derecha, con una etiqueta de estado cada uno: esqueleto y núcleo (hecho), motor real (en curso), API y arranque, interfaz de tres pantallas y piloto en otro proyecto (después). Debajo, una nota: el motor de pruebas ya recorre el ciclo completo y todavía no se generan imágenes reales. / en: Five-step diagram, left to right, each with a status label: skeleton and core (done), real engine (in progress), API and startup, three-screen interface and pilot in another project (later). Below, a note: the test engine already runs the whole cycle and no real images are generated yet. | discord |
| `medios/diagrama.en.png` | es: Diagrama de cinco pasos, de izquierda a derecha, con una etiqueta de estado cada uno: esqueleto y núcleo (hecho), motor real (en curso), API y arranque, interfaz de tres pantallas y piloto en otro proyecto (después). Debajo, una nota: el motor de pruebas ya recorre el ciclo completo y todavía no se generan imágenes reales. / en: Five-step diagram, left to right, each with a status label: skeleton and core (done), real engine (in progress), API and startup, three-screen interface and pilot in another project (later). Below, a note: the test engine already runs the whole cycle and no real images are generated yet. | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P10 de `docs/difusion/propuestas/2026-11-02.md`. Las fases del plan son F0-F5; en la imagen F0 y F1 van juntas en el paso 1. La propuesta dice «cinco fases»; el plan tiene seis, y el diagrama agrupa en cinco pasos.
- Las marcas hermanas y el proyecto del piloto no se nombran. El repo es privado y sin licencia (`README.md:110`): ningún texto enlaza.
- La propuesta cita `docs/traspaso.md:12` para los 282 tests; en el archivo está en la línea 13.
- La captura del prototipo como segunda imagen queda sin hacer: la propuesta la deja a decisión de la persona.
- Canal foro no usado en esta pieza (la propuesta pide solo discord y linkedin).

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
