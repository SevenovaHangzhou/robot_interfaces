<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Autonomy 域接口视图

> 契约版本：1.0.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Autonomy 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（1 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| G-01 | `/autonomy/execute_demo_task` | Action | `robot_autonomy_interfaces/action/ExecuteDemoTask` | 外部/本地入口 | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 Demo schema；不能直接用于 V3 任务；V3 Autonomy 仅按注册表调用泵/LED/保护复位，不直接控制阀/运动 |

## 本域消费（34 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-01 | `/perception/build_wall_task_plan` | Action | `robot_perception_interfaces/action/BuildWallTaskPlan` | Perception | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 固定计划协议：25箱/15序列/0.74m；不代表 V3 箱墙观测和选箱职责 |
| P-02 | `/perception/refine_sequence_poses` | Action | `robot_perception_interfaces/action/RefineSequencePoses` | Perception | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 序列精定位协议；不代表 V3 墙图更新和掉箱识别 |
| P-04 | `/perception/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Perception | Q_LATCHED；1 Hz |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Motion | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Motion | ROS 标准类型；map → odom 由 Navigation/Motion 发布；Perception 通过 TF 查询 map→odom |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_motion_interfaces/action/NavigateToPoseTask` | Motion | — |
| N-05 | `/navigation/localization/status` | Topic | `robot_motion_interfaces/msg/LocalizationStatus` | Motion | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic | `robot_motion_interfaces/msg/LandmarkArray` | Motion | Q_STATE |
| N-15 | `/navigation/semanticmap/get_landmark` | Service | `robot_motion_interfaces/srv/GetLandmark` | Motion | — |
| N-16 | `/navigation/semanticmap/get_map` | Service | `robot_motion_interfaces/srv/GetSemanticMap` | Motion | — |
| N-17 | `/navigation/mapping/set_turn_state` | Service | `robot_motion_interfaces/srv/SetMappingTurnState` | Motion | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 Turn 边界，保留既有协议；不是 V3 底盘接管或同步运动接口；turn_sequence 单调递增，同一 BEGIN_TURN/TURN_COMPLETE 重试幂等 |
| M-08 | `/motion/execute_stage` | Action | `robot_motion_interfaces/action/ExecuteMotionStage` | Motion | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 分阶段机械动作：12臂轴与Turn/Updown；保留供旧消费者迁移，不是 V3 双七轴或新抓放流程；不得通过旧流程调用已退役 VacuumGrip |
| M-06 | `/motion/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Motion | Q_LATCHED；1 Hz |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Motion | Q_LATCHED；1 Hz |
| R-IN-04 | `/rt/vacuum/pump/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetEnabled` | RT-Control | — |
| R-IN-12 | `/rt/led/set_rgbw` | Service | `robot_rt_control_interfaces/srv/SetLedRgbw` | RT-Control | — |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-03 | `/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；ROS 标准类型；整机各受管模块按真实采样时间发布不重叠关节子集；一关节一个权威来源；有效性与时效由模块状态配套表达 |
| R-OUT-04L | `/rt/battery/left/state` | Topic | `sensor_msgs/msg/BatteryState` | RT-Control | Q_STATE；0.2 Hz；ROS 标准类型；BMS 周期 5 s；只读，不作为业务控制入口 |
| R-OUT-04R | `/rt/battery/right/state` | Topic | `sensor_msgs/msg/BatteryState` | RT-Control | Q_STATE；0.2 Hz；ROS 标准类型；BMS 周期 5 s；只读，不作为业务控制入口 |
| R-OUT-05L | `/rt/vacuum/left/pressure` | Topic | `sensor_msgs/msg/FluidPressure` | RT-Control | Q_STATE；20～50 Hz；ROS 标准类型 |
| R-OUT-05R | `/rt/vacuum/right/pressure` | Topic | `sensor_msgs/msg/FluidPressure` | RT-Control | Q_STATE；20～50 Hz；ROS 标准类型 |
| R-OUT-19A | `/rt/ultrasonic/channel1/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19B | `/rt/ultrasonic/channel2/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19C | `/rt/ultrasonic/channel3/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19D | `/rt/ultrasonic/channel4/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19E | `/rt/ultrasonic/channel5/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19F | `/rt/ultrasonic/channel6/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19G | `/rt/ultrasonic/channel7/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-19H | `/rt/ultrasonic/channel8/range` | Topic | `sensor_msgs/msg/Range` | RT-Control | Q_FAST_STATE；最大年龄 2500 ms；ROS 标准类型 |
| R-OUT-20 | `/rt/sensors/state` | Topic | `robot_rt_control_interfaces/msg/SensorStatusArray` | RT-Control | Q_STATE |
| R-OUT-21 | `/rt/infrared/state` | Topic | `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control | Q_STATE |
| R-OUT-09 | `/rt/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | RT-Control | Q_LATCHED；1 Hz |

## 本域禁止的通信边

- 不得访问 `/rt/base/cmd_vel`
- 不得访问 `/rt/arms/follow_joint_trajectory`
- 不得访问 `/rt/enable`
- 不得访问 `/rt/disable`
- 不得访问 `/rt/reset_fault`
- 不得访问 `/rt/vacuum/left_valve/set_enabled`
- 不得访问 `/rt/vacuum/right_valve/set_enabled`

## 已删除的 endpoint

出现在 ROS graph 中即为违约：

- `/rt/arms/rolling/open_session`
- `/rt/arms/rolling/close_session`
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
- `/vacuum/events`
- `/control/safety_state`
- `/control/set_enabled`
- `/pp/left/move`
- `/rt_control/motion/state`
- `/pp/right/move`
- `/protective_stop/reset`
- `/vacuum/state`
- `/rt_control/modules/state`
- `/vacuum/valves/set`
- `/protective_stop/state`
- `/updown/move`
- `/edge/state`
- `/cmd_vel`
- `/rt/rolling_joint_control/update`
- `/whole_body_jtc/follow_joint_trajectory`
- `/rt/joint_control/set_mode`
- `/rt/rolling_joint_control/open`
- `/rt/rolling_joint_control/close`
- `/led/set_rgbw`
- `/head/move`
- `/wheel/odom`
- `/rt/rolling_joint_control/state`
- `/rt_control/readiness`
- `/rt_control/sensors/status`
- `/infrared/state`
- `/imu/data`
- `/rt_control/left_wrist/wrench`
- `/rt_control/right_wrist/wrench`
- `/ultrasonic/channel1/range`
- `/ultrasonic/channel2/range`
- `/ultrasonic/channel3/range`
- `/ultrasonic/channel4/range`
- `/ultrasonic/channel5/range`
- `/ultrasonic/channel6/range`
- `/ultrasonic/channel7/range`
- `/ultrasonic/channel8/range`
- `/vacuum/pump/set_enabled`
- `/battery_state`
