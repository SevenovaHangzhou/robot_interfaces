# Complete point for the active rolling axis set. The ordered names and SI
# units are frozen by axis_set_hash for the controller lifecycle. Both arrays
# must contain exactly active_axis_count values; the protocol supports 1..14.

uint16 MAX_AXIS_COUNT=14

uint64 time_from_session_start_ns
float64[<=14] positions
float64[<=14] velocities
