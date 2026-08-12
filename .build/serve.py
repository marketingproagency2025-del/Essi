#!/usr/bin/env python3
"""
serve.py - a local server that mimics how Cloudflare Workers Assets serves this repo.

The site has no build step and no Worker script. Clean URLs come from Cloudflare's
default html_handling ("auto-trailing-slash"), which maps /services to services.html
and /it/services to it/services.html. Nothing in the repo encodes that, so nothing in
the repo can be tested against it either - which is why this exists.

    python .build/serve.py [port]

Read-only. Serves the repo root, resolves extensionless paths the way the platform
does, and returns 404 otherwise so a missing page fails loudly instead of silently
falling back to index.html.
"""
import http.server
import os
import posixpath
import socketserver
import sys
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def translate_path(self, path):
        clean = unquote(urlparse(path).path)
        rel = posixpath.normpath(clean).lstrip('/')
        full = os.path.join(ROOT, rel.replace('/', os.sep))

        # An existing file is served as-is.
        if os.path.isfile(full):
            return full
        # A directory, or the site root, resolves to its index.html.
        if clean.endswith('/') or clean == '':
            idx = os.path.join(full, 'index.html')
            if os.path.isfile(idx):
                return idx
        # Extensionless path -> <path>.html. This is the clean-URL rule.
        if '.' not in posixpath.basename(clean):
            html = full + '.html'
            if os.path.isfile(html):
                return html
            idx = os.path.join(full, 'index.html')
            if os.path.isfile(idx):
                return idx
        return full

    def log_message(self, fmt, *args):
        pass  # quiet


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', port), Handler) as httpd:
        print(f'serving {ROOT} on http://127.0.0.1:{port}')
        httpd.serve_forever()
