# Entrega al Portal: desajustes entre su hoja y la nuestra (2026-11-12)

Para la sesión del repo `Portal-Galivelop`. Desde `galivelop-image-generator` ese repo solo se lee: aquí se dice **qué
cambia y dónde**; el cambio lo hace su sesión. Leído en la rama `ccr-47f8fddd-o5ek6p` (`6574c4f`, 2026-11-12, la más
nueva) y en `main` (`e16500f`). Nuestra hoja: [`docs/marcas/portal/hoja.md`](../../marcas/portal/hoja.md), secciones
«Interfaz del Portal», «Recursos» y «Familia Galivelop». Acompaña a
[`entrega-marca-2026-11-12.md`](entrega-marca-2026-11-12.md), que entrega las imágenes.

Los ratios son WCAG 2.x calculados sobre los hex de `src/estilos/global.css`, no medidos en pantalla.

## Cambios de texto en `docs/marca.md`

| # | Dónde (`6574c4f`) | Qué dice hoy | Qué cambia | Por qué |
|---|---|---|---|---|
| 1 | l.147-151, «Mar y tecnología» | Las excepciones son solo los dos barcos de papel (19 y 15 de Developer) | Añadir la tercera: las portadas 6, un motivo por estado (faro, boya, barco) | Decisión de la persona del 2026-11-12; sustituye a la serie de tres faros |
| 2 | l.240, tabla B, fila 6 | Describe la portada como «ventana de editor» | Describir faro (desarrollo), boya (diseño) y barco de papel (publicado) | La fila quedó de antes de la aprobación |
| 3 | l.142-145 | Cita nuestra hoja en `db9c364` | Citar el commit de `galivelop-image-generator` que traiga esta entrega | La hoja cambió: tokens, recursos y familia |
| 4 | l.86 | Tracking de los datos `.04em` | `0.06em` | `src/estilos/global.css` l.22 (`--datos-espaciado: 0.06em`); manda el código |
| 5 | l.25-26 (regla 3) y tabla de tokens l.50-70 | Chaflán de 14 px «en fichas y botones» | Botones a 10 px y fila para `--chaflan-pequeno` | `global.css` l.27 y l.444-450 |
| 6 | Tabla de tokens l.50-70 | No lista `--fondo-alterno`, `--superficie-2`, `--texto-3`, `--enlace`, `--sombra`, `--reticula-paso` ni `--datos` | Añadir sus filas | Están en `global.css` l.21, l.28, l.56, l.58, l.62-63, l.66 (y l.91-101 en oscuro) |
| 7 | l.38-39 (regla 10) | Sobre `--celeste`, «solo etiquetas grandes o el granito» | Sobre `--celeste`, solo la tinta | Blanco sobre `#1aa6df` da 2,78:1 (no llega al 3:1 de texto grande); la tinta `#13212b`, 5,91:1 |
| 8 | l.211-220, «Dudas que decide la persona» | Las dudas 1 y 2 siguen listadas como abiertas | Marcarlas como aplicadas, o pedir el «sí» expreso de la persona | La hoja ya las aplica (l.152-156 y l.268) |

## Cambios en código o recursos

| # | Dónde | Qué pasa | Qué cambia |
|---|---|---|---|
| 9 | Icono de la línea «ia-local» (`docs/marca.md` l.130) | Sigue con `Cpu` de lucide; el 7b entregado (q560) no se usa | Usar el 7b, o decir por qué no y pedir otro: una serie se usa entera (`entrega-marca-2026-11-12.md` l.22-27) |
| 10 | Recurso 12, separador (`docs/marca.md` l.246) | Aprobado aquí (q564, versión transparente); en el Portal no tiene componente | Crear el componente que lo pinta, o cancelarlo como 11, 16, 20 y 21 |

## Pendiente de nuestra parte (no pide cambio al Portal)

- **Logo 1 y 1b:** `public/marca/gv-logo.svg` sigue siendo el prototipo (degradado `#2BB3EA → #0083C1`, `rx` 30), que
  no cumple las reglas 2 y 3 de `docs/marca.md`. Falta generarlo con gimg (l.229: cuadrado de cerúleo plano, chaflán de
  28/128, trazo de 12/128).
- **3, 4, 5, 23 de Tarkor y 24:** sin generar (l.232-234, l.267-268).
- **Versión oscura de 18 y 19:** la duda 3 sigue abierta (l.217-218); hoy 10 y 18 se muestran enmarcadas (l.137-138).

## Pendiente de la persona

Los acentos de producto de `src/data/productos/*.json` l.5 son un solo hex cada uno y el Portal usa dos tonos de su
acento (vivo y hondo). Sobre el papel `#fbfcfd`: image-generator `#7C5CD6` 4,69:1, voice-generator `#C9467A` 4,41:1 (decidido después: `#D9467A`, 4,00:1; cambio 14),
developer `#0E9A93` 3,37:1, workflow `#1AA6DF` 2,70:1. Solo el primero llega a 4,5:1. Además, workflow tiene otro
acento en `src/data/proyectos/galivelop-workflow.json` l.7 (`#3D6FD9`, 4,57:1). El segundo tono de cada acento, su
variante oscura y cuál de los dos de workflow manda los decide la persona; aquí no se propone ningún hex.

## Decidido por la persona el 2026-11-12 (después de escribir lo anterior)

Detalle en `docs/marcas/portal/hoja.md`, «Familia Galivelop», «Decisiones de la persona (2026-11-12)».

| # | Dónde | Qué cambia |
|---|---|---|
| 11 | `src/data/productos/galivelop-workflow.json` l.5 (`#1AA6DF`) | Pasa a `#3D6FD9`, el de `src/data/proyectos/galivelop-workflow.json` l.7: es el acento que manda para workflow |
| 12 | `docs/marca.md` l.215-216 (duda 2) | Cerrada: el acento del producto va donde el Portal usa el alga; papel, tinta y tipografías no cambian |
| 13 | Donde el Portal use el acento de un producto para texto, enlaces o bloques con texto blanco | Usar el tono hondo (tema claro) o la variante oscura que calcule la hoja de cada producto, no el hex vivo: el vivo solo marca puntos, foco y tinte |
| 14 | `src/data/productos/galivelop-voice-generator.json` l.5 (`#C9467A`) | Pasa a `#D9467A`, el vivo que usan la hoja de voice, el plan y `brand.palette`: **decidido por la persona (2026-11-12)**. Sobre papel da 4,00:1 (blanco encima 4,11); el texto va en el hondo `#ce3c71` (4,53; 4,66 con blanco) y en oscuro `#db487b` (4,51 sobre `#0d171e`) |

## Añadido el 2026-11-12 (tarde): toda la web en la línea de la marca

| # | Dónde | Qué cambia |
|---|---|---|
| 15 | Toda la web, también la página interna de cada proyecto | Colores, tipografías y reglas de nuestra hoja en todas las partes (sección «Alcance» de `docs/marcas/portal/hoja.md`). Solo el contenido que enseña cada proyecto (galerías, capturas, vídeos) puede salirse de la paleta, dentro de su contenedor y con `/* marca: permitido, contenido del proyecto */`; del proyecto, en el marco, solo entra su acento donde va el alga |
| 16 | `src/estilos/marca.test.ts` | Que cubra todas las hojas de estilo de la web, también las de las páginas de proyecto |
| 17 | Recursos 6, 10, 18, 19 y 25-30 | Ver «Recursos» de nuestra hoja: portadas 6 con un motivo por estado, 10 rehecha, piezas 25-30 nuevas y versiones oscuras de 10, 18, 19, 27 y 28 (en cola; llegan con la próxima entrega de imágenes). 11, 16, 20 y 21 siguen por CSS |
