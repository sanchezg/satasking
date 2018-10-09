import ast
import logging
import socket

from django.conf import settings

from simulator.messages import (MSG_ENCODING, MSG_DISCONNECT, MSG_OK, MSG_PING, MSG_PONG,
                                MSG_RESOURCES_PREFIX, MSG_SEPARATOR, MSG_TASK_PREFIX)

# Logger
logger = logging.getLogger(__name__)


class SatelliteClient:
    def __init__(self, host, port, resources):
        self.host = host
        self.port = port
        self.resources = resources.split(',')  # Total resources
        self.connected = False
        self.encoding = 'utf-8'
        self.available = [r for r in resources]  # Resources available
        self.tasks = {}
        if settings.DEBUG:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            logger.addHandler(handler)

    def init_client(self):
        """Init instance and connect to specified server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        logger.info('Connected to {}'.format((self.host, self.port)))
        self.init_connection()

    def init_connection(self):
        """Init a very simple protocol.

        Init a very simple protocol to check connection and notice the server that this
        client is ready to receive commands.
        """
        if self.ping():
            self.connected = True
            self.send_resources()
        else:
            logger.error("Can't connect to server, try again later.")
        return

    def ping(self):
        """Send a ping to server and check response.

        If response is OK return True, otherwise return False.
        """
        self.write(MSG_PING)
        response = self.read()
        return response == MSG_PONG

    def send_resources(self):
        """Communicate self resources to the server."""
        self.write("{}{}".format(MSG_RESOURCES_PREFIX, ','.join(self.resources)))
        response = self.read()
        if response != MSG_OK:
            logger.error("Can't send resources to server, exiting")
        return

    def write(self, message):
        """Write to socket peer (socket server) the specified `message`."""
        self.socket.sendall(bytes(message, self.encoding))
        logger.info("Sent message: {} to peer: {}".format(message, self.socket.getpeername()))

    def read(self, count=1024):
        """Read and return `count` amount (max) from socket peer (server)."""
        response = str(self.socket.recv(count), self.encoding)
        logger.info("Received message: {} from peer: {}".format(response,
                                                                self.socket.getpeername()))
        return response

    def wait_for_command(self):
        """Wait until receives a new message from peer and process it as a command."""
        message = self.read()
        # import ipdb; ipdb.set_trace()
        self.process_message(message)

    def process_message(self, message):
        """Process incoming message from peer, and call the proper action."""
        if MSG_TASK_PREFIX in message:
            task_message = message.split(MSG_TASK_PREFIX)[1]
            task_name, task_payoff, task_resources = task_message.split(MSG_SEPARATOR)
            task_resources = ast.literal_eval(task_resources)
            self.execute_task(task_name, task_payoff, task_resources)
        return

    def execute_task(self, name, payoff, resources):
        """."""
        self.tasks[name] = (payoff, resources)
        for res in resources:
            self.available.remove(res)
        logger.debug("Executing task '{}' with payoff '{}'".format(name, payoff))
        logger.debug("Available resources: {}".format(self.available))

    def run(self):
        if not self.connected:
            self.init_client()
        try:
            while self.connected:
                # TODO: Still not working
                self.wait_for_command()
                pass
        except KeyboardInterrupt:
            print('caught keyboard interrupt, exiting')

    def stop(self):
        """Stop and close current socket. Clean used resources."""
        self.write(MSG_DISCONNECT)
        self.socket.close()