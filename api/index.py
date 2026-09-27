from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import yt_dlp

def cari_audio(q):
    # 1. COBA CARI DI YOUTUBE DENGAN PROTOKOL TV / MWEB
    ydl_opts_yt = {
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'mweb']
            }
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts_yt) as ydl:
            info = ydl.extract_info(f"ytsearch1:{q}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                formats = entry.get('formats', [])
                for f in reversed(formats):
                    if f.get('acodec') != 'none' and f.get('url'):
                        return {
                            'title': entry.get('title'),
                            'url': f.get('url'),
                            'source': 'YouTube'
                        }
    except Exception:
        pass # Jika YouTube membatasi, langsung lanjut ke SoundCloud

    # 2. OTOMATIS BERALIH KE SOUNDCLOUD (100% BEBAS DARI BLOKIR BOT)
    ydl_opts_sc = {
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        'nocheckcertificate': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts_sc) as ydl:
            info = ydl.extract_info(f"scsearch1:{q}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                url = entry.get('url')
                if not url and 'formats' in entry:
                    for f in reversed(entry['formats']):
                        if f.get('url'):
                            url = f.get('url')
                            break
                if url:
                    return {
                        'title': entry.get('title'),
                        'url': url,
                        'source': 'SoundCloud'
                    }
    except Exception as e:
        return {'error': str(e)}

    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_params = parse_qs(urlparse(self.path).query)
        q = query_params.get('q', [''])[0]

        if not q:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'Server Audio Streaming Aktif',
                'contoh': '/api?q=denny+caknan'
            }).encode())
            return

        hasil = cari_audio(q)

        if hasil and 'url' in hasil:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(hasil).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Lagu tidak ditemukan'}).encode())
