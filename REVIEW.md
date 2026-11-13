<!-- galivelop-workflow v0.5.0 -->
# Guía de revisión

Lo que el revisor (`/code-review`, o cualquier agente que revise un diff) comprueba en cada diff de galivelop-image-generator,
además de los fallos de siempre. Lo mecánico ya lo hacen el check (`for f in .githooks/pre-commit .githooks/pre-push .githooks/commit-msg; do bash -n "$f"; done`) y los ganchos de git; aquí está lo que
pide criterio. Cada regla acaba en `(check: …)`, con lo que la hace cumplir, o en `(criterio)` si no hay check; una
regla mecánica marcada `(criterio)` pide su check. La rellena el proyecto; el flujo nunca la sobrescribe una vez
creada.

## Cómo se informa

- Antes de dar un hallazgo, intenta refutarlo: busca el código, el test o el gancho que ya lo cubre. Solo se informa
  de lo que sobrevive, con la ruta y la línea. (criterio)
- Los hallazgos se escriben también en un archivo fuera del árbol (el scratchpad, o
  `"$(git rev-parse --git-dir)/review.md"`), no solo en la conversación: una compactación o un relevo se los lleva, y
  de ese archivo salen los encargos de los arreglos y los leves que se apuntan en la bitácora. (criterio)
- Un dato que caduca (una versión, un precio, una cuota, un límite de un servicio externo) escrito en el diff lleva su
  fecha y su fuente; si no, es un hallazgo. (criterio)
- La revisión acaba con un veredicto, uno de tres: `SHIP` (nada que arreglar), `SHIP WITH FIXES` (hay arreglos, ninguno
  bloquea) o `DO NOT SHIP` (algo grave o que rompe). (criterio)

## Un dato, un sitio

- Un dato que ya vive en un sitio (un archivo de configuración, uno de datos, una constante) no se repite a mano en
  el código, la documentación ni el README; si hay que repetirlo, todas las copias cambian en el mismo commit.
  (criterio)
- La configuración del flujo vive solo en `.claude/gw.json` y solo la lee `.claude/gw/scripts/config.py`. (criterio)

## Ganchos y scripts

- La raíz del repo se saca de la ruta del script (`$(dirname "$0")`) o de `git rev-parse --show-toplevel`, nunca de
  `$CLAUDE_PROJECT_DIR` ni del directorio actual: una sesión puede arrancar fuera del repo. (criterio)
- Un gancho de subida comprueba **el commit que se sube**, no la carpeta de trabajo. (criterio)
- Los ganchos **fallan cerrados** cuando les falta un dato (un commit que el clon no tiene, una API que no responde),
  con la orden que lo arregla. Excepción razonada: las claves de rutas (`log`, `reviewMark`, `recordsDir`,
  `proposalsDir`, `ciLocalLog`) son opcionales con defecto en inglés, así que una ausente no es un dato que falte.
  (criterio)
- Los scripts de shell corren en bash 3.2 (macOS): nada de `mapfile` ni arrays asociativos. Lo mecánico (`readlink -f`,
  `mapfile`, `declare -A`, `${v,,}`, `wc` comparado como cadena) lo comprueba `tests/test_portabilidad.py`; la revisión
  mira el resto (opciones de GNU en `sed`, `date`, `stat`…). (check: `tests/test_portabilidad.py`, en parte)
- Una carpeta con nombre fijo en un directorio compartido (`$TMPDIR`, `/tmp`) es por usuario, se crea con permisos 700
  y se rechaza si ya existe como symlink o de otro usuario; los archivos sueltos, con `mktemp`. (criterio)
- Cada cambio en un gancho o un script lleva su caso en los tests; un caso que espera un fallo comprueba el motivo,
  no solo el código de salida. Vale para los scripts propios del proyecto. (criterio)
- Los scripts de `.claude/gw/scripts/` se prueban en el repo del flujo y no se editan aquí: un cambio va al flujo
  como propuesta, con `gw-harvest` (check: `config-guard.py` pregunta antes de editarlos). (criterio)
- Un gancho que pregunta o bloquea se revisa **probando cómo saltárselo**: envoltorios con opciones que llevan valor
  (`sudo -u X`, `sudo -uX`, `env -u X`, `nice -n 5`, `timeout 5`, `xargs -I{}`), el destino de los copiadores (`cp`,
  `install`, `rsync`, `dd of=`, `-t DIR`), una carpeta antecesora de la protegida y una ruta relativa o con `..`; y
  los falsos positivos habituales (leer o copiar **desde** la carpeta, `git restore --staged`). Cada forma, su caso.
  (criterio)
- `pkill -f <patrón>` (y `pgrep -f`) casa también con la orden que lo lanza cuando el patrón va en ella
  (`bash -c "… pkill -f servidor"`), y la mata: un pidfile, `pgrep -x` o un patrón que no se case a sí mismo
  (`[s]ervidor`). (criterio)
- Un runbook o encargo que sigue una tarea programada (una sesión sin persona delante) se revisa como código, aunque
  case con `content`: lo que dice se ejecuta tal cual. (criterio)

## Traído de otro repo: se adapta a los contratos de este

- El código, los scripts o las reglas traídos de otro repositorio se comprueban contra **este** repo, no contra el
  original: formatos, rutas, extensiones de archivo, patrones de nombres, constantes, claves de configuración e
  identificadores de tarea. (criterio)
- Lo que viene de un proyecto que sube de otra forma (directo a la rama protegida, o por pull request) se adapta a
  cómo sube este a `main`. (criterio)
- Una tabla o un ejemplo de una guía que lee un script lo lee ese script en un test. (criterio)

## Idiomas visibles

- Si `.claude/gw.json` declara `visibleLanguages`, todo texto nuevo que vea un usuario existe en cada uno de esos
  idiomas (etiquetas, textos alternativos, títulos de página, mensajes), y una traducción es de verdad, no el mismo
  texto. (criterio)

## Reglas del proyecto

<!-- Las rellena el proyecto: lo que nunca se publica, reglas del dominio, accesibilidad, rendimiento, seguridad. -->

- **Rutas y nombres de archivo (D25).** Todo campo o código que acabe en una ruta o un nombre de archivo tiene tests
  que rechazan `\n`, `\x00`, rutas absolutas, `~` y segmentos `..`, y la guardia de verdad resuelve la ruta (con
  enlaces) y comprueba que queda dentro; el regex de un esquema solo ayuda al editor.
- **Esquemas con semántica estándar.** Los esquemas los leen también otros validadores (ajv, el editor; D17): un
  `pattern` sigue ECMA-262 y un tipo sigue JSON Schema 2020-12. Que `gimg/schema.py` dé otro resultado que el
  estándar sobre el mismo dato es un hallazgo.
- **CHANGELOG por fase.** Un PR que cierra una fase (o trae algo visible para el usuario) añade su entrada en
  `CHANGELOG.md` y `CHANGELOG.es.md`; las notas de cada release de GitHub salen de ahí (`releases.py notes`). Que
  falte es un hallazgo medio. (criterio)
- **Tabla de estados HTTP.** `gimg/server.py` mapea todos los códigos de error, también los de órdenes solo de CLI, y
  `tests/test_server.py` lo exige: un código nuevo va a esa tabla o a la lista de 500 del test. Que esté sin endpoint
  no es un hallazgo; que falte, sí (lo pilla el test). (criterio)
