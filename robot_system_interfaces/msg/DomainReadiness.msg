string STATUS_HEALTHY=HEALTHY
string STATUS_DEGRADED=DEGRADED
string STATUS_UNAVAILABLE=UNAVAILABLE

# Final cross-domain capability-readiness envelope.
# ready is the sole capability-admission verdict. Consumers MUST NOT infer
# admission from status, operational_state, blockers, or errors independently.
#
# Consistency rules:
# - HEALTHY requires ready=true and empty blockers/errors.
# - DEGRADED requires ready=true, empty blockers, and one or more errors; every
#   error MUST have WARN severity.
# - UNAVAILABLE requires ready=false and at least one blocker or FAULT error.
# - blockers contains stable reason tokens that currently prevent admission.
# - errors contains structured cross-domain ErrorInfo values relevant to this
#   readiness_name; every entry has a non-SUCCESS canonical DREE code and MUST
#   NOT have OK severity.
# - map_version MUST be empty when readiness does not depend on a map.
# - producer_instance_id MUST remain stable for one process lifetime and change
#   when the producer process restarts.
# - operational_state is provider-owned detail and never overrides ready.
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
