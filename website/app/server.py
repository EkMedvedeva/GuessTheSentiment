from http.server import HTTPServer
import importlib

request_handler = importlib.import_module('request_handler')


class MyHTTPServer(HTTPServer):

    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.deploy_needed = False

    def process_request(self, request, client_address):
        HTTPServer.process_request(self, request, client_address)
        if self.deploy_needed:
            global request_handler
            request_handler = importlib.reload(request_handler)
            self.RequestHandlerClass = request_handler.MyRequestHandler
            self.deploy_needed = False
            print('Deployed!')


port = 8080
server_address = ('', port)
httpd = MyHTTPServer(server_address, request_handler.MyRequestHandler)
print(f'Server running on port {port}...')
httpd.serve_forever()

