from http.server import ThreadingHTTPServer
from http import HTTPStatus
import importlib
from ssl import SSLContext

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

    def __init__(self, server_address, use_ssl=True):
        self.request_handler_module = importlib.import_module('server.request_handler')
        ThreadingHTTPServer.__init__(self, server_address, self.request_handler_module.MyRequestHandler)
        if use_ssl:
            self.ssl_context = SSLContext()
            self.ssl_context.load_cert_chain(CERT_FILE_PATH, keyfile=KEY_FILE_PATH)
            self.socket = self.ssl_context.wrap_socket(
                self.socket,
                server_side=True
            )

    def deployment_start(self):
        self.RequestHandlerClass = DeploymentRequestHandler

    def deployment_finalize(self):
        self.request_handler_module = importlib.reload(self.request_handler_module)
        self.RequestHandlerClass = self.request_handler_module.MyRequestHandler


def run(local):
    if local:
        port = 80
        use_ssl = False
    else:
        port = 443
        use_ssl = True
    server_address = ('', port)
    httpd = MyHTTPServer(server_address, use_ssl=use_ssl)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

