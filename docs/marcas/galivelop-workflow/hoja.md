# Hoja de estilo mínima: Galivelop-workflow

**Propuesta** (2026-11-04), **Aprobada por la persona el 2026-11-04**; segundo caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md) (F2.12), rellenada
tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y con su misma forma. Complementa a
[`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita, campo a campo y en el orden de la
plantilla. Estados como en [`../README.md`](../README.md): sin marca sale de un repo (ruta en la sección 13); **heredado de
`<marca>`** sale del repo de la marca paraguas (el Portal) leído a través de la biblia; **[P]** es propuesta pendiente de la
persona, con su porqué en la misma celda; *(suposición)* se comprueba en una ronda; «no hay» solo donde la plantilla lo admite.

Commits de referencia: Galivelop-workflow `7d61089` (`main`, 2026-11-04; la biblia cita `56212e8`, anterior); este repo
`78f0083` (`f2-motor`); Portal-Galivelop `aa76b34` (lo heredado, vía `biblia.md` §10 y `docs/marcas/portal/biblia.md`; desde
aquí no se abre ese repo). El repo de Workflow se ha leído **sin modificar nada**.

**Lo primero que hay que saber:** el repo de Galivelop-workflow **no tiene identidad visual propia**: ni CSS, ni SVG, ni
favicon, ni logo, ni paleta declarada. Lo único con color y fuente son las plantillas HTML de su skill `gw-media-content`
(`skills/gw-media-content/template/media/source/*.html`), que traen una paleta genérica «para sobrescribir según el proyecto»
y que el propio repo no sobrescribe (no existe `.claude/gw/gw-media-content.md` en él). Todo lo visual de esta hoja viene, por
tanto, del Portal (heredado) o de la biblia y los prompts de este repo; la identidad **de voz** sí sale del repo de Workflow.

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Galivelop-workflow»: G mayúscula, guion, w minúscula, de una pieza. Así va en el título del `README.md`, en `plugin.json` («Galivelop-workflow served from its own repository») y en el lockup. En los textos del propio repo se le llama «el flujo» | Workflow (`README.md` l.1, `README.es.md` l.1, `.claude-plugin/plugin.json`) |
| Nombre en código | Obl. | `galivelop-workflow` | repo (`examples/galivelop-workflow/galivelop-images.json`, `name`); coincide con `name` de `.claude-plugin/plugin.json` de Workflow |
| Fuente de verdad | Rec. | Galivelop-workflow `main` `7d61089` (voz, propósito, licencia, canales); Portal `aa76b34` (paleta, tipografía, baldosa, acento); este repo `78f0083` (prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a workflow pese a la nota de las líneas); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2 | repo (`docs/records/contenido/r1-fondos.md` l.52-53; `docs/marcas/README.md`, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`, **con tres valores propios justificados**: fondo `#0d1b2a` (no `#06121c`), texto `#eef6fb` (no `#eaf4fa`) y titular Inter (no Sora), porque la biblia toma la paleta y la letra de los siete diagramas `gw-*.svg` que el Portal ya publica del flujo: son lo más parecido a una marca que Workflow tiene. Baldosa del logo, la de la familia (`rx` 30/128, trazo 12) | heredado de Portal-Galivelop `aa76b34` (`docs/diagramas/gw-*.svg`, vía `biblia.md` §2-§3 y §10) |
| Hereda de | Opc. | Portal-Galivelop `aa76b34` (leído solo a través de `biblia.md` §10 y `docs/marcas/portal/biblia.md`) | repo |

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
| Motivos Sí | Obl. | 1) varias líneas finas de luz que corren hacia el borde derecho, se bifurcan y se vuelven a unir, con un nodo redondo en cada unión (el grafo de ramas); 2) un trazo corto de luz («dash») que pasa del final de una línea al principio de la siguiente en un nodo brillante (el relevo, el testigo); 3) celeste en las líneas, unos pocos nodos en ámbar y verde; 4) azul noche plano con rejilla tenue (los diagramas del Portal). Sin usar aún, de la biblia: el sello de revisión (anillo con marca de visto), el cuaderno de bitácora cerrado | repo (`prompts/estilo.txt`, elegido en r2 con el «sí» de la persona en r1; `docs/plan.md` l.634-636; `biblia.md` §7) |
| Motivos No | Obl. | personas, manos, pantallas, teclados, robots, cerebros, circuitos, lluvia de código, neón saturado, texto; la píldora o cápsula (r1 la pintó al pedir «capsule») | repo (`biblia.md` §7; `r1-fondos.md` l.47 y l.57) |
| Palabras vetadas | Obl. | `robot`, `brain`, `circuit`, `code rain`, `capsule`, `pill`, `hand`, `keyboard`, `screen`, `human`, `humanoid`, `spark`, `sparkle`, `magic`, `text`, `letters`, `logo`; más `like` y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7: `robot`, `brain`, `circuit`, `code rain`, `capsule`, `hand`, `keyboard`, `screen`, `like a`); `pill`, `human`, `humanoid`, `spark`, `sparkle`, `magic`, `text`, `letters`, `logo` **[P]** (cierran lo que «Nunca se muestra» nombra y lo que se parece a texto o logo, como pide la plantilla). **`estilo.txt`, `r2-*.txt` y `r5-*.txt` no las contienen; `og.txt` y `orders/r1-og.json` sí llevan `capsule`** (son el prompt de r1, superado) |
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
| 8 | Ningún prompt con palabra vetada, negación ni «like» | **no pasa del todo:** `og.txt` y `orders/r1-og.json` llevan `capsule` (prompt de r1, superado); `estilo.txt`, `r2-palabras/hex/material/luz.txt`, `r5-*.txt`, `orders/r2-control.json` y `r2-luz.json` pasan |
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
