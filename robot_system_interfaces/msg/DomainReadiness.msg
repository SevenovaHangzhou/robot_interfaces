# 域就绪心跳。Q_LATCHED；状态变化立即发布，稳定时 1 Hz。
#
# 消费方按本地 steady clock 接收年龄派生 HEALTHY / DEGRADED / UNAVAILABLE：
#   HEALTHY      合法、ready=true、版本匹配、age <= 2 s
#   DEGRADED     上一条原本合法且 ready=true，2 s < age <= 3 s
#   UNAVAILABLE  age > 3 s，或新鲜消息明确 ready=false / 内容非法
#
# 额外 1 s 宽限只容忍未收到新心跳或 DDS 到达延迟。新鲜 ready=false、
# fatal reason、版本/hash 不匹配、producer_instance_id 改变均不享受宽限。

std_msgs/Header header

# 本域是否可接受新业务派发。
bool ready

# 未就绪原因。ready=true 时 code 必须为 SUCCESS。
ErrorInfo blocker

# 进程实例标识。producer 每次启动生成随机 UUID，运行期不变。
# 实例 ID 改变即进程重启，新实例不得加入旧 G-01。
unique_identifier_msgs/UUID producer_instance_id

# 本域编译时使用的契约 schema hash，用于发现新旧版本混跑。
string contract_version
