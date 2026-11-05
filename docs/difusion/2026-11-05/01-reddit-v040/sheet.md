# Sheet: reddit-v040 (2026-11-05)

The source of everything published for this piece. What is not here, with its source, does not go out in the channels.
Piece folder: `docs/difusion/2026-11-05/01-reddit-v040/`.

Languages: es, en

## Channels

- reddit

## What is told

- **In one sentence (for who uses it):** galivelop-image-generator 0.4.0 genera imágenes con IA local en tu propia máquina Linux con Vulkan (referencia: Steam Deck) y ya tiene interfaz en el navegador para pedir, probar y elegir.
- **In one sentence (technical):** un servicio por máquina en Python solo con la biblioteca estándar que envuelve `sd-cli` de stable-diffusion.cpp con FLUX.2 klein 4B, cola persistente, API HTTP local, composición y medida de marca.
- **Status:** released in version 0.4.0 (2026-11-05)

## Verified facts

| Fact | Source |
|---|---|
| Versión 0.4.0 publicada el 2026-11-05 (fase F4 Interfaz); 0.3.0 el mismo día (F1-F3) | `CHANGELOG.es.md` l.12, l.34; `README.md` l.11, l.17-23 |
| Interfaz en el navegador: tres pantallas, en español e inglés | `README.md` l.23 |
| Enlaces: release v0.4.0 (`/releases/tag/v0.4.0`), página del portal y repo Galivelop-workflow | `docs/handoff.md` fila `plan-piezas` (release v0.4.0); los otros dos, dados por la persona el 2026-11-05 |
| Plantillas de composición elegibles por perfil y por intento | `CHANGELOG.es.md` l.21-23 |
| Editor de elementos: mover y redimensionar titular, logo y adornos con puntero o teclado, chip de contraste en vivo, guardar como plantilla nueva | `CHANGELOG.es.md` l.24-27 |
| Panel de nuevo pedido (perfil, prompt, número, borrador, plantilla, modelo), pestañas Piezas y Marca, cajón de la cola con reordenar y «Vaciar cola» con confirmación | `CHANGELOG.es.md` l.28-32 |
| Licencia MIT; los modelos conservan su licencia | `CHANGELOG.es.md` l.18; `README.md` l.149-150 |
| `arrancar.sh` abre la interfaz con doble clic | `CHANGELOG.es.md` l.19 |
| Pruebas de la interfaz en un Chrome headless, sin generar imágenes | `CHANGELOG.es.md` l.20 |
| Requisitos: Python 3.10+ solo con la biblioteca estándar, sin dependencias | `README.md` l.6-7, l.91 |
| Solo Linux con Vulkan; la Steam Deck es la máquina de referencia; otros equipos en F7 | `README.md` l.139 |
| Instalación: `git clone` + `./instalar.sh`; `gimg` en `~/.local/bin`; motor (release fija de stable-diffusion.cpp con Vulkan) y modelos por defecto (~7 GB) con comprobación sha256, fuera del repo | `README.md` l.131-135 |
| `gimg doctor` dice qué falta y cómo arreglarlo; opciones `--with`, `--only-cli`, `--models-from`, `--dry-run` | `README.md` l.136-137 |
| Modelo por defecto: FLUX.2 klein 4B Q8 (Apache-2.0) con codificador Qwen3-4B y VAE | `gimg/models.json`; `docs/plan.md` l.59 |
| Banner 1280×512 a 6 pasos en la Deck: ~150 s | `docs/plan.md` l.59-60 |
| Protecciones del motor: memoria libre mínima antes de lanzar, vigilante de `MemAvailable`, matar el grupo de procesos de `sd-cli`, comportamiento ante Ollama (abortar o descargar) | `CHANGELOG.es.md` l.45-49; `docs/plan.md` l.61-62 |
| Un servicio por máquina que comparten varios proyectos; cada proyecto declara perfiles en `galivelop-images.json` | `README.md` l.5, l.47-66 |
| Pedido con clave, perfil, prompt, referencias y semilla; la elegida se entrega en la carpeta del proyecto (`uploads/images/fauna/red-howler-banner.png`) | `README.md` l.68-80 |
| Intentos con notas y estados, elegir y deshacer, cola persistente, CLI en español e inglés con `--json` | `CHANGELOG.es.md` l.38-44 |
| Borradores, img2img, composición (titular, logo, adornos), medida de marca (paleta, contraste WCAG, distancia a la referencia), hojas de contactos | `CHANGELOG.es.md` l.53-57 |
| API HTTP local en `127.0.0.1:8737`, solo local, con comprobación de Host, Origin y Content-Type; arranque bajo demanda y `gimg ui` | `CHANGELOG.es.md` l.59-62; `README.md` l.124-127 |
| El motor de pruebas (`fake`) es el de por defecto hasta que `instalar.sh` elige el real | `README.md` l.14-15 |
| Hoja de ruta: F5 piloto con proyectos reales, F6 director local opcional (Ollama), F7 compatibilidad (CPU, CUDA, ROCm, Metal, otros Linux, Windows, quizá macOS) | `README.md` l.24-26 |
| Próximos pasos: capas con piezas existentes, transparencia y «Quitar fondo», imágenes de referencia, cajas de texto antes de generar, borrar con confirmación, edición por prompt, editar texto y tipografía | `README.md` l.30-43 |
| Faltan comprobaciones manuales en la Deck | `README.md` l.12-13 |
| 252 commits del 2026-10-25 al 2026-11-05, 54 archivos de test | `figures.py --since v0.1.0` (2026-11-05) |
| Portadas con logo compuestas con gimg para cinco proyectos del taller el 2026-11-04 | `docs/handoff.md`, «Pendiente», «Tras aplicar las hojas», (c) |

## Reddit

- **Subreddit:** ninguno: publicado en el perfil de la persona, u/Alvaro-Garcia-Grana
- **Rules read:** no aplica (sin subreddit)
- **Self-promotion:** no aplica: es el perfil propio

## Images

| Image | Alt text | Channels |
|---|---|---|
| `media/portada-gimg.webp` | es: Portada oscura con paneles de cristal violeta; texto «galivelop-image-generator», «Pide, prueba, elige.» e «Imágenes con IA local: un servicio por máquina, para varios proyectos.» / en: Dark cover with purple glass panes; text in Spanish: "galivelop-image-generator", "Ask, try, choose." and "Local AI images: one service per machine, for several projects." | reddit |
| `media/portada-galivelop.webp` | es: Una puerta luminosa sobre el agua; texto «Galivelop», «Un taller, no un escaparate.» y «Hacemos reales los proyectos que parecen imposibles.» / en: A glowing doorway over water; text in Spanish: "Galivelop", "A workshop, not a shop window." and "We make real the projects that seem impossible." | reddit |
| `media/portada-tarkor-lapiz.webp` | es: Agujas de piedra y un cardo dibujados a lápiz; texto «Tarkor», «El mundo sigue aunque tú te detengas.» y «RPG narrativo de fantasía con IA local. En desarrollo, a la vista.» / en: Pencil drawing of stone spires and a thistle; text in Spanish: "Tarkor", "The world goes on even if you stop." and "Narrative fantasy RPG with local AI. In development, in the open." | reddit |
| `media/portada-tarkor-desierto.webp` | es: Un desierto con un esqueleto y un tótem; mismo texto de Tarkor / en: A desert with a skeleton and a totem; same Tarkor text in Spanish | reddit |
| `media/portada-toveriai.webp` | es: Collage en acuarela con un periódico, una regla y un compás; texto «toVeriAI», «La verdad no es binaria.» y «Entre lo cierto y lo falso hay todo un espectro. Nosotros lo medimos.» / en: Watercolour collage with a newspaper, a ruler and a compass; text in Spanish: "toVeriAI", "Truth is not binary." and "Between true and false there is a whole spectrum. We measure it." | reddit |

## Internal use

- Rama `ccr-85e9d14e-zt7p8b`; fases F0-F4 en `main` (PR #2, #3, #4).
- Las portadas son las que bajó la persona; que se hicieran con gimg sale de la bitácora: confirmarlo con la persona antes de publicar.
- Publicado por la persona el 2026-11-05 en su perfil (u/Alvaro-Garcia-Grana), no en un subreddit; `check.py` no contempla perfiles y falla en «Subreddit:» y «Rules read:».
- El repo es público (enlace en el texto: https://github.com/Zeldris/galivelop-image-generator); confirmarlo antes de publicar.

## Published

| Channel | Language | Date | Link |
|---|---|---|---|
| reddit | en | 2026-11-05 | https://www.reddit.com/user/Alvaro-Garcia-Grana/comments/1xoxbzy/i_built_a_local_ai_image_generator_for_the_steam/ |
