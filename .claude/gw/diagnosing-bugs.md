# diagnosing-bugs — notas del proyecto

Las lee la skill `diagnosing-bugs` antes de empezar. Son del proyecto. Origen: retro 2026-11-06
(`docs/records/retro-2026-11-06-ci-rojo-y-prueba-inestable.md`), propuesta también al flujo.

## Fallo caro de reproducir

Cuando el bucle rápido de la fase 1 no se puede construir porque el fallo solo aparece en un sitio caro (1 de cada N
pasadas del check largo, solo en el CI, solo en Chrome), **mide antes de arreglar**: el arreglo espera a una medida
que decida entre las hipótesis de la fase 3.

1. **Prueba inestable:** el mensaje de fallo de la prueba recoge la evidencia que separa las hipótesis (estado,
   pids, versiones, stderr de cada proceso, valores intermedios). Se sube así y se espera el siguiente fallo natural;
   se arregla cuando ese mensaje decide la causa. Después, varias decenas de pasadas seguidas en verde.
2. **Fallo solo en el CI o en otro navegador:** sin ese entorno en local, una rama de diagnóstico propia mide allí
   (rectángulos, tamaños, valores en el mensaje de la aserción) y se empuja para que la corra el CI. El arreglo va
   después, en la misma rama, y se fusiona con el CI en verde en ella.
3. **El commit del arreglo cita la salida que decidió la causa** y nombra las hipótesis descartadas (lo exige
   `REVIEW.md`).

Ejemplos: la prueba de autoarranque (`ca6cea2` diagnóstico, `ec89eb0` arreglo) y el editor a 360 en Chrome
(`f3aeb47` diagnóstico, `f4cd0be` arreglo, tras dos arreglos de hipótesis sin medir).
