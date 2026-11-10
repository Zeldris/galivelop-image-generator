# Tarkor — peticiones de recursos gráficos para gimg

Hoja de pedidos para el generador local (gimg, FLUX.2 klein 4B en la Steam Deck). Pide **solo lo que el generador
propio de Tarkor (WMF-imagenes) no produce** y que hoy en la interfaz es un emoji, un degradado CSS marcado como
provisional o un archivo de relleno. Forma tomada de la hoja del Portal (`docs/marca.md` de Portal-Galivelop,
«Recursos de imagen para el generador»). Escrita el 2026-11-10 leyendo los repos del juego en solo lectura.

## 0. Fuente

| Repo | Commit | Rama | Rutas leídas |
| --- | --- | --- | --- |
| `World-Maker-Fantasy` | `3537d84822185b5c5f04e0c70c03e4e6a1446078` | `claude/generador-mapas` | `frontend/src/index.css` (entero), `frontend/src/assets/fonts/fonts.css`, `frontend/public/favicon.svg`, `frontend/public/icons.svg`, `frontend/index.html`, `frontend/src/components/{Miniatura,PanelEmptyState,IconCard,Esqueleto,HealthBar,HungerBar,ThirstBar,EnergyBar,DiceRoll,SkillBarHud,SideNav,CollapsedRail,NavTabs,WorldCard,CharacterCard,GameHeader,ErrorBoundary,CombatPanel}.tsx`, `frontend/src/pages/Home.tsx`, `frontend/src/lib/{gamePhase,enciclopediaTargets}.ts`, `backend/src/services/imagePromptGenerator.ts` (l.49), `backend/src/routes/world.ts` (l.58-76, l.807) |
| `WMF-imagenes` | `735f5239adbe6409ba4a349869338fb65ece35c1` | — | `image-generator/README.md`, `image-generator/fichas/` (listado), `image-generator/interfaz/adaptador_tarkor.py` (l.1-125), `docs/producto/roadmap-imagenes.md` (extractos: bloques, IMG-37) |
| `Instalador-WMF-Tarkor` | `ce9f33aba0d2054591445ba43383678910966bc9` | — | `app/src/estilos.css` (entero), `app/src-tauri/icons/` (`icon.png` 512², `fuente.png` 1024²), `app/src-tauri/tauri.conf.json` (l.34), `docs/11-diseno-del-frontal.md` (l.135) |
| Este repo | rama `portal-marca` | — | `docs/marcas/tarkor/biblia.md` §7-8, `hoja.md` §6-7 y §15 (antiguas: mandan los repos del juego), `examples/tarkor/galivelop-images.json`, `examples/tarkor/logos/` |

**Referencia de calidad y estilo (dato de la persona, 2026-11-10):** los dos logos de
`examples/tarkor/logos/`: `Tarkor_ La semilla rota.png` (1672×941) y `Emblema dorado y título TARKOR.png` (2172×724).
Lo que enseñan: fantasía épica AAA; letras serif talladas en **oro viejo** con textura de piedra, biseles con puntas y
filos que rematan en espina; **emblema circular de oro** con una **semilla de piedra partida en seis gajos** y luz
dorada saliendo del centro; **anillos de energía** dorados girando alrededor; **estrellas de cuatro puntas**
brillantes como remates (en los cuatro puntos cardinales del anillo, en la O del título y bajo el subtítulo); el aro
exterior deja ver un fondo de **cristal azul-verdoso** entre los gajos; fondo nocturno **azul índigo profundo** con
montañas rocosas y un castillo de agujas. Los recursos de esta hoja casan con esa estética **y** con los tokens
reales de la interfaz (madera, hierro, cristal azul). Donde chocan, está en «Dudas».

## 1. La estética: madera de la interfaz + oro y piedra de los logos

Precisión de la persona (2026-11-10): la estética de esta hoja es **la de los logos mezclada con la hoja actual de
la interfaz del juego**, más lo que haga falta para que todo llegue a la calidad del logo y de su fondo. En
concreto:

| Capa | De dónde viene | Qué aporta |
| --- | --- | --- |
| **Base: madera, hierro y cristal** | `World-Maker-Fantasy/frontend/src/index.css`, bloque `@theme` (l.1-60: `--color-wood-*`, `--color-iron-*`, `--color-accent-*`, `--color-accent2-*`) y sus clases `.wood-grain` l.129, `.plank-panel` l.167, `.iron-band` l.216, `.crystal-sky` l.269, `.rivet` l.324 | Todo fondo y toda superficie grande es **madera oscura con veta** (tablones `wood-800/700`, fondo `wood-950/900`) o **hierro forjado** (`iron-800/700`, con remaches). El cristal azul `accent-500` es el único acento frío. La luz de la interfaz es cálida y baja (ámbar sobre madera). |
| **Ornamento: oro tallado, piedra, semilla rota, estrellas** | `examples/tarkor/logos/Tarkor_ La semilla rota.png` y `Emblema dorado y título TARKOR.png` | Marcos, cantos, remates, emblemas y pictogramas son **oro viejo tallado** con textura de piedra, biseles vivos y puntas en espina; los remates son **estrellas de cuatro puntas** que brillan; el motivo central es la **semilla de piedra partida en seis gajos** con luz dorada saliendo del centro y **anillos de energía** alrededor. |
| **Acabado AAA (toques añadidos para llegar a la calidad del logo)** | Decisión de esta hoja | Luz rasante dorada desde arriba-izquierda sobre el oro y la madera (la del logo), sombras frías y profundas en las hendiduras, **cristal azul con facetas y luz interior** en las estrellas y gemas (une el acento `accent-500` de la interfaz con el brillo de los logos), grano fino visible en madera y piedra, bordes nítidos, sin niebla ni desenfoque, y un velo nocturno índigo (el fondo de los logos) solo en el cielo y la estampa. Nada plano, nada «flat vector»: todo con volumen y materia. |

Regla de reparto: **la madera sostiene, el oro remata**. Un panel es madera con canto de oro, no un panel de oro; un
pictograma es oro y piedra sobre el hierro o la madera del fondo; la semilla rota y la estrella aparecen como emblema,
remate o gema, nunca como relleno.

### Paleta para las imágenes

Hex del CSS real (`frontend/src/index.css`, bloque `@theme`), más los tonos de oro, piedra y noche que los logos traen
y el CSS no tiene (medidos a ojo sobre los PNG; propuestos, marcados con *).

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
| Oro viejo tallado (cuerpo del metal) * | — | `#b8862b` |
| Oro claro (biseles, filos, luz rasante) * | — | `#f2c45a` |
| Resplandor dorado (centro de la semilla, estrellas) * | — | `#ffd66b` |
| Bronce oscuro (sombra del oro, hendiduras) * | — | `#5a3a14` |
| Noche índigo (cielo de los logos) * | — | `#1a2140` |
| Cristal verdoso del aro del emblema * | — | `#2f6b7a` |
| Arcilla de marca (`brand.palette` de `examples/tarkor`) | — | `#E0703A` |

Atributos (solo si algún día se piden sus pictogramas): fuerza `#cc5852`, destreza `#3fb89d`, constitución `#9566cc`,
inteligencia `#6bb83f`, voluntad `#cca63f`, carisma `#cc5794`, magia `#5772cc`.

Tipografía de la interfaz (para saber con qué conviven los recursos, **nunca para pintar letras**): Cinzel en
títulos (`--font-serif`), Inter en texto, Cascadia Code en números. Radios: píldoras `rounded-full`, botones `md`,
tarjetas `lg`, paneles `xl`, ranura de habilidad 3 px (`.skill-slot`).

## 2. Cómo pedirlas

- **Bloque común** (se antepone a cada prompt, en inglés; escribe la mezcla de §1 en tres frases: base de la
  interfaz, ornamento de los logos, acabado AAA):

  > Epic fantasy game interface asset with the finish of a AAA title screen. Base materials from the game's
  > interface: aged dark wood planks with fine visible grain in #332415 and #46311d, dark forged iron in #171310
  > with small rivets, faceted blue crystal in #4aa8d8. Ornament materials from the game's emblem: old carved gold
  > in #b8862b with a chiselled stone texture, sharp bevelled edges and spiked tips, highlights in #f2c45a, deep
  > bronze shadows in #5a3a14; glowing four-pointed stars, thin rings of golden energy, and a stone seed split into
  > six wedges with golden light #ffd66b pouring from its core. The wood and iron carry the piece, the gold trims
  > and crowns it. Lighting: warm golden raking light from the upper left, deep cool shadows in every groove, inner
  > glow inside the crystal. Painterly realism with fine grain, crisp edges, high contrast, rich colour, volume and
  > weight in every material, every surface solid and tactile.

- **Negativo** (gimg aún no tiene campo para él; se deja aquí, como en la hoja del Portal, para cuando lo tenga o
  para pegarlo a mano en sd-cli):

  > text, letters, words, logo, watermark, signature, caption, numbers, people, person, human, face, hands,
  > character, creature, cartoon, flat vector, clipart, emoji, low detail, blurry, soft focus, noise, jpeg
  > artifacts, oversaturated neon, purple, violet, pink, sun disc, moon, photo of a screen, frame cut off,
  > cropped, asymmetric, tilted, perspective view.

- **Nada de letras** en ningún recurso: el título va en Cinzel desde el CSS y el logo desde los SVG.
- **Transparencia:** gimg no la hace todavía. Lo que la necesita (pictogramas, esquinas, separadores, emblema) se
  pide sobre **fondo liso de un solo color** para recortar luego: verde `#00ff00` cuando la pieza no lleva verde
  (todas las de aquí) y se marca `[recorte]` en la columna de notas. La pieza se pide **centrada, con margen libre
  del 15 %** por cada lado, de frente, sin perspectiva.
- **Mosaico (texturas):** FLUX no genera mosaicos perfectos. Se pide «seamless tileable» igual, se generan 2-3
  semillas y se arregla la costura con `convert ... -virtual-pixel tile -blur` o a mano. Para fondos de
  `background-size: cover` (cielo, estampa) no hace falta.
- **Perfiles de generación:** tamaño múltiplo de 64 y ≤ 1 048 576 px (Deck). Sugeridos para `galivelop-images.json`
  del proyecto: `textura` 1024×1024, `banda` 1024×256, `cielo` 1536×640, `icono` 512×512, `emblema` 1024×1024,
  `estampa` 1280×512 (ya existe como `banner`), `tira` 1024×128. `steps` 6, `cfg` 1.0, `euler`, 2-3 semillas por
  pieza y se elige.
- **Modelo:** FLUX.2 klein primero. En la columna «Modelo»: **K** = klein debería bastar; **K?** = probar con
  klein, probable que haga falta el perfil de más calidad (FLUX.3 klein en CPU del generador de Tarkor, 50-60 min
  por pieza, o Qwen-Image 2.1) o retoque a mano; **M** = casi seguro modelo mejor o trabajo vectorial.
- **Destino:** carpeta nueva `frontend/src/assets/ui/` del juego (Vite resuelve `url()` desde `index.css`), salvo
  donde la tabla diga otra. Esta hoja no toca el repo del juego: la entrega se deja en `examples/tarkor/entrega/ui/`
  y se propone desde aquí (`docs/propuestas/`).

## 3. Recursos

Orden: la pieza de referencia primero; después bloques A-D por prioridad. «Medidas» es lo que se entrega;
«Perfil» lo que se genera.

### Referencia de estilo

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Emblema de la semilla rota** (pieza de referencia: fija el oro, la piedra y la luz para todo lo demás) | 1024×1024 PNG; de él salen 512² (icono del instalador), 192² y 32² (favicon PNG), 96² (placeholder #16) | `emblema` 1024×1024 | `frontend/public/favicon.svg` es un rayo violeta genérico sin relación con la marca (`#863bff`, `#7e14ff`, `#47bfff`): se sustituye por PNG + `<link rel="icon">` en `frontend/index.html` (hoy sin `<link>`). Instalador: `app/src-tauri/icons/icon.png` y `fuente.png` son hoy un rombo azul plano sobre disco marrón, sin relación con los logos (`tauri.conf.json` l.34). | A circular emblem seen straight on, centred on a flat solid bright green background. A thick ring of old carved gold with chiselled stone texture, sharp bevelled edges and four short spiked points at top, bottom, left and right, each point tipped with a small glowing four-pointed star. Inside the ring, a dark teal faceted crystal field. At the centre, a round stone seed split into six wedges, dark cracked rock with golden light pouring out from the core between the wedges, two thin rings of golden energy orbiting it at an angle. Symmetric, game icon, 15 percent empty margin on every side. | `[recorte]` fondo verde. **K?**: klein hace bien el oro y la luz; los seis gajos y la simetría del aro piden varias semillas (6-10) o retoque. El favicon a 32 px pierde los gajos: para 16-32 px, versión simplificada vectorial desde `tarkor-b.svg` (duda D3). |

### Bloque A — fondos y texturas (hoy degradados CSS marcados como provisionales)

`index.css` l.150: «Provisional: esto se sustituirá por fondos generados de verdad cuando exista la API de prompts
de imagen». Las clases: `.wood-grain` l.129, `.dust-road` l.152, `.plank-panel` l.167, `.plank-panel-defense` l.193,
`.iron-band` l.216, `.crystal-sky` l.269, `.iron-etched` l.292. El instalador copia las mismas ideas en CSS:
`.riel` (`estilos.css` l.31-33) y `.principal` (l.49-53).

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | **Tablón de panel** (madera oscura con veta, para tarjetas y paneles) | 1024×1024 PNG, mosaico; se usa a 50 % (512 px CSS) | `textura` 1024×1024 | `.plank-panel` (`index.css` l.167): WorldCard, CharacterCard, botones de `Home.tsx` l.41, PanelDrawer, CombatModal; `.principal` del instalador (l.49-53) | Seamless tileable texture of aged dark wood planks seen straight on, wood colours #332415 and #46311d with lighter grain lines in #7a5934, fine straight grain, a few tight knots, soft worn surface, subtle warm light from the upper left, even exposure across the whole image, flat, edge to edge, top view. | **K**. 2-3 semillas; costura con `-virtual-pixel tile`. Los remaches (`.rivet` l.324) y el borde siguen en CSS. |
| 3 | **Madera de fondo de página** (más oscura y sorda que el tablón) | 1024×1024 PNG, mosaico | `textura` 1024×1024 | `.wood-grain` (`index.css` l.129): fondo de `App.tsx`, `ErrorBoundary.tsx` l.32, `GamePanelCajon.tsx`, `LogPanel.tsx` | Seamless tileable texture of very dark aged wood seen straight on, nearly black brown #1b130c with faint grain in #241a10 and sparse hairline highlights in #332415, matte, low contrast, calm, even exposure, flat, edge to edge, top view. | **K**. Debe quedar por debajo del tablón en luminosidad (YAVG < 40) para que el texto `wood-100` siga en AA. |
| 4 | **Camino de polvo** (fondo del panel de narración) | 1024×1024 PNG, mosaico | `textura` 1024×1024 | `.dust-road` (`index.css` l.152), usado en `LogPanel.tsx` y `ChatComposer.tsx` | Seamless tileable texture of packed dry earth and fine red dust seen straight on, colours #241a10 and #332415 with scattered tiny grains in #a3814f and #E0703A, faint dragged marks, matte, very low contrast, even exposure, flat, edge to edge, top view. | **K**. Es el fondo del texto largo: contraste bajísimo, sin motivos que se lean como letras. |
| 5 | **Banda de hierro y oro** (cabecera y pie del juego, riel del instalador) | 1024×256 PNG, mosaico horizontal | `banda` 1024×256 | `.iron-band` (`index.css` l.216): `GameHeader.tsx` l.93, `GameFooter`; `.iron-etched` l.292 en botones; `.riel` del instalador (l.31-33) | Seamless horizontally tileable band of dark forged iron seen straight on, colour #171310 with a faint engraved grid of fine lines in #52626f, a thin bevelled strip of old carved gold #b8862b along the top edge and another along the bottom edge, matte metal with subtle scratches, even exposure, flat, edge to edge. | **K**. La tira de oro debe medir ~6 px de los 256 para no competir con el texto de la cabecera. |
| 6 | **Cielo nocturno de cristal** (pantalla de inicio y tarjeta de Helek Sirik) | 1536×640 PNG, `background-size: cover` | `cielo` 1536×640 | `.crystal-sky` (`index.css` l.269): `Home.tsx` l.20, `WorldCard.tsx` l.25 (solo `helek-sirik`) | Wide night sky of deep indigo #1a2140 fading to near black at the top, a slanted belt of glowing dust across the sky in pale blue #4aa8d8 and #a8d8f0, scattered small four-pointed stars with soft golden #ffd66b glints, tiny floating crystal shards catching the light, faint silhouettes of jagged rock spires and a distant castle of thin towers along the bottom edge in #0e0b08, atmospheric haze, cinematic matte painting, calm, the lower third darker and emptier for interface elements. | **K**. Canon del juego: la noche es un cinturón de polvo que brilla, con velo perlado y **sin luna** (vetada). El tercio inferior libre es donde cae el título de `Home.tsx` l.29-30. |
| 7 | **Tablón de defensa** (variante azul-acero del #2) | 1024×1024 PNG, mosaico | `textura` 1024×1024 | `.plank-panel-defense` (`index.css` l.193); `CombatPanel.tsx` l.474 explica que hoy se tiñe el `background-image` del tablón, cosa que con un PNG ya no vale | Seamless tileable texture of aged dark wood planks seen straight on, the wood stained a cold blue grey, colours #221c16 and #52626f with grain lines in #6b7d8c and a faint cold sheen of #3488b8, fine straight grain, a few tight knots, even exposure, flat, edge to edge, top view. | **K**. Misma semilla y misma composición que el #2 si se puede (img2img del #2 a 0,3 con este prompt). |

### Bloque B — marcos y ornamentos (hoy pseudoelementos CSS)

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | **Esquina ornamental** (una; las otras tres por volteo) | 512×512 generado → 128×128 PNG entregado (se usa a 32-48 px) | `icono` 512×512 | `.corner-bracket` (`index.css` l.300-322: escuadra de hierro con borde dorado hecha en CSS), usado en `ModalShell.tsx` y `DetailModal.tsx` | A single corner ornament for a frame, occupying the top left quadrant, on a flat solid bright green background: two short arms of old carved gold meeting at a right angle, chiselled stone texture, sharp bevels, each arm ending in a spiked point, a small glowing four-pointed star set in the joint, dark iron rivets along the arms, straight on, crisp edges, 15 percent empty margin. | `[recorte]` verde. **K?**: a 32 px el detalle se pierde; pedir pocas formas y gruesas. Las otras esquinas, con `transform: scaleX(-1)` etc. |
| 9 | **Separador horizontal con estrella** (filete que se desvanece con remate central) | 1024×128 generado → 1024×64 PNG | `tira` 1024×128 | `.accent-hairline` + `.gem` (`index.css` l.226 y l.246): `Home.tsx` l.24-27 y l.31-34; `.filete` del instalador (`estilos.css` l.60) | A thin horizontal divider centred on a flat solid bright green background: a hairline of old carved gold that fades out towards both ends, and at its centre one small four-pointed star of faceted blue crystal #4aa8d8 set in a gold mount with a soft golden glow, symmetric, straight on, crisp, the band occupies only the middle fifth of the height. | `[recorte]` verde. **K**. Si no sale limpio, el filete sigue en CSS y solo se recorta la estrella (64×64) para `.gem`. |
| 10 | **Marco de ranura de habilidad** (anillo de oro para encajar el icono de cada habilidad) | 512×512 generado → 88×88 PNG (ranura 44 px @2x) | `icono` 512×512 | `.skill-slot` (`index.css`: 44×44, radio 3 px; el icono es un emoji) y `SkillBarHud.tsx` l.63; `IconCard.tsx` l.62 | A square slot frame for a game hotbar, centred on a flat solid bright green background: a square border of old carved gold with chiselled stone texture, sharp bevelled edges, a tiny four-pointed star at each corner, the inside of the square empty and filled with the same flat bright green, straight on, symmetric, 15 percent empty margin. | `[recorte]` verde por fuera **y por dentro**. **K**. Los iconos que van dentro los hace el generador de Tarkor (habilidades, clases: §4). |

### Bloque C — pictogramas de interfaz (hoy emojis del sistema)

Un prompt por pictograma, misma plantilla; se generan a 512×512 y se entregan a 128×128 y 64×64. Se usan a 20-32 px
(`SideNav`, `CollapsedRail`, barras) y a 40-48 px (`PanelEmptyState`, `IconCard`). Plantilla (tras el bloque común):

> Single game interface icon of {motivo}, centred on a flat solid bright green background, made of old carved gold
> with chiselled stone texture and sharp bevels over dark forged iron, a faint golden glow at its edges, straight
> on, symmetric where possible, bold simple silhouette readable at small size, 15 percent empty margin on every
> side.

| # | Recurso | Medidas | Perfil | Dónde va | {motivo} de cada pieza | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | **Pestañas del cajón** (12) | 128² y 64² PNG | `icono` 512×512 ×12 | `NavTabs.ts` l.23-41 (hoy ⚔️ 🎒 ✨ 👥 🏰 🗺️ 📖 📕 🎯 🤝 📚) y `PersonajePanel.tsx` l.22 (equipo ⚔️); se pintan en `SideNav.tsx` l.60 y `CollapsedRail.tsx` l.24; reutilizables en `PanelEmptyState.tsx` l.16 y las notificaciones (`notificaciones.ts`: 🎒 🎯) | personaje: a straight sword pointing up · inventario: a closed leather satchel with a buckle · habilidades: a four-pointed star of blue crystal · compañeros: two crossed spears over a small round shield · reino: a timber palisade with a single watchtower · mapa: a rolled parchment with a wax seal · diario: an open book · leyendas: a closed book with an iron clasp · misiones: a hanging banner on a crossbar with a four-pointed star · reputación: two interlocked iron rings · enciclopedia: a stack of three stone tablets · equipo: a horned iron helmet seen from the front | `[recorte]` verde. **K?**: klein da bien la materia; a 20 px hace falta silueta gruesa. Generar 3 semillas y elegir; si no leen a 20 px, vectorizar a mano sobre el PNG (**M**). Sin figuras humanas (vetadas): compañeros y reputación van por objetos. |
| 12 | **Barras de estado del HUD** (3) | 64² y 32² PNG | `icono` 512×512 ×3 | `HungerBar.tsx` l.16 (🍖), `ThirstBar.tsx` l.14 (💧), `EnergyBar.tsx` l.9 (⚡) | hambre: a roasted joint of meat on a bone · sed: a single drop of water, faceted, in blue crystal · energía: a small flame rising from an iron brazier | `[recorte]` verde. **K**. Se usan a 16-20 px: una sola forma cada uno. |
| 13 | **Fases del juego** (8) | 64² y 32² PNG | `icono` 512×512 ×8 | `gamePhase.ts` l.107-116 (`ETIQUETA_FASE`: ✒️ 🧭 ⚠️ ⚔️ 💬 ⭐ 💀 📜), mostrada en `GameHeader` / `GameFooter` | pensando: a quill pen · ocupado: a compass rose with a four-pointed needle · encuentro: a curved war horn · combate: two crossed swords · dinámico: a small campfire · elección: a four-pointed star of blue crystal in a gold mount · muerte: a cracked stone skull of a horned beast · fin: a rolled scroll with a hanging wax seal | `[recorte]` verde. **K**. «combate» puede compartir pieza con la pestaña personaje si se prefiere una sola espada; «elección» comparte con la estrella del #9. |
| 14 | **Dado de hueso** | 64² y 32² PNG | `icono` 512×512 | `DiceRoll.tsx` l.113 (🎲 fijo junto al número que gira) | a six-sided die carved from pale bone #e3cba8 with golden pips, seen from a corner showing three faces | `[recorte]` verde. **K**. |
| 15 | **Categorías de objeto** (15, respaldo cuando la ficha no tiene miniatura) | 64² PNG | `icono` 512×512 ×15 | `enciclopediaTargets.ts` l.191-220 (`itemIcon`, por defecto 📦) y l.40-56 (`ITEM_CATEGORY_ORDER`: especial, arma, herramienta, ropa, accesorio, armadura, cosmetico, consumible, medicinal, alimento, documento, valor, piel, hueso, madera); se pinta en `Miniatura.tsx` l.16 a 32 px | especial: a four-pointed star · arma: a short axe · herramienta: a hammer and a chisel crossed · ropa: a folded hooded cloak · accesorio: a ring with a small blue gem · armadura: a breastplate · cosmetico: a small clay pot with a lid · consumible: a corked round flask · medicinal: a bundle of dried herbs tied with cord · alimento: a loaf of bread · documento: a folded letter with a wax seal · valor: a stack of three gold coins · piel: a stretched animal hide on a frame · hueso: a single long bone · madera: three stacked logs | `[recorte]` verde. **K**. Prioridad baja: la mayoría de fichas ya traen miniatura del generador de Tarkor; este juego cubre los huecos. |
| 16 | **Medallón de ficha sin imagen** (placeholder de miniatura y retrato) | 768×768 PNG (se muestra a 32-96 px y en el `aspect-[2.5/1]` del combate recortado) | `emblema` 1024×1024 | `Miniatura.tsx` l.16 (emoji cuando no hay `thumbnail`), `CombatPanel.tsx` l.758 (⚔️ cuando no hay retrato), `MediaSlot` de `ImagePromptDisplay.tsx` | A round medallion of aged dark wood #332415 with a rim of old carved gold, at its centre the six-wedge stone seed emblem in low relief with a faint golden glow from its core, four small four-pointed stars around the rim, straight on, symmetric, soft vignette, square image, the medallion fills the frame edge to edge. | Sin recorte (fondo del propio medallón). **K**. Derivado del #1 (img2img 0,4) para que el emblema sea el mismo. |

### Bloque D — instalador y escaparate

| # | Recurso | Medidas | Perfil | Dónde va | Prompt (tras el bloque común) | Notas |
| --- | --- | --- | --- | --- | --- | --- |
| 17 | **Estados de las comprobaciones del instalador** (4) | 64² y 32² PNG | `icono` 512×512 ×4 | `Instalador-WMF-Tarkor/docs/11-diseno-del-frontal.md` l.135: «7 comprobaciones ... con un icono de estado cada» (sin recurso propio; `estilos.css` solo colorea `.pasos li.hecho/.actual`) | plantilla del bloque C con: hecho: a four-pointed star of blue crystal #4aa8d8 in a gold mount, glowing · aviso: a four-pointed star of amber crystal #f59e0b in a gold mount · error: a four-pointed star of red crystal #ef4444 in a gold mount, dimmed · en curso: a compass rose of old gold with a four-pointed needle | `[recorte]` verde. **K**. Una sola forma (la estrella de los logos) con cuatro colores: coherente y legible a 20 px. «hecho»/«aviso»/«error» pueden salir de una pieza recoloreada en HSL. |
| 18 | **Estampa del mundo Helek Sirik** (cabecera de la tarjeta de mundo) | 1280×512 PNG, `object-cover` | `estampa` 1280×512 (= `banner`) | `WorldCard.tsx` l.24-25: hoy `plank-panel` + `crystal-sky` por CSS; no hay imagen de mundo. El generador de Tarkor hace banners **de entidades** (fauna, flora, NPC, lugar), no una portada del mundo | Wide panoramic view of a wild land seen from a high ridge at the last light of day: dark iron rock spires rising from red sand crests, a long timber palisade with banners on a far hill, a thin line of campfire smoke, a cold deep indigo sky with the first glowing belt of dust and a few four-pointed stars, warm raking light from low on the right, atmospheric haze, cinematic matte painting, the left third calmer and emptier. | **K?**: paisaje es lo que klein mejor hace, pero la coherencia con los banners del juego (Qwen/ChatGPT) puede pedir FLUX.3. Motivos del canon (Agujas Imán, empalizada de Telda) de `biblia.md` §7. Zona libre a la izquierda para el nombre del mundo. |

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

Fuera de esta hoja: la **portada social / og:image** del juego (`frontend/index.html` no tiene `<meta property="og:image">`)
ya tiene perfil `og` y plantilla en `examples/tarkor` (r7 pendiente de la persona); no se duplica aquí.

## 5. Orden de trabajo

1. **#1 emblema** (referencia de estilo): 6-10 semillas, se elige una y se guarda como referencia de estilo del
   proyecto. Se mide con `measure` que el oro quede en `#b8862b`-`#f2c45a` y no en amarillo `quest`.
2. **Bloque A** en este orden: #2 tablón, #3 fondo, #5 banda, #6 cielo, #4 polvo, #7 defensa. Tras #2 y #3,
   comprobar contraste del texto `wood-100`/`wood-300` sobre ellos (≥ 4,5:1) antes de seguir.
3. **#16 medallón** (del #1) y **#10 marco de ranura**: cierran lo que se ve en cada pantalla de juego.
4. **Bloque C**: #12 HUD (3) y #13 fases (8) primero, que se ven siempre; después #11 pestañas (12) y #14 dado;
   #15 categorías al final.
5. **Bloque B** #8 y #9, y **bloque D** #17 y #18.
6. Entrega en `examples/tarkor/entrega/ui/<n>-<nombre>.png` (más los recortes `-alpha.png` hechos con
   `convert -fuzz 8% -transparent '#00ff00'`), hoja de contactos por bloque y propuesta a los repos del juego y del
   instalador desde `docs/propuestas/` (nunca se tocan desde aquí).

Tiempo estimado en la Deck (klein, 6 pasos): ~25 s por icono 512², ~70 s por 1024², ~60 s por 1536×640. Con 3
semillas por pieza, el total (48 piezas) ronda las 2 h de GPU. Antes de generar: `curl localhost:11434/api/ps`,
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
  logos es azul-violeta. Los prompts piden «deep indigo blue» y el negativo lleva `purple, violet`. Confirmar que ese
  veto sigue vigente con los logos nuevos.
- **D3 · Favicon e icono del instalador.** A 16-32 px el emblema de seis gajos no se lee. Propuesta: #1 para 128 px en
  adelante (instalador `icon.png`, `128x128` a doble densidad, `apple-touch`), y una versión vectorial simplificada (aro + estrella
  de cuatro puntas) desde `tarkor-b.svg` para 16-64 px. ¿Se hace aquí o se pide al instalador?
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

- **D1:** el canto de oro va por CSS (`border`), no en la textura, para que el mosaico cierre. Los 6 hex propuestos
  entran en la interfaz solo por una propuesta al juego en `docs/propuestas/`; aquí se usan en los prompts.
- **D2:** el veto sigue: «deep indigo blue», nunca violeta. Si sale violeta, se corrige el prompt, no la regla.
- **D3:** #1 sirve desde 128 px. La versión pequeña (aro + estrella) se hace aquí con el paso a SVG de `docs/plan.md`
  cuando exista; hasta entonces el instalador sigue con su icono.
- **D4:** los dos PNG son la referencia de estilo, no sustituyen aún a `tarkor-a/b` en `compose`: hace falta una
  versión vectorial del logo nuevo. La biblia se rehace cuando la persona confirme el cambio de marca.
- **D5:** pendiente: mirar en solo lectura si `backend/uploads/images/` tiene iconos de habilidad antes del bloque C.
- **D6:** se genera con fondo verde plano igualmente; el recorte entra con la «Transparencia opcional» de gimg
  (`docs/plan.md`). Nada de ImageMagick a mano en lo que se entrega.
- **D7:** #18 queda fuera de esta hoja: casa mejor con los banners del generador de Tarkor; se propone allí.
