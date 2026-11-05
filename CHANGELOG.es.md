# Registro de cambios

[English](CHANGELOG.md)

Aquí se apuntan todos los cambios notables del proyecto.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Añadido

- Plantillas elegibles por perfil (F4b): `compose.templates`, `zone` y `textColor`; `gimg templates`, `--template` en
  `compose` y `attempt new`, rutas de la API y un selector de plantilla por intento en la interfaz (también en el
  panel de retoque). El chip de contraste mide con la zona y el color de texto de la plantilla.

## [0.3.0] - 2026-11-05

### Añadido

- API HTTP local y servicio (`gimg serve`, `--detach`, `--status`, `--stop`, `--idle-min`): proyectos, pedidos,
  intentos, elegir y deshacer, componer, medir y cola, con acceso solo local, comprobaciones de Host, Origin y
  Content-Type y errores en JSON en español e inglés. Documentada en `docs/api.md`.
- Arranque bajo demanda del servicio (`GIMG_AUTOSTART=0` lo apaga) y `gimg ui`, que abre la interfaz.
- `GET /api/projects` añade `profiles`, `orders` y `delivered` por proyecto; el pedido y las respuestas de
  `choose`/`undo` añaden `deliveredTo` (ruta relativa a la raíz del proyecto).
- Un test que comprueba que cada ruta registrada aparece en `docs/api.md`.

## Antes de 0.3.0 (F0)

### Añadido

- JSON Schema de la configuración del proyecto, el pedido y el perfil de máquina.
- Preajuste de perfil de máquina `steam-deck`.
- Validador mínimo de JSON Schema con la biblioteca estándar.
- Textos visibles en español e inglés.
- Tests unitarios.
