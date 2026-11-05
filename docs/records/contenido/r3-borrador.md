# r3 borrador frente a definitivo (2026-10-27)

¿Sirve un borrador barato para decidir antes de pagar el definitivo (D20, D30)? El estilo elegido en r2
(`examples/<proyecto>/prompts/estilo.txt`), semilla 3, con FLUX.2 klein 4B Q8_0: borrador 640×320 a 4 pasos y
definitivo 1280×640 a 8 pasos. En portal, además, FLUX.3 Image Klein a 640×320/8 y 1280×640/16 (`R3_FLUX3`).
`examples/pilot/ronda.sh r3`. Para revisar: `piloto/r3/index.html`.

## Ejecución

| Pieza | Tiempo | Muestreo | VAE | Mín. libre |
|---|---|---|---|---|
| Borrador 640×320, 4 pasos (×7) | 51-52 s | ~39,4 s | ~6,6 s | 7299-7571 MB |
| Definitivo 1280×640, 8 pasos (×7) | 228-230 s | ~194,5 s | ~28,6 s | 7094-7655 MB |
| FLUX.3, en la GPU (×2) | falla a los 12-13 s | — | — | ~7560 MB |

El borrador cuesta **el 22 %** del definitivo: unos cuatro borradores por definitivo. Los 14 de klein, salida 0 y
tiempos casi idénticos entre proyectos (el prompt no cambia el coste).

**FLUX.3 en la GPU no arranca** con el `--max-vram vulkan0=2` de `generar.sh`: «cannot make enough memory available on
Vulkan0: need 5862.40 MB device / 5350.40 MB budget, available … 2048.00 MB budget», porque su grafo va en un solo
segmento que no se trocea. Es lo mismo que encontró el banco de Tarkor (`WMF-imagenes/docs/arquitectura/reutilizables/
01-generacion-imagenes-local.md`, y subir el tope bloqueó la Deck). Arreglo en `ronda.sh`: FLUX.3 con
`--backend diffusion=cpu -t 8`, `Qwen3VL-4B-Instruct-Q4_K_M` y `flux2-vae`, como el banco (r10 allí: ~62 min a
1280×512/16 pasos). Relanzado tras r5:

| Pieza (FLUX.3 en la CPU) | Muestreo | VAE | `generate_image` | Mín. libre |
|---|---|---|---|---|
| 640×320, 8 pasos | 520 s (65 s/paso) | 12 s | 544 s en total | 5115 MB |
| 1280×640, 16 pasos | 3462 s (216 s/paso) | 53 s | 3524 s (59 min) | 3133 MB |

El reloj del segundo marcó 21 875 s (6 h): la diferencia, unas 5 h, no está en ninguna fase del log de `sd-cli`, así
que casi seguro la Deck se suspendió durante la noche con el proceso parado. Cuenta el cómputo: **59 min, unas 15
veces el definitivo de klein (229 s)**, y la RAM libre bajó a 3,1 GB (la máquina, sin margen para otra cosa).

**Calidad frente a klein (misma semilla y prompt):** FLUX.3 sale más fotográfico y arquitectónico (una puerta real en
una sala de hormigón, con haz de luz y suelo mojado), pero se va del estilo de marca: menos cian, puntos de color más
pequeños y desperdigados, SATAVG 7 frente a 14 y paleta 61 % frente a 71 % (YAVG 61 frente a 59). Para el portal,
klein se ajusta mejor a la biblia; FLUX.3 no compensa en esta máquina. Hoja: `piloto/r3/portal/intentos/`.

## Medidas (`examples/pilot/medir.py`)

YAVG / SATAVG / % de paleta (hex de `prompts/r2-hex.txt`, ΔE76 < 15), imagen entera.

| Proyecto | Borrador | Definitivo |
|---|---|---|
| portal | 51 / 24 / 74 % | 59 / 14 / 71 % |
| toveriai | 186 / 12 / 66 % | 180 / 12 / 69 % |
| galivelop-workflow | 29 / 13 / 96 % | 39 / 9 / 97 % |
| tarkor | 166 / 5 / 79 % | 155 / 7 / 78 % |
| galivelop-image-generator | 39 / 13 / 84 % | 44 / 15 / 76 % |
| galivelop-voice-generator | 35 / 12 / 86 % | 47 / 16 / 75 % |
| galivelop-developer | 29 / 12 / 91 % | 39 / 12 / 87 % |

El borrador sale algo más oscuro (YAVG 4-12 puntos menos, salvo Tarkor y toVeriAI, que son claros) y su % de paleta
queda a ±11 puntos del definitivo. Tarkor sigue lavado (YAVG 155-166, SATAVG 5-7) frente al 70-95 / 15-30 que acepta
el juego: lo prueba `r5-og-bajo`.

## Lectura a ojo

Hoja: borrador, definitivo y og compuesto (r4), una fila por proyecto.

- **El borrador anticipa** el estilo, la paleta, el sujeto y dónde queda el hueco para el texto (a la izquierda) en 6
  de 7 proyectos: portal (umbral a la derecha), toVeriAI (franja de acuarela), Tarkor (agujas a la derecha),
  image-generator (paneles), voice-generator (espiral) y developer (anillo y línea).
- **No anticipa el detalle:** con la misma semilla, el definitivo recoloca (el umbral de portal gira y gana el charco;
  las líneas de workflow cambian de cruce por completo; la línea de developer se alarga hacia la izquierda, que es la
  que luego cruzó el título en r4).
- Con 8 pasos, el definitivo gana textura y profundidad (charco de portal, grano de la acuarela, niebla de Tarkor).

## Conclusiones

1. **El borrador vale para elegir estilo y semilla, no para dar por buena la composición.** Lo que decide el texto (si
   algo cruza la zona reservada) solo se ve en el definitivo. En la interfaz (decisión 5 de `docs/interfaz/propuesta.md`):
   «borrador primero» como opción, activada por defecto desde 1280×640, con la nota «el definitivo puede
   recolocar».
2. Con 4 borradores por definitivo, una tanda típica (3 borradores y el definitivo de la elegida) cuesta ~6,5 min frente a
   ~11,5 min de tres definitivos.
3. FLUX.3 no cabe en el motor tal como lo lanza `generar.sh`; F2 tiene que poder pasar `--backend` por modelo
   (perfil de máquina, D15) y avisar si un modelo no cabe en la GPU antes de encolar.
4. En la CPU, FLUX.3 cuesta ~15 veces klein y no gana en estilo de marca: en el perfil de esta máquina, klein por
   defecto y FLUX.3 como opción marcada «lento (~1 h)», con el tiempo estimado antes de encolar (paso 6, «Retocar», de la
   propuesta de interfaz).
