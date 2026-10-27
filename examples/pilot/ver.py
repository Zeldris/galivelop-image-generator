#!/usr/bin/env python3
"""F2.0: sirve el repo en http://127.0.0.1 para ver las páginas del piloto y el prototipo de la interfaz.

Uso: examples/pilot/ver.py [puerto]   (por defecto 8765; Ctrl+C para pararlo)
Abiertas como archivo desde VS Code en flatpak (o un navegador en flatpak), las páginas llegan por el portal de
documentos, que da acceso solo a ese HTML y no a las imágenes de al lado: se ven los prompts y no las imágenes.
Servidas por HTTP en local, sí. Solo escucha en 127.0.0.1, solo sirve PREFIJOS, sin listados de carpeta, y rechaza
un Host que no sea 127.0.0.1 o localhost (DNS rebinding).
"""
import functools
import http.server
import posixpath
import sys
import urllib.parse
from pathlib import Path

R = Path(__file__).resolve().parents[2]
PAGINAS = ('piloto/index.html', 'piloto/logos/index.html', 'docs/interfaz/prototipo/index.html')
# Lo que cargan esas páginas: el piloto, el prototipo y los logos de las biblias (MAR en el prototipo). Nada más (.git/).
PREFIJOS = ('/piloto/', '/docs/interfaz/', '/docs/marcas/')


class Manejador(http.server.SimpleHTTPRequestHandler):
    def _permitido(self):
        puerto = self.server.server_address[1]
        if self.headers.get('Host') not in (f'127.0.0.1:{puerto}', f'localhost:{puerto}'):
            self.send_error(403, 'Host no permitido')
            return False
        ruta = urllib.parse.unquote(self.path.split('?', 1)[0].split('#', 1)[0])  # como lo decodifica translate_path
        ruta = posixpath.normpath(ruta.replace('\\', '/'))
        if '\x00' in ruta or not any((ruta + '/').startswith(p) for p in PREFIJOS):
            self.send_error(404, 'No se sirve')
            return False
        return True

    def list_directory(self, path):
        self.send_error(404, 'Sin listados de carpeta')

    def do_GET(self):
        if self._permitido():
            super().do_GET()

    def do_HEAD(self):
        if self._permitido():
            super().do_HEAD()


def main(argv):
    try:
        puerto = int(argv[1]) if len(argv) > 1 else 8765
    except ValueError:
        print(__doc__.strip().splitlines()[2])
        return 2
    manejador = functools.partial(Manejador, directory=str(R))
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
