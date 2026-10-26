# toVeriAI — biblia de estilo

Fuente de verdad: repo `VeriNews_AI`, commit `02ac654`, sobre todo su kit visual v1.1 (rutas en la sección 10). Sin marca,
el dato sale del repo; **[P]** es propuesta pendiente de la persona; *(suposición)* se comprueba en una ronda.

**Incoherencias del repo, pendientes de decidir [P]:**

1. **Wordmark:** el kit dice «toVeriAI» (tres segmentos `to` + `Veri` + `AI`, sin puntos medios); los PNG del frontend
   (`logo.png`, `logo-vertical.png`) dicen «VeriNews» con «Veri» gris `#4A4A4A`. Aquí manda el kit: «toVeriAI».
2. **Rangos del IMI:** el kit dice 0-39 / 40-69 / 70-100; `marketing.html` dice 0-49 / 50-74 / 75-100.
3. **Colores del símbolo:** el `favicon.png` usa un verde salvia (~`#6B8176` medido) y un dorado (~`#AD8E5C`), no los hex del
   kit; las propuestas usan los del kit (`#2D6A4F`, `#B5832A`).
4. `favicon.svg` (morado) es un archivo huérfano; se ignora.

## 1. Esencia

- **Qué es:** analiza noticias (texto, URL, imagen) y devuelve el IMI 0-100 por 7 o 9 dimensiones, con un modelo propio
  local (VeriAI, Ollama). https://www.toveriai.com.
- **Lema:** «La verdad no es binaria».
- **Para quién:** quien lee noticias y quiere medir antes de creer; redes objetivo del kit: Instagram, LinkedIn y X.
- **Valores:** sereno, editorial, nada sensacionalista; «matices, no veredictos absolutos»; la desinformación se cuenta con
  claridad, matiz y capas de lectura.
- **Nunca se muestra:** alarmismo, iconos de stop o prohibido, lupas sobre prensa amarilla, rojo puro de error, etiquetas
  «fake news», sellos FAKE, tijeras, escudos con tick, flechas rojas, emojis, clickbait, stock photos.

## 2. Paleta

| Rol | Hex | Uso |
|---|---|---|
| Papel | `#F7F5F2` | fondo |
| Tarjeta | `#FDFCFB`, `#F0EDE8` | superficies |
| Borde y línea | `#E8E4DF`, `#D8D4CF` | filetes |
| Texto | `#1A1A1A`; gris `#999999`; borde oscuro `#2A2A2A` | texto y pieza oscura |
| Verde de marca | `#2D6A4F` | «Veri», único acento en piezas genéricas, símbolo |
| Verdes de apoyo | `#52B788`, `#74C69D`, `#B7E4C7`, pálido `#E8F4EE` | IMI alto, fondos tenues |
| Ámbar | `#B5832A` | IMI medio; hojas del símbolo |
| Granate | `#9B2335` | IMI bajo |
| Hero | `#1c3028 → #2D6A4F` | solo el hero de la web |

Combinaciones:

- **Pieza clara (la de la marca):** papel `#F7F5F2` o tarjeta `#FDFCFB`, texto `#1A1A1A`, un solo acento `#2D6A4F`.
- **Pieza oscura:** fondo `#1A1A1A` con texto blanco; «Veri» sigue en verde. Solo cuando la pieza lo pide; la web es solo
  modo claro.
- **Sobre imagen:** sobre papel o acuarela, en la zona reservada; texto `#1A1A1A`.
- **Semáforo IMI:** granate, ámbar y verde solo cuando la pieza habla de un nivel de credibilidad (rangos: ver incoherencia 2).

Prohibidos: `#000`, blanco puro de fondo, azules corporativos, degradados brillantes, neón, glassmorphism, estética tech
azul; degradados en el símbolo.

## 3. Tipografía

| Uso | Familia | Peso | Tracking |
|---|---|---|---|
| Titulares y cifras | Cormorant Garamond | 300 | normal |
| Wordmark «to**Veri**AI» | Cormorant Garamond | 400 (nunca bold) | 0,08 em |
| Eyebrows (mayúsculas) | DM Sans | 400-500 | 0,28-0,32 em |
| Cuerpo | DM Sans | 400-500 | normal |

Nunca negritas. El wordmark cambia solo el color de `to`/`AI` (negro sobre claro, blanco sobre oscuro); «Veri» siempre verde.

## 4. Logo

El símbolo real existe solo como PNG (`frontend/public/favicon.png` 512×512): V de dos barras planas, cuatro hojas doradas en
abanico y once puntos (3 dorados grandes en triángulo, 1 dorado mediano, 7 verdes en filas de 2, 2, 2 y 1; la lectura
contó 12). Falta el SVG: de aquí sale.

Propuestas (`logos/toveriai-<letra>.svg` y `-lockup.svg`), conceptos distintos:

- **a. Vectorización fiel** del favicon, medida sobre el PNG, con los hex del kit en plano; a 16 px es una V con una mancha
  dorada, como el favicon de hoy.
- **b. Simplificado:** V de dos trazos curvos (verde y ámbar) con tres puntos dorados; se lee a 16 px (los puntos quedan
  como un acento).
- **c. La verdad no es binaria:** V de tinta plana en tres estratos (granate, ámbar, verde) que se rozan sin mezclarse,
  con un hilo de papel entre ellos; a 16 px es una V oscura con bandas.
- **d. Anillo de score:** arco abierto del IMI (trazo 5/128, más grueso que la línea ~1,3 px del kit, que a 16 px no
  existiría) con una V de dos hojas dentro; a 16 px queda la V y el anillo se insinúa.

Tras elegir **[P]**:

- Variantes: clara (la de la marca) y oscura (sobre `#1A1A1A`, mismos colores de símbolo; si el verde no contrasta, el
  símbolo va sobre una tarjeta `#FDFCFB` de radio 6).
- Margen libre: la altura de la «V» del wordmark. Altura mínima del wordmark ~18 px; por debajo, solo el símbolo (16 px).
- Símbolo y wordmark: siempre juntos en lockup (símbolo a la izquierda) o el símbolo solo en una esquina; nunca el símbolo
  suelto en el centro ni el wordmark solo si el símbolo iba a aparecer.
- Prohibido: degradados, 3D, otro símbolo inventado (para ilustrar un concepto se usa el anillo de score), bold, «VeriNews».

## 5. Forma e iconografía

- Radios: 3 px (pequeño), 4 px (tarjetas y botones, el más frecuente), 6 px (contenedores); píldora solo en badges.
- Iconos de línea fina (~1,3 px a escala de icono pequeño), sin relleno, remates redondeados, un solo color heredado del
  texto; nada de 3D ni iconos flat genéricos.
- Lenguaje: papel y tinta, tiras y estratos, línea fina, mucho aire, sombras cálidas y suaves. Motivo de apoyo: el anillo de
  score.

## 6. Voz y frases

- **Tono:** sereno, editorial, contenido; pregunta antes que sentencia.
- **Campo semántico:** medir, matiz, espectro, credibilidad, capas de lectura, dudar bien, índice.
- **Lema:** «La verdad no es binaria».
- **Variaciones (kit):** «Entre lo cierto y lo falso hay todo un espectro. Nosotros lo medimos.» · «Menos veredictos. Más
  matices.» · «La credibilidad no se decreta: se mide.» · «No te decimos qué creer. Te damos con qué pensar.» · «Dudar bien
  también es informarse.»
- **Ganchos (kit):** «Esta noticia sacó un 34 sobre 100. ¿Habrías dudado tú?» · «¿Y si no es falsa… pero tampoco es del todo
  verdad?» · «Esta noticia no es falsa. Tampoco del todo verdad.» · «Léela dos veces. O pásala por aquí primero.»
- **Cierres (kit):** «Analiza. Compara. Decide tú. — toVeriAI» · «Mide antes de creer. toVeriAI.» · «Pon a prueba tu próximo
  titular. Gratis, en toVeriAI.»

## 7. Estilo de imagen (FLUX)

- **Sí:** papel cálido con textura sutil; tintas de acuarela (granate, ámbar, verde) que se rozan sin mezclarse; tiras y
  estratos de papel; línea fina sin relleno; mucho aire; luz plana y acabado de impresión; solo modo claro.
- **No:** alarmismo, lupas, sellos, tijeras, escudos, flechas rojas, prensa amarilla, pantallas azules, neón, 3D,
  glassmorphism, negro `#000`, blanco puro, personas de stock.
- **Motivos:** entre dos tintas, el espectro, cita tipográfica sobre papel, doble página de periódico vista cenital, anillo
  de score.
- **Palabras vetadas:** fake, stop, magnifying glass, stamp, scissors, shield, red arrow, newspaper headline, text, logo,
  letters, pink, magenta (el vino tira a magenta: r1), y cualquier «like …».
- **Zona reservada:** el tercio superior «calm, bare paper» (og, wide) o la mitad superior (square) para wordmark y frase.

## 8. Prompts

| Archivo | Pieza | Estado |
|---|---|---|
| `examples/toveriai/prompts/og.txt` | og 1200×630, «Entre dos tintas» | r1 (`5d0178c`): **sí** por la persona. Palanca r2: nombrar el vino con más peso («deep burgundy», «oxblood») y quitar lo que lo acerque al rosa |

Los 20 prompts del kit (redes, banners, iconografía, mockups, miniaturas, abstracto; por plataforma) se adaptan quitando el
texto y describiendo la zona reservada. Plantilla: `<formato> abstract conceptual artwork on warm beige textured paper.
<motivo en positivo, con los colores en palabras>. The <zona reservada> is calm, bare beige paper with a soft natural grain.
Flat even light and a printed fine art finish. Style: editorial watercolour on paper, delicate and contemplative, soft
muted colours. Colours: warm beige paper, deep burgundy, forest green, amber. Mood: serene, thoughtful, balanced. The image
is completely textless.`

## 9. Formatos y piezas

Perfiles (tabla común del README): `og`, `square`, `portrait`, `wide`, `header`, `icon`. Del kit: Instagram 1080×1080 y
1080×1350 (Reel 1080×1920 con el tercio inferior libre), LinkedIn 1200×1200 y 1200×628, X 1200×675, banners 1920×640 y
1600×600.

Primera ronda: 1) og:image 1200×630 (hoy apunta al favicon de 512): «Entre dos tintas» + wordmark + lema; 2) `square`
«Cita tipográfica»; 3) banner «El espectro» como `header` o `banner`; 4) `wide` de gancho para X; 5) apple-touch-icon y
manifest desde el símbolo elegido (solo composición).

## 10. Fuentes

Repo `VeriNews_AI`, commit `02ac654`:

- Kit visual (paleta, tipografía, logo, forma, tono, IMI, frases, 20 prompts, formatos): `Documentacion/v1.1/kit-visual-ia.html`.
- Símbolo: `frontend/public/favicon.png` (512×512, medido aquí), `frontend/src/assets/logo.png` y `logo-vertical.png`
  (wordmark «VeriNews»); `frontend/public/favicon.svg` huérfano.
- Rangos del IMI en `marketing.html` (incoherencia 2).
- Resumen de lectura: `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`, secciones 2 y 4; plan: `docs/plan.md`,
  «Estilos por proyecto»; veredicto r1: `docs/registros/contenido/r1-fondos.md`.
