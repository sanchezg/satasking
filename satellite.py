import logging
import selectors
import socket

import click


# Settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65265
EVENT_MASK = selectors.EVENT_READ | selectors.EVENT_WRITE


# Logger
logger = logging.getLogger(__name__)


def connect_server(host, port):
    sel = selectors.DefaultSelector()
    addr = (host, port)
    logger.info('Connected to {}'.format(addr))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    sel.register(sock, EVENT_MASK, data=None)
    return sel


@click.command()
@click.option('--host', default=DEFAULT_HOST, help='Host where the socket server will listen.')
@click.option('--port', default=DEFAULT_PORT, help='Port where the socket server will listen.')
@click.option('--resources', '-r', multiple=True,
              help='Resource id that this satellite will handle.')
def sate_loop(host, port, resources):
    """Execute server main loop listening for new connections or clients responses."""
    sel = connect_server(host, port)
    try:
        while True:
            events = sel.select(timeout=None)
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print('caught keyboard interrupt, exiting')
    finally:
        sel.close()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    sate_loop()
