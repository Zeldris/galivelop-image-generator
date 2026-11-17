# Pedido del Portal (2026-11-17, tarde): revisión de `portal-web-final/tarkor/`

Copia del mensaje de la sesión del Portal; estado de cada punto al final.

## 1. 23c icono de Tarkor (q1417, aprobado): rehacer solo el SVG

- El trazo de `svg/23-icono-tarkor.svg` sale en escalones de píxel (`L338 113 L345 113 L345 114…`): a 1024 px se ven
  los dientes. Retrazar con curvas suaves: subir el original a 2048² antes de trazar, o suavizar el contorno (Bézier,
  no segmentos de 1 px). Un solo color, #E0703A, y el hueco del colmillo vacío (sin `--matte`).
- `viewBox` recortado al dibujo y cuadrado, margen de ~8 %: ahora es `0 0 512 512` y el dibujo ocupa 139-371 ×
  113-405, así que sale pequeño y descentrado en el menú. Algo como `viewBox="101 105 308 308"`, centrado en el dibujo.
- Comprobar que se lee a 24 px (sobre blanco y sobre #0b1220); si el trazo se pierde, engrosarlo ~1,5× sin cerrar el
  hueco ni pegar el cordón al colmillo.
- Regenerar `23-icono-tarkor.png` 512² desde el SVG nuevo y poner la línea de comando en el LEEME.

## 2. 24c og de Tarkor (q1414, en `pendiente/`): no vale; rehacer (3-4 intentos)

Fallos: un colmillo grande con grieta, cuya raíz parece la boca hueca de un cuerno, y otro pequeño colgado del cordón
(se pedían dos parecidos); el grande cruza la mitad izquierda, que tiene que quedar limpia para el texto.

Pedido: 1200×630, grabado antiguo en dos tintas, como las otras placas 24 (q932 anillo, q1150 rosa, q1157 boyas): mar
en calma con olas grabadas en líneas paralelas, sin horizonte. Dos colmillos de marfil parecidos en tamaño y curva,
cruzados o en paralelo, atados por la base con un cordón y una sola cuenta naranja #E0703A, flotando a la deriva en el
tercio derecho, con ondas concéntricas suaves alrededor. La base de cada colmillo, maciza y redondeada (nada de boca
hueca, grietas ni aspecto de cuerno). La mitad izquierda, solo agua tranquila, sin objetos ni ondas fuertes (va texto
encima con velo oscuro). Nada toca los bordes. Sin texto, sin barcos, sin sombras duras ni reflejos fotográficos; no
es foto ni pintura.

Al juzgar: los dos colmillos se leen como colmillos a 600×315 y la zona izquierda está limpia.

Idea para no repetir los fallos (troubleshooting): composición con FLUX (dos colmillos en el tercio derecho, izquierda
vacía) y grabado con Z-Image img2img, como 31f.

## 3. (Opcional) 31f

Mover q1425-1428 a `top` al reanudar la cola.

## Estado

| Punto | Estado |
|---|---|
| 1 SVG del icono | hecho (2026-11-17): curvas, `viewBox` 314 329 1412 1412, trazo ~1,5×, PNG 512² regenerado; a 24 px se lee como silueta del colmillo, el cordón se funde |
| 2 og 24c | rehecho como 24d: composición FLUX q1429-1432 en cola (17-11); falta grabado img2img |
| 3 31f a top | hecho (17-11, cola reanudada) |
