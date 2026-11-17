# Revisión de bloque — `hoja-datos`, paso 2 (2026-11-17)

Revisión de bloque (fase 1) de `ce7dc83..8a0d78b` (pasos 2A `cc2e3a4` y 2B `8a0d78b`): `/code-review --max-findings all`
con el criterio de `REVIEW.md`, solo código y tests (sin `docs/` ni `docs/metrics/ledger.jsonl`). Contrato:
`docs/interfaz/marca.md` §4 y §2.10, `docs/plan.md` «FM en detalle». No se repite lo ya apuntado en `docs/handoff.md`
(fila `hoja-datos`) ni en `revision-hoja-datos-paso1.md`. Hay 12 hallazgos: 0 graves, 2 medios y 10 leves.

**Veredicto:** `SHIP WITH FIXES`.

Comprobado y bien:

- `GET /api/projects/{p}` amplía con `sheet` y `pieceTypes`, y un proyecto sin hoja da `present: false` sin error.
- `brand/prompt` y `brand/lint` no pasan por `_heavy()`, y `lint` va siempre en `free`, así que nunca da `blocked`.
- `brand prompt --json` y `POST …/brand/prompt` dan lo mismo (lo comprueba un test).
- La guarda D25 de la hoja propia está en `brand init` (`paths.inside`).

## Medios

1. **`gimg/doctor.py:455` y `gimg/server.py:48`: si falta la hoja del padre, se culpa a la hoja del hijo.**
   - `resolve` llama a `_project_sheet(padre, hijo)`, y `load()` lanza `brandsheet.missing` con la ruta del padre.
     `_project_sheet` solo convierte en `extends_missing` los casos «padre sin registrar» y «padre sin `brand.sheet`».
   - Escenario: el proyecto A tiene `marca.json` con `extends: B`, y B declara `brand.sheet`, pero su archivo se borró.
     - `GET /api/projects/A/check` da `sheet.present FAIL: no existe la hoja de marca declarada: marca.json`, que es la
       ruta de A, y propone el arreglo `gimg brand init --project A`.
     - Esa orden falla con `brandsheet.exists`. Con `--force`, pisa la hoja buena de A.
     - `GET …/A/brand/sheet` y `POST …/A/brand/prompt` dan 404 `brandsheet.missing`, cuando el contrato pide 422 para
       un padre roto.
   - Variante: si la config del padre no es válida, `project.config_invalid` sale por `resolve`:
     - `doctor` lo pinta como `sheet.valid FAIL` con el arreglo «corrige la hoja <la de A>».
     - La API da 500.
   - **Arreglo:** en `_project_sheet`, con `child` definido, convertir `brandsheet.missing`, `unreadable`, `invalid`,
     `project.config_*` y `path.*` del padre en `brandsheet.extends_missing` (o en un código `extends_broken` con la
     causa). El test: padre registrado con su archivo borrado, comprobando el código y que el arreglo no es
     `brand init`.
2. **`gimg/doctor.py:471-476`: `sheet.contrast` mide el acento vivo, y en la familia avisa siempre.**
   - Por diseño, el acento de la hoja es el vivo. Sus tonos para texto los calcula `accent_tones` y no se guardan
     (esquema: «The deep and dark tones of the accent are computed, not stored»).
   - Escenario: un producto de la familia con acento `#0e9a93`, como el fixture `family` de
     `tests/test_brandsheet.py:158`, da 3,37:1. El `#1aa6df` del Portal da 2,70:1. La fila `sheet.contrast` queda en
     `warn` para siempre en hojas correctas, y la pestaña Comprobación enseña un aviso falso con el arreglo «corrige la
     hoja».
   - **Arreglo:** para el acento, comprobar que existe el tono hondo (`accent_tones(...)["deep"]`, y `warn` solo con
     `brandsheet.no_tone`). Si se quiere el dato, decir el contraste del tono hondo. La tinta sigue como está. Test con
     el acento teal en `ok`.

## Leves (se apuntan; no se arreglan en este PR salvo que caigan de paso)

3. **`gimg/cli.py:334-341`: `brand init --extends P` solo comprueba que P está registrado.**
   - `--extends A` sobre el propio A, o un P sin `brand.sheet`, escriben y enlazan una hoja que nunca resuelve: todo lo
     posterior da `extends_cycle` o `extends_missing`.
   - **Arreglo:** rechazar `P == project` y llamar a `brandsheet.resolve(P)` antes de escribir.
4. **`gimg/server.py:50`: `brandsheet.bad_placeholder` (contenido de la hoja) queda fuera del grupo 422.**
   - Por la regla `.bad_`, da 400.
   - Escenario: un `paletteSentence` con `{halo}` sin `halo` en la paleta hace que `GET …/brand/sheet`, `prompt` y
     `lint` den 400, como si la petición estuviera mal.
   - El punto 10 del paso 1 lo dejaba para el paso 2, y se decidió solo para el resto de códigos.
   - **Arreglo:** añadirlo, y `bad_hex` si es alcanzable, a la tupla 422 con su test.
5. **`gimg/cli.py:326-327`: el destino de `brand init` no se protege como `delivery.dir` y `manifest`.**
   - `load_config` solo pasa `paths.inside` a `brand.sheet`, sin `_forbidden`.
   - Escenario: con `brand.sheet: "galivelop-images.json"` (una errata), `gimg brand init --force` sustituye la config
     del proyecto por la hoja, y el proyecto deja de cargar. Lo mismo vale para una ruta bajo `.git/`.
   - **Arreglo:** `_forbidden(root, "brand.sheet", sheet)` en `load_config`.
6. **`gimg/cli.py:348-350`: enlazar la hoja reescribe la config del usuario con `fsutil.write_json`.**
   - `write_json` ordena las claves y reindenta. Es la primera vez que gimg escribe esa config, y un campo nuevo deja
     un diff de todo el archivo en el repo del proyecto.
   - **Arreglo:** escribir sin `sort_keys` (conserva el orden de `json.load`), o solo avisar con la línea que hay que
     añadir.
7. **`gimg/cli.py:342-350`: hoja y enlace son dos escrituras sin lock.**
   - Si la segunda falla, queda una hoja sin enlazar, y repetir la orden sin `--force` da `brandsheet.exists`.
   - Una edición concurrente de la config entre `read_json` y `write_json` se pierde.
   - **Arreglo:** enlazar primero, o con el error decir que se repita con `--force`; `fsutil.lock` sobre la config.
8. **`gimg/doctor.py:452`: el mensaje de error se pinta en `i18n.default_lang()` y viaja como parámetro.**
   - Con el servidor en `es` y la petición en `lang=en`, la fila sale como «the brand sheet is not valid: la hoja de
     marca … no es válida».
   - **Arreglo:** pasar el código y los parámetros de la excepción y pintarlos en `as_dict(lang)`.
9. **`gimg/doctor.py:488` frente a `run` (l.489-505): `gimg doctor` no ejecuta `_sheet`.**
   - El docstring de `run_project` dice «the same functions as `run`, limited to `name`», pero `run` recorre
     `_fonts()` y `_template_files()` de todos los proyectos y no las hojas.
   - **Arreglo:** un `_sheets()` en `run` sobre `list_projects()`, o corregir el docstring.
10. **`gimg/brandsheet.py:533-560` (`status`), `:568-577` (`sheet_view`) y `:516` (`prompt_response`): lecturas
    repetidas.**
    - `GET /api/projects/{p}` lee y valida la config tres veces y la hoja propia dos.
    - `sheet_view` repite `projects.get` por cada dueño de la cadena, y `prompt_response` lo repite para los perfiles.
    - **Arreglo:** que `resolve` devuelva las configs o rutas que ya leyó, y pasar el proyecto a `status`.
11. **`gimg/cli.py:309-345`: `_brand_init` repite `brandsheet.declared()` (l.325 y l.344).**
    - `STARTER_SHEET` repite a mano `PAPER_LIGHT`.
    - Un futuro `POST …/brand/init` tendría que importar de `cli`.
    - **Arreglo:** mover `STARTER_SHEET` y la lógica de `init` a `brandsheet.py` («what the CLI and the API both
      serve»), y usar `PAPER_LIGHT`.
12. **`tests/test_server_sheet.py:130`: `test_rows_of_a_good_sheet` acepta `sheet.contrast` en `ok` o en `warn`.**
    - Así no comprueba el caso bueno. Con el punto 2 arreglado, debe exigir `ok`.

Fuera del alcance (documentación): en `docs/api.md:403` y `docs/en/api.md`, la frase nueva se metió tras un
«Error:» que quedó colgando.
