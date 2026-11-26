# Interfaz de Galivelop IG para el proceso de marca: diseño (borrador, sin decidir)

Diseño de interfaz de la fase FM (`docs/plan/fm.md`, D41), escrito el 2026-11-16; no está prototipado
ni probado en navegador. Donde este documento y el plan difieran (versiones, decisiones), manda el plan. Parte de la
propuesta de FM, de la interfaz de hoy (`gimg/ui/`),
de `docs/interfaz/f4a.md`, de la hoja propia (`docs/marcas/galivelop-image-generator/hoja.md`, «Interfaz: tokens y
reglas») y del proceso a mano (`docs/marcas/portal/hoja.md` «Cómo se escribe el prompt»,
`docs/records/troubleshooting-portal-marca.md`, puntos 9 y 10 de `docs/plan.md`).

Tres ideas que ordenan todo lo demás:

1. **Las reglas viven en el servidor, la interfaz solo las pinta.** El prompt montado, la comprobación, la nota y el
   contador de fallos llegan hechos por la API (los mismos que dan `gimg brand prompt` y `gimg brand lint`). El JS no
   repite ninguna regla de la hoja: si la repitiera, CLI e interfaz acabarían discrepando.
2. **Nada nuevo de navegación salvo una pestaña.** Las tres pantallas de hoy (proyectos, proyecto, pedido) siguen; se
   añade la pestaña «Bandeja» y el resto son paneles dentro de lo que ya hay.
3. **La persona siempre puede hacer ella lo que se pide a la bandeja** (D39). La bandeja es una lista de preguntas con
   formulario; que conteste Claude, Ollama o la persona es indiferente para la interfaz.

---

## 1. Mapa de pantallas

```
#/                          Proyectos (sin cambios; la tarjeta gana «hoja: sí/no» y «bandeja: n»)
#/p/<p>/pedidos             Pedidos: columna «modo» (marca/libre), estado de entrega, fallos n/3
#/p/<p>/piezas              Piezas: con hoja, tarjetas por TIPO DE PIEZA de la hoja; debajo, perfiles sin tipo
#/p/<p>/marca[?s=…]         Marca: subpestañas Hoja · Comprobación · Troubleshooting · Taller
#/p/<p>/bandeja             Bandeja del agente (NUEVA)
#/p/<p>/o/<perfil>/<clave>  Pedido: tandas, nota, descartes, contador, siguiente paso, entrega
(siempre)                   Cola agrupada por tandas · pastilla «Bandeja n» en la cabecera
(diálogos)                  Nuevo pedido con conmutador de modo · Recortar · Desglose de nota
```

### Cómo conviven «Pieza de marca» e «Imagen libre»

Un solo diálogo «Nuevo pedido» (`gimg/ui/js/components/new-order.js`) y un solo panel lateral
(`retouch-panel.js`), con un **conmutador de dos posiciones arriba** (`role="radiogroup"`, flechas ←/→ lo cambian):

| | Pieza de marca | Imagen libre |
|---|---|---|
| Por defecto | Sí, si el proyecto tiene hoja válida | Sí, si no hay hoja |
| Se escribe | Tipo de pieza, sujeto, zona limpia (opcional) | Prompt entero, como hoy |
| Perfil, registro, croma, semilla, count, modelo | Los pone el tipo de pieza (se ven, plegados en «Ajustes de la pieza») | Los elige la persona |
| Comprobación | Bloquea «Encolar» con el motivo escrito | Avisa, nunca bloquea (como hoy `bannedWords`) |
| Agrupación | Siempre en tanda | Tanda si count > 1 |
| Nota | Con descarte (propuesto o automático) y contador de fallos | Informativa si hay hoja; sin descarte ni contador |
| Entrega | raíz / aprobadas / pendiente / descartes + LEEME | Como hoy |

- **Entrada.** Tres puertas que ya existen: «Nuevo pedido» en Pedidos (abre en el modo por defecto), «Pedir» en una
  tarjeta de Piezas (abre en marca con ese tipo fijado) y el panel lateral de un pedido existente (su modo es el del pedido).
- **El modo es del pedido**, y cada intento guarda con qué modo se generó (distintivo «Marca» o «Libre» en la tarjeta).
- **De marca a libre** («Pasar a imagen libre», en el diálogo y en el panel): el prompt montado se copia entero al
  campo de prompt libre, editable. Es la salida de emergencia cuando la hoja bloquea algo que la persona quiere probar;
  por eso el modo marca no tiene «encolar de todos modos». En un pedido existente pide confirmación y dice qué se
  pierde: descarte por nota, contador de fallos y entrega por carpetas dejan de aplicarse a las tandas nuevas.
- **De libre a marca** («Convertir en pieza de marca»): pide el tipo de pieza y propone como sujeto el prompt sin los
  bloques que reconoce de la hoja (lo hace el servidor: `brand/prompt?from=`); lo que no reconoce queda en el sujeto,
  con aviso. Los intentos libres anteriores se quedan con su distintivo y no cuentan para el contador.
- **Recordar el modo**: el último usado por proyecto, en `store` (como los filtros), nunca por encima de «sin hoja».

---

## 2. Pantallas y paneles

Convenciones comunes: estados con texto además de color (regla de `f4a.md` §6); región `aria-live="polite"` para lo
que cambia solo; foco de 3 px (`--focus-w`); objetivo táctil 44 px (`--tap`); textos por `i18n.t` (claves `ui.piece.*`,
`ui.score.*`, `ui.batch.*`, `ui.discard.*`, `ui.fail.*`, `ui.crop.*`, `ui.next.*`, `ui.delivery.*`, `ui.tray.*`,
`ui.sheet.*`); los mensajes de comprobación y los nombres de rasgo llegan traducidos de la API con `?lang=`, como
hoy `check`. El texto del prompt es inglés siempre: va en `<code lang="en">`.

**Mando** (Steam Input en perfil teclado, el supuesto de `f4a.md` §5 sigue por comprobar en la Deck): todo lo nuevo se
puede hacer con cruceta (flechas), A (Intro), B (Esc) y Tab; ninguna acción depende de arrastrar ni de una tecla
modificadora. Escribir el sujeto pide el teclado en pantalla de Steam (Steam+X); por eso existen «Copiar de…» y
«Pedir sujeto a la bandeja». Atajos de una tecla nuevos (nunca dentro de un campo): `K` recortar, `D` desglose de la
nota, `U` recuperar un descarte, `[` y `]` tanda anterior/siguiente, `B` bandeja (global).

### 2.1 Pieza de marca: prompt montado y comprobación en vivo

- **Propósito:** que la persona escriba solo el sujeto y vea, antes de gastar 10 minutos por imagen, el prompt exacto
  que se va a mandar y si pasa la hoja.
- **Contenido** (componente nuevo `components/brand-prompt.js`, usado por `new-order.js` y por `retouch-panel.js`):
  - Tipo de pieza (`select`, con su perfil y registro al lado como chips: «portada · 1600×900 · grabado · sin croma»).
  - Clave (como hoy; se propone `<tipo>/<slug del sujeto>` y se puede cambiar).
  - Sujeto (`textarea`, contador de palabras con el margen 120-200 del total montado).
  - Zona limpia (`select` de zonas de la hoja: ninguna, izquierda, derecha, arriba, abajo, centro; más texto libre).
  - **Prompt montado**, de solo lectura, partido en los tramos de la hoja, cada uno con su rótulo y de dónde sale:
    `1 Sujeto (tú)` · `2 Zona limpia (tú)` · `3 Registro: grabado (hoja Portal)` · `4 Cierre (hoja Portal)` ·
    `5 Paleta (hoja GVIG, hereda de Portal)`. Los tramos de la hoja van en `--surface-2` con filete; los de la persona,
    en `--surface`. Las palabras que rompen una regla van subrayadas y con `<mark>` dentro del tramo. «Copiar prompt».
  - **Comprobación**: lista como la de `brand-tab.js` (`ul.check-list`, chips ok/aviso/fallo), una fila por regla del
    punto 5 de la hoja: acaba en paleta con los hex; un solo registro; cierre a sangre; zona limpia antes del bloque;
    palabras que no se escriben; color fuera de tinta; motivo vetado (con «permitido por excepción: 06» cuando toca);
    croma si se recorta; semilla fija y count 2-4; longitud. Cada fallo enlaza al campo que lo arregla.
  - **«Ya falló antes»**: si el sujeto contiene un término de una fila de troubleshooting («compass», «window»), aviso
    con el rediseño que se apuntó. No bloquea.
  - Ajustes de la pieza (`details`, cerrado): semilla, count, modelo, croma. Cambiarlos se ve como «distinto de la hoja».
  - Pie: «Encolar tanda de N · ~40 min» (ETA con `estimateMs`, como hoy) · «Pedir sujeto a la bandeja» · «Pasar a imagen libre».
- **Estados:**
  - *Sin hoja:* el conmutador deja «Pieza de marca» deshabilitado con el motivo («Este proyecto no tiene hoja de
    marca») y un enlace a Marca.
  - *Hoja con errores* (`brand lint` de la hoja en rojo): bloqueado, con el primer error y enlace a Marca › Comprobación.
  - *Vacío:* sujeto en blanco; el prompt montado enseña los tramos de la hoja y el hueco «1 Sujeto» punteado; botón
    deshabilitado con «Escribe el sujeto».
  - *Cargando:* la comprobación se pide 300 ms después de la última tecla; mientras, «comprobando…» con `.spin` y el
    botón deshabilitado (no se encola con una comprobación vieja: cada respuesta lleva un número de secuencia, como
    `loadSeq` de hoy).
  - *Bloqueado con motivo:* botón deshabilitado y debajo «No se puede encolar: 2 fallos» con la lista; `aria-describedby`.
  - *Error / sin servicio:* «No se pudo comprobar» + «Reintentar»; en marca no se encola sin comprobación.
  - *Con avisos:* se encola; los avisos viajan con la tanda y se ven en su cabecera.
- **Mando:** orden de Tab = conmutador → tipo → clave → sujeto → zona → comprobación (cada fallo es un enlace
  enfocable) → ajustes → botones. Ctrl+Intro encola desde el sujeto.
- **Reutiliza / cambia:** `new-order.js` (gana el conmutador y monta `brand-prompt.js` en vez del `textarea` de
  prompt; el resto del formulario, «Copiar de…», textos de composición y plantilla no cambian); `retouch-panel.js`
  (en un pedido de marca el campo «prompt» pasa a ser sujeto + zona, y «estilo del perfil en solo lectura» pasa a ser
  el prompt montado); `attempt-util.js` `bannedWord` queda solo para el modo libre sin hoja; lista de comprobación de
  `brand-tab.js` extraída a `components/check-list.js` para usarla en los dos sitios.

### 2.2 Tandas en la cola

- **Propósito:** una pieza de marca son 2-4 imágenes que se juzgan juntas; la cola tiene que moverlas, cancelarlas y
  contarlas juntas.
- **Contenido** (`queue-bar.js`): las entradas con el mismo `batch.id` se pintan como un grupo con cabecera: clave,
  tipo de pieza, «2 de 4», semillas `311-314`, ETA de la tanda entera, botones **subir / bajar / primera / cancelar
  tanda**, y `details` para ver sus entradas (cada una con la fila de hoy: miniatura, progreso, cancelar). Una entrada
  sin tanda se pinta como hoy. La pastilla de la cabecera dice «1 generando · 2 tandas en cola (7 imágenes)».
- **En el pedido** (`order-view.js`): la galería se parte en secciones por tanda, la más nueva arriba, cada una con
  cabecera: «Tanda 3 · sujeto: "a stone islet with only the foundations…" · 4 intentos · mejor 8,1 · 2 descartados»,
  y los avisos con los que se encoló. La elegida sigue fijada arriba del todo.
- **Estados:** *vacía* (como hoy); *tanda a medias* («2 de 4 · faltan ~20 min», las ya hechas se pueden juzgar);
  *tanda con un fallo técnico* (la entrada fallida dentro del grupo con «Reintentar», no cuenta como fallo de marca);
  *en pausa* (como hoy); *bloqueada:* una tanda de un pedido en troubleshooting queda en la cola como «retenida:
  pedido en troubleshooting» y no arranca hasta resolverlo o cancelarla.
- **Mando:** la cabecera del grupo es enfocable; Intro abre o cierra; ←/→ recorre sus botones; `[` `]` saltan de tanda.
- **Reutiliza / cambia:** `queue-bar.js` (`entry()` se queda; se añade `group()` y `queuedOrder()` ordena por
  tanda); `queue-poll.js` sin cambios (las entradas traen `batch`); `attempt-card.js` `queueCard` sin cambios;
  `order-view.js` agrupa al pintar; `confirm.js` para «Cancelar tanda».

### 2.3 Tarjeta de intento con nota y desglose

- **Propósito:** ver de un vistazo si un intento vale como marca y por qué, sin abrir nada.
- **Contenido** (`attempt-card.js` + componente nuevo `components/score-chip.js`):
  - **Chip de nota** en la fila de metadatos, delante del chip D31: «8,1 / 10 · propuesta» (verde, ≥ umbral),
    «6,4 / 10 · bajo el umbral» (rojo), siempre con número y palabra. La nota la calcula el trabajador al terminar el
    intento y viaja en el intento: no hay espera ni cola de medidas para pintarla.
  - **Desglose** (`details` bajo el chip, o `D`): tabla rasgo · valor medido · referencia · puntos / peso, con una
    barra plana por fila y su número («Ajuste a paleta 91 % · ref. ≥ 80 % · 2,7 / 3»; «Colores fuera de paleta:
    `#d9a441` 6 %»; luminancia; saturación; marco crema en el borde; densidad de grabado). Debajo, **«No medido»**:
    los rasgos que la hoja declara de criterio (horizonte, motivo repetido, glifos), cada uno con tres botones:
    «Bien» · «Mal» · «Pedir juicio a la bandeja». Es la lista de comprobación a ojo, no una nota inventada.
  - **«No» con motivo**: al pulsar «No» (o `N`) se despliega una fila de motivos rápidos (los rasgos no medidos de la
    hoja + «otro», que usa la nota de texto). El motivo alimenta el contador de fallos y la fila de troubleshooting.
    Un segundo `N` sin motivo descarta igual (no se obliga).
  - Distintivos nuevos: «Marca» / «Libre», «Recorte de q574», «Propuesta» (≥ umbral), «Descarte propuesto».
  - Dentro de una tanda, orden por nota descendente (la elegida sigue primero en el pedido).
  - El chip D31 (contraste en la zona de texto) se queda para las piezas compuestas; su «paleta %» pasa al desglose
    cuando hay nota, para no decir lo mismo dos veces.
- **Estados:** *sin nota* (libre sin hoja, o intento anterior a 0.8): chip «sin nota» + «Calcular»; *calculando*
  (recalcular a mano): `.spin`, por la cola de `measure-chip.js` (`requestMeasure`); *nota caducada* (la hoja cambió
  desde que se calculó): chip gris «nota de la hoja anterior» + «Recalcular»; *error* («no se pudo medir: falta
  ffmpeg»): texto y botón; *sin referencias* (la hoja no tiene aprobadas): nota parcial, dicho en el desglose.
- **Mando:** `D` abre el desglose y lleva el foco a la tabla; Esc lo cierra y devuelve el foco a la tarjeta.
- **Reutiliza / cambia:** `attempt-card.js` (fila `meta`, `badges()`, botón «No»); `measure-chip.js` como modelo y su
  cola para recalcular; `compare-view.js` enseña las dos notas y marca el rasgo en el que más difieren.

### 2.4 Descartes recuperables

- **Propósito:** que descartar (a mano o por nota) quite el intento de en medio sin perderlo.
- **Contenido** (`order-view.js`, componente nuevo `components/discards.js`): sección plegada al final de la galería,
  «Descartes (7)», con tarjetas pequeñas: miniatura, `q<id>`, nota, **motivo** («nota 5,2: paleta 41 %» o «a mano:
  horizonte»), cuándo, y «Recuperar» (`U`). «Vaciar descartes» con confirmación (`confirm.js`) queda para más tarde:
  de entrada no se borra nada desde aquí.
  Al descartar: aviso con «Deshacer» (`toast.js` ya admite acción). Hoy el descartado se queda en la galería al 62 % de
  opacidad; pasa a salir de ella y entrar en esta sección.
  **Descarte propuesto** (mientras el automático esté apagado, ver §5): la cabecera de la tanda dice «3 bajo el
  umbral» y ofrece «Descartar los 3»; las tarjetas llevan el distintivo.
- **Estados:** *vacío* (la sección no se pinta); *cargando* miniaturas (`loading="lazy"`); *error al recuperar*
  (el archivo ya no está: «No se puede recuperar: falta el archivo» y la ruta); *bloqueado:* no se descarta la elegida
  sin deshacer antes la elección (el botón lo dice, como hoy «Elegir» dice por qué no).
- **Mando:** la cabecera de la sección es un `summary` enfocable; dentro, flechas entre tarjetas y `U`.
- **Reutiliza / cambia:** `attempt-card.js` (variante compacta), `order-view.js`, `project-view.js` (filtro de
  estado gana «con descartes»), `toast.js`.

### 2.5 Troubleshooting y contador de fallos

- **Propósito:** aplicar desde la interfaz la regla «tras 2-3 intentos fallidos, troubleshooting y rediseño», sin
  que dependa de la memoria de nadie.
- **Qué cuenta como fallo:** una tanda de marca **terminada** sin ningún intento válido: todos bajo el umbral, o la
  persona pulsa «Ninguno vale» en la cabecera de la tanda (con motivo). Un fallo técnico o una cancelación no cuentan.
  El contador es por pedido y por sujeto: lo pone a cero un rediseño apuntado o una elección.
- **Contenido:**
  - **Marcador** en la cabecera del pedido, junto al título: «Fallos 2 de 3 ■■□», con texto siempre. En la lista de
    pedidos, columna «fallos».
  - **Al 2.º:** aviso suave sobre el panel lateral: «Un fallo más y toca rediseñar. Motivos hasta ahora: horizonte ×2».
  - **Al 3.º: pedido «En troubleshooting».** Los botones que encolan (panel lateral, «Variar», «Recrear», `G`) quedan
    deshabilitados con el motivo, y el **formulario de troubleshooting** (componente nuevo `components/troubleshoot.js`)
    sale **encima** del panel de retoque (no lo sustituye), con las tres columnas del registro: *Problema* (propuesto con los motivos
    apuntados), *Intentos* (los `q` de las tandas fallidas, ya rellenos), *Rediseño* (texto). Tres salidas:
    1. «Apuntar y rediseñar yo»: guarda la fila, pone el contador a cero y abre el panel de pieza con el sujeto vacío.
    2. «Pedir rediseño a la bandeja»: crea la tarea con las tandas y motivos; el pedido queda «esperando rediseño».
    3. «Una tanda más sin rediseñar»: pide confirmación, se apunta en la fila y permite una sola tanda **por ciclo de fallos** (pregunta 4, §6): el ciclo acaba al poner el contador a cero (fila apuntada, elección o nota de 7 o más); usada la tanda, el botón queda deshabilitado con el motivo y el servidor responde `order.extend_used` (409).
  - **Registro** en Marca › Troubleshooting: la tabla de `troubleshooting-portal-marca.md` como datos, con enlaces a
    los intentos y filtro por pieza.
- **Estados:** *sin fallos* (el marcador no se pinta); *bloqueado* (lo descrito); *esperando rediseño* (enlace a la
  tarea de la bandeja y «Responder yo»); *error al guardar la fila* (el formulario conserva lo escrito).
- **Mando:** al bloquearse, el foco va al título del formulario (`tabindex="-1"`) y se anuncia con `role="alert"`.
- **Reutiliza / cambia:** `order-view.js` (cabecera y guardas de los atajos; monta el formulario encima del panel de retoque), `retouch-panel.js` (estado bloqueado),
  `brand-tab.js` (subpestaña), `confirm.js`.

### 2.6 Recortar (punto 9 del plan)

- **Propósito:** sacar una portada sin marco o un icono de una hoja 2×2 sin salir de la interfaz ni tocar el original.
- **Contenido** (componente nuevo `components/crop-editor.js`, un `dialog` como el de `layout-editor.js`): la imagen
  cruda del intento con **un** rectángulo; barra con: proporción (bloqueada a la del perfil por defecto, «soltar»),
  **rejilla** (libre · 2×2 · 3×3: elegir una celda coloca la caja en ella, que es el caso de los iconos), paso
  (1 · 10 · 50 px), modo (mover · tamaño), caja en números (`x0,y0,x1,y1`, editables), tamaño de salida; vista
  previa al tamaño del perfil; «Guardar como intento derivado» y «Llevar a otro pedido…» (perfil + clave, existente
  o nueva). Si el intento ya es un recorte, «Repetir la misma caja en…» otro intento de la tanda.
- **Estados:** *cargando* la imagen; *caja demasiado pequeña* (la salida se ampliaría más de ×2): aviso, no bloquea;
  *bloqueado:* caja fuera de la imagen o de área cero, con el motivo; *error* de la API dentro del diálogo (un
  `dialog` modal tapa los avisos, como en `new-order.js`); *ocupado* (`api.heavy_busy`): «otra tarea pesada en curso».
- **Mando:** con la caja enfocada, flechas mueven o cambian tamaño según el botón de modo, al paso elegido; ningún
  gesto pide Mayús ni Alt (que el mando no tiene), aunque en teclado siguen valiendo los de `layout-editor.js`. Las
  celdas de la rejilla son botones. Táctil: asas de 44 px.
- **Reutiliza / cambia:** el arrastre con captura de puntero, las asas y `onBoxKey` de `layout-editor.js` se extraen
  a `components/box-drag.js` y los usan los dos editores; `attempt-card.js` gana «Recortar» en «Más acciones» y el
  distintivo «Recorte de q…»; `lightbox.js` sin cambios.

### 2.7 Taller enlazado según el tipo de pieza

- **Propósito:** que tras elegir se vea cuál es el paso siguiente de esa pieza y se llegue a él con todo cargado.
- **Contenido:** una **tira de pasos** en la cabecera del pedido de marca (componente nuevo `components/next-step.js`),
  que sale del tipo de pieza de la hoja: p. ej. icono = `Generar ✓ → Elegir ✓ → Recortar → Quitar fondo (croma) →
  SVG → Entregar`; portada = `Generar → Elegir → Entregar`; logo = el sistema entero. El paso actual es un botón
  primario («Siguiente: quitar fondo»), los hechos llevan ✓ y enlace a su resultado, los futuros están deshabilitados
  con su motivo («antes hay que elegir un intento»), igual que hace hoy el taller.
  El botón abre Marca › Taller con `?src=perfil|clave|intento&piece=<tipo>`: `brand-workshop.js` ya admite `src`; con
  `piece` enseña solo los pasos de ese tipo (un icono no ve wordmark ni lockups), propone el nombre desde la clave y
  pone el croma de la hoja como color de fondo de «Quitar fondo». Al guardar, vuelve al pedido con el paso marcado.
- **Estados:** *sin elegida* (tira visible, todo lo posterior deshabilitado); *paso en curso* («trabajando…», como
  hoy); *paso que falta en la máquina* (`rsvg-convert`): bloqueado con la orden que lo arregla (de `check`);
  *pieza sin croma que pide recorte*: aviso en el paso («este intento no va sobre croma: el recorte puede dejar halo»).
- **Mando:** la tira es una lista (`ol`) con un solo botón activo; ←/→ entre pasos.
- **Reutiliza / cambia:** `brand-workshop.js` (parámetro `piece`, lista de pasos visible, vuelta al pedido),
  `attempt-card.js` («Usar para marca» se queda para el modo libre), `order-view.js`.

### 2.8 Entrega

- **Propósito:** saber qué hay entregado, dónde, y sustituir una aprobada sin perderla.
- **Contenido** (`order-view.js`, sustituye a la caja verde «Entregada»; componente nuevo `components/delivery.js`):
  - Cuatro contadores con su ruta copiable: **raíz** (la elegida, el archivo que usa el proyecto) · **aprobadas/**
    (las que pasaron y no se usan, o las sustituidas) · **pendiente/** (≥ umbral sin juzgar) · **descartes/**.
  - «Deshacer» (como hoy) y «Ver LEEME» (texto de solo lectura generado por gimg: pieza, intento, semilla, prompt
    montado, nota, de qué versión de la hoja).
  - **Sustituir:** elegir otro intento cuando ya hay entregada abre una confirmación con las dos imágenes lado a lado
    (`compare-view.js`) y sus notas: «q635 pasa a aprobadas/, q641 pasa a la raíz». Nunca borra.
  - «Aprobar sin elegir» en la tarjeta (≥ umbral): la manda a aprobadas/ sin cambiar la raíz.
  - En Pedidos (`project-view.js`): columna de entrega («entregada · 2 aprobadas · 1 pendiente») y filtros nuevos
    «pendientes de juicio» y «en troubleshooting».
- **Estados:** *sin entregar*; *entregada*; *destino no escribible o fuera de la raíz* (error de la API con la ruta,
  D25/D40); *la raíz ya tiene un archivo que gimg no puso*: bloqueado hasta confirmar, como `brand.exists` en el taller.
- **Mando:** la confirmación de sustituir tiene el foco inicial en «Cancelar».
- **Reutiliza / cambia:** `order-view.js`, `compare-view.js`, `confirm.js`, `project-view.js`.

### 2.9 Bandeja del agente

- **Propósito:** un solo sitio donde está todo lo que pide criterio, quién lo tiene y qué contestó; y donde la
  persona puede contestar ella.
- **Contenido** (pestaña nueva `components/tray-tab.js`, ruta `#/p/<p>/bandeja`; pastilla «Bandeja 3» en la
  cabecera junto a la de la cola, que suma todos los proyectos):
  - Filtros: pendientes · respondidas sin aplicar · cerradas · todas.
  - Una tarjeta por tarea: **tipo** (escribir sujeto · juzgar lo no medible · rediseñar tras 3 fallos · elegir entre
    candidatos · hoja inicial), pedido enlazado, la pregunta en una frase, el contexto (miniaturas, notas, motivos),
    estado, y quién contestó («Claude», «Ollama», «tú»).
  - **Respuesta**: siempre una propuesta estructurada del mismo tipo que el formulario que la persona rellenaría: un
    sujeto (se ve montado y comprobado con `brand-prompt.js`), un veredicto por rasgo, una fila de troubleshooting,
    un intento elegido con su razón. Botones: **Aplicar** · **Editar y aplicar** · **Rechazar** (con motivo, vuelve a
    pendiente) · **Responder yo** (abre el mismo formulario vacío).
  - Línea de estado de quien atiende: «Última lectura de la bandeja: hace 12 min (Claude)» o «Nadie ha leído la
    bandeja desde ayer», con la orden `gimg agent todo`.
  - Los botones «Pedir … a la bandeja» de §2.1, §2.3, §2.5 crean la tarea y dejan un chip «en la bandeja» en el sitio.
- **Estados:** *vacía* («Nada espera criterio»); *cargando*; *error*; *tarea caducada* (el pedido cambió desde que
  se pidió: la respuesta no se puede aplicar, se dice por qué y se ofrece «Volver a pedir»); *respuesta que no pasa
  la comprobación* (un sujeto del agente con una palabra vetada): «Aplicar» bloqueado con el motivo, «Editar y
  aplicar» abierto.
- **Mando:** lista vertical; ↑/↓ entre tareas, Intro abre, ←/→ entre sus botones; `B` desde cualquier pantalla.
- **Reutiliza / cambia:** `project-view.js` (cuarta pestaña), `router.js` (`bandeja` en la lista de pestañas),
  `index.html` + `app.js` (pastilla), `queue-poll.js` (el mismo sondeo de 3 s trae el contador), `brand-prompt.js`,
  `troubleshoot.js`, `attempt-card.js` (variante compacta).

### 2.10 Hoja de marca visible en la pestaña Marca

- **Propósito:** que lo que hoy solo está en un Markdown de 800 líneas se vea como lo ve gimg, con su procedencia.
- **Contenido** (`brand-tab.js`, que pasa a tener subpestañas con `?s=hoja|check|fallos|taller`; el router ya lee
  la consulta):
  - **Hoja** (componente nuevo `components/sheet-view.js`), en fichas: *Ficha* (archivo, versión, cadena de herencia
    «GVIG ← Portal» con lo que cambia marcado «propio» y lo demás «heredado»); *Paleta por papeles* (papel, tinta,
    acento, halo: muestra, hex, nombre, y la frase de paleta tal como se escribe); *Registros* (los dos bloques y el
    cierre, en `code`, con «Copiar»); *Vetos* (por grupo: ética, motivos, colores, palabras que no se escriben; cada
    excepción con la pieza a la que se limita); *Tipos de pieza* (tabla: tipo, perfil, registro, croma, semilla, count,
    pasos de taller, y «Pedir»); *Aceptación* (pesos por rasgo, umbral, referencias aprobadas con miniatura y su nota,
    rasgos no medibles).
  - **Probar un sujeto**: `brand-prompt.js` suelto, sin encolar. Es la cara de `gimg brand prompt` y `brand lint` y
    da uso a la hoja desde 0.6, antes de que exista el pedido de marca.
  - **Comprobación**: la de hoy (`check`) más las filas de la hoja: esquema válido, `extends` resuelto, Markdown y
    datos coinciden, las referencias existen, las aprobadas sacan ≥ umbral.
  - **Troubleshooting** (§2.5) y **Taller** (el de hoy, sin cambios salvo §2.7).
  - Solo lectura: la hoja se edita en el archivo (ruta copiable). Editarla desde la interfaz queda fuera (pregunta 7).
- **Estados:** *sin hoja* (lo de hoy: paleta y vetos de `brand` de la configuración, más «Este proyecto no tiene
  hoja» y cómo crearla: `gimg brand init` (nueva en 0.6.0, ver el plan), o «Pedir hoja inicial a la bandeja» desde 0.10); *hoja con errores*
  (se pinta lo que se pueda leer y la lista de errores arriba); *padre de `extends` no encontrado* (bloquea el modo
  marca, se dice qué proyecto falta o qué archivo no se lee); *cargando*; *error*.
- **Mando:** subpestañas con ←/→ (`role="tablist"`, como las de `project-view.js`).
- **Reutiliza / cambia:** `brand-tab.js` (se parte: lo de hoy pasa a `check` y a la ficha de paleta), muestras
  `swatch`, `dl.facts`, `check-list`; `pieces-tab.js` (con hoja, una tarjeta por tipo de pieza, con su perfil dentro;
  los perfiles sin tipo, debajo, con «Pedir» en modo libre).

---

## 3. Bocetos

### 3.1 Nuevo pedido en modo «Pieza de marca» (diálogo, 1280×800)

```
┌─ NUEVO PEDIDO ──────────────────────────────────────────────────────────────────────────────────────────┐
│  (●) PIEZA DE MARCA   ( ) IMAGEN LIBRE                                       hoja: Portal › GVIG  v3    │
├──────────────────────────────────────────────┬──────────────────────────────────────────────────────────┤
│ TIPO DE PIEZA  [ portada            ▾]       │ PROMPT MONTADO · 164 palabras (120-200)      [⎘ Copiar]  │
│  portada · 1600×900 · grabado · sin croma    │ ┌ 1 SUJETO (tú) ──────────────────────────────────────┐  │
│                                              │ │ A small stone islet with only the foundations of a  │  │
│ CLAVE  [ portada/06-diseno             ]     │ │ lighthouse, stakes and ropes, a ̲g̲o̲l̲d̲e̲n̲ plumb line…  │  │
│                                              │ ├ 2 ZONA LIMPIA (tú) ─────────────────────────────────┤  │
│ SUJETO                          38 palabras  │ │ the left third stays calm, plain water              │  │
│ ┌──────────────────────────────────────────┐ │ ├ 3 REGISTRO: GRABADO (hoja Portal) ──────────────────┤  │
│ │ A small stone islet with only the        │ │ │ fine engraving in two inks, like a fine sea chart…  │  │
│ │ foundations of a lighthouse, stakes and  │ │ ├ 4 CIERRE (hoja Portal) ─────────────────────────────┤  │
│ │ ropes, a golden plumb line…              │ │ │ No photographic rendering, no glow, no text, … no   │  │
│ └──────────────────────────────────────────┘ │ │ border, no frame                                    │  │
│ ZONA LIMPIA  [ tercio izquierdo     ▾]       │ ├ 5 PALETA (hoja GVIG, hereda de Portal) ─────────────┤  │
│                                              │ │ Palette strictly limited to ink grey #13212b on …   │  │
│ ▸ AJUSTES DE LA PIEZA                        │ └─────────────────────────────────────────────────────┘  │
│   semilla 311 · count 4 · zimage-turbo-q6    │ COMPROBACIÓN · 1 fallo · 1 aviso · 8 bien                │
│                                              │  ✗ FALLO  Color fuera de tinta: «golden» → ir al sujeto  │
│ [ Copiar de… ]                               │  ! AVISO  Ya falló antes: «plumb line» (q616) → rediseño │
│                                              │  ✓ BIEN   Acaba en la frase de paleta con los 4 hex      │
│                                              │  ✓ BIEN   Un solo registro · cierre a sangre · … (+5)    │
├──────────────────────────────────────────────┴──────────────────────────────────────────────────────────┤
│ No se puede encolar: 1 fallo.      [Pedir sujeto a la bandeja] [Pasar a imagen libre] [Cancelar]        │
│                                                                    [ ENCOLAR TANDA DE 4 · ~40 MIN ] (off)│
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
En menos de 900 px de ancho las dos columnas se apilan: formulario, comprobación y, plegado, el prompt montado.

### 3.2 Pedido de marca: tandas, nota, contador, descartes

```
Proyectos › portal › portada/06-diseno @ portada              [1 generando · 1 tanda en cola] [Bandeja 2] ES ?
┌───────────────────────────────────────────────────────────────────────────────────┬───────────────────────┐
│ PORTADA/06-DISENO   [MARCA] portada · grabado          FALLOS 2 DE 3 ■■□          │ PIEZA DE MARCA        │
│ Generar ✓ → Elegir → Entregar           [ SIGUIENTE: ELEGIR UN INTENTO ]          │ sujeto                │
│ Entrega: raíz — · aprobadas 1 · pendiente 2 · descartes 7                         │ ┌───────────────────┐ │
├───────────────────────────────────────────────────────────────────────────────────┤ │ A small stone     │ │
│ TANDA 3 · «A small stone islet with only the foundations…» · 4 · mejor 8,1        │ │ islet with only…  │ │
│                                  [Ninguno vale] [Descartar los 2 bajo el umbral]  │ └───────────────────┘ │
│ ┌──────────────────────────┐ ┌──────────────────────────┐ ┌─────────────────────┐ │ zona [izquierda ▾]    │
│ │        (imagen)          │ │        (imagen)          │ │      (imagen)       │ │ ▸ prompt montado      │
│ │ [PROPUESTA]              │ │ [PROPUESTA]              │ │ [DESCARTE PROPUESTO]│ │ ✓ comprobación: bien  │
│ │ q634 · semilla 311       │ │ q635 · semilla 312       │ │ q636 · semilla 313  │ │ ! Un fallo más y toca │
│ │ [8,1/10 · PROPUESTA] ▾   │ │ [7,4/10 · PROPUESTA] ▸   │ │ [5,2/10 · BAJO] ▸   │ │   rediseñar.          │
│ │  paleta   91 % ████▌ 2,7/3│ │ [Sí][No][★ Elegir][⇄]    │ │ [Sí][No][Elegir][⇄] │ │   Motivos: horizonte  │
│ │  fuera    2 %  ████▌ 1,8/2│ │ nota: ____________       │ │ nota: ___________   │ │   ×2                  │
│ │  luz      ok   ███▌  1,5/2│ └──────────────────────────┘ └─────────────────────┘ │                       │
│ │  grabado  ok   ████  2,1/3│ ┌──────────────────────────┐                         │ [ OTRA TANDA DE 4     │
│ │  No medido: horizonte     │ │ ┄┄ q637 EN COLA · 2.º ┄┄ │                         │   · ~40 MIN ]         │
│ │   [Bien][Mal][Bandeja]    │ │   semilla 314 · ~12 min  │                         │ [Pedir sujeto a la    │
│ │  glifos [Bien][Mal][Band.]│ │        [Cancelar]        │                         │  bandeja]             │
│ │ [Sí][No][★ Elegir][⇄]     │ └──────────────────────────┘                         │ [Pasar a imagen libre]│
│ └──────────────────────────┘                                                      │                       │
│ TANDA 2 · «…lighthouse drawn as a dashed blueprint» · 4 · FALLO: ninguno vale (macizo)                    │
│ ▸ 4 intentos descartados                                                          │ ▸ TEXTOS              │
│ ▾ DESCARTES (7)                                                                   │                       │
│ │ q630 4,9 nota: paleta 41 % [Recuperar] │ q631 6,1 a mano: horizonte [Recuperar] │ …                     │
└───────────────────────────────────────────────────────────────────────────────────┴───────────────────────┘
```
Al tercer fallo, el panel derecho pasa a ser «EN TROUBLESHOOTING: Problema / Intentos (q630, q631, q636…) /
Rediseño · [Apuntar y rediseñar yo] [Pedir rediseño a la bandeja] [Una tanda más]».

### 3.3 Cajón de la cola con tandas

```
┌─ COLA ──────────────────────── [⏸ Pausar] [Vaciar] ┐
│ (Pendientes) Terminadas  Fallidas  Todas           │
│ ▾ TANDA · portada/06-diseno · portada   2 DE 4     │
│   semillas 311-314 · faltan ~22 min       [✕ tanda]│
│   ▓▓▓▓▓▓▓▓░░░░ q636 generando · paso 5/8 [Cancelar]│
│   ┄ q637 en cola · 2.º                   [Cancelar]│
│ ▸ TANDA · icono/07-hoja · icono (croma)  0 DE 2    │
│   semillas 90-91 · ~20 min     [↑][↓][⤒] [✕ tanda] │
│ ┄ q640 og/portal · libre · en cola 5.º  [↑][↓][⤒][✕]│
│ ▸ TANDA · portada/06-publicado           RETENIDA  │
│   pedido en troubleshooting → [Ir al pedido]       │
└────────────────────────────────────────────────────┘
```

### 3.4 Bandeja del agente

```
Proyectos › portal                    [Pedidos] [Piezas] [Marca] [BANDEJA 3]
Última lectura de la bandeja: hace 12 min (Claude) · gimg agent todo
(Pendientes 2) (Respondidas 1) Cerradas  Todas
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ REDISEÑAR TRAS 3 FALLOS · portada/06-diseno                          RESPONDIDA · Claude │
│ Tandas 1-3: macizo ×2, horizonte ×1   [q630][q631][q636] (miniaturas)                    │
│ Propuesta: «El islote con solo los cimientos, estacas, cuerdas y bloques»                │
│  Problema: la línea discontinua sale maciza · Comprobación del sujeto: ✓ bien            │
│                              [Aplicar] [Editar y aplicar] [Rechazar…] [Responder yo]     │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ JUZGAR LO NO MEDIBLE · portada/06-publicado · q641                   PENDIENTE · 8 min   │
│ ¿Hay horizonte o cielo? ¿Se repite el barco de la q311?   [q641] [q311]                  │
│                                                                    [Responder yo]        │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ ESCRIBIR SUJETO · icono/07-historial                                 PENDIENTE · 2 min   │
│ Pedido: «icono de historial, sin reloj»                            [Responder yo]        │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.5 Recortar

```
┌─ RECORTAR q574 · icono/07-hoja ─────────────────────────────────────────────────────────┐
│ ┌───────────────────────────────────────────┐  PROPORCIÓN (●) 1:1 del perfil ( ) libre  │
│ │ ╔═══════════════════╗·····················│  REJILLA    ( ) libre (●) 2×2 ( ) 3×3     │
│ │ ║■                 ■║                     │             [1][2]                        │
│ │ ║    (celda 1)      ║     (celda 2)       │             [3][4]                        │
│ │ ║■                 ■║                     │  MODO (●) mover ( ) tamaño   PASO [10 px▾]│
│ │ ╚═══════════════════╝·····················│  CAJA  x0[  0] y0[  0] x1[512] y1[512]    │
│ │      (celda 3)      ·     (celda 4)       │  SALIDA 1024×1024 (×2,0)                  │
│ └───────────────────────────────────────────┘  ┌ vista previa ┐                         │
│                                                └──────────────┘                         │
│ El original no se toca.    [Cancelar] [Llevar a otro pedido…] [GUARDAR COMO DERIVADO]   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Endpoints y datos por pantalla

Nombres propuestos, en la forma de los de hoy (`gimg/ui/js/api.js`, `docs/api.md`). «(amplía)» = ruta que existe y
gana campos.

| Pantalla | Ruta | Datos |
|---|---|---|
| Todas | `GET /api/projects/{p}` (amplía) | `sheet: {present, valid, version, path, extends: [..], errors: [..]}`, `pieceTypes: [{id, label:{es,en}, profile, register, chroma, seed, count, workshop:[..]}]` |
| Hoja en Marca | `GET /api/projects/{p}/brand/sheet` | Hoja resuelta: `roles` (papel, tinta, acento, halo: hex, nombre), `registers`, `closing`, `paletteSentence`, `vetoes` (grupos, excepciones), `pieceTypes`, `acceptance` (pesos, umbral, `autoDiscard`, refs con su nota, `unmeasured`), y por valor `origin: own|inherited` + archivo |
| Comprobación de la hoja | `GET /api/projects/{p}/check` (amplía) | Filas `sheet.*` con el formato de hoy `{id, status, message, fix}` |
| Prompt montado y comprobación | `POST /api/projects/{p}/brand/prompt` | Entra `{piece, subject, cleanZone, key?, overrides?}` (o `{from: "<prompt libre>"}` para convertir). Sale `{prompt, words, segments:[{role, text, source}], checks:[{id, status, message, field?, span?:[i,j]}], blocked, defaults:{profile, seed, count, model, chroma}, known:[{term, row}]}`. Sin efectos, rápida (no pasa por `_heavy()`) |
| Comprobación en libre | `POST /api/projects/{p}/brand/lint` | `{prompt}` → `{checks}` (nunca `blocked`) |
| Nuevo pedido | `POST /api/projects/{p}/orders` (amplía) | `mode: brand|free`, `piece`, `subject`, `cleanZone`. En marca el servidor monta y comprueba otra vez; si no pasa, 422 `brand.blocked` con `errors` (lo que ya enseña el diálogo) |
| Otra tanda | `POST …/attempts` (amplía) | Igual, más `subject`; devuelve `batch: {id, size}`. 409 `order.troubleshooting` si el pedido está bloqueado |
| Pedido | `GET …/orders/{profile}/{key}` (amplía) | `mode`, `piece`, `subject`, `batches:[{id, index, subject, warnings, state, best, failed, reason}]`, `failures:{count, limit, reasons}`, `troubleshooting:{state, row?, task?}`, `steps:[{id, state, reason?, href?}]`, `delivery:{root, approved:[..], pending:[..], discards:n, paths}`; cada intento: `batch`, `mode`, `score`, `human:{<rasgo>: ok|bad}`, `derivedFrom:{attempt, box}` |
| Cola | `GET /api/queue` (amplía) | Cada entrada: `batch:{id, index, size}`, `held?: "troubleshooting"` |
| Cola por tanda | `POST /api/queue/batches/{id}/move` · `…/cancel` | `{to: up|down|first}` |
| Nota | (dentro del intento) + `POST …/attempts/{id}/score` | `score:{value, threshold, verdict, sheetVersion, stale, traits:[{id, label, measured, reference, points, weight, status, detail}], unmeasured:[{id, label}]}`. El `POST` recalcula (pesada, puede dar `measure.busy`) |
| Juicio a ojo | `POST …/attempts/{id}/judge` | `{trait, verdict: ok|bad}` |
| Descartar con motivo | `POST …/attempts/{id}/mark` (amplía) | `{state: "discarded", reason?: {trait?, text?}}`; mueve el archivo |
| Tanda sin válidos | `POST …/batches/{id}/fail` | `{reason}` → `failures` actualizado |
| Descartes | `GET …/orders/{profile}/{key}/discards` · `POST …/discards/{id}/restore` · `GET …/discards/{id}/image` | `[{id, score, reason:{auto, trait, text}, at}]` |
| Troubleshooting | `GET /api/projects/{p}/troubleshooting` · `POST` · `POST …/orders/{profile}/{key}/troubleshooting/extend` | Fila `{piece, key, problem, attempts:[..], redesign, terms:[..], at, by}`; el `POST` pone el contador a cero; `extend` da una tanda más, una sola por ciclo de fallos (la segunda: 409 `order.extend_used`; con una sin usar: 409 `order.extend_pending`) |
| Recortar | `POST …/attempts/{id}/crop` | `{box:[x0,y0,x1,y1], lockRatio, to?:{profile, key}}` → intento derivado. Vista previa: en el cliente con `<canvas>` (sin servidor) |
| Taller enlazado | `GET /api/projects/{p}/brand` (amplía) · rutas `brand/*` de hoy | Borrador enlazado a `{profile, key, attempt, piece}`; `matte` toma el croma de la hoja por defecto |
| Entrega | `POST …/choose` (amplía) · `POST …/attempts/{id}/approve` · `GET …/delivery/readme` | `choose` devuelve `replaced:{attempt, movedTo}`; 409 `delivery.foreign_file` si la raíz tiene algo ajeno, con `force` |
| Bandeja | `GET /api/agent/todo[?project=&state=]` · `POST /api/agent/tasks` · `POST /api/agent/tasks/{id}/answer` · `…/apply` · `…/reject` | Tarea `{id, type, project, order?, attempts?, question, context, state, answer?:{by, at, payload}, stale}`; `answer` es el mismo cuerpo que usa `gimg agent answer` y el formulario de la persona. Cabecera `X-Agent-Pending` y `X-Agent-Last-Read` en `GET /api/queue` para la pastilla, como hoy `X-Queue-Paused` |

Dos peticiones al backend que salen del diseño: (a) **la nota se calcula en el trabajador al terminar el intento** y
se guarda con él, para que la galería no dependa de medir en el momento de pintar; (b) **cada respuesta que
depende de la hoja lleva `sheetVersion`**, para poder decir «nota de la hoja anterior» y «tarea caducada».

---

## 5. Reparto por versiones y cambios a la propuesta

| Versión | Interfaz |
|---|---|
| **0.6.0** Hoja como datos | Marca con subpestañas; `sheet-view.js`; filas de la hoja en Comprobación; **«Probar un sujeto»** (`brand-prompt.js` suelto); `check-list.js` extraído; Piezas por tipo de pieza; «hoja: sí/no» en la tarjeta de proyecto |
| **0.7.0** Pieza de marca | Conmutador de modo en `new-order.js` y `retouch-panel.js`; tandas en cola y en galería; distintivo Marca/Libre; **«No» con motivo y «Ninguno vale»**; contador de fallos, bloqueo y formulario de troubleshooting; subpestaña Troubleshooting; aviso «ya falló antes» |
| **0.8.0** Nota y descarte | `score-chip.js` con desglose y «No medido» (Bien/Mal); orden por nota; `discards.js` con recuperar; descarte propuesto y «Descartar los N»; el contador pasa a alimentarse también de la nota |
| **0.9.0** Cerrar el circuito | `box-drag.js` + `crop-editor.js`; tira de pasos `next-step.js` y taller con `piece`; `delivery.js`, sustituir con comparación, LEEME, filtros de entrega en Pedidos |
| **0.10.0** Bandeja | Pestaña y pastilla; botones «Pedir … a la bandeja»; aplicar / editar / rechazar / responder yo; «Pedir hoja inicial» |

Lo que cambiaría de la propuesta, visto desde la interfaz:

1. **El descarte a mano con motivo va en 0.7, no en 0.8.** El contador de fallos de 0.7 necesita saber qué es un
   fallo antes de que exista la nota; con «Ninguno vale» y los motivos, 0.7 funciona entero y 0.8 solo añade la
   fuente automática. Mover el archivo a `descartes/` puede esperar a 0.8.
2. **El descarte automático empieza apagado** (`acceptance.autoDiscard: false` en la hoja): 0.8 marca «descarte
   propuesto» y ofrece «Descartar los N». Se enciende por proyecto cuando la comprobación de la hoja dice que sus
   aprobadas sacan ≥ 7 y sus descartes apuntados < 7 (el criterio de «pasa si» del punto 10). Un automático mal
   calibrado en una máquina que tarda 10 minutos por imagen sale caro y quita confianza en la nota.
3. **El contrato de la bandeja se fija en 0.7, aunque la bandeja llegue en 0.10.** La fila de troubleshooting, el
   sujeto y el juicio por rasgo que la persona rellena en 0.7-0.8 deben ser ya los cuerpos de `agent answer`. Así 0.10
   solo añade la lista y quién contesta, y ningún formulario se rehace.
4. **Recortar no depende de la hoja y es el dolor de hoy**: puede adelantarse a 0.7 o salir como 0.6.x si la persona
   sigue recortando a mano. Solo «el taller enlazado» necesita 0.9.
5. **Montar y comprobar, solo en el servidor**, con una ruta sin efectos y rápida; la interfaz no lleva reglas.
6. **En modo marca no hay «encolar de todos modos»**: la salida es pasar a libre, que es visible y queda apuntada en
   el intento. Dos modos claros valen más que un modo con excepciones.
7. **Las excepciones de los vetos van atadas a la pieza** (faro solo en las 06, barco solo en la 19 y la 15 de
   Developer) y la comprobación dice cuál aplicó. Sin eso, o se bloquea lo aprobado o se abre el veto para todo.
8. **Los rasgos no medibles se declaran en la hoja** (`acceptance.unmeasured`) con su rótulo es/en: son los botones
   Bien/Mal de la tarjeta, los motivos de «No» y los tipos de juicio de la bandeja. Una sola lista para los tres usos.
9. **Dónde vive la hoja:** `marca.json` aparte. La pestaña Marca enseña procedencia por archivo («heredado de
   Portal») y eso es natural con un archivo por hoja y `extends`; dentro de `galivelop-images.json` la herencia entre
   repos sería más rara de pintar y de explicar.
10. **En libre, avisar** (con la misma lista de comprobación, sin bloquear) y poner nota informativa si hay hoja: es
    gratis con el mismo componente y enseña por qué un intento libre no parece de la marca.

---

## 6. Riesgos y preguntas para la persona

**Riesgos**

- **El mando en la Deck sigue sin probarse** (`f4a.md` §5 lo deja como supuesto). Este diseño añade mucho formulario;
  si la cruceta no mueve bien el foco entre columnas, el panel de pieza y la bandeja serán incómodos. Conviene el
  recorrido en la máquina antes de 0.7.
- **Escribir el sujeto en inglés con el teclado en pantalla** es lo más lento de todo el proceso en la Deck. «Copiar
  de…», los sujetos de troubleshooting y la bandeja lo alivian; no lo quitan.
- **La nota puede no separar lo bueno de lo malo.** El punto 10 pide investigar primero. Si no separa, 0.8 se queda
  en desglose informativo y el contador vive solo de los motivos a mano (por eso el cambio 1).
- **Tandas de 40 minutos**: bloquear por troubleshooting al tercer fallo puede llegar dos horas tarde. El aviso al
  segundo y el «ya falló antes» al escribir son el freno temprano.
- **Densidad de la tarjeta**: nota, desglose, juicio a ojo, motivos, plantilla y editor en 300 px. Todo lo nuevo va
  plegado salvo el chip; hay que mirarlo a 1280×800 con dos columnas.
- **Hoja y Markdown que se separan**: la interfaz enseña los datos; si el test de coincidencia falla, la persona ve
  una hoja y lee otra. La fila correspondiente de Comprobación tiene que ser un fallo, no un aviso.
- **Dos sondeos** (cola y bandeja) sobre un servidor que serializa lo pesado: por eso el contador de la bandeja viaja
  en la respuesta de la cola.
- **Recortes pequeños ampliados** (una celda de 512 px a 1024) se ven blandos con bilineal; el editor lo avisa, no
  lo arregla.

**Preguntas**

1. ¿Qué cuenta como fallo: la **tanda** entera sin ningún válido (lo propuesto) o cada intento descartado?
2. ¿El contador es por pedido o por sujeto? (Lo propuesto: por pedido, y un rediseño apuntado lo pone a cero.)
3. Umbral 7: ¿descarte **propuesto** hasta calibrar y automático después (lo propuesto), o automático desde el
   primer día?
4. Al tercer fallo, ¿bloqueo duro o se permite «una tanda más» apuntándolo? ¿Cuántas veces? **Decidido 2026-11-26:** una vez por ciclo de fallos.
5. ¿Las respuestas de la bandeja se aplican solas alguna vez (p. ej. un sujeto que pasa la comprobación) o siempre
   las confirma la persona? Lo propuesto: siempre confirma, al menos hasta F6.
6. ¿La bandeja es por proyecto (pestaña, lo propuesto) con contador global, o una pantalla global?
7. ¿La hoja se edita desde la interfaz algún día (añadir un veto, una referencia aprobada con un botón «Usar como
   referencia» en la tarjeta) o siempre en el archivo? El botón de referencia sería lo primero que pediría.
8. En un pedido de marca, ¿«Pasar a imagen libre» convierte el pedido entero o solo la siguiente tanda?
9. ¿El modelo y el count de una pieza se pueden cambiar en modo marca (se ve como «distinto de la hoja») o quedan
   fijos y para cambiarlos hay que ir a libre?
10. ¿Recortar se adelanta a 0.7 / 0.6.x?
11. ¿La entrega por carpetas (raíz, aprobadas, pendiente, descartes) vale también para los pedidos libres de un
    proyecto con hoja, o solo para las piezas de marca?
12. ¿Parar una tanda sola cuando ya hay un intento con nota alta (≥ 8, por ejemplo) para ahorrar tiempo de Deck, o
    siempre se generan todas?
