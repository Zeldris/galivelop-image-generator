# Entrega de la hoja de estilo al Instalador (2026-11-12)

Para la sesión del Instalador (`Instalador-WMF-Tarkor`). Desde aquí no se toca ese repo: esta nota dice qué leer y
qué cambiar allí. Leído en `origin/claude/installer-docs-review-09e7vs` `34d2bb27` (`main` está en `5631e77b`).

**Qué leer de galivelop-image-generator:**

1. `docs/marcas/tarkor/peticiones.md` §3, «Bloque I — Instalador»: vuestras I1-I6 tal como las pedisteis en
   `docs/13-hoja-de-estilos-e-imagenes.md` §3 (`d9d33fe`, `608661d`).
2. `docs/marcas/tarkor/hoja.md` §16 (reglas con su comprobación) y §17, tabla «Instalador» (estado de cada pieza).

**Dónde estarán las imágenes:** `examples/tarkor/entrega/` de galivelop-image-generator, fuera de git. La persona
las copia a `entrega/` en la raíz de vuestro repo (vuestra decisión 4) y `INS-58` las convierte y coloca. Los SVG
ya existen: `docs/marcas/tarkor/logos/tarkor-emblema-simple.svg`, `tarkor-lockup-v.svg`, `tarkor-lockup-h.svg`.

## Qué cambiar en el Instalador

1. **Nombres de hierro en la tabla de paleta del doc 13.** Llama `iron-950` a `#0e0b08` e `iron-900` a `#171310`.
   En el juego son `iron-900` `#0e0b08` e `iron-800` `#171310` (`frontend/src/index.css` l.35-36, `c858a150`);
   `iron-950` no existe. Los hex están bien: solo cambian los nombres.
2. **Tokens que faltan en `app/src/estilos.css`** (INS-56), con el valor de la hoja §3:

   | Token | Valor | Token | Valor |
   |---|---|---|---|
   | `gold-100` | `#ffe9a8` | `stone-500` | `#6b6257` |
   | `gold-300` | `#f2c45a` | `stone-700` | `#3a342d` |
   | `gold-500` | `#b8862b` | `night-900` | `#1a2140` |
   | `gold-700` | `#7a5a1e` | `night-950` | `#0f1428` |
   | `gold-900` | `#5a3a14` | | |

3. **`.filete` y `.btn.pri` dejan el cristal** (`accent`) y pasan a oro: el cristal queda para foco y enlace
   (regla C6). Filete en `gold-700`. **Propuesta de galivelop-image-generator, sin decidir:** el botón principal,
   con cerco `gold-700` sobre madera; la regla solo exige que deje el cristal.
4. **`.btn.pri { color: #fff }`** incumple C9 (blanco puro): pasa a hueso `#f1e4d0`.
5. **Cinzel:** hoy cargáis 400, 600 y 700. La hoja usa 700 en titulares y 900 solo en el hero del juego; «TARKOR»
   en el riel, con `.title-gold`, va en 700 salvo que queráis el 900 (entonces hay que empaquetarlo).
6. **Lo que gimg no hace hoy** y, hasta que lo haga, convierte `INS-58`: BMP de 24 bits sin alfa (I1, I2), WebP
   (I3, I4), ICO (I5), el perfil `lateral` 704×1344 (I1 saldrá de `portrait` 896×1152 recortado a 602×1152, como
   prevé vuestro doc) y los recortes (1536×384, 600×900, 920×430). Lo que recibiréis es PNG al tamaño generado.
7. **Qué recibiréis y dónde va**, por orden de llegada:
   - E14 → `app/src-tauri/icons/` (siete archivos; el `.ico` lo hacéis allí). Disco de noche `#0f1428`, como
     decidisteis: la hoja ya lo dice así (antes decía madera).
   - I2 (composición, sin generar) e I1 → `app/src-tauri/windows/cabecera.bmp` y `lateral.bmp`.
   - #17 estados (4) → `app/src/imagenes/estado-*.png`; E7 pista y relleno (ya válidas: q357, q359).
   - I3 → `app/src/imagenes/portada.webp`; I6 y los recortes de E4 y E5 → `app/src-tauri/steam/`.
   - I4, #2, #3, #5 (`.barra`), #9, E13: al final; hasta entonces sigue el CSS.
8. **Comprobaciones al colocar** (hoja §16): I4 con luminancia media < 40 sobre 255 (A5); estados legibles a 20 px
   en gris (A3); I6 legible a 200 px de ancho (A4); todo lo de `app/src/imagenes/` por debajo de 1 MB (A8); los
   BMP sin alfa (A9).
9. **Decidido por la persona (2026-11-12):** I6 (cápsula vertical, 600×900) y el icono 256² (es E14) amplían la
   decisión de Steam de la hoja. Lo demás de la Deck (920×430, 1536×384 y el resto de vuestro doc 13 §3 D) son
   recortes de E4 y E5, sin pieza propia.
