# Hoja de estilo mínima de un proyecto (plantilla)

**Para quién:** quien lleva un proyecto (o el agente que lee su repo) y quiere que `gimg` le haga piezas de marca:
`og`, `social`, `square`, `portrait`, `header`, `banner`, `avatar`, `icon`. **Borrador de F2.12** (pedido de la persona
del 2026-11-04); se ajusta con lo que enseñen r2-r4 y se congela en r5. Los 17 cambios que dejó rellenarla por primera vez
([`galivelop-image-generator/hoja.md`](galivelop-image-generator/hoja.md)) están aplicados desde el 2026-11-04, aprobados
por la persona.

**Cómo se usa:**

1. Se copia esta plantilla y se rellena campo a campo, en este orden. Una hoja rellena vive en
   `docs/marcas/<proyecto>/biblia.md` (aquí) mientras su repo no la adopte, y se le propone en
   `docs/propuestas/<proyecto>.md`. **El repo del proyecto manda:** cada dato que sale de él se cita con ruta y commit.
   **Al rellenar, cada tabla se queda en cuatro columnas: Campo / Nivel / Valor / Estado.** «Qué es y formato», «Ejemplo» y
   «Dónde acaba» se quitan (esta plantilla sigue siendo donde se consultan); el estado y la fuente de cada valor van en
   «Estado».
2. De la hoja salen tres cosas, y la columna «Dónde acaba» de cada campo dice cuál: la configuración
   `galivelop-images.json` (esquema `gimg/schemas/project-config.schema.json`), los prompts
   (`examples/<proyecto>/prompts/*.txt` y el `prompt` de cada pedido) y las plantillas SVG de composición. Lo que no acaba en
   ninguna de las tres «solo lo lee el agente» al escribir prompts y plantillas.
3. Tres niveles por campo:
   - **Obligatorio (Obl.):** sin esto no se genera una pieza de marca correcta. Cada uno lleva su porqué en media línea.
   - **Recomendado (Rec.):** mejora mucho el resultado o ahorra una ronda.
   - **Opcional (Opc.):** afina.

   **Hay 18 campos obligatorios** (los de las secciones 0-12 cuyo nivel empieza por «Obl.»). Con la familia Galivelop
   (sección 0) son **15**: fondo, texto y titular pasan a Rec. con el valor de la familia. El validador (sección 14) cuenta
   los Obl. de la hoja rellena y los compara con esta cifra; si la plantilla cambia de cifra, se cambia aquí y allí.
4. **Un dato desconocido se escribe «no hay» o *(suposición)*; nunca se inventa.** Estados, como en
   [README.md](README.md): sin marca sale del repo; **heredado de `<marca>`** sale del repo de una marca paraguas leído a
   través de su biblia (se cita con la ruta y el commit de esa marca, que se anota en «Hereda de» de la ficha, y con un
   bloque propio por repo en la sección 13); **[P]** es propuesta pendiente de la persona; *(suposición)* se comprueba en
   una ronda. Un campo obligatorio admite «no hay» solo donde la tabla da una salida por defecto.
5. **Mínimo = obligatorio, pero cuantos más detalles mejor.** Cada ronda que se ahorra son ~3 min de Deck por pieza con
   el modelo rápido y ~1 h con el de calidad.

Reglas que valen para toda la hoja: los prompts van en inglés, en frases completas y en positivo, sin prompt negativo
(FLUX con cfg 1 lo ignora) y **sin nombrar lo que no se quiere ver** (el modelo pinta lo que se nombra, también negado o en
una comparación); el texto y el logo nunca los genera el modelo, los pone la composición (D28, D29).

---

## 0. Ficha

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Nombre de marca | Obl. | Como se escribe en público, con mayúsculas y puntos exactos | «toVeriAI», «Tarkor» | solo el agente (wordmark del lockup, textos) |
| Nombre en código | Obl. *(es la clave del proyecto en `gimg`)* | `^[a-z0-9][a-z0-9-]*$` | `tarkor`, `galivelop-workflow` | `name` |
| Fuente de verdad | Rec. | Repo, rama y commit de donde salen los datos; rutas por campo en la sección 13 (un bloque por repo) | `VeriNews_AI` `02ac654`, `Documentacion/v1.1/kit-visual-ia.html` | solo el agente |
| Quién decide | Obl. *(sin un «sí» nada pasa a definitivo)* | Persona que da el veredicto; si lo delega, a quién y desde cuándo | «la persona; delegado al agente el 2026-10-26 hasta que diga otra cosa» | solo el agente (registro de la ronda) |
| Fecha de la hoja | Rec. | AAAA-MM-DD de la última revisión | `2026-11-04` | solo el agente |
| Familia visual | Rec. | `Galivelop` (hereda los valores de abajo) o `propia` (se rellena todo) | `Galivelop` (herramientas del taller) | solo el agente; rellena fondo, texto, tipografía y baldosa |
| Hereda de | Opc. | Marca paraguas y su commit, si hay datos «heredado de» | Portal-Galivelop `aa76b34` | solo el agente (sección 13) |

**Familia Galivelop.** Con `Galivelop` la hoja puede dar por rellenados, sin repetir su cita, estos valores (heredados del
Portal): fondo `#06121c` (oscuro, por defecto) o `#f6fafd` (claro); texto `#eaf4fa` sobre oscuro y `#0a1a28` sobre claro;
titular Sora 700 (reserva `sans-serif`) y texto Inter 400/500; baldosa del logo (`rx` 30/128, trazo 12). Una hoja de
herramienta se reduce entonces al acento, los motivos, las palabras vetadas, los perfiles y los textos. Cualquier valor que
cambie se escribe y se justifica.

## 1. Identidad

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Propósito | Obl. *(sin saber qué es el proyecto, el motivo de la pieza es arbitrario)* | Una frase: qué hace y para quién | «Analiza noticias y devuelve el IMI 0-100; para quien quiere medir antes de creer» | solo el agente (elige motivo y sujeto del prompt) |
| Lema | Rec. | La frase de marca, literal, en su idioma | «La verdad no es binaria» · «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas» | `text` del pedido (`title`/`subtitle`) |
| Tono | Rec. | 3-5 adjetivos y lo que no es | «sereno, editorial, nada sensacionalista» · «cercano, concreto, honesto; sin vender» | prompt: «Mood: …» y elección de motivos |
| Idiomas | Opc. | Códigos de los idiomas en que se publican las piezas; el primero manda. `es` salvo que el repo publique piezas en otro | `es, gl, en` (Portal); `es` por defecto | `text` del pedido (una pieza por idioma) |
| Campo semántico | Opc. | Palabras propias y palabras fuera | dentro: relevo, bitácora, sello; fuera: magia, robot | solo el agente |

## 2. Ética en imagen

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Nunca se muestra | Obl. *(una pieza que enseña lo vetado es incorrecta aunque sea bonita; «no hay nada especial» también es respuesta)* | Lista de cosas, situaciones y tópicos que la marca no enseña | toVeriAI: alarmismo, sellos FAKE, lupas sobre prensa, rojo de error. Tarkor: interfaz de juego falsa, humanos, luna, «AAA genérico». Workflow: robots, cerebros, autonomía total de la IA | solo el agente; se traduce en la lista de palabras vetadas (sección 6) |
| Personas y rostros | Rec. | Si pueden aparecer personas; si se pueden sugerir personas reales | «nunca personas de stock»; voces: «nada que sugiera clonar a alguien» | prompt (se omiten) y palabras vetadas |
| Promesas | Rec. | Lo que la pieza no puede afirmar (fechas, precios, «contrata») | Portal: nada de «encargo», «de pago», gráficas de crecimiento | `text` del pedido |

## 3. Paleta

Mínimo tres roles, porque la composición los necesita (fondo bajo el texto, color del texto y un acento) y
`gimg measure` mide la pieza contra ellos. Cuantos más roles, mejor mide y mejor compone.

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Fondo | Obl. fuera de la familia Galivelop; Rec. dentro *(decide pieza clara u oscura y el velo)* | hex `#RRGGBB`, uno por variante (clara / oscura) | Tarkor: hueso `#f1e4d0` (clara), madera 900 `#241a10` (oscura) | `brand.palette`; velo de la plantilla SVG; prompt («the left third … in the colour #8a9aa8») |
| Texto | Obl. fuera de la familia Galivelop; Rec. dentro *(sin él no hay contraste que medir)* | hex, sobre fondo claro y sobre oscuro | hierro `#221c16` sobre claro; hueso `#f1e4d0` sobre oscuro | plantilla SVG (`fill`); `gimg measure --text` |
| Acento | Obl. *(el único color que hace de marca en la imagen; uno por pieza)* | hex; si hay varios candidatos, cuál manda fuera del producto | Tarkor arcilla `#E0703A` **[P]** (cristal `#4aa8d8` dentro del juego); toVeriAI verde `#2D6A4F` | `brand.palette`; prompt («a single warm accent in #E0703A»); logo |
| Resto de la paleta | Rec. | Tabla rol / hex / uso (3-12 colores más): superficies, bordes, secundarios, semánticos | toVeriAI: papel `#F7F5F2`, ámbar `#B5832A` y granate `#9B2335` solo si la pieza habla del IMI | `brand.palette` (≤ 16 hex en total, `^#[0-9A-Fa-f]{6}$`) |
| Combinaciones | Rec. | Qué va con qué en pieza clara, pieza oscura y sobre imagen (velo: hex y opacidad 0-1) | Tarkor clara: `#f1e4d0` + texto `#221c16` + velo `#f1e4d0:0.55`; oscura: `#241a10` + `#f1e4d0` + velo `#221c16:0.45` | plantilla SVG |
| Prohibidos | Rec. | Colores y efectos que no entran | `#000` y `#fff` puros, neón, morado (Tarkor), azules corporativos (toVeriAI), más de un acento por pieza | solo el agente; palabras vetadas |
| Degradados | Opc. | Dónde se permiten | solo la baldosa de la familia Galivelop | logo SVG |

**Cómo se mide** (`gimg measure <imagen> --project <p>`): `palette_pct` es el % de píxeles a ΔE76 < 15 de algún color
de `brand.palette`, sobre la imagen reducida a 256 px de ancho; `palette_by_color` reparte ese % por color. Calibrado
(`docs/records/contenido/calibracion-measure.md`): Tarkor ≥ 30 % (su portada da 42), toVeriAI ≥ 65 %, workflow ≥ 90 %.
r2 enseñó que decir el color en palabras, en hex o por materiales da casi la misma imagen: el prompt lleva una línea
«Colours: #…, #…» por costumbre, no porque el modelo obedezca el hex.

## 4. Logo

Los logos **nunca se generan** (D29): son SVG a mano, idénticos en todas las piezas. El generador solo los coloca.

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Símbolo SVG | Obl. *(sin él no hay `avatar`, `icon` ni logo en las piezas; «no hay» vale y entonces solo salen fondos y texto, y se dice quién lo dibuja)* | Ruta relativa dentro del repo del proyecto a un `.svg`: `viewBox="0 0 128 128"`, sin texto, sin raster, sin `filter`, sin fuentes incrustadas, `<title>`, solo colores de la paleta; legible a 16 px | `docs/marcas/tarkor/logos/tarkor-a.svg` | `profiles.<p>.compose.logo` (`{{logo}}`); copia en `examples/<p>/logos/` idéntica byte a byte **[P]** |
| Lockup (símbolo + nombre) | Rec. | Ruta a un `.svg` de alto 128 con el símbolo a la izquierda y el nombre. Vale `<text>` con `font-family` y reserva genérica mientras `compose.fonts` garantice la fuente; el nombre en trazos es Opc., para cuando la pieza salga del taller | `tarkor-a-lockup.svg` (sobre oscuro), `tarkor-a-lockup-claro.svg` | `compose.logo` del perfil que lo use |
| Variante clara y oscura | Rec. | Qué archivo va sobre cada fondo; si solo hay uno, sobre cuál funciona | toVeriAI: «to»/«AI» negro sobre claro, blanco sobre oscuro; «Veri» siempre verde | plantilla SVG (un perfil, una variante) |
| Tamaño mínimo y margen | Rec. | px mínimos del símbolo y del wordmark; margen libre alrededor | Tarkor: símbolo 16 px, wordmark 20 px de alto; margen = altura de la «T» | plantilla SVG |
| Usos prohibidos | Opc. | Lo que no se hace con el logo | estirar, rotar, sombra, brillo, símbolo sin wordmark fuera de esquina y avatar | solo el agente |
| Logo fuera de la paleta | Opc. | Si el logo usa colores que no están en la paleta (y por qué) | Portal: degradado `#2BB3EA → #0083C1` | `brand.palette` (se añaden) |

Comprobación antes de entregar un SVG: `rsvg-convert -w 512` y `-w 32`, mirados.

## 5. Tipografía

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Familia de titular | Obl. fuera de la familia Galivelop; Rec. dentro, con Sora 700 escrito *(toda pieza compuesta lleva titular)* | Nombre exacto de la familia, peso, y una genérica de reserva (`serif` / `sans-serif`) | Cinzel 700 (reserva `serif`); Cormorant Garamond 400, nunca bold | `compose.fonts` (nombres, ≤ 10); plantilla SVG (`font-family`) |
| Familia de texto | Rec. *(por defecto Inter)* | Igual, para subtítulos y cuerpo | Inter 400/500; DM Sans 400-500 | `compose.fonts`; plantilla SVG |
| Licencia y archivo | Rec. | Licencia que permita instalarla (OFL, Apache) y de dónde se baja o en qué ruta del repo está | Cinzel e Inter OFL, en `frontend/src/assets/fonts/` de WMF | `gimg doctor` comprueba que está instalada (`~/.local/share/fonts`) |
| Tracking y mayúsculas | Opc. | Tracking en em, uso de mayúsculas, eyebrows | «TARKOR» tracking 0,18 em; eyebrows DM Sans 0,28-0,32 em | plantilla SVG |

## 6. Escenas y motivos (lo que el modelo pinta)

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Motivos Sí | Obl. *(es el sujeto del prompt; sin al menos uno no hay nada que pedir)* | 1-5 motivos en positivo, con materiales y texturas | Tarkor: agujas de roca de hierro sobre crestas de arena, empalizada de troncos, estandarte al viento. toVeriAI: dos tintas de acuarela sobre papel que se rozan sin mezclarse | `prompt` del pedido; `examples/<p>/prompts/estilo.txt` |
| Motivos No | Obl. *(lo que, de salir, tira la pieza)* | Lista de cosas que no se piden ni se nombran | personajes, criaturas fuera del canon, interfaz, tráiler AAA, oscuridad total | solo el agente (no se escriben en el prompt) |
| Palabras vetadas | Obl. *(el modelo pinta lo que se nombra: sin la lista, una negación las mete)* | Lista en inglés, minúsculas, una por línea; incluye lo que se parezca a texto o logo | Tarkor: `moon`, `moonlight`, `crystal dust`, `scar`, `sun`, nombres propios. toVeriAI: `fake`, `stop`, `magnifying glass`, `stamp`, `pink`, `magenta` | solo el agente; comprobable por script sobre cada `prompt` (hueco, sección 15) |
| Estilo de imagen | Rec. | Una línea «Style: …» y otra «Mood: …» para cerrar el prompt | «Style: cinematic landscape photograph, natural muted colours, subtle filmic grade. Mood: wild, quiet, lived-in.» | final del `prompt`; `profiles.<p>.style` (sin usar hoy: pesa poco) |
| Lenguaje de forma | Opc. | Radios, grosores, línea vs. relleno | toVeriAI: línea fina ~1,3 px sin relleno, radios 3-6 px | plantilla SVG; prompt |

Plantilla de prompt (120-320 palabras): `[escena y luz, lo importante primero] → [zona reservada, en fracciones desde un
borde] → [sujeto y su posición, un ancla nombrada una vez] → [detalles de vida] → Style: … Colours: … Mood: … The image
is completely textless.` Sin negaciones, sin «like …», sin lugares reales.

## 7. Luz y atmósfera

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Dirección de la luz | Rec. | De dónde viene (lateral, rasante, contraluz) **sin nombrar la fuente** («sun» pinta el disco) | «a warm raking light comes from low behind them, from the right» | `prompt` |
| Momento y clima | Rec. | Día / atardecer / noche; calima, lluvia, nieve; si la escena es oscura o sobria **se dice al principio** | «in low subdued light, the ground darker than the sky» | `prompt`, primera frase |
| Luminosidad objetivo (YAVG) | Rec. | Rango 0-255 medido sobre la imagen de marca | Tarkor 105-150 (portada 127); toVeriAI 180-225; workflow 30-50 | solo el agente; `gimg measure` (`yavg`) |
| Saturación objetivo (SATAVG) | Rec. | Rango medido igual | Tarkor 18-32 (portada 25); toVeriAI ≤ 10; Portal 13-19 | solo el agente; `gimg measure` (`satavg`) |

Sin estos datos se usa luz natural suave por dirección, y los rangos de `calibracion-measure.md` si el proyecto está allí.
Las pautas de luz son del 2026-11-02 y **r2-luz las está comprobando** *(suposición hasta su veredicto)*.

## 8. Referencias de marca

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Imágenes de marca | Rec. *(sin ellas no hay EMD ni rangos propios: se usan los de la calibración; sirve también de «lo ya publicado»)* | Dos datos por imagen, 1-3 imágenes: **publicada dónde** (ruta, repo, commit; así se sabe qué existe y no se repite) y **vale como referencia** (sí / no / **[P]**, según la persona) | Tarkor: `public/proyectos/tarkor/portada.webp` (Portal `aa76b34`), ya enseña los Pilares Rotos: el `og` va con otro motivo; toVeriAI: su portada es casi blanca, **[P]** si vale | `gimg measure --refs` (EMD Y/Cb/Cr); solo el agente (motivo que no se repite) |

## 9. Formatos y piezas

Un perfil por tamaño de destino. Se genera a un tamaño del modelo (múltiplos de 64, 64-4096 px) y se entrega al de
destino (`targetWidth`/`targetHeight`, 16-4096), recortando a `cover` o escalando a `contain`.

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Perfiles | Obl. *(sin al menos uno no hay nada que generar)* | Tabla: perfil (`^[a-z][a-z0-9]*$`) / generación an×al / destino an×al / dónde se publica | `og` 1280×640 → 1200×630, og:image y vista previa en LinkedIn, Discord y X; `square` 1024×1024 → 1080×1080, Instagram; `header` 1536×512 → 1500×500, X | `profiles.<p>.width/height/targetWidth/targetHeight`; modelo, pasos, cfg y sampler los da el catálogo (`flux2-klein-4b-q8`, 6, 1.0, euler) |
| Zona reservada | Obl. *(sin ella el texto cae sobre el sujeto y el contraste no se puede medir)* | Por perfil, **una sola forma: fracción del lado y borde** (`izquierda 1/3`, `abajo 1/3`, `arriba 1/2`); la misma frase vale en el prompt, la plantilla SVG y la medida (conversión debajo de la tabla) | Tarkor: tercio izquierdo en `og`, `banner`, `header`; tercio inferior en `square` y `portrait`. toVeriAI: tercio superior de papel liso | `prompt` («the left third, from the left edge inward, is a calm, open stretch…»); plantilla SVG (caja del texto); `gimg measure --zone x,y,w,h` |
| Composición por perfil | Rec. | Plantilla SVG con huecos `{{title}}`, `{{subtitle}}`, `{{logo}}`; campos (≤ 10, `^(?!logo$)[a-z][a-zA-Z0-9]*$`); `fit` | `compose: {template, logo, fields: ["title","subtitle"], fonts: ["Cinzel","Inter"], fit: "cover"}` | `profiles.<p>.compose` |
| Piezas solo de logo | Rec. | `avatar` 512×512 e `icon` 180/192/512: símbolo sobre fondo plano, sin modelo | Tarkor avatar: `tarkor-a.svg` sobre `#241a10` | hoy fuera del perfil (hueco, sección 15); las hace `examples/pilot/piezas.py` |
| Borrador | Opc. | Cómo se abarata una prueba del perfil | `draft: {scale: 0.5, steps: 4}` (lo medido en r3) | `profiles.<p>.draft` |
| Velo por perfil | Rec. *(cambia de perfil a perfil: Galivelop `0` en `og`, `0.3` en el resto)* | Hex y opacidad 0-1 del velo de cada perfil compuesto, tras medir el contraste | `#06121c:0.3` en `square`; `#f1e4d0:0.55` en `og` clara | plantilla SVG; hueco, sección 15 |
| Logo en la pieza | Rec. *(sin él, un lockup sale ilegible: a 24 px en r4)* | Por perfil: esquina, % del alto de la pieza y separación del texto | lockup en la esquina inferior izquierda, 9 % del alto, margen 6 % | plantilla SVG; hueco, sección 15 |
| Palancas extra | Opc. | Una fila para lo que casi nunca se usa; «no hay» por defecto. Referencias de sujeto (cuestan +60 % y **no** dan acabado ni paleta; `references` del pedido, rutas dentro del repo, D25), imagen inicial (boceto SVG rasterizado con fuerza 0,85-0,97 para forzar la zona; `initImage` y `strength`), gradación o LUT (`.cube`; `compose.lut`, F2.11, aún no existe), conversión final (webp, ≤ KB; fuera de `gimg`, D35) | Tarkor: 304 `.webp` solo para fauna; Portal: `.webp` 1600×640; «si la zona no sale limpia, boceto a 0,95» | pedido o solo el agente, según la palanca |
| Prioridad | Rec. | Las 3-5 piezas de la primera ronda, en orden | 1) og 2) banner y cabecera de Discord 3) square con el lema 4) avatar | solo el agente (plan de la ronda) |

**Zona reservada a píxeles.** Sobre el tamaño entregado (`targetWidth`×`targetHeight`, o el de generación si no hay): borde
izquierdo o derecho, `w = fracción × ancho` (`x = 0`, o `x = ancho − w`), `y = 0`, `h = alto`; borde superior o inferior,
`h = fracción × alto` (`y = 0`, o `y = alto − h`), `x = 0`, `w = ancho`. Es lo que se pasa a `gimg measure --zone x,y,w,h`.
La caja del texto en la plantilla es esa zona menos un margen (el que declare la hoja, por ejemplo el 6 %).

Tabla común de destinos en [README.md](README.md) («Común a todos»).

## 10. Textos de composición

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Titular del primer perfil compuesto | Obl. *(el pedido de una pieza compuesta no sale sin `text`; el `avatar` y el `icon` no llevan texto)* | Frase literal, en el idioma de la pieza; una línea; orientativo ≤ 40 caracteres en `og` (lo que cabe en un tercio a Sora 700) | «El mundo sigue aunque tú te detengas.» (37) | `text.title` del pedido (≤ 200 caracteres, sin control) |
| Subtítulo | Rec. | Una línea; orientativo ≤ 70 caracteres | «RPG narrativo de fantasía con IA local. En desarrollo, a la vista.» (64) | `text.subtitle` |
| Variaciones, ganchos y cierres | Rec. | 2-3 de cada, para `square`, `portrait`, `header` y redes | «Deja la partida. El mundo sigue.» · «Juega en local. Nadie mira.» | `text` de otros pedidos |
| Longitud máxima por campo | Rec. | Caracteres por campo y perfil, o «la fija la plantilla» | título 2 líneas con `title1`/`title2` partidas a mano | plantilla SVG; test que comprueba que cada línea cabe **[P]** |
| Wordmark compuesto como texto | Opc. | Si el nombre se escribe con tipografía en vez de logo, y sus colores | toVeriAI: «to**Veri**AI», «Veri» en `#2D6A4F` | plantilla SVG |

## 11. Entrega

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Carpeta de entrega | Obl. *(el esquema la exige; es lo único que `gimg` escribe en el repo del proyecto, D25)* | Ruta relativa a la raíz del repo, sin `..` ni absoluta | `entrega`, `public/proyectos/tarkor` | `delivery.dir` |
| Nombre del archivo | Rec. | Plantilla con `{key}` y `{profile}`, acabada en `.png` | `{key}-{profile}.png` (por defecto) → `estilo-og.png` | `delivery.template` |
| Dónde se publica cada pieza | Rec. | Ruta o etiqueta que consume la pieza en su repo o web | og:image de `index.html` (hoy apunta al favicon de 512); `public/proyectos/tarkor/portada.webp` (1600×640) | solo el agente (propuesta al repo) |
| Manifiesto | Opc. | Dónde queda la lista de entregas | `galivelop-images.manifest.json` (por defecto) | `manifest` |
| Conversión final | Opc. | Si el repo pide otro formato o peso (webp, ≤ KB) | Portal: `.webp` 1600×640 | solo el agente (fuera de `gimg`, D35) |

## 12. Aceptación

El juicio a ojo («se lee como la marca») va antes que la medida; `gimg measure` lo apoya y nunca acepta una pieza sola.
Reglas de ronda: cada palanca en 2 semillas (3 y 7); lo que no mejora en 2 rondas sale del prompt y pasa a boceto, LUT o
composición; una ronda se cierra con la mayoría de piezas «sí».

| Campo | Nivel | Qué es y formato | Ejemplo | Dónde acaba |
|---|---|---|---|---|
| Veredicto | Obl. *(ya en la ficha: quién da el «sí»; sin veredicto decide el agente y lo apunta)* | Persona o delegado; dónde se apunta | `docs/records/contenido/rN-<tema>.md` | solo el agente |
| Contraste del texto | Rec. *(por defecto WCAG ≥ 4,5:1; ≥ 3:1 en titulares grandes)* | Relación mínima entre el color del texto y la zona reservada, con velo si lo hay | Tarkor og r4: peor 6,97:1; toVeriAI: 15:1 | `gimg measure --zone --text` (`contrast.worst`) |
| Umbrales de medida | Rec. | Los números **no se repiten aquí**: % de paleta mínimo de la sección 3, YAVG y SATAVG de la sección 7 | Tarkor ≥ 30 % y 105-150 / 18-32; toVeriAI ≥ 65 % | solo el agente (`calibracion-measure.md`) |
| EMD frente a la marca | Opc. | Mediana por canal; Cb ≲ 6 y Cr ≲ 7,5 son los de Tarkor, a revalidar por marca; la EMD de Y pesa la composición y no sirve sola | toVeriAI ≤ 6 / ≤ 6; workflow ≤ 3 / ≤ 4 | `gimg measure --refs` (`emd_median`) |
| Cuándo se da por bueno el estilo | Opc. | Regla de cierre | «3 piezas prioritarias con “sí” a la primera o segunda ronda» | solo el agente |

## 13. Fuentes de verdad

Un bloque por repo (el del proyecto y, si hay, el de la marca paraguas «Hereda de»), con una línea por dato que sale de
él: `repo` `commit`: `ruta` `líneas` (qué). Lo que no tenga línea aquí es **[P]** o *(suposición)*. Ejemplo:
`WMF 73965f62: frontend/src/index.css l.23-54 (madera, hierro, cristal, acero)`.

**Lo que la configuración no refleja aún.** Lista de diferencias entre la hoja y `galivelop-images.json` (color fuera de
`brand.palette`, perfiles hechos sin declarar, destino sin `targetWidth`/`targetHeight`, prompt que incumple la
comprobación 8 o 9): es la entrada de `docs/propuestas/<proyecto>.md`. Vacía, se escribe «nada».

---

## 14. Lista de comprobación de lo obligatorio

Redactada para que un script la valide: «Máquina» dice qué la comprueba hoy, o «nadie aún». Las de «criterio» las mira
el agente o la persona al recibir la hoja.

| # | Comprobación | Máquina / criterio | Quién la hace hoy |
|---|---|---|---|
| 1 | `name` existe y cumple `^[a-z0-9][a-z0-9-]*$` | máquina | esquema (`gimg project add`) |
| 2 | Propósito en una frase | criterio | agente |
| 3 | «Nunca se muestra» tiene lista o dice «no hay nada especial» (nunca vacío) | máquina (campo presente y no vacío) | nadie aún |
| 4 | `brand.palette` con ≥ 3 hex válidos `^#[0-9A-Fa-f]{6}$`, ≤ 16, y la hoja nombra fondo, texto y acento | máquina (hex y cuenta); criterio (roles) | esquema (hex y ≤ 16); nadie el mínimo de 3 ni los roles |
| 5 | Símbolo SVG: ruta relativa `.svg` dentro del repo, `viewBox="0 0 128 128"`, sin `<text>`, sin `<image>`, sin `filter`; o «no hay» con quién lo dibuja | máquina (ruta, extensión, viewBox, etiquetas); criterio (legible a 16 px) | esquema (`svgPath`, dentro de la raíz); `rsvg-convert` a mano; identidad con `docs/marcas/<p>/logos/` **[P]** |
| 6 | Familia de titular con reserva genérica, instalada | máquina | `gimg doctor` (`compose.fonts`) |
| 7 | ≥ 1 motivo Sí; motivos No; lista de palabras vetadas no vacía | máquina (listas no vacías); criterio (sentido) | nadie aún |
| 8 | Ningún prompt del proyecto contiene una palabra vetada ni una negación (`no`, `not`, `without`, `never`) ni «like»; sin excepciones, el cierre tampoco | máquina | nadie aún (grep sobre `prompts/*.txt` y `orders/*.json`) |
| 9 | Todo prompt acaba en «The image is completely textless.» y tiene 120-320 palabras | máquina | nadie aún |
| 10 | ≥ 1 perfil con `width`/`height` múltiplos de 64 entre 64 y 4096; `targetWidth`/`targetHeight` cuando el destino difiere | máquina | esquema (rango y pareja); `multipleOf` pendiente (leve de F0) |
| 11 | Cada perfil compuesto declara su zona reservada (fracción y borde) y el prompt la describe | máquina (campo presente); criterio (que salga limpia: `measure --zone`) | nadie aún |
| 12 | Titular de la primera pieza: ≤ 200 caracteres, sin control, cabe en la columna de la plantilla | máquina | esquema del pedido (200); test de ajuste **[P]** |
| 13 | `delivery.dir` relativa, sin `..` | máquina | esquema |
| 14 | «Quién decide» rellenado | máquina (no vacío) | nadie aún |
| 15 | Todo hex nombrado en Fondo, Texto y Acento (y en el logo) está en `brand.palette` | máquina | nadie aún |
| 16 | Si la hoja da un destino distinto del tamaño de generación, el perfil lleva `targetWidth` y `targetHeight` | máquina | nadie aún |

Lo que hoy hace «nadie aún» se junta en un validador de la hoja, **decidido el 2026-11-04: `gimg doctor --project <p>`,
antes de r5** (aún no implementado). Además de las 16 comprobaciones, cuenta los campos Obl. de la hoja rellena: **18**
(15 con la familia Galivelop, sección 0). Las 15 y 16 miran la coherencia entre hoja y configuración; lo que falle se apunta en
«Lo que la configuración no refleja aún» (sección 13).

## 15. Huecos

**Campos de la hoja sin sitio en `galivelop-images.json` hoy** (se leen de la hoja o acaban en el prompt / la plantilla):

- Roles de la paleta: `brand.palette` es una lista plana de hex; fondo, texto y acento no se distinguen (la plantilla SVG
  los lleva a mano).
- Zona reservada: solo existe en el texto del prompt y en la caja de la plantilla SVG; `measure --zone` la pide a mano en
  píxeles (la conversión desde fracción y borde está en la sección 9, pero ningún campo la hace).
- Velo y logo en la pieza (posición, % del alto, separación): solo en la plantilla SVG o en el código del piloto
  (`componer.py`); `compose` no los lleva.
- Palabras vetadas y motivos No: no hay campo; nada impide que un pedido las lleve.
- Umbrales de aceptación (YAVG, SATAVG, % paleta, EMD, contraste): viven en `calibracion-measure.md`; `measure` no da
  veredicto a propósito (F2.9, dec. 2).
- `avatar` e `icon`: no se pueden declarar (`width`/`height` obligatorios y todo pasa por la cola); los compone el piloto.
  Decidido para F2.12 (F2.10, dec. 6).
- Varias variantes de logo: un perfil admite un `compose.logo`; clara y oscura obligan a dos perfiles o dos plantillas.
- Tipografía: `compose.fonts` lleva nombres; licencia y archivo no se declaran (`gimg doctor` solo mira que esté instalada).
- Imágenes de marca para la EMD: `references` es del pedido y fija sujeto; no hay lista de referencias de marca a nivel de
  proyecto.
- Longitud máxima por campo de texto: el esquema del pedido fija 200; el ajuste a la columna es un test **[P]**, no un dato.
- Idiomas y textos por idioma: una pieza por pedido; nada agrupa las variantes.
- `compose.lut` (F2.11) y `style.lora` (F5) aún no existen.
- Copia de los logos en `examples/<p>/logos/` idéntica a `docs/marcas/<p>/logos/` (F2.10, dec. 3): pendiente de hacer.

**Lo que sigue siendo *(suposición)* hasta r2-r4:**

- Que las pautas de luz del 2026-11-02 (dirección sin fuente, escena oscura al principio, posiciones en fracciones) arreglen
  el lavado de Tarkor sin estropear a los demás: lo contesta r2-luz (23 piezas, semillas 3 y 7).
- Los rangos de YAVG/SATAVG y % de paleta por proyecto son orientativos; developer y voice-generator se calibraron sin
  imagen de marca, y las portadas del Portal valen como marca solo si la persona lo dice (la de toVeriAI es casi blanca).
- Si Tarkor necesita LUT (F2.11) o basta el prompt; el LoRA `wmf-estilo` queda para F5.
- Los velos (`#f1e4d0:0.55`, `#221c16:0.45`) salen de r4-r5 del piloto con el modelo rápido; con otro modelo se vuelven a
  medir.
- El acento de Tarkor (arcilla fuera del juego, cristal dentro) es decisión delegada **[P]**, como los logos elegidos del
  README.
- Los límites orientativos de caracteres (≤ 40 titular, ≤ 70 subtítulo) salen de las piezas de r5 con Sora/Cinzel a un
  tercio de `og`; otra familia u otra zona los cambia.
- Que el borrador (`draft` a 0,5 y 4 pasos) anticipe estilo y hueco con cualquier marca: visto en 6 de 7 en r3.
