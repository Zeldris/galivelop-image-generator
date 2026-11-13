# Hoja de estilo mínima: toVeriAI

**Aprobada el 2026-11-04** (decisiones delegadas por la persona; ver [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md)); tercer caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md)
(F2.12), rellenada tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y
[`../galivelop-workflow/hoja.md`](../galivelop-workflow/hoja.md) (aprobada el 2026-11-04) y con su misma forma. Complementa a
[`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita, campo a campo y en el orden de la
plantilla. Estados como en [`../README.md`](../README.md): sin marca sale de un repo (ruta en la sección 13); **[P]** es
propuesta del agente aprobada por delegación (no es un valor que salga de un repo), con su porqué en la misma celda; *(suposición)* se comprueba en una ronda; «no hay» solo
donde la plantilla lo admite.

Commits de referencia: `VeriNews_AI` `1f98db6` (`main`, leído el 2026-11-12; la hoja citaba `5a7401f` y la biblia, antes,
`02ac654`). **Comprobación del 2026-11-12 (`5a7401f..1f98db6`, `git diff --stat`):** no cambia ningún CSS, ni `fonts.css`, ni
`index.html`, ni `frontend/public/`, ni `Documentacion/`: paleta, tipografía, wordmark, favicon, kit y tarjeta compartible
siguen como dice esta hoja. Lo que sí cambia y la toca: `frontend/src/components/Navbar.jsx` pasa los rótulos de
administración a `t('nav.admin.…')` (l.139 en adelante; el wordmark sigue en l.98-105, tres `span` en l.101-103); los JSON de
`i18n/` crecen y los rangos del IMI de `es_ES.json` suben una línea (l.529-531; `home.title` sigue en l.33); `GLOSSARY.md` l.1
pasa a `galivelop-workflow v0.5.0`; `README.md` solo cambia Java 17 → 21. Ampliaciones propuestas ese día: sección 16. Este repo `5460d2c` (`f2-motor`; la biblia, `74d99f8`; los
logos, `b7f1baf`). El repo de toVeriAI se ha leído **sin modificar nada**. Familia visual `propia`: toVeriAI no es una
herramienta del taller y no hereda nada del Portal.

**Lo primero que hay que saber:** toVeriAI es la única de las seis marcas con **producto visual real y documentado**: una web
pública (`https://www.toveriai.com`), un CSS con los tokens de color (`frontend/src/App.css`), fuentes auto-alojadas
(`frontend/src/fonts.css`, woff2 en `frontend/public/fonts/`), cuatro cuentas en redes enlazadas desde el pie, un kit visual
para IA generativa escrito a mano (`Documentacion/v1.1/kit-visual-ia.html`, 20 prompts) y **otro sistema dentro de la propia
app que ya hace piezas de marca** (`frontend/src/utils/shareImage.js`: tarjeta 1080×1350 y sello 480×480, HTML → PNG). Casi
todo lo obligatorio sale literal del repo; lo que falta es el símbolo en SVG (el repo solo tiene PNG) y los destinos declarados
en la configuración.

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «toVeriAI»: `to` en minúscula, `Veri` y `AI` con mayúscula inicial, de una pieza y sin puntos medios. Así va en el `<title>`, en el `ld+json` (`Organization.name`), en el wordmark del `Navbar` y del pie (`to` + `Veri` + `AI` en tres `span`, con `translate="no"`) y en la tarjeta compartible. «VeriNews» / «VeriNews AI» es el nombre del repo y del proyecto de ciclo (`README.md`), no el de la marca (ver «Contradicciones», 1) | VeriNews_AI (`frontend/index.html` `<title>`; `frontend/src/components/Navbar.jsx` l.98-104; `Footer.jsx` l.86; `components/share/ShareCard.jsx`; `Documentacion/v1.1/kit-visual-ia.html` l.335) |
| Nombre en código | Obl. | `toveriai` | repo (`examples/toveriai/galivelop-images.json`, `name`) |
| Fuente de verdad | Rec. | `VeriNews_AI` `main` `1f98db6` (paleta, tipografía, wordmark, favicon, tono, frases, canales, rangos del IMI); este repo `5460d2c` (prompts, piezas, medidas, logos vectorizados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a toveriai, por proyecto); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa, con dos encargos explícitos: el agente vectoriza el símbolo y **la persona lo aprueba** (`docs/plan.md` l.260), y las decisiones de marca delegadas se le proponen al cerrar (wordmark «toVeriAI», rangos IMI del kit en las piezas; `docs/marcas/README.md` l.39-42). Todas las decisiones delegadas quedan aprobadas el 2026-11-04 (`docs/records/decisiones-hojas-2026-11-04.md`) y las de agente llevan **[P]** con la nota «aprobada por delegación»; el dibujo del símbolo sigue pendiente de ver por la persona | repo (`docs/records/contenido/r1-fondos.md` l.52-53; `docs/plan.md` l.258-261; `docs/marcas/README.md` l.14, l.39-42) |
| Fecha de la hoja | Rec. | `2026-11-12` (aprobada el 2026-11-04; comprobada contra `VeriNews_AI` `1f98db6` y ampliada con la sección 16 el 2026-11-12; afinada el 2026-11-11 con lo aprendido al generar con `gimg` en las otras marcas: modelos, lista vetada, zona limpia, croma y tema oscuro; los cambios llevan **[P]** hasta que la persona los vea) | — |
| Familia visual | Rec. | `propia`: papel cálido, serif fina, verde bosque como único acento; nada de la familia Galivelop (fondo oscuro, Sora, baldosa) | repo (`docs/marcas/README.md` l.84: «toVeriAI puede salirse de la familia») |
| Hereda de | Opc. | no hay | — |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | Analiza una noticia (texto pegado, URL o captura) con IA y devuelve el IMI, un índice de credibilidad de 0 a 100 por dimensiones (siete en texto, nueve en URL), con cada dimensión explicada; gratis, en cinco idiomas, para quien quiere medir antes de creer | VeriNews_AI (`frontend/index.html` `<meta name="description">` y `ld+json` `WebApplication`: `inLanguage ["es","ca","gl","eu","en"]`, precio 0 EUR; `GLOSSARY.md` «IMI», «Dimensión»; `README.md` l.1-10) |
| Lema | Rec. | «La verdad no es binaria» (sin punto en la home; con punto en el `og` de r4) | VeriNews_AI (`frontend/src/i18n/es_ES.json` l.33 `home.title`; `Documentacion/v1.1/kit-visual-ia.html` l.457 «frase de marca ya viva en la home») |
| Tono | Rec. | sereno, editorial, nada sensacionalista; «matices, no veredictos absolutos»: toVeriAI no dice «esto es fake news», da un índice interpretativo por dimensiones; pregunta antes que sentencia. No es: alarmista, de «alerta/peligro», tech azul | VeriNews_AI (`kit-visual-ia.html` l.425, l.428) |
| Idiomas | Opc. | `es, ca, gl, eu, en`: la web publica en los cinco (`i18n/{es_ES,ca_ES,gl_ES,eu_ES,en_US}.json`; `Footer.jsx` l.50-54). Las piezas de r4-r5 van solo en `es`; las demás versiones están sin hacer. El `README.md` del repo dice «ES, GL, CA, EU» (cuatro): el código manda | VeriNews_AI (`frontend/index.html` `inLanguage`; `Footer.jsx` l.50-54; `README.md`, i18n) |
| Campo semántico | Opc. | dentro: claridad, matiz, capas de lectura, medir, espectro, credibilidad, dudar bien, índice, dimensión; fuera: alerta, peligro, «fake news», veredicto, sentencia | VeriNews_AI (`kit-visual-ia.html` l.425, l.428); «espectro», «dudar bien», «índice» salen de sus frases (l.461-465) |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | alarmismo; iconografía de «stop» o prohibido; lupas sobre titulares de prensa amarilla; rojo puro de error; etiquetas o sellos «fake news»; escudos con tick, tijeras, flechas rojas, emojis, clickbait; estética tech azul y glassmorphism; fotos de stock. La desinformación se cuenta con «claridad, matiz, capas de lectura», no con «alerta/peligro» | VeriNews_AI (`kit-visual-ia.html` l.425, l.428, l.284); la lista larga, `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.282-283 (leída del kit) y `biblia.md` §7 |
| Personas y rostros | Rec. | nunca personas de stock; en las piezas hechas no aparece nadie (motivo abstracto). Los dos fundadores salen nombrados en el `ld+json` del sitio, no en imagen | VeriNews_AI (`kit-visual-ia.html` «stock photos» en los prohibidos); `biblia.md` §7 |
| Promesas | Rec. | nada de «detecta fake news» ni «dice si es verdad» (el producto da un índice, no un veredicto); nada de cifras de IMI inventadas como si fueran de una noticia real (los ganchos del kit con «34 sobre 100» y «68» son ejemplos de redacción, no datos); no afirmar como hecha la fase que la web declara beta («acceso sujeto a revisión», `marketing.html` l.486); nada de precios: es gratis (`ld+json`, precio 0 EUR) | VeriNews_AI (`kit-visual-ia.html` l.425, l.470-472; `Documentacion/v1.1/marketing.html` l.486; `frontend/index.html`) |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Obl. | clara (por defecto y única hecha): papel `#F7F5F2` (`--color-bg`); superficies `#FDFCFB` (tarjeta) y `#F0EDE8` (alterna). Oscura (tema oscuro): `#1A1A1A` (pie, «hero de contraste»), **solo compuesta sobre fondo plano, sin imagen generada**: el papel de la marca es claro y una acuarela sobre papel oscuro ya no es toVeriAI; texto `#FFFFFF`, filetes y acentos `#52B788` (el verde «sobre fondo oscuro» del kit), lockup oscuro de §4. Sin pieza hecha *(suposición: el contraste está sin medir)* **[P]** | VeriNews_AI (`frontend/src/App.css` l.114-116, l.117; `kit-visual-ia.html` l.273-275); repo (`galivelop-images.json` `brand.palette`; `piezas.json` `velo`) |
| Texto | Obl. | `#1A1A1A` sobre claro («nunca negro puro»); `#FFFFFF` sobre oscuro; secundarios `#777777` (apagado), `#999999` (gris medio) | VeriNews_AI (`App.css` l.117-119, l.159; `kit-visual-ia.html` l.273-275); `#1A1A1A` es el `color_texto` de las cuatro piezas de `piezas.json` y **no está en `brand.palette`** |
| Acento | Obl. | verde bosque `#2D6A4F` (`--color-green`): «Veri» del wordmark, CTAs, enlaces y **único acento en piezas genéricas**; es también el verde del símbolo. El Portal da al proyecto `#2F7A55`; **resuelto: manda `#2D6A4F`** (ver «Contradicciones», 6) | VeriNews_AI (`App.css` l.127; `kit-visual-ia.html` l.284; `frontend/src/utils/imiColors.js` `C_GREEN`) |
| Acentos en imagen, en orden de peso y significado | Rec. | en piezas genéricas, uno solo (`#2D6A4F`). En piezas que hablan del IMI, el semáforo con su significado: verde `#2D6A4F` = credibilidad alta (70-100), ámbar `#B5832A` = moderada (40-69), granate `#9B2335` = baja (0-39; «granate/vino, no un rojo de alarma»). En la imagen generada el orden de peso es el del motivo «entre dos tintas»: granate y verde a los lados, ámbar en la banda central | VeriNews_AI (`kit-visual-ia.html` l.284, l.442-447; `imiColors.js`: ≥70 verde, ≥40 ámbar, resto granate; `i18n/es_ES.json` l.529-531); el orden en imagen, repo (`prompts/estilo.txt`) |
| Resto de la paleta | Rec. | verdes de apoyo `#52B788` (medio, «acentos sobre fondo oscuro»), `#74C69D` (claro), `#B7E4C7` (pálido), `#E8F4EE` (fondo verde); ámbar claro `#E9A94A` y fondo `#FBF6ED`; granate claro `#E07085` y fondo `#FBF0F2`; bordes `#E8E4DF` y `#F0EDE9`, línea decorativa `#D8D4CF`, borde oscuro `#2A2A2A`, placeholder `#C0BCB8`. Los siete colores de métricas (`#D97706`, `#7C3AED`, `#3B82F6`, `#EA580C`, `#0D9488`…) son de la interfaz, no de marca. `brand.palette` lleva **8**: `#F7F5F2`, `#9B2335`, `#2D6A4F`, `#B5832A`, `#1A1A1A`, `#FDFCFB`, `#F0EDE8` y `#FFFFFF` (texto, superficies y blanco de la pieza oscura; añadidos el 2026-11-04) | VeriNews_AI (`App.css` l.114-160; `kit-visual-ia.html` l.248-266); repo (`galivelop-images.json`) |
| Combinaciones | Rec. | clara estándar: `#F7F5F2` + texto `#1A1A1A` + acento `#2D6A4F`; tarjeta: `#FDFCFB` + `#1A1A1A` + `#2D6A4F`; oscura: `#1A1A1A` + `#FFFFFF` + `#2D6A4F` (sin pieza hecha); sobre un score: `#F7F5F2` + `#1A1A1A` + verde/ámbar/granate según el IMI. Sobre imagen (r4-r5): texto `#1A1A1A` con velo `#F7F5F2:0.35` en los cuatro formatos; contraste medido 14,7-15,9:1 | VeriNews_AI (`kit-visual-ia.html` l.271-276); repo (`piezas.json` `velo`, `color_texto`; `r4-composicion.md` l.17; `r5-piezas.md` l.31) |
| Prohibidos | Rec. | negro puro `#000`; blanco puro `#FFF` **como fondo**; azules corporativos; degradados brillantes o neón; más de un acento en **lo compuesto** de una pieza genérica (texto, filete, wordmark: solo `#2D6A4F`); ámbar y granate fuera de piezas que hablan del IMI, salvo en la imagen generada, donde las tres tintas **son** el espectro del IMI (motivo «entre dos tintas», §6) y por eso valen en todas las piezas; rojo de alarma puro. Añadidos en la biblia: rosa y magenta (el vino de r1 tiraba a magenta) | VeriNews_AI (`kit-visual-ia.html` l.284, l.447); rosa/magenta, repo (`r1-fondos.md` l.50, l.60; `biblia.md` §2) |
| Degradados | Opc. | solo en el hero de la web: el kit dice `#1c3028 60 % → #2D6A4F`; el código `linear-gradient(135deg, #1B4332 0%, #2D6A4F 55%, #40916C 100%)` (ver «Contradicciones», 5). En las piezas y el logo, ninguno («toVeriAI no», regla de la familia) | VeriNews_AI (`kit-visual-ia.html` l.45; `frontend/src/pages/ComoFuncionaPage.css` l.10, `DimensionesPage.css` l.10, `EscalaIMIPage.css` l.10, `HistorialPage.css` l.57); repo (`docs/marcas/README.md` l.125) |

**Medido:** la calibración da a este proyecto paleta ≥ 65 % (r1 42-64 %; r2 material 68,7 %, hex 67,2 %, palabras 52,4 %; r4 og
66,95 %; r5 67-77 %) frente al 95 % de la portada del Portal, que es casi blanca y por eso puntúa tan alto
(`docs/records/contenido/calibracion-measure.md` l.35, l.37-38, l.53, l.70). El `favicon.png` da 1 % porque `measure` no
descarta el alfa y lo mide sobre negro (l.36; leve de F2.9, `docs/handoff.md` l.38). r2 enseñó que materiales dan la mejor paleta
y «palabras» deja un hueco blanco en medio (`r2-estilo.md` l.39-41, l.53).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/toveriai/logos/toveriai-a.svg`: el símbolo del favicon vectorizado, simétrico (una mitad en `<g id="toveriai-a-mitad">` y su `<use>` reflejado): dos barras de «V» en verde `#2D6A4F` con las puntas cortadas en diagonal, cuatro hojas curvas en ámbar `#B5832A` que nacen abajo y se abren en abanico, y once puntos encima (4 dorados, 7 verdes). Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; solo colores de la paleta. **El repo de toVeriAI no tiene este SVG:** su símbolo es `frontend/public/favicon.png` 512×512 RGBA (el mismo archivo en `frontend/src/assets/favicon.png`), que la web usa como favicon, en el `Navbar` (36 px), en la tarjeta compartible y como `og:image` | **[P]** (el archivo existe en este repo, `b7f1baf`; la persona lo aprueba según `docs/plan.md` l.260). El **concepto** (fiel al favicon, con los hex del kit en vez de los medidos en el PNG) es decisión delegada, `docs/marcas/README.md` l.14 «elegido **a**». Fuente del dibujo: VeriNews_AI `frontend/public/favicon.png`; descripción del kit l.348, l.362 |
| Lockup (símbolo + nombre) | Rec. | `logos/toveriai-a-lockup.svg` (`viewBox 0 0 520 128`, `data-fondo="claro"`): símbolo a la izquierda, nombre a `x=156` en `<text font-family="'Cormorant Garamond', serif" font-weight="400" font-size="76" letter-spacing="6">` (6/76 ≈ 0,08 em), `to` y `AI` en `#1A1A1A`, `Veri` en `#2D6A4F`. Es el wordmark del `Navbar` llevado a SVG: Cormorant Garamond 400, tracking 0,08 em, `to`/`AI` en `--color-dark`, `Veri` en `--color-green`, favicon de 36 px al lado | repo (archivo, `b7f1baf`); medidas de VeriNews_AI (`Navbar.css` l.16-27; `kit-visual-ia.html` l.325, l.335) |
| Variante clara y oscura | Rec. | clara: `to`/`AI` en `#1A1A1A` (el único archivo que existe). Oscura: `to`/`AI` en `#FFFFFF` y `Veri` siempre en `#2D6A4F`, como el pie de la web (`.vn-footer-logo`, blanco con `span` verde; allí a peso **300**, no 400) | VeriNews_AI (`kit-visual-ia.html` l.335; `Footer.css` l.22-27); el archivo oscuro **no hay** (**[P]** hacerlo si una pieza va sobre `#1A1A1A`) |
| Tamaño mínimo y margen | Rec. | margen libre alrededor del wordmark: al menos la altura de la «V» mayúscula; por debajo de ~18 px de alto el wordmark no se lee (serif fina) y se usa el símbolo; símbolo legible a 16 px (favicon) *(suposición: el SVG `a` a 16 px no se ha mirado con `rsvg-convert -w 32`; el README propone la variante `b`, de dos trazos, para ≤ 32 px)* | VeriNews_AI (`kit-visual-ia.html` l.345, l.348); `b` para ≤ 32 px **[P]** (`docs/marcas/README.md` l.14) |
| Usos prohibidos | Opc. | nunca bold en el wordmark (solo existen los pesos 300/400/500); no inventar otro símbolo (para ilustrar un concepto, el anillo de score); el símbolo va siempre junto al wordmark (lockup) o solo en una esquina libre, nunca suelto en el centro; sin degradados ni 3D en el logo; nunca el wordmark «VeriNews» | VeriNews_AI (`kit-visual-ia.html` l.310, l.368, l.372; `frontend/src/fonts.css`: sin 600/700); «VeriNews» prohibido, decisión delegada **[P]** (`docs/marcas/README.md` l.39-42; ver «Contradicciones», 1) |
| Logo fuera de la paleta | Opc. | el SVG `a` usa `#2D6A4F` y `#B5832A`, los dos en `brand.palette`; el lockup añade `#1A1A1A`, que ya está en `brand.palette` desde el 2026-11-04. El `favicon.png` real usa un verde salvia (~`#6B8176`) y un dorado (~`#AD8E5C`) que no son los hex del kit (ver «Contradicciones», 3) | repo (archivos; `galivelop-images.json`); `biblia.md` incoherencia 3 |

Copia en `examples/toveriai/logos/`: **solo el lockup `a`** (`toveriai-a-lockup.svg`, desde `6abfc9d`), que es el `logo` del `compose` del perfil `og` (`examples/toveriai/galivelop-images.json` l.43); el símbolo suelto y las propuestas `b`-`d` siguen solo en `docs/marcas/toveriai/logos/`, y `piezas.json` (piloto) apunta allí.
En r5 el lockup va al 9 % del alto de la pieza (`r4-composicion.md` l.28-33); en el `avatar` de r5, «sobre fondo oscuro, el
símbolo dorado pierde algo frente al claro de la marca» (`r5-piezas.md` l.56). Los PNG `frontend/src/assets/logo.png`
(2190×1980) y `logo-vertical.png` (2230×750), con el wordmark «VeriNews», **no los referencia ningún archivo del frontend**;
`frontend/public/favicon.svg` (morado) **ya no existe** (borrado en `e8b251c`): la incoherencia 4 de la biblia sobra.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Obl. | Cormorant Garamond **300** (reserva `serif`) en titulares y cifras; 400 en el wordmark; nunca bold. `piezas.json` fija `peso_titulo: 300` (único proyecto que lo declara). **La regla «titular 700 / subtítulo Inter 400» de la familia Galivelop no aplica aquí:** toVeriAI tiene familia propia y el kit dice «nunca bold»; solo vale el principio «lo compuesto y medido manda» (titular 300, subtítulo DM Sans 400 con opacidad 0,82; ver «Contradicciones», 13) | VeriNews_AI (`frontend/src/App.css` l.11 `--font-serif`; `fonts.css` pesos 300/400/500; `kit-visual-ia.html` l.298, l.310); repo (`piezas.json` l.4) |
| Familia de texto | Rec. | DM Sans 400/500 (reserva `sans-serif`) en cuerpo, eyebrows y subtítulos; monoespaciada `Courier New` solo en la interfaz | VeriNews_AI (`App.css` l.10, l.12; `kit-visual-ia.html` l.303); repo (`piezas.json` `fuente_texto`) |
| Licencia y archivo | Rec. | las dos son OFL. En el repo de toVeriAI van **auto-alojadas**: `frontend/src/fonts.css` (`@font-face`, «Generado desde Google Fonts», `font-display: swap`) con seis woff2 en `frontend/public/fonts/` (Cormorant Garamond 300/400/500 y 300/400 cursiva; DM Sans 300/400/500). Para componer aquí, `examples/pilot/fuentes.sh` baja `CormorantGaramond[wght].ttf` y `DMSans[opsz,wght].ttf` de `google/fonts` a `piloto/fuentes/` (fuera de git); no instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)* | VeriNews_AI (`frontend/src/fonts.css` l.1-130; `frontend/public/fonts/`); repo (`examples/pilot/fuentes.sh`) |
| Tracking y mayúsculas | Opc. | wordmark 0,08 em sin mayúsculas sostenidas; eyebrows DM Sans en mayúsculas con tracking 0,28-0,32 em (en el código: `vn-label` 0,24 em, botones 0,14 em, `shc-eyebrow` 0,26 em); titulares sin tracking; cifras del IMI en Cormorant Garamond 500 (tarjeta compartible: 82 px; sello: 92 px) | VeriNews_AI (`kit-visual-ia.html` l.325; `frontend/uno.config.ts` `vn-label`, `vn-btn-base`; `components/share/ShareCard.css` l.29-34, l.48; `ShareSeal.css` l.30) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | 1) **«entre dos tintas»**: dos tintas de acuarela sobre papel de algodón crudo que se encuentran y conservan cada una su color donde se tocan (sangre de buey seca desde un lado, musgo en sombra desde el otro), con una banda central ancha de venas finas en ámbar de resina y tierras: «la banda es la protagonista, rica en matices, entre las dos»; 2) el espectro (la banda graduada del IMI); 3) cita tipográfica sobre papel; 4) doble página de periódico vista cenital; 5) anillo de score. Solo el 1) está generado (r1-r5); los otros cuatro son del kit, sin probar | VeriNews_AI (`kit-visual-ia.html` l.689 «Entre dos tintas», l.547 «El espectro», l.368 anillo; `docs/plan.md` l.617-618); repo (`prompts/estilo.txt`, elegido en r2 con el «sí» de la persona en r1) |
| Motivos No | Obl. | la iconografía de «verificación»: sello «FAKE» o con palabra legible, lupa sobre un titular de prensa amarilla, tijeras, escudos con tick, flechas rojas, señal de stop (en el bodegón de redacción de r8 el sello es solo una huella de tinta borrosa y la lupa un utensilio sobre la mesa, nunca sobre un titular); pantallas azules, neón, 3D, glassmorphism, iconos flat genéricos, personas y rostros (tampoco retratos en los recortes, veredicto r7), negro `#000`, blanco puro de fondo; **letras legibles y cualquier logo, emblema o wordmark pintado** (ningún generado pasa por el logo real: la publicación propia de r8 se sugiere con una banda verde y un filete en la cabecera, no con un símbolo); **marco o banda blanca no pedidos** (el borde de la hoja sobre linón vale solo en el bodegón del `og`; en el resto el papel llena el encuadre); el rosa/magenta en las tintas (r1) y el amarillo en el ámbar | VeriNews_AI (`kit-visual-ia.html` l.284, l.425); repo (`docs/plan.md` l.618-620; `r1-fondos.md` l.50; `biblia.md` §7) |
| Palabras vetadas | Obl. | Lista corta y con porqué, para cumplirla (una lista que nadie sigue no sirve): **lo que el kit prohíbe y ningún motivo necesita** `fake`, `stop`, `scissors`, `shield`, `red arrow`; **lo que pide letras o pasa por el logo** `text`, `letters`, `words`, `headline`, `masthead`, `logo`, `emblem`, `wordmark` (el cierre «textless» no casa con `\btext\b`); **lo que desvía los colores** `pink`, `magenta` (el vino tiraba a magenta, r1) y `\bgold(en)?\b` (visto en otras marcas con Z-Image: «golden» con una sola tinta da amarillo; el ámbar se pide «resin amber #B5832A», el metal «brass»); más `like` como comparación y cualquier lugar real (reglas comunes). **Salen de la lista** `magnifying glass`, `stamp` y `newspaper headline` (2026-11-11): el veredicto de r7 pide lupa, sello y pluma como utensilios del bodegón, así que la lista los prohibía y los prompts los iban a nombrar; lo que sigue vetado es su uso como iconografía de verificación (Motivos No). **Estado de los prompts:** `estilo.txt`, `r2-*.txt`, `r5-*.txt`, `orders/r2-control.json`, `r2-luz.json` y `r6-detalle.json` pasan. `og.txt` y `orders/r1-og.json` llevan «without» (r1, histórico, decisión del 2026-11-04). **`orders/r7.json` no pasa:** «no readable letters, words or numbers anywhere» (negación y `letters`, `words`) y «lies across the amber band like a bandage» (comparación); se corrige en el pedido de r8, no en el histórico | repo (`biblia.md` §7). Origen: `fake`, `stop`, `red arrow`, `shield`, `scissors` traducen los prohibidos del kit (l.425, y «sellos FAKE, tijeras, escudos con tick, flechas rojas», `lectura-2026-10-26…` l.282); `pink`, `magenta`, de r1 (`r1-fondos.md` l.50); `text`, `logo`, `letters`, la regla común de la plantilla; `words`, `headline`, `masthead`, `emblem`, `wordmark`, `gold(en)` y las tres bajas, **[P]** del 2026-11-11 (veredicto r7 en §6 «Estilo de imagen»; lección de gimg en otras marcas) |
| Estilo de imagen | Rec. | **Vigente (r7):** «Style: editorial watercolour and newsprint collage still life on paper, delicate and contemplative, soft muted colours, low saturation, high key. Colours: #F7F5F2, #9B2335, #2D6A4F, #B5832A, #F0EDE8, #1A1A1A in the details. Mood: serene, thoughtful, measured, journalistic.», en prosa larga con los hex (desde r6; «minimal» rechazado en r4: ninguna publicable). Lo impreso del collage se describe **en positivo** como ilegible («columns of tiny type blurred beyond reading», «type sorts with faces worn smooth», «a halftone photograph that dissolves into the wash»): el único cierre es «The image is completely textless.»; el «no readable letters, words or numbers anywhere» de r7 **se retira** (negación: con Z-Image también se cuela y nombra `letters`). Histórico: la línea de r2-r5 era «Style: editorial watercolour on paper, delicate and contemplative, soft muted colours. Materials and light: unbleached cotton paper, dried oxblood ink, shaded moss green ink, warm resin amber, flat daylight. Mood: serene, thoughtful, balanced.» (`estilo.txt`). **r7 (2026-11-04, tras el 7/10 de r6):** el bodegón se vuelve collage de redacción: recortes de periódico rasgados con columnas de tipo borroso, una foto de semitono, tipos móviles gastados, la huella de un sello, cinta de máquina de escribir, sobre las dos tintas y con los instrumentos de medida; se conserva el papel rasgado, que gustó (`orders/r7.json`). **r8 (veredicto de r7, 8/10, 2026-11-05):** el recorte de periódico pasa a ser una publicación propia de toVeriAI (cabecera como banda en `#2D6A4F` con un filete y columnas borrosas; sin símbolo, sin wordmark y sin texto legible inventado) y, en lugar del retrato de una persona, gráficas o un medidor del espectro de veracidad; los utensilios mezclan periodismo antiguo (tipos móviles, lupa, pluma, sello) y moderno (tableta, gráfico impreso, lápiz óptico). Se mantienen el papel rasgado, las tintas y la mitad izquierda despejada. El pedido de r8 va con `zimage-turbo-q6` (8 pasos, cfg 1.0) y sin la comparación «like a bandage» de r7 | repo (`prompts/estilo.txt`, elegido en r2: materiales en vez de hex o palabras, `r2-estilo.md` l.53; `orders/r6-detalle.json`, `orders/r7.json`); veredicto r6 en `../../records/contenido/r4-composicion.md` |
| Lenguaje de forma | Opc. | línea fina ~1,3 px sin relleno (iconos); radios 3 / 4 / 6 px, píldora 999 px solo en badges; sombras cálidas y muy suaves (`0 2px 8px rgba(0,0,0,0.06)` a `0 16px 48px rgba(0,0,0,0.10)`), nunca duras ni negras; mucho aire; acabado de impresión. **Iconos generados con `gimg`** (si alguno no se dibuja a mano): línea simple de un solo color, `#2D6A4F` sobre claro y `#52B788` o `#FFFFFF` en tema oscuro, sin relleno, sombra ni degradado, centrado con un 15 % de margen sobre croma (abajo, «Cómo se pide»); se acepta solo si se lee a 24 px (`rsvg-convert -w 24` o escalado del PNG, mirado) **[P]** | VeriNews_AI (`kit-visual-ia.html` l.281, l.397, l.400-414; `App.css` radios `sm 3px, md 4px, lg 6px, pill 999px` y sombras) |

Prompts del proyecto (`examples/toveriai/prompts/`): `estilo.txt` (= `r2-material.txt`, 160 palabras; elegido en r2 sobre el «sí»
de la persona a `og.txt` en r1), `og.txt` (r1, 138; lleva «without» y «neither red nor green»: superado por `estilo.txt`, se
conserva como historia), `r2-hex.txt` (149) y `r2-palabras.txt` (147) (descartados), `r5-cuadrado.txt` (167), `r5-vertical.txt`
(168), `r5-cabecera.txt` (168) (compuestos y medidos), `r2-luz.txt` (193, sin veredicto). Todos de 138-193 palabras, dentro del
rango 120-320; todos acaban en «The image is completely textless.». Los pedidos de r6 y r7 (`orders/r6-detalle.json`, 310
palabras; `orders/r7.json`, 431) son la dirección vigente y están por encima de los prompts sueltos; r7 pasa de las 320 palabras
que FLUX recorta (con Z-Image el límite no está medido). Los 20 prompts del kit (l.494-806: redes, banners,
iconografía, mockups, miniaturas, abstracto, por plataforma) piden texto dentro de la imagen y se adaptan quitándolo y
describiendo la zona reservada (`biblia.md` §8).

**Cómo se pide con el generador** (lo aprendido con `gimg` en las otras marcas, 2026-11-11; todo **[P]** hasta la primera
ronda de toVeriAI con Z-Image):

- **Modelos.** `flux2-klein-4b-q8` solo para bocetos (`draft`); la pieza de calidad con `zimage-turbo-q6`, 8 pasos, cfg 1.0,
  euler (sus valores por defecto en `gimg/models.json`). Qwen-Image, fuera del catálogo hoy, solo si una pieza exige
  fotorrealismo o un detalle muy concreto (el latón de los compases, el menisco de la tinta) que Z-Image no dé. Ninguno tiene
  prompt negativo efectivo: lo que no se quiere no se nombra ni negado, porque a veces se cuela.
- **Zona limpia.** El estilo es texturizado (grano, granulación, fibra de periódico) y ensucia lo que debe quedar liso. La zona
  reservada se pide como un objeto en positivo y **antes** del motivo («The left half of the frame, from the left edge to the
  middle, is open bare paper showing only its fine cotton grain, even in tone»), y el motivo se acota por sus propios límites
  («the inks and the collage stay inside the right half»); nada de «at most a couple of droplets reach its edge» (r7): invita a
  las gotas. El velo de la plantilla (0,45 → 0 al 60 % del ancho) es la red de seguridad, no el remedio; se comprueba con
  `gimg measure --zone`.
- **Recuentos.** «two inks», «three torn swatches», «a pair of dividers» orientan, no se garantizan. Lo que debe ser exacto
  (los tres colores del semáforo como tres muestras, un solo anillo de score) se compone en SVG o se acepta la variación.
- **A sangre.** Cuando la pieza no quiere marco ni banda, el papel llena el encuadre («the paper fills the frame edge to edge»);
  el borde desflecado sobre linón `#F0EDE8` es un motivo del bodegón del `og`, no la regla.
- **Recortes y mosaicos.** `gimg` no da transparencia: un elemento suelto (utensilio, anillo de score, icono) se genera sobre
  un fondo plano de croma y se recorta con `gimg brand matte` (fondo tomado del borde; `--tol 60`, `--soft 110`). Para
  toVeriAI el croma es **`#ff00ff`, nombrado solo por hex** (`pink`/`magenta` siguen vetadas como palabra; el verde `#00ff00`
  se confunde con las tintas de musgo). Una textura repetible (grano de papel, fibra) va en un perfil con `tileable: "xy"`
  (o `"x"`/`"y"`) y se pide «seamless, edge to edge».
- **Nada que pase por el logo.** Ningún prompt pide el símbolo, la «V», las hojas, el anillo con la V dentro ni el wordmark,
  tampoco como «aire de toVeriAI» en la publicación de r8: la marca la pone `compose` con el lockup real (§4, §9).

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | plana y uniforme, sin fuente; vigente (r6-r7): «photographed straight down under flat even daylight with only the faintest soft warm shadows, with a printed fine art finish»; las sombras de los utensilios, «each casting a soft warm shadow». En `r2-luz.txt`, «under flat even light falling from straight above» y las posiciones en fracciones («halfway across from the left edge and two thirds of the way down») | repo (`orders/r6-detalle.json`, `r7.json`; `prompts/estilo.txt`); la variante de r2-luz *(suposición: sin veredicto)* |
| Momento y clima | Rec. | día, luz plana de interior o de estudio; escena clara, dicha al principio («Wide abstract conceptual artwork on warm unbleached cotton paper»); nunca oscura | repo (`prompts/estilo.txt`, `r2-luz.txt`) |
| Luminosidad objetivo (YAVG) | Rec. | 180-225 (r1 162-166; r2 material 181,9; r3 borrador 186 / definitivo 180; r4 og compuesto 186,52; r5 188-196). La portada del Portal da 220 | repo (`calibracion-measure.md` l.35, l.37-38, l.70; `r3-borrador.md` l.47; `r4-composicion.md` l.17) |
| Saturación objetivo (SATAVG) | Rec. | ≤ 10 (r1 20-22, demasiado; r2 material 12,0; r4 og 10,18; r5 7-8). La portada del Portal da 2 | repo (`calibracion-measure.md` l.35, l.37-38, l.70) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **publicada dónde:** en el repo de toVeriAI, la única imagen de marca es `frontend/public/favicon.png` (512×512, con alfa): favicon (`<link rel="icon">`), `og:image` y `twitter:image` (`summary`, cuadrada) **(consta)**; las tarjetas compartibles 1080×1350 y sellos 480×480 las genera la app en el navegador del usuario y no quedan en el repo **(no consta)**; en Instagram, LinkedIn, Facebook y X las cuentas constan (`Footer.jsx` l.57-62) pero no qué imágenes llevan **(no consta)**; social preview de GitHub, no comprobable. La ficha del Portal tiene `portada.webp` (YAVG 220, SATAVG 2, paleta 95 %: casi blanca); EMD de r1 frente a ella Y 55-58, Cb 9,9-10,9, Cr 14-16; de r5, Y 24-33, Cb 4,5-5,4, Cr 2,4-5,2. **Vale como referencia:** el favicon, **sí** como imagen de marca (es lo que la web publica), pero `measure` lo lee sobre negro (1 %); la portada del Portal, **[P]** (la hizo el agente, es casi blanca; la persona dice si es marca) | VeriNews_AI (`frontend/index.html` `og:image`, `twitter:image`, `<link rel="icon">`; `Footer.jsx` l.57-62; `utils/shareImage.js`); repo (`calibracion-measure.md` l.11, l.35-38, l.53, l.81-85; `docs/handoff.md` l.38) *(suposición: la ruta de la portada es `Portal-Galivelop/public/proyectos/toveriai/portada.webp`; no se ha abierto ese repo)* |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración, cinco: `og` 1280×640, `square` 1024×1024, `portrait` 896×1152, `wide` 1280×768, `header` 1536×512; todos a `flux2-klein-4b-q8`, 6 pasos, cfg 1.0, euler; con `targetWidth`/`targetHeight` desde el 2026-11-04. **Modelo por declarar [P]:** FLUX es el de boceto; la pieza final lleva `model: "zimage-turbo-q6"`, `steps: 8`, `cfg: 1.0` en el perfil y FLUX en `draft.model` (`params` de un pedido solo cambia pasos, cfg y sampler, no el modelo; r7 ya pidió 8 pasos). Destinos: `og` → 1200×630 (og:image, y LinkedIn 1200×628 del kit); `square` → 1080×1080 (Instagram, kit l.507, l.714); `portrait` → 1080×1350 (Instagram, kit l.714); `wide` → 1200×675 (X, kit l.784; 5:3 → 16:9 recorta ~6 % de alto, `docs/handoff.md` l.66) **nunca generado**: ni prompt ni pieza; `header` → 1500×500 (cabecera de X; el kit no lo trae, sus banners son 1920×640 y 1600×600; Discord y LinkedIn serían perfiles aparte si hacen falta) | repo (`galivelop-images.json`; `piezas.json`); destinos de VeriNews_AI (`kit-visual-ia.html` l.507, l.714, l.749, l.784) y de la tabla «Común a todos» de `docs/marcas/README.md`; `header` 1500×500 como destino **[P]** (no está en el kit; aprobada por delegación) |
| Zona reservada | Obl. | **r7:** `og` pasa a `izquierda 1/2` («The left half of the frame … is open bare paper … kept clear for legibility»; las tintas y el collage en la mitad derecha, sangre de buey desde arriba a la derecha y musgo desde abajo a la derecha, la banda ámbar en diagonal), caja `data-caja` de la plantilla `60,60,604,510` (margen 60, columna 604; logo a 52-54 px de alto, titular en dos líneas, filete corto en el acento y subtítulo en dos líneas; r7); el velo claro cae de izquierda a derecha (0,45 → 0 al 60 % del ancho). Motivo: el veredicto de r6 («la posición de los textos es lo que menos convence»: logo, titular y subtítulo apretados en la franja de arriba). Hasta r6, `og`, `wide`: `arriba 1/3` («The upper third of the frame is calm, bare unbleached cotton paper»); `square`, `portrait`: `arriba 1/2` («The upper half of the frame is calm, bare…»); `header`: `izquierda 2/3` («The left two thirds of the frame are calm, bare…», las tintas «stay inside the right third»). En píxeles (conversión de la plantilla): `og` 1200×630 → `0,0,600,630` (hasta r6, `0,0,1200,210`); `square` 1080×1080 → `0,0,1080,540`; `portrait` 1080×1350 → `0,0,1080,675`; `header` 1500×500 → `0,0,1000,500`. **Una sola zona por perfil, la del prompt** (criterio 3 de las decisiones): el `og` ya coincide (caja `60,60,604,510` dentro de la mitad izquierda, r7); en `square`, `portrait` y `header` la caja del piloto no coincide hoy (`arriba` ocupa el 48 % del alto, `izquierda` el 55 % del ancho, menos que los dos tercios de `header`; margen 6 %) y **se alinea a estas fracciones al portar a `compose`** (ver «Contradicciones», 9). Cómo se pide la zona para que salga limpia: §6, «Cómo se pide con el generador». La biblia §7 recoge ya las cuatro, `header` incluido | repo (`prompts/estilo.txt`, `r5-*.txt`; `examples/pilot/componer.py` `caja_zona` l.105-115; `biblia.md` §7; `r2-estilo.md` l.16 «en toVeriAI el texto va arriba») |
| Velo por perfil | Rec. | `#F7F5F2:0.35` en los cuatro formatos compuestos (og, cuadrado, vertical, cabecera): el papel ya es claro y el velo solo iguala el grano bajo el texto | repo (`piezas.json` `velo`; `r4-composicion.md` l.17) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza (57 px en el `og`), en lo alto de la caja de la zona con el título debajo, margen 6 %. Regla del kit que lo respalda: el símbolo siempre junto al wordmark; si no caben, solo el símbolo en una esquina | repo (`componer.py` l.129-137; `r4-composicion.md` l.28-33); VeriNews_AI (`kit-visual-ia.html` l.372) |
| Composición por perfil | Rec. | **`og` ya lo declara** (desde `6abfc9d`): `compose: {template: "plantillas/og.svg", fields: ["title1","title2","subtitle","subtitle2"], logo: "logos/toveriai-a-lockup.svg", fonts: ["Cormorant Garamond","DM Sans"], fit: "cover"}`. Los otros cuatro perfiles (`square`, `portrait`, `wide`, `header`) **no**: para ellos el piloto sigue construyendo el SVG en código (`componer.construir_svg`: velo, lockup al 9 %, título Cormorant Garamond 300, subtítulo DM Sans 400 con opacidad 0,82); portarlos a `compose` con su plantilla es **[P]** (F2.8/F2.12; `docs/plan.md` l.824-826) | repo (`examples/toveriai/galivelop-images.json` l.35-49; `examples/toveriai/plantillas/og.svg`) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `toveriai-a.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180 (apple-touch-icon) / 192 (manifest) / 512: no hay; la web solo tiene el `favicon.png` de 512 y no tiene manifest ni apple-touch-icon | repo (`piezas.json`); `icon` **[P]** (`biblia.md` §9, primera ronda 5; `docs/plan.md` l.624-626) |
| Borrador | Opc. | `draft: {scale: 0.5, steps: 4}` declarado en `og` (r3 midió 640×320 a 4 pasos, 51 s: YAVG/SATAVG/paleta 186/12/66 % frente a 180/12/69 % del definitivo, anticipando estilo y hueco). El borrador es el sitio de FLUX: al pasar el perfil a Z-Image, `draft.model: "flux2-klein-4b-q8"` | **[P]** aprobada por delegación (F2.10, dec. 7; `r3-borrador.md` l.47, l.63); `draft.model` **[P]** 2026-11-11 |
| Palancas extra | Opc. | sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia desde r1 con solo decirla), sin LUT (paleta 67-77 % sobre un umbral de 65), sin conversión final por parte de `gimg`. **Croma y mosaico** (§6, «Cómo se pide»): elementos sueltos sobre `#ff00ff` por hex y recorte con `gimg brand matte`; texturas repetibles en un perfil con `tileable`. Hoy ninguna pieza los usa | repo (`r1-fondos.md` l.50; `r5-piezas.md` l.31); croma y `tileable` **[P]** 2026-11-11 |
| Prioridad | Rec. | la de la biblia: 1) og:image 1200×630 (hoy apunta al favicon de 512): «entre dos tintas» + wordmark + lema; 2) `square` «cita tipográfica»; 3) banner «el espectro» como `header`; 4) `wide` de gancho para X; 5) apple-touch-icon y manifest desde el símbolo (solo composición). Hechas en el piloto: `og`, `cuadrado`, `vertical`, `cabecera`, `avatar` (todas con «entre dos tintas»); `wide` e `icon`, sin hacer | repo (`biblia.md` §9; `docs/plan.md` l.624-626) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | «La verdad no es binaria.» (24 caracteres), en `og` | repo (`piezas.json`, r4); es el lema literal de la home (`frontend/src/i18n/es_ES.json` l.33), con punto final |
| Subtítulo | Rec. | «Entre lo cierto y lo falso hay todo un espectro. Nosotros lo medimos.» (70); en `compose` va en dos campos desde r7, `subtitle` «Entre lo cierto y lo falso hay todo un espectro.» (48) y `subtitle2` «Nosotros lo medimos.» (20), a 24 px en la columna de 604 | VeriNews_AI (`kit-visual-ia.html` l.461, primera «variación del tagline»); repo (`piezas.json`, r4) |
| Variaciones, ganchos y cierres | Rec. | usados en r5, **todos literales del kit**: `cuadrado` «Menos veredictos. Más matices.» / «No te decimos qué creer. Te damos con qué pensar.»; `vertical` «Dudar bien también es informarse.» / «Léela dos veces. O pásala por aquí primero.»; `cabecera` «La credibilidad no se decreta: se mide.» / «Analiza. Compara. Decide tú.» (el kit lo cierra con «— toVeriAI»). Sin usar: «Mide antes de creer. toVeriAI.» · «Pon a prueba tu próximo titular. Gratis, en toVeriAI.» · «¿Y si no es falsa… pero tampoco es del todo verdad?» · «Tu feed no trae etiquetas. Nosotros tampoco las ponemos.» · «El índice está en verde. ¿Y tu noticia? Compruébalo en toVeriAI.» (no recogido en la biblia) | VeriNews_AI (`kit-visual-ia.html` l.461-465, l.470-474, l.479-483); repo (`piezas.json`) |
| Longitud máxima por campo | Rec. | la fija la composición: `componer.py` baja el cuerpo hasta 16 px y falla si el texto no cabe en la zona. Orientativo con Cormorant Garamond 300 en la caja «arriba»: titular ≤ 40 (los de r4-r5 van de 24 a 39), subtítulo ≤ 70 (el más largo, 70) | repo (`examples/pilot/componer.py`; `piezas.json`) |
| Wordmark compuesto como texto | Opc. | el nombre va en el lockup como `<text>`: «to**Veri**AI», Cormorant Garamond 400, tracking 0,08 em, `Veri` en `#2D6A4F`, nunca como `text` del pedido. La web lo hace igual (tres `span`) en `Navbar`, pie y tarjeta compartible | repo (lockup); VeriNews_AI (`Navbar.jsx` l.98-104; `Footer.jsx` l.86; `ShareCard.css` l.29-31) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` | repo (`galivelop-images.json` `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto, escrito explícito) | repo (`delivery.template`) |
| Dónde se publica cada pieza | Rec. | `og`: `og:image` y `twitter:image` de `frontend/index.html` (**consta**; hoy apuntan a `https://www.toveriai.com/favicon.png`, 512 cuadrado, y `twitter:card` es `summary`, que con una pieza 1200×630 pasaría a `summary_large_image`); `square` y `portrait`: Instagram `instagram.com/toveriai/` (cuenta **consta** en el pie, piezas **no consta**); `wide`: X `x.com/toVeriAIX` y LinkedIn `linkedin.com/company/toveriai/` (cuentas **constan**, piezas **no consta**); `header`: cabecera de X y Facebook `facebook.com/profile.php?id=61591928098458` (cuentas **constan**, piezas **no consta**); `avatar`: las cuatro redes (**no consta**); `icon`: apple-touch-icon y manifest (**no existen** en el repo); social preview de GitHub, no comprobable | VeriNews_AI (`frontend/index.html` `og:image`, `twitter:image`, `twitter:card`; `Footer.jsx` l.57-62 `SOCIAL_LINKS`) |
| Otras piezas de marca que hace otro sistema | Rec. | **sí, dentro de la propia app:** `frontend/src/utils/shareImage.js` captura con `html-to-image` (`pixelRatio: 2`) la **tarjeta compartible** `ShareCard` (1080×1350, «etiqueta nutricional editorial», «Diseño acordado con Fable») y el **sello** `ShareSeal` (480×480), y los comparte por la Web Share API con título «toVeriAI». Toman paleta y fuente **a mano, en CSS propio** (`ShareCard.css`: `#2D6A4F`, `#B7E4C7`, `#B5832A`, `#9B2335`, `#52B788`, `#74C69D`, `#E8F4EE`, `#1A1A1A` y un gris verdoso **`#6B7F76` que no es token de `App.css`** (`ShareCard.css` l.50, `ShareSeal.css` l.26), Cormorant Garamond y DM Sans; `bandaImi` en `shareImage.js` l.3-7, que repite los hex de `imiColors.js` l.1-3), no de `App.css`: `ShareCard.css` no usa ni un `var(--…)`; el reparto línea a línea, en la sección 16, fila A8; **se capturan sobre `#FFFFFF` puro** (`backgroundColor: '#ffffff'`; `.shc-canvas` `background: #FFFFFF`), el blanco de fondo que el kit prohíbe (ver «Contradicciones», 8). Usan `favicon.png` + wordmark en `span`, como el `Navbar`. Además, `gw-media-content` si el repo adopta el flujo (ya tiene `GLOSSARY.md` de Galivelop-workflow v0.5.0) | VeriNews_AI (`utils/shareImage.js`; `components/share/ShareCard.jsx`, `ShareCard.css` l.5-10, l.29-31, l.84-85; `ShareSeal.jsx`, `ShareSeal.css`; `kit-visual-ia.html` l.284; `GLOSSARY.md` l.1) |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto, no declarado) | repo (esquema) |
| Conversión final | Opc. | el `og:image` de la web es PNG hoy (`favicon.png`); una pieza 1200×630 en PNG o WebP la decide el repo *(suposición: PNG, como lo que ya sirve; LinkedIn no acepta WebP en vista previa)* | VeriNews_AI (`frontend/index.html`) |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona: r1 «sí» (2026-10-26, por proyecto; nota: «el vino tira a magenta»); r2-r5 delegado al agente. Apuntado en `docs/records/contenido/r1-fondos.md` l.50-53, `r2-estilo.md` l.53 (elegida «material»), `r4-composicion.md` l.17, `r5-piezas.md` l.31. Pendiente de la persona: el símbolo SVG (`docs/plan.md` l.260) y las dos decisiones delegadas de marca (`docs/marcas/README.md` l.39-42) | repo |
| Contraste del texto | Rec. | ≥ 4,5:1 (por defecto); medido con velo `#F7F5F2:0.35` y texto `#1A1A1A`: og r4 15,5 (peor 15,0); r5 cuadrado 15,92 (15,6), vertical 15,19 (14,69), cabecera 15,05 (14,83). Todas sobre el 7:1 de AAA; el papel claro lo regala | repo (`r4-composicion.md` l.17; `r5-piezas.md` l.31) |
| Umbrales de medida | Rec. | los de las secciones 3 y 7: paleta ≥ 65 %, YAVG 180-225, SATAVG ≤ 10 | repo (`calibracion-measure.md` l.70) |
| EMD frente a la marca | Opc. | Cb ≤ 6 / Cr ≤ 6 (frente a la portada del Portal: r5 Cb 4,5-5,4, Cr 2,4-5,2; r1 Cb 9,9-10,9, Cr 14-16, fuera). La EMD de Y (24-33) pesa la composición y no sirve sola | repo (`calibracion-measure.md` l.37-38, l.70) *(suposición: la referencia, sección 8)* |
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» de la persona en r1 y la palanca de r1 («oxblood» en vez de vino) funcionó en r2; r5 dio las tres piezas de formato a la primera y «la acuarela de toVeriAI» se reconoce en la hoja de contactos (`r5-piezas.md` l.51). Pendiente: el veredicto de la persona sobre el símbolo y lo delegado, `wide` e `icon` | repo (registros r1-r5) |

## 13. Fuentes de verdad

**VeriNews_AI** (toVeriAI), `main` `1f98db6` (leído solo; nada modificado; las líneas se han vuelto a mirar el 2026-11-12):

- `frontend/index.html` (`<title>` «toVeriAI — Verificación de credibilidad de noticias con IA»; `<meta name="description">`;
  `og:image` y `twitter:image` = `https://www.toveriai.com/favicon.png`; `twitter:card` `summary`; canonical
  `https://www.toveriai.com/`; `<link rel="icon" type="image/png" href="/favicon.png">`; `ld+json` `Organization` y
  `WebApplication` con `inLanguage ["es","ca","gl","eu","en"]` y precio 0 EUR).
- `frontend/src/App.css` l.10-12 (`--font-sans` DM Sans, `--font-serif` Cormorant Garamond, `--font-mono`), l.114-124 (papel,
  tarjeta, alterno, texto, apagados, bordes, blanco), l.127-139 (verdes, ámbar, granate y sus claros y fondos), l.142-155
  (colores de métricas, de interfaz), l.158-160 (línea `#D8D4CF`, gris `#999999`, borde oscuro `#2A2A2A`), sombras, radios
  (`3px, 4px, 6px, 999px`), `--text-display-sm 26px` (logo).
- `frontend/src/fonts.css` l.1-130 (`@font-face` auto-alojadas: Cormorant Garamond 300/400/500 y 300/400 cursiva, DM Sans
  300/400/500; sin 600/700) y `frontend/public/fonts/` (seis woff2).
- `frontend/src/components/Navbar.jsx` l.98-104 y `Navbar.css` l.16-27 (favicon 36 px + wordmark en tres `span`, Cormorant
  Garamond 400, 26 px, tracking 0,08 em, `to`/`AI` `--color-dark`, `Veri` `--color-green`); `Footer.jsx` l.50-54 (idiomas),
  l.57-62 (`SOCIAL_LINKS`: Instagram, LinkedIn, Facebook, X), l.86 (wordmark); `Footer.css` l.22-27 (wordmark blanco a peso 300
  sobre `#1A1A1A`).
- `frontend/src/i18n/es_ES.json` l.33 (`home.title` «La verdad no es binaria»), l.529-531 (rangos «Baja (0–39)», «Moderada
  (40–69)», «Alta (70–100)»; igual en los otros cuatro idiomas).
- `frontend/src/utils/imiColors.js` (`C_GREEN #2D6A4F`, `C_AMBER #B5832A`, `C_RED #9B2335`; ≥ 70 / ≥ 40; claros
  `#52B788/#E9A94A/#E07085`; fondos `#EFF8F3/#FBF6ED/#FBF0F2`); las excepciones `pages/AdminPage.jsx` l.12-13 y
  `AdminDatasetPage.jsx` l.100-101 (≥ 75 / ≥ 50) y `AdminIncidenciasPage.jsx` l.29 (`#C0392B`).
- `frontend/src/utils/shareImage.js`, `components/share/ShareCard.jsx`, `ShareCard.css` l.5-10, l.15, l.29-34, l.48, l.84-85,
  `ShareSeal.jsx`, `ShareSeal.css` l.6-36 (tarjeta 1080×1350 y sello 480×480; captura sobre `#ffffff`; `bandaImi`).
- `frontend/src/pages/ComoFuncionaPage.css` l.10, `DimensionesPage.css` l.10, `EscalaIMIPage.css` l.10 y l.91,
  `HistorialPage.css` l.57, `FeedPublicoPage.css` l.5, `Auth.css` l.11 (degradados del hero `#1B4332 → #2D6A4F → #40916C` y
  espectro del IMI).
- `frontend/uno.config.ts` (`vn-label` 0,24 em mayúsculas; `vn-btn-base` 0,14 em).
- `frontend/public/favicon.png` (512×512 RGBA; idéntico a `frontend/src/assets/favicon.png`); `frontend/src/assets/logo.png`
  (2190×1980) y `logo-vertical.png` (2230×750), wordmark «VeriNews», **sin referencias** en el frontend.
- `Documentacion/v1.1/kit-visual-ia.html` l.6 (v1.1), l.45 (hero `#1c3028 → #2D6A4F`), l.248-266 (tabla de paleta), l.271-276
  (combinaciones), l.281 (sombras), l.284 (acento único y prohibidos), l.298-310 (tipografía, «nunca bold»), l.325 (tracking),
  l.335 (wordmark), l.345 (margen y mínimo), l.348-372 (símbolo, favicon.svg huérfano, no inventar símbolo, convivencia),
  l.397-414 (iconos ~1,3 px, radios), l.425-428 (tono, campo semántico), l.442-447 (rangos IMI y nota del granate), l.457-483
  (lema, variaciones, ganchos, cierres), l.494-806 (20 prompts; l.507, l.547, l.559, l.689, l.714, l.749, l.772, l.784 los
  formatos), l.846 («valores sacados literales del código real»).
- `Documentacion/v1.1/marketing.html` l.6 (`<title>` «toVeriAI — …»), l.278-285 (rangos 0–49 / 50–74 / 75–100 con `#e74c3c`,
  `#c9761f`, `#27ae60`), l.486 (beta).
- `README.md` l.1-10 (TFC de DAW, «siete dimensiones», «ES, GL, CA, EU», autores), `GLOSSARY.md` l.1 (flujo v0.5.0), «IMI»,
  «Dimensión».
- **Ya no existe:** `frontend/public/favicon.svg` (borrado en `e8b251c`). **No existe:** manifest, apple-touch-icon,
  `theme-color`, SVG del símbolo, pieza `og` 1200×630, tema oscuro (ni `prefers-color-scheme` ni `data-theme` en `frontend/src`
  ni en `index.html`). **Existe y nadie lo usa:** `frontend/public/icons.svg`, un sprite de seis iconos (`bluesky-icon`,
  `discord-icon`, `documentation-icon`, `github-icon`, `social-icon`, `x-icon`) con relleno `#08060d`, fuera de la paleta y sin
  referencias en `frontend/src` ni en `index.html`.

**Este repo**, `f2-motor` `5460d2c`:

- `examples/toveriai/galivelop-images.json` (`name`, `brand.palette` de 4 hex, `delivery`, perfiles `og`, `square`, `portrait`,
  `wide`, `header`; último cambio `b65bd81`).
- `examples/toveriai/piezas.json` (fuentes Cormorant Garamond / DM Sans, `peso_titulo` 300, textos, zona, color de texto y velo
  de las cuatro piezas, ruta del lockup y del avatar).
- `examples/toveriai/prompts/estilo.txt`, `og.txt`, `r2-material.txt`, `r2-hex.txt`, `r2-palabras.txt`, `r2-luz.txt`,
  `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` y `orders/r1-og.json`, `r2-control.json`, `r2-luz.json`, `r6-detalle.json` (`32739be`) y `r7.json` (`af139bf`) (motivo, estilo,
  zona por formato, luz).
- `docs/marcas/toveriai/logos/toveriai-a.svg` y `-a-lockup.svg` (último cambio `b7f1baf`); las propuestas `b`-`d` siguen en la
  carpeta (`b`, dos trazos con remates redondos y tres puntos, candidata para ≤ 32 px).
- `docs/marcas/README.md` l.14 («elegido **a** (b ≤ 32 px)»), l.39-42 (decisiones delegadas: wordmark «toVeriAI», rangos del kit),
  l.84 (familia), l.125 (degradados), l.143-150 (conceptos de logo), tabla «Común a todos».
- `docs/marcas/toveriai/biblia.md` (`74d99f8`; cita `02ac654`; incoherencias 1-4, paleta, tipografía, reglas del logo, vetos,
  frases, tabla de prompts; lo que es **[P]** allí lo sigue siendo aquí).
- `docs/plan.md` l.258-261 (decisiones del 2026-10-26: «el agente vectoriza el símbolo de toVeriAI como SVG y la persona lo
  aprueba»), l.586 (acento del Portal `#2F7A55`), l.612-626 («Estilos por proyecto», toVeriAI), l.824-826 (`compose` con
  Cormorant Garamond y DM Sans).
- `docs/records/contenido/calibracion-measure.md` l.11, l.35-38, l.53, l.70, l.81-85; `r1-fondos.md` l.50-53, l.60, l.68;
  `r2-estilo.md` l.16, l.39-41, l.53, l.67; `r3-borrador.md` l.47, l.63; `r4-composicion.md` l.17, l.28-33; `r5-piezas.md` l.31,
  l.51, l.56; `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.129-154, l.256-285.
- `docs/handoff.md` l.38 (leves de F2.9: alfa, portada casi blanca), l.66 (`wide` 5:3 → 16:9).
- `examples/pilot/componer.py` l.105-115 (`caja_zona`), l.119 (`peso_titulo`), l.129-137 (logo al 9 %), l.159-160 (subtítulo
  400); `examples/pilot/fuentes.sh` (origen y licencia de las fuentes).

Sin línea aquí y por tanto **[P]** o *(suposición)*: el dibujo del símbolo SVG, el lockup oscuro, la variante `b` para ≤ 32 px,
«VeriNews» como prohibido, la pieza oscura con su velo, `header` 1500×500 como destino, `compose`, `icon`, la portada
del Portal como marca, el formato del `og:image` final.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo y a `VeriNews_AI`):

- ~~Texto `#1A1A1A` fuera de `brand.palette`~~ **resuelto (2026-11-04)**: la paleta lleva ya `#1A1A1A`, `#FDFCFB`, `#F0EDE8` y `#FFFFFF`.
- ~~Ningún perfil lleva `targetWidth`/`targetHeight`~~ **resuelto (2026-11-04)**, con estos destinos: `og` → 1200×630, `square` → 1080×1080, `portrait` →
  1080×1350, `wide` → 1200×675, `header` → 1500×500. El piloto los entrega ya a esos tamaños (`piezas.json`).
- `wide` declarado (1280×768) y nunca generado: ni prompt ni pieza; `icon` (primera ronda 5 de la biblia) no se puede declarar
  (hueco) y no está hecho.
- `compose`: el perfil `og` lo declara (`galivelop-images.json` l.35-49, plantilla `plantillas/og.svg`, desde `6abfc9d`); para
  `square`, `portrait`, `wide` y `header`, plantilla, fuentes, zona, velo `#F7F5F2:0.35`, peso 300 y logo al 9 % siguen en
  `examples/pilot/componer.py` y `piezas.json`.
- `prompts/og.txt` y `orders/r1-og.json` llevan «without» y «neither red nor green» (comprobación 8: negación y nombra `red`):
  se dejan como histórico (decisión del 2026-11-04); `orders/r7.json` lleva «no readable letters, words or numbers anywhere»
  y «like a bandage» (negación, `letters`, `words` y comparación) y 431 palabras: es la dirección vigente, se corrige en el
  pedido de r8 (§6) y no se toca el histórico.
- Los cinco perfiles declaran `flux2-klein-4b-q8` (boceto); la pieza final pide `zimage-turbo-q6` a 8 pasos y FLUX en
  `draft.model` (§9, Perfiles y Borrador). Sin perfil con `tileable` ni pieza sobre croma (ninguna lo necesita hoy).
- Copia de los logos en `examples/toveriai/logos/`: solo el lockup `a` (`6abfc9d`, lo usa el `compose` de `og`); el símbolo suelto,
  pendiente de A1 (§16).
- En `VeriNews_AI`: el `og:image` apunta al favicon de 512 y `twitter:card` es `summary`; no hay manifest ni apple-touch-icon;
  los PNG «VeriNews» siguen en `assets/`; la tarjeta compartible toma los hex a mano y se captura sobre `#ffffff`. Todo va a
  `docs/propuestas/verinews-ai/entrega-hoja-2026-11-12.md` (escrita el 2026-11-12), no se toca desde aquí.

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; sale de la `description` y el `ld+json` de `index.html`) |
| 3 | «Nunca se muestra» no vacío | pasa (lista del kit l.425); nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | pasa (8 hex): fondo `#F7F5F2`, texto `#1A1A1A` y acento `#2D6A4F` están (la hoja nombra los roles, la configuración no los lleva) |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, `<title>`, sin `<text>`/`<image>`/`filter`; dos colores de la paleta); **legibilidad a 16 px sin mirar** (`rsvg-convert -w 32` pendiente; el README reserva `b` para ≤ 32 px); copia en `examples/<p>/logos/`: solo el lockup `a` (`6abfc9d`); **el dibujo es [P]** (la persona lo aprueba) |
| 6 | Familia de titular instalada | **no comprobable**: `og` declara `compose.fonts` (Cormorant Garamond, DM Sans; `galivelop-images.json` l.44-47), pero las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts` |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | **pasa salvo dos:** `og.txt` y `orders/r1-og.json` llevan «without» y «neither red nor green» (r1, histórico, no se tocan); `orders/r7.json` lleva «no readable letters, words or numbers anywhere» y «like a bandage» (negación, `letters`, `words`, comparación: se corrige en r8). `estilo.txt`, `r2-material/hex/palabras/luz.txt`, `r5-*.txt`, `orders/r2-control.json`, `r2-luz.json` y `r6-detalle.json` pasan con la lista del 2026-11-11 (grep de ese día) |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa en los nueve prompts (138-193 palabras) y en `r6-detalle.json` (310); `r7.json` acaba bien pero tiene 431 (sobre 320 FLUX recorta; con Z-Image, sin medir) |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | múltiplos de 64 pasa (los cinco); destino declarado en los cinco (2026-11-04) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | el prompt la describe en los cuatro formatos generados (`wide` no tiene prompt); ningún perfil la declara (hueco de esquema); la fracción de cada perfil es la del prompt y la caja del piloto se alinea al portar a `compose` |
| 12 | Titular ≤ 200, cabe en la columna | pasa (24 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | pasa desde el 2026-11-04: texto `#1A1A1A` (también en el lockup), superficies `#FDFCFB`/`#F0EDE8`, blanco `#FFFFFF`, fondo `#F7F5F2`, acento `#2D6A4F` y los dos colores del símbolo están |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | pasa desde el 2026-11-04 en los cinco perfiles (`og` 1280×640 → 1200×630; `square` 1024 → 1080; `portrait` 896×1152 → 1080×1350; `wide` 1280×768 → 1200×675; `header` 1536×512 → 1500×500) |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 18** (familia propia).
**17 salen de un repo** (14 de `VeriNews_AI` directa o indirectamente, el resto de este) y **1 es [P]**: el dibujo del símbolo SVG,
que la persona tiene que aprobar según el plan.

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan: roles de la paleta (`brand.palette` no distingue el acento único de las piezas
genéricas del semáforo del IMI), zona reservada (solo en prompt y en `componer.py`, y con tres fracciones distintas según el
formato), velo y logo en la pieza (solo en `componer.py`), palabras vetadas sin campo (y un prompt histórico con negaciones),
`avatar` sin perfil (lo hace `piezas.py`) e `icon` declarado desde el 2026-11-13 (1024² → 512²; la web no tiene manifest ni apple-touch-icon: sería la
primera pieza útil), **varias variantes de logo** (lockup claro y oscuro obligan a dos plantillas; solo existe el claro),
tipografía sin licencia ni ruta declaradas (aunque el repo de toVeriAI sí las aloja), imágenes de marca para la EMD sin lista (el
favicon con alfa se mide mal y la portada del Portal es casi blanca), idiomas y textos por idioma (la web publica en cinco; las
piezas solo en `es`), copia de los logos en `examples/<p>/logos/` a medias (solo el lockup `a`). No le afectan: `compose.lut` (paleta 67-77 % sobre
65), `style.lora`.

**Hueco propio de este proyecto, que la plantilla ya recoge desde Workflow pero con otra cara:** el «otro sistema que hace
piezas de marca» no es una skill del flujo sino **la propia aplicación**, que genera piezas en el navegador del usuario final
(tarjeta y sello compartibles) con los hex copiados a mano en su CSS. La hoja debería ser su fuente igual que lo es de `gimg`;
hoy nada los alinea y la tarjeta ya se desvía (fondo `#ffffff`).

## 16. Ampliaciones propuestas (2026-11-12)

**Todo lo de esta sección es PROPUESTA (no decidida).** No cambia la identidad de toVeriAI (papel cálido, Cormorant Garamond +
DM Sans, verde bosque `#2D6A4F`, semáforo del IMI): añade lo que el repo no tiene hoy y `gimg` puede darle. Cada fila dice qué
falta (con su fuente en `VeriNews_AI` `1f98db6`), qué pieza de `gimg` lo produce y en qué perfil de
`examples/toveriai/galivelop-images.json`, y quién decide. Nada se dibuja a mano: los SVG salen de `gimg brand trace` sobre un
PNG, y las imágenes, de un pedido. La entrega para la sesión de su repo es
`docs/propuestas/verinews-ai/entrega-hoja-2026-11-12.md`; nada de esto se ha generado todavía.

| # | PROPUESTA | Qué falta hoy (fuente) | Pieza de `gimg` y perfil | Decide |
|---|---|---|---|---|
| A1 | **Símbolo en SVG sacado de su PNG** | el símbolo solo existe como `frontend/public/favicon.png` 512×512 RGBA (igual a `frontend/src/assets/favicon.png`); no hay SVG del símbolo en el repo. El `logos/toveriai-a.svg` de aquí (`b7f1baf`) se dibujó antes de la regla «todo nace del generador» y sigue sin aprobar (§4) | `gimg brand trace <favicon.png> --mode color --palette "#2D6A4F,#B5832A"` (el PNG ya trae alfa: sin `--matte`); alternativa fiel al píxel, `--colors 2`, que saca el salvia y el dorado del PNG (Contradicciones, 3). Sin perfil: es una orden de marca, no genera | su dueña/dueño: qué colores (kit o PNG) y si sustituye al `a` |
| A2 | **Variantes mono y silueta del símbolo** | no hay ninguna; el símbolo tiene dos colores y a 16-32 px los once puntos se empastan *(suposición: sin mirar)* | `gimg brand trace <favicon.png> --mode mono` y `--mode silhouette`; se usa en `#1A1A1A` sobre claro y `#FFFFFF` sobre oscuro. Sin perfil | su dueña/dueño, viendo la hoja de contactos (A13) |
| A3 | **Wordmark y lockups «toVeriAI» a trazos** (horizontal y vertical), en lugar de los PNG «VeriNews» | `frontend/src/assets/logo.png` (2190×1980) y `logo-vertical.png` (2230×750) llevan el nombre viejo y nadie los importa; el wordmark vive solo como tres `span` (`Navbar.jsx` l.101-103) | `gimg brand system` sobre el favicon con `--name toVeriAI --text toVeriAI --font CormorantGaramond[wght].ttf --weight 400 --spacing 0.08` (peso y tracking de `Navbar.css` l.18-26): PNG sin fondo, emblema en color y mono, nombre, dos lockups (`h`, `v`) y su hoja de contactos. **Límite:** `brand wordmark` y `brand lockup --color` dan el nombre en **un solo color**; el «Veri» en verde no sale de ahí. El lockup a dos tintas sigue siendo el `<text>` de `compose` (`examples/toveriai/logos/toveriai-a-lockup.svg`). Sin perfil | su dueña/dueño: si quiere los lockups mono o espera a que `gimg` dé el nombre a dos tintas |
| A4 | **Lockup para fondo oscuro, con «Veri» legible** | el pie pinta `to`/`AI` en blanco y `Veri` en `--color-green` sobre `#1A1A1A` (`Footer.css` l.22-27; kit l.275, «pieza oscura», acento `#2D6A4F`): **2,72:1**, por debajo del 3:1 que WCAG pide incluso a texto grande | `gimg brand lockup <emblema> <nombre> --color "#FFFFFF"` (mono claro); para dos tintas sobre oscuro, `Veri` en `#52B788` (`--color-green-mid`, `App.css` l.128; 7,03:1 sobre `#1A1A1A`), que es el verde que el kit da para fondo oscuro. Sin perfil; en piezas, plantilla oscura de `compose` | su dueña/dueño: cambia un color del wordmark en el pie; hasta que decida, §4 sigue diciendo «`Veri` siempre en `#2D6A4F`» |
| A5 | **`og:image` 1200×630** | `index.html` l.29 y l.36 apuntan a `https://www.toveriai.com/favicon.png` (512, cuadrado) y l.33 dice `twitter:card` `summary` | perfil `og` (1280×640 → 1200×630), plantilla `plantillas/og.svg`, lema de §10; ya compuesto en r4-r7, falta el veredicto de r8 (§6) | la persona de aquí da el veredicto; su dueña/dueño lo publica |
| A6 | **Tarjetas para redes** | las cuatro cuentas constan (`Footer.jsx` l.57-62), ninguna pieza en el repo | perfiles `square` (1080×1080, Instagram), `portrait` (1080×1350), `wide` (1200×675, X y LinkedIn; **nunca generado**: le falta prompt) y `header` (1500×500, cabecera de X); textos de §10, todos literales de su kit | su dueña/dueño: qué redes y qué frases |
| A7 | **Iconos de aplicación** (apple-touch-icon 180, manifest 192 y 512, favicon 32) y `theme-color` | `index.html` l.5 solo tiene `<link rel="icon" … href="/favicon.png">`; no hay manifest, ni apple-touch-icon, ni `theme-color` | desde el SVG de A1 (y el mono de A2 para 32 px). **Hueco de `gimg`:** no hay perfil `icon` (§15); hoy lo haría el piloto, como el `avatar`. `theme-color` propuesto: `#F7F5F2` (`--color-bg`, `App.css` l.114) | su dueña/dueño; depende de A1 |
| A8 | **Tarjeta compartible con tokens** en vez de hex copiados | `ShareCard.css` no usa ningún `var(--…)`: `#FFFFFF` (l.8), `#1A1A1A` (l.10, l.30), `#2D6A4F` (l.15, l.31), `#B7E4C7` (l.20, l.36, l.74, l.81, l.83), `#B5832A` (l.34, l.63, l.71, l.84), `#74C69D` (l.49), `#6B7F76` (l.50), `#52B788` (l.64), `#E8F4EE` (l.78), `#9B2335` (l.85); `font-weight: 700` en l.52 (no hay woff2 de ese peso: `fonts.css` solo 300/400/500); `ShareSeal.css` l.26, l.33, l.37 igual; `shareImage.js` l.5-7 repite `imiColors.js` l.1-3 y l.21 captura sobre `'#ffffff'` | no la produce `gimg` (la genera la app en el navegador): la hoja le da los tokens (tabla de la entrega) y `gimg measure <captura.png> --palette …` y `--zone … --text "#1A1A1A"` la comprueban después. `#6B7F76` **no tiene token**: o entra en `App.css` como token nuevo o pasa a `--color-muted` (`#777777`, l.119) | su dueña/dueño: fondo (`#F7F5F2` o `#FDFCFB`), qué hacer con `#6B7F76` y con el 700 |
| A9 | **Serie de iconos propia** | los iconos van como SVG en línea en cada componente (p. ej. el chevrón de `Navbar.jsx` l.202-204); `frontend/public/icons.svg` es un sprite ajeno a la marca (relleno `#08060d`) que nadie referencia | cada icono, un pedido sobre croma `#ff00ff` en `square`, recorte con `gimg brand matte` y `gimg brand trace --mode mono`; reglas del kit l.397 (trazo ~1,3 px, sin relleno, un color) y de §6 «Lenguaje de forma»; se acepta si se lee a 24 px | su dueña/dueño: si quiere serie propia y de qué conceptos (dimensiones del IMI, tipos de entrada, estados) |
| A10 | **Ilustración para la web** (cabeceras de página, estados vacíos, 404) y los cuatro motivos del kit sin probar | las cabeceras son un degradado CSS (`ComoFuncionaPage.css` l.10 y otras tres); de los cinco motivos de §6 solo «entre dos tintas» está generado | estilo y forma de pedir de §6; `header` para cabeceras, `og` y `wide` para apaisadas, `square` para estados vacíos; una ronda por motivo (espectro, cita tipográfica, doble página, anillo de score), en borrador FLUX y pieza con Z-Image | su dueña/dueño: si la web lleva ilustración o se queda tipográfica |
| A11 | **Tema oscuro: no** en la web; solo piezas oscuras compuestas | no hay tema oscuro (ni `prefers-color-scheme` ni `data-theme` en `frontend/src`); lo único oscuro es el pie y el «hero de contraste» (kit l.275) | recomendación: no ofrecerlo (la marca es papel claro, §3); para una pieza oscura, fondo plano `#1A1A1A` compuesto por `compose`, sin imagen generada, con los pares de contraste de abajo | su dueña/dueño |
| A12 | **Reglas comprobables** (contraste, tamaños mínimos, zona libre) | el kit da margen y mínimo en prosa (l.345, l.348) y ningún contraste medido | tabla de abajo; en piezas, `gimg measure --zone X,Y,W,H --text #RRGGBB` da el contraste real; zona libre con `gimg brand lockup --margin` (en diámetros del emblema) | su dueña/dueño confirma los mínimos |
| A13 | **Hoja de contactos para decidir** | — | `gimg sheet` con A1-A4 a 16, 32, 64 y 512 px sobre `#F7F5F2` y sobre `#1A1A1A`: una sola imagen para decir sí o no | la persona de aquí la manda; su dueña/dueño decide |

**Contrastes de sus propios tokens** (calculados el 2026-11-12 con la fórmula de luminancia relativa de WCAG 2.1 sobre los hex
de `frontend/src/App.css` l.114-139 y l.159; umbrales: 4,5:1 texto normal, 3:1 texto grande —desde 24 px, o 18,66 px en
negrita— y elementos gráficos):

| Par (texto sobre fondo) | Contraste | Vale para |
|---|---|---|
| `#1A1A1A` sobre `#F7F5F2` / `#FDFCFB` / `#F0EDE8` | 15,99 / 16,98 / 14,90 | todo |
| `#2D6A4F` sobre `#F7F5F2` / `#FDFCFB` / `#F0EDE8` / `#E8F4EE` | 5,87 / 6,24 / 5,47 / 5,66 | todo |
| `#FFFFFF` sobre `#2D6A4F` | 6,39 | todo (botones) |
| `#9B2335` sobre `#F7F5F2` / `#FDFCFB` / `#FBF0F2` | 7,19 / 7,63 / 7,02 | todo |
| `#B5832A` sobre `#F7F5F2` / `#FDFCFB` / `#FBF6ED` / `#FFFFFF` | 3,09 / 3,28 / 3,12 / 3,36 | **solo texto grande y gráficos**: el ámbar del IMI no pasa como texto pequeño |
| `#777777` sobre `#F7F5F2` / `#FDFCFB` | 4,12 / 4,37 | **solo texto grande**: el gris apagado se queda corto para cuerpo |
| `#999999` / `#AAAAAA` sobre `#F7F5F2` | 2,62 / 2,13 | **ninguno**: solo decorativo |
| `#FFFFFF` sobre `#1A1A1A` | 17,40 | todo |
| `#2D6A4F` sobre `#1A1A1A` | 2,72 | **ninguno** (es el «Veri» del pie: A4) |
| `#52B788` / `#74C69D` / `#B7E4C7` sobre `#1A1A1A` | 7,03 / 8,54 / 12,38 | todo |
| `#B5832A` / `#E9A94A` sobre `#1A1A1A` | 5,18 / 8,49 | todo |
| `#9B2335` / `#E07085` sobre `#1A1A1A` | 2,23 / 5,66 | el granate oscuro, **ninguno**; el claro, todo |
| `#B7E4C7` sobre `#2D6A4F` | 4,55 | todo, por poco (cabecera de la tarjeta compartible) |

**Tamaños mínimos y zona libre** (PROPUESTA; lo que ya decía §4, puesto en cifras que se pueden comprobar): wordmark, 18 px
de alto como mínimo y por debajo solo el símbolo (kit l.345); símbolo en color hasta 32 px y, por debajo, la variante mono de
A2 *(suposición hasta ver A13)*; zona libre del lockup, la altura de la «V» (kit l.345), que en `gimg brand lockup` se
aproxima con `--margin 0.25`; en una pieza, el lockup al 9 % del alto (§9) y nunca a menos de 32 px de alto.

---

## Contradicciones

Entre el repo de toVeriAI (`1f98db6`; ninguna cambia de estado entre `5a7401f` y `1f98db6`) y su propio kit, entre el repo y la biblia (`74d99f8`), o entre la biblia y lo que ya
generó el motor.

1. **Wordmark «toVeriAI» frente a «VeriNews».** El código (`Navbar`, pie, `ShareCard`), el `<title>`, el `ld+json` y el kit
   dicen «toVeriAI»; los PNG `frontend/src/assets/logo.png` y `logo-vertical.png` dicen «VeriNews» con `Veri` gris, y **ningún
   archivo del frontend los referencia**. El `README.md` llama al proyecto «VeriNews AI» (es su nombre académico).
   **Resuelta (aprobada por delegación):** la hoja manda con «toVeriAI» (decisión delegada, `docs/marcas/README.md` l.39-42, que la persona confirma);
   en `docs/propuestas/verinews-ai/entrega-hoja-2026-11-12.md` se le pide al repo retirar los dos PNG huérfanos o regenerarlos con el wordmark actual.
2. **Rangos del IMI.** Kit (l.442-444), `imiColors.js`, i18n (l.529-531) y seis páginas dicen 0-39 / 40-69 / 70-100 con
   granate / ámbar / verde; `Documentacion/v1.1/marketing.html` l.278-285 dice 0-49 / 50-74 / 75-100 con `#e74c3c`, `#c9761f`,
   `#27ae60` (colores fuera de marca); `AdminPage.jsx` l.12-13 y `AdminDatasetPage.jsx` l.100-101 cortan en ≥ 75 / ≥ 50, y
   `AdminIncidenciasPage.jsx` l.29 pinta el bajo con `#C0392B`. **Resuelta (aprobada por delegación):** en las piezas, los rangos y colores del kit (lo
   que ve el usuario, decisión delegada); al repo se le apunta la incoherencia de `marketing.html` y de las tres páginas de
   administración, sin tocarlas desde aquí.
3. **Colores del símbolo.** El `favicon.png` real usa un verde salvia (~`#6B8176`) y un dorado (~`#AD8E5C`), medidos; el SVG `a`
   usa los hex del kit (`#2D6A4F`, `#B5832A`), como pide el kit l.362 («dos de los trazos exteriores en verde bosque #…»).
   **Resuelta (aprobada por delegación):** mantener los hex del kit en el SVG (así el logo está dentro de la paleta y mide); si la persona prefiere el
   favicon tal cual, se recolorea el SVG y se añaden los dos hex a `brand.palette`. Es parte de lo que aprueba al ver el símbolo.
4. **`favicon.svg` ya no existe.** La biblia (incoherencia 4) y el kit (l.352) hablan de un `favicon.svg` morado huérfano; en
   `5a7401f` está borrado (`e8b251c`). **Resuelta (aprobada por delegación):** quitar la incoherencia 4 de la biblia; el kit la corrige su repo.
5. **Degradado del hero.** Kit l.45: `#1c3028 60 % → #2D6A4F`; código: `linear-gradient(135deg, #1B4332 0%, #2D6A4F 55%,
   #40916C 100%)` en cuatro páginas (`FeedPublicoPage.css` y `Auth.css` con variantes). La biblia §2 copia el kit. **Resuelta (aprobada por delegación):**
   para las piezas no importa (sin degradados); la biblia anota los dos y señala que el kit l.846 («valores sacados literales del
   código real») no se cumple aquí.
6. **Acento según el Portal.** `docs/plan.md` l.586 y la biblia del Portal dan a toVeriAI el acento `#2F7A55`; el repo dice
   `#2D6A4F` en todas partes. **Resuelta (aprobada por delegación):** `#2D6A4F` manda (es el del producto); el `#2F7A55` es cosa del Portal, que puede
   mantenerlo como su aproximación o corregirlo; se apunta en la propuesta al Portal, no aquí.
7. **Commit citado por la biblia.** La biblia cita `02ac654`; el repo está en `5a7401f` (2026-11-03). Entre los dos, de lo visual
   solo cambia `Navbar.jsx` (9 líneas). **Resuelta (aprobada por delegación):** actualizar la cita en la biblia a `5a7401f` al aprobar esta hoja. **2026-11-12:** hoja y biblia citan ya `1f98db6`; de `5a7401f` a `1f98db6` vuelve a cambiar solo `Navbar.jsx` (rótulos de administración a i18n), sin efecto en la marca.
8. **La tarjeta compartible rompe dos reglas del kit.** `ShareCard.css` l.8 y `shareImage.js` capturan sobre `#FFFFFF` puro,
   que el kit l.284 prohíbe como fondo; `.shc-dim-name` va a `font-weight: 500` y hay un `700` en l.52, cuando el kit l.310 dice
   «nunca bold» (y `fonts.css` no sirve ese peso: el navegador lo sintetiza). Además toma los hex a mano, no de `App.css`.
   **Resuelta (aprobada por delegación):** la hoja es la fuente de la tarjeta igual que de `gimg` (fila «Otras piezas», sección 11); al repo se le
   propone fondo `#F7F5F2` (o `#FDFCFB`) y variables de `App.css` en `ShareCard.css`; `gimg` no la sustituye.
9. **Zona reservada: fracción del prompt frente a caja del piloto.** Los prompts piden `arriba 1/3` (og), `arriba 1/2` (square,
   portrait) e `izquierda 2/3` (header); `componer.py` compone en una caja del 48 % del alto (`arriba`) o del 55 % del ancho
   (`izquierda`), margen 6 %: en el `og` el texto puede caer por debajo del tercio limpio (el contraste salió 15,0 porque el
   velo y el papel lo absorben); en la `cabecera` la caja desaprovecha un 12 % de ancho. La biblia §7 dice «tercio superior (og,
   wide) o mitad superior (square)» y no menciona `header`. **Resuelta (aprobada por delegación):** declarar las tres fracciones en la hoja (hecho,
   sección 9) y alinear la caja al portar a `compose` (pendiente del piloto); `izquierda 2/3` para `header` ya está en la biblia §7.
10. **Siete o nueve dimensiones; cuatro o cinco idiomas.** `README.md` del repo: «siete dimensiones», «ES, GL, CA, EU»;
    `index.html`: «9 dimensiones», cinco idiomas con `en`; `GLOSSARY.md`: siete en texto y nueve en URL. **Resuelta (aprobada por delegación):** en las
    piezas no se nombra la cifra salvo que la pida una pieza concreta, y entonces «7 o 9 según el tipo de entrada»; los idiomas
    de las piezas son los cinco del código. Se apunta al repo que el `README.md` está desfasado.
11. **`og:image` cuadrado.** `index.html` sirve el favicon de 512 como `og:image` y `twitter:image` con `twitter:card` `summary`.
    **Resuelta (aprobada por delegación):** la pieza `og` 1200×630 de esta hoja (ya compuesta en r4) pasa a `og:image`, con `twitter:card`
    `summary_large_image`; es la primera pieza de la prioridad y la entrada principal de `docs/propuestas/verinews-ai/entrega-hoja-2026-11-12.md`.
12. **Peso del wordmark en el pie.** El kit l.335 y el `Navbar` ponen el wordmark a 400; `Footer.css` l.24 lo pone a 300 sobre
    `#1A1A1A`. **Resuelta (aprobada por delegación):** el lockup oscuro, si se hace, a 400 como el kit; se apunta al repo la diferencia, menor.
13. **Pesos de la familia Galivelop.** La regla acordada para la familia (titular 700, subtítulo Inter 400 con opacidad 0,82) no
    aplica a toVeriAI, que tiene familia propia y el kit dice «nunca bold». **Resuelta (aprobada por delegación):** titular
    Cormorant Garamond 300 y subtítulo DM Sans 400 con opacidad 0,82, que es lo compuesto y medido en r4-r5; aplica solo el
    principio «lo compuesto y medido manda».
14. **La lista vetada frente al veredicto de r7.** La lista del 2026-11-04 vetaba `magnifying glass`, `stamp` y `newspaper
    headline`; el veredicto de r7 (8/10) pide lupa, sello y pluma como utensilios del bodegón y una publicación propia con
    cabecera, y el pedido de r7 ya decía «stamp». Una lista que los prompts van a incumplir no sirve. **Resuelta [P]
    (2026-11-11, pendiente de la persona):** las tres salen de la lista y el veto queda como criterio en Motivos No (sello
    con palabra legible, lupa sobre un titular); entran las que piden letras o pasan por el logo (`words`, `headline`,
    `masthead`, `emblem`, `wordmark`) y `gold(en)`, que amarillea el ámbar.

## Cambios que pediría a la plantilla

Los tres de Workflow ya están aplicados y a toVeriAI le vienen bien (semáforo del IMI en «Acentos en imagen», la tarjeta
compartible en «Otras piezas», los canales con «consta / no consta»). Dos cosas más, pequeñas:

1. **«Otras piezas de marca que hace otro sistema» supone un sistema del taller.** El ejemplo y el porqué hablan de `gimg` y
   `gw-media-content`; aquí el otro sistema es **la propia aplicación del proyecto**, que genera piezas en tiempo de ejecución
   para el usuario final. **Pediría:** que el «Qué es» diga «qué sistema (incluida la propia app del proyecto, si genera
   imágenes)», para que el agente que lee un repo busque también `html-to-image`, `canvas` o equivalentes y no solo skills.
2. **Comprobación 5 y SVG con `<use>`.** El símbolo `a` dibuja una mitad y la refleja con `<use href="#…">` y un `id` con
   prefijo del proyecto; la comprobación 5 lista etiquetas prohibidas (`<text>`, `<image>`, `filter`) pero no dice si `<use>` e
   `id` valen cuando el SVG se incrusta en una plantilla junto a otros SVG (colisión de `id`). **Pediría:** que la comprobación
   admita `<use>` interno y exija `id` con prefijo `<proyecto>-`, o que lo prohíba; hoy el agente decide solo.

Lo demás encaja: toVeriAI es el caso para el que la plantilla trae más ejemplos y casi todos salieron literales.

---

## Lo que enseñó rellenarla

**Balance de este proyecto:** 18 obligatorios (familia propia); **17 completos desde un repo** (`VeriNews_AI` o este), **1 [P]**
(el dibujo del símbolo SVG, que la persona aprueba según el plan; su concepto, fiel al favicon con los hex del kit, es decisión
delegada). De los 66 campos de la plantilla, 10 son **[P]** en todo o en parte (dibujo del símbolo, lockup oscuro, variante `b`
para ≤ 32 px, «VeriNews» como prohibido, `header` 1500×500 como destino, `compose`, `icon`, `draft`, portada del Portal como
marca, formato del `og:image` final) y 2 son «no hay» admitidos (Hereda de, Palancas extra). De los recomendados, 4 «no hay» o
no comprobables (composición por perfil, copia de logos, fuentes instaladas en el sistema, lockup oscuro), como en los otros dos
casos.

**Diferencia con image-generator y Workflow:** es la primera hoja en que **la identidad visual entera sale del repo del
proyecto**, no de este ni del Portal: los hex, las fuentes (auto-alojadas), el wordmark, el tono, el lema, las nueve frases de
r4-r5 y los cuatro canales de redes son literales de `VeriNews_AI`. Lo que este repo aporta es el símbolo en SVG (el repo solo
tiene PNG), el motivo generado y las medidas. A cambio, es el repo con más contradicciones internas (trece, frente a cinco de
Workflow): un kit que dice sacar los valores «literales del código» y difiere en el hero y el `favicon.svg`, un `marketing.html`
con otros rangos y otros colores, PNG huérfanos con otro nombre, y una tarjeta compartible que ya hace piezas de marca sobre
blanco puro. La hoja sirve aquí menos para rellenar huecos que para **elegir qué fuente manda cuando el repo se contradice**:
el código que ve el usuario, luego el kit, y la biblia detrás.
