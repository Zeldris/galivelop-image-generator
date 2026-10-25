# Un servicio local independiente, no una copia por proyecto ni ComfyUI

El generador de imágenes es un servicio propio, instalado una vez por máquina y compartido por todos los proyectos,
con API HTTP, CLI e interfaz web. Copiarlo en cada proyecto, como el `image-generator/` de World-Maker-Fantasy,
duplicaría los modelos (19 GB allí) y haría que cada copia divergiera. ComfyUI o InvokeAI resolverían la interfaz,
pero obligan a PyTorch y no traen las protecciones de memoria que la Steam Deck necesita (con `--max-vram vulkan0=6`
se bloqueó el 2026-10-24); un envoltorio fino de stable-diffusion.cpp las mantiene.

## Consecuencias

- Los proyectos dependen de un servicio externo a su repo: se conectan por su configuración del proyecto y
  la API, y su CI no puede generar imágenes.
