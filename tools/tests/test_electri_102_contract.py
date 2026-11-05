"""ELECTRI-102 rolling joint public-contract tests."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RT_PACKAGE = ROOT / "robot_rt_control_interfaces"
MOTION_PACKAGE = ROOT / "robot_motion_interfaces"


def schema(relative_path: str) -> str:
    return (RT_PACKAGE / relative_path).read_text(encoding="utf-8")


def motion_schema(relative_path: str) -> str:
    return (MOTION_PACKAGE / relative_path).read_text(encoding="utf-8")


def constants(relative_path: str) -> dict[str, int]:
    return {
        name: int(value)
        for name, value in re.findall(
            r"^uint8\s+([A-Z][A-Z0-9_]*)=(\d+)\s*$",
            schema(relative_path),
            flags=re.MULTILINE,
        )
    }


def fields(text: str) -> list[str]:
    return [
        line for line in text.splitlines()
        if line and not line.startswith("#") and line != "---"
        and not re.match(r"^\w+ [A-Z][A-Z0-9_]*=", line)
    ]


class RollingSchemaTest(unittest.TestCase):
    def test_session_services_and_protocol_identity_are_gone(self) -> None:
        for name in (
            "msg/RollingLimitsSource.msg",
            "msg/RollingRejectCode.msg",
            "msg/RollingServiceResult.msg",
            "msg/RollingSessionState.msg",
            "msg/RollingStopReason.msg",
            "srv/CloseRollingJointSession.srv",
            "srv/OpenRollingJointSession.srv",
        ):
            self.assertFalse((RT_PACKAGE / name).exists(), name)

    def test_batch_and_point_carry_only_timing_and_targets(self) -> None:
        self.assertEqual(
            fields(motion_schema("msg/RollingJointTargetBatch.msg")),
            [
                "uint32 epoch",
                "uint64 sequence",
                "builtin_interfaces/Time replace_from",
                "RollingJointPoint[<=256] points",
            ],
        )
        self.assertEqual(
            fields(motion_schema("msg/RollingJointPoint.msg")),
            [
                "builtin_interfaces/Duration time_from_start",
                "float64[14] positions",
                "float64[14] velocities",
            ],
        )

    def test_state_has_five_fields_and_distinct_codes(self) -> None:
        state = schema("msg/RollingJointControlState.msg")
        self.assertEqual(
            fields(state),
            [
                "uint32 epoch",
                "uint8 state",
                "uint64 last_sequence",
                "uint8 last_result",
                "uint8 stop_reason",
            ],
        )
        codes = constants("msg/RollingJointControlState.msg")
        states = [codes[name] for name in ("HOLDING", "RUNNING", "STOPPING")]
        results = [value for name, value in codes.items() if name not in (
            "HOLDING", "RUNNING", "STOPPING") and not name.startswith("STOP_")]
        stops = [value for name, value in codes.items() if name.startswith("STOP_")]
        for group in (states, results, stops):
            self.assertEqual(len(group), len(set(group)))
        self.assertEqual(codes["ACCEPTED"], 0)
        self.assertEqual(codes["STOP_NONE"], 0)

    def test_mode_service_takes_only_the_target(self) -> None:
        service = schema("srv/SetJointControlMode.srv")
        request, response = service.split("\n---\n")
        self.assertEqual(fields(request), ["JointControlMode target_mode"])
        self.assertEqual(
            fields(response),
            ["bool accepted", "robot_system_interfaces/ErrorInfo error", "JointControlMode mode"],
        )


class RollingEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = yaml.safe_load(
            (ROOT / "contract/endpoints.yaml").read_text(encoding="utf-8")
        )

    def test_three_rolling_endpoints_are_registered(self) -> None:
        endpoints = {entry["id"]: entry for entry in self.document["endpoints"]}
        expected = {
            "R-IN-06": (
                "/rt/arms/set_control_mode",
                "robot_rt_control_interfaces/srv/SetJointControlMode",
                "Q_DEFAULT",
            ),
            "M-09": (
                "/rt/arms/rolling/target_batch",
                "robot_motion_interfaces/msg/RollingJointTargetBatch",
                "Q_ROLLING_COMMAND",
            ),
            "R-OUT-07": (
                "/rt/arms/rolling/state",
                "robot_rt_control_interfaces/msg/RollingJointControlState",
                "Q_ROLLING_STATE",
            ),
        }
        for endpoint_id, (name, type_name, qos) in expected.items():
            endpoint = endpoints[endpoint_id]
            self.assertEqual(
                (endpoint["ros_name"], endpoint["type"], endpoint["qos"]),
                (name, type_name, qos),
            )
        self.assertNotIn("R-IN-07", endpoints)
        self.assertNotIn("R-IN-09", endpoints)
        removed = self.document["removed_endpoints"]
        self.assertIn("/rt/arms/rolling/open_session", removed)
        self.assertIn("/rt/arms/rolling/close_session", removed)

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

    def test_cpp_and_python_profiles_freeze_the_same_values(self) -> None:
        cpp = (ROOT / "qos/include/robot_interfaces_qos/profiles.hpp").read_text(
            encoding="utf-8"
        )
        python = (ROOT / "qos/robot_interfaces_qos/__init__.py").read_text(
            encoding="utf-8"
        )

        self.assertRegex(
            cpp,
            r"(?s)rolling_command\(\).*?KeepLast\(1\).*?best_effort\(\).*?"
            r"milliseconds\(100\).*?milliseconds\(100\)",
        )
        self.assertRegex(
            cpp,
            r"(?s)rolling_state\(\).*?KeepLast\(5\).*?reliable\(\).*?"
            r"milliseconds\(100\).*?milliseconds\(200\)",
        )
        self.assertRegex(
            python,
            r"(?s)rolling_command\(\).*?depth=1.*?BEST_EFFORT.*?"
            r"100_000_000.*?100_000_000",
        )
        self.assertRegex(
            python,
            r"(?s)rolling_state\(\).*?depth=5.*?RELIABLE.*?"
            r"100_000_000.*?200_000_000",
        )


if __name__ == "__main__":
    unittest.main()
