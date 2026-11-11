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
# previous: <el registro de la ronda anterior>
exclude_tasks: warmup
cold_ms: 100
```

`cold_ms: 100` marca como frío el 100 % de las llamadas: `sd-cli` carga el modelo en cada imagen (no hay servidor
residente). Es el comportamiento esperado, no un hallazgo, mientras gimg no tenga motor residente.

## Banco de pruebas

Aprobado el 2026-11-11 (P2), sin lanzar: necesita la GPU libre (ni el juego ni el narrador cargado en Ollama). Un
pedido fijo, `examples/portal/orders/marca/14-icono-implantacion.json`, con 3 semillas y a 1024×1024 en el perfil
**`steam-deck-libre`**: FLUX definitivo, FLUX borrador y Z-Image (unos 30-35 min). Su registro va a
`piloto/opt-ai/base-<fecha>.jsonl` y pasa a `previous` en los ajustes. Segunda pasada, la de P1: Z-Image con
`--vae-tile-size 512 --vae-tile-overlap 0.25`, mismas semillas, comparada con
`measure.py <después> --previous <base> --profile steam-deck-libre` y mirando las imágenes a tamaño real por si hay
costuras en cuadrícula de 512.

Desglose por tamaño, pasos y fase (carga, muestreo, VAE), que `measure.py` no da:
`python3 .claude/gw/gw-opt-ai-desglose.py <registro> [--profile P]`.

## Casos de calidad

No hay RAG. La calidad de imagen la juzgan la persona y los equipos de cada marca; los veredictos y descartes de
cada ronda quedan en `docs/handoff.md` (sección «Pendiente») y en `piloto/portal-marca/portal-web-final/`
(`descartes/` dentro de cada proyecto).

## Tiempos aceptables

Propuestos el 2026-11-11 (P3), se fijan con los números del banco: en `steam-deck-libre`, Z-Image 1024² p95 ≤ 9,5
min; FLUX borrador ≤ 1,2 min; FLUX definitivo 1024² ≤ 4,5 min. Ronda del 2026-11-11 (desglose): Z-Image 1024² p50
536 s (carga 5,6, muestreo 461, VAE 71); FLUX con imagen de referencia 1344×768, 551 s (81 s/paso, n=2). Sin FLUX
1024² ni borrador medidos aún en este perfil.

## Ya en marcha

- Perfil `steam-deck-libre` a 7 GB de VRAM (2026-11-10).
- FLUX solo para bocetos; calidad con Z-Image a 8 pasos (2026-11-10).
- Desglose por tamaño y fase, `.claude/gw/gw-opt-ai-desglose.py` (P5, 2026-11-11).
- Aprobadas el 2026-11-11, pendientes de GPU libre: banco de pruebas (P2), VAE en trozos de 512 con solape 0,25 (P1,
  solo si el banco no muestra costuras ni fallos de memoria) y tiempos aceptables (P3).
- No se propone: bajar Z-Image a menos de 8 pasos ni `--taesd` en la imagen final (calidad).
- `flux3-klein-q8` sigue con ajustes en `steam-deck-libre.json` sin estar instalado (1 llamada fallida el 2026-11-10);
  se deja: es una configuración puesta a propósito y no estorba.
