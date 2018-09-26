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


class GroundStation:
    """Represent the ground station that will handle tasking to remote clients satellites.

    By default the GroundStation listen on port 65265. This behavior can be set with `port`
    argument.
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.selector = None
        self.clients = []

    def init_server(self):
        """Init and start the socket server.

        Init a socket server and bind it to the specified host and port.
        The socket is configured as non-blocking.
        """
        if self.selector is not None:
            raise RuntimeError("init_server should be called once")
        self.selector = selectors.DefaultSelector()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.host, self.port))
        lsock.listen()
        logger.info('Listening on {}'.format((self.host, self.port)))
        lsock.setblocking(False)
        self.selector.register(lsock, EVENT_MASK, data=None)

    def connect_client(self, socket_fd):
        conn, addr = socket_fd.accept()
        logger.info('Accepted connection from {}'.format(addr))
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, data=None)
        self.clients.append(conn)

    def disconnect_client(self, sock):
        """Unregister a client."""
        try:
            self.selector.unregister(sock)
        except Exception as e:
            logger.error(f'Error disconnecting client %s' % repr(e))
        else:
            logger.info("Unregistered client from %s" % repr(sock.getpeername()))
            sock.close()
            sock = None  # delete reference for gc

    def run(self):
        """Execute main loop."""
        if self.selector is None:
            self.init_server()
        # TODO: this loop should be executed in a separated thread
        try:
            while True:
                events = self.selector.select(timeout=None)  # block untils there're any sockets ready for I/O
                for key, mask in events:
                    if key.data is None:
                        # from listening socket, then accept connection
                        try:
                            self.connect_client(key.fileobj)
                        except OSError:
                            # Client socket disconnected
                            self.disconnect_client(key.fileobj)
                    else:
                        pass  # Do nothing by now
        except KeyboardInterrupt:
            logger.info('caught keyboard interrupt, exiting')
        finally:
            self.shutdown()

    def shutdown(self):
        """Perform shutdown operations, like closing the selector and opened sockets."""
        self.selector.close()


@click.command()
@click.option('--host', default=DEFAULT_HOST, help='Host where the socket server will listen.')
@click.option('--port', default=DEFAULT_PORT, help='Port where the socket server will listen.')
def main(host, port):
    gs = GroundStation(host, port)
    gs.run()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    main()
