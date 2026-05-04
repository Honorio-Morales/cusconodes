from flask import Flask, send_from_directory, jsonify
import os
import glob
import json
from datetime import datetime

app = Flask(__name__, static_folder='web', static_url_path='')


def find_latest_processed():
    folder = os.path.join(os.getcwd(), 'data', 'processed')
    pattern = os.path.join(folder, 'alertas_clasificadas_*.json')
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return latest


@app.route('/')
def index():
    return send_from_directory('web', 'index.html')


@app.route('/api/alerts/latest')
def api_latest_alerts():
    latest = find_latest_processed()
    if latest and os.path.exists(latest):
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # ensure list
            if isinstance(data, dict) and 'alerts' in data:
                arr = data['alerts']
            elif isinstance(data, list):
                arr = data
            else:
                arr = []
            # sort by fecha_scrape if present
            try:
                arr.sort(key=lambda x: x.get('fecha_scrape',''), reverse=True)
            except Exception:
                pass
            return jsonify(arr)
        except Exception as e:
            return jsonify([]), 500

    # fallback: try web/ultimas_noticias.json
    fallback = os.path.join('web', 'ultimas_noticias.json')
    if os.path.exists(fallback):
        try:
            with open(fallback, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception:
            return jsonify([])

    return jsonify([])


if __name__ == '__main__':
    # Run on 0.0.0.0:8000 for local demos
    app.run(host='0.0.0.0', port=8000, debug=True)
