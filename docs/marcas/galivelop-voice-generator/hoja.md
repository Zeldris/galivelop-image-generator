# Hoja de estilo mínima: galivelop-voice-generator

> **Dos identidades en esta hoja.** Desde el 2026-11-12 voice-generator es un **producto de la familia Galivelop**: sigue
> la hoja del Portal ([`../portal/hoja.md`](../portal/hoja.md), «Familia Galivelop: lo que heredan los productos» y
> «Decisiones de la persona (2026-11-12)») y solo pone su acento y su motivo. **Lo vigente son los cuatro bloques de
> abajo**, con la misma forma que los del Portal: «Identidad vigente», «Interfaz: tokens y reglas», «Recursos» y «Familia
> Galivelop: lo que hereda y cómo se comprueba». Las secciones 0-15, «Contradicciones» y «Lo que enseñó»,
> [`biblia.md`](biblia.md) y los ocho SVG de [`logos/`](logos/) describen la identidad anterior (`#06121c`, Sora/Inter,
> FLUX, cinta de luz, baldosa con degradado) con la que se hicieron las piezas de r1-r5: se quedan como histórico y **no
> se siguen para piezas nuevas**. De ellas sigue vigente lo que no es visual: propósito, tono, vocabulario y ética
> (secciones 1 y 2).

**Aprobada el 2026-11-04** (decisiones delegadas por la persona; ver `docs/records/decisiones-hojas-2026-11-04.md`);
reescrita el 2026-11-12 para seguir al Portal sección por sección. Estados como en [`../README.md`](../README.md):
**heredado** remite a una sección de la hoja del Portal y no repite sus valores salvo donde hacen falta para comprobar;
**propio** es lo que solo vale para voice; **calculado** sale de [`tonos.py`](tonos.py); **[P]** es propuesta del agente
(las que esperan a la persona están en «Dudas que decide la persona»).

Commits de referencia: galivelop-voice-generator `main` `5f67bd4` (2026-11-11, «F1: núcleo de gvoice (#4)»; antes esta
hoja citaba `claude/voces-f1` `ab1ff10`); Portal-Galivelop rama `ccr-47f8fddd-o5ek6p` `6574c4f` (el que cita la hoja del
Portal); este repo `8bb0ae1` (`hojas-repos`). Los dos repos ajenos se han leído con `git show`, **sin modificar nada**.

**Lo primero que hay que saber:** el repo de voces **sigue sin nada visual** en `5f67bd4`: ningún `.css`, `.html`,
`.svg`, `.png`, `.jpg`, `.ico` ni `.webp` (`git ls-tree -r --name-only origin/main`, 0 archivos), ni logo, ni licencia
(`README.md` l.70, «Todavía no hay licencia»). **F1 no trae nada visual:** `git diff --stat ab1ff10 origin/main` son 50
archivos de `gvoice/`, `tests/`, `examples/`, `docs/` y los dos README; la orden `gvoice` es de terminal (`README.md`
l.18-33) y la interfaz es la fase F5 de su plan (`docs/plan.md` l.45: «Proyectos; pedidos; galería de tomas con
reproductor y comparación; ficha con avisos; efectos con escucha; es/en»), sin empezar. Todo lo visual vive aquí.

---

## Identidad vigente (2026-11-12): lo que gimg necesita

Lo que se aplica a cada pedido nuevo de voice. Cada fila dice qué hereda (y de qué fila del bloque «Identidad vigente»
del Portal) y qué es propio. Donde esta hoja y la del Portal digan cosas distintas en algo heredado, manda la del Portal
y esta se corrige.

| Campo | Valor | Estado |
|---|---|---|
| Paleta | **Heredado:** cerúleo `#0072a8` («medium cerulean ocean blue #0072a8»), papel `#fbfcfd`, tinta `#13212b`; versión oscura, fondo `#0d171e` y líneas `#e6eef3`; los grabados admiten «tints and shades» del cerúleo; los iconos, una sola tinta. **Propio: el acento frambuesa ocupa el lugar del alga `#5d7a6a`**, en poca cantidad («a touch of»), nunca bloque grande ni protagonista. Frase final de todo prompt de voice: **«Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of raspberry pink #d9467a.»** (sin «and its tints and shades» en línea simple). `brand.palette` del proyecto pasa a ser la del Portal con los tres tonos del acento en lugar del alga: `#0072a8`, `#1aa6df`, `#fbfcfd`, `#13212b`, `#e6eef3`, `#0d171e`, `#d9467a`, `#ce3c71`, `#db487b` (hoy lleva la anterior: ver «Recursos», pendientes) | Portal, fila «Paleta» y «Qué cambia», fila «Acento secundario» (`../portal/hoja.md` l.52, l.262) y decisión 3 (l.355-357); el nombre «raspberry pink» es el de `examples/galivelop-voice-generator/prompts/estilo.txt`; el tono que va en la frase, **[P]** (duda 2) |
| Acento: tres tonos | **Vivo `#d9467a`** (el hex de hoy), **hondo `#ce3c71`** (tema claro) y **variante oscura `#db487b`** (tema oscuro). El hondo y la oscura son **calculados**, no elegidos: OKLCH del vivo `L` 0,6143, `C` 0,1869, `h` 2,78°; hondo, 6 pasos de 0,005 hacia abajo (`L` 0,5843); oscura, 1 paso hacia arriba (`L` 0,6193); croma y tono sin tocar (los dos caen dentro de sRGB). Ratios en «Interfaz». Reproduce: `python3 docs/marcas/galivelop-voice-generator/tonos.py '#D9467A'` | **calculado** con el método de la decisión 1 del Portal (`../portal/hoja.md` l.333-352); vivo: `docs/plan.md` l.765 («voces frambuesa `#D9467A`»), `docs/marcas/README.md` l.180, `examples/galivelop-voice-generator/galivelop-images.json` `brand.palette`. **El Portal traía otro hex, `#C9467A`** (`src/data/productos/galivelop-voice-generator.json` l.5, `6574c4f`): **Decidido por la persona (2026-11-12): vivo `#D9467A`**, y el Portal cambia su l.5 (duda 1, cerrada) |
| Tipografía | **Heredado sin cambio:** Big Shoulders Display (titulares), Literata (texto), JetBrains Mono (datos). **Ninguna imagen lleva texto**, ni generado ni compuesto: lo pone la web o la interfaz con sus fuentes. Sora e Inter y las piezas compuestas con título (r4-r5) son histórico | Portal, fila «Tipografía» (l.53) y decisión 3 |
| Modelo y parámetros | **Heredado:** calidad con `zimage-turbo-q6`, 8 pasos, cfg 1.0, euler, base 1024 y `draft {scale 0.5, steps 4}`; FLUX solo bocetos; Qwen-Image no hace falta. Con cfg 1.0 no hay prompt negativo. Los perfiles de `examples/galivelop-voice-generator/galivelop-images.json` (FLUX, 1280×640) son los de r1-r5: histórico | Portal, fila «Modelo y parámetros» (l.54) |
| Mar y tecnología | **Heredado:** el mar pone el dónde (carta, isobatas, papel, cerúleo) y la tecnología el qué; ningún motivo náutico protagonista; voice no añade excepción. **Propio, el qué de voice: la onda como dato.** 1) En grabado: la forma de onda dibujada como una sola línea, el perfil de profundidad del fondo de una carta («a sound wave drawn as a single depth profile line of the seabed»). 2) En línea simple: una ventana de aplicación con una fila de barras verticales de distinta altura («an application window holding a row of short vertical bars of varying height, a waveform»), sin número de barras; la toma elegida se marca con un visto o un subrayado, no con color. 3) En el logo: la onda que entra y se enrosca en espiral, la huella de la voz | Portal, fila «Mar y tecnología» (l.55); motivo 1, pedido `examples/portal/orders/marca/15-proximamente-voz.json` (aprobado, q331) y Portal `docs/marca.md` l.254 (`6574c4f`); motivo 2, **[P]** del 2026-11-11 (sin pieza); motivo 3, `docs/plan.md` l.770 («una cinta de onda que se enrosca en una huella») y `logos/galivelop-voice-generator-a.svg` (`<title>`) |
| Dos registros de dibujo | **Heredado, con los bloques literales del Portal:** grabado a dos tintas para lo grande; línea simple para iconos y logo. No se mezclan. **Deja de valer** el estilo de r1-r5 («thin precise luminous lines, soft glow, smooth gradients», sección 6): pide resplandor y degradado, prohibidos en toda la familia | Portal, fila «Dos registros de dibujo» (l.56) y «Prohibido en toda la familia» (l.297-305) |
| Zonas limpias, recuentos, encuadre | **Heredado sin cambio:** zona limpia en positivo y al principio, como papel; trama confinada; nunca «exactly N» (las barras, «a row of», «several»); todo a sangre con el cierre del Portal. La «zona reservada» en azul noche de r1-r5 (sección 9) es histórico | Portal, filas «Zonas limpias», «Recuentos», «Encuadre» (l.57, l.58, l.61) |
| Fondo y recorte | **Heredado:** lo que se recorta (logo, iconos sueltos) va sobre croma `#00ff00` y se recorta y vectoriza con `gimg brand`. **Propio:** ninguna pieza de voice lleva verde, así que no hace falta `#ff00ff`; **el frambuesa y el magenta están a un paso**: nunca croma `#ff00ff` en una pieza con acento | Portal, fila «Fondo y recorte» (l.59) |
| Versión oscura | **Heredado:** iconos y logo por CSS (`currentColor`), sin generar; un grabado, segunda generación con la misma semilla y la frase «printed in two inks on dark slate paper #0d171e: pale off-white #e6eef3 lines and medium cerulean ocean blue #0072a8 tints and shades», con el toque de acento igual (`#d9467a`: en imagen no se cambia de tono). Ninguna pieza de voice la necesita hoy | Portal, fila «Versión oscura» (l.60) |
| Perfiles | **Heredado:** los de `examples/portal/galivelop-images.json` (`cuadrado`, `icono`, `social`, `portada`, `tarjeta`, `cabecera`…), todos Z-Image. La tarjeta 15 se hizo con `tarjeta` del proyecto del Portal. Voice no tiene aún perfiles propios con la identidad vigente | Portal, fila «Perfiles» (l.62) |
| Referencias aprobadas | **Lo que gusta:** la tarjeta «Próximamente» de voz, **q331** (la onda como perfil del fondo, grabado a dos tintas, tercio inferior limpio), entregada y publicada en el Portal. **Histórico aprobado:** r1 «sí» de la persona (semillas 3 y 4, cinta rosa y anillos) con la identidad anterior; vale como antecedente del motivo (la onda que se enrosca), no como estilo. **Rechazado en la familia:** resplandores, degradados, marcos y bandas blancas | Portal `docs/marca.md` l.122, l.254 (`6574c4f`); `../portal/hoja.md` l.204; `docs/records/contenido/r1-fondos.md` l.46 |

**Cómo se escribe el prompt:** heredado entero de «Cómo se escribe el prompt» del Portal (`../portal/hoja.md` l.65-90):
orden, negaciones solo en el cierre, ningún color fuera de las tintas, 120-200 palabras, comprobación antes de encolar
(con el frambuesa donde aquel dice los cuatro hex). **Propio de voice**, además de lo vetado en toda la familia:

- **No se nombran** (ética, sección 2): `microphone`, `mic`, `headphones`, `speaker`, `studio`, `mouth`, `lips`, `face`,
  `person`, `singer`, `voice actor`, `human`. Tampoco como negación en el sujeto: el modelo pinta lo nombrado.
- **Nada que sugiera clonar la voz de alguien**: las voces son personas sintéticas (`GLOSSARY.md` l.43 de voces,
  «Voz»).
- **El acento no es adjetivo del sujeto:** «a raspberry wave» lo vuelve protagonista. El color lo pone solo la frase de
  paleta; el toque se sitúa describiendo la forma («one small mark on the chosen bar»).
- El pedido aprobado de la 15 nombra en el sujeto lo que no quiere («no rocks, no seaweed, no plants») y lleva el alga en
  la frase de paleta: **está aprobado y no se rehace**; si un día se regenera, va en positivo («a smooth bare seabed
  profile») y con la frase de paleta de voice.

**Dudas que decide la persona** (2026-11-12):

1. **Cerrada. Decidido por la persona (2026-11-12): el acento vivo es `#D9467A`** (hondo `#ce3c71`, oscura `#db487b`). El Portal cambia `src/data/productos/galivelop-voice-generator.json` l.5 de `#C9467A` a `#D9467A` (entrega al Portal, cambio 14). El cálculo con `#C9467A` (hondo `#c74479`, oscura `#d35083`) queda como histórico.
2. **Qué tono va en la imagen generada.** La decisión 3 dice «a touch of» el acento sin decir cuál de los tres.
   **Recomendación:** el vivo `#d9467a` en claro y en oscuro; el hondo y la oscura existen para texto en interfaz, y en
   un toque pequeño el modelo no distingue `#d9467a` de `#ce3c71` (contraste entre ellos, 1,13:1).
3. **Sobre el acento vivo no cabe texto.** El Portal pone la tinta sobre su vivo a 5,91:1; sobre `#d9467a` la tinta da
   3,99 y el blanco 4,11: ninguno llega a 4,5. **Recomendación:** en voice el vivo no lleva texto encima nunca (foco,
   punto de estado y tinte, que es para lo que está); el texto sobre color va sobre el hondo, en blanco (4,66).
4. **El acento se parece al peligro heredado.** `--peligro` `#a3135f` tiene tono OKLCH 356,0° y croma 0,183; el hondo
   de voice, 2,9° y 0,186: son 7° de diferencia y 1,60:1 entre ellos. **Recomendación:** mantener el peligro del Portal
   (la herencia manda) y cumplir a rajatabla su regla 6, peligro siempre con ✗ y texto, nunca solo color; se comprueba
   en la primera pantalla de F5 y, si se confunden, se vuelve a la persona.
5. **Nombre en el lockup.** El lockup común va en mayúsculas («GALIVELOP VOICE GENERATOR», como el `nombre` de la ficha
   del Portal, l.3); el repo se titula `galivelop-voice-generator`, en minúsculas y con guiones (`README.md` l.1), que
   era la regla de esta hoja. **Recomendación:** mayúsculas y sin guiones en el lockup (decisión 4 de la persona); el
   nombre con guiones se queda para código, rutas y texto corrido.
6. **Las piezas con título de r4-r5** (`og`, `cuadrado`, `vertical`, `cabecera` con lema compuesto) chocan con «ninguna
   imagen lleva texto». **Recomendación:** darlas por históricas y no rehacerlas; la tarjeta social sale sin texto y el
   título lo pone quien la publica. El lema y las frases de la sección 10 siguen valiendo como texto.

---

## Interfaz: tokens y reglas (2026-11-12)

Voice no tiene interfaz (llega en F5). Cuando la tenga, copia los tokens del Portal y cambia solo los del acento. Los
nombres de los tokens del acento son **[P]**: los fija su repo; los valores, no. Ratios WCAG 2.x calculados por
`tonos.py` sobre los hex, no medidos en pantalla.

**Heredado sin cambiar un valor** (tabla de tokens del Portal, `../portal/hoja.md` l.127-152, y «Qué se copia tal
cual», l.236-246): `--papel`, `--superficie`, `--fondo-alterno`, `--superficie-2`, `--tinta`, `--tinta-2`, `--texto-3`,
`--filete`, `--reticula` y `--reticula-paso` (24 px), `--peligro`, `--sobre-peligro`, `--peligro-tinte`, `--ok-texto`,
`--noche`, `--velo*`, `--sombra`, los tres chaflanes (28 / 14 / 10 px), `--curva` y `--transicion`; la tipografía por
papel (Big Shoulders Display 800/700 en mayúsculas, Literata 400/600 a 17 px / 1,6, JetBrains Mono 500 a 12 px con
tracking 0,06 em) y las once reglas de interfaz (l.160-178). Tema claro por defecto.

**Propio: el acento en el papel de `--celeste`, `--celeste-hondo`, `--enlace` y `--tinte`.**

| Token **[P]** | Claro | Oscuro | Papel que hace (el del Portal) | Contraste | Umbral y resultado |
|---|---|---|---|---|---|
| `--acento` (vivo) | `#d9467a` | `#d9467a` | El de `--celeste`: foco (`outline` 2 px), punto de estado, marca. Sin texto encima | sobre papel 4,00 / 4,41; blanco encima 4,11; tinta encima 3,99 | Mismo hex en los dos temas: cumple. No es texto sobre papel claro (4,00 < 4,5): cumple. Como elemento no textual pasa el 3:1 en los dos temas. **Tinta encima ≥ 4,5: no cumple** (Portal 5,91): duda 3 |
| `--acento-hondo` | `#ce3c71` | `#ce3c71` | El de `--celeste-hondo`: bloques grandes de color, enlaces en claro, cuadrado del logo, texto de acento | sobre papel `#fbfcfd` 4,53; sobre superficie `#ffffff` 4,66; blanco encima 4,66 | ≥ 4,5 sobre papel y blanco encima ≥ 4,5: **cumple** (Portal 5,15 y 5,29). En oscuro no se oscurece otro paso: los bloques con texto blanco usan este mismo hex (decisión 1, l.349-351) |
| `--enlace` | `--acento-hondo` | `#db487b` | El de `--enlace`: texto y enlaces sobre el papel oscuro | 4,53 / 4,51 sobre `#0d171e` | ≥ 4,5 sobre el papel de su tema: **cumple**. El Portal llega a 9,49 en oscuro; un producto lleva una sola variante oscura a 4,5 (decisión 1). **Límite:** sobre la superficie oscura `#111f29` da 4,17: los enlaces en fichas oscuras van subrayados o en tinta |
| `--tinte` | `#d9467a` al 12 % (`#f7e6ed` sobre papel) | al 18 % (`#321f2f` sobre papel) | El de `--tinte`: hover, chips, píldoras | tinta encima 13,67 / 13,03 | Mismos porcentajes y tinta ≥ 7: **cumple** (Portal 14,25 / 11,65) |
| Isobatas sobre el bloque | blanco al 20-50 % sobre `#ce3c71` | igual | Las del Portal sobre `--celeste-hondo`; en voice, la línea de la onda | — | Mismos porcentajes (heredado) |

**Lo que el producto no tiene:** acento secundario. En el Portal es el alga; junto al Portal, el secundario **es** el
acento de voice. En la interfaz de voice «hecho» es `--ok-texto` y el fallo `--peligro`, heredados; no se añade un
cuarto color.

**Relaciones del Portal, una a una** (`../portal/hoja.md` l.265-279): 1, 4, 5 y 6 se cumplen porque papel, tinta,
filete, retícula, velos y peligro son los mismos hex. 2 (un acento con dos tonos): cumple, vivo y hondo comparten tono
(2,8° y 2,9°) y croma. 3 (en oscuro el vivo no cambia, el tinte sube a 18 %): cumple; el hondo no se oscurece y el
enlace se aclara un paso, como fija la decisión 1. 7 (cuatro tintas en imagen, iconos de una): cumple con la frase de
paleta de arriba.

**Los tonos de la identidad anterior no pasan a la interfaz:** `#A62E5A` (6,47 sobre papel, elegido a ojo) y `#F6B1CA`
(10,41 sobre `#0d171e`) eran el «acento oscuro» y el «acento claro» de la sección 3. La decisión 1 pide tonos
calculados, así que los sustituyen `#ce3c71` y `#db487b`; se quedan en el histórico y en los SVG de `logos/`.

## Recursos: entregado, histórico y pendiente (2026-11-12)

| Recurso | Estado | Dónde está | Fuente |
|---|---|---|---|
| Tarjeta «Próximamente» de voz (recurso 15 del Portal) | **Entregada y publicada** (q331): la onda como perfil del fondo marino, 720×405 | Portal `public/proyectos/galivelop-voice-generator/proxima.webp`; pedido `examples/portal/orders/marca/15-proximamente-voz.json` | Portal `docs/marca.md` l.122, l.254 (`6574c4f`); `../portal/hoja.md` l.204 |
| Logo: símbolo | **Pendiente.** **Decidido por la persona (2026-11-12):** el símbolo es el monograma de iniciales en una tinta (papel `#fbfcfd`) sobre el cuadrado plano con chaflán de 28/128 en el tono hondo del acento; los logos anteriores (degradado, `rx` 30, Sora) pasan a histórico y no se copian a su repo. **Dependencia:** `gimg brand` no tiene aún la orden que monte el cuadrado con chaflán; se crea en este repo. Antes de la decisión: regla heredada: cuadrado plano del hondo `#ce3c71`, chaflán de 28/128 arriba a la derecha, dibujo de trazo 12/128 en una tinta, sin degradado ni redondeo; nace de gimg sobre croma `#00ff00` y se vectoriza con `gimg brand trace`. Dibujo propio: la onda que se enrosca (el concepto del `a`). **Hueco:** `gimg brand` no tiene hoy una orden que monte el cuadrado con chaflán alrededor del trazo, y a mano no se dibuja | — | `../portal/hoja.md` l.290, l.313 |
| Logos `a`-`d` y sus lockups | **Históricos.** Dibujados a mano el 2026-10 (`10d71ec`), baldosa `rx` 30 con degradado `#D9467A → #A62E5A` y nombre en Sora: no cumplen la regla del logo ni la del lockup. El `a` queda como boceto del dibujo; mientras no haya otro, es lo único que hay | `logos/galivelop-voice-generator-{a,b,c,d}.svg` y `-lockup.svg` | `../portal/hoja.md` l.374 («quedan como históricos») |
| Lockup común | **Pendiente** del símbolo y de la fuente. Nombre: `gimg brand wordmark "GALIVELOP VOICE GENERATOR" --font <Big Shoulders Display variable .ttf> --weight 800 --spacing 0.01`; lockups: `gimg brand lockup simbolo.svg wordmark.svg --layout h --cap 0.45 --gap 0.25 --margin 0.25` y `--layout v --width 1.6 --gap 0.25 --margin 0.25`. Nombre en `currentColor` (tinta), nunca en el acento. Mínimo: `S` ≥ 32 px en horizontal, ≥ 48 px en vertical; por debajo, el símbolo solo hasta 16 px. La fuente no está instalada en el equipo donde se escribió esta hoja (`fc-list`, 2026-11-12) | — | `../portal/hoja.md` l.358-374 (decisión 4) |
| Icono de proyecto (recurso 23 del Portal) | **Pendiente.** Línea simple, una tinta `#13212b`, nodos huecos, legible a 24 px: la ventana con la fila de barras. El Portal usa hoy el genérico `"icono": "audio"` | — | Portal `src/data/productos/galivelop-voice-generator.json` l.6; `../portal/hoja.md` l.212, l.292 |
| `og.jpg` del proyecto (recurso 24 del Portal) | **Pendiente.** Grabado, perfil `social`, la onda como perfil del fondo y el toque de frambuesa; sin texto | Portal `tools/og/fuentes/galivelop-voice-generator/og-fuente.png` | `../portal/hoja.md` l.213 |
| Tarjeta social del repo (GitHub, 1280×640) | **Pendiente**, la misma imagen que el 24 en perfil `social` | — | sección 11 |
| Iconos de interfaz (tomas, huella, cola, efectos) | **No hay y no se piden aún:** esperan a F5 y a la lista que haga su repo. Serán una serie entera, sin mezclar con lucide | — | voces `docs/plan.md` l.45; `../portal/hoja.md` l.292 |
| Piezas de r1-r5 (`og`, `cuadrado`, `vertical`, `cabecera`, `avatar`) | **Históricas**: azul noche, cinta de luz, título compuesto en Sora. Dos se ven en la ficha de image-generator del Portal como muestras del piloto (r3 y r5) y ahí se quedan | `piloto/` (fuera de git); Portal `src/data/proyectos/galivelop-image-generator.json` l.271-289 | secciones 9-12 |
| Proyecto de gimg | **Pendiente de reescribir**: `examples/galivelop-voice-generator/galivelop-images.json` lleva `brand.palette` y perfiles de la identidad anterior (FLUX, `#06121c`). No se toca desde esta tarea | `examples/galivelop-voice-generator/` | fila «Paleta» de arriba |

**Prompts propuestos para lo pendiente** (**[P]**, sin encolar; siguen el orden del Portal y se revisan con su punto 5):

- **Símbolo** (perfil `cuadrado`, sobre croma): «A single continuous line that enters from the left as a gentle sound
  wave and curls inward into a spiral of a few turns, centred, on a plain flat solid bright green #00ff00 background.
  Simple line icon style: one uniform stroke width, rounded caps and joins, no shading, no hatching, no fill, no
  texture, bold and clear enough to read at 24 pixels, generous empty margin around each icon, a single ink colour. No
  photographic rendering, no glow, no text, no letters, no numbers, no watermark, no border, no frame. Palette strictly
  limited to ink grey #13212b.» Se alarga hasta 120 palabras describiendo la forma, no el color.
- **Icono de proyecto** (perfil `icono`, sobre papel `#fbfcfd`): el mismo bloque de línea simple, con el sujeto «an
  application window holding a row of short vertical bars of varying height, a waveform, one bar underlined».
- **`og` y tarjeta social** (perfil `social`): el sujeto de la 15 en positivo («a sound wave drawn as a single depth
  profile line of a smooth bare seabed, crossing the upper two thirds from side to side; the lower third of the sheet is
  plain flat off-white paper, open and unmarked»), el bloque de grabado y la frase de paleta de voice.

## Familia Galivelop: lo que hereda y cómo se comprueba

Las seis comprobaciones de «Cómo se comprueba una hoja de producto» (`../portal/hoja.md` l.307-315), con el resultado
de hoy:

| # | Comprobación | Resultado |
|---|---|---|
| 1 | Tres hex del acento, calculados, con ratios; ninguno bajo 4,5 donde el método lo exige | **Pasa.** Vivo `#d9467a`, hondo `#ce3c71` (4,53 sobre `#fbfcfd`; blanco encima 4,66), oscura `#db487b` (4,51 sobre `#0d171e`). Salida literal abajo. Abierto: cuál es el vivo (duda 1) |
| 2 | Papel, tinta, filete, retícula, tipografías y chaflanes coinciden con el Portal valor por valor | **Pasa por remisión:** esta hoja no escribe otros valores; los cita |
| 3 | Frase de paleta del Portal con el acento en el lugar del alga; ningún prompt nombra otro color | **Pasa** en la frase y en los tres prompts propuestos. El pedido aprobado de la 15 lleva el alga: histórico aprobado |
| 4 | Logo: cuadrado plano del hondo, chaflán 28/128, trazo 12/128, salido de gimg | **No pasa:** no existe; los de `logos/` son los anteriores |
| 5 | Iconos de una tinta, sin relleno, nodos huecos, legibles a 24 px | **Sin iconos:** nada que comprobar |
| 6 | Nada de «Prohibido en toda la familia» | **Pasa** en los bloques vigentes. Lo incumplen, y por eso son histórico: el degradado y el `rx` de los logos, el «soft glow, smooth gradients» de `estilo.txt`, el texto compuesto de r4-r5 |

Salida de `python3 docs/marcas/galivelop-voice-generator/tonos.py '#D9467A' '#C9467A'` (2026-11-12). El mismo script
reproduce los ratios del Portal con `'#1aa6df'` (2,70 / 2,78 / 5,91 / 6,53 y tintes 14,25 / 11,65: `../portal/hoja.md`
l.135, l.142), que es la prueba de que calcula lo mismo:

```text
vivo   #d9467a  OKLCH L=0.6143 C=0.1869 h=2.78
       sobre #fbfcfd 4.00 | blanco encima 4.11 | tinta #13212b encima 3.99 | sobre #0d171e 4.41
hondo  #ce3c71  L=0.5843 C=0.1869 (6 pasos)
       sobre #fbfcfd 4.53 | blanco encima 4.66 | sobre #0d171e 3.89
oscuro #db487b  L=0.6193 C=0.1869 (1 pasos)
       sobre #0d171e 4.51
tinte  12 % sobre #fbfcfd = #f7e6ed, tinta encima 13.67 | 18 % sobre #0d171e = #321f2f, tinta #e6eef3 encima 13.03

vivo   #c9467a  OKLCH L=0.5892 C=0.1721 h=359.36
       sobre #fbfcfd 4.41 | blanco encima 4.53 | tinta #13212b encima 3.63 | sobre #0d171e 4.01
hondo  #c74479  L=0.5842 C=0.1721 (1 pasos)
       sobre #fbfcfd 4.51 | blanco encima 4.63 | sobre #0d171e 3.91
oscuro #d35083  L=0.6192 C=0.1721 (6 pasos)
       sobre #0d171e 4.53
tinte  12 % sobre #fbfcfd = #f5e6ed, tinta encima 13.61 | 18 % sobre #0d171e = #2f1f2f, tinta #e6eef3 encima 13.17
```

Una precisión del método que el texto del Portal no fija y `tonos.py` sí: cuando un paso cae fuera de sRGB, la croma se
baja **desde la del vivo en cada paso** (no se arrastra la rebaja al paso siguiente). Con el frambuesa no ha hecho
falta: ningún paso sale de sRGB.

**Qué ha cambiado en el repo de voces desde `ab1ff10`** (lo que las secciones históricas citan con línea vieja):

| Dato | En `ab1ff10` (secciones 0-15) | En `main` `5f67bd4` |
|---|---|---|
| Estado | «F0 hecha», «Aún no genera voces» (`README.md` l.10-13) | «F1 (núcleo) hecha … **Aún no genera voces de verdad**: el motor real llega en F2» (`README.md` l.12-13). La promesa de la sección 2 sigue igual: no se afirma que genera voces |
| Licencia | «Todavía no hay licencia» (`README.md` l.50) | Igual, ahora en l.70 |
| Orden | No había | `python3 -m gvoice` con `project`, `order`, `work`, `choose`, `attempt`, `undo`, `queue` (`README.md` l.18-33); solo motor `fake` (l.33) |
| Flujo | Galivelop-workflow v0.3.0, sin `gw-media-content` | Igual (`.claude/gw.json` `version`; `AGENTS.md` l.1) |
| Interfaz | Sin fecha | Fase F5 del plan (`docs/plan.md` l.45), sin empezar |
| Rama | `claude/voces-f1` | F1 fusionada en `main` por el PR #4; siguiente, F2 en rama nueva (`docs/traspaso.md`, «Estado actual») |

Lo que sale de aquí hacia su sesión está en
[`../../propuestas/galivelop-voice-generator/entrega-hoja-2026-11-12.md`](../../propuestas/galivelop-voice-generator/entrega-hoja-2026-11-12.md).

---

## Histórico (identidad anterior, r1-r5)

Desde aquí, la hoja del 2026-11-04 tal como se aprobó, con sus citas a `ab1ff10`. **No se sigue para piezas nuevas**;
valen las secciones 1 y 2 (identidad de voz y ética).

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «galivelop-voice-generator»: en minúsculas, con guiones, de una pieza (así va en el título de `README.md` y `README.en.md` y en el lockup). No tiene nombre «bonito»; en los textos del propio repo se le llama «el generador» | voces (`README.md` l.1, `README.en.md` l.1; `GLOSSARY.md` l.32-36, «Generador») |
| Nombre en código | Obl. | `galivelop-voice-generator` | repo (`examples/galivelop-voice-generator/galivelop-images.json`, `name`); coincide con el nombre del repo `github.com/Zeldris/galivelop-voice-generator` |
| Fuente de verdad | Rec. | galivelop-voice-generator `claude/voces-f1` `ab1ff10` (propósito, tono, vocabulario, idiomas, estado); Portal `aa76b34` (fondo, texto, tipografía, baldosa); este repo `fd2ae53` (acento, prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a voice-generator en las semillas 3 y 4); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2. El 2026-11-04 delegó las dudas de esta hoja y quedó aprobada (`docs/records/decisiones-hojas-2026-11-04.md`) | repo (`docs/records/contenido/r1-fondos.md` l.46 y l.52-53; `docs/marcas/README.md` l.24-38, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`: fondo, texto, tipografía y baldosa son los de la familia, sin cambios (Rec. aquí, no Obl.) | heredado de Portal-Galivelop `aa76b34` (vía `docs/marcas/portal/biblia.md` §2-§4); `docs/plan.md` l.662-665 («Herramientas del taller … entran en la familia del Portal **[P]**»; la familia está confirmada por las piezas de r1-r5, el acento sigue **[P]**) |
| Hereda de | Opc. | **Vigente:** [`../portal/hoja.md`](../portal/hoja.md), bloques «Identidad vigente» y «Familia Galivelop» (2026-11-12). **Histórico (piezas r1-r5):** Portal-Galivelop `aa76b34` (leído solo a través de `docs/marcas/portal/biblia.md`) | repo |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Generador de voces con IA local para desarrollo: un servicio por máquina que comparten varios proyectos»; con motor `qwentts.cpp`; **no conoce el dominio** (D3: sabe de voces, cadenas de efectos y frases); para los proyectos del taller (Tarkor/WMF el primero) que necesitan voces de NPC sin servicio externo | voces (`README.md` l.5-8; `docs/plan.md` D1-D3; `docs/adr/0002-generador-sin-dominio.md`) |
| Lema | Rec. | «Una voz, su huella, todas sus frases.» | **[P]** (`biblia.md` §1 y §6; no sale de ningún texto del repo de voces; sus tres palabras sí: «Voz», «Huella» y «Frase» son términos de `GLOSSARY.md` l.43-68) |
| Tono | Rec. | técnico, sobrio, honesto con el estado real («**Aún no genera voces**: el núcleo llega en F1 y el motor real en F2», `README.md` l.13); dice lo que no hace («No conoce el dominio», «Sin dependencias», «Todavía no hay licencia»); nunca vende, nada de «magia». El vocabulario se cuida palabra a palabra (cada término del glosario lleva su «Evitar») | voces (`README.md` l.5-16 y l.50; `GLOSSARY.md`); la lista «nunca vende, nada de magia», `biblia.md` §6 |
| Idiomas | Opc. | `es` manda (las piezas de r4-r5 van en español); el repo publica también en `en` (`README.en.md`; textos visibles es/en de F0; `visibleLanguages: ["es","en"]`), pero no hay pieza en inglés decidida | voces (`README.en.md`; `.claude/gw.json` `language: es`, `visibleLanguages`); pieza `en` **[P]** |
| Campo semántico | Opc. | dentro: generador, motor, voz, referencia, ficha de diseño, huella, frase, intento, **toma** (solo como palabra visible: en código es `attempt`), candidata, elegida, desfasada, cadena de efectos, paquete de voces, cola, candado de la máquina, perfil de máquina, carpeta de entrega; fuera (los «Evitar» del glosario): servidor, modelo (por motor), hablante, timbre, embedding, prompt, voz fijada, línea, diálogo, clip, filtro, preset, banco de voces, librería, cliente, mundo, juego, encargo, job, slug, prueba, variante. Añadidos por la biblia: clonar, «dar vida» | voces (`GLOSSARY.md` l.28-143, «Términos del proyecto», con sus «Evitar»); «clonar» y «dar vida» **[P]** (`biblia.md` §6: no están en el glosario) |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | rostros, bocas, labios, personas ni siluetas humanas; micrófonos, cascos, altavoces o estudios de grabación; robots o cerebros; chispas o «magia» de IA; nada que sugiera **clonar la voz de alguien**; texto generado por el modelo | repo (`docs/plan.md` l.666-667, herramientas: «*No:* robots, cerebros, rostros, personas reales (voces: nada que sugiera clonar a alguien), “magia” de IA»; `docs/marcas/README.md` l.179 «nada de micrófono, cara, boca ni persona»; `biblia.md` §1). El motivo sale del repo de voces: «Voz: una persona sintética reconocible, definida por su referencia elegida» (`GLOSSARY.md` l.43-46) y no hay texto sobre consentimiento ni clonación (`docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.198-199) |
| Personas y rostros | Rec. | nunca personas, rostros, bocas ni manos (vetados `face`, `person`, `singer`, `voice actor`, `human`, `mouth`, `lips`); nunca sugerir una persona real: las voces son personas sintéticas | repo (`biblia.md` §7; lectura l.198-199); voces (`GLOSSARY.md` l.43-46) |
| Promesas | Rec. | no afirmar que ya genera voces reales mientras el `README` diga «Aún no genera voces» (hoy hay un motor de pruebas, F1.5; el real llega en F2); **nada de licencia** («en abierto», «MIT»): el repo no tiene (`README.md` l.50), a diferencia de Workflow; nada de «clona tu voz» ni de voces de personas conocidas; nada de precios ni fechas; nada de «sin supervisión»: el humano elige la toma | voces (`README.md` l.10-13 y l.50; `docs/traspaso.md` «Estado actual», F1.5 con `FakeEngine`); clonar, lectura l.198-199; el resto `biblia.md` §1 |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. (familia Galivelop) | oscura (por defecto) `#06121c`; clara `#f6fafd` **[P]** (ninguna pieza clara hecha) | heredado de Portal-Galivelop `aa76b34` (`global.css` vía `portal/biblia.md` §2); repo (`galivelop-images.json` `brand.palette`; `piezas.json` `velo`) |
| Texto | Rec. (familia Galivelop) | `#eaf4fa` sobre oscuro (secundario `#9fb4c4`); `#0a1a28` sobre claro **[P]** (va con la pieza clara) | heredado de Portal-Galivelop `aa76b34`; `#eaf4fa` es el `color_texto` de las cuatro piezas compuestas de `piezas.json`; **ya está en `brand.palette`** (añadido el 2026-11-04, contradicción 3) |
| Acento | Obl. | `#D9467A` (frambuesa), uno por pieza: la cinta de onda en la imagen, la baldosa y el nombre del lockup; sobre fondo claro, `#A62E5A` | **[P]** (`docs/plan.md` l.665-666 «Acentos propuestos [P] … voces frambuesa `#D9467A`»; `docs/marcas/README.md` l.38 «Acentos de las herramientas … como se propusieron», decisión delegada); repo (`galivelop-images.json` `brand.palette`; `prompts/r2-hex.txt`; `logos/galivelop-voice-generator-a.svg`) |
| Acentos en imagen, en orden de peso y significado | Rec. | un solo acento con su tono claro, en este orden: frambuesa `#D9467A` (la cinta: la voz, la toma elegida), rosa `#F6B1CA` (los anillos finos y los halos: las tomas no elegidas, la huella), blanco `#FFFFFF` (las crestas de la cinta). Es el reparto de `r2-hex.txt` («rings … in #F6B1CA. The ribbon glows in #D9467A with soft highlights in #ffffff») | repo (`prompts/r2-hex.txt`, descartado en r2 pero es el que fija los hex de `brand.palette` y de la calibración); el significado de cada tono, **[P]** (`biblia.md` §2) |
| Resto de la paleta | Rec. | acento claro `#F6B1CA` **[P]**; acento oscuro `#A62E5A` (final del degradado de la baldosa; acento sobre claro) **[P]**; superficies `#0c1d2b`, `#11283a`; borde `#1b3447`; texto 2 `#9fb4c4`; blanco `#FFFFFF` (trazo del símbolo). `brand.palette` lleva 6: `#06121c`, `#F6B1CA`, `#D9467A`, `#ffffff`, `#eaf4fa` (el texto) y `#A62E5A` (el logo); los dos últimos entraron el 2026-11-04 | repo (`galivelop-images.json` `brand.palette`, de `prompts/r2-hex.txt`); superficies, borde y texto 2 heredados de Portal-Galivelop `aa76b34` (vía `portal/biblia.md` §2); los tres tonos frambuesa **[P]** (`biblia.md` §2) |
| Combinaciones | Rec. | oscura: `#06121c` + texto `#eaf4fa` + velo `#06121c:0` en `og` (contraste sobra, 16,97) y `#06121c:0.3` en `cuadrado`, `vertical` y `cabecera`; sobre imagen: texto `#eaf4fa` en la zona reservada que el prompt deja lisa, el logo siempre en su baldosa; clara **[P]**: `#f6fafd` + `#0a1a28` + acento `#A62E5A` | repo (`piezas.json`, `velo`, `color_texto`; `r4-composicion.md` l.21); la clara **[P]** (`biblia.md` §2, sin pieza hecha) |
| Prohibidos | Rec. | el celeste del Portal `#1aa6df` como acento de la herramienta; el violeta `#8B5CF6` del generador de imágenes (son gemelos: no se mezclan); rojo puro o magenta neón; negro `#000`; acento sobre acento; más de un acento por pieza | **[P]**, aprobada por delegación (`biblia.md` §2: lo escribió el agente; ninguna pieza lo ha puesto a prueba) |
| Degradados | Opc. | solo la baldosa del logo (`#D9467A → #A62E5A`) | repo (`logos/galivelop-voice-generator-a.svg`); regla de familia en `docs/marcas/README.md` «Común a todos» |

**Medido:** la calibración da a este proyecto paleta ≥ 72 % (r1 y r5: 75-86 %; r2 palabras 75,7 %; r5 cuadrado 80 %, vertical 81 %,
cabecera 75 %), con los 4 hex que entonces tenía `brand.palette` y ΔE76 < 15 (`docs/records/contenido/calibracion-measure.md` l.44 y l.74). **La og
compuesta de r4 midió 70,22 %**, por debajo de ese umbral (`r4-composicion.md` l.21): el texto `#eaf4fa` y el nombre del lockup no
contaban como paleta porque no estaban en `brand.palette`; ya están (ver «Contradicciones», 3), falta volver a medir. r2 confirmó que hex, palabras o materiales dan
casi la misma imagen (74,3 / 74,4 / 75,7 %); se eligió «palabras» porque material ensucia el fondo con textura (`r2-estilo.md`
l.27-29 y l.49).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/galivelop-voice-generator/logos/galivelop-voice-generator-a.svg` («onda que se enrosca»: una onda entra por la izquierda y se cierra en espiral, la huella de la voz; trazo blanco 12/128 con remates redondos en la baldosa de la familia, `rx` 30, degradado `#D9467A → #A62E5A`). Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; colores `#D9467A`, `#A62E5A`, `#FFFFFF` | repo (archivo, `10d71ec`); la elección de **a** es delegada **[P]** (`docs/marcas/README.md` l.18 y l.35: «la más propia; la **d** es una onda genérica»); el concepto «onda que se enrosca en una huella» es la metáfora del plan (`docs/plan.md` l.670) |
| Lockup (símbolo + nombre) | Rec. | `logos/galivelop-voice-generator-a-lockup.svg` (`viewBox 0 0 1100 128`): símbolo a la izquierda, nombre «galivelop-voice-generator» a la derecha en Sora 700, cuerpo 56/128, `#D9467A`, `letter-spacing` −1,5 (≈ −0,03 em), separación 28/128 (`x=156`). Lleva `<text>` con `font-family="Sora, sans-serif"` (reserva genérica), que la plantilla admite mientras `compose.fonts` garantice la fuente; el paso a trazos queda Opc. | repo (archivo, `10d71ec`); separación y tracking coinciden con `biblia.md` §3-§4 |
| Variante clara y oscura | Rec. | la baldosa lleva su propio fondo y vale sobre los dos; el nombre del lockup, `#D9467A` sobre oscuro (único archivo que existe) y `#A62E5A` sobre claro | **[P]** (`biblia.md` §4; solo existe el archivo para oscuro y nadie ha medido `#A62E5A` sobre `#f6fafd`) |
| Tamaño mínimo y margen | Rec. | símbolo 16 px; lockup 24 px de alto y por debajo solo el símbolo; margen libre un cuarto del lado de la baldosa; nombre a la derecha a 28/128 de separación, nunca debajo | **[P]** (`biblia.md` §4; reglas escritas por el agente al elegir) |
| Usos prohibidos | Opc. | cambiar el `rx` o el trazo, sacar el dibujo de la baldosa, rotar, recolorear, sombra o brillo, **convertir la onda en boca o en micrófono** | **[P]** (`biblia.md` §4) |
| Logo fuera de la paleta | Opc. | no hay: `#A62E5A` (final del degradado) está en el SVG, en `brand.palette` (desde el 2026-11-04) y en la tabla de la biblia | repo (`galivelop-images.json`, `biblia.md` §2) |

Copia en `examples/galivelop-voice-generator/logos/`: **no hay** (F2.10, dec. 3, pendiente); `piezas.json` apunta hoy a
`docs/marcas/…/logos/`. En r4 el lockup de 1100×128 salía a ~24 px de alto y el nombre no se leía; desde entonces el piloto lo pone al
9 % del alto de la pieza (`r4-composicion.md` l.29-33). El repo de voces no tiene favicon ni logo: el `a` sería el primero.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Rec. (familia Galivelop) | Sora 700 (reserva `sans-serif`); tracking −0,03 em en el wordmark. **Peso 700 en el titular**, como salió en r4-r5 (`componer.py` `peso_titulo=700`) y como pone la biblia; es la misma regla de los siete proyectos (`docs/records/decisiones-hojas-2026-11-04.md`) | heredado de Portal-Galivelop `aa76b34` (`Logo.tsx` vía `portal/biblia.md` §3); repo (`piezas.json` `fuente`; lockup `font-family="Sora, sans-serif"`; `examples/pilot/componer.py` l.119) |
| Familia de texto | Rec. | Inter (reserva `sans-serif`); **el subtítulo, Inter 400 con opacidad 0,82**, como salió en las piezas; el 500 solo en interfaz, no en pieza | heredado de Portal-Galivelop `aa76b34`; repo (`piezas.json` `fuente_texto`; `componer.py` l.159-160) |
| Licencia y archivo | Rec. | Sora e Inter, OFL, del repo `google/fonts`; `examples/pilot/fuentes.sh` las baja a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`. No instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)* | repo (`examples/pilot/fuentes.sh` l.8-12) |
| Tracking y mayúsculas | Opc. | títulos Sora −0,02 em; sin mayúsculas sostenidas (el nombre va en minúsculas, con sus guiones, en una línea y un solo color); monoespaciada del sistema para claves y órdenes (`orcos/guerrero-1`, `gvoice`) | heredado de Portal-Galivelop `aa76b34` (vía `portal/biblia.md` §3); monoespaciada **[P]** (`biblia.md` §3, sin pieza que la use); las claves, voces (`GLOSSARY.md` l.97-100; `docs/plan.md` D9) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivo propio (identidad vigente, 2026-11-11) | Obl. | **La onda como dato, no como sonido en el aire:** la forma de onda dibujada como una sola línea, el perfil de profundidad del fondo marino de una carta (lo que el Portal ya le pide en `orders/marca/15-proximamente-voz.json`: «a sound wave drawn as a single depth profile line of the seabed»); en icono, línea simple, las barras de tomas dentro de una ventana de aplicación («an application window holding a row of short vertical bars of varying height, a waveform»), sin número de barras y sin ninguna «encendida» (una tinta: la elegida se marca con un visto o un subrayado, no con color). Nada de micrófono, boca ni cara, como siempre. El pedido 15 nombra en el sujeto lo que no quiere («no rocks, no seaweed, no plants»): se reescribe en positivo («a smooth bare seabed profile») según el punto 2 de «Cómo se escribe el prompt». **Desde el 2026-11-12** el acento es además el «a touch of» de la frase de paleta (bloque «Identidad vigente», fila «Paleta»), no solo logo e interfaz | **propuesta del agente, 2026-11-11**, según `../portal/hoja.md` «Mar y tecnología»; pieza en `examples/portal/orders/marca/15-proximamente-voz.json` |
| Motivos Sí | Obl. | 1) una sola cinta de luz con forma de onda sonora («sound-wave ribbon») que entra desde el centro y se enrosca en anillos concéntricos finos hechos de hilos de luz (la huella de la voz); 2) frambuesa cálida con crestas blancas (la voz, la toma elegida); 3) azul noche profundo con rejilla tenue de puntos (la web del Portal). Sin usar aún, de la biblia: las barras de tomas con una encendida; los anillos concéntricos sueltos | repo (`prompts/estilo.txt`, «sí» de la persona en r1 sobre `og.txt`, elegido en r2; `docs/plan.md` l.670 «Voces: una cinta de onda que se enrosca en una huella»; `biblia.md` §7) |
| Motivos No | Obl. | micrófonos, cascos, altavoces, estudios, bocas, caras, personas, cantantes, actores de voz, robots, cerebros, chispas, texto | repo (`biblia.md` §7; `docs/plan.md` l.666-667; `docs/marcas/README.md` l.179) |
| Palabras vetadas | Obl. | `microphone`, `mic`, `headphones`, `speaker`, `studio`, `mouth`, `lips`, `face`, `person`, `singer`, `voice actor`, `human`, `robot`, `brain`, `sparkle`, `magic`, `text`, `letters`, `logo`; más `like` y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7). `estilo.txt`, `r2-*.txt` y `r5-*.txt` no las contienen (grep del 2026-11-04); `og.txt` y `orders/r1-og.json` llevan «shaped like a sound wave» y se **dejan como históricos** (prompt de r1, superado: r2 lo cambió a «sound-wave ribbon»; contradicción 4). **Vigente desde el 2026-11-11:** las palabras propias (micrófono, cascos, altavoz, estudio, boca, labios, cara, persona, cantante, actor de voz, robot, cerebro, texto) siguen vetadas por ética; el veto a `no`/`not`/`without`/`like` **no se aplica** a piezas nuevas: rige «Cómo se escribe el prompt» de `../portal/hoja.md` («shaped like a sound wave» dejaría de ser un problema; lo que importa es no nombrar en el sujeto lo que no se quiere) |
| Estilo de imagen | Rec. | «Style: minimal elegant digital art, thin precise luminous lines, soft glow, smooth gradients. Colours: deep midnight navy, raspberry pink, soft rose and white highlights. Mood: calm, warm, attentive.» | repo (`prompts/estilo.txt`, elegido en r2) |
| Lenguaje de forma | Opc. | ondas, barras, anillos y espirales; curvas continuas, plano, sin perspectiva ni sombra dura; una sola toma encendida; trazo 12/128 con remates redondos; `rx` 30/128 en la baldosa | repo (`biblia.md` §5; `logos/…-a.svg`); baldosa y trazo heredados de Portal-Galivelop `aa76b34` (`gv-logo.svg`) |

Prompts del proyecto (`examples/galivelop-voice-generator/prompts/`): `estilo.txt` (= `r2-palabras.txt`, **118 palabras**; elegido
en r2), `og.txt` (r1, 122; «sí» de la persona en semillas 3 y 4; lleva «shaped like»: histórico, superado por `estilo.txt`), `r2-hex.txt` (**115**) y `r2-material.txt` (131) (descartados), `r5-cuadrado.txt` (124), `r5-vertical.txt` (125),
`r5-cabecera.txt` (127) (compuestos y medidos), `r2-luz.txt` (160, sin veredicto). **Dos están por debajo de los 120 de la
plantilla** (`estilo.txt` y `r2-hex.txt`; el mínimo pasa a aviso, ver «Contradicciones», 2); `r2-control.json` tiene 119 y es histórico; los demás, 122-161. Todos acaban en «The image is completely
textless.».

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | la luz sale de la propia cinta (no hay fuente externa: «ribbon of light», «glowing concentric rings», «soft white highlights along its crests»); en `r2-luz.txt`: «the only light comes from the right», los anillos «centred a quarter of the way in from the right edge», «lighting the dark surface around it and fading into darkness toward the left» | repo (`prompts/estilo.txt`); la variante *(suposición: r2-luz sin veredicto)* |
| Momento y clima | Rec. | escena oscura, dicha al principio: «Dark wide abstract banner: the whole frame is deep midnight navy…» (r2-luz); en `estilo.txt` el fondo oscuro va en la primera frase («on a deep midnight navy background») | repo (`orders/r2-luz.json`) *(suposición)* |
| Luminosidad objetivo (YAVG) | Rec. | 33-55 (r1 y r5: 35-52; r2 palabras 46,0; r3 borrador 35 frente a 47 del definitivo; r4 og compuesto 52,6) | repo (`calibracion-measure.md` l.44 y l.74; `r2-estilo.md` l.29; `r3-borrador.md` l.51; `r4-composicion.md` l.21) |
| Saturación objetivo (SATAVG) | Rec. | 10-16 (r1 y r5: 11-15; r2 palabras 15,8; r4 og 16,02, justo en el borde) | repo (`calibracion-measure.md`; `r4-composicion.md` l.21) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **publicada dónde:** no hay. En el repo de voces, nada (sin web, sin og:image, sin favicon, sin `docs/media/`: no consta); social preview de GitHub: no comprobable desde el repo; en el Portal, **no tiene ficha ni portada** («Developer y voice-generator no tienen portada en el Portal, así que no tienen EMD»). Es el único de los siete proyectos, con developer, sin ninguna imagen de marca: la calibración se hizo solo con sus piezas del piloto. **Vale como referencia:** nada que valorar; **[P]** si la og compuesta de r4 pasa a ser la primera imagen de marca cuando la persona la apruebe | repo (`calibracion-measure.md` l.17-18 y l.76) |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 → 1200×630 (con `draft`), `social` 1280×640, `square` 1024×1024 → 1080×1080 (`cuadrado`), `portrait` 896×1152 → 1080×1350 (`vertical`), `header` 1536×512 → 1500×500 (`cabecera`). Los tres últimos, hechos en r5, se declararon el 2026-11-04 (F2.10, dec. 2 los había dejado fuera) | repo (`galivelop-images.json`; `piezas.json`; `docs/records/decisiones-hojas-2026-11-04.md`) |
| Zona reservada | Obl. | `og`, `social`, `header`: `izquierda 1/2` («The left half of the frame is a calm, smooth, dark navy surface, nearly empty and softly out of focus»); `square`, `portrait`: `arriba 1/2` («The upper half of the frame is a calm, smooth, dark navy surface…»). En píxeles (conversión de la plantilla): `og` entregado 1200×630 → `0,0,600,630`; `social` 1280×640 → `0,0,640,640`; `square` 1080×1080 → `0,0,1080,540`; `portrait` 1080×1350 → `0,0,1080,675`; `header` 1500×500 → `0,0,750,500`. La caja del piloto es 55 % del ancho menos margen (izquierda) o 48 % del alto (arriba), margen 6 %: no coincide con 1/2 y se alinea al portar a `compose` | repo (`prompts/*.txt`; `examples/pilot/componer.py` `caja_zona` l.105-115). Para `square` manda la mitad (`arriba 1/2`), la que pidió y midió r5; la biblia ya no dice «tercio» (ver «Contradicciones», 1) |
| Velo por perfil | Rec. | `og` `#06121c:0`; `cuadrado`, `vertical` y `cabecera` `#06121c:0.3` | repo (`piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza (57 px en el `og`), en lo alto de la caja de la zona con el título debajo, margen 6 %; solo baja si no cabe a lo ancho de la columna | repo (`componer.py` l.129-137; `r4-composicion.md` l.29-33) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 %, título Sora 700, subtítulo Inter 400). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-voice-generator-a.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5, limpio. `icon` 180/192/512: no hay; el repo de voces no tiene web ni favicon que lo consuma | repo (`piezas.json`; `r5-piezas.md` l.56); `icon` **[P]** |
| Borrador | Opc. | `draft: {scale: 0.5, steps: 4}` en `og` (declarado el 2026-11-04); r3 midió 640×320 a 4 pasos (51 s): YAVG/SATAVG/paleta 35/12/86 % frente a 47/16/75 % del definitivo, con la espiral anticipada y el hueco a la izquierda | repo (`galivelop-images.json`; F2.10, dec. 7; `r3-borrador.md` l.51 y l.62-64) |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia en r1-r5 sin boceto), sin LUT (paleta 75-86 %, dentro de rango), sin conversión final por parte de `gimg` | repo (`r1-fondos.md` l.46; `r5-piezas.md` l.35 y l.50-52) |
| Prioridad | Rec. | la de la biblia: 1) logo elegido y `avatar` 512; 2) `social` 1280×640 de GitHub; 3) `og` 1200×630. Hechas en el piloto: `avatar`, `og`, `cuadrado`, `vertical`, `cabecera`; `social` sale del mismo fondo que `og` sin recortar. `banner` 1600×640 solo si el Portal presenta las herramientas | repo (`biblia.md` §9; `docs/plan.md` l.667-668 y l.672) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | «Una voz, su huella, todas sus frases.» (37 caracteres), en `og` | **[P]** (`piezas.json`, r4; es el lema, que es propuesta) |
| Subtítulo | Rec. | «Voces con IA local: un servicio por máquina, para varios proyectos.» (**67**, ≤ 70; la forma del subtítulo de image-generator). `piezas.json` aún lleva la frase de 78 y se actualiza al recomponer el `og` | **[P]**, aprobada por delegación (decisión del 2026-11-04); la frase de `piezas.json` r4 es casi literal de la primera frase del `README.md` de voces (l.5: «Generador de voces con IA local para desarrollo: un servicio por máquina que comparten varios proyectos») |
| Variaciones, ganchos y cierres | Rec. | usados en r5: `cuadrado` «Cinco tomas, una elegida.» / «Voces sintéticas, elegidas toma a toma.»; `vertical` «Suena igual en cada frase.» / «La referencia manda; el motor puede cambiar.»; `cabecera` «Tú eliges la toma.» / «IA local: nada sale de tu equipo. Sin instalar nada.» | «Suena igual en cada frase» y «La referencia manda; el motor puede cambiar» resumen el glosario de voces («Voz: … suena igual en todas sus frases», `GLOSSARY.md` l.44; «Referencia: … la fuente de verdad de la voz, válida con cualquier motor futuro», l.49); «Sin instalar nada» resume «Sin dependencias: Python 3 solo con la biblioteca estándar» (`README.md` l.6); «Tú eliges la toma» es «Elegida: el intento que la persona escoge» (l.116); «toma» como palabra visible lo admite el glosario (l.104). El resto **[P]** (`biblia.md` §6; `piezas.json`): «cinco» no sale de ningún texto |
| Longitud máxima por campo | Rec. | la fija la composición: `componer.py` baja el cuerpo hasta 16 px y falla si el texto no cabe en la zona. Orientativo: titular ≤ 40 (los de r4-r5 van de 18 a 37), subtítulo ≤ 70 (el de `og` pasa a 67; los de r5, 39-52) | repo (`examples/pilot/componer.py` l.139-151; `piezas.json`) |
| Wordmark compuesto como texto | Opc. | el nombre va en el lockup (Sora 700, `#D9467A`), nunca como `text` del pedido | repo (lockup) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` | repo (`galivelop-images.json` `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto, escrito explícito) | repo (`delivery.template`) |
| Dónde se publica cada pieza | Rec. | `social`: social preview del repo `github.com/Zeldris/galivelop-voice-generator` (no comprobable desde el repo: lo fija la interfaz de GitHub); `avatar`: GitHub y Discord (no consta en el repo); `og`: no hay web ni `og:image` que lo consuma (no consta: el repo no tiene HTML); `banner` del Portal solo si la persona decide presentar las herramientas allí (hoy no están) | voces (remoto `origin`; ausencia de HTML, favicon y `docs/media/`); Portal y `banner` **[P]** (`biblia.md` §9; `docs/plan.md` l.663 «no … están en el Portal», l.667-668) |
| Otras piezas de marca que hace otro sistema | Rec. | **no hay hoy**: el repo de voces lleva Galivelop-workflow v0.3.0, sin la skill `gw-media-content` (sus skills son `gw-init`, `gw-update`, `gw-doctor`, `scout-updates`, `retro`, `opt-*`…). Cuando actualice el flujo (`gw-update` a 0.5.0) ganará `gw-media-content-now` con tarjetas 1200×675 HTML → PNG/WebP y paleta genérica «para sobrescribir según el proyecto»: entonces esta hoja es la fuente de sus hex, vía una nota `.claude/gw/gw-media-content.md` con `Palette:` (`--background: #06121c; --surface: #0c1d2b; --border: #1b3447; --text: #eaf4fa; --muted: #9fb4c4; --accent: #D9467A; --accent-text: #06121c`) y `--font: Sora, Inter, …` | voces (`.claude/skills/`, `.claude/gw.json` `version: 0.3.0`, `AGENTS.md` l.6); la nota propuesta **[P]** (se propondrá al repo de voces con el flujo nuevo, como en `../galivelop-workflow/hoja.md`, «Contradicciones», 1) |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto, no declarado) | repo (esquema) |
| Conversión final | Opc. | no hay | — |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona: r1 «sí» (2026-10-26, semillas 3 y 4: «Onda rosa y anillos concéntricos, a la derecha; en s4 una estela entra hacia el centro. Bien.»); r2-r5 delegado al agente. Apuntado en `docs/records/contenido/r1-fondos.md` l.46 y l.52-53, `r2-estilo.md` l.49 (elegida «palabras»), `r4-composicion.md` l.21, `r5-piezas.md` l.35 | repo |
| Contraste del texto | Rec. | ≥ 4,5:1 (por defecto); medido: og r4 16,97 (peor 16,34) sin velo; r5 cuadrado 15,46 (peor 14,6), vertical 15,89 (15,66), cabecera 15,07 (14,45) con velo 0,3. Todas sobre el 7:1 de AAA | repo (`r4-composicion.md` l.21; `r5-piezas.md` l.35) |
| Umbrales de medida | Rec. | los de las secciones 3 y 7: paleta ≥ 72 %, YAVG 33-55, SATAVG 10-16; «calibrado solo con piezas propias del piloto, sin imagen de marca» | repo (`calibracion-measure.md` l.74 y l.76) |
| EMD frente a la marca | Opc. | no hay: sin portada en el Portal ni imagen de marca propia, no hay referencia que medir («sin portada» en la tabla de umbrales). Cuando la persona apruebe una pieza como marca, se mide frente a ella y se fijan Cb/Cr (los gemelos dan ≤ 4 / ≤ 5) | repo (`calibracion-measure.md` l.17-18 y l.74) |
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» de la persona en r1 a la primera y estilo elegido en r2; r5 dio las tres piezas de formato a la primera («el estilo aguanta los formatos … la onda de voice-generator»). Pendiente solo el veredicto de la persona sobre lo delegado | repo (`r1-fondos.md` l.46; `r5-piezas.md` l.50-52) |

## 13. Fuentes de verdad

**galivelop-voice-generator**, `claude/voces-f1` `ab1ff10` (leído solo; nada modificado):

- `README.md` l.1 (nombre), l.5-8 (propósito, motor, D3, sin dependencias), l.10-13 («Estado»: F0 hecha, «Aún no genera
  voces»), l.50 («Todavía no hay licencia»); `README.en.md` l.1-8 (idioma `en`).
- `GLOSSARY.md` l.28-143, «Términos del proyecto» (campo semántico con sus «Evitar»; «Voz: una persona sintética…» l.43-46;
  «Referencia» l.48-51; «Huella» l.59-63; «Frase» l.65-68; «Intento … toma (solo como palabra visible)» l.102-105; «Elegida»
  l.115-118; «Clave del pedido» l.97-100).
- `docs/plan.md` D1-D3 (gemelo del de imágenes; herramienta de desarrollo; sin dominio), D9 (`gvoice`, `galivelop-voices.json`),
  D11 (aviso por deriva infantil: lo comprobable lo hace un script); `docs/adr/0002-generador-sin-dominio.md`.
- `docs/traspaso.md` «Estado actual» (F1.5 con motor de pruebas; F1.6 sin empezar).
- `.claude/gw.json` (`version: 0.3.0`, `language: es`, `visibleLanguages: ["es","en"]`, `pushToProtected: pr`); `AGENTS.md` l.6
  (Galivelop-workflow v0.3.0); `.claude/skills/` (sin `gw-media-content`).
- Remoto `origin`: `https://github.com/Zeldris/galivelop-voice-generator.git`.
- **No existe** en el repo: CSS, HTML, SVG, favicon, logo, imagen alguna, `LICENSE`, `docs/media/`, nota de `gw-media-content`.

**Portal-Galivelop** `aa76b34` (marca paraguas, «heredado de»), leído solo a través de `docs/marcas/portal/biblia.md`:
`src/estilos/global.css` (fondos `#06121c` / `#f6fafd`, texto `#eaf4fa` / `#9fb4c4` / `#0a1a28`, superficies `#0c1d2b`,
`#11283a`, borde `#1b3447`), `src/componentes/Logo.tsx` (Sora 700, −0,03 em), `public/marca/gv-logo.svg` (baldosa `rx` 30,
trazo 12).

**Este repo**, `f2-motor` `fd2ae53`:

- `examples/galivelop-voice-generator/galivelop-images.json` (`name`, `brand.palette` de 4 hex, `delivery`, perfiles `og` y
  `social`; último cambio `b65bd81`).
- `examples/galivelop-voice-generator/piezas.json` (fuentes Sora/Inter, textos, zona, color de texto y velo de las cuatro piezas
  compuestas, ruta del lockup y del avatar).
- `examples/galivelop-voice-generator/prompts/estilo.txt`, `og.txt`, `r2-palabras.txt`, `r2-hex.txt`, `r2-material.txt`,
  `r2-luz.txt`, `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` y `orders/r1-og.json`, `r2-control.json`, `r2-luz.json`
  (motivos, estilo, zona por formato, luz, hex de la paleta).
- `docs/marcas/galivelop-voice-generator/logos/galivelop-voice-generator-a.svg` y `-a-lockup.svg` (último cambio `10d71ec`); las
  propuestas `b`-`d` siguen en la carpeta.
- `docs/marcas/README.md` l.18 y l.35 (logo `a`, «Elegido por el agente»), l.38 (acento `#D9467A`), l.179-184 (conceptos de logo),
  «Común a todos» (destinos).
- `docs/marcas/galivelop-voice-generator/biblia.md` (paleta, tipografía, reglas del logo, vetos, frases; lo que es **[P]** allí lo
  sigue siendo aquí).
- `docs/plan.md` l.662-672 («Herramientas del taller»: familia del Portal **[P]**, acentos **[P]**, *No*, formatos, metáfora de las
  voces, primera ronda), l.752-754 (F2.10, dec. 2: `og` y `social` solo), F2.10 dec. 3 y 7 (logos dentro del ejemplo, `draft`).
- `docs/records/contenido/calibracion-measure.md` l.17-18, l.44, l.74, l.76; `r1-fondos.md` l.46, l.52-53, l.62;
  `r2-estilo.md` l.27-29, l.49, l.55; `r3-borrador.md` l.51, l.62-64; `r4-composicion.md` l.21, l.29-33; `r5-piezas.md` l.35,
  l.50-52, l.56.
- `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.196-200 (sección 3: qué es, límites «no hay texto sobre consentimiento ni
  clonación», metáfora).
- `examples/pilot/componer.py` l.105-115 (`caja_zona`), l.119 (`peso_titulo=700`), l.129-137 (logo al 9 %), l.139-151 (ajuste del
  texto), l.159-160 (subtítulo 400); `examples/pilot/fuentes.sh` l.8-12 (origen y licencia de las fuentes).

Sin línea aquí y por tanto **[P]** o *(suposición)*: el acento y sus tres tonos, el lema y las frases que no resumen el glosario, el
logo elegido (no su concepto), las reglas del logo tras elegir, la pieza clara, los prohibidos de la paleta, la monoespaciada, «clonar»
y «dar vida» como palabras fuera, `compose`, `icon`, el Portal como destino, la
nota `Palette:` para un `gw-media-content` que el repo aún no tiene.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo; al de voces no hay nada que proponer hoy):

- Hecho el 2026-11-04 en `galivelop-images.json`: `og` con `targetWidth` 1200 / `targetHeight` 630 y `draft`; `#eaf4fa` y `#A62E5A`
  en `brand.palette`; perfiles `square`, `portrait` y `header` con su destino. Falta volver a medir la og (70,22 % antes de añadir
  `#eaf4fa`) y poner el subtítulo de 67 caracteres en `piezas.json`.
- `compose`: plantilla, fuentes, zona, velo y logo en la pieza viven en `examples/pilot/componer.py`.
- `prompts/og.txt` y `orders/r1-og.json` llevan «shaped like a sound wave» (comprobación 8): se dejan como históricos;
  `estilo.txt` es el que manda.
- `prompts/estilo.txt` (118 palabras) y `r2-hex.txt` (115) quedan bajo los 120 de la comprobación 9, que pasa a aviso.
- Copia de los logos en `examples/galivelop-voice-generator/logos/`: pendiente (F2.10, dec. 3).

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; es la primera frase del `README.md` de voces) |
| 3 | «Nunca se muestra» no vacío | pasa; nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | pasa (6 hex); fondo `#06121c`, texto `#eaf4fa` y acento `#D9467A` están (la hoja nombra los roles, la configuración no los lleva) |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, `<title>`, sin `<text>`/`<image>`/`filter`; legible a 16 px según la elección de `docs/marcas/README.md`); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: sin `compose.fonts`, y las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts` |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | pasa en los históricos, salvo `og.txt` y `orders/r1-og.json` («shaped like»), históricos por decisión; `estilo.txt`, `r2-palabras/hex/material/luz.txt`, `r5-*.txt`, `orders/r2-control.json` y `r2-luz.json` pasan (comprobado el 2026-11-04 por palabra). **Para piezas nuevas no se aplica tal cual**: la comprobación es el punto 5 de «Cómo se escribe el prompt» de `../portal/hoja.md` |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | cierre pasa, los nueve; palabras: **aviso en tres** (`estilo.txt` 118, `r2-hex.txt` 115, `r2-control.json` 119; el mínimo es aviso desde el 2026-11-04), los otros 122-161 |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | múltiplos de 64 pasa; `og` 1200×630, `square` 1080×1080, `portrait` 1080×1350 y `header` 1500×500 declarados |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | el prompt la describe en los cuatro formatos; ningún perfil la declara (hueco: hasta `compose`, la zona vive en este documento y en `piezas.json`) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (37 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | pasa para los hex de la pieza oscura y del logo (`#eaf4fa` y `#A62E5A` entraron el 2026-11-04); no están el fondo claro `#f6fafd`, texto sobre claro `#0a1a28`, texto 2 `#9fb4c4` y las superficies (la clara no está hecha: entran con ella) |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | pasa (`og`, `square`, `portrait`, `header` declarados) |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 15** (familia Galivelop;
18 con la familia propia). Fondo, texto y titular son Rec. y están completos, heredados del Portal sin cambios.

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan: roles de la paleta (`brand.palette` no los distingue y le falta el del texto), zona
reservada (solo en prompt y en `componer.py`), velo y logo en la pieza (solo en `componer.py`), palabras vetadas sin campo (y un
prompt histórico con un «like»), `avatar` sin perfil (lo hace `piezas.py`), tipografía sin licencia ni ruta declaradas (las baja
`fuentes.sh`), imágenes de marca para la EMD sin lista (y aquí ni siquiera hay imagen: la calibración usó las piezas del piloto),
idiomas y textos por idioma (el repo publica en `es` y `en`; las piezas solo en `es`), copia de los logos en `examples/<p>/logos/`
pendiente. No le afectan: varias variantes de logo (la baldosa vale sobre claro y oscuro), `compose.lut` (paleta dentro de rango),
`style.lora`.

**Hueco propio de este proyecto:** es la única marca de las siete (con developer) **sin ninguna imagen de marca ni web**, así que
sus umbrales de `measure` se calibraron sobre sus propias piezas del piloto y no hay EMD posible. La primera og que la persona
apruebe pasa a ser la referencia; hasta entonces, «imagen de marca» es «no hay».

---

## Contradicciones

Entre el repo de voces (`ab1ff10`) y la biblia, o entre la biblia, la plantilla y lo que ya generó el motor.

1. **Resuelta: `arriba 1/2`** (criterios 2 y 3 de `docs/records/decisiones-hojas-2026-11-04.md`: lo compuesto y medido manda; una zona por perfil); la biblia §7 queda corregida. **Zona reservada del `square`.** Biblia §7: «en `square` **[P]**, el
   tercio superior». `prompts/r5-cuadrado.txt` y `r5-vertical.txt` piden «The upper half of the frame», `piezas.json` compone en
   `arriba` (48 % del alto) y la medida salió 15,46 (peor 14,6) y 15,89 (15,66). Es el mismo caso que Workflow resolvió el
   2026-11-04 a favor de la mitad. **Propuesta:** `arriba 1/2`; corregir la biblia §7.
2. **Resuelta: el mínimo de 120 pasa a aviso** (cambio de plantilla, ya aplicado); no se alarga `estilo.txt`. **Dos prompts bajo el mínimo de 120 palabras.** La plantilla (comprobación 9, «máquina») exige
   120-320 palabras; `estilo.txt`, el prompt que manda (= `r2-palabras.txt`, elegido en r2 y heredero del «sí» de r1), tiene 118, y
   `r2-hex.txt` 115. El prompt no está mal: es el más corto de los siete proyectos porque la escena es una sola cinta (image-generator
   va en 124-130, «en el suelo»). **Propuesta:** no alargar `estilo.txt` por dos palabras (cambiaría la imagen aprobada); dos
   salidas: (a) cuando r2-luz tenga veredicto, su versión de 160 palabras pasa a ser `estilo.txt` y la comprobación queda en verde;
   (b) la plantilla baja el mínimo o lo deja en aviso (ver «Cambios que pediría a la plantilla», 1). Mientras, la comprobación 9
   se apunta «no pasa en dos».
3. **Resuelta: `#eaf4fa` y `#A62E5A` entran en `brand.palette`** (hecho el 2026-11-04); queda volver a medir la og, y si sigue bajo 72 se fija el umbral en lo medido (≥ 70). **La og compuesta no llega a su propio umbral de paleta.**
   La calibración fija ≥ 72 % para este proyecto (de r1 y r5: 75-86 %), pero la og compuesta de r4 midió 70,22 %
   (`r4-composicion.md` l.21): el texto `#eaf4fa` y el nombre del lockup no están en los 4 hex de `brand.palette`, así que la
   composición baja el porcentaje. Image-generator lo arregló el 2026-11-04 añadiendo `#eaf4fa`; aquí no se hizo. **Propuesta:**
   añadir `#eaf4fa` (y `#A62E5A`, el del logo) a `brand.palette` y medir de nuevo la og; si sigue bajo 72, el umbral de las piezas
   compuestas se fija en lo medido (≥ 70) y se apunta en `calibracion-measure.md`.
4. **Resuelta: históricos.** `og.txt` y `orders/r1-og.json` se dejan como están, marcados históricos en esta hoja; `estilo.txt` manda. **«shaped like a sound wave» en `og.txt` y `orders/r1-og.json`.** Es el prompt de r1 (el que la
   persona aprobó) y lleva una comparación con «like», que la plantilla veta (comprobación 8); r2 lo cambió a «sound-wave ribbon»
   sin que la imagen cambiara (r2 palabras: «Igual que hex, con más aire a la izquierda»). **Propuesta:** como en Workflow:
   marcarlos como históricos (o retirarlos); `estilo.txt` ya es el que manda.
5. **Resuelta: se recorta a «Voces con IA local: un servicio por máquina, para varios proyectos.» (67)**; `piezas.json` se actualiza al recomponer. **Subtítulo del `og` de 78 caracteres.** La plantilla da ≤ 70 como orientativo
   (salido de las piezas de r5 a un tercio de `og`); este es el más largo de las cuatro piezas y entró porque la zona es la mitad,
   no un tercio. **Propuesta:** dejarlo (cupo y mide 16,97 de contraste) o acortarlo a «Voces con IA local: un servicio por
   máquina, para varios proyectos.» (65), que es la forma del subtítulo de image-generator.
6. **Resuelta: biblia al día** (citas de este repo a `fd2ae53`, `og.txt` marcado histórico). **Menor: biblia desfasada.** §Fuentes cita este repo en `24d69c8` (hoy `fd2ae53`) y la tabla de §8 dice que `og.txt` es «aprobado
   en r1» sin avisar de su «shaped like». El repo de voces sigue en `ab1ff10`, como dice la biblia; su `README.md` dice «F0 hecha» y la
   bitácora F1.5: la frase «Aún no genera voces» sigue siendo cierta (motor de pruebas), que es lo que importa a «Promesas».

## Cambios que pediría a la plantilla

**Aplicados el 2026-11-04** (mínimo de 120 palabras como aviso; licencia en «Promesas»). Voice-generator es la herramienta más parecida a image-generator (gemelas por diseño, D1 de su plan), y la plantilla con los 20
cambios ya aplicados le encaja casi entera. Pediría uno:

1. **El mínimo de palabras de la comprobación 9 como aviso, no como bloqueo** (o bajarlo a ~100). El prompt aprobado de este
   proyecto tiene 118 palabras y los de image-generator 124-130: las escenas abstractas de una sola figura se describen en menos
   palabras que un paisaje de Tarkor, y alargar un prompt aprobado solo para cumplir la cifra cambia la imagen. El máximo (320) sí
   protege de algo real (FLUX recorta); el mínimo solo mide longitud. Si se mantiene como bloqueo, que la fila diga qué se hace con
   un prompt ya aprobado que no llega.

Y una nota pequeña, sin fila nueva: en «Promesas», añadir la **licencia** a los ejemplos de lo que la pieza no puede afirmar («en
abierto», «MIT») cuando el repo no la tiene; aquí es el caso (`README.md` l.50) y no estaba en la lista de la plantilla (fechas,
precios, «contrata»).

Las tres filas nuevas del 2026-11-04 le valen: «Acentos en imagen» se rellena con los tres tonos de `r2-hex.txt` (un acento y su tono
claro, no tres acentos distintos como Workflow); «Otras piezas de marca que hace otro sistema» da «no hay hoy» con la razón (flujo
v0.3.0) y deja escrita la nota `Palette:` para cuando el repo actualice; las listas de canales «consta / no consta» dicen lo que hay:
nada en el repo y nada en el Portal.

---

## Lo que enseñó rellenarla

**Balance de este proyecto:** 15 obligatorios (familia Galivelop; fondo, texto y titular pasaron a Rec. y siguen completos, heredados
del Portal sin cambios); **12 completos desde un repo** (voces, Portal vía biblia o este), **3 [P]** (acento, logo elegido como
decisión delegada, titular), 0 «no hay». De los 67 campos de la plantilla, 15 son **[P]** en todo o en parte (lema, pieza `en`, «clonar»
y «dar vida», acento y sus tonos, significado de los tonos en imagen, pieza clara y sus valores, prohibidos de la paleta, logo
elegido, variantes, tamaños y márgenes, usos prohibidos del logo, monoespaciada, perfiles `square`/`portrait`/`header`, `compose`,
`icon`, `draft`, subtítulo y variaciones, Portal como destino) y 3 son «no hay» admitidos (`icon`, imágenes de marca, EMD). De los
recomendados, 5 «no hay» o no comprobables (composición por perfil, copia de logos, fuentes instaladas, imagen de marca, otro
sistema de piezas).

**Diferencia con image-generator:** misma familia, mismo esquema de hoja y los mismos tres [P] obligatorios, pero aquí tres de las
seis frases de r5 resumen el glosario del repo de voces (que define cada término con su «Evitar»), y el subtítulo del `og` es casi
literal de su `README`. A cambio, voice-generator es la marca con menos material de las siete: ni una imagen publicada, ni portada en
el Portal, ni licencia, y un flujo (v0.3.0) sin el generador de tarjetas que sí tienen Workflow y este repo. **Diferencia con
Workflow:** allí el repo traía otra paleta dentro (`gw-media-content`) que alinear; aquí no hay nada que alinear todavía, pero lo
habrá en cuanto el repo actualice el flujo, y la hoja ya deja escrita la nota `Palette:`.
