# Hoja de estilo: Galivelop IG

**r10 (2026-11-12): propuesta, pendiente de aplicar.** Reescribe la r9 (2026-11-11, aprobada y aplicada: `de53727`,
`1b211f6`, `e4b5db0`, PR #6 `2509674`) con la **estructura y las relaciones de la hoja del Portal**
([`../portal/hoja.md`](../portal/hoja.md), sección «Familia Galivelop: lo que heredan los productos», l.228-375) y las
cuatro **decisiones de la persona del 2026-11-12** (misma hoja, l.331-375): dos tonos de acento calculados, papel, tinta
y tipografías heredados sin cambio, el acento en el lugar del alga y lockup común. El violeta pasa a ser el que el Portal
tiene para este producto, `#7C5CD6` (Portal `6574c4f`, `src/data/productos/galivelop-image-generator.json` l.5, citado en
`../portal/hoja.md` l.323 y l.575).

**Qué es de quién en esta hoja:** lo **heredado** se copia del Portal valor por valor y se dice «heredado»; lo **propio**
(acento, símbolo, motivo, lema, y lo que una aplicación con formularios necesita y la web del Portal no tiene) va marcado
«propio» con su porqué; lo que sale de un cálculo lleva la orden que lo reproduce. **Nada de r10 está aplicado:** la
interfaz, los logos y las pruebas siguen en r9. Las diferencias, una a una, están en «Interfaz: diferencias con el código
de hoy» y los cambios que piden, en
[`../../propuestas/galivelop-image-generator/entrega-hoja-2026-11-12.md`](../../propuestas/galivelop-image-generator/entrega-hoja-2026-11-12.md).
Lo que r10 cambia de una decisión de r9 está en «Contradicciones» (r10) y lo decide la persona.

Sigue [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md) (F2.12) y complementa a [`biblia.md`](biblia.md),
que describe la identidad anterior a r9. Estados como en [`../README.md`](../README.md): **heredado** sale de
`../portal/hoja.md` (con su línea); **propio** sale de este repo (ruta y línea); **[P]** es propuesta pendiente de la
persona; *(suposición)* se comprueba en una ronda.

Commits de referencia: este repo `8bb0ae1` (rama `hojas-repos`); el Portal, solo a través de `../portal/hoja.md` en ese
commit (que cita Portal `6574c4f`); desde aquí no se abre ese repo. Contrastes: WCAG 2.x sobre hex de 8 bits, calculados
el 2026-11-12 con [`acento_oklch.py`](acento_oklch.py).

**Idea de marca** (de r9, se conserva). El Portal es una carta náutica: el mapa de todo el taller. Galivelop IG es **la
hoja de contactos sobre ese mismo papel**: una rejilla de intentos dibujada con la misma tinta y la misma línea, con un
solo intento marcado en violeta. El violeta no decora: señala **lo elegido** («Pide, prueba, elige.»). Todo lo demás es
del Portal.

| Heredado del Portal (no cambia ni un valor) | Propio de Galivelop IG |
|---|---|
| Papel `#fbfcfd` / `#0d171e`, superficie `#ffffff` / `#111f29`, tinta `#13212b` / `#e6eef3` y sus dos escalones | Acento violeta en dos tonos: vivo y hondo `#7C5CD6`, variante oscura `#896ae5` (calculados) |
| Filete, retícula de 24 px, peligro, «hecho», velos, noche | Símbolo «rejilla de intentos», siglas «GVIG», nombre «Galivelop IG» (D38) |
| Big Shoulders Display 800/700 en mayúsculas, Literata, JetBrains Mono | Motivo: la ventana con miniaturas y una elegida; lema «Pide, prueba, elige.» |
| Chaflán 28/14/10 px, `border-radius` 0, una sola sombra, sin degradados ni desenfoques | Lo de aplicación: borde de control a ≥ 3:1, aviso (`--warn`), foco de 3 px, objetivo táctil de 44 px |
| Dos registros de dibujo, Z-Image, reglas de prompt, lockup con las medidas comunes | Tamaños de título de aplicación (30 / 23 / 18 px) |

---

## Identidad vigente (2026-11-12): lo que gimg necesita

Lo que se aplica a cada pedido nuevo de `examples/galivelop-image-generator/`. Es la identidad vigente del Portal
(`../portal/hoja.md` l.40-117) con el acento del producto en el lugar del alga; donde esta sección y la del Portal digan
cosas distintas sobre algo heredado, manda la del Portal.

| Campo | Valor | Estado |
|---|---|---|
| Paleta | Cuatro tintas: cerúleo `#0072a8`, papel `#fbfcfd`, gris tinta `#13212b` y **violeta `#7C5CD6` solo como «a touch of»** (ocupa el lugar del verde alga `#5d7a6a`; nunca protagonista ni color dominante). Los grabados admiten «tints and shades» del cerúleo; los iconos, una sola tinta (`#13212b`). Versión oscura: fondo `#0d171e`, líneas `#e6eef3`, cerúleo igual. Frase final: «Palette strictly limited to medium cerulean ocean blue #0072a8, off-white #fbfcfd, ink grey #13212b and a touch of violet #7C5CD6.» (en grabados, «…#0072a8 and its tints and shades, …»). El nombre «violet» es *(suposición)*: «sky blue» desvió el cerúleo en el Portal, así que la primera ronda mide si «violet #7C5CD6» da ese hex. **Hoy** `brand.palette` lleva los 5 hex de la identidad anterior (`examples/galivelop-image-generator/galivelop-images.json` l.6-12) y no se toca hasta medir la ronda plana (r9, contradicción 7) | heredado (`../portal/hoja.md` l.52, l.262, l.278-279; frase literal en `examples/portal/prompts/estilo.txt` y `examples/portal/orders/marca/06-portada-diseno.json`); el cuarto color, **decisión de la persona 2026-11-12**, punto 3 (l.360-362) |
| `brand.palette` propuesto | Las siete del Portal con el violeta en el sitio del alga: `#0072a8`, `#1aa6df`, `#fbfcfd`, `#13212b`, `#7C5CD6`, `#e6eef3`, `#0d171e` (`#1aa6df` solo para que `gimg measure` cuente el celeste que el modelo tiende a dar) | **[P]**, según `../portal/hoja.md` l.52; se aplica con la ronda plana |
| Tipografía | Big Shoulders Display, Literata, JetBrains Mono. **Ninguna imagen generada lleva texto.** Las piezas compuestas (`og`) ponen el texto con `compose`: hoy Sora e Inter (`galivelop-images.json` l.41-44); con la ronda plana, las tres de la familia | heredado (l.53); lo de `compose`, propio |
| Modelo y parámetros | Calidad: `zimage-turbo-q6`, 8 pasos, cfg 1.0, euler, base 1024, `draft {scale 0.5, steps 4}`. FLUX (`flux2-klein-4b-q8`, 6 pasos) solo bocetos. Sin prompt negativo. **Hoy** los perfiles `og` y `social` llevan FLUX a 6 pasos (`galivelop-images.json` l.19-24, l.48-55): son los de las piezas r1-r8 | heredado (l.54) |
| Mar y tecnología | El mar pone el dónde (carta, isobatas, papel, cerúleo); la tecnología, el qué. Ningún motivo náutico protagonista; las tres excepciones son del Portal y esta hoja no añade ninguna | heredado (l.55, l.295) |
| **Motivo propio** | **La cola y la elegida, en informática:** una ventana de aplicación con una fila de miniaturas (celdas de una retícula), una marcada con un visto. Grabado: la ventana sobre el mar de carta. Línea simple: la ventana sola. En el prompt: «an application window holding a row of small thumbnails, one of them marked with a tick» (sin número de miniaturas). El toque de violeta va **en la elegida** y en nada más | propio (r9 §6, propuesta del agente del 2026-11-11); sin pieza generada |
| Dos registros de dibujo | Grabado a dos tintas para lo grande (cabeceras, `og`, portada); línea simple para iconos y símbolo. Los bloques literales son los del Portal; no se mezclan en una pieza | heredado (l.56) |
| Zonas limpias | La zona de texto se describe en positivo y al principio, como papel; la trama se confina; «filling the whole sheet to every edge» nunca junto a una zona limpia | heredado (l.57) |
| Recuentos | Sin «exactly N». La rejilla del símbolo (2×2, una celda encendida) **sí depende del número**: lo generado es boceto y el número se fija al vectorizar | heredado (l.58); lo del símbolo, propio |
| Fondo y recorte | Sin transparencia: lo que se recorta va sobre croma `#00ff00` (la paleta no lleva verde, no hace falta `#ff00ff`) y pasa por `gimg brand matte` y `trace` | heredado (l.59) |
| Versión oscura | Iconos y logo: por CSS (`currentColor`), sin generar. Grabados: segunda generación con la misma semilla y las tintas cambiadas | heredado (l.60; propuesta del agente allí) |
| Encuadre | A sangre: «full-bleed edge to edge, no border, no frame, no white margin, no blank band». El chaflán no se pide al modelo | heredado (l.61) |
| Perfiles | Hoy: `og` 1280×640 → 1200×630 y `social` 1280×640 (`galivelop-images.json` l.18-55). Para la ronda plana **[P]**: los mismos tamaños con Z-Image; `cuadrado` 1024² para símbolo e iconos (como `examples/portal/galivelop-images.json`) | propio; el modelo, heredado |
| Referencias aprobadas | Del registro: las del Portal (q310, q311; l.63). Propias en la identidad vigente: **ninguna** (no hay ronda plana). Las piezas r1-r8 (vidrio sobre `#06121c`) son de la identidad anterior | repo (`docs/handoff.md` l.18: «Queda, en otra tarea: medir una ronda plana y `og`/`social` con el lockup nuevo») |

**Cómo se escribe el prompt:** como en el Portal (`../portal/hoja.md` l.65-90), sin cambios: orden sujeto → zona limpia
→ bloque del registro → cierre → frase de paleta; negaciones solo en el cierre; ningún color fuera de las tintas, ni como
adjetivo (el violeta solo aparece en la frase de paleta); 120-200 palabras; `seed` fijo y `count` 2-4. **Propio:** siguen
vetadas por ética y motivo `camera`, `lens`, `brush`, `paint`, `palette`, `easel`, `canvas`, `sparkle`, `spark`, `magic`,
`robot`, `brain`, `face`, `person`, `artist`, `gallery` (`biblia.md` l.98-99).

## Acento: los dos tonos, calculados

Método de la decisión 1 de la persona (`../portal/hoja.md` l.333-345). Orden que lo reproduce, desde la raíz del repo:

```
python3 docs/marcas/galivelop-image-generator/acento_oklch.py '#7C5CD6'
```

| Tono | Hex | OKLCH | Cómo sale | Ratios |
|---|---|---|---|---|
| **Vivo** | `#7C5CD6` | L 0,5690 · C 0,1795 · h 291,77 | el hex del Portal para este producto | sobre papel `#fbfcfd` 4,69; sobre `#0d171e` 3,76; blanco encima 4,82; tinta `#13212b` encima 3,41 |
| **Hondo** (tema claro) | `#7C5CD6` | el mismo | **es el vivo:** ya da ≥ 4,5:1 sobre el papel, y la regla 5 del método dice que entonces no se busca otro (0 pasos) | sobre papel 4,69; blanco `#ffffff` encima 4,82; sobre superficie `#ffffff` 4,82 |
| **Variante oscura** | `#896ae5` | L 0,6140 · C 0,1795 · h 291,77 | L sube 9 pasos de 0,005; C no baja (cabe en sRGB) | sobre `#0d171e` 4,54; sobre superficie `#111f29` 4,20; blanco encima 3,99 |
| Tinte claro | `#ece9f8` | — | vivo al 12 % sobre `#fbfcfd` | tinta encima 13,73; hondo encima 4,03 |
| Tinte oscuro | `#21233f` | — | vivo al 18 % sobre `#0d171e` | tinta `#e6eef3` encima 12,99; variante oscura encima 3,82 |

El método se comprobó con los datos del Portal: da para `#7C5CD6` los mismos 4,69 / 4,82 / 3,76 que su tabla
(`../portal/hoja.md` l.323).

**Qué relación del Portal se cumple y cuál no** (tabla «Qué cambia», `../portal/hoja.md` l.256-263):

| Relación del Portal | Aquí | Resultado |
|---|---|---|
| Vivo: el mismo hex en claro y oscuro | `#7C5CD6` en los dos | cumple |
| Hondo: ≥ 4,5:1 sobre papel y blanco encima ≥ 4,5:1 | 4,69 y 4,82 | cumple |
| Variante oscura: texto y enlaces sobre `#0d171e` a ≥ 4,5:1 (el método; el Portal llega a 9,49 con `#5cc8f2`) | 4,54 | cumple el método, **justo** |
| Tinte al 12 % / 18 %, tinta encima ≥ 7:1 | 13,73 / 12,99 | cumple |
| Bloques con texto blanco: el hondo, también en tema oscuro | blanco sobre `#7C5CD6` 4,82 (sobre `#896ae5` daría 3,99: por eso no) | cumple |
| Vivo sobre el papel oscuro ≥ 4,5:1 (Portal 6,53) | 3,76 | **no cumple** como texto; vale para foco y puntos de estado (≥ 3:1) |
| Sobre el vivo solo va la tinta, a ≥ 4,5:1 (Portal 5,91) | tinta 3,41; blanco 4,82 | **al revés que en el Portal:** aquí vivo y hondo son el mismo hex, así que encima va el **blanco**, nunca la tinta |
| Un acento con dos tonos (hondo en superficie grande, vivo en puntos) | un solo hex en claro | **se pierde la diferencia de tono en claro**; queda en oscuro (`#7C5CD6` relleno, `#896ae5` texto) |

**Dónde no llega el texto de acento** (el método solo exige el papel; una aplicación pone enlaces dentro de fichas):

| Texto de acento sobre | Hex del método | Ratio | Tono que haría falta, con el mismo método (`--sobre <fondo>`) |
|---|---|---|---|
| Superficie clara `#ffffff` | `#7C5CD6` | 4,82 | — |
| Banda alterna clara `#f1f6f9` | `#7C5CD6` | 4,43 | `#7b5ad4` (4,53) |
| Tinte claro `#ece9f8` | `#7C5CD6` | 4,03 | `#7453cc` (4,56; sobre papel 5,31; blanco encima 5,45) |
| Superficie oscura `#111f29` | `#896ae5` | 4,20 | `#8f70ec` (4,55) |
| Segundo plano oscuro `#16242e` | `#896ae5` | 3,96 | `#9375f1` (4,57) |
| Tinte oscuro `#21233f` | `#896ae5` | 3,82 | `#9577f3` (4,51; sobre `#0d171e` 5,36) |

**Regla de esta hoja mientras la persona no decida otra cosa (pregunta 2):** el texto de acento (enlaces, «IG», rótulos
en violeta) va solo sobre el papel o sobre `#ffffff`; dentro de una ficha oscura, sobre una banda alterna o sobre el
tinte, el texto va en tinta y el acento se queda en el borde, el subrayado o el punto. Los hex de la última columna están
calculados, no adoptados.

## Interfaz: tokens y reglas

Qué valor lleva cada papel en la interfaz de Galivelop IG. «Portal» es el token de `../portal/hoja.md` l.127-152; «Aquí»,
el nombre en `gimg/ui/css/tokens.css`.

| Papel | Portal → aquí | Claro | Oscuro | Contraste (claro / oscuro) | Origen |
|---|---|---|---|---|---|
| Fondo de página | `--papel` → `--bg` | `#fbfcfd` | `#0d171e` | — | heredado |
| Fichas y paneles | `--superficie` → `--surface` | `#ffffff` | `#111f29` | tinta encima 16,40 / 14,29 | heredado |
| Segundo plano, bandas | `--fondo-alterno`, `--superficie-2` → `--surface-2` | `#f1f6f9` | `#16242e` | tinta encima 15,07 / 13,49 | heredado |
| Texto y línea | `--tinta` → `--text` | `#13212b` | `#e6eef3` | 15,97 / 15,44 | heredado |
| Texto secundario | `--tinta-2` → `--text-2` | `#4a5c69` | `#9fb2bf` | 6,76 / 8,28 (sobre superficie 6,94 / 7,66) | heredado |
| Texto terciario | `--texto-3` → `--text-3` (nuevo) | `#5a6d7a` | `#7d919e` | 5,24 / 5,54 | heredado |
| Filete, bordes de 1 px | `--filete` → `--rule` | `#b9cbd6` | `#2b3d49` | 1,63 / 1,61 (estructura) | heredado |
| Retícula de 24 px | `--reticula`, `--reticula-paso` → `--grid`, `--grid-step` (nuevos) | `#e3edf3` | `#16242e` | 1,16 / 1,14 | heredado |
| **Borde de control** | no hay → `--border` | `#6f8493` | `#6f8493` | 3,79 / 4,66; sobre superficie 3,89 / 4,31 | **propio:** campos y botones de formulario necesitan ≥ 3:1 (WCAG 1.4.11) y el filete del Portal da 1,63; se conserva el de r9 (`tokens.css` l.17) |
| **Acento vivo** | `--celeste` → `--accent`, `--focus` | `#7C5CD6` | `#7C5CD6` | sobre fondo 4,69 / 3,76; sobre superficie 4,82 / 3,48; sobre segundo plano oscuro 3,29 (≥ 3:1 en todos) | propio, calculado |
| **Acento hondo** | `--celeste-hondo` → `--accent-fill` | `#7C5CD6` | `#7C5CD6` | blanco encima 4,82 | propio, calculado |
| Texto sobre el acento | — → `--on-accent` | `#ffffff` | `#ffffff` | 4,82 | heredado (la relación) |
| **Texto de acento** | `--enlace` → `--accent-text` | `#7C5CD6` | `#896ae5` | 4,69 / 4,54 (ver «Dónde no llega») | propio, calculado |
| **Tinte** | `--tinte` → `--accent-soft` | vivo al 12 % (`#ece9f8`) | vivo al 18 % (`#21233f`) | tinta encima 13,73 / 12,99 | heredado (porcentajes), calculado |
| Enlace al Portal | `--celeste-hondo`, `--enlace` → `--family` | `#0072a8` | `#5cc8f2` | 5,15 / 9,49 (sobre superficie 5,29 / 8,79) | heredado: es un enlace del Portal y lleva su color de enlace; ≤ 2 % (r9, contradicción 5) |
| «Hecho», la elegida | `--ok-texto` → `--ok` | `#3f5a4b` | `#8fb09e` | 7,37 / 7,66; texto encima (`--on-status`) 7,57 / 7,66 | heredado; siempre con ✓ o texto |
| Fallo | `--peligro` → `--bad` | `#a3135f` | `#f27ab0` | 7,26 / 7,07; texto encima 7,46 / 7,07 | heredado; siempre con ✗ y texto |
| **Aviso** | no hay → `--warn` | `#8a5a00` | `#f2c14e` | 5,77 / 10,80; texto encima 5,93 / 10,80 | **propio:** el Portal no tiene color de aviso (su alga hace de «aviso suave» y aquí ese sitio es del violeta); se conserva el de r9 (`tokens.css` l.29, l.69). Pregunta 4 |
| Texto sobre estado | → `--on-status` | `#ffffff` | `#0d171e` | arriba | heredado (`--sobre-peligro`) |
| Sombra, solo panel flotante | `--sombra` → `--shadow` | `0 12px 32px -18px` tinta al 35 % | negro al 70 % | — | heredado |
| Velo sobre imagen | `--velo` → `--overlay` | `rgb(6 18 28)` al 62 / 68 / 78 % | igual | blanco encima, peor caso 5,33 | heredado |
| Chaflán | `--chaflan-grande` / `--chaflan` / `--chaflan-pequeno` → sustituyen a `--r`, `--r-s` | 28 / 14 / 10 px | igual | — | heredado |
| **Foco** | `outline` 2 px → `--focus-w` | 3 px | 3 px | — | **propio:** la máquina de referencia es la Steam Deck (D4) y el foco se ve a distancia; se conserva (`tokens.css` l.46) |
| **Objetivo táctil** | no hay → `--tap` | 44 px | 44 px | — | propio (`tokens.css` l.43) |

**Tipografía por papel.** Heredado (`../portal/hoja.md` l.154-158): títulos en **Big Shoulders Display** 800 (h1-h3) y
700 (h4), en mayúsculas, tracking 0,01 em, interlineado 1,02; texto en **Literata** 400/600 a 17 px / 1,6; datos
(etiquetas, fechas, versiones, semillas, hex, rutas, botones) en **JetBrains Mono** 500, 12 px / 1,4, en mayúsculas,
tracking 0,06 em. Las tres van servidas sin red desde `gimg/ui/fonts/` (D6; `tokens.css` l.6-8), con licencia OFL
(`gimg/ui/fonts/OFL.txt`). **Propio:** los tamaños de título son de aplicación, no de página web: h1 30 px, h2 23 px,
h3 18 px (`gimg/ui/css/base.css` l.14-16), no el `clamp(44px, 9vw, 96px)` del Portal; el peso, la caja y el tracking sí
son los heredados. Regla de uso (r9): lo que la herramienta **dice**, en Literata; lo que **mide**, en JetBrains Mono; lo
que **nombra**, en Big Shoulders Display.

**Reglas de interfaz**, las once del Portal (`../portal/hoja.md` l.160-178), heredadas: 1) tema claro por defecto; 2) sin
resplandores, desenfoques ni degradados (`backdrop-filter`, `blur(`, `-gradient(`, `drop-shadow(`, sombra difusa);
3) esquinas rectas o con chaflán, `border-radius` 0 salvo el punto de estado; 4) líneas antes que sombras; 5) datos en
monoespaciada y mayúsculas; 6) el acento, en bloques grandes y planos; 7) la retícula de 24 px se ve; 8) numeración
real; 9) movimiento de 200 ms y 2-3 px; 10) AA sobre el acento (aquí, blanco sobre `#7C5CD6`: 4,82); 11) los diagramas
siguen la hoja. **Excepción propia a la 3:** el indicador de espera (`.spin`, `base.css` l.137) y el punto de estado son
redondos; todo lo demás, recto.

### Interfaz: diferencias con el código de hoy

Código leído en `8bb0ae1`. Cada fila es una diferencia entre esta hoja y la interfaz real; el cambio que pide está en la
entrega, con el mismo número.

| # | Qué | Hoy (archivo y línea) | Esta hoja |
|---|---|---|---|
| D1 | Acento de texto y borde, claro | `--accent`, `--accent-text` `#5B34C9` (`tokens.css` l.21-22) | `#7C5CD6` |
| D2 | Relleno del botón primario | `--accent-fill` `#5B34C9` en los dos temas (l.23, l.63, l.89); blanco encima 7,56 | `#7C5CD6`; blanco encima 4,82 |
| D3 | Acento en oscuro | `--accent`, `--accent-text` `#A78BFA` (l.61-62, l.87-88); 6,66 sobre `#0d171e` | `--accent` `#7C5CD6`, `--accent-text` `#896ae5` (4,54) |
| D4 | Violeta de marca | `--brand` `#8B5CF6` (l.26, l.66, l.92) | desaparece: el vivo `#7C5CD6` hace ese papel |
| D5 | Foco | `--focus` `#5B34C9` / `#A78BFA` (l.32, l.72, l.98) | `#7C5CD6` en los dos temas (≥ 3:1) |
| D6 | Fondo de selección | `--accent-soft` `#e8e0fa` / `#241a4a`, «[derivado]» (l.25, l.65, l.91) | tinte: vivo al 12 % / 18 % (`#ece9f8` / `#21233f`) |
| D7 | Superficie | `--surface` `#e6eef3` / `#13212b` (l.13, l.55, l.81) | `#ffffff` / `#111f29` |
| D8 | Segundo plano | `--surface-2` `#d9e4eb` / `#1b2e3b`, «[derivado]» (l.14, l.56, l.82) | `#f1f6f9` / `#16242e` |
| D9 | Texto secundario | `--text-2` `#4a5b66` / `#9fb4c4` (l.20, l.60, l.86) | `#4a5c69` / `#9fb2bf` |
| D10 | Texto terciario | no existe | `--text-3` `#5a6d7a` / `#7d919e` |
| D11 | Filete | `--rule` `#c9d5dd` / `#2b3d4a` (l.18, l.58, l.84) | `#b9cbd6` / `#2b3d49` |
| D12 | Retícula | no existe | cuadrícula de 24 px, `#e3edf3` / `#16242e`, líneas de 1 px |
| D13 | Enlace al Portal en oscuro | `--family` `#1aa6df` (l.67, l.93) | `#5cc8f2` |
| D14 | «Hecho» | `--ok` `#1b7a3e` / `#5ad38a` (l.28, l.68, l.94) | `#3f5a4b` / `#8fb09e` |
| D15 | Fallo | `--bad` `#b3261e` / `#ff7b6b` (l.30, l.70, l.96) | `#a3135f` / `#f27ab0` |
| D16 | Sombra | dos capas difusas, `0 1px 2px` y `0 8px 24px` (l.33; oscuro l.73, l.99) | una: `0 12px 32px -18px`, solo en panel flotante |
| D17 | Velo | `--overlay` `rgb(13 23 30 / .72)` / `.78` (l.34, l.74, l.100) | `rgb(6 18 28)` al 62-78 % |
| D18 | Radios | `--r` 12 px, `--r-s` 8 px (l.40-41), y además `999px` (`base.css` l.95, l.125-128), `4px` (`base.css` l.106; `layout.css` l.40-41, l.69-70), `50%` en muestras, pasos y tiradores (`components.css` l.66, l.154, l.92) | `border-radius` 0; chaflán de 28 / 14 / 10 px arriba a la derecha; redondo solo el punto de estado (`layout.css` l.21, l.25) y el indicador de espera |
| D19 | Desenfoque | `backdrop-filter: blur(4px)` en las etiquetas sobre la imagen (`components.css` l.23) | prohibido: velo plano |
| D20 | Color suelto | `#eaf4fa` y `#ffffff` escritos a mano (`components.css` l.23, l.26) | tokens (`--on-accent`; el texto sobre velo, blanco) |
| D21 | Títulos | 700, tracking 0, caja normal, interlineado 1,2 (`base.css` l.13-16) | 800, mayúsculas, tracking 0,01 em, interlineado 1,02; los tamaños se quedan |
| D22 | Texto | Literata 16 px / 1,45 (`base.css` l.10) | 17 px / 1,6 |
| D23 | Datos y botones | botones en Literata 500 de 15 px (`base.css` l.50); rótulos de campo en Literata 500 de 13 px (`base.css` l.76) | JetBrains Mono 500, 12 px, mayúsculas, tracking 0,06 em |
| D24 | Nombre en la cabecera | «Galivelop IG» en 700 con «IG» en el acento (`layout.css` l.9, l.11) | wordmark en 800 y mayúsculas, todo en tinta; el acento no pinta letras del nombre |
| D25 | Símbolo y favicon | baldosa `#5B34C9` con `rx="28"` (esquinas **redondas**, las cuatro), dibujada a mano (`gimg/ui/assets/gvig.svg` l.4; igual en `logos/galivelop-image-generator-b.svg`) | cuadrado plano `#7C5CD6` con **chaflán** de 28/128 solo arriba a la derecha, salido de gimg |
| D26 | Lockup | `<text>` vivo, Big Shoulders Display 700, caja normal, «IG» en `#5B34C9` (`gimg/ui/assets/gvig-lockup.svg` l.12) | trazados de `gimg brand wordmark` y `lockup`, con las medidas comunes |
| D27 | Paleta de la maqueta | `PALETTE` con `#06121c`, `#A78BFA`, `#8B5CF6` (`gimg/ui/mock/api-mock.js` l.11) | la de `brand.palette` cuando cambie |

**Lo que ya coincide** (no se toca): fondo `#fbfcfd` / `#0d171e` (l.12, l.54, l.80), tinta `#13212b` / `#e6eef3` (l.19,
l.59, l.85), las tres familias tipográficas servidas en local (l.6-8, l.36-38), tema claro por defecto con oscuro por
`prefers-color-scheme` o `data-theme` (l.2, l.52-53, l.79), `--on-accent` `#ffffff` (l.24), `--family` `#0072a8` en claro
(l.27), y que no hay transiciones salvo el indicador de espera (`base.css` l.137-140).

## Recursos: hecho y pendiente

| # | Recurso | Estado | Dónde | Fuente |
|---|---|---|---|---|
| R1 | Símbolo (baldosa) | **Hecho en r9, a mano:** no cumple r10 (D25) ni la regla de que todo gráfico nace de gimg. Pendiente rehacerlo | `logos/galivelop-image-generator-b.svg`, `gimg/ui/assets/gvig.svg` | `1b211f6`; `../portal/hoja.md` l.290, l.303-304 |
| R2 | Símbolo de línea, claro y oscuro | Hecho en r9, a mano, con la celda elegida en `#8B5CF6`. Pendiente: sale del mismo trazado que R1 | `logos/…-b-linea.svg`, `…-b-linea-oscuro.svg` | `tests/test_brand_assets.py` l.14-15 |
| R3 | Wordmark | **No hay** como archivo: el nombre es `<text>` dentro del lockup | — | D26 |
| R4 | Lockup horizontal y vertical | Hecho en r9 solo el horizontal, con `<text>`; el vertical **no hay**. Pendiente con `gimg brand lockup` | `logos/…-b-lockup.svg`, `…-b-lockup-oscuro.svg`, `gimg/ui/assets/gvig-lockup.svg` | `tests/test_brand_assets.py` l.19-21 |
| R5 | Monograma «GVIG» | Sin dibujar (**[P]** desde r9). Con r10 es un wordmark más: `gimg brand wordmark "GVIG"` | — | r9 §4 |
| R6 | Copia del lockup para `compose` | Copia congelada del lockup **anterior a r9** (degradado, Sora), la que usan `og` y `social`; vigilada por `REDRAWN_COPY_SHA256` | `examples/galivelop-image-generator/logos/galivelop-image-generator-b-lockup.svg` | `tests/test_examples.py` l.316; `docs/handoff.md` l.18 |
| R7 | `og` y `social` | Hechas en r4-r8 con la identidad anterior (vidrio, `#06121c`, FLUX). **Pendiente: medir una ronda plana** y componerlas con el lockup nuevo | `examples/galivelop-image-generator/` | `docs/handoff.md` l.18 |
| R8 | `avatar` 512 | Hecho en r5 con la baldosa anterior. Pendiente con R1 | `examples/galivelop-image-generator/piezas.json` | r9 §9 |
| R9 | `og.jpg` del producto en el Portal (su recurso 24) | Pendiente; el acento del producto como «a touch of» | Portal `tools/og/fuentes/<slug>/og-fuente.png` | `../portal/hoja.md` l.213 |
| R10 | Iconos de la interfaz | **No hay serie propia.** Si la interfaz lleva iconos, la serie es de línea simple, entera y sin mezclar | — | `../portal/hoja.md` l.292 |
| R11 | Candidatos `-a`, `-c`, `-d` y sus lockups | Historia (degradado, Sora) | `logos/` | r9 §4 |

## Herencia del Portal: las seis comprobaciones

Las de «Cómo se comprueba una hoja de producto» (`../portal/hoja.md` l.307-315), con el resultado de hoy.

| # | Comprobación | En esta hoja | En el repo, hoy |
|---|---|---|---|
| 1 | Tres hex del acento, calculados, con sus ratios; ninguno bajo 4,5:1 donde el método lo exige | cumple: `#7C5CD6`, `#7C5CD6`, `#896ae5`; 4,69, 4,82 y 4,54 | no: `#5B34C9`, `#A78BFA`, `#8B5CF6` (D1-D5) |
| 2 | Papel, tinta, filete, retícula, tipografías y chaflanes, valor por valor | cumple | en parte: papel, tinta y familias sí; superficie, texto 2, filete, retícula, pesos y radios no (D7-D12, D18, D21-D23) |
| 3 | Frase de paleta del Portal con el acento en el lugar del alga | cumple (fila «Paleta») | no: los prompts son los de la identidad anterior (`examples/galivelop-image-generator/prompts/`) |
| 4 | Logo: cuadrado plano del hondo, chaflán 28/128, trazo 12/128, salido de gimg | lo pide (sección 4) | no: `#5B34C9`, `rx` 28, hecho a mano (D25) |
| 5 | Iconos de una tinta, sin relleno, nodos huecos, legibles a 24 px | lo pide (R10) | no hay serie |
| 6 | Nada de «Prohibido en toda la familia» | cumple | no: `backdrop-filter` (D19), esquinas redondas (D18), sombra difusa (D16), SVG a mano (D25, D26) |

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Galivelop IG» (siglas «GVIG»): en interfaz, README, hoja, textos y piezas. El repo, el paquete y la orden `gimg` no cambian. En el wordmark, «GALIVELOP IG», en mayúsculas | repo (`docs/plan.md` l.50, D38, decisión de la persona del 2026-11-04) |
| Nombre en código | Obl. | `galivelop-image-generator` | repo (`examples/galivelop-image-generator/galivelop-images.json` l.4) |
| Fuente de verdad | Rec. | Este repo `8bb0ae1`; para lo heredado, `../portal/hoja.md` en ese commit | repo |
| Quién decide | Obl. | La persona. Suyas: D38, las siete de r9 (2026-11-11) y las cuatro del 2026-11-12. El detalle de r10 es del agente y va **[P]** o «calculado» | repo (`docs/handoff.md` l.20; `../portal/hoja.md` l.331-375) |
| Fecha de la hoja | Rec. | `2026-11-12` (r10); anteriores `2026-11-11` (r9) y `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`: papel, tinta, tipografías, forma, registros de dibujo y lockup son de la familia | heredado (`../portal/hoja.md` l.236-250) |
| Hereda de | Opc. | Portal Galivelop, `../portal/hoja.md` «Familia Galivelop» | repo |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos»; para los proyectos del taller (Tarkor/WMF el primero) y quien quiera generar en local sin instalar nada | repo (`README.md` l.5-7; `docs/plan.md` D1, D2, D6) |
| Idea de marca | Rec. | la hoja de contactos sobre el papel de la carta: muchos intentos en tinta, uno marcado en violeta | propio (r9, aprobada el 2026-11-11) |
| Lema | Rec. | «Pide, prueba, elige.» | **[P]** (`biblia.md` l.16) |
| Tono | Rec. | técnico, sobrio, honesto con el estado real; nunca vende, nada de «magia». Frases cortas, datos antes que adjetivos | repo (`README.md` «Estado»; `biblia.md` l.83) |
| Idiomas | Opc. | `es` manda; el repo publica también en `en` (`README.en.md`, `docs/en/`), sin pieza en inglés decidida | repo (`es`); `en` **[P]** |
| Campo semántico | Opc. | dentro: pedido, intento, candidata, descartada, elegida, cola, entrega, manifiesto, perfil, motor, referencia, hoja de contactos; fuera: render, job, cliente, prompt engineering, «magia» | repo (`GLOSSARY.md`) |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | Lo prohibido en toda la familia (personas, manos, rostros, robots, cerebros, cohetes, gráficas de crecimiento, banderas, lugares reales reconocibles, motivos náuticos protagonistas) y, propio: cámaras, pinceles, paletas, lienzos, chispas o «magia» de IA, artistas sustituidos, obras reconocibles | heredado (`../portal/hoja.md` l.297-305); propio (`biblia.md` l.21-22, l.96) |
| Promesas | Rec. | nada de «arte ilimitado»; no afirmar en una pieza lo que el README no diga ya; nada de precios ni fechas | repo (`biblia.md` l.22; `README.md` «Estado») |
| Texto en imagen | Rec. | ninguna imagen generada lleva texto; lo pone `compose` | heredado (`../portal/hoja.md` l.53, l.294) |

## 3. Paleta

Los valores están en «Acento: los dos tonos, calculados» e «Interfaz: tokens y reglas». Aquí, las reglas.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. (familia) | claro (por defecto) `#fbfcfd`; oscuro `#0d171e`; superficie `#ffffff` / `#111f29` | heredado (`../portal/hoja.md` l.240) |
| Texto | Rec. (familia) | `#13212b`, `#4a5c69`, `#5a6d7a` sobre claro; `#e6eef3`, `#9fb2bf`, `#7d919e` sobre oscuro | heredado (l.241) |
| Acento | Obl. | violeta en dos tonos: vivo y hondo `#7C5CD6`; variante oscura `#896ae5` para texto sobre `#0d171e` | propio; el vivo, Portal (`../portal/hoja.md` l.323); los otros, calculados |
| Proporción | Rec. | **Sin número.** r9 decía 70 % papel, 20 % tinta, hasta 10 % violeta; el Portal dice que la proporción «no tiene número en ninguna fuente» y que no se inventa. Queda el orden: el papel es la mayor superficie, la tinta la línea, el acento hondo en bloques y marcando **una sola cosa por pantalla** (lo elegido). Si hace falta el número, se mide con `gimg measure` sobre piezas aprobadas | heredado (`../portal/hoja.md` l.281-284); «una sola cosa», propio (r9) |
| Combinaciones | Rec. | clara: papel + tinta + un bloque o un punto `#7C5CD6`; oscura: `#0d171e` + `#e6eef3` + relleno `#7C5CD6` o texto `#896ae5`. Sobre el acento, texto blanco. Sobre imagen, texto sobre la zona de papel o sobre velo plano | propio, calculado; el velo, heredado (l.275-276) |
| En imagen generada | Obl. | cerúleo, papel, tinta y un toque de `#7C5CD6`; nunca el violeta como dominante | heredado (l.278-279, l.302) |
| Prohibidos | Rec. | lo de la familia (l.297-305) y, propio: el celeste del Portal como acento de la herramienta (solo `--family`, ≤ 2 %); texto en tinta sobre el acento (3,41:1); texto blanco sobre `#896ae5` (3,99:1); violeta neón o magenta; más de una cosa en violeta por pantalla; los violetas de r9 (`#5B34C9`, `#A78BFA`, `#8B5CF6`) en piezas nuevas | propio (r9, contradicción 5; cálculo) |
| Degradados | Opc. | ninguno | heredado (l.244) |

**Medido:** con la identidad anterior, paleta ≥ 72 % con `brand.palette` de 4 hex (`docs/records/contenido/calibracion-measure.md`).
Con la paleta de r10 no hay nada medido.

## 4. Logo

Reglas heredadas (`../portal/hoja.md` l.290-291, l.363-375): cuadrado de color plano en el **acento hondo**, chaflán de
28/128 arriba a la derecha que pone el SVG y no el modelo, dibujo de trazo 12/128 en una sola tinta, sin degradado,
sombra ni redondeo; se genera con gimg sobre croma `#00ff00` y se vectoriza con `gimg brand trace`. Lockup común.

| Pieza | Qué es | Regla | De quién | Hoy |
|---|---|---|---|---|
| Símbolo | **Decidido por la persona (2026-11-12): monograma «IG» en una tinta (`#fbfcfd`) sobre el cuadrado con chaflán en el hondo**; sustituye a la rejilla 2×2, que pasa a histórico junto a los logos anteriores (degradado, `rx` 30, Sora), no se copian a repos. **Dependencia:** orden nueva en `gimg brand` que monte el cuadrado con chaflán | cuadrado `#7C5CD6`, chaflán 28/128, «IG» de trazo 12/128 en `#fbfcfd` (4,69:1 sobre el cuadrado) | la forma del cuadrado, heredada; el dibujo, propio | `logos/galivelop-image-generator-b.svg`: `#5B34C9`, `rx` 28, a mano (R1) |
| Símbolo de una tinta | la rejilla sin cuadrado, para papel | `currentColor` (tinta `#13212b` o `#e6eef3`); la celda elegida, rellena en la misma tinta. Es `emblema-mono.svg` de `gimg brand system` | propio | `…-b-linea.svg` con la celda en `#8B5CF6` (R2) |
| Favicon | el símbolo | el mismo archivo que el símbolo; mínimo 16 px | propio | `gimg/ui/assets/gvig.svg` |
| Wordmark | «GALIVELOP IG» | Big Shoulders Display 800, mayúsculas, tracking 0,01 em, en `currentColor`, **nunca en el acento** | heredado | no hay (R3) |
| Lockup horizontal | símbolo + nombre a la derecha | alto de letras 0,45 `S`; hueco 0,25 `S`; margen 0,25 `S`; mínimo `S` ≥ 32 px | heredado | `…-b-lockup.svg`: 700, caja normal, «IG» en `#5B34C9`, hueco 28/128 = 0,22 `S` (R4) |
| Lockup vertical | símbolo + nombre debajo | ancho del nombre 1,6 `S`; hueco y margen 0,25 `S`; mínimo `S` ≥ 48 px | heredado | no hay; r9 y la biblia decían «nunca el nombre debajo» (`biblia.md` l.72) |
| Monograma | «GVIG» como wordmark suelto | un wordmark con las mismas reglas, donde no cabe el nombre; **el «IG» del símbolo es el decidido el 2026-11-12** | propio **[P]** (el wordmark); símbolo decidido | no hay (R5) |

Órdenes (las medidas son las de la decisión 4 de la persona; `--spacing` y `--margin` hay que escribirlos porque los
valores por defecto de `gimg` son 0,12 y 0, `gimg/cli.py` l.123, l.131):

```
gimg brand wordmark "GALIVELOP IG" --font gimg/ui/fonts/BigShouldersDisplay.ttf --weight 800 --spacing 0.01 -o wordmark.svg
gimg brand lockup simbolo.svg wordmark.svg --layout h --cap 0.45 --gap 0.25 --margin 0.25 -o lockup-h.svg
gimg brand lockup simbolo.svg wordmark.svg --layout v --width 1.6 --gap 0.25 --margin 0.25 -o lockup-v.svg
```

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Colores del logo | Obl. | `#7C5CD6`, `#fbfcfd`; el nombre, `#13212b` (claro) o `#e6eef3` (oscuro) | propio, calculado; heredado el del nombre |
| Variantes | Rec. | con cuadrado (vale sobre claro y oscuro: lleva su fondo) y de una tinta (por `currentColor`) | propio |
| Tamaño mínimo | Obl. | símbolo 16 px; lockup horizontal `S` ≥ 32 px, vertical `S` ≥ 48 px; por debajo, el símbolo solo | heredado (l.366-370); r9 decía lockup de 24 px de alto |
| Margen | Obl. | 0,25 `S` por cada lado | heredado; coincide con el «un cuarto del lado» de r9 |
| Usos prohibidos | Obl. | deformar, girar, cambiar el violeta por el azul del Portal, **encender más de una celda**, sombra o brillo, degradado, redondear el cuadrado, pintar letras del nombre en el acento, ponerlo sobre una zona con detalle sin velo | propio (r9) y heredado |
| Copia para `compose` | Rec. | `examples/galivelop-image-generator/logos/galivelop-image-generator-b-lockup.svg`: copia congelada del lockup anterior a r9; se cambia por `lockup-h.svg` al medir la ronda plana, y entonces se quita `REDRAWN_COPY_SHA256` | repo (`tests/test_examples.py` l.316; `docs/handoff.md` l.18) |

**Por qué una sola celda** (r9, se conserva). El símbolo dice lo que hace la herramienta: muchos intentos, uno elegido.
Dos celdas encendidas ya no dicen eso. **Propio frente a la regla de iconos:** la familia pide iconos sin relleno y con
los interiores huecos; la celda rellena es la única excepción y solo en el símbolo, porque es su significado.

**Lo que `gimg` no hace todavía** (va a la entrega): no hay orden que ponga el dibujo trazado sobre el cuadrado con
chaflán (`gimg brand` tiene `matte`, `trace`, `wordmark`, `lockup` y `system`, `gimg/cli.py` l.104-144), y
`gimg brand system` no tiene `--margin`. Hasta que exista, el símbolo con cuadrado no puede nacer entero de gimg.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titulares | Rec. | **Big Shoulders Display** 800 (h1-h3) y 700 (h4), mayúsculas, tracking 0,01 em, interlineado 1,02 | heredado (`../portal/hoja.md` l.243); **hoy** 700, caja normal, tracking 0 (D21) |
| Texto | Rec. | **Literata** 400/600, 17 px / 1,6 | heredado; **hoy** 16 px / 1,45 (D22) |
| Datos | Rec. | **JetBrains Mono** 500, 12 px / 1,4, mayúsculas, tracking 0,06 em: etiquetas, botones, semillas, hex, rutas, medidas | heredado; **hoy** botones y rótulos en Literata (D23) |
| Tamaños de título | Rec. | h1 30 px, h2 23 px, h3 18 px | propio (`gimg/ui/css/base.css` l.14-16) |
| Piezas, hoy | — | Sora 700 e Inter 400/500: solo en la composición de `og` (`galivelop-images.json` l.41-44) | repo |
| Licencia y origen | Rec. | las tres son OFL; TTF variables en `gimg/ui/fonts/` | repo (`gimg/ui/fonts/OFL.txt`) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivo propio | Obl. | la ventana de aplicación con una fila de miniaturas y una elegida (fila «Motivo propio» de arriba) | propio; sin pieza |
| Iconografía | Rec. | línea simple: un solo grosor, remates y uniones redondos, sin relleno, trama ni sombra, una tinta, legibles a 24 px, nodos e interiores huecos; vectorizados con `gimg brand trace --mode color --matte --dp-tol 0.5 --palette '#13212b,#fbfcfd'`; en la interfaz a `currentColor`, pintados a 22 px; la serie se usa entera | heredado (`../portal/hoja.md` l.292) |
| Ilustración | Rec. | grabado de carta náutica a dos tintas, bloque literal del Portal; el sujeto es el motivo propio y el cuarto color de la frase, el violeta | heredado (l.293) |
| Composición | Rec. | zona limpia en positivo y al principio; a sangre; sin texto; sin «exactly N»; lo que se recorta, sobre croma | heredado (l.294) |
| Motivos: no | Obl. | cámaras, pinceles, paletas, lienzos, caballetes, chispas y varitas, robots, cerebros, caras y personas, galerías con cuadros reconocibles; marcos de cristal con brillo (eran de r6-r8) | propio (`biblia.md` l.96-99) |
| Estilo medido (identidad anterior) | — | r6-r8: marcos de vidrio, PBR, luz volumétrica sobre fondo oscuro (r7: 9/10 de la persona). Sigue en `og` y `social` hasta la ronda plana; no se mezcla con el plano en una pieza | repo (`examples/galivelop-image-generator/prompts/`); r9, contradicción 3 |
| Lenguaje de formas | Rec. | trazo 12/128; marcos interiores de esquina viva; chaflán 28/128 en el cuadrado | heredado y propio |

> **Las secciones 7 a 15 no cambian desde r9:** describen las piezas hechas con la identidad anterior (escena oscura,
> vidrio, Sora e Inter), que siguen siendo las de `og` y `social` hasta que una ronda plana fije sus propios valores.
> Donde citen los violetas de r9 o Sora, es lo que hay en esas piezas, no lo que pide r10.

## 7. Luz y atmósfera

> **r9:** estos valores son de la identidad anterior (escena oscura, vidrio) y siguen valiendo para `og` y `social`. El estilo plano **[P]** no tiene luz: fondo de papel, sin sombras; sus objetivos de YAVG y SATAVG salen de su primera ronda.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | la luz sale de los propios marcos (no hay fuente externa); en `r2-luz.txt`: «the only light comes from the right» y el marco encendido «a quarter of the way in from the right edge» | repo (`prompts/estilo.txt`); la variante *(suposición: r2-luz sin veredicto)* |
| Momento y clima | Rec. | escena oscura, dicha al principio: «Dark wide abstract banner: the whole frame is deep midnight navy…» (r2-luz); en `estilo.txt` el fondo oscuro va en la primera frase | repo (`orders/r2-luz.json`) *(suposición)* |
| Luminosidad objetivo (YAVG) | Rec. | 33-52 (r1 y r5: 33-50; r4 og: 47,9; r2 palabras: 41,7) | repo (`calibracion-measure.md`, umbrales orientativos) |
| Saturación objetivo (SATAVG) | Rec. | 10-16 (r4 og: 15,17; r2 palabras: 15,3) | repo (`calibracion-measure.md`) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **publicada dónde:** en este repo, nada (sin web ni og:image); la calibración midió una `portada.webp` de este proyecto en el Portal (YAVG 41, SATAVG 13, paleta 77 %; EMD de r1 y r5: Y 8-11, Cb 1,2-3,3, Cr 2,5-4,2), pero el plan dice que las herramientas «no están en el Portal». **Vale como referencia:** **[P]** | *(suposición: existe `Portal-Galivelop/public/proyectos/<?>/portada.webp`; la persona dice si vale como marca, «Portadas que no son marca» de `calibracion-measure.md`)* |

## 9. Formatos y piezas

> **r9:** los perfiles no cambian. Las piezas hechas son de la identidad anterior; con r9 aprobada, la primera pieza plana es una cabecera de documentación, no el `og`.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 → 1200×630 (`targetWidth`/`targetHeight` añadidos el 2026-11-04) y `social` 1280×640. Hechos en el piloto y sin perfil: `square` 1024×1024 → 1080×1080, `portrait` 896×1152 → 1080×1350, `header` 1536×512 → 1500×500 | repo (`galivelop-images.json`); los tres de r5 **[P]** (bitácora: «lo decide la persona» en F2.8) |
| Zona reservada | Obl. | `og`, `social`, `header`: `izquierda 1/2` («The left half … calm, smooth, dark navy surface, nearly empty and softly out of focus»); `square`, `portrait`: `arriba 1/2`. En píxeles, por la conversión de la plantilla (sección 9): `og` entregado 1200×630 → `0,0,600,630`; caja `data-caja` de la plantilla `60,60,604,510` (margen 60, columna 604; logo a 52-54 px de alto, titular en una línea a 52 px, filete corto en el acento y subtítulo en dos líneas; r7). La caja del piloto es 55 % del ancho menos margen (izquierda) o 48 % del alto (arriba), margen 6 %: no coincide con 1/2 y se alinea al portar a `compose` | repo (`prompts/*.txt`; `examples/pilot/componer.py` `caja_zona`). La biblia dice «tercio superior **[P]**» para `square`: r5 hizo la mitad |
| Velo por perfil | Rec. | `og` `#06121c:0`; `square`, `portrait` y `header` `#06121c:0.3` | repo (`piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza, margen 6 % (desde r4, que lo tuvo a ~24 px y no se leía) *(suposición: la esquina; confirmar en `componer.py`)* | repo (`r4-composicion.md`; `examples/pilot/componer.py`) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 % del alto, título y subtítulo). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-image-generator-b.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay | repo (`piezas.json`); `icon` **[P]** |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia en r1-r5 sin boceto), sin LUT (las piezas salen dentro de rango; `compose.lut`, F2.11, no se necesita), sin conversión final | repo (`r1-fondos.md`, `r5-piezas.md`) |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos (51 s) y anticipa estilo y hueco. Propuesto `draft: {scale: 0.5, steps: 4}` en `og` | **[P]** (F2.10, dec. 7) |
| Prioridad | Rec. | 1) logo elegido y `avatar` 512; 2) `social` 1280×640; 3) `og` 1200×630. Hechas en el piloto, además, `square`, `portrait` y `header` (r5) | repo (`biblia.md` §9) |

## 10. Textos de composición

> **r9:** el nombre que se compone es «Galivelop IG» (D38). En las piezas, titular en Big Shoulders Display y subtítulo en Literata **[P]**; hoy, Sora e Inter (la interfaz ya usa las nuevas).

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | «Pide, prueba, elige.» (20 caracteres), en `og` | **[P]** (`piezas.json`, r4; el lema es propuesta) |
| Subtítulo | Rec. | «Imágenes con IA local: un servicio por máquina, para varios proyectos.» (70) | **[P]** (`piezas.json`, r4) |
| Variaciones, ganchos y cierres | Rec. | usados en r5: `square` «¿Diez intentos y una elegida?» / «Así trabaja. Tú eliges; él recuerda cómo se hizo.»; `portrait` «Se enciende cuando se le pide.» / «Nada residente y sin instalar nada: Python 3, solo stdlib.»; `header` «Cada elegida, con su manifiesto.» / «IA local: nada sale de tu equipo.». Sin usar: «Un servicio por máquina, para todos tus proyectos.» · «Sin instalar nada.» | **[P]** (`piezas.json`; `biblia.md` §6) |
| Longitud máxima por campo | Rec. | la fija la composición: `componer.py` baja el cuerpo hasta 16 px y falla si el texto no cabe en la zona («acorta el título o el subtítulo, o usa otra zona»). Orientativo: titular ≤ 40, subtítulo ≤ 70 (el de r4 está justo en el límite) | repo (`examples/pilot/componer.py`) |
| Wordmark compuesto como texto | Opc. | el nombre va en el lockup (Sora 700, `#8B5CF6`), nunca como `text` del pedido | repo (lockup) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` | repo (`galivelop-images.json` `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto, escrito explícito) | repo (`delivery.template`) |
| Dónde se publica cada pieza | Rec. | `social`: social preview del repo en GitHub; `avatar`: GitHub y Discord. `og`: no hay web que lo consuma; `banner` del Portal solo si la persona decide presentar las herramientas allí | **[P]** (`biblia.md` §9; `docs/plan.md` «Formatos» de las herramientas) |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto, no declarado) | repo (esquema) |
| Conversión final | Opc. | no hay | — |

## 12. Aceptación

> **r9:** los umbrales son los medidos con la identidad anterior. No se aplican a una pieza plana hasta que una ronda fije los suyos.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona; delegado al agente desde el 2026-10-26. Apuntado en `docs/records/contenido/r1-fondos.md` (sí, s3 y s4, «de las mejores»), `r2-estilo.md` (elegida «palabras»), `r4-composicion.md`, `r5-piezas.md` | repo |
| Contraste del texto | Rec. | ≥ 4,5:1 (por defecto); medido: og r4 17,08 (peor 16,49) sin velo; r5 cuadrado 16,48 (15,42), vertical 16,44 (16,28), cabecera 15,49 (15,33) con velo 0,3 | repo (`r4-composicion.md`, `r5-piezas.md`) |
| Umbrales de medida | Rec. | los de las secciones 3 y 7: paleta ≥ 72 %, YAVG 33-52, SATAVG 10-16 | repo (`calibracion-measure.md`) |
| EMD frente a la marca | Opc. | Cb ≤ 4 / Cr ≤ 5 (medido frente a la portada del Portal: Cb 1,2-3,3, Cr 2,5-4,2) | repo (`calibracion-measure.md`) *(suposición: la referencia, sección 8)* |
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» en r1 a la primera y estilo elegido en r2; r5 dio las tres piezas de formato a la primera. Pendiente solo el veredicto de la persona sobre lo delegado | repo (registros r1-r5) |

## 13. Fuentes de verdad

**Este repo**, `f2-motor` `2259370`:

- `README.md` l.5-7, «Estado» (propósito, honestidad con el estado); `README.en.md` (idioma `en`).
- `GLOSSARY.md`, «Términos del proyecto» (campo semántico).
- `examples/galivelop-image-generator/galivelop-images.json` (`name`, `brand.palette` de 5 hex, `delivery`, perfiles `og` y
  `social`; último cambio `b65bd81`, más el de 2026-11-04).
- `examples/galivelop-image-generator/piezas.json` (fuentes Sora/Inter, textos, zona, color de texto y velo de las cinco
  piezas, ruta del lockup y del avatar).
- `examples/galivelop-image-generator/prompts/estilo.txt`, `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt`,
  `r2-luz.txt` y `orders/*.json` (motivos, estilo, zona reservada por formato, luz).
- `docs/marcas/galivelop-image-generator/logos/galivelop-image-generator-b.svg` y `-b-lockup.svg` (último cambio `10d71ec`).
- `docs/marcas/README.md` («Elegido por el agente»: quién decide, logo b, acento `#8B5CF6`; conceptos de logo l.172-177).
- `docs/marcas/galivelop-image-generator/biblia.md` (vetos, palabras vetadas, reglas del logo, frases; lo que es **[P]** allí
  lo sigue siendo aquí).
- `docs/plan.md` «Estilos por proyecto» (herramientas del taller: familia del Portal, acento, *No*, formatos, metáforas),
  F2.8 dec. 2 y F2.10 dec. 6-7 (`avatar`/`icon`, `draft`), fila F2.12.
- `docs/records/contenido/calibracion-measure.md` (umbrales y medidas), `r1-fondos.md`, `r2-estilo.md`,
  `r4-composicion.md`, `r5-piezas.md` (veredictos y medidas).
- `examples/pilot/componer.py` (`caja_zona`, ajuste del texto), `examples/pilot/fuentes.sh` (origen y licencia de las fuentes).

**Portal-Galivelop** `aa76b34` (marca paraguas, «heredado de»), leído solo a través de `docs/marcas/portal/biblia.md` y
`docs/records/lectura-2026-10-26-tarkor-y-marcas.md`: `src/estilos/global.css` (fondos, texto, superficies, borde),
`src/componentes/Logo.tsx` (Sora 700, −0,03 em), `public/marca/gv-logo.svg` (baldosa `rx` 30, trazo 12).

Sin línea aquí y por tanto **[P]** o *(suposición)*: acento y sus dos tonos, lema y frases, logo elegido, reglas del logo
tras elegir, monoespaciada, perfiles `square`/`portrait`/`header`, `draft`, `compose`, la portada del Portal como marca.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo): los perfiles `square`, `portrait` y
`header` de r5 (hechos en el piloto, sin declarar); `#5B34C9` (final del degradado de la baldosa) fuera de `brand.palette`;
`compose` (plantilla SVG, fuentes, zona, velo y logo en la pieza viven en `examples/pilot/componer.py`). Arreglados el
2026-11-04: `#eaf4fa` ya está en `brand.palette`; `og` lleva `targetWidth` 1200 y `targetHeight` 630; el cierre de `r2-luz`
ya no lleva «no letters, no logos».

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio) |
| 3 | «Nunca se muestra» no vacío | pasa; nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | hex pasa (4); el texto `#eaf4fa` ya está en `brand.palette` (corregido el 2026-11-04); el acento oscuro `#5B34C9` del logo sigue fuera (la hoja nombra los roles, la configuración no los lleva) |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, sin `<text>`/`<image>`/`filter`, legible a 16 px según la elección); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: la configuración no tiene `compose.fonts`, y las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts` |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» pasa: `estilo.txt`, `r5-*.txt` y `r2-luz.txt` (su cierre «no letters, no logos» se cambió a «The image is completely textless.» el 2026-11-04, según el cambio 5 de la plantilla) |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (124-130 palabras), `r2-luz.txt` incluido |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | pasa: múltiplos de 64 y `og` con `targetWidth` 1200 y `targetHeight` 630 (corregido el 2026-11-04) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | el prompt la describe; ningún perfil la declara (hueco) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (20 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | no pasa del todo: Fondo claro `#f6fafd`, texto sobre claro `#0a1a28`, acento sobre claro `#5B34C9` y los de las superficies no están; los de la pieza oscura sí (`#06121c`, `#eaf4fa`, `#8B5CF6`). Se decide con la persona si la clara entra |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | pasa para `og` (1200×630); `square`, `portrait` y `header` no están declarados (hueco) |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 15** (familia
Galivelop; 18 con la familia propia).

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan: roles de la paleta (`brand.palette` no los distingue), zona reservada (solo en
prompt y en `componer.py`), velo y logo en la pieza (solo en `componer.py`), palabras vetadas sin campo, `avatar` sin perfil (lo hace `piezas.py`), tipografía sin licencia
ni ruta declaradas (las baja `fuentes.sh`), imágenes de marca para la EMD sin lista (la calibración usó una del Portal), copia
de los logos en `examples/<p>/logos/` pendiente. No le afectan: varias variantes de logo (la baldosa vale sobre claro y
oscuro), `compose.lut` (no hace falta), `style.lora`, idiomas (solo `es`).


**Fuentes de r10** (2026-11-12), además de las de arriba: `docs/marcas/portal/hoja.md` l.40-117 (identidad vigente),
l.121-178 (tokens y reglas), l.228-375 (familia y decisiones de la persona); `gimg/ui/css/tokens.css` l.1-102,
`base.css`, `layout.css`, `components.css`; `gimg/ui/assets/gvig.svg`, `gvig-lockup.svg`; `gimg/cli.py` l.104-144
(`gimg brand`); `tests/test_ui.py` l.563-594 y `tests/test_brand_assets.py` l.14-21, l.58-60, l.95 (lo que hoy fijan las
pruebas); `docs/handoff.md` l.18, l.20; [`acento_oklch.py`](acento_oklch.py) (cálculo).

---

## Contradicciones

### r10 (2026-11-12): con decisiones de r9. Pendientes de la persona

r9 la aprobó la persona el 2026-11-11; las decisiones del 2026-11-12 son posteriores y generales para la familia. Donde
chocan, esta hoja sigue la más reciente y lo dice aquí; la recomendación va con cada una.

1. **Los tres violetas de r9** (`#5B34C9` claro, `#A78BFA` oscuro, `#8B5CF6` marca) frente a «su hex de hoy es el vivo»
   y los otros dos se calculan (`#7C5CD6`, `#896ae5`). Lo que se pierde: contraste (texto de acento 7,36 → 4,69 en claro
   y 6,66 → 4,54 en oscuro; blanco sobre el botón 7,56 → 4,82). **Recomendación:** seguir la decisión del 2026-11-12; es
   la que hace familia y el contraste sigue en AA.
2. **Texto de acento dentro de fichas.** El método solo exige el papel: sobre superficie oscura `#111f29` da 4,20 y sobre
   el tinte 4,03 / 3,82. **Recomendación:** un tono de texto calculado contra el peor fondo de cada tema (`#7453cc` en
   claro, `#9577f3` en oscuro, tabla «Dónde no llega»), dejando `#7C5CD6` para rellenos, foco y logo. Es añadir un paso
   al método, así que lo decide la persona y valdría para toda la familia.
3. **«IG» en violeta dentro del nombre** (r9 §4) frente a «el nombre va en `currentColor`, nunca en el acento».
   **Recomendación:** nombre de una tinta, como el resto de la familia; el violeta queda en el cuadrado.
4. **Lockup vertical.** r9 y la biblia: «nunca el nombre debajo»; el lockup común tiene versión vertical.
   **Recomendación:** admitirla (avatar con nombre, pieza cuadrada); la horizontal sigue siendo la principal.
5. **Proporción 70 / 20 / 10** de r9 frente a «no se inventa un reparto». **Recomendación:** quitar el número y medirlo
   en la ronda plana.
6. **Colores de estado.** r9 tenía verde, ámbar y rojo propios; la familia hereda «hecho» y peligro del Portal y no tiene
   aviso. **Recomendación:** heredar los dos y conservar el ámbar propio (`#8a5a00` / `#f2c14e`) como única excepción.
7. **Superficie.** r9 puso `#e6eef3` (que en el Portal es la tinta del tema oscuro) como superficie clara y `#13212b`
   como oscura; el Portal usa `#ffffff` y `#111f29`. **Recomendación:** las del Portal; además, el acento sobre `#e6eef3`
   daría 4,10.
8. **Cuadrado redondeado.** r9 pedía «chaflán 28/128» y el SVG aplicado lleva `rx="28"`, que redondea las cuatro
   esquinas; la prueba fija ese `rx` (`tests/test_brand_assets.py` l.58). **Recomendación:** chaflán de verdad, solo
   arriba a la derecha, al rehacer el símbolo con gimg.

### r9 (2026-11-11): resueltas por la persona

1. **La interfaz usaba la identidad anterior.** Decisión: aplicar r9 a `tokens.css` con tema claro por defecto.
   **Aplicado** (`de53727`).
2. **Claro u oscuro por defecto.** Decisión: **claro**; las piezas `og`/`social` siguen oscuras hasta una ronda plana.
   Sigue vigente.
3. **Vidrio o plano.** Decisión: **dos estilos, medir antes**; el plano se mide en una ronda antes de tocar `og.txt`.
   Sigue vigente: es la ronda pendiente.
4. **Logo con degradado y `rx` 30/128.** Decisión: redibujar símbolo, lockup y favicon. **Aplicado** (`1b211f6`); r10 lo
   vuelve a abrir (contradicción 8 de r10).
5. **El azul del Portal.** Decisión: solo como `--family` (≤ 2 %) en el enlace «parte de Galivelop». Sigue vigente.
6. **D38 sin aplicar.** Decisión: «Galivelop IG» en README, textos e interfaz. **Aplicado** (`1ca2bb6`).
7. **`brand.palette`** con los hex de la identidad anterior. Decisión: no se toca hasta la ronda plana. Sigue vigente;
   entonces serán los siete de la fila «`brand.palette` propuesto», no los seis de r9.

## Cambios que pediría a la plantilla

Los cinco de r9 siguen pendientes (idea de marca, tabla «se comparte / es propio», roles con dos temas, sistema de logo
como tabla, fila «Hoy»). r10 añade:

6. **Una tabla «diferencias con el código»** para las marcas que tienen interfaz: sin ella, la hoja y el CSS se separan
   sin que nadie lo vea.
7. **Los fondos sobre los que se comprueba el texto de acento:** el método de la familia mide solo el papel y una
   aplicación escribe sobre fichas.

## Lo que enseñó rellenarla

**r10:** copiar las relaciones del Portal con otro hex saca a la luz lo que el hex no puede hacer. `#7C5CD6` es a la vez
vivo y hondo, así que en tema claro la marca tiene un tono, no dos; y el texto sobre el acento pasa de la tinta al blanco.
La herencia se comprueba mejor contra el código que contra la hoja anterior: 27 diferencias, de las que r9 solo conocía
el monograma y el `<text>` del lockup.

**r9:** una variante se define mejor por lo que **no** cambia (papel, tinta, línea, letras) que por su acento; y una hoja
propuesta tiene que decir en cada fila qué hay hoy, o quien la lea aplicará lo que aún nadie aprobó.

## Historia

- **r10 (2026-11-12):** estructura y relaciones de la hoja del Portal; acento `#7C5CD6` con sus tonos calculados;
  lockup común. Propuesta, sin aplicar.
- **r9 (2026-11-11):** variante de la identidad nueva del Portal; aprobada y aplicada (PR #6). Hoja entera:
  `git show 8bb0ae1:docs/marcas/galivelop-image-generator/hoja.md`.
- **2026-11-04 a 2026-11-05 (hasta r8):** identidad oscura con violeta, familia del Portal anterior (`aa76b34`), Sora e
  Inter, vidrio en las piezas. Hoja entera: `git show a4e394d:docs/marcas/galivelop-image-generator/hoja.md`.
