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
