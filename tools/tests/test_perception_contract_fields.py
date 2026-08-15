"""Perception P-01/P-02 traceability field regression tests."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PerceptionContractFieldsTest(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_p01_carries_task_profile_and_returns_scene(self) -> None:
        action = self._read(
            "robot_perception_interfaces/action/BuildWallTaskPlan.action"
        )
        plan = self._read("robot_perception_interfaces/msg/WallTaskPlan.msg")
        self.assertIn("unique_identifier_msgs/UUID task_id", action)
        self.assertIn("string scene_profile_id", action)
        self.assertIn("unique_identifier_msgs/UUID scene_id", plan)

    def test_p02_carries_scene_arm_and_suction_constraints(self) -> None:
        action = self._read(
            "robot_perception_interfaces/action/RefineSequencePoses.action"
        )
        box = self._read("robot_perception_interfaces/msg/BoxPose.msg")
        self.assertIn("unique_identifier_msgs/UUID expected_scene_id", action)
        self.assertIn("uint8[] arms", action)
        self.assertIn("uint8[] suction_modes", action)
        self.assertIn("uint8 arm", box)
        self.assertIn("uint8 suction_mode", box)


if __name__ == "__main__":
    unittest.main()
