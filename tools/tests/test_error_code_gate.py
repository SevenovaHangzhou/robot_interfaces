"""error_code_gate 的行为测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import error_code_gate as gate  # noqa: E402


BASE = [("SUCCESS", 0)]


class DecodeTest(unittest.TestCase):
    def test_decodes_domain_recoverable_event(self) -> None:
        self.assertEqual(gate.decode(3140), (3, 1, 4))
        self.assertEqual(gate.decode(1020), (1, 0, 2))
        self.assertEqual(gate.decode(70), (0, 0, 7))

    def test_recovery_bit_is_the_only_difference(self) -> None:
        """同类事件仅恢复位不同，其余位一致。"""
        d0, r0, e0 = gate.decode(1020)
        d1, r1, e1 = gate.decode(1120)
        self.assertEqual((d0, e0), (d1, e1))
        self.assertNotEqual(r0, r1)


class ValidateTest(unittest.TestCase):
    def test_accepts_valid_set(self) -> None:
        consts = BASE + [
            ("TIMEOUT", 2),
            ("RT_DRIVE_FAULT", 1020),
            ("PERC_BOX_NOT_FOUND", 2141),
            ("MOTION_PLANNING_FAILED", 3150),
            ("AUTO_DOMAIN_UNAVAILABLE", 4130),
        ]
        self.assertEqual(gate.validate(consts), [])

    def test_rejects_missing_success(self) -> None:
        findings = gate.validate([("TIMEOUT", 2)])
        self.assertTrue(any("SUCCESS" in f for f in findings))

    def test_rejects_duplicate_value(self) -> None:
        findings = gate.validate(BASE + [("TIMEOUT", 2), ("OTHER", 2)])
        self.assertTrue(any("数值重复" in f for f in findings))

    def test_rejects_duplicate_name(self) -> None:
        findings = gate.validate(BASE + [("TIMEOUT", 2), ("TIMEOUT", 3)])
        self.assertTrue(any("常量名重复" in f for f in findings))

    def test_rejects_recovery_bit_out_of_range(self) -> None:
        # 第 2 位 = 5，非 0/1
        findings = gate.validate(BASE + [("RT_ODD", 1520)])
        self.assertTrue(any("第 2 位" in f for f in findings))

    def test_rejects_undefined_domain(self) -> None:
        findings = gate.validate(BASE + [("X_THING", 7020)])
        self.assertTrue(any("不是已定义的域" in f for f in findings))

    def test_rejects_wrong_domain_prefix(self) -> None:
        # 3xxx 是 Motion 段，却用 PERC_ 前缀
        findings = gate.validate(BASE + [("PERC_WRONG", 3020)])
        self.assertTrue(any("须以 MOTION_ 开头" in f for f in findings))

    def test_rejects_domain_prefix_in_common_segment(self) -> None:
        findings = gate.validate(BASE + [("RT_LEAKED", 20)])
        self.assertTrue(any("不应带域前缀" in f for f in findings))

    def test_rejects_internal_error_marked_recoverable(self) -> None:
        findings = gate.validate(BASE + [("RT_INTERNAL_ERROR", 1190)])
        self.assertTrue(any("不得标为可自主恢复" in f for f in findings))

    def test_rejects_internal_error_outside_9x(self) -> None:
        findings = gate.validate(BASE + [("RT_INTERNAL_ERROR", 1020)])
        self.assertTrue(any("须落在事件分类 9x" in f for f in findings))

    def test_rejects_code_out_of_space(self) -> None:
        findings = gate.validate(BASE + [("RT_HUGE", 99999)])
        self.assertTrue(any("超出" in f for f in findings))

    def test_rejects_oversized_segment(self) -> None:
        consts = BASE + [
            (f"MOTION_THING_{i}", 3000 + i) for i in range(gate.MAX_PER_SEGMENT + 1)
        ]
        findings = gate.validate(consts)
        self.assertTrue(any("超过上限" in f for f in findings))


class RealFileTest(unittest.TestCase):
    def test_shipped_error_code_msg_is_valid(self) -> None:
        path = Path(__file__).resolve().parents[2] / gate.ERROR_CODE
        if not path.is_file():
            self.skipTest(f"{gate.ERROR_CODE} 不在预期位置")
        consts = gate.parse(path.read_text(encoding="utf-8"))
        self.assertEqual(gate.validate(consts), [])
        self.assertIn(("SUCCESS", 0), consts)
        for expected in (
            ("PERC_STANDOFF_TABLE_MISMATCH", 2010),
            ("PERC_CAMERA_FAULT", 2020),
            ("PERC_INCOMPLETE_WALL", 2040),
            ("PERC_INTERNAL_ERROR", 2090),
            ("PERC_CAPTURE_FAILED", 2140),
            ("PERC_BOX_NOT_FOUND", 2141),
            ("PERC_POSE_UNRELIABLE", 2142),
        ):
            self.assertIn(expected, consts)


if __name__ == "__main__":
    unittest.main()
