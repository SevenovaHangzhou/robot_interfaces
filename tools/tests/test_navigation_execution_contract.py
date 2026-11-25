"""Freeze published navigation indexes and exercise registry acceptance behavior."""

from pathlib import Path
import re
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from navigation_execution_contract import decode_snapshot


class NavigationExecutionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        contract = yaml.safe_load((ROOT / "contract/endpoints.yaml").read_text())
        cls.endpoints = {entry["id"]: entry for entry in contract["endpoints"]}
        cls.policy = contract["navigation_execution_v1"]
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
                    self.assertEqual(entry["producer"], "navigation")
                    self.assertEqual(entry["consumers"], ["rt_control"])
                    self.assertEqual(entry["qos"], "Q_CONTROL")
                    self.assertEqual(entry["watchdog_ms"], 300)
                else:
                    self.assertEqual(entry["producer"], "rt_control")
                    self.assertEqual(entry["consumers"], ["navigation", "autonomy"])
                    self.assertEqual(entry["qos"], "Q_CONTROL" if identifier == "R-OUT-30" else "Q_FAST_STATE")
                    self.assertEqual(entry["max_age_ms"], {
                        "R-OUT-30": 300, "R-OUT-31": 100, "R-OUT-31C": 100,
                        "R-OUT-32": 200,
                    }[identifier])

    def test_fixed_header_and_module_indexes(self):
        rows = re.findall(r"^\| (\d+) \| ([a-z_]+) \|", self.schema, re.M)
        header = [
            "schema_version", "snapshot_ros_time", "sequence", "ready", "status",
            "gated", "waiting_for_alignment", "translation_branch", "reference_vx",
            "reference_vy", "reference_wz", "reference_ax", "reference_ay",
            "reference_alpha", "measured_vx", "measured_vy", "measured_wz",
            "max_steering_rate", "max_steering_acceleration", "max_steering_jerk",
            "max_translation_acceleration", "max_body_jerk", "max_wheel_acceleration",
            "max_wheel_speed", "gate", "release", "flip_hysteresis",
        ]
        module = [
            "module_id", "actual_heading", "actual_wheel_speed", "reference_heading",
            "reference_heading_rate", "reference_heading_acceleration",
            "reference_wheel_speed", "reversed", "holding", "final_heading_target",
            "heading_error", "effective_heading_min", "effective_heading_max",
            "wheel_radius", "module_x", "module_y",
        ]
        self.assertEqual(rows, [(str(i), name) for i, name in enumerate(header)] +
                         [(str(i), name) for i, name in enumerate(module)])
        self.assertEqual(len(header) + 4 * len(module), 91)
        self.assertEqual(self.policy["header"], header)
        self.assertEqual(self.policy["module"], module)
        self.assertEqual(self.policy["size"], 91)

    def snapshot(self):
        # Deliberately synthetic state; no claim of hardware or predictor proof.
        data = [0.0] * 91
        data[:8] = [1, 10, 2, 1, 1, 0, 0, -1]
        for identity, start in enumerate((27, 43, 59, 75), 1):
            data[start] = identity
            data[start + 1] = identity / 10
            data[start + 8] = identity % 2
            data[start + 9] = identity / 5
        return data

    def test_identity_reordering_and_internal_state_preservation(self):
        data = self.snapshot()
        header, modules = decode_snapshot(data, self.policy, 10.05, 9.9)
        self.assertEqual(header["translation_branch"], -1)
        self.assertEqual(modules[1]["holding"], 1)
        self.assertNotEqual(modules[1]["final_heading_target"], modules[1]["reference_heading"])
        reordered = data[:27] + data[75:91] + data[59:75] + data[43:59] + data[27:43]
        self.assertEqual(decode_snapshot(reordered, self.policy, 10.05), (header, modules))

    def test_invalid_wire_values_and_ready_policy(self):
        for index, value in ((0, 2), (2, -1), (2, 1.5), (3, 0), (3, 2),
                             (4, 0), (4, 4), (5, 2), (7, 2), (27, 2),
                             (27, 1.5), (43, 5), (34, -1), (35, 2)):
            with self.subTest(index=index, value=value):
                data = self.snapshot()
                data[index] = value
                with self.assertRaises(ValueError):
                    decode_snapshot(data, self.policy, 10.05)
        for index in range(91):
            for invalid in (float("nan"), float("inf"), -float("inf")):
                data = self.snapshot()
                data[index] = invalid
                with self.assertRaises(ValueError):
                    decode_snapshot(data, self.policy, 10.05)
        for status in (1, 2, 3):
            data = self.snapshot()
            data[4] = status
            self.assertEqual(decode_snapshot(data, self.policy, 10.05)[0]["status"], status)

    def test_timestamp_length_and_effective_configuration(self):
        data = self.snapshot()
        for now in (10.101, 9.989):
            with self.assertRaises(ValueError):
                decode_snapshot(data, self.policy, now)
        for previous in (10, 10.01):
            with self.assertRaises(ValueError):
                decode_snapshot(data, self.policy, 10.05, previous)
        for malformed in (data[:-1], data + [0]):
            with self.assertRaises(ValueError):
                decode_snapshot(malformed, self.policy, 10.05)
        for index in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 38, 39, 40, 41, 42):
            expected = {index: data[index]}
            decode_snapshot(data, self.policy, 10.05, expected_fields=expected)
            changed = data.copy()
            changed[index] += 0.001
            with self.assertRaises(ValueError):
                decode_snapshot(changed, self.policy, 10.05, expected_fields=expected)

    def test_observation_provenance_policy(self):
        self.assertEqual(self.policy["observed_steering_rate"], {
            "minimum_actual_samples": 2,
            "provenance": ["hardware_sequence_and_sample_time", "host_receive_age_fall"],
            "require_advancing_observation_time": True,
            "host_observer_hz": 1000,
            "host_sync_period_ms": 4,
            "host_receive_age_strict_fall": True,
            "ambiguous_continuity_resets_history": True,
            "device_timestamp_claimed_for_host_observer": False,
            "invalid_value": "NaN",
            "zero_fallback": False,
        })
        self.assertEqual(self.policy["max_age_ms"], 100)
        self.assertEqual(self.policy["max_future_ms"], 10)
        self.assertTrue(self.policy["stamp_must_advance"])
        self.assertEqual(self.policy["configuration_absolute_tolerance"], 1e-5)

    def test_existing_observation_identity_is_unchanged(self):
        entry = self.endpoints["R-OUT-29"]
        self.assertEqual(entry["ros_name"], "/rt/base/wheel_observations")
        self.assertEqual(entry["type"], "robot_rt_control_interfaces/msg/WheelObservationArray")
        self.assertIn("FL/FR/RL/RR", entry["constraint"])
        self.assertEqual(self.endpoints["N-04"]["watchdog_ms"], 500)
        self.assertEqual(self.endpoints["R-OUT-02"]["rate_hz"], [50, 50])


if __name__ == "__main__":
    unittest.main()
