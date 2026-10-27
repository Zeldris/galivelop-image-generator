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
