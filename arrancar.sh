#!/usr/bin/env bash
# arrancar.sh: abre la interfaz de gimg en el navegador (arranca el servicio si no está en marcha).
# Uso: ./arrancar.sh  (o doble clic en el gestor de archivos, «Ejecutar en terminal»)
# Opens the gimg UI in the browser, starting the local service if needed.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

# Desde el sandbox de VS Code (flatpak) XDG apunta dentro del sandbox: se fijan las carpetas de siempre.
export GIMG_CONFIG_HOME="${GIMG_CONFIG_HOME:-$HOME/.config/gimg}"
export GIMG_DATA_HOME="${GIMG_DATA_HOME:-$HOME/.local/share/gimg}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "arrancar.sh: hace falta python3 (3.10 o más nuevo)" >&2
  exit 1
fi
exec python3 -m gimg ui "$@"
