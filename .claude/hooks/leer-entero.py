#!/usr/bin/env python3
"""Gancho PreToolUse de Read: rechaza leer enteros los documentos grandes del proyecto y dice cómo leer solo lo que hace
falta. Con `offset` o `limit` deja pasar. Una lectura entera de `docs/plan.md` arrastró 348k tokens en F2.0
(`.claude/gw/opt-tokens.md`).

Lee el JSON del gancho en la entrada estándar; ante cualquier error deja pasar (un gancho no rompe la sesión).
"""
import json
import os
import sys

GRANDES = {
    'docs/plan.md': "grep -n '^| D22 \\|^| F2\\.4 ' docs/plan.md (las filas que cites) o Read con offset/limit",
}


def decision(datos, raiz):
    entrada = datos.get('tool_input') or {}
    ruta = entrada.get('file_path')
    if datos.get('tool_name') != 'Read' or not isinstance(ruta, str) or entrada.get('offset') or entrada.get('limit'):
        return None
    rel = os.path.relpath(os.path.realpath(ruta), os.path.realpath(raiz)).replace(os.sep, '/')
    if rel not in GRANDES:
        return None
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': f'{rel} es grande y leerlo entero se arrastra en cada llamada: usa {GRANDES[rel]}.',
    }}


def main():
    try:
        datos = json.loads(sys.stdin.read() or '{}')
        raiz = os.environ.get('CLAUDE_PROJECT_DIR') or datos.get('cwd') or os.getcwd()
        salida = decision(datos, raiz) if isinstance(datos, dict) else None
    except Exception:  # noqa: BLE001 — falla abierto
        return 0
    if salida:
        print(json.dumps(salida, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
