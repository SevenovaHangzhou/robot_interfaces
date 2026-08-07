# N-05 /navigation/localization/status。Perception → Motion、Autonomy。
# 发布者唯一；10～20 Hz；最大年龄 200 ms。
# 定位无效时 Motion 不得输出非零速度。

std_msgs/Header header

# 定位是否可用于导航决策。
bool localized

# 位置与朝向估计标准差。
float64 position_stddev_m
float64 yaw_stddev_rad

robot_system_interfaces/ErrorInfo blocker
