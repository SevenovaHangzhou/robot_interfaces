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
        self.assertIn("CAMERA_VIEW 可选", motion_stage["constraint"])

        vacuum_grip = endpoints["R-IN-05"]
        self.assertEqual(vacuum_grip["consumers"], ["autonomy"])
        self.assertIn(
            {"from": "motion", "to": "/vacuum/grip"},
            self.document["forbidden_edges"],
        )

        removed_endpoints = set(self.document["removed_endpoints"])
        self.assertTrue(
            {
                "/motion/move_to_camera_view_pose",
                "/motion/plan_and_execute_pick",
                "/motion/plan_and_execute_place",
            }.issubset(removed_endpoints)
        )

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
