from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import shutil
import yt_dlp

def cari_audio(q):
    # =========================================================================
    # 1. COBA CARI DI YOUTUBE (MENGGUNAKAN PROTOKOL TV / MWEB)
    # =========================================================================
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
    
    # Periksa dan salin cookies ke folder /tmp jika tersedia
    src_cookie = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    if not os.path.exists(src_cookie):
        src_cookie = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')
    tmp_cookie = '/tmp/cookies.txt'
    if os.path.exists(src_cookie):
        try:
            shutil.copyfile(src_cookie, tmp_cookie)
            ydl_opts_yt['cookiefile'] = tmp_cookie
        except Exception:
            pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts_yt) as ydl:
            info = ydl.extract_info(f"ytsearch1:{q}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                formats = entry.get('formats', [])
                for f in reversed(formats):
                    u = f.get('url', '')
                    # Pastikan bukan .m3u8 agar ESP32 bisa memutar langsung
                    if '.m3u8' not in u and f.get('acodec') != 'none' and u:
                        return {
                            'title': entry.get('title'),
                            'url': u,
                            'source': 'YouTube'
                        }
    except Exception:
        pass # Jika YouTube membatasi, otomatis lanjut ke SoundCloud

    # =========================================================================
    # 2. OTOMATIS BERALIH KE SOUNDCLOUD (100% BEBAS DARI BLOKIR BOT)
    # =========================================================================
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
                formats = entry.get('formats', [])
                
                audio_url = None
                
                # Prioritas 1: Ambil format MP3 progressive langsung (bukan .m3u8)
                for f in formats:
                    u = f.get('url', '')
                    if '.m3u8' not in u and (f.get('ext') == 'mp3' or 'http_mp3' in f.get('format_id', '')):
                        audio_url = u
                        break

                # Prioritas 2: Ambil format audio murni apa pun yang bukan .m3u8
                if not audio_url:
                    for f in formats:
                        u = f.get('url', '')
                        if '.m3u8' not in u and u:
                            audio_url = u
                            break

                # Fallback terakhir jika hanya ada link utama
                if not audio_url:
                    audio_url = entry.get('url')

                if audio_url:
                    return {
                        'title': entry.get('title'),
                        'url': audio_url,
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
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(hasil).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Lagu tidak ditemukan'}).encode())
