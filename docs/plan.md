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
| D18 | Cada pedido lleva una **clave del pedido** que pone el proyecto (p. ej. `fauna/aullador-rojo`); clave + perfil identifican el pedido, y reenviarlo **lo actualiza** conservando sus intentos | Como `<tipo>/<slug>` y `ImagePrompt` en WMF; sin clave, cada reenvío lo duplicaría |
| D19 | La interfaz deja **retocar el prompt**; cada intento guarda el prompt exacto y el manifiesto el de la elegida; el original del proyecto no se toca | Así se afina en WMF (`prompt \| desdeBase`); el proyecto sigue siendo la fuente (D2) |
| D20 | La configuración del proyecto declara **por perfil** tamaño, pasos, cfg, sampler y modelo; un pedido o la interfaz los cambian por intento, dentro del perfil de máquina | Hoy pasos y cfg son variables de entorno de `generar.sh`, sin selector |
| D21 | Entrega en **PNG**, con nombre por plantilla de la configuración del proyecto (por defecto `{clave}-{perfil}.png`); WebP y miniaturas, posproceso opcional más adelante | `sd-cli` da PNG y convertir sin dependencias no es trivial; el nombre coincide con `uploads/images/<tipo>/<slug>-<perfil>.png` de WMF |
| D22 | Interfaz en **tres pantallas**: proyectos; pedidos de un proyecto (filtros por perfil y estado, cola visible); un pedido (galería con estados, notas por intento, retoque de prompt y parámetros, otra semilla o N seguidas, comparar dos lado a lado) | Todo lo de WMF más estados, cola y comparar |
| D23 | Repo `galivelop-image-generator`, orden **`gimg`**, configuración del proyecto en `galivelop-images.json` | Corto y sin choques habituales en Linux |
| D24 | Instalación con `git clone` + `instalar.sh` (pone `gimg` en `~/.local/bin`, descarga motor y modelos, D5); la configuración del proyecto declara la **versión mínima** del generador y `gimg` avisa si la instalada es más antigua; semver y CHANGELOG | Sin pip ni paquetes; un proyecto sabe si su configuración vale con lo instalado |
| D25 | **Solo escribe** en su carpeta de datos y en la carpeta de entrega de proyectos registrados; **solo lee** referencias dentro del proyecto; rechaza `..` y enlaces que salgan. API solo en localhost, Content-Type JSON y mismo Origin | Las rutas de un pedido vienen del proyecto |
| D26 | El registro es **JSONL en el formato de `opt-ai`** (`.claude/skills/opt-ai/references/log-format.md`), una línea por intento: `gen_ai.provider.name` = `stable-diffusion.cpp`, `gen_ai.request.model`, `app.task` = perfil, `app.machine_profile`, `app.duration_ms`, `app.load_ms`, `app.error`, y lo propio de la imagen bajo `app.image.*` (pasos, cfg, sampler, tamaño, semilla, referencias, commit del motor, tiempos de muestreo y decodificado, memoria mínima). Se propone al flujo, con `gw-harvest`, una operación de imagen en `log-format.md` | `medir.py` acepta cualquier operación y agrupa por perfil de máquina, tarea y modelo, así que mide imágenes sin cambios; cierra IMG-3 de WMF |

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

## Fases (aprobadas el 2026-10-25)

Cada fase es una rama y un pull request a `main`, con las tres fases de revisión de `AGENTS.md`.

| Fase | Qué trae | Hecha cuando |
|---|---|---|
| F0 Esqueleto | Estructura del repo; JSON Schema de la configuración del proyecto, el pedido y el perfil de máquina; textos es/en; README es/en; `check` real (`python3 -m unittest`) | El check corre tests y los esquemas validan los ejemplos |
| F1 Núcleo | Proyectos registrados, pedidos (clave + perfil), intentos y estados, elegida con deshacer, entrega y manifiesto, cola persistente, límites de seguridad, registro JSONL; CLI `gimg` básica; todo con un **motor de pruebas** que no genera de verdad | Tests en verde del ciclo completo con el motor de pruebas |
| F2 Motor real | Envoltorio de `sd-cli` con el perfil de máquina (memoria, `--max-vram`, tope, cancelar, progreso); `instalar.sh` con versiones fijas y checksum | Un pedido real generado en la Deck (comprobación manual de la persona) |
| F3 API y arranque | API HTTP (D17, D25) y arranque bajo demanda; unidad `systemd --user` opcional | Tests de la API; `gimg` arranca el servicio solo |
| F4 Interfaz | Las tres pantallas de D22, es/en | Recorrido completo en el navegador |
| F5 Piloto WMF | Configuración de ejemplo para WMF, guía de integración y propuesta de migración para su repo; medida base con `opt-ai` y comparación `sd-server` (D14) | WMF genera y recibe una elegida sin copia a mano |

## Pendiente

- Proponer al flujo (`gw-harvest`) una operación de imagen en `opt-ai/references/log-format.md` (D26).
