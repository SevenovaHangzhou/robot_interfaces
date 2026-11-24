uint8 NOT_SEARCHED=0
uint8 FOUND=1
uint8 NOT_FOUND=2
# 没看到不等于没有：视野或遮挡不足时用这个值。
uint8 NOT_OBSERVABLE=3
uint8 AMBIGUOUS=4
uint8 FAILED=5

string candidate_id
uint8 outcome
bool observed_time_known
builtin_interfaces/Time observed_at
robot_system_interfaces/ErrorInfo error
