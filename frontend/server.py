#!/usr/bin/env python3
"""
Simple HTTP server for Historical Facts Explorer Frontend
Serves static files with proper MIME types
"""

import http.server
import socketserver
import os
import mimetypes
import sys
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve static files with proper headers"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def guess_type(self, path):
        """Enhanced MIME type detection"""
        mimetype, encoding = mimetypes.guess_type(path)
        
        # Handle specific extensions
        if path.endswith('.html') or path.endswith('.htm'):
            mimetype = 'text/html'
        elif path.endswith('.css'):
            mimetype = 'text/css'
        elif path.endswith('.js'):
            mimetype = 'application/javascript'
        elif path.endswith('.json'):
            mimetype = 'application/json'
        elif path.endswith('.ico'):
            mimetype = 'image/x-icon'
        elif path.endswith('.svg'):
            mimetype = 'image/svg+xml'
        elif mimetype is None:
            mimetype = 'text/html' if path.endswith('.html') or path.endswith('.htm') or path == '/index.html' else 'application/octet-stream'
            
        return mimetype, encoding
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Serve index.html for root path
        if parsed_path.path == '/':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.date_time_string()}] {format % args}")

def main():
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    
    # Change to the directory containing the frontend files
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"🚀 Historical Facts Explorer Frontend")
    print(f"📁 Serving directory: {os.getcwd()}")
    print(f"🌐 Server running at: http://0.0.0.0:{port}")
    print(f"📱 Local access: http://localhost:{port}")
    print("   Press Ctrl+C to stop the server\n")
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            # Allow address reuse
            httpd.allow_reuse_address = True
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
