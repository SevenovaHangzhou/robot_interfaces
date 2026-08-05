<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Autonomy 域接口视图

> 契约版本：0.4.0
> 事实源：`contract/endpoints.yaml`
> 权威语义：`robot_system/docs/cross-domain-interfaces.md`

本文只列 Autonomy 域**产出**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域产出（1 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| G-01 | `/autonomy/execute_demo_task` | Action | `robot_task_interfaces/action/ExecuteDemoTask` | 外部/本地入口 | — |

## 本域消费（18 条）

| ID | ROS 名称 | 形式 | 类型 | 生产方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-01 | `/perception/build_wall_task_plan` | Action | `robot_task_interfaces/action/BuildWallTaskPlan` | Perception | — |
| P-02 | `/perception/refine_sequence_poses` | Action | `robot_task_interfaces/action/RefineSequencePoses` | Perception | — |
| P-04 | `/perception/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Perception | Q_LATCHED；1 Hz |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Perception | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception | ROS 标准类型；map → odom，唯一发布者为 Perception |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_navigation_interfaces/action/NavigateToPoseTask` | Motion | — |
| N-05 | `/navigation/localization/status` | Topic | `robot_navigation_interfaces/msg/LocalizationStatus` | Perception | Q_STATE；10～20 Hz；最大年龄 200 ms |
| M-01 | `/motion/move_to_camera_view_pose` | Action | `robot_task_interfaces/action/MoveToCameraViewPose` | Motion | — |
| M-02 | `/motion/plan_and_execute_pick` | Action | `robot_task_interfaces/action/PlanAndExecutePick` | Motion | — |
| M-03 | `/motion/plan_and_execute_place` | Action | `robot_task_interfaces/action/PlanAndExecutePlace` | Motion | — |
| M-06 | `/motion/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Motion | Q_LATCHED；1 Hz |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Motion | Q_LATCHED；1 Hz |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态与静态 TF（含 /tf_static） |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型；只含 14 个 EtherCAT 机械轴，不含履带控制关节 |
| R-OUT-04 | `/battery_state` | Topic | `sensor_msgs/msg/BatteryState` | RT-Control | Q_STATE；0.2 Hz；ROS 标准类型；BMS 周期 5 s；只读，不作为业务控制入口 |
| R-OUT-05 | `/vacuum/state` | Topic | `robot_control_interfaces/msg/VacuumState` | RT-Control | Q_STATE；20～50 Hz |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_control_interfaces/msg/SafetyState` | RT-Control | Q_STATE；10～50 Hz；最大年龄 200 ms |
| R-OUT-09 | `/rt_control/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | RT-Control | Q_LATCHED；1 Hz |

## 本域禁止的通信边

- 不得访问 `/cmd_vel_safe`
- 不得访问 `/whole_body_jtc/follow_joint_trajectory`
- 不得访问 `/control/set_enabled`
- 不得访问 `/vacuum/pump/set_enabled`
- 不得访问 `/vacuum/grip`

## 已删除的 endpoint

出现在 ROS graph 中即为违约：

- `/navigation/set_base_motion_inhibit`
- `/robot_model/info`
- `/calibration/info`
- `/navigation/base_motion_gate_state`
- `/motion/base_travel_readiness`
