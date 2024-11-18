import sys


def main():
    
    command = sys.argv[1]
    options = sys.argv[2:]
    
    if command == 'server':
        local = '--local' in options
        from server import server
        server.run(local)
        return
    
    if command == 'deploy':
        from deployment import deployment_manager
        deployment_manager.run()
        return
    
    print('Invalid arguments.\nUsage: python app/main.py <server|deploy>')


main()

