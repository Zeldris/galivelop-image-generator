# Biblias de estilo de Galivelop

Una biblia por proyecto: todo lo que hace falta para crear una pieza (imagen, logo, publicación) sin volver a leer su repo.
El molde es el kit visual de toVeriAI (`VeriNews_AI/Documentacion/v1.1/kit-visual-ia.html`, resumido en
`docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`, sección 4). Pedido de la persona del 2026-10-26: «que nos sirva como
biblia», y lo primero, varias propuestas de logo por app para elegir.

| Proyecto | Biblia | Logos | Estado |
|---|---|---|---|
| Portal Galivelop (paraguas) | [portal/biblia.md](portal/biblia.md) | `portal/logos/` | elegido **a** (alt. b) |
| toVeriAI | [toveriai/biblia.md](toveriai/biblia.md) | `toveriai/logos/` | elegido **a** (b ≤ 32 px) |
| Galivelop-workflow | [galivelop-workflow/biblia.md](galivelop-workflow/biblia.md) | `galivelop-workflow/logos/` | elegido **a** |
| Tarkor | [tarkor/biblia.md](tarkor/biblia.md) | `tarkor/logos/` | elegido **a**, a retocar |
| galivelop-image-generator | [galivelop-image-generator/biblia.md](galivelop-image-generator/biblia.md) | `galivelop-image-generator/logos/` | elegido **b** |
| galivelop-voice-generator | [galivelop-voice-generator/biblia.md](galivelop-voice-generator/biblia.md) | `galivelop-voice-generator/logos/` | elegido **a** |
| galivelop-developer | [galivelop-developer/biblia.md](galivelop-developer/biblia.md) | `galivelop-developer/logos/` | elegido **d** |

La página de revisión con todas las propuestas la genera `python3 examples/pilot/logos.py`, en `piloto/logos/index.html`
(fuera de git).

## Elegido por el agente (delegado, 2026-10-26)

La persona dejó estas decisiones en manos del agente («lo dejo en tus manos»); valen hasta que ella diga otra cosa y se
proponen a cada repo al cerrar F2 (`docs/propuestas/`).

- **Logos** (tabla de arriba), con el porqué:
  - Portal **a**: el logo de hoy simplificado, sin ruptura con lo publicado.
  - toVeriAI **a**, fiel, y **b** para favicon y ≤ 32 px, donde el abanico de hojas se empasta.
  - Galivelop-workflow **a**: el monograma «gw» que la persona ya eligió en el plan.
  - Tarkor **a**, los Pilares Rotos, el emblema aprobado en el plan; se retoca para que no se lea como una M.
  - Imágenes **b**: la más limpia a 16 px y la que cuenta «intentos y una elegida».
  - Voces **a**: la más propia; la **d** es una onda genérica.
  - Developer **d**: hace familia con «gw»; la **a** se lee como una «b».
- **Tarkor:** acento de marca arcilla `#E0703A`; el cristal `#4aa8d8` queda dentro del juego y como secundario.
- **Acentos de las herramientas:** imágenes `#8B5CF6`, voces `#D9467A` y developer `#2BB3A3`, como se propusieron.
- **toVeriAI:**
  - wordmark «toVeriAI», el del código del kit;
  - rangos IMI del kit (0-39 / 40-69 / 70-100) en las piezas;
  - la incoherencia con `marketing.html` y los PNG «VeriNews» se propone arreglar en su repo.

## Reglas de verdad

- **El repo de cada proyecto manda.** Lo que sale de su código se cita con ruta y commit; si la marca cambia allí, se
  actualiza aquí.
- Cada dato lleva su estado:
  - sin marca: sale del repo;
  - **[P]**: propuesta, pendiente de la persona;
  - *(suposición)*: se comprueba en una ronda.
- Lo que la persona elige aquí (un logo, una paleta) se propone después al repo del proyecto. Desde aquí nunca se toca
  otro repo.

## Molde de una biblia

Mismas secciones en todas, en este orden; una sección sin datos dice «no hay» y qué falta.

1. **Esencia:** qué es, lema, para quién, valores y ética, y lo que nunca se muestra.
2. **Paleta:**
   - tabla rol / hex / uso;
   - combinaciones por contexto (pieza clara, pieza oscura, sobre imagen);
   - prohibidos.
3. **Tipografía:** familias, pesos, tracking y cuál va en el wordmark.
4. **Logo:**
   - las propuestas en curso (una línea por propuesta);
   - tras elegir: variantes clara y oscura, margen libre, tamaño mínimo, cómo conviven símbolo y wordmark, y usos
     prohibidos.
5. **Forma e iconografía:** radios, grosor de línea y lenguaje de forma.
6. **Voz y frases:** tono, campo semántico, lema, variaciones, ganchos y cierres (las que no salen del repo, con [P]).
7. **Estilo de imagen** (para FLUX):
   - lo que sí y lo que no;
   - motivos;
   - palabras vetadas, porque el modelo pinta lo que se nombra, también en una comparación;
   - zona reservada para texto.
8. **Prompts:** los de `examples/<proyecto>/prompts/`, con su estado (qué ronda los aprobó), y la plantilla para uno nuevo.
9. **Formatos y piezas:** qué perfiles usa (tabla común de abajo) y la primera ronda de piezas.
10. **Fuentes:** repo, commit y rutas de cada dato.

## Común a todos

- **Familia Galivelop:** la baldosa del logo del Portal (`gv-logo.svg`: 128×128, `rx` 30, trazo blanco de 12 con remates
  redondos) es el contenedor común de los iconos de app.
  - Los proyectos con identidad propia (toVeriAI, Tarkor) pueden salirse de ella; las herramientas del taller la usan
    siempre.
- **Texto en imagen:** nunca lo genera el modelo. Los prompts acaban en «The image is completely textless.», y el texto y
  el logo los pone la composición (D28, D29).
- **Prompts FLUX:** frases completas en positivo, lo importante primero, «Style: … Mood: …» al final, sin negativo y sin
  comparaciones («like …»).

| Perfil | Destino (px) | Uso |
|---|---|---|
| `og` | 1200×630 | og:image; vista previa en LinkedIn, Discord y X |
| `social` | 1280×640 | social preview de GitHub |
| `square` | 1080×1080 | Instagram y LinkedIn |
| `portrait` | 1080×1350 | Instagram 4:5 |
| `wide` | 1200×675 | X |
| `header` | 1500×500 (X), 1584×396 (LinkedIn), 960×540 (Discord) | cabeceras |
| `banner` | 1600×640 | portada en el Portal |
| `avatar` | 512×512 | Discord, GitHub y favicon grande |
| `icon` | 180, 192 y 512 | apple-touch-icon y manifest |

## Logos: cómo se dibujan las propuestas

Cuatro propuestas por proyecto (`a`-`d`), **conceptos distintos, no variantes de color**. Cada una tiene dos archivos en
`<proyecto>/logos/`:

- **`<proyecto>-<letra>.svg`, el símbolo:**
  - `viewBox="0 0 128 128"`, sin texto;
  - se lee a 16 px (favicon) y funciona sobre fondo claro y oscuro (si no, lleva su propia baldosa).
- **`<proyecto>-<letra>-lockup.svg`:**
  - el símbolo a la izquierda y el nombre a la derecha, en horizontal, con `viewBox` de alto 128;
  - el nombre va como `<text>` con su `font-family` de la biblia y una genérica de reserva (`serif` o `sans-serif`);
  - si solo funciona sobre un fondo, lo dice en la raíz con `data-fondo="claro"` u `"oscuro"`, y la página de revisión
    lo muestra solo sobre ese;
  - al elegirse, el texto se pasa a trazos con la fuente de verdad.

Reglas del SVG:

- Código a mano, legible, sin raster, sin `filter` y sin fuentes incrustadas.
- `<title>` y un comentario de una línea con el concepto.
- Todos los `id` llevan el prefijo `<proyecto>-<letra>-`, porque la página de revisión mete todos los SVG en el mismo
  documento.
- Solo colores de la paleta de la biblia; degradados solo donde la biblia los permite (la baldosa de la familia sí;
  toVeriAI no).
- Comprobación: `rsvg-convert -w 512` y `-w 32` del símbolo, mirados, antes de entregar.

### Conceptos de partida

Cada letra es una dirección. El dibujante puede ajustar la geometría, no cambiar la idea; si una idea no funciona pequeña,
lo dice.

**Portal Galivelop** (además se muestra `portal-actual.svg`, copia literal de `gv-logo.svg`, como referencia):

- **a. GV de un trazo:** la G y la V de un único trazo continuo en la baldosa actual. Es el logo de hoy, simplificado.
- **b. Umbral:** una G que es también un arco de puerta abierta, con un punto de luz celeste dentro (el portal, el taller
  que se abre).
- **c. Luz y mar:** la G trazada por una línea de ola que se cierra en el travesaño. Galicia como luz y mar, nunca como
  postal; sin faro ni bandera literal.
- **d. Wordmark primero:** «galivelop» en minúsculas Sora 700, con el punto de la «i» como baldosa celeste `rx` proporcional.
  El símbolo es esa baldosa con una «g».

**toVeriAI** (wordmark «to·Veri·AI», Cormorant Garamond 400 con «Veri» en `#2D6A4F`; nada de «VeriNews»):

- **a. Vectorización fiel** del símbolo actual (V de dos barras + 4 hojas doradas en abanico + constelación de 12 puntos;
  sección 4 de la lectura), con los hex del kit (`#2D6A4F`, `#B5832A`) y relleno plano.
- **b. Simplificado para tamaños pequeños:** V de dos trazos curvos, uno verde y otro ámbar, con 3 puntos encima. Tiene que
  leerse a 16 px.
- **c. La verdad no es binaria:** V formada por tres estratos o tiras de tinta planas (granate `#9B2335`, ámbar, verde) que
  se rozan sin mezclarse.
- **d. Anillo de score:** un arco fino abierto (el anillo del IMI, línea ~1,3 px a escala de 512) con una V de hoja dentro.

**Galivelop-workflow** (acento `#3D6FD9`, fondo de diagramas `#0d1b2a`):

- **a. Monograma «gw»** en la baldosa de la familia, con degradado `#3D6FD9 → #0d1b2a` (lo del plan).
- **b. Relevo:** dos trazos curvos que se cruzan y se pasan un testigo corto; el testigo, en ámbar `#f2b34a`.
- **c. Lo que no está subido no existe:** tres nodos de commit en línea, los dos primeros huecos y el último lleno, con
  una flecha de subida que sale de él.
- **d. Sello de revisión:** un círculo de sello con una marca de visto dentro. El humano revisa; nada de chispa ni de magia.

**Tarkor** (Cinzel; dos paletas posibles **[P]**: la arcilla del Portal, `#E0703A`, o el cristal del juego, `#4aa8d8`,
sobre madera y hierro; las propuestas usan las dos para que la persona elija):

- **a. Los Pilares Rotos:** silueta de las torres con un puente colgante, en un trazo, en la baldosa de la familia con
  `#E0703A → #8a3b1e` (lo del plan).
- **b. La gema de la interfaz:** el rombo `.gem` en cristal `#4aa8d8` con filetes a los lados. Lockup «TARKOR» en Cinzel
  mayúsculas con tracking amplio, como el título del juego.
- **c. La Semilla:** una semilla o rombo vertical partido en dos mitades, cristal claro y hierro oscuro (fidelidad y
  ruptura). Insinúa sin resolver nada reservado; sin luz morada.
- **d. Hierro y madera:** escudo redondo de madera `#5c4126` con aro de hierro, cuatro remaches y una T forjada.

**galivelop-image-generator** (acento [P] `#8B5CF6`, en la baldosa de la familia; nada de cámara, pincel ni chispa):

- **a. La cola:** tres marcos en fila escalonada, el de delante encendido (la elegida).
- **b. Rejilla de intentos:** un marco con 2×2 celdas y una encendida.
- **c. Un marco y su vuelta:** un marco con una esquina que se dobla en flecha de deshacer (D9: elegir y deshacer).
- **d. El taller que se enciende:** un marco cuyo borde se cierra en un punto de luz (arranque bajo demanda).

**galivelop-voice-generator** (acento [P] `#D9467A`; nada de micrófono, cara, boca ni persona):

- **a. Onda que se enrosca:** una onda que se cierra en espiral de huella.
- **b. Tomas:** cinco barras de onda con una resaltada (la toma elegida).
- **c. Huella de anillos:** anillos concéntricos partidos en segmentos, que forman a la vez una huella y una onda.
- **d. Una onda en la baldosa:** una sola onda sinusoidal blanca que atraviesa la baldosa de la familia.

**galivelop-developer** (acento [P] `#2BB3A3`; nada de robot ni de cerebro):

- **a. Rama que vuelve:** un tronco con una rama corta que sale y vuelve a él por un anillo de revisión.
- **b. Tercer relevo:** tres trazos paralelos, el tercero más corto y del acento, que pasan por un anillo.
- **c. Terminal:** «›_» en la baldosa, con un trazo de la familia.
- **d. Monograma «gd»** en la baldosa, con la «d» cerrada en anillo de revisión.
