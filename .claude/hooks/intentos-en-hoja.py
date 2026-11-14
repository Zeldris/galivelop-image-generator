#!/usr/bin/env python3
"""Gancho PreToolUse de Read: al leer suelto un `.png` de intentos (`.../attempts/q...`) no bloquea, avisa de que
conviene revisarlos en una hoja de contactos (`gimg sheet`). 44 imágenes sueltas arrastraron 4-5 M de tokens
(`.claude/gw/gw-opt-tokens.md`, sesión c7c2a076). Avisa igual con las capturas del scratchpad (28 sueltas, ~2,2 M en
la revisión de la interfaz de `ccr-85e9d14e-zt7p8b`), salvo que el nombre diga que ya es una hoja; la primera
captura suelta de cada sesión pasa sin aviso (mirar una sola es legítimo) y avisa desde la segunda (con o sin `session_id`); las marcas de más de un día se limpian. Vale para
`.png`, `.jpg`, `.jpeg` y `.webp`.

Lee el JSON del gancho en la entrada estándar; ante cualquier error deja pasar.
"""
import hashlib
import json
import os
import sys
import tempfile
import time

AVISO = ('Cada imagen suelta (intento o captura) se arrastra en cada llamada: para revisarlas, una hoja: '
         '`gimg sheet IMAGEN... --out hoja.png` (una hoja de 6 cuesta como una imagen).')


PREFIJO = 'gimg-captura-'
IMAGENES = ('.png', '.jpg', '.jpeg', '.webp')


VIDA_MARCA = 24 * 3600  # las marcas de sesión más viejas se borran


def _limpiar(carpeta):
    """Borra las marcas `gimg-captura-*` de más de un día (las de sesiones ya acabadas)."""
    limite = time.time() - VIDA_MARCA
    try:
        nombres = os.listdir(carpeta)
    except OSError:
        return
    for nombre in nombres:
        if not nombre.startswith(PREFIJO):
            continue
        ruta = os.path.join(carpeta, nombre)
        try:
            if os.path.getmtime(ruta) < limite:
                os.remove(ruta)
        except OSError:
            pass


def _primera_captura(datos, carpeta):
    """True la primera vez que se ve una captura suelta en la sesión (lo apunta en `carpeta`).

    Sin `session_id` la clave de reserva es el proceso padre (el Claude Code que lanza el gancho: el mismo en toda la
    sesión), así que se comporta igual que con uno."""
    sesion = str(datos.get('session_id') or '') or 'ppid-%d' % os.getppid()
    carpeta = carpeta or tempfile.gettempdir()
    _limpiar(carpeta)
    marca = os.path.join(carpeta, PREFIJO + hashlib.sha256(sesion.encode()).hexdigest()[:16])
    try:
        os.close(os.open(marca, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    except OSError:
        return False
    return True


def decision(datos, carpeta=None):
    ruta = (datos.get('tool_input') or {}).get('file_path')
    if datos.get('tool_name') != 'Read' or not isinstance(ruta, str):
        return None
    ruta = ruta.replace('\\', '/')
    nombre = ruta.rsplit('/', 1)[-1].lower()
    if not nombre.endswith(IMAGENES):
        return None
    captura = '/scratchpad/' in ruta and 'hoja' not in nombre and 'sheet' not in nombre
    if '/attempts/q' in ruta or (captura and not _primera_captura(datos, carpeta)):
        return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': AVISO}}
    return None


def main():
    try:
        datos = json.loads(sys.stdin.read() or '{}')
        salida = decision(datos) if isinstance(datos, dict) else None
    except Exception:  # noqa: BLE001 — falla abierto
        return 0
    if salida:
        print(json.dumps(salida, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
