# Troubleshooting de las hojas de los repos (Tarkor)

Lo que el generador no saca bien tras dos o tres intentos se apunta aquí y se **rediseña con algo que sí sale** (regla de
la persona, 2026-11-12). Ronda de interfaz de Tarkor del 2026-11-15 (#986-1125), juzgada por el agente (delegado).

**Causa común:** el preámbulo de materiales y «warm raking light, deep cool shadows» se cuela en texturas, bandas y
placas: madera donde se pide hierro, haces de luz horneados, perspectiva. Conviene un preámbulo reducido para los
perfiles `textura`, `banda` y `tira`.

**Al reescribir (2026-11-15):** las negaciones de la columna «Rediseño» son la idea, no el texto: la regla P3 de
`docs/marcas/tarkor/hoja.md` las prohíbe (se cuelan: «no stars» pintó una estrella), así que los pedidos describen en
positivo lo que sí debe salir. Hover y pulsado de e13 se derivan del botón base; sus pedidos se borraron.

| Problema | Intentos | Rediseño |
|---|---|---|
| 02 tablón, 03 madera de fondo y 07 tablón de defensa: haces de luz y sombra azul horneados, desconchones dorados; no repiten | q986-q991, q1000-q1002 | Sin la frase de luz rasante: «flat diffuse light, no cast shadows, no gold» |
| 04 camino de polvo: salen tablones con polvo rojo | q992-q994 | Sin preámbulo: «packed dry earth ground, fine red dust, no planks, no wood» |
| 05 banda de hierro: sale madera con un parche de piedra | q995-q997 | Solo «dark forged iron plate», sin madera ni piedra; el filete dorado, por CSS |
| 09 separador con estrella: barra gruesa de hierro y madera | q1006-q1007 | Generar solo el remate de cuatro puntas (cuadrado, croma); el filete que se desvanece, por CSS (`.gold-hairline`) |
| 11 pestaña reputación: un anillo, idéntico a la categoría accesorio | q1043-q1045 | Corona de laurel en oro (o dos eslabones), sin «ring» |
| 12 barra de hambre: sale un hueso, choca con la categoría hueso | q1048-q1049 | «a roasted drumstick, thick round meat on a short bone, not a bare bone» |
| 13 fase fin: un «60» grabado; silueta rara con aro de pinchos | q1060-q1061 | Pergamino enrollado con cinta, «blank, no numbers», aro liso de hierro |
| 15 categoría alimento: los panes llevan «%» grabado | q1072-q1073 | Hogaza redonda con tres cortes, «blank surface, no symbols» |
| 15 categoría piel: sale un animal de pie | q1094-q1095 | Piel extendida vista desde arriba, «no head, no standing animal» |
| 16 medallón: haz de luz sobre el croma, piedra morada, aro cobrizo | q1100-q1101 | «flat even light, no light beam», aro #b8862b, piedra gris parda |
| e13 botón, hover y pulsado: bandeja en perspectiva o placa manchada; el pulsado no se lee hundido | q1118-q1123 | Una sola placa ortográfica, plana y lisa; hover y pulsado derivados por brillo (CSS o `gimg export`) |
| e17 tooltip: discos ovalados de madera en perspectiva | q1124-q1125 | Placa de hierro rectangular ortográfica, esquinas rectas; o resolverlo con CSS y el filete dorado |

**Familias (observaciones):** habilidades y fase elección son la misma gema; fase ocupado y estado en curso, la misma
rosa: vale si no conviven en pantalla. Los cuatro estados solo se distinguen por una gema diminuta (ámbar y rojo casi
iguales): reforzar el color por CSS. Pestañas pedidas: 12, no 13.

## Encargo UX-41 (2026-11-16, pedidos `examples/tarkor/orders/ux41/`, sin encolar)

Rediseños al escribir los pedidos, antes de generar (elegido por el agente, delegado):

| Problema | Intentos | Rediseño |
|---|---|---|
| 11 pestaña reputación: anillo (q1043-q1045); el rediseño a laurel, sin probar, es otro círculo abierto a 16-24 px | q1043-q1045 | Balanza: poste, astil recto y dos platillos (`ux41/14-pestana-reputacion`) |
| 13 fase fin: «60» grabado y silueta rara; el rediseño a pergamino choca con mapa y leyendas | q1060-q1061 | Puerta cerrada en arco, de tablones con dos herrajes (`ux41/15-fase-fin`) |
| 11 pestaña mapa: «rolled parchment» da un pergamino, igual que leyendas | q1032 | «flat unfolded map sheet» con pliegues, ruta a trazos y una X; sin «parchment» ni «scroll» |
| 15 alimento: hogaza con «%» grabado | q1072-q1073 | La categoría nueva `comida` es una cuña de queso con agujeros; el muslo queda para `hud-hambre` |
| 17 estados: solo cambiaba una gema diminuta | q1103-q1109 | Tres siluetas: triángulo con exclamación, aspa sobre sello rojo, marca de verificación sobre sello musgo |
| 08 esquina: brazos de madera finos, filo verdoso al recortar | q1005 | Toda de oro, brazos de un quinto de su largo, contorno de bronce grueso; `gimg brand matte --grow 4` |
| e07 barras: fondo de madera y piedra que hubo que recortar | q660, q662 | Bloque reducido y croma; las bajas se piden a un cuarto del alto y se reducen en vertical a 900×16 |

## Juicio del 2026-11-17 (cola #1137-1246)

Tarkor (instalador y UX-41):
- **ux41/07 enciclopedia:** el libro descrito con materiales sale suelto, sin medallón. Rediseño: medallón primero en la frase; el libro, emblema plano de oro montado en las tablas.
- **ux41/08 mapa:** el pliegue central lo lee como libro abierto a 24 px. Rediseño: hoja plana sin pliegue, borde rasgado, cuatro trazos gruesos y X grande.
- **ux41/12 dado:** con 3 semillas no cuenta puntos (P7) y mete madera. Rediseño: cubo de oro liso con caras en blanco; los puntos 1-2-3, por SVG.
- **ux41/03 hecho:** «stamped into a round seal» deforma el aro; «laid over a round seal» (error) sí funcionó.
- **ux41/06 medicinal:** la receta de categorías da un mortero de bulto que desborda; si se rehace, emblema plano montado.
- **Iconos fuera del aro:** «kept inside the rim» acierta uno de cada tres en flechas y rayos.
- **i3 portada:** con camino, puerta y estandartes el cinturón desaparece; describir primero el cinturón ancho (frase de i6) y la empalizada como silueta lejana.
- **i4 riel:** el bloque común de materiales gana a «hierro». Rediseño sin ese bloque: chapa continua `#171310` con rejilla grabada.
- **SVG de medallones:** el trazado del medallón entero sale posterizado (motas de oro en la madera, cerco verde del croma); para vector limpio, trazar solo el motivo.

Portal y GVE:
- **«deep teal #16827c» junto al cerúleo** sale azul petróleo, igual que el mar (og de Developer). Rediseño: el vivo `#0e9a93` con nombre de verde.
- **«capsule… vial of a spirit level»** en cuadrado da cápsula vertical (termómetro) las tres veces. Rediseño: figura apaisada descrita de izquierda a derecha.
- **«dark olive green #6b7509»** sobre croma magenta sale verde botella: igualar al hondo al vectorizar.
- **Cantidades vagas** («a few lines») dan 6-7 filas; aros «a lo largo» de una curva la deshacen. Mejor posiciones que cantidades.
- **Grabados sobre papel traen marco y margen** pese a «no border»: se recorta. Los de mar a sangre, no.
- **Regla de mareas:** 2 de 8 intentos con garabatos como cifras; mirarla siempre de cerca.
- **Iconos que ocupan poco cuadro** se emborronan a 28 px: recortar al motivo antes de trazar.
- **«off-white #fbfcfd» sale crema** en fondos y tarjetas, como el 12 del Portal.
- **31e portada de workflow (q1421-1424), quinta ronda:** con Z-Image los cuatro salen pintura casi fotográfica, no grabado; boyas esféricas en perspectiva baja en vez de discos vistos desde arriba; la cuerda sale por los dos bordes pese a «nothing touches the edges». Rediseño: composición con FLUX (cenital, discos, cadena dentro) y grabado con Z-Image img2img sobre ella; o dibujar la cadena por código y pedir solo el mar. El visto en la boya azul sí sale bien las cuatro veces.
