<!-- 本节由 tools/gen_domain_views.py 从 contract/endpoints.yaml 生成，请勿手工编辑 -->

## 5. 接口总表

ID 前缀含义：`G` = Gateway/本地入口，`P` = Perception 提供，`N` = 导航能力（Motion 或 Perception 提供），`M` = Motion 提供，`R-IN` = RT-Control 输入，`R-OUT` = RT-Control 输出。

### 5.1 任务入口（Autonomy 提供）

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| G-01 | `/autonomy/execute_demo_task` | Action / `robot_autonomy_interfaces/action/ExecuteDemoTask` | 外部/本地入口 ⇄ Autonomy | 同时只接受一个活动 Goal，第二个在 Goal 响应阶段 reject；终态三选一 |

### 5.2 Perception 提供

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| P-01 | `/perception/build_wall_task_plan` | Action / `robot_perception_interfaces/action/BuildWallTaskPlan` | Autonomy ⇄ Perception | Goal 携带非零 `task_id` 与锁定 `scene_profile_id`；真实单次同步采集；Result 返回新 `scene_id`；25 箱；固定 15 序列；每箱冻结 arm 与 suction_mode，pose 为吸取表面接触位姿；每序列自带 `station_id`、统一 0.74 m 退避的 `station_nav_pose(map)`、按臂绑定重拍位；每个 G-01 只调用一次；严格成功 |
| P-02 | `/perception/refine_sequence_poses` | Action / `robot_perception_interfaces/action/RefineSequencePoses` | Autonomy ⇄ Perception | Goal 的 `expected_scene_id`、sequence、box_ids、arms、suction_modes 必须与当前 producer instance 最近一次成功 P-01 完全一致；同箱同序；返回同臂同吸取方式的吸取表面接触位姿；`base_link`；stamp=真实曝光时刻；底盘静止、TF、标定不变 |
| P-03 | `/perception/obstacle_cloud` | Topic / `robot_perception_interfaces/msg/ObstacleCloud` | Perception → Motion | **产品预留**；Demo 不部署、不订阅、不依赖 |
| P-04 | `/perception/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Perception → Autonomy | `Q_LATCHED`；故障立即 `ready=false`；变化立即发；稳定 1 Hz |
| P-IF-01 | `/perception/set_sku_catalog` | Service / `robot_perception_interfaces/srv/SetSkuCatalog` | Autonomy ⇄ Perception | 标称尺寸单位米，按箱体局部轴 X 宽/Y 深/Z 高；至少两个轴为有限正数，未知轴填 0，负数、NaN、Inf 拒绝；dimension_tolerance_known=false 时用视觉默认容差 0.04 m，为 true 时容差为有限非负数；目录只描述箱型，不含数量；SKU ID 唯一；观测进行中拒绝设置，调用方等本轮结束后重试；同 ID 同版本但内容不同时拒绝，相同内容重复设置返回已加载结果；accepted 只表示字典已加载，不表示已有箱子快照；一次观测内不混用两版字典 |
| P-IF-03 | `/perception/get_wall_map` | Service / `robot_perception_interfaces/srv/GetWallMap` | Autonomy ⇄ Perception | 只读已有数据：不拍照、不转头、不等待新观测；返回全局箱子库的全部箱子，不按场景或墙面筛选；库未建好时 success=false，已确认的空库 success=true 且 boxes 为空；一次响应只对应一个已提交版本；重复读取不递增版本、不刷新观测时间；精确读取不存在的版本时失败，不回退到最新；坐标有效性用导航地图版本、定位状态和 TF 判断 |
| P-IF-04 | `/perception/wall_map` | Topic / `robot_perception_interfaces/msg/WallMap` | Perception → Autonomy、外部/本地入口 | 每次成功提交时发布完整全局快照；晚加入的订阅者收到最近一份；Autonomy 的正常更新以 P-IF-08 的 Result 为准，本 Topic 供显示和其他消费者使用 |
| P-IF-05 | `/perception/wall_map_status` | Topic / `robot_perception_interfaces/msg/WallMapStatus` | Perception → Autonomy、外部/本地入口 | 最近提交的快照引用、当前更新阶段、最近一次尝试的结果；仅作可观测性，不作为主流程握手 |
| P-IF-06 | `/perception/recognize_dropped_boxes` | Action / `robot_perception_interfaces/action/RecognizeDroppedBoxes` | Autonomy ⇄ Perception | 每次 1 或 2 个区域，各数组同长同序；detection_goal_id 为导航检测的 Goal UUID，原样返回；按候选观测时刻的 TF 把 odom 下 XY 转到 map；必须配置真实的地面高度和搜索高度，缺失时明确失败，不假设 z=0；候选区域必须进入相机视野；输出 map 下箱体中心、朝向和尺寸；看不到时返回 NOT_OBSERVABLE，不报 NOT_FOUND；不修改正常箱子库；与 P-IF-08 共用相机和头部，冲突时后到的请求返回忙 |
| P-IF-08 | `/perception/update_wall_map` | Action / `robot_perception_interfaces/action/UpdateWallMap` | Autonomy ⇄ Perception | Autonomy 在 PickAndCarry 整组终态且有成功侧到运输位后发一次；必须是受理之后取得的新观测；Result 直接带本次提交的完整快照，调用方不再读取箱墙；是否更新看 map_committed，提交后被取消或出故障仍返回已提交快照，提交前失败则旧库不变；不提供强制删箱，不返回逐箱移除核对，箱子是否移除由视觉证据决定；expected_map 版本比当前旧可接受，超前则拒绝；处理可与转向、卸货并行，usable_view_obtained 不是底盘运动许可 |
| P-IF-09 | `/perception/camera/head/color/image_rect/compressed` | Topic / `sensor_msgs/msg/CompressedImage` | Perception → Autonomy、外部/本地入口 | 头部彩色图，JPEG；视觉栈启动后持续发布，不需要请求；不低于 2 Hz，长边不超过 1280 像素；header.stamp 为曝光时刻，frame_id 为相机坐标系且能在 TF 中查到；发布端使用 best-effort、keep last 1 |
| P-IF-10 | `/perception/camera/chest/color/image_rect/compressed` | Topic / `sensor_msgs/msg/CompressedImage` | Perception → Autonomy、外部/本地入口 | 胸部彩色图，其余同 P-IF-09；胸部相机随视觉栈默认开启 |
| P-IF-11 | `/perception/boxes/head/image_annotated/compressed` | Topic / `sensor_msgs/msg/CompressedImage` | Perception → Autonomy、外部/本地入口 | 头部标注图，每个箱子上写箱号，箱号与箱子快照里的 box_id 一致；其余同 P-IF-09 |
| P-IF-12 | `/perception/camera/head/camera_info` | Topic / `sensor_msgs/msg/CameraInfo` | Perception → Autonomy、外部/本地入口 | 头部相机内参，与 P-IF-09 同一相机、同一分辨率 |
| P-IF-13 | `/perception/camera/chest/camera_info` | Topic / `sensor_msgs/msg/CameraInfo` | Perception → Autonomy、外部/本地入口 | 胸部相机内参，与 P-IF-10 同一相机、同一分辨率 |

### 5.3 Motion 提供

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| P-NAV-01 | `/odom` | Topic / `nav_msgs/msg/Odometry` | Motion → Perception、Autonomy | Navigation/Motion 发布融合里程计；50 Hz；最大年龄 200 ms；Perception 可用于定位/视觉时空对齐；**最终停稳证据** |
| P-NAV-02 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | Motion → Perception、Autonomy | map→odom 定位边唯一发布者为 Navigation/Motion；/tf 按坐标边判唯一性 |
| N-01 | `/navigation/navigate_to_pose` | Action / `robot_motion_interfaces/action/NavigateToPoseTask` | Autonomy ⇄ Motion | `target_name + map_version` 由 Motion 通过语义地图解析为 Nav2 目标；真实调用 Nav2；最多总调用三次；SUCCEEDED 必须同时满足位置和朝向到位、定位有效、实际运动反馈确认已停稳，不以零速指令或 Nav2 自身成功代替；CANCELED 必须对应车已停止，无法确认时返回失败；目标与当前位置 XY 相同时原地旋转；受理时固定目标位姿 |
| N-04 | `/rt/base/cmd_vel` | Topic / `geometry_msgs/msg/Twist` | Motion → RT-Control | 底盘速度入口，仅在 R-IN-23 为 VELOCITY_READY（使能后默认）时生效，FJT_READY 时不被接受；20～50 Hz；500 ms 本地接收超时；不与旧 `/cmd_vel_safe` 或未来第二 writer 并行生效 |
| N-05 | `/navigation/localization/status` | Topic / `robot_motion_interfaces/msg/LocalizationStatus` | Motion → Autonomy | 发布者唯一；10～20 Hz；最大年龄 200 ms |
| N-10 | `/navigation/semanticmap/landmark_array` | Topic / `robot_motion_interfaces/msg/LandmarkArray` | Motion → Perception、Autonomy、外部/本地入口 | 当前语义地图地标列表；按 map_version 区分地图版本 |
| N-11 | `/navigation/semanticmap/add_landmark` | Service / `robot_motion_interfaces/srv/AddLandmark` | Perception、外部/本地入口 ⇄ Motion | 按指定位姿新增语义地标；返回 used_map_version 与最终地标 |
| N-12 | `/navigation/semanticmap/add_current_landmark` | Service / `robot_motion_interfaces/srv/AddCurrentLandmark` | Perception、外部/本地入口 ⇄ Motion | 以当前 base_footprint 位姿新增语义地标；返回 used_map_version 与最终地标 |
| N-13 | `/navigation/semanticmap/update_landmark` | Service / `robot_motion_interfaces/srv/UpdateLandmark` | Perception、外部/本地入口 ⇄ Motion | 更新语义地标属性和位姿；返回 used_map_version 与最终地标 |
| N-14 | `/navigation/semanticmap/remove_landmark` | Service / `robot_motion_interfaces/srv/RemoveLandmark` | Perception、外部/本地入口 ⇄ Motion | 按 name 删除指定 map_version 内的语义地标 |
| N-15 | `/navigation/semanticmap/get_landmark` | Service / `robot_motion_interfaces/srv/GetLandmark` | Perception、Autonomy、外部/本地入口 ⇄ Motion | 按 target_name 查询语义地标；N-01 服务端用它解析导航目标 |
| N-16 | `/navigation/semanticmap/get_map` | Service / `robot_motion_interfaces/srv/GetSemanticMap` | Perception、Autonomy、外部/本地入口 ⇄ Motion | 查询指定 map_version 下全部语义地标 |
| N-17 | `/navigation/mapping/set_turn_state` | Service / `robot_motion_interfaces/srv/SetMappingTurnState` | Autonomy、外部/本地入口 ⇄ Motion | 转台运动前 BEGIN_TURN 必须先暂停 FAST-LIO 到底盘的融合输入；停稳后同 caller_id、turn_sequence 的 TURN_COMPLETE 仅在实时 base_footprint←LiDAR TF 新鲜且连续稳定满配置窗口时切换固定外参，丢弃切换前排队里程计并恢复融合；乱序、并发事务或调用者不一致必须拒绝 |
| M-08 | `/motion/execute_stage` | Action / `robot_motion_interfaces/action/ExecuteMotionStage` | Autonomy ⇄ Motion | 单一串行阶段 Action；无活动抓取流程时 TURN/CAMERA_VIEW/NAMED_JOINT_POSE 可任意独立触发；抓取流程固定 PREGRASP→APPROACH→PLACE→HOME，活动期间禁止独立任务、并发、跳步和提前触发 |
| M-09 | `/rt/arms/rolling/target_batch` | Topic / `robot_motion_interfaces/msg/RollingJointTargetBatch` | Motion → RT-Control | 仅在 /rt/arms/set_control_mode 切到 ROLLING_READY 后生效；epoch 等于 R-OUT-07 当前 epoch；sequence 在同一 epoch 内严格递增；replace_from 为 ROS 时间（运控与 RT-Control 同机），不早于当前时刻 + 替换提前量；首点 time_from_start=0，位置与速度在拼接容差内等于缓冲轨迹在 replace_from 处的值；点时间严格递增，1～256 点，总长不超过缓冲上限；位置/速度/加速度不超过 robot_description 关节限位，且从任一点起都能在限值内停住；不满足整批拒绝，结果见 R-OUT-07 last_result；final=true 为本段最后一批，末点各轴速度须为 0（否则 FINAL_NOT_AT_REST）；最新接受的批次为 final 时不再需要后续批次、不计更新超时，执行到末点后保持并报 STOP_COMPLETED，期间仍可用新批次从其 replace_from 起替换，替换批次非 final 时恢复更新超时；最新接受的批次非 final 时，超过更新超时未收到有效批次，或缓冲耗尽时按限值刹停并保持；best-effort/volatile/keep-last(1)，deadline/lifespan 100 ms |
| M-06 | `/motion/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 机械能力准入；变化立即发；稳定 1 Hz |
| N-06 | `/navigation/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | Motion → Autonomy | 导航执行能力准入；变化立即发；稳定 1 Hz |
| M-IF-02 | `/motion/pick_and_carry` | Action / `robot_motion_interfaces/action/PickAndCarry` | Autonomy ⇄ Motion | 一个 Action 内完成检查、规划、接近、贴近、开阀、等吸附、抽离、进入运输位，不设独立可行性接口；tcp_target 为 base_link 下 TCP，Motion 不再叠加工具偏移；Motion 不启停泵；开阀后收到参与侧 p<=-60 kPa 的有效新压力样本即抽离，不加固定延时或多帧稳定等待；source_observed_at 只作记录，不作为拒绝条件；有效压力样本未达标或吸附1秒超时作为业务警告继续，传感器状态无效/过期或持箱期间无有效压力作为阻断故障，停止并等待RT终态和关节停稳，不自动续跑；分臂给出成功/失败/取消/未知，一侧成功一侧失败时 overall=PARTIAL 并以 ABORTED 返回，保留成功侧事实；同时只接受一个 Goal，忙时拒绝；客户端取消须停止并确认停稳，确认后 ROS CANCELED/业务4，无法确认时 ROS ABORTED/业务5；不自动松阀、关泵、回 Home；本版仅 NORMAL_PICK=1，DROPPED_BOX_RECOVERY 暂拒绝 |
| M-IF-03 | `/motion/place_carried_boxes` | Action / `robot_motion_interfaces/action/PlaceCarriedBoxes` | Autonomy ⇄ Motion | 前提是导航已到卸货朝向并停稳；顺序为 LM 运动到 Motion 配置的默认放置位、关闭所选阀并读回确认、等待释放、回 Home、确认停稳；不关泵；本版要求释放侧等于当前任务记录的全部持箱侧，不支持单侧剩余箱恢复或部分释放；箱 ID 与持箱记录不一致时在释放前拒绝；阀已释放但回 Home 失败时整体不成功，保留已释放事实且不重放释放；取消/异常停止须确认停稳，确认后客户端取消为 CANCELED/业务4，无法确认不得报 CANCELED；不松阀、不回 Home、不反转已释放输出 |
| M-IF-05 | `/motion/state` | Topic / `robot_motion_interfaces/msg/ManipulationState` | Motion → Autonomy | 持续发布执行事实：当前操作、分臂阶段、关联箱 ID、吸附事实、阀输出是否已确认释放、上部是否停稳；Action 结束后继续发布；持箱与否的业务判断由 Autonomy 做；各项观测带自己的时间，重发不刷新旧观测时间；warnings[] 报告业务警告和阻断故障，error 只表达任务级错误 |
| N-IF-16 | `/navigation/detect_dropped_boxes` | Action / `robot_motion_interfaces/action/DetectDroppedBoxes` | Autonomy ⇄ Motion | 一个 Goal 执行一轮检测，不常驻监听；必须能检出请求发出前已经落地的箱子；Autonomy 判定掉箱后先取消在途导航与运控动作再立即发起；reference_valid=true 时 reference_stamp 是掉箱前仍在吸附的时刻再提前 1 s（电控压力消息头时钟），导航须保留至少 5 s 的点云/高度图历史以便回看该时刻（导航已确认）；导航 Goal 被取消时先停车再以 CANCELED 结束（见 N-01）；reference_valid=false 时按无基准方式检测，不得拒绝；同时只接受一个 Goal；有效完成且有候选：SUCCEEDED/ok=true/detected=true；有效完成无候选：SUCCEEDED/ok=true/detected=false；点云不可用、TF 失败或超时：ABORTED/ok=false，不能当作现场无箱；取消：CANCELED，只停检测，不发停车指令；超时计时独立于点云回调；结果只在 Result 里一次返回；候选为 odom 下粗定位，数量不限于 2 |
| M-IF-04 | `/motion/move_to_posture` | Action / `robot_motion_interfaces/action/MoveToPosture` | Autonomy ⇄ Motion | posture_id=home 时回到默认 Home；不以压力或旧任务记录拒绝，是否适合移动由上层判断；从实时实测关节起点规划、碰撞检查并时间化后执行；不启停泵、不动阀；取消须确认停稳，客户端取消 ROS CANCELED、服务 terminate 时 ROS ABORTED 但业务为停止；不清旧任务记录，由 M-IF-07 负责 |
| M-IF-06 | `/motion/terminate_task` | Service / `robot_motion_interfaces/srv/TerminateTask` | Autonomy ⇄ Motion | 使用 OperationContext 匹配当前活动 attempt；只停止当前任务，不自动清理任务记录、不松阀、不关泵、不回 Home、不规划新动作；in-flight PickAndCarry/PlaceCarriedBoxes/MoveToPosture 结束，客户端取消为 CANCELED，服务终止为 ABORTED 但业务仍为取消；必须等待 RT 终态和真实关节反馈确认停稳，accepted 只表示受理，stopped/stop_confirmation_valid 才表示停止；停稳超时 stopped=false/stop_confirmation_valid=false 并在 error 说明；无匹配活动 attempt 时 accepted=false；复位由 M-IF-07 执行 |
| M-IF-07 | `/motion/reset_task` | Service / `robot_motion_interfaces/srv/ResetTask` | Autonomy ⇄ Motion | 使用 OperationContext 匹配原 attempt；只要求没有执行中任务、没有受理中或终态未确认的 RT 目标；清理目标集合、持箱记录和任务锁；不移动、不松阀、不关泵、不清 RT 故障、不清 attempt 去重记录；不检查压力或额外停稳窗口；现场负载处置由上层负责 |
| M-IF-08 | `/motion/get_end_effector_pose_at_time` | Service / `robot_motion_interfaces/srv/GetEndEffectorPoseAtTime` | Autonomy ⇄ Motion | 查询指定操作事件时刻的 TCP；reference_frame 仅支持 base_link；只使用前后真实关节反馈样本插值，不外推、不用当前位姿替代；事件来源/实例/序号只用于关联追溯；无支持样本时 pose_valid=false 并在 per_arm_errors 说明；不改变业务状态 |

### 5.4 RT-Control 输入

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-IN-02 | `/rt/arms/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 完整三代双臂 7+7 轴；位置 rad、速度 rad/s；不包含 turn/updown 或 PP；`allow_partial_joints_goal=false`；整组取消。准入（RT-Control 实时侧）：每点必须带速度、末点速度为 0；首点时间为 0 时距实测位置 ≤ 1°，首点在未来时距实测位置 ≤ 速度上限×首点时间；各点速度与每段平均速度 ≤ 速度上限；每段三次插值加速度（含从上一条指令接入首点的一段）≤ 加速度上限；上限取自 robot_description（双臂 30°/s、60°/s²）；不满足整条拒绝 |
| R-IN-02L | `/rt/arms/left/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 仅单臂作用域提供；left_joint1..7；位置 rad、速度 rad/s；`allow_partial_joints_goal=false`；整组取消；双臂作用域只提供 R-IN-02 |
| R-IN-02R | `/rt/arms/right/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 仅单臂作用域提供；right_joint1..7；其余同 R-IN-02L |
| R-IN-22 | `/rt/arms/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 完整三代双臂 7+7 轴；位置 rad、速度 rad/s；准入同 R-IN-02；用 header.stamp 标注首点时间基准；末点速度必须为 0；控制器从上一条指令接续新轨迹；与 R-IN-02 并发时以最后到达者为准（执行中的 action 目标被中止） |
| R-IN-22L | `/rt/arms/left/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 仅单臂作用域提供；left_joint1..7；其余同 R-IN-22 |
| R-IN-22R | `/rt/arms/right/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 仅单臂作用域提供；right_joint1..7；其余同 R-IN-22 |
| R-IN-18 | `/rt/enable` | Service / `robot_rt_control_interfaces/srv/RtEnable` | 外部/本地入口 ⇄ RT-Control | 按使能策略分批使能全部受管驱动与握手设备并激活运动控制器；失败时返回失败批次、关节、状态字、阶段与 DREE 错误；不复位急停、安全继电器或 STO |
| R-IN-19 | `/rt/disable` | Service / `robot_rt_control_interfaces/srv/RtEnable` | 外部/本地入口 ⇄ RT-Control | 停用运动控制器后有序失能全部受管设备；已失能时直接成功 |
| R-IN-20 | `/rt/reset_fault` | Service / `robot_rt_control_interfaces/srv/RtEnable` | 外部/本地入口 ⇄ RT-Control | 对作用域内全部故障设备做一次组复位；任一从站不在 OP 或反馈过期时拒绝（device_offline）；需要重启时拒绝（restart_required）；不使能 |
| R-IN-21 | `/rt/run_self_check` | Service / `std_srvs/srv/Trigger` | 外部/本地入口 ⇄ RT-Control | 用最新一组设备状态重跑启动自检规则；success=false 表示有阻断项；message 给出阻断/警告数量；不写总线、不改变使能状态 |
| R-IN-04 | `/rt/vacuum/pump/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetEnabled` | Autonomy ⇄ RT-Control | Autonomy 设置共用泵目标状态；普通停泵要求左右阀回读有效且为释放、左右压力有效且 >= -1 kPa、无活动阀操作；检查与执行期间阻止新吸附；enabled 为输出回读，输出未确认或未知时 accepted=false 并在 error 给出原因；reason 为 manual 的人工停泵不受上述停泵准入限制，由操作员保证箱子已有人扶住 |
| R-IN-05L | `/rt/vacuum/left_valve/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetEnabled` | Motion、Autonomy ⇄ RT-Control | enabled=true 吸附、false 释放；输出回读确认即返回 accepted=true，不等待建立真空；同侧忙拒绝；RT 不自动重试；输出未确认或未知时 accepted=false 并在 error 给出原因；正常抓放由 Motion 调用；Autonomy 只在重置流程和联调操作页的人工开关时调用，流程自动执行期间不调用 |
| R-IN-05R | `/rt/vacuum/right_valve/set_enabled` | Service / `robot_rt_control_interfaces/srv/SetEnabled` | Motion、Autonomy ⇄ RT-Control | 同 R-IN-05L，作用于右阀 |
| R-IN-06 | `/rt/arms/set_control_mode` | Service / `robot_rt_control_interfaces/srv/SetJointControlMode` | Motion ⇄ RT-Control | 仅在已使能且手臂静止时切换 FJT_READY/ROLLING_READY（VELOCITY_READY 只用于底盘 R-IN-23，手臂拒绝）；切换前 Motion 取消并等待 R-IN-02 Action 终态；新控制器以当前位置保持起步；失败时 accepted=false 并给出 ErrorInfo，mode 为调用后的实际模式；歧义切换进入 RESTART_REQUIRED（见 R-OUT-09） |
| R-IN-23 | `/rt/base/set_control_mode` | Service / `robot_rt_control_interfaces/srv/SetJointControlMode` | Motion ⇄ RT-Control | 仅在已使能且底盘静止时在 VELOCITY_READY（舵轮控制器接受 N-04，行走轮 CSV）与 FJT_READY（R-IN-24/R-IN-25 的轮子轨迹控制器接管 8 个轮关节位置，行走轮 CSP）之间切换；使能后默认 VELOCITY_READY；切换前 Motion 停发 N-04、取消并等待 R-IN-24 Action 终态；新控制器以当前位置保持起步，行走轮驱动器确认新模式后才返回成功；ROLLING_READY 拒绝；失败时 accepted=false 并给出 ErrorInfo，mode 为调用后的实际模式；歧义切换进入 RESTART_REQUIRED（见 R-OUT-09） |
| R-IN-24 | `/rt/base/follow_joint_trajectory` | Action / `control_msgs/action/FollowJointTrajectory` | Motion ⇄ RT-Control | 仅在 R-IN-23 为 FJT_READY 时接受；完整 8 轴；位置 rad、速度 rad/s；转向位置在机器人模型限位内；`allow_partial_joints_goal=false`；整组取消。准入（RT-Control 实时侧）：每点必须带速度、末点速度为 0；首点时间为 0 时距实测位置 ≤ 1°，首点在未来时距实测位置 ≤ 速度上限×首点时间；速度与加速度不超过底盘导航限值（转向 35°/s、35°/s²；行走轮轮面 2 m/s、2 m/s²，按轮半径换算为关节单位；由 RT-Control 底盘导航配置拥有，与 N-04 同一组）；不满足时整条拒绝（INVALID_GOAL），不执行半条 |
| R-IN-25 | `/rt/base/joint_trajectory` | Topic / `trajectory_msgs/msg/JointTrajectory` | RT-Control → Motion | 仅在 R-IN-23 为 FJT_READY 时接受；完整 8 轴；位置 rad、速度 rad/s；准入同 R-IN-24；用 header.stamp 标注首点时间基准；末点速度必须为 0；控制器从上一条指令接续新轨迹；与 R-IN-24 并发时以最后到达者为准（执行中的 action 目标被中止） |
| R-IN-12 | `/rt/led/set_rgbw` | Service / `robot_rt_control_interfaces/srv/SetLedRgbw` | Autonomy ⇄ RT-Control | 六路灯带完整 RGBW 设置；全零灭灯；响应只证明通信写确认，不证明实际发光；退出和重启不主动改色或重放 |
| R-IN-16 | `/rt/head/move` | Action / `robot_rt_control_interfaces/action/MoveHead` | Perception ⇄ RT-Control | 具名 head_joint/head_pitch_joint 弧度目标；同资源忙拒绝；取消停止并保持；旧 command topic 不允许外部并行写入 |

### 5.5 RT-Control 输出

| ID | ROS 名称 | 形式 / 类型 | 方向 | 关键约束 |
| --- | --- | --- | --- | --- |
| R-OUT-01 | `/tf` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体动态坐标边唯一；`map→odom` 与 `odom→base_footprint` 不由本域发布 |
| R-OUT-01S | `/tf_static` | Topic / `tf2_msgs/msg/TFMessage` | RT-Control → Perception、Motion、Autonomy | 本体固定坐标边唯一；`Q_LATCHED`；与 `/tf` 分开登记 |
| R-OUT-02 | `/rt/base/odom` | Topic / `nav_msgs/msg/Odometry` | RT-Control → Perception | `frame_id=odom`、`child_frame_id=base_footprint`；`Q_FAST_STATE`；50 Hz；**不作为到站或停稳最终证据** |
| R-OUT-03 | `/joint_states` | Topic / `sensor_msgs/msg/JointState` | RT-Control → Motion、Perception、Autonomy | 双臂、PP、升降、头部及底盘相关关节使用统一入口；不填伪造零值、不刷新旧样本时间、不把多模块拼成虚假同步快照 |
| R-OUT-04L | `/rt/battery/left/state` | Topic / `sensor_msgs/msg/BatteryState` | RT-Control → Autonomy | 左电池（BMS 地址 1）；BMS 周期 5 s（0.2 Hz）；只读，不作为业务控制入口 |
| R-OUT-04R | `/rt/battery/right/state` | Topic / `sensor_msgs/msg/BatteryState` | RT-Control → Autonomy | 右电池（BMS 地址 2）；BMS 周期 5 s（0.2 Hz）；只读，不作为业务控制入口 |
| R-OUT-05L | `/rt/vacuum/left/pressure` | Topic / `sensor_msgs/msg/FluidPressure` | RT-Control → Motion、Autonomy | 左侧真空表压，单位 Pa，负值为真空（偏离 FluidPressure 标准的绝压定义）；p<=-60000 Pa 为建立、p>=-1000 Pa 为释放，由消费方按此阈值判定；stamp 为样本时间；通信失败停发，由 R-OUT-20 报错 |
| R-OUT-05R | `/rt/vacuum/right/pressure` | Topic / `sensor_msgs/msg/FluidPressure` | RT-Control → Motion、Autonomy | 右侧真空表压，单位 Pa，负值为真空（偏离 FluidPressure 标准的绝压定义）；p<=-60000 Pa 为建立、p>=-1000 Pa 为释放，由消费方按此阈值判定；stamp 为样本时间；通信失败停发，由 R-OUT-20 报错 |
| R-OUT-19A | `/rt/ultrasonic/channel1/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 米制距离；通信失败停发并由状态接口立即报错；年龄超过 2.5 s 过期；无目标 +Inf，协议异常 NaN |
| R-OUT-19B | `/rt/ultrasonic/channel2/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19C | `/rt/ultrasonic/channel3/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19D | `/rt/ultrasonic/channel4/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19A；通道与安装外参须由版本化配置确认 |
| R-OUT-19E | `/rt/ultrasonic/channel5/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 米制距离；第二 E08 独立发布，第一模块失败不得阻止本侧；其余同 R-OUT-19A |
| R-OUT-19F | `/rt/ultrasonic/channel6/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-19G | `/rt/ultrasonic/channel7/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-19H | `/rt/ultrasonic/channel8/range` | Topic / `sensor_msgs/msg/Range` | RT-Control → Autonomy | 同 R-OUT-19E；通道与安装外参须由版本化配置确认 |
| R-OUT-20 | `/rt/sensors/state` | Topic / `robot_rt_control_interfaces/msg/SensorStatusArray` | RT-Control → Motion、Autonomy | 逐传感器声明有效、无目标、协议异常、通信错误、过期或未配置；每项保留真实样本时间，数组发布时间不刷新旧观测 |
| R-OUT-21 | `/rt/infrared/state` | Topic / `robot_rt_control_interfaces/msg/DigitalInputStateArray` | RT-Control → Autonomy | 手臂红外只表示目标检测开关量；逐通道标识、原始电平、语义状态和有效性；未知不得当成未检测，不直接触发运动停止 |
| R-OUT-22 | `/rt/imu/data` | Topic / `sensor_msgs/msg/Imu` | RT-Control → Motion | 当前 Navigation 职责由 motion 域消费；SI 单位；时间为主机发布/接收链语义，不声明设备同步；无效拼接不重发旧测量；独立磁场不公开 |
| R-OUT-23L | `/rt/force_torque/left_wrist/wrench` | Topic / `geometry_msgs/msg/WrenchStamped` | RT-Control → Motion | 左传感器坐标系、N/Nm、经设备标定与单位换算；不做工具/箱子重力补偿、不自动调零；配置未闭合时不可宣称有效 |
| R-OUT-23R | `/rt/force_torque/right_wrist/wrench` | Topic / `geometry_msgs/msg/WrenchStamped` | RT-Control → Motion | 右传感器坐标系、N/Nm、经设备标定与单位换算；不做工具/箱子重力补偿、不自动调零；配置未闭合时不可宣称有效 |
| R-OUT-07 | `/rt/arms/rolling/state` | Topic / `robot_rt_control_interfaces/msg/RollingJointControlState` | RT-Control → Motion | 每次激活 epoch 加 1；state 为 HOLDING（无轨迹）/STARTING（开始一段轨迹的批次已接受，等待其 replace_from）/RUNNING/STOPPING；last_sequence/last_result 只报本 epoch 最新收到的批次；stop_reason 为当前或最近一段轨迹的停止原因，自开始该段的批次被接受起为 STOP_NONE，停止后保持到下一段开始；final 轨迹执行到末点报 STOP_COMPLETED，由 RUNNING 直接进入 HOLDING；reliable/volatile/keep-last(5)，deadline 100 ms、lifespan 200 ms |
| R-OUT-09 | `/rt/readiness` | Topic / `robot_system_interfaces/msg/DomainReadiness` | RT-Control → Autonomy | ready 表示 RT-Control 当前能接收指令：未使能、控制器或硬件未激活、设备离线或故障锁存均为 false，blockers 给出稳定标记；变化立即发；稳定 1 Hz |
| R-OUT-28 | `/rt/capabilities` | Topic / `std_msgs/msg/String` | RT-Control → 外部/本地入口 | JSON 对象：schema_version=1、control_scope、use_mock_hardware、capabilities（本作用域提供的能力名列表）、hardware；作用域启动时发布一次 |
| R-OUT-10 | `/diagnostics` | Topic / `diagnostic_msgs/msg/DiagnosticArray` | RT-Control → 外部/本地入口 | `Q_DIAGNOSTIC`；不替代 Action Result、readiness 或硬安全链 |
