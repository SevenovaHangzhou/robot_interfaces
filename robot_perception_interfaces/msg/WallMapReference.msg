# 一份箱子快照的身份。快照是全局的，不按墙面或场景划分。
unique_identifier_msgs/UUID producer_instance_id
# 只在成功提交新快照后递增；读取不递增。
uint64 map_version
# 稳定的真实 map 坐标身份（视觉部署配置，默认 physical_map_v1）；字段名沿用 V0.4，不要求导航状态话题。
# map 原点或方向改变时必须改变该身份并重建。
string navigation_map_version
