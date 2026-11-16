# Pedidos del encargo UX-41 (Tarkor)

Encargo: `docs/proposals/tarkor/encargo-ux41-2026-11-15.md` (23 puntos). Aquí hay **46 pedidos y 115 imágenes**
(suma de `count`): 3 intentos por pieza, 2 por cada una de las 23 categorías del punto 17. Clave `ux41/<nn>-<nombre>`,
con `<nn>` = punto del encargo. Escritos el 2026-11-16, sin encolar.

Encolar todos, desde la raíz del repo:

```sh
for f in examples/tarkor/orders/ux41/*.json; do python3 -m gimg order submit tarkor "$f"; done
```

## Punto del encargo → pedido

| Punto | Pedido (`ux41/…`) | Perfil | Motivo |
|---|---|---|---|
| 1 | `01-estado-aviso` | icono | triángulo de oro con exclamación, filete ámbar |
| 2 | `02-estado-error` | icono | aspa de oro sobre sello de lacre rojo oscuro |
| 3 | `03-estado-hecho` | icono | marca de verificación sobre sello verde musgo |
| 4 | `04-fase-ocupado` | icono | reloj de arena |
| 5 | `05-fase-eleccion` | icono | camino que se bifurca en Y, con dos puntas de flecha |
| 6 | `06-categoria-medicinal` | icono | mortero con mano y dos hojas |
| 7 | `07-pestana-enciclopedia` | icono | tomo cerrado con broche y un ojo en la tapa |
| 8 | `08-pestana-mapa` | icono | mapa desplegado con ruta a trazos y una X |
| 9 | `09-pestana-leyendas` | icono | arpa de bardo |
| 10 | `10-pestana-personaje` | icono | busto con capucha |
| 11 | `11-hud-energia` | icono | rayo |
| 12 | `12-dado` | icono | dado de oro, caras 1-2-3, pieza suelta |
| 13 | `13-pestana-misiones` | icono | estandarte con una diana grande |
| 14 | `14-pestana-reputacion` | icono | balanza |
| 15 | `15-fase-fin` | icono | puerta cerrada en arco |
| 16 | `16-hud-hambre` | icono | muslo asado |
| 17 | `17-categoria-<nombre>` (23) | icono | ver la tabla de abajo |
| 18 | `18-barra-relleno-neutra` | tira | relleno gris claro, para teñir por código |
| 19 | `19-barra-pista-baja`, `19-barra-relleno-baja` | tira | versiones bajas con el borde de oro en un hilo |
| 20 | `20-esquina-oro` | icono | esquina toda de oro, brazos gruesos, remate en cada punta |
| 21 | `21-favicon` | icono | gema azul sobre medallón de oro |
| 22 | `22-logo-gema` | icono | solo la gema suelta; el nombre no lo pinta el modelo (montaje abajo) |
| 23 | `23-og-cielo` | og | solo el cielo, con el centro vacío; el logo se superpone (montaje abajo) |

Categorías del punto 17: piedra (peñasco), mena (roca con pepitas y pico), comida (cuña de queso), bebida (jarra con
espuma), piel (piel extendida vista desde arriba), fibra (huso con hilo), cuerda (rollo con un cabo anudado), metal
(tres lingotes), gema (gema tallada de perfil, cristal azul), semilla (semilla con brote), hierba (ramita de hojas
pareadas), mueble (silla de perfil), montura (silla de montar con estribo), trampa (cepo abierto), munición (haz de
tres flechas), instrumento (laúd), joya (collar con colgante), llave, libro (dos libros apilados de canto), poción
(botella panzuda con líquido azul), veneno (vial anguloso con calavera), ingrediente (dos setas), otro (caja de madera).

## Decisiones: elegido por el agente (delegado)

- **Dos recetas de medallón.** Las piezas `pestana-*`, `hud-*`, `estado-*` y `fase-*` llevan la receta nueva del
  encargo: medallón de tablas con aro de piedra fino (8 % del diámetro), motivo al 70 %, «bold chunky silhouette with
  thick strokes». Las **categorías** (puntos 6 y 17) conservan la receta de la serie (`orders/ui/15-categoria-*`: hueco
  al 80 %, motivo al 60 %) para casar con las 14 ya aprobadas: el encargo limita el cambio de aro a los cuatro grupos de
  iconos pequeños. Si Tarkor quiere también las categorías con aro fino, se rehacen las 37 a la vez.
- **Motivo elegido donde el encargo da a elegir:** error = aspa sobre sello (no escudo partido); elección = camino en Y;
  medicinal = mortero; mapa = mapa con ruta y X (sin «parchment» ni «scroll», que dieron el pergamino); leyendas = arpa
  (silueta triangular, lejos del libro del diario y del laúd de `categoria-instrumento`); reputación = balanza; fin =
  puerta cerrada; hambre = muslo asado.
- **Rediseños respecto a lo ya fallado** (apuntados en `docs/records/troubleshooting-hojas-repos.md`): reputación pasa
  del laurel a la balanza (una corona es un círculo abierto y a 16-24 px vuelve a leerse como el anillo de accesorio);
  fase fin pasa del pergamino a la puerta (el pergamino choca con mapa y leyendas); comida es una cuña de queso (la
  hogaza salió con «%» grabado y el muslo es de `hud-hambre`); piel usa el rediseño ya escrito y sin probar.
- **Colisiones evitadas entre categorías:** gema de perfil ancho (la de habilidades es un cristal alto); joya = collar
  (accesorio es un anillo); libro = dos tomos de canto (diario es un libro abierto, enciclopedia un tomo de frente);
  poción panzuda con líquido azul y veneno anguloso con calavera (consumible es un frasco); hierba = ramita en pie
  (medicinal era el manojo); instrumento = laúd (encuentro es un cuerno, leyendas un arpa).
- **Sin negaciones ni palabras vetadas** (P2 y P3 de `docs/marcas/tarkor/hoja.md`): la diana de misiones se pide como
  «target», la exclamación como «exclamation mark»; todo en positivo. Contra el reflejo verde en el oro, una frase en
  positivo antes del croma: «The gold keeps its own warm colour right up to its edges».
- **Croma verde `#00ff00` en todo**, también en `03-estado-hecho` (musgo oscuro `#4f5f33`, a 182 de distancia del
  croma: `gimg brand matte` con `--tol 60 --soft 110` no lo toca). Margen del 15 % (el encargo pide ≥ 10 %).
- **Dado:** pieza suelta de oro con puntos oscuros hundidos, como el aprobado q1068. P7 de la hoja pide de 6 a 10
  semillas cuando importa un recuento; el pedido lleva 3: si ninguna trae 1-2-3 bien puestos, más intentos con
  `gimg attempt new`, y si tampoco, los puntos van por SVG encima.
- **Barras en el perfil `tira`** (1024×128, el de e07 aprobado q660/q662), con el bloque reducido de
  `docs/marcas/tarkor/peticiones.md` (sin madera ni piedra ni luz rasante, que se colaban) y sobre croma, para no tener
  que recortar un fondo de madera como en e07. `tira` es FLUX: para cumplir P6 (Z-Image en lo que se entrega),
  encolar las tres con `--model zimage-turbo-q6` es decisión de la sesión principal (Z-Image a 1024×128 está sin
  probar).
- **Barras bajas:** se piden a un cuarto del alto del lienzo (≈ 32 px), no a 16: a 16 px el modelo no dibuja el hilo de
  oro. Se recortan a ≈ 900×32 y se reducen a 900×16 (abajo).
- **Esquina:** toda de oro (la aprobada q1005 salió con brazos de madera y poco oro), brazos de un quinto de su largo,
  remate en punta de flecha de oro y contorno de bronce oscuro grueso, que es lo que separa el oro del croma. El filo
  verdoso se quita al recortar, con `--grow 4`.
- **Favicon y gema del logo** se generan a 512² (`icono`, Z-Image) y se reducen con `gimg export`.
- **og:** el perfil `og` (Z-Image, 1280×640 → 1200×630) compone solo con el lockup de la Semilla que fija
  `galivelop-images.json`; el og del encargo (gema + «TARKOR») se monta a mano desde la imagen cruda, o desde el cielo
  aprobado `06-cielo-q998.png`.

## Pendiente de decidir (no es del agente)

- El encargo pide **la gema azul** como símbolo (favicon, logo, og). La hoja de Tarkor (L1 y §4) fija el emblema de la
  Semilla y los SVG de `docs/marcas/tarkor/logos/`, y deja la gema como el concepto **b**, no elegido. Estos pedidos
  siguen el encargo; qué símbolo es el oficial lo decide la persona.
- `10-pestana-personaje` es un busto con capucha: la hoja veta personajes en piezas **de marca**; aquí es un icono de
  interfaz pedido por Tarkor.

## Montaje (tras elegir los intentos)

`E` es la carpeta de entrega del proyecto (`<raíz de tarkor>/entrega/ux41`), `L` una carpeta de trabajo y `F` la fuente
(`Cinzel[wght].ttf`, en `$XDG_DATA_HOME/fonts/galivelop/`). Las órdenes se probaron el 2026-11-16 con piezas de
prueba (q1022 como gema y q998 como cielo); con las piezas reales, sin probar.

**Recorte de cualquier pieza sobre croma** (`--holes` si encierra verde, como el arpa o la balanza):

```sh
python3 -m gimg brand matte "$E/20-esquina-oro-icono.png" --grow 4 -o "$L/esquina-oro-alpha.png"
```

**Favicon (21):**

```sh
python3 -m gimg brand matte "$E/21-favicon-icono.png" --grow 4 -o "$L/favicon-alpha.png"
python3 -m gimg export "$L/favicon-alpha.png" "$L/favicon.ico" --icon-sizes 16,32,48
python3 -m gimg export "$L/favicon-alpha.png" "$L/favicon-32.png" --size 32x32
python3 -m gimg export "$L/favicon-alpha.png" "$L/favicon-16.png" --size 16x16
```

**Logo (22):** gema a SVG, nombre a trazos y lockup vertical (gema encima). El nombre es el SVG de la marca
(`tarkor-wordmark.svg`, Cinzel 800); a 1200 px se le ven los escalones del trazado: si molestan, se rehace con la
segunda orden y se usa `$L/wordmark.svg` en la tercera.

```sh
python3 -m gimg brand trace "$E/22-logo-gema-icono.png" --matte --mode color \
  --palette '#4aa8d8,#a8d8f0,#1f4a55,#b8862b,#f2c45a,#5a3a14' -o "$L/tarkor-gema.svg"
python3 -m gimg brand wordmark TARKOR --font "$F" --weight 800 -o "$L/wordmark.svg"   # opcional
python3 -m gimg brand lockup "$L/tarkor-gema.svg" docs/marcas/tarkor/logos/tarkor-wordmark.svg \
  --layout v --width 6 --gap 0.2 --color '#b8862b' -o "$L/tarkor-gema-lockup-v.svg"
rsvg-convert -w 1200 -h 400 --keep-aspect-ratio -o "$L/logo-raw.png" "$L/tarkor-gema-lockup-v.svg"
ffmpeg -i "$L/logo-raw.png" -vf "format=rgba,pad=1200:400:(ow-iw)/2:(oh-ih)/2:color=0x00000000" \
  -frames:v 1 "$L/logo-1200x400.png"
```

`--width 6` da un lockup de 2,9:1 (1169×400 antes de centrarlo en 1200×400). La gema trazada ocupa su lienzo entero
con el margen del croma: si queda pequeña, `gimg crop` del intento a la caja de la gema antes de trazar.

**og:image (23):** cielo a 1200×630 y el logo centrado al 70 % del ancho. El cielo es la imagen cruda del intento
elegido de `ux41/23-og-cielo` (la entrega del perfil `og` ya lleva compuesto el lockup de la Semilla) o, sin generar
nada, el aprobado q998 (su cinturón cruza el centro, por detrás del logo).

```sh
python3 -m gimg export piloto/tarkor-final/06-cielo-q998.png "$L/cielo-og.png" --size 1200x630
rsvg-convert -w 840 --keep-aspect-ratio -o "$L/logo-og.png" "$L/tarkor-gema-lockup-v.svg"
ffmpeg -i "$L/cielo-og.png" -i "$L/logo-og.png" -filter_complex "overlay=(W-w)/2:(H-h)/2" \
  -frames:v 1 "$L/og-1200x630.png"
```

**Barras (18 y 19):** recorte del croma y, en las bajas, reducción solo en vertical (el borde queda más fino, que es
lo que pide el punto 19).

```sh
python3 -m gimg brand matte "$E/19-barra-pista-baja-tira.png" -o "$L/pista-baja-alpha.png"
ffmpeg -i "$L/pista-baja-alpha.png" -vf "crop=900:32,scale=900:16:flags=lanczos" -frames:v 1 "$L/barra-pista-900x16.png"
```

La caja de `crop` se ajusta a la barra que salga (`crop=ancho:alto:x:y`). **Alternativa para el punto 18, sin
generar:** el relleno aprobado en gris, con la misma forma y tamaño exactos (864×48):

```sh
ffmpeg -i piloto/tarkor-final/e07-barra-relleno-q662.png \
  -vf "format=rgba,hue=s=0,eq=brightness=0.18:contrast=0.9" -frames:v 1 "$L/barra-relleno-neutra.png"
```
