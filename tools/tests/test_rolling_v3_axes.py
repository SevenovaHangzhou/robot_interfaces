"""V3 axis order is a semantic contract, even though the wire arrays stay length 14."""

import copy
import hashlib
from pathlib import Path
import re
import unittest

import yaml

from tools import contract_gate

ROOT = Path(__file__).resolve().parents[2]
NAMES = [f"{side}_joint{i}" for side in ("right", "left") for i in range(1, 8)]
HASH = "f4c8ff8a32183d1733032494600c9f5d1e7e625673a4ad51556b3ac6c35adee4"


class V3RollingAxesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load((ROOT / "contract/endpoints.yaml").read_text())

    def test_registered_order_units_and_canonical_digest(self):
        axes = self.contract["axis_sets"]["v3_dual_arm"]
        self.assertEqual(axes["joint_names"], NAMES)
        self.assertEqual(axes["count"], 14)
        self.assertEqual((axes["position_unit"], axes["velocity_unit"]), ("rad", "rad/s"))
        canonical = "".join(f"{name}:rad:rad/s\n" for name in axes["joint_names"])
        self.assertEqual(hashlib.sha256(canonical.encode("utf-8")).hexdigest(), HASH)
        self.assertEqual(axes["sha256"], HASH)

    def test_point_documents_every_slot_without_mixed_units(self):
        point = (ROOT / "robot_motion_interfaces/msg/RollingJointPoint.msg").read_text()
        listed = re.findall(r"\b(?:right|left)_joint[1-7]\b", point)
        self.assertEqual(listed, NAMES)
        self.assertIn(HASH, point)
        self.assertNotIn("right_joint1..6", point)
        self.assertNotIn("position m, velocity m/s", point)
        fields = [line for line in point.splitlines() if line and not line.startswith("#")]
        self.assertEqual(fields, ["uint64 time_from_session_start_ns",
                                  "float64[14] positions", "float64[14] velocities"])

    def test_fjt_open_update_and_state_reference_the_same_axis_set(self):
        endpoints = {entry["id"]: entry for entry in self.contract["endpoints"]}
        for identifier in ("R-IN-02", "R-IN-07", "M-09", "R-OUT-07"):
            entry = endpoints[identifier]
            self.assertEqual(entry["axis_set"], "v3_dual_arm")
            self.assertIn("right_joint1..7", entry["note"])
            self.assertIn("left_joint1..7", entry["note"])
        self.assertIn("AXIS_SET_MISMATCH", endpoints["R-IN-07"]["constraint"])

    def test_old_same_length_axis_set_is_not_compatible(self):
        old_names = [f"{side}_joint{i}" for side in ("right", "left") for i in range(1, 7)]
        old = "".join(f"{name}:rad:rad/s\n" for name in old_names)
        old += "turn:rad:rad/s\nupdown:m:m/s\n"
        self.assertNotEqual(hashlib.sha256(old.encode()).hexdigest(), HASH)
        for filename in ("srv/OpenRollingJointSession.srv", "msg/RollingJointControlState.msg"):
            text = (ROOT / "robot_rt_control_interfaces" / filename).read_text()
            self.assertIn(HASH, text)
            self.assertIn("right_joint1..7, left_joint1..7", text)

    def test_gate_rejects_axis_order_drift_without_matching_identity(self):
        document = copy.deepcopy(self.contract)
        document["axis_sets"]["v3_dual_arm"]["joint_names"][-1] = "updown"
        self.assertTrue(any("axis_set_hash mismatch" in finding
                            for finding in contract_gate.validate(document)))

    def test_gate_rejects_unknown_axis_reference(self):
        document = copy.deepcopy(self.contract)
        endpoint = next(entry for entry in document["endpoints"] if entry["id"] == "M-09")
        endpoint["axis_set"] = "missing"
        self.assertTrue(any("unknown axis_set" in finding
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
