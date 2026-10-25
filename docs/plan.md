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
| D22 | Interfaz en **tres pantallas**: proyectos; pedidos de un proyecto (filtros por perfil y estado, cola visible); un pedido (galería con estados, notas por intento, retoque de prompt y parámetros, otra semilla o N seguidas, comparar dos lado a lado) | Todo lo de WMF más estados, cola y comparar |
| D23 | Repo `galivelop-image-generator`, orden **`gimg`**, configuración del proyecto en `galivelop-images.json` | Corto y sin choques habituales en Linux |
| D24 | Instalación con `git clone` + `instalar.sh` (pone `gimg` en `~/.local/bin`, descarga motor y modelos, D5); la configuración del proyecto declara la **versión mínima** del generador y `gimg` avisa si la instalada es más antigua; semver y CHANGELOG | Sin pip ni paquetes; un proyecto sabe si su configuración vale con lo instalado |
| D25 | **Solo escribe** en su carpeta de datos y en la carpeta de entrega de proyectos registrados; **solo lee** referencias dentro del proyecto; rechaza `..` y enlaces que salgan. API solo en localhost, Content-Type JSON y mismo Origin | Las rutas de un pedido vienen del proyecto |
| D26 | El registro es **JSONL en el formato de `opt-ai`** (`.claude/skills/opt-ai/references/log-format.md`), una línea por intento: `gen_ai.provider.name` = `stable-diffusion.cpp`, `gen_ai.request.model`, `app.task` = perfil, `app.machine_profile`, `app.duration_ms`, `app.load_ms`, `app.error`, y lo propio de la imagen bajo `app.image.*` (pasos, cfg, sampler, tamaño, semilla, referencias, commit del motor, tiempos de muestreo y decodificado, memoria mínima). Se propone al flujo, con `gw-harvest`, una operación de imagen en `log-format.md` | `medir.py` acepta cualquier operación y agrupa por perfil de máquina, tarea y modelo, así que mide imágenes sin cambios; cierra IMG-3 de WMF |
| D27 | **Contrato y código en inglés**: claves JSON en camelCase (esquemas, API, configuración del proyecto), identificadores y comentarios del código en inglés; los textos visibles siguen en es/en (D16) y el glosario da el nombre en código de cada término (pedido = `order`, intento = `attempt`, elegida = `chosen`…) | Decidido por la persona en F0: herramienta para publicar; la bitácora, el plan y los commits siguen en español |

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
| F2 Motor real | Envoltorio de `sd-cli` con el perfil de máquina (memoria, `--max-vram`, tope, cancelar, progreso); `instalar.sh` con versiones fijas y checksum | Un pedido real generado en la Deck (comprobación manual de la persona) |
| F3 API y arranque | API HTTP (D17, D25) y arranque bajo demanda; unidad `systemd --user` opcional | Tests de la API; `gimg` arranca el servicio solo |
| F4 Interfaz | Las tres pantallas de D22, es/en | Recorrido completo en el navegador |
| F5 Piloto WMF | Configuración de ejemplo para WMF, guía de integración y propuesta de migración para su repo; medida base con `opt-ai` y comparación `sd-server` (D14) | WMF genera y recibe una elegida sin copia a mano |

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
D19) + `", "` + `style` del perfil (solo si `style` no está vacío). `params` = ajustes del perfil (`width`, `height`,
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
`machineProfile` en `<config>/config.json`; por defecto `steam-deck`. La ruta del perfil de máquina es entrada de confianza de la persona en su propia máquina
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
entrada fallida es siempre `{"code": ..., "params": {...}}` (JSON): el `GimgError` conserva código y parámetros,
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
ordenadas, sangría 2 y salto final. Deshacer hasta `null` borra el archivo entregado y su entrada. Las referencias
pasan por `inside(root, …)` y tienen que existir.

**CLI** (`gimg/cli.py`, `python3 -m gimg`; el lanzador `gimg` llega con `instalar.sh` en F2). Órdenes en inglés:
`project add|remove|list`; `order submit <proyecto> <archivo|->` (crea o actualiza y encola `count` intentos, dice
el estimado); `order list <proyecto> [--profile] [--chosen|--unchosen]`; `order show <proyecto> <key> <perfil>`;
`attempt new <proyecto> <key> <perfil> [--seed] [--count] [--prompt] [--steps] [--cfg] [--sampler]`;
`attempt mark … <id> new|candidate|discarded`; `attempt note … <id> <texto>`; `choose … <id>`; `undo …`;
`queue list|cancel <id>`; `work [--once]` (procesa la cola; en F3 lo hará el servicio); `version`. Errores por stderr
con salida 1.

### Pasos de F1

| Paso | Qué | Hecho cuando |
|---|---|---|
| F1.1 | `paths`, `fsutil`, `projects`, `maxLength` de `key` y `prompt` | Tests de la guardia (D25), del registro y de la carga de la configuración |
| F1.2 | `orders`: pedidos, intentos, estados, notas, elegir y deshacer (sin entrega) | Tests de reenvío, estados y pila de elegidas |
| F1.3 | `engine` (`FakeEngine`), `limits`, `log` y estimado | Tests del PNG, los límites, el formato del registro y la mediana |
| F1.4 | `queue` y `worker` | Tests de orden, cancelar, reinicio y un solo trabajador |
| F1.5 | `delivery` y manifiesto, enganchados a elegir y deshacer | Tests de entrega, guardia de la plantilla y manifiesto |
| F1.6 | `cli` y prueba del ciclo completo; README es/en con el uso | Test de extremo a extremo: añadir proyecto, pedir, trabajar, elegir, deshacer |

## Pendiente

- Proponer al flujo (`gw-harvest`) una operación de imagen en `opt-ai/references/log-format.md` (D26).
