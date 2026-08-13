<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Perception 域接口视图

> 契约版本：0.6.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Perception 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（9 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-01 | `/perception/build_wall_task_plan` | Action | `robot_perception_interfaces/action/BuildWallTaskPlan` | Autonomy | — |
| P-02 | `/perception/refine_sequence_poses` | Action | `robot_perception_interfaces/action/RefineSequencePoses` | Autonomy | — |
| P-03 | `/perception/obstacle_cloud` | Topic | `robot_perception_interfaces/msg/ObstacleCloud` | Motion | Q_STATE；**产品预留，Demo 不部署** |
| P-04 | `/perception/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Motion、Autonomy | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Motion、Autonomy | ROS 标准类型；map → odom，唯一发布者为 Perception |
| N-05 | `/navigation/localization/status` | Topic | `robot_perception_interfaces/msg/LocalizationStatus` | Motion、Autonomy | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-07 | `/map` | Topic | `nav_msgs/msg/OccupancyGrid` | Motion | Q_LATCHED；ROS 标准类型 |
| N-09 | `/navigation/scan` | Topic | `sensor_msgs/msg/LaserScan` | Motion | Q_FAST_STATE；ROS 标准类型 |

## 本域消费（5 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-02 | `/wheel/odom` | Topic | `nav_msgs/msg/Odometry` | RT-Control | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型；frame_id=odom，child_frame_id=base_footprint；rt-control 不发 odom→base_footprint TF |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 200 ms；ROS 标准类型；只含 14 个 EtherCAT 机械轴，不含履带控制关节 |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_rt_control_interfaces/msg/SafetyState` | RT-Control | Q_STATE；10～50 Hz；最大年龄 200 ms |

## 本域禁止的通信边

- 不得访问 `/navigation/navigate_to_pose`

## 已删除的 endpoint

出现在 ROS graph 中即为违约：

- `/navigation/set_base_motion_inhibit`
- `/robot_model/info`
- `/calibration/info`
- `/navigation/base_motion_gate_state`
- `/motion/base_travel_readiness`
- `/motion/move_to_camera_view_pose`
- `/motion/plan_and_execute_pick`
- `/motion/plan_and_execute_place`
