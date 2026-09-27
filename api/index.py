from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import shutil
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

        # Salin cookies ke folder /tmp
        src_cookie = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        if not os.path.exists(src_cookie):
            src_cookie = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')

        tmp_cookie = '/tmp/cookies.txt'
        has_cookie = False
        if os.path.exists(src_cookie):
            try:
                shutil.copyfile(src_cookie, tmp_cookie)
                has_cookie = True
            except Exception:
                pass

        # PENTING: Tanpa filter format kaku agar tidak muncul error "Requested format not available"
        ydl_opts = {
            'default_search': 'ytsearch1',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            }
        }

        if has_cookie:
            ydl_opts['cookiefile'] = tmp_cookie

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(q, download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    
                    # Script Python memilih link audio terbaik secara cerdas
                    audio_url = None
                    formats = entry.get('formats', [])
                    
                    # Prioritas 1: Format Audio murni (tanpa video)
                    for f in reversed(formats):
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url'):
                            audio_url = f.get('url')
                            break
                    
                    # Prioritas 2: Format apa pun yang memiliki audio
                    if not audio_url:
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
