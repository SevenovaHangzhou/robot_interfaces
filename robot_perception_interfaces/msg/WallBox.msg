# 全局箱子库里的一个箱子。
uint8 TENTATIVE=0
uint8 CONFIRMED=1
uint8 MISSING_CANDIDATE=2
uint8 REMOVED_CONFIRMED=3

uint8 VISIBILITY_UNKNOWN=0
uint8 VISIBLE=1
uint8 OCCLUDED=2
uint8 OUT_OF_VIEW=3

uint8 RESOLVED=0
uint8 AMBIGUOUS=1

uint8 SUPPORT_UNKNOWN=0
uint8 SUPPORT_FREE=1
uint8 SUPPORT_BLOCKED=2
uint8 SUPPORT_REMOVED=3

# 在全局库内稳定。
string box_id
bool sku_known
string sku_id
# 箱体局部轴尺寸，米：X 宽、Y 深、Z 高。
# 0 表示该轴未知，不是零厚度实物；使用各中心自己的有效标记。
geometry_msgs/Vector3 dimensions_m
# map 下三种中心，均使用箱体轴 X=宽、Y=由正面向箱内、Z=高。
# 各中心独立有效；stamp 保留该几何的观测时间。
# 正面为局部 -Y，顶面为局部 +Z。侧吸从正面中心生成 TCP，顶吸从顶面中心生成，不重复减半深度。
geometry_msgs/PoseStamped face_center_pose
bool face_center_pose_valid
geometry_msgs/PoseStamped top_center_pose
bool top_center_pose_valid
# 体心仅在尺寸足以推导时有效；无深度不使已知面心失效。
geometry_msgs/PoseStamped box_center_pose
bool box_center_pose_valid
uint8 lifecycle_state
uint8 visibility_state
uint8 identity_state
# 最近一次真实看到的时间；读取和重发不刷新。
builtin_interfaces/Time last_observed_at
builtin_interfaces/Time state_determined_at
bool confidence_known
float32 confidence
string[] occluded_by_box_ids
# 上方占用。
uint8 support_state
string[] above_box_ids
string[] support_unknown_box_ids
builtin_interfaces/Time support_evaluated_at
# 视觉层面的必要条件，不代表机械臂可达或无碰撞。
bool grasp_candidate
string[] grasp_block_reasons
