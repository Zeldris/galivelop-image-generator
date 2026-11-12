# Entrega de la hoja de estilo a World-Maker-Fantasy (2026-11-12)

Para la sesión del juego (`World-Maker-Fantasy`). Desde aquí no se toca ese repo: esta nota dice qué leer y qué
cambiar allí. Leído en `origin/main` `3a10a3fa` y en `origin/claude/marca-interfaz` `c858a150`.

**Qué leer de galivelop-image-generator**, en este orden:

1. `docs/marcas/tarkor/hoja.md` §16: las reglas (DEBE / NUNCA) con su comprobación.
2. `docs/marcas/tarkor/hoja.md` §17: qué pieza lleva cada pantalla, su tamaño, formato y estado.
3. `docs/marcas/tarkor/peticiones.md` §3: el prompt de cada pieza.
4. `docs/propuestas/tarkor/diseno-interfaz-2026-11-10.md`: la propuesta de la que salió UX-40 (ya la tenéis como
   `docs/producto/diseno-interfaz-marca.md`).

**Dónde estarán las imágenes:** `examples/tarkor/entrega/ui/` (interfaz) y `examples/tarkor/entrega/marca/`
(og, avatar, cápsulas) de galivelop-image-generator, fuera de git; la copia al juego la hace la persona. Los logos
en SVG ya existen: `docs/marcas/tarkor/logos/`.

## Qué cambiar en el juego

1. **Fusionar UX-40 a `main`, antes de recibir imágenes** (decisión de la persona, 2026-11-12: hasta entonces no
   se os entrega ninguna). La marca en la interfaz está hecha en `claude/marca-interfaz` (`c858a150`) y `main`
   no la tiene: faltan `--color-gold-100…900`, `--color-stone-500/700`, `--color-night-900/950` y
   `--color-crystal-deep` (`frontend/src/index.css` l.55-66 de esa rama), `.gold-hairline` (l.277),
   `.corner-bracket-gold` (l.372) y `.title-gold` (l.462). Sin esos tokens, UX-41 no tiene dónde apoyarse.
2. **Valores que tienen que quedar tal cual** (hoja §3 y regla C1):

   | Token | Valor | Token | Valor |
   |---|---|---|---|
   | `gold-100` | `#ffe9a8` | `stone-500` | `#6b6257` |
   | `gold-300` | `#f2c45a` | `stone-700` | `#3a342d` |
   | `gold-500` | `#b8862b` | `night-900` | `#1a2140` |
   | `gold-700` | `#7a5a1e` | `night-950` | `#0f1428` |
   | `gold-900` | `#5a3a14` | `crystal-deep` | `#1f4a55` |

3. **Favicon:** `frontend/public/favicon.svg` sigue siendo el de Vite (lleva `#863bff`, morado: regla C9). Se
   sustituye por `docs/marcas/tarkor/logos/tarkor-emblema-simple.svg` y se añade `<link rel="icon">` en
   `frontend/index.html`.
4. **`og:image`:** `frontend/index.html` ya tiene `og:title` y `og:description` en la rama de UX-40, pero no
   `og:image`. Llegará `e03-og.png` (1200×630); hoy está pedida y se rehace.
5. **Tarjetas de `gw-media-content`** (`.claude/gw/gw-media-content.md` y
   `docs/media/_plantilla/media/source/{tarjeta,diagrama}.html`): usan la paleta del Portal y DejaVu / Liberation
   Sans. Para Tarkor, fuera del juego:

   | Hoy | Pasa a | Papel |
   |---|---|---|
   | `#06121c` | `#0f1428` | fondo |
   | `#0c1d2b` | `#1a2140` | superficie |
   | `#1b3447` | `#7a5a1e` | borde |
   | `#eaf4fa` | `#f1e4d0` | texto |
   | `#1aa6df` | `#b8862b` | acento (≤ 10 % de la tarjeta) |

   Titulares en Cinzel 700 y texto en Inter 400, las dos ya empaquetadas en `frontend/src/assets/fonts/`. El
   **Propuesta de galivelop-image-generator, sin decidir:** el reparto de papeles lo decide la persona.
6. **UX-41, las imágenes**, en el orden en que llegarán (estado de cada una: hoja §17):
   - ya válidas: barra de progreso E7 (pista y relleno, 1024×32), marco de retrato E11 y plantilla de captura E12;
   - después: texturas #2 (`.plank-panel`), #3 (`.wood-grain`), #4 (`.dust-road`), #5 (`.iron-band`) y #7
     (`.plank-panel-defense`), PNG de 1024² en mosaico (la #5, 1024×256);
   - después: esquinas #8, separador #9, ranura #10 y los pictogramas #11-#15, que sustituyen a los emojis;
   - al final: cielo #6, carga E6, hero E5.
   Destino propuesto: `frontend/src/assets/ui/`.
   Recomprobado en los componentes de `c858a150`: el ⚔️ de `Home.tsx` l.45 no tiene pieza pedida (vale la pestaña
   «personaje» del #11); el 🎲 está también en `CombatExchangeBadge.tsx`, `RollBadge.tsx`, `ExtendedRollBadge.tsx` y
   `GatheringDiceReveal.tsx`, no solo en `DiceRoll.tsx` l.113, y el #14 sirve para todos; quedan emojis sin pieza en
   `EnciclopediaPanel.tsx`, `EquipoPanel.tsx`, `HungerThirstSelectionModal.tsx`, `CompanerosPanel.tsx` y
   `EstadisticasPanel.tsx`: decid si se piden. `.corner-bracket-gold` (l.372) no lo usa ningún componente y
   `.title-gold` solo `Home.tsx` l.30.
7. **`.dust-road`** sigue marcado «Provisional» (l.175): deja de serlo cuando llegue la #4.
8. **Mapa de Helek: pintado**, con el acabado de vuestras ilustraciones (`estilos.mapa` de
   `image-generator/estilo/mundo.json`); decisión de la persona, 2026-11-12 (hoja §16, regla A12). La montaña de
   prueba (q373) salió en vector plano y se repite. Cambios que pedimos al original,
   `docs/producto/pedido-imagenes-mapa.md` (`7c5e2d13`, rama `claude/pedido-mapa`), ya hechos en nuestra copia
   `docs/marcas/tarkor/pedido-mapa.md`: bloque de terreno con el acabado pintado y bloque de icono escrito aparte (M-B); fuera el bloque «Negativo»; la
   costura la da `tileable`, no se arregla a mano; perfiles `texturamapa` 1024², `iconomapa` 768², `cartela`
   1024×512, `bandamapa` y `marcomapa` 1024×256; modelo Z-Image a 8 pasos; #39 y #43 sin `star`; #40 sin `title`;
   la frase de croma de la hoja al final de cada pieza recortada; #27-#38, #42 y #45-#47 con el texto de
   nuestros pedidos.
9. `image-generator/estilo/` (`gradacion.json`, LUT): sin cambios. `mundo.json`: una sola cosa a revisar, en
   `docs/propuestas/wmf-imagenes/entrega-hoja-2026-11-12.md`. Las fichas, banners y miniaturas
   del mundo siguen siendo de vuestro generador y no pasan por esta hoja.
