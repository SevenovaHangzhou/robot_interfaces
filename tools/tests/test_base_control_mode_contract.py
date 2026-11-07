"""Base CSV/CSP switching: one mode service, one wheel axis set, distinct mode values."""

from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
WHEELS = [f"steer{i}_joint" for i in range(1, 5)] + [f"wheel{i}_joint" for i in range(1, 5)]


class BaseControlModeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load((ROOT / "contract/endpoints.yaml").read_text(encoding="utf-8"))
        cls.endpoints = {entry["id"]: entry for entry in cls.contract["endpoints"]}

    def test_wheel_axis_set_lists_steering_then_drive_wheels(self):
        axes = self.contract["axis_sets"]["v3_swerve_wheels"]
        self.assertEqual(axes["joint_names"], WHEELS)
        self.assertEqual(axes["count"], 8)
        self.assertEqual((axes["position_unit"], axes["velocity_unit"]), ("rad", "rad/s"))

    def test_base_mode_service_and_wheel_trajectory_entries(self):
        expected = {
            "R-IN-23": ("/rt/base/set_control_mode", "robot_rt_control_interfaces/srv/SetJointControlMode"),
            "R-IN-24": ("/rt/base/follow_joint_trajectory", "control_msgs/action/FollowJointTrajectory"),
            "R-IN-25": ("/rt/base/joint_trajectory", "trajectory_msgs/msg/JointTrajectory"),
        }
        for identifier, (name, type_name) in expected.items():
            entry = self.endpoints[identifier]
            self.assertEqual((entry["ros_name"], entry["type"]), (name, type_name))
        for identifier in ("R-IN-24", "R-IN-25"):
            self.assertEqual(self.endpoints[identifier]["axis_set"], "v3_swerve_wheels")

    def test_mode_values_are_distinct_and_velocity_ready_exists(self):
        text = (ROOT / "robot_rt_control_interfaces/msg/JointControlMode.msg").read_text()
        values = dict(re.findall(r"^uint8 ([A-Z_]+)=(\d+)$", text, re.M))
        self.assertIn("VELOCITY_READY", values)
        self.assertEqual(len(set(values.values())), len(values))


if __name__ == "__main__":
    unittest.main()
