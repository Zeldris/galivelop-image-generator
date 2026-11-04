# Hoja de estilo mínima: galivelop-image-generator

Primer caso real de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md) (F2.12), rellenada el 2026-11-04 para
este mismo repo. Complementa a [`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita,
campo a campo y en el orden de la plantilla. Estados como en [`../README.md`](../README.md): sin marca sale del repo (ruta en
la sección 13); **heredado de `<marca>`** sale del repo de la marca paraguas (aquí, el Portal) leído a través de su biblia;
**[P]** es propuesta pendiente de la persona; *(suposición)* se comprueba en una ronda; «no hay» no existe. Puesta al día el
2026-11-04 con la plantilla de los 17 cambios aprobados.

Commits de referencia: este repo `2259370` (rama `f2-motor`); Portal-Galivelop `aa76b34` (lo heredado, vía
`docs/marcas/portal/biblia.md`, que lo lee desde `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`; desde aquí no se
abre ese repo).

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «galivelop-image-generator»: en minúsculas, con guiones, de una pieza (así va en `README.md` y en el lockup). No tiene nombre «bonito»; en los textos se le llama «el generador» | repo |
| Nombre en código | Obl. | `galivelop-image-generator` | repo (`examples/galivelop-image-generator/galivelop-images.json`, `name`) |
| Fuente de verdad | Rec. | Este repo, `f2-motor` `2259370`; Portal `aa76b34` para lo heredado. Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona; delegado al agente el 2026-10-26 («lo dejo en tus manos») hasta que diga otra cosa; cada decisión delegada lleva **[P]** y se le propone al cerrar F2 | repo (`docs/marcas/README.md`, «Elegido por el agente») |
| Fecha de la hoja | Rec. | `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`: fondo, texto, tipografía y baldosa son los de la familia (Rec. aquí, no Obl.) | heredado de Portal-Galivelop `aa76b34` |
| Hereda de | Opc. | Portal-Galivelop `aa76b34` (leído solo a través de `docs/marcas/portal/biblia.md`) | repo |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos»; para los proyectos del taller (Tarkor/WMF el primero) y quien quiera generar en local sin instalar nada | repo (`README.md` l.5-7; `docs/plan.md` D1, D2, D6) |
| Lema | Rec. | «Pide, prueba, elige.» | **[P]** (`biblia.md` §1; no sale de ningún texto del repo) |
| Tono | Rec. | técnico, sobrio, honesto con el estado real («aún no genera imágenes reales» está en el README); nunca vende, nada de «magia» | repo (`README.md` «Estado»; `biblia.md` §6) |
| Idiomas | Opc. | `es` manda (las piezas de r4-r5 van en español); el repo publica también en `en` (`README.en.md`, textos es/en de F0), pero no hay pieza en inglés decidida | repo (`es`); `en` **[P]** |
| Campo semántico | Opc. | dentro: pedido, intento, candidata, descartada, elegida, cola, entrega, manifiesto, perfil, motor, referencia; fuera: render, job, cliente, prompt engineering, «magia» | repo (`GLOSSARY.md`, «Términos del proyecto») |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | cámaras, pinceles, paletas, chispas o «magia» de IA, robots, cerebros, rostros, personas o artistas sustituidos, obras reconocibles, texto generado por el modelo | repo (`docs/plan.md` «Estilos por proyecto», herramientas: *No*; `docs/marcas/README.md` l.172; `biblia.md` §1 y §7) |
| Personas y rostros | Rec. | nunca personas ni rostros (vetados `face`, `person`, `artist`) | repo (`biblia.md` §7) |
| Promesas | Rec. | nada de «arte ilimitado»; no afirmar que ya genera imágenes reales en una pieza mientras el README diga lo contrario; nada de precios ni fechas | repo (`biblia.md` §1; `README.md` «Estado») |

## 3. Paleta

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. (familia Galivelop) | oscura (por defecto) `#06121c`; clara `#f6fafd` | heredado de Portal-Galivelop `aa76b34` (`global.css` vía `portal/biblia.md` §2) |
| Texto | Rec. (familia Galivelop) | `#eaf4fa` sobre oscuro (secundario `#9fb4c4`); `#0a1a28` sobre claro | heredado de Portal-Galivelop `aa76b34`; `#eaf4fa` es el `color_texto` de las piezas de `piezas.json` y ya está en `brand.palette` |
| Acento | Obl. | `#8B5CF6` (uno por pieza); sobre fondo claro, `#5B34C9` | **[P]** (`docs/plan.md` «Estilos por proyecto»; `docs/marcas/README.md` «Acentos de las herramientas») |
| Resto de la paleta | Rec. | acento claro `#A78BFA` (halos, texto de acento sobre oscuro) **[P]**; acento oscuro `#5B34C9` (final del degradado de la baldosa) **[P]**; superficies `#0c1d2b`, `#11283a`; borde `#1b3447`; texto 2 `#9fb4c4`; blanco `#FFFFFF` (trazo del símbolo). `brand.palette` de hoy lleva 5: `#06121c`, `#A78BFA`, `#8B5CF6`, `#ffffff` y el texto `#eaf4fa` (añadido el 2026-11-04) | repo (`galivelop-images.json` `brand.palette`, de `prompts/r2-hex.txt`); el resto heredado de Portal-Galivelop `aa76b34` |
| Combinaciones | Rec. | oscura: `#06121c` + texto `#eaf4fa` + velo `#06121c:0` en `og` (contraste sobra) y `#06121c:0.3` en `square`, `portrait` y `header`; clara: `#f6fafd` + `#0a1a28` + acento `#5B34C9`; sobre imagen: texto blanco en la zona reservada y el logo siempre en su baldosa | repo (`piezas.json`, `velo`); la clara **[P]** (`biblia.md` §2, sin pieza hecha) |
| Prohibidos | Rec. | el celeste del Portal `#1aa6df` como acento de la herramienta; violeta neón o magenta puro; negro `#000`; texto de acento sobre fondo de acento; más de un acento por pieza | **[P]** (`biblia.md` §2) |
| Degradados | Opc. | solo la baldosa del logo (`#8B5CF6 → #5B34C9`) | repo (`logos/galivelop-image-generator-b.svg`); regla de familia en `docs/marcas/README.md` |

**Medido:** la calibración da a este proyecto paleta ≥ 72 % (r1 y r5: 75-88 %; r4 og 72,36 %) con `brand.palette` de 4 hex (medido
antes de añadir el texto `#eaf4fa`) y ΔE76 < 15 (`docs/registros/contenido/calibracion-measure.md`). r2 confirmó que hex, palabras o materiales dan casi la misma
imagen (69,9 / 74,8 / 76,3 %); se eligió «palabras» (`r2-estilo.md`).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/galivelop-image-generator/logos/galivelop-image-generator-b.svg` («rejilla de intentos»: marco 2×2 con una celda encendida, en la baldosa de la familia). Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; colores `#8B5CF6`, `#5B34C9`, `#FFFFFF` | repo (archivo); la elección de **b** es delegada **[P]** (`docs/marcas/README.md`) |
| Lockup (símbolo + nombre) | Rec. | `logos/galivelop-image-generator-b-lockup.svg` (`viewBox 0 0 1100 128`), nombre en Sora 700 `#8B5CF6`. Lleva `<text>` con `font-family="Sora, sans-serif"` (reserva genérica), que la plantilla admite mientras `compose.fonts` garantice la fuente; el paso a trazos queda Opc. y `rsvg-convert` lo resuelve con la Sora de `piloto/fuentes/` | repo; paso a trazos Opc. (cambio aprobado) |
| Variante clara y oscura | Rec. | la baldosa lleva su propio fondo y vale sobre los dos; el nombre del lockup, `#8B5CF6` sobre oscuro y `#5B34C9` sobre claro (solo existe el archivo para oscuro) | **[P]** (`biblia.md` §4) |
| Tamaño mínimo y margen | Rec. | símbolo 16 px; lockup 24 px de alto y por debajo solo el símbolo; margen libre un cuarto del lado de la baldosa; nombre a la derecha a 28/128 de separación, nunca debajo | **[P]** (`biblia.md` §4) |
| Usos prohibidos | Opc. | cambiar el `rx` o el trazo, sacar el dibujo de la baldosa, rotar, recolorear, sombra o brillo | **[P]** (`biblia.md` §4) |
| Logo fuera de la paleta | Opc. | `#5B34C9` (final del degradado) no está en `brand.palette` de la configuración; sí en la tabla de la biblia | repo (diferencia entre `galivelop-images.json` y `biblia.md`) |

Copia en `examples/galivelop-image-generator/logos/`: **no hay** (F2.10, dec. 3, pendiente); `piezas.json` apunta hoy a
`docs/marcas/…/logos/`. En r4 el lockup de 1100×128 salía a ~24 px de alto y el nombre no se leía; desde entonces el piloto
lo pone al 9 % del alto de la pieza (`r4-composicion.md`).

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Familia de titular | Rec. (familia Galivelop) | Sora 700 (reserva `sans-serif`), tracking −0,03 em en el wordmark | heredado de Portal-Galivelop `aa76b34` (`Logo.tsx`); repo (`piezas.json` `fuente`, lockup `font-family="Sora, sans-serif"`) |
| Familia de texto | Rec. | Inter 400/500 (reserva `sans-serif`) | heredado de Portal-Galivelop `aa76b34`; repo (`piezas.json` `fuente_texto`) |
| Licencia y archivo | Rec. | Sora e Inter, OFL, del repo `google/fonts`; `examples/pilot/fuentes.sh` las baja a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`. No instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)* | repo (`examples/pilot/fuentes.sh`) |
| Tracking y mayúsculas | Opc. | títulos Sora −0,02 em; sin mayúsculas sostenidas; monoespaciada del sistema para claves y órdenes (`fauna/aullador-rojo`, `gimg order submit`) | heredado de Portal-Galivelop `aa76b34`; monoespaciada **[P]** (`biblia.md` §3) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | 1) fila de marcos finos de cristal flotando en azul noche, solapados y en profundidad, cada uno con un brillo difuso (la cola); 2) un marco más encendido que los demás, en violeta, que derrama luz sobre sus vecinos (la elegida); 3) rejilla tenue de puntos en el fondo (la web del Portal); 4) un punto de luz (el arranque bajo demanda), sin usar aún | repo (`prompts/estilo.txt`; `docs/plan.md` «Metáforas»; `biblia.md` §7) |
| Motivos No | Obl. | cámaras, pinceles, paletas, caballetes, chispas, robots, cerebros, personas, cuadros reconocibles, interfaz, texto | repo (`biblia.md` §7; `docs/plan.md`) |
| Palabras vetadas | Obl. | `camera`, `lens`, `brush`, `paint`, `palette`, `easel`, `canvas`, `sparkle`, `spark`, `magic`, `robot`, `brain`, `face`, `person`, `artist`, `gallery`, `text`, `letters`, `logo`; más `like` y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7). Ningún prompt de `prompts/*.txt` las contiene (grep del 2026-11-04) |
| Estilo de imagen | Rec. | «Style: minimal elegant digital art, smooth gradients, soft volumetric light, crisp glass reflections. Colours: deep midnight navy, violet, soft lavender and white highlights. Mood: calm, focused, quietly creative.» | repo (`prompts/estilo.txt`, elegido en r2) |
| Lenguaje de forma | Opc. | marcos, celdas, filas y puntos de luz; plano, sin perspectiva ni sombra dura; una sola cosa encendida; trazo 12/128 con remates redondos; radios `rx` 30/128 en la baldosa, 16/128 en el marco interior | repo (`biblia.md` §5; `logos/…-b.svg`) |

Prompts del proyecto (`examples/galivelop-image-generator/prompts/`): `estilo.txt` (= `og.txt` = `r2-palabras.txt`, aprobado
r1 en semillas 3 y 4, elegido r2), `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` (r5, compuestos y medidos),
`r2-luz.txt` (r2-luz, sin veredicto). Todos de 124-130 palabras: dentro del rango 120-320, en el suelo. Todos acaban en «The image is completely textless.» (el cierre de `r2-luz.txt` y su pedido se igualó el 2026-11-04).

## 7. Luz y atmósfera

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

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 → 1200×630 (`targetWidth`/`targetHeight` añadidos el 2026-11-04) y `social` 1280×640. Hechos en el piloto y sin perfil: `square` 1024×1024 → 1080×1080, `portrait` 896×1152 → 1080×1350, `header` 1536×512 → 1500×500 | repo (`galivelop-images.json`); los tres de r5 **[P]** (bitácora: «lo decide la persona» en F2.8) |
| Zona reservada | Obl. | `og`, `social`, `header`: `izquierda 1/2` («The left half … calm, smooth, dark navy surface, nearly empty and softly out of focus»); `square`, `portrait`: `arriba 1/2`. En píxeles, por la conversión de la plantilla (sección 9): `og` entregado 1200×630 → `0,0,600,630`. La caja del piloto es 55 % del ancho menos margen (izquierda) o 48 % del alto (arriba), margen 6 %: no coincide con 1/2 y se alinea al portar a `compose` | repo (`prompts/*.txt`; `examples/pilot/componer.py` `caja_zona`). La biblia dice «tercio superior **[P]**» para `square`: r5 hizo la mitad |
| Velo por perfil | Rec. | `og` `#06121c:0`; `square`, `portrait` y `header` `#06121c:0.3` | repo (`piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza, margen 6 % (desde r4, que lo tuvo a ~24 px y no se leía) *(suposición: la esquina; confirmar en `componer.py`)* | repo (`r4-composicion.md`; `examples/pilot/componer.py`) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 % del alto, título y subtítulo). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-image-generator-b.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay | repo (`piezas.json`); `icon` **[P]** |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia en r1-r5 sin boceto), sin LUT (las piezas salen dentro de rango; `compose.lut`, F2.11, no se necesita), sin conversión final | repo (`r1-fondos.md`, `r5-piezas.md`) |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos (51 s) y anticipa estilo y hueco. Propuesto `draft: {scale: 0.5, steps: 4}` en `og` | **[P]** (F2.10, dec. 7) |
| Prioridad | Rec. | 1) logo elegido y `avatar` 512; 2) `social` 1280×640; 3) `og` 1200×630. Hechas en el piloto, además, `square`, `portrait` y `header` (r5) | repo (`biblia.md` §9) |

## 10. Textos de composición

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

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona; delegado al agente desde el 2026-10-26. Apuntado en `docs/registros/contenido/r1-fondos.md` (sí, s3 y s4, «de las mejores»), `r2-estilo.md` (elegida «palabras»), `r4-composicion.md`, `r5-piezas.md` | repo |
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
- `docs/registros/contenido/calibracion-measure.md` (umbrales y medidas), `r1-fondos.md`, `r2-estilo.md`,
  `r4-composicion.md`, `r5-piezas.md` (veredictos y medidas).
- `examples/pilot/componer.py` (`caja_zona`, ajuste del texto), `examples/pilot/fuentes.sh` (origen y licencia de las fuentes).

**Portal-Galivelop** `aa76b34` (marca paraguas, «heredado de»), leído solo a través de `docs/marcas/portal/biblia.md` y
`docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`: `src/estilos/global.css` (fondos, texto, superficies, borde),
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

---

## Lo que enseñó rellenarla

Los 17 cambios propuestos a la plantilla se aplicaron el 2026-11-04 (aprobados por la persona); esta hoja ya sigue la nueva.

**Balance de este proyecto:** 15 obligatorios (familia Galivelop; fondo, texto y titular pasaron a Rec. y siguen completos,
heredados del Portal); 12 completos desde el repo, 3 **[P]** (acento, logo elegido como decisión delegada, titular), 0 «no hay». De los recomendados, 4 «no hay» o no comprobables (composición
por perfil, copia de logos, fuentes instaladas, imagen de marca propia).
