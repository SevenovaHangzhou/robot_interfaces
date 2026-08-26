# Fixed 14-axis order and SI units:
#   right_joint1..6, left_joint1..6, turn: position rad, velocity rad/s
#   updown: position m, velocity m/s

uint64 time_from_session_start_ns
float64[14] positions
float64[14] velocities
