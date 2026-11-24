"""WallBox 的三种中心各自带时间戳、各自有效。"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ThreeCenterWallBox(unittest.TestCase):
    def test_each_center_is_stamped_and_independently_valid(self):
        text = (ROOT / 'robot_perception_interfaces/msg/WallBox.msg').read_text()
        for center in ('face', 'top', 'box'):
            self.assertIn(f'geometry_msgs/PoseStamped {center}_center_pose\n', text)
            self.assertIn(f'bool {center}_center_pose_valid\n', text)

    def test_map_reference_layout_is_preserved(self):
        text = (ROOT / 'robot_perception_interfaces/msg/WallMapReference.msg').read_text()
        fields = [line for line in text.splitlines() if line and not line.startswith('#')]
        self.assertEqual(fields, ['unique_identifier_msgs/UUID producer_instance_id',
                                  'uint64 map_version', 'string navigation_map_version'])


if __name__ == '__main__':
    unittest.main()
