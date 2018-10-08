import logging
import threading
from django.conf import settings
from django.db import models

from simulator.ground_station import GroundStationServer


logger = logging.getLogger(__name__)


class GroundStation(models.Model):
    hostname = models.CharField(max_length=64, default=settings.DEFAULT_SERVER_HOSTNAME,
                                help_text="Server hostname where will be listening.")
    port = models.PositiveIntegerField(default=settings.DEFAULT_SERVER_PORT,
                                       help_text="Server port where will be listening.")
    running = models.BooleanField(default=False, editable=False)

    def run(self):
        """Execute the SocketServer for GroundStation."""
        if self.running:
            logger.error("Currently Server seems to be already running, if not, please stop it.")
            return
        server = GroundStationServer(self.hostname, self.port)
        th_server = threading.Thread(target=server.serve_forever)
        th_server.start()
        settings.SERVER = server  # Save the running server instance reference
        settings.SERVER_TH = th_server  # Save the running thread instance reference
        self.running = True
        self.save()

    def stop(self):
        """Stop the running SocketServer."""
        if not self.running:
            logger.error("Currently Server seems to be already stopped.")
            return
        try:
            settings.SERVER.shutdown()
        except AttributeError:
            logger.error("Seems that currently server has been lost")
        else:
            # Wipe references and memory will be freed by gc
            settings.SERVER = None
            settings.SERVER_TH = None
        self.running = False
        self.save()

    def dispatch_tasks(self, tasks):
        """Call the dispatch _tasks method from SocketServer with desired tasks to dispatch to
        clients."""
        settings.SERVER.dispatch_tasks(tasks)


class Satellite(models.Model):
    hostname = models.CharField(max_length=64, default=settings.DEFAULT_SERVER_HOSTNAME,
                                help_text="Server hostname where this client will connect.")
    port = models.PositiveIntegerField(default=settings.DEFAULT_SERVER_PORT,
                                       help_text="Server port where this client will connect.")
    resources = models.CharField(max_length=settings.MAX_CHAR_LENGTH,
                                 help_text="Comma separated resources ids.")


class Task(models.Model):
    """Represent a task in the system."""
    name = models.CharField(max_length=settings.MAX_CHAR_LENGTH, help_text="Task name")
    payoff = models.PositiveIntegerField(help_text="Task payoff")
    resources = models.CharField(max_length=settings.MAX_CHAR_LENGTH,
                                 help_text="Comma separated resources ids.")

    def __repr__(self):
        args = {
            'name': self.name,
            'payoff': self.payoff,
            'resources': self.resources
        }
        return "Task(name={name}, payoff={payoff}, resources={resources})"\
               .format(**args)
