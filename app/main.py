import sys


def get_command():
    if len(sys.argv) != 2:
        return None
    command = sys.argv[1]
    if command not in ('server', 'deploy'):
        return None
    return command

command = get_command()

if command is None:
    print('Invalid arguments.\nUsage: python app/main.py <server|deploy>')

elif command == 'server':
    from server import server
    server.run()

elif command == 'deploy':
    from deployment import deployment_manager
    deployment_manager.run()
