#!/usr/bin/env bash
# Descarga a piloto/fuentes/ las fuentes OFL de las marcas (repo google/fonts). No instala nada en el sistema.
# Uso: bash examples/pilot/fuentes.sh
set -euo pipefail
raiz="$(cd "$(dirname "$0")/../.." && pwd)"
dest="$raiz/piloto/fuentes"
mkdir -p "$dest"
base="https://raw.githubusercontent.com/google/fonts/main/ofl"
# carpeta|archivo (las variables llevan corchetes y coma: se codifican en la URL)
lista=(
  "sora|Sora[wght].ttf"
  "inter|Inter[opsz,wght].ttf"
  "cormorantgaramond|CormorantGaramond[wght].ttf"
  "dmsans|DMSans[opsz,wght].ttf"
  "cinzel|Cinzel[wght].ttf"
)
for par in "${lista[@]}"; do
  carpeta="${par%%|*}"; archivo="${par#*|}"
  salida="$dest/$archivo"
  if [ -s "$salida" ]; then echo "ya está: $archivo"; continue; fi
  url="$base/$carpeta/$(printf '%s' "$archivo" | sed 's/\[/%5B/g; s/\]/%5D/g; s/,/%2C/g')"
  tmp="$(mktemp)"
  if ! curl -fsSL --retry 3 -o "$tmp" "$url"; then
    rm -f "$tmp"; echo "no existe o falla: $url" >&2; exit 1
  fi
  mv "$tmp" "$salida"; echo "descargada: $archivo"
done
echo "Fuentes en $dest"
