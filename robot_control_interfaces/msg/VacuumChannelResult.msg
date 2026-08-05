# VacuumGrip Result 的单通道结果。字段集已冻结，不得扩充。

# verification_level 取值
uint8 UNVERIFIED=0
uint8 ATTACHED_VERIFIED=1
uint8 DETACH_UNVERIFIED=2

# 通道标识，与 Goal 请求同数量、同集、同序。
uint8 channel

# 命令是否被 RT-Control 接受。
bool command_accepted

# 阀动作是否执行完成。
# false 不等于命令一定未发送，不得据此授权物理重试。
bool valve_actuation_completed

# RT-Control 的权威判定。
# GRIP 全通道新鲜表压 <= -50 kPa 才 ATTACHED_VERIFIED。
# RELEASE 永远为 DETACH_UNVERIFIED，不以压力判定释放成功。
uint8 verification_level

robot_system_interfaces/ErrorInfo error
