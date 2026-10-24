<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Motion 域接口视图

> 契约版本：1.0.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Motion 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（17 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Perception、Autonomy | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Autonomy | ROS 标准类型；map → odom 由 Navigation/Motion 发布；Perception 通过 TF 查询 map→odom |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_motion_interfaces/action/NavigateToPoseTask` | Autonomy | — |
| N-04 | `/cmd_vel` | Topic | `geometry_msgs/msg/Twist` | RT-Control | Q_CONTROL；20～50 Hz；看门狗 500 ms；ROS 标准类型；当前 Navigation 职责由 motion 域承载；Twist 无 header，看门狗只使用 RT 本地接收间隔；后续 Motion 接管底盘另立协议 |
| N-05 | `/navigation/localization/status` | Topic | `robot_motion_interfaces/msg/LocalizationStatus` | Autonomy | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic | `robot_motion_interfaces/msg/LandmarkArray` | Perception、Autonomy、外部/本地入口 | Q_STATE |
| N-11 | `/navigation/semanticmap/add_landmark` | Service | `robot_motion_interfaces/srv/AddLandmark` | Perception、外部/本地入口 | — |
| N-12 | `/navigation/semanticmap/add_current_landmark` | Service | `robot_motion_interfaces/srv/AddCurrentLandmark` | Perception、外部/本地入口 | — |
| N-13 | `/navigation/semanticmap/update_landmark` | Service | `robot_motion_interfaces/srv/UpdateLandmark` | Perception、外部/本地入口 | — |
| N-14 | `/navigation/semanticmap/remove_landmark` | Service | `robot_motion_interfaces/srv/RemoveLandmark` | Perception、外部/本地入口 | — |
| N-15 | `/navigation/semanticmap/get_landmark` | Service | `robot_motion_interfaces/srv/GetLandmark` | Perception、Autonomy、外部/本地入口 | — |
| N-16 | `/navigation/semanticmap/get_map` | Service | `robot_motion_interfaces/srv/GetSemanticMap` | Perception、Autonomy、外部/本地入口 | — |
| N-17 | `/navigation/mapping/set_turn_state` | Service | `robot_motion_interfaces/srv/SetMappingTurnState` | Autonomy、外部/本地入口 | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 Turn 边界，保留既有协议；不是 V3 底盘接管或同步运动接口；turn_sequence 单调递增，同一 BEGIN_TURN/TURN_COMPLETE 重试幂等 |
| M-08 | `/motion/execute_stage` | Action | `robot_motion_interfaces/action/ExecuteMotionStage` | Autonomy | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 分阶段机械动作：12臂轴与Turn/Updown；保留供旧消费者迁移，不是 V3 双七轴或新抓放流程；不得通过旧流程调用已退役 VacuumGrip |
| M-09 | `/rt/rolling_joint_control/update` | Topic | `robot_motion_interfaces/msg/RollingJointTargetBatch` | RT-Control | Q_ROLLING_COMMAND；30 Hz；三代双七轴：right_joint1..7 后接 left_joint1..7；全部 rad/rad/s；完整 future suffix，非运动臂仍须包含 |
| M-06 | `/motion/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |

## 本域消费（26 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-03 | `/perception/obstacle_cloud` | Topic | `robot_perception_interfaces/msg/ObstacleCloud` | Perception | Q_STATE；**产品预留，Demo 不部署** |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action | `control_msgs/action/FollowJointTrajectory` | RT-Control | ROS 标准类型；三代双七轴 right_joint1..7,left_joint1..7；完整 14 轴；allow_partial_joints_goal=false |
| R-IN-18 | `/control/set_chassis_align_first` | Service | `std_srvs/srv/SetBool` | RT-Control | ROS 标准类型 |
| R-OUT-28 | `/rt_control/chassis/align_first` | Topic | `std_msgs/msg/Bool` | RT-Control | Q_LATCHED；1 Hz；ROS 标准类型 |
| R-IN-05 | `/vacuum/valves/set` | Action | `robot_rt_control_interfaces/action/SetVacuumValves` | RT-Control | — |
| R-IN-06 | `/rt/joint_control/set_mode` | Service | `robot_rt_control_interfaces/srv/SetJointControlMode` | RT-Control | — |
| R-IN-07 | `/rt/rolling_joint_control/open` | Service | `robot_rt_control_interfaces/srv/OpenRollingJointSession` | RT-Control | 三代 right_joint1..7,left_joint1..7；hold_positions 全部 rad、hold_velocities 全部 rad/s；拒绝旧轴哈希 |
| R-IN-09 | `/rt/rolling_joint_control/close` | Service | `robot_rt_control_interfaces/srv/CloseRollingJointSession` | RT-Control | — |
| R-IN-13 | `/pp/left/move` | Action | `robot_rt_control_interfaces/action/MoveAxis` | RT-Control | — |
| R-IN-14 | `/pp/right/move` | Action | `robot_rt_control_interfaces/action/MoveAxis` | RT-Control | — |
| R-IN-15 | `/updown/move` | Action | `robot_rt_control_interfaces/action/MoveAxis` | RT-Control | — |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；ROS 标准类型；整机各受管模块按真实采样时间发布不重叠关节子集；一关节一个权威来源；有效性与时效由模块状态配套表达 |
| R-OUT-05 | `/vacuum/state` | Topic | `robot_rt_control_interfaces/msg/VacuumState` | RT-Control | Q_STATE；20～50 Hz |
| R-OUT-18 | `/vacuum/events` | Topic | `robot_rt_control_interfaces/msg/VacuumStateEvent` | RT-Control | Q_STATE |
| R-OUT-20 | `/rt_control/sensors/status` | Topic | `robot_rt_control_interfaces/msg/SensorStatusArray` | RT-Control | Q_STATE |
| R-OUT-22 | `/imu/data` | Topic | `sensor_msgs/msg/Imu` | RT-Control | Q_FAST_STATE；ROS 标准类型 |
| R-OUT-23L | `/rt_control/left_wrist/wrench` | Topic | `geometry_msgs/msg/WrenchStamped` | RT-Control | Q_FAST_STATE；ROS 标准类型 |
| R-OUT-23R | `/rt_control/right_wrist/wrench` | Topic | `geometry_msgs/msg/WrenchStamped` | RT-Control | Q_FAST_STATE；ROS 标准类型 |
| R-OUT-24 | `/rt_control/modules/state` | Topic | `robot_rt_control_interfaces/msg/ModuleStateArray` | RT-Control | Q_LATCHED |
| R-OUT-25 | `/rt_control/motion/state` | Topic | `robot_rt_control_interfaces/msg/MotionExecutionState` | RT-Control | Q_STATE |
| R-OUT-26 | `/protective_stop/state` | Topic | `robot_rt_control_interfaces/msg/ProtectiveStopState` | RT-Control | Q_LATCHED |
| R-OUT-27 | `/edge/state` | Topic | `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control | Q_STATE |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_rt_control_interfaces/msg/SafetyState` | RT-Control | Q_STATE；10～50 Hz；最大年龄 200 ms |
| R-OUT-07 | `/rt/rolling_joint_control/state` | Topic | `robot_rt_control_interfaces/msg/RollingJointControlState` | RT-Control | Q_ROLLING_STATE；50 Hz；最大年龄 200 ms；三代双七轴 right_joint1..7,left_joint1..7；desired_positions rad、desired_velocities rad/s；axis_set_hash 与 open 一致 |

## 本域禁止的通信边

- 不得访问 `/vacuum/pump/set_enabled`
- 不得访问 `/led/set_rgbw`

## 已删除的 endpoint

出现在 ROS graph 中即为违约：

- `/cmd_vel_safe`
- `/vacuum/grip`
- `/led0/color`
- `/led1/color`
- `/led2/color`
- `/led3/color`
- `/led4/color`
- `/led5/color`
- `/head_position_controller/commands`
- `/navigation/set_base_motion_inhibit`
- `/robot_model/info`
- `/calibration/info`
- `/navigation/base_motion_gate_state`
- `/motion/base_travel_readiness`
- `/map`
- `/navigation/scan`
- `/motion/move_to_camera_view_pose`
- `/motion/plan_and_execute_pick`
- `/motion/plan_and_execute_place`
