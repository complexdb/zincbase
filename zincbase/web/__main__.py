import argparse

from .socket_server import serve

parser = argparse.ArgumentParser(prog='python3 -m zincbase.web')
parser.add_argument('--redis', help='Address of Redis instance (default: localhost:6379)',
                      default='localhost:6379', type=str)

if __name__ == '__main__':
    args = parser.parse_args()
    serve(args)