# Hoja de estilo: Galivelop IG

**r9 (2026-11-11), aprobada por la persona el 2026-11-11** (decisiones en «Contradicciones»). Rehace la hoja del
2026-11-04 (identidad oscura con violeta, en «Historia») como **variante de la identidad nueva del Portal**
(Portal-Galivelop `08c7fe5`, `docs/marca.md`): comparte con ella papel, tinta, tipografías y lenguaje de línea, y conserva
lo propio (el violeta, la rejilla de intentos, los marcos). Interfaz, logos y nombre (D38) están **aplicados
el 2026-11-11** en la rama `claude/marca-r9` (`de53727`, `1b211f6`, `e4b5db0`), fusionada en `main` por el PR #6
(`2509674`). Lo que sigue marcado **[P]** no está aplicado. Las piezas `og`/`social`,
`og.txt` y `brand.palette` **no cambian** hasta medir una ronda plana.

> **Para imagen generada nueva manda además la identidad vigente del Portal (2026-11-11).** r9 leyó el Portal en
> `08c7fe5`; después, el bloque «Identidad vigente» de [`../portal/hoja.md`](../portal/hoja.md) fijó lo que enseñó generar
> con gimg: Z-Image-Turbo q6 a 8 pasos (FLUX solo bocetos), «el mar pone el dónde, la tecnología pone el qué», dos
> registros de dibujo (grabado y línea simple), zonas limpias, croma para recortar, versión oscura y «Cómo se escribe el
> prompt» (negaciones solo en el cierre, `like` como comparación de estilo, ningún color fuera de tinta). Esta hoja añade
> lo propio: la fila «Motivo propio» de la sección 6 y el violeta para logo e interfaz (en imagen generada, ver la duda 2
> del Portal). La interfaz y los logos de r9 ya casan con esa identidad (papel, tinta, oscuro y tipografías).

Sigue [`../plantilla-hoja-de-estilo.md`](../plantilla-hoja-de-estilo.md) (F2.12) y complementa a [`biblia.md`](biblia.md).
Estados como en [`../README.md`](../README.md): sin marca sale del repo (ruta en la sección 13); **heredado de
`<marca>`** sale del repo de la marca paraguas; **[P]** es propuesta pendiente de la persona; *(suposición)* se comprueba
en una ronda; «no hay» no existe. Las contradicciones se resuelven con
[`../../records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md).

Commits de referencia: este repo `a4e394d` (rama `ccr-85e9d14e-zt7p8b`); Portal-Galivelop `08c7fe5`, leído solo a través
de `examples/portal/` de la rama `portal-marca` (su `README.md`, `galivelop-images.json` y `prompts/estilo.txt`); desde
aquí no se abre ese repo. Contrastes: WCAG 2.x, calculados el 2026-11-11.

**Idea de marca.** El Portal es una carta náutica: el mapa de todo el taller. Galivelop IG es **la hoja de contactos
sobre ese mismo papel**: una rejilla de intentos dibujada con la misma tinta y la misma línea, con un solo intento
marcado en violeta. El violeta no decora: señala **lo elegido** («Pide, prueba, elige.»). Todo lo demás es del Portal.

| Se comparte con el Portal | Es propio de Galivelop IG |
|---|---|
| Papel `#fbfcfd`, tinta `#13212b`, superficie `#e6eef3`, fondo oscuro `#0d171e` | Acento violeta: `#5B34C9` (claro), `#A78BFA` (oscuro), `#8B5CF6` (marca) |
| Big Shoulders Display, Literata, JetBrains Mono | Símbolo «rejilla de intentos», siglas «GVIG» |
| Línea fina de grosor uniforme, plano, sin degradados ni brillo | Motivos: marcos, cola, el intento elegido |
| Chaflán 28/128 y trazo 12/128 del logo | Lema «Pide, prueba, elige.» y campo semántico del pedido |
| Verde alga `#5d7a6a` como toque de ilustración | Colores de estado de la interfaz |

---

## 0. Ficha

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nombre de marca | Obl. | «Galivelop IG» (siglas «GVIG»): en interfaz, README, hoja, textos y piezas. El repo, el paquete y la orden `gimg` no cambian | repo (`docs/plan.md` D38, decisión de la persona del 2026-11-04) |
| Nombre en código | Obl. | `galivelop-image-generator` | repo (`examples/galivelop-image-generator/galivelop-images.json`, `name`) |
| Fuente de verdad | Rec. | Este repo `a4e394d`; Portal `08c7fe5` para lo compartido. Rutas por campo en la sección 13 | repo |
| Quién decide | Obl. | La persona. Esta r9 la pidió ella el 2026-11-11 («una variante que comparte estilos con el portal»); el detalle es del agente y va **[P]** | repo (`docs/handoff.md`) |
| Fecha de la hoja | Rec. | `2026-11-11` (r9); anterior `2026-11-04` | — |
| Familia visual | Rec. | `Galivelop`, identidad nueva del Portal (carta náutica): papel, tinta, tipografías y línea son de la familia | heredado de Portal-Galivelop `08c7fe5` **[P]** |
| Hereda de | Opc. | Portal-Galivelop `08c7fe5` (`docs/marca.md`), leído a través de `examples/portal/` de `portal-marca` | repo |

## 1. Identidad

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Propósito | Obl. | «Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos»; para los proyectos del taller (Tarkor/WMF el primero) y quien quiera generar en local sin instalar nada | repo (`README.md` l.5-7; `docs/plan.md` D1, D2, D6) |
| Idea de marca | Rec. | la hoja de contactos sobre el papel de la carta: muchos intentos en tinta, uno marcado en violeta | **[P]** (r9) |
| Lema | Rec. | «Pide, prueba, elige.» | **[P]** (`biblia.md` §1) |
| Tono | Rec. | técnico, sobrio, honesto con el estado real; nunca vende, nada de «magia». Como el Portal: frases cortas, datos antes que adjetivos | repo (`README.md` «Estado»; `biblia.md` §6) |
| Idiomas | Opc. | `es` manda; el repo publica también en `en` (`README.en.md`, `docs/en/`), sin pieza en inglés decidida | repo (`es`); `en` **[P]** |
| Campo semántico | Opc. | dentro: pedido, intento, candidata, descartada, elegida, cola, entrega, manifiesto, perfil, motor, referencia, hoja de contactos; fuera: render, job, cliente, prompt engineering, «magia» | repo (`GLOSSARY.md`) |

## 2. Ética en imagen

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Nunca se muestra | Obl. | cámaras, pinceles, paletas, chispas o «magia» de IA, robots, cerebros, rostros, personas o artistas sustituidos, obras reconocibles, texto generado por el modelo | repo (`docs/plan.md` «Estilos por proyecto»; `biblia.md` §1 y §7) |
| Personas y rostros | Rec. | nunca personas ni rostros (vetados `face`, `person`, `artist`) | repo (`biblia.md` §7) |
| Promesas | Rec. | nada de «arte ilimitado»; no afirmar en una pieza lo que el README no diga ya; nada de precios ni fechas | repo (`biblia.md` §1; `README.md` «Estado») |
| Texto en imagen | Rec. | ninguna imagen generada lleva texto; el texto lo pone `compose` | heredado de Portal-Galivelop `08c7fe5` (`examples/portal/README.md`); repo (cierre «completely textless» de los prompts) |

## 3. Paleta

Proporción: **70 % papel, 20 % tinta, hasta 10 % violeta** (60/30/10 con el acento más escaso: el violeta señala una sola
cosa por pantalla o pieza). El modo por defecto es el **claro**, como el Portal.

| Rol | Token | Hex claro | Hex oscuro | Uso | Contraste | Origen |
|---|---|---|---|---|---|---|
| Fondo | `--bg` | `#fbfcfd` | `#0d171e` | papel de la carta; fondo de pantalla y de pieza | — | Portal |
| Superficie | `--surface` | `#e6eef3` | `#13212b` | tarjetas, cabeceras, celdas de la rejilla | — | Portal |
| Texto | `--text` | `#13212b` | `#e6eef3` | tinta: texto, líneas de ilustración, trazo del símbolo de línea | 15,97 / 15,44 (13,97 sobre superficie) | Portal |
| Texto secundario | `--text-2` | `#4a5b66` | `#9fb4c4` | ayudas, rótulos, metadatos | 6,86 / 8,46 (6,00 / 7,66 sobre superficie) | propio (`tokens.css`) |
| Borde de control | `--border` | `#6f8493` | `#6f8493` | bordes de campos y botones, foco inactivo (≥ 3:1) | 3,79 / 4,66 (3,31 sobre superficie clara) | propio (`tokens.css`) |
| Línea suave | `--rule` | `#c9d5dd` | `#2b3d4a` | separadores y rejilla de fondo; decorativa, sin requisito de contraste | 1,46 / 1,61 | propio (`tokens.css`) |
| **Acento** | `--accent` | `#5B34C9` | `#A78BFA` | **lo elegido**: enlace, botón primario, foco, celda marcada. Texto blanco sobre `#5B34C9`: 7,56 | 7,36 / 6,66 (6,44 / 6,03 sobre superficie) | propio |
| Violeta de marca | `--brand` | `#8B5CF6` | `#8B5CF6` | celda encendida del símbolo, rellenos y titulares grandes. **Nunca texto de cuerpo** | 4,12 / 4,28 (no llega a AA) | propio |
| Enlace de familia | `--family` | `#0072a8` | `#1aa6df` | solo para nombrar o enlazar al Portal (marca de familia, pie); ≤ 2 % | 5,15 / 6,53 | Portal (`tokens.css`) |
| Toque de ilustración | — | `#5d7a6a` | `#5d7a6a` | verde alga: un detalle por ilustración, nunca en interfaz | 4,59 sobre papel | Portal |
| Estado: bien | `--ok` | `#1b7a3e` | `#5ad38a` | solo interfaz, nunca en piezas | 5,24 / 9,60 | propio (`tokens.css`) |
| Estado: aviso | `--warn` | `#8a5a00` | `#f2c14e` | solo interfaz | 5,77 / 10,80 | propio (`tokens.css`) |
| Estado: error | `--err` | `#b3261e` | `#ff7b6b` | solo interfaz | 6,36 / 7,16 | propio (`tokens.css`) |

Contraste: sobre `--bg` de su modo (claro / oscuro). Texto ≥ 4,5:1; bordes y foco ≥ 3:1.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Fondo | Rec. (familia Galivelop) | claro (por defecto) `#fbfcfd`; oscuro `#0d171e` | heredado de Portal-Galivelop `08c7fe5`; aplicado en la interfaz (`gimg/ui/css/tokens.css`), **[P]** en las piezas. Piezas hoy, compuesto y medido: `#06121c` / `#f6fafd` |
| Texto | Rec. (familia Galivelop) | `#13212b` sobre claro; `#e6eef3` sobre oscuro | heredado de Portal-Galivelop `08c7fe5`; aplicado en la interfaz, **[P]** en las piezas. Piezas hoy: `#eaf4fa` (`color_texto` de `piezas.json`) |
| Acento | Obl. | violeta, uno por pieza: `#5B34C9` sobre claro, `#A78BFA` sobre oscuro; `#8B5CF6` solo como relleno o marca | repo (`docs/plan.md` «Estilos por proyecto»; `tokens.css`, que ya reparte el acento por modo) |
| Resto de la paleta | Rec. | la tabla de roles. `brand.palette` propuesto (6, como el del Portal): `#fbfcfd`, `#13212b`, `#e6eef3`, `#5B34C9`, `#8B5CF6`, `#A78BFA`. El de hoy lleva 5: `#06121c`, `#A78BFA`, `#8B5CF6`, `#ffffff`, `#eaf4fa` | **[P]**; el de hoy, repo (`galivelop-images.json`) |
| Combinaciones | Rec. | clara: papel + tinta + un `#5B34C9`; oscura: `#0d171e` + `#e6eef3` + un `#A78BFA`; sobre imagen: texto en tinta sobre la zona de papel, sin velo (la imagen plana ya deja papel libre); logo de línea directo sobre el papel | **[P]**. Hoy: velo `#06121c:0`-`0.3` y logo en baldosa (`piezas.json`) |
| Prohibidos | Rec. | el azul del Portal como acento (solo como enlace de familia); violeta neón o magenta; negro `#000` y blanco `#fff` puros como fondo; `#8B5CF6` en texto de cuerpo; más de un acento por pieza; violeta en más del 10 % | aplicado en interfaz y logos; **[P]** en las piezas (levanta en parte el veto del 2026-11-04 a `#1aa6df`) |
| Degradados | Opc. | ninguno: ni en el logo ni en la interfaz ni en las ilustraciones | heredado de Portal-Galivelop `08c7fe5` («no gradients, no glow»); aplicado en logo e interfaz. Las ilustraciones planas, **[P]** (sin ronda) |

**Medido (identidad anterior):** paleta ≥ 72 % (r1 y r5: 75-88 %; r4 og 72,36 %) con `brand.palette` de 4 hex y ΔE76 < 15
(`docs/records/contenido/calibracion-measure.md`). Con la paleta nueva no hay nada medido: la primera ronda plana lo dirá
*(suposición: el estilo plano sube el % de paleta, como en el Portal)*.

## 4. Logo

**Sistema de logo.** Una idea, seis piezas. El redibujo r9 de la última columna está hecho (2026-11-11, `1b211f6`) salvo el
monograma, que sigue **[P]**. Los dibujos anteriores (baldosa con degradado violeta, `rx` 30/128, nombre en Sora) quedan en
el historial de git.

| Pieza | Archivo | Qué es | Mínimo | Redibujo r9 |
|---|---|---|---|---|
| Símbolo (baldosa) | `logos/galivelop-image-generator-b.svg` | rejilla 2×2 de marcos con una celda encendida, sobre baldosa | 16 px | baldosa plana `#5B34C9`, chaflán 28/128 (como el Portal), líneas `#fbfcfd` de 12/128, celda elegida rellena `#fbfcfd`; sin degradado |
| Símbolo de línea | `logos/galivelop-image-generator-b-linea.svg`, `-b-linea-oscuro.svg` | la misma rejilla sin baldosa, para papel | 24 px | líneas `#13212b` (o `#e6eef3` sobre oscuro) de 12/128 y la celda elegida rellena `#8B5CF6`; es la pieza que más se parece al Portal |
| Favicon | `gimg/ui/assets/gvig.svg` | el símbolo, para la pestaña | 16 px | el símbolo de baldosa (misma figura que `logos/…-b.svg`); a 16 px la celda elegida ocupa 4 px como mínimo |
| Monograma | no hay | «IG» | 12 px de alto | **Decidido por la persona (2026-11-12): «IG» en una tinta (`#fbfcfd`) sobre el cuadrado con chaflán en el hondo `#5B34C9`, que pasa a ser el símbolo del producto** (sustituye a la rejilla; la rejilla y los dibujos con degradado, `rx` 30 o Sora son históricos). **Dependencia:** orden nueva en `gimg brand` que monte el cuadrado con chaflán. Sin dibujar |
| Nombre | dentro del lockup | «Galivelop IG» | 14 px de alto | Big Shoulders Display 700, tinta `#13212b`; «IG» en `#5B34C9` (en oscuro, `#e6eef3` y `#A78BFA`) |
| Lockup | `logos/galivelop-image-generator-b-lockup.svg`, `-b-lockup-oscuro.svg`, `gimg/ui/assets/gvig-lockup.svg` | símbolo + nombre a la derecha | 24 px de alto | símbolo de baldosa + nombre; separación 28/128 del lado de la baldosa. El nombre va aún como `<text>` vivo: falta pasarlo a trazados |

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Archivos | Obl. | los de la tabla; los candidatos `-a`, `-c` y `-d` se quedan como historia. `viewBox 0 0 128 128` (símbolo) y `0 0 1100 128` (lockup), con `<title>`; el símbolo no lleva `<text>` | repo (`docs/marcas/galivelop-image-generator/logos/`) |
| Colores del logo | Obl. | `#5B34C9`, `#fbfcfd`, `#8B5CF6`, `#13212b` (en oscuro, `#e6eef3` y `#A78BFA`), planos | repo |
| Variantes | Rec. | baldosa (vale sobre claro y oscuro) y línea (una versión por fondo) | repo |
| Tamaño mínimo | Obl. | símbolo 16 px, lockup 24 px de alto | repo |
| Margen | Obl. | un cuarto del lado de la baldosa por cada lado | repo |
| Posición en la pieza | Rec. | lockup al 9 % de la altura de la pieza | repo (`examples/pilot/componer.py`) |
| Usos prohibidos | Obl. | deformar, girar, cambiar el violeta por el azul del Portal, encender más de una celda, sombra o brillo, ponerlo sobre una zona con detalle sin velo; con r9, además, degradado en la baldosa | repo |
| Copia para `compose` | Rec. | `examples/galivelop-image-generator/logos/galivelop-image-generator-b-lockup.svg`: copia congelada del lockup **anterior**, la que usan `og`/`social` (`piezas.json`); se cambia por el redibujo al volver a medir las piezas | repo |

**Por qué una sola celda.** El símbolo dice lo que hace la herramienta: muchos intentos, uno elegido. Dos celdas
encendidas ya no dicen eso; por eso es un uso prohibido y no una variante.

## 5. Tipografía

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Titulares | Rec. | **Big Shoulders Display** 700 (800 en el monograma), mayúsculas o caja normal, tracking 0 | **heredado de Portal-Galivelop** `08c7fe5`; aplicado en la interfaz (`gimg/ui/fonts/`); pesos *(suposición)* |
| Texto | Rec. | **Literata** 400 (500 para énfasis) | **heredado de Portal-Galivelop**; aplicado en la interfaz |
| Datos | Rec. | **JetBrains Mono** 400: semillas, hex, rutas, órdenes, medidas | **heredado de Portal-Galivelop**; aplicado en la interfaz |
| Piezas, hoy | — | Sora 700 (tracking −0,03 em en el nombre, −0,02 en títulos) e Inter 400/500: solo en la composición de piezas, ya no en la interfaz | repo (`examples/pilot/componer.py`, `piezas.json`) |
| Licencia y origen | Rec. | las cinco son OFL, de `google/fonts`; `examples/pilot/fuentes.sh` baja hoy Sora e Inter a `piloto/fuentes/` y `componer.py` las usa con `FONTCONFIG_FILE` | repo; las tres nuevas *(suposición: la ruta en `google/fonts` se comprueba al bajarlas)* |

**Regla de uso.** Lo que la herramienta **dice** va en Literata; lo que **mide** va en JetBrains Mono; lo que **nombra**
(títulos, botones principales) va en Big Shoulders Display. Una semilla o un hex nunca en Literata.

## 6. Escenas y motivos

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Motivo propio (identidad vigente, 2026-11-11) | Obl. | **La cola y la elegida, en informática:** una ventana de aplicación con una fila de miniaturas (celdas de una retícula), una de ellas marcada con un visto; variantes: la ventana sobre el mar de carta (grabado, portadas) o sola (icono, línea simple). Nada de cámaras, pinceles ni marcos de cristal con brillo. Icono: «an application window holding a row of small thumbnails, one of them marked with a tick» (sin número exacto de miniaturas). Violeta solo en logo, baldosa e interfaz; en la imagen generada, las cuatro tintas del Portal salvo que la persona decida la duda 2 de su hoja | **propuesta del agente, 2026-11-11**, según la fila «Mar y tecnología» de `../portal/hoja.md`; pendiente de pieza (`#24 og por proyecto` del Portal) |
| Motivos: sí | Obl. | fila o rejilla de marcos finos (la cola de intentos); un solo marco relleno de violeta (el elegido); rejilla tenue de puntos; un punto de luz | repo (`prompts/estilo.txt`, `biblia.md`) |
| Motivos r9 | Rec. | los mismos, dibujados como la carta del Portal: marcos de línea de tinta de grosor uniforme, la celda elegida como único relleno, la rejilla de puntos como retícula de carta, mucho papel vacío | **[P]** |
| Motivos: no | Obl. | cámaras, pinceles, paletas, lienzos, caballetes, chispas y varitas, robots, cerebros, caras y personas, galerías con cuadros reconocibles | repo |
| Palabras vetadas en prompts | Obl. | `camera`, `lens`, `brush`, `paint`, `palette`, `easel`, `canvas`, `sparkle`, `spark`, `magic`, `robot`, `brain`, `face`, `person`, `artist`, `gallery`, `text`, `letters`, `logo`; además `like` y nombres de lugares reales. **Para piezas nuevas (2026-11-11):** las palabras propias siguen vetadas por ética y motivo; el veto a `no`/`not`/`without`/`like` no se aplica: rige «Cómo se escribe el prompt» de `../portal/hoja.md` | repo |
| Estilo de imagen, medido | Obl. | r6-r8: marcos de vidrio, PBR, luz volumétrica, humo violeta sobre fondo oscuro (r7: 9/10 de la persona) | repo (`examples/galivelop-image-generator/prompts/`) |
| Estilo de imagen r9 | Rec. | para los recursos de marca (símbolo, cabeceras de documentación, ilustraciones de la interfaz): plano, el del Portal («flat vector illustration… thin lines of even width, no gradients, no glow, no shading… lots of empty space»), con el motivo de los marcos en vez de la carta. Las piezas `og`/`social` ya medidas siguen en vidrio hasta que una ronda mida el plano | **[P]** *(suposición: sin ronda)* |
| Lenguaje de formas | Rec. | trazo 12/128 con extremos redondos; esquinas: hoy `rx` 30/128 en la baldosa y 16/128 en el marco interior; r9: chaflán 28/128 en la baldosa, marcos interiores de esquina viva (aplicado al logo) | repo |
| Prompts | Obl. | `estilo.txt` = `og.txt` = `r2-palabras.txt`; `r5-cuadrado.txt`, `r5-vertical.txt`, `r5-cabecera.txt`, `r2-luz.txt`; 124-130 palabras; acaban en «The image is completely textless.» | repo |

**Dos estilos, un motivo.** El vidrio (r6-r8) y el plano (r9) cuentan lo mismo con los mismos marcos y el mismo violeta.
Mientras la persona no decida, cada uno tiene su sitio: vidrio en las piezas para redes ya medidas, plano en lo que
convive con el Portal. Lo que no vale es mezclarlos en una misma pieza.

## 7. Luz y atmósfera

> **r9:** estos valores son de la identidad anterior (escena oscura, vidrio) y siguen valiendo para `og` y `social`. El estilo plano **[P]** no tiene luz: fondo de papel, sin sombras; sus objetivos de YAVG y SATAVG salen de su primera ronda.

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

> **r9:** los perfiles no cambian. Las piezas hechas son de la identidad anterior; con r9 aprobada, la primera pieza plana es una cabecera de documentación, no el `og`.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Perfiles | Obl. | en la configuración: `og` 1280×640 → 1200×630 (`targetWidth`/`targetHeight` añadidos el 2026-11-04) y `social` 1280×640. Hechos en el piloto y sin perfil: `square` 1024×1024 → 1080×1080, `portrait` 896×1152 → 1080×1350, `header` 1536×512 → 1500×500 | repo (`galivelop-images.json`); los tres de r5 **[P]** (bitácora: «lo decide la persona» en F2.8) |
| Zona reservada | Obl. | `og`, `social`, `header`: `izquierda 1/2` («The left half … calm, smooth, dark navy surface, nearly empty and softly out of focus»); `square`, `portrait`: `arriba 1/2`. En píxeles, por la conversión de la plantilla (sección 9): `og` entregado 1200×630 → `0,0,600,630`; caja `data-caja` de la plantilla `60,60,604,510` (margen 60, columna 604; logo a 52-54 px de alto, titular en una línea a 52 px, filete corto en el acento y subtítulo en dos líneas; r7). La caja del piloto es 55 % del ancho menos margen (izquierda) o 48 % del alto (arriba), margen 6 %: no coincide con 1/2 y se alinea al portar a `compose` | repo (`prompts/*.txt`; `examples/pilot/componer.py` `caja_zona`). La biblia dice «tercio superior **[P]**» para `square`: r5 hizo la mitad |
| Velo por perfil | Rec. | `og` `#06121c:0`; `square`, `portrait` y `header` `#06121c:0.3` | repo (`piezas.json`, `velo`) |
| Logo en la pieza | Rec. | lockup al 9 % del alto de la pieza, margen 6 % (desde r4, que lo tuvo a ~24 px y no se leía) *(suposición: la esquina; confirmar en `componer.py`)* | repo (`r4-composicion.md`; `examples/pilot/componer.py`) |
| Composición por perfil | Rec. | no hay plantilla SVG ni `compose` en la configuración: el piloto construye el SVG en código (`componer.construir_svg`: velo en degradado, lockup al 9 % del alto, título y subtítulo). Portar a `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Sora","Inter"], fit: "cover"}` | **[P]** (F2.8/F2.12) |
| Piezas solo de logo | Rec. | `avatar` 512×512: `galivelop-image-generator-b.svg` rasterizado, sin fondo (`"fondo": null`); hecho en r5. `icon` 180/192/512: no hay | repo (`piezas.json`); `icon` **[P]** |
| Palancas extra | Opc. | no hay: sin referencias de sujeto (motivo abstracto), sin imagen inicial (la zona salió limpia en r1-r5 sin boceto), sin LUT (las piezas salen dentro de rango; `compose.lut`, F2.11, no se necesita), sin conversión final | repo (`r1-fondos.md`, `r5-piezas.md`) |
| Borrador | Opc. | no hay en la configuración; r3 midió 640×320 a 4 pasos (51 s) y anticipa estilo y hueco. Propuesto `draft: {scale: 0.5, steps: 4}` en `og` | **[P]** (F2.10, dec. 7) |
| Prioridad | Rec. | 1) logo elegido y `avatar` 512; 2) `social` 1280×640; 3) `og` 1200×630. Hechas en el piloto, además, `square`, `portrait` y `header` (r5) | repo (`biblia.md` §9) |

## 10. Textos de composición

> **r9:** el nombre que se compone es «Galivelop IG» (D38). En las piezas, titular en Big Shoulders Display y subtítulo en Literata **[P]**; hoy, Sora e Inter (la interfaz ya usa las nuevas).

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

> **r9:** los umbrales son los medidos con la identidad anterior. No se aplican a una pieza plana hasta que una ronda fije los suyos.

| Campo | Nivel | Valor | Estado |
|---|---|---|---|
| Veredicto | Obl. | la persona; delegado al agente desde el 2026-10-26. Apuntado en `docs/records/contenido/r1-fondos.md` (sí, s3 y s4, «de las mejores»), `r2-estilo.md` (elegida «palabras»), `r4-composicion.md`, `r5-piezas.md` | repo |
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
- `docs/records/contenido/calibracion-measure.md` (umbrales y medidas), `r1-fondos.md`, `r2-estilo.md`,
  `r4-composicion.md`, `r5-piezas.md` (veredictos y medidas).
- `examples/pilot/componer.py` (`caja_zona`, ajuste del texto), `examples/pilot/fuentes.sh` (origen y licencia de las fuentes).

**Portal-Galivelop** `aa76b34` (marca paraguas, «heredado de»), leído solo a través de `docs/marcas/portal/biblia.md` y
`docs/records/lectura-2026-10-26-tarkor-y-marcas.md`: `src/estilos/global.css` (fondos, texto, superficies, borde),
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

## Contradicciones

Entre esta hoja (r9) y lo que había en el repo. **Resueltas por la persona el 2026-11-11**; cada una lleva su decisión.

1. **La interfaz usaba la identidad anterior.** `gimg/ui/css/tokens.css` (D39) tenía fondo oscuro, Sora e Inter.
   **Decisión:** aplicar r9 a `tokens.css` en tarea propia (rama `claude/marca-r9`), con tema claro por defecto y el
   oscuro (`#0d171e`) como alternativa; hasta que llegue a `main` manda el `tokens.css` de `main`. **Aplicado el
   2026-11-11** (`de53727`).
2. **Claro u oscuro por defecto.** **Decisión: claro** (papel `#fbfcfd`) por defecto en interfaz y documentación, oscuro
   (`#0d171e`) como alternativa; las piezas `og`/`social` siguen oscuras hasta una ronda plana.
3. **Vidrio o plano.** r6-r8 (vidrio, luz volumétrica; r7 con 9/10) contradice «sin degradados ni brillo» del Portal.
   **Decisión: dos estilos, medir antes** («Dos estilos, un motivo», sección 6): no se tira lo medido; el plano entra
   por los recursos de marca y se mide en una ronda antes de tocar `og.txt`.
4. **Logo con degradado y `rx` 30/128** frente a baldosa plana con chaflán 28/128. **Decisión:** redibujar símbolo,
   lockup y favicon según la tabla de la sección 4, en la misma tarea que la interfaz; los SVG anteriores pasan a
   historia. **Aplicado el 2026-11-11** (`1b211f6`); falta el monograma «IG», decidido por la persona (2026-11-12) como símbolo.
5. **El azul del Portal.** **Decisión: solo ese uso.** El celeste `#1aa6df` sigue prohibido como acento de la
   herramienta; se admite únicamente como `--family` (≤ 2 %) en el enlace «parte de Galivelop». `biblia.md` lo recoge.
6. **D38 sin aplicar.** **Decisión:** «Galivelop IG» (siglas «GVIG») se aplica al README, a los textos de
   `examples/galivelop-image-generator` y a la interfaz en la misma tarea que r9. **Aplicado el 2026-11-11** (`1ca2bb6`;
   la interfaz ya lo decía y los textos de `examples/` no nombran el producto).
7. **`brand.palette` de la configuración** tiene los 4 hex de la identidad anterior, con los que se midió el 72-88 %.
   **Decisión:** no se toca hasta la ronda plana; entonces, los 6 hex de la sección 3.

## Cambios que pediría a la plantilla

1. **Un apartado «Idea de marca»** antes de la ficha: una frase que explique por qué la marca es así. Sin ella, la hoja
   es una lista de valores y dos agentes la rellenan distinto.
2. **Una tabla «se comparte / es propio»** para las marcas que son variante de otra: hoy «heredado de `<marca>`» va
   celda a celda y no se ve el conjunto.
3. **Roles con dos temas** en la paleta (hex claro y hex oscuro por rol, con su contraste): la plantilla supone un solo
   fondo.
4. **«Sistema de logo» como tabla de piezas** (símbolo, línea, favicon, monograma, nombre, lockup), como en la hoja de
   Tarkor, en vez de una lista de archivos.
5. **Una fila «Hoy»** donde lo propuesto y lo aplicado difieren, para que la hoja no mienta mientras espera el «sí».

## Lo que enseñó rellenarla

Los 17 cambios propuestos a la plantilla el 2026-11-04 se aplicaron ese día (aprobados por la persona); los 5 de arriba
son nuevos y están pendientes.

**Balance de r9:** de los 15 obligatorios, 12 siguen completos desde el repo (son los de la identidad anterior, que es la
aplicada) y 3 eran **[P]** (acento, logo, titular). r9 nació como propuesta; el 2026-11-11 se aplicaron la paleta por roles
y las tipografías (interfaz), el sistema de logo (salvo el monograma) y el nombre. Siguen **[P]** el estilo plano, sin
ninguna ronda medida, `brand.palette` y las piezas. Lo que la hoja gana es criterio:
qué se comparte con el Portal, qué es propio y por qué.

**Lo aprendido:** una variante se define mejor por lo que **no** cambia (papel, tinta, línea, letras) que por su acento;
y una hoja propuesta tiene que decir en cada fila qué hay hoy, o quien la lea aplicará lo que aún nadie aprobó.

## Historia

- **r9 (2026-11-11):** variante de la identidad nueva del Portal; propuesta.
- **2026-11-04 a 2026-11-05 (hasta r8):** identidad oscura con violeta, familia del Portal anterior (`aa76b34`), Sora e
  Inter, vidrio en las piezas. Hoja entera: `git show a4e394d:docs/marcas/galivelop-image-generator/hoja.md`.
