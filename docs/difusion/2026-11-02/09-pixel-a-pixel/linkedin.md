# LinkedIn: pixel-a-pixel

800 a 1.300 caracteres (el máximo es 3.000). Las dos primeras líneas enganchan: son lo único que se ve antes de
«ver más». Reto, cómo y qué se aprendió. De 3 a 5 etiquetas al final. LinkedIn no admite WebP: la imagen es el
`.png`.

## es

Cambiamos de script a servicio y las 14 imágenes salieron idénticas, píxel a píxel.

Estamos desarrollando un generador de imágenes con IA local. Antes se generaba con un script de pruebas; ahora lo hace un servicio con cola, y el cambio no debía alterar el resultado. «Debía» no es una comprobación, así que repetimos las 14 piezas con las mismas semillas y comparamos.

La comparación es una línea por imagen: el md5 de los fotogramas decodificados con ffmpeg (`-f md5`). Los archivos PNG no son idénticos byte a byte, porque el servicio añade un bloque de metadatos, pero el md5 de los píxeles coincide en las 14.

Lo que aprendimos: comparar archivos engaña, comparar píxeles no. Y otro dato útil para planificar: el tiempo de cada pieza va con los píxeles y los pasos, y se puede predecir con un margen de ±1 %.

El servicio todavía está en desarrollo. ¿Cómo comprobáis vosotros que un cambio de motor no cambia la imagen?

#IAgenerativa #Reproducibilidad #BuildInPublic #Python
Imagen: medios/codigo.png

## en

We moved from a script to a service and all 14 images came out identical, pixel for pixel.

We're building a local AI image generator. It used to run through a test script; now a queue-backed service does it, and the change wasn't supposed to alter the result. "Supposed to" isn't a check, so we regenerated the 14 pieces with the same seeds and compared.

The comparison is one line per image: the md5 of the frames decoded with ffmpeg (`-f md5`). The PNG files aren't byte-identical, because the service adds a metadata block, but the pixel md5 matches on all 14.

What we learned: comparing files misleads, comparing pixels doesn't. And a useful planning note: each piece's time follows its pixels and steps, and can be predicted within ±1 %.

The service is still in development. How do you check that an engine change doesn't change the image?

#GenerativeAI #Reproducibility #BuildInPublic #Python
Imagen: medios/codigo.en.png
