# galivelop-image-generator

[English](README.en.md)

Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos (D1, D2). Usa
stable-diffusion.cpp como motor y la Steam Deck como máquina de referencia (D4). Sin dependencias: Python 3 solo con
la biblioteca estándar (D6).

## Estado

Versión **0.4.0**, fases **F0-F4 hechas** y en `main`: proyectos, pedidos, intentos, elegida y entrega, cola
persistente, CLI, motor real (`sd-cli`, con `instalar.sh`), composición y medida de marca, API HTTP local e interfaz en
el navegador. Quedan comprobaciones manuales en la Deck (rondas del piloto, recorrido de la interfaz en el navegador),
el piloto con proyectos reales (F5) y lo que sigue (ver «Próximos pasos»). El motor de pruebas (`fake`, imágenes de
color liso) sigue siendo el de por defecto hasta que `instalar.sh` elige el real.

| Fase | Qué trae |
|---|---|
| F0 Esqueleto | Esquemas de configuración, pedido y perfil de máquina; textos es/en; README; tests |
| F1 Núcleo | Proyectos, pedidos, intentos, elegida, entrega, cola persistente y CLI `gimg` básica |
| F2 Motor real | Envoltorio de `sd-cli` con el perfil de máquina, `instalar.sh`, catálogo de modelos, composición, medida de marca y `gimg doctor` (0.3.0) |
| F3 API y arranque | API HTTP local (`gimg serve`), arranque bajo demanda y `gimg ui` (0.3.0) |
| F4 Interfaz | Tres pantallas en el navegador, es/en, con plantillas elegibles y editor de elementos (0.4.0) |
| F5 Piloto WMF | Configuración de ejemplo, guía de integración y medidas |
| F6 Director local | Opcional: un LLM local (Ollama) redacta prompts y ayuda a elegir |
| F7 Compatibilidad | Última fase: cualquier equipo, no solo Vulkan (CPU, CUDA, ROCm, Metal), otros Linux, Windows y quizá macOS |

Detalle, decisiones D1-D65 y criterios de cierre en [`docs/plan.md`](docs/plan.md).

### Próximos pasos

Pedido de la persona del 2026-11-05, sin fase asignada aún (nueva F4e o dentro de otra); el diseño está en
[`docs/plan.md`](docs/plan.md), «Piezas, edición y borrado»:

1. Composición por capas con piezas ya existentes (fondo, logo, elementos sueltos y texto), de intentos elegidos o de
   archivos propios (PNG o SVG).
2. Transparencia opcional al generar y «Quitar fondo» sobre una pieza, sin instalar nada (por investigar).
3. Imágenes de referencia al generar una pieza (por comprobar qué acepta `sd-cli`).
4. Cajas de texto colocadas antes de generar, que el generador tiene en cuenta (prompt, imagen inicial, chip de
   contraste).
5. Borrar intentos, composiciones, plantillas y elementos, con confirmación.
6. Edición por prompt: un intento nuevo a partir de otro, sin tocar el original.
7. Editar el texto y la tipografía de los elementos de un resultado compuesto.

## Cómo se conecta un proyecto

Cada proyecto lleva en su repo un archivo `galivelop-images.json` (D12):

```json
{
  "$schema": "https://raw.githubusercontent.com/Zeldris/galivelop-image-generator/main/gimg/schemas/project-config.schema.json",
  "minVersion": "0.1.0",
  "name": "example-world",
  "delivery": { "dir": "uploads/images", "template": "{key}-{profile}.png" },
  "profiles": {
    "banner": { "width": 1280, "height": 512, "steps": 6, "cfg": 1.0, "sampler": "euler", "model": "flux2-klein-4b-q8" }
  }
}
```

- `$schema`: esquema contra el que se valida el archivo.
- `minVersion`: versión mínima del generador que entiende esta configuración (D24).
- `name`: nombre del proyecto.
- `delivery.dir`: carpeta de entrega, relativa al repo del proyecto.
- `delivery.template`: nombre del archivo entregado; `{key}` es la clave del pedido y `{profile}` el perfil.
- `profiles`: perfiles de generación con nombre (tamaño, pasos, `cfg`, muestreador y modelo).

Un pedido pide una imagen con una clave y un perfil:

```json
{"key": "fauna/red-howler", "profile": "banner", "prompt": "...", "references": ["refs/wolf.png"], "seed": 42}
```

- `key`: identifica la imagen dentro del proyecto; puede llevar subcarpetas.
- `profile`: perfil de la configuración del proyecto que se aplica.
- `prompt`: descripción de la imagen.
- `references`: imágenes de referencia (el perfil de máquina limita cuántas).
- `seed`: semilla, para repetir un resultado.

La elegida se entrega en `uploads/images/fauna/red-howler-banner.png` (D21).

Esquemas:
[configuración del proyecto](gimg/schemas/project-config.schema.json),
[pedido](gimg/schemas/order.schema.json) y
[perfil de máquina](gimg/schemas/machine-profile.schema.json).
El preajuste de la Steam Deck está en [`gimg/machine_profiles/steam-deck.json`](gimg/machine_profiles/steam-deck.json)
(D15).

## Uso (CLI)

Se lanza con `python3 -m gimg …` desde la carpeta del repo (Python 3.10+, sin instalar nada), o con `gimg` tras
`./instalar.sh`. Con `GIMG_ENGINE=fake` las imágenes son de prueba (`sdcpp` es el motor real). `--lang es|en` elige el
idioma y `--json` da la salida en JSON para integrarlo desde otro programa (la forma está en `docs/plan.md`).

```sh
python3 -m gimg project add ~/mi-proyecto            # registra la carpeta con galivelop-images.json
python3 -m gimg order submit mi-proyecto pedido.json  # crea el pedido y encola `count` intentos ("-" lee de stdin)
python3 -m gimg work                                  # procesa la cola (--once: una sola entrada)
python3 -m gimg order show mi-proyecto fauna/red-howler banner
python3 -m gimg attempt mark mi-proyecto fauna/red-howler banner 1 candidate   # new | candidate | discarded
python3 -m gimg attempt note mi-proyecto fauna/red-howler banner 1 "buenas alas"
python3 -m gimg choose mi-proyecto fauna/red-howler banner 1   # entrega el PNG y el manifiesto al proyecto
python3 -m gimg undo mi-proyecto fauna/red-howler banner       # vuelve a la elegida anterior (o a ninguna)
python3 -m gimg attempt new mi-proyecto fauna/red-howler banner --count 2 --steps 8   # más intentos
python3 -m gimg order list mi-proyecto --unchosen
python3 -m gimg queue list                            # estado de la cola, con los errores
python3 -m gimg queue cancel 3
python3 -m gimg compose mi-proyecto fauna/red-howler banner 1 --template cartel   # recompone sin generar
python3 -m gimg templates mi-proyecto banner          # plantillas de composición del perfil
python3 -m gimg measure imagen.png --project mi-proyecto   # paleta, contraste y distancia a la marca
python3 -m gimg sheet --out hoja.png a.png b.png      # hoja de contactos para revisar una ronda
python3 -m gimg doctor                                # comprueba el motor, los modelos y las herramientas (--verify)
python3 -m gimg serve                                 # servicio local en 127.0.0.1:8737 (--detach, --status, --stop, --port, --idle-min)
python3 -m gimg ui                                    # abre la interfaz en el navegador (arranca el servicio si hace falta; --no-browser)
./arrancar.sh                                         # lo mismo, con doble clic o desde el sandbox de VS Code (fija GIMG_CONFIG_HOME y GIMG_DATA_HOME)
python3 -m gimg project list | project remove mi-proyecto | version
```

Los datos van a `$GIMG_DATA_HOME` (por defecto `~/.local/share/gimg`) y el registro de proyectos a
`$GIMG_CONFIG_HOME` (`~/.config/gimg`). Los errores salen por stderr con código 1 (`GIMG_DEBUG=1` añade el traceback).

## Servicio

`gimg serve` levanta una API HTTP local en `127.0.0.1:8737` (la misma capa que la CLI) y la interfaz de `gimg/ui`;
`gimg ui` la arranca si hace falta y abre el navegador. Solo escucha en local y exige `Content-Type: application/json`
al escribir. `GIMG_PORT` cambia el puerto y `GIMG_AUTOSTART=0` apaga el arranque bajo demanda. Rutas, cuerpos, errores y
ejemplos `curl` en [`docs/api.md`](docs/api.md).

## Instalación

`git clone` de este repo y `./instalar.sh` (D24):

1. `gimg` queda en `~/.local/bin`.
2. El motor (release fija de stable-diffusion.cpp con Vulkan) y los modelos por defecto del catálogo (~7 GB) se
   descargan fuera del repo, en una carpeta del usuario compartida (D5), con comprobación de sha256.
3. `gimg doctor` dice si falta algo y cómo arreglarlo. Opciones de `instalar.sh`: `--with <id>`, `--only-cli`,
   `--models-from <carpeta>` y `--dry-run`.

Solo Linux con Vulkan (la Steam Deck es la máquina de referencia); otros equipos llegan en F7. Las comprobaciones
manuales en la Deck que faltan están en [`docs/plan.md`](docs/plan.md).

## Desarrollo

```sh
python3 -m unittest discover -s tests -t .
```

El flujo de trabajo del repo (relevos, ramas, revisión) está en [`AGENTS.md`](AGENTS.md); el vocabulario, en
[`GLOSSARY.md`](GLOSSARY.md). El código es [MIT](LICENSE); los modelos de
[`gimg/models.json`](gimg/models.json) tienen cada uno su propia licencia.
