# Interfaz de `gimg` — propuesta de diseño (F4, primera versión)

Estado: propuesta del agente, 2026-10-27; **las 8 decisiones las confirmó la persona el 2026-10-27** (todas como se
recomendaban, ver el final). Prototipo navegable en
[`prototipo/index.html`](prototipo/index.html) (un archivo, sin dependencias; ábrelo desde el repo para que carguen las
imágenes del piloto). Vocabulario del `GLOSSARY.md`: proyecto, perfil, pedido, clave, intento, candidata, descartada,
elegida, cola, manifiesto, carpeta de entrega, perfil de máquina.

## Qué es «personalizado»

Lo que cambia de un proyecto a otro ya existe como datos, no como código:

| Dato | Dónde vive hoy | Qué hace la interfaz con él |
|---|---|---|
| Paleta, tipografía, acento | `docs/marcas/<p>/biblia.md` §2-3 → `galivelop-images.json` | Tiñe la pantalla del proyecto (acento, baldosa) y previsualiza el texto compuesto con su fuente y color |
| Logo SVG (símbolo y lockup, claro/oscuro) | `docs/marcas/<p>/logos/` (D29) | Lo coloca en la previsualización y en la composición real (D28) |
| Estilo por perfil (prompt fijo) y zona reservada | biblia §7-8 → `style` del perfil | Lo muestra como cola del prompt (solo lectura) y marca la zona en la previsualización |
| Piezas: tamaño, zona, logo, título, subtítulo, velo | `examples/<p>/piezas.json` → `compose` del perfil + `text` del pedido | Son las **plantillas de pieza**: un pedido nuevo nace de una con todo prellenado |
| Reglas de lo que no se muestra, palabras vetadas | biblia §1 y §7 | Aviso al retocar el prompt si aparece una palabra vetada |

La interfaz no contiene nada de marca: lo lee del generador (API de F3), que lo lee del proyecto (D2, D12).

## Recorrido: de «quiero el og de Portal» a «PNG entregado»

1. **Proyectos** → tarjeta «Portal Galivelop» (logo, acento, 4 pedidos, 1 en cola).
2. **Proyecto › Piezas** → fila `og` 1200×630 (zona izquierda, logo `portal-a-lockup`, prompt `estilo.txt` aprobado en r2) →
   «Pedir».
3. **Nuevo pedido** (panel sobre la misma pantalla): clave `portada`, título y subtítulo prellenados desde la pieza, prompt
   prellenado desde la plantilla de la biblia, modelo rápido, semilla 3, «borrador primero» opcional → «Encolar 1» (o «3
   seguidas»). Si el pedido supera el perfil de máquina (tamaño, pasos, referencias), se rechaza ahí mismo con el motivo (D15).
4. **Cola** (barra persistente arriba): «1 generando · 2 en cola»; el intento en marcha enseña progreso y tiempo estimado
   (el del perfil en esa máquina, ~3 min). La interfaz sigue usable: se puede abrir otro pedido o preparar otro.
5. **Pedido** `portada @ og`: el intento aparece en la galería al terminar (sondeo cada pocos segundos, sin recargar).
   Veredicto a ojo con **sí / no** como en la página del piloto (sí = candidata, no = descartada; teclas `s`/`n` sobre la
   tarjeta enfocada); «Comparar» pone dos lado a lado; cada tarjeta lleva semilla, pasos, modelo, tiempo y la medida de D31
   (contraste de la zona reservada, % de paleta).
6. **Retocar**: prompt (D19), semilla, pasos, modelo, borrador (D20, D30) → «Otra semilla» / «3 seguidas» encolan intentos
   nuevos del mismo pedido. El texto (título, subtítulo, zona, velo) se cambia en el panel y la previsualización en el
   navegador se actualiza al instante sobre todos los intentos; la composición real la hace `gimg compose` sin volver a
   generar (D28).
7. **Elegir** una candidata → se entrega `portada-og.png` en la carpeta de entrega del proyecto, el manifiesto se actualiza
   (D13, D21) y la tarjeta queda «Elegida · entregada», con **Deshacer**.

## Pantallas

Las tres de D22, más dos pestañas dentro de la segunda y un panel. No añado pantallas nuevas: lo personalizado cabe como
pestañas del proyecto, porque la marca y las plantillas son *del proyecto*, no del generador ni del pedido.

### 1. Proyectos (`#/`)

- Muestra: una tarjeta por proyecto registrado (D12) con logo, nombre, acento, nº de pedidos, elegidas, en cola, último
  intento; aviso si la configuración pide una versión de `gimg` más nueva (D24).
- Permite: entrar; «Añadir proyecto» (ruta) solo como texto de ayuda, porque es la CLI quien registra (D12).
- Estados: sin proyectos (cómo registrar uno); proyecto cuya carpeta no se encuentra (tarjeta atenuada con el motivo).

### 2. Proyecto (`#/p/<id>`) con tres pestañas

**Pedidos** (la de D22): lista con clave, perfil, tamaño, nº de intentos, elegida (miniatura), último estado; filtros por
perfil y por estado (todos · con elegida · sin elegida · en cola · con fallo · sin intentos); la parte del proyecto en la cola,
visible arriba. Permite abrir, «Nuevo pedido» y reordenar o cancelar lo suyo en la cola.

**Piezas** *(añadido a D22)*: una fila por plantilla de pieza (`piezas.json` → `compose` del perfil): perfil, tamaño de
destino y de generación, zona reservada, logo, texto por defecto, ronda que aprobó su prompt. Permite «Pedir» (abre el panel
de nuevo pedido prellenado). Por qué: el pedido no se escribe desde cero; las piezas de r4-r5 ya son plantillas, y sin esta
pestaña la persona tendría que copiar tamaño, logo y texto a mano cada vez.

**Marca** *(añadido a D22)*: paleta con roles (y combinaciones clara / oscura / sobre imagen), tipografía, logos elegidos
(símbolo y lockup sobre su fondo), zona reservada por perfil, lo que no se muestra y las palabras vetadas; de dónde sale
cada dato (repo y commit). Solo lectura: se edita en el repo del proyecto (D2). Por qué: es la referencia que la persona
consulta al juzgar un intento («¿respeta la paleta?»), y es lo que hace que el generador sea «suyo» para cada proyecto.

### 3. Pedido (`#/p/<id>/pedido/<clave>@<perfil>`)

- **Galería** de intentos, la más nueva primero, con estado (nueva · candidata · descartada · elegida · en cola ·
  generando · fallo), semilla, pasos, modelo, tiempo, medida (D31), nota editable; botones sí / no / elegir / comparar;
  «Ver con texto» alterna la previsualización compuesta y el fondo crudo (`q<id>.png` / `q<id>.raw.png`, D28).
- **Comparar**: dos tarjetas marcadas → panel con las dos al mismo tamaño y botón de intercambiar.
- **Panel de retoque** (lateral en 1280 px, debajo en móvil): prompt del pedido editable + estilo del perfil en solo lectura
  (D19); parámetros dentro del perfil de máquina (modelo del catálogo, pasos, cfg, semilla, borrador; D20, D30); texto de
  la composición (título, subtítulo, zona, color, velo) con previsualización inmediata; «Otra semilla», «3 seguidas»,
  «Recomponer la elegida».
- **Entrega**: con elegida, la ruta del PNG entregado y el manifiesto; «Deshacer» (D13).

### Panel «Nuevo pedido» (desde Piezas o Pedidos)

Clave, perfil (fija la pieza), título y subtítulo, prompt prellenado, modelo, semilla, borrador primero, N intentos. Valida
contra el perfil de máquina antes de encolar y avisa de palabras vetadas de la biblia.

### Cola (barra persistente, todas las pantallas)

Pastilla «1 generando · 2 en cola» con progreso; al desplegarla, la lista completa (proyecto, clave, perfil, modelo, tiempo
previsto) con cancelar y subir/bajar lo que aún no ha empezado; el intento en marcha se puede cancelar (F2.5). Los
terminados recientes enlazan a su pedido.

## Estados

| Dónde | Estado | Qué se ve |
|---|---|---|
| Cola | vacía | «Nada en cola»; el generador se para solo (arranque bajo demanda, F3) |
| Cola | generando | barra con % o tiempo transcurrido / previsto (el perfil de máquina da la previsión), memoria libre mínima |
| Cola | motor sin arrancar / sin memoria | aviso con el motivo del perfil de máquina y qué hacer (cerrar otra cosa, bajar tamaño) |
| Intento | fallo | tarjeta roja con el motivo (código de `sd-cli`, tope de tiempo, memoria) y «Reintentar» / «Ver registro»; el intento queda en el historial |
| Pedido | sin intentos | el panel de retoque en primer plano y un solo botón: «Generar el primer intento» |
| Pedido | con elegida | tarjeta destacada, ruta entregada, «Deshacer»; elegir otra la sustituye y apila la anterior |
| Proyecto | sin pedidos | «Pide la primera pieza» → pestaña Piezas |
| Pedido | rechazado por el perfil de máquina | el formulario no encola y dice qué límite se supera (D15) |
| Interfaz | sin conexión con `gimg` | banda arriba «El generador no responde»; lo ya cargado sigue visible, nada se pierde |

## Técnica (resumen, para F4)

- HTML + CSS + JS en `gimg/ui/`, servidos por el propio `gimg` (F3); sin build, sin CDN, sin fuentes externas (las de marca
  se usan si están instaladas; si no, la de reserva de la biblia). Rutas por `#hash`, estado en memoria, sondeo a la API
  cada 3 s mientras haya algo en cola (o SSE si F3 lo da).
- Textos de la interfaz en `gimg/locales/<es|en>.json` (D16); el idioma sale del navegador y se puede cambiar en la
  cabecera. Tema por `prefers-color-scheme` con selector (auto / claro / oscuro) guardado en el navegador.
- Previsualización compuesta: superposición HTML sobre la miniatura (logo `<img>` SVG, título y subtítulo con la fuente de
  la biblia, zona y velo); la composición de verdad siempre la hace `gimg compose` (D28). Lo que se guarda (notas,
  veredictos, elegida) va a la API; en el navegador solo quedan comodidades (filtros, pestaña, tema).
- Lo que la página del piloto ya hace bien y se conserva: sí / no por tarjeta, comparar al mismo tamaño, pincha para ver
  a tamaño real, «Copiar veredicto» (útil para pegarlo en el chat del agente mientras el agente no lea la API).

## Decisiones (confirmadas por la persona, 2026-10-27)

Las ocho, tal como se recomendaban. Pregunta y razón:

1. **¿Pestañas «Piezas» y «Marca» dentro de la pantalla del proyecto (D22 pasa de tres pantallas a tres pantallas + dos
   pestañas)?** Recomiendo **sí**: sin plantillas, cada pedido se escribe a mano; sin la marca a la vista, no se puede
   juzgar un intento.
2. **¿Cola como barra persistente en todas las pantallas, o solo dentro de «Pedidos»?** Recomiendo **persistente**: con
   ~3 min por imagen, lo normal es encolar y hacer otra cosa.
3. **¿Veredicto en dos estados (sí = candidata, no = descartada) como el piloto, o con una escala?** Recomiendo **dos
   estados + elegir**, que es lo que D13 ya modela; una nota libre por intento para lo demás.
4. **¿El texto compuesto (título, subtítulo) se edita por pedido o por intento?** Recomiendo **por pedido** (todos los
   intentos lo heredan y se previsualiza al instante); un intento solo guarda lo que tenía al componerse, por el manifiesto.
5. **¿«Borrador primero» (640×320, ~50 s) activado por defecto en los pedidos grandes?** Con r3 hecha
   (`docs/registros/contenido/r3-borrador.md`): el borrador cuesta el 22 % del definitivo y anticipa estilo, paleta y
   hueco en 6 de 7 proyectos, pero no el detalle (el definitivo recoloca). Recomiendo **activado por defecto desde
   1280×640**, con la nota «el definitivo puede recolocar», y el veredicto de composición solo sobre el definitivo.
6. **¿Medidas de D31 en la tarjeta de cada intento, o solo al abrirlo?** Recomiendo **chip corto en la tarjeta** (contraste
   de la zona y % de paleta, en verde/ámbar/rojo con los umbrales calibrados) y el detalle al abrirlo.
7. **¿Idioma por el navegador con selector en la cabecera, o fijo en la configuración del usuario?** Recomiendo
   **navegador + selector** guardado en el navegador; la CLI sigue con la configuración del usuario.
8. **¿Comparar con dos imágenes lado a lado, o con cortina deslizante?** Recomiendo **lado a lado** (lo del piloto, y lo
   que cabe en móvil); la cortina solo sirve para la misma semilla con distinto retoque, que es el caso raro.
