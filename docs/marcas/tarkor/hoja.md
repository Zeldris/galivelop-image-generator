# Hoja de estilo mínima: Tarkor

**Aprobada el 2026-11-04** por delegación y **rehecha el 2026-11-10 con la dirección que la persona confirmó por sí misma** (los dos PNG de `examples/tarkor/logos/` y las diez decisiones de [`propuesta-fable-2026-11-10.md`](propuesta-fable-2026-11-10.md) §9; r7 queda archivada al final, en «Historia»); tercer caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md)
(F2.12), rellenada tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y
[`../galivelop-workflow/hoja.md`](../galivelop-workflow/hoja.md), con su misma forma, y el **primero de familia visual
`propia`** (18 obligatorios en vez de 15). Complementa a [`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es
lo que `gimg` necesita, campo a campo y en el orden de la plantilla. Estados como en [`../README.md`](../README.md): sin marca
sale de un repo (ruta en la sección 13); **[P]** es propuesta del agente **aprobada por delegación** (la persona no ha visto la pieza ni dado un «sí» propio), con su porqué en la misma celda;
*(suposición)* se comprueba en una ronda; «no hay» solo donde la plantilla lo admite. Aquí no hay «heredado de»: la paleta y
la letra son del juego; el acento que el Portal asignó (arcilla) dejó de ser el de la marca el 2026-11-10 (sección 0, «Hereda de»). Las filas con «aprobado por la persona, 2026-11-10» llevan su «sí» propio, no delegado.

Commits de referencia (2026-11-12): World-Maker-Fantasy (WMF, el juego; repo **privado** según el `README.md` del
Instalador) `main` `3a10a3fa` y, sin fusionar, `claude/marca-interfaz` `c858a150` (UX-40: la marca en la interfaz);
WMF-imagenes, clon del mismo origen (`image-generator/estilo/mundo.json` leído en su `origin/main`); Instalador-WMF-Tarkor
`main` `5631e77b` (repo público) y `claude/installer-docs-review-09e7vs` `34d2bb27` (su pedido de imágenes, doc 13);
Portal-Galivelop `aa76b34` (acento y portada, vía `biblia.md` §10; desde aquí no se abre ese repo); este repo, rama
`agent/hojas-tarkor`. Lecturas anteriores, de las que quedan citas de lore y de producto sin recomprobar (sección 13):
WMF `e3778e61` (2026-11-04) y `3537d84` (2026-11-10), WMF-imagenes `8a48fe52`, WMF-fichas `d77142b4`, Instalador `a73f881` y
`ce9f33a`. Los repos de Tarkor se han leído **sin modificar nada**.

**Lo primero que hay que saber:** la marca de Tarkor **se creó en este repo**: el juego tiene paleta y fuentes propias
(`frontend/src/index.css`, madera + hierro, Cinzel e Inter) pero en `main` (`3a10a3fa`) **ni logo, ni og:image, ni favicon propio**; el oro, la noche y el titular tallado están hechos en la rama `claude/marca-interfaz` (`c858a150`), sin fusionar (el `favicon.svg`
es el rayo violeta de Vite, `#863bff`, un color que la propia marca prohíbe). Lo único de marca que el juego ya enseña en
público es el icono de la app del Instalador (`app/src-tauri/icons/`): un rombo de cristal claro sobre un disco de madera
oscura, que es el concepto **b** (la gema) de la biblia, no el **a** elegido, y con el acento cristal, no el arcilla (el Instalador ya decidió sustituirlo por E14 sobre un disco de noche: su doc 13 §6.1, `608661d`). La persona
dio un **«no» a los fondos de r1 sin motivo** (2026-10-26) y desde entonces lo demás está delegado: todo lo que sigue del estilo
de imagen es hipótesis del agente, medida y ahora **aprobada por delegación** (2026-11-04), y el estilo sale **desaturado** en
todos los formatos (SATAVG 5-7 frente a los 18-32 de la portada); r2-luz y r2-luz-r1, que lo intentan arreglar, siguen
**sin medir**.

**Desde el 2026-11-10 ya no todo es delegación:** la persona vio los dos PNG de `examples/tarkor/logos/` (`Emblema dorado y
título TARKOR.png`, `Tarkor_ La semilla rota.png`) y dio un **«sí» propio** a esa dirección («la madera sostiene, el oro
remata») y a las diez decisiones de [`propuesta-fable-2026-11-10.md`](propuesta-fable-2026-11-10.md) §9. Las filas marcadas
«aprobado por la persona, 2026-11-10» son ese «sí»; **[P]** sigue siendo lo delegado. La saturación (SATAVG) queda como
problema de los **paisajes**; las piezas nuevas (emblema, tablones, noche, oro) no se miden con esa regla y aún no se han medido.

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Tarkor»: T mayúscula, el resto minúsculas. Así va en `<title>Tarkor</title>` del juego, en `productName` del Instalador y en el título del `README.md` del Instalador. «TARKOR» en mayúsculas solo como wordmark del lockup (y como eyebrow de la Home del juego, con tracking 0,3 em). El repo del juego se llama World-Maker-Fantasy: es el nombre del repo, no de la marca | WMF (`frontend/index.html`), Instalador (`app/src-tauri/tauri.conf.json`, `README.md`) |
| Nombre en código | Obl. | `tarkor` | repo (`examples/tarkor/galivelop-images.json`, `name`); coincide con `src/data/proyectos/tarkor.json` del Portal (vía biblia §10) |
| Fuente de verdad | Rec. | WMF `main` `3a10a3fa` y `claude/marca-interfaz` `c858a150` (paleta, fuentes y clases, comprobadas el 2026-11-12; lema, propósito, voz, canon y canales, leídos en `e3778e61` y sin recomprobar); WMF-imagenes (`estilo/mundo.json` releído el 2026-11-12 en su `origin/main`: preámbulo, estilos, vetadas; LUT y rangos del juego, de `8a48fe52`); Instalador `main` `5631e77b` y `34d2bb27` (icono público, `estilos.css`, y su pedido I1-I6 en `docs/13-hoja-de-estilos-e-imagenes.md`, `d9d33fe` y `608661d`); Portal `aa76b34` (portada; acento ya superado); este repo: los dos PNG de `examples/tarkor/logos/` (`Emblema dorado y título TARKOR.png`, `Tarkor_ La semilla rota.png`), [`propuesta-fable-2026-11-10.md`](propuesta-fable-2026-11-10.md) (dirección, paleta, sistema de logo, piezas E1-E18, decisiones), [`peticiones.md`](peticiones.md) (bloque común, negativo, nombres de archivo, perfiles, orden) y [`biblia.md`](biblia.md). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio el veredicto de r1 (2026-10-26, **«no» a Tarkor sin motivo**) y aprobó ese día «la paleta y el emblema propuestos y Cinzel (OFL) como tipografía del wordmark, provisional hasta r4»; después delegó las decisiones de marca del piloto («lo dejo en tus manos») y el 2026-11-04 las dudas de esta hoja, aprobadas con el criterio de [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md). **El 2026-11-10 decidió por sí misma:** confirmó la dirección de los dos PNG y aprobó las diez decisiones de la propuesta §9 (1 noche índigo fuera del juego, madera dentro; 2 cuatro puntos cardinales; 3 campo de cristal `#1f4a55`; 4 luz de la semilla en dos capas; 5 Cinzel 800 modificada; 6 arcilla fuera; 7 Steam solo cápsula, cabecera y principal; 8 avatar = emblema completo desde 64 px; 9 sin cursor; 10 bloque de tokens entero). Lo delegado sigue con **[P]**. El **canon del juego** no se decide aquí: tiene su dueño en WMF (creador: Álvaro García Graña) y esta hoja solo lo cita | repo (`docs/records/contenido/r1-fondos.md` l.52; `docs/plan.md` l.257-261; `propuesta-fable-2026-11-10.md` §9); WMF (`docs/producto/tarkor-contenido-web.md` l.35) |
| Fecha de la hoja | Rec. | `2026-11-12` (reglas con medida §16, cobertura §17, repos al día §18 y las siete decisiones de ese día; la del 2026-11-11 fue la afinada con la revisión del equipo de Tarkor y lo aprendido al generar con Z-Image: §4, §6, §9, §12; la del 2026-11-04 queda en «Historia») | — |
| Familia visual | Rec. | `propia`: fondo, texto, tipografía y escena son del juego. De la familia Galivelop toma **solo la baldosa del símbolo** (`rx` 30/128) y el acento que el Portal le asignó | repo (`docs/marcas/README.md` l.84; `biblia.md` §4-§5) |
| Hereda de | Opc. | Portal-Galivelop `aa76b34`: portada `public/proyectos/tarkor/portada.webp` (1600×640, Pilares Rotos; la sustituyen E2/E5 cuando existan). El acento que el Portal le asignó, arcilla `#E0703A` (`src/data/proyectos/tarkor.json` l.7), **ya no es el de la marca** (decisión 6): el Portal tendría que pasar a oro `#b8862b` (propuesta a ese repo; ver «Contradicciones», 13). Nada más | repo (`biblia.md` §10); Portal: pendiente |

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
| Fondo | Obl. | **dentro del juego (interfaz):** madera 950 `#1b130c` (cuerpo) con tablones madera 800 `#332415` / 700 `#46311d` y bandas de hierro 900 `#0e0b08` / 800 `#171310`; **fuera del juego (og, avatar, cabecera, cápsulas, hero):** noche índigo `night-950` `#0f1428` → `night-900` `#1a2140` (decisión 1); **pieza clara:** hueso `#f1e4d0` (madera 100), solo para documentos y la variante clara del logo. Salen la madera 900 `#241a10` plana y los velos sobre foto de r4-r5: la pieza de marca ya no es un paisaje velado | hex: WMF (`frontend/src/index.css` l.23-37); noche y roles: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 y §9.1) |
| Texto | Obl. | hueso `#f1e4d0` sobre noche y madera; hierro 700 `#221c16` sobre hueso; el **titular hero** en oro tallado (Cinzel 900, relleno `gold-300` `#f2c45a` → `gold-700` `#7a5a1e`, `text-shadow: 0 1px 0 #5a3a14`); sobre claro la tinta dorada es `gold-900` `#5a3a14`, nunca `gold-500`. Calculado (WCAG, aún no medido sobre pieza): hueso/`#0f1428` **14,55:1**; hueso/`#1a2140` 12,54; hueso/`#1b130c` 14,63; hueso/`#332415` 11,93; `#f2c45a`/`#0f1428` 11,14; `#b8862b`/`#0f1428` 5,63; `#221c16`/hueso 13,44; `#5a3a14`/hueso 8,17; `#7a5a1e`/hueso 5,06; `#b8862b`/hueso **2,58 (no vale)**; `#a8d8f0`/`#1f4a55` 6,34 | WMF (`index.css` l.23-37); oro y noche: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 y §7); contrastes calculados aquí, pendientes de medir |
| Acento | Obl. | **oro tallado `gold-500` `#b8862b`** (familia `gold-100…900`: `#ffe9a8` núcleo de luz, `#f2c45a` bisel, `#b8862b` cuerpo, `#7a5a1e` pátina, `#5a3a14` filo y contorno): «la madera sostiene, el oro remata», ≤ 10 % de la superficie y el brillo ≤ 5 %. **Arcilla `#E0703A` sale de la marca** (decisión 6; queda solo como tierra de Berig en los paisajes). El cristal `#4aa8d8` (`accent-*` del juego) sigue dentro del juego como gema y como campo (`crystal-deep` `#1f4a55`, decisión 3), nunca como acento de marca. Un solo acento por pieza: el oro | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4, §9.3 y §9.6); hex del juego: WMF (`index.css` `--color-accent-*`); Portal `aa76b34` sigue en arcilla (`tarkor.json` l.7): propuesta a ese repo |
| Acentos en imagen, en orden de peso y significado | Rec. | 1) oro tallado (`#b8862b`, bisel `#f2c45a`, pátina `#7a5a1e`): la **única luz** de la pieza, en las juntas de la Semilla, la estrella y los filos (M2); 2) cristal `#1f4a55` / `#4aa8d8` solo como campo del emblema o gema del juego (M3); 3) la noche índigo es fondo, no acento. Nunca arcilla; el oro es figura y el cristal campo: no compiten | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §2 M2-M3, §4); `peticiones.md` §1 «Paleta» |
| Resto de la paleta | Rec. | madera 950 `#1b130c`, 800 `#332415`, 700 `#46311d`, 600 `#5c4126` (veta), 200 `#e3cba8`, 100 `#f1e4d0`; hierro 900 `#0e0b08`, 800 `#171310`, 700 `#221c16`; piedra `stone-700` `#3a342d` (gajos de la Semilla) y `stone-500` `#6b6257`; noche `#0f1428` / `#1a2140`; cristal `crystal-deep` `#1f4a55`, claro `#2f6b7a`, `#4aa8d8`, `#a8d8f0`; acero `#8a9aa8` / `#52626f` (`accent2`, texto secundario del juego); `#ffd66b` solo como halo del núcleo; musgo, `danger`, `cost` y `quest` **solo semánticos en el juego**. Madera 400 `#a3814f` y 300 `#c9a877` dejan de ser de marca (eran el wordmark de r4-r7) | WMF (`index.css` l.23-54); nuevos: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 y §9.10) |
| Combinaciones | Rec. | **marca (fuera del juego):** noche `#0f1428` → `#1a2140` + emblema completo + wordmark en oro + texto hueso; **interfaz:** madera `#1b130c` + tablones `#332415` / `#46311d` + bandas hierro `#171310` + filetes `gold-700` / `gold-900` + texto hueso; **clara (documentos, logo claro):** hueso `#f1e4d0` + texto `#221c16` + oro en `gold-900`. Proporción **60/30/10**: madera o noche / hierro y piedra / oro (brillo ≤ 5 %, cristal ≤ 10 %); se mide con `gimg measure --family` (ejemplo en C7). Los velos de r4-r7 sobre paisaje **salen** | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 «Proporción», §9.1); `peticiones.md` §1 |
| Prohibidos | Rec. | negro `#000` y blanco `#fff` puros; morado y violeta (luz reservada del canon; el `#863bff` del favicon de Vite que el juego aún lleva); neón; cromo y «lens flare»; brillo o halo por encima del 5 %; arcilla `#E0703A` en lo de marca; más de un acento por pieza; `gold-500` como tinta sobre claro (2,58:1); degradados fuera del bisel del oro, la gema y el cielo de noche; azules corporativos | repo (`biblia.md` §2); **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 y §7); WMF (`frontend/public/favicon.svg`; `00-nucleo.md` «luz morada» reservada) |
| Degradados | Opc. | el bisel del oro `gold-300` `#f2c45a` → `gold-700` `#7a5a1e` (wordmark, `.title-gold`, filos); el campo de cristal `#1f4a55` → `#2f6b7a` detrás del emblema y en la gema (`accent-300 → accent-600` sigue en `.gem` del juego); la noche `#0f1428` → `#1a2140` → `#0e0b08` (`.crystal-sky`); nada más | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4-§5); WMF (`index.css` l.246-254, l.269-286) |

**Medido:** la calibración del 2026-11-02 (umbral de paleta ≥ 30 %, portada del Portal 42 %; r1 7-12 %, r4-r5 50-84 %) sigue
valiendo para los **paisajes** (`og` y `banner` de fondo). Las piezas nuevas (emblema, tablones, noche, oro) **no se han
medido**: los contrastes de la fila «Texto» son calculados, y el porcentaje de paleta se medirá cuando `brand.palette` lleve
la paleta nueva (sección 13). La saturación baja de r1-r5 era un problema del paisaje, no de la marca: con el oro como única
luz, el criterio de la pieza de marca es la proporción 60/30/10, no el SATAVG.

## 4. Logo

*Dirección del 2026-11-10 (aprobada por la persona): el emblema de la Semilla rota con la estrella, por los dos PNG de `examples/tarkor/logos/`. Los SVG los genera gimg (D37, `gimg brand system`; `peticiones.md` §5 paso 2), nunca se dibujan a mano: desde el 2026-11-10 existen `tarkor-emblema.svg`, `tarkor-emblema-simple.svg`, `tarkor-emblema-mono.svg`, `tarkor-wordmark.svg`, `tarkor-lockup-h.svg` y `tarkor-lockup-v.svg` (trazados a dos tintas desde el boceto FLUX q185, el único con seis gajos); faltan el glifo, el monograma, las variantes `-claro` y la versión tallada con `feSpecularLighting`. `tarkor-a.svg`, `tarkor-a-lockup*.svg` y `tarkor-b-lockup*.svg` quedan en `logos/` como historia.*

**Regla que salió de la primera ronda (2026-11-11):** ningún modelo pinta el emblema real. Z-Image da el aro de oro y el campo de cristal, pero las juntas de la piedra salen en X o en cinco, no en seis; FLUX acierta los gajos y falla el aro. El `e04` rechazado («emblema falso») lo prueba: **nunca se pide al modelo un emblema, logo, wordmark ni «sello con el emblema» dentro de otra pieza**, ni se describe la zona libre por lo que irá encima («reserved for an emblem / a title»: el modelo lo pinta). En su lugar: la pieza se pide con la zona libre descrita como lo que es (cielo liso, madera lisa, cera lisa) y el emblema lo pone la composición desde los SVG (`compose.logo`, `piezas.py`) o, si tiene que ir en relieve dentro de la materia (E9 sello, #16 medallón, #26-38 fichas), **img2img desde el SVG rasterizado** sobre el color de la pieza (`initImage`, fuerza 0,35-0,45) *(suposición: se comprueba al rehacer E9)*. El emblema generado (`ui/01-emblema`, q175) vale solo como boceto del SVG.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/tarkor/logos/tarkor-emblema.svg` (**previsto**): la **Semilla rota con la estrella**: aro de oro tallado (círculo r 100, aro 14) con **cuatro puntos cardinales** de 36 más allá del aro (decisión 2); dentro, el disco de piedra `#3a342d` (r 58) partido por tres cortes de 6 a 0°/60°/120° en seis gajos, y entre los gajos **juntas de luz** (`gold-300` `#f2c45a` con núcleo `gold-100` `#ffe9a8`, decisión 4: dos capas); sobre el centro, la estrella de cuatro puntas 28×16; luz a 45° desde arriba a la izquierda (M5: tres valores de luminosidad y contorno bronce `gold-900` `#5a3a14` de 1-2 px); campo de cristal `#1f4a55` opcional detrás (decisión 3). `viewBox` cuadrado con margen (p. ej. `0 0 288 288`), `<title>Tarkor: la Semilla rota</title>`, sin `<text>` ni `<image>`; `feSpecularLighting` solo en la versión ≥ 40 px. **`tarkor-emblema-simple.svg`:** aro, gajos y estrella en `gold-500` `#b8862b` plano sobre `wood-950` `#1b130c`, para favicon 16-64 px. **`tarkor-glifo.svg`:** solo asterisco y estrella, 16 px (M1, E16). Referencia pintada: `examples/tarkor/logos/Emblema dorado y título TARKOR.png`. Copia en `examples/tarkor/logos/`: los PNG y, byte a byte, `tarkor-emblema.svg` y los dos lockups | dirección y geometría: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §5 y §9.2-9.4); archivos: emblema, simple, mono, wordmark y lockups **generados el 2026-11-10** (dos tintas, sin bisel); glifo, monograma, `-claro` y versión tallada pendientes |
| Lockup (símbolo + nombre) | Rec. | `tarkor-lockup-h.svg` (previsto): emblema a la izquierda y wordmark «TARKOR» a la derecha, altura de la mayúscula 0,45 del diámetro del emblema, hueco 0,25 del diámetro, mínimo 160 px de ancho. `tarkor-lockup-v.svg`: emblema arriba, wordmark debajo (ancho 1,6 diámetros), el separador #9 entre ambos, mínimo 96 px de alto; es el de la og (E3) y la cápsula (E4). `tarkor-wordmark.svg`: Cinzel 800 **modificada y pasada a trazos** (decisión 5: remates en espina ≈ 8 % de la altura de la mayúscula, barra de la T con cuernos, pierna larga de la K, O como aro con la estrella, pierna de la R en espina); plano ≥ 20 px; tallado ≥ 40 px (`gold-300` → `gold-700`, `feSpecularLighting`, filo `gold-900`). `tarkor-monograma.svg`: la T sola, dentro del aro simplificado (avatar pequeño) o sola (viñeta). Referencia pintada: `examples/tarkor/logos/Tarkor_ La semilla rota.png` (letras del modelo: referencia, no pieza). Sin `<text>`: no depende de fuentes instaladas | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §5 y §9.5); archivos pendientes |
| Variante clara y oscura | Rec. | **oscura** (normal): oro tallado sobre noche `#0f1428` o madera `#1b130c`; **clara:** oro en `gold-900` `#5a3a14` plano (sin bisel ni luz) y piedra `#3a342d` sobre hueso `#f1e4d0` (8,17:1); **mono:** un solo color (hueso o `#221c16`) para sello, grabado y cera (E9). Tres archivos por pieza, sufijos `-claro` y `-mono` | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §5); archivos pendientes |
| Tamaño mínimo y margen | Rec. | por debajo de 64 px, glifo o emblema simple; desde 128 px, emblema pintado o tallado; wordmark 20 px de alto plano y 40 px tallado; lockup horizontal 160 px, vertical 96 px; avatar: emblema completo desde 64 px (decisión 8). Margen libre = la altura de la T del wordmark | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §2 M1, §5 y §9.8) |
| Usos prohibidos | Opc. | nunca estirado, rotado, con sombra arrojada ni brillo fuera del bisel; nunca sobre morado, sobre arcilla ni sobre foto sin noche o madera debajo; nunca el emblema por debajo de 64 px (ahí va el glifo); nunca el wordmark como `<text>` ni con letras pintadas por el modelo; nunca el aro sin sus cuatro puntos; **nunca pedido al modelo** dentro de otra pieza, ni nombrado en un prompt (`emblem`, `logo`, `seal with the emblem`, `title`: regla de arriba y palabras vetadas, §6) | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §5); lo del modelo: revisión de Tarkor, 2026-11-11 |
| Logo fuera de la paleta | Opc. | el logo usa `gold-100…900`, `#3a342d`, `#1f4a55`, `#0f1428` y `#1b130c`: **ninguno está hoy en `brand.palette`**, que sigue con los diez hex de r7 (`#E0703A` incluido); al rehacer la configuración entran todos y salen `#E0703A`, `#8a3b1e` y `#a3814f` (sección 13) | repo (`examples/tarkor/galivelop-images.json` `brand.palette`, 2026-11-10: los 16 hex) |

## 5. Tipografía

*Dirección del 2026-11-10: Cinzel 800 modificada en el wordmark, Cinzel 700/900 en titulares, Inter en texto, Cascadia Code en cifras. Metamorphous, Almendra y New Rocker (r7) quedan fuera: ver «Historia».*

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Obl. | **Cinzel** (OFL): **800 modificada y a trazos** en el wordmark (decisión 5); **700** en los titulares de la interfaz del juego (cabeceras de `.plank-panel`, modales) y en los titulares compuestos de las piezas; **900** con `letter-spacing: 0.08em` y relleno de oro (`background-clip: text`, `gold-300` → `gold-700`, `text-shadow: 0 1px 0 #5a3a14`) solo en el **hero** (`Home.tsx` h1, E5). Reserva `serif`. Oro solo en wordmark y hero; el resto en hueso | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §7 y §9.5); WMF (`frontend/src/index.css` l.9-14; `pages/Home.tsx` l.30) |
| Familia de texto | Rec. | **Inter 400** (cuerpo y subtítulo de las piezas, opacidad 0,82); **Inter 500** en mayúsculas con tracking 0,3 em en el eyebrow; **Cascadia Code** en cifras y datos, solo dentro del juego. El lema bajo el lockup vertical (E3) va en Inter 400 hueso | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §7); WMF (`index.css` l.9-14, l.113-117) |
| Licencia y archivo | Rec. | Cinzel e Inter **OFL**, empaquetadas en el juego como variables (peso 400-900): `frontend/src/assets/fonts/cinzel-latin-wght-normal.woff2`, `cinzel-latin-ext-wght-normal.woff2`, `inter-latin-wght-normal.woff2`, `inter-latin-ext-wght-normal.woff2`, `fonts.css` (@fontsource-variable 5.3.0), `LICENSE-Cinzel.txt`, `LICENSE-Inter.txt`. En este repo las baja `examples/pilot/fuentes.sh` (`Cinzel[wght].ttf`, `Inter[opsz,wght].ttf`) a `piloto/fuentes/`, que **en esta máquina no existe hoy**; el wordmark a trazos no las necesita, el `compose` de E3 (lema en Inter) sí: `compose.fonts: ["Cinzel", "Inter"]` | WMF (`frontend/src/assets/fonts/`); repo (`examples/pilot/fuentes.sh` l.11-15; `componer.py` l.14, l.29) |
| Tracking y mayúsculas | Opc. | wordmark «TARKOR» en mayúsculas, Cinzel 800 modificada, con el espaciado dibujado en los trazos (sin `letter-spacing`); titular hero Cinzel 900 a 0,08 em; eyebrow «Tarkor» de la Home: Inter 500, `uppercase`, 0,3 em, en hueso (`text-wood-200`) en vez de `accent-400` (el cristal deja de ser acento); titulares de interfaz Cinzel 700 sin tracking extra | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §7); WMF (`pages/Home.tsx` l.29) |

## 6. Escenas y motivos (lo que el modelo pinta)

*Dirección del 2026-11-10: materia tallada (madera, hierro, oro, piedra) y la Semilla rota; los paisajes de r2-r5 (agujas, calima) quedan solo como fondo de `og`/`banner` si hace falta un paisaje; r7 (lápiz) archivada en «Historia».*

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | **de marca:** la Semilla rota (disco de piedra oscura `#3a342d` en seis gajos, juntas de luz de oro, estrella de cuatro puntas), el aro de oro con cuatro puntos, la noche índigo con polvo de estrellas fino (sin luna), tablones de madera veteada `#332415` / `#46311d`, bandas de hierro `#171310` con remaches, piedra agrietada, pátina en los huecos (M6); todo nace del emblema (M8), pero el emblema **no se pinta**: donde una pieza lo lleva en relieve, img2img 0,35-0,45 desde el SVG rasterizado (§4), y pedestal de piedra para los pictogramas. En las piezas de escena (E2, E3, E4, E6, #6) el motivo es la noche con su cinturón de polvo, siempre presente y la única luz del cielo: **sin estrellas de cuatro puntas pintadas** (la estrella es la del emblema, que llega por composición; en `e02` q349 la pintada compitió con el logo). **De paisaje** (solo `og`/`banner` de fondo, hipótesis de r2 aprobada por delegación): agujas de roca de hierro, crestas de arena, llanura en calima, hilo de humo, estandarte; del canon: Pilares Rotos, Agujas Imán, empalizada de Telda, obelisco. Sin esquirlas (r7) | marca: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §2 M1-M8 y §6); paisaje: **[P]** (`biblia.md` §7; `examples/tarkor/prompts/estilo.txt`; WMF `regiones/llanuras-del-viento-rojo.md` l.376-385) |
| Motivos No | Obl. | texto y letras pintadas por el modelo; personajes, rostros, manos y criaturas; interfaz falsa; luna y disco del sol; «heavens»; cualquier cosa morada o violeta; cromo, neón, destellos, rayos de luz, calima brillante; sombra arrojada y vista en perspectiva en las piezas de interfaz; dibujo plano, clipart, cartoon; pólvora; estética de otro juego y «AAA genérico»; el canon reservado (qué sabe Tarkor, la Entidad, la luz morada, Reino Nabierus, Ciudad Hundida, Archivo Cegado, muro de obsidiana), Vaelira, fechas y promesas | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §7); WMF (`00-nucleo.md` «Tono prohibido»); repo (`biblia.md` §7) |
| Palabras vetadas | Obl. | del juego (`mundo.json`, como patrones): `moon`, `moons`, `moonlit`, `moonlight`; `crystal dust`, `heavens`; `scar`, `scars`, `scarred`, `wound`, `wounds`, `gash`, `gashes`; negaciones `no`, `not`, `without`, `never`, `none`, `nothing`, `nobody`, `n't`; nombres propios; humanos (`human`, `man`, `woman`, `people`); pólvora (`gunpowder`, `musket`, `cannon`). De la marca: `purple`, `violet` (luz reservada); `castle` (decidido por la persona, 2026-11-12); `like`; `sun` (pinta el disco). Comunes: `text`, `letters`, `logo`, `watermark`, `caption`, `sign`, y desde el 2026-11-11 `emblem`, `title`, `star`, `stars` (en las piezas que reciben el logo) y `fire`/`lamp` negados (ver abajo). Fuera del prompt también `glowing`, `pouring light`, `flare` (M2). **No hay prompt negativo:** el pedido de gimg no tiene campo `negative` y con `cfg` 1.0 ni FLUX ni Z-Image lo atienden; el bloque negativo de la propuesta (M10) queda como **lista de lo que no se nombra**, no como campo. Las negaciones dentro del prompt se cuelan: `e02` pidió «no stars» en la zona libre y salió una estrella; `e06` pidió «no fires and no lamps» y salió sin la hoguera que E6 quiere; «reserved for an emblem» pintó un emblema (`e04`). Regla: lo que no se quiere **no se nombra ni negado**, y la zona libre se describe como lo que es («plain calm sky in #1a2140, even and empty»). «no haze» al final del bloque común sigue siendo la única negación admitida (frase aprobada; no ha pintado niebla) | repo (`biblia.md` §7; `peticiones.md` §2); WMF-imagenes (`mundo.json` l.146-152); negativo como lista: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §7); sin campo y negaciones que se cuelan: ronda del 2026-11-10/11 (`docs/handoff.md`) |
| Estilo de imagen | Rec. | **piezas de marca e interfaz:** el bloque común (M10): «Epic fantasy game asset. Materials: aged dark wood planks with raised grain in #332415 and #46311d, dark forged iron in #171310, old carved gold in #b8862b with dark patina #7a5a1e in the recesses and bright worn edges in #f2c45a, dark cracked stone in #3a342d. Warm raking light from the upper left, deep cool shadows in every groove. A thin dark bronze outline separates gold from background. Physically plausible materials, crisp edges, high contrast, no haze.» Va delante de las piezas **de materia** (tablones, bandas, marcos, fichas, pictogramas, sello, insignia). **Piezas de escena nocturna** (E2, E3, E4, E6, #6): el bloque común, que lista oro, hierro y madera, hace que el modelo los reparta por toda la escena (`e06` q355 pasó del 10 % de oro); llevan en su lugar el **bloque de noche**: «Epic fantasy matte painting, physically plausible, crisp edges, high contrast, clear air, no haze. Deep indigo blue night sky #1a2140, slightly green-leaning, near black #0f1428 at the top. A slanted belt of pale shimmering stardust in #4aa8d8 and #a8d8f0 crosses the sky and is the only light in it.» y nombran la materia una sola vez, donde está (la banda de madera o hierro del borde, con **una** línea fina de oro) *(suposición: se comprueba al rehacer E2-E6)*. Los recortes van sobre croma (fila «Recorte sobre croma»). **Paisajes** (`og`/`banner` de fondo): «cinematic landscape photograph, rich natural colour» de `r2-luz-r1.txt`, sin «muted», sin arcilla en el prompt salvo la tierra de Berig. Los prompts `estilo.txt`, `r5-*.txt`, `og.txt` y `r7-*` son históricos | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §7 y §9.10; `peticiones.md` §2); bloque de noche: revisión de Tarkor, 2026-11-11 (`e02` q349, `e06` q355 rechazadas); paisaje: repo (`examples/tarkor/prompts/r2-luz-r1.txt`) |
| Recorte sobre croma | Rec. | gimg no da transparencia: lo que la necesita se genera sobre croma plano y se recorta con `gimg matte` (`remove_bg`, `t0=60`, `t1=110`, `--holes` para vaciar lo encerrado; `-alpha.png` en la entrega). Croma **verde `#00ff00`** por defecto; **magenta `#ff00ff`** cuando la pieza lleva verde (bosques, ciénaga, musgo). Cómo se pide, para que salga puro: la frase del fondo **cierra el prompt** y dice color, hex y uniformidad: «Centred on a solid, uniform, evenly lit chroma-key green background #00ff00, one flat colour edge to edge, the object lit evenly and floating, 15 percent empty margin on every side.» Sin «background» a secas ni adjetivos de material o de pincelada que lo alcancen: en el mapa 03 (q372-373) «perfectly flat background of pure #00ff00 green» con el bloque pictórico delante salió **no puro** (el pincel pintó el fondo), y el emblema `01-emblema` (Z-Image, «perfectly flat untouched bright green background, lit evenly») salió mate y se recortó limpio. Si aun así el fondo sale con gradiente, se sube `t0` antes de repetir la generación. Para un marco 9-slice (E11) basta **una** esquina limpia: se refleja en la composición | repo (`gimg/matte.py` l.3-16; `docs/handoff.md`, mapa 03 «fondo no puro»); frase: *(suposición)* hasta el primer recorte limpio del mapa |
| Recuentos | Rec. | ningún modelo garantiza un número (seis gajos, cuatro puntas, cinco segmentos, tres picos): el prompt lo dice igual, se piden 6-10 semillas cuando el recuento importa y la pieza se acepta solo si está bien; lo que exige un recuento exacto va al SVG (D37) o se compone, no se pide pintado | ronda del 2026-11-10 (`01-emblema`: X o cinco gajos; `01b`: estrella de cinco puntas) |
| Mapa de Helek: estilo de terreno e iconos | Rec. | **Pintado, con el acabado de las ilustraciones del juego** (decisión de la persona, 2026-11-12): el de `estilos.mapa` de `image-generator/estilo/mundo.json`, «Painterly realism halfway between a photograph and an oil painting: realistic terrain, light and texture rendered with soft, visible brushwork». Bloque de terreno ([`pedido-mapa.md`](pedido-mapa.md) §2): «Hand-painted fantasy map terrain, seen from directly above. Painterly realism halfway between a photograph and an oil painting: realistic terrain, light and texture rendered with soft, visible brushwork. Restrained natural colour, soft warm light from the upper left, even exposure, calm and readable, no haze.» Un icono o una textura que salga como **vector plano NUNCA se acepta**: los iconos de la prueba (03 montaña, q373 y q372) salieron planos y se repiten con este bloque; la nota de cada pieza la sigue poniendo Álvaro. Los iconos (M-B y #3) llevan el **bloque de icono**, el mismo sin «seen from directly above» y sin «even exposure» (`pedido-mapa.md` §2). Los 48 pedidos de `examples/tarkor/orders/mapa/` llevan estos bloques y la frase de croma de la fila «Recorte sobre croma» desde el 2026-11-12; ninguno se ha generado todavía con ellos | decisión de la persona, 2026-11-12; WMF-imagenes (`mundo.json`, `estilos.mapa`); primera ronda, 2026-11-11 (sección 12) |
| Lenguaje de forma | Opc. | materia tallada y forjada: madera veteada, hierro negro, oro viejo con pátina, piedra agrietada; **la madera sostiene, el oro remata**: oro solo en filos, juntas, remaches y la estrella; una sola luz (rasante desde arriba a la izquierda), la misma en la pieza, el SVG y el CSS; cuatro puntos cardinales en todo lo redondo; silueta rellena antes que contorno; radios: paneles 12 px, remaches redondos, gema con esquinas vivas; filetes de 1 px (`.gold-hairline`, `.accent-hairline`); simetría rota a propósito | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §2 y §5); WMF (`index.css` l.226-234, l.246-254, l.324-348) |

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | **piezas de marca e interfaz:** «Warm raking light from the upper left, deep cool shadows in every groove»: rasante a 45°, la misma en el SVG, el CSS y los PNG, y la única (nada brilla por sí mismo salvo las juntas de la Semilla, M2). **Paisajes:** «A warm raking light comes from low behind them, from the right» (`r2-luz.txt`), sin nombrar la fuente | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §2 M2 y §7); paisaje: *(suposición)* (`r2-luz.txt`) |
| Momento y clima | Rec. | **marca:** noche índigo `#1a2140`, ligeramente verdosa, con polvo de estrellas fino y sin luna ni disco (decisión 1; la noche del canon es un cinturón de polvo que brilla); dentro del juego, interior de madera sin cielo. **Paisajes:** amanecer bajo en calima (`r2-luz`) o contraluz cálido (`r2-luz-r1`); nunca golden hour | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 y §9.1); paisaje: *(suposición)* (`r2-luz.txt`, `r2-luz-r1.txt`); canon: WMF (`genesis.md` l.146-155) |
| Luminosidad objetivo (YAVG) | Rec. | **paisajes:** 105-150 (portada 127), como hasta ahora (r1 129/125; r2 155; og r4 169; r5 172-177; og-bajo 66). **Piezas de marca e interfaz:** sin rango fijado; se miden aparte cuando existan (una pieza de noche con oro saldrá muy por debajo de 105 a propósito: manda el 60/30/10, no el YAVG) | repo (`docs/records/contenido/calibracion-measure.md` l.31-34, l.69); piezas nuevas: pendiente de medir |
| Saturación objetivo (SATAVG) | Rec. | **paisajes:** 18-32 (portada 25), el problema abierto de r2-r5 (6,4-8,6; r5 5-7). **Piezas de marca e interfaz:** sin rango: la paleta es madera, hierro y piedra con el oro como único color; lo que se comprueba es la proporción 60/30/10 y que el brillo no pase del 5 % | repo (`calibracion-measure.md` l.31-34; `r2-estilo.md` l.36-38); piezas nuevas: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4 «Proporción») |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | **0) los dos PNG de `examples/tarkor/logos/`** (`Emblema dorado y título TARKOR.png`, `Tarkor_ La semilla rota.png`): la dirección que la persona confirmó el 2026-11-10; referencia de dirección, no piezas (el modelo pintó las letras). **1) `portada.webp`** 1600×640 (los Pilares Rotos), publicada en la ficha de Tarkor del Portal (`public/proyectos/tarkor/portada.webp`, Portal `aa76b34`): YAVG 127, SATAVG 25, paleta 42 %; calibró los paisajes; la sustituyen E2/E5 cuando existan. **2)** 304 `.webp` de arte del juego en el Portal: referencia `-r` de sujeto. **3)** banners por región de WMF-imagenes: no son marca. **Lo que no hay:** og:image en el juego (`frontend/index.html` sin `og:`), social preview, pieza publicada en redes | repo (`examples/tarkor/logos/`; `biblia.md` §10); dirección: **aprobado por la persona, 2026-11-10** |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | 27 declarados (`lateral`, `linkedin`, `discord` y `panorama` desde el 2026-11-13), todos con `cfg` 1.0, `euler`, múltiplos de 64 y ≤ 1 048 576 px. **Modelo por perfil:** `zimage-turbo-q6` a **8 pasos** en lo que se entrega (`og`, `banda`, `icono`, `cabecera`, `carga`, `capsula`, `marco` y los cinco del mapa); `flux2-klein-4b-q8` a 6 pasos solo en los que aún no se han pedido en calidad (`social`, `banner`, `square`, `header`, `portrait`, `emblema`, `textura`, `cielo`, `estampa`, `tira`, `avatar`): antes de generarlos en definitivo pasan a Z-Image. Redes: `og` 1280×640 → 1200×630, `social` 1280×640, `banner` 1280×512 → 1600×640, `square` 1024² → 1080², `header` 1536×512 → 1500×500, `portrait` 896×1152 → 1080×1350. Marca e interfaz (Bloque E): `emblema` 1024², `textura` 1024², `banda` 1024×256, `cielo` 1536×640, `icono` 512², `estampa` 1280×512, `tira` 1024×128, `avatar` 1024², `cabecera` 1536×512 → 1500×500, `carga` 1280×704, `capsula` 1024×576 → 616×353, `marco` 1280×704. Mapa (`pedido-mapa.md`; nombres propios para no pisar los de interfaz): `texturamapa` 1024² `tileable: "xy"`, `iconomapa` 768², `cartela` 1024×512, `bandamapa` 1024×256, `marcomapa` 1024×256 `tileable: "x"`. Las texturas sin costura llevan `tileable` en el perfil (`--circular` de sd-cli, arreglado en `b9c0187`): ya no se arregla la costura a mano. Steam: cápsula, cabecera y principal (decisión 7) y, desde el 2026-11-12, la cápsula vertical de la Deck (I6, 600×900) y el icono 256²; lo demás de la Deck son recortes de E4 y E5. Discord 960×540 sale de `cabecera`; LinkedIn 1584×396, aparte cuando se pida; Reddit usa E1 y E2 (decidido el 2026-11-12) | repo (`examples/tarkor/galivelop-images.json`, 2026-11-11); modelos: `docs/handoff.md` (FLUX solo bocetos; Z-Image 8 pasos; Qwen-Image solo fotorrealismo o detalle muy concreto, sin perfil hoy); **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §6 y §9.7; `peticiones.md` §3) |
| Zona reservada | Obl. | las piezas de marca ya no son paisajes con un hueco: `og` (E3) es el lockup vertical centrado sobre noche con el lema debajo, sin zona; `cabecera` (E2): emblema a la izquierda (1/3) y madera o noche a la derecha; `capsula` (E4): emblema centrado, 60 % del hueco; hero (E5): mitad izquierda para el titular, emblema a la derecha. En el prompt la zona se describe **como cielo o madera lisa, con su fracción desde el borde** («the left third, from the left edge inward, is plain calm sky in #1a2140, even and empty»), nunca por lo que irá encima (§6, vetadas); el cinturón de polvo y la silueta del borde quedan en el resto. Para los paisajes de fondo sigue lo de r5: `izquierda 1/3` en og/social/banner, `izquierda 1/2` en header, `abajo 1/2` en square/portrait | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §6 E2-E5); paisaje: decidido el 2026-11-04 |
| Composición por perfil | Rec. | `og` lleva `compose` E3 desde el 2026-11-10: `plantillas/og.svg` (solo vector sobre la noche generada: `<image id="gimg-logo">` 456×420 centrado, emblema 283,5 px = 45 % del alto, margen libre arriba y abajo ≈ 65 px = altura de la T; `<text id="gimg-lema">` Inter 400 30 px hueso `#f1e4d0` al 0,82, centrado debajo; sin velo, sin marco, sin separador #9 porque no tiene SVG), `logo: logos/tarkor-lockup-v.svg`, `fields: ["lema"]`, `fonts: ["Cinzel", "Inter"]` (Cinzel por la familia de marca; el wordmark va en trazos dentro del lockup). Los lockups se regeneraron con `brand.lockup(color="#b8862b")`: embebidos por `<image>`, `currentColor` salía negro. Las demás piezas de marca (E1, E2, E4, E5, E14) se componen en SVG sobre los PNG de `entrega/marca/`, sin velo | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §6); **configurado el 2026-11-10** (`tests/test_examples.py` `TarkorOgE3Tests` lo ata; prueba sin modelo en `piloto/tarkor/og-e3-prueba.png`) |
| Piezas solo de logo | Rec. | `avatar` (E1, `e01-avatar.png`) 1024² → 400²: emblema completo sobre noche, desde 64 px (decisión 8; el monograma T solo por debajo); `icon` (E14, `e14-icono-app.png`) 512² → 16/32/128/512 y `fuente.png` 1024 para el Instalador: emblema sobre un disco de noche `night-950` `#0f1428` (emblema simple de 64 px para abajo; corregido el 2026-11-12, sección 18); favicon del juego: `tarkor-emblema-simple.svg`. Sustituir el favicon de Vite y el icono b del Instalador es propuesta a esos repos (`docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md`) | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §6 E1 y E14, §9.8); WMF e Instalador: pendientes |
| Borrador | Opc. | `draft: {scale: 0.5, steps: 4}` en los 27 perfiles. **FLUX es solo para bocetos** (composición, reparto, bocetos para el SVG: así salieron los de `piloto/tarkor/`); lo que se entrega va con `draft: false` en Z-Image a 8 pasos (~10 min por imagen a 1024² en la Deck). Un borrador no se puede elegir con `gimg choose` ni pasar por pieza | repo (`galivelop-images.json`; `docs/handoff.md`, prueba Z-Image del 2026-11-10) |
| Velo por perfil | Rec. | **ninguno**: las piezas nuevas van sobre noche o madera generadas, no sobre foto velada. Los velos de r4-r5 (`#f1e4d0:0.55`, `#221c16:0.45`) salieron de `piezas.json` el 2026-11-10: las tres piezas que quedan (`og`, `cabecera`, `avatar`) llevan `velo: "#0f1428:0"` porque `piezas.py` exige la clave cuando hay fondo | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §4); `examples/tarkor/piezas.json` rehecho el 2026-11-10 |
| Logo en la pieza | Rec. | E3 (`og`): lockup vertical centrado, emblema ≈ 45 % del alto; E2 (`cabecera`): emblema a la izquierda, ≈ 70 % del alto; E4 (`capsula`): emblema centrado al 60 % del hueco, wordmark debajo; E5 (hero): emblema a la derecha, titular en oro a la izquierda; E1/E14: solo emblema. Margen = altura de la T. Nunca al 9 % en una esquina sobre un paisaje (r4-r5). **Jerarquía:** el logo es lo más luminoso de la pieza; el fondo generado no lleva estrellas pintadas, ni castillo ni oro que pasen del 10 % (el cinturón de polvo es tenue y pasa por detrás del detalle, no del logo) | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §6); jerarquía: revisión de Tarkor, 2026-11-11 (`e02` q349) |
| Palancas extra | Opc. | **img2img** (`initImage` + `strength` del pedido): desde el **SVG rasterizado** sobre el color de la pieza, fuerza 0,35-0,45, para lo que lleva el emblema en relieve (E9, #16, #26-38), de modo que los gajos y las puntas sean los del SVG (M8 reescrita: el `01-emblema` generado no sirve de semilla, §4); desde un intento aceptado «como referencia» (el cielo de `e04` q352), fuerza 0,5-0,7, para conservar su composición al rehacer la pieza. **Referencias de sujeto** `-r`: los 304 `.webp` del Portal, solo paisajes. **LUT** `estilo/lut/` del juego y **LoRA `wmf-estilo`**: solo paisajes, F5. **Conversión final:** `.webp` del Portal y los `-alpha.png` de los recortes (fuera de `gimg`, D35) | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §2 M8-M9); resto: repo (`docs/plan.md` l.254, l.872) |
| Prioridad | Rec. | la de `peticiones.md` §5: 1) `01-emblema` (semilla de todo, 8-10 semillas, medido); 2) los SVG del sistema de logo, favicon y E14; 3) marca fuera del juego: E1 avatar, E2 cabecera, E3 og, E4 Steam; 4) Bloque A (`02-tablon`, `03-fondo`, `05-banda`, `06-cielo`, `04-polvo`, `07-defensa`); 5) `16-medallon`, `10-ranura`, E6 carga, E7 barra; 6) Bloque C (`12-hud`, `13-fase`, `11-pestana`, `14-dado`, `15-categoria`); 7) `08-esquina`, `09-separador`, `17-estado`, E9-E13, E5, E17, E18; 8) entrega y propuesta a los repos. Hechas: bocetos FLUX de #1 (q154, q175 en Z-Image) y el sistema SVG (paso 2, dos tintas); primera ronda Z-Image revisada el 2026-11-11 (§12): valen E7 (q357, q359) y mapa 03 (q373), E11 y E12 con arreglo; ninguna pieza entregada aún. **Siguiente:** rehacer E2, E3, E4, E6, E9 y E10 con §4 y §6 nuevos, luego E11/E12 arreglados; el mapa, cuando decida Álvaro | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §8; `peticiones.md` §5); estado: 2026-11-11 |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular del primer perfil compuesto | Obl. | `og` (E3): el titular es el wordmark «TARKOR» del lockup vertical (a trazos, no texto compuesto); debajo, una línea en Inter 400: **«El mundo sigue aunque tú te detengas.»** (37 caracteres, variación del lema; el lema literal, 70, cabe en una línea a 1200 px si se prefiere) | composición: **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §6 E3); texto: **[P]** (`examples/tarkor/piezas.json` `og.titulo`; `biblia.md` §6) |
| Subtítulo | Rec. | E3: ninguno más (lockup + una línea). E5 (hero): titular Cinzel 900 en oro «Tarkor» y subtítulo Inter 400 hueso «RPG narrativo de fantasía con IA local. En desarrollo, a la vista.» (64) | **[P]** (`piezas.json` `og.subtitulo`; `biblia.md` §6) |
| Variaciones, ganchos y cierres | Rec. | variaciones: «Deja la partida. El mundo sigue.» (`square`); ganchos: «Lo que no hagas, lo hará otro.» (`portrait`), «Madera, hierro y cristal.» + «Y un mundo que no te espera.» (`header`; el cristal sigue siendo materia del juego aunque no sea acento de marca); cierres: «Juega en local. Nadie mira.», «En desarrollo, a la vista.» | **[P]** (`biblia.md` §6; `piezas.json`) |
| Longitud máxima por campo | Rec. | orientativo ≤ 40 el titular y ≤ 70 el subtítulo (el lema, 70); la línea bajo el lockup de E3 va en una sola línea; la fija la plantilla E3 cuando exista | *(suposición)* (`piezas.json`; `r5-piezas.md` l.33) |
| Wordmark compuesto como texto | Opc. | **no, nunca**: el nombre va en `tarkor-wordmark.svg` a trazos (Cinzel 800 modificada); ni `<text>` ni letras pintadas por el modelo (los PNG de referencia las llevan y por eso son referencia, no pieza) | **aprobado por la persona, 2026-11-10** (`propuesta-fable-2026-11-10.md` §5 y §9.5) |

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
| Veredicto | Obl. | la persona (marca) y **el equipo de Tarkor** (interfaz y mapa: la nota la pone Álvaro, `pedido-mapa.md` §5); se apunta en `docs/records/contenido/rN-<tema>.md`. Dado hasta hoy: r1 **«no»** sin motivo (2026-10-26). r2-r5 del piloto: medidas del agente, sin veredicto; r2-luz, sin medir. **Primera ronda Z-Image, revisada por el equipo de Tarkor el 2026-11-11 (aceptada):** valen mapa 03 icono de montaña **q373** (el mejor) y q372, barras E7 **q357** (pista) y **q359** (relleno); valen con arreglo E11 marco de retrato **q365** (reflejar la esquina limpia para el 9-slice) y E12 plantilla de captura **q366**; rechazadas E2 q349 (la estrella compite con el logo; falta el cinturón de polvo), E4 q352/q353 (emblema falso; del q352 vale el cielo como referencia), E6 q355 (más del 10 % de oro, sin hoguera), E7 q356 y q358, E11 q364, E12 q367. **Se rehacen** E2, E3, E4, E6, E9, E10 y los arreglos de E11 y E12, con las reglas nuevas de §4, §6 y §9; el mapa espera la decisión de Álvaro (§6) | repo (`docs/records/contenido/r1-fondos.md` l.49, l.52; `r2-estilo.md`; `r5-piezas.md`; `docs/handoff.md`); revisión de Tarkor: 2026-11-11, pendiente de pasar a `docs/records/contenido/` |
| Contraste del texto | Rec. | ≥ 4,5:1 (3:1 en titulares grandes). Medido: og r4 11,26 (peor 6,97); og-bajo 9,5 (7,36); cabecera 11,39 (6,89); cuadrado 6,28 (**5,18**); vertical 7,22 (**4,98**): los dos últimos pasan AA, no AAA, y son los que tienen la caja fuera de la zona | repo (`r4-composicion.md` l.19; `r5-piezas.md` l.33, l.41-43) |
| Umbrales de medida | Rec. | **paisajes:** paleta **≥ 30 %** (sección 3); YAVG **105-150** y SATAVG **18-32** (sección 7); hoy pasa la paleta y no pasan ni YAVG ni SATAVG en ninguna pieza de paisaje. **Piezas de marca e interfaz:** proporción 60/30/10 a ojo (oro ≤ 10 %, brillo ≤ 5 %), recuentos correctos, croma recortable y, en texturas, repetidas 4×4 sin costura ni motivo que se repita; icono legible a 24 px en gris (`pedido-mapa.md` §5) | repo (`calibracion-measure.md` l.69); piezas nuevas: `propuesta-fable-2026-11-10.md` §4; revisión de Tarkor, 2026-11-11 |
| EMD frente a la marca | Opc. | Cb ≲ 6 y Cr ≲ 7,5 (medianas; son los de aceptación del propio juego, `gradacion.json`). Medido frente a `portada.webp`: r1 Cb 4,7 / Cr 5,1 y 4,6 / 9,9 (cerca); r5 Cb 6,8-8,1 / Cr 19-20; og-bajo 12,3 / 22,3 (lejos: el estilo elegido se aleja de la portada en color). La EMD de Y (14,7 r1; 45-50 r5; 61,3 og-bajo) pesa la composición y no se usa sola | repo (`calibracion-measure.md` l.32-34, l.69); WMF-imagenes (`estilo/gradacion.json`) |
| Cuándo se da por bueno el estilo | Opc. | regla del plan para r2 luz: si Tarkor no entra en 105-150 / 18-32, la ronda cuenta como sin mejora y la segunda la decide la persona (otro prompt, LUT de F2.11 o aceptar la marca desaturada). Propuesta de cierre: `og` y `square` con «sí» de la persona y dentro de los rangos, o «sí» con los rangos corregidos por ella | repo (`docs/plan.md` l.796-798); cierre **[P]** |

## 13. Fuentes de verdad

**World-Maker-Fantasy** (WMF), leído solo, nada modificado. Comprobado el 2026-11-12 en `main` `3a10a3fa` y en
`claude/marca-interfaz` `c858a150` (UX-40, sin fusionar); las líneas son de `c858a150`:

- `frontend/src/index.css` l.9-14 (`--font-sans` Inter, `--font-serif` Cinzel, `--font-mono` Cascadia Code), l.23-32 (madera
  950-100), l.35-37 (hierro 900 `#0e0b08`, 800 `#171310`, 700 `#221c16`), l.40-43 (cristal `accent` 300-600), l.46-49 (acero
  `accent2`), l.55-59 (`gold-100…900`), l.61-62 (`stone-500/700`), l.64-65 (`night-900/950`), l.66 (`crystal-deep`), l.69-71
  (musgo), l.78-83 (`danger`, `cost`), l.89-91 (`quest`); clases: `.wood-grain` l.154, `.dust-road` l.177, `.plank-panel`
  l.192, `.plank-panel-defense` l.223, `.iron-band` l.246, `.accent-hairline` l.258, `.gold-hairline` l.277, `.gem` l.288,
  `.crystal-sky` l.316, `.iron-etched` l.340, `.corner-bracket` l.348, `.corner-bracket-gold` l.372 (sin usar en ningún
  componente), `.rivet` l.377, `.skill-slot` l.422, `.title-gold` l.462. **En `main` no existen** los tokens `gold-*`,
  `stone-*`, `night-*`, `crystal-deep` ni las clases de oro.
- `frontend/src/pages/Home.tsx` l.20 (`.crystal-sky`), l.30 (`<h1>` `title-gold`), l.45 (emoji ⚔️ aún en la tarjeta);
  eyebrow «Tarkor» en `text-wood-200`, filetes `gold-hairline`.
- `frontend/src/assets/fonts/` (`cinzel-latin(-ext)-wght-normal.woff2`, `inter-latin(-ext)-wght-normal.woff2`, `fonts.css`
  @fontsource-variable 5.3.0, `LICENSE-Cinzel.txt`, `LICENSE-Inter.txt`); `frontend/index.html` (`<title>Tarkor</title>`,
  `lang="es"`; en `c858a150`, además `theme-color` `#1b130c`, `og:title` y `og:description`; sin `og:image` ni
  `<link rel="icon">`); `frontend/public/favicon.svg` (rayo de Vite, `#863bff`, sigue en `main`).
- `docs/producto/02-decisiones.md` nº 6 (2026-07-16: base «madera + hierro», acentos tematizables por mundo; Helek Sirik
  azules y grises); `docs/producto/tarkor-contenido-web.md` l.31-35 (Steam Deck, sin conexión, español, alpha e hito 0.3,
  creador), l.40 (lema), l.41-42 (línea del juego), pilares 5 y 8.
- `docs/media/guia-canales.md` (en `3a10a3fa`; antes `docs/difusion/guia-canales.md`: voz, §X, §LinkedIn, §Reddit, §Discord,
  §Portal, §Imágenes, leídas en `e3778e61` y sin releer en la ruta nueva); `docs/media/README.md`;
  `docs/media/_plantilla/media/source/{tarjeta,diagrama}.html`; `.claude/gw/gw-media-content.md` (`3a10a3fa`: paleta del
  Portal `#06121c`, `#0c1d2b`, `#1b3447`, `#eaf4fa`, `#1aa6df`, DejaVu / Liberation Sans, 1600×900, `es` y `en`).
- `docs/canon-opencode/00-nucleo.md` l.37-43 («Tono prohibido»), QA-274; `docs/rpgtarkor/lore-mundo/genesis.md` l.146-155 («El
  cielo sin luna»); `docs/rpgtarkor/lore-mundo/regiones/llanuras-del-viento-rojo.md` l.376-385 (Los Pilares Rotos);
  `docs/producto/plan-imagenes/guia-visual-mundo.md` §1.5 y §2; `docs/producto/plan-imagenes/plantilla-prompt.md` l.15-22.
- **No existe** en `main` (`3a10a3fa`): logo, lockup, `og:image`, favicon propio, social preview declarado. Las citas de
  `02-decisiones.md`, `tarkor-contenido-web.md`, `canon-opencode`, `rpgtarkor` y `plan-imagenes` de esta lista son de
  `e3778e61` y no se han recomprobado el 2026-11-12.

**WMF-imagenes** (clon del mismo origen que WMF; leído solo). `image-generator/estilo/mundo.json`, releído el 2026-11-12 en
su `origin/main`: preámbulos día / atardecer / noche (la noche: «the sky is full of stars under a soft, even pearly glow»);
estilos `banner` (fotográfico), `icono` y `thumbnail` (óleo), `fotorreal` y **`mapa`** («Painterly realism halfway between a
photograph and an oil painting: realistic terrain, light and texture rendered with soft, visible brushwork»: es el acabado
del mapa pintado, sección 6); cinco regiones con luz y estaciones; `vetadas` (luna, `crystal dust`, `heavens`, heridas,
`fossilised sand`) y `negaciones` como regex. De `8a48fe52`, sin recomprobar: `estilo/gradacion.json` (aceptación EMD
Cb ≲ 6 / Cr ≲ 7,5; ventanas plan 70-95 / 15-30, día 103-133 / 12-17, noche 31-52 / 2-10), `estilo/lut/{dia,atardecer,noche}.cube`,
`scripts/` y, sin versionar, `bin-nuevo/` y `loras/`.

**WMF-fichas**, `claude/fichas-banners` `d77142b4` (leído solo): mismo frontal e `index.css` que WMF; nada propio de marca.

**Instalador-WMF-Tarkor** (leído solo; **repo público**), `main` `5631e77b` y `claude/installer-docs-review-09e7vs`
`34d2bb27` (2026-11-12): `docs/13-hoja-de-estilos-e-imagenes.md` (`d9d33fe` pedido INS-57, `608661d` dudas resueltas): §2
reglas y destino, §3 piezas I1-I6 y dónde va cada pieza ya pedida, §6 decisiones de la usuaria (E14 sobre noche; la copia
de la entrega la hace ella); `app/src/estilos.css` (sin tokens `gold-*`, `night-*` ni `stone-*`; `.filete` l.60 y `.btn.pri`
en `accent`; `.btn.pri { color: #fff }`; `.barra` l.65; `.riel` l.31-33; `.pista` y `.relleno` l.90-91; Cinzel 400, 600 y
700); `app/src-tauri/icons/` (rombo azul, a sustituir por E14); `app/src-tauri/windows/installer.nsi`;
`app/src-tauri/tauri.conf.json` (`productName` «Tarkor»); `README.md` (dice que el repo del juego es privado). De
`a73f881`, sin recomprobar: `docs/11-diseno-del-frontal.md` l.14-15 y l.135, `diseno/prototipo-asistente.html` l.1-25.

**`plan-imagenes-tarkor`**: carpeta sin git; copia de WMF `docs/producto/plan-imagenes/` (se cita la de WMF).

**Portal-Galivelop** `aa76b34`, solo a través de `biblia.md` §10: `src/data/proyectos/tarkor.json` l.7 (acento `#E0703A`),
`public/proyectos/tarkor/portada.webp` (1600×640), `public/proyectos/tarkor/arte/` (304 `.webp`), `public/marca/gv-logo.svg`
(baldosa).

**Este repo**, rama `agent/hojas-tarkor` (2026-11-12):

- `examples/tarkor/galivelop-images.json`: `name`; `brand.palette` de **16 hex** (`#8a9aa8`, `#221c16`, `#332415`, `#f1e4d0`,
  `#241a10`, `#52626f`, `#4aa8d8`, `#ffe9a8`, `#f2c45a`, `#b8862b`, `#7a5a1e`, `#5a3a14`, `#3a342d`, `#1f4a55`, `#0f1428`,
  `#1b130c`); `delivery`; **23 perfiles** (`avatar`, `banda`, `bandamapa`, `banner`, `cabecera`, `capsula`, `carga`,
  `cartela`, `cielo`, `emblema`, `estampa`, `header`, `icono`, `iconomapa`, `marco`, `marcomapa`, `og`, `portrait`, `social`,
  `square`, `textura`, `texturamapa`, `tira`); desde el 2026-11-13 también `lateral`, `linkedin`, `discord` y `panorama`. `gimg/measure.py` l.25 (`DELTA_E = 15.0`), l.83-84 (ΔE76),
  l.170 (`palette_share`). Pedidos en `examples/tarkor/orders/{marca,ui,mapa}/`.
- `examples/tarkor/piezas.json` (Cinzel / Inter; desde el 2026-11-10 solo `og` E3, `cabecera` E2 y `avatar` E1, con los logos de
  `examples/tarkor/logos/`, lema «El mundo sigue aunque tú te detengas.» y velo a 0; `og-bajo`, `cuadrado` y `vertical` eran paisajes
  de r4-r5 y se quitaron). Límite: `piezas.py` pone el logo al 9 % en una esquina y busca los fondos en `piloto/`; la maqueta E3 real
  es `og.compose`, y para las otras piezas hace falta un camino nuevo sobre `entrega/marca/`.
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
- Desde el 2026-11-10: [`propuesta-fable-2026-11-10.md`](propuesta-fable-2026-11-10.md) (dirección, M1-M10, paleta, sistema
  de logo, piezas E1-E18, decisiones §9 aprobadas por la persona), [`peticiones.md`](peticiones.md) (bloque común, negativo,
  nombres `entrega/ui/<nn>-<nombre>.png` y `entrega/marca/e<nn>-<nombre>.png`, perfiles por declarar, orden de trabajo),
  [`biblia.md`](biblia.md) (reescrita); `examples/tarkor/logos/Emblema dorado y título TARKOR.png` y `Tarkor_ La semilla
  rota.png` (dirección confirmada); `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md` (propuesta al juego, al
  Instalador y al Portal).

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo; lo de WMF y el Instalador va como propuesta a
esos repos):

- Hecho el 2026-11-04: destinos (`og` 1200×630, `square` 1080×1080, `header` 1500×500, `banner` 1600×640, `portrait` 1080×1350),
  `draft` en `og` y `brand.palette` con `#241a10`, `#8a3b1e`, `#a3814f`, `#52626f` y `#4aa8d8` (fuera a propósito: `#1b130c`,
  la banda que sale, y `#f2b34a`, solo si r2-luz-r1 gana).
- Falta: `social` y `banner` declarados y nunca generados; el 16:9 de 1600×900 que pide `guia-canales.md`, Discord 960×540 y
  LinkedIn 1584×396 tienen perfil desde el 2026-11-13 (`panorama`, `discord`, `linkedin`), sin prompt todavía.
- `compose`: `og` lo declara desde el 2026-11-10 (plantilla E3, `tarkor-lockup-v.svg`, Cinzel/Inter, campo `lema`); ningún pedido de
  `orders/` lleva todavía `text` con el lema (`textos/og.json` solo lo lee el test). Las demás piezas siguen sin `compose`.
- `estilo.txt`, `r2-hex/palabras/material.txt`, `r5-*.txt` y `og.txt` nombran «sun» contra la pauta del 2026-11-02; `estilo.txt`
  pide «muted»; `r5-cuadrado/vertical.txt` piden «lower third»; `og.txt` lleva además «golden hour», «nearly empty» y «Shot on a
  full-frame camera with a 35mm lens». **Son históricos** (no se tocan) y se rehacen con la hoja; `r2-luz.txt` es el candidato
  a `estilo.txt` (decidido). El pedido `r2-control.json` conserva «sun» (el test del repo lo ata byte a byte a `prompts/r2-hex.txt`, histórico).
- Copia de los logos en `examples/tarkor/logos/`: hecha el 2026-11-10 (`tarkor-emblema.svg`, `tarkor-lockup-h.svg`,
  `tarkor-lockup-v.svg`, byte a byte con `docs/marcas/tarkor/logos/`); los `logo` de `piezas.json` apuntan a esa copia.
- `piloto/fuentes/` no existe aquí: `fuentes.sh` no se ha corrido en esta máquina; las piezas de r4-r5 se compusieron donde sí.
- En WMF: la nota de `gw-media-content` lleva la paleta del Portal, no la de Tarkor (ver «Contradicciones», 5); sin og:image;
  favicon de Vite. En el Instalador: icono del concepto b. Lo que les toca ahora está en `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md`;
  al Portal, además, el acento `tarkor.json` l.7 de arcilla a oro `#b8862b`.
- **Desde el 2026-11-10, todo lo de arriba más esto:** en el repo ya están `brand.palette` con los 16 hex de la sección 3 y el
  logo (fuera `#E0703A`, `#8a3b1e` y `#a3814f`), `draft` en los 18 perfiles, los once perfiles del Bloque E,
  `orders/ui/01-emblema.json` con el bloque común M10 y el prompt de `peticiones.md` #1, y los pedidos E2-E4, E6, E7, E9-E12
  (`orders/marca/`, `orders/ui/`). Con los SVG del sistema nuevo ya generados, el mismo día pasaron a la hoja `og.compose`
  (plantilla E3, `logos/tarkor-lockup-v.svg`, Cinzel/Inter; `tests/test_examples.py` lo ata) y `piezas.json` (sin velos, lockups
  nuevos); `plantillas/og.svg` de r7 (velo de pergamino, Metamorphous/Almendra, `tarkor-b-lockup.svg`) ya no existe.
- **Desde el 2026-11-11:** los pedidos `orders/marca/e02-e04` y `orders/ui/e06, e09, e10` incumplen la hoja afinada y se
  rehacen: llevan negaciones («no stars and no spires», «no fires and no lamps», «no cast shadow», «no halo»), nombran la zona
  libre por lo que irá encima («reserved for an emblem / a title»), piden estrellas de cuatro puntas en piezas que reciben el
  logo, anteponen el bloque de materia a escenas de noche, y `e09` pide el emblema pintado en la cera. Los del mapa
  (`orders/mapa/01-36`) siguen el pedido de WMF y esperan la decisión de Álvaro (§6). `e07`, `e11`, `e12` y `mapa/03` ya
  dieron intentos válidos y no se tocan (el 9-slice de E11 se arregla en la composición). Los perfiles del mapa se declararon
  con nombre propio (`texturamapa`, `iconomapa`, `cartela`, `bandamapa`, `marcomapa`), no con los `textura`/`icono` que cita
  `pedido-mapa.md` §2: avisar a WMF cuando se entregue.

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio; es la línea del juego en `tarkor-contenido-web.md`) |
| 3 | «Nunca se muestra» no vacío | pasa (la lista más larga de los seis proyectos: el canon reserva mucho); nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | pasa por forma (10 hex), **no por contenido desde el 2026-11-10**: lleva el acento viejo `#E0703A` y no lleva `#b8862b`, `#0f1428` ni `#3a342d`; se rehace con la configuración (sección 13) |
| 5 | Símbolo SVG válido | `tarkor-emblema.svg` existe desde el 2026-11-10 (`gimg brand system` sobre q185; dos tintas, sin `<text>`/`<image>`/`filter`), con `-simple`, `-mono`, `wordmark` y los dos lockups; copia byte a byte en `examples/<p>/logos/` (emblema y lockups). Pendientes: glifo, monograma, `-claro`, versión tallada; el `viewBox` es el que da `system`, no `0 0 128 128`. `tarkor-a.svg` es historia |
| 6 | Familia de titular instalada | desde el 2026-11-10 `og.compose.fonts` declara Cinzel e Inter y `gimg doctor` las comprueba (`fc-list` las encuentra en esta máquina); el lockup nuevo va en trazos y no depende de ninguna fuente; el lema sí necesita Inter instalada |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida; Motivos Sí es **[P]** entero |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | `r2-luz` y `r2-luz-r1` **pasan** la lista de esta hoja; `r2-control` no (`r2-control` conserva el «sun» histórico de `r2-hex.txt`; «muted» no es palabra vetada). Los prompts históricos con «sun» (`r2-hex.txt` y su pedido, `estilo.txt`, `r2-hex/palabras/material.txt`, `r5-*.txt`, `og.txt`) no pasan y se rehacen. **Los pedidos E de 2026-11-10 tampoco pasan** (negaciones, `emblem`, `title`, `stars`; sección 13) y se rehacen; `01-emblema` y `01b` llevan `no rays, no flare, zero shading…` y valen solo como boceto del SVG |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (129-241 palabras), los once |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | pasa: múltiplos de 64 en los seis y destino declarado en todos los que lo tienen distinto (`social` es igual y no lo lleva) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | zona decidida (og/social/banner `izquierda 1/3`, `header` `izquierda 1/2`, `square`/`portrait` `abajo 1/2`); ningún perfil la declara aún (hueco de `compose`); los prompts de `square` y `portrait` piden todavía 1/3 (históricos, por rehacer) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (37 caracteres; r4 compuesto; 70 del lema cupo como subtítulo en `vertical`) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | **no pasa desde el 2026-11-10**: faltan `#b8862b`, `#f2c45a`, `#7a5a1e`, `#5a3a14`, `#ffe9a8`, `#0f1428`, `#1a2140`, `#3a342d`, `#1f4a55`; sobran `#E0703A`, `#8a3b1e`, `#a3814f` |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | pasa: `og` 1200×630, `banner` 1600×640, `square` 1080×1080, `header` 1500×500 y `portrait` 1080×1350 declarados; `social` es igual y no necesita destino |

Validador: `gimg doctor --project <p>`, antes de r5 (aún no implementado). **Obligatorios de esta hoja: 18** (familia propia):
**14 salen de un repo o de una decisión** y **4 eran [P]** aprobadas por delegación; desde el 2026-11-10, fondo, acento, símbolo y motivos Sí de marca llevan el «sí» propio de la persona (la dirección de los PNG y las diez decisiones); el titular sigue [P]. Las comprobaciones 4, 5 y 15 vuelven a rojo hasta rehacer la configuración y dibujar los SVG.

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
(aquel), y la plantilla no tiene fila para «el producto genera sus propias imágenes con otras reglas». **Desde el 2026-11-10 se añaden:** 4) un **sistema de logo de siete SVG** (emblema, simple, glifo, monograma, wordmark, dos lockups) con tres variantes cada uno, donde la plantilla prevé un símbolo y un lockup; 5) **once perfiles** de texturas, bandas y pictogramas que no son piezas de redes (`textura`, `banda`, `cielo`, `icono`, `estampa`, `tira`, `avatar`, `cabecera`, `carga`, `capsula`, `marco`): la fila «Perfiles» piensa en og y cabeceras; 6) el **acento heredado del Portal** (arcilla) deja de ser el de la marca y la plantilla no dice cómo se avisa al que lo hereda; 7) **favicon e icono de app** viven en otros repos (WMF, Instalador) y la hoja solo puede proponerlos (`docs/propuestas/tarkor/`); 8) el **negativo** común de las piezas no tiene fila (la plantilla solo prevé palabras vetadas en positivo).

---

## 16. Reglas estrictas (2026-11-12)

Cada regla dice **DEBE** o **NUNCA**, con qué se comprueba. Mandan sobre las secciones 1-12 si chocan.

**Decisiones de la persona del 2026-11-12** (`docs/propuestas/tarkor/auditoria-hoja-2026-11-12.md`): 1) tolerancia de
color ΔE76 ≤ 15 en imagen generada y hex exacto en CSS y SVG; 2) el «30» de 60/30/10 queda sin cota hasta que gimg mida
por familia; 3) Steam se amplía con la cápsula vertical de la Deck (I6) y el icono 256², y lo demás de la Deck son
recortes; 4) se pide al juego que fusione UX-40 en `main` antes de recibir imágenes; 5) `castle` es palabra vetada;
6) el mapa de Helek es **pintado**, con el acabado de las ilustraciones del juego; 7) Reddit usa E1 y E2. «Paleta» son los 16 hex de `brand.palette` (`examples/tarkor/galivelop-images.json`). ΔE es ΔE76, la
distancia euclídea en Lab de `gimg/measure.py` (l.83-84), con su umbral `DELTA_E = 15.0` (l.25).

### Color

| Id | Regla | Cómo se comprueba |
|---|---|---|
| C1 | En CSS, SVG y composición, todo color **DEBE** ser un hex de la sección 3, exacto (ΔE = 0) | `grep` de hex en el archivo contra la sección 3 |
| C2 | En imagen generada, un color cuenta como de paleta si está a ΔE ≤ 15 de uno de sus hex. **NUNCA** otra tolerancia (decisión 1) | `gimg measure` (`palette_share`, `measure.py` l.170) |
| C3 | Un paisaje (`og`, `banner`, `social`, `header` de fondo) **DEBE** tener ≥ 30 % de píxeles de paleta | `gimg measure`; calibración del 2026-11-02 (sección 3, «Medido») |
| C4 | El oro (`#ffe9a8`, `#f2c45a`, `#b8862b`, `#7a5a1e`, `#5a3a14`, a ΔE ≤ 15) **NUNCA** pasa del 10 % de los píxeles de una pieza | Sin comando: hueco de gimg (sección 15). Hasta entonces, a ojo y apuntado como «no medido» |
| C5 | El brillo (`#ffe9a8` y el halo `#ffd66b`) **NUNCA** pasa del 5 % de los píxeles | Igual que C4 |
| C6 | El cristal (`#1f4a55`, `#2f6b7a`, `#4aa8d8`, `#a8d8f0`) **NUNCA** pasa del 10 % y **NUNCA** es acento fuera del juego: solo campo del emblema o gema | Igual que C4 |
| C7 | Madera o noche **DEBEN** sumar ≥ 60 % de los píxeles. El 30 (hierro y piedra) no tiene cota hasta que se fije (decisión 2); gimg ya mide por familia: `python3 -m gimg measure pieza.png --family "madera-noche=#1b130c,#332415,#46311d,#5c4126,#0f1428,#1a2140" --family "hierro-piedra=#0e0b08,#171310,#221c16,#3a342d,#6b6257" --family "oro=#ffe9a8,#f2c45a,#b8862b,#7a5a1e,#5a3a14"` (madera/noche, hierro+piedra, oro; ΔE76 < 15, el resto en `otros`) | Igual que C4 |
| C8 | Fuera del juego (og, avatar, cabeceras, cápsulas, hero, instalador de Windows) el fondo **DEBE** ser noche `#0f1428` → `#1a2140`. Dentro del juego y del asistente, madera `#1b130c` | A la vista, con el hex de la esquina superior |
| C9 | **NUNCA** `#000000` ni `#ffffff`, ni morado o violeta, ni arcilla `#E0703A` en una pieza de marca | `grep -i '#000\b\|#fff\b\|#e0703a'` en CSS y SVG; en imagen, a la vista |
| C10 | Un solo acento por pieza: el oro. **NUNCA** dos | A la vista |
| C11 | Degradados: solo `#f2c45a` → `#7a5a1e` (bisel), `#1f4a55` → `#2f6b7a` (campo) y `#0f1428` → `#1a2140` → `#0e0b08` (noche). **NUNCA** otro | `grep gradient` en CSS y SVG |

### Texto sobre imagen

| Id | Regla | Cómo se comprueba |
|---|---|---|
| T1 | Ningún modelo pinta letras. Todo texto **DEBE** llegar por composición (`compose`) o por CSS | El prompt no lleva `text`, `letters`, `title`, `caption`, `sign` |
| T2 | Contraste **DEBE** ser ≥ 4,5:1; ≥ 3:1 solo en titulares de 24 px o más. Medido en el peor punto de la caja, no en la media | `gimg measure` sobre la pieza compuesta (medidas previas: sección 12, «Contraste del texto») |
| T3 | Pares que valen sin medir (calculados, sección 3): hueso `#f1e4d0` sobre `#0f1428` 14,55 · sobre `#1a2140` 12,54 · sobre `#1b130c` 14,63 · sobre `#332415` 11,93; `#f2c45a` sobre `#0f1428` 11,14; `#b8862b` sobre `#0f1428` 5,63; `#221c16` sobre hueso 13,44; `#5a3a14` sobre hueso 8,17; `#7a5a1e` sobre hueso 5,06 | — |
| T4 | **NUNCA** `#b8862b` como tinta sobre hueso (2,58:1) | `grep` en CSS y plantillas |
| T5 | Texto sobre escena generada **DEBE** caer en la zona libre declarada del perfil (sección 9, «Zona reservada»). **NUNCA** con velo: si no llega a T2, la pieza se repite | Caja del `<text>` de la plantilla dentro de la fracción declarada |
| T6 | Familias: Cinzel en titulares (700; 900 solo en el hero), Inter en texto (400; 500 en el eyebrow). **NUNCA** otra familia en una pieza de marca | `fonts` del perfil y `font-family` de la plantilla |
| T7 | El lema bajo el lockup de la og **DEBE** ir en Inter 400, 30 px, `#f1e4d0` al 0,82, centrado | `plantillas/og.svg`; `tests/test_examples.py` `TarkorOgE3Tests` |

### Logo

| Id | Regla | Cómo se comprueba |
|---|---|---|
| L1 | El emblema, el wordmark y los lockups **DEBEN** salir de los SVG de `docs/marcas/tarkor/logos/`. **NUNCA** los pinta un modelo ni se nombran en un prompt | Palabras vetadas (P2) |
| L2 | Emblema completo: **NUNCA** por debajo de 64 px. De 64 px para abajo, `tarkor-emblema-simple.svg` | Tamaño del `<image>` en la plantilla |
| L3 | Mínimos: lockup horizontal 160 px de ancho; lockup vertical 96 px de alto; wordmark 20 px de alto plano y 40 px tallado | Igual |
| L4 | Margen libre alrededor del logo **DEBE** ser ≥ la altura de la T del wordmark en esa pieza | Medido en la plantilla (og: ≈ 65 px) |
| L5 | **NUNCA** estirado, rotado, con sombra arrojada, con brillo fuera del bisel, ni el aro sin sus cuatro puntos | `transform` y `filter` del `<image>` en la plantilla |
| L6 | **NUNCA** sobre morado, arcilla ni foto sin noche o madera debajo | A la vista |
| L7 | En una pieza con logo, el logo **DEBE** ser lo más claro de la pieza | Luminancia máxima del fondo < la del oro `#f2c45a` en la caja del logo; a ojo hasta que gimg lo mida |
| L8 | Tamaños fijados: og, emblema al 45 % del alto (283,5 px en 630); cápsula, emblema al 60 % del hueco; cabecera, emblema en el tercio izquierdo; lateral del instalador, lockup vertical a 120 px de ancho en la de 164; cabecera del instalador, emblema simple a 41 px en 57 | Plantilla de cada pieza |

### Prompt y generación

| Id | Regla | Cómo se comprueba |
|---|---|---|
| P1 | Todo prompt **DEBE** empezar por el bloque común (materia) o el bloque de noche (cielo), literal (sección 6 y `peticiones.md` §2) | Comparación de cadenas con el pedido en `orders/` |
| P2 | **NUNCA** en un prompt: `moon`, `sun`, `star`, `stars`, `emblem`, `logo`, `title`, `text`, `letters`, `sign`, `caption`, `watermark`, `glowing`, `flare`, `purple`, `violet`, `like`, `human`, `man`, `woman`, `people`, `castle` (decisión 5), nombres propios, ni las de la sección 6 | `grep -iw` de la lista sobre `orders/` |
| P3 | **NUNCA** una negación (`no`, `not`, `without`, `never`, `none`, `nothing`), salvo el `no haze` de los bloques. Sin prompt negativo | Igual |
| P4 | La zona libre **DEBE** describirse como cielo o madera lisa, con su fracción desde el borde. **NUNCA** por lo que irá encima | Lectura del pedido |
| P5 | Lado múltiplo de 64 y ancho × alto ≤ 1 048 576; `cfg` 1.0; `euler` | `galivelop-images.json`; lo valida gimg |
| P6 | Lo que se entrega **DEBE** salir de `zimage-turbo-q6` a 8 pasos con `draft: false`. FLUX, solo bocetos | Manifiesto de la entrega |
| P7 | De 2 a 3 semillas por pieza; de 6 a 10 cuando importa un recuento. Lo que exige un recuento exacto **NUNCA** se pide pintado: va al SVG | Número de intentos en el manifiesto |
| P8 | Pieza con transparencia: la frase de croma **DEBE** cerrar el prompt; verde `#00ff00`, o magenta `#ff00ff` si la pieza lleva verde; recorte con `gimg matte` | Pedido y archivo `-alpha.png` |
| P9 | Pieza suelta (icono, esquina, sello): centrada, de frente, con ≥ 15 % de margen libre por lado | Caja del recorte en `-alpha.png` |

### Aceptación por tipo de pieza

| Id | Regla | Cómo se comprueba |
|---|---|---|
| A1 | Textura en mosaico: repetida 4×4 **NUNCA** enseña costura ni un motivo que se repita | Montaje 4×4 a la vista; perfil con `tileable` |
| A2 | Icono de interfaz o de mapa: **DEBE** leerse a 24 px en gris | Reducción a 24 px, sin color |
| A3 | Icono de estado del asistente: **DEBE** leerse a 20 px en gris | Igual, a 20 px (Instalador, doc 13 §3, `d9d33fe`) |
| A4 | Cápsula vertical: **DEBE** leerse a 200 px de ancho | Reducción a 200 px (doc 13 §3) |
| A5 | Fondo bajo texto del asistente (I4): luminancia media **DEBE** ser < 40 sobre 255 | YAVG de `gimg measure` (doc 13 §3) |
| A6 | Paisaje: YAVG 105-150 y SATAVG 18-32. Las piezas de noche y de materia **NUNCA** se juzgan por estos rangos | `gimg measure` (sección 7) |
| A7 | EMD frente a la portada: Cb ≤ 6 y Cr ≤ 7,5, solo en paisajes | `gimg measure` (sección 12) |
| A8 | Imágenes del asistente: WebP a calidad 85, o PNG si llevan transparencia; **NUNCA** más de 1 MB entre todas | `du -cb app/src/imagenes/*` en el Instalador (doc 13 §2) |
| A9 | BMP del instalador de Windows: 24 bits, **NUNCA** con alfa | `file lateral.bmp cabecera.bmp` |
| A10 | Recuentos (seis gajos, cuatro puntas, tres picos): la pieza se acepta solo si el número es exacto | Contado a mano |
| A12 | Mapa de Helek: terreno e iconos **DEBEN** ser pintados (pincelada visible, acabado de `estilos.mapa` del juego). **NUNCA** vector plano, tinta plana ni contorno uniforme (decisión 6) | A la vista, al 100 %; el prompt lleva el bloque de terreno o el de icono de la sección 6, literal |
| A11 | El veredicto **DEBE** apuntarse en `docs/records/contenido/rN-<tema>.md` con el intento (`qNNN`) | Existe la línea |

## 17. Matriz de cobertura (2026-11-12)

Cada tipo de contenido, con lo que le aplica. **Bloque:** `común` (materia), `noche`, `terreno` e `icono` (mapa),
`—` (no se genera: se compone). **Estado:** `hecho` (aprobado o entregado), `pedido` (hay prompt escrito),
`falta` (ni prompt ni pieza), `ajeno` (lo hace otro sistema). Medidas: generado → entregado.

### Interfaz del juego, por pantalla

Clases y líneas de `frontend/src/index.css` en `c858a150` (rama `claude/marca-interfaz`, sin fusionar a `main`). El reparto por pantalla se recomprobó el 2026-11-12 en los componentes de ese commit (`git grep` de cada clase y de cada emoji); las líneas de la columna «Pieza» son de ahí.

| Pantalla | Pieza | Reglas | Bloque | Perfil | Salida | Formato | Estado | Fuente |
|---|---|---|---|---|---|---|---|---|
| Todas (`App.tsx`, `ErrorBoundary.tsx`) | #3 madera de fondo, `.wood-grain` l.154 | C7, A1 | común | `textura` | 1024² | PNG mosaico | pedido | `peticiones.md` §3 A |
| Inicio (`Home.tsx` l.20) y tarjeta de Helek Sirik (`WorldCard.tsx` l.25) | #6 cielo, `.crystal-sky` l.316 | C8, C11, P2 | noche | `cielo` | 1536×640 | PNG | pedido (prompt rehecho el 2026-11-12) | `peticiones.md` §3 A |
| Inicio | Titular `.title-gold` l.462 (`Home.tsx` l.30, único uso), filete `.gold-hairline` l.277 | T6, C11 | — | — | CSS | CSS | hecho en rama | WMF `c858a150` |
| Inicio | Emoji ⚔️ de la tarjeta (`Home.tsx` l.45) | A2 | común | `icono` | 512² → 64² | PNG alfa | falta: ningún pedido lo cubre (vale la pestaña «personaje» del #11) | WMF `c858a150` |
| Inicio | E5 fondo del hero | C8, T5 | noche | `cabecera` | 1536×512 | PNG | pedido | `peticiones.md` §3 E |
| Carga | E6 pantalla de carga | C8, T1 | noche | `carga` | 1280×704 | PNG | pedido (`orders/ui/e06-carga.json`) | `peticiones.md` §3 E |
| Carga y progreso | E7 pista y relleno | C4, A1 | común | `tira` | 1024×128 → 1024×32 | PNG alfa | hecho (q357, q359); se regenera con los prompts nuevos (#659-666, 2026-11-12); sin entregar | sección 12 |
| Mundos (`WorldCard.tsx`), personajes (`CharacterCard.tsx`, `CharacterSelect.tsx`, `CharacterSaves.tsx`), modales (`ModalShell.tsx`, `DetailModal.tsx`, `EspecializacionModal.tsx`), avisos (`Notificaciones.tsx`) y mapa (`InteractiveMap.tsx`) | #2 tablón, `.plank-panel` l.192 | C7, A1 | común | `textura` | 1024² | PNG mosaico | pedido | `peticiones.md` §3 A |
| Personajes (`CharacterSelect`, `CharacterSaves`) | #2 tablón; E11 marco de retrato | A10, P8 | común | `icono` | 512² → 96² y 192² | PNG alfa | hecho con arreglo (q365); se regenera con los prompts nuevos (#659-666, 2026-11-12) | sección 12 |
| Partida, cabecera y pie (`GameHeader.tsx`, `GameFooter.tsx`), riel plegado (`CollapsedRail.tsx`), cajón (`PanelDrawer.tsx`) y barra lateral derecha (`SideNav.tsx` l.34) | #5 banda, `.iron-band` l.246 | C4, A1 | común | `banda` | 1024×256 | PNG mosaico x | pedido | `peticiones.md` §3 A |
| Partida, cabecera | #13 fases (8) | A2, P8, P9 | común | `icono` | 512² → 64² y 32² | PNG alfa | pedido | `peticiones.md` §3 C |
| Partida, narración (`LogPanel.tsx`, `ChatComposer.tsx`) y barra lateral izquierda (`SideNav.tsx` l.34) | #4 camino de polvo, `.dust-road` l.177 | C7, A1 | común | `textura` | 1024² | PNG mosaico | pedido | `peticiones.md` §3 A |
| Partida, combate (`CombatPanel.tsx` l.483) | #7 tablón de defensa, `.plank-panel-defense` l.223 | A1 | común | `textura` | 1024² | PNG mosaico | pedido | `peticiones.md` §3 A |
| Partida, tiradas (`DiceRoll.tsx` l.113 y, además, `CombatExchangeBadge.tsx`, `RollBadge.tsx`, `ExtendedRollBadge.tsx`, `GatheringDiceReveal.tsx`, que el pedido no nombra) | #14 dado | A2, A10, P8 | común | `icono` | 512² → 64² y 32² | PNG alfa | pedido | `peticiones.md` §3 C |
| Partida, HUD (`HungerBar.tsx` l.16, `ThirstBar.tsx` l.14, `EnergyBar.tsx` l.9; `SkillBarHud.tsx` l.43-72 y `GameFooter.tsx` l.115) | #12 barras (3); #10 ranura, `.skill-slot` l.422 | A2, P8 | común | `icono` | 512² → 64², 32²; 88² | PNG alfa | pedido | `peticiones.md` §3 B y C |
| Partida, cajón (`NavTabs.ts` l.23, `PersonajePanel.tsx` l.22) | #11 pestañas (12) | A2, P8, P9 | común | `icono` | 512² → 128² y 64² | PNG alfa | pedido | `peticiones.md` §3 C |
| Narración y barra lateral (`LogPanel.tsx` l.196, `SideNav.tsx` l.34: `.corner-bracket` l.348; `.corner-bracket-gold` l.372 no lo usa ningún componente) | #8 esquinas; #9 separador | C4, P8 | común | `icono`, `tira` | 512² → 128²; 1024×128 → 1024×64 | PNG alfa | pedido | `peticiones.md` §3 B |
| Enciclopedia | #15 categorías (15); #16 medallón | A2, L1, P8 | común | `icono`, `emblema` | 512² → 64²; 768² | PNG alfa | pedido (#16 rehecho el 2026-11-12: la Semilla, por composición) | `peticiones.md` §3 C |
| Botones y avisos | E13 botón ×3; E10 insignia; E9 sello; E17 tooltip | T1, L1, P8 | común | `banda`, `icono` | 128×48; 160×80; 96²; 128×64 | PNG alfa | E10 y E9 pedidos (`orders/ui/`, sincronizados con `peticiones.md` el 2026-11-12); E13 y E17 falta | `peticiones.md` §3 E |
| Capturas | E12 plantilla | P8 | común | `marco` | 1280×704 | PNG alfa | hecho con arreglo (q366); se regenera con los prompts nuevos (#659-666, 2026-11-12) | sección 12 |
| `ComingSoon`, `Admin*` | Ninguna propia | — | — | — | — | — | falta: sin pedido del juego | WMF `c858a150` |

### Mundo: regiones, mapa, personajes

| Contenido | Reglas | Bloque | Perfil | Salida | Formato | Estado | Fuente |
|---|---|---|---|---|---|---|---|
| Biomas (13) como textura de terreno, M-A (15 piezas) | A1, hex por bioma de `pedido-mapa.md` l.58-70 | terreno | `texturamapa` | 1024² | PNG mosaico xy | pedido; la prueba se repite con el bloque pintado (A12) | `pedido-mapa.md` §3 |
| Relieve y vegetación, M-B (10) | A2, A10, P8 (magenta si lleva verde) | icono | `iconomapa` | 768² | PNG alfa | pedido; la montaña q373 salió en vector plano: se repite pintada (A12) | `pedido-mapa.md`; sección 12 |
| Fichas de lugares, M-C (13) | A2, P8 | común | `iconomapa` | 768² | PNG alfa | pedido | `pedido-mapa.md` |
| Cartografía y marco, M-D (6) | A1 (marco), T1 (cartela vacía) | común | `iconomapa`, `cartela`, `bandamapa`, `marcomapa` | 768²; 1024×512; 1024×256 | PNG | pedido | `pedido-mapa.md` |
| Capas del juego, M-E (4) | A1, C9 | terreno | `texturamapa`, `iconomapa` | 1024²; 768² | PNG | pedido | `pedido-mapa.md` |
| Estilo del mapa | A12: pintado, con el acabado de las ilustraciones del juego | terreno | — | — | — | decidido por la persona, 2026-11-12 | sección 6 |
| Mapas de zona 832×624, banners 1280×512 y miniaturas 768² de fichas (lugares, fauna, flora, objetos, PNJ, razas, facciones) | Las de `image-generator/estilo/mundo.json` del juego, no las de esta hoja | — | — | — | — | ajeno (WMF-imagenes) | `peticiones.md` §4 |
| Personajes y criaturas en piezas de marca | **NUNCA** (sección 6, «Motivos No»; P2) | — | — | — | — | no se hace | sección 6 |
| Iconos de habilidad, clase y asentamiento | Las del juego | — | — | 512² | — | ajeno (WMF-imagenes) | `peticiones.md` §4 |

### Logo e iconos de aplicación

| Contenido | Reglas | Perfil | Salida | Formato | Estado | Fuente |
|---|---|---|---|---|---|---|
| Emblema, emblema simple, emblema mono, wordmark, lockup h y v | L1-L7 | `gimg brand system` | vectorial | SVG | hecho | `docs/marcas/tarkor/logos/` |
| Variantes `-claro` y `-mono` de cada pieza; glifo (E16); monograma | L1, C1 | `gimg brand` | vectorial | SVG | falta (hay `tarkor-emblema-mono.svg` y `tarkor-a-lockup-claro.svg`) | sección 4 |
| Favicon del juego | L2 | — | vectorial | SVG | hecho aquí; sin colocar en el juego | `tarkor-emblema-simple.svg` |
| E14 icono de aplicación (= I5) | L2, C8: disco `#0f1428` | composición | 1024, 512, 256, 128, 64, 32 y `.ico` 16/24/32/48/64/256 | PNG, ICO | falta: sin pedido; ICO es hueco de gimg | `peticiones.md` E14; doc 13 §3 A |
| E1 avatar | L2, C8 | `avatar` | 1024² → 512², 400², 256² | PNG | pedido (rehecho el 2026-11-12: fondo de noche generado y emblema por composición) | `peticiones.md` E1 |

### Instalador (Instalador-WMF-Tarkor, `docs/13-hoja-de-estilos-e-imagenes.md`, `d9d33fe` y `608661d`)

| Id | Contenido | Reglas | Bloque | Perfil | Salida | Formato | Estado |
|---|---|---|---|---|---|---|---|
| I1 | Lateral de NSIS | C8, L8, A9, P4 | noche | `lateral` 704×1344 | 164×314 y 328×628 | BMP 24 bits | pedido; BMP con `gimg export` |
| I2 | Cabecera de NSIS | C1, L2, L8, A9 | — | composición | 150×57 y 300×114 | BMP 24 bits | pedido; BMP con `gimg export` |
| I3 | Portada del asistente | C8, T1, A8 | noche | `cabecera` | 1536×512 → 1536×384 | WebP q85 | pedido; recorte y WebP (sin pérdida) con `gimg export` |
| I4 | Hierro del riel | A1, A5, A8 | común | `textura` | 1024² | WebP q85 mosaico xy | pedido |
| I5 | Icono del instalador | = E14 | — | — | `.ico` | ICO | falta |
| I6 | Cápsula vertical de la Deck | C8, L1, A4 | noche | `portrait` | 896×1152 → 768×1152 → 600×900 | PNG | pedido (aprobada el 2026-11-12, decisión 3) |
| #17 | Estados de comprobación (4) | A3, P8 | común | `icono` | 512² → 64² y 32² | PNG alfa | pedido (`orders/ui/17-estado-{aviso,en-curso,error,hecho}.json`) |
| #5, #2, #3, #9, E7, E13 | Barra, tablón, fondo, filete, progreso, botón | Las del juego | común | — | — | PNG | las mismas piezas del juego |

### Steam

| Contenido | Reglas | Perfil | Salida | Formato | Estado | Fuente |
|---|---|---|---|---|---|---|
| Cápsula principal y cabecera (E4) | C8, L8 | `capsula` | 1024×576 → 616×353 y 460×215 (231×87 sale de la cabecera) | PNG | pedido (`orders/marca/e04-capsula.json`); rechazada q352 y q353, se rehace | sección 12 |
| Cápsula horizontal de la Deck | C8, L8 | `capsula` | 1024×576 → 1024×478 → 920×430 | PNG | falta: recorte de E4 (decisión 3); `gimg export --crop 0,49,1024,478 --size 920x430` | doc 13 §3 D |
| Cápsula vertical | A4 | `portrait` | 600×900 (I6); 374×448 en la tienda | PNG | pedido (decisión 3) | doc 13 §3 D; `peticiones.md` E4 |
| Fondo (E5) | C8, sin logo | `cabecera` | 3840×1240; 1920×620 en la Deck | PNG | pedido; escalado, hueco | `peticiones.md` E5 |
| Logo | L1, L3 | — | 1280×720 transparente | PNG | falta: es `tarkor-lockup-v.svg` rasterizado | doc 13 §3 D |
| Icono | L2 | — | 256² | PNG | falta: es E14 (aprobado el 2026-11-12, decisión 3) | doc 13 §3 D |

### Redes, Portal y tarjetas

| Contenido | Reglas | Perfil | Salida | Formato | Estado | Fuente |
|---|---|---|---|---|---|---|
| og:image (E3) | C8, L8, T7 | `og` | 1280×640 → 1200×630 | PNG | pedido (`orders/marca/e03-og.json`); se rehace | sección 9 |
| X, cabecera (E2) | C8, L8, P2 | `cabecera` | 1536×512 → 1500×500 | PNG | pedido; rechazada q349; prompt rehecho el 2026-11-12 | sección 12 |
| X, Discord, GitHub, itch: avatar (E1) | L2, C8 | `avatar` | 400² | PNG | pedido | fila E1 |
| Discord, cabecera | C8 | `discord` | 1344×768 → 960×540 | PNG | perfil desde el 2026-11-13 | `peticiones.md` E2 |
| LinkedIn, cabecera | C8 | `linkedin` | 1536×384 → 1584×396 | PNG | perfil desde el 2026-11-13 | sección 9 |
| Reddit | L2, C8 | `avatar`, `cabecera` | las de E1 y E2 | PNG | usa E1 y E2, sin pieza propia (decisión 7) | decisión de la persona, 2026-11-12 |
| Publicación cuadrada y vertical | C3, T5 | `square`, `portrait` | 1024² → 1080²; 896×1152 → 1080×1350 | PNG | perfiles declarados en FLUX; pasan a Z-Image antes de entregar | sección 9 |
| Portal, ficha de Tarkor: portada | C3, T1 | `banner` | 1280×512 → 1600×640 | WebP | consta una portada (Portal `aa76b34`, vía `biblia.md` §10); con la marca del 2026-11-10, falta | sección 11 |
| Portal, novedades | C3 | `banner` | 1600 px y `-mini` 720 px | WebP | falta | sección 11 |
| Tarjetas de `gw-media-content` (juego) | C8, C9, T2, T6 | — (HTML del juego) | 1600×900, `es` y `en` | PNG | ajeno; hoy con la paleta del Portal: se propone cambiarla | WMF `3a10a3fa`, `.claude/gw/gw-media-content.md` |
| Hoja de contactos (E18) | — | composición | 1536×640 | PNG | falta | `peticiones.md` E18 |

## 18. Estado de los repos (2026-11-12)

Los mismos commits que citan las secciones 0 y 13 desde el 2026-11-12.

| Repo | Ref | Commit | Qué hay de marca |
|---|---|---|---|
| World-Maker-Fantasy | `origin/main` | `3a10a3fa` | Sin tokens `gold-*`, `night-*` ni `crystal-deep`; favicon de Vite; `docs/media/guia-canales.md` (antes `docs/difusion/`) |
| World-Maker-Fantasy | `origin/claude/marca-interfaz` | `c858a150` | UX-40 hecha y comprobada en pantalla, **sin fusionar**: tokens (index.css l.55-66), `.gold-hairline` l.277, `.corner-bracket-gold` l.372, `.title-gold` l.462; `theme-color`, `og:title` y `og:description` en `index.html`. UX-41 (imágenes) espera a este repo |
| Instalador-WMF-Tarkor | `origin/main` | `5631e77b` | — |
| Instalador-WMF-Tarkor | `origin/claude/installer-docs-review-09e7vs` | `34d2bb27` | `docs/13-hoja-de-estilos-e-imagenes.md` (`d9d33fe`, `608661d`): pide I1-I6. `app/src/estilos.css` aún sin oro ni noche (INS-56) |
| WMF-imagenes | — | — | Clon del mismo origen que el juego; nada que cambiar por esta hoja |
| galivelop-image-generator | `agent/hojas-tarkor` | desde `3c04dd1` | 23 perfiles y 16 hex en `examples/tarkor/galivelop-images.json`; sin perfil `lateral` |

La sección 9 decía que E14 va sobre madera 950: va sobre un disco de noche `#0f1428` (decisión de la usuaria en el
Instalador, doc 13 §6.1, `608661d`; ya lo decía `peticiones.md`). Corregido el 2026-11-12.

## Contradicciones

Entre los repos de Tarkor y la biblia (`a50b544`), o entre la biblia y lo que ya generó el motor. Todas **resueltas el
2026-11-04** por delegación, con el criterio de [`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md) (lo publicado manda sobre lo que está en desarrollo; lo compuesto, visto y medido sobre lo escrito; una zona por perfil; la propuesta de la hoja si no choca). La persona no había visto ninguna pieza desde el «no» de r1 **hasta el 2026-11-10**, cuando confirmó la dirección de los dos PNG y aprobó las diez decisiones de la propuesta: la 9 y la 12 quedan superadas (nota en cada una) y se añaden la 13 y la 14.

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
   **Superada el 2026-11-10 (aprobado por la persona):** la arcilla sale de la marca (decisión 6 de la propuesta): el acento es el oro tallado `#b8862b`; el cristal sigue dentro del juego como campo y gema. El Portal sigue presentando a Tarkor en arcilla: ver la 13.
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
    **Superada el 2026-11-10 (aprobado por la persona):** la paleta de la sección 3 sustituye a la del plan y a la de r7; `#f2b34a` no entra (el cálido de marca es `#f2c45a`, el bisel del oro); r2-luz-r1 sigue siendo solo cosa de paisajes.
13. **El acento del Portal.** Portal `aa76b34` presenta a Tarkor en arcilla `#E0703A` (`src/data/proyectos/tarkor.json` l.7) y su
    `docs/marca.md` l.3-4 dice «pendiente de elegir tipografía»; desde el 2026-11-10 el acento de marca es el oro `#b8862b` y la
    tipografía, Cinzel. **Propuesta:** pedir al Portal `#b8862b` en `tarkor.json` y la frase de `marca.md`; hasta entonces el
    Portal y la marca no coinciden (desde aquí no se toca ese repo). **Estado:** pendiente del Portal; apuntado en `docs/handoff.md`.
14. **La configuración sigue en r7.** `examples/tarkor/galivelop-images.json` (`brand.palette`; `og.compose` con `plantillas/og.svg`,
    `tarkor-b-lockup.svg` y Metamorphous/Almendra), `piezas.json` (velos, lockups a/b) y `orders/ui/01-emblema.json` (bloque común y
    prompt viejos) contradicen las secciones 3, 4, 5 y 9. **Propuesta:** rehacerlos con `peticiones.md` cuando se generen las piezas
    (esta tarea solo toca documentos). **Estado:** resuelta el 2026-11-10: `brand.palette` y `01-emblema.json` ya iban con la hoja;
    `og.compose` (plantilla E3 con `tarkor-lockup-v.svg`, Cinzel/Inter) y `piezas.json` (sin velos, lockups nuevos) se rehicieron en
    `claude/tarkor-og-e3`, sección 13. Queda que algún pedido lleve el lema en `text` y que `piezas.py` sepa centrar un lockup (hoy
    pone el logo en una esquina).

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

**Lo que cambió el 2026-11-10:** por primera vez la persona vio algo acabado (los dos PNG) y dijo «sí» a una dirección concreta
en vez de delegarla. Una marca de fantasía se decide mejor con una imagen delante que con tablas de hex. De las cinco
separaciones marca/producto de arriba, tres se cierran (la marca ya no quiere pieza clara, ya no es arcilla contra cristal y el
producto tendrá logo); las dos que quedan (escena de marca, lema en titular) ya no son de paisaje sino de emblema. Lo medido en
r1-r5 sigue valiendo para los paisajes y para nada más.

## Historia: r7 (archivada el 2026-11-10)

r7 (2026-11-04, propuesta nunca aprobada) fue la dirección «lápiz de fantasía»: ilustración a lápiz sobre papel hueso `#f1e4d0`
con un lavado de arcilla `#E0703A`, motivos del juego (Agujas Imán, Osario de la Manada), velo claro, texto en madera 900/700,
tipografía Metamorphous/Almendra y wordmark New Rocker a trazos, y el lockup `logos/tarkor-b-lockup.svg` (Semilla de hierro
partida con siete esquirlas; versión plana en `tarkor-b-lockup-r7a.svg`). La persona la vio el 2026-11-10 junto a los dos PNG y
eligió estos: la Semilla rota con la estrella, oro tallado sobre madera y noche, Cinzel. Sus archivos (`logos/tarkor-b-lockup*.svg`,
`orders/r7-lapiz*.json`, `plantillas/og.svg`, el `compose` de `og`) quedan en git como historia; el bloque completo está en
`git show ef94330:docs/marcas/tarkor/hoja.md` (sección «r7 (2026-11-04)»).
