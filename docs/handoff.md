<!-- galivelop-workflow v0.5.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `portal-marca` (desde `origin/main` `fa1076e`); el trabajo de F4e sigue en `f4e-piezas` |
| **Fase / tarea** | marca del Portal y de Tarkor (hoja nueva, `gimg brand`) |
| **Último punto estable** | `main` en `c5827e2` (PR #22, barrido de `brand.py` y retro, 2026-11-16, CI en verde); release v0.6.0 publicada (etiqueta en `98fcc7c`, PR #20, 2026-11-16) |
| **Siguiente paso** | el de la fila de `ccr-85e9d14e-zt7p8b` |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |
| **Tarea en curso · `fix-0.4.1`** | Fusionada en `main` por el PR #5 (`fa1076e`, 2026-11-06, CI en verde); etiqueta y release v0.4.1 publicadas; rama terminada. |
| **Tarea en curso · `ccr-85e9d14e-zt7p8b`** | Tanda L8 y barrido P2 de `brand.py` hechos (2026-11-16); **ir a `main` (la persona, 2026-11-17)**: fase 1 sobre `72478e3` (0 graves/medios, 4 leves en `docs/records/leves-ccr-85e9d14e-zt7p8b.md`), fase 2 hecha (retro `retro-2026-11-17-tanda-l8.md` aprobada entera). Presupuesto de compactaciones: 0. Queda: asas táctiles de 44 px en un dispositivo (la persona). Siguiente: fase 3 (`reviewed.sh`, PR con la skill `pr`, CI en verde, fusionar con confirmación). **En la próxima sesión en local, avisar a la persona**: reanudar la cola de `hojas-repos`. |
| **Tarea en curso · `claude/marca-r9`** | Fusionada en `main` por el PR #6 (`2509674`, 2026-11-11): hoja r9 aplicada a interfaz, logos y nombre (detalle en «Hecho»); rama terminada. Queda, en otra tarea: medir una ronda plana y `og`/`social` con el lockup nuevo (entonces se quitan la copia congelada y `REDRAWN_COPY_SHA256`) |
| **Tarea en curso · `portal-marca`** | Fusionada en `hojas-repos`; sus imágenes del Portal están completas en `piloto/portal-marca/portal-web-final/portal/` (LEEME; raíz = aprobado, `svg/`, `aprobadas/`, `pendiente/`, `descartes/`). Historia de rondas, intentos aprobados y reglas en «Hecho». Falta: la sesión del Portal aplica `docs/proposals/portal/entrega-marca-2026-11-12.md`. Siguiente: nada aquí; seguir por la fila de `hojas-repos`. |
| **Tarea en curso · `hojas-repos`** | Historia en «Hecho». 31f: composición FLUX q1425-1428 encolada; img2img (Z-Image, fuerza 0,5/0,6) en `docs/records/troubleshooting-hojas-repos.md`. Pendiente: ux41-14 q1370 en `piloto/tarkor-final/pendiente/`. **Cola en pausa por la persona (17-11)**: 105 en espera (~6 h); reanudar solo con el servicio del equipo vivo. **Pedido del Portal de la tarde** (`docs/proposals/portal/pedido-tarkor-2026-11-17.md`): punto 1, SVG del icono, hecho (receta en el LEEME de `tarkor/`). Siguiente: encolar 24c (composición FLUX + grabado Z-Image, 3-4 intentos); al reanudar (servicio del equipo), q1425-1428 y 24c a `top`, juzgar 31f y luego el img2img. |

Aquí `logRows` está apagado en `.claude/gw.json`: las filas se editan a mano (`handoff.py set-row` no escribe) y no
hace falta `GW_SHARED_LOG`. Aun así, cada rama toca solo su fila salvo al cerrar o fusionar otra.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-11-17 — hojas-repos, 17-11 tarde: fase 1 del bloque 6398948..d877030 (Findings: 6, leves en docs/records/leves-ccr-85e9d14e-zt7p8b.md); pedido del Portal #1412-1424 juzgado; icono de Tarkor q1417 elegido por la persona (SVG, anillo a aprobadas/); ux41-13 misiones q1367 sustituye a q1034; merge de origin/main (PR #23) en 6db1f4a.
2. 2026-11-17 — 2026-11-16/17 · `ccr-85e9d14e-zt7p8b`: tanda L8 (orders, cli crop, export._resample, aviso del taller), barrido P2 de `brand.py`, `GIMG_AUTOSTART=0` en `tests/test_cli.py`; fase 1 (4 leves) y retro `retro-2026-11-17-tanda-l8.md`.
3. 2026-11-17 — 17-11 (hojas-repos): cola #1137-1246 juzgada; /gw-opt-ai P1-P4 aprobadas, iconos del Portal a 512²; 48 entradas quemadas por un servicio sin GPU, reencoladas; banco P4 en frío sin regresión (58,1 s/paso); pedido del Portal #1412-1424 encolado delante.
4. 2026-11-17 — hojas-repos, 17-11: cola #1137-1246 juzgada: Tarkor 10 aprobadas en `piloto/tarkor-final/`, Portal/GVE 21 en `piloto/portal-marca/portal-web-final/` (carpeta nueva `galivelop-evaluator/`); 9 pedidos rehechos (ux41 07/08/12, instalador i3/i4, og-developer, 23b-gve-b, 25b, 25e) y encolados; lecciones en `docs/records/troubleshooting-hojas-repos.md`.
5. 2026-11-16 — **FM 0.6.0 Recortar (2026-11-16, `ccr-85e9d14e-zt7p8b`):** `gimg/crop.py` + `POST …/attempts/{id}/crop` (intento derivado con `derivedFrom`; errores `crop.bad_box|outside|ratio_mismatch|bad_target|write_failed|compose_unsupported`); revisión del backend (`2b1a08e`, Findings: 4: destino que compone rechazado, alta atómica del destino, `tileable` fuera). Interfaz: `box-drag.js` extraído de `layout-editor.js`, `crop-editor.js`, «Recortar» y distintivo en `attempt-card.js`; revisión (`34a00b1`, Findings: 7). Flujo a Galivelop-workflow v0.7.0 (confirmado por la persona).

## Pendiente

- **Barrido de color/pintura de `gimg/brand.py` (0.7.0; retro del 2026-11-17, P3, aprobada):** cerrar los leves de `brand.py` del archivo de leves: `_mute` (`op0 or w0`), `fill` explícito en `<line>`, `rgb` con separadores mezclados, exponentes, `hsl(none …)`, `fill-opacity`/`opacity`, `turn`/`rad`; la persona elige cuáles.
- **`tests-for.py --run` sin `tests/__init__.py` (2026-11-16):** `test-run.py` descubre con `top_level_dir=tests`, así que no se importa `tests/__init__.py` y `GIMG_AUTOSTART=0` no se fija: `ComposeCliTests` y `FullCycleTests` fallan con el aviso `service_failed` y dejan un `gimg serve` vivo. El check completo pasa. Parcheado en `tests/test_cli.py` (fija `GIMG_AUTOSTART=0` al importarse); el arreglo general, en el flujo (`.claude/gw/scripts/`, necesita permiso) o con un `testMap.command` del proyecto que use `-t .`.
- **Barrido de `gimg/brand.py` (0.7.0; retro del 2026-11-16 «barrido-brand», P2): hecho (2026-11-16)**, revisado en la sesión y en la fase 1 del 2026-11-17 (un leve nuevo, en el archivo de leves): quitado `_mute_attrs` del `flat`, unidos los dos bucles de `_paint_colors`, `_mute_attrs` llama a `_no_paint` y `_mute` lleva `stroke-opacity` 0 y `stroke-width` 0 por separado. El punto 4 cambia comportamiento: una opacidad de trazo 0 heredada ya no la deshace un ancho propio. El barrido anterior (P5) y `orders.add_derived` (2), hechos.
- **Al flujo (retro del 2026-11-16, P1, P2, P4, aprobadas):** comprobar filas de la tabla de estado; registro de tokens
  en un archivo ignorado volcado en el `pre-commit`; dos líneas en el encargo de `gw-orchestrate-dealer`. Detalle en
  `docs/records/retro-2026-11-16-barrido-b.md`, «For Galivelop-workflow».
- **Barrido B de `crop-editor.js` (retro del 2026-11-16, P3):** hecho en `4c297c1` (2026-11-16): vista previa por `requestAnimationFrame`, error solo en el diálogo, «Repetir» desactivado si el perfil compone, `trapDialog` en `dialog-trap.js` para los dos editores, `boxFor` desde `toBox`. Fase 1 hecha (`6398948`, `Findings: 5`).
- **Leves de la fase 1 de la sexta tanda (2026-11-15):** `tile`: la copia que no se pudo borrar, en ejecuciones siguientes, `recover_backups` la da por «puede ser el original», contradiciendo el aviso anterior (el estado no queda en el nombre); `brand`: un `fill` explícito en un `<line>` sigue contando como color (aplanado de más); `trace`: `min_island` sigue en píxeles reducidos, así que con reducción una forma pequeña de un color se pierde aunque el trazo no salga vacío (dividir siempre por factor² deja de quitar motas: descartado).
- **Leves de las tandas 1-5 de `ccr-85e9d14e-zt7p8b` (2026-11-13/14):** los abiertos, en `docs/records/leves-ccr-85e9d14e-zt7p8b.md` («Tandas 1-5»); la próxima tanda los elige de ahí.
- **Ramas viejas sin fusionar `main` (2026-11-15):** `f4e-piezas` (contiene `claude/ui5-retoque` y `claude/f4e2c-texto`) y `fix-editor-escala-y` (contiene `claude/ui9-talla-mando`) llevan 40-75 commits propios sin equivalente en `main` y chocan en 16-19 archivos de la interfaz y el editor por los dos lados: no se fusionaron, decide la persona. `piloto-imagenes` y `release-install` (1 commit cada una, ya superadas) chocan en un archivo; `claude/gimg-overlay` ya está en `hojas-repos`.
- **gw-opt-ai del 14-11 (aprobadas, sin aplicar):** P1 perfil `icono` del Portal a 768² con prueba previa, y P2 tope de portadas 1344×768 (p95 ≤ 630 s); detalle en `.claude/gw/gw-opt-ai.md` («Ya en marcha»). Aplicar cuando la persona lo diga, no a mitad de la cola actual.
- **Huecos de `gimg` vistos en `hojas-repos` (2026-11-12):** todos hechos en `ccr-85e9d14e-zt7p8b` (`system --mono` y `--margin`, espaciado 0,01; perfiles nuevos; `gimg export` a WebP, ICO y BMP con `--crop`/`--anchor`; `measure --family`; `brand square`) salvo Big Shoulders Display sin `.ttf` en el equipo (depende del equipo de la persona). Aviso: `red-without-fix.sh` usa el stash compartido y, con varios worktrees a la vez, uno puede recoger el stash de otro (pasó el 2026-11-13, otra vez con dos subagentes: cada uno recogió el stash del otro; recuperado, nada perdido). Proponer al flujo que use `git worktree`/copia temporal en vez de `git stash`, o `--fix-at HEAD` por omisión.
- **`examples/` de developer y workflow** siguen con la identidad anterior (paleta, perfiles FLUX; `tests/test_examples.py` l.312 fija el lockup `b` de workflow); r10 de image-generator rompería `tests/test_ui.py` l.564-597 y `tests/test_brand_assets.py` l.58 al aplicarse.

- **Hueco de `gimg brand trace` (2026-11-17, `hojas-repos`):** en un icono de trazo curvo, `--dp-tol 0.5` deja escalones de 1 px y la CLI no deja subir `max_side` (512): el SVG de 23c salió subiendo el PNG a 2048² con un script aparte y llamando a `brand.trace` con `max_side=2048`, `dp_tol=3`. Falta en la CLI una opción de subida (`--upscale N`) o `--max-side`, y otra de engrosar (`--grow`).
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
