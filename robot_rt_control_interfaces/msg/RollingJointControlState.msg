# Rolling controller state (R-OUT-07), published while the rolling controller is active.

# No trajectory: holding a position. An accepted batch starts STARTING.
uint8 HOLDING=0
# Following the buffered trajectory.
uint8 RUNNING=1
# Braking within the limits (see stop_reason); HOLDING follows.
uint8 STOPPING=2
# A batch started the trajectory; holding until its replace_from, then RUNNING.
uint8 STARTING=3

uint8 ACCEPTED=0
uint8 WRONG_EPOCH=1
uint8 STALE_SEQUENCE=2
# Empty, too many points, not finite, or point times not strictly increasing.
uint8 INVALID_BATCH=3
# replace_from earlier than now + the replace lead.
uint8 LATE_REPLACE=4
# First point does not match the buffered trajectory at replace_from.
uint8 SPLICE_MISMATCH=5
# A position, velocity or acceleration limit of the robot model is exceeded.
uint8 LIMIT_EXCEEDED=6
# From some point of the batch the arms could not stop within the limits.
uint8 NOT_STOPPABLE=7
# Beyond the buffer capacity or the maximum horizon.
uint8 HORIZON_EXCEEDED=8
# Braking (STOPPING), or the arms are not where the held command is; resend once HOLDING.
uint8 NOT_ACCEPTING=9
# final is set but a velocity of the last point is not 0.
uint8 FINAL_NOT_AT_REST=10

uint8 STOP_NONE=0
# No accepted batch within the update timeout while the newest accepted batch is not final.
uint8 STOP_UPDATE_TIMEOUT=1
# The buffered trajectory ran out while the newest accepted batch is not final.
uint8 STOP_BUFFER_END=2
# Mode switched away, disabled or controller deactivated.
uint8 STOP_DEACTIVATED=3
uint8 STOP_FAULT=4
uint8 STOP_INTERNAL=5
# The final trajectory reached its last point; the arms hold there (RUNNING, then HOLDING).
uint8 STOP_COMPLETED=6

# Increments on every activation of the rolling controller.
uint32 epoch
uint8 state
# Sequence of the newest batch received in this epoch and its result.
uint64 last_sequence
uint8 last_result
# Why the current or latest trajectory stopped: STOP_NONE from the batch that starts a
# trajectory until that trajectory stops, and before the first trajectory of the epoch.
uint8 stop_reason
