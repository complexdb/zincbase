import context

import pytest

from zincbase.web import socket_server

class Args:
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

args = Args(redis='localhost:6379')

@pytest.fixture(scope='session')
def server_and_args():
    yield socket_server.app, socket_server.serve, args