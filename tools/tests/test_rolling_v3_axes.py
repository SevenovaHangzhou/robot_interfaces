"""V3 axis order is a semantic contract, even though the wire arrays stay length 14."""

import copy
from pathlib import Path
import unittest

import yaml

from tools import contract_gate

ROOT = Path(__file__).resolve().parents[2]
NAMES = [f"{side}_joint{i}" for side in ("right", "left") for i in range(1, 8)]


class V3RollingAxesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load((ROOT / "contract/endpoints.yaml").read_text())

    def test_registered_order_and_units(self):
        axes = self.contract["axis_sets"]["v3_dual_arm"]
        self.assertEqual(axes["joint_names"], NAMES)
        self.assertEqual(axes["count"], 14)
        self.assertEqual((axes["position_unit"], axes["velocity_unit"]), ("rad", "rad/s"))

    def test_trajectory_endpoints_reference_the_same_axis_set(self):
        endpoints = {entry["id"]: entry for entry in self.contract["endpoints"]}
        for identifier in ("R-IN-02", "R-IN-22", "M-09"):
            self.assertEqual(endpoints[identifier]["axis_set"], "v3_dual_arm")

    def test_gate_rejects_unknown_axis_reference(self):
        document = copy.deepcopy(self.contract)
        endpoint = next(entry for entry in document["endpoints"] if entry["id"] == "M-09")
        endpoint["axis_set"] = "missing"
        self.assertTrue(any("unknown axis_set" in finding
                            for finding in contract_gate.validate(document)))

    def test_gate_rejects_duplicate_axis_names(self):
        document = copy.deepcopy(self.contract)
        document["axis_sets"]["v3_dual_arm"]["joint_names"][-1] = "right_joint1"
        self.assertTrue(any("duplicate names" in finding
                            for finding in contract_gate.validate(document)))

    def test_old_business_interfaces_are_explicitly_legacy(self):
        entries = {entry["id"]: entry for entry in self.contract["endpoints"]}
        for identifier in ("G-01", "P-01", "P-02", "M-08", "N-17"):
            self.assertTrue(entries[identifier]["legacy_only"])
            self.assertIn("V2", entries[identifier]["note"])
        task = (ROOT / "robot_autonomy_interfaces/action/ExecuteDemoTask.action").read_text()
        self.assertIn("V3", task)
        self.assertNotIn("# 但不直接控制 RT-Control。", task)


if __name__ == "__main__":
    unittest.main()
