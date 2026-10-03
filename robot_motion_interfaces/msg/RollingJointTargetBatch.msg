# Complete authoritative suffix update for one V3 dual-seven-axis session.
# protocol 1.0 requires an exact version match AND the V3 axis_set_hash at open.
# Every point uses right_joint1..7, left_joint1..7; ALL positions rad, velocities rad/s.
# No axis substitution or partial-arm update; the non-moving arm is still included.

uint16 TRANSPORT_MAX_POINTS=256
uint16 PROTOCOL_MAJOR=1
uint16 PROTOCOL_MINOR=0

uint16 protocol_major
uint16 protocol_minor
unique_identifier_msgs/UUID controller_boot_id
unique_identifier_msgs/UUID session_id
unique_identifier_msgs/UUID client_instance_id
uint64 sequence
# Session-relative replacement boundary. The first point time must equal it.
uint64 replace_from_ns
RollingJointPoint[<=256] points
