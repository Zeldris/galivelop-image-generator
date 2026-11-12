#!/usr/bin/env bash
# Uso: reemplaza.sh <nueva.png> <destino.png>
# Si el destino existe, lo mueve a <carpeta>/descartes/<nombre>-anterior.png (con sufijo numérico si ya hay uno),
# copia la nueva al destino y anota la sustitución en el LEEME.md de la carpeta (lo crea si falta).
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "uso: $0 <nueva.png> <destino.png>" >&2
  exit 2
fi
nueva=$1
destino=$2
[ -f "$nueva" ] || { echo "no existe la nueva: $nueva" >&2; exit 1; }

carpeta=$(dirname -- "$destino")
nombre=$(basename -- "$destino")
base=${nombre%.*}
case $nombre in *.*) suf=".${nombre##*.}" ;; *) suf="" ;; esac
mkdir -p -- "$carpeta"
leeme="$carpeta/LEEME.md"
fecha=$(date +%F)
nota=""

if [ -e "$destino" ] && [ "$nueva" -ef "$destino" ]; then
  echo "la nueva y el destino son el mismo archivo: $destino" >&2
  exit 1
fi
if [ -f "$destino" ]; then
  mkdir -p -- "$carpeta/descartes"
  descarte="$carpeta/descartes/$base-anterior$suf"
  n=2
  while [ -e "$descarte" ]; do
    descarte="$carpeta/descartes/$base-anterior-$n$suf"
    n=$((n + 1))
  done
  mv -- "$destino" "$descarte"
  nota="sustituye al anterior, movido a descartes/$(basename -- "$descarte")"
fi

cp -- "$nueva" "$destino"

if [ ! -f "$leeme" ]; then
  printf '# %s\n\n## Descartes\n\n' "$(basename -- "$carpeta")" > "$leeme"
fi
printf -- '- %s: %s (%s)%s\n' "$nombre" "$([ -n "$nota" ] && echo "$nota" || echo "nuevo")" "$fecha" "" >> "$leeme"
