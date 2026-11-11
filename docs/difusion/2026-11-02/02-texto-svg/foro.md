# Foro: el texto no lo pinta el modelo

Post de foro propio: título y cuerpo en Markdown, tono técnico y cercano, hasta 10000 caracteres por idioma.

## es

**Título:** El texto no lo pinta el modelo: plantilla SVG y recomponer en 2 segundos

Estoy trabajando en un generador de imágenes local y me topé con lo de siempre: FLUX no da texto legible. Los prompts
de otro de mis proyectos acaban pidiendo «completely textless», y aun así el titular y el logo tienen que salir
perfectos en cada pieza.

La solución que estoy montando (**en desarrollo**, todavía no está entregada) saca el texto del modelo:

- El perfil declara una plantilla SVG con huecos (título, subtítulo, logo) y el tamaño de destino.
- El pedido trae los textos.
- El generador rasteriza la plantilla con `rsvg-convert` y la superpone con `ffmpeg` sobre la imagen generada,
  recortada y escalada al tamaño de destino.
- Se guardan las dos imágenes: la cruda (`q<id>.raw.png`) y la compuesta (`q<id>.png`), que es la que se ve y se entrega.

Lo que gano: un cambio de titular tras 49 minutos de generación no puede costar otros 49. Con la cruda guardada,
`gimg compose` recompone sin volver a generar, y componer una pieza lleva unos 2 segundos sin tocar la imagen.

Los logos, además, son SVG vectoriales y nunca se generan: un logo tiene que ser idéntico en todas las piezas.

Un detalle que ya me ha dado trabajo: medir el contraste por percentiles no ve las líneas finas que cruzan el texto.
Lo siguiente es medir en la caja real de cada línea.

Imagen: medios/diagrama.webp

¿Cómo resolvéis vosotros el texto en imágenes con IA local? ¿Componéis aparte o lo dejáis al modelo?

## en

**Title:** The model doesn't paint the text: an SVG template and recomposing in 2 seconds

I'm building a local image generator and ran into the usual wall: FLUX doesn't give legible text. The prompts of
another project of mine end up asking for "completely textless", yet the headline and logo still have to come out
perfect on every piece.

The approach I'm putting together (**work in progress**, not delivered yet) takes the text away from the model:

- The profile declares an SVG template with slots (title, subtitle, logo) and the target size.
- The order carries the text values.
- The generator rasterizes the template with `rsvg-convert` and overlays it with `ffmpeg` on the generated image,
  cropped and scaled to the target size.
- Both images are kept: the raw one (`q<id>.raw.png`) and the composed one (`q<id>.png`), which is the one you see
  and deliver.

What I get: a headline change after 49 minutes of generation can't cost another 49. With the raw image kept,
`gimg compose` recomposes without regenerating, and composing a piece takes about 2 seconds without touching the
generated image.

Logos are also vector SVGs and are never generated: a logo has to be identical on every piece.

One detail that already cost me some work: measuring contrast by percentiles misses thin lines crossing the text.
Next I'll measure inside the real box of each text line.

Imagen: medios/diagrama.en.webp

How do you handle text in local AI images? Do you compose separately or leave it to the model?
