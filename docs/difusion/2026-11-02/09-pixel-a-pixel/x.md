# X: pixel-a-pixel

Hilo de 1 a 4 posts, cada uno de 280 caracteres como mucho (un enlace cuenta 23, un emoji 2). La imagen va en el
primero. Marca cada post con `**1/**`, `**2/**`… Un hashtag como mucho.

## es

**1/** Pasamos de un script de pruebas a un servicio local para generar imágenes. ¿Sale lo mismo con la misma semilla? Sí: 14 imágenes, idénticas píxel a píxel. En desarrollo.
Imagen: medios/codigo.webp

**2/** Lo comprobamos con el md5 de los fotogramas decodificados (`ffmpeg -f md5`). Los bytes del PNG difieren por un bloque de metadatos; los píxeles no. ¿Cómo comprobáis vosotros la reproducibilidad? #StableDiffusion

## en

**1/** We moved from a test script to a local service for generating images. Same seed, same output? Yes: 14 images, identical pixel for pixel. Work in progress.
Imagen: medios/codigo.en.webp

**2/** We checked the md5 of the decoded frames (`ffmpeg -f md5`). The PNG bytes differ by a metadata block; the pixels don't. How do you check reproducibility? #StableDiffusion
