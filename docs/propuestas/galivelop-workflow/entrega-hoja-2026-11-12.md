# Entrega a Galivelop-workflow: su hoja de marca (2026-11-12)

Para la sesión del repo `Galivelop-workflow`. Desde `galivelop-image-generator` ese repo solo se lee: esta nota dice
**qué leer aquí, qué crear allí y qué se le puede generar**; el cambio lo hace su sesión. Leído en `origin/main`
`2e55d66` (2026-11-12, `v0.5.2`). La hoja: [`docs/marcas/galivelop-workflow/hoja.md`](../../marcas/galivelop-workflow/hoja.md)
de `galivelop-image-generator`, rama `hojas-repos`.

**En una línea:** Workflow sigue la identidad del Portal (papel, tinta y tipografías sin cambio) con su acento
`#3D6FD9`; el repo de Workflow no tiene hoy ningún archivo de marca (`git ls-tree -r origin/main` no lista `.svg`,
`.png`, `.css` ni `.ico`), y el logo nuevo **todavía no está generado**.

## Qué leer de aquí

| Qué | Dónde (`galivelop-image-generator`) | Para qué |
|---|---|---|
| Lo vigente de Workflow | `docs/marcas/galivelop-workflow/hoja.md`, bloques «Identidad vigente», «Interfaz», «Recursos» y «Familia Galivelop» | Acento y sus tonos, motivo, prompts, lo pendiente |
| Lo heredado | `docs/marcas/portal/hoja.md`, «Familia Galivelop: lo que heredan los productos» y «Decisiones de la persona (2026-11-12)» | Papel, tinta, tipografías, forma, lockup común, prohibidos |
| El cálculo del acento | `docs/marcas/galivelop-workflow/acento.py` (`python3 acento.py`, solo stdlib) | Reproduce los hex y los ratios |
| Voz, lema, ética y textos | La misma hoja, secciones 1, 2, 6 y 10 del histórico (siguen valiendo) | Salen del propio repo de Workflow |

Los valores que más se van a usar:

| Papel | Claro | Oscuro | Contraste |
|---|---|---|---|
| Papel / superficie | `#fbfcfd` / `#ffffff` | `#0d171e` / `#111f29` | heredado del Portal |
| Tinta / secundaria | `#13212b` / `#4a5c69` | `#e6eef3` / `#9fb2bf` | heredado del Portal |
| Acento (vivo y hondo: el mismo hex) | `#3d6fd9` | `#3d6fd9` | 4,57:1 sobre el papel claro; blanco encima 4,69:1; 3,86:1 sobre el papel oscuro (solo trazo, foco y punto) |
| Texto de acento y enlaces | `#3d6fd9` | `#487ce7` | 4,57:1 / 4,59:1 |
| Tinte | acento al 12 % | acento al 18 % | tinta encima 13,71:1 / 12,79:1 |

Tipografías: Big Shoulders Display 800 en mayúsculas (títulos), Literata (texto), JetBrains Mono (datos). Las tres, OFL.

## Qué crear en el repo de Workflow

| # | Qué | Dónde | Detalle |
|---|---|---|---|
| 1 | `docs/marca.md` | `docs/marca.md` (casa con `content`, `^docs/`, de `.claude/gw.json`: no pide revisión de código) | Corto y **sin copiar valores que puedan desfasarse**: dice que la fuente de verdad es `docs/marcas/galivelop-workflow/hoja.md` de `galivelop-image-generator` (con el commit leído), lista los archivos de `docs/marca/` con su origen, y apunta la tabla de valores de arriba. Si hay versión inglesa, `docs/en/` lleva la suya |
| 2 | Carpeta de logos | `docs/marca/` | Los SVG copiados de `docs/marcas/galivelop-workflow/logos/` **cuando existan los nuevos** (ver «Lo que hay hoy»): `galivelop-workflow.svg` (símbolo), `galivelop-workflow-lockup-h.svg`, `galivelop-workflow-lockup-v.svg`. Copia idéntica: no se editan allí |
| 3 | `README.md` y `README.es.md` con logo | cabecera de los dos (son `releaseDocs`) | El lockup con `<picture>` y `prefers-color-scheme`, para que el nombre (a `currentColor` en el SVG) salga en tinta `#13212b` sobre claro y `#e6eef3` sobre oscuro; GitHub no hereda `currentColor` en un `<img>`, así que hacen falta dos archivos (claro y oscuro), que salen de `gimg brand lockup --color`. Con el nombre de 18 letras el horizontal es muy ancho: se elige entre vertical y símbolo solo al verlo |
| 4 | Nota de paleta de las tarjetas | `.claude/gw/gw-media-content.md` (hoy no existe) | La línea `Palette:` de la hoja, «Recursos»: `--background: #fbfcfd; --surface: #ffffff; --border: #b9cbd6; --text: #13212b; --muted: #4a5c69; --accent: #3d6fd9; --accent-text: #ffffff; --good: #3f5a4b; --bad: #a3135f`. Sustituye a la propuesta del 2026-11-04 (`#0d1b2a`, `#38b6e8`). Es la nota **del repo**, no la plantilla (`skills/gw-media-content/note.md` l.15 la define como «CSS variable overrides») |
| 5 | Social preview | Ajustes del repo en GitHub (1280×640) | Cuando se genere; no es un archivo del repo |

**¿La marca viaja con lo que se instala? No (recomendación; lo decide la persona).** Workflow es una plantilla:
`apply.py` copia `scripts/`, las skills, los ganchos de git y el CI al proyecto que lo adopta (`docs/es/apply.md`
l.107-108). La marca de Workflow es del repo de Workflow, no de esos proyectos:

- Los archivos de marca van en `docs/marca.md`, `docs/marca/` y los `README`, **nunca** en `scripts/`, `skills/`,
  `templates/` ni `hooks/`. Su sesión confirma con `apply.py --help` que nada de `docs/` se copia.
- Las plantillas de `gw-media-content` (`skills/gw-media-content/template/media/source/*.html`) **se quedan con su
  paleta genérica**: `card.html` l.12 dice «override these to match the project» y cada proyecto pone la suya en su
  nota. La paleta de Workflow va solo en la nota del punto 4.
- Lo único que puede nombrar el flujo en un proyecto ajeno es texto (la cabecera «Galivelop-workflow v…» de los
  archivos generados), como hoy. Sin logo.

## Lo que hay hoy en `logos/` y por qué no se copia todavía

`docs/marcas/galivelop-workflow/logos/galivelop-workflow-{a,b,c,d}.svg` y sus `-lockup.svg` son de la identidad
anterior: baldosa con degradado y `rx` 30, nombre en Sora. No cumplen la regla de familia (cuadrado plano del acento,
chaflán de 28/128 arriba a la derecha, trazo de 12/128, sin degradado ni redondeo; lockup en Big Shoulders Display).
El icono que sí vale hoy es el de proyecto que el Portal ya publica (su recurso 23, q490: tres nodos encadenados, el
último con visto), en `public/proyectos/galivelop-workflow/icono.svg` del Portal.

## Qué se le puede generar (todo con gimg, en local)

| Pieza | Formato | Estado | Depende de |
|---|---|---|---|
| Símbolo: cuadrado `#3d6fd9` con chaflán y monograma en blanco | SVG; PNG 512 para avatar | Pendiente: prompt propuesto en la hoja | La persona decide el dibujo (monograma «GW», recomendado, o los nodos) |
| Símbolo en negativo y a una tinta | SVG | Sale del anterior, sin generar | El símbolo |
| Lockup horizontal y vertical, en claro y oscuro | SVG | Pendiente: órdenes en la hoja, «Familia Galivelop», punto 4 | El símbolo y el `.ttf` variable de Big Shoulders Display (no está en el equipo) |
| Social preview de GitHub | PNG 1280×640 | Pendiente | Perfil nuevo con Z-Image en `examples/galivelop-workflow/` |
| Cabecera del `README` (grabado: ruta de commits sobre la carta) | PNG o WebP 1600×500 | No pedida | Lo mismo |
| `og` de la ficha del Portal (recurso 24) | JPG 1200×630 | Pendiente | Lo pide el Portal |
| Serie de iconos propia (relevo, bitácora, revisión, rama protegida…) | SVG a `currentColor` | No pedida | Que Workflow diga qué iconos y dónde (el Management Center de la `1.0`) |
| Tarjetas de redes | — | **No las hace gimg**: las renderiza `gw-media-content-now` con la nota del punto 4 | — |

## Pendiente de la persona

Las seis dudas de la hoja («Dudas que decide la persona»), cada una con recomendación: 1) vivo y hondo son el mismo
hex; 2) monograma «GW» o nodos como símbolo; 3) el alga como acento secundario en la interfaz propia; 4) el ámbar
del testigo y los colores de los diagramas `gw-*.svg`; 5) la marca no viaja con lo instalado; 6) el nombre en
mayúsculas en el lockup. Hasta que se cierre la 2 no se genera el símbolo, y sin símbolo no hay lockup ni logo en el
`README`: los puntos 1 y 4 de «Qué crear» sí se pueden hacer ya.
