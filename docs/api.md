# API local de galivelop-image-generator

API HTTP del servicio local (`gimg serve`), versión de la API **1** (`GET /api/health` → `"api": 1`). Es la misma capa
que la CLI: cada ruta llama a la función que ya llama `gimg/cli.py`, así que las respuestas coinciden con las de
`--json`. Texto de referencia; el diseño y las decisiones están en `docs/plan.md` (D17, D25, «F3 en detalle»).

La doc se comprueba con `tests/test_api_doc.py`: cada ruta registrada en `gimg/server.py` tiene aquí su apartado.

## Arranque

| Orden | Qué hace |
|---|---|
| `gimg serve` | Servicio en primer plano en `127.0.0.1:8737` (Ctrl-C para). `--port N`, `--idle-min N` |
| `gimg serve --detach` | Lo arranca en segundo plano, espera a `health` hasta 5 s y escribe la URL (`--json`: el estado) |
| `gimg serve --status` / `--stop` | Dice si corre / lo para (SIGTERM; no corta una generación en curso) |
| `gimg ui [--no-browser]` | Arranca el servicio si hace falta y abre la interfaz en el navegador; escribe la URL siempre |

- **Puerto:** `--port`, si no `GIMG_PORT`, si no `"serve": {"port"}` de `<config>/config.json`, si no **8737**. Si está
  ocupado, error `serve.port_busy` (no se busca otro). Escucha siempre solo en `127.0.0.1`.
- **Una instancia:** `<data>/serve.lock`; el estado vive en `<data>/serve.json` (`pid`, `port`, `url`, `version`,
  `startedAt`) y el log en `<data>/serve.log`.
- **Arranque bajo demanda:** `gimg ui`, `gimg order submit` y `gimg attempt new` arrancan el servicio si no corre.
  `GIMG_AUTOSTART=0` (también `false`, `no`, `off`, sin distinguir mayúsculas) lo apaga.
- **Inactividad:** se para solo tras 15 min sin peticiones, sin trabajador y sin entradas `queued`/`running`
  (`--idle-min`, `"serve": {"idleMinutes"}`; `0` = nunca).
- **Trabajador:** el servicio no genera: lanza `gimg work` como proceso aparte cuando hay entradas en cola.

Los ejemplos usan `B=http://127.0.0.1:8737`.

## Convenciones

- **Prefijo** `/api`. `{p}` es el proyecto, `{profile}` el perfil, `{key}` la clave del pedido en **un solo segmento**:
  la `/` de `fauna/lobo` se codifica `%2F` (`fauna%2Flobo`). `{id}` es el número del intento.
- **Cuerpos** JSON, objeto en todos los que escriben (`{}` vale). Un campo no previsto da `api.bad_param`.
- **Respuestas** JSON salvo las imágenes (`image/png`), el log (`text/plain`) y los SVG (`image/svg+xml`). Las de `/api`
  llevan `Cache-Control: no-store`; las imágenes de intentos, `private, no-cache` con `ETag` y `304` a `If-None-Match`.
- **Rutas del proyecto** nunca salen como rutas absolutas: las imágenes se piden por id de intento, y `deliveredTo` es
  relativa a la raíz del proyecto.

## Seguridad

Antes de tocar nada, en cada petición y en este orden:

1. **Host:** `127.0.0.1:<puerto>` o `localhost:<puerto>`; si no, 403 `api.bad_host` (corta el *DNS rebinding*).
2. **Origin:** si viene, `http://127.0.0.1:<puerto>` o `http://localhost:<puerto>`; si no, 403 `api.bad_origin`. Sin
   `Origin` se acepta (CLI, `curl`, otros programas). `Sec-Fetch-Site`, si viene, `same-origin` o `none`.
3. **Métodos:** solo `GET`, `POST` y `PUT`; el resto (también `OPTIONS`) da 405 `api.method_not_allowed`.
4. **Content-Type:** `POST` y `PUT` exigen `Content-Type: application/json` (415 `api.content_type`), `Content-Length`
   (411 `api.length_required`) de hasta 1 MiB (413 `api.body_too_large`) y un objeto JSON (400 `api.bad_json`). Por eso
   un formulario de otra web no puede escribir.
5. **Sin CORS:** no se envía ningún `Access-Control-*`; otro origen no puede leer las respuestas.

Un segmento con `..`, `\`, NUL o vacío da 404 sin llegar a disco. Todas las respuestas llevan `X-Content-Type-Options:
nosniff`, `Referrer-Policy: no-referrer` y `Cross-Origin-Resource-Policy: same-origin`. No hay token de acceso.

## Errores e idioma

Toda respuesta de error es:

```json
{"error": {"code": "order.unknown", "params": {"key": "x", "profile": "banner"}, "message": "…", "errors": ["…"]}}
```

`code` y `params` son los de la `GimgError`; `message` está en el idioma de la petición; `errors` (opcional) son las
líneas del esquema cuando el pedido no valida. Idioma: `?lang=es|en`, si no el primero soportado de `Accept-Language`,
si no el del sistema. Estados: 400 petición mal formada o valor no válido (`api.bad_json`, `api.bad_param`, `*.invalid`,
`limit.*`, `path.*`, `key.*`); 403 Host u Origin; 404 `project.unknown`, `order.unknown`, `order.profile_unknown`,
`order.attempt_unknown`, `queue.unknown`, `api.not_found`; 405, 411, 413, 415 de arriba; 409 estado que no lo permite
(`order.choose_*`, `order.undo_*`, `order.history_empty`, `queue.not_cancellable`, `compose.busy`, `measure.busy`,
`api.heavy_busy`, `delivery.target_taken`); 500 fallos del lado del servidor (`api.unexpected` lleva `"message":
"Tipo: texto"`). Los textos de todos los códigos: `GET /api/locales/{lang}`.

## Rutas

### GET /api/health

Estado del servicio. Respuesta: `{"ok": true, "api": 1, "version", "pid", "port", "engine", "worker": bool}`.

```sh
curl -s $B/api/health
```

### GET /api/locales/{lang}

Los textos (errores e interfaz) de `es` o `en`, tal como están en `gimg/locales/<lang>.json`. Error: `api.not_found`.

```sh
curl -s $B/api/locales/es
```

### GET /api/projects

Proyectos registrados. Respuesta: `[{"name", "root", "ok", "profiles": [nombre], "orders": n, "delivered": n,
"error"?}]`; `delivered` cuenta los pedidos con elegida. Un proyecto cuya configuración no carga sale con
`"ok": false`, `error` y los contadores a cero: no rompe la lista.

```sh
curl -s $B/api/projects
```

### GET /api/projects/{p}

`{"name", "root", "config"}` (perfiles, `compose`, `brand`). Errores: `project.*`.

```sh
curl -s $B/api/projects/mi-proyecto
```

### GET /api/projects/{p}/orders

Pedidos del proyecto, como `order list --json`. Query: `profile=<perfil>`, `chosen=true|false`. Errores:
`order.profile_unknown`, `api.bad_param`.

```sh
curl -s "$B/api/projects/mi-proyecto/orders?profile=banner&chosen=false"
```

### POST /api/projects/{p}/orders

Crea un pedido (el JSON de `order.schema.json`, con su `count`) y encola los intentos; `"draft": true` los pide en
borrador. Respuesta 201: `{"order", "entries", "estimateMs"}`. Errores: `order.invalid` (con `errors`), `limit.*`,
`key.*`, `order.profile_unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/orders \
  -d '{"key":"fauna/lobo","profile":"banner","prompt":"un lobo en la nieve","count":2}'
```

### GET /api/projects/{p}/orders/{profile}/{key}

El pedido con sus intentos, como `order show --json`, más `deliveredTo`: ruta del archivo entregado relativa a la raíz
del proyecto, o `null` si no hay elegida. Error: `order.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo
```

### PUT /api/projects/{p}/orders/{profile}/{key}/text

Sustituye los textos del pedido. Cuerpo: `{"text": {"title": "…"}}` (`{}` los borra). Respuesta: el pedido. Errores:
`order.text_unknown_field`, `order.invalid`, `api.bad_param`.

```sh
curl -s -X PUT -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/text \
  -d '{"text":{"title":"El lobo"}}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts

Más intentos (otra semilla, retoque del prompt, varios seguidos, borrador). Cuerpo, todo opcional: `{"count", "seed",
"prompt", "steps", "cfg", "sampler", "draft"}`. Respuesta 202: `{"entries", "estimateMs"}`. Errores:
`order.count_invalid`, `order.prompt_too_long`, `limit.*`, `order.unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts -d '{"count":2,"seed":7}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/mark

Marca un intento. Cuerpo: `{"state": "new|candidate|discarded"}`. Respuesta: el intento. Errores:
`order.state_invalid`, `order.discard_chosen` (409), `order.attempt_unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/mark -d '{"state":"candidate"}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/note

Nota del intento. Cuerpo: `{"text": "…"}`. Respuesta: el intento. Error: `order.note_invalid`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/note -d '{"text":"buenas alas"}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/choose

Elige un intento y entrega su PNG y el manifiesto al proyecto. Cuerpo: `{"attempt": <id>}` (entero). Respuesta:
`{"old", "new", "deliveredTo"}`; `deliveredTo` es relativa a la raíz del proyecto. Errores: `order.choose_*` (409),
`delivery.*`, `order.attempt_unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/choose -d '{"attempt":1}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/undo

Vuelve a la elegida anterior (o a ninguna, y entonces retira lo entregado). Cuerpo: `{}`. Respuesta: `{"old", "new",
"deliveredTo"}` (`null` si ya no hay elegida). Errores: `order.history_empty`, `order.undo_*` (409).

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/undo -d '{}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/compose

Recompone el texto y el logo sobre el intento (necesita ffmpeg y rsvg-convert). Cuerpo opcional: `{"text": {"campo":
"valor"}}`. Respuesta: el intento (con `delivered` si es la elegida). Una sola tarea pesada a la vez: la segunda espera
hasta 60 s y da 409 `api.heavy_busy`. Errores: `compose.busy` (409), `compose.*`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/attempts/1/compose -d '{"text":{"title":"El lobo"}}'
```

### GET /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/image

PNG del intento; `?raw=1` da la imagen cruda (sin composición). Con `ETag`: `If-None-Match` devuelve 304. Error:
`api.not_found`.

```sh
curl -s -o intento.png "$B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/image?raw=1"
```

### GET /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/log

`text/plain` del log del intento. Error: `api.not_found`.

```sh
curl -s $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/log
```

### GET /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/measure

Mide la imagen del intento como `gimg measure --json`, con la paleta de `brand`. Query: `raw=1`, y juntas `zone=x,y,w,h`
y `text=%23RRGGBB`. Una tarea pesada a la vez (409 `api.heavy_busy`). Errores: `measure.*`, `api.bad_param`.

```sh
curl -s "$B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/attempts/1/measure?zone=40,40,600,120&text=%23FFFFFF"
```

### GET /api/projects/{p}/profiles/{profile}/assets/{kind}

El SVG declarado en `compose` del perfil; `{kind}` es `template` o `logo`. Se sirve con una CSP que impide ejecutar
script. Errores: `compose.template_missing`, `compose.logo_missing`, `api.not_found`.

```sh
curl -s $B/api/projects/mi-proyecto/profiles/og/assets/template
```

### GET /api/queue

La cola: cada entrada con `progress`, `errorText` y `estimateMs` si procede (sin la ruta de la vista previa). Query:
`state=queued|running|done|failed|cancelled`. Error: `queue.bad_state`.

```sh
curl -s "$B/api/queue?state=running"
```

### GET /api/queue/{id}/preview

PNG de la vista previa mientras la entrada corre (`Cache-Control: no-store`). Error: `api.not_found`.

```sh
curl -s -o preview.png $B/api/queue/3/preview
```

### POST /api/queue/{id}/cancel

Cancela una entrada. Cuerpo: `{}`. Respuesta: la entrada. Errores: `queue.unknown`, `queue.not_cancellable` (409).

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/3/cancel -d '{}'
```

## Interfaz

`GET /` sirve `gimg/ui/index.html` y `GET /ui/<ruta>` los archivos de `gimg/ui/` (extensiones `.html .css .js .svg
.png .woff2 .json`), con una CSP sin JS en línea ni recursos externos.
