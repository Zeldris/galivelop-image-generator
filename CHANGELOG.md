# Changelog

[Español](CHANGELOG.es.md)

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The interface is light by default (it was dark); the dark theme stays available. Palette by roles from the r9 brand
  sheet.
- New interface fonts: Big Shoulders Display, Literata and JetBrains Mono replace Inter and Sora.
- Logo and favicon redrawn (r9 brand sheet): flat tile, light and dark lockups and line versions.
- The product's visible name is "Galivelop IG" (GVIG) in the README and in `cli.description` (D38); the repository,
  the package and the command stay `galivelop-image-generator` and `gimg`.
- `gimg brand wordmark` and `system`, and the "Logo system" workshop, space the letters 0.01 em by default (it was
  0.12), the family's tracking.

### Added

- `gimg queue pause` and `gimg queue resume`: pausing leaves the `queue.paused` mark in the data directory; the worker
  finishes the image in progress and takes no other, `gimg serve` launches no worker meanwhile and `queue list` says
  so. On resume the service relaunches the worker at its next beat (a few seconds). While paused, what is queued does
  not keep the service alive, and `gimg queue resume` starts it again if anything is still queued. The queue drawer
  of the interface has a "Pause queue" / "Resume queue" button and the queue pill says "paused".
- `gimg brand system --margin` (free space around both lockups) and `--mono` (lockups with the one-ink emblem: the
  whole lockup in `currentColor`, as the family's sheets ask).
- Example profiles for the channels the brand sheets ask for: `lateral` 704×1344 (Windows installer), `linkedin`
  1584×396, `discord` 960×540 and `panorama` 1600×900 in `examples/tarkor/`, and `icon` 512×512 in `examples/toveriai/`.
- `gimg export IMAGE OUT`: copies a delivered PNG to lossless WebP, ICO (one PNG per side, 16 to 256) or 24-bit BMP
  without alpha (over `--background`), or to a PNG of another size; `--size` crops around the centre and scales
  down, never up. Pure-Python encoders; the delivery stays the PNG with its provenance.
- English translation of the local API: `docs/en/api.md`; the API doc test now checks both languages.
- Logo system (`gimg brand`, D37): `matte` removes the flat background of a generated emblem (`--holes` also empties
  what is enclosed), `trace` turns it into an SVG with the brand palette or in one ink, `wordmark` turns the name into
  paths with an installed font, `lockup` composes emblem and name horizontally or vertically, and `system` does it
  all in one go with its contact sheet. The name needs `rsvg-convert`; the rest, only Python.
- "Logo system" workshop in the Brand tab: the same steps from an attempt of the project, previewed on light and
  dark, and "Save" to the project's data or to its `brand.dir` folder. New API routes:
  `GET /api/projects/{p}/brand`, `POST .../brand/matte`, `trace`, `wordmark`, `lockup` and `save`, and
  `GET .../brand/files/{name}/{file}`.
- `tileable` (`xy`, `x` or `y`) in the profile and in the order: seamless textures.
- Model `zimage-turbo-q6` (Z-Image-Turbo, Apache-2.0) in the catalogue.

### Fixed

- `gimg work` no longer gives up when it only finds shared probes of `worker.lock` (`_single_worker` keeps waiting);
  if a probe never lets go, it fails after a few seconds with `worker.already_running` instead of spinning forever.
- The indeterminate progress bar uses `--accent`, with enough contrast on its track in the dark theme.
- When another CLI has just replaced the service with one of other code, the CLI that waited keeps it and now warns
  about it (it used to say nothing).

## [0.4.1] - 2026-11-06

### Fixed

- Two CLIs starting at once over a service of an older version sometimes kept the old one: the `worker.lock` and
  `serve.lock` probes take the shared lock and the running service is recognised by the pid in `serve.json`.
- `arrancar.sh` (and `gimg ui`) replaces the running service when its code is older, even with the same version:
  `/api/health` and `serve.json` carry `build`, a fingerprint of the code. With a job running, it only warns.

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
