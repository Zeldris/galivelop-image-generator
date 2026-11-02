# Ficha: revisiones con IA, en cifras (2026-11-02)

La fuente de todo lo que se publica de esta pieza. Lo que no esté aquí, con su fuente, no sale en los canales.
Carpeta de la pieza: `docs/difusion/2026-11-02/05-retro-revision-ia/` (NN = número de la pieza del día).

Idiomas: es, en

## Canales

- x
- linkedin
- foro

## Qué se cuenta

- **En una frase (quien lo usa):** Una fase hecha con agentes de código: la revisión con IA dio 24 hallazgos, se arreglaron 14, y una prueba a mano encontró lo que las revisiones no vieron.
- **En una frase (técnico):** Datos de proceso de una fase: hallazgos de la revisión del diff, arreglos, llamadas de la sesión principal, contexto medio, subagentes y tokens; y los fallos que se escaparon y se convirtieron en tests.
- **Estado:** fusionado en la rama principal el 2026-10-25 (la fase del núcleo); el motor real sigue en desarrollo

## Hechos comprobados

| Dato | Fuente |
|---|---|
| La revisión de la fase dio 24 hallazgos, 14 arreglados y 12 leves apuntados en la bitácora | `docs/registros/retro-2026-10-25-f1.md:3-4` |
| En la sesión principal: 77 llamadas y contexto medio de 109k; 20 subagentes y 13,4 M de tokens | `docs/registros/retro-2026-10-25-f1.md:3-4` |
| Un archivo que el ciclo completo dejaba en el repo del proyecto lo encontró una prueba a mano, no las revisiones; un test comprueba ahora la lista exacta de archivos y falla con la entrega anterior | `docs/registros/retro-2026-10-25-f1.md:16-18` |
| Las revisiones no vieron cuatro códigos de error sin texto; un test exige ahora texto en es y en para cada código | `docs/registros/retro-2026-10-25-f1.md:14-15` |
| Se limpia el contexto al cerrar cada paso si la sesión principal pasa de ~120k; el contrato de cada fase lo escribe un subagente y la principal revisa su diff | `docs/registros/retro-2026-10-25-f1.md:10-13` |
| La fase del núcleo se fusionó en la rama principal el 2026-10-25 | `git log` (commit `021806c`, 2026-10-25) |

## Imágenes

Una fila por cada archivo de `medios/` que se usa (`.webp` para X y Discord, `.png` para LinkedIn, `.pdf` para un
carrusel de LinkedIn). El texto alternativo describe lo que se ve de la pieza, con el formato `es: texto / en: text`.
El primer idioma de `Idiomas:` usa `medios/<n>.webp`; otro idioma puede tener su propia imagen
`medios/<n>.<idioma>.webp` (fuente `<n>.<idioma>.html`), con su fila y el texto alternativo en ese idioma.

| Imagen | Texto alternativo | Canales |
|---|---|---|
| `medios/metricas.webp` | es: Tarjeta de métricas con la cifra 24 (hallazgos en la revisión con IA) y tres barras: 24 hallazgos, 14 arreglados y 12 leves apuntados en la bitácora. / en: Metrics card with the figure 24 (findings in the AI review) and three bars: 24 findings, 14 fixed and 12 minor ones logged. | x, foro |
| `medios/metricas.en.webp` | es: Tarjeta de métricas en inglés con la cifra 24 y tres barras: 24 hallazgos, 14 arreglados y 12 leves. / en: Metrics card with the figure 24 (findings in the AI review) and three bars: 24 findings, 14 fixed and 12 minor ones logged. | x, foro |
| `medios/metricas.png` | es: Tarjeta de métricas con la cifra 24 (hallazgos en la revisión con IA) y tres barras: 24 hallazgos, 14 arreglados y 12 leves apuntados en la bitácora. / en: Metrics card with the figure 24 (findings in the AI review) and three bars: 24 findings, 14 fixed and 12 minor ones logged. | linkedin |
| `medios/metricas.en.png` | es: Tarjeta de métricas en inglés con la cifra 24 y tres barras: 24 hallazgos, 14 arreglados y 12 leves. / en: Metrics card with the figure 24 (findings in the AI review) and three bars: 24 findings, 14 fixed and 12 minor ones logged. | linkedin |

## Uso interno

Lo que sirve al equipo y no se publica: ids de tareas, ramas, PRs y notas. Nada de esto va en los canales.

- Propuesta P5 de `docs/difusion/propuestas/2026-11-02.md`; origen: retro de F1 (sesión 38762d2d), solo la parte de datos.
- Nota: 14 arreglados + 12 leves suman 26, no 24; la fuente no explica la diferencia (se publica cada cifra por separado, sin sumarlas).
- «Cuatro códigos de error sin texto» y los cambios (limpiar contexto, contrato por subagente) vienen de R1, O1 y O2 de la retro.
- Sin repo enlazado (privado, sin licencia, `README.md:110`). El hallazgo del archivo que quedaba es R2.

## Publicado

| Canal | Idioma | Fecha | Enlace |
|---|---|---|---|
