# Entrega a WMF-imagenes: la marca de Tarkor en el front del generador (2026-11-16)

Para la sesión de World-Maker-Fantasy que trabaje en `image-generator/interfaz/`. Desde aquí no se toca ese repo: esta
entrega dice qué cambiar y por qué; el código lo escribe vuestra sesión, con la confirmación de vuestra persona.
Complementa a [`entrega-hoja-2026-11-12.md`](entrega-hoja-2026-11-12.md), que solo trataba los prompts de `mundo.json`.

Leído el 2026-11-16 en `origin/main` de World-Maker-Fantasy (`b55cdf06`): `image-generator/interfaz/index.html` entero
(409 líneas; último cambio `c96744c8`, 2026-10-26), las rutas de `image-generator/interfaz/servidor.py` y los tokens de
`frontend/src/index.css` (UX-40 y UX-41 ya fusionadas: `gold-*`, `stone-*`, `night-*`, `crystal-deep`, y las piezas en
`frontend/src/assets/interfaz/`).

## 1. Enfoque

**Elegido por el agente (delegado, 2026-11-16).** La persona pidió dar marca al front reutilizando elementos de Tarkor
y delegó el cómo.

- **Es una herramienta de trabajo, no una pantalla del juego:** sobria y legible. Se cambian los colores, la letra de
  los títulos y la cabecera; no se añaden texturas, tablones ni marcos.
- **Un solo tema, oscuro, con los mismos tokens que el juego:** fondo madera 950, paneles madera 900, texto hueso,
  **oro como único acento** («la madera sostiene, el oro remata»: botón principal, perfil activo, barra de progreso,
  filete de la cabecera; muy por debajo del 10 % de la pantalla).
- **Por qué oscuro y no pergamino claro:** las imágenes que se revisan aquí se ven después en el juego sobre
  `wood-950` `#1b130c`; juzgarlas sobre ese mismo fondo es juzgarlas como se verán. Casi todas son escenas oscuras o de
  noche, y un fondo hueso `#f1e4d0` las apaga y cansa más en sesiones largas. La hoja reserva el hueso para documentos
  y para la variante clara del logo, no para interfaz. El tema claro de hoy (`#f6f4ef`) **desaparece**; si vuestra
  persona quiere conservarlo, la sección 8 da su tabla.
- **La cabecera es lo único «fuera del juego»:** noche índigo (`night-950` → `night-900`) con un filete de oro debajo,
  como las piezas de marca. Sin imagen.
- **Cinzel solo en los títulos de sección; Inter en todo lo demás.**
- **Nada encima ni alrededor de la imagen que se está juzgando:** ni filtros, ni velos de color, ni adornos sobre las
  tarjetas de la galería.

## 2. Tokens: cada hex de hoy y su sustituto

El `index.html` usa doce variables, cada una con un valor claro (`:root`) y otro oscuro (`@media (prefers-color-scheme:
dark)`), más dos hex sueltos en `#grande`. Los nombres de las variables **se conservan**: así no cambia ninguna regla
que las use.

| Variable | Claro hoy | Oscuro hoy | Uso en el archivo | Sustituto (token de `frontend/src/index.css`) |
|---|---|---|---|---|
| `--fondo` | `#f6f4ef` | `#1b1916` | fondo de `body`; fondo de campos, botones y tarjetas; `:hover` de la lista | `wood-950` `#1b130c` |
| `--panel` | `#fff` | `#25221e` | fondo de `section` y `aside` | `wood-900` `#241a10` |
| `--texto` | `#26231f` | `#ece6dc` | texto general; `pre` del aviso | `wood-100` `#f1e4d0` (hueso) |
| `--suave` | `#6d665c` | `#a59c8f` | `label`, `small`, `.suave`, datos de la tarjeta, texto del progreso | `wood-300` `#c9a877` |
| `--borde` | `#ddd6ca` | `#3d3832` | todos los bordes: paneles, lista, campos, botones, tarjetas, imágenes | `wood-700` `#46311d`, **solo como filete decorativo** (paneles, filas de la lista, tarjetas, imágenes, `#nuevoForm`); los controles pasan a `--control` (abajo) |
| `--acento` | `#8a5a2b` | `#c98a4b` | botón principal, perfil activo, barra de progreso, marca del elemento activo, distintivo «Actual del juego» | `gold-500` `#b8862b` |
| `--acento-texto` | `#fff` | `#1b1916` | texto sobre `--acento` y sobre el distintivo `--ok` | `wood-950` `#1b130c` (nunca hueso sobre oro: 2,58:1) |
| `--ok` | `#2f7a3d` | `#6cc17a` | «✓ elegida», borde de la tarjeta elegida, distintivo, aviso bueno, «guardada ✓» | `moss-400` `#8fae6a` |
| `--ok-fondo` | `#e3f2e5` | `#1f3324` | fondo del aviso bueno | `iron-800` `#171310` |
| `--error` | `#a33a2a` | `#e07a68` | aviso de error, «Sin imagen» | `danger-400` `#f87171` |
| `--error-fondo` | `#f8e4df` | `#3a211c` | fondo del aviso de error | `iron-800` `#171310` |
| `--hueco` | `#e9e3d8` | `#332f29` | miniatura vacía, fondo de imagen sin cargar, pista de la barra, fila activa de la lista | `wood-800` `#332415` |
| (suelto) | `#000d` | igual | velo de `#grande` (imagen ampliada) | `iron-900` `#0e0b08` al 92 % (`#0e0b08eb`): la hoja prohíbe el negro puro |
| (suelto) | `#eee` | igual | pie de `#grande figure` | `wood-100` `#f1e4d0` |

Variables nuevas (tres):

| Variable | Valor | Para qué |
|---|---|---|
| `--control` | `wood-400` `#a3814f` | borde de `input`, `select`, `textarea` y `button` (hoy usan `--borde`): `wood-700` no llega a 3:1 y el borde es lo que deja ver dónde está el campo |
| `--foco` | `gold-300` `#f2c45a` | `:focus-visible` (hoy el archivo no define foco propio) |
| `--noche-1`, `--noche-2` | `night-950` `#0f1428`, `night-900` `#1a2140` | degradado de la cabecera |

Los dos avisos comparten fondo (`iron-800`) porque el juego no tiene tokens de fondo verde ni rojo oscuros y aquí no se
inventan hex: se distinguen por el color del texto y, propuesto, por un borde izquierdo de 3 px en `--ok` o `--error`.

Bloque propuesto (sustituye al `:root` y al `@media (prefers-color-scheme: dark)` de las líneas 9-14):

```css
:root {
  color-scheme: dark;
  --fondo:#1b130c; --panel:#241a10; --texto:#f1e4d0; --suave:#c9a877; --borde:#46311d; --control:#a3814f;
  --acento:#b8862b; --acento-texto:#1b130c; --foco:#f2c45a;
  --ok:#8fae6a; --ok-fondo:#171310; --error:#f87171; --error-fondo:#171310; --hueco:#332415;
  --noche-1:#0f1428; --noche-2:#1a2140; --velo:#0e0b08eb;
  --titulo:"Cinzel", Georgia, serif;
  --cuerpo:"Inter", system-ui, "Segoe UI", Roboto, sans-serif;
  --mono:"Cascadia Code", "SF Mono", ui-monospace, monospace;
}
```

`color-scheme: dark` hace que los controles nativos (desplegables, flechas de los campos numéricos, barras de
desplazamiento) salgan oscuros también en un sistema en modo claro. En `<head>`, además,
`<meta name="theme-color" content="#1b130c">`, como el juego.

Dónde se usa cada cosa, además de la sustitución directa:

- **Cabecera** (`header`): fondo `linear-gradient(180deg, var(--noche-1), var(--noche-2))`; el `border-bottom` pasa de
  `--borde` a 1 px de `--acento` (el filete de oro, el `.gold-hairline` del juego). El `<span id="mundo">` sigue en
  `--suave`.
- **Controles:** `border-color: var(--control)` en `input, select, textarea` y en `button`. El botón principal y el
  perfil activo siguen con borde `--acento`.
- **Foco:** `:focus-visible { outline: 2px solid var(--foco); outline-offset: 2px; }`.
- **Texto de ayuda de los campos:** `::placeholder { color: var(--suave); opacity: 1; }`.
- **`#grande`:** fondo `var(--velo)`, pie en `var(--texto)`.
- **Prohibidos de la hoja que aquí importan:** `#000` y `#fff` puros, morado o violeta, un segundo acento. El cristal
  azul (`accent-*`) es del juego y de cada mundo: aquí no se usa.

## 3. Tipografía

| Dónde | Hoy | Propuesto |
|---|---|---|
| `body` | `15px/1.45 system-ui, sans-serif` | `15px/1.45 var(--cuerpo)` (Inter 400) |
| `header h1` | 18 px, peso por defecto | `var(--titulo)`, **Cinzel 700**, 18 px, hueso `--texto` |
| `h2` de sección («Elemento», «Elige un elemento», «Imágenes del elemento») | 15 px | `var(--titulo)`, Cinzel 700, 16 px, hueso |
| `.cabecera h2` (`#fichaNombre`: el slug) | 18 px | **Inter 600**, 18 px: Cinzel no tiene minúsculas (las pinta como versalitas) y un slug tiene que leerse tal cual es |
| `h3`, `label`, `button`, `.titulo`, `.datos`, `small` | system-ui | Inter (heredada); pesos y tamaños como hoy |
| `#prompt` | `ui-monospace, monospace`, 13 px | `var(--mono)`, 13 px |
| `.tarjeta details pre`, `.aviso pre` | por defecto | `var(--mono)`, 12 px como hoy |

- El titular en oro tallado (`.title-gold`) es del h1 de la Home del juego, uno por pantalla: aquí **no se usa**; los
  títulos van en hueso.
- El wordmark «TARKOR» nunca se compone con texto (hoja §4): la cabecera dice «Generador de imágenes» en Cinzel, sin
  escribir «TARKOR» al lado. Sí puede ir en el `<title>`: «Tarkor · Generador de imágenes».
- Sin red: Cinzel e Inter no se piden a Google. Están en `frontend/src/assets/fonts/` (cuatro `.woff2` variables,
  OFL, 174 kB en total). Para que este front las cargue hace falta servirlas (sección 6); si no se sirven, las pilas
  de arriba caen a Georgia y a la fuente del sistema, o a Cinzel e Inter si están instaladas, y todo sigue leyéndose.

## 4. Piezas aprobadas que se reutilizan

Las piezas ya están recortadas y en WebP en vuestro propio repo (`frontend/src/assets/interfaz/`, UX-41); la columna
«Origen» es el PNG aprobado en `piloto/tarkor-final/` de galivelop-image-generator, por si hiciera falta rehacerlas.
Destino sugerido para todo: una carpeta `image-generator/interfaz/marca/`, con copias, para que la herramienta no
dependa de la carpeta del juego (`IMG_RAIZ` puede apuntar a otro sitio).

| Pieza | Origen (aprobada) | En WMF hoy | Uso propuesto | ¿Por defecto? |
|---|---|---|---|---|
| Favicon | `docs/marcas/tarkor/logos/tarkor-emblema-simple.svg` (6,2 kB; oro `#b8862b` plano sobre `#1b130c`) | `frontend/public/favicon.svg` sigue siendo el rayo violeta de Vite | `<link rel="icon" type="image/svg+xml">`. **El favicon definitivo de Tarkor es el punto 21 de UX-41** (la gema azul sobre un medallón de oro), en preparación: cuando llegue a `frontend/public/`, este front usa **el mismo archivo**; hasta entonces, el emblema simple | sí |
| Dado | `14-dado-q1068.png` | `dado.webp` (5,4 kB) | sustituye al emoji 🎲 del botón `#azar`, a 20 px, con `alt=""` y el `title` de hoy; el juego ya cambió sus emojis por estas piezas | sí |
| Esquina de oro | `08-esquina-oro-q1005.png` | `esquina-oro.webp` (1,8 kB) | dos esquinas opuestas del panel `#ficha` (arriba a la izquierda y abajo a la derecha), a 20 px, como `.corner-bracket-gold`. **Nunca sobre una tarjeta de la galería** | opcional |
| Cielo | `06-cielo-q998.png` | `cielo.webp` (70 kB) | fondo de la cabecera, bajo el degradado de noche | **no**: la cabecera mide unos 48 px de alto y el cielo no se aprecia; basta el degradado |
| Icono de la herramienta | pedido nuevo (sección 5) | no existe | a la izquierda del `h1`, a 28 px | cuando esté aprobado |

No se reutilizan: las gemas de estado (`estado-hecho`, `estado-error`…: en una herramienta el texto en `--ok` y
`--error` se lee antes que una gema de 16 px), los marcos de retrato y de ranura (irían alrededor de la imagen que se
juzga), el sello y la insignia.

## 5. Pieza nueva: el icono de la herramienta

Un solo pedido, escrito con la receta exacta de las pestañas del juego (`examples/tarkor/orders/ui/11-pestana-mapa.json`:
motivo de oro tallado en un hueco redondo de hierro, croma verde, `count` 3):

- `examples/tarkor/orders/marca/g1-icono-generador.json`: un pincel ancho de pintor, de pie.

**Sin encolar** a fecha de hoy. Sirve para distinguir la herramienta del juego en la cabecera; el front queda completo
sin él. Si se aprueba, llegará recortado como las demás piezas.

## 6. Lo único que no es CSS: servir tres o cuatro archivos

`servidor.py` solo entrega `/` (el `index.html`), `/api/…`, `/ref/…` e `/img/…`. Fuentes, favicon y piezas necesitan
una de estas dos salidas, a elegir por vuestra sesión:

1. **Una ruta estática cerrada** (por ejemplo `/marca/<archivo>`), con lista blanca de nombres y de extensiones
   (`.woff2`, `.svg`, `.webp`) y servida desde `image-generator/interfaz/marca/`. Es la opción limpia, y la única
   razonable para las fuentes.
2. **Incrustar en el HTML** como `data:`: vale para el favicon (6 kB), el dado y la esquina; no para las fuentes.

Sin ninguna de las dos, se aplican igual los tokens y la tipografía de reserva (secciones 2 y 3), que son el grueso
del cambio.

## 7. Contrastes (WCAG 2.1, calculados)

Calculados con la fórmula de luminancia relativa de WCAG sobre los hex de la sección 2; **no medidos en pantalla**.
Umbrales: 4,5:1 para texto, 3:1 para bordes de control, iconos y foco.

| Pareja | Dónde | Contraste | Umbral | |
|---|---|---|---|---|
| `--texto` `#f1e4d0` / `--fondo` `#1b130c` | texto en campos y tarjetas | 14,63 | 4,5 | vale |
| `--texto` / `--panel` `#241a10` | texto en paneles | 13,61 | 4,5 | vale |
| `--texto` / `--hueco` `#332415` | fila activa de la lista | 11,93 | 4,5 | vale |
| `--texto` / `--noche-1` `#0f1428` | título de la cabecera | 14,55 | 4,5 | vale |
| `--texto` / `--noche-2` `#1a2140` | título de la cabecera (abajo) | 12,54 | 4,5 | vale |
| `--suave` `#c9a877` / `--panel` | `label`, `small`, datos | 7,60 | 4,5 | vale |
| `--suave` / `--fondo` | datos en la tarjeta, texto de ayuda | 8,17 | 4,5 | vale |
| `--suave` / `--hueco` | datos en la fila activa | 6,66 | 4,5 | vale |
| `--suave` / `--noche-2` | nombre del mundo en la cabecera | 7,00 | 4,5 | vale |
| `--acento-texto` `#1b130c` / `--acento` `#b8862b` | botón principal, perfil activo, distintivo «Actual del juego» | 5,66 | 4,5 | vale |
| `--acento` / `--panel` | botón principal frente al panel | 5,27 | 3 | vale |
| `--acento` / `--hueco` | relleno de la barra sobre su pista; marca de la fila activa | 4,62 | 3 | vale |
| `--acento` / `--noche-2` | filete de la cabecera | 4,85 | 3 | vale |
| `--control` `#a3814f` / `--panel` | borde de campos y botones | 4,72 | 3 | vale |
| `--control` / `--fondo` | el mismo borde, por dentro | 5,07 | 3 | vale |
| `--foco` `#f2c45a` / `--panel` | anillo de foco | 10,42 | 3 | vale |
| `--ok` `#8fae6a` / `--panel` | «✓ elegida», borde de la tarjeta elegida | 6,85 | 4,5 | vale |
| `--ok` / `--ok-fondo` `#171310` | aviso bueno | 7,41 | 4,5 | vale |
| `--acento-texto` / `--ok` | distintivo «✓ Elegida» | 7,36 | 4,5 | vale |
| `--error` `#f87171` / `--error-fondo` `#171310` | aviso de error | 6,68 | 4,5 | vale |
| `--error` / `--fondo` | «Sin imagen» | 6,63 | 4,5 | vale |
| `--texto` / `iron-800` `#171310` | `pre` del log dentro del aviso | 14,73 | 4,5 | vale |
| `--texto` / `iron-900` `#0e0b08` | pie de la imagen ampliada | 15,65 | 4,5 | vale (sobre el velo opaco; al 92 % varía poco) |
| `--borde` `#46311d` / `--panel` | filete de paneles, filas y tarjetas | 1,40 | no aplica | decorativo: no identifica ningún control (por eso los controles usan `--control`) |

Parejas que **no valen** y que hay que evitar al aplicar:

| Pareja | Contraste | En su lugar |
|---|---|---|
| hueso `#f1e4d0` sobre `gold-500` `#b8862b` | 2,58 | texto `wood-950` sobre oro |
| `wood-500` `#7a5934` como borde de control sobre `wood-900` | 2,69 | `wood-400` (`--control`) |
| `gold-700` `#7a5a1e` como borde o texto sobre `wood-900` | 2,69 | `gold-500` |
| `wood-600` `#5c4126` como borde de control | 1,82 | `wood-400` |

`button:disabled` (opacidad 0,5) queda fuera de los umbrales, como en WCAG.

## 8. Si se quiere conservar un tema claro

No es lo propuesto (sección 1). Si vuestra persona lo pide, es la «pieza clara» de la hoja: fondo hueso `wood-100`
`#f1e4d0`, paneles `wood-200` `#e3cba8`, texto `iron-700` `#221c16` (13,44 y 10,74), texto suave `wood-600` `#5c4126`
(7,48 y 5,97), acento **`gold-900` `#5a3a14`** con texto hueso (8,17; `gold-500` sobre hueso no vale), borde de
control `wood-500` `#7a5934` (5,07 sobre hueso, 4,05 sobre el panel). `moss-600` (3,93) y `danger-600` (3,85) **no
llegan a 4,5** como texto sobre hueso: el estado tendría que ir en texto `iron-700` con un borde de color.

## 9. Qué no cambia

Solo cambia el aspecto. Queda igual:

- **El marcado y los `id`**, de los que depende todo el script, y todos los textos visibles.
- **El script entero:** las rutas (`/api/inicio`, `/api/elementos`, `/api/elemento`, `/api/prompt`, `/api/referencia`,
  `/api/estado`, `/api/generar`, `/api/nota`, `/api/elegir`, `/ref/…`, `/img/…`), el sondeo cada segundo, la clave
  `generador-cfg43` de `localStorage`, la tabla `TAMANOS` y `PERFIL_DEL_TIPO`.
- **La maquetación:** rejilla de dos columnas, corte a 900 px, alturas de la lista, tamaños de miniatura (48 px) y de
  tarjeta (`minmax(280px, 1fr)`), radios de esquina.
- **Las imágenes, sin tratar:** sin `filter`, sin `mix-blend-mode`, sin velo ni marco encima; `object-fit`, `loading:
  lazy`, los cursores de ampliar y reducir, el clic y la tecla Escape de `#grande`, la comparación a dos columnas con
  «Actual del juego».
- **Un solo archivo, sin compilación, sin red exterior:** ni Tailwind, ni CDN, ni Google Fonts. Los tokens se copian
  como hex en el `:root`; si `frontend/src/index.css` cambia un token, este archivo se actualiza a mano.
- **`servidor.py`**, salvo la ruta estática de la sección 6 si se elige: sigue en `127.0.0.1`, una generación a la
  vez, `Cache-Control: no-store`.
- **Los prompts y `mundo.json`:** no pasan por esta entrega.

## 10. Orden recomendado

1. `:root`, `color-scheme` y `theme-color` (sección 2): es casi todo el cambio y no necesita nada más.
2. `--control`, foco y texto de ayuda; cabecera de noche con filete de oro.
3. Tipografía con las pilas de reserva (sección 3).
4. Ruta estática o `data:` (sección 6): fuentes, favicon, dado.
5. Opcional: esquina de oro en `#ficha`; icono de la herramienta cuando esté aprobado.
6. Comprobar en pantalla, en Firefox, lo que aquí solo está calculado: los contrastes de la sección 7 y que el oro no
   pase del 10 % con la galería llena.

## Decisiones del 2026-11-17 (elegido por el agente, delegado)

- **Tema:** solo oscuro. Las imágenes del mundo se ven en el juego sobre fondo oscuro, y juzgarlas en el mismo fondo
  evita sorpresas; la tabla clara de §8 queda como referencia, sin aplicar.
- **Favicon:** el del juego (gema de UX-41, punto 21, cuando se apruebe; mientras, `tarkor-emblema-simple.svg`). El
  icono propio del pincel (`g1-icono-generador`) no se encola.
