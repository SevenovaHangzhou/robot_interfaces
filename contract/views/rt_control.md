<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# RT-Control 域接口视图

> 契约版本：1.0.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 RT-Control 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（41 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| R-IN-02 | `/whole_body_jtc/follow_joint_trajectory` | Action | `control_msgs/action/FollowJointTrajectory` | Motion | ROS 标准类型；三代双七轴 right_joint1..7,left_joint1..7；完整 14 轴；allow_partial_joints_goal=false |
| R-IN-03 | `/control/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetControlEnabled` | 外部/本地入口 | — |
| R-IN-04 | `/vacuum/pump/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetPumpEnabled` | Autonomy | — |
| R-IN-05 | `/vacuum/valves/set` | Action | `robot_rt_control_interfaces/action/SetVacuumValves` | Motion | — |
| R-IN-06 | `/rt/joint_control/set_mode` | Service | `robot_rt_control_interfaces/srv/SetJointControlMode` | Motion | — |
| R-IN-07 | `/rt/rolling_joint_control/open` | Service | `robot_rt_control_interfaces/srv/OpenRollingJointSession` | Motion | 三代 right_joint1..7,left_joint1..7；hold_positions 全部 rad、hold_velocities 全部 rad/s；拒绝旧轴哈希 |
| R-IN-09 | `/rt/rolling_joint_control/close` | Service | `robot_rt_control_interfaces/srv/CloseRollingJointSession` | Motion | — |
| R-IN-12 | `/led/set_rgbw` | Service | `robot_rt_control_interfaces/srv/SetLedRgbw` | Autonomy | — |
| R-IN-13 | `/pp/left/move` | Action | `robot_rt_control_interfaces/action/MoveAxis` | Motion | — |
| R-IN-14 | `/pp/right/move` | Action | `robot_rt_control_interfaces/action/MoveAxis` | Motion | — |
| R-IN-15 | `/updown/move` | Action | `robot_rt_control_interfaces/action/MoveAxis` | Motion | — |
| R-IN-16 | `/head/move` | Action | `robot_rt_control_interfaces/action/MoveHead` | Perception | — |
| R-IN-17 | `/protective_stop/reset` | Service | `robot_rt_control_interfaces/srv/ResetProtectiveStop` | Autonomy | — |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Motion、Autonomy | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Motion、Autonomy | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-02 | `/wheel/odom` | Topic | `nav_msgs/msg/Odometry` | Perception | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型；frame_id=odom，child_frame_id=base_footprint；rt-control 不发 odom→base_footprint TF |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | Motion、Perception、Autonomy | Q_FAST_STATE；ROS 标准类型；整机各受管模块按真实采样时间发布不重叠关节子集；一关节一个权威来源；有效性与时效由模块状态配套表达 |
| R-OUT-04 | `/battery_state` | Topic | `sensor_msgs/msg/BatteryState` | Autonomy | Q_STATE；0.2 Hz；ROS 标准类型；BMS 周期 5 s；只读，不作为业务控制入口 |
| R-OUT-05 | `/vacuum/state` | Topic | `robot_rt_control_interfaces/msg/VacuumState` | Motion、Autonomy | Q_STATE；20～50 Hz |
| R-OUT-18 | `/vacuum/events` | Topic | `robot_rt_control_interfaces/msg/VacuumStateEvent` | Motion、Autonomy | Q_STATE |
| R-OUT-19A | `/ultrasonic/channel1/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19B | `/ultrasonic/channel2/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19C | `/ultrasonic/channel3/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19D | `/ultrasonic/channel4/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19E | `/ultrasonic/channel5/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19F | `/ultrasonic/channel6/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19G | `/ultrasonic/channel7/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19H | `/ultrasonic/channel8/range` | Topic | `sensor_msgs/msg/Range` | Autonomy | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-20 | `/rt_control/sensors/status` | Topic | `robot_rt_control_interfaces/msg/SensorStatusArray` | Motion、Autonomy | Q_STATE |
| R-OUT-21 | `/infrared/state` | Topic | `robot_rt_control_interfaces/msg/DigitalInputStateArray` | Autonomy | Q_STATE |
| R-OUT-22 | `/imu/data` | Topic | `sensor_msgs/msg/Imu` | Motion | Q_FAST_STATE；ROS 标准类型 |
| R-OUT-23L | `/rt_control/left_wrist/wrench` | Topic | `geometry_msgs/msg/WrenchStamped` | Motion | Q_FAST_STATE；ROS 标准类型 |
| R-OUT-23R | `/rt_control/right_wrist/wrench` | Topic | `geometry_msgs/msg/WrenchStamped` | Motion | Q_FAST_STATE；ROS 标准类型 |
| R-OUT-24 | `/rt_control/modules/state` | Topic | `robot_rt_control_interfaces/msg/ModuleStateArray` | Perception、Motion、Autonomy | Q_LATCHED |
| R-OUT-25 | `/rt_control/motion/state` | Topic | `robot_rt_control_interfaces/msg/MotionExecutionState` | Perception、Motion、Autonomy | Q_STATE |
| R-OUT-26 | `/protective_stop/state` | Topic | `robot_rt_control_interfaces/msg/ProtectiveStopState` | Perception、Motion、Autonomy | Q_LATCHED |
| R-OUT-27 | `/edge/state` | Topic | `robot_rt_control_interfaces/msg/DigitalInputStateArray` | Perception、Motion、Autonomy | Q_STATE |
| R-OUT-06 | `/control/safety_state` | Topic | `robot_rt_control_interfaces/msg/SafetyState` | Perception、Motion、Autonomy | Q_STATE；10～50 Hz；最大年龄 200 ms |
| R-OUT-07 | `/rt/rolling_joint_control/state` | Topic | `robot_rt_control_interfaces/msg/RollingJointControlState` | Motion | Q_ROLLING_STATE；50 Hz；最大年龄 200 ms；三代双七轴 right_joint1..7,left_joint1..7；desired_positions rad、desired_velocities rad/s；axis_set_hash 与 open 一致 |
| R-OUT-09 | `/rt_control/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| R-OUT-10 | `/diagnostics` | Topic | `diagnostic_msgs/msg/DiagnosticArray` | 外部/本地入口 | Q_DIAGNOSTIC；ROS 标准类型；不得替代 Action Result、readiness 或 SafetyState 证据 |

## 本域消费（2 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| N-04 | `/cmd_vel` | Topic | `geometry_msgs/msg/Twist` | Motion | Q_CONTROL；20～50 Hz；看门狗 500 ms；ROS 标准类型；当前 Navigation 职责由 motion 域承载；Twist 无 header，看门狗只使用 RT 本地接收间隔；后续 Motion 接管底盘另立协议 |
| M-09 | `/rt/rolling_joint_control/update` | Topic | `robot_motion_interfaces/msg/RollingJointTargetBatch` | Motion | Q_ROLLING_COMMAND；30 Hz；三代双七轴：right_joint1..7 后接 left_joint1..7；全部 rad/rad/s；完整 future suffix，非运动臂仍须包含 |

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
