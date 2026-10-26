# r1 fondos (2026-10-26)

El og de los siete proyectos (`examples/<proyecto>/prompts/og.txt`, versión de `5d0178c`, ya sin comparaciones) con el
`generar.sh` de Tarkor (`examples/pilot/ronda.sh r1`), semillas 3 y 4. Para revisar: `piloto/index.html` (en el repo,
fuera de git: prompt, intentos, tiempos y sí/no por proyecto) y `piloto/r1/hoja.png` (una fila por proyecto en orden
alfabético, una columna por semilla).

## Ejecución

Las 14 piezas con flux2 klein 4B Q8_0, 1280×640, 6 pasos, salida 0.

| Medida | Valor |
|---|---|
| Total por pieza | 180-182 s |
| Muestreo | 146,0-147,0 s (~24,4 s/paso) |
| Decodificar | 28,5-29,2 s |
| Mín. libre (peor pieza) | 7305 MB (el resto, 7935-8206 MB) |
| Ronda entera | ~42 min |

Ninguna pieza se acercó al umbral del vigilante (1500 MB) ni al de arranque (7000 MB, la peor quedó a 305 MB de él).

## Lo que se vio

| Proyecto | s3 | s4 | Lo que se ve |
|---|---|---|---|
| galivelop-developer | sí | sí | Una línea fina con un anillo verde: limpio pero casi vacío; la línea cruza la mitad izquierda. |
| galivelop-image-generator | sí | sí | Marcos de cristal violeta en fila, a la derecha; mitad izquierda limpia. De las mejores. |
| galivelop-voice-generator | sí | sí | Onda rosa y anillos concéntricos, a la derecha; en s4 una estela entra hacia el centro. Bien. |
| galivelop-workflow | sí | sí | Las líneas invaden la mitad izquierda y «capsule» salió como una píldora. No vale tal cual. |
| portal | no | no | Orbe celeste con puntos de colores: limpio pero genérico, no dice «portal». |
| tarkor | no | no | Pilares de piedra con puentes de cuerda al atardecer, polvo; cielo libre a la izquierda. s4 más épica. |
| toveriai | sí | sí | Bandas de acuarela vino→ocre→verde sobre papel, tercio superior libre. El vino tira a magenta. |

Veredicto de la persona (2026-10-26), por proyecto y no por semilla: sí a todos menos portal y tarkor. Workflow pasa
pese a la nota de arriba.

## Palancas para r2 (una por proyecto, misma semilla)

- **galivelop-workflow:** decir que la mitad izquierda es fondo liso y vacío, y cambiar «capsule» por lo que se quiere
  ver (sin nombrar la píldora).
- **portal:** sustituir el orbe por un motivo propio del Portal (puerta, umbral o anillo de acceso).
- **toveriai:** nombrar el rojo vino con más peso («deep burgundy», «oxblood») y quitar lo que lo acerque al rosa.
- **galivelop-developer:** más presencia en la mitad derecha y la línea solo a la derecha.
- El resto, según el veredicto de la persona.

## Veredicto

Técnico: sí, 14/14 con tiempos estables. Estético: sí a cinco proyectos; no a portal y tarkor.

Antes de r2, la persona pide una biblia de estilo por proyecto (con el kit visual de toVeriAI como molde) y propuestas
de logo: los fondos de portal y tarkor se rehacen desde su biblia.
