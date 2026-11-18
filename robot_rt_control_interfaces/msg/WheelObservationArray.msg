# R-OUT-29 /rt/base/wheel_observations: per-wheel feedback snapshot for navigation fusion.

# stamp: snapshot time, not a sample time (see each channel). frame_id: frame of the wheel
# geometry and steering angles, base_footprint (x forward, y left, z up).
std_msgs/Header header
# Stable identity of the producing data source.
string source_id
# Producer session; changes on producer restart, reactivation or ROS time rollback.
string session_id
# Strictly increasing within one session.
uint64 sequence
# Immutable identity of the geometry, unit-conversion and zero calibration in use.
string calibration_id
# Fixed order FRONT_LEFT, FRONT_RIGHT, REAR_LEFT, REAR_RIGHT; check wheel_id.
WheelObservation[4] wheels
