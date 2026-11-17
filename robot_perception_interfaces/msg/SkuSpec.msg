string sku_id
string display_name
# 标称尺寸，米，按箱体局部轴：X 宽、Y 深、Z 高。至少两个轴已知；未知轴填 0。
geometry_msgs/Vector3 nominal_dimensions_m
# false：视觉使用默认容差 0.04 m，dimension_tolerance_m 不解析。
bool dimension_tolerance_known
geometry_msgs/Vector3 dimension_tolerance_m
