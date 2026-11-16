# Entrega de la hoja de galivelop-evaluator (2026-11-16)

Para la sesión de **galivelop-evaluator** (GVE). Desde aquí no se toca ese repo: esto dice qué cambió en la hoja
respecto de su copia, qué decisiones se tomaron y qué archivos volver a copiar. Leído de GVE: `origin/main` `261f3bd`
(2026-11-16), con `git show`, sin modificar nada: `docs/projects/galivelop-image-generator.md` (traslados 1 y 2) y
`docs/design/marca/` (su copia, traída de este repo en `ff92f8f`).

**La hoja deja de ser borrador.** Responde a sus dos traslados: el 1 (hondo `#6b7509`) está aplicado; del 2, las dudas
2, 5 y 6 están cerradas por delegación de la persona en el agente de GVIG (2026-11-16), que puede revertirlas.

## Qué cambió respecto de su copia (`docs/design/marca/`, de `ff92f8f`)

| # | Qué | Antes (su copia) | Ahora | Dónde |
|---|---|---|---|---|
| 1 | Hondo del acento (traslado 1) | `#6f7a05` (46 pasos; 4,58 sobre papel, 4,32 sobre `#f1f6f9`, 4,25 sobre el tinte) | **`#6b7509`** (49 pasos, tono 115,6°, croma 0,119) | `hoja.md` entera, `biblia.md` §2 y §4, pedidos `23b-icono-gve-a` y `-b` |
| 2 | `tonos.py` | El de voice: el hondo solo cumple sobre el papel `#fbfcfd` | El hondo cumple a la vez sobre papel, banda alterna `#f1f6f9` (`--surface-2`) y tinte claro (vivo al 12 %); imprime una línea más con esos ratios. **Da `#6b7509` sin argumentos extra** | `tonos.py` (`BANDA`, `buscar` con varios fondos) |
| 3 | Regla «dónde no llega el texto de acento» | Texto de acento solo sobre papel o `#ffffff` | **Retirada:** el hondo vale como texto sobre todos los fondos claros del front | `hoja.md`, «Acento», último párrafo; `biblia.md` §2, «Prohibidos» |
| 4 | Estado | «Borrador del 2026-11-15, sin aprobar» | «Hoja cerrada el 2026-11-16» | cabecera de `hoja.md` y de `biblia.md` |
| 5 | «Dudas que decide la persona» | Seis abiertas, más la del relleno oscuro en «Interfaz» | «Decisiones», siete cerradas, cada una con quién la cerró y cómo se revierte | `hoja.md`, tras «Cómo se escribe el prompt» |
| 6 | Tabla de tokens | Columnas «Hoy (provisional)» / «Propuesto [P]» | «Antes» / «Vigente (aplicado por GVE, 2026-11-15)», con `light-dark(#6b7509, #b4c424)` | `hoja.md`, «Interfaz» |
| 7 | Monograma | «GVE» | **«GE»** | `hoja.md` R3, sección 4; `biblia.md` §4 |
| 8 | Icono de proyecto | Dial recomendado, nivel de alternativa | **Nivel de burbuja** (R2); el dial, de reserva (R1) y en el estado vacío (R12) | `hoja.md` «Mar y tecnología», R1-R2, secciones 6 y 9; `biblia.md` §4, §7, §9 |

Ratios nuevos del hondo `#6b7509` (`python3 docs/marcas/galivelop-evaluator/tonos.py '#B4C424'`), los mismos que da su
traslado:

| Par | Ratio | Antes (`#6f7a05`) |
|---|---|---|
| Sobre el papel `#fbfcfd` | 4,90 | 4,58 |
| Blanco `#ffffff` encima (y texto de acento sobre `#ffffff`) | 5,03 | 4,71 |
| Sobre la banda alterna `#f1f6f9` (`--surface-2`) | 4,62 | 4,32 |
| Sobre el tinte claro `#f2f5e3` | 4,54 | 4,25 |
| Tinta `#13212b` encima (prohibido) | 3,26 | 3,49 |
| Sobre `#0d171e` (no es texto en oscuro) | 3,60 | 3,85 |

El vivo `#b4c424`, la variante oscura (es el vivo, 9,38) y los tintes `#f2f5e3` / `#2b361f` **no cambian**.

## Decisiones tomadas

| Duda | Decisión | Quién | Porqué, en una línea |
|---|---|---|---|
| 1. Acento `#b4c424` | Aprobado | La persona, 2026-11-15 | — |
| 2. Regla de mareas como protagonista de portada, `og` y cabecera | **Se acepta** | Elegido por el agente (delegado, 2026-11-16) | Es el patrón ya aprobado de los hermanos (objeto con banderín del acento sobre el mar grabado) y dice «medir» sin una cifra |
| 3. Acento y «sube» | El acento no significa resultado | GVE, con la recomendación (2026-11-15) | — |
| 4. Series y puestos | Siguen en cerúleo | GVE, con la recomendación (2026-11-15) | — |
| 5. Monograma | **«GE»** | Elegido por el agente (delegado, 2026-11-16) | Los monogramas de la familia son de dos letras (GV, GD, GW, IG) y tres no se leen a 16-32 px con el trazo 12/128; «GVE» sigue siendo la sigla en texto |
| 6. Icono de proyecto | **Nivel de burbuja** (`23b-icono-gve-b`); dial de reserva | Elegido por el agente (delegado, 2026-11-16) | Tres formas grandes y simétricas que aguantan 16 px y el modelo dibuja sin contar; el dial tiene marcas finas, invita a cifras y se lee como «puntuación» |
| 7. Relleno de acento en oscuro | El vivo con tinta oscura encima (9,38) | GVE, con la recomendación (2026-11-15) | — |

Cómo se revierte cada una de las tres delegadas está en la propia hoja («Decisiones», puntos 2, 5 y 6).

## Qué copiar

De este repo, rama `hojas-repos`, el commit que trae esta nota, a `docs/design/marca/` de GVE:

| Archivo de aquí | A | Nota |
|---|---|---|
| `docs/marcas/galivelop-evaluator/hoja.md` | `docs/design/marca/hoja.md` | Rehacer los dos enlaces relativos (`../portal/hoja.md`, `../README.md`) como enlaces fijos al commit nuevo, como en su copia actual |
| `docs/marcas/galivelop-evaluator/biblia.md` | `docs/design/marca/biblia.md` | Los mismos dos enlaces |
| `docs/marcas/galivelop-evaluator/tonos.py` | `docs/design/marca/tonos.py` | Tal cual; `python3 docs/design/marca/tonos.py '#b4c424'` tiene que dar `hondo  #6b7509 … (49 pasos)` |

Y en su `docs/design/marca/README.md`: el origen (commit nuevo, ya no «borrador sin aprobar»), quitar «Una diferencia
con la hoja» (ya no la hay) y la lista de dudas pendientes.

**En el front de GVE no hay que cambiar ningún valor:** sus tokens ya llevan `light-dark(#6b7509, #b4c424)` y
`--accent-soft` `light-dark(#f2f5e3, #2b361f)`, que es lo que la hoja dice ahora. Sus traslados 1 y 2 a GVIG pueden
pasar a hechos.

## Qué queda de este lado (GVIG)

- **Piezas:** ninguna aprobada. El icono elegido se genera con `23b-icono-gve-b` (ya con `#6b7509` en el prompt); si
  hay una ronda anterior hecha con `#6f7a05`, el trazado se hace igualmente con `--palette '#6b7509'`.
- **Símbolo «GE» y lockup:** `gimg brand` (órdenes en `hoja.md`, R3 y R4); dependen del `.ttf` de Big Shoulders Display.
- **Suposiciones sin comprobar:** el nombre «chartreuse yellow-green» para `#b4c424` y el recorte de un trazo oliva
  sobre magenta; se miden en la primera ronda (`hoja.md`, sección 15).
