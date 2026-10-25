# Plan: generador de imágenes local reutilizable

Un generador de imágenes con IA local, instalado una vez por máquina, que cualquier proyecto puede usar. Nace del
`image-generator/` de World-Maker-Fantasy (WMF), que es su primer consumidor. Vocabulario en
[GLOSSARY.md](../GLOSSARY.md).

## Decisiones de diseño

Tomadas con `grilling` el 2026-10-25.

| # | Decisión | Por qué |
|---|---|---|
| D1 | El generador es un **servicio local independiente**, uno por máquina, con API HTTP, CLI e interfaz web propias | Copiarlo en cada proyecto duplica 19 GB de modelos y el código diverge; ComfyUI o InvokeAI no traen las protecciones de memoria de la Deck y obligan a PyTorch |
| D2 | **No conoce el dominio** de ningún proyecto: recibe pedidos cerrados (prompt, perfil, referencias, destino) | La lógica de prompts (fichas, `mundo.json`, `prompt_ficha.py`) es de cada proyecto; como mucho, un estilo del proyecto declarado, sin lógica |
| D3 | Cada proyecto se conecta con su **configuración del proyecto** (perfiles, estilo, carpeta de entrega) y manda pedidos por API o CLI; el generador no lee su base de datos ni su backend | Quita el Postgres por `podman`, el mundo fijo y la copia a mano a `uploads/images/` de WMF |
| D4 | **Primero Linux**, con la Steam Deck (Vulkan) como máquina de referencia; el motor, detrás de una interfaz para añadir Windows o NVIDIA sin reescribir | Es lo único probado; WMF es todo Linux |
| D5 | Binarios y modelos **fuera de git**, en una carpeta del usuario compartida por todos los proyectos, instalados por un script con versiones fijas y checksum; por defecto solo los usados (~7 GB) | Un solo juego de modelos por máquina; FLUX.3, la versión base y RealESRGAN quedan opcionales |
| D6 | **Python 3 solo stdlib** para servidor y CLI, `unittest` como check, interfaz en HTML + JS sin framework | Se instala junto a cualquier stack sin dependencias |
| D7 | **WMF es el piloto**: el diseño debe sustituir su `image-generator/` sin perder nada (galería, notas, elegida, referencia `-r`, estimado, protecciones de memoria); su migración es una tarea del repo de WMF | Valida el diseño con un caso real; desde aquí no se toca WMF |
| D8 | El término del dominio es **pedido**, no «encargo» | «Encargo a un subagente» ya es del flujo y un agente los confundiría |
| D9 | Un pedido tiene **N intentos**, cada uno *nuevo*, *candidata* o *descartada*, y **como mucho una elegida**; elegir otra sustituye la entrega, conserva el historial y se puede deshacer | WMF solo tiene «elegida» y elegir sobrescribe sin deshacer |
| D10 | **Cola persistente en disco**: una generación a la vez, en orden de llegada, cancelable, con estimado por mediana del registro (motor, perfil, pasos, referencia); sobrevive a un reinicio | En la Deck no caben dos a la vez; era IMG-11 en WMF |
| D11 | La CLI **arranca el servicio bajo demanda**, solo en `127.0.0.1`; unidad `systemd --user` opcional | Parado no gasta nada; en la Deck nada residente mientras se juega |
| D12 | El generador guarda en la configuración del usuario la **lista de proyectos** (`… proyecto añadir <ruta>`); la configuración de cada proyecto vive en su repo (p. ej. `galivelop-images.json`) | Un servicio, varios proyectos, cada uno con su configuración versionada |
| D13 | **Intentos, cola y registro** en la carpeta de datos del usuario, por proyecto; **elegidas** en la carpeta de entrega; un **manifiesto** versionable en el proyecto. El registro guarda todos los parámetros (versión del motor, modelos, cfg, sampler, pasos, semilla, tamaño, tiempo, memoria) con rutas relativas | El repo no se ensucia y cada elegida es reproducible; WMF no guardaba cfg ni modelo y usaba rutas absolutas |
| D14 | Motor inicial: **`sd-cli` lanzado por imagen**; `sd-server` se mide después como tarea de `opt-ai` | `sd-server` ocuparía ~7 GB fijos de los 16 GB compartidos de la Deck; se decide midiendo |
| D15 | Las protecciones van en un **perfil de máquina** (memoria libre mínima, `--max-vram`, `--params-backend`, referencias por pedido, tope de tiempo), con preajuste `steam-deck`; un pedido que lo supera se rechaza con un mensaje claro | Hoy están fijas en `generar.sh` y solo valen para la Deck |
| D16 | Interfaz y documentación en **español e inglés** desde el principio (`visibleLanguages` en `.claude/gw.json`), textos en un archivo por idioma | Herramienta para reutilizar y publicar; traducir después sale más caro |
| D17 | Los proyectos usan la **API HTTP y la CLI documentadas**, con JSON Schema de la configuración del proyecto y del pedido; sin librería cliente hasta que un segundo proyecto la pida | WMF (TypeScript) llama por HTTP; los esquemas validan sin código propio |

Decisiones difíciles de revertir, con su ADR: [0001](adr/0001-servicio-local-independiente.md) (D1) y
[0002](adr/0002-generador-sin-dominio.md) (D2).

## Punto de partida: lo que hay en WMF

- Motor: stable-diffusion.cpp `master-1000-95ff762`, `sd-cli` lanzado una vez por imagen, Vulkan, FLUX.2 klein 4B Q8 +
  Qwen3-4B Q4_K_M + VAE small decoder. Banner 1280x512 a 6 pasos: ~150 s (con `-r`, ~275 s).
- Protecciones: aborta con menos de 7000 MB libres, vigila `MemAvailable` (1500 MB), `--params-backend disk`,
  `--max-vram vulkan0=2` (`vulkan0=6` bloqueó la Deck).
- Interfaz: Python stdlib en `127.0.0.1:7861`, una generación a la vez sin cola, galería, notas, elegir.
- Deuda que el diseño no debe heredar: dos fuentes de prompt, registro sin cfg ni modelo y con rutas absolutas,
  `sd-server` sin uso, elegir sin deshacer, sin tests, solo Linux.

## Pendiente de decidir

Ronda 3 de `grilling`: identidad de un pedido, editar el prompt desde la interfaz, parámetros por perfil, formato y
nombre de la entrega, pantallas de la interfaz, nombre de la herramienta, instalación y versiones, límites de
seguridad, medición con `opt-ai`. Después, las fases de implementación.
