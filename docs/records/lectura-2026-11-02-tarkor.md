# Lectura 2026-11-02: novedades del generador de Tarkor

Resumen de un subagente `sonnet` (solo lectura) de lo cambiado desde la lectura del 2026-10-26
(`lectura-2026-10-26-tarkor-y-marcas.md`). Fuente: `WMF-imagenes`, rama `claude/plan-imagenes`, HEAD `56653c08`;
carpetas `image-generator/` y `docs/producto/plan-imagenes/` (`pautas.md`, `investigacion-lora-2.md`, `lora-kaggle.md`,
`resultados.md`, roadmap). Lo marcado *(inferencia)* no está en sus archivos. Las propuestas que salen de aquí están al
final, pendientes de la persona.

## Qué hicieron

- **IMG-21/22, `pautas.md` v5.2 (cerradas):** guía de prompting con evidencia por ronda. Con la v1 un agente barato
  acertaba 1 de 8; con la v5, 6 de 8 «se leen como su banner» a la primera, igual en semillas 3 y 7. Reglas de proceso:
  R1 (cada pauta en 2 semillas), R2 (lo que no mejora en 2 rondas sale del banco por prompt), R3 (se cierra con la
  mayoría).
- **IMG-23, perfil fotorreal y cadena de planos (cerrada):** `generar.sh` gana `PERFIL=fotorreal` (FLUX.3, CPU, tope
  10800), `BOCETO=`/`FUERZA_BOCETO` (0,97) y `MOMENTO=dia|atardecer|noche`, que **gradúa al terminar** con `gradar.sh`.
  La noche cruda sale con luz de día; gradada, la mediana EMD contra el banner baja de Y 35,8 / Cb 10,6 / Cr 11,4 a
  8,3 / 4,4 / 5,8 (el rojo se apaga: SATAVG 4,7). `planos.sh`: plancha, sujeto sobre croma guiado por boceto, montaje y
  armonización img2img a 0,5-0,7. Final 1280×512 a 16 pasos: 49 min, 5,8 GB libres de mínimo.
- **IMG-24, bocetos paramétricos (cerrada):** `bocetos/plantilla.py`, seis planes corporales de fauna en SVG, sin
  dependencias, rasterizados con rsvg-convert; las cuentas (ojos, placas) van en el boceto, no en el prompt.
- **IMG-27, encuadre desde la ficha (cerrada):** `scripts/encuadre.py` pasa fracciones del lienzo (horizonte, lado y
  ancho del sujeto) a posiciones de `montar.sh`, escaladas con el lienzo.
- **IMG-28, la palabra «sun» (cerrada, evidencia corta):** nombrarla pinta el disco aunque se diga «fuera de cuadro»;
  sin ella, la luz llega por la dirección pedida.
- **IMG-29/30/31, LoRA y referencias:** la release `master-1039-290148d` de stable-diffusion.cpp carga LoRAs
  diffusers/PEFT de FLUX.3 sobre Q8_0 en CPU (`--lora-model-dir` y `<lora:nombre:peso>` en el prompt). Con `-r`, **la
  referencia fija el sujeto** en otra escena. Una referencia de otro sujeto **no da el acabado** y cuesta +60 %.
  `--ref-image-args pass_to_vlm=true` no hace nada. No hay IP-Adapter, Redux ni ControlNet para FLUX.3.
- **IMG-32, LoRA de estilo entrenado en Kaggle (en curso):** 134 banners, rank 16, T4 de 16 GB, ~30 s/paso en fp32,
  1000 pasos (~8,5 h). Trampas: autocast fp16 de `accelerator.prepare()` daba `nan`, `context_embedder` sin cuantizar,
  tokenizador desde `text_encoder/`. Sin resultado de calidad todavía.

## Pautas generalizables

- Medidas relativas y fracciones del encuadre, no adjetivos; «a quarter of the way down from the top».
- Un ancla nombrada una vez, con su diferencia; nombrar un lugar real arrastra su contenido.
- Color y proporción se miden en la referencia, no se describen.
- **Luz:** por dirección, sin nombrar la fuente. El modelo tiende a escena luminosa y cálida; decir la escena oscura
  **al principio** del prompt lo corrige en parte. Gradar una imagen que ya sale sin sol, no arreglarla gradando.
- Sujeto y fondo por separado, con fondo de croma de un color que el sujeto no tenga.
- Boceto como imagen inicial a 0,95-0,97; por debajo de ~0,92 sale plano.
- El juicio «se lee como la referencia» va antes que la nota numérica.

## Propuestas para este repo (pendientes de la persona)

1. Pautas de luz y proceso (R1-R3) en las reglas de prompt y del banco, antes de r2 (F2.10). Coste bajo.
2. F2.9 como apoyo del juicio, no como aceptación sola. Coste nulo.
3. Gradación tras generar (como `MOMENTO=`) dentro de F2.11; *(inferencia)* es más probable que la LUT arregle la
   desaturación de Tarkor que una referencia de estilo. Coste medio.
4. Rebajar la expectativa de la ronda de referencias: `-r` sirve para conservar un sujeto, no un acabado. Coste nulo.
5. stable-diffusion.cpp `master-1039` con LoRA, a F5. Coste bajo, cambia la versión fija de `instalar.sh`.
6. Bocetos, planos y encuadre: a F5 (piloto de WMF); en contenido corporativo no hay sujeto que bocetar.
7. LoRA entrenado: esperar al veredicto de IMG-32.
