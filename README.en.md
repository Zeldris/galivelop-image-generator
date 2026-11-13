# Galivelop IG

[Español](README.md)

**Galivelop IG** (short name **GVIG**) is the product name; the repository, the package and the command are still `galivelop-image-generator` and `gimg` (D38).

A local AI image generator: one service per machine, shared by several projects (D1, D2). It uses stable-diffusion.cpp
as the engine and the Steam Deck as the reference machine (D4). No dependencies: Python 3 standard library only (D6).

## Status

Version **0.4.1**, phases **F0-F4 done** and on `main`: projects, orders, attempts, chosen candidate and delivery,
persistent queue, CLI, real engine (`sd-cli`, with `instalar.sh`), composition and brand measurement, local HTTP API
and browser interface. Still pending: manual checks on the Deck (pilot rounds, a full walk through the interface in
the browser), the pilot with real projects (F5) and what follows (see "Next steps"). The test engine (`fake`,
flat-colour images) stays the default until `instalar.sh` selects the real one.

| Phase | What it brings |
|---|---|
| F0 Skeleton | Schemas for project config, order and machine profile; es/en texts; README; tests |
| F1 Core | Projects, orders, attempts, chosen candidate, delivery, persistent queue and a basic `gimg` CLI |
| F2 Real engine | `sd-cli` wrapper driven by the machine profile, `instalar.sh`, model catalog, composition, brand measurement and `gimg doctor` (0.3.0) |
| F3 API and startup | Local HTTP API (`gimg serve`), on-demand startup and `gimg ui` (0.3.0) |
| F4 UI | Three browser screens, es/en, with selectable templates and an element editor (0.4.0) |
| F5 WMF pilot | Example config, integration guide and measurements |
| F6 Local director | Optional: a local LLM (Ollama) drafts prompts and helps choose |
| F7 Compatibility | Last phase: any machine, not only Vulkan (CPU, CUDA, ROCm, Metal), other Linux distros, Windows and maybe macOS |

Details, decisions D1-D65 and exit criteria in [`docs/plan.md`](docs/plan.md) (in Spanish).

### Next steps

Roadmap by version (details in [`docs/plan.md`](docs/plan.md), "Hoja de ruta por versiones hasta la 1.0.0"); fixes to
what is published ship first, as a patch:

| Version | What |
|---|---|
| 0.5.0 | Delete attempts, compositions, templates and elements; edit the text and typography of a composed result; rename an order; interface improvements |
| 0.6.0 | **Montage**: a format is built in layers from the project's pieces and the user's own files (blocks and absolutes, as in CSS), and the engine "fits" it with img2img |
| 0.7.0 | Text boxes placed before generating (a phrase in the prompt and the contrast chip) |
| 0.8.0 | Delete orders, and everything from the interface |
| 0.9.0 | F5: WMF pilot, LoRA, transparency and "Remove background", reference images, prompt editing |
| later | Editable pieces and brand, team panel, F6, F7 and, last, gamepad and touch, up to 1.0.0 |

## How a project connects

Each project keeps a `galivelop-images.json` file in its repo (D12):

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

- `$schema`: schema the file is validated against.
- `minVersion`: minimum generator version that understands this config (D24).
- `name`: project name.
- `delivery.dir`: delivery dir, relative to the project repo.
- `delivery.template`: name of the delivered file; `{key}` is the order key and `{profile}` the profile.
- `profiles`: named generation profiles (size, steps, `cfg`, sampler and model).

An order asks for one image by key and profile:

```json
{"key": "fauna/red-howler", "profile": "banner", "prompt": "...", "references": ["refs/wolf.png"], "seed": 42}
```

- `key`: identifies the image inside the project; it may include subfolders.
- `profile`: profile from the project config to apply.
- `prompt`: description of the image.
- `references`: reference images (the machine profile limits how many).
- `seed`: seed, to reproduce a result.

The chosen candidate is delivered to `uploads/images/fauna/red-howler-banner.png` (D21).

Schemas:
[project config](gimg/schemas/project-config.schema.json),
[order](gimg/schemas/order.schema.json) and
[machine profile](gimg/schemas/machine-profile.schema.json).
The Steam Deck preset is [`gimg/machine_profiles/steam-deck.json`](gimg/machine_profiles/steam-deck.json) (D15).

## Usage (CLI)

Run it as `python3 -m gimg …` from the repo folder (Python 3.10+, nothing to install), or as `gimg` after
`./instalar.sh`. With `GIMG_ENGINE=fake` the images are test images (`sdcpp` is the real engine). `--lang es|en` picks the
language and `--json` gives JSON output for integrating from another program (its shape is in `docs/plan.md`).

```sh
python3 -m gimg project add ~/my-project             # registers the folder holding galivelop-images.json
python3 -m gimg order submit my-project order.json    # creates the order and queues `count` attempts ("-" reads stdin)
python3 -m gimg work                                  # processes the queue (--once: a single entry)
python3 -m gimg order show my-project fauna/red-howler banner
python3 -m gimg attempt mark my-project fauna/red-howler banner 1 candidate   # new | candidate | discarded
python3 -m gimg attempt note my-project fauna/red-howler banner 1 "nice wings"
python3 -m gimg choose my-project fauna/red-howler banner 1   # delivers the PNG and the manifest to the project
python3 -m gimg undo my-project fauna/red-howler banner       # back to the previous chosen (or none)
python3 -m gimg attempt new my-project fauna/red-howler banner --count 2 --steps 8   # more attempts
python3 -m gimg order list my-project --unchosen
python3 -m gimg queue list                            # queue state, with errors
python3 -m gimg queue cancel 3
python3 -m gimg compose my-project fauna/red-howler banner 1 --template poster   # recompose without generating
python3 -m gimg templates my-project banner           # the profile's composition templates
python3 -m gimg measure image.png --project my-project   # palette, contrast and distance to the brand
python3 -m gimg measure image.png --family "wood=#1b130c,#332415" --family "gold=#b8862b,#f2c45a"   # % of pixels per colour family (+ other)
python3 -m gimg sheet --out sheet.png a.png b.png     # contact sheet to review a round
python3 -m gimg export a.png a.webp --size 960x540   # copy to WebP, ICO or BMP (the delivery stays PNG)
python3 -m gimg export a.png b.png --crop 64,0,768,1152 --size 600x900   # declared crop (X,Y,W,H of the original), then scale down
python3 -m gimg export a.png b.png --size 1536x384 --anchor top   # where the proportion crop sits: top|bottom|left|right (or top-left…), centre by default
python3 -m gimg brand matte logo.png                  # removes the flat background: logo-alpha.png (the original is untouched)
python3 -m gimg brand trace logo-alpha.png --mode color|mono|silhouette   # PNG to SVG (--palette, --colors, --matte)
python3 -m gimg brand wordmark TARKOR --font Cinzel.ttf -o wordmark.svg   # the name as paths, no <text> (--weight, --spacing)
python3 -m gimg brand lockup emblema.svg wordmark.svg --layout h|v   # emblem and wordmark in one SVG (--cap, --gap, --width, --margin, --color, -o)
python3 -m gimg brand square ig.svg --fill '#7C5CD6' --ink '#fbfcfd' --png 512,128,32   # the symbol: square with a 28/128 chamfer and the drawing in one ink (--chamfer, --pad, -o, --force)
python3 -m gimg brand system emblema.png --name Tarkor --font Cinzel.ttf --out-dir marca/   # the seven files of the logo system (--weight, --spacing, --palette, --colors, --text, --cap, --gap, --width, --margin, --mono for a one-ink lockup, --force overwrites)
python3 -m gimg doctor                                # checks the engine, models and tools (--verify)
python3 -m gimg serve                                 # local service on 127.0.0.1:8737 (--detach, --status, --stop, --port, --idle-min)
python3 -m gimg ui                                    # open the interface in the browser (starts the service if needed; --no-browser)
./arrancar.sh                                         # the same, by double click or from the VS Code sandbox (sets GIMG_CONFIG_HOME and GIMG_DATA_HOME)
python3 -m gimg project list | project remove my-project | version
```

Data goes to `$GIMG_DATA_HOME` (default `~/.local/share/gimg`) and the project registry to `$GIMG_CONFIG_HOME`
(`~/.config/gimg`). Errors go to stderr with exit code 1 (`GIMG_DEBUG=1` adds the traceback).

## Service

`gimg serve` starts a local HTTP API on `127.0.0.1:8737` (the same layer as the CLI) and the UI in `gimg/ui`; `gimg ui`
starts it if needed and opens the browser. It listens on localhost only and requires `Content-Type: application/json`
for writes. `GIMG_PORT` changes the port and `GIMG_AUTOSTART=0` turns off on-demand start. Routes, bodies, errors and
`curl` examples are in [`docs/en/api.md`](docs/en/api.md).

## Installation

`git clone` this repo and run `./instalar.sh` (D24):

1. `gimg` lands in `~/.local/bin`.
2. The engine (a pinned stable-diffusion.cpp release with Vulkan) and the catalog's default models (~7 GB) are
   downloaded outside the repo, into a shared per-user folder (D5), with a sha256 check.
3. `gimg doctor` tells you what is missing and how to fix it. `instalar.sh` options: `--with <id>`, `--only-cli`,
   `--models-from <folder>` and `--dry-run`.

Linux with Vulkan only (the Steam Deck is the reference machine); other machines arrive in F7. The manual checks on the
Deck still pending are in [`docs/plan.md`](docs/plan.md).

## Development

```sh
python3 -m unittest discover -s tests -t .
```

The repo workflow (handoffs, branches, review) is in [`AGENTS.md`](AGENTS.md) (in Spanish); the vocabulary is in
[`GLOSSARY.md`](GLOSSARY.md). The code is [MIT](LICENSE); each model in
[`gimg/models.json`](gimg/models.json) has its own license.
