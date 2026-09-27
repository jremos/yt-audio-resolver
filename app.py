from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/yt')
def get_audio():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Parameter q kosong'}), 400

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'default_search': 'ytsearch1',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                return jsonify({
                    'title': entry.get('title'),
                    'url': entry.get('url')
                })
        return jsonify({'error': 'Lagu tidak ditemukan'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
