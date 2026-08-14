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
| P-01 | `/perception/build_wall_task_plan` | Action / `robot_perception_interfaces/action/BuildWallTaskPlan` | Autonomy ⇄ Perception | 真实单次同步采集；25 箱；固定 15 序列；箱 pose 为吸取表面接触位姿；每序列自带 `station_id`、统一 0.74 m 退避的 `station_nav_pose(map)`、按臂绑定重拍位；每个 G-01 只调用一次；严格成功 |
| P-02 | `/perception/refine_sequence_poses` | Action / `robot_perception_interfaces/action/RefineSequencePoses` | Autonomy ⇄ Perception | 同箱同序；返回吸取表面接触位姿；`base_link`；stamp=真实曝光时刻；底盘静止、TF、标定不变 |
| P-03 | `/perception/obstacle_cloud` | Topic / `robot_perception_interfaces/msg/ObstacleCloud` | Perception → Motion | **产品预留**；Demo 不部署、不订阅、不依赖 |
| P-04 | `/perception/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Perception → Autonomy | `Q_LATCHED`；故障立即 `ready=false`；变化立即发；稳定 1 Hz |

### 5.3 Motion 提供

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| P-NAV-01 | `/odom` | Topic / `nav_msgs/msg/Odometry` | Motion → Perception、Autonomy | Navigation/Motion 发布融合里程计；50 Hz；最大年龄 200 ms；Perception 可用于定位/视觉时空对齐；**最终停稳证据** |
| P-NAV-02 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | Motion → Perception、Autonomy | map→odom 定位边唯一发布者为 Navigation/Motion；/tf 按坐标边判唯一性 |
| N-01 | `/navigation/navigate_to_pose` | Action / `robot_motion_interfaces/action/NavigateToPoseTask` | Autonomy ⇄ Motion | `target_name + map_version` 由 Motion 通过语义地图解析为 Nav2 目标；真实调用 Nav2；最多总调用三次 |
| N-04 | `/cmd_vel_safe` | Topic / `geometry_msgs/msg/Twist` | Motion → RT-Control | 见 R-IN-01；Motion 是唯一生产者 |
| N-05 | `/navigation/localization/status` | Topic / `robot_motion_interfaces/msg/LocalizationStatus` | Motion → Autonomy | 发布者唯一；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic / `robot_motion_interfaces/msg/LandmarkArray` | Motion → Perception、Autonomy、外部/本地入口 | 当前语义地图地标列表；按 map_version 区分地图版本 |
| N-11 | `/navigation/semanticmap/add_landmark` | Service / `robot_motion_interfaces/srv/AddLandmark` | Perception、外部/本地入口 ⇄ Motion | 按指定位姿新增语义地标；返回 used_map_version 与最终地标 |
| N-12 | `/navigation/semanticmap/add_current_landmark` | Service / `robot_motion_interfaces/srv/AddCurrentLandmark` | Perception、外部/本地入口 ⇄ Motion | 以当前 base_footprint 位姿新增语义地标；返回 used_map_version 与最终地标 |
| N-13 | `/navigation/semanticmap/update_landmark` | Service / `robot_motion_interfaces/srv/UpdateLandmark` | Perception、外部/本地入口 ⇄ Motion | 更新语义地标属性和位姿；返回 used_map_version 与最终地标 |
| N-14 | `/navigation/semanticmap/remove_landmark` | Service / `robot_motion_interfaces/srv/RemoveLandmark` | Perception、外部/本地入口 ⇄ Motion | 按 name 删除指定 map_version 内的语义地标 |
| N-15 | `/navigation/semanticmap/get_landmark` | Service / `robot_motion_interfaces/srv/GetLandmark` | Perception、Autonomy、外部/本地入口 ⇄ Motion | 按 target_name 查询语义地标；N-01 服务端用它解析导航目标 |
| N-16 | `/navigation/semanticmap/get_map` | Service / `robot_motion_interfaces/srv/GetSemanticMap` | Perception、Autonomy、外部/本地入口 ⇄ Motion | 查询指定 map_version 下全部语义地标 |
| M-08 | `/motion/execute_stage` | Action / `robot_motion_interfaces/action/ExecuteMotionStage` | Autonomy ⇄ Motion | 单一串行阶段 Action；CAMERA_VIEW 可选，其余固定 PREGRASP→APPROACH→PLACE→HOME；禁止并发、非法跳步和阶段重放 |
| M-06 | `/motion/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 机械能力准入；变化立即发；稳定 1 Hz |
| N-06 | `/navigation/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 导航执行能力准入；变化立即发；稳定 1 Hz |

### 5.4 RT-Control 输入

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 完整 14 轴；`allow_partial_joints_goal=false`；整组取消 |
| R-IN-03 | `/control/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetControlEnabled` | 外部/本地入口 ⇄ RT-Control | 不复位急停、安全继电器或 STO；不属于箱级任务流程 |
| R-IN-04 | `/vacuum/pump/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetPumpEnabled` | 外部/本地入口 ⇄ RT-Control | 活动真空命令或可能持箱时拒绝普通停泵 |
| R-IN-05 | `/vacuum/grip` | Action / `robot_rt_control_interfaces/action/VacuumGrip` | Autonomy ⇄ RT-Control | Autonomy 在 M-08 阶段之间编排；通道固定 `left/right` 且同数量/同集/同序；当前只接受 `grip_profile_id=default`；GRIP 每通道新鲜 `attached=true`；RELEASE 仍 `UNVERIFIED` |

### 5.5 RT-Control 输出

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-OUT-01 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体动态坐标边唯一；`map→odom` 与 `odom→base_footprint` 不由本域发布 |
| R-OUT-01S | `/tf_static` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体固定坐标边唯一；`Q_LATCHED`；与 `/tf` 分开登记 |
| R-OUT-02 | `/wheel/odom` | Topic / `nav_msgs/msg/Odometry` | RT-Control → Perception | `frame_id=odom`、`child_frame_id=base_footprint`；`Q_FAST_STATE`；50 Hz；**不作为到站或停稳最终证据** |
| R-OUT-03 | `/joint_states` | Topic / `sensor_msgs/msg/JointState` | RT-Control → Motion、Perception、Autonomy | 只含 14 个 EtherCAT 机械轴，不含履带关节；仅 position；`Q_FAST_STATE`；125 Hz |
| R-OUT-04 | `/battery_state` | Topic / `sensor_msgs/msg/BatteryState` | RT-Control → Autonomy | BMS 周期 5 s（0.2 Hz）；只读，不作为业务控制入口 |
| R-OUT-05 | `/vacuum/state` | Topic / `robot_rt_control_interfaces/msg/VacuumState` | RT-Control → Autonomy | `Q_STATE`；20～50 Hz；发布 `left/right` 新鲜 `attached` 布尔状态；只 RT-Control 用于 GRIP 判定；Motion 不订阅 |
| R-OUT-06 | `/control/safety_state` | Topic / `robot_rt_control_interfaces/msg/SafetyState` | RT-Control → Perception、Motion、Autonomy | **软件可观测摘要，不含硬安全链状态**；`Q_STATE`；10～50 Hz；最大年龄 200 ms；`safe_to_start_motion=false` 或过期时禁止新动作 |
| R-OUT-09 | `/rt_control/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | RT-Control → Autonomy | 故障立即 `ready=false`；变化立即发；稳定 1 Hz |
| R-OUT-10 | `/diagnostics` | Topic / `diagnostic_msgs/msg/DiagnosticArray` | RT-Control → 外部/本地入口 | `Q_DIAGNOSTIC`；不替代 Action Result、SafetyState 或硬安全链 |
