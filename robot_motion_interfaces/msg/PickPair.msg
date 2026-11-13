# 一次整组抓取的目标：最多左右各一个箱子。
uint8 PURPOSE_UNSPECIFIED=0
uint8 NORMAL_PICK=1
uint8 DROPPED_BOX_RECOVERY=2

robot_system_interfaces/OperationContext context
uint8 purpose
string navigation_map_version
# 目标是否来自视觉的箱子快照。掉箱回收时为 false，下面两个快照字段不解析。
bool uses_wall_map
unique_identifier_msgs/UUID wall_producer_instance_id
uint64 wall_map_version
# 目标是否来自缓存的旧观测。只描述来源。
bool uses_cached_observation
# 换算 TCP 时 map 下的 base_link 位姿。只作追溯。
# Autonomy 负责：停稳后换算、换算后立即下发、抓取期间底盘不动。
geometry_msgs/PoseStamped base_pose_at_target_generation
# 引用 Motion 管理的版本化配置，不携带环境几何或关节角。
string collision_scene_profile_id
string carry_posture_id
PickTarget left
PickTarget right
