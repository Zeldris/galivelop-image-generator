#!/usr/bin/env python3
"""Gancho PreToolUse de Read: rechaza leer enteros los documentos grandes del proyecto y dice cómo leer solo lo que hace
falta. Deja pasar una lectura con `limit` de hasta `MAX_LINEAS` líneas. Una lectura entera de `docs/plan.md` arrastró
348k tokens en F2.0 (`.claude/gw/opt-tokens.md`).

Lee el JSON del gancho en la entrada estándar; ante cualquier error deja pasar (un gancho no rompe la sesión).
"""
import json
import os
import sys

GRANDES = {
    'docs/plan.md': "grep -nE '^\\| (D22|F2\\.4) ' docs/plan.md (las filas que cites) o Read con offset y limit",
}
MAX_LINEAS = 300


def grande(ruta, raiz):
    """La clave de GRANDES de `ruta`, dentro de la raíz o de un worktree suyo (una carpeta con `.claude/gw.json`)."""
    real = os.path.realpath(ruta).replace(os.sep, '/')
    rel = os.path.relpath(real, os.path.realpath(raiz)).replace(os.sep, '/')
    if rel in GRANDES:
        return rel
    for clave in GRANDES:
        if real.endswith('/' + clave) and os.path.isfile(os.path.join(real[:-len(clave)], '.claude', 'gw.json')):
            return clave
    return None


def decision(datos, raiz):
    entrada = datos.get('tool_input') or {}
    ruta, limite = entrada.get('file_path'), entrada.get('limit')
    if datos.get('tool_name') != 'Read' or not isinstance(ruta, str):
        return None
    if isinstance(limite, int) and not isinstance(limite, bool) and 0 < limite <= MAX_LINEAS:
        return None
    rel = grande(ruta, raiz)
    if rel is None:
        return None
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': f'{rel} es grande y leerlo entero se arrastra en cada llamada: usa {GRANDES[rel]} '
                                    f'(limit de hasta {MAX_LINEAS}).',
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
