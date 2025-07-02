from datetime import datetime
from flask import Flask, jsonify

from .db import last_seen

app = Flask(__name__)

@app.route('/where/<item>')
def where(item):
    zone, ts = last_seen(item)
    if ts is None:
        return jsonify({'item': item, 'zone': None, 'last_seen': None})
    delta = datetime.utcnow() - ts
    minutes = int(delta.total_seconds() // 60)
    return jsonify({'item': item, 'zone': zone, 'minutes_ago': minutes})

def run_server(host='0.0.0.0', port=8000):
    app.run(host=host, port=port)
