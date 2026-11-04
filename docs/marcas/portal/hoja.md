# Hoja de estilo mínima: Portal Galivelop

**Aprobada el 2026-11-04** (decisiones delegadas por la persona; ver
[`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md)); tercer caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md)
(F2.12), rellenada tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y
[`../galivelop-workflow/hoja.md`](../galivelop-workflow/hoja.md), con su misma forma. Complementa a [`biblia.md`](biblia.md): la
biblia es la lectura larga; esta hoja es lo que `gimg` necesita, campo a campo y en el orden de la plantilla. Estados como en
[`../README.md`](../README.md): sin marca sale de un repo (ruta en la sección 13); **[P]** es propuesta del agente **aprobada por delegación**
(no la ha visto la persona), con su porqué en la misma celda; *(suposición)* se comprueba en una ronda; «no hay» solo donde la plantilla lo admite. **«Heredado
de» no aparece:** el Portal es la marca paraguas; las otras hojas heredan de esta.

Commits de referencia: Portal-Galivelop `main` `7c9a704` (2026-10-25; es lo publicado en GitHub Pages) y rama de trabajo
`ccr-47f8fddd-o5ek6p` `66ec4f1` (2026-10-27, WIP: trae el ADR 0002 y el alta de Galivelop Image Generator). El `aa76b34` que
citan la biblia y las hojas aprobadas está en esa rama de trabajo, **no en `main`**, pero entre `7c9a704` y `aa76b34` no cambia
ninguna variable de `global.css`, ni el logo, ni los textos del hero: lo que la biblia leyó es lo publicado. Este repo
`5460d2c` (`f2-motor`). El repo del Portal se ha leído **sin modificar nada**.

**Lo primero que hay que saber:** el Portal es el único proyecto de la familia con una identidad visual completa en su repo
(CSS con los dos temas, logo SVG, dos tipografías servidas, tres imágenes de marca), así que casi todo lo obligatorio sale de
un archivo con línea. Lo que no sale del repo es lo que el agente decidió por delegación tras el «no» de la persona en r1: el
**motivo** (el umbral de luz) y el **dibujo** del logo `a`. Y hay una grieta temporal: la rama de trabajo del Portal cambia la
identidad («Marca de software: taller y Productos», ADR 0002) y añade un cuarto proyecto; está sin publicar y sin confirmar por
la persona, y la hoja sigue lo publicado en `main` (decidido el 2026-11-04; ver «Contradicciones», 1).

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Galivelop»: una palabra, G mayúscula, sin guion ni espacio; Gali(cia) + Develop. En el wordmark, «Gali» en celeste y «velop» en el color del texto. «Portal Galivelop» es el nombre del repo y de la ficha en este repo, no el de la marca | Portal (`index.html` l.6 `<title>Galivelop</title>`; `README.md` l.5-9; `src/components/Logo.tsx` l.24-29; `README.md` l.38, «**Gali**cia … **Develop**») |
| Nombre en código | Obl. | `portal` | repo (`examples/portal/galivelop-images.json`, `name`) |
| Fuente de verdad | Rec. | Portal-Galivelop `main` `7c9a704` (paleta, tipografía, logo, textos, canales; publicado) y rama de trabajo `66ec4f1` (solo para las contradicciones); este repo `5460d2c` (prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio el veredicto de r1 (2026-10-26: **«no»** al orbe del Portal, con la palanca «puerta, umbral o anillo de acceso»); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa, y el 2026-11-04 delegó también las dudas de esta hoja (aprobada por delegación); el logo `a` y el umbral de r2 son decisiones delegadas y llevan **[P]** | repo (`docs/records/contenido/r1-fondos.md` l.48, l.52, l.59; `docs/marcas/README.md` l.24-30, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`, **origen de la familia**: esta hoja es la fuente de los valores que la plantilla da por rellenados con `Galivelop` (fondo `#06121c`/`#f6fafd`, texto `#eaf4fa`/`#0a1a28`, Sora 700 / Inter 400, baldosa `rx` 30/128 trazo 12). Por eso aquí fondo, texto y titular son Obl. y se citan con línea (ver «Cambios que pediría a la plantilla», 1) | Portal (`src/estilos/global.css`, `public/marca/gv-logo.svg`) |
| Hereda de | Opc. | **no hay** (es la marca paraguas) | — |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Taller independiente de software. Hacemos reales los proyectos que parecen imposibles.»: la web de la marca Galivelop, que presenta sus proyectos (Tarkor, toVeriAI, Galivelop-workflow) con su estado real, para quien quiera verlos, seguirlos o sumarse. **En la rama de trabajo del Portal** (`66ec4f1`, sin publicar) pasa a «Marca de software: taller y Productos»: «Galivelop son dos cosas: el taller… y Productos» (ver «Contradicciones», 1) | Portal `main` (`src/i18n/textos.ts` l.11-13 `hero.antetitulo`, `hero.titulo1-2`; `index.html` l.7 y l.17; `README.md` l.5-9; `AGENTS.md` l.112 «Portal público de la marca Galivelop») |
| Lema | Rec. | «Hacemos reales los proyectos que parecen imposibles» (es el título del hero en dos partes; se mantiene igual en la rama de trabajo) | Portal (`src/i18n/textos.ts` l.12-13; gl l.235-236 «Facemos reais / os proxectos que semellan imposibles»; en l.456-457; `README.md` l.9) |
| Tono | Rec. | cercano, humilde, concreto, honesto con el estado real; «Galivelop es un taller, no un escaparate»; «Lo que nos mueve no es el beneficio económico»; enseña «cada proyecto tal y como está, con sus avances y sus pendientes». No es: vendedor, corporativo, épico, «startup» | Portal (`src/i18n/textos.ts` l.59 `sobre.texto1`, l.60 `sobre.texto2` «esta web no vende: muestra cada proyecto tal y como está»; `README.md` l.34 «No es un escaparate. No nos mueve el beneficio económico») |
| Idiomas | Opc. | `es, gl, en`: toda la web va en los tres (es sin prefijo, `/gl/`, `/en/`) y el gallego es obligatorio en cada texto. Las piezas de r4-r5 van solo en `es`; `gl` y `en` de cada pieza, sin hacer | Portal (`src/main.tsx` l.12 «castellano sin prefijo, /gl/… y /en/…»; `src/i18n/textos.ts` bloques es/gl/en; `AGENTS.md` l.138 «Todo texto visible, en castellano, gallego e inglés») |
| Campo semántico | Opc. | dentro: taller, hacer real, proyecto, estado real, avances y pendientes, en abierto, a la vista, Galicia (luz y mar), relevo; fuera: escaparate, vender, cliente, encargo, de pago, beneficio, crecimiento, «startup», postal gallega | Portal (`src/i18n/textos.ts` l.59-60; `pie.hecho` l.213 «Hecho en Galicia»; `GLOSSARY.md` l.6 «Taller: … expone sus proyectos, no los vende»); «Encargo», rama de trabajo (`GLOSSARY.md` l.7 en `aa76b34`); «luz y mar» y «relevo», `biblia.md` §6 |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | «contrata nuestros servicios», venta, precios, promesas infladas, gráficas de crecimiento, gente en traje, apretones de manos, oficinas de banco de imágenes, cohetes, robots; la postal gallega (faro, bandera, gaita); nada que diga «encargo» ni «de pago» en nombre del taller (los encargos son de cada miembro, no de Galivelop) | Portal `main` (`GLOSSARY.md` l.6 «expone sus proyectos, no los vende»; `src/i18n/textos.ts` l.60 «esta web no vende»); lo de «encargo» y «de pago», rama de trabajo (`docs/adr/0001-encargos-por-miembro.md` l.1, l.22-24 «Se dice sin vender. Sin “de pago” ni distintivos» y `GLOSSARY.md` l.7 «Encargo», ya en `aa76b34`, **no en `main`**); lista visual, repo (`docs/plan.md` l.597-598; `biblia.md` §1 y §7) |
| Personas y rostros | Rec. | nunca personas, manos ni rostros; nada que sugiera a los miembros del equipo (tienen página propia con su foto, pero no son la marca) | repo (`biblia.md` §7; `docs/plan.md` l.597-598). La ausencia de personas en `galivelop-social.png` y `gv-logo-512.png` es de Portal (`tools/generar-marca.mjs`) |
| Promesas | Rec. | nada de fechas, precios ni «ya disponible»; nada de «cuatro proyectos» ni de «Productos» hasta que el Portal publique el ADR 0002; nada de LinkedIn como canal hasta que conste (sección 11); no afirmar que una herramienta del taller «está en el Portal» si no tiene ficha publicada | Portal (`docs/adr/0002-marca-taller-y-productos.md` l.4-7 «Sin publicar en main hasta que la persona lo vea y confirme», l.92 sin precios; `src/data/marca.ts` l.3-5); lo demás **[P]** (regla de esta hoja) |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Obl. | oscura (por defecto, «la de la casa») `#06121c`, alterno `#081826`; clara `#f6fafd`, alterno `#eaf4fa`. Las cinco piezas de r4-r5 son oscuras; la clara no tiene pieza hecha | Portal (`src/estilos/global.css` l.20-34 tema oscuro, l.23 `--fondo`; l.36-49 tema claro, l.38 `--fondo`; `index.html` l.8 `theme-color #06121C`) |
| Texto | Obl. | sobre oscuro `#eaf4fa` (secundario `#9fb4c4`, terciario `#6f8799`); sobre claro `#0a1a28` (secundario `#43586a`, terciario `#6b8193`) | Portal (`global.css` l.28-30 `--texto`, `--texto-2`, `--texto-3`; l.43-45 tema claro); `#eaf4fa` es el `color_texto` de las cuatro piezas de `piezas.json` |
| Acento | Obl. | celeste `#1aa6df` (`--celeste`): «Gali» del wordmark, antetítulos, resplandor del hero, luz del umbral en la imagen. Intenso `#0083c1` (`--celeste-intenso`, extremo del degradado de la baldosa); claro `#5cc8f2` (enlaces sobre oscuro, halo del resplandor en la imagen); `#006c9f` (enlaces sobre claro) | Portal (`global.css` l.4-5, l.31 `--enlace`, l.46; `Logo.tsx` l.29 `logo-gali`; `global.css` l.139 `.logo-gali`) |
| Acentos en imagen, en orden de peso y significado | Rec. | 1) celeste `#1aa6df` (la luz, lo de Galivelop: domina); 2) `#5cc8f2` (halo, siempre junto al celeste); 3) los **acentos de los proyectos, solo como tres puntos pequeños** dentro del umbral y en este orden: Tarkor `#E0703A`, toVeriAI `#2F7A55`, Galivelop-workflow `#3D6FD9`. Nunca como color dominante. En la rama de trabajo hay un cuarto, Galivelop Image Generator `#8B5CF6` (sin publicar; ver «Contradicciones», 1 y 4) | Portal `main` (`src/data/proyectos/tarkor.json`, `toveriai.json`, `galivelop-workflow.json` l.7 `acento`); orden y «tres puntos», repo (`prompts/estilo.txt`; `biblia.md` §2 l.33; `docs/plan.md` l.597; `r2-estilo.md` l.51: la variante hex fue «la única con los tres puntos de color dentro del umbral») |
| Resto de la paleta | Rec. | oscuro: superficies `#0c1d2b`, `#11283a`, borde `#1b3447`, brillo `rgb(26 166 223 / 0.22)`; claro: superficies `#ffffff`, `#f0f6fa`, borde `#d6e4ee`, brillo `rgb(26 166 223 / 0.16)`; blanco `#ffffff` (`--blanco`, trazo del monograma); baldosa `#2BB3EA → #0083c1`. `brand.palette` lleva 11: `#06121c`, `#1aa6df`, `#5cc8f2`, `#E0703A`, `#2F7A55`, `#3D6FD9`, `#ffffff` y, añadidos el 2026-11-04, `#eaf4fa` (el texto de todas las piezas), `#2BB3EA` y `#0083c1` (la baldosa) y `#9fb4c4` (texto 2); **siguen fuera** los del tema claro y el fondo alterno `#081826` (ninguna pieza los usa) | Portal (`global.css` l.1 «azul celeste y blanco de la bandera gallega», l.4-6, l.20-34, l.36-49); repo (`galivelop-images.json`, de `prompts/r2-hex.txt`) |
| Combinaciones | Rec. | oscura: `#06121c` + texto `#eaf4fa` + «Gali» `#1aa6df` + baldosa; velo `#06121c:0` en `og` (contraste sobra, 17,04) y `#06121c:0.3` en `cuadrado`, `vertical` y `cabecera`; sobre imagen: el logo siempre en su baldosa, texto solo en la zona reservada oscura, nunca celeste sobre celeste ni sobre la baldosa. Clara **[P]**: `#f6fafd` + `#0a1a28` + «Gali» `#1aa6df` + baldosa; sin pieza hecha | repo (`piezas.json` `velo`, `color_texto`; `r4-composicion.md` l.16); clara, `biblia.md` §2 l.39 |
| Prohibidos | Rec. | cualquier color fuera de la tabla; los acentos de proyecto como color dominante o en el texto; celeste sobre el degradado de la baldosa (no contrasta); negro `#000`; sombras y brillos sobre el logo; degradados que no sean la baldosa, el resplandor radial o el título destacado de la web | Portal, en parte (`global.css` l.511 `.destacado`: el único degradado de texto de la web; `.hero-fondo` l.478-492: el único resplandor); el resto **[P]** (`biblia.md` §2 l.43-44, escrito por el agente; ninguna pieza lo ha puesto a prueba) |
| Degradados | Opc. | la baldosa del logo (`#2BB3EA → #0083C1`, diagonal), el resplandor radial celeste del fondo (`radial-gradient` al 85 % 30 % y al 10 % 90 %) y, en la web, el título destacado (`linear-gradient(120deg, celeste, texto)`) | Portal (`public/marca/gv-logo.svg`; `global.css` l.478-492, l.511) |

**Medido:** la calibración da a este proyecto paleta ≥ 70 %: imágenes de marca 82 y 80 %, r1 65-77 %, r2 hex 73,5 %, r5 70-82 %; r4
`og` compuesto 66,95 % (`docs/records/contenido/calibracion-measure.md` l.27-30 y l.68; `r2-estilo.md` l.33; `r4-composicion.md` l.16;
`r5-piezas.md` l.30). Es el único proyecto en que **hex ganó a palabras y material** aunque palabras diera más paleta (86,4 %): hex fue
«la única con los tres puntos de color dentro del umbral, como pide la biblia» (`r2-estilo.md` l.33-35, l.51). FLUX.3 se probó aquí
y perdió: SATAVG 7 frente a 14 y paleta 61 % frente a 71 % (`r3-borrador.md` l.37-38).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | **Publicado:** `public/marca/gv-logo.svg` del Portal (copia literal en `docs/marcas/portal/logos/portal-actual.svg`): baldosa 128×128 `rx` 30 con degradado `#2BB3EA → #0083C1`, monograma G+V en dos trazos blancos de 12 con remates redondos; también `favicon` y `apple-touch-icon` (`gv-logo-512.png`). **Para las piezas:** `docs/marcas/portal/logos/portal-a.svg`, la misma baldosa con la G y la V en **un solo trazo** (`M50 64 H66 A24 24 0 1 1 42 40 H72 L90 88 L108 40`). Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; colores `#2BB3EA`, `#0083C1`, `#FFFFFF` | Portal (`public/marca/gv-logo.svg`; `src/components/Logo.tsx` l.15; `index.html` l.10-11; `docs/desarrollo.md` l.32-33). El `a` es **[P]**: lo eligió el agente por delegación («el logo de hoy simplificado, sin ruptura con lo publicado», alternativa `b`), es la única pieza de la familia que **sustituye un logo publicado** y el Portal no sabe de él (`docs/marcas/README.md` l.13, l.30; `biblia.md` §4 l.73) |
| Lockup (símbolo + nombre) | Rec. | `logos/portal-a-lockup.svg` (`viewBox 0 0 470 128`, `data-fondo="oscuro"`): símbolo a la izquierda, «Gali**velop**» en Sora 700, 64/128 de alto, `letter-spacing` −1,9 (≈ −0,03 em), «Gali» `#1AA6DF` y «velop» `#EAF4FA`, separación 24/128 (`x=152`, ≈ 0,19 del alto: **aprobada**, ver «Contradicciones», 7). Es el wordmark de la web pasado a archivo: en el Portal es HTML (`.logo-texto` Sora 700, 1,3 rem, −0,03 em; `.logo-gali` celeste), no existe exportado. Lleva `<text>` con `font-family="Sora, sans-serif"`, que la plantilla admite mientras `compose.fonts` garantice la fuente; el paso a trazos queda Opc. | repo (archivo, `b7f1baf`); medidas de Portal (`Logo.tsx` l.24-29; `global.css` l.131-139). La separación 24/128 **no** era el «cuarto del lado» (32/128) de la biblia §4; la biblia se corrige (ver «Contradicciones», 7) |
| Variante clara y oscura | Rec. | la baldosa lleva su propio fondo y vale sobre los dos; el wordmark cambia solo «velop»: `#eaf4fa` sobre oscuro (único archivo que existe) y `#0a1a28` sobre claro (sin archivo). El Portal publica solo la oscura (la web clara usa el mismo `Logo.tsx`, con «velop» en `--texto` del tema) | Portal (`Logo.tsx`; `global.css` l.131-139: el color sale del tema); archivo claro **[P]** (`biblia.md` §4 l.77; nadie lo ha dibujado) |
| Tamaño mínimo y margen | Rec. | símbolo 16 px (el favicon lo prueba a 16 y 32); wordmark 20 px de alto, por debajo solo el símbolo; margen libre un cuarto del lado de la baldosa; símbolo y wordmark en horizontal, separación un cuarto del lado; nunca el wordmark sobre la baldosa | Portal, solo el 16 px (`index.html` l.10 favicon SVG); el resto **[P]** (`biblia.md` §4 l.78-81, reglas escritas por el agente al elegir) |
| Usos prohibidos | Opc. | cambiar el degradado, quitar el radio, estirar, girar, trazo de otro grosor, sombras o 3D, colores de proyecto en el monograma, el símbolo suelto sobre la ilustración. **El propio Portal lo rompe** en `galivelop-social.png` (`drop-shadow` sobre el logo; ver «Contradicciones», 2) | **[P]** (`biblia.md` §4 l.82-83); la sombra, Portal (`tools/generar-marca.mjs` l.20 `drop-shadow`) |
| Logo fuera de la paleta | Opc. | `#2BB3EA` y `#0083C1` (la baldosa) están en el SVG y, desde el 2026-11-04, también en `brand.palette`. `#0083c1` es `--celeste-intenso` de la web; `#2BB3EA` solo existe en el logo. Trazo del monograma: `#EAF4FA` como valor de referencia y el Portal publica `#fff` (ver «Contradicciones», 9) | Portal (`global.css` l.5; `gv-logo.svg`); repo (diferencia con `galivelop-images.json`) |

Copia en `examples/portal/logos/`: **no hay** (F2.10, dec. 3, pendiente); `piezas.json` apunta hoy a `docs/marcas/portal/logos/`.
El lockup del Portal (470×128) es el más compacto de los siete: en r4 ya salía a 57 px, el 9 % del alto del `og`, y fue la medida
que el piloto adoptó para todas las marcas («lo que ya tenía portal», `r4-composicion.md` l.31-32). `portal-b`-`d` y sus lockups
siguen en la carpeta como propuestas.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Obl. | Sora 700 (reserva `'Sora Variable', 'Sora', system-ui, sans-serif`), títulos h1-h3 con `letter-spacing` −0,02 em; el wordmark −0,03 em. Peso de titular **700 aprobado** (decisión 4 del 2026-11-04, la misma regla en toda la familia). Es lo que `piezas.json` declara (`fuente: Sora`) y lo que compuso r4-r5 con `peso_titulo=700` | Portal (`global.css` l.8 `--fuente-titulos`, l.78-83 h1-h3, l.131-135 `.logo-texto`; `src/main.tsx` l.1-2 importa `@fontsource-variable/sora`); repo (`piezas.json`; `examples/pilot/componer.py` l.119) |
| Familia de texto | Obl. (origen de la familia) | Inter 400 (reserva `'Inter Variable', 'Inter', system-ui, sans-serif`); en la web 500-600 en etiquetas y antetítulos. Subtítulo **Inter 400 con opacidad 0,82, aprobado** (decisión 4 del 2026-11-04; es lo que salió en r4-r5) | Portal (`global.css` l.9 `--fuente-texto`, l.375-381 `.antetitulo` 600; `src/main.tsx` l.1-2 `@fontsource-variable/inter`); repo (`piezas.json` `fuente_texto`; `componer.py` l.159-160) |
| Licencia y archivo | Rec. | Sora e Inter, OFL; el Portal las sirve él mismo desde `@fontsource-variable/sora` y `@fontsource-variable/inter` `^5.3.0` (no de Google Fonts). En este repo, `examples/pilot/fuentes.sh` las baja de `google/fonts` a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`; no instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)* | Portal (`package.json` l.15-16; `docs/desarrollo.md` l.36 «servidas desde el propio sitio»); repo (`examples/pilot/fuentes.sh` l.8-12) |
| Tracking y mayúsculas | Opc. | títulos −0,02 em; wordmark −0,03 em; antetítulos y etiquetas en mayúsculas Inter 600 con tracking 0,16 em en celeste (también 0,04-0,14 em en otras etiquetas); el nombre siempre «Galivelop» en una palabra, nunca en mayúsculas sostenidas ni partido. Chips con radio 999 px | Portal (`global.css` l.78-83, l.131-135, l.375-381 `.antetitulo`, l.201+ chips) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | 1) un **umbral** alto y abierto, de esquinas suaves, en la oscuridad, por el que entra luz celeste `#1aa6df` que se derrama por un suelo liso en ondas suaves y sube en un resplandor radial `#5cc8f2` (el portal, el taller con la puerta abierta); 2) **tres puntos pequeños de luz** dentro del umbral, `#E0703A`, `#2F7A55`, `#3D6FD9` (los proyectos); 3) **rejilla tenue de puntos** que cubre el fondo y se funde en la oscuridad (así es la web: `.hero-fondo` con `background-size: 26px 26px`); 4) fondo `#06121c` con resplandor radial celeste. Sin usar aún, de la biblia: ola de luz, anillo de acceso, Galicia solo como luz y mar | el fondo con resplandor y rejilla es de Portal (`global.css` l.478-492); el **umbral es [P]**: lo eligió el agente en r2 por delegación tras el «no» de la persona al orbe de r1 (`r1-fondos.md` l.48, l.52, l.59 «puerta, umbral o anillo de acceso»; `r2-estilo.md` l.51), y ninguna pieza del Portal lleva aún un «sí» de la persona. Prompts: `prompts/estilo.txt`, `r5-*.txt`; `biblia.md` §7 |
| Motivos No | Obl. | gente en traje, apretones de manos, oficinas de banco de imágenes, cohetes, robots, gráficas de crecimiento, postal gallega (faro, bandera, gaita), orbes y esferas genéricos (r1: «limpio pero genérico, no dice portal»), texto, logos; nada que sugiera venta ni «contrata» | repo (`biblia.md` §7; `docs/plan.md` l.597-598; `r1-fondos.md` l.48); la raíz del veto a la venta, Portal (`GLOSSARY.md`; ADR 0001) |
| Palabras vetadas | Obl. | `lighthouse`, `flag`, `handshake`, `rocket`, `robot`, `suit`, `office`, `chart`, `logo`, `text`, `letters`; más `like` y cualquier lugar real (reglas comunes). Añadidas **[P]** (aprobadas por delegación): `orb`, `sphere`, `globe` (lo que pintó r1), `bagpipe` (la postal), `person`, `people`, `human`, `hand` (nunca personas), `graph`, `arrow`, `coin`, `money` (crecimiento y venta), `sun` (pinta el disco). **Ningún prompt ni pedido de `examples/portal/` contiene ninguna de las dos listas, ni `no`/`not`/`without`/`never`/`like`** (grep sobre `prompts/*.txt` y `orders/*.json`, 2026-11-04) | repo (`biblia.md` §7 l.112-113); las trece añadidas **[P]**, aprobadas por delegación (cierran lo que «Nunca se muestra» y «Motivos No» nombran, como pide la plantilla; `sun` por la pauta de Tarkor en `docs/plan.md` l.588-590) |
| Estilo de imagen | Rec. | «minimal» y «nearly empty» **rechazados** (r4: ninguna publicable). Desde r6: «Style: elegant digital art, physically based rendering, soft volumetric light, crisp reflections, smooth gradients, fine material detail. Colours: #06121c, #1aa6df, #5cc8f2, … and #ffffff highlights. Mood: honest, quietly ambitious, inviting.» Los colores van en hex, no en palabras: hex fue la variante elegida en r2. **r7 (2026-11-04, tras el 7/10 de r6):** el marco del umbral pasa a mármol blanco pulido con vetas grises, filo achaflanado de acero cepillado y una junta continua de luz por dentro; por el hueco entra una **aurora** (cortinas de turquesa `#1aa6df`/`#5cc8f2`, verde `#2F7A55` y violeta `#3D6FD9`) que se refleja en un suelo de agua quieta en vetas largas y ondas concéntricas; los tres puntos siguen (`orders/r7.json`) **r8 (veredicto de r7, 4/10, 2026-11-05):** demasiado contraste de color; la aurora **no** va dentro del portal como cortina: sale del portal como humo o estela de colores (como el humo de image-gen), se expande por la escena y se refleja en el fondo y sobre la puerta, con colores suaves. El portal, de mármol blanco pulido muy detallado, de época moderna y futurista, con detalles simétricos (molduras, incrustaciones de luz, geometría limpia). | repo (`prompts/estilo.txt` = `r2-hex.txt`, elegido en r2, `r2-estilo.md` l.51) |
| Lenguaje de forma | Opc. | un trazo continuo, círculos y rectas, sin relleno ni detalle fino; trazo 12/128 (9,4 % del lado) con remates y uniones redondos; `rx` 30/128 (23 %) en la baldosa; radios 18 px (`--radio`), 10 px (`--radio-sm`), 6 px en piezas pequeñas, píldora 999 px en chips; la luz como resplandor radial, nunca como destello dibujado; esquinas suaves también en el umbral («softly rounded corners») | Portal (`gv-logo.svg`; `global.css` l.11-12, l.103, l.201+); «un trazo» y «nunca destello», **[P]** (`biblia.md` §5 l.86-92) |

Prompts del proyecto (`examples/portal/prompts/`): `estilo.txt` (= `r2-hex.txt`, 148 palabras; elegido en r2 por el agente),
`og.txt` (r1, 125; el orbe, «no» de la persona: superado, se conserva como historia), `r2-palabras.txt` (143) y `r2-material.txt`
(163) (descartados), `r2-luz.txt` (208, sin veredicto), `r5-cuadrado.txt` (158), `r5-vertical.txt` (159), `r5-cabecera.txt` (161)
(compuestos y medidos). Todos de 125-208 palabras, dentro del rango 120-320; todos acaban en «The image is completely textless.».
Pedidos: `orders/r1-og.json` (`og.txt`, semilla 3, dos imágenes), `r2-control.json` (`estilo.txt`, semilla 7), `r2-luz.json` (semilla 3).

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | la luz sale del umbral, a la derecha, y se derrama hacia el centro y el suelo; la mitad izquierda queda en penumbra. En `r2-luz.txt`: «the only light comes from the right», el umbral «centred a quarter of the way in from the right edge», y «The left half, from the left edge to the middle» en sombra. Nunca se nombra la fuente (ni «sun» ni lámpara): la luz «pours out through» el umbral | repo (`prompts/estilo.txt`, `r5-*.txt`); la variante *(suposición: r2-luz sin veredicto)* |
| Momento y clima | Rec. | escena nocturna, dicha al principio: «Wide abstract banner on a background in the colour #06121c…» (`estilo.txt`) o «Dark wide abstract banner: the whole frame is a deep dark surface…» (`r2-luz.txt`); sin clima (interior abstracto, suelo liso con ondas) | repo (`prompts/estilo.txt`; `orders/r2-luz.json`) |
| Luminosidad objetivo (YAVG) | Rec. | 45-65 (imágenes de marca 52 y 47; r1 59-63; r2 hex 56,9; r4 og 64,85; r5 53-62). La más clara de las marcas oscuras: el umbral ilumina medio cuadro | repo (`calibracion-measure.md` l.27-30, l.68; `r2-estilo.md` l.33; `r4-composicion.md` l.16) |
| Saturación objetivo (SATAVG) | Rec. | 13-19 (marca 15 y 17; r1 17-18; r2 hex 15,6; r4 og 14,4; r5 14-16) | repo (`calibracion-measure.md` l.27-30, l.68) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **publicada dónde:** `public/marca/galivelop-portal.jpg` 1200×630, el og:image de todas las páginas (**consta en el repo**: `index.html` l.19, `scripts/paginas-estaticas.mjs` l.10) y «captura de la portada» (`index.html` l.13), no arte; `public/marca/galivelop-social.png` 1200×630, social preview de GitHub (**consta** el archivo y su generador, `tools/generar-marca.mjs`; que GitHub lo use no se lee desde el repo); `public/marca/gv-logo-512.png`, apple-touch-icon y `logo` del `Organization` de JSON-LD (**consta**: `index.html` l.11; `paginas-estaticas.mjs` l.72). Portadas de los proyectos en `public/proyectos/<p>/portada.webp` (1600×640 Tarkor, 1600×1000 workflow, 1440×900 toVeriAI): son de cada proyecto, no del Portal. **Vale como referencia:** la calibración midió `galivelop-portal.jpg` (YAVG 52, SATAVG 15, paleta 82 %) y `galivelop-social.png` (47, 17, 80 %) y sacó de ahí los umbrales del Portal, pero la primera es una captura de la interfaz y la segunda la hace un script con otra tipografía (ver «Contradicciones», 2 y 3): **Decidido el 2026-11-04:** `galivelop-portal.jpg` solo calibra la medida (no es arte de marca) y `galivelop-social.png` es pieza heredada que este sistema sustituye (ver «Contradicciones», 2 y 3) | Portal (`index.html` l.13 «Imagen: captura de la portada», l.19, l.22; `docs/desarrollo.md` l.37-38, l.42; `tools/generar-marca.mjs` l.16-23); repo (`calibracion-measure.md` l.9, l.27-28, l.84-85) |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración (2026-11-04): `og` 1280×640 → 1200×630, `social` 1280×640 → 1200×630 (el tamaño del archivo que publica el Portal, que este sistema sustituye), `square` 1024×1024 → 1080×1080 (`cuadrado`), `portrait` 896×1152 → 1080×1350 (`vertical`), `header` 1536×512 → 1500×500 (`cabecera`, formato de X). **Sin perfil `banner`:** el 1600×640 salía de la configuración del Portal y no tiene respaldo en su biblia (ver «Contradicciones», 8). Discord 960×540 y LinkedIn 1584×396 (la biblia los pedía) no se han generado ni declarado: LinkedIn, hasta que la persona confirme el canal. Hecho sin modelo: `avatar` 512×512 | repo (`galivelop-images.json`; `piezas.json`); `square` y `portrait` **[P]**, aprobados por delegación (los hizo r5 sin que el Portal tenga Instagram ni X; el Portal publica solo en Discord y GitHub, sección 11) |
| Zona reservada | Obl. | `og`, `social`: `izquierda 1/2` («The left half of the frame is a calm, smooth surface in #06121c, nearly empty and softly out of focus»); `square`, `portrait`: `arriba 1/2` («The upper half of the frame is a calm, smooth surface»); `header`: `izquierda 2/3` («The left two thirds of the frame are a calm, smooth surface»). **Aprobada la zona del compositor** (`caja_zona`): izquierda 55 % del ancho menos margen, o arriba 48 % del alto, margen 6 % del lado menor. En píxeles: `og`/`social` 1200×630 → desde r7 caja `data-caja` de la plantilla `60,60,604,510` (margen 60, columna 604; logo a 52-54 px de alto, titular en dos líneas, filete corto en el acento y subtítulo en dos líneas; r7); hasta r6, caja `38,38,622,554`; `square` 1080×1080 → `65,65,950,453`; `header` 1500×500 → `30,30,795,440`. **Desajuste conocido:** la caja de `og`/`social` llega a x=664 (r7; antes 660), unos 60 px más allá de la mitad que pide el prompt (el contraste medido en esa caja fue 15-17:1, así que no falla); alinear prompt y caja al portar a `compose` queda para el piloto, sin tocar los prompts de rondas pasadas | repo (`prompts/estilo.txt`, `r5-*.txt`; `examples/pilot/componer.py` `caja_zona` l.105-115). La biblia decía «la mitad o el tercio izquierdo» sin perfil: se corrige a una zona por perfil (ver «Contradicciones», 6) |
| Velo por perfil | Rec. | `og` `#06121c:0`; `cuadrado`, `vertical` y `cabecera` `#06121c:0.3` | repo (`piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza (57 px en el `og`), en lo alto de la caja de la zona con el título debajo, margen 6 %; solo baja si no cabe a lo ancho de la columna. El Portal fue la referencia de esa medida | repo (`componer.py` l.129-137; `r4-composicion.md` l.31-32) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo, lockup al 9 %, título Sora 700, subtítulo Inter 400). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `portal-a.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. El Portal ya publica `gv-logo-512.png` con el logo **actual**: el avatar `a` lo sustituiría (ver Símbolo SVG). `icon` 180/192/512: el Portal usa el SVG como favicon y `gv-logo-512.png` como apple-touch-icon; no hay 180 ni 192 ni manifest | repo (`piezas.json`); Portal (`index.html` l.10-11; `docs/desarrollo.md`: `tools/generar-marca.mjs` regenera `gv-logo-512.png`); `icon` **[P]** |
| Borrador | Opc. | r3 midió 640×320 a 4 pasos: YAVG/SATAVG/paleta 51/24/74 % frente a 59/14/71 % del definitivo, con el umbral que «gira y gana el charco» entre borrador y definitivo (el borrador anticipa la zona y el estilo, no el detalle). `draft: {scale: 0.5, steps: 4}` declarado en `og` (2026-11-04) | **[P]**, aprobado por delegación (F2.10, dec. 7; `r3-borrador.md` l.46, l.63-65) |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia en r2 con solo decirlo), sin LUT (paleta 70-82 %), sin conversión final por parte de `gimg`. FLUX.3 probado y descartado para este proyecto | repo (`r2-estilo.md` l.51; `r3-borrador.md` l.37-38; `r5-piezas.md`) |
| Prioridad | Rec. | la de la biblia: 1) og:image por proyecto (3 piezas 1200×630: portada del proyecto + logo + wordmark); 2) `avatar` 512 y cabecera de Discord 960×540 (solo composición); 3) `banner` 1600×640 de las cinco líneas de trabajo (IA local y responsable, mundos que viven solos, información verificable, del prototipo al producto, método con IA): **sin perfil y sin hacer** hasta que el Portal tenga dónde ponerlos; 4) logo para fondo claro y wordmark exportado; 5) cabecera de LinkedIn 1584×396. Hechas en el piloto: `og` (del Portal, no por proyecto), `avatar`, `cuadrado`, `vertical`, `cabecera` 1500×500 (formato de X, que el Portal no tiene); **sin hacer: 1), la cabecera de Discord, los `banner`, el logo claro y LinkedIn** | repo (`biblia.md` §9 l.138-141; `docs/plan.md` l.602-606); las cinco líneas, Portal (`src/data/lineas.ts` l.1; `textos.ts` l.142-150 `linea.*.titulo`) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | «Un taller, no un escaparate.» (28 caracteres), en `og` | repo (`piezas.json`, r4); recorta la frase literal de la web «Galivelop es un taller, no un escaparate» (Portal, `src/i18n/textos.ts` l.59 `sobre.texto1`; `README.md` l.34) |
| Subtítulo | Rec. | «Hacemos reales los proyectos que parecen imposibles.» (52): el lema literal con punto final | repo (`piezas.json`, r4); Portal (`textos.ts` l.12-13) |
| Variaciones, ganchos y cierres | Rec. | usados en r5: `cuadrado` «Esto es lo que hay hoy.» / «Proyectos con sus avances y sus pendientes.»; `vertical` «Tres proyectos, un mismo taller.» / «Tarkor, toVeriAI y Galivelop-workflow, con su estado real.»; `cabecera` «Software hecho en Galicia, en abierto.» / «Galivelop. Un taller independiente.». Sin usar: «Mira el estado real en galivelop.». **Dos de ellos caducan si el Portal publica el ADR 0002:** «Un taller independiente.» y «Tres proyectos» (ver «Contradicciones», 1) | «con sus avances y sus pendientes» y «Hecho en Galicia» son literales de Portal (`textos.ts` l.60 `sobre.texto2`, l.213 `pie.hecho`); «Un taller independiente» es el antetítulo del hero (l.11). El resto **[P]** (`biblia.md` §6 l.98-102; `piezas.json`) |
| Longitud máxima por campo | Rec. | la fija la composición: `componer.py` baja el cuerpo hasta 16 px y falla si el texto no cabe en la zona. Orientativo: titular ≤ 40 (los de r4-r5 van de 23 a 38), subtítulo ≤ 70 (el más largo, 59) | repo (`examples/pilot/componer.py` l.138-149; `piezas.json`) |
| Wordmark compuesto como texto | Opc. | el nombre va en el lockup («Gali» `#1AA6DF` + «velop» `#EAF4FA`, Sora 700, −0,03 em), nunca como `text` del pedido. En la web es texto HTML con las mismas reglas; en `galivelop-social.png` el Portal lo pinta con `system-ui` 800 y tracking −4 px (ver «Contradicciones», 2) | Portal (`Logo.tsx` l.24-29; `global.css` l.131-139; `tools/generar-marca.mjs` l.19, l.22) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` | repo (`galivelop-images.json` `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto, escrito explícito) | repo (`delivery.template`) |
| Dónde se publica cada pieza | Rec. | `og` → `public/marca/galivelop-portal.jpg` del Portal, og:image de todas las páginas (**consta en el repo**; hoy es una captura); `social` → `public/marca/galivelop-social.png` (**consta** el archivo; su uso como social preview de GitHub lo fija la interfaz de GitHub, no comprobable desde el repo); `avatar` → `gv-logo-512.png` (apple-touch-icon y JSON-LD, **consta**), GitHub y Discord (**no consta**: solo el enlace de invitación `discord.gg/8vyjW3VrN`); `banner` → no hay destino (el Portal no tiene portada propia; solo la de Tarkor mide 1600×640); `header` Discord 960×540 (**no consta**); LinkedIn: **no consta en el repo** (el Portal no lo tiene en `marca.ts`, solo lo nombra un comentario de `index.html` l.12 y el `og:image` sirve de vista previa allí); su cabecera 1584×396 no se hace hasta que la persona confirme el canal; `square`, `portrait`, X: **no consta** y la biblia dice «no hay Instagram, X ni YouTube» | Portal (`index.html` l.10-13, l.19, l.23; `src/data/marca.ts` l.3-5: correo, GitHub, Discord; `scripts/paginas-estaticas.mjs` l.10, l.72); `biblia.md` §9 l.143 |
| Otras piezas de marca que hace otro sistema | Rec. | **`tools/generar-marca.mjs` del Portal**: regenera `gv-logo-512.png` y `galivelop-social.png` (1200×630) con **su propia tipografía y efectos**: `font-family: system-ui`, peso 800, `letter-spacing` −4 px, «Gali» `#1aa6df`, subtítulo «Taller de creación, investigación y aprendizaje» en `#9fb4c4`, resplandor `rgba(26,166,223,.35)` sobre `#06121c`, `drop-shadow` sobre el logo. Toma los hex de la paleta pero no la fuente ni las reglas del logo. **`scripts/paginas-estaticas.mjs`**: pone el og:image por página con `?v=hash`. En este repo, además, `examples/pilot/componer.py` (composición). Ningún `gw-media-content` (el Portal no tiene nota de redes) | Portal (`tools/generar-marca.mjs` l.16-23; `docs/desarrollo.md` l.37-43; `scripts/paginas-estaticas.mjs` l.10) |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto, no declarado) | repo (esquema) |
| Conversión final | Opc. | `og` a `.jpg` 1200×630 si sustituye a `galivelop-portal.jpg` *(suposición: el nombre y la extensión los fija `index.html` y `paginas-estaticas.mjs`, que se cambiarían a la vez)*; `social` `.png` 1200×630 | Portal (`index.html` l.19; `public/marca/`; `public/proyectos/tarkor/portada.webp`) |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona: r1 **«no»** (2026-10-26, «Orbe celeste con puntos de colores: limpio pero genérico, no dice portal»; palanca: puerta, umbral o anillo); r2-r5 delegado al agente (umbral elegido en r2, hex). **Ninguna pieza del Portal tiene aún un «sí» de la persona** (la hoja está aprobada por delegación, las piezas no). Apuntado en `docs/records/contenido/r1-fondos.md` l.48, l.52, l.59, `r2-estilo.md` l.51 (elegida hex), `r4-composicion.md` l.16, `r5-piezas.md` l.30 | repo |
| Contraste del texto | Rec. | ≥ 4,5:1 (por defecto); medido: og r4 17,04 (peor 15,78) sin velo; r5 cuadrado 15,07 (14,17), vertical 14,54 (**peor 10,98**: «el haz del umbral sube hasta la zona»), cabecera 15,69 (15,29) con velo 0,3. Todas sobre el 7:1 de AAA; el vertical es el peor contraste de las marcas oscuras | repo (`r4-composicion.md` l.16; `r5-piezas.md` l.30, l.58) |
| Umbrales de medida | Rec. | los de las secciones 3 y 7: paleta ≥ 70 %, YAVG 45-65, SATAVG 13-19 | repo (`calibracion-measure.md` l.68) |
| EMD frente a la marca | Opc. | Cb ≤ 6 / Cr ≤ 7,5 (los de Tarkor, que el Portal cumple: r5 Cb 4,3-5,4, Cr 5,8-6,9; r1 llegaba a Cr 9). La referencia es `galivelop-portal.jpg`, que es una captura: si la persona no la da por marca, la EMD del Portal queda sin referencia hasta que haya una pieza aceptada | repo (`calibracion-measure.md` l.29-30, l.56, l.68) *(suposición: la referencia, sección 8)* |
| Cuándo se da por bueno el estilo | Opc. | pendiente: el Portal es, con Tarkor, el proyecto que recibió «no» en r1; el umbral de r2 «se reconoce en los tres formatos» (r5) pero no ha pasado por la persona. Regla propuesta: «sí» de la persona al `og` de r4 (o al `estilo.txt`) y a una de las tres piezas de r5; hasta entonces nada del Portal es definitivo | **[P]** (`r1-fondos.md` l.52, l.66; `r5-piezas.md` l.50) |

## 13. Fuentes de verdad

**Portal-Galivelop**, `main` `7c9a704` (publicado; leído solo, nada modificado). Entre `7c9a704` y el `aa76b34` de la biblia no
cambia ninguna variable de `global.css`, ni `Logo.tsx`, ni `gv-logo.svg`, ni los textos del hero. Números de línea de
`textos.ts` según `main`.

- `index.html` l.6 (`<title>Galivelop</title>`), l.7 (`description`), l.8 (`theme-color #06121C`), l.10-11 (favicon SVG,
  `apple-touch-icon` `gv-logo-512.png`), l.12-13 (comentario «Vista previa al compartir (X, WhatsApp, LinkedIn…) … Imagen:
  captura de la portada»), l.17 (`og:title` «Galivelop · Taller independiente de software»), l.19-21 (`og:image`
  `marca/galivelop-portal.jpg`, 1200×630), l.22 (`alt` «Portada de Galivelop: «Hacemos reales los proyectos que parecen
  imposibles», con Tarkor y toVeriAI»), l.23 (`twitter:card summary_large_image`).
- `src/estilos/global.css` l.1 («azul celeste y blanco de la bandera gallega»), l.4-6 (`--celeste`, `--celeste-intenso`,
  `--blanco`), l.8-9 (fuentes), l.11-12 (radios), l.20-34 (tema oscuro: l.23 `--fondo`, l.28-31 textos y enlace, l.33
  `--brillo`), l.36-49 (tema claro: l.38, l.43-46, l.48), l.78-83 (h1-h3 Sora −0,02 em), l.103 (6 px), l.131-139
  (`.logo-texto` −0,03 em, `.logo-gali`), l.201+ (chips 999 px), l.375-381 (`.antetitulo` 600, 0,16 em, mayúsculas,
  celeste), l.478-492 (`.hero-fondo`: resplandor radial y rejilla de puntos 26 px), l.511 (`.destacado`).
- `src/components/Logo.tsx` l.15 (`stroke="#fff"`, `strokeWidth 12`), l.24-29 (`Logo`: símbolo + «Gali**velop**»);
  `public/marca/gv-logo.svg` (`<title>Galivelop</title>`, degradado `#2BB3EA → #0083C1`, `rx` 30, trazo `#FFFFFF` 12);
  `public/marca/gv-logo-512.png` (512 RGBA), `galivelop-portal.jpg` (1200×630 JPEG), `galivelop-social.png` (1200×630 PNG).
- `src/i18n/textos.ts` l.11-13 (`hero.antetitulo`, `hero.titulo1-2`), l.59-60 (`sobre.texto1`, `sobre.texto2`),
  l.142-150 (títulos de las líneas), l.213 (`pie.hecho`); gl l.234-236, l.282, l.436; en l.455-457, l.503, l.657.
  `src/main.tsx` l.1-2 (fontsource), l.12 (rutas: castellano sin prefijo, `/gl/`, `/en/`).
- `src/data/marca.ts` l.3-5 (correo, GitHub `github.com/Zeldris`, Discord `discord.gg/8vyjW3VrN`; **sin LinkedIn**).
- `src/data/proyectos/tarkor.json`, `toveriai.json`, `galivelop-workflow.json` l.7 (`acento`: `#E0703A`, `#2F7A55`,
  `#3D6FD9`); `src/data/lineas.ts` l.1 (las cinco líneas).
- `README.md` l.1-9 (logo, «Taller independiente de software», lema), l.15-17 (Discord y correo), l.21 (Galego/English),
  l.26 (`galivelop-social.png`), l.34 («No es un escaparate. No nos mueve el beneficio económico»), l.38 (Gali + Develop).
- `GLOSSARY.md` l.6 («Taller: … expone sus proyectos, no los vende»); `AGENTS.md` l.112, l.138. **No están en `main`:**
  `docs/adr/0001-encargos-por-miembro.md` ni la entrada «Encargo» del glosario (ver el bloque de la rama de trabajo).
- `docs/desarrollo.md` l.30-43 («Marca»: logo, colores «de la bandera gallega, sin su composición», Sora e Inter «servidas
  desde el propio sitio», `galivelop-portal.jpg` «captura de la portada», `paginas-estaticas.mjs`, `generar-marca.mjs`).
- `package.json` l.15-16 (`@fontsource-variable/inter`, `@fontsource-variable/sora` `^5.3.0`); `scripts/paginas-estaticas.mjs`
  l.10 (`IMAGEN`), l.72 (`Organization.logo`); `tools/generar-marca.mjs` l.16-23 (1200×630, `system-ui`, 800, −4 px,
  `drop-shadow`, subtítulo propio; idéntico en `main` y en `66ec4f1`).
- `public/proyectos/tarkor/portada.webp` 1600×640, `galivelop-workflow/portada.webp` 1600×1000, `toveriai/portada.webp`
  1440×900.

**Portal-Galivelop**, rama de trabajo `ccr-47f8fddd-o5ek6p` `66ec4f1` (WIP, sin publicar; incluye `aa76b34`):
`docs/adr/0001-encargos-por-miembro.md` l.1, l.22-24 (añadido en `94fb94f` «sin publicar»; ya en `aa76b34`) y `GLOSSARY.md`
l.7 «Encargo» (la fuente de «ni encargo ni de pago» de la biblia §1); `docs/adr/0002-marca-taller-y-productos.md` (2026-10-27, «aceptada» en el ADR; l.4-7 «Sin publicar en main hasta que la
persona lo vea y confirme»; l.56 es/gl/en; l.92 sin precios), `src/i18n/textos.ts` l.11-15 (nuevo hero «Marca de software:
taller y Productos», «Galivelop son dos cosas…»), l.310 («Aquí no se vende: se crea, se investiga y se aprende a la vista»),
`index.html` l.7 y l.17 (nuevo `og:title` «Galivelop · Marca de software: taller y Productos»), `GLOSSARY.md` l.6-20 (Marca,
Taller, Productos, Producto, Integrante promocionado, Encargo), `README.md` l.5-9 y l.44-47 (cuatro proyectos),
`src/components/Idioma.tsx` l.10-16 (selector de idioma, nuevo),
`src/data/proyectos/galivelop-image-generator.json` l.7 (`#8B5CF6`), `src/data/productos/*.json` l.5 (acentos de producto:
image-generator `#7C5CD6`, developer `#0E9A93`, voice-generator `#C9467A`, workflow `#1AA6DF`),
`public/proyectos/galivelop-image-generator/portada.webp` 1600×1000.

**Este repo**, `f2-motor` `5460d2c`:

- `examples/portal/galivelop-images.json` (`name`, `brand.palette` de 7 hex, `delivery`, perfiles `og`, `social`, `banner`,
  `header`; último cambio `b65bd81`).
- `examples/portal/piezas.json` (fuentes Sora/Inter, textos, zona, color de texto y velo de las cuatro piezas, ruta del
  lockup y del avatar).
- `examples/portal/prompts/estilo.txt`, `og.txt`, `r2-hex.txt`, `r2-palabras.txt`, `r2-material.txt`, `r2-luz.txt`,
  `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` y `orders/r1-og.json`, `r2-control.json`, `r2-luz.json`.
- `docs/marcas/portal/logos/portal-a.svg`, `portal-a-lockup.svg`, `portal-actual.svg` (último cambio `b7f1baf`); `b`-`d`
  siguen en la carpeta.
- `docs/marcas/README.md` l.13 (fila del Portal: elegido `a`, alt. `b`), l.24-30 («Elegido por el agente»), l.82-90 (familia
  Galivelop, texto en imagen, prompts), l.93-101 (tabla de destinos), l.133-140 (conceptos `a`-`d`).
- `docs/marcas/portal/biblia.md` (`74d99f8`; cita Portal `aa76b34`): §1 l.8-17, §2 l.23-44, §3 l.50-55, §4 l.59-83, §5
  l.86-92, §6 l.96-102, §7 l.106-115, §8 l.126-130, §9 l.137-143, §10 l.147-156. Lo que es **[P]** allí lo sigue siendo aquí.
- `docs/plan.md` l.520-528 (tabla de destinos), l.586-590 (acentos de los proyectos; pautas de luz y posición), l.596-606
  («Estilos por proyecto», Portal), l.663-664 (herramientas en la familia del Portal).
- `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.10 (Portal `aa76b34`), l.94-121 (Portal), l.329-337 (lo que añade).
- `docs/records/contenido/r0-humo.md` l.3, l.10 (og del Portal, 184 s); `r1-fondos.md` l.48, l.52, l.59, l.66, l.69;
  `r2-estilo.md` l.6, l.33-35, l.51; `r3-borrador.md` l.5, l.37-38, l.46, l.63-65; `r4-composicion.md` l.16, l.31-32;
  `r5-piezas.md` l.30, l.50, l.58; `calibracion-measure.md` l.9-10, l.18, l.20, l.27-30, l.56, l.68, l.84-85.
- `examples/pilot/componer.py` l.105-115 (`caja_zona`), l.119 (`peso_titulo=700`), l.124 (margen 6 %), l.129-137 (logo al
  9 %), l.138-149 (ajuste del texto), l.159-160 (subtítulo 400, opacidad 0,82); `examples/pilot/piezas.py` l.8, l.92-93
  (`fondo: null` = avatar); `examples/pilot/fuentes.sh` l.8-12.

Sin línea aquí y por tanto **[P]** o *(suposición)*: el umbral como motivo (sin «sí» de la persona), el dibujo del logo `a`
(sustituye al publicado), reglas del logo tras elegir (variantes, tamaños, separación, prohibidos), pieza clara, prohibidos de
la paleta, trece palabras vetadas añadidas, perfiles `square`/`portrait`, `draft`, `compose`, `icon`, cinco de las seis frases
de r5, las imágenes de marca como referencia, la regla de cierre, el `og` como sustituto de la captura.

**Lo que la configuración reflejaba de menos, ya al día (2026-11-04):** `og`, `social`, `square`, `portrait` y `header` con su
`targetWidth`/`targetHeight`; `draft` en `og`; `banner` retirado; `brand.palette` con `#eaf4fa`, `#2BB3EA`, `#0083c1` y
`#9fb4c4`. **Lo que sigue pendiente:**

- `compose`: plantilla, fuentes, zona, velo y logo en la pieza viven en `examples/pilot/componer.py`.
- Copia de los logos en `examples/portal/logos/`: pendiente (F2.10, dec. 3); `piezas.json` apunta fuera de la raíz del
  ejemplo (D25).
- `prompts/og.txt` y `orders/r1-og.json` son el orbe de r1 («no» de la persona): histórico, sin tocar; `estilo.txt` es el que
  manda. No llevan palabra vetada (comprobación 8 pasa).
- Cuando el ADR 0002 llegue a `main` del Portal: revisar propósito, sección 10 («Un taller independiente.», «Tres proyectos»)
  y el cuarto punto de color (`#8B5CF6`).
- En el repo del Portal (propuestas, no se hacen desde aquí): `tools/generar-marca.mjs` hace `galivelop-social.png` con otra
  tipografía y una sombra; que la pieza `social` salga de `gimg` o que el script use Sora 700 sin sombra.

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; es el antetítulo y el título del hero del Portal `main`); **caduca con el ADR 0002** |
| 3 | «Nunca se muestra» no vacío | pasa; nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | pasa (11 hex); fondo `#06121c`, texto `#eaf4fa` y acento `#1aa6df` están |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, `<title>`, sin `<text>`/`<image>`/`filter`; el favicon del Portal prueba la baldosa a 16 px, el trazo único del `a` no se ha probado a 16 px más que a ojo); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: sin `compose.fonts`, y las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts` |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | **pasa** los nueve prompts y los tres pedidos (grep del 2026-11-04 sobre las dos listas y `no`/`not`/`without`/`never`/`like`) |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (125-208 palabras), los nueve |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | pasa: múltiplos de 64 en los cinco perfiles y destino declarado en todos (1200×630, 1200×630, 1080×1080, 1080×1350, 1500×500) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | el prompt la describe en los cuatro formatos hechos; ningún perfil la declara (hueco de esquema, `compose` pendiente); la caja es la del compositor, con el desajuste de la sección 9 |
| 12 | Titular ≤ 200, cabe en la columna | pasa (28 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | **pasa** para lo que usan las piezas (texto, baldosa, texto 2, fondo, acentos y blanco); fuera quedan el fondo alterno `#081826` y los del tema claro, sin pieza que los use |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | **pasa:** `og`, `social`, `square`, `portrait` y `header` declaran su destino |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 18** (origen de la
familia: fondo, texto y titular son Obl. y salen del repo con línea). **16 completos desde un repo**, **2 [P]**: el motivo
(umbral, delegado tras el «no» de r1) y el dibujo del símbolo `a` (sustituye al publicado).

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan: roles de la paleta (`brand.palette` lleva los tres acentos de proyecto al mismo nivel
que el celeste), zona reservada (solo en prompt y en `componer.py`; tres zonas distintas según perfil), velo y
logo en la pieza (solo en `componer.py`), palabras vetadas sin campo, `avatar` sin perfil (lo hace `piezas.py`), tipografía sin
licencia ni ruta declaradas, imágenes de marca para la EMD sin lista (la calibración usó una captura de la interfaz), idiomas y
textos por idioma (el Portal publica en `es`, `gl` y `en`, con gl obligatorio; las piezas solo en `es`), varias variantes de logo
(el lockup claro no existe y `compose.logo` admite uno), copia de los logos en `examples/<p>/logos/` pendiente. No le afectan:
`compose.lut` (paleta 70-82 %, dentro del umbral sin LUT), `style.lora`.

**Huecos propios de este proyecto, que la plantilla no lista:**

1. **Dos estados del repo de origen.** La marca publicada (`main`) y la marca en desarrollo (rama de trabajo con el ADR 0002)
   dicen cosas distintas sobre qué es Galivelop y cuántos proyectos tiene. La hoja sigue `main`; ningún campo de la
   configuración ni de la hoja marca la fecha de caducidad.
2. **Un logo que sustituye al publicado.** El `a` no es un logo nuevo para una marca sin logo (como en las herramientas), sino
   una simplificación del que ya está en el favicon, el `apple-touch-icon` y el README del Portal. Si se acepta, hay que
   proponérselo al Portal (`public/marca/gv-logo.svg`, `src/components/Logo.tsx`, `tools/generar-marca.mjs`); si no, las piezas
   deben usar `portal-actual.svg`. La plantilla no distingue «logo propuesto» de «logo publicado».
3. **Un generador de marca en el repo del propio Portal** (`tools/generar-marca.mjs`) que no sigue sus propias reglas de
   tipografía ni de logo (ver «Contradicciones», 2). La fila nueva de la sección 11 ya lo recoge; falta que alguien lo alinee.

---

## Contradicciones

Todas **resueltas el 2026-11-04** por delegación de la persona, con el criterio de
[`decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md). Entre el repo del Portal (`main` `7c9a704` y rama `66ec4f1`) y la biblia (`74d99f8`), o entre la biblia y lo que ya generó el
motor.

1. **La identidad cambia en la rama de trabajo del Portal.**
   `main` (publicado) y la biblia dicen «Taller independiente de software»; la rama `ccr-47f8fddd-o5ek6p` (`66ec4f1`, 2026-10-27)
   trae el ADR 0002 «Galivelop como marca con taller y oferta de productos e integrantes»: hero «Marca de software: taller y
   Productos», «Galivelop son dos cosas: el taller… y Productos» (software de descarga local y servicios de sus integrantes, sin
   precios), `og:title` nuevo, glosario con «Marca», «Productos», «Integrante promocionado», y un **cuarto proyecto**
   (Galivelop Image Generator, acento `#8B5CF6`, con portada 1600×1000). El propio ADR dice «Sin publicar en main hasta que
   la persona lo vea y confirme». El lema no cambia. **Afecta a la hoja:** el propósito (sección 1), el cierre «Galivelop. Un
   taller independiente.» y el gancho «Tres proyectos, un mismo taller.» / «Tarkor, toVeriAI y Galivelop-workflow» (sección
   10, piezas `cabecera` y `vertical` de r5), los tres puntos de la imagen (serían cuatro) y «Nunca se muestra» (el taller no
   vende, pero la marca tendrá Productos: la frontera hay que redibujarla). **Propuesta:** la hoja sigue lo publicado hasta
   que la persona publique el ADR; mientras, no se compone ninguna pieza nueva con «taller independiente» ni con «tres
   proyectos» (lo de r5 queda como ronda de prueba), y al publicarse se revisan propósito, sección 10 y el prompt (cuatro
   puntos) en una ronda corta. Si la persona prefiere anticipar el ADR en las piezas, se cambia la hoja antes. **Resuelta:** manda **`main`** («Taller independiente de software», acentos `#E0703A`, `#2F7A55`, `#3D6FD9`); la hoja no se adelanta al ADR 0002 (criterio 1: lo publicado manda). Al fusionarse el ADR en el Portal se revisa la hoja (propósito, sección 10 y el cuarto punto `#8B5CF6` si lo trae).
2. **`galivelop-social.png` rompe las reglas de su propia marca.**
   Lo genera `tools/generar-marca.mjs` con `font-family: system-ui` peso 800 y `letter-spacing` −4 px (la web usa Sora 700,
   −0,03 em), con `drop-shadow` sobre el logo (prohibido en la biblia §4 y en esta hoja) y con un subtítulo propio («Taller de
   creación, investigación y aprendizaje») que no está en la web; mide 1200×630 cuando la tabla común da `social` como
   1280×640. **Propuesta:** la pieza `social` del Portal la hace `gimg` desde el mismo fondo que `og` (sin recorte, 1200×630
   si GitHub lo admite, o 1280×640 y entonces se cambia el archivo), con el lockup `a` o el actual según decida la persona;
   al Portal se le propone sustituir la salida del script o hacer que use Sora 700 sin sombra. **Resuelta:** `galivelop-social.png` es pieza heredada que este sistema sustituye; la propuesta al Portal sigue siendo propuesta (criterio 5: no se modifica desde aquí).
3. **El og:image es una captura, no arte de marca.** `galivelop-portal.jpg` es
   «captura de la portada» (`docs/desarrollo.md`), y es la imagen con la que la calibración fijó los umbrales del Portal
   (YAVG 45-65, SATAVG 13-19, paleta ≥ 70 %) y la referencia de su EMD. Si no cuenta como marca, los umbrales se sostienen
   solo en r5 (53-62, 14-16, 70-82 %) y la EMD queda sin referencia. **Propuesta:** la persona decide; si el `og` de r4 se
   acepta, pasa a ser la referencia y sustituye a la captura en el Portal (propuesta al Portal: `index.html` l.19,
   `paginas-estaticas.mjs` l.10). **Resuelta:** la captura `galivelop-portal.jpg` solo calibra la medida; no es arte de marca ni referencia de estilo. La EMD queda sin referencia hasta que una pieza `og` reciba el «sí» de la persona.
4. **Dos juegos de acentos en la rama de trabajo.** `src/data/proyectos/*.json` da workflow
   `#3D6FD9` e image-generator `#8B5CF6`; `src/data/productos/*.json` da workflow `#1AA6DF` (el celeste de la marca) e
   image-generator `#7C5CD6`, más developer `#0E9A93` y voice-generator `#C9467A`. La biblia y el prompt usan solo los de
   proyecto; las biblias de las herramientas (`docs/plan.md` l.664) proponen otros (`#2BB3A3` developer, `#D9467A` voces).
   **Propuesta:** en la imagen del Portal, los puntos son **de proyecto** (lo que la biblia y r2 fijaron) y nunca de
   producto; se le pide al Portal un solo acento por entidad, y a las hojas de las herramientas que lean el suyo del Portal
   cuando se publique. **Resuelta:** los puntos de la imagen son de proyecto, nunca de producto, y se queda en los tres de `main` mientras el ADR 0002 no se publique; el acento único por entidad es propuesta al Portal.
5. **LinkedIn como canal.** La biblia §9 dice «Redes: Discord, LinkedIn y
   GitHub». En el repo solo constan correo, GitHub y Discord (`src/data/marca.ts` l.3-5; el `sameAs` de JSON-LD,
   `paginas-estaticas.mjs` l.105, enlaza los proyectos, no redes del taller); LinkedIn
   aparece solo como destino de la vista previa (`index.html` l.12, comentario) y en la tabla común de este repo.
   **Propuesta:** la cabecera 1584×396 de LinkedIn queda **[P]** hasta que la persona confirme una página; la biblia §9 pasa a
   «Discord y GitHub constan; LinkedIn, no». **Resuelta:** LinkedIn «no consta en el repo»; su cabecera 1584×396 no se hace hasta que la persona confirme el canal; la biblia §9 se corrige.
6. **Zona reservada.** Biblia §7: «la mitad o el tercio izquierdo», sin perfil. Lo
   hecho y medido: `og`/`social` mitad izquierda, `square`/`portrait` mitad superior, `header` dos tercios izquierdos
   (`prompts/*.txt`, `piezas.json`). **Propuesta:** la tabla de la sección 9 manda; corregir la biblia §7. **Resuelta:** zona la del compositor (criterio 3: una sola por perfil); biblia §7 corregida. Queda el desajuste de caja y prompt anotado en la sección 9.
7. **Separación del lockup.** Biblia §4 (reglas **[P]** tras elegir): «separación de un
   cuarto del lado» (32/128). `portal-a-lockup.svg` pone el texto en `x=152`, 24/128. Es lo que r4-r5 compusieron y midieron.
   **Propuesta:** 24/128 (3/16 del lado) en la hoja y corregir la biblia; si la persona prefiere el cuarto, se redibuja el
   lockup y se recompone sin regenerar. **Resuelta:** manda el archivo, 24/128 (≈ 0,19 del alto); biblia §4 corregida.
8. **`banner` 1600×640 y las portadas.** La tabla común y la biblia dan `banner` como
   portada 1600×640 «en el Portal», pero en el Portal solo Tarkor tiene esa medida; workflow e image-generator son 1600×1000 y
   toVeriAI 1440×900, y el Portal no tiene portada propia. Los cinco `banner` de las líneas de trabajo no tienen hoy sitio
   en la web. **Propuesta:** no generar `banner` del Portal hasta que la persona diga dónde iría (una sección de líneas en la
   web, o nada); si va, 1600×640 como Tarkor y `.webp`. **Resuelta:** la pieza `banner` 1600×640 sale de la configuración del Portal (no tiene respaldo en su biblia); perfil retirado de `galivelop-images.json`.
9. **`stroke="#fff"` en `Logo.tsx` y `#FFFFFF` en el SVG.** Mismo color, dos notaciones; los
   dibujos de este repo usan `#FFFFFF`. Sin propuesta, solo para que un grep por hex no lo tome por un color distinto. **Resuelta:** trazo del logo `#EAF4FA` como valor de referencia (la biblia) y se apunta que el Portal publica `#fff`; los SVG de `logos/` siguen en `#FFFFFF` hasta que alguien los redibuje.

## Cambios que pediría a la plantilla

El Portal es la marca paraguas: aquí la plantilla se lee al revés (nada se hereda, todo se origina) y choca en tres sitios.

1. **La familia Galivelop necesita una fuente con línea.** El bloque «Familia Galivelop» de la plantilla da por rellenados
   fondo, texto, titular y baldosa «heredados del Portal», y las hojas aprobadas los citan como «heredado de Portal-Galivelop
   `aa76b34`» a través de las biblias. Hoy esos valores viven en `global.css` y `gv-logo.svg` del Portal con línea, y aquí se
   citan por primera vez. **Pediría:** que «Familia visual» admita `Galivelop (origen)` para la marca paraguas (entonces fondo,
   texto y titular son Obl., 18 en total, y «Hereda de» es «no hay»), y que el bloque «Familia Galivelop» de la plantilla
   cite esta hoja (`docs/marcas/portal/hoja.md`, secciones 3-5) como la fuente de los valores heredados, de modo que un cambio
   en el Portal se anote una vez y las demás hojas lo hereden por referencia.
2. **Un logo propuesto que sustituye a uno publicado.** La fila «Símbolo SVG» admite ruta o «no hay»; no contempla que la marca
   **ya tenga** un logo publicado y la hoja proponga otro. Aquí el `a` convive con `portal-actual.svg` y con el favicon, el
   `apple-touch-icon` y el README del Portal. **Pediría:** una subfila o una nota en «Símbolo SVG»: «logo publicado hoy (ruta
   en su repo) / logo de las piezas (ruta aquí) / qué pasa si no se acepta» (la hoja debe decir qué archivo usan las piezas
   mientras la propuesta no se acepte).
3. **Fuente de verdad con dos commits cuando lo publicado y lo que se desarrolla difieren.** «Fuente de verdad» pide «repo, rama
   y commit». El Portal publica desde `main` y desarrolla en una rama que cambia la identidad; la biblia leyó un commit de la
   rama de trabajo (`aa76b34`) creyéndolo lo publicado (y acertó solo porque lo que leyó no había cambiado). **Pediría:** que la
   fila distinga «publicado (rama y commit)» de «en desarrollo (rama y commit), solo para contradicciones», y que la sección
   13 lleve un bloque por cada uno, como hace esta hoja.

Las tres filas nuevas de la plantilla (acentos en imagen, otras piezas de otro sistema, canales con «consta / no consta») le
vienen bien al Portal: los tres puntos de proyecto, `tools/generar-marca.mjs` y el inventario de Discord/GitHub/LinkedIn no
tenían sitio antes.

---

## Lo que enseñó rellenarla

**Balance de este proyecto:** 18 obligatorios (origen de la familia); **16 completos desde un repo** (Portal `main` o este),
**2 [P]** (aprobados por delegación) (el motivo umbral, elegido por el agente tras el «no» de la persona en r1; el dibujo del símbolo `a`, que sustituye
al publicado). De los 67 campos de la plantilla, 16 son **[P]** en todo o en parte (umbral, logo `a`, variantes, tamaños y
márgenes, usos prohibidos del logo, pieza clara y sus combinaciones, prohibidos de la paleta, trece palabras vetadas,
`square`/`portrait`, `compose`, `icon`, `draft`, cinco frases de r5, imágenes de marca como referencia, regla de cierre, promesas
de esta hoja) y 1 es «no hay» (Hereda de, por ser el origen). De los recomendados, 4 «no hay» o no comprobables (composición
por perfil, copia de logos, fuentes instaladas, lockup claro), los mismos que en las dos hojas anteriores.

**Diferencia con image-generator y Workflow:** allí casi todo lo visual era heredado o propuesto; aquí casi todo lo visual sale
de un archivo del Portal con línea (CSS, SVG, fontsource, textos), y lo que es **[P]** es justo lo que la persona no ha visto:
el umbral y el logo `a`. A cambio, el Portal trae dos problemas que las herramientas no tienen: su repo está a punto de
cambiar de identidad en una rama sin publicar (ADR 0002), y sus propias imágenes de marca (una captura y un PNG con
`system-ui` y sombra) no cumplen la hoja que acaban de originar. Es la única marca de la familia en que la hoja es más
estricta que lo publicado.
