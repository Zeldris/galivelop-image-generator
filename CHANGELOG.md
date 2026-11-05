# Changelog

[Español](CHANGELOG.es.md)

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `arrancar.sh`: opens the interface by double click or from the VS Code sandbox (sets the config and data folders).
- Interface tests in a headless Chrome (`tests/test_ui_browser.py`), without generating images; skipped without Chrome.
- Selectable templates per profile (F4b): `compose.templates`, `zone` and `textColor`; `gimg templates`,
  `--template` on `compose` and `attempt new`, API routes and a per-attempt template selector in the interface
  (also in the retouch panel). The contrast chip measures with the template's zone and text color.
- Element editor in the interface (F4c): move and resize the headline, logo and ornaments of a composed attempt with
  pointer or keyboard, live contrast chip per text element, apply, back to the template and save as a new template
  (local or project), export of local templates. `GET …/templates` lists the `elements` of each template. It replaces
  the HTML text preview.
- New order panel and F4d views in the interface (F4d): profile, prompt, count, draft, template and model (blocked
  models disabled with their reason), "copy from…", banned-word warning; a Pieces tab (the project's profiles), a
  read-only Brand tab with the `/check` result, a model selector in the retouch panel, and move up/down/top plus a
  confirmed "clear queue" in the queue drawer. `POST …/orders` and `gimg order submit` accept `model`.

## [0.3.0] - 2026-11-05

### Added

- Local HTTP API and service (`gimg serve`, `--detach`, `--status`, `--stop`, `--idle-min`): projects, orders,
  attempts, choose/undo, compose, measure and queue, with localhost-only access, Host/Origin/Content-Type checks and
  JSON errors in Spanish and English. Documented in `docs/api.md`.
- On-demand start of the service (`GIMG_AUTOSTART=0` turns it off) and `gimg ui`, which opens the interface.
- `GET /api/projects` adds `profiles`, `orders` and `delivered` per project; the order and the answers of
  `choose`/`undo` add `deliveredTo` (path relative to the project root).
- A test that checks every registered route appears in `docs/api.md`.

## Before 0.3.0 (F0)

### Added

- JSON Schemas for project config, order and machine profile.
- `steam-deck` machine profile preset.
- Minimal stdlib JSON Schema validator.
- User-facing texts in Spanish and English.
- Unit tests.
