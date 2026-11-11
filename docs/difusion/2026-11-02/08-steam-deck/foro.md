# Foro: steam-deck

Post de foro propio: un título y un cuerpo en Markdown (10.000 caracteres como máximo por idioma). Sin normas de
subreddit. Aporta algo a la comunidad antes que promocionar.

## es

**Título:** Generar imágenes en una Steam Deck: el modelo grande no cabe en la GPU y en CPU tarda 59 min

Estamos construyendo un generador local de imágenes (trabajo en curso, aún no entregado) cuya máquina de referencia es
una Steam Deck. Esto es lo que hemos medido al probar dos modelos a 1280×640.

**Lo que medimos**

- **FLUX.3 en la GPU no arranca.** Falla a los 12-13 s con: «need 5862.40 MB device / 5350.40 MB budget». Su grafo va
  en un solo segmento que no se trocea, así que limitar la memoria de vídeo no ayuda.
- **FLUX.3 en CPU sí funciona, pero tarda 59 min** (16 pasos), unas 15 veces el definitivo del modelo pequeño, y la RAM
  libre baja a unos 3 GB.
- **El modelo pequeño hace el definitivo en 229 s**, unos 4 minutos, con 8 pasos.

**Un aviso**

Subir el tope de memoria de vídeo a lo bruto llegó a bloquear la Deck. Por eso el generador lleva protecciones de
memoria propias.

**La pregunta**

Si generáis con modelos locales en una máquina justa, ¿qué os ha funcionado: partir el grafo, pasar a CPU, o quedaros
con un modelo más pequeño? Las rondas reales en la Deck siguen abiertas y vuestra experiencia nos sirve.

Imagen: medios/tarjeta.webp

## en

**Title:** Generating images on a Steam Deck: the big model does not fit on the GPU and takes 59 min on CPU

We are building a local image generator (work in progress, not shipped yet) whose reference machine is a Steam Deck.
This is what we measured when trying two models at 1280×640.

**What we measured**

- **FLUX.3 on the GPU does not start.** It fails after 12-13 s with: "need 5862.40 MB device / 5350.40 MB budget".
  Its graph is a single segment that cannot be split, so capping video memory does not help.
- **FLUX.3 on CPU works, but takes 59 min** (16 steps), about 15 times the small model's final, and free RAM drops to
  around 3 GB.
- **The small model makes the final in 229 s**, about 4 minutes, in 8 steps.

**A warning**

Raising the video memory cap by brute force ended up freezing the Deck. That is why the generator ships its own memory
safeguards.

**The question**

If you run local models on a tight machine, what has worked for you: splitting the graph, moving to CPU, or settling
for a smaller model? The real rounds on the Deck are still open and your experience helps.

Imagen: medios/tarjeta.en.webp
