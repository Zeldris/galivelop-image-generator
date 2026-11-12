# Retro 2026-11-12: hojas a cada repo y tanda del Portal (`hojas-repos` → `main`)

**Estado:** aprobada y aplicada por la persona el 2026-11-12: R1-R4, A2, T1-T3 y W1-W3 aplicadas; A1
aprobada a prueba (se decide tras comparar 25a/25c/26a a 768²); colores de enlace en oscuro adoptados (#5185f1
workflow, #e75485 voice).

A3 se mira en la próxima ronda, con A2 ya en uso.

Fase 2 de la ida a `main`: `gw-opt-ai` (ronda de imágenes del 11-11 22 h al 12-11 22 h), `gw-opt-tokens` (sesión
`c7c2a076`) y retro. Solo se aplica lo que la persona confirme.

## gw-opt-ai (103 imágenes, `steam-deck-libre`, contra `ronda-2026-11-11`)

Medición (`measure.py` y `gw-opt-ai-desglose.py` sobre `piloto/opt-ai/ronda-2026-11-12.jsonl`): sin errores (la
`texturamapa` pasa de 100 % de fallos a 0). Z-Image 1024² n=43: p50 551 s, **p95 615 s, por encima del tope de
9,5 min (570 s)**. Las 13 imágenes de más de 570 s corrieron con la memoria libre mínima por debajo de 4,2 GB
(2,1-4,2 GB); con 4,9-5,6 GB libres tardan 535-549 s. FLUX 1344×768 sin referencia: 267 s.

- **A1. Iconos a 768² en vez de 1024².** Medida: Z-Image 768² 295 s frente a 551 s (−46 %); hoy salieron unos 20
  iconos `cuadrado` (~3 h). Coste: cambiar el tamaño del perfil `cuadrado` de los pedidos de icono (o un perfil
  `icono768`). Puede empeorar: trazo más fino o menos limpio, peor SVG con `brand trace` a 24 px. Comprobación: tres
  iconos aprobados (25a, 25c, 26a) con sus semillas a 768², trazados igual y comparados en hoja con los de 1024² y a
  24/64 px; solo si la persona no ve diferencia.
- **A2. Generar con la memoria libre.** Medida: +10-15 % de tiempo (≈ +60 s por imagen) cuando quedan menos de
  4,2 GB libres. Coste: ninguno en código: antes de una tanda larga, cerrar lo que come memoria compartida (navegador
  con la interfaz de gimg abierta, sesiones paralelas). Puede empeorar: nada en calidad. Comprobación: el desglose de
  la próxima ronda, `min_free_mb` frente a `total_s`.
- **A3. Problema, no propuesta:** el p95 de Z-Image 1024² supera su tope. Si A2 no lo baja, decidir si el tope sube
  a 10,5 min.

## gw-opt-tokens (sesión `c7c2a076`: 382 llamadas, contexto medio 114k, 4 compactaciones; subagentes 45 M de entrada)

- **T1. Revisar intentos con `gimg sheet`, no uno a uno.** Medida: 44 imágenes leídas en la principal, cada una
  ~1,6k tokens y ~130k arrastrados (≈ 4-5 M en total). Ya estaba en «Costes conocidos» y no se cumplió: un gancho
  `PreToolUse` de Read que avise al leer `…/attempts/q*.png` (proponer `gimg sheet`). Riesgo: ninguno; la hoja
  muestra lo mismo a menos tamaño, y se abre una sola si hace falta detalle.
- **T2. Adelgazar la bitácora.** Medida: `docs/handoff.md` leída 10 veces (979k arrastrados); la fila de
  `portal-marca` tiene 10 115 caracteres (tope 800) y la de `hojas-repos` 3 791. Pasar lo hecho a «Hecho» y dejar
  cada fila en estado + falta + siguiente. Riesgo: perder un detalle; va a «Hecho», no se borra.
- **T3. Subagentes por encima del tope de llamadas.** «Decisiones de familia» 80 llamadas (contexto medio 93k),
  «Hoja de Tarkor» 66: el tope de ~30 de `gw-orchestrate-dealer` no se aplicó en el encargo. Usarlo: partir esos
  encargos en dos. Riesgo: un arranque más (~36k).

## Retro

- **R1. Parar el generador no lo para (proyecto, grave).** La persona pidió parar; al matar `gimg work`, `gimg serve`
  lo relanzó a los 18 min y salió la #833. No hay `gimg queue pause`. Propuesta: orden `gimg queue pause|resume`
  (el servicio no arranca trabajador en pausa y la pausa espera a que acabe la imagen en curso), con test. Hasta
  entonces: `gimg serve --stop` además de matar el trabajador.
- **R2. Sustituir una imagen aprobada sin perder la anterior (proyecto).** La 10 vieja (q478) se sobrescribió antes de
  moverla a `descartes/` y hubo que rescatarla de `attempts/`. Script `examples/pilot/reemplaza.sh <nueva> <destino>`
  que mueve la anterior a `descartes/<nombre>-anterior.png`, copia la nueva y añade la línea al LEEME.
- **R3. El motivo de la marca, por escrito para los subagentes (proyecto).** El subagente de diseño cambió el 30b a
  boyas de cristal sobre el mar, contra la regla «el mar solo de fondo; el motivo es software», que vivía en la
  conversación. Añadirla a las «Reglas de imagen» de `docs/marcas/portal/hoja.md` y que el encargo de pedidos de
  imagen apunte a esa sección.
- **R4. Registro de la ronda por fecha (proyecto).** El comando de `.claude/gw/gw-opt-ai.md` junta todo el registro;
  filtrar por `ts` (desde la ronda anterior) para que la ronda sea solo la nueva.

## For Galivelop-workflow

- **W1.** `gw-opt-ai` tiene `disable-model-invocation`, pero `AGENTS.md` (fase 2) pide al agente lanzarlo: la persona
  tuvo que escribirlo. O se permite invocarlo, o la fase 2 dice que lo lanza la persona.
- **W2.** El aviso de celdas de la bitácora de más de 800 caracteres sale en cada commit y se ignora (10 115): que
  `handoff.py` ofrezca mover a «Hecho» lo cerrado de una fila, o que el gancho falle a partir de un segundo tope.
- **W3.** Un subagente que acaba con trabajo de fondo propio reenvió su informe cuatro veces: la plantilla de
  `gw-orchestrate-dealer` debería pedir que espere la subida antes de responder (ya lo dice para el push; añadir
  «no respondas hasta que acabe»).
