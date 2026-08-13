"""changelog_gate 的行为测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import changelog_gate as gate  # noqa: E402


HEADER = "## [Unreleased]\n\n"


def entry(
    entry_type: str = "非破坏性",
    title: str = "示例变更",
    interface: str = "`robot_system_interfaces/msg/ErrorInfo`",
    reason: str = "旧字段无法区分 DDS 抖动与进程重启，导致宽限判定错误放行。",
    proposer: str = "@kkozia（system）",
    affected: str = "motion、rt_control",
) -> str:
    lines = [f"### {entry_type}：{title}", ""]
    if interface is not None:
        lines.append(f"- **接口**：{interface}")
    if reason is not None:
        lines.append(f"- **原因**：{reason}")
    if proposer is not None:
        lines.append(f"- **提出人**：{proposer}")
    if affected is not None:
        lines.append(f"- **影响域**：{affected}")
    return HEADER + "\n".join(lines) + "\n"


class ValidateFormatTest(unittest.TestCase):
    def test_accepts_complete_entry(self) -> None:
        self.assertEqual(gate.validate_format(entry()), [])

    def test_rejects_missing_unreleased_section(self) -> None:
        text = entry().replace("## [Unreleased]", "## [0.1.0] - 2026-01-01")
        findings = gate.validate_format(text)
        self.assertTrue(any("Unreleased" in f for f in findings))

    def test_rejects_missing_reason(self) -> None:
        findings = gate.validate_format(entry(reason=None))
        self.assertTrue(any("**原因**" in f for f in findings))

    def test_rejects_missing_proposer(self) -> None:
        findings = gate.validate_format(entry(proposer=None))
        self.assertTrue(any("**提出人**" in f for f in findings))

    def test_rejects_proposer_without_handle(self) -> None:
        findings = gate.validate_format(entry(proposer="运控组"))
        self.assertTrue(any("@GitHub" in f for f in findings))

    def test_rejects_short_reason(self) -> None:
        findings = gate.validate_format(entry(reason="改一下"))
        self.assertTrue(any("过短" in f for f in findings))

    def test_rejects_vague_reason(self) -> None:
        findings = gate.validate_format(entry(reason="为了优化接口，提升扩展性。"))
        self.assertTrue(any("笼统" in f for f in findings))

    def test_rejects_invalid_type(self) -> None:
        findings = gate.validate_format(entry(entry_type="小改"))
        self.assertTrue(any("非法" in f for f in findings))

    def test_rejects_breaking_change_with_no_affected_domain(self) -> None:
        findings = gate.validate_format(entry(entry_type="破坏性", affected="无"))
        self.assertTrue(any("影响域" in f for f in findings))

    def test_allows_non_breaking_change_with_no_affected_domain(self) -> None:
        self.assertEqual(gate.validate_format(entry(affected="无")), [])

    def test_ignores_fenced_format_example(self) -> None:
        text = (
            "```markdown\n"
            "### <类型>：<一句话说明>\n"
            "- **原因**：优化\n"
            "```\n\n" + entry()
        )
        self.assertEqual(gate.validate_format(text), [])


class ValidateRecordedTest(unittest.TestCase):
    def test_no_finding_when_no_interface_files_touched(self) -> None:
        findings = gate.validate_recorded(entry(), ["README.md"])
        self.assertEqual(findings, [])

    def test_rejects_interface_change_without_changelog_edit(self) -> None:
        findings = gate.validate_recorded(
            entry(), ["robot_perception_interfaces/msg/BoxPose.msg"]
        )
        self.assertTrue(any("未更新" in f for f in findings))

    def test_rejects_empty_unreleased_section(self) -> None:
        text = "## [Unreleased]\n\n<!-- 注释不算内容 -->\n\n## [0.1.0] - 2026-01-01\n"
        findings = gate.validate_recorded(
            text,
            ["robot_perception_interfaces/msg/BoxPose.msg", "contract/CHANGELOG.md"],
        )
        self.assertTrue(any("为空" in f for f in findings))

    def test_accepts_interface_change_with_unreleased_entry(self) -> None:
        findings = gate.validate_recorded(
            entry(),
            ["robot_perception_interfaces/msg/BoxPose.msg", "contract/CHANGELOG.md"],
        )
        self.assertEqual(findings, [])

    def test_watches_multiword_domain_package(self) -> None:
        findings = gate.validate_recorded(
            entry(), ["robot_rt_control_interfaces/msg/SafetyState.msg"]
        )
        self.assertTrue(any("未更新" in f for f in findings))

    def test_endpoints_change_also_requires_changelog(self) -> None:
        findings = gate.validate_recorded(entry(), ["contract/endpoints.yaml"])
        self.assertTrue(any("未更新" in f for f in findings))


if __name__ == "__main__":
    unittest.main()
