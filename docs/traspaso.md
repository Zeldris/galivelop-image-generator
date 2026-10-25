<!-- galivelop-workflow v0.4.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `f1-nucleo` |
| **Fase / tarea** | F1 Núcleo: contrato y pasos F1.1-F1.6 en `docs/plan.md` («F1 en detalle»); compactaciones: presupuesto 1, llevadas 0 |
| **Último punto estable** | F1.6 hecho: `gimg/cli.py` + `python3 -m gimg`, `--json` y `--lang`, test de extremo a extremo (`tests/test_cli.py`), README es/en con el uso; check en verde, 267 tests. F1 completa, sin revisar. Revisión de F1, arreglos de entrega: claves `error.delivery.*` y `error.project.bad_name` + test que exige texto a todo código lanzado, cerrojo de entrega en el directorio de datos (choose/undo enteros bajo él), destino sin `.git`/config, colisión `delivery.target_taken`; 273 tests. Arreglos de la revisión de F1 (cola/CLI/límites): prompt+estilo validado en `attempt_specs` (`order.prompt_too_long`), errores de esquema conservados en el `error` de la entrada, motor validado antes de encolar, `config.json` ilegible traducido, `is_cancel_requested` sin recuperar, mensajes del trabajador en el idioma de la CLI; 282 tests |
| **Siguiente paso** | Fases 1 y 2 de F1 cerradas (retro `docs/registros/retro-2026-10-25-f1.md`, aplicada): fase 3, `revisado.sh`, push, descripción del PR con `pr`; el PR a `main` solo con confirmación de la persona |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |

Con `logRows` en `.claude/gw.json`, cada rama escribe solo en su fila de esta tabla, como mucho 600 caracteres, con
la forma ``| **Tarea en curso · `<rama>`** | tarea, fases antes de `main`, qué falta y siguiente paso |``; el push lo comprueba.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-10-25 — F0 (`f0-esqueleto`) a `main` por push directo con confirmación de la persona: CI sin cuota (pagos fallidos), **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `17e28eb`.
2. 2026-10-25 — `diseno-generador` a `main` por push directo con confirmación de la persona: CI sin cuota, **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `b111e4f`.
3. 2026-10-25 — Diseño ronda 3 aprobada: clave del pedido, retoque de prompt, entrega PNG, `gimg`, seguridad, registro opt-ai.
4. 2026-10-25 — Diseño ronda 2 aprobada: pedido/intentos/elegida, cola, perfil de máquina, es+en, ADR 0001-0002.
5. 2026-10-25 — Diseño ronda 1 aprobada: servicio local independiente, sin dominio, Python stdlib, WMF piloto (`docs/plan.md`).

## Pendiente

- **Leves de la revisión de F0** (no se revisan más en este PR):
  - F2: `width`/`height` sin `multipleOf` (lo que exija `sd-cli` por modelo); el validador aún no lo soporta.
  - `propertyNames` solo pasa el `pattern` del primer error: si falla por otra cosa, el mensaje sale vacío.
- **Leves de las revisiones de F1:**
  - `orders._FULL_PARAMS` repite a mano límites de `width`/`height`/`model` en vez de usar `$defs/profile` del esquema de la configuración del proyecto.
  - Un lector (`list`/`get`/`enqueue`) que toma `worker.lock` un instante hace que un trabajador que arranca falle con
    `worker.already_running`: reintentar el cerrojo una vez tras ~100 ms o documentarlo.
  - Si `add_attempt` falla después de escribir `order.json`, el `finally` del trabajador borra la imagen y queda un
    intento con `queueEntry` sin imagen: comprobar con `attempt_for_entry` antes de borrar.
  - `queue.is_cancel_requested` lee la cola entera bajo cerrojo cada 20 ms durante la generación; espaciar el sondeo si la cola crece.
  - `cli.main(['--lang','fr'])` lanza SystemExit en vez de devolver 2 (`_prescan_lang` fuera del try) y su uso no habla de las órdenes.
  - `delivery.undo` prepara la entrega antes de que `orders.undo` rechace un destino descartado: con la imagen borrada sale `delivery.source_missing` en vez de `order.undo_discarded`.
  - Al cambiar `delivery.template`/`dir` y volver a elegir, el archivo entregado en la ruta antigua queda huérfano.
  - `undo` hasta `null` no borra las subcarpetas vacías que creó la entrega.
  - Un dato, un sitio: el rango de `count` (1-50) en `attempt_specs` y `paths.MAX_KEY` repiten el esquema del pedido (junto con `_FULL_PARAMS`).
  - Reutilización: escritura atómica copiada en `fsutil.write_json`, `delivery._copy` y `FakeEngine.generate`; `_now()` en cuatro módulos; `delivery._find` reimplementa `orders._attempt`; `worker._single_worker` repite `queue._no_worker`; `cli.opt()` es igual a `arg()`.
  - Eficiencia: `choose`/`undo` releen y validan la configuración, el pedido y el manifiesto varias veces.
  - `GIMG_CONFIG_HOME`/`GIMG_DATA_HOME` relativas dependen de la carpeta actual (las XDG relativas sí se ignoran).
  - `orders.mark` no toma el cerrojo de la entrega: un `mark` a mitad de `choose` lo revierte con `order.choose_discarded` (mitigado).
  - `delivery.target_taken` también bloquea un `undo` hasta `null` si otra entrada del manifiesto comparte `file`
    (tras cambiar la plantilla), y compara sin `casefold` (no ve colisiones en discos sin mayúsculas).
  - `order submit` guarda el pedido antes de que `attempt_specs` rechace un prompt+estilo largo: queda sin encolar.
- **Cuando la persona avise:** revisar las actualizaciones de Tarkor (otro repo) sobre su generador de imágenes: lo lee
  un subagente `Explore` que devuelve un resumen con rutas (`orchestrate-dealer`); desde aquí no se modifica.
- El flujo copiado es la 0.4.0 **sin publicar** (rama `ccr-6dfbc880-ddr41g` del flujo, commit `d227bbf`; su `main` está en
  0.3.0): `/gw-update` cuando la 0.4.0 salga publicada.
- Proponer al flujo (`gw-harvest`) lo de `docs/registros/retro-2026-10-25-diseno.md` (R1-R4, R7) y de
  `docs/registros/retro-2026-10-25-f0.md` (R1, R3, R4); el hallazgo
  MEDIO de R7 (claves pegadas a una letra en `pre-commit`) conviene arreglarlo antes de publicar la 0.4.0.
- Proponer al flujo (`gw-harvest`) R3a y R3b de `docs/registros/retro-2026-10-25-f1.md`.
- Proponer al flujo (`gw-harvest`) una operación de imagen en el `log-format.md` de `opt-ai` (D26).

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit .githooks/pre-push .githooks/commit-msg` y `python3 -m unittest discover -s tests -t .`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recuperar.py --estado`.
