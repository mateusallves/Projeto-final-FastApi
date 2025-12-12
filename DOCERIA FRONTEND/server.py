#!/usr/bin/env python3
"""
Servidor HTTP simples para servir o frontend
Execute: python server.py
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 5500
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Adiciona headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"\n{'='*60}")
        print(f"🚀 Servidor Frontend iniciado!")
        print(f"{'='*60}")
        print(f"📡 URL: {url}")
        print(f"🌐 Porta: {PORT}")
        print(f"📁 Diretório: {DIRECTORY}")
        print(f"{'='*60}\n")
        print("Pressione Ctrl+C para parar o servidor\n")
        
        # Abre o navegador automaticamente
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServidor encerrado.")

if __name__ == "__main__":
    main()

