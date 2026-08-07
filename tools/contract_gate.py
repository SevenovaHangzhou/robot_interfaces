#!/usr/bin/env python3
"""校验 contract/endpoints.yaml 与仓库内 IDL 文件双向闭合。

杀掉四类漂移：
  - 注册表点名的类型不存在（历史上 alfa_* 六个包全组织零命中就是这一类）
  - 仓库里有类型但没有任何 endpoint 引用（无主孤儿类型）
  - IDL 文件存在但没有列入 CMakeLists.txt（不会生成代码）
  - 自定义 endpoint 类型没有归档到提供方所属域包
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ENDPOINTS = Path("contract/endpoints.yaml")

KIND_DIR = {"topic": "msg", "service": "srv", "action": "action"}
KIND_EXT = {"topic": ".msg", "service": ".srv", "action": ".action"}

REQUIRED_KEYS = ("id", "ros_name", "kind", "type", "producer", "consumers", "qos")


def local_idl_types() -> set[str]:
    """仓库内全部 IDL 类型的全名，如 robot_perception_interfaces/msg/BoxPose。"""
    found: set[str] = set()
    for pkg in sorted(Path(".").glob("robot_*_interfaces")):
        for sub, ext in (("msg", ".msg"), ("srv", ".srv"), ("action", ".action")):
            for path in sorted((pkg / sub).glob(f"*{ext}")):
                found.add(f"{pkg.name}/{sub}/{path.stem}")
    return found


def declared_in_cmake(package: str) -> set[str]:
    """CMakeLists.txt 中 rosidl_generate_interfaces 实际列出的文件。"""
    cmake = Path(package) / "CMakeLists.txt"
    if not cmake.is_file():
        return set()
    declared: set[str] = set()
    for line in cmake.read_text(encoding="utf-8").splitlines():
        stripped = line.strip().strip('"')
        for sub, ext in (("msg", ".msg"), ("srv", ".srv"), ("action", ".action")):
            if stripped.startswith(f"{sub}/") and stripped.endswith(ext):
                declared.add(f"{package}/{sub}/{Path(stripped).stem}")
    return declared


def validate(document: dict) -> list[str]:
    findings: list[str] = []

    domains = set(document.get("domains") or [])
    package_owners = document.get("package_owners") or {}
    profiles = set(document.get("qos_profiles") or [])
    endpoints = document.get("endpoints") or []
    member_types = set(document.get("member_types") or [])

    if not endpoints:
        return ["endpoints.yaml: endpoints 为空"]

    local = local_idl_types()
    local_packages = {type_name.split("/", 1)[0] for type_name in local}
    referenced: set[str] = set(member_types)
    seen_ids: set[str] = set()
    seen_names: dict[str, str] = {}

    if not package_owners:
        findings.append("endpoints.yaml: 缺少 package_owners，无法校验 IDL 域归属")

    valid_owners = (domains - {"external"}) | {"shared"}
    for package in sorted(local_packages - set(package_owners)):
        findings.append(f"{package}: 未在 package_owners 声明归属")
    for package in sorted(set(package_owners) - local_packages):
        findings.append(f"package_owners: {package} 在仓库中不存在")
    for package, owner in sorted(package_owners.items()):
        if owner not in valid_owners:
            findings.append(
                f"package_owners: {package} 的 owner={owner!r} 非法，"
                "必须是已声明业务域或 shared"
            )
            continue
        if owner != "shared":
            expected_package = f"robot_{owner}_interfaces"
            if package != expected_package:
                findings.append(
                    f"package_owners: {package} 归属 {owner!r}，"
                    f"域包必须命名为 {expected_package}"
                )

    for entry in endpoints:
        eid = entry.get("id", "<无 id>")

        for key in REQUIRED_KEYS:
            if key not in entry:
                findings.append(f"{eid}: 缺少必填字段 {key}")

        if eid in seen_ids:
            findings.append(f"{eid}: id 重复")
        seen_ids.add(eid)

        kind = entry.get("kind")
        if kind not in KIND_DIR:
            findings.append(f"{eid}: kind={kind!r} 非法，必须是 topic/service/action")

        producer = entry.get("producer")
        if producer and producer not in domains:
            findings.append(f"{eid}: producer={producer!r} 不是已声明的域")

        for consumer in entry.get("consumers") or []:
            if consumer not in domains:
                findings.append(f"{eid}: consumer={consumer!r} 不是已声明的域")

        if producer and producer in (entry.get("consumers") or []):
            findings.append(f"{eid}: producer 与 consumer 同域，不是跨域 endpoint")

        qos = entry.get("qos")
        if qos and qos not in profiles:
            findings.append(f"{eid}: qos={qos!r} 不是已声明的命名剖面")

        # 同一 ros_name 只允许一个权威生产者。
        # 例外：TF 的唯一性按坐标边判定而非按 topic 判定（契约 6.11），
        # /tf 天生是多发布者 topic —— Perception 发 map→odom，
        # RT-Control 的 robot_state_publisher 发本体边。标 multi_producer: true
        # 表示已在契约中逐条指定了每条边的权威发布者。
        ros_name = entry.get("ros_name")
        if ros_name and not entry.get("multi_producer"):
            if ros_name in seen_names and seen_names[ros_name] != producer:
                findings.append(
                    f"{eid}: {ros_name} 已由 {seen_names[ros_name]} 生产，"
                    "同一名称不得有两个权威生产者"
                    "（TF 一类按边判定唯一性的可标 multi_producer: true）"
                )
            seen_names.setdefault(ros_name, producer)

        # 类型闭合
        type_name = entry.get("type")
        if not type_name:
            continue
        referenced.add(type_name)

        if entry.get("external_type"):
            if type_name.startswith("robot_"):
                findings.append(
                    f"{eid}: 标为 external_type 但 type={type_name} 属于本仓库"
                )
            continue

        if not type_name.startswith("robot_"):
            findings.append(
                f"{eid}: type={type_name} 非本仓库类型，需显式标注 external_type: true"
            )
            continue

        if type_name not in local:
            findings.append(f"{eid}: type={type_name} 在仓库中不存在")
            continue

        package = type_name.split("/", 1)[0]
        package_owner = package_owners.get(package)
        if package_owner not in (producer, "shared"):
            findings.append(
                f"{eid}: type={type_name} 归属 {package_owner!r}，"
                f"但 endpoint 提供方是 {producer!r}；"
                "自定义 IDL 必须放在提供方域包中（shared 基础类型除外）"
            )

        expected_dir = KIND_DIR.get(kind)
        if expected_dir and f"/{expected_dir}/" not in type_name:
            findings.append(
                f"{eid}: kind={kind} 与 type={type_name} 的目录不匹配"
            )

    # 反向闭合：仓库里的类型必须有主
    for type_name in sorted(local - referenced):
        findings.append(
            f"{type_name}: 未被任何 endpoint 或 member_types 引用，"
            "属于无主类型；域内接口不得留在公共契约仓库"
        )

    for type_name in sorted(member_types - local):
        findings.append(f"member_types: {type_name} 在仓库中不存在")

    # CMake 声明闭合：写了文件但没进 CMakeLists 会静默不生成
    for pkg in sorted(Path(".").glob("robot_*_interfaces")):
        pkg_local = {t for t in local if t.startswith(f"{pkg.name}/")}
        declared = declared_in_cmake(pkg.name)
        for missing in sorted(pkg_local - declared):
            findings.append(
                f"{missing}: 文件存在但未列入 {pkg.name}/CMakeLists.txt，不会生成代码"
            )
        for extra in sorted(declared - pkg_local):
            findings.append(f"{extra}: CMakeLists.txt 声明了但文件不存在")

    return findings


def main() -> int:
    if not ENDPOINTS.is_file():
        print(f"FAIL: 缺少 {ENDPOINTS}", file=sys.stderr)
        return 1

    try:
        document = yaml.safe_load(ENDPOINTS.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"FAIL: endpoints.yaml 不是合法 YAML: {exc}", file=sys.stderr)
        return 1

    findings = validate(document)
    if findings:
        print("FAIL: 契约闭合门禁未通过", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    count = len(document.get("endpoints") or [])
    print(f"PASS: 契约闭合门禁（{count} 个 endpoint，{len(local_idl_types())} 个本地类型）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
