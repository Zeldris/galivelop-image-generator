# Hoja de estilo mínima: galivelop-voice-generator

**Aprobada el 2026-11-04** (decisiones delegadas por la persona; ver `docs/records/decisiones-hojas-2026-11-04.md`); tercer caso de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md)
(F2.12), rellenada tras [`../galivelop-image-generator/hoja.md`](../galivelop-image-generator/hoja.md) y
[`../galivelop-workflow/hoja.md`](../galivelop-workflow/hoja.md) (las dos aprobadas el 2026-11-04) y con su misma forma.
Complementa a [`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita, campo a campo y en el
orden de la plantilla. Estados como en [`../README.md`](../README.md): sin marca sale de un repo (ruta en la sección 13);
**heredado de `<marca>`** sale del repo de la marca paraguas (el Portal) leído a través de su biblia; **[P]** es propuesta
del agente, **aprobada por delegación** el 2026-11-04 (la persona no la ha visto pieza a pieza), con su porqué en la misma celda; *(suposición)* se comprueba en una ronda; «no hay» solo donde la
plantilla lo admite.

Commits de referencia: galivelop-voice-generator `ab1ff10` (`claude/voces-f1`, el mismo que cita la biblia; `main` solo tiene el
diseño, PR #2 de ese repo); este repo `fd2ae53` (`f2-motor`; la biblia cita `24d69c8`, anterior); Portal-Galivelop `aa76b34` (lo
heredado, vía `docs/marcas/portal/biblia.md`; desde aquí no se abre ese repo). El repo de voces se ha leído **sin modificar nada**.

> **Hereda de la identidad vigente del Portal (2026-11-11).** Lo que esta hoja dice de fondo, texto, tipografía, modelo,
> estilo de imagen y palabras vetadas (`#06121c`, Sora/Inter, FLUX, cinta de luz frambuesa, veto a `no`/`not`/`like`) es
> la identidad anterior de la familia, con la que se hicieron las piezas de r1-r5: se queda como histórico. **Para cualquier
> pieza nueva manda el bloque «Identidad vigente» de [`../portal/hoja.md`](../portal/hoja.md)**, y esta hoja solo añade lo
> propio: el motivo de la fila «Motivo propio» de la sección 6 y el acento `#D9467A` para logo e interfaz. Lo ético de la
> sección 2 (nada de micrófonos, bocas, rostros ni «clonar») sigue entero.

**Lo primero que hay que saber:** el repo de galivelop-voice-generator **no tiene identidad visual**: ni CSS, ni HTML, ni SVG, ni
favicon, ni logo, ni paleta, ni web. Tampoco tiene licencia («Todavía no hay licencia», `README.md` l.50) ni la skill
`gw-media-content` (su flujo es Galivelop-workflow v0.3.0, anterior a esa skill). Todo lo visual de esta hoja viene del Portal
(heredado), de la biblia y de los prompts y piezas de este repo; la identidad **de voz** (propósito, tono, vocabulario) sí sale del
repo de voces (`README.md`, `GLOSSARY.md`).

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «galivelop-voice-generator»: en minúsculas, con guiones, de una pieza (así va en el título de `README.md` y `README.en.md` y en el lockup). No tiene nombre «bonito»; en los textos del propio repo se le llama «el generador» | voces (`README.md` l.1, `README.en.md` l.1; `GLOSSARY.md` l.32-36, «Generador») |
| Nombre en código | Obl. | `galivelop-voice-generator` | repo (`examples/galivelop-voice-generator/galivelop-images.json`, `name`); coincide con el nombre del repo `github.com/Zeldris/galivelop-voice-generator` |
| Fuente de verdad | Rec. | galivelop-voice-generator `claude/voces-f1` `ab1ff10` (propósito, tono, vocabulario, idiomas, estado); Portal `aa76b34` (fondo, texto, tipografía, baldosa); este repo `fd2ae53` (acento, prompts, piezas, medidas, logos dibujados). Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Dio ella el veredicto de r1 (2026-10-26, «sí» a voice-generator en las semillas 3 y 4); desde entonces, delegado al agente («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2. El 2026-11-04 delegó las dudas de esta hoja y quedó aprobada (`docs/records/decisiones-hojas-2026-11-04.md`) | repo (`docs/records/contenido/r1-fondos.md` l.46 y l.52-53; `docs/marcas/README.md` l.24-38, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`: fondo, texto, tipografía y baldosa son los de la familia, sin cambios (Rec. aquí, no Obl.) | heredado de Portal-Galivelop `aa76b34` (vía `docs/marcas/portal/biblia.md` §2-§4); `docs/plan.md` l.662-665 («Herramientas del taller … entran en la familia del Portal **[P]**»; la familia está confirmada por las piezas de r1-r5, el acento sigue **[P]**) |
| Hereda de | Opc. | **Vigente:** [`../portal/hoja.md`](../portal/hoja.md), bloque «Identidad vigente» (2026-11-10 y 11). **Histórico (piezas r1-r5):** Portal-Galivelop `aa76b34` (leído solo a través de `docs/marcas/portal/biblia.md`) | repo |

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
| Motivo propio (identidad vigente, 2026-11-11) | Obl. | **La onda como dato, no como sonido en el aire:** la forma de onda dibujada como una sola línea, el perfil de profundidad del fondo marino de una carta (lo que el Portal ya le pide en `orders/marca/15-proximamente-voz.json`: «a sound wave drawn as a single depth profile line of the seabed»); en icono, línea simple, las barras de tomas dentro de una ventana de aplicación («an application window holding a row of short vertical bars of varying height, a waveform»), sin número de barras y sin ninguna «encendida» (una tinta: la elegida se marca con un visto o un subrayado, no con color). Nada de micrófono, boca ni cara, como siempre. El pedido 15 nombra en el sujeto lo que no quiere («no rocks, no seaweed, no plants»): se reescribe en positivo («a smooth bare seabed profile») según el punto 2 de «Cómo se escribe el prompt». Acento frambuesa `#D9467A` solo en logo, baldosa e interfaz | **propuesta del agente, 2026-11-11**, según `../portal/hoja.md` «Mar y tecnología»; pieza en `examples/portal/orders/marca/15-proximamente-voz.json` |
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
