# Biblia de estilo: galivelop-voice-generator

Herramienta del taller, sin identidad propia: **familia del Portal** con acento frambuesa **[P]**. Molde y reglas comunes
en [`../README.md`](../README.md). Datos de su repo (rama `claude/voces-f1`) en `ab1ff10`; de este, en `fd2ae53`; del
Portal, en `aa76b34`.

**Aprobada el 2026-11-04** (decisiones delegadas por la persona, `docs/records/decisiones-hojas-2026-11-04.md`): lo que sigue
marcado **[P]** es propuesta del agente aprobada por delegación. Campo a campo, en [`hoja.md`](hoja.md).

## 1. Esencia

- **Qué es:** «Generador de voces con IA local para desarrollo: un servicio por máquina que comparten varios proyectos»,
  con motor `qwentts.cpp` (`README.md`). Gemelo del de imágenes; diseña voces, pregenera frases y exporta paquetes de
  voces. No conoce el dominio (D3).
- **Lema [P]:** «Una voz, su huella, todas sus frases.»
- **Para quién:** proyectos del taller (Tarkor/WMF el primero) que necesitan voces de NPC sin servicio externo.
- **Valores y ética:** IA local, nada residente, el humano elige la toma. Las voces son **personas sintéticas** definidas
  por una referencia elegida (`GLOSSARY.md`): en imagen nunca se sugiere clonar a nadie.
- **Nunca se muestra:** rostros, bocas, labios, personas ni siluetas humanas; micrófonos, cascos o estudios de
  grabación; robots o cerebros; «magia» de IA; texto generado por el modelo.

## 2. Paleta

| Rol | Hex | Uso |
|---|---|---|
| Acento **[P]** | `#D9467A` | símbolo, nombre en el lockup, la toma elegida, enlaces sobre oscuro |
| Acento claro **[P]** | `#F6B1CA` | tomas no elegidas, halos, texto de acento sobre oscuro |
| Acento oscuro **[P]** | `#A62E5A` | final del degradado de la baldosa, acento sobre fondo claro |
| Fondo oscuro | `#06121c` | fondo de piezas (Portal) |
| Superficies | `#0c1d2b`, `#11283a` | tarjetas y paneles |
| Borde | `#1b3447` | filetes |
| Texto / texto 2 | `#eaf4fa` / `#9fb4c4` | sobre oscuro |
| Fondo claro / texto claro | `#f6fafd` / `#0a1a28` | pieza clara |
| Blanco | `#FFFFFF` | trazo del símbolo |

- **Pieza oscura (por defecto):** `#06121c` con rejilla de puntos y resplandor radial del acento (20-30 %); texto
  `#eaf4fa`, secundario `#9fb4c4`, acento `#F6B1CA`. Velo `#06121c` a 0 en `og` y a 0,3 en `square`, `portrait` y `header`.
- **Pieza clara:** `#f6fafd`, texto `#0a1a28`, acento `#A62E5A`.
- **Sobre imagen:** texto `#eaf4fa` (el de las piezas compuestas de r4-r5) en la zona reservada; el logo siempre en su baldosa.
- **`brand.palette`** de la configuración: `#06121c`, `#F6B1CA`, `#D9467A`, `#ffffff`, `#eaf4fa` y `#A62E5A`.
- **Prohibidos:** el celeste del Portal como acento de la herramienta; rojo puro o magenta neón; negro `#000`; acento
  sobre acento. El violeta `#8B5CF6` es del generador de imágenes: no se mezclan.

## 3. Tipografía

- **Sora 700** en títulos y en el nombre del lockup, tracking −0,03 em (Portal). Titular siempre a 700.
- **Inter 400** en el subtítulo, con opacidad 0,82 (como salió en r4-r5); el 500 solo en interfaz. Misma regla en toda la familia.
- **Monoespaciada del sistema [P]** para claves (`orcos/guerrero-1`) y órdenes.
- Wordmark: `galivelop-voice-generator` en minúsculas, con guiones, de una pieza y un solo color.

## 4. Logo

Propuestas en `logos/` (símbolo `galivelop-voice-generator-<letra>.svg` y su `-lockup.svg`), todas en la baldosa de la
familia (128×128, `rx` 30, trazo blanco 12, degradado `#D9467A → #A62E5A`):

- **a. Onda que se enrosca:** una onda entra por la izquierda y se cierra en espiral: la huella de la voz.
- **b. Tomas:** cinco barras de onda; la más alta y blanca es la toma elegida, las demás en `#F6B1CA`.
- **c. Huella de anillos:** un punto y dos anillos partidos en segmentos, a la vez huella y onda que se expande.
- **d. Una onda en la baldosa:** una sola onda sinusoidal blanca que atraviesa la baldosa.

**Elegido (agente, delegado):** a — la más propia (la huella de la voz); la d es una onda genérica.

Tras elegir **[P]**:

- Variantes: la baldosa es la misma sobre claro y oscuro. El nombre del lockup, `#D9467A` sobre oscuro y `#A62E5A`
  sobre claro.
- Margen libre: un cuarto del lado de la baldosa. Tamaño mínimo: símbolo 16 px; lockup 24 px de alto, y por debajo
  solo el símbolo.
- Símbolo y wordmark: en horizontal, nombre a la derecha a 28/128 de separación; nunca el nombre debajo.
- Prohibido: cambiar el `rx` o el trazo, sacar el dibujo de la baldosa, rotarlo, recolorearlo, añadirle sombra o brillo,
  convertir la onda en boca o en micrófono.

## 5. Forma e iconografía

- Radios: baldosa `rx` 30/128 (23 %); en interfaz, 18 y 10 px (Portal).
- Línea: trazo 12/128 con remates redondos; a 24 px, iconos de 2 px.
- Lenguaje: ondas, barras, anillos y espirales; curvas continuas, plano, sin perspectiva ni sombra dura; una sola toma
  encendida.

## 6. Voz y frases

- **Tono:** técnico, sobrio y honesto con el estado real («aún no genera voces»); nunca vende.
- **Campo semántico** (`GLOSSARY.md`): voz, referencia, ficha de diseño, huella, frase, intento (la toma), candidata,
  elegida, desfasada, cadena de efectos, paquete de voces, cola, candado de la máquina. Evitar: clonar, hablante,
  timbre, embedding, clip, diálogo, «dar vida».
- **Lema [P]:** «Una voz, su huella, todas sus frases.»
- **Subtítulo del `og` [P]:** «Voces con IA local: un servicio por máquina, para varios proyectos.» (67 caracteres; el
  límite orientativo es 70).
- **Variaciones [P]:** «Suena igual en cada frase.» · «Voces sintéticas, elegidas toma a toma.» · «IA local: nada sale
  de tu equipo.»
- **Ganchos [P]:** «Cinco tomas, una elegida.» · «La referencia manda; el motor puede cambiar.»
- **Cierres [P]:** «Sin instalar nada.» · «Tú eliges la toma.»

## 7. Estilo de imagen (FLUX)

- **Sí:** fondo azul noche profundo con rejilla de puntos; una cinta de luz con forma de onda que se enrosca en anillos
  finos; líneas precisas y luminosas, brillo suave, degradados lisos; frambuesa, rosa suave y blanco.
- **No:** micrófonos, cascos, altavoces, estudios, bocas, caras, personas, cantantes, robots, cerebros, texto.
- **Motivos:** la onda que se enrosca (la huella), las barras de tomas con una encendida, los anillos concéntricos.
- **Palabras vetadas:** microphone, mic, headphones, speaker, studio, mouth, lips, face, person, singer, voice actor,
  human, robot, brain, sparkle, magic, text, letters, logo.
- **Zona reservada para texto** (una por perfil, la misma en prompt, plantilla y medida): `izquierda 1/2`, lisa y desenfocada,
  en `og`, `social` y `header`; `arriba 1/2` en `square` y `portrait` (lo que pidieron y midieron los prompts de r5).

## 8. Prompts

| Archivo | Estado |
|---|---|
| `examples/galivelop-voice-generator/prompts/og.txt` (este repo) | aprobado en r1 (sí en semillas 3 y 4, `docs/records/contenido/r1-fondos.md`). **Histórico**: lleva «shaped like a sound wave» (comparación con «like»), superado por `estilo.txt` |
| `examples/galivelop-voice-generator/prompts/r2-palabras.txt` | r2, **elegida** (ahora `estilo.txt`). Misma escena de og (sin el «shaped like»); paleta en palabras |
| `examples/galivelop-voice-generator/prompts/r2-hex.txt` | r2, descartada. Misma escena, colores en hex |
| `examples/galivelop-voice-generator/prompts/r2-material.txt` | r2, descartada. Misma escena, paleta en materiales y luz (terciopelo azul, cristal frambuesa, cuarzo rosa) |
| `examples/galivelop-voice-generator/prompts/estilo.txt` | og: el estilo elegido en r2. r3: el borrador (640×320, 4 pasos, 51 s) anticipa estilo y hueco, no el detalle; r4: og compuesto, contraste peor 16.34:1, paleta 70 % (sin `#eaf4fa` en `brand.palette`; ya está, falta volver a medir). 118 palabras: el mínimo de 120 de la plantilla es un aviso |
| `examples/galivelop-voice-generator/prompts/r5-cuadrado.txt` | r5: generado y compuesto (`piloto/r5/galivelop-voice-generator/intentos/cuadrado.png`), contraste 15.46:1, peor 14.6:1, paleta 79.98 %. Misma escena en cuadrado 1080×1080 (se genera a 1024×1024): onda y anillos en la mitad inferior, mitad superior libre |
| `examples/galivelop-voice-generator/prompts/r5-vertical.txt` | r5: generado y compuesto (`piloto/r5/galivelop-voice-generator/intentos/vertical.png`), contraste 15.89:1, peor 15.66:1, paleta 80.51 %. Misma escena en vertical 1080×1350 (896×1152): onda y anillos en la mitad inferior, mitad superior libre |
| `examples/galivelop-voice-generator/prompts/r5-cabecera.txt` | r5: generado y compuesto (`piloto/r5/galivelop-voice-generator/intentos/cabecera.png`), contraste 15.07:1, peor 14.45:1, paleta 74.95 %. Misma escena en cabecera 1500×500 (1536×512): onda en la mitad derecha, mitad izquierda libre |

Plantilla para uno nuevo: `<formato y fondo> + <motivo de onda en la zona de imagen> + <zona reservada, lisa> + Style: …
Colours: deep midnight navy, raspberry pink, soft rose and white highlights. Mood: calm, warm, attentive. The image is
completely textless.`

## 9. Formatos y piezas

Perfiles (tabla del `README.md` de marcas): `social`, `og`, `avatar`, `icon`; `banner` solo si el Portal la presenta
**[P]**. Primera ronda: 1) logo elegido y avatar 512; 2) `social` 1280×640; 3) `og` 1200×630.

En la configuración (`examples/galivelop-voice-generator/galivelop-images.json`): `og` 1280×640 → 1200×630 (con borrador a
la mitad y 4 pasos), `social` 1280×640, `square` 1024×1024 → 1080×1080, `portrait` 896×1152 → 1080×1350 y `header`
1536×512 → 1500×500; los tres últimos son las piezas de r5 (`cuadrado`, `vertical`, `cabecera`). `avatar` 512 (logo
rasterizado) lo hace `piezas.py`.

## 10. Fuentes

- galivelop-voice-generator `ab1ff10` (`claude/voces-f1`): `README.md` (qué es, motor, D3), `GLOSSARY.md` (voz,
  referencia, huella, toma, cadena de efectos, paquete de voces). Allí no hay ningún dato visual.
- Este repo `fd2ae53`: `docs/plan.md` «Estilos por proyecto» (acento, familia, metáfora, vetos, formatos y primera
  ronda), `examples/galivelop-voice-generator/prompts/og.txt`, `docs/records/contenido/r1-fondos.md` (veredicto),
  `docs/records/lectura-2026-10-26-tarkor-y-marcas.md` sección 3 (límites: nada que sugiera clonar).
- Portal-Galivelop `aa76b34`: `public/marca/gv-logo.svg` (baldosa), `Logo.tsx` (Sora 700), tema oscuro y claro, vía la
  misma lectura.
- Sin dato en ningún repo (**[P]**): acento y sus tonos, lema y frases, monoespaciada, reglas del logo tras elegir.
