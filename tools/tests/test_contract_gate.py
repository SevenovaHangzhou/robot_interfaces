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


if __name__ == "__main__":
    unittest.main()
