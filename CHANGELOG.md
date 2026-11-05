# Changelog

[Español](CHANGELOG.es.md)

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Delete from the interface (F4e.1b): "Delete" with a yes/no confirmation on each attempt, on its composition (it
  warns that the delivery already made does not change if the attempt is the chosen one) and on each template (it
  says how many attempts use it and, for a project template, that the change stays in the repository without a
  commit); "Hide" / "Show" per element in the element editor.

### Fixed

- The element editor now reads `hidden` from the applied layout and sends it again, so applying or saving as a template
  no longer shows an element hidden from the command line.

## [0.4.0] - 2026-11-05

### Added

- `releases.py`: release notes from the two CHANGELOGs and a check that the `origin/main` version has a `vX.Y.Z` tag
  and a GitHub release.
- MIT license (`LICENSE`); the catalog models keep their own licenses.
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

- Core (F1): registered projects (`gimg project add|remove|list`), per-profile orders with attempts, notes, states,
  choose and undo (`gimg order submit|list|show`, `gimg attempt new|mark|note`, `gimg choose`, `gimg undo`), with the
  project config and orders validated against their JSON Schema.
- Persistent queue and worker (`gimg queue list|cancel|move|clear`, `gimg work`), with limits on what is set, a
  per-attempt log with an estimate, schema errors in the queue and recovery of interrupted work.
- Delivery when an attempt is chosen: copy to the profile's target in the project, manifest, own lock and restore on
  undo (`gimg/delivery.py`). `python3 -m gimg` CLI in Spanish and English, with `--json` output.
- Real engine (F2): `SdCppEngine`, which launches `sd-cli` (stable-diffusion.cpp) as a process, with queue progress,
  preview, per-attempt log and a `gimg` chunk in the PNG; the worker kills the `sd-cli` group on SIGTERM/SIGHUP.
- Engine protections: free memory before starting (`min_free_mb`), Ollama handling (`engine.ollama`: `abort` or
  `unload`) and a watchdog for the out-of-memory driver.
- Model catalog (`gimg/models.json`) and machine profiles (`gimg/machine_profiles/steam-deck.json`, with `engine.*`),
  which resolve model and machine; `instalar.sh` installs the engine and the `installDefault` models, and
  `gimg doctor` (with `--verify`) diagnoses the environment with the fixing command.
- Drafts (`draft` in the profile and the order, `--draft`; not choosable) and img2img (`initImage`, `strength`).
- Composition (`gimg compose`, `recompose`): `text` in the order, raw and composed images (headline, logo and
  ornaments), with fonts checked by `gimg doctor`.
- Brand measurement (`gimg measure`, `--project`) with palette, signalstats, distance to the reference and WCAG
  contrast; `brand.palette` in the project; `gimg sheet` builds contact sheets.
- `examples/` with config and orders for seven projects, and a minimal style sheet per project with its template.
- Local HTTP API and service (`gimg serve`, `--detach`, `--status`, `--stop`, `--idle-min`): projects, orders,
  attempts, choose/undo, compose, measure and queue, with localhost-only access, Host/Origin/Content-Type checks and
  JSON errors in Spanish and English. Documented in `docs/api.md`.
- On-demand start of the service (`GIMG_AUTOSTART=0` turns it off) and `gimg ui`, which opens the interface.
- `GET /api/projects` adds `profiles`, `orders` and `delivered` per project; the order and the answers of
  `choose`/`undo` add `deliveredTo` (path relative to the project root).
- A test that checks every registered route appears in `docs/api.md`.

## [0.1.0] - 2026-10-25

### Added

- JSON Schemas for project config, order and machine profile.
- `steam-deck` machine profile preset.
- Minimal stdlib JSON Schema validator.
- User-facing texts in Spanish and English.
- Unit tests.
