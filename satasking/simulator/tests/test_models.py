from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from simulator.models import GroundStation, Satellite


class GroundStationModelTestCase(TestCase):
    def setUp(self):
        settings.SERVER = None

    def test_run_sets_running_true(self):
        """Check that run() method sets the inner running variable."""
        gs = GroundStation.objects.create()
        self.assertEqual(gs.running, False)
        with patch('simulator.models.GroundStationServer') as gs_mock:
            with patch('simulator.models.threading') as th_mock:
                gs.run()
        self.assertEqual(gs.running, True)

    def test_run_sets_settings_server(self):
        """Check that run() method sets the SERVER variable (in settings.py)."""
        gs = GroundStation.objects.create()
        self.assertIsNone(settings.SERVER)
        with patch('simulator.models.GroundStationServer') as gs_mock:
            with patch('simulator.models.threading') as th_mock:
                gs.run()
        self.assertIsNotNone(settings.SERVER)

    def test_run_cant_run_twice(self):
        """Check that if a server is currenctly running, then you cant run other instance."""
        gs = GroundStation.objects.create()
        self.assertIsNone(settings.SERVER)  # Ensure that no other server is running
        with patch('simulator.models.GroundStationServer') as gs_mock:
            with patch('simulator.models.threading') as th_mock:
                gs.run()
        self.assertEqual(gs.running, True)
        # Run again
        with patch('simulator.models.GroundStationServer') as gs_mock:
            with patch('simulator.models.threading') as th_mock:
                gs.run()  # This call should print a log message
                self.assertEqual(th_mock.call_count, 0)  # Here th_mock differs from previous mock

class SatelliteModelTestCase(TestCase):
    def setUp(self):
        settings.SATELLITES = {}

    def test_run_sets_running_true(self):
        """Check that run() method sets the inner running variable."""
        sat = Satellite.objects.create(resources="1", name="Coso")
        self.assertEqual(sat.running, False)
        with patch('simulator.models.SatelliteClient') as sat_mock:
            with patch('simulator.models.threading') as th_mock:
                sat.run()
        self.assertEqual(sat.running, True)

    def test_run_sets_settings_satellite(self):
        """Check that run() method sets the SATELLITES variable (in settings.py)."""
        sat_name = "Coso"
        sat = Satellite.objects.create(resources="1", name=sat_name)
        self.assertEqual(settings.SATELLITES, {})
        with patch('simulator.models.SatelliteClient') as sat_mock:
            with patch('simulator.models.threading') as th_mock:
                sat.run()
        self.assertNotEqual(len(settings.SATELLITES), 0)
        self.assertIn(sat_name, settings.SATELLITES)

    def test_run_cant_run_twice(self):
        """Check that if a satellite is currently running, then you cant run again the same
        instance.
        """
        sat_name = "Coso"
        sat = Satellite.objects.create(resources="1", name=sat_name)
        self.assertEqual(settings.SATELLITES, {})
        with patch('simulator.models.SatelliteClient') as sat_mock:
            with patch('simulator.models.threading') as th_mock:
                sat.run()
        self.assertNotEqual(len(settings.SATELLITES), 0)
        self.assertIn(sat_name, settings.SATELLITES)
        # Run again
        with patch('simulator.models.SatelliteClient') as sat_mock:
            with patch('simulator.models.threading') as th_mock:
                sat.run()  # This call should print a log message
                self.assertEqual(th_mock.call_count, 0)  # Here th_mock differs from previous mock
        self.assertLess(len(settings.SATELLITES), 2)
