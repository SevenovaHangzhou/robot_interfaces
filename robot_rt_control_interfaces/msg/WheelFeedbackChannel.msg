# Timing and validity of one wheel feedback channel (member of WheelObservation).
# A channel is one device sample: drive position and velocity share the drive channel.

uint8 REASON_OK=0
# No sample has been received yet in this session.
uint8 REASON_NOT_READY=1
# The latest sample is older than the producer's feedback timeout; the value is the old one.
uint8 REASON_STALE=2
uint8 REASON_NONFINITE=3
# The device reports a fault state.
uint8 REASON_DEVICE_FAULT=4

# Sample time on the ROS time axis; kept unchanged while the same sample is republished.
builtin_interfaces/Time sample_stamp
# ObservationMeta.TIME_SOURCE_* (HOST_RECEIVE, READ_COMPLETE, ...); never DEVICE_SAMPLE
# unless a device clock is mapped to ROS time.
uint8 time_source
# Increments only when a new sample arrives; unchanged for a republished old sample.
uint64 sample_sequence
# Continuity generation: changes after any invalid gap, sequence regression or detected
# discontinuity. Increments across a change of epoch are not valid displacements.
uint32 epoch
bool valid
uint8 reason
