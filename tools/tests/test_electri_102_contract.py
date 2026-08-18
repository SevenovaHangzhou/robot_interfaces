"""ELECTRI-102 rolling joint public-contract tests."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RT_PACKAGE = ROOT / "robot_rt_control_interfaces"


def schema(relative_path: str) -> str:
    return (RT_PACKAGE / relative_path).read_text(encoding="utf-8")


def constants(relative_path: str) -> dict[str, int]:
    return {
        name: int(value)
        for name, value in re.findall(
            r"^uint8\s+([A-Z][A-Z0-9_]*)=(\d+)\s*$",
            schema(relative_path),
            flags=re.MULTILINE,
        )
    }


class RollingSchemaTest(unittest.TestCase):
    def test_required_interface_files_exist(self) -> None:
        expected = {
            "msg/JointControlMode.msg",
            "msg/RollingJointPoint.msg",
            "msg/RollingJointTargetBatch.msg",
            "msg/RollingJointControlState.msg",
            "msg/RollingLimitsSource.msg",
            "msg/RollingRejectCode.msg",
            "msg/RollingServiceResult.msg",
            "msg/RollingSessionState.msg",
            "msg/RollingStopReason.msg",
            "srv/CloseRollingJointSession.srv",
            "srv/OpenRollingJointSession.srv",
            "srv/SetJointControlMode.srv",
        }

        missing = sorted(path for path in expected if not (RT_PACKAGE / path).is_file())

        self.assertEqual(missing, [])

    def test_point_and_batch_are_fixed_and_bounded(self) -> None:
        point = schema("msg/RollingJointPoint.msg")
        batch = schema("msg/RollingJointTargetBatch.msg")

        self.assertIn("float64[14] positions", point)
        self.assertIn("float64[14] velocities", point)
        self.assertIn(
            "RollingJointPoint[<=256] points",
            batch,
        )
        self.assertNotIn("std_msgs/Header", batch)

    def test_reject_and_stop_codes_are_independent_and_stable(self) -> None:
        reject = constants("msg/RollingRejectCode.msg")
        stop = constants("msg/RollingStopReason.msg")

        self.assertEqual(
            reject,
            {
                "NONE": 0,
                "WRONG_PROTOCOL": 1,
                "WRONG_BOOT": 2,
                "WRONG_SESSION": 3,
                "WRONG_CLIENT": 4,
                "STALE_SEQUENCE": 5,
                "INVALID_SHAPE": 6,
                "NON_FINITE": 7,
                "NON_MONOTONIC_TIME": 8,
                "LATE_REPLACE": 9,
                "TIME_GAP": 10,
                "CAPACITY_EXCEEDED": 11,
                "INSUFFICIENT_HORIZON": 12,
                "POSITION_DISCONTINUITY": 13,
                "VELOCITY_DISCONTINUITY": 14,
                "POSITION_LIMIT": 15,
                "VELOCITY_LIMIT": 16,
                "ACCELERATION_LIMIT": 17,
                "NOT_STOPPING_VIABLE": 18,
                "SESSION_NOT_ACCEPTING": 19,
                "HORIZON_EXCEEDED": 20,
            },
        )
        self.assertEqual(
            stop,
            {
                "NONE": 0,
                "GRACEFUL_CLOSE": 1,
                "PRIME_TIMEOUT": 2,
                "UPDATE_TIMEOUT": 3,
                "LOW_WATER": 4,
                "CLOCK_ANOMALY": 5,
                "INTERNAL_INVARIANT": 6,
                "CONTROLLER_DEACTIVATED": 7,
                "DISABLE": 8,
                "GROUP_FAULT": 9,
                "CONTROLLER_RESTART": 10,
            },
        )

    def test_limits_source_has_distinct_provisional_value(self) -> None:
        self.assertEqual(
            constants("msg/RollingLimitsSource.msg"),
            {
                "UNSPECIFIED": 0,
                "PRODUCTION": 1,
                "TEST_ONLY": 2,
                "PROVISIONAL": 3,
            },
        )

    def test_close_operation_is_explicit(self) -> None:
        close_service = schema("srv/CloseRollingJointSession.srv")

        self.assertIn("uint8 REQUEST_STOP=1", close_service)
        self.assertIn("uint8 FINALIZE=2", close_service)
        self.assertIn("uint8 operation", close_service)

    def test_services_carry_typed_result_and_error_info(self) -> None:
        for relative_path in (
            "srv/SetJointControlMode.srv",
            "srv/OpenRollingJointSession.srv",
            "srv/CloseRollingJointSession.srv",
        ):
            service = schema(relative_path)
            self.assertIn("RollingServiceResult result", service)
            self.assertIn("robot_system_interfaces/ErrorInfo error", service)


class RollingEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = yaml.safe_load(
            (ROOT / "contract/endpoints.yaml").read_text(encoding="utf-8")
        )

    def test_five_rolling_endpoints_are_registered(self) -> None:
        endpoints = {
            entry["id"]: entry for entry in self.document["endpoints"]
        }
        expected = {
            "R-IN-06": (
                "/rt/joint_control/set_mode",
                "robot_rt_control_interfaces/srv/SetJointControlMode",
                "Q_DEFAULT",
            ),
            "R-IN-07": (
                "/rt/rolling_joint_control/open",
                "robot_rt_control_interfaces/srv/OpenRollingJointSession",
                "Q_DEFAULT",
            ),
            "R-IN-08": (
                "/rt/rolling_joint_control/update",
                "robot_rt_control_interfaces/msg/RollingJointTargetBatch",
                "Q_ROLLING_COMMAND",
            ),
            "R-IN-09": (
                "/rt/rolling_joint_control/close",
                "robot_rt_control_interfaces/srv/CloseRollingJointSession",
                "Q_DEFAULT",
            ),
            "R-OUT-07": (
                "/rt/rolling_joint_control/state",
                "robot_rt_control_interfaces/msg/RollingJointControlState",
                "Q_ROLLING_STATE",
            ),
        }

        for endpoint_id, (name, type_name, qos) in expected.items():
            endpoint = endpoints[endpoint_id]
            self.assertEqual(endpoint["ros_name"], name)
            self.assertEqual(endpoint["type"], type_name)
            self.assertEqual(endpoint["qos"], qos)
            self.assertEqual(endpoint["producer"], "rt_control")
            self.assertEqual(endpoint["consumers"], ["motion"])

    def test_named_qos_profiles_are_registered(self) -> None:
        self.assertIn("Q_ROLLING_COMMAND", self.document["qos_profiles"])
        self.assertIn("Q_ROLLING_STATE", self.document["qos_profiles"])


class RollingQosSourceTest(unittest.TestCase):
    def test_cpp_and_python_expose_both_profiles(self) -> None:
        cpp = (ROOT / "qos/include/robot_interfaces_qos/profiles.hpp").read_text(
            encoding="utf-8"
        )
        python = (ROOT / "qos/robot_interfaces_qos/__init__.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("inline rclcpp::QoS rolling_command()", cpp)
        self.assertIn("inline rclcpp::QoS rolling_state()", cpp)
        self.assertIn("def rolling_command() -> QoSProfile:", python)
        self.assertIn("def rolling_state() -> QoSProfile:", python)


if __name__ == "__main__":
    unittest.main()
