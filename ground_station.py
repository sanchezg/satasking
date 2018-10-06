import ast
import logging
import threading
import time
from collections import defaultdict
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn

import click


DEBUG = True


# Settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 65265

EXIT_MSG = ''

# Logger
logger = logging.getLogger(__name__)

# Messages
MSG_OK = "ok"
MSG_PING = "hello"
MSG_PONG = "world"
MSG_RESOURCES_PREFIX = "::r::"
MSG_TASK_PREFIX = "::t::"
MSG_SEPARATOR = "::"

tasks = []


class GroundStationServer(ThreadingMixIn, TCPServer):
    """Define the async behavior for our GroundStation socket server."""

    server_running = False
    tasks = []
    resources_by_clients = defaultdict(set)  # Indicates the resources that have available a client
    clients = defaultdict(dict)

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

    def dispatch_tasks(self):
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
            (idx, float(t.payoff) / len(t.resources)) for idx, t in enumerate(self.tasks)
        ]
        payoff_by_resources.sort(key=lambda x: x[1], reverse=True)

        # import ipdb; ipdb.set_trace()
        # Algorithm
        for idx, _ in payoff_by_resources:
            task_resources = self.tasks[idx].resources  # task resources
            clients_available = set([handler for handler in self.clients]) # Will address clients who can process this task
            for tr in task_resources:
                clients_available &= self.resources_by_clients[tr]
            try:
                candidate = clients_available.pop()
            except KeyError:
                logger.error("There's no available client to process this task: {}"
                             .format(self.tasks[idx].name))
            else:
                # Remove resource available from client
                for r in self.tasks[idx].resources:
                    self.resources_by_clients[r].remove(candidate)
                # Delegate task to client
                results[self.tasks[idx].name] = candidate
                total_payoff += self.tasks[idx].payoff
                self.clients[candidate]['tasks'].append(self.tasks[idx])
                candidate.new_task_available(self.tasks[idx])
                self.tasks.pop(idx)
        logger.debug("Results: {}".format(results))
        logger.debug("Resources available: {}".format(self.resources_by_clients))
        logger.debug("Total payoff: {}".format(total_payoff))
        # return results, self.resources_by_clients, total_payoff


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
        # import ipdb; ipdb.set_trace()
        if message == EXIT_MSG:
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
        self.request.sendall(bytes(message, 'utf-8'))
        logger.debug("Sent message: {} to peer: {}".format(message, self.client_address))

    def _read(self, count=1024):
        """Read and return `count` amount (max) from socket peer (server)."""
        response = str(self.request.recv(count), 'utf-8')
        logger.debug("Received message: {} from peer: {}".format(response, self.client_address))
        return response


class Satellite:

    def __init__(self, name, resources):
        self.name = name
        self.resources = resources


class Task:
    """Simple structure to represent a task."""

    def __init__(self, name, payoff, resources):
        self.name = name
        self.payoff = int(payoff)
        self.resources = resources

    def __str__(self):
        args = {
            'name': self.name,
            'payoff': self.payoff,
            'resources': self.resources
        }
        return "Task(name={name}, payoff={payoff}, resources={resources})"\
               .format(**args)


def create_task(*args):
    """Create a task and appends to server tasks."""
    server_instance = args[0]
    name = input("Task name> ")
    payoff = input("Payoff> ")
    resources = input("Resources (separated by spaces)> ").split()
    t = Task(name, payoff, resources)
    server_instance.tasks.append(t)
    logger.debug("Task created: {}".format(t))
    return


def dispatch_tasks(*args):
    server_instance = args[0]
    server_instance.dispatch_tasks()


def show_tasks(*args):
    """Show tasks created."""
    server_instance = args[0]

    for task in server_instance.tasks:
        print(task)


def menu(server_instance):
    """Print in console the interactive menu and call proper action."""
    print(
        "\n"
        "1. Insert new task\n"
        "2. Dispatch tasks to satellites\n"
        "3. Show tasks\n"
        "4. Exit program\n"
    )
    
    options = {
        '1': create_task,
        '2': dispatch_tasks,
        '3': show_tasks,
        '4': exit
    }
    option = input("Choose option number> ")
    try:
        options[option](server_instance)
    except KeyError:
        logger.warning("Error, bad option number!")


def create_debug_tasks(server_instance):
    tasks_def = {
        't1': (['1', '2', '3', '5'], 150),
        't2': (['1', '6', '3', '4'], 250),
        't3': (['1', '2'], 50),
        't4': (['2', '3', '6'], 100),
        't5': (['2', '3', '5', '8'], 125),
        't6': (['1', '2', '3', '4'], 450),
    }
    tasks = [
        Task(k, v[1], v[0]) for k, v in tasks_def.items()
    ]
    server_instance.tasks += tasks
    logger.debug("Created debug tasks")


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
    if DEBUG:
        create_debug_tasks(server)
    try:
        while(server.server_running):
            menu(server)
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
