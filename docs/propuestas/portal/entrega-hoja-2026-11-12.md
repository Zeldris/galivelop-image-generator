# Entrega al Portal: desajustes entre su hoja y la nuestra (2026-11-12)

Para la sesión del repo `Portal-Galivelop`. Desde `galivelop-image-generator` ese repo solo se lee: aquí se dice **qué
cambia y dónde**; el cambio lo hace su sesión. **Todo se leyó en `7fc0357`** (rama `ccr-47f8fddd-o5ek6p`, «la hoja del
generador del 2026-11-12, aplicada»), y el Portal ya cita nuestra hoja en `2a9af6f`. Esta nota se escribió sobre `6574c4f`
y se ha corregido con lo que `7fc0357` ya aplica: cada cambio dice **aplicado en `7fc0357`** o **pendiente**. Las citas a
`docs/marca.md` son por sección y fila, no por línea (el Portal reorganizó el archivo). Nuestra hoja:
[`docs/marcas/portal/hoja.md`](../../marcas/portal/hoja.md), secciones «Interfaz del Portal», «Recursos» y «Familia
Galivelop». Acompaña a [`entrega-marca-2026-11-12.md`](entrega-marca-2026-11-12.md), que entrega las imágenes.

Los ratios son WCAG 2.x calculados sobre los hex de `src/estilos/global.css`, no medidos en pantalla.

**Resumen:** los cambios 1-17 están aplicados en `7fc0357`. Lo pendiente es lo que no depende del Portal (imágenes en cola:
portadas 6 definitivas, 10 rehecha, 25-30, versiones oscuras de 10, 18, 19, 27 y 28; logo 1 y 1b; 3, 4, 5, 23 de Tarkor y 24) y
volver a citar nuestra hoja en `docs/marca.md` cuando suba el commit de esta corrección (cambio 3).

## Cambios de texto en `docs/marca.md`

| # | Dónde (`docs/marca.md`) | Qué decía (`6574c4f`) | Qué cambia | Estado en `7fc0357` |
|---|---|---|---|---|
| 1 | «Cómo pedirlas», «El mar pone el dónde…» | Las excepciones son solo los dos barcos de papel (19 y 15 de Developer) | Añadir la tercera: las portadas 6, un motivo por estado (faro, boya, barco). Decisión de la persona del 2026-11-12; sustituye a la serie de tres faros | **Aplicado:** nombra las tres excepciones |
| 2 | «B. Portada y secciones», fila 6 | Describe la portada como «ventana de editor» | Describir faro (desarrollo), boya (diseño) y barco de papel (publicado) | **Aplicado:** la fila describe los tres motivos y dice «Sin ventana de editor». «Entregados», fila 6, mantiene los tres faros provisionales hasta que lleguen las portadas definitivas |
| 3 | «Cómo pedirlas» (primer párrafo) | Citaba nuestra hoja en `db9c364` | Citar el commit de `galivelop-image-generator` que traiga esta entrega | **Aplicado:** cita `2a9af6f` (rama `hojas-repos`). **Pendiente:** volver a citar cuando suba la corrección de esta nota |
| 4 | «Tipografía» | Tracking de los datos `.04em` | `0.06em` | **Aplicado:** `.06em` (`--datos-espaciado`; manda el código) |
| 5 | «Reglas», regla 3, y tabla de «Tokens» | Chaflán de 14 px «en fichas y botones» | Botones a 10 px y fila para `--chaflan-pequeno` | **Aplicado:** regla 3 con 10 px en botones y fila `--chaflan` / `--chaflan-grande` / `--chaflan-pequeno` (`global.css` l.27 y l.463-469) |
| 6 | Tabla de «Tokens» | No listaba `--fondo-alterno`, `--superficie-2`, `--texto-3`, `--enlace`, `--sombra`, `--reticula-paso` ni `--datos` | Añadir sus filas | **Aplicado:** están todas (`global.css` l.21, l.28, l.56, l.58, l.62-63, l.66, y l.91-101 en oscuro) |
| 7 | «Reglas», regla 10 | Sobre `--celeste`, «solo etiquetas grandes o el granito» | Sobre `--celeste`, solo la tinta | **Aplicado:** «sobre `--celeste` solo va la tinta» (blanco `2,78:1`; tinta `#13212b`, `5,91:1`) |
| 8 | «Cómo pedirlas», «Dudas que decidió la persona» | Las dudas 1 y 2 seguían listadas como abiertas | Marcarlas como aplicadas, o pedir el «sí» expreso de la persona | **Aplicado:** duda 1 «Aplicada», duda 2 «Cerrada (la persona, 2026-11-12)» y duda 3 «Reducida» |

## Cambios en código o recursos

| # | Dónde | Qué pasaba | Qué cambia | Estado en `7fc0357` |
|---|---|---|---|---|
| 9 | Icono de la línea «ia-local» (`src/pages/Inicio.tsx`) | Seguía con `Cpu` de lucide | Usar la serie 7 entera sin repetir (`entrega-marca-2026-11-12.md` l.22-27) | **Aplicado:** 7a `codigo.svg` en «ia-local»; 7b `papel-ventana.svg` (q651) en «Del prototipo al producto»; 7c `documento-check.svg` en información; 7d `compas.svg` en método; 7e `mundos.svg` en mundos (todas en `src/assets/iconos/`) |
| 10 | Recurso 12, separador (`docs/marca.md`, «B. Portada y secciones», fila 12) | Aprobado aquí (filete con rosa de ocho puntas en el centro, q564, versión transparente); en el Portal no tenía componente | Crear el componente que lo pinta, o cancelarlo como 11, 16, 20 y 21 | **Aplicado:** `src/components/Separador.tsx` con `public/marca/separador.webp`: en el inicio antes de «Próximamente» y de «Es para ti si…», en la ficha antes de «Avance», en `/novedades` entre meses y en las legales antes de «Otros textos legales»; en oscuro se invierte por CSS (`.separador`) |

## Pendiente de nuestra parte (no pide cambio al Portal)

- **Logo 1 y 1b:** `public/marca/gv-logo.svg` sigue siendo el prototipo (degradado `#2BB3EA → #0083C1`, `rx` 30), que
  no cumple las reglas 2 y 3 de `docs/marca.md`. Falta generarlo con gimg («A. Marca», fila 1: cuadrado de cerúleo plano,
  chaflán de 28/128, trazo de 12/128).
- **3, 4, 5 de «A. Marca» y 23 de Tarkor y 24:** sin generar («A. Marca», filas 3-5; «D. Por proyecto», filas 23 y 24).
- **Versión oscura de 10, 18, 19, 27 y 28:** en cola, una sola lista para toda la hoja (la duda 3 quedó «Reducida»); hoy 10 y 18
  se muestran enmarcadas en el tema oscuro («Entregados», párrafo tras la tabla).

## Acentos de producto (era «Pendiente de la persona»)

**Resuelto en `7fc0357`.** Los acentos de `src/data/productos/*.json` (l.5) son hoy: image-generator `#7C5CD6`, voice-generator
`#D9467A` (decidido por la persona el 2026-11-12; antes `#C9467A`, 4,41:1; `#D9467A` da 4,00:1 sobre el papel `#fbfcfd`),
developer `#0E9A93`, workflow `#3D6FD9` (antes `#1AA6DF`). El Portal calcula el hondo y el oscuro de cada acento con
`src/data/tonos.ts` (`estiloAcento`), con el método de nuestra hoja, y el test `src/data/tonos.test.ts` da los mismos hex
(voice `#ce3c71` / `#db487b`, developer `#16827c`).

## Decidido por la persona el 2026-11-12 (después de escribir lo anterior)

Detalle en `docs/marcas/portal/hoja.md`, «Familia Galivelop», «Decisiones de la persona (2026-11-12)».

| # | Dónde | Qué cambia | Estado en `7fc0357` |
|---|---|---|---|
| 11 | `src/data/productos/galivelop-workflow.json` l.5 (`#1AA6DF`) | Pasa a `#3D6FD9`, el de `src/data/proyectos/galivelop-workflow.json` l.7: es el acento que manda para workflow | **Aplicado** |
| 12 | `docs/marca.md`, «Cómo pedirlas», duda 2 | Cerrada: el acento del producto va donde el Portal usa el alga; papel, tinta y tipografías no cambian | **Aplicado** («Acento de cada proyecto» y duda 2 «Cerrada») |
| 13 | Donde el Portal use el acento de un producto para texto, enlaces o bloques con texto blanco | Usar el tono hondo (tema claro) o la variante oscura, no el hex vivo: el vivo solo marca puntos, foco y tinte | **Aplicado:** `--acento-proyecto` (vivo: filetes, bordes, puntos, barras, tinte), `--acento-texto` (hondo en claro, oscuro en oscuro) y `--acento-bloque` (hondo en los dos temas) |
| 14 | `src/data/productos/galivelop-voice-generator.json` l.5 (`#C9467A`) | Pasa a `#D9467A`, el vivo que usan la hoja de voice, el plan y `brand.palette` (la persona, 2026-11-12). Sobre papel da 4,00:1 (blanco encima 4,11); el texto va en el hondo `#ce3c71` (4,53; 4,66 con blanco) y en oscuro `#db487b` (4,51 sobre `#0d171e`) | **Aplicado** (también en `src/data/proximamente.json`) |

## Añadido el 2026-11-12 (tarde): toda la web en la línea de la marca

| # | Dónde | Qué cambia | Estado en `7fc0357` |
|---|---|---|---|
| 15 | Toda la web, también la página interna de cada proyecto | Colores, tipografías y reglas de nuestra hoja en todas las partes (sección «Alcance» de `docs/marcas/portal/hoja.md`). Solo el contenido que enseña cada proyecto (galerías, capturas, vídeos) puede salirse de la paleta, dentro de su contenedor y con `/* marca: permitido, contenido del proyecto */`; del proyecto, en el marco, solo entra su acento donde va el alga | **Aplicado:** sección «Alcance» de `docs/marca.md` |
| 16 | `src/estilos/marca.test.ts` | Que cubra todas las hojas de estilo de la web, también las de las páginas de proyecto | **Aplicado:** recorre todas las hojas `.css` de `src/` |
| 17 | Recursos 6, 10, 18, 19 y 25-30 | Ver «Recursos» de nuestra hoja: portadas 6 con un motivo por estado, 10 rehecha, piezas 25-30 nuevas y versiones oscuras de 10, 18, 19, 27 y 28 (en cola; llegan con la próxima entrega de imágenes). 11, 16, 20 y 21 siguen por CSS | **Aplicado en el texto:** «B. Portada y secciones» (6 y 10), «E. Pedidos del Portal del 2026-11-12» (25-30) y el párrafo de versiones oscuras. Las imágenes siguen **pendientes** (en cola) |

### Dónde van las piezas 9 y 25-30 (confirmado)

- **9a y 9b** (ramas, bombilla): solo en el inicio, en «Participa». La persona **rechazó** (2026-11-12, «queda mal») ponerlas
  encima del título de `/participa/unirse` y `/participa/proponer`; el Portal ya las quitó (`0d5aa12`). La 9a también va en
  «¿Quieres participar en…?» de la ficha, en los proyectos con colaboración abierta.
- **25** índice y títulos de la ficha de proyecto; **26** hitos de «Avance»; **27** avisos vacíos del muro y de novedades
  (sustituye a las isobatas tenues `.vacio-carta`); **28** errores de carga; **29** «¿Quieres participar en…?» de la ficha;
  **30** arriba de `/novedades`. Son los destinos que propone el Portal en `docs/marca.md`, «E. Pedidos del Portal del
  2026-11-12».
