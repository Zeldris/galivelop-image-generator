# Registro de cambios

[English](CHANGELOG.md)

Aquí se apuntan todos los cambios notables del proyecto.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Cambiado

- La interfaz es clara por defecto (antes oscura); el tema oscuro sigue disponible. Paleta por roles de la hoja de
  marca r9.
- Fuentes nuevas de la interfaz: Big Shoulders Display, Literata y JetBrains Mono sustituyen a Inter y Sora.
- Logo y favicon redibujados (hoja de marca r9): baldosa plana, lockups claro y oscuro y versiones en línea.
- El nombre visible del producto es «Galivelop IG» (GVIG) en el README y en `cli.description` (D38); el repositorio,
  el paquete y la orden siguen siendo `galivelop-image-generator` y `gimg`.
- `gimg brand wordmark` y `system`, y el taller «Sistema de logo», espacian las letras 0,01 em por defecto (antes
  0,12), el de la familia.

### Añadido

- `gimg export --crop X,Y,W,H` (caja en píxeles del original, antes de `--size`, también para ICO) y `--anchor`
  (`center` por defecto, `top`, `bottom`, `left`, `right` o una esquina como `top-left`: dónde cae el recorte de
  proporción de `--size`). El resultado lleva `crop` y la CLI lo dice, así una cadena de recortes queda como orden
  repetible. Errores `export.bad_crop`, `export.crop_outside` y `export.bad_anchor`.
- `gimg queue pause` y `gimg queue resume`: la pausa deja la marca `queue.paused` en el directorio de datos; el
  trabajador termina la imagen en curso y no coge otra, `gimg serve` no lanza trabajador mientras dure y `queue list`
  lo avisa. Al reanudar, el servicio relanza el trabajador en su siguiente latido (unos segundos). En pausa, lo que
  espera en cola no mantiene vivo el servicio, y `gimg queue resume` lo vuelve a arrancar si queda algo en cola. El
  cajón de la cola de la interfaz tiene el botón «Pausar cola» / «Reanudar cola» y la pastilla dice «en pausa».
- `gimg brand system --margin` (espacio libre alrededor de los dos lockups) y `--mono` (lockups con el emblema en una
  tinta: todo el lockup en `currentColor`, como piden las hojas de la familia).
- Perfiles de ejemplo para los canales que piden las hojas de marca: `lateral` 704×1344 (instalador de Windows),
  `linkedin` 1584×396, `discord` 960×540 y `panorama` 1600×900 en `examples/tarkor/`, e `icon` 512×512 en
  `examples/toveriai/`.
- `gimg export IMAGEN SALIDA`: copia un PNG entregado a WebP sin pérdida, ICO (un PNG por lado, 16 a 256) o BMP de
  24 bits sin alfa (sobre `--background`), o a un PNG de otro tamaño; `--size` recorta al centro y reduce, nunca
  amplía. Codificadores en Python puro; la entrega sigue siendo el PNG con su procedencia.
- Traducción al inglés de la API local: `docs/en/api.md`; el test de la documentación de la API comprueba los dos idiomas.
- Sistema de logo (`gimg brand`, D37): `matte` recorta el fondo plano de un emblema generado (`--holes` vacía también
  lo encerrado), `trace` lo vectoriza a SVG con la paleta de la marca o en una tinta, `wordmark` convierte el nombre
  en trazados con una fuente instalada, `lockup` compone emblema y nombre en horizontal o vertical y `system` hace
  todo de una vez con su hoja de contactos. El nombre necesita `rsvg-convert`; el resto, solo Python.
- Taller «Sistema de logo» en la pestaña Marca: los mismos pasos desde un intento del proyecto, con vista previa sobre
  claro y oscuro, y «Guardar» en los datos del proyecto o en su carpeta `brand.dir`. Rutas nuevas de la API:
  `GET /api/projects/{p}/brand`, `POST .../brand/matte`, `trace`, `wordmark`, `lockup` y `save`, y
  `GET .../brand/files/{name}/{file}`.
- `tileable` (`xy`, `x` o `y`) en el perfil y en el pedido: texturas sin costura.
- Modelo `zimage-turbo-q6` (Z-Image-Turbo, Apache-2.0) en el catálogo.

### Corregido

- `gimg work` ya no se rinde cuando solo encuentra sondeos compartidos de `worker.lock` (`_single_worker` sigue
  esperando); si un sondeo no se suelta nunca, falla a los pocos segundos con `worker.already_running` en vez de girar
  para siempre.
- La barra de progreso indeterminada usa `--accent`, con contraste suficiente sobre su pista en el tema oscuro.
- Cuando otro CLI acaba de reemplazar el servicio por uno de otro código, el CLI que esperaba lo conserva y ahora lo
  avisa (antes no decía nada).

## [0.4.1] - 2026-11-06

### Corregido

- Al arrancar dos CLI a la vez sobre un servicio de una versión vieja, a veces quedaba el viejo: los sondeos de
  `worker.lock` y `serve.lock` toman el cerrojo compartido y el servicio en marcha se reconoce por el pid de `serve.json`.
- `arrancar.sh` (y `gimg ui`) reemplaza el servicio en marcha si su código es más viejo, aunque la versión sea la
  misma: `/api/health` y `serve.json` llevan `build`, una huella del código. Con un trabajo en marcha, solo avisa.

## [0.4.0] - 2026-11-05

### Añadido

- `releases.py`: notas de release desde los dos CHANGELOG y comprobación de que la versión de `origin/main` tiene
  etiqueta `vX.Y.Z` y release de GitHub.
- Licencia MIT (`LICENSE`); los modelos del catálogo conservan su propia licencia.
- `arrancar.sh`: abre la interfaz con doble clic o desde el sandbox de VS Code (fija las carpetas de configuración y datos).
- Pruebas de la interfaz en un Chrome headless (`tests/test_ui_browser.py`), sin generar imágenes; se saltan sin Chrome.
- Plantillas elegibles por perfil (F4b): `compose.templates`, `zone` y `textColor`; `gimg templates`, `--template` en
  `compose` y `attempt new`, rutas de la API y un selector de plantilla por intento en la interfaz (también en el
  panel de retoque). El chip de contraste mide con la zona y el color de texto de la plantilla.
- Editor de elementos en la interfaz (F4c): mover y redimensionar titular, logo y adornos de un intento compuesto con
  puntero o teclado, chip de contraste en vivo por texto, aplicar, volver a la plantilla y guardar como plantilla nueva
  (local o del proyecto), exportar las plantillas locales. `GET …/templates` trae los `elements` de cada plantilla.
  Sustituye a la previsualización HTML de los textos.
- Panel de nuevo pedido y vistas de F4d en la interfaz: perfil, prompt, número, borrador, plantilla y modelo (los
  bloqueados, desactivados con su motivo), «Copiar de…» y aviso de palabras prohibidas; pestaña Piezas (los perfiles
  del proyecto), pestaña Marca de solo lectura con el resultado de `/check`, selector de modelo en el retoque y, en
  el cajón de la cola, subir, bajar y arriba del todo más «Vaciar cola» con confirmación. `POST …/orders` y
  `gimg order submit` aceptan `model`.

## [0.3.0] - 2026-11-05

### Añadido

- Núcleo (F1): proyectos registrados (`gimg project add|remove|list`), pedidos por perfil con intentos, notas,
  estados, elegir y deshacer (`gimg order submit|list|show`, `gimg attempt new|mark|note`, `gimg choose`,
  `gimg undo`), con la configuración del proyecto y los pedidos validados contra su JSON Schema.
- Cola persistente y trabajador (`gimg queue list|cancel|move|clear`, `gimg work`), con límites sobre lo fijado,
  registro por intento con estimado, errores de esquema en la cola y recuperación de lo interrumpido.
- Entrega al elegir un intento: copia al destino del perfil en el proyecto, manifiesto, cerrojo propio y restauración
  al deshacer (`gimg/delivery.py`). CLI `python3 -m gimg` en español e inglés, con salida `--json`.
- Motor real (F2): `SdCppEngine`, que lanza `sd-cli` (stable-diffusion.cpp) como proceso, con progreso en la cola,
  vista previa, registro por intento y chunk `gimg` en el PNG; el trabajador mata el grupo de `sd-cli` ante
  SIGTERM/SIGHUP.
- Protecciones del motor: memoria libre previa (`min_free_mb`), comportamiento ante Ollama (`engine.ollama`:
  `abort` o `unload`) y vigilante del controlador sin memoria.
- Catálogo de modelos (`gimg/models.json`) y perfiles de máquina (`gimg/machine_profiles/steam-deck.json`, con
  `engine.*`), que resuelven modelo y máquina; `instalar.sh` instala el motor y los modelos `installDefault`, y
  `gimg doctor` (con `--verify`) diagnostica el entorno con la orden que lo arregla.
- Borradores (`draft` en el perfil y el pedido, `--draft`; no elegibles) e img2img (`initImage`, `strength`).
- Composición (`gimg compose`, `recompose`): `text` en el pedido, imagen cruda y compuesta (titular, logo y adornos) con
  fuentes comprobadas en `gimg doctor`.
- Medida de marca (`gimg measure`, `--project`) con paleta, signalstats, distancia a la referencia y contraste WCAG;
  `brand.palette` en el proyecto; `gimg sheet` genera hojas de contactos.
- `examples/` con configuración y pedidos de siete proyectos, y hoja de estilo mínima por proyecto con su plantilla.
- API HTTP local y servicio (`gimg serve`, `--detach`, `--status`, `--stop`, `--idle-min`): proyectos, pedidos,
  intentos, elegir y deshacer, componer, medir y cola, con acceso solo local, comprobaciones de Host, Origin y
  Content-Type y errores en JSON en español e inglés. Documentada en `docs/api.md`.
- Arranque bajo demanda del servicio (`GIMG_AUTOSTART=0` lo apaga) y `gimg ui`, que abre la interfaz.
- `GET /api/projects` añade `profiles`, `orders` y `delivered` por proyecto; el pedido y las respuestas de
  `choose`/`undo` añaden `deliveredTo` (ruta relativa a la raíz del proyecto).
- Un test que comprueba que cada ruta registrada aparece en `docs/api.md`.

## [0.1.0] - 2026-10-25

### Añadido

- JSON Schema de la configuración del proyecto, el pedido y el perfil de máquina.
- Preajuste de perfil de máquina `steam-deck`.
- Validador mínimo de JSON Schema con la biblioteca estándar.
- Textos visibles en español e inglés.
- Tests unitarios.
