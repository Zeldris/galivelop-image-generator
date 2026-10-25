# galivelop-image-generator

[Español](README.md)

A local AI image generator: one service per machine, shared by several projects (D1, D2). It uses stable-diffusion.cpp
as the engine and the Steam Deck as the reference machine (D4). No dependencies: Python 3 standard library only (D6).

## Status

Under development, phase **F1 (core) done**: projects, orders, attempts, chosen candidate and delivery, persistent
queue and CLI work end to end with the **test engine** (`fake`, flat-colour images). **It does not generate real
images yet**: the real engine (`sd-cli`) arrives in F2.

| Phase | What it brings |
|---|---|
| F0 Skeleton | Schemas for project config, order and machine profile; es/en texts; README; tests |
| F1 Core | Projects, orders, attempts, chosen candidate, delivery, persistent queue and a basic `gimg` CLI |
| F2 Real engine | `sd-cli` wrapper driven by the machine profile, and `instalar.sh` |
| F3 API and startup | HTTP API, on-demand startup and an optional `systemd --user` unit |
| F4 UI | Three browser screens, es/en |
| F5 WMF pilot | Example config, integration guide and measurements |

Details, decisions D1-D27 and exit criteria in [`docs/plan.md`](docs/plan.md) (in Spanish).

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

Until `instalar.sh` arrives in F2, run it as `python3 -m gimg …` from the repo folder (Python 3.10+, nothing to
install). With `GIMG_ENGINE=fake` (the only engine in F1) the images are test images. `--lang es|en` picks the
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
python3 -m gimg project list | project remove my-project | version
```

Data goes to `$GIMG_DATA_HOME` (default `~/.local/share/gimg`) and the project registry to `$GIMG_CONFIG_HOME`
(`~/.config/gimg`). Errors go to stderr with exit code 1 (`GIMG_DEBUG=1` adds the traceback).

## Installation (planned, **does not exist yet**)

Designed this way (D24), but none of it is available yet:

1. `git clone` this repo and run `./instalar.sh`.
2. `gimg` would land in `~/.local/bin`.
3. The engine and models (~7 GB) are downloaded outside the repo, into a shared per-user folder (D5).

## Development

```sh
python3 -m unittest discover -s tests -t .
```

The repo workflow (handoffs, branches, review) is in [`AGENTS.md`](AGENTS.md) (in Spanish); the vocabulary is in
[`GLOSSARY.md`](GLOSSARY.md). There is no license yet.
