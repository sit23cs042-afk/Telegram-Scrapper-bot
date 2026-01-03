"""
Simple HTTP health check server for Render
Runs alongside the Telegram listener
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = b'''
            <!DOCTYPE html>
            <html>
            <head><title>Telegram Discount Bot</title></head>
            <body>
                <h1>🤖 Telegram Discount Bot is Running!</h1>
                <p>✅ Status: Active</p>
                <p>📊 Monitoring 37 Telegram channels for deals</p>
                <p>🔗 <a href="/health">Health Check</a></p>
            </body>
            </html>
            '''
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass

def start_health_server(port=10000):
    """Start health check server in background thread"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"✅ Health check server running on port {port}")
    return server
