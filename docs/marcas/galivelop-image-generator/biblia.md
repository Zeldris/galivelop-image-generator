# Biblia de estilo: galivelop-image-generator

Herramienta del taller, sin identidad propia: **familia del Portal** con acento violeta **[P]**. Molde y reglas comunes en
[`../README.md`](../README.md). Datos de este repo en `24d69c8`; del Portal, en `aa76b34`.

## 1. Esencia

- **Qué es:** «Generador de imágenes con IA local: un servicio por máquina que comparten varios proyectos» (`README.md`).
  No conoce el dominio del proyecto (D2) y es reproducible: cada elegida lleva su manifiesto (D13, D34).
- **Lema [P]:** «Pide, prueba, elige.»
- **Para quién:** proyectos del taller (Tarkor/WMF el primero) y quien quiera un generador local sin instalar nada
  (Python 3 solo stdlib, D6) en una máquina modesta (la Steam Deck es la de referencia, D4).
- **Valores y ética:** IA local (nada sale del equipo), nada residente (arranca bajo demanda, D11), el humano elige
  (intento → candidata → elegida, y deshacer, D9), honestidad con el estado («aún no genera imágenes reales»).
- **Nunca se muestra:** cámaras, pinceles, chispas o «magia» de IA, robots, cerebros, personas o artistas sustituidos,
  obras reconocibles, promesas de «arte ilimitado», texto generado por el modelo.

## 2. Paleta

| Rol | Hex | Uso |
|---|---|---|
| Acento **[P]** | `#8B5CF6` | símbolo, nombre en el lockup, la «elegida» encendida, enlaces sobre oscuro |
| Acento claro **[P]** | `#A78BFA` | resplandores, halos, texto de acento sobre oscuro |
| Acento oscuro **[P]** | `#5B34C9` | final del degradado de la baldosa, acento sobre fondo claro |
| Fondo oscuro | `#06121c` | fondo de piezas (Portal) |
| Superficies | `#0c1d2b`, `#11283a` | tarjetas y paneles |
| Borde | `#1b3447` | filetes |
| Texto / texto 2 | `#eaf4fa` / `#9fb4c4` | sobre oscuro |
| Fondo claro / texto claro | `#f6fafd` / `#0a1a28` | pieza clara |
| Blanco | `#FFFFFF` | trazo del símbolo |

- **Pieza oscura (por defecto):** `#06121c` con rejilla de puntos y resplandor radial del acento (20-30 % de opacidad);
  texto `#eaf4fa`, secundario `#9fb4c4`, acento `#A78BFA`.
- **Pieza clara:** `#f6fafd`, texto `#0a1a28`, acento `#5B34C9` (más contraste que `#8B5CF6` sobre blanco).
- **Sobre imagen:** texto blanco en la zona reservada; el logo siempre en su baldosa.
- **Prohibidos:** el celeste del Portal (`#1aa6df`) como acento de la herramienta (confunde con el paraguas); violeta
  neón o magenta puro; negro `#000`; texto de acento sobre fondo de acento.

## 3. Tipografía

- **Sora 700** en títulos y en el nombre del lockup, tracking −0,03 em (como `Logo.tsx` del Portal).
- **Inter 400/500** en texto.
- **Monoespaciada del sistema [P]** para claves de pedido y órdenes (`fauna/aullador-rojo`, `gimg order submit`).
- Wordmark: `galivelop-image-generator` en minúsculas, con guiones, de una pieza y un solo color.

## 4. Logo

Propuestas en `logos/` (símbolo `galivelop-image-generator-<letra>.svg` y su `-lockup.svg`), todas en la baldosa de la
familia (128×128, `rx` 30, trazo blanco 12, degradado `#8B5CF6 → #5B34C9`):

- **a. La cola:** tres marcos en fila escalonada hacia el fondo; el de delante, lleno, es la elegida.
- **b. Rejilla de intentos:** un marco con cuatro celdas y una encendida.
- **c. Un marco y su vuelta:** la esquina del marco se dobla en una flecha que apunta a su propio trazo (elegir y
  deshacer, D9).
- **d. El taller que se enciende:** el borde del marco no se cierra: acaba en un punto de luz (arranque bajo demanda).

**Elegido (agente, delegado):** b — la más limpia a 16 px y la que cuenta «intentos y una elegida».

Tras elegir **[P]**:

- Variantes: la baldosa es la misma sobre claro y oscuro (lleva su fondo). El nombre del lockup, `#8B5CF6` sobre oscuro y
  `#5B34C9` sobre claro.
- Margen libre: un cuarto del lado de la baldosa. Tamaño mínimo: símbolo 16 px; lockup 24 px de alto, y por debajo solo
  el símbolo.
- Símbolo y wordmark: en horizontal, nombre a la derecha a 28/128 de separación; nunca el nombre debajo.
- Prohibido: cambiar el `rx` o el trazo, sacar el dibujo de la baldosa, rotarlo, recolorearlo, añadirle sombra o brillo.

## 5. Forma e iconografía

- Radios: baldosa `rx` 30/128 (23 %); en interfaz, 18 y 10 px (Portal).
- Línea: trazo 12/128 con remates y uniones redondos; a 24 px, iconos de 2 px.
- Lenguaje: marcos, celdas, filas y puntos de luz; plano, sin perspectiva ni sombra dura; una sola cosa encendida.

## 6. Voz y frases

- **Tono:** técnico, sobrio y honesto con el estado real; nunca vende.
- **Campo semántico** (`GLOSSARY.md`): pedido, intento, candidata, descartada, elegida, cola, entrega, manifiesto,
  perfil, motor, referencia. Evitar: render, job, cliente, prompt engineering, «magia».
- **Lema [P]:** «Pide, prueba, elige.»
- **Variaciones [P]:** «Un servicio por máquina, para todos tus proyectos.» · «Cada elegida, con su manifiesto.» ·
  «IA local: nada sale de tu equipo.»
- **Ganchos [P]:** «¿Diez intentos y una elegida? Así trabaja.» · «Se enciende cuando se le pide.»
- **Cierres [P]:** «Sin instalar nada.» · «Tú eliges; él recuerda cómo se hizo.»

## 7. Estilo de imagen (FLUX)

- **Sí:** fondo azul noche profundo con rejilla de puntos; marcos finos de cristal en fila, uno más encendido que los
  demás, en violeta; luz volumétrica suave, degradados lisos, reflejos nítidos; arte digital mínimo y elegante.
- **No:** cámaras, pinceles, paletas, chispas, robots, cerebros, personas, cuadros reconocibles, texto.
- **Motivos:** la fila de marcos (la cola), la celda encendida (la elegida), el punto de luz (el arranque).
- **Palabras vetadas** (el modelo pinta lo que se nombra): camera, lens, brush, paint, palette, easel, canvas, sparkle,
  spark, magic, robot, brain, face, person, artist, gallery, text, letters, logo.
- **Zona reservada para texto:** la mitad izquierda, lisa y desenfocada (`og`, `social`); en `square` **[P]**, el
  tercio superior.

## 8. Prompts

| Archivo | Estado |
|---|---|
| `examples/galivelop-image-generator/prompts/og.txt` | aprobado en r1 (sí en semillas 3 y 4, «de las mejores», `docs/registros/contenido/r1-fondos.md`) |
| `examples/galivelop-image-generator/prompts/r2-palabras.txt` | r2, **elegida** (ahora `estilo.txt`). Misma escena de og; paleta en palabras |
| `examples/galivelop-image-generator/prompts/r2-hex.txt` | r2, descartada. Misma escena, colores en hex |
| `examples/galivelop-image-generator/prompts/r2-material.txt` | r2, descartada. Misma escena, paleta en materiales y luz (agua quieta de noche, cristal, amatista, vidrio esmerilado) |
| `examples/galivelop-image-generator/prompts/estilo.txt` | og: el estilo elegido en r2 | r3: el borrador (640×320, 4 pasos, 51 s) anticipa estilo y hueco, no el detalle; r4: og compuesto, contraste peor 16.49:1, paleta 72 % |
| `examples/galivelop-image-generator/prompts/r5-cuadrado.txt` | r5: generado y compuesto (`piloto/r5/galivelop-image-generator/intentos/cuadrado.png`), contraste 16.48:1, peor 15.42:1, paleta 74.87 %. Misma escena en cuadrado 1080×1080 (se genera a 1024×1024): marcos en la mitad inferior, mitad superior libre |
| `examples/galivelop-image-generator/prompts/r5-vertical.txt` | r5: generado y compuesto (`piloto/r5/galivelop-image-generator/intentos/vertical.png`), contraste 16.44:1, peor 16.28:1, paleta 79.11 %. Misma escena en vertical 1080×1350 (896×1152): marcos en la mitad inferior, mitad superior libre |
| `examples/galivelop-image-generator/prompts/r5-cabecera.txt` | r5: generado y compuesto (`piloto/r5/galivelop-image-generator/intentos/cabecera.png`), contraste 15.49:1, peor 15.33:1, paleta 75.16 %. Misma escena en cabecera 1500×500 (1536×512): marcos en la mitad derecha, mitad izquierda libre |

Plantilla para uno nuevo: `<formato y fondo> + <motivo en la zona de imagen> + <zona reservada, lisa> + Style: … Colours: deep
midnight navy, violet, soft lavender and white highlights. Mood: calm, focused, quietly creative. The image is completely
textless.`

## 9. Formatos y piezas

Perfiles (tabla del `README.md` de marcas): `social`, `og`, `avatar`, `icon`; `banner` solo si el Portal la presenta
**[P]**. Primera ronda: 1) logo elegido y avatar 512; 2) `social` 1280×640; 3) `og` 1200×630.

## 10. Fuentes

- Este repo `24d69c8`: `README.md` (qué es, estado, D-números), `GLOSSARY.md` (campo semántico), `docs/plan.md`
  «Estilos por proyecto» (acento, familia, metáforas, vetos, formatos y primera ronda),
  `examples/galivelop-image-generator/prompts/og.txt`, `docs/registros/contenido/r1-fondos.md` (veredicto).
- Portal-Galivelop `aa76b34`: `public/marca/gv-logo.svg` (baldosa), `Logo.tsx` (Sora 700, tracking −0,03 em), tema
  (`#06121c`, `#0c1d2b`, `#11283a`, `#1b3447`, `#eaf4fa`, `#9fb4c4`, `#f6fafd`, `#0a1a28`), vía
  `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md`.
- Sin dato en ningún repo (**[P]**): acento y sus tonos, lema y frases, monoespaciada, reglas del logo tras elegir.
