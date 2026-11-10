# Leves de ramas ya fusionadas

Sacados de «Pendiente» de `docs/handoff.md` el 2026-11-06 (retro de `fix-0.4.1`, P4): son hallazgos leves de revisiones ya cerradas, que no se vuelven a revisar en su PR. Se retoman si una tarea toca lo mismo. Desde ahora, al fusionar una rama, sus leves van a `docs/records/leves-<rama>.md`.

- **Leves de la fase 1 de `release-install` (2026-11-05, no se revisan más en este PR):** `release.yml` copia a mano los pasos «Install» y «Check» de `check.yml` (un workflow reutilizable con `workflow_call` quitaría la copia: P2 de la retro, al flujo; mientras, el test de P1 vigila que no se desvíen); el test inestable de `test_engine_sdcpp` puede tumbar una release: se reintenta con `gh run rerun`.
- **Leve de la fase 3 de `f2-motor`:** el check deja dos `ResourceWarning: unclosed file` (descriptores 7 y 8), seguramente el `stderr=PIPE` del Chrome de `tests/browser.py`, que `close()` no cierra.
- **Leves de la revisión de fase 1 de `f2-motor` (2026-11-05, no se revisan más en este PR)** (`docs/records/revision-fase1-f2-motor-2026-11-05.md`): (6) `_contrast_of` decodifica la imagen una vez por elemento de texto; (7) `save_template` puede dejar un `.json` huérfano que bloquea el nombre; (8) `_sidecar` no comprueba que `zone` quepa en `target_size`; sin verificar: `gimg queue list` quizá ordena por archivo y no por `position`.
- **Leves de la revisión de F4a** (`docs/records/revision-F4a-2026-11-05.md`, 10-16): no se revisan más en este PR. Además: con algo en marcha, el cajón de la cola se repinta cada 3 s (conserva el foco por `data-fid`, no el desplazamiento).
- **Leve de la revisión de F3.3:** `queue.submit_order/new_attempts/queued_view` son orquestación (engine + orders + queue), no cola; si molesta, un `gimg/actions.py` fino que importe los tres.
- **Leves de la revisión de F3.2 (no se revisan más en este PR):** (3) el log de sd-cli se sirve entero en memoria, sin tope; (4) la vista previa no es atómica (sd-cli reescribe `.pending-N.preview.png` en su sitio: un PNG truncado un sondeo); (7) `attempt_log` saca la carpeta del pedido con el truco `orders.attempt_image(..., {"image": "."})`: mejor un `orders.order_folder()` público.
- **De la revisión de F3.4 (leves, pendientes):** `serve.json` pasa por `write_json` con el umask (0644) y el `chmod 0600` llega tras el `replace` (ventana corta, contenido no secreto: darle `mode` a `write_json`); un POST que encola entre la parada por inactividad y `shutdown()` deja la entrada `queued` hasta el próximo `serve` (hacer un último `maybe_launch_worker` tras `shutdown()`).
- **De la revisión de F3.1 (leves):** hechos (el 304 en F3.2; `worker_alive()` sin crear nada y con `None` = no se sabe, F3.4).
- **Leves de la revisión antes de `main` de `f2-motor` (`33f2dde`, 2026-11-04; no se revisan más en este PR):** (a) `projects.load_config` relee y valida `models.json` en cada `projects.get` (caché de módulo), y un modelo fuera del catálogo deja el proyecto sin cargar también con el motor falso; (b) si `add_attempt` falla, `attempts/q<id>.log` queda huérfano (`worker.py` ~316); (c) sin `targetWidth`/`targetHeight`, la composición usa el tamaño del perfil e ignora el `width`/`height` del pedido (`compose.target_size`); (d) `order submit`/`attempt new` cargan el perfil de máquina y el catálogo solo para el nombre del proveedor (`cli.py` ~283); (e) guarda redundante en `queue._set_running` (`_txn` ya no escribe sin cambios).
- **Leves de F2.9 (`gimg measure`; revisión de `d6fc49d`, no se revisan más en este PR):** (a) un nombre con `%d` lo toma image2 por secuencia (no hay arreglo general: `-pattern_type none` rompe los webp; rechazarlo con error claro); (b) EXIF: ffmpeg gira los JPEG y ffprobe no, la zona da `zone_outside` o `tool_failed` opaco y la paleta se estira (`-noautorotate`); (c) sin tope de alto (256×40000 tarda 8 s): limitar `tw*th`; (d) «de 1 colores»; (e) el test de EMD no compara con `emd.py` de Tarkor sino con una fórmula a mano con `delta=1`; (f) `--palette ""` se ignora en vez de `measure.bad_hex`; además: no descarta los píxeles transparentes (un PNG con alfa se mide sobre negro: favicon de toVeriAI, 1 % de paleta); una paleta con colores repetidos junta sus `by_color`; con orientación EXIF el tamaño de `ffprobe` y la zona podrían no casar. Las portadas del Portal como referencia: que la persona diga si son marca (la de toVeriAI es casi blanca).
- **Leves de la revisión de E3 de F2.8 (`a2bb37b`; no se revisan más en este PR):** (a) si `delivery` falla tras `set_composed`, el registro ya apuntó éxito y el archivo entregado queda viejo: documentarlo o código propio («compuesto pero no entregado: `gimg choose`»); (b) `doctor._fonts`: registro ilegible muestra `str(exc)` con proyecto «-» y sin test; un `RecursionError` de `load_config` tumba todo `gimg doctor`: `exc.message()`, clave propia y `except Exception` por proyecto; (c) de E3: la línea vieja con `app.image.compose_error` sigue en el registro tras recomponer; `doctor.fonts.project_error` sale en el idioma por defecto.
- **Leves de la revisión de E2 de F2.8 (`e1a5d7f`; no se revisan más en este PR):** (a) `delivery.choose`: si `set_composed` entra entre `orders.get` y `orders.choose`, el intento leído con `composeError` falla con `order.choose_discarded`, motivo que no corresponde: releer y lanzar `check_choosable` del intento fresco; (b) el registro deja la línea vieja con `app.image.compose_error` tras recomponer y, con perfil de solo destino, no consta la composición (E3 añade una línea `app.image.compose` al recomponer); (c) tras un SIGTERM la entrada queda `running` y la siguiente consulta la devuelve a `queued` (comportamiento previo a F2.8); (d) al componer desde la cruda tras un SIGTERM (entrada retomada) no se escribe línea de registro.
- **Leves de la revisión de E1 de F2.8 (`79c3442`; no se revisan más en este PR):** (a) `cover` escala antes de recortar: con 4096×64 → 16×4096 el intermedio sería enorme y ffmpeg falla con `tool_failed` opaco; recortar primero en coordenadas de la cruda y escalar después; (b) si la cruda no trae chunk `gimg`, la compuesta sale sin `compose` (contradice el docstring); escribir `{"compose": info}` igualmente; (c) una plantilla con `encoding="ISO-8859-1"` y solo ASCII pasa y se escribe en UTF-8 con la declaración Latin-1 («ñ» sale mal); rechazar codificaciones distintas de UTF-8 y pasar el logo a base64 desde sus bytes; (d) `test_the_template_cannot_read_files_outside_its_own_folder` pasaría sin la carpeta temporal vacía (lo bloquea librsvg): usar un `secret.png` junto a la plantilla dentro del proyecto; (e) `fieldName` copiado a mano en los dos esquemas sin test que compare los dos `$defs`.
- **Leves de la revisión de F0** (no se revisan más en este PR):
  - F2: `width`/`height` sin `multipleOf` (lo que exija `sd-cli` por modelo); el validador aún no lo soporta.
  - `propertyNames` solo pasa el `pattern` del primer error: si falla por otra cosa, el mensaje sale vacío.
- **Leves de la revisión de `941efa9` (componer/medir, F2.0):** pruebas de Lab/umbral y del recorte cover con píxeles; `fuentes.sh` sin test, `mktemp` fuera del destino y descarga de `main` sin fijar; `HEX` con `$` en vez de `fullmatch`; viewBox `1.2.3` o `0 0 0 0` da traza; `esc` no quita caracteres de control; salida `.svg` machaca el SVG de depuración; sin `timeout` en subprocesos; sin `piloto/fuentes/` cae a otra fuente sin avisar; `ffprobe` sin `which`; signalstats es BT.601 rango limitado (calibrar igual en F2.9).
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
- **Leves de la revisión de `49e6176` (F2.5, `instalar.sh` y `gimg doctor`; no se revisan más en este PR):** `--with` valida
  el id con `grep -qx` sin `-F` (un `flux.*` pasa y no instala nada; con `pipefail` puede dar SIGPIPE); el `doctor` final
  sale con 1 si faltan `ffmpeg` o `rsvg-convert`, así que `instalar.sh` acaba en error aunque lo suyo haya ido bien (decidir
  si con `engine: fake` son `warn`, D36); `sha256_of` de `doctor.py` no captura `OSError` (permisos) y sale como error
  interno; `--json` da `message`/`fix` localizados sin `key`/`params` (quien lo parsee depende del idioma); el lanzador
  sobrescribe un `~/.local/bin/gimg` ajeno; el aviso de flatpak solo sale en el paso 6, tras bajar ~7 GB a la carpeta
  equivocada (avisar antes del paso 3); `--with` con `--only-cli` se ignora en silencio; si `curl` falla, `set -e` sale sin
  mensaje propio; `tests/test_worker.py:361` deja «disk full» en stderr (parchea `log.append` a propósito: ruido, silenciar).
