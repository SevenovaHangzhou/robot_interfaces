"""Navigation type ownership, including endpoints whose ROS name is outside /navigation/."""
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class NavigationInterfaceTests(unittest.TestCase):
    def test_navigation_owns_its_ros_types_and_transport_endpoints(self):
        registry = yaml.safe_load((ROOT / 'contract/endpoints.yaml').read_text())
        self.assertEqual(registry['package_owners']['robot_navigation_interfaces'], 'navigation')
        for endpoint in registry['endpoints']:
            if endpoint['id'].startswith(('N-', 'P-NAV-')):
                with self.subTest(endpoint=endpoint['id']):
                    self.assertEqual(endpoint['producer'], 'navigation')
                    if endpoint['type'].startswith('robot_') and endpoint['id'] != 'N-06':
                        self.assertTrue(endpoint['type'].startswith('robot_navigation_interfaces/'))

    def test_navigation_types_do_not_also_exist_in_motion(self):
        navigation = ROOT / 'robot_navigation_interfaces'
        for kind in ('action', 'srv', 'msg'):
            for idl in (navigation / kind).glob('*.' + kind):
                with self.subTest(idl=idl.name):
                    self.assertFalse((ROOT / 'robot_motion_interfaces' / kind / idl.name).exists())
                    self.assertNotIn('robot_motion_interfaces/', idl.read_text())
