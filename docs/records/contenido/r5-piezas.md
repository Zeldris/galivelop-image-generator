# r5 piezas por formato (2026-10-27)

¿El mismo estilo aguanta los formatos de redes sin rehacer la marca? Para cada proyecto, el estilo elegido en r2 con
la composición pensada para cada formato (`examples/<proyecto>/prompts/r5-*.txt`, escritos por Fable desde las
biblias): cuadrado 1080×1080 (se genera a 1024×1024), vertical 1080×1350 (896×1152), cabecera 1500×500 (1536×512) y
avatar (solo el logo, sin generar). En Tarkor, además, `r5-og-bajo`: el og con menos luz. FLUX.2 klein 4B Q8_0,
6 pasos, semilla 3.

- Fondos: `examples/pilot/ronda.sh r5` → `piloto/r5-fondos/`.
- Piezas: `python3 examples/pilot/piezas.py r5` → `piloto/r5/<proyecto>/intentos/`, con medidas en `medidas/`.
- Para verlas: `python3 examples/pilot/ver.py` y `http://127.0.0.1:8765/piloto/r5/index.html` (abiertas como archivo
  desde VS Code en flatpak no cargan las imágenes; ver «Páginas» abajo).

## Ejecución

| Formato | Tiempo (×7) | Mín. libre |
|---|---|---|
| Cuadrado 1024×1024 | 227-230 s | 7323-7787 MB |
| Vertical 896×1152 | 223-225 s | 7308-7791 MB |
| Cabecera 1536×512 | 172-174 s | 7589-8104 MB |
| og-bajo de Tarkor 1280×640 | 180 s | 7502 MB |

22 de 22, salida 0, en ~78 min. El coste va con los píxeles (1,05 M el cuadrado y el vertical, 0,79 M la cabecera), no
con el prompt. Componer las 29 piezas (con los 7 avatares) lleva ~1 min.

## Medidas (contraste del fondo con velo y sin texto en la zona; paleta de la pieza)

| Proyecto | Cuadrado | Vertical | Cabecera |
|---|---|---|---|
| portal | 15,07 (peor 14,17) · 82 % | 14,54 (10,98) · 76 % | 15,69 (15,29) · 70 % |
| toveriai | 15,92 (15,6) · 67 % | 15,19 (14,69) · 75 % | 15,05 (14,83) · 77 % |
| galivelop-workflow | 15,75 (15,54) · 94 % | 15,89 (15,64) · 94 % | 15,14 (14,82) · 93 % |
| tarkor | 6,28 (5,18) · 84 % | 7,22 (4,98) · 69 % | 11,39 (6,89) · 73 % |
| galivelop-image-generator | 16,48 (15,42) · 75 % | 16,44 (16,28) · 79 % | 15,49 (15,33) · 75 % |
| galivelop-voice-generator | 15,46 (14,6) · 80 % | 15,89 (15,66) · 81 % | 15,07 (14,45) · 75 % |
| galivelop-developer | 17,01 (16,87) · 91 % | 16,5 (16,33) · 88 % | 13,22 (9,87) · 83 % |

Todas sobre el 4,5:1 de AA. Tarkor es el único que baja del 7:1 de AAA (texto oscuro sobre niebla clara en el tercio
inferior), con el vertical en 4,98 en su peor punto: se lee, pero es el primero que fallaría con otra semilla.

**Tarkor og-bajo** (frente al og de r4): YAVG 169 → 66, el fondo deja de estar lavado y el texto pasa a claro
(`#f1e4d0`, contraste 9,5, peor 7,36). Pero SATAVG sigue en 5 (r4: 7,8), lejos del 15-30 que pide el juego, y la
paleta cae al 51 % (el cielo `#52626f` no está entre los hex de la biblia). Más luz baja no basta: hace falta pedir el
color de forma explícita (acento en las agujas, banda cálida más ancha) o aceptar que la marca es desaturada.

## Lectura a ojo

Hoja: las cuatro piezas de cada proyecto en una fila.

- **El estilo aguanta los formatos.** Cada proyecto se reconoce en los tres formatos: el umbral de portal, la acuarela
  de toVeriAI, las líneas de workflow, las agujas de Tarkor, los marcos de image-generator, la onda de voice-generator
  y el anillo de developer. El prompt por formato (dónde va el sujeto, dónde queda libre) se respetó en los 21 fondos.
- **Un fallo, arreglado en la pieza:** en la cabecera de developer, con la zona izquierda, la línea de luz terminaba
  justo en la última letra del título. La medida no lo vio (peor 15,96: la línea queda fuera de la caja de la zona,
  pero el título la toca). Con la zona abajo queda limpio (peor 9,87). Es el mismo caso que el og de r4.
- **Los avatares** salen limpios (la baldosa del logo a 512×512); en el de toVeriAI, sobre fondo oscuro, el símbolo
  dorado pierde algo frente al claro de la marca.
- El vertical de portal tiene el peor contraste de los oscuros (10,98): el haz del umbral sube hasta la zona.

## Conclusiones para F2

1. **Un prompt por formato basta**: no hace falta una biblia por formato, sino decir en cada perfil de pieza dónde va
   el sujeto y dónde el hueco (perfiles de D3 y D20). Los perfiles r5 se pueden pasar tal cual a F2.
2. **La zona tiene que mirar el fondo**, y no solo la caja: dos de 29 piezas con texto (og y cabecera de developer)
   tenían un trazo brillante tocando el texto. Para F2.9: medir en la caja del texto real, ampliada unos píxeles, y
   avisar de bordes fuertes ahí, además del contraste por percentiles.
3. **El tiempo es predecible** por píxeles y pasos (±1 %): la interfaz puede dar el tiempo estimado antes de encolar
   con una tabla por modelo y máquina hasta que el registro tenga mediana (D10).
4. Tarkor necesita otra vuelta en su estilo, no en la composición: queda como pendiente de marca, no del generador.

## Páginas

Las páginas del piloto (`piloto/**/index.html`) y el prototipo (`docs/interfaz/prototipo/`) cargan bien servidas por
HTTP. Abiertas como archivo desde VS Code en flatpak, el portal de documentos da al navegador solo ese HTML: se ven los
prompts y no las imágenes. `examples/pilot/ver.py` sirve el repo en `127.0.0.1:8765`, y las páginas avisan si una
imagen no carga desde `file://`.
