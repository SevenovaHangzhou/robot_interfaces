# 一次业务操作的关联标识，由 Autonomy 生成。
# 只用于日志和结果对账；不表示去重，也不保证“恰好一次”。
# 同一逻辑操作重试时保留 operation_id，换新的 attempt_id。
unique_identifier_msgs/UUID task_id
string group_id
unique_identifier_msgs/UUID operation_id
unique_identifier_msgs/UUID attempt_id
