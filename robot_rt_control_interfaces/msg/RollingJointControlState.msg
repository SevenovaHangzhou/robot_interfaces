# Public rolling state. All time fields are session-relative or monotonic ages;
# published_at is diagnostic only and never orders or samples commands.

uint16 PROTOCOL_MAJOR=1
uint16 PROTOCOL_MINOR=0

uint16 protocol_major
uint16 protocol_minor
unique_identifier_msgs/UUID controller_boot_id
unique_identifier_msgs/UUID session_id
unique_identifier_msgs/UUID client_instance_id

JointControlMode control_mode
RollingSessionState session_state
bool has_session
bool has_accepted_update
bool pending_generation_valid

uint64 active_generation
uint64 validation_base_generation
uint64 pending_generation
uint64 last_seen_sequence
uint64 last_accepted_sequence
uint64 last_rejected_sequence

uint64 execution_time_ns
uint64 replaceable_from_ns
uint64 buffered_until_ns
uint64 available_horizon_ns
# prime_age is meaningful before the first accepted update; accepted_update_age
# is meaningful only while has_accepted_update=true. Both use steady time.
uint64 prime_age_ns
uint64 accepted_update_age_ns

# Same fixed axis order and units as RollingJointPoint.
float64[14] desired_positions
float64[14] desired_velocities
uint16 buffer_point_count
uint16 buffer_capacity

RollingRejectCode last_reject
RollingStopReason stop_reason
RollingServiceResult last_mode_result
unique_identifier_msgs/UUID last_mode_request_id
bool source_controller_deactivated
bool target_controller_activated
bool restart_required
RollingLimitsSource limits_source
bool test_only_limits
uint8[32] axis_set_hash
uint8[32] limits_version

uint64 accepted_count
uint64 rejected_count
uint64 superseded_pending_count
uint64 timeout_count
uint64 invariant_failure_count
uint64 command_deadline_miss_count
uint64 state_sequence
builtin_interfaces/Time published_at
