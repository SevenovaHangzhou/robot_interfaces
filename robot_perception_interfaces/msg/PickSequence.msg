# 一个取放序列。双箱序列共用同一个 Goal，是不可拆分的整体。
# 全部字段由 P-01 一次产出，下游只消费不重算。

# 序列序号，从 0 起，全计划内唯一且连续。
uint16 sequence_index

# 本序列的 1～2 个箱。双箱任一侧失败则整个序列不 Commit。
BoxPose[] boxes

# 本序列对应的工位标识。同一工位可对应多个序列。
string station_id

# 本序列所属的箱墙排号。**0 = 最下排，向上递增。**
# 感知事实：由箱墙结构识别得到，供下游展示、诊断和顺序核对。
uint8 wall_row

# 本序列实际使用的退避距离，单位 m。
#
# 当前所有 wall_row 统一使用 0.74 m。Perception 填写**实际使用的值**；
# 消费方不据此重算位姿，仅用于诊断与配置一致性核对。
float32 station_standoff_m

# 可直接执行的到站导航位姿，map 坐标系，非空。
#
# 导出规则：
#   取本序列所属列的箱墙面心 → 法向量与 XY 方向平均值
#   → 沿箱墙外法向回退统一的 station_standoff_m（当前 0.74 m）
#
# 该位姿用于以 station_id 为 landmark name 注册或更新 semantic map。
# N-01 /navigation/navigate_to_pose 只接收 target_name + map_version；
# Autonomy 导航本序列时传入 target_name=station_id，由 Motion 查询 semantic map
# 后把对应 Landmark.landmark_pose 转发给内部 Nav2，不重算、不自行加偏置。
geometry_msgs/PoseStamped station_nav_pose

# 本序列的近距离重拍位，按臂绑定，1～2 项，与 boxes 同集同序。
# M-01 直接消费，不重新解算。
CameraViewPose[] camera_view_poses
