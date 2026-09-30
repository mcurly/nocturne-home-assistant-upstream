"""Loopback-only synthetic preview. No HA access, files, keys or health data."""
import http.server
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shared/rootfs/opt/nocturne-ha'))
from help_ui import language, render


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path != '/':
            self.send_error(404)
            return
        state = {'demo': True, 'ready': False, 'channel': 'Stable', 'error': 'CERT_FILES'}
        body = render(state, language(urlsplit(self.path).query)).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
    print('Preview: http://127.0.0.1:8765/?lang=nl', flush=True)
    server.serve_forever()
