# V3 dual-seven-axis order (positions in rad; velocities in rad/s for ALL axes):
# [0..6]  right_joint1, right_joint2, right_joint3, right_joint4,
#         right_joint5, right_joint6, right_joint7
# [7..13] left_joint1, left_joint2, left_joint3, left_joint4,
#         left_joint5, left_joint6, left_joint7
# Independent PP grippers, head, chassis and lift are not in this array.
# axis_set_hash: SHA-256 of UTF-8 joint_name:rad:rad/s followed by LF per axis,
# including the final LF; no BOM, CR, spaces or header.
# f4c8ff8a32183d1733032494600c9f5d1e7e625673a4ad51556b3ac6c35adee4
# Machine-readable authority: contract/endpoints.yaml axis_sets.v3_dual_arm.

uint64 time_from_session_start_ns
float64[14] positions
float64[14] velocities
