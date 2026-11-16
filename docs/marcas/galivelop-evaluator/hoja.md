# Hoja de estilo mínima: galivelop-evaluator (GVE)

> **Producto de la familia Galivelop.** GVE sigue la hoja del Portal ([`../portal/hoja.md`](../portal/hoja.md),
> «Identidad vigente», «Familia Galivelop: lo que heredan los productos» y «Decisiones de la persona (2026-11-12)») y
> solo pone **su acento y su motivo**. Donde esta hoja y la del Portal digan cosas distintas en algo heredado, **manda la
> del Portal** y esta se corrige. Todo gráfico nace de `gimg` (FLUX para bocetos y composición, Z-Image para calidad);
> nada se dibuja a mano.

**Hoja cerrada el 2026-11-16** (escrita el 2026-11-15). El acento `#b4c424` lo **aprobó la persona** el 2026-11-15; el
hondo pasa a `#6b7509` por el traslado 1 de GVE; la regla de mareas, el monograma «GE» y el icono (nivel de burbuja)
son **elegidos por el agente (delegado, 2026-11-16)** y la persona puede revertirlos (ver «Decisiones»). Las piezas y
los prompts siguen como **[P]** hasta el «sí» de cada ronda. Estados como en
[`../README.md`](../README.md): **heredado** remite a la hoja del Portal y no repite sus valores salvo donde hacen falta
para comprobar; **propio** solo vale para GVE; **calculado** sale de [`tonos.py`](tonos.py); *(suposición)* se comprueba
en la primera ronda.

Commits de referencia: galivelop-evaluator `origin/ccr-4fe19114-typsl9` `2e2dc15` (2026-11-15), leído con `git show`,
**sin modificar nada**; Portal, el que cita su hoja (`7fc0357`); este repo `5089629` (`hojas-repos`).

**Lo primero que hay que saber:** GVE **no tiene nada de marca**: ningún `.svg`, `.png`, `.ico` ni `.webp` en la rama, ni
`README.md` en la raíz, ni logo. Sí tiene **front** (`front/v2/`: maquetas HTML, CSS y gráficos generados por
`front/v2/generador/`) con los neutros y las tipografías del Portal y **el celeste del Portal como acento provisional**
(`front/v2/estilos/tokens.css` l.21-27: `--accent: #1aa6df`). Esta hoja le da el suyo.

---

## Identidad vigente (2026-11-15): lo que gimg necesita

| Campo | Valor | Estado |
|---|---|---|
| Paleta | **Heredado:** cerúleo `#0072a8` («medium cerulean ocean blue #0072a8»), papel `#fbfcfd`, tinta `#13212b`; versión oscura, fondo `#0d171e` y líneas `#e6eef3`; los grabados admiten «tints and shades» del cerúleo; los iconos, una sola tinta. **Propio: el acento «verde nivel» ocupa el lugar del alga `#5d7a6a`**, solo como «a touch of», nunca bloque grande ni protagonista. Frase final de todo prompt de GVE: **«Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424.»** (sin «and its tints and shades» en línea simple; en las piezas con banderín, «… on the pennant only»). `brand.palette` propuesto: `#0072a8`, `#1aa6df`, `#fbfcfd`, `#13212b`, `#e6eef3`, `#0d171e`, `#b4c424`, `#6b7509` | Portal, fila «Paleta» y «Qué cambia», fila «Acento secundario» (`../portal/hoja.md` l.52, l.296) y decisión 3; el nombre «chartreuse yellow-green» es *(suposición)*: la primera ronda mide con `gimg measure` si da ese hex («sky blue» desvió el cerúleo en el Portal) |
| Acento: tres tonos | **Vivo `#b4c424`**, **hondo `#6b7509`** (tema claro), **variante oscura `#b4c424`** (es el vivo: ya da 9,38:1 sobre `#0d171e`, regla 5 del método). Detalle y ratios en «Acento: los tres tonos, calculados» | vivo elegido por el agente (delegado) y **aprobado por la persona el 2026-11-15**; hondo y oscura, **calculados** (hondo corregido el 2026-11-16, traslado 1 de GVE) |
| Tipografía | **Heredado sin cambio:** Big Shoulders Display (titulares), Literata (texto), JetBrains Mono (datos). **Ninguna imagen lleva texto**, ni generado ni compuesto: lo pone la web o el front con sus fuentes | Portal, fila «Tipografía» (l.53) y decisión 3; GVE ya las usa (`tokens.css` l.54-57) |
| Modelo y parámetros | **Heredado:** calidad con `zimage-turbo-q6`, 8 pasos, cfg 1.0, euler, `draft {scale 0.5, steps 4}`; FLUX (`flux2-klein-4b-q8`, 6 pasos) para bocetos y para fijar una composición; Qwen-Image no hace falta. Con cfg 1.0 no hay prompt negativo. **Si una pieza con la regla graduada sale con cifras** (lo esperable: una escala invita a números), el camino es el de la 31d: boceto FLUX limpio y Z-Image en img2img sobre él (`initImage`, `strength` 0,5) | Portal, fila «Modelo y parámetros» (l.54); `examples/portal/orders/marca/31d-portada-workflow-img2img.json` |
| Mar y tecnología | **Heredado:** el mar pone el dónde (carta, isobatas, papel, cerúleo) y la tecnología el qué; ningún motivo náutico protagonista sin decisión de la persona. **Propio, el qué de GVE: la medida que deja rastro.** Tres formas del mismo motivo: 1) **en el mar grabado** (portada, `og`, cabecera): una **regla de mareas**, un listón graduado que sale del agua con marcas sin cifras y un banderín pequeño del acento, como la boya con banderín de voz (15v) y de workflow (31d); 2) **en grabado sobre papel** (tarjeta, estado vacío): **las sondas**, el perfil del fondo medido con varias líneas de sonda que bajan desde la superficie (las sondas de una carta son medidas: cada punto de profundidad tiene detrás una línea echada); 3) **en línea simple** (icono de proyecto): **el nivel de burbuja**, una cápsula horizontal con dos marcas y la burbuja hueca entre ellas (decisión 6); **el dial de medida** (media corona con marcas y aguja de eje hueco) queda para el estado vacío, en grabado, y como reserva del icono | Portal, fila «Mar y tecnología» (l.55); motivo, **[P]** del agente. La regla de mareas es un objeto de mar como protagonista de tres piezas: sigue el patrón aprobado de los hermanos (15v, 31d, 24); **aceptada: elegido por el agente (delegado, 2026-11-16)**, decisión 2 |
| Dos registros de dibujo | **Heredado, con los bloques literales del Portal:** grabado a dos tintas para lo grande; línea simple para iconos y símbolo. No se mezclan en una pieza | Portal, fila «Dos registros de dibujo» (l.56) |
| Zonas limpias, recuentos, encuadre | **Heredado sin cambio:** zona limpia en positivo y como papel o agua en calma; trama confinada; nunca «exactly N» (marcas y sondas, «a few», «several», «a regular ladder of»); todo a sangre con el cierre del Portal | Portal, filas «Zonas limpias», «Recuentos», «Encuadre» (l.57, l.58, l.61) |
| Fondo y recorte | **Heredado:** lo que se recorta va sobre croma plano y pasa por `gimg brand matte` y `trace`. **Propio: el croma de GVE es siempre magenta `#ff00ff`**, nunca `#00ff00`: el acento es un amarillo verdoso y su borde suavizado se funde con el verde (es la regla del Portal para las piezas con verde). Las hojas de iconos para revisar, sobre papel `#fbfcfd` | Portal, fila «Fondo y recorte» (l.59) |
| Versión oscura | **Heredado:** iconos y símbolo por CSS (`currentColor`), sin generar; un grabado, segunda generación con la **misma semilla** cambiando la frase de paleta por «printed in two inks on dark slate paper #0d171e: pale off-white #e6eef3 lines and medium cerulean ocean blue #0072a8 tints and shades, and a touch of chartreuse yellow-green #b4c424». Solo se generan las que el front o el Portal enseñen a sangre en oscuro (hoy, ninguna pedida) | Portal, fila «Versión oscura» (l.60) |
| Perfiles | **Heredado:** los de `examples/portal/galivelop-images.json`, todos Z-Image: `icono` 1024² → 512², `cuadrado` 768² → 1024², `social` 1344×704 → 1200×630, `portada` 1344×768 → 1600×900, `tarjeta` 1344×768 → 1200×675, `cabecera` 1664×512 → 1600×500, `fondo` 1024² → 1200², `patron` 1792×448 → 1200×300 (`tileable: "xy"`), `formulario` 1024×768 → 800×600. Los pedidos de GVE se encolan en el proyecto `portal` con clave `marca/…`, como los de los hermanos (`23b`, `24`, `15v`, `31`, `32`); GVE no tiene aún proyecto propio en `examples/` | Portal, fila «Perfiles» (l.62); `examples/portal/galivelop-images.json` (`5089629`) |
| Referencias aprobadas | Del registro: las del Portal (q310, q311) y las piezas hermanas con objeto y banderín sobre el mar (15v de voz; 24 de Tarkor q932; mar de plantilla 32h q984). **Propias: ninguna** (no hay ronda) | `docs/handoff.md` de este repo, «Hecho», 2026-11-14 |

**Cómo se escribe el prompt:** heredado entero de «Cómo se escribe el prompt» del Portal (`../portal/hoja.md` l.67-92):
orden sujeto → zona limpia → bloque del registro → cierre → frase de paleta; negaciones solo en el cierre; ningún color
fuera de las tintas, ni como adjetivo; `seed` fijo y `count` 2-4. **Propio de GVE**, además de lo vetado en la familia:

- **No se nombran** (ética y motivo, sección 2): `chart`*(como gráfica)*, `graph`, `bar chart`, `growth`, `arrow up`,
  `trophy`, `medal`, `podium`, `star rating`, `stars`, `score`, `percent`, `thumbs up`, `exam`, `teacher`, `judge`,
  `gavel`, `scales of justice`, `robot`, `brain`, `magnifying glass`, `microscope`, `lab coat`, `test tube`. «nautical
  chart» y «sea chart» son del bloque de estilo y se quedan.
- **Nada que parezca un resultado:** ni cifras, ni porcentajes, ni marcas de «aprobado»: GVE no promete un número en
  una imagen (un dato ausente nunca cuenta como éxito, `docs/discovery/vision-v0.2.md` l.8-9). La regla lleva marcas
  **sin cifras**; el cierre añade siempre «no numbers, no digits».
- **El acento no es adjetivo del sujeto** fuera del banderín o de la única marca que lo lleva; se sitúa con la forma
  («a little pennant», «one of the weights») y lo repite la frase de paleta con «only».
- **El icono se dibuja en el tono hondo**, no en el vivo: el vivo da 1,88:1 sobre el papel y no se lee.

**Decisiones** (las «dudas que decide la persona» del 2026-11-15; **todas cerradas el 2026-11-16**). Las tres marcadas
«elegido por el agente (delegado, 2026-11-16)» las puede revertir la persona; al lado va qué habría que cambiar.

1. **El acento. Cerrada: aprobado por la persona (2026-11-15).** `#b4c424`, «verde nivel»: el amarillo verdoso del
   líquido de un nivel de burbuja. Es el tono que queda más lejos de todos los hermanos a la vez (ver la tabla de
   tonos). Alternativa descartada: ámbar «latón» (tono ~80°), que cae sobre el aviso `--warn` del propio front y a 33°
   de Tarkor.
2. **La regla de mareas como protagonista** de portada, `og` y cabecera. **Cerrada: se acepta; elegido por el agente
   (delegado, 2026-11-16).** Porqué: es el mismo patrón ya aprobado en los hermanos (objeto pequeño con banderín del
   acento sobre el mar grabado: boya de campana de voz 15v, boyas con cuerda de workflow 31d, 24 de Tarkor), así que la
   familia se lee como una serie, y «medir» se entiende sin una sola cifra. Para revertirla: R5, R6 y R9 pasan al
   motivo de las sondas (el de R8), que no añade objeto de mar.
3. **El acento y el estado «sube» del front. Cerrada: aplicada por GVE con la recomendación (2026-11-15).** `--up` es
   `#2f6a4a` (tono 157,5°, croma 0,081) y el hondo de GVE `#6b7509` (115,6°, 0,119): 42° de diferencia, pero los dos
   son verdes y de claridad parecida. Se mantiene la regla que el front ya tiene (`tokens.css` l.29: el color solo dice
   «sube / baja», siempre con signo) y el acento no se usa para nada que signifique resultado; se comprueba en la
   primera pantalla y, si se confunden, se vuelve a la persona.
4. **Series y escala de puestos del front. Cerrada: aplicada por GVE con la recomendación (2026-11-15).** `--s-work` y
   `--r1`…`--r4` siguen en cerúleo (`tokens.css` l.40, l.49-52): es tinta de la familia y dato, no acento; el acento
   queda para foco, enlaces, bloques y marca.
5. **Monograma. Cerrada: «GE»; elegido por el agente (delegado, 2026-11-16).** Porqué: los monogramas de la familia
   son todos de dos letras (decisión 6 del Portal: GV, GD, GW, IG) y el trazo de la familia (12/128) deja tres letras
   sin aire en el cuadrado con chaflán: a 16-32 px, que es donde el símbolo va solo, dos letras se leen y tres se
   empastan. «GVE» sigue siendo la sigla **en texto** (`GLOSSARY.md` l.33) y «GALIVELOP EVALUATOR» el nombre del
   lockup. Para revertirla: cambiar `"GE"` por `"GVE"` en la primera orden de R3; nada más depende de ello.
6. **Icono de proyecto. Cerrada: el nivel de burbuja (R2, `23b-icono-gve-b`); elegido por el agente (delegado,
   2026-11-16).** Porqué: son tres formas grandes y simétricas (cápsula, dos marcas, burbuja hueca) que aguantan los 16
   px del favicon y que el modelo dibuja sin contar; el dial depende de una fila de marcas finas que a 16-24 px se
   funde y que invita al modelo a poner cifras, y además se lee como velocímetro o «puntuación», justo el resultado que
   GVE no promete. Es también el objeto que da nombre al acento («verde nivel»). El dial (R1, `23b-icono-gve-a`) queda
   **de reserva**, con su pedido, y sigue en el estado vacío (R12). Para revertirla, o si el nivel no sale en 2-3
   intentos o se confunde con un interruptor: se aprueba R1 en su lugar.
7. **Relleno de acento en tema oscuro. Cerrada: aplicada por GVE con la recomendación (2026-11-15).** El front
   mantiene el vivo con tinta oscura encima (9,38:1) en vez del hondo con blanco de la familia (ver «Interfaz»).

---

## Acento: los tres tonos, calculados

Método de la decisión 1 de la persona (`../portal/hoja.md` l.368-396). Orden que lo reproduce:

```
python3 docs/marcas/galivelop-evaluator/tonos.py '#B4C424'
```

```text
vivo   #b4c424  OKLCH L=0.7819 C=0.1692 h=115.68
       sobre #fbfcfd 1.88 | blanco encima 1.93 | tinta #13212b encima 8.49 | sobre #0d171e 9.38
hondo  #6b7509  L=0.5369 C=0.1192 (49 pasos)
       sobre #fbfcfd 4.90 | blanco encima 5.03 | sobre #0d171e 3.60
       sobre banda #f1f6f9 4.62 | sobre tinte #f2f5e3 4.54 | tinta #13212b encima 3.26
oscuro #b4c424  L=0.7819 C=0.1692 (0 pasos)
       sobre #0d171e 9.38
tinte  12 % sobre #fbfcfd = #f2f5e3, tinta encima 14.80 | 18 % sobre #0d171e = #2b361f, tinta #e6eef3 encima 10.84
```

`tonos.py` es el de voice con una exigencia más para el hondo (**traslado 1 de GVE, 2026-11-16**): además del papel
`#fbfcfd`, tiene que dar ≥ 4,5:1 sobre la banda alterna `#f1f6f9` (`--surface-2` del front) y sobre el tinte claro
`#f2f5e3`, porque el front de GVE pone texto de acento sobre los dos (`.b-info`) y su `tests/test_front_contraste.py`
lo exige. Con solo el papel salía `#6f7a05` (46 pasos; 4,58 sobre papel, pero 4,32 y 4,25 sobre esos dos fondos); con
los tres sale `#6b7509` (49 pasos). Para el vivo, con `'#1aa6df'` da los ratios del Portal (2,70 / 2,78 / 5,91 / 6,53),
que es la prueba de que calcula lo mismo. En el hondo la croma baja de 0,1692 a 0,1192: a esa claridad el tono 115° no
cabe en sRGB con la croma del vivo, y el método la reduce sin tocar el tono (paso 4).

| Tono | Hex | Cómo sale | Ratios |
|---|---|---|---|
| **Vivo** | `#b4c424` | elegido por el agente (delegado); aprobado por la persona (2026-11-15) | sobre papel 1,88; tinta `#13212b` encima 8,49; sobre `#0d171e` 9,38 |
| **Hondo** (tema claro) | `#6b7509` | L baja 49 pasos de 0,005 (hasta cumplir sobre papel, banda alterna y tinte); C baja a 0,1192 para entrar en sRGB | sobre papel 4,90; blanco encima 5,03; papel `#fbfcfd` encima 4,90; sobre la banda `#f1f6f9` 4,62; sobre el tinte `#f2f5e3` 4,54 |
| **Variante oscura** | `#b4c424` | **es el vivo** (0 pasos) | sobre `#0d171e` 9,38; sobre `#111f29` 8,68; sobre `#16242e` 8,19 |
| Tinte claro | `#f2f5e3` | vivo al 12 % sobre `#fbfcfd` | tinta encima 14,80; hondo encima 4,54 |
| Tinte oscuro | `#2b361f` | vivo al 18 % sobre `#0d171e` | tinta `#e6eef3` encima 10,84; vivo encima 6,58 |

**Por qué este tono** (OKLCH, calculado con el mismo script):

| Marca | Hex | Tono h | A cuántos grados queda GVE (115,7°) |
|---|---|---|---|
| galivelop-voice-generator | `#D9467A` | 2,8° | 113° |
| Tarkor | `#E0703A` | 44,4° | 71° |
| toVeriAI (ámbar / verde) | `#B5832A` / `#2D6A4F` | 77,6° / 162,2° | 38° / 47° |
| galivelop-developer | `#0E9A93` | 189,0° | 73° |
| Portal (celeste) | `#1aa6df` | 233,0° | 117° |
| galivelop-workflow | `#3D6FD9` | 263,1° | 147° |
| galivelop-image-generator | `#7C5CD6` | 291,8° | 176° |
| Estados del front de GVE: `--warn` / `--up` | `#8a5a00` / `#2f6a4a` | 73,3° / 157,5° | 42° / 42° |

El mayor hueco de la rueda entre los productos y proyectos del Portal va de Tarkor (44°) a developer (189°); GVE se
pone en su centro (116°), que además equidista del aviso y del «sube» de su propio front.

**Qué relación del Portal se cumple y cuál no** (tabla «Qué cambia», `../portal/hoja.md` l.290-297):

| Relación del Portal | Aquí | Resultado |
|---|---|---|
| Vivo: el mismo hex en claro y oscuro; no es texto sobre papel claro | `#b4c424`; 1,88 sobre papel | cumple. **Más claro que el del Portal (2,70):** sobre papel no llega a 3:1 ni como elemento no textual, así que **en tema claro el foco y los puntos de estado usan el hondo** (como hace ya el front: `--focus` es el tono hondo, `tokens.css` l.27) y el vivo queda para el tinte y el tema oscuro |
| Sobre el vivo solo va la tinta, a ≥ 4,5:1 (Portal 5,91) | 8,49 | cumple (voice y GVIG no llegan) |
| Vivo sobre el papel oscuro ≥ 4,5:1 (Portal 6,53) | 9,38 | cumple |
| Hondo: ≥ 4,5:1 sobre papel y blanco encima ≥ 4,5:1 | 4,90 y 5,03 | cumple |
| Variante oscura a ≥ 4,5:1 sobre `#0d171e` | 9,38 (es el vivo) | cumple, y también sobre las superficies oscuras (8,68 y 8,19) |
| Tinte al 12 % / 18 %, tinta encima ≥ 7:1 | 14,80 / 10,84 | cumple |
| Un acento con dos tonos (hondo en superficie grande, vivo en puntos) | mismo tono (115,7° y 115,6°), croma 0,169 y 0,119 | cumple |
| Bloques con texto blanco: el hondo, también en oscuro | blanco sobre `#6b7509` 5,03 | cumple |

**Dónde llega el texto de acento** (corregido el 2026-11-16, traslado 1 de GVE): el hondo `#6b7509` da ≥ 4,5:1 sobre
todos los fondos claros del front: papel 4,90, `#ffffff` 5,03, banda alterna `#f1f6f9` 4,62 y su propio tinte `#f2f5e3`
4,54. La regla anterior de esta hoja (texto de acento solo sobre papel o blanco, porque `#6f7a05` daba 4,32 y 4,25)
**queda retirada**. En tema oscuro el texto de acento es el vivo (9,38 / 8,68 / 8,19 / 6,58 sobre el tinte oscuro); el
hondo no es texto sobre fondo oscuro (3,60).

## Interfaz: tokens y reglas

GVE ya tiene front. **Heredado sin cambiar un valor** (tabla de tokens del Portal y «Qué se copia tal cual»,
`../portal/hoja.md` l.269-281): papel y superficie, tinta y sus escalones, filete y retícula de 24 px, peligro, «hecho»,
velos, chaflanes (28 / 14 / 10 px), `border-radius` 0, tipografía por papel y tema claro por defecto.

**Propio: el acento.** Con los nombres que el front ya usa (`front/v2/estilos/tokens.css` l.21-27, `2e2dc15`):

| Token de GVE | Antes (provisional, `2e2dc15`) | Vigente (aplicado por GVE, 2026-11-15) | Papel que hace (el del Portal) |
|---|---|---|---|
| `--accent` | `#1aa6df` | `#b4c424` | el de `--celeste`: marca, tinte, puntos en oscuro |
| `--accent-text` | `light-dark(#0072a8, #5cc8f2)` | `light-dark(#6b7509, #b4c424)` | enlaces y texto de acento (4,90 / 9,38) |
| `--accent-fill` | `light-dark(#0072a8, #5cc8f2)` | `light-dark(#6b7509, #b4c424)` | bloques y botones |
| `--on-accent` | `light-dark(#ffffff, #0d171e)` | igual | texto sobre el relleno (5,03 / 9,38) |
| `--accent-soft` | `light-dark(#e4f3fa, #10303f)` | `light-dark(#f2f5e3, #2b361f)` | tinte al 12 % / 18 % (tinta encima 14,80 / 10,84) |
| `--focus` | `light-dark(#0072a8, #5cc8f2)` | `light-dark(#6b7509, #b4c424)` | `outline` de foco (4,90 / 9,38) |

**Diferencias del front con el Portal** (se apuntan; no se corrigen desde aquí): relleno claro con tinta encima en tema
oscuro, donde la familia pide el hondo con blanco en los dos temas (con `#b4c424` y `#0d171e` encima da 9,38: se
mantiene lo del front, decisión 7); `--text-2` oscuro `#a9bbc7` (Portal
`#9fb2bf`), sin `--texto-3`; `--border` `#6f8493` propio; `--font-ui` de sistema para la interfaz, que el Portal no
tiene; un solo chaflán de 14 px. Sus contrastes están en `docs/design/F1-v2.md` de GVE.

## Recursos: piezas y prompts

Ninguna hecha. Todas **[P]**, sin encolar. Se encolan desde `examples/portal` (`gimg order submit`), cada una en su
`orders/marca/<id>.json` con `key` `marca/<id>`. «Semillas» es el `count` recomendado.

| # | Id | Recurso | Perfil (genera → entrega) | Modelo | Semilla / `count` | Registro |
|---|---|---|---|---|---|---|
| R1 | `23b-icono-gve-a` | Icono de proyecto, dial: **reserva** (decisión 6) | `icono` 1024² → 512² | Z-Image | 2361 / 3 | línea simple, croma `#ff00ff` |
| R2 | `23b-icono-gve-b` | **Icono de proyecto elegido**, nivel de burbuja (recurso 23 del Portal; también favicon; decisión 6) | `icono` 1024² → 512² | Z-Image | 2371 / 3 | línea simple, croma `#ff00ff` |
| R3 | — | Símbolo: monograma «GE» en el cuadrado con chaflán (decisión 5) | sin generar | `gimg brand` | — | órdenes abajo |
| R4 | — | Lockup horizontal y vertical | sin generar | `gimg brand` | — | órdenes abajo |
| R5 | `33-portada-gve` | Portada del producto en el Portal | `portada` 1344×768 → 1600×900 | Z-Image (boceto FLUX si salen cifras) | 3341 / 3 | grabado, mar |
| R6 | `24-og-gve` | `og.jpg` del producto (recurso 24) | `social` 1344×704 → 1200×630 | Z-Image | 2441 / 3 | grabado, mar |
| R7 | — | Tarjeta social del repo en GitHub (1280×640) | sin generar: `gimg export` de R6 | — | — | — |
| R8 | `15-proximamente-gve` | Tarjeta «Próximamente» del Portal (recurso 15) | `tarjeta` 1344×768 → 1200×675 | Z-Image | 1541 / 3 | grabado, papel |
| R9 | `16-cabecera-gve` | Cabecera (README, X) | `cabecera` 1664×512 → 1600×500 | Z-Image | 1641 / 3 | grabado, mar |
| R10 | `11-fondo-gve` | Fondo tenue de sección | `fondo` 1024² → 1200² | Z-Image | 1141 / 2 | grabado, papel |
| R11 | `21-patron-gve` | Patrón sin costura de sondas | `patron` 1792×448 → 1200×300 | Z-Image | 2141 / 2 | plano, papel |
| R12 | `27-estado-vacio-gve` | Estado vacío del front («sin corridas») | `formulario` 1024×768 → 800×600 | Z-Image | 2741 / 2 | grabado, papel |
| R13 | `25a`…`25j-icono-gve-*` | Diez iconos de panel del front | `cuadrado` 768² → 1024² | Z-Image | 2501-2510 / 2 cada uno | línea simple, papel |
| R14 | — | `avatar` 512 e `icon` 180/192/512 | sin generar: `gimg export` del símbolo | — | — | — |

### Bloques comunes (literales; cada prompt los lleva enteros)

- **[MAR]** (grabado, el de 15v, 24 y 31d): «Richly detailed engraved nautical chart style, like a fine antique sea
  chart printed in two inks: the sea built from many layers of fine wave lines and hatching, line density increasing
  towards the deep water to give depth, tonal bands from deep cerulean at the bottom to lighter cerulean at the top,
  bathymetric contour lines with small depth soundings drawn as tiny dots, subtle foam strokes and a few glints of light
  on the crests. Every wave is drawn as visible engraved line work, like a steel engraving, never painted, never smooth.
  Crisp sharp lines of several weights, intricate but calm, premium print quality, high detail, elegant.»
- **[PAPEL]** (grabado sobre papel, el del Portal): «Richly detailed engraved antique nautical chart style, like a fine
  sea chart printed in two inks: many layers of fine lines and hatching, line density increasing in the darker areas to
  give depth and tone, lines of several weights, crisp and sharp, intricate but calm, premium print quality, high
  detail, elegant.»
- **[LÍNEA]** (línea simple del Portal, con lo que enseñaron las 23b): «Simple line register: one single uniform
  stroke weight everywhere, thick and bold, the very same line thickness in every part of the icon, rounded line caps
  and rounded joins, outlines only, no fill anywhere, no solid shape, the background colour shows through every shape.»

### R1 · `marca/23b-icono-gve-a` (dial; reserva)

```
A minimal flat line icon, centred, seen straight on: a measuring dial gauge made entirely of outlines. First, a large half ring: one wide semicircular arc, like the upper half of a circle, open at the bottom, its two ends finishing level with each other. Second, along the inside of the arc, a few short straight tick marks pointing towards the centre, evenly spread, all the same length, none of them touching the arc. Third, one straight needle that starts at the middle of the base and points up and to the right, towards the upper right part of the arc, stopping short of the tick marks. Fourth, at the foot of the needle, one small hollow ring, the hub, its inside empty, the background showing through it. Simple line register: one single uniform stroke weight everywhere, thick and bold, the very same line thickness in every part of the icon, rounded line caps and rounded joins, outlines only, no fill anywhere, no solid shape, the background colour shows through every shape. The whole icon is drawn in one single colour, dark olive green #6b7509, and nothing else. The background is a perfectly flat, plain, uniform pure chroma key magenta #ff00ff filling the whole square, with no gradient, no texture, no vignette and no shadow. Generous empty margin all around, the icon takes about two thirds of the square, balanced, geometric, clean vector look, few large simple shapes with wide gaps between the lines, legible at very small size. No shading, no hatching, no drop shadow, no glow, no highlights, no 3D, no perspective, no photographic rendering, no second colour in the icon, no thin lines, no extra details, no ornaments, no text, no letters, no numbers, no digits, no watermark.
```

### R2 · `marca/23b-icono-gve-b` (nivel de burbuja; el elegido)

```
A minimal flat line icon, centred, seen straight on: the vial of a spirit level made entirely of outlines. First, one wide horizontal capsule outline, a long pill shape with fully rounded ends, about three times as wide as it is tall, perfectly level. Second, inside the capsule, two short straight vertical lines standing side by side near the middle, a little apart, each running from near the top edge to near the bottom edge without touching them. Third, exactly between those two lines, one hollow circle, the bubble, its inside empty, the background showing through it, not touching the lines. The whole figure is symmetrical left to right. Simple line register: one single uniform stroke weight everywhere, thick and bold, the very same line thickness in every part of the icon, rounded line caps and rounded joins, outlines only, no fill anywhere, no solid shape, the background colour shows through every shape. The whole icon is drawn in one single colour, dark olive green #6b7509, and nothing else. The background is a perfectly flat, plain, uniform pure chroma key magenta #ff00ff filling the whole square, with no gradient, no texture, no vignette and no shadow. Generous empty margin all around, the icon takes about two thirds of the width of the square, balanced, geometric, clean vector look, few large simple shapes with wide gaps between the lines, legible at very small size. No liquid, no shading, no hatching, no drop shadow, no glow, no highlights, no reflections, no 3D, no perspective, no photographic rendering, no second colour in the icon, no thin lines, no extra details, no ornaments, no text, no letters, no numbers, no digits, no watermark.
```

Elegido R2 (decisión 6; R1 solo si R2 no sale): `gimg brand matte` sobre el magenta (con `--holes` para la burbuja, o
para el eje si se usa R1) y
`gimg brand trace --mode color --matte --dp-tol 0.5 --palette '#6b7509'`, en el mismo paso que la aprobación; en la web
va a `currentColor` (hondo en claro, vivo en oscuro).

### R3 y R4 · símbolo y lockup (sin generar)

```
gimg brand wordmark "GE" --font <Big Shoulders Display variable .ttf> --weight 800 --spacing 0.01
gimg brand square GE.svg --fill '#6b7509' --ink '#fbfcfd'
gimg brand wordmark "GALIVELOP EVALUATOR" --font <Big Shoulders Display variable .ttf> --weight 800 --spacing 0.01
gimg brand lockup simbolo.svg wordmark.svg --layout h --cap 0.45 --gap 0.25 --margin 0.25
gimg brand lockup simbolo.svg wordmark.svg --layout v --width 1.6 --gap 0.25 --margin 0.25
```

Cuadrado plano del hondo, chaflán de 28/128 arriba a la derecha (lo pone `square`), monograma «GE» en papel (4,90:1). El
nombre va en `currentColor` (tinta), nunca en el acento. Mínimos: `S` ≥ 32 px en horizontal, ≥ 48 px en vertical; por
debajo, el símbolo solo hasta 16 px. Depende de tener el `.ttf` de Big Shoulders Display en el equipo.

### R5 · `marca/33-portada-gve` (portada, 1600×900)

```
A single slender tide gauge staff standing upright in the open sea, seen from slightly above: a tall, narrow, flat wooden board fixed to a thin post that rises straight out of the water. The face of the board is marked from top to bottom with a regular ladder of short plain horizontal tick marks, alternating longer and shorter strokes, the bare scale of a ruler and nothing else on it. The waterline crosses the staff about one third of the way up, with a small ring of ripples drawn as lines around its foot. On top of the staff, a little plain chartreuse yellow-green #b4c424 pennant flag on a thin mast. The staff is small, about one quarter of the image height, and stands in the right half of the image with water all around it. It is drawn in crisp off-white and ink grey line art with fine engraved shading. The left half and the whole bottom of the image are calm open water with only gentle wave lines. Richly detailed engraved nautical chart style, like a fine antique sea chart printed in two inks: the sea built from many layers of fine wave lines and hatching, line density increasing towards the deep water to give depth, tonal bands from deep cerulean at the bottom to lighter cerulean at the top, bathymetric contour lines with small depth soundings drawn as tiny dots, subtle foam strokes and a few glints of light on the crests. Every wave is drawn as visible engraved line work, like a steel engraving, never painted, never smooth. Crisp sharp lines of several weights, intricate but calm, premium print quality, high detail, elegant. No realistic objects, no photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no figures on the staff, no watermark, no horizon, no sky, full-bleed edge to edge, no border, no frame. Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424 on the pennant only.
```

Si las tres semillas traen cifras en la regla: el mismo prompt como boceto FLUX, se elige el que tenga la regla limpia
y se repite con Z-Image añadiendo `"initImage": "referencias/33-portada-gve-q<n>.png", "strength": 0.5`. Si el agua
sale fotográfica, se monta sobre el mar de plantilla (32h, q984), como la portada 32.

### R6 · `marca/24-og-gve` (`og`, 1200×630; de ella sale R7)

```
A single slender tide gauge staff standing upright in the open sea, seen from slightly above: a tall, narrow, flat wooden board fixed to a thin post that rises straight out of the water, its face marked from top to bottom with a regular ladder of short plain horizontal tick marks, alternating longer and shorter strokes, the bare scale of a ruler and nothing else on it. On top of the staff, a little plain chartreuse yellow-green #b4c424 pennant flag on a thin mast. The staff is drawn in crisp off-white and ink grey line art with fine engraved shading. From the foot of the staff, concentric ripples spread out across the water surface, drawn as fine engraved off-white lines in the water itself: wide flattened ellipses seen in perspective, much wider than tall, the nearer arcs larger and bolder, the farther arcs thinner and fading into the wave lines, dying out well before the left third of the image. Richly detailed engraved nautical chart style, like a fine antique sea chart printed in two inks: the sea built from many layers of fine wave lines and hatching, line density increasing towards the deep water to give depth, tonal bands from deep cerulean at the bottom to lighter cerulean at the top, bathymetric contour lines with small depth soundings drawn as tiny dots, subtle foam strokes and a few glints of light on the crests. Every wave is drawn as visible engraved line work, like a steel engraving, never painted, never smooth. Crisp sharp lines of several weights, intricate but calm, premium print quality, high detail, elegant. No realistic objects, no photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no figures on the staff, no watermark, no horizon, no sky. The engraved sea fills the whole wide image edge to edge. The staff is medium-small and stands in the right half of the image with water all around it; the entire left third of the image is completely calm open water with nothing in it, only quiet engraved wave lines. Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424 on the pennant only.
```

R7: `gimg export` de la entregada de R6 a 1280×640 con `--crop` (ancla a la derecha, donde está la regla).

### R8 · `marca/15-proximamente-gve` (tarjeta, 1200×675)

```
A sounding survey drawn as a cross-section on an antique chart, flat and seen straight on. The lower third of the sheet is plain flat off-white paper, open and unmarked. Across the upper part, the sea surface drawn as one fine horizontal wave line running from side to side. Below it, the seabed drawn as a single smooth rolling depth profile line, rising and falling gently, also from side to side. Between the two, several thin straight vertical sounding lines drop from the surface down to the seabed, unevenly spaced, each of a different length as the bottom rises and falls, and each ending in a small hollow round weight resting on the bottom. One of the weights, near the middle, is filled with chartreuse yellow-green #b4c424; all the others are empty outlines. The water between surface and seabed is shaded with hatching and fine wave lines only in the upper two thirds of the sheet, denser towards the bottom of the sea. Richly detailed engraved antique nautical chart style, like a fine sea chart printed in two inks: many layers of fine lines and hatching, line density increasing in the darker areas to give depth and tone, lines of several weights, crisp and sharp, intricate but calm, premium print quality, high detail, elegant. No photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no labels, no watermark, full-bleed edge to edge, no border, no frame, no white margin, no blank band. Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424 on one weight only.
```

### R9 · `marca/16-cabecera-gve` (cabecera, 1600×500)

```
A very wide view of the open sea seen from slightly above, almost all of it calm water. In the right quarter only, a single slender tide gauge staff stands upright in the sea: a tall, narrow, flat wooden board fixed to a thin post rising straight out of the water, its face marked from top to bottom with a regular ladder of short plain horizontal tick marks, alternating longer and shorter strokes, the bare scale of a ruler and nothing else on it, and on top a little plain chartreuse yellow-green #b4c424 pennant flag on a thin mast. The staff is small, about half the image height, drawn in crisp off-white and ink grey line art with fine engraved shading, with a small ring of ripples drawn as lines around its foot. The left three quarters of the image are calm open water with nothing in it, only long quiet engraved wave lines. Richly detailed engraved nautical chart style, like a fine antique sea chart printed in two inks: the sea built from many layers of fine wave lines and hatching, line density increasing towards the deep water to give depth, tonal bands from deep cerulean at the bottom to lighter cerulean at the top, bathymetric contour lines with small depth soundings drawn as tiny dots, subtle foam strokes and a few glints of light on the crests. Every wave is drawn as visible engraved line work, like a steel engraving, never painted, never smooth. Crisp sharp lines of several weights, intricate but calm, premium print quality, high detail, elegant. No realistic objects, no photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no figures on the staff, no watermark, no horizon, no sky, full-bleed edge to edge, no border, no frame. Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424 on the pennant only.
```

### R10 · `marca/11-fondo-gve` (fondo, 1200×1200)

```
Faint chart detail of open water, very pale and quiet, made to sit behind text: a few wide bathymetric contour lines curving gently across the sheet and, scattered between them, many small depth soundings drawn as tiny dots, evenly spread, with a few short straight survey lines joining some of the dots in a loose row. Everything is drawn very light, in pale ink grey and pale cerulean on off-white paper, low and uniform contrast over the whole sheet, no dark areas anywhere, no coastline, no land. Richly detailed engraved antique nautical chart style, like a fine sea chart printed in two inks: many layers of fine lines and hatching, line density increasing in the darker areas to give depth and tone, lines of several weights, crisp and sharp, intricate but calm, premium print quality, high detail, elegant. Flat graphic seen straight on. No photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no labels, no compass rose, no watermark, full-bleed edge to edge, no border, no frame. Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd and ink grey #13212b.
```

Sin acento a propósito: un fondo bajo texto no lleva el toque.

### R11 · `marca/21-patron-gve` (patrón sin costura, 1200×300)

```
Seamless repeating pattern of survey marks on a flat solid off-white #fbfcfd paper ground: thin ink grey bathymetric contour lines of one fine even weight flowing gently from side to side, and between them small depth soundings drawn as tiny round dots and tiny plus-shaped tick marks, evenly spread over the whole surface, low and uniform contrast so captions placed on top stay readable, calm and regular, the same density everywhere. Flat two-ink print, crisp and sharp, seen straight on. No waves, no crests, no foam, no hatching, no shading, no compass rose, no photographic rendering, no gradients, no glow, no text, no letters, no numbers, no digits, no watermark, no border, no frame. Palette strictly limited to off-white #fbfcfd, ink grey #13212b and medium cerulean ocean blue #0072a8.
```

Para un pie sobre color se usa el patrón 21 del Portal (isobatas blancas sobre cerúleo): el acento del producto no es
color dominante de una pieza generada.

### R12 · `marca/27-estado-vacio-gve` (estado vacío, 800×600)

```
An empty state illustration, flat and seen straight on: in the centre, a single measuring dial instrument drawn as crisp ink grey line art with fine engraved shading: a round case with a plain rim, and inside it a blank dial face of plain off-white paper with a ring of short plain tick marks around its edge and one thin straight needle resting at the far left end of the scale, at rest. The small round hub at the foot of the needle is filled with chartreuse yellow-green #b4c424. The dial face carries nothing else. The instrument takes about one third of the width, with wide empty paper margins around it; the background is light off-white #fbfcfd paper with only very faint, pale cerulean bathymetric contour lines of a sea chart, barely visible, kept pale and quiet. Richly detailed engraved antique nautical chart style, like a fine sea chart printed in two inks: many layers of fine lines and hatching, line density increasing in the darker areas to give depth and tone, lines of several weights, crisp and sharp, intricate but calm, premium print quality, high detail, elegant. No horizon, no sky, no landscape, no photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no labels, no brand marks, no watermark, no border, no frame. Palette strictly limited to medium cerulean ocean blue #0072a8 and its tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424 on the hub only.
```

### R13 · `marca/25<letra>-icono-gve-<panel>` (diez iconos de panel)

Una serie entera, sin mezclar con lucide; un pedido por icono, con este molde y el sujeto de la tabla en lugar de
`<SUJETO>`. Sobre papel (no se recortan por croma: se trazan con
`gimg brand trace --mode color --matte --dp-tol 0.5 --palette '#13212b,#fbfcfd'`).

```
A minimal flat line icon, centred, seen straight on: <SUJETO> Simple line icon style: one uniform stroke width, rounded caps and joins, no shading, no hatching, no fill, no texture, bold and clear enough to read at 24 pixels, generous empty margin around the icon, a single ink colour. Every small circle is a hollow ring, its inside empty, the paper showing through it. The icon takes about two thirds of the square, balanced, geometric, clean vector look, few large simple shapes with wide gaps between the lines. The background is perfectly flat, plain, uniform off-white #fbfcfd paper with no gradient, no texture and no shadow. No photographic rendering, no glow, no 3D, no perspective, no second colour, no thin lines, no extra details, no ornaments, no text, no letters, no numbers, no digits, no watermark, no border, no frame. Palette strictly limited to ink grey #13212b on off-white #fbfcfd.
```

| Id | Panel del front | `seed` | `<SUJETO>` |
|---|---|---|---|
| `25a-icono-gve-resumen` | Resumen | 2501 | `an application window outline with a narrow title bar, holding one large hollow ring on the left and two short horizontal lines stacked on the right.` |
| `25b-icono-gve-corridas` | Corridas | 2502 | `a list: a few short horizontal lines stacked one above another, evenly spaced, each one starting with a small hollow ring at its left end.` |
| `25c-icono-gve-corrida` | Corrida | 2503 | `a stopwatch: one large hollow circle with a short stem and a small flat cap on top, and inside the circle a single straight hand pointing up and to the right from the centre.` |
| `25d-icono-gve-comparar` | Comparar | 2504 | `a balance: a short vertical post on a flat base line, a straight horizontal beam resting across its top, and one hollow ring hanging from each end of the beam on a short straight line, both at the same height.` |
| `25e-icono-gve-curva` | Curva | 2505 | `two axis lines forming an L, and inside them one smooth curve that climbs from the lower left and then levels off towards the right, with a few small hollow rings set along it.` |
| `25f-icono-gve-mejoras` | Mejoras | 2506 | `a wrench drawn as one outline, set diagonally from lower left to upper right, with an open jaw at the upper end and a hollow ring at the lower end.` |
| `25g-icono-gve-informes` | Informes | 2507 | `a sheet of paper standing upright, its upper right corner folded down as a small triangle, with a few short horizontal lines of different lengths inside.` |
| `25h-icono-gve-agentes` | Agentes | 2508 | `an application window outline with a narrow title bar, and inside it a command prompt: one chevron pointing right followed by a short horizontal underscore line.` |
| `25i-icono-gve-traslados` | Traslados | 2509 | `two straight horizontal arrows one above the other, the upper one pointing right and the lower one pointing left, each with a simple open arrowhead.` |
| `25j-icono-gve-eventos` | Eventos | 2510 | `a history line: one straight vertical line with a few hollow rings set along it, and a short horizontal line leaving each ring to the right.` |

La curva (25e) es el icono literal del panel «Curva», no una gráfica de crecimiento: sube y **se aplana**; en una pieza
de marca no se usa.

## Familia Galivelop: lo que hereda y cómo se comprueba

Las seis comprobaciones de «Cómo se comprueba una hoja de producto» (`../portal/hoja.md` l.340-348):

| # | Comprobación | Resultado |
|---|---|---|
| 1 | Tres hex del acento, calculados, con ratios; ninguno bajo 4,5 donde el método lo exige | **Pasa.** Vivo `#b4c424`, hondo `#6b7509` (4,90 sobre `#fbfcfd`; blanco encima 5,03; 4,62 sobre `#f1f6f9`; 4,54 sobre el tinte), oscura `#b4c424` (9,38 sobre `#0d171e`) |
| 2 | Papel, tinta, filete, retícula, tipografías y chaflanes coinciden con el Portal valor por valor | **Pasa por remisión** en la hoja. En el front, casi: ver «Diferencias del front con el Portal» |
| 3 | Frase de paleta del Portal con el acento en el lugar del alga; ningún prompt nombra otro color | **Pasa.** El único color fuera de la frase es «dark olive green #6b7509» en R1 y R2, que es el hondo del propio acento, y el magenta del croma, que es fondo y no tinta |
| 4 | Logo: cuadrado plano del hondo, chaflán 28/128, trazo 12/128, salido de gimg | **Lo pide** (R3); no existe aún |
| 5 | Iconos de una tinta, sin relleno, nodos huecos, legibles a 24 px | **Lo pide** (R1, R2, R13); sin generar |
| 6 | Nada de «Prohibido en toda la familia» | **Pasa**, con dos avisos: la regla de mareas (aceptada, decisión 2) y el icono de la curva (R13, 25e) |

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Galivelop Evaluator»; siglas «GVE»; en el lockup, «GALIVELOP EVALUATOR» | `GLOSSARY.md` l.33 (`2e2dc15`); lo del lockup, decisión 4 del Portal |
| Nombre en código | Obl. | `galivelop-evaluator` | `GLOSSARY.md` l.33 |
| Fuente de verdad | Rec. | `galivelop-evaluator`, rama `origin/ccr-4fe19114-typsl9`, `2e2dc15`; sin nada publicado en `main` que citar | sección 13 |
| Quién decide | Obl. | La persona; delegó en el agente el acento (2026-11-15, que luego aprobó) y las decisiones 2, 5 y 6 (2026-11-16), que puede revertir | encargo de esta hoja |
| Fecha de la hoja | Rec. | 2026-11-15; cerrada el 2026-11-16 | — |
| Familia visual | Rec. | `Galivelop`: hereda papel, tinta, tipografías, lockup común y estilo de imagen | regla de la persona; `../portal/hoja.md`, «Familia Galivelop» |
| Hereda de | Opc. | Portal Galivelop, por su hoja (`../portal/hoja.md`, Portal `7fc0357`) | heredado |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | Mide sistemas de IA (texto, imagen y voz; modelos locales y por API) con evidencia trazable, compara corridas y propone correcciones verificadas; primero para los proyectos propios | `docs/discovery/vision-v0.2.md` l.8-13 |
| Lema | Rec. | «Medir, corregir y demostrar» | `vision-v0.2.md` l.16 (lo dice como posición, no como lema: **[P]**) |
| Tono | Rec. | Sobrio, exacto, comprobable, honesto con lo que falta; no triunfal, no «benchmark ganador» | *(suposición)*, de `vision-v0.2.md` y `docs/design/F-front.md` (regla 1: el front no calcula) |
| Idiomas | Opc. | `es`, `en` (las piezas no llevan texto; el front, lo que diga su repo) | `vision-v0.2.md` l.12 |
| Campo semántico | Opc. | Dentro: corrida, caso, lote, registro de evidencia, mejora demostrada, base, causa, traslado, sonda, medida. Fuera: magia, ranking, ganador, nota, examen, inteligencia | `GLOSSARY.md` l.31-48; lo de fuera, **[P]** |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | Lo vetado en toda la familia (personas, manos, rostros, robots, cerebros, cohetes, gráficas de crecimiento, banderas, lugares reales) y, propio: cifras, porcentajes, podios, medallas, estrellas de valoración, marcas de «aprobado», jueces, balanzas de justicia, batas y probetas | `../portal/hoja.md` l.330-338; lo propio, **[P]** |
| Personas y rostros | Rec. | Nunca | heredado |
| Promesas | Rec. | Ninguna pieza afirma un resultado, una mejora ni una fecha; nada de «el mejor modelo»; sin licencia que citar (no consta en la rama) | `vision-v0.2.md` l.8-9 («un dato ausente nunca cuenta como éxito») |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. | Papel `#fbfcfd` (claro, por defecto); `#0d171e` (oscuro) | heredado; coincide con `tokens.css` l.13 |
| Texto | Rec. | Tinta `#13212b` sobre claro; `#e6eef3` sobre oscuro | heredado; `tokens.css` l.18 |
| Acento | Obl. | «Verde nivel»: vivo `#b4c424`, hondo `#6b7509`, oscura `#b4c424` | vivo aprobado por la persona (2026-11-15); hondo y oscura calculados con `tonos.py` |
| Acentos en imagen | Rec. | 1) cerúleo `#0072a8` y sus tonos (el mar); 2) tinta; 3) un toque del acento, solo en el banderín o en una marca | heredado; relación 7 del Portal |
| Resto de la paleta | Rec. | La del Portal entera (superficies, filete, retícula, peligro, «hecho», velos). Del front, propios de dato: `--up` `#2f6a4a`/`#8fd0a8`, `--down` `#a3135f`/`#f27ab0`, `--warn` `#8a5a00`/`#f2c14e`, serie de reserva `#a8480f`/`#f0a35e` | heredado; `tokens.css` l.30-41 |
| Combinaciones | Rec. | Las del Portal: papel + tinta + bloque del hondo con blanco; texto sobre imagen, sobre velo plano de tinta al 62-78 % | heredado |
| Prohibidos | Rec. | Lo de la familia; además, el acento como color de resultado y el vivo como texto o trazo sobre papel claro (1,88:1) | propio |
| Degradados | Opc. | Ninguno | heredado |

`gimg measure`: sin umbral propio hasta que haya una pieza aprobada; se mide con `brand.palette` de arriba y se compara
con los rangos de los hermanos sobre mar (Portal).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | **No hay.** Lo hace `gimg brand` (R3: monograma «GE» sobre el cuadrado con chaflán en `#6b7509`); el icono de proyecto, R2 (nivel) | pendiente de generar; decisiones 5 y 6 |
| Lockup | Rec. | **No hay.** Común a la familia, de `gimg brand lockup` (R4) | pendiente |
| Variante clara y oscura | Rec. | Una: el cuadrado del hondo vale sobre los dos papeles; el nombre, en `currentColor` | heredado |
| Tamaño mínimo y margen | Rec. | `S` ≥ 32 px (horizontal), ≥ 48 px (vertical); margen 0,25 `S`; símbolo solo hasta 16 px | heredado (decisión 4 del Portal) |
| Usos prohibidos | Opc. | Degradado, sombra, redondeo, nombre en el acento, monograma en tinta oscura sobre el hondo (3,26:1) | heredado; el ratio, calculado |
| Logo fuera de la paleta | Opc. | No | — |

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Rec. | Big Shoulders Display 800/700, en mayúsculas; reserva `sans-serif` | heredado; `tokens.css` l.54 |
| Familia de texto | Rec. | Literata 400/600; datos en JetBrains Mono 500 | heredado; `tokens.css` l.55, l.57 |
| Licencia y archivo | Rec. | OFL las tres; el `.ttf` de Big Shoulders Display no consta instalado en el equipo de la sesión | `docs/handoff.md` de este repo, «Huecos de gimg» |
| Tracking y mayúsculas | Opc. | Wordmark: mayúsculas, tracking 0,01 em; etiquetas mono: 0,06 em | heredado; `tokens.css` l.59 |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | 1) Regla de mareas con marcas sin cifras y banderín del acento, sobre el mar grabado. 2) Sondas: líneas que bajan de la superficie al perfil del fondo, con una pesa marcada. 3) Nivel de burbuja: cápsula, dos marcas y burbuja hueca (icono de proyecto). 4) Dial de medida de media corona, aguja y eje hueco (estado vacío; reserva del icono). 5) Sondas como puntos y marcas en fondos y patrones | **[P]** |
| Motivos No | Obl. | Gráficas de barras o de crecimiento, podios, medallas, estrellas, notas, lupas, microscopios, probetas, robots, cerebros, balanzas de justicia, personas; cualquier cifra | propio + heredado |
| Palabras vetadas | Obl. | `graph`, `bar chart`, `growth`, `trophy`, `medal`, `podium`, `stars`, `score`, `percent`, `thumbs up`, `exam`, `teacher`, `judge`, `gavel`, `scales of justice`, `robot`, `brain`, `magnifying glass`, `microscope`, `lab coat`, `test tube`, `person`, `hand`, `face`; y las del Portal (`transparent`, `exactly`, `sky blue`) | propio + heredado |
| Estilo de imagen | Rec. | Los bloques [MAR], [PAPEL] y [LÍNEA] de «Recursos»; sin «Style: … Mood: …» | heredado |
| Lenguaje de forma | Opc. | Chaflán a 45°, radios 0, un solo grosor en iconos, nodos huecos | heredado |

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | No hay: grabado plano a dos tintas, sin fuente de luz; «a few glints of light on the crests» es trazo | heredado |
| Momento y clima | Rec. | Mar en calma; sin cielo ni horizonte | heredado |
| YAVG / SATAVG | Rec. | No hay rango propio; los del Portal sobre mar, a medir en la primera ronda | *(suposición)* |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | Propias, ninguna. De la familia: 15v de voz, 24 de Tarkor (q932), mar 32h (q984), 06 del Portal (q310, q311) | `docs/handoff.md` de este repo |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | Los del Portal, por tabla en «Recursos»: `icono`, `cuadrado`, `social`, `portada`, `tarjeta`, `cabecera`, `fondo`, `patron`, `formulario` | heredado |
| Zona reservada | Obl. | Sin texto compuesto. Zona limpia para el texto de la web: `social`, izquierda 1/3; `portada`, izquierda 1/2 y abajo; `cabecera`, izquierda 3/4; `tarjeta`, abajo 1/3 | propio, **[P]** |
| Composición por perfil | Rec. | No hay `compose`: ninguna imagen lleva texto ni logo | heredado |
| Piezas solo de logo | Rec. | `avatar` 512 e `icon` 180/192/512, con `gimg export` del símbolo (R14) | pendiente |
| Borrador | Opc. | `draft {scale 0.5, steps 4}` | heredado |
| Velo, logo en la pieza, palancas extra | Rec. / Opc. | No hay; palanca: `initImage` + `strength` 0,5 sobre boceto FLUX cuando salen cifras | heredado; R5 |
| Prioridad | Rec. | 1) R2 icono (R1 de reserva); 2) R6 `og` (y R7); 3) R5 portada; 4) R3-R4 símbolo y lockup; 5) R13 iconos de panel; después R8-R12 | **[P]** |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | No hay pieza compuesta. Para quien publique: «Medir, corregir y demostrar» | **[P]** |
| Subtítulo | Rec. | «Evidencia trazable para sistemas de IA: cada resultado, hasta su configuración exacta.» (86) | **[P]**, de `vision-v0.2.md` l.8-9 |
| Variaciones | Rec. | «Un dato ausente nunca cuenta como éxito.» · «Antes y después, con evidencia.» | **[P]**, de `vision-v0.2.md` l.9-11 |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | La del proyecto `portal` (`entrega`); la sesión copia lo aprobado a `piloto/` (regla de la persona) | `examples/portal/galivelop-images.json` |
| Nombre del archivo | Rec. | `{key}-{profile}.png` | heredado |
| Dónde se publica | Rec. | Portal: icono 23, `og` 24, tarjeta 15, portada (no consta aún ficha de GVE en el Portal). Front de GVE: iconos de panel, estado vacío, fondo, símbolo (no consta). GitHub: tarjeta social (no consta) | pendiente |
| Otras piezas que hace otro sistema | Rec. | Los gráficos de datos del front (`front/v2/generador/charts.py`): no son piezas de marca; toman de aquí solo el acento | `2e2dc15` |
| Conversión final | Opc. | `gimg export` a WebP, ICO y 1280×640 | heredado |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | La persona; se apunta en la bitácora de este repo y lo aprobado va a `piloto/` | regla de la persona |
| Contraste del texto | Rec. | No hay texto en imagen; en interfaz, los ratios de «Acento» | calculado |
| Umbrales de medida | Rec. | Sin número propio; se mira que el acento dé `#b4c424` y no pase de «un toque» | *(suposición)* |
| Cuándo se da por bueno | Opc. | Icono, `og` y portada con «sí»; lo que no salga en 2-3 intentos se apunta en troubleshooting y se rediseña | regla de la persona |

## 13. Fuentes de verdad

- galivelop-evaluator `2e2dc15` (`origin/ccr-4fe19114-typsl9`): `GLOSSARY.md` l.31-48 (nombre, siglas, términos);
  `docs/discovery/vision-v0.2.md` l.8-16 (propósito, posición); `docs/design/F-front.md` (reglas del front, paneles);
  `docs/roadmap.md` (bloques `E`, `M`, `R`, `N`, `F`); `front/v2/estilos/tokens.css` l.9-67 (neutros, acento
  provisional, estados, series, tipografías, medidas); `AGENTS.md` (flujo; nada visual).
- Portal, por su hoja en este repo `5089629`: `docs/marcas/portal/hoja.md` l.42-121 (identidad vigente), l.261-425
  (familia y decisiones de la persona).
- Este repo `5089629`: `examples/portal/galivelop-images.json` (perfiles); `examples/portal/orders/marca/` `23b-*`,
  `24-og-tarkor`, `15v-portada-voz`, `31d-*`, `32h-*`, `27-estado-vacio-zi`, `21-patron-pie`, `11-fondo-para-ti`
  (prompts hermanos); `docs/marcas/galivelop-voice-generator/tonos.py` (método).

**Lo que la configuración no refleja aún:** todo. No hay `examples/galivelop-evaluator/` ni pedidos; `brand.palette`
del proyecto `portal` no lleva `#b4c424` ni `#6b7509` (para medir el toque hace falta añadirlos o un proyecto propio).

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado |
|---|---|---|
| 1 | `name` válido | `galivelop-evaluator`: pasa |
| 2 | Propósito en una frase | pasa (sección 1) |
| 3 | «Nunca se muestra» no vacío | pasa |
| 4 | Paleta con ≥ 3 hex y roles | pasa (8 hex propuestos; fondo, texto, acento) |
| 5 | Símbolo SVG | «no hay»: lo hace `gimg brand` (R3) |
| 6 | Familia de titular instalada | pendiente del `.ttf` en el equipo |
| 7 | Motivos Sí y No, vetadas | pasa |
| 8-9 | Reglas de prompt | **Las del Portal**, no las de la plantilla (negaciones en el cierre, «like» en el bloque, sin «The image is completely textless.»): ver «Contradicciones» |
| 10 | Perfiles múltiplos de 64 con destino | pasa (los del Portal) |
| 11-12 | Zona reservada y titular | sin piezas compuestas; zonas limpias declaradas en la sección 9 |
| 13 | `delivery.dir` relativa | pasa (la del Portal) |
| 14 | «Quién decide» | pasa |
| 15-16 | Hex en `brand.palette`; destinos | no: falta añadir el acento (sección 13) |

## 15. Huecos que tocan a este proyecto

- No hay proyecto de gimg para GVE: los pedidos van al del Portal y el acento no está en su `brand.palette`.
- El nombre de color del acento en inglés es *(suposición)* hasta medir la primera ronda.
- Una escala graduada invita a cifras: R5, R6 y R9 pueden necesitar el camino FLUX → img2img.
- El recorte sobre magenta de un trazo verde oliva no se ha probado (los hermanos recortaron sobre verde).
- Big Shoulders Display sin `.ttf` en el equipo: R3 y R4 esperan a eso.

## Contradicciones

1. **Plantilla frente a Portal.** La plantilla (sección 0, «Familia Galivelop») aún da por heredados `#06121c`, Sora,
   Inter y la baldosa `rx` 30, y sus comprobaciones 8 y 9 vetan las negaciones y piden «The image is completely
   textless.». Manda la hoja del Portal (identidad del 2026-11-10 al 12): papel `#fbfcfd`, Big Shoulders Display,
   cuadrado con chaflán, negaciones en el cierre.
2. **Remates de los iconos.** La hoja del Portal pide remates y uniones redondos; los pedidos entregados `23b` de GVIG
   y voz piden «flat square line caps and sharp mitered joins» (el de developer, redondos). Esta hoja sigue la regla
   escrita (redondos); si la persona prefiere los de GVIG y voz, se cambia una frase del bloque [LÍNEA].
3. **Tono del icono de proyecto.** Los hermanos lo dibujan en su vivo; GVE, en el hondo, porque su vivo no se lee
   sobre papel. En la web da igual: el SVG va a `currentColor`.
4. **El front de GVE** rellena en oscuro con el tono claro y tinta encima; la familia pide el hondo con blanco en los
   dos temas (ver «Interfaz»).

## Cambios que pediría a la plantilla

- Actualizar el párrafo «Familia Galivelop» de la sección 0 y las comprobaciones 8-9 a la identidad vigente del Portal.
- Un campo «croma de recorte» por proyecto (`#00ff00` o `#ff00ff`), que hoy solo vive en la fila «Fondo y recorte».
- Un campo «tono del acento con que se dibuja el icono» (vivo u hondo), con su ratio sobre el papel.

## Lo que enseñó rellenarla

- Elegir el acento por el hueco mayor de la rueda de tonos (OKLCH) da un criterio comprobable y evita discutir a ojo.
- Un vivo muy claro cumple lo que voice y GVIG no (tinta encima, texto en oscuro) y falla lo contrario (no sirve ni
  como punto sobre papel): el reparto vivo/hondo del Portal no se traslada igual a todos los tonos.
- Un producto que ya tiene front necesita, además de las piezas de los hermanos, la serie de iconos de sus paneles y un
  estado vacío.
