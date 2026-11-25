<!-- 本文由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

# Navigation 域接口视图

> 契约版本：2.0.0
> 事实源：`contract/endpoints.yaml`
> Wire schema：本仓库对应的 `robot_*_interfaces` IDL

本文只列 Navigation 域**提供**与**消费**的跨域 endpoint，用于分域阅读。
语义约束、成功判定、重试规则和错误码以权威契约为准，本文不重复。

## 本域提供（16 条）

| ID | ROS 名称 | 形式 | 类型 | 消费方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| P-NAV-01 | `/odom` | Topic | `nav_msgs/msg/Odometry` | Perception、Autonomy | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型 |
| P-NAV-02 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | Perception、Autonomy | ROS 标准类型；map → odom 由 Navigation 发布；Perception 通过 TF 查询 map→odom |
| N-01 | `/navigation/navigate_to_pose` | Action | `robot_navigation_interfaces/action/NavigateToPoseTask` | Autonomy | — |
| N-04 | `/rt/base/cmd_vel` | Topic | `geometry_msgs/msg/Twist` | RT-Control | Q_CONTROL；20～50 Hz；看门狗 500 ms；ROS 标准类型；由 navigation 域发送；Twist 无 header，看门狗只使用 RT 本地接收间隔；后续 Motion 接管底盘另立协议 |
| N-07 | `/rt/base/terminal_rotation_request` | Topic | `std_msgs/msg/Bool` | RT-Control | Q_CONTROL；50 Hz；看门狗 300 ms；ROS 标准类型；Navigation provides this request, as for N-04; design robot_driver#334 |
| N-05 | `/navigation/localization/status` | Topic | `robot_navigation_interfaces/msg/LocalizationStatus` | Autonomy | Q_STATE；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic | `robot_navigation_interfaces/msg/LandmarkArray` | Perception、Autonomy、外部/本地入口 | Q_STATE |
| N-11 | `/navigation/semanticmap/add_landmark` | Service | `robot_navigation_interfaces/srv/AddLandmark` | Perception、外部/本地入口 | — |
| N-12 | `/navigation/semanticmap/add_current_landmark` | Service | `robot_navigation_interfaces/srv/AddCurrentLandmark` | Perception、外部/本地入口 | — |
| N-13 | `/navigation/semanticmap/update_landmark` | Service | `robot_navigation_interfaces/srv/UpdateLandmark` | Perception、外部/本地入口 | — |
| N-14 | `/navigation/semanticmap/remove_landmark` | Service | `robot_navigation_interfaces/srv/RemoveLandmark` | Perception、外部/本地入口 | — |
| N-15 | `/navigation/semanticmap/get_landmark` | Service | `robot_navigation_interfaces/srv/GetLandmark` | Perception、Autonomy、外部/本地入口 | — |
| N-16 | `/navigation/semanticmap/get_map` | Service | `robot_navigation_interfaces/srv/GetSemanticMap` | Perception、Autonomy、外部/本地入口 | — |
| N-17 | `/navigation/mapping/set_turn_state` | Service | `robot_navigation_interfaces/srv/SetMappingTurnState` | Autonomy、外部/本地入口 | **Legacy V2，仅保留迁移；非 V3 工作流**；Legacy V2 Turn 边界，保留既有协议；不是 V3 底盘接管或同步运动接口；turn_sequence 单调递增，同一 BEGIN_TURN/TURN_COMPLETE 重试幂等 |
| N-06 | `/navigation/readiness` | Topic | `robot_system_interfaces/msg/DomainReadiness` | Autonomy | Q_LATCHED；1 Hz |
| N-IF-16 | `/navigation/detect_dropped_boxes` | Action | `robot_navigation_interfaces/action/DetectDroppedBoxes` | Autonomy | — |

## 本域消费（9 条）

| ID | ROS 名称 | 形式 | 类型 | 提供方 | 约束 |
| --- | --- | --- | --- | --- | --- |
| R-OUT-01 | `/tf` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | ROS 标准类型；robot_state_publisher 发布本体动态 TF |
| R-OUT-01S | `/tf_static` | Topic | `tf2_msgs/msg/TFMessage` | RT-Control | Q_LATCHED；ROS 标准类型；robot_state_publisher 发布本体固定坐标边 |
| R-OUT-02 | `/rt/base/odom` | Topic | `nav_msgs/msg/Odometry` | RT-Control | Q_FAST_STATE；50 Hz；最大年龄 200 ms；ROS 标准类型；frame_id=odom，child_frame_id=base_footprint；rt-control 不发 odom→base_footprint TF |
| R-OUT-29 | `/rt/base/wheel_observations` | Topic | `robot_rt_control_interfaces/msg/WheelObservationArray` | RT-Control | Q_FAST_STATE；100 Hz；逐轮观测，供导航逐轮融合；与 R-OUT-02 同源，导航不得把两者同时作为独立观测 |
| R-OUT-30 | `/rt/base/terminal_rotation_active` | Topic | `std_msgs/msg/Bool` | RT-Control | Q_CONTROL；50 Hz；最大年龄 300 ms；ROS 标准类型 |
| R-OUT-31 | `/rt/base/execution_state` | Topic | `std_msgs/msg/Float64MultiArray` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 100 ms；ROS 标准类型 |
| R-OUT-31C | `/rt_control/chassis/execution_state` | Topic | `std_msgs/msg/Float64MultiArray` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 100 ms；ROS 标准类型 |
| R-OUT-32 | `/rt_control/chassis/joint_states` | Topic | `sensor_msgs/msg/JointState` | RT-Control | Q_FAST_STATE；100 Hz；最大年龄 200 ms；ROS 标准类型 |
| R-OUT-22 | `/rt/imu/data` | Topic | `sensor_msgs/msg/Imu` | RT-Control | Q_FAST_STATE；ROS 标准类型 |

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
