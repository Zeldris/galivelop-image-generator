#!/usr/bin/env python3
"""Gancho PreToolUse de Read: al leer suelto un `.png` de intentos (`.../attempts/q...`) no bloquea, avisa de que
conviene revisarlos en una hoja de contactos (`gimg sheet`). 44 imágenes sueltas arrastraron 4-5 M de tokens
(`.claude/gw/gw-opt-tokens.md`, sesión c7c2a076). Avisa igual con las capturas del scratchpad (28 sueltas, ~2,2 M en
la revisión de la interfaz de `ccr-85e9d14e-zt7p8b`), salvo que el nombre diga que ya es una hoja.

Lee el JSON del gancho en la entrada estándar; ante cualquier error deja pasar.
"""
import json
import sys

AVISO = ('Cada imagen suelta (intento o captura) se arrastra en cada llamada: para revisarlas, una hoja: '
         '`gimg sheet IMAGEN... --out hoja.png` (una hoja de 6 cuesta como una imagen).')


def decision(datos):
    ruta = (datos.get('tool_input') or {}).get('file_path')
    if datos.get('tool_name') != 'Read' or not isinstance(ruta, str):
        return None
    ruta = ruta.replace('\\', '/')
    nombre = ruta.rsplit('/', 1)[-1].lower()
    captura = '/scratchpad/' in ruta and 'hoja' not in nombre and 'sheet' not in nombre
    if nombre.endswith('.png') and ('/attempts/q' in ruta or captura):
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
