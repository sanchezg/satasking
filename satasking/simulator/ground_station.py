import logging
from collections import defaultdict
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn

from django.conf import settings

from simulator.messages import (MSG_ENCODING, MSG_NULL, MSG_OK, MSG_PING, MSG_PONG,
                                MSG_RESOURCES_PREFIX, MSG_SEPARATOR, MSG_TASK_PREFIX)

# Logger
logger = logging.getLogger(__name__)


class GroundStationServer(ThreadingMixIn, TCPServer):
    """Define the async behavior for our GroundStation socket server."""

    server_running = False
    tasks = []
    resources_by_clients = defaultdict(set)  # Indicates the resources that have available a client
    clients = defaultdict(dict)

    def __init__(self, host, port):
        """Init a SocketServer with `GroundStationHandler`."""
        super().__init__((host, port), GroundStationHandler)
        if settings.DEBUG:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            logger.debug("Server up and running!")

    def service_actions(self):
        """Set the inner variable `server_running` to True."""
        self.server_running = True
        super().service_actions()

    def update_resources(self, client, resources):
        """Update inner `resources_by_clients` dict."""
        for res in resources:
            self.resources_by_clients[res].add(client)
        self.clients[client]['resources'] = resources
        self.clients[client]['tasks'] = []
        logger.debug("Updated resources information: {}".format(self.resources_by_clients))
        logger.debug("Updated clients information: {}".format(self.clients[client]))

    def dispatch_tasks(self, tasks):
        """Dispatch all registered tasks to be executed by the available clients.

        Use a kind of greedy choice to dispatch tasks to the clients with corresponding
        resources available.
        `payoff_by_resources` is a sorted list where the order is defined by `payoff/n_resources`
        where `n_resources` is the amount of required resources by the task and `payoff` is the
        payoff of the task.
        First we choose to deliver the tasks with highest `payoff/n_resources` to lower ones.
        Then we look for all clients with the required resources available, and choose the first
        one as `candidate` to execute the task.
        Then we must disassociate required resources with the candidate client.
        As final step, we send a message to all clients with tasks that must execute addressed
        tasks.
        """
        total_payoff = 0  # Total payoff to be executed
        results = dict()  # dict with pair of 'task_name': 'satellite'

        # Sort tasks to be processed to maximize payoff
        payoff_by_resources = [
            # Keep idx of task in original list
            (idx, float(t.payoff) / len(t.resources)) for idx, t in enumerate(tasks)
        ]
        payoff_by_resources.sort(key=lambda x: x[1], reverse=True)

        # Algorithm
        for idx, _ in payoff_by_resources:
            task_resources = tasks[idx].resources.split(',')  # task resources
            clients_available = set([handler for handler in self.clients])  # TODO: Can be improved
            for tr in task_resources:
                clients_available &= self.resources_by_clients[tr]
            try:
                candidate = clients_available.pop()
            except KeyError:
                logger.error("There's no available client to process this task: {}"
                             .format(tasks[idx].name))
            else:
                # Remove resource available from client
                for r in task_resources:
                    self.resources_by_clients[r].remove(candidate)
                # Delegate task to client
                results[tasks[idx].name] = candidate
                total_payoff += tasks[idx].payoff
                self.clients[candidate]['tasks'].append(tasks[idx])
                candidate.new_task_available(tasks[idx])
        logger.debug("Results: {}".format(results))
        logger.debug("Resources available: {}".format(self.resources_by_clients))
        logger.debug("Total payoff: {}".format(total_payoff))


class GroundStationHandler(BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server.
    Current thread: threading.current_thread()
    """

    def setup(self):
        """Append the connected client address to inner clients list."""
        self.server.clients[self]['address'] = (self.client_address[0], self.client_address[1])
        self.client_connected = True
        logger.info("New client {}".format(self.client_address))
        logger.debug("Updated clients list: {}".format(self.server.clients))

    def handle(self):
        logger.debug("Accepted new client: {}".format(self.client_address))
        while(self.client_connected):
            message = self._read()
            self.process_message(message)

    def disconnect_client(self):
        """Perform needed actions when a client is disconnected."""
        del self.server.clients[self]
        self.client_connected = False
        logger.debug("Disconnected client: {}".format(self.client_address))
        logger.debug("Updated clients list: {}".format(self.server.clients))

    def new_task_available(self, task):
        """Called from the server when a new task is available for this client."""
        message = "{n}{sep}{p}{sep}{r}".format(n=task.name, sep=MSG_SEPARATOR,
                                               p=task.payoff, r=task.resources)
        self._write("%s%s" % (MSG_TASK_PREFIX, message))

    def process_message(self, message):
        """Read received message and make an appropriate response."""
        if message == MSG_NULL:
            # Empty message, remove client from list
            self.disconnect_client()
        elif message == MSG_PING:
            # Simple handshake
            self._write(MSG_PONG)
        elif MSG_RESOURCES_PREFIX in message:
            resources_list = message.split(MSG_RESOURCES_PREFIX)[1].split(',')
            logger.debug("delegate message with: {}".format(resources_list))
            self.server.update_resources(self, resources_list)
            self._write(MSG_OK)
        return

    def _write(self, message):
        """Write to socket peer (socket server) the specified `message`."""
        self.request.sendall(bytes(message, MSG_ENCODING))
        logger.debug("Sent message: {} to peer: {}".format(message, self.client_address))

    def _read(self, count=1024):
        """Read and return `count` amount (max) from socket peer (server)."""
        response = str(self.request.recv(count), MSG_ENCODING)
        logger.debug("Received message: {} from peer: {}".format(response, self.client_address))
        return response
