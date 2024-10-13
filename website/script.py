from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import random
import subprocess


class ReviewLoader:

    def __init__(self):
        with open('reviews/mattress/data.json', 'r') as file:
            mattress_data = json.loads(file.read())
        
        self.product = mattress_data['product']
        self.reviews = mattress_data['reviews']

    def get_random_review(self):
        return random.choice(self.reviews)


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
                with open('website/home.html', 'rb') as file:
                    data = file.read()
                self._send_html(data)
            
            elif self.path == '/style.css':
                with open('website/style.css', 'rb') as file:
                    data = file.read()
                self._send_css(data)
            
            elif self.path == '/script.js':
                with open('website/script.js', 'rb') as file:
                    data = file.read()
                self._send_js(data)
            
            elif self.path == '/review':
                review = review_loader.get_random_review()
                review_rating = review['rating']
                review_title = review['title']
                review_text = review['review']
                data = {
                    'product': review_loader.product['name'],
                    'product_description': review_loader.product['description'],
                    'review': f'Rating: {review_rating}/5\nTitle: {review_title}\nComment: {review_text}'
                }
                self._send_json(data)
            
            elif self.path == '/admin/check-update':
                data = []
                
                command = ['git', 'remote', 'update']
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = process.communicate(timeout=5)
                data.append({
                    'command': command,
                    'output': output.decode('utf-8', errors='ignore'),
                    'error': error.decode('utf-8', errors='ignore')
                })
                
                command = ['git', 'status', '-uno']
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = process.communicate(timeout=5)
                data.append({
                    'command': command,
                    'output': output.decode('utf-8', errors='ignore'),
                    'error': error.decode('utf-8', errors='ignore')
                })
                
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

    review_loader = ReviewLoader()
    
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f'Server running on port {port}...')
    httpd.serve_forever()
