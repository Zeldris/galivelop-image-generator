# Entrega de la hoja de galivelop-developer (2026-11-12)

Para la sesión de **galivelop-developer**. Desde aquí no se toca ese repo: esto dice qué leer de este, qué crear allí y
qué piezas se le pueden generar. Leído de developer: `main` `70b0396` (2026-10-25, F0 cerrada), con `git show`, sin
modificar nada. La hoja de este repo citaba `8fa309c` (rama `claude/f1-instalacion`, por delante de `main`); entre los
dos no cambia nada de lo que la hoja usa (`README.md`, `GLOSSARY.md`, `docs/adr/`, `.claude/gw.json` son idénticos).

Lo que cambia: por pedido de la persona (2026-11-12), los productos Galivelop siguen los estilos del Portal con su
color, manteniendo la relación entre aspectos. La identidad anterior de developer (`#06121c`, Sora/Inter, `#2BB3A3`,
baldosa con degradado) pasa a histórico.

## Qué leer de aquí

| Qué | Dónde (repo galivelop-image-generator) | Para qué |
|---|---|---|
| Hoja de developer, los cuatro bloques vigentes | `docs/marcas/galivelop-developer/hoja.md`: «Identidad vigente», «Interfaz», «Recursos», «Familia Galivelop: cómo la cumple esta hoja» | Lo propio: acento, motivo, dudas abiertas, qué falta |
| Hoja del Portal | `docs/marcas/portal/hoja.md`: «Identidad vigente», «Interfaz del Portal: tokens y reglas», «Familia Galivelop: lo que heredan los productos», «Decisiones de la persona (2026-11-12)» | Todo lo heredado (papel, tinta, tipografías, forma, registros de dibujo, reglas de prompt): la hoja de developer no repite esos valores |
| Cálculo de los tonos | `docs/marcas/galivelop-developer/tonos.py`; `python3 docs/marcas/galivelop-developer/tonos.py '#0E9A93'` | Reproducir hondo, variante oscura, tintes y ratios |
| Voz | `docs/marcas/galivelop-developer/hoja.md` secciones 1, 2 y 10; `biblia.md` §1 y §6 | Propósito, tono, ética, frases: siguen vigentes |
| Histórico | secciones 0-15 de la hoja, el resto de `biblia.md`, `docs/marcas/galivelop-developer/logos/` | Solo consulta: **no se siguen ni se copian** |

Los valores propios, en corto (fuente: Portal `6574c4f` `src/data/productos/galivelop-developer.json` l.5 para el vivo;
`tonos.py` para lo demás):

| Papel | Hex | Contraste |
|---|---|---|
| Acento vivo (foco, punto de estado; los dos temas) | `#0e9a93` | papel claro 3,37 (no es texto en claro); tinta `#13212b` encima 4,74; sobre `#0d171e` 5,23; **nunca blanco encima** (3,46) |
| Acento hondo (bloques, enlaces en claro, cuadrado del logo) | `#16827c` | sobre `#fbfcfd` 4,52; blanco encima 4,65; **encima solo blanco** |
| Enlace en oscuro | `#0e9a93` (el vivo) | 5,23 sobre `#0d171e` |
| Tinte | vivo al 12 % (`#dff0f0`) / 18 % (`#0d2f33`) | tinta encima 13,95 / 12,16 |

## Qué crear en su repo

Hoy no hay nada visual en `main` `70b0396` (ni SVG, PNG, CSS, HTML; sin licencia, `README.md` l.52). Nada de esto
urge: `gdev` es una orden de terminal.

| # | Dónde | Hoy | Cambio | Por qué |
|---|---|---|---|---|
| 1 | `docs/marca.md` (nuevo) | No existe | Una página corta que **remita** a `docs/marcas/galivelop-developer/hoja.md` de galivelop-image-generator con su commit, y diga: identidad heredada del Portal; acento `#0e9a93` / `#16827c`; ninguna imagen lleva texto; todo gráfico nace de `gimg`. Sin copiar tablas | Un solo sitio que mantener; la hoja canónica vive aquí |
| 2 | `assets/` o `docs/assets/` (nuevo, cuando exista el logo) | No existe | Copiar los SVG del logo y de los lockups **nuevos**, tal como salgan de `gimg brand`. **No copiar** los de `logos/` de aquí: son de la identidad anterior (degradado, `rx` 30, Sora, `#2BB3A3`) | Regla de logo de la familia: cuadrado plano del hondo, chaflán 28/128, trazo 12/128 |
| 3 | Tokens CSS (solo si llega a tener web o documentación con estilo) | No hay interfaz | Los tokens del Portal sin cambio (`--papel`, `--tinta`, `--filete`, `--reticula`, `--chaflan*`…) más los propios **[P]**: `--acento: #0e9a93`, `--acento-hondo: #16827c`, `--enlace` (`#16827c` claro / `#0e9a93` oscuro), `--tinte` (12 % / 18 % del vivo) | Hoja, «Interfaz de galivelop-developer» |
| 4 | `.claude/gw/gw-media-content.md`, línea `Palette:` (cuando actualice el flujo: `main` lleva 0.3.0, `.claude/gw.json` l.3; la rama `claude/gw-update-0.5.1` `82bb114`, 0.5.1) | No existe | fondo `#fbfcfd`, superficie `#ffffff`, borde `#b9cbd6`, texto `#13212b`, apagado `#4a5c69`, acento `#16827c`, texto sobre acento `#ffffff` | Los valores heredados son los de `docs/marcas/portal/hoja.md` (tokens); el mapeo de la sección 11 de la hoja es de la identidad anterior |
| 5 | `README.md` / `README.en.md` | Sin imagen | Nada hasta que exista el lockup; entonces, el lockup horizontal en `currentColor` arriba. Sin «open source» ni «MIT» mientras no haya licencia | l.52; hoja, «Prohibido» |

En el **Portal** no hay nada que cambiar por esta hoja: ya publica `#0E9A93` y la tarjeta 15. Solo cuenta lo que su
propia entrega ya dice: texto y bloques del producto, con el hondo `#16827c`, no con el vivo.

## Qué piezas se le pueden generar

Todo **PROPUESTA**: nada se ha generado para esta entrega. Sale de `gimg` en local, con Z-Image (`zimage-turbo-q6`, 8
pasos, cfg 1.0) y los perfiles de `examples/portal/galivelop-images.json`.

| Pieza | Cómo | Depende de |
|---|---|---|
| Logo: cuadrado `#16827c` con monograma «GD» en blanco, y su SVG | Monograma en línea simple sobre croma `#00ff00`, perfil `cuadrado`; `gimg brand trace --mode color` con paleta; el cuadrado y el chaflán los pone el SVG | Duda 4 (monograma) |
| Lockup horizontal y vertical | `gimg brand wordmark "GALIVELOP DEVELOPER" --font <Big Shoulders Display .ttf> --weight 800 --spacing 0.01`; `gimg brand lockup … --layout h --cap 0.45 --gap 0.25 --margin 0.25` y `--layout v --width 1.6` | El logo; duda 2 (nombre); la fuente instalada (su ruta no consta en el repo) |
| Icono de proyecto (23 del Portal) y favicon | Terminal con chevrón y cursor, o la rama que sale y vuelve con nodo hueco; una tinta `#13212b`, a `currentColor` | Duda 4; el Portal hoy solo pide el 23 para Tarkor y Workflow (m.267) |
| `og` del Portal (24), 1200×630 | Grabado a dos tintas con el barco de papel, tercio izquierdo limpio para el icono; cuarto color `#16827c` | El icono; duda 3 (la palabra «deep teal» es suposición: se comprueba en la ronda) |
| Social preview de GitHub, 1280×640 | El mismo barco, a sangre, sin texto | Duda 3 |
| Versión oscura | Líneas `#e6eef3` sobre `#0d171e`, toque `#0e9a93`; logo e iconos no se regeneran (SVG a `currentColor`) | — |
| `examples/galivelop-developer/` reescrito | Configuración, prompts y pedidos con la identidad vigente (hoy son FLUX, `#06121c`, `#2BB3A3`) | Tarea de este repo, no de developer |

Ya entregada: la tarjeta «Próximamente» (15), el barco de papel q311, en el Portal
`public/proyectos/galivelop-developer/proxima.webp` (Portal `docs/marca.md` `6574c4f` m.125, m.254). No se regenera.

## Pendiente de la persona

Las seis dudas de la hoja («Dudas que decide la persona»), con su recomendación:

1. Acento vivo: `#0E9A93` (Portal) o `#2BB3A3` (hoja anterior). **Recomendado `#0E9A93`**; con el otro, hondo `#118376`.
2. Nombre en el lockup: **«GALIVELOP DEVELOPER»** en mayúsculas y sin guion; `galivelop-developer` para repo y código.
3. Tono en la frase de paleta: **hondo en claro, vivo en oscuro**. El vivo da 5,23 en oscuro, no el ≥ 7 del alga del
   Portal; el método no calcula un tono más claro.
4. Motivo de logo e icono: **monograma «GD»** y **terminal con la rama que vuelve** (la portada, el barco, ya está
   cerrada por la persona).
5. SVG de `logos/`: **histórico**, no se copian; logo nuevo con `gimg`.
6. Lema y frases: se conservan; **falta la versión `en`** (y `gl` para el Portal).
