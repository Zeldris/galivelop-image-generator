# Portal Galivelop: recursos de imagen de marca

Fuente de verdad: `docs/marca.md` del repo Portal-Galivelop, sección «Recursos de imagen para el generador»
(commit `08c7fe5` de `origin/main`). Aquí solo viven los pedidos; la hoja manda en prompts, medidas y destinos.
Sustituye a la identidad anterior (fondo oscuro, Sora/Inter, `og` con títulos compuestos): ninguna imagen lleva texto.

- `prompts/estilo.txt`: bloque de estilo común, literal. Cada pedido es el prompt de la hoja + ese bloque.
- `galivelop-images.json`: paleta nueva y un perfil por tamaño de entrega (modelo `flux2-klein-4b-q8`, euler, cfg 1.0,
  6 pasos, borrador a 0,5 y 4 pasos). Generación múltiplo de 64 y ≤ 1 MP (Deck), con la proporción de la entrega.
- Todos los pedidos: `seed` 1 y `count` 4 (misma semilla en serie).
- El esquema de pedido no tiene prompt negativo: el de la hoja (`text, letters, watermark, gradient, glow, bokeh,
  rounded corners, 3d, photo, realistic water, waves, seagulls, flag, people`) no se aplica; queda dicho en el bloque común.

## No salen de aquí

- **#2 isobatas**: datos EMODnet + `gdal_contour`, no es del generador.
- **#22 textura de papel** (opcional): no se genera aquí.

## Pedidos

| # | Pedido | Perfil | Generación | Entrega | Destino en el Portal |
|---|---|---|---|---|---|
| 1 | `orders/marca/01-logo.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/gv-logo.svg`, `gv-logo-512.png`, favicon |
| 1b | `orders/marca/01b-logo-negativo.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/gv-logo-negativo.svg` |
| 3 | `orders/marca/03-portada-social.json` | `social` | 1344×704 | 1200×630 | `public/marca/galivelop-portal.jpg` |
| 4 | `orders/marca/04-rosa-vientos.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/rosa-vientos.svg` |
| 5 | `orders/marca/05-sello.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/sello.svg` |
| 6 | `orders/marca/06-portada-desarrollo.json` | `portada` | 1344×768 | 1600×900 | `public/proyectos/<slug>/portada.webp` |
| 6 | `orders/marca/06-portada-diseno.json` | `portada` | 1344×768 | 1600×900 | ídem |
| 6 | `orders/marca/06-portada-publicado.json` | `portada` | 1344×768 | 1600×900 | ídem |
| 7 | `orders/marca/07-iconos-lineas.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/iconos/*.svg` |
| 8 | `orders/marca/08-iconos-valores.json` | `cuadrado` | 1024×1024 | 1024×1024 | ídem |
| 9 | `orders/marca/09-iconos-participacion.json` | `hoja3` | 1536×512 | 1536×512 | ídem |
| 10 | `orders/marca/10-como-funciona.json` | `panoramica` | 1536×576 | 1600×600 | `public/marca/*.webp`, `/unirse` |
| 11 | `orders/marca/11-fondo-para-ti.json` | `fondo` | 1024×1024 | 1200×1200 | `public/marca/*.webp`, `/unirse` |
| 12 | `orders/marca/12-separador.json` | `separador` | 1536×128 | 1200×100 | `public/marca/*.svg` |
| 13 | `orders/marca/13-cabecera-productos.json` | `cabecera` | 1664×512 | 1600×500 | `/productos` |
| 14 | `orders/marca/14-icono-implantacion.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/iconos/*.svg` |
| 15 | `orders/marca/15-proximamente-developer.json` | `tarjeta` | 1344×768 | 1200×675 | `TarjetaProxima` |
| 15 | `orders/marca/15-proximamente-voz.json` | `tarjeta` | 1344×768 | 1200×675 | `TarjetaProxima` |
| 16 | `orders/marca/16-cabecera-muro.json` | `muro` | 1792×448 | 1600×400 | `/muro` |
| 17 | `orders/marca/17-marco-retrato.json` | `cuadrado` | 1024×1024 | 1024×1024 | `public/marca/*.svg`, `/equipo` |
| 18 | `orders/marca/18-404.json` | `ilustracion` | 1152×768 | 1200×800 | `NoEncontrado.tsx` |
| 19 | `orders/marca/19-enviado.json` | `formulario` | 1024×768 | 800×600 | `form.listo` |
| 20 | `orders/marca/20-cabecera-legal.json` | `legal` | 1920×128 | 1200×80 | `public/marca/*.svg`, páginas legales |
| 21 | `orders/marca/21-patron-pie.json` | `patron` | 1792×448 | 1200×300 | `Pie.tsx` |
| 23 | `orders/marca/23-icono-tarkor.json` | `icono` | 1024×1024 | 512×512 | `public/proyectos/tarkor/icono.png` |
| 23 | `orders/marca/23-icono-workflow.json` | `icono` | 1024×1024 | 512×512 | `public/proyectos/galivelop-workflow/icono.png` |

## Pendientes

- **Transparencia y SVG**: #1, #1b, #4, #5, #7-#9, #12, #14, #17 y #20 piden PNG transparente y vectorizado a SVG;
  gimg aún no lo hace (salen sobre fondo opaco).
- **#12 y #20 (tiras finas)**: se generan más altas (`separador` 1536×128 → 1200×100; `legal` 1920×128 → 1200×80) y
  falta recortar/vectorizar a 1200×24 y 1200×80. #12 pide 50:1 y el modelo no da tiras tan finas.
- **Versión oscura** de lo que va sobre papel (#10, #11, #16, #18, #19, #1b…): líneas `#e6eef3` sobre `#0d171e`, o SVG coloreado por CSS.
- **#24 `og` por proyecto**: sin pedidos hasta saber el motivo de cada proyecto (mismo prompt que #3, con el motivo en vez de la rosa de los vientos; perfil `social`).
- #1/#1b piden chaflán de 28/128 y trazo de 12/128 exactos: se afinan al vectorizar.
- Referencia: la hoja pide pasar la portada social (#3) como referencia al resto; falta elegir la imagen aprobada.
- **Desvío del bloque común de la hoja (2026-11-10):** en la tanda 1, «sky blue #0072a8» dio `#1aa6df` (70 % de los píxeles, 0 % de `#0072a8`) y «45-degree cut corners» puso marcos y esquinas blancas en 3 de 4. «deep ocean blue» dio marino (`#13212b`, 64 %); aquí se pide «medium cerulean ocean blue #0072a8» y «full-bleed edge to edge, no border, no frame»; el chaflán de iconos y tarjetas va por CSS o al vectorizar.
