#!/usr/bin/env python3
"""
Universal API Tester - Web GUI for Termux (No X11 Required)
"""

import http.server
import socketserver
import json
import threading
from urllib.parse import parse_qs, urlparse
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from core.api_scanner import APIScanner
from core.login_handler import LoginHandler
from core.code_generator import CodeGenerator

class APIRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api_scanner = APIScanner()
        self.code_generator = CodeGenerator()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_interface().encode())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(self.get_css().encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/scan':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)
            
            devtools_data = data.get('devtools_data', [''])[0]
            
            # Process the data
            apis = self.api_scanner.extract_apis(devtools_data)
            results = self.api_scanner.test_sequential(apis)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results, indent=2).encode())
        
        elif self.path == '/generate_code':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            results = data.get('results', [])
            template_type = data.get('template', 'requests')
            
            if template_type == 'requests':
                code = self.code_generator.generate_python_code(results, 'requests')
            elif template_type == 'aiohttp':
                code = self.code_generator.generate_python_code(results, 'aiohttp')
            else:
                code = self.code_generator.generate_curl_commands(results)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'code': code}).encode())
    
    def get_html_interface(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal API Tester - Web GUI</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Universal API Tester</h1>
            <p>Automated API Detection & Testing Tool</p>
        </header>

        <div class="main-content">
            <!-- Input Section -->
            <div class="section">
                <h2>📋 Paste DevTools Data</h2>
                <textarea id="devtoolsData" placeholder="Paste your browser DevTools network data here..."></textarea>
                <button onclick="scanAPIs()" class="btn btn-primary">🔍 Scan APIs</button>
            </div>

            <!-- Results Section -->
            <div class="section">
                <h2>📊 API Results</h2>
                <div id="results" class="results-container"></div>
            </div>

            <!-- Code Generation -->
            <div class="section">
                <h2>💻 Generate Code</h2>
                <div class="code-options">
                    <button onclick="generateCode('requests')" class="btn btn-secondary">Python Requests</button>
                    <button onclick="generateCode('aiohttp')" class="btn btn-secondary">Python aiohttp</button>
                    <button onclick="generateCode('curl')" class="btn btn-secondary">cURL Commands</button>
                </div>
                <pre id="generatedCode" class="code-block"></pre>
            </div>
        </div>

        <footer>
            <p>Made with ❤️ for Termux Users</p>
        </footer>
    </div>

    <script>
        function scanAPIs() {
            const data = document.getElementById('devtoolsData').value;
            if (!data.trim()) {
                alert('Please paste some DevTools data first!');
                return;
            }

            const formData = new FormData();
            formData.append('devtools_data', data);

            fetch('/scan', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(results => {
                displayResults(results);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error scanning APIs: ' + error);
            });
        }

        function displayResults(results) {
            const resultsDiv = document.getElementById('results');
            let html = '<div class="results-summary">';
            
            const successful = results.filter(r => r.success).length;
            const failed = results.length - successful;
            
            html += `<p>📈 Found ${results.length} APIs | ✅ ${successful} Successful | ❌ ${failed} Failed</p>`;
            html += '</div><div class="results-table">';
            
            results.forEach((result, index) => {
                const statusIcon = result.success ? '✅' : '❌';
                html += `
                    <div class="result-item ${result.success ? 'success' : 'failed'}">
                        <div class="result-header">
                            <span class="status">${statusIcon}</span>
                            <span class="method">${result.method || 'GET'}</span>
                            <span class="url">${result.api}</span>
                            <span class="type">${result.type}</span>
                        </div>
                        <div class="result-details">
                            <strong>Status:</strong> ${result.status_code} | 
                            <strong>Size:</strong> ${result.size || 'N/A'} bytes
                            ${result.error ? `<br><strong>Error:</strong> ${result.error}` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            resultsDiv.innerHTML = html;
            
            // Store results for code generation
            window.currentResults = results;
        }

        function generateCode(templateType) {
            if (!window.currentResults || window.currentResults.length === 0) {
                alert('Please scan APIs first!');
                return;
            }

            fetch('/generate_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    results: window.currentResults,
                    template: templateType
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('generatedCode').textContent = data.code;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error generating code: ' + error);
            });
        }

        // Sample data for testing
        function loadSampleData() {
            const sampleData = `GET https://api.example.com/v1/users
POST https://api.example.com/v1/login
{"username": "test", "password": "test"}
GET https://api.example.com/v1/data.json`;
            
            document.getElementById('devtoolsData').value = sampleData;
        }

        // Load sample data on page load
        window.onload = loadSampleData;
    </script>
</body>
</html>
"""
    
    def get_css(self):
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
    color: white;
    padding: 30px;
    text-align: center;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

header p {
    font-size: 1.2em;
    opacity: 0.9;
}

.main-content {
    padding: 30px;
}

.section {
    margin-bottom: 40px;
    padding: 25px;
    background: #f8f9fa;
    border-radius: 10px;
    border-left: 5px solid #3498db;
}

.section h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    font-size: 1.5em;
}

textarea {
    width: 100%;
    height: 200px;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    resize: vertical;
    margin-bottom: 15px;
}

textarea:focus {
    outline: none;
    border-color: #3498db;
}

.btn {
    padding: 12px 25px;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 5px;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-2px);
}

.btn-secondary {
    background: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background: #7f8c8d;
    transform: translateY(-2px);
}

.code-options {
    margin-bottom: 20px;
}

.results-container {
    max-height: 500px;
    overflow-y: auto;
}

.results-summary {
    background: #2ecc71;
    color: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    text-align: center;
    font-weight: bold;
}

.result-item {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    transition: all 0.3s ease;
}

.result-item:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.result-item.success {
    border-left: 5px solid #2ecc71;
}

.result-item.failed {
    border-left: 5px solid #e74c3c;
}

.result-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.status {
    font-size: 1.2em;
}

.method {
    background: #3498db;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.9em;
}

.url {
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    color: #2c3e50;
}

.type {
    background: #9b59b6;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8em;
}

.result-details {
    font-size: 0.9em;
    color: #7f8c8d;
}

.code-block {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.4;
    max-height: 400px;
    overflow-y: auto;
}

footer {
    background: #34495e;
    color: white;
    text-align: center;
    padding: 20px;
    margin-top: 30px;
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        margin: 10px;
        border-radius: 10px;
    }
    
    .main-content {
        padding: 15px;
    }
    
    .result-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    header h1 {
        font-size: 2em;
    }
}
"""

def start_web_gui(port=8000):
    """Start the web-based GUI server"""
    print("🚀 Starting Universal API Tester - Web GUI")
    print("=" * 50)
    print(f"🌐 Open your browser and visit: http://localhost:{port}")
    print("📱 On Termux, use termux-open-url to open in browser")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Try to open browser automatically in Termux
    try:
        os.system(f"termux-open-url http://localhost:{port}")
    except:
        pass
    
    with socketserver.TCPServer(("", port), APIRequestHandler) as httpd:
        print(f"✅ Server running on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_web_gui()
