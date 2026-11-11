# Foro: más oscuro no es más color

Post de foro propio: título y cuerpo en Markdown, tono técnico y cercano, hasta 10000 caracteres por idioma.

## es

**Título:** Bajar la luz arregló el brillo, pero no el color: SATAVG 5 donde la marca pide 15-30

Estoy construyendo un generador de imágenes local y he medido las piezas de la marca de un juego. Es trabajo **en
desarrollo**, así que esto es una lectura de mitad de camino, y no me favorece.

La primera versión salía con el fondo lavado. Oscurecí la pieza y el brillo mejoró: el YAVG pasó de 169 a 66 y el texto
claro quedó bien contrastado. Pero el color no se movió:

- **SATAVG sigue en 5** (en la versión anterior era 7,8), cuando la marca pide entre 15 y 30.
- **El ajuste a la paleta cae al 51 %**: el cielo que sale no está entre los colores hex de la guía de la marca.

Conclusión: bajar la luz no basta. O pido el color de forma explícita (un acento en las agujas, una banda cálida más
ancha) o acepto que la marca queda desaturada.

Algo que ya sabía y que encaja: en pruebas anteriores, cómo escribía el color (con palabras, con hex o con materiales)
daba casi la misma imagen, y los hex no mejoraban de forma clara el porcentaje de paleta. Solo el material cambiaba la
escena, metiendo objetos y texturas.

Imagen: medios/metricas.webp

Aún no he decidido si corregirlo con una LUT o con color explícito en el prompt. ¿Qué os ha funcionado a vosotros para
subir la saturación sin que el modelo reinterprete la escena?

## en

**Title:** Darker fixed the brightness, not the colour: SATAVG 5 where the brand asks for 15-30

I'm building a local image generator and I measured the pieces of a game's brand. This is **work in progress**, so
it is a halfway reading, and it doesn't flatter me.

The first version came out with a washed-out background. I darkened the piece and the brightness improved: YAVG went
from 169 to 66 and the light text got good contrast. But the colour didn't move:

- **SATAVG is still 5** (it was 7.8 in the previous version), when the brand asks for 15 to 30.
- **Palette fit drops to 51 %**: the sky that comes out isn't among the hex colours in the brand guide.

Conclusion: lowering the light isn't enough. Either I ask for the colour explicitly (an accent on the spires, a wider
warm band) or I accept that the brand ends up desaturated.

Something I already knew that fits: in earlier tests, how I wrote the colour (words, hex or materials) gave almost the
same image, and hex values didn't clearly improve the palette percentage. Only materials changed the scene, bringing in
objects and textures.

Imagen: medios/metricas.en.webp

I haven't decided yet whether to fix it with a LUT or with explicit colour in the prompt. What has worked for you to
raise saturation without the model reinterpreting the scene?
