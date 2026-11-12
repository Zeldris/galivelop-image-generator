# Entrega de marca a galivelop-voice-generator (2026-11-12)

Para la sesión del repo `galivelop-voice-generator`. Desde `galivelop-image-generator` ese repo solo se lee: aquí se
dice **qué hay, qué crear allí y qué se le puede generar**; el cambio lo hace su sesión. Leído en `main` `5f67bd4`
(2026-11-11, «F1: núcleo de gvoice (#4)»). En ese commit el repo no tiene nada visual: ningún `.css`, `.html`, `.svg`
ni imagen (`git ls-tree -r --name-only origin/main`), ni logo, ni licencia (`README.md` l.70). F1 no cambia eso: es
código de `gvoice/`, tests y documentación (`git diff --stat ab1ff10 origin/main`).

Los ratios son WCAG 2.x calculados sobre los hex con
[`docs/marcas/galivelop-voice-generator/tonos.py`](../../marcas/galivelop-voice-generator/tonos.py), no medidos en
pantalla.

## Qué leer de aquí

| Qué | Dónde | Para qué |
|---|---|---|
| La hoja de voice | [`docs/marcas/galivelop-voice-generator/hoja.md`](../../marcas/galivelop-voice-generator/hoja.md), bloques «Identidad vigente», «Interfaz: tokens y reglas», «Recursos» y «Familia Galivelop» | Lo propio de voice: acento, motivo, vetos, estado de cada pieza. Las secciones 0-15 son histórico; de ellas valen la 1 (propósito, tono, vocabulario) y la 2 (ética) |
| La hoja del Portal | [`docs/marcas/portal/hoja.md`](../../marcas/portal/hoja.md), «Interfaz del Portal: tokens y reglas» (l.121-183) y «Familia Galivelop: lo que heredan los productos» (l.228-374) | Todo lo heredado: papel, tinta, filete, retícula, tipografías, chaflanes, las once reglas de interfaz, el lockup común y lo prohibido en la familia |
| El cálculo de los tonos | `python3 docs/marcas/galivelop-voice-generator/tonos.py '#D9467A'` (solo stdlib) | Reproduce los tres hex y sus ratios; con otro hex vivo, los recalcula |

En una frase: **voice es el Portal con el frambuesa donde el Portal pone el alga**. Papel, tinta y tipografías no
cambian ni un valor (decisión de la persona, 2026-11-12, `docs/marcas/portal/hoja.md` l.355-357).

## Qué crear en su repo

| # | Qué | Cuándo | Contenido |
|---|---|---|---|
| 1 | `docs/marca.md` | Ya (es contenido, no código) | Una página que **remite aquí** y no copia valores heredados: 1) fuente de verdad: las dos hojas de arriba, con el commit de `galivelop-image-generator` que traiga esta entrega; 2) los tres hex del acento y para qué sirve cada uno (tabla de abajo); 3) el motivo («la onda como dato») y lo que nunca se muestra (micrófonos, cascos, bocas, rostros, personas, nada que sugiera clonar una voz); 4) estado de las piezas (tabla «Qué se le puede generar»); 5) la regla: ningún gráfico se dibuja a mano, todo nace de `gimg` |
| 2 | Tokens de interfaz | Cuando empiece F5 (`docs/plan.md` l.45 de su repo), no antes | Los del Portal copiados tal cual (`docs/marcas/portal/hoja.md` l.127-152) más los cuatro del acento de la tabla de abajo. Los nombres de los tokens del acento los fija su repo; los valores, no |
| 3 | Comprobación de las reglas | Con los tokens | Un test como `src/estilos/marca.test.ts` del Portal: sin `-gradient(`, `blur(`, `backdrop-filter`, `drop-shadow(` ni `border-radius` distinto de 0 (salvo el punto de estado). En un repo de solo stdlib, un test de `unittest` que lea el CSS |
| 4 | Logos SVG | **Cuando exista el símbolo nuevo**, no hoy | Se copian desde `docs/marcas/galivelop-voice-generator/logos/` de este repo. **Hoy esa carpeta solo tiene los anteriores** (`galivelop-voice-generator-{a,b,c,d}.svg` y sus `-lockup.svg`: baldosa redondeada con degradado, nombre en Sora), que no cumplen la regla de la familia. Recomendación: no copiarlos; si hace falta un icono antes, `galivelop-voice-generator-a.svg` como provisional y dicho como tal en `docs/marca.md` |
| 5 | Nota de `gw-media-content` | Cuando actualice el flujo (hoy v0.3.0, `.claude/gw.json`; la skill llega después) | `.claude/gw/gw-media-content.md` con `Palette:` `--background: #fbfcfd; --surface: #ffffff; --border: #b9cbd6; --text: #13212b; --muted: #4a5c69; --accent: #ce3c71; --accent-text: #ffffff` y `--font: "Big Shoulders Display", Literata, "JetBrains Mono"`. Sustituye a la nota de la sección 11 del histórico (azul noche, Sora) |

**Los tokens del acento** (todo lo demás, heredado):

| Token (nombre propuesto) | Claro | Oscuro | Uso | Contraste |
|---|---|---|---|---|
| `--acento` | `#d9467a` | `#d9467a` | Foco (`outline` 2 px), punto de estado, marca. **Sin texto encima** | sobre papel 4,00 / 4,41; tinta encima 3,99; blanco encima 4,11 |
| `--acento-hondo` | `#ce3c71` | `#ce3c71` | Bloques grandes con texto blanco, cuadrado del logo, texto de acento y enlaces en claro | sobre `#fbfcfd` 4,53; blanco encima 4,66 |
| `--enlace` | `#ce3c71` | `#db487b` | Enlaces y texto de acento | 4,53 sobre `#fbfcfd`; 4,51 sobre `#0d171e` (4,17 sobre la superficie oscura `#111f29`: ahí, subrayado o tinta) |
| `--tinte` | `#d9467a` al 12 % | al 18 % | Hover, chips, píldoras | tinta encima 13,67 / 13,03 |

Dos avisos para cuando haya pantalla: `--peligro` (`#a3135f`, heredado) está a 7° de tono del acento, así que el fallo
va **siempre con ✗ y texto**, nunca solo color; y la toma elegida se marca con forma (visto, subrayado), no solo con el
acento.

## Qué se le puede generar

Todo sale de `gimg` en este repo (Z-Image, 8 pasos; unos 10 min por imagen en la Deck). Los prompts propuestos están en
la hoja, «Recursos».

| Pieza | Estado | Qué falta |
|---|---|---|
| Tarjeta «Próximamente» (la onda como perfil del fondo marino) | **Hecha y publicada en el Portal** (q331; `public/proyectos/galivelop-voice-generator/proxima.webp`) | Nada |
| Símbolo del logo: cuadrado plano `#ce3c71` con chaflán de 28/128 y la onda que se enrosca, trazo 12/128 | Pendiente | Generar el trazo sobre croma y vectorizarlo (`gimg brand trace`). `gimg brand` no tiene todavía una orden que monte el cuadrado con chaflán: es trabajo de este repo |
| Lockup común (símbolo + «GALIVELOP VOICE GENERATOR» en Big Shoulders Display 800), horizontal y vertical | Pendiente | El símbolo y la fuente; las órdenes están en la hoja |
| Icono de proyecto, línea simple (ventana con fila de barras) | Pendiente | Generar; sustituiría al `"icono": "audio"` genérico de la ficha del Portal |
| `og` / tarjeta social del repo (1280×640 y 1200×630), sin texto | Pendiente | Generar |
| Iconos de la interfaz (tomas, huella, cola, efectos, ficha) | No pedidos | **Que su sesión mande la lista** cuando diseñe F5: se hacen como serie entera, de una tinta, sin mezclar con otra librería |

## Pendiente de la persona

Detalle y recomendación de cada una en la hoja, «Dudas que decide la persona».

1. **El hex vivo:** aquí `#D9467A`; el Portal publica `#C9467A` (`src/data/productos/galivelop-voice-generator.json`
   l.5, `6574c4f`). Con el segundo, hondo `#c74479` y oscura `#d35083`. Recomendación: `#D9467A` y que el Portal cambie
   su línea. **Hasta que decida, su repo no fija los tokens en código.**
2. Qué tono va en la imagen generada (recomendación: el vivo).
3. Sobre el vivo no cabe texto a 4,5:1 ni en tinta ni en blanco (recomendación: no poner texto encima).
4. Acento y peligro se parecen (recomendación: mantener el peligro heredado, siempre con ✗ y texto).
5. Nombre del lockup en mayúsculas y sin guiones (recomendación: sí; con guiones, solo en código y texto).
6. Las piezas con título de r4-r5 quedan como históricas (recomendación: sí, no se rehacen).
