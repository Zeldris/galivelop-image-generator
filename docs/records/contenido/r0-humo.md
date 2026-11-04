# r0 humo (2026-10-26)

El og del Portal (`examples/portal/prompts/og.txt`, versión de `beb3970`) con el `generar.sh` de Tarkor
(`examples/pilot/ronda.sh r0`).

## Ejecución

| Proyecto | Clave | Modelo | Tamaño | Semilla | Pasos | Total | Muestreo | Decodificar | Mín. libre | Resultado |
|---|---|---|---|---|---|---|---|---|---|---|
| portal | og-s3 | flux2 klein 4B Q8_0 | 1280×640 | 3 | 6 | 184 s | 149,6 s (~24,5 s/paso) | 28,7 s | 8141 MB | OK, salida 0 |

## Lo que se vio

- **Funciona:** la mitad izquierda queda limpia, la rejilla de puntos está bien y el resplandor celeste también, sobre el
  azul noche.
- **Falla porque el modelo pinta lo que se nombra, también en una comparación:**
  - «like distant lanterns» dibujó un farolillo literal.
  - «caustic» salió como rayos.
- **Arreglo antes de r1:** se quitan todas las comparaciones de los prompts, no solo de este: «lanterns», «caustic», «art
  magazine», «relay» y «fingerprint».
  - Es la regla de las palabras vetadas de Tarkor, ampliada: **nada de «like …»**, se describe la cosa directamente.

## Datos para F2

- **Progreso**, en el log de `-v`: líneas `|========>   | 1/6 -  27.46s/it - ETA 02:17`, separadas por `\x1b[K` y mezcladas
  con `[V] loading …`. Sale por paso y con s/it.
- **Tiempos:** `sampling completed, taking 149.61s` y `decode_first_stage completed, taking 28.69s`, como en Tarkor.
- **Carpeta de datos:** VS Code en flatpak fija `XDG_DATA_HOME=~/.var/app/com.visualstudio.code/data`, así que la salida fue
  a `~/.var/app/com.visualstudio.code/data/gimg/pilot/` y no a `~/.local/share/gimg/`. Apuntado en «Pendiente».

## Veredicto

Técnico: sí. Estético: pendiente de la persona; va en r1 con el prompt arreglado.
