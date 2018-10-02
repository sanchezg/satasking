import logging
import threading
import time
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn

import click


# Settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65265

EXIT_MSG = ''

# Logger
logger = logging.getLogger(__name__)


class GroundStationServer(ThreadingMixIn, TCPServer):
    """Define the async behavior for our GroundStation socket server."""

    server_running = False

    def service_actions(self):
        """Set the inner variable `server_running` to True."""
        self.server_running = True
        super().service_actions()


class GroundStationHandler(BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server.
    Current thread: threading.current_thread()
    """

    def setup(self):
        """Append the connected client address to inner clients list."""
        try:
            # As the documentation states, this is called once before the handle method.
            self.server.clients[self.client_address[1]] = self.client_address[0]
        except AttributeError:
            self.server.clients = {}
            self.server.clients[self.client_address[1]] = self.client_address[0]
        self.client_connected = True
        logger.info("New client {}".format(self.client_address))
        logger.info("Updated clients list: {}".format(self.server.clients))

    def handle(self):
        logger.info("Accepted new client: {}".format(self.client_address))
        while(self.client_connected):
            message = self._read()
            self.process_message(message)

    def disconnect_client(self):
        """Perform needed actions when a client is disconnected."""
        del self.server.clients[self.client_address[1]]
        self.client_connected = False
        logger.info("Disconnected client: {}".format(self.client_address))
        logger.info("Updated clients list: {}".format(self.server.clients))

    def process_message(self, message):
        """Read received message and make an appropriate response."""
        if message == EXIT_MSG:
            # Empty message, remove client from list
            self.disconnect_client()
        elif message == 'hello':
            # Simple handshake
            self._write('world')
        return

    def _write(self, message):
        """Write to socket peer (socket server) the specified `message`."""
        self.request.sendall(bytes(message, 'utf-8'))
        logger.info("Sent message: {} to peer: {}".format(message, self.client_address))

    def _read(self, count=1024):
        """Read and return `count` amount (max) from socket peer (server)."""
        response = str(self.request.recv(count), 'utf-8')
        logger.info("Received message: {} from peer: {}".format(response, self.client_address))
        return response


@click.command()
@click.option('--host', default=DEFAULT_HOST, help='Host where the socket server will listen.')
@click.option('--port', default=DEFAULT_PORT, help='Port where the socket server will listen.')
def main(host, port):
    """Run app GroundStation and listen for user commands.

    Init the GroundStation instance and dispatch it execution.

    """
    def wait_for_server():
        while not server.server_running:
            pass
    server = GroundStationServer((host, port), GroundStationHandler)
    th_server = threading.Thread(target=server.serve_forever)
    th_server.start()
    wait_for_server()
    logger.info("Server running!")
    try:
        while(server.server_running):
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        logger.info('Program aborted!')
        server.shutdown()
        th_server.join()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    main()
