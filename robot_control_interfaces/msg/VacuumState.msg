# R-OUT-05 /vacuum/state。Q_STATE；20～50 Hz。
# 只有 RT-Control 用于 GRIP 判定，其他域不得自行计算吸取成功。

std_msgs/Header header

# 真空泵运行状态。
bool pump_on

# 各通道状态，顺序与 VacuumGrip 的通道顺序一致。
VacuumChannelState[] channels
