from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class InvalidRequestData(Exception):
    pass

class InternalError(Exception):
    pass


class MyRequestHandler(BaseHTTPRequestHandler):

    def _send_response(self, content_type, data, code=200):
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

    def _send_error(self, data):
        encoded_data = json.dumps(data).encode()
        self._send_response('application/json', encoded_data, code=400)

    def _receive_json(self):
        content_length = int(self.headers['Content-Length'])
        encoded_data = self.rfile.read(content_length)
        try:
            data = json.loads(encoded_data)
        except json.JSONDecodeError:
            raise InvalidRequestData('Invalid JSON')
        return data
    
    def do_GET(self):

        try:
            
            if self.path == '/':
                with open('home.html', 'rb') as file:
                    data = file.read()
                self._send_html(data)
                    
            elif self.path == '/style.css':
                with open('style.css', 'rb') as file:
                    data = file.read()
                self._send_css(data)
                    
            elif self.path == '/script.js':
                with open('script.js', 'rb') as file:
                    data = file.read()
                self._send_js(data)
                    
            elif self.path == '/review':
                data = {
                    'product': 'Shampoo',
                    'product_description': 'Roslin shampoo offers gentle care for all hair types and the scalp, thanks to its neutral pH 5.5, making it perfect for daily use.',
                    'review': '"Large volume, colorless, thick, pleasant smell. Doesn’t lather very well, you need to use a bit more for washing hair. Tried it out, had a different one before. I think it lathers poorly, you need to use a bit more. The smell is nice, not sharp, pleasant, lasts about five hours. Rinses well, thick. The neck under the cap is sealed with foil. Colorless. Worth buying."'
                }
                self._send_json(data)
                
        except InvalidRequestData as e:
            data = {'error': f'Invalid request data: {e}'}
            self._send_error(data)

        except InternalError as e:
            data = {'error': 'Internal server error'}
            self._send_error(data)
    
    
    def do_PUT(self):

        try:
            
            if self.path == '/rate':
                data = self._receive_json()
                try:
                    rating = int(data['rating'])
                except Exception as e:
                    raise InvalidRequestData('rating needs to be an integer')
                self._send_json({})
                
        except InvalidRequestData as e:
            data = {'error': f'Invalid request data: {e}'}
            self._send_error(data)

        except InternalError as e:
            data = {'error': 'Internal server error'}
            self._send_error(data)
        

if __name__ == '__main__':
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f'Server running on port {port}...')
    httpd.serve_forever()
