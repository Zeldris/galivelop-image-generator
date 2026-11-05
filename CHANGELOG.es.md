# Registro de cambios

[English](CHANGELOG.md)

Aquí se apuntan todos los cambios notables del proyecto.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [0.4.0] - 2026-11-05

### Añadido

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
