# Lectura 2026-10-26: generador de Tarkor y marcas de los proyectos

Resúmenes de dos subagentes `Explore` (solo lectura) para preparar F2 con piloto de contenido corporativo. Lo marcado
«sin confirmar» no se ha comprobado.

Fuentes, al día con su `main`:

- Tarkor: `WMF-imagenes`, rama `claude/plan-imagenes`, HEAD `f81345cb`, que contiene todo `origin/main` (78 commits sin
  subir a su rama remota).
- Marcas: copias de `origin/main` en la carpeta temporal de la sesión: Portal-Galivelop `aa76b34`, VeriNews_AI
  (toVeriAI) `19db489` y Galivelop-workflow `56212e8`. Las copias locales de los tres estaban atrasadas.
- Tarkor no tiene marca corporativa: **se crea desde cero** (decisión de la persona). En el resto se parte de lo que ya
  hay en cada repo.
- Cada estilo se adapta a la modalidad, la ética y la temática de su proyecto (persona, 2026-10-26).

## 1. Generador de Tarkor hoy

`plan-imagenes-tarkor/` es una copia antigua y está superada: lo vigente está en
`WMF-imagenes/docs/producto/plan-imagenes/` (`plan-fotorreal.md` IMG-16…IMG-23, `banco/resultados.md`).

### Cadena

- `image-generator/scripts/generar.sh <dir> <nombre> <prompt.txt> <ancho> <alto> [semilla] [pasos] [args]`, lo envuelve
  `probar.sh`; la interfaz es `interfaz/servidor.py` (stdlib, puerto 7861).
- El motor es `sd-cli` de stable-diffusion.cpp `master-1000-95ff762` (Vulkan), con `LD_LIBRARY_PATH=bin` porque las
  librerías de Ollama le quitan la GPU.
- **Perfil rápido:** FLUX.2 klein 4B Q8_0, LLM Qwen3-4B Q4_K_M, VAE small decoder; cfg 1, euler, 6 pasos,
  `--flash-attn off,diffusion=on --vae-tiling --params-backend disk --max-vram vulkan0=2`. Tiempos: banner 1280×512 en
  110-150 s (200-275 s con `-r`); 768×768 en ~100 s.
- **Perfil de calidad, el que avanza:** FLUX.3 Image Klein Q8_0 (5,6 B, 16 pasos, guía 1), Qwen3VL-4B Q4_K_M y VAE
  flux2 completo.
  - Va con `--backend diffusion=cpu -t 8`, porque con un tope de 2 GB de GPU no arranca; el VAE va en GPU.
  - Un banner 1280×512 tarda ~49 min (~180 s/paso). Mínimo de memoria libre medido: 4,4-6 GB. Tope de 10800 s.
  - La licencia de FLUX.3 está sin confirmar; klein 4B, Z-Image y los VAE son Apache 2.0.
- **Referencias e img2img:**
  - `-r` con klein arregla la proporción (+80 % de tiempo). Con FLUX.3 cuesta ×9 y vira a azul; dos `-r` no caben.
  - img2img `-i`: con FLUX.3 hace falta `--extra-sample-args strength_as_noise_level=true`; si no, cualquier fuerza es
    casi ruido total.
- **Protecciones:**
  - Antes de arrancar pide ≥7000 MB libres; en pruebas se bajó a 5000.
  - Un vigilante mata el proceso a <1500 MB, y se aborta si el log dice «reported free 0.00 MB».
  - Ollama tiene que estar vacío.
  - Con `sd-cli` en marcha no se pueden pasar el check ni los tests.
- **Borrador:** 640×256 a 8 pasos (~9 min) anticipa la composición del definitivo, y `--preview proj` es legible desde
  el paso 2, lo que permite abortar a tiempo.
- **Descartado en la Deck:** LoRA, IC-Light, regional prompting, ADetailer, reescritura por LLM, hires fix (y
  Real-ESRGAN solo sirve para llegar al tamaño, no da calidad).

### Prompts

- `scripts/prompt_ficha.py` es determinista, sin LLM y **sin prompt negativo** (FLUX con cfg 1 lo ignora).
- **Separación dominio/técnica:** `estilo/mundo.json` guarda lo común (preámbulo, estilos por perfil, encuadres,
  vetadas) y `fichas/<tipo>/<slug>.json` un elemento cada una.
- **Reglas** (`plantilla-prompt.md`):
  - Bloques en orden fijo, frases completas en positivo y sin nombres propios inventados.
  - Palabras vetadas, porque el modelo pinta lo nombrado aunque se niegue.
  - Lo que va primero manda: el párrafo final de estilo apenas pesa.
  - Perfil `fotorreal`, tope de 520 palabras y final «Style: … Mood: …» (recomendación de BFL).

### Composición y posproceso (ffmpeg + rsvg-convert + Python stdlib; no hay ImageMagick)

- **Planos** (`banco/planos.sh`):
  - La plancha (fondo sin sujeto) va por un lado y el sujeto por otro, sobre verde croma, guiado por un boceto SVG con
    `--init-img` a fuerza 0,97.
  - `montar.sh` recorta, monta héroe y manada, y añade sombra, gradación, viñeta y grano.
  - Para armonizar gana `-i` a 0,5 (72 s).
- **Recorte por dominancia del verde** (IMG-19c): FLUX.3 pinta el croma apagado y en degradado, así que es fondo el
  píxel cuyo verde supera al rojo y al azul en más de 12.
- **Gradación:** `scripts/gradar.sh` con `estilo/gradacion.json` horneado a LUT 3D `.cube` (~0,3 s).
- **Medida objetiva:** `scripts/medir.sh` (signalstats, EMD de croma con `emd.py`, rejilla frente a referencias).
  Aceptación: mediana EMD Cb ≲6, Cr ≲7,5, YAVG 70-95, SATAVG 15-30.
- **Revisión:**
  - Banco de rondas `.tsv` con semilla fija, una palanca a la vez; `recorte.sh` compara detalle al 100 %.
  - El veredicto final es «sí/no a ojo» de la persona.
  - Sigue sin cola, sin deshacer y sin cfg/modelo en el registro (lo que F1 ya resuelve aquí).

### Reutilizable para contenido corporativo

- **Sirve tal cual o casi:**
  - Las protecciones de `generar.sh`, los dos perfiles con sus tiempos y `strength_as_noise_level`.
  - Prompts en frases sin LLM ni negativo, y la separación estilo/encuadre en JSON.
  - Borrador más preview antes del definitivo.
  - Planos con sujeto sobre verde y `montar.sh`.
  - El boceto SVG como guía de composición, que sirve para reservar zonas libres para texto o logo.
  - `gradar.sh` + LUT + `medir.sh`, convertibles en LUT de marca y medida frente a referencias de marca.
  - El banco de rondas.
- **Específico de Tarkor:** `mundo.json`, las fichas, el lore, las anclas de animales, los bocetos de animales, la LUT
  calibrada con banners y la interfaz atada a la enciclopedia.
- **Texto y logos:** FLUX no da texto legible (los prompts piden «completely textless»). Los logos tienen que ser SVG y
  el texto se compone encima con SVG o ffmpeg; esto último está **sin confirmar en WMF**.

## 2. Marcas

Portal = marca paraguas Galivelop: presenta Tarkor, toVeriAI y Galivelop-workflow, cada uno con un color de acento
(`src/data/proyectos/*.json`): Tarkor `#E0703A`, toVeriAI `#2F7A55`, workflow `#3D6FD9`. No hay un sistema de diseño
común.

### Portal Galivelop

- **Qué es:** «Taller independiente de software. Hacemos reales los proyectos que parecen imposibles.» Gali(cia) +
  Develop; se publica en ES, GL y EN.
- **Tono:**
  - «No es un escaparate. No nos mueve el beneficio económico»: enseña cada proyecto con sus avances y sus pendientes.
  - Es cercano, humilde y honesto con el estado real.
  - Líneas de trabajo: IA local y responsable, mundos que viven solos, información verificable, del prototipo al
    producto, método con IA.
- **Límites:**
  - Nada de imágenes de «contrata nuestros servicios», venta ni promesas infladas.
  - En la web no se dice «encargo» ni «de pago» (`GLOSSARY.md`, `docs/adr/0001-encargos-por-miembro.md`).
- **Identidad visual:**
  - Logo `public/marca/gv-logo.svg`: cuadrado con radio 30, degradado `#2BB3EA → #0083C1` y monograma G+V en trazo
    blanco.
  - El wordmark es HTML (Sora 700, con «Gali» en celeste).
  - Paleta: la bandera gallega, celeste `#1aa6df`, `#0083c1` y blanco.
    - Oscuro por defecto: fondo `#06121c`, superficie `#0c1d2b` y `#11283a`, borde `#1b3447`, texto `#eaf4fa` y
      `#9fb4c4`, enlace `#5cc8f2`.
    - Claro: fondo `#f6fafd`, texto `#0a1a28`, enlace `#006c9f`.
  - Tipografías: Sora (títulos 700) e Inter.
  - Fondos con resplandor radial celeste y rejilla de puntos; radios de 18 y 10 px.
- **Imágenes que ya hay:**
  - `galivelop-social.png` y `galivelop-portal.jpg` (1200×630, la segunda es el og:image) y `gv-logo-512.png`.
  - Arte de Tarkor: unas 304 `.webp` en `public/proyectos/tarkor/arte/` y `portada.webp` a 1600×640.
  - Capturas de toVeriAI y 7 diagramas del workflow a 1600×900.
- **Huecos:**
  - No hay wordmark exportado, ni logo para fondo claro, ni avatar o cabecera de Discord.
  - Tampoco hay banners por sección ni og:image por proyecto.
- **Redes:** Discord, LinkedIn y GitHub; no hay Instagram, X ni YouTube de empresa.

### toVeriAI (repo VeriNews_AI)

- **Qué es:** analiza noticias (texto, URL, imagen) y devuelve el IMI 0-100 por 7 o 9 dimensiones. Está en
  https://www.toveriai.com, con un modelo propio local (VeriAI, Ollama).
- **Lema y voz:**
  - Lema: «La verdad no es binaria».
  - Voz: «Sereno, editorial, nada sensacionalista»; «matices, no veredictos absolutos».
  - Frases: «Mide antes de creer.» y «Analiza. Compara. Decide tú.»
- **Ya tiene kit visual para IA generativa, con prompts para redes y banners:**
  `VeriNews_AI/Documentacion/v1.1/kit-visual-ia.html`. **Se parte de él.**
- **Prohibido en imágenes:**
  - Alarmismo, iconos de «stop»/prohibido, lupas sobre prensa amarilla, rojo puro de error y etiquetas «fake news».
  - `#000`, blanco puro de fondo, azules corporativos, degradados brillantes y neón.
- **Identidad visual:**
  - Wordmark «to·Veri·AI» en Cormorant Garamond 400 (nunca bold, tracking 0.08em), con «Veri» en `#2D6A4F`.
  - Símbolo: una V de trazos curvos en verde `#2D6A4F` y ámbar `#B5832A` con una constelación encima
    (`frontend/public/favicon.png`, 512×512; `logo.png` y `logo-vertical.png`).
  - Paleta «papel cálido»: `#F7F5F2`, `#FDFCFB`, `#F0EDE8`, texto `#1A1A1A`; el hero es un degradado
    `#1c3028 → #2D6A4F`.
    - Verdes `#52B788`, `#74C69D`, `#B7E4C7`; ámbar `#B5832A`; granate `#9B2335`.
    - Semáforo IMI: granate, ámbar y verde.
  - Tipografías: Cormorant Garamond y DM Sans.
  - Iconos de línea fina (~1.3 px), sin relleno; nada de 3D. Estética de papel y tinta, mucho aire; solo modo claro.
- **Huecos:** no hay og:image 1200×630 (apunta al favicon de 512), ni manifest, ni apple-touch-icon.
- **Redes objetivo** del kit: Instagram, LinkedIn y X. No hay cuentas enlazadas.

### Galivelop-workflow

- **Qué es:** el flujo de trabajo con agentes de IA (plugin, v0.4.1, MIT).
- **Lema:** «Lo que no está subido no existe».
- **Tono:** técnico, sobrio y pragmático, con reconocimiento de fuentes (`CREDITS.md`).
- **Límites:** las imágenes no deben sugerir autonomía total de la IA ni «magia»: el humano decide y revisa.
- **Identidad visual:**
  - **El repo no tiene ninguna** (ni logo, ni icono, ni CSS).
  - La única está en el Portal: acento `#3D6FD9` y diagramas oscuros en `Portal-Galivelop/docs/diagramas/gw-*.svg`.
  - Paleta de los diagramas: fondo `#0d1b2a`, texto `#eef6fb` y `#8a9bb0`, acentos `#38b6e8`, `#f2b34a` y `#4cc38a`;
    fuente Inter.
- **Huecos:** logo, avatar, og:image y social preview de GitHub.

### Tarkor

- **Qué es:** un juego de rol con IA local, de fantasía, con arte propio y acento naranja `#E0703A` en el Portal.
- **Marca:** no hay marca corporativa; **se crea desde cero**, coherente con el arte del juego.

## 3. Herramientas del taller (añadidas por la persona el 2026-10-26)

Leídas en su árbol de trabajo, que contiene todo `origin/main`: galivelop-image-generator (`f2-motor`),
galivelop-voice-generator (`claude/voces-f1`, 15 commits sobre `main`) y galivelop-developer (`claude/f1-instalacion`, 3 sobre
`main`).

**Lo común a las tres:**

- No tienen ningún svg, png, webp, ico ni jpg, ni logo, colores o tipografías propias.
- Son CLI y servicios locales sin interfaz todavía, y ninguna está en el Portal ni prevé estarlo.
- Las tres usan Galivelop-workflow y tienen a Tarkor/WMF como primer consumidor.
- Comparten principios: IA local, solo stdlib, nada residente (arranque bajo demanda en `127.0.0.1`) y la Steam Deck como
  máquina de referencia.

### galivelop-image-generator

- **Qué es:** «Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos».
- **Límites:** no conoce el dominio (D2) y es reproducible (D13, D34).
- **Metáfora**, sacada de su texto: la cola que genera de uno en uno, los intentos con una elegida y deshacer (D9) y un
  taller que se enciende solo cuando se le pide (D11).

### galivelop-voice-generator

- **Qué es:** «Generador de voces con IA local para desarrollo», con motor qwentts.cpp. Es gemelo del de imágenes y genera
  paquetes de voces para el juego.
- **Límites:** las voces son personas sintéticas definidas por una referencia elegida. No hay texto sobre consentimiento ni
  clonación, así que en imagen no se sugiere clonar a nadie (nada de rostros ni personas reales).
- **Metáfora:** la onda, las tomas como intentos y la huella de la voz (`GLOSSARY.md`).

### galivelop-developer

- **Qué es:** «Agente de programación local: Aider sobre un modelo local, como tercer relevo junto a las sesiones de Claude
  Code».
- **Límites:**
  - Trabaja solo en `local/<tarea>` y nunca toca la bitácora, `main` ni `.claude/`.
  - Sus límites los imponen scripts.
  - Lo revisa Claude o la persona antes del merge: el humano decide.
- **Metáfora:** el tercer relevo y una rama local acotada que vuelve al tronco tras la revisión (`docs/adr/0002-tercer-relevo.md`).

## 4. Ampliación para la biblia de estilo y los logos (2026-10-26, tarde)

Dos subagentes `Explore` más, sobre `origin/main` recién traído: VeriNews_AI `02ac654`, Portal-Galivelop `aa76b34`,
Galivelop-workflow `56212e8`, World-Maker-Fantasy `73965f62`. Lo que ya está arriba no se repite.

### El molde: `VeriNews_AI/Documentacion/v1.1/kit-visual-ia.html`

17 secciones en 4 grupos, todas con valores literales sacados del código (hex, px, radios) y el porqué de cada regla:

- **Identidad de marca:**
  1. Paleta: base, acento con tonos, neutros, combinaciones por contexto, sombras, reglas y qué evitar.
  2. Tipografía: pareja, pesos, escala por token y tracking.
  3. Logotipo: wordmark claro y oscuro, margen libre, tamaño mínimo, símbolo y cómo conviven los dos.
  4. Iconografía y forma: grosor de línea, radios y lenguaje de forma.
- **Voz y sistema:**
  5. Tono: qué evitar y el campo semántico.
  6. Color semántico (el IMI).
  7. Frases reutilizables: lema, variaciones, ganchos y cierres.
- **Prompts de generación (12):**
  8. Redes.
  9. Banners.
  10. Iconografía conceptual.
  11. Mockups.
  12. Miniaturas.
  13. Abstracto.

  Cada prompt lleva formato en px, fondo en hex, tipografía, posición de cada cosa, posición del logo, mood y lista negativa.
- **Prompts por plataforma:**
  14. Instagram.
  15. LinkedIn.
  16. X.
- **Uso:**
  17. Copiar y pegar, qué reforzar si falla el tono, adjuntar capturas reales y «el código manda» (si cambia la marca,
    primero el código y luego el kit).

Formatos del kit:

| Red | Formato y medida |
|---|---|
| Instagram | Feed 1080×1080 o 1080×1350; Reel 1080×1920 con el tercio inferior libre |
| LinkedIn | 1200×1200 o 1200×628; vídeo 1280×720 |
| X | 1200×675 |
| Otros | Banners 1920×640 y 1600×600 |

### toVeriAI: lo que añade el kit

- **Paleta:**
  - Fondo y tinta: borde `#E8E4DF`, línea `#D8D4CF`, gris `#999999`, borde oscuro `#2A2A2A`.
  - Verdes: pálido `#E8F4EE`.
  - Reglas: pieza oscura `#1A1A1A` con texto blanco; en piezas genéricas el único acento es `#2D6A4F`.
  - Rangos IMI del kit: 0-39, 40-69 y 70-100. `marketing.html` dice 0-49, 50-74 y 75-100: **incoherencia del repo**.
- **Tipografía:**
  - Cormorant Garamond 300 en titulares y cifras, 400 en el wordmark; DM Sans 400 y 500. Nunca bold.
  - Eyebrows con tracking 0,28-0,32 em.
- **Logo:**
  - Margen libre: la altura de la «V». Altura mínima del wordmark: ~18 px; por debajo, el símbolo.
  - El símbolo va con el wordmark (lockup) o solo en una esquina, nunca suelto en el centro.
  - Relleno plano, sin degradados ni 3D. Motivo de apoyo: el anillo de score.
- **El símbolo real** (`frontend/src/assets/logo.png` 2190×1980, `logo-vertical.png` 2230×750 —en realidad horizontal—,
  `frontend/public/favicon.png` 512×512), simétrico:
  - Dos barras anchas y planas de «V» en verde salvia (~`#5F7C6B`), con las puntas de arriba cortadas en diagonal, que se
    unen abajo en una punta.
  - Dentro, 4 hojas curvas afiladas en dorado (~`#B08D57`), dos por lado; la exterior es más larga. Nacen juntas abajo y se
    abren en abanico por encima de las barras.
  - Encima, 12 puntos: 3 dorados grandes en triángulo, 1 dorado mediano en el centro y 8 verdes pequeños en filas de 2, 2,
    2 y 1.
- **Discrepancias del repo:**
  - El wordmark de los PNG es «VeriNews» («Veri» gris `#4A4A4A`, «News» verde); el del kit, «to·Veri·AI» con «Veri» en
    verde.
  - Los colores del PNG no son exactamente los hex del kit.
  - `favicon.svg` (morado) es un archivo huérfano.
- **Prohibido en imagen**, además de lo de arriba: stock photos, sellos FAKE, tijeras, escudos con tick, flechas rojas,
  emojis, clickbait, glassmorphism y estética tech azul.

### Galivelop-workflow: `skills/gw-media-content/`

- Propone hasta 10 posts por proyecto, de 16 tipos, y no publica nunca.
- `reglas.json` fija los límites por red (X 280 caracteres, URL 23...) y `nota.md` admite una `Palette` por proyecto.
- Renderiza HTML con Playwright a WebP.
- No dice nada de logos ni de cómo hacer una biblia; sirve para formatos y medidas.

### Tarkor (WMF): identidad de partida

- **Marca:** no hay logo ni emblema. `frontend/public/favicon.svg` es el rayo violeta de Vite.
  - El título sale como texto pequeño en mayúsculas con tracking amplio, filetes `accent-hairline` y un rombo `.gem` encima
    (`frontend/src/pages/Home.tsx:28`). Es lo más parecido a un lockup que tiene.
- **Mundo:**
  - El mundo se llama Helek Sirik («Origen Azul») y se juega en el continente Berig.
  - «Tarkor» es también la última y más sabia de las 13 Semillas de Madre, que se fue y volvió «frío y oscuro», y de ella
    nace la magia salvaje (`docs/rpgtarkor/lore-mundo/genesis.md`).
  - **Reservado, no se muestra ni se resuelve:** qué sabe Tarkor, la Entidad, la luz morada, el Reino Nabierus, la Ciudad
    Hundida, el Archivo Cegado y el muro de obsidiana.
  - El símbolo puede insinuar la ambigüedad (fidelidad y ruptura), sin presentar a Tarkor como villano ni como héroe.
- **Tono:**
  - Épico y trágico, con letalidad media.
  - Fantasía con causa física visible; mundo a medio vaciar, artesanal (madera de Telda, piel, hueso, piedra, hierro
    negro).
  - Sin humanos ni pólvora. **Sin luna**: el cielo tiene un cinturón de polvo de cristal perlado.
  - Ética: privado por diseño (sin cuentas ni telemetría), «el motor decide, la IA narra» y la Steam Deck como objetivo.
  - Voz de difusión: cercana, concreta y honesta, sin vender (`docs/difusion/guia-canales.md`).
- **Motivos con potencial de símbolo:** cristal azul y cinturón perlado, rombo-gema con filetes, Pilares Rotos con puentes
  (la portada del Portal), Agujas Imán, crestas de arena imán, tótems orcos, empalizada de troncos, obelisco goirnte,
  remaches y hierro negro.
- **Vetos:** luna, humanos, pólvora, Vaelira, todo lo reservado, texto, y las palabras moon, crystal dust, heavens, scar,
  wound y gash.
- **Interfaz** (`frontend/src/index.css`): identidad «madera + hierro» con el cristal como acento (`docs/producto/02-decisiones.md`
  nº 6).
  - Madera: 950 `#1b130c`, 900 `#241a10`, 800 `#332415`, 700 `#46311d`, 600 `#5c4126`, 500 `#7a5934`, 400 `#a3814f`,
    300 `#c9a877`, 200 `#e3cba8`, 100 `#f1e4d0`.
  - Hierro: `#0e0b08`, `#171310`, `#221c16`.
  - Cristal: 300 `#a8d8f0`, 400 `#7bc4e8`, 500 `#4aa8d8`, 600 `#3488b8`.
  - Acero: `#b0bec8`, `#8a9aa8`, `#6b7d8c`, `#52626f`. Musgo: `#8fae6a`.
  - Tipografías: Cinzel en títulos (OFL, empaquetada en `frontend/src/assets/fonts/`), Inter en texto y Cascadia Code en
    datos.
  - **El acento del juego (cristal `#4aa8d8`) no coincide con el del Portal (`#E0703A`).**
- **Lema público:** «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas.» Creador: Álvaro García Graña.

### Portal: lo que añade

- `public/marca/gv-logo.svg` (128×128):
  - Fondo `rect rx=30` con `linearGradient` diagonal de `#2BB3EA` a `#0083C1`.
  - Trazo blanco de 12, con remates y uniones redondeados.
  - G: `M55.4 45.6 A24 24 0 1 0 64 64` y `M50 64 H80`. V: `M71 40 L89.5 88 L108 40`.
  - `Logo.tsx`: icono + «Gali**velop**» en Sora 700, tracking -0,03 em, «Gali» en celeste.
- Tema oscuro: alterno `#081826` y texto-3 `#6f8799`. Claro: superficie `#fff`, borde `#d6e4ee` y texto-2 `#43586a`.
- Títulos con tracking -0,02 em. Gali(cia) + Develop; gl obligatorio en cada texto.
