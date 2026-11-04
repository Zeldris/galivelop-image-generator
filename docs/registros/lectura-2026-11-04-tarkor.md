# Lectura 2026-11-04: el LoRA de estilo de Tarkor (IMG-32/33)

Resumen de un subagente `sonnet` (solo lectura) de lo cambiado desde la lectura del 2026-11-02
(`lectura-2026-11-02-tarkor.md`, HEAD `56653c08`) hasta `8a48fe52` de `WMF-imagenes` (`claude/plan-imagenes`), más
lo que no está en git en `World-Maker-Fantasy/image-generator/` (`bin-nuevo/`, `loras/`, `generated/banco/img32/`).
Lo marcado *(inferencia)* no está en sus archivos.

## Qué hicieron

- **IMG-32, LoRA de estilo:** 134 banners del juego (1280×512), textos de Qwen3-VL-2B con la palabra disparadora
  `wmfstyle`; diffusers 0.42.1 sobre `flux-3-image-klein-base`, transformer nf4 calculando en fp32 (fp16 daba `nan`),
  rank 16, LR 1e-4, 1000 pasos, Kaggle T4 ×2, 9 h 32 min. Archivo: `loras/wmf-estilo.safetensors`, 161 MB, sin
  versionar (`lora/entrenar.ipynb` y `lora/conjunto.sh`). Prueba a 640×256, 8 pasos, semilla 42: +7-8 % de tiempo
  (508 → 546 s). EMD de Y: aullador (está en el entreno) 21,3 → 13,8; criatura nueva en valle gris 13,9 → 14,0 (peso
  1), 12,9 (1,5), 12,7 (2, con fallos); criatura nueva en escena cálida 47,2 → 30,7 (1) y 29,6 (1,5). **Veredicto:**
  peso 1 en el perfil fotorreal; acerca la luz y la neblina a los banners, **no la forma** de la criatura.
- **IMG-33, integración:** `bin-nuevo/sd-cli` es la release `master-1039-290148d` (Vulkan, precompilada, descargada a
  mano), aparte de `bin/` (`master-1000-95ff762`). `generar.sh` con `PERFIL=fotorreal` usa `bin-nuevo`, añade
  `wmfstyle, <prompt> <lora:wmf-estilo:$LORA>` y `--lora-model-dir`; `LORA=0` lo quita, un peso no numérico sale con 2,
  sin el archivo avisa y sigue. LoRA más gradación por `MOMENTO`: 563 s y 5,4 GB libres de mínimo. 5 tests con un
  `sd-cli` falso. La cadena de planos no se ha corrido entera con `bin-nuevo`.
- **IMG-4 cerrada; IMG-6 se rehace** con la cadena fotorreal y el LoRA (tanda del 2026-11-03 en `generated/`:
  aullador, cardo, Hulki, pastos), veredicto de la usuaria pendiente.
- **Retro (QA-280…284):** `/code-review` al cerrar cada tarea (los medios salían días después); a `main` por bloque
  (90 commits en 8 días); `hoja.sh --archivos`: hojas de contactos para revisar imágenes (14 sueltas costaron ~890k
  tokens; una hoja de 6 cuesta como una imagen); `gradar.sh` firma cada LUT con un sha1 de sus curvas en el `TITLE` y,
  si no casa con `gradacion.json`, usa las curvas y avisa de rehornear. QA-271: `--max-vram` alto (`vulkan0=6`) y
  `--offload-to-cpu` bloquearon la Deck.
- **Luz por momento:** el estilo lleva `{luz}` con un valor por momento (el «golden-hour» llegaba a la noche).
- **Abierto:** licencia FLUX Kommunity sin leer; términos de OpenAI sobre entrenar con los banners sin cerrar; cuota de
  Kaggle sin confirmar. No planean un LoRA por marca *(inferencia: lo que daría la forma sería uno por sujeto)*.

## Medida propia (`gimg measure`, `generated/banco/img32/`)

| Imagen | YAVG base → LoRA | SATAVG base → LoRA |
|---|---|---|
| aullador (en el entreno) | 94,6 → 84,3 | 34,5 → 42,1 |
| criatura nueva, escena cálida | 132,4 → 113,7 (1,5: 111,8) | 27,7 → 34,2 (1,5: 36,1) |
| criatura nueva, valle gris | 115,3 → 118,4 (2: 116,2) | 6,6 → 5,8 (2: 5,5) |

El LoRA satura cuando el prompt ya pide una escena cálida como las del juego. Con un prompt gris, la saturación se
queda en 5-6, la misma que el Tarkor corporativo en r5 (5-7). Esto es lo que más pesa en las propuestas.

## Propuestas para este repo (pendientes de la persona)

Están en la conversación del 2026-11-04 y en la bitácora (Pendiente) hasta que la persona decida.
