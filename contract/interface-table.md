<!-- 本节由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

## 5. 接口总表

ID 前缀含义：`G` = Gateway/本地入口，`P` = Perception 提供，`N` = 导航能力（Motion 或 Perception 提供），`M` = Motion 提供，`R-IN` = RT-Control 输入，`R-OUT` = RT-Control 输出。

### 5.1 任务入口（Autonomy 提供）

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| G-01 | `/autonomy/execute_demo_task` | Action / `robot_autonomy_interfaces/action/ExecuteDemoTask` | 外部/本地入口 ⇄ Autonomy | 同时只接受一个活动 Goal，第二个在 Goal 响应阶段 reject；终态三选一 |

### 5.2 Perception 提供

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| P-01 | `/perception/build_wall_task_plan` | Action / `robot_perception_interfaces/action/BuildWallTaskPlan` | Autonomy ⇄ Perception | Goal 携带非零 `task_id` 与锁定 `scene_profile_id`；真实单次同步采集；Result 返回新 `scene_id`；25 箱；固定 15 序列；每箱冻结 arm 与 suction_mode，pose 为吸取表面接触位姿；每序列自带 `station_id`、统一 0.74 m 退避的 `station_nav_pose(map)`、按臂绑定重拍位；每个 G-01 只调用一次；严格成功 |
| P-02 | `/perception/refine_sequence_poses` | Action / `robot_perception_interfaces/action/RefineSequencePoses` | Autonomy ⇄ Perception | Goal 的 `expected_scene_id`、sequence、box_ids、arms、suction_modes 必须与当前 producer instance 最近一次成功 P-01 完全一致；同箱同序；返回同臂同吸取方式的吸取表面接触位姿；`base_link`；stamp=真实曝光时刻；底盘静止、TF、标定不变 |
| P-03 | `/perception/obstacle_cloud` | Topic / `robot_perception_interfaces/msg/ObstacleCloud` | Perception → Motion | **产品预留**；Demo 不部署、不订阅、不依赖 |
| P-04 | `/perception/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Perception → Autonomy | `Q_LATCHED`；故障立即 `ready=false`；变化立即发；稳定 1 Hz |

### 5.3 Motion 提供

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| P-NAV-01 | `/odom` | Topic / `nav_msgs/msg/Odometry` | Motion → Perception、Autonomy | Navigation/Motion 发布融合里程计；50 Hz；最大年龄 200 ms；Perception 可用于定位/视觉时空对齐；**最终停稳证据** |
| P-NAV-02 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | Motion → Perception、Autonomy | map→odom 定位边唯一发布者为 Navigation/Motion；/tf 按坐标边判唯一性 |
| N-01 | `/navigation/navigate_to_pose` | Action / `robot_motion_interfaces/action/NavigateToPoseTask` | Autonomy ⇄ Motion | `target_name + map_version` 由 Motion 通过语义地图解析为 Nav2 目标；真实调用 Nav2；最多总调用三次 |
| N-04 | `/rt/base/cmd_vel` | Topic / `geometry_msgs/msg/Twist` | Motion → RT-Control | 当前唯一底盘速度入口；20～50 Hz；500 ms 本地接收超时；不与旧 `/cmd_vel_safe` 或未来第二 writer 并行生效 |
| N-05 | `/navigation/localization/status` | Topic / `robot_motion_interfaces/msg/LocalizationStatus` | Motion → Autonomy | 发布者唯一；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic / `robot_motion_interfaces/msg/LandmarkArray` | Motion → Perception、Autonomy、外部/本地入口 | 当前语义地图地标列表；按 map_version 区分地图版本 |
| N-11 | `/navigation/semanticmap/add_landmark` | Service / `robot_motion_interfaces/srv/AddLandmark` | Perception、外部/本地入口 ⇄ Motion | 按指定位姿新增语义地标；返回 used_map_version 与最终地标 |
| N-12 | `/navigation/semanticmap/add_current_landmark` | Service / `robot_motion_interfaces/srv/AddCurrentLandmark` | Perception、外部/本地入口 ⇄ Motion | 以当前 base_footprint 位姿新增语义地标；返回 used_map_version 与最终地标 |
| N-13 | `/navigation/semanticmap/update_landmark` | Service / `robot_motion_interfaces/srv/UpdateLandmark` | Perception、外部/本地入口 ⇄ Motion | 更新语义地标属性和位姿；返回 used_map_version 与最终地标 |
| N-14 | `/navigation/semanticmap/remove_landmark` | Service / `robot_motion_interfaces/srv/RemoveLandmark` | Perception、外部/本地入口 ⇄ Motion | 按 name 删除指定 map_version 内的语义地标 |
| N-15 | `/navigation/semanticmap/get_landmark` | Service / `robot_motion_interfaces/srv/GetLandmark` | Perception、Autonomy、外部/本地入口 ⇄ Motion | 按 target_name 查询语义地标；N-01 服务端用它解析导航目标 |
| N-16 | `/navigation/semanticmap/get_map` | Service / `robot_motion_interfaces/srv/GetSemanticMap` | Perception、Autonomy、外部/本地入口 ⇄ Motion | 查询指定 map_version 下全部语义地标 |
| N-17 | `/navigation/mapping/set_turn_state` | Service / `robot_motion_interfaces/srv/SetMappingTurnState` | Autonomy、外部/本地入口 ⇄ Motion | 转台运动前 BEGIN_TURN 必须先暂停 FAST-LIO 到底盘的融合输入；停稳后同 caller_id、turn_sequence 的 TURN_COMPLETE 仅在实时 base_footprint←LiDAR TF 新鲜且连续稳定满配置窗口时切换固定外参，丢弃切换前排队里程计并恢复融合；乱序、并发事务或调用者不一致必须拒绝 |
| M-08 | `/motion/execute_stage` | Action / `robot_motion_interfaces/action/ExecuteMotionStage` | Autonomy ⇄ Motion | 单一串行阶段 Action；无活动抓取流程时 TURN/CAMERA_VIEW/NAMED_JOINT_POSE 可任意独立触发；抓取流程固定 PREGRASP→APPROACH→PLACE→HOME，活动期间禁止独立任务、并发、跳步和提前触发 |
| M-09 | `/rt/arms/rolling/target_batch` | Topic / `robot_motion_interfaces/msg/RollingJointTargetBatch` | Motion → RT-Control | 仅在 /rt/arms/set_control_mode 切到 ROLLING_READY 后生效；epoch 等于 R-OUT-07 当前 epoch；sequence 在同一 epoch 内严格递增；replace_from 为 ROS 时间（运控与 RT-Control 同机），不早于当前时刻 + 替换提前量；首点 time_from_start=0，位置与速度在拼接容差内等于缓冲轨迹在 replace_from 处的值；点时间严格递增，1～256 点，总长不超过缓冲上限；位置/速度/加速度不超过 robot_description 关节限位，且从任一点起都能在限值内停住；不满足整批拒绝，结果见 R-OUT-07 last_result；超过更新超时未收到有效批次，或缓冲耗尽时按限值刹停并保持；best-effort/volatile/keep-last(1)，deadline/lifespan 100 ms |
| M-06 | `/motion/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 机械能力准入；变化立即发；稳定 1 Hz |
| N-06 | `/navigation/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 导航执行能力准入；变化立即发；稳定 1 Hz |

### 5.4 RT-Control 输入

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-IN-02 | `/rt/arms/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 完整三代双臂 7+7 轴；位置 rad、速度 rad/s；不包含 turn/updown 或 PP；`allow_partial_joints_goal=false`；整组取消。准入（RT-Control 实时侧）：每点必须带速度、末点速度为 0；首点时间为 0 时距实测位置 ≤ 1°，首点在未来时距实测位置 ≤ 速度上限×首点时间；各点速度与每段平均速度 ≤ 速度上限；每段三次插值加速度（含从上一条指令接入首点的一段）≤ 加速度上限；上限取自 robot_description（双臂 30°/s、60°/s²）；不满足整条拒绝 |
| R-IN-02L | `/rt/arms/left/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 仅单臂作用域提供；left_joint1..7；位置 rad、速度 rad/s；`allow_partial_joints_goal=false`；整组取消；双臂作用域只提供 R-IN-02 |
| R-IN-02R | `/rt/arms/right/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 仅单臂作用域提供；right_joint1..7；其余同 R-IN-02L |
| R-IN-22 | `/rt/arms/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 完整三代双臂 7+7 轴；位置 rad、速度 rad/s；准入同 R-IN-02；用 header.stamp 标注首点时间基准；末点速度必须为 0；控制器从上一条指令接续新轨迹；与 R-IN-02 并发时以最后到达者为准（执行中的 action 目标被中止） |
| R-IN-22L | `/rt/arms/left/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 仅单臂作用域提供；left_joint1..7；其余同 R-IN-22 |
| R-IN-22R | `/rt/arms/right/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 仅单臂作用域提供；right_joint1..7；其余同 R-IN-22 |
| R-IN-18 | `/rt/enable` | Service / `robot_rt_control_interfaces/srv/RtEnable` | 外部/本地入口 ⇄ RT-Control | 按使能策略分批使能全部受管驱动与握手设备并激活运动控制器；失败时返回失败批次、关节、状态字、阶段与 DREE 错误；不复位急停、安全继电器或 STO |
| R-IN-19 | `/rt/disable` | Service / `robot_rt_control_interfaces/srv/RtEnable` | 外部/本地入口 ⇄ RT-Control | 停用运动控制器后有序失能全部受管设备；已失能时直接成功 |
| R-IN-20 | `/rt/reset_fault` | Service / `robot_rt_control_interfaces/srv/RtEnable` | 外部/本地入口 ⇄ RT-Control | 对作用域内全部故障设备做一次组复位；任一从站不在 OP 或反馈过期时拒绝（device_offline）；需要重启时拒绝（restart_required）；不使能 |
| R-IN-21 | `/rt/run_self_check` | Service / `std_srvs/srv/Trigger` | 外部/本地入口 ⇄ RT-Control | 用最新一组设备状态重跑启动自检规则；success=false 表示有阻断项；message 给出阻断/警告数量；不写总线、不改变使能状态 |
| R-IN-04 | `/rt/vacuum/pump/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetEnabled` | Autonomy ⇄ RT-Control | Autonomy 设置共用泵目标状态；普通停泵要求左右阀回读有效且为释放、左右压力有效且 >= -1 kPa、无活动阀操作；检查与执行期间阻止新吸附；enabled 为输出回读，输出未确认或未知时 accepted=false 并在 error 给出原因 |
| R-IN-05L | `/rt/vacuum/left_valve/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetEnabled` | Motion ⇄ RT-Control | enabled=true 吸附、false 释放；输出回读确认即返回 accepted=true，不等待建立真空；同侧忙拒绝；RT 不自动重试；输出未确认或未知时 accepted=false 并在 error 给出原因 |
| R-IN-05R | `/rt/vacuum/right_valve/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetEnabled` | Motion ⇄ RT-Control | 同 R-IN-05L，作用于右阀 |
| R-IN-06 | `/rt/arms/set_control_mode` | Service / `robot_rt_control_interfaces/srv/SetJointControlMode` | Motion ⇄ RT-Control | 仅在已使能且手臂静止时切换 FJT_READY/ROLLING_READY；切换前 Motion 取消并等待 R-IN-02 Action 终态；新控制器以当前位置保持起步；失败时 accepted=false 并给出 ErrorInfo，mode 为调用后的实际模式；歧义切换进入 RESTART_REQUIRED（见 R-OUT-09） |
| R-IN-12 | `/rt/led/set_rgbw` | Service / `robot_rt_control_interfaces/srv/SetLedRgbw` | Autonomy ⇄ RT-Control | 六路灯带完整 RGBW 设置；全零灭灯；响应只证明通信写确认，不证明实际发光；退出和重启不主动改色或重放 |
| R-IN-16 | `/rt/head/move` | Action / `robot_rt_control_interfaces/action/MoveHead` | Perception ⇄ RT-Control | 具名 head_joint/head_pitch_joint 弧度目标；同资源忙拒绝；取消停止并保持；旧 command topic 不允许外部并行写入 |

### 5.5 RT-Control 输出

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-OUT-01 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体动态坐标边唯一；`map→odom` 与 `odom→base_footprint` 不由本域发布 |
| R-OUT-01S | `/tf_static` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体固定坐标边唯一；`Q_LATCHED`；与 `/tf` 分开登记 |
| R-OUT-02 | `/rt/base/odom` | Topic / `nav_msgs/msg/Odometry` | RT-Control → Perception | `frame_id=odom`、`child_frame_id=base_footprint`；`Q_FAST_STATE`；50 Hz；**不作为到站或停稳最终证据** |
| R-OUT-03 | `/joint_states` | Topic / `sensor_msgs/msg/JointState` | RT-Control → Motion、Perception、Autonomy | 双臂、PP、升降、头部及底盘相关关节使用统一入口；不填伪造零值、不刷新旧样本时间、不把多模块拼成虚假同步快照 |
| R-OUT-04L | `/rt/battery/left/state` | Topic / `sensor_msgs/msg/BatteryState` | RT-Control → Autonomy | 左电池（BMS 地址 1）；BMS 周期 5 s（0.2 Hz）；只读，不作为业务控制入口 |
| R-OUT-04R | `/rt/battery/right/state` | Topic / `sensor_msgs/msg/BatteryState` | RT-Control → Autonomy | 右电池（BMS 地址 2）；BMS 周期 5 s（0.2 Hz）；只读，不作为业务控制入口 |
| R-OUT-05L | `/rt/vacuum/left/pressure` | Topic / `sensor_msgs/msg/FluidPressure` | RT-Control → Motion、Autonomy | 左侧真空表压，单位 Pa，负值为真空（偏离 FluidPressure 标准的绝压定义）；p<=-60000 Pa 为建立、p>=-1000 Pa 为释放，由消费方按此阈值判定；stamp 为样本时间；通信失败停发，由 R-OUT-20 报错 |
| R-OUT-05R | `/rt/vacuum/right/pressure` | Topic / `sensor_msgs/msg/FluidPressure` | RT-Control → Motion、Autonomy | 右侧真空表压，单位 Pa，负值为真空（偏离 FluidPressure 标准的绝压定义）；p<=-60000 Pa 为建立、p>=-1000 Pa 为释放，由消费方按此阈值判定；stamp 为样本时间；通信失败停发，由 R-OUT-20 报错 |
| R-OUT-19A | `/rt/ultrasonic/channel1/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 米制距离；通信失败停发并由状态接口立即报错；年龄超过 2.5 s 过期；无目标 +Inf，协议异常 NaN |
| R-OUT-19B | `/rt/ultrasonic/channel2/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19C | `/rt/ultrasonic/channel3/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19D | `/rt/ultrasonic/channel4/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19E | `/rt/ultrasonic/channel5/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 米制距离；第二 E08 独立发布，第一模块失败不得阻止本侧；其余同 R-OUT-19A |
| R-OUT-19F | `/rt/ultrasonic/channel6/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-19G | `/rt/ultrasonic/channel7/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-19H | `/rt/ultrasonic/channel8/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-20 | `/rt/sensors/state` | Topic / `robot_rt_control_interfaces/msg/SensorStatusArray` | RT-Control → Motion、Autonomy | 逐传感器声明有效、无目标、协议异常、通信错误、过期或未配置；每项保留真实样本时间，数组发布时间不刷新旧观测 |
| R-OUT-21 | `/rt/infrared/state` | Topic / `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control → Autonomy | 手臂红外只表示目标检测开关量；逐通道标识、原始电平、语义状态和有效性；未知不得当成未检测，不直接触发运动停止 |
| R-OUT-22 | `/rt/imu/data` | Topic / `sensor_msgs/msg/Imu` | RT-Control → Motion | 当前 Navigation 职责由 motion 域消费；SI 单位；时间为主机发布/接收链语义，不声明设备同步；无效拼接不重发旧测量；独立磁场不公开 |
| R-OUT-23L | `/rt/force_torque/left_wrist/wrench` | Topic / `geometry_msgs/msg/WrenchStamped` | RT-Control → Motion | 左传感器坐标系、N/Nm、经设备标定与单位换算；不做工具/箱子重力补偿、不自动调零；配置未闭合时不可宣称有效 |
| R-OUT-23R | `/rt/force_torque/right_wrist/wrench` | Topic / `geometry_msgs/msg/WrenchStamped` | RT-Control → Motion | 右传感器坐标系、N/Nm、经设备标定与单位换算；不做工具/箱子重力补偿、不自动调零；配置未闭合时不可宣称有效 |
| R-OUT-07 | `/rt/arms/rolling/state` | Topic / `robot_rt_control_interfaces/msg/RollingJointControlState` | RT-Control → Motion | 每次激活 epoch 加 1；state 为 HOLDING/RUNNING/STOPPING；last_sequence/last_result 只报本 epoch 最新收到的批次；stop_reason 为本 epoch 最近一次停止原因；reliable/volatile/keep-last(5)，deadline 100 ms、lifespan 200 ms |
| R-OUT-09 | `/rt/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | RT-Control → Autonomy | ready 表示 RT-Control 当前能接收指令：未使能、控制器或硬件未激活、设备离线或故障锁存均为 false，blockers 给出稳定标记；变化立即发；稳定 1 Hz |
| R-OUT-28 | `/rt/capabilities` | Topic / `std_msgs/msg/String` | RT-Control → 外部/本地入口 | JSON 对象：schema_version=1、control_scope、use_mock_hardware、capabilities（本作用域提供的能力名列表）、hardware；作用域启动时发布一次 |
| R-OUT-10 | `/diagnostics` | Topic / `diagnostic_msgs/msg/DiagnosticArray` | RT-Control → 外部/本地入口 | `Q_DIAGNOSTIC`；不替代 Action Result、readiness 或硬安全链 |
