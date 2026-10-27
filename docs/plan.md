# Plan: generador de imágenes local reutilizable

Un generador de imágenes con IA local, instalado una vez por máquina, que cualquier proyecto puede usar. Nace del
`image-generator/` de World-Maker-Fantasy (WMF), que es su primer consumidor. Vocabulario en
[GLOSSARY.md](../GLOSSARY.md).

## Decisiones de diseño

Tomadas con `grilling` el 2026-10-25.

| # | Decisión | Por qué |
|---|---|---|
| D1 | El generador es un **servicio local independiente**, uno por máquina, con API HTTP, CLI e interfaz web propias | Copiarlo en cada proyecto duplica 19 GB de modelos y el código diverge; ComfyUI o InvokeAI no traen las protecciones de memoria de la Deck y obligan a PyTorch |
| D2 | **No conoce el dominio** de ningún proyecto: recibe pedidos cerrados (prompt, perfil, referencias, destino) | La lógica de prompts (fichas, `mundo.json`, `prompt_ficha.py`) es de cada proyecto; como mucho, un estilo del proyecto declarado, sin lógica |
| D3 | Cada proyecto se conecta con su **configuración del proyecto** (perfiles, estilo, carpeta de entrega) y manda pedidos por API o CLI; el generador no lee su base de datos ni su backend | Quita el Postgres por `podman`, el mundo fijo y la copia a mano a `uploads/images/` de WMF |
| D4 | **Primero Linux**, con la Steam Deck (Vulkan) como máquina de referencia; el motor, detrás de una interfaz para añadir Windows o NVIDIA sin reescribir | Es lo único probado; WMF es todo Linux |
| D5 | Binarios y modelos **fuera de git**, en una carpeta del usuario compartida por todos los proyectos, instalados por un script con versiones fijas y checksum; por defecto solo los usados (~7 GB) | Un solo juego de modelos por máquina; FLUX.3, la versión base y RealESRGAN quedan opcionales |
| D6 | **Python 3 solo stdlib** (mínimo 3.10, el de Ubuntu 22.04) para servidor y CLI, `unittest` como check, interfaz en HTML + JS sin framework | Se instala junto a cualquier stack sin dependencias |
| D7 | **WMF es el piloto**: el diseño debe sustituir su `image-generator/` sin perder nada (galería, notas, elegida, referencia `-r`, estimado, protecciones de memoria); su migración es una tarea del repo de WMF | Valida el diseño con un caso real; desde aquí no se toca WMF |
| D8 | El término del dominio es **pedido**, no «encargo» | «Encargo a un subagente» ya es del flujo y un agente los confundiría |
| D9 | Un pedido tiene **N intentos**, cada uno *nuevo*, *candidata* o *descartada*, y **como mucho una elegida**; elegir otra sustituye la entrega, conserva el historial y se puede deshacer | WMF solo tiene «elegida» y elegir sobrescribe sin deshacer |
| D10 | **Cola persistente en disco**: una generación a la vez, en orden de llegada, cancelable, con estimado por mediana del registro (motor, perfil, pasos, referencia); sobrevive a un reinicio | En la Deck no caben dos a la vez; era IMG-11 en WMF |
| D11 | La CLI **arranca el servicio bajo demanda**, solo en `127.0.0.1`; unidad `systemd --user` opcional | Parado no gasta nada; en la Deck nada residente mientras se juega |
| D12 | El generador guarda en la configuración del usuario la **lista de proyectos** (`… proyecto añadir <ruta>`); la configuración de cada proyecto vive en su repo (p. ej. `galivelop-images.json`) | Un servicio, varios proyectos, cada uno con su configuración versionada |
| D13 | **Intentos, cola y registro** en la carpeta de datos del usuario, por proyecto; **elegidas** en la carpeta de entrega; un **manifiesto** versionable en el proyecto. El registro guarda todos los parámetros (versión del motor, modelos, cfg, sampler, pasos, semilla, tamaño, tiempo, memoria) con rutas relativas | El repo no se ensucia y cada elegida es reproducible; WMF no guardaba cfg ni modelo y usaba rutas absolutas |
| D14 | Motor inicial: **`sd-cli` lanzado por imagen**; `sd-server` se mide después como tarea de `opt-ai` | `sd-server` ocuparía ~7 GB fijos de los 16 GB compartidos de la Deck; se decide midiendo |
| D15 | Las protecciones van en un **perfil de máquina** (memoria libre mínima, `--max-vram`, `--params-backend`, referencias por pedido, tope de tiempo), con preajuste `steam-deck`; un pedido que lo supera se rechaza con un mensaje claro | Hoy están fijas en `generar.sh` y solo valen para la Deck |
| D16 | Interfaz y documentación en **español e inglés** desde el principio (`visibleLanguages` en `.claude/gw.json`), textos en un archivo por idioma | Herramienta para reutilizar y publicar; traducir después sale más caro |
| D17 | Los proyectos usan la **API HTTP y la CLI documentadas**, con JSON Schema de la configuración del proyecto y del pedido; sin librería cliente hasta que un segundo proyecto la pida | WMF (TypeScript) llama por HTTP; los esquemas validan sin código propio |
| D18 | Cada pedido lleva una **clave del pedido** que pone el proyecto (p. ej. `fauna/aullador-rojo`); clave + perfil identifican el pedido, y reenviarlo **lo actualiza** conservando sus intentos | Como `<tipo>/<slug>` y `ImagePrompt` en WMF; sin clave, cada reenvío lo duplicaría |
| D19 | La interfaz deja **retocar el prompt**; cada intento guarda el prompt exacto y el manifiesto el de la elegida; el original del proyecto no se toca | Así se afina en WMF (`prompt \| desdeBase`); el proyecto sigue siendo la fuente (D2) |
| D20 | La configuración del proyecto declara **por perfil** tamaño, pasos, cfg, sampler y modelo; un pedido o la interfaz los cambian por intento, dentro del perfil de máquina | Hoy pasos y cfg son variables de entorno de `generar.sh`, sin selector |
| D21 | Entrega en **PNG**, con nombre por plantilla de la configuración del proyecto (por defecto `{key}-{profile}.png`, que debe llevar los dos; los nombres de perfil no llevan guion para que dos pedidos nunca compartan archivo); WebP y miniaturas, posproceso opcional más adelante | `sd-cli` da PNG y convertir sin dependencias no es trivial; el nombre coincide con `uploads/images/<tipo>/<slug>-<perfil>.png` de WMF |
| D22 | Interfaz en **tres pantallas**: proyectos; un proyecto con las pestañas **Pedidos** (filtros por perfil y estado), **Piezas** (plantillas que prellenan el pedido) y **Marca** (solo lectura); un pedido (galería con estados, veredicto sí / no + elegir y nota por intento, chip de medidas D31, retoque de prompt y parámetros, texto compuesto por pedido, otra semilla o N seguidas, borrador por defecto desde 1280×640, comparar dos lado a lado). Cola en barra persistente; idioma por el navegador con selector. Detalle en `docs/interfaz/propuesta.md` (confirmada por la persona, 2026-10-27) | Todo lo de WMF más estados, cola y comparar |
| D23 | Repo `galivelop-image-generator`, orden **`gimg`**, configuración del proyecto en `galivelop-images.json` | Corto y sin choques habituales en Linux |
| D24 | Instalación con `git clone` + `instalar.sh` (pone `gimg` en `~/.local/bin`, descarga motor y modelos, D5); la configuración del proyecto declara la **versión mínima** del generador y `gimg` avisa si la instalada es más antigua; semver y CHANGELOG | Sin pip ni paquetes; un proyecto sabe si su configuración vale con lo instalado |
| D25 | **Solo escribe** en su carpeta de datos y en la carpeta de entrega de proyectos registrados; **solo lee** referencias dentro del proyecto; rechaza `..` y enlaces que salgan. API solo en localhost, Content-Type JSON y mismo Origin | Las rutas de un pedido vienen del proyecto |
| D26 | El registro es **JSONL en el formato de `opt-ai`** (`.claude/skills/opt-ai/references/log-format.md`), una línea por intento: `gen_ai.provider.name` = `stable-diffusion.cpp`, `gen_ai.request.model`, `app.task` = perfil, `app.machine_profile`, `app.duration_ms`, `app.load_ms`, `app.error`, y lo propio de la imagen bajo `app.image.*` (pasos, cfg, sampler, tamaño, semilla, referencias, commit del motor, tiempos de muestreo y decodificado, memoria mínima). Se propone al flujo, con `gw-harvest`, una operación de imagen en `log-format.md` | `medir.py` acepta cualquier operación y agrupa por perfil de máquina, tarea y modelo, así que mide imágenes sin cambios; cierra IMG-3 de WMF |
| D27 | **Contrato y código en inglés**: claves JSON en camelCase (esquemas, API, configuración del proyecto), identificadores y comentarios del código en inglés; los textos visibles siguen en es/en (D16) y el glosario da el nombre en código de cada término (pedido = `order`, intento = `attempt`, elegida = `chosen`…) | Decidido por la persona en F0: herramienta para publicar; la bitácora, el plan y los commits siguen en español |
| D28 | **La composición de texto y logo la hace el generador, como paso declarado, no el modelo ni el proyecto.** El perfil declara `compose` (una plantilla SVG con huecos `{{title}}`, `{{subtitle}}`, `{{logo}}`… y el tamaño de destino) y el pedido trae `text` (los valores); el generador rasteriza la plantilla con `rsvg-convert` y la superpone con `ffmpeg` sobre la imagen generada, recortada y escalada al tamaño de destino. Se guardan las dos: `attempts/q<id>.raw.png` (lo que dio el modelo) y `attempts/q<id>.png` (la compuesta, la que ve la galería y se entrega); `gimg compose` recompone desde la cruda sin volver a generar. Alternativas: pedir el texto al modelo (FLUX no da texto legible: los prompts de Tarkor piden «completely textless»); que cada proyecto componga (repite ffmpeg y rsvg en cada repo, justo lo que D1 evita). Es compatible con D2: la plantilla es datos sin lógica, como el estilo. **Recomendación:** esta; **[P]** confirmar que ffmpeg y rsvg-convert entran como herramientas externas junto a `sd-cli` (D6: las comprueba `gimg doctor`, no se instalan con `instalar.sh` porque vienen del sistema; en la Deck ya están: ffmpeg 7.1.3 y rsvg-convert 2.63.3) | Un cambio de titular tras 49 min de generación no puede costar otros 49 |
| D29 | **Los logos son SVG vectoriales, nunca generados.** El modelo no reproduce una marca; cada proyecto aporta su logo en SVG dentro de su repo (`{{logo}}` lo referencia por ruta relativa, guardada por D25) y la composición lo coloca. Donde no hay SVG (toVeriAI solo tiene `favicon.png` de 512 px; Galivelop-workflow y Tarkor no tienen nada) el generador sirve para **bocetar** conceptos (intentos de 1024×1024 con el prompt del símbolo) y el logo final lo escribe el agente como SVG (código, como `gv-logo.svg`), la persona lo aprueba y se propone al repo de cada proyecto. Alternativa descartada: vectorizar lo generado (no hay herramienta stdlib y el resultado no es una marca estable) | Un logo tiene que ser idéntico en todas las piezas y escalar sin pérdida |
| D30 | **Dos conjuntos de modelos heredados de Tarkor, en un catálogo, y un solo perfil de máquina que sabe correr cada uno.** `gimg/models.json` (versionado) declara cada conjunto con id, licencia, archivos (difusión, codificador de texto, VAE: nombre, URL, sha256, MB) y valores por defecto: `flux2-klein-4b-q8` (**rápido**: FLUX.2 klein 4B Q8_0 + Qwen3-4B Q4_K_M + `full_encoder_small_decoder`; cfg 1, euler, 6 pasos; banner 1280×512 en 110-150 s) y `flux3-klein-q8` (**calidad**: FLUX.3 Image Klein Q8_0 + Qwen3VL-4B-Instruct Q4_K_M + `flux2-vae`; guía 1, 16 pasos; ~49 min). El perfil de máquina añade `engine.models.<id>` con lo propio de esa máquina para ese modelo: `args` (`--backend diffusion=cpu -t 8` para FLUX.3, que con 2 GB de GPU no arranca), `timeoutS` (900 frente a 10800) y `minFreeMemoryMb`. El `model` del perfil del proyecto es un id del catálogo. Alternativa: dos perfiles de máquina (`steam-deck`, `steam-deck-calidad`): obliga a cambiar la configuración del usuario para alternar rápido y calidad en la misma sesión. **Recomendación:** catálogo + sobrescritura por modelo | Hoy son variables de entorno de `generar.sh` (`MODELO=`, `LLM=`, `VAE=`, `TOPE=`) y cada script las repite |
| D31 | **Medida de marca primero, LUT solo si hace falta.** `gimg measure <imagen> --palette <hex,…> [--refs <imágenes>] [--zone x,y,w,h --text <hex>]` da el porcentaje de píxeles cerca de la paleta, YAVG y SATAVG (`signalstats` de ffmpeg) y, con referencias, la EMD de Cb y Cr como `medir.sh` de Tarkor; con `--zone`, la relación de contraste WCAG entre la zona reservada y el color del texto. Los umbrales se **calibran con las imágenes de marca que ya existen** en cada repo (no se inventan). Si la ronda r2 muestra que el modelo no respeta la paleta, se hornea una LUT 3D `.cube` por marca como `gradar.sh --hornear` (`compose.lut` en el perfil, aplicada con `lut3d` antes de componer); si la respeta, la LUT pasa a F5. Alternativa: LUT desde el principio (coste fijo por marca sin saber si hace falta) | Tarkor mide antes de gradar y su aceptación es numérica (mediana EMD Cb ≲ 6, Cr ≲ 7,5, YAVG 70-95, SATAVG 15-30) |
| D32 | **Borrador antes del definitivo.** `order submit --draft` y `attempt new --draft` aplican el `draft` del perfil, que por defecto es el **mismo modelo a la mitad de lado** (redondeado a múltiplo de 64) y **8 pasos**, como el 640×256 de Tarkor (~5-9 min con FLUX.3; `[E]` en su plan); un perfil puede declarar otro (`{"model": "flux2-klein-4b-q8", "steps": 6}`: el modelo rápido a tamaño completo, ~2,5 min). El intento guarda `draft: true` y no se puede elegir. Además, todo intento escribe una vista previa por paso (`--preview proj --preview-interval 1` a `attempts/.preview-<entrada>.png`) para abortar a tiempo. **Recomendación:** por defecto el mismo modelo pequeño (misma composición *(suposición)*: lo comprueba la ronda r3, igual que IMG-19a en Tarkor, aún sin resolver); si no coincide, el borrador pasa a ser el modelo rápido y solo decide el prompt | A 49 min por definitivo, iterar sin borrador no es posible |
| D33 | **El motor real corre `sd-cli` como proceso en su propio grupo, con las protecciones de `generar.sh` en Python y sin `timeout`:** memoria libre mínima antes de arrancar, vigilante de `MemAvailable` que mata el grupo por debajo de `watchMemoryMb`, aborto si el log dice «reported free 0.00 MB», tope de tiempo del perfil (o del modelo) y comprobación de Ollama (`engine.ollama`: `abort` por defecto, `unload` o `ignore`). Cancelar y tope matan el grupo entero (`os.killpg`): en Tarkor, matar `timeout` dejaba `sd-cli` vivo con la memoria. `LD_LIBRARY_PATH` es la carpeta del motor (las librerías de Ollama le quitan la GPU) | Las protecciones son lo único que evita que la Deck se congele; hoy valen solo para Tarkor |
| D34 | **El registro guarda la orden completa.** Cada intento guarda `command` (argv de `sd-cli` con rutas relativas a la carpeta de modelos) y el registro añade `app.image.model_files` (difusión, texto, VAE), `app.image.backend`, `app.image.threads`, `app.image.draft` y `app.image.compose` (plantilla); `app.image.engine_version` es la release de stable-diffusion.cpp (`master-1000-95ff762`). Lo que no se registró no se reproduce (D13) | Tarkor no guardaba cfg ni modelo y hubo que rehacer pruebas |
| D35 | **Las elegidas del piloto no van a git.** La carpeta de entrega de cada `examples/<proyecto>/` (`entrega/`) está en `.gitignore`; cada ronda deja en `docs/registros/contenido/rN-<tema>.md` su tabla y una miniatura WebP ≤ 100 KB por pieza (`ffmpeg`, 640 px de ancho) **[P]**. Las piezas definitivas se proponen a cada repo con la configuración | Un og:image PNG pesa 1-2 MB y el repo no es un almacén de imágenes (D5) |
| D36 | **El motor por defecto sigue siendo `fake` hasta que `instalar.sh` escribe `"engine": "sdcpp"` en `<config>/config.json`**; `GIMG_ENGINE` manda sobre el archivo. Los tests fijan `fake` y nunca necesitan `sd-cli`, GPU, ffmpeg ni rsvg: el envoltorio se prueba con un `sd-cli` falso (`GIMG_SD_CLI=tests/fake_sd_cli.py`) y la composición y la medida con `skipUnless(shutil.which(...))` **[P]** (el CI de GitHub los instala con `apt`; sin ellos, los tests que los usan se saltan y lo dicen) | El check tiene que pasar en cualquier máquina y en el CI |

Decisiones difíciles de revertir, con su ADR: [0001](adr/0001-servicio-local-independiente.md) (D1) y
[0002](adr/0002-generador-sin-dominio.md) (D2).

## Punto de partida: lo que hay en WMF

- Motor: stable-diffusion.cpp `master-1000-95ff762`, `sd-cli` lanzado una vez por imagen, Vulkan, FLUX.2 klein 4B Q8 +
  Qwen3-4B Q4_K_M + VAE small decoder. Banner 1280x512 a 6 pasos: ~150 s (con `-r`, ~275 s).
- Protecciones: aborta con menos de 7000 MB libres, vigila `MemAvailable` (1500 MB), `--params-backend disk`,
  `--max-vram vulkan0=2` (`vulkan0=6` bloqueó la Deck).
- Interfaz: Python stdlib en `127.0.0.1:7861`, una generación a la vez sin cola, galería, notas, elegir.
- Deuda que el diseño no debe heredar: dos fuentes de prompt, registro sin cfg ni modelo y con rutas absolutas,
  `sd-server` sin uso, elegir sin deshacer, sin tests, solo Linux.

## Fases (aprobadas el 2026-10-25)

Cada fase es una rama y un pull request a `main`, con las tres fases de revisión de `AGENTS.md`.

| Fase | Qué trae | Hecha cuando |
|---|---|---|
| F0 Esqueleto | Estructura del repo; JSON Schema de la configuración del proyecto, el pedido y el perfil de máquina; textos es/en; README es/en; `check` real (`python3 -m unittest`) | El check corre tests y los esquemas validan los ejemplos |
| F1 Núcleo | Proyectos registrados, pedidos (clave + perfil), intentos y estados, elegida con deshacer, entrega y manifiesto, cola persistente, límites de seguridad, registro JSONL; CLI `gimg` básica; todo con un **motor de pruebas** que no genera de verdad | Tests en verde del ciclo completo con el motor de pruebas |
| F2 Motor real | Envoltorio de `sd-cli` con el perfil de máquina (memoria, `--max-vram`, tope, cancelar, progreso); `instalar.sh` con versiones fijas y checksum; catálogo de modelos, borradores, composición de texto y logo, medida de marca; **piloto de contenido corporativo** (Portal, Tarkor, toVeriAI, Galivelop-workflow) con configuraciones de ejemplo en este repo *(aprobado 2026-10-26)* | Un pedido real generado en la Deck y la primera ronda de piezas definitivas de los cuatro proyectos elegidas por la persona (comprobación manual) |
| F3 API y arranque | API HTTP (D17, D25) y arranque bajo demanda; unidad `systemd --user` opcional | Tests de la API; `gimg` arranca el servicio solo |
| F4 Interfaz | Las tres pantallas de D22, es/en | Recorrido completo en el navegador |
| F5 Piloto WMF | Configuración de ejemplo para WMF, guía de integración y propuesta de migración para su repo; medida base con `opt-ai` y comparación `sd-server` (D14); LUT por marca si F2 la deja pendiente *(aprobado 2026-10-26: el piloto corporativo pasa a F2 y WMF sigue aquí)* | WMF genera y recibe una elegida sin copia a mano |

## F1 en detalle

Contrato de F1 (lo implementan los pasos de abajo; un cambio de este contrato se apunta aquí en el mismo commit).
Todo en `gimg/`, Python stdlib, identificadores en inglés (D27), mensajes visibles por `i18n.t` en es y en (D16).

**Carpetas** (`gimg/paths.py`). Configuración: `$GIMG_CONFIG_HOME`, si no `$XDG_CONFIG_HOME/gimg`, si no
`~/.config/gimg`. Datos: `$GIMG_DATA_HOME`, si no `$XDG_DATA_HOME/gimg`, si no `~/.local/share/gimg`. Los tests
fijan las dos variables `GIMG_*` a carpetas temporales. La guardia de rutas (D25) es `inside(root, rel)`: rechaza
`rel` absoluta, con `~` inicial, segmentos `..`, `\`, NUL o caracteres de control; resuelve con enlaces y exige que el
resultado quede dentro de `root` resuelto. Toda ruta que venga de un proyecto pasa por ella.

**Escritura** (`gimg/fsutil.py`). JSON con escritura atómica (temporal en la misma carpeta + `os.replace`), y un
cerrojo `fcntl.flock` por archivo para cada leer-modificar-escribir.

**Proyectos** (`gimg/projects.py`). Registro en `<config>/projects.json`: `{"projects": {"<name>": {"root":
"<ruta absoluta>"}}}`. `project add <ruta>` lee `<ruta>/galivelop-images.json`, lo valida con su esquema, comprueba
`minVersion` contra `gimg.__version__` y que `delivery.dir` y `manifest` no caigan en `.git/` ni sean
`galivelop-images.json`; mismo nombre con otra ruta es un error. La configuración se relee en cada operación.

**Pedidos e intentos** (`gimg/orders.py`). Un pedido vive en `<datos>/projects/<proyecto>/orders/<key>/@<perfil>/`
(la `@` evita que la clave `a/banner` choque con la clave `a` y el perfil `banner`): `order.json` y
`attempts/<id>.png` (o `attempts/q<entrada>.png` si lo creó una entrada de la cola). `order.json`: `key`, `profile`, `prompt` (el del proyecto), `references`, `params`, `seed`,
`createdAt`, `updatedAt`, `attempts` (lista de `{id, state, seed, prompt, params, references, image, note,
createdAt, queueEntry?}`, con `prompt` exacto ya con el estilo y `params` completos: `width`, `height`, `steps`, `cfg`,
`sampler`, `model`), `chosen` (id o `null`) y `chosenHistory` (pila para deshacer). Estados: `new`, `candidate`,
`discarded`. Reenviar clave + perfil actualiza prompt, referencias y parámetros y conserva los intentos (D18). Elegir
apila la elegida anterior (aunque sea `null`); deshacer la desapila. No se elige una descartada ni se descarta la
elegida. Deshacer no restaura una descartada (`order.undo_discarded`): se marca antes `new` o `candidate`; volver a `null` sí. `key` con `maxLength` 200 en el esquema y cada segmento ≤ 100 caracteres en el código; `prompt` con
`maxLength` 4000.

**Prompt y parámetros de un intento** (`orders.attempt_specs`). `prompt` exacto = prompt del pedido (o el retocado,
D19) + `", "` + `style` del perfil (solo si `style` no está vacío); si el resultado supera el `maxLength` del `prompt` del esquema del pedido, `attempt_specs` falla con `order.prompt_too_long` antes de encolar. `params` = ajustes del perfil (`width`, `height`,
`steps`, `cfg`, `sampler`, `model`, los que defina) pisados por `params` del pedido y estos por los del intento.
`choose` y `undo` devuelven `{old, new}` para que la entrega se enganche; elegir la ya elegida no apila.
**Imagen de un intento:** el campo `image` (relativo a la carpeta del pedido) manda; la ruta sale de
`orders.attempt_image(proyecto, key, perfil, intento)` (resuelta y dentro de la carpeta, D25), y la entrega de F1.5 la lee del
registro del intento. Un intento creado por la cola lleva `queueEntry: <id de la entrada>` e `image: attempts/q<id>.png`
(el id de entrada es único en todo el generador); `orders.add_attempt(..., entry_id=)` es idempotente por entrada (si ya hay un
intento con ese `queueEntry` devuelve su id sin añadir fila) y `orders.attempt_for_entry` lo busca. Sin `entry_id`, `image` es `attempts/<id>.png`.
Los textos de error de pedidos usan `{order}` (no `{key}`, que choca con `i18n.t`).

**Semillas.** Con `seed` en el pedido, el intento i usa `seed + i`; sin ella, aleatoria en `[0, 2^32)`. Un intento
nuevo (otra semilla, N seguidas, prompt o parámetros retocados, D19-D20) no cambia el pedido. `order submit` usa la semilla del
pedido, así que reenviarlo con semilla reproduce la misma imagen; `attempt new` sin `--seed` usa una aleatoria.

**Límites** (`gimg/limits.py`, D15). Al encolar y al ejecutar: referencias ≤ `maxReferences`, `steps` ≤ `maxSteps`,
`width × height` ≤ `maxPixels` (lo que el perfil no fije, como `steps`, no se comprueba; los valores por
defecto de cada modelo los pone el motor real en F2); si no, `LimitError` con mensaje claro. La memoria la comprueba el motor real (F2). El
perfil de máquina sale de `GIMG_MACHINE_PROFILE` (nombre de `gimg/machine_profiles/` o ruta a un JSON) o de
`machineProfile` en `<config>/config.json` (si ese archivo no se puede leer, `machine.config_unreadable`); por defecto `steam-deck`. La ruta del perfil de máquina es entrada de confianza de la persona en su propia máquina
(fuera de D25): puede ser absoluta o relativa y se expande `~`; sin caracteres de control (`machine.bad_path`), y si no se puede leer, `machine.unreadable`.

**Motor** (`gimg/engine.py`). `generate(job, should_cancel) -> EngineResult`. `EngineJob`: prompt, width, height,
steps, cfg, sampler, model, seed, references (rutas absolutas), output (ruta absoluta), machine (perfil), timeout_s.
`EngineResult`: `duration_ms`, `load_ms`, `sample_ms`, `decode_ms`, `engine_version`, `min_free_mb` (opcional).
Errores: `EngineError(message)` y `Cancelled`. `FakeEngine` (`provider` = `fake`) escribe un PNG válido del tamaño
pedido, de un color que sale de la semilla, y admite fallar o tardar a propósito. `GIMG_ENGINE` elige motor; en F1
solo existe `fake`. El motor de pruebas lee `GIMG_FAKE_DELAY` (segundos de espera, cancelable) y `GIMG_FAKE_FAIL` (falla con ese mensaje), para los tests de la cola y el trabajador (`GIMG_FAKE_DELAY` debe ser finito y >= 0, si no `engine.bad_delay`). Si `timeout_s` (segundos, admite fracciones) es menor que la espera, el motor de pruebas para en `timeout_s` y lanza `EngineTimeout` (subclase de `EngineError`, mensaje estable `timeout`, `engine.TIMEOUT_MESSAGE`) para que el trabajador lo distinga. Los archivos finales (PNG y JSON) respetan la umask como un `open()` normal.

**Registro** (`gimg/log.py`, D26). `<datos>/projects/<proyecto>/log.jsonl`, una línea por intento (bien o mal) en el
formato de `opt-ai`, sin campos `null`: `ts`, `gen_ai.operation.name` = `image_generation`, `gen_ai.provider.name`,
`gen_ai.request.model`, `app.task` = perfil, `app.machine_profile`, `app.duration_ms`, `app.load_ms`, `app.error`, y
`app.image.*`: `key`, `steps`, `cfg`, `sampler`, `width`, `height`, `seed`, `references` (cuántas), `engine_version`,
`sample_ms`, `decode_ms`, `min_free_mb`. Estimado: mediana de `app.duration_ms` de las líneas sin error con el mismo
motor, perfil, pasos y con o sin referencia; sin datos, no hay estimado.

**Cola** (`gimg/queue.py`, D10). Una para todo el generador: `<datos>/queue.json`, `{"nextId": n, "entries": [...]}`;
cada entrada: `id`, `project`, `key`, `profile`, `seed`, `prompt`, `params`, `references`, `state` (`queued`,
`running`, `done`, `failed`, `cancelled`), `pid`, `enqueuedAt`, `startedAt`, `finishedAt`, `error`, `attemptId`,
`cancelRequested`. En orden de llegada; cancelar una `queued` la pasa a `cancelled`, una `running` pide cancelar.
Una `running` cuyo trabajador murió vuelve a `queued` (o a `cancelled` con `cancelRequested`); eso lo decide el cerrojo
`worker.lock`, no el `pid`: quien consigue tomarlo sin esperar sabe que no hay trabajador vivo, así que toda `running` está
muerta. El trabajador lo hace justo después de tomar su cerrojo (`queue.recover_orphans`); `list`, `get` y `enqueue` lo
intentan sin esperar (si lo toman, recuperan y lo sueltan; si no, dejan las `running`); `claim`, `cancel`, `finish`,
`next_queued` e `is_cancel_requested` nunca recuperan. `pid` queda solo como información. La recuperación borra los
`.pending-<entrada>.png` de las entradas recuperadas (solo esas: más barato que recorrer todos los pedidos, y un fallo solo
puede dejarlo de una entrada que estaba `running`). Se guardan las 200
últimas terminadas. El trabajador (`gimg/worker.py`) toma un cerrojo propio (`worker.lock`) para que corra uno solo:
saca la primera `queued`, comprueba límites, llama al motor, crea el intento, escribe el registro y cierra la entrada.
Detalles de F1.4: toda lectura y escritura de `queue.json` va bajo `fsutil.lock`, y la recuperación (reinicio y poda) se hace
en esa misma transacción; una `running` recuperada con `cancelRequested` pasa a `cancelled`, no a `queued`. `enqueue` valida
que el pedido exista y los límites del perfil de máquina de ese momento; si una spec falla, no se encola ninguna. `error` de una
entrada fallida es siempre `{"code": ..., "params": {...}}` (JSON), más `"errors": [{path, code, params}]` si el `GimgError` traía errores de esquema (`error_text` los pinta debajo, como `GimgError.message`; tolera formas antiguas): el `GimgError` conserva código, parámetros y errores,
`EngineTimeout` es `engine.timeout`, otro `EngineError` es `engine.failed` con `{"message"}` y una excepción inesperada
`worker.unexpected` con `{"message": "Tipo: mensaje"}`; `queue.error_text(error_o_entrada, idioma)` lo traduce con i18n
(la CLI de F1.6 lo usa). **Id y orden del intento:** la imagen se llama como la entrada: el motor escribe
`attempts/.pending-<entrada>.png`, el trabajador lo mueve con `os.replace` a `attempts/q<entrada>.png` y solo entonces llama a
`add_attempt(..., entry_id=)`, luego escribe la línea de registro y cierra la entrada. Antes de generar, si ya hay un intento
con ese `queueEntry` (cayó tras `add_attempt`), no llama al motor y cierra `done`. Un fallo no deja huérfanos: el temporal
se borra en cualquier fallo o cancelación y la imagen movida si `add_attempt` falla; si el movimiento falla, la entrada
falla con `worker.image_move`. Una vez creado el intento nada puede fallar la entrada: la línea de registro y `finish` se
intentan sin más (si `finish` falla, la entrada queda `running` y la recuperación se ocupa) y nunca se escribe una línea
de fallo; ningún error de `finish` para el bucle de `run()`. **Registro:** una línea por cada intento que llega a ejecutarse y
termina, bien o mal (límites, referencias, motor y `timeout` llevan `app.error`, el texto en inglés del error); cancelar no escribe línea. Los límites se
comprueban otra vez al ejecutar con el perfil de máquina actual. Un segundo trabajador falla con `worker.already_running`.

**Entrega y manifiesto** (`gimg/delivery.py`, D13, D21, D25). Elegir copia la imagen (temporal + `os.replace`) a
`inside(inside(root, delivery.dir), template con {key} y {profile})` y escribe el manifiesto (`manifest`, por defecto
`galivelop-images.manifest.json`): `{"version": 1, "images": {"<key>": {"<perfil>": {file, prompt, seed, params,
references, engine, engineVersion, attemptId, chosenAt}}}}`, con `file` relativo a la raíz del proyecto, claves
ordenadas, sangría 2 y salto final. Deshacer hasta `null` borra su entrada y el archivo entregado solo si el `file` de la entrada es
el destino actual (si la configuración cambió, el archivo no se toca). Elegir sobrescribe lo que haya en el destino: la carpeta de
entrega es del generador. La entrega no comprueba las referencias (solo importan al generar; las comprueba el trabajador).

API: `delivery.choose(project, key, profile, attempt_id)` y `delivery.undo(project, key, profile)` envuelven a `orders.choose`/`undo`
y devuelven su `{old, new}`; la CLI solo llama a estas. **Orden y fallos:** 1) se prepara sin tocar nada: ruta destino (la
segunda guardia es relativa a la carpeta de entrega, así `../` o un enlace que salga de ella se rechazan con `path.*`; el
destino no puede ser el manifiesto, la configuración ni la propia carpeta: `delivery.reserved`), imagen del intento (`delivery.source_missing`)
y manifiesto legible (`delivery.manifest_corrupt`); 2) se cambia el pedido; 3) se copia
(temporal en la carpeta destino + `os.replace`, umask respetada) y se escribe el manifiesto bajo `fsutil.lock`, o, si la nueva elegida es
`null`, se borra el archivo (si no existe no es error) y su entrada (la clave sin perfiles se quita). Si el paso 3 falla
(`delivery.write_failed`), se revierte el pedido (`orders.undo` tras un `choose`; `orders.choose` de la anterior tras un `undo`, a mejor
esfuerzo) y se relanza; si el archivo entregado ya había cambiado (falló la escritura del manifiesto tras la copia o el borrado), la
reversión también lo restaura (copia de nuevo la imagen de la elegida anterior, o quita el archivo si no había; el manifiesto en disco
no cambió porque su escritura es atómica) y, si eso también falla, el error que se relanza es el original; si falla el paso 1, el pedido no cambia. Elegir la ya elegida vuelve a entregarla. **Cerrojo:** `choose`/`undo` enteros (leer el pedido, decidir el plan, cambiar el pedido, entregar y revertir) corren bajo un solo cerrojo por proyecto, `<datos>/projects/<proyecto>/delivery.lock`, nunca dentro del proyecto entregado; el manifiesto se escribe bajo él. Si un intento deja de estar descartado entre leer y cambiar el pedido (un `mark` fuera del cerrojo), se revierte y se da `order.choose_discarded`/`order.undo_discarded`. Un intento
guarda `engine` y `engineVersion` (los pone el trabajador) y el manifiesto los copia (`null` si falta, en intentos antiguos). Una carpeta
de entrega que sea un enlace hacia fuera ya la rechaza `projects.get` al cargar la configuración (`path.outside`)

**CLI** (`gimg/cli.py`, `python3 -m gimg`; el lanzador `gimg` llega con `instalar.sh` en F2). Órdenes en inglés:
`project add|remove|list`; `order submit <proyecto> <archivo|->` (crea o actualiza y encola `count` intentos, dice
el estimado); `order list <proyecto> [--profile] [--chosen|--unchosen]`; `order show <proyecto> <key> <perfil>`;
`attempt new <proyecto> <key> <perfil> [--seed] [--count] [--prompt] [--steps] [--cfg] [--sampler]`;
`attempt mark … <id> new|candidate|discarded`; `attempt note … <id> <texto>`; `choose … <id>`; `undo …`;
`queue list|cancel <id>`; `work [--once]` (procesa la cola, y sus mensajes salen en el `--lang` de la CLI; en F3 lo hará el servicio); `version`. Errores por stderr
con salida 1.
Opciones globales (antes o después de la orden): `--lang es|en` (por defecto `i18n.default_lang()`) y `--json`. La CLI
es una capa fina: llama a los módulos del núcleo y todo texto visible sale de `i18n.t` (claves `cli.*`). `order submit` encola
`count` intentos con la semilla del pedido; `attempt new` sin `--seed` usa una aleatoria. Errores: un `GimgError` imprime su
mensaje traducido por stderr con salida 1; un error de uso de `argparse` sale con 2; una excepción inesperada imprime una línea
(`cli.unexpected`) con salida 1, y el traceback solo con `GIMG_DEBUG=1`. `work` falla con 1 si ya hay un trabajador.
**Forma de `--json`** (stdout, `ensure_ascii` falso, sangría 2): `project list` → `[{name, root}]`; `project add` → `{name}`;
`project remove` → `{removed}`; `order list` → lista de pedidos (el registro de `order.json`); `order show` → el pedido;
`order submit` y `attempt new` → `{entries: [entrada de la cola], estimateMs: n|null}`; `attempt mark|note` → el intento;
`choose` y `undo` → `{old, new}`; `queue list` → lista de entradas y `queue cancel` → la entrada, cada una con `errorText`
(traducido, solo si tiene error) además de su `error` `{code, params}`; `work` → `{processed}`.

### Pasos de F1

| Paso | Qué | Hecho cuando |
|---|---|---|
| F1.1 | `paths`, `fsutil`, `projects`, `maxLength` de `key` y `prompt` | Tests de la guardia (D25), del registro y de la carga de la configuración |
| F1.2 | `orders`: pedidos, intentos, estados, notas, elegir y deshacer (sin entrega) | Tests de reenvío, estados y pila de elegidas |
| F1.3 | `engine` (`FakeEngine`), `limits`, `log` y estimado | Tests del PNG, los límites, el formato del registro y la mediana |
| F1.4 | `queue` y `worker` | Tests de orden, cancelar, reinicio y un solo trabajador |
| F1.5 | `delivery` y manifiesto, enganchados a elegir y deshacer | Tests de entrega, guardia de la plantilla y manifiesto |
| F1.6 | `cli` y prueba del ciclo completo; README es/en con el uso | Test de extremo a extremo: añadir proyecto, pedir, trabajar, elegir, deshacer |

## F2 en detalle

**Aprobado por la persona el 2026-10-26** con las recomendaciones de cada [P] (abajo); lo marcado
*(suposición)* no está en las fuentes y se comprueba en la primera ronda. Fuentes: `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`
(generador de Tarkor y marcas), el kit visual de toVeriAI (`VeriNews_AI/Documentacion/v1.1/kit-visual-ia.html`), el Portal
(`public/marca/`, `src/estilos/global.css`, `src/data/proyectos/`) y, en Tarkor, `image-generator/scripts/` y
`docs/producto/plan-imagenes/`. Las decisiones nuevas, D28-D36, están en la tabla general. F2 sigue el modelo del generador de Tarkor: sus protecciones, sus dos perfiles (rápido y de calidad), su banco de
rondas y su cadena de composición con ffmpeg y rsvg-convert; su piloto es **contenido corporativo** (marca, logos, redes,
cabeceras, og:image) de cuatro proyectos: Portal Galivelop (marca paraguas), Tarkor, toVeriAI y Galivelop-workflow. El piloto
de WMF sigue en F5.

### Alcance

**Entra en F2**, en este orden, para que haya contenido real cuanto antes (con la CLI; la interfaz es F4):

0. **Arranque con lo que ya hay [P]:** los modelos y `sd-cli` de Tarkor ya están en la Deck
   (`World-Maker-Fantasy/image-generator/{bin,modelos}`, 35 GB). Las rondas r0 y r1 se lanzan **antes de escribir código**
   con su `generar.sh` tal cual (solo se ejecuta: escribe en la carpeta de salida que se le pasa, que va fuera de su repo,
   en `<datos>/pilot/rN/`), con los prompts de los estilos de abajo en `examples/<proyecto>/prompts/`. Así los estilos se
   prueban mientras se construye F2.1-F2.5, y r0 da el formato real del log y del progreso que imita el `sd-cli` falso.
1. El motor real: envoltorio de `sd-cli` (`gimg/engine_sdcpp.py`), catálogo de modelos e `instalar.sh`. Lo primero que se
   genera es un fondo sin texto en la Deck (ronda r0, abajo).
2. Las configuraciones de ejemplo de los cuatro proyectos (`examples/<proyecto>/galivelop-images.json` y sus pedidos en
   `examples/<proyecto>/orders/`), con las que se prueban los estilos. Viven aquí porque desde este repo no se toca otro;
   al cerrar F2 se proponen a cada repo en `docs/propuestas/<proyecto>.md`.
3. Borradores (`--draft`) y progreso con vista previa, para iterar barato.
4. Composición de texto y logo encima de la imagen (`compose`), con recorte y escala al tamaño de destino.
5. Medida de marca (`gimg measure`): el criterio objetivo de las rondas.

**No entra:** la API HTTP y el arranque bajo demanda (F3), la interfaz (F4), WMF (F5), `sd-server` (D14, F5), WebP y
miniaturas de entrega (D21, después), Real-ESRGAN (solo da tamaño, no calidad: F5 si hace falta), Windows o NVIDIA (D4), y
cualquier LoRA, inpainting o regional prompting (descartados en la Deck por Tarkor). **Se mueve a F5 si F2 se alarga:** la LUT
por marca (D31) y las piezas no prioritarias de cada proyecto. Lo que se queda fuera se apunta en «Pendiente».

**Decisiones de la persona (2026-10-26):** arranque F2.0 con el `generar.sh` de Tarkor; ffmpeg y rsvg-convert como
herramientas externas (D28); elegidas del piloto fuera de git y miniaturas WebP ≤ 100 KB en los registros (D35); el CI instala
ffmpeg y rsvg con `apt` (D36); hasta confirmar la licencia de FLUX.3, lo publicado sale de klein 4B; el agente vectoriza el
símbolo de toVeriAI como SVG y la persona lo aprueba; monograma «gw» para Galivelop-workflow; Tarkor con la paleta y el
emblema propuestos y Cinzel (OFL) como tipografía del wordmark, provisional hasta r4.

### Decisiones nuevas

D28-D36, en la tabla general de decisiones.

### Contratos

**Catálogo de modelos** (`gimg/models.json`, esquema `gimg/schemas/models.schema.json`). `{"models": {"<id>": {"license":
"Apache-2.0", "files": {"diffusion": {...}, "text": {...}, "vae": {...}}, "defaults": {"steps", "cfg", "sampler"}, "args":
[...]}}}`; cada archivo `{"name", "url", "sha256", "sizeMb"}`. Ids iniciales: `flux2-klein-4b-q8` y `flux3-klein-q8` (D30); `args`
comunes a los dos: `--flash-attn off,diffusion=on --vae-tiling`. Los archivos viven en `<datos>/models/{diffusion,text,vae}/`
(`$GIMG_MODELS_HOME` para otra ruta, p. ej. una tarjeta SD de la Deck) y el motor en `<datos>/engine/<release>/`. El `model` de un
perfil del proyecto tiene que existir en el catálogo (`model.unknown`) y estar instalado al ejecutar (`model.not_installed`, con
la orden que lo instala). Las URLs y los sha256 se toman de las descargas que ya hay en la Deck (`WMF-imagenes/image-generator/
descargas/` y `modelos/`), que la persona verifica **[P]**; la licencia de FLUX.3 queda `"unconfirmed"` hasta confirmarla (Riesgos).

**Perfil de máquina** (cambios en `machine-profile.schema.json`). `engine` añade `sdCli` (ruta del binario, por defecto la del
motor instalado), `ollama` (`abort`|`unload`|`ignore`), `threads` y `models.<id>` (`args`, `timeoutS`, `minFreeMemoryMb`, que
pisan los del perfil para ese modelo). `steam-deck.json` queda: `minFreeMemoryMb` 7000, `watchMemoryMb` 1500, `maxReferences` 1,
`timeoutS` 900, `maxSteps` 50, `maxPixels` 1048576, `engine: {"maxVram": "vulkan0=2", "paramsBackend": "disk", "ollama": "abort",
"models": {"flux3-klein-q8": {"args": ["--backend", "diffusion=cpu", "-t", "8"], "timeoutS": 10800, "minFreeMemoryMb": 5000}}}` (el
5000 es el valor al que Tarkor bajó en pruebas; FLUX.3 corrió con 4,4-6 GB libres de mínimo).

*Hecho en F2.1* (`gimg/models.py`): `load_catalog()` (`model.catalog_invalid`), `check_known(id)` y `resolve(id, machine)`, que
devuelve `defaults`, `args` (catálogo y luego `engine.models.<id>.args`), `timeoutS`, `minFreeMemoryMb` (los del modelo si el perfil
los fija, aunque sean 0, si no los generales) y `files[kind]` con su `path` bajo `paths.models_dir()`; `missing_files()` dice qué
archivos faltan en disco (el error `model.not_installed` es de F2.5). Los ids son exactos (minúsculas, sin normalizar) y un id
fuera del catálogo da `model.unknown`, también en `load_config` de un perfil del proyecto. **Decisión:** un `engine.models.<id>` del
perfil de máquina que nombra un modelo ausente del catálogo se ignora (un perfil puede sobrevivir a un cambio del catálogo); pedir
ese id sigue siendo `model.unknown`. `sizeMb` son 10^6 bytes redondeados. Los `sha256` y las URLs están comprobados contra la
cabecera `x-linked-etag` de Hugging Face y contra `sha256sum` de los archivos de la Deck; el codificador de FLUX.3 se guarda como
`Qwen3VL-4B-Instruct-Q4_K_M.gguf` (el nombre del repositorio de Qwen), no `Qwen3-VL-…`.

**Motor** (`gimg/engine_sdcpp.py`, `provider` = `stable-diffusion.cpp`, D26). `SdCppEngine(machine, catalog).generate(job,
should_cancel)` con el `EngineJob` de F1 más `draft: bool`, `init_image: str | None` y `strength: float | None` (img2img; con
FLUX.3 añade `--extra-sample-args strength_as_noise_level=true`, sin él cualquier fuerza es casi ruido). Orden: 1) resolver el
modelo (catálogo + `engine.models`), comprobar archivos; 2) protecciones previas: `MemAvailable` ≥ mínimo (`engine.low_memory`,
con los MB libres y los que pide), Ollama (`engine.ollama_loaded`, con los modelos cargados y `ollama stop <modelo>`); 3) argv:
`sd-cli --diffusion-model … --llm … --vae … -p <prompt> --cfg-scale … --steps … --sampling-method … -W … -H … --seed …
--params-backend disk --max-vram vulkan0=2 <args del modelo y de la máquina> [-r <ref>]… [-i <init> --strength …] --preview proj
--preview-interval 1 --preview-path <pending>.preview.png -o <output> -v`; 4) `subprocess.Popen(start_new_session=True)`, stdout y
stderr a `attempts/.pending-<entrada>.log`; 5) bucle cada 0,5 s: `should_cancel()` → `killpg` + `Cancelled`; tope → `killpg` +
`EngineTimeout`; `MemAvailable` < `watchMemoryMb` o «reported free 0.00 MB» en el log → `killpg` + `EngineError` con el motivo;
progreso: la barra de pasos de `sd-cli` (`| 3/6 -  24.65s/it - ETA 01:16`, confirmada en el log real) se escribe en la
entrada de la cola (`progress: {"step": n, "steps": N, "etaS": …}`; `queue list` lo pinta); 6) código de salida ≠ 0 → `EngineError`
con las últimas 5 líneas del log; 7) `EngineResult` con `load_ms`, `sample_ms` («sampling completed, taking Xs») y `decode_ms`
(«decode_first_stage completed»), `min_free_mb` del vigilante, `engine_version` = release y `command` (D34). El log del intento se
conserva junto a la imagen (`attempts/q<id>.log`). Tests con `GIMG_SD_CLI` apuntando a un `sd-cli` falso que escribe un PNG,
imprime líneas de progreso y tarda lo que le digan: argv, progreso, cancelar, tope, memoria (el lector de `/proc/meminfo` se
inyecta), código de salida, campos del registro.

*Hecho en F2.2* (`gimg/engine_sdcpp.py`, `tests/fake_sd_cli.py`): solo la parte de proceso (pasos 3-7 del contrato, sin los puntos 2 ni `draft`/`initImage`/`strength`).
**Decisiones:** (1) *Tope:* manda el `timeoutS` resuelto por modelo (`engine.models.<id>.timeoutS`, si no el del perfil); `job.timeout_s` solo vale si el
perfil no trae ninguno, porque el worker ya le pasa el general y daría igual el del modelo; `None`, `0` o negativo = sin tope en esa fuente. (2) *Perfil:* manda
`job.machine` si no está vacío (el worker lo recarga en cada entrada), si no el del constructor. (3) *Log:* el motor escribe `<salida>.log` (con la salida
`.pending-<entrada>.png` del worker, `.pending-<entrada>.log`; la vista previa, `.pending-<entrada>.preview.png`) y devuelve la ruta en
`EngineResult.log_path`; el worker lo renombra a `attempts/q<id>.log` tras mover la imagen (si falla, no pasa nada) y lo borra, con la vista previa,
si el intento falla o se cancela; `queue.recover_orphans` también los limpia. (4) *Matar:* `killpg` con SIGTERM, 3 s de gracia y SIGKILL al grupo;
sin `os.killpg` (Windows), `terminate()` y luego `kill()` del proceso solo (deja a sus hijos; sin probar, el proyecto corre en Linux). Una excepción
en el bucle (o Ctrl-C) mata el grupo antes de salir. (5) `load_ms` es la suma de las líneas `loading tensors completed`; `sample_ms` y `decode_ms`, la
última de su tipo; si la línea no está, `None`. (6) `command` lleva `sd-cli` sin carpeta y las rutas de modelos relativas a `paths.models_dir()`; el
registro (`log.record_for`) lo escribe desde F2.4. (7) Binario ausente o sin permiso: `engine.binary_missing`/`engine.binary_not_executable`; sin
`job.model`, `model.required`; sin archivos, `model.not_installed` con `instalar.sh --with <id>` (el script es de F2.5). (8) `-t <threads>` va antes de
los `args` del catálogo y la máquina, para que estos puedan fijar los suyos. (9) `get_engine()` lee `GIMG_ENGINE`, luego `"engine"` de `<config>/config.json`
(`sdcpp`/`fake`), por defecto `fake`.
**Para F2.3/F2.4:** el bucle llama a `SdCppEngine._on_tick(proc, log_path, job)` en cada pulso (0,5 s, `poll_s`): ahí van el vigilante de `MemAvailable`, el
aborto por «reported free 0.00 MB» y el progreso en la cola; la memoria previa y Ollama van en `generate` antes del `Popen`. Sin hacer tras F2.2
(F2.3 hizo lo de las protecciones y F2.4 el progreso y el registro): `draft`, `initImage`, `strength`; F2.7 lo hizo.

*Hecho en F2.3* (`gimg/engine_sdcpp.py`, `tests/test_engine_protections.py`): las protecciones del contrato (puntos 2 y 5) y `min_free_mb`.
**Decisiones:** (1) *Orden:* tras armar el argv y antes de crear el log: un rechazo no deja proceso, log ni imagen. (2) *Memoria previa:* `MemAvailable` ≥ `minFreeMemoryMb`
resuelto (el del modelo, aunque sea 0, si no el general); `engine.low_memory` con `free_mb` y `needed_mb`. El lector es `read_meminfo` (argumento del
constructor; por defecto `read_meminfo_mb`, que lee `GIMG_MEMINFO` o `/proc/meminfo`); sin `/proc`, o con un formato que no se entiende (`parse_meminfo` es
estricto: `MemAvailable: <n> kB`), da `None`: la comprobación y el vigilante se saltan y una línea `[gimg] …` al principio del log del intento lo dice. `GIMG_MEMINFO`
existe para que los tests (también los de un `gimg work` en subproceso) no dependan de la memoria de la máquina. (3) *Ollama:* `engine.ollama` (`abort` por defecto, también si el valor
no se reconoce, `unload`, `ignore`); URL de `GIMG_OLLAMA_URL`, si no `engine.ollamaUrl` (campo nuevo del esquema), si no `http://localhost:11434`; solo `http`/`https` (`engine.ollama_url`),
sin proxy. `GET /api/ps` con 2 s; servicio apagado, lento, error HTTP, JSON inválido, sin `models` o con entradas raras = nada cargado; solo cuentan los `size` numéricos > 0 (un
booleano o una cadena no). `unload` hace `POST /api/generate` y `/api/embed` con `keep_alive: 0` por modelo (10 s) y vuelve a mirar hasta 15 s cada 1 s (la descarga
es asíncrona, como en `generar.sh`); si siguen cargados, `engine.ollama_loaded` con `models` y `hint` (`ollama stop <m>; …`). (4) *Vigilante* (`_on_tick`): `MemAvailable` <
`watchMemoryMb` (estricto, sin umbral no vigila) o «reported free 0.00 MB» en lo nuevo del log (se lee desde la última posición, con el final de la lectura anterior por si la
frase queda cortada) → mata el grupo y lanza `EngineError`. (5) `EngineError` gana `code` y `params` opcionales: el worker guarda ese código (`engine.watch_memory`,
`engine.driver_no_memory`) en vez de `engine.failed`, para que el motivo salga traducido; `message` sigue siendo el texto en inglés. (6) `min_free_mb` es el mínimo de
todas las lecturas del intento, la previa incluida; el registro lo escribe solo si el intento acaba bien: **pendiente leve**, un intento que falla no lo guarda (el `EngineError` no lo lleva).
(7) Los tests del motor y del worker con `sdcpp` fijan `GIMG_MEMINFO` y una URL de Ollama sin servicio (`protections_off_env`); los de Ollama usan un `http.server` propio.

*Hecho en F2.4* (`gimg/engine_sdcpp.py`, `gimg/png.py`, `gimg/queue.py`, `gimg/worker.py`, `gimg/log.py`, `tests/test_progress.py`, `tests/test_png.py`): progreso, vista previa, registro D34 y chunk del PNG.
**Decisiones:** (1) *Progreso:* `parse_progress` lee la barra de pasos del log real (`\r` entre barras, `\x1b[K` detrás de cada una; `s/it` o `it/s`). Una barra solo cuenta con un
terminador detrás (`\x1b`, `\r` o `\n`): una cortada por la lectura (`ETA 02:1`) se guarda en `_Run.bar_carry` y se lee entera en el pulso siguiente. Solo valen las
barras anteriores a «sampling completed» (la del VAE por teselas, `1/36`, viene después); entre ellas las de total = pasos del job, y si ninguna, las del total de la primera;
gana la última. `etaS` sale de `mm:ss` o `hh:mm:ss`, `None` en la última barra (no lleva ETA). (2) *Enganche:* `EngineJob.on_progress` (callback; el motor falso no lo llama); el worker
lo apunta a `queue.set_progress(id, progress)`, que valida la forma (`queue.bad_progress`), exige entrada `running` (`queue.not_running`) y no reescribe el archivo si no cambia; el motor
solo llama cuando cambia `(step, steps)` e ignora cualquier excepción del callback. `queue.finish` y la recuperación a `queued` quitan `progress` y `preview`. (3) *Vista previa:* el worker
guarda en la entrada `preview` (ruta absoluta de `Engine.preview_path(salida)`; `None` en el motor falso) antes de generar con `queue.set_preview`; el archivo aparece cuando `sd-cli` lo escribe
y se borra con el intento (F2.2). `queue list` pinta `progress` y `preview` solo de una entrada `running` (`3/6 · ETA 1:16`; `vista previa: <ruta>` solo si el archivo existe). No hay `queue show`; servirla es de F4.
(4) *Registro (D34):* `app.image.model_files` (`{"diffusion","text","vae"}` con el nombre del archivo), `app.image.backend` (`cpu` si los args traen `--backend` con `cpu` o `diffusion=cpu`, si no `vulkan`: la única GPU de
la release; `--max-vram` va en el `command`), `app.image.threads` (el último `-t`), `app.image.draft` (`False`; F2.7 lo pone), `app.image.compose` (se omite mientras sea `None`; F2.8),
`app.image.command`. **`app.image.load_ms` no se añade:** el tiempo de carga ya es `app.load_ms` (nombre de opt-ai); duplicarlo rompería «un dato, un sitio». El motor falso solo escribe `draft`. El intento
(`orders.add_attempt`) gana `command`, `modelFiles` y `log` (`attempts/q<id>.log`, solo si se conservó); el esquema de pedidos no describe los intentos, no hubo que tocarlo. `EngineResult` gana
`model_files`, `backend`, `threads`, `draft`, `compose` y `params` (pasos, cfg y sampler efectivos: los del job o los del modelo). (5) *Chunk del PNG:* `gimg/png.py` (`png_bytes` se movió ahí y `engine`
lo reexporta; `read_text_chunks` lee `tEXt`, `zTXt` e `iTXt`, `add_text_chunk` escribe `tEXt` si el texto cabe en Latin-1 sin NUL y si no `iTXt` en UTF-8, sustituye la misma clave, verifica
firma, longitudes y CRC y escribe con archivo temporal + `os.replace`). Lo escribe el **worker**, clave `gimg`, sobre el PNG pendiente antes de moverlo (así vale para todos los motores y se escribe
una vez): JSON con `project`, `key`, `profile`, `seed`, `prompt`, `model`, `width`, `height`, `steps`, `cfg`, `sampler` (efectivos), `references` (solo nombres de archivo) y `engineVersion`. Si no se puede, el
intento sigue sin él y sale una línea por stderr. **Pendiente en F2.8:** `gimg compose` debe conservar el chunk (`read_text_chunks` ya está). **Pendiente leve:** `app.image.steps`/`cfg` del registro siguen siendo los del
intento (pueden faltar si los pone el modelo), mientras el PNG lleva los efectivos.

**`instalar.sh`** (raíz del repo, bash, `set -euo pipefail`). Sin argumentos instala el motor y el conjunto rápido (~7 GB, D5);
`--with flux3-klein-q8` añade el de calidad; `--only-cli` solo el lanzador. Pasos: 1) Python ≥ 3.10; 2) `gimg` en `~/.local/bin`
(script que hace `exec python3 -m gimg` desde el repo; avisa si `~/.local/bin` no está en `PATH`); 3) release fija de
stable-diffusion.cpp (`master-1000-95ff762`, Linux Vulkan) a `<datos>/engine/<release>/`, con sha256 del zip; 4) cada archivo del
catálogo con `curl -L -C -` y `sha256sum -c`, nunca sobrescribe uno que ya cuadra; con `--models-from <carpeta>` (p. ej. la
de Tarkor) enlaza los archivos que ya hay en la máquina en vez de descargarlos, tras comprobar su sha256 (D5: un juego por
máquina); 5) escribe `"engine": "sdcpp"` en
`<config>/config.json` (D36); 6) `gimg doctor`. Versiones y sumas viven solo en `gimg/models.json` y en una variable del script
(un dato, un sitio). **`gimg doctor`** dice, con la orden que lo arregla: binario y librerías, modelos instalados por id, ffmpeg y
rsvg-convert, fuentes que nombran las plantillas de los proyectos registrados (`fc-list`), memoria libre ahora y perfil de
máquina activo.

*Hecho en F2.5* (`instalar.sh`, `gimg/doctor.py`, `tests/test_doctor.py`, `tests/test_instalar.py`): **Decisiones:** (1) *Motor fijo:* el asset es
`sd-master-95ff762-bin-Linux-Ubuntu-24.04-x86_64-vulkan.zip` (37 MB, el mismo `sd-cli` de la Deck) y su sha256 `5af606a8…dad1` coincide con el
`digest` que publica GitHub y con el zip descargado a un scratchpad. Asset y suma viven en **una** variable del script, `SD_ZIP="<asset> <sha256>"`; la release no se
repite: el script la lee de `engine_sdcpp.RELEASE` y un test casa el hash corto del asset con ella. "Motor ya instalado" = `sd-cli` ejecutable y
`<datos>/engine/<release>/.zip-sha256` igual a la suma fijada (se extrae en una carpeta temporal y se mueve, así una descarga rota no deja un motor a medias).
(2) *Catálogo:* `installDefault: true` (esquema, opcional) marca lo que `instalar.sh` baja sin `--with` y lo que `doctor` exige (hoy `flux2-klein-4b-q8`; así el
conjunto rápido vive solo en `gimg/models.json`). `GIMG_CATALOG` apunta `load_catalog()` a otro archivo (hueco de test: el script y el doctor lo leen en procesos
propios). (3) *`instalar.sh`:* las carpetas salen de `gimg.paths` por `python3 -c` (sin reimplementar el XDG); cada archivo va a `<archivo>.part` con `curl -fL -C -`,
se comprueba con `sha256sum -c` (o `shasum -a 256 -c`) y solo entonces se renombra (una descarga con suma errónea se borra); uno que ya cuadra no se toca, uno que no cuadra se sustituye al final, nunca antes de tener el nuevo (y se dice); el motor viejo se aparta a `.old.<pid>` hasta mover el nuevo; con `--models-from` se busca
`<carpeta>/<nombre>` y `<carpeta>/<tipo>/<nombre>`, se enlaza solo si la suma cuadra y si no se descarga; `--dry-run` no hashea (solo mira si el destino existe) ni
llama a `curl`. Mensajes es/en según `GIMG_LANG`/`LANG`. No hay `--skip-engine`: los tests usan un motor ya instalado (marca) y un `curl` falso. (4) *`gimg doctor`:*
`doctor.run(verify, ollama_url)` devuelve `Check(id, status, …)` con la orden que arregla cada cosa; lo del motor real (binario, `libggml*`, modelo por defecto, Ollama
cargado) es `fail` con `engine: sdcpp` y solo `warn` con `fake` (D36: un clon sin instalar no está roto); un modelo a medias o con tamaño distinto es `fail` siempre. El
tamaño se compara con `sizeMb` (±1 MB); `--verify` suma el sha256. `ffmpeg` y `rsvg-convert` faltantes son `fail` con los paquetes de apt y pacman (D28: se
comprueban, no se instalan). Código de salida 1 con algún `fail`; `--json` da `{"ok", "checks": [{id, status, message, fix}]}`. (5) *Flatpak (decisión de la nota de
«Pendiente»):* **no se ignora el XDG**, `XDG_DATA_HOME` manda aunque apunte a `~/.var/app/…`; `doctor` avisa (`warn`) si `XDG_DATA_HOME` o `XDG_CONFIG_HOME` contienen
`/.var/app/` y la variable `GIMG_*_HOME` correspondiente no está fijada, y dice la línea `export GIMG_DATA_HOME="$HOME/.local/share/gimg"` (o `GIMG_CONFIG_HOME`) para que
todas las terminales vean las mismas carpetas y modelos. **Queda:** las fuentes de las plantillas con `fc-list` (F2.8, cuando existan las plantillas); el `--dry-run`
de la descarga real del zip y la instalación de verdad, **manual en la Deck** (la persona corre `./instalar.sh` y `gimg doctor`; hasta entonces el zip solo está
comprobado por suma). *Hecho el 2026-10-27 en la Deck (agente, con permiso de la persona):* `instalar.sh --models-from <modelos de Tarkor>` bajó el zip (37 MB),
enlazó los tres archivos del modelo rápido tras comprobar su sha256 y escribió `engine: sdcpp`; `gimg doctor --verify` en verde salvo Ollama con modelos
cargados. El aviso de flatpak salió y se resolvió con `GIMG_DATA_HOME`/`GIMG_CONFIG_HOME`.

*Hecho en F2.6* (`examples/<proyecto>/galivelop-images.json`, `examples/<proyecto>/orders/r1-og.json`, `.gitignore`, `tests/test_examples.py`): los
**siete** proyectos del ajuste del 2026-10-26, no cuatro. **Decisiones:** (1) *Perfiles:* los de generación de la tabla de formatos que lista cada proyecto
(`og`, `social`, `square`, `wide`, `banner`; `portrait` 896×1152 y `header` 1536×512, las medidas que r5 ya corrió en la Deck, en vez de 768×960 y 1280×448),
todos con 6 pasos, cfg 1, euler y `flux2-klein-4b-q8`; `avatar` e `icon` son solo composición y entran con `compose` en F2.8; `targetWidth`/`targetHeight` y
`draft` también quedan para F2.7/F2.8. (2) *Sin `style`:* los prompts del piloto llevan el estilo dentro y `attempt_specs` pegaría `, <style>` al final, con lo
que r1 no daría lo mismo; el `style` por perfil se decide en F2.10 con lo aprendido en r2. (3) *Pedido r1:* clave `fondos/r1`, perfil `og`, `prompt` =
`prompts/og.txt` sin el salto final (el log de r1 enseña que `generar.sh` tampoco lo pasó), `seed` 3 y `count` 2 (semillas 3 y 4, consecutivas como en
`ronda.sh r1`). (4) *Entrega:* `entrega/` y el manifiesto `galivelop-images.manifest.json` de los ejemplos fuera de git (D35: sin las imágenes, el manifiesto
solo apuntaría a archivos ausentes). (5) *Test:* registra cada ejemplo en carpetas temporales, envía el pedido y comprueba que `attempt_specs` da exactamente
las semillas 3 y 4, el prompt de `og.txt` y 1280×640 a 6 pasos. **Hecho en la Deck el 2026-10-27 (agente, con la persona autorizando la generación):** `gimg project add
examples/<p>` y `gimg order submit <p> examples/<p>/orders/r1-og.json` para los siete, `gimg work` sobre los 14 intentos (~43 min) y comparación con
`piloto/r1/`: **14/14 píxel a píxel iguales** (`ffmpeg -f md5`; los bytes difieren solo por el `tEXt` que añade `gimg`). Las dos columnas están en
`r1-fondos.md`. Diferencia conocida frente a `generar.sh`: `gimg` añade `--preview proj --preview-interval 1 --preview-path …`; `-t` no aparece porque
`steam-deck.json` no fija hilos. La imagen no cambia, que es justo lo que medía la comparación; los tiempos salen 0-7 s más lentos en cuatro proyectos por
la caché de disco tras descargar Ollama, no por el motor. CI de GitHub sin cuota el 2026-10-27: los pasos del CI (`comprobar.yml`: check y `pre-commit` de `main` sobre el rango) reproducidos en local sobre `370cf91`, en verde; comprobado solo en local a petición de la persona.

*Hecho en F2.7 (a)* (`gimg/orders.py`, `queue.py`, `worker.py`, `engine.py`, `engine_sdcpp.py`, `delivery.py`, `projects.py`, `cli.py`, esquemas `project-config` y `order`, `locales/`, `tests/test_draft.py`): borradores (D32). **Decisiones:**
(1) *Perfil:* `draft` `{model?, steps?, scale?}` (`scale` 0.1-1); `load_config` comprueba `draft.model` contra el catálogo. (2) *Pedido:* `draft` booleano (por defecto false), guardado en `orders.submit`.
(3) *`orders.draft_params`:* sin `draft` en el perfil, lados × 0,5, 8 pasos y mismo modelo; con él, `scale` (o 1), `steps` y `model` (o los que ya había); cada lado =
`max(64, round(lado × scale / 64) × 64)`; cfg y sampler no cambian. (4) *`attempt_specs(..., draft=None)`:* `None` usa el del pedido; cada spec lleva `draft`; el orden es perfil, pedido,
`params` de la llamada, borrador, y un `steps` explícito de la llamada gana al del borrador; los límites corren después, en `queue.enqueue`. (5) *Cola y trabajador:* la entrada guarda `draft`
(las antiguas, sin la clave, no lo son); `EngineJob.draft` y `EngineResult.draft` (el registro ya lo lee en `app.image.draft`); el chunk `gimg` del PNG y el intento llevan `draft: true`
solo si lo es. (6) *No elegible:* `orders.choose` lanza `order.choose_draft` y `delivery.choose` no prepara la entrega; marcar y deshacer no cambian. (7) *CLI:* `--draft` en
`order submit` y `attempt new`; `queue list` y `order show` marcan los borradores.
**Queda:** (b) `initImage`/`strength`. **Arreglos de la revisión de `a814e5b`:** la estimación del tiempo filtra por borrador (`app.image.draft`; una línea sin la clave no lo es); `attempt new` acepta `--draft`/`--no-draft` (sin opción manda el `draft` del pedido); `order submit --draft` escribe `draft: true` en el pedido, así que persiste; `app.image.draft` del registro sale de la entrada y no del motor (un borrador fallido también queda marcado; `draft` desaparece de `EngineJob` y `EngineResult`); `draft_params` redondea medio hacia arriba y con `scale` ausente o 1 no toca los lados; una sola regla de elegibilidad, `orders.check_choosable`, usada por `orders.choose` y `delivery.choose`.

*Hecho en F2.7 (b)* (`gimg/orders.py`, `queue.py`, `worker.py`, `engine.py`, `engine_sdcpp.py`, `models.py`, `models.json`, esquemas `order` y `models`, `cli.py`, `locales/`, `tests/test_img2img.py`): img2img. (1) *Pedido:* `initImage` (`relativePath`, D25) y `strength` (0-1); el esquema declara `dependentRequired: {strength: [initImage]}` (el validador lo implementa; `orders.submit` da `order.invalid`) y `submit` guarda ambos (`None` si faltan; al reenviar se sustituyen). (2) `attempt_specs` los copia, `queue.enqueue` los guarda (las entradas antiguas, sin la clave, se leen con `.get`) y `add_attempt` los guarda siempre en el intento (pedido, entrada e intento llevan las dos claves, `None` si faltan; lo ya guardado sin ellas se lee con `.get`). (3) *Trabajador:* resuelve `initImage` con `paths.inside` (archivo, o `worker.init_image_missing`); `EngineJob.init_image`/`strength`; el chunk `gimg` lleva `initImage` (solo el nombre) y `strength` solo con imagen inicial; un ayudante `_inside_file` sirve a referencias e imagen inicial. (4) *Motor:* tras los `-r`, `-i <init>` y `--strength <s>` (si hay) y luego `initImageArgs` del catálogo (`models.resolve`; `flux3-klein-q8`: `--extra-sample-args strength_as_noise_level=true`; `flux2`: ninguno). (5) *CLI:* sin opciones nuevas; `order show` imprime `cli.out.order_init` solo con imagen inicial. Cierra F2.7. *Arreglos de la revisión de `508750d`:* el registro lleva `app.image.initImage` (nombre) y `app.image.strength` y las estimaciones (`log.estimate`, `queue.estimate_for`) agrupan por img2img; el manifiesto de la elegida copia `initImage`/`strength` si los hay; `dependentRequired` en el validador; test real de una cola antigua sin las claves.

**Configuración del proyecto** (cambios en `project-config.schema.json`). El perfil añade: `targetWidth`/`targetHeight`
(tamaño de destino; si faltan, los de generación), `draft` (`{"model"?, "steps"?, "scale"?}`, D32) y `compose`
(`{"template": <ruta relativa .svg>, "fields": ["title", "subtitle"], "logo"?: <ruta relativa .svg>, "fonts"?: ["Sora", "Inter"],
"fit": "cover"|"contain", "lut"?: <ruta .cube>}`). `width`×`height` de generación son múltiplos de 64 (`multipleOf`, leve pendiente de
F0; lo que exija cada modelo queda por confirmar) y respetan `maxPixels`; el recorte y la escala al destino los hace la
composición (`fit: cover` recorta centrado; con `fit: contain` el fondo lo da la plantilla). Un perfil sin `compose` entrega la
imagen cruda escalada al destino. **Pedido** (`order.schema.json`): `text` (objeto de cadenas ≤ 200 caracteres, solo las claves de
`compose.fields`, escapadas como XML al sustituir), `draft` (bool) e `initImage`/`strength` (img2img, ruta relativa guardada por D25).
**Composición** (`gimg/compose.py`): 1) copia de la plantilla con los huecos sustituidos (`{{logo}}` → `href` al SVG del logo,
dentro del proyecto); 2) `rsvg-convert -w <target> -h <target>` → capa RGBA; 3) `ffmpeg -i raw.png -i capa.png -filter_complex
"[0]scale=…,crop=…[b];[b][1]overlay" out.png`; 4) `gimg compose <proyecto> <key> <perfil> [<intento>] [--text k=v…]` recompone
sin generar. Las fuentes las resuelve fontconfig en la máquina (Sora, Inter, Cormorant Garamond, DM Sans son OFL: se instalan en
`~/.local/share/fonts`, lo dice `gimg doctor`); si `rsvg-convert` acepta `@font-face` con `url()` local *(suposición, comprobar)* la
plantilla puede llevar las suyas.

### F2.8 en detalle (composición, D28)

Tres encargos en serie (E1 núcleo, E2 integración, E3 frente); cada uno deja el check en verde y sus locales es/en.

**Decisiones de F2.8** (tomadas por el agente con la autorización de la bitácora; la persona puede revertirlas):
1. `piezas.json` de developer, image-generator y voice-generator (`cuadrado`, `vertical`, `cabecera`): se decide en F2.10, cuando los ejemplos ganen `compose`; en F2.8 los ejemplos no cambian.
2. `avatar`/`icon` (solo composición, sin modelo) quedan fuera de F2.8 (F2.10/F2.12): hoy `width`/`height` son obligatorios y todo pasa por la cola.
3. `examples/<proyecto>/` no gana `compose`, plantillas ni logos en F2.8; en F2.8 solo la plantilla mínima de los tests. Ojo para F2.10: `piezas.json` apunta a `docs/marcas/...` fuera de la raíz de cada ejemplo (D25 lo rechaza); los logos tendrían que copiarse dentro.
4. Sin partir líneas: sustitución literal, una línea por campo (una plantilla puede usar `title1`/`title2`). Un `compose.wrap` declarado se decide en F2.10 con r4.
5. `gimg compose --text k=v` se guarda en el pedido (`orders.set_text`): los intentos siguientes y la galería usan el texto nuevo.
6. Fallo de composición (sin ffmpeg, plantilla rota…): el intento queda `done` con la cruda como `image`, `composeError={code, params}` y no elegible (`order.choose_uncomposed`); nunca se pierde la generación. `gimg compose` lo arregla después.
7. `gimg doctor`: fuentes que faltan son `warn`, no `fail`.
8. `lut` no entra en el esquema (es de F2.11; sin aplicarse sería un dato ignorado en silencio).
9. Los borradores también se componen (baratos, sirven de vista previa); siguen sin poder elegirse.
10. `{{logo}}` se sustituye por un data URI `data:image/svg+xml;base64,…` (como `componer.py`): rsvg no resuelve rutas fuera de la carpeta del SVG y el SVG sustituido se escribe en una carpeta temporal vacía, así rsvg no lee nada más del disco (D25 gratis; sin `--unlimited`).

**1. Flujo**
- Worker (`gimg/worker.py::_generate`): el motor escribe `.pending-<e>.png` y el chunk `gimg` se añade como hoy. Luego `plan = compose.plan_for(profile_cfg, *png.size(tmp))` con el perfil leído en ese momento (como los límites).
  - `plan is None` (sin `compose` y sin destino, o destino igual al tamaño de la cruda): todo sigue igual (`q<e>.png`, sin cruda aparte, sin ffmpeg). r1 y los tests actuales no cambian.
  - Con plan: (a) `os.replace(tmp, q<e>.raw.png)` (la cruda a salvo antes que nada); (b) `compose.render(...)` → `q<e>.png`; (c) `add_attempt` con `raw="attempts/q<e>.raw.png"` y `compose={template, logo, fit, targetWidth, targetHeight, text}`.
  - Si `render` lanza cualquier `GimgError` (`compose.*`, `path.*`, `png.*`): intento con `image=attempts/q<e>.raw.png` y `composeError`, entrada `done`, línea `worker.compose_failed` por stderr.
  - `state["final"]` limpia también la cruda si falla `add_attempt`.
- Sin `compose` pero con destino distinto: la cruda se escala con ffmpeg (fit `cover`). Sin ffmpeg, mismo camino de `composeError` (`compose.tool_missing`).
- Registro: quitar `EngineResult.compose` (no es cosa del motor; ajustar `tests/test_progress.py`). `log.record_for(..., compose=None, compose_error=None)` escribe `app.image.compose` (ruta de la plantilla) y `app.image.compose_error` (código).
- Intento (`orders.add_attempt`): guarda `raw`, `compose` y `composeError` solo si tienen el tipo correcto. Nuevas: `orders.raw_image_name(entry_id)`; `orders.raw_image(project, key, profile, attempt) -> Path` (`attempt["raw"]` o `image`); `orders.set_composed(project, key, profile, attempt_id, compose)` con cerrojo: pone `image` en la compuesta, guarda `raw` y `compose`, quita `composeError`.
- Delivery: entrega `image` (ya la compuesta), sin cambio; el manifiesto copia `compose` si existe.
- `queue._clean_pending` borra también `.pending-<e>.compose.png`.
- Carpeta temporal: `tempfile.TemporaryDirectory(dir=<attempts>, prefix=".compose-")` (mismo sistema de archivos para `os.replace`).
- Chunk: `render` lee el `gimg` de la cruda (`png.read_text_chunks`), añade `"compose": {...}` y lo escribe en la compuesta con `png.add_text_chunk`; si no puede, línea por stderr y sigue. ffmpeg con `-map_metadata -1`.

**2. Esquemas** (el validador propio admite `additionalProperties` como esquema, `propertyNames`, `maxLength`, `maxItems`, `enum`, `pattern` con lookahead, `dependentRequired`, `$ref` con otras claves; no `multipleOf`, `uniqueItems`, `not`, `maxProperties`, `anyOf`).
- `project-config.schema.json`, `$defs/profile`: `targetWidth`/`targetHeight` enteros 16-4096 con `dependentRequired` en ambos sentidos; `compose` con `additionalProperties:false`, `required:[template]`: `template` y `logo` → `$defs/svgPath` (relativePath + `\.svg$`); `fields`: array de `fieldName` (`^(?!logo$)[a-z][a-zA-Z0-9]*$`, maxLength 40), maxItems 10; `fonts`: array de cadenas 1-100 sin controles, maxItems 10; `fit`: enum `cover|contain`, por defecto `cover`.
- `order.schema.json`: `text` objeto con `propertyNames` = `fieldName` y `additionalProperties: {type:string, maxLength:200, pattern:"^[^\\u0000-\\u001f\\u007f]*$"}`.
- Cruce en `orders.submit`: las claves de `text` tienen que estar en `compose.fields` del perfil; si no, `order.text_unknown_field` {field, profile, fields}. `submit` guarda `text` (`{}` si falta); `attempt_specs`, `queue.enqueue` y la entrada lo copian (`.get` en entradas antiguas). Un campo que falta se sustituye por `""`.

**3. `gimg/compose.py`** (stdlib; errores `GimgError("compose.*")`)
- `TIMEOUT_S = 120`, `MAX_SVG_BYTES = 5_000_000`.
- `target_size(profile_cfg) -> (w, h)`; `plan_for(profile_cfg, raw_w, raw_h) -> dict | None`.
- `fit_geometry(src_w, src_h, dst_w, dst_h, fit) -> (scale_w, scale_h, x, y)`, enteros. cover: escala por el lado que manda con redondeo hacia arriba y recorte centrado `(sw-W)//2`; og 1280×640→1200×630 da `(1260,630,30,0)`; wide 1280×768→1200×675 da `(1200,720,0,22)`; square 1024→1080 da `(1080,1080,0,0)`. contain: escala hacia abajo y `pad` centrado.
- `xml_escape(s)`: `& < > " '`. `substitute(svg_text, values) -> str`: una sola pasada con `re.sub(r"\{\{([A-Za-z][A-Za-z0-9]*)\}\}")` (un valor que contenga `{{logo}}` no se vuelve a expandir); hueco desconocido → `compose.field_unknown` {field}.
- `resolve_assets(project_root, compose_cfg) -> (template_path, logo_path|None)`: `paths.inside` + `is_file` (`compose.template_missing`/`compose.logo_missing` {path}; los `path.*` de `PathError` ya existen) + tope (`compose.svg_too_big`). Plantilla con `{{logo}}` sin `compose.logo` → `compose.no_logo`.
- `rsvg_argv(svg, out, w, h)` = `["rsvg-convert","-w",W,"-h",H,"-o",out,svg]`.
- `ffmpeg_argv(raw, layer|None, out, geom, fit)` = `["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",raw,("-i",layer),"-filter_complex",F,"-map","[out]","-frames:v","1","-update","1","-map_metadata","-1",out]`. F cover: `[0:v]scale=SW:SH:flags=lanczos,crop=W:H:X:Y[b];[b][1:v]overlay=0:0:format=auto,format=rgb24[out]`; contain: `pad=W:H:X:Y:color=black@0` y `format=rgba` (la plantilla pinta las bandas); sin capa, lo mismo sin overlay.
- `_run(argv, tool)`: `subprocess.run(capture_output, stdin=DEVNULL, timeout=TIMEOUT_S)`; sin herramienta → `compose.tool_missing` {tool}; por tiempo → `compose.timeout` {tool, seconds}; salida ≠ 0 → `compose.tool_failed` {tool, reason: última línea de stderr ≤ 300}.
- `render(project, profile_cfg, raw_path, out_path, text) -> dict` (la info `compose` del intento): `resolve_assets`, `substitute`, rsvg a la capa, ffmpeg, chunk, `os.replace`.
- `recompose(project, key, profile, attempt_id=None, text=None) -> dict` (E3): intento por defecto el elegido, si no el último (id más alto); sin `raw` (anterior a F2.8) copia `image` a `<stem>.raw.png`; con `text`, `orders.set_text` lo fusiona en el pedido; `render`, `orders.set_composed`, y si es el elegido `delivery.choose(...)` del mismo id (vuelve a entregar y actualiza el manifiesto). Perfil sin nada que hacer → `compose.nothing_to_do` {profile}.
- `png.size(path) -> (w, h)` nuevo en `gimg/png.py`: lee IHDR o lanza `png.invalid`.

**4. CLI** (`gimg/cli.py`, E3): `leaf(top, "compose", "cli.cmd.compose", project, okey, oprofile, arg("attempt", ..., nargs="?", type=int), opt("--text", "cli.arg.text_kv", action="append", default=[]))`. `k=v` se parte por el primer `=`; mal formado → `cli.text_invalid` {value}. `--json` devuelve el intento. Claves: `cli.cmd.compose`, `cli.arg.attempt_optional`, `cli.arg.text_kv`, `cli.out.composed` {id, image}, `cli.out.composed_delivered` {id, path}, `cli.out.compose_error_mark` (en `order show`), `error.cli.text_invalid`, `error.order.text_unknown_field`, `error.order.choose_uncomposed`, `error.compose.*`, `worker.compose_failed`.

**5. `gimg doctor`** (E3): ffmpeg y rsvg-convert ya los comprueba `_tools()`. Añadir `_fonts()` tras `_tools` en `doctor.run`: recorre `projects.list_projects()`, `load_config` de cada uno (si falla, `warn doctor.fonts.project_error` {project, message}); junta los `compose.fonts`; una sola llamada `fc-list --format '%{family}\n'`, familias separadas por coma, comparación sin mayúsculas. Falta una → `warn doctor.fonts.missing` {font, projects} con `doctor.fix.fonts` (copiar a `~/.local/share/fonts` y `fc-cache -f`). Sin `fc-list` → `warn doctor.fonts.no_fc_list`; sin fuentes declaradas → `ok doctor.fonts.none`.

**6. Tests** (cada uno por `rojo-sin-arreglo.sh`; patrón `EN_CI` + `skipUnless` de `tests/test_pilot_scripts.py`, con `color_png`):
- `tests/test_compose.py` sin herramientas: `fit_geometry` (og, wide, square, contain, tamaños ≤ 0); `substitute` (escape de `<&"'`, una sola pasada, hueco desconocido con motivo, `{{logo}}` data URI); guardia de rutas de plantilla y logo (`../`, absoluta, `~`, `\n`, `\x00`, enlace que sale, no es archivo) con su código; `rsvg_argv`/`ffmpeg_argv` exactos (cover, contain, sin capa); `plan_for` (None cuando no hay nada que hacer); `tool_missing` con `PATH` vacío.
- `tests/test_compose.py` con herramientas: plantilla mínima con un rect y `{{title}}` con `&<` → salida 1200×630; píxeles con `ffmpeg -f rawvideo -pix_fmt rgb24 -` (cover: fondo de dos colores, la franja recortada no aparece; logo de color conocido en su sitio); el chunk `gimg` sigue en la compuesta con `compose`; `tool_failed` con SVG roto, comprobando el motivo.
- `tests/test_schema.py`, `tests/test_orders.py`: `targetWidth` sin `targetHeight`, `fit` fuera del enum, campo `logo` reservado, `text` > 200 o con control, clave fuera de `fields`, `choose_uncomposed`.
- `tests/test_compose_worker.py` (base `QueueBase` + motor `fake`): sin compose igual que hoy (sin `.raw.png`); con compose y `PATH` vacío: `done`, cruda guardada, `composeError`, no elegible; con herramientas: `q<e>.raw.png` + `q<e>.png`, `app.image.compose` en el log, borrador compuesto.
- `tests/test_delivery.py`: manifiesto con `compose`. `tests/test_cli.py`: `gimg compose` sobre el elegido vuelve a entregar; `--text` mal formado; `--text` se guarda. `tests/test_doctor.py`: `fc-list` falso (con y sin «Sora»), proyecto roto. `tests/test_png.py`: `png.size`.

**7. Reparto**
- **E1 núcleo:** los dos esquemas, `png.size`, `gimg/compose.py` sin `recompose`, locales `error.compose.*`, tests de `test_compose.py`, `test_schema`, `test_png`. Hecho cuando `render` compone una cruda sintética a 1200×630 con chunk y lo que no necesita herramientas pasa sin ellas.
- **E2 integración:** `orders` (`text` en `submit`/`specs`, `set_text`, `raw_image_name`, `raw_image`, `add_attempt`, `set_composed`, `check_choosable`), `queue.enqueue`/`_clean_pending`, el camino del worker, `log.record_for` + quitar `EngineResult.compose` (y `test_progress`), manifiesto de `delivery`. Hecho cuando `test_compose_worker`, `test_orders`, `test_delivery` en verde; un perfil sin compose deja el disco igual que antes (test); el fallo de composición conserva la cruda.
- **E3 frente:** `compose.recompose`, `gimg compose`, marca en `order show`, `doctor._fonts`, locales, `test_cli`/`test_doctor`, y en `docs/plan.md` «Hecho en F2.8». Hecho cuando un cambio de título recompone el elegido y vuelve a entregar sin generar, y `gimg doctor` lista las fuentes.

*Hecho en E2* (`orders`, `queue`, `worker`, `log`, `delivery`, `engine`; `tests/test_compose_worker.py`, `test_orders`, `test_delivery`): frente al detalle, (1) `set_composed` no recibe rutas: la cruda es `raw` del intento o, sin ella, su `image` como `<stem>.raw.png`, y `image` pasa a ser la cruda sin `.raw` (`q3.raw.png` -> `q3.png`); (2) un intento con `composeError` y `raw` queda con `image` = `raw` (lo hace `add_attempt`, no el worker); (3) el worker vuelve a leer el perfil tras generar y trata un PNG ilegible o un perfil desaparecido como «nada que componer»; (4) `state["final"]` es una lista (cruda y compuesta); (5) `_clean_pending` borra las carpetas `.compose-*` de un worker muerto (no existe `.pending-<e>.compose.png`: el temporal lo gestiona `render`); (6) `record_for` recibe `compose` solo con éxito y `compose_error` solo con fallo; (7) un error que no sea `GimgError` en `render` sigue siendo `failed` y borra la cruda.

**Formatos del piloto** (perfiles compartidos por los cuatro proyectos; tamaños habituales de cada red en 2026, a comprobar al
publicar; generación ≤ 1 Mpx y múltiplo de 64, lo que cabe en la Deck según `maxPixels`):

| Perfil | Destino (px) | Generación (px) | Uso |
|---|---|---|---|
| `og` | 1200×630 | 1280×640, recorte centrado | og:image web; vista previa en LinkedIn, Discord y X |
| `social` | 1280×640 | 1280×640 | social preview de GitHub |
| `square` | 1080×1080 | 1024×1024, escala | publicación en Instagram y LinkedIn |
| `portrait` | 1080×1350 | 768×960, escala | Instagram 4:5 |
| `wide` | 1200×675 | 1280×768, recorte a 16:9 y escala | X |
| `header` | 1500×500 (X), 1584×396 (LinkedIn), 960×540 (Discord) | 1280×448, recorte y escala por destino | cabeceras |
| `banner` | 1600×640 | 1280×512, escala | portada en el Portal (Tarkor ya usa 1600×640) |
| `avatar` | 512×512 | sin modelo: solo composición (logo sobre fondo) o 512×512 generado | Discord, GitHub, favicon grande |
| `icon` | 180×180, 192×192, 512×512 | solo composición | apple-touch-icon y manifest |

El borrador de `og` es 640×320 a 8 pasos; con FLUX.3 un definitivo de 1280×640 cuesta ~25 % más que el 1280×512 medido (~60 min,
*suposición*).

### Estilos por proyecto

Reglas comunes, heredadas de `plantilla-prompt.md` de Tarkor: frases completas en positivo, sin prompt negativo (FLUX con cfg 1
lo ignora), sin palabras que no queremos ver (el modelo pinta lo que se nombra aunque se niegue), lo importante primero (el
párrafo de estilo final apenas pesa), «completely textless, no letters, no logos» siempre, y la **zona reservada** para texto o
logo descrita en el prompt («the left third is calm, out of focus and nearly empty») y, si no obedece, guiada con un boceto SVG
rasterizado como `initImage` (fuerza 0,85-0,97 con `strength_as_noise_level`, como los planos de Tarkor). El `style` de cada perfil
lleva la paleta en palabras, no en hexadecimales *(suposición: el modelo no respeta códigos hex; la ronda r2 lo mide)*. Los
colores de acento de cada proyecto salen de `Portal-Galivelop/src/data/proyectos/*.json`: Tarkor `#E0703A`, toVeriAI `#2F7A55`,
workflow `#3D6FD9`.

**Portal Galivelop** (marca paraguas; `examples/portal/`). *Propósito y tono:* «Taller independiente de software. Hacemos
reales los proyectos que parecen imposibles»; cercano, humilde, honesto con el estado real; no es un escaparate ni le mueve el
beneficio; se publica en es, gl y en. *Ética en imagen:* nada de «contrata nuestros servicios», venta, promesas infladas ni
gráficas de crecimiento; no se dice «encargo» ni «de pago». *Sí:* fondos oscuros `#06121c` con resplandor radial celeste y rejilla
de puntos (así es la web), luz y materia de taller en abstracto (vidrio, agua, luz celeste sobre azul profundo), los tres
proyectos como tres acentos (naranja, verde, azul) sobre el celeste, Galicia solo como luz y mar, nunca como postal. *No:*
gente en traje, apretones de manos, oficinas de banco de imágenes, cohetes, robots. *Paleta:* celeste `#1aa6df`, `#2BB3EA`,
`#0083c1`, blanco; oscuro `#06121c`, `#0c1d2b`, `#11283a`, borde `#1b3447`, texto `#eaf4fa` y `#9fb4c4`, enlace `#5cc8f2`; claro
`#f6fafd`, texto `#0a1a28`. *Tipografía (composición):* Sora 700 en títulos, Inter en texto; radios 18 y 10 px. *Logo:*
`public/marca/gv-logo.svg` (cuadrado rx 30, degradado `#2BB3EA → #0083C1`, monograma G+V blanco), tal cual. *Formatos:* `og`,
`banner`, `header` (Discord), `avatar`, `social`. *Primera ronda (huecos de la lectura):* 1) og:image por proyecto (3 piezas
1200×630: la portada de cada proyecto + logo GV + wordmark «Galivelop» con «Gali» en celeste); 2) avatar 512×512 y cabecera
960×540 de Discord (solo composición: logo sobre fondo con resplandor); 3) banners 1600×640 de las cinco líneas de trabajo (IA
local y responsable, mundos que viven solos, información verificable, del prototipo al producto, método con IA); 4) versión del
logo para fondo claro y wordmark exportado (SVG a mano, propuesta al repo, sin modelo); 5) cabecera de LinkedIn 1584×396.

**toVeriAI** (repo `VeriNews_AI`; `examples/toveriai/`). Se parte del kit visual v1.1: paleta, tipografía, forma y 20 prompts para
redes y banners ya escritos; aquí sus prompts se adaptan quitando el texto (lo pone la composición) y describiendo la zona
reservada. *Propósito y tono:* analiza noticias y da el IMI 0-100 por 7 o 9 dimensiones; «La verdad no es binaria»; sereno,
editorial, nada sensacionalista; «matices, no veredictos absolutos». *Ética en imagen:* nada de alarmismo, iconos de stop o
prohibido, lupas sobre prensa amarilla, rojo puro de error ni etiquetas «fake news»; la desinformación se cuenta con «claridad,
matiz, capas de lectura». *Sí:* papel cálido con textura sutil, tintas de acuarela que se rozan sin mezclarse (granate, ámbar,
verde), tiras y estratos de papel, línea fina (~1,3 px) sin relleno, mucho aire, sombras cálidas y suaves, solo modo claro. *No:*
`#000`, blanco puro de fondo, azules corporativos, degradados brillantes, neón, 3D, iconos flat genéricos, negritas, esquinas
muy redondeadas (radios 3-6 px; píldora solo en badges). *Paleta:* fondo `#F7F5F2`, tarjeta `#FDFCFB`, `#F0EDE8`, borde
`#E8E4DF`, texto `#1A1A1A`; verde `#2D6A4F` (único acento en piezas genéricas), `#52B788`, `#74C69D`, `#B7E4C7`; ámbar `#B5832A` y
granate `#9B2335` solo cuando la pieza habla de un nivel de credibilidad; hero `#1c3028 → #2D6A4F`. *Tipografía (composición):*
Cormorant Garamond 400 (nunca bold) en titulares y wordmark «to·Veri·AI» con tracking 0,08 em y «Veri» en `#2D6A4F`; DM Sans en
eyebrows (mayúsculas, tracking 0,28-0,32 em) y cuerpo. *Logo:* el wordmark se compone como texto; el símbolo (V de trazos
curvos verde y ámbar con constelación) solo existe en `frontend/public/favicon.png` 512×512: **falta el SVG** (D29; propuesta al
repo **[P]** quién lo vectoriza). *Formatos:* `og`, `square`, `portrait`, `wide`, `header`, `icon`. *Primera ronda (huecos):* 1) og:image
1200×630 (hoy apunta al favicon de 512): fondo «Entre dos tintas» del kit + wordmark + «La verdad no es binaria»; 2) `square`
1080×1080 «Cita tipográfica» (papel + frase del kit compuesta); 3) banner «El espectro» como `header` o `banner`; 4) `wide`
1200×675 de gancho para X («Esta noticia no es falsa. Tampoco del todo verdad.»); 5) apple-touch-icon y manifest desde el
símbolo (solo composición, cuando haya SVG).

**Galivelop-workflow** (`examples/galivelop-workflow/`). *Propósito y tono:* el flujo de trabajo con agentes de IA (plugin,
MIT); «Lo que no está subido no existe»; técnico, sobrio, pragmático, con crédito a las fuentes. *Ética en imagen:* nada que
sugiera autonomía total de la IA ni «magia»: el humano decide y revisa. *Sí:* la metáfora del **relevo** (un testigo que pasa de
mano en mano, hilos que se anudan y siguen), grafos de ramas y commits como trazas de luz, el sello o marca de revisión, un
cuaderno de bitácora; fondo oscuro `#0d1b2a` con rejilla tenue como los siete diagramas del Portal. *No:* robots, cerebros
luminosos, circuitos brillantes, lluvia de código, humanoides, manos de robot sobre teclados. *Paleta:* la de los diagramas:
fondo `#0d1b2a`, texto `#eef6fb` y `#8a9bb0`, acentos `#38b6e8`, `#f2b34a` (lo de Matt Pocock va en ámbar en los diagramas) y
`#4cc38a`; acento del Portal `#3D6FD9`. *Tipografía (composición):* Inter (800 en títulos, como los diagramas) y DejaVu Sans
Mono para lo que es código. *Logo:* **no existe** nada en el repo. Propuesta **[P]**: monograma «gw» en Inter 800 blanco sobre
cuadrado rx 30 con degradado `#3D6FD9 → #0d1b2a`, de la misma familia que `gv-logo.svg` (mismo cuadrado y radio, otro acento),
dibujado a mano como SVG. *Formatos:* `social`, `og`, `square`, `banner`, `avatar`. *Primera ronda (huecos):* 1) logo y avatar
512×512 [P]; 2) social preview de GitHub 1280×640; 3) og:image 1200×630 de su ficha en el Portal; 4) `square` 1080×1080 con el
lema «Lo que no está subido no existe» (tarjeta de cita: fondo abstracto + texto compuesto); 5) banner 1600×640 del relevo.

**Tarkor** (`examples/tarkor/`). *Propósito y tono:* RPG narrativo con IA local, de fantasía; «Un RPG narrativo donde el mundo
sigue adelante aunque tú te detengas»; en desarrollo. *Ética en imagen:* nada de interfaz de juego falsa ni promesas de fecha;
nada de «AAA genérico» (destellos, armaduras cromadas); el arte propio manda. *Sí:* el mundo del juego como fondo (Los Pilares
Rotos: torres de roca roja con puentes colgantes, la portada actual a 1600×640; hay 304 `.webp` de arte en
`public/proyectos/tarkor/arte/` que sirven de referencia `-r` con el modelo rápido), la luz que ganó en el banco de Tarkor
(«cine2»: sol bajo a contraluz, cielo ámbar, polvo encendido, borde de luz), paisajes sin criaturas (no hace falta el canon de
fauna para una pieza de marca). *No:* texto, personajes fuera del canon, estética de otro juego, oscuridad total. *Marca desde
cero, propuesta **[P]**:* paleta a partir del acento `#E0703A` y de la roca roja: tierra oscura `#1b0f0a`, roca `#8a3b1e`, ocre
`#c98a3a`, hueso `#efe3cf`, cielo ámbar `#f2b34a` *(suposición: medidos sobre `portada.webp` en la ronda r1)*; tipografía con
carácter para el wordmark «Tarkor» (una serif o display de fantasía, a elegir entre las OFL de Google Fonts **[P]**; Sora sería la
alternativa coherente con el Portal); símbolo: la silueta de los Pilares Rotos con un puente, en un trazo, dentro del mismo
cuadrado rx 30 de la familia (fondo `#E0703A → #8a3b1e`); el generador boceta 4-6 emblemas de 1024×1024 como inspiración y el
SVG se dibuja a mano (D29). *Formatos:* `banner`, `og`, `square`, `header` (Discord), `avatar`. *Primera ronda:* 1) bocetos del
emblema y SVG del símbolo [P]; 2) og:image 1200×630 con los Pilares Rotos + wordmark; 3) banner 1600×640 nuevo para el Portal y
cabecera 960×540 de Discord; 4) `square` 1080×1080 con el lema; 5) avatar 512×512.

**Herramientas del taller: generador de imágenes, generador de voces y galivelop-developer** (añadidas por la persona el
2026-10-26; `examples/<repo>/`; lectura en el registro, sección 3). *Común:* no tienen identidad visual ni están en el Portal,
son CLI locales y sus principios son IA local, nada residente y el humano revisa. Por eso entran **en la familia del Portal**
**[P]**: fondo `#06121c` con rejilla de puntos, Sora e Inter, y un logo en el mismo cuadrado rx 30 de `gv-logo.svg` con un
monograma y su acento. Acentos propuestos **[P]**, distintos de los del Portal y de los tres proyectos: imágenes violeta
`#8B5CF6`, voces frambuesa `#D9467A` y developer verde azulado `#2BB3A3`. *No:* robots, cerebros, rostros, personas reales
(voces: nada que sugiera clonar a alguien), «magia» de IA. *Formatos:* `social` (GitHub), `og`, `avatar`; el `banner` del
Portal solo si la persona decide presentarlas allí. *Metáforas* (de sus textos):

- **Imágenes:** marcos de cristal en fila, uno de ellos encendido (la cola y la elegida).
- **Voces:** una cinta de onda que se enrosca en una huella.
- **Developer:** un tronco de luz con una rama corta que sale y vuelve por un anillo de revisión.

*Primera ronda:* 1) logo SVG y avatar de cada una; 2) social preview 1280×640 de GitHub; 3) og 1200×630.

### Plan de pruebas de contenido

Como el banco de Tarkor (`banco.sh` y `resultados.md`): **semilla fija (3), una palanca por ronda, borrador y luego definitivo,
y veredicto «sí/no a ojo» de la persona.** Cada ronda es un archivo `docs/registros/contenido/rN-<tema>.md` con la tabla
(proyecto, clave, perfil, modelo, semilla, pasos, palanca, tiempo, memoria mínima, medida, veredicto) y las miniaturas (D35); los
pedidos de la ronda son los JSON de `examples/<proyecto>/orders/` enviados con `gimg order submit`. **Todo lo que corre en la
Deck es comprobación manual de la persona, nunca un test**; lo que se apunta es lo medido, no lo previsto. Criterios:

- *Objetivo* (`gimg measure`, D31): porcentaje de píxeles cerca de la paleta y YAVG/SATAVG dentro del rango que den las
  imágenes de marca existentes (`galivelop-portal.jpg`, el hero y `favicon.png` de toVeriAI, `gw-*.svg` rasterizados, `portada.webp`
  de Tarkor), medidas en r1 para fijar los umbrales; con referencias, mediana EMD Cb ≲ 6 y Cr ≲ 7,5 (lo de Tarkor, a revalidar
  por marca); contraste WCAG texto/zona reservada ≥ 4,5:1 (≥ 3:1 en titulares grandes).
- *Subjetivo:* la persona dice sí o no a cada pieza y, si no, qué palanca toca la ronda siguiente; una pieza «sí» pasa a
  definitivo; el estilo de un proyecto se da por bueno cuando 3 de sus piezas prioritarias son «sí» a la primera o segunda ronda.

| Ronda | Qué | Palanca | Coste en la Deck *(estimado)* |
|---|---|---|---|
| r0 humo | 1 fondo del Portal con `flux2-klein-4b-q8`, 1280×640, 6 pasos; se comprueban tiempo, `min_free_mb`, cancelar y la línea del registro | ninguna | ~3 min |
| r1 fondos | 4 proyectos × perfil `og` × 2 semillas (3 y 4), modelo rápido, prompt base de cada estilo; se calibran los umbrales de `measure` con las imágenes de marca | estilo base | 8 × ~3 min |
| r2 estilo | por proyecto, 3 variantes del `style` (paleta en palabras, con hexadecimales, con material y luz), misma semilla | el `style` del perfil | 12 × ~3 min |
| r3 borrador | la mejor pieza por proyecto: borrador FLUX.3 640×320 a 8 pasos y definitivo 1280×640 a 16; ¿coincide la composición? | modelo y tamaño | 4 × (~8 + ~60 min) |
| r4 composición | texto y logo sobre los definitivos de r3; legibilidad medida y a ojo; si la zona reservada no sale limpia, boceto SVG como `initImage` | plantilla y zona | sin modelo, o 4 borradores |
| r5 piezas | las 3-5 piezas prioritarias de cada proyecto en definitivo, con composición; propuestas a cada repo | ninguna (lo aprendido) | ~16 × ~60 min, en varias sesiones |

La LUT (D31) solo se hornea si r2 muestra que la paleta no se respeta con palabras. Entre rondas no se cambia más de una
cosa; una ronda que no cabe en una sesión se parte y lo hecho se apunta en el mismo registro.

**Ajuste del 2026-10-26** (la persona delega en el agente y pide las pruebas de concepto de todo antes de la interfaz):

- Las rondas van con los **siete proyectos** y como pruebas de concepto con `examples/pilot/`, no con `gimg`:
  - el motor real llega en F2.1-F2.5;
  - `compose` y `measure` se prueban con scripts del piloto que luego portan F2.8 y F2.9.
- **r2:** tres variantes del estilo por proyecto, sacadas de su biblia (`docs/marcas/<p>/biblia.md`, sección 7). Las de
  Portal y Tarkor corrigen el «no» de r1.
- **r3:**
  - borrador y definitivo con el modelo rápido en los siete;
  - FLUX.3 solo en un proyecto, para contestar si el borrador anticipa la composición.

  Las piezas publicables salen del modelo rápido mientras la licencia de FLUX.3 no esté confirmada.
- **r4 y r5:**
  - el logo elegido (`docs/marcas/README.md`), el texto y la medida, sobre los definitivos;
  - r5 con 3-4 piezas por proyecto.
- **Revisión:** todo resultado queda en `piloto/<ronda>/` con su página, y su registro va en
  `docs/registros/contenido/`. La persona revisa allí y, sin veredicto suyo, decide el agente y lo apunta.

### Pasos de F2

Pasos pequeños, cada uno con su commit y la bitácora al día; el orden lleva la primera ronda de contenido (F2.0) lo antes
posible.

| Paso | Qué | Comprobación |
|---|---|---|
| F2.0 | **Arranque [P]:** prompts de los cuatro estilos en `examples/<proyecto>/prompts/` y rondas r0 y r1 con el `generar.sh` de Tarkor (solo ejecutado, salida en `<datos>/pilot/`) | **Manual persona:** `docs/registros/contenido/r0-humo.md` y `r1-fondos.md`, con el log real de `sd-cli` guardado para F2.2-F2.4 |
| F2.1 | Catálogo `gimg/models.json` y su esquema; `model` del perfil validado contra el catálogo; `engine.*` nuevo en el perfil de máquina y `steam-deck.json` con FLUX.3 (D30) | Tests del esquema, del catálogo y de la resolución modelo + máquina |
| F2.2 | `engine_sdcpp.py`: argv, `LD_LIBRARY_PATH`, proceso en su grupo, tope, cancelar, código de salida, `EngineResult` con tiempos y `command` (D33, D34); `GIMG_ENGINE=sdcpp` y `config.json` (D36); `tests/fake_sd_cli.py` | Tests con el `sd-cli` falso: argv exacto, cancelar mata el grupo, tope, fallo con el motivo |
| F2.3 | Protecciones: memoria previa, vigilante, «reported free 0.00 MB», Ollama (`urllib`), `min_free_mb` | Tests con `/proc/meminfo` y Ollama simulados; cada fallo con su motivo |
| F2.4 | Progreso y vista previa: `progress` en la entrada de la cola, `queue list` lo pinta, `--preview proj`; registro ampliado (D34) y `attempts/q<id>.log`; los parámetros de generación también en un chunk `tEXt` del PNG del intento, que `gimg compose` conserva (`docs/interfaz/propuesta.md`, decisión nueva 2) | Tests del parseo y del formato del registro |
| F2.5 | `instalar.sh` y `gimg doctor` (lanzador, release fija y sha256, modelos del catálogo, `config.json`) | `bash -n`; test de `doctor` sobre carpetas falsas; **manual Deck:** instalar y `gimg doctor` en verde |
| F2.6 | Configuraciones y pedidos de ejemplo de los siete proyectos (`examples/<proyecto>/`), `.gitignore` de `entrega/`, con los prompts de F2.0; **r1 repetida con `gimg`** (mismos pedidos y semillas: debe dar lo mismo que con `generar.sh`) | `test_examples` valida los siete; **manual persona:** `r1-fondos.md` con las dos columnas |
| F2.7 | Borradores: `draft` del perfil, `--draft`, `draft: true` en el intento, no elegible (D32); `initImage`/`strength` | Tests de specs, límites y de que no se elige un borrador |
| F2.8 | Composición: `compose` en el perfil, `text` en el pedido, `gimg/compose.py`, `q<id>.raw.png` + `q<id>.png`, `gimg compose` (D28) | Tests con una plantilla mínima (sustitución y escape, guardia de rutas, recorte y escala; `skipUnless` ffmpeg y rsvg) |
| F2.9 | `gimg measure` (paleta, signalstats, EMD, contraste) (D31); calibración con las imágenes de marca | Tests con PNG sintéticos de color conocido; `skipUnless` ffmpeg |
| F2.10 | **Rondas r2-r4 en la Deck**; ajustes de estilo y plantillas que salgan | **Manual persona:** registros `r2-estilo.md`, `r3-borrador.md`, `r4-composicion.md` |
| F2.11 | LUT por marca solo si r2 lo pide (`compose.lut`, `gimg lut bake`); si no, se apunta para F5 | Tests del `.cube` generado; manual: `measure` antes y después |
| F2.12 | **Ronda r5** y propuestas `docs/propuestas/<proyecto>.md` (configuración, plantillas, logos SVG, piezas elegidas) | **Manual persona:** `r5-piezas.md`; cada propuesta enlaza su configuración de ejemplo |
| F2.13 | README es/en (instalación, motor real, composición, medida), CHANGELOG, versión 0.2.0, tabla de fases al día | Check en verde; `minVersion` de los ejemplos = 0.2.0 |

### Riesgos y no confirmado

- **Licencia de FLUX.3 Image Klein.** `investigacion-lora.md` de Tarkor dice *FLUX Kommunity License* (uso comercial gratis por
  debajo de 5 M USD anuales); no está confirmado en la fuente de BFL ni se sabe si cubre piezas de marca de un producto
  publicado (toVeriAI). Hasta confirmarlo **[P]**, las piezas que se publiquen salen del modelo rápido (klein 4B, Apache 2.0); FLUX.3
  solo para comparar. Qwen3 y los VAE son Apache 2.0; el Portal declara que no le mueve el beneficio, pero toVeriAI es un producto.
- **Tiempos.** ~49 min por definitivo 1280×512 con FLUX.3 en CPU (180 s/paso + 40 s de VAE); 1280×640 y 1024×1024 costarán más
  *(suposición: +25 % y +60 %)*. r3 y r5 suman ~20 h de Deck: varias sesiones, con la Deck sin juego ni Ollama. Con el modelo
  rápido todo cabe en una tarde.
- **Memoria.** FLUX.3 corrió con 4,4-6 GB libres de mínimo y abortó por el narrador (5,2 GB); `-r` con FLUX.3 no arrancó y dos
  `-r` no caben; `--max-vram vulkan0=6` bloqueó la Deck (nunca subirlo). Con `sd-cli` en marcha no se pasan el check ni los tests.
  `maxPixels` 1048576 por confirmar con FLUX.3 a 1024×1024 **(manual Deck)**.
- **Texto legible.** No se pide al modelo nunca; todo texto es composición. Depende de que las fuentes estén instaladas en la
  máquina (`gimg doctor` lo dice) y de que `rsvg-convert` las resuelva por fontconfig *(suposición)*. Componer con SVG o ffmpeg
  está **sin confirmar en Tarkor**: F2.8 es la primera vez.
- **Colores por hexadecimal.** *(suposición)* El modelo no respeta códigos hex; se mide en r2 y, si no, LUT (D31).
- **Borrador frente a definitivo.** Que 640×320 a 8 pasos anticipe la composición de 1280×640 a 16 no está probado (IMG-19a de
  Tarkor sin resolver); `--preview proj` para FLUX.3 tampoco. r3 lo decide; si no coincide, el borrador pasa a ser el modelo rápido.
- **Formato del progreso.** La línea de pasos de `sd-cli` se parsea del log `-v`; el formato exacto se confirma en r0 y el
  `sd-cli` falso lo imita.
- **Múltiplos de tamaño.** Lo que exige `sd-cli` por modelo (16 o 64) está por confirmar; el plan usa 64, lo que Tarkor usa.
- **Marcas sin material.** Tarkor y Galivelop-workflow parten de cero: lo propuesto arriba es un punto de partida para que la
  persona decida [P]; sin su decisión, su ronda r5 no empieza. El símbolo de toVeriAI necesita SVG antes de componerlo.
- **Sumas y URLs del catálogo.** Se toman de lo descargado en la Deck y la persona las verifica; sin red o con cuota de Hugging
  Face, `instalar.sh` reintenta con `-C -`.
- **Herramientas del CI.** ffmpeg y rsvg-convert se instalan con `apt` en `comprobar.yml`; si el CI no arranca (sin cuota), vale el
  check en local con la confirmación de la persona (`AGENTS.md`, «Relevos»).

## Pendiente

- Proponer al flujo (`gw-harvest`) una operación de imagen en `opt-ai/references/log-format.md` (D26).
