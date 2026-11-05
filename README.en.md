# galivelop-image-generator

[Español](README.md)

A local AI image generator: one service per machine, shared by several projects (D1, D2). It uses stable-diffusion.cpp
as the engine and the Steam Deck as the reference machine (D4). No dependencies: Python 3 standard library only (D6).

## Status

Version **0.4.0**, phases **F0-F4 done** and on `main`: projects, orders, attempts, chosen candidate and delivery,
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

Requested on 2026-11-05, no phase assigned yet (a new F4e or part of another); the design is in
[`docs/plan.md`](docs/plan.md), "Piezas, edición y borrado":

1. Layered composition from existing pieces (background, logo, loose elements and text), from chosen attempts or the
   user's own files (PNG or SVG).
2. Optional transparency when generating, and "Remove background" on a piece, installing nothing (to be researched).
3. Reference images when generating a piece (to check what `sd-cli` accepts).
4. Text boxes placed before generating, which the generator takes into account (prompt, initial image, contrast chip).
5. Delete attempts, compositions, templates and elements, with confirmation.
6. Prompt editing: a new attempt made from another one, leaving the original untouched.
7. Edit the text and typography of the elements of a composed result.

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
python3 -m gimg fonts                                     # installed fonts and the ones the profiles ask for
python3 -m gimg measure image.png --project my-project   # palette, contrast and distance to the brand
python3 -m gimg sheet --out sheet.png a.png b.png     # contact sheet to review a round
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
`curl` examples are in [`docs/api.md`](docs/api.md) (in Spanish).

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
