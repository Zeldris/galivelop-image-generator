# Hoja de estilo mínima: galivelop-developer

**Propuesta** (2026-11-04), pendiente de la persona; tercer caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md)
(F2.12), rellenada tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y
[`../galivelop-workflow/hoja.md`](../galivelop-workflow/hoja.md) (las dos aprobadas el 2026-11-04) y con su misma forma.
Complementa a [`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita, campo a campo y en el
orden de la plantilla. Estados como en [`../README.md`](../README.md): sin marca sale de un repo (ruta en la sección 13);
**heredado de `<marca>`** sale del repo de la marca paraguas (el Portal) leído a través de su biblia; **[P]** es propuesta
pendiente de la persona, con su porqué en la misma celda; *(suposición)* se comprueba en una ronda; «no hay» solo donde la
plantilla lo admite. Incluye las tres filas que dejó la hoja de Workflow (acentos en imagen, otro sistema que hace piezas,
canales con «consta / no consta en el repo»).

Commits de referencia: galivelop-developer `8fa309c` (rama `claude/f1-instalacion`, árbol local; el mismo que cita la biblia);
este repo `fd2ae53` (`f2-motor`); Portal-Galivelop `aa76b34` (lo heredado, vía `biblia.md` §10 y `docs/marcas/portal/biblia.md`;
desde aquí no se abre ese repo). El repo de developer se ha leído **sin modificar nada**.

**Lo primero que hay que saber:** el repo de galivelop-developer **no tiene identidad visual**: ni SVG, ni PNG, ni CSS, ni HTML,
ni favicon, ni licencia (`README.md` l.52: «Todavía no hay licencia»). Lleva Galivelop-workflow **0.3.0**, anterior a
`gw-media-content`, así que tampoco tiene plantillas de tarjetas ni paleta genérica que alinear. Todo lo visual de esta hoja
viene del Portal (heredado) o de la biblia y los prompts de este repo; la identidad **de voz** (propósito, límites, campo
semántico, tono) sí sale del repo de developer, y es la más clara de las tres herramientas: `README.md`, `GLOSSARY.md` y las dos
ADR dicen lo que es y lo que nunca hace.

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «galivelop-developer»: en minúsculas, con guion, de una pieza, como se llama el repo y como va en el título del `README.md` y en el `<text>` de los lockups. La orden es `gdev`. En los textos del propio repo se le llama «el agente local» o «el tercer relevo» | developer (`README.md` l.1; `GLOSSARY.md` l.30-33; `docs/plan.md` D8); repo (`logos/galivelop-developer-d-lockup*.svg`) |
| Nombre en código | Obl. | `galivelop-developer` | repo (`examples/galivelop-developer/galivelop-images.json`, `name`); coincide con el nombre del repo y con `galivelop-developer.json`, su archivo de configuración (`README.md` l.38) |
| Fuente de verdad | Rec. | galivelop-developer `claude/f1-instalacion` `8fa309c` (voz, propósito, límites, idiomas, estado); Portal `aa76b34` (fondos, texto, tipografía, baldosa); este repo `fd2ae53` (acento, prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a developer en s3 y s4); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2 | repo (`docs/records/contenido/r1-fondos.md` l.44 y l.52; `docs/marcas/README.md` l.22-24, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`, sin cambiar ningún valor de la familia: fondo `#06121c`, texto `#eaf4fa`, Sora 700 e Inter, baldosa `rx` 30/128 con trazo 12. Solo añade el acento y sus dos tonos | heredado de Portal-Galivelop `aa76b34` (vía `biblia.md` §2-§3 y `docs/marcas/portal/biblia.md` §2); la familia para las herramientas la fija `docs/plan.md` l.662-666 **[P]** (la persona las añadió; la familia la propuso el agente) |
| Hereda de | Opc. | Portal-Galivelop `aa76b34` (leído solo a través de `biblia.md` §10 y `docs/marcas/portal/biblia.md`) | repo |

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
| Resto de la paleta | Rec. | acento oscuro `#157D74` **[P]**; acento claro `#9FE3DA` **[P]**; superficies `#0c1d2b`, `#11283a`; borde `#1b3447`; texto 2 `#9fb4c4`; blanco `#FFFFFF` (trazo del símbolo en la baldosa). `brand.palette` de hoy lleva 4: `#06121c`, `#eaf4fa`, `#2BB3A3`, `#9FE3DA` (los del prompt `r2-hex.txt`); **faltan** `#157D74` y `#FFFFFF` (los del logo) y `#9fb4c4` | repo (`galivelop-images.json`; `biblia.md` §2); superficies, borde y texto 2 heredados de Portal-Galivelop `aa76b34` (`portal/biblia.md` §2) |
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
| Logo fuera de la paleta | Opc. | `#157D74` y `#FFFFFF` están en el SVG y **no** en `brand.palette` de la configuración; sí en la tabla de la biblia | repo (diferencia entre `galivelop-images.json` y `biblia.md` §2) |

Copia en `examples/galivelop-developer/logos/`: **no hay** (F2.10, dec. 3, pendiente); `piezas.json` apunta hoy a
`docs/marcas/…/logos/`. En r4 el lockup de 770×128 salía a ~34 px de alto; desde entonces el piloto lo pone al 9 % del alto de la
pieza (`r4-composicion.md` l.29-33). El repo de developer no tiene favicon ni logo: el `d` sería el primero.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Rec. (familia Galivelop) | Sora 700 (reserva `sans-serif`); tracking −0,02 em en títulos y −0,03 em en el wordmark | heredado de Portal-Galivelop `aa76b34` (`Logo.tsx` vía `portal/biblia.md`); repo (`piezas.json` `fuente`; `componer.py` l.119 `peso_titulo=700`; lockups `font-family="Sora, sans-serif"`) |
| Familia de texto | Rec. | Inter (reserva `sans-serif`); la biblia pide 400/600, las piezas salieron a 400 con opacidad 0,82 (ver «Contradicciones», 2) | heredado de Portal-Galivelop `aa76b34`; repo (`piezas.json` `fuente_texto`; `componer.py` l.160); `biblia.md` §3 |
| Licencia y archivo | Rec. | Sora e Inter, OFL, del repo `google/fonts`; `examples/pilot/fuentes.sh` las baja a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`; no instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)*. DejaVu Sans Mono (órdenes `gdev task`, rutas): fuente del sistema, sin archivo en ningún repo *(suposición: instalada en la Deck)* | repo (`examples/pilot/fuentes.sh` l.8-12); la monoespaciada **[P]** (`biblia.md` §3, sin pieza que la use) |
| Tracking y mayúsculas | Opc. | títulos Sora −0,02 em; wordmark −0,03 em; sin mayúsculas sostenidas (el nombre va «galivelop-developer», minúsculas, con su guion, en una línea y un solo color); monoespaciada para claves y órdenes (`gdev task <nombre>`, `local/<tarea>`, `galivelop-developer.json`) | heredado de Portal-Galivelop `aa76b34` (vía `biblia.md` §3); la monoespaciada **[P]** |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | 1) una línea recta horizontal de luz blanca suave que corre desde el centro hasta el borde derecho (las sesiones, el tronco); 2) una rama de luz teal que sale de la línea, da una vuelta grande y cuidada que llena la mitad derecha y vuelve a la línea pasando por un anillo brillante (la tarea local que vuelve revisada); 3) la rama y el anillo brillan con fuerza y echan un halo teal sobre el fondo; 4) azul noche plano con rejilla de puntos tenue (la web del Portal). Sin usar aún, de la biblia: tres relevos paralelos, una consola vacía (solo la forma) | repo (`prompts/estilo.txt`, elegido en r2 con el «sí» de la persona en r1 sobre `og.txt`; `docs/plan.md` l.673; `biblia.md` §7) |
| Motivos No | Obl. | personas, manos, robots, cerebros, pantallas, teclados, código legible, nubes (es local), engranajes, chips y circuitos, texto; **hojas o brotes en la rama** (r2 material los pintó: la rama es luz, no planta) | repo (`biblia.md` §7; `docs/plan.md` l.667); las hojas, `r2-estilo.md` l.47 |
| Palabras vetadas | Obl. | `robot`, `brain`, `cloud`, `chip`, `circuit`, `gear`, `hand`, `screen`; más `like` como comparación y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7). **Añadidas [P]:** `face`, `person`, `human`, `humanoid`, `magic`, `spark`, `sparkle`, `keyboard`, `code`, `text`, `letters`, `logo` (cierran lo que «Nunca se muestra» nombra y lo que se parece a texto o logo, como pide la plantilla) y `leaf`, `leaves`, `foliage`, `plant` (lo que r2 material pintó). **Ojo:** todos los prompts dicen «a side branch … **leaves** the main line» (verbo) y «branch» es también rama de árbol: *(suposición)* que esa pareja es lo que invitó el brote de hojas; se propone «departs from the main line» en la próxima ronda, sin cambiar nada más, para comprobarlo. Ningún prompt contiene las ocho de la biblia ni negaciones; `vector-like` dispara un grep de palabra entera (ver comprobación 8) |
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
| Perfiles | Obl. | en la configuración: `og` 1280×640 (**sin** `targetWidth`/`targetHeight` 1200×630) y `social` 1280×640 (= destino). Hechos en el piloto y sin perfil: `square` 1024×1024 → 1080×1080 (`cuadrado`), `portrait` 896×1152 → 1080×1350 (`vertical`), `header` 1536×512 → 1500×500 (`cabecera`) | repo (`galivelop-images.json`; `piezas.json`); los tres de r5 **[P]** (bitácora: «lo decide la persona» en F2.8; `docs/plan.md` l.752) |
| Zona reservada | Obl. | **lo que piden los prompts:** `og`, `social`, `header`: `izquierda 1/2` («The left half of the frame is a plain, empty dark background with only the faint grid»); `square`, `portrait`: `arriba 1/2` («The upper half of the frame is a plain, empty dark background»). **Lo que compuso el piloto:** `og` y `cabecera` **`abajo 1/2`** (r4: con la zona izquierda la línea de luz cruzaba el título; r5: en la cabecera tocaba la última letra), `cuadrado` y `vertical` `arriba 1/2`. En píxeles (conversión de la plantilla): `og` 1200×630 `abajo` → `0,315,1200,315`; `square` 1080×1080 `arriba` → `0,0,1080,540`. La caja del piloto es 48 % del alto menos margen (`arriba`/`abajo`, 6 %), no 1/2: se alinea al portar a `compose` | repo (`prompts/*.txt`; `piezas.json` `zona`; `componer.py` `caja_zona` l.105-115; `r4-composicion.md` l.34-35; `r5-piezas.md` l.53-55). **La biblia §7 dice «mitad izquierda en og y social; tercio superior en square»; el prompt dice izquierda y la pieza compone abajo** (ver «Contradicciones», 1) |
| Velo por perfil | Rec. | `og` `#06121c:0.55` (el único `og` de la familia con velo; 0,55 no bastó con la zona izquierda y sí con `abajo`); `cuadrado`, `vertical` y `cabecera` `#06121c:0.3` | repo (`piezas.json`, `velo`; `r4-composicion.md` l.22 y l.34-35) |
| Logo en la pieza | Rec. | lockup oscuro al 9 % del alto de la pieza (57 px en el `og`), en lo alto de la caja de la zona con el título debajo, margen 6 %; solo baja si no cabe a lo ancho de la columna | repo (`componer.py` l.124-137; `r4-composicion.md` l.29-33) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 %, título Sora 700, subtítulo Inter 400). Portar a `compose: {template, logo: "logos/galivelop-developer-d-lockup-oscuro.svg", fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-developer-d.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay; el repo de developer no tiene web ni favicon que lo consuma | repo (`piezas.json`); `icon` **[P]** |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos: YAVG/SATAVG/paleta 29/12/91 % frente a 39/12/87 % del definitivo; anticipa el anillo y la línea, pero el definitivo alargó la línea hacia la izquierda (la que luego cruzó el título). Propuesto `draft: {scale: 0.5, steps: 4}` en `og` | **[P]** (F2.10, dec. 7; `r3-borrador.md` l.52 y l.64-66) |
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
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» de la persona en r1 y la palanca de r1 (más presencia a la derecha, línea solo a la derecha) funcionó en r2; r5 dio las tres piezas de formato a la primera, con la zona de la cabecera cambiada a `abajo`. Pendiente: el veredicto de la persona sobre lo delegado y la zona del `og` (sección 9) | repo (registros r1-r5) |

## 13. Fuentes de verdad

**galivelop-developer**, `claude/f1-instalacion` `8fa309c` (árbol local; leído solo, nada modificado):

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
- `docs/marcas/README.md` l.19 (fila del proyecto, elegido **d**), l.22-24 y l.36 («Elegido por el agente»: quién decide, el
  porqué de **d**), l.38 (acento `#2BB3A3`), l.80-99 («Común a todos», tabla de destinos), l.186-191 (conceptos de logo).
- `docs/marcas/galivelop-developer/biblia.md` (`74d99f8`, contenido de `a50b544`; paleta, tipografía, reglas del logo, vetos,
  frases; lo que es **[P]** allí lo sigue siendo aquí).
- `docs/plan.md` l.662-675 («Herramientas del taller»: familia del Portal, acentos [P], *No*, formatos, metáfora de developer),
  l.450-451 y l.752 (`piezas.json` y perfiles de r5: lo decide la persona), l.768 (`avatar`/`icon` a F2.12), l.803 y l.824
  (developer en r3 y r4: la línea que cruzó el título, zona `abajo`).
- `docs/records/contenido/calibracion-measure.md` l.17, l.43, l.73, l.76; `r1-fondos.md` l.44, l.52, l.61; `r2-estilo.md`
  l.21-23, l.47; `r3-borrador.md` l.52, l.64-66; `r4-composicion.md` l.22, l.29-35; `r5-piezas.md` l.36, l.52-55, l.64.
- `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` l.176-185 y l.202-209 (lectura de las herramientas: sin identidad
  visual, límites, metáfora).
- `examples/pilot/componer.py` l.105-115 (`caja_zona`), l.119 (`peso_titulo=700`), l.124-137 (margen 6 %, logo al 9 %), l.135
  (cuerpo del título), l.160 (subtítulo 400, opacidad 0,82); `examples/pilot/fuentes.sh` l.8-12 (origen y licencia de las fuentes).

Sin línea aquí y por tanto **[P]** o *(suposición)*: acento y sus dos tonos, lema y frases, logo elegido, reglas del logo tras
elegir, pieza clara, prohibidos de la paleta, monoespaciada, palabras vetadas añadidas y la hipótesis de «leaves», zona del
`og`/`header` (prompt frente a composición), perfiles `square`/`portrait`/`header`, `draft`, `compose`, `icon`, el Portal como
destino, el mapeo de `Palette:` para un futuro `gw-media-content`.

**Lo que la configuración no refleja aún** (entrada de la propuesta a este repo y a developer):

- `og` sin `targetWidth` 1200 / `targetHeight` 630 (image-generator lo arregló el 2026-11-04; aquí no).
- `square`, `portrait` y `header` generados y compuestos en r5 y no declarados.
- `#157D74` y `#FFFFFF` (los del logo) y `#9fb4c4` fuera de `brand.palette`.
- **La zona del `og` no está en ningún sitio de la configuración y el prompt dice otra:** `estilo.txt` deja libre la mitad
  izquierda y `piezas.json` compone `abajo`; la cabecera igual. Hasta que la persona decida (Contradicciones, 1), la
  comprobación 11 no se puede dar por pasada.
- `compose`: plantilla, fuentes, zona, velo (0,55 en `og`) y logo en la pieza viven en `examples/pilot/componer.py` y
  `piezas.json`.
- Copia de los logos en `examples/galivelop-developer/logos/`: pendiente (F2.10, dec. 3).
- `draft` no declarado.
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
| 8 | Ningún prompt con palabra vetada, negación ni «like» | pasa con matiz: ninguno de los nueve prompts ni los tres pedidos lleva las ocho palabras de la biblia, las añadidas ni `no`/`not`/`without`/`never`; **`vector-like`** (la línea «Style:» de los siete proyectos) dispara un grep de palabra entera sobre `like` sin ser comparación (ver «Cambios que pediría a la plantilla», 1). Todos llevan «leaves» como verbo (hipótesis de la sección 6) |
| 9 | Prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | pasa (121-173 palabras), los nueve |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | múltiplos de 64 pasa; **`og` sin destino declarado** (1200×630) |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | **no pasa:** ningún perfil la declara (hueco) y, en `og` y `header`, el prompt describe la mitad izquierda libre mientras la pieza compone abajo; `square` y `portrait` sí coinciden (`arriba 1/2`) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (17 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |
| 15 | Todo hex de Fondo, Texto y Acento (y del logo) en `brand.palette` | **no pasa:** `#157D74` y `#FFFFFF` del logo, texto 2 `#9fb4c4` y los de la pieza clara no están; los de la pieza oscura sí (`#06121c`, `#eaf4fa`, `#2BB3A3`, `#9FE3DA`) |
| 16 | Destino ≠ generación implica `targetWidth`/`targetHeight` | **no pasa** para `og` (1280×640 → 1200×630); `social` pasa (destino = generación); `square`, `portrait` y `header` no están declarados (hueco) |

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

1. **Abierta: la persona decide la zona del `og` y la cabecera.** **Zona reservada.** Biblia §7: «mitad izquierda en `og` y
   `social`; tercio superior en `square`». Los prompts (`estilo.txt`, `r5-cabecera.txt`) piden la mitad izquierda vacía, pero
   la línea de luz arranca «from the centre of the frame» y la caja del texto llega al 55 % del ancho: en r4 la línea cruzó el
   título y en r5 tocó su última letra, y las dos piezas se compusieron **`abajo`** (`piezas.json`), donde quedan limpias
   (peor 11,82 con velo 0,55; 9,87 con 0,3). `square` y `portrait` piden y componen la **mitad** superior, no el tercio.
   **Propuesta:** (a) declarar `abajo 1/2` para `og`, `social` y `header`, que es lo medido, y reescribir el prompt para que
   diga que la mitad inferior queda libre (línea y bucle en la mitad superior), de modo que prompt, plantilla y medida digan
   lo mismo; o (b) mantener `izquierda 1/2` como el resto de la familia y empujar la línea a la derecha en el prompt («from
   two thirds of the way across», como intenta `r2-luz.txt` con «from the right edge to the middle», sin veredicto), con un
   boceto como `initImage` si no obedece. El agente se inclina por (a): es lo único que ha dado piezas limpias dos veces. En
   los dos casos, `arriba 1/2` para `square` y `portrait` y corregir la biblia.
2. **Abierta: la persona elige viendo una pieza.** **Peso de Inter.** Biblia §3: texto Inter 400/600. Las piezas de r4-r5
   salieron a 400 con opacidad 0,82 (`componer.py` l.160); `piezas.json` no declara peso. **Propuesta:** si prefiere 600 en
   subtítulos, se cambia `componer.py` (o el futuro `compose`) y se recompone sin regenerar; si no, se corrige la biblia a 400.
3. **Resuelta por los datos; la hoja lo dice.** **Velo del `og`.** La plantilla (fila «Velo por perfil») explica «Galivelop
   `0` en `og`, `0.3` en el resto»; el `og` de developer lleva `0.55` (`piezas.json`), porque con la zona izquierda y sin velo
   la línea seguía brillando a la altura del título. La biblia no dice velo. **Propuesta:** la hoja fija `0.55` con la zona
   `abajo`; si la persona elige la zona izquierda (1b), se vuelve a medir.
4. **Abierta, leve.** **Palabras vetadas frente a «Nunca se muestra».** Biblia §1 veta rostros, personas y «magia», y §7 solo
   lista `robot`, `brain`, `cloud`, `chip`, `circuit`, `gear`, `hand`, `screen`: `face`, `person`, `magic` no están. La hoja
   los añade **[P]** con los que se parecen a texto o logo y con `leaf`/`leaves` (r2 material pintó «un brote de hojas»,
   `r2-estilo.md` l.47; todos los prompts dicen «a side branch … leaves the main line»). **Propuesta:** completar §7 y probar
   «departs from the main line» en la próxima ronda, una palanca sola.
5. **Abierta, leve.** **Formato de la biblia §8.** La fila de `estilo.txt` tiene tres celdas en una tabla de dos columnas (la
   tercera lleva r3 y r4), y la fila de `og.txt` dice «r1: sí» sin la palanca de r1 que sí está en `r1-fondos.md` l.61.
   **Propuesta:** una celda de estado por archivo, como en las otras biblias.

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
