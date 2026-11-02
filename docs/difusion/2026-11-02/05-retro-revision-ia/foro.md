# Foro: Revisiones con IA, en cifras

Post de foro propio: título y cuerpo en Markdown, 10000 caracteres como mucho por idioma. Aporta algo a la comunidad
antes que promocionar. La imagen va en una línea `Imagen:`.

## es

**Título:** Una fase con agentes de código: 24 hallazgos de revisión, 14 arreglos y lo que se escapó

Hicimos una fase entera de un proyecto (un generador de imágenes local) con agentes de código y, al cerrarla, medimos el proceso. Comparto las cifras por si a alguien le sirven de referencia.

Imagen: medios/metricas.webp

### Las cifras

- La revisión completa del diff dio **24 hallazgos**: **14 se arreglaron** y **12**, leves, quedaron apuntados como pendientes en la bitácora.
- La sesión principal hizo **77 llamadas**, con un contexto medio de **109k**.
- Se repartió trabajo a **20 subagentes**, que gastaron **13,4 M de tokens**.

### Lo que la revisión no vio

- Un archivo que el ciclo completo dejaba en el repositorio del proyecto lo encontró **una prueba a mano**, no las revisiones. Ahora un test comprueba la lista exacta de archivos que queda y falla con la entrega anterior.
- Cuatro códigos de error sin texto: los tests solo miraban el código. Ahora un test exige mensaje en español y en inglés para cada uno.

### Qué cambiamos

- Limpiar el contexto al cerrar cada paso de una fase si la sesión principal pasa de unos 120k.
- Que el contrato de cada fase lo escriba un subagente y la sesión principal revise su diff.
- Convertir cada fallo que se escapa en un test.

### Qué os pregunto

¿Qué cifras medís vosotros al trabajar con agentes? ¿Y qué se os ha escapado que luego cazó una prueba a mano?

## en

**Title:** One phase with coding agents: 24 review findings, 14 fixes and what slipped through

We built a whole phase of a project (a local image generator) with coding agents and measured the process when it closed. Sharing the numbers in case they are useful as a reference.

Imagen: medios/metricas.en.webp

### The numbers

- The full review of the diff gave **24 findings**: **14 were fixed** and **12**, minor ones, were logged as pending in the project log.
- The main session made **77 calls**, with an average context of **109k**.
- Work was handed to **20 subagents**, which used **13.4 M tokens**.

### What the review missed

- A file the full cycle left in the project repository was found by **a hand test**, not by the reviews. A test now checks the exact list of files left behind and fails with the earlier delivery.
- Four error codes with no message text: the tests only looked at the code. A test now demands a message in Spanish and English for each one.

### What we changed

- Clear the context when each step of a phase closes if the main session passes about 120k.
- Have a subagent write each phase's contract and the main session review its diff.
- Turn every failure that slips through into a test.

### What I am asking

Which numbers do you track when working with agents? And what has slipped past you that a hand test then caught?
