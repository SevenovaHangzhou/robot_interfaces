# 单个真空通道的实时状态。VacuumState 的成员，不单独发布。

# 通道标识，全系统稳定编号。
uint8 channel

# 电磁阀线圈实际通电状态。
bool solenoid_on

# 通道新鲜表压，单位 kPa，负值表示真空。
float32 gauge_pressure_kpa

# 表压读数是否新鲜可信。false 时不得用于任何吸取判定。
bool pressure_fresh

# RT-Control 的权威吸附判定，取值见 VacuumChannelResult 的 verification_level。
uint8 verification_level
