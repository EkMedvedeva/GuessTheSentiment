from http.server import HTTPServer
from base_request_handler import MyBaseRequestHandler, InvalidRequestData, InternalError
import importlib
import command_helper


class DeploymentRequestHandler(MyBaseRequestHandler):

    def request_handle(self, full_path):
        
        if full_path == ('GET', '/'):
            with open('website/static/maintenance.html', 'rb') as file:
                data = file.read()
            self._send_html(data)

        else:
            data = {'error': 'Website under maintenance'}
            self._send_error(data, HTTPStatus.SERVICE_UNAVAILABLE)


class MyHTTPServer(HTTPServer):

    def __init__(self, server_address):
        self.request_handler_module = importlib.import_module('request_handler')
        HTTPServer.__init__(self, server_address, self.request_handler_module.MyRequestHandler)

    def deployment_start(self):
        self.RequestHandlerClass = DeploymentRequestHandler

    def deployment_finalize(self):
        self.request_handler_module = importlib.reload(self.request_handler_module)
        self.RequestHandlerClass = self.request_handler_module.MyRequestHandler


port = 8080
server_address = ('', port)
httpd = MyHTTPServer(server_address)
print(f'Server running on port {port}...')
httpd.serve_forever()

