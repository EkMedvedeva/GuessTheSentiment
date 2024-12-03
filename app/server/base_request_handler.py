from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import json
import urllib.parse


class InvalidRequestData(Exception):
    pass

class InternalError(Exception):
    pass


class MyBaseRequestHandler(BaseHTTPRequestHandler):

    def _send_response(self, content_type, data, code=HTTPStatus.OK, location=None):
        self.send_response(code)
        if content_type is not None:
            self.send_header('Content-type', content_type)
        if location is not None:
            self.send_header('Location', location)
        self.end_headers()
        if data is not None:
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

    def _send_image(self, data):
        self._send_response('image/jpeg', data)

    def _send_svg(self, data):
        self._send_response('image/svg+xml', data)

    def _send_pdf(self, data):
        self._send_response('application/pdf', data)

    def _send_error(self, data, code):
        encoded_data = json.dumps(data).encode()
        print(f'Sending error code {code}, data:\n{data}')
        self._send_response('application/json', encoded_data, code=code)

    def _send_redirect(self, location):
        self._send_response(None, None, code=HTTPStatus.MOVED_PERMANENTLY, location=location)
    
    def _receive_json(self):
        if self.command == 'GET':
            # Special case for GET requests, there is no body
            # Convert the query string into a dictionary instead
            query = self.parse_result.query
            query_data = urllib.parse.parse_qs(query)
            for key in query_data:
                if len(query_data[key]) > 1:
                    raise InvalidRequestData('Invalid query')
                query_data[key] = query_data[key][0]
            return query_data
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

            host = self.headers.get('Host')
            if host is not None and host.startswith('www.'):
                location = f'http://{host[4:]}{self.path}'
                self._send_redirect(location)
                return
            
            self.parse_result = urllib.parse.urlparse(self.path)
            full_path = (self.command, self.parse_result.path)
            self.request_handle(full_path)
            
        except InvalidRequestData as error:
            data = {'error': f'Invalid request data: {error}'}
            self._send_error(data, HTTPStatus.BAD_REQUEST)

        except InternalError as error:
            data = {'error': 'Internal server error'}
            self._send_error(data, HTTPStatus.INTERNAL_SERVER_ERROR)
        

