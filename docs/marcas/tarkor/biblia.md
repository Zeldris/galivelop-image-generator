# Tarkor — biblia de estilo

Marca nueva, creada desde cero (decisión de la persona, 2026-10-26): casi todo es **[P]**. Lo que no lleva marca sale del
repo del juego, World-Maker-Fantasy (WMF) `73965f62`, o del Portal `aa76b34`; rutas en la sección 10. Molde y reglas
comunes: [../README.md](../README.md).

## 1. Esencia

- **Qué es:** RPG narrativo de fantasía con IA local. Se juega en Berig, continente de Helek Sirik («Origen Azul»).
  «Tarkor» es también la última y más sabia de las 13 Semillas, que se fue y volvió «frío y oscuro» (`genesis.md`).
- **Lema:** «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas.»
- **Para quién:** quien juega rol narrativo y quiere IA en su máquina, sin cuentas; la Steam Deck es el objetivo.
- **Valores y ética:** privado por diseño (sin cuentas, telemetría ni conexión); «el motor decide, la IA narra»; mundo
  artesanal con causa física para todo; voz de difusión cercana, concreta y honesta, sin vender.
- **Nunca se muestra:** lo reservado del canon (qué sabe Tarkor, la Entidad, la luz morada, el Reino Nabierus, la
  Ciudad Hundida, el Archivo Cegado, el muro de obsidiana); luna; humanos; pólvora; Vaelira; interfaz de juego falsa;
  fechas o promesas; «AAA genérico» (destellos, cromados, armaduras brillantes). El símbolo no presenta a Tarkor como
  héroe ni como villano: como mucho insinúa la ambigüedad (fidelidad y ruptura).

## 2. Paleta

Base «madera + hierro» del juego (`index.css`, decisión nº 6); el acento es la decisión abierta de abajo.

| Rol | Hex | Uso |
|---|---|---|
| Madera 900 / 800 | `#241a10` / `#332415` | fondo de pieza oscura, tablón |
| Madera 700 / 600 / 400 | `#46311d` / `#5c4126` / `#a3814f` | veta de tablón; madera vista; wordmark en el lockup de revisión **[P]** |
| Madera 100 (hueso) | `#f1e4d0` | texto sobre oscuro; trazo del símbolo a; fondo de pieza clara **[P]** |
| Hierro | `#0e0b08` / `#171310` / `#221c16` | aros, remaches, texto sobre claro |
| Acero | `#52626f` / `#8a9aa8` | filo de remache, texto secundario |
| Arcilla (Portal) | `#E0703A` → `#8a3b1e` | acento A: baldosa de la familia, roca de los Pilares |
| Cristal (juego) | `#a8d8f0` / `#7bc4e8` / `#4aa8d8` / `#3488b8` | acento B: gema, filetes, Semilla |
| Musgo | `#8fae6a` | solo semántico (multijugador en el juego); no en marca |

- **Combinaciones:** pieza clara: hueso `#f1e4d0` + texto hierro `#221c16` + un acento; pieza oscura: madera 900
  `#241a10` + texto hueso + un acento; sobre imagen: texto hueso con banda de madera 950 `#1b130c` al 70 % **[P]**.
- **Prohibidos:** negro `#000` y blanco `#fff` puros; morado/violeta (luz reservada); neón; más de un acento por pieza;
  degradados fuera de la baldosa de la familia y la gema.
- **Decisión abierta [P]: arcilla `#E0703A` o cristal `#4aa8d8` como acento de marca.** Recomendación: **arcilla
  fuera del juego, cristal dentro.** Razones: 1) todo el arte que existe (portada y 304 `.webp`) es roca roja de las
  Llanuras, y la marca debe casar con él; 2) en la familia Galivelop el cristal `#4aa8d8` choca con el celeste del
  Portal (`#1aa6df`) y el azul del workflow; la arcilla es el único acento cálido y ya es el asignado por el Portal;
  3) arcilla, madera y hierro son una sola familia de materiales. El cristal queda como acento secundario (gema,
  noche, interfaz) y no se cambia en el juego. Si la persona elige b o c, gana el cristal y se invierte la regla.

## 3. Tipografía

- **Cinzel** (OFL, empaquetada en el juego) para títulos y wordmark: 700 en el lockup, 400 con tracking 0,3 em en
  filetes y eyebrows, como el título de la Home **[P]**.
- **Inter** 400/500 en texto; Cascadia Code en datos (solo en el juego).
- **Wordmark:** «TARKOR» en mayúsculas, Cinzel 700, tracking 0,18 em (9 px a 50 px); en el lockup, altura de la
  mayúscula ≈ 0,28 del símbolo. Reserva: `serif`.

## 4. Logo

Propuestas en `logos/`; conceptos del README. Todas se leen a 16 px (comprobado con `rsvg-convert -w 32` y `-w 16`).

| | Concepto | Nota de dibujo |
|---|---|---|
| a | **Los Pilares Rotos:** dos torres de hueso que nacen del borde de la baldosa de la familia (arcilla), unidas por un puente colgante | «en un trazo» se leía como una M; va en silueta rellena con el puente como trazo de 6 |
| b | **La gema:** el rombo `.gem` tallado en cuatro caras de cristal, con filetes `accent-hairline` a los lados | los filetes desaparecen a 16 px; la gema basta |
| c | **La Semilla:** semilla vertical partida en dos mitades que han resbalado, cristal claro y hierro, misma piel de cristal | fidelidad (una piel) y ruptura (el corte); nada morado |
| d | **Hierro y madera:** escudo de tablones con aro de hierro, cuatro remaches y una T forjada | el aro se funde con el fondo oscuro, a propósito |

**Elegido (agente, delegado):** a — los Pilares Rotos, el emblema aprobado en el plan; retocado para que no se lea
como una M (torres desiguales, la derecha quebrada a media altura, puente más largo y más bajo que sale del flanco de
la alta).

Tras elegir **[P]:** variante clara y oscura; margen libre = la altura de la «T» del wordmark; mínimo 16 px el
símbolo, 20 px de altura el wordmark; el símbolo va con el wordmark o solo en esquina o avatar, nunca estirado,
rotado ni con sombra o brillo; el texto del lockup se pasa a trazos con Cinzel.

## 5. Forma e iconografía

- **Radios:** baldosa `rx` 30/128 (familia); paneles 12 px; remaches redondos; gema con esquinas vivas.
- **Línea:** silueta rellena antes que contorno; trazos de 3,5-6/128; filetes de 1 px que se desvanecen.
- **Lenguaje:** materia tallada y forjada (madera veteada, hierro negro, hueso, cristal facetado), simetría rota a
  propósito (cimas desiguales, mitades desplazadas). Nada de 3D, brillos, destellos ni cromo.

## 6. Voz y frases

- **Tono:** épico y trágico en el mundo; cercano, concreto y honesto al contar el proyecto; una idea por mensaje.
- **Campo semántico:** mundo que sigue, Semilla, Origen Azul, madera, hierro, cristal, llanura, puente, clan, motor,
  local. Fuera: luna, magia sin causa, héroe elegido, épica de tráiler.
- **Lema:** «Un RPG narrativo donde el mundo sigue adelante aunque tú te detengas.»
- **Variaciones [P]:** «El mundo sigue aunque tú te detengas.» · «Deja la partida. El mundo sigue.»
- **Ganchos [P]:** «Lo que no hagas, lo hará otro.» · «Madera, hierro y cristal. Y un mundo que no te espera.»
- **Cierres [P]:** «Juega en local. Nadie mira.» · «En desarrollo, a la vista.»

## 7. Estilo de imagen (FLUX)

- **Sí:** paisajes de Berig sin criaturas; colores naturales y apagados con un acento por escena; gradación fílmica
  suave; huella pequeña (empalizadas, pasarelas, estandartes, tótems); madera, piel, hueso, piedra, hierro negro.
- **No:** texto, personajes, interfaz, criaturas fuera del canon, oscuridad total, cielo de otro mundo, tráiler AAA.
- **Motivos:** Pilares Rotos con puentes y estandartes (ya en la portada: no repetir en el og), Agujas Imán y crestas
  de arena imán, empalizada de troncos de Telda, obelisco goirnte, noche con estrellas y velo perlado (sin disco).
- **Vetadas** (`mundo.json`): moon/moonlit/moonlight, crystal dust, heavens, scar/wound/gash, negaciones (`no`,
  `without`...), nombres propios, humanos, pólvora.
- **Zona reservada:** un tercio izquierdo liso (og, banner, header); tercio inferior en `square` y `portrait`.
- **Qué cambiar tras el «no» de r1 [P]** (la persona no dio motivo; hipótesis, a confirmar en una ronda):
  1. El fondo repetía la portada del Portal: elegir otro motivo (Agujas Imán al amanecer o empalizada al ocaso).
  2. «Cinematic matte painting at golden hour» con cielo ámbar y carmesí es justo el AAA que la biblia veta: usar el
     preámbulo del juego («grounded... muted natural colours, subtle filmic grade, single accent colour»).
  3. La mitad izquierda vacía quedaba muerta: pedir «calm open plain in soft haze», no «nearly empty».
  4. Nada decía «el mundo sigue»: una huella mínima de vida (humo de un campamento lejano, estandartes al viento).

## 8. Prompts

| Archivo | Estado |
|---|---|
| `examples/tarkor/prompts/og.txt` | r1 (`5d0178c`): técnico sí, persona **no**; se rehace con la sección 7 |
| `examples/tarkor/prompts/r2-palabras.txt` | r2, descartada. Escena nueva por la hipótesis 1 de la sección 7 (el og repetía la portada): agujas de roca de hierro al amanecer, tercio izquierdo de llanura en calima, hilo de humo y estandarte (hipótesis 3 y 4 de propina); estilo del preámbulo del juego (hipótesis 2, lo que pide la plantilla). Paleta en palabras, acento único arcilla |
| `examples/tarkor/prompts/r2-hex.txt` | r2, **elegida** (ahora `estilo.txt`). Misma escena, colores en hex |
| `examples/tarkor/prompts/r2-material.txt` | r2, descartada. Misma escena, paleta en materiales y luz (arcilla cocida, hierro forjado, hueso, calima) |
| `examples/tarkor/prompts/estilo.txt` | og: el estilo elegido en r2 | r3: el borrador (640×320, 4 pasos, 51 s) anticipa estilo y hueco, no el detalle; r4: og compuesto, contraste peor 6.97:1, paleta 72 %; sigue lavado para el juego (YAVG 169): lo prueba r5-og-bajo |
| `examples/tarkor/prompts/r5-cuadrado.txt` | r5: generado y compuesto (`piloto/r5/tarkor/intentos/cuadrado.png`), contraste 6.28:1, peor 5.18:1, paleta 84.35 %; el más justo de r5 (sobre AA, no AAA). Misma escena en cuadrado 1080×1080 (se genera a 1024×1024): agujas y cielo en los dos tercios superiores, tercio inferior de llanura en calima libre |
| `examples/tarkor/prompts/r5-vertical.txt` | r5: generado y compuesto (`piloto/r5/tarkor/intentos/vertical.png`), contraste 7.22:1, peor 4.98:1, paleta 69.21 %; el más justo de r5 (sobre AA, no AAA). Misma escena en vertical 1080×1350 (896×1152): agujas arriba, tercio inferior de llanura libre |
| `examples/tarkor/prompts/r5-cabecera.txt` | r5: generado y compuesto (`piloto/r5/tarkor/intentos/cabecera.png`), contraste 11.39:1, peor 6.89:1, paleta 73.33 %. Misma escena en cabecera 1500×500 (1536×512): llanura en la mitad izquierda, agujas en la derecha |
| `examples/tarkor/prompts/r5-og-bajo.txt` | r5: generado y compuesto (`piloto/r5/tarkor/intentos/og-bajo.png`), contraste 9.5:1, peor 7.36:1, paleta 50.52 %; YAVG 169 → 66 frente al og de r4, pero SATAVG sigue en 5 (el juego pide 15-30). Misma escena del og (1280×640) con la luz más baja y más color (cielo #52626f, banda cálida en el horizonte, acento #E0703A fuerte), buscando YAVG 70-95 y SATAVG 15-30 (r2 dio ~155 y ~7) |

Plantilla para uno nuevo: preámbulo de `mundo.json` (día o atardecer) → encuadre con la zona reservada («the left
third is a calm, nearly plain stretch of haze») → sujeto y región con su luz (`regiones.*.luz`) → «Style: cinematic
landscape photograph, natural muted colours, subtle filmic grade. Mood: wild, quiet, lived-in.» → «The image is
completely textless.» Entre 120 y 320 palabras, sin negaciones ni comparaciones.

## 9. Formatos y piezas

Perfiles: `banner`, `og`, `social`, `square`, `header` (Discord 960×540), `avatar`, `icon`.

Primera ronda **[P]:**

1. Elegir logo y paleta (esta página).
2. og 1200×630 nuevo, desde la sección 7.
3. Banner 1600×640 del Portal y cabecera 960×540 de Discord.
4. `square` 1080×1080 con el lema.
5. Avatar 512×512 e `icon` del símbolo elegido.

## 10. Fuentes

- WMF `73965f62`: `frontend/src/index.css` l.9-14 (fuentes), l.23-54 (madera, hierro, cristal, acero, musgo),
  l.226-234 (`.accent-hairline`), l.246-254 (`.gem`), l.324-348 (`.rivet`); `frontend/src/pages/Home.tsx` l.24-31
  (título con gema y filetes); `frontend/src/assets/fonts/` (Cinzel e Inter, OFL); `docs/producto/02-decisiones.md`
  nº 6 (madera + hierro); `docs/producto/tarkor-contenido-web.md` l.40 (lema), l.66 y l.76 (motor y privacidad);
  `docs/difusion/guia-canales.md` l.3-4 (voz); `docs/canon-opencode/00-nucleo.md` «Tono prohibido»;
  `docs/rpgtarkor/lore-mundo/genesis.md` (las Semillas, arco de Tarkor, «El cielo sin luna» l.146-155);
  `docs/rpgtarkor/lore-mundo/regiones/llanuras-del-viento-rojo.md` l.376-385 (Los Pilares Rotos);
  `docs/producto/plan-imagenes/guia-visual-mundo.md` §1-2; `image-generator/estilo/mundo.json` (preámbulo, vetadas).
- Portal `aa76b34`: `src/data/proyectos/tarkor.json` l.7 (acento `#E0703A`); `public/proyectos/tarkor/portada.webp`
  (1600×640, Pilares Rotos); `public/marca/gv-logo.svg` (baldosa de la familia).
- Aquí: `docs/plan.md` «Estilos por proyecto», párrafo Tarkor (`#8a3b1e`, `#1b0f0a`, `#c98a3a`, `#efe3cf`, `#f2b34a`,
  medidos sobre la portada, *suposición*); `docs/registros/contenido/r1-fondos.md`;
  `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md` §1, §2 y §4.
