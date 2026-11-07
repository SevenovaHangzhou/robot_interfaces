# Controller ownership mode of a joint group: arms (R-IN-06) or base (R-IN-23).

uint8 DISABLED=0
# Joint trajectory controller owns the group: arms R-IN-02/R-IN-22; base R-IN-24/R-IN-25,
# where the drive wheels run in CSP.
uint8 FJT_READY=1
# Arms only: the rolling controller owns the arms (M-09).
uint8 ROLLING_READY=2
uint8 RESTART_REQUIRED=3
# Base only: the swerve controller accepts /rt/base/cmd_vel (N-04); the drive wheels run in CSV.
uint8 VELOCITY_READY=4

uint8 value
