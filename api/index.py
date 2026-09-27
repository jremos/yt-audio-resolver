from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import yt_dlp

def cari_audio(q):
    # Gunakan pencarian SoundCloud langsung (Terbukti 100% cepat dan tidak memblokir Vercel)
    ydl_opts = {
        'default_search': 'scsearch1',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        'nocheckcertificate': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch1:{q}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                url = entry.get('url')
                
                # Cari link stream yang langsung bisa diakses
                if not url and 'formats' in entry:
                    for f in entry['formats']:
                        if f.get('url'):
                            url = f.get('url')
                            break
                            
                if url:
                    return {
                        'title': entry.get('title', q),
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
            self.wfile.write(json.dumps({'status': 'Server Audio Aktif'}).encode())
            return

        hasil = cari_audio(q)

        if hasil and 'url' in hasil:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(hasil).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Lagu tidak ditemukan'}).encode())
