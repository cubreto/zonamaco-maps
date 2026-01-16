"""
ZonaMaco 2026 VIP Maps - Flask Application
Serves interactive maps for ZonaMaco art week events
"""

import os
from flask import Flask, send_from_directory, redirect, url_for

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """Serve the main index page."""
    return send_from_directory('static/maps', 'index.html')

@app.route('/maps/<path:filename>')
def serve_map(filename):
    """Serve individual map files."""
    return send_from_directory('static/maps', filename)

@app.route('/<path:filename>')
def serve_root_file(filename):
    """Serve files from root (for compatibility)."""
    if os.path.exists(os.path.join('static/maps', filename)):
        return send_from_directory('static/maps', filename)
    return redirect(url_for('index'))

# Health check for deployment platforms
@app.route('/health')
def health():
    return {'status': 'healthy', 'app': 'zonamaco-maps'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
