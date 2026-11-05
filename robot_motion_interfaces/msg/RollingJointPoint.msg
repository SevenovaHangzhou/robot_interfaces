# One point of a rolling batch. Axis order and units: contract axis_sets.v3_dual_arm
# (right_joint1..7, then left_joint1..7; positions rad, velocities rad/s). Every arm axis is
# present, the arm that does not move included.

# Time after the batch's replace_from; the first point is 0.
builtin_interfaces/Duration time_from_start
float64[14] positions
float64[14] velocities
