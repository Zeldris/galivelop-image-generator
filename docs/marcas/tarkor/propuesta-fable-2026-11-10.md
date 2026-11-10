# Tarkor — propuesta de hoja de estilo con más impacto (Fable, 2026-11-10)

Propuesta de dirección de arte sobre `peticiones.md` (hoja actual, §1-§6 y decisiones D1-D7), los dos logos de
referencia de `examples/tarkor/logos/`, la hoja de bocetos `piloto/tarkor/flux-01-emblema.png` (q148-q155; elegido
q154, luego q150 y q153) y el `@theme` de `World-Maker-Fantasy/frontend/src/index.css`. No genera nada ni toca
código: todo lo de aquí se aplica editando `peticiones.md`, `galivelop-images.json` y, por propuesta, el CSS del
juego. La dirección «lápiz de fantasía» (r7) queda archivada y no se mezcla.

Vetos que respeta (biblia §1, §6, §7): sin luna, sin violeta/púrpura, sin humanos ni rostros, sin pólvora, sin
«AAA genérico» (cromados, destellos sin oficio), sin letras pintadas por el modelo, nada del canon reservado.

## 1. Diagnóstico

- La hoja actual acierta en lo estructural: «la madera sostiene, el oro remata», el canto de oro por CSS para que el
  mosaico cierre (D1), la estrella de cuatro puntas como único remate, el fondo verde para recorte y el orden de
  trabajo (#1 como referencia de estilo). Nada de eso se cambia.
- Los bocetos FLUX no son el emblema de los logos: el aro salió **de madera con remaches**, no de oro tallado; las
  puntas salieron **ocho y de cristal azul** (el logo tiene cuatro estrellas de oro); la semilla es un disco agrietado,
  no seis gajos; y la luz es un **destello de lente** que tapa la piedra y las órbitas. Leído a 32 px, q154 es «una
  rueda de barco con pinchos azules», no la semilla rota.
- Causas en el prompt: «golden light pouring from its core» y «glowing» piden un fogonazo; «faceted blue crystal
  #4aa8d8» en el bloque común se aplica a lo primero que encuentra (las puntas); el bloque común es largo (120
  palabras de adjetivos) y klein pondera lo primero y lo último; y la hoja no tiene **ningún hex de piedra**, así
  que la semilla sale del gris que toque.
- Lo que resta impacto al conjunto: no hay un glifo firma que sobreviva a 16 px; el oro, el cristal y el brillo
  compiten por el mismo papel (el acento); y las piezas de marca (og, cabeceras) no tienen un escenario propio: el
  impacto de los logos viene del **oro sobre noche índigo**, y la hoja solo tiene madera.

## 2. Mejoras de impacto

**M1 · Glifo firma: la semilla-asterisco.** La semilla partida en seis gajos se reduce a un glifo geométrico: disco
con **tres cortes que pasan por el centro** (seis gajos) y una **estrella de cuatro puntas** en el cruce; alrededor,
un aro con cuatro puntas cardinales. A 16 px queda «aro + asterisco + punto»: se reconoce en favicon, cursor de
carga, viñeta de lista y sello. Es el mismo dibujo que el emblema completo, no otro logo. Vectorial, no sale de FLUX.
Regla: todo lo que mida menos de 64 px usa el glifo; de 128 px en adelante, el emblema pintado. Riesgo: ninguno con
klein (no interviene); el riesgo es dibujarlo sin la misma geometría que el emblema: se fija primero el SVG y el
prompt del emblema describe ese SVG.

**M2 · Una sola fuente de luz, y es la grieta.** El brillo se **confina a las juntas** entre gajos; las caras de la
piedra siguen oscuras y mates. Nada de rayos, nada de fogonazo. Así la piedra se lee y el oro no compite. En prompt,
se sustituye «golden light pouring from its core» por:
> the six wedges are dark matte cracked stone; between the wedges run thin seams of molten gold light; the stone
> faces stay dark and fully readable; the light is narrow and contained, no rays, no flare, no haze

Si aun así tapa, se pide en dos pasadas: el emblema **mate** (sin luz) y una segunda pasada img2img 0,25-0,3 con la
frase de las juntas, y se mezclan en «pantalla» en la hoja de contactos; o se pinta la luz en el SVG. Riesgo klein:
medio; «molten» puede fundir la piedra. Alternativa de palabra: «hairline cracks filled with glowing gold».

**M3 · Disciplina del cristal: el cristal es campo o gema, nunca remate.** El azul no toca el aro ni las puntas. En
el emblema es el **campo oscuro verde-azul tras los gajos** (`#2f6b7a` → `#1f4a55`); en la interfaz, una gema por
pieza como máximo. El bloque común deja de nombrar el cristal (se pide solo en la pieza que lo lleva) y el emblema
dice explícitamente:
> the ring and its four points are solid old gold with no gems; inside the ring, a dark teal faceted crystal field
Proporción: cristal ≤ 10 % del área de cualquier pieza; en el emblema completo, solo el campo. Riesgo klein: bajo;
quitarlo del bloque común es lo que más efecto tiene.

**M4 · Cuatro puntas cardinales, no ocho.** La silueta del emblema es «círculo con cuatro puntas largas» (una
estrella-brújula), la de los logos. Las cuatro puntas diagonales cortas del logo del emblema dorado se permiten
**solo** de 256 px en adelante, y más cortas que las cardinales (≤ 40 %). Esa silueta es distinta de un sol, de una
rueda y de la gema del Portal. Prompt:
> exactly four long points at top, bottom, left and right, nothing between them
Riesgo klein: alto (los conteos): se generan 8-10 semillas y se elige por silueta, y la versión final se vectoriza
sobre la mejor; el SVG garantiza las cuatro.

**M5 · Tres valores, no cinco.** Toda pieza se compone con tres escalones de luminosidad: **fondo** oscuro (madera,
hierro, noche: L < 20), **cuerpo** medio (oro viejo y piedra: L 35-60) y **luz** (bisel claro, estrella, junta: L >
85) en menos del 5 % del área. Entre el oro y el fondo siempre hay **un filo de bronce oscuro** (`#5a3a14`) de 1-2 px
para que la pieza no se funda con la madera. Comprobación: la hoja de contactos se mira a 32 px en escala de grises;
lo que no se lee ahí se repite. Prompt (va en el bloque común): `a thin dark bronze outline separates the gold from
the background`. Riesgo klein: bajo.

**M6 · Oro con oficio: pátina en el hueco, pulido en el filo.** El desgaste tiene lógica: la suciedad se queda en las
hendiduras y los cantos vivos se pulen con el uso. Nada de arañazos repartidos ni «scratches» aleatorios. Prompt:
> old gold with dark patina settled in the recesses and bright worn edges on the high ridges, chiselled stone-like
> relief
Para la madera: `oil-finished dark wood, grain raised, no gloss`. Riesgo klein: bajo; es lo que mejor hace.

**M7 · Escenario de marca: noche índigo.** Dentro del juego manda la madera. Fuera (og, cabeceras de redes, Steam,
pantalla de carga, portada del instalador), el fondo es la **noche índigo con el cinturón de polvo** de los logos
(`#0f1428` → `#1a2140`, polvo `#4aa8d8`/`#a8d8f0` al 30 %). El oro sobre índigo es el contraste complementario que da
el impacto de las referencias; sobre madera, el oro es cálido sobre cálido y pierde la mitad. La madera entra en esas
piezas como **banda inferior o marco** (un tercio como mucho), nunca como fondo entero. Sin luna, sin violeta: el
índigo se pide como `deep indigo blue, slightly green-leaning` para que klein no derive a púrpura. Riesgo klein: medio
(deriva a violeta): si pasa, se baja la saturación del hex en el prompt (`#182038`), no se cede en la regla.

**M8 · Mismo origen para todo: el emblema es la semilla.** El medallón (#16), el icono del instalador, el avatar, el
sello y las insignias salen de **img2img del emblema elegido** (fuerza 0,35-0,45), no de prompts sueltos; los
pictogramas (#11-#15, #17) comparten un **pedestal común**: un hueco circular de hierro de 0,8 del lado, con el motivo
de oro encima. La fuerza 0,35-0,45 conserva composición y luz y cambia el motivo. Se guarda la semilla y el prompt del
emblema en `galivelop-images.json` como `reference` del proyecto. Riesgo klein: bajo; es el camino que ya hace el
#16.

**M9 · Verde limpio.** En los bocetos la pieza proyecta sombra sobre el verde y el verde rebota en el metal: el
recorte sale sucio. Se pide `the object floats on a perfectly flat untouched green background, lit evenly, with no
cast shadow and no reflection of the green on the metal`; la sombra, si se quiere, se pone en CSS (`drop-shadow`).
Riesgo klein: medio; el `fuzz` del recorte se mide en la primera pieza y se apunta.

**M10 · Bloque común corto y por materiales.** Klein obedece mejor a 50-60 palabras concretas que a 120 de
adjetivos. El bloque nuevo (§4) nombra materiales, luz y acabado en cuatro frases y saca de él el cristal (M3), el
brillo (M2) y la semilla (M8), que se piden solo donde van. Las frases de «AAA» («painterly realism, rich colour,
volume and weight, solid and tactile») se reducen a una: `physically plausible materials`. Riesgo: ninguno; se
comprueba en #1 y #2 con la misma semilla que q154 para ver la diferencia.

## 3. Paleta revisada

Se conservan **todos** los tokens del `@theme` real; se ajustan los propuestos (*) y se añaden los que faltaban (piedra,
oro de pátina, noche profunda). Proporción de superficie por pieza: **60 fondo / 30 cuerpo / 10 luz y acento**, con
el acento frío dentro del 10 y el brillo dentro del 5.

| Rol | Token / hex | Uso | Proporción |
| --- | --- | --- | --- |
| Fondo de página, hendiduras | `wood-950` `#1b130c` · `iron-900` `#0e0b08` | lo más oscuro de la interfaz; sombra del oro | 60 (con la fila siguiente) |
| Tablón, hierro de mando | `wood-800` `#332415` · `wood-700` `#46311d` · `iron-800` `#171310` | paneles, cabecera, pedestal de pictogramas | — |
| Noche de marca * | `night-950` `#0f1428` · `night-900` `#1a2140` | fondo de og, cabeceras, Steam, carga (M7); nunca dentro del juego | 60 en piezas de marca |
| Piedra de la semilla * (nuevo) | `stone-700` `#3a342d` · `stone-500` `#6b6257` | gajos de la semilla, relieve tallado, sello | 30 (con oro) |
| Oro de pátina * (nuevo) | `gold-700` `#7a5a1e` | la cara en sombra del oro, entre cuerpo y bronce; sin él el oro salta a amarillo | — |
| Oro viejo, cuerpo * | `gold-500` `#b8862b` | metal del aro, letras del wordmark, cantos | — |
| Bronce oscuro, filo * | `gold-900` `#5a3a14` | contorno de 1-2 px que separa oro de fondo (M5); tinta del logo sobre claro | — |
| Oro claro, bisel * | `gold-300` `#f2c45a` | aristas con luz rasante | 10 |
| Núcleo de luz * (ajustado) | `gold-100` `#ffe9a8` | solo el cruce de la estrella y el centro de la junta; `#ffd66b` pasa a halo | ≤ 5 |
| Cristal de campo * (ajustado) | `crystal-deep` `#1f4a55` → `#2f6b7a` | campo tras los gajos del emblema; fondo de gema | ≤ 10 |
| Cristal de interfaz | `accent-500` `#4aa8d8` · `accent-300` `#a8d8f0` | gema, filete, destello de la estrella **en la interfaz**; polvo del cielo | ≤ 10 |
| Acero, musgo, peligro, coste, misión | `accent2-*`, `moss-*`, `danger-*`, `cost-*`, `quest-*` | solo semánticos; no son oro: `cost`/`quest` nunca sustituyen a `gold-*` | — |
| Hueso | `wood-200` `#e3cba8` · `wood-100` `#f1e4d0` | texto; dado; pieza clara del logo | texto |
| Arcilla | `#E0703A` | solo **tierra de Berig** en el #4 y en paisajes; deja de ser acento de marca | — |

Por qué los ajustes: `#ffd66b` como núcleo salía naranja-amarillo plano (q149, q151); un núcleo casi blanco con halo
`#ffd66b` es lo que tienen los dos logos. El campo de cristal baja a `#1f4a55` porque `#2f6b7a` en área grande tira
a turquesa y se come al oro (q148). La piedra no tenía hex: `#3a342d`/`#6b6257` son los medidos en los gajos del
logo «La semilla rota». La arcilla se saca de la marca porque la dirección anterior la tenía como único acento y
mezclarla con el oro da tres acentos.

## 4. Bloque común y negativo reescritos

Bloque común (se antepone a cada prompt; 58 palabras):

> Epic fantasy game asset. Materials: aged dark wood planks with raised grain in #332415 and #46311d, dark forged
> iron in #171310, old carved gold in #b8862b with dark patina #7a5a1e in the recesses and bright worn edges in
> #f2c45a, dark cracked stone in #3a342d. Warm raking light from the upper left, deep cool shadows in every groove.
> A thin dark bronze outline separates gold from background. Physically plausible materials, crisp edges, high
> contrast, no haze.

Qué sale del bloque y entra solo en la pieza que lo lleva: el cristal (`faceted crystal field in #1f4a55` o `one
small gem of blue crystal #4aa8d8`), la luz de la semilla (frase de M2), la estrella (`a small four-pointed star,
white-gold #ffe9a8 core with a soft golden halo`), la noche (`deep indigo blue night #1a2140, slightly green-leaning,
a slanted belt of glowing pale dust`).

Negativo (para cuando gimg tenga campo o para sd-cli; klein no lo usa, por eso todo lo importante está en positivo):

> text, letters, words, watermark, signature, people, face, hands, creature, cartoon, flat vector, clipart, blurry,
> lens flare, light rays, glow haze, chrome, neon, purple, violet, pink, moon, sun disc, cast shadow, cropped,
> tilted, perspective view

## 5. Sistema de logo

Geometría común (fija el SVG, y el prompt del emblema la describe): círculo de radio 100; aro de grosor 14; cuatro
puntas cardinales que salen 36 más allá del aro; disco interior de radio 58 (la semilla) con tres cortes por el centro
a 0°, 60° y 120° de anchura 6; estrella de cuatro puntas en el cruce, alta 28 y ancha 16 (vertical, como en la O del
logo). Luz desde arriba-izquierda a 45°.

| Pieza | Descripción | Mínimo | Origen |
| --- | --- | --- | --- |
| **Emblema completo** | Aro de oro tallado con cuatro puntas, campo de cristal oscuro, semilla de piedra en seis gajos con juntas de luz, dos anillos finos de energía inclinados, estrella en el cruce | 128 px | Boceto FLUX (prompt abajo) → vectorizado a mano en SVG respetando la geometría común; el PNG 1024² elegido sirve de icono del instalador y de referencia img2img (M8) |
| **Emblema simplificado** (favicon) | Aro + cuatro puntas + disco con tres cortes + estrella (M1). Dos tintas: `gold-500` sobre `wood-950`; a 16 px, los cortes miden 1 px y la estrella es un rombo de 3×5 | 16 px (16, 32, 48, 64) | Vectorial directo; `favicon.svg` y PNG 32/16 con `rsvg-convert` |
| **Monograma T** | La T del logo: barra alta con los extremos en espina vueltos hacia arriba, fuste que acaba en punta; dentro del aro simplificado (sin semilla) para avatar; sola para viñeta | 24 px sola · 64 px en aro | Vectorial directo, dibujada sobre la T de la referencia; no se pide a FLUX |
| **Wordmark «TARKOR»** | Base **Cinzel 800** (variable `wght`, ya empaquetada en el juego) pasada a trazos y retocada: remates alargados en espina (≈ 8 % de la altura de versal), T con la barra en cuernos, K con pierna larga que corta la línea base, **O sustituida por el aro simplificado con la estrella**, R con pierna en espina. Dos acabados: **plano** (una tinta) y **tallado** (degradado `gold-300`→`gold-700`, bisel con `feSpecularLighting`, filo `gold-900`, como ya hace `tarkor-b-lockup.svg`) | 20 px de altura de versal (plano) · 40 px (tallado) | Vectorial; FLUX nunca pinta letras. La referencia se mira, no se calca |
| **Lockup horizontal** | Emblema a la izquierda, wordmark a la derecha; altura de versal = 0,45 del diámetro del emblema (con puntas); hueco = 0,25 del diámetro | 160 px de ancho | Vectorial (compone emblema + wordmark) |
| **Lockup vertical** | Emblema arriba, wordmark debajo centrado, con el filete-separador de estrella (#9) entre ambos opcional; ancho del wordmark = 1,6 del diámetro | 96 px de ancho | Vectorial |
| **Sobre oscuro** | Oro tallado sobre `wood-950` o `night-900`: el principal | — | — |
| **Sobre claro / monocromo** | Una tinta `gold-900` `#5a3a14` sobre hueso `wood-100`; monocromo en hierro `#221c16`; invertido en hueso sobre oscuro para impresión. Sin degradados ni brillo: la silueta debe bastar | — | Vectorial; el mismo SVG con `fill` cambiado |
| **Margen libre** | La altura de la T del wordmark por cada lado; el emblema nunca se estira, rota ni lleva sombra en la interfaz | — | Regla |

Prompt del boceto del emblema completo (tras el bloque común; sustituye al de #1):

> A circular emblem seen straight on, centred, floating on a perfectly flat untouched bright green background, lit
> evenly, no cast shadow. A thick ring of old carved gold with chiselled relief and exactly four long gold points at
> top, bottom, left and right, nothing between them; the ring and its points are solid gold with no gems. Inside the
> ring, a dark teal faceted crystal field in #1f4a55. At the centre, a round seed of dark matte cracked stone in
> #3a342d split by three straight cuts into six equal wedges; between the wedges run thin seams of molten gold light
> with a white-gold #ffe9a8 core; the stone faces stay dark and fully readable; the light is narrow and contained, no
> rays, no flare, no haze. Two thin rings of golden light orbit the seed at an angle without covering it. Symmetric
> game emblem, 15 percent empty margin on every side.

Semillas: 8-10; criterio de elección: silueta a 32 px en gris (M5), piedra legible, cuatro puntas. Si en 10 ninguna
tiene seis gajos, se elige por aro y luz y los gajos se dibujan en el SVG: el PNG es boceto, no el logo final.

## 6. Catálogo de elementos que faltan

Perfiles nuevos para `galivelop-images.json`: `avatar` 1024×1024, `cabecera` 1536×512, `carga` 1280×704, `capsula`
1024×576, `marco` 1280×704. Lo «vectorial» sale del sistema de logo (§5) y de los tokens, sin FLUX. Los fondos de
marca usan el escenario de noche (M7).

| Id | Pieza | Medidas | Perfil | Prioridad | Prompt (tras el bloque común) o «vectorial» |
| --- | --- | --- | --- | --- | --- |
| E1 | **Avatar** redondo (X, Discord, GitHub, itch) | 512² y 256² PNG, recorte circular | `avatar` 1024² | alta | img2img 0,35 del emblema elegido: `the emblem fills the frame, behind it a deep indigo blue night #1a2140 fading to #0f1428 at the edges, a faint belt of pale glowing dust crossing behind the ring`. A 48 px (lista de Discord) se usa el simplificado: vectorial |
| E2 | **Cabecera de X** (1500×500) y **banner de Discord** (960×540, `object-cover`) | 1536×512 PNG | `cabecera` 1536×512 | alta | `Wide night sky of deep indigo blue #1a2140, slightly green-leaning, near black #0f1428 at the top, a slanted belt of glowing pale dust in #4aa8d8 and #a8d8f0, a few small four-pointed stars with white-gold cores, jagged dark rock spires and a distant castle of thin towers along the bottom edge in #0e0b08, a band of aged dark wood planks with a thin bevelled gold strip across the bottom tenth, the right two thirds calm and empty`. El lockup horizontal se compone en SVG sobre el tercio izquierdo |
| E3 | **og:image** (sustituye a la plantilla r7 de `examples/tarkor`) | 1200×630 | `og` existente | alta | misma escena que E2 con `the lower half calmer and emptier`; lockup vertical compuesto a la izquierda, lema en Inter a la derecha |
| E4 | **Steam: capsule header** 460×215, **small** 231×87, **main** 616×353, **vertical** 374×448 | se derivan de una | `capsula` 1024×576 (+ 768×896 para la vertical) | media (alta si hay fecha de ficha) | E2 recentrada: `the emblem's night sky, the belt of dust rising from the lower left to the upper right, the centre calm`; el logo se compone en vectorial por tamaño (small lleva solo el wordmark plano) |
| E5 | **Steam library hero** 3840×1240 + **logo** 1280×720 PNG alfa | 1536×512 generado y escalado ×2,5 con img2img por mitades si hace falta | `cabecera` | baja | mismo prompt que E2 sin la banda de madera; el logo de biblioteca es el lockup vertical vectorial |
| E6 | **Pantalla de carga** (juego e instalador) | 1280×704 PNG + barra | `carga` 1280×704 | alta | `A night view from a high ridge: deep indigo blue sky with the belt of glowing dust, dark rock spires, a long timber palisade with banners on a far hill, one campfire, the lower quarter a band of dark forged iron with a thin gold strip`; sobre el hierro, el emblema simplificado girando (CSS) y la barra E7 |
| E7 | **Barra de progreso** (carga, instalador) | pista 1024×32, relleno 1024×32, cabeza 64² | `tira` 1024×128 ×2 | alta | pista: `a long horizontal groove carved in dark forged iron with a thin bevelled gold rim`; relleno: `a long horizontal bar of molten gold light with a white-gold core and golden halo, flat ends`; cabeza: la estrella de #9 recortada |
| E8 | **Separador vertical** (entre riel y contenido) | 128×1024 → 64×1024 | `tira` girada (1024×128 generado y rotado) | media | el #9 rotado 90° por CSS; no se genera |
| E9 | **Sello de cera** con el glifo (fin de partida, documento, «hecho») | 512² → 96² y 48² | `icono` 512² | media | `A round wax seal of dark red-brown wax #5a1e14 pressed with the seed-and-star emblem in low relief, the relief catching golden raking light, on a flat untouched green background, no cast shadow` |
| E10 | **Insignia «alpha» / «en desarrollo»** y **de versión** | 512×256 → 160×80 y 96×48 | `banda` 1024×256 recortada | alta | `A small hanging banner of aged dark wood with an iron rim and a thin gold strip, a square plate of dark iron at its centre, empty, on a flat untouched green background`; el texto («ALPHA», «v0.4») va en Cinzel por CSS/SVG, nunca pintado |
| E11 | **Marco de retrato** (personaje, compañero) | 512² → 96² y 192² (9-slice) | `icono` 512² | media | `A square frame of old carved gold with chiselled relief, a small gold four-pointed star at each corner, iron rivets at the midpoints, the inside empty and filled with the same flat green, outside also flat green`; variante redonda para el medallón (#16) |
| E12 | **Plantilla de captura** (marco para capturas en redes y README) | 1280×704 con hueco 16:9 | `marco` 1280×704 | media | `A rectangular frame of aged dark wood planks with an inner rim of dark iron and a thin bevelled gold edge, four gold corner ornaments, the inside empty and filled with flat bright green`; el lockup pequeño y la insignia E10 se componen en vectorial |
| E13 | **Botón** (normal, hover, pulsado; 9-slice) | 512×192 ×3 → 128×48 | `banda` 1024×256 recortada | media | img2img 0,3 entre estados: `a horizontal button plate of aged dark wood with a dark iron rim and a thin gold strip along the top edge` · hover: `the gold strip brighter and a faint golden glow inside the rim` · pulsado: `the plate darker and recessed, the gold strip dim`. El texto va en Cinzel por CSS |
| E14 | **Icono de aplicación** (instalador `icon.png` 512² y `fuente.png` 1024²) | 1024², 512², 256², 128² | `emblema` | alta | el emblema completo elegido (#1) sobre disco de `night-950` con el aro ocupando el 80 %; de 64 px hacia abajo, el simplificado vectorial (D3) |
| E15 | **Cursor** | 32² y 16² | — | baja | solo si el juego decide cursor propio: puntero de hueso con filo de oro, vectorial; no merece FLUX. Recomiendo no hacerlo ahora |
| E16 | **Viñeta de lista y punto de notificación** | 16² | — | alta | el glifo simplificado sin aro (asterisco + estrella) en `gold-500`; vectorial |
| E17 | **Tooltip / globo** (fondo 9-slice) | 512×256 → 128×64 | `banda` | baja | `a small plate of dark forged iron with a thin gold rim, flat, on a flat untouched green background`; o solo CSS con `gold-700` de borde (recomendado) |
| E18 | **Hoja de contactos de marca** (una lámina con emblema, lockups, paleta, texturas) | 1536×640 compuesta | — | media | vectorial/compuesta con `compose`; sirve para enseñar la marca y para comprobar coherencia (M8) |

Cambios a las piezas #1-#18 existentes (solo los que mejoran):

- **#1 emblema:** prompt nuevo de §5 (M2, M3, M4, M9). Es el cambio que arrastra a todos los demás.
- **#6 cielo:** añadir `slightly green-leaning` al índigo y `#0f1428` arriba (M7); quitar «tiny floating crystal
  shards» (klein los pinta como brillantina sobre todo el cielo).
- **#8 esquina:** son dos brazos de oro; el `.corner-bracket` real es acero `accent2`. Hacer dos variantes: oro
  (modales de personaje) y acero (paneles «del mundo»), misma pieza recoloreada en HSL.
- **#9 separador:** la estrella del centro pasa a oro con núcleo blanco-oro; el cristal azul solo como gema `.gem`
  aparte (M3). Así el filete vale también fuera del juego.
- **#10 ranura:** quitar «a tiny four-pointed star at each corner» (a 44 px son cuatro manchas); una estrella arriba
  al centro o ninguna.
- **#11-#15, #17 pictogramas:** plantilla con el pedestal común de M8: `set in a shallow round recess of dark forged
  iron that fills 80 percent of the frame`; motivo de oro «con una sola silueta gruesa». Y se decide una altura de
  motivo: 60 % del hueco.
- **#16 medallón:** img2img del emblema a 0,4 (ya previsto); el borde pasa a E11 redondo para que sea la misma pieza.
- **#2, #3, #4, #5, #7, #12, #13, #14:** bien como están.
- **#18:** fuera (D7), sin cambio.

## 7. Tipografía

- **Wordmark:** Cinzel 800 modificada a trazos (§5). Razón: la referencia es una serif tallada de proporciones
  clásicas con remates en espina; Cinzel ya tiene esa estructura (inscripcional, versales), la fuente ya viaja con el
  juego y el título de `Home.tsx` y el logo serán la misma familia. Alternativa si se quiere más fiereza: **Cinzel
  Decorative** (OFL, misma autora) como base de T, K y R y Cinzel 800 para el resto; no la recomiendo entera porque a
  20 px los rasgos se cierran.
- **Títulos de interfaz y piezas:** Cinzel 700 (como hoy); para el titular de héroe (Home, pantalla de carga, og)
  Cinzel **900** con `letter-spacing: 0.08em` y relleno de oro (`background-clip: text` con `gold-300`→`gold-700`) y
  un `text-shadow: 0 1px 0 #5a3a14`. La variable ya trae 900: no se añade archivo.
- **Texto:** Inter 400/500 como hoy; eyebrow en Inter 500 mayúsculas con tracking 0,3 em. **Datos:** Cascadia Code.
  Nada cambia.
- **Convivencia:** el oro solo en el wordmark y en el titular de héroe; el resto de títulos en hueso `wood-100`. Un
  solo elemento de oro tipográfico por pantalla.
- **Nunca:** letras pintadas por FLUX, ni New Rocker/Metamorphous/Almendra (r7 archivada).

## 8. Propuestas a la interfaz del juego (solo propuesta; se entrega desde `docs/propuestas/`)

Tokens nuevos en el `@theme` de `index.css`, con el mismo criterio que `danger`/`cost` (fijos, no tematizables):

```css
/* Oro tallado de la marca (logos 2026-11-10): remata, nunca sostiene */
--color-gold-100: #ffe9a8;  /* núcleo de luz: estrella, junta */
--color-gold-300: #f2c45a;  /* bisel con luz */
--color-gold-500: #b8862b;  /* cuerpo del metal */
--color-gold-700: #7a5a1e;  /* pátina, cara en sombra */
--color-gold-900: #5a3a14;  /* filo, contorno, tinta sobre claro */
/* Piedra de la Semilla */
--color-stone-500: #6b6257;
--color-stone-700: #3a342d;
/* Noche de marca (fuera del juego y en .crystal-sky) */
--color-night-900: #1a2140;
--color-night-950: #0f1428;
--color-crystal-deep: #1f4a55;  /* campo del emblema; fondo de gema */
```

Clases que se benefician:

- `.plank-panel`: `border-color: var(--color-gold-900)` en el panel activo o seleccionado (hoy `iron-700` siempre);
  el canto de oro de D1 vive aquí, no en la textura.
- `.iron-band`: una línea de 1 px `gold-700` en el borde inferior (`box-shadow: inset 0 -1px 0`), que es la tira de
  oro del #5 sin depender de la imagen.
- `.gem`: montura: `box-shadow: 0 0 0 1px var(--color-gold-700), 0 0 8px …`; la gema sigue siendo `accent`.
- `.corner-bracket`: variante `.corner-bracket-gold` con `border-color: gold-700` para los modales de personaje; la
  de acero queda para «el mundo».
- `.crystal-sky`: base `linear-gradient(180deg, var(--color-night-950), var(--color-night-900) 50%, var(--color-iron-900))`
  en lugar de `#0d2230` y la mezcla de `accent-600`: es el cielo de los logos y sigue sin luna ni violeta.
- `.accent-hairline`: hermana `.gold-hairline` para el separador bajo el título de `Home.tsx`.
- `.skill-slot`: `border: 1px solid var(--color-gold-900)` y, con imagen #10, `border-image`.
- Título de `Home.tsx`: clase `.title-gold` (Cinzel 900, relleno de oro, sombra `gold-900`), un solo uso por pantalla.
- `favicon.svg`: el emblema simplificado (§5) sustituye al rayo violeta; `index.html` gana `<link rel="icon">` y
  `<meta property="og:image">` (E3).

## 9. Decisiones para la persona

1. **Escenario de marca (M7):** ¿noche índigo con cinturón de polvo como fondo de todo lo que está fuera del juego?
   Recomendación: sí; dentro del juego sigue la madera. **Aprobada por la persona, 2026-11-10.**
2. **Cuatro puntas o cuatro más cuatro (M4):** recomendación: cuatro cardinales en todo; las diagonales solo en el
   emblema de 256 px en adelante, y más cortas. **Aprobada por la persona, 2026-11-10.**
3. **Campo del emblema:** cristal oscuro `#1f4a55` (logo) o el azul `accent-500` de la interfaz. Recomendación: el
   oscuro; el azul vivo queda como gema y destello dentro del juego. **Aprobada por la persona, 2026-11-10.**
4. **Luz de la semilla (M2):** horneada en el boceto o en dos capas (mate + luz). Recomendación: dos capas; la luz se
   controla en el SVG y el boceto se elige por piedra y oro. **Aprobada por la persona, 2026-11-10.**
5. **Base del wordmark (§7):** Cinzel 800 modificada o dibujo a mano desde la referencia. Recomendación: Cinzel 800
   modificada; coherencia con el juego y la mitad de trabajo. **Aprobada por la persona, 2026-11-10.**
6. **Arcilla fuera de la marca:** recomendación: sí; queda como tierra de Berig en texturas y paisajes. **Aprobada por la
   persona, 2026-11-10.**
7. **Steam (E4-E5) ahora o cuando haya ficha:** recomendación: solo el `capsule header` y `main` ahora (salen de E2);
   el resto cuando exista la ficha. **Aprobada por la persona, 2026-11-10.**
8. **Avatar (E1):** emblema sobre noche o monograma T. Recomendación: emblema completo de 64 px en adelante y el
   simplificado por debajo; la T solo como viñeta y sello. **Aprobada por la persona, 2026-11-10.**
9. **Cursor (E15):** recomendación: no ahora. **Aprobada por la persona, 2026-11-10.**
10. **Tokens al juego (§8):** ¿se propone el bloque entero de `gold`/`stone`/`night` o solo `gold-500/700/900`?
    Recomendación: el bloque entero, una sola propuesta, para que `.crystal-sky` y el título puedan cambiar a la vez.
    **Aprobada por la persona, 2026-11-10.**
