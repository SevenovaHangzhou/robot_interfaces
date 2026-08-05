# 单个箱体位姿事实。

# 箱标识，全任务唯一且稳定。
string box_id

# 箱位姿。frame 与 stamp 由生产者按接口约定填写：
# P-01 计划使用 map，P-02 精定位使用 base_link 且 stamp 为真实曝光时刻。
geometry_msgs/PoseStamped pose

# 箱尺寸，单位 m。
geometry_msgs/Vector3 size
