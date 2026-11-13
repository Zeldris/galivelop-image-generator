# Tarkor — peticiones de recursos gráficos para gimg

Hoja de pedidos para el generador local (gimg en la Steam Deck: Z-Image a 8 pasos para lo que se entrega, FLUX.2 klein solo para bocetos). Pide **solo lo que el generador
propio de Tarkor (WMF-imagenes) no produce** y que hoy en la interfaz es un emoji, un degradado CSS marcado como
provisional o un archivo de relleno. Forma tomada de la hoja del Portal (`docs/marca.md` de Portal-Galivelop,
«Recursos de imagen para el generador»). Escrita el 2026-11-10 leyendo los repos del juego en solo lectura.

## 0. Fuente

| Repo | Commit | Rama | Rutas leídas |
| --- | --- | --- | --- |
| `World-Maker-Fantasy` | `3537d84822185b5c5f04e0c70c03e4e6a1446078` (lectura del 2026-11-10; las líneas de `index.css` de las tablas son de ahí). El 2026-11-12: `main` `3a10a3fa` y UX-40 en `c858a150`, con las líneas nuevas en `hoja.md` §13 y §17 | `claude/generador-mapas`; `claude/marca-interfaz` | `frontend/src/index.css` (entero), `frontend/src/assets/fonts/fonts.css`, `frontend/public/favicon.svg`, `frontend/public/icons.svg`, `frontend/index.html`, `frontend/src/components/{Miniatura,PanelEmptyState,IconCard,Esqueleto,HealthBar,HungerBar,ThirstBar,EnergyBar,DiceRoll,SkillBarHud,SideNav,CollapsedRail,NavTabs,WorldCard,CharacterCard,GameHeader,ErrorBoundary,CombatPanel}.tsx`, `frontend/src/pages/Home.tsx`, `frontend/src/lib/{gamePhase,enciclopediaTargets}.ts`, `backend/src/services/imagePromptGenerator.ts` (l.49), `backend/src/routes/world.ts` (l.58-76, l.807) |
| `WMF-imagenes` | `735f5239adbe6409ba4a349869338fb65ece35c1` | — | `image-generator/README.md`, `image-generator/fichas/` (listado), `image-generator/interfaz/adaptador_tarkor.py` (l.1-125), `docs/producto/roadmap-imagenes.md` (extractos: bloques, IMG-37) |
| `Instalador-WMF-Tarkor` | `ce9f33aba0d2054591445ba43383678910966bc9` (2026-11-10). El 2026-11-12: `main` `5631e77b` y `34d2bb27`, con `docs/13-hoja-de-estilos-e-imagenes.md` entero (`d9d33fe`, `608661d`) | —; `claude/installer-docs-review-09e7vs` | `app/src/estilos.css` (entero), `app/src-tauri/icons/` (`icon.png` 512², `fuente.png` 1024²), `app/src-tauri/tauri.conf.json` (l.34), `docs/11-diseno-del-frontal.md` (l.135) |
| Este repo | rama `portal-marca` (2026-11-10); `agent/hojas-tarkor` (2026-11-12) | — | `docs/marcas/tarkor/biblia.md` §7-8, `hoja.md` §6-7 y §15 (antiguas: mandan los repos del juego), `examples/tarkor/galivelop-images.json`, `examples/tarkor/logos/` |

**Referencia de calidad y estilo (dato de la persona, 2026-11-10):** los dos logos de
`examples/tarkor/logos/`: `Tarkor_ La semilla rota.png` (1672×941) y `Emblema dorado y título TARKOR.png` (2172×724).
Lo que enseñan: fantasía épica AAA; letras serif talladas en **oro viejo** con textura de piedra, biseles con puntas y
filos que rematan en espina; **emblema circular de oro** con una **semilla de piedra partida en seis gajos** y luz
dorada saliendo del centro; **anillos de energía** dorados girando alrededor; **estrellas de cuatro puntas**
brillantes como remates (en los cuatro puntos cardinales del anillo, en la O del título y bajo el subtítulo); el aro
exterior deja ver un fondo de **cristal azul-verdoso** entre los gajos; fondo nocturno **azul índigo profundo** con
montañas rocosas y un castillo de agujas. Los recursos de esta hoja casan con esa estética **y** con los tokens
reales de la interfaz (madera, hierro, cristal azul). Donde chocan, está en «Dudas». **El 2026-11-10 la persona confirmó
que esa dirección es la marca** (r7 «lápiz de fantasía» queda archivada en `hoja.md`) y aprobó las diez decisiones de §9 de
[`propuesta-fable-2026-11-10.md`](propuesta-fable-2026-11-10.md): esta hoja las aplica (paleta §3, bloque común §4, logo §5,
piezas §6, tipografía §7 de la propuesta).

## 1. La estética: madera de la interfaz + oro y piedra de los logos

Precisión de la persona (2026-11-10): la estética de esta hoja es **la de los logos mezclada con la hoja actual de
la interfaz del juego**, más lo que haga falta para que todo llegue a la calidad del logo y de su fondo. En
concreto:

| Capa | De dónde viene | Qué aporta |
| --- | --- | --- |
| **Base: madera, hierro y cristal** | `World-Maker-Fantasy/frontend/src/index.css`, bloque `@theme` (l.1-60: `--color-wood-*`, `--color-iron-*`, `--color-accent-*`, `--color-accent2-*`) y sus clases `.wood-grain` l.129, `.plank-panel` l.167, `.iron-band` l.216, `.crystal-sky` l.269, `.rivet` l.324 | Todo fondo y toda superficie grande es **madera oscura con veta** (tablones `wood-800/700`, fondo `wood-950/900`) o **hierro forjado** (`iron-800/700`, con remaches). El cristal azul `accent-500` es el único acento frío. La luz de la interfaz es cálida y baja (ámbar sobre madera). |
| **Ornamento: oro tallado, piedra, semilla rota, estrellas** | `examples/tarkor/logos/Tarkor_ La semilla rota.png` y `Emblema dorado y título TARKOR.png` | Marcos, cantos, remates, emblemas y pictogramas son **oro viejo tallado** con textura de piedra, biseles vivos y puntas en espina; los remates son **estrellas de cuatro puntas** que brillan; el motivo central es la **semilla de piedra partida en seis gajos** con luz dorada saliendo del centro y **anillos de energía** alrededor. |
| **Acabado (lo que hace que llegue a la calidad del logo)** | `propuesta-fable-2026-11-10.md` §2 (M1-M10, aprobadas) | **Una sola luz** rasante desde arriba-izquierda sobre el oro y la madera; sombras frías y profundas en cada hendidura; la luz de la Semilla son **juntas finas de oro fundido** entre gajos de piedra mate, nunca un resplandor que tape la piedra (M2). El cristal azul solo como **campo** del emblema (`#1f4a55`) o como **gema** pequeña (M3); las estrellas de cuatro puntas son oro con núcleo blanco-dorado `#ffe9a8`, cuatro cardinales (M4). Cada pieza de oro con tres valores (pátina `#7a5a1e`, cuerpo `#b8862b`, bisel `#f2c45a`) y contorno bronce de 1-2 px `#5a3a14` (M5); pátina en los huecos (M6). Noche índigo `#1a2140` solo fuera del juego (M7). Grano fino, bordes nítidos, **sin niebla, sin rayos, sin destellos**. Nada plano, nada «flat vector». |

Regla de reparto: **la madera sostiene, el oro remata**. Un panel es madera con canto de oro, no un panel de oro; un
pictograma es oro y piedra sobre el hierro o la madera del fondo; la semilla rota y la estrella aparecen como emblema,
remate o gema, nunca como relleno.

### Paleta para las imágenes

Hex del CSS real (`frontend/src/index.css`, bloque `@theme`), más los tonos de oro, piedra, noche y cristal oscuro fijados en
§3 de `propuesta-fable-2026-11-10.md` (aprobados por la persona el 2026-11-10; marcados con *, son los tokens que se proponen
al juego en `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md`). Proporción **60/30/10**: madera e hierro 60, oro y
piedra 30, luz y cristal 10 (brillo `gold-100` ≤ 5 %, cristal ≤ 10 %).

| Rol en la imagen | Token | Hex |
| --- | --- | --- |
| Hierro más oscuro (sombras, fondo de pictogramas sobre hierro) | `iron-900` | `#0e0b08` |
| Hierro (fondo de cabecera/pie, riel del instalador) | `iron-800` / `iron-700` | `#171310` / `#221c16` |
| Madera de fondo de página | `wood-950` / `wood-900` | `#1b130c` / `#241a10` |
| Madera de tablón (paneles, tarjetas) | `wood-800` / `wood-700` / `wood-600` | `#332415` / `#46311d` / `#5c4126` |
| Madera clara (veta iluminada, cantos) | `wood-500` / `wood-400` / `wood-300` | `#7a5934` / `#a3814f` / `#c9a877` |
| Hueso, pergamino, texto claro | `wood-200` / `wood-100` | `#e3cba8` / `#f1e4d0` |
| Cristal azul (Helek Sirik, acento, estrellas) | `accent-300` / `400` / `500` / `600` | `#a8d8f0` / `#7bc4e8` / `#4aa8d8` / `#3488b8` |
| Acero (hierro pulido, tablón de defensa) | `accent2-300` / `400` / `500` / `600` | `#b0bec8` / `#8a9aa8` / `#6b7d8c` / `#52626f` |
| Musgo (estado bueno, hecho) | `moss-400` / `500` / `600` | `#8fae6a` / `#6f9450` / `#587a3c` |
| Peligro (salud baja, error) | `danger-400` / `500` | `#f87171` / `#ef4444` |
| Ámbar de coste y amarillo de misión (los únicos «oros» del CSS) | `cost-400` / `500` · `quest-400` / `500` | `#fbbf24` / `#f59e0b` · `#facc15` / `#eab308` |
| Oro: cuerpo del metal | `gold-500` * | `#b8862b` |
| Oro: bisel con luz (10 %) | `gold-300` * | `#f2c45a` |
| Oro: núcleo de luz (estrella, junta de la Semilla; ≤ 5 %) | `gold-100` * | `#ffe9a8` |
| Oro: pátina, cara en sombra | `gold-700` * | `#7a5a1e` |
| Oro: filo, contorno de 1-2 px, tinta sobre fondo claro | `gold-900` * | `#5a3a14` |
| Piedra de la Semilla (gajos, pedestal de piedra) | `stone-700` / `stone-500` * | `#3a342d` / `#6b6257` |
| Noche de marca (fuera del juego; dentro solo `.crystal-sky`) | `night-950` / `night-900` * | `#0f1428` / `#1a2140` |
| Cristal oscuro: campo del emblema, fondo de gema (≤ 10 %) | `crystal-deep` * | `#1f4a55` (claro `#2f6b7a`) |
| Halo dorado (solo resplandor alrededor de un núcleo `#ffe9a8`; nunca cuerpo ni relleno) | — | `#ffd66b` |
| Arcilla (`brand.palette` de `examples/tarkor`, resto de r7): **fuera de la marca** (decisión 6); solo tierra de Berig en #4 y en paisajes | — | `#E0703A` |

Atributos (solo si algún día se piden sus pictogramas): fuerza `#cc5852`, destreza `#3fb89d`, constitución `#9566cc`,
inteligencia `#6bb83f`, voluntad `#cca63f`, carisma `#cc5794`, magia `#5772cc`.

Tipografía de la interfaz (para saber con qué conviven los recursos, **nunca para pintar letras**): Cinzel en
títulos (`--font-serif`), Inter en texto, Cascadia Code en números. Radios: píldoras `rounded-full`, botones `md`,
tarjetas `lg`, paneles `xl`, ranura de habilidad 3 px (`.skill-slot`).

## 2. Cómo pedirlas

Reglas con medida: `hoja.md` §16. Revisado el 2026-11-12.

- **Bloque común** (se antepone a cada prompt, en inglés; 58 palabras, M10: solo materiales y luz; lo que cambia por
  pieza va en su prompt):

  > Epic fantasy game asset. Materials: aged dark wood planks with raised grain in #332415 and #46311d, dark forged
  > iron in #171310, old carved gold in #b8862b with dark patina #7a5a1e in the recesses and bright worn edges in
  > #f2c45a, dark cracked stone in #3a342d. Warm raking light from the upper left, deep cool shadows in every groove.
  > A thin dark bronze outline separates gold from background. Physically plausible materials, crisp edges, high
  > contrast, no haze.

- **Módulos por pieza** (se añaden solo a las piezas que los llevan):
  - cristal: `faceted crystal field in #1f4a55` (campo) o `one small gem of blue crystal #4aa8d8` (gema);
  - noche (solo fuera del juego y en #6): el **bloque de noche** del Bloque I, entero, **en lugar** del bloque común;
  - madera: `oil-finished dark wood, grain raised, matte`.
  La luz de la Semilla y la estrella de cuatro puntas **ya no son módulos**: son del emblema, y el emblema llega por
  composición desde los SVG de `logos/` (regla L1). Ningún prompt los pide.

- **Sin prompt negativo y sin negaciones** (regla P3): lo que no debe salir no se nombra, ni negado. La única
  negación admitida es el `no haze` de los dos bloques. Palabras que no entran: regla P2 (`castle` incluida).
- **Nada de letras** en ningún recurso: el título va en Cinzel desde el CSS y el logo desde los SVG.
- **Transparencia:** la pieza se pide sobre **croma plano** y se recorta con `gimg matte` (`-alpha.png`). Verde
  `#00ff00` cuando la pieza no lleva verde (todas las de aquí); se marca `[recorte]` en la columna de notas. La frase
  de croma **cierra el prompt** y es la de `hoja.md` §6 («Recorte sobre croma»), literal: `Centred on a solid, uniform,
  evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15
  percent empty margin on every side.` (con `magenta background #ff00ff` si la pieza lleva verde). El hueco de un marco
  se pide `filled with the same chroma-key green #00ff00`. La pieza va centrada, de frente, con el 15 % de margen por lado (reglas P8 y P9).
- **Mosaico (texturas):** el perfil lleva `tileable` (`"xy"`, o `"x"` en las bandas) y gimg genera sin costura; el
  prompt dice «seamless tileable» igual. De 2 a 3 semillas. La costura **NUNCA** se arregla a mano. Para fondos de
  `background-size: cover` (cielo, estampa) no hace falta.
- **Perfiles de generación:** tamaño múltiplo de 64 y ≤ 1 048 576 px (Deck). Para `galivelop-images.json` del
  proyecto: `textura` 1024×1024, `banda` 1024×256, `cielo` 1536×640, `icono` 512×512, `emblema` 1024×1024,
  `estampa` 1280×512, `tira` 1024×128; y para el bloque E: `avatar`
  1024×1024, `cabecera` 1536×512, `carga` 1280×704, `capsula` 1024×576, `marco` 1280×704; todos declarados, con los del mapa y los de redes (23 en total). `cfg` 1.0, `euler`; de 2 a 3 semillas por pieza y se elige (de 6 a 10
  cuando importa un recuento). **Nada sale por img2img del #1**: lo que lleva el emblema (E1, E9, E14, #16) se
  genera sin él y lo recibe por composición desde el SVG, que es el mismo en todas partes.
- **Modelo:** lo que se entrega sale de `zimage-turbo-q6` a 8 pasos con `draft: false` (regla P6); FLUX.2 klein,
  solo bocetos. La columna «Modelo» de las tablas (**K**, **K?**, **M**) es del 2026-11-10 y hoy solo dice la
  dificultad prevista: **K** fácil; **K?** puede pedir más semillas; **M** recuento o detalle que va al SVG.
- **Destino:** carpeta nueva `frontend/src/assets/ui/` del juego (Vite resuelve `url()` desde `index.css`), salvo
  donde la tabla diga otra. Esta hoja no toca el repo del juego: la entrega se deja en `examples/tarkor/entrega/ui/`
  y se propone desde aquí (`docs/propuestas/`).

## 3. Recursos

Orden: la pieza de referencia primero; después bloques A-D por prioridad. «Medidas» es lo que se entrega;
«Perfil» lo que se genera.

### Referencia de estilo

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Emblema de la Semilla rota** (pieza de referencia: fija el oro, la piedra y la luz de todo lo demás; M8) | 1024×1024 PNG = boceto del que `gimg brand system` trazó los SVG del sistema de logo (§5 de la propuesta): `tarkor-emblema.svg`, `tarkor-emblema-simple.svg` (favicon 16-64 px), `tarkor-monograma.svg`, `tarkor-wordmark.svg`, `tarkor-lockup-h.svg`, `tarkor-lockup-v.svg` en `docs/marcas/tarkor/logos/` | `emblema` 1024×1024 | `frontend/public/favicon.svg` es un rayo violeta genérico sin relación con la marca (`#863bff`, `#7e14ff`, `#47bfff`): se sustituye por `tarkor-emblema-simple.svg` + PNG 32/16 y `<link rel="icon">` en `frontend/index.html` (hoy sin `<link>`). Instalador: `app/src-tauri/icons/icon.png` y `fuente.png` son hoy un rombo azul plano sobre disco marrón (`tauri.conf.json` l.34): se sustituyen por E14. | (prompt retirado el 2026-11-12: el emblema ya no se pide pintado, regla L1; el texto que dio el boceto q185 queda, como historia, en `orders/ui/01-emblema.json`) | `[recorte]` verde. **K?**: 8-10 semillas; se elige por silueta en gris a 32 px, piedra legible y cuatro puntas limpias; si no salen seis gajos, se dibujan en el SVG. Geometría del SVG: círculo r 100, anillo 14, puntas 36 más allá del anillo, disco r 58 con tres cortes de 6 a 0°/60°/120°, estrella 28×16 (decisión 2: las diagonales solo a ≥ 256 px y ≤ 40 % más cortas). El pedido `orders/ui/01-emblema.json` y `01b-emblema-plano.json` (el plano del que se trazaron los SVG) quedan como historia y no se sincronizan. |

### Bloque A — fondos y texturas (hoy degradados CSS marcados como provisionales)

`index.css` l.150: «Provisional: esto se sustituirá por fondos generados de verdad cuando exista la API de prompts
de imagen». Las clases: `.wood-grain` l.129, `.dust-road` l.152, `.plank-panel` l.167, `.plank-panel-defense` l.193,
`.iron-band` l.216, `.crystal-sky` l.269, `.iron-etched` l.292. El instalador copia las mismas ideas en CSS:
`.riel` (`estilos.css` l.31-33) y `.principal` (l.49-53).

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | **Tablón de panel** (madera oscura con veta, para tarjetas y paneles) | 1024×1024 PNG, mosaico; se usa a 50 % (512 px CSS) | `textura` 1024×1024 | `.plank-panel` (`index.css` l.167): WorldCard, CharacterCard, botones de `Home.tsx` l.41, PanelDrawer, CombatModal; `.principal` del instalador (l.49-53) | Seamless tileable texture of aged dark wood planks seen straight on, wood colours #332415 and #46311d with lighter grain lines in #7a5934, fine straight grain, a few tight knots, soft worn surface, subtle warm light from the upper left, even exposure across the whole image, flat, edge to edge, top view. | **K**. 2-3 semillas; el perfil lleva `tileable` y no hay costura que arreglar. Los remaches (`.rivet` l.324) y el borde siguen en CSS. |
| 3 | **Madera de fondo de página** (más oscura y sorda que el tablón) | 1024×1024 PNG, mosaico | `textura` 1024×1024 | `.wood-grain` (`index.css` l.129): fondo de `App.tsx`, `ErrorBoundary.tsx` l.32, `GamePanelCajon.tsx`, `LogPanel.tsx` | Seamless tileable texture of very dark aged wood seen straight on, nearly black brown #1b130c with faint grain in #241a10 and sparse hairline highlights in #332415, matte, low contrast, calm, even exposure, flat, edge to edge, top view. | **K**. Debe quedar por debajo del tablón en luminosidad (YAVG < 40) para que el texto `wood-100` siga en AA. |
| 4 | **Camino de polvo** (fondo del panel de narración) | 1024×1024 PNG, mosaico | `textura` 1024×1024 | `.dust-road` (`index.css` l.152), usado en `LogPanel.tsx` y `ChatComposer.tsx` | Seamless tileable texture of packed dry earth and fine red dust seen straight on, colours #241a10 and #332415 with scattered tiny grains in #a3814f and #E0703A, faint dragged marks, matte, very low contrast, even exposure, flat, edge to edge, top view. | **K**. Es el fondo del texto largo: contraste bajísimo, sin motivos que se lean como letras. |
| 5 | **Banda de hierro y oro** (cabecera y pie del juego, `.barra` del instalador; el riel es I4) | 1024×256 PNG, mosaico horizontal | `banda` 1024×256 | `.iron-band` (`index.css` l.216): `GameHeader.tsx` l.93, `GameFooter`; `.iron-etched` l.292 en botones; `.riel` del instalador (l.31-33) | Seamless horizontally tileable band of dark forged iron seen straight on, colour #171310 with a faint engraved grid of fine lines in #52626f, a thin bevelled strip of old carved gold #b8862b along the top edge and another along the bottom edge, matte metal with subtle scratches, even exposure, flat, edge to edge. | **K**. La tira de oro debe medir ~6 px de los 256 para no competir con el texto de la cabecera. |
| 6 | **Cielo nocturno** (pantalla de inicio y tarjeta de Helek Sirik) | 1536×640 PNG, `background-size: cover` | `cielo` 1536×640 | `.crystal-sky` (`index.css` l.269): `Home.tsx` l.20, `WorldCard.tsx` l.25 (solo `helek-sirik`); el degradado CSS pasa a `night-950` → `night-900` → `iron-900` mientras no haya imagen | (tras el bloque de noche, no el común) Wide view. The belt of stardust crosses the upper half of the frame from the lower left to the upper right. Low silhouettes of jagged dark rock spires in #0e0b08 stand along the very bottom edge. Above them, the lower third of the frame is plain dark sky fading to #0e0b08, even and empty. | **K**. Canon del juego: la noche es un cinturón de polvo que brilla, con velo perlado y **sin luna** (vetada). Sin esquirlas flotantes ni niebla (M3, bloque común). El tercio inferior libre es donde cae el título de `Home.tsx` l.29-30. Misma escena que E2/E3 con otro encuadre. Reescrito el 2026-11-12 (reglas P1-P4). |
| 7 | **Tablón de defensa** (variante azul-acero del #2) | 1024×1024 PNG, mosaico | `textura` 1024×1024 | `.plank-panel-defense` (`index.css` l.193); `CombatPanel.tsx` l.474 explica que hoy se tiñe el `background-image` del tablón, cosa que con un PNG ya no vale | Seamless tileable texture of aged dark wood planks seen straight on, the wood stained a cold blue grey, colours #221c16 and #52626f with grain lines in #6b7d8c and a faint cold sheen of #3488b8, fine straight grain, a few tight knots, even exposure, flat, edge to edge, top view. | **K**. Misma semilla y misma composición que el #2 si se puede (img2img del #2 a 0,3 con este prompt). |

### Bloque B — marcos y ornamentos (hoy pseudoelementos CSS)

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | **Esquina ornamental** (una; las otras tres por volteo; dos variantes) | 512×512 generado → 128×128 PNG entregado (se usa a 32-48 px); `08-esquina-oro` y `08-esquina-acero` | `icono` 512×512 | `.corner-bracket-gold` (nueva, modales de personaje) y `.corner-bracket` (`index.css` l.300-322: escuadra de acero hecha en CSS, paneles de mundo), usadas en `ModalShell.tsx` y `DetailModal.tsx` | A single corner ornament for a frame, seen straight on: two short thick arms of old carved gold meeting at a right angle, the joint towards the top left, chiselled relief, sharp bevels, each arm ending in a spiked point, a small raised gold boss with four tapered points set in the joint, dark iron rivets along the arms. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde. **K?**: a 32 px el detalle se pierde; pedir pocas formas y gruesas. Variante acero: la misma pieza recoloreada en HSL a `accent2` (`#8a9aa8` / `#52626f`), no un segundo prompt. Las otras esquinas, con `transform: scaleX(-1)` etc. |
| 9 | **Separador horizontal con estrella** (filete que se desvanece con remate central) | 1024×128 generado → 1024×64 PNG; la estrella sola a 64×64 (`09-estrella`) sirve de cabeza de E7 y de viñeta grande | `tira` 1024×128 | `.gold-hairline` (nueva, hermana de `.accent-hairline` l.226) + `.gem` (l.246): `Home.tsx` l.24-27 y l.31-34; `.filete` del instalador (`estilos.css` l.60); girado 90° por CSS es E8 | A thin horizontal divider seen straight on: a hairline of old carved gold that fades out towards both ends and, at its centre, one small gold finial with four long tapered points at top, bottom, left and right and a white-gold #ffe9a8 core, symmetric, the divider occupying only the middle fifth of the height. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde. **K**. La estrella es oro (M3): el cristal azul queda solo en `.gem` por CSS. Si no sale limpio, el filete sigue en CSS y solo se recorta la estrella (64×64). |
| 10 | **Marco de ranura de habilidad** (marco de oro para encajar el icono de cada habilidad) | 512×512 generado → 88×88 PNG (ranura 44 px @2x) | `icono` 512×512 | `.skill-slot` (`index.css` l.369-388: 44×44, radio 3 px; el icono es un emoji) y `SkillBarHud.tsx` l.63; `IconCard.tsx` l.62; va como `border-image` con `border: 1px solid gold-900` de respaldo | A square slot frame for a game hotbar, seen straight on: a square border of old carved gold with chiselled relief and sharp bevelled edges, one small raised gold boss with four tapered points at the top centre, symmetric, the inside of the square empty and filled with the same chroma-key green #00ff00. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde por fuera **y por dentro**. **K**. Sin estrellas en las esquinas (cuatro a 44 px se emborronan): una arriba al centro o ninguna. Los iconos que van dentro los hace el generador de Tarkor (habilidades, clases: §4). |

### Bloque C — pictogramas de interfaz (hoy emojis del sistema)

Un prompt por pictograma, misma plantilla; se generan a 512×512 y se entregan a 128×128 y 64×64. Se usan a 20-32 px
(`SideNav`, `CollapsedRail`, barras) y a 40-48 px (`PanelEmptyState`, `IconCard`). Plantilla (tras el bloque común):

> Single game interface icon of {motivo}, set in a shallow round recess of dark forged iron that fills 80 percent of
> the frame. The motif is old carved gold with chiselled relief, one thick simple silhouette filling 60 percent of the
> recess, with a thin dark bronze outline, straight on, symmetric where possible, readable at small size. Centred on a
> solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly
> and floating, 15 percent empty margin on every side.

El pedestal de hierro (M8) da a los doce pictogramas el mismo fondo y la misma escala; a 20 px se ve un disco oscuro
con una forma de oro encima. Los motivos «de cristal azul» (#11 habilidades, #12 sed, #13 elección, #17) son la gema
de M3: una sola pieza pequeña de `#4aa8d8`, el resto oro.

| # | Recurso | Medidas | Perfil | Dónde va | {motivo} de cada pieza | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | **Pestañas del cajón** (12) | 128² y 64² PNG | `icono` 512×512 ×12 | `NavTabs.ts` l.23-41 (hoy ⚔️ 🎒 ✨ 👥 🏰 🗺️ 📖 📕 🎯 🤝 📚) y `PersonajePanel.tsx` l.22 (equipo ⚔️); se pintan en `SideNav.tsx` l.60 y `CollapsedRail.tsx` l.24; reutilizables en `PanelEmptyState.tsx` l.16 y las notificaciones (`notificaciones.ts`: 🎒 🎯) | personaje: a straight sword pointing up · inventario: a closed leather satchel with a buckle · habilidades: a faceted gem of blue crystal #4aa8d8 with four tapered points · compañeros: two crossed spears over a small round shield · reino: a timber palisade with a single watchtower · mapa: a rolled parchment with a wax seal · diario: an open book · leyendas: a closed book with an iron clasp · misiones: a hanging banner on a crossbar with a gold fringe · reputación: two interlocked iron rings · enciclopedia: a stack of three stone tablets · equipo: a horned iron helmet seen from the front | `[recorte]` verde. **K?**: klein da bien la materia; a 20 px hace falta silueta gruesa. Generar 3 semillas y elegir; si no leen a 20 px, vectorizar a mano sobre el PNG (**M**). Sin figuras humanas (vetadas): compañeros y reputación van por objetos. |
| 12 | **Barras de estado del HUD** (3) | 64² y 32² PNG | `icono` 512×512 ×3 | `HungerBar.tsx` l.16 (🍖), `ThirstBar.tsx` l.14 (💧), `EnergyBar.tsx` l.9 (⚡) | hambre: a roasted joint of meat on a bone · sed: a single drop of water, faceted, in blue crystal · energía: a small flame rising from an iron brazier | `[recorte]` verde. **K**. Se usan a 16-20 px: una sola forma cada uno. |
| 13 | **Fases del juego** (8) | 64² y 32² PNG | `icono` 512×512 ×8 | `gamePhase.ts` l.107-116 (`ETIQUETA_FASE`: ✒️ 🧭 ⚠️ ⚔️ 💬 ⭐ 💀 📜), mostrada en `GameHeader` / `GameFooter` | pensando: a quill pen · ocupado: a compass rose with a four-pointed needle · encuentro: a curved war horn · combate: two crossed swords · dinámico: a small campfire · elección: a faceted gem of blue crystal #4aa8d8 with four tapered points in a gold mount · muerte: a cracked stone skull of a horned beast · fin: a rolled scroll with a hanging wax seal | `[recorte]` verde. **K**. «combate» puede compartir pieza con la pestaña personaje si se prefiere una sola espada; «elección» comparte con la estrella del #9. |
| 14 | **Dado de hueso** | 64² y 32² PNG | `icono` 512×512 | `DiceRoll.tsx` l.113 (🎲 fijo junto al número que gira) | a six-sided die carved from pale bone #e3cba8 with golden pips, seen from a corner showing three faces | `[recorte]` verde. **K**. |
| 15 | **Categorías de objeto** (15, respaldo cuando la ficha no tiene miniatura) | 64² PNG | `icono` 512×512 ×15 | `enciclopediaTargets.ts` l.191-220 (`itemIcon`, por defecto 📦) y l.40-56 (`ITEM_CATEGORY_ORDER`: especial, arma, herramienta, ropa, accesorio, armadura, cosmetico, consumible, medicinal, alimento, documento, valor, piel, hueso, madera); se pinta en `Miniatura.tsx` l.16 a 32 px | especial: a gold finial with four long tapered points · arma: a short axe · herramienta: a hammer and a chisel crossed · ropa: a folded hooded cloak · accesorio: a ring with a small blue gem · armadura: a breastplate · cosmetico: a small clay pot with a lid · consumible: a corked round flask · medicinal: a bundle of dried herbs tied with cord · alimento: a loaf of bread · documento: a folded letter with a wax seal · valor: a stack of three gold coins · piel: a stretched animal hide on a frame · hueso: a single long bone · madera: three stacked logs | `[recorte]` verde. **K**. Prioridad baja: la mayoría de fichas ya traen miniatura del generador de Tarkor; este juego cubre los huecos. |
| 16 | **Medallón de ficha sin imagen** (placeholder de miniatura y retrato) | 768×768 PNG (se muestra a 32-96 px y en el `aspect-[2.5/1]` del combate recortado) | `emblema` 1024×1024 | `Miniatura.tsx` l.16 (emoji cuando no hay `thumbnail`), `CombatPanel.tsx` l.758 (⚔️ cuando no hay retrato), `MediaSlot` de `ImagePromptDisplay.tsx` | A round medallion of aged dark wood #332415 with a rim of old carved gold with chiselled relief, its centre a plain disc of dark matte cracked stone #3a342d, even and empty, seen straight on, symmetric, the medallion fills the frame edge to edge. | Sin recorte (fondo del propio medallón). **K**. La Semilla llega por composición desde `tarkor-emblema.svg`, centrada sobre el disco de piedra (regla L1); el borde es la variante redonda de E11. Reescrito el 2026-11-12. |

### Bloque D — instalador y escaparate

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 17 | **Estados de las comprobaciones del instalador** (4) | 64² y 32² PNG | `icono` 512×512 ×4 | `Instalador-WMF-Tarkor/docs/11-diseno-del-frontal.md` l.135: «7 comprobaciones ... con un icono de estado cada» (sin recurso propio; `estilos.css` solo colorea `.pasos li.hecho/.actual`) | plantilla del bloque C (con pedestal) con: hecho: a gold finial with four long tapered points and a small gem of blue crystal #4aa8d8 at its core · aviso: the same finial with a gem of amber crystal #f59e0b at its core · error: the same finial with a gem of red crystal #ef4444 at its core · en curso: a compass rose of old gold with a four-pointed needle | `[recorte]` verde. **K**. Una sola forma (la estrella) con la gema en cuatro colores: coherente y legible a 20 px. «hecho»/«aviso»/«error» salen de una pieza recoloreada en HSL. |
| 18 | ~~**Estampa del mundo Helek Sirik**~~ (cabecera de la tarjeta de mundo) | 1280×512 PNG, `object-cover` | `estampa` 1280×512 (= `banner`) | `WorldCard.tsx` l.24-25: hoy `plank-panel` + `crystal-sky` por CSS; no hay imagen de mundo | (prompt retirado) | **Fuera de esta hoja (D7, 2026-11-10):** casa mejor con los banners del generador de Tarkor y se propone allí. La fila queda como registro del número. |

### Bloque E — marca y piezas nuevas (propuesta de Fable §6, aprobada el 2026-11-10)

Lo que la marca necesita fuera del juego (redes, Steam, og:image, icono) y lo que el juego pide además del bloque A-D
(carga, progreso, sellos, botones). Nombres de archivo previstos: `examples/tarkor/entrega/marca/e<nn>-<nombre>.png`
para lo de fuera del juego (E1-E5, E14, E18) y `examples/tarkor/entrega/ui/e<nn>-<nombre>.png` para lo que entra en la
interfaz (E6-E13, E16, E17); recortes `-alpha.png`. El SVG manda cuando la pieza es vectorial (E8, E14 ≤ 64 px, E16).
Los once perfiles del Bloque E están declarados en `galivelop-images.json` (repo, 2026-11-10).

| Id | Recurso | Medidas | Perfil | Prioridad | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | **Avatar** (X, Discord, GitHub, itch) | 512² y 256², recortado en círculo; `e01-avatar` | `avatar` 1024×1024 | alta | (tras el bloque de noche) Square view. The belt of stardust crosses the frame from the lower left to the upper right, faint and dim. The centre of the frame is plain calm sky in #1a2140, even and empty, and the edges fade to near black #0f1428. | **K**. Solo se genera el fondo; `tarkor-emblema.svg` va encima por composición, centrado. Emblema completo de 64 px en adelante; por debajo, `tarkor-emblema-simple.svg` (decisión 8, regla L2). También es el avatar de Reddit (decisión del 2026-11-12). Reescrito el 2026-11-12. |
| E2 | **Cabecera** de X 1500×500 y Discord 960×540 | 1536×512 → 1500×500 y 960×540 (recorte central); `e02-cabecera` | `cabecera` 1536×512 | alta | (tras el bloque de noche) Wide view. The belt of stardust crosses the right two thirds of the frame from the lower left to the upper right. Jagged dark rock spires in #0e0b08 stand along the bottom edge. Across the bottom tenth, a band of aged dark wood planks in #332415 with one thin line of old gold #b8862b on its top edge. The left third, from the left edge inward, is plain calm sky in #1a2140, even and empty. | **K**. Lockup horizontal (`tarkor-lockup-h.svg`) en el tercio izquierdo, que es la zona libre, por `compose`. También es la cabecera de Reddit (decisión del 2026-11-12). Reescrito el 2026-11-12: el tercio libre es el del logo (hoja §9, «Zona reservada»). |
| E3 | **og:image** del juego y del Portal (sustituye a la plantilla r7 `plantillas/og.svg` con `tarkor-b-lockup.svg`, Metamorphous y Almendra) | 1280×640 → 1200×630; `e03-og` | `og` (existe) | alta | (tras el bloque de noche) Wide view. The belt of stardust crosses the frame low, from the lower left to the right edge, below the middle of the height. Jagged dark rock spires in #0e0b08 stand along the bottom edge. The central half of the frame, from the top edge downward, is plain calm sky in #1a2140, even and empty. | **K**. Lockup vertical (`tarkor-lockup-v.svg`) centrado y el lema en Inter 400 debajo (hoja §9 y regla T7; antes decía izquierda y derecha); plantilla nueva `plantillas/og.svg` con `fonts: ["Cinzel", "Inter"]`. |
| E4 | **Steam**: capsule header 460×215 y main 616×353 (small 231×87 sale del header; vertical 374×448 cuando haya ficha) | 1024×576 → 616×353 y 460×215; `e04-capsula` | `capsula` 1024×576 | media | (tras el bloque de noche) Wide view. The belt of stardust rises from the lower left to the upper right. The centre of the frame is plain calm sky in #1a2140, even and empty. | **K**. Decisión 7: solo header y main ahora; emblema centrado + wordmark debajo por `compose`. |
| E5 | **Steam hero** 3840×1240 y logo 1280×720 | `e05-hero` | `cabecera` 1536×512 (escalada) | baja | E2 sin la banda de madera | Cuando exista la ficha. El logo de Steam es el lockup vertical sobre transparente. |
| E6 | **Pantalla de carga** del juego | 1280×704 PNG, `background-size: cover`; `e06-carga` | `carga` 1280×704 | alta | (tras el bloque de noche) Wide view from a high ridge. The belt of stardust crosses the upper half of the frame from the lower left to the upper right. Dark rock spires in #0e0b08 and a long dark timber palisade with plain dark banners stand on a far hill, with one small campfire at the foot of the palisade. Across the lower quarter, a band of dark forged iron #171310 with one thin line of old gold #b8862b on its top edge. | **K**. Encima, `tarkor-emblema-simple.svg` girando por CSS y la barra E7. Reescrito el 2026-11-12 con el bloque de noche (hoja §6: con el común, q355 pasó del 10 % de oro); la hoguera se nombra en afirmativo. Única noche dentro del juego junto a #6 (M7). |
| E7 | **Barra de progreso**: pista, relleno y cabeza | pista 1024×32, relleno 1024×32, cabeza 64² (`09-estrella`); `e07-barra-pista`, `e07-barra-relleno` | `tira` 1024×128 ×2 | alta | pista: A long horizontal groove carved in dark forged iron #171310 with a thin bevelled gold rim, even along its whole length, flat ends. · relleno: A long horizontal bar of polished bright gold #f2c45a with a slightly lighter centre line and darker #b8862b edges, even along its whole length, flat ends. | **K**. Se recortan a 32 px de alto; la cabeza es el remate del #9. Las aceptadas (q357, q359) salieron de este texto; el relleno llevaba además una negación, quitada el 2026-11-12. |
| E8 | **Separador vertical** | 128×1024 → 64×1024 | — | media | no se genera: el #9 girado 90° por CSS (`transform: rotate(90deg)`) | vectorial/CSS. |
| E9 | **Sello de cera** (cierres, firmas de documentos del juego) | 512² → 96² y 48²; `e09-sello` | `icono` 512×512 | media | A round wax seal of dark red-brown wax #5a1e14 seen straight on, the whole seal one single colour, with a raised uneven rim and a plain smooth recessed centre, the rim catching warm raking light. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde. **K**. El relieve llega por composición: `tarkor-emblema-mono.svg` en el centro liso (regla L1). Reescrito el 2026-11-12. |
| E10 | **Insignia alpha / versión** | 512×256 → 160×80 y 96×48; `e10-insignia` | `banda` 1024×256 (recortada) | alta | A small hanging banner of aged dark wood with an iron rim and a thin gold strip, seen straight on, a square plate of dark iron at its centre, plain and empty. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde. **K**. El texto («alpha 0.3») va en Cinzel por CSS o SVG, nunca pintado. |
| E11 | **Marco de retrato** (9-slice) y su variante redonda | 512² → 96² y 192²; `e11-marco-retrato`, `e11-marco-retrato-redondo` | `icono` 512×512 ×2 | media | A square frame of old carved gold with chiselled relief, seen straight on, a small raised gold boss with four tapered points at each corner, iron rivets at the midpoints, the inside of the frame empty and filled with the same chroma-key green #00ff00. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde por fuera y por dentro. **K**. La redonda es el borde del #16. Para el 9-slice basta una esquina limpia (hoja §6). La aceptada salió del prompt anterior (con `star`); el pedido lleva ya este. |
| E12 | **Plantilla de captura** (marco para capturas de pantalla en redes) | 1280×704; `e12-plantilla-captura` | `marco` 1280×704 | media | A rectangular frame of aged dark wood planks with an inner rim of dark iron and a thin bevelled gold edge, four gold corner ornaments, seen straight on, the frame reaching the edges of the image. The inside of the frame is empty and filled with one solid, uniform, evenly lit chroma-key green #00ff00, one flat colour edge to edge. | `[recorte]` verde por dentro. **K**. |
| E13 | **Botón** en tres estados | 512×192 → 128×48 ×3; `e13-boton`, `e13-boton-hover`, `e13-boton-pulsado` | `banda` 1024×256 (recortada) | media | img2img 0,3 del #2 (cada estado cierra con la frase de croma de §2): A horizontal button plate of aged dark wood with a dark iron rim and a thin gold strip along the top edge, seen straight on. · hover: the same plate with the gold strip brighter and a faint warm sheen inside the rim. · pulsado: the same plate darker and recessed, the gold strip dim. | `[recorte]` verde. **K**. Hasta que exista, el botón sigue en CSS (`.plank-panel` + borde `gold-900`). |
| E14 | **Icono de aplicación** (Instalador `icon.png`, `fuente.png`; escritorio) | 1024², 512², 256², 128², 64², 32² e `icon.ico` (16, 24, 32, 48, 64, 256; = I5); `e14-icono-app` | `emblema` 1024×1024 | alta | no se genera (corregido el 2026-11-12: ningún modelo pinta el emblema): `tarkor-emblema.svg` compuesto sobre un disco `night-950` `#0f1428` que llena el marco, el anillo al 80 por ciento del disco | **K**. A 64 px o menos, `tarkor-emblema-simple.svg` rasterizado (decisión 8). Sustituye al rombo azul del Instalador. |
| E15 | Cursor | — | — | baja | **no ahora** (decisión 9) | — |
| E16 | **Viñeta / punto de lista** | 16² SVG; `tarkor-glifo.svg` | — | alta | no se genera: el glifo del emblema sin anillo (seis gajos + estrella) en `gold-500`, vectorial | vectorial. |
| E17 | **Tooltip** (fondo) | 512×256 → 128×64; `e17-tooltip` | `banda` 1024×256 (recortada) | baja | A small plate of dark forged iron with a thin gold rim, flat, seen straight on. Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side. | `[recorte]` verde. **K**. Recomendado dejarlo en CSS (`iron-800` + `border: 1px solid gold-700`) y no generarlo. |
| E18 | **Hoja de contactos** de la marca (todo lo anterior en una lámina) | 1536×640; `e18-contactos` | — | media | compuesta (sin generar) con los PNG y SVG entregados | la hace `gimg` o el piloto al cerrar el bloque. |

### Bloque I — Instalador (pedido del Instalador, 2026-11-11; añadido el 2026-11-12)

Fuente: `Instalador-WMF-Tarkor`, `docs/13-hoja-de-estilos-e-imagenes.md` §3, commits `d9d33fe` (pedido, INS-57) y
`608661d` (dudas resueltas), leído en la rama `claude/installer-docs-review-09e7vs` (`34d2bb27`). Los prompts son
los suyos, literales. Destino: `examples/tarkor/entrega/`; la copia a su repo la hace la persona (doc 13 §6,
decisión 4) y allí `INS-58` convierte, mide y coloca. Reglas: `hoja.md` §16; cobertura: `hoja.md` §17.

**Bloque de noche** (va delante de I1, I3 e I6; I4 lleva el bloque común de §2):

> Epic fantasy matte painting, physically plausible, crisp edges, high contrast, clear air, no haze. Deep indigo
> blue night sky #1a2140, slightly green-leaning, near black #0f1428 at the top. A slanted belt of pale shimmering
> stardust in #4aa8d8 and #a8d8f0 crosses the sky and is the only light in it.

| Id | Recurso | Medidas | Perfil | Dónde va (Instalador) | Prompt | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| I1 | **Lateral del instalador de Windows** (bienvenida y final) | 704×1344 → 164×314 y 328×628, BMP de 24 bits sin alfa | `lateral` 704×1344 (perfil desde el 2026-11-13) | `sidebarImage` → `app/src-tauri/windows/lateral.bmp` | Tall upright view. The belt of stardust rises from the lower left to the upper right across the middle of the frame. Low jagged dark rock spires in #0e0b08 stand along the bottom. Under them, across the bottom tenth, a band of dark forged iron #171310 with one thin line of old gold #b8862b on its top edge. The upper third, from the top edge downward, is plain calm sky in #1a2140, even and empty. | Prioridad alta. `tarkor-lockup-v.svg` en el tercio superior, por composición, a 120 px de ancho en la de 164. Reducción y BMP: `gimg export … lateral.bmp --size 164x314` (y `328x628`) |
| I2 | **Cabecera del instalador** y del desinstalador | 150×57 y 300×114, BMP de 24 bits sin alfa | no se genera: composición | `headerImage`, `uninstallerHeaderImage` → `windows/cabecera.bmp` | — | Prioridad alta. Fondo liso `#0f1428`, `tarkor-emblema-simple.svg` centrado a 41 px de alto, línea de 1 px `#7a5a1e` en el borde inferior. BMP: `gimg export cabecera.png cabecera.bmp` |
| I3 | **Portada del asistente** («Bienvenida» y «Listo») | 1536×512 → 1536×384 (recorte central), WebP q85; se ve a 870×218 | `cabecera` 1536×512 | `app/src/imagenes/portada.webp` | Wide view along a packed earth road in #241a10 that runs from the bottom centre to a long dark timber palisade on a low hill, its closed gate in the middle of the frame, plain dark banners hanging on its posts, jagged dark rock spires in #0e0b08 on both sides. The gate has dark forged iron fittings #171310 and one thin line of old gold #b8862b across its lintel. The upper half is calm sky crossed by the belt of stardust. All the detail sits in the middle band of the height; the top fifth and the bottom fifth are quiet and even. | Prioridad media. Sin logo y sin texto encima. Aprobada como idea por la usuaria (doc 13 §6). Lo importante, en el centro: con la ventana al mínimo se recortan los lados. Recorte y WebP: `gimg export … --size 1536x384` (WebP sin pérdida; q85 con pérdida, no) |
| I4 | **Hierro del riel** | 1024×1024, mosaico en las dos direcciones, WebP q85 | `textura` 1024×1024 con `tileable: "xy"` | Fondo de `.riel`, 230 px de ancho; `app/src/imagenes/riel-hierro.webp` | Seamless tileable texture of dark forged iron seen straight on, colour #171310 with a faint engraved grid of fine lines in #52626f, matte metal with subtle scratches and a few hammer marks, even exposure across the whole image, flat, edge to edge, top view. | Prioridad baja. Luminancia media < 40 sobre 255 (encima va texto). Si la madera o el oro del bloque común se cuelan, se repite sin el bloque. Es el #5 sin las tiras de oro |
| I5 | **Icono del instalador y del desinstalador** | `.ico` con 16, 24, 32, 48, 64 y 256 | no se genera: es E14 | `installerIcon`, `uninstallerIcon` → `app/src-tauri/icons/icon.ico` | — | ICO: `gimg export emblema.png icon.ico --icon-sizes 16,24,32,48,64,256` |
| I6 | **Cápsula vertical de la biblioteca de Steam** (Steam Deck) | 896×1152 → 768×1152 (recorte central) → 600×900 PNG | `portrait` 896×1152 | `app/src-tauri/steam/` (ruta por confirmar en `INS-51`) | Tall upright view. The belt of stardust rises from the lower left to the upper right through the lower half of the frame. Along the bottom quarter, a long dark timber palisade on a low hill between jagged dark rock spires in #0e0b08, with one thin line of old gold #b8862b across the lintel of its gate. The upper half, from the top edge downward, is plain calm sky in #1a2140, even and empty. | Prioridad media. `tarkor-lockup-v.svg` en la mitad superior, por composición. Tiene que leerse a 200 px de ancho. Si una semilla de I1 convence, se prueba antes su recorte a 704×1056. Aprobada por la persona el 2026-11-12: amplía la decisión 7 (Steam) junto con el icono 256² |

**Lo demás que pide el Instalador ya está en esta hoja** y allí solo se coloca: E14 (siete archivos en
`app/src-tauri/icons/`: `fuente.png` 1024, `icon.png` 512, `128x128@2x.png`, `128x128.png`, `64x64.png`,
`32x32.png`, `icon.ico`), #17 (estados, a 20 px y 64 px), E7 (`.pista`, `.relleno`), #9 (`.filete`), #2
(`.principal`, `.caja`), #3 (fondo de la ventana), **#5 (`.barra`, no el riel: el riel es vertical y lleva I4)**,
E13 (`.btn`), E3 (vista previa del repo en GitHub). Para la Deck, sin generar nada: cápsula horizontal 920×430
(E4 recortada a 1024×478), fondo 1920×620 (E5), logo 1280×720 transparente (`tarkor-lockup-v.svg`) e icono 256²
(E14).

## 4. Lo que ya hace el generador de Tarkor (y por eso no se pide)

`WMF-imagenes/image-generator` (README; `interfaz/adaptador_tarkor.py` l.67-122; `backend/src/services/imagePromptGenerator.ts`
l.49: `'thumbnail' | 'banner' | 'mapa' | 'icono'`):

- **Banners 1280×512 y miniaturas 768×768** de cada ficha de la enciclopedia: `construccion`, `fauna`, `flora`,
  `item`, `location`, `npc`, `raza`, `faction`, con variantes por sexo, raza y momento del día. Los pinta
  `CombatPanel.tsx` l.237, `Miniatura.tsx` l.15, `useEntityBanner.ts`, `LogPanel`.
- **Mapas de zona 832×624** (`entityType 'zona'`, `sizeProfile 'mapa'`; `world.ts` l.58) y por momento del día;
  el mapa base `frontend/src/assets/maps/helek-sirik-berig.png` sale de `map-generator/`.
- **Iconos 512×512** de asentamientos (`location` + `icono`, `world.ts` l.76), **habilidades, clases y
  especializaciones** (catálogo del adaptador l.111-122). Por eso el #10 pide solo el marco de la ranura, no los
  iconos de habilidad.
- Fases F0-F4 con LoRA de estilo, referencias con rol y perfil fotorreal (FLUX.3 en CPU); recorte con transparencia
  pendiente (IMG-37). Cuando IMG-37 llegue, los `[recorte]` de esta hoja podrían hacerse allí.

La **portada social / og:image** del juego (`frontend/index.html` no tiene `<meta property="og:image">`) es E3 del
bloque E: el perfil `og` existe en `examples/tarkor`, pero su plantilla `plantillas/og.svg` y su `compose` (logo
`tarkor-b-lockup.svg`, fuentes Metamorphous y Almendra) son de r7, archivada el 2026-11-10, y se rehacen con E3.

## 5. Orden de trabajo

1. **#1 emblema** (referencia de estilo, M8): 8-10 semillas con el prompt nuevo (`orders/ui/01-emblema.json` rehecho: repo, 2026-11-10),
   se elige por silueta a 32 px, piedra legible y cuatro puntas, y se guarda como referencia img2img. Se mide con
   `measure` que el oro quede en `#b8862b`-`#f2c45a` y la piedra en `#3a342d`, no en amarillo `quest` ni en blanco.
2. **Sistema de logo en SVG** (lo genera gimg con `gimg brand system`, desde el #1; D37): `tarkor-emblema.svg`, `tarkor-emblema-simple.svg`,
   `tarkor-wordmark.svg` (Cinzel 800 a trazos, modificada: §7 de la propuesta), `tarkor-lockup-h.svg`,
   `tarkor-lockup-v.svg`, `tarkor-glifo.svg` (E16). Con ellos, `favicon.svg` y el PNG 32/16, y E14.
3. **Marca fuera del juego**: E1 avatar, E2 cabecera, E3 og (plantilla nueva y `compose` con Cinzel e Inter), E4 Steam
   (header y main). Son las piezas que el Portal y las redes pueden publicar antes que nada del juego.
4. **Bloque A** en este orden: #2 tablón, #3 fondo, #5 banda, #6 cielo, #4 polvo, #7 defensa. Tras #2 y #3,
   comprobar contraste del texto `wood-100`/`wood-300` sobre ellos (≥ 4,5:1) antes de seguir.
5. **#16 medallón** (del #1), **#10 marco de ranura**, **E6 carga** y **E7 barra**: cierran lo que se ve en cada
   pantalla de juego y al arrancar.
6. **Bloque C**: #12 HUD (3) y #13 fases (8) primero, que se ven siempre; después #11 pestañas (12) y #14 dado;
   #15 categorías al final.
7. **Bloque B** #8 (dos variantes) y #9, **bloque D** #17, y lo que queda del bloque E: E9, E10, E11, E12, E13; E5,
   E17 y E18 al final.
8. Entrega en `examples/tarkor/entrega/ui/<nn>-<nombre>.png` y `entrega/marca/e<nn>-<nombre>.png` (más los recortes
   `-alpha.png` con la transparencia de gimg, D6), hoja de contactos (E18) y propuesta a los repos del juego y del
   instalador desde `docs/propuestas/tarkor/` (nunca se tocan desde aquí). La de la interfaz ya está escrita:
   `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md` (tokens, clases y tipografía se aplican sin esperar imágenes).

Tiempo estimado en la Deck (klein, 6 pasos): ~25 s por icono 512², ~70 s por 1024², ~60 s por 1536×640. Con 3
semillas por pieza, el total (48 piezas de A-D más unas 20 del bloque E) ronda las 3 h de GPU. Antes de generar: `curl localhost:11434/api/ps`,
`free -m`, `pgrep -x sd-cli` (gimg y el generador de Tarkor comparten GPU y Ollama; nunca `LIBERAR_OLLAMA=1`).

## 6. Dudas para la sesión principal

- **D1 · Logos frente a interfaz.** La interfaz real es madera, hierro y cristal azul (`index.css`, `@theme`) y no
  tiene ningún token de oro ni de noche índigo (lo más cercano, `cost-*` ámbar y `quest-*` amarillo); los logos son oro
  tallado sobre noche índigo. La mezcla pedida por la persona está escrita en §1 («la madera sostiene, el oro remata»)
  y en el bloque común. Quedan dos cosas por decidir: (a) si los seis hex de oro, bronce, noche y cristal verdoso
  propuestos en §1 entran como tokens en `index.css` del juego (propuesta desde `docs/propuestas/`) o se quedan solo
  en las imágenes; (b) si los paneles de madera llevan canto de oro **en la imagen** (#2, #7) o el canto va por CSS
  (`border` con el hex de oro) y las texturas quedan sin él, que es como está en esta hoja para que el mosaico cierre.
- **D2 · Violeta.** `biblia.md` §7 y `hoja.md` §6 vetan «purple/violet» (luz reservada del canon) y el cielo de los
  logos es azul-violeta. Los prompts piden «deep indigo blue» y no nombran `purple` ni `violet` (no hay negativo: regla P3). Confirmar que ese
  veto sigue vigente con los logos nuevos.
- **D3 · Favicon e icono del instalador.** A 16-32 px el emblema de seis gajos no se lee. Propuesta: #1 para 128 px en
  adelante (instalador `icon.png`, `128x128` a doble densidad, `apple-touch`), y una versión vectorial simplificada (aro + estrella
  de cuatro puntas) desde `tarkor-emblema-simple.svg` para 16-64 px. ¿Se hace aquí o se pide al instalador?
- **D4 · Los logos como marca.** ¿Los dos PNG sustituyen a los lockups SVG `tarkor-a/b` de `examples/tarkor/logos/` en
  `compose` (og) y en la biblia? Si sí, `biblia.md` §4 y §7 («lápiz de fantasía» r7) quedan obsoletas y hay que
  rehacer `estilo.txt`.
- **D5 · Iconos de habilidad.** El catálogo del adaptador de Tarkor incluye habilidades, clases y especializaciones,
  pero no he visto si ya hay iconos generados en `backend/uploads/images/`; si no los hay y no están previstos, el
  bloque C debería crecer con ellos (uno por habilidad, mismo marco #10).
- **D6 · Transparencia.** Mientras gimg no recorte, los `[recorte]` dependen de `convert`/ImageMagick en la Deck (fuera
  del producto). Si eso choca con D6 («todo nace del generador»), adelantar el recorte en gimg o esperar a IMG-37.
- **D7 · Estampa del mundo (#18).** Es la única pieza de paisaje; el juego podría preferir hacerla con su generador
  (mismo estilo que sus banners). Pedirla aquí solo si la persona la quiere en el estilo de los logos.

### Decisiones (sesión principal, delegadas por la persona, 2026-11-10)

- **D1:** el canto de oro va por CSS (`border`), no en la textura, para que el mosaico cierre. Los tokens de oro, piedra y
  noche entran en la interfaz por la propuesta `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md` (decisión 10:
  el bloque entero); aquí se usan en los prompts.
- **D2:** el veto sigue: «deep indigo blue», nunca violeta. Si sale violeta, se corrige el prompt, no la regla.
- **D3:** #1 sirve desde 128 px. La versión pequeña es `tarkor-emblema-simple.svg` (dos tintas, `gold-500` sobre
  `wood-950`; cortes de 1 px y estrella como rombo 3×5 a 16 px), generada aquí con gimg desde un emblema plano (D37); hasta entonces el
  instalador sigue con su icono.
- **D4 (resuelta el 2026-11-10 por la persona):** la dirección de los dos PNG **es la marca**; r7 («lápiz de fantasía»,
  New Rocker, arcilla, Semilla de hierro) queda archivada en `hoja.md`. `biblia.md` y `hoja.md` están rehechas con esa
  dirección; `tarkor-a/b` siguen en `logos/` solo como historia hasta que existan los SVG del punto 2 de §5, que
  sustituyen a `tarkor-b-lockup.svg` en `compose` (E3).
- **D5:** mirado el 2026-11-10 (solo lectura): `backend/uploads/images/` tiene 222 imágenes de contenido del mundo (fauna 61, location 62, zona 35, item 24, raza 19…) y solo 1 de `ability`; ningún icono de habilidad ni de interfaz, así que el bloque C no se solapa con lo que ya hay.
- **D6:** se genera con fondo verde plano igualmente; el recorte entra con la «Transparencia opcional» de gimg
  (`docs/plan.md`). Nada de ImageMagick a mano en lo que se entrega.
- **D7:** #18 queda fuera de esta hoja: casa mejor con los banners del generador de Tarkor; se propone allí.


**Decisiones 1-10 de `propuesta-fable-2026-11-10.md` §9: aprobadas por la persona el 2026-11-10 tal como se recomendaban**
(noche índigo fuera del juego; cuatro puntas cardinales; campo `#1f4a55`; luz de la Semilla en dos capas; Cinzel 800
modificada; arcilla fuera; Steam solo header y main; avatar = emblema; sin cursor; bloque de tokens entero al juego).
