#!/bin/bash
# F2.0: lanza una ronda del piloto de contenido con el generar.sh de Tarkor, que solo se ejecuta (su repo no se toca):
# la salida va a <datos>/pilot/<ronda>/<proyecto>/{intentos,logs,prompts}/ y el resumen a <datos>/pilot/<ronda>/resumen.txt.
# Uso: examples/pilot/ronda.sh r0|r1   (con el juego, el navegador y Ollama cerrados)
# r0: humo, el og del Portal con semilla 3. r1: el og de los cuatro proyectos con semillas 3 y 4, y una hoja de contacto.
# TARKOR_GEN=<ruta de generar.sh> para otra copia; salta lo que ya existe, así que una ronda cortada se relanza igual.
# sin pipefail: generar.sh devuelve 3 si aborta antes de arrancar (memoria, Ollama) y entonces se para la ronda entera
set -u
R=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
GEN=${TARKOR_GEN:-$R/../WMF-imagenes/image-generator/scripts/generar.sh}
DATOS=${GIMG_DATA_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/gimg}
RONDA=${1:-}; W=1280; H=640; PASOS=6
case $RONDA in
  r0) PIEZAS="portal:3" ;;
  r1) PIEZAS="portal:3 portal:4 toveriai:3 toveriai:4 galivelop-workflow:3 galivelop-workflow:4 tarkor:3 tarkor:4" ;;
  *) echo "Uso: $0 r0|r1"; exit 2 ;;
esac
[ -x "$GEN" ] || { echo "No encuentro generar.sh de Tarkor en $GEN (TARKOR_GEN=<ruta>)"; exit 2; }
OUT=$DATOS/pilot/$RONDA; mkdir -p "$OUT"
for p in $PIEZAS; do
  proy=${p%%:*}; semilla=${p##*:}; nombre=og-s$semilla
  [ -s "$OUT/$proy/intentos/$nombre.png" ] && { echo "ya está: $proy/$nombre"; continue; }
  echo "== $proy $nombre ($W×$H, $PASOS pasos)"
  "$GEN" "$OUT/$proy" "$nombre" "$R/examples/$proy/prompts/og.txt" $W $H "$semilla" $PASOS | tee -a "$OUT/resumen.txt"
  rc=${PIPESTATUS[0]}
  [ "$rc" = 3 ] && { echo "Ronda parada: generar.sh abortó antes de arrancar (arriba, el motivo)"; exit 3; }
done
# Hoja de contacto: una fila por proyecto (orden alfabético), una columna por semilla.
if [ "$RONDA" = r1 ] && [ "$(ls "$OUT"/*/intentos/og-s*.png 2>/dev/null | wc -l)" = 8 ]; then
  ffmpeg -loglevel error -y -pattern_type glob -i "$OUT/*/intentos/og-s*.png" -vf "scale=640:-1,tile=2x4" -frames:v 1 \
    "$OUT/hoja.png" && echo "Hoja: $OUT/hoja.png"
fi
echo "Resumen: $OUT/resumen.txt"
