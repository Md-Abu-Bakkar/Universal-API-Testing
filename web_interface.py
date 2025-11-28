#!/usr/bin/env python3
"""
Web-based interface for Termux (X11 ছাড়া)
"""

from flask import Flask, render_template, request, jsonify
import threading
from core.api_scanner import APIScanner

app = Flask(__name__)
api_scanner = APIScanner()

@app.route('/')
def index():
    return """
    <html>
    <head><title>Universal API Tester</title></head>
    <body>
        <h1>Universal API Tester - Web Interface</h1>
        <textarea id="devtoolsData" rows="10" cols="80" placeholder="Paste DevTools data here..."></textarea>
        <br>
        <button onclick="scanAPIs()">Scan APIs</button>
        <div id="results"></div>
        
        <script>
        function scanAPIs() {
            const data = document.getElementById('devtoolsData').value;
            fetch('/scan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({data: data})
            })
            .then(r => r.json())
            .then(results => {
                document.getElementById('results').innerHTML = JSON.stringify(results, null, 2);
            });
        }
        </script>
    </body>
    </html>
    """

@app.route('/scan', methods=['POST'])
def scan_apis():
    data = request.json['data']
    apis = api_scanner.extract_apis(data)
    results = api_scanner.test_sequential(apis)
    return jsonify(results)

def start_web_interface():
    print("🌐 Web interface starting at http://localhost:5000")
    print("📱 Open this URL in your mobile browser")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_web_interface()
