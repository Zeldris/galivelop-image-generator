<!-- galivelop-workflow v0.4.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `main` (F1 fusionada); F2 en una rama nueva `f2-motor` |
| **Fase / tarea** | F1 Núcleo cerrada y en `main`; siguiente fase F2 Motor real (`docs/plan.md`, fila F2) |
| **Último punto estable** | F1 en `main` (`0d02f51`, marca de revisión sobre `fe7d968`): F1.1-F1.6, revisión completa con 14 arreglos, retro aplicada; check en verde, 282 tests |
| **Siguiente paso** | F2: `git switch -c f2-motor --no-track origin/main` y `git push -u origin f2-motor`; el contrato «F2 en detalle» lo escribe un subagente `opus` y la sesión principal lo revisa y lo lleva a la persona (`.claude/gw/orchestrate-dealer.md`); apuntar el presupuesto de compactaciones |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |
| **Tarea en curso · `f2-motor`** | F2.0 pruebas de concepto e interfaz F4 en propuesta (13 decisiones confirmadas). Antes de `main`: fases 1, 2 y 3 hechas (arreglos de la revisión de la fase 2 y marca con `revisado.sh`). Falta: CI en verde (la persona hace `! ~/.local/bin/gh auth login`; luego `~/.local/bin/gh run list --branch f2-motor`) y su confirmación para ir a `main`. Presupuesto: 4 compactaciones (5 gastadas) |

Con `logRows` en `.claude/gw.json`, cada rama escribe solo en su fila de esta tabla, como mucho 600 caracteres, con
la forma ``| **Tarea en curso · `<rama>`** | tarea, fases antes de `main`, qué falta y siguiente paso |``; el push lo comprueba.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-10-25 — F1 (`f1-nucleo`) a `main` por push directo con confirmación de la persona: CI no comprobado (sin `gh` en esta máquina; en F0, sin cuota), **comprobado solo en local** (check del `pre-push` sobre `0d02f51`). Tres fases hechas, marca en `fe7d968`.
2. 2026-10-25 — F0 (`f0-esqueleto`) a `main` por push directo con confirmación de la persona: CI sin cuota (pagos fallidos), **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `17e28eb`.
3. 2026-10-25 — `diseno-generador` a `main` por push directo con confirmación de la persona: CI sin cuota, **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `b111e4f`.
4. 2026-10-25 — Diseño ronda 3 aprobada: clave del pedido, retoque de prompt, entrega PNG, `gimg`, seguridad, registro opt-ai.
5. 2026-10-25 — Diseño ronda 2 aprobada: pedido/intentos/elegida, cola, perfil de máquina, es+en, ADR 0001-0002.

## Pendiente

- **Carpeta de datos en flatpak:** VS Code en flatpak fija `XDG_DATA_HOME=~/.var/app/com.visualstudio.code/data`, y `gimg` (y `ronda.sh`) lanzados desde su terminal usan otra carpeta de datos que desde una terminal normal (`docs/registros/contenido/r0-humo.md`); decidir en F2.5 (`gimg doctor` lo avisa, o se ignora el XDG de flatpak).
- **Leves de la revisión de F0** (no se revisan más en este PR):
  - F2: `width`/`height` sin `multipleOf` (lo que exija `sd-cli` por modelo); el validador aún no lo soporta.
  - `propertyNames` solo pasa el `pattern` del primer error: si falla por otra cosa, el mensaje sale vacío.
- **Leves de la revisión de `941efa9` (componer/medir, F2.0):** pruebas de Lab/umbral y del recorte cover con píxeles; `fuentes.sh` sin test, `mktemp` fuera del destino y descarga de `main` sin fijar; `HEX` con `$` en vez de `fullmatch`; viewBox `1.2.3` o `0 0 0 0` da traza; `esc` no quita caracteres de control; salida `.svg` machaca el SVG de depuración; sin `timeout` en subprocesos; sin `piloto/fuentes/` cae a otra fuente sin avisar; `ffprobe` sin `which`; signalstats es BT.601 rango limitado (calibrar igual en F2.9).
- **Referencias de estilo (antes de F5):** ronda del piloto con `sd-cli` y 1-2 imágenes de referencia sobre Tarkor,
  medida con D31; si mejora el % de paleta sin estropear el contraste, entra en F5 (fila «Referencias» de la pestaña
  Marca). Confirmado por la persona el 2026-10-27 (`docs/interfaz/propuesta.md`, decisión nueva 1).
- **Marca de Tarkor:** el estilo sale desaturado en todos los formatos (SATAVG 5-7 frente al 15-30 del juego;
  `r5-og-bajo` arregla la luz, YAVG 66, pero no el color): otra vuelta del prompt con la persona
  (`docs/registros/contenido/r5-piezas.md`).
- **Leves de la revisión de `3dc054d` (piezas/componer, F2.0):** avatar rasterizado con `-w` y `-h` deforma un logo no
  cuadrado; `'640x320' in name` frágil (un `2640x320`); sin tests de `main()` con piezas, `paleta_de`, avatar,
  `pagina.medidas` ni `ronda.sh r5`; la prueba del lockup no cubre la rama en que manda el ancho de la columna.
- **Aviso de presupuesto de compactaciones (cambio local del flujo):** `.claude/gw/scripts/recuperar.py` gana
  `compaction_budget`; proponerlo al repo de Galivelop-workflow para que una actualización del flujo no lo pise.
- **Leves de la revisión de la fase 2 (`cf1191f`, `0ebd00c`; no se revisan más en este PR):** el presupuesto se compara con las compactaciones de la sesión, que vuelven a 0 tras un `/clear` (no con las «gastadas» de la fila); `compaction_budget` vuelve a cargar la configuración y la bitácora, y solo lee la fila con `logRows`; el lint de shell da falso positivo con un comentario al final de una línea que nombre lo prohibido; `leer-entero` no cubre `cat docs/plan.md` por Bash.
- **Leves de la revisión de `bb7719a` (piloto, fase 1 antes de `main`; no se revisan más en este PR):** `piezas.pieza`
  mide el fondo limpio con `medir.medir` y tira su `signalstats` (basta `contraste_zona`); el velo repite `rect` en las
  cuatro zonas y parchea `offset="0.55"` con `replace`; `recorte_cover` es código muerto; sin tests de `logos.py`,
  `fuentes.sh` ni `pagina.pagina_ronda/resumen/tiempos`; las páginas del piloto solo en español (`visibleLanguages`
  es/en: traducir o declararlas internas); `ver.py` no resuelve enlaces simbólicos dentro de `piloto/`; algún
  `read_text` de `componer.py` sin `encoding`. **Para F2.8:** el piloto mete el fondo en base64 dentro del SVG y lo
  rasteriza entero con rsvg; D28 pide que rsvg haga solo la capa y ffmpeg la superponga: no portarlo tal cual.
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
