from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import json


class InvalidRequestData(Exception):
    pass

class InternalError(Exception):
    pass


class MyBaseRequestHandler(BaseHTTPRequestHandler):

    def _send_response(self, content_type, data, code=HTTPStatus.OK):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, data):
        self._send_response('text/html', data)

    def _send_css(self, data):
        self._send_response('text/css', data)

    def _send_js(self, data):
        self._send_response('application/javascript', data)

    def _send_json(self, data):
        encoded_data = json.dumps(data).encode()
        self._send_response('application/json', encoded_data)

    def _send_chunked_json(self, data, first=False):
        if first:
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
        if data is None:
            encoded_data = b''
        else:
            encoded_data = json.dumps(data).encode() + b'\n'
        chunk_data = b'%X\r\n%s\r\n' % (len(encoded_data), encoded_data)
        self.wfile.write(chunk_data)
        self.wfile.flush()

    def _send_error(self, data, code):
        encoded_data = json.dumps(data).encode()
        self._send_response('application/json', encoded_data, code=code)
    
    def _receive_json(self):
        content_length = int(self.headers['Content-Length'])
        encoded_data = self.rfile.read(content_length)
        try:
            data = json.loads(encoded_data)
        except json.JSONDecodeError as error:
            raise InvalidRequestData('Invalid JSON')
        return data

    def do_GET(self):
        self.base_request_handle()

    def do_POST(self):
        self.base_request_handle()

    def do_PUT(self):
        self.base_request_handle()

    def base_request_handle(self):
        try:

            full_path = (self.command, self.path)
            self.request_handle(full_path)
            
        except InvalidRequestData as error:
            data = {'error': f'Invalid request data: {error}'}
            self._send_error(data, HTTPStatus.BAD_REQUEST)

        except InternalError as error:
            data = {'error': 'Internal server error'}
            self._send_error(data, HTTPStatus.INTERNAL_SERVER_ERROR)
        

