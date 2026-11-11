# LinkedIn: Revisiones con IA, en cifras

## es

¿Qué da de sí una revisión de código hecha con IA? Estos son nuestros datos de una fase.
Y también lo que se le escapó.

Estamos construyendo un generador de imágenes local y esta fase (el núcleo) la hicimos con agentes de código. Al cerrarla medimos el proceso:

• La revisión completa del diff dio 24 hallazgos: 14 se arreglaron y 12, leves, quedaron apuntados como pendientes.
• La sesión principal hizo 77 llamadas, con un contexto medio de 109k.
• Se repartió trabajo a 20 subagentes, que gastaron 13,4 M de tokens.

Lo que la revisión no vio: un archivo que el ciclo completo dejaba en el repositorio del proyecto lo encontró una prueba a mano. Desde entonces un test comprueba la lista exacta de archivos que queda, y falla con la entrega anterior. Tampoco vio cuatro códigos de error sin texto: ahora otro test exige mensaje en español y en inglés para cada código.

Lo que aprendimos: las revisiones con IA encuentran mucho, pero una prueba a mano sigue cazando lo que no mira ninguna. Y cuando algo se escapa, lo convertimos en test.

¿Qué se os ha escapado a vosotros que luego pillaron otras pruebas?

#IA #AgentesDeCódigo #RevisiónDeCódigo #Productividad
Imagen: medios/metricas.png

## en

What does an AI code review deliver? Here is our data from one phase.
And also what it missed.

We are building a local image generator, and this phase (the core) was built with coding agents. When it closed we measured the process:

• The full review of the diff gave 24 findings: 14 were fixed and 12 minor ones were logged as pending.
• The main session made 77 calls, with an average context of 109k.
• Work was handed to 20 subagents, which used 13.4 M tokens.

What the review did not see: a file the full cycle left in the project repository was found by a hand test. Since then a test checks the exact list of files left behind, and it fails with the earlier delivery. It also missed four error codes with no message text: another test now demands a message in Spanish and English for every code.

What we learned: AI reviews find a lot, but a hand test still catches what no review looks at. And when something slips through, we turn it into a test.

What has slipped past you that other tests then caught?

#AI #CodingAgents #CodeReview #Productivity
Imagen: medios/metricas.en.png
