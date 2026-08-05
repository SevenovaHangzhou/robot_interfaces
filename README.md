# robot_interfaces

半人形拆码垛机器人的**跨域公共契约**。本仓库是四域之间通信的可编译事实源。

对应文档：`robot_system/docs/cross-domain-interfaces.md`（接口总表）。
文档描述语义，本仓库提供 IDL；两者由 CI 保证一致。

## 只收域间接口

四条收录判据，**全部满足**才收：

1. 生产者与消费者跨越 RT-Control / Perception / Motion / Autonomy 的域边界
   （Gateway 是部署边界，不计入业务域）
2. 在接口总表中有 ID（`G` / `P` / `N` / `M` / `R-IN` / `R-OUT`）
3. ROS 标准类型无法直接表达（`/cmd_vel_safe` 用 `geometry_msgs/Twist`、
   `/joint_states` 用 `sensor_msgs/JointState`，这类不收）
4. 有明确的单位、坐标系、时效和成功语义

反向即退出条件：**不在总表中的类型不得留在本仓库**。域内接口由各域自持，
例如 RT-Control 的 `/plc/io_state`、`/rt/enable` 归 `robot_driver` 的
`rt_control_interfaces`。

## 包结构

| 包 | 内容 | 对应 ID |
| --- | --- | --- |
| `robot_system_interfaces` | 就绪心跳、错误载荷、模型与标定版本 | P-04、M-06、N-06、R-OUT-07～09 |
| `robot_task_interfaces` | 任务级 Action 与载荷 | G-01、P-01、P-02、M-01～M-03 |
| `robot_navigation_interfaces` | 导航任务、定位状态 | N-01、N-05 |
| `robot_control_interfaces` | 使能、真空、安全状态 | R-IN-03～05、R-OUT-05、R-OUT-06 |
| `robot_perception_interfaces` | 障碍点云（产品预留） | P-03 |
| `robot_interfaces_qos` | 命名 QoS 剖面（C++ / Python） | 第 4 节全部剖面 |

一个仓库多个包：`source-lock.yaml` 锁单个 SHA 即一次原子升级，同时各域只
`<depend>` 用得到的包，避免一个字段变更触发全量重编。

依赖方向：`system` ← `control` / `navigation` ← `task`。无环。

底盘与手臂互斥是 Motion 域内不变量，用 Action Goal 拒绝表达，无对应公共类型。

## 分域视图

各部门只需读自己域的视图：`contract/views/{rt_control,perception,motion,autonomy}.md`。

这些文件由 `tools/gen_domain_views.py` 从 `endpoints.yaml` **生成**，不要手工编辑 ——
CI 校验其与契约一致，因此不可能出现"分域文档与权威契约不一致"的漂移。
语义约束、成功判定、重试规则和错误码只在权威契约里定义，视图不重复。

> 桌面上人工维护的《拆垛机器人五域接口规范》已退役，被本目录取代。

## 改接口的流程

1. **判定类型**。新增字段/常量为非破坏性；删除或重命名字段、改类型、单位、
   坐标系、终态语义、错误语义、包名为破坏性。
2. **破坏性变更先开 design issue**，说明原因、影响域、迁移方案、发布顺序，
   经接口所有者与全部消费域评审。没有消费者迁移和原子发布方案不得合并。
3. **同批更新** IDL、`contract/endpoints.yaml`、`contract/CHANGELOG.md`
   和接口总表。
4. **在 CHANGELOG 的 `[Unreleased]` 追加条目**，四要素齐备：接口、原因、
   提出人、影响域。原因必须写触发变更的具体问题，不接受"优化""完善"。
5. 合并后打 tag，各域更新 `source-lock.yaml` 的 SHA。

> ROS 2 类型不匹配是**静默失败**：两侧节点都正常启动、日志无报错，但数据
> 完全不通。破坏性变更必须原子发布。

## 本地校验

```bash
python3 tools/contract_gate.py        # endpoints.yaml 与 IDL 双向闭合
python3 tools/error_code_gate.py      # 错误码 DREE 编码规则
python3 tools/changelog_gate.py       # CHANGELOG 格式与四要素
python3 tools/gen_domain_views.py     # 重新生成分域视图（--check 只校验）
python3 -m unittest discover -s tools/tests -p 'test_*.py'
colcon build                          # 全部包可编译
```

`contract_gate.py` 拦三类漂移：注册表点名的类型不存在、仓库里有类型但无
endpoint 引用、文件存在但漏写进 `CMakeLists.txt`。
