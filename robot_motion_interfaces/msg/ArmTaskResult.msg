# 单臂在一次 Action 里的结果。
uint8 NOT_REQUESTED=0
uint8 SUCCEEDED=1
uint8 FAILED=2
uint8 CANCELED=3
# 动作可能已经发生但状态不明。不等于没有执行。
uint8 UNKNOWN=4

string arm
string box_id
uint8 outcome
ArmExecutionState final_state
bool stop_confirmed
bool stop_confirmation_valid
robot_system_interfaces/ErrorInfo error
