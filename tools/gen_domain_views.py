#!/usr/bin/env python3
"""从 contract/endpoints.yaml 生成分域可读视图。

替代人工维护的五域规范：每个域只看自己产出和消费的 endpoint，
但事实源唯一，不可能与权威契约不一致。

  tools/gen_domain_views.py            # 写入 contract/views/
  tools/gen_domain_views.py --check    # 只校验是否最新（CI 用）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ENDPOINTS = Path("contract/endpoints.yaml")
VIEW_DIR = Path("contract/views")

BANNER = "<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->"

DOMAIN_LABEL = {
    "rt_control": "RT-Control",
    "perception": "Perception",
    "motion": "Motion",
    "autonomy": "Autonomy",
    "external": "外部/本地入口",
}

KIND_LABEL = {"topic": "Topic", "service": "Service", "action": "Action"}


def load() -> dict:
    return yaml.safe_load(ENDPOINTS.read_text(encoding="utf-8")) or {}


def constraints(entry: dict) -> str:
    """把 endpoint 的约束字段拼成一句人可读的说明。"""
    parts: list[str] = []
    if entry.get("qos") and entry["qos"] != "Q_DEFAULT":
        parts.append(entry["qos"])
    rate = entry.get("rate_hz")
    if rate:
        lo, hi = rate
        parts.append(f"{lo} Hz" if lo == hi else f"{lo}～{hi} Hz")
    if entry.get("max_age_ms"):
        parts.append(f"最大年龄 {entry['max_age_ms']} ms")
    if entry.get("watchdog_ms"):
        parts.append(f"看门狗 {entry['watchdog_ms']} ms")
    if entry.get("reserved"):
        parts.append("**产品预留，Demo 不部署**")
    if entry.get("external_type"):
        parts.append("ROS 标准类型")
    if entry.get("note"):
        parts.append(entry["note"])
    return "；".join(parts) or "—"


def _table(entries: list[dict], peer_key: str) -> list[str]:
    """peer_key: 'consumers' 显示消费方，'producer' 显示生产方。"""
    lines = [
        "| ID | ROS 名称 | 形式 | 类型 | " + ("消费方" if peer_key == "consumers" else "生产方") + " | 约束 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for e in entries:
        if peer_key == "consumers":
            peer = "、".join(DOMAIN_LABEL.get(c, c) for c in e.get("consumers", []))
        else:
            peer = DOMAIN_LABEL.get(e.get("producer"), e.get("producer", ""))
        lines.append(
            f"| {e['id']} | `{e['ros_name']}` | {KIND_LABEL.get(e['kind'], e['kind'])} "
            f"| `{e['type']}` | {peer or '—'} | {constraints(e)} |"
        )
    return lines


def render(domain: str, doc: dict) -> str:
    endpoints = doc.get("endpoints") or []
    produced = [e for e in endpoints if e.get("producer") == domain]
    consumed = [e for e in endpoints if domain in (e.get("consumers") or [])]

    label = DOMAIN_LABEL.get(domain, domain)
    out = [
        BANNER,
        "",
        f"# {label} 域接口视图",
        "",
        f"> 契约版本：{doc.get('version', '未标注')}",
        "> 事实源：`contract/endpoints.yaml`",
        "> Wire schema：本仓库对应的 `robot_*_interfaces` IDL",
        "",
        f"本文只列 {label} 域**产出**与**消费**的跨域 endpoint，用于分域阅读。",
        "语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。",
        "",
        f"## 本域产出（{len(produced)} 条）",
        "",
    ]

    if produced:
        out += _table(produced, "consumers")
    else:
        out.append("本域不产出跨域 endpoint。")

    out += ["", f"## 本域消费（{len(consumed)} 条）", ""]

    if consumed:
        out += _table(consumed, "producer")
    else:
        out.append("本域不消费跨域 endpoint。")

    # 禁止的通信边
    forbidden = [
        f for f in (doc.get("forbidden_edges") or []) if f.get("from") == domain
    ]
    if forbidden:
        out += ["", "## 本域禁止的通信边", ""]
        out += [f"- 不得访问 `{f['to']}`" for f in forbidden]

    removed = doc.get("removed_endpoints") or []
    if removed:
        out += [
            "",
            "## 已删除的 endpoint",
            "",
            "出现在 ROS graph 中即为违约：",
            "",
        ]
        out += [f"- `{r}`" for r in removed]

    return "\n".join(out) + "\n"


SECTIONS = [
    ("5.1 任务入口（Autonomy 提供）", lambda e: e["producer"] == "autonomy"),
    ("5.2 Perception 提供", lambda e: e["producer"] == "perception"),
    ("5.3 Motion 提供", lambda e: e["producer"] == "motion"),
    ("5.4 RT-Control 输入", lambda e: e["producer"] == "rt_control"
        and e["id"].startswith("R-IN")),
    ("5.5 RT-Control 输出", lambda e: e["producer"] == "rt_control"
        and not e["id"].startswith("R-IN")),
]

KIND_FORM = {"topic": "Topic", "service": "Service", "action": "Action"}


def render_master_table(doc: dict) -> str:
    """生成 cross-domain-interfaces.md 第 5 节接口总表。"""
    endpoints = doc.get("endpoints") or []
    out = [
        BANNER.replace("本文", "本节"),
        "",
        "## 5. 接口总表",
        "",
        "ID 前缀含义：`G` = Gateway/本地入口，`P` = Perception 提供，"
        "`N` = 导航能力（Motion 或 Perception 提供），`M` = Motion 提供，"
        "`R-IN` = RT-Control 输入，`R-OUT` = RT-Control 输出。",
        "",
    ]
    for title, pred in SECTIONS:
        rows = [e for e in endpoints if pred(e)]
        if not rows:
            continue
        out += [f"### {title}", "", "| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |",
                "| --- | --- | --- | --- | --- |"]
        for e in rows:
            cons = "、".join(DOMAIN_LABEL.get(c, c) for c in e.get("consumers") or [])
            prod = DOMAIN_LABEL.get(e["producer"], e["producer"])
            arrow = " ⇄ " if e["kind"] in ("action", "service") else " → "
            direction = (cons + arrow + prod) if e["kind"] in ("action", "service") \
                else (prod + arrow + cons)
            out.append(
                f"| {e['id']} | `{e['ros_name']}` | "
                f"{KIND_FORM[e['kind']]} / `{e['type']}` | {direction} | "
                f"{e.get('constraint', '—')} |"
            )
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="只校验视图是否与 endpoints.yaml 一致"
    )
    parser.add_argument(
        "--master-table", metavar="PATH",
        help="额外生成接口总表到指定路径（供 robot_system 契约引用）",
    )
    args = parser.parse_args(argv)

    if not ENDPOINTS.is_file():
        print(f"FAIL: 缺少 {ENDPOINTS}", file=sys.stderr)
        return 1

    doc = load()
    domains = [d for d in (doc.get("domains") or []) if d != "external"]

    stale: list[str] = []
    for domain in domains:
        path = VIEW_DIR / f"{domain}.md"
        content = render(domain, doc)
        if args.check:
            if not path.is_file():
                stale.append(f"{path}: 缺失")
            elif path.read_text(encoding="utf-8") != content:
                stale.append(f"{path}: 与 endpoints.yaml 不一致")
        else:
            VIEW_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    if args.master_table:
        mt = Path(args.master_table)
        content = render_master_table(doc)
        if args.check:
            if not mt.is_file():
                stale.append(f"{mt}: 缺失")
            elif mt.read_text(encoding="utf-8") != content:
                stale.append(f"{mt}: 与 endpoints.yaml 不一致")
        else:
            mt.parent.mkdir(parents=True, exist_ok=True)
            mt.write_text(content, encoding="utf-8")
            print(f"已生成接口总表到 {mt}")

    if args.check:
        if stale:
            print("FAIL: 分域视图过期", file=sys.stderr)
            for item in stale:
                print(f"  - {item}", file=sys.stderr)
            print("  运行 tools/gen_domain_views.py 重新生成", file=sys.stderr)
            return 1
        print(f"PASS: 分域视图门禁（{len(domains)} 个域视图与契约一致）")
        return 0

    print(f"已生成 {len(domains)} 个分域视图到 {VIEW_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
