from collections import defaultdict
from unittest.mock import MagicMock

from django.conf import settings
from django.test import TestCase

from simulator.ground_station import GroundStationServer
from simulator.models import Task


class GroundStationServerTestCase(TestCase):
    def setUp(self):
        self.t1 = Task.objects.create(name='t1', payoff=10, resources='1,2,3')
        self.t2 = Task.objects.create(name='t2', payoff=20, resources='2,3,4')
        self.t3 = Task.objects.create(name='t3', payoff=20, resources='3,4,5')

    def tearDown(self):
        """Put all inner variables from gss as it was just initialized."""
        Task.objects.all().delete()

    def test_update_resources_updates_correctly(self):
        """Check that update_resources method works correctly."""
        client_id1 = 'client1'
        client_resources1 = ['1', '2', '3', '4', '5']
        client_id2 = 'client2'
        client_resources2 = ['6', '7', '8', '9', '0']
        gss = GroundStationServer(settings.DEFAULT_SERVER_HOSTNAME, settings.DEFAULT_SERVER_PORT)
        gss.update_resources(client_id1, client_resources1)
        gss.update_resources(client_id2, client_resources2)
        for res in gss.resources_by_clients:
            # Checks that for each resource, the resource has the correct client adressed
            if res in client_resources1:
                self.assertIn(client_id1, gss.resources_by_clients[res])
                self.assertNotIn(client_id2, gss.resources_by_clients[res])
            else:
                self.assertNotIn(client_id1, gss.resources_by_clients[res])
                self.assertIn(client_id2, gss.resources_by_clients[res])

    def test_dispatch_tasks_add_task_to_client(self):
        """Check that all tasks that can be executed are assigned to clients."""
        client_id1 = MagicMock(name='c1')  # Client can be anything in this context
        client_resources1 = ['1', '2', '3', '5']  # Can execute t1
        client_id2 = MagicMock(name='c2')  # Client can be anything in this context
        client_resources2 = ['2', '3', '4', '9']  # Can execute t2
        # MonkeyPatch 'new_task_available' method from client handlers to prevent a miscalling
        client_id1.new_task_available = MagicMock()
        client_id2.new_task_available = MagicMock()
        gss = GroundStationServer(settings.DEFAULT_SERVER_HOSTNAME, settings.DEFAULT_SERVER_PORT)
        gss.update_resources(client_id1, client_resources1)
        gss.update_resources(client_id2, client_resources2)
        # First check that clients havent tasks assigned
        for c in gss.clients:
            self.assertListEqual(gss.clients[c]['tasks'], [])
        gss.dispatch_tasks([self.t1, self.t2, self.t3])
        # Check that correct tasks were assigned
        client_id1.new_task_available.assert_called_with(self.t1)
        client_id2.new_task_available.assert_called_with(self.t2)
        self.assertListEqual(gss.clients[client_id1]['tasks'], [self.t1])
        self.assertListEqual(gss.clients[client_id2]['tasks'], [self.t2])

    def test_dispatch_tasks_removes_candidate_from_resources_if_assign_task(self):
        """Check that if a task is assigned to a client, then required resources arent available
        anymore in that client.
        """
        client_id1 = MagicMock(name='c1')  # Client can be anything in this context
        client_resources1 = ['1', '2', '3', '5']  # Can execute t1, will be free '5'
        client_id2 = MagicMock(name='c2')  # Client can be anything in this context
        client_resources2 = ['2', '3', '4', '9']  # Can execute t2, will be free '9'
        # MonkeyPatch 'new_task_available' method from client handlers to prevent a miscalling
        client_id1.new_task_available = MagicMock()
        client_id2.new_task_available = MagicMock()
        gss = GroundStationServer(settings.DEFAULT_SERVER_HOSTNAME, settings.DEFAULT_SERVER_PORT)
        gss.update_resources(client_id1, client_resources1)
        gss.update_resources(client_id2, client_resources2)

        gss.dispatch_tasks([self.t1, self.t2, self.t3])
        for res in gss.resources_by_clients:
            if res in client_resources1 and res not in self.t1.resources.split(','):
                    self.assertIn(client_id1, gss.resources_by_clients[res])
            if res in client_resources2 and res not in self.t2.resources.split(','):
                    self.assertIn(client_id2, gss.resources_by_clients[res])

class SatelliteClientTestCase(TestCase):
    def setUp(self):
        pass
