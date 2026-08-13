# M-08 的双臂目标。Pose 固定表达在 base_link 坐标系中。

# 0 为非法默认值，防止未赋值消息触发运动。
uint8 GRASP_MODE_UNSPECIFIED=0
uint8 GRASP_MODE_TOP_SUCTION=1
uint8 GRASP_MODE_SIDE_SUCTION=2
uint8 GRASP_MODE_NO_MOVE=3

# CAMERA_VIEW：TOP/SIDE 仅表示该臂参与，Pose 姿态原样执行；NO_MOVE 表示该臂无目标。
# PREGRASP：TOP/SIDE 分别表示顶吸面中心和侧吸正面中心；Motion 据此生成抓取流程。
# APPROACH/PLACE/HOME：本消息不参与规划，服务端使用当前活动流程中缓存的目标与轨迹。
# 单臂目标可将另一臂设为 NO_MOVE；Motion 可采用已验收的双臂镜像降级。
# 两臂同时 NO_MOVE 非法。
uint8 left_grasp_mode
geometry_msgs/Pose left_pose

uint8 right_grasp_mode
geometry_msgs/Pose right_pose
