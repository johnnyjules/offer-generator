#!/usr/bin/env python3
"""
Discogs CORS Proxy Server
Vermittelt zwischen dem Offer Generator Tool und der Discogs API
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class ProxyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Parse the request path
        if self.path.startswith('/proxy?url='):
            # Extract the target URL
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            if 'url' not in params:
                self.send_error(400, "Missing 'url' parameter")
                return
            
            target_url = params['url'][0]
            
            try:
                # Forward request to Discogs API
                req = urllib.request.Request(
                    target_url,
                    headers={'User-Agent': 'OliverDiscogsTool/1.0 +https://oliver.example.com'}
                )
                
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    
                    # Send response with CORS headers
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    self.wfile.write(data)
                    
            except urllib.error.HTTPError as e:
                self.send_error(e.code, f"Discogs API Error: {e.reason}")
            except Exception as e:
                self.send_error(500, f"Proxy Error: {str(e)}")
        else:
            self.send_error(404, "Use /proxy?url=<discogs-api-url>")
    
    def do_OPTIONS(self):
        # Handle preflight CORS requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[PROXY] {self.address_string()} - {format % args}")

def run_proxy(port=None):
    if port is None:
        port = int(os.environ.get('PORT', 8001))
    
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    print(f"╔═══════════════════════════════════════════════════════╗")
    print(f"║   DISCOGS CORS PROXY SERVER LÄUFT                     ║")
    print(f"║   Port: {port}                                           ║")
    print(f"║   Bereit für Offer Generator Requests                ║")
    print(f"╚═══════════════════════════════════════════════════════╝")
    print(f"\nZum Beenden: CTRL+C drücken\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nProxy Server gestoppt.")
        server.shutdown()

if __name__ == '__main__':
    run_proxy()
