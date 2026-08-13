# Centralized numeric error code constants.
#
# Encoding: D R EE
# D: domain ownership, 0=common 1=rt_control 2=perception 3=motion 4=autonomy
# R: machine recoverable, 0=no 1=yes
# EE: event class, shared across domains
#   00-09 communication/API misuse
#   10-19 configuration/version
#   20-29 hardware/device
#   30-39 environment/external condition
#   40-49 data quality
#   50-59 computation/solving
#   60-69 execution/motion
#   70-79 safety/interlock
#   80-89 task/flow
#   90-99 internal error
#
# SUCCESS=0 is the only exception and does not use DREE.

uint32 SUCCESS=0

# Common, not machine recoverable.
uint32 COMMUNICATION_UNKNOWN=1
uint32 TIMEOUT=2
uint32 GOAL_REJECTED=3
uint32 INVALID_GOAL=4
uint32 VERSION_MISMATCH=10
uint32 SAFETY_DENIED=70
uint32 CANCELED=80
uint32 INTERNAL_ERROR=90
uint32 UNKNOWN=91

# Common, machine recoverable.
uint32 RETRYABLE_INVALID_GOAL=100
uint32 NOT_READY=130

# RT-Control, not machine recoverable.
uint32 RT_TOLERANCE_VIOLATED=1060

# RT-Control, machine recoverable.
uint32 RT_CMD_VEL_STALE=1130
uint32 RT_ODOM_STALE=1131

# Perception, machine recoverable.
uint32 PERC_TF_UNAVAILABLE=2100
uint32 PERC_LOCALIZATION_LOST=2150

# ---------- 3 Motion · 不可自主恢复（3000~3099） ----------
# 阶段顺序错误、阶段重放或当前活动流程与请求不一致。
uint32 MOTION_STAGE_SEQUENCE_INVALID=3004
# 目标超出可达域；指向标定或退避表配置，不是规划器问题。
uint32 MOTION_TARGET_UNREACHABLE=3010
# 手臂未在行走包络内，或存在活动手臂 goal（契约 6.7）。
uint32 MOTION_ARM_NOT_STOWED=3070
# 底盘未静止，或存在活动导航 goal（契约 6.7）。
uint32 MOTION_BASE_IN_MOTION=3071
uint32 MOTION_EXECUTION_FAILED=3060
# 生成轨迹不满足完整关节集、时间单调、速度或连续性约束。
uint32 MOTION_TRAJECTORY_INVALID=3061
# RT-Control 拒绝轨迹 Goal，且原请求不允许直接重放。
uint32 MOTION_EXECUTION_REJECTED=3062
# 控制器返回成功前或收敛检查中发现跟踪误差超限。
uint32 MOTION_TRACKING_FAILED=3063
uint32 MOTION_INTERNAL_ERROR=3090

# ---------- 3 Motion · 可自主恢复（3100~3199） ----------
# 关节状态、TF 或场景事实暂时缺失/过期。
uint32 MOTION_STATE_UNAVAILABLE=3130
# 取箱位姿超过 max_pose_age，重新精定位后可再试。
uint32 MOTION_POSE_STALE=3140
# 规划失败（含 IK 无解）；换目标或重规划可能成功。
uint32 MOTION_PLANNING_FAILED=3150
# 碰撞检出，需重规划。
uint32 MOTION_COLLISION_DETECTED=3151
# 目标位姿当前没有满足约束的逆解。
uint32 MOTION_IK_NO_SOLUTION=3152
# Nav2 本次未到达，属 N-01 三次预算内可重试。
uint32 MOTION_NAV_FAILED=3160

# Autonomy, not machine recoverable.
uint32 AUTO_TARGET_UNAVAILABLE=4040
uint32 AUTO_TARGET_NOT_NAVIGABLE=4041
uint32 AUTO_INTERNAL_ERROR=4090

# Autonomy, machine recoverable.
uint32 AUTO_DOMAIN_UNAVAILABLE=4130

uint8 unused
