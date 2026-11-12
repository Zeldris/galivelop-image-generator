# Entrega de la hoja de estilo a WMF-imagenes (2026-11-12)

Para la sesión de `WMF-imagenes` (clon de World-Maker-Fantasy donde vive el generador del mundo). Desde aquí no se
toca ese repo. Leído: `image-generator/estilo/mundo.json` en su `origin/main`, entero, el 2026-11-12.

**Qué leer de galivelop-image-generator:** `docs/marcas/tarkor/hoja.md` §6 (fila «Mapa de Helek») y §16 (reglas C9,
P2, P3 y A12).

## Qué no cambia

`mundo.json` es del mundo (fichas, banners, miniaturas, iconos de objeto) y la hoja de Tarkor es de la marca
(logo, interfaz, redes, Instalador, Steam): son dos cosas distintas y sus reglas no se pisan.

- El preámbulo de noche («the sky is full of stars under a soft, even pearly glow») se queda: la hoja veta `stars`
  y `glowing` solo en las piezas de marca, donde la estrella es del emblema.
- `vetadas` y `negaciones` se quedan: coinciden con la hoja (sin luna; lo que no debe salir no se nombra).
- `gradacion.json` y los LUT no pasan por esta hoja.

## Qué alinear

1. **«long violet shadows»** en `luz.atardecer` de las Llanuras del Viento Rojo. El violeta es la luz reservada
   de la marca y del canon (hoja §6, «Palabras vetadas»; regla C9): se pide revisarlo, por ejemplo «long cool blue
   shadows». Lo decide vuestra sesión con la persona; si es intencionado para el mundo, decidlo y la hoja lo apunta
   como excepción.
2. **`estilos.mapa` es ahora el acabado del mapa de Helek** (decisión de la persona, 2026-11-12: pintado, con el
   acabado de las ilustraciones del juego). Los bloques de terreno y de icono de `docs/marcas/tarkor/pedido-mapa.md` §2 copian su
   frase literal («Painterly realism halfway between a photograph and an oil painting: realistic terrain, light and
   texture rendered with soft, visible brushwork»). Si cambiáis `estilos.mapa.base`, avisad: el bloque se vuelve a
   copiar.
3. **`encuadres.mapa`** («Empty terrain seen from straight above…») y el bloque de terreno dicen lo mismo con
   otras palabras («seen from directly above»). No hace falta unificarlos; se apunta para que nadie los crea
   distintos.
