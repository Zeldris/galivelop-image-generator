# LinkedIn: texto-svg

## es

Un cambio de titular no debería costar otros 49 minutos de generación.

FLUX no da texto legible, así que en mi generador de imágenes local el texto no lo pinta el modelo. El perfil declara una plantilla SVG con huecos (título, subtítulo, logo) y el tamaño de destino; el pedido trae los textos. El generador rasteriza la plantilla con rsvg-convert y la superpone con ffmpeg sobre la imagen generada, recortada y escalada.

Se guardan las dos imágenes: la cruda y la compuesta, que es la que se ve y se entrega. Así, recomponer con otro titular lleva unos 2 segundos y no toca la imagen generada. Los logos son SVG vectoriales, nunca generados: un logo tiene que ser idéntico en todas las piezas.

Esto está en desarrollo, todavía no entregado. Una lección por el camino: medir el contraste por percentiles no ve las líneas finas que cruzan el texto; toca medir en la caja de cada línea.

¿Componéis el texto aparte o se lo dejáis al modelo?

#IA #ImagenesIA #SVG #Desarrollo
Imagen: medios/diagrama.png

## en

A headline change shouldn't cost another 49 minutes of generation.

FLUX doesn't give legible text, so in my local image generator the model doesn't paint it. The profile declares an SVG template with slots (title, subtitle, logo) and the target size; the order carries the text values. The generator rasterizes the template with rsvg-convert and overlays it with ffmpeg on the generated image, cropped and scaled.

Both images are kept: the raw one and the composed one, which is what you see and deliver. So recomposing with a new headline takes about 2 seconds and never touches the generated image. Logos are vector SVGs, never generated: a logo has to be identical on every piece.

This is work in progress, not delivered yet. One lesson on the way: measuring contrast by percentiles misses thin lines crossing the text, so the next step is to measure inside the box of each line.

Do you compose text separately or leave it to the model?

#AI #GenerativeAI #SVG #BuildInPublic
Imagen: medios/diagrama.en.png
