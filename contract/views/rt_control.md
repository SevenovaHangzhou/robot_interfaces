<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# RT-Control 域接口视图

> 契约版本：0.7.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 RT-Control 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（17 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action | `control_msgs/action/FollowJointTrajectory` | Motion | ROS 标准类型；完整 14 轴；allow_partial_joints_goal=false |
| R-IN-03 | `/control/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetControlEnabled` | 外部/本地入口 | — |
| R-IN-04 | `/vacuum/pump/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetPumpEnabled` | 外部/本地入口 | — |
| R-IN-05 | `/vacuum/grip` | Action | `robot_rt_control_interfaces/action/VacuumGrip` | Autonomy | — |
| R-IN-06 | `/rt/joint_control/set_mode` | Service | `robot_rt_control_interfaces/srv/SetJointControlMode` | Motion | — |
| R-IN-07 | `/rt/rolling_joint_control/open` | Service | `robot_rt_control_interfaces/srv/OpenRollingJointSession` | Motion | — |
| R-IN-09 | `/rt/rolling_joint_control/close` | Service | `robot_rt_control_interfaces/srv/CloseRollingJointSession` | Motion | — |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Motion、Autonomy | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Motion、Autonomy | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-02 | `/wheel/odom` | Topic | `nav_msgs/msg/Odometry` | Perception | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型；frame_id=odom，child_frame_id=base_footprint；rt-control 不发 odom→base_footprint TF |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | Motion、Perception、Autonomy | Q_FAST_STATE；125 Hz；最大年龄 200 ms；ROS 标准类型；只含 14 个 EtherCAT 机械轴，不含履带控制关节；250 Hz controller_manager 将配置的 100 Hz 量化为实测 125 Hz |
| R-OUT-04 | `/battery_state` | Topic | `sensor_msgs/msg/BatteryState` | Autonomy | Q_STATE；0.2 Hz；ROS 标准类型；BMS 周期 5 s；只读，不作为业务控制入口 |
| R-OUT-05 | `/vacuum/state` | Topic | `robot_rt_control_interfaces/msg/VacuumState` | Autonomy | Q_STATE；20～50 Hz |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_rt_control_interfaces/msg/SafetyState` | Perception、Motion、Autonomy | Q_STATE；10～50 Hz；最大年龄 200 ms |
| R-OUT-07 | `/rt/rolling_joint_control/state` | Topic | `robot_rt_control_interfaces/msg/RollingJointControlState` | Motion | Q_ROLLING_STATE；50 Hz；最大年龄 200 ms |
| R-OUT-09 | `/rt_control/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| R-OUT-10 | `/diagnostics` | Topic | `diagnostic_msgs/msg/DiagnosticArray` | 外部/本地入口 | Q_DIAGNOSTIC；ROS 标准类型；不得替代 Action Result、readiness 或 SafetyState 证据 |

## 本域消费（2 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| N-04 | `/cmd_vel_safe` | Topic | `geometry_msgs/msg/Twist` | Motion | Q_CONTROL；20～50 Hz；看门狗 500 ms；ROS 标准类型；Twist 无 header；看门狗只用本地接收间隔，不得推导 stamp 或 frame |
| M-09 | `/rt/rolling_joint_control/update` | Topic | `robot_motion_interfaces/msg/RollingJointTargetBatch` | Motion | Q_ROLLING_COMMAND；30 Hz；Motion 发布完整权威 future suffix；点间隔由 Motion 决定，本期约 100 ms |

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
