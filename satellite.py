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


class Satellite:
    def __init__(self, host, port, *resources):
        self.host = host
        self.port = port
        self.selector = None
        self.resources = resources

    def init_client(self):
        if self.selector is not None:
            raise RuntimeError("init_client should be called once")
        self.selector = selectors.DefaultSelector()
        self._connect_server()

    def _connect_server(self):
        """Connect to specified server."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex((self.host, self.port))
        logger.info('Connected to {}'.format((self.host, self.port)))
        self.selector.register(sock, EVENT_MASK, data=None)

    def run(self):
        if self.selector is None:
            self.init_client()
        # TODO: Move to a separated block
        try:
            while True:
                events = self.selector.select(timeout=None)
                # Check for a socket being monitored to continue.
                if not self.selector.get_map():
                    break
        except KeyboardInterrupt:
            print('caught keyboard interrupt, exiting')
        finally:
            self.selector.close()


@click.command()
@click.option('--host', default=DEFAULT_HOST, help='Host where the socket server will listen.')
@click.option('--port', default=DEFAULT_PORT, help='Port where the socket server will listen.')
@click.option('--resources', '-r', multiple=True,
              help='Resource id that this satellite will handle.')
def main(host, port, resources):
    sate = Satellite(host, port, resources)
    sate.run()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    main()
