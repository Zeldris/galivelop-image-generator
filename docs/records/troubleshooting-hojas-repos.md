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
