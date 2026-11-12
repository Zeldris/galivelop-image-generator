# Entrega: hoja r10 de Galivelop IG (2026-11-12)

Qué hay que cambiar en **este repo** para que la interfaz, los logos, las pruebas y los documentos cumplan
[`docs/marcas/galivelop-image-generator/hoja.md`](../../marcas/galivelop-image-generator/hoja.md) (r10), y qué piezas
hay que generar. **Nada de esto está hecho:** esta tarea solo escribió la hoja, el script del cálculo y esta lista. Es
trabajo para una tarea posterior, con su rama, su revisión y su check.

Código leído en `8bb0ae1` (rama `hojas-repos`). Los hex nuevos salen de
`python3 docs/marcas/galivelop-image-generator/acento_oklch.py '#7C5CD6'` (y `--par A B`, `--sobre FONDO`); los
heredados, de `docs/marcas/portal/hoja.md` l.127-152 y l.236-250. Los números `D…` son los de la tabla «Interfaz:
diferencias con el código de hoy» de la hoja.

## Qué leer antes

1. La hoja r10: «Acento: los dos tonos, calculados», «Interfaz: tokens y reglas» y «Contradicciones» (r10).
2. `docs/marcas/portal/hoja.md` l.228-375 («Familia Galivelop» y «Decisiones de la persona (2026-11-12)»).
3. `tests/test_ui.py` l.563-597 y `tests/test_brand_assets.py` l.12-22, l.54-60, l.95: fijan los valores de r9 y
   **fallarán** con los cambios de abajo; se cambian en el mismo commit que el valor que vigilan.

## Antes de tocar nada: lo que decide la persona

| # | Pregunta | Opciones | Recomendación |
|---|---|---|---|
| Q1 | r9 (aprobada el 2026-11-11) fijó tres violetas, `#5B34C9`, `#A78BFA` y `#8B5CF6`; la decisión del 2026-11-12 da `#7C5CD6` y `#896ae5`. ¿Se sustituyen? | sí / se quedan los de r9 | **Sí.** Es la decisión más reciente y la que hace familia. Se pierde contraste (texto 7,36 → 4,69; botón 7,56 → 4,82) pero sigue en AA |
| Q2 | El método solo garantiza 4,5:1 sobre el papel. Dentro de fichas el texto de acento da 4,43 (`#f1f6f9`), 4,20 (`#111f29`), 3,96 (`#16242e`), 4,03 / 3,82 (tinte) | A: método estricto y texto de acento solo sobre papel o `#ffffff` (hay que quitar enlaces de fichas oscuras y dos pares de `tests/test_ui.py` l.564). B: un tono de texto calculado contra la peor superficie: `#7453cc` claro (papel 5,31; `#ffffff` 5,45; `#f1f6f9` 5,01; tinte 4,56), `#9577f3` oscuro (`#0d171e` 5,36; `#111f29` 4,96; `#16242e` 4,68; tinte 4,51) | **B**, solo para `--accent-text`; `#7C5CD6` sigue en rellenos, foco y logo. Añade un paso al método de la familia, así que vale para los demás productos |
| Q3 | «IG» en violeta en el nombre (r9) frente a nombre en una tinta (lockup común) | una tinta / «IG» en acento | **Una tinta** |
| Q4 | Aviso (`--warn` `#8a5a00` / `#f2c14e`): la familia no tiene color de aviso | conservar el ámbar propio / avisar con tinta e icono | **Conservarlo**: una cola de generación necesita distinguir «en espera» de «fallo» |
| Q5 | Enlace al Portal en oscuro: `#1aa6df` (r9) o `#5cc8f2` (el enlace del Portal) | — | **`#5cc8f2`** (9,49 sobre `#0d171e`) |
| Q6 | Lockup vertical, que r9 y la biblia prohibían | admitirlo / no | **Admitirlo** como secundario |
| Q7 | El cuadrado con chaflán no lo sabe hacer `gimg` (ver G1). ¿Se añade a `gimg brand` o el símbolo va sin cuadrado hasta entonces? | añadir `--tile` / esperar | **Añadirlo**: sin eso ningún producto de la familia puede sacar su logo de gimg |

Las tablas de abajo dan el valor con las recomendaciones; donde Q2 cambia el valor, van los dos.

## 1. `gimg/ui/css/tokens.css`

Cada fila son tres sitios: claro, oscuro por `prefers-color-scheme` y oscuro por `data-theme`.

| # | Token (líneas) | Hoy | Nuevo | Por qué |
|---|---|---|---|---|
| T1 | `--surface` (l.13, l.55, l.81) | `#e6eef3` / `#13212b` | `#ffffff` / `#111f29` | D7, heredado |
| T2 | `--surface-2` (l.14, l.56, l.82) | `#d9e4eb` / `#1b2e3b` | `#f1f6f9` / `#16242e` | D8, heredado |
| T3 | `--rule` (l.18, l.58, l.84) | `#c9d5dd` / `#2b3d4a` | `#b9cbd6` / `#2b3d49` | D11, heredado |
| T4 | `--text-2` (l.20, l.60, l.86) | `#4a5b66` / `#9fb4c4` | `#4a5c69` / `#9fb2bf` | D9; 6,76 / 8,28; sobre `--surface-2` 6,37 / 7,24; sobre el tinte 5,81 / 6,97 |
| T5 | `--text-3` (nuevo) | — | `#5a6d7a` / `#7d919e` | D10; 5,24 / 5,54 |
| T6 | `--accent` (l.21, l.61, l.87) | `#5B34C9` / `#A78BFA` | `#7C5CD6` / `#7C5CD6` | D1, D3: el vivo no cambia con el tema |
| T7 | `--accent-text` (l.22, l.62, l.88) | `#5B34C9` / `#A78BFA` | A: `#7C5CD6` / `#896ae5` · **B: `#7453cc` / `#9577f3`** | D1, D3, Q2 |
| T8 | `--accent-fill` (l.23, l.63, l.89) | `#5B34C9` | `#7C5CD6` | D2; blanco encima 4,82 |
| T9 | `--accent-soft` (l.25, l.65, l.91) | `#e8e0fa` / `#241a4a` | `color-mix(in srgb, var(--accent) 12%, var(--bg))` y `18%`; en hex, `#ece9f8` / `#21233f` | D6. Con `color-mix`, `tests/test_ui.py` no puede leer el hex: mejor el hex con el porcentaje en comentario |
| T10 | `--brand` (l.26, l.66, l.92) | `#8B5CF6` | se quita; sus usos pasan a `--accent` | D4 |
| T11 | `--family` oscuro (l.67, l.93) | `#1aa6df` | `#5cc8f2` | D13, Q5 |
| T12 | `--ok` (l.28, l.68, l.94) | `#1b7a3e` / `#5ad38a` | `#3f5a4b` / `#8fb09e` | D14; 7,37 / 7,66 |
| T13 | `--bad` (l.30, l.70, l.96) | `#b3261e` / `#ff7b6b` | `#a3135f` / `#f27ab0` | D15; 7,26 / 7,07 |
| T14 | `--focus` (l.32, l.72, l.98) | `#5B34C9` / `#A78BFA` | `#7C5CD6` | D5; 4,69 / 3,76; sobre superficie 4,82 / 3,48; sobre `--surface-2` 4,43 / 3,29 |
| T15 | `--shadow` (l.33, l.73, l.99) | dos capas difusas | `0 12px 32px -18px rgb(19 33 43 / .35)`; oscuro `rgb(0 0 0 / .7)` | D16 |
| T16 | `--overlay` (l.34, l.74, l.100) | `rgb(13 23 30 / .72)` / `.78` | `rgb(6 18 28 / .68)` (62 % para lo ligero, 78 % para diálogos) | D17 |
| T17 | `--r`, `--r-s` (l.40-41) | 12 px, 8 px | se quitan; entran `--chamfer-l: 28px`, `--chamfer: 14px`, `--chamfer-s: 10px` | D18 |
| T18 | `--grid`, `--grid-step` (nuevos) | — | `#e3edf3` / `#16242e`, `24px` | D12 |
| — | `--bg`, `--text`, `--border`, `--warn`, `--on-accent`, `--on-status`, `--tap`, `--focus-w`, fuentes | — | **no cambian** | propios o ya heredados |

## 2. `gimg/ui/css/base.css`, `layout.css`, `components.css`

| # | Archivo (línea) | Hoy | Cambio | Por qué |
|---|---|---|---|---|
| C1 | `base.css` l.10 | `font: 16px/1.45` | `17px/1.6` | D22 |
| C2 | `base.css` l.13 | h1-h3: `letter-spacing: 0; line-height: 1.2` | `font-weight: 800; text-transform: uppercase; letter-spacing: .01em; line-height: 1.02` | D21 |
| C3 | `base.css` l.14-16 | peso 700 en 30 / 23 / 18 px | los tamaños se quedan; el peso lo da C2 (h4, si lo hay, 700) | D21 |
| C4 | `base.css` l.32-35 | foco: `outline` + `box-shadow` + radio | `outline: var(--focus-w) solid var(--focus); outline-offset: 2px`, sin sombra ni radio | regla 2 y 3 |
| C5 | `base.css` l.44-52 (`.btn`) | `border-radius: var(--r-s)`, `font: 500 15px/1.2 var(--font-body)` | radio 0; `font: 500 12px/1.4 var(--font-mono); text-transform: uppercase; letter-spacing: .06em`; el alto sigue en `--tap` | D18, D23 |
| C6 | `base.css` l.76 (rótulos de campo) | Literata 500, 13 px | JetBrains Mono 500, 12 px, mayúsculas, tracking 0,06 em | D23 |
| C7 | `base.css` l.95 (chips) | `border-radius: 999px` | 0 | D18 |
| C8 | `base.css` l.106 | `border-radius: 4px` | 0 | D18 |
| C9 | `base.css` l.112 (`.card`) | `border-radius: var(--r)` | 0 y chaflán: `clip-path: polygon(0 0, calc(100% - var(--chamfer)) 0, 100% var(--chamfer), 100% 100%, 0 100%)`. El `clip-path` recorta el borde de 1 px en la diagonal: comprobar a ojo en el navegador (`tests/test_ui_browser.py`) | D18 |
| C10 | `base.css` l.125-128 (barra de progreso) | `border-radius: 999px`; relleno `--accent` sobre `--rule` | radio 0; la barra lleva contorno de 1 px `--border` (3,57 / 4,07 sobre `--surface-2`), porque `#7C5CD6` sobre el filete da 2,89 / 2,34 | D18; par `("accent", "rule")` de las pruebas |
| C11 | `base.css` l.132 (diálogo) | radio y sombra de dos capas | radio 0, chaflán grande, `--shadow` nueva | D16, D18 |
| C12 | `base.css` l.137 (`.spin`) | redondo | **se queda** | excepción propia a la regla 3 |
| C13 | `layout.css` l.9, l.11 | título 700; `.brand .sigla` en `--accent-text` | 800 y mayúsculas; se quita el color de `.sigla` | D24, Q3 |
| C14 | `layout.css` l.17, l.40-41, l.69-70 | radios (`--r-s`, `4px`) | 0 | D18 |
| C15 | `layout.css` l.21, l.25 | puntos de estado al 50 % | **se quedan** | única excepción heredada |
| C16 | `layout.css` l.33 | `box-shadow: var(--shadow)` | se queda solo si el panel flota; si no, filete de 1 px | regla 4 |
| C17 | `components.css` l.7, l.67 | `box-shadow` propias | fuera, o `--shadow` si flota | D16 |
| C18 | `components.css` l.23 | `backdrop-filter: blur(4px)`, `#eaf4fa` | sin `backdrop-filter`; fondo `--overlay`; texto `#ffffff` por token | D19, D20 |
| C19 | `components.css` l.26 | `#ffffff` | `var(--on-accent)` | D20 |
| C20 | `components.css` l.16, l.57, l.73, l.85, l.98, l.114, l.137, l.144, l.160, l.166 | radios | 0 (chaflán pequeño en miniaturas, si se quiere marca) | D18 |
| C21 | `components.css` l.66, l.92, l.154 | muestras, tirador y número de paso al 50 % | cuadrados | D18 |
| C22 | fondo de página | liso | retícula: dos `linear-gradient` de 1 px cada `--grid-step` en `--grid`. **Ojo:** la regla 2 prohíbe `-gradient(`; el Portal la dibuja igual y lo exceptúa (`docs/marcas/portal/hoja.md` l.160-178): copiar su excepción en la prueba que lo vigile | D12 |

## 3. Logos e `index.html`

| # | Archivo (línea) | Hoy | Cambio | Por qué |
|---|---|---|---|---|
| L1 | `gimg/ui/assets/gvig.svg` l.4; `docs/marcas/galivelop-image-generator/logos/galivelop-image-generator-b.svg` | `<rect rx="28" fill="#5B34C9">`, a mano | sustituir por el símbolo de la pieza P1 (`#7C5CD6`, chaflán arriba a la derecha) | D25 |
| L2 | `logos/…-b-linea.svg`, `…-b-linea-oscuro.svg` | celda en `#8B5CF6` | `emblema-mono.svg` de P1, en `currentColor` | hoja §4 |
| L3 | `gimg/ui/assets/gvig-lockup.svg` l.12; `logos/…-b-lockup.svg`, `…-b-lockup-oscuro.svg` | `<text>` 700 con «IG» en `#5B34C9` / `#A78BFA` | `lockup-h.svg` de P2 (trazados, `currentColor`); el oscuro deja de ser un archivo aparte | D26 |
| L4 | `logos/` | — | añadir `wordmark.svg`, `lockup-v.svg` | hoja §4 |
| L5 | `gimg/ui/index.html` l.8, l.19 | favicon y logo de 28 px en la cabecera | mismos archivos; a 28 px va el símbolo solo y el nombre como texto de la cabecera (lockup mínimo: `S` ≥ 32 px) | hoja §4 |
| L6 | `examples/galivelop-image-generator/logos/galivelop-image-generator-b-lockup.svg` | copia congelada del lockup anterior a r9 | `lockup-h.svg`, **al medir la ronda plana (P4)**, no antes | `docs/handoff.md` l.18 |

## 4. Pruebas que cambian con lo anterior

| # | Prueba (línea) | Hoy fija | Cambio |
|---|---|---|---|
| X1 | `tests/test_ui.py` l.564 (`TEXT_PAIRS`) | `accent-text` sobre `bg`, `surface`, `surface-2` ≥ 4,5 | con B pasa tal cual (peor caso 4,68); con A hay que quitar `surface` y `surface-2` y vigilar por otra vía que no haya texto de acento ahí |
| X2 | `tests/test_ui.py` l.569 (`NONTEXT_PAIRS`) | `("accent", "rule")` ≥ 3 | daría 2,89 / 2,34: cambiar por el contorno de C10 |
| X3 | `tests/test_ui.py` l.585, l.587 | `accent-fill == #5b34c9`; blanco ≥ 7,5 | `#7c5cd6`; blanco ≥ 4,5 (da 4,82) |
| X4 | `tests/test_ui.py` l.592-594 | existe `--brand` y vale `#8b5cf6` | quitar `brand`; añadir `text-3`, `grid` |
| X5 | `tests/test_ui.py` l.597 | `family` oscuro `#1aa6df` | `#5cc8f2` |
| X6 | `tests/test_brand_assets.py` l.12-22 | tintas y «IG» de símbolos y lockups | `#7C5CD6`; sin «IG» de color; sin `<text>` en el lockup |
| X7 | `tests/test_brand_assets.py` l.54-60 | `fill #5B34C9`, `rx 28` | `#7C5CD6` y un trazado con cinco vértices (sin `rx`) |
| X8 | `tests/test_brand_assets.py` l.95 | el oscuro es el claro con dos hex cambiados | se quita con L3 |
| X9 | `tests/test_examples.py` l.316 | `REDRAWN_COPY_SHA256` | se quita con L6 |
| X10 | nueva | — | **la herencia como comprobación** (`AGENTS.md`: lo comprobable lo hace un script): los tokens heredados de `tokens.css` iguales a una lista; `acento_oklch.py` da `#7c5cd6` / `#896ae5`; ningún `backdrop-filter`, `blur(` ni `border-radius` distinto de 0 fuera de las excepciones |

## 5. Ejemplo, maqueta y documentos

| # | Archivo (línea) | Hoy | Cambio | Cuándo |
|---|---|---|---|---|
| E1 | `examples/galivelop-image-generator/galivelop-images.json` l.6-12 | `brand.palette`: `#06121c`, `#A78BFA`, `#8B5CF6`, `#ffffff`, `#eaf4fa` | `#0072a8`, `#1aa6df`, `#fbfcfd`, `#13212b`, `#7C5CD6`, `#e6eef3`, `#0d171e` | con P4 (r9, contradicción 7) |
| E2 | mismo, l.19-24, l.48-55 | perfiles `og` y `social` con `flux2-klein-4b-q8`, 6 pasos | `zimage-turbo-q6`, 8 pasos, cfg 1.0, euler, `draft {scale 0.5, steps 4}` | con P4 |
| E3 | mismo, l.40-45 | `compose`: logo anterior, Sora e Inter | `lockup-h.svg`; Big Shoulders Display y Literata | con P4 |
| E4 | `examples/galivelop-image-generator/plantillas/og.svg` l.2, l.6 | velo en degradado `#06121c`; filete `#8B5CF6` con `rx="2"` | velo plano; filete `#7C5CD6` sin `rx` | con P4 |
| E5 | `examples/galivelop-image-generator/prompts/` | prompts de vidrio | prompts nuevos con el orden y la frase de paleta de la hoja; los de vidrio se guardan como historia | con P4 |
| E6 | `gimg/ui/mock/api-mock.js` l.11 | `PALETTE` de la identidad anterior | la de E1 | con E1 |
| E7 | `gimg/ui/mock/api-mock.js` l.239 | degradado `#06121c` → violeta en las miniaturas de la maqueta | color plano | con la interfaz |
| E8 | `docs/marcas/README.md` l.39, l.173 | acento de imágenes `#8B5CF6` | `#7C5CD6` (Portal `6574c4f`) | ya |
| E9 | `docs/plan.md` l.765 | `#8B5CF6` | `#7C5CD6`, o nota de que la hoja manda | ya |
| E10 | `docs/marcas/galivelop-image-generator/biblia.md` | identidad anterior a r9 | reescribirla sobre r10 cuando se aplique; hoy solo lleva la nota de cabecera | tras aplicar |
| E11 | `README.md`, `README.en.md`, `docs/en/` | capturas y logo de r9 | capturas nuevas al aplicar (memoria del proyecto: cada versión revisa README y docs) | tras aplicar |

**Fuera de este repo** (se anota, no se toca): la ficha de proyecto del Portal aún dice `#8B5CF6`
(`src/data/proyectos/galivelop-image-generator.json` l.7, según `docs/marcas/portal/hoja.md` l.574), mientras su ficha de
producto dice `#7C5CD6`.

## 6. Lo que le falta a `gimg`

| # | Qué | Dónde | Por qué |
|---|---|---|---|
| G1 | No hay orden que ponga el dibujo trazado sobre el cuadrado con chaflán de 28/128 | `gimg brand` (`gimg/cli.py` l.104-144) solo tiene `matte`, `trace`, `wordmark`, `lockup`, `system` | sin eso el símbolo con cuadrado se monta a mano, que es lo prohibido (Q7). Propuesta: `gimg brand tile emblema.svg --fill '#7C5CD6' --ink '#fbfcfd' --chamfer 0.21875` |
| G2 | `gimg brand system` no acepta `--margin` | `gimg/cli.py` l.134-144 | el lockup común pide margen 0,25 `S`; hoy hay que llamar a `lockup` aparte |
| G3 | `--spacing` vale 0,12 por defecto en `wordmark` y `system` | `gimg/cli.py` l.123, l.139 | la familia usa 0,01: quien olvide la opción saca un nombre que no es el de la familia. Propuesta: leerlo de `brand` en `galivelop-images.json` |

## 7. Piezas que hay que generar

Todo con `gimg` en local; nada dibujado a mano. Desde VS Code, con `GIMG_CONFIG_HOME` y `GIMG_DATA_HOME` fijados
(memoria del proyecto).

| # | Pieza | Cómo | Depende de |
|---|---|---|---|
| P1 | **Símbolo**: rejilla 2×2 con una celda encendida | boceto en línea simple sobre croma `#00ff00` con `zimage-turbo-q6`, perfil `cuadrado` 1024²; sin «exactly N» (el 2×2 se fija al elegir la candidata); `gimg brand matte` y `gimg brand trace --mode color --matte --dp-tol 0.5 --palette '#13212b,#fbfcfd'`; cuadrado con G1. Si no sale en 2-3 intentos, se apunta en troubleshooting y se rediseña (memoria del proyecto) | G1, Q7 |
| P2 | **Wordmark y lockups** | las tres órdenes de la hoja §4 («GALIVELOP IG», 800, `--spacing 0.01`; `h` con `--cap 0.45 --gap 0.25 --margin 0.25`; `v` con `--width 1.6`) | P1, Q3, Q6 |
| P3 | **Favicon y monograma «GVIG»** | el símbolo de P1; `gimg brand wordmark "GVIG"` con las mismas opciones | P1 |
| P4 | **Ronda plana medida** (lo pendiente de `docs/handoff.md` l.18) | grabado a dos tintas, el motivo propio, frase de paleta con «a touch of violet #7C5CD6»; `count` 2-4, `seed` fijo; `gimg measure` con la paleta de E1. Mide dos cosas: si «violet» da `#7C5CD6` y qué proporción ocupa. Con el resultado se fijan E1-E5 y los umbrales de la hoja §12 | P2 |
| P5 | **`og` 1200×630 y `social` 1280×640** con el lockup nuevo | sobre la ronda de P4, `compose` con `lockup-h.svg`; zona limpia de papel a la izquierda; entonces L6 y X9 | P2, P4 |
| P6 | **`avatar` 512** | el símbolo de P1 | P1 |
| P7 | **`og.jpg` del producto en el Portal** (recurso 24 de su hoja, l.213) | misma ronda que P5; se entrega como `tools/og/fuentes/<slug>/og-fuente.png` por la vía de entregas del Portal, no escribiendo en su repo | P4 |
| P8 | **Iconos de la interfaz**, si se decide que los lleve | serie entera de línea simple, una tinta, legibles a 24 px; no se mezcla con otra serie | Q de producto, no de marca |
| P9 | **Versión oscura de los grabados** | segunda generación con la misma semilla y las tintas cambiadas | P4 |

## Orden propuesto

1. Q1-Q7 con la persona.
2. G1 (y G2, G3) en `gimg brand`, con sus pruebas.
3. P1-P3 y, con ellas, L1-L5 y X6-X8.
4. Tokens y CSS (T1-T18, C1-C22) con X1-X5 y X10; prueba en navegador real (`tests/test_ui_browser.py`).
5. P4, y solo con su medida, E1-E7, P5-P7, L6 y X9.
6. E8-E11 y la bitácora.
