# Retro 2026-10-25: aplicar el flujo y diseño del generador

**Estado:** aprobada por la persona el 2026-10-25; R5 aplicada en la rama; R1-R4 y R7 propuestas al flujo
(abajo, para `gw-harvest`); R6 sin cambio (ya es criterio de F0).

Sesión `a0f496d5`: paso 1 (flujo v0.4.0 aplicado) y paso 2 (diseño D1-D26, fases F0-F5, ADR 0001-0002).
Gasto medido en `.claude/gw/opt-tokens.md` (referencias medidas).

## Del proyecto

- **R5** (aplicada): `AGENTS.md`, "Reglas del proyecto", tenía `_(por rellenar)_`, una línea que se carga en cada
  llamada sin cambiar nada; ahora es un puntero a `docs/plan.md`. La línea de instalar se rellena en F0.
- **R6** (sin cambio): el check solo hace `bash -n` de los ganchos; F0 lo cambia por `python3 -m unittest` y la
  validación de los ejemplos con los esquemas, como ya dice su fila en `docs/plan.md`.

Salió bien: la lectura de WMF con Explore en haiku, `domain-modeling` detectando el choque de «encargo» y las rondas
de `grilling`.

## Para Galivelop-workflow

- **R1 · `selector` no se aplicó al empezar una tarea.** El paso 2 empezó leyendo otro repo en la sesión principal,
  sin `selector`, `orchestrate-dealer` ni `grilling`, hasta que la persona interrumpió («usa los pasos del
  workflow»). La línea de la plantilla de `CLAUDE.md` existe pero su redacción no dispara. Propuesta: «Antes de la
  primera herramienta de cada tarea nueva: una línea con skill + modelo (`selector`)», y que `recuperar.py --estado`
  lo recuerde en su salida.
- **R2 · `/code-review` se ahoga en una rama que aplica el flujo.** 9.600 líneas copiadas del flujo taparon 4
  archivos propios; el revisor leyó ~500 y paró. Propuesta: un modo de `es-codigo.sh` (o de la fase 1 de
  `AGENTS.md`) que separe los archivos del flujo (su manifiesto) de los propios: los propios enteros, los del flujo
  solo su delta desde la marca de revisión del propio flujo.
- **R3 · `aplicar.py` aplica una versión sin publicar sin avisar.** La fuente estaba en una rama de trabajo del flujo
  (`ccr-6dfbc880-ddr41g`), no en un tag ni en `main`; luego `--check` falló solo porque el flujo avanzó. Propuesta:
  avisar cuando la fuente no es una versión publicada y guardar el commit de origen, para que `--check` compare con
  él.
- **R4 · `domain-modeling/ADR-FORMAT.md` trae los encabezados en inglés** («Consequences», «Considered Options») en
  un proyecto `es`. Propuesta: que diga que van en el `language` del proyecto, o traer la versión `es`.
- **R7 · Revisión del delta sin marca `26494a1..d227bbf`** (subagente revisor, solo lectura):
  - MEDIO · `templates/githooks/pre-commit`, `KEY_FORMATS`: el borde izquierdo `(^|[^A-Za-z0-9])` deja pasar una
    clave pegada a una letra o dígito (`"x=\nsk-ant-…"`, `a%3Dsk-…`, `1AKIA…`), que antes se detectaba; el arreglo
    contra `musk-tells-…` abrió el hueco. Comprobado con el grep del gancho.
  - LEVE · `templates/githooks/commit-msg:36`: `git diff --cached --name-only` sin `-z` ni `core.quotepath=false`
    escapa los nombres con acentos y `grep -Fx "$log"` no ve una bitácora como `docs/bitácora.md`; sale con 0.
  - LEVE · `templates/githooks/commit-msg:48` frente a `scripts/prepush-ramas.sh:103`: uno pide la fecha de hoy y el
    otro la de autor (`%as`); un `--amend` al día siguiente con la bitácora en el índice choca. Deducido leyendo, no
    ejecutado.
  - LEVE · `scripts/doctor.py:43-51`: el escaneo de invisibles no cubre U+2060-2064, U+00AD, U+180E, U+FE00-FE0F ni
    los Tag U+E0000-E007F, el vector habitual de instrucciones ocultas.
  - LEVE · `scripts/revision-antes-de-main.sh`, `from_bash`: con continuación `\<nl>` las dos lecturas (`glue`)
    devuelven la misma acción y `handle` la procesa dos veces; mismo resultado, doble de llamadas.
  - Sin hallazgos: el prefiltro sin `SUSPECT` (34 casos, entradas de 200 KB en 0,02-0,33 s), `recuperar.py`, el
    tamaño de `AGENTS.md`/`CLAUDE.md` en `doctor.py`, `pre-push` y `comprobar.yml`.
