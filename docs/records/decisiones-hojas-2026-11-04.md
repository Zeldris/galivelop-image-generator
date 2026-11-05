# Decisiones sobre las hojas de estilo de los 5 proyectos (2026-11-04)

La persona delegó el 2026-11-04 todas las dudas de las hojas de voice-generator, developer, portal, tarkor y toveriai
(«intenta resolver tú todas las dudas de la mejor forma posible… apruebo lo que tú consideres mejor siguiendo la línea de
los proyectos»). Las decide la sesión principal con un criterio único, y con él quedan **aprobadas** las cinco hojas.

## Criterio

1. **Lo publicado manda sobre lo que está en desarrollo**, y una pieza no se adelanta a una decisión que el proyecto aún no
   ha tomado: cuando la rama de trabajo llegue a `main`, se revisa la hoja.
2. **Lo compuesto, visto y medido manda sobre lo escrito**: si la biblia dice una cosa y las piezas de r4-r5 otra, se
   corrige la biblia, salvo que la medida diga que lo hecho falla.
3. **Una sola zona de texto por perfil**, la misma en prompt, plantilla y medida.
4. **La propuesta de cada hoja** se adopta tal cual cuando no choca con 1-3.
5. Lo que toca otros repos se apunta como propuesta para ese repo; desde aquí no se modifican.

## Las cuatro que se presentaron abiertas

| # | Duda | Decisión | Por qué |
|---|---|---|---|
| 1 | Portal: identidad de `main` o la del ADR 0002 de la rama `66ec4f1` | **`main`** («Taller independiente de software», acentos `#E0703A`, `#2F7A55`, `#3D6FD9`). Al fusionarse el ADR 0002 en el Portal, se revisa la hoja (y se añade Image Generator `#8B5CF6` si lo trae) | Criterio 1 |
| 2 | Developer: zona del texto | **`abajo 1/2`** en `og`, `social` y `header`; el prompt se reescribe para dejar libre la mitad inferior; la biblia se corrige | Criterios 2 y 3: es lo compuesto y medido en r4-r5, y el fallo (línea sobre el título) se debía a que el prompt pedía otra zona |
| 3 | Tarkor: acento | **Arcilla `#E0703A` en las piezas; cristal `#4aa8d8` dentro del juego**; el icono del Instalador (concepto b, cristal) queda como propuesta a ese repo | Arcilla es el color con el que el Portal presenta a Tarkor en la familia |
| 4 | Pesos de letra (Developer y Workflow, contradicción 3) | **Lo compuesto en r4-r5: titular 700, subtítulo Inter 400 con opacidad 0,82**, en toda la familia; las biblias se corrigen | Criterio 2; además es la misma regla para los siete proyectos |

## El resto, por proyecto

Cada hoja adopta su propia propuesta en cada contradicción, con estas precisiones:

- **Voice-generator:** zona de `square` `arriba 1/2`; `#eaf4fa` y `#A62E5A` entran en `brand.palette` (salen en las piezas
  compuestas y faltaban); subtítulo recortado a ≤ 70 caracteres; el mínimo de 120 palabras pasa a aviso (cambio de
  plantilla); «shaped like» de `og.txt`/r1 se deja como histórico; citas de la biblia al día.
- **Developer:** velo 0,55 en `og` (el «0 en og» de la plantilla es un ejemplo, no una regla); `face`, `person`, `human`,
  `humanoid`, `magic`, `leaf`, `leaves`, `foliage`, `plant` (y el resto de la lista de la hoja) a vetadas; «leaves the main
  line» → «departs from the main line»; formato de la biblia §8 corregido.
- **Portal:** `galivelop-social.png` es pieza heredada que este sistema sustituye; la captura `galivelop-portal.jpg` solo
  calibra la medida; LinkedIn «no consta en el repo» y su cabecera no se hace hasta que la persona confirme el canal; zona
  la del compositor; separación del lockup la del archivo (≈ 0,19 del alto); la pieza `banner` 1600×640 sale de la
  configuración del Portal (no tiene respaldo en su biblia); trazo del logo `#EAF4FA` (la biblia) y se apunta que el Portal
  publica `#fff`.
- **Tarkor:** `header` a 1/2 (lo del prompt y la medida, no el tercio de la biblia); `square` y `portrait` piden en el prompt la mitad libre (casa con la
  caja del 48 %); `sun` vetada y `r2-luz.txt` candidato a `estilo.txt`; «rich natural colour» en vez de «natural muted
  colours» (LUT de F2.11 si no basta); fondo oscuro plano `#241a10`, velo `#221c16:0.45`; la marca se mide contra la
  portada del juego; biblia §3 corregida (el eyebrow de la Home es Inter); `header` X 1500×500 con destino, Discord y
  LinkedIn como perfiles aparte cuando haga falta; propuestas a WMF (`Palette:` de `gw-media-content`) y al Instalador
  (icono).
- **toVeriAI:** manda «toVeriAI» (los PNG «VeriNews» huérfanos, propuesta de retirarlos); rangos IMI del kit
  (0-39/40-69/70-100); símbolo con los hex del kit; `#2D6A4F` es el acento (propuesta al Portal de dejar `#2F7A55`); citas
  de la biblia a `5a7401f`; la `ShareCard` de la app recibe la hoja como fuente (propuesta: `#F7F5F2`, sin bold); piezas sin
  cifra de dimensiones o idiomas; `og:image` = pieza `og` con `summary_large_image` (propuesta al repo); lockup oscuro a 400.

## Plantilla

Se aplican los 14 cambios propuestos por las cinco hojas (que la regla de «like» no salte con `vector-like`; comprobación
11 que compare prompt, plantilla y medida; vetadas como patrón; perfiles con varios destinos; nivel `Galivelop (origen)`;
logo publicado / logo de las piezas; publicado frente a en desarrollo; la propia app como «otra pieza de marca»; «repo
privado: no comprobable»; mínimo de 120 palabras como aviso; licencia en «Promesas»; velo por perfil como ejemplo;
`<use>`/`id` con prefijo en el SVG).
