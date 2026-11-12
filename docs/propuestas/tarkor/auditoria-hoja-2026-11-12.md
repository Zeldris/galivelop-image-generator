# Auditoría de las canónicas de Tarkor frente a sus repos (2026-11-12)

Qué dicen `docs/marcas/tarkor/{hoja,biblia,peticiones,pedido-mapa}.md` que ya no casa con los repos. Los repos se
leyeron sin tocarlos (`git fetch` y `git show`), el 2026-11-12.

**Estado de los repos leídos**

| Repo | Ref | Commit | Fecha |
|---|---|---|---|
| World-Maker-Fantasy | `origin/main` | `3a10a3fa` | 2026-11-11 |
| World-Maker-Fantasy | `origin/claude/marca-interfaz` (UX-40, **sin fusionar**) | `c858a150` | 2026-11-10 |
| World-Maker-Fantasy | `origin/claude/pedido-mapa` | `1fe72655` | — |
| Instalador-WMF-Tarkor | `origin/main` | `5631e77b` | 2026-11-11 |
| Instalador-WMF-Tarkor | `origin/claude/installer-docs-review-09e7vs` | `34d2bb27` | 2026-11-12 |
| WMF-imagenes | clon del mismo origen que World-Maker-Fantasy (mismas ramas) | `main` local `04f693a9` | — |
| galivelop-image-generator | `agent/hojas-tarkor` | `3c04dd1` | 2026-11-12 |

## Hallazgos

Gravedad: **C** contradice (dos fuentes dicen cosas distintas), **D** desfasado (era cierto, ya no), **H** hueco (falta).

| # | G | Dónde (canónica) | Qué dice | Qué hay en el repo (fuente) | Arreglo |
|---|---|---|---|---|---|
| A1 | C | `hoja.md` l.148 | E14, icono de app: emblema simple sobre madera 950 | Disco `night-950` `#0f1428`: `peticiones.md` l.221 y decisión del Instalador, `docs/13-hoja-de-estilos-e-imagenes.md` §6.1 (`608661d`, rama `34d2bb27`) | Hoja → noche. Hecho en este cambio |
| A2 | D | `hoja.md` l.12-18, l.42, l.220-224; `peticiones.md` §0; `biblia.md` §10 | Citan World-Maker-Fantasy `e3778e61`/`3537d84` e Instalador `a73f881`/`ce9f33a` | `main` del juego es `3a10a3fa`; `main` del Instalador es `5631e77b` y su trabajo de marca está en `34d2bb27` | Citas al día en la tabla de fuentes de la hoja (§18) |
| A3 | D | `hoja.md` §1-§5 (eyebrow en `accent-400`, tokens «propuestos», sin `og:`) | La marca en la interfaz es una propuesta | Aplicada en `c858a150` (UX-40, «comprobada en pantalla»), **sin fusionar a `main`**: `frontend/src/index.css` trae `gold-100…900` (l.55-59), `stone-500/700` (l.61-62), `night-900/950` (l.64-65), `crystal-deep` (l.66), `.gold-hairline` (l.277), `.corner-bracket-gold` (l.372), `.title-gold` (l.462); `frontend/index.html` añade `theme-color #1b130c`, `og:title` y `og:description`; `Home.tsx` usa `gold-hairline`, eyebrow `text-wood-200` y h1 `title-gold`. En `main` (`3a10a3fa`) esos tokens no existen | Hoja §18 distingue «aplicado en rama» de «en `main`»; entrega al juego pide la fusión |
| A4 | H | `hoja.md` l.20-24 | «ni og ni favicon» | Sigue sin `og:image` ni `<link rel="icon">` propio; `frontend/public/favicon.svg` de Vite sigue en `3a10a3fa`. UX-41 («la marca con imágenes», `docs/producto/roadmap-front-ux.md` §4.8 en `c858a150`) espera las piezas de aquí | Entrega al juego, puntos 3 y 4 |
| A5 | D | `hoja.md` l.171-172 y §13 l.204-205 | `docs/difusion/guia-canales.md` | La ruta es `docs/media/guia-canales.md` (`3a10a3fa`); junto a ella, `docs/media/README.md` y `docs/media/_plantilla/media/source/{tarjeta,diagrama}.html` | Ruta corregida en la matriz (§17) |
| A6 | H | `hoja.md`, `peticiones.md` | No existen las piezas del asistente | El Instalador pide I1-I6 en `docs/13-hoja-de-estilos-e-imagenes.md` §3 (`d9d33fe`, dudas resueltas en `608661d`) y un perfil `lateral` 704×1344 | Bloque «Instalador» en `peticiones.md`; filas en la matriz; perfil → hueco de gimg |
| A7 | C | `peticiones.md` #5 | Barra de hierro para el `.riel` del Instalador | El riel es vertical y lleva su propia textura (I4, mosaico en las dos direcciones); #5 va a `.barra` (doc 13 l.65) | Corregido en el bloque «Instalador» |
| A8 | D | `biblia.md` §4 | «Los SVG no existen todavía: se dibujan a mano» | Existen 18 archivos en `docs/marcas/tarkor/logos/` desde el 2026-11-10, generados con `gimg brand`. Además contradice la regla «nada a mano» | Biblia §4 (pendiente, ver «Sin hacer») |
| A9 | D | `biblia.md` §7-§9 | Negativo y negaciones en el prompt; «todo sale por img2img del #1»; `01-emblema.json` «lleva aún el prompt anterior»; perfiles «por declarar» | La hoja prohíbe negaciones (reglas del 2026-11-11) y el emblema se compone desde el SVG; `examples/tarkor/galivelop-images.json` declara 23 perfiles | Biblia §7-§9 (pendiente) |
| A10 | D | `peticiones.md` l.117-119, l.123 | «costura a mano»; `steps 6` | gimg tiene `tileable` (`texturamapa` `xy`, `marcomapa` `x` en `examples/tarkor/galivelop-images.json`); entrega con Z-Image a 8 pasos (hoja) | Nota de vigencia al principio del bloque «Instalador»; el resto, pendiente |
| A11 | C | `peticiones.md` E2 y #6 | Prompts con «distant castle» y «four-pointed stars» | El doc 13 del Instalador lista `castle` entre las vetadas; la hoja prohíbe que el modelo pinte el emblema o estrellas de cuatro puntas | Pregunta 5; reescritura de E2 y #6, pendiente |
| A12 | C | Instalador, `docs/13-…md`, tabla de paleta | Llama `iron-950` a `#0e0b08` e `iron-900` a `#171310` | En el juego son `iron-900` `#0e0b08` (index.css l.35) e `iron-800` `#171310` (l.36), `c858a150`; `iron-950` no existe | Entrega al Instalador, punto 1 |
| A13 | C | Instalador, `app/src/estilos.css` (`34d2bb27`) | Sin tokens `gold-*`, `night-*`, `stone-*`; `.filete` y `.btn.pri` en `accent` (cristal); `.btn.pri { color: #fff }`; Cinzel 400/600/700 | La hoja reserva el cristal a foco y enlace, prohíbe el blanco puro y pone el filete en oro (su INS-56, pendiente) | Entrega al Instalador, puntos 2-4 |
| A14 | C | World-Maker-Fantasy, `.claude/gw/gw-media-content.md` (`3a10a3fa`) | Tarjetas con la paleta del Portal (`#06121c`, `#0c1d2b`, `#1b3447`, `#eaf4fa`, `#1aa6df`), DejaVu/Liberation Sans, 1600×900 | La hoja pide noche + oro y Cinzel e Inter fuera del juego | Entrega al juego, punto 5 |
| A15 | D | `hoja.md` §13 l.232 | «Este repo, f2-motor `5460d2c`»; paleta de 10 hex | `brand.palette` de `examples/tarkor/galivelop-images.json` tiene 16 hex; rama actual `3c04dd1` | Tabla de fuentes (§18) |
| A16 | H | `hoja.md` decisión 7 | Steam: solo cabecera y cápsula principal | El Instalador pide además, para Steam Deck: cápsula vertical 600×900 (I6), horizontal 920×430, fondo 1920×620, logo 1280×720 transparente, icono 256² (doc 13 §3) | Pregunta 3; filas «pedido» en la matriz |
| A17 | H | `hoja.md` §12 | «60/30/10 a ojo» | `gimg/measure.py` solo mide la cuota de paleta: `DELTA_E = 15.0` (l.25), distancia euclídea en Lab (l.83-84), `palette_share` (l.170). No hay medida por familia | Reglas con fórmula en §16; la medida por familia es hueco de gimg |

## Huecos de gimg (no se implementan aquí)

1. Sin perfil `lateral` 704×1344 (I1).
2. Sin salida BMP de 24 bits sin alfa (I1, I2), ni WebP (I3, I4), ni ICO con varios tamaños (I5/E14).
3. Sin recorte ni reducción declarados: 704×1344 → 164×314 y 328×628; 1536×512 → 1536×384; 896×1152 → 768×1152 → 600×900;
   1024×576 → 1024×478 → 920×430.
4. Sin perfiles para LinkedIn 1584×396, Discord 960×540 y tarjeta 16:9 1600×900.
5. `gimg measure` no reparte los píxeles por familia (madera, hierro, oro, cristal): la regla 60/30/10 no se puede
   comprobar con un comando.
6. Sin comprobación de luminancia media (I4 pide < 40 de 255) ni de contraste WCAG entre un texto y su fondo.
7. `piezas.py` no centra el lockup en un tercio dado de la imagen (I1: tercio superior).

## Decisiones de la persona (2026-11-12)

Eran siete preguntas; la persona las respondió el mismo día y están aplicadas en `hoja.md` §16 y §17.

1. **Tolerancia de color:** ΔE76 ≤ 15 en imagen generada; hex exacto en CSS y SVG.
2. **60/30/10:** el «30» queda sin cota hasta que gimg mida por familia.
3. **Steam Deck:** sí a la cápsula vertical I6 y al icono 256²; lo demás son recortes de E4 y E5.
4. **UX-40:** se pide al juego que la fusione en `main` antes de recibir imágenes.
5. **`castle`:** vetada.
6. **Mapa de Helek:** pintado, con el acabado de las ilustraciones del juego.
7. **Reddit:** usa E1 (avatar) y E2 (cabecera).

## Segunda pasada (2026-11-12)

| # | Dónde | Qué había | Arreglo |
|---|---|---|---|
| B1 | `peticiones.md` #6, #16, E1, E2, E3, E4, E9 | `stars`, `castle`, `glowing`, emblema pedido al modelo, img2img del #1, negación en E9 | Reescritos en su sitio |
| B2 | `peticiones.md` E2 y E3 | E2 dejaba libres los dos tercios derechos y ponía el logo en el izquierdo; E3 decía logo a la izquierda y lema a la derecha | La zona libre es la del logo (hoja §9): tercio izquierdo en E2, centro en E3 |
| B3 | `peticiones.md` §2 | Negativo, módulos de estrella y luz de la Semilla, «gimg no hace transparencia», costura a mano, `steps` 6, FLUX | Reescrito en su sitio |
| B4 | `biblia.md` §7-§10; `hoja.md` §0 y §13; `peticiones.md` §0 | Commits y líneas del 2026-11-04 y del 2026-11-10 | Reescritos con lo comprobado el 2026-11-12; lo no recomprobado (lore, producto) lo dice |
| B5 | `pedido-mapa.md` §2 | Negativo; costura a mano; perfiles `textura` e `icono` (son `texturamapa` e `iconomapa` 768²); modelo klein | Corregido en la copia; pedido al original |
| B6 | `pedido-mapa.md` #39 y #43 (`star`), #40 (`for a title`) | Palabras vetadas; zona descrita por lo que irá encima | Reescritos |
| B7 | `pedido-mapa.md` §1 y bloque de terreno | «Matte painterly brushwork, fine detail» dio iconos en vector plano (q373) | Bloque con el acabado de `estilos.mapa` de `mundo.json`; la prueba se repite |
| B8 | `examples/tarkor/orders/` (`mapa/*`, `ui/e09-sello.json`, `marca/e02-cabecera.json`, `e03-og.json`, `e04-capsula.json`) | Llevan los prompts anteriores | Fuera de las rutas de este encargo: pendiente |
| B9 | Juego `c858a150`, `Home.tsx` l.45 | Emoji ⚔️ que ningún pedido cubre | Fila en hoja §17; entrega al juego |
| B10 | Juego `c858a150`, tiradas | El 🎲 está también en `CombatExchangeBadge.tsx`, `RollBadge.tsx`, `ExtendedRollBadge.tsx` y `GatheringDiceReveal.tsx`; el #14 solo nombra `DiceRoll.tsx` | Fila en hoja §17; entrega al juego |
| B11 | Juego `c858a150` | `.corner-bracket-gold` (l.372) no lo usa ningún componente; `.title-gold` solo `Home.tsx` l.30 | Entrega al juego |
| B12 | WMF-imagenes, `estilo/mundo.json` | La noche del juego nombra `stars` y la región de las Llanuras usa «long violet shadows»; la marca veta las dos | Reglas distintas para dos cosas distintas (ilustración del mundo y pieza de marca); `violet`, a revisar allí: entrega a WMF-imagenes |
