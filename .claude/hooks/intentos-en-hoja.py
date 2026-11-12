#!/usr/bin/env python3
"""Gancho PreToolUse de Read: al leer suelto un `.png` de intentos (`.../attempts/q...`) no bloquea, avisa de que
conviene revisarlos en una hoja de contactos (`gimg sheet`). 44 imágenes sueltas arrastraron 4-5 M de tokens
(`.claude/gw/gw-opt-tokens.md`, sesión c7c2a076).

Lee el JSON del gancho en la entrada estándar; ante cualquier error deja pasar.
"""
import json
import sys

AVISO = ('Leer intentos sueltos se arrastra en cada llamada: para revisarlos, una hoja: '
         '`gimg sheet IMAGEN... --out hoja.png` (una hoja de 6 cuesta como una imagen).')


def decision(datos):
    ruta = (datos.get('tool_input') or {}).get('file_path')
    if datos.get('tool_name') != 'Read' or not isinstance(ruta, str):
        return None
    ruta = ruta.replace('\\', '/')
    if ruta.lower().endswith('.png') and '/attempts/q' in ruta:
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
