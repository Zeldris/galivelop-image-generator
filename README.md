# galivelop-image-generator

[English](README.en.md)

Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos (D1, D2). Usa
stable-diffusion.cpp como motor y la Steam Deck como máquina de referencia (D4). Sin dependencias: Python 3 solo con
la biblioteca estándar (D6).

## Estado

En desarrollo, fase **F1 (núcleo) hecha**: proyectos, pedidos, intentos, elegida y entrega, cola persistente y CLI
funcionan de extremo a extremo con el **motor de pruebas** (`fake`, imágenes de color liso). **Aún no genera imágenes
reales**: el motor real (`sd-cli`) llega en F2.

| Fase | Qué trae |
|---|---|
| F0 Esqueleto | Esquemas de configuración, pedido y perfil de máquina; textos es/en; README; tests |
| F1 Núcleo | Proyectos, pedidos, intentos, elegida, entrega, cola persistente y CLI `gimg` básica |
| F2 Motor real | Envoltorio de `sd-cli` con el perfil de máquina e `instalar.sh` |
| F3 API y arranque | API HTTP, arranque bajo demanda y unidad `systemd --user` opcional |
| F4 Interfaz | Tres pantallas en el navegador, es/en |
| F5 Piloto WMF | Configuración de ejemplo, guía de integración y medidas |

Detalle, decisiones D1-D27 y criterios de cierre en [`docs/plan.md`](docs/plan.md).

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

Hasta que `instalar.sh` llegue en F2 se lanza con `python3 -m gimg …` desde la carpeta del repo (Python 3.10+, sin
instalar nada). Con `GIMG_ENGINE=fake` (el único motor de F1) las imágenes son de prueba. `--lang es|en` elige el
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
python3 -m gimg project list | project remove mi-proyecto | version
```

Los datos van a `$GIMG_DATA_HOME` (por defecto `~/.local/share/gimg`) y el registro de proyectos a
`$GIMG_CONFIG_HOME` (`~/.config/gimg`). Los errores salen por stderr con código 1 (`GIMG_DEBUG=1` añade el traceback).

## Instalación (prevista, **todavía no existe**)

Pensada así (D24), pero nada de esto está disponible aún:

1. `git clone` de este repo y `./instalar.sh`.
2. `gimg` quedaría en `~/.local/bin`.
3. El motor y los modelos (~7 GB) se descargan fuera del repo, en una carpeta del usuario compartida (D5).

## Desarrollo

```sh
python3 -m unittest discover -s tests -t .
```

El flujo de trabajo del repo (relevos, ramas, revisión) está en [`AGENTS.md`](AGENTS.md); el vocabulario, en
[`GLOSSARY.md`](GLOSSARY.md). Todavía no hay licencia.
