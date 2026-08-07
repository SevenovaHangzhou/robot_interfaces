# 近距离重拍位，绑定到具体的臂。PickSequence 的成员，不单独发布。
# 由 P-01 随计划一次产出，M-01 直接消费，不重新解算。

# arm 取值。与 robot_description 定义的 14 轴关节顺序一致。
uint8 ARM_LEFT=0
uint8 ARM_RIGHT=1

# 本重拍位由哪条臂执行。
uint8 arm

# 本重拍位对应的箱标识，与所属 PickSequence 的 boxes 中某一项对应。
string box_id

# 重拍观测位姿，map 坐标系。
geometry_msgs/PoseStamped pose
