# Entrega de la hoja de estilo a toVeriAI (2026-11-12)

Para la sesión de `VeriNews_AI` (la marca es **toVeriAI**). Desde aquí no se toca ese repo: esta nota dice qué leer
de galivelop-image-generator, qué cambiar allí y qué piezas puede generarle `gimg`. Todo lo citado de su repo es de
`main` `1f98db6` (leído el 2026-11-12, sin modificar nada). Nada de lo que se ofrece está generado todavía: lo de
«Piezas» es **PROPUESTA** hasta que su dueña o dueño diga sí.

**Lo que no cambia:** la identidad es la suya y la hoja la respeta: papel cálido `#F7F5F2`, Cormorant Garamond + DM
Sans auto-alojadas, verde bosque `#2D6A4F` como único acento, semáforo del IMI granate / ámbar / verde, wordmark
«toVeriAI» con `Veri` en verde.

## Qué leer de aquí

En galivelop-image-generator (rama de trabajo hasta que llegue a `main`):

1. `docs/marcas/toveriai/hoja.md`: la hoja de estilo, campo a campo, con la fuente de cada valor en su repo (sección
   13). **Sección 16**: las trece ampliaciones propuestas (A1-A13), la tabla de contrastes WCAG de sus tokens y los
   tamaños mínimos y zona libre. **Contradicciones**: las catorce incoherencias del repo y del kit, con qué fuente
   manda (el código que ve el usuario, luego el kit).
2. `docs/marcas/toveriai/biblia.md`: la lectura larga (tono, motivos, qué no hacer en imagen).
3. `docs/marcas/toveriai/logos/`: los SVG `a`-`d` y sus lockups. **No son definitivos:** se dibujaron antes de la
   regla de que todo nace del generador y el símbolo sigue sin aprobar (hoja §4); A1 los sustituye por uno sacado de
   su propio `favicon.png`.

## Qué cambiar en su repo

Sin decisión pendiente (alinea el repo con su propio kit y su `App.css`):

| # | Archivo (línea) | Hoy | Cambio | Por qué |
|---|---|---|---|---|
| 1 | `frontend/src/components/share/ShareCard.css` (l.10, l.15, l.20, l.30, l.31, l.34, l.36, l.49, l.63, l.64, l.71, l.74, l.78, l.81, l.83-85) | hex a mano | `var(--color-text)` `#1A1A1A`, `var(--color-green)` `#2D6A4F`, `var(--color-green-pale)` `#B7E4C7`, `var(--color-amber)` `#B5832A`, `var(--color-green-lt)` `#74C69D`, `var(--color-green-mid)` `#52B788`, `var(--color-green-bg)` `#E8F4EE`, `var(--color-red)` `#9B2335` (tokens de `App.css` l.114-139) | un cambio de paleta hoy no llega a la tarjeta (hoja, Contradicciones 8) |
| 2 | `frontend/src/components/share/ShareSeal.css` (l.33, l.37) | `#74C69D`, `#1A1A1A` | `var(--color-green-lt)`, `var(--color-text)` | ídem |
| 3 | `frontend/src/utils/shareImage.js` (l.5-7) | repite `#2D6A4F`/`#E8F4EE`, `#B5832A`/`#FBF6ED`, `#9B2335`/`#FBF0F2` | importar `C_GREEN`, `C_AMBER`, `C_RED` de `utils/imiColors.js` (l.1-3) | una sola fuente para el semáforo |
| 4 | `frontend/index.html` (l.33) | `twitter:card` `summary` | `summary_large_image`, cuando exista la `og:image` de la fila «Piezas» P4 | la tarjeta grande es la que se ve en X y LinkedIn (hoja, Contradicciones 11) |
| 5 | `frontend/index.html` (l.29, l.36) | `og:image` y `twitter:image` = `favicon.png` 512×512 | la imagen 1200×630 de P4 | ídem |
| 6 | `frontend/src/assets/logo.png`, `logo-vertical.png` | dicen «VeriNews» y ningún archivo los importa | borrarlos, o sustituirlos por los lockups de P3 | nombre viejo (hoja, Contradicciones 1) |
| 7 | `frontend/public/icons.svg` (**opcional**) | sprite huérfano con relleno `#08060d`: ningún archivo de `frontend/` lo referencia (`git grep icons.svg` en `1f98db6`, sin resultados) | borrarlo, o dejarlo hasta que exista la serie propia P7 | no es de la marca ni se usa; no estorba, por eso es opcional |
| 8 | `README.md` (l.3, l.26, l.116) | «siete dimensiones», «ES, GL, CA, EU» | «7 o 9 según el tipo de entrada»; los cinco idiomas del código (con `en`) | desfasado frente a `index.html` (hoja, Contradicciones 10) |
| 9 | `Documentacion/v1.1/marketing.html` (l.278-285); `AdminPage.jsx` (l.12-13), `AdminDatasetPage.jsx` (l.100-101), `AdminIncidenciasPage.jsx` (l.29) | rangos 0-49 / 50-74 / 75-100 y `#e74c3c`, `#c9761f`, `#27ae60`, `#C0392B` | rangos 0-39 / 40-69 / 70-100 y los tres colores de `imiColors.js` | lo que ve el usuario manda (hoja, Contradicciones 2) |
| 10 | `Documentacion/v1.1/kit-visual-ia.html` (l.45, l.352) | hero `#1c3028 → #2D6A4F`; habla de un `favicon.svg` que ya no existe | el degradado real (`#1B4332 0% → #2D6A4F 55% → #40916C 100%`); quitar el `favicon.svg` | el kit dice ser literal del código (l.846) y no lo es (Contradicciones 4 y 5) |

Con decisión de su dueña o dueño (la recomendación entre paréntesis):

| # | Archivo (línea) | Hoy | Opciones |
|---|---|---|---|
| 11 | `ShareCard.css` (l.8) y `shareImage.js` (l.21) | fondo y captura sobre `#FFFFFF`, que el kit l.284 prohíbe | `var(--color-bg)` `#F7F5F2` o `var(--color-bg-card)` `#FDFCFB` (**recomendado `#FDFCFB`**: la tarjeta es una tarjeta, y sigue siendo claro al compartirla) |
| 12 | `ShareCard.css` (l.50) y `ShareSeal.css` (l.26) | `#6B7F76`, sin token | token nuevo en `App.css` (p. ej. `--color-muted-green`) o `var(--color-muted)` `#777777` (**recomendado el token nuevo**: el gris verdoso es deliberado y `#777777` solo vale para texto grande, hoja §16) |
| 13 | `ShareCard.css` (l.52) | `font-weight: 700`; `fonts.css` solo sirve 300, 400 y 500 | 500 (**recomendado**: el kit l.310 dice «nunca bold» y el 700 lo sintetiza el navegador) |
| 14 | `Footer.css` (l.27) | `Veri` en `#2D6A4F` sobre `#1A1A1A`: 2,72:1, no pasa WCAG ni como texto grande | `var(--color-green-mid)` `#52B788` (7,03:1), el verde del kit para fondo oscuro (**recomendado**) |
| 15 | `Footer.css` (l.24) | wordmark a 300 | 400 como el `Navbar` y el kit l.335 (**recomendado**, menor) |
| 16 | `frontend/index.html` (l.5) | solo `<link rel="icon" … /favicon.png>` | añadir `apple-touch-icon` 180, `manifest` con 192 y 512, favicon 32 y `<meta name="theme-color" content="#F7F5F2">` cuando existan las piezas P6 (**recomendado**) |

## Qué piezas podemos generarle

Todas con `gimg` en local (ninguna dibujada a mano), con la configuración de `examples/toveriai/galivelop-images.json`
de este repo. Detalle de cada una en la hoja, §16.

| # | Pieza | Cómo sale en `gimg` | Perfil | Va a |
|---|---|---|---|---|
| P1 | Símbolo en SVG (A1) | `gimg brand trace frontend/public/favicon.png --mode color --palette "#2D6A4F,#B5832A"` (o `--colors 2`, fiel al salvia y dorado del PNG) | — | `frontend/public/` y `src/assets/` |
| P2 | Símbolo mono y silueta (A2) | `gimg brand trace … --mode mono` / `--mode silhouette`, en `#1A1A1A` sobre claro y `#FFFFFF` sobre oscuro | — | favicon de 16-32 px, sello |
| P3 | Wordmark y lockups horizontal y vertical (A3, A4) | `gimg brand system` sobre el favicon con `--name toVeriAI --text toVeriAI --font "CormorantGaramond[wght].ttf" --weight 400 --spacing 0.08`; lockup oscuro con `gimg brand lockup … --color "#FFFFFF"`. **Límite:** el nombre sale de un solo color; el «Veri» en verde aún no | — | sustituye a `logo.png` y `logo-vertical.png` |
| P4 | `og:image` 1200×630 (A5) | pedido con la plantilla `plantillas/og.svg` y el lema de la hoja §10; compuesto en r4-r7, falta el veredicto de r8 | `og` | `frontend/public/og.png` (cambios 4 y 5) |
| P5 | Tarjetas para redes (A6) | un pedido por red, textos literales de su kit (hoja §10) | `square`, `portrait`, `wide`, `header` | sus cuatro cuentas (`Footer.jsx` l.57-62) |
| P6 | Iconos de aplicación 32/180/192/512 (A7) | desde P1 y P2; `gimg` no tiene aún perfil `icon` (hoja §15) | — | cambio 16 |
| P7 | Serie de iconos de la interfaz (A9) | pedido sobre croma, `gimg brand matte` y `gimg brand trace --mode mono`; trazo ~1,3 px, un color (kit l.397) | `square` | en lugar de los SVG en línea de cada componente |
| P8 | Ilustraciones de cabecera, estados vacíos y 404 (A10) | los motivos de la hoja §6, borrador FLUX y pieza Z-Image | `header`, `og`, `wide`, `square` | `ComoFuncionaPage` y las otras tres cabeceras con degradado |
| P9 | Hoja de contactos para decidir P1-P3 (A13) | `gimg sheet` a 16, 32, 64 y 512 px sobre `#F7F5F2` y `#1A1A1A` | — | para la decisión, no para la web |

Comprobación después, también desde aquí: `gimg measure <captura.png> --palette … --zone X,Y,W,H --text "#1A1A1A"` sobre
una captura de la tarjeta compartible o de cualquier pieza da la paleta y el contraste reales (hoja §16, A8 y A12).

## Qué decide su dueña o dueño

1. **Colores del símbolo en SVG:** los del kit (`#2D6A4F`, `#B5832A`) o los del PNG (salvia y dorado). Recomendado: los
   del kit, que están en la paleta (hoja, Contradicciones 3).
2. **Si el SVG nuevo sustituye a los `a`-`d` de aquí** y a los PNG «VeriNews». Recomendado: sí, viendo P9.
3. **Lockups de un color ya, o esperar** a que `gimg` dé el nombre a dos tintas. Recomendado: mono ya para el pie y las
   piezas pequeñas; el de dos tintas sigue siendo el texto HTML de la web.
4. Las opciones de los cambios 11 a 16.
5. **Qué redes y qué frases** para P5, y si quiere serie de iconos propia (P7) y de qué conceptos.
6. **Si la web lleva ilustración** (P8) o se queda tipográfica. Recomendado: probar una ronda de cabeceras antes de
   decidir.
7. **Tema oscuro:** recomendado **no** en la web (la marca es papel claro); solo piezas oscuras compuestas, con los pares
   de contraste de la hoja §16.
8. Los tamaños mínimos y la zona libre de la hoja §16 (wordmark ≥ 18 px de alto; símbolo en color hasta 32 px y mono por
   debajo; zona libre la altura de la «V»).
