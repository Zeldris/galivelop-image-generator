# API local de galivelop-image-generator

[English](en/api.md)

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
  `build`, `startedAt`) y el log en `<data>/serve.log`.
- **Arranque bajo demanda:** `gimg ui`, `gimg order submit` y `gimg attempt new` arrancan el servicio si no corre.
  `GIMG_AUTOSTART=0` (también `false`, `no`, `off`, sin distinguir mayúsculas) lo apaga.
- **Inactividad:** se para solo tras 15 min sin peticiones, sin trabajador y sin entradas `queued`/`running`
  (`--idle-min`, `"serve": {"idleMinutes"}`; `0` = nunca).
- **Trabajador:** el servicio no genera: lanza `gimg work` como proceso aparte cuando hay entradas en cola, salvo con la cola en pausa.

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
`order.attempt_unknown`, `order.batch_unknown`, `queue.unknown`, `queue.batch_not_found`, `api.not_found`; 405, 411, 413, 415 de arriba; 409 estado que no lo permite
(`compose.template_exists`, `order.choose_*`, `order.undo_*`, `order.history_empty`, `order.troubleshooting`, `order.batch_failed`, `order.not_blocked`, `order.extend_pending`, `order.extend_used`, `brand.missing_piece`, `brand.exists`, `queue.not_cancellable`, `queue.not_movable`, `compose.busy`, `measure.busy`,
`api.heavy_busy`, `delivery.target_taken`); 422 la hoja de marca no permite montarlo (`brand.blocked`, `brand.no_sheet` y los `brandsheet.*` sobre el contenido de la hoja); 500 fallos del lado del servidor (`api.unexpected` lleva `"message":
"Tipo: texto"`). Los textos de todos los códigos: `GET /api/locales/{lang}`.

## Rutas

### GET /api/health

Estado del servicio. Respuesta: `{"ok": true, "api": 1, "version", "build", "pid", "port", "engine", "worker": bool, "paused": bool}`. `paused` es `true` con la cola en pausa (`gimg queue pause`).
`build` es una huella del código que corre el servicio, sacada de las rutas y el contenido de los `.py` y `.json` de
`gimg`, sin `gimg/ui/` (la interfaz se lee del disco en cada petición). Dos copias del mismo código dan la misma huella. Con la misma versión y otro código (tras un `git pull`), `gimg ui` (`arrancar.sh`) para el servicio
viejo y arranca uno nuevo, salvo con un trabajador vivo.

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

`{"name", "root", "config", "sheet", "pieceTypes"}` (perfiles, `compose`, `brand`). `sheet`: `{"present", "valid", "version", "path", "extends": [..], "errors": [..]}` (sin hoja: `present: false` y `pieceTypes: []`, sin error); `pieceTypes`: `[{"id", "label", "profile", "register", "chroma", "seed", "count", "workshop", "profileProject", ..}]` (`profileProject`: el proyecto cuyo `profiles` tiene ese perfil; un tipo heredado usa el del proyecto que lo declaró, no uno homónimo del hijo). Errores: `project.*`.

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
borrador. `"template"` (opcional, no se guarda en el pedido): id de la plantilla de composición de los intentos
(`gimg order submit --template`); se valida antes de guardar y de encolar nada. `"model"` (opcional, tampoco se guarda en el pedido): modelo de los
intentos (`gimg order submit --model`); si no está en el catálogo, `model.unknown` y no se guarda nada; un valor que no
es texto, `api.bad_param`. Cada entrada de la cola lleva `position` (la cola la sirve el worker de menor a mayor;
`POST /api/queue/{id}/move` la cambia). Respuesta 201: `{"order", "entries",
"estimateMs"}`. Errores: `order.invalid` (con `errors`), `limit.*`, `key.*`, `order.profile_unknown`,
`compose.template_unknown` (400).

Modo marca (0.8.0): `"mode": "brand"` (ausente o `"free"` es el pedido de siempre) con `"piece"` (tipo de pieza de la
hoja), `"subject"` (no vacío, hasta 4000 caracteres) y `"cleanZone"` (opcional). La hoja arma el prompt (`brand/prompt`)
y se guarda en `order.prompt`; el perfil sale de la pieza (otro distinto, `order.profile_mismatch`; si falta se rellena)
y `seed`, `count` y el modelo salen de la pieza si el cuerpo no los da. No lleva el `style` del perfil. El pedido guarda
`mode`, `piece`, `subject`, `cleanZone` y `sheetVersion`; cada intento y cada entrada de la cola, `mode` y (en modo marca)
`sheetVersion` (los anteriores se leen como `free`). `sheetVersion` y `modeChanges` del cuerpo se ignoran. Errores
400: `order.piece_required`, `order.subject_required`, `order.brand_prompt` (en modo marca no se envía `prompt`),
`order.profile_mismatch`, `brandsheet.unknown_piece`; 422: `brand.no_sheet` (el proyecto no tiene hoja),
`brand.blocked` (el lint de la hoja falla: `errors` lleva las comprobaciones que fallan) y los `brandsheet.*` de una hoja
rota. Con hoja válida la respuesta lleva además `checks` (el lint: en modo marca los avisos; en un pedido libre, todos
avisos, nunca bloquea); sin hoja, no hay `checks`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/orders \
  -d '{"key":"fauna/lobo","profile":"banner","prompt":"un lobo en la nieve","count":2}'
```

### GET /api/projects/{p}/orders/{profile}/{key}

El pedido con sus intentos, como `order show --json`, más `deliveredTo`: ruta del archivo entregado relativa a la raíz
del proyecto, o `null` si no hay elegida. En un pedido de marca (`order.json`, que guarda `failures: {count, limit, reasons}` y
`troubleshooting: {rows, extendPending, extensions}`; uno viejo sin ellos vale) la respuesta lleva `failures` (siempre, con `count: 0` y `limit: 3`
por omisión) y `troubleshooting: {"state": "open|blocked|extended", "extensionUsed"?, "row"?}` (`row`: la última fila). Error: `order.unknown`.

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
"prompt", "negative", "steps", "cfg", "sampler", "draft", "template", "model", "subject", "cleanZone", "mode"}` (`negative`: prompt negativo retocado; `""` lo quita; `template`: id de una plantilla de
`GET …/profiles/{profile}/templates`, la de los intentos nuevos; sin él, `default`; `model`: id de `GET /api/models`
que sustituye al del perfil en estos intentos, como `gimg attempt new --model`). Respuesta 202: `{"entries",
"estimateMs"}`; cada entrada lleva su `template`. Errores: `order.count_invalid`, `order.prompt_too_long`, `limit.*`,
`order.unknown`, `compose.template_unknown` (400, antes de encolar nada), `model.unknown` (400), `limit.steps` si
el modelo no cabe en el perfil de máquina.

En un pedido de modo marca, `subject` y `cleanZone` (`""` la quita) rearman el prompt con la hoja actual y lo lintan
(`brand.blocked`, 422, sin tocar el pedido); sin ellos se rearma con los guardados. Se actualizan `subject`,
`cleanZone`, `prompt` y `sheetVersion` del pedido. `prompt` en un pedido de marca es `order.brand_prompt`, salvo con
`"mode": "free"` («Pasar a imagen libre»): el pedido pasa a libre con ese prompt (se le añade el `style` del perfil
como siempre) y se anota en `modeChanges: [{"from", "to", "at"}]`; `mode: "free"` sin `prompt` o con `subject` o
`cleanZone` es `order.mode_conflict`. En un pedido libre, `subject`, `cleanZone` o `mode: "brand"` son
`order.not_brand` (pasar de libre a marca no existe aquí). La respuesta lleva `checks` como la de crear el pedido.

Un pedido de marca con tantos fallos seguidos como su límite está en troubleshooting: `order.troubleshooting` (409, con `count` y
`limit`; también al enviar otra vez el pedido, aunque cambie el sujeto) hasta una fila de troubleshooting, un cambio a libre o `…/troubleshooting/extend`.
Sus entradas ya encoladas quedan retenidas (`held`, en `GET /api/queue`) y el trabajador no las arranca; cambiar el sujeto en un pedido que no
está bloqueado pone el contador a cero.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts -d '{"count":2,"seed":7}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/mark

Marca un intento. Cuerpo: `{"state": "new|candidate|discarded", "reason"?: {"trait", "text"?}}`. `reason` es el «No» con motivo
(solo con `discarded`; los rasgos de la hoja u `other` con `text`) y se guarda en el intento. Cuando todos los intentos de una tanda de
marca están descartados (la tanda tiene los `size` intentos: una entrada cancelada o fallida por el motor no cuenta) la tanda falla: un fallo
en `failures`, con el motivo del último. Respuesta: el intento. Errores: `order.reason_invalid` (400),
`order.state_invalid`, `order.discard_chosen` (409), `order.attempt_unknown`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/attempts/1/mark -d '{"state":"candidate"}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/batches/{id}/fail

«Ninguno vale»: la tanda `id` (la de su primera entrada de la cola, la de `order.json` `batches`) de un pedido de marca falló. Descarta sus
intentos (el elegido no: `order.discard_chosen`), marca la tanda `failed` con su `reason` y suma un fallo al pedido. Cuerpo:
`{"reason": {"trait": "<rasgo de la hoja u other>", "text": "nota"}}` (`other` necesita `text`; los rasgos son los de
`acceptance.traits` y `acceptance.unmeasured` de la hoja). Respuesta: `{"failures": {"count", "limit", "reasons"},
"troubleshooting": {"state", "row?"}}`. Solo cuentan los pedidos de marca, y solo el fallo a mano: un fallo técnico del motor o una
cancelación no suman. El contador por pedido llega al límite (3, `brand.failureLimit` de la configuración del proyecto lo cambia)
y el pedido queda en troubleshooting; lo pone a cero un intento con nota de 5 o más (cuando haya nota), cambiar el sujeto o una fila de
troubleshooting. Errores: `order.reason_invalid` (400), `order.not_brand` (400), `order.batch_unknown` (404),
`order.batch_failed` (409, la tanda ya cuenta), `order.discard_chosen` (409). CLI: `gimg order fail <proyecto> <clave> <perfil> <tanda> --reason RASGO [--note TEXTO]`.
Las entradas que queden en la cola de esa tanda no se cancelan solas (`POST /api/queue/batches/{id}/cancel`).

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/batches/3/fail -d '{"reason":{"trait":"horizon"}}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/troubleshooting/extend

«Una tanda más» para un pedido en troubleshooting: la siguiente llamada a `attempts` (o el envío del pedido) se acepta aunque el pedido
esté bloqueado. Las entradas de esa tanda llevan `extended: true` (no se retienen) y la ampliación queda apuntada en
`order.json` `troubleshooting.extensions` (`{at, batch}`); acabada la tanda, el pedido sigue bloqueado si el contador no bajó.
Solo una por ciclo de fallos (el ciclo acaba cuando el contador vuelve a cero); mientras tanto `troubleshooting` lleva
`extensionUsed: true`. Cuerpo: `{}`. Respuesta: `{"failures", "troubleshooting"}` (`state: "extended"`). Errores:
`order.not_blocked` (409), `order.extend_pending` (409, ya hay una sin usar), `order.extend_used` (409, ya se usó en este
ciclo). CLI: `gimg troubleshoot extend <proyecto> <clave> <perfil>`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/banner/fauna%2Flobo/troubleshooting/extend -d '{}'
```

### GET /api/projects/{p}/troubleshooting

Las filas de troubleshooting de todos los pedidos del proyecto, de la más antigua a la más reciente: `[{"piece", "key", "profile",
"problem", "attempts": [..], "redesign", "terms": [..], "at", "by"}]`. Errores: `project.unknown`. CLI:
`gimg troubleshoot list <proyecto>`.

```sh
curl -s $B/api/projects/mi-proyecto/troubleshooting
```

### POST /api/projects/{p}/troubleshooting

Escribe una fila en el pedido que dice `key` + `profile`. Cuerpo: `{"key", "profile", "problem", "attempts"?: [ids], "redesign"?,
"terms"?: [..], "by"?}` (`by` por omisión `person`). Respuesta 201: la fila. Pone el contador de fallos del pedido a cero, con lo que lo
retenido en la cola se libera, y gimg genera el Markdown (`brand.troubleshootingMarkdown` del proyecto, relativo a su raíz; sin él,
`troubleshooting.md` en la carpeta de datos del proyecto). Errores: `api.bad_param` (400), `order.unknown` (404), `order.not_brand`
(400), `order.attempt_unknown` (404). CLI: `gimg troubleshoot add <proyecto> <clave> <perfil> --problem TEXTO [--attempt N]
[--redesign TEXTO] [--term T] [--by NOMBRE]`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/troubleshooting \
  -d '{"key":"fauna/lobo","profile":"banner","problem":"el islote sale plano","attempts":[1,2],"terms":["islet"]}'
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
"valor"}, "template": "id", "layout": {"title": {"x", "y", "w", "h"}}}`. Con `template` se compone con esa plantilla y
el intento la conserva (`compose.templateId`); sin él, con la que ya tenía (si no, `default`). `layout` mueve los
elementos de la plantilla (`id="gimg-<nombre>"` con `data-gimg-box`), en píxeles enteros del destino, y el intento lo
conserva (`compose.layout`, solo lo movido); `{}` vuelve a la plantilla, y sin `layout` se mantiene el del intento salvo
que cambie la plantilla (entonces se vacía). `compose.contrast` guarda el contraste de cada texto sobre la imagen base.
Respuesta: el intento (con `delivered` si es la
elegida). Una sola tarea pesada a la vez: la segunda espera hasta 60 s y da 409 `api.heavy_busy`. Errores:
`compose.busy` (409), `compose.template_unknown` (400; una `templateId` guardada que ya no existe también falla, sin
cambiar a otra), `compose.element_unknown`, `compose.bad_layout`, `compose.bad_element` (400, antes de cambiar nada si
el `layout` viene en la petición), `compose.*`.

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/attempts/1/compose -d '{"text":{"title":"El lobo"}}'
```

### POST /api/projects/{p}/orders/{profile}/{key}/attempts/{id}/crop

Recorta el intento con una caja y guarda el trozo como **intento derivado**; el original no se toca. Cuerpo: `{"box":
[x0, y0, x1, y1], "lockRatio": true, "to": {"profile": "p", "key": "k"}}`. `box` son cuatro enteros en píxeles de la
imagen cruda del intento (`x1` e `y1` no se incluyen); `lockRatio` (por defecto `true`) exige que la caja tenga la
proporción del perfil de destino (1 % de margen) y da exactamente su `width`×`height`; con `false` el derivado tiene el
tamaño de la caja, sin remuestrear. Al reducir se promedia el área y al ampliar es bilineal. `to` (opcional) lleva el
trozo a otro pedido del proyecto; si no existe se crea con el `prompt` del pedido de origen, y el perfil tiene que
existir. El derivado queda en estado `new`, con `image` `attempts/<id>.png`, la semilla, el prompt, los `params` (con
el nuevo `width` y `height`), las referencias, el negativo y el borrador del origen, y `derivedFrom`: `{"profile",
"key", "attempt", "box", "lockRatio"}`; se elige con `choose` como cualquier otro. Respuesta: `{"attempt": {…},
"profile": "p", "key": "k", "created": false}` (`created` es `true` si el pedido de destino era nuevo). Una sola tarea
pesada a la vez: la segunda espera hasta 60 s y da 409 `api.heavy_busy`. Errores: `crop.bad_box` (400: no son cuatro
enteros o la caja no tiene área), `crop.outside` (400: sale de la imagen), `crop.ratio_mismatch` (400), `crop.compose_unsupported` (400: the destination profile composes),
`crop.bad_target` (400), `order.unknown` y `order.attempt_unknown` (404), `order.profile_unknown` (404, también el del
destino).

```sh
curl -s -X POST -H 'Content-Type: application/json' \
  $B/api/projects/mi-proyecto/orders/portada/fauna%2Flobo/attempts/1/crop -d '{"box":[0,64,1536,928]}'
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

Mide la imagen del intento como `gimg measure --json`, con la paleta de `brand`. Query: `raw=1` (la cruda, tal cual) o
`base=1` (la imagen base: la cruda llevada al destino, sin la capa; con `zone` en píxeles del destino, que se lleva a la
cruda con `compose.zone_to_raw`, y la respuesta repite esa `zone`), y juntas `zone=x,y,w,h` y `text=%23RRGGBB`. `raw=1`
y `base=1` no van juntos (`api.bad_param`). Una tarea pesada a la vez (409 `api.heavy_busy`). Errores: `measure.*`, `api.bad_param`.

```sh
curl -s "$B/api/projects/mi-proyecto/orders/og/fauna%2Flobo/attempts/1/measure?zone=40,40,600,120&text=%23FFFFFF"
```

### GET /api/projects/{p}/profiles/{profile}/templates

Las plantillas de composición del perfil: `[{"id", "template", "logo", "fields", "zone"?, "textColor"?, "source",
"default"}]`, `default` primero y el resto por id (`logo` y `zone`/`textColor` heredados como dice `compose.effective`).
`source` dice de dónde sale: `config` (`compose.templates`), `project` (`<compose.templatesDir>/<perfil>/`) o `local`
(`<datos>/projects/<p>/templates/<perfil>/`); un id repetido entre fuentes vale el de la primera. Un perfil sin
`compose` da `[]`. Cada entrada trae además `"elements"`: lo que lee `compose.elements` en su SVG
(`[{"id", "kind": "text|logo|ornament", "box": {x, y, w, h}, "color"?}]`), `[]` si el `viewBox` no es el del destino, si no
hay elementos o si el SVG no se puede leer (el resto de la lista sale igual). Es la misma lista que `gimg templates --json`.
Si el perfil admite guardar en el proyecto lo dice `compose.templatesDir` de la configuración (`GET /api/projects/{p}`).
Error: `order.profile_unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/profiles/og/templates
```

### POST /api/projects/{p}/profiles/{profile}/templates

Guarda como plantilla nueva la de un intento con su `layout` aplicado y los huecos sin sustituir. Cuerpo: `{"from":
{"key": "<pedido>", "attempt": <id>}, "name": "<id nuevo>", "dest": "local|project"}` (`dest` por defecto `local`).
`local` escribe `<datos>/projects/<p>/templates/<perfil>/<name>.svg`; `project`, `<compose.templatesDir>/<perfil>/<name>.svg`
dentro del proyecto. Al lado va `<name>.json` con `base` (la plantilla de origen) y lo heredado (`logo`, `fields`,
`zone`, `textColor`). Respuesta 201: la entrada nueva de la lista de plantillas. Nunca sobrescribe. Errores:
`compose.template_exists` (409, el nombre ya existe en cualquier fuente), `compose.templates_dir_missing` (400, `project`
sin `templatesDir`), `compose.bad_name`, `compose.bad_dest`, `compose.element_unknown`, `compose.template_unknown`
(400), `order.unknown`, `order.attempt_unknown`, `order.profile_unknown` (404), `api.bad_param`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/projects/mi-proyecto/profiles/og/templates \
  -d '{"from":{"key":"fauna/lobo","attempt":1},"name":"lobo-izquierda","dest":"local"}'
```

### GET /api/projects/{p}/profiles/{profile}/assets/{kind}

El SVG declarado en `compose` del perfil; `{kind}` es `template` o `logo`. Con `?id=<plantilla>`, el de esa plantilla
(sin `id`, el de `default`). Se sirve con una CSP que impide ejecutar script. Errores: `compose.template_missing`,
`compose.logo_missing`, `compose.template_unknown` (400), `api.not_found`.

```sh
curl -s "$B/api/projects/mi-proyecto/profiles/og/assets/template?id=claro"
```

### GET /api/queue

La cola: cada entrada con `progress`, `errorText`, `held: "troubleshooting"` (una entrada `queued` de un pedido de marca en troubleshooting: el
trabajador no la arranca hasta resolverlo o cancelarla; la de una tanda `extended` no) y `estimateMs` si procede (sin la ruta de la vista previa). Query:
`state=queued|running|done|failed|cancelled`. Error: `queue.bad_state`. La respuesta lleva la cabecera
`X-Queue-Paused: 1|0` (la cola está en pausa o no, como `paused` de `/api/health`); el cuerpo sigue siendo la lista.

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

### POST /api/queue/{id}/move

Mueve una entrada que espera (`queued`) en la fila de la que toma el trabajador. Cuerpo: `{"to": "up|down|top"}`
(`up`/`down` un puesto; `top` la primera). Respuesta: la entrada. Errores: `queue.unknown`, `queue.not_movable` (409,
no está `queued`), `queue.bad_move` (400). CLI: `gimg queue move <id> up|down|top`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/5/move -d '{"to":"top"}'
```

### POST /api/queue/batches/{id}/move

Mueve una tanda entera. Una tanda son las entradas de un mismo envío de pedido o de una misma llamada a `attempts`;
las de modo marca siempre forman una (también de una), las libres solo si son más de una. Cada entrada de tanda lleva
`batch: {"id", "index", "size"}` (`id` es el de su primera entrada; también sale en `GET /api/queue`), el intento que
genera lleva `batch: <id>` y `order.json` guarda `batches: [{id, size, mode, subject?, cleanZone?, warnings, createdAt}]`.
Las entradas `queued` de la tanda se mueven juntas, como un bloque: `up`/`down` pasan por encima de una entrada u otra
tanda vecina; `top` las pone primeras. Cuerpo: `{"to": "up|down|top"}`. Respuesta: `{"entries": [...]}` (las movidas).
Errores: `queue.batch_not_found` (404), `queue.not_movable` (409, ninguna `queued`), `queue.bad_move` (400). CLI:
`gimg queue move --batch <id> up|down|top`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/batches/4/move -d '{"to":"top"}'
```

### POST /api/queue/batches/{id}/cancel

Cancela las entradas `queued` de la tanda y pide la cancelación de la que corre (como `cancel`). Cuerpo: `{}`.
Respuesta: `{"entries": [...]}` (todas las de la tanda). Errores: `queue.batch_not_found` (404), `queue.not_cancellable`
(409, ya no queda ninguna `queued` ni `running`). CLI: `gimg queue cancel --batch <id>`. Parada por nota: cuando un
intento de la tanda termina con `score.value` >= 9 (`queue.STOP_SCORE`; la nota llega en 0.9.0), el trabajador cancela
las entradas `queued` que quedan de su tanda y les pone `stoppedBy: <id del intento>`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/batches/4/cancel -d '{}'
```

### POST /api/queue/clear

Cancela todas las entradas `queued` (solo las de `project`, si se da); nunca toca una `running`. Cuerpo:
`{"project"?}`. Respuesta: la lista de entradas canceladas. CLI: `gimg queue clear [--project P]`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/clear -d '{"project":"mi-proyecto"}'
```

### POST /api/queue/pause

Pausan y reanudan la cola (cuerpo `{}`, con `Content-Type: application/json`). Con la cola en pausa el trabajador termina la imagen en curso y no
coge otra, y el servicio no lanza trabajador; al reanudar lo relanza en su siguiente latido (unos segundos). Respuesta:
`{"paused": bool, "changed": bool}` (`changed` es `false` si ya estaba así). El estado se lee en `paused` de
`GET /api/health`. Con la cola en pausa, lo que espera en ella no mantiene vivo el servicio: se apaga por inactividad
como sin cola, y `gimg queue resume` lo vuelve a arrancar si queda algo en cola. CLI: `gimg queue pause` y
`gimg queue resume`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/pause -d '{}'
```

### POST /api/queue/resume

Quita la pausa (cuerpo `{}`); respuesta `{"paused": false, "changed": bool}`. Ver `POST /api/queue/pause`. CLI: `gimg queue resume`.

```sh
curl -s -X POST -H 'Content-Type: application/json' $B/api/queue/resume -d '{}'
```

### GET /api/models

El catálogo de modelos (`gimg/models.json`) frente al perfil de máquina: `[{"id", "license", "defaults": {"steps",
"cfg", "sampler"}, "installDefault", "allowed", "reason"?}]`. Si `allowed` es `false`, `reason` es `{"code",
"message"}` del `limit.*` que lo impide (hoy `limit.steps`: los pasos por defecto del modelo superan `maxSteps`).

```sh
curl -s $B/api/models
```

### GET /api/projects/{p}/check

Las comprobaciones de `gimg doctor` que tocan al proyecto (fuentes de `compose.fonts`, archivos de plantillas y
logos, elementos editables y `viewBox`): `[{"id", "status": "ok|warn|fail", "message", "fix"?}]`.
Con hoja de marca (o sin ella, avisando) añade las filas `sheet.present`, `sheet.valid`, `sheet.extends` y `sheet.contrast` (tinta y tono hondo del acento sobre el papel, mínimo 4,5:1; una hoja o configuración del padre rota sale en `sheet.extends`). Con hoja válida y `brand.sheetMarkdown` en la configuración (ruta relativa a la raíz, el `hoja.md` con el bloque de `gimg brand md`), añade `sheet.markdown`: OK si el bloque coincide con los datos (en `es` o en `en`), FAIL si difiere, no tiene marcadores o no se lee. Error: `project.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/check
```

### GET /api/projects/{p}/brand

Los borradores de marca del proyecto: `[{"slug", "files": [claves presentes], "modified"}]`. El taller de cada marca es
`<datos>/projects/<p>/brand/<slug>/` (slug = nombre sin acentos, minúsculas y guiones); las claves son las de los archivos
del sistema: `emblema-alpha.png`, `emblema.svg`, `emblema-mono.svg`, `wordmark.svg`, `lockup-h.svg`, `lockup-v.svg`,
`contactos.png`. Cada paso pisa su copia en el taller y nunca toca el intento de origen. Error: `project.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/brand
```

### GET /api/projects/{p}/brand/sheet

La hoja de marca resuelta (con la herencia de `extends` aplicada): `name`, `version`, `chain` (proyectos, el propio primero),
`roles` (`{papel: {"hex", "name"}}` de `paper`, `ink`, `accent`, `halo`, `grid`), `palette` (los tokens), `registers`,
`closing`, `paletteSentence` y `paletteSentenceText` (con los colores puestos), `vetoes`, `pieceTypes` (lista, cada tipo con `profileProject` como en `GET /api/projects/{p}`), `acceptance`,
`promptWords` y `origin`: por cada valor (ruta con puntos, p. ej. `palette.paper.$value`; las excepciones de vetos, por su
posición en la lista fusionada) `{"origin": "own|inherited", "project", "file"}`. Errores: `brandsheet.none` y
`brandsheet.missing` (404), `brandsheet.invalid`, `brandsheet.unreadable`, `brandsheet.extends_missing`, `brandsheet.extends_broken`,
`brandsheet.extends_cycle`, `brandsheet.incomplete`, `brandsheet.unknown_register`, `brandsheet.no_tone` (sin tono del acento con contraste 4,5:1 sobre el papel), `brandsheet.markdown_marker_in_data`, `brandsheet.bad_placeholder`, `brandsheet.bad_hex` y cualquier otro `brandsheet.*` sin estado propio (422), `project.unknown`.

```sh
curl -s $B/api/projects/mi-proyecto/brand/sheet
```

### POST /api/projects/{p}/brand/prompt

Monta el prompt de una pieza de marca y lo comprueba, sin efectos y sin pasar por la cola: lo mismo que
`gimg brand prompt --json`. Campos: `piece`, `subject`, `cleanZone` (opcional). Devuelve `{"prompt", "words", "segments",
"checks", "blocked", "defaults", "known"}` (`known`: `[{"term", "row"}]`, los términos de las filas de troubleshooting del proyecto que aparecen
en el sujeto, palabra entera y sin distinguir mayúsculas, cada uno con su fila); cada comprobación lleva `message: {"key", "params"}` (clave de i18n). `from`
(convertir un prompt libre) aún no existe: `brandsheet.convert_unsupported` (400). Errores: `brandsheet.unknown_piece`
(400), `api.bad_param`, los de la hoja de `GET .../brand/sheet`, `project.unknown`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/prompt -H 'Content-Type: application/json' \
  -d '{"piece": "cover", "subject": "Un zorro en la nieve", "cleanZone": "arriba a la izquierda"}'
```

### POST /api/projects/{p}/brand/lint

Comprueba un prompt escrito a mano contra la hoja, en modo libre (los errores bajan a avisos; nunca `blocked`). Campos:
`prompt`, `piece` (opcional). Devuelve `{"checks"}`. Errores: `brandsheet.unknown_piece` (400), `api.bad_param`, los de la
hoja, `project.unknown`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/lint -H 'Content-Type: application/json' \
  -d '{"prompt": "a red fox in the snow", "piece": "cover"}'
```

### POST /api/projects/{p}/brand/matte

Quita el fondo plano de un intento del proyecto. Campos: `name` (nombre de la marca), `source`
(`{"profile", "key", "attempt"}`, resuelto como `attempt_image`), `tol` (60), `soft` (110), `border` (6), `grow` (3, de 0 a 32), `holes` (false: con `true` también se vacían las regiones de color de fondo no conectadas al borde, como un anillo encerrado; en cualquier caso, un píxel ya transparente de la entrada vacía lo conectado a él, si el borde tiene color opaco).
Escribe `emblema-alpha.png` y devuelve lo que `gimg brand matte`. Errores: `api.bad_param`, `brand.bad_name`,
`brand.empty_text`, `brand.no_matte`, `order.attempt_unknown` (404), `api.not_found` (404), `project.unknown`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/matte -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "source": {"profile": "og", "key": "fauna/lobo", "attempt": 1}}'
```

### POST /api/projects/{p}/brand/trace

Pasa el emblema recortado a SVG. Campos: `name`, `mode` (`color` o `mono`), `colors` (solo `color`, de 1 a 64), `usePalette`
(solo `color`; toma `brand.palette` del proyecto y excluye a `colors`), `dp_tol` (1,2), `min_island` (12). Escribe
`emblema.svg` o `emblema-mono.svg`. Errores: `brand.missing_piece` (409, falta el recorte), `brand.no_palette`,
`brand.bad_option`, `api.bad_param`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/trace -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "mode": "color", "usePalette": true}'
```

### POST /api/projects/{p}/brand/wordmark

Dibuja el nombre a trazos. Campos: `name`, `font` (familia instalada, p. ej. `Cinzel`; se resuelve con `fc-match`, nunca
una ruta), `text` (por defecto el nombre en mayúsculas), `weight` (800), `spacing` (según la familia: 0,01 Big Shoulders Display, 0,12 las demás). Escribe `wordmark.svg`. Errores:
`brand.font_unknown`, `brand.font_unreadable`, `brand.tool_missing` (500), `brand.wordmark_no_fit`, `brand.text_too_long`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/wordmark -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "font": "Cinzel", "weight": 700}'
```

### POST /api/projects/{p}/brand/lockup

Junta emblema y wordmark del taller. Campos: `name`, `layout` (`h` o `v`), `cap` (0,45), `gap` (0,25), `width` (1,6).
Escribe `lockup-h.svg` o `lockup-v.svg`. Errores: `brand.missing_piece` (409, faltan `emblema.svg` o `wordmark.svg`),
`brand.bad_option`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/lockup -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "layout": "h"}'
```

### POST /api/projects/{p}/brand/save

Hoja de contactos y sistema completo (7 archivos con el prefijo del slug). Campos: `name`, `dest` (`data`: carpeta
`brand-out/<slug>/` de los datos del proyecto; `project`: la carpeta `brand.dir` de su configuración, dentro de la raíz,
como `compose.templatesDir`), `force` (false). Devuelve `{name, slug, dest, out_dir, files, contact_size, overwritten}`.
Errores: `brand.missing_piece` (409), `brand.exists` (409, sin `force`), `brand.dir_missing` (400, `dest: project` sin
`brand.dir`), `path.outside` (400, `brand.dir` que sale de la raíz por un enlace), `brand.bad_option`.

```sh
curl -s -X POST $B/api/projects/mi-proyecto/brand/save -H 'Content-Type: application/json' \
  -d '{"name": "Mi Marca", "dest": "project", "force": true}'
```

### GET /api/projects/{p}/brand/files/{name}/{file}

Un archivo del taller: `name` es el slug y `file` una de las claves de arriba (`emblema.svg`, no el nombre con prefijo);
cualquier otro nombre da `api.not_found` (404). Los SVG llevan `Content-Security-Policy: sandbox` y `nosniff`; la caché
es `no-cache` con ETag. Un slug mal formado da `brand.bad_name`.

```sh
curl -s $B/api/projects/mi-proyecto/brand/files/mi-marca/emblema.svg
```

## Tarea de bandeja (contrato, 0.11.0)

`gimg/schemas/agent-task.schema.json` fija desde 0.8.0 la forma de una tarea de la bandeja del agente; la bandeja
(`gimg agent todo/answer`, API, pestaña) llega en 0.11.0. Una tarea lleva `schemaVersion`, `id`, `type`, `state`
(`pending`, `answered`, `applied`, `rejected`, `expired`), `question`, `order` (`{key, profile}`; ausente en `sheet`),
`context`, `answer`, `answeredBy` (`claude`, `ollama`, `person`), `rejection`, `createdAt` y `answeredAt`.

Cada `answer` es **el cuerpo de una ruta que ya existe**, para que formulario y `gimg agent answer` compartan forma
(el validador de gimg no tiene palabras condicionales: `answer` se valida contra la definición que nombra `type`):

| `type` | Definición | Cuerpo |
|---|---|---|
| `subject` | `answerSubject` | `subject` y `cleanZone` de `POST …/attempts` y `POST …/brand/prompt` |
| `judgment` | `answerJudgment` | `{attempt, human: {<rasgo>: ok\|bad}}`; cada `bad` es un `reason.trait` de `POST …/attempts/{id}/mark` |
| `redesign` | `answerRedesign` | el cuerpo de `POST /api/projects/{p}/troubleshooting` |
| `choice` | `answerChoice` | `{attempt, reason}`: `attempt` es el cuerpo de `POST …/choose`; `reason` se queda en la tarea |
| `sheet` | `answerSheet` | `{sheet}`: una hoja entera según `brand-sheet.schema.json` (no se siguen referencias entre archivos) |

`tests/test_agent_task.py` comprueba que lo que el esquema da por válido lo acepta la función de la API y que lo que
esta rechaza, el esquema también.

## Interfaz

`GET /` sirve `gimg/ui/index.html` y `GET /ui/<ruta>` los archivos de `gimg/ui/` (extensiones `.html .css .js .svg
.png .woff2 .ttf .json`), con una CSP sin JS en línea ni recursos externos.
