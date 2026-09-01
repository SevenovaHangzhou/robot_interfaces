<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Motion 域接口视图

> 契约版本：0.7.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Motion 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（16 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Perception、Autonomy | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Autonomy | ROS 标准类型；map → odom 由 Navigation/Motion 发布；Perception 通过 TF 查询 map→odom |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_motion_interfaces/action/NavigateToPoseTask` | Autonomy | — |
| N-04 | `/cmd_vel_safe` | Topic | `geometry_msgs/msg/Twist` | RT-Control | Q_CONTROL；20～50 Hz；看门狗 500 ms；ROS 标准类型；Twist 无 header；看门狗只用本地接收间隔，不得推导 stamp 或 frame |
| N-05 | `/navigation/localization/status` | Topic | `robot_motion_interfaces/msg/LocalizationStatus` | Autonomy | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic | `robot_motion_interfaces/msg/LandmarkArray` | Perception、Autonomy、外部/本地入口 | Q_STATE |
| N-11 | `/navigation/semanticmap/add_landmark` | Service | `robot_motion_interfaces/srv/AddLandmark` | Perception、外部/本地入口 | — |
| N-12 | `/navigation/semanticmap/add_current_landmark` | Service | `robot_motion_interfaces/srv/AddCurrentLandmark` | Perception、外部/本地入口 | — |
| N-13 | `/navigation/semanticmap/update_landmark` | Service | `robot_motion_interfaces/srv/UpdateLandmark` | Perception、外部/本地入口 | — |
| N-14 | `/navigation/semanticmap/remove_landmark` | Service | `robot_motion_interfaces/srv/RemoveLandmark` | Perception、外部/本地入口 | — |
| N-15 | `/navigation/semanticmap/get_landmark` | Service | `robot_motion_interfaces/srv/GetLandmark` | Perception、Autonomy、外部/本地入口 | — |
| N-16 | `/navigation/semanticmap/get_map` | Service | `robot_motion_interfaces/srv/GetSemanticMap` | Perception、Autonomy、外部/本地入口 | — |
| N-17 | `/navigation/mapping/set_turn_state` | Service | `robot_motion_interfaces/srv/SetMappingTurnState` | Autonomy、外部/本地入口 | 只用于固定 LiDAR 外参建图模式；turn_sequence 由调用方单调递增，同一 BEGIN_TURN/TURN_COMPLETE 重试幂等 |
| M-08 | `/motion/execute_stage` | Action | `robot_motion_interfaces/action/ExecuteMotionStage` | Autonomy | CAMERA_VIEW/PREGRASP Pose 固定表达在 base_link；TURN 目标单位 rad；命名姿态只改变双臂 12 轴并保持 Turn/Updown；真空吸放由 Autonomy 编排 RT-Control |
| M-06 | `/motion/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |

## 本域消费（6 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-03 | `/perception/obstacle_cloud` | Topic | `robot_perception_interfaces/msg/ObstacleCloud` | Perception | Q_STATE；**产品预留，Demo 不部署** |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action | `control_msgs/action/FollowJointTrajectory` | RT-Control | ROS 标准类型；完整 14 轴；allow_partial_joints_goal=false |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；125 Hz；最大年龄 200 ms；ROS 标准类型；只含 14 个 EtherCAT 机械轴，不含履带控制关节；250 Hz controller_manager 将配置的 100 Hz 量化为实测 125 Hz |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_rt_control_interfaces/msg/SafetyState` | RT-Control | Q_STATE；10～50 Hz；最大年龄 200 ms |

## 本域禁止的通信边

- 不得访问 `/vacuum/grip`

## 已删除的 endpoint

出现在 ROS graph 中即为违约：

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
