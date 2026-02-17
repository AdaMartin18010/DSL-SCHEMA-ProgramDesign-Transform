#!/usr/bin/env python3
"""
Schema Tools REST API
提供HTTP接口用于Schema验证和转换
"""

import json
import sys
sys.path.insert(0, '../Tools')

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from schema_validator import SchemaValidator


class SchemaAPIHandler(BaseHTTPRequestHandler):
    """Schema API请求处理器"""
    
    validator = SchemaValidator()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/health':
            self._send_json({'status': 'healthy', 'version': '1.0.0'})
        
        elif path == '/api/v1/docs':
            self._send_json({
                'endpoints': [
                    {'path': '/health', 'method': 'GET'},
                    {'path': '/api/v1/validate', 'method': 'POST'}
                ]
            })
        
        else:
            self._send_error(404, 'Not found')
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._send_error(400, 'Invalid JSON')
            return
        
        if path == '/api/v1/validate':
            self._handle_validate(data)
        
        else:
            self._send_error(404, 'Not found')
    
    def _handle_validate(self, data):
        """处理验证请求"""
        schema = data.get('schema')
        document = data.get('document')
        
        if not schema or not document:
            self._send_error(400, 'Missing schema or document')
            return
        
        result = self.validator.validate_json_schema_detailed(document, schema)
        self._send_json(result)
    
    def _send_json(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status, message):
        """发送错误响应"""
        self._send_json({'error': message}, status)


def run_server(port=8000):
    """运行API服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SchemaAPIHandler)
    print(f"Schema API Server running on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
