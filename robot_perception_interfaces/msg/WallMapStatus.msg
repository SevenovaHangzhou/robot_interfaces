# P-IF-05 /perception/wall_map_status。
uint8 IDLE=0
uint8 AIMING=1
uint8 CAPTURING=2
uint8 PROCESSING=3
uint8 FAILED=4

std_msgs/Header header
unique_identifier_msgs/UUID producer_instance_id
bool map_available
WallMapReference last_committed_map
uint8 update_state
bool active_operation_known
robot_system_interfaces/OperationContext active_context
builtin_interfaces/Time last_attempt_completed_at
bool last_attempt_time_known
bool last_attempt_succeeded
robot_system_interfaces/ErrorInfo error
