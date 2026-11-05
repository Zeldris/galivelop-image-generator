# Revisión de fase 1 de `f2-motor` (diff `origin/main...HEAD`, 2026-11-05)

Ningún hallazgo grave. Los medios se arreglan en la rama, cada uno con su test (rojo sin el arreglo, salvo el 4); los leves quedan
como pendientes y no se revisan más en este PR.

**Medio**
1. `gimg/doctor.py` ~379 `_template_files`: resolvía cada plantilla con `compose_mod._asset(proj["root"], rel, …)`, pero una plantilla
   local (guardada con `gimg template save`) es relativa a su `templateRoot`. Daba un WARN falso `doctor.templates.bad` y no corría
   `_element_problem`. **Hecho:** la plantilla se resuelve con el `templateRoot` de `compose.effective(...)` (el logo sigue dentro del
   proyecto) y la marca de «ya comprobado» incluye esa raíz. Test: `tests.test_template_save.SourcesTests.test_a_local_template_saved_alone_does_not_warn_in_doctor` (rojo sin el arreglo).
2. `gimg/queue.py` ~450 `submit_order`: `models_mod.check_allowed` (pasos del modelo frente a `maxSteps`) solo corría en `enqueue`, con el
   pedido ya guardado. **Hecho:** `orders.check_order` devuelve las specs candidatas y `queue.check_specs` (límites, modelo, plantilla)
   la comparten `enqueue` y `submit_order`; la lógica no se duplica. Test: `tests.test_f4d_engine.OrderModelTests.test_a_model_over_max_steps_stores_and_queues_nothing`
   (`limit.steps` con 16 y 10, ningún pedido guardado, cola vacía; rojo sin el arreglo).
3. `gimg/ui/js/components/order-view.js` ~93 `retry`: reenviaba `steps`, `cfg` y `sampler` pero no el modelo del intento (F4d). **Hecho:**
   reenvía `model` (de `e.params.model`) cuando no es el del pedido ni el del perfil. `recreate` y `vary` no tienen el hueco: pasan por
   el selector de modelo del panel de retoque (`load` lo rellena y `spec` lo manda). Test: `tests.test_ui.ReviewFixes.test_retry_resends_the_model_of_the_entry_when_it_is_not_the_profile_one` (rojo sin el arreglo; es estático, no hay JS ejecutable en los tests salvo el Chrome headless).
4. `order-view.js` ~45: `ctx.measure.zone` sale del perfil. **Hecho: nada que cambiar.** `measureFor` (`slots.js`), que usan `attempt-card.js` y
   `compare-view.js`, ya resuelve la zona por intento con la `zone` de la plantilla de ese intento (`templateOf` → `ctx.templates`, que
   trae `zone` de `effective`) y deja la del perfil solo de respaldo. Se añade `test_the_measured_zone_is_the_one_of_the_template_of_each_attempt`, que lo fija (pasa también sin cambios).
5. `gimg/ui/js/components/layout-editor.js` ~85: `applied0` solo miraba `attempt.compose.layout`; si la última composición falló, `compose`
   desaparece y la maqueta queda en `composeError.layout` (`orders.py`). **Hecho:** `(attempt.composeError || attempt.compose || {}).layout`.
   Test: `tests.test_ui.LayoutEditor.test_the_applied_layout_falls_back_to_the_one_of_the_compose_error` (rojo sin el arreglo). Nota:
   `editorSlot` solo abre el editor con `compose` y sin `composeError`; no se cambió, así que el arreglo cubre un editor ya abierto cuando falla.

**Leve (pendientes)**
6. `gimg/compose.py` ~416 `_contrast_of` decodifica la imagen con `measure.pixels` una vez por elemento de texto y en cada recomposición.
7. `gimg/compose.py` ~891 `save_template`: si el proceso muere entre escribir `<nombre>.json` y el SVG queda el `.json` huérfano, y `O_EXCL` bloquea ese nombre.
8. `gimg/compose.py` ~173 `_sidecar` no comprueba que `zone` quepa en `target_size`.

**Sin verificar:** `gimg queue list` quizá ordena por archivo y no por `position`.
