# M-IF-05 /motion/state。Motion 持续发布的执行事实，Action 结束后继续发布。
# 各项观测带自己的时间；消息重发不刷新旧观测时间。
std_msgs/Header header
unique_identifier_msgs/UUID producer_instance_id
bool active_operation_known
robot_system_interfaces/OperationContext active_context
ArmExecutionState left
ArmExecutionState right
string current_posture_id
bool updown_position_valid
float64 updown_position_m
builtin_interfaces/Time updown_observed_at
bool configuration_held
bool hold_observation_valid
builtin_interfaces/Time hold_observed_at
# Mock 执行时为 true。
bool simulated
robot_system_interfaces/ErrorInfo error
robot_system_interfaces/ErrorInfo[] warnings
