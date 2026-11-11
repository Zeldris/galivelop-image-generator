# Reddit: reddit-v040

The subreddit, the day its rules were read and what they say about self-promotion are in `sheet.md`. The title is
300 characters at most. Give something to the community before promoting.

## es

**Title:** He hecho un generador de imágenes con IA local para la Steam Deck (Linux + Vulkan, FLUX.2 klein): la versión 0.4.0 ya trae interfaz en el navegador

Image: media/portada-gimg.webp
Image: media/portada-galivelop.webp
Image: media/portada-tarkor-lapiz.webp
Image: media/portada-tarkor-desierto.webp
Image: media/portada-toveriai.webp

Las imágenes del post son portadas de cinco proyectos de mi taller, compuestas con la herramienta (fondo generado + titular y logo).

**Qué es**

galivelop-image-generator es un servicio que corre en tu propia máquina y genera imágenes con IA local para varios proyectos a la vez. Cada proyecto dice qué tamaños y estilos necesita, tú pides, pruebas varios intentos, eliges uno y se entrega en la carpeta del proyecto.

**Qué trae la 0.4.0 (hoy)**

- Interfaz en el navegador, en español e inglés: nuevo pedido (perfil, prompt, cuántos intentos, borrador, plantilla, modelo), revisión de intentos y la cola, que se puede reordenar o vaciar.
- Plantillas de composición elegibles por perfil y por intento.
- Editor de elementos: mueves y redimensionas titular, logo y adornos con ratón o teclado, con un indicador de contraste en vivo, y lo guardas como plantilla nueva.
- Pestañas Piezas y Marca.
- `arrancar.sh` para abrirla con doble clic.
- Licencia MIT (los modelos conservan la suya).

**Requisitos**

- Linux con Vulkan. La máquina de referencia es la Steam Deck.
- Python 3.10 o más. Nada más que instalar: solo usa la biblioteca estándar.
- Unos 7 GB de disco para el motor y los modelos por defecto.

Instalación: `git clone` y `./instalar.sh`. Deja `gimg` en `~/.local/bin` y descarga una release fija de stable-diffusion.cpp con Vulkan y los modelos, con comprobación sha256 y fuera del repo. `gimg doctor` te dice qué falta y la orden que lo arregla.

**La parte técnica**

- Motor: `sd-cli` de stable-diffusion.cpp lanzado como proceso. Modelo por defecto: FLUX.2 klein 4B Q8 (Apache-2.0) con Qwen3-4B como codificador. Un banner de 1280×512 a 6 pasos tarda unos 150 s en la Deck.
- Protecciones para no tumbar la máquina: comprueba la memoria libre antes de lanzar, vigila `MemAvailable` durante la generación, mata el grupo de procesos de `sd-cli` al cancelar y, si Ollama está ocupando memoria, aborta o lo descarga (tú eliges).
- Un servicio por máquina que comparten varios proyectos. Cada proyecto lleva un `galivelop-images.json` con sus perfiles (tamaño, pasos, cfg, muestreador, modelo).
- Un pedido lleva clave, perfil, prompt, referencias y semilla. La imagen elegida acaba en, por ejemplo, `uploads/images/fauna/red-howler-banner.png` dentro del proyecto, con manifiesto y deshacer.
- Cola persistente, intentos con notas y estados, y una CLI en español e inglés con salida `--json` para usarla desde otros programas.
- Borradores, img2img, composición (titular, logo, adornos), medida de marca (paleta, contraste WCAG, distancia a la referencia) y hojas de contactos para revisar una ronda.
- API HTTP solo en `127.0.0.1:8737`, con comprobación de Host, Origin y Content-Type. Arranca bajo demanda, y `gimg ui` abre la interfaz.
- Sin `./instalar.sh` usa un motor de pruebas que da imágenes de color liso: sirve para probar el flujo sin GPU.
- 252 commits del 25 de octubre al 5 de noviembre, con 54 archivos de test, incluidas pruebas de la interfaz en un Chrome headless.

**Lo que sigue**

Primero, las comprobaciones manuales que faltan en la Deck. Después, en la hoja de ruta:

- Composición por capas con piezas que ya tienes (fondo, logo, elementos sueltos, texto), de intentos elegidos o de PNG/SVG propios.
- Transparencia al generar y «Quitar fondo».
- Imágenes de referencia al generar.
- Cajas de texto colocadas antes de generar, que el generador tiene en cuenta.
- Borrar intentos, composiciones y plantillas, con confirmación.
- Edición por prompt: un intento nuevo a partir de otro.
- Editar el texto y la tipografía de lo ya compuesto.
- F5: piloto con proyectos reales. F6 (opcional): un LLM local con Ollama que redacte prompts y ayude a elegir. F7: más equipos (CPU, CUDA, ROCm, Metal), otros Linux, Windows y quizá macOS.

Enlaces:

- Código: https://github.com/Zeldris/galivelop-image-generator
- Notas de la 0.4.0: https://github.com/Zeldris/galivelop-image-generator/releases/tag/v0.4.0
- Página del proyecto en el portal de Galivelop: https://zeldris.github.io/Portal-Galivelop/proyectos/galivelop-image-generator
- El flujo de trabajo con agentes de IA con el que lo hago (Galivelop-workflow): https://github.com/Zeldris/Galivelop-workflow

Una pregunta para quien genere en local: ¿qué os falta más en vuestro flujo, quitar fondo, capas o imágenes de referencia? Y si tenéis una Deck u otro Linux con Vulkan y lo probáis, me vienen muy bien los tiempos que os dé.

## en

**Title:** I built a local AI image generator for the Steam Deck (Linux + Vulkan, FLUX.2 klein): version 0.4.0 adds a browser UI

Image: media/portada-gimg.webp
Image: media/portada-galivelop.webp
Image: media/portada-tarkor-lapiz.webp
Image: media/portada-tarkor-desierto.webp
Image: media/portada-toveriai.webp

The images are covers for five projects from my workshop, composited with the tool (generated background plus headline and logo). The text on them is in Spanish.

**What it is**

galivelop-image-generator is a service that runs on your own machine and generates images with local AI for several projects at once. Each project declares the sizes and styles it needs; you request an image, try a few attempts, pick one, and it gets delivered into the project's folder.

**What's new in 0.4.0 (out today)**

- A browser UI in Spanish and English: a new-order panel (profile, prompt, number of attempts, draft, template, model), attempt review, and a queue you can reorder or clear.
- Composition templates you can pick per profile and per attempt.
- An element editor: move and resize the headline, logo and decorations with mouse or keyboard, with a live contrast indicator, then save the layout as a new template.
- Pieces and Brand tabs.
- `arrancar.sh` to open it with a double click.
- MIT licence (the models keep their own).

**Requirements**

- Linux with Vulkan. The reference machine is the Steam Deck.
- Python 3.10+. Nothing else to install: it only uses the standard library.
- About 7 GB of disk for the engine and the default models.

Install: `git clone` and `./instalar.sh`. It puts `gimg` in `~/.local/bin` and downloads a pinned stable-diffusion.cpp Vulkan release plus the models, checked against sha256 and kept outside the repo. `gimg doctor` tells you what's missing and the command that fixes it.

**The technical side**

- Engine: stable-diffusion.cpp's `sd-cli`, run as a subprocess. Default model: FLUX.2 klein 4B Q8 (Apache-2.0) with Qwen3-4B as the text encoder. A 1280×512 banner at 6 steps takes about 150 s on the Deck.
- Safeguards so it doesn't take the machine down: it checks free memory before launching, watches `MemAvailable` while generating, kills the whole `sd-cli` process group on cancel, and if Ollama is holding memory it either aborts or unloads it (your call).
- One service per machine, shared by several projects. Each project ships a `galivelop-images.json` with its profiles (size, steps, cfg, sampler, model).
- An order carries a key, profile, prompt, references and seed. The chosen image ends up at, say, `uploads/images/fauna/red-howler-banner.png` inside the project, with a manifest and undo.
- A persistent queue, attempts with notes and states, and a CLI in Spanish and English with `--json` output so other programs can drive it.
- Drafts, img2img, composition (headline, logo, decorations), brand measurement (palette, WCAG contrast, distance to a reference) and contact sheets for reviewing a round.
- An HTTP API bound to `127.0.0.1:8737` only, with Host, Origin and Content-Type checks. It starts on demand, and `gimg ui` opens the interface.
- Without `./instalar.sh` it uses a test engine that outputs flat-colour images, so you can try the workflow without a GPU.
- 252 commits from 25 October to 5 November, with 54 test files, including UI tests in headless Chrome.

**What's next**

First, the manual checks still pending on the Deck. Then, on the roadmap:

- Layered composition from pieces you already have (background, logo, loose elements, text), taken from chosen attempts or your own PNG/SVG files.
- Transparency when generating, and "Remove background".
- Reference images when generating.
- Text boxes placed before generating, which the generator takes into account.
- Deleting attempts, compositions and templates, with confirmation.
- Prompt-based editing: a new attempt derived from another one.
- Editing the text and typography of something already composited.
- F5: a pilot with real projects. F6 (optional): a local LLM via Ollama that drafts prompts and helps you choose. F7: more hardware (CPU, CUDA, ROCm, Metal), other Linux distros, Windows and maybe macOS.

Links:

- Code: https://github.com/Zeldris/galivelop-image-generator
- 0.4.0 release notes: https://github.com/Zeldris/galivelop-image-generator/releases/tag/v0.4.0
- Project page on the Galivelop portal: https://zeldris.github.io/Portal-Galivelop/proyectos/galivelop-image-generator
- The AI-agent workflow I build it with (Galivelop-workflow): https://github.com/Zeldris/Galivelop-workflow

A question for anyone generating locally: what's missing most from your workflow — background removal, layers or reference images? And if you have a Deck or another Linux box with Vulkan and give it a try, I'd love to hear your timings.
