# 全局箱子快照。header.frame_id 为 map；header.stamp 是提交时间，读取时不改。
std_msgs/Header header
WallMapReference reference
string sku_catalog_id
uint64 sku_catalog_revision
builtin_interfaces/Time observation_started_at
builtin_interfaces/Time observation_finished_at
# 库里保留的全部箱子，包括暂时不可见和已确认移除的记录。
WallBox[] boxes
