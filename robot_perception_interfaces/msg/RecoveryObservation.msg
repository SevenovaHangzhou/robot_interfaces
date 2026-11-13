# 掉箱搜索里新看到的一个箱子。不写入正常箱子库，不恢复原箱 ID。
string observation_id
bool matched_candidate_known
string matched_candidate_id
bool sku_known
string sku_id
# map 下的箱体中心和朝向。
geometry_msgs/PoseStamped box_center_pose
bool box_center_pose_valid
geometry_msgs/Vector3 dimensions_m
builtin_interfaces/Time observed_at
bool confidence_known
float32 confidence
