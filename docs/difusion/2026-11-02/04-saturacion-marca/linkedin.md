# LinkedIn: saturacion-marca

800 a 1.300 caracteres (el máximo es 3.000). Las dos primeras líneas enganchan: son lo único que se ve antes de
«ver más». Reto, cómo y qué se aprendió. De 3 a 5 etiquetas al final. LinkedIn no admite WebP: la imagen es el
`.png`.

## es

Bajar la luz arregló el brillo de una pieza, pero no su color.

Medimos la saturación de las piezas de la marca de un juego con el generador de imágenes local que estamos desarrollando. La primera versión salía lavada, así que oscurecimos el fondo: el brillo (YAVG) pasó de 169 a 66 y el texto claro quedó bien contrastado.

El color, en cambio, no se movió. La saturación (SATAVG) sigue en 5, cuando la marca pide entre 15 y 30. Y el ajuste a la paleta cayó al 51 %, porque el cielo que sale no está entre los colores de la guía de la marca.

Lo que sacamos: un fondo más oscuro no da más color. Toca pedirlo de forma explícita (un acento, una banda cálida más ancha) o aceptar que la marca queda desaturada. Y cómo se escribe el color en el prompt (palabras, hex o materiales) cambió muy poco la imagen.

Es trabajo en desarrollo y la cifra no nos favorece, pero justo por eso sirve de medida real. ¿Cómo corregís la saturación en imágenes generadas?

#IAgenerativa #ImagenIA #Diseño #BuildInPublic
Imagen: medios/metricas.png

## en

Darkening a piece fixed its brightness, but not its colour.

We measured the saturation of a game brand's pieces with the local image generator we're building. The first version came out washed out, so we darkened the background: brightness (YAVG) went from 169 to 66 and the light text got good contrast.

The colour, though, didn't move. Saturation (SATAVG) is still 5, when the brand asks for 15 to 30. And palette fit dropped to 51 %, because the sky that comes out isn't among the colours in the brand guide.

What we took from it: a darker background doesn't give you more colour. You have to ask for it explicitly (an accent, a wider warm band) or accept that the brand ends up desaturated. And how the colour is written in the prompt (words, hex or materials) barely changed the image.

It's work in progress and the figure doesn't flatter us, but that is what makes it a real measurement. How do you correct saturation in generated images?

#GenerativeAI #AIImages #Design #BuildInPublic
Imagen: medios/metricas.en.png
