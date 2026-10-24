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
| N-04 | `/cmd_vel` | Topic / `geometry_msgs/msg/Twist` | Motion → RT-Control | 当前唯一底盘速度入口；20～50 Hz；500 ms 本地接收超时；不与旧 `/cmd_vel_safe` 或未来第二 writer 并行生效 |
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
| M-09 | `/rt/rolling_joint_control/update` | Topic / `robot_motion_interfaces/msg/RollingJointTargetBatch` | Motion → RT-Control | 协议 1.0 精确匹配；轴序/单位遵守 axis_sets.v3_dual_arm，不包含 turn/updown/PP/头部/底盘；sequence 非零且严格递增；replace_from_ns 与首点 session-relative 时间完全相等；points 非空且不超过 open 回报 capacity/传输上限 256；best-effort/volatile/keep-last(1)，deadline/lifespan 100 ms；DDS deadline 仅诊断，停止由 accepted-update age 与 low-water 决定 |
| M-06 | `/motion/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 机械能力准入；变化立即发；稳定 1 Hz |
| N-06 | `/navigation/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 导航执行能力准入；变化立即发；稳定 1 Hz |

### 5.4 RT-Control 输入

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 完整三代双臂 7+7 轴；位置 rad、速度 rad/s；不包含 turn/updown 或 PP；`allow_partial_joints_goal=false`；整组取消 |
| R-IN-03 | `/control/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetControlEnabled` | 外部/本地入口 ⇄ RT-Control | 不复位急停、安全继电器或 STO；不属于箱级任务流程 |
| R-IN-18 | `/control/set_chassis_align_first` | Service / `std_srvs/srv/SetBool` | Motion ⇄ RT-Control | data=true 为对齐模式，false 为连续模式；保持使能，仅在导航执行权有效、持续收到新鲜零速、四轮参考为零且有效实测轮速满足既有停稳窗口时切换；运动中拒绝，不自动停车或排队；success=true 仅在控制周期确认生效后返回；message 仅供人读；失败或超时后保持零速并核对 R-OUT-28，不推断是否改变；切换保留执行历史，不使能、不复位，应用时废弃已接收指令，后续以RT本地接收时间判新；调用方收到确认前持续零速；不持久化为启动默认值 |
| R-IN-04 | `/vacuum/pump/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetPumpEnabled` | Autonomy ⇄ RT-Control | Autonomy 设置共用泵目标状态；普通停泵要求左右阀回读有效且为释放、左右压力有效且 >= -1 kPa、无活动或结果未知阀操作；检查与执行期间阻止新吸附 |
| R-IN-05 | `/vacuum/valves/set` | Action / `robot_rt_control_interfaces/action/SetVacuumValves` | Motion ⇄ RT-Control | Motion 设置 left/right 或双侧吸附/释放；输出确认即完成，不等待吸附；同侧忙拒绝、双侧预检原子、部分成功不回退、request_id 仅追踪不去重、RT 不自动重试 |
| R-IN-06 | `/rt/joint_control/set_mode` | Service / `robot_rt_control_interfaces/srv/SetJointControlMode` | Motion ⇄ RT-Control | 协议 1.0 精确匹配；expected_mode 是 compare-and-set guard；Motion 在 FJT→rolling 前 cancel 并等待 Action 终态；admission 失败不得调用 controller_manager；同 client/request_id 幂等；STRICT 结果含 source/target controller 证据，歧义进入 RESTART_REQUIRED 且不自动重试 |
| R-IN-07 | `/rt/rolling_joint_control/open` | Service / `robot_rt_control_interfaces/srv/OpenRollingJointSession` | Motion ⇄ RT-Control | 仅 ROLLING_READY/NONE 可 open；协议、boot、axis_sets.v3_dual_arm 的14轴哈希、反馈新鲜度、source hold 与 limits 完整性 fail-closed 校验；任何不同轴哈希必须在创建会话前返回 AXIS_SET_MISMATCH；同 client/request_id 幂等；返回 session/hold、limits source/version、capacity、horizon、replace lead、update timeout 与名义周期的实际生效值 |
| R-IN-09 | `/rt/rolling_joint_control/close` | Service / `robot_rt_control_interfaces/srv/CloseRollingJointSession` | Motion ⇄ RT-Control | 协议/boot/session/client 精确匹配；REQUEST_STOP 异步锁存 stopping，完成以 state=HOLDING 为准；HOLDING 后显式 FINALIZE 销毁 session；同 client/request_id 幂等；无公共 abrupt abort，disable/fault 走既有高优先级生命周期 |
| R-IN-12 | `/led/set_rgbw` | Service / `robot_rt_control_interfaces/srv/SetLedRgbw` | Autonomy ⇄ RT-Control | 六路灯带完整 RGBW 设置；全零灭灯；响应只证明通信写确认，不证明实际发光；退出和重启不主动改色或重放 |
| R-IN-13 | `/pp/left/move` | Action / `robot_rt_control_interfaces/action/MoveAxis` | Motion ⇄ RT-Control | 左 PP 米制绝对位置；同资源忙拒绝、无队列/抢占；取消后停止并保持，不自动张开 |
| R-IN-14 | `/pp/right/move` | Action / `robot_rt_control_interfaces/action/MoveAxis` | Motion ⇄ RT-Control | 右 PP 米制绝对位置；同资源忙拒绝、无队列/抢占；取消后停止并保持，不自动张开 |
| R-IN-15 | `/updown/move` | Action / `robot_rt_control_interfaces/action/MoveAxis` | Motion ⇄ RT-Control | 升降米制绝对关节位置；同资源忙拒绝；取消停止并保持，不下降、回零或直接失能；生产参数缺失时 fail closed |
| R-IN-16 | `/head/move` | Action / `robot_rt_control_interfaces/action/MoveHead` | Perception ⇄ RT-Control | 具名 head_joint/head_pitch_joint 弧度目标；同资源忙拒绝；取消停止并保持；旧 command topic 不允许外部并行写入 |
| R-IN-17 | `/protective_stop/reset` | Service / `robot_rt_control_interfaces/srv/ResetProtectiveStop` | Autonomy ⇄ RT-Control | 仅处理人工流程后的保护复位请求；RT 仍复核输入解除、数据有效、所需运动已停止和无阻塞故障；复位只恢复新命令准入 |

### 5.5 RT-Control 输出

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-OUT-28 | `/rt_control/chassis/align_first` | Topic / `std_msgs/msg/Bool` | RT-Control → Motion | 实际生效模式：true=align_first，false=steer_while_driving；切换时立即更新，稳定时1Hz；只表示模式，不表示使能、停稳或运动准入；消费者按本地接收时间检查新鲜度，重启后丢弃旧状态并等待新实例发布；重新configure或进程重启恢复部署默认模式 |
| R-OUT-01 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体动态坐标边唯一；`map→odom` 与 `odom→base_footprint` 不由本域发布 |
| R-OUT-01S | `/tf_static` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体固定坐标边唯一；`Q_LATCHED`；与 `/tf` 分开登记 |
| R-OUT-02 | `/wheel/odom` | Topic / `nav_msgs/msg/Odometry` | RT-Control → Perception | `frame_id=odom`、`child_frame_id=base_footprint`；`Q_FAST_STATE`；50 Hz；**不作为到站或停稳最终证据** |
| R-OUT-03 | `/joint_states` | Topic / `sensor_msgs/msg/JointState` | RT-Control → Motion、Perception、Autonomy | 双臂、PP、升降、头部及底盘相关关节使用统一入口；不填伪造零值、不刷新旧样本时间、不把多模块拼成虚假同步快照 |
| R-OUT-04 | `/battery_state` | Topic / `sensor_msgs/msg/BatteryState` | RT-Control → Autonomy | BMS 周期 5 s（0.2 Hz）；只读，不作为业务控制入口 |
| R-OUT-05 | `/vacuum/state` | Topic / `robot_rt_control_interfaces/msg/VacuumState` | RT-Control → Motion、Autonomy | 左右独立压力、阀输出回读、泵状态与样本有效性；p<=-60 kPa 为建立、p>=-1 kPa 为释放、中间态独立表达；单个有效新鲜样本立即分类 |
| R-OUT-18 | `/vacuum/events` | Topic / `robot_rt_control_interfaces/msg/VacuumStateEvent` | RT-Control → Motion、Autonomy | 发布左右真空分类变化和最近阀操作上下文；实例+序号标识事件；仅为信号变化证据，不声明箱子掉落或事件因果 |
| R-OUT-19A | `/ultrasonic/channel1/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 米制距离；通信失败停发并由状态接口立即报错；年龄超过 2.5 s 过期；无目标 +Inf，协议异常 NaN |
| R-OUT-19B | `/ultrasonic/channel2/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19C | `/ultrasonic/channel3/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19D | `/ultrasonic/channel4/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19E | `/ultrasonic/channel5/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 米制距离；第二 E08 独立发布，第一模块失败不得阻止本侧；其余同 R-OUT-19A |
| R-OUT-19F | `/ultrasonic/channel6/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-19G | `/ultrasonic/channel7/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-19H | `/ultrasonic/channel8/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-20 | `/rt_control/sensors/status` | Topic / `robot_rt_control_interfaces/msg/SensorStatusArray` | RT-Control → Motion、Autonomy | 逐传感器声明有效、无目标、协议异常、通信错误、过期或未配置；每项保留真实样本时间，数组发布时间不刷新旧观测 |
| R-OUT-21 | `/infrared/state` | Topic / `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control → Autonomy | 手臂红外只表示目标检测开关量；逐通道标识、原始电平、语义状态和有效性；未知不得当成未检测，不直接触发运动停止 |
| R-OUT-22 | `/imu/data` | Topic / `sensor_msgs/msg/Imu` | RT-Control → Motion | 当前 Navigation 职责由 motion 域消费；SI 单位；时间为主机发布/接收链语义，不声明设备同步；无效拼接不重发旧测量；独立磁场不公开 |
| R-OUT-23L | `/rt_control/left_wrist/wrench` | Topic / `geometry_msgs/msg/WrenchStamped` | RT-Control → Motion | 左传感器坐标系、N/Nm、经设备标定与单位换算；不做工具/箱子重力补偿、不自动调零；配置未闭合时不可宣称有效 |
| R-OUT-23R | `/rt_control/right_wrist/wrench` | Topic / `geometry_msgs/msg/WrenchStamped` | RT-Control → Motion | 右传感器坐标系、N/Nm、经设备标定与单位换算；不做工具/箱子重力补偿、不自动调零；配置未闭合时不可宣称有效 |
| R-OUT-24 | `/rt_control/modules/state` | Topic / `robot_rt_control_interfaces/msg/ModuleStateArray` | RT-Control → Perception、Motion、Autonomy | 分别表达安装、实现、启用、配置、数据和故障；未安装触边及未实现力控/换电不得伪报可用；不替代各能力 DomainReadiness.ready |
| R-OUT-25 | `/rt_control/motion/state` | Topic / `robot_rt_control_interfaces/msg/MotionExecutionState` | RT-Control → Perception、Motion、Autonomy | 按资源发布实际位置、执行、停止/保持和反馈有效性；只证明对应资源事实，不形成底盘与双臂/PP/升降的跨组互斥令牌 |
| R-OUT-26 | `/protective_stop/state` | Topic / `robot_rt_control_interfaces/msg/ProtectiveStopState` | RT-Control → Perception、Motion、Autonomy | 软件保护摘要，不代表硬安全链；触边未安装明确不可用；安装启用后触发、通信失效或过期停止约定范围并锁存 |
| R-OUT-27 | `/edge/state` | Topic / `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control → Perception、Motion、Autonomy | 逐通道触边输入；当前未安装不得伪造未触发；启用后的时效、地址和电平来自实物配置 |
| R-OUT-06 | `/control/safety_state` | Topic / `robot_rt_control_interfaces/msg/SafetyState` | RT-Control → Perception、Motion、Autonomy | **软件可观测摘要，不含硬安全链状态**；`Q_STATE`；10～50 Hz；最大年龄 200 ms；`safe_to_start_motion=false` 或过期时禁止新动作 |
| R-OUT-07 | `/rt/rolling_joint_control/state` | Topic / `robot_rt_control_interfaces/msg/RollingJointControlState` | RT-Control → Motion | 协议、boot/session/client、mode/session、generation/sequence、execution/replaceable/buffered/age、三代双臂 desired q/qdot、独立 RejectCode/StopReason、switch evidence 与 limits source 全量可观测；reliable/volatile/keep-last(5)，deadline 100 ms、lifespan 200 ms；published_at 仅诊断，不参与命令排序或采样 |
| R-OUT-09 | `/rt_control/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | RT-Control → Autonomy | 故障立即 `ready=false`；变化立即发；稳定 1 Hz |
| R-OUT-10 | `/diagnostics` | Topic / `diagnostic_msgs/msg/DiagnosticArray` | RT-Control → 外部/本地入口 | `Q_DIAGNOSTIC`；不替代 Action Result、SafetyState 或硬安全链 |
