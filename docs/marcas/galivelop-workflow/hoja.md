# Hoja de estilo mínima: Galivelop-workflow

> **Dos identidades en esta hoja.** Desde el 2026-11-12 Galivelop-workflow sigue la identidad vigente del Portal con
> su propio acento: papel `#fbfcfd`, tinta `#13212b`, Big Shoulders Display, Literata y JetBrains Mono **heredados**, y
> el acento **`#3D6FD9`** con sus tonos calculados (hondo `#3d6fd9`, variante oscura `#487ce7`). La referencia es
> [`../portal/hoja.md`](../portal/hoja.md) (este repo, `8bb0ae1`), sección «Familia Galivelop: lo que heredan los
> productos» (l.228-374) y su subsección «Decisiones de la persona (2026-11-12)» (l.331-374). **Lo vigente está en los
> cuatro bloques de abajo**, con los mismos títulos y el mismo orden que la hoja del Portal: «Identidad vigente»,
> «Interfaz», «Recursos» y «Familia Galivelop». Lo que se hereda se dice como herencia y remite al Portal; lo propio va
> explícito. Las secciones 0-15, «Contradicciones» y «Lo que enseñó», [`biblia.md`](biblia.md) y [`logos/`](logos/)
> describen la identidad anterior (`#0d1b2a`, Inter/Sora, líneas de luz, FLUX) y se quedan como histórico de r1-r8: no
> se siguen para piezas nuevas.

Commits de referencia: Galivelop-workflow `origin/main` `2e55d66` (2026-11-12, etiqueta `v0.5.2`; antes esta hoja
citaba `7d61089`, y la `v0.5.1` es `eeec886`, 2026-11-05); Portal-Galivelop rama `ccr-47f8fddd-o5ek6p` `6574c4f` y
`main` `e16500f`, leídos a través de `../portal/hoja.md`; este repo `8bb0ae1` (`hojas-repos`). El repo de Workflow se
ha leído **sin modificar nada** (`git show origin/main:<ruta>`).

**Lo primero que hay que saber:** el repo de Galivelop-workflow **sigue sin identidad visual propia** en `2e55d66`:
ni CSS, ni SVG, ni favicon, ni logo, ni imagen en el `README` (`git ls-tree -r origin/main` no lista ningún `.svg`,
`.png`, `.css`, `.webp` ni `.ico`; `docs/design/*.md` es el diseño del flujo `1.0.0`, no diseño gráfico:
`docs/design/README.md` l.1). Lo único con color son las plantillas HTML de su skill `gw-media-content`
(`skills/gw-media-content/template/media/source/card.html` l.12-17), con una paleta genérica «override these to match
the project». Es además **una plantilla que se instala en otros repos** (`docs/es/apply.md` l.107-108: `apply.py`
copia `scripts/`, las skills, los ganchos y el CI): la marca es del repo de Workflow, no de lo que instala (ver
«Recursos» y «Dudas», 5).

---

## Identidad vigente (2026-11-12): lo que gimg necesita

Lo que se aplica a cada pedido nuevo de Workflow. **Toda fila que dice «heredado» vale lo que diga la fila del mismo
nombre del bloque «Identidad vigente» de `../portal/hoja.md` (l.50-63)**: aquí no se copia el texto, para que no haya
dos versiones; si la del Portal cambia, cambia esta. Donde un pedido de `examples/galivelop-workflow/` y esta sección
digan cosas distintas, manda esta sección (los pedidos y la configuración de hoy son de la identidad anterior: ver
«Recursos», «Lo que la configuración no refleja»).

| Campo | Valor | Estado |
|---|---|---|
| Paleta | **Heredado:** cerúleo `#0072a8`, papel `#fbfcfd`, gris tinta `#13212b`; tonos del cerúleo en los grabados; iconos a una sola tinta; versión oscura `#0d171e` / `#e6eef3`. **Propio:** el cuarto color, que en el Portal es el verde alga, aquí es el acento de Workflow, **`#3D6FD9`**, y solo como «a touch of», nunca protagonista. Frase final: «Palette strictly limited to medium cerulean ocean blue #0072a8, off-white #fbfcfd, ink grey #13212b and a touch of cobalt blue #3d6fd9.» El nombre «cobalt blue» es *(suposición: sin ronda)*: el Portal aprendió que el nombre desvía el color («sky blue» dio `#1aa6df`) y aquí hay dos azules en la misma frase (cerúleo `#0072a8`, tono OKLCH 239,7°; acento, 263,1°: 23,4° de distancia; `acento.py "#0072a8"`), así que la primera tanda mide con `gimg measure` si el modelo los separa. `brand.palette` para lo nuevo: `#0072a8`, `#fbfcfd`, `#13212b`, `#3d6fd9`, `#487ce7`, `#e6eef3`, `#0d171e`. **El `#1AA6DF` no es color de Workflow**: es el celeste del Portal | heredado de `../portal/hoja.md` l.52; el lugar del acento, decisión de la persona 2026-11-12 (l.355-357); el hex, decisión 2 (l.353-354; Portal `src/data/proyectos/galivelop-workflow.json` l.7); tonos, `acento.py` |
| Tipografía | **Heredado, sin cambio:** Big Shoulders Display (titulares), Literata (texto), JetBrains Mono (código y datos). Ninguna imagen generada lleva texto: lo pone quien la usa (la web del Portal, el `README`, la tarjeta HTML). Inter y Sora quedan en el histórico | heredado de `../portal/hoja.md` l.53 y l.154-158; decisión 3 (l.355) |
| Modelo y parámetros | **Heredado:** calidad con `zimage-turbo-q6`, 8 pasos, cfg 1.0, euler, base 1024; FLUX solo para bocetos; Qwen-Image solo fotorrealismo (ninguna pieza de Workflow lo pide). Sin prompt negativo efectivo | heredado de `../portal/hoja.md` l.54 |
| Mar y tecnología | **Heredado:** el mar pone el dónde (carta, isobatas, papel, cerúleo), la tecnología el qué. **Propio, el qué de Workflow: el relevo como historial de commits**: una línea de nodos redondos unidos por tramos cortos, una rama que se aparta y vuelve a unirse, y el último nodo con un visto (la revisión); el testigo es un tramo más grueso entre dos nodos. Workflow no añade ningún motivo náutico: las tres excepciones son del Portal | heredado de `../portal/hoja.md` l.55 y l.295; el motivo, propuesta del agente del 2026-11-11 que el Portal ya usa en su recurso 23 (`examples/portal/orders/marca/23-icono-workflow.json`; entregado, q490) |
| Dos registros de dibujo | **Heredado, con los dos bloques literales del Portal.** Línea simple: el motivo solo (icono, símbolo, avatar). Grabado a dos tintas: el motivo sobre el mar de carta, con la línea de nodos como **ruta trazada sobre la carta** (cabecera, social, `og`). No se mezclan en una pieza | heredado de `../portal/hoja.md` l.56 |
| Zonas limpias | **Heredado.** Las piezas anchas de Workflow reservan papel liso para el texto que pone quien las usa: se describe en positivo y al principio, y la trama se confina a la otra parte | heredado de `../portal/hoja.md` l.57 |
| Recuentos | **Heredado:** nunca «exactly N». **Propio:** el motivo se pide «a few round nodes»; lo que sí es significado (una rama que se une, un solo visto en el último nodo) se fija al vectorizar | heredado de `../portal/hoja.md` l.58 |
| Fondo y recorte | **Heredado:** lo que se recorta, sobre croma plano `#00ff00` (el acento es azul: no hace falta `#ff00ff`); matte y trace con `gimg brand`; entregas `-alpha.png` y `.svg` | heredado de `../portal/hoja.md` l.59 |
| Versión oscura | **Heredado:** iconos, símbolo y lockup, sin generar nada (el SVG a `currentColor`); grabados, segunda generación con la misma semilla y las tintas cambiadas. **Propio:** en imagen el acento no cambia de hex (como el cerúleo y el alga en el Portal); `#3d6fd9` da 3,86:1 sobre `#0d171e`, que vale para trazo y no para texto. Ninguna pieza oscura pedida hoy | heredado de `../portal/hoja.md` l.60; ratio, `acento.py` |
| Encuadre | **Heredado:** todo a sangre; el chaflán del cuadrado del logo lo pone el SVG, no el modelo | heredado de `../portal/hoja.md` l.61 |
| Perfiles | **Heredado en nombres y medidas** (`cuadrado` 1024², `icono` 1024 → 512, `social` 1344×704 → 1200×630, `cabecera` 1664×512 → 1600×500), con Z-Image y `draft` 0,5/4. **Propio:** el social preview de GitHub es 1280×640 (`social` con otro destino). Hoy `examples/galivelop-workflow/galivelop-images.json` solo tiene los perfiles de la identidad anterior (`og`, `social`, `square`, `banner`, todos con `flux2-klein-4b-q8`): falta declarar los nuevos | heredado de `../portal/hoja.md` l.62; repo (`examples/galivelop-workflow/galivelop-images.json`, `profiles`) |
| Referencias aprobadas | **Lo que gusta:** el icono de proyecto que el Portal ya publica (recurso 23, q490: tres nodos encadenados y el último con visto). **Heredado:** el registro de grabado que la persona aprobó en q310/q311. **Histórico, no referencia para lo nuevo:** r7 (6/10) y r8 (filamentos de vidrio, árbol de nodos de luz) | `../portal/hoja.md` l.63 y l.212; históricos, sección 6 |

**Cómo se escribe el prompt.** Heredado entero de `../portal/hoja.md` l.65-90 (orden, negaciones solo en el cierre,
ningún color fuera de las tintas, vetos de ética, comprobación antes de encolar). Lo propio:

1. **Sujeto:** el motivo de arriba, dicho sin números («a short commit history: a line of a few round nodes joined by
   short links, one branch leaving the line and joining it again, the last node holding a checkmark tick»).
2. **Frase de paleta:** la de la fila «Paleta», con el acento en el lugar del alga.
3. **Vetos propios, que se suman a los del Portal** (sección 6, vigentes): `robot`, `brain`, `circuit`, `code rain`,
   `capsule`, `pill`, `hand`, `keyboard`, `screen`, `human`, `humanoid`, `spark`, `sparkle`, `magic`. La placa de
   circuito es motivo permitido en el Portal (l.55) y **no en Workflow**: su ética veta lo que sugiera autonomía o
   «magia» de la IA (sección 2). `text`, `letters` y `logo` solo aparecen en el cierre («no text, no letters»).
4. **Prompts propuestos** (texto, sin encolar; los pedidos van en `examples/galivelop-workflow/orders/`, fuera del
   alcance de este cambio):
   - **Símbolo (boceto, perfil `cuadrado`, sobre croma):** «Monogram logo, centred: the capital letters G and W drawn
     as one continuous stroke of even width with rounded caps and joins, on a solid flat square. Flat vector
     pictogram, geometric, no shading, no hatching, no texture, no gradients, no glow, no other text, no watermark,
     no border, no frame, the square on a plain flat solid bright green #00ff00 background. Palette strictly limited
     to cobalt blue #3d6fd9 for the square and white #ffffff for the stroke.» El chaflán de 28/128 y el trazo de
     12/128 se fijan al vectorizar. *(suposición: sin ronda; el `01-logo` del Portal sigue en boceto, q133)*
   - **Icono de proyecto:** el del pedido 23 del Portal, ya entregado; no se rehace.
   - **Cabecera y social (grabado):** «A sea chart seen from above with a route traced across it as a short commit
     history: a line of a few round nodes joined by short links, one branch leaving the route and joining it again,
     the last node holding a checkmark tick, in the right two thirds of the sheet; the left third is plain flat
     off-white paper, open and unmarked. [bloque de grabado del Portal, l.56]. No photographic rendering, no glow, no
     text, no letters, no numbers, no watermark, full-bleed edge to edge, no border, no frame. [frase de paleta].»
     *(suposición: sin ronda)*

**Dudas que decide la persona** (2026-11-12), con recomendación:

1. **El vivo y el hondo de Workflow son el mismo hex.** El método (l.343, punto 5) lo dice así: `#3D6FD9` ya da
   4,57:1 sobre el papel, luego el hondo es el vivo. Consecuencia: las reglas del **vivo** del Portal no se cumplen
   al pie de la letra, porque están escritas para un vivo claro (`#1aa6df`): sobre el acento de Workflow el texto va
   en **blanco** (4,69:1) y no en tinta (3,50:1), y «texto blanco sobre el acento vivo» (prohibido de familia, l.302)
   aquí es lo correcto. **Recomendación:** aceptarlo y que Workflow tenga dos hex (`#3d6fd9` y `#487ce7`) y no tres;
   la alternativa, un vivo más claro, contradice que el vivo es el hex de hoy.
2. **Cerrada. Símbolo del logo: decidido por la persona (2026-11-12), monograma «GW»** en una tinta sobre el cuadrado con chaflán de 28/128 en el hondo `#3d6fd9`; los logos anteriores (degradado, `rx` 30, Sora) son históricos y no se copian a su repo. Los nodos del icono 23 se quedan como icono de proyecto y motivo de las ilustraciones. **Dependencia:** `gimg brand` no tiene aún la orden que monte el cuadrado con chaflán.
3. **Acento secundario en la interfaz propia.** La decisión 3 pone el acento del producto donde el Portal usa el alga
   en las piezas generadas y junto al Portal; no dice qué hace de secundario dentro de la interfaz de Workflow
   (avisos suaves, «en desarrollo»). **Recomendación:** se hereda el alga del Portal (`#5d7a6a` / `#8fb09e`) sin
   inventar otro hex; `--ok-texto` ya sale de ella.
4. **Ámbar del testigo, verde y rojo de los diagramas.** La identidad anterior daba significado a `#f2b34a`
   (testigo), `#4cc38a` (ok) y `#f0716a` (rechazo), los de los diagramas `gw-*.svg` del Portal. La familia hereda
   `--ok-texto` y `--peligro` y no tiene ámbar. **Recomendación:** en lo nuevo, «hecho» y fallo con los tokens del
   Portal, y el testigo se dice con forma (el tramo más grueso), sin color propio; los diagramas `gw-*.svg` son del
   Portal y los rehace su sesión.
5. **¿La marca viaja con lo que Workflow instala en otros repos?** **Recomendación: no.** El logo, `docs/marca.md` y
   la nota de paleta se quedan en el repo de Workflow, fuera de `scripts/`, `skills/`, `templates/` y `hooks/`; las
   plantillas de `gw-media-content` siguen con su paleta genérica, porque cada proyecto que adopta el flujo pone la
   suya (`card.html` l.12). Detalle en
   [`../../propuestas/galivelop-workflow/entrega-hoja-2026-11-12.md`](../../propuestas/galivelop-workflow/entrega-hoja-2026-11-12.md).
6. **El nombre en mayúsculas.** El lockup común escribe «GALIVELOP-WORKFLOW» en Big Shoulders Display 800 y en
   `currentColor` (decisión 4, l.358-374); la ficha de la identidad anterior decía «w minúscula, sin mayúsculas
   sostenidas» y el lockup de r7 iba en dos tonos. **Recomendación:** manda la decisión 4 en el lockup; en texto
   corrido el nombre sigue siendo «Galivelop-workflow», como en el título del `README` (l.1).

---

## Interfaz de Galivelop-workflow: tokens y reglas (2026-11-12)

Workflow no tiene hoy interfaz con CSS propio. Estos tokens son para lo que sí pinta color: las tarjetas HTML de
`gw-media-content` **del propio repo de Workflow**, su `README`, su ficha en el Portal y, cuando exista, el Management
Center (la `1.0`: `README.es.md` l.9-12; `docs/design/G-mmc.md`). **Todo token que no está en la tabla se hereda del
Portal sin cambiar un valor** (`../portal/hoja.md` l.127-152 y «Qué se copia tal cual», l.236-246): `--papel`,
`--superficie`, `--fondo-alterno`, `--tinta`, `--tinta-2`, `--texto-3`, `--filete`, `--reticula`, `--peligro`,
`--ok-texto`, `--noche`, `--velo*`, `--sombra`, `--chaflan*`, `--reticula-paso`, `--curva`, `--transicion`.

Lo propio son los papeles del acento. Los nombres de token son los del Portal con `acento` en lugar de `celeste`
(propuesta: Workflow no tiene CSS que los fije). Los ratios son WCAG 2.x calculados sobre los hex, no medidos en
pantalla.

| Token | Claro | Oscuro | Papel que hace | Contraste (claro / oscuro) | En el Portal |
|---|---|---|---|---|---|
| `--acento` (vivo) | `#3d6fd9` | `#3d6fd9` | Marca, foco (`outline` 2 px), punto de estado, base del tinte | sobre papel 4,57 / 3,86; blanco encima 4,69; tinta encima 3,50 | `--celeste` `#1aa6df` (2,70 / 6,53) |
| `--acento-hondo` | `#3d6fd9` (**es el vivo**: ya cumple) | `#3d6fd9` | Bloques grandes con texto blanco (también en oscuro), cuadrado del logo, texto de acento y enlaces en claro | sobre papel claro 4,57 (AA); blanco encima 4,69 | `--celeste-hondo` `#0072a8` (5,15; blanco 5,29) |
| `--enlace` | `--acento-hondo` | `#487ce7` (**variante oscura**, OKLCH L 0,604) | Texto de acento y enlaces | 4,57 / 4,59 sobre `#0d171e`. **Límite:** sobre la superficie oscura `#111f29` da 4,24 y sobre `#16242e` 4,01 (< 4,5): en fichas y bandas oscuras el texto de enlace va en tinta o subrayado, y el acento queda en borde, subrayado o punto. Tono que haría falta, mismo método (`acento.py`): `#5185f1` (4,51 sobre `#16242e`, 4,77 sobre `#111f29`, 5,16 sobre `#0d171e`; blanco encima 3,51), calculado, no adoptado | `--celeste-hondo` / `#5cc8f2` (5,15 / 9,49) |
| `--tinte` | acento al 12 % (`#e4ebf9` sobre papel) | acento al 18 % (`#162740`) | Plano translúcido: hover, chips, píldoras | tinta sobre tinte 13,71 / 12,79 | 14,25 / 11,65 |
| Isobatas sobre el bloque | blanco al 20-50 % sobre `#3d6fd9` | igual | Textura del bloque grande | — | mismos porcentajes |
| Acento secundario | **heredado [P]:** `--alga` `#5d7a6a` | `#8fb09e` | «En desarrollo», avisos suaves | 4,59 / 7,66 | el mismo (ver «Dudas», 3) |

**De dónde salen los hex** (método de `../portal/hoja.md` l.333-345; nada se elige a ojo):

```
$ python3 docs/marcas/galivelop-workflow/acento.py
vivo   #3d6fd9  OKLCH L=0.564 C=0.172 h=263.1
hondo  #3d6fd9  (es el vivo: ya cumple)
oscuro #487ce7  (L=0.604 C=0.172)
  4.57:1  vivo sobre papel #fbfcfd
  4.69:1  blanco sobre vivo
  3.50:1  tinta #13212b sobre vivo
  3.86:1  vivo sobre papel oscuro #0d171e
  4.57:1  hondo sobre papel #fbfcfd
  4.69:1  blanco sobre hondo
  3.86:1  hondo sobre papel oscuro #0d171e
  4.59:1  oscuro sobre papel oscuro #0d171e
  4.59:1  papel oscuro #0d171e sobre oscuro (texto encima)
 13.71:1  tinta sobre tinte claro #e4ebf9 (vivo al 12 %)
 12.79:1  tinta clara #e6eef3 sobre tinte oscuro #162740 (vivo al 18 %)
  1.00:1  vivo frente a hondo
```

[`acento.py`](acento.py) (solo stdlib) sigue el método paso a paso: OKLab de Ottosson, `h` y `C` fijos, `L` en pasos
de 0,005, contraste sobre el hex redondeado a 8 bits. La variante oscura sale en el octavo paso (L 0,564 → 0,604) sin
salirse de sRGB. Con otro hex como argumento reproduce los ratios de la tabla del Portal (l.321-326): `#1aa6df` da
2,70 / 2,78 / 5,91 / 6,53 y `#7C5CD6`, 4,69 / 4,82.

**Dónde se aparta Workflow de la relación del Portal, y por qué** (todo sale del método, no de una elección):

| Relación del Portal (`../portal/hoja.md` l.258-262) | En Workflow | Motivo |
|---|---|---|
| El vivo no lleva texto blanco ni se usa para texto sobre papel; encima, solo tinta a ≥ 4,5:1 | Al revés: blanco encima 4,69; tinta encima 3,50; como texto sobre papel, 4,57 | El vivo es el hondo (punto 5 del método): hace los dos papeles con las reglas del hondo. Ver «Dudas», 1 |
| El vivo, ≥ 4,5:1 sobre el papel oscuro | 3,86: en oscuro el vivo solo marca foco, punto y trazo (≥ 3:1 de elemento gráfico); el texto va en `#487ce7` | El método no mueve el vivo |
| El hondo se oscurece en oscuro y el blanco encima da ≥ 7:1 | El hondo no cambia; blanco encima 4,69 (AA) | Decisión 1 (l.349-351): un producto lleva una sola variante oscura, la de texto |
| Enlace en oscuro ≥ 7:1 | 4,59 | El método fija el umbral en 4,5:1 (l.340-341) |

**Tipografía por papel.** Heredada sin cambio (`../portal/hoja.md` l.154-158): títulos en Big Shoulders Display 800
(700 en h4), mayúsculas, tracking 0,01 em; texto en Literata 400/600 a 17 px / 1,6; datos (órdenes, rutas, versiones,
`Siguiente:`) en JetBrains Mono 500 a 12 px, mayúsculas, tracking 0,06 em. Las tres, OFL. **Ninguna está instalada en
este equipo** (`~/.local/share/fonts/galivelop/` solo tiene Inter, Sora y las de otras marcas): hace falta el `.ttf`
variable de Big Shoulders Display para `gimg brand wordmark`.

**Reglas de interfaz.** Las once del Portal (`../portal/hoja.md` l.160-178), heredadas: tema claro por defecto; sin
resplandores, desenfoques ni degradados; esquinas rectas o con chaflán de 45° arriba a la derecha (28 / 14 / 10 px);
líneas antes que sombras; datos en monoespaciada; el acento en bloques grandes y planos; retícula de 24 px a la
vista; numeración real; movimiento de 200 ms y 2-3 px; contraste AA; los diagramas siguen la misma hoja. Lo propio
es la regla 10: **sobre el acento de Workflow, texto blanco** (4,69:1). Nada las comprueba en el repo de Workflow (no
tiene CSS); el `marca.test.ts` del Portal comprueba su ficha.

**Los logos de `logos/` no las cumplen:** `galivelop-workflow-a.svg` y `-b.svg` son baldosas con degradado y `rx` 30,
y los `*-lockup.svg` llevan Sora. Son de la identidad anterior y quedan como históricos (`../portal/hoja.md` l.374).

## Recursos: entregado, cancelado y pendiente (2026-11-12)

| Recurso | Estado | Dónde está o iría | Fuente |
|---|---|---|---|
| Icono de proyecto (recurso 23 del Portal) | **Entregado** (q490): tres nodos encadenados, el último con visto; línea simple, una tinta | Portal `public/proyectos/galivelop-workflow/icono.svg` | `../portal/hoja.md` l.212; `examples/portal/orders/marca/23-icono-workflow.json` |
| Símbolo del logo (cuadrado plano `#3d6fd9`, chaflán 28/128, monograma «GW» de trazo 12/128 en una tinta; decidido por la persona, 2026-11-12) | **Pendiente**: sin generar; depende de la orden nueva de `gimg brand` que monte el cuadrado con chaflán. Los `logos/galivelop-workflow-{a,b,c,d}.svg` son históricos | `docs/marcas/galivelop-workflow/logos/` y, copiado, `docs/marca/` del repo de Workflow | regla heredada, `../portal/hoja.md` l.290; «Dudas», 2 |
| Símbolo en negativo y a `currentColor` | **Pendiente**: sale del SVG del símbolo, sin generar | igual | `../portal/hoja.md` l.60 |
| Lockup horizontal y vertical | **Pendiente**: necesita el símbolo y el `.ttf` de Big Shoulders Display. Órdenes en «Familia Galivelop», punto 4 | igual; `README` de Workflow | decisión 4, `../portal/hoja.md` l.358-374 |
| Social preview de GitHub, 1280×640 | **Pendiente** con la identidad vigente. Las de r4-r8 son de la anterior | ajustes del repo en GitHub (no es un archivo: no se comprueba desde el repo) | sección 11 |
| `og.jpg` de la ficha del Portal (recurso 24) | **Pendiente** | Portal `tools/og/fuentes/galivelop-workflow/og-fuente.png` | `../portal/hoja.md` l.213 |
| Cabecera del `README`, 1600×500 (grabado) | **No pedida**; se puede generar | `docs/marca/` del repo de Workflow | «Cómo se escribe el prompt», 4 |
| Avatar 512 | **Pendiente**: el símbolo rasterizado. El de r5 es el logo `a`, histórico | GitHub, Discord | sección 9 |
| Tarjetas de redes (1200×675) | **No las hace `gimg`**: las renderiza `gw-media-content-now` desde HTML. Paleta: la nota del repo de Workflow (ver abajo) | `docs/media/` del repo de Workflow | Workflow `skills/gw-media-content/note.md` l.10, l.15; `card.html` l.8 |
| Portada de la ficha en el Portal | Publicada con la identidad anterior *(suposición: `public/proyectos/galivelop-workflow/portada.webp`)*; la decide el Portal | Portal | sección 8 |
| `banner` 1600×640, `og`/`cuadrado`/`vertical`/`cabecera` de r4-r8 | **Históricos**: identidad anterior | `piloto/` (fuera de git) | secciones 9 y 12 |

**Paleta para las tarjetas de `gw-media-content` del repo de Workflow** (sustituye a la propuesta del 2026-11-04 de
«Contradicciones», 1, que usaba `#0d1b2a` y `#38b6e8`). Las variables son las de `card.html` l.13-17; los valores, los
tokens heredados y el acento calculado:

```
Palette: --background: #fbfcfd; --surface: #ffffff; --border: #b9cbd6; --text: #13212b; --muted: #4a5c69;
         --accent: #3d6fd9; --accent-text: #ffffff; --good: #3f5a4b; --bad: #a3135f;
         --font: "Literata", serif; --mono: "JetBrains Mono", monospace
```

`.brand` (l.22) pinta el nombre en `--accent` a 20 px y 700: `#3d6fd9` sobre `#fbfcfd` da 4,57:1, pasa. Esa nota
(`.claude/gw/gw-media-content.md`) es **del repo de Workflow**, no de la plantilla que instala.

**Lo que la configuración de este repo no refleja** (fuera del alcance de este cambio; va a la bitácora):
`examples/galivelop-workflow/galivelop-images.json` tiene `brand.palette` y los cuatro perfiles de la identidad
anterior, con FLUX; `prompts/`, `orders/`, `plantillas/` y `piezas.json` también; `tests/test_examples.py` l.312 exige
la copia de `galivelop-workflow-b-lockup.svg` (histórico) en `examples/galivelop-workflow/logos/`. No hay pedidos con
la identidad vigente.

## Familia Galivelop: lo que hereda y cómo lo cumple

Las seis comprobaciones de «Cómo se comprueba una hoja de producto» (`../portal/hoja.md` l.307-315), una a una:

| # | Comprobación | En Workflow | Resultado |
|---|---|---|---|
| 1 | Tres hex del acento calculados, con ratios; ninguno bajo 4,5:1 donde el método lo exige | vivo `#3d6fd9`, hondo `#3d6fd9` (4,57 sobre `#fbfcfd`; blanco encima 4,69), oscuro `#487ce7` (4,59 sobre `#0d171e`); salida de `acento.py` arriba | **pasa** (dos hex distintos: «Dudas», 1) |
| 2 | Papel, tinta, filete, retícula, tipografías, chaflanes y retícula de 24 px, valor por valor | Esta hoja no los copia: remite a la tabla del Portal | **pasa por remisión** |
| 3 | Frase de paleta del Portal con el acento en el lugar del alga; ningún prompt nombra otro color | Fila «Paleta» y prompts propuestos. Los prompts de `examples/galivelop-workflow/prompts/` son históricos y nombran otros | **pasa en lo vigente**; ningún pedido nuevo encolado |
| 4 | Logo: cuadrado plano del acento hondo, chaflán 28/128, trazo 12/128, salido de gimg | No existe: los de `logos/` llevan degradado y `rx` 30 | **no pasa: pendiente** |
| 5 | Iconos de una tinta, sin relleno, nodos huecos, legibles a 24 px | El 23 (q490), entregado por la serie del Portal; Workflow no tiene serie propia | **pasa** con el único icono que hay |
| 6 | Nada de «Prohibido en toda la familia» (l.297-305) | Lo vigente, nada, con una salvedad: «texto blanco sobre el acento vivo» («Dudas», 1). Los logos históricos tienen degradado y esquinas redondas | **pasa en lo vigente**, con la salvedad |

**Lo que se hereda, por aspecto** (`../portal/hoja.md` l.286-295), y lo propio:

1. **Logo.** Heredado: cuadrado de color plano, chaflán de 28/128 arriba a la derecha puesto por el SVG, monograma de
   trazo 12/128 en una tinta, generado sobre croma `#00ff00` y vectorizado con `gimg brand trace`. Propio: el hex del
   cuadrado (`#3d6fd9`) y el dibujo (monograma «GW»; «Dudas», 2).
2. **Iconos.** Heredado: línea simple, un grosor, remates redondos, sin relleno ni trama, una tinta, nodos huecos,
   `gimg brand trace --mode color --matte --dp-tol 0.5 --palette '#13212b,#fbfcfd'`, a `currentColor`. Propio: el
   motivo (nodos, ramas, visto, el tramo grueso del testigo). Una serie se usa entera, sin mezclarla con lucide.
3. **Ilustración.** Heredado: grabado de carta náutica a dos tintas con el bloque literal, Z-Image, 120-200 palabras,
   cierre y frase de paleta. Propio: el sujeto (la ruta de commits sobre la carta) y el cuarto color.
4. **Lockup.** Heredado entero, con las medidas del Portal (l.362-367): nombre a 0,45 `S` de alto en horizontal y
   1,6 `S` de ancho en vertical, hueco y margen de 0,25 `S`, mínimo `S` ≥ 32 px (horizontal) y ≥ 48 px (vertical);
   por debajo, el símbolo solo hasta 16 px. Nombre en `currentColor`, nunca en el acento. Propio: el símbolo y el
   texto. Órdenes (a falta del símbolo y de la fuente):

   ```
   gimg brand wordmark "GALIVELOP-WORKFLOW" --font <BigShouldersDisplay variable .ttf> --weight 800 --spacing 0.01 -o wordmark.svg
   gimg brand lockup simbolo.svg wordmark.svg --layout h --cap 0.45 --gap 0.25 --margin 0.25 -o galivelop-workflow-lockup-h.svg
   gimg brand lockup simbolo.svg wordmark.svg --layout v --width 1.6 --gap 0.25 --margin 0.25 -o galivelop-workflow-lockup-v.svg
   ```

   El nombre tiene 18 caracteres: en horizontal el lockup sale muy ancho, y el `README` puede preferir el vertical o
   el símbolo solo. Eso se ve al generarlo; las medidas no se tocan sin decisión de la persona.
5. **Composición y prohibidos.** Heredados sin cambio (l.294, l.297-305). Se suman los vetos de la ética de Workflow
   (sección 2): nada que sugiera autonomía de la IA.

---

## Histórico: identidad anterior (r1-r8)

Todo lo que sigue, hasta el final, es la hoja aprobada el 2026-11-04 con la identidad anterior. **No se sigue para
piezas nuevas.** Sigue valiendo, y lo usan los bloques de arriba: la sección 1 (propósito, lema, tono, idiomas, campo
semántico), la sección 2 (ética), los vetos propios de la sección 6 y los textos de la sección 10. Las líneas del
repo de Workflow se han vuelto a comprobar en `2e55d66`: el lema sigue en `AGENTS.md` l.24, `templates/es/AGENTS.md`
l.27 y l.32, `templates/es/GLOSSARY.md` l.11 y `templates/es/log.md` l.4; en `README.es.md` pasa de l.43 a **l.47**,
el estado es ahora «`0.5.2`, etapa 1 en rodaje» (l.9, antes «0.4.3») y `.claude-plugin/plugin.json` dice `0.5.2`; la
paleta de `card.html` (l.13-15) no ha cambiado. Donde abajo se lee `7d61089`, la lectura es de esa fecha.

**Propuesta** (2026-11-04), **Aprobada por la persona el 2026-11-04**; segundo caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md) (F2.12), rellenada
tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y con su misma forma. Complementa a
[`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita, campo a campo y en el orden de la
plantilla. Estados como en [`../README.md`](../README.md): sin marca sale de un repo (ruta en la sección 13); **heredado de
`<marca>`** sale del repo de la marca paraguas (el Portal) leído a través de la biblia; **[P]** es propuesta pendiente de la
persona, con su porqué en la misma celda; *(suposición)* se comprueba en una ronda; «no hay» solo donde la plantilla lo admite.

Commits de esa lectura: Galivelop-workflow `7d61089` (`main`, 2026-11-04; la biblia cita `56212e8`, anterior); este repo
`78f0083` (`f2-motor`); Portal-Galivelop `aa76b34` (vía `biblia.md` §10 y `docs/marcas/portal/biblia.md`).

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Galivelop-workflow»: G mayúscula, guion, w minúscula, de una pieza. Así va en el título del `README.md`, en `plugin.json` («Galivelop-workflow served from its own repository») y en el lockup. En los textos del propio repo se le llama «el flujo» | Workflow (`README.md` l.1, `README.es.md` l.1, `.claude-plugin/plugin.json`) |
| Nombre en código | Obl. | `galivelop-workflow` | repo (`examples/galivelop-workflow/galivelop-images.json`, `name`); coincide con `name` de `.claude-plugin/plugin.json` de Workflow |
| Fuente de verdad | Rec. | Galivelop-workflow `main` `7d61089` (voz, propósito, licencia, canales); Portal `aa76b34` (paleta, tipografía, baldosa, acento); este repo `78f0083` (prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a workflow pese a la nota de las líneas); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2 | repo (`docs/records/contenido/r1-fondos.md` l.52-53; `docs/marcas/README.md`, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`, **con tres valores propios justificados**: fondo `#0d1b2a` (no `#06121c`), texto `#eef6fb` (no `#eaf4fa`) y titular Inter (no Sora), porque la biblia toma la paleta y la letra de los siete diagramas `gw-*.svg` que el Portal ya publica del flujo: son lo más parecido a una marca que Workflow tiene. Baldosa del logo, la de la familia (`rx` 30/128, trazo 12) | heredado de Portal-Galivelop `aa76b34` (`docs/diagramas/gw-*.svg`, vía `biblia.md` §2-§3 y §10) |
| Hereda de | Opc. | **Vigente:** [`../portal/hoja.md`](../portal/hoja.md), bloques «Identidad vigente» y «Familia Galivelop» (2026-11-12), como dicen los bloques de arriba. **Histórico (piezas r1-r8):** Portal-Galivelop `aa76b34` (leído solo a través de `biblia.md` §10 y `docs/marcas/portal/biblia.md`) | repo |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «La forma de trabajar del taller Galivelop con agentes de programación (primero Claude Code), fuente única y versionada de sus skills, ganchos, scripts y plantillas»; para quien trabaja por relevos con agentes y no quiere perder nada entre sesiones | Workflow (`README.es.md` l.5-8; `.claude-plugin/plugin.json`, `description`) |
| Lema | Rec. | «Lo que no está subido no existe» | Workflow (`AGENTS.md` l.24; `README.es.md` l.43; `templates/es/log.md` l.4; `templates/es/AGENTS.md` l.27) |
| Tono | Rec. | técnico, sobrio, pragmático; dice lo que hace y lo que falta («Estado: 0.4.3, etapa 1 en rodaje»); desconfía de la buena voluntad y confía en el script («Las reglas las hace cumplir un script, no la buena voluntad del agente»); agradece a quien enseñó (sección «Agradecimientos», `CREDITS.md`). No es: vendedor, épico, «mágico» | Workflow (`README.es.md` l.9, l.30-32, «Calidad primero», «Agradecimientos»; `CREDITS.md`) |
| Idiomas | Opc. | `es, en`: el repo publica todo en los dos (`README.md` en inglés, `README.es.md`; `docs/en/`, `docs/es/`; plantillas `templates/{es,en}/`), y su skill de redes da por defecto `Languages: es, en` con `es` primero. Las piezas de r4-r5 van solo en `es`; la versión `en` de cada pieza está sin hacer | Workflow (`README.md`, `README.es.md`, `skills/gw-media-content/note.md` tabla «Key»; `.claude/gw.json` `language: es`) |
| Campo semántico | Opc. | dentro: relevo, bitácora, punto estable, check en verde, marca de revisión, rama protegida, subir, fusionar, retro, testigo, «Siguiente:»; fuera: magia, autonomía, robot, «el agente decide» | Workflow (`templates/es/GLOSSARY.md` l.11 «Relevo»; `AGENTS.md` §«Relevos»; `README.es.md`); «testigo» y la lista «fuera», `biblia.md` §6 |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | robots, cerebros luminosos, circuitos brillantes, lluvia de código, humanoides, manos de robot sobre teclados, chispas de IA; nada que sugiera autonomía total de la IA ni «magia»: el humano decide y revisa | repo (`docs/plan.md` l.633-637 «Estilos por proyecto», Galivelop-workflow; `biblia.md` §1). El principio sale de Workflow (`README.es.md`: «A la rama protegida solo se va con la confirmación de la persona»; «Nada se aplica sin confirmación»), que no tiene texto de ética visual |
| Personas y rostros | Rec. | nunca personas, manos ni rostros (vetados `hand`, `human`, `humanoid`, `face`) | repo (`biblia.md` §7; `docs/plan.md` l.636) |
| Promesas | Rec. | nada de «automático» ni «sin supervisión»; no afirmar la etapa 2 (instalación sin IA) como hecha mientras el README la dé por «más adelante»; nada de cifras de ahorro de tokens que no salgan de `gw-opt-tokens` (la propia skill de redes exige que cada número venga de `figures.py` o de un archivo y línea); nada de precios ni fechas | Workflow (`README.es.md` «Cómo se aplica», etapa 2; `skills/gw-media-content/SKILL.md` l.14-16) |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. (familia Galivelop, con valor propio) | oscura (por defecto) `#0d1b2a`, el fondo de los diagramas del Portal; alterno `#06121c` (fichas, el fondo del Portal). Clara `#f6fafd` **[P]**: ninguna pieza clara hecha; se propone por si una pieza va sobre la web clara del Portal | heredado de Portal-Galivelop `aa76b34` (`docs/diagramas/gw-*.svg`, vía `biblia.md` §2); repo (`galivelop-images.json` `brand.palette`; `piezas.json` `velo`) |
| Texto | Rec. (familia Galivelop, con valor propio) | `#eef6fb` sobre oscuro (secundario `#8a9bb0`); `#0a1a28` sobre claro **[P]** (va con la pieza clara) | heredado de Portal-Galivelop `aa76b34` (vía `biblia.md` §2); `#eef6fb` es el `color_texto` de las cuatro piezas de `piezas.json` y está en `brand.palette` |
| Acento | Obl. | `#3D6FD9`: el acento que el Portal da al proyecto; manda en el logo (baldosa), el nombre del lockup y el símbolo suelto. **En la imagen generada no aparece:** allí el color que hace de marca es el celeste `#38b6e8` de las líneas, con ámbar y verde en los nodos (ver «Resto» y «Cambios que pediría a la plantilla») | heredado de Portal-Galivelop `aa76b34` (`src/data/proyectos/galivelop-workflow.json`, vía `biblia.md` §10); repo (`logos/galivelop-workflow-a.svg`, `-lockup.svg`) |
| Resto de la paleta | Rec. | celeste `#38b6e8` (líneas de luz, lo propio de galivelop en los diagramas); ámbar `#f2b34a` (el testigo del relevo; lo de Matt Pocock en los diagramas); verde `#4cc38a` (check, «subido», ok); rojo `#f0716a` (rechazo del gancho; solo semántico, nunca decorativo); blanco `#FFFFFF` (trazo del símbolo); texto 2 `#8a9bb0`. `brand.palette` de hoy lleva 5: `#0d1b2a`, `#38b6e8`, `#f2b34a`, `#4cc38a`, `#eef6fb`; **faltan** `#3D6FD9` y `#FFFFFF` (los del logo) y `#8a9bb0` | heredado de Portal-Galivelop `aa76b34` (`docs/diagramas/gw-*.svg`, vía `biblia.md` §2); repo (`galivelop-images.json`, de `prompts/r2-hex.txt`) |
| Combinaciones | Rec. | oscura: `#0d1b2a` + texto `#eef6fb` + velo `#0d1b2a:0` en `og` (contraste sobra) y `#0d1b2a:0.3` en `cuadrado`, `vertical` y `cabecera`; sobre imagen: el logo siempre en su baldosa (nunca el símbolo suelto sobre la ilustración), texto en la mitad que los prompts dejan vacía; acentos en la imagen en este orden de peso: celeste, ámbar, verde. Clara **[P]**: `#f6fafd` + `#0a1a28` + acento `#3D6FD9`, ámbar solo en detalles | repo (`piezas.json`, `velo`, `color_texto`); orden de acentos y clara, `biblia.md` §2 (la clara sin pieza hecha) |
| Prohibidos | Rec. | degradados fuera de la baldosa y del fondo radial de los diagramas; neón; rojo como decoración; mezclar el acento `#3D6FD9` con el celeste `#38b6e8` en el mismo texto; negro `#000`; más de un color de acento en el texto | **[P]** (`biblia.md` §2: lo escribió el agente a partir de los diagramas; ninguna pieza lo ha puesto a prueba) |
| Degradados | Opc. | solo la baldosa del logo (`#3D6FD9 → #0d1b2a`) | repo (`logos/galivelop-workflow-a.svg`); regla de familia en `docs/marcas/README.md` |

**Medido:** la calibración da a este proyecto paleta ≥ 90 % (r1 y r5: 93-96 %; r2 palabras 96,6 %; r4 og 93,38 %), el más alto de los
siete (`docs/records/contenido/calibracion-measure.md` l.40 y l.71): un fondo plano de un solo azul con líneas finas cae casi
entero dentro de ΔE76 < 15. r2 enseñó que hex, palabras o materiales dan casi la misma paleta (96,5 / 96,6 / 83,8 %): se eligió
«palabras» porque material deja una mancha (`r2-estilo.md` l.30-32, l.50).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/galivelop-workflow/logos/galivelop-workflow-a.svg`: monograma «gw» de trazo 12/128 blanco con remates redondos, en la baldosa de la familia (`rx` 30) con degradado `#3D6FD9 → #0d1b2a`. Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; colores `#3D6FD9`, `#0d1b2a`, `#FFFFFF`. Las letras son trazos geométricos (círculo + asta + gancho; zigzag), no una fuente. **r7 (2026-11-04):** la persona pide que el logo siga el formato del de Galivelop (r6, 1/10) → `galivelop-workflow-b.svg`: monograma «GW» de un solo trazo blanco de 12 con remates redondos, la misma «G» del símbolo de Galivelop (`portal-a`) seguida de una «W», en la baldosa `rx` 30 con degradado del acento `#3D6FD9 → #1E3E99` (como el celeste → celeste intenso del Portal); es el elegido para `compose` | repo (archivo, `55148cc`). El **concepto** lo decidió la persona («monograma “gw” para Galivelop-workflow», `docs/plan.md` l.258-261, decisiones del 2026-10-26); el **dibujo** es **[P]**: el plan lo describía «en Inter 800 blanco» y el SVG lo resuelve en trazos de la familia, sin fuente, para que no dependa de tener Inter instalada y haga familia con `gv-logo.svg` |
| Lockup (símbolo + nombre) | Rec. | **r7:** `logos/galivelop-workflow-b-lockup.svg` (`viewBox 0 0 800 128`, `data-fondo="oscuro"`), con el formato del lockup de Galivelop: símbolo `b` a la izquierda, nombre a `x=152` en Sora 700 a 64/128 de alto, `letter-spacing` −1,9, en dos tonos: «Galivelop» `#EAF4FA` y «-workflow» `#3D6FD9`; es el que apunta `compose.logo`. Hasta r6, `logos/galivelop-workflow-a-lockup.svg` (`viewBox 0 0 760 128`): símbolo a la izquierda, nombre «Galivelop-workflow» a la derecha en Sora 700, 52/128 de alto, `#3D6FD9`, `letter-spacing` −1,5 (≈ −0,03 em), separación 28/128 (`x=156`). Lleva `<text>` con `font-family="Sora, sans-serif"` (reserva genérica), que la plantilla admite mientras `compose.fonts` garantice la fuente; el paso a trazos queda Opc. | repo (archivo); las medidas coinciden con las reglas de `biblia.md` §4 |
| Variante clara y oscura | Rec. | la baldosa lleva su propio fondo y vale sobre los dos; el nombre del lockup va en `#3D6FD9` sobre oscuro (único archivo que existe) y también sobre claro; símbolo suelto en `#3D6FD9` sobre claro y oscuro, o en `#eef6fb` sobre oscuro | **[P]** (`biblia.md` §4; solo existe el archivo para oscuro y nadie ha medido `#3D6FD9` sobre `#f6fafd`) |
| Tamaño mínimo y margen | Rec. | baldosa 16 px; símbolo suelto 24 px; lockup 120 px de ancho (por debajo, solo la baldosa); margen libre el grosor del trazo (12/128) por cada lado, que la baldosa ya incluye; nombre a la derecha a 52/128 de alto y 28/128 de separación, nunca debajo en menos de 160 px | **[P]** (`biblia.md` §4; reglas escritas por el agente al elegir) |
| Usos prohibidos | Opc. | girar, estirar, sombra o brillo, cambiar el radio de la baldosa, recolorear, poner el símbolo suelto sobre la ilustración | **[P]** (`biblia.md` §4) |
| Logo fuera de la paleta | Opc. | `#3D6FD9` y `#FFFFFF` están en el SVG y **no** en `brand.palette` de la configuración; sí en la tabla de la biblia | repo (diferencia entre `galivelop-images.json` y `biblia.md` §2) |

Copia en `examples/galivelop-workflow/logos/`: `galivelop-workflow-b-lockup.svg`, idéntica al original (r7; `compose.logo` apunta a ella y `tests/test_examples.py` exige la copia idéntica); `piezas.json` apunta hoy al `a` en
`docs/marcas/…/logos/`. En r4 el lockup de 760×128 salía a ~34 px de alto; desde entonces el piloto lo pone al 9 % del alto de
la pieza (`r4-composicion.md` l.28-33). El repo de Workflow no tiene favicon ni logo: el `a` sería el primero.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Rec. (familia Galivelop, con valor propio) | Inter (reserva `sans-serif`), como los títulos de los diagramas del Portal; el wordmark del lockup sigue en Sora 700 para casar con «Galivelop». **Peso: 700** (lo compuesto en r4-r5: `piezas.json` no declara peso y `componer.py` usa `peso_titulo=700`; decidido el 2026-11-04, ver «Contradicciones», 3) | heredado de Portal-Galivelop `aa76b34` (`docs/diagramas/gw-*.svg`, vía `biblia.md` §3); repo (`piezas.json` `fuente`; `examples/pilot/componer.py` l.119) |
| Familia de texto | Rec. | Inter (reserva `sans-serif`), **400 con opacidad 0,82** en subtítulos (lo compuesto en r4-r5; decidido el 2026-11-04, ver «Contradicciones», 3) | repo (`piezas.json` `fuente_texto`; `componer.py` l.159-160); `biblia.md` §3 |
| Licencia y archivo | Rec. | Inter y Sora, OFL, del repo `google/fonts`; `examples/pilot/fuentes.sh` las baja a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`; no instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)*. DejaVu Sans Mono (código, rutas, órdenes): fuente del sistema, sin archivo en ningún repo *(suposición: instalada en la Deck; las plantillas de Workflow la listan en su reserva `--mono`)* | repo (`examples/pilot/fuentes.sh` l.8-12); Workflow (`skills/gw-media-content/template/media/source/card.html` l.16-17) |
| Tracking y mayúsculas | Opc. | títulos Inter −0,02 em; wordmark Sora −0,03 em; sin mayúsculas sostenidas (el nombre va «Galivelop-workflow», con su guion y la w minúscula, en una línea y un solo color); monoespaciada para claves y órdenes (`reviewed.sh`, `docs/handoff.md`) | heredado de Portal-Galivelop `aa76b34` (vía `biblia.md` §3); la monoespaciada es **[P]** (`biblia.md` §3, sin pieza que la use) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivo propio (identidad vigente, 2026-11-11; pasa a la fila «Mar y tecnología» de arriba) | Obl. | **El relevo como historial de commits:** una línea de nodos redondos unidos por tramos cortos, una rama que se aparta y vuelve a unirse, y el último nodo con un visto (la revisión); el testigo, un tramo más grueso entre dos nodos. Es el icono que el Portal ya le pide (`orders/marca/23-icono-workflow.json`: «three round nodes chained in a row by short links, the last node holding a checkmark tick»). Variantes: solo, en línea simple (icono, avatar); sobre el mar de carta, en grabado, con la línea de nodos como ruta trazada sobre la carta (portada). Sin número exacto de nodos en el prompt («a few round nodes»). En imagen generada, las tres tintas del Portal y un toque del acento `#3D6FD9`; el ámbar y el verde de los nodos, ver «Dudas», 4 | **propuesta del agente, 2026-11-11**, según `../portal/hoja.md` «Mar y tecnología»; icono en `examples/portal/orders/marca/23-icono-workflow.json` |
| Motivos Sí | Obl. | 1) varias líneas finas de luz que corren hacia el borde derecho, se bifurcan y se vuelven a unir, con un nodo redondo en cada unión (el grafo de ramas); 2) un trazo corto de luz («dash») que pasa del final de una línea al principio de la siguiente en un nodo brillante (el relevo, el testigo); 3) celeste en las líneas, unos pocos nodos en ámbar y verde; 4) azul noche plano con rejilla tenue (los diagramas del Portal). Sin usar aún, de la biblia: el sello de revisión (anillo con marca de visto), el cuaderno de bitácora cerrado | repo (`prompts/estilo.txt`, elegido en r2 con el «sí» de la persona en r1; `docs/plan.md` l.634-636; `biblia.md` §7) |
| Motivos No | Obl. | personas, manos, pantallas, teclados, robots, cerebros, circuitos, lluvia de código, neón saturado, texto; la píldora o cápsula (r1 la pintó al pedir «capsule») | repo (`biblia.md` §7; `r1-fondos.md` l.47 y l.57) |
| Palabras vetadas | Obl. | `robot`, `brain`, `circuit`, `code rain`, `capsule`, `pill`, `hand`, `keyboard`, `screen`, `human`, `humanoid`, `spark`, `sparkle`, `magic`, `text`, `letters`, `logo`; más `like` y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7: `robot`, `brain`, `circuit`, `code rain`, `capsule`, `hand`, `keyboard`, `screen`, `like a`); `pill`, `human`, `humanoid`, `spark`, `sparkle`, `magic`, `text`, `letters`, `logo` **[P]** (cierran lo que «Nunca se muestra» nombra y lo que se parece a texto o logo, como pide la plantilla). **`estilo.txt`, `r2-*.txt` y `r5-*.txt` no las contienen; `og.txt` y `orders/r1-og.json` sí llevan `capsule`** (son el prompt de r1, superado). **Vigente desde el 2026-11-11:** las palabras propias (robot, cerebro, circuito, lluvia de código, cápsula, mano, teclado, pantalla, persona, texto) siguen vetadas; el veto a `no`/`not`/`without`/`like` **no se aplica** a piezas nuevas: rige «Cómo se escribe el prompt» de `../portal/hoja.md` |
| Estilo de imagen | Rec. | «minimal» y el diagrama plano **rechazados** (r4: ninguna publicable; r6, 1/10: «faltan brillos, efectos realistas, un árbol que se vea en 3D, más calidad»). **r7 (2026-11-04), concepto nuevo:** un árbol de ramas en 3D hecho de filamentos de vidrio encendidos en `#38b6e8` que se bifurcan, corren en paralelo y vuelven a unirse (relevos y ramas que se fusionan), una esfera de vidrio en cada unión, el testigo ámbar `#f2b34a` pasando de un tramo al siguiente, anillo verde `#4cc38a` en la última unión (la revisión), profundidad de campo, bokeh y reflejo en el suelo pulido, sobre el fondo `#0d1b2a` con la rejilla de difuminado radial que ya gustó: «Style: elegant digital art, physically based rendering, glass and light, soft volumetric glow, bokeh, crisp reflections, fine detail. Colours: #0d1b2a, #38b6e8, #f2b34a, #4cc38a, #eef6fb, #8a9bb0. Mood: precise, trustworthy, in motion.» (`orders/r7.json`) **r8 (veredicto de r7, 6/10, 2026-11-05):** sin árbol realista con luces encima: el árbol **lo forman** los nodos de luz y sus líneas de conexión (tronco, ramas y copa hechos de nodos y trazos luminosos). Reflejo en el suelo más rico. La rejilla del fondo, de celdas todas del mismo tamaño, y que se difumine más cuanto más se acerca al suelo. | repo (`prompts/estilo.txt`, elegido en r2; `orders/r6-detalle.json`, `orders/r7.json`); veredicto r6 en `../../records/contenido/r4-composicion.md` |
| Lenguaje de forma | Opc. | líneas de luz finas que se bifurcan y se vuelven a unir, nodos redondos, sellos circulares, testigos cortos; trazo 12/128 con remates y uniones redondos (9/128 en anillos y nodos pequeños); `rx` 30/128 en la baldosa; nada de flechas con punta rellena ni cajas con sombra; fondo plano, brillo suave | heredado de Portal-Galivelop `aa76b34` (`public/marca/gv-logo.svg`, vía `biblia.md` §5); lo demás **[P]** (`biblia.md` §5) |

Prompts del proyecto (`examples/galivelop-workflow/prompts/`): `estilo.txt` (= `r2-palabras.txt`, 139 palabras; «sí» de la persona
en r1 sobre `og.txt`, elegido en r2), `og.txt` (r1, 133; lleva «capsule» y las líneas «from left to right»: superado por
`estilo.txt`, se conserva como historia), `r2-hex.txt` (135) y `r2-material.txt` (158) (descartados), `r5-cuadrado.txt` (140),
`r5-vertical.txt` (141), `r5-cabecera.txt` (141) (compuestos y medidos), `r2-luz.txt` (181, sin veredicto). Todos de 133-181
palabras, dentro del rango 120-320; todos acaban en «The image is completely textless.».

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | la luz sale de las propias líneas (no hay fuente externa); en `r2-luz.txt`: «the only light comes from the glowing lines on the right», el nodo más brillante «a quarter of the way in from the right edge», y el brillo «fades into darkness toward the left» | repo (`prompts/estilo.txt`); la variante *(suposición: r2-luz sin veredicto)* |
| Momento y clima | Rec. | escena oscura, dicha al principio: «Dark wide abstract technical illustration: the whole frame is deep dark navy…» (r2-luz); en `estilo.txt` el fondo oscuro va en la primera frase | repo (`orders/r2-luz.json`) *(suposición)* |
| Luminosidad objetivo (YAVG) | Rec. | 30-50 (r1 y r5: 33-48; r2 palabras 35,7; r4 og compuesto 43,02; portada del Portal 39) | repo (`calibracion-measure.md` l.39-40, l.71) |
| Saturación objetivo (SATAVG) | Rec. | 8-12 (r1 y r5: 9-11; r2 palabras 9,1; r4 og 9,27; portada 10) | repo (`calibracion-measure.md`) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **publicada dónde:** en el repo de Workflow, nada (sin web, sin social preview declarado, sin favicon). Workflow **sí tiene ficha en el Portal** (`src/data/proyectos/galivelop-workflow.json`, de donde sale el acento) y la calibración midió su `portada.webp` allí (YAVG 39, SATAVG 10, paleta 95 %; EMD de r1 y r5 frente a ella: Y 4-10, Cb 0,9-1,8, Cr 1,4-3,5). Los siete diagramas `gw-*.svg` del Portal son lo más publicado del flujo y la fuente de la paleta. **Vale como referencia:** **[P]** (la portada la hizo el agente para el Portal; la persona dice si es marca) | *(suposición: la ruta es `Portal-Galivelop/public/proyectos/galivelop-workflow/portada.webp`; no se ha abierto ese repo)*; `calibracion-measure.md` l.39 |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 (**sin** `targetWidth`/`targetHeight` 1200×630), `social` 1280×640, `square` 1024×1024 (**sin** destino 1080×1080), `banner` 1280×512 (sin destino 1600×640; **nunca generado**: ni prompt ni pieza). Hechos en el piloto y sin perfil: `portrait` 896×1152 → 1080×1350 (`vertical`), `header` 1536×512 → 1500×500 (`cabecera`) | repo (`galivelop-images.json`; `piezas.json`); `portrait` y `header` **[P]** (bitácora: «lo decide la persona» en F2.8); `banner` está en la primera ronda de la biblia y sigue sin hacer |
| Zona reservada | Obl. | `og`, `social`, `header`, `banner`: `izquierda 1/2` («The left half of the frame is a plain, empty dark background with only the faint grid»); `square`, `portrait`: `arriba 1/2` («The upper half of the frame is a plain, empty dark background»). En píxeles (conversión de la plantilla): `og` entregado 1200×630 → `0,0,600,630`, caja `data-caja` de la plantilla `60,60,604,510` (margen 60, columna 604; logo a 52-54 px de alto, titular en dos líneas, filete corto en el acento y subtítulo en dos líneas; r7); `square` 1080×1080 → `0,0,1080,540`. La caja del piloto es 55 % del ancho menos margen (izquierda) o 48 % del alto (arriba), margen 6 %: no coincide con 1/2 y se alinea al portar a `compose` | repo (`prompts/*.txt`; `examples/pilot/componer.py` `caja_zona` l.105-115). **La biblia dice «tercio superior» para `square`; r5 pidió y midió la mitad** (ver «Contradicciones») |
| Velo por perfil | Rec. | `og` `#0d1b2a:0`; `cuadrado`, `vertical` y `cabecera` `#0d1b2a:0.3` | repo (`piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza (57 px en el `og`), en lo alto de la caja de la zona con el título debajo, margen 6 %; solo baja si no cabe a lo ancho de la columna | repo (`componer.py` l.129-137; `r4-composicion.md` l.28-33) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo, lockup al 9 %, título Inter 700, subtítulo Inter 400). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Inter","Sora"], fit: "cover"}`; Sora hace falta aunque el titular sea Inter, porque el `<text>` del lockup la usa | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-workflow-a.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay; el repo de Workflow no tiene favicon ni web que lo consuma | repo (`piezas.json`); `icon` **[P]** |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos: YAVG/SATAVG/paleta 29/13/96 % frente a 39/9/97 % del definitivo, con las líneas cambiando de cruce pero mismo estilo y hueco. Propuesto `draft: {scale: 0.5, steps: 4}` en `og` | **[P]** (F2.10, dec. 7; `r3-borrador.md` l.48 y l.66) |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia desde r2 con solo decirlo), sin LUT (paleta 93-97 %), sin conversión final por parte de `gimg` | repo (`r2-estilo.md` l.50; `r5-piezas.md`) |
| Prioridad | Rec. | la de la biblia: 1) logo y `avatar` 512; 2) `social` 1280×640 de GitHub; 3) `og` 1200×630 de la ficha del Portal; 4) `square` con el lema; 5) `banner` 1600×640 del relevo. Hechas en el piloto: `avatar`, `og`, `cuadrado`, `vertical`, `cabecera`; `social` sale del mismo fondo que `og` sin recortar; `banner`, sin hacer | repo (`biblia.md` §9; `docs/plan.md` l.642-644) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | «Lo que no está subido no existe.» (33 caracteres), en `og` | repo (`piezas.json`, r4; es el lema literal de `AGENTS.md` l.24 de Workflow, con punto final) |
| Subtítulo | Rec. | «Flujo de trabajo por relevos para agentes de IA, en abierto (MIT).» (67) | **[P]** como frase (`piezas.json`, r4); sus hechos salen de Workflow (`README.es.md` l.5-6; `LICENSE`) |
| Variaciones, ganchos y cierres | Rec. | usados en r5: `cuadrado` «Cada sesión es un relevo.» / «Commit, push, bitácora. Siguiente.»; `vertical` «Nada llega a main sin revisión.» / «El humano decide y revisa; la IA ejecuta y propone.»; `cabecera` «¿Y si la sesión se corta ahora mismo?» / «El estado vive en los archivos, no en la conversación.». Sin usar: «Hecho, revisado y subido.» · «Elegir el modelo antes de empezar ahorra más que compactar.» | «El estado vive en los archivos, no en la conversación» es literal de Workflow (`templates/es/AGENTS.md` l.32); «Nada llega a main sin revisión» resume el epígrafe «Nada sin revisar llega a la rama protegida» (`README.es.md`); «Siguiente.» es la última línea de cada commit del flujo (`AGENTS.md`). El resto **[P]** (`biblia.md` §6; `piezas.json`) |
| Longitud máxima por campo | Rec. | la fija la composición: `componer.py` baja el cuerpo hasta 16 px y falla si el texto no cabe en la zona. Orientativo: titular ≤ 40 (los de r4-r5 van de 25 a 37), subtítulo ≤ 70 (el más largo, 67) | repo (`examples/pilot/componer.py`; `piezas.json`) |
| Wordmark compuesto como texto | Opc. | el nombre va en el lockup (Sora 700; desde r7 en dos tonos, «Galivelop» `#EAF4FA` + «-workflow» `#3D6FD9`, el formato del lockup de Galivelop; hasta r6 todo en `#3D6FD9`), nunca como `text` del pedido. En las tarjetas de `gw-media-content` el nombre del proyecto va en mayúsculas con tracking 0,16 em (`.brand`), que no es el wordmark de la biblia (ver «Contradicciones») | repo (lockup); Workflow (`skills/gw-media-content/template/media/source/card.html` l.22) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` | repo (`galivelop-images.json` `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto, escrito explícito) | repo (`delivery.template`) |
| Dónde se publica cada pieza | Rec. | `social`: social preview del repo `github.com/Zeldris/Galivelop-workflow`; `avatar`: GitHub y Discord; `og`: og:image de la ficha del Portal (hoy no consta qué imagen usa esa ficha); `banner`: portada 1600×640 en el Portal; las tarjetas de redes (X, LinkedIn, Discord, Reddit; 1200×675) **no las hace `gimg`**: las renderiza `gw-media-content-now` desde sus HTML y las deja en `docs/media/` del repo de Workflow (ver «Cambios que pediría a la plantilla») | Workflow (`.claude-plugin/plugin.json` `repository`; `skills/gw-media-content/note.md`, `template/media/source/card.html` `gw-size`); Portal y `banner` **[P]** (`biblia.md` §9; `docs/plan.md` l.642-644) |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto, no declarado) | repo (esquema) |
| Conversión final | Opc. | `banner` a `.webp` si va al Portal *(suposición: como la portada de Tarkor)*; LinkedIn no acepta WebP, exige `.png` o `.jpg` (`rules.json` `linkedin.image_formats`); X admite PNG ≤ 5 MB | Workflow (`skills/gw-media-content/rules.json`) |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona: r1 «sí» (2026-10-26, por proyecto y no por semilla, «pasa pese a la nota»); r2-r5 delegado al agente. Apuntado en `docs/records/contenido/r1-fondos.md` l.47-57, `r2-estilo.md` l.50 (elegida «palabras»), `r4-composicion.md` l.18, `r5-piezas.md` l.32 | repo |
| Contraste del texto | Rec. | ≥ 4,5:1 (por defecto); medido: og r4 16,64 (peor 15,86) sin velo; r5 cuadrado 15,75 (15,54), vertical 15,89 (15,64), cabecera 15,14 (14,82) con velo 0,3. Todas sobre el 7:1 de AAA | repo (`r4-composicion.md` l.18; `r5-piezas.md` l.32) |
| Umbrales de medida | Rec. | los de las secciones 3 y 7: paleta ≥ 90 %, YAVG 30-50, SATAVG 8-12 | repo (`calibracion-measure.md` l.71) |
| EMD frente a la marca | Opc. | Cb ≤ 3 / Cr ≤ 4 (medido frente a la portada del Portal: Cb 0,9-1,8, Cr 1,4-3,5), los más bajos de los siete | repo (`calibracion-measure.md` l.40, l.71) *(suposición: la referencia, sección 8)* |
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» de la persona en r1 y la palanca de r1 (mitad izquierda vacía, «dash» por «capsule») funcionó en r2; r5 dio las tres piezas de formato a la primera. Pendiente: el veredicto de la persona sobre lo delegado y el `banner` | repo (registros r1-r5) |

## 13. Fuentes de verdad

**Galivelop-workflow**, `main` `7d61089` (leído solo; nada modificado):

- `README.md` l.1-12 y `README.es.md` l.1-12 (nombre, propósito, estado «0.4.3, etapa 1 en rodaje»), l.14-23 (los cuatro
  problemas), «Lo que lo hace distinto» (tono: «Las reglas las hace cumplir un script, no la buena voluntad del agente»;
  «Calidad primero»; «Nada sin revisar llega a la rama protegida»), «Cómo se aplica» (etapa 2, promesa que no se hace),
  «Agradecimientos» y «Licencia».
- `AGENTS.md` l.7 (relevos), l.24 (lema literal), §«Relevos» (campo semántico, «Siguiente:»).
- `templates/es/log.md` l.4 y `templates/es/AGENTS.md` l.27 (lema), l.32 («El estado vive en los archivos…»);
  `templates/es/GLOSSARY.md` l.11 («Relevo»).
- `LICENSE` (MIT), `CREDITS.md` (Matt Pocock, `LICENSE-mattpocock-skills`).
- `.claude-plugin/plugin.json` (`name`, `description`, `repository`, versión `0.5.0`), `.claude-plugin/marketplace.json`;
  `.claude/gw.json` (`language: es`, `version: 0.5.0`).
- `skills/gw-media-content/note.md` (canales por defecto `x, reddit, linkedin, discord`; `Languages: es, en`; clave
  `Palette`; carpeta `docs/media`), `rules.json` (límites por red: LinkedIn sin WebP, X ≤ 5 MB), `catalog.md` (tipos de
  publicación), `template/media/source/{card,diagram,metrics,quote,code,before-after,carousel}.html` (paleta por defecto
  `#0f172a`, `#1e293b`, `#334155`, `#f1f5f9`, `#94a3b8`, `#38bdf8`, `#4ade80`, `#f87171`; fuente `system-ui…`; `.brand` en
  mayúsculas con tracking 0,16 em; `gw-size` 1200×675), `SKILL.md` l.14-16 (cada número con su fuente).
- **No existe** en el repo: CSS, HTML de web, SVG, favicon, logo, `.claude/gw/gw-media-content.md` (nota con `Palette`),
  `docs/media/` (piezas publicadas).

**Portal-Galivelop** `aa76b34` (marca paraguas, «heredado de»), leído solo a través de `biblia.md` §10 y
`docs/marcas/portal/biblia.md`: `src/data/proyectos/galivelop-workflow.json` (acento `#3D6FD9`; la ficha del proyecto),
`docs/diagramas/gw-*.svg` (fondo `#0d1b2a`, texto `#eef6fb` y `#8a9bb0`, celeste, ámbar, verde, rojo; Inter 800 / 600),
`public/marca/gv-logo.svg` y `src/components/Logo.tsx` (baldosa `rx` 30, trazo 12; Sora 700, −0,03 em), tema (`#06121c`,
`#f6fafd`, `#0a1a28`).

**Este repo**, `f2-motor` `78f0083`:

- `examples/galivelop-workflow/galivelop-images.json` (`name`, `brand.palette` de 5 hex, `delivery`, perfiles `og`, `social`,
  `square`, `banner`; último cambio `b65bd81`).
- `examples/galivelop-workflow/piezas.json` (fuentes Inter/Inter, textos, zona, color de texto y velo de las cuatro piezas,
  ruta del lockup y del avatar).
- `examples/galivelop-workflow/prompts/estilo.txt`, `og.txt`, `r2-palabras.txt`, `r2-hex.txt`, `r2-material.txt`,
  `r2-luz.txt`, `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` y `orders/*.json` (motivos, estilo, zona por
  formato, luz).
- `docs/marcas/galivelop-workflow/logos/galivelop-workflow-a.svg` y `-a-lockup.svg` (último cambio `55148cc`); las
  propuestas `b`-`d` siguen en la carpeta.
- `docs/marcas/README.md` l.15, l.32 («Elegido por el agente»: logo `a`), l.153-157 (conceptos de logo), tabla «Común a todos».
- `docs/marcas/galivelop-workflow/biblia.md` (`a50b544`; paleta, tipografía, reglas del logo, vetos, frases; lo que es **[P]**
  allí lo sigue siendo aquí).
- `docs/plan.md` l.258-261 (decisiones de la persona del 2026-10-26: monograma «gw»), l.632-644 («Estilos por proyecto»,
  Galivelop-workflow), l.900 («Marcas sin material»).
- `docs/records/contenido/calibracion-measure.md` l.39-40, l.56, l.71; `r1-fondos.md` l.47-57; `r2-estilo.md` l.30-32, l.50;
  `r3-borrador.md` l.48, l.66; `r4-composicion.md` l.18, l.28-33; `r5-piezas.md` l.32, l.51.
- `examples/pilot/componer.py` l.105-115 (`caja_zona`), l.119 (`peso_titulo=700`), l.129-137 (logo al 9 %), l.159-160
  (subtítulo 400); `examples/pilot/fuentes.sh` l.8-12 (origen y licencia de las fuentes).

Sin línea aquí y por tanto **[P]** o *(suposición)*: el dibujo del logo (no el concepto), reglas del logo tras elegir, pieza
clara, prohibidos de la paleta, monoespaciada, nueve palabras vetadas añadidas, perfiles `portrait`/`header`, `draft`,
`compose`, `icon`, el subtítulo y cinco de las seis frases de r5, el Portal como destino, la portada del Portal como marca.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo y a Workflow):

- `og` sin `targetWidth` 1200 / `targetHeight` 630 y `square` sin 1080×1080 (image-generator lo arregló el 2026-11-04;
  aquí no).
- `banner` declarado (1280×512, sin destino 1600×640) y nunca generado; `portrait` y `header` generados en r5 y no
  declarados.
- `#3D6FD9` y `#FFFFFF` (los del logo) y `#8a9bb0` fuera de `brand.palette`.
- `compose`: plantilla, fuentes, zona, velo y logo en la pieza viven en `examples/pilot/componer.py`.
- `prompts/og.txt` y `orders/r1-og.json` llevan `capsule`, vetada desde r1 (comprobación 8): o se marcan como históricos o se
  retiran; `estilo.txt` ya es el que manda.
- Copia de los logos en `examples/galivelop-workflow/logos/`: pendiente (F2.10, dec. 3).
- En el repo de Workflow: su nota `.claude/gw/gw-media-content.md` no existe y sus tarjetas saldrían con la paleta genérica
  de las plantillas; se le propone una línea `Palette:` con los hex de la biblia (ver «Contradicciones», 1).

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; es la primera frase del README de Workflow) |
| 3 | «Nunca se muestra» no vacío | pasa; nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | hex pasa (5); fondo `#0d1b2a` y texto `#eef6fb` están; **el acento `#3D6FD9` no está** (la hoja nombra los roles, la configuración no los lleva) |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, `<title>`, sin `<text>`/`<image>`/`filter`; «sí» a 16 px según la tabla de la biblia §4); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: sin `compose.fonts`, y las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts`; DejaVu Sans Mono sin archivo declarado |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | **no pasa del todo** en los históricos: `og.txt` y `orders/r1-og.json` llevan `capsule` (prompt de r1, superado); `estilo.txt`, `r2-palabras/hex/material/luz.txt`, `r5-*.txt`, `orders/r2-control.json` y `r2-luz.json` pasan. **Para piezas nuevas no se aplica tal cual**: la comprobación es el punto 5 de «Cómo se escribe el prompt» de `../portal/hoja.md` |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (133-181 palabras), los nueve |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | múltiplos de 64 pasa; **`og` y `square` sin destino declarado** (1200×630 y 1080×1080) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | el prompt la describe en los cuatro formatos; ningún perfil la declara (hueco) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (33 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | **no pasa:** acento `#3D6FD9` y blanco `#FFFFFF` del logo, texto 2 `#8a9bb0`, fondo alterno `#06121c` y los de la pieza clara no están; los de la pieza oscura sí (`#0d1b2a`, `#eef6fb`) |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | **no pasa** para `og` (1280×640 → 1200×630) ni `square` (1024 → 1080); `banner` (→ 1600×640) tampoco; `portrait` y `header` no están declarados (hueco) |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 15** (familia
Galivelop; 18 con la familia propia). Fondo, texto y titular son Rec. y están completos, aunque los tres cambian el valor de la
familia con su justificación (sección 0).

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan: roles de la paleta (`brand.palette` no distingue el acento del logo del celeste de la
imagen), zona reservada (solo en prompt y en `componer.py`), velo y logo en la pieza (solo en `componer.py`), palabras vetadas sin
campo (y un prompt histórico que lleva una), `avatar` sin perfil (lo hace `piezas.py`), tipografía sin licencia ni ruta
declaradas (DejaVu Sans Mono ni siquiera tiene archivo), imágenes de marca para la EMD sin lista (la calibración usó la portada
del Portal), idiomas y textos por idioma (Workflow publica en `es` y `en`; las piezas solo en `es`), copia de los logos en
`examples/<p>/logos/` pendiente. No le afectan: varias variantes de logo (la baldosa vale sobre claro y oscuro), `compose.lut`
(paleta 93-97 %), `style.lora`.

**Hueco propio de este proyecto, que la plantilla no lista:** dos sistemas hacen piezas de marca de Workflow con paletas
distintas: `gimg` (fondos y composición, paleta de la biblia) y `gw-media-content-now` (tarjetas HTML → PNG/WebP de 1200×675,
paleta genérica de sus plantillas). Nada los alinea hoy. Ver «Cambios que pediría a la plantilla», 2.

---

## Contradicciones

Entre el repo de Workflow (`7d61089`) y la biblia (`a50b544`), o entre la biblia y lo que ya generó el motor.

1. **Resuelto (2026-11-04): la hoja manda con la biblia; el cambio va al repo de Workflow como propuesta (`gw-harvest`), no se hace desde aquí.** **Paleta y letra de las tarjetas de redes.** Lo único con color del repo de Workflow son las plantillas de
   `gw-media-content` (`skills/gw-media-content/template/media/source/*.html`): fondo `#0f172a`, superficie `#1e293b`, borde
   `#334155`, texto `#f1f5f9`, apagado `#94a3b8`, acento `#38bdf8`, verde `#4ade80`, rojo `#f87171`, fuente `system-ui…`, nombre
   del proyecto en mayúsculas con tracking 0,16 em. La biblia §2-§3 dice `#0d1b2a`, `#eef6fb`, `#8a9bb0`, `#38b6e8`, `#4cc38a`,
   `#f0716a`, Inter, wordmark en una línea sin mayúsculas. Los tonos son vecinos (azul noche, celeste, verde, rojo), pero no
   son los mismos hex, y las propias plantillas dicen «override these to match the project» mientras el repo no tiene la
   nota `.claude/gw/gw-media-content.md` que lo haría. **Propuesta:** la hoja manda con la biblia; en `docs/propuestas/galivelop-workflow.md`
   se le pide a Workflow una nota con `Palette:` que mapee `--background: #0d1b2a; --surface: #06121c; --border: #1b3447;
   --text: #eef6fb; --muted: #8a9bb0; --accent: #38b6e8; --accent-text: #0d1b2a; --good: #4cc38a; --bad: #f0716a` y
   `--font: Inter, …` (el borde `#1b3447` es el de las superficies oscuras del Portal, `docs/marcas/portal/biblia.md` l.28; la biblia de Workflow no lo lista). El `.brand` en mayúsculas queda como está
   si la persona lo acepta como rótulo de tarjeta, no como wordmark.
2. **Resuelto (2026-11-04): `arriba 1/2`, lo medido; biblia corregida.** **Zona reservada del `square`.** Biblia §7: «el tercio superior en `square`». `prompts/r5-cuadrado.txt` y `r5-vertical.txt`
   piden «the upper half», `piezas.json` compone en `arriba` (48 % del alto) y la medida salió 15,75 (peor 15,54).
   **Propuesta:** `arriba 1/2`, lo medido; corregir la biblia.
3. **Resuelta (2026-11-04): titular 700, subtítulo Inter 400 con opacidad 0,82; biblia corregida.** **Pesos de Inter.** Biblia §3 decía títulos Inter 800 y subtítulos 600. Las piezas de r4-r5 salieron a 700 y 400 (`componer.py`
   `peso_titulo=700`, subtítulo `font-weight="400"` con opacidad 0,82); `piezas.json` no declara peso. **Decisión (delegada, `docs/records/decisiones-hojas-2026-11-04.md`, fila 4):** manda lo compuesto y visto, y es la misma regla para los siete proyectos; los 800/600 quedan solo en los diagramas del Portal, que no son piezas de `gimg`.
4. **Resuelto (2026-11-04): se mantienen los trazos; biblia y plan corregidos.** **Dibujo del monograma.** `docs/plan.md` l.640 y la biblia §4 (tabla) hablan del «gw» «en Inter 800 blanco»; el SVG `a`
   dibuja las letras en trazos de 12/128 con remates redondos, sin fuente. **Propuesta:** mantener los trazos (sin dependencia
   de fuente, mismo lenguaje que `gv-logo.svg`) y apuntarlo en la biblia; es la parte **[P]** del logo.
5. **Resuelto (2026-11-04): biblia al día (`rules.json`, `7d61089`, v0.5.0).** **Rutas y versión desfasadas en la biblia.** §10 cita `skills/gw-media-content/reglas.json` y el commit `56212e8`; hoy el
   archivo es `rules.json` (el `CHANGELOG.md` l.743 y l.879 aún lo nombran `reglas.json`) y el commit `7d61089`. §1 dice «v0.4.x»; el `README` dice
   `0.4.3` y `.claude-plugin/plugin.json` y `.claude/gw.json` dicen `0.5.0` (la versión en desarrollo). **Propuesta:** actualizar
   §10; en las piezas no se nombra versión salvo que la pida una tarjeta de release, que la toma de `figures.py`.

## Cambios que pediría a la plantilla

**Aplicados (2026-11-04)** en [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md): los tres.

Workflow es una herramienta de desarrollo sin producto visual, sin web propia y con otro generador de piezas dentro de su repo.
Tres cosas de la plantilla no le encajan sin forzar:

1. **«Acento: el único color que hace de marca en la imagen; uno por pieza».** Aquí el acento de marca (`#3D6FD9`) vive solo
   en el logo y el wordmark, y la imagen habla el lenguaje de los diagramas del Portal, con **tres acentos con significado**
   (celeste = lo de galivelop, ámbar = el testigo y lo aprendido de otros, verde = ok) en un orden de peso. La fila obliga a
   elegir uno y deja el resto en «Resto de la paleta», donde se pierde el orden y el significado. **Pediría:** que «Acento»
   admita «acento de marca (logo y wordmark)» y, debajo, una fila Rec. «Acentos en imagen, en orden de peso y con su
   significado», para los proyectos cuyo lenguaje visual es un diagrama. Los proyectos con un solo acento la dejan en «no hay».
2. **Dos sistemas que hacen piezas de marca.** La plantilla da por hecho que las piezas de marca las hace `gimg` (o las dibuja
   el agente en SVG). En Workflow las tarjetas de redes (1200×675, el perfil `wide` de la tabla común) las hace
   `gw-media-content-now` desde HTML, con su propia paleta y fuente, y las deja en `docs/media/` del repo del proyecto. Pasará
   lo mismo en cualquier proyecto que adopte el flujo, incluido este. **Pediría:** una fila Rec. en la sección 11 («Otras
   piezas de marca que hace otro sistema: qué sistema, qué formatos, dónde toma la paleta y la fuente»), para que la hoja sea
   el sitio donde los dos leen los mismos hex. Hoy esa alineación no la hace nadie (sección 15).
3. **«Imágenes de marca: publicada dónde» y «Dónde se publica cada pieza» suponen una web.** Para un plugin, «publicado» es el
   social preview de GitHub, el avatar de Discord, la ficha en el Portal (que es de otro repo) y las publicaciones de
   `gw-media-content` en `docs/media/`. Nada de eso se lee desde el repo del proyecto, así que la fila se queda en «no consta
   en el repo» aunque la pieza esté publicada. **Pediría:** que las dos filas admitan como valor una lista de canales con
   «consta / no consta en el repo», y que el social preview de GitHub se marque explícitamente como no comprobable desde el
   repo (lo fija la interfaz de GitHub, no un archivo).

Lo demás de la plantilla encaja: Workflow tiene lema, tono, campo semántico y textos literales en su repo, más que ninguna de
las otras herramientas.

---

## Lo que enseñó rellenarla

**Balance de este proyecto:** 15 obligatorios (familia Galivelop); **14 completos desde un repo** (Workflow, Portal vía biblia o
este), **1 [P]** (el dibujo del símbolo; su concepto lo decidió la persona). De los 66 campos de la plantilla, 12 son **[P]**
en todo o en parte (pieza clara y sus dos valores, prohibidos de la paleta, dibujo del logo, variantes, tamaños y márgenes, usos
prohibidos del logo, monoespaciada, nueve palabras vetadas añadidas, `portrait`/`header`, `compose`, `icon`, `draft`, subtítulo y
variaciones, Portal y `banner` como destino, portada del Portal como marca) y 1 es «no hay» (`icon`, admitido). De los
recomendados, 4 «no hay» o no comprobables (composición por perfil, copia de logos, fuentes instaladas, imagen de marca propia),
los mismos que en image-generator.

**Diferencia con image-generator:** allí el lema y las frases eran **[P]**; aquí el lema y dos de las frases son literales del
repo, porque Workflow escribe su manera de trabajar en `AGENTS.md` y el `README`. A cambio, Workflow no tiene ni un hex ni una
fuente propios: toda la identidad visual es heredada o propuesta, y su repo lleva dentro otra paleta (la de `gw-media-content`)
que nadie ha alineado con la biblia.
