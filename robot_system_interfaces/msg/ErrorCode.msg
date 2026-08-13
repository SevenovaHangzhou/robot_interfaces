# Centralized numeric error code constants.
#
# Encoding: D R EE
# D: domain ownership, 0=common 1=rt_control 2=perception 3=motion 4=autonomy
# R: machine recoverable, 0=no 1=yes
# EE: event class, shared across domains
#   00-09 communication/API misuse
#   10-19 configuration/version
#   20-29 hardware/device
#   30-39 environment/external condition
#   40-49 data quality
#   50-59 computation/solving
#   60-69 execution/motion
#   70-79 safety/interlock
#   80-89 task/flow
#   90-99 internal error
#
# SUCCESS=0 is the only exception and does not use DREE.

uint32 SUCCESS=0

# Common, not machine recoverable.
uint32 COMMUNICATION_UNKNOWN=1
uint32 TIMEOUT=2
uint32 GOAL_REJECTED=3
uint32 INVALID_GOAL=4
uint32 VERSION_MISMATCH=10
uint32 SAFETY_DENIED=70
uint32 CANCELED=80
uint32 INTERNAL_ERROR=90
uint32 UNKNOWN=91

# Common, machine recoverable.
uint32 RETRYABLE_INVALID_GOAL=100
uint32 NOT_READY=130

# RT-Control, not machine recoverable.
uint32 RT_TOLERANCE_VIOLATED=1060

# RT-Control, machine recoverable.
uint32 RT_CMD_VEL_STALE=1130
uint32 RT_ODOM_STALE=1131

# Perception, machine recoverable.
uint32 PERC_TF_UNAVAILABLE=2100
uint32 PERC_LOCALIZATION_LOST=2150

# Motion, not machine recoverable.
uint32 MOTION_BASE_IN_MOTION=3071

# Motion, machine recoverable.
uint32 MOTION_BASE_NOT_STATIONARY=3130
uint32 MOTION_NAV_FAILED=3160

# Autonomy, not machine recoverable.
uint32 AUTO_TARGET_UNAVAILABLE=4040
uint32 AUTO_TARGET_NOT_NAVIGABLE=4041
uint32 AUTO_INTERNAL_ERROR=4090

# Autonomy, machine recoverable.
uint32 AUTO_DOMAIN_UNAVAILABLE=4130

uint8 unused
