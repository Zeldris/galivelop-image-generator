<!-- galivelop-workflow v0.5.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `fix-0.4.1` (desde `origin/main` `71a69a3`): parche 0.4.1; el trabajo de F4e sigue en `f4e-piezas` |
| **Fase / tarea** | 0.4.1: arreglos de lo publicado en 0.4.0, antes que la 0.5.0 (decisión de la persona del 2026-11-06: los arreglos van primero) |
| **Último punto estable** | `main` en `71a69a3` (PR #4, CI en verde), etiqueta y release v0.4.0 |
| **Siguiente paso** | el de la fila de `fix-0.4.1` |
| **Check** | `bash -n` de los ganchos + `python3 -m unittest discover -s tests -t .` |
| **Tarea en curso · `f2-motor`** | Fusionada en `main` por el PR #2 (`624f7a9`, 2026-11-05, CI en verde); rama terminada. |
| **Tarea en curso · `plan-piezas`** | Fusionada en `main` por el PR #3 (`d128106`, 2026-11-05, CI en verde); rama terminada. v0.4.0 etiquetada en `d128106`; `release.yml` falló (sin `ffmpeg`/`rsvg-convert`) y la release se creó a mano con `releases.py notes` y el mismo título (mismo árbol que el CI verde del PR); `releases.py check` en verde. |
| **Tarea en curso · `release-install`** | Fusionada en `main` por el PR #4 (`71a69a3`, 2026-11-05, CI en verde, confirmado por la persona); rama terminada. |
| **Tarea en curso · `fix-0.4.1`** | Abierta el 2026-11-06. Hecho: arreglos y bump 0.4.1 (ver «Hecho»), fase 1 (arreglos con pruebas en rojo sin su arreglo; leves en «Pendiente»), fase 2: retro `docs/records/retro-2026-11-06-fix-0.4.1.md` aprobada entera (P1 `tests/test_locks.py`, P2 `releases.py bump` pone la versión de los README, P4 leves a `docs/records/leves-fusionadas.md`, P5 esta celda). Falta: fase 3, PR a `main` (con confirmación), etiqueta `v0.4.1` y release, `releases.py check`; luego `git merge origin/main` en `f4e-piezas`. |
| **Tarea en curso · `portal-marca`** | Abierta el 2026-11-10 (desde `origin/main` `fa1076e`). Hoja nueva del Portal y de Tarkor; hecho en «Hecho» y «Pendiente». Los SVG del logo **no se dibujan a mano** (D37; la persona paró a Fable el 2026-11-10): los genera gimg. Hecho: `matte.py`, `trace.py`, `png.read_rgba`/`rgba_bytes` y `gimg/brand.py` con `gimg brand matte|trace|wordmark|lockup|system` (tests en `tests/test_brand.py`; `system` sobre el emblema Z-Image q175 de Tarkor: ~10 s, 16 trazados; la interfaz falta). Siguiente: el paso de marca en la interfaz (`docs/plan.md`, «Proceso de marca en la interfaz»), corregir `hoja.md` §4 y generar el sistema de logo de Tarkor; luego `og.compose` y `piezas.json`. Falta: 6-9, el resto y la entrega al Portal. Compactaciones: por encima del presupuesto (2): repartir a subagentes. |

Aquí `logRows` está apagado en `.claude/gw.json`: las filas se editan a mano (`handoff.py set-row` no escribe) y no
hace falta `GW_SHARED_LOG`. Aun así, cada rama toca solo su fila salvo al cerrar o fusionar otra.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-11-10 — **`portal-marca` (2026-11-10):** `examples/portal`; bocetos FLUX y Z-Image-Turbo (ver «Pendiente»); propuesta de Fable (`docs/marcas/tarkor/propuesta-fable-2026-11-10.md`, §9 aprobado por la persona); hoja única de Tarkor (`biblia`, `peticiones`, `hoja`; r7 archivada); `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md` para el repo del juego (la persona se lo pasa); `examples/tarkor` en la dirección nueva (`og.compose` y `piezas.json` esperan los SVG).
2. 2026-11-10 — `portal-marca` (2026-11-10, Fable): `examples/tarkor` en la dirección nueva: `brand.palette` con los 16 hex (fuera arcilla, `#8a3b1e`, `#a3814f`), `draft` en los 18 perfiles, los once perfiles del bloque E, `orders/ui/01-emblema.json` con el bloque común y el prompt nuevo (10 semillas, borrador) y diez pedidos E (`orders/marca/e02-e04`, `orders/ui/e06-e12`, 3 semillas). `og.compose` y `piezas.json` esperan los SVG nuevos. `gimg/models.json`: `sizeMb` de Z-Image y su `ae` estaban en MiB (5019, 320); pasan a MB (5263, 335), sha256 comprobados en la Deck.
3. 2026-11-06 — `fix-0.4.1`: *cherry-pick* de `ca6cea2` y `ec89eb0` (sondeos de `worker.lock`/`serve.lock` con cerrojo compartido, `_live()` con el pid de `serve.json`) y `398a7af` (huella `build` para que `arrancar.sh` reemplace el servicio viejo); CHANGELOG es/en; `releases.py bump 0.4.1`; README es/en con la versión y la hoja de ruta por versiones. Fase 1: `_no_worker` con cerrojo compartido, reintento de `_single_instance`, huella por contenido y espera en `_live`.
4. 2026-10-25 — F1 (`f1-nucleo`) a `main` por push directo con confirmación de la persona: CI no comprobado (sin `gh` en esta máquina; en F0, sin cuota), **comprobado solo en local** (check del `pre-push` sobre `0d02f51`). Tres fases hechas, marca en `fe7d968`.
5. 2026-10-25 — F0 (`f0-esqueleto`) a `main` por push directo con confirmación de la persona: CI sin cuota (pagos fallidos), **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `17e28eb`.

## Pendiente

- **`portal-marca` (2026-11-10):** el generador de Tarkor y gimg comparten Ollama y GPU y cada uno aborta si el otro corre; antes de generar, `curl localhost:11434/api/ps`, `free -m`, `pgrep -x sd-cli`; nunca `LIBERAR_OLLAMA=1` (descarga el narrador del juego). Avisar al Portal: el encabezado de su `docs/marca.md` (l.3-4) aún dice «pendiente de elegir tipografía».
- **`portal-marca`, ronda FLUX (2026-11-10, hojas en `piloto/portal-marca/flux-*.png` y `piloto/tarkor/flux-01-emblema.png`):** mejores, por delegación: #1 q133, #4 q142, #5 q146 (bocetos para el SVG), #1b ninguno (salió en positivo), emblema de Tarkor q154 (luego q150, q153; el brillo tapa la piedra). Elegidos con `gimg choose` (intentos 2, 3, 3 y 7) y copiados a `piloto/portal-marca/{portal,tarkor}/intentos/` (página regenerada). **Prueba Z-Image (`ui/01-emblema` de Tarkor, 10 semillas, 2026-11-10):** FLUX en borrador (512, 4 pasos; q164-173, intentos 9-18): 1,08 min por imagen (65 s de media). Z-Image-Turbo q6, 8 pasos, 1024, `--no-draft` (proyecto `tarkor-zi`, copia en el scratchpad; q174-183, intentos 1-10): 10,07 min por imagen (no comparable: FLUX en borrador; un FLUX definitivo, q184, tardó 3,97 min). Hojas en `piloto/tarkor/`: `flux2-01-emblema.png`, `zi-01-emblema.png`, `comparativa-01-emblema.png` (Z-Image / FLUX / los dos PNG de `examples/tarkor/logos/`). **Elegido por el agente (delegado), según `hoja.md` §4 (aro, piedra y oro):** Z-Image q175 (intento 2, `gimg choose` hecho; suplentes q176 y q183; copiado a `piloto/tarkor/intentos/01-emblema-zi-q175.png`); FLUX q170 (intento 15, borrador; suplentes q169 y q173; copiado a `piloto/tarkor/intentos/01-emblema-flux-q170.png`). `gimg choose` no admite borradores («el intento 15 es un borrador y no se puede elegir») y la misma semilla 7 a 1024 (q184) sale otra imagen (ocho puntas, aro de madera): el de FLUX queda solo como candidato, sin elegir. **Juicio:** Z-Image da el aro de oro tallado con cuatro puntas, el campo de cristal facetado y la piedra agrietada con juntas de luz, pero las juntas salen en X (cuatro gajos) o cinco, no seis; el campo verde es mate y cae bien para recortar. FLUX borrador acierta los seis gajos y la estrella central, pero el aro sale de madera con bronce, no de oro tallado, y el campo de cristal es liso; para el SVG sirve mejor Z-Image como boceto del aro y el cristal, y el q170 de FLUX para el reparto de gajos y estrella.
- **`portal-marca`, pedido del mapa de Helek (2026-11-10, WMF `MAP-19`, copia en `docs/marcas/tarkor/pedido-mapa.md`, WMF `7c5e2d13`):** 48 piezas con el estilo de la hoja de Tarkor: prueba de estilo #1-3 (arena roja, hielo, icono de montaña) y, con el sí de Álvaro (nota 1-10, se juzga dentro del mapa), M-A texturas de bioma sin costura (#4-15), M-B iconos de relieve y vegetación (#16-25), M-C fichas de lugar (#26 base, el resto img2img a 0,35-0,45), M-D rosa, cartela, escala, marco y costas (#39-44), M-E capas de juego (#45-48). Entrega en `examples/tarkor/entrega/mapa/` (`m01-arena-roja.png`, recortes `-alpha.png` sobre `#00ff00` o `#ff00ff`) con una hoja de contactos por bloque. Va tras el sistema de logo; antes, en gimg: `docs/plan.md` punto 8 (sin costura, fondo magenta, perfiles `cartela` y `banda`). Avisar a WMF: #41-42 usan `banda` 1024×256 sin declararlo. GPU compartida con el juego.
- **`portal-marca`, `gimg brand lockup/system` (2026-11-10):** revisión hecha y arreglada. La hoja §4 no fija el hueco del lockup vertical ni el margen (0,25 y 0, `--gap`/`--margin`); falta el separador #9 y el margen libre = altura de la T. Leves sin hacer: `lockup -o` por defecto pisa en el cwd sin `--force` (`system` sí lo tiene); sin test de fallo a mitad de la copia ni de `--force` sobre un symlink; `PATH=""` de `test_missing_tool_writes_nothing` solo probado en Linux (pendiente de máquina).
- **`portal-marca`, hoja de Tarkor (2026-11-10, leves):** Commits de WMF citados distintos entre documentos (`3537d84`, `e3778e61`; HEAD `e5a41d18`, sin cambios en lo citado); el bloque común acaba en «no haze» (negación aprobada); Portal sigue con arcilla en `tarkor.json` y «pendiente de elegir tipografía» (avisar al Portal); los SVG del sistema de logo nuevo están «previstos», no hechos.
- **`portal-marca`, `gimg/brand.py` (2026-11-10, leves de la revisión de 238711d):** (5) el peso de una fuente variable no está probado en macOS ni Windows, y (6) la ruta temporal de fontconfig tampoco: pendiente, lo prueba la persona en cada sistema; (9) quedan sin test los errores de `matte` con un PNG ilegible y el CLI sin `--font`; (10) al cablear la ruta HTTP, pasar `brand.*` de 500 a 400 en `server.status_for` y en `INTENDED_500` de `tests/test_server.py`.
- **Leves de ramas ya fusionadas:** en `docs/records/leves-fusionadas.md` (hasta `release-install`) y, desde `fix-0.4.1`, en `docs/records/leves-<rama>.md`; se miran solo si una tarea toca lo mismo.
- **Leves de la fase 1 de `fix-0.4.1` (2026-11-06, no se revisan más en este PR):** el sustituto `fresh` que deja otro CLI en `ensure_running` no se compara con la versión y la huella propias (dos copias con código distinto se quedan con la del primero, sin aviso); los sondeos `worker_alive`/`lock_held`/`_no_worker` y los reintentos de `_single_worker`/`_single_instance` están copiados (un `fsutil` común); `server.BUILD` se calcula al importar `gimg.server`.
- **Releases en GitHub** (pedido de la persona del 2026-11-05, `docs/plan.md` tras la tabla de fases): v0.1.0, v0.3.0 y v0.4.0 hechas (v0.4.0 a mano: ver `release-install`); las siguientes, con `releases.py bump` y la etiqueta (`release.yml`) (`python3 releases.py check` en cada cierre de fase).
- **Test inestable en el CI:** `tests.test_engine_sdcpp.RunTests.test_cancel_kills_the_whole_group` falló en `1eae6d7` y `44f8987` y pasó en la subida siguiente; diagnosticarlo con `diagnosing-bugs` tras el PR de F4 (retro del 2026-11-05).
- `docs/en/api.md` (D16 pide docs en es y en).
- **Tras r7 (pedido de la persona del 2026-11-04):** (a) y (b) hechas el 2026-11-05 (hojas r8, D39); (c) aplicar D38 («Galivelop IG», siglas «GVIG») a la hoja de estilo, el README, los textos de `examples/galivelop-image-generator` y la interfaz.
- **Tras aplicar las hojas (2026-11-04), lo que queda:** (a) prompts por rehacer en la próxima ronda: Tarkor `estilo.txt`, `r2-hex/palabras/material` y `r5-*` sin `sun` ni «muted» (`r2-luz.txt` candidato a `estilo.txt`), `r5-cuadrado`/`r5-vertical` con la mitad inferior; developer `og.txt`/`r5-cabecera.txt` con la mitad inferior y «departs from»; (b) piloto: alinear `caja_zona` de `componer.py` y `piezas.json` con la zona de cada hoja (Portal 55 % frente a 1/2; toVeriAI `og` arriba 1/3), subtítulo de voice-generator (67 car.) y volver a medir su og; (c) `icon`, y `compose` con logos para voice-generator y developer (los otros 5, hechos el 2026-11-04); con gimg, `GIMG_CONFIG_HOME=~/.config/gimg GIMG_DATA_HOME=~/.local/share/gimg` desde el sandbox de VS Code; (d) el validador (`gimg doctor --project`) con las comprobaciones 5, 8, 9 y 11 nuevas de la plantilla; (e) propuestas a otros repos (`docs/propuestas/`): toVeriAI (og:image, PNG «VeriNews», ShareCard), WMF (`Palette:`), Instalador de Tarkor (icono), Portal (`generar-marca.mjs`, `#2F7A55`); (f) revisar la hoja del Portal cuando su ADR 0002 llegue a `main`; (g) Portal: trazo del logo `#EAF4FA` en los SVG; (h) `docs/marcas/README.md` l.16 y l.33 y `docs/plan.md` l.653-655 (paleta de Tarkor) a remitir a la hoja; (i) flaky visto una vez: `tests/test_worker.py` `test_second_worker_refused_other_process`.
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
- El flujo copiado es la 0.4.0 **sin publicar** (rama `ccr-6dfbc880-ddr41g` del flujo, commit `d227bbf`; su `main` está en
  0.3.0): `/gw-update` cuando la 0.4.0 salga publicada.
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
