<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Motion 域接口视图

> 契约版本：0.6.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Motion 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（7 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_motion_interfaces/action/NavigateToPoseTask` | Autonomy | — |
| N-04 | `/cmd_vel_safe` | Topic | `geometry_msgs/msg/Twist` | RT-Control | Q_CONTROL；20～50 Hz；看门狗 500 ms；ROS 标准类型；Twist 无 header；看门狗只用本地接收间隔，不得推导 stamp 或 frame |
| M-01 | `/motion/move_to_camera_view_pose` | Action | `robot_motion_interfaces/action/MoveToCameraViewPose` | Autonomy | — |
| M-02 | `/motion/plan_and_execute_pick` | Action | `robot_motion_interfaces/action/PlanAndExecutePick` | Autonomy | — |
| M-03 | `/motion/plan_and_execute_place` | Action | `robot_motion_interfaces/action/PlanAndExecutePlace` | Autonomy | — |
| M-06 | `/motion/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |

## 本域消费（12 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-03 | `/perception/obstacle_cloud` | Topic | `robot_perception_interfaces/msg/ObstacleCloud` | Perception | Q_STATE；**产品预留，Demo 不部署** |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Perception | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception | ROS 标准类型；map → odom，唯一发布者为 Perception |
| N-05 | `/navigation/localization/status` | Topic | `robot_perception_interfaces/msg/LocalizationStatus` | Perception | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-07 | `/map` | Topic | `nav_msgs/msg/OccupancyGrid` | Perception | Q_LATCHED；ROS 标准类型 |
| N-09 | `/navigation/scan` | Topic | `sensor_msgs/msg/LaserScan` | Perception | Q_FAST_STATE；ROS 标准类型 |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action | `control_msgs/action/FollowJointTrajectory` | RT-Control | ROS 标准类型；完整 14 轴；allow_partial_joints_goal=false |
| R-IN-05 | `/vacuum/grip` | Action | `robot_rt_control_interfaces/action/VacuumGrip` | RT-Control | — |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 200 ms；ROS 标准类型；只含 14 个 EtherCAT 机械轴，不含履带控制关节 |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_rt_control_interfaces/msg/SafetyState` | RT-Control | Q_STATE；10～50 Hz；最大年龄 200 ms |

## 已删除的 endpoint

出现在 ROS graph 中即为违约：

- `/navigation/set_base_motion_inhibit`
- `/robot_model/info`
- `/calibration/info`
- `/navigation/base_motion_gate_state`
- `/motion/base_travel_readiness`
