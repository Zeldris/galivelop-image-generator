# Plan: generador de imágenes local reutilizable

Un generador de imágenes con IA local, instalado una vez por máquina, que cualquier proyecto puede usar. Nace del
`image-generator/` de World-Maker-Fantasy (WMF), que es su primer consumidor. Vocabulario en
[GLOSSARY.md](../GLOSSARY.md).

## Decisiones de diseño

Tomadas con `grilling` el 2026-10-25.

| # | Decisión | Por qué |
|---|---|---|
| D1 | El generador es un **servicio local independiente**, uno por máquina, con API HTTP, CLI e interfaz web propias | Copiarlo en cada proyecto duplica 19 GB de modelos y el código diverge; ComfyUI o InvokeAI no traen las protecciones de memoria de la Deck y obligan a PyTorch |
| D2 | **No conoce el dominio** de ningún proyecto: recibe encargos cerrados (prompt, perfil, referencias, destino) | La lógica de prompts (fichas, `mundo.json`, `prompt_ficha.py`) es de cada proyecto; como mucho, un estilo del proyecto declarado, sin lógica |
| D3 | Cada proyecto se conecta con su **configuración del proyecto** (perfiles, estilo, carpeta de entrega) y manda encargos por API o CLI; el generador no lee su base de datos ni su backend | Quita el Postgres por `podman`, el mundo fijo y la copia a mano a `uploads/images/` de WMF |
| D4 | **Primero Linux**, con la Steam Deck (Vulkan) como máquina de referencia; el motor, detrás de una interfaz para añadir Windows o NVIDIA sin reescribir | Es lo único probado; WMF es todo Linux |
| D5 | Binarios y modelos **fuera de git**, en una carpeta del usuario compartida por todos los proyectos, instalados por un script con versiones fijas y checksum; por defecto solo los usados (~7 GB) | Un solo juego de modelos por máquina; FLUX.3, la versión base y RealESRGAN quedan opcionales |
| D6 | **Python 3 solo stdlib** para servidor y CLI, `unittest` como check, interfaz en HTML + JS sin framework | Se instala junto a cualquier stack sin dependencias |
| D7 | **WMF es el piloto**: el diseño debe sustituir su `image-generator/` sin perder nada (galería, notas, elegida, referencia `-r`, estimado, protecciones de memoria); su migración es una tarea del repo de WMF | Valida el diseño con un caso real; desde aquí no se toca WMF |

## Punto de partida: lo que hay en WMF

- Motor: stable-diffusion.cpp `master-1000-95ff762`, `sd-cli` lanzado una vez por imagen, Vulkan, FLUX.2 klein 4B Q8 +
  Qwen3-4B Q4_K_M + VAE small decoder. Banner 1280x512 a 6 pasos: ~150 s (con `-r`, ~275 s).
- Protecciones: aborta con menos de 7000 MB libres, vigila `MemAvailable` (1500 MB), `--params-backend disk`,
  `--max-vram vulkan0=2` (`vulkan0=6` bloqueó la Deck).
- Interfaz: Python stdlib en `127.0.0.1:7861`, una generación a la vez sin cola, galería, notas, elegir.
- Deuda que el diseño no debe heredar: dos fuentes de prompt, registro sin cfg ni modelo y con rutas absolutas,
  `sd-server` sin uso, elegir sin deshacer, sin tests, solo Linux.

## Pendiente de decidir

Siguientes rondas de `grilling`: ciclo de vida de los intentos, cola, cómo se arranca el servicio, registro de
proyectos, dónde viven intentos y registro, motor (`sd-cli` o `sd-server`), protecciones por máquina, idiomas de la
interfaz.
