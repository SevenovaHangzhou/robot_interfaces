# 单个箱体位姿事实。

# 箱标识，全任务唯一且稳定。
string box_id

# 可执行的吸取表面接触位姿，不是箱体几何中心。姿态的工具进给轴指向箱体内部。
# frame 与 stamp 由生产者按接口约定填写：P-01 使用 map；P-02 使用 base_link，
# 且 stamp 为生成该位姿所用图像的真实曝光时刻。
geometry_msgs/PoseStamped pose

# 箱尺寸，单位 m。
geometry_msgs/Vector3 size
