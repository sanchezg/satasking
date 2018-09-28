import logging
import selectors
import socket

import click


# Settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65265


# Logger
logger = logging.getLogger(__name__)


class Satellite:
    def __init__(self, host, port, *resources):
        self.host = host
        self.port = port
        self.resources = resources
        self.connected = False
        self.encoding = 'utf-8'

    def init_client(self):
        """Init instance and connect to specified server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.connect_ex((self.host, self.port))
        logger.info('Connected to {}'.format((self.host, self.port)))
        # TODO: Still not working
        # self.init_connection()
        self.connected = True

    def init_connection(self):
        """Init a very simple protocol.

        Init a very simple protocol to check connection and notice the server that this
        client is ready to receive commands.
        """
        self.write('hello')
        response = self.read()
        if response == 'world':
            self.connected = True
        else:
            logger.error("Can't connect to server, try again later.")
        return

    def write(self, message):
        """Write to socket peer (socket server) the specified `message`."""
        self.socket.sendall(bytes(message, self.encoding))
        logger.info("Sent message: {} to peer: {}".format(message, self.socket.getpeername()))

    def read(self, count=1024):
        """Read and return `count` amount (max) from socket peer (server)."""
        response = str(self.socket.recv(count), self.encoding)
        logger.info("Received message: {} from peer: {}".format(response, self.socket.getpeername()))
        return response

    def wait_for_command(self):
        """Wait until receives a new message from peer and process it as a command."""
        message = self.read()
        self.process_message(message)

    def process_message(self, message):
        """Process incoming message from peer, and call the proper action."""
        # TODO
        pass

    def run(self):
        if not self.connected:
            self.init_client()
        try:
            while self.connected:
                # TODO: Still not working
                # self.wait_for_command()
                pass
        except KeyboardInterrupt:
            print('caught keyboard interrupt, exiting')


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