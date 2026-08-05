# 箱墙任务计划。P-01 单次同步采集的产物。
#
# 计划生命周期由当前 G-01 管理，不携带 valid_until。
# 每个 G-01 只调用一次 P-01；计划不跨 G-01 复用。

std_msgs/Header header

# 采集时刻，即计划事实的时间基准。
builtin_interfaces/Time source_stamp

# 完整 25 箱、15 个序列。任一序列缺失即 P-01 失败。
# 每个序列自带工位、到站导航位姿和按臂绑定的重拍位，下游只消费不重算。
PickSequence[] sequences

# 模型与标定版本一致性不在运行期消息中校验：四域通过 release/source-lock.yaml
# 引用同一个 robot_description commit 保证（见契约 6.12），因此本消息不携带
# model_hash / calibration_hash —— 运行期没有权威版本源可供对账。
