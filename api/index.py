from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote_plus
import urllib.request
import json

# Daftar server proxy Invidious publik yang bebas blokir bot
INSTANCES = [
    "https://inv.nadeko.net",
    "https://invidious.nerdvpn.de",
    "https://invidious.tiekoetter.com"
]

def cari_audio_youtube(query):
    for base_url in INSTANCES:
        try:
            # Cari video lewat API Invidious
            search_url = f"{base_url}/api/v1/search?q={quote_plus(query)}"
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=6) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    for item in data:
                        if item.get('type') == 'video':
                            video_id = item.get('videoId')
                            title = item.get('title')
                            
                            # itag 140 adalah format audio murni M4A/AAC 128kbps
                            audio_url = f"{base_url}/latest_version?id={video_id}&itag=140&local=true"
                            return {
                                'title': title,
                                'url': audio_url
                            }
        except Exception:
            continue # Jika server 1 sibuk, otomatis coba server ke-2
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
                'status': 'Server YouTube Resolver Invidious Aktif',
                'contoh': '/api?q=denny+caknan'
            }).encode())
            return

        hasil = cari_audio_youtube(q)

        if hasil:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(hasil).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Lagu tidak ditemukan atau server sibuk'}).encode())
