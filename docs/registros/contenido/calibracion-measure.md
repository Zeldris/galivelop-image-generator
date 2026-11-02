# Calibración de `gimg measure` (2026-11-02, F2.9 punto 7)

Primera pasada de `gimg measure` (F2.9) sobre las imágenes de marca que ya existen y sobre las piezas del piloto, para
proponer umbrales por proyecto. Se hizo en la Deck, sin modelo.

**Paleta por proyecto:** los hexadecimales de `examples/<proyecto>/prompts/r2-hex.txt`, con ΔE76 < 15.

**Imágenes de marca:**
- `Portal-Galivelop/public/marca/galivelop-portal.jpg` y `galivelop-social.png`.
- `Portal-Galivelop/public/proyectos/<proyecto>/portada.webp`.
- `VeriNews_AI/frontend/public/favicon.png`.

**Piezas del piloto:**
- `piloto/r1-gimg/*-og-s3|s4.png`, de la rama `piloto-imagenes`.
- `piloto/r5/<proyecto>/intentos/*.png`, del stash de `f2-motor`. Son piezas compuestas, con texto y logo.

**EMD:** se mide frente a la primera imagen de marca del proyecto. Developer y voice-generator no tienen portada en el
Portal, así que no tienen EMD.

Los avatares no se midieron, porque son solo logo. Los `gw-*.svg` del Portal tampoco: son diagramas, no arte de marca.
Los números completos están en la salida JSON de la sesión; aquí van redondeados.

## Resultados

| Proyecto | Imagen | YAVG | SATAVG | % paleta | EMD Y / Cb / Cr |
|---|---|---|---|---|---|
| portal | marca `galivelop-portal.jpg` | 52 | 15 | 82 | — |
| portal | marca `galivelop-social.png` | 47 | 17 | 80 | — |
| portal | r1 s3 / s4 | 63 / 59 | 18 / 17 | 65 / 77 | 18,7 / 7,6 / 9,0 · 13,8 / 6,3 / 9,0 |
| portal | r5 cabecera, cuadrado, vertical | 53-62 | 14-16 | 70-82 | Y 19-26, Cb 4,3-5,4, Cr 5,8-6,9 |
| tarkor | marca `portada.webp` | 127 | 25 | 42 | — |
| tarkor | r1 s3 / s4 | 129 / 125 | 35 / 31 | 7 / 12 | 14,7 / 12,8 / 4,7 · 5,1 / 9,9 / 4,6 |
| tarkor | r5 cabecera, cuadrado, vertical | 172-177 | 5-7 | 69-84 | Y 45-50, Cb 6,8-8,1, Cr 19-20 |
| tarkor | r5 og-bajo | 66 | 5 | 51 | 61,3 / 12,3 / 22,3 |
| toveriai | marca `portada.webp` | 220 | 2 | 95 | — |
| toveriai | marca `favicon.png` | 39 | 3 | 1 | — (ver «Límites») |
| toveriai | r1 s3 / s4 | 162 / 166 | 22 / 20 | 42 / 64 | Y 55-58, Cb 9,9-10,9, Cr 14-16 |
| toveriai | r5 cabecera, cuadrado, vertical | 188-196 | 7-8 | 67-77 | Y 24-33, Cb 4,5-5,4, Cr 2,4-5,2 |
| workflow | marca `portada.webp` | 39 | 10 | 95 | — |
| workflow | r1 y r5 | 33-48 | 9-11 | 93-96 | Y 4-10, Cb 0,9-1,8, Cr 1,4-3,5 |
| image-generator | marca `portada.webp` | 41 | 13 | 77 | — |
| image-generator | r1 y r5 | 33-50 | 11-15 | 75-88 | Y 8-11, Cb 1,2-3,3, Cr 2,5-4,2 |
| developer | r1 y r5 | 28-48 | 10-11 | 83-97 | — |
| voice-generator | r1 y r5 | 35-52 | 11-15 | 75-86 | — |

## Lectura

**Tarkor.** La medida confirma lo que ya se había visto a ojo (`r5-piezas.md`). Las piezas r5 salen mucho más claras
que la portada: YAVG de 175 frente a 127. También salen mucho más desaturadas: SATAVG de 5-7 frente a 25. Su EMD Cr, de
19-22, está lejos del 7,5 de Tarkor. El r1 tenía la luz y la saturación de la portada, pero no la paleta: solo un 7-12 %
de píxeles cerca. Es el caso para la LUT de F2.11 y las pautas de luz de r2.

**toVeriAI.** La portada del Portal es casi blanca: YAVG 220, SATAVG 2. Las piezas r5 se le acercan en color, con Cb y Cr
por debajo de 6. El r1 no se le acercaba.

**Portal, workflow e image-generator.** Están dentro de los umbrales de color de Tarkor, Cb ≲ 6 y Cr ≲ 7,5. En el Portal,
Cr da 5,8-6,9 en r5 y 9 en r1.

**EMD Y.** Pesa mucho la composición. Un texto y un logo claros sobre fondo oscuro suben la luma media, así que la EMD Y
no sirve sola como criterio de marca.

## Umbrales propuestos

Son orientativos. Mandan el juicio a ojo y las reglas R1-R3 de `docs/plan.md`.

| Proyecto | YAVG | SATAVG | % paleta | EMD Cb / Cr |
|---|---|---|---|---|
| portal | 45-65 | 13-19 | ≥ 70 | ≤ 6 / ≤ 7,5 |
| tarkor | 105-150 | 18-32 | ≥ 30 | ≤ 6 / ≤ 7,5 |
| toveriai | 180-225 | ≤ 10 | ≥ 65 | ≤ 6 / ≤ 6 |
| galivelop-workflow | 30-50 | 8-12 | ≥ 90 | ≤ 3 / ≤ 4 |
| galivelop-image-generator | 33-52 | 10-16 | ≥ 72 | ≤ 4 / ≤ 5 |
| galivelop-developer | 25-50 | 9-12 | ≥ 80 | sin portada |
| galivelop-voice-generator | 33-55 | 10-16 | ≥ 72 | sin portada |

Developer y voice-generator se calibraron solo con piezas propias del piloto, sin imagen de marca. Tarkor se calibró
con su portada, no con sus piezas.

## Límites encontrados

- **Transparencia.** `measure` no tiene en cuenta la transparencia: un PNG transparente, como el favicon de toVeriAI, se
  mide como si su fondo fuera negro, y sale un 1 % de paleta. Se apunta como leve: descartar los píxeles con alfa 0, o
  componer sobre un color dado.
- **Portadas que no son marca.** Las portadas del Portal pueden ser capturas de la interfaz y no arte de marca. Así lo
  sugiere la de toVeriAI, casi blanca. La persona dice si sirven de referencia.
