# Revisión 0.8.0 paso 5c (interfaz web: troubleshooting)

Diff `5ae590f..HEAD` (53fbfa2), `/code-review --max-findings all`, criterio de `REVIEW.md`. Contrato: `docs/api.md`
(GET/POST `/api/projects/{p}/troubleshooting`, POST `…/troubleshooting/extend`, GET pedido `failures`/`troubleshooting`,
POST `…/brand/prompt` `known`) y `docs/interfaz/marca.md` §2.5. Fuera: `docs/metrics/ledger.jsonl`, lo que ya está en
`docs/records/pending.md` y en `docs/records/revision-fm-080-paso5ab.md`. Todo comprobado leyendo el código, incluido
el backend `gimg/failures.py` y `gimg/orders.py`. Nada se ha reproducido en un navegador.

Comprobado sin hallazgo:
- El cuerpo del POST de la fila casa con `failures._row`: `key`, `profile`, `problem` (str, no vacío), `attempts`
  (lista de int), `redesign` (solo si hay texto), `terms` (lista de str), `by`. No se manda ningún campo de más
  (`api.bad_param`) y `extend` manda `{}`.
- Las claves de `es.json` y `en.json` son las mismas, y las `{params}` de `ui.ts.*` y `ui.prompt.known*` coinciden. Toda
  clave `t('ui.…')` nueva existe.
- No hay `innerHTML` nuevo: todo pasa por `h()` como texto.
- Al fallar el POST de la fila, lo escrito se conserva (el formulario no se rehace) y el error sale con `role="alert"`.

## Hallazgos

Formato: `ruta:línea | gravedad | ancla | problema. arreglo.`, seguido del escenario.

1. gimg/ui/js/components/order-view.js:260 | medio | marca.md §2.5 «error al guardar la fila (el formulario conserva lo escrito)»; demostrado (`orders._fail_whole_batch`, `failures.fail_batch` no miran el bloqueo) | La firma del panel lleva `ctx.blocked`, que es el texto «N fallos de M». Si el contador sube con el pedido ya bloqueado, el formulario se rehace entero: se pierde lo escrito y el foco salta al título (l.273). Arreglo: usar en la firma `Boolean(ctx.blocked)` y el estado, o pasar los valores del formulario viejo al nuevo.
   Escenario: hay 4 tandas terminadas y la persona falla la 1, la 2 y la 3, así que el pedido queda bloqueado. Escribe Problema y Rediseño, y luego descarta en la galería los intentos de la tanda 4. `failures.count` pasa a 4, la firma cambia, el formulario sale otra vez con los valores propuestos y el foco salta al h2.
2. gimg/ui/js/components/troubleshoot.js:18 | medio | demostrado (`orders.reset_failures` no quita `batch.failed`) | `failedAttemptIds` toma todas las tandas con `failed` del historial. Tras una fila, el contador vuelve a 0, pero las tandas siguen marcadas como falladas, así que el campo Intentos de la segunda fila propone también los intentos del ciclo anterior. Arreglo: limitarse a las tandas de los motivos actuales: `new Set(failuresOf(order).reasons.map(r => r.batch).filter(b => b != null))`.
   Escenario: fallan las tandas 1-3 y se apunta una fila con q1..q6. Luego, con sujeto nuevo, fallan las tandas 4-6 y el formulario propone q1..q12. Si no se corrige a mano, la fila mezcla dos ciclos.
3. gimg/ui/js/components/order-view.js:269 | medio | marca.md §2.5.3 «permite una sola tanda»; texto `ui.ts.extendMessage` | `failures.admit` gasta `extendPending` al encolar la tanda de la extensión, y el estado vuelve a `blocked` mientras esa tanda está en cola o corriendo. Entonces el formulario reaparece, roba el foco y vuelve a ofrecer «Una tanda más». `failures.extend` solo rechaza si hay una extensión sin usar, así que se pueden pedir tandas sin rediseñar sin límite. Arreglo: que el backend rechace `extend` si ya se usó una extensión desde el último reinicio del contador, y que la interfaz trate esa tanda como «extendida» hasta juzgarla.
   Escenario: «Una tanda más», encolar, el estado vuelve a `blocked`, el formulario sale de nuevo, «Una tanda más» otra vez y el servidor la acepta. Se repite sin rediseño.
4. gimg/ui/js/components/troubleshoot.js:55 | leve | marca.md §2.5 «Mando» y la cabecera de `confirm.js` (el foco vuelve a `opener`) | `run()` deshabilita los botones antes de abrir `confirmAction`. Al cancelar, `back.focus()` cae sobre un botón deshabilitado y el foco se queda en `<body>`. Arreglo: abrir la confirmación antes de `run()`, o pasar `opener` como función que rehabilite y devuelva el botón.
   Escenario: con teclado, Tab hasta «Una tanda más», Intro y luego Esc. `document.activeElement` queda en `body`.
5. gimg/ui/js/components/order-view.js:95-99 | leve | demostrado | `reload()` se traga el error con un toast. Si falla tras el 201 de la fila, el formulario bloqueado sigue en pantalla y otro clic en «Apuntar» apunta una fila duplicada. Arreglo: que `reload` diga si falló y, en ese caso, quitar o deshabilitar el formulario.
   Escenario: la red se corta justo después del POST. Salen dos toasts (éxito y error), el formulario sigue igual y un segundo clic deja dos filas iguales en el registro y en el Markdown.
6. gimg/ui/js/components/troubleshoot.js:47 | leve | demostrado (`describeError` envuelve un `Error` normal en `ui.error.generic`) | Con Problema vacío, el aviso dice «Algo falló: Escribe el problema…», como si hubiera fallado el servidor. Arreglo: pintar `t('ui.ts.problemRequired')` en `errorHost` y salir sin lanzar.
7. gimg/ui/js/components/brand-prompt.js:26 | leve | demostrado (es.json:1042, en.json) | `rowLabel` devuelve ahora `row.key`, pero `ui.prompt.known` sigue diciendo «fila {row} de troubleshooting». Arreglo: «(pedido {row})» en es y en, como `knownRedesign`.
   Escenario: una fila sin rediseño muestra «Ya falló antes: «x» (fila portada/rows-icon de troubleshooting)».
8. gimg/ui/js/components/troubleshoot.js:84 | leve | demostrado | `ui.ts.count` («{n} filas» / «{n} rows») no tiene singular, así que con una fila filtrada sale «1 filas» / «1 rows». Arreglo: clave singular, o «Filas: {n}».
9. gimg/ui/js/components/troubleshoot.js:72 | leve | marca.md §2.5 «Mando» (accesibilidad) | `aria-live=polite` cubre todo el contenedor y `draw()` lo rehace entero, así que cada cambio de filtro hace leer la tabla completa. Arreglo: dejar la región viva solo en el contador.
10. docs/handoff.md:1 | leve | AGENTS.md «La bitácora se actualiza en el mismo commit que el trabajo que describe» | 53fbfa2 cierra el paso 5c sin tocar la bitácora ni el plan. Es la misma falta que el n.º 11 de la revisión 5a-5b, pero en un commit nuevo. Arreglo: actualizarlos en el commit de los arreglos.

## Observaciones

- marca.md §2.5 dice que el panel lateral «se sustituye» por el formulario, pero `order-view.js:271` deja el formulario encima de `retouch.node`. Se puede leer como un cambio de diseño consciente (el panel apagado con su motivo), así que conviene confirmarlo y dejarlo dicho en marca.md.
- `parseIds` lee cualquier número: «q1-q3» da `[1, 3]`, no un rango. El hint dice «q1, q2…», así que no es un fallo.
- Los tests estáticos de `test_ui.py` solo buscan cadenas. Los de navegador sí comprueban el motivo (texto de `order.attempt_unknown`, del 409 y del rediseño). Ninguno cubre los hallazgos 1-4.

Veredicto: SHIP WITH FIXES.
