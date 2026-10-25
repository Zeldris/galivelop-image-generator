# galivelop-image-generator

[English](README.en.md)

Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos (D1, D2). Usa
stable-diffusion.cpp como motor y la Steam Deck como máquina de referencia (D4). Sin dependencias: Python 3 solo con
la biblioteca estándar (D6).

## Estado

En desarrollo, fase **F0 (esqueleto)**: **aún no genera imágenes**. Por ahora solo hay los esquemas JSON y sus tests.

| Fase | Qué trae |
|---|---|
| F0 Esqueleto | Esquemas de configuración, pedido y perfil de máquina; textos es/en; README; tests |
| F1 Núcleo | Proyectos, pedidos, intentos, elegida, entrega, cola persistente y CLI `gimg` básica |
| F2 Motor real | Envoltorio de `sd-cli` con el perfil de máquina e `instalar.sh` |
| F3 API y arranque | API HTTP, arranque bajo demanda y unidad `systemd --user` opcional |
| F4 Interfaz | Tres pantallas en el navegador, es/en |
| F5 Piloto WMF | Configuración de ejemplo, guía de integración y medidas |

Detalle, decisiones D1-D27 y criterios de cierre en [`docs/plan.md`](docs/plan.md).

## Cómo se conecta un proyecto (lo previsto)

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
