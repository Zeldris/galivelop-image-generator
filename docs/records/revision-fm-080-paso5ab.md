# Revisión 0.8.0 pasos 5a-5b (interfaz web)

Diff `e257ddf..HEAD` (1a33403, 8c5b50e, de894bf, e85c712), `/code-review --max-findings all`, criterio de `REVIEW.md`.
Contrato: `docs/api.md` y `docs/interfaz/marca.md` §2.1, 2.2, 2.5. Fuera: `docs/metrics/ledger.jsonl` y lo que ya está
en `docs/records/pending.md`. Los hallazgos están comprobados leyendo el código; ninguno se ha reproducido en un navegador.

Comprobado sin hallazgo: las claves i18n de `es.json` y `en.json` son las mismas, y toda clave literal `t('…')` de
`gimg/ui/js` existe. Las únicas que no aparecen son los prefijos dinámicos `ui.state.`, que ya estaban antes del diff.
No hay `innerHTML` nuevo con datos.

## Hallazgos

Formato: `ruta:línea | gravedad | ancla | problema. arreglo.`, seguido del escenario de fallo.

1. gimg/ui/js/components/queue-bar.js:55 | medio | demostrado (contrato de `queue.move`, docs/api.md) | `queuedOrder` coloca toda la tanda en la posición de su primera entrada, pero `queue.move` de una entrada suelta solo intercambia posiciones y puede meterla en medio de una tanda. Así, el cajón muestra un orden que no es el del trabajador. Arreglo: que `queue.move` salte bloques de tanda enteros (como `move_batch`), o que el cajón pinte por `position`.
   Escenario: B1a=1, B1b=2, L=3. Con ▲ en L, el servidor guarda B1a=1, L=2, B1b=3, y el cajón sigue mostrando B1a, B1b, L. El clic parece no hacer nada y el trabajador corre L antes que B1b.
2. gimg/ui/js/components/order-view.js:275-279 | medio | demostrado (`failures.fail_batch` → `order.discard_chosen`, gimg/failures.py:151) | `sectionsOf` recibe los intentos sin la elegida, así que `canFail` ofrece «Ninguno vale» en la tanda que la contiene, y la cabecera cuenta un intento de menos. Arreglo: dejar la elegida en los datos de su sección (sin pintarla dos veces) y `canFail = false` si `order.chosen` está en la tanda.
   Escenario: la tanda 5 tiene q10..q13 y la elegida es q11. La cabecera dice «3 intentos» y muestra «Ninguno vale». Al elegir motivo, el POST devuelve `order.discard_chosen` y la persona solo ve un toast de error.
3. gimg/ui/js/components/order-view.js:380 | medio | demostrado (antes del diff, la galería iba de la más nueva a la más vieja) | En un pedido libre, los intentos de una sola imagen no tienen tanda y `sectionsOf` deja la sección «sin tanda» siempre al final. El intento recién pedido, y su tarjeta en cola o corriendo, quedan debajo de todas las tandas. Arreglo: ordenar secciones y sueltos por el id más nuevo.
   Escenario: «3 seguidas» crea la tanda 20 y luego «Otra semilla» (count 1) crea la entrada 24. La tarjeta de la 24 y su intento salen al fondo de la galería.
4. gimg/ui/js/components/retouch-panel.js:163 (y order-view.js:120-121) | medio | marca.md §2.5 y el mensaje de commit («envían subject/cleanZone») | Ni los intentos (`orders._new_record`) ni las entradas (`queue.enqueue`) guardan `subject`/`cleanZone`, así que `attempt.subject !== undefined` siempre es falso. «Recrear» carga el sujeto actual del pedido y «Reintentar» no manda ninguno. Arreglo: leerlos de `order.batches.find(b => b.id === attempt.batch)` (o de `e.batch`), o guardarlos en el intento y la entrada.
   Escenario: la tanda 3 se hizo con «faro» y luego el sujeto pasó a «puerto». Recrear y Reintentar un intento de la tanda 3 generan con «puerto».
5. gimg/ui/js/components/retouch-panel.js:181 | leve | marca.md §2.2 (no se encola sin comprobación superada) | «Variar» en marca llama a `load()` (estado `loading`) y encola en el acto, saltándose el bloqueo de `syncButtons`. Arreglo: esperar a `builder.flush()` y encolar solo si `status === 'ready'`.
   Escenario: el sujeto ya no pasa un veto de la hoja. ▶ Variar hace el POST y sale un toast `brand.blocked` en lugar del motivo en línea.
6. gimg/ui/js/components/retouch-panel.js:124 (y new-order.js:99) | leve | demostrado | «Pasar a imagen libre» manda solo `{count, mode, prompt, seed}` y pierde negativo, pasos, cfg, sampler, borrador, plantilla y modelo. Además, mientras la comprobación está en `loading`, envía un `state().prompt` viejo. Arreglo: montar el cuerpo con `spec({mode:'free', prompt})` sin `subject`/`cleanZone`, y desactivar el botón fuera de ready/blocked.
   Escenario: con borrador y 12 pasos marcados, el intento libre sale sin borrador y con los pasos del perfil. Si se edita el sujeto y se pulsa antes de 300 ms, el prompt libre es el del sujeto anterior.
7. gimg/ui/js/components/new-order.js:263 | leve | demostrado | `onBuilder` llama a `loadProfile()` cada vez que el perfil de la pieza difiere, y eso borra `copiedParams` y la nota de copia. Mientras la comprobación está en `loading`, `st.defaults` son los de la pieza anterior. Arreglo: seguir `d.profile` solo con el estado ready/blocked, y no borrar lo copiado cuando el cambio de perfil viene de la pieza.
   Escenario: se elige la pieza A (P2) y luego «Copiar de…» un pedido de la pieza B (P1). El perfil va y vuelve, el pedido se crea sin los pasos, cfg y sampler copiados, y la nota desaparece.
8. gimg/ui/js/components/batch-head.js:23 | leve | demostrado (`reasonsText` de brand-order.js sí muestra la nota) | Una tanda fallada con «otro» y nota muestra solo «otro». Arreglo: usar `rec.reason.text` si el rasgo es `other`.
   Escenario: «Ninguno vale» con Otro y la nota «manos deformes» muestra «Falló: otro».
9. gimg/ui/js/components/order-view.js:269 | leve | demostrado (`badges()` depende de `order.mode`) | La firma de la tarjeta no incluye `ctx.order.mode`, así que el chip Marca/Libre queda viejo tras cambiar de modo. Además, ↑/↓ en la galería (`i ± cols`) no tiene en cuenta las cabeceras de tanda de ancho completo. Arreglo: meter `order.mode` en la firma y hacer que la navegación vertical sepa de secciones.
   Escenario: tras «Pasar a imagen libre», las tarjetas antiguas siguen con «Marca» hasta recargar la página. ↓ salta a una tarjeta que no es la de debajo.
10. gimg/ui/js/components/reason-picker.js:259 | leve | demostrado | La repetición automática de la tecla N abre el diálogo y el keydown repetido cae dentro, donde N es «Sin motivo». Arreglo: `if (ev.repeat) return;` en el keydown del diálogo.
    Escenario: con N algo sostenida, el intento de marca se descarta sin motivo.
11. docs/handoff.md:1 | leve | AGENTS.md «La bitácora se actualiza en el mismo commit que el trabajo que describe» | Ninguno de los cuatro commits toca la bitácora. Arreglo: ponerla al día (rama, qué falta de 5b/5c, siguiente paso) en el próximo commit de trabajo.
12. (mensajes de commit e85c712 y 8c5b50e) | leve | AGENTS.md «Cuerpo: … y estado del check» | e85c712 no dice el estado del check, y 8c5b50e solo pone «Tests estáticos y de navegador.», sin resultado. Arreglo: decir el resultado del check en los siguientes cuerpos.

## Observaciones

- Ningún hallazgo coincide con `docs/records/pending.md`. Los leves de backend de los pasos 1-4 ya están allí y no se repiten.
- No se ha visto ninguna petición con `prompt` en modo marca ni campos mal nombrados frente a `docs/api.md`, salvo la omisión de `subject`/`cleanZone` del n.º 4.
