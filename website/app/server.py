from http.server import HTTPServer
import importlib
import command_helper


class MyHTTPServer(HTTPServer):

    def __init__(self, server_address):
        self.request_handler_module = importlib.import_module('request_handler')
        HTTPServer.__init__(self, server_address, self.request_handler_module.MyRequestHandler)
        self.deploy_needed = False

    def process_request(self, request, client_address):
        HTTPServer.process_request(self, request, client_address)
        if self.deploy_needed:
            print('Running the deployment script...')
            command = ['python3', 'deployment/deployment_manager.py']
            command_result = command_helper.command_run(command, timeout=60, cwd='../source')
            print('Deployment script finished! Result:')
            print(command_result.asdict())
            self.request_handler_module = importlib.reload(self.request_handler_module)
            self.RequestHandlerClass = self.request_handler_module.MyRequestHandler
            self.deploy_needed = False
            print('Deployed!')


port = 8080
server_address = ('', port)
httpd = MyHTTPServer(server_address)
print(f'Server running on port {port}...')
httpd.serve_forever()

