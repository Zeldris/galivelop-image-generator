# r2 con las hojas aprobadas (2026-11-04)

Primera ronda con las siete hojas aprobadas (`docs/records/decisiones-hojas-2026-11-04.md`), por la cola de `gimg`
(`order submit` + `attempt new`, perfil `og`, sin borrador) y `gimg work`. Pedidos: `estilo/r2-control` (prompt
`estilo.txt`, semilla 7) y `estilo/r2-luz` (`r2-luz.txt`, semilla 3) de cada proyecto; Tarkor con `r2-luz` y
`r2-luz-r1` en vez de control (#15 cancelada). **Voice-generator y developer fuera** hasta que la persona los retome
(canceladas #32-#34 y #38-#40).

Para revisar: `piloto/r2-hojas/<proyecto>.png` (hojas de contactos de `gimg sheet`, 2 columnas; ignoradas por git; se
rehacen con `gimg sheet --out … --columns 2 --width 560` sobre
`~/.local/share/gimg/projects/<p>/orders/estilo/<pedido>/@og/attempts/q<N>.raw.png`).

## Medidas (`gimg --json measure --project <p> --zone <zona de la hoja> --text #hex`)

Paleta: `brand.palette` del proyecto, ΔE 15. Contraste: la zona de texto del `og` de cada hoja, con el color de texto de
la hoja; media / peor 10 %.

| Proyecto | Pedido | Intento | Y | S | Paleta % | Contraste |
|---|---|---|---|---|---|---|
| tarkor | r2-luz | q16 | 144,7 | 9,3 | 75,3 | 6,95 / 1,06 |
| tarkor | r2-luz | q17 | 145,2 | 8,4 | 83,6 | 7,0 / 1,14 |
| tarkor | r2-luz-r1 | q18 | 95,4 | 27,2 | 61,4 | — |
| tarkor | r2-luz-r1 | q19 | 85,9 | 24,0 | 66,2 | — |
| toveriai | r2-control | q20 | | | 76,4 | ≈ 16 |
| toveriai | r2-luz | q21 / q22 | | | 65,2 / 65,8 | ≈ 16 |
| portal | r2-control | q23 | | | 76,9 | 17,4 |
| portal | r2-luz | q24 / q25 | | | 79,5 / 78,9 | ≈ 18 |
| galivelop-image-generator | r2-control | q29 | | | 82,9 | ≈ 17,5 |
| galivelop-image-generator | r2-luz | q30 / q31 | | | 74,6 / 81,2 | ≈ 17,5 |
| galivelop-workflow | r2-control | q35 | | | 97,1 | ≈ 17-18 |
| galivelop-workflow | r2-luz | q36 / q37 | | | 97,0 / 96,2 | ≈ 17-18 |

Tarkor (objetivo de su hoja: Y 105-150, S 18-32): el contraste bajo de r2-luz no es del cielo sino de que el tercio
izquierdo entra en el suelo oscuro; con el velo `#221c16:0.45` del compositor el texto queda legible, pero el prompt
tiene que dejar el tercio limpio de arriba abajo.

## Elegidos (elegido por el agente, delegado)

| Proyecto | Elegido | Por qué | Lo que falla aún |
|---|---|---|---|
| tarkor | **q18** (`r2-luz-r1`) | Primera vez con la saturación dentro del rango (27,2) y color «rico» sin `sun` | Y algo bajo (95); faltan el ámbar `#f2b34a` y el carmesí en la paleta |
| toveriai | **q20** (control) | Mejor paleta (76,4) y zona de arriba limpia | — |
| portal | **q23** (control) | Limpio; q24 trae un punto rosa fuera de paleta y q25 un marco | — |
| galivelop-image-generator | **q29** (control) | Paleta 82,9; las dos `luz` cortan el motivo en el borde | — |
| galivelop-workflow | **q37** (luz) | Las tres miden igual (≈ 97 %); q37, el mejor a la vista en la hoja de contactos | — |

## Siguiente

Componer los elegidos con `gimg choose` / `compose` (pendiente (c) de la bitácora) y, para Tarkor, una ronda con
`r2-luz-r1.txt` como `estilo.txt` subiendo la luz y pidiendo el ámbar y el carmesí.
