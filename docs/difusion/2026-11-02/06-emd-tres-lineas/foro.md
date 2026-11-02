# Foro: EMD en tres líneas

Post de foro propio: título y cuerpo en Markdown, tono técnico y cercano, hasta 10000 caracteres por idioma.

## es

**Título:** ¿Se parece esta imagen a la marca? La distancia entre histogramas de color en tres líneas de Python

Estoy construyendo un generador de imágenes con IA local y necesitaba una pregunta con respuesta numérica: ¿esta imagen se parece a las de la marca de un juego? Es trabajo **en desarrollo**: la medida todavía no está fusionada en la rama principal.

Lo que he usado es la distancia de Wasserstein (EMD) entre los histogramas de cada canal, Y, Cb y Cr. En una dimensión es sencilla: se acumula cada histograma y se suma la diferencia absoluta entre las dos distribuciones acumuladas, nivel a nivel, sobre los 256 niveles.

```python
def emd(planes_a, planes_b) -> dict:
    # Wasserstein-1: suma sobre los 256 niveles de |CDF a - CDF b|
    return {name: sum(abs(x - y) for x, y in zip(_cdf(a), _cdf(b)))
            for name, a, b in zip(CHANNELS, planes_a, planes_b)}
```

(`_cdf` acumula el histograma del canal y lo divide por el total de píxeles. He partido el `return` en dos líneas y cambiado el docstring por un comentario para que quepa.)

Lo que me gusta de esto:

- **No hace falta numpy.** El proyecto usa solo la biblioteca estándar de Python.
- **Devuelve un número por canal**, no un veredicto: la misma función sirve para comparar con una referencia o con varias.
- **Es pequeña**, así que se puede leer y discutir entera.

Imagen: medios/codigo.webp

En el generador, `gimg measure` junta esta medida con el porcentaje de paleta, el YAVG y el SATAVG, y el contraste WCAG de una zona de texto. Lo que no sé aún es qué umbrales dar por buenos. ¿Qué distancia usáis vosotros para comparar estilo entre imágenes?

## en

**Title:** Does this image match the brand? Colour-histogram distance in three lines of Python

I'm building a local AI image generator and needed a question with a numeric answer: does this image look like the ones from a game's brand? It's **work in progress**: the measurement isn't merged into the main branch yet.

I used the Wasserstein distance (EMD) between the histograms of each channel, Y, Cb and Cr. In one dimension it's simple: accumulate each histogram and add up the absolute difference between the two cumulative distributions, level by level, over the 256 levels.

```python
def emd(planes_a, planes_b) -> dict:
    # Wasserstein-1: sum over the 256 levels of |CDF a - CDF b|
    return {name: sum(abs(x - y) for x, y in zip(_cdf(a), _cdf(b)))
            for name, a, b in zip(CHANNELS, planes_a, planes_b)}
```

(`_cdf` accumulates the channel's histogram and divides by the total pixel count. I split the `return` over two lines and swapped the docstring for a comment so it fits.)

What I like about it:

- **No numpy needed.** The project uses only the Python standard library.
- **It returns one number per channel**, not a verdict: the same function compares against one reference or several.
- **It's small**, so the whole thing can be read and discussed.

Imagen: medios/codigo.en.webp

In the generator, `gimg measure` puts this together with palette fit, YAVG and SATAVG, and the WCAG contrast of a text zone. What I still don't know is which thresholds to accept. What distance do you use to compare style between images?
