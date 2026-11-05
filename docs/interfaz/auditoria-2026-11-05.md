# Auditoría de la interfaz web (`gimg/ui`) — 2026-11-05

Pedido de la persona tras probar F4e.5: «un montón de errores de responsive», comprobar que los paneles están bien
creados y conectados, y que la interfaz es «muy poco accesible». Esta auditoría no cambia `gimg/ui`: mide, apunta
cada hallazgo con su archivo y línea, y propone la mejora por pasos para que la persona decida qué va antes de
F4e.2c. Parte de `docs/interfaz/f4a.md`, `propuesta.md` y `referentes.md`: no repite lo que ya está ahí.

## 1. Método

- **Navegador real.** Firefox del sistema por WebDriver BiDi, el mismo arnés que `tests/browser.py` y
  `tests/test_ui_browser.py` (sin Playwright, D6). El sandbox lo lanzó sin problema (`flatpak-spawn --host`).
- **Datos.** Proyecto de prueba con dos pedidos del perfil `fondo` (motor `fake`), uno con intentos en estado
  nuevo, votado y elegido, con composición; cola con entradas encoladas, en marcha y fallidas; idioma `es` y tema
  oscuro (más una pasada en claro y otra en `en`).
- **Anchos.** 360, 768, 1024 y 1440 px, en 15 pantallas y paneles: proyectos, pedidos, piezas, marca, pedido (con el
  panel de retoque arriba y abajo), cajón de la cola, nuevo pedido, comparar, editor de plantilla, ayuda de atajos,
  caja de luz, renombrar, confirmar, borrar plantilla. 62 capturas; seis útiles en `docs/interfaz/auditoria/`.
- **Sondas por pantalla** (`document`/`getBoundingClientRect`/`getComputedStyle`): desbordamiento horizontal
  del documento y de cada contenedor, elementos recortados, objetivos menores de 44 px, controles sin nombre
  accesible, contraste de texto (fórmula WCAG), `tabindex` positivos, altura real de la cabecera frente al token,
  tamaño mínimo de fuente, número de focalizables, elemento con foco al cargar, orden de encabezados y orden de
  tabulación.
- **Por código.** Cliente `api.js` contra las rutas de `gimg/server.py`; claves `ui.*` de `es.json` y `en.json`
  contra las usadas en `gimg/ui/js` e `index.html`; manejo de foco y teclado en los componentes.
- **Lo que no se midió.** Mando (gamepad): no hay API de mando en la interfaz, y Firefox sin un mando real no la
  ejercita; se audita por código (§3.4). Lector de pantalla real (Orca): no probado; roles y nombres sí.

Una nota sobre las capturas: el guion de auditoría no cerraba cada diálogo antes de la pantalla siguiente, así
que algunas capturas de 1024 y 1440 llevan el cajón de la cola abierto. Es un artefacto del guion, no un fallo.

## 2. Capturas

| Captura | Qué enseña |
|---|---|
| `auditoria/proyectos-360.png` | Cabecera a dos líneas, selectores de idioma y tema de 28 px de ancho (texto invisible), ruta del proyecto en crudo en la tarjeta. |
| `auditoria/pedidos-360.png` | Migas a tres líneas con «fond…» cortado, cabecera de 86 px (el token dice 56), aviso flotante tapando las filas. |
| `auditoria/cola-360.png` | Cajón de la cola solapando la cabecera, entradas recortadas por la izquierda (la miniatura no se ve), pestañas de filtro cortadas (solo «Todas»), «Cerrar» encima de los filtros. |
| `auditoria/cola-1440.png` | Lo mismo a 1440: el cajón recorta por dentro («…ed», «All») aunque sobra pantalla. |
| `auditoria/editor-360.png` | Escenario de ~320 px con cajas de 16 px de asa que se pisan entre sí y con sus etiquetas. |
| `auditoria/nuevo-pedido-360.png` | El diálogo de nuevo pedido sí se adapta: una columna, campos de 44 px. Referencia de lo que está bien. |

## 3. Hallazgos

Gravedad: **G** rompe el uso en ese ancho o incumple AA de forma clara; **M** estorba; **L** detalle.

### 3.1 Responsive

| # | G | Hallazgo | Dónde |
|---|---|---|---|
| R1 | G | La cabecera no cabe a 360: el `brand`, las migas (`flex-wrap`) y las herramientas (`margin-left: auto`, sin `flex-wrap` ni `min-width`) compiten y la cabecera crece a 86 px (proyectos) y **139 px** (pedido) a 360, 78 a 768/1024 y 61 a 1440, frente al token `--header-h: 56px`. Los `select` de idioma y tema quedan aplastados a **18-28 px** de ancho (texto invisible, imposible de usar con el dedo). | `gimg/ui/css/layout.css:3-8` (`.app-header`), `:12` (`.crumbs`), `:15` (`.crumbs b`, `max-width: 40vw`), `:16` (`.header-tools`), `:17` (`.select-inline`); `gimg/ui/index.html:22-33` |
| R2 | G | El cajón de la cola es `position: fixed; top: var(--header-h)`: como la cabecera real mide más de 56 px (R1), el cajón **se monta encima de la cabecera** en todos los anchos (sonda: `drawerTop=56` con `headerH` 61-139). | `gimg/ui/css/layout.css:30-35` |
| R3 | G | El cajón desborda en horizontal en **todos** los anchos (sonda `hscroll: aside#queue-drawer` a 360/768/1024/1440): la rejilla `64px 1fr auto` más los botones de la columna `auto` (mover, cancelar, borrar) suma más que `min(100vw, 440px) - 24px`; a 360 las entradas se recortan por la izquierda y la miniatura desaparece; las pestañas de filtro (`div.row`) no envuelven y se cortan tras «Todas»; el botón «Cerrar» se superpone a los filtros. | `gimg/ui/css/layout.css:30-35`, `:37` (`.queue-entry`), `:42-43`; `gimg/ui/js/components/queue-bar.js:108-111` (filtros y acciones en `div.row`), `:149` (`.queue-move`) |
| R4 | M | A 360 el editor de plantilla deja un escenario de ~320 px: las asas de 16 px de cada caja se solapan entre sí y con las etiquetas; con el dedo no se distingue qué asa se coge. A ≤1000 el panel lateral pasa debajo (`.ed-body` a una columna) pero el escenario no gana altura. | `gimg/ui/css/components.css:82` (`.ed-body`), `:85` (`.ed-stage`), `:94-98` (`.ed-handle`), `:106` |
| R5 | M | El panel de retoque a 1440 es más alto que la ventana (parámetros + plantilla + textos): el panel «Textos» queda cortado por abajo y hay que desplazar toda la página, no el panel (`.order-panel` no tiene `max-height`/`overflow` ni es `sticky`). A ≤1000 pasa a estático y se apila debajo de la galería: en un pedido con muchas tarjetas, el retoque queda a varias pantallas de distancia (ver `pedido-panel-abajo-*.png`). | `gimg/ui/css/layout.css:75` (`.order-layout`), `:82-86` |
| R6 | M | Los avisos flotantes (`.toasts`) van fijos abajo al centro con `min(92vw, 520px)`: a 360 tapan las filas de pedidos y los botones del pie de tarjeta; a 1440 se posan sobre la galería. No hay zona reservada ni se apilan hacia arriba sobre un pie. | `gimg/ui/css/components.css:115-119` |
| R7 | M | La tarjeta de proyecto pinta la ruta en crudo (`/home/deck/.cache/...`) como texto de una línea: a 360 se corta sin elipsis significativa y no aporta nada a la persona. | `gimg/ui/js/components/projects-view.js:30`; `gimg/ui/css/layout.css:52-60` |
| R8 | L | A 768 la galería hace dos columnas de 300 px y luego salta a una; la tarjeta de intento de 300 px con el pie de seis botones queda apretada (los chips «Midiendo…»/medida se pegan al borde). | `gimg/ui/css/layout.css:78` (`minmax(300px, 1fr)`), `:89`; `gimg/ui/css/components.css:5-13`, `:49` |
| R9 | L | Las pestañas de proyecto (`.tabs`) no envuelven (`.gallery-bar` sí, `:77`): con un cuarto destino (panel del equipo) o en `en` largo, a 360 se salen del ancho visible. | `gimg/ui/css/layout.css:61-63` |
| R10 | L | `.cols-2` está definido dos veces con reglas distintas (`repeat(2, 1fr)` y `1fr 1fr` con otro `gap`) y su paso a una columna va en un tercer punto de corte (600) distinto de los dos que usa el resto (640 y 1000). Tres puntos de corte para una sola interfaz. | `gimg/ui/css/base.css:88`; `gimg/ui/css/components.css:128`, `:150`; `layout.css:82`, `:87` |

### 3.2 Paneles y botones conectados

Resultado: **todo conectado.** Cada ruta que pide `gimg/ui/js/api.js` existe en `gimg/server.py` y cada botón de los
paneles llama a su función (retoque → `POST /api/orders/.../more`, textos → `PUT .../texts` + recomposición, plantilla
→ `PUT .../layout`, editor → `PUT /api/templates/...`, nuevo pedido → `POST /api/orders`, cola → mover, cancelar,
borrar, parar, reanudar; renombrar → `PATCH`; borrar intento y composición). Las pruebas existentes de
`tests/test_ui_browser.py` ya ejercitan cada panel por el navegador (retoque, textos, selector de plantilla, editor,
nuevo pedido, copiar de, mover y limpiar la cola, votar, elegir, comparar, caja de luz, renombrar).

Lo que **sí** está mal conectado es el **foco y el estado** alrededor de los paneles, no los datos:

| # | G | Hallazgo | Dónde |
|---|---|---|---|
| P1 | G | Al cargar un pedido, la vista **roba el foco** a la primera tarjeta (`article.card.attempt.is-new`): la persona que viene con el teclado o un lector desde las migas aterriza en medio de la galería sin saber dónde está, y en cada repintado se vuelve a enfocar. | `gimg/ui/js/components/order-view.js:366`, `:311-312` |
| P2 | G | El cajón de la cola no es un diálogo: no tiene `role="dialog"` ni `aria-modal`, no atrapa el foco, no deja inerte el resto y la tecla `Tab` sale del cajón hacia el contenido que tiene debajo (tapado). Sí cierra con `Esc` y devuelve el foco a la pastilla. | `gimg/ui/js/components/queue-bar.js:33-34`, `:90` (pastilla con `aria-expanded`/`aria-controls`, correcto) |
| P3 | M | La navegación por flechas de la galería calcula las columnas con `clientWidth / (offsetWidth + 12)`: con el `gap` real (`var(--gap)`) y en los anchos donde la rejilla hace una columna y media, `ArrowDown` salta a una tarjeta que no es la de debajo. | `gimg/ui/js/components/order-view.js:328-336` |
| P4 | M | Los diálogos (nuevo pedido, confirmar, renombrar, editor) paran la propagación de `keydown` para que los atajos de una tecla no disparen mientras se escribe; el panel de retoque y el de textos, que no son diálogos, dependen de que el manejador global compruebe el `target`. Una regla, dos mecanismos: un campo nuevo en un panel que olvide una de las dos dispara `S`/`N`/`E` al escribir. | `gimg/ui/js/components/new-order.js:206`, `confirm.js:15`, `rename-dialog.js:31`, `layout-editor.js:268`; `gimg/ui/js/app.js` (atajos) |
| P5 | L | El editor de plantilla implementa su propia trampa de `Tab`; `askTemplate` abre un segundo `<dialog>` encima del editor. Funciona, pero el foco al cerrar el segundo vuelve al cuerpo del editor y no al botón «Guardar como plantilla» que lo abrió. | `gimg/ui/js/components/layout-editor.js` (trampa de `Tab`, `askTemplate`) |

### 3.3 Accesibilidad (WCAG 2.2 AA)

| # | G | Criterio | Hallazgo | Dónde |
|---|---|---|---|---|
| A1 | G | 2.5.8 Tamaño del objetivo (mín. 24) y la regla del proyecto (44) | Menores de 44 px, varios menores de 24: los `select` de idioma y tema a 360 (**18×44** y **28×44**), el enlace `Proyectos` y el del proyecto en las migas (66×20, 39×20), la casilla «borrador» (15-22×22) y la de atajos (16×22), el chip de medida (42×25), el botón «Cerrar» de los diálogos (44×**36**: `width` sin `min-height`), el selector de plantilla por tarjeta (×37), el botón de los avisos (36). | `layout.css:12-17`; `base.css:61` (`.btn-icon`); `components.css:49` (`.measure .btn`), `:119`; `queue-bar.js`, `attempt-card.js` (selects y casillas) |
| A2 | G | 2.4.3 Orden del foco, 2.4.7 Foco visible | El foco robado al cargar (P1) y el cajón sin trampa (P2). El anillo de foco (`:focus-visible`, `base.css:31-35`) es correcto y de 2 px; pero `:focus { outline: none }` en `base.css:30` lo apaga en navegadores sin `:focus-visible` (hoy todos lo tienen; es tolerable). | `base.css:30-35`; `order-view.js:366`; `queue-bar.js:33` |
| A3 | M | 1.4.3 Contraste | Texto secundario de **11-12,5 px** (`.thumb-empty` «—» a 4,47:1 en 11 px; `.what` del cajón; `kbd` de la ayuda a 11,5 px) por debajo del mínimo cómodo; 4,47 pasa AA por poco. Los chips superpuestos («Sin veredicto», «Compuesta») van sobre la imagen con su propio fondo: pasan, pero tapan el título de la pieza en las tarjetas pequeñas. | `layout.css:43`, `:70`; `base.css:93-97` (`.chip`); `components.css:22-26` (`.badges`) |
| A4 | M | 1.3.1 Información y relaciones | Orden de encabezados: en el cajón, `h2 Cola` antes del `h1` de la página en el DOM (`aside` va antes de `main`); en la ayuda, `h3` dentro de un `dl` (HTML no lo permite: el lector pierde el grupo). El pedido va bien (`h1 > h2 Retoque > h3 > h2 Textos`). | `gimg/ui/index.html:41-43`; `gimg/ui/js/components/shortcuts.js:59-60` |
| A5 | M | 4.1.2 Nombre, rol, valor | El campo «cantidad» de la tanda del retoque solo lleva `aria-label` (sin `<label>` visible; el de nuevo pedido sí lo tiene, `new-order.js:80`); el chip de medida es `role="img"` con `tabindex=0`: focalizable sin ser interactivo (ruido de tabulación); las tarjetas de intento son `article` con `tabindex=0` y `aria-label` «n, estado» pero sin `role` que anuncie que dentro hay botones (un lector lee «artículo» y luego seis botones sin agrupar). Los `sr-only` (`#alerts`, etiquetas) sí están bien. | `retouch-panel.js:33`; `measure-chip.js:100`; `attempt-card.js:84`, `:118` |
| A6 | M | 2.5.7 Movimientos de arrastre | El editor mueve las cajas arrastrando **y** con flechas (alternativa de un solo puntero: cumple). Pero el cambio de tamaño solo se hace con las asas (arrastre), sin alternativa (Mayús+flechas o campos de ancho y alto). | `layout-editor.js` (`ARROWS`, asas) |
| A7 | M | 2.3.3 Animación por interacción, 2.2.2 Pausar | `prefers-reduced-motion` quita el `pulse` y el `spin` (`base.css:139-142`): bien. Las barras de `progress` del cajón y la pastilla siguen moviéndose, lo que es información, no adorno: correcto. Falta una forma de **parar** el refresco automático de la galería mientras se vota (cada repintado mueve el foco: P1). | `base.css:137-142`; `order-view.js:311` |
| A8 | L | 1.4.4 Cambio de tamaño del texto | Toda la interfaz va en `px` (`14px` cuerpo, `12.5px` chips): el zoom del navegador escala, pero la preferencia de «tamaño de fuente» del sistema no. Pasa AA por el zoom; falta una talla «grande» propia (la comunidad de Firefly pide justo esto). | `base.css` (tokens tipográficos) |
| A9 | L | 1.4.13 Contenido al pasar el ratón | Los `title` de la ruta del proyecto y de los botones de icono solo salen con ratón; en táctil y teclado no hay equivalente visible salvo el `aria-label`. | `projects-view.js:30`; `base.css:61` |
| A10 | L | 2.4.11 Foco no oscurecido | Con el cajón abierto, el foco puede seguir en el contenido tapado (P2); con un aviso flotante, el botón del pie de la tarjeta queda detrás del aviso (R6). | `components.css:115`; `queue-bar.js` |

**Teclado.** Los atajos de una tecla (`S`, `N`, `E`, `C`, `F`, `G`, `R`, `?`, `Q`, flechas) cubren votar, elegir,
comparar, cola y ayuda, y ya los prueba `test_keyboard_shortcuts`. Faltan: ir al panel de retoque y al de textos desde
la galería (hoy hay que tabular 80 focalizables), y cerrar el aviso flotante con el teclado sin tabular hasta él.

**Mando.** No hay soporte: el navegador no mapea el mando a foco. Para la Deck en modo escritorio vale el teclado
virtual y el ratón del trackpad; un mapeo propio (`navigator.getGamepads`, D-pad → flechas, A → `Enter`, B → `Esc`)
es una pieza pequeña y aislada que se puede añadir cuando el foco esté bien (P1, P2); no antes.

### 3.4 Idiomas

Paridad **es/en correcta**: 323 claves `ui.*` en cada archivo, ninguna solo en uno, todas las claves usadas en
`gimg/ui/js` e `index.html` existen. Textos sin traducir en código: ninguno. Un detalle: `ui.state.*` se usa en
`aria-label` compuestos a mano (`${id}, ${t(...)}`), que en `en` suena bien y en `es` lee «3, nuevo»: aceptable.

### 3.5 Los diez peores, en una línea

1. R1 Cabecera de 86-139 px a 360 con los selectores de idioma y tema aplastados a 18-28 px (`layout.css:3-17`).
2. R2 El cajón de la cola se monta encima de la cabecera en todos los anchos (`layout.css:30`).
3. R3 El cajón desborda en horizontal en todos los anchos; a 360 pierde la miniatura, los filtros y el «Cerrar» (`layout.css:30-43`, `queue-bar.js:108-149`).
4. P1 La vista de pedido roba el foco a la primera tarjeta al cargar y en cada repintado (`order-view.js:366`, `:311`).
5. P2 El cajón no es diálogo: sin `role`, sin trampa de foco, sin `inert` (`queue-bar.js:33`).
6. A1 Objetivos menores de 24 px: migas, casillas, selectores, chip de medida; «Cerrar» de 44×36 (`base.css:61`, `layout.css:12-17`).
7. R5 Panel de retoque más alto que la ventana a 1440 (Textos cortado) y a varias pantallas de la galería a ≤1000 (`layout.css:75-86`).
8. R6 Avisos flotantes que tapan filas y botones a 360 y la galería a 1440 (`components.css:115`).
9. R4 Editor con asas de 16 px que se pisan a 360 (`components.css:82-98`).
10. A3/A5 Texto de 11-12,5 px y tarjetas sin rol que agrupe sus botones (`layout.css:43,70`, `attempt-card.js:84`).

## 4. Referentes: qué hacen bien y qué nos llevamos

`docs/interfaz/referentes.md` ya cubre estilo por proyecto, reutilizar un intento, coste visible, cola con
parar/reanudar y pestaña de fallidos, plantillas con campos bloqueados y texto en capas. Aquí solo lo que toca a esta
auditoría: disposición, responsive y accesibilidad.

| Referente | Qué hace bien | Qué nos llevamos | Fuente |
|---|---|---|---|
| **Leonardo.ai** | Un panel lateral fijo con los ajustes (modelo, modo rápido/ultra, tamaño, número de imágenes) y una galería que ocupa todo lo demás; las acciones de cada imagen salen al pasar el ratón; biblioteca para operaciones en bloque. Las reseñas de 2026 le reprochan complejidad y que el lienzo no va bien en móvil. | El **panel de retoque como columna lateral pegajosa** con su propio desplazamiento (R5), no un bloque que crece con la página. Y la advertencia: en móvil el lienzo (nuestro editor) no intenta ser el mismo; a 360 el editor va a pantalla completa con las asas grandes o se queda en «mover con flechas y campos». | [Ayuda: cómo generar](https://intercom.help/leonardo-ai/en/articles/8942360-how-to-generate-images-with-leonardo-ai), [reseña 2026](https://dev.to/techsifted/leonardo-ai-review-2026-the-creative-professionals-ai-tool-fc) |
| **Midjourney (web)** | Create es un solo editor: la barra «Imagine» con el prompt y un cajón de ajustes que fija **valores por defecto para los siguientes pedidos**; Organize es la biblioteca con filtros (modelo, proporción, fecha), carpetas y acciones en bloque; dentro de una carpeta, un indicador bajo la barra dice «dónde van» las imágenes. | **Un solo sitio para pedir** (hoy tenemos «Nuevo pedido» y «Retoque» como dos formularios distintos con los mismos campos): el retoque es el mismo panel con el pedido ya cargado. El indicador «dónde va» es nuestra miga del perfil. Los filtros de Organize son nuestras pestañas de la galería, bien. | [Creating on Web](https://docs.midjourney.com/hc/en-us/articles/33390732264589-Creating-on-Web), [Organizing](https://docs.midjourney.com/hc/en-us/articles/33329462451469-Organizing-Your-Creations), [Folders](https://docs.midjourney.com/hc/en-us/articles/34580542725645-Using-Folders) |
| **Ideogram** | El editor de 2026 («Studio», antes Canvas) separa en **capas** el texto de la imagen (texto editable: fuente, tamaño, color), y cada edición apila una versión para volver atrás o comparar. | Para F4e.2c: el panel de texto y tipografía como **lista de capas de texto** a la derecha del escenario (`aside.ed-side`), cada una con fuente, tamaño, color y alineación, y «añadir» y «quitar» como en una lista; las versiones son nuestros intentos y composiciones. | [Editor → Studio](https://docs.ideogram.ai/canvas-and-editing/editor), [Canvas overview](https://docs.ideogram.ai/canvas-and-editing/canvas/canvas-overview), [Tom's Guide](https://www.tomsguide.com/ai/ai-image-video/ideogram-drops-new-canvas-editor-i-got-early-access-and-its-a-game-changer) |
| **Krea** | Lienzo en tiempo real y rediseño de marzo de 2026 con **navegación unificada** y arrastrar y soltar; las reseñas lo notan «apretado». | La navegación unificada: una cabecera que no cambia de altura ni de forma entre pantallas (R1). Y no imitar lo apretado: 44 px y aire. | [Reseña 2026](https://omidsaffari.com/blog/krea-ai-review-2026), [Dupple](https://dupple.com/reviews/krea-ai) |
| **Adobe Firefly** | Texto alternativo automático para cada imagen generada; teclado, lector de pantalla y contraste declarados (WCAG 2.1 AA, con un ACR de 2024 solo parcial); la comunidad pide tamaño de letra del prompt, escala de la interfaz y conmutador claro/oscuro. | El **`alt` de cada intento** con su prompt resumido y estado (hoy el `aria-label` de la tarjeta dice «n, estado»); una **talla de texto** propia (A8) junto a tema e idioma; el conmutador de tema ya lo tenemos. | [Firefly alt text](https://research.adobe.com/news/firefly-alt-text-helping-blind-and-low-vision-creators/), [FAQ](https://helpx.adobe.com/firefly/get-set-up/learn-the-basics/adobe-firefly-faq.md), [ACR 2024](https://www.adobe.com/accessibility/compliance/adobe-firefly-2024-acr), [peticiones](https://community.adobe.com/feature-requests-405/adobe-firefly-accessibility-suggestions-1481412) |
| **Playground** | Editor por capas (texto, imagen, forma), plantillas por categoría y «Extract Text» (2026) que vuelve editable el texto plano de una plantilla. Solo fuentes de terceros: no se verificó en el producto. | Confirma la dirección de F4e.2c (texto como capas editables sobre la plantilla); nada más que llevarse sin verlo. | [fast.io](https://fast.io/resources/playground-ai-review-2026/), [Knowara](https://knowara.com/ai-tools/image/playground-ai-review/) |
| **WCAG 2.2** | Novedades que nos aplican: 2.5.8 tamaño mínimo 24 px (AA), 2.4.11 foco no oscurecido, 2.5.7 alternativa al arrastre, 3.2.6 ayuda consistente. | Las cuatro: A1, A10, A6 y la ayuda `?` en el mismo sitio de la cabecera en todas las pantallas. | [What's new in 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/) |

## 5. Propuesta de mejora por pasos

Cada paso es pequeño, se implementa en un commit y lleva su prueba en `tests/test_ui_browser.py` (la prueba falla
sin el arreglo: `red-without-fix.sh`). Orden por impacto. Los pasos **1 a 5 van antes de F4e.2c**: el panel de texto y
tipografía nace dentro del editor (paso 8) y heredaría la cabecera, el cajón y el foco rotos; arreglarlos después
obliga a tocar dos veces el mismo CSS. Los pasos 6 a 9 pueden ir con F4e.2c o después, según decida la persona.

| Paso | Qué | Arregla | Prueba nueva (`tests/test_ui_browser.py`) |
|---|---|---|---|
| **1. Cabecera fija de una altura** | `.app-header` en rejilla de dos filas a ≤640 (fila 1: marca + herramientas; fila 2: migas con `overflow: hidden; text-overflow: ellipsis` en una línea y `b` con `max-width` en `ch`, no `vw`); `.header-tools` con `flex: none` y `min-width` por `select`; `--header-h` pasa a medirse (`ResizeObserver` → `setVars`) o se fija por punto de corte (56 / 96). Selectores de idioma y tema a 44×44 (icono + `sr-only`) o un solo menú «Ajustes» con los dos y la talla de texto (paso 9). | R1, A1 (selectores, migas), parte de A10 | `test_header_fits_at_360`: a 360×780, `headerH <= 96`, `#lang`/`#theme` ≥ 44×44, migas en una línea, `documentElement.scrollWidth == clientWidth`. |
| **2. Cajón de la cola como diálogo** | `top` del cajón ligado a la altura real de la cabecera (variable del paso 1); `role="dialog"`, `aria-modal`, `aria-labelledby` del `h2`, `inert` en `main` y cabecera mientras está abierto, trampa de `Tab` (la del editor, extraída a `ui/js/lib/focus-trap.js` y reutilizada), foco al `h2` o al primer botón, vuelta a la pastilla al cerrar (ya existe). `.queue-entry` a `64px minmax(0,1fr)` con las acciones en una **segunda fila** (`grid-column: 1 / -1`) y `flex-wrap` en `.row` (filtros, limpiar); `.what` a 13 px. A 360 el cajón ocupa `100vw` y empieza bajo la cabecera. | R2, R3, P2, A10, A3 (`.what`) | `test_queue_drawer_fits_and_traps_focus`: a 360 y 1440, `drawerTop == headerH`, sin `scrollWidth > clientWidth` en `#queue-drawer`, miniatura y filtro «Fallidas» visibles, `Tab` desde el último botón vuelve al primero, `main.inert == true`, `Esc` cierra y enfoca la pastilla. |
| **3. Foco que no se roba** | Al cargar un pedido, foco al `h1` (`tabindex=-1`) y no a la tarjeta; el repintado conserva el foco por `data-attempt` + índice del control (hoy por índice global) y no enfoca nada si el foco estaba fuera de la galería; `#alerts` anuncia «n intentos, m nuevos». Atajos `T` (retoque) y `X` (textos) que enfocan el primer control del panel. | P1, A2, A7, teclado | `test_order_page_keeps_focus`: al abrir, `activeElement` es `h1`; tras votar y repintar, el foco sigue en el mismo botón; `T` lleva al panel de retoque. Se amplía `test_keyboard_shortcuts`. |
| **4. Objetivos de 44 px** | `.btn-icon { min-height: var(--tap) }`; migas con `padding: 12px 4px` y `min-height: 44px`; casillas (`borrador`, atajos) con `label` de 44 px de alto que abarca el texto; chip de medida y botón del aviso con `min-height: 44px` (o a 32 si se decide que el chip no es un objetivo y se le quita el `button`); `select` de plantilla por tarjeta a 44. | A1 | `test_tap_targets_are_44px`: en proyectos, pedido (con panel), cajón y editor, ningún `a, button, input, select, [tabindex="0"]` visible mide menos de 44×44 (lista de excepciones vacía o explícita). |
| **5. Panel de retoque pegajoso y aviso que no tapa** | `.order-panel { position: sticky; top: calc(var(--header-h) + 12px); max-height: calc(100vh - var(--header-h) - 24px); overflow: auto }` a >1000; a ≤1000, botón «Retoque» en la barra de la galería que abre el mismo panel como diálogo lateral (reutiliza la trampa del paso 2) en vez de apilarlo bajo las tarjetas. `.toasts` pasa a esquina inferior derecha a >640 y a **arriba, bajo la cabecera**, a ≤640; cada aviso se cierra con `Esc` cuando tiene el foco y el último se cierra con `Esc` global si no hay diálogo. | R5, R6, A10 | `test_retouch_panel_is_reachable_and_toasts_do_not_cover`: a 1440 el panel no supera la ventana y «Textos» es visible sin desplazar la página; a 360 el botón «Retoque» abre el panel; un aviso no solapa el `rect` de ningún botón del pie de la primera tarjeta. |
| 6. Editor a 360 | A ≤640 el escenario ocupa `100vw − 24px` y `max(50vh, 320px)`; asas de 24 px (`--ed-handle`) con zona de toque de 44 por `::before`; cambio de tamaño con Mayús+flechas y campos `x y w h` en `aside.ed-side` (alternativa de un solo puntero, 2.5.7); etiquetas de caja fuera del escenario (en la lista lateral) cuando el escenario mide menos de 480 px. | R4, A6 | `test_editor_resizes_with_the_keyboard`: Mayús+flecha cambia `w`/`h`; a 360 ningún par de asas de cajas distintas se solapa. |
| 7. Rejillas y puntos de corte | Un solo juego: 640 y 1000 (quitar el 600 y el `.cols-2` duplicado); `.gallery` con `minmax(min(100%, 280px), 1fr)`; `.tabs` y `.gallery-bar` con `flex-wrap`; tarjeta de proyecto sin la ruta en crudo (va al `title` y a un `details` «Carpeta»); `.thumb-empty` sin texto «—» (solo `aria-label`). | R7, R8, R9, R10, A3 | `test_no_horizontal_overflow_anywhere`: recorre las 15 pantallas a 360/768/1024/1440 y exige `scrollWidth == clientWidth` en `html` y en cada `main > *`, `aside`, `dialog[open]`. Esta prueba vigila también todo lo anterior. |
| 8. Tarjeta y semántica | `article` de intento con `role="group"` y `aria-labelledby` (título visible «Intento n · estado»); `alt` de la imagen con prompt resumido y estado (Firefly); `aside` después de `main` en el DOM (orden de encabezados); `h3` de la ayuda fuera del `dl`; `<label>` visible para la cantidad de la tanda; chip de medida sin `tabindex` (su texto ya lo lee el lector dentro de la tarjeta). | A4, A5 | `test_cards_and_dialogs_are_named`: cada `article.card` tiene nombre accesible que empieza por «Intento»; el orden de `h1..h3` del documento es monótono; el campo de la tanda tiene `labels.length == 1`. |
| 9. Talla de texto y mando | Tercer selector en «Ajustes» (`--font-scale` 1 / 1.15 / 1.3 en `rem`, con los tokens pasando de `px` a `rem`); `gamepad.js`: `navigator.getGamepads` → eventos de teclado sintéticos (D-pad → flechas, A → Enter, B → Esc, Y → `?`), activo solo si hay mando. | A8, mando | `test_font_scale_persists`: elegir «grande» sube `font-size` del `html` y sobrevive a recargar. El mando no se prueba en el navegador: queda apuntado como «lo comprueba la persona en la Deck». |

Lo que ya está bien y no se toca: el diálogo de nuevo pedido (R-referencia), los anillos de foco, `sr-only` y
`#alerts`, `prefers-reduced-motion`, los `<dialog>` nativos (renombrar, confirmar, borrar plantilla, caja de luz),
los atajos existentes y la paridad es/en.

### Cómo encajan las pantallas de la hoja de ruta

- **F4e.2c, panel de texto y tipografía** (`docs/plan.md` «Pasos de F4e»): en el editor, `aside.ed-side` pasa a tener
  dos secciones: «Cajas» (la lista actual) y «Textos» (una fila por texto: contenido, fuente del `GET /api/fonts`,
  tamaño, color de la paleta, alineación; «añadir» y «quitar» como botones de la lista; avisos de `overflow` y
  `missingFonts` como `chip-bad` con texto, no solo color). A ≤1000 ese `aside` va bajo el escenario y, con el paso 6,
  cabe. El panel «Textos» del pedido (solo contenido) se queda como está: es el atajo sin abrir el editor.
- **Borrar pedidos** («Pendiente»): botón «Borrar» en la fila del pedido (`.order-row`, columna `auto`) y en la cabecera
  del pedido junto a «Renombrar», con el diálogo «confirmar» que ya existe. Necesita la columna `auto` de la fila sin
  recortar (paso 7).
- **Piezas y marca editables**: las pestañas actuales ya son rutas (`#/p/<p>/piezas`, `/marca`); editar es un
  diálogo por pieza (como renombrar) o el editor de plantilla reutilizado. No toca la cabecera.
- **Nuevo proyecto**: botón en la cabecera de `#/` (`.page-head`) con un diálogo como el de nuevo pedido
  (ruta, nombre, perfiles); hereda el diálogo que ya está bien.
- **Panel del equipo**: un cuarto destino de la cabecera (junto a cola y ayuda) o una pestaña de proyecto; con la
  cabecera del paso 1 cabe a 360 porque las herramientas son iconos de 44 px y las migas van en su fila.
- **Pruebas reales de la interfaz**: los pasos de arriba añaden nueve pruebas; la del paso 7 (`no_horizontal_overflow`)
  es la que vigila el responsive de todo lo que venga después.

### Prototipo

No se ha tocado `docs/interfaz/prototipo/index.html`: lo que propone esta auditoría es CSS y foco sobre la interfaz
real, que ya existe; un prototipo lo duplicaría. Si la persona quiere ver la cabecera del paso 1 y el cajón del
paso 2 antes de decidir, se hace una página de prueba de esas dos piezas solas en el mismo prototipo.

## 6. Decisiones para la persona

**Decidido por la persona el 2026-11-05:** (1) pasos 1-5 antes de F4e.2c; (2) un botón «Ajustes» con menú (idioma, tema
y talla de texto); (3) retoque a ≤1000 como diálogo lateral; (4) el chip de medida es un objetivo: botón de 44 px que
abre el detalle; (5) el mando entra ya; (6) talla de texto propia. Con eso, antes de F4e.2c van los pasos 1-5, el 9
(talla y mando) y el chip como botón del paso 4; los pasos 6-8 (sin la parte del chip) van con F4e.2c o después.

1. **¿Pasos 1-5 antes de F4e.2c?** Es lo que se propone: F4e.2c añade un panel dentro del editor y conviene que el
   editor, la cabecera y el foco estén bien antes. Alternativa: F4e.2c primero y los pasos 1-5 después, aceptando
   retocar dos veces `components.css:82-106`.
2. **Herramientas de la cabecera:** ¿dos selectores de 44 px con icono (idioma, tema) más la talla de texto, o un solo
   botón «Ajustes» que abre un menú con los tres? El menú deja la cabecera más limpia a 360; los selectores son un
   toque menos.
3. **Retoque a ≤1000:** ¿panel como diálogo lateral (botón «Retoque» en la barra de la galería) o seguir apilado bajo
   las tarjetas con un botón «Ir al retoque» que desplace? El diálogo es lo que hacen Leonardo y Midjourney; el
   desplazamiento es más barato.
4. **Chip de medida:** ¿es un objetivo (entonces 44 px y un botón que abra el detalle) o solo información (entonces sin `tabindex` y sin foco, como propone el paso 8)?
5. **Mando:** ¿se hace (paso 9) o se deja para después de F5? Solo tiene sentido si la persona usa la interfaz en la
   Deck en modo juego; en escritorio sobra.
6. **Talla de texto:** ¿tercer ajuste propio o basta con el zoom del navegador?

## 7. Lo que no entra aquí

- Lector de pantalla real (Orca sobre Firefox): se prueba a mano cuando el paso 8 esté hecho.
- Modo de alto contraste (`forced-colors`): no hay regla; los tokens de color dependen de `prefers-color-scheme`.
  Pendiente de ver cuando se toquen los tokens (paso 9).
- Playground: sin verificar en el producto (solo reseñas).
