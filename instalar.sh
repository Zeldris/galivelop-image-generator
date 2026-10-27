#!/usr/bin/env bash
# instalar.sh: pone gimg en ~/.local/bin, descarga el motor (stable-diffusion.cpp, release fija) y los modelos del
# catálogo (gimg/models.json), y deja el motor real como el de por defecto (D5, D24, D36).
# Installs the gimg launcher, the pinned stable-diffusion.cpp release and the catalog models, and selects the real engine.
#
# Uso / Usage: ./instalar.sh [--with <id>]... [--only-cli] [--models-from <carpeta>] [--dry-run]
#   (sin argumentos)       motor + modelos por defecto del catálogo / engine + the catalog's default models
#   --with <id>            añade otro modelo del catálogo (repetible) / adds another catalog model (repeatable)
#   --only-cli             solo el lanzador `gimg` / only the `gimg` launcher
#   --models-from <dir>    enlaza los archivos ya presentes, tras comprobar su sha256 / links files already there
#   --dry-run              imprime lo que haría, sin descargar ni escribir nada / prints what it would do
#
# Solo herramientas comunes: curl, sha256sum (o shasum), unzip y python3 (3.10+). Las carpetas salen de `gimg.paths`
# (GIMG_DATA_HOME, GIMG_CONFIG_HOME, GIMG_MODELS_HOME, XDG_*): este script no las reimplementa.
set -euo pipefail

# Motor fijo: "<asset del zip> <sha256 del zip>" (release de Linux con Vulkan). La release es `RELEASE` de
# gimg/engine_sdcpp.py, que lee este script (un dato, un sitio); el asset lleva su hash corto
# y un test los casa. Fixed engine zip; the release itself is read from gimg/engine_sdcpp.py.
SD_ZIP="sd-master-95ff762-bin-Linux-Ubuntu-24.04-x86_64-vulkan.zip 5af606a86cff7981ab6d98f35b8ae0e3c305bed7a1e4c04b4b0c1101c0c0dad1"
SD_URL_BASE="https://github.com/leejet/stable-diffusion.cpp/releases/download"

REPO=$(cd "$(dirname "$0")" && pwd)

case "${GIMG_LANG:-${LC_ALL:-${LC_MESSAGES:-${LANG:-}}}}" in
  es*) LANG_UI=es ;;
  *) LANG_UI=en ;;
esac

# say "<texto es>" "<text en>"
say() {
  if [ "$LANG_UI" = es ]; then printf '%s\n' "$1"; else printf '%s\n' "$2"; fi
}

die() {
  if [ "$LANG_UI" = es ]; then printf 'instalar.sh: %s\n' "$1" >&2; else printf 'instalar.sh: %s\n' "$2" >&2; fi
  exit 1
}

py() {
  (cd "$REPO" && python3 "$@")
}

usage() {
  sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
}

DRY=0
ONLY_CLI=0
WITH=""
MODELS_FROM=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --only-cli) ONLY_CLI=1 ;;
    --with)
      [ $# -ge 2 ] || die "--with necesita un id de modelo" "--with needs a model id"
      WITH="$WITH $2"
      shift
      ;;
    --models-from)
      [ $# -ge 2 ] || die "--models-from necesita una carpeta" "--models-from needs a folder"
      MODELS_FROM="$2"
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *) die "opción desconocida: $1 (mira --help)" "unknown option: $1 (see --help)" ;;
  esac
  shift
done

if [ -n "$MODELS_FROM" ]; then
  [ -d "$MODELS_FROM" ] || die "no existe la carpeta de --models-from: $MODELS_FROM" "--models-from folder does not exist: $MODELS_FROM"
  MODELS_FROM=$(cd "$MODELS_FROM" && pwd)
fi

WORK=""
OLD_ENGINE=""
cleanup() {
  if [ -n "$WORK" ]; then rm -rf "$WORK"; fi
  # El motor viejo solo se borra si el nuevo está en su sitio: si no, es la única copia.
  if [ -n "$OLD_ENGINE" ] && [ -f "$ENGINE_DIR/sd-cli" ]; then rm -rf "$OLD_ENGINE"; fi
}
trap cleanup EXIT

SHA_TOOL=""
sha_ok() { # sha_ok <archivo> <sha256>
  if [ "$SHA_TOOL" = sha256sum ]; then
    printf '%s  %s\n' "$2" "$1" | sha256sum -c --status - 2>/dev/null
  else
    printf '%s  %s\n' "$2" "$1" | shasum -a 256 -c --status 2>/dev/null
  fi
}

# ---- 1. Python >= 3.10 -------------------------------------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  die "hace falta Python 3.10 o más (python3); instálalo con el gestor de tu sistema" \
    "Python 3.10 or newer (python3) is required; install it with your system package manager"
fi
say "[1/6] Python $(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])'): bien" \
  "[1/6] Python $(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])'): ok"

if command -v sha256sum >/dev/null 2>&1; then
  SHA_TOOL=sha256sum
elif command -v shasum >/dev/null 2>&1; then
  SHA_TOOL=shasum
else
  die "falta sha256sum (o shasum); instala coreutils (o perl) con el gestor de tu sistema" \
    "sha256sum (or shasum) is missing; install coreutils (or perl) with your system package manager"
fi

DATA=$(py -c 'from gimg import paths; print(paths.data_dir())')
CONFIG=$(py -c 'from gimg import paths; print(paths.config_dir())')
MODELS=$(py -c 'from gimg import paths; print(paths.models_dir())')
RELEASE=$(py -c 'from gimg import engine_sdcpp; print(engine_sdcpp.RELEASE)')
SD_ASSET=${SD_ZIP%% *}
SD_SHA=${SD_ZIP##* }

# ---- 2. Lanzador ---------------------------------------------------------------------------------------------
LAUNCHER_DIR="$HOME/.local/bin"
LAUNCHER="$LAUNCHER_DIR/gimg"
REPO_QUOTED=$(printf '%s' "$REPO" | sed "s/'/'\\\\''/g")
LAUNCHER_TEXT="#!/bin/sh
# Escrito por instalar.sh (gimg). Written by instalar.sh.
PYTHONPATH='$REPO_QUOTED'\"\${PYTHONPATH:+:\$PYTHONPATH}\" exec python3 -m gimg \"\$@\""
if [ -f "$LAUNCHER" ] && [ "$(cat "$LAUNCHER")" = "$LAUNCHER_TEXT" ]; then
  say "[2/6] Lanzador ya al día: $LAUNCHER" "[2/6] Launcher already up to date: $LAUNCHER"
elif [ "$DRY" = 1 ]; then
  say "[dry-run] [2/6] escribiría el lanzador $LAUNCHER (exec python3 -m gimg, desde $REPO)" \
    "[dry-run] [2/6] would write the launcher $LAUNCHER (exec python3 -m gimg, from $REPO)"
else
  mkdir -p "$LAUNCHER_DIR"
  printf '%s\n' "$LAUNCHER_TEXT" >"$LAUNCHER"
  chmod 755 "$LAUNCHER"
  say "[2/6] Lanzador escrito: $LAUNCHER" "[2/6] Launcher written: $LAUNCHER"
fi
case ":$PATH:" in
  *":$LAUNCHER_DIR:"*) ;;
  *) say "      Aviso: $LAUNCHER_DIR no está en PATH; añade a tu ~/.profile: export PATH=\"\$HOME/.local/bin:\$PATH\"" \
    "      Warning: $LAUNCHER_DIR is not in PATH; add to your ~/.profile: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

if [ "$ONLY_CLI" = 1 ]; then
  say "Solo el lanzador (--only-cli): sin motor, modelos ni configuración." \
    "Launcher only (--only-cli): no engine, models or configuration."
  exit 0
fi

# ---- 3. Motor --------------------------------------------------------------------------------------------------
ENGINE_DIR="$DATA/engine/$RELEASE"
MARK="$ENGINE_DIR/.zip-sha256"
if [ -x "$ENGINE_DIR/sd-cli" ] && [ "$(cat "$MARK" 2>/dev/null || true)" = "$SD_SHA" ]; then
  say "[3/6] Motor $RELEASE ya instalado en $ENGINE_DIR" "[3/6] Engine $RELEASE already installed in $ENGINE_DIR"
elif [ "$DRY" = 1 ]; then
  say "[dry-run] [3/6] descargaría $SD_URL_BASE/$RELEASE/$SD_ASSET, comprobaría su sha256 y lo extraería en $ENGINE_DIR" \
    "[dry-run] [3/6] would download $SD_URL_BASE/$RELEASE/$SD_ASSET, check its sha256 and extract it to $ENGINE_DIR"
else
  command -v curl >/dev/null 2>&1 || die "falta curl" "curl is missing"
  command -v unzip >/dev/null 2>&1 || die "falta unzip" "unzip is missing"
  mkdir -p "$DATA/engine"
  WORK=$(mktemp -d "$DATA/engine/.tmp.XXXXXX")
  say "[3/6] Descargando el motor $RELEASE..." "[3/6] Downloading the engine $RELEASE..."
  curl -fL --retry 3 -o "$WORK/$SD_ASSET" "$SD_URL_BASE/$RELEASE/$SD_ASSET"
  sha_ok "$WORK/$SD_ASSET" "$SD_SHA" || die "el sha256 del zip del motor no cuadra (esperado $SD_SHA)" \
    "the engine zip sha256 does not match (expected $SD_SHA)"
  mkdir "$WORK/x"
  unzip -q "$WORK/$SD_ASSET" -d "$WORK/x"
  [ -f "$WORK/x/sd-cli" ] || die "el zip del motor no trae sd-cli" "the engine zip has no sd-cli"
  chmod 755 "$WORK/x/sd-cli"
  if [ -f "$WORK/x/sd-server" ]; then chmod 755 "$WORK/x/sd-server"; fi
  printf '%s\n' "$SD_SHA" >"$WORK/x/.zip-sha256"
  if [ -e "$ENGINE_DIR" ] || [ -L "$ENGINE_DIR" ]; then
    OLD_ENGINE="$ENGINE_DIR.old.$$"
    mv "$ENGINE_DIR" "$OLD_ENGINE"
    if ! mv "$WORK/x" "$ENGINE_DIR"; then
      mv "$OLD_ENGINE" "$ENGINE_DIR" || true
      die "no se pudo mover el motor nuevo a $ENGINE_DIR; el anterior sigue ahí (o en $OLD_ENGINE)" \
        "could not move the new engine to $ENGINE_DIR; the previous one is still there (or at $OLD_ENGINE)"
    fi
    rm -rf "$OLD_ENGINE"
    OLD_ENGINE=""
  else
    mv "$WORK/x" "$ENGINE_DIR"
  fi
  say "      Motor instalado en $ENGINE_DIR" "      Engine installed in $ENGINE_DIR"
fi

# ---- 4. Modelos -----------------------------------------------------------------------------------------------
# Una línea por archivo: id<TAB>tipo<TAB>nombre<TAB>url<TAB>sha256<TAB>MB<TAB>por-defecto (0/1).
CATALOG_LINES=$(py -c '
import json
from gimg import models
for mid, m in sorted(models.load_catalog()["models"].items()):
    for kind in models.KINDS:
        f = m["files"][kind]
        print("\t".join([mid, kind, f["name"], f["url"], f["sha256"], str(f["sizeMb"]), "1" if m.get("installDefault") else "0"]))
')
KNOWN_IDS=$(printf '%s\n' "$CATALOG_LINES" | cut -f1 | sort -u)
for wanted in $WITH; do
  printf '%s\n' "$KNOWN_IDS" | grep -qx -- "$wanted" || die \
    "modelo desconocido en --with: $wanted (conocidos: $(printf '%s' "$KNOWN_IDS" | tr '\n' ' '))" \
    "unknown model in --with: $wanted (known: $(printf '%s' "$KNOWN_IDS" | tr '\n' ' '))"
done

wanted_model() { # wanted_model <id> <por-defecto>
  [ "$2" = 1 ] && return 0
  case " $WITH " in *" $1 "*) return 0 ;; esac
  return 1
}

install_file() { # install_file <id> <tipo> <nombre> <url> <sha256> <mb>
  local id=$1 kind=$2 name=$3 url=$4 sha=$5 mb=$6
  local dest="$MODELS/$kind/$name" src=""
  if [ "$DRY" = 1 ]; then
    if [ -e "$dest" ]; then
      say "[dry-run]      $id/$kind: $name ya está; se comprobaría su sha256 y no se tocaría si cuadra" \
        "[dry-run]      $id/$kind: $name is already there; its sha256 would be checked and kept if it matches"
    else
      if [ -n "$MODELS_FROM" ]; then
        if [ -f "$MODELS_FROM/$name" ]; then src="$MODELS_FROM/$name"; elif [ -f "$MODELS_FROM/$kind/$name" ]; then src="$MODELS_FROM/$kind/$name"; fi
      fi
      if [ -n "$src" ]; then
        say "[dry-run]      $id/$kind: enlazaría $src -> $dest tras comprobar su sha256" \
          "[dry-run]      $id/$kind: would link $src -> $dest after checking its sha256"
      else
        say "[dry-run]      $id/$kind: descargaría $url (${mb} MB) -> $dest" \
          "[dry-run]      $id/$kind: would download $url (${mb} MB) -> $dest"
      fi
    fi
    return 0
  fi
  if [ -e "$dest" ] && sha_ok "$dest" "$sha"; then
    say "      $id/$kind: $name ya cuadra; no se toca" "      $id/$kind: $name already matches; left alone"
    return 0
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    say "      $id/$kind: $name no cuadra con el catálogo; se sustituye" \
      "      $id/$kind: $name does not match the catalog; replacing it"
  fi
  mkdir -p "$MODELS/$kind"
  if [ -n "$MODELS_FROM" ]; then
    if [ -f "$MODELS_FROM/$name" ]; then src="$MODELS_FROM/$name"; elif [ -f "$MODELS_FROM/$kind/$name" ]; then src="$MODELS_FROM/$kind/$name"; fi
  fi
  if [ -n "$src" ]; then
    if sha_ok "$src" "$sha"; then
      ln -sf "$src" "$dest.part"
      mv -f "$dest.part" "$dest"
      say "      $id/$kind: enlazado $src" "      $id/$kind: linked $src"
      return 0
    fi
    say "      $id/$kind: $src no cuadra con el sha256 del catálogo; se descarga" \
      "      $id/$kind: $src does not match the catalog sha256; downloading"
  fi
  command -v curl >/dev/null 2>&1 || die "falta curl" "curl is missing"
  say "      $id/$kind: descargando $name (${mb} MB)..." "      $id/$kind: downloading $name (${mb} MB)..."
  curl -fL -C - --retry 3 -o "$dest.part" "$url" || die \
    "falló la descarga de $name; lo que había en $dest no se ha tocado, repite para reanudarla" \
    "the download of $name failed; whatever was at $dest is untouched, retry to resume it"
  if ! sha_ok "$dest.part" "$sha"; then
    rm -f "$dest.part"
    die "el sha256 de $name no cuadra; se ha borrado la descarga, repite (o revisa la URL del catálogo)" \
      "the sha256 of $name does not match; the download was deleted, retry (or check the catalog URL)"
  fi
  mv -f "$dest.part" "$dest"
}

say "[4/6] Modelos en $MODELS" "[4/6] Models in $MODELS"
CHOSEN=""
while IFS=$'\t' read -r id kind name url sha mb dflt; do
  [ -n "$id" ] || continue
  if wanted_model "$id" "$dflt"; then
    case " $CHOSEN " in *" $id "*) ;; *) CHOSEN="$CHOSEN $id" ;; esac
    install_file "$id" "$kind" "$name" "$url" "$sha" "$mb"
  fi
done <<EOF
$CATALOG_LINES
EOF
if [ -z "$CHOSEN" ]; then
  say "      (el catálogo no marca ningún modelo por defecto y no se pidió --with)" \
    "      (the catalog marks no default model and no --with was given)"
fi

# ---- 5. Configuración ------------------------------------------------------------------------------------------
if [ "$DRY" = 1 ]; then
  say "[dry-run] [5/6] escribiría \"engine\": \"sdcpp\" en $CONFIG/config.json sin pisar otras claves" \
    "[dry-run] [5/6] would set \"engine\": \"sdcpp\" in $CONFIG/config.json keeping other keys"
else
  py -c '
import sys
from gimg import fsutil, paths
path = paths.config_dir() / "config.json"
try:
    data = fsutil.read_json(path, {})
except (OSError, ValueError) as exc:
    sys.exit("%s: %s" % (path, exc))
if not isinstance(data, dict):
    sys.exit("%s: no es un objeto JSON / is not a JSON object" % path)
data["engine"] = "sdcpp"
fsutil.write_json(path, data)
' || die "no se pudo escribir $CONFIG/config.json (arréglalo a mano y repite)" \
    "could not write $CONFIG/config.json (fix it by hand and retry)"
  say "[5/6] Motor por defecto: sdcpp ($CONFIG/config.json)" "[5/6] Default engine: sdcpp ($CONFIG/config.json)"
fi

# ---- 6. Comprobación -------------------------------------------------------------------------------------------
if [ "$DRY" = 1 ]; then
  say "[dry-run] [6/6] correría: gimg doctor" "[dry-run] [6/6] would run: gimg doctor"
  exit 0
fi
say "[6/6] gimg doctor" "[6/6] gimg doctor"
py -m gimg doctor
