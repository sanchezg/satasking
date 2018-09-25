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


def run_server(host, port):
    """Execute a socket server and binds to specified host and port.

    Return the selector used to switch between sockets.
    """
    sel = selectors.DefaultSelector()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    logger.info('Listening on {}'.format((host, port)))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    return sel


def connect_client(sel, sock):
    """Accept and register a new socket client connection."""
    conn, addr = sock.accept()  # Should be ready to read
    logger.info('accepted connection from {}'.format(addr))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=None)


def disconnect_client(sel, sock):
    """Unregister a client."""
    try:
        sel.unregister(sock)
        sock.close()
    except Exception as e:
        logger.error(f'error: selector.unregister() exception for',
                     {repr(e)})
    else:
        sock = None  # delete reference for gc
        logger.info("Unregistered client")

@click.command()
@click.option('--host', default=DEFAULT_HOST, help='Host where the socket server will listen.')
@click.option('--port', default=DEFAULT_PORT, help='Port where the socket server will listen.')
def server_loop(host, port):
    """Execute server main loop listening for new connections or clients responses."""
    sel = run_server(host, port)
    try:
        while True:
            events = sel.select(timeout=None)  # block untils there're any sockets ready for I/O
            for key, mask in events:
                if key.data is None:
                    # from listening socket, then accept connection
                    try:
                        connect_client(sel, key.fileobj)
                    except OSError:
                        # Socket disconnected
                        disconnect_client(sel, key.fileobj)
                else:
                    pass  # Do nothing by now
    except KeyboardInterrupt:
        logger.info('caught keyboard interrupt, exiting')
    finally:
        sel.close()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    server_loop()
