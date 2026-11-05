# Retro de `release-install` (2026-11-05)

**Estado:** pendiente de la decisión de la persona.

Tarea: `release.yml` falló al etiquetar v0.4.0 porque no instalaba `ffmpeg`/`rsvg-convert` (`ciInstall`). La
revisión de fase 1 encontró otro desajuste de la misma clase: `release.yml` pasaba el check con Python 3.10 y
`check.yml` con el del runner. Gasto de la tarea: 17 llamadas, 52k de contexto medio, sin compactaciones
(`gw-opt-tokens`, sin propuestas).

## Candidatos, de más a menos grave

### P1 · Comprobaciones automáticas: un test que compare `release.yml` con `check.yml` (proyecto)

Los dos fallos vienen de que `release.yml` copia a mano partes de `check.yml` y se desvía. El test actual solo busca
dos cadenas. Propuesta: en `tests/test_releases.py`, comparar el bloque `run:` de los pasos «Install» y «Check» de
los dos workflows (normalizando espacios) y exigir que `release.yml` no tenga `setup-python` mientras `check.yml` lo
condicione a `pyproject.toml`/`requirements*.txt`. Coste: un test de unas 20 líneas, stdlib. Riesgo: ninguno; falla
si alguien cambia uno de los dos workflows a propósito, y entonces se actualizan los dos.

### P2 · Para Galivelop-workflow: `release.yml` que reutilice `check.yml` (general)

`release.yml` es del proyecto, pero `check.yml` lo copia el flujo y no se parchea aquí. El arreglo de fondo va al
flujo: `check.yml` con `on: workflow_call` y `release.yml`
con un job `check` que lo llame (`uses: ./.github/workflows/check.yml`) y `needs: check` antes de crear la release.
Desaparece la copia y con ella P1. No se parchea aquí: va como propuesta al flujo.

### P3 · Economía de herramientas: lanzar `check.sh` después del último cambio (leve, sin cambio)

El primer `check.sh` se lanzó antes de los arreglos de la revisión y no quedó apuntado (el árbol cambió), así que
hubo que repetirlo (~3,5 min). Ya lo avisa el propio script; no hace falta otra regla.

## Lo que funcionó

- `code-review --max-findings all` encontró el desajuste de Python, que el arreglo original no había visto.

## For Galivelop-workflow

- P2: `check.yml` invocable con `workflow_call` y `release.yml` que lo llame, en lugar de copiar sus pasos.
