# FM en detalle (proceso de marca, D41)

Sacado de `docs/plan.md` el 2026-11-18 (retro de tokens de 0.7.0, P2): el detalle de cada fase o versión vive
en su archivo y `docs/plan.md` guarda el puntero.

Pedido de la persona del 2026-11-16: que todo lo que se genera en un proyecto vaya bajo su marca u hoja de estilo,
con el mismo proceso que se sigue hoy a mano con el agente (hoja, prompt en su orden, cola, intentos, troubleshooting),
lo más determinista posible y dejando al agente solo lo que pide criterio. Contrastado el 2026-11-16 con la auditoría
del código, una búsqueda en la web (DTCG 2025.10, CIEDE2000, despill de croma, patrón de interrupción humano/agente),
los repos del Portal y del flujo, y un diseño de interfaz (`docs/interfaz/marca.md`). **Borrador:** las decisiones
marcadas «(abierta)» son de la persona.

### Qué cambia

1. **La hoja como datos.** Cada proyecto puede declarar `brand.sheet` en `galivelop-images.json`: ruta a un
   `marca.json` dentro de su raíz (D25), con esquema propio `gimg/schemas/brand-sheet.schema.json` y `schemaVersion`,
   que reutiliza los `$defs` compartidos (`tests/test_examples.py`). Lleva:
   - **paleta por papeles** (papel, tinta, acento, halo, retícula), en forma DTCG (`$value`, `$type`); los tonos
     hondo y oscuro del acento no se guardan, se calculan como `tonos.ts` del Portal (OKLCH, 4,5:1), con un test
     cruzado contra sus valores; `brand.palette` pasa a derivarse de la hoja cuando la hay;
   - **registros** (grabado, línea simple): bloque de prompt, frase de cierre y frase de paleta con hex;
   - **vetos**: palabras, motivos y colores fuera de tinta, con **excepciones atadas al tipo de pieza** (el faro solo
     en las 06, el barco solo en la 19; la grúa entra en la excepción de las 06, persona, 2026-11-17);
   - **tipos de pieza** (logo, icono, portada, fondo, marco…): perfil, registro, croma sí/no y color, seed y count por
     defecto, paso de taller siguiente y destino de entrega; el tipo puede llevar su propio cierre, su frase de paleta,
     su rango de palabras y la posición de la zona limpia (`cleanZone`: `beforeRegister`, por defecto, o `afterClosing`, al final del cierre)
     (persona, 2026-11-17), porque los pedidos aprobados (las 06, la 19) tienen cierre y frase propios;
   - **aceptación**: rasgos medibles con peso y referencias aprobadas, `autoDiscard` (apagado por defecto) y
     `unmeasured`, la lista de rasgos que solo juzga alguien (horizonte, motivo repetido, glifos) con rótulo es/en;
   - **herencia** `extends: "<proyecto registrado>"`: por nombre, no por ruta; gimg lee la hoja del padre dentro de la
     raíz del padre con la misma guarda (D25). Los productos declaran solo acento y motivo.
   El Markdown (`docs/marcas/<p>/hoja.md`) queda como lectura humana y un test comprueba que coincide con los datos.
2. **Dos modos sobre el mismo motor, no dos sistemas.** El modo es del pedido y cada intento guarda el suyo.
   - **Pieza de marca** (por defecto si hay hoja): la persona escribe solo el sujeto y la zona limpia y elige el tipo
     de pieza; gimg monta el prompt en el orden de la hoja (sujeto → zona limpia → registro → cierre → paleta), lo
     comprueba y **bloquea** con el motivo, pone croma, seed y count, mide y cuenta fallos. El `style` del perfil no se
     añade: el registro lo sustituye. No hay «encolar de todos modos»: la salida es «Pasar a imagen libre», que copia
     el prompt montado y queda apuntada.
   - **Imagen libre**: como hoy (`prompt` + `style` del perfil); la comprobación de la hoja **avisa sin bloquear**.
3. **El pedido** gana `mode`, `piece` y `subject` opcionales; `prompt` sigue valiendo (los pedidos de hoy son
   libres). El prompt montado se guarda en el intento con `sheetVersion` (hash de la hoja resuelta), para repetirlo.
4. **Tanda = una entrada de la cola con su count.** No hace falta otro concepto: los intentos llevan el id de la
   entrada que los generó y la cola y la galería los agrupan; mover y vaciar ya trabajan por entrada.
5. **Fallo y contador** (persona, 2026-11-16: valen **los dos criterios**). Hay fallo cuando la persona dice «Ninguno
   vale» o descarta todos los intentos de una tanda, con motivo, **o** cuando un intento saca **menos de 5** de nota
   (desde que exista la nota). Al **tercer fallo seguido** el pedido se bloquea hasta apuntar una fila de troubleshooting (motivo, cambio de sujeto), que pone
   el contador a cero; un intento de 5 o más también lo pone a cero. El contador vive en `order.json`. Al escribir el
   sujeto, la comprobación avisa si coincide con uno que ya falló. El «No» a mano lleva motivo (los `unmeasured` más
   «colores», «marco», «otro»). Umbrales, número de fallos y el resto de valores de una pieza son **configurables con
   valores por defecto** (persona): la hoja los fija por tipo de pieza y el pedido puede cambiarlos, y la interfaz
   marca lo que difiere de la hoja.
6. **Nota 0-10 (punto 10).** Sobre `measure()`: ajuste a paleta con CIEDE2000 (stdlib), luminancia y saturación frente
   a las referencias, marco en el borde y densidad de grabado; desglose por rasgo y los `unmeasured` como «No
   medido». Se calcula en el trabajador al terminar el intento. Primero se investiga si separa: pasa si las aprobadas
   del Portal (q311, q628, q635) sacan 7 o más y los descartes del troubleshooting menos. Hasta entonces, **descarte
   propuesto** («Descartar los N»), no automático (persona, 2026-11-16). Una tanda **se para sola en cuanto un intento
   saca 9 o más** (persona): los intentos que quedan de esa entrada de la cola se cancelan.
7. **Descartar mueve el archivo** a `discarded/` del pedido, con nota y motivo, recuperable; vale para el descarte a
   mano. El manifiesto y `chosenHistory` no se tocan: un intento elegido no se puede descartar sin deshacer antes.
8. **Recursos del proyecto** (persona, 2026-11-16): lo ya generado y aprobado (de gimg o archivos de la persona) se
   puede usar en el diseño de cada proyecto: como referencia de la nota, como capa de una composición y, desde la
   interfaz, añadido a la hoja con «Usar como referencia». La hoja se edita también desde la interfaz.
9. **Recortar (punto 9) y taller enlazado:** el tipo de pieza dice qué paso sigue (recortar, quitar fondo, pasar a
   SVG) y el taller (`brand-workshop.js`) se abre con `?piece=`.
10. **Entrega por tipo de pieza** (también para los pedidos libres de un proyecto con hoja, persona): destino `<raíz>/<carpeta>/<slug>/` con `aprobadas/`, `pendiente/`, `descartes/` y
   `svg/` y su LEEME, como `piloto/portal-marca/`; ancho, formato y postproceso del tipo. Sustituir una aprobada
   guarda la anterior en `aprobadas/` (como `reemplaza.sh`). Nunca en `public/` del Portal: lo copia su sesión.
11. **Bandeja del agente:** lo que pide criterio sale como tarea (`id`, `kind`, entrada, esquema de respuesta,
    estado, `resolvedBy`), validada al contestar: escribir el sujeto desde un encargo, juzgar los `unmeasured`,
    rediseñar tras tres fallos, elegir entre candidatos ≥ 7, escribir la hoja inicial desde la biblia. `gimg agent
    todo` da JSON y `gimg agent answer` contesta; la persona siempre puede «Responder yo». Hoy la atiende Claude;
    con F6, Ollama sobre el mismo contrato. Nada se aplica solo: la persona confirma.

### Reparto: qué es determinista y qué no

| gimg (script, con test) | Agente o persona (criterio) |
|---|---|
| Resolver la hoja y su herencia; derivar paleta y tonos | Escribir la hoja inicial desde la biblia del proyecto |
| Montar el prompt; comprobarlo (vetos, colores, orden, longitud 120-200 palabras, negaciones solo en el cierre) | Escribir el sujeto y la zona limpia |
| Croma, seed y count por tipo; agrupar la tanda | Juzgar horizonte, motivo repetido, glifos |
| Medir, nota, descarte propuesto, mover a `discarded/` | Elegir entre candidatos que pasan |
| Contar fallos, bloquear al tercero, avisar de sujetos fallidos | Rediseñar tras tres fallos (fila de troubleshooting) |
| Recortar, quitar fondo, SVG, entrega con LEEME | Decidir qué se sustituye en la entrega |

### Versiones

Cada versión trae CLI + API + su parte de interfaz (`docs/interfaz/marca.md` §5, que sigue el orden anterior),
CHANGELOG es/en, README «Versión», `docs/api.md` y su release (`releases.py bump`). Orden (2026-11-16, tras las
respuestas de la persona): recortar primero, porque no depende de la hoja y hoy se hace a mano; la pieza de marca
antes que la nota, porque el contador ya funciona con el fallo a mano y la nota solo le añade el criterio de «menor
que 5». La nota se calibra con lo que ya hay (aprobadas y descartes del Portal) y con lo que junten 0.8.0 y antes.

| Versión | Qué trae | Pasa si |
|---|---|---|
| **0.6.0 Recortar** | Punto 9: `gimg crop`, intento derivado, «Llevar a otro pedido», `crop-editor.js` | Las portadas 06 y los iconos 07 de una hoja 2×2 salen recortados sin tocar archivos a mano |
| **0.7.0 Hoja como datos** | Esquema `brand-sheet` con `extends`; `gimg/brandsheet.py`; `gimg brand init`, `gimg brand prompt` y `gimg brand lint`; migrar el Portal y sus productos (y corregir la retícula de `hoja.md`, que no coincide con el CSS del Portal); hoja.md ↔ datos; pestaña Marca con Hoja y Comprobación, «Probar un sujeto», Piezas por tipo | `brand prompt` reproduce los prompts aprobados del Portal desde su sujeto; `brand lint` rechaza los descartes de vetos del troubleshooting por su motivo |
| **0.8.0 Pieza de marca** | Modo en el pedido y en el retoque; montaje y comprobación en el servidor; tandas agrupadas y parada con 9; contador de fallos a mano, bloqueo y troubleshooting; esquema de la tarea de bandeja fijado | Un pedido de marca del Portal hecho de principio a fin desde la interfaz, sin escribir el prompt entero |
| **0.9.0 Nota y descarte** | Investigación y nota del punto 10 en el trabajador; desglose; descarte propuesto y mover a `discarded/` recuperable; `autoDiscard` por proyecto tras calibrar; el contador suma el criterio «nota menor que 5» | El «pasa si» del punto 10 |
| **0.10.0 Taller, recursos y entrega** | Tira de pasos al taller por tipo de pieza; recursos del proyecto y «Usar como referencia»; editar la hoja desde la interfaz; entrega por carpetas con LEEME y sustituir sin perder | Una pieza del Portal entregada en su carpeta sin tocar archivos a mano |
| **0.11.0 Bandeja** | `gimg agent todo/answer`, API y pestaña Bandeja; F6 la atiende con Ollama después | Una tanda con un juicio pedido y contestado desde la bandeja |

### 0.8.0 en pasos (2026-11-26)

La interfaz de 0.8.0 es la fila «0.7.0 Pieza de marca» de `docs/interfaz/marca.md` §5 (su numeración va una por
detrás). Cada paso, con sus tests, su commit y la API en `docs/api.md`; revisión de bloque tras los pasos 2 y 4.

1. **Pedido de marca (backend):** `mode` (`brand`|`free`, sin él `free`), `piece`, `subject`, `cleanZone` en el
   pedido; en marca el servidor monta y comprueba (`brand.blocked` con los errores), el perfil, la semilla, el count
   y el modelo salen del tipo de pieza, no se añade el `style`; el intento guarda `mode` y `sheetVersion`; «Pasar a
   imagen libre» cambia el modo del pedido y lo apunta; en libre con hoja, la respuesta trae los avisos. CLI y API.
2. **Tandas:** la entrada de la cola lleva `batch:{id, index, size}` y el intento su `batch`; mover y cancelar por
   tanda (API y CLI); parada de la tanda con una nota de 9 o más (el mecanismo; la nota llega en 0.9.0).
3. **Fallos y troubleshooting:** «No» con motivo y «Ninguno vale» de una tanda; `failures` en `order.json`; al tercero
   seguido, bloqueo (`order.troubleshooting`, tandas retenidas en la cola); filas de troubleshooting como datos, que
   ponen el contador a cero; `extend`; `known` de `brand prompt` con los términos de las filas.
4. **Esquema de la tarea de bandeja** (`agent-task.schema.json`): los cuerpos de respuesta (sujeto, fila de
   troubleshooting, juicio por rasgo) son los de los formularios de los pasos 3 y 5.
5. **Interfaz:** conmutador de modo en `new-order.js` y `retouch-panel.js` con `brand-prompt.js`; `check-list.js`
   extraído; tandas en la cola y en la galería; distintivo Marca/Libre; «No» con motivo, «Ninguno vale», marcador de
   fallos, `troubleshoot.js` y subpestaña Troubleshooting; aviso «ya falló antes».
   **Hecho (2026-11-26, 5a-5c).** Fuera por diseño: nota/desglose y descartes (0.9.0) y «Pedir rediseño a la bandeja»
   **Barrido previsto para 0.9.0 (aprobado el 2026-11-26, retro P1):** `troubleshoot.js` y `brand-prompt.js`: foco que cae en
   `body` al cancelar `confirmAction` (l. 55); aviso de Problema vacío envuelto en «Algo falló:» (l. 47); `ui.ts.count` sin
   singular (l. 84); `aria-live` sobre todo el contenedor (l. 72); `rowLabel` devuelve `row.key` (`brand-prompt.js:26`).
   (0.9.0/F6, con la bandeja). «Una tanda más»: una sola vez por ciclo de fallos (`order.extend_used`).
6. **Cierre (hecho, versión 0.8.0):** CHANGELOG es/en, README «Versión», `python3 releases.py bump X.Y.Z` (sube `__version__`, los dos CHANGELOG y la «Versión» de los README: no se editan a mano); recorrido con mando en la Deck (pendiente de la
   persona, riesgo de abajo) antes de `main`.

### Barrido B de `gimg/brandsheet.py` en 0.8.0 (retro 2026-11-18, P2, aprobada)

**Hecho (2026-11-25/26):** (a) en `bdc482a`, (b) en `5fdaefd` y `594c9fe` (paso 1 #12 y paso 3 #8: no aplican), arreglos de la revisión del bloque en `730f488`.

Los 16 leves abiertos de `brandsheet.py` (detalle en `docs/records/revision-hoja-datos-paso{1,3,4}.md`), en dos encargos
`gw-worker` sonnet: **(a) validación y lint** — paso 1 #6 (hex «missing» solo en la última frase), #7 (`_HEX` sin
`#rgb`/`#rrggbbaa`), #8 (zona limpia de espacios), #9 (registro contenido en otro), #14 (test de `..` por `extends`);
paso 3 #4 (orden con `cleanZone: afterClosing`), #5 (`own_text` exime todos los registros), #6 (marcador malo sin la
pieza). **(b) repeticiones y recálculos** — paso 1 #11 (contraste repetido de `measure.py`), #12 (`lint` recalcula
`palette()`), #13 (documentar que la herencia no borra claves); paso 3 #7 (validación de marcadores duplicada), #8
(`own_text` y `quiet`, la misma lista); paso 4 #7 (rama `threshold` imposible), #8 (`try` de `accent_tones` repetido),
#11 (`_block_span` recorre el texto cinco veces).

### Decisiones de la persona (2026-11-16)

1. Fallo: los dos criterios, «Ninguno vale» o tanda descartada entera (a mano) y nota menor que 5. 2. Bloqueo: al tercer fallo seguido. 3. Descarte por debajo de 7:
propuesto hasta calibrar. 4. Modelo, count y umbrales: configurables, con valores por defecto. 5. Recortar: cuándo, a
criterio del agente (va primero, 0.6.0). 6. La entrega por carpetas vale también para lo libre. 7. La tanda se para
sola con un 9 o más. 8. La hoja se edita desde la interfaz y lo ya generado se usa como recurso del proyecto.

Segunda ronda (2026-11-16):

- **Contador:** fallo a mano (una tanda) y fallo por nota (como mucho uno por tanda) suman en la misma cuenta; un
  intento de 5 o más, cambiar el sujeto o una fila de troubleshooting la ponen a cero. Por pedido. Al tercero se puede
  seguir con «una tanda más», que queda apuntada. El troubleshooting vive en `order.json` y gimg genera el `.md`.
- **Nota:** de 5 a 6,9 no es fallo, pero se propone descartar. La parada con 9 cancela solo lo que queda de esa
  tanda, también con rasgos sin juzgar (avisa de cuáles). Lo libre de un proyecto con hoja lleva nota informativa,
  sin fallos ni parada. El descarte automático lo enciende la persona con un botón que solo se activa si la
  calibración pasa.
- **Hoja:** `marca.json` es la fuente y gimg genera `hoja.md`. Padre: Portal; heredan Galivelop-workflow,
  galivelop-developer, galivelop-voice-generator y galivelop-evaluator (por dar de alta en gimg si no lo están). Tarkor y toVeriAI son independientes, con hoja propia.
  `marca.json` se escribe donde declare el proyecto, como las plantillas (D40). Desde la interfaz se edita todo
  menos la herencia, avisando de los hijos afectados. **Manda la hoja de cada proyecto**, no el CSS: si el CSS del
  Portal no coincide (la retícula), se avisa al Portal. Cambiar la hoja deja las notas desactualizadas: la interfaz
  dice «La marca ha cambiado, ¿recalcular las notas?» y, si se dice que no, el botón «Recalcular notas» sigue
  disponible.
- **Pieza de marca:** el sujeto se escribe en inglés o en español (más idiomas, más adelante); el español pasa por la
  bandeja para traducirlo, con confirmación; mientras no haya F6, la interfaz avisa al escribirlo («en español:
  espera traducción») y deja encolarlo igualmente en inglés. Seed fija en la primera tanda y +1 en cada siguiente. «Pasar a imagen
  libre» cambia el pedido entero, apuntado. El fondo de croma se quita solo al terminar, con copia.
- **Pedidos existentes:** quedan libres; los del Portal y los de Tarkor se centralizan y reestructuran con la persona
  en su equipo, viendo lo que hay, al llegar 0.7.0 (con sus hojas ya hechas).
- **Entrega:** lo libre va a la carpeta que marque gimg por defecto, con la ruta cambiable y «Guardar como»; al
  sustituir una aprobada, la anterior pasa a `aprobadas/` con fecha.
- **Bandeja:** nada se aplica sin confirmar hasta F6; por proyecto, con contador global en la cabecera; el agente la
  mira al empezar cada sesión y lo dice en una línea.
- **Orden:** la cola parada la reanuda el agente en la próxima sesión en local, con la persona y FM sigue en paralelo; los leves, después de
  0.7.0. Una versión, un PR y una release cada vez. El recorrido con mando queda pendiente de la persona, sin
  bloquear. El diseño de interfaz de `docs/interfaz/marca.md` queda aprobado, con los cambios de este plan.

### Riesgos

- El mando en la Deck sigue sin probarse y FM añade formulario: el recorrido con mando, antes de 0.8.0.
- Escribir el sujeto con el teclado en pantalla es lento; lo alivian «Copiar de…» y la bandeja.
- La nota puede no separar lo bueno de lo malo: entonces 0.9.0 se queda en desglose informativo.
- Con tandas de ~40 min, el bloqueo al tercer fallo llega tarde; el aviso al segundo y el de sujeto fallido frenan
  antes.
- Hoja y Markdown que se separan: en Comprobación es un fallo, no un aviso.
