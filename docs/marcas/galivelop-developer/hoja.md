# Hoja de estilo mínima: galivelop-developer

> **Dos identidades en esta hoja.** Desde el 2026-11-12 galivelop-developer sigue la identidad vigente del Portal con su
> propio acento: papel `#fbfcfd`, tinta `#13212b`, Big Shoulders Display, Literata y JetBrains Mono **heredados sin
> cambio**, y un acento verde azulado en dos tonos (vivo `#0e9a93`, hondo `#16827c`) en el lugar que el Portal da al
> alga. La referencia es [`../portal/hoja.md`](../portal/hoja.md), sección «Familia Galivelop: lo que heredan los
> productos» y su subsección «Decisiones de la persona (2026-11-12)». **Lo vigente son los cuatro bloques de abajo**, con
> la misma forma que la hoja del Portal: «Identidad vigente», «Interfaz», «Recursos» y «Familia Galivelop: cómo la
> cumple esta hoja». Lo que se hereda se dice como herencia y remite al Portal; lo propio va explícito. Las secciones
> 0-15, «Contradicciones» y «Lo que enseñó», [`biblia.md`](biblia.md) y los SVG de [`logos/`](logos/) describen la
> identidad anterior (`#06121c`, Sora/Inter, acento `#2BB3A3`, línea de luz, baldosa con degradado) y se quedan como
> histórico de r1-r5: no se siguen para piezas nuevas. De ellas sigue vigente la **voz** (secciones 1, 2 y 10: propósito,
> tono, ética, frases), que sale del repo de developer y no choca con nada.

Commits de referencia (leídos el 2026-11-12 con `git show`, **sin modificar nada**):

- **galivelop-developer** `main` `70b0396` (2026-10-25, «F0 cerrada»: lo publicado). Antes esta hoja citaba `8fa309c`
  (2026-10-25, rama `claude/f1-instalacion`, **por delante de `main`**: trae F1.1). Entre los dos solo cambian
  `docs/plan.md`, `docs/traspaso.md`, `gdev/engine.py`, `gdev/locales/{es,en}.json`,
  `gdev/machine_profiles/steam-deck.json` y tres archivos de tests (`git diff --stat origin/main 8fa309c`): `README.md`,
  `README.en.md`, `GLOSSARY.md`, `docs/adr/` y `.claude/gw.json` son idénticos, así que las líneas que la sección 13
  cita de ellos valen en `70b0396`. Hay además una rama `claude/gw-update-0.5.1` `82bb114` (flujo 0.5.1, sin fusionar).
- **Portal-Galivelop** rama `ccr-47f8fddd-o5ek6p` `6574c4f` (la que cita la hoja del Portal): `docs/marca.md` (m.),
  `src/estilos/global.css` (l.) y `src/data/productos/galivelop-developer.json`.
- **Este repo** `8bb0ae1` (rama `hojas-repos`): `docs/marcas/portal/hoja.md`.

**Lo primero que hay que saber:** el repo de galivelop-developer **sigue sin identidad visual**: en `main` `70b0396`
no hay ningún SVG, PNG, WebP, ICO, CSS ni HTML (`git ls-tree -r --name-only origin/main`: fuera de `.claude/`, solo
Markdown, JSON y Python), ni licencia (`README.md` l.52). Es una orden de terminal (`gdev`), sin interfaz gráfica. Todo
lo visual de esta hoja es herencia del Portal o cálculo; lo único que el Portal dice de este producto es su ficha
(`src/data/productos/galivelop-developer.json` `6574c4f`: l.3 nombre «Galivelop Developer», l.5 acento `#0E9A93`, l.8
estado «proximamente») y su tarjeta «Próximamente» (m.125).

---

## Identidad vigente (2026-11-12): lo que gimg necesita

Lo que se aplica a cada pedido nuevo de galivelop-developer. «Heredado» quiere decir: el valor es el de
[`../portal/hoja.md`](../portal/hoja.md), bloque «Identidad vigente», fila del mismo nombre, y aquí no se repite ni se
cambia. Donde esta hoja y la del Portal digan cosas distintas en algo heredado, manda la del Portal y esta se corrige.

| Campo | Valor | Estado |
|---|---|---|
| Paleta | **Heredadas:** cerúleo `#0072a8` (el mar, la tinta de color), papel `#fbfcfd`, gris tinta `#13212b`. **Propia:** el acento verde azulado **ocupa el lugar del verde alga** `#5d7a6a` y solo como «a touch of», nunca protagonista. Dos tonos calculados (ver «Interfaz», «Cálculo»): **vivo `#0e9a93`** y **hondo `#16827c`**; la variante de tema oscuro es el propio vivo. En imagen clara el toque es el hondo (4,52:1 sobre el papel, como el alga del Portal, que da 4,59); en la versión oscura, el vivo (5,23:1 sobre `#0d171e`). Frase de paleta: «Palette strictly limited to medium cerulean ocean blue #0072a8, off-white #fbfcfd, ink grey #13212b and a touch of deep teal #16827c.» *(suposición: el nombre «deep teal» se comprueba en una ronda; ninguna pieza se ha generado con él)*. Los grabados admiten «tints and shades» del cerúleo, no del acento; los iconos, **una sola tinta** `#13212b`. `brand.palette` para `gimg measure`: `#0072a8`, `#1aa6df`, `#fbfcfd`, `#13212b`, `#16827c`, `#0e9a93`, `#e6eef3`, `#0d171e`. El acento se distingue del cerúleo (ΔE76 39,1 el hondo y 43,0 el vivo, sobre el umbral de 15 de `gimg measure`); hondo y vivo entre sí no (ΔE76 9,7): la medida los cuenta juntos | heredado de `../portal/hoja.md` (fila «Paleta»; «Decisiones de la persona», punto 3); vivo: Portal `6574c4f` `src/data/productos/galivelop-developer.json` l.5; hondo: `tonos.py` (cálculo); qué tono va en la frase: **[P]** («Dudas», 3) |
| Tipografía | **Heredada:** Big Shoulders Display (títulos), Literata (texto), JetBrains Mono (datos y órdenes: `gdev task <nombre>`, `local/<tarea>`). **Ninguna imagen lleva texto**, ni generado ni compuesto: lo pone quien publica la pieza. Sora, Inter y DejaVu Sans Mono (secciones 5 y 10) quedan como histórico | heredado de `../portal/hoja.md` (fila «Tipografía»; «Tipografía por papel»; «Decisiones», punto 3) |
| Modelo y parámetros | **Heredado:** calidad `zimage-turbo-q6`, 8 pasos, cfg 1.0, euler; FLUX solo bocetos; Qwen-Image solo fotorrealismo (ninguna pieza de developer lo necesita); sin prompt negativo. Las piezas de r1-r5 salieron con FLUX: histórico | heredado de `../portal/hoja.md` (fila «Modelo y parámetros») |
| Mar y tecnología | **Heredado:** el mar pone el dónde, la tecnología el qué; ningún motivo náutico protagonista. **Propio:** developer tiene una de las tres excepciones cerradas del Portal, **el barco de papel sobre mar con olas** (q311): «ese barco es la portada de Developer» (la persona, 2026-11-11). Es la única; no añade otra sin decisión de la persona | heredado de `../portal/hoja.md` (fila «Mar y tecnología», excepción 2); Portal `6574c4f` `docs/marca.md` m.125, m.254 |
| Motivo propio | **Portada e ilustración grande: el barco de papel sobre el mar de carta con olas** (grabado a dos tintas), decidido por la persona; sustituye a «la terminal con la rama y el anillo» que pedía esta hoja (m.125). **Iconos y logo:** el motivo de software propio es **la terminal** (ventana con el chevrón del prompt y el cursor de bloque) y **la rama que sale de la línea principal y vuelve** (la tarea local que vuelve revisada), en línea simple; el anillo de revisión va como nodo hueco, según la regla de iconos de la familia. Verbo de la rama: «departs from the main line», nunca «leaves». **Sin engranaje** (cerrado por la persona el 2026-11-11) | barco: **decisión de la persona, 2026-11-11** (m.125, m.254; `../portal/hoja.md`, estado de las dudas, 4); terminal y rama para iconos y logo: **[P]**, de la sección 6 y `biblia.md` §4-§5 («Dudas», 4) |
| Dos registros de dibujo | **Heredado**, con los dos bloques literales del Portal: grabado a dos tintas para lo grande (portada, `og`, social) y línea simple para iconos y logo. No se mezclan. El estilo «clean minimal vector-like … soft glow» de la sección 6 es histórico: «minimal» y «glow» ya no se escriben | heredado de `../portal/hoja.md` (fila «Dos registros de dibujo») |
| Zonas limpias | **Heredado:** la zona se describe en positivo y al principio, como papel; la trama se confina; «filling the whole sheet to every edge» solo sin zona. Zonas de developer: tercio inferior limpio en la tarjeta (m.254) y **tercio izquierdo** en el `og` del Portal, para el icono (m.268). Las zonas `abajo 1/2` y `arriba 1/2` de la sección 9 eran para texto compuesto y quedan como histórico | heredado de `../portal/hoja.md` (fila «Zonas limpias»); Portal `docs/marca.md` m.254, m.268 |
| Recuentos | **Heredado:** nunca «exactly N». En developer el número que significa algo es **una** rama que sale y vuelve: el generado es boceto y se fija al vectorizar | heredado de `../portal/hoja.md` (fila «Recuentos») |
| Fondo y recorte | **Heredado:** lo que se recorta (logo, iconos sueltos) va sobre croma plano `#00ff00` y se recorta y vectoriza con `gimg brand`. El logo y los iconos se generan en una sola tinta, sin el acento: el color del cuadrado lo pone el SVG | heredado de `../portal/hoja.md` (fila «Fondo y recorte») |
| Versión oscura | **Heredado:** líneas `#e6eef3` sobre `#0d171e`, cerúleo igual. **Propio:** el toque de acento pasa del hondo al vivo `#0e9a93`. Iconos y logo, sin generar nada: el SVG a `currentColor` | heredado de `../portal/hoja.md` (fila «Versión oscura», propuesta del agente allí); el tono: `tonos.py` |
| Encuadre | **Heredado:** todo a sangre, sin marco ni banda; el chaflán del cuadrado del logo lo pone el SVG, no el modelo | heredado de `../portal/hoja.md` (fila «Encuadre») |
| Perfiles | **Heredados** los de `examples/portal/galivelop-images.json`: `cuadrado` e `icono` (logo, iconos), `tarjeta` (la 15), `social` (`og` 1200×630), `portada`. Los de `examples/galivelop-developer/galivelop-images.json` (`og`, `social`, `square`, `portrait`, `header`, con FLUX y `#06121c`) son histórico: **falta pasarlos a la identidad vigente** («Recursos», pendiente) | heredado de `../portal/hoja.md` (fila «Perfiles»); repo (`examples/galivelop-developer/galivelop-images.json`) |
| Referencias aprobadas | **Lo que gusta:** q311, el barco de papel sobre mar con olas (la persona, 2026-11-11), entregada como tarjeta 15. **Histórico, aprobado para la identidad anterior:** el `og` de r1 («sí» de la persona, 2026-10-26) y las piezas de r4-r5 (delegadas). **Rechazado:** el engranaje y la rama con anillo en la tarjeta 15 | Portal `docs/marca.md` m.125; `../portal/hoja.md` («Referencias aprobadas»; «Recursos», 15); sección 12 de esta hoja |

**Cómo se escribe el prompt.** Heredado entero de `../portal/hoja.md`, «Cómo se escribe el prompt» (orden, negaciones
solo en el cierre, ningún color fuera de las tintas, comprobación antes de encolar). Lo propio:

1. La frase final es la de la fila «Paleta», con el acento donde el Portal pone «seaweed green #5d7a6a»; en la versión
   oscura, «a touch of teal #0e9a93».
2. Palabras propias que siguen vetadas por ética y motivo (sección 2 y fila «Palabras vetadas» de la sección 6):
   `robot`, `brain`, `cloud`, `chip`, `gear`, `hand`, `screen`, `face`, `person`, `human`, `humanoid`, `magic`, `spark`,
   `keyboard`, `leaf`, `leaves`, `foliage`, `plant`. El código no es legible: «rows of short indented dashes».
3. De los motivos náuticos solo se nombra el barco de papel, y solo en la portada de developer.
4. El veto a `no`/`not`/`without`/`like` y el cierre «The image is completely textless.» son de la identidad anterior:
   no se aplican a piezas nuevas.

**Dudas que decide la persona** (2026-11-12; la recomendación va en cada una):

1. **Cerrada. Decidido por la persona (2026-11-12): el acento vivo es `#0E9A93`** (hondo `#16827c`); `#2BB3A3` pasa a histórico. El cálculo con `#2BB3A3` (hondo `#118376`) queda como histórico.
2. **Cómo se escribe el nombre en el lockup.** La regla común pide mayúsculas en Big Shoulders Display 800; el Portal
   lo llama «Galivelop Developer» (l.3) y esta hoja decía «galivelop-developer», en minúsculas y con guion, «sin
   mayúsculas sostenidas» (secciones 0 y 5). **Recomendación: «GALIVELOP DEVELOPER»**, sin guion, en el lockup y en
   titulares; `galivelop-developer` con guion queda para el repo, el nombre en código y la monoespaciada.
3. **Qué tono del acento va en la frase de paleta.** **Recomendación:** el hondo `#16827c` en piezas claras y el vivo
   `#0e9a93` en la versión oscura, que es la relación del alga del Portal en claro (≥ 4,5:1 sobre el papel). En oscuro
   el Portal pide ≥ 7:1 a su alga y el vivo da 5,23: el método no calcula un tono más claro y aquí no se inventa.
4. **Motivo de iconos y logo.** La persona cerró la portada (el barco) y quitó de ella la rama con anillo. **Símbolo del logo: decidido por la persona (2026-11-12)**: monograma «GD» en una tinta sobre el cuadrado con chaflán en el hondo `#16827c`; **orden:** `gimg brand square GD.svg --fill '#16827c' --ink '#ffffff'` monta el cuadrado con chaflán. **Sigue abierto** el icono de proyecto. **Recomendación:** la terminal con la rama que vuelve.
5. **Los SVG de `logos/`.** (Decidido por la persona, 2026-11-12: históricos, no se copian.) Los nueve son de la identidad anterior: baldosa con degradado y `rx` 30, nombre en Sora,
   `#2BB3A3`; no cumplen las reglas 2 y 3 del Portal y no salieron de gimg. **Recomendación:** dejarlos como histórico,
   no copiarlos al repo de developer y generar el logo nuevo con gimg («Recursos»).
6. **El lema y las frases** («El tercer relevo», sección 10) son propuesta aprobada por delegación y no chocan con
   nada: se conservan. Falta la versión `en` (el repo publica en es y en; el Portal, además, en gl).

---

## Interfaz de galivelop-developer: tokens y reglas (2026-11-12)

**Hoy no hay interfaz que vestir:** `gdev` es una orden de terminal y el repo no tiene CSS ni HTML (`70b0396`). Esta
sección fija lo que usaría una web, una página de documentación o las tarjetas de `gw-media-content` si llegan.

**Tokens heredados sin cambio** (valor por valor, de `../portal/hoja.md`, «Interfaz del Portal: tokens y reglas»):
`--papel`, `--superficie`, `--fondo-alterno`, `--superficie-2`, `--tinta`, `--tinta-2`, `--texto-3`, `--filete`,
`--reticula`, `--reticula-paso`, `--peligro*`, `--ok-texto`, `--noche`, `--velo*`, `--sombra`, `--chaflan*`, `--curva`
y `--transicion`. También la tipografía por papel y las once reglas de interfaz.

**Tokens propios: el acento.** Ocupan los papeles de `--celeste`, `--celeste-hondo`, `--enlace` y `--tinte` del
Portal. Los nombres de variable son **[P]**; los hex salen de `tonos.py` y los ratios son WCAG 2.x sobre esos hex.

| Token **[P]** | Claro | Oscuro | Papel que hace (el del Portal) | Contraste, con el umbral de la familia | Fuente |
|---|---|---|---|---|---|
| `--acento` (vivo) | `#0e9a93` | `#0e9a93` | Lo que `--celeste`: foco (`outline` 2 px), punto de estado, marca. Mismo hex en los dos temas | sobre papel claro 3,37 (no es color de texto en claro); blanco encima 3,46 (**nunca texto blanco encima**); tinta `#13212b` encima 4,74 (≥ 4,5); sobre `#0d171e` 5,23 (≥ 4,5); sobre la superficie oscura `#111f29` 4,84 | Portal `productos/galivelop-developer.json` l.5; `tonos.py` |
| `--acento-hondo` | `#16827c` | `#16827c` | Lo que `--celeste-hondo`: bloques grandes, enlaces en claro, cuadrado del logo, texto de acento en claro. **En oscuro no se oscurece otro paso:** los bloques con texto blanco usan el mismo hondo | sobre papel claro 4,52 (≥ 4,5); blanco encima 4,65 (≥ 4,5); en oscuro, como bloque sobre `#0d171e`, 3,90 (no es texto); la tinta `#13212b` encima 3,53 y la tinta clara `#e6eef3` 3,96: **sobre el hondo solo va blanco** | `tonos.py`: OKLCH L 0,5498, C 0,0903, 14 pasos |
| `--enlace` | `--acento-hondo` | `#0e9a93` | Enlaces y texto de acento | 4,52 / 5,23 (≥ 4,5 los dos). El Portal da 9,49 en oscuro; aquí manda el método, que pide 4,5 | `tonos.py`: la variante oscura es el vivo (regla 5 del método, 0 pasos) |
| `--tinte` | vivo al 12 % sobre papel (`#dff0f0`) | vivo al 18 % (`#0d2f33`) | Hover, chips, píldoras | tinta encima 13,95 / 12,16 (≥ 7) | `tonos.py` |
| Isobatas sobre el bloque | blanco al 20-50 % sobre `#16827c` | igual | Textura del bloque de acento | mismos porcentajes que el Portal | heredado |

**En qué se aparta del Portal, y por qué:** 1) el Portal oscurece su hondo en tema oscuro (`#0b5e88`) y aclara el
enlace (`#5cc8f2`); un producto lleva una sola variante oscura, la de texto (decisión de la hoja del Portal, punto 1).
2) Aquí la variante oscura coincide con el vivo, porque `#0e9a93` ya da 5,23:1 sobre `#0d171e`. 3) El alga `#5d7a6a` no
pasa a la interfaz del producto como acento secundario: su lugar lo ocupa el acento propio («Decisiones», punto 3);
«hecho» sigue siendo `--ok-texto` y el fallo `--peligro`, heredados. Al lado del Portal (su web, sus fichas) el acento
de developer es solo el toque.

**Reglas de interfaz:** heredadas las once. Las dos que nombran el acento, con los hex de developer: regla 6, el
acento en bloques grandes y planos es `#16827c`, con isobatas en blanco al 20-50 %; regla 10, sobre `#16827c`, texto
blanco (4,65:1); sobre `#0e9a93`, solo la tinta `#13212b` (4,74:1).

**Cálculo** (método de `../portal/hoja.md`, «Decisiones de la persona», punto 1; script [`tonos.py`](tonos.py), solo
biblioteca estándar). Se reproduce con:

```sh
python3 docs/marcas/galivelop-developer/tonos.py '#0E9A93'
```

```text
vivo                         #0e9a93   OKLCH L=0.6198 C=0.1053 h=189.05
vivo sobre papel claro       3.37      #fbfcfd
blanco sobre vivo            3.46      #ffffff
tinta sobre vivo             4.74      #13212b
vivo sobre papel oscuro      5.23      #0d171e
hondo                        #16827c   L=0.5498 C=0.0903 pasos=14
hondo sobre papel claro      4.52      #fbfcfd
blanco sobre hondo           4.65      #ffffff
hondo sobre papel oscuro     3.90      #0d171e
oscuro                       #0e9a93   L=0.6198 C=0.1053 pasos=0
oscuro sobre papel oscuro    5.23      #0d171e
tinte 12 % (claro)           #dff0f0   tinta encima 13.95
tinte 18 % (oscuro)          #0d2f33   tinta encima 12.16
```

Comprobado contra la hoja del Portal: el script da para `#0E9A93` los 3,37 / 3,46 / 5,23 de su tabla «Lo que falta» y,
con `#1AA6DF`, los 2,70 / 2,78 / 5,91 / 6,53 y los tintes 14,25 / 11,65 de su tabla de tokens. El croma baja de 0,1053
a 0,0903 en el hondo porque a esa luminosidad el tono 189° con el croma del vivo cae fuera de sRGB (regla 4). Lo que
el método no fija y el script decide está en su cabecera: el paso 0 es el propio vivo, el croma vuelve al del vivo en
cada paso y la tolerancia de «dentro de sRGB» es 1e-6. Con `#2BB3A3` (duda 1): hondo `#118376`, oscuro `#2bb3a3`.

## Recursos: entregado, cancelado y pendiente (2026-11-12)

Números de `docs/marca.md` del Portal (`6574c4f`, m.) donde los hay. Nada nuevo se ha generado para esta hoja.

| Recurso | Estado | Dónde está | Fuente |
|---|---|---|---|
| Tarjeta «Próximamente» de Developer (15) | **Entregada** el 2026-11-11: el barco de papel sobre mar con olas (q311), 720×405 | Portal `public/proyectos/galivelop-developer/proxima.webp`; original en `piloto/portal-marca/portal-web-final/portal/aprobadas/06-portada-developer-q311.png` (fuera de git) | m.125, m.254; `../../propuestas/portal/entrega-marca-2026-11-12.md` l.20-21 |
| Logo: cuadrado plano `#16827c` con chaflán y monograma | **Pendiente**: sin boceto. El `d` de `logos/` es de la identidad anterior | — | «Familia», «Logo, iconos e ilustración» |
| Lockup horizontal y vertical | **Pendiente**: depende del logo y de la duda 2 (el nombre) | — | `../portal/hoja.md`, «Decisiones», punto 4 |
| Icono de proyecto (23) y favicon | **Pendiente**: el Portal solo pide el 23 para Tarkor y Workflow (m.267); la ficha de producto usa hoy `"icono": "code"` (l.6) | — | m.267; `productos/galivelop-developer.json` l.6 |
| `og.jpg` del proyecto (24) | **Pendiente** en toda la familia: 1200×630, tercio izquierdo para el icono, el acento en el lugar del alga | Portal `tools/og/fuentes/galivelop-developer/og-fuente.png` (cuando exista) | m.268 |
| Social preview de GitHub (1280×640) y avatar | **Pendiente** con la identidad vigente; no consta en el repo cuál hay puesto | — | sección 11 |
| `examples/galivelop-developer/`: configuración, prompts y pedidos | **Histórico** (FLUX, `#06121c`, `#2BB3A3`, Sora/Inter): falta reescribirlos con Z-Image, la paleta de la fila «Paleta» y los perfiles del Portal. Fuera del alcance de esta hoja | repo `examples/galivelop-developer/` | `galivelop-images.json` l.9 (`#2BB3A3`) |
| Piezas de r1-r5 (`og`, cuadrado, vertical, cabecera, avatar) | **Histórico**: hechas con la identidad anterior, nunca publicadas | `piloto/r5/galivelop-developer/` (fuera de git) | secciones 9 y 12 |
| SVG de `logos/` (`a`-`d` y lockups) | **Histórico**: se conservan en la carpeta, no se usan en piezas nuevas («Dudas», 5) | [`logos/`](logos/) | sección 4 |
| Tarjetas de `gw-media-content` | **No hay**: developer lleva el flujo 0.3.0 en `main` (0.5.1 en una rama sin fusionar). El mapeo `Palette:` de la sección 11 es de la identidad anterior; el vigente va en la entrega | `../../propuestas/galivelop-developer/entrega-hoja-2026-11-12.md` | developer `70b0396` `.claude/gw.json` l.3; `82bb114` l.3 |

## Familia Galivelop: cómo la cumple esta hoja

Sigue, apartado por apartado, «Familia Galivelop: lo que heredan los productos» de `../portal/hoja.md`.

### Qué se copia tal cual

Las siete filas de la tabla del Portal, sin cambiar un valor: papel y superficie, tinta y sus dos escalones, filete y
retícula, tipografías por papel, forma (chaflán de 45° arriba a la derecha, `border-radius` 0, una sola sombra, sin
degradados), peligro / «hecho» / velos / noche, y los dos registros de dibujo con el modelo y las reglas de prompt.
Aquí no se copian los hex: se leen allí, para que no haya dos sitios que mantener.

### Qué cambia: los papeles de color

| Papel | En el Portal | En galivelop-developer | Relación que cumple |
|---|---|---|---|
| Acento vivo | `#1aa6df` | `#0e9a93`, igual en los dos temas | papel claro 3,37 (no es texto); blanco encima 3,46 (prohibido); tinta encima 4,74 ≥ 4,5; sobre `#0d171e` 5,23 ≥ 4,5 |
| Acento hondo | `#0072a8` / `#0b5e88` | `#16827c` en los dos temas | sobre papel 4,52 ≥ 4,5; blanco encima 4,65 ≥ 4,5. No llega al ≥ 7 que el Portal da en oscuro con su `#0b5e88`: un producto no lleva ese tercer tono |
| Enlace en oscuro | `#5cc8f2` | `#0e9a93` (el vivo) | 5,23 ≥ 4,5, el umbral del método; no llega al 7 del Portal |
| Tinte | vivo al 12 % / 18 % | igual, con `#0e9a93` | tinta encima 13,95 / 12,16 ≥ 7 |
| Acento secundario | alga `#5d7a6a` / `#8fb09e` | **no tiene**: el acento propio ocupa ese lugar, en poca cantidad, junto al Portal y en las piezas generadas | toque: `#16827c` en claro (4,52 ≥ 4,5), `#0e9a93` en oscuro (5,23; «Dudas», 3) |
| Isobatas sobre el bloque | blanco al 20-50 % | igual, sobre `#16827c` | mismos porcentajes |

Relaciones 1 y 3-6 del Portal (tinta sobre papel, tema oscuro, filete y retícula, texto sobre velo, estado nunca solo):
heredadas con sus hex. Relación 2: un acento con dos tonos, el hondo en superficie y el vivo en puntos. Relación 7: en
imagen generada, como mucho cerúleo, papel, tinta y un toque del acento; iconos, una tinta. **La proporción papel /
tinta / acento sigue sin número**, como en el Portal.

### Logo, iconos e ilustración

| Aspecto | Regla heredada | Lo propio de developer | Estado |
|---|---|---|---|
| Logo | Cuadrado de color plano del acento hondo, chaflán de 28/128 arriba a la derecha (lo pone el SVG), monograma de trazo 12/128 en una sola tinta; sin degradado, sombra ni redondeo; generado con gimg sobre croma `#00ff00` y vectorizado con `gimg brand trace` | Cuadrado `#16827c`; monograma **«GD»** en blanco `#ffffff` (4,65:1 sobre el hondo; la tinta `#13212b` daría 3,53). El dibujo sale del generador, en línea simple y sobre croma, como el «GV» del Portal (m.229) | **Pendiente**; el monograma «GD» y el blanco son **[P]** («Dudas», 4) |
| Lockup | Símbolo + nombre en Big Shoulders Display 800, mayúsculas, tracking 0,01 em, en `currentColor` (tinta `#13212b` en claro, `#e6eef3` en oscuro), nunca en el acento; horizontal: letras a 0,45 `S`, hueco 0,25 `S`, margen 0,25 `S`, mínimo `S` ≥ 32 px; vertical: nombre a 1,6 `S` de ancho, mínimo `S` ≥ 48 px; por debajo, el símbolo solo (hasta 16 px) | Nombre «GALIVELOP DEVELOPER» («Dudas», 2). Órdenes: `gimg brand wordmark "GALIVELOP DEVELOPER" --font <Big Shoulders Display variable .ttf> --weight 800 --spacing 0.01 -o wordmark.svg`; `gimg brand lockup simbolo.svg wordmark.svg --layout h --cap 0.45 --gap 0.25 --margin 0.25 -o galivelop-developer-lockup-h.svg`; lo mismo con `--layout v --width 1.6 --gap 0.25 --margin 0.25`. Las medidas anteriores (52/128, separación 28/128, mínimo 120 px, nombre en `#2BB3A3`) y los `*-lockup*.svg` de `logos/` son histórico | **Pendiente**: necesita el símbolo; la ruta de la fuente no consta en el repo |
| Iconos | Línea simple, un grosor, remates redondos, sin relleno ni trama, una tinta `#13212b`, legibles a 24 px, nodos e interiores huecos; `gimg brand trace --mode color --matte --dp-tol 0.5 --palette '#13212b,#fbfcfd'`; a `currentColor`; la serie entera, sin mezclar con lucide | Motivos: terminal con chevrón y cursor de bloque; rama que sale y vuelve, con el nodo hueco. El Portal ya tiene `terminal.svg` (9c, q537) y `ramas-unidas.svg` (8d, q547): son de sus series y no se reutilizan como marca de developer | **Pendiente**; motivos **[P]** |
| Ilustración | Grabado de carta náutica a dos tintas, bloque literal del Portal; Z-Image, 8 pasos, cfg 1.0; 120-200 palabras; cierre y frase de paleta al final | Sujeto: el barco de papel sobre el mar con olas (portada, `og`, social). Cuarto color de la frase: `#16827c` | q311 **entregada** (con la paleta del Portal, alga incluida: no se regenera); `og` y social, pendientes |
| Composición | Zona limpia en positivo y al principio; a sangre; sin texto en la imagen; sin «exactly N»; lo que se recorta, sobre croma | Nada. Los títulos y lockups compuestos de r4-r5 son histórico | heredado |
| Mar y tecnología | Ningún motivo náutico protagonista fuera de las tres excepciones | Usa la excepción 2 (el barco); ninguna más | heredado |

### Prohibido

Todo lo de «Prohibido en toda la familia» de `../portal/hoja.md`. Además, propio (sección 2 y `biblia.md` §1): nada
que lo muestre autónomo (trabaja en una rama acotada y lo revisa una persona o Claude), nubes (es local), engranajes,
pantallas con código legible, teclados, hojas o brotes en la rama; nada de «en abierto», «MIT» ni «open source» (el
repo no tiene licencia, `README.md` l.52), ni de mostrarlo ejecutando tareas mientras el `README` diga «aún no ejecuta
ninguna tarea» (l.10). De la identidad anterior quedan anulados, por chocar con lo vigente: el degradado de la baldosa,
el halo y el «soft glow», el `rx` 30, el nombre del lockup en el color del acento, y «el celeste del Portal junto al
acento» como prohibición (ahora el acento va junto al cerúleo como toque; ΔE76 39,1, se distinguen).

### Comprobación de esta hoja

Los seis puntos de «Cómo se comprueba una hoja de producto»:

| # | Punto | Resultado |
|---|---|---|
| 1 | Tres hex del acento calculados, con ratios, ninguno bajo 4,5 donde el método lo exige | **Pasa:** vivo `#0e9a93`, hondo `#16827c` (4,52 sobre papel; blanco 4,65), oscuro `#0e9a93` (5,23) |
| 2 | Papel, tinta, filete, retícula, tipografías y chaflanes coinciden con el Portal | **Pasa** por remisión: esta hoja no escribe otros valores en lo vigente |
| 3 | Frase de paleta del Portal con el acento en el lugar del alga; ningún prompt nombra otro color | **Pasa en la hoja; no en `examples/galivelop-developer/prompts/`**, que son histórico y están por reescribir |
| 4 | Logo: cuadrado plano del hondo con chaflán de 28/128 y trazo de 12/128, salido de gimg | **No pasa:** pendiente de generar; los de `logos/` son la baldosa anterior |
| 5 | Iconos de una tinta, sin relleno, nodos huecos, legibles a 24 px | **Sin iconos todavía** |
| 6 | Nada de «Prohibido en toda la familia» | **Pasa en lo vigente;** el histórico (degradado, `rx` 30, halo) está marcado como tal |

---

> **Histórico (identidad anterior, r1-r5).** De aquí al final la hoja es la aprobada el 2026-11-04 (decisiones delegadas;
> ver [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md)), con la forma de
> [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md). Estados: sin marca sale de un repo; **[P]** es propuesta
> del agente aprobada por delegación; *(suposición)* se comprueba en una ronda. No se sigue para piezas nuevas, salvo la voz
> (secciones 1, 2 y 10). Donde cita galivelop-developer `8fa309c`, vale lo dicho arriba en «Commits de referencia».

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «galivelop-developer»: en minúsculas, con guion, de una pieza, como se llama el repo y como va en el título del `README.md` y en el `<text>` de los lockups. La orden es `gdev`. En los textos del propio repo se le llama «el agente local» o «el tercer relevo» | developer (`README.md` l.1; `GLOSSARY.md` l.30-33; `docs/plan.md` D8); repo (`logos/galivelop-developer-d-lockup*.svg`) |
| Nombre en código | Obl. | `galivelop-developer` | repo (`examples/galivelop-developer/galivelop-images.json`, `name`); coincide con el nombre del repo y con `galivelop-developer.json`, su archivo de configuración (`README.md` l.38) |
| Fuente de verdad | Rec. | galivelop-developer `claude/f1-instalacion` `8fa309c` (voz, propósito, límites, idiomas, estado); Portal `aa76b34` (fondos, texto, tipografía, baldosa); este repo `fd2ae53` (acento, prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a developer en s3 y s4); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2 | repo (`docs/records/contenido/r1-fondos.md` l.44 y l.52; `docs/marcas/README.md` l.24-26, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`, sin cambiar ningún valor de la familia: fondo `#06121c`, texto `#eaf4fa`, Sora 700 e Inter, baldosa `rx` 30/128 con trazo 12. Solo añade el acento y sus dos tonos | heredado de Portal-Galivelop `aa76b34` (vía `biblia.md` §2-§3 y `docs/marcas/portal/biblia.md` §2); la familia para las herramientas la fija `docs/plan.md` l.662-666 **[P]** (la persona las añadió; la familia la propuso el agente) |
| Hereda de | Opc. | **Vigente:** [`../portal/hoja.md`](../portal/hoja.md), bloque «Identidad vigente» (2026-11-10 y 11). **Histórico (piezas r1-r5):** Portal-Galivelop `aa76b34` (leído solo a través de `biblia.md` §10 y `docs/marcas/portal/biblia.md`) | repo |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Agente de programación local: Aider sobre un modelo local, como tercer relevo junto a las sesiones de Claude Code, con la Steam Deck como perfil mínimo»; para los proyectos del taller que ya usan Galivelop-workflow y quieren tareas pequeñas y acotadas hechas en local | developer (`README.md` l.5-6 y l.16-18; `docs/plan.md` l.3-4) |
| Lema | Rec. | «El tercer relevo»; alternativa «Una rama acotada que vuelve revisada» | **[P]** (`biblia.md` §1 y §6); «tercer relevo» es literal del repo (`README.md` l.5 y l.17; `GLOSSARY.md` l.32; `docs/adr/0002-tercer-relevo.md`, título), pero como lema no lo usa ningún texto suyo |
| Tono | Rec. | directo, escueto, honesto con el estado («**aún no ejecuta ninguna tarea**», «Instalación (prevista, **todavía no existe**)», «Todavía no hay licencia»); dice sus límites antes que sus promesas («sin tocar nunca la bitácora, la rama protegida ni `.claude/`»); confía en el script, no en la regla escrita («Un modelo de 9-14B … se salta reglas escritas, así que los límites no se confían a las convenciones»). No es: vendedor, épico, «mágico», ni habla de autonomía | developer (`README.md` l.8-12, l.23-26, l.52; `docs/adr/0002-tercer-relevo.md` l.3-8) |
| Idiomas | Opc. | `es, en`: el repo publica el README en los dos (`README.md`, `README.en.md`), los textos visibles de `gdev` salen de un catálogo es/en (D7) y `.claude/gw.json` dice `language: es`, `visibleLanguages: ["es", "en"]`. Las piezas de r4-r5 van solo en `es`; la versión `en` de cada pieza está sin hacer | developer (`README.md` l.3; `README.en.md`; `gdev/locales/{es,en}.json`; `.claude/gw.json`; `docs/plan.md` D7); `en` en piezas **[P]** |
| Campo semántico | Opc. | dentro: agente local, tercer relevo, tarea local, rama `local/<tarea>`, motor, perfil de máquina, banco de velocidad y de calidad, tarea del banco, convenciones, revisar, volver al tronco; fuera: nube, autónomo, «el agente decide», robot, magia, copiloto | developer (`GLOSSARY.md` l.28-45, «Términos del proyecto»; `docs/adr/0001-ollama-compartido.md`); «volver al tronco» y la lista «fuera», `biblia.md` §6 **[P]** |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | robots, cerebros, rostros, personas, «magia» de IA, chispas, pantallas con código legible, teclados, nubes (es local), engranajes; nada que lo muestre autónomo: trabaja en una rama acotada y **lo revisa una persona o Claude antes del merge** | repo (`docs/plan.md` l.667-668, *No* de las herramientas; `biblia.md` §1 y §7). El principio sale de developer (`docs/adr/0002-tercer-relevo.md` l.3-5 y l.12-13: «se revisa entera»; `README.md` l.17), que no tiene texto de ética visual |
| Personas y rostros | Rec. | nunca personas, manos ni rostros (vetados `hand`; `face`, `person`, `human` **[P]**, sección 6) | repo (`biblia.md` §1 y §7; `docs/plan.md` l.667) |
| Promesas | Rec. | nada que lo muestre ejecutando tareas, instalado o con lanzador mientras el `README` diga que F0 está hecha y «aún no ejecuta ninguna tarea» (la bitácora del repo va por F1.1, en pausa, pero lo público es el README); **nada de «en abierto», «MIT» ni «open source»**: el repo no tiene licencia; nada de cifras del banco (tokens/s, % a la primera) hasta que `gdev bench` exista; nada de nube ni de precios | developer (`README.md` l.8-12, l.23-26, l.52; `docs/traspaso.md` l.11-14; `docs/plan.md` fases F1-F3) |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. (familia Galivelop) | oscura (por defecto) `#06121c` con rejilla de puntos tenue; clara `#f6fafd` **[P]**: ninguna pieza clara hecha | heredado de Portal-Galivelop `aa76b34` (`global.css` vía `portal/biblia.md` §2); repo (`galivelop-images.json` `brand.palette`; `piezas.json` `velo`; `prompts/r2-hex.txt` «#06121c») |
| Texto | Rec. (familia Galivelop) | `#eaf4fa` sobre oscuro (secundario `#9fb4c4`); `#0a1a28` sobre claro **[P]** (va con la pieza clara) | heredado de Portal-Galivelop `aa76b34`; `#eaf4fa` es el `color_texto` de las cuatro piezas de `piezas.json` y está en `brand.palette` |
| Acento | Obl. | `#2BB3A3` (verde azulado), uno por pieza: baldosa, rama local, anillo de revisión y nombre del lockup sobre oscuro. Sus dos tonos: oscuro `#157D74` (nombre sobre claro, tronco del símbolo suelto, extremo de la baldosa) y claro `#9FE3DA` (halo, «pale aqua» del prompt). **El acento de marca y el de la imagen son el mismo** (teal en las líneas, sin otros acentos) | **[P]** (`docs/plan.md` l.666-667, «acentos propuestos [P]»; `docs/marcas/README.md` l.38; `biblia.md` §2: los tonos «derivados a mano del acento»); repo (`galivelop-images.json`: `#2BB3A3` y `#9FE3DA` en `brand.palette`; `logos/galivelop-developer-d*.svg`) |
| Acentos en imagen, en orden de peso y significado | Rec. | no hay: un solo acento. En la imagen el teal es la rama y el anillo (lo que developer hace), el blanco suave es la línea principal (las sesiones) y el aqua `#9FE3DA` solo es halo; no son acentos distintos sino el mismo con su luz | repo (`prompts/estilo.txt`; `biblia.md` §7) |
| Resto de la paleta | Rec. | acento oscuro `#157D74` **[P]**; acento claro `#9FE3DA` **[P]**; superficies `#0c1d2b`, `#11283a`; borde `#1b3447`; texto 2 `#9fb4c4`; blanco `#FFFFFF` (trazo del símbolo en la baldosa). `brand.palette` lleva 7: `#06121c`, `#eaf4fa`, `#2BB3A3`, `#9FE3DA`, `#157D74`, `#FFFFFF` (los del logo) y `#9fb4c4` (texto 2); fuera quedan los de la pieza clara (sin pieza) | repo (`galivelop-images.json`; `biblia.md` §2); superficies, borde y texto 2 heredados de Portal-Galivelop `aa76b34` (`portal/biblia.md` §2) |
| Combinaciones | Rec. | oscura: `#06121c` + texto `#eaf4fa` + velo `#06121c:0.55` en `og` (zona `abajo`, el único `og` de la familia con velo: la línea de luz brillaba a la altura del título) y `#06121c:0.3` en `cuadrado`, `vertical` y `cabecera`; sobre imagen: el logo siempre en su baldosa, texto `#eaf4fa` en la mitad que el prompt deja vacía. Clara **[P]**: `#f6fafd` + `#0a1a28` + estructura en `#157D74` y `#2BB3A3` solo en lo que destaca (el acento a secas no llega a 3:1 sobre claro, según la biblia; sin medir) | repo (`piezas.json`, `velo`, `color_texto`; `r4-composicion.md` l.34-35); la clara **[P]** (`biblia.md` §2, sin pieza hecha ni contraste medido) |
| Prohibidos | Rec. | el acento como color de texto pequeño sobre claro; degradados fuera de la baldosa; el celeste del Portal `#1aa6df` junto al acento (se confunden); rojo o ámbar decorativos; negro `#000`; más de un acento por pieza; verde «hoja» o verde saturado (la rama es luz, no planta: ver «Palabras vetadas») | **[P]** (`biblia.md` §2: lo escribió el agente; ninguna pieza lo ha puesto a prueba); «verde hoja» **[P]** nuevo, de `r2-estilo.md` l.47 |
| Degradados | Opc. | solo la baldosa del logo (`#2BB3A3 → #157D74`) | repo (`logos/galivelop-developer-d.svg`); regla de familia en `docs/marcas/README.md` «Común a todos» |

**Medido:** la calibración da a este proyecto paleta ≥ 80 % (r1 y r5: 83-97 %; r2 palabras 87,4 %; r4 og compuesto 85,7 %; r5
cuadrado 91 %, vertical 88 %, cabecera 83 %) con `brand.palette` de 4 hex y ΔE76 < 15 (`docs/records/contenido/calibracion-measure.md`
l.43 y l.73). r2 enseñó que hex, palabras o materiales dan paleta parecida (80,3 / 87,4 / 65,8 %) pero no la misma imagen: material
añadió «un brote de hojas que no está en la biblia» y hex «un destello de más»; se eligió «palabras» (`r2-estilo.md` l.21-23 y l.47).
Sin portada en el Portal, developer **no tiene EMD** (`calibracion-measure.md` l.17 y l.76).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/galivelop-developer/logos/galivelop-developer-d.svg`: monograma «gd» en la baldosa de la familia (`rx` 30, degradado `#2BB3A3 → #157D74`), trazo blanco 12/128 con remates redondos; la «d» cierra su panza en un anillo (r 15) mayor que el de la «g» (r 13): el anillo de revisión. Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; colores `#2BB3A3`, `#157D74`, `#FFFFFF`. Las letras son trazos geométricos, no una fuente | repo (archivo, `3dc054d`); la elección de **d** es delegada **[P]** (`docs/marcas/README.md` l.19 y l.36: «hace familia con “gw”; la a se lee como una “b”»); las propuestas `a`-`c` siguen en la carpeta |
| Lockup (símbolo + nombre) | Rec. | dos archivos, los únicos de las siete marcas con variante por fondo: `logos/galivelop-developer-d-lockup-oscuro.svg` (nombre en `#2BB3A3`; el que usan las piezas) y `logos/galivelop-developer-d-lockup.svg` (nombre en `#157D74`, para fondo claro). `viewBox 0 0 770 128`: símbolo a la izquierda, «galivelop-developer» en Sora 700, 52/128 de alto, `letter-spacing` −1,5 (≈ −0,03 em), separación 28/128 (`x=156`). Llevan `<text>` con `font-family="Sora, sans-serif"` (reserva genérica), que la plantilla admite mientras `compose.fonts` garantice la fuente; el paso a trazos queda Opc. | repo (archivos, `3dc054d`; `piezas.json` `logo`); las medidas coinciden con `biblia.md` §3-§4 |
| Variante clara y oscura | Rec. | la baldosa lleva su propio fondo y vale sobre los dos; el nombre del lockup va en `#2BB3A3` sobre oscuro (`-lockup-oscuro.svg`) y en `#157D74` sobre claro (`-lockup.svg`); símbolo suelto (sin baldosa, como las propuestas `a` y `b`) en `#157D74` + `#2BB3A3` para claro y oscuro, sin archivo para `d` | repo (los dos lockups); el suelto **[P]** (`biblia.md` §4, sin archivo) |
| Tamaño mínimo y margen | Rec. | baldosa 16 px; símbolo suelto 24 px; lockup 120 px de ancho (por debajo, solo la baldosa); margen libre el grosor del trazo (12/128) por cada lado, que la baldosa ya incluye; nombre a la derecha a 52/128 de alto y 28/128 de separación, nunca debajo | **[P]** (`biblia.md` §4; reglas escritas por el agente al elegir) |
| Usos prohibidos | Opc. | girar, estirar, sombra o brillo, cambiar el radio de la baldosa, recolorear, invertir los colores del tronco y la rama (la rama es siempre el acento), usar el símbolo como icono de «terminal» genérico fuera de la marca, poner el símbolo suelto sobre la ilustración | **[P]** (`biblia.md` §4) |
| Logo fuera de la paleta | Opc. | `#157D74` y `#FFFFFF` están en el SVG y ya en `brand.palette` de la configuración (resuelto el 2026-11-04) | repo (`galivelop-images.json`, `biblia.md` §2) |

Copia en `examples/galivelop-developer/logos/`: **no hay** (F2.10, dec. 3, pendiente); `piezas.json` apunta hoy a
`docs/marcas/…/logos/`. En r4 el lockup de 770×128 salía a ~34 px de alto; desde entonces el piloto lo pone al 9 % del alto de la
pieza (`r4-composicion.md` l.29-33). El repo de developer no tiene favicon ni logo: el `d` sería el primero.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Rec. (familia Galivelop) | Sora 700 (reserva `sans-serif`); tracking −0,02 em en títulos y −0,03 em en el wordmark | heredado de Portal-Galivelop `aa76b34` (`Logo.tsx` vía `portal/biblia.md`); repo (`piezas.json` `fuente`; `componer.py` l.119 `peso_titulo=700`; lockups `font-family="Sora, sans-serif"`) |
| Familia de texto | Rec. | Inter (reserva `sans-serif`); **aprobado: subtítulo Inter 400 con opacidad 0,82** (la biblia decía 400/600 y se corrige; «Contradicciones», 2); titular Sora 700 | heredado de Portal-Galivelop `aa76b34`; repo (`piezas.json` `fuente_texto`; `componer.py` l.160); `biblia.md` §3 |
| Licencia y archivo | Rec. | Sora e Inter, OFL, del repo `google/fonts`; `examples/pilot/fuentes.sh` las baja a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`; no instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)*. DejaVu Sans Mono (órdenes `gdev task`, rutas): fuente del sistema, sin archivo en ningún repo *(suposición: instalada en la Deck)* | repo (`examples/pilot/fuentes.sh` l.8-12); la monoespaciada **[P]** (`biblia.md` §3, sin pieza que la use) |
| Tracking y mayúsculas | Opc. | títulos Sora −0,02 em; wordmark −0,03 em; sin mayúsculas sostenidas (el nombre va «galivelop-developer», minúsculas, con su guion, en una línea y un solo color); monoespaciada para claves y órdenes (`gdev task <nombre>`, `local/<tarea>`, `galivelop-developer.json`) | heredado de Portal-Galivelop `aa76b34` (vía `biblia.md` §3); la monoespaciada **[P]** |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivo propio (identidad vigente, 2026-11-11) | Obl. | **La terminal y la rama que vuelve revisada:** una ventana de terminal con el chevrón del prompt y el cursor de bloque esperando (lo que el Portal ya le pide en `orders/marca/15-proximamente-developer.json` y en el tercer icono de `09-iconos-participacion.json`), y, saliendo de ella o debajo, una rama que se aparta de la línea principal, da la vuelta y vuelve pasando por un anillo (la revisión). Icono, línea simple: «a terminal window with a prompt chevron and a block caret; below it a line with one side branch that departs and rejoins through a small ring». Portada, grabado: la terminal sobre el mar de carta, la rama como ruta trazada. **Sin engranaje:** el «a small gear beside it» del pedido 15 choca con «Nunca se muestra» de esta hoja (engranajes) y no aporta: se quita del pedido (duda 4 de `../portal/hoja.md`, bloque «Identidad vigente»). El verbo de la rama sigue siendo «departs» (no «leaves»). Acento `#2BB3A3` solo en logo, baldosa e interfaz | **propuesta del agente, 2026-11-11**, según `../portal/hoja.md` «Mar y tecnología»; piezas en `examples/portal/orders/marca/15-proximamente-developer.json` y `09-iconos-participacion.json` |
| Motivos Sí | Obl. | 1) una línea recta horizontal de luz blanca suave que corre desde el centro hasta el borde derecho (las sesiones, el tronco); 2) una rama de luz teal que sale de la línea, da una vuelta grande y cuidada que llena la mitad derecha y vuelve a la línea pasando por un anillo brillante (la tarea local que vuelve revisada); 3) la rama y el anillo brillan con fuerza y echan un halo teal sobre el fondo; 4) azul noche plano con rejilla de puntos tenue (la web del Portal). Sin usar aún, de la biblia: tres relevos paralelos, una consola vacía (solo la forma) | repo (`prompts/estilo.txt`, elegido en r2 con el «sí» de la persona en r1 sobre `og.txt`; `docs/plan.md` l.673; `biblia.md` §7) |
| Motivos No | Obl. | personas, manos, robots, cerebros, pantallas, teclados, código legible, nubes (es local), engranajes, chips y circuitos, texto; **hojas o brotes en la rama** (r2 material los pintó: la rama es luz, no planta) | repo (`biblia.md` §7; `docs/plan.md` l.667); las hojas, `r2-estilo.md` l.47 |
| Palabras vetadas | Obl. | `robot`, `brain`, `cloud`, `chip`, `circuit`, `gear`, `hand`, `screen`; más `like` como comparación y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7). **Añadidas (aprobadas por delegación el 2026-11-04):** `face`, `person`, `human`, `humanoid`, `magic`, `spark`, `sparkle`, `keyboard`, `code`, `text`, `letters`, `logo` (cierran lo que «Nunca se muestra» nombra y lo que se parece a texto o logo) y `leaf`, `leaves`, `foliage`, `plant` (lo que r2 material pintó). **Verbo de la rama:** «a side branch … leaves the main line» pasa a **«departs from the main line»** (`leaves` es también hoja y `branch` rama de árbol). Los prompts de `prompts/` que lo dicen (`estilo.txt`, `og.txt`, `r2-*.txt`, `r5-*.txt`) son histórico o están pendientes de reescribir con la zona; los pedidos `r2-control` y `r2-luz` siguen con «leaves» porque un test exige que copien `estilo.txt` y `r2-luz.txt`. `vector-like` no es comparación (se aplica el cambio de plantilla: `(?<!-)\blike\b`, ver comprobación 8). **Vigente desde el 2026-11-11:** las palabras propias (robot, cerebro, nube, chip, engranaje, mano, pantalla, persona, hoja/brote, texto) siguen vetadas por ética y motivo; `circuit` y `code` dejan de estar vetadas como palabras (la placa de circuito y la ventana de código son motivos de la familia, `13-cabecera-productos`), pero el código sigue sin ser legible: se dibuja «as rows of short indented dashes». El veto a `no`/`not`/`without`/`like` **no se aplica** a piezas nuevas: rige «Cómo se escribe el prompt» de `../portal/hoja.md` |
| Estilo de imagen | Rec. | «Style: clean minimal vector-like digital illustration, thin precise strokes, soft glow, flat dark background. Colours: deep midnight navy, teal, pale aqua, soft white. Mood: calm, careful, reliable.» | repo (`prompts/estilo.txt`, elegido en r2) |
| Lenguaje de forma | Opc. | una línea recta y continua (las sesiones), una rama corta que vuelve, un anillo donde se revisa; tres trazos paralelos para «relevos»; trazo 12/128 redondo, anillos 9/128; `rx` 30/128 en la baldosa; radios 18 y 10 px en interfaz; nada de engranajes, rayos ni chispas; fondo plano, brillo suave | heredado de Portal-Galivelop `aa76b34` (`gv-logo.svg`, vía `biblia.md` §5); lo demás **[P]** (`biblia.md` §5) |

Prompts del proyecto (`examples/galivelop-developer/prompts/`): `estilo.txt` (= `r2-palabras.txt`, 144 palabras; «sí» de la
persona en r1 sobre `og.txt`, elegido en r2 por el agente), `og.txt` (r1, 121: la línea cruzaba toda la pieza, «nearly empty»;
superado por `estilo.txt`, se conserva como historia), `r2-hex.txt` (145) y `r2-material.txt` (161) (descartados),
`r5-cuadrado.txt` (150), `r5-vertical.txt` (151), `r5-cabecera.txt` (146) (compuestos y medidos), `r2-luz.txt` (173, sin
veredicto). Todos de 121-173 palabras, dentro del rango 120-320 (`og.txt` en el suelo); todos acaban en «The image is completely
textless.». Ninguno lleva palabra vetada de la biblia ni negación.

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | la luz sale de las propias líneas (no hay fuente externa); en `r2-luz.txt`: «the only light comes from the glowing lines on the right», el anillo «a quarter of the way in from the right edge, the brightest point of the image», y el brillo «fades into darkness toward the left» | repo (`prompts/estilo.txt`); la variante *(suposición: r2-luz sin veredicto)* |
| Momento y clima | Rec. | escena oscura, dicha al principio: «Dark wide abstract technical illustration: the whole frame is deep midnight navy…» (r2-luz); en `estilo.txt` el fondo oscuro va en la primera frase | repo (`orders/r2-luz.json`) *(suposición)* |
| Luminosidad objetivo (YAVG) | Rec. | 25-50 (r1 y r5: 28-48; r2 palabras 36,8; r3 borrador 29, definitivo 39; r4 og compuesto 36,94) | repo (`calibracion-measure.md` l.43 y l.73; `r2-estilo.md` l.23; `r3-borrador.md` l.52; `r4-composicion.md` l.22) |
| Saturación objetivo (SATAVG) | Rec. | 9-12 (r1 y r5: 10-11; r2 palabras 12,7; r4 og 10,43) | repo (`calibracion-measure.md` l.43 y l.73) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **publicada dónde:** en el repo de developer, nada (sin web, sin favicon, sin social preview declarado: **no consta en el repo**); en el Portal, nada (developer no tiene ficha ni portada: la calibración lo midió «sin portada», solo con las piezas del piloto); en GitHub, el social preview del repo `github.com/Zeldris/galivelop-developer` no se puede comprobar desde el repo (lo fija la interfaz). **Vale como referencia:** **no hay**; cuando la persona apruebe el `og` de r4 o el `social`, esa pieza pasa a ser la primera imagen de marca y la referencia de la EMD **[P]** | repo (`calibracion-measure.md` l.17, l.43 y l.76); developer (`git remote`, sin ningún archivo de imagen en el árbol) |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 → 1200×630 (`targetWidth`/`targetHeight`), `social` 1280×640 (= destino), `square` 1024×1024 → 1080×1080 (`cuadrado`), `portrait` 896×1152 → 1080×1350 (`vertical`), `header` 1536×512 → 1500×500 (`cabecera`) | repo (`galivelop-images.json`; `piezas.json`); los tres de r5 **[P]** (aprobados por delegación; `docs/plan.md` l.752) |
| Zona reservada | Obl. | **Aprobada: `abajo 1/2` en `og`, `social` y `header`; `arriba 1/2` en `square` y `portrait`.** Una sola zona por perfil, la misma en prompt, plantilla y medida. En `og`, `social` y `header` la línea de luz y el bucle van en la mitad superior y la inferior queda vacía («The lower half of the frame is a plain, empty dark background with only the faint grid»); `square` y `portrait` ya lo piden así con la mitad superior libre. En píxeles (conversión de la plantilla): `og` 1200×630 `abajo` → `0,315,1200,315`; `square` 1080×1080 `arriba` → `0,0,1080,540`. La caja del piloto es 48 % del alto menos margen (`arriba`/`abajo`, 6 %), no 1/2: se alinea al portar a `compose`. **Pendiente (los prompts no se tocan en esta tarea):** `estilo.txt`, `og.txt` y `r5-cabecera.txt` siguen pidiendo la mitad izquierda libre; hay que reescribirlos a mitad inferior libre en la ronda siguiente (también `r2-control` y `r2-luz`, que hoy copian `estilo.txt` y `r2-luz.txt` y un test lo exige) | repo (`prompts/*.txt`; `piezas.json` `zona`; `componer.py` `caja_zona` l.105-115; `r4-composicion.md` l.34-35; `r5-piezas.md` l.53-55); decisión 2 de `docs/records/decisiones-hojas-2026-11-04.md` (criterios 2 y 3: es lo compuesto y medido; el fallo se debía a que el prompt pedía otra zona). La biblia §7 y §2 quedan corregidas |
| Velo por perfil | Rec. | `og` `#06121c:0.55` (el único `og` de la familia con velo; 0,55 no bastó con la zona izquierda y sí con `abajo`; el «0 en `og`» de la plantilla es un ejemplo, no una regla); `cuadrado`, `vertical` y `cabecera` `#06121c:0.3` | repo (`piezas.json`, `velo`; `r4-composicion.md` l.22 y l.34-35) |
| Logo en la pieza | Rec. | lockup oscuro al 9 % del alto de la pieza (57 px en el `og`), en lo alto de la caja de la zona con el título debajo, margen 6 %; solo baja si no cabe a lo ancho de la columna | repo (`componer.py` l.124-137; `r4-composicion.md` l.29-33) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 %, título Sora 700, subtítulo Inter 400). Portar a `compose: {template, logo: "logos/galivelop-developer-d-lockup-oscuro.svg", fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-developer-d.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay; el repo de developer no tiene web ni favicon que lo consuma | repo (`piezas.json`); `icon` **[P]** |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos: YAVG/SATAVG/paleta 29/12/91 % frente a 39/12/87 % del definitivo; anticipa el anillo y la línea, pero el definitivo alargó la línea hacia la izquierda (la que luego cruzó el título). `draft: {scale: 0.5, steps: 4}` declarado en `og` | **[P]** aprobado por delegación (F2.10, dec. 7; `r3-borrador.md` l.52 y l.64-66) |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin LUT (paleta 83-97 %), sin conversión final. **Candidata:** imagen inicial (boceto SVG a 0,85-0,97) si la persona prefiere la zona izquierda para el `og` y el prompt no consigue que la línea respete la mitad (r2-luz la pide «from the right edge to the middle»; sin veredicto) | repo (`r2-estilo.md` l.47; `r5-piezas.md` l.36); el boceto *(suposición)* |
| Prioridad | Rec. | la de la biblia: 1) logo elegido y `avatar` 512; 2) `social` 1280×640 de GitHub; 3) `og` 1200×630; `banner` del Portal solo si la persona decide presentar las herramientas allí. Hechas en el piloto: `avatar`, `og`, `cuadrado`, `vertical`, `cabecera`; `social` sale del mismo fondo que `og` sin recortar | repo (`biblia.md` §9; `docs/plan.md` l.668-669 y l.675) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | «El tercer relevo.» (17 caracteres), en `og` | **[P]** (`piezas.json`, r4; el lema es propuesta, aunque «tercer relevo» sea literal de `README.md` l.5 y de la ADR 0002) |
| Subtítulo | Rec. | «Aider sobre un modelo local, junto a las sesiones de Claude Code.» (65) | **[P]** como frase (`piezas.json`, r4); sus hechos son literales de developer (`README.md` l.5: «Aider sobre un modelo local, como tercer relevo junto a las sesiones de Claude Code») |
| Variaciones, ganchos y cierres | Rec. | usados en r5: `cuadrado` «Tareas pequeñas, en local.» (26) / «Revisadas enteras. Lo revisa una persona. Siempre.» (50); `vertical` «Sin nube, sin sudo, sin nada residente.» (39) / «Un Ollama para toda la máquina.» (31); `cabecera` «Una rama acotada que vuelve revisada.» (37) / «Vuelve al tronco cuando alguien lo ha leído.» (44). Sin usar: «¿Qué puede hacer un modelo de 9B sin tocar tu main?» | **[P]** (`biblia.md` §6; `piezas.json`). Sus hechos salen de developer: «sin `sudo`» (`README.md` l.25), «un solo Ollama por máquina» (`docs/adr/0001-ollama-compartido.md` l.3), «se revisa entera» (`docs/adr/0002-tercer-relevo.md` l.12-13), «vuelve a la rama de trabajo por `git merge`, después de que lo revise Claude … o la persona» (l.3-5) |
| Longitud máxima por campo | Rec. | la fija la composición: `componer.py` baja el cuerpo hasta 16 px y falla si el texto no cabe en la zona. Orientativo: titular ≤ 40 (los de r4-r5 van de 17 a 39), subtítulo ≤ 70 (el más largo, 65). Con la zona `abajo` la caja es ancha y baja: cabe más por línea y menos líneas | repo (`examples/pilot/componer.py` l.135-160; `piezas.json`) |
| Wordmark compuesto como texto | Opc. | el nombre va en el lockup (Sora 700, `#2BB3A3` sobre oscuro, `#157D74` sobre claro), nunca como `text` del pedido | repo (lockups) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` | repo (`galivelop-images.json` `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto, escrito explícito) | repo (`delivery.template`) |
| Dónde se publica cada pieza | Rec. | `social`: social preview del repo `github.com/Zeldris/galivelop-developer` (no comprobable desde el repo); `avatar`: GitHub y Discord (no consta en el repo); `og`: no hay web que lo consuma (no consta); `banner`: portada 1600×640 en el Portal **solo si la persona decide presentar las herramientas allí** (hoy developer no está en el Portal); `square`, `portrait`, `header`: redes del taller, sin canal declarado en el repo de developer (su `.claude/gw.json` 0.3.0 no tiene nota de canales) | developer (`git remote`; `.claude/gw.json`; sin `docs/media/`); Portal y `banner` **[P]** (`biblia.md` §9; `docs/plan.md` l.668-669) |
| Otras piezas de marca que hace otro sistema | Rec. | **no hay hoy:** developer lleva Galivelop-workflow 0.3.0, sin `gw-media-content`. **Lo habrá** cuando actualice el flujo (este repo ya tiene `gw-media-content` y `gw-media-content-now` en 0.5.0): sus tarjetas 1200×675 saldrían con la paleta genérica de las plantillas salvo que el repo tenga una nota `.claude/gw/gw-media-content.md` con `Palette:`. Esta hoja es la fuente de esos hex: `--background: #06121c; --surface: #0c1d2b; --border: #1b3447; --text: #eaf4fa; --muted: #9fb4c4; --accent: #2BB3A3; --accent-text: #06121c; --good: #2BB3A3; --font: Sora, Inter, …` | developer (`AGENTS.md` l.1 «v0.3.0»; `.claude/skills/` sin `gw-media-content`); repo (`.claude/skills/gw-media-content/`, `.claude/gw/gw-media-content.md`); el mapeo **[P]** |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto, no declarado) | repo (esquema) |
| Conversión final | Opc. | `banner` a `.webp` si va al Portal *(suposición: como la portada de Tarkor)*; nada más | — |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona: r1 «sí» (2026-10-26, s3 y s4: «limpio pero casi vacío; la línea cruza la mitad izquierda»); r2-r5 delegado al agente. Apuntado en `docs/records/contenido/r1-fondos.md` l.44 y l.52, `r2-estilo.md` l.47 (elegida «palabras»), `r4-composicion.md` l.22 y l.34, `r5-piezas.md` l.36 y l.53 | repo |
| Contraste del texto | Rec. | ≥ 4,5:1 (por defecto); medido: og r4 14,56 (peor 11,82) con velo 0,55 y zona `abajo`; r5 cuadrado 17,01 (16,87), vertical 16,5 (16,33), cabecera 13,22 (9,87) con velo 0,3. Todas sobre el 7:1 de AAA. **La medida no vio la línea que cruzaba el título** en r4 (peor 16,72 con zona izquierda) ni la que lo tocaba en la cabecera de r5 (15,96): un trazo fino ocupa menos del 10 % de la caja y el p90 lo ignora | repo (`r4-composicion.md` l.22 y l.34-35; `r5-piezas.md` l.36 y l.53-55) |
| Umbrales de medida | Rec. | los de las secciones 3 y 7: paleta ≥ 80 %, YAVG 25-50, SATAVG 9-12 | repo (`calibracion-measure.md` l.73) |
| EMD frente a la marca | Opc. | no hay: sin imagen de marca (sección 8). Cuando la haya, empezar por los de Tarkor (Cb ≲ 6, Cr ≲ 7,5) y revalidar | repo (`calibracion-measure.md` l.17 y l.76) |
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» de la persona en r1 y la palanca de r1 (más presencia a la derecha, línea solo a la derecha) funcionó en r2; r5 dio las tres piezas de formato a la primera, con la zona de la cabecera cambiada a `abajo`. La zona del `og` queda decidida (`abajo 1/2`, sección 9); queda reescribir el prompt a mitad inferior libre y generar de nuevo | repo (registros r1-r5) |

## 13. Fuentes de verdad

**galivelop-developer**, `main` `70b0396` (releído el 2026-11-12 con `git show`, nada modificado). Las líneas de `README.md`,
`README.en.md`, `GLOSSARY.md`, `docs/adr/`, `.claude/gw.json` y `AGENTS.md` son las mismas que en `claude/f1-instalacion`
`8fa309c`, que es lo que esta lista citaba; `docs/traspaso.md` l.11-14 (F1.1 hecha, en pausa), `gdev/locales/` y las líneas de
`docs/plan.md` son de `8fa309c`, que va por delante de `main`:

- `README.md` l.1 (nombre), l.3 (enlace a `README.en.md`), l.5-6 (propósito), l.8-12 («Estado»: F0 hecha, «aún no ejecuta
  ninguna tarea»), l.14-21 («Qué es»: `local/<tarea>`, nunca la bitácora, la rama protegida ni `.claude/`, «tercer relevo»,
  «defensas hechas por script»), l.23-26 («Instalación (prevista, todavía no existe)», sin `sudo`), l.28-41 (subcomandos
  `gdev`, `GDEV_LANG` es/en, `galivelop-developer.json`), l.52 («Todavía no hay licencia»); `README.en.md` (idioma `en`).
- `GLOSSARY.md` l.28-45 («Términos del proyecto»: agente local, tercer relevo, tarea local, perfil de máquina, motor, bancos,
  tarea del banco, convenciones); l.11 («Relevo», del flujo).
- `docs/adr/0002-tercer-relevo.md` l.1-8 y l.12-15 (rama acotada, revisión de Claude o la persona, límites por script, «se
  revisa entera»); `docs/adr/0001-ollama-compartido.md` l.1-7 (un Ollama por máquina).
- `docs/plan.md` l.1-4 (qué es), D3 (tercer relevo), D7 (es/en), D8 (`gdev`), D13 (sin `sudo`, `pip` ni `distrobox`), tabla
  de fases F0-F5 (qué no existe aún).
- `.claude/gw.json` (`version: 0.3.0`, `language: es`, `visibleLanguages: ["es", "en"]`, `pushToProtected: pr`); `AGENTS.md`
  l.1 y l.6 («Galivelop-workflow v0.3.0»); `docs/traspaso.md` l.11-14 (F1.1 hecha, en pausa).
- `gdev/locales/{es,en}.json` (todo texto visible sale del catálogo: tono escueto, «no se puede…», «no responde…»).
- `git remote`: `https://github.com/Zeldris/galivelop-developer.git`.
- **No existe** en el repo: SVG, PNG, WebP, ICO, CSS, HTML, favicon, `LICENSE`, `docs/media/`, `.claude/skills/gw-media-content`,
  `.claude/gw/gw-media-content.md`.

**Portal-Galivelop** `aa76b34` (marca paraguas, «heredado de»), leído solo a través de `biblia.md` §10 y
`docs/marcas/portal/biblia.md` §2-§4: `src/estilos/global.css` (fondos `#06121c`, `#f6fafd`; texto `#eaf4fa`, `#9fb4c4`,
`#0a1a28`; superficies `#0c1d2b`, `#11283a`; borde `#1b3447`), `src/components/Logo.tsx` (Sora 700, −0,03 em),
`public/marca/gv-logo.svg` (baldosa `rx` 30, trazo 12).

**Este repo**, `f2-motor` `fd2ae53`:

- `examples/galivelop-developer/galivelop-images.json` (`name`, `brand.palette` de 4 hex, `delivery`, perfiles `og` y `social`;
  último cambio `b65bd81`).
- `examples/galivelop-developer/piezas.json` (`a50b544`: fuentes Sora/Inter, textos, zona `abajo`/`arriba`, color de texto y velo
  de las cuatro piezas compuestas, ruta de los lockups y del avatar).
- `examples/galivelop-developer/prompts/estilo.txt` (`6065ac1`), `og.txt`, `r2-palabras.txt`, `r2-hex.txt`, `r2-material.txt`,
  `r2-luz.txt`, `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` y `orders/r1-og.json`, `r2-control.json`, `r2-luz.json`
  (motivos, estilo, zona por formato, luz).
- `docs/marcas/galivelop-developer/logos/galivelop-developer-d.svg`, `-d-lockup.svg`, `-d-lockup-oscuro.svg` (último cambio
  `3dc054d`); las propuestas `a`-`c` siguen en la carpeta.
- `docs/marcas/README.md` l.19 (fila del proyecto, elegido **d**), l.24-26 y l.36 («Elegido por el agente»: quién decide, el
  porqué de **d**), l.38 (acento `#2BB3A3`), l.80-99 («Común a todos», tabla de destinos), l.186-191 (conceptos de logo).
- `docs/marcas/galivelop-developer/biblia.md` (`74d99f8`, contenido de `a50b544`; paleta, tipografía, reglas del logo, vetos,
  frases; lo que es **[P]** allí lo sigue siendo aquí).
- `docs/plan.md` l.662-675 («Herramientas del taller»: familia del Portal, acentos [P], *No*, formatos, metáfora de developer),
  l.450-451 y l.752 (`piezas.json` y perfiles de r5: lo decide la persona), l.768 (`avatar`/`icon` a F2.12), l.803 y l.824
  (developer en r3 y r4: la línea que cruzó el título, zona `abajo`).
- `docs/records/contenido/calibracion-measure.md` l.17, l.43, l.73, l.76; `r1-fondos.md` l.44, l.52, l.61; `r2-estilo.md`
  l.21-23, l.47; `r3-borrador.md` l.52, l.64-66; `r4-composicion.md` l.22, l.29-35; `r5-piezas.md` l.36, l.52-55, l.64.
- `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.173-186 y l.202-211 (lectura de las herramientas: sin identidad
  visual, límites, metáfora).
- `examples/pilot/componer.py` l.105-115 (`caja_zona`), l.119 (`peso_titulo=700`), l.124-137 (margen 6 %, logo al 9 %), l.135
  (cuerpo del título), l.160 (subtítulo 400, opacidad 0,82); `examples/pilot/fuentes.sh` l.8-12 (origen y licencia de las fuentes).

Sin línea aquí y por tanto **[P]** o *(suposición)*: acento y sus dos tonos, lema y frases, logo elegido, reglas del logo tras
elegir, pieza clara, prohibidos de la paleta, monoespaciada, palabras vetadas añadidas y la hipótesis de «leaves», zona del
`og`/`header` (prompt frente a composición), perfiles `square`/`portrait`/`header`, `draft`, `compose`, `icon`, el Portal como
destino, el mapeo de `Palette:` para un futuro `gw-media-content`.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo y a developer; actualizado el 2026-11-04):

- Hecho en `galivelop-images.json`: `og` con `targetWidth` 1200 / `targetHeight` 630 y `draft`; perfiles `square`, `portrait` y
  `header` con su destino; `#157D74`, `#FFFFFF` y `#9fb4c4` en `brand.palette`.
- **Prompts:** `estilo.txt`, `og.txt` y `r5-cabecera.txt` siguen con la mitad izquierda libre; hay que reescribirlos a mitad
  inferior libre y «departs from the main line» (también los pedidos `r2-control` y `r2-luz`: hoy copian `estilo.txt` y `r2-luz.txt` y un test lo exige; se cambian a la vez que ellos).
- `compose`: plantilla, fuentes, zona (`abajo 1/2`), velo (0,55 en `og`) y logo en la pieza viven en
  `examples/pilot/componer.py` y `piezas.json`.
- Copia de los logos en `examples/galivelop-developer/logos/`: pendiente (F2.10, dec. 3).
- En el repo de developer: nada que recibir hoy (sin web, favicon ni `gw-media-content`); la propuesta
  `docs/propuestas/galivelop-developer.md` le llevaría la hoja, el logo `d` como favicon y social preview, y la nota `Palette:`
  para cuando actualice el flujo.

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; es la primera frase del `README.md` de developer) |
| 3 | «Nunca se muestra» no vacío | pasa; nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | hex pasa (4); fondo `#06121c`, texto `#eaf4fa` y acento `#2BB3A3` están (la hoja nombra los roles, la configuración no los lleva) |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, `<title>`, sin `<text>`/`<image>`/`filter`; «sí» a 16 px según la tabla de la biblia §4); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: sin `compose.fonts`, y las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts`; DejaVu Sans Mono sin archivo declarado |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | pasa en los históricos con la regla de plantilla aprobada (`like` no precedido de guion): ninguno de los prompts ni los pedidos lleva las ocho palabras de la biblia, las añadidas ni `no`/`not`/`without`/`never`. Los pedidos `r2-control` y `r2-luz` y los prompts históricos y `estilo.txt` siguen con «leaves» (verbo; `leaves` es vetada) hasta reescribirlos. **Para piezas nuevas no se aplica tal cual**: la comprobación es el punto 5 de «Cómo se escribe el prompt» de `../portal/hoja.md` |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (121-173 palabras), los nueve |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | pasa (`og`, `square`, `portrait`, `header` con destino) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | **decidida, pendiente de prompts:** la zona es `abajo 1/2` (`og`, `social`, `header`) y `arriba 1/2` (`square`, `portrait`); `square` y `portrait` ya la dicen; `estilo.txt`, `og.txt` y `r5-cabecera.txt` aún piden la izquierda. Ningún perfil la declara en la configuración (hueco de `compose`) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (17 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | pasa para la pieza oscura y el logo (`#06121c`, `#eaf4fa`, `#2BB3A3`, `#9FE3DA`, `#157D74`, `#FFFFFF`, `#9fb4c4`); los de la pieza clara no están (sin pieza) |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | pasa: `og`, `square`, `portrait` y `header` declaran destino; `social` es destino = generación |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 15** (familia
Galivelop; 18 con la familia propia). Fondo, texto y titular son Rec. y están completos con los valores de la familia, sin cambios.

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan: roles de la paleta (`brand.palette` no distingue el acento de sus tonos ni del
blanco del logo), zona reservada (solo en prompt y en `piezas.json`/`componer.py`, y aquí además no coinciden), velo y logo en
la pieza (solo en `componer.py`; el velo 0,55 del `og` no está en ningún campo), palabras vetadas sin campo, `avatar` sin perfil
(lo hace `piezas.py`), tipografía sin licencia ni ruta declaradas (DejaVu Sans Mono ni siquiera tiene archivo), imágenes de
marca para la EMD sin lista (y aquí sin ninguna imagen: la primera será la que apruebe la persona), idiomas y textos por idioma
(developer publica en `es` y `en`; las piezas solo en `es`), copia de los logos en `examples/<p>/logos/` pendiente. No le
afectan: varias variantes de logo (la baldosa vale sobre claro y oscuro; los dos lockups ya existen), `compose.lut` (paleta
83-97 %), `style.lora`.

**Hueco propio de este proyecto:** la medida de contraste por percentiles **no ve un trazo fino que cruza el texto** (r4 og,
peor 16,72 con la línea sobre el título; r5 cabecera, 15,96 con la línea tocando la última letra). Las dos veces lo vio el ojo
y se arregló cambiando la zona. Es lo que `r4-composicion.md` y `r5-piezas.md` piden para F2.9 (medir en la caja real del
texto, ampliada, y avisar de bordes fuertes); developer es el caso de prueba.

---

## Contradicciones

Entre el repo de developer (`8fa309c`) y la biblia (`a50b544`), o entre la biblia y lo que ya generó el motor.

1. **Resuelta el 2026-11-04.** **Zona reservada.** Biblia §7 decía «mitad izquierda en `og` y `social`; tercio superior en
   `square`». Los prompts pedían la mitad izquierda vacía, pero la línea de luz arrancaba «from the centre of the frame»: en r4
   cruzó el título y en r5 tocó su última letra, y las dos piezas se compusieron `abajo`. **Decisión:** `abajo 1/2` en `og`,
   `social` y `header`, `arriba 1/2` en `square` y `portrait` (criterios 2 y 3: lo compuesto y medido manda, y una sola zona por
   perfil); el prompt se reescribe para dejar libre la mitad inferior; la biblia se corrige (hecho). El fallo se debía a que el
   prompt pedía otra zona.
2. **Resuelta el 2026-11-04.** **Peso de Inter.** Biblia §3: Inter 400/600; las piezas de r4-r5 salieron a 400 con opacidad
   0,82. **Decisión:** lo compuesto manda, en toda la familia: titular 700, subtítulo Inter 400 con opacidad 0,82; la biblia se
   corrige (hecho).
3. **Resuelta por los datos; la hoja lo dice.** **Velo del `og`.** La plantilla explica «Galivelop `0` en `og`, `0.3` en el
   resto»; el `og` de developer lleva `0.55` (`piezas.json`). **Decisión:** `0.55` con la zona `abajo`; el «0 en `og`» de la
   plantilla es un ejemplo, no una regla.
4. **Resuelta el 2026-11-04.** **Palabras vetadas frente a «Nunca se muestra».** **Decisión:** `face`, `person`, `human`,
   `humanoid`, `magic`, `leaf`, `leaves`, `foliage`, `plant` y el resto de la lista de la hoja pasan a vetadas (biblia §7
   completada); «leaves the main line» → «departs from the main line» (pendiente en `prompts/` y en los pedidos `r2-control` y `r2-luz`).
5. **Resuelta el 2026-11-04.** **Formato de la biblia §8.** **Decisión:** una celda de estado por archivo, como en las otras
   biblias; la fila de `og.txt` recoge la palanca de r1 (`r1-fondos.md` l.61). Hecho.

No hay contradicción entre el repo de developer y la biblia en lo que la biblia toma de él: nombre, propósito, estado («F0
hecha, aún no ejecuta tareas»), límites, Python ≥ 3.10 solo stdlib y commit `8fa309c` coinciden. Lo único que la biblia no
recoge y el README dice es «**Todavía no hay licencia**» (l.52): va en «Promesas».

## Cambios que pediría a la plantilla

Developer encaja casi entero: es la herramienta con más voz propia en su repo y la que menos identidad visual tiene (ninguna).
Dos cosas no encajan sin forzar, y una tercera es un matiz:

1. **Comprobación 8 y «like».** Tal como está escrita («ni “like”»), un grep de palabra entera falla en los siete proyectos:
   la línea «Style: clean minimal **vector-like** digital illustration…» es un compuesto con guion, no una comparación. Las
   hojas de image-generator y Workflow dan la comprobación por pasada; esta la da «con matiz». **Pediría:** que la
   comprobación diga «“like” como palabra suelta o seguida de “a”/“an”/“the”, no precedida de guion», y que el validador lo
   implemente así (`(?<!-)\blike\b`).
2. **Comprobación 11 compara la zona declarada con la que el prompt describe.** Hoy dice «cada perfil compuesto declara su
   zona y el prompt la describe», y se da por pasada si el prompt describe *una* zona. Developer enseña el caso que se
   escapa: el prompt deja libre la mitad izquierda y la pieza se compone abajo, porque un trazo fino cruzaba el texto; dos
   rondas lo arreglaron en la composición sin tocar el prompt, y nadie lo apuntó como desajuste. **Pediría:** que la fila
   «Zona reservada» exija una sola zona por perfil para prompt, plantilla y medida, y que, si la composición acaba en otra,
   se diga por qué y se cambie el prompt en la ronda siguiente; y que la comprobación 11 compare las dos (la del campo
   `compose` cuando exista y la frase del prompt).
3. **Matiz en «Velo por perfil».** El paréntesis del nivel («Galivelop `0` en `og`, `0.3` en el resto») se lee como regla de
   familia y es un ejemplo: developer lleva `0.55` en `og`. **Pediría:** «por ejemplo, Galivelop…» o mover el ejemplo a la
   columna «Ejemplo».

Las tres filas nuevas de la hoja de Workflow sirven aquí tal cual: «Acentos en imagen» se queda en «no hay» (un solo acento),
«Otras piezas de marca» en «no hay hoy, lo habrá al actualizar el flujo», y las listas de canales con «consta / no consta en el
repo» dicen, para un repo sin web, que **nada consta**.

---

## Lo que enseñó rellenarla

**Balance de este proyecto:** 15 obligatorios (familia Galivelop); **12 completos desde un repo** (developer, Portal vía biblia
o este), **3 [P]** (acento, logo elegido como decisión delegada, titular), 0 «no hay». De los 68 campos de la plantilla (66 más
las dos filas nuevas), 15 son **[P]** en todo o en parte (acento y sus dos tonos, logo elegido, titular, subtítulo y las seis
frases de r5, pieza clara y sus valores, prohibidos de la paleta, símbolo suelto, tamaños y márgenes, usos prohibidos del logo,
monoespaciada, palabras vetadas añadidas y la hipótesis de «leaves», zona del `og`/`header`, perfiles `square`/`portrait`/
`header`, `compose`, `draft`, `icon`, el Portal como destino, el mapeo `Palette:`), 2 son «no hay» admitidos («Acentos en
imagen», «Otras piezas de marca»; la imagen de marca es «no hay» hasta que la persona apruebe una pieza) y 4 recomendados no
comprobables o sin hacer (composición por perfil, copia de logos, fuentes instaladas, EMD), los mismos que en las otras dos.

**Diferencia con image-generator y Workflow:** developer es la única marca de las tres **sin ninguna imagen publicada en ningún
sitio** (ni Portal, ni web, ni favicon): su primera imagen de marca será la que la persona apruebe de r4-r5, y hasta entonces no
hay EMD. Es también la única cuyo **prompt y cuya composición no están de acuerdo en la zona** (izquierda frente a abajo), por un
motivo que la medida no ve: un trazo fino sobre el texto. Y la única con los dos lockups (claro y oscuro) ya dibujados. En voz
va la primera: propósito, límites y campo semántico son literales del `README`, el `GLOSSARY` y las ADR; solo el lema y las
frases son propuesta, como en image-generator.
