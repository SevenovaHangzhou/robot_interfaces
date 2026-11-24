"""Freeze navigation v1 endpoint metadata and its documented fixed-index schema."""

from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class NavigationExecutionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        contract = yaml.safe_load((ROOT / "contract/endpoints.yaml").read_text())
        cls.endpoints = {entry["id"]: entry for entry in contract["endpoints"]}
        cls.schema = (ROOT / "contract/navigation-execution-v1.md").read_text()

    def test_standard_external_types_and_rates(self):
        expected = {
            "N-07": ("/rt/base/terminal_rotation_request", "std_msgs/msg/Bool", 50),
            "R-OUT-30": ("/rt/base/terminal_rotation_active", "std_msgs/msg/Bool", 50),
            "R-OUT-31": ("/rt/base/execution_state", "std_msgs/msg/Float64MultiArray", 100),
            "R-OUT-31C": ("/rt_control/chassis/execution_state", "std_msgs/msg/Float64MultiArray", 100),
            "R-OUT-32": ("/rt_control/chassis/joint_states", "sensor_msgs/msg/JointState", 100),
        }
        for identifier, (name, wire_type, rate) in expected.items():
            with self.subTest(endpoint=identifier):
                entry = self.endpoints[identifier]
                self.assertEqual(entry["ros_name"], name)
                self.assertEqual(entry["type"], wire_type)
                self.assertTrue(entry["external_type"])
                self.assertEqual(entry["kind"], "topic")
                self.assertEqual(entry["rate_hz"], [rate, rate])
                if identifier == "N-07":
                    self.assertEqual(entry["producer"], "motion")
                    self.assertEqual(entry["consumers"], ["rt_control"])
                    self.assertEqual(entry["qos"], "Q_CONTROL")
                    self.assertEqual(entry["watchdog_ms"], 300)
                else:
                    self.assertEqual(entry["producer"], "rt_control")
                    self.assertEqual(entry["consumers"], ["motion", "autonomy"])
                    self.assertEqual(entry["qos"], "Q_FAST_STATE")
                    self.assertEqual(entry["max_age_ms"], 300)

    def test_fixed_header_and_module_indexes(self):
        rows = re.findall(r"^\| (\d+) \| ([a-z_]+) \|", self.schema, re.M)
        header = [
            "schema_version", "sequence", "snapshot_ros_time", "ready", "status",
            "gated", "waiting_for_alignment", "terminal_rotation_active",
            "terminal_request_fresh", "reference_vx", "reference_vy", "reference_wz",
            "reference_ax", "reference_ay", "reference_alpha", "measured_vx",
            "measured_vy", "measured_wz", "max_translation_speed", "max_yaw_speed",
            "max_translation_acceleration", "max_yaw_acceleration", "max_steering_rate",
            "max_steering_acceleration", "max_steering_jerk", "max_wheel_speed",
            "max_wheel_acceleration", "max_body_jerk", "enabled", "feedback_valid",
            "command_fresh",
        ]
        module = [
            "actual_heading", "actual_wheel_speed", "reference_heading",
            "reference_heading_rate", "reference_heading_acceleration",
            "final_heading_target", "heading_error", "branch", "effective_heading_min",
            "effective_heading_max", "wheel_radius", "module_x", "module_y",
            "feedback_valid", "reference_wheel_speed",
        ]
        self.assertEqual(rows, [(str(i), name) for i, name in enumerate(header)] +
                         [(str(i), name) for i, name in enumerate(module)])
        self.assertEqual(len(header) + 4 * len(module), 91)
        for text in ('label="rt_base_execution_state_v1"', "size=91", "stride=91",
                     "layout.data_offset=0", "quiet NaN", "age >300 ms", "θ=-q",
                     "physical wiring", "module1..4", "0=inactive", "7=steering_hold_fault"):
            self.assertIn(text, self.schema)

    def test_normalized_joint_state_and_execution_semantics(self):
        names = [f"module_{module}_{kind}" for module in range(1, 5)
                 for kind in ("steering", "wheel")]
        constraint = self.endpoints["R-OUT-32"]["constraint"]
        self.assertIn("[" + ", ".join(names) + "]", constraint)
        self.assertNotIn("steer1_joint", constraint)
        self.assertIn("steering velocity NaN", constraint)
        for name in names:
            self.assertIn(name, self.schema)
        for text in ("next core tick", "not terminal-only", "(vx, vy, wz*R)",
                     "infinity are NaN on the wire", "Steering velocities are NaN"):
            self.assertIn(text, self.schema)

    def test_existing_observation_identity_is_unchanged(self):
        entry = self.endpoints["R-OUT-29"]
        self.assertEqual(entry["ros_name"], "/rt/base/wheel_observations")
        self.assertEqual(entry["type"], "robot_rt_control_interfaces/msg/WheelObservationArray")
        self.assertIn("FL/FR/RL/RR", entry["constraint"])
        self.assertEqual(self.endpoints["N-04"]["watchdog_ms"], 500)
        self.assertEqual(self.endpoints["R-OUT-02"]["rate_hz"], [50, 50])


if __name__ == "__main__":
    unittest.main()
