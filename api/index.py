from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote_plus
import json
import urllib.request
import yt_dlp

def cari_audio_ogg(query):
    # 1. Cari Link Video di YouTube/SoundCloud
    ydl_opts = {
        'default_search': 'ytsearch1',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': True # Cukup ambil ID/link-nya saja secara cepat
    }
    
    webpage_url = None
    title = query
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                webpage_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                title = entry.get('title', query)
    except Exception:
        # Fallback jika YouTube diblokir, cari di SoundCloud
        try:
            with yt_dlp.YoutubeDL({'default_search': 'scsearch1', 'quiet': True}) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    webpage_url = entry.get('url')
                    title = entry.get('title', query)
        except Exception:
            pass

    if not webpage_url:
        return None

    # 2. Tembak Cobalt API untuk Mengubah Audio Menjadi OGG OPUS Murni
    # Server Cobalt resmi mengonversi audio ke OGG tanpa membebani Vercel
    cobalt_instances = [
        "https://api.cobalt.tools",
        "https://cobalt-api.kwiatekmiki.com",
        "https://co.wuk.sh"
    ]
    
    for instance in cobalt_instances:
        try:
            req_data = json.dumps({
                "url": webpage_url,
                "downloadMode": "audio",
                "audioFormat": "opus" # Minta format OPUS / OGG untuk Xiaozhi
            }).encode('utf-8')

            req = urllib.request.Request(
                instance,
                data=req_data,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
            )

            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    stream_url = res_json.get('url')
                    if stream_url:
                        return {
                            'title': title,
                            'url': stream_url,
                            'format': 'ogg_opus'
                        }
        except Exception:
            continue

    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_params = parse_qs(urlparse(self.path).query)
        q = query_params.get('q', [''])[0]

        if not q:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'Server OGG Resolver Aktif'}).encode())
            return

        hasil = cari_audio_ogg(q)

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
            self.wfile.write(json.dumps({'error': 'Gagal mengambil audio OGG'}).encode())
