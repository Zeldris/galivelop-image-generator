# Tarkor — biblia de estilo

**Dirección aprobada por la persona el 2026-11-10:** la de los dos PNG de `examples/tarkor/logos/` (anillo de oro tallado,
Semilla de piedra con juntas de luz, estrella de cuatro puntas), desarrollada en
[`propuesta-fable-2026-11-10.md`](propuesta-fable-2026-11-10.md) (§9: diez decisiones aprobadas). **r7** («lápiz de
fantasía», New Rocker, arcilla, Semilla de hierro) queda archivada en [`hoja.md`](hoja.md), sección «Historia»; su texto
anterior está en git (`ef94330`). Marca creada desde cero (decisión de la persona, 2026-10-26); lo que sigue sin marca
viene del repo del juego, World-Maker-Fantasy (WMF) `3537d84`, o del Portal `aa76b34`; rutas en la sección 10. Molde y
reglas comunes: [../README.md](../README.md). Las piezas concretas y sus prompts están en [`peticiones.md`](peticiones.md).

> **Vigencia (2026-11-12).** Las reglas con medida están en [`hoja.md`](hoja.md) §16, la cobertura por tipo de
> contenido en §17 y el estado de los repos en §18 (el juego, `main` `3a10a3fa` y UX-40 en `c858a150`; el
> Instalador, `main` `5631e77b` y su pedido en `34d2bb27`). De esta biblia ya no vale: en §4, que los SVG no existan
> y se dibujen a mano (existen desde el 2026-11-10 en `logos/`, generados con `gimg brand system`; nada se dibuja a
> mano); en §7, el negativo y el img2img del #1 (el emblema se compone desde el SVG, ningún modelo lo pinta); en §8,
> el estado de `01-emblema.json`; en §9, los perfiles «por declarar» (hay 23 en
> `examples/tarkor/galivelop-images.json`); en §10, los commits `3537d84` y `ce9f33a`.

## 1. Esencia

- **Qué es:** RPG narrativo de fantasía con IA local. Se juega en Berig, continente de Helek Sirik («Origen Azul»).
  «Tarkor» es también la última y más sabia de las 13 Semillas, que se fue y volvió «frío y oscuro» (`genesis.md`).
- **Lema:** «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas.»
- **Para quién:** quien juega rol narrativo y quiere IA en su máquina, sin cuentas; la Steam Deck es el objetivo.
- **Valores y ética:** privado por diseño (sin cuentas, telemetría ni conexión); «el motor decide, la IA narra»; mundo
  artesanal con causa física para todo; voz de difusión cercana, concreta y honesta, sin vender.
- **Nunca se muestra:** lo reservado del canon (qué sabe Tarkor, la Entidad, la luz morada, el Reino Nabierus, la
  Ciudad Hundida, el Archivo Cegado, el muro de obsidiana); luna; humanos; pólvora; Vaelira; interfaz de juego falsa;
  fechas o promesas; «AAA genérico» (destellos, cromados, armaduras brillantes). El símbolo no presenta a Tarkor como
  héroe ni como villano: como mucho insinúa la ambigüedad (fidelidad y ruptura).
- **Idea de marca:** «la madera sostiene, el oro remata». La madera y el hierro del juego son el cuerpo; el oro tallado
  de los logos es el remate (bordes, estrella, juntas de luz), nunca el fondo.

## 2. Paleta

Base «madera + hierro» del juego (`index.css`, decisión nº 6) más los tonos de los logos (propuesta §3). Proporción
**60/30/10**: madera e hierro 60 %, oro y piedra 30 %, luz y cristal 10 % (brillo `gold-100` ≤ 5 %, cristal ≤ 10 %).

| Rol | Token | Hex | Uso |
| --- | --- | --- | --- |
| Madera 950 / hierro 900 | `wood-950` / `iron-900` | `#1b130c` / `#0e0b08` | fondo de pieza oscura dentro del juego; siluetas de roca y castillo |
| Madera 800 / 700 | `wood-800` / `wood-700` | `#332415` / `#46311d` | tablón y su veta: el cuerpo de todo |
| Hierro 800 | `iron-800` | `#171310` | aros, remaches, pedestales de los pictogramas, pista de la barra |
| Noche 950 / 900 | `night-950` / `night-900` | `#0f1428` / `#1a2140` | fondo de pieza oscura **fuera del juego** (avatar, cabecera, og, Steam, icono); dentro, solo `.crystal-sky` y la pantalla de carga |
| Piedra 700 / 500 | `stone-700` / `stone-500` | `#3a342d` / `#6b6257` | la Semilla: gajos mates, pedestal de piedra |
| Oro 900 | `gold-900` | `#5a3a14` | filo, contorno de 1-2 px, tinta del logo sobre fondo claro |
| Oro 700 | `gold-700` | `#7a5a1e` | pátina, cara en sombra, bordes finos de interfaz |
| Oro 500 | `gold-500` | `#b8862b` | cuerpo del metal; logo a una tinta sobre oscuro |
| Oro 300 | `gold-300` | `#f2c45a` | bisel con luz |
| Oro 100 | `gold-100` | `#ffe9a8` | núcleo de luz: estrella, juntas de la Semilla (halo `#ffd66b` solo alrededor de un núcleo) |
| Cristal oscuro | `crystal-deep` | `#1f4a55` (claro `#2f6b7a`) | campo del emblema; fondo de gema |
| Cristal (juego) | `accent-500` / `accent-300` | `#4aa8d8` / `#a8d8f0` | gema pequeña; cinturón de polvo de la noche |
| Acero | `accent2` | `#8a9aa8` / `#52626f` | esquina de acero, texto secundario |
| Madera 200 / 100 (hueso) | `wood-200` / `wood-100` | `#e3cba8` / `#f1e4d0` | texto sobre oscuro; fondo de pieza clara |
| Musgo, peligro, coste, misión | `moss-*`, `danger-*`, `cost-*`, `quest-*` | del CSS | solo semánticos dentro del juego; nunca en marca |

- **Combinaciones:** pieza oscura de marca: `night-900` → `night-950` + oro (logo, estrella) + texto hueso; pieza
  oscura dentro del juego: `wood-950`/`wood-800` + filo `gold-900` + texto hueso; pieza clara: hueso `#f1e4d0` + logo
  en `gold-900` + texto hierro `#221c16`; sobre imagen: velo `#221c16:0.45` y texto hueso, sin banda.
- **Prohibidos:** negro `#000` y blanco `#fff` puros; morado/violeta (luz reservada); rosa; neón; cromo; oro como fondo
  o como relleno grande; cristal como superficie (solo campo del emblema o gema); más de un acento de color por pieza;
  degradados fuera del oro tallado (`gold-300` → `gold-700`), la gema y el cielo nocturno.
- **Acento (aprobado el 2026-11-10, decisión 6):** el oro tallado es el acento de marca; **la arcilla `#E0703A` sale**
  de la marca (sigue siendo la tierra de Berig en los paisajes y en #4 de `peticiones.md`, y el acento con que el
  Portal presenta a Tarkor hasta que ese repo lo cambie). El cristal `#4aa8d8` queda dentro del juego (gema, filetes)
  y como cinturón de polvo de la noche. Razones: los dos PNG aprobados son oro sobre noche; el oro no choca con el
  celeste del Portal ni con el azul del workflow, y oro, madera, hierro y piedra son una sola familia de materiales.
  Nunca oro y arcilla en la misma pieza.

## 3. Tipografía

- **Wordmark:** «TARKOR» en Cinzel **800** pasada a trazos y modificada (propuesta §7): remates en punta de ≈ 8 % de
  la altura de la mayúscula, la barra de la T con cuernos, la K con pierna larga, la O como anillo simplificado con la
  estrella, la R con pierna en punta. Plana (`gold-500` sobre oscuro, `gold-900` sobre claro) desde 20 px de altura de
  mayúscula; tallada (degradado `gold-300` → `gold-700`, `feSpecularLighting`, filo `gold-900`) desde 40 px.
- **Cinzel** (OFL, empaquetada en el juego) en títulos: **700** en los títulos de interfaz y de las piezas; **900** solo
  en el titular héroe (Home del juego, og), con `letter-spacing: 0.08em`, relleno de oro (`background-clip: text`,
  `gold-300` → `gold-700`) y `text-shadow: 0 1px 0 #5a3a14`.
- **Inter** en texto: 400 en el subtítulo y el lema, con opacidad 0,82 (regla de toda la familia); 500 en el
  **eyebrow**, en mayúsculas con tracking 0,3 em, como en la Home del juego (`Home.tsx`: `text-xs tracking-[0.3em]
  uppercase`, sin `font-serif`: es Inter, no Cinzel). Cascadia Code en datos (solo en el juego).
- **El oro en texto solo en el wordmark y en el titular héroe**; el resto, hueso sobre oscuro o hierro sobre claro.
- **Nunca:** letras pintadas por el modelo; New Rocker, Metamorphous ni Almendra (r7). Reserva: `serif`.

## 4. Logo

Sistema de la propuesta §5, derivado de los dos PNG de `examples/tarkor/logos/` (la referencia aprobada). Los SVG
**existen desde el 2026-11-10** en `docs/marcas/tarkor/logos/` (`tarkor-emblema.svg`, `-simple`, `-mono`,
`tarkor-wordmark.svg`, `tarkor-lockup-h.svg`, `tarkor-lockup-v.svg`), generados con `gimg brand system`: nada se
dibuja a mano (corregido el 2026-11-12). Los `tarkor-a/b/c/d.svg` y sus lockups de ahí son historia (r7 y anteriores).

| Pieza | Archivo previsto | Qué es | Mínimo |
| --- | --- | --- | --- |
| Emblema completo | `tarkor-emblema.svg`; PNG 1024² (= #1 elegido) | anillo de oro tallado (ancho 14 sobre círculo r 100), cuatro puntas cardinales (36 más allá del anillo), campo de cristal oscuro `#1f4a55`, disco de piedra r 58 con tres cortes de 6 a 0°/60°/120° (seis gajos) y juntas de luz, estrella 28×16 vertical en el cruce; luz a 45° desde arriba-izquierda | 128 px |
| Emblema simplificado / favicon | `tarkor-emblema-simple.svg` + PNG 64/48/32/16 | dos tintas, `gold-500` sobre `wood-950`: anillo, cuatro puntas, seis gajos, estrella; a 16 px los cortes son de 1 px y la estrella un rombo 3×5 | 16 px |
| Glifo | `tarkor-glifo.svg` | el centro sin anillo (seis gajos + estrella) en `gold-500`; viñeta, punto de lista, separador | 12 px |
| Monograma T | `tarkor-monograma.svg` | la T del wordmark dentro del anillo | 24 px (64 px con relieve) |
| Wordmark | `tarkor-wordmark.svg` | «TARKOR» Cinzel 800 modificada (sección 3); plana o tallada | 20 px / 40 px de mayúscula |
| Lockup horizontal | `tarkor-lockup-h.svg` | emblema + wordmark a la derecha; mayúscula = 0,45 del diámetro; hueco 0,25 | 160 px de ancho |
| Lockup vertical | `tarkor-lockup-v.svg` | emblema sobre wordmark (ancho 1,6 diámetros); el separador #9 entre ambos | 96 px de ancho |

- **Variantes:** oscura (oro sobre `wood-950` o `night-900`); clara (`gold-900` sobre `wood-100`); monocroma (hierro
  `#221c16` sobre claro, hueso sobre oscuro). Dentro del juego, el fondo es madera; fuera, noche (decisión 1).
- **Puntas:** exactamente cuatro, cardinales; las diagonales solo a 256 px o más y un 40 % más cortas (decisión 2).
- **Luz de la Semilla:** dos capas, núcleo `gold-100` y halo; juntas finas, la piedra siempre legible (decisión 4).
- **Reglas:** margen libre = altura de la T del wordmark; nunca estirado, rotado, con sombra ni con brillo añadido; el
  símbolo va con el wordmark o solo (esquina, avatar, favicon, icono); el texto del lockup siempre a trazos.
- **Dónde:** favicon del juego (`frontend/public/favicon.svg`, hoy un rayo violeta ajeno a la marca), icono del
  Instalador (hoy un rombo azul), avatar y cabeceras de redes, og:image, Steam, pantalla de carga, medallón #16.

## 5. Forma e iconografía

- **Radios:** baldosa `rx` 30/128 (familia); paneles 12 px; remaches redondos; gema con esquinas vivas; anillo y
  medallón circulares, ranuras y marcos cuadrados con bisel.
- **Línea:** silueta rellena antes que contorno; contorno bronce `gold-900` de 1-2 px entre oro y fondo (M5); trazos
  de 3,5-6/128; filetes de 1 px que se desvanecen; cada pieza de oro con tres valores (pátina, cuerpo, bisel).
- **Lenguaje:** materia tallada y forjada (madera veteada al aceite sin brillo, hierro negro, piedra agrietada mate,
  oro con pátina en los huecos, cristal facetado solo como campo o gema); una sola luz rasante desde arriba-izquierda
  con sombras frías en cada hendidura (M2); simetría de emblema (cuatro puntas, seis gajos) y simetría rota en los
  paisajes. Nada de 3D de plástico, destellos, rayos, niebla ni cromo. Los pictogramas, sobre un pedestal redondo de
  hierro (M8): una forma gruesa de oro al 60 % del hueco.

## 6. Voz y frases

- **Tono:** épico y trágico en el mundo; cercano, concreto y honesto al contar el proyecto; una idea por mensaje.
- **Campo semántico:** mundo que sigue, Semilla, Origen Azul, madera, hierro, cristal, llanura, puente, clan, motor,
  local. Fuera: luna, magia sin causa, héroe elegido, épica de tráiler.
- **Lema:** «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas.»
- **Variaciones [P]:** «El mundo sigue aunque tú te detengas.» · «Deja la partida. El mundo sigue.»
- **Ganchos [P]:** «Lo que no hagas, lo hará otro.» · «Madera, hierro y cristal. Y un mundo que no te espera.»
- **Cierres [P]:** «Juega en local. Nadie mira.» · «En desarrollo, a la vista.»

## 7. Estilo de imagen (FLUX)

- **Dos familias:** (a) **piezas de marca e interfaz** (emblema, marcos, pictogramas, texturas, cielos de marca) con el
  bloque común de `peticiones.md` §2 (materiales y luz, 58 palabras) y sus módulos (cristal, luz de la Semilla, estrella,
  noche, madera); (b) **paisajes** de Berig (banner, cuadrado, vertical, cabecera de paisaje) con el preámbulo de
  `mundo.json`, donde la arcilla sigue siendo la tierra.
- **Sí:** oro tallado con tres valores y pátina; piedra mate agrietada; madera veteada; una luz rasante y sombras
  frías; noche índigo `#1a2140` tirando a verde, casi negro arriba, con el cinturón de polvo en `#4aa8d8`/`#a8d8f0` y
  pocas estrellas de cuatro puntas con núcleo `#ffe9a8`; siluetas de agujas de roca y de un castillo de torres finas
  en `#0e0b08`; en paisajes, huella pequeña (empalizadas, pasarelas, estandartes, tótems, una hoguera).
- **No:** texto, personajes, rostros, manos, criaturas, interfaz, oscuridad total, cielo de otro mundo, tráiler AAA,
  destellos, rayos, niebla luminosa, cromo, neón, esquirlas de cristal flotando, sombra arrojada en los recortes,
  perspectiva (todo de frente).
- **Motivos:** la Semilla rota y la estrella (emblema, medallón, sello, glifo); el cielo nocturno con su cinturón de
  polvo (avatar, cabecera, og, Steam, carga, #6); Agujas Imán y crestas de arena imán, empalizada de troncos de Telda,
  obelisco goirnte en los paisajes; Pilares Rotos ya en la portada del Portal (no repetir en el og).
- **Vetadas** (`mundo.json`): moon/moonlit/moonlight, crystal dust, heavens, scar/wound/gash, negaciones (`no`,
  `without`...), nombres propios, humanos, pólvora; y de la marca: `purple`, `violet`, `like` y **`sun`** (pinta el disco: se
  dice la dirección, no la fuente). En las piezas de marca el negativo de `peticiones.md` §2 lleva además las negaciones
  que FLUX sí admite como negativo (moon, sun disc, purple, violet, pink, lens flare, light rays, glow haze...).
- **Zona reservada:** un tercio izquierdo liso (og, banner); la **mitad** izquierda en `header`; la mitad inferior en `square` y
  `portrait` (el prompt pide esa mitad libre, como la caja del 48 %). Una sola zona por perfil, la misma en prompt, plantilla
  y medida. En E2/E3 (cabecera y og), los dos tercios derechos en calma y la mitad inferior más vacía.
- **Recortes:** las piezas con transparencia se generan sobre verde plano `#00ff00` («perfectly flat untouched bright
  green background, lit evenly, no cast shadow») y entran con la transparencia de gimg (D6 de `peticiones.md`).
- **El emblema manda (M8):** todo lo que lleve la Semilla sale por img2img del #1 elegido (fuerza 0,35-0,45), para que
  sea el mismo en avatar, icono, sello y medallón.

## 8. Prompts

| Archivo / pieza | Estado |
| --- | --- |
| `peticiones.md` §2 bloque común + negativo | **vigente** (2026-11-10): materiales y luz, módulos por pieza |
| `peticiones.md` #1 emblema | **vigente**: prompt de la propuesta §5; 8-10 semillas; elección por silueta a 32 px. `examples/tarkor/orders/ui/01-emblema.json` lleva aún el prompt anterior (`5503a04`) y se rehace |
| `peticiones.md` #2-#17 y E1-E18 | vigentes; #18 fuera (D7) |
| `examples/tarkor/plantillas/og.svg` + `compose` del perfil `og` | **r7, se rehace con E3**: lockup vertical a la izquierda, lema en Inter a la derecha, fuentes Cinzel e Inter |
| `examples/tarkor/prompts/og.txt` | r1 (`5d0178c`): técnico sí, persona **no**; histórico |
| `examples/tarkor/prompts/r2-*.txt`, `estilo.txt`, `r5-*.txt` | r2-r5, paisajes con acento arcilla; históricos: nombran «sun» (vetada), «natural muted colours», «lower third». Sus medidas siguen valiendo como medidas de lo que eran (contraste, paleta, YAVG) |
| `piloto/tarkor/flux-01-emblema.png`, `piloto/portal-marca/tarkor/intentos/` | ronda FLUX del 2026-11-10 con el prompt anterior (q154, q150, q153): el brillo tapaba la piedra; es lo que corrige M2 |

Plantilla para una pieza de marca nueva: bloque común de `peticiones.md` §2 → módulos que lleve (cristal, luz de la
Semilla, estrella, noche, madera) → la pieza («A ... seen straight on, centred, floating on a perfectly flat untouched
bright green background») → materiales con hex → «15 percent empty margin on every side» → negativo. Entre 60 y 160
palabras después del bloque común, en afirmativo (las negaciones van al negativo), con `[recorte]` si lleva fondo verde.

Plantilla para un paisaje: preámbulo de `mundo.json` (noche con cinturón de polvo, día o atardecer) → encuadre con la
zona reservada → sujeto y región con su luz (`regiones.*.luz`) → «Style: cinematic matte painting, rich natural colour,
subtle filmic grade. Mood: wild, quiet, lived-in.» → «The image is completely textless.» Entre 120 y 320 palabras, sin
negaciones ni comparaciones. Objetivo de luminosidad de la marca: el de la portada (YAVG 105-150, SATAVG 18-32) en los
paisajes; las piezas nocturnas de marca (E1-E6) son más oscuras por definición y se miden aparte.

## 9. Formatos y piezas

Perfiles de `examples/tarkor/galivelop-images.json`: `banner` (1600×640), `og` (1200×630), `social`, `square`
(1080×1080), `portrait` (1080×1350), `header` (**1500×500**, cabecera de X), `emblema` (1024×1024). Por declarar
(`peticiones.md` §2): `textura`, `banda`, `cielo`, `icono`, `estampa`, `tira`, `avatar`, `cabecera`, `carga`, `capsula`,
`marco`. Discord (960×540) sale de `cabecera`; LinkedIn (1584×396) aparte, cuando se pida.

Orden de trabajo (el detalle, en `peticiones.md` §5):

1. **#1 emblema** (referencia de todo) y, a mano, el sistema de logo en SVG (sección 4): favicon e icono del Instalador.
2. **Marca fuera del juego:** E1 avatar, E2 cabecera, E3 og (plantilla nueva), E4 Steam (header y main; decisión 7).
3. **Interfaz:** bloque A (fondos), #16 medallón, #10 ranura, E6 carga, E7 barra, bloque C (pictogramas), B, D y el resto de E.
4. **Paisajes** (banner, cuadrado, vertical, cabecera) con la plantilla de paisaje, cuando el Portal los pida.
5. **Hoja de contactos** (E18) y propuestas a los repos del juego y del Instalador desde `docs/propuestas/tarkor/`
   (la de la interfaz: `../../propuestas/tarkor/diseno-interfaz-2026-11-10.md`).

Entrega: `examples/tarkor/entrega/ui/<nn>-<nombre>.png` (interfaz), `entrega/marca/e<nn>-<nombre>.png` (marca),
recortes `-alpha.png`; SVG en `docs/marcas/tarkor/logos/`.

## 10. Fuentes

- WMF `3537d84` (HEAD de `claude/generador-mapas` el 2026-11-10: `3e4582dc`, sin cambios en estos archivos):
  `frontend/src/index.css` l.9-14 (fuentes), l.23-67 (madera, hierro, cristal, acero, musgo, peligro, coste, misión),
  l.167-184 (`.plank-panel`), l.216-222 (`.iron-band`), l.226-234 (`.accent-hairline`), l.246-254 (`.gem`), l.269-286
  (`.crystal-sky`), l.300-322 (`.corner-bracket`), l.324-348 (`.rivet`), l.369-388 (`.skill-slot`);
  `frontend/src/pages/Home.tsx` l.20-34 (cielo, eyebrow, título con gema y filetes); `frontend/index.html` (sin
  `<link rel="icon">` ni `og:image`); `frontend/public/favicon.svg` (rayo violeta `#863bff`, ajeno a la marca);
  `frontend/src/assets/fonts/` (Cinzel e Inter, OFL); `docs/producto/02-decisiones.md` nº 6 (madera + hierro);
  `docs/producto/tarkor-contenido-web.md` l.40 (lema), l.66 y l.76 (motor y privacidad); `docs/difusion/guia-canales.md`
  l.3-4 (voz); `docs/canon-opencode/00-nucleo.md` «Tono prohibido»; `docs/rpgtarkor/lore-mundo/genesis.md` (las
  Semillas, arco de Tarkor, «El cielo sin luna» l.146-155); `docs/rpgtarkor/lore-mundo/regiones/llanuras-del-viento-rojo.md`
  l.376-385 (Los Pilares Rotos); `docs/producto/plan-imagenes/guia-visual-mundo.md` §1-2; `image-generator/estilo/mundo.json`
  (preámbulo, vetadas).
- Instalador-WMF-Tarkor `ce9f33a`: `app/src-tauri/icons/icon.png` y `fuente.png` (rombo azul sobre disco marrón,
  `tauri.conf.json` l.34); `docs/11-diseno-del-frontal.md` l.135 (iconos de estado); `estilos.css` l.60 (`.filete`).
- Portal `aa76b34`: `src/data/proyectos/tarkor.json` l.7 (acento `#E0703A`, **pendiente de cambiar a oro `#b8862b`**
  por propuesta a ese repo); `public/proyectos/tarkor/portada.webp` (1600×640, Pilares Rotos); `public/marca/gv-logo.svg`
  (baldosa de la familia); `docs/marca.md` l.3-4 (aún «pendiente de elegir tipografía»).
- Aquí: `examples/tarkor/logos/` (los dos PNG aprobados; `tarkor-a/b-lockup.svg` son r7); `examples/tarkor/galivelop-images.json`
  (`5503a04`: perfiles, `brand.palette` y `compose` del `og` aún de r7); `propuesta-fable-2026-11-10.md` (§2 M1-M10, §3-§9);
  `peticiones.md` (piezas, prompts, decisiones D1-D7); `docs/plan.md` «Estilos por proyecto», párrafo Tarkor (paleta
  medida sobre la portada, *suposición*, de r7); `docs/records/contenido/r1-fondos.md`;
  `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` §1, §2 y §4; `docs/records/decisiones-hojas-2026-11-04.md`
  (decisiones de r7, superadas el 2026-11-10 en lo que toca a acento, tipografía y logo).
