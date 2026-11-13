# 单臂的执行事实。持箱与否的业务判断由 Autonomy 做，这里不给结论。
uint8 IDLE=0
uint8 APPROACH=1
uint8 WAIT_SUCTION=2
uint8 EXTRACT=3
uint8 TRANSPORT=4
uint8 CARRY=5
uint8 PLACE=6
uint8 RELEASE=7
uint8 DELAY=8
uint8 CONVERGE=9
uint8 STOPPED=10
uint8 FAULT=11

# left 或 right。
string arm
bool participating
bool target_known
string box_id
uint8 phase
# Motion 依据 RT 压力判断的吸附事实；valid=false 时 established 不解析。
bool suction_established
bool suction_observation_valid
builtin_interfaces/Time suction_observed_at
bool target_cleared_from_wall
bool target_clear_evidence_valid
# 阀输出已确认释放。不代表箱子已经脱离。
bool output_release_confirmed
bool release_delay_completed
bool arm_stationary
bool stationary_observation_valid
builtin_interfaces/Time stationary_observed_at
robot_system_interfaces/ErrorInfo error
