# Changelog

[Español](CHANGELOG.es.md)

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
