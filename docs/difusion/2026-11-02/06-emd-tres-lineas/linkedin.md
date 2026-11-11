# LinkedIn: emd-tres-lineas

800 a 1.300 caracteres (el máximo es 3.000). Las dos primeras líneas enganchan: son lo único que se ve antes de
«ver más». Reto, cómo y qué se aprendió. De 3 a 5 etiquetas al final. LinkedIn no admite WebP: la imagen es el
`.png`.

## es

¿Se parece esta imagen a la marca? Se puede responder con un número y tres líneas de Python.

Estamos desarrollando un generador de imágenes con IA local y necesitábamos medir, no opinar, si lo que sale encaja con la marca de un juego. Una de las medidas es la distancia de Wasserstein (EMD) entre los histogramas de color de la imagen y los de una referencia, por cada canal: Y, Cb y Cr.

En una dimensión es corta: se acumula cada histograma y se suma la diferencia absoluta entre las dos distribuciones acumuladas sobre los 256 niveles. Sin numpy, solo con la biblioteca estándar de Python, y devuelve un número por canal, no un veredicto.

Lo que aprendimos: cuando la medida cabe en una pantalla, se puede leer, discutir y fiarse de ella. Lo que aún no sabemos es qué umbrales dar por buenos, y por eso la medida sigue en desarrollo.

¿Qué distancia usáis vosotros para comparar el estilo de dos imágenes?

#Python #VisiónPorComputador #IAgenerativa #BuildInPublic
Imagen: medios/codigo.png

## en

Does this image match the brand? You can answer it with one number and three lines of Python.

We're building a local AI image generator and needed to measure, not guess, whether its output fits a game's brand. One of the measures is the Wasserstein distance (EMD) between the colour histograms of the image and of a reference, per channel: Y, Cb and Cr.

In one dimension it's short: accumulate each histogram and sum the absolute difference between the two cumulative distributions over the 256 levels. No numpy, just the Python standard library, and it returns one number per channel, not a verdict.

What we learned: when a measure fits on one screen, you can read it, argue about it and trust it. What we still don't know is which thresholds to accept, which is why the measure is still in development.

What distance do you use to compare the style of two images?

#Python #ComputerVision #GenerativeAI #BuildInPublic
Imagen: medios/codigo.en.png
