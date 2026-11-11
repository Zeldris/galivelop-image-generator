<!-- galivelop-workflow v0.5.0 -->
# gw-opt-ai — notas del proyecto

Las lee primero la skill `gw-opt-ai`; aquí vive todo lo propio de los modelos de IA local de este proyecto. El flujo
las crea una vez; desde entonces son del proyecto.

## Motores y modelos

- Un solo motor: **stable-diffusion.cpp** (`sd-cli`, backend Vulkan), lanzado por `gimg/engine.py`. No hay
  texto ni RAG: cada llamada es `gen_ai.operation.name = image_generation` (operación propia de gimg, D26; el
  `log-format.md` del flujo aún no la lista).
- Los nombres de modelo (`flux2-klein-4b-q8`, `zimage-turbo-q6`, `qwen-image-…`) y sus archivos viven en el
  catálogo de gimg (`gimg models`) y en los perfiles de cada proyecto (`examples/<proyecto>/galivelop-images.json`);
  no se copian aquí.
- Reparto acordado con la persona: FLUX solo bocetos; Z-Image-Turbo q6 a 8 pasos para calidad; Qwen-Image solo
  fotorrealismo o detalle muy concreto.
- **Comparte GPU con Ollama** (el narrador de Tarkor): el perfil de máquina lleva `ollama: abort` y nunca se usa
  `LIBERAR_OLLAMA=1`.

## Tareas

- `app.task` es el **perfil de imagen** del pedido (`og`, `cuadrado`, `portada`, `icono`, `texturamapa`…); el
  modelo va en `gen_ai.request.model`, el borrador en `app.image.draft`.
- No hay llamadas de calentamiento. Las filas sin modelo (`og/-`, `unknown/og/-`) son del motor falso de los
  tests y de rondas antiguas sin perfil: se excluyen al medir (`--exclude-task` no basta; filtrar por
  `gen_ai.request.model` presente al montar el registro de la ronda).
- Tiempos útiles además de `app.duration_ms`: `app.load_ms`, `app.image.sample_ms`, `app.image.decode_ms`,
  `app.image.min_free_mb`, y `app.image.width/height/steps` para comparar a igual tamaño.

## Perfiles de máquina

- `steam-deck-libre` (**el mínimo** y el de uso real): Steam Deck, Vulkan, `maxVram vulkan0=7`, 7000 MB libres
  mínimos, 1 Mpx máximo. Archivo: `~/.config/gimg/steam-deck-libre.json`.
- `steam-deck`: el preset por defecto de gimg (rondas r1-r8 del 2026-11-04 al 10).
- Se fija con `machineProfile` en `~/.config/gimg/config.json` o `GIMG_MACHINE_PROFILE`. El registro está siempre
  activo: gimg escribe una línea por generación en `~/.local/share/gimg/projects/<proyecto>/log.jsonl`.

## Ajustes

Los lee `scripts/measure.py` de la skill; las rutas relativas se resuelven desde la raíz del repo. El registro de
la ronda se monta antes de medir (queda en `piloto/`, fuera de git, porque lleva los prompts):

```sh
mkdir -p piloto/opt-ai
cat ~/.local/share/gimg/projects/*/log.jsonl \
  | python3 -c "import json,sys; [print(l, end='') for l in sys.stdin if json.loads(l).get('gen_ai.request.model')]" \
  > piloto/opt-ai/ronda-$(date +%F).jsonl
```

```gw-opt-ai
log: piloto/opt-ai/ronda-2026-11-11.jsonl
previous: piloto/opt-ai/base-2026-11-11.jsonl
exclude_tasks: warmup
cold_ms: 100
```

`cold_ms: 100` marca como frío el 100 % de las llamadas: `sd-cli` carga el modelo en cada imagen (no hay servidor
residente). Es el comportamiento esperado, no un hallazgo, mientras gimg no tenga motor residente.

## Banco de pruebas

Lanzado el 2026-11-11 (P2), con la GPU libre: un pedido fijo, `examples/portal/orders/marca/14-icono-implantacion.json`
(claves `opt-ai/14-*` del proyecto `portal`), semillas 1-3, a 1024×1024 en **`steam-deck-libre`**: FLUX definitivo, FLUX
borrador y Z-Image. Registro en `piloto/opt-ai/base-2026-11-11.jsonl` (es el `previous`), hoja en
`piloto/opt-ai/base-2026-11-11.png`. Para repetirlo: `order submit --model <id> [--draft|--no-draft]` con una copia
del pedido (`key` `opt-ai/…`, `count` 3). Una pasada con otro perfil de máquina: `gimg serve --stop`, encolar con
`GIMG_AUTOSTART=0` y `GIMG_MACHINE_PROFILE=<json> gimg work` (si no, el trabajador del servicio la corre con el perfil
normal).

Resultado (desglose, n=3 cada uno): FLUX definitivo 1024² 278 s (carga 6, muestreo 231, VAE 44; 28,8 s/paso);
FLUX borrador 512² 48 s; Z-Image 1024² 537 s (carga 8, muestreo 461, VAE 71; 57,7 s/paso). Calidad en el icono de
prueba: Z-Image da el trazo más limpio; FLUX definitivo deja fondo moteado gris y sale peor que su borrador.

**P1 descartada (2026-11-11):** Z-Image con `--vae-tile-size 512 --vae-tile-overlap 0.25` (9 trozos en vez de 49 de
256) da el mismo VAE (70,3 s frente a 70,5), la misma memoria libre (5367 frente a 5359 MB) y la misma imagen sin
costuras: no se aplica. Registro en `piloto/opt-ai/vae512-2026-11-11.jsonl`.

Desglose por tamaño, pasos y fase (carga, muestreo, VAE), que `measure.py` no da:
`python3 .claude/gw/gw-opt-ai-desglose.py <registro> [--profile P]`.

## Casos de calidad

No hay RAG. La calidad de imagen la juzgan la persona y los equipos de cada marca; los veredictos y descartes de
cada ronda quedan en `docs/handoff.md` (sección «Pendiente») y en `piloto/portal-marca/portal-web-final/`
(`descartes/` dentro de cada proyecto).

## Tiempos aceptables

Fijados con el banco del 2026-11-11 (P3), en `steam-deck-libre`: Z-Image 1024² p95 ≤ 9,5 min (medido 537 s);
FLUX borrador ≤ 1,2 min (medido 48 s); FLUX definitivo 1024² ≤ 4,5 min (medido 278 s, 8 s por encima: sin decidir si se
sube a 5 min; FLUX solo hace bocetos y su borrador sale mejor). FLUX con imagen de referencia 1344×768: 551 s (81 s/paso, n=2, ronda del 11-11).

## Ya en marcha

- Perfil `steam-deck-libre` a 7 GB de VRAM (2026-11-10).
- FLUX solo para bocetos; calidad con Z-Image a 8 pasos (2026-11-10).
- Desglose por tamaño y fase, `.claude/gw/gw-opt-ai-desglose.py` (P5, 2026-11-11).
- Banco de pruebas (P2) y tiempos aceptables (P3), 2026-11-11. VAE en trozos de 512 (P1) medido y descartado: no
  gana nada.
- No se propone: bajar Z-Image a menos de 8 pasos ni `--taesd` en la imagen final (calidad).
- `flux3-klein-q8` sigue con ajustes en `steam-deck-libre.json` sin estar instalado (1 llamada fallida el 2026-11-10);
  se deja: es una configuración puesta a propósito y no estorba.
