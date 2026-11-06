# Replaces the buffered rolling trajectory from replace_from onwards (M-09).
uint16 MAX_POINTS=256

# RollingJointControlState.epoch of the activation this batch is meant for.
uint32 epoch
# Strictly increasing within one activation.
uint64 sequence
# ROS time of the first point. It must not be earlier than now + the replace lead, and the
# first point must match the buffered trajectory there (position and velocity).
builtin_interfaces/Time replace_from
RollingJointPoint[<=256] points
# Last batch of the trajectory: every velocity of its last point is 0. While the newest
# accepted batch is final no further batch is needed: the controller runs to that point, holds
# there and reports STOP_COMPLETED. A later batch may still replace the trajectory from its
# replace_from; if that batch is not final, the update timeout applies again.
bool final
