# F4a · Interfaz de Galivelop IG (GVIG)

Interfaz local servida por `gimg serve` desde `gimg/ui/` (D6: HTML + CSS + módulos ES, sin instalar nada, sin CDN; CSP
`default-src 'self'; img-src 'self' data: blob:; script-src 'self'; style-src 'self'`). Pensada para la Steam Deck
(1280x800, mando y panel táctil) y para escritorio. Parte de `propuesta.md`, `referentes.md` y la hoja
`docs/marcas/galivelop-image-generator/hoja.md`. Contrato: `docs/api.md`.

**Probar:** `gimg ui` (o `gimg serve` y abrir `http://127.0.0.1:8737/`). Con `?mock=1` la interfaz usa una API
fingida en memoria (`gimg/ui/mock/api-mock.js`, solo se importa con ese parámetro); sigue pidiendo los textos a
`/api/locales/{lang}`, así que hay que servirla con `gimg serve`.

## Qué cambió al casarla con la API real

- Los estáticos van en `/ui/<ruta>` y `/` sirve `index.html`; el servidor admite también `.ttf`. Fuentes Sora e Inter
  (OFL, `gimg/ui/fonts/OFL.txt`) en TTF variable, activadas en `tokens.css`.
- Los textos `ui.*` viven en `gimg/locales/{es,en}.json`, planos como el resto, y `i18n.js` lee `GET /api/locales/{lang}` tal cual.
- `GET /api/projects` ya trae `profiles`, `orders` y `delivered`; `GET order` y `choose`/`undo` traen `deliveredTo`
  (relativa a la raíz del proyecto): las preguntas 2 y 3 del diseño quedaron resueltas en F3.6.
- `measure` devuelve `image` = id del intento, `contrast {mean, p10, p90, worst}` y `palette {pct}`. El chip espera
  también ante `api.heavy_busy` (409 de la tarea pesada única), no solo `measure.busy`.
- Una composición fallida es `composeError {code, params}` (la interfaz solo mira que exista).
- El mock lee los textos de la API real (antes, de un JSON suelto).
- `tests/test_ui.py` vigila lo que aquí no se puede probar con un navegador: reglas de la CSP, imports y exports,
  claves `ui.*`, rutas y métodos contra el router, estáticos servidos y contraste de `tokens.css`.

## Pendiente (MISSING)

- **Duración del intento** (`durationMs`): no está en el registro del intento, solo en el log de opt-ai; la tarjeta no
  la enseña hasta que la API la dé.
- **Zona y color del texto** para el contraste (`compose.zone`, `compose.textColor`): el esquema del perfil no los
  declara; el chip mide solo la paleta (F4b).
- **Catálogo de modelos** por la API (hoy el modelo es de solo lectura), reordenar y vaciar la cola, pestañas Piezas y
  Marca (F4d), selector de plantilla (F4b) y editor (F4c): huecos en `js/components/slots.js`.
- **Prueba en navegador:** recorrido completo de F4a en el navegador de la Deck y en escritorio, con teclado y con mando.

# Diseño (del agente de diseño, adaptado)

## 1. Pantallas

| Ruta (hash) | Pantalla | Carga | Estados |
|---|---|---|---|
| `#/` | **Proyectos**: rejilla de tarjetas (nombre, ruta, pedidos, entregados, perfiles). Un proyecto roto se ve con su error y sin enlace. | `GET /api/projects` | cargando · vacío (con la orden `gimg project add`) · error |
| `#/p/<p>/pedidos` | **Proyecto**: pestañas Pedidos / Piezas / Marca. Pedidos: filtros por perfil y estado (sin elegir / entregados), filas con miniatura de la elegida (o del último), nº de intentos, pendientes en cola, fecha. Piezas y Marca: «próximamente» (F4d), Marca enseña ya la paleta. | `GET /api/projects/{p}` (config) + `GET …/orders?profile=&chosen=` | cargando · vacío (con `gimg order submit`) · error |
| `#/p/<p>/o/<perfil>/<clave>` | **Pedido** (el corazón): galería + panel lateral pegajoso. `?a=<id>` enfoca ese intento. | `GET project` + `GET order` + cola del store | cargando · sin intentos · error · sin servicio |
| (siempre) | **Barra de cola**: pastilla en la cabecera («1 generando · 2 en cola» + progreso) y cajón a la derecha con filtros Pendientes/Terminadas/Fallidas/Todas, cancelar, miniatura (vista previa si está generando), «Ir al intento»/«Ir al pedido». | `GET /api/queue` cada 3 s (`queue-poll.js`), `POST /api/queue/{id}/cancel`, `GET …/preview` | vacía · sin servicio (la pastilla queda con el último dato; la banda avisa) |

La clave del pedido puede llevar `/` (`portada/og`): va codificada en un solo segmento, como en la API.

## 2. Pantalla del pedido

- **Galería** (`gallery`, `role=list`, `aria-live=polite`): tarjetas de 300 px mínimo, auto-fill; en la Deck a
  1280 px caben 2 columnas con el panel abierto. Orden: la **elegida primero**, luego de la más nueva a la más
  vieja; delante van las **entradas de la cola sin intento** (en cola con puesto y ETA, generando con vista previa,
  progreso y cancelar, fallida con el error, «Reintentar» y «Copiar el error»).
- **Tarjeta de intento** (`attempt-card.js`): imagen compuesta (o fondo crudo con `F`), con `aspect-ratio` del perfil
  para que nada salte al cargar; distintivos (Candidato / Elegida / Descartado / Borrador / Compuesta); metadatos
  (`q3`, semilla, pasos, modelo, tamaño, duración) y **chip de medida D31**; botones **Sí / No** (`aria-pressed`,
  otra pulsación lo quita), **Elegir** (★; sobre la elegida pasa a **Deshacer**; un descartado, un borrador o un intento
  sin componer no se puede elegir y se dice por qué), **Comparar**; nota (se guarda al perder el foco, `POST note`);
  «Más acciones»: Recrear (carga sus parámetros en el panel), Variar (semilla + 1 con sus parámetros), Copiar
  parámetros, Ver registro; y los huecos F4b/F4c.
- **Estados visuales**: candidato borde violeta; elegida borde verde doble; descartado al 62 % de opacidad (vuelve al
  100 % con foco o ratón); en cola borde discontinuo; generando borde verde discontinuo; fallo borde rojo; en
  comparación contorno discontinuo violeta claro.
- **Comparar** (`compare-view.js`): la segunda tarjeta marcada abre la comparación encima de la galería, al mismo
  tamaño, con su estado, semilla y medida; Intercambiar y Cerrar. Máximo dos: la tercera sustituye a la primera.
- **Panel lateral** (`retouch-panel.js`): prompt (contador, aviso si usa una palabra vetada de `brand.bannedWords`,
  Restaurar), estilo del perfil en solo lectura (D19), modelo en solo lectura (no hay catálogo en la API mínima),
  pasos / CFG / sampler, semilla con dado, Borrador (mitad de tamaño, menos pasos, no se entrega), **Otra semilla**
  (semilla + 1: vecindario, D22) y **N seguidas** (2-20). Los botones muestran la ETA (mediana de `estimateMs` de la
  cola del perfil o la del último 202). Solo se envía lo que difiere del pedido (`POST …/attempts`).
- **Textos** (`text-panel.js`): un campo por `compose.fields` del perfil (rótulos `ui.text.field.*`, o el nombre del
  campo si no hay rótulo), «sin guardar», **Guardar** (`PUT …/text`), **Recomponer la elegida** (`POST …/compose`) y
  casilla «Previsualizar»: superpone en HTML (logo SVG del perfil, titular, subtítulo, velo) sobre el fondo crudo
  mientras se escribe (`compose-preview.js`). Es una aproximación: la composición real la hace `gimg compose`.
- **Entregada**: caja verde arriba con `q<id>`, la ruta de entrega si la API la da y **Deshacer** (`POST …/undo`).
- **Refresco**: al cambiar la cola (sondeo) se repinta solo si el pedido tiene entradas; al terminar, fallar o
  cancelarse una entrada del pedido se recarga `GET order`. El foco se conserva en la misma tarjeta. El panel solo se
  reconstruye si cambian prompt/parámetros/textos/elegida, para no perder lo que se está escribiendo.
- **Vista previa de lo que se genera**: `GET /api/queue/{id}/preview` con `?t=` para no cachear, al 55 % de opacidad
  bajo el texto de estado; si no hay imagen aún, se quita sin error.

## 3. Componentes → rutas de la API

| Componente | Rutas |
|---|---|
| `api.js` | envoltorio de `fetch`: `?lang=`, `Content-Type: application/json`, `cache: no-store`; `ApiError{status,code,params,message,errors}`, `OfflineError`; `setTransport` para el mock y los tests; `paths.*` con la clave en un segmento |
| `i18n.js` | `GET /api/locales/{lang}`; `t(key, params)` con `{nombre}` como `gimg/i18n.py`; si falta una clave, se ve la clave |
| `queue-poll.js` / `queue-bar.js` | `GET /api/queue`, `POST /api/queue/{id}/cancel`, `GET /api/queue/{id}/preview` |
| `projects-view.js` | `GET /api/projects` |
| `project-view.js` | `GET /api/projects/{p}`, `GET …/orders?profile=&chosen=`, `GET …/attempts/{id}/image` (miniaturas) |
| `order-view.js` | `GET …/orders/{profile}/{key}`, `POST …/choose`, `POST …/undo`, `POST …/attempts` |
| `attempt-card.js` | `GET …/attempts/{id}/image[?raw=1]`, `POST …/mark`, `POST …/note`, `POST …/compose`, `GET …/log` |
| `measure-chip.js` | `GET …/attempts/{id}/measure?zone=&text=` (409 `measure.busy`: reintento a los 5 s, 3 veces, luego botón «Medir») |
| `compose-preview.js` | `GET /api/projects/{p}/profiles/{profile}/assets/logo` |
| `retouch-panel.js` / `text-panel.js` | `POST …/attempts` (202 `{entries, estimateMs}`), `PUT …/text`, `POST …/compose` |
| `app.js` | `GET /api/health` (aviso si `worker: false`), banda «sin servicio» con `onOffline` |

Errores: todo `ApiError` llega como aviso (`#toasts`, `role=status`) y, si es grave, también a `#alerts`
(`role=alert`, `aria-live=assertive`); el mensaje ya viene traducido por la API (`?lang`). Un `OfflineError` enciende
la banda `#banner` con la orden `gimg serve` y «Reintentar».

## 4. Chip de medida (D31)

Medir cuesta (ffmpeg) y el servidor serializa: el chip pide **de una en una**, solo cuando la tarjeta entra en pantalla
(`IntersectionObserver`), y guarda el resultado por intento y versión de la composición (recomponer o elegir lo
invalida). Muestra «peor contraste:1 · paleta %»: verde si contraste ≥ 4,5 y paleta ≥ `brand.paletteMin` (72, calibrado
en `docs/records/contenido/calibracion-measure.md`); ámbar si contraste ≥ 3 o paleta ≥ mínimo − 12; rojo si no. El
`title` y el `aria-label` llevan la medida completa (media, p10/p90 no: sobran en un chip).

## 5. Atajos (teclado y mando)

Globales: `?` ayuda · `Q` cola · `Esc` cierra cola, imagen o ayuda · `Tab`/`Mayús+Tab` recorren todo. En la galería
(con una tarjeta o un botón suyo enfocado): `←`/`→` intento anterior/siguiente, `↑`/`↓` fila (columnas calculadas
con el ancho real), `Intro` imagen a tamaño real, `S` sí, `N` no, `E` elegir (sobre la elegida, deshacer), `C`
comparar, `F` crudo/compuesta, `G` otra semilla, `R` ir al prompt. Ninguno actúa dentro de un campo de texto.
Mando de la Deck (Steam Input, perfil teclado, **supuesto a comprobar en la máquina**): cruceta → flechas, A → Intro,
B → Esc, Y → S, X → N, gatillo derecho → E, panel táctil → ratón. El diálogo `?` lo documenta.

## 6. Accesibilidad (WCAG 2.2 AA)

- Objetivos táctiles ≥ 44 px (`--tap`), también los botones de la tarjeta (altura mínima) y la pastilla de la cola.
- Foco visible doble (anillo `--accent-text` 3 px + separación del fondo) en `:focus-visible`; las tarjetas son
  focalizables (`tabindex=0`, `aria-label` con id y estado); orden lógico: cabecera → entregada → comparar → galería →
  panel.
- `aria-live`: galería `polite`, avisos `polite`, errores `assertive`; `aria-busy` en la lista de pedidos; la pastilla
  lleva `aria-expanded`/`aria-controls`; `<progress>` nativo con rótulo; distintivos con texto, no solo color (los
  estados también cambian el borde o la opacidad, y la elegida lleva ★).
- `prefers-reduced-motion`: sin pulso, sin giro, sin transiciones. `prefers-color-scheme`: tema claro automático
  (y selector Automático/Oscuro/Claro guardado en `localStorage`). Imágenes con `alt` descriptivo en la caja de luz y
  vacío en las decorativas; el logo es decorativo (el nombre va en texto).
- Idioma: `<html lang>` sigue al selector; por defecto el del navegador (es/en), guardado en `localStorage`.

### Contraste medido (`contraste.py` en esta carpeta, fórmula WCAG)

Oscuro (hoja): texto `#eaf4fa`/`#06121c` **16,9**; secundario `#9fb4c4`/`#06121c` **8,8** (sobre superficie
`#0c1d2b` 7,1); acento claro `#A78BFA`/`#06121c` **6,95** (texto y foco; sobre superficie 2 `#11283a` 5,6);
acento `#8B5CF6` como texto 4,46 (justo; se usa solo en bordes, chips y texto grande). **Blanco sobre `#8B5CF6` da
4,23: no llega a AA para botones** → los botones primarios usan `#5B34C9` (el acento oscuro de la hoja) con blanco:
**7,56**. Estados: ok `#5ad38a` 10,0 · ámbar `#f2c14e` 11,3 · rojo `#ff7b6b` 7,5 (texto oscuro encima; **propuestos**:
la hoja no trae colores de estado). Claro: texto `#0a1a28`/`#f6fafd` **16,8**; acento `#5B34C9` 7,2; secundario
`#4b5f70` 6,3; ok `#1b7a3e` 5,1 · ámbar `#8a5a00` 5,7 · rojo `#b3261e` 6,2 (propuestos). Bordes de campos
`#5f7689` claro 4,5 / `#587891` oscuro 3,7 sobre superficie (≥ 3 para componentes, AA 1.4.11).
Ajuste mínimo pedido a la hoja (ya propuesto en `hoja.md` §3, pendiente de la persona): declarar `#5B34C9` como color de relleno de botón y añadir los colores de estado.

## 7. Decisiones visuales

- Tres capas (`--bg` → `--surface` → `--surface-2`) y bordes `--border`; una sola tipografía de título (Sora 700) y
  cuerpo (Inter) con `font-display`-less fallbacks a `system-ui`: **sin fuentes externas**: Sora e Inter van en `gimg/ui/fonts/` (TTF variable, OFL) y se declaran en `tokens.css`.
- Densidad para 1280×800: cabecera 56 px, panel 380 px, galería de 2 columnas, textos 14-15 px; por debajo de 1000 px
  el panel baja debajo de la galería; por debajo de 640 px, una columna.
- Sin `innerHTML`: `dom.js#h()` construye todo; ningún dato del servidor se interpreta como HTML. Variables CSS por
  CSSOM (`el.style.setProperty`), que la CSP permite (solo prohíbe el atributo `style`).
- Estado en la API, no en el navegador: el store solo guarda la cola, filtros y preferencias (`showRaw`, tema, idioma).
- Rutas por `#hash`: sin servidor de rutas y sin romper los estáticos de `gimg serve`.

## 8. Queda para F4b / F4c / F4d

- **F4b** (hecha; JS sin ejecutar, recorrido en navegador pendiente de la persona): `slots.js#templateSlot` es un
  `<select>` por intento (solo con más de una plantilla; `GET …/profiles/{profile}/templates`, una vez por vista de
  pedido) y al cambiar hace `POST …/compose {"template"}`; el panel de retoque tiene el mismo selector y manda
  `template` en `POST …/attempts`; el chip de contraste y la previsualización usan la `zone` (`x,y,w,h`), el
  `textColor`, los campos y el logo de la plantilla del intento. Queda: la previsualización HTML sigue siendo una
  aproximación (zona izquierda/arriba) hasta el editor de F4c.
- **F4c** (`slots.js#editorSlot`): editor de elementos sobre la imagen (mover/redimensionar titular, subtítulo, logo,
  adornos; `POST …/compose {"layout"}`; guardar como plantilla local o del proyecto, D40). Sustituye a la
  previsualización HTML de `compose-preview.js`.
- **F4d** (`slots.js#newOrderSlot`, pestañas Piezas y Marca): nuevo pedido desde la interfaz, piezas como índice,
  marca con la validación de `gimg doctor`, catálogo de modelos en la API, reordenar y vaciar la cola.
- Pendiente de comprobar **en la Deck** (no se puede probar con tests): mapa de Steam Input, panel táctil sobre
  `details`/`dialog`, rendimiento de la galería con 30+ imágenes de 1280 px (`loading=lazy` ya puesto).

## 9. Preguntas abiertas del diseño

1. Zona y color del texto: pendientes (ver arriba).
2. y 3. `deliveredTo` y el resumen de proyectos: resueltas en la API (F3.6).
4. Fuentes: copiadas (TTF variable).
5. Tope del prompt: la interfaz muestra 2000 caracteres orientativos; el real lo dice la API (`order.prompt_too_long`).
