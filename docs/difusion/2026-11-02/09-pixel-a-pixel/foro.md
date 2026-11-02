# Foro: pixel a pixel

Post de foro propio: título y cuerpo en Markdown, tono técnico y cercano, hasta 10000 caracteres por idioma.

## es

**Título:** Mismo resultado, píxel a píxel: cómo comprobé que el servicio genera lo mismo que mi script

Estoy construyendo un generador de imágenes con IA local. Al principio generaba con un script de pruebas; ahora lo hace un servicio con cola. Es trabajo **en desarrollo**: el motor real todavía no está fusionado en la rama principal. El cambio no debía alterar nada, pero quería una prueba, no una impresión.

La prueba: las 14 piezas de la ronda (1280×640, 6 pasos, dos semillas) se generaron de nuevo con el servicio y se compararon con las del script.

Comparar archivos no sirve: los PNG difieren byte a byte porque el servicio añade un bloque `tEXt` de metadatos. Lo que importa son los píxeles, y para eso basta el md5 de los fotogramas decodificados con ffmpeg:

```sh
# mismo md5 = mismos píxeles
ffmpeg -v error -i script/og-s3.png -f md5 -
ffmpeg -v error -i servicio/og-s3.png -f md5 -
```

(Los nombres de archivo están simplificados.) Resultado: **las 14 imágenes dan el mismo md5**, píxel a píxel iguales.

Imagen: medios/codigo.webp

Dos notas:

- **Reproducibilidad con semilla:** con el mismo modelo, los mismos pasos y la misma semilla, el servicio no cambió ni un píxel.
- **El tiempo es predecible:** va con los píxeles y los pasos, y se puede estimar con un margen de ±1 %.

¿Cómo comprobáis vosotros la reproducibilidad entre versiones o entre motores? ¿Usáis md5 de píxeles, una métrica de diferencia o a ojo?

## en

**Title:** Same result, pixel for pixel: how I checked the service generates what my script did

I'm building a local AI image generator. It started out generating through a test script; now a queue-backed service does it. This is **work in progress**: the real engine isn't merged into the main branch yet. The change wasn't supposed to alter anything, but I wanted proof, not a feeling.

The test: the 14 pieces of the round (1280×640, 6 steps, two seeds) were generated again with the service and compared with the script's.

Comparing files doesn't work: the PNGs differ byte for byte because the service adds a `tEXt` metadata block. What matters is the pixels, and the md5 of the frames decoded with ffmpeg is enough for that:

```sh
# same md5 = same pixels
ffmpeg -v error -i script/og-s3.png -f md5 -
ffmpeg -v error -i service/og-s3.png -f md5 -
```

(File names are simplified.) Result: **all 14 images give the same md5**, identical pixel for pixel.

Imagen: medios/codigo.en.webp

Two notes:

- **Reproducibility with a seed:** with the same model, steps and seed, the service didn't change a single pixel.
- **Time is predictable:** it follows pixels and steps, and can be estimated within ±1 %.

How do you check reproducibility across versions or engines? Pixel md5, a difference metric, or by eye?
