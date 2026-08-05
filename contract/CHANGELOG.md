# 接口变更日志

本文是 `robot_interfaces` 全部公共接口变更的唯一记录。任何触及
`robot_*_interfaces/**` 或 `contract/endpoints.yaml` 的 PR 都必须在本文
追加条目，由 `tools/changelog_gate.py` 在 CI 强制校验。

## 条目格式

每次发布一个 `## [版本] - 日期` 小节，其下每条变更用四级要素记录：

```markdown
### <类型>：<一句话说明>

- **接口**：受影响的 endpoint ID 与类型全名
- **原因**：为什么必须改。写触发变更的具体问题或需求，不写"优化""完善"
- **提出人**：@GitHub 用户名（域名）
- **影响域**：需要同批升级的域，或 `无`
```

`<类型>` 取 `新增` / `非破坏性` / `破坏性` 之一：

| 类型 | 判定 | 发布要求 |
| --- | --- | --- |
| `新增` | 新增 endpoint、msg/srv/action 文件或常量 | 同批更新 `endpoints.yaml` 与接口总表 |
| `非破坏性` | 已有类型新增字段、新增错误码 | PR 列出全部生产者与消费者，通知受影响域负责人 |
| `破坏性` | 删除或重命名字段、改类型/单位/坐标系/终态语义/错误语义、改包名 | 先开 design issue，经接口所有者与全部消费域评审，随统一 package 原子发布。**没有消费者迁移和原子发布方案不得合并** |

三条硬性要求：

1. **原因必须可追溯到具体问题**。"为了扩展性"不是原因；"Twist 无 header 导致 RT-Control
   无法用消息年龄做看门狗判据"是原因。
2. **提出人是人，不是仓库或域**。需要一个能回答"当初为什么这么定"的具体人。
3. **破坏性变更必须写清不原子升级的后果**。ROS 2 类型不匹配是静默失败，
   两侧节点都正常起、日志无报错，但数据完全不通。

---

## [Unreleased]

<!-- 新条目追加到本节。发布时改为 ## [x.y.z] - YYYY-MM-DD 并新建空的 Unreleased -->

### 破坏性：`SafetyState` 拆分总线字段并删除三项无法填写的字段

- **接口**：`robot_control_interfaces/msg/SafetyState` —— `bool fieldbus_online`
  拆为 `bool ethercat_online` + `bool canopen_online`；删除 `air_pressure_ok`、
  `emergency_stop`、`protective_stop`、`safe_torque_off`
- **原因**：拆总线是因为 rt-control 实际有两条独立总线（EtherCAT 承载 14 个机械轴、
  CANopen 承载履带），故障后果不同 —— EtherCAT 掉线手臂不能动，CANopen 掉线底盘不能动，
  单个布尔无法表达"一条通一条不通"，消费方只能一律停。删除四个字段是因为实机
  **填不出真值**：`air_pressure_ok` 无对应传感器；三个硬安全链状态（急停、安全继电器、
  STO）未接入软件可读通路。保留填不出的字段比删掉更危险 —— 消费方看到
  `emergency_stop=false` 会读成"急停未触发"，而实际含义是"不知道"。
- **提出人**：@kkozia（任务规划 / 契约）；字段删除范围由 rt-control 实现确定
- **影响域**：rt_control（发布方）、perception、motion、autonomy（订阅方）。
  **不原子升级的后果**：字段增删改变 wire 格式，版本不一致时 `SafetyState`
  无法反序列化，订阅方收不到安全状态；按 fail-closed 语义会禁止一切新动作。
  **已登记风险**：`SafetyState` 现在只是**软件可观测摘要，不含硬安全链状态**。
  消费方不得从本消息推断急停/安全继电器/STO 是否触发。硬安全链仍由硬件回路保证
  （契约 3.1：不得由软件层代替），但软件侧失去了这三项的可观测性。

### 非破坏性：`/joint_states` 与 `/battery_state` 频率按实机对齐

- **接口**：R-OUT-03 `/joint_states` 100 Hz → **50 Hz**（并注明只含 14 个 EtherCAT
  机械轴，不含履带关节）；R-OUT-04 `/battery_state` 1 Hz → **0.2 Hz**（BMS 周期 5 s）；
  R-OUT-02 `/wheel/odom` 补注 `frame_id=odom`、`child_frame_id=base_footprint`
- **原因**：契约这三处的数值是设计阶段写的，与实机不符 ——
  `joint_state_broadcaster.update_rate` 实为 50，BMS 上报周期实为 5 s。
  契约里的频率是各域做时序预算和新鲜度判断的依据，写错会导致消费方按不存在的
  频率设置超时。同时 rt-control 明确 `enable_odom_tf=false`，只发 `/wheel/odom`
  消息而不发 `odom → base_footprint` TF，该 TF 归属此前是契约空洞，一并补进 6.11。
- **提出人**：@kkozia（任务规划 / 契约）；实测值由 rt-control 提供
- **影响域**：无（仅频率与说明修正，字段与 wire 格式不变）。
  各域若曾按 100 Hz / 1 Hz 设置超时阈值需相应放宽。

### 破坏性：删除 R-OUT-07 / R-OUT-08，模型版本一致性改为靠仓库引用

- **接口**：删除 endpoint R-OUT-07 `/robot_model/info`、R-OUT-08 `/calibration/info`
  及类型 `robot_system_interfaces/msg/RobotModelInfo`、`CalibrationInfo`；
  `WallTaskPlan` 删除 `model_hash`、`calibration_hash` 两个字段
- **原因**：rt-control 实机从未实现这两个 topic。改为四域通过
  `release/source-lock.yaml` 引用**同一个 `robot_description` commit** 保证一致性 ——
  URDF、标定数据和退避表都在该仓库内，构建期即可验证，比运行期 hash 对账更强。
  特殊情况需要其他版本模型时在该仓库另开分支单独引用。同一事实若有仓库 SHA 与运行期
  hash 两个来源，两者必须保持同步而这个同步没有强制机制；删掉运行期那份消除了矛盾面。
  `WallTaskPlan` 的两个 hash 字段随之失去对账目标，按"说不出哪个消费者读它就不加"删除。
- **提出人**：@kkozia（任务规划 / 契约）
- **影响域**：perception（不再填写两个 hash 字段）、
  motion 与 autonomy（原本也未订阅这两个 topic）。
  **不原子升级的后果**：`WallTaskPlan` 是 P-01 Result 的载荷，删字段改变 wire 格式，
  Perception 与 Autonomy 版本不一致时 P-01 Result 无法反序列化，计划阶段即失败。
  **已登记风险**：删除运行期校验后，若某域部署了与 source-lock 不一致的镜像，
  运行期无法发现，发布纪律成为唯一防线。`DomainReadiness.contract_version`
  只覆盖接口 schema，不覆盖模型与标定。

### 新增：错误码落地为集中常量 `ErrorCode.msg`，采用 DREE 四位编码

- **接口**：新增 `robot_system_interfaces/msg/ErrorCode`，46 个常量。
  四位编码 **D R E E**：D=域归属（0 通用 / 1 RT-Control / 2 Perception / 3 Motion /
  4 Autonomy），R=是否可机器自主恢复（0/1），EE=事件分类（00 通信 / 10 配置 /
  20 硬件 / 30 环境 / 40 数据 / 50 求解 / 60 执行 / 70 安全 / 80 任务 / 90 内部）。
  配套 `tools/error_code_gate.py` 在 CI 校验编码规则
- **原因**：契约此前只写"错误码按域分段，具体分段表随统一 interfaces package 落地"，
  但分段表从未落地 —— `ErrorInfo.code` 是个无取值来源的 `uint32`，各域只能各自编号，
  必然冲突。更关键的是**只有分段规则、没有段内分类规则**，加码时无依据可循。
  确定受众是 Autonomy 域与现场运维后，分类维度按其实际问题设计：第 1 位答"该找谁"、
  第 2 位答"要不要等机器自愈"、后两位答"往哪查"。恢复性入编码是有意的冗余 ——
  同一事件按可恢复性分成两个码（如 `RT_DRIVE_FAULT=1020` 需人工复位
  vs `RT_FIELDBUS_OFFLINE=1120` 等重连），让人看码即知处置方式。
- **提出人**：@kkozia（任务规划 / 契约）；分类维度由用户指定
- **影响域**：无（新增类型，现有字段与 wire 格式不变）。各域在自己 D 段内扩充是
  非破坏性变更；D=0 通用段扩充需契约评审。
  **注意**：改变某个码的第 2 位即改变其数值，属破坏性变更 —— 可恢复性判断应在
  引入该码时做扎实。第 2 位必须与 `ErrorInfo.retryable` 一致，由 CI 校验；
  Autonomy 的重试判定只读 `retryable`，不解析 `code`。

### 破坏性：M-01 改为转发 P-01 的重拍位，`PickSequence` 补齐工位与重拍位

- **接口**：`PickSequence` 新增 `string station_id` 与 `CameraViewPose[] camera_view_poses`；
  新增类型 `robot_task_interfaces/msg/CameraViewPose`（`arm` / `box_id` / `pose`，
  `ARM_LEFT=0`、`ARM_RIGHT=1`）；`MoveToCameraViewPose.Goal` 的 `string[] box_ids`
  改为 `CameraViewPose[] camera_view_poses`
- **原因**：抓取计划确定由 Perception 产出（含序列、工位、到站位姿、近距离重拍位），
  但原 IDL 只表达了序列与到站位姿，重拍位和工位在契约里没有落点 —— M-01 只收到
  `box_ids`，等于要求 Motion 自行解算观测位姿，与"计划由 Perception 产出、
  下游不重算"矛盾。重拍位必须绑定到具体臂（左/右），否则双箱序列无法表达哪条臂
  拍哪个箱。补齐后 M-01 退化为纯执行，消除了同一位姿两处解算的风险。
- **提出人**：@kkozia（任务规划 / 契约）
- **影响域**：perception（产出新增字段）、motion（M-01 改为执行给定位姿，
  删除自行解算逻辑）、autonomy（原样转发计划中的重拍位）。
  **不原子升级的后果**：`MoveToCameraViewPose.Goal` 字段类型改变，Autonomy 与 Motion
  版本不一致时 Action 类型不匹配、Goal 无法送达，取箱前卡住。必须同批发布。

### 破坏性：`PickSequence` 新增 `wall_row` 与 `station_standoff_m`，固化退避表

- **接口**：`PickSequence` 新增 `uint8 wall_row`（**0 = 最下排，向上递增**）与
  `float32 station_standoff_m`（实际使用的退避距离，单位 m）；契约 2.1 新增退避表与
  "序列不得跨退避组"约束
- **原因**：`station_nav_pose` 由"箱墙列面心 → 法向量与 XY 方向平均值 → X 方向回退
  退避距离"导出，退避距离**按箱墙排取值不同**：下两排 0.70 m，上三排 0.90 m
  （上排取箱手臂俯仰行程更大，底盘必须停得更远）。既然是按排查表而非全局常量，
  按"单一事实源"原则它就应当作为计划数据显式出现，而不是散在感知实现里的隐式配置。
  该表由运控拥有、Perception 消费，是跨部门配置依赖：夹具或臂长变化时若不同步更新，
  几何计算仍成功、位姿仍是合法 PoseStamped、底盘仍会开过去，但手臂够不着，
  且任何一层都不报错 —— 属于**静默错误**。让感知回报实际使用值，可把配置漂移从
  "现场才暴露"提前到"运行期可核对"。
- **提出人**：@kkozia（任务规划 / 契约）；退避表数值由机械臂运控部提供
- **影响域**：perception（产出两个新字段，按 `wall_row` 查表）、
  autonomy（原样转发）、motion 与观测工具（可选核对配置一致性）。
  **不原子升级的后果**：`PickSequence` 是 `WallTaskPlan` 的成员，字段增加改变 wire 格式，
  Perception 与 Autonomy 版本不一致时 P-01 的 Result 无法反序列化，计划阶段即失败。
  配套动作：退避表纳入机器人模型版本校验范围。
  另：序列的箱不得跨退避组（`wall_row` 1|2 边界），否则单个 `station_standoff_m`
  无法表达本序列退避距离；同组内是否跨排为待定项。编号方向反了会让下排用 0.90 m、
  上排用 0.70 m，几何计算仍成功、位姿仍合法，只在现场暴露 —— 已列入边界验收清单。

### 破坏性：删除底盘软件门 N-02 / N-03 / M-07 及其对账协议

- **接口**：删除 `robot_navigation_interfaces/srv/SetBaseMotionInhibit`（N-02）、
  `robot_navigation_interfaces/msg/BaseMotionGateState`（N-03）、
  `robot_navigation_interfaces/msg/BaseMotionGateToken`、
  `robot_motion_interfaces/msg/BaseTravelReadiness`（M-07）；
  `robot_motion_interfaces` 包整体取消（M-07 是其唯一类型），公共包 6 个减为 5 个；
  `PlanAndExecutePick.Goal` 与 `PlanAndExecutePlace.Goal` 删除 `gate_owner`、`gate_token`
- **原因**：这套协议守护的全部事实都在 Motion 域内 —— `/cmd_vel_safe` 的唯一生产者是
  Motion，M-01/M-02/M-03 的服务端也是 Motion，手臂构型与活动 goal 是其自有状态；
  M-07 四项公式的数据来源逐项检查后同样全在 Motion 手里。把域内不变量做成跨域协议，
  迫使 Autonomy 为跨域通信的不可靠性自建 generation/epoch 版本对账、五条件采纳判定和
  CAS 线性化点重读，占契约正文约四分之一，且违反"判定权归产生事实的一方、
  调用方不重算服务端判定"。互斥改由 Motion 在 Action Goal 拒绝阶段自行判定，
  用 ROS 2 原生机制替代自建对账，安全性更强 —— Motion 拿自己的实时状态直接判，
  没有跨网络的信息损失，也不存在 Autonomy 对账失败导致的误判。
- **提出人**：@kkozia（任务规划 / 契约）
- **影响域**：motion（删除三个服务端与发布者，改为 Goal 拒绝）、
  autonomy（删除全部 acquire/release 与对账逻辑，不再持有互斥状态）。
  **不原子升级的后果**：Autonomy 若仍调用已删除的 N-02，Service 不存在会导致调用超时，
  按现有 fail-closed 逻辑会卡在取箱前不再推进；Motion 若未实现 Goal 拒绝，
  则互斥不变量在两侧都无人保证 —— 手臂可能在底盘可动时伸出。必须同批发布。
  另：`ExecuteDemoTask.Feedback` 的 TaskPhase 2、4、6、12 失去对应行为，编号保留不动
  （重编号会改变既有常量语义，收益仅为去掉四个未用值），Autonomy 不再上报这四个值。

## [0.2.0] - 2026-08-02

### 破坏性：公共接口包前缀 `alfa_*` 统一改为 `robot_*`

- **接口**：全部 6 个公共包 —— `robot_task_interfaces`、`robot_system_interfaces`、
  `robot_navigation_interfaces`、`robot_motion_interfaces`、
  `robot_control_interfaces`、`robot_perception_interfaces`
- **原因**：组织下 7 个仓库全部使用 `robot_` 前缀，但接口总表沿用历史 `alfa_` 前缀，
  且这批包此前从未落地为真实 IDL。落地时若保留 `alfa_`，会长期存在
  "仓库叫 robot_、类型叫 alfa_、导航里还有 alfa_nav_interfaces" 的三重命名混乱。
- **提出人**：@kkozia（system）
- **影响域**：rt_control、perception、motion、autonomy。纯改包名，字段不变，
  但 wire 上类型全名改变，四域必须同批切换。

### 破坏性：`/cmd_vel_safe` 由 `TwistStamped` 改为 `Twist`，看门狗改为 500 ms

- **接口**：N-04、R-IN-01 `/cmd_vel_safe` —— `geometry_msgs/msg/TwistStamped`
  → `geometry_msgs/msg/Twist`
- **原因**：底盘速度指令不需要按消息 stamp 做时序对齐，`TwistStamped` 的 header
  在本链路无消费者。改用 `Twist` 后消息无时间戳，看门狗判据必须同步从
  "200 ms 消息年龄" 改为 "500 ms 本地接收间隔"，`Q_CONTROL` 的 lifespan 也必须
  从 200 ms 放宽到 500 ms —— 否则消息会在看门狗到期前先被 DDS 丢弃，两个数字互相打架。
- **提出人**：@kkozia（system）
- **影响域**：motion（唯一生产者）、rt_control（唯一消费者）。
  **不原子升级的后果**：topic 类型不匹配，两侧节点都正常启动、日志无任何报错，
  但底盘完全收不到速度指令。必须同批发布。

### 破坏性：移除 `PlcIoState` 与 `RtEnable`

- **接口**：删除 `robot_interfaces/msg/PlcIoState`（`/plc/io_state`）与
  `robot_interfaces/srv/RtEnable`（`/rt/enable`、`/rt/disable`、`/rt/reset_fault`）
- **原因**：这两个类型是 RT-Control 域内接口 —— 三个 topic/service 名在跨域接口总表中
  均无对应 ID。公共契约仓库只收录域间接口，域内接口由各域自持。它们已迁至
  `robot_driver` 的 `rt_control_interfaces`，同时消除了此前公共仓库与
  `robot_driver/src/interfaces/robot_interfaces/` 两份同名副本的双事实源问题。
- **提出人**：@kkozia（rt_control）
- **影响域**：rt_control。`enable_manager` 与 `plc_node` 改依赖
  `rt_control_interfaces`。其他三域从未依赖这两个类型。

### 新增：落地接口总表点名的全部域间类型

- **接口**：G-01、P-01～P-04、N-01～N-03、N-05、M-01～M-03、M-06、M-07、
  R-IN-03～R-IN-05、R-OUT-05～R-OUT-09
- **原因**：`cross-domain-interfaces.md` 自称"接口冻结基线"，但其点名的 6 个接口包
  在全组织零命中 —— 冻结条目此前只有文字、没有可编译 IDL，各域只能自建接口包或
  互相猜字段。本次将总表条目逐条落为 IDL，并加 CI 双向闭合校验防止再次漂移。
- **提出人**：@kkozia（system）
- **影响域**：四域全部。首次落地，无存量消费者需要迁移。

### 非破坏性：`DomainReadiness` 新增 `producer_instance_id` 与 `contract_version`

- **接口**：`robot_system_interfaces/msg/DomainReadiness`
- **原因**：`producer_instance_id` 用于区分"DDS 抖动"与"进程重启" —— 1 s 内由同一
  实例恢复视为抖动可享受宽限，实例 ID 改变即进程重启，新实例不得加入旧 G-01。
  `contract_version` 用于运行期发现新旧 schema 混跑，此前契约要求
  "版本/hash 不匹配不享受宽限"，但这个 hash 在 IDL 里并不存在，无法执行。
- **提出人**：@kkozia（system）
- **影响域**：四域全部（各域均发布 readiness）。随本次首批落地一并生效。
