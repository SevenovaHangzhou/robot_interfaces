# 单臂抓取目标。左右由 PickPair 的字段名决定。
uint8 GRASP_MODE_UNSPECIFIED=0
uint8 SIDE_SUCTION=1
uint8 TOP_SUCTION=2

# false 时其余字段不解析。
bool enabled
string box_id
string sku_id
uint8 grasp_mode
# base_link 下的 TCP 位姿，米，四元数 xyzw。Motion 不再叠加工具偏移。
# header.stamp 是 Autonomy 换算的时刻。
geometry_msgs/PoseStamped tcp_target
# left_tool0 或 right_tool0。
string tcp_frame
# 视觉原始观测时间。只作记录，不作为拒绝条件。
builtin_interfaces/Time source_observed_at
# 箱体局部轴尺寸，米。
geometry_msgs/Vector3 box_dimensions_m
# mass_known=false 时 mass_kg 不解析，Motion 使用配置的默认质量。
bool mass_known
float64 mass_kg
