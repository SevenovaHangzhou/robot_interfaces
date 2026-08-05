#!/usr/bin/env python3
"""校验 ErrorCode.msg 的 DREE 编码规则。

编码：D=域归属，R=可自主恢复，EE=事件分类。
没有这个门禁，编码规则会在几次提交后退化成"看起来像分段的随机数"。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ERROR_CODE = Path("robot_system_interfaces/msg/ErrorCode.msg")

CONST = re.compile(r"^uint32\s+([A-Z][A-Z0-9_]*)\s*=\s*(\d+)\s*$", re.MULTILINE)

DOMAIN_NAMES = {0: "全域通用", 1: "rt_control", 2: "perception", 3: "motion", 4: "autonomy"}

# 各域的名字前缀。全域通用段无前缀要求。
DOMAIN_PREFIX = {1: "RT_", 2: "PERC_", 3: "MOTION_", 4: "AUTO_"}

EVENT_CLASSES = {
    0: "通信与接口误用",
    1: "配置与版本",
    2: "硬件与设备",
    3: "环境与外部条件",
    4: "数据质量",
    5: "计算与求解",
    6: "执行与运动",
    7: "安全与联锁",
    8: "任务与流程",
    9: "内部错误",
}

MAX_PER_SEGMENT = 30


def parse(text: str) -> list[tuple[str, int]]:
    return [(m.group(1), int(m.group(2))) for m in CONST.finditer(text)]


def decode(code: int) -> tuple[int, int, int]:
    """返回 (domain, recoverable, event_class)。"""
    return code // 1000, (code // 100) % 10, (code // 10) % 10


def validate(constants: list[tuple[str, int]]) -> list[str]:
    findings: list[str] = []

    if not constants:
        return ["ErrorCode.msg: 未找到任何 uint32 常量"]

    names = [n for n, _ in constants]
    codes = [c for _, c in constants]

    for name in sorted({n for n in names if names.count(n) > 1}):
        findings.append(f"{name}: 常量名重复")
    for code in sorted({c for c in codes if codes.count(c) > 1}):
        dupes = sorted(n for n, c in constants if c == code)
        findings.append(f"{code}: 数值重复，被 {'、'.join(dupes)} 共用")

    if ("SUCCESS", 0) not in constants:
        findings.append("SUCCESS=0 必须存在且为 0")

    segments: dict[tuple[int, int], int] = {}

    for name, code in constants:
        if name == "SUCCESS":
            continue

        if code < 1 or code > 9999:
            findings.append(f"{name}={code}: 超出 1~9999 的 DREE 编码空间")
            continue

        domain, recoverable, event = decode(code)

        if domain not in DOMAIN_NAMES:
            findings.append(
                f"{name}={code}: 第 1 位 {domain} 不是已定义的域"
                f"（可用 {'/'.join(str(d) for d in sorted(DOMAIN_NAMES))}）"
            )
            continue

        if recoverable not in (0, 1):
            findings.append(
                f"{name}={code}: 第 2 位必须是 0（不可自主恢复）或 1（可自主恢复），实际 {recoverable}"
            )

        if event not in EVENT_CLASSES:
            findings.append(f"{name}={code}: 第 3 位事件分类 {event} 未定义")

        prefix = DOMAIN_PREFIX.get(domain)
        if prefix and not name.startswith(prefix):
            findings.append(
                f"{name}={code}: 属 {DOMAIN_NAMES[domain]} 段，名字须以 {prefix} 开头"
            )
        if prefix is None and any(
            name.startswith(p) for p in DOMAIN_PREFIX.values()
        ):
            findings.append(f"{name}={code}: 在全域通用段，不应带域前缀")

        # 内部错误必须落在 90~99 且不可自主恢复
        if name.endswith("INTERNAL_ERROR"):
            if event != 9:
                findings.append(f"{name}={code}: 内部错误须落在事件分类 9x")
            if recoverable != 0:
                findings.append(f"{name}={code}: 内部错误不得标为可自主恢复")

        segments[(domain, recoverable)] = segments.get((domain, recoverable), 0) + 1

    for (domain, recoverable), count in sorted(segments.items()):
        if count > MAX_PER_SEGMENT:
            label = "可自主恢复" if recoverable else "不可自主恢复"
            findings.append(
                f"{DOMAIN_NAMES[domain]} · {label}: {count} 个码超过上限 {MAX_PER_SEGMENT}，"
                "错误码在替代 retryable 承担程序判断"
            )

    return findings


def summarize(constants: list[tuple[str, int]]) -> str:
    counts: dict[tuple[int, int], int] = {}
    for name, code in constants:
        if name == "SUCCESS":
            continue
        domain, recoverable, _ = decode(code)
        counts[(domain, recoverable)] = counts.get((domain, recoverable), 0) + 1
    parts = []
    for (domain, recoverable), count in sorted(counts.items()):
        parts.append(f"{DOMAIN_NAMES[domain]}{'+' if recoverable else '-'}{count}")
    return "，".join(parts)


def main() -> int:
    if not ERROR_CODE.is_file():
        print(f"FAIL: 缺少 {ERROR_CODE}", file=sys.stderr)
        return 1

    constants = parse(ERROR_CODE.read_text(encoding="utf-8"))
    findings = validate(constants)

    if findings:
        print("FAIL: 错误码编码门禁未通过", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print(f"PASS: 错误码编码门禁（{len(constants)} 个常量；{summarize(constants)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
