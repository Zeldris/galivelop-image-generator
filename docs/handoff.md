<!-- galivelop-workflow v0.5.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `main` (F1 fusionada); F2 en una rama nueva `f2-motor` |
| **Fase / tarea** | F1 Núcleo cerrada y en `main`; siguiente fase F2 Motor real (`docs/plan.md`, fila F2) |
| **Último punto estable** | F1 en `main` (`0d02f51`, marca de revisión sobre `fe7d968`): F1.1-F1.6, revisión completa con 14 arreglos, retro aplicada; check en verde, 282 tests |
| **Siguiente paso** | F2: `git switch -c f2-motor --no-track origin/main` y `git push -u origin f2-motor`; el contrato «F2 en detalle» lo escribe un subagente `opus` y la sesión principal lo revisa y lo lleva a la persona (`.claude/gw/orchestrate-dealer.md`); apuntar el presupuesto de compactaciones |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |
| **Tarea en curso · `f2-motor`** | F3 hecha (0.3.0). F4a en `gimg/ui/`, revisada y con los arreglos 1-9 hechos (`docs/records/revision-F4a-2026-11-05.md`; 10-16 leves, pendientes); JS sin ejecutar (no hay node): recorrido en navegador en la Deck, de la persona. **Siguiente:** F4b/F4c (contratos los decide la sesión, «pendiente de la persona») → fase 1-2 antes de `main` (parar antes de `reviewed.sh`). Presupuesto de compactaciones: 3 (gastadas 2) |

Con `logRows` en `.claude/gw.json`, cada rama escribe solo en su fila de esta tabla, como mucho 600 caracteres, con
la forma ``| **Tarea en curso · `<rama>`** | tarea, fases antes de `main`, qué falta y siguiente paso |``; el push lo comprueba.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-10-25 — F1 (`f1-nucleo`) a `main` por push directo con confirmación de la persona: CI no comprobado (sin `gh` en esta máquina; en F0, sin cuota), **comprobado solo en local** (check del `pre-push` sobre `0d02f51`). Tres fases hechas, marca en `fe7d968`.
2. 2026-10-25 — F0 (`f0-esqueleto`) a `main` por push directo con confirmación de la persona: CI sin cuota (pagos fallidos), **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `17e28eb`.
3. 2026-10-25 — `diseno-generador` a `main` por push directo con confirmación de la persona: CI sin cuota, **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `b111e4f`.
4. 2026-10-25 — Diseño ronda 3 aprobada: clave del pedido, retoque de prompt, entrega PNG, `gimg`, seguridad, registro opt-ai.
5. 2026-10-25 — Diseño ronda 2 aprobada: pedido/intentos/elegida, cola, perfil de máquina, es+en, ADR 0001-0002.

## Pendiente

- **Leves de la revisión de F4a** (`docs/records/revision-F4a-2026-11-05.md`, 10-16): no se revisan más en este PR. Además: con algo en marcha, el cajón de la cola se repinta cada 3 s (conserva el foco por `data-fid`, no el desplazamiento).

- `docs/en/api.md` (D16 pide docs en es y en).
- **Leve de la revisión de F3.3:** `queue.submit_order/new_attempts/queued_view` son orquestación (engine + orders + queue), no cola; si molesta, un `gimg/actions.py` fino que importe los tres.
- **Leves de la revisión de F3.2 (no se revisan más en este PR):** (3) el log de sd-cli se sirve entero en memoria, sin tope; (4) la vista previa no es atómica (sd-cli reescribe `.pending-N.preview.png` en su sitio: un PNG truncado un sondeo); (7) `attempt_log` saca la carpeta del pedido con el truco `orders.attempt_image(..., {"image": "."})`: mejor un `orders.order_folder()` público.
- **De la revisión de F3.4 (leves, pendientes):** `serve.json` pasa por `write_json` con el umask (0644) y el `chmod 0600` llega tras el `replace` (ventana corta, contenido no secreto: darle `mode` a `write_json`); un POST que encola entre la parada por inactividad y `shutdown()` deja la entrada `queued` hasta el próximo `serve` (hacer un último `maybe_launch_worker` tras `shutdown()`).
- **De la revisión de F3.1 (leves):** hechos (el 304 en F3.2; `worker_alive()` sin crear nada y con `None` = no se sabe, F3.4).
- **Tras r7 (pedido de la persona del 2026-11-04):** (a) y (b) hechas el 2026-11-05 (hojas r8, D39); (c) aplicar D38 («Galivelop IG», siglas «GVIG») a la hoja de estilo, el README, los textos de `examples/galivelop-image-generator` y la interfaz.
- **Tras aplicar las hojas (2026-11-04), lo que queda:** (a) prompts por rehacer en la próxima ronda: Tarkor `estilo.txt`, `r2-hex/palabras/material` y `r5-*` sin `sun` ni «muted» (`r2-luz.txt` candidato a `estilo.txt`), `r5-cuadrado`/`r5-vertical` con la mitad inferior; developer `og.txt`/`r5-cabecera.txt` con la mitad inferior y «departs from»; (b) piloto: alinear `caja_zona` de `componer.py` y `piezas.json` con la zona de cada hoja (Portal 55 % frente a 1/2; toVeriAI `og` arriba 1/3), subtítulo de voice-generator (67 car.) y volver a medir su og; (c) `icon`, y `compose` con logos para voice-generator y developer (los otros 5, hechos el 2026-11-04); con gimg, `GIMG_CONFIG_HOME=~/.config/gimg GIMG_DATA_HOME=~/.local/share/gimg` desde el sandbox de VS Code; (d) el validador (`gimg doctor --project`) con las comprobaciones 5, 8, 9 y 11 nuevas de la plantilla; (e) propuestas a otros repos (`docs/propuestas/`): toVeriAI (og:image, PNG «VeriNews», ShareCard), WMF (`Palette:`), Instalador de Tarkor (icono), Portal (`generar-marca.mjs`, `#2F7A55`); (f) revisar la hoja del Portal cuando su ADR 0002 llegue a `main`; (g) Portal: trazo del logo `#EAF4FA` en los SVG; (h) `docs/marcas/README.md` l.16 y l.33 y `docs/plan.md` l.653-655 (paleta de Tarkor) a remitir a la hoja; (i) flaky visto una vez: `tests/test_worker.py` `test_second_worker_refused_other_process`.
- **Leves de la revisión antes de `main` de `f2-motor` (`33f2dde`, 2026-11-04; no se revisan más en este PR):** (a) `projects.load_config` relee y valida `models.json` en cada `projects.get` (caché de módulo), y un modelo fuera del catálogo deja el proyecto sin cargar también con el motor falso; (b) si `add_attempt` falla, `attempts/q<id>.log` queda huérfano (`worker.py` ~316); (c) sin `targetWidth`/`targetHeight`, la composición usa el tamaño del perfil e ignora el `width`/`height` del pedido (`compose.target_size`); (d) `order submit`/`attempt new` cargan el perfil de máquina y el catálogo solo para el nombre del proveedor (`cli.py` ~283); (e) guarda redundante en `queue._set_running` (`_txn` ya no escribe sin cambios).
- **LoRA de Tarkor (lectura del 2026-11-04, `docs/records/lectura-2026-11-04-tarkor.md`):** propuestas 1-7 **aprobadas por la persona el 2026-11-04** y repartidas en `docs/plan.md` (F2.10: hojas de contactos y aviso de `maxVram` en `doctor`; F2.11: huella de la LUT, sin LoRA; F2.12: `master-1039`; F5: LoRA en el perfil; proceso: revisión por paso y a `main` por bloques). Hojas y aviso se hacen antes de revisar r2.
- **Hoja de estilo mínima por proyecto (pedido de la persona del 2026-11-04, fila F2.12 de `docs/plan.md`):** borrador hecho (`docs/marcas/plantilla-hoja-de-estilo.md`, Fable, revisado): 18 filas obligatorias, lista de 14 comprobaciones (7 sin validar aún) y 11 huecos del perfil (sección 15). Presentado a la persona el 2026-11-04, pendiente de su visto bueno. Caso real hecho: `docs/marcas/galivelop-image-generator/hoja.md` (15 obligatorios del repo, 3 **[P]**), con 17 cambios propuestos a la plantilla al final, pendientes de la persona; falta decidir dónde vive el validador (`gimg doctor --project` o script del piloto) antes de r5. Hechos `gimg sheet` (hoja de contactos con rótulos vía rsvg-convert; el ffmpeg de la Deck no trae `drawtext`) y el aviso `doctor.vram` (umbral 2 GB, el de `steam-deck.json`), 950 tests; las rondas se revisan con `gimg sheet`.
- **Leves de F2.9 (`gimg measure`; revisión de `d6fc49d`, no se revisan más en este PR):** (a) un nombre con `%d` lo toma image2 por secuencia (no hay arreglo general: `-pattern_type none` rompe los webp; rechazarlo con error claro); (b) EXIF: ffmpeg gira los JPEG y ffprobe no, la zona da `zone_outside` o `tool_failed` opaco y la paleta se estira (`-noautorotate`); (c) sin tope de alto (256×40000 tarda 8 s): limitar `tw*th`; (d) «de 1 colores»; (e) el test de EMD no compara con `emd.py` de Tarkor sino con una fórmula a mano con `delta=1`; (f) `--palette ""` se ignora en vez de `measure.bad_hex`; además: no descarta los píxeles transparentes (un PNG con alfa se mide sobre negro: favicon de toVeriAI, 1 % de paleta); una paleta con colores repetidos junta sus `by_color`; con orientación EXIF el tamaño de `ffprobe` y la zona podrían no casar. Las portadas del Portal como referencia: que la persona diga si son marca (la de toVeriAI es casi blanca).
- **Leves de la revisión de E3 de F2.8 (`a2bb37b`; no se revisan más en este PR):** (a) si `delivery` falla tras `set_composed`, el registro ya apuntó éxito y el archivo entregado queda viejo: documentarlo o código propio («compuesto pero no entregado: `gimg choose`»); (b) `doctor._fonts`: registro ilegible muestra `str(exc)` con proyecto «-» y sin test; un `RecursionError` de `load_config` tumba todo `gimg doctor`: `exc.message()`, clave propia y `except Exception` por proyecto; (c) de E3: la línea vieja con `app.image.compose_error` sigue en el registro tras recomponer; `doctor.fonts.project_error` sale en el idioma por defecto.
- **Leves de la revisión de E2 de F2.8 (`e1a5d7f`; no se revisan más en este PR):** (a) `delivery.choose`: si `set_composed` entra entre `orders.get` y `orders.choose`, el intento leído con `composeError` falla con `order.choose_discarded`, motivo que no corresponde: releer y lanzar `check_choosable` del intento fresco; (b) el registro deja la línea vieja con `app.image.compose_error` tras recomponer y, con perfil de solo destino, no consta la composición (E3 añade una línea `app.image.compose` al recomponer); (c) tras un SIGTERM la entrada queda `running` y la siguiente consulta la devuelve a `queued` (comportamiento previo a F2.8); (d) al componer desde la cruda tras un SIGTERM (entrada retomada) no se escribe línea de registro.
- **Leves de la revisión de E1 de F2.8 (`79c3442`; no se revisan más en este PR):** (a) `cover` escala antes de recortar: con 4096×64 → 16×4096 el intermedio sería enorme y ffmpeg falla con `tool_failed` opaco; recortar primero en coordenadas de la cruda y escalar después; (b) si la cruda no trae chunk `gimg`, la compuesta sale sin `compose` (contradice el docstring); escribir `{"compose": info}` igualmente; (c) una plantilla con `encoding="ISO-8859-1"` y solo ASCII pasa y se escribe en UTF-8 con la declaración Latin-1 («ñ» sale mal); rechazar codificaciones distintas de UTF-8 y pasar el logo a base64 desde sus bytes; (d) `test_the_template_cannot_read_files_outside_its_own_folder` pasaría sin la carpeta temporal vacía (lo bloquea librsvg): usar un `secret.png` junto a la plantilla dentro del proyecto; (e) `fieldName` copiado a mano en los dos esquemas sin test que compare los dos `$defs`.
- **Carpeta de datos en flatpak (resuelto en F2.5, `49e6176`):** VS Code en flatpak fija `XDG_DATA_HOME=~/.var/app/…`, y `gimg` desde su terminal usaría otra carpeta de datos que desde una terminal normal (`docs/records/contenido/r0-humo.md`). Decidido: no se ignora el XDG; `gimg doctor` lo avisa y dice que se fije `GIMG_DATA_HOME`/`GIMG_CONFIG_HOME` (mandan sobre XDG). Visto en la Deck el 2026-10-27: el aviso sale y, con las dos variables, instalación y datos van a `~/.local/share/gimg` y `~/.config/gimg`.
- **Leves de la revisión de F0** (no se revisan más en este PR):
  - F2: `width`/`height` sin `multipleOf` (lo que exija `sd-cli` por modelo); el validador aún no lo soporta.
  - `propertyNames` solo pasa el `pattern` del primer error: si falla por otra cosa, el mensaje sale vacío.
- **Leves de la revisión de `941efa9` (componer/medir, F2.0):** pruebas de Lab/umbral y del recorte cover con píxeles; `fuentes.sh` sin test, `mktemp` fuera del destino y descarga de `main` sin fijar; `HEX` con `$` en vez de `fullmatch`; viewBox `1.2.3` o `0 0 0 0` da traza; `esc` no quita caracteres de control; salida `.svg` machaca el SVG de depuración; sin `timeout` en subprocesos; sin `piloto/fuentes/` cae a otra fuente sin avisar; `ffprobe` sin `which`; signalstats es BT.601 rango limitado (calibrar igual en F2.9).
- **Referencias de estilo (antes de F5):** ronda del piloto con `sd-cli` y 1-2 imágenes de referencia sobre Tarkor,
  medida con D31; si mejora el % de paleta sin estropear el contraste, entra en F5 (fila «Referencias» de la pestaña
  Marca). Confirmado por la persona el 2026-10-27 (`docs/interfaz/propuesta.md`, decisión nueva 1).
  Expectativa rebajada el 2026-11-02 (Tarkor, IMG-30/31): la referencia conserva un sujeto (útil para mascota o
  producto), no el acabado ni la paleta; lo desaturado de Tarkor se espera arreglar con la LUT de F2.11.
- **Marca de Tarkor:** (en r2, probar antes las pautas de luz del 2026-11-02 de `docs/plan.md`, «Estilos por proyecto») el estilo sale desaturado en todos los formatos (SATAVG 5-7 frente al 15-30 del juego;
  `r5-og-bajo` arregla la luz, YAVG 66, pero no el color): otra vuelta del prompt con la persona
  (`docs/records/contenido/r5-piezas.md`).
- **Leves de la revisión de `3dc054d` (piezas/componer, F2.0):** avatar rasterizado con `-w` y `-h` deforma un logo no
  cuadrado; `'640x320' in name` frágil (un `2640x320`); sin tests de `main()` con piezas, `paleta_de`, avatar,
  `pagina.medidas` ni `ronda.sh r5`; la prueba del lockup no cubre la rama en que manda el ancho de la columna.
- **Leves de la revisión de la fase 2 (`cf1191f`, `0ebd00c`; no se revisan más en este PR):** (lo del presupuesto de compactaciones se fue con la v0.5.0, que lo trae de serie) el lint de shell da falso positivo con un comentario al final de una línea que nombre lo prohibido; `leer-entero` no cubre `cat docs/plan.md` por Bash.
- **Leves de la revisión de `bb7719a` (piloto, fase 1 antes de `main`; no se revisan más en este PR):** `piezas.pieza`
  mide el fondo limpio con `medir.medir` y tira su `signalstats` (basta `contraste_zona`); el velo repite `rect` en las
  cuatro zonas y parchea `offset="0.55"` con `replace`; `recorte_cover` es código muerto; sin tests de `logos.py`,
  `fuentes.sh` ni `pagina.pagina_ronda/resumen/tiempos`; las páginas del piloto solo en español (`visibleLanguages`
  es/en: traducir o declararlas internas); `ver.py` no resuelve enlaces simbólicos dentro de `piloto/`; algún
  `read_text` de `componer.py` sin `encoding`. **Para F2.8:** el piloto mete el fondo en base64 dentro del SVG y lo
  rasteriza entero con rsvg; D28 pide que rsvg haga solo la capa y ffmpeg la superponga: no portarlo tal cual.
- **Leves de la revisión de F2.6 (`2d224b4`..`c231eaa`; no se revisan más en este PR):** `PilotExampleTests.setUp` es la sexta copia del parche de `GIMG_CONFIG_HOME`/`GIMG_DATA_HOME` a carpeta temporal (`test_cli.CliBase`, `test_orders`, `test_limits`, `test_queue`, `test_projects`): sacar un ayudante común en `tests/`; el perfil `wide` de toVeriAI genera 1280×768 (5:3) y su destino es 1200×675 (16:9): ningún 16:9 es múltiplo de 64 bajo el tope, se decide con `targetWidth`/`targetHeight` en F2.7-F2.8 (recorte de ~6 % de alto). **Para F2.8 (lo decide la persona):** `piezas.json` de developer, image-generator y voice-generator trae `cuadrado`, `vertical` y `cabecera` de r5, pero sus biblias solo listan `og` y `social` y sus configuraciones siguen la biblia (decisión 1 de F2.6): o esas piezas entran en las biblias y ganan perfil, o se quitan de `piezas.json` al portarlo a `compose`.
- **Leves de las revisiones de F1:**
  - `orders._FULL_PARAMS` repite a mano límites de `width`/`height`/`model` en vez de usar `$defs/profile` del esquema de la configuración del proyecto.
  - Un lector (`list`/`get`/`enqueue`) que toma `worker.lock` un instante hace que un trabajador que arranca falle con
    `worker.already_running`: reintentar el cerrojo una vez tras ~100 ms o documentarlo.
  - Si `add_attempt` falla después de escribir `order.json`, el `finally` del trabajador borra la imagen y queda un
    intento con `queueEntry` sin imagen: comprobar con `attempt_for_entry` antes de borrar.
  - `queue.is_cancel_requested` lee la cola entera bajo cerrojo cada 20 ms durante la generación; espaciar el sondeo si la cola crece.
  - `cli.main(['--lang','fr'])` lanza SystemExit en vez de devolver 2 (`_prescan_lang` fuera del try) y su uso no habla de las órdenes.
  - `delivery.undo` prepara la entrega antes de que `orders.undo` rechace un destino descartado: con la imagen borrada sale `delivery.source_missing` en vez de `order.undo_discarded`.
  - Al cambiar `delivery.template`/`dir` y volver a elegir, el archivo entregado en la ruta antigua queda huérfano.
  - `undo` hasta `null` no borra las subcarpetas vacías que creó la entrega.
  - Un dato, un sitio: el rango de `count` (1-50) en `attempt_specs` y `paths.MAX_KEY` repiten el esquema del pedido (junto con `_FULL_PARAMS`).
  - Reutilización: escritura atómica copiada en `fsutil.write_json`, `delivery._copy` y `FakeEngine.generate`; `_now()` en cuatro módulos; `delivery._find` reimplementa `orders._attempt`; `worker._single_worker` repite `queue._no_worker`; `cli.opt()` es igual a `arg()`.
  - Eficiencia: `choose`/`undo` releen y validan la configuración, el pedido y el manifiesto varias veces.
  - `GIMG_CONFIG_HOME`/`GIMG_DATA_HOME` relativas dependen de la carpeta actual (las XDG relativas sí se ignoran).
  - `orders.mark` no toma el cerrojo de la entrega: un `mark` a mitad de `choose` lo revierte con `order.choose_discarded` (mitigado).
  - `delivery.target_taken` también bloquea un `undo` hasta `null` si otra entrada del manifiesto comparte `file`
    (tras cambiar la plantilla), y compara sin `casefold` (no ve colisiones en discos sin mayúsculas).
  - `order submit` guarda el pedido antes de que `attempt_specs` rechace un prompt+estilo largo: queda sin encolar.
- **Generador de Tarkor libre (la persona levantó el aviso el 2026-10-27):** ya se pueden generar imágenes desde este repo.
  Antes de cada tanda, `gimg doctor`: el 2026-10-27 Ollama volvía a cargar `tarkor-narrador-llama31` cada ~20 s (algún
  proceso de Tarkor lo seguía llamando) y la memoria libre bajaba a ~2,5 GB; con eso `gimg` aborta (`engine.ollama: abort`).
  Resuelto ese día cuando la persona confirmó que nadie usaba nada: descarga por la API de Ollama (`POST /api/generate` y
  `/api/embed` con `keep_alive: 0`; el binario `ollama` no se ve desde el flatpak) y la r1 de `gimg` corrió entera sin recargas.
- **URLs del catálogo a verificar [P]** (`gimg/models.json`): deducidas, no copiadas (WMF-imagenes no las apunta); las seis dan 200
  y su `x-linked-etag` coincide con el sha256 de la Deck. Confirmar el repositorio del VAE de FLUX.3
  (`Comfy-Org/flux2-dev`, `split_files/vae/flux2-vae.safetensors`) y el nombre `Qwen3VL-4B-Instruct-Q4_K_M.gguf` (el del
  repo de Qwen; `Qwen3-VL-…` da 404).
- **Leves de la revisión de `0523f8b` (F2.1; no se revisan más en este PR):** `model.catalog_invalid` no muestra `reason`
  en el texto; `resolve` compone `path` sin `paths.inside`; `test_bad_file_fields` no prueba `\n`, `\x00`, `/abs`, `~x` ni
  `x/..`; el patrón de `url` acepta `https://a b` (`\s` ASCII en `_compile`); `model.unknown` de `load_config` no dice el
  perfil ni el archivo, y relee el catálogo en cada `load_config`; el patrón de id repetido en vez de `$ref` a `$defs/name`;
  `read_text`/`write_text` sin `encoding` en `tests/test_models.py`. **Para F2.5:** `defaults.steps` del catálogo no se
  contrasta con `maxSteps`; `worker._generate` usa el `timeoutS` general y no `resolve()`.
- **Leves de la revisión de `081977d` (F2.2; no se revisan más en este PR):** `load_ms` suma las 149 líneas «loading
  tensors completed» del log real, que caen dentro del muestreo (`--params-backend disk`): se solapa con `sample_ms` y
  `decode_ms` (documentarlo o contar solo las cargas anteriores a «sampling using» antes de que F2.4 lo registre); un
  `GIMG_SD_CLI` relativo sin barra pasa `is_file` pero `Popen` lo busca en `PATH` (`resolve()` en `binary_path`) y
  cualquier `OSError` de `Popen` sale como `engine.binary_not_executable`; si `orders.add_attempt` falla tras mover el
  log, `attempts/q<id>.log` queda huérfano; `open`/`mkdir` del log sin envolver en `GimgError`; el párrafo «Motor» del
  plan no lista `-t` (el código lo pone antes de los `args`); `sd-cli` muerto por señal sale como «exited with code -9».
- **Leves de la revisión de `e9af90f` (F2.3; no se revisan más en este PR):** con `engine.ollama: unload` la memoria
  previa se mide antes de descargar Ollama (puede rechazar por `engine.low_memory` justo antes de liberarla: releer tras
  el `unload`); `GIMG_MEMINFO` con una ruta ilegible salta la protección en silencio (avisar por stderr o llamarla
  `GIMG_TEST_MEMINFO`); `json.loads` de `/api/ps` no captura `RecursionError`; el opener sin proxy sigue redirecciones
  (quitar `HTTPRedirectHandler`); el timeout de urllib es por socket, no total; el `unload` (hasta 15 s más los POST) no
  mira `should_cancel`; el patrón de `ollamaUrl` del esquema acepta control y espacios (`re.ASCII`) y `test_models` no
  prueba el campo; `min_free_mb` no llega a `orders.add_attempt` y se pierde en un intento fallido; `read_text`/`write_text`
  sin `encoding` en los tests nuevos; `dead_ollama_url` reserva y suelta un puerto (ventana de colisión inocua).
- **Leves de la revisión de `29dc2b1` (F2.4; no se revisan más en este PR):** el chunk `gimg` del PNG sale sin modelo ni
  archivos si el perfil no define `model` (añadir `modelFiles` o el id resuelto) y sin `provider` (el docstring de
  `worker.py` lo promete); el chunk va antes de `IEND` (lectores en streaming y Pillow sin `load()` solo ven los anteriores a
  `IDAT`: insertarlo tras `IHDR`); un prompt con sustituto suelto (`\ud800`) hace que `add_text_chunk` lance
  `UnicodeEncodeError` fuera del `except` del worker; el fallo del chunk solo va a stderr, no al intento (F4 no sabrá que
  falta); `set_preview` y el campo `log` del intento aceptan cualquier cadena (validar con D25 antes de que F4 los sirva)
  y `_eta_text(inf)` desborda; sin marcador «sampling completed» la barra del VAE se leería como progreso si `steps` no
  coincide (solo con `FAKE_SD_NO_TIMES`); `app.image.steps/cfg` del registro son los del intento y el PNG lleva los efectivos.
- **F2.5 manual, en la Deck (persona), solo cuando el generador de Tarkor esté libre:** `./instalar.sh` de verdad (descarga
  del zip `master-1000-95ff762` de stable-diffusion.cpp y de los modelos de `installDefault` desde Hugging Face: ninguna
  descarga se ha probado, solo con fakes) y `gimg doctor --verify` en verde. Si `instalar.sh` ya encuentra el motor y los
  modelos de WMF-imagenes, `--models-from` evita bajarlos otra vez.
- **Leves de la revisión de `49e6176` (F2.5, `instalar.sh` y `gimg doctor`; no se revisan más en este PR):** `--with` valida
  el id con `grep -qx` sin `-F` (un `flux.*` pasa y no instala nada; con `pipefail` puede dar SIGPIPE); el `doctor` final
  sale con 1 si faltan `ffmpeg` o `rsvg-convert`, así que `instalar.sh` acaba en error aunque lo suyo haya ido bien (decidir
  si con `engine: fake` son `warn`, D36); `sha256_of` de `doctor.py` no captura `OSError` (permisos) y sale como error
  interno; `--json` da `message`/`fix` localizados sin `key`/`params` (quien lo parsee depende del idioma); el lanzador
  sobrescribe un `~/.local/bin/gimg` ajeno; el aviso de flatpak solo sale en el paso 6, tras bajar ~7 GB a la carpeta
  equivocada (avisar antes del paso 3); `--with` con `--only-cli` se ignora en silencio; si `curl` falla, `set -e` sale sin
  mensaje propio; `tests/test_worker.py:361` deja «disk full» en stderr (parchea `log.append` a propósito: ruido, silenciar).
- **Flujo:** `red-without-fix.sh` falla con «cannot stash» si antes se hizo `git add -N` de archivos nuevos (funciona
  sin añadirlos); proponerlo al flujo con el resto (`gw-harvest`).
- **Cuando la persona avise:** revisar las actualizaciones de Tarkor (otro repo) sobre su generador de imágenes: lo lee
  un subagente `Explore` que devuelve un resumen con rutas (`gw-orchestrate-dealer`); desde aquí no se modifica.
- El flujo copiado es la 0.4.0 **sin publicar** (rama `ccr-6dfbc880-ddr41g` del flujo, commit `d227bbf`; su `main` está en
  0.3.0): `/gw-update` cuando la 0.4.0 salga publicada.
- Proponer al flujo (`gw-harvest`) lo de `docs/records/retro-2026-10-25-diseno.md` (R1-R4, R7) y de
  `docs/records/retro-2026-10-25-f0.md` (R1, R3, R4); el hallazgo
  MEDIO de R7 (claves pegadas a una letra en `pre-commit`) conviene arreglarlo antes de publicar la 0.4.0.
- Proponer al flujo (`gw-harvest`) R3a y R3b de `docs/records/retro-2026-10-25-f1.md`.
- Proponer al flujo (`gw-harvest`) una operación de imagen en el `log-format.md` de `gw-opt-ai` (D26).

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `for f in .githooks/pre-commit .githooks/pre-push .githooks/commit-msg; do bash -n "$f"; done` y `python3 -m unittest discover -s tests -t .`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
