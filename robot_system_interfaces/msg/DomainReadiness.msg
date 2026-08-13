string STATUS_HEALTHY=HEALTHY
string STATUS_DEGRADED=DEGRADED
string STATUS_UNAVAILABLE=UNAVAILABLE

std_msgs/Header header
string domain
string readiness_name
bool ready
string status
string operational_state
string map_version
string producer_instance_id
string[] blockers
robot_system_interfaces/ErrorInfo[] errors
