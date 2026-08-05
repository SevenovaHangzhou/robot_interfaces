# R-OUT-06 /control/safety_state。Q_STATE；10～50 Hz；最大年龄 200 ms。
# deny 或过期时禁止新动作。200 ms 严格时效，不套用 readiness 的 1 s 宽限。
#
# 本消息是**软件可观测的安全摘要**，不是硬安全链状态。
# 急停、安全继电器、STO 的真实状态不在本消息内（见契约 6.12），
# 消费方不得从本消息推断硬安全链是否触发。

std_msgs/Header header

# 是否允许下发新动作。false 或消息过期时全系统禁止新动作。
bool allow_motion

# 驱动器动力使能实际状态。由 enable_manager 汇总。
bool motor_power_enabled

# 两条现场总线独立上报：EtherCAT 承载 14 个机械轴，CANopen 承载履带。
# 分开是因为故障后果不同 —— EtherCAT 掉线手臂不能动，CANopen 掉线底盘不能动，
# 单个布尔无法表达"一条通一条不通"。
bool ethercat_online
bool canopen_online

# 禁止动作原因。allow_motion=true 时 code 必须为 SUCCESS。
robot_system_interfaces/ErrorInfo blocker
