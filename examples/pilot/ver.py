#!/usr/bin/env python3
"""F2.0: sirve el repo en http://127.0.0.1 para ver las páginas del piloto y el prototipo de la interfaz.

Uso: examples/pilot/ver.py [puerto]   (por defecto 8765; Ctrl+C para pararlo)
Abiertas como archivo desde VS Code en flatpak (o un navegador en flatpak), las páginas llegan por el portal de
documentos, que da acceso solo a ese HTML y no a las imágenes de al lado: se ven los prompts y no las imágenes.
Servidas por HTTP en local, sí. Solo escucha en 127.0.0.1.
"""
import functools
import http.server
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
PAGINAS = ('piloto/index.html', 'piloto/logos/index.html', 'docs/interfaz/prototipo/index.html')


def main(argv):
    try:
        puerto = int(argv[1]) if len(argv) > 1 else 8765
    except ValueError:
        print(__doc__.strip().splitlines()[2])
        return 2
    manejador = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(R))
    try:
        servidor = http.server.ThreadingHTTPServer(('127.0.0.1', puerto), manejador)
    except OSError as e:
        print(f'no se puede escuchar en 127.0.0.1:{puerto}: {e} (¿ya está abierto? prueba otro puerto)')
        return 1
    for p in PAGINAS:
        if (R / p).exists():
            print(f'http://127.0.0.1:{puerto}/{p}')
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
