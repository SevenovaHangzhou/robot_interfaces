from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from tools import contract_gate


class ContractGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = yaml.safe_load(
            Path("contract/endpoints.yaml").read_text(encoding="utf-8")
        )

    def test_repository_contract_is_valid(self) -> None:
        self.assertEqual(contract_gate.validate(self.document), [])

    def test_rejects_type_owned_by_another_domain(self) -> None:
        document = copy.deepcopy(self.document)
        endpoint = next(e for e in document["endpoints"] if e["id"] == "N-01")
        endpoint["type"] = "robot_autonomy_interfaces/action/ExecuteDemoTask"

        findings = contract_gate.validate(document)

        self.assertTrue(
            any("自定义 IDL 必须放在提供方域包中" in f for f in findings),
            findings,
        )

    def test_rejects_unregistered_interface_package(self) -> None:
        document = copy.deepcopy(self.document)
        del document["package_owners"]["robot_motion_interfaces"]

        findings = contract_gate.validate(document)

        self.assertIn(
            "robot_motion_interfaces: 未在 package_owners 声明归属",
            findings,
        )

    def test_rejects_capability_name_for_domain_package(self) -> None:
        document = copy.deepcopy(self.document)
        del document["package_owners"]["robot_motion_interfaces"]
        document["package_owners"]["robot_navigation_interfaces"] = "motion"

        findings = contract_gate.validate(document)

        self.assertIn(
            "package_owners: robot_navigation_interfaces 归属 'motion'，"
            "域包必须命名为 robot_motion_interfaces",
            findings,
        )

    def test_motion_stage_contract_replaces_legacy_motion_actions(self) -> None:
        endpoints = {
            endpoint["id"]: endpoint for endpoint in self.document["endpoints"]
        }
        motion_stage = endpoints["M-08"]

        self.assertEqual(motion_stage["ros_name"], "/motion/execute_stage")
        self.assertEqual(
            motion_stage["type"],
            "robot_motion_interfaces/action/ExecuteMotionStage",
        )
        self.assertEqual(motion_stage["producer"], "motion")
        self.assertEqual(motion_stage["consumers"], ["autonomy"])
        self.assertIn("TURN/CAMERA_VIEW/NAMED_JOINT_POSE", motion_stage["constraint"])
        self.assertIn("PREGRASP→APPROACH→PLACE→HOME", motion_stage["constraint"])

        schema = Path(
            "robot_motion_interfaces/action/ExecuteMotionStage.action"
        ).read_text(encoding="utf-8")
        for declaration in (
            "uint8 EXECUTION_STAGE_TURN=6",
            "uint8 EXECUTION_STAGE_NAMED_JOINT_POSE=7",
            "uint8 NAMED_JOINT_POSE_REMOTE_CAMERA_VIEW=1",
            "uint8 NAMED_JOINT_POSE_ARM_CONVERGED=2",
            "float64 turn_target_rad",
            "uint8 named_joint_pose",
        ):
            self.assertIn(declaration, schema)
        self.assertIn("Turn 与 Updown 均保持当前位置", schema)

        vacuum_valves = endpoints["R-IN-05"]
        self.assertEqual(vacuum_valves["ros_name"], "/vacuum/valves/set")
        self.assertEqual(
            vacuum_valves["type"],
            "robot_rt_control_interfaces/action/SetVacuumValves",
        )
        self.assertEqual(vacuum_valves["consumers"], ["motion"])
        self.assertIn(
            {"from": "autonomy", "to": "/vacuum/valves/set"},
            self.document["forbidden_edges"],
        )

        removed_endpoints = set(self.document["removed_endpoints"])
        self.assertTrue(
            {
                "/motion/move_to_camera_view_pose",
                "/motion/plan_and_execute_pick",
                "/motion/plan_and_execute_place",
                "/vacuum/grip",
            }.issubset(removed_endpoints)
        )

    def test_rt_v3_contract_replaces_legacy_writers_and_preserves_component_parallelism(self) -> None:
        endpoints = {
            endpoint["id"]: endpoint for endpoint in self.document["endpoints"]
        }

        self.assertEqual(endpoints["N-04"]["ros_name"], "/cmd_vel")
        self.assertEqual(endpoints["R-IN-04"]["consumers"], ["autonomy"])
        self.assertEqual(endpoints["R-OUT-05"]["consumers"], ["motion", "autonomy"])
        self.assertEqual(
            endpoints["R-IN-16"]["type"],
            "robot_rt_control_interfaces/action/MoveHead",
        )
        self.assertIn("不形成", endpoints["R-OUT-25"]["constraint"])

        removed = set(self.document["removed_endpoints"])
        self.assertTrue(
            {
                "/cmd_vel_safe",
                "/vacuum/grip",
                "/head_position_controller/commands",
                "/led0/color",
            }.issubset(removed)
        )

        valve_schema = Path(
            "robot_rt_control_interfaces/action/SetVacuumValves.action"
        ).read_text(encoding="utf-8")
        for declaration in (
            "unique_identifier_msgs/UUID request_id",
            "string[<=2] channels",
            "OutputCommandResult[<=2] channel_results",
            "VacuumChannelState[<=2] channels",
        ):
            self.assertIn(declaration, valve_schema)

        vacuum_state = Path(
            "robot_rt_control_interfaces/msg/VacuumChannelState.msg"
        ).read_text(encoding="utf-8")
        for declaration in (
            "float64 pressure_kpa",
            "ObservationMeta pressure_observation",
            "uint8 vacuum_state",
            "OutputState valve",
            "bool last_request_known",
        ):
            self.assertIn(declaration, vacuum_state)

    def test_mapping_turn_state_contract_is_registered_and_transactional(self) -> None:
        endpoints = {
            endpoint["id"]: endpoint for endpoint in self.document["endpoints"]
        }
        endpoint = endpoints["N-17"]

        self.assertEqual(
            endpoint["ros_name"], "/navigation/mapping/set_turn_state"
        )
        self.assertEqual(
            endpoint["type"],
            "robot_motion_interfaces/srv/SetMappingTurnState",
        )
        self.assertEqual(endpoint["producer"], "motion")
        self.assertEqual(endpoint["consumers"], ["autonomy", "external"])
        self.assertIn("BEGIN_TURN", endpoint["constraint"])
        self.assertIn("TURN_COMPLETE", endpoint["constraint"])
        self.assertIn("连续稳定", endpoint["constraint"])

        schema = Path(
            "robot_motion_interfaces/srv/SetMappingTurnState.srv"
        ).read_text(encoding="utf-8")
        for declaration in (
            "uint8 BEGIN_TURN=1",
            "uint8 TURN_COMPLETE=2",
            "uint64 turn_sequence",
            "string caller_id",
            "uint8 STATE_RESUME_PENDING=3",
            "uint64 applied_turn_sequence",
            "builtin_interfaces/Time effective_stamp",
            "robot_system_interfaces/ErrorInfo error",
        ):
            self.assertIn(declaration, schema)

    def test_error_info_is_the_cross_domain_uint32_dree_envelope(self) -> None:
        schema = Path("robot_system_interfaces/msg/ErrorInfo.msg").read_text(
            encoding="utf-8"
        )

        self.assertIn("# Cross-domain error envelope.", schema)
        self.assertIn("uint32 code", schema)
        self.assertNotIn("string code", schema)
        self.assertIn("canonical DREE", schema)
        self.assertIn("domain-private", schema)
        self.assertIn("retryable MUST match the R digit", schema)

    def test_domain_readiness_freezes_shared_consistency_rules(self) -> None:
        schema = Path(
            "robot_system_interfaces/msg/DomainReadiness.msg"
        ).read_text(encoding="utf-8")

        required_rules = (
            "ready is the sole capability-admission verdict",
            "HEALTHY requires ready=true and empty blockers/errors",
            "DEGRADED requires ready=true",
            "error MUST have WARN severity",
            "UNAVAILABLE requires ready=false",
            "non-SUCCESS canonical DREE code",
            "NOT have OK severity",
            "map_version MUST be empty when readiness does not depend on a map",
            "producer_instance_id MUST remain stable for one process lifetime",
        )
        for rule in required_rules:
            self.assertIn(rule, schema)


if __name__ == "__main__":
    unittest.main()
