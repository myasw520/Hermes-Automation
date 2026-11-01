# -*- coding: utf-8 -*-
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Redirect stdout/stderr to log or devnull for pythonw.exe
if sys.stdout is None:
    sys.stdout = open(os.path.join(script_dir, 'server.log'), 'a', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.path.join(script_dir, 'server.log'), 'a', encoding='utf-8')

import http.server
import socketserver
import webbrowser
import urllib.request
import traceback

PORT = 8088

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        pass

def is_already_running(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=1) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass
    return False

def run():
    try:
        is_silent = ('--silent' in sys.argv or '--no-browser' in sys.argv)

        if is_already_running(PORT):
            if not is_silent:
                webbrowser.open(f"http://localhost:{PORT}")
            sys.exit(0)

        socketserver.TCPServer.allow_reuse_address = True

        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            sys.stdout.write(f"Server started on port {PORT}\n")
            sys.stdout.flush()
            if not is_silent:
                webbrowser.open(f"http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception:
        with open(os.path.join(script_dir, 'server_error.log'), 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)

if __name__ == '__main__':
    run()
