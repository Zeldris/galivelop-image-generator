# r4 composición y medida (2026-10-27)

La pieza og (1200×630) de cada proyecto: el definitivo de r3 (`estilo-1280x640-p8-s3`) recortado a cover, con velo,
lockup, título y subtítulo de `examples/<proyecto>/piezas.json` (los escribió Fable desde las biblias), compuesto en SVG
y rasterizado con `rsvg-convert` (prueba de concepto de `gimg compose`, D28) y medido (D31).
`python3 examples/pilot/piezas.py r4`. Para revisar: `piloto/r4/<proyecto>/intentos/og.png` (con su SVG en `svg/` y sus
medidas en `medidas/og.json`) y la página `piloto/index.html`. Sin generar nada: ~2 s por pieza.

## Medidas

Contraste WCAG entre el color del texto y la caja de la zona (`componer.caja_zona`) del fondo **con velo y sin el
texto** (si no, el propio texto sube la media). Paleta, YAVG y SATAVG, de la pieza terminada.

| Proyecto | Zona | Texto | Velo | Contraste medio | Peor (p10/p90) | Paleta % | YAVG / SATAVG |
|---|---|---|---|---|---|---|---|
| portal | izquierda | #eaf4fa | #06121c:0 | 17.04 | 15.78 | 66.95 | 64.85 / 14.4 |
| toveriai | arriba | #1A1A1A | #F7F5F2:0.35 | 15.5 | 15.0 | 66.95 | 186.52 / 10.18 |
| galivelop-workflow | izquierda | #eef6fb | #0d1b2a:0 | 16.64 | 15.86 | 93.38 | 43.02 / 9.27 |
| tarkor | izquierda | #221c16 | #f1e4d0:0.55 | 11.26 | 6.97 | 72.32 | 168.91 / 7.79 |
| galivelop-image-generator | izquierda | #eaf4fa | #06121c:0 | 17.08 | 16.49 | 72.36 | 47.9 / 15.17 |
| galivelop-voice-generator | izquierda | #eaf4fa | #06121c:0 | 16.97 | 16.34 | 70.22 | 52.6 / 16.02 |
| galivelop-developer | abajo | #eaf4fa | #06121c:0.55 | 14.56 | 11.82 | 85.7 | 36.94 / 10.43 |

Todas pasan con holgura el 4,5:1 de WCAG AA (y el 7:1 de AAA salvo el peor punto de Tarkor, 6,97). Los fondos de r2-r3
ya se pidieron con la zona libre, así que el velo casi no hace falta en los oscuros.

## Lo que salió mal en la primera pasada y se arregló

1. **Lockups ilegibles en los nombres largos.** El logo medía `min(0,15·alto, 0,4·ancho de columna·lh/lw)`: un lockup
   de 1100×128 (image-generator, voice-generator) salía a ~24 px de alto y el nombre no se leía; workflow y developer
   (760-770 de ancho), a ~34 px. Ahora todos van a la misma altura, el 9 % del alto (57 px en el og, lo que ya tenía
   portal), y solo bajan si no caben a lo ancho de la columna (`componer.construir_svg`, test
   `test_lockup_ancho_sale_a_la_altura_comun`).
2. **La línea de luz de developer cruzaba el título** (zona izquierda, sin velo). La medida **no lo vio**: peor 16,72,
   porque la línea ocupa menos del 10 % de la caja y el p90 la ignora. Un velo de 0,55 no bastó (la línea sigue
   brillando a la altura del título); con la zona «abajo» el texto queda bajo la línea, limpio (peor 11,82).

## Conclusiones para F2 (D28, D31)

1. La composición en SVG + `rsvg-convert` da piezas listas en ~2 s y sin tocar la imagen generada: se puede recomponer
   (otro texto, otra zona) sin volver a generar, que es lo que propone D28.
2. **La medida de contraste por percentiles no ve líneas finas que cruzan el texto.** Para F2.9: medir también el
   contraste en la caja real de cada línea de texto (no la zona entera) y un percentil alto (p99) o la densidad de
   bordes, que es lo que delata un trazo brillante.
3. **La zona conviene elegirla según el fondo**, no fijarla en la plantilla: `gimg compose` podría proponer la zona con
   más hueco (menos bordes) entre las permitidas por el perfil, y la interfaz enseñarla.
4. Tarkor tiene un contraste suficiente sobre fondo claro, pero el fondo sigue lavado para el juego (YAVG 169): r5 prueba
   un og más bajo de luz (`r5-og-bajo`).

## Con gimg (F2.10, 2026-11-04)

Cadena real de F2.8 sobre los elegidos de r2 (`r2-hojas.md`), solo los cinco proyectos activos (voice-generator y
developer fuera). Configuración de E4: `examples/<p>/plantillas/og.svg` (zona de la hoja, caja en `data-caja`),
`logos/<lockup>.svg` (copia idéntica, la comprueba `test_examples.py`), `compose` en el perfil `og` y el texto en
`examples/<p>/textos/og.json` (campos `title1`, `title2`, `subtitle`, `subtitle2`: sin `wrap`, los subtítulos de 52-70
caracteres no caben en una línea). Fuentes OFL instaladas en `~/.local/share/fonts/galivelop/` (y en la carpeta de datos
del sandbox de VS Code, que es la que ve fontconfig ahí).

Orden: `gimg compose <p> estilo/<pedido> og <n> --text CAMPO=TEXTO…` (el número es el del intento dentro del pedido, no el
`q` de la cola), `gimg choose` (entrega en `examples/<p>/entrega/`, fuera de git) y
`gimg --json measure --project <p> --zone <data-caja> --text <color>` sobre la compuesta. Hoja de contactos:
`piloto/r4-gimg/elegidos.png` (fuera de git).

| Proyecto | Intento | Zona | Paleta % | Contraste media / peor 10 % | A ojo |
|---|---|---|---|---|---|
| tarkor | q18 (#1) | izquierda 1/3, velo `#221c16:0.45` | 66,2 | 7,0 / 5,1 | legible; titular pequeño (Cinzel 27 px: la zona de 1/3 no da más) |
| toveriai | q20 (#1) | arriba 1/3, velo `#F7F5F2:0.35` | 74,3 | 15,6 / 15,7 | limpio; lockup (34 px) y titular (40 px) modestos para la franja |
| portal | q23 (#1) | izquierda 55 % | 73,9 | 10,3 / 17,6 | bien |
| galivelop-image-generator | q29 (#1) | izquierda 1/2 | 79,1 | 10,6 / 17,8 | bien |
| galivelop-workflow | q37 (#2) | izquierda 1/2 | 94,0 | 10,4 / 18,3 | bien |

Las cinco pasan ≥ 4,5:1 en el peor 10 % (la media baja porque la caja incluye el propio texto). **Cierre:** pendiente de la
persona («sí» por proyecto si la da por publicable). Ajustes propuestos para la próxima vuelta: Tarkor, titular en tres
líneas o zona 2/5 (choca con el 1/3 de la hoja); toVeriAI, lockup y titular más grandes dentro de la franja.
