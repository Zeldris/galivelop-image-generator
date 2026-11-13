# galivelop-image-generator local API

[Español](../api.md)

HTTP API of the local service (`gimg serve`), API version **1** (`GET /api/health` → `"api": 1`). It is the same layer
as the CLI: each route calls the function that `gimg/cli.py` already calls, so the responses match those of
`--json`. Reference text; the design and decisions are in `docs/plan.md` (D17, D25, "F3 en detalle"; the plan is in
Spanish, see [`../plan.md`](../plan.md)).

The doc is checked by `tests/test_api_doc.py`: every route registered in `gimg/server.py` has its section here.

## Startup

| Command | What it does |
|---|---|
| `gimg serve` | Service in the foreground on `127.0.0.1:8737` (Ctrl-C stops it). `--port N`, `--idle-min N` |
| `gimg serve --detach` | Starts it in the background, waits for `health` up to 5 s and prints the URL (`--json`: the state) |
| `gimg serve --status` / `--stop` | Says whether it is running / stops it (SIGTERM; does not cut a generation in progress) |
| `gimg ui [--no-browser]` | Starts the service if needed and opens the interface in the browser; always prints the URL |

- **Port:** `--port`, else `GIMG_PORT`, else `"serve": {"port"}` in `<config>/config.json`, else **8737**. If it is
  taken, error `serve.port_busy` (no other port is tried). It always listens on `127.0.0.1` only.
- **One instance:** `<data>/serve.lock`; the state lives in `<data>/serve.json` (`pid`, `port`, `url`, `version`,
  `build`, `startedAt`) and the log in `<data>/serve.log`.
- **On-demand start:** `gimg ui`, `gimg order submit` and `gimg attempt new` start the service if it is not running.
  `GIMG_AUTOSTART=0` (also `false`, `no`, `off`, case-insensitive) turns it off.
- **Inactivity:** it stops by itself after 15 min with no requests, no worker and no `queued`/`running` entries
  (`--idle-min`, `"serve": {"idleMinutes"}`; `0` = never).
- **Worker:** the service does not generate: it launches `gimg work` as a separate process, unless the queue is paused, when there are entries in the
  queue.

The examples use `B=http://127.0.0.1:8737`.

## Conventions

- **Prefix** `/api`. `{p}` is the project, `{profile}` the profile, `{key}` the order key in **a single segment**:
  the `/` of `fauna/lobo` is encoded `%2F` (`fauna%2Flobo`). `{id}` is the attempt number.
- **Bodies** are JSON, an object in every route that writes (`{}` is valid). An unexpected field gives `api.bad_param`.
- **Responses** are JSON except images (`image/png`), the log (`text/plain`) and SVGs (`image/svg+xml`). Those under
  `/api` carry `Cache-Control: no-store`; attempt images carry `private, no-cache` with `ETag` and `304` on
  `If-None-Match`.
- **Project paths** never come out as absolute paths: images are requested by attempt id, and `deliveredTo` is relative
  to the project root.

## Security

Before touching anything, on every request and in this order:

1. **Host:** `127.0.0.1:<port>` or `localhost:<port>`; otherwise 403 `api.bad_host` (stops *DNS rebinding*).
2. **Origin:** if present, `http://127.0.0.1:<port>` or `http://localhost:<port>`; otherwise 403 `api.bad_origin`.
   Without `Origin` it is accepted (CLI, `curl`, other programs). `Sec-Fetch-Site`, if present, must be `same-origin` or
   `none`.
3. **Methods:** only `GET`, `POST` and `PUT`; the rest (`OPTIONS` too) give 405 `api.method_not_allowed`.
4. **Content-Type:** `POST` and `PUT` require `Content-Type: application/json` (415 `api.content_type`),
   `Content-Length` (411 `api.length_required`) of up to 1 MiB (413 `api.body_too_large`) and a JSON object (400
   `api.bad_json`). That is why a form on another website cannot write.
5. **No CORS:** no `Access-Control-*` header is sent; another origin cannot read the responses.

A segment with `..`, `\`, NUL or empty gives 404 without reaching the disk. All responses carry `X-Content-Type-Options:
nosniff`, `Referrer-Policy: no-referrer` and `Cross-Origin-Resource-Policy: same-origin`. There is no access token.

## Errors and language

Every error response is:

```json
{"error": {"code": "order.unknown", "params": {"key": "x", "profile": "banner"}, "message": "…", "errors": ["…"]}}
```

`code` and `params` are those of the `GimgError`; `message` is in the language of the request; `errors` (optional) are
the schema lines when the order does not validate. Language: `?lang=es|en`, else the first supported one in
`Accept-Language`, else the system's. Statuses: 400 malformed request or invalid value (`api.bad_json`,
`api.bad_param`, `*.invalid`, `limit.*`, `path.*`, `key.*`); 403 Host or Origin; 404 `project.unknown`,
`order.unknown`, `order.profile_unknown`, `order.attempt_unknown`, `queue.unknown`, `api.not_found`; 405, 411, 413, 415
as above; 409 state that does not allow it (`compose.template_exists`, `order.choose_*`, `order.undo_*`,
`order.history_empty`, `queue.not_cancellable`, `queue.not_movable`, `compose.busy`, `measure.busy`,
`api.heavy_busy`, `delivery.target_taken`); 500 server-side failures (`api.unexpected` carries `"message":
"Type: text"`). The texts of all codes: `GET /api/locales/{lang}`.

## Routes

### GET /api/health

Service status. Response: `{"ok": true, "api": 1, "version", "build", "pid", "port", "engine", "worker": bool, "paused": bool}`. `paused` is `true` while the queue is paused (`gimg queue pause`).
`build` is a fingerprint of the code the service is running, taken from the paths and contents of the `.py` and `.json`
files of `gimg`, excluding `gimg/ui/` (the interface is read from disk on every request). Two copies of the same code
give the same fingerprint. With the same version and different code (after a `git pull`), `gimg ui` (`arrancar.sh`)
stops the old service and starts a new one, unless a worker is alive.

```sh
curl -s $B/api/health
```

### GET /api/locales/{lang}

The texts (errors and interface) of `es` or `en`, as they are in `gimg/locales/<lang>.json`. Error: `api.not_found`.

```sh
curl -s $B/api/locales/es
```

### GET /api/projects

Registered projects. Response: `[{"name", "root", "ok", "profiles": [name], "orders": n, "delivered": n,
"error"?}]`; `delivered` counts the orders with a chosen attempt. A project whose configuration does not load comes out
with `"ok": false`, `error` and the counters at zero: it does not break the list.

```sh
curl -s $B/api/projects
```

### GET /api/projects/{p}

`{"name", "root", "config"}` (profiles, `compose`, `brand`). Errors: `project.*`.

```sh
curl -s $B/api/projects/mi-proyecto
```

### GET /api/projects/{p}/orders

The project's orders, like `order list --json`. Query: `profile=<profile>`, `chosen=true|false`. Errors:
`order.profile_unknown`, `api.bad_param`.

```sh
curl -s "$B/api/projects/mi-proyecto/orders?profile=banner&chosen=false"
```

### POST /api/projects/{p}/orders

Creates an order (the JSON of `order.schema.json`, with its `count`) and enqueues the attempts; `"draft": true` requests
them as drafts. `"template"` (optional, not saved in the order): id of the composition template for the attempts
(`gimg order submit --template`); it is validated before saving and before enqueuing anything. `"model"` (optional,
also not saved in the order): model for the attempts (`gimg order submit --model`); if it is not in the catalog,
`model.unknown` and nothing is saved; a value that is not text, `api.bad_param`. Each queue entry carries `position`
(the worker serves the queue from lowest to highest; `POST /api/queue/{id}/move` changes it). Response 201: `{"order",
"entries", "estimateMs"}`. Errors: `order.invalid` (with `errors`), `limit.*`, `key.*`, `order.profile_unknown`,
`compose.template_unknown` (400).

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/orders \
  -d '{"key":"fauna/lobo","profile":"banner","prompt":"un lobo en la nieve","count":2}'
```

### GET /api/projects/{p}/orders/{profile}/{key}

The order with its attempts, like `order show --json`, plus `deliveredTo`: path of the delivered file relative to the
project root, or `null` if there is no chosen attempt. Error: `order.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo
```

### PUT /api/projects/{p}/orders/{profile}/{key}/text

Replaces the order's texts. Body: `{"text": {"title": "…"}}` (`{}` clears them). Response: the order. Errors:
`order.text_unknown_field`, `order.invalid`, `api.bad_param`.

```sh
curl -s -X PUT -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/text \
  -d '{"text":{"title":"El lobo"}}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts

More attempts (another seed, a prompt tweak, several in a row, draft). Body, all optional: `{"count", "seed",
"prompt", "steps", "cfg", "sampler", "draft", "template", "model"}` (`template`: id of a template from
`GET …/profiles/{profile}/templates`, the one for the new attempts; without it, `default`; `model`: id from
`GET /api/models` that replaces the profile's in these attempts, like `gimg attempt new --model`). Response 202:
`{"entries", "estimateMs"}`; each entry carries its `template`. Errors: `order.count_invalid`,
`order.prompt_too_long`, `limit.*`, `order.unknown`, `compose.template_unknown` (400, before enqueuing anything),
`model.unknown` (400), `limit.steps` if the model does not fit the machine profile.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts -d '{"count":2,"seed":7}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/mark

Marks an attempt. Body: `{"state": "new|candidate|discarded"}`. Response: the attempt. Errors:
`order.state_invalid`, `order.discard_chosen` (409), `order.attempt_unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/mark -d '{"state":"candidate"}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/note

The attempt's note. Body: `{"text": "…"}`. Response: the attempt. Error: `order.note_invalid`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/note -d '{"text":"buenas alas"}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/choose

Chooses an attempt and delivers its PNG and the manifest to the project. Body: `{"attempt": <id>}` (integer). Response:
`{"old", "new", "deliveredTo"}`; `deliveredTo` is relative to the project root. Errors: `order.choose_*` (409),
`delivery.*`, `order.attempt_unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/choose -d '{"attempt":1}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/undo

Goes back to the previous chosen attempt (or to none, and then withdraws what was delivered). Body: `{}`. Response:
`{"old", "new", "deliveredTo"}` (`null` if there is no chosen attempt any more). Errors: `order.history_empty`,
`order.undo_*` (409).

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/undo -d '{}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/compose

Recomposes the text and the logo over the attempt (needs ffmpeg and rsvg-convert). Optional body: `{"text": {"campo":
"valor"}, "template": "id", "layout": {"title": {"x", "y", "w", "h"}}}`. With `template` it composes with that template
and the attempt keeps it (`compose.templateId`); without it, with the one it already had (else `default`). `layout`
moves the template's elements (`id="gimg-<name>"` with `data-gimg-box`), in whole pixels of the target, and the attempt
keeps it (`compose.layout`, only what was moved); `{}` goes back to the template, and without `layout` the attempt's own
is kept unless the template changes (then it is emptied). `compose.contrast` stores the contrast of each text over the
base image. Response: the attempt (with `delivered` if it is the chosen one). Only one heavy task at a time: the second
waits up to 60 s and gives 409 `api.heavy_busy`. Errors: `compose.busy` (409), `compose.template_unknown` (400; a stored
`templateId` that no longer exists also fails, without switching to another), `compose.element_unknown`,
`compose.bad_layout`, `compose.bad_element` (400, before changing anything if the `layout` comes in the request),
`compose.*`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/attempts/1/compose -d '{"text":{"title":"El lobo"}}'
```

### GET /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/image

The attempt's PNG; `?raw=1` gives the raw image (without composition). With `ETag`: `If-None-Match` returns 304. Error:
`api.not_found`.

```sh
curl -s -o intento.png "$B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/image?raw=1"
```

### GET /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/log

`text/plain` of the attempt's log. Error: `api.not_found`.

```sh
curl -s $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/log
```

### GET /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/measure

Measures the attempt's image like `gimg measure --json`, with the `brand` palette. Query: `raw=1` (the raw one, as is)
or `base=1` (the base image: the raw one taken to the target size, without the layer; with `zone` in pixels of the
target, which is taken to the raw one with `compose.zone_to_raw`, and the response repeats that `zone`), and together
`zone=x,y,w,h` and `text=%23RRGGBB`. `raw=1` and `base=1` do not go together (`api.bad_param`). One heavy task at a time
(409 `api.heavy_busy`). Errors: `measure.*`, `api.bad_param`.

```sh
curl -s "$B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/attempts/1/measure?zone=40,40,600,120&text=%23FFFFFF"
```

### GET /api/projects/{p}/profiles/{profile}/templates

The profile's composition templates: `[{"id", "template", "logo", "fields", "zone"?, "textColor"?, "source",
"default"}]`, `default` first and the rest by id (`logo` and `zone`/`textColor` inherited as `compose.effective` says).
`source` says where it comes from: `config` (`compose.templates`), `project` (`<compose.templatesDir>/<profile>/`) or
`local` (`<data>/projects/<p>/templates/<profile>/`); an id repeated across sources takes the first one's. A profile
without `compose` gives `[]`. Each entry also carries `"elements"`: what `compose.elements` reads in its SVG
(`[{"id", "kind": "text|logo|ornament", "box": {x, y, w, h}, "color"?}]`), `[]` if the `viewBox` is not the target's, if
there are no elements or if the SVG cannot be read (the rest of the list comes out the same). It is the same list as
`gimg templates --json`. Whether the profile allows saving into the project is stated by `compose.templatesDir` in the
configuration (`GET /api/projects/{p}`). Error: `order.profile_unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/profiles/og/templates
```

### POST /api/projects/{p}/profiles/{profile}/templates

Saves as a new template the one from an attempt with its `layout` applied and the gaps left unfilled. Body: `{"from":
{"key": "<order>", "attempt": <id>}, "name": "<new id>", "dest": "local|project"}` (`dest` defaults to `local`).
`local` writes `<data>/projects/<p>/templates/<profile>/<name>.svg`; `project`,
`<compose.templatesDir>/<profile>/<name>.svg` inside the project. Next to it goes `<name>.json` with `base` (the source
template) and what is inherited (`logo`, `fields`, `zone`, `textColor`). Response 201: the new entry of the template
list. It never overwrites. Errors: `compose.template_exists` (409, the name already exists in any source),
`compose.templates_dir_missing` (400, `project` without `templatesDir`), `compose.bad_name`, `compose.bad_dest`,
`compose.element_unknown`, `compose.template_unknown` (400), `order.unknown`, `order.attempt_unknown`,
`order.profile_unknown` (404), `api.bad_param`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/profiles/og/templates \
  -d '{"from":{"key":"fauna/lobo","attempt":1},"name":"lobo-izquierda","dest":"local"}'
```

### GET /api/projects/{p}/profiles/{profile}/assets/{kind}

The SVG declared in the profile's `compose`; `{kind}` is `template` or `logo`. With `?id=<template>`, that template's
(without `id`, the `default` one). It is served with a CSP that prevents running script. Errors:
`compose.template_missing`, `compose.logo_missing`, `compose.template_unknown` (400), `api.not_found`.

```sh
curl -s "$B/api/projects/mi-proyecto/profiles/og/assets/template?id=claro"
```

### GET /api/queue

The queue: each entry with `progress`, `errorText` and `estimateMs` where applicable (without the preview path). Query:
`state=queued|running|done|failed|cancelled`. Error: `queue.bad_state`.

```sh
curl -s "$B/api/queue?state=running"
```

### GET /api/queue/{id}/preview

PNG of the preview while the entry runs (`Cache-Control: no-store`). Error: `api.not_found`.

```sh
curl -s -o preview.png $B/api/queue/3/preview
```

### POST /api/queue/{id}/cancel

Cancels an entry. Body: `{}`. Response: the entry. Errors: `queue.unknown`, `queue.not_cancellable` (409).

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/3/cancel -d '{}'
```

### POST /api/queue/{id}/move

Moves a waiting (`queued`) entry in the line the worker takes from. Body: `{"to": "up|down|top"}` (`up`/`down` one
place; `top` the first). Response: the entry. Errors: `queue.unknown`, `queue.not_movable` (409, it is not `queued`),
`queue.bad_move` (400). CLI: `gimg queue move <id> up|down|top`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/5/move -d '{"to":"top"}'
```

### POST /api/queue/clear

Cancels all `queued` entries (only those of `project`, if given); it never touches a `running` one. Body:
`{"project"?}`. Response: the list of cancelled entries. CLI: `gimg queue clear [--project P]`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/clear -d '{"project":"mi-proyecto"}'
```

### POST /api/queue/pause

Pause and resume the queue (body `{}`, with `Content-Type: application/json`). While paused the worker finishes the image in progress and takes no
other, and the service launches no worker; on resume it relaunches one at its next beat (a few seconds). Response:
`{"paused": bool, "changed": bool}` (`changed` is `false` if it was already so). The state is read in `paused` of
`GET /api/health`. While paused, what waits in the queue does not keep the service alive: it stops when idle as with
an empty queue, and `gimg queue resume` starts it again if anything is still queued. CLI: `gimg queue pause` and
`gimg queue resume`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/pause -d '{}'
```

### POST /api/queue/resume

Removes the pause (body `{}`); response `{"paused": false, "changed": bool}`. See `POST /api/queue/pause`. CLI: `gimg queue resume`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/resume -d '{}'
```

### GET /api/models

The model catalog (`gimg/models.json`) against the machine profile: `[{"id", "license", "defaults": {"steps",
"cfg", "sampler"}, "installDefault", "allowed", "reason"?}]`. If `allowed` is `false`, `reason` is the `{"code",
"message"}` of the `limit.*` that prevents it (today `limit.steps`: the model's default steps exceed `maxSteps`).

```sh
curl -s $B/api/models
```

### GET /api/projects/{p}/check

The `gimg doctor` checks that concern the project (sources of `compose.fonts`, template and logo files, editable
elements and `viewBox`): `[{"id", "status": "ok|warn|fail", "message", "fix"?}]`. Error: `project.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/check
```

### GET /api/projects/{p}/brand

The project's brand drafts: `[{"slug", "files": [keys present], "modified"}]`. Each brand's workshop is
`<data>/projects/<p>/brand/<slug>/` (slug = the name without accents, lowercase and with hyphens); the keys are those of
the system files: `emblema-alpha.png`, `emblema.svg`, `emblema-mono.svg`, `wordmark.svg`, `lockup-h.svg`, `lockup-v.svg`,
`contactos.png`. Each step overwrites its own copy in the workshop and never touches the source attempt. Error:
`project.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/brand
```

### POST /api/projects/{p}/brand/matte

Removes the flat background of one of the project's attempts. Fields: `name` (the brand name), `source`
(`{"profile", "key", "attempt"}`, resolved like `attempt_image`), `tol` (60), `soft` (110), `border` (6), `grow` (3, 0 to 32),
`holes` (false: with `true`, background-coloured regions not connected to the edge are emptied too, such as an enclosed
ring). Writes `emblema-alpha.png` and returns what `gimg brand matte` returns. Errors: `api.bad_param`,
`brand.bad_name`, `brand.empty_text`, `brand.no_matte`, `order.attempt_unknown` (404), `api.not_found` (404),
`project.unknown`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/matte -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "source": {"profile": "og", "key": "fauna/lobo", "attempt": 1}}'
```

### POST /api/projects/{p}/brand/trace

Turns the cut-out emblem into SVG. Fields: `name`, `mode` (`color` or `mono`), `colors` (`color` only, 1 to 64), `usePalette`
(`color` only; takes the project's `brand.palette` and excludes `colors`), `dp_tol` (1.2), `min_island` (12). Writes
`emblema.svg` or `emblema-mono.svg`. Errors: `brand.missing_piece` (409, the cut-out is missing), `brand.no_palette`,
`brand.bad_option`, `api.bad_param`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/trace -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "mode": "color", "usePalette": true}'
```

### POST /api/projects/{p}/brand/wordmark

Draws the name as outlines. Fields: `name`, `font` (an installed family, e.g. `Cinzel`; resolved with `fc-match`, never
a path), `text` (defaults to the name in capitals), `weight` (800), `spacing` (0.01). Writes `wordmark.svg`. Errors:
`brand.font_unknown`, `brand.font_unreadable`, `brand.tool_missing` (500), `brand.wordmark_no_fit`,
`brand.text_too_long`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/wordmark -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "font": "Cinzel", "weight": 700}'
```

### POST /api/projects/{p}/brand/lockup

Joins the workshop's emblem and wordmark. Fields: `name`, `layout` (`h` or `v`), `cap` (0.45), `gap` (0.25), `width`
(1.6). Writes `lockup-h.svg` or `lockup-v.svg`. Errors: `brand.missing_piece` (409, `emblema.svg` or `wordmark.svg` is
missing), `brand.bad_option`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/lockup -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "layout": "h"}'
```

### POST /api/projects/{p}/brand/save

Contact sheet and the whole system (7 files prefixed with the slug). Fields: `name`, `dest` (`data`: the
`brand-out/<slug>/` folder in the project's data; `project`: the `brand.dir` folder of its configuration, inside the
root, like `compose.templatesDir`), `force` (false). Returns `{name, slug, dest, out_dir, files, contact_size,
overwritten}`. Errors: `brand.missing_piece` (409), `brand.exists` (409, without `force`), `brand.dir_missing` (400,
`dest: project` without `brand.dir`), `path.outside` (400, a `brand.dir` that leaves the root through a link),
`brand.bad_option`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/save -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "dest": "project", "force": true}'
```

### GET /api/projects/{p}/brand/files/{name}/{file}

A workshop file: `name` is the slug and `file` one of the keys above (`emblema.svg`, not the prefixed name); any other
name gives `api.not_found` (404). SVGs carry `Content-Security-Policy: sandbox` and `nosniff`; caching is `no-cache` with
an ETag. A malformed slug gives `brand.bad_name`.

```sh
curl -s $B/api/projects/mi-proyecto/brand/files/mi-marca/emblema.svg
```

## Interface

`GET /` serves `gimg/ui/index.html` and `GET /ui/<path>` the files of `gimg/ui/` (extensions `.html .css .js .svg
.png .woff2 .ttf .json`), with a CSP without inline JS or external resources.
