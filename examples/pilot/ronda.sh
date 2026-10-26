#!/bin/bash
# F2.0: lanza una ronda del piloto de contenido con el generar.sh de Tarkor, que solo se ejecuta (su repo no se toca):
# la salida va a piloto/<ronda>/<proyecto>/{intentos,logs,prompts}/ (en el repo, fuera de git; PILOTO=<carpeta> para otra),
# el resumen a piloto/<ronda>/resumen.txt y la página de revisión a piloto/index.html (examples/pilot/pagina.py).
# Uso: examples/pilot/ronda.sh r0|r1|r2|r3   (con el juego, el navegador y Ollama cerrados)
# r0: humo, el og del Portal con semilla 3. r1: el og de cada proyecto con semillas 3 y 4, y una hoja de contacto.
# r2: las tres variantes de estilo de cada proyecto (prompts/r2-{palabras,hex,material}.txt) con semilla 3, y su hoja.
# r3: borrador (640×320, 4 pasos) contra definitivo (1280×640, 8 pasos) del estilo elegido (prompts/estilo.txt) con
# FLUX.2 klein; en R3_FLUX3 (por defecto portal), además FLUX.3 a 640×320/8 y 1280×640/16 pasos (tope R3_TOPE, 7200 s).
# TARKOR_GEN=<ruta de generar.sh> para otra copia; salta lo que ya existe, así que una ronda cortada se relanza igual.
# sin pipefail: generar.sh devuelve 3 si aborta antes de arrancar (memoria, Ollama) y entonces se para la ronda entera
set -u
R=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
GEN=${TARKOR_GEN:-$R/../WMF-imagenes/image-generator/scripts/generar.sh}
PILOTO=${PILOTO:-$R/piloto}
RONDA=${1:-}
PROYECTOS="portal toveriai galivelop-workflow tarkor galivelop-image-generator galivelop-voice-generator galivelop-developer"
N=$(echo $PROYECTOS | wc -w)
# Cada pieza es proyecto:prompt:semilla[:ancho:alto:pasos[:modelo]] (examples/<proyecto>/prompts/<prompt>.txt); por
# defecto 1280×640, 6 pasos y el modelo de generar.sh. La imagen, <prompt>-s<semilla>, o <prompt>-<ancho>x<alto>-p<pasos>
# [-<modelo>]-s<semilla> si la pieza da tamaño.
case $RONDA in
  r0) PIEZAS="portal:og:3"; COLS=1 ;;
  r1) PIEZAS=""; for q in $PROYECTOS; do PIEZAS="$PIEZAS $q:og:3 $q:og:4"; done; COLS=2 ;;
  r2) PIEZAS=""; for q in $PROYECTOS; do for v in palabras hex material; do PIEZAS="$PIEZAS $q:r2-$v:3"; done; done; COLS=3 ;;
  r3) PIEZAS=""; F3=${R3_FLUX3:-portal}; for q in $PROYECTOS; do PIEZAS="$PIEZAS $q:estilo:3:640:320:4 $q:estilo:3:1280:640:8"
        [ "$q" = "$F3" ] && PIEZAS="$PIEZAS $q:estilo:3:640:320:8:flux3 $q:estilo:3:1280:640:16:flux3"; done; COLS=0 ;;
  *) echo "Uso: $0 r0|r1|r2|r3"; exit 2 ;;
esac
[ -x "$GEN" ] || { echo "No encuentro generar.sh de Tarkor en $GEN (TARKOR_GEN=<ruta>)"; exit 2; }
# Todos los prompts antes de la primera imagen, para no parar la ronda a medias.
for p in $PIEZAS; do IFS=: read -r proy prompt _ <<< "$p"; pf=$R/examples/$proy/prompts/$prompt.txt
  [ -s "$pf" ] || { echo "Falta el prompt $pf"; exit 2; }; done
OUT=$PILOTO/$RONDA; mkdir -p "$OUT"
for p in $PIEZAS; do
  IFS=: read -r proy prompt semilla W H PASOS MOD <<< "$p"
  if [ -n "$W" ]; then nombre=$prompt-${W}x$H-p$PASOS${MOD:+-$MOD}-s$semilla; else nombre=$prompt-s$semilla; W=1280; H=640; PASOS=6; fi
  pf=$R/examples/$proy/prompts/$prompt.txt
  # flux3 es el GGUF de FLUX.3 klein (~49 min por definitivo en la Deck): necesita más tope que los 900 s de generar.sh.
  ENTORNO=(); [ "$MOD" = flux3 ] && ENTORNO=(MODELO=flux3-image-klein-Q8_0.gguf TOPE=${R3_TOPE:-7200})
  [ -s "$OUT/$proy/intentos/$nombre.png" ] && { echo "ya está: $proy/$nombre"; continue; }
  echo "== $proy $nombre ($W×$H, $PASOS pasos${MOD:+, $MOD})"
  env "${ENTORNO[@]}" "$GEN" "$OUT/$proy" "$nombre" "$pf" $W $H "$semilla" $PASOS | sed -u "s|^|$proy |" | tee -a "$OUT/resumen.txt"
  rc=${PIPESTATUS[0]}
  [ "$rc" = 3 ] && { echo "Ronda parada: generar.sh abortó antes de arrancar (arriba, el motivo)"; exit 3; }
done
# Hoja de contacto: una fila por proyecto (orden alfabético), una columna por pieza del proyecto.
if [ "$COLS" -gt 1 ] && [ "$(ls "$OUT"/*/intentos/*.png 2>/dev/null | wc -l)" = $((N * COLS)) ]; then
  ffmpeg -loglevel error -y -pattern_type glob -i "$OUT/*/intentos/*.png" -vf "scale=640:-1,tile=${COLS}x$N" -frames:v 1 \
    "$OUT/hoja.png" && echo "Hoja: $OUT/hoja.png"
fi
echo "Resumen: $OUT/resumen.txt"
python3 "$R/examples/pilot/pagina.py" "$PILOTO"
