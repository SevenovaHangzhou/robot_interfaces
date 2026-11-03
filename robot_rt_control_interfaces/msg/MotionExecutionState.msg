uint8 EXECUTION_UNKNOWN=0
uint8 EXECUTION_IDLE=1
uint8 EXECUTION_EXECUTING=2
uint8 EXECUTION_STOPPING=3
uint8 EXECUTION_HOLDING=4
uint8 EXECUTION_FAULT=5

std_msgs/Header header
string resource_id
string[] joint_names
float64[] actual_positions
ObservationMeta feedback_observation
uint8 execution_state
bool stop_confirmed
bool stop_confirmation_valid
bool goal_known
unique_identifier_msgs/UUID goal_id
robot_system_interfaces/ErrorInfo error
