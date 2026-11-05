# Registro de cambios

[English](CHANGELOG.md)

Aquí se apuntan todos los cambios notables del proyecto.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

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
