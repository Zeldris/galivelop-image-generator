#!/bin/bash
# F2.0: lanza una ronda del piloto de contenido con el generar.sh de Tarkor, que solo se ejecuta (su repo no se toca):
# la salida va a piloto/<ronda>/<proyecto>/{intentos,logs,prompts}/ (en el repo, fuera de git; PILOTO=<carpeta> para otra),
# el resumen a piloto/<ronda>/resumen.txt y la página de revisión a piloto/index.html (examples/pilot/pagina.py).
# Uso: examples/pilot/ronda.sh r0|r1|r2   (con el juego, el navegador y Ollama cerrados)
# r0: humo, el og del Portal con semilla 3. r1: el og de cada proyecto con semillas 3 y 4, y una hoja de contacto.
# r2: las tres variantes de estilo de cada proyecto (prompts/r2-{palabras,hex,material}.txt) con semilla 3, y su hoja.
# TARKOR_GEN=<ruta de generar.sh> para otra copia; salta lo que ya existe, así que una ronda cortada se relanza igual.
# sin pipefail: generar.sh devuelve 3 si aborta antes de arrancar (memoria, Ollama) y entonces se para la ronda entera
set -u
R=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
GEN=${TARKOR_GEN:-$R/../WMF-imagenes/image-generator/scripts/generar.sh}
PILOTO=${PILOTO:-$R/piloto}
RONDA=${1:-}; W=1280; H=640; PASOS=6
PROYECTOS="portal toveriai galivelop-workflow tarkor galivelop-image-generator galivelop-voice-generator galivelop-developer"
N=$(echo $PROYECTOS | wc -w)
# Cada pieza es proyecto:prompt:semilla (examples/<proyecto>/prompts/<prompt>.txt); la imagen, <prompt>-s<semilla>.
case $RONDA in
  r0) PIEZAS="portal:og:3"; COLS=1 ;;
  r1) PIEZAS=""; for q in $PROYECTOS; do PIEZAS="$PIEZAS $q:og:3 $q:og:4"; done; COLS=2 ;;
  r2) PIEZAS=""; for q in $PROYECTOS; do for v in palabras hex material; do PIEZAS="$PIEZAS $q:r2-$v:3"; done; done; COLS=3 ;;
  *) echo "Uso: $0 r0|r1|r2"; exit 2 ;;
esac
[ -x "$GEN" ] || { echo "No encuentro generar.sh de Tarkor en $GEN (TARKOR_GEN=<ruta>)"; exit 2; }
# Todos los prompts antes de la primera imagen, para no parar la ronda a medias.
for p in $PIEZAS; do IFS=: read -r proy prompt _ <<< "$p"; pf=$R/examples/$proy/prompts/$prompt.txt
  [ -s "$pf" ] || { echo "Falta el prompt $pf"; exit 2; }; done
OUT=$PILOTO/$RONDA; mkdir -p "$OUT"
for p in $PIEZAS; do
  IFS=: read -r proy prompt semilla <<< "$p"
  nombre=$prompt-s$semilla; pf=$R/examples/$proy/prompts/$prompt.txt
  [ -s "$OUT/$proy/intentos/$nombre.png" ] && { echo "ya está: $proy/$nombre"; continue; }
  echo "== $proy $nombre ($W×$H, $PASOS pasos)"
  "$GEN" "$OUT/$proy" "$nombre" "$pf" $W $H "$semilla" $PASOS | sed -u "s|^|$proy |" | tee -a "$OUT/resumen.txt"
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
