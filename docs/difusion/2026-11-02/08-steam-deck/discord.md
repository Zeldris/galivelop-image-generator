# Discord: steam-deck

Markdown de Discord. Cada mensaje tiene menos de 2.000 caracteres; si hace falta más, se parte con una línea que
solo contenga `---`. Título, novedades, detalle técnico y qué viene. El título va con `###`: un `##` cierra la
sección del idioma.

## es

### Generar en una Steam Deck: lo que cabe y lo que no

- El modelo grande (FLUX.3) no arranca en la GPU: pide 5862 MB y el margen es de 5350 MB.
- En CPU sí funciona, pero tarda 59 min a 1280×640.
- El modelo pequeño hace el definitivo en 229 s, unos 4 minutos.

Imagen: medios/tarjeta.webp

---

Detalle: en la GPU, el grafo del modelo grande va en un solo segmento que no se trocea, así que el tope de memoria no
le sirve; en CPU son unas 15 veces el tiempo del pequeño y la RAM libre baja a unos 3 GB. Subir el tope de memoria de
vídeo a lo bruto también llegó a bloquear la consola. Todo esto es trabajo en curso: las rondas reales en la Deck
siguen abiertas.

## en

### Generating on a Steam Deck: what fits and what does not

- The big model (FLUX.3) will not start on the GPU: it needs 5862 MB and the budget is 5350 MB.
- On CPU it runs, but it takes 59 min at 1280×640.
- The small model makes the final in 229 s, about 4 minutes.

Imagen: medios/tarjeta.en.webp

---

Detail: on the GPU, the big model's graph is a single segment that cannot be split, so the memory cap does not help;
on CPU it is about 15 times the small model's time and free RAM drops to around 3 GB. Raising the video memory cap by
brute force also ended up freezing the console. All of this is work in progress: the real rounds on the Deck are
still open.
