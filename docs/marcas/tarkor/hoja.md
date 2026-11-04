# Hoja de estilo mínima: Tarkor

**Aprobada el 2026-11-04** (decisiones delegadas por la persona; ver [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md)); tercer caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md)
(F2.12), rellenada tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y
[`../galivelop-workflow/hoja.md`](../galivelop-workflow/hoja.md), con su misma forma, y el **primero de familia visual
`propia`** (18 obligatorios en vez de 15). Complementa a [`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es
lo que `gimg` necesita, campo a campo y en el orden de la plantilla. Estados como en [`../README.md`](../README.md): sin marca
sale de un repo (ruta en la sección 13); **[P]** es propuesta del agente **aprobada por delegación** (la persona no ha visto la pieza ni dado un «sí» propio), con su porqué en la misma celda;
*(suposición)* se comprueba en una ronda; «no hay» solo donde la plantilla lo admite. Aquí no hay «heredado de»: la paleta y
la letra son del juego; del Portal solo viene el acento asignado.

Commits de referencia: World-Maker-Fantasy (WMF, el juego; repo **privado** según el `README.md` del Instalador) `e3778e61`
(`claude/narrador-tiempos`, 2026-11-04; la biblia cita `73965f62`: los archivos de identidad que cita no cambian entre los dos);
WMF-imagenes `8a48fe52` (`claude/plan-imagenes`); WMF-fichas `d77142b4` (`claude/fichas-banners`; mismo frontal y mismo
`index.css` que WMF, no aporta nada propio); Instalador-WMF-Tarkor `a73f881` (`main`, repo público); `plan-imagenes-tarkor`
(carpeta sin git; su contenido vive en WMF `docs/producto/plan-imagenes/`); Portal-Galivelop `aa76b34` (acento y portada, vía
`biblia.md` §10; desde aquí no se abre ese repo); este repo `5460d2c` (`f2-motor`). Los cinco repos de Tarkor se han leído
**sin modificar nada**.

**Lo primero que hay que saber:** la marca de Tarkor **se creó en este repo**: el juego tiene paleta y fuentes propias
(`frontend/src/index.css`, madera + hierro, Cinzel e Inter) pero **ni logo, ni og:image, ni favicon propio** (el `favicon.svg`
es el rayo violeta de Vite, `#863bff`, un color que la propia marca prohíbe). Lo único de marca que el juego ya enseña en
público es el icono de la app del Instalador (`app/src-tauri/icons/`): un rombo de cristal claro sobre un disco de madera
oscura, que es el concepto **b** (la gema) de la biblia, no el **a** elegido, y con el acento cristal, no el arcilla (cambiar ese icono es propuesta a ese repo). La persona
dio un **«no» a los fondos de r1 sin motivo** (2026-10-26) y desde entonces lo demás está delegado: todo lo que sigue del estilo
de imagen es hipótesis del agente, medida y ahora **aprobada por delegación** (2026-11-04), y el estilo sale **desaturado** en
todos los formatos (SATAVG 5-7 frente a los 18-32 de la portada); r2-luz y r2-luz-r1, que lo intentan arreglar, siguen
**sin medir**.

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Tarkor»: T mayúscula, el resto minúsculas. Así va en `<title>Tarkor</title>` del juego, en `productName` del Instalador y en el título del `README.md` del Instalador. «TARKOR» en mayúsculas solo como wordmark del lockup (y como eyebrow de la Home del juego, con tracking 0,3 em). El repo del juego se llama World-Maker-Fantasy: es el nombre del repo, no de la marca | WMF (`frontend/index.html`), Instalador (`app/src-tauri/tauri.conf.json`, `README.md`) |
| Nombre en código | Obl. | `tarkor` | repo (`examples/tarkor/galivelop-images.json`, `name`); coincide con `src/data/proyectos/tarkor.json` del Portal (vía biblia §10) |
| Fuente de verdad | Rec. | WMF `e3778e61` (paleta, fuentes, lema, propósito, voz, canon, canales); WMF-imagenes `8a48fe52` (preámbulo, vetadas, LUT, rangos del juego); Instalador `a73f881` (icono público, tokens reutilizados); Portal `aa76b34` (acento, portada); este repo `5460d2c` (logos, prompts, piezas, medidas). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio el veredicto de r1 (2026-10-26, **«no» a Tarkor sin motivo**) y aprobó ese día «la paleta y el emblema propuestos y Cinzel (OFL) como tipografía del wordmark, provisional hasta r4»; la elección entre los logos a-d y las decisiones de marca del piloto están delegadas al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2. El 2026-11-04 la persona delegó también las dudas de esta hoja y quedó **aprobada** con el criterio de [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md). El **canon del juego** no se decide aquí: tiene su dueño en WMF (creador: Álvaro García Graña) y esta hoja solo lo cita | repo (`docs/records/contenido/r1-fondos.md` l.52; `docs/plan.md` l.257-261; `docs/marcas/README.md` «Elegido por el agente»); WMF (`docs/producto/tarkor-contenido-web.md` l.35) |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `propia`: fondo, texto, tipografía y escena son del juego. De la familia Galivelop toma **solo la baldosa del símbolo** (`rx` 30/128) y el acento que el Portal le asignó | repo (`docs/marcas/README.md` l.84; `biblia.md` §4-§5) |
| Hereda de | Opc. | Portal-Galivelop `aa76b34`: acento `#E0703A` (`src/data/proyectos/tarkor.json` l.7) y portada `public/proyectos/tarkor/portada.webp` (1600×640, Pilares Rotos). Nada más | repo (`biblia.md` §10) |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Juego de rol por texto con una IA local como directora de juego, en un mundo de bolsillo…» (la línea del juego); se juega en Berig, continente de Helek Sirik («Origen Azul»). Para quien juega rol narrativo y quiere la IA en su máquina, sin cuentas; la Steam Deck es el objetivo; sin conexión; en alpha (hito 0.3 «Reino profundo», Llanuras como región jugable) | WMF (`docs/producto/tarkor-contenido-web.md` l.31-34, l.41-42); `biblia.md` §1 |
| Lema | Rec. | «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas.» (70 caracteres, literal) | WMF (`docs/producto/tarkor-contenido-web.md` l.40) |
| Tono | Rec. | épico y trágico **en el mundo**; cercano, concreto y honesto **al contar el proyecto**, sin vender; una idea por mensaje, un emoji como mucho en X | WMF (`docs/difusion/guia-canales.md` l.3-4 y §X); `biblia.md` §6 |
| Idiomas | Opc. | `es` (el juego es en español: `lang="es"`, «Idioma: Español»). El Portal publica la ficha en `es`, `gl`, `en` (`guia-canales.md` §Portal) y las tarjetas de `gw-media-content` salen en `es` y `en`; las piezas de imagen, solo en `es` (sin texto o con el lema en español) | WMF (`frontend/index.html`; `docs/producto/tarkor-contenido-web.md` l.33; `.claude/gw/gw-media-content.md` l.27) |
| Campo semántico | Opc. | dentro: mundo que sigue, Semilla, Origen Azul, madera, hierro, cristal, llanura, puente, clan, motor; fuera: todo el «Tono prohibido» del canon (luna, pólvora y arcabuz, vocabulario técnico, especies con nombre real, palabras en inglés) y lo de la fila «Nunca se muestra» | repo (`biblia.md` §6); WMF (`docs/canon-opencode/00-nucleo.md` l.37-43) |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | lo reservado del canon (qué sabe Tarkor, la Entidad, la luz morada, el Reino Nabierus, la Ciudad Hundida, el Archivo Cegado, el muro de obsidiana); **luna** (Berig no tiene: «El cielo sin luna», un cinturón de polvo que brilla de noche); humanos; pólvora; Vaelira; interfaz de juego falsa; fechas o promesas; «AAA genérico» (destellos, cromados, armaduras brillantes). El símbolo no presenta a Tarkor como héroe ni como villano: como mucho, la ambigüedad (fidelidad y ruptura). Que Tarkor volvió transformado es saber común; lo reservado es el porqué | repo (`biblia.md` §1); WMF (`docs/canon-opencode/00-nucleo.md` «Tono prohibido»; `docs/rpgtarkor/lore-mundo/genesis.md` l.146-155; `00-nucleo.md` QA-274); `docs/plan.md` l.647-648 |
| Personas y rostros | Rec. | ninguna persona ni personaje en las piezas de marca (el canon de personajes y razas no hace falta para un fondo); nunca humanos (no los hay en Berig); nunca el creador real ni nadie reconocible | repo (`biblia.md` §7 «No»); `docs/plan.md` l.651-652 |
| Promesas | Rec. | nada de fechas; el estado se dice como estado («alpha», «en desarrollo»), no como plazo; precio: no consta en el repo, no se afirma; nada de «sin bugs» ni de cuentas o servicios que el juego no tiene (es privado por diseño: sin cuentas, telemetría ni conexión) | repo (`biblia.md` §1); WMF (`docs/producto/tarkor-contenido-web.md` l.32-34, pilar 8) |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Obl. | **pieza clara:** hueso `#f1e4d0` (madera 100); **pieza oscura:** madera 900 `#241a10`, plano (sobre imagen no hay banda: ver «Combinaciones»). Los hex son del juego; **los roles no**: el juego es oscuro único (`color-scheme: dark`, cuerpo en madera 950 `#1b130c`), y la «pieza clara» sobre hueso la inventó la marca en r4 porque el texto oscuro sobre el fondo lavado daba 1,8-2,9:1 y el velo claro lo subió a 11,26. Porqué de mantener las dos: el og compuesto en r4 (claro) y el og-bajo de r5 (oscuro) son las dos piezas con mejor contraste del piloto | hex: WMF (`frontend/src/index.css` l.23-54; `body` l.113-116); roles **[P]** aprobados por delegación, contradicción 6 (`biblia.md` §2 l.28 y l.35-36; `docs/records/contenido/r2-estilo.md` l.67-69; `r4-composicion.md` l.19) |
| Texto | Obl. | hierro 700 `#221c16` sobre claro; hueso `#f1e4d0` sobre oscuro. Medido: 11,26:1 (peor 6,97) sobre el velo claro del og de r4; 9,5:1 (peor 7,36) sobre el velo oscuro del og-bajo de r5 | WMF (`index.css` l.23-54); repo (`examples/tarkor/piezas.json` `color_texto`; `r4-composicion.md` l.19; `r5-piezas.md` l.41-43) |
| Acento | Obl. | **arcilla `#E0703A`** (acento de marca: baldosa del símbolo, luz rasante de las escenas, un solo acento por pieza). **Decidido (2026-11-04, delegado):** arcilla en las piezas, cristal solo dentro del juego. El juego usa **cristal `#4aa8d8`** (familia `accent-*`, tematizable por mundo: gema `.gem`, filetes, eyebrow «Tarkor» de la Home en `accent-400` `#7bc4e8`) y el icono público del Instalador también es cristal. Regla: **arcilla fuera del juego, cristal dentro**, porque todo el arte que existe es roca roja, la arcilla es el único acento cálido de la familia Galivelop y es el que el Portal ya asignó (con ese color presenta a Tarkor); el cristal queda como secundario (gema, noche) y no se toca en el juego | decidido, [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md) (decisión 3); razones en `biblia.md` §2 l.39-44 y `docs/marcas/README.md` l.37; hex: Portal `aa76b34` (`tarkor.json` l.7, vía biblia); WMF (`index.css` `--color-accent-*`; `pages/Home.tsx` l.24-33); Instalador (`app/src-tauri/icons/`) |
| Acentos en imagen, en orden de peso y significado | Rec. | uno por pieza: 1) arcilla `#E0703A`, la luz baja que enciende las puntas de la roca y la banda del horizonte (la marca); 2) cristal `#4aa8d8` solo dentro del juego (escenas de noche o con la gema), nunca en una pieza de marca. Nunca los dos en la misma pieza. No es un proyecto de diagrama: no hay más | repo (`biblia.md` §2 «Prohibidos» l.37; `examples/tarkor/prompts/estilo.txt` y `r5-og-bajo.txt`, «Colours:») |
| Resto de la paleta | Rec. | madera 950 `#1b130c` (cuerpo del juego), 800 `#332415` (crestas de la escena, tablón), 700 `#46311d`, 600 `#5c4126` (veta), 400 `#a3814f` (wordmark del lockup oscuro), 300 `#c9a877`, 200 `#e3cba8`; hierro 900 `#0e0b08`, 800 `#171310` (aros, remaches); acero `#52626f` (cielo y llanura del og-bajo), `#8a9aa8` (llanura en calima de la escena), `#6b7d8c`, `#b0bec8` (texto secundario); cristal `#a8d8f0`, `#7bc4e8`, `#3488b8`; musgo `#8fae6a` / `#6f9450` / `#587a3c` **solo semántico en el juego, no en marca**; `danger` y `cost` (rojos y ámbares de Tailwind) solo interfaz | WMF (`index.css` l.23-54, l.56-70); repo (`biblia.md` §2; prompts) |
| Combinaciones | Rec. | **clara:** `#f1e4d0` + texto `#221c16` + lockup claro + velo `#f1e4d0:0.55` (og r4, cuadrado, vertical y cabecera de r5); **oscura:** velo `#221c16:0.45` + texto `#f1e4d0` + lockup con wordmark `#a3814f` (og-bajo r5); pieza plana oscura: `#241a10`. La banda de madera 950 `#1b130c` al 70 % de la biblia **sale**: lo medido la sustituye (ver «Contradicciones», 6) | repo (`examples/tarkor/piezas.json`; `r4-composicion.md` l.19; `r5-piezas.md` l.33, l.41-43) |
| Prohibidos | Rec. | negro `#000` y blanco `#fff` puros; morado y violeta (la luz reservada del canon; también el `#863bff` del favicon de Vite que el juego aún lleva); neón; más de un acento por pieza; degradados fuera de la baldosa y la gema; azules corporativos en lo de marca (el cristal es del juego) | repo (`biblia.md` §2 l.37-38); WMF (`frontend/public/favicon.svg`; `00-nucleo.md` «luz morada» reservada) |
| Degradados | Opc. | la baldosa del símbolo `#E0703A → #8a3b1e` (`tarkor-a.svg`, `linearGradient`); la gema del juego `accent-300 → accent-600` (`.gem`); nada más | repo (`docs/marcas/tarkor/logos/tarkor-a.svg`); WMF (`index.css` l.246-254) |

**Medido:** la calibración da a este proyecto el umbral de paleta más bajo (**≥ 30 %**) porque su imagen de marca, la portada
del Portal, da 42 % contra los hex de la biblia; las piezas del piloto dan más (og r4 72,32 %; r5 69-84 %; og-bajo 50,52 %,
porque su cielo `#52626f` no estaba en la paleta medida) y r1, mucho menos (7-12 %, paleta de la portada *suposición*). El
problema de Tarkor no es la paleta: es la **saturación** (sección 7).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/tarkor/logos/tarkor-a.svg`: **los Pilares Rotos**, dos torres de hueso `#f1e4d0` en silueta rellena, desiguales (la izquierda alta, la derecha quebrada a media altura), unidas por un puente colgante en trazo de 6 con remate redondo, sobre la baldosa de la familia (`rx` 30/128) con el degradado arcilla `#E0703A → #8a3b1e`. `viewBox="0 0 128 128"`, `<title>Tarkor: Los Pilares Rotos</title>`, sin `<text>`, `<image>` ni `filter`. El **concepto** lo aprobó la persona (el emblema del plan, 2026-10-26); la **elección** entre a-d y el **retoque** para que no se lea como una M (el que lleva el archivo desde `c63761f`) son del agente, delegados: faltan sus ojos. Copia en `examples/tarkor/logos/`: **no hay** (F2.10, dec. 3) | archivo: repo (`docs/marcas/tarkor/logos/tarkor-a.svg`, último cambio `c63761f`); dibujo **[P]** (`biblia.md` §4 l.65-67; `docs/marcas/README.md` l.16 y l.33; `docs/plan.md` l.257-261 y l.655-657) |
| Lockup (símbolo + nombre) | Rec. | `tarkor-a-lockup.svg` (`viewBox 0 0 468 128`): símbolo a la izquierda y `<text>` «TARKOR» en Cinzel 700, 50 px, `letter-spacing` 9 (0,18 em), relleno madera 400 `#a3814f`, para fondo oscuro. `tarkor-a-lockup-claro.svg`: igual con relleno hierro `#221c16` (`data-fondo="claro"`; el propio archivo anota que madera 400 no llega a 3:1 sobre hueso). El nombre va como `<text>`, no a trazos: depende de que Cinzel esté instalada (`piloto/fuentes/`, `examples/pilot/fuentes.sh`); pasarlo a trazos es **[P]** de la biblia | repo (`docs/marcas/tarkor/logos/tarkor-a-lockup.svg`, `tarkor-a-lockup-claro.svg`); trazos **[P]** (`biblia.md` §4 l.71) |
| Variante clara y oscura | Rec. | el símbolo vale sobre claro y oscuro (baldosa arcilla con hueso dentro); el lockup tiene dos archivos: `-claro` (hierro) sobre hueso y velo claro, el normal (madera 400) sobre madera y velo oscuro. Así se usaron en r4-r5 | repo (`examples/tarkor/piezas.json`, `logo` de `og` y `og-bajo`) |
| Tamaño mínimo y margen | Rec. | símbolo 16 px, wordmark 20 px de alto; margen libre = la altura de la «T» del wordmark; en el lockup, altura de la mayúscula ≈ 0,28 del símbolo | **[P]** (`biblia.md` §3 l.51-52 y §4 l.69-70; «sí» a 16 px solo visto por el agente en la tabla de la biblia §4) |
| Usos prohibidos | Opc. | el símbolo va con el wordmark, o solo en esquina y avatar; nunca estirado, rotado, con sombra ni brillo; nunca el símbolo sobre morado ni con el cristal como baldosa | **[P]** (`biblia.md` §4 l.70-71) |
| Logo fuera de la paleta | Opc. | `#8a3b1e` (fin del degradado) y `#a3814f` (wordmark oscuro) no están en `brand.palette`; `#E0703A` y `#f1e4d0` sí | repo (`tarkor-a.svg`, `tarkor-a-lockup.svg`; `galivelop-images.json`) |

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Obl. | **Cinzel 700** (titular de las piezas y wordmark), reserva `serif`. Es la `--font-serif` del juego («Cinzel», Georgia, serif) y la de su `<h1>` de la Home (`font-serif`); la persona la aprobó para el wordmark «provisional hasta r4»; r4 y r5 se compusieron con ella (`piezas.json` `fuente: Cinzel`) y falta su «sí» definitivo | WMF (`frontend/src/index.css` l.9-14; `pages/Home.tsx` l.31-33); repo (`docs/plan.md` l.258; `examples/tarkor/piezas.json`) |
| Familia de texto | Rec. | **Inter 400** en el subtítulo de las piezas, con opacidad 0,82 (lo compuesto en r4-r5, la misma regla de los siete proyectos; `fuente_texto: Inter`); 500 solo en el eyebrow. Es la `--font-sans` del juego y la fuente del cuerpo. Cascadia Code en cifras, solo dentro del juego | WMF (`index.css` l.9-14, l.113-117); repo (`piezas.json`) |
| Licencia y archivo | Rec. | Cinzel e Inter **OFL**, empaquetadas en el juego como variables (peso 400-900): `frontend/src/assets/fonts/cinzel-latin-wght-normal.woff2`, `cinzel-latin-ext-wght-normal.woff2`, `inter-latin-wght-normal.woff2`, `inter-latin-ext-wght-normal.woff2`, `fonts.css` (@fontsource-variable 5.3.0), `LICENSE-Cinzel.txt`, `LICENSE-Inter.txt`. En este repo las baja `examples/pilot/fuentes.sh` (`Cinzel[wght].ttf`, `Inter[opsz,wght].ttf` del repo google/fonts) a `piloto/fuentes/`, que **en esta máquina no existe hoy**: rsvg usaría la reserva | WMF (`frontend/src/assets/fonts/`); repo (`examples/pilot/fuentes.sh` l.11-15; `componer.py` l.14, l.29) |
| Tracking y mayúsculas | Opc. | wordmark «TARKOR» en mayúsculas, Cinzel 700, **0,18 em** (9 px a 50 px). El juego lleva otro rótulo «Tarkor» como eyebrow de la Home: `text-xs`, `uppercase`, **0,3 em**, en cristal `accent-400` y **sin `font-serif`** (hereda Inter del cuerpo), con filetes y gema: el eyebrow es **Inter 500**, no Cinzel (biblia §3 corregida; ver «Contradicciones», 8) | repo (`tarkor-a-lockup.svg`; `biblia.md` §3); WMF (`pages/Home.tsx` l.24-33; `index.css` l.113-117) |

## 6. Escenas y motivos (lo que el modelo pinta)

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | la escena del estilo elegido (r2): **agujas de roca de hierro oscuro `#221c16` sobre crestas de arena `#332415`**, con las puntas encendidas por una luz baja en arcilla; tercio izquierdo (o inferior) de **llanura abierta en calima `#8a9aa8`**, lisa; **un hilo de humo** de un campamento lejano y **un estandarte** de tela cruda en un poste de madera (la «huella de vida»: el mundo sigue). Del canon: los Pilares Rotos con puentes y estandartes (ya en la portada: no repetir en el og), Agujas Imán y crestas de arena imán, empalizada de troncos de Telda, obelisco goirnte, noche de estrellas con velo perlado (sin disco). **Es hipótesis del agente, aprobada por delegación,** tras el «no» sin motivo de r1 (que el og repetía la portada; que el golden hour era el AAA vetado; que la mitad vacía quedaba muerta; que nada decía «el mundo sigue»); r2 y r5 lo midieron, la persona no lo ha visto | **[P]** (`biblia.md` §7 l.92-96 y l.100-105; `examples/tarkor/prompts/estilo.txt`; `docs/records/contenido/r2-estilo.md` l.52); canon: WMF (`regiones/llanuras-del-viento-rojo.md` l.376-385; `guia-visual-mundo.md` §1-2) |
| Motivos No | Obl. | texto; personajes y rostros; criaturas (ninguna fuera del canon, y para marca ninguna); interfaz; oscuridad total; cielo de otro mundo (ni luna ni «heavens»); tráiler AAA (destellos, cromados, armaduras); estética de otro juego; el disco del sol; cualquier cosa morada; las ruinas del canon reservado | repo (`biblia.md` §7 «No»; `docs/plan.md` l.651-652); WMF (`00-nucleo.md` «Tono prohibido») |
| Palabras vetadas | Obl. | del juego (`mundo.json`, como patrones): `moon`, `moons`, `moonlit`, `moonlight`; `crystal dust`, `heavens`; `scar`, `scars`, `scarred`, `wound`, `wounds`, `gash`, `gashes`; negaciones `no`, `not`, `without`, `never`, `none`, `nothing`, `nobody`, `n't`; nombres propios; humanos (`human`, `man`, `woman`, `people`); pólvora (`gunpowder`, `musket`, `cannon`). De la marca: `purple`, `violet` (luz reservada); `like`. De la pauta de luz (2026-11-02): **`sun` vetada** (pinta el disco; se dice la dirección, no la fuente: «light», «backlight», «from low behind them»). Comunes: `text`, `letters`, `logo`, `watermark`, `caption`, `sign`. Las de marca y la pauta se añaden a la lista del juego, aprobadas por delegación (2026-11-04) | repo (`biblia.md` §7 l.97-98; `docs/plan.md` l.578-592); WMF-imagenes (`image-generator/estilo/mundo.json` l.146-152; `docs/producto/plan-imagenes/plantilla-prompt.md` l.15-22); añadidas, aprobadas por delegación |
| Estilo de imagen | Rec. | «Style: cinematic landscape photograph, **rich natural colour**, subtle filmic grade, fine detail. Colours: #E0703A, #221c16, #f1e4d0, #8a9aa8. Mood: wild, quiet, lived-in.» **«Natural muted colours» (la línea del r2 elegido y de la guía visual del mundo, §1.5, que allí es [propuesta]) queda retirada** (decisión 2026-11-04): pedía lo que la medida penaliza. Los prompts históricos (`estilo.txt`, r5) conservan «muted» hasta rehacerlos. El juego, en cambio, genera sus banners con «photorealistic fantasy matte painting, cinematic concept art, {luz}, **rich natural colour**. Mood: epic, hazy, grounded.» y preámbulos «vivid, saturated natural colours»; `r2-luz-r1.txt` prueba «rich natural colour» frente a `r2-luz.txt` (que se queda en «muted» como contraste de esa prueba); si no basta, la LUT de F2.11. Ver «Contradicciones», 4 | repo (`examples/tarkor/prompts/estilo.txt` l.final, `r2-luz-r1.txt`); WMF-imagenes (`mundo.json` preámbulos y estilos; `guia-visual-mundo.md` §1.5) |
| Lenguaje de forma | Opc. | materia tallada y forjada (madera veteada, hierro negro, hueso, cristal facetado); silueta rellena antes que contorno; radios: baldosa 30/128, paneles 12 px, remaches redondos, gema con esquinas vivas; trazos 3,5-6/128; filetes de 1 px que se desvanecen (`.accent-hairline`); simetría rota a propósito | repo (`biblia.md` §5); WMF (`index.css` l.226-234, l.246-254, l.324-348) |

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | «A warm raking light in #E0703A comes from low behind them, from the right» (rasante, a contraluz, sin nombrar la fuente). Solo `r2-luz.txt` y `r2-luz-r1.txt` lo hacen así; `estilo.txt`, `r5-*.txt` y `og.txt` nombran «the first low sun» / «the low sun» y son históricos hasta rehacerlos (ver «Contradicciones», 3). r2-luz sigue sin medir | *(suposición)* (`examples/tarkor/prompts/r2-luz.txt`; `docs/plan.md` l.773-798 «r2 luz») |
| Momento y clima | Rec. | amanecer bajo en calima: «in low subdued light… the ground darker than the sky» al principio del prompt (r2-luz); variante `r2-luz-r1`: «deep warm backlight», cielo ámbar y carmesí `#f2b34a`, la luz que ganó en el banco del juego («cine2: sol bajo a contraluz, cielo ámbar, polvo encendido, borde de luz»). El og-bajo de r5 probó «last minutes before sunrise» con cielo y llanura en acero `#52626f`: bajó el YAVG (169 → 66) y no el color. Nunca noche con luna; la noche del canon es un cinturón de polvo que brilla, con velo perlado | *(suposición)* (`r2-luz.txt`, `r2-luz-r1.txt`, `r5-og-bajo.txt`; `docs/plan.md` l.650-651; `r5-piezas.md` l.41-43); canon: WMF (`genesis.md` l.146-155) |
| Luminosidad objetivo (YAVG) | Rec. | **105-150** (portada 127). Medido: r1 129/125; r2 hex 155,2; og r4 168,91; r5 172-177 (lavado); og-bajo 66 (pasado de oscuro). El juego usa otros rangos para sus propias imágenes: 70-95 (plan) y 103-133 (banners de día): ver «Contradicciones», 7 | repo (`docs/records/contenido/calibracion-measure.md` l.31-34, l.69); WMF-imagenes (`estilo/gradacion.json`) |
| Saturación objetivo (SATAVG) | Rec. | **18-32** (portada 25). Medido: r1 35/31 (dentro, pero «no»); r2 6,4-8,6; og r4 7,79; r5 5-7; og-bajo 5. **Ninguna pieza del estilo elegido llega**: es el problema abierto de la marca; r2-luz y, si no basta, la LUT de F2.11 (sin LoRA en F2) | repo (`calibracion-measure.md` l.31-34, l.69; `r2-estilo.md` l.36-38, l.64-66; `docs/handoff.md` l.52; `docs/plan.md` l.872) |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **1) `portada.webp`** 1600×640 (los Pilares Rotos), **publicada:** ficha de Tarkor en el Portal (`public/proyectos/tarkor/portada.webp`, Portal `aa76b34`: consta, vía biblia); **valores:** YAVG 127, SATAVG 25, paleta 42 %; es la única imagen con la que se calibró Tarkor (los rangos de la sección 7 salen de ella). **2)** 304 `.webp` de arte del juego en `public/proyectos/tarkor/arte/` del Portal: referencia `-r` de sujeto, no de marca (consta en el Portal, vía plan). **3)** los banners por región del juego (1280×512, WMF-imagenes `image-generator/`, los 134 del LoRA): no publicados, repo sin versionar, no son marca. **Lo que no hay:** og:image en el juego (`frontend/index.html` sin `og:`), social preview de GitHub (WMF es privado: no comprobable; Instalador: no consta), ninguna pieza publicada en X, LinkedIn, Reddit o Discord que conste en los repos. **Pendiente de la persona:** si la portada vale como imagen de marca (es la del Portal, no del juego) | repo (`biblia.md` §10; `docs/plan.md` l.649-650; `calibracion-measure.md` l.31, l.76); portada **[P]** como marca (`docs/handoff.md`, leves de F2.9) |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración (todos 6 pasos, cfg 1.0, euler, `flux2-klein-4b-q8`; con destino declarado desde el 2026-11-04): `og` 1280×640 → `targetWidth`/`targetHeight` 1200×630 (og:image del juego —no existe aún—, ficha del Portal, vista previa en LinkedIn), `social` 1280×640 (social preview de GitHub 1280×640, mismo tamaño: sin destino; del juego no comprobable, privado; del Instalador no consta), `banner` 1280×512 → 1600×640 (la portada del Portal; **nunca generado**), `square` 1024×1024 → 1080×1080 (X y LinkedIn), `header` 1536×512 → 1500×500 (cabecera de X), `portrait` 896×1152 → 1080×1350 (`vertical`, declarado). **Discord (960×540) y LinkedIn (1584×396) son perfiles aparte, cuando se pidan** (no están). Además, `guia-canales.md` pide **1600×900 (16:9)** para X, LinkedIn, Reddit y Discord y el Portal una WebP de 1600 px con `-mini` de 720: formato sin perfil | repo (`examples/tarkor/galivelop-images.json`; `examples/tarkor/piezas.json`; `docs/marcas/README.md` «Común a todos»); 16:9 **[P]**; canales: WMF (`docs/difusion/guia-canales.md` §Imágenes) |
| Zona reservada | Obl. | `og`, `social`, `banner`: **`izquierda 1/3`** («The left third of the frame is a calm, open stretch of plain under soft morning haze…»; caja del piloto 55 % del ancho, margen 6 %); `header`: **`izquierda 1/2`** («The left half of the frame…», 11,39:1, peor 6,89; decidido, la biblia se corrige); `square`, `portrait`: **`abajo 1/2`**: el prompt pide la mitad libre («The lower half of the frame…», casa con la caja del piloto, 48 % del alto). Los `r5-cuadrado.txt` y `r5-vertical.txt` actuales piden aún «lower third»: son históricos y hay que rehacerlos (ver «Contradicciones», 1 y 2). En píxeles del destino: og 1200×630, columna izquierda de 400 px; square 1080×1080, banda inferior de 540 px | repo (`biblia.md` §7 l.99; `prompts/estilo.txt`, `r5-cabecera.txt`, `r5-cuadrado.txt`, `r5-vertical.txt`; `piezas.json` `zona`; `examples/pilot/componer.py`; `r5-piezas.md` l.33); decididas el 2026-11-04 (una sola zona por perfil, la misma en prompt, plantilla y medida) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose`: el piloto construye el SVG en código (velo, lockup al 9 %, título Cinzel 700, subtítulo Inter 400). Portar a `compose: {template, logo: "logos/tarkor-a-lockup-claro.svg", fields: ["title","subtitle"], fonts: ["Cinzel","Inter"], fit: "cover"}` (y un segundo perfil o plantilla para la pieza oscura con el lockup normal) | **[P]** (F2.8/F2.12; `examples/pilot/componer.py`) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `tarkor-a.svg` rasterizado sin fondo (`"fondo": null`), hecho en r5. `icon` 180/192/512: **no hay** en este repo; el juego lleva el favicon de Vite y el Instalador su propio icono (gema de cristal sobre madera, 32/128/512 px y `fuente.png` 1024, desde `36ff771`): sustituirlos por el símbolo elegido es una propuesta a esos repos, no se hace desde aquí | repo (`examples/tarkor/piezas.json`); `icon` **[P]**; WMF (`frontend/public/favicon.svg`); Instalador (`app/src-tauri/icons/`) |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos: 166/5/79 % frente a 155/7/78 % del definitivo, mismo estilo y hueco. `draft: {scale: 0.5, steps: 4}` **declarado** en `og` | repo (`galivelop-images.json`; F2.10, dec. 7; `docs/records/contenido/r3-borrador.md` l.49) |
| Velo por perfil | Rec. | `og`, `cuadrado`, `vertical`, `cabecera`: `#f1e4d0:0.55`; `og-bajo` (pieza oscura): `#221c16:0.45` | repo (`examples/tarkor/piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza, en lo alto de la caja de la zona con el título debajo, margen 6 %; `-claro` sobre velo claro, normal sobre velo oscuro | repo (`examples/pilot/componer.py` l.129-137; `piezas.json` `logo`) |
| Palancas extra | Opc. | **referencias de sujeto:** los 304 `.webp` del Portal valen para `-r` (fija el sujeto, +60 %, no da acabado ni paleta); no se usaron en r1-r5. **LUT:** el juego tiene `estilo/lut/{dia,atardecer,noche}.cube` y `gradar.sh` (firma sha1); F2.11 trae `compose.lut` con huella, **sin LoRA**, para cuando r2-luz no baste. **LoRA `wmf-estilo`** (134 banners, rank 16, 161 MB sin versionar): satura la escena cálida (27,7 → 34,2) y no la gris (6,6 → 5,8); queda para F5 en el perfil, aprobado 2026-11-04. **Conversión final:** la portada del Portal es `.webp` 1600×640 (fuera de `gimg`, D35) | repo (`docs/plan.md` l.254, l.649-650, l.872; `docs/records/lectura-2026-11-04-tarkor.md`; `lectura-2026-11-02-tarkor.md`; `docs/handoff.md` l.36); WMF-imagenes (`estilo/lut/`, `scripts/gradar.sh`) |
| Prioridad | Rec. | la de la biblia: 1) logo y paleta; 2) `og` 1200×630 nuevo; 3) `banner` 1600×640 del Portal y cabecera 960×540 de Discord; 4) `square` con el lema; 5) `avatar` e `icon`. Hechas en el piloto, sin «sí»: `og` (r4), `og-bajo`, `cuadrado`, `vertical`, `cabecera` 1500×500 y `avatar` (r5); `banner`, `social`, Discord e `icon`, sin hacer | **[P]** (`biblia.md` §9; `docs/plan.md` l.657-660; `piezas.json`) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | `og`: «El mundo sigue aunque tú te detengas.» (37 caracteres): variación del lema, no el lema literal (70, no cabe en una línea a un tercio del og). Compuesto en r4 (11,26:1) | **[P]** (`examples/tarkor/piezas.json` `og.titulo`; `biblia.md` §6 l.86 «Variaciones [P]») |
| Subtítulo | Rec. | «RPG narrativo de fantasía con IA local. En desarrollo, a la vista.» (64) | **[P]** (`piezas.json` `og.subtitulo`; `biblia.md` §6 l.88 «Cierres [P]») |
| Variaciones, ganchos y cierres | Rec. | variaciones: «Deja la partida. El mundo sigue.» (`cuadrado`); ganchos: «Lo que no hagas, lo hará otro.» (`vertical`), «Madera, hierro y cristal.» + «Y un mundo que no te espera.» (`cabecera`); cierres: «Juega en local. Nadie mira.», «En desarrollo, a la vista.». El `vertical` lleva el lema literal como subtítulo (70) y cupo (peor 4,98) | **[P]** (`biblia.md` §6 l.86-88; `piezas.json`) |
| Longitud máxima por campo | Rec. | orientativo ≤ 40 el titular (el más largo compuesto: 37) y ≤ 70 el subtítulo (el lema, 70, cupo en `vertical`); la fija la plantilla cuando exista `compose` | *(suposición)* (`piezas.json`; `r5-piezas.md` l.33) |
| Wordmark compuesto como texto | Opc. | no: el nombre va en el lockup SVG (`<text>` Cinzel 700 hasta que se pase a trazos) | repo (`tarkor-a-lockup.svg`) |

## 11. Entrega

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Carpeta de entrega | Obl. | `entrega` (relativa a `examples/tarkor/`, en `.gitignore`, D35). El destino real de cada pieza está en otros repos (sección siguiente): `gimg` no escribe en ellos; la copia la hace la persona o una propuesta | repo (`examples/tarkor/galivelop-images.json`, `delivery.dir`) |
| Nombre del archivo | Rec. | `{key}-{profile}.png` (el valor por defecto) → `estilo-og.png` | repo (`galivelop-images.json`, `delivery.template`) |
| Dónde se publica cada pieza | Rec. | **Portal, ficha de Tarkor:** `public/proyectos/tarkor/portada.webp` 1600×640 (**consta**, Portal `aa76b34` vía biblia; novedades en `src/data/proyectos/tarkor.json`, `guia-canales.md` §Portal). **og:image del juego:** `frontend/index.html` **no consta** (sin `og:`; el repo es privado y no hay web pública del juego). **Social preview de GitHub:** WMF, no comprobable (privado); Instalador, no consta. **X** (cabecera 1500×500, tarjeta 16:9), **LinkedIn**, **Reddit**, **Discord** (servidor de Galivelop, `guia-canales.md` §Discord): canales declarados, **ninguna pieza consta** en los repos. **Icono de la app:** Instalador `app/src-tauri/icons/` (**consta**, pero es otro dibujo) | repo (`biblia.md` §10); WMF (`docs/difusion/guia-canales.md` §X, §LinkedIn, §Reddit, §Discord, §Portal, §Imágenes; `frontend/index.html`); Instalador (`app/src-tauri/icons/`) |
| Otras piezas de marca que hace otro sistema | Rec. | **1) `gw-media-content` en WMF** (`.claude/gw/gw-media-content.md`): tarjetas y diagramas HTML → imagen de **1600×900**, una por idioma (`es`, `en`), con **la paleta oscura del Portal** (fondo `#06121c`, superficie `#0c1d2b`, borde `#1b3447`, texto `#eaf4fa`, celeste `#1aa6df`) y **DejaVu Sans / Liberation Sans**: ni un hex de Tarkor ni Cinzel. Esta hoja debería ser su fuente: ver «Contradicciones», 5. **2) `image-generator/` de WMF-imagenes:** banners 1280×512 por región y fichas para el juego, con su `mundo.json`, LUT y los hex de `index.css`; son imágenes **del juego**, no de marca, y no se tocan desde aquí. **3) El Instalador** dibuja su icono por su cuenta | WMF (`.claude/gw/gw-media-content.md` l.23-28); WMF-imagenes (`image-generator/estilo/mundo.json`, `scripts/`); Instalador (`app/src-tauri/icons/`) |
| Manifiesto | Opc. | `galivelop-images.manifest.json` (por defecto) | repo |
| Conversión final | Opc. | Portal: `.webp` 1600×640 (portada) y 1600 px + `-mini` 720 px (novedades); fuera de `gimg` (D35) | repo (`biblia.md` §10); WMF (`guia-canales.md` §Imágenes) |

## 12. Aceptación

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona; se apunta en `docs/records/contenido/rN-<tema>.md`. Dado hasta hoy: r1 **«no»** sin motivo (2026-10-26). r2-r5 del piloto: medidas del agente, sin veredicto; r2-luz, sin medir | repo (`docs/records/contenido/r1-fondos.md` l.49, l.52; `r2-estilo.md`; `r5-piezas.md`; `docs/handoff.md`) |
| Contraste del texto | Rec. | ≥ 4,5:1 (3:1 en titulares grandes). Medido: og r4 11,26 (peor 6,97); og-bajo 9,5 (7,36); cabecera 11,39 (6,89); cuadrado 6,28 (**5,18**); vertical 7,22 (**4,98**): los dos últimos pasan AA, no AAA, y son los que tienen la caja fuera de la zona | repo (`r4-composicion.md` l.19; `r5-piezas.md` l.33, l.41-43) |
| Umbrales de medida | Rec. | paleta **≥ 30 %** (sección 3); YAVG **105-150** y SATAVG **18-32** (sección 7). Hoy pasa la paleta y no pasan ni YAVG ni SATAVG en ninguna pieza del estilo elegido | repo (`calibracion-measure.md` l.69) |
| EMD frente a la marca | Opc. | Cb ≲ 6 y Cr ≲ 7,5 (medianas; son los de aceptación del propio juego, `gradacion.json`). Medido frente a `portada.webp`: r1 Cb 4,7 / Cr 5,1 y 4,6 / 9,9 (cerca); r5 Cb 6,8-8,1 / Cr 19-20; og-bajo 12,3 / 22,3 (lejos: el estilo elegido se aleja de la portada en color). La EMD de Y (14,7 r1; 45-50 r5; 61,3 og-bajo) pesa la composición y no se usa sola | repo (`calibracion-measure.md` l.32-34, l.69); WMF-imagenes (`estilo/gradacion.json`) |
| Cuándo se da por bueno el estilo | Opc. | regla del plan para r2 luz: si Tarkor no entra en 105-150 / 18-32, la ronda cuenta como sin mejora y la segunda la decide la persona (otro prompt, LUT de F2.11 o aceptar la marca desaturada). Propuesta de cierre: `og` y `square` con «sí» de la persona y dentro de los rangos, o «sí» con los rangos corregidos por ella | repo (`docs/plan.md` l.796-798); cierre **[P]** |

## 13. Fuentes de verdad

**World-Maker-Fantasy** (WMF), `claude/narrador-tiempos` `e3778e61` (leído solo; nada modificado; la biblia cita `73965f62`
y `git diff --stat` entre los dos no toca `index.css`, `assets/fonts`, `index.html`, `02-decisiones.md` ni
`tarkor-contenido-web.md`; `Home.tsx` solo cambia un botón de administración; `00-nucleo.md`, una línea):

- `frontend/src/index.css` l.9-14 (`--font-sans` Inter, `--font-serif` Cinzel, `--font-mono` Cascadia Code), l.23-54 (madera
  950-100, hierro 900-700, cristal `accent` 300-600 «tematizable por mundo», acero `accent2`, musgo), l.56-70 (`danger`,
  `cost`: solo interfaz), l.113-117 (`body`: fondo madera 950, texto hueso, Inter), l.226-234 (`.accent-hairline`), l.246-254
  (`.gem`), l.324-348 (`.rivet`).
- `frontend/src/pages/Home.tsx` l.24-33 (filetes, gema, eyebrow «Tarkor» 0,3 em en `accent-400`, `<h1>` `font-serif`
  en hueso).
- `frontend/src/assets/fonts/` (`cinzel-latin(-ext)-wght-normal.woff2`, `inter-latin(-ext)-wght-normal.woff2`, `fonts.css`
  @fontsource-variable 5.3.0, `LICENSE-Cinzel.txt`, `LICENSE-Inter.txt`); `frontend/index.html` (`<title>Tarkor</title>`,
  `lang="es"`, sin `og:`); `frontend/public/favicon.svg` (rayo de Vite, `#863bff`).
- `docs/producto/02-decisiones.md` nº 6 (2026-07-16: base «madera + hierro», acentos tematizables por mundo; Helek Sirik
  azules y grises); `docs/producto/tarkor-contenido-web.md` l.31-35 (Steam Deck, sin conexión, español, alpha e hito 0.3,
  creador), l.40 (lema), l.41-42 (línea del juego), pilares 5 y 8.
- `docs/difusion/guia-canales.md` l.3-4 (voz), §X, §LinkedIn, §Reddit, §Discord, §Portal, §Imágenes (1600×900, WebP del
  Portal); `.claude/gw/gw-media-content.md` l.23-28 (paleta del Portal y fuentes de las tarjetas).
- `docs/canon-opencode/00-nucleo.md` l.37-43 («Tono prohibido»), QA-274; `docs/rpgtarkor/lore-mundo/genesis.md` l.146-155 («El
  cielo sin luna»); `docs/rpgtarkor/lore-mundo/regiones/llanuras-del-viento-rojo.md` l.376-385 (Los Pilares Rotos);
  `docs/producto/plan-imagenes/guia-visual-mundo.md` §1.5 y §2; `docs/producto/plan-imagenes/plantilla-prompt.md` l.15-22.
- **No existe** en el repo: logo, lockup, og:image, favicon propio, social preview declarado, piezas publicadas (`docs/media`).

**WMF-imagenes**, `claude/plan-imagenes` `8a48fe52` (leído solo): `image-generator/estilo/mundo.json` (preámbulos día /
atardecer / noche «vivid, saturated natural colours…»; estilos banner / icono / fotorreal «rich natural colour… epic, hazy,
grounded»; regiones; l.146-152 `vetadas` y `negaciones` como regex); `estilo/gradacion.json` (aceptación EMD Cb ≲ 6 / Cr ≲ 7,5;
ventanas plan 70-95 / 15-30, día 103-133 / 12-17, noche 31-52 / 2-10); `estilo/lut/{dia,atardecer,noche}.cube`; `scripts/`
(`generar.sh`, `gradar.sh`, `medir.sh`, `montar.sh`, `planos.sh`); sin versionar: `bin-nuevo/` (sd-cli `master-1039`), `loras/`
(`wmf-estilo`, 161 MB).

**WMF-fichas**, `claude/fichas-banners` `d77142b4` (leído solo): mismo frontal e `index.css` que WMF; nada propio de marca.

**Instalador-WMF-Tarkor**, `main` `a73f881` (leído solo; **repo público**): `README.md` (dice que el repo del juego es
privado); `app/src-tauri/tauri.conf.json` (`productName` «Tarkor»); `app/src-tauri/icons/` (`32x32.png`, `128x128.png`,
`icon.png` 512, `icon.ico`, `fuente.png` 1024; desde `36ff771`); `docs/11-diseno-del-frontal.md` l.14-15 (reutiliza los tokens de
`index.css`, acento azul de Helek Sirik, Cinzel títulos, Inter texto); `diseno/prototipo-asistente.html` l.1-25 (tokens copiados,
`color-scheme: dark`, Cinzel e Inter de Google Fonts).

**`plan-imagenes-tarkor`**: carpeta sin git; copia de WMF `docs/producto/plan-imagenes/` (se cita la de WMF).

**Portal-Galivelop** `aa76b34`, solo a través de `biblia.md` §10: `src/data/proyectos/tarkor.json` l.7 (acento `#E0703A`),
`public/proyectos/tarkor/portada.webp` (1600×640), `public/proyectos/tarkor/arte/` (304 `.webp`), `public/marca/gv-logo.svg`
(baldosa).

**Este repo**, `f2-motor` `5460d2c`:

- `examples/tarkor/galivelop-images.json` (`name`, `brand.palette` de 10 hex: `#8a9aa8`, `#221c16`, `#332415`, `#E0703A`,
  `#f1e4d0` y, desde el 2026-11-04, `#241a10`, `#8a3b1e`, `#a3814f`, `#52626f`, `#4aa8d8`; `delivery`; perfiles `og`, `social`, `banner`, `square`, `header` y `portrait`, con destino salvo `social`, y `draft` en `og`;
  actualizada el 2026-11-04 con esta hoja).
- `examples/tarkor/piezas.json` (Cinzel / Inter; `og`, `og-bajo`, `cuadrado`, `vertical`, `cabecera`, `avatar`: fondo, logo,
  textos, zona, color de texto y velo).
- `examples/tarkor/prompts/`: `og.txt` (r1, «no»), `r2-palabras.txt`, `r2-hex.txt` (= `estilo.txt`, elegida), `r2-material.txt`,
  `r2-luz.txt` y `r2-luz-r1.txt` (r2 luz, sin medir), `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt`, `r5-og-bajo.txt`;
  `orders/r1-og.json`, `r2-control.json`, `r2-luz.json`, `r2-luz-r1.json`.
- `docs/marcas/tarkor/biblia.md` (`a50b544`, movida en `74d99f8`), `docs/marcas/tarkor/logos/` (a-d con lockups; `tarkor-a.svg`
  `c63761f`), `docs/marcas/README.md` l.16, l.33, l.37, l.84, l.161-170 y «Común a todos».
- `docs/records/contenido/r1-fondos.md` l.49, l.52, l.68-69; `r2-estilo.md` l.36-38, l.52, l.64-69; `r3-borrador.md` l.49;
  `r4-composicion.md` l.19, l.47; `r5-piezas.md` l.33, l.41-43, l.69; `calibracion-measure.md` l.31-34, l.48-51, l.69, l.76.
- `docs/plan.md` l.254, l.257-261, l.578-592, l.646-660, l.773-798, l.872-873, l.880, l.893; `docs/handoff.md` l.36, l.52;
  `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.293-327, `lectura-2026-11-02-tarkor.md`, `lectura-2026-11-04-tarkor.md`.
- `examples/pilot/componer.py` (l.14, l.29, l.129-137, l.190-196), `examples/pilot/fuentes.sh` l.11-15; `piloto/fuentes/` no
  existe en esta máquina.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo; lo de WMF y el Instalador va como propuesta a
esos repos):

- Hecho el 2026-11-04: destinos (`og` 1200×630, `square` 1080×1080, `header` 1500×500, `banner` 1600×640, `portrait` 1080×1350),
  `draft` en `og` y `brand.palette` con `#241a10`, `#8a3b1e`, `#a3814f`, `#52626f` y `#4aa8d8` (fuera a propósito: `#1b130c`,
  la banda que sale, y `#f2b34a`, solo si r2-luz-r1 gana).
- Falta: `social` y `banner` declarados y nunca generados; el 16:9 de 1600×900 que pide `guia-canales.md` no tiene perfil;
  Discord 960×540 y LinkedIn 1584×396 tampoco (perfiles aparte cuando se pidan).
- `compose`: plantilla, fuentes, zona, velo y logo viven en `examples/pilot/componer.py` y `piezas.json`; sin `compose`.
- `estilo.txt`, `r2-hex/palabras/material.txt`, `r5-*.txt` y `og.txt` nombran «sun» contra la pauta del 2026-11-02; `estilo.txt`
  pide «muted»; `r5-cuadrado/vertical.txt` piden «lower third»; `og.txt` lleva además «golden hour», «nearly empty» y «Shot on a
  full-frame camera with a 35mm lens». **Son históricos** (no se tocan) y se rehacen con la hoja; `r2-luz.txt` es el candidato
  a `estilo.txt` (decidido). El pedido `r2-control.json` conserva «sun» (el test del repo lo ata byte a byte a `prompts/r2-hex.txt`, histórico).
- Copia de los logos en `examples/tarkor/logos/`: pendiente (F2.10, dec. 3); los `logo` de `piezas.json` apuntan a
  `docs/marcas/tarkor/logos/`.
- `piloto/fuentes/` no existe aquí: `fuentes.sh` no se ha corrido en esta máquina; las piezas de r4-r5 se compusieron donde sí.
- En WMF: la nota de `gw-media-content` lleva la paleta del Portal, no la de Tarkor (ver «Contradicciones», 5); sin og:image;
  favicon de Vite. En el Instalador: icono del concepto b.

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; es la línea del juego en `tarkor-contenido-web.md`) |
| 3 | «Nunca se muestra» no vacío | pasa (la lista más larga de los seis proyectos: el canon reserva mucho); nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | pasa (10 hex); texto `#221c16` y `#f1e4d0`, acento `#E0703A`, fondo claro `#f1e4d0` y fondo oscuro `#241a10` están |
| 5 | Símbolo SVG válido | pasa a mano (`viewBox="0 0 128 128"`, `<title>`, sin `<text>`/`<image>`/`filter`; «sí» a 16 px solo según la tabla de la biblia §4, no visto por la persona); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: sin `compose.fonts`, y `piloto/fuentes/` no existe en esta máquina (`fuentes.sh` sin correr); el lockup usa `<text>` Cinzel y saldría en la reserva `serif` |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida; Motivos Sí es **[P]** entero |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | `r2-luz` y `r2-luz-r1` **pasan** la lista de esta hoja; `r2-control` no (`r2-control` conserva el «sun» histórico de `r2-hex.txt`; «muted» no es palabra vetada). Los prompts históricos con «sun» (`r2-hex.txt` y su pedido, `estilo.txt`, `r2-hex/palabras/material.txt`, `r5-*.txt`, `og.txt`) no pasan y se rehacen |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (129-241 palabras), los once |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | pasa: múltiplos de 64 en los seis y destino declarado en todos los que lo tienen distinto (`social` es igual y no lo lleva) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | zona decidida (og/social/banner `izquierda 1/3`, `header` `izquierda 1/2`, `square`/`portrait` `abajo 1/2`); ningún perfil la declara aún (hueco de `compose`); los prompts de `square` y `portrait` piden todavía 1/3 (históricos, por rehacer) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (37 caracteres; r4 compuesto; 70 del lema cupo como subtítulo en `vertical`) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | pasa: `#241a10`, `#8a3b1e`, `#a3814f`, `#4aa8d8`, `#f1e4d0`, `#221c16` y `#E0703A` están |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | pasa: `og` 1200×630, `banner` 1600×640, `square` 1080×1080, `header` 1500×500 y `portrait` 1080×1350 declarados; `social` es igual y no necesita destino |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 18** (familia propia):
**14 salen de un repo o de una decisión** (el acento ya está decidido) y **4 son [P]** aprobadas por delegación (fondo por roles, dibujo del símbolo, motivos Sí, titular).

## 15. Huecos que tocan a este proyecto

De los catorce de la plantilla, le afectan **todos menos uno**: roles de la paleta (`brand.palette` no distingue el fondo
oscuro del tablón ni el acento de marca del secundario), zona reservada (solo en prompt y en `componer.py`, y con la caja
descasada en `square`/`portrait`), velo y logo en la pieza (solo en `componer.py`), palabras vetadas y motivos No sin campo (y
ocho prompts con «sun»), umbrales (en `calibracion-measure.md`), `avatar` e `icon` sin perfil, **dos variantes de lockup** (clara y
oscura, que obligan a dos perfiles o dos plantillas), tipografía con licencia y archivo en otro repo (y sin instalar aquí),
imágenes de marca para la EMD sin lista (la portada del Portal, pendiente de que la persona la dé por marca), longitud máxima
de texto, idiomas (`es` en las piezas; `es`/`en` en las tarjetas de Workflow; `es`/`gl`/`en` en el Portal), `compose.lut`
(F2.11, es el proyecto que lo pide) y copia de los logos en `examples/<p>/logos/`. No le afecta `style.lora` hasta F5.

**Huecos propios de este proyecto, que la plantilla no lista:** 1) la paleta de referencia es la del **producto** (un juego
oscuro único) y la marca necesita una pieza clara que el producto no tiene: la hoja la declara, ningún campo dice de dónde sale
cada rol; 2) **la hoja apunta a cuatro repos** (juego, imágenes, instalador, Portal) y uno es privado: «publicada dónde» no se
puede comprobar para el social preview ni para el og:image del juego; 3) el proyecto tiene **su propio generador de imágenes**
(WMF-imagenes) con otros rangos y otro estilo: la hoja tiene que decir cuál manda en marca (esta) y cuál dentro del juego
(aquel), y la plantilla no tiene fila para «el producto genera sus propias imágenes con otras reglas».

---

## Contradicciones

Entre los repos de Tarkor y la biblia (`a50b544`), o entre la biblia y lo que ya generó el motor. Todas **resueltas el
2026-11-04** por delegación, con el criterio de [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md) (lo publicado manda sobre lo que está en desarrollo; lo compuesto, visto y medido sobre lo escrito; una zona por perfil; la propuesta de la hoja si no choca). La persona no ha visto ninguna pieza desde el «no» de r1.

1. **Zona del `header`.** Biblia §7: «un tercio izquierdo liso (og, banner, header)». `prompts/r5-cabecera.txt` pide «The
   left half of the frame» y la pieza medida (11,39:1, peor 6,89) se compuso así. **Propuesta:** `izquierda 1/2` en `header`
   (a 1500×500 un tercio son 500 px, menos que el alto: no cabe lockup, título y subtítulo); corregir la biblia.
   **Resuelta:** `header` a `izquierda 1/2`, lo del prompt y la medida (criterios 2 y 3); la biblia §7 se corrige.
2. **Zona de `square` y `portrait` frente a la caja.** Biblia y prompts: tercio inferior («The lower third»). La caja del
   piloto ocupa el 48 % del alto (`componer.py`), así que el texto pisa el sujeto: son las dos piezas más justas de r5 (peor
   5,18 y 4,98, AA sin AAA). **Propuesta:** o el prompt pide «the lower half» (como en Workflow, `arriba 1/2` medido) o la
   caja baja a un tercio; lo decide una pieza medida en r2 con las dos; la hoja queda en `abajo 1/3` hasta entonces.
   **Resuelta:** `square` y `portrait` piden en el prompt la mitad libre (`abajo 1/2`), que casa con la caja del 48 % (criterio 3); la biblia §7 se corrige. Los `r5-cuadrado.txt` y `r5-vertical.txt` actuales son históricos hasta rehacerlos.
3. **«sun» en los prompts.** La pauta del 2026-11-02 (plan l.578-592, IMG-28: «sun» pinta el disco; se da la dirección sin la
   fuente) solo la cumplen `r2-luz.txt` y `r2-luz-r1.txt`; `estilo.txt` (el elegido), los tres de r2, los cuatro de r5 y `og.txt`
   dicen «the first low sun» o «the low sun». **Propuesta:** `sun` entra en la lista vetada de la hoja (sección 6); `r2-luz.txt`
   pasa a `estilo.txt` si r2-luz mide igual o mejor; los demás se marcan históricos en `biblia.md` §8 hasta rehacerlos.
   **Resuelta:** `sun` vetada; `r2-luz.txt` es candidato a `estilo.txt`; los prompts con «sun» se marcan históricos en la biblia §8. `r2-control.json` sigue con «sun» porque es copia exacta de `prompts/r2-hex.txt` (histórico; lo exige `tests/test_examples.py`), y se rehará con él; `r2-luz.json` y `r2-luz-r1.json` ya cumplen.
4. **«natural muted colours» frente a lo que se mide.** El estilo elegido pide colores apagados (guía visual del mundo §1.5,
   [propuesta] allí) y la aceptación pide SATAVG 18-32 (la portada, 25): el prompt pide lo que la medida penaliza, y las piezas
   dan 5-8. El juego genera sus banners con «vivid, saturated natural colours» y «rich natural colour» (`mundo.json`) y el LoRA
   sube la saturación solo en escena cálida. **Propuesta:** la línea de estilo pasa a «rich natural colour» (lo que prueba
   `r2-luz-r1.txt`) y «muted» sale; si r2-luz no entra en 18-32, LUT de F2.11; la biblia §7 «Sí» se corrige con el resultado.
   **Resuelta:** «rich natural colour» en lugar de «natural muted colours» en la línea de estilo (LUT de F2.11 si no basta). Los pedidos `r2-control` y `r2-luz` conservan «muted» a propósito: son el contraste de `r2-luz-r1`, que prueba «rich natural colour» (la prueba pierde sentido si se igualan).
5. **Las tarjetas de Tarkor salen con la paleta del Portal.** `.claude/gw/gw-media-content.md` de WMF manda las tarjetas y
   diagramas (1600×900, `es` y `en`) con fondo `#06121c`, celeste `#1aa6df`, texto `#eaf4fa` y DejaVu Sans: ni madera, ni hueso,
   ni arcilla, ni Cinzel. Esta hoja es la fuente de los hex de `gw-media-content` (fila «Otras piezas», plantilla §11).
   **Propuesta:** proponer a WMF (desde aquí no se modifica) una `Palette:` con `--background: #241a10; --surface: #1b130c;
   --border: #46311d; --text: #f1e4d0; --muted: #8a9aa8; --accent: #E0703A; --accent-text: #f1e4d0; --good: #8fae6a; --bad:
   #f87171` y `--font: Cinzel` para títulos e `Inter` para texto (las de `frontend/src/assets/fonts/`, sin red); `#f87171` es el
   `danger-400` del juego, el único rojo que tiene.
   **Resuelta:** la hoja es la fuente de los hex; la `Palette:` se propone a WMF (criterio 5: desde aquí no se modifica ese repo).
6. **Fondo oscuro: tres hex.** Biblia §2: fondo de pieza oscura madera 900 `#241a10` y, sobre imagen, «banda de madera 950
   `#1b130c` al 70 %» [P]. El og-bajo se compuso con velo hierro `#221c16:0.45` (9,5:1) y `brand.palette` lleva `#332415`, no
   `#241a10`. **Propuesta:** pieza plana oscura `#241a10`; velo sobre imagen `#221c16:0.45` (lo medido); `#241a10` entra en
   `brand.palette`; la banda al 70 % sale de la biblia.
   **Resuelta:** fondo oscuro plano `#241a10`, velo `#221c16:0.45`, `#241a10` en `brand.palette` (ya está) y la banda `#1b130c` al 70 % fuera.
7. **Rangos de luminosidad: marca frente a juego.** Esta hoja: YAVG 105-150 y SATAVG 18-32 (la portada). El juego acepta sus
   banners en 70-95 / 15-30 (ventana del plan) o 103-133 / 12-17 (día) y `r5-og-bajo` buscó 70-95 (`biblia.md` §8). **Propuesta:**
   la marca mide contra la portada (es lo publicado) y los rangos del juego solo guían la LUT; la biblia §8 deja de citar 70-95
   como objetivo de marca.
   **Resuelta:** la marca se mide contra la portada del Portal, que es lo publicado (criterio 1); los rangos del juego solo guían la LUT.
8. **El eyebrow de la Home no es Cinzel.** Biblia §3: «Cinzel 400 con tracking 0,3 em en filetes y eyebrows, como el título de la
   Home». En `Home.tsx` l.31 el `<p>` «Tarkor» lleva `text-xs tracking-[0.3em] uppercase text-accent-400` y **no** `font-serif`:
   hereda Inter del `body`. **Propuesta:** la hoja fija el wordmark en Cinzel 700 a 0,18 em (el lockup) y, si se quiere un
   eyebrow, Inter 500 en mayúsculas a 0,3 em como en el juego; la biblia corrige la frase.
   **Resuelta:** el eyebrow es Inter; biblia §3 corregida. Pesos de la familia: titular 700, subtítulo Inter 400 con opacidad 0,82.
9. **Acento: arcilla en la marca, cristal en todo lo público del juego.** Lo único de Tarkor que ya se ve fuera (icono del
   Instalador, eyebrow y gema de la Home) es cristal; la marca propone arcilla. Delegado **[P]**; la biblia lo razona (§2
   l.39-44). **Propuesta:** arcilla fuera, cristal dentro, como está; y que el icono del Instalador pase al símbolo elegido
   cuando la persona lo apruebe (propuesta a ese repo).
   **Resuelta:** arcilla `#E0703A` en las piezas, cristal `#4aa8d8` dentro del juego, porque el Portal presenta a Tarkor en arcilla (decisión 3). El icono del Instalador (concepto b, cristal) queda como propuesta a ese repo.
10. **Cabecera de Discord.** Biblia §9: `header` «Discord 960×540». Lo hecho en r5 es la cabecera de X, 1500×500, y el README
    «Común a todos» da tres destinos al `header` (X, LinkedIn 1584×396, Discord 960×540). Un perfil lleva un destino.
    **Propuesta:** `header` → 1500×500 (X) con `targetWidth`/`targetHeight`; Discord (960×540, 16:9: no sale de un 3:1
    recortado) y LinkedIn (1584×396), perfiles aparte cuando se pidan.
    **Resuelta:** `header` 1500×500 con destino ya declarado; Discord y LinkedIn, perfiles aparte cuando haga falta.
11. **«A retocar» frente a «retocado».** `docs/marcas/README.md` l.16 y l.33 dicen que el logo a «se retoca» para que no se
    lea como una M; la biblia §4 dice «retocado» y el SVG de `c63761f` ya lleva las torres desiguales y el puente bajo.
    **Propuesta:** el README pasa a «retocado, pendiente de la persona»; si ella sigue viendo una M, se vuelve a dibujar.
    **Resuelta:** «retocado, pendiente de la persona» (cambio del README, que desde esta rama no se toca).
12. **La paleta del plan.** `docs/plan.md` l.653-655 lleva la paleta *suposición* de la portada (`#1b0f0a`, `#8a3b1e`, `#c98a3a`,
    `#efe3cf`, `#f2b34a`), superada por la del juego (`index.css`) desde la biblia; `r2-luz-r1.txt` recupera `#f2b34a` para el
    cielo. **Propuesta:** el párrafo del plan remite a esta hoja; `#f2b34a` entra en la paleta solo si r2-luz-r1 gana.
    **Resuelta:** el párrafo del plan remite a esta hoja (cambio de `docs/plan.md`, que esta tarea no toca); `#f2b34a` fuera de `brand.palette` hasta que r2-luz-r1 gane.

## Cambios que pediría a la plantilla

Todos modestos; ninguno bloquea la hoja.

1. **Palabras vetadas como patrones.** La fila (§6) pide «una por línea»; la lista del juego son regex (`\bscar(s|red)?\b`,
   `n't\b`) porque «scarred» o «don't» se cuelan con palabras sueltas. Que la fila admita patrones (y la comprobación 8 los
   use), o que diga que la hoja los desarrolla a mano, como hace esta.
2. **Perfiles con más de un destino.** La fila «Perfiles» (§9) da un destino por perfil y `gimg` también; `header` tiene tres
   (X, LinkedIn, Discord) y el 16:9 de los canales es otro. Que la fila diga cómo se escribe (un perfil por destino, con el
   nombre del canal) para no dejarlo a cada hoja.
3. **Producto que genera sus propias imágenes.** Tarkor tiene otro generador (WMF-imagenes) con otros rangos y otro estilo; la
   fila «Otras piezas de marca que hace otro sistema» (§11) cubre tarjetas de redes, no «el producto pinta sus imágenes con
   otras reglas». Una frase en esa fila: «si el producto genera imágenes propias, se dice qué manda en marca y qué dentro del
   producto».
4. **Repos privados en «publicada dónde».** La fila (§8 y §11) prevé «no comprobable» para el social preview de GitHub; con un
   repo privado nada de él es comprobable desde aquí (og:image, favicon, preview). Que admita «repo privado: no comprobable».

## Lo que enseñó rellenarla

**Balance de este proyecto:** 18 obligatorios (familia propia); **13 completos desde un repo** (WMF, WMF-imagenes, Instalador,
Portal vía biblia o este), **5 [P]** al redactarla (fondo por roles, acento, dibujo del símbolo, motivos Sí, titular); tras la aprobación por delegación el acento está decidido y los otros cuatro siguen [P]. De los 66 campos de la
plantilla, 19 eran **[P]** en todo o en parte (los cinco obligatorios, hoy cuatro porque el acento se decidió, tamaños y márgenes del logo, usos prohibidos, lockup a
trazos, vetadas añadidas, `portrait` y 16:9, `header` a 1/2, `compose`, `icon`, `draft`, prioridad, subtítulo, variaciones, la
portada como marca, regla de cierre), 3 *(suposición)* (dirección de la luz, momento y clima, longitudes: lo que r2-luz mide) y 2
«no hay» (`icon` y copia de logos, admitidos). De los recomendados, 3 no comprobables (fuentes instaladas, social preview y
og:image del juego).

**Diferencia con image-generator y Workflow:** aquí hay más repo que en ninguno (paleta de 30 hex, dos fuentes OFL empaquetadas,
canon, voz, canales, un generador y hasta un icono público) y a la vez **menos marca**: nada de lo que existe fuera del juego
(icono del Instalador, tarjetas de Workflow, favicon) usa lo que la biblia propone, y ninguna pieza del piloto tiene un «sí». Los
cinco [P] obligatorios son los cinco en que la marca se separa del producto: el producto es oscuro y la marca quiere una pieza
clara; el producto es cristal y la marca arcilla; el producto no tiene logo; el producto no tiene escena de marca; y el lema del
producto no cabe en un titular. Es el único proyecto en que **la medida contradice al prompt** (pide apagado, se exige 18-32) y
el único con dos sistemas (este y `gw-media-content` en WMF) pintando a Tarkor con paletas que no son la suya.
