# Hoja de estilo mínima: galivelop-image-generator

Primer caso real de [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md) (F2.12), rellenada el 2026-11-04 para
este mismo repo. Complementa a [`biblia.md`](biblia.md): la biblia es la lectura larga; esta hoja es lo que `gimg` necesita,
campo a campo y en el orden de la plantilla. Estados como en [`../README.md`](../README.md): sin marca sale del repo (ruta en
la sección 13); **[P]** es propuesta pendiente de la persona; *(suposición)* se comprueba en una ronda; «no hay» no existe.

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

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos»; para los proyectos del taller (Tarkor/WMF el primero) y quien quiera generar en local sin instalar nada | repo (`README.md` l.5-7; `docs/plan.md` D1, D2, D6) |
| Lema | Rec. | «Pide, prueba, elige.» | **[P]** (`biblia.md` §1; no sale de ningún texto del repo) |
| Tono | Rec. | técnico, sobrio, honesto con el estado real («aún no genera imágenes reales» está en el README); nunca vende, nada de «magia» | repo (`README.md` «Estado»; `biblia.md` §6) |
| Idiomas | Rec. | `es` manda (las piezas de r4-r5 van en español); el repo publica también en `en` (`README.en.md`, textos es/en de F0), pero no hay pieza en inglés decidida | repo (`es`); `en` **[P]** |
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
| Fondo | Obl. | oscura (por defecto) `#06121c`; clara `#f6fafd` | heredado del Portal (`global.css` vía `portal/biblia.md` §2) |
| Texto | Obl. | `#eaf4fa` sobre oscuro (secundario `#9fb4c4`); `#0a1a28` sobre claro | heredado del Portal; `#eaf4fa` es el `color_texto` de las cuatro piezas de `piezas.json` |
| Acento | Obl. | `#8B5CF6` (uno por pieza); sobre fondo claro, `#5B34C9` | **[P]** (`docs/plan.md` «Estilos por proyecto»; `docs/marcas/README.md` «Acentos de las herramientas») |
| Resto de la paleta | Rec. | acento claro `#A78BFA` (halos, texto de acento sobre oscuro) **[P]**; acento oscuro `#5B34C9` (final del degradado de la baldosa) **[P]**; superficies `#0c1d2b`, `#11283a`; borde `#1b3447`; texto 2 `#9fb4c4`; blanco `#FFFFFF` (trazo del símbolo). `brand.palette` de hoy lleva solo 4: `#06121c`, `#A78BFA`, `#8B5CF6`, `#ffffff` | repo (`galivelop-images.json` `brand.palette`, de `prompts/r2-hex.txt`); el resto heredado del Portal |
| Combinaciones | Rec. | oscura: `#06121c` + texto `#eaf4fa` + velo `#06121c:0` en `og` (contraste sobra) y `#06121c:0.3` en `square`, `portrait` y `header`; clara: `#f6fafd` + `#0a1a28` + acento `#5B34C9`; sobre imagen: texto blanco en la zona reservada y el logo siempre en su baldosa | repo (`piezas.json`, `velo`); la clara **[P]** (`biblia.md` §2, sin pieza hecha) |
| Prohibidos | Rec. | el celeste del Portal `#1aa6df` como acento de la herramienta; violeta neón o magenta puro; negro `#000`; texto de acento sobre fondo de acento; más de un acento por pieza | **[P]** (`biblia.md` §2) |
| Degradados | Opc. | solo la baldosa del logo (`#8B5CF6 → #5B34C9`) | repo (`logos/galivelop-image-generator-b.svg`); regla de familia en `docs/marcas/README.md` |

**Medido:** la calibración da a este proyecto paleta ≥ 72 % (r1 y r5: 75-88 %; r4 og 72,36 %) con `brand.palette` de 4 hex y
ΔE76 < 15 (`docs/registros/contenido/calibracion-measure.md`). r2 confirmó que hex, palabras o materiales dan casi la misma
imagen (69,9 / 74,8 / 76,3 %); se eligió «palabras» (`r2-estilo.md`).

## 4. Logo

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Símbolo SVG | Obl. | `docs/marcas/galivelop-image-generator/logos/galivelop-image-generator-b.svg` («rejilla de intentos»: marco 2×2 con una celda encendida, en la baldosa de la familia). Cumple: `viewBox="0 0 128 128"`, `<title>`, sin `<text>`, sin raster, sin `filter`; colores `#8B5CF6`, `#5B34C9`, `#FFFFFF` | repo (archivo); la elección de **b** es delegada **[P]** (`docs/marcas/README.md`) |
| Lockup (símbolo + nombre) | Rec. | `logos/galivelop-image-generator-b-lockup.svg` (`viewBox 0 0 1100 128`), nombre en Sora 700 `#8B5CF6`. **Aún lleva `<text>`**: el paso a trazos «al elegirse» no está hecho; `rsvg-convert` lo resuelve con la Sora de `piloto/fuentes/` | repo; paso a trazos pendiente **[P]** |
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
| Familia de titular | Obl. | Sora 700 (reserva `sans-serif`), tracking −0,03 em en el wordmark | heredado del Portal (`Logo.tsx`); repo (`piezas.json` `fuente`, lockup `font-family="Sora, sans-serif"`) |
| Familia de texto | Rec. | Inter 400/500 (reserva `sans-serif`) | heredado del Portal; repo (`piezas.json` `fuente_texto`) |
| Licencia y archivo | Rec. | Sora e Inter, OFL, del repo `google/fonts`; `examples/pilot/fuentes.sh` las baja a `piloto/fuentes/` (fuera de git) y `componer.py` las suma por `FONTCONFIG_FILE`. No instaladas en `~/.local/share/fonts` *(suposición: `gimg doctor` lo dirá cuando haya `compose.fonts`)* | repo (`examples/pilot/fuentes.sh`) |
| Tracking y mayúsculas | Opc. | títulos Sora −0,02 em; sin mayúsculas sostenidas; monoespaciada del sistema para claves y órdenes (`fauna/aullador-rojo`, `gimg order submit`) | heredado del Portal; monoespaciada **[P]** (`biblia.md` §3) |

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivos Sí | Obl. | 1) fila de marcos finos de cristal flotando en azul noche, solapados y en profundidad, cada uno con un brillo difuso (la cola); 2) un marco más encendido que los demás, en violeta, que derrama luz sobre sus vecinos (la elegida); 3) rejilla tenue de puntos en el fondo (la web del Portal); 4) un punto de luz (el arranque bajo demanda), sin usar aún | repo (`prompts/estilo.txt`; `docs/plan.md` «Metáforas»; `biblia.md` §7) |
| Motivos No | Obl. | cámaras, pinceles, paletas, caballetes, chispas, robots, cerebros, personas, cuadros reconocibles, interfaz, texto | repo (`biblia.md` §7; `docs/plan.md`) |
| Palabras vetadas | Obl. | `camera`, `lens`, `brush`, `paint`, `palette`, `easel`, `canvas`, `sparkle`, `spark`, `magic`, `robot`, `brain`, `face`, `person`, `artist`, `gallery`, `text`, `letters`, `logo`; más `like` y cualquier lugar real (reglas comunes) | repo (`biblia.md` §7). Ningún prompt de `prompts/*.txt` las contiene (grep del 2026-11-04) |
| Estilo de imagen | Rec. | «Style: minimal elegant digital art, smooth gradients, soft volumetric light, crisp glass reflections. Colours: deep midnight navy, violet, soft lavender and white highlights. Mood: calm, focused, quietly creative.» | repo (`prompts/estilo.txt`, elegido en r2) |
| Lo ya publicado | Rec. | en este repo, nada (no tiene web ni og:image). La calibración midió una `portada.webp` de este proyecto en el Portal (YAVG 41, SATAVG 13, paleta 77 %), pero el plan dice que las herramientas «no están en el Portal» | *(suposición: existe `Portal-Galivelop/public/proyectos/<?>/portada.webp`; confirmar ruta y si es marca)* |
| Lenguaje de forma | Opc. | marcos, celdas, filas y puntos de luz; plano, sin perspectiva ni sombra dura; una sola cosa encendida; trazo 12/128 con remates redondos; radios `rx` 30/128 en la baldosa, 16/128 en el marco interior | repo (`biblia.md` §5; `logos/…-b.svg`) |

Prompts del proyecto (`examples/galivelop-image-generator/prompts/`): `estilo.txt` (= `og.txt` = `r2-palabras.txt`, aprobado
r1 en semillas 3 y 4, elegido r2), `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt` (r5, compuestos y medidos),
`r2-luz.txt` (r2-luz, sin veredicto). Todos de 124-130 palabras: dentro del rango 120-320, en el suelo.

## 7. Luz y atmósfera

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Dirección de la luz | Rec. | la luz sale de los propios marcos (no hay fuente externa); en `r2-luz.txt`: «the only light comes from the right» y el marco encendido «a quarter of the way in from the right edge» | repo (`prompts/estilo.txt`); la variante *(suposición: r2-luz sin veredicto)* |
| Momento y clima | Rec. | escena oscura, dicha al principio: «Dark wide abstract banner: the whole frame is deep midnight navy…» (r2-luz); en `estilo.txt` el fondo oscuro va en la primera frase | repo (`orders/r2-luz.json`) *(suposición)* |
| Luminosidad objetivo (YAVG) | Rec. | 33-52 (r1 y r5: 33-50; r4 og: 47,9; r2 palabras: 41,7) | repo (`calibracion-measure.md`, umbrales orientativos) |
| Saturación objetivo (SATAVG) | Rec. | 10-16 (r4 og: 15,17; r2 palabras: 15,3) | repo (`calibracion-measure.md`) |
| Gradación | Opc. | no hay: las piezas salen dentro de rango sin LUT; `compose.lut` (F2.11) no se necesita para este proyecto | — |

## 8. Referencias de marca

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Imágenes de marca | Rec. | en este repo, **no hay** (sin web, sin imagen publicada). La calibración usó una `portada.webp` del Portal como marca de este proyecto (EMD de r1 y r5: Y 8-11, Cb 1,2-3,3, Cr 2,5-4,2) | *(suposición: ruta y validez de esa portada; la persona dice si vale como marca, «Portadas que no son marca» de `calibracion-measure.md`)* |
| Referencias de sujeto | Opc. | no hay (el motivo es abstracto; nada que conservar) | — |
| Imagen inicial | Opc. | no hay: la zona reservada salió limpia en r1-r5 sin boceto | repo (`r1-fondos.md`, `r5-piezas.md`) |

## 9. Formatos y piezas

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 y `social` 1280×640, **sin `targetWidth`/`targetHeight`** (el piloto recorta el og a 1200×630 fuera de `gimg`). Hechos en el piloto y sin perfil: `square` 1024×1024 → 1080×1080, `portrait` 896×1152 → 1080×1350, `header` 1536×512 → 1500×500 | repo (`galivelop-images.json`); los tres de r5 **[P]** (bitácora: «lo decide la persona» en F2.8) |
| Zona reservada | Obl. | `og`, `social`, `header`: mitad izquierda («The left half … calm, smooth, dark navy surface, nearly empty and softly out of focus»); `square`, `portrait`: mitad superior. La caja del piloto: 55 % del ancho menos margen (izquierda) o 48 % del alto (arriba), margen 6 % | repo (`prompts/*.txt`; `examples/pilot/componer.py` `caja_zona`). La biblia dice «tercio superior **[P]**» para `square`: r5 hizo la mitad |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 % del alto, título y subtítulo). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-image-generator-b.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay | repo (`piezas.json`); `icon` **[P]** |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos (51 s) y anticipa estilo y hueco. Propuesto `draft: {scale: 0.5, steps: 4}` en `og` | **[P]** (F2.10, dec. 7) |
| Prioridad | Rec. | 1) logo elegido y `avatar` 512; 2) `social` 1280×640; 3) `og` 1200×630. Hechas en el piloto, además, `square`, `portrait` y `header` (r5) | repo (`biblia.md` §9) |

## 10. Textos de composición

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titular de la primera pieza | Obl. | «Pide, prueba, elige.» (20 caracteres), en `og` | **[P]** (`piezas.json`, r4; el lema es propuesta) |
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
| % de paleta mínimo | Rec. | ≥ 72 | repo (`calibracion-measure.md`) |
| YAVG y SATAVG | Rec. | 33-52 / 10-16 | repo (`calibracion-measure.md`) |
| EMD frente a la marca | Opc. | Cb ≤ 4 / Cr ≤ 5 (medido frente a la portada del Portal: Cb 1,2-3,3, Cr 2,5-4,2) | repo (`calibracion-measure.md`) *(suposición: la referencia, sección 8)* |
| Cuándo se da por bueno el estilo | Opc. | ya cumplido para `og`: «sí» en r1 a la primera y estilo elegido en r2; r5 dio las tres piezas de formato a la primera. Pendiente solo el veredicto de la persona sobre lo delegado | repo (registros r1-r5) |

## 13. Fuentes de verdad

Este repo, `f2-motor` `2259370`:

- `README.md` l.5-7, «Estado» (propósito, honestidad con el estado); `README.en.md` (idioma `en`).
- `GLOSSARY.md`, «Términos del proyecto» (campo semántico).
- `examples/galivelop-image-generator/galivelop-images.json` (`name`, `brand.palette` de 4 hex, `delivery`, perfiles `og` y
  `social`; último cambio `b65bd81`).
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

Portal-Galivelop `aa76b34`, leído solo a través de `docs/marcas/portal/biblia.md` y
`docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`: `src/estilos/global.css` (fondos, texto, superficies, borde),
`src/componentes/Logo.tsx` (Sora 700, −0,03 em), `public/marca/gv-logo.svg` (baldosa `rx` 30, trazo 12).

Sin línea aquí y por tanto **[P]** o *(suposición)*: acento y sus dos tonos, lema y frases, logo elegido, reglas del logo
tras elegir, monoespaciada, perfiles `square`/`portrait`/`header`, `draft`, `compose`, la portada del Portal como marca.

---

## 14. Lista de comprobación de lo obligatorio (este proyecto)

| # | Comprobación | Resultado hoy |
|---|---|---|
| 1 | `name` válido | pasa (esquema) |
| 2 | Propósito en una frase | pasa (criterio) |
| 3 | «Nunca se muestra» no vacío | pasa; nadie lo valida por script |
| 4 | `brand.palette` ≥ 3 hex ≤ 16; fondo, texto y acento nombrados | hex pasa (4); **el color del texto `#eaf4fa` no está en `brand.palette`** y el acento oscuro `#5B34C9` del logo tampoco: la hoja nombra los roles, la configuración no los lleva |
| 5 | Símbolo SVG válido | pasa a mano (viewBox, sin `<text>`/`<image>`/`filter`, legible a 16 px según la elección); copia en `examples/<p>/logos/` **no hay** |
| 6 | Familia de titular instalada | **no comprobable**: la configuración no tiene `compose.fonts`, y las fuentes viven en `piloto/fuentes/`, no en `~/.local/share/fonts` |
| 7 | Motivos Sí, No y palabras vetadas no vacíos | pasa; nadie lo valida |
| 8 | Ningún prompt con palabra vetada, negación ni «like» | `estilo.txt` y `r5-*.txt` pasan; **`r2-luz.txt` contiene `no` dos veces** («no letters, no logos»), que es el cierre que la propia plantilla de prompt manda (sección 6 de la plantilla) |
| 9 | Prompt acaba en «The image is completely textless» y tiene 120-320 palabras | pasa (124-130 palabras); `r2-luz.txt` acaba en «…textless, no letters, no logos.» |
| 10 | ≥ 1 perfil con múltiplos de 64; `targetWidth`/`targetHeight` cuando el destino difiere | múltiplos pasan; **`og` genera 1280×640 para un destino de 1200×630 sin `targetWidth`/`targetHeight`** |
| 11 | Cada perfil compuesto declara su zona y el prompt la describe | el prompt la describe; ningún perfil la declara (hueco) |
| 12 | Titular ≤ 200, cabe en la columna | pasa (20 caracteres; r4 compuesto) |
| 13 | `delivery.dir` relativa | pasa (esquema) |
| 14 | «Quién decide» rellenado | pasa; nadie lo valida |

## 15. Huecos que tocan a este proyecto

De los once de la plantilla, le afectan: roles de la paleta (el texto no está en `brand.palette`), zona reservada (solo en
prompt y en `componer.py`), palabras vetadas sin campo, `avatar` sin perfil (lo hace `piezas.py`), tipografía sin licencia
ni ruta declaradas (las baja `fuentes.sh`), imágenes de marca para la EMD sin lista (la calibración usó una del Portal), copia
de los logos en `examples/<p>/logos/` pendiente. No le afectan: varias variantes de logo (la baldosa vale sobre claro y
oscuro), `compose.lut` (no hace falta), `style.lora`, idiomas (solo `es`).

---

## Lo que enseñó rellenarla

Hallazgos del primer caso real, sobre la plantilla (no se modifica aquí; son propuestas).

**Campos ambiguos:**

1. **«Estado» no tiene columna.** La plantilla pide «cada campo con su valor y su estado», pero sus tablas son Campo / Nivel /
   Qué es / Ejemplo / Dónde acaba: al rellenar hay que inventar la columna. Propuesta: la hoja rellena usa Campo / Nivel /
   Valor / Estado (fuente), y la plantilla dice que las columnas «Qué es», «Ejemplo» y «Dónde acaba» se quitan al rellenar.
2. **«Heredado» no es un estado.** Casi todo lo obligatorio de este proyecto (fondo, texto, tipografía, baldosa) sale del
   repo del Portal, no del suyo, y la regla «cada dato que sale de él se cita con ruta y commit» no dice cómo se cita un dato
   de otro repo leído a través de una biblia. Propuesta: cuarto estado «heredado de `<marca>`» con el commit de la marca
   paraguas en la ficha, y en la sección 13 un bloque por repo.
3. **«Lo ya publicado» e «Imágenes de marca» se solapan** y aquí dieron la misma respuesta (una portada del Portal que el
   plan dice que no existe). Propuesta: fundirlos en «Imágenes de marca» con dos columnas (publicada dónde / vale como
   referencia sí-no-**[P]**), o que «Lo ya publicado» pase a Opc.
4. **La zona reservada en fracciones no casa con la caja del piloto.** El prompt dice «mitad izquierda»; `caja_zona` usa el
   55 % menos margen; `measure --zone` pide píxeles. Propuesta: la plantilla fija una sola forma de decirla (fracción y
   borde) y dice cómo se convierte a píxeles por tamaño de perfil, para que el campo sea el mismo en prompt, plantilla SVG y
   medida.
5. **Contradicción interna:** la comprobación 8 prohíbe `no` en los prompts y la plantilla de prompt de la sección 6 acaba
   en «no letters, no logos». Aquí ya pilla a `r2-luz.txt`. Propuesta: o el cierre pasa a «The image is completely textless.»
   a secas (lo que usan los prompts aprobados), o la comprobación 8 exime ese cierre literal.
6. **Las cifras de medida se piden dos veces** (YAVG/SATAVG en la sección 7 y en la 12; % de paleta en la 3 y la 12).
   Propuesta: la sección 12 solo referencia («los de la sección 7») o se mueven todas a 12.

**Campos que sobran o cuyo nivel no se sostiene para una herramienta de la familia:**

7. **Idiomas (Rec.)**: en una CLI sin web la única respuesta es `es`; cuesta más decidir si `en` cuenta que el valor que
   da. Propuesta: Opc., con «`es` salvo que el repo publique piezas en otro».
8. **Familia de titular (Obl.)**: para la familia Galivelop la respuesta es siempre Sora 700, y la propia plantilla ya lo da
   por defecto. Propuesta: Obl. solo fuera de la familia; dentro, Rec. con el valor por defecto escrito.
9. **Fondo y Texto (Obl.)**: igual que la tipografía, los hereda la familia. Propuesta: la plantilla admite «familia
   Galivelop» como valor que rellena fondo, texto, tipografía y baldosa de una vez (la hoja de una herramienta se reduce al
   acento, los motivos, las palabras vetadas, los perfiles y los textos).
10. **Referencias de sujeto, Imagen inicial, Gradación, Conversión final (Opc.)**: cuatro «no hay» seguidos. No sobran, pero
    cuestan una fila cada uno. Propuesta: una sola fila «Palancas extra» (referencias, boceto, LUT, conversión) con «no hay»
    por defecto.
11. **Lockup (Rec.)** exige «nombre en trazos (no `<text>`)», pero ningún lockup elegido lo cumple aún y el piloto los renderiza
    bien con `<text>` y la fuente cargada. Propuesta: aceptar `<text>` con `font-family` y reserva mientras `compose.fonts` la
    garantice, y dejar los trazos como Opc. para cuando la pieza salga del taller.

**Campos que faltan:**

12. **Velo por combinación como dato del perfil**: la plantilla lo mete en «Combinaciones» (sección 3) como ejemplo, pero es
    lo que más cambió entre r4 y r5 (`0` en og, `0.3` en el resto) y no tiene fila propia ni sitio en `compose`. Propuesta:
    fila «Velo por perfil» en la sección 9 y hueco en la 15.
13. **Posición y tamaño del logo en la pieza**: el fallo visible de r4 (lockup a 24 px, ilegible) no cabe en ningún campo;
    «Tamaño mínimo» habla del logo suelto, no del logo en la composición. Propuesta: fila «Logo en la pieza» (esquina,
    % del alto, separación del texto) en la sección 9 o 10.
14. **Diferencias entre configuración y hoja**: aquí salieron tres (texto fuera de `brand.palette`, `#5B34C9` fuera,
    perfiles de r5 sin declarar, `og` sin `targetWidth`) y no hay dónde apuntarlas salvo la sección 14. Propuesta: la sección
    13 gana una lista «Lo que la configuración no refleja aún», que es la entrada de `docs/propuestas/<proyecto>.md`.
15. **Qué es «primera pieza»**: la sección 10 pide el titular «de la primera pieza» y la 9 la «prioridad»; aquí la primera
    de la prioridad es el avatar, que no lleva texto. Propuesta: «Titular del primer perfil compuesto».

**Sobre la lista de comprobación:**

16. Cuatro de las ocho que hoy pasan solo las ve alguien leyendo (3, 7, 11, 14) y ninguna de las comprobaciones mira la
    coherencia hoja ↔ configuración (texto en la paleta, destino ≠ generación sin `target*`). Propuesta: añadir 15 «todo
    hex nombrado en Fondo/Texto/Acento está en `brand.palette`» y 16 «si la hoja da un destino distinto del tamaño de
    generación, el perfil lleva `targetWidth`/`targetHeight`», las dos de máquina.
17. La bitácora cuenta «12 campos obligatorios» y la plantilla tiene 18 filas Obl. (3 en la ficha, 1 identidad, 1 ética, 3
    paleta, 1 logo, 1 tipografía, 3 escenas, 2 formatos, 1 textos, 1 entrega, 1 aceptación). Conviene que la plantilla diga
    la cifra y que el validador la cuente.

**Balance de este proyecto:** 18 obligatorios; 15 completos desde el repo (3 de ellos heredados del Portal: fondo, texto y tipografía), 3 **[P]** (acento,
logo elegido como decisión delegada, titular), 0 «no hay». De los recomendados, 4 «no hay» o no comprobables (composición
por perfil, copia de logos, fuentes instaladas, imagen de marca propia).
