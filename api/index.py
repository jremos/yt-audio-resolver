from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import yt_dlp

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_params = parse_qs(urlparse(self.path).query)
        q = query_params.get('q', [''])[0]

        if not q:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'Server YouTube Resolver Aktif', 'contoh': '/api?q=denny+caknan'}).encode())
            return

        # Cari lokasi file cookies.txt
        cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        if not os.path.exists(cookie_path):
            cookie_path = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'default_search': 'ytsearch1',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False
        }

        # Pasang cookies jika file ditemukan
        if os.path.exists(cookie_path):
            ydl_opts['cookiefile'] = cookie_path

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(q, download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    res = {
                        'title': entry.get('title'),
                        'url': entry.get('url')
                    }
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(res).encode())
                    return
            
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Lagu tidak ditemukan'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
