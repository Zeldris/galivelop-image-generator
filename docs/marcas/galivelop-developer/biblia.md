# galivelop-developer — biblia de estilo

Estado: **aprobada el 2026-11-04** (decisiones delegadas por la persona; ver
[`docs/records/decisiones-hojas-2026-11-04.md`](../../records/decisiones-hojas-2026-11-04.md) y [`hoja.md`](hoja.md)). El repo
no tiene ninguna identidad visual (ni logo, ni color, ni tipografía): es una herramienta del taller y entra en la familia del
Portal con un acento propio. Lo marcado **[P]** es propuesta del agente aprobada por delegación; lo que sale del repo va sin
marca. Fuentes en la sección 10.

## 1. Esencia

- **Qué es:** agente de programación local: Aider sobre un modelo local (Ollama), como **tercer relevo** junto a las
  sesiones de Claude Code. Python ≥ 3.10 solo stdlib; la Steam Deck es el perfil mínimo. Estado: F0 hecha, aún no
  ejecuta tareas.
- **Lema [P]:** «El tercer relevo» (del ADR 0002). Alternativa **[P]**: «Una rama acotada que vuelve revisada».
- **Para quién:** proyectos del taller que ya usan Galivelop-workflow y quieren tareas pequeñas hechas en local.
- **Valores:** IA local y compartida (un solo Ollama por máquina), nada residente, límites impuestos por scripts, cada
  tarea local pequeña y revisada entera.
- **Ética:** trabaja solo en `local/<tarea>`, nunca toca la bitácora, `main` ni `.claude/`; lo revisa Claude o la persona
  antes del merge: **el humano decide**. Ninguna pieza lo muestra autónomo.
- **Nunca se muestra:** robots, cerebros, rostros, personas, «magia» de IA, pantallas con código legible.
- **Promesas:** el repo no tiene licencia (`README.md`: «Todavía no hay licencia»): nada de «en abierto», «MIT» ni «open
  source». Nada que lo muestre ejecutando tareas, instalado o con lanzador mientras el `README` diga que F0 está hecha y «aún no
  ejecuta ninguna tarea»; nada de cifras del banco hasta que `gdev bench` exista; nada de nube ni de precios.

## 2. Paleta

Familia del Portal (fondos, textos) más un acento propio y sus dos tonos, derivados a mano del acento.

| Rol | Hex | Uso |
|---|---|---|
| Acento **[P]** | `#2BB3A3` | baldosa, rama local, anillo de revisión, nombre sobre oscuro |
| Acento oscuro **[P]** | `#157D74` | tronco y trazos principales del símbolo suelto; nombre sobre claro; extremo oscuro de la baldosa |
| Acento claro **[P]** | `#9FE3DA` | detalles sobre oscuro, resplandor |
| Fondo oscuro | `#06121c` | fondo por defecto (Portal) |
| Superficie | `#0c1d2b`, `#11283a` | tarjetas; borde `#1b3447` |
| Texto | `#eaf4fa` / `#9fb4c4` | títulos / apoyo sobre oscuro |
| Fondo claro | `#f6fafd` | piezas claras; texto `#0a1a28` |
| Blanco | `#FFFFFF` | trazo sobre la baldosa |

Combinaciones por contexto:

- **Pieza oscura (por defecto):** `#06121c` con rejilla de puntos, texto `#eaf4fa`, rama y anillo en `#2BB3A3`, línea
  principal en blanco suave.
- **Pieza clara:** `#f6fafd`, texto `#0a1a28`, estructura en `#157D74` y acento `#2BB3A3` solo en lo que destaca (el
  acento a secas no llega a 3:1 sobre claro).
- **Sobre imagen:** logo en baldosa; texto `#eaf4fa` en la mitad inferior (`abajo 1/2`) en `og`, `social` y `header`, y en la
  superior (`arriba 1/2`) en `square` y `portrait`. Velo `#06121c:0.55` en `og` (la línea de luz brillaba a la altura del
  título) y `#06121c:0.3` en el resto.
- **Prohibidos:** el acento como color de texto pequeño sobre claro; degradados fuera de la baldosa; celeste del Portal
  `#1aa6df` junto al acento (se confunden); rojo o ámbar decorativos; verde «hoja» o saturado (la rama es luz, no planta).

## 3. Tipografía

| Uso | Familia | Peso | Tracking |
|---|---|---|---|
| Títulos | Sora | 700 | -0,02 em |
| Texto | Inter | 400 (subtítulo con opacidad 0,82) | 0 |
| Órdenes (`gdev task`), rutas | DejaVu Sans Mono | 400 | 0 |
| Wordmark (lockup) | Sora | 700 | -0,03 em |

- Pesos aprobados el 2026-11-04 (lo compuesto en r4-r5, igual en toda la familia): titular 700, subtítulo Inter 400 con
  opacidad 0,82.
- Wordmark: «galivelop-developer» en minúsculas, como se llama el repo y la orden; un color (`#157D74` sobre claro,
  `#2BB3A3` o `#eaf4fa` sobre oscuro).

## 4. Logo

Propuestas en `logos/` (símbolo `galivelop-developer-<letra>.svg` y su `-lockup.svg`):

| | Concepto | A 16 px |
|---|---|---|
| a | Rama que vuelve: tronco en `#157D74`, rama corta en `#2BB3A3` que sale y vuelve a él por el anillo de revisión | sí, pero se lee como una letra «b» / «þ»; es inherente al concepto |
| b | Tercer relevo: tres trazos paralelos en diagonal; el tercero, más corto y del acento, acaba en el anillo | sí: tres rayas y un punto |
| c | Terminal: el indicador «›_» con el trazo de la familia, en la baldosa `#2BB3A3 → #157D74` | sí |
| d | Monograma «gd» en la baldosa; la «d» cierra su panza en un anillo mayor que la de la «g» | sí: baldosa con dos letras |

**Elegido (agente, delegado):** d — hace familia con «gw»; la a se lee como una «b».

Reglas tras elegir:

- **Variantes:** en baldosa (avatar, favicon, sobre imagen; a y b pasan a trazo blanco, con la rama o el tercer trazo en
  `#06121c` para que destaque) y suelto en `#157D74` + `#2BB3A3` para claro y oscuro.
- **Margen libre:** el grosor del trazo (12/128) por cada lado.
- **Tamaño mínimo:** 16 px la baldosa, 24 px el símbolo suelto, 120 px de ancho el lockup.
- **Símbolo y wordmark:** símbolo a la izquierda, nombre a 52/128 de alto, separación 28/128.
- **Prohibido:** girar, estirar, sombra o brillo, cambiar el radio (30/128), invertir los colores del tronco y la rama
  (la rama es siempre el acento), usar el símbolo como icono de «terminal» genérico fuera de la marca.

## 5. Forma e iconografía

- Baldosa `rx` 30/128; radios 18 y 10 px en interfaz, como el Portal.
- Trazo 12/128 redondo; anillos a 9/128.
- Lenguaje: una línea recta y continua (las sesiones), una rama corta que vuelve, un anillo donde se revisa; tres
  trazos paralelos para «relevos». Nada de engranajes, rayos ni chispas.

## 6. Voz y frases

- **Tono:** directo, escueto, honesto con el estado («aún no ejecuta ninguna tarea»); dice sus límites antes que sus
  promesas.
- **Campo semántico:** tercer relevo, tarea local, rama `local/`, motor, perfil de máquina, banco de velocidad y de
  calidad, convenciones, revisar, volver al tronco.
- **Lema [P]:** «El tercer relevo».
- **Variaciones [P]:** «Tareas pequeñas, en local, revisadas enteras»; «Un Ollama para toda la máquina».
- **Ganchos [P]:** «¿Qué puede hacer un modelo de 9B sin tocar tu main?»; «Sin nube, sin sudo, sin nada residente».
- **Cierres [P]:** «Vuelve al tronco cuando alguien lo ha leído»; «Lo revisa una persona. Siempre».

## 7. Estilo de imagen (FLUX)

- **Sí:** ilustración técnica abstracta sobre azul noche con rejilla de puntos; una línea recta de luz blanca suave (las
  sesiones) y, en la mitad superior, una rama corta de luz verde azulada que sale, da una vuelta cuidada y vuelve por un
  anillo brillante; trazos finos, brillo suave, fondo plano. La mitad inferior queda libre.
- **No:** personas, manos, robots, cerebros, pantallas, teclados, código legible, nubes (es local), engranajes.
- **Motivos:** rama que vuelve, tres relevos paralelos, el anillo, una consola vacía (solo la forma).
- **Palabras vetadas:** `robot`, `brain`, `cloud`, `chip`, `circuit`, `gear`, `hand`, `screen`, `like` como comparación;
  `face`, `person`, `human`, `humanoid`, `magic`, `spark`, `sparkle`, `keyboard`, `code`, `text`, `letters`, `logo` (lo que
  «Nunca se muestra» nombra y lo que se parece a texto o logo) y `leaf`, `leaves`, `foliage`, `plant` (r2 material pintó un
  brote de hojas: la rama es luz, no planta). Más negaciones (`no`, `not`, `without`, `never`) y cualquier lugar real.
- **Verbo de la rama:** «departs from the main line», no «leaves the main line» (`leaves` es también hoja y `branch` rama de
  árbol).
- **Zona reservada para texto:** `abajo 1/2` en `og`, `social` y `header` (la línea y el bucle en la mitad superior, la
  inferior vacía: lo compuesto y medido en r4-r5, donde con la mitad izquierda la línea cruzaba el título); `arriba 1/2` en
  `square` y `portrait`. Una sola zona por perfil, la misma en prompt, plantilla y medida.

## 8. Prompts

| Archivo | Estado |
|---|---|
| `examples/galivelop-developer/prompts/og.txt` | **r1: sí** (limpio pero casi vacío; la palanca de r1 para r2 fue más presencia a la derecha y la línea solo en esa mitad, `r1-fondos.md` l.61). Histórico: la línea cruzaba toda la pieza |
| `examples/galivelop-developer/prompts/r2-palabras.txt` | r2, **elegida** (ahora `estilo.txt`). Misma escena de og con la palanca de r1 (línea desde el centro a la derecha, bucle grande que llena la mitad derecha); paleta en palabras |
| `examples/galivelop-developer/prompts/r2-hex.txt` | r2, descartada. Misma escena, colores en hex |
| `examples/galivelop-developer/prompts/r2-material.txt` | r2, descartada. Misma escena, paleta en materiales y luz (pizarra pulida, luz esmerilada, vidrio de mar) |
| `examples/galivelop-developer/prompts/estilo.txt` | og: el estilo elegido en r2. r3: el borrador (640×320, 4 pasos, 51 s) anticipa estilo y hueco, no el detalle; r4: og compuesto, contraste peor 11.82:1, paleta 86 %; zona `abajo`: en la izquierda la línea de luz cruzaba el título. **Pendiente de reescribir** (no se toca aquí): línea y bucle en la mitad superior, mitad inferior libre, «departs from the main line» |
| `examples/galivelop-developer/prompts/r5-cuadrado.txt` | r5: generado y compuesto (`piloto/r5/galivelop-developer/intentos/cuadrado.png`), contraste 17.01:1, peor 16.87:1, paleta 91.27 %. Misma escena en cuadrado 1080×1080 (se genera a 1024×1024): línea y bucle en la mitad inferior, mitad superior libre |
| `examples/galivelop-developer/prompts/r5-vertical.txt` | r5: generado y compuesto (`piloto/r5/galivelop-developer/intentos/vertical.png`), contraste 16.5:1, peor 16.33:1, paleta 88.28 %. Misma escena en vertical 1080×1350 (896×1152): línea y bucle en la mitad inferior, mitad superior libre |
| `examples/galivelop-developer/prompts/r5-cabecera.txt` | r5: generado y compuesto (`piloto/r5/galivelop-developer/intentos/cabecera.png`), contraste 13.22:1, peor 9.87:1, paleta 83.05 %; zona abajo: con la izquierda la línea tocaba el final del título. Misma escena en cabecera 1500×500 (1536×512): el archivo deja libre la mitad izquierda; **pendiente de reescribir** a mitad inferior libre (`abajo 1/2`) |

Plantilla para uno nuevo:

> Wide abstract technical illustration on a deep midnight navy background with a faint grid of tiny evenly spaced dots.
> [Motivo de la sección 7 en la mitad superior, en positivo.] The lower half of the frame is a plain, empty dark
> background with only the faint grid. Style: clean minimal vector-like digital illustration, thin precise strokes, soft glow, flat dark
> background. Colours: deep midnight navy, teal, pale aqua, soft white. Mood: calm, careful, reliable. The image is completely
> textless.

## 9. Formatos y piezas

Perfiles de la tabla común: `social`, `og`, `avatar`, `icon`; `banner` solo si la persona decide presentarlo en el Portal.

Zonas y velos: `og`, `social`, `header` con `abajo 1/2`; `square`, `portrait` con `arriba 1/2`. Velo `#06121c:0.55` en `og`,
`0.3` en `square`, `portrait` y `header`. Hechas en el piloto, y declaradas ya como perfiles: `square` 1024×1024 → 1080×1080,
`portrait` 896×1152 → 1080×1350, `header` 1536×512 → 1500×500; `og` 1280×640 → 1200×630.

Primera ronda:

1. Logo elegido y avatar 512×512 [P].
2. Social preview de GitHub 1280×640.
3. og:image 1200×630.

## 10. Fuentes

| Dato | Repo y commit | Ruta |
|---|---|---|
| Qué es, estado, subcomandos, principios | galivelop-developer `8fa309c` (árbol local, rama `claude/f1-instalacion`) | `README.md` |
| Campo semántico | galivelop-developer `8fa309c` | `GLOSSARY.md` («Términos del proyecto») |
| Tercer relevo, límites por script, el humano revisa | galivelop-developer `8fa309c` | `docs/adr/0002-tercer-relevo.md`; motor compartido en `docs/adr/0001-ollama-compartido.md` |
| Ausencia de identidad visual | galivelop-developer `8fa309c` | ningún svg/png/css en el árbol |
| Familia: baldosa, fondos, textos, tipografías | Portal-Galivelop `aa76b34` | `public/marca/gv-logo.svg`, `src/components/Logo.tsx`, tema |
| Acento `#2BB3A3` y metáfora de la rama | este repo | `docs/plan.md`, «Herramientas del taller» **[P]** |
| Lectura y veredicto r1 | este repo | `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` (§3), `docs/records/contenido/r1-fondos.md` |
