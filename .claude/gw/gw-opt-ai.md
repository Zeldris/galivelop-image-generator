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

Pendiente de montar (propuesta, 2026-11-11): un pedido fijo por modelo con 3 semillas, mismo prompt y mismo
tamaño (1024×1024), con el juego y Ollama parados: `examples/portal/orders/marca/14-icono-implantacion.json` en
FLUX definitivo, FLUX borrador y Z-Image. Unos 30 min en total.

## Casos de calidad

No hay RAG. La calidad de imagen la juzgan la persona y los equipos de cada marca; los veredictos y descartes de
cada ronda quedan en `docs/handoff.md` (sección «Pendiente») y en `piloto/portal-marca/portal-web-final/`
(`descartes/` dentro de cada proyecto).

## Tiempos aceptables

Sin fijar. Referencia medida a mano (2026-11-10, `steam-deck-libre`): Z-Image 8 pasos a 1024 ≈ 10 min por
imagen; FLUX definitivo ≈ 4 min; FLUX borrador (512, 4 pasos) ≈ 1 min.

## Ya en marcha

- Perfil `steam-deck-libre` a 7 GB de VRAM (2026-11-10).
- FLUX solo para bocetos; calidad con Z-Image a 8 pasos (2026-11-10).
