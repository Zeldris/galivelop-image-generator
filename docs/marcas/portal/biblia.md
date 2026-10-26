# Portal Galivelop — biblia de estilo

Marca paraguas del taller. Fuente de verdad: repo `Portal-Galivelop`, commit `aa76b34` (rutas en la sección 10). Sin marca,
el dato sale del repo; **[P]** es propuesta pendiente de la persona; *(suposición)* se comprueba en una ronda.

## 1. Esencia

- **Qué es:** «Taller independiente de software. Hacemos reales los proyectos que parecen imposibles.» Gali(cia) + Develop;
  se publica en es, gl y en (gl obligatorio en cada texto).
- **Lema:** «Hacemos reales los proyectos que parecen imposibles».
- **Para quién:** quien quiera ver qué hace el taller y en qué estado real está cada proyecto (Tarkor, toVeriAI,
  Galivelop-workflow y las herramientas).
- **Valores:** cercano, humilde, honesto con el estado real; «no es un escaparate, no nos mueve el beneficio económico».
- **Líneas de trabajo:** IA local y responsable, mundos que viven solos, información verificable, del prototipo al producto,
  método con IA.
- **Nunca se muestra:** «contrata nuestros servicios», venta, promesas infladas, gráficas de crecimiento; no se dice
  «encargo» ni «de pago» (`GLOSSARY.md`, `docs/adr/0001-encargos-por-miembro.md`).

## 2. Paleta

| Rol | Hex | Uso |
|---|---|---|
| Celeste (marca) | `#1aa6df` | «Gali» del wordmark, acentos, resplandor (`--celeste`) |
| Celeste baldosa | `#2BB3EA` → `#0083c1` | degradado diagonal de la baldosa del logo; `#0083c1` es `--celeste-intenso` |
| Enlace oscuro / claro | `#5cc8f2` / `#006c9f` | enlaces en cada tema |
| Blanco | `#ffffff` | trazo del monograma, superficie clara |
| Fondo oscuro | `#06121c`, alterno `#081826` | fondo por defecto de la web |
| Superficies oscuras | `#0c1d2b`, `#11283a`; borde `#1b3447` | tarjetas y paneles |
| Texto oscuro | `#eaf4fa`, `#9fb4c4`, `#6f8799` | texto, secundario, terciario |
| Fondo claro | `#f6fafd`, alterno `#eaf4fa`; superficie `#ffffff`, `#f0f6fa`; borde `#d6e4ee` | tema claro |
| Texto claro | `#0a1a28`, `#43586a`, `#6b8193` | texto, secundario, terciario |
| Brillo | `rgb(26 166 223 / 0.22)` oscuro, `/ 0.16` claro | resplandor radial (`--brillo`) |
| Acentos de proyecto | Tarkor `#E0703A`, toVeriAI `#2F7A55`, workflow `#3D6FD9` | solo como tres puntos o tres trazos sobre el celeste |

Combinaciones:

- **Pieza oscura (la de la casa):** fondo `#06121c` + resplandor radial celeste + rejilla de puntos; texto `#eaf4fa`;
  «Gali» `#1aa6df`; logo con baldosa.
- **Pieza clara:** fondo `#f6fafd`, texto `#0a1a28`, enlaces `#006c9f`; logo con baldosa (el trazo blanco necesita la
  baldosa).
- **Sobre imagen:** solo sobre la zona reservada oscura; texto `#eaf4fa` y baldosa; nunca celeste sobre celeste.

Prohibidos: cualquier color fuera de la tabla; los acentos de proyecto como color dominante; degradados que no sean la
baldosa o el resplandor **[P]**; celeste sobre el degradado de la baldosa (no contrasta).

## 3. Tipografía

| Uso | Familia | Peso | Tracking |
|---|---|---|---|
| Títulos | Sora (`'Sora Variable', 'Sora', system-ui, sans-serif`) | 700 | -0,02 em |
| Wordmark «Gali**velop**» | Sora | 700 | -0,03 em (`Logo.tsx`) |
| Texto | Inter (`'Inter Variable', 'Inter', system-ui, sans-serif`) | 400 | normal |
| Etiquetas en mayúsculas | Inter | 400-600 | 0,04-0,16 em (`global.css`) |

El wordmark hoy es HTML, no un archivo: «Gali» en `#1aa6df` y «velop» en el color de texto del tema.

## 4. Logo

Referencia: `logos/portal-actual.svg`, copia literal de `public/marca/gv-logo.svg` (baldosa 128×128 `rx` 30, degradado
`#2BB3EA → #0083C1`, monograma G+V en trazo blanco de 12 con remates redondos).

Propuestas (`logos/portal-<letra>.svg` y `-lockup.svg`), conceptos distintos:

- **a. GV de un trazo:** travesaño, bowl, tapa y V en una sola línea blanca sobre la baldosa actual; a 16 px se lee igual
  que el logo de hoy.
- **b. Umbral:** baldosa oscura `#06121c`; la G es un arco de puerta (arco, jamba, suelo y hoja) con un punto de luz
  `#5cc8f2` dentro y su resplandor; a 16 px queda la G, la luz es un punto.
- **c. Luz y mar:** el bowl de la G es el arco de luz y el travesaño sale como una línea de ola, la superficie del mar;
  a 16 px se lee «G» con cola.
- **d. Wordmark primero:** «galivelop» en Sora 700 minúsculas con el punto de la «i» como baldosa celeste; el símbolo es la
  baldosa con una «g» de un trazo. Su lockup es el propio wordmark (no símbolo + nombre), porque la baldosa ya va en la «i».

**Elegido (agente, delegado):** a — el logo de hoy simplificado, sin ruptura con lo publicado; alternativa b.

Tras elegir **[P]**:

- Variantes: oscura (la de la web: «velop» `#eaf4fa`) y clara («velop» `#0a1a28`); la baldosa es la misma en las dos.
- Margen libre: un cuarto del lado de la baldosa. Tamaño mínimo: símbolo 16 px; wordmark 20 px de alto, por debajo solo
  el símbolo.
- Símbolo y wordmark: en horizontal, símbolo a la izquierda, separación de un cuarto del lado; nunca el wordmark sobre la
  baldosa.
- Prohibido: cambiar el degradado, quitar el radio, estirar, trazo de otro grosor, sombras o 3D, colores de proyecto en
  el monograma.

## 5. Forma e iconografía

- Radios: 18 px (`--radio`) y 10 px (`--radio-sm`); 6 px en piezas pequeñas; píldora (999 px) en chips. Baldosa del logo:
  `rx` 30 sobre 128 (23 % del lado).
- Grosor de línea: el del monograma, 12/128 (9,4 % del lado), con remates y uniones redondos; los iconos de app de la
  familia usan el mismo trazo blanco sobre la baldosa.
- Lenguaje: un trazo continuo, círculos y rectas, nada de relleno ni detalle fino; la luz como resplandor radial, no como
  destello dibujado.

## 6. Voz y frases

- **Tono:** cercano, humilde, concreto; cuenta lo hecho y lo pendiente; nunca vende.
- **Campo semántico:** taller, hacer real, proyecto, estado real, avances y pendientes, luz y mar, relevo.
- **Lema:** «Hacemos reales los proyectos que parecen imposibles».
- **Variaciones [P]:** «Un taller, no un escaparate.» · «Proyectos con sus avances y sus pendientes.» · «Software hecho en
  Galicia, en abierto.»
- **Ganchos [P]:** «Esto es lo que hay hoy.» · «Tres proyectos, un mismo taller.»
- **Cierres [P]:** «Galivelop. Un taller independiente.» · «Mira el estado real en galivelop.»

## 7. Estilo de imagen (FLUX)

- **Sí:** fondo `#06121c` con resplandor radial celeste y rejilla de puntos (así es la web); luz y materia de taller en
  abstracto (vidrio, agua, luz celeste sobre azul profundo); umbral, puerta o anillo de acceso como motivo del Portal; los
  tres proyectos como tres puntos de color; Galicia solo como luz y mar.
- **No:** gente en traje, apretones de manos, oficinas de banco de imágenes, cohetes, robots, gráficas de crecimiento,
  postal gallega (faro, bandera, gaita), orbes genéricos (r1: «limpio pero genérico, no dice portal»).
- **Motivos:** umbral que se abre, luz que entra por una puerta, ola de luz, rejilla de puntos, tres acentos.
- **Palabras vetadas:** lighthouse, flag, handshake, rocket, robot, suit, office, chart, logo, text, letters, y cualquier
  «like …» (el modelo pinta lo que se nombra).
- **Zona reservada:** la mitad o el tercio izquierdo «calm, smooth, nearly empty, softly out of focus» para wordmark y
  frase; el motivo a la derecha.

## 8. Prompts

| Archivo | Pieza | Estado |
|---|---|---|
| `examples/portal/prompts/og.txt` | og 1200×630 | r1 (`5d0178c`): **no** por la persona; orbe con tres puntos, genérico. Palanca r2: motivo propio (umbral, puerta, anillo) en vez del orbe |
| `examples/portal/prompts/r2-palabras.txt` | og, «Umbral»: escena nueva (umbral abierto del que sale luz celeste, tres puntos de color dentro), paleta en palabras | r2, pendiente |
| `examples/portal/prompts/r2-hex.txt` | misma escena, colores en hex | r2, pendiente |
| `examples/portal/prompts/r2-material.txt` | misma escena, paleta en materiales y luz (pizarra pulida, cristal grueso, arcilla, esmalte) | r2, pendiente |

Plantilla para uno nuevo: `Wide abstract <pieza> on a deep midnight navy background. <motivo del Portal en la mitad derecha,
en positivo>. A faint grid of tiny dots fades into the darkness. The left half is a calm, smooth, dark navy surface, nearly
empty and softly out of focus. Style: minimal elegant digital art, soft volumetric light, crisp and clean. Colours: deep
midnight navy, sky blue, cyan and white highlights. Mood: calm, honest, quietly ambitious. The image is completely textless.`

## 9. Formatos y piezas

Perfiles (tabla común del README): `og`, `banner`, `header` (Discord 960×540 y LinkedIn 1584×396), `avatar`, `social`.

Primera ronda: 1) og:image por proyecto (3 piezas: portada del proyecto + logo + wordmark); 2) avatar 512 y cabecera de
Discord 960×540 (solo composición); 3) banners 1600×640 de las cinco líneas de trabajo; 4) logo para fondo claro y
wordmark exportado (sale de la elección de la sección 4); 5) cabecera de LinkedIn.

Redes: Discord, LinkedIn y GitHub; no hay Instagram, X ni YouTube.

## 10. Fuentes

Repo `Portal-Galivelop`, commit `aa76b34`:

- Esencia, tono y límites: textos de la web, `GLOSSARY.md`, `docs/adr/0001-encargos-por-miembro.md`.
- Paleta, tipografías, radios y brillo: `src/estilos/global.css` (`:root`, temas oscuro y claro).
- Logo y wordmark: `public/marca/gv-logo.svg`, `src/componentes/Logo.tsx`; imágenes existentes en `public/marca/`
  (`galivelop-social.png`, `galivelop-portal.jpg`, `gv-logo-512.png`).
- Acentos de proyecto: `src/data/proyectos/*.json`.
- Resumen de lectura: `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`, secciones 2 y 4; plan: `docs/plan.md`,
  «Estilos por proyecto»; veredicto r1: `docs/registros/contenido/r1-fondos.md`.
