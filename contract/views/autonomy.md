<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Autonomy 域接口视图

> 契约版本：2.0.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Autonomy 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（1 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| G-01 | `/autonomy/execute_demo_task` | Action | `robot_autonomy_interfaces/action/ExecuteDemoTask` | 外部/本地入口 | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 Demo schema；不能直接用于 V3 任务；V3 Autonomy 仅按注册表调用泵/LED/保护复位，不直接控制阀/运动 |

## 本域消费（58 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-01 | `/perception/build_wall_task_plan` | Action | `robot_perception_interfaces/action/BuildWallTaskPlan` | Perception | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 固定计划协议：25箱/15序列/0.74m；不代表 V3 箱墙观测和选箱职责 |
| P-02 | `/perception/refine_sequence_poses` | Action | `robot_perception_interfaces/action/RefineSequencePoses` | Perception | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 序列精定位协议；不代表 V3 墙图更新和掉箱识别 |
| P-04 | `/perception/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Perception | Q_LATCHED；1 Hz |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Navigation | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Navigation | ROS 标准类型；map → odom 由 Navigation 发布；Perception 通过 TF 查询 map→odom |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_navigation_interfaces/action/NavigateToPoseTask` | Navigation | — |
| N-05 | `/navigation/localization/status` | Topic | `robot_navigation_interfaces/msg/LocalizationStatus` | Navigation | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic | `robot_navigation_interfaces/msg/LandmarkArray` | Navigation | Q_STATE |
| N-15 | `/navigation/semanticmap/get_landmark` | Service | `robot_navigation_interfaces/srv/GetLandmark` | Navigation | — |
| N-16 | `/navigation/semanticmap/get_map` | Service | `robot_navigation_interfaces/srv/GetSemanticMap` | Navigation | — |
| N-17 | `/navigation/mapping/set_turn_state` | Service | `robot_navigation_interfaces/srv/SetMappingTurnState` | Navigation | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 Turn 边界，保留既有协议；不是 V3 底盘接管或同步运动接口；turn_sequence 单调递增，同一 BEGIN_TURN/TURN_COMPLETE 重试幂等 |
| M-08 | `/motion/execute_stage` | Action | `robot_motion_interfaces/action/ExecuteMotionStage` | Motion | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 分阶段机械动作：12臂轴与Turn/Updown；保留供旧消费者迁移，不是 V3 双七轴或新抓放流程；不得通过旧流程调用已退役 VacuumGrip |
| M-06 | `/motion/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Motion | Q_LATCHED；1 Hz |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Navigation | Q_LATCHED；1 Hz |
| R-IN-04 | `/rt/vacuum/pump/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetEnabled` | RT-Control | — |
| R-IN-05L | `/rt/vacuum/left_valve/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetEnabled` | RT-Control | — |
| R-IN-05R | `/rt/vacuum/right_valve/set_enabled` | Service | `robot_rt_control_interfaces/srv/SetEnabled` | RT-Control | — |
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
| R-OUT-30 | `/rt/base/terminal_rotation_active` | Topic | `std_msgs/msg/Bool` | RT-Control | Q_FAST_STATE；50 Hz；最大年龄 300 ms；ROS 标准类型 |
| R-OUT-31 | `/rt/base/execution_state` | Topic | `std_msgs/msg/Float64MultiArray` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 300 ms；ROS 标准类型 |
| R-OUT-31C | `/rt_control/chassis/execution_state` | Topic | `std_msgs/msg/Float64MultiArray` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 300 ms；ROS 标准类型 |
| R-OUT-32 | `/rt_control/chassis/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 300 ms；ROS 标准类型 |
| R-OUT-20 | `/rt/sensors/state` | Topic | `robot_rt_control_interfaces/msg/SensorStatusArray` | RT-Control | Q_STATE |
| R-OUT-21 | `/rt/infrared/state` | Topic | `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control | Q_STATE |
| R-OUT-09 | `/rt/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | RT-Control | Q_LATCHED；1 Hz |
| M-IF-02 | `/motion/pick_and_carry` | Action | `robot_motion_interfaces/action/PickAndCarry` | Motion | — |
| M-IF-03 | `/motion/place_carried_boxes` | Action | `robot_motion_interfaces/action/PlaceCarriedBoxes` | Motion | — |
| M-IF-05 | `/motion/state` | Topic | `robot_motion_interfaces/msg/ManipulationState` | Motion | Q_STATE；10 Hz |
| N-IF-16 | `/navigation/detect_dropped_boxes` | Action | `robot_navigation_interfaces/action/DetectDroppedBoxes` | Navigation | — |
| P-IF-01 | `/perception/set_sku_catalog` | Service | `robot_perception_interfaces/srv/SetSkuCatalog` | Perception | — |
| P-IF-03 | `/perception/get_wall_map` | Service | `robot_perception_interfaces/srv/GetWallMap` | Perception | — |
| P-IF-04 | `/perception/wall_map` | Topic | `robot_perception_interfaces/msg/WallMap` | Perception | Q_LATCHED |
| P-IF-05 | `/perception/wall_map_status` | Topic | `robot_perception_interfaces/msg/WallMapStatus` | Perception | Q_STATE |
| P-IF-06 | `/perception/recognize_dropped_boxes` | Action | `robot_perception_interfaces/action/RecognizeDroppedBoxes` | Perception | — |
| P-IF-14 | `/perception/finish_wall_observation` | Service | `robot_perception_interfaces/srv/FinishWallObservation` | Perception | — |
| P-IF-08 | `/perception/update_wall_map` | Action | `robot_perception_interfaces/action/UpdateWallMap` | Perception | — |
| M-IF-04 | `/motion/move_to_posture` | Action | `robot_motion_interfaces/action/MoveToPosture` | Motion | — |
| M-IF-06 | `/motion/terminate_task` | Service | `robot_motion_interfaces/srv/TerminateTask` | Motion | — |
| P-IF-09 | `/perception/camera/head/color/image_rect/compressed` | Topic | `sensor_msgs/msg/CompressedImage` | Perception | Q_SENSOR；ROS 标准类型 |
| P-IF-10 | `/perception/camera/chest/color/image_rect/compressed` | Topic | `sensor_msgs/msg/CompressedImage` | Perception | Q_SENSOR；ROS 标准类型 |
| P-IF-11 | `/perception/boxes/head/image_annotated/compressed` | Topic | `sensor_msgs/msg/CompressedImage` | Perception | Q_SENSOR；ROS 标准类型 |
| P-IF-12 | `/perception/camera/head/camera_info` | Topic | `sensor_msgs/msg/CameraInfo` | Perception | Q_SENSOR；ROS 标准类型 |
| P-IF-13 | `/perception/camera/chest/camera_info` | Topic | `sensor_msgs/msg/CameraInfo` | Perception | Q_SENSOR；ROS 标准类型 |

## 本域禁止的通信边

- 不得访问 `/rt/base/cmd_vel`
- 不得访问 `/rt/arms/follow_joint_trajectory`
- 不得访问 `/rt/enable`
- 不得访问 `/rt/disable`
- 不得访问 `/rt/reset_fault`

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
