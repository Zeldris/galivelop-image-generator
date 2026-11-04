# r1 fondos (2026-10-26)

El og de los siete proyectos (`examples/<proyecto>/prompts/og.txt`, versión de `5d0178c`, ya sin comparaciones) con el
`generar.sh` de Tarkor (`examples/pilot/ronda.sh r1`), semillas 3 y 4. Para revisar: `piloto/index.html` (en el repo,
fuera de git: prompt, intentos, tiempos y sí/no por proyecto) y `piloto/r1/hoja.png` (una fila por proyecto en orden
alfabético, una columna por semilla).

## Ejecución

Las 14 piezas con flux2 klein 4B Q8_0, 1280×640, 6 pasos, salida 0. Dos columnas: la ronda original con el `generar.sh`
de Tarkor (2026-10-26) y la repetición con `gimg` (F2.6, 2026-10-27: `examples/<p>/orders/r1-og.json`, `seed` 3 y
`count` 2, `gimg work` sobre los 14 intentos en cola, `master-1000-95ff762` instalado con `instalar.sh --models-from`).

| Medida | `generar.sh` | `gimg` |
|---|---|---|
| Total por pieza | 180-182 s | 179,6-189,3 s |
| Carga del modelo | — (no se midió aparte) | 12,3-21,6 s (`app.load_ms`) |
| Muestreo | 146,0-147,0 s (~24,4 s/paso) | 146,1-154,4 s (~24,3-25,7 s/paso) |
| Decodificar | 28,5-29,2 s | 28,5-28,6 s |
| Mín. libre (peor pieza) | 7305 MB (el resto, 7935-8206 MB) | 7586 MB (el resto, 7647-7996 MB) |
| Ronda entera | ~42 min | ~43 min |
| Imágenes | 14 | 14, **píxel a píxel iguales** a las de `generar.sh` (`ffmpeg -f md5`) |

Ninguna pieza se acercó al umbral del vigilante (1500 MB) ni al de arranque (7000 MB, la peor quedó a 305 MB de él).

**Comparación `gimg` frente a `generar.sh`.** Las 14 imágenes de `gimg` (`piloto/r1-gimg/<p>-og-s{3,4}.png`, copia de
`~/.local/share/gimg/projects/<p>/orders/fondos/r1/@og/attempts/q<N>.png`; hoja en `piloto/r1-gimg/hoja.png`) dan el mismo
md5 de píxeles que `piloto/r1/<p>/intentos/og-s{3,4}.png`. Los bytes de los PNG difieren solo por un bloque `tEXt` que
añade `gimg`. La orden registrada por `gimg` (`app.image.command` en `log.jsonl`) es la de `generar.sh` más
`--preview proj --preview-interval 1 --preview-path …`; no lleva `-t` porque el perfil de máquina no fija hilos. Lo que
cambia son los tiempos: el muestreo salió 0-7 s más lento en portal, toveriai, workflow y tarkor, con la carga del modelo
también más lenta en esos mismos (16-22 s frente a 12-13 s), que es lo que se espera de la caché de disco tras el episodio
de Ollama (ver abajo) y no del motor. El decodificado es idéntico (28,5 s). Mín. libre más alto porque Ollama quedó vacío.

Antes de arrancar, `gimg doctor` abortaba por Ollama (`engine.ollama: abort`): algo de Tarkor volvía a cargar
`tarkor-narrador-llama31` cada ~20 s y la memoria libre bajaba a ~1,3-2,5 GB. Se descargaron los modelos por la API
(`POST /api/generate` y `/api/embed` con `keep_alive: 0`) cuando la persona confirmó que nadie usaba nada, y Ollama se
quedó vacío (9,1 GB libres) durante toda la tanda.

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
