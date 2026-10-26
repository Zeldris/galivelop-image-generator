# r2 estilo (2026-10-27)

Tres maneras de decir el color en el mismo prompt de cada proyecto (`examples/<proyecto>/prompts/r2-{palabras,hex,material}.txt`,
escritos con Fable desde las biblias): con palabras, con los hex de la biblia, o con materiales y luz. `examples/pilot/ronda.sh r2`,
semilla 3. Para revisar: `piloto/r2/index.html` y `piloto/r2/hoja.png` (una fila por proyecto en orden alfabético; columnas
hex, material, palabras). Portal y Tarkor estrenan escena (umbral de luz; agujas de hierro al amanecer), por el «no» de r1.

## Ejecución

Las 21 piezas con flux2 klein 4B Q8_0, 1280×640, 6 pasos, salida 0: 174-182 s por pieza, ~63 min la ronda, mín. libre
7372 MB en la peor. Igual que r1: el estilo no cambia el coste.

## Medidas (`examples/pilot/medir.py`)

Paleta: los hex del prompt `r2-hex` del proyecto, ΔE76 < 15 (umbral sin calibrar). Contraste: zona izquierda
0,0,560,640 (la reservada al texto en el og; en toVeriAI el texto va arriba, así que su fila no dice mucho), texto blanco
y casi negro (#111111).

| Proyecto | Variante | YAVG | SATAVG | Paleta % | Contraste blanco | Contraste #111 |
|---|---|---|---|---|---|---|
| galivelop-developer | hex | 52.6 | 10.7 | 80.3 | 18.07 (peor 18.07) | 1.05 (peor 1.01) |
| galivelop-developer | material | 60.9 | 4.0 | 65.8 | 17.42 (peor 16.68) | 1.08 (peor 1.05) |
| galivelop-developer | palabras | 36.8 | 12.7 | 87.4 | 19.97 (peor 19.97) | 1.06 (peor 1.06) |
| galivelop-image-generator | hex | 53.9 | 17.4 | 69.9 | 17.98 (peor 17.41) | 1.05 (peor 1.03) |
| galivelop-image-generator | material | 54.4 | 13.6 | 76.3 | 17.16 (peor 14.28) | 1.10 (peor 1.08) |
| galivelop-image-generator | palabras | 41.7 | 15.3 | 74.8 | 19.55 (peor 19.29) | 1.04 (peor 1.02) |
| galivelop-voice-generator | hex | 56.8 | 19.1 | 74.3 | 17.33 (peor 16.78) | 1.09 (peor 1.06) |
| galivelop-voice-generator | material | 44.7 | 13.9 | 74.4 | 18.37 (peor 16.60) | 1.03 (peor 1.03) |
| galivelop-voice-generator | palabras | 46.0 | 15.8 | 75.7 | 19.39 (peor 18.93) | 1.03 (peor 1.00) |
| galivelop-workflow | hex | 42.2 | 7.2 | 96.5 | 17.86 (peor 17.06) | 1.06 (peor 1.03) |
| galivelop-workflow | material | 58.6 | 12.0 | 83.8 | 14.95 (peor 14.45) | 1.26 (peor 1.22) |
| galivelop-workflow | palabras | 35.7 | 9.1 | 96.6 | 19.10 (peor 18.60) | 1.01 (peor 1.01) |
| portal | hex | 56.9 | 15.6 | 73.5 | 19.75 (peor 19.60) | 1.05 (peor 1.04) |
| portal | material | 60.9 | 6.8 | 73.3 | 18.58 (peor 18.31) | 1.02 (peor 1.00) |
| portal | palabras | 45.9 | 13.0 | 86.4 | 20.43 (peor 20.31) | 1.08 (peor 1.08) |
| tarkor | hex | 155.2 | 6.7 | 78.5 | 1.82 (peor 1.26) | 10.36 (peor 2.41) |
| tarkor | material | 145.7 | 6.4 | 80.2 | 2.15 (peor 1.39) | 8.80 (peor 1.79) |
| tarkor | palabras | 152.3 | 8.6 | 83.7 | 1.80 (peor 1.28) | 10.50 (peor 2.92) |
| toveriai | hex | 187.2 | 13.0 | 67.2 | 1.63 (peor 1.13) | 11.58 (peor 1.70) |
| toveriai | material | 181.9 | 12.0 | 68.7 | 1.52 (peor 1.12) | 12.41 (peor 1.31) |
| toveriai | palabras | 158.8 | 19.3 | 52.4 | 2.03 (peor 1.30) | 9.30 (peor 1.00) |

## Elegida (agente, delegado)

| Proyecto | Elegida | Por qué |
|---|---|---|
| galivelop-developer | palabras | Bucle limpio a la derecha. Material le añade un brote de hojas que no está en la biblia. Hex mete un destello de más. |
| galivelop-image-generator | palabras | Marcos de cristal más a la derecha y mitad izquierda más vacía. Material refleja los marcos hacia abajo. |
| galivelop-voice-generator | palabras | Igual que hex, con más aire a la izquierda. Material ensucia el fondo con textura. |
| galivelop-workflow | palabras | Las líneas ya respetan la mitad izquierda (la palanca de r1 funcionó). Material deja una mancha. |
| portal | hex | Es la única con los tres puntos de color dentro del umbral, como pide la biblia. El resto los saca fuera o los convierte en esferas. |
| tarkor | hex | Agujas de roca creíbles y un estandarte. Material las convierte en una empalizada de pinchos. |
| toveriai | material | Bandas vino→ocre→verde más ricas, y el tercio superior libre. Palabras deja un hueco blanco en medio. |

La elegida se copia a `examples/<proyecto>/prompts/estilo.txt`, que es la entrada de r3.

## Lo que se aprende

- **Cómo se dice el color importa poco:** en las cuatro herramientas las tres variantes dan casi la misma imagen. Palabras
  sale un poco más oscura (YAVG 36-46 frente a 42-61), con más contraste para texto blanco. Los hex no mejoran el
  porcentaje de paleta de forma clara. Material sí cambia la escena: mete objetos y texturas.
- **Paleta:** 52-97 %. Con el umbral sin calibrar no sirve como aceptación. Hace falta calibrarla con las imágenes de
  marca de cada repo (D31, F2.9).
- **Tarkor, fuera del rango de su juego:** YAVG 146-155 y SATAVG 6-9, cuando la aceptación de Tarkor (`medir.sh`) es YAVG
  70-95 y SATAVG 15-30. El amanecer en calima sale lavado. Es el caso de prueba para la LUT de D31 o para una variante más
  baja de luz. Para no mezclar variables, r3 no lo toca; se prueba en r5.
- **Texto:** en los seis fondos oscuros, el blanco sobre la mitad izquierda da 15-20:1 sin velo. En Tarkor y toVeriAI el
  texto tiene que ser oscuro: en Tarkor, el peor punto de su zona baja a 1,8-2,9:1 por la llanura del pie, así que pide
  velo o ir solo en el cielo.

