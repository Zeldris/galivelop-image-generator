# Biblia de estilo: Galivelop Evaluator (GVE)

Todo lo que hace falta para crear una pieza de GVE sin volver a leer su repo. **Borrador del 2026-11-15, sin
aprobar.** GVE es un producto de la familia Galivelop: hereda del Portal papel, tinta, tipografías, lockup común y
estilo de imagen; lo único propio es el acento y el motivo. El detalle, los ratios y los prompts completos están en
[`hoja.md`](hoja.md); ante cualquier diferencia manda la sección «Familia Galivelop» de
[`../portal/hoja.md`](../portal/hoja.md). Estados como en [`../README.md`](../README.md): sin marca sale del repo
(`galivelop-evaluator`, `origin/ccr-4fe19114-typsl9`, `2e2dc15`); **[P]** es propuesta; *(suposición)* se comprueba en
una ronda.

## 1. Esencia

- **Qué es:** un evaluador que mide sistemas de IA (texto, imagen y voz; modelos locales y por API) con **evidencia
  trazable**: cada resultado se rastrea hasta su configuración exacta, y un dato ausente nunca cuenta como éxito.
  Compara corridas, propone correcciones verificadas y las publica con su antes y después
  (`docs/discovery/vision-v0.2.md` l.8-13).
- **Lema [P]:** «Medir, corregir y demostrar» (`vision-v0.2.md` l.16, donde es la posición del proyecto).
- **Para quién:** primero, los proyectos propios, que hacen de laboratorio (hoy, el RAG de Tarkor); después, quien
  quiera mejoras con evidencia.
- **Valores:** trazabilidad, honestidad con lo que falta, reproducibilidad; el front no calcula, solo pinta lo que da
  una orden de `gve` (`docs/design/F-front.md`, regla 1).
- **Nunca se muestra:** cifras o porcentajes dentro de una imagen, podios, medallas, estrellas, notas, «ganadores»,
  gráficas de crecimiento, jueces, balanzas de justicia, batas, probetas, lupas, robots, cerebros, personas, manos,
  rostros. Ninguna pieza afirma un resultado.

## 2. Paleta

| Rol | Hex | Uso |
|---|---|---|
| Papel | `#fbfcfd` (oscuro `#0d171e`) | Fondo; heredado |
| Tinta | `#13212b` (oscuro `#e6eef3`) | Línea y texto; heredado |
| Cerúleo | `#0072a8` (y sus tonos en grabados) | El mar; la tinta de color de la familia; heredado |
| **Acento vivo, «verde nivel»** | `#b4c424` | Marca, tinte (12 % / 18 %), foco y enlaces en tema oscuro, el toque en imagen. **Elegido por el agente (delegado)** |
| **Acento hondo** | `#6f7a05` | Bloques con texto blanco, enlaces, foco y puntos en tema claro, cuadrado del logo, icono. Calculado |
| **Variante oscura** | `#b4c424` | Es el vivo: 9,38:1 sobre `#0d171e`. Calculado |

- **Por qué este acento:** es el amarillo verdoso del líquido de un nivel de burbuja, el instrumento que dice si algo
  está donde debe; y su tono (115,7° en OKLCH) cae en el centro del mayor hueco de la rueda entre los hermanos: a 71°
  de Tarkor, 73° de developer, 113° de voice, 147° de workflow y 176° de GVIG.
- **Cálculo:** `python3 docs/marcas/galivelop-evaluator/tonos.py '#B4C424'` ([`tonos.py`](tonos.py)); ratios en la
  hoja.
- **Pieza clara:** papel + tinta + bloque del hondo con blanco encima (4,71:1). **Pieza oscura:** `#0d171e` + líneas
  `#e6eef3` + el vivo. **Sobre imagen:** texto blanco sobre velo plano de tinta al 62-78 %.
- **En imagen generada:** cerúleo, papel y tinta; el acento, solo «a touch of», en el lugar del alga del Portal.
- **Prohibidos:** el acento como color dominante de una pieza o como color de resultado («sube», «aprobado»); el vivo
  como texto o trazo sobre papel claro (1,88:1); texto de acento sobre banda alterna o sobre el tinte (4,32 y 4,25);
  degradados, resplandores, cualquier color fuera de las tintas.

## 3. Tipografía

Heredada sin cambio: **Big Shoulders Display** 800/700 en mayúsculas (títulos y wordmark, tracking 0,01 em),
**Literata** 400/600 (texto), **JetBrains Mono** 500 (datos y etiquetas, tracking 0,06 em). El front de GVE ya las
declara (`front/v2/estilos/tokens.css` l.54-57) y añade una de sistema para la interfaz. Ninguna imagen lleva texto.

## 4. Logo

- **No hay ninguno.** No se dibuja a mano: todo nace de `gimg`.
- **Símbolo [P]:** monograma «GVE» en papel `#fbfcfd` sobre el cuadrado plano del hondo `#6f7a05`, con chaflán de
  28/128 arriba a la derecha (`gimg brand wordmark` + `gimg brand square`).
- **Icono de proyecto [P]:** el dial de medida (media corona con marcas, aguja y eje hueco); alternativa, el nivel de
  burbuja. Línea simple, una tinta, generado sobre croma magenta y vectorizado con `gimg brand trace` en el mismo paso
  que la aprobación.
- **Lockup:** el común de la familia: símbolo + «GALIVELOP EVALUATOR» en Big Shoulders Display 800, de
  `gimg brand lockup` (horizontal: letras a 0,45 `S`, hueco y margen 0,25 `S`; vertical: nombre a 1,6 `S`). Nombre en
  tinta, nunca en el acento.
- **Mínimos:** `S` ≥ 32 px en horizontal, ≥ 48 px en vertical; por debajo, el símbolo solo hasta 16 px.
- **Prohibido:** degradado, sombra, redondeo, estirar, rotar, monograma en tinta oscura sobre el hondo.

## 5. Forma e iconografía

Heredado: chaflán de 45° arriba a la derecha (28 / 14 / 10 px), radios 0, una sola sombra, retícula de 24 px. Iconos
de línea simple: un grosor, remates redondos, sin relleno, **nodos e interiores huecos**, legibles a 24 px, en
`currentColor`. La serie de paneles del front (resumen, corridas, corrida, comparar, curva, mejoras, informes, agentes,
traslados, eventos) se usa entera, sin mezclarla con lucide.

## 6. Voz y frases

- **Tono *(suposición)*:** sobrio, exacto, comprobable; dice lo que falta. No triunfal, no vende.
- **Campo semántico:** corrida, caso, lote de trabajo y de reserva, registro de evidencia, base, causa, mejora
  demostrada, traslado (`GLOSSARY.md` l.31-48); sonda, medida, marca. **Fuera:** magia, ranking, ganador, nota, examen.
- **Frases [P]:** «Medir, corregir y demostrar.» · «Un dato ausente nunca cuenta como éxito.» · «Antes y después, con
  evidencia.» · «Cada resultado, hasta su configuración exacta.»

## 7. Estilo de imagen (para gimg)

- **Dos registros, los del Portal:** grabado de carta náutica a dos tintas para lo grande; línea simple para iconos.
  No se mezclan. Z-Image (`zimage-turbo-q6`, 8 pasos, cfg 1.0) para calidad; FLUX para bocetos y para fijar una
  composición.
- **El mar pone el dónde; la medida, el qué.** Tres formas del motivo:
  1. **Regla de mareas** sobre el mar grabado: un listón graduado que sale del agua, con marcas **sin cifras** y un
     banderín pequeño del acento (portada, `og`, cabecera). **[P]**: es un objeto de mar y lo decide la persona.
  2. **Sondas** en grabado sobre papel: el perfil del fondo y varias líneas que bajan desde la superficie, cada una
     con su pesa; una pesa lleva el acento (tarjeta). Los puntos de sonda, en fondos y patrones.
  3. **Dial de medida** en línea simple (icono) y en grabado sobre papel (estado vacío).
- **Sí:** agua en calma, isobatas, puntos de sonda, marcas regulares, zonas limpias dichas en positivo.
- **No:** cifras, gráficas, podios, personas, resplandores, cielo ni horizonte, marcos.
- **Palabras vetadas:** `graph`, `bar chart`, `growth`, `trophy`, `medal`, `podium`, `stars`, `score`, `percent`,
  `thumbs up`, `exam`, `teacher`, `judge`, `gavel`, `scales of justice`, `robot`, `brain`, `magnifying glass`,
  `microscope`, `lab coat`, `test tube`, `person`, `hand`, `face`, `transparent`, `exactly`, `sky blue`.
- **Croma de recorte:** siempre magenta `#ff00ff` (el acento es verdoso). **Zona para el texto de la web:** `og`,
  tercio izquierdo; portada, mitad izquierda; cabecera, tres cuartos izquierdos; tarjeta, tercio inferior.
- **Si salen cifras en la regla:** boceto FLUX limpio y Z-Image en img2img sobre él (`strength` 0,5).

## 8. Prompts

Ninguno aprobado (no hay ronda). Los propuestos, completos y listos para encolar, están en `hoja.md`, «Recursos».
Plantilla para uno nuevo:

```
[sujeto y dónde está, con el motivo de medida] [zona limpia, en positivo] [bloque del registro: MAR, PAPEL o LÍNEA,
literal] No photographic rendering, no glow, no gradient, no text, no letters, no numbers, no digits, no watermark,
full-bleed edge to edge, no border, no frame. Palette strictly limited to medium cerulean ocean blue #0072a8 and its
tints and shades, off-white #fbfcfd, ink grey #13212b and a touch of chartreuse yellow-green #b4c424 on <la forma> only.
```

## 9. Formatos y piezas

Perfiles del Portal (`examples/portal/galivelop-images.json`); los pedidos se encolan en el proyecto `portal` con
clave `marca/…`.

| Pieza | Id | Perfil | Destino |
|---|---|---|---|
| Icono de proyecto (dial / nivel) | `23b-icono-gve-a`, `-b` | `icono` | 512×512 |
| Símbolo y lockup | sin generar (`gimg brand`) | — | SVG |
| Portada en el Portal | `33-portada-gve` | `portada` | 1600×900 |
| `og` (y tarjeta social de GitHub, por `gimg export`) | `24-og-gve` | `social` | 1200×630 (1280×640) |
| Tarjeta «Próximamente» | `15-proximamente-gve` | `tarjeta` | 1200×675 |
| Cabecera | `16-cabecera-gve` | `cabecera` | 1600×500 |
| Fondo de sección | `11-fondo-gve` | `fondo` | 1200×1200 |
| Patrón sin costura | `21-patron-gve` | `patron` | 1200×300 |
| Estado vacío del front | `27-estado-vacio-gve` | `formulario` | 800×600 |
| Iconos de panel (diez) | `25a`…`25j-icono-gve-*` | `cuadrado` | 1024×1024 → SVG |

**Primera ronda:** icono, `og`, portada; después símbolo y lockup, y los iconos de panel.

## 10. Fuentes

- galivelop-evaluator `2e2dc15` (`origin/ccr-4fe19114-typsl9`): `GLOSSARY.md` l.31-48; `docs/discovery/vision-v0.2.md`
  l.8-16; `docs/design/F-front.md`; `docs/roadmap.md`; `front/v2/estilos/tokens.css`.
- Portal, por su hoja: `docs/marcas/portal/hoja.md` l.42-121 y l.261-425 (este repo `5089629`).
- Método del acento: `docs/marcas/galivelop-voice-generator/tonos.py`, copiado en [`tonos.py`](tonos.py).
- Prompts hermanos: `examples/portal/orders/marca/` (`23b-*`, `24-og-tarkor`, `15v-portada-voz`, `31d-*`, `32h-*`).
