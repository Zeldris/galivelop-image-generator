# Galivelop-workflow — biblia de estilo

Estado: **propuestas** (2026-10-26). El repo no tiene identidad visual; lo que hay sale del Portal. Lo marcado **[P]** lo
decide la persona. Fuentes con ruta y commit en la sección 10.

## 1. Esencia

- **Qué es:** el flujo de trabajo del taller con agentes de IA (plugin para Claude Code primero), MIT, v0.4.x; fuente
  única y versionada de sus skills, ganchos y plantillas.
- **Lema:** «Lo que no está subido no existe».
- **Para quién:** quien trabaja por relevos con agentes y no quiere perder nada entre sesiones.
- **Valores:** relevos sin pérdida, elegir bien antes de empezar, nada sin revisar llega a `main`, pocos tokens sin perder
  calidad; crédito a las fuentes (Matt Pocock, `CREDITS.md`).
- **Ética:** el humano decide y revisa; la IA ejecuta y propone. Ninguna pieza sugiere autonomía total ni «magia».
- **Nunca se muestra:** robots, cerebros luminosos, circuitos brillantes, lluvia de código, humanoides, manos de robot
  sobre teclados, chispas de IA.

## 2. Paleta

La de los siete diagramas del Portal (`gw-*.svg`) más el acento que el Portal da al proyecto.

| Rol | Hex | Uso |
|---|---|---|
| Acento del proyecto | `#3D6FD9` | logo, enlaces, nombre en el lockup, trazo de los símbolos sueltos |
| Fondo de diagramas | `#0d1b2a` | fondo de piezas oscuras; extremo oscuro del degradado de la baldosa |
| Fondo del Portal | `#06121c` | fondo alterno (fichas, redes) |
| Texto | `#eef6fb` | títulos sobre oscuro |
| Texto secundario | `#8a9bb0` | subtítulos, código, pies |
| Celeste | `#38b6e8` | líneas de luz, lo propio de galivelop en los diagramas |
| Ámbar | `#f2b34a` | el testigo del relevo; lo de Matt Pocock en los diagramas |
| Verde | `#4cc38a` | verde del check, «subido», ok |
| Rojo | `#f0716a` | rechazo del gancho, error; solo semántico, nunca decorativo |
| Blanco | `#FFFFFF` | trazo sobre la baldosa |

Combinaciones por contexto:

- **Pieza oscura (por defecto):** fondo `#0d1b2a` con rejilla tenue (`#ffffff` al 2,5 %), texto `#eef6fb`, apoyo
  `#8a9bb0`, acentos celeste, ámbar y verde en ese orden de peso.
- **Pieza clara [P]:** fondo `#f6fafd` del Portal, texto `#0a1a28`, acento `#3D6FD9`; ámbar solo en detalles pequeños.
- **Sobre imagen:** el logo en baldosa (nunca el símbolo suelto sobre fotografía) y el texto en `#eef6fb` sobre la mitad
  izquierda, que los prompts dejan vacía.
- **Prohibidos:** degradados fuera de la baldosa y del fondo radial de los diagramas; neón; rojo como decoración; mezclar
  el acento `#3D6FD9` con el celeste `#38b6e8` en el mismo texto.

## 3. Tipografía

| Uso | Familia | Peso | Tracking |
|---|---|---|---|
| Títulos de diagramas y piezas | Inter | 800 | -0,02 em |
| Subtítulos | Inter | 600 | 0 |
| Código, rutas, órdenes | DejaVu Sans Mono | 400 | 0 |
| Wordmark (lockup) | Sora | 700 | -0,03 em (como «Galivelop» en el Portal) |

- El wordmark es «Galivelop-workflow» tal cual, con guion y la W minúscula; una sola línea y un solo color.
- Alternativa **[P]**: wordmark en Inter 800, igual que los títulos de los diagramas; se descarta de partida para que el
  nombre encaje con el del Portal.

## 4. Logo

Propuestas en `logos/` (símbolo `galivelop-workflow-<letra>.svg` y su `-lockup.svg`):

| | Concepto | A 16 px |
|---|---|---|
| a | Monograma «gw» de trazo 12 en la baldosa de la familia, degradado `#3D6FD9 → #0d1b2a` | sí: baldosa azul con dos letras |
| b | Relevo: un trazo que llega y otro que sale, a distinta altura, y el testigo ámbar vertical entre los dos | regular: queda un garabato con un punto ámbar |
| c | Tres commits en línea, dos huecos y el último lleno, con la flecha de subida saliendo de él | sí la silueta; hueco/lleno se distingue desde 32 px |
| d | Sello de revisión: anillo con la marca de visto, cuyo brazo largo sale por la abertura del anillo | sí |

**Elegido (agente, delegado):** a — el monograma «gw» que la persona ya eligió en el plan.

Reglas tras elegir (valen para cualquiera):

- **Variantes:** en baldosa (avatar, favicon, sobre imagen) y suelto en `#3D6FD9` para claro y oscuro; en piezas oscuras
  el símbolo suelto puede ir en `#eef6fb`. Las propuestas b-d se llevan a la baldosa invirtiendo el trazo a blanco y el
  ámbar se mantiene.
- **Margen libre:** el grosor del trazo (12/128 del símbolo) por cada lado; la baldosa ya lo incluye.
- **Tamaño mínimo:** 16 px la baldosa, 24 px el símbolo suelto, 120 px de ancho el lockup.
- **Símbolo y wordmark:** símbolo a la izquierda, nombre a la derecha a 52/128 de alto, separación 28/128; nunca el
  nombre debajo del símbolo en menos de 160 px.
- **Prohibido:** girar, estirar, añadir sombra o brillo, cambiar el radio de la baldosa (30/128), recolorear el ámbar,
  poner el símbolo suelto sobre fotografía.

## 5. Forma e iconografía

- Baldosa `rx` 30/128; radios de 18 y 10 px en interfaz, como el Portal.
- Trazo 12/128 con remates y uniones redondos (`gv-logo.svg`); en iconos pequeños, 9/128 para anillos y nodos.
- Lenguaje: líneas de luz finas que se bifurcan y se vuelven a unir, nodos redondos, sellos circulares, testigos cortos;
  nada de flechas con punta rellena ni cajas con sombra.

## 6. Voz y frases

- **Tono:** técnico, sobrio, pragmático; dice lo que hace y lo que falta; agradece a quien enseñó.
- **Campo semántico:** relevo, bitácora, punto estable, check en verde, marca de revisión, rama protegida, subir,
  fusionar, retro, testigo.
- **Lema:** «Lo que no está subido no existe».
- **Variaciones [P]:** «Cada sesión es un relevo»; «Nada llega a main sin revisión»; «El estado vive en los archivos, no en
  la conversación» (esta sale de `AGENTS.md`).
- **Ganchos [P]:** «¿Y si la sesión se corta ahora mismo?»; «Elegir el modelo antes de empezar ahorra más que compactar».
- **Cierres [P]:** «Commit, push, bitácora. Siguiente.»; «Hecho, revisado y subido».

## 7. Estilo de imagen (FLUX)

- **Sí:** ilustración técnica abstracta sobre azul noche con rejilla tenue; líneas de luz que se bifurcan y se unen con
  nodos redondos; un testigo que pasa de una línea a la siguiente; grafos de ramas y commits; el sello de revisión; la
  mitad izquierda vacía para el texto. Trazos finos y precisos, brillo suave, fondo plano.
- **No:** personas, manos, pantallas, teclados, robots, cerebros, circuitos, lluvia de código, neón saturado, texto.
- **Motivos:** relevo, grafo de ramas, sello, cuaderno de bitácora (cerrado, sin texto legible).
- **Palabras vetadas** (el modelo pinta lo que se nombra): `robot`, `brain`, `circuit`, `code rain`, `capsule` (en r1
  salió una píldora), `like a …`, `hand`, `keyboard`, `screen`.
- **Zona reservada para texto:** la mitad izquierda en `og`, `social` y `banner`; el tercio superior en `square`.

## 8. Prompts

| Archivo | Estado |
|---|---|
| `examples/galivelop-workflow/prompts/og.txt` | **r1: sí** (veredicto de la persona pese a que las líneas invaden la mitad izquierda y «capsule» salió como píldora; palanca para r2 en `r1-fondos.md`) |
| `examples/galivelop-workflow/prompts/r2-palabras.txt` | r2, **elegida** (ahora `estilo.txt`). Misma escena de og con las palancas de r1 (líneas solo en la mitad derecha, «dash» en vez de «capsule»); paleta en palabras |
| `examples/galivelop-workflow/prompts/r2-hex.txt` | r2, descartada. Misma escena, colores en hex |
| `examples/galivelop-workflow/prompts/r2-material.txt` | r2, descartada. Misma escena, paleta en materiales y luz (pizarra azul, cristal azul, latón, jade) |
| `examples/galivelop-workflow/prompts/r5-cuadrado.txt` | r5, pendiente. Misma escena en cuadrado 1080×1080 (se genera a 1024×1024): líneas en la mitad inferior, mitad superior libre |
| `examples/galivelop-workflow/prompts/r5-vertical.txt` | r5, pendiente. Misma escena en vertical 1080×1350 (896×1152): líneas en la mitad inferior, mitad superior libre |
| `examples/galivelop-workflow/prompts/r5-cabecera.txt` | r5, pendiente. Misma escena en cabecera 1500×500 (1536×512): líneas en la mitad derecha, mitad izquierda libre |

Plantilla para uno nuevo:

> Wide abstract technical illustration on a deep dark navy background with a faint fine grid. [Motivo de la sección 7,
> en frases completas y en positivo, situado en la mitad derecha.] The left half of the frame is a plain, empty dark
> background. Style: clean minimal vector-like digital illustration, thin precise strokes, soft glow, flat dark
> background. Colours: deep navy, sky blue, amber, soft green, off-white. Mood: calm, precise, trustworthy. The image is
> completely textless.

## 9. Formatos y piezas

Perfiles de la tabla común: `social`, `og`, `square`, `banner`, `avatar`, `icon`.

Primera ronda (huecos del repo y del Portal):

1. Logo elegido y avatar 512×512 [P].
2. Social preview de GitHub 1280×640.
3. og:image 1200×630 de la ficha del Portal.
4. `square` 1080×1080 con el lema, texto compuesto (D28).
5. Banner 1600×640 del relevo.

## 10. Fuentes

| Dato | Repo y commit | Ruta |
|---|---|---|
| Qué es, versión, licencia, valores | Galivelop-workflow `56212e8` | `README.md`, `CHANGELOG.md`, `LICENSE` |
| Créditos | Galivelop-workflow `56212e8` | `CREDITS.md` |
| Lema y campo semántico | Galivelop-workflow `56212e8` | `AGENTS.md`, `templates/es/log.md` |
| Límites por red de `gw-media-content` | Galivelop-workflow `56212e8` | `skills/gw-media-content/reglas.json` |
| Acento `#3D6FD9` | Portal-Galivelop `aa76b34` | `src/data/proyectos/galivelop-workflow.json` |
| Paleta y tipografía de los diagramas | Portal-Galivelop `aa76b34` | `docs/diagramas/gw-*.svg` |
| Baldosa de la familia | Portal-Galivelop `aa76b34` | `public/marca/gv-logo.svg`, `src/components/Logo.tsx` |
| Fondos claro y oscuro del Portal | Portal-Galivelop `aa76b34` | tema (`#06121c`, `#f6fafd`, `#0a1a28`) |
| Lectura y veredicto r1 | este repo | `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md` (§2, §4), `docs/registros/contenido/r1-fondos.md` |
| Propuesta de logo del plan | este repo | `docs/plan.md`, «Estilos por proyecto», Galivelop-workflow |
