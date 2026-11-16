<!-- galivelop-workflow v0.5.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `portal-marca` (desde `origin/main` `fa1076e`); el trabajo de F4e sigue en `f4e-piezas` |
| **Fase / tarea** | marca del Portal y de Tarkor (hoja nueva, `gimg brand`) |
| **Último punto estable** | `main` en `4624825` (PR #18, 2026-11-15, CI en verde); última release v0.5.0 (`529468b`, 2026-11-13) |
| **Siguiente paso** | el de la fila de `ccr-85e9d14e-zt7p8b` |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |
| **Tarea en curso · `fix-0.4.1`** | Fusionada en `main` por el PR #5 (`fa1076e`, 2026-11-06, CI en verde); etiqueta y release v0.4.1 publicadas; rama terminada. |
| **Tarea en curso · `ccr-85e9d14e-zt7p8b`** | **FM 0.6.0 Recortar (2026-11-16)**, en esta rama (el PR llevará también el diseño de FM, `55a9f88`..`8c38457`; D41, «FM en detalle» en `docs/plan.md`). Hecho: backend `gimg crop` + API, interfaz (`crop-editor.js`, `box-drag.js`), revisiones de bloque del backend (`Findings: 4`) y de la interfaz (`Findings: 7`); detalle en «Hecho». Leves en `docs/records/leves-ccr-85e9d14e-zt7p8b.md`. Fase 2: `gw-opt-tokens` hecha y aprobada (2026-11-16). Falta: asas táctiles de 44 px en un dispositivo (la persona), retro (leer-entero.py frente a whole-read.py), fase 3, release 0.6.0. Siguiente: retro, tras un `/clear`. **En la próxima sesión en local, avisar a la persona**: reanudar la cola de `hojas-repos` y, al llegar 0.7.0, centralizar los pedidos del Portal y Tarkor. |
| **Tarea en curso · `claude/marca-r9`** | Fusionada en `main` por el PR #6 (`2509674`, 2026-11-11): hoja r9 aplicada a interfaz, logos y nombre (detalle en «Hecho»); rama terminada. Queda, en otra tarea: medir una ronda plana y `og`/`social` con el lockup nuevo (entonces se quitan la copia congelada y `REDRAWN_COPY_SHA256`) |
| **Tarea en curso · `portal-marca`** | Fusionada en `hojas-repos`; sus imágenes del Portal están completas en `piloto/portal-marca/portal-web-final/portal/` (LEEME; raíz = aprobado, `svg/`, `aprobadas/`, `pendiente/`, `descartes/`). Historia de rondas, intentos aprobados y reglas en «Hecho». Falta: la sesión del Portal aplica `docs/proposals/portal/entrega-marca-2026-11-12.md`. Siguiente: nada aquí; seguir por la fila de `hojas-repos`. |
| **Tarea en curso · `hojas-repos`** | Abierta el 2026-11-12 (hojas de estilo a cada repo por la vía A; detalle en «Hecho»). **Cola del generador parada**: pendientes #832, #834-835, #812, #814, #820, #824, #826 y el mapa de Tarkor; #833 sin revisar; reanudar con `gimg serve` (o `gimg queue resume` si se pausó). **Fusionada en `main` por el PR #8 (`2e6b642`, 2026-11-12, CI en verde)**; R1 `gimg queue pause|resume` incluida, retro aprobada. Después: cola del Portal, oscuras 10/18/19/27/28, prueba A1 a 768², nota de entrega al Portal, 61 pedidos de Tarkor. Leves: botón de pausa en la UI y `_busy` en pausa, hechos en `ccr-85e9d14e-zt7p8b` (2026-11-13); tonos repetidos sin validar el hex en `docs/marcas/*/tonos.py` y `acento*.py`, también hecho allí. Siguiente: reanudar la cola y revisar lo del Portal. |

Aquí `logRows` está apagado en `.claude/gw.json`: las filas se editan a mano (`handoff.py set-row` no escribe) y no
hace falta `GW_SHARED_LOG`. Aun así, cada rama toca solo su fila salvo al cerrar o fusionar otra.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-11-16 — **FM 0.6.0 Recortar (2026-11-16, `ccr-85e9d14e-zt7p8b`):** `gimg/crop.py` + `POST …/attempts/{id}/crop` (intento derivado con `derivedFrom`; errores `crop.bad_box|outside|ratio_mismatch|bad_target|write_failed|compose_unsupported`); revisión del backend (`2b1a08e`, Findings: 4: destino que compone rechazado, alta atómica del destino, `tileable` fuera). Interfaz: `box-drag.js` extraído de `layout-editor.js`, `crop-editor.js`, «Recortar» y distintivo en `attempt-card.js`; revisión (`34a00b1`, Findings: 7). Flujo a Galivelop-workflow v0.7.0 (confirmado por la persona).
2. 2026-11-15 — **Séptima tanda (L7), 2026-11-15, `ccr-85e9d14e-zt7p8b`:** `tile` marca como `.gimg-stale-*` la copia que no pudo borrar y `recover_backups` la borra o la da como `stale`, nunca como original; la CLI usa `tile.describe_recovery` (`42987df`). `brand`: el fill de `<line>` no cuenta al aplanar, `_has_fill` = `_sets`, `lockup --force` con `cli.arg.brand_force`, validaciones compartidas, color de `lockup` con `trace._COLOR`, `brand.write_file` público, `border_color` una vez, tests de `lockup` (`9bb35cd`). Taller: `resolve_font` pide el peso a `fc-match` y acepta `.ttc`/`.otc`, límites de la UI = servidor y `PIECES` = `SYSTEM_FILES` con test (`7b3b1a6`). Sin probar con fuente real (equipo de la persona): el peso en `fc-match` y una `.ttc` renderizada. Fuera: `trace` `min_island`; `brand_force_square` sobra (mismo texto que `brand_force`).
3. 2026-11-15 — **Sexta tanda acotada de leves (`ccr-85e9d14e-zt7p8b`), elegida por la persona:** `brand square`: un `<line>` ya no hereda el `fill` de la raíz; `trace` con `max_side` bajo ya no da error de capas vacías (si todo sale vacío y hubo reducción, repite sin suavizar y con `min_island`/factor²); `tile`: lo restaurado antes de un fallo de `recover_backups` viaja en `exc.recovered` y lo dice la CLI; la copia que no se pudo borrar tras un éxito sale en `stale_backups` y la CLI pide borrarla a mano.
4. 2026-11-14 — Quinta tanda de leves de gimg (`ccr-85e9d14e-zt7p8b`, 2026-11-14): tests del gancho y de la UI (`bd26c65`); matte con anillos en `_band` y siembra desde píxeles transparentes con borde opaco (`a2d7af1`); trace mono con diagonal conexa y aviso de marco oscuro traducible en `warnings` (`55a20dd`); tile con copias `.gimg-bak-<hash>-<pid>-<ns>-<uuid>` respetadas si su proceso vive, `recovered` en la CLI y mezcla ~2× más rápida (`31f0f3a`); brand square con rgb/hsl estrictos y recortados, unidades de tono, opacidad 0 y `<g>` anidados en una pasada O(n), herencia de la raíz y comillas simples (6279e6d).
5. 2026-11-14 — `ccr-85e9d14e-zt7p8b`, cuarta tanda de leves, cinco ramas fusionadas con check en verde: `matte` solo con croma verde/magenta (distancia ≤90) en una pasada y gancho de hojas con clave por sesión/transcript y marcas limpiadas; `brand` (`_norm_color` con rgba/hsl/#rgba, alfa 0 no pinta, `fill` de la raíz, `_DECL`, pesos de Big Shoulders); `trace` mono (`_thin` sin rebabas, un color opaco y SVG vacío rechazados en todos los modos, paleta vacía, `ink=[]`, aviso de marco oscuro); `tile` (publicación todo o nada apartando el destino, tope 2048² por cabecera, borde a peso 0) y 409 de `server`; tests de la UI (cascada de foco, `sides()`, booleano de la pausa, `Page.close`).

## Pendiente

- **Leves de la fase 1 de la sexta tanda (2026-11-15):** `tile`: la copia que no se pudo borrar, en ejecuciones siguientes, `recover_backups` la da por «puede ser el original», contradiciendo el aviso anterior (el estado no queda en el nombre); `brand`: un `fill` explícito en un `<line>` sigue contando como color (aplanado de más); `trace`: `min_island` sigue en píxeles reducidos, así que con reducción una forma pequeña de un color se pierde aunque el trazo no salga vacío (dividir siempre por factor² deja de quitar motas: descartado).
- **Leves de las tandas 1-5 de `ccr-85e9d14e-zt7p8b` (2026-11-13/14):** los abiertos, en `docs/records/leves-ccr-85e9d14e-zt7p8b.md` («Tandas 1-5»); la próxima tanda los elige de ahí.
- **Huecos de `gimg` vistos en `hojas-repos` (2026-11-12):** todos hechos en `ccr-85e9d14e-zt7p8b` (`system --mono` y `--margin`, espaciado 0,01; perfiles nuevos; `gimg export` a WebP, ICO y BMP con `--crop`/`--anchor`; `measure --family`; `brand square`) salvo Big Shoulders Display sin `.ttf` en el equipo (depende del equipo de la persona). Aviso: `red-without-fix.sh` usa el stash compartido y, con varios worktrees a la vez, uno puede recoger el stash de otro (pasó el 2026-11-13, otra vez con dos subagentes: cada uno recogió el stash del otro; recuperado, nada perdido). Proponer al flujo que use `git worktree`/copia temporal en vez de `git stash`, o `--fix-at HEAD` por omisión.
- **`examples/` de developer y workflow** siguen con la identidad anterior (paleta, perfiles FLUX; `tests/test_examples.py` l.312 fija el lockup `b` de workflow); r10 de image-generator rompería `tests/test_ui.py` l.564-597 y `tests/test_brand_assets.py` l.58 al aplicarse.

- **Hueco de `gimg brand trace` (2026-11-11, `portal-marca`):** hecho en `42e7c02` (tinta = todo menos el papel; líneas de 1 px con `_thin`); quedan los leves de la tercera tanda.
- **`portal-marca` (2026-11-10):** el generador de Tarkor y gimg comparten Ollama y GPU y cada uno aborta si el otro corre; antes de generar, `curl localhost:11434/api/ps`, `free -m`, `pgrep -x sd-cli`; nunca `LIBERAR_OLLAMA=1` (descarga el narrador del juego). Avisar al Portal: el encabezado de su `docs/marca.md` (l.3-4) aún dice «pendiente de elegir tipografía».
- **Archivado (2026-11-16):** los detalles de `portal-marca` del 2026-11-10 (ronda FLUX, mapa de Helek, emblema plano, `brand lockup/system`, leves de la hoja de Tarkor y de `gimg/brand.py`) en [handoff-archive.md](records/handoff-archive.md), «portal-marca (2026-11-10)».
- **`check.py` de `gw-media-content` y los perfiles de Reddit (2026-11-05):** una pieza publicada en `u/<persona>` no pasa («Subreddit:» exige `r/<nombre>` y bloque de reglas); que acepte `u/<nombre>` sin reglas. Es del flujo: proponerlo allí.
- **Archivado (2026-11-16):** 3 elemento(s) de versiones ya publicadas (≤ 0.5.0) en [handoff-archive.md](records/handoff-archive.md)
- **Releases en GitHub** (pedido de la persona del 2026-11-05, `docs/plan.md` tras la tabla de fases): v0.1.0, v0.3.0 y v0.4.0 hechas (v0.4.0 a mano: ver `release-install`); las siguientes, con `releases.py bump` y la etiqueta (`release.yml`) (`python3 releases.py check` en cada cierre de fase).
- **Tras r7 (pedido de la persona del 2026-11-04):** (a) y (b) hechas el 2026-11-05 (hojas r8, D39); (c) hecha el 2026-11-11 en `claude/marca-r9` (D38 en la hoja de estilo, los README, `cli.description` y la interfaz; los textos de `examples/galivelop-image-generator` no nombran el producto).
- **Tras aplicar las hojas (2026-11-04), lo que queda:** (a) prompts por rehacer en la próxima ronda: Tarkor `estilo.txt`, `r2-hex/palabras/material` y `r5-*` sin `sun` ni «muted» (`r2-luz.txt` candidato a `estilo.txt`), `r5-cuadrado`/`r5-vertical` con la mitad inferior; developer `og.txt`/`r5-cabecera.txt` con la mitad inferior y «departs from»; (b) piloto: alinear `caja_zona` de `componer.py` y `piezas.json` con la zona de cada hoja (Portal 55 % frente a 1/2; toVeriAI `og` arriba 1/3), subtítulo de voice-generator (67 car.) y volver a medir su og; (c) `icon`, y `compose` con logos para voice-generator y developer (los otros 5, hechos el 2026-11-04); con gimg, `GIMG_CONFIG_HOME=~/.config/gimg GIMG_DATA_HOME=~/.local/share/gimg` desde el sandbox de VS Code; (d) el validador (`gimg doctor --project`) con las comprobaciones 5, 8, 9 y 11 nuevas de la plantilla; (e) propuestas a otros repos (`docs/proposals/`): toVeriAI (og:image, PNG «VeriNews», ShareCard), WMF (`Palette:`), Instalador de Tarkor (icono), Portal (`generar-marca.mjs`, `#2F7A55`); (f) revisar la hoja del Portal cuando su ADR 0002 llegue a `main`; (g) Portal: trazo del logo `#EAF4FA` en los SVG; (h) hecho el 2026-11-10 (`docs/marcas/README.md` y `docs/plan.md` remiten a `tarkor/hoja.md`); (i) hecho el 2026-11-10: el flaky de `test_second_worker_refused_other_process` venía de que `_single_worker` se rendía ante un sondeo `LOCK_SH` de `_no_worker`; ahora espera mientras solo haya sondeos (`_only_probes`, test en `tests/test_service.py` `Races`). `service._single_instance` tiene el mismo patrón sin tocar: va con el `fsutil` común.
- **LoRA de Tarkor (lectura del 2026-11-04, `docs/records/lectura-2026-11-04-tarkor.md`):** propuestas 1-7 **aprobadas por la persona el 2026-11-04** y repartidas en `docs/plan.md` (F2.10: hojas de contactos y aviso de `maxVram` en `doctor`; F2.11: huella de la LUT, sin LoRA; F2.12: `master-1039`; F5: LoRA en el perfil; proceso: revisión por paso y a `main` por bloques). Hojas y aviso se hacen antes de revisar r2.
- **Hoja de estilo mínima por proyecto (pedido de la persona del 2026-11-04, fila F2.12 de `docs/plan.md`):** borrador hecho (`docs/marcas/plantilla-hoja-de-estilo.md`, Fable, revisado): 18 filas obligatorias, lista de 14 comprobaciones (7 sin validar aún) y 11 huecos del perfil (sección 15). Presentado a la persona el 2026-11-04, pendiente de su visto bueno. Caso real hecho: `docs/marcas/galivelop-image-generator/hoja.md` (15 obligatorios del repo, 3 **[P]**), con 17 cambios propuestos a la plantilla al final, pendientes de la persona; falta decidir dónde vive el validador (`gimg doctor --project` o script del piloto) antes de r5. Hechos `gimg sheet` (hoja de contactos con rótulos vía rsvg-convert; el ffmpeg de la Deck no trae `drawtext`) y el aviso `doctor.vram` (umbral 2 GB, el de `steam-deck.json`), 950 tests; las rondas se revisan con `gimg sheet`.
- **Carpeta de datos en flatpak (resuelto en F2.5, `49e6176`):** VS Code en flatpak fija `XDG_DATA_HOME=~/.var/app/…`, y `gimg` desde su terminal usaría otra carpeta de datos que desde una terminal normal (`docs/records/contenido/r0-humo.md`). Decidido: no se ignora el XDG; `gimg doctor` lo avisa y dice que se fije `GIMG_DATA_HOME`/`GIMG_CONFIG_HOME` (mandan sobre XDG). Visto en la Deck el 2026-10-27: el aviso sale y, con las dos variables, instalación y datos van a `~/.local/share/gimg` y `~/.config/gimg`.
- **Referencias de estilo (antes de F5):** ronda del piloto con `sd-cli` y 1-2 imágenes de referencia sobre Tarkor,
  medida con D31; si mejora el % de paleta sin estropear el contraste, entra en F5 (fila «Referencias» de la pestaña
  Marca). Confirmado por la persona el 2026-10-27 (`docs/interfaz/propuesta.md`, decisión nueva 1).
  Expectativa rebajada el 2026-11-02 (Tarkor, IMG-30/31): la referencia conserva un sujeto (útil para mascota o
  producto), no el acabado ni la paleta; lo desaturado de Tarkor se espera arreglar con la LUT de F2.11.
- **Marca de Tarkor:** (en r2, probar antes las pautas de luz del 2026-11-02 de `docs/plan.md`, «Estilos por proyecto») el estilo sale desaturado en todos los formatos (SATAVG 5-7 frente al 15-30 del juego;
  `r5-og-bajo` arregla la luz, YAVG 66, pero no el color): otra vuelta del prompt con la persona
  (`docs/records/contenido/r5-piezas.md`).
- **Generador de Tarkor libre (la persona levantó el aviso el 2026-10-27):** ya se pueden generar imágenes desde este repo.
  Antes de cada tanda, `gimg doctor`: el 2026-10-27 Ollama volvía a cargar `tarkor-narrador-llama31` cada ~20 s (algún
  proceso de Tarkor lo seguía llamando) y la memoria libre bajaba a ~2,5 GB; con eso `gimg` aborta (`engine.ollama: abort`).
  Resuelto ese día cuando la persona confirmó que nadie usaba nada: descarga por la API de Ollama (`POST /api/generate` y
  `/api/embed` con `keep_alive: 0`; el binario `ollama` no se ve desde el flatpak) y la r1 de `gimg` corrió entera sin recargas.
- **URLs del catálogo a verificar [P]** (`gimg/models.json`): deducidas, no copiadas (WMF-imagenes no las apunta); las seis dan 200
  y su `x-linked-etag` coincide con el sha256 de la Deck. Confirmar el repositorio del VAE de FLUX.3
  (`Comfy-Org/flux2-dev`, `split_files/vae/flux2-vae.safetensors`) y el nombre `Qwen3VL-4B-Instruct-Q4_K_M.gguf` (el del
  repo de Qwen; `Qwen3-VL-…` da 404).
- **F2.5 manual, en la Deck (persona), solo cuando el generador de Tarkor esté libre:** `./instalar.sh` de verdad (descarga
  del zip `master-1000-95ff762` de stable-diffusion.cpp y de los modelos de `installDefault` desde Hugging Face: ninguna
  descarga se ha probado, solo con fakes) y `gimg doctor --verify` en verde. Si `instalar.sh` ya encuentra el motor y los
  modelos de WMF-imagenes, `--models-from` evita bajarlos otra vez.
- **Flujo:** `red-without-fix.sh` falla con «cannot stash» si antes se hizo `git add -N` de archivos nuevos (funciona
  sin añadirlos); proponerlo al flujo con el resto (`gw-harvest`).
- **Cuando la persona avise:** revisar las actualizaciones de Tarkor (otro repo) sobre su generador de imágenes: lo lee
  un subagente `Explore` que devuelve un resumen con rutas (`gw-orchestrate-dealer`); desde aquí no se modifica.
- Proponer al flujo (`gw-harvest`) lo de `docs/records/retro-2026-10-25-diseno.md` (R1-R4, R7) y de
  `docs/records/retro-2026-10-25-f0.md` (R1, R3, R4); el hallazgo
  MEDIO de R7 (claves pegadas a una letra en `pre-commit`) conviene arreglarlo antes de publicar la 0.4.0.
- Proponer al flujo (`gw-harvest`) R3a y R3b de `docs/records/retro-2026-10-25-f1.md`.
- Proponer al flujo (`gw-harvest`) una operación de imagen en el `log-format.md` de `gw-opt-ai` (D26).

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `for f in .githooks/pre-commit .githooks/pre-push .githooks/commit-msg; do bash -n "$f"; done` y `python3 -m unittest discover -s tests -t .`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
