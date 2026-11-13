# 一份箱子快照的身份。快照是全局的，不按墙面或场景划分。
unique_identifier_msgs/UUID producer_instance_id
# 只在成功提交新快照后递增；读取不递增。
uint64 map_version
string navigation_map_version
