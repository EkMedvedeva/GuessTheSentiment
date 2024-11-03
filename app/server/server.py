from http.server import ThreadingHTTPServer
from http import HTTPStatus
import importlib
import ssl

from server.base_request_handler import MyBaseRequestHandler, InvalidRequestData, InternalError
from helpers import command_helper


CERT_FILE_PATH = '/etc/letsencrypt/live/guess-the-sentiment.com/fullchain.pem'
KEY_FILE_PATH = '/etc/letsencrypt/live/guess-the-sentiment.com/privkey.pem'


class DeploymentRequestHandler(MyBaseRequestHandler):

    def request_handle(self, full_path):
        
        if full_path == ('GET', '/'):
            with open('website/static/maintenance.html', 'rb') as file:
                data = file.read()
            self._send_html(data)

        else:
            data = {'error': 'Website under maintenance'}
            self._send_error(data, HTTPStatus.SERVICE_UNAVAILABLE)


class MyHTTPServer(ThreadingHTTPServer):

    def __init__(self, server_address):
        self.request_handler_module = importlib.import_module('server.request_handler')
        ThreadingHTTPServer.__init__(self, server_address, self.request_handler_module.MyRequestHandler)
        self.socket = ssl.wrap_socket(
            self.socket,
            certfile=CERT_FILE_PATH,
            keyfile=KEY_FILE_PATH,
            server_side=True
        )

    def deployment_start(self):
        self.RequestHandlerClass = DeploymentRequestHandler

    def deployment_finalize(self):
        self.request_handler_module = importlib.reload(self.request_handler_module)
        self.RequestHandlerClass = self.request_handler_module.MyRequestHandler


def run():
    port = 443
    server_address = ('', port)
    httpd = MyHTTPServer(server_address)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

