from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
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

        # TRIK SAKTI: Menyamar sebagai Web Embed Google (Bebas Bot Check & Bebas Cookies)
        ydl_opts = {
            'default_search': 'ytsearch1',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'http_headers': {
                'Referer': 'https://www.google.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_embedded']
                }
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(q, download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    
                    audio_url = None
                    formats = entry.get('formats', [])
                    
                    # Cari format audio yang tersedia
                    for f in reversed(formats):
                        if f.get('acodec') != 'none' and f.get('url'):
                            audio_url = f.get('url')
                            break

                    if not audio_url:
                        audio_url = entry.get('url')

                    if audio_url:
                        res = {
                            'title': entry.get('title'),
                            'url': audio_url
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
