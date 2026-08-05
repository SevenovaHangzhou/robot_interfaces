#!/usr/bin/env python3
"""校验 contract/CHANGELOG.md 记录了本次接口变更的原因与提出人。

用法：
    tools/changelog_gate.py                    # 只校验格式
    tools/changelog_gate.py --base origin/main # 额外校验变更是否被记录
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CHANGELOG = Path("contract/CHANGELOG.md")
ENDPOINTS = Path("contract/endpoints.yaml")

# 触发必须记日志的路径
WATCHED = (re.compile(r"^robot_[a-z]+_interfaces/.+\.(msg|srv|action)$"),
           re.compile(r"^contract/endpoints\.yaml$"))

ENTRY_TYPES = ("新增", "非破坏性", "破坏性")

# 每条变更必须齐备的四要素
REQUIRED_FIELDS = ("接口", "原因", "提出人", "影响域")

# 被判为无实质内容的原因表述
VAGUE_REASONS = ("优化", "完善", "改进", "重构", "调整", "扩展性", "更好", "统一风格")

MIN_REASON_LEN = 20


def _run(*args: str) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout


def changed_files(base: str) -> list[str]:
    merge_base = _run("git", "merge-base", base, "HEAD").strip() or base
    diff = _run("git", "diff", "--name-only", f"{merge_base}...HEAD")
    return [line for line in diff.splitlines() if line]


def _strip_fenced(text: str) -> str:
    """去掉 ``` 围栏代码块，避免把格式示例当成真实条目。

    保留换行数以维持行号语义。
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def _entry_blocks(text: str) -> list[tuple[str, str, str]]:
    """返回 (类型, 标题, 正文) 三元组。"""
    text = _strip_fenced(text)
    pattern = re.compile(
        r"^###\s*(?P<type>[^：:]+)[：:]\s*(?P<title>.+?)\s*$\n"
        r"(?P<body>.*?)(?=^###\s|^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return [
        (m.group("type").strip(), m.group("title").strip(), m.group("body"))
        for m in pattern.finditer(text)
    ]


def _field_value(body: str, field: str) -> str | None:
    pattern = re.compile(
        rf"^-\s*\*\*{re.escape(field)}\*\*[：:]\s*(?P<value>.+?)"
        rf"(?=^-\s*\*\*|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    if match is None:
        return None
    return " ".join(match.group("value").split())


def validate_format(text: str) -> list[str]:
    findings: list[str] = []

    if "## [Unreleased]" not in text:
        findings.append("CHANGELOG: 缺少 '## [Unreleased]' 小节")

    entries = _entry_blocks(text)
    if not entries:
        findings.append("CHANGELOG: 未找到任何 '### <类型>：<说明>' 条目")

    for entry_type, title, body in entries:
        label = f"条目 '{title[:40]}'"

        if entry_type not in ENTRY_TYPES:
            findings.append(
                f"{label}: 类型 {entry_type!r} 非法，必须是 {'/'.join(ENTRY_TYPES)}"
            )

        for field in REQUIRED_FIELDS:
            value = _field_value(body, field)
            if value is None:
                findings.append(f"{label}: 缺少 **{field}** 要素")
                continue
            if not value:
                findings.append(f"{label}: **{field}** 为空")

        reason = _field_value(body, "原因") or ""
        if reason and len(reason) < MIN_REASON_LEN:
            findings.append(
                f"{label}: **原因** 过短（{len(reason)} 字），"
                f"至少 {MIN_REASON_LEN} 字并说明触发变更的具体问题"
            )
        if reason and any(v in reason for v in VAGUE_REASONS) and len(reason) < 60:
            findings.append(
                f"{label}: **原因** 只有笼统表述，需写出触发变更的具体问题"
            )

        proposer = _field_value(body, "提出人") or ""
        if proposer and not proposer.startswith("@"):
            findings.append(
                f"{label}: **提出人** 必须以 @GitHub 用户名开头，实际为 {proposer!r}"
            )

        if entry_type == "破坏性":
            affected = _field_value(body, "影响域") or ""
            if affected.strip() in ("无", "None", "-"):
                findings.append(f"{label}: 破坏性变更的 **影响域** 不能为 '无'")

    return findings


def validate_recorded(text: str, files: list[str]) -> list[str]:
    """接口文件有改动时，Unreleased 小节必须有新条目。"""
    touched = [f for f in files if any(p.match(f) for p in WATCHED)]
    if not touched:
        return []

    if str(CHANGELOG) not in files:
        return [
            f"改动了 {len(touched)} 个接口文件但未更新 {CHANGELOG}："
            + "、".join(touched[:5])
        ]

    match = re.search(
        r"^##\s*\[Unreleased\]\s*$\n(?P<body>.*?)(?=^##\s*\[|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    body = match.group("body") if match else ""
    stripped = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
    if not stripped:
        return [
            "改动了接口文件，但 '## [Unreleased]' 小节为空。"
            "新条目必须追加到 Unreleased，发布时才移入版本小节。"
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default=None,
        help="对比基线（如 origin/main）。给出时额外校验变更是否被记录。",
    )
    args = parser.parse_args(argv)

    if not CHANGELOG.is_file():
        print(f"FAIL: 缺少 {CHANGELOG}", file=sys.stderr)
        return 1

    text = CHANGELOG.read_text(encoding="utf-8")
    findings = validate_format(text)

    if args.base:
        findings.extend(validate_recorded(text, changed_files(args.base)))

    if findings:
        print("FAIL: 接口变更日志门禁未通过", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print("PASS: 接口变更日志门禁")
    return 0


if __name__ == "__main__":
    sys.exit(main())
