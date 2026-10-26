# Biblia de estilo: galivelop-voice-generator

Herramienta del taller, sin identidad propia: **familia del Portal** con acento frambuesa **[P]**. Molde y reglas comunes
en [`../README.md`](../README.md). Datos de su repo (rama `claude/voces-f1`) en `ab1ff10`; de este, en `24d69c8`; del
Portal, en `aa76b34`.

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
  `#eaf4fa`, secundario `#9fb4c4`, acento `#F6B1CA`.
- **Pieza clara:** `#f6fafd`, texto `#0a1a28`, acento `#A62E5A`.
- **Sobre imagen:** texto blanco en la zona reservada; el logo siempre en su baldosa.
- **Prohibidos:** el celeste del Portal como acento de la herramienta; rojo puro o magenta neón; negro `#000`; acento
  sobre acento. El violeta `#8B5CF6` es del generador de imágenes: no se mezclan.

## 3. Tipografía

- **Sora 700** en títulos y en el nombre del lockup, tracking −0,03 em (Portal).
- **Inter 400/500** en texto.
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
- **Zona reservada para texto:** la mitad izquierda, lisa y desenfocada (`og`, `social`); en `square` **[P]**, el
  tercio superior.

## 8. Prompts

| Archivo | Estado |
|---|---|
| `examples/galivelop-voice-generator/prompts/og.txt` (este repo) | aprobado en r1 (sí en semillas 3 y 4, `docs/registros/contenido/r1-fondos.md`) |
| `examples/galivelop-voice-generator/prompts/r2-palabras.txt` | r2, **elegida** (ahora `estilo.txt`). Misma escena de og (sin el «shaped like»); paleta en palabras |
| `examples/galivelop-voice-generator/prompts/r2-hex.txt` | r2, descartada. Misma escena, colores en hex |
| `examples/galivelop-voice-generator/prompts/r2-material.txt` | r2, descartada. Misma escena, paleta en materiales y luz (terciopelo azul, cristal frambuesa, cuarzo rosa) |

Plantilla para uno nuevo: `<formato y fondo> + <motivo de onda en la zona de imagen> + <zona reservada, lisa> + Style: …
Colours: deep midnight navy, raspberry pink, soft rose and white highlights. Mood: calm, warm, attentive. The image is
completely textless.`

## 9. Formatos y piezas

Perfiles (tabla del `README.md` de marcas): `social`, `og`, `avatar`, `icon`; `banner` solo si el Portal la presenta
**[P]**. Primera ronda: 1) logo elegido y avatar 512; 2) `social` 1280×640; 3) `og` 1200×630.

## 10. Fuentes

- galivelop-voice-generator `ab1ff10` (`claude/voces-f1`): `README.md` (qué es, motor, D3), `GLOSSARY.md` (voz,
  referencia, huella, toma, cadena de efectos, paquete de voces). Allí no hay ningún dato visual.
- Este repo `24d69c8`: `docs/plan.md` «Estilos por proyecto» (acento, familia, metáfora, vetos, formatos y primera
  ronda), `examples/galivelop-voice-generator/prompts/og.txt`, `docs/registros/contenido/r1-fondos.md` (veredicto),
  `docs/registros/lectura-2026-10-26-tarkor-y-marcas.md` sección 3 (límites: nada que sugiera clonar).
- Portal-Galivelop `aa76b34`: `public/marca/gv-logo.svg` (baldosa), `Logo.tsx` (Sora 700), tema oscuro y claro, vía la
  misma lectura.
- Sin dato en ningún repo (**[P]**): acento y sus tonos, lema y frases, monoespaciada, reglas del logo tras elegir.
