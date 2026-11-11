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
| **Tarea en curso · `ccr-85e9d14e-zt7p8b`** | Difusión: piezas en `docs/difusion/2026-11-02/` y `2026-11-05/01-reddit-v040/` (**publicada** el 2026-11-05 en u/Alvaro-Garcia-Grana). Hoja r9 de Galivelop IG **aprobada por la persona el 2026-11-11** (decisiones en «Contradicciones» de `docs/marcas/galivelop-image-generator/hoja.md`; lo anterior, en «Hecho»). Presupuesto de compactaciones: 11. **Siguiente:** nada aquí; r9 se aplica en `claude/marca-r9` (su fila). Sin decidir: los 5 «Cambios que pediría a la plantilla» de la hoja y si se cruza la pieza de Reddit a algún subreddit |
| **Tarea en curso · `claude/marca-r9`** | Abierta el 2026-11-11 desde `ccr-85e9d14e-zt7p8b` (`14ea62d`): hoja r9 aplicada a interfaz, logos y nombre (detalle en «Hecho»). No se tocaron `og.txt`, `brand.palette` ni las piezas `og`/`social`; `origin/claude/marca-ui` (`dd6cc7e`) no se fusiona aquí. Presupuesto de compactaciones: 3 (van 5: no se abre nada más aquí). **Leves (sin revisar más):** `gimg/ui/mock/api-mock.js` nombra «Sora» en datos simulados; los `<title>` de los símbolos dicen «galivelop-image-generator: rejilla de intentos»; el nombre del lockup va en `<text>` vivo; monograma «GVIG» sin dibujar. **Siguiente:** ir a `main` con las tres fases y pull request, solo con confirmación de la persona. Después, en otra tarea: medir una ronda plana y `og`/`social` con el lockup nuevo (entonces se quitan la copia congelada y `REDRAWN_COPY_SHA256`) |

Aquí `logRows` está apagado en `.claude/gw.json`: las filas se editan a mano (`handoff.py set-row` no escribe) y no
hace falta `GW_SHARED_LOG`. Aun así, cada rama toca solo su fila salvo al cerrar o fusionar otra.

## Para la próxima publicación

—

## Hecho (5 últimas)

1. 2026-11-11 — claude/marca-r9 (2026-11-11): hoja r9 aplicada. (c) D38 en README.md, README.en.md y cli.description (1ca2bb6, fusionado en e4b5db0); (a) tokens r9 y fuentes de la interfaz (89e3e35, 4dd9a23, fusionado en de53727); (b) redibujo de baldosa, línea, favicon y lockup (47c4695, fusionado en 1b211f6; og/social siguen con la copia congelada del lockup anterior en examples/galivelop-image-generator/logos/); hoja sin [P] en lo aplicado y D38 anotada en docs/plan.md (c6e1534).
2. 2026-11-11 — `ccr-85e9d14e-zt7p8b` (2026-11-10/11): fusionada `main` (v0.4.1), paleta de Tarkor remitida a su hoja, `docs/en/api.md`, tests inestables arreglados (pid atómicos en `tests/fake_sd_cli.py`; `_single_worker` no se rinde ante un sondeo `LOCK_SH`), ResourceWarning de `tests/browser.py`; hoja de estilo r9 de Galivelop IG (variante de la identidad del Portal, `portal-marca` `08c7fe5`), aprobada por la persona el 2026-11-11.
3. 2026-11-06 — `fix-0.4.1`: *cherry-pick* de `ca6cea2` y `ec89eb0` (sondeos de `worker.lock`/`serve.lock` con cerrojo compartido, `_live()` con el pid de `serve.json`) y `398a7af` (huella `build` para que `arrancar.sh` reemplace el servicio viejo); CHANGELOG es/en; `releases.py bump 0.4.1`; README es/en con la versión y la hoja de ruta por versiones. Fase 1: `_no_worker` con cerrojo compartido, reintento de `_single_instance`, huella por contenido y espera en `_live`.
4. 2026-10-25 — F1 (`f1-nucleo`) a `main` por push directo con confirmación de la persona: CI no comprobado (sin `gh` en esta máquina; en F0, sin cuota), **comprobado solo en local** (check del `pre-push` sobre `0d02f51`). Tres fases hechas, marca en `fe7d968`.
5. 2026-10-25 — F0 (`f0-esqueleto`) a `main` por push directo con confirmación de la persona: CI sin cuota (pagos fallidos), **comprobado solo en local** (check del `pre-push` sobre el mismo commit). Tres fases hechas, marca en `17e28eb`.

## Pendiente

- **`check.py` de `gw-media-content` y los perfiles de Reddit (2026-11-05):** una pieza publicada en `u/<persona>` no pasa («Subreddit:» exige `r/<nombre>` y bloque de reglas); que acepte `u/<nombre>` sin reglas. Es del flujo: proponerlo allí.
- **Leves de ramas ya fusionadas:** en `docs/records/leves-fusionadas.md` (hasta `release-install`) y, desde `fix-0.4.1`, en `docs/records/leves-<rama>.md`; se miran solo si una tarea toca lo mismo.
- **Leves de la fase 1 de `fix-0.4.1` (2026-11-06, no se revisan más en este PR):** el sustituto `fresh` que deja otro CLI en `ensure_running` no se compara con la versión y la huella propias (dos copias con código distinto se quedan con la del primero, sin aviso); los sondeos `worker_alive`/`lock_held`/`_no_worker` y los reintentos de `_single_worker`/`_single_instance` están copiados (un `fsutil` común); `server.BUILD` se calcula al importar `gimg.server`.
- **Releases en GitHub** (pedido de la persona del 2026-11-05, `docs/plan.md` tras la tabla de fases): v0.1.0, v0.3.0 y v0.4.0 hechas (v0.4.0 a mano: ver `release-install`); las siguientes, con `releases.py bump` y la etiqueta (`release.yml`) (`python3 releases.py check` en cada cierre de fase).
- **Tras r7 (pedido de la persona del 2026-11-04):** (a) y (b) hechas el 2026-11-05 (hojas r8, D39); (c) hecha el 2026-11-11 en `claude/marca-r9` (D38 en la hoja de estilo, los README, `cli.description` y la interfaz; los textos de `examples/galivelop-image-generator` no nombran el producto).
- **Tras aplicar las hojas (2026-11-04), lo que queda:** (a) prompts por rehacer en la próxima ronda: Tarkor `estilo.txt`, `r2-hex/palabras/material` y `r5-*` sin `sun` ni «muted» (`r2-luz.txt` candidato a `estilo.txt`), `r5-cuadrado`/`r5-vertical` con la mitad inferior; developer `og.txt`/`r5-cabecera.txt` con la mitad inferior y «departs from»; (b) piloto: alinear `caja_zona` de `componer.py` y `piezas.json` con la zona de cada hoja (Portal 55 % frente a 1/2; toVeriAI `og` arriba 1/3), subtítulo de voice-generator (67 car.) y volver a medir su og; (c) `icon`, y `compose` con logos para voice-generator y developer (los otros 5, hechos el 2026-11-04); con gimg, `GIMG_CONFIG_HOME=~/.config/gimg GIMG_DATA_HOME=~/.local/share/gimg` desde el sandbox de VS Code; (d) el validador (`gimg doctor --project`) con las comprobaciones 5, 8, 9 y 11 nuevas de la plantilla; (e) propuestas a otros repos (`docs/propuestas/`): toVeriAI (og:image, PNG «VeriNews», ShareCard), WMF (`Palette:`), Instalador de Tarkor (icono), Portal (`generar-marca.mjs`, `#2F7A55`); (f) revisar la hoja del Portal cuando su ADR 0002 llegue a `main`; (g) Portal: trazo del logo `#EAF4FA` en los SVG; (h) hecho el 2026-11-10 (`docs/marcas/README.md` y `docs/plan.md` remiten a `tarkor/hoja.md`); (i) hecho el 2026-11-10: el flaky de `test_second_worker_refused_other_process` venía de que `_single_worker` se rendía ante un sondeo `LOCK_SH` de `_no_worker`; ahora espera mientras solo haya sondeos (`_only_probes`, test en `tests/test_service.py` `Races`). `service._single_instance` tiene el mismo patrón sin tocar: va con el `fsutil` común.
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
